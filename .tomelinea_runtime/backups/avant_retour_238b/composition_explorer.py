from __future__ import annotations

import re
import textwrap
import unicodedata
import tkinter as tk
from tkinter import ttk
from typing import Any

from src.gui_v4 import theme
from src.gui_v4.controls import TLScrollbar
from src.v4.structure_auto import is_auto_origin_page
from src.v4.structure_covers import (
    BACK_COVER,
    FRONT_COVER,
    INSIDE_BACK_COVER,
    INSIDE_FRONT_COVER,
    cover_face,
    cover_label,
)
from src.v4.book_pagination import interior_page_number
from src.v4.structure_parity import RECTO, VERSO, physical_side
from src.v4.structure_spreads import page_spread


def _norm(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = "".join(
        ch for ch in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(ch)
    )
    text = re.sub(r"\s+", " ", text)
    return text


def _is_part_title(title: str) -> bool:
    norm = _norm(title)

    if re.fullmatch(r"[ivxlcdm]+", norm):
        return True

    return bool(
        re.search(
            r"\bpartie\b",
            norm,
        )
    )


def _root_for_group(
    title: str,
    pages: list[tuple[int, str, Any]],
    total_pages: int,
) -> str:
    norm = _norm(title)

    if (
        norm in {"debut", "preliminaires", "preliminaire"}
        or norm.startswith("debut ")
    ):
        return "debut"

    if (
        norm in {"fin", "fin du livre"}
        or norm.startswith("fin ")
    ):
        return "fin"

    # Les faces physiques suffisent à placer les extrémités,
    # même si l'analyse éditoriale n'a pas encore nommé le groupe.
    cover_numbers = []

    for number, _page_id, page in pages:
        try:
            face = cover_face(page)
        except Exception:
            face = None

        if face is not None:
            cover_numbers.append(
                int(number)
            )

    if cover_numbers:
        if min(cover_numbers) <= 2:
            return "debut"

        if max(cover_numbers) >= max(1, total_pages - 1):
            return "fin"

    # Quelques intitulés usuels de fin d'ouvrage.
    # Ils servent uniquement à la navigation : aucune donnée du Livre
    # n'est modifiée par cette classification d'affichage.
    if norm and (
        "remerciement" in norm
        or "glossaire" in norm
        or "acheve" in norm
        or "auteur" in norm
        or norm.startswith("notes")
    ):
        return "fin"

    return "corps"


def navigation_model(book: Any) -> dict[str, Any]:
    """Construit Structure depuis la hiérarchie réelle du Livre.

    Règles 2.38A :
    - Début / Corps / Fin sont les seules racines fixes ;
    - aucune branche artificielle « Sans partie » ou « Ouverture » ;
    - un chapitre réel porte directement ses pages ;
    - une vraie Partie contient ses chapitres ;
    - sans vraie Partie, les chapitres sont directement sous Corps ;
    - les quatre faces physiques sont rangées dans Début / Fin.
    """

    page_order = list(getattr(book, "page_order", ()) or ())
    pages = getattr(book, "pages", {}) or {}
    parts = getattr(book, "parts", {}) or {}
    part_order = list(getattr(book, "part_order", ()) or ())

    roots = {
        "debut": {
            "id": "root:debut",
            "label": "Début",
            "count": 0,
            "kind": "root",
            "pages": [],
            "children": [],
        },
        "corps": {
            "id": "root:corps",
            "label": "Corps",
            "count": 0,
            "kind": "root",
            "pages": [],
            "children": [],
        },
        "fin": {
            "id": "root:fin",
            "label": "Fin",
            "count": 0,
            "kind": "root",
            "pages": [],
            "children": [],
        },
    }

    direct_pages: dict[str | None, list[tuple[int, str, Any]]] = {}
    body_count = 0

    for number, page_id in enumerate(page_order, start=1):
        page = pages.get(page_id)
        if page is None:
            continue

        face = None
        try:
            face = cover_face(page)
        except Exception:
            pass

        data = (number, str(page_id), page)

        if face in {FRONT_COVER, INSIDE_FRONT_COVER}:
            roots["debut"]["pages"].append(data)
            roots["debut"]["count"] += 1
            continue

        if face in {INSIDE_BACK_COVER, BACK_COVER}:
            roots["fin"]["pages"].append(data)
            roots["fin"]["count"] += 1
            continue

        part_id = getattr(page, "part_id", None)
        part = parts.get(part_id) if part_id is not None else None
        part_type = _norm(getattr(part, "part_type", "")) if part is not None else ""

        if part_type in {"debut", "préliminaires", "preliminaires", "liminaires"}:
            roots["debut"]["pages"].append(data)
            roots["debut"]["count"] += 1
            continue

        if part_type in {"fin", "annexe", "annexes"}:
            roots["fin"]["pages"].append(data)
            roots["fin"]["count"] += 1
            continue

        direct_pages.setdefault(part_id, []).append(data)
        body_count += 1

    roots["corps"]["count"] = body_count

    # Les parties réellement connues du Livre sont l'autorité. Les IDs non
    # présents dans part_order sont ajoutés après, dans l'ordre de leurs pages.
    ordered_part_ids: list[str] = []
    for part_id in part_order:
        if part_id in parts and part_id not in ordered_part_ids:
            ordered_part_ids.append(part_id)

    first_position = {
        part_id: values[0][0]
        for part_id, values in direct_pages.items()
        if part_id is not None and values
    }
    for part_id in sorted(
        (pid for pid in direct_pages if pid is not None and pid not in ordered_part_ids),
        key=lambda pid: first_position.get(pid, 10**9),
    ):
        ordered_part_ids.append(part_id)

    nodes: dict[str, dict[str, Any]] = {}

    for part_id in ordered_part_ids:
        part = parts.get(part_id)
        if part is None:
            continue

        part_type = _norm(getattr(part, "part_type", ""))
        if part_type in {"debut", "fin"}:
            continue

        part_pages = list(direct_pages.get(part_id, ()))
        title = str(getattr(part, "title", "") or "").strip()

        if part_type in {"corps", "body"}:
            roots["corps"]["pages"].extend(part_pages)
            continue

        if part_type in {"partie", "part"}:
            role = "part"
            kind = "branch"
            label = title or "Partie"
        elif part_type in {"chapitre", "chapter"}:
            role = "chapter"
            kind = "terminal"
            label = title or "Chapitre"
        else:
            # Un niveau existant mais non typé reste visible tel quel ; on ne
            # lui invente ni « Partie » ni « Chapitre ».
            role = "group"
            kind = "terminal"
            label = title or "Pages du corps"

        nodes[part_id] = {
            "id": f"structure:{part_id}",
            "part_id": part_id,
            "label": label,
            "kind": kind,
            "role": role,
            "pages": part_pages,
            "children": [],
            "parent_id": getattr(part, "parent_id", None),
        }

    for part_id in ordered_part_ids:
        node = nodes.get(part_id)
        if node is None:
            continue

        parent_id = node.get("parent_id")
        parent = nodes.get(str(parent_id)) if parent_id is not None else None
        if parent is not None and parent.get("role") == "part":
            parent["children"].append(node)
        else:
            roots["corps"]["children"].append(node)

    # Pages réellement sans niveau : directement sous Corps. Aucun dossier
    # « Sans partie » n'est créé.
    roots["corps"]["pages"].extend(direct_pages.get(None, ()))

    # Ordre physique stable pour les pages directes des racines.
    for root in roots.values():
        root["pages"] = sorted(root.get("pages", ()), key=lambda item: item[0])

    return {
        "roots": [
            roots["debut"],
            roots["corps"],
            roots["fin"],
        ],
        "page_count": len(page_order),
    }

class CompositionExplorer(tk.Frame):
    """Navigation stable de type Explorateur Windows."""

    FOLDER_COLOR = "#D8B875"
    PAGE_COLOR = "#D7D2C7"
    AUTO_PAGE_COLOR = "#D77973"
    SPREAD_COLOR = "#AFC7D2"
    SPREAD_BACKGROUND = "#394852"

    def __init__(
        self,
        parent,
        *,
        app,
        book,
    ):
        super().__init__(
            parent,
            bg=theme.PANEL,
        )

        self.app = app
        self.book = book
        self.page_items: dict[str, str] = {}
        self.item_pages: dict[str, tuple[str, ...]] = {}
        self.item_page_columns: dict[str, dict[str, str]] = {}
        self.folder_pages: dict[str, list[tuple[int, str, Any]]] = {}
        self.loaded_folders: set[str] = set()
        self.auto_page_ids: set[str] = set()
        self.chapter_folder_ids: set[str] = set()
        self._built_once = False

        # Glisser-déposer Structure : le Treeview ne modifie jamais lui-même
        # l'ordre du Livre. Il ne fait que décrire la cible au moteur V4.
        self._drag_candidate_page_id: str | None = None
        self._drag_start_xy: tuple[int, int] | None = None
        self._dragging = False
        self._drag_target: tuple[str, str] | None = None

        style = ttk.Style(self)
        self._style_name = "TomeLineaNav.Treeview"

        # Sous certains themes Windows, le fond natif du Treeview reste
        # blanc sous la derniere ligne meme si fieldbackground est configure.
        # On reutilise uniquement l'element de fond du theme ttk "clam" pour
        # CE Treeview. Le theme global de TomeLinea n'est donc pas modifie.
        field_element = "TomeLineaNav.Treeview.field"
        try:
            style.element_create(
                field_element,
                "from",
                "clam",
                "Treeview.field",
            )
        except tk.TclError:
            # L'element existe deja si le bureau a ete reconstruit.
            pass

        try:
            style.layout(
                self._style_name,
                [
                    (
                        field_element,
                        {
                            "sticky": "nswe",
                            "border": "0",
                            "children": [
                                (
                                    "Treeview.padding",
                                    {
                                        "sticky": "nswe",
                                        "children": [
                                            (
                                                "Treeview.treearea",
                                                {"sticky": "nswe"},
                                            )
                                        ],
                                    },
                                )
                            ],
                        },
                    )
                ],
            )
        except tk.TclError:
            # Repli de securite : le style configure ci-dessous reste valable.
            pass

        style.configure(
            self._style_name,
            background=theme.PANEL,
            fieldbackground=theme.PANEL,
            foreground=theme.INK,
            borderwidth=0,
            relief="flat",
            rowheight=38,
            font=(theme.FONT_UI, 9),
        )

        style.map(
            self._style_name,
            background=[
                ("selected", theme.PANEL_SOFT),
            ],
            foreground=[
                ("selected", theme.INK),
            ],
        )

        self.tree = ttk.Treeview(
            self,
            columns=("right_page",),
            show="tree",
            selectmode="none",
            style=self._style_name,
            takefocus=True,
        )

        # L'arbre occupe un peu plus de la moitie gauche pour que les titres
        # de structure restent lisibles. La zone droite est assez large pour
        # afficher un recto sur deux lignes sans le tronquer au bord.
        self.tree.column(
            "#0",
            width=195,
            minwidth=155,
            stretch=True,
            anchor="w",
        )
        self.tree.column(
            "right_page",
            width=165,
            minwidth=135,
            stretch=True,
            anchor="center",
        )

        scroll = TLScrollbar(
            self,
            orient="vertical",
            command=self.tree.yview,
        )

        self.tree.configure(
            yscrollcommand=scroll.set,
        )

        scroll.pack(
            side="right",
            fill="y",
        )

        self.tree.pack(
            side="left",
            fill="both",
            expand=True,
        )

        # Ligne d'insertion discrète pendant un clic-glisser. Elle est un
        # simple retour visuel : le déplacement réel reste transactionnel.
        self._drop_line = tk.Frame(
            self,
            bg=theme.ACCENT_BRIGHT,
            height=2,
        )

        self.tree.tag_configure(
            "active",
            background=theme.ERROR,
            foreground=theme.WHITE,
            font=(theme.FONT_UI, 8, "bold"),
        )
        self.tree.tag_configure(
            "selected_page",
            background=theme.ERROR,
            foreground=theme.WHITE,
            font=(theme.FONT_UI, 8, "bold"),
        )
        self.tree.tag_configure(
            "folder",
            foreground=self.FOLDER_COLOR,
            font=(theme.FONT_UI, 9, "bold"),
        )
        self.tree.tag_configure(
            "active_chapter",
            background=theme.PANEL_SOFT,
            foreground=self.FOLDER_COLOR,
            font=(theme.FONT_UI, 9, "bold"),
        )
        self.tree.tag_configure(
            "page",
            foreground=self.PAGE_COLOR,
            font=(theme.FONT_UI, 8),
        )
        self.tree.tag_configure(
            "auto_page",
            foreground=self.AUTO_PAGE_COLOR,
            font=(theme.FONT_UI, 8, "bold"),
        )
        self.tree.tag_configure(
            "double_page",
            background=self.SPREAD_BACKGROUND,
            foreground=self.SPREAD_COLOR,
            font=(theme.FONT_UI, 8, "bold"),
        )
        self.tree.tag_configure(
            "double_auto_page",
            background=self.SPREAD_BACKGROUND,
            foreground=self.AUTO_PAGE_COLOR,
            font=(theme.FONT_UI, 8, "bold"),
        )

        self.tree.bind(
            "<<TreeviewOpen>>",
            self._on_open,
            add="+",
        )
        self.tree.bind(
            "<<TreeviewClose>>",
            self._on_close,
            add="+",
        )
        self.tree.bind(
            "<ButtonPress-1>",
            self._on_button_press,
            add="+",
        )
        self.tree.bind(
            "<B1-Motion>",
            self._on_drag_motion,
            add="+",
        )
        self.tree.bind(
            "<ButtonRelease-1>",
            self._on_button_release,
            add="+",
        )
        self.tree.bind(
            "<MouseWheel>",
            self._on_mousewheel,
            add="+",
        )
        self.tree.bind(
            "<Configure>",
            self._on_tree_resize,
            add="+",
        )

        self.refresh()

    def _page_side(
        self,
        page_id: str,
        number: int,
    ) -> str:
        """Renvoie le cote physique utilise pour la disposition visuelle."""

        try:
            side = physical_side(
                self.book,
                str(page_id),
            )
        except Exception:
            side = None

        if side in {RECTO, VERSO}:
            return str(side)

        # Certaines faces de couverture peuvent etre exclues du calcul
        # de parite. L'Explorateur garde alors l'alternance de l'ordre reel.
        return (
            RECTO
            if int(number) % 2 == 1
            else VERSO
        )

    def _spread_for_page(
        self,
        page_id: str,
    ):
        try:
            return page_spread(
                self.book,
                str(page_id),
            )
        except Exception:
            return None

    def _on_tree_resize(
        self,
        event,
    ) -> None:
        """Repartit la largeur pour que le recto ne soit plus coupe."""

        try:
            total = max(300, int(event.width) - 8)
            right = max(140, int(total * 0.46))
            left = max(160, total - right)
            self.tree.column(
                "#0",
                width=left,
            )
            self.tree.column(
                "right_page",
                width=right,
            )
        except Exception:
            return

    def _is_automatic_blank_page(self, page: Any) -> bool:
        """Repère toute page née automatiquement, couvertures comprises."""

        try:
            automatic = bool(is_auto_origin_page(page))
        except Exception:
            automatic = False

        metadata = getattr(page, "metadata", None)
        if isinstance(metadata, dict):
            automatic = automatic or bool(
                metadata.get("generated_cover_placeholder")
                or metadata.get("automatic_page")
                or metadata.get("automatic_origin")
            )

        return automatic

    def _page_caption(
        self,
        number: int,
        page: Any,
    ) -> str:
        """Libellé compact ; les couvertures gardent leur rôle physique."""

        try:
            face = cover_face(page)
        except Exception:
            face = None

        if face is not None:
            return cover_label(page)

        page_type = str(
            getattr(page, "page_type", "")
            or ""
        ).strip()

        page_title = str(
            getattr(page, "title", "")
            or ""
        ).strip()

        page_name = page_title or page_type or "Page"

        # La Structure affiche la pagination intérieure réelle : les quatre
        # faces de couverture existent physiquement mais ne décalent jamais p. 1.
        display_number = interior_page_number(
            self.book,
            str(getattr(page, "id", "") or ""),
        )
        if display_number is None:
            display_number = int(number)

        raw = f"p. {display_number} · {page_name}"
        lines = textwrap.wrap(
            raw,
            width=24,
            break_long_words=False,
            break_on_hyphens=False,
        )

        if not lines:
            return raw
        if len(lines) <= 2:
            return "\n".join(lines)

        second = " ".join(lines[1:]).strip()
        if len(second) > 24:
            second = second[:23].rstrip() + "…"
        return f"{lines[0]}\n{second}"

    def _close_descendants(self, item: str) -> None:
        """Referme recursivement tout ce qui se trouve sous ``item``."""

        for child in self.tree.get_children(item):
            self._close_descendants(str(child))

            try:
                self.tree.item(
                    child,
                    open=False,
                )
            except tk.TclError:
                pass

    def _saved_open_nodes(self) -> set[str]:
        value = getattr(
            self.app,
            "_composition_tree_open_nodes",
            set(),
        )
        if not isinstance(value, set):
            value = set(value or ())
        return {
            str(item)
            for item in value
        }

    def _save_open_nodes(self) -> None:
        opened: set[str] = set()

        def walk(parent: str) -> None:
            for item in self.tree.get_children(parent):
                if bool(self.tree.item(item, "open")):
                    opened.add(str(item))
                walk(item)

        walk("")
        self.app._composition_tree_open_nodes = opened

    def _insert_folder(
        self,
        parent: str,
        *,
        item_id: str,
        label: str,
        pages: list[tuple[int, str, Any]] | None = None,
        open_state: bool = False,
    ) -> str:
        item = self.tree.insert(
            parent,
            "end",
            iid=item_id,
            text=label,
            open=False,
            tags=("folder",),
        )

        if pages:
            self.folder_pages[item_id] = list(pages)
            self.tree.insert(
                item,
                "end",
                iid=f"dummy:{item_id}",
                text="",
            )

        if open_state:
            if pages:
                self._load_pages(item_id)
            self.tree.item(
                item,
                open=True,
            )

        return item

    def _node_page_count(
        self,
        node: dict[str, Any],
    ) -> int:
        total = len(
            list(
                node.get(
                    "pages",
                    (),
                )
                or ()
            )
        )

        for child in (
            node.get(
                "children",
                (),
            )
            or ()
        ):
            total += self._node_page_count(
                child
            )

        return total

    def _insert_node(
        self,
        parent: str,
        node: dict[str, Any],
        opened: set[str],
    ) -> None:
        item_id = str(node["id"])
        base_label = str(node["label"])
        page_count = self._node_page_count(node)
        label = (
            f"{base_label}   {page_count} p."
            if page_count > 0
            else base_label
        )
        pages = list(node.get("pages", ()) or ())
        role = str(node.get("role") or "")

        item = self._insert_folder(
            parent,
            item_id=item_id,
            label=label,
            pages=(pages if pages else None),
            open_state=False,
        )

        if role == "chapter":
            self.chapter_folder_ids.add(item_id)

        # Une vraie Partie peut porter sa page d'ouverture et ses chapitres.
        # On crée ses lignes de pages avant les sous-chapitres afin de garder
        # l'ordre naturel, sans ajouter un faux dossier « Ouverture ».
        if role == "part" and pages:
            self._load_pages(item_id)

        for child in node.get("children", ()) or ():
            self._insert_node(item, child, opened)

        if item_id in opened:
            if item_id in self.folder_pages:
                self._load_pages(item_id)
            try:
                self.tree.item(item_id, open=True)
            except tk.TclError:
                pass

    def refresh(
        self,
        *,
        focus_page_id: str | None = None,
    ) -> None:
        if self._built_once:
            self._save_open_nodes()

        opened = self._saved_open_nodes()

        self.page_items.clear()
        self.item_pages.clear()
        self.item_page_columns.clear()
        self.folder_pages.clear()
        self.loaded_folders.clear()
        self.auto_page_ids.clear()
        self.chapter_folder_ids.clear()

        for item in self.tree.get_children(""):
            self.tree.delete(item)

        model = navigation_model(self.book)

        for root in model["roots"]:
            root_id = str(root["id"])
            label = f"{root['label']}   {int(root['count'])} p."
            root_pages = list(root.get("pages", ()) or ())

            root_item = self._insert_folder(
                "",
                item_id=root_id,
                label=label,
                pages=(root_pages if root_pages else None),
                open_state=False,
            )

            # Les pages directement rattachées à Début / Corps / Fin sont
            # déjà construites : un seul clic sur la racine suffit à les voir.
            # Elles sont créées avant les sous-niveaux pour respecter l'ordre.
            if root_pages:
                self._load_pages(root_id)

            for child in root.get("children", ()) or ():
                self._insert_node(root_item, child, opened)

            if root_id in opened:
                self.tree.item(root_item, open=True)

        self.update_selection()
        self._built_once = True

        if focus_page_id is not None:
            self.scroll_to_page(str(focus_page_id), expand=False)

    def _register_single_page_row(
        self,
        folder_id: str,
        *,
        number: int,
        page_id: str,
        page: Any,
    ) -> None:
        item_id = f"page:{page_id}"
        caption = self._page_caption(
            int(number),
            page,
        )

        is_auto_blank = self._is_automatic_blank_page(
            page
        )
        if is_auto_blank:
            self.auto_page_ids.add(
                str(page_id)
            )

        side = self._page_side(
            str(page_id),
            int(number),
        )

        tags = (
            ("auto_page",)
            if is_auto_blank
            else ("page",)
        )

        self.tree.insert(
            folder_id,
            "end",
            iid=item_id,
            text=(
                caption
                if side == VERSO
                else ""
            ),
            values=(
                (
                    caption
                    if side == RECTO
                    else ""
                ),
            ),
            tags=tags,
        )

        self.page_items[str(page_id)] = item_id
        self.item_pages[item_id] = (str(page_id),)
        self.item_page_columns[item_id] = {
            (
                "#0"
                if side == VERSO
                else "#1"
            ): str(page_id)
        }

    def _register_spread_row(
        self,
        folder_id: str,
        *,
        spread_id: str,
        left_data: tuple[int, str, Any],
        right_data: tuple[int, str, Any],
    ) -> None:
        left_number, left_id, left_page = left_data
        right_number, right_id, right_page = right_data

        left_id = str(left_id)
        right_id = str(right_id)
        item_id = f"spread:{spread_id}"

        left_auto = self._is_automatic_blank_page(
            left_page
        )
        right_auto = self._is_automatic_blank_page(
            right_page
        )

        if left_auto:
            self.auto_page_ids.add(left_id)
        if right_auto:
            self.auto_page_ids.add(right_id)

        tags = (
            ("double_auto_page",)
            if left_auto or right_auto
            else ("double_page",)
        )

        # Une vraie 2P tient sur UNE seule ligne : gauche dans la moitie
        # gauche, droite dans la moitie droite. Aucun sigle 2P n'est ajoute.
        self.tree.insert(
            folder_id,
            "end",
            iid=item_id,
            text=self._page_caption(
                int(left_number),
                left_page,
            ),
            values=(
                self._page_caption(
                    int(right_number),
                    right_page,
                ),
            ),
            tags=tags,
        )

        self.page_items[left_id] = item_id
        self.page_items[right_id] = item_id
        self.item_pages[item_id] = (
            left_id,
            right_id,
        )
        self.item_page_columns[item_id] = {
            "#0": left_id,
            "#1": right_id,
        }

    def _load_pages(
        self,
        folder_id: str,
    ) -> None:
        folder_id = str(folder_id)

        if folder_id in self.loaded_folders:
            return

        pages = self.folder_pages.get(
            folder_id,
            [],
        )

        dummy = f"dummy:{folder_id}"

        if self.tree.exists(dummy):
            self.tree.delete(dummy)

        index = 0

        while index < len(pages):
            number, page_id, page = pages[index]
            page_id = str(page_id)
            spread = self._spread_for_page(
                page_id
            )

            # Le moteur 2P est l'autorite. On regroupe uniquement la paire
            # reelle gauche/droite si ses deux pages consecutives sont dans
            # ce meme niveau terminal.
            if (
                spread is not None
                and page_id == str(spread.left_page_id)
                and index + 1 < len(pages)
            ):
                next_data = pages[index + 1]
                next_id = str(next_data[1])

                if next_id == str(spread.right_page_id):
                    self._register_spread_row(
                        folder_id,
                        spread_id=str(spread.spread_id),
                        left_data=(
                            int(number),
                            page_id,
                            page,
                        ),
                        right_data=(
                            int(next_data[0]),
                            next_id,
                            next_data[2],
                        ),
                    )
                    index += 2
                    continue

            self._register_single_page_row(
                folder_id,
                number=int(number),
                page_id=page_id,
                page=page,
            )
            index += 1

        self.loaded_folders.add(
            folder_id
        )

        self.update_selection()

    def _on_open(
        self,
        _event=None,
    ) -> None:
        item = str(
            self.tree.focus()
            or ""
        )

        if item in self.folder_pages:
            self._load_pages(
                item
            )

        self.after_idle(
            self._save_open_nodes
        )

    def _on_close(
        self,
        _event=None,
    ) -> None:
        item = str(
            self.tree.focus()
            or ""
        )

        if item:
            # Replier une branche signifie repartir proprement a sa
            # prochaine ouverture : aucun sous-dossier ne conserve son
            # ancien etat ouvert.
            self._close_descendants(
                item
            )

        self.after_idle(
            self._save_open_nodes
        )

    def _page_at_pointer(
        self,
        event,
    ) -> tuple[str, str] | None:
        """Retourne (item, page_id) pour la moitié de page pointée."""

        item = str(
            self.tree.identify_row(event.y)
            or ""
        )
        if not item:
            return None

        pages = self.item_pages.get(item)
        if not pages:
            return None

        column = str(
            self.tree.identify_column(event.x)
            or ""
        )
        page_id = self.item_page_columns.get(
            item,
            {},
        ).get(column)

        if page_id is None and len(pages) == 1:
            page_id = pages[0]

        if page_id is None:
            return None

        return item, str(page_id)

    def _hide_drop_line(self) -> None:
        try:
            self._drop_line.place_forget()
        except Exception:
            pass
        self._drag_target = None

    def _show_drop_line(
        self,
        y: int,
    ) -> None:
        try:
            width = max(20, self.tree.winfo_width() - 8)
            self._drop_line.place(
                x=self.tree.winfo_x() + 4,
                y=self.tree.winfo_y() + int(y) - 1,
                width=width,
                height=2,
            )
            self._drop_line.lift()
        except Exception:
            self._hide_drop_line()

    def _drop_target_at_pointer(
        self,
        event,
    ) -> tuple[str, str, int] | None:
        """Calcule une frontière avant/après sans inventer de Structure.

        Une ligne de page donne une cible précise. Un niveau terminal replié
        accepte aussi un dépôt : moitié haute = début du niveau, moitié basse
        = fin du niveau. Les branches générales restent volontairement
        ambiguës et ne sont donc pas des cibles de dépôt.
        """

        item = str(
            self.tree.identify_row(event.y)
            or ""
        )
        if not item:
            return None

        try:
            bbox = self.tree.bbox(item)
        except tk.TclError:
            bbox = ()

        if not bbox:
            return None

        _x, row_y, _width, row_height = bbox
        before = event.y < (row_y + row_height / 2)

        pages = self.item_pages.get(item)
        if pages:
            column = str(
                self.tree.identify_column(event.x)
                or ""
            )
            anchor_page_id = self.item_page_columns.get(
                item,
                {},
            ).get(column)

            if anchor_page_id is None and len(pages) == 1:
                anchor_page_id = pages[0]

            if anchor_page_id is None:
                # Sur une 2P, si le pointeur tombe exactement dans la gouttière
                # entre colonnes, la moitié géométrique choisit la page cible.
                anchor_page_id = (
                    pages[0]
                    if event.x < self.tree.winfo_width() / 2
                    else pages[-1]
                )

            return (
                str(anchor_page_id),
                "before" if before else "after",
                int(row_y if before else row_y + row_height),
            )

        terminal_pages = self.folder_pages.get(item)
        if terminal_pages:
            # 2.38B — un chapitre ouvert expose ses vraies lignes de pages.
            # Son en-tête ne doit donc jamais devenir implicitement « fin du
            # chapitre » simplement parce que le pointeur arrive par le haut.
            #
            # - chapitre ouvert : l'en-tête signifie début du chapitre ;
            # - chapitre replié : moitié haute = début, moitié basse = fin.
            is_open_chapter = False
            if item in getattr(self, "chapter_folder_ids", set()):
                try:
                    is_open_chapter = bool(self.tree.item(item, "open"))
                except tk.TclError:
                    is_open_chapter = False

            if is_open_chapter:
                anchor_page_id = str(terminal_pages[0][1])
                position = "before"
                line_y = int(row_y + row_height)
            elif before:
                anchor_page_id = str(terminal_pages[0][1])
                position = "before"
                line_y = int(row_y)
            else:
                anchor_page_id = str(terminal_pages[-1][1])
                position = "after"
                line_y = int(row_y + row_height)

            return anchor_page_id, position, line_y

        return None

    def _on_button_press(
        self,
        event,
    ):
        pointed = self._page_at_pointer(event)
        if pointed is None:
            # Laisser ttk gérer normalement les flèches d'ouverture des
            # dossiers et les clics sur les niveaux de Structure.
            self._drag_candidate_page_id = None
            self._drag_start_xy = None
            self._dragging = False
            self._hide_drop_line()
            return None

        _item, page_id = pointed

        # Le clic garde exactement son comportement de sélection actuel.
        self.app._composition_plan_page_click(
            event,
            page_id,
        )

        # Ctrl reste réservé à la sélection multiple : aucun déplacement ne
        # démarre tant que Ctrl est maintenu.
        ctrl = bool(
            getattr(event, "state", 0) & 0x0004
        )
        manual_constraint_selection = bool(
            getattr(
                self.app,
                "_composition_constraint_manual_selection",
                False,
            )
        )

        page = getattr(self.book, "pages", {}).get(page_id)
        try:
            fixed_cover = cover_face(page) is not None
        except Exception:
            fixed_cover = False

        self._drag_candidate_page_id = (
            None
            if ctrl or manual_constraint_selection or fixed_cover
            else page_id
        )
        self._drag_start_xy = (int(event.x), int(event.y))
        self._dragging = False
        self._hide_drop_line()

        return "break"

    def _on_drag_motion(
        self,
        event,
    ):
        page_id = self._drag_candidate_page_id
        start = self._drag_start_xy
        if page_id is None or start is None:
            return None

        if not self._dragging:
            distance = abs(int(event.x) - start[0]) + abs(int(event.y) - start[1])
            if distance < 7:
                return "break"
            self._dragging = True
            try:
                self.tree.configure(cursor="fleur")
            except Exception:
                pass

        # Défilement doux en bord de liste pour déplacer une page loin dans
        # un livre sans devoir interrompre le clic-glisser.
        try:
            height = max(1, self.tree.winfo_height())
            if event.y < 24:
                self.tree.yview_scroll(-1, "units")
            elif event.y > height - 24:
                self.tree.yview_scroll(1, "units")
        except Exception:
            pass

        candidate = self._drop_target_at_pointer(event)
        if candidate is None:
            self._hide_drop_line()
            return "break"

        anchor_page_id, position, line_y = candidate
        self._drag_target = (
            str(anchor_page_id),
            str(position),
        )
        self._show_drop_line(line_y)

        return "break"

    def _on_button_release(
        self,
        _event,
    ):
        page_id = self._drag_candidate_page_id
        dragging = bool(self._dragging)
        target = self._drag_target

        self._drag_candidate_page_id = None
        self._drag_start_xy = None
        self._dragging = False
        self._hide_drop_line()

        try:
            self.tree.configure(cursor="")
        except Exception:
            pass

        if not dragging or page_id is None:
            return "break"

        if target is None:
            return "break"

        anchor_page_id, position = target
        self.app._composition_move_page_from_explorer(
            str(page_id),
            str(anchor_page_id),
            str(position),
        )

        return "break"

    def _on_mousewheel(
        self,
        event,
    ):
        try:
            self.tree.yview_scroll(
                int(
                    -event.delta / 120
                ),
                "units",
            )
            return "break"
        except Exception:
            return None

    def update_selection(self) -> None:
        selected = {
            str(page_id)
            for page_id in (
                getattr(
                    self.app,
                    "_composition_selected_page_ids",
                    set(),
                )
                or set()
            )
        }

        active = str(
            getattr(
                self.app.session,
                "active_page_id",
                "",
            )
            or ""
        )

        for item_id, page_ids in list(self.item_pages.items()):
            if not self.tree.exists(item_id):
                continue

            if active and active in page_ids:
                tags = ("active",)
            elif any(page_id in selected for page_id in page_ids):
                tags = ("selected_page",)
            elif len(page_ids) == 2:
                has_auto = any(page_id in self.auto_page_ids for page_id in page_ids)
                tags = (("double_auto_page",) if has_auto else ("double_page",))
            else:
                page_id = page_ids[0]
                tags = (("auto_page",) if page_id in self.auto_page_ids else ("page",))

            self.tree.item(item_id, tags=tags)

        # Repère permanent du chapitre courant, même quand ses pages sont
        # repliées. La page active conserve parallèlement son rouge habituel.
        for folder_id in list(self.chapter_folder_ids):
            if not self.tree.exists(folder_id):
                continue
            folder_pages = self.folder_pages.get(folder_id, ())
            in_active_chapter = bool(
                active
                and any(str(page_id) == active for _n, page_id, _p in folder_pages)
            )
            self.tree.item(
                folder_id,
                tags=(("active_chapter",) if in_active_chapter else ("folder",)),
            )

    def _folder_for_page(
        self,
        page_id: str,
    ) -> str | None:
        """Retourne le niveau terminal qui contient physiquement la page."""

        page_id = str(page_id)

        for folder_id, pages in self.folder_pages.items():
            for _number, candidate_id, _page in pages:
                if str(candidate_id) == page_id:
                    return str(folder_id)

        return None

    def _open_path_to_item(
        self,
        item_id: str,
    ) -> None:
        """Ouvre uniquement la chaine de parents necessaire a ``item_id``."""

        chain: list[str] = []
        current = str(item_id or "")

        while current:
            chain.append(current)
            try:
                current = str(
                    self.tree.parent(current)
                    or ""
                )
            except tk.TclError:
                break

        # On ouvre de la racine vers le niveau terminal. Les autres branches
        # conservent exactement leur etat : la navigation ne replie rien.
        for node_id in reversed(chain):
            try:
                self.tree.item(
                    node_id,
                    open=True,
                )
            except tk.TclError:
                continue

    def scroll_to_page(
        self,
        page_id: str,
        *,
        expand: bool = False,
    ) -> None:
        """Cadre la page et, si demande, revele son chemin dans l'arbre."""

        page_id = str(page_id)
        item = self.page_items.get(page_id)

        if expand:
            folder_id = self._folder_for_page(page_id)

            if folder_id is not None:
                # Les pages d'un niveau terminal sont chargees a la demande.
                # Il faut donc ouvrir le chemin puis creer les lignes de pages
                # avant de pouvoir surligner et cadrer la page active.
                self._open_path_to_item(folder_id)
                self._load_pages(folder_id)

                try:
                    self.tree.item(
                        folder_id,
                        open=True,
                    )
                except tk.TclError:
                    pass

                item = self.page_items.get(page_id)

            if item is not None:
                # Cas d'une page deja chargee mais masquee par un parent
                # replie : on revele toute sa chaine sans toucher aux autres.
                try:
                    parent = str(
                        self.tree.parent(item)
                        or ""
                    )
                except tk.TclError:
                    parent = ""

                if parent:
                    self._open_path_to_item(parent)

            # Le surlignage depend de la page active de la session. Les pages
            # venant d'etre creees doivent donc recevoir leurs tags maintenant.
            self.update_selection()
            self._save_open_nodes()

        if item is None:
            return

        try:
            self.tree.see(item)
        except tk.TclError:
            return

        # ``see`` peut faire evoluer la zone visible ; le tag actif est deja
        # applique par update_selection et reste donc immediatement perceptible.
