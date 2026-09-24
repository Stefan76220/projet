from __future__ import annotations

"""TomeLinea V5 — chaîne séquentielle.

Source DOCX immuable -> copie de travail -> TLDocument -> rendu LibreOffice.
Le PDF est une projection fidèle, jamais la vérité de travail.

V5-32A :
- visionneur direct PyMuPDF ;
- Structure logique indépendante du rendu ;
- ordre logique avec repère de dépôt ;
- sélection multiple Ctrl/Shift ;
- navigation selon l'ordre visible ;
- hiérarchie éditoriale du Corps : Partie > Chapitre > Section.
"""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json
import shutil
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from uuid import uuid4
import zipfile
import xml.etree.ElementTree as ET

from PIL import Image, ImageTk
import pymupdf

from src.gui_v4 import theme
from tomelinea.document import build_tldocument_from_docx
from tomelinea.rendering import render_document_to_pdf


EP = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"

STRUCTURE_SCHEMA = "tomelinea-logical-structure"
STRUCTURE_VERSION = 3

STRUCTURE_ZONES = {
    "prelim": "Pages liminaires",
    "body": "Corps",
    "end": "Fin",
    "unclassified": "Non classées",
}


@dataclass(frozen=True, slots=True)
class PreparedBook:
    source: Path
    working: Path
    pdf: Path
    structure_path: Path
    page_count: int
    paragraph_count: int
    image_count: int
    warning_count: int
    render_seconds: float
    engine_origin: str


def _file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _cached_docx_pages(path: Path) -> int | None:
    try:
        with zipfile.ZipFile(path, "r") as archive:
            root = ET.fromstring(archive.read("docProps/app.xml"))
        node = root.find(f"{{{EP}}}Pages")
        if node is not None and (node.text or "").strip():
            return int(node.text.strip())
    except Exception:
        pass
    return None


def _pdf_page_count(path: Path, fallback: int | None = None) -> int:
    try:
        with pymupdf.open(path) as document:
            return int(document.page_count)
    except Exception:
        return int(fallback or 1)


class TomeLineaV5SequentialShell(tk.Tk):
    def __init__(self) -> None:
        super().__init__()

        self.title("TomeLinea V5 — chaîne séquentielle")
        self.geometry("1480x900")
        self.minsize(1120, 700)
        self.configure(bg=theme.WINDOW)

        self.project_root = Path(__file__).resolve().parents[2]
        self.runtime_root = self.project_root / ".tomelinea_runtime" / "v5"
        self.runtime_root.mkdir(parents=True, exist_ok=True)

        self._source_path: Path | None = None
        self._working_path: Path | None = None
        self._pdf_path: Path | None = None
        self._structure_path: Path | None = None
        self._pdf_document: pymupdf.Document | None = None

        self._page_count = 0
        self._active_page_no = 1
        self._page_photo: ImageTk.PhotoImage | None = None
        self._resize_after_id: str | None = None
        self._busy = False

        self._structure_zone_by_page: dict[int, str] = {}
        self._structure_order_by_zone: dict[str, list[int]] = {
            zone: []
            for zone in STRUCTURE_ZONES
        }

        # Hiérarchie éditoriale du Corps.
        self._body_nodes: dict[str, dict[str, object]] = {}
        self._body_node_order: list[str] = []
        self._body_node_by_page: dict[int, str] = {}

        self._structure_rebuilding = False

        # Glisser-déposer Structure.
        self._drag_page_no: int | None = None
        self._drag_page_nos: list[int] = []
        self._drag_start_xy: tuple[int, int] | None = None
        self._dragging = False
        self._drag_target: tuple[
            str,
            int | None,
            str,
            str | None,
        ] | None = None

        self._build_ui()

    # =========================================================
    # UI
    # =========================================================

    def _build_ui(self) -> None:
        top = tk.Frame(
            self,
            bg=theme.PANEL,
            height=58,
        )
        top.pack(fill="x")
        top.pack_propagate(False)

        tk.Label(
            top,
            text="TOMELINEA",
            bg=theme.PANEL,
            fg=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 15, "bold"),
        ).pack(
            side="left",
            padx=(18, 20),
        )

        self.import_button = tk.Button(
            top,
            text="Importer un DOCX",
            command=self._choose_docx,
            bg=theme.ACCENT,
            fg="white",
            activebackground=theme.ACCENT_BRIGHT,
            relief="flat",
            bd=0,
            padx=18,
            pady=7,
            cursor="hand2",
            font=(theme.FONT_UI, 9, "bold"),
        )
        self.import_button.pack(
            side="left",
            pady=12,
        )

        self.refresh_button = tk.Button(
            top,
            text="Recalculer le rendu",
            command=self._refresh_render,
            state="disabled",
            bg=theme.PANEL_ALT,
            fg=theme.INK,
            activebackground=theme.PANEL_SOFT,
            relief="flat",
            bd=0,
            padx=16,
            pady=7,
            cursor="hand2",
            font=(theme.FONT_UI, 9),
        )
        self.refresh_button.pack(
            side="left",
            padx=(10, 0),
            pady=12,
        )

        self.top_status = tk.Label(
            top,
            text="Aucun livre ouvert",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 9),
            anchor="e",
        )
        self.top_status.pack(
            side="right",
            fill="x",
            expand=True,
            padx=18,
        )

        body = tk.PanedWindow(
            self,
            orient="horizontal",
            sashwidth=5,
            bg=theme.WINDOW,
            bd=0,
            relief="flat",
        )
        body.pack(
            fill="both",
            expand=True,
        )

        left = tk.Frame(
            body,
            bg=theme.PANEL,
            width=330,
        )
        center = tk.Frame(
            body,
            bg=theme.WINDOW,
        )
        right = tk.Frame(
            body,
            bg=theme.PANEL,
            width=265,
        )

        body.add(
            left,
            minsize=280,
        )
        body.add(
            center,
            minsize=560,
        )
        body.add(
            right,
            minsize=230,
        )

        # ---------------- Structure ----------------

        tk.Label(
            left,
            text="STRUCTURE LOGIQUE",
            bg=theme.PANEL,
            fg=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 10, "bold"),
            anchor="w",
        ).pack(
            fill="x",
            padx=16,
            pady=(16, 4),
        )

        tk.Label(
            left,
            text=(
                "Classement logique uniquement.\n"
                "Ctrl/Shift : sélectionner plusieurs pages."
            ),
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 8),
            anchor="w",
            justify="left",
            wraplength=290,
        ).pack(
            fill="x",
            padx=16,
            pady=(0, 8),
        )

        structure_tools = tk.Frame(
            left,
            bg=theme.PANEL,
        )
        structure_tools.pack(
            fill="x",
            padx=10,
            pady=(0, 8),
        )

        for label, kind in (
            ("+ Partie", "partie"),
            ("+ Chapitre", "chapitre"),
            ("+ Section", "section"),
        ):
            tk.Button(
                structure_tools,
                text=label,
                command=lambda k=kind: self._create_body_node(k),
                bg=theme.PANEL_ALT,
                fg=theme.INK,
                activebackground=theme.PANEL_SOFT,
                relief="flat",
                bd=0,
                padx=6,
                pady=4,
                cursor="hand2",
                font=(theme.FONT_UI, 8),
            ).pack(
                side="left",
                padx=(0, 4),
            )

        tk.Button(
            structure_tools,
            text="Renommer",
            command=self._rename_selected_body_node,
            bg=theme.PANEL_ALT,
            fg=theme.INK,
            activebackground=theme.PANEL_SOFT,
            relief="flat",
            bd=0,
            padx=6,
            pady=4,
            cursor="hand2",
            font=(theme.FONT_UI, 8),
        ).pack(
            side="left",
        )

        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(
            "TL.Treeview",
            background=theme.PANEL,
            fieldbackground=theme.PANEL,
            foreground=theme.INK,
            borderwidth=0,
            rowheight=25,
            font=(theme.FONT_UI, 9),
        )

        style.map(
            "TL.Treeview",
            background=[
                ("selected", theme.ACCENT),
            ],
            foreground=[
                ("selected", "white"),
            ],
        )

        self.structure_tree = ttk.Treeview(
            left,
            show="tree",
            style="TL.Treeview",
            selectmode="extended",
        )
        self.structure_tree.pack(
            fill="both",
            expand=True,
            padx=(10, 8),
            pady=(0, 14),
        )

        self.structure_tree.tag_configure(
            "editorial_part",
            foreground=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 9, "bold"),
        )
        self.structure_tree.tag_configure(
            "editorial_chapter",
            foreground=theme.INK,
            font=(theme.FONT_UI, 9, "bold"),
        )
        self.structure_tree.tag_configure(
            "editorial_section",
            foreground=theme.MUTED,
            font=(theme.FONT_UI, 8, "bold"),
        )

        self.structure_tree.bind(
            "<<TreeviewSelect>>",
            self._on_structure_select,
        )
        self.structure_tree.bind(
            "<ButtonPress-1>",
            self._on_structure_button_press,
            add="+",
        )
        self.structure_tree.bind(
            "<B1-Motion>",
            self._on_structure_drag_motion,
            add="+",
        )
        self.structure_tree.bind(
            "<ButtonRelease-1>",
            self._on_structure_button_release,
            add="+",
        )

        # Ligne d'insertion reprise de l'Explorateur V4.
        self._drop_line = tk.Frame(
            left,
            bg=theme.ACCENT_BRIGHT,
            height=2,
        )

        # ---------------- Centre ----------------

        self.center = center

        viewer_bar = tk.Frame(
            center,
            bg=theme.PANEL,
            height=38,
        )
        viewer_bar.pack(
            fill="x",
        )
        viewer_bar.pack_propagate(
            False
        )

        self.prev_button = tk.Button(
            viewer_bar,
            text="‹",
            command=self._previous_page,
            state="disabled",
            bg=theme.PANEL,
            fg=theme.INK,
            activebackground=theme.PANEL_ALT,
            relief="flat",
            bd=0,
            width=3,
            font=(theme.FONT_UI, 14, "bold"),
        )
        self.prev_button.pack(
            side="left",
            padx=(8, 0),
            pady=4,
        )

        self.page_label = tk.Label(
            viewer_bar,
            text="Aucune page",
            bg=theme.PANEL,
            fg=theme.INK,
            font=(theme.FONT_UI, 9, "bold"),
        )
        self.page_label.pack(
            side="left",
            padx=10,
        )

        self.next_button = tk.Button(
            viewer_bar,
            text="›",
            command=self._next_page,
            state="disabled",
            bg=theme.PANEL,
            fg=theme.INK,
            activebackground=theme.PANEL_ALT,
            relief="flat",
            bd=0,
            width=3,
            font=(theme.FONT_UI, 14, "bold"),
        )
        self.next_button.pack(
            side="left",
            pady=4,
        )

        self.viewer_canvas = tk.Canvas(
            center,
            bg=theme.WINDOW_DEEP,
            highlightthickness=0,
            bd=0,
        )
        self.viewer_canvas.pack(
            fill="both",
            expand=True,
        )
        self.viewer_canvas.bind(
            "<Configure>",
            self._on_viewer_resize,
        )

        self.viewer_canvas.create_text(
            0,
            0,
            text="Importe un DOCX",
            fill=theme.INK,
            font=(theme.FONT_UI, 18, "bold"),
            tags=("placeholder_title",),
            anchor="center",
        )
        self.viewer_canvas.create_text(
            0,
            0,
            text=(
                "TomeLinea créera une copie de travail, l'analysera,\n"
                "puis affichera le rendu fidèle calculé par son moteur."
            ),
            fill=theme.MUTED,
            font=(theme.FONT_UI, 10),
            justify="center",
            tags=("placeholder_text",),
            anchor="center",
        )

        # ---------------- Attente ----------------

        self.busy_overlay = tk.Frame(
            center,
            bg=theme.WINDOW,
        )
        self.busy_label = tk.Label(
            self.busy_overlay,
            text="",
            bg=theme.WINDOW,
            fg=theme.INK,
            font=(theme.FONT_UI, 12, "bold"),
        )
        self.busy_label.pack(
            pady=(0, 14),
        )

        self.busy_progress = ttk.Progressbar(
            self.busy_overlay,
            mode="indeterminate",
            length=300,
        )
        self.busy_progress.pack()

        # ---------------- Etat ----------------

        tk.Label(
            right,
            text="ÉTAT DU LIVRE",
            bg=theme.PANEL,
            fg=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 10, "bold"),
            anchor="w",
        ).pack(
            fill="x",
            padx=16,
            pady=(16, 10),
        )

        self.state_text = tk.Label(
            right,
            text=(
                "Source : —\n"
                "Document de travail : —\n"
                "TLDocument : —\n"
                "Rendu : —"
            ),
            bg=theme.PANEL,
            fg=theme.INK,
            font=(theme.FONT_UI, 8),
            anchor="nw",
            justify="left",
            wraplength=225,
        )
        self.state_text.pack(
            fill="x",
            padx=16,
        )

        tk.Frame(
            right,
            bg=theme.BORDER,
            height=1,
        ).pack(
            fill="x",
            padx=16,
            pady=16,
        )

        tk.Label(
            right,
            text="À CETTE ÉTAPE",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 8, "bold"),
            anchor="w",
        ).pack(
            fill="x",
            padx=16,
        )

        tk.Label(
            right,
            text=(
                "Structure uniquement.\n\n"
                "Partie → Chapitre → Section.\n"
                "Aucune opération de Structure ne modifie le rendu."
            ),
            bg=theme.PANEL,
            fg=theme.INK,
            font=(theme.FONT_UI, 8),
            anchor="nw",
            justify="left",
            wraplength=225,
        ).pack(
            fill="x",
            padx=16,
            pady=(6, 0),
        )

        self.after(
            50,
            self._position_placeholder,
        )

    def _position_placeholder(self) -> None:
        width = max(
            1,
            self.viewer_canvas.winfo_width(),
        )
        height = max(
            1,
            self.viewer_canvas.winfo_height(),
        )

        self.viewer_canvas.coords(
            "placeholder_title",
            width / 2,
            height * 0.46,
        )
        self.viewer_canvas.coords(
            "placeholder_text",
            width / 2,
            height * 0.54,
        )

    # =========================================================
    # Import
    # =========================================================

    def _set_busy(
        self,
        active: bool,
        message: str = "",
    ) -> None:
        self._busy = active

        self.import_button.configure(
            state=(
                "disabled"
                if active
                else "normal"
            )
        )

        self.refresh_button.configure(
            state=(
                "disabled"
                if active or self._working_path is None
                else "normal"
            )
        )

        if active:
            self.busy_label.configure(
                text=(
                    message
                    or "Traitement en cours…"
                )
            )
            self.busy_overlay.place(
                x=0,
                y=38,
                relwidth=1,
                relheight=1,
                height=-38,
            )
            self.busy_overlay.lift()
            self.busy_progress.start(
                12
            )
        else:
            self.busy_progress.stop()
            self.busy_overlay.place_forget()

    def _choose_docx(self) -> None:
        if self._busy:
            return

        selected = filedialog.askopenfilename(
            title="TomeLinea - Importer un manuscrit DOCX",
            filetypes=[
                ("Document Word DOCX", "*.docx"),
            ],
        )

        if not selected:
            return

        self._prepare_async(
            Path(selected).resolve()
        )

    def _prepare_async(
        self,
        source: Path,
    ) -> None:
        self._set_busy(
            True,
            "Analyse du document et calcul du rendu…",
        )
        self.top_status.configure(
            text=f"Ouverture : {source.name}"
        )

        threading.Thread(
            target=self._prepare_worker,
            args=(source,),
            daemon=True,
        ).start()

    def _prepare_worker(
        self,
        source: Path,
    ) -> None:
        try:
            source_hash = _file_sha256(
                source
            )
            work_root = (
                self.runtime_root
                / "books"
                / source_hash[:16]
            )
            work_root.mkdir(
                parents=True,
                exist_ok=True,
            )

            working = (
                work_root
                / f"{source.stem}__TL_TRAVAIL.docx"
            )

            structure_path = (
                work_root
                / "structure_logique.json"
            )

            render_dir = (
                work_root
                / "render"
            )
            render_dir.mkdir(
                parents=True,
                exist_ok=True,
            )

            shutil.copy2(
                source,
                working,
            )

            if (
                _file_sha256(source)
                != _file_sha256(working)
            ):
                raise RuntimeError(
                    "La copie de travail n'est pas identique à la Source."
                )

            logical, integrity = build_tldocument_from_docx(
                working
            )

            if not integrity.ready_for_visual_twin:
                details = "\n".join(
                    integrity.blockers[:8]
                )
                raise RuntimeError(
                    "Le document n'a pas passé le contrôle d'intégrité.\n"
                    + details
                )

            rendered = render_document_to_pdf(
                working,
                render_dir,
            )

            source_pages = _cached_docx_pages(
                working
            )
            page_count = _pdf_page_count(
                rendered.pdf_path,
                source_pages,
            )

            prepared = PreparedBook(
                source=source,
                working=working,
                pdf=rendered.pdf_path,
                structure_path=structure_path,
                page_count=page_count,
                paragraph_count=logical.counts["paragraphs"],
                image_count=logical.counts["images"],
                warning_count=len(integrity.warnings),
                render_seconds=rendered.elapsed_seconds,
                engine_origin=rendered.engine.origin,
            )

        except Exception as exc:
            self.after(
                0,
                lambda e=exc: self._prepare_failed(e),
            )
            return

        self.after(
            0,
            lambda p=prepared: self._prepare_done(p),
        )

    def _prepare_failed(
        self,
        exc: Exception,
    ) -> None:
        self._set_busy(
            False
        )
        self.top_status.configure(
            text="Ouverture interrompue"
        )
        messagebox.showerror(
            "TomeLinea",
            str(exc),
        )

    def _prepare_done(
        self,
        book: PreparedBook,
    ) -> None:
        self._source_path = book.source
        self._working_path = book.working
        self._pdf_path = book.pdf
        self._structure_path = book.structure_path
        self._page_count = book.page_count
        self._active_page_no = 1

        self._load_structure_state(
            book.page_count
        )
        self._populate_structure(
            book.page_count
        )
        self._open_pdf_document(
            book.pdf
        )
        self._show_page(
            1,
            sync_structure=True,
        )

        self.state_text.configure(
            text=(
                f"Source : intacte\n"
                f"{book.source.name}\n\n"
                f"Document de travail : prêt\n"
                f"{book.working.name}\n\n"
                f"TLDocument : prêt\n"
                f"{book.paragraph_count} paragraphes\n"
                f"{book.image_count} images\n"
                f"{book.warning_count} avertissement(s)\n\n"
                f"Rendu : prêt\n"
                f"{book.page_count} pages\n"
                f"{book.render_seconds:.2f} s\n"
                f"Moteur : {book.engine_origin}"
            )
        )

        self.top_status.configure(
            text=(
                f"{book.source.name} — "
                f"{book.page_count} pages"
            )
        )

        self.refresh_button.configure(
            state="normal"
        )
        self._set_busy(
            False
        )

    # =========================================================
    # Persistance Structure
    # =========================================================

    def _normalize_structure_state(
        self,
        page_count: int,
    ) -> None:
        valid_zones = tuple(
            STRUCTURE_ZONES
        )
        valid_zone_set = set(
            valid_zones
        )
        valid_pages = set(
            range(
                1,
                int(page_count) + 1,
            )
        )

        normalized_zone: dict[int, str] = {}

        for page_no in sorted(
            valid_pages
        ):
            zone = self._structure_zone_by_page.get(
                page_no,
                "unclassified",
            )
            if zone not in valid_zone_set:
                zone = "unclassified"
            normalized_zone[
                page_no
            ] = zone

        normalized_order: dict[
            str,
            list[int],
        ] = {
            zone: []
            for zone in valid_zones
        }

        seen: set[int] = set()

        for zone in valid_zones:
            raw = self._structure_order_by_zone.get(
                zone,
                [],
            )
            for value in raw:
                try:
                    page_no = int(
                        value
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    continue

                if (
                    page_no not in valid_pages
                    or page_no in seen
                    or normalized_zone.get(page_no) != zone
                ):
                    continue

                normalized_order[
                    zone
                ].append(
                    page_no
                )
                seen.add(
                    page_no
                )

        for page_no in sorted(
            valid_pages
        ):
            if page_no in seen:
                continue

            zone = normalized_zone.get(
                page_no,
                "unclassified",
            )
            normalized_order[
                zone
            ].append(
                page_no
            )
            seen.add(
                page_no
            )

        self._structure_zone_by_page = (
            normalized_zone
        )
        self._structure_order_by_zone = (
            normalized_order
        )

        self._normalize_body_nodes(
            page_count
        )

    def _normalize_body_nodes(
        self,
        page_count: int,
    ) -> None:
        valid_types = {
            "partie",
            "chapitre",
            "section",
        }

        cleaned: dict[
            str,
            dict[str, object],
        ] = {}

        for node_id, raw in self._body_nodes.items():
            if not isinstance(
                raw,
                dict,
            ):
                continue

            node_type = str(
                raw.get("type")
                or ""
            )
            if node_type not in valid_types:
                continue

            parent_raw = raw.get(
                "parent_id"
            )
            parent_id = (
                str(parent_raw)
                if parent_raw
                else None
            )

            cleaned[
                str(node_id)
            ] = {
                "id": str(node_id),
                "type": node_type,
                "title": str(
                    raw.get("title")
                    or node_type.capitalize()
                ),
                "parent_id": parent_id,
            }

        for node in cleaned.values():
            parent_id = node.get(
                "parent_id"
            )
            if (
                parent_id is not None
                and str(parent_id) not in cleaned
            ):
                node[
                    "parent_id"
                ] = None

        # Hiérarchie V4.
        for node in cleaned.values():
            node_type = str(
                node.get("type")
            )
            parent_id = node.get(
                "parent_id"
            )

            if node_type == "partie":
                node[
                    "parent_id"
                ] = None
                continue

            if parent_id is None:
                continue

            parent = cleaned.get(
                str(parent_id)
            )
            parent_type = (
                str(
                    parent.get("type")
                )
                if parent
                else ""
            )

            if (
                node_type == "chapitre"
                and parent_type != "partie"
            ):
                node[
                    "parent_id"
                ] = None

            if (
                node_type == "section"
                and parent_type != "chapitre"
            ):
                node[
                    "parent_id"
                ] = None

        self._body_nodes = cleaned

        ordered = [
            node_id
            for node_id in self._body_node_order
            if node_id in cleaned
        ]

        for node_id in cleaned:
            if node_id not in ordered:
                ordered.append(
                    node_id
                )

        self._body_node_order = ordered

        valid_body_pages = {
            page_no
            for page_no in range(
                1,
                int(page_count) + 1,
            )
            if self._structure_zone_by_page.get(
                page_no
            ) == "body"
        }

        self._body_node_by_page = {
            int(page_no): str(node_id)
            for page_no, node_id in self._body_node_by_page.items()
            if (
                int(page_no) in valid_body_pages
                and str(node_id) in cleaned
            )
        }

    def _load_structure_state(
        self,
        page_count: int,
    ) -> None:
        self._structure_zone_by_page = {}
        self._structure_order_by_zone = {
            zone: []
            for zone in STRUCTURE_ZONES
        }
        self._body_nodes = {}
        self._body_node_order = []
        self._body_node_by_page = {}

        path = self._structure_path

        if (
            path is not None
            and path.is_file()
        ):
            try:
                data = json.loads(
                    path.read_text(
                        encoding="utf-8"
                    )
                )

                version = int(
                    data.get(
                        "version"
                    )
                    or 0
                )

                if (
                    data.get("schema")
                    == STRUCTURE_SCHEMA
                    and version
                    in {
                        1,
                        2,
                        STRUCTURE_VERSION,
                    }
                ):
                    raw_zones = data.get(
                        "page_zones",
                        {},
                    )

                    if isinstance(
                        raw_zones,
                        dict,
                    ):
                        for key, value in raw_zones.items():
                            try:
                                page_no = int(
                                    key
                                )
                            except (
                                TypeError,
                                ValueError,
                            ):
                                continue

                            self._structure_zone_by_page[
                                page_no
                            ] = str(
                                value
                            )

                    if version >= 2:
                        raw_orders = data.get(
                            "zone_orders",
                            {},
                        )
                        if isinstance(
                            raw_orders,
                            dict,
                        ):
                            for zone in STRUCTURE_ZONES:
                                values = raw_orders.get(
                                    zone,
                                    [],
                                )
                                if isinstance(
                                    values,
                                    list,
                                ):
                                    self._structure_order_by_zone[
                                        zone
                                    ] = list(
                                        values
                                    )

                    if version >= 3:
                        raw_nodes = data.get(
                            "body_nodes",
                            [],
                        )

                        if isinstance(
                            raw_nodes,
                            list,
                        ):
                            for item in raw_nodes:
                                if not isinstance(
                                    item,
                                    dict,
                                ):
                                    continue

                                node_id = str(
                                    item.get("id")
                                    or ""
                                ).strip()

                                if not node_id:
                                    continue

                                self._body_nodes[
                                    node_id
                                ] = {
                                    "id": node_id,
                                    "type": str(
                                        item.get("type")
                                        or "section"
                                    ),
                                    "title": str(
                                        item.get("title")
                                        or ""
                                    ),
                                    "parent_id": (
                                        str(
                                            item.get(
                                                "parent_id"
                                            )
                                        )
                                        if item.get(
                                            "parent_id"
                                        )
                                        else None
                                    ),
                                }

                        raw_node_order = data.get(
                            "body_node_order",
                            [],
                        )
                        if isinstance(
                            raw_node_order,
                            list,
                        ):
                            self._body_node_order = [
                                str(value)
                                for value in raw_node_order
                            ]

                        raw_membership = data.get(
                            "body_node_by_page",
                            {},
                        )
                        if isinstance(
                            raw_membership,
                            dict,
                        ):
                            for key, value in raw_membership.items():
                                try:
                                    page_no = int(
                                        key
                                    )
                                except (
                                    TypeError,
                                    ValueError,
                                ):
                                    continue

                                self._body_node_by_page[
                                    page_no
                                ] = str(
                                    value
                                )

            except Exception:
                self._structure_zone_by_page = {}
                self._structure_order_by_zone = {
                    zone: []
                    for zone in STRUCTURE_ZONES
                }
                self._body_nodes = {}
                self._body_node_order = []
                self._body_node_by_page = {}

        self._normalize_structure_state(
            page_count
        )

    def _save_structure_state(
        self,
    ) -> None:
        path = self._structure_path

        if path is None:
            return

        payload = {
            "schema": STRUCTURE_SCHEMA,
            "version": STRUCTURE_VERSION,
            "page_zones": {
                str(page_no): zone
                for page_no, zone in sorted(
                    self._structure_zone_by_page.items()
                )
            },
            "zone_orders": {
                zone: list(
                    self._structure_order_by_zone.get(
                        zone,
                        [],
                    )
                )
                for zone in STRUCTURE_ZONES
            },
            "body_nodes": [
                {
                    "id": node_id,
                    "type": str(
                        self._body_nodes[
                            node_id
                        ].get(
                            "type",
                            "section",
                        )
                    ),
                    "title": str(
                        self._body_nodes[
                            node_id
                        ].get(
                            "title",
                            "",
                        )
                    ),
                    "parent_id": self._body_nodes[
                        node_id
                    ].get(
                        "parent_id"
                    ),
                }
                for node_id in self._body_node_order
                if node_id in self._body_nodes
            ],
            "body_node_order": [
                node_id
                for node_id in self._body_node_order
                if node_id in self._body_nodes
            ],
            "body_node_by_page": {
                str(page_no): node_id
                for page_no, node_id in sorted(
                    self._body_node_by_page.items()
                )
            },
        }

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temp = path.with_suffix(
            path.suffix + ".tmp"
        )

        temp.write_text(
            json.dumps(
                payload,
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

        temp.replace(
            path
        )

    def _pages_for_zone(
        self,
        zone: str,
    ) -> list[int]:
        return list(
            self._structure_order_by_zone.get(
                zone,
                [],
            )
        )

    # =========================================================
    # Arbre Structure
    # =========================================================

    def _populate_structure(
        self,
        page_count: int,
    ) -> None:
        self._structure_rebuilding = True
        tree = self.structure_tree

        try:
            for item in tree.get_children(
                ""
            ):
                tree.delete(
                    item
                )

            root = tree.insert(
                "",
                "end",
                iid="book",
                text="Livre",
                open=True,
            )

            for zone in (
                "prelim",
                "body",
                "end",
                "unclassified",
            ):
                pages = self._pages_for_zone(
                    zone
                )

                folder = tree.insert(
                    root,
                    "end",
                    iid=zone,
                    text=(
                        f"{STRUCTURE_ZONES[zone]} "
                        f"({len(pages)})"
                    ),
                    open=(
                        zone == "unclassified"
                        or bool(pages)
                    ),
                )

                if zone == "body":
                    self._populate_body_editorial_tree(
                        folder
                    )
                else:
                    for page_no in pages:
                        tree.insert(
                            folder,
                            "end",
                            iid=f"page:{page_no}",
                            text=f"Page {page_no}",
                        )

        finally:
            self._structure_rebuilding = False

    def _body_descendant_pages(
        self,
        node_id: str,
    ) -> list[int]:
        descendants = {
            str(node_id)
        }

        changed = True

        while changed:
            changed = False

            for candidate_id, node in self._body_nodes.items():
                parent = node.get(
                    "parent_id"
                )
                if (
                    parent in descendants
                    and candidate_id not in descendants
                ):
                    descendants.add(
                        candidate_id
                    )
                    changed = True

        return [
            int(page_no)
            for page_no in self._structure_order_by_zone.get(
                "body",
                [],
            )
            if self._body_node_by_page.get(
                int(page_no)
            ) in descendants
        ]

    def _body_node_children(
        self,
        parent_id: str | None,
    ) -> list[str]:
        result = [
            node_id
            for node_id in self._body_node_order
            if (
                node_id in self._body_nodes
                and self._body_nodes[
                    node_id
                ].get(
                    "parent_id"
                ) == parent_id
            )
        ]

        body_order = [
            int(value)
            for value in self._structure_order_by_zone.get(
                "body",
                [],
            )
        ]

        positions = {
            page_no: index
            for index, page_no in enumerate(
                body_order
            )
        }

        def first_position(
            node_id: str,
        ) -> tuple[int, int]:
            pages = self._body_descendant_pages(
                node_id
            )

            first = min(
                (
                    positions.get(
                        page_no,
                        10**9,
                    )
                    for page_no in pages
                ),
                default=10**9,
            )

            try:
                fallback = self._body_node_order.index(
                    node_id
                )
            except ValueError:
                fallback = 10**9

            return (
                first,
                fallback,
            )

        result.sort(
            key=first_position
        )
        return result

    def _body_container_items(
        self,
        parent_id: str | None,
    ) -> list[
        tuple[
            int,
            int,
            str,
            object,
        ]
    ]:
        body_order = [
            int(value)
            for value in self._structure_order_by_zone.get(
                "body",
                [],
            )
        ]

        positions = {
            page_no: index
            for index, page_no in enumerate(
                body_order
            )
        }

        items: list[
            tuple[
                int,
                int,
                str,
                object,
            ]
        ] = []

        for page_no in body_order:
            assigned = self._body_node_by_page.get(
                page_no
            )

            if parent_id is None:
                belongs = assigned is None
            else:
                belongs = assigned == parent_id

            if belongs:
                items.append(
                    (
                        positions[
                            page_no
                        ],
                        1,
                        "page",
                        page_no,
                    )
                )

        for child_id in self._body_node_children(
            parent_id
        ):
            pages = self._body_descendant_pages(
                child_id
            )

            first = min(
                (
                    positions.get(
                        page_no,
                        10**9,
                    )
                    for page_no in pages
                ),
                default=10**9,
            )

            items.append(
                (
                    first,
                    0,
                    "node",
                    child_id,
                )
            )

        items.sort(
            key=lambda item: (
                item[0],
                item[1],
            )
        )

        return items

    def _insert_body_node(
        self,
        parent_item: str,
        node_id: str,
    ) -> None:
        node = self._body_nodes.get(
            node_id
        )

        if node is None:
            return

        node_type = str(
            node.get("type")
            or "section"
        )
        title = str(
            node.get("title")
            or node_type.capitalize()
        )

        pages = self._body_descendant_pages(
            node_id
        )

        label = {
            "partie": "Partie",
            "chapitre": "Chapitre",
            "section": "Section",
        }.get(
            node_type,
            node_type.capitalize(),
        )

        tag = {
            "partie": "editorial_part",
            "chapitre": "editorial_chapter",
            "section": "editorial_section",
        }.get(
            node_type,
            "editorial_section",
        )

        iid = f"node:{node_id}"

        self.structure_tree.insert(
            parent_item,
            "end",
            iid=iid,
            text=(
                f"{label} · "
                f"{title} "
                f"({len(pages)})"
            ),
            open=True,
            tags=(tag,),
        )

        for (
            _pos,
            _rank,
            kind,
            value,
        ) in self._body_container_items(
            node_id
        ):
            if kind == "page":
                page_no = int(
                    value
                )
                self.structure_tree.insert(
                    iid,
                    "end",
                    iid=f"page:{page_no}",
                    text=f"Page {page_no}",
                )
            else:
                self._insert_body_node(
                    iid,
                    str(value),
                )

    def _populate_body_editorial_tree(
        self,
        body_item: str,
    ) -> None:
        for (
            _pos,
            _rank,
            kind,
            value,
        ) in self._body_container_items(
            None
        ):
            if kind == "page":
                page_no = int(
                    value
                )
                self.structure_tree.insert(
                    body_item,
                    "end",
                    iid=f"page:{page_no}",
                    text=f"Page {page_no}",
                )
            else:
                self._insert_body_node(
                    body_item,
                    str(value),
                )

    def _body_node_from_tree_item(
        self,
        item: str,
    ) -> str | None:
        value = str(
            item
            or ""
        )

        if not value.startswith(
            "node:"
        ):
            return None

        node_id = value.split(
            ":",
            1,
        )[1]

        return (
            node_id
            if node_id in self._body_nodes
            else None
        )

    def _body_node_ancestor_of_type(
        self,
        node_id: str | None,
        wanted_type: str,
    ) -> str | None:
        current = (
            str(node_id)
            if node_id
            else None
        )

        seen: set[str] = set()

        while (
            current
            and current not in seen
        ):
            seen.add(
                current
            )

            node = self._body_nodes.get(
                current
            )

            if node is None:
                return None

            if str(
                node.get("type")
            ) == wanted_type:
                return current

            parent = node.get(
                "parent_id"
            )

            current = (
                str(parent)
                if parent
                else None
            )

        return None

    def _selected_body_pages(
        self,
    ) -> list[int]:
        return [
            page_no
            for page_no in self._selected_structure_pages()
            if self._structure_zone_by_page.get(
                int(page_no)
            ) == "body"
        ]

    def _focused_body_node_id(
        self,
    ) -> str | None:
        return self._body_node_from_tree_item(
            str(
                self.structure_tree.focus()
                or ""
            )
        )

    def _resolve_new_node_parent(
        self,
        node_type: str,
        pages: list[int],
    ) -> str | None:
        if node_type == "partie":
            return None

        focused = self._focused_body_node_id()

        if node_type == "chapitre":
            if (
                focused
                and self._body_nodes.get(
                    focused,
                    {},
                ).get("type")
                == "partie"
            ):
                return focused

            candidates = {
                self._body_node_ancestor_of_type(
                    self._body_node_by_page.get(
                        page_no
                    ),
                    "partie",
                )
                for page_no in pages
            }
            candidates.discard(
                None
            )

            if len(candidates) == 1:
                return next(
                    iter(candidates)
                )

            return None

        # Section -> Chapitre.
        if (
            focused
            and self._body_nodes.get(
                focused,
                {},
            ).get("type")
            == "chapitre"
        ):
            return focused

        candidates = {
            self._body_node_ancestor_of_type(
                self._body_node_by_page.get(
                    page_no
                ),
                "chapitre",
            )
            for page_no in pages
        }
        candidates.discard(
            None
        )

        if len(candidates) == 1:
            return next(
                iter(candidates)
            )

        return None

    def _create_body_node(
        self,
        node_type: str,
    ) -> None:
        if node_type not in {
            "partie",
            "chapitre",
            "section",
        }:
            return

        pages = self._selected_body_pages()

        if not pages:
            messagebox.showinfo(
                "Structure",
                "Sélectionne d'abord une ou plusieurs pages dans Corps.",
            )
            return

        parent_id = self._resolve_new_node_parent(
            node_type,
            pages,
        )

        if (
            node_type == "section"
            and parent_id is None
        ):
            messagebox.showinfo(
                "Structure",
                (
                    "Pour créer une Section, sélectionne son Chapitre "
                    "ou des pages appartenant au même Chapitre."
                ),
            )
            return

        default_title = {
            "partie": "Nouvelle partie",
            "chapitre": "Nouveau chapitre",
            "section": "Nouvelle section",
        }[
            node_type
        ]

        prompt = {
            "partie": "Nom de la partie :",
            "chapitre": "Nom du chapitre :",
            "section": "Nom de la section :",
        }[
            node_type
        ]

        title = simpledialog.askstring(
            "Structure",
            prompt,
            initialvalue=default_title,
            parent=self,
        )

        if title is None:
            return

        title = title.strip()

        if not title:
            return

        node_id = str(
            uuid4()
        )

        self._body_nodes[
            node_id
        ] = {
            "id": node_id,
            "type": node_type,
            "title": title,
            "parent_id": parent_id,
        }

        self._body_node_order.append(
            node_id
        )

        for page_no in pages:
            self._body_node_by_page[
                int(page_no)
            ] = node_id

        self._normalize_body_nodes(
            self._page_count
        )
        self._save_structure_state()

        active_page = self._active_page_no

        self._populate_structure(
            self._page_count
        )

        node_item = f"node:{node_id}"

        if self.structure_tree.exists(
            node_item
        ):
            self._structure_rebuilding = True
            try:
                self.structure_tree.selection_set(
                    node_item
                )
                self.structure_tree.focus(
                    node_item
                )
                self.structure_tree.see(
                    node_item
                )
            finally:
                self._structure_rebuilding = False

        self._active_page_no = active_page
        self._update_navigation_buttons()

        self.top_status.configure(
            text=(
                f"{title} créé — "
                f"{len(pages)} page"
                f"{'s' if len(pages) > 1 else ''} — "
                "rendu inchangé"
            )
        )

    def _rename_selected_body_node(
        self,
    ) -> None:
        node_id = self._focused_body_node_id()

        if node_id is None:
            messagebox.showinfo(
                "Structure",
                (
                    "Sélectionne une Partie, un Chapitre "
                    "ou une Section à renommer."
                ),
            )
            return

        node = self._body_nodes.get(
            node_id
        )

        if node is None:
            return

        current = str(
            node.get("title")
            or ""
        )

        title = simpledialog.askstring(
            "Structure",
            "Nouveau nom :",
            initialvalue=current,
            parent=self,
        )

        if title is None:
            return

        title = title.strip()

        if not title:
            return

        node[
            "title"
        ] = title

        self._save_structure_state()

        active_page = self._active_page_no

        self._populate_structure(
            self._page_count
        )

        node_item = f"node:{node_id}"

        if self.structure_tree.exists(
            node_item
        ):
            self._structure_rebuilding = True
            try:
                self.structure_tree.selection_set(
                    node_item
                )
                self.structure_tree.focus(
                    node_item
                )
                self.structure_tree.see(
                    node_item
                )
            finally:
                self._structure_rebuilding = False

        self._active_page_no = active_page

        self.top_status.configure(
            text=(
                f"Structure renommée : {title} — "
                "rendu inchangé"
            )
        )

    def _on_structure_select(
        self,
        _event=None,
    ) -> None:
        if self._structure_rebuilding:
            return

        selection = self.structure_tree.selection()

        if not selection:
            return

        # La dernière ligne sélectionnée qui est une page devient la page active.
        page_no = None

        for item in reversed(
            selection
        ):
            candidate = self._page_no_from_tree_item(
                str(item)
            )
            if candidate is not None:
                page_no = candidate
                break

        if page_no is None:
            return

        self._show_page(
            page_no,
            sync_structure=False,
        )

    def _sync_structure_selection(
        self,
        page_no: int,
    ) -> None:
        iid = f"page:{page_no}"

        if not self.structure_tree.exists(
            iid
        ):
            return

        self._structure_rebuilding = True

        try:
            current = iid

            while current:
                parent = str(
                    self.structure_tree.parent(
                        current
                    )
                    or ""
                )

                if parent:
                    self.structure_tree.item(
                        parent,
                        open=True,
                    )

                current = parent

            self.structure_tree.selection_set(
                iid
            )
            self.structure_tree.focus(
                iid
            )
            self.structure_tree.see(
                iid
            )

        finally:
            self._structure_rebuilding = False

    # =========================================================
    # Glisser-deposer Structure
    # =========================================================

    def _page_no_from_tree_item(
        self,
        item: str,
    ) -> int | None:
        if not str(
            item
        ).startswith(
            "page:"
        ):
            return None

        try:
            return int(
                str(item).split(
                    ":",
                    1,
                )[1]
            )
        except (
            TypeError,
            ValueError,
        ):
            return None

    def _tree_zone_for_item(
        self,
        item: str,
    ) -> str | None:
        current = str(
            item
            or ""
        )

        while current:
            if current in STRUCTURE_ZONES:
                return current

            try:
                current = str(
                    self.structure_tree.parent(
                        current
                    )
                    or ""
                )
            except tk.TclError:
                return None

        return None

    def _tree_body_node_for_item(
        self,
        item: str,
    ) -> str | None:
        current = str(
            item
            or ""
        )

        while current:
            node_id = self._body_node_from_tree_item(
                current
            )
            if node_id is not None:
                return node_id

            try:
                current = str(
                    self.structure_tree.parent(
                        current
                    )
                    or ""
                )
            except tk.TclError:
                return None

        return None

    def _drop_target_from_pointer(
        self,
        event,
    ) -> tuple[
        str,
        int | None,
        str,
        str | None,
        int,
    ] | None:
        tree = self.structure_tree

        item = str(
            tree.identify_row(
                event.y
            )
            or ""
        )

        if not item or item == "book":
            return None

        try:
            bbox = tree.bbox(
                item
            )
        except tk.TclError:
            bbox = ()

        if not bbox:
            return None

        _x, row_y, _width, row_height = bbox

        before = int(
            event.y
        ) < (
            int(row_y)
            + int(row_height) / 2
        )

        page_no = self._page_no_from_tree_item(
            item
        )

        if page_no is not None:
            zone = self._tree_zone_for_item(
                item
            )

            if zone not in STRUCTURE_ZONES:
                return None

            body_node = (
                self._tree_body_node_for_item(
                    item
                )
                if zone == "body"
                else None
            )

            return (
                zone,
                page_no,
                (
                    "before"
                    if before
                    else "after"
                ),
                body_node,
                int(
                    row_y
                    if before
                    else row_y + row_height
                ),
            )

        node_id = self._body_node_from_tree_item(
            item
        )

        if node_id is not None:
            pages = self._body_descendant_pages(
                node_id
            )

            if pages:
                anchor = (
                    pages[0]
                    if before
                    else pages[-1]
                )
                position = (
                    "before"
                    if before
                    else "after"
                )
            else:
                anchor = None
                position = "end"

            return (
                "body",
                anchor,
                position,
                node_id,
                int(
                    row_y
                    if before
                    else row_y + row_height
                ),
            )

        if item not in STRUCTURE_ZONES:
            return None

        zone = item
        pages = self._pages_for_zone(
            zone
        )

        if not pages:
            return (
                zone,
                None,
                "end",
                None,
                int(
                    row_y + row_height
                ),
            )

        if before:
            anchor = pages[0]
            position = "before"
        else:
            anchor = pages[-1]
            position = "after"

        return (
            zone,
            anchor,
            position,
            None,
            int(
                row_y
                if before
                else row_y + row_height
            ),
        )

    def _hide_drop_line(
        self,
    ) -> None:
        try:
            self._drop_line.place_forget()
        except Exception:
            pass

        self._drag_target = None

    def _show_drop_line(
        self,
        line_y: int,
    ) -> None:
        try:
            width = max(
                20,
                self.structure_tree.winfo_width()
                - 8,
            )

            self._drop_line.place(
                x=(
                    self.structure_tree.winfo_x()
                    + 4
                ),
                y=(
                    self.structure_tree.winfo_y()
                    + int(line_y)
                    - 1
                ),
                width=width,
                height=2,
            )

            self._drop_line.lift()

        except Exception:
            self._hide_drop_line()

    def _selected_structure_pages(
        self,
        *,
        include_page: int | None = None,
    ) -> list[int]:
        selected: set[int] = set()

        for item in self.structure_tree.selection():
            page_no = self._page_no_from_tree_item(
                str(item)
            )
            if page_no is not None:
                selected.add(
                    page_no
                )

        if include_page is not None:
            selected.add(
                int(include_page)
            )

        sequence = self._logical_navigation_sequence()

        ordered = [
            page_no
            for page_no in sequence
            if page_no in selected
        ]

        for page_no in sorted(
            selected
        ):
            if page_no not in ordered:
                ordered.append(
                    page_no
                )

        return ordered

    def _on_structure_button_press(
        self,
        event,
    ) -> None:
        self._hide_drop_line()

        self._drag_page_no = None
        self._drag_page_nos = []
        self._drag_start_xy = None
        self._dragging = False

        item = str(
            self.structure_tree.identify_row(
                event.y
            )
            or ""
        )

        page_no = self._page_no_from_tree_item(
            item
        )

        if page_no is None:
            return

        self._drag_page_no = page_no
        self._drag_page_nos = self._selected_structure_pages(
            include_page=page_no
        )
        self._drag_start_xy = (
            int(event.x),
            int(event.y),
        )

    def _on_structure_drag_motion(
        self,
        event,
    ) -> None:
        if (
            self._drag_page_no is None
            or self._drag_start_xy is None
        ):
            return

        if not self._dragging:
            distance = (
                abs(
                    int(event.x)
                    - self._drag_start_xy[0]
                )
                + abs(
                    int(event.y)
                    - self._drag_start_xy[1]
                )
            )

            if distance < 7:
                return

            self._dragging = True
            self._drag_page_nos = self._selected_structure_pages(
                include_page=self._drag_page_no
            )

            try:
                self.structure_tree.configure(
                    cursor="fleur"
                )
            except tk.TclError:
                pass

        try:
            height = max(
                1,
                self.structure_tree.winfo_height(),
            )

            if int(
                event.y
            ) < 24:
                self.structure_tree.yview_scroll(
                    -1,
                    "units",
                )
            elif int(
                event.y
            ) > (
                height - 24
            ):
                self.structure_tree.yview_scroll(
                    1,
                    "units",
                )

        except Exception:
            pass

        candidate = self._drop_target_from_pointer(
            event
        )

        if candidate is None:
            self._hide_drop_line()
            return

        (
            zone,
            anchor_page,
            position,
            body_node,
            line_y,
        ) = candidate

        if (
            anchor_page is not None
            and anchor_page
            in self._drag_page_nos
        ):
            self._hide_drop_line()
            return

        self._drag_target = (
            zone,
            anchor_page,
            position,
            body_node,
        )

        self._show_drop_line(
            line_y
        )

    def _on_structure_button_release(
        self,
        _event,
    ) -> None:
        page_no = self._drag_page_no
        page_nos = list(
            self._drag_page_nos
        )
        dragging = bool(
            self._dragging
        )
        target = self._drag_target

        self._drag_page_no = None
        self._drag_page_nos = []
        self._drag_start_xy = None
        self._dragging = False

        self._hide_drop_line()

        try:
            self.structure_tree.configure(
                cursor=""
            )
        except tk.TclError:
            pass

        if (
            not dragging
            or page_no is None
            or target is None
        ):
            return

        if not page_nos:
            page_nos = [
                page_no
            ]

        (
            zone,
            anchor_page,
            position,
            body_node,
        ) = target

        self._move_pages_logically(
            page_nos,
            zone,
            anchor_page=anchor_page,
            position=position,
            body_node_id=body_node,
        )

    def _move_pages_logically(
        self,
        page_nos: list[int],
        zone: str,
        *,
        anchor_page: int | None,
        position: str,
        body_node_id: str | None = None,
    ) -> None:
        if zone not in STRUCTURE_ZONES:
            return

        requested = {
            int(value)
            for value in page_nos
            if (
                1
                <= int(value)
                <= self._page_count
            )
        }

        if not requested:
            return

        current_sequence = self._logical_navigation_sequence()

        valid_pages = [
            page_no
            for page_no in current_sequence
            if page_no in requested
        ]

        if (
            anchor_page is not None
            and int(anchor_page)
            in requested
        ):
            return

        for candidate_zone in STRUCTURE_ZONES:
            self._structure_order_by_zone[
                candidate_zone
            ] = [
                value
                for value in self._structure_order_by_zone.get(
                    candidate_zone,
                    [],
                )
                if int(value)
                not in requested
            ]

        for page_no in valid_pages:
            self._structure_zone_by_page[
                page_no
            ] = zone

            if zone == "body":
                if (
                    body_node_id is not None
                    and body_node_id
                    in self._body_nodes
                ):
                    self._body_node_by_page[
                        page_no
                    ] = body_node_id
                else:
                    self._body_node_by_page.pop(
                        page_no,
                        None,
                    )
            else:
                self._body_node_by_page.pop(
                    page_no,
                    None,
                )

        target = self._structure_order_by_zone.setdefault(
            zone,
            [],
        )

        if (
            anchor_page is not None
            and int(anchor_page)
            in target
        ):
            index = target.index(
                int(anchor_page)
            )

            if position == "after":
                index += 1

        elif position == "before":
            index = 0

        else:
            index = len(
                target
            )

        for offset, page_no in enumerate(
            valid_pages
        ):
            target.insert(
                index + offset,
                page_no,
            )

        self._normalize_structure_state(
            self._page_count
        )
        self._save_structure_state()

        self._populate_structure(
            self._page_count
        )

        moved_items = [
            f"page:{page_no}"
            for page_no in valid_pages
            if self.structure_tree.exists(
                f"page:{page_no}"
            )
        ]

        if moved_items:
            self._structure_rebuilding = True

            try:
                self.structure_tree.selection_set(
                    moved_items
                )
                self.structure_tree.focus(
                    moved_items[0]
                )
                self.structure_tree.see(
                    moved_items[0]
                )

            finally:
                self._structure_rebuilding = False

        self._update_navigation_buttons()

        count = len(
            valid_pages
        )

        self.top_status.configure(
            text=(
                f"{count} page"
                f"{'s' if count > 1 else ''} classée"
                f"{'s' if count > 1 else ''} dans "
                f"« {STRUCTURE_ZONES[zone]} » — "
                "rendu inchangé"
            )
        )

    def _move_page_logically(
        self,
        page_no: int,
        zone: str,
        *,
        anchor_page: int | None,
        position: str,
    ) -> None:
        self._move_pages_logically(
            [
                int(
                    page_no
                )
            ],
            zone,
            anchor_page=anchor_page,
            position=position,
        )

    # =========================================================
    # Visionneur PDF direct
    # =========================================================

    def _close_pdf_document(
        self,
    ) -> None:
        document = self._pdf_document
        self._pdf_document = None

        if document is not None:
            try:
                document.close()
            except Exception:
                pass

    def _open_pdf_document(
        self,
        pdf_path: Path,
    ) -> None:
        self._close_pdf_document()

        self._pdf_document = pymupdf.open(
            pdf_path
        )

    def _show_page(
        self,
        page_no: int,
        *,
        sync_structure: bool,
    ) -> None:
        document = self._pdf_document

        if document is None:
            return

        if document.page_count <= 0:
            return

        page_no = max(
            1,
            min(
                int(page_no),
                int(
                    document.page_count
                ),
            ),
        )

        self._active_page_no = page_no
        self._page_count = int(
            document.page_count
        )

        self.page_label.configure(
            text=(
                f"Page {page_no} / "
                f"{self._page_count}"
            )
        )

        self._update_navigation_buttons()

        self._render_active_page()

        if sync_structure:
            self._sync_structure_selection(
                page_no
            )

    def _render_active_page(
        self,
    ) -> None:
        document = self._pdf_document

        if document is None:
            return

        page_index = max(
            0,
            min(
                self._active_page_no
                - 1,
                document.page_count
                - 1,
            ),
        )

        page = document.load_page(
            page_index
        )
        rect = page.rect

        canvas_width = max(
            120,
            self.viewer_canvas.winfo_width(),
        )
        canvas_height = max(
            120,
            self.viewer_canvas.winfo_height(),
        )

        margin = 30

        available_width = max(
            50,
            canvas_width
            - margin * 2,
        )
        available_height = max(
            50,
            canvas_height
            - margin * 2,
        )

        zoom = min(
            available_width
            / max(
                1.0,
                rect.width,
            ),
            available_height
            / max(
                1.0,
                rect.height,
            ),
        )

        zoom = max(
            0.2,
            min(
                zoom,
                2.5,
            ),
        )

        pixmap = page.get_pixmap(
            matrix=pymupdf.Matrix(
                zoom,
                zoom,
            ),
            alpha=False,
        )

        image = Image.frombytes(
            "RGB",
            (
                pixmap.width,
                pixmap.height,
            ),
            pixmap.samples,
        )

        photo = ImageTk.PhotoImage(
            image=image
        )
        self._page_photo = photo

        self.viewer_canvas.delete(
            "all"
        )

        x = canvas_width / 2
        y = canvas_height / 2

        self.viewer_canvas.create_rectangle(
            x
            - pixmap.width / 2
            - 1,
            y
            - pixmap.height / 2
            - 1,
            x
            + pixmap.width / 2
            + 1,
            y
            + pixmap.height / 2
            + 1,
            fill=theme.PAGE_BORDER,
            outline="",
        )

        self.viewer_canvas.create_image(
            x,
            y,
            image=photo,
            anchor="center",
        )

    def _on_viewer_resize(
        self,
        _event=None,
    ) -> None:
        if self._resize_after_id is not None:
            try:
                self.after_cancel(
                    self._resize_after_id
                )
            except Exception:
                pass

        if self._pdf_document is None:
            self._position_placeholder()
            return

        self._resize_after_id = self.after(
            120,
            self._render_after_resize,
        )

    def _render_after_resize(
        self,
    ) -> None:
        self._resize_after_id = None

        if self._pdf_document is not None:
            self._render_active_page()

    # =========================================================
    # Navigation logique
    # =========================================================

    def _body_logical_sequence(
        self,
    ) -> list[int]:
        result: list[int] = []

        def walk(
            parent_id: str | None,
        ) -> None:
            for (
                _pos,
                _rank,
                kind,
                value,
            ) in self._body_container_items(
                parent_id
            ):
                if kind == "page":
                    result.append(
                        int(value)
                    )
                else:
                    walk(
                        str(value)
                    )

        walk(
            None
        )

        return result

    def _logical_navigation_sequence(
        self,
    ) -> list[int]:
        sequence: list[int] = []
        seen: set[int] = set()

        for zone in (
            "prelim",
            "body",
            "end",
            "unclassified",
        ):
            if zone == "body":
                values = self._body_logical_sequence()
            else:
                values = self._structure_order_by_zone.get(
                    zone,
                    [],
                )

            for value in values:
                try:
                    page_no = int(
                        value
                    )
                except (
                    TypeError,
                    ValueError,
                ):
                    continue

                if (
                    1
                    <= page_no
                    <= self._page_count
                    and page_no
                    not in seen
                ):
                    sequence.append(
                        page_no
                    )
                    seen.add(
                        page_no
                    )

        for page_no in range(
            1,
            self._page_count + 1,
        ):
            if page_no not in seen:
                sequence.append(
                    page_no
                )
                seen.add(
                    page_no
                )

        return sequence

    def _logical_navigation_index(
        self,
    ) -> tuple[
        list[int],
        int | None,
    ]:
        sequence = self._logical_navigation_sequence()

        try:
            index = sequence.index(
                int(
                    self._active_page_no
                )
            )
        except ValueError:
            index = None

        return (
            sequence,
            index,
        )

    def _update_navigation_buttons(
        self,
    ) -> None:
        sequence, index = self._logical_navigation_index()

        self.prev_button.configure(
            state=(
                "normal"
                if (
                    index is not None
                    and index > 0
                )
                else "disabled"
            )
        )

        self.next_button.configure(
            state=(
                "normal"
                if (
                    index is not None
                    and index
                    < len(sequence) - 1
                )
                else "disabled"
            )
        )

    def _previous_page(
        self,
    ) -> None:
        sequence, index = self._logical_navigation_index()

        if (
            index is None
            or index <= 0
        ):
            return

        self._show_page(
            sequence[
                index - 1
            ],
            sync_structure=True,
        )

    def _next_page(
        self,
    ) -> None:
        sequence, index = self._logical_navigation_index()

        if (
            index is None
            or index
            >= len(sequence) - 1
        ):
            return

        self._show_page(
            sequence[
                index + 1
            ],
            sync_structure=True,
        )

    # =========================================================
    # Recalcul reel du document
    # =========================================================

    def _refresh_render(
        self,
    ) -> None:
        if (
            self._working_path is None
            or self._busy
        ):
            return

        working = self._working_path
        previous_page = self._active_page_no

        self._set_busy(
            True,
            "Recalcul de la mise en page…",
        )

        def worker() -> None:
            try:
                render_dir = (
                    working.parent
                    / "render_refresh"
                )
                render_dir.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                rendered = render_document_to_pdf(
                    working,
                    render_dir,
                )

                pages = _pdf_page_count(
                    rendered.pdf_path,
                    _cached_docx_pages(
                        working
                    ),
                )

                self.after(
                    0,
                    lambda: self._refresh_done(
                        rendered.pdf_path,
                        pages,
                        rendered.elapsed_seconds,
                        previous_page,
                    ),
                )

            except Exception as exc:
                self.after(
                    0,
                    lambda e=exc: self._prepare_failed(e),
                )

        threading.Thread(
            target=worker,
            daemon=True,
        ).start()

    def _refresh_done(
        self,
        pdf_path: Path,
        pages: int,
        elapsed: float,
        previous_page: int,
    ) -> None:
        old_count = self._page_count

        self._pdf_path = pdf_path
        self._page_count = pages

        self._open_pdf_document(
            pdf_path
        )

        if pages != old_count:
            self._normalize_structure_state(
                pages
            )
            self._save_structure_state()
            self._populate_structure(
                pages
            )

        target = max(
            1,
            min(
                previous_page,
                pages,
            ),
        )

        self._show_page(
            target,
            sync_structure=True,
        )

        self.top_status.configure(
            text=(
                f"Rendu recalculé — "
                f"{pages} pages — "
                f"{elapsed:.2f} s"
            )
        )

        self._set_busy(
            False
        )

    def destroy(
        self,
    ) -> None:
        self._close_pdf_document()
        super().destroy()


__all__ = [
    "TomeLineaV5SequentialShell",
]