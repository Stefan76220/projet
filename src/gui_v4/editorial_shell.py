from __future__ import annotations

"""
TomeLinea V4 — habillage éditorial.

IMPORTANT :
ce module ne contient aucune logique métier.

Il habille TomeLineaV4 sans :
- créer de Livre ;
- choisir un type de livre ;
- modifier Source / Analyse / Structure ;
- importer gui_v3 ;
- toucher au Visionneur.

La logique reste dans src.gui_v4.app.TomeLineaV4.
"""

from pathlib import Path
import hashlib
import queue
import threading
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from PIL import (
    Image,
    ImageDraw,
    ImageEnhance,
    ImageTk,
)

from src.gui_v4 import theme

# Le moteur Phase 2.35 doit toujours utiliser le runtime tkwry/WebView2
# embarque par TomeLinea. Sans ceci, un ancien tkwry installe dans Python
# peut etre importe en premier et rester en cache dans sys.modules.
_TL_RUNTIME_PYTHON = Path(__file__).resolve().parents[2] / "runtime" / "python"
if _TL_RUNTIME_PYTHON.is_dir():
    _tl_runtime_value = str(_TL_RUNTIME_PYTHON)
    if _tl_runtime_value not in sys.path:
        sys.path.insert(0, _tl_runtime_value)

from src.gui_v4.canvas_editor_host import CanvasEditorWebHost
from src.v4.canvas_loading import CanvasLoadSession, prepare_canvas_load
from src.v4.canvas_editor_payload import build_canvas_editor_payload
from src.v4.canvas_editor_document import build_canvas_editor_document
from src.v4.canvas_chapter_runtime import (
    ChapterBookLayout,
    apply_exported_state,
    detect_chapters,
    slice_payload,
)
from src.v4.chapter_working_copy import (
    load_chapter_working_copy,
    record_chapter_export,
    restore_chapter_export,
)
from src.v4.composition_structure import (
    synchronize_composition_structure,
)
from src.v4.editorial_structure_classifier import (
    apply_structure_choice,
    classify_editorial_structure,
)
from src.v4.source_phase2 import Phase2BlockedError
from src.v4.editorial_persistence import (
    load_editorial_state,
    persisted_choices_for_plan,
    record_editorial_choice,
)
from src.gui_v4.app import (
    TomeLineaV4 as TomeLineaV4Logic,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STRUCTURE_CATALOG_PATH = PROJECT_ROOT / "resources" / "editorial" / "structure_catalog.json"

BACKGROUND_HOME = (
    PROJECT_ROOT
    / "assets"
    / "interface"
    / "backgrounds"
    / "editorial_bg_accueil.png"
)

BACKGROUND_SOFT = (
    PROJECT_ROOT
    / "assets"
    / "interface"
    / "backgrounds"
    / "editorial_bg_soft.png"
)

VISIBILITY_ROOT = (
    PROJECT_ROOT
    / "assets"
    / "branding"
    / "tomelinea"
    / "logo_pack_visibilite"
)

BRAND_ICON = (
    VISIBILITY_ROOT
    / "TomeLinea_512x512.png"
)

BRAND_TITLE = (
    VISIBILITY_ROOT
    / "TomeLinea_titre_relief.png"
)




# ==============================================================
# PANNEAU TOMELINEA
# ==============================================================

class CutPanel(tk.Canvas):

    def __init__(
        self,
        parent,
        *,
        fill: str = theme.PANEL,
        border: str = theme.BORDER_SOFT,
        cut: int = 15,
        padding: tuple[int, int] = (
            20,
            18,
        ),
        **kwargs,
    ):

        try:
            parent_bg = parent.cget(
                "bg"
            )
        except Exception:
            parent_bg = theme.WINDOW_DEEP

        super().__init__(
            parent,
            bg=parent_bg,
            bd=0,
            highlightthickness=0,
            **kwargs,
        )

        self._fill = fill
        self._border = border
        self._cut = cut

        self._pad_x = padding[0]
        self._pad_y = padding[1]

        self.body = tk.Frame(
            self,
            bg=fill,
        )

        self._body_id = (
            self.create_window(
                self._pad_x,
                self._pad_y,
                anchor="nw",
                window=self.body,
            )
        )

        self.bind(
            "<Configure>",
            self._redraw,
            add="+",
        )


    def _redraw(
        self,
        _event=None,
    ) -> None:

        width = max(
            30,
            self.winfo_width(),
        )

        height = max(
            30,
            self.winfo_height(),
        )

        cut = min(
            self._cut,
            max(
                5,
                width // 10,
            ),
            max(
                5,
                height // 10,
            ),
        )

        points = [
            1, 1,
            width - cut, 1,
            width - 1, cut,
            width - 1, height - cut,
            width - cut, height - 1,
            cut, height - 1,
            1, height - cut,
            1, cut,
        ]

        self.delete(
            "panel_shape"
        )

        self.create_polygon(
            points,
            fill=self._fill,
            outline=self._border,
            width=1,
            tags=(
                "panel_shape",
            ),
        )

        self.tag_lower(
            "panel_shape"
        )

        inner_width = max(
            1,
            width
            - self._pad_x * 2,
        )

        inner_height = max(
            1,
            height
            - self._pad_y * 2,
        )

        self.coords(
            self._body_id,
            self._pad_x,
            self._pad_y,
        )

        self.itemconfigure(
            self._body_id,
            width=inner_width,
            height=inner_height,
        )


# ==============================================================
# BOUTON TOMELINEA
# ==============================================================

class TLButton(tk.Button):

    def __init__(
        self,
        parent,
        text: str,
        command=None,
        *,
        primary: bool = False,
        compact: bool = False,
        state: str = "normal",
        width: int | None = None,
    ):

        if primary:
            base_bg = theme.ACCENT_DARK
            hover_bg = theme.ACCENT
            fg = theme.WHITE
            active_fg = theme.WINDOW_DEEP

        else:
            base_bg = theme.PANEL_SOFT
            hover_bg = theme.ACCENT_SOFT
            fg = theme.INK
            active_fg = theme.WHITE

        kwargs = {}

        if width is not None:
            kwargs[
                "width"
            ] = width

        super().__init__(
            parent,
            text=text,
            command=command,
            state=state,
            bg=base_bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground=active_fg,
            disabledforeground=theme.MUTED_DARK,
            relief="flat",
            bd=0,
            padx=(
                11
                if compact
                else 16
            ),
            pady=(
                6
                if compact
                else 9
            ),
            font=(
                theme.FONT_UI,
                9,
                "bold",
            ),
            cursor=(
                "hand2"
                if state != "disabled"
                else "arrow"
            ),
            **kwargs,
        )

        self._base_bg = base_bg
        self._hover_bg = hover_bg

        self.bind(
            "<Enter>",
            self._enter,
            add="+",
        )

        self.bind(
            "<Leave>",
            self._leave,
            add="+",
        )


    def _enter(
        self,
        _event=None,
    ) -> None:

        if str(
            self.cget(
                "state"
            )
        ) != "disabled":
            self.configure(
                bg=self._hover_bg
            )


    def _leave(
        self,
        _event=None,
    ) -> None:

        self.configure(
            bg=self._base_bg
        )


# ==============================================================
# COUCHE GRAPHIQUE V4
# ==============================================================

class TomeLineaV4Editorial(
    TomeLineaV4Logic
):

    def __init__(
        self,
        *,
        defer_show: bool = False,
    ) -> None:

        # Caches graphiques indépendants.
        self._editorial_bg_sources = {}
        self._editorial_bg_cache = {}

        self._brand_icon_cache = {}
        self._brand_title_cache = {}

        self._line_icon_cache = {}

        # Phase 2.37A : Canvas par chapitre / unité de composition.
        # L'analyse porte toujours sur le Livre complet, mais un seul petit
        # Canvas reste vivant pendant l'édition. La pagination globale est
        # reconstruite à partir des paginations locales mesurées au démarrage.
        self._phase2_canvas_host = None
        self._phase2_canvas_key = None
        self._phase2_canvas_state = "idle"
        self._phase2_canvas_generation = 0
        self._phase2_canvas_queue = queue.Queue()
        self._phase2_canvas_poll_after = None
        self._phase2_canvas_overlay = None
        self._phase2_canvas_overlay_title = None
        self._phase2_canvas_overlay_detail = None
        self._phase2_canvas_syncing_page = False
        self._phase2_canvas_last_failure = None
        self._phase2_chapter_prepared = None
        self._phase2_chapter_detection = None
        self._phase2_chapter_layout = None
        self._phase2_chapter_plans = []
        self._phase2_active_chapter_index = None
        self._phase2_loading_chapter_index = None
        self._phase2_preflight_index = 0
        self._phase2_pending_global_index = 0
        self._phase2_switch_in_progress = False
        self._phase2_destroy_requested = False

        # Toute la fenêtre est construite hors écran. Le Tk racine n'est
        # affiché qu'une fois l'habillage, la géométrie et l'Accueil prêts :
        # aucun flash intermédiaire ni reconstruction visible au démarrage.
        super().__init__(start_hidden=True)

        try:
            self.overrideredirect(
                True
            )
        except tk.TclError:
            pass

        self._fit_to_work_area()
        self.update_idletasks()

        if not defer_show:
            self.show_prepared_window()

    def show_prepared_window(self) -> None:
        """Affiche la fenêtre V4 uniquement lorsqu'elle est entièrement prête."""
        try:
            self.deiconify()
            self.lift()
            self.update_idletasks()
        except tk.TclError:
            pass

    def destroy(self) -> None:
        """Ferme TomeLinea après sauvegarde du chapitre Canvas actif.

        Canvas reste l'unique moteur de pagination. La Source DOCX n'est jamais
        réécrite : l'export est enregistré comme copie de travail TomeLinea.
        """
        if bool(getattr(self, "_phase2_destroy_requested", False)):
            return

        host = getattr(self, "_phase2_canvas_host", None)
        chapter_index = getattr(self, "_phase2_active_chapter_index", None)

        if (
            host is None
            or not getattr(host, "ready", False)
            or chapter_index is None
        ):
            return super().destroy()

        self._phase2_destroy_requested = True
        finished = {"done": False}

        def finish(exported=None):
            if finished["done"]:
                return
            finished["done"] = True

            if isinstance(exported, dict) and exported.get("ok") is True:
                try:
                    self._phase2_apply_exported_chapter(
                        int(chapter_index),
                        exported,
                    )
                except Exception:
                    pass

            try:
                self._phase2_destroy_current_host()
            except Exception:
                pass

            try:
                super(TomeLineaV4Editorial, self).destroy()
            except Exception:
                try:
                    tk.Tk.destroy(self)
                except Exception:
                    pass

        try:
            host.export_document_state(finish)
            # La fermeture ne doit jamais rester bloquée si WebView2 ne répond pas.
            self.after(2000, finish)
        except Exception:
            finish()


    # ==========================================================
    # CANVAS PAR CHAPITRE / COPIE DE TRAVAIL
    # ==========================================================






    def _phase2_save_active_before_clear(self) -> None:
        """Sauvegarde le chapitre Canvas actif avant de quitter l'écran.

        ``show_home`` et les changements d'espace appellent ``_clear`` de façon
        synchrone. La 2.37B sauvegardait déjà à la fermeture de l'application,
        mais ``_clear`` détruisait encore le WebView avant son export. On attend
        donc uniquement l'export léger du chapitre actif, puis on poursuit la
        navigation. La Source DOCX reste intacte.
        """
        host = getattr(self, "_phase2_canvas_host", None)
        chapter_index = getattr(self, "_phase2_active_chapter_index", None)
        if (
            host is None
            or not getattr(host, "ready", False)
            or chapter_index is None
        ):
            return

        try:
            chapter_index = int(chapter_index)
        except (TypeError, ValueError):
            return

        finished = {"done": False}
        waiter = tk.BooleanVar(master=self, value=False)
        timeout_id = None

        def finish(exported=None):
            if finished["done"]:
                return
            finished["done"] = True

            if isinstance(exported, dict) and exported.get("ok") is True:
                try:
                    self._phase2_apply_exported_chapter(
                        chapter_index,
                        exported,
                    )
                except Exception:
                    pass

            try:
                waiter.set(True)
            except Exception:
                pass

        try:
            host.export_document_state(finish)
            timeout_id = self.after(2000, finish)
            try:
                self.wait_variable(waiter)
            except tk.TclError:
                pass
        except Exception:
            finish()
        finally:
            if timeout_id is not None:
                try:
                    self.after_cancel(timeout_id)
                except Exception:
                    pass

    def _clear(self) -> None:
        # Non-régression 2.37D : conserver la copie de travail du chapitre
        # Canvas actif avant toute reconstruction d'écran.
        self._phase2_save_active_before_clear()
        self._phase2_destroy_host()
        self._phase2_cancel_poll()
        super()._clear()












    def _composition_pan_motion(self, event):
        return super()._composition_pan_motion(event)















    # ==========================================================
    # CANVAS PAR CHAPITRE + STRUCTURE ÉDITORIALE PHYSIQUE RÉELLE
    # ==========================================================

    def _composition_document_metadata(self, *, create: bool = False) -> dict | None:
        """Métadonnées de la copie de travail TomeLinea, jamais de la Source."""
        session = getattr(self, "session", None)
        project = getattr(session, "project", None) if session is not None else None
        if project is None:
            return None
        value = project.metadata.get("composition_document")
        if isinstance(value, dict):
            return value
        if not create:
            return None
        value = {
            "engine": "canvas-editor-by-chapter",
            "import_contract": "content_first",
            "working_font_family": "Arial",
        }
        project.metadata["composition_document"] = value
        return value

    def _composition_sync_pages_simple(self, count: int) -> None:
        """Repli minimal sans ancien paginateur de traitement de texte."""
        from src.v4.domain import PageOrigin, PageV4

        session = getattr(self, "session", None)
        book = getattr(session, "book", None) if session is not None else None
        if book is None:
            return
        count = max(1, int(count))
        ids = self._phase2_composition_page_ids()

        while len(ids) > count:
            page_id = ids.pop()
            if page_id in book.page_order:
                book.page_order.remove(page_id)
            book.pages.pop(page_id, None)

        while len(ids) < count:
            page = PageV4(
                page_type="Page texte",
                title=f"Page {len(ids) + 1}",
                origin=PageOrigin.AUTHOR,
            )
            page.metadata["composition_page"] = True
            page.metadata["composition_page_index"] = len(ids)
            book.add_page(page)
            ids.append(page.id)

        for index, page_id in enumerate(ids):
            page = book.pages.get(page_id)
            if page is None:
                continue
            page.metadata["composition_page"] = True
            page.metadata["composition_page_index"] = index
            page.metadata["composition_page_start"] = index
            if page.page_type == "Page texte":
                page.title = f"Page {index + 1}"
        try:
            session.refresh_context()
        except Exception:
            pass

    def _phase2_source_path(self) -> Path | None:
        """Retrouve le DOCX original depuis le magasin Source du projet."""
        session = getattr(self, "session", None)
        project = getattr(session, "project", None) if session is not None else None
        if project is None:
            return None

        element_id = str(project.metadata.get("primary_source_element_id") or "")
        source_store = getattr(project, "source", None)
        elements = getattr(source_store, "elements", {}) if source_store is not None else {}
        element = elements.get(element_id) if element_id else None
        version = getattr(element, "active_version", None) if element is not None else None
        raw = str(getattr(version, "original_path", "") or "").strip()
        if not raw:
            return None
        candidate = Path(raw).expanduser()
        if candidate.suffix.lower() != ".docx" or not candidate.is_file():
            return None
        return candidate.resolve()


    def _phase2_composition_page_ids(self) -> list[str]:
        """Pages texte du Canvas, dans leur ordre éditorial interne.

        Les quatre faces de couverture existent maintenant dans BookV4, mais
        elles ne font pas partie de la pagination locale du moteur Canvas.
        Toute correspondance Canvas -> Livre doit donc passer par cette liste.
        """
        session = getattr(self, "session", None)
        book = getattr(session, "book", None) if session is not None else None
        if book is None:
            return []

        result: list[tuple[int, str]] = []
        fallback = 0
        for page_id in list(getattr(book, "page_order", ())):
            page = book.pages.get(page_id)
            metadata = getattr(page, "metadata", None) if page is not None else None
            if not isinstance(metadata, dict) or not metadata.get("composition_page"):
                continue
            try:
                index = int(metadata.get("composition_page_index", fallback))
            except (TypeError, ValueError):
                index = fallback
            result.append((index, str(page_id)))
            fallback += 1

        result.sort(key=lambda item: item[0])
        return [page_id for _index, page_id in result]

    def _phase2_active_page_index(self) -> int | None:
        session = getattr(self, "session", None)
        page = getattr(session, "active_page", None) if session is not None else None
        if page is None:
            return None
        metadata = getattr(page, "metadata", None)
        if not isinstance(metadata, dict) or not metadata.get("composition_page"):
            return None
        try:
            return max(0, int(metadata.get("composition_page_index", 0)))
        except (TypeError, ValueError):
            return None


    def _phase2_can_render(self) -> bool:
        return (
            str(getattr(self, "current_workspace", "")) == "composition"
            and getattr(self, "session", None) is not None
            and getattr(self.session, "book", None) is not None
            and self._phase2_source_path() is not None
            and self._phase2_active_page_index() is not None
        )

    def _phase2_state_file(self, source: Path) -> Path:
        marker = hashlib.sha256(str(source.resolve()).casefold().encode("utf-8")).hexdigest()[:20]
        return PROJECT_ROOT / ".tomelinea_runtime" / "editorial_state" / f"{marker}.json"

    def _phase2_working_copy_file(self, source: Path) -> Path:
        marker = hashlib.sha256(
            str(source.resolve()).casefold().encode("utf-8")
        ).hexdigest()[:20]
        return (
            PROJECT_ROOT
            / ".tomelinea_runtime"
            / "chapter_working_copy"
            / f"{marker}.json"
        )

    def _phase2_cancel_poll(self) -> None:
        after_id = getattr(self, "_phase2_canvas_poll_after", None)
        if after_id is not None:
            try:
                self.after_cancel(after_id)
            except Exception:
                pass
        self._phase2_canvas_poll_after = None

    def _phase2_destroy_overlay(self) -> None:
        overlay = getattr(self, "_phase2_canvas_overlay", None)
        if overlay is not None:
            try:
                overlay.destroy()
            except Exception:
                pass
        self._phase2_canvas_overlay = None
        self._phase2_canvas_overlay_title = None
        self._phase2_canvas_overlay_detail = None

    def _phase2_show_overlay(self, canvas, title: str, detail: str = "") -> None:
        overlay = getattr(self, "_phase2_canvas_overlay", None)
        try:
            valid = overlay is not None and overlay.winfo_exists() and overlay.master is canvas
        except Exception:
            valid = False
        if not valid:
            self._phase2_destroy_overlay()
            overlay = tk.Frame(canvas, bg=theme.WINDOW_DEEP, bd=0, highlightthickness=0)
            overlay.place(x=0, y=0, relwidth=1, relheight=1)
            self._phase2_canvas_overlay = overlay
            self._phase2_canvas_overlay_title = tk.Label(
                overlay,
                text="",
                bg=theme.WINDOW_DEEP,
                fg=theme.INK,
                font=(theme.FONT_TITLE, 17, "bold"),
            )
            self._phase2_canvas_overlay_title.place(relx=0.5, rely=0.44, anchor="center")
            self._phase2_canvas_overlay_detail = tk.Label(
                overlay,
                text="",
                bg=theme.WINDOW_DEEP,
                fg=theme.MUTED,
                font=(theme.FONT_UI, 10),
                justify="center",
                wraplength=560,
            )
            self._phase2_canvas_overlay_detail.place(relx=0.5, rely=0.51, anchor="center")
        try:
            self._phase2_canvas_overlay_title.configure(text=str(title))
            self._phase2_canvas_overlay_detail.configure(text=str(detail or ""))
            overlay.lift()
        except Exception:
            pass

    def _phase2_destroy_current_host(self) -> None:
        host = getattr(self, "_phase2_canvas_host", None)
        if host is not None:
            try:
                host.shutdown()
            except Exception:
                pass
            try:
                host.destroy()
            except Exception:
                pass
        self._phase2_canvas_host = None
        self._phase2_loading_chapter_index = None

    def _phase2_destroy_host(self) -> None:
        """Détruit le document de composition courant et son cache de chapitres."""
        self._phase2_destroy_current_host()
        self._phase2_canvas_key = None
        self._phase2_canvas_state = "idle"
        self._phase2_canvas_last_failure = None
        self._phase2_chapter_prepared = None
        self._phase2_chapter_detection = None
        self._phase2_chapter_layout = None
        self._phase2_chapter_plans = []
        self._phase2_active_chapter_index = None
        self._phase2_preflight_index = 0
        self._phase2_pending_global_index = 0
        self._phase2_switch_in_progress = False
        self._phase2_editorial_structure_analysis = None
        self._phase239_review_queue = []
        self._phase239_review_current = None
        self._phase239_review_prompt_open = False
        self._phase239_review_return_global_index = 0
        self._phase2_destroy_overlay()

    def _phase2_persist_choice(self, source: Path, event: dict) -> None:
        try:
            record_editorial_choice(self._phase2_state_file(source), source, event)
        except Exception:
            return
        try:
            self.session.project.touch()
        except Exception:
            pass

    def _phase2_sync_page_count(self, count: int) -> None:
        try:
            count = max(1, int(count))
        except (TypeError, ValueError):
            return

        metadata = self._composition_document_metadata(create=True)
        layout = getattr(self, "_phase2_chapter_layout", None)
        detection = getattr(self, "_phase2_chapter_detection", None)

        if layout is not None and detection is not None:
            try:
                result = synchronize_composition_structure(
                    self.session.book,
                    detection,
                    list(layout.page_counts),
                    getattr(self, "_phase2_editorial_structure_analysis", None),
                )
                if metadata is not None:
                    metadata["page_count"] = count
                    metadata["canvas_page_count"] = count
                    metadata["canvas_chapter_page_counts"] = list(layout.page_counts)
                    metadata["canvas_chapter_mode"] = str(detection.mode)
                    metadata["canvas_chapter_count"] = len(detection.chapters)
                    metadata["physical_page_count"] = int(result.physical_page_count)
                    metadata.pop("canvas_structure_sync_error", None)
                self.session.refresh_context()
                if result.changed:
                    try:
                        self.session.project.touch()
                    except Exception:
                        pass
            except Exception as exc:
                if metadata is not None:
                    metadata["canvas_structure_sync_error"] = f"{type(exc).__name__}: {exc}"
                self._composition_sync_pages_simple(count)
        else:
            self._composition_sync_pages_simple(count)
            if metadata is not None:
                metadata["page_count"] = count
                metadata["canvas_page_count"] = count

        try:
            active_id = str(self.session.active_page_id or "")
            self._composition_render_plan(focus_page_id=(active_id or None), animate=False)
            self._composition_update_plan_selection()
            self._composition_refresh_center_navigation()
        except Exception:
            pass


    def _phase239_ambiguous_structure_units(self) -> list[dict]:
        analysis = getattr(self, "_phase2_editorial_structure_analysis", None)
        if not isinstance(analysis, dict):
            return []
        return [
            dict(unit)
            for unit in list(analysis.get("units") or [])
            if isinstance(unit, dict) and unit.get("ask_user")
        ]

    def _phase239_unit_page_range(self, unit: dict) -> tuple[int, int]:
        layout = getattr(self, "_phase2_chapter_layout", None)
        if layout is None:
            return 1, 1
        try:
            chapter_index = int(unit.get("canvas_index", 0))
        except (TypeError, ValueError):
            chapter_index = 0
        chapter_index = max(0, min(chapter_index, len(layout.page_counts) - 1))
        start = int(layout.chapter_start_page(chapter_index))
        count = max(1, int(layout.page_counts[chapter_index]))
        return start, start + count - 1

    def _phase239_unit_context(self, unit: dict) -> tuple[str, str]:
        analysis = getattr(self, "_phase2_editorial_structure_analysis", None)
        units = list(analysis.get("units") or []) if isinstance(analysis, dict) else []
        try:
            wanted = int(unit.get("canvas_index", -1))
        except (TypeError, ValueError):
            wanted = -1

        previous = ""
        following = ""
        for pos, current in enumerate(units):
            if not isinstance(current, dict):
                continue
            try:
                current_index = int(current.get("canvas_index", -999))
            except (TypeError, ValueError):
                continue
            if current_index != wanted:
                continue

            if pos > 0 and isinstance(units[pos - 1], dict):
                previous = str(
                    units[pos - 1].get("editorial_label")
                    or units[pos - 1].get("title")
                    or ""
                ).strip()
            if pos + 1 < len(units) and isinstance(units[pos + 1], dict):
                following = str(
                    units[pos + 1].get("editorial_label")
                    or units[pos + 1].get("title")
                    or ""
                ).strip()
            break

        return previous, following

    def _phase239_begin_structure_review(self, canvas) -> None:
        self._phase239_review_queue = self._phase239_ambiguous_structure_units()
        self._phase239_review_current = None
        self._phase239_review_prompt_open = False
        self._phase239_review_return_global_index = max(
            0,
            int(getattr(self, "_phase2_pending_global_index", 0) or 0),
        )
        self._phase2_destroy_overlay()
        self.after(20, lambda: self._phase239_review_next(canvas))

    def _phase239_review_next(self, canvas) -> None:
        queue_items = list(getattr(self, "_phase239_review_queue", []) or [])
        if not queue_items:
            self._phase239_review_current = None
            self._phase239_review_prompt_open = False
            layout = getattr(self, "_phase2_chapter_layout", None)
            if layout is not None:
                self._phase2_sync_page_count(layout.total_pages)
            target = max(
                0,
                int(getattr(self, "_phase239_review_return_global_index", 0) or 0),
            )
            self.after(
                20,
                lambda: self._phase2_request_global_page(
                    canvas,
                    target,
                    force=True,
                ),
            )
            return

        unit = dict(queue_items[0])
        self._phase239_review_current = unit

        layout = getattr(self, "_phase2_chapter_layout", None)
        if layout is None:
            return
        try:
            chapter_index = int(unit.get("canvas_index", 0))
        except (TypeError, ValueError):
            chapter_index = 0
        chapter_index = max(0, min(chapter_index, len(layout.page_counts) - 1))
        target = int(layout.global_index(chapter_index, 0))

        # La navigation synchronisée ouvrira aussi la bonne branche Structure.
        self._phase2_request_global_page(canvas, target, force=True)
        self.after(
            100,
            lambda: self._phase239_wait_for_review_page(canvas, 0),
        )

    def _phase239_wait_for_review_page(self, canvas, attempt: int) -> None:
        unit = getattr(self, "_phase239_review_current", None)
        if not isinstance(unit, dict):
            return
        layout = getattr(self, "_phase2_chapter_layout", None)
        host = getattr(self, "_phase2_canvas_host", None)
        if layout is None:
            return

        try:
            chapter_index = int(unit.get("canvas_index", 0))
        except (TypeError, ValueError):
            chapter_index = 0

        ready = bool(
            host is not None
            and getattr(host, "ready", False)
            and getattr(self, "_phase2_active_chapter_index", None) == chapter_index
            and not getattr(self, "_phase2_switch_in_progress", False)
        )

        if ready:
            try:
                host.go_to_page(1, smooth=False)
            except Exception:
                pass
            self.after(180, lambda: self._phase239_show_structure_question(canvas))
            return

        if int(attempt) < 80:
            self.after(
                75,
                lambda a=int(attempt) + 1: self._phase239_wait_for_review_page(
                    canvas,
                    a,
                ),
            )
            return

        self._phase239_show_structure_question(canvas)

    def _phase239_show_structure_question(self, canvas) -> None:
        if getattr(self, "_phase239_review_prompt_open", False):
            return

        unit = getattr(self, "_phase239_review_current", None)
        if not isinstance(unit, dict):
            return

        self._phase239_review_prompt_open = True
        title = str(unit.get("title") or "Section").strip() or "Section"
        zone = str(unit.get("zone") or "bodymatter")
        key = str(unit.get("key") or "")
        start_page, end_page = self._phase239_unit_page_range(unit)
        previous, following = self._phase239_unit_context(unit)

        if start_page == end_page:
            page_text = f"Page intérieure {start_page}"
        else:
            page_text = f"Pages intérieures {start_page} à {end_page}"

        context_lines = []
        if previous:
            context_lines.append(f"Après : « {previous} »")
        if following:
            context_lines.append(f"Avant : « {following} »")
        context = "\n".join(context_lines)

        create = messagebox.askyesno(
            "Structure du livre",
            (
                "TomeLinea a repéré une nouvelle section.\n\n"
                f"« {title} »\n"
                f"{page_text}\n"
                + (f"\n{context}\n" if context else "\n")
                + "\nLa première page concernée est affichée au centre.\n\n"
                "Oui = créer une section distincte\n"
                "Non = rattacher ce contenu à l’unité précédente"
            ),
            parent=self,
        )

        analysis = getattr(self, "_phase2_editorial_structure_analysis", None)
        project = getattr(getattr(self, "session", None), "project", None)
        stored = {}
        if project is not None:
            raw = project.metadata.get("editorial_structure_choices")
            if isinstance(raw, dict):
                stored = {
                    str(k): dict(v)
                    for k, v in raw.items()
                    if isinstance(v, dict)
                }

        if create:
            name = simpledialog.askstring(
                "Nom de la section",
                "Nom de cette section :",
                initialvalue=title,
                parent=self,
            )
            name = str(name or title).strip() or title
            if isinstance(analysis, dict):
                analysis = apply_structure_choice(
                    analysis,
                    key,
                    create_section=True,
                    name=name,
                )
            stored[key] = {
                "decision": "create",
                "name": name,
                "zone": zone,
            }
        else:
            if isinstance(analysis, dict):
                analysis = apply_structure_choice(
                    analysis,
                    key,
                    create_section=False,
                )
            stored[key] = {
                "decision": "merge",
                "zone": zone,
            }

        if isinstance(analysis, dict):
            self._phase2_editorial_structure_analysis = analysis

        if project is not None:
            project.metadata["editorial_structure_choices"] = stored
            if isinstance(analysis, dict):
                project.metadata["editorial_structure_last_summary"] = dict(
                    analysis.get("summary") or {}
                )
            try:
                project.touch()
            except Exception:
                pass

        queue_items = list(getattr(self, "_phase239_review_queue", []) or [])
        if queue_items:
            queue_items.pop(0)
        self._phase239_review_queue = queue_items
        self._phase239_review_current = None
        self._phase239_review_prompt_open = False

        layout = getattr(self, "_phase2_chapter_layout", None)
        if layout is not None:
            self._phase2_sync_page_count(layout.total_pages)
        self.after(80, lambda: self._phase239_review_next(canvas))


    def _phase2_worker(self, generation: int, source: Path) -> None:
        """Analyse une fois le Livre complet puis prépare les plans par chapitre."""
        try:
            project = getattr(getattr(self, "session", None), "project", None)
            substitutions = {}
            if project is not None:
                raw = project.metadata.get("font_substitutions")
                if isinstance(raw, dict):
                    substitutions = {str(k): dict(v) for k, v in raw.items() if isinstance(v, dict)}

            prepared = prepare_canvas_load(
                source,
                project_root=PROJECT_ROOT,
                font_substitutions=substitutions,
            )
            translated = build_canvas_editor_payload(prepared.canvas.contract)
            if not prepared.ready or not translated.valid:
                raise RuntimeError("Préparation Canvas invalide avant découpage du Livre.")

            detection = detect_chapters(translated.payload)
            if not detection.chapters:
                raise RuntimeError("Aucune unité de composition n'a pu être construite.")

            structure_choices = {}
            if project is not None:
                raw_structure_choices = project.metadata.get("editorial_structure_choices")
                if isinstance(raw_structure_choices, dict):
                    structure_choices = {
                        str(key): dict(value)
                        for key, value in raw_structure_choices.items()
                        if isinstance(value, dict)
                    }

            structure_analysis = classify_editorial_structure(
                translated.payload,
                detection,
                catalog_path=STRUCTURE_CATALOG_PATH,
                persisted_choices=structure_choices,
            )

            state = load_editorial_state(self._phase2_state_file(source), source)
            persisted = persisted_choices_for_plan(state)
            review = {
                "automatic_corrections": list(prepared.text_quality.automatic_corrections),
                "editorial_decisions": list(prepared.text_quality.editorial_decisions),
                "blocking_anomalies": list(prepared.text_quality.blocking_anomalies),
            }

            working_copy = load_chapter_working_copy(
                self._phase2_working_copy_file(source),
                source,
            )

            plans = []
            for chapter in detection.chapters:
                chapter_payload = slice_payload(translated.payload, chapter)
                document = build_canvas_editor_document(chapter_payload)
                if not document.valid:
                    raise RuntimeError(
                        f"Plan Canvas invalide pour {chapter.title!r} : "
                        + ", ".join(document.errors)
                    )
                document.plan["persisted_editorial_choices"] = persisted
                document.plan["visual_review"] = review
                document.plan["tomelinea_ui"] = {"mode": "embedded_composition"}
                document.plan["tomelinea_chapter"] = {
                    "index": chapter.index,
                    "title": chapter.title,
                    "detected_by": chapter.detected_by,
                }

                # Restaurer la copie de travail avant la pré-pagination : les
                # numéros de pages globaux sont alors recalculés sur l'état édité.
                restore_chapter_export(
                    document.plan,
                    working_copy,
                    chapter,
                )
                plans.append(document.plan)

            self._phase2_canvas_queue.put((
                generation,
                "ready",
                source,
                prepared,
                detection,
                plans,
                structure_analysis,
            ))
        except Phase2BlockedError as exc:
            blockers = [
                {
                    "kind": item.code,
                    "message": item.message,
                    "solution": item.solution,
                    "details": item.details,
                }
                for item in exc.blockers
            ]
            self._phase2_canvas_queue.put((generation, "blocked", source, blockers))
        except Exception as exc:
            self._phase2_canvas_queue.put((
                generation,
                "error",
                source,
                {"stage": "preparation", "message": f"{type(exc).__name__}: {exc}"},
            ))

    def _phase2_start_analysis(self, canvas) -> None:
        source = self._phase2_source_path()
        if source is None:
            return
        key = str(source.resolve())
        if self._phase2_canvas_state in {
            "preparing", "preflight", "chapter_loading", "ready"
        } and self._phase2_canvas_key == key:
            return

        self._phase2_destroy_host()
        self._phase2_canvas_key = key
        self._phase2_canvas_state = "preparing"
        self._phase2_canvas_generation += 1
        generation = self._phase2_canvas_generation
        self._phase2_show_overlay(
            canvas,
            "Préparation de Composition",
            "Analyse complète du Livre et préparation des unités éditoriales…",
        )
        threading.Thread(
            target=self._phase2_worker,
            args=(generation, source),
            daemon=True,
        ).start()
        self._phase2_schedule_poll(canvas)

    def _phase2_schedule_poll(self, canvas) -> None:
        self._phase2_cancel_poll()
        try:
            self._phase2_canvas_poll_after = self.after(60, lambda: self._phase2_poll(canvas))
        except Exception:
            self._phase2_canvas_poll_after = None

    def _phase2_poll(self, canvas) -> None:
        self._phase2_canvas_poll_after = None
        handled = False
        while True:
            try:
                item = self._phase2_canvas_queue.get_nowait()
            except queue.Empty:
                break
            generation, kind, source, *payload = item
            if generation != self._phase2_canvas_generation:
                continue
            handled = True
            if kind == "ready":
                prepared, detection, plans, structure_analysis = payload
                # 2.39B : les questions ambiguës sont volontairement différées.
                # TomeLinea termine d'abord la pagination afin de pouvoir montrer
                # la vraie page concernée au centre avant de demander un choix.
                self._phase2_editorial_structure_analysis = structure_analysis
                self._phase2_begin_preflight(canvas, source, prepared, detection, plans)
            elif kind == "blocked":
                self._phase2_canvas_state = "blocked"
                blockers = payload[0] if payload else []
                first = blockers[0] if blockers else {}
                self._phase2_show_overlay(
                    canvas,
                    "Composition suspendue",
                    str(first.get("message") or "TomeLinea a besoin d'une correction avant de poursuivre.")
                    + ("\n\n" + str(first.get("solution") or "") if first.get("solution") else ""),
                )
            else:
                self._phase2_canvas_state = "failed"
                failure = payload[0] if payload else {}
                self._phase2_canvas_last_failure = failure
                self._phase2_show_overlay(
                    canvas,
                    "Composition impossible",
                    str((failure or {}).get("message") or "Le moteur de composition n'a pas pu être préparé."),
                )
        if self._phase2_canvas_state == "preparing" and not handled:
            self._phase2_schedule_poll(canvas)

    def _phase2_begin_preflight(self, canvas, source: Path, prepared, detection, plans) -> None:
        """Compose successivement chaque chapitre pour connaître le Livre global."""
        self._phase2_chapter_prepared = prepared
        self._phase2_chapter_detection = detection
        self._phase2_chapter_plans = list(plans)
        self._phase2_chapter_layout = ChapterBookLayout(detection.chapters)
        self._phase2_active_chapter_index = None
        self._phase2_preflight_index = 0
        self._phase2_canvas_state = "preflight"
        self._phase2_pending_global_index = max(0, int(self._phase2_active_page_index() or 0))
        self._phase2_preflight_next(canvas)

    def _phase2_preflight_next(self, canvas) -> None:
        layout = getattr(self, "_phase2_chapter_layout", None)
        prepared = getattr(self, "_phase2_chapter_prepared", None)
        detection = getattr(self, "_phase2_chapter_detection", None)
        if layout is None or prepared is None or detection is None:
            self._phase2_on_failed(canvas, {"stage": "preflight", "message": "État chapitre incomplet."})
            return

        index = int(self._phase2_preflight_index)
        if index >= len(detection.chapters):
            self._phase2_destroy_current_host()
            self._phase2_sync_page_count(layout.total_pages)
            self._phase2_canvas_state = "prepared"

            # 2.39B : si une frontière reste ambiguë, ouvrir d'abord sa vraie
            # page au centre et seulement ensuite demander la décision.
            ambiguous = self._phase239_ambiguous_structure_units()
            if ambiguous:
                self._phase239_begin_structure_review(canvas)
                return

            self._phase2_show_overlay(
                canvas,
                "Composition prête",
                f"{len(detection.chapters)} unité(s) — {layout.total_pages} page(s). Ouverture de la page active…",
            )
            self.after(20, lambda: self._phase2_request_global_page(
                canvas,
                int(self._phase2_active_page_index() or 0),
                force=True,
            ))
            return

        chapter = detection.chapters[index]
        self._phase2_show_overlay(
            canvas,
            "Préparation de Composition",
            f"Pagination {index + 1}/{len(detection.chapters)} — {chapter.title}",
        )
        self._phase2_loading_chapter_index = index

        # La pré-pagination utilise un seul WebView2 pour toutes les unités.
        # Canvas Editor détruit déjà son document courant dans tomeLineaCanvasLoad.
        # Le host natif est détruit une seule fois après la dernière unité.
        host = getattr(self, "_phase2_canvas_host", None)
        if host is None:
            host = CanvasEditorWebHost(
                canvas,
                project_root=PROJECT_ROOT,
                background=theme.WINDOW_DEEP,
            )
            self._phase2_canvas_host = host
            host.place(x=0, y=0, relwidth=1, relheight=1)
            try:
                host.lower()
            except Exception:
                pass
        try:
            host.load_document(
                self._phase2_chapter_plans[index],
                CanvasLoadSession(prepared.canvas.contract),
                on_ready=lambda snapshot, idx=index: self._phase2_preflight_ready(canvas, idx, snapshot),
                on_failed=lambda failure, idx=index: self._phase2_preflight_failed(canvas, idx, failure),
            )
        except Exception as exc:
            self._phase2_preflight_failed(
                canvas,
                index,
                {"stage": "load_document", "message": f"{type(exc).__name__}: {exc}"},
            )
        try:
            self._phase2_canvas_overlay.lift()
        except Exception:
            pass

    def _phase2_preflight_ready(self, canvas, chapter_index: int, snapshot: dict) -> None:
        if self._phase2_canvas_state != "preflight" or chapter_index != self._phase2_preflight_index:
            return
        layout = self._phase2_chapter_layout
        if layout is None:
            return
        try:
            count = int((snapshot or {}).get("page_count") or 1)
        except (TypeError, ValueError):
            count = 1
        layout.set_page_count(chapter_index, count)
        self._phase2_preflight_index += 1
        # Réutilise le même host/WebView pour l'unité suivante.
        self.after(15, lambda: self._phase2_preflight_next(canvas))

    def _phase2_preflight_failed(self, canvas, chapter_index: int, failure: dict) -> None:
        detection = self._phase2_chapter_detection
        title = "chapitre"
        if detection is not None and 0 <= chapter_index < len(detection.chapters):
            title = detection.chapters[chapter_index].title
        self._phase2_on_failed(
            canvas,
            {
                "stage": "chapter_preflight",
                "message": f"Impossible de composer {title!r} : "
                + str((failure or {}).get("message") or "erreur Canvas"),
            },
        )

    def _phase2_apply_exported_chapter(self, chapter_index: int, exported: dict) -> None:
        if not (0 <= int(chapter_index) < len(self._phase2_chapter_plans)):
            return

        index = int(chapter_index)

        try:
            apply_exported_state(
                self._phase2_chapter_plans[index],
                exported,
            )
        except Exception:
            pass

        # Persistance TomeLinea séparée de la Source originale.
        try:
            source = self._phase2_source_path()
            detection = self._phase2_chapter_detection
            if (
                source is not None
                and detection is not None
                and 0 <= index < len(detection.chapters)
            ):
                record_chapter_export(
                    self._phase2_working_copy_file(source),
                    source,
                    detection.chapters[index],
                    exported,
                )
        except Exception:
            pass

        layout = self._phase2_chapter_layout
        if layout is not None:
            try:
                count = int((exported or {}).get("pageCount") or 0)
            except (TypeError, ValueError):
                count = 0
            if count > 0 and count != layout.page_counts[index]:
                layout.set_page_count(index, count)
                self._phase2_sync_page_count(layout.total_pages)
        try:
            self.session.project.touch()
        except Exception:
            pass

    def _phase2_request_global_page(self, canvas, global_index: int, *, force: bool = False) -> None:
        layout = getattr(self, "_phase2_chapter_layout", None)
        if layout is None:
            return
        global_index = max(0, min(int(global_index), layout.total_pages - 1))
        self._phase2_pending_global_index = global_index

        if self._phase2_canvas_state in {"preparing", "preflight"}:
            return
        if self._phase2_switch_in_progress and not force:
            return

        chapter_index, local_index = layout.locate_global_index(global_index)
        host = getattr(self, "_phase2_canvas_host", None)
        if (
            host is not None
            and host.ready
            and self._phase2_active_chapter_index == chapter_index
        ):
            host.go_to_page(local_index + 1, smooth=False)
            self._phase2_canvas_state = "ready"
            return

        if (
            host is not None
            and host.ready
            and self._phase2_active_chapter_index is not None
        ):
            # Sauvegarde la copie de travail du chapitre avant de détruire son
            # WebView. Aucune écriture dans la Source DOCX.
            old_index = int(self._phase2_active_chapter_index)
            self._phase2_switch_in_progress = True
            self._phase2_canvas_state = "chapter_switch"
            self._phase2_show_overlay(
                canvas,
                "Changement de chapitre",
                "Conservation de la copie de travail puis chargement de la page demandée…",
            )

            def _after_export(exported: dict, old=old_index) -> None:
                self._phase2_apply_exported_chapter(old, exported)
                self._phase2_destroy_current_host()
                self._phase2_active_chapter_index = None
                self._phase2_switch_in_progress = False
                self._phase2_request_global_page(
                    canvas,
                    int(self._phase2_pending_global_index),
                    force=True,
                )

            host.export_document_state(_after_export)
            return

        self._phase2_load_chapter(canvas, chapter_index, local_index)

    def _phase2_load_chapter(self, canvas, chapter_index: int, local_index: int) -> None:
        prepared = getattr(self, "_phase2_chapter_prepared", None)
        detection = getattr(self, "_phase2_chapter_detection", None)
        if prepared is None or detection is None:
            self._phase2_on_failed(canvas, {"stage": "chapter_load", "message": "Préparation du Livre absente."})
            return
        if not (0 <= chapter_index < len(self._phase2_chapter_plans)):
            return

        self._phase2_destroy_current_host()
        self._phase2_loading_chapter_index = chapter_index
        self._phase2_switch_in_progress = True
        self._phase2_canvas_state = "chapter_loading"
        chapter = detection.chapters[chapter_index]
        self._phase2_show_overlay(
            canvas,
            "Ouverture de l’unité",
            str(chapter.title),
        )

        host = CanvasEditorWebHost(
            canvas,
            project_root=PROJECT_ROOT,
            on_ready=lambda snapshot, idx=chapter_index: self._phase2_chapter_ready(canvas, idx, snapshot),
            on_failed=lambda failure: self._phase2_on_failed(canvas, failure),
            on_editorial_choice=lambda event, src=self._phase2_source_path(): (
                self._phase2_persist_choice(src, event) if src is not None else None
            ),
            on_page_changed=self._phase2_on_page_changed,
            background=theme.WINDOW_DEEP,
        )
        self._phase2_canvas_host = host
        host.place(x=0, y=0, relwidth=1, relheight=1)
        try:
            host.lower()
        except Exception:
            pass
        try:
            host.load_document(
                self._phase2_chapter_plans[chapter_index],
                CanvasLoadSession(prepared.canvas.contract),
            )
        except Exception as exc:
            self._phase2_on_failed(
                canvas,
                {"stage": "chapter_load", "message": f"{type(exc).__name__}: {exc}"},
            )
            return
        try:
            self._phase2_canvas_overlay.lift()
        except Exception:
            pass

    def _phase2_chapter_ready(self, canvas, chapter_index: int, snapshot: dict) -> None:
        if chapter_index != self._phase2_loading_chapter_index:
            return
        host = getattr(self, "_phase2_canvas_host", None)
        layout = getattr(self, "_phase2_chapter_layout", None)
        if host is None or layout is None:
            return

        try:
            count = int((snapshot or {}).get("page_count") or 1)
        except (TypeError, ValueError):
            count = 1
        if count != layout.page_counts[chapter_index]:
            layout.set_page_count(chapter_index, count)
            self._phase2_sync_page_count(layout.total_pages)

        self._phase2_active_chapter_index = chapter_index
        self._phase2_loading_chapter_index = None
        self._phase2_switch_in_progress = False
        self._phase2_canvas_state = "ready"
        self._phase2_destroy_overlay()
        try:
            host.show_when_ready(x=0, y=0, relwidth=1, relheight=1)
        except Exception as exc:
            self._phase2_on_failed(canvas, {"stage": "show", "message": str(exc)})
            return

        # Si l'utilisateur a changé de page pendant le chargement, prendre la
        # demande la plus récente, pas celle qui a déclenché l'ouverture.
        target_global = int(self._phase2_pending_global_index)
        target_chapter, local_index = layout.locate_global_index(target_global)
        if target_chapter == chapter_index:
            host.go_to_page(local_index + 1, smooth=False)
        else:
            self.after_idle(lambda: self._phase2_request_global_page(canvas, target_global, force=True))

    def _phase2_on_page_changed(self, event: dict) -> None:
        if self._phase2_canvas_syncing_page:
            return
        layout = getattr(self, "_phase2_chapter_layout", None)
        chapter_index = self._phase2_active_chapter_index
        if layout is None or chapter_index is None:
            return

        # 2.37C : Canvas reste seul propriétaire de la pagination locale. Dès
        # qu'il ajoute ou retire une page dans le chapitre actif, il transmet
        # seulement le nouveau compteur. TomeLinea peut donc mettre à jour le
        # Livre global et la Structure sans exporter le texte ni repaginer les
        # autres chapitres.
        try:
            local_page_count = int(event.get("pageCount") or event.get("page_count") or 0)
        except (TypeError, ValueError):
            local_page_count = 0
        if (
            local_page_count > 0
            and 0 <= int(chapter_index) < len(layout.page_counts)
            and local_page_count != layout.page_counts[int(chapter_index)]
        ):
            layout.set_page_count(int(chapter_index), local_page_count)
            self._phase2_sync_page_count(layout.total_pages)

        try:
            local_page_no = int(event.get("pageNo") or event.get("page_no") or 0)
        except (TypeError, ValueError):
            return
        if local_page_no < 1:
            return

        global_index = layout.global_index(chapter_index, local_page_no - 1)
        book = getattr(self.session, "book", None)
        if book is None:
            return
        # BookV4 contient désormais aussi les quatre faces physiques. Canvas
        # ne doit naviguer que parmi les pages texte internes.
        order = self._phase2_composition_page_ids()
        if global_index >= len(order):
            return
        page_id = str(order[global_index])
        if page_id == str(self.session.active_page_id or ""):
            return
        self._phase2_canvas_syncing_page = True
        try:
            TomeLineaV4Logic._activate_page(self, page_id)
        finally:
            self._phase2_canvas_syncing_page = False

    def _phase2_on_failed(self, canvas, failure: dict) -> None:
        self._phase2_canvas_state = "failed"
        self._phase2_switch_in_progress = False
        self._phase2_canvas_last_failure = dict(failure or {})
        self._phase2_show_overlay(
            canvas,
            "Composition impossible",
            str((failure or {}).get("message") or "Le rendu Canvas n'a pas pu être terminé."),
        )

    def _draw_phase2_canvas_page(self, canvas) -> None:
        canvas.delete("all")

        source = self._phase2_source_path()
        if source is None:
            return
        key = str(source.resolve())

        if self._phase2_canvas_key != key:
            self._phase2_destroy_host()

        if self._phase2_canvas_state == "idle":
            self.after_idle(lambda c=canvas: self._phase2_start_analysis(c))
            self._phase2_show_overlay(
                canvas,
                "Préparation de Composition",
                "Import du contenu et construction du Livre…",
            )
            return
        if self._phase2_canvas_state in {"preparing", "preflight", "blocked", "failed"}:
            return

        global_index = self._phase2_active_page_index()
        if global_index is None:
            return

        host = getattr(self, "_phase2_canvas_host", None)
        if host is not None and host.ready and self._phase2_canvas_state == "ready":
            try:
                host.place(x=0, y=0, relwidth=1, relheight=1)
                host.tk.call("raise", host._w)
                if host._web is not None:
                    host._web.sync_bounds()
            except Exception:
                pass
            self._phase2_request_global_page(canvas, global_index)
            return

        if self._phase2_canvas_state in {"prepared", "chapter_loading", "chapter_switch"}:
            self._phase2_request_global_page(canvas, global_index)


    # ==========================================================
    # CANVAS PAR CHAPITRE / VRAIE PAGE
    # ==========================================================

    def _activate_page(
        self,
        page_id: str,
        *,
        preserve_page_selection: bool = False,
    ) -> None:
        """Navigation TomeLinea + synchronisation du Canvas par chapitre."""
        super()._activate_page(page_id, preserve_page_selection=preserve_page_selection)
        if self.current_workspace != "composition" or not self._phase2_can_render():
            return
        index = self._phase2_active_page_index()
        canvas = getattr(self, "_composition_editor_canvas", None)
        if canvas is None or index is None or self._phase2_canvas_syncing_page:
            return
        try:
            self.after_idle(lambda c=canvas, i=int(index): self._phase2_request_global_page(c, i))
        except Exception:
            pass

















    def _draw_page(self, canvas) -> None:
        if self._phase2_can_render():
            self._draw_phase2_canvas_page(canvas)
            return

        phase2_host = getattr(self, "_phase2_canvas_host", None)
        if phase2_host is not None:
            try:
                phase2_host.place_forget()
            except Exception:
                pass
        super()._draw_page(canvas)



    def _save_project(self) -> None:
        # Seule la copie de travail Canvas du Livre est sauvegardée.
        self._phase2_save_active_before_clear()
        super()._save_project()


    def _docx_source_dialog(self, title: str):
        return filedialog.askopenfilename(
            parent=self,
            title=title,
            filetypes=(
                ("Documents pris en charge", "*.docx *.pdf *.odt"),
                ("Document Word DOCX", "*.docx"),
                ("Document PDF", "*.pdf"),
                ("OpenDocument Texte", "*.odt"),
            ),
        )

    def _create_project_from_source(self) -> None:
        from src.v4.project import ProjectV4
        from src.v4.workspace import WorkspaceSessionV4

        filename = self._docx_source_dialog("Créer un livre TomeLinea")
        if not filename:
            return

        source_path = Path(filename)
        clean_title = " ".join(source_path.stem.replace("_", " ").strip().split()) or "Nouveau livre"

        self._begin_project_transition()
        try:
            project = ProjectV4(title=clean_title)
            self.session = WorkspaceSessionV4(project)
            self.project_path = None
            self.current_workspace = "composition"

            if not self._source_import_file(str(source_path)):
                self._rollback_project_transition()
        except Exception as exc:
            self._rollback_project_transition()
            messagebox.showerror(
                "TomeLinea V4",
                f"Le nouveau projet n'a pas pu être préparé.\n\n{exc}",
                parent=self,
            )

    def _source_import(self) -> None:
        if self.session.project.book is not None:
            messagebox.showinfo(
                "TomeLinea V4",
                "Le Livre existe déjà.\n\nL'ajout de contenu complémentaire sera traité séparément.",
                parent=self,
            )
            return

        filename = self._docx_source_dialog("Choisir la Source du livre")
        if not filename:
            return
        self._source_import_file(filename)

    def _source_import_file(self, filename: str) -> bool:
        if Path(filename).suffix.lower() != ".docx":
            return super()._source_import_file(filename)

        project = self.session.project
        source_path = Path(filename)

        try:
            from src.v4.docx_phase1 import analyze_docx_phase1
            from src.v4.domain import BookFormat, BookKind, BookV4, PageOrigin, PageV4, SourceLink

            element = project.source.register_file(source_path)
            version = element.active_version
            if version is None:
                raise RuntimeError("La version DOCX importée est introuvable.")

            phase1 = analyze_docx_phase1(source_path)
            model = phase1.model
            document = model.get("document", {})
            sections = list(document.get("sections") or [])
            props = sections[0].get("properties", {}) if sections else {}
            page = props.get("page", {}) if isinstance(props, dict) else {}
            margins = props.get("margins", {}) if isinstance(props, dict) else {}

            fmt = BookFormat(
                width_mm=float(page.get("width_mm") or 148.0),
                height_mm=float(page.get("height_mm") or 210.0),
                margin_top_mm=float(margins.get("top_mm") or 15.0),
                margin_bottom_mm=float(margins.get("bottom_mm") or 15.0),
                margin_inside_mm=float(margins.get("left_mm") or 15.0),
                margin_outside_mm=float(margins.get("right_mm") or 15.0),
            )

            book = BookV4(title=project.title, kind=BookKind.UNKNOWN, format=fmt)
            book.metadata["source_kind"] = "docx"
            book.metadata["source_import_contract"] = "content_first"
            book.metadata["working_font_family"] = "Arial"
            book.metadata["source_format"] = {
                "width_mm": fmt.width_mm,
                "height_mm": fmt.height_mm,
                "margin_top_mm": fmt.margin_top_mm,
                "margin_bottom_mm": fmt.margin_bottom_mm,
                "margin_inside_mm": fmt.margin_inside_mm,
                "margin_outside_mm": fmt.margin_outside_mm,
            }

            placeholder = PageV4(
                page_type="Page texte",
                title="Composition",
                origin=PageOrigin.AUTHOR,
                source=SourceLink(source_id=element.id, source_version_id=version.id, source_page=None),
            )
            placeholder.metadata.update({
                "composition_page": True,
                "composition_page_index": 0,
                "composition_page_start": 0,
                "source_placeholder": True,
                "canvas_chapter_index": 0,
            })
            book.add_page(placeholder)

            project.metadata["primary_source_element_id"] = element.id
            project.metadata["source_import_mode"] = "docx_content_first"
            project.metadata["source_document"] = {
                "source_path": str(source_path.resolve()),
                "source_element_id": element.id,
                "source_version_id": version.id,
                "fingerprint": phase1.fingerprint,
                "paragraph_count": int(document.get("paragraph_count") or phase1.paragraph_count),
                "table_count": int(document.get("table_count") or 0),
                "image_count": int(document.get("placed_image_count") or 0),
                "explicit_page_break_count": int(document.get("explicit_page_break_count") or 0),
                "section_count": int(document.get("section_count") or phase1.section_count),
                "source_fonts": list(model.get("fonts", {}).get("used_families") or []),
                "cached_source_pages": model.get("properties", {}).get("extended", {}).get("pages"),
            }
            project.metadata["composition_document"] = {
                "engine": "canvas-editor-by-chapter",
                "import_contract": "content_first",
                "working_font_family": "Arial",
                "page_count": 1,
            }
            project.set_book(book)

            self.session.refresh_context()
            self.current_workspace = "composition"
            self._composition_book_state_open = False
            self._composition_text_flow_open = False
            self._composition_book_state_edit = False
            self._finish_project_transition()
            self.show_workspace("composition")
            return True

        except Exception as exc:
            messagebox.showerror(
                "TomeLinea V4",
                "Impossible d'importer le contenu du DOCX.\n\n" + str(exc),
                parent=self,
            )
            return False



    # ==========================================================
    # FENETRE
    # ==========================================================

    def _fit_to_work_area(
        self,
    ) -> None:

        try:
            
            class RECT(
                ctypes.Structure
            ):
                _fields_ = [
                    (
                        "left",
                        ctypes.c_long,
                    ),
                    (
                        "top",
                        ctypes.c_long,
                    ),
                    (
                        "right",
                        ctypes.c_long,
                    ),
                    (
                        "bottom",
                        ctypes.c_long,
                    ),
                ]

            rect = RECT()

            SPI_GETWORKAREA = (
                0x0030
            )

            ok = (
                ctypes.windll.user32.SystemParametersInfoW(
                    SPI_GETWORKAREA,
                    0,
                    ctypes.byref(
                        rect
                    ),
                    0,
                )
            )

            if ok:
                width = max(
                    1100,
                    rect.right
                    - rect.left,
                )

                height = max(
                    700,
                    rect.bottom
                    - rect.top,
                )

                self.geometry(
                    (
                        f"{width}x{height}"
                        f"+{rect.left}"
                        f"+{rect.top}"
                    )
                )

                return

        except Exception:
            pass

        width = max(
            1100,
            self.winfo_screenwidth(),
        )

        height = max(
            700,
            self.winfo_screenheight()
            - 48,
        )

        self.geometry(
            f"{width}x{height}+0+0"
        )


    # ==========================================================
    # IMAGES
    # ==========================================================

    def _background_source(
        self,
        path: Path,
    ):

        key = str(
            path
        )

        cached = (
            self._editorial_bg_sources.get(
                key
            )
        )

        if cached is not None:
            return cached

        if not path.exists():
            return None

        image = Image.open(
            path
        ).convert(
            "RGB"
        )

        # Traitement doux validé dans l'esprit TomeLinea :
        # on évite le fond criard ou trop contrasté.
        image = (
            ImageEnhance.Color(
                image
            ).enhance(
                0.82
            )
        )

        image = (
            ImageEnhance.Brightness(
                image
            ).enhance(
                0.90
            )
        )

        self._editorial_bg_sources[
            key
        ] = image

        return image


    def _background_photo(
        self,
        path: Path,
        width: int,
        height: int,
        key: str,
    ):

        width = max(
            400,
            int(width),
        )

        height = max(
            300,
            int(height),
        )

        cache_key = (
            str(path),
            width,
            height,
            key,
        )

        cached = (
            self._editorial_bg_cache.get(
                cache_key
            )
        )

        if cached is not None:
            return cached

        source = (
            self._background_source(
                path
            )
        )

        if source is None:
            return None

        source_width, source_height = (
            source.size
        )

        scale = max(
            width / source_width,
            height / source_height,
        )

        resized_width = max(
            width,
            int(
                source_width
                * scale
            ),
        )

        resized_height = max(
            height,
            int(
                source_height
                * scale
            ),
        )

        image = source.resize(
            (
                resized_width,
                resized_height,
            ),
            Image.Resampling.LANCZOS,
        )

        left = max(
            0,
            (
                resized_width
                - width
            ) // 2,
        )

        top = max(
            0,
            (
                resized_height
                - height
            ) // 2,
        )

        image = image.crop(
            (
                left,
                top,
                left + width,
                top + height,
            )
        )

        photo = ImageTk.PhotoImage(
            image
        )

        if len(
            self._editorial_bg_cache
        ) > 10:
            self._editorial_bg_cache.clear()

        self._editorial_bg_cache[
            cache_key
        ] = photo

        return photo


    def _brand_icon_photo(
        self,
        size: int,
    ):

        size = int(
            size
        )

        cached = (
            self._brand_icon_cache.get(
                size
            )
        )

        if cached is not None:
            return cached

        if not BRAND_ICON.exists():
            return None

        image = Image.open(
            BRAND_ICON
        ).convert(
            "RGBA"
        )

        image.thumbnail(
            (
                size,
                size,
            ),
            Image.Resampling.LANCZOS,
        )

        photo = ImageTk.PhotoImage(
            image
        )

        self._brand_icon_cache[
            size
        ] = photo

        return photo


    def _brand_title_photo(
        self,
        width: int,
    ):

        width = int(
            width
        )

        cached = (
            self._brand_title_cache.get(
                width
            )
        )

        if cached is not None:
            return cached

        if not BRAND_TITLE.exists():
            return None

        image = Image.open(
            BRAND_TITLE
        ).convert(
            "RGBA"
        )

        ratio = (
            width
            / max(
                1,
                image.width,
            )
        )

        image = image.resize(
            (
                width,
                max(
                    1,
                    int(
                        image.height
                        * ratio
                    ),
                ),
            ),
            Image.Resampling.LANCZOS,
        )

        photo = ImageTk.PhotoImage(
            image
        )

        self._brand_title_cache[
            width
        ] = photo

        return photo


    # ==========================================================
    # ICONES LIGNE TOMELINEA
    # ==========================================================

    def _line_icon(
        self,
        kind: str,
        size: int = 34,
        color: str | None = None,
    ):
        """
        Pictogrammes TomeLinea V4.

        Trait fin, sans halo.
        Les trois couleurs rappellent les stations du logo :
        céladon, bleu doux et orang?.
        """

        cache_key = (
            "tl_v4_refined",
            kind,
            int(size),
        )

        cached = self._line_icon_cache.get(
            cache_key
        )

        if cached is not None:
            return cached

        scale = 4
        side = max(
            22,
            int(size),
        ) * scale

        image = Image.new(
            "RGBA",
            (side, side),
            (0, 0, 0, 0),
        )

        draw = ImageDraw.Draw(
            image
        )

        celadon = (
            127,
            184,
            174,
            255,
        )

        blue = (
            125,
            151,
            181,
            255,
        )

        orange = (
            210,
            132,
            94,
            255,
        )

        pale = (
            205,
            211,
            213,
            235,
        )

        quiet = (
            125,
            137,
            147,
            175,
        )

        stroke = max(
            4,
            int(side * 0.018),
        )

        thin = max(
            3,
            int(side * 0.012),
        )

        def p(x, y):
            return (
                int(x * side),
                int(y * side),
            )

        # ------------------------------------------------------
        # Ligne éditoriale commune aux trois pictogrammes.
        # ------------------------------------------------------

        draw.line(
            [
                p(0.15, 0.82),
                p(0.85, 0.82),
            ],
            fill=quiet,
            width=thin,
        )

        stations = (
            (0.30, celadon),
            (0.50, blue),
            (0.70, orange),
        )

        radius = max(
            4,
            int(side * 0.025),
        )

        for x, station_color in stations:
            cx, cy = p(
                x,
                0.82,
            )

            draw.ellipse(
                (
                    cx - radius,
                    cy - radius,
                    cx + radius,
                    cy + radius,
                ),
                fill=station_color,
            )

        # ------------------------------------------------------
        # CRÉER
        # Feuille éditoriale + ajout.
        # ------------------------------------------------------

        if kind == "create":

            draw.rounded_rectangle(
                [
                    p(0.25, 0.16),
                    p(0.63, 0.67),
                ],
                radius=max(
                    5,
                    int(side * 0.025),
                ),
                outline=pale,
                width=stroke,
            )

            # Deux lignes de composition.
            draw.line(
                [
                    p(0.33, 0.31),
                    p(0.54, 0.31),
                ],
                fill=blue,
                width=thin,
            )

            draw.line(
                [
                    p(0.33, 0.40),
                    p(0.50, 0.40),
                ],
                fill=celadon,
                width=thin,
            )

            # Petit + TomeLinea, détaché de la page.
            draw.line(
                [
                    p(0.70, 0.30),
                    p(0.70, 0.52),
                ],
                fill=orange,
                width=stroke,
            )

            draw.line(
                [
                    p(0.59, 0.41),
                    p(0.81, 0.41),
                ],
                fill=orange,
                width=stroke,
            )

        # ------------------------------------------------------
        # OUVRIR
        # Deux feuillets qui s'écartent.
        # ------------------------------------------------------

        elif kind == "open":

            draw.line(
                [
                    p(0.20, 0.25),
                    p(0.44, 0.18),
                    p(0.49, 0.63),
                    p(0.25, 0.67),
                    p(0.20, 0.25),
                ],
                fill=pale,
                width=stroke,
                joint="curve",
            )

            draw.line(
                [
                    p(0.49, 0.63),
                    p(0.54, 0.18),
                    p(0.78, 0.25),
                    p(0.73, 0.67),
                    p(0.49, 0.63),
                ],
                fill=pale,
                width=stroke,
                joint="curve",
            )

            draw.line(
                [
                    p(0.30, 0.34),
                    p(0.41, 0.31),
                ],
                fill=celadon,
                width=thin,
            )

            draw.line(
                [
                    p(0.58, 0.31),
                    p(0.69, 0.34),
                ],
                fill=orange,
                width=thin,
            )

            draw.line(
                [
                    p(0.49, 0.21),
                    p(0.49, 0.61),
                ],
                fill=blue,
                width=thin,
            )

        # ------------------------------------------------------
        # PROJET ACTIF
        # Petit livre assemblé / progression.
        # ------------------------------------------------------

        elif kind == "active":

            draw.rounded_rectangle(
                [
                    p(0.23, 0.17),
                    p(0.72, 0.66),
                ],
                radius=max(
                    5,
                    int(side * 0.025),
                ),
                outline=pale,
                width=stroke,
            )

            draw.line(
                [
                    p(0.33, 0.17),
                    p(0.33, 0.66),
                ],
                fill=blue,
                width=thin,
            )

            draw.line(
                [
                    p(0.42, 0.31),
                    p(0.62, 0.31),
                ],
                fill=celadon,
                width=thin,
            )

            draw.line(
                [
                    p(0.42, 0.42),
                    p(0.59, 0.42),
                ],
                fill=orange,
                width=thin,
            )

            # Marque-page très discret.
            draw.line(
                [
                    p(0.62, 0.17),
                    p(0.62, 0.40),
                    p(0.67, 0.35),
                    p(0.72, 0.40),
                    p(0.72, 0.18),
                ],
                fill=orange,
                width=thin,
            )

        else:

            draw.ellipse(
                [
                    p(0.28, 0.22),
                    p(0.72, 0.66),
                ],
                outline=pale,
                width=stroke,
            )

        image = image.resize(
            (
                int(size),
                int(size),
            ),
            Image.Resampling.LANCZOS,
        )

        photo = ImageTk.PhotoImage(
            image
        )

        self._line_icon_cache[
            cache_key
        ] = photo

        return photo

    # ==========================================================
    # BOUTON GLOBAL
    # ==========================================================

    def _button(
        self,
        parent,
        text: str,
        command,
        *,
        accent: bool = False,
        enabled: bool = True,
        compact: bool = False,
        width: int | None = None,
    ):

        return TLButton(
            parent,
            text,
            command,
            primary=accent,
            compact=compact,
            state=(
                "normal"
                if enabled
                else "disabled"
            ),
            width=width,
        )


    # ==========================================================
    # ACCUEIL
    # ==========================================================

    def show_home(
        self,
    ) -> None:

        self._clear()

        screen = tk.Frame(
            self,
            bg=theme.WINDOW_DEEP,
        )

        screen.pack(
            fill="both",
            expand=True,
        )

        background = tk.Label(
            screen,
            bg=theme.WINDOW_DEEP,
            bd=0,
        )

        background.place(
            x=0,
            y=0,
            relwidth=1,
            relheight=1,
        )

        def refresh_background(
            event,
        ):

            photo = (
                self._background_photo(
                    BACKGROUND_HOME,
                    event.width,
                    event.height,
                    "home",
                )
            )

            if photo is not None:
                background.configure(
                    image=photo
                )

                background.image = (
                    photo
                )

        screen.bind(
            "<Configure>",
            refresh_background,
            add="+",
        )

        # ------------------------------------------------------
        # IDENTITE
        # ------------------------------------------------------

        header = tk.Frame(
            screen,
            bg=theme.WINDOW_DEEP,
        )

        header.place(
            relx=0.085,
            rely=0.045,
            relwidth=0.83,
            relheight=0.145,
        )

        brand = tk.Frame(
            header,
            bg=theme.WINDOW_DEEP,
        )

        brand.place(
            relx=0,
            rely=0,
            relwidth=0.68,
            relheight=1,
        )

        icon = (
            self._brand_icon_photo(
                92
            )
        )

        if icon is not None:

            label = tk.Label(
                brand,
                image=icon,
                bg=theme.WINDOW_DEEP,
                bd=0,
            )

            label.image = icon

            label.place(
                x=0,
                y=2,
            )

        title = (
            self._brand_title_photo(
                455
            )
        )

        if title is not None:

            label = tk.Label(
                brand,
                image=title,
                bg=theme.WINDOW_DEEP,
                bd=0,
            )

            label.image = title

            label.place(
                x=110,
                y=8,
            )

        else:

            tk.Label(
                brand,
                text="TomeLinea",
                bg=theme.WINDOW_DEEP,
                fg=theme.INK,
                font=(
                    theme.FONT_TITLE,
                    34,
                ),
            ).place(
                x=110,
                y=10,
            )

        tk.Label(
            brand,
            text="V4",
            bg=theme.WINDOW_DEEP,
            fg=theme.ACCENT,
            font=(
                theme.FONT_UI,
                13,
                "bold",
            ),
        ).place(
            x=575,
            y=16,
        )

        tk.Label(
            brand,
            text=(
                "LA LIGNE ÉDITORIALE "
                "JUSQU’AU LIVRE"
            ),
            bg=theme.WINDOW_DEEP,
            fg=theme.ACCENT,
            font=(
                theme.FONT_UI,
                9,
                "bold",
            ),
        ).place(
            x=114,
            y=75,
        )

        # Aide et Préférences ne sont pas affichées tant que leurs
        # fonctions ne sont pas réellement disponibles. Sur l’Accueil,
        # tout élément qui ressemble à une commande doit être actionnable.

        close = tk.Label(
            header,
            text="✕",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(
                theme.FONT_UI,
                15,
                "bold",
            ),
            cursor="hand2",
            padx=8,
            pady=2,
        )

        close.place(
            relx=0.995,
            y=7,
            anchor="ne",
        )

        close.bind(
            "<Button-1>",
            lambda _event: (
                self.destroy()
            ),
        )

        close.bind(
            "<Enter>",
            lambda _event: (
                close.configure(
                    fg=theme.ERROR
                )
            ),
        )

        close.bind(
            "<Leave>",
            lambda _event: (
                close.configure(
                    fg=theme.INK
                )
            ),
        )

        # ------------------------------------------------------
        # TITRE ACCUEIL
        # ------------------------------------------------------

        intro = tk.Frame(
            screen,
            bg=theme.WINDOW_DEEP,
        )

        intro.place(
            relx=0.105,
            rely=0.235,
            relwidth=0.77,
            relheight=0.105,
        )

        tk.Label(
            intro,
            text="VOTRE LIVRE",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(
                theme.FONT_UI,
                14,
                "bold",
            ),
        ).pack(
            anchor="w"
        )

        tk.Label(
            intro,
            text=(
                "Un projet TomeLinea commence "
                "par sa Source. "
                "Le livre sera compris avant "
                "d'être organisé."
            ),
            bg=theme.WINDOW_DEEP,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                9,
            ),
        ).pack(
            anchor="w",
            pady=(5, 0),
        )

        # Ligne éditoriale / stations.
        line = tk.Canvas(
            intro,
            bg=theme.WINDOW_DEEP,
            height=15,
            bd=0,
            highlightthickness=0,
        )

        line.pack(
            fill="x",
            pady=(12, 0),
        )

        line.create_line(
            0,
            7,
            520,
            7,
            fill=theme.BORDER,
            width=1,
        )

        station_colors = (
            theme.ACCENT,
            "#8DA7C4",
            "#D28A6E",
        )

        for index, color in enumerate(
            station_colors
        ):
            x = (
                80
                + index * 175
            )

            line.create_oval(
                x - 4,
                3,
                x + 4,
                11,
                fill=color,
                outline="",
            )

        # ------------------------------------------------------
        # 3 ACTIONS — NOUVELLE LOGIQUE V4
        # ------------------------------------------------------

        # Les trois entrées sont pos?es directement
        # sur l'écran afin que le fond éditorial reste
        # visible entre elles.
        cards = screen

        active = (
            self.session is not None
        )

        active_name = (
            self.session.project.title
            if active
            else "Aucun projet actif"
        )

        self._home_action_panel(
            cards,
            column=0,
            icon_kind="create",
            title="Créer un projet",
            text=(
                "Créer l'espace de travail, "
                "puis apporter la Source du livre."
            ),
            button="Créer",
            command=(
                self._create_project_dialog
            ),
            primary=True,
        )

        self._home_action_panel(
            cards,
            column=1,
            icon_kind="open",
            title="Ouvrir",
            text=(
                "Ouvrir un projet TomeLinea V4 "
                "déjà enregistré."
            ),
            button="Ouvrir un projet",
            command=self._open_project,
        )

        self._home_action_panel(
            cards,
            column=2,
            icon_kind="active",
            title="Projet actif",
            text=active_name,
            button="Accéder au projet",
            command=lambda: (
                self.show_workspace(
                    self.current_workspace
                )
            ),
            enabled=active,
        )



    def _home_action_panel(
        self,
        parent,
        *,
        column: int,
        icon_kind: str,
        title: str,
        text: str,
        button: str,
        command,
        primary: bool = False,
        enabled: bool = True,
    ) -> None:

        # Même matière pour les trois entrées :
        # l'action principale est indiqu?e par le contenu,
        # pas par un énorme encadrement coloré.
        panel = CutPanel(
            parent,
            fill="#252C35",
            border="#44505A",
            cut=10,
            padding=(
                18,
                15,
            ),
        )

        positions = {
            0: 0.120,
            1: 0.385,
            2: 0.650,
        }

        panel.place(
            relx=positions[column],
            rely=0.405,
            relwidth=0.230,
            relheight=0.285,
        )

        body = panel.body

        # Petit bandeau supérieur, plus proche d'une station
        # que d'une carte d'application.
        top = tk.Frame(
            body,
            bg="#252C35",
        )

        top.pack(
            fill="x",
            pady=(0, 9),
        )

        icon = self._line_icon(
            icon_kind,
            36,
        )

        icon_label = tk.Label(
            top,
            image=icon,
            bg="#252C35",
            bd=0,
        )

        icon_label.image = icon

        icon_label.pack(
            side="left"
        )

        # Trait éditorial discret.
        rule = tk.Canvas(
            top,
            width=72,
            height=12,
            bg="#252C35",
            bd=0,
            highlightthickness=0,
        )

        rule.pack(
            side="left",
            padx=(11, 0),
        )

        rule.create_line(
            1,
            6,
            68,
            6,
            fill=(
                theme.ACCENT
                if primary
                else theme.BORDER
            ),
            width=1,
        )

        rule.create_oval(
            30,
            3,
            36,
            9,
            fill=(
                theme.ACCENT
                if primary
                else theme.MUTED_DARK
            ),
            outline="",
        )


        tk.Label(
            body,
            text=title,
            bg="#252C35",
            fg=theme.INK,
            font=(
                theme.FONT_TITLE,
                15,
                "bold",
            ),
        ).pack(
            anchor="w",
            pady=(3, 6),
        )

        tk.Label(
            body,
            text=text,
            bg="#252C35",
            fg=theme.MUTED,
            justify="left",
            wraplength=230,
            font=(
                theme.FONT_UI,
                8,
            ),
        ).pack(
            anchor="w"
        )

        tk.Frame(
            body,
            bg="#252C35",
            height=9,
        ).pack(
            fill="x"
        )

        tk.Frame(
            body,
            bg="#252C35",
        ).pack(
            fill="both",
            expand=True,
        )

        self._button(
            body,
            button,
            command,
            accent=primary,
            enabled=enabled,
            compact=True,
        ).pack(
            anchor="w",
            pady=(5, 2),
        )

    # ==========================================================
    # CREATION — AUCUN TYPE DE LIVRE
    # ==========================================================

    def _create_project_dialog(
        self,
    ) -> None:

        # Le cas normal ne nécessite plus
        # de dialogue de création.
        #
        # L'utilisateur choisit directement
        # le document original.
        self._create_project_from_source()

    def _build_workspace_header(
        self,
        parent,
    ) -> None:

        has_book = (
            self.session.project.book
            is not None
        )

        bar = tk.Frame(
            parent,
            bg=theme.WINDOW_DEEP,
            height=68,
        )

        bar.pack(
            fill="x"
        )

        bar.pack_propagate(
            False
        )

        # Accueil.
        left = tk.Frame(
            bar,
            bg=theme.WINDOW_DEEP,
        )

        left.pack(
            side="left",
            fill="y",
            padx=(18, 10),
        )

        self._button(
            left,
            "Accueil",
            self.show_home,
            compact=True,
        ).pack(
            side="left",
            pady=17,
        )

        # Marque compacte.
        brand = tk.Frame(
            left,
            bg=theme.WINDOW_DEEP,
        )

        brand.pack(
            side="left",
            padx=(17, 20),
            pady=8,
        )

        icon = self._brand_icon_photo(
            42
        )

        if icon is not None:

            label = tk.Label(
                brand,
                image=icon,
                bg=theme.WINDOW_DEEP,
                bd=0,
            )

            label.image = icon

            label.pack(
                side="left"
            )

        title = (
            self._brand_title_photo(
                150
            )
        )

        if title is not None:

            label = tk.Label(
                brand,
                image=title,
                bg=theme.WINDOW_DEEP,
                bd=0,
            )

            label.image = title

            label.pack(
                side="left",
                padx=(7, 0),
            )

        # Navigation.
        nav = tk.Frame(
            bar,
            bg=theme.WINDOW_DEEP,
        )

        nav.pack(
            side="left",
            fill="y",
        )

        for key, label in theme.NAV_ITEMS:

            enabled = (
                key == "source"
                or has_book
            )

            active = (
                key
                == self.current_workspace
            )

            wrap = tk.Frame(
                nav,
                bg=theme.WINDOW_DEEP,
            )

            wrap.pack(
                side="left",
                fill="y",
                padx=3,
            )

            button = tk.Button(
                wrap,
                text=label,
                command=lambda k=key: (
                    self.show_workspace(
                        k
                    )
                ),
                state=(
                    tk.NORMAL
                    if enabled
                    else tk.DISABLED
                ),
                bg=theme.WINDOW_DEEP,
                fg=(
                    theme.ACCENT_BRIGHT
                    if active
                    else theme.MUTED
                ),
                disabledforeground=theme.MUTED_DARK,
                activebackground=theme.WINDOW_DEEP,
                activeforeground=theme.WHITE,
                relief="flat",
                bd=0,
                padx=12,
                pady=8,
                font=(
                    theme.FONT_UI,
                    9,
                    (
                        "bold"
                        if active
                        else "normal"
                    ),
                ),
                cursor=(
                    "hand2"
                    if enabled
                    else "arrow"
                ),
            )

            button.pack(
                pady=(13, 0),
            )

            tk.Frame(
                wrap,
                bg=(
                    theme.ACCENT
                    if active
                    else theme.WINDOW_DEEP
                ),
                height=2,
            ).pack(
                fill="x",
                padx=8,
            )

        # Outils à droite.
        right = tk.Frame(
            bar,
            bg=theme.WINDOW_DEEP,
        )

        right.pack(
            side="right",
            fill="y",
            padx=(10, 18),
        )

        close = tk.Label(
            right,
            text="✕",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(
                theme.FONT_UI,
                13,
                "bold",
            ),
            cursor="hand2",
            padx=8,
        )

        close.pack(
            side="right",
            pady=20,
            padx=(8, 0),
        )

        close.bind(
            "<Button-1>",
            lambda _event: (
                self.destroy()
            ),
        )

        close.bind(
            "<Enter>",
            lambda _event: (
                close.configure(
                    fg=theme.ERROR
                )
            ),
        )

        close.bind(
            "<Leave>",
            lambda _event: (
                close.configure(
                    fg=theme.INK
                )
            ),
        )

        self._button(
            right,
            "Enregistrer",
            self._save_project,
            accent=True,
            compact=True,
        ).pack(
            side="right",
            pady=17,
            padx=4,
        )

        # IMPORTANT : le bandeau éditorial remplace entièrement celui de
        # TomeLineaV4. Il doit donc conserver les références aux mêmes
        # commandes d'historique et raccorder explicitement la session.
        # Sans cela, les boutons restent dans l'état calculé à l'ouverture
        # et ne voient jamais les nouvelles entrées Undo/Redo.
        self._workspace_redo_button = self._button(
            right,
            "Rétablir",
            self._redo,
            compact=True,
            enabled=True,
        )
        self._workspace_redo_button.pack(
            side="right",
            pady=17,
            padx=3,
        )

        self._workspace_undo_button = self._button(
            right,
            "Annuler",
            self._undo,
            compact=True,
            enabled=True,
        )
        self._workspace_undo_button.pack(
            side="right",
            pady=17,
            padx=3,
        )

        # Le moteur d'historique notifie immédiatement le bandeau après
        # chaque transaction, y compris Ajouter/Supprimer une page, les
        # contraintes et les futures modifications de texte.
        self.session.set_history_change_callback(
            self._refresh_history_buttons
        )

        # Synchronisation initiale après construction des widgets.
        self._refresh_history_buttons()


    # ==========================================================
    # SOURCE — PEAU TOMELINEA
    # ==============================================================


    def _build_source(
        self,
        parent,
    ) -> None:
        """
        Compatibilité interne uniquement.

        Source n'est plus un bureau utilisateur.
        Le moteur Source reste actif dans src.v4.
        """

        project = self.session.project

        if project.book is not None:
            self.current_workspace = "composition"

            self.after_idle(
                lambda: self.show_workspace(
                    "composition"
                )
            )

            return

        # Ce cas ne doit normalement plus être visible :
        # la création attend simplement que l'analyse construise
        # le Livre avant d'ouvrir Composition.
        tk.Label(
            parent,
            text="Préparation du livre\u2026",
            bg=theme.WINDOW_DEEP,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                10,
            ),
        ).pack(
            expand=True,
        )

    def _summary_value(
        self,
        parent,
        label: str,
        value: str,
    ) -> None:

        tk.Label(
            parent,
            text=label,
            bg="#252C35",
            fg=theme.MUTED_DARK,
            font=(
                theme.FONT_UI,
                8,
                "bold",
            ),
        ).pack(
            anchor="w",
            pady=(12, 2),
        )

        tk.Label(
            parent,
            text=value,
            bg="#252C35",
            fg=theme.INK,
            font=(
                theme.FONT_UI,
                10,
            ),
        ).pack(
            anchor="w"
        )


    # ==========================================================
    # HISTORIQUE — RAFRAICHISSEMENT SANS RECONSTRUCTION COMPLETE
    # ==============================================================

    def _undo(
        self,
    ) -> None:

        # Dans Composition, utiliser le rafraichissement ciblé de
        # TomeLineaV4. Le chemin générique appelle show_workspace(),
        # détruit le bureau puis le reconstruit entièrement et provoque
        # le flash visible lors d'Annuler/Rétablir.
        if self.current_workspace == "composition":
            self._composition_undo()
            return

        super()._undo()


    def _redo(
        self,
    ) -> None:

        if self.current_workspace == "composition":
            self._composition_redo()
            return

        super()._redo()


    # ==========================================================
    # BARRE BASSE
    # ==============================================================

    def _build_status(
        self,
        parent,
    ) -> None:

        bar = tk.Frame(
            parent,
            bg="#1E242C",
            height=27,
        )

        bar.pack(
            fill="x",
            side="bottom",
        )

        bar.pack_propagate(
            False
        )

        path_text = (
            str(
                self.project_path
            )
            if self.project_path
            else "Projet non enregistré"
        )

        tk.Label(
            bar,
            text=path_text,
            bg="#1E242C",
            fg=theme.MUTED_DARK,
            font=(
                theme.FONT_UI,
                8,
            ),
        ).pack(
            side="left",
            padx=14,
        )

        phase = (
            "Source · Analyse"
            if self.session.project.book
            is None
            else (
                self.current_workspace.capitalize()
            )
        )

        tk.Label(
            bar,
            text=(
                f"TomeLinea V4   •   {phase}"
            ),
            bg="#1E242C",
            fg=theme.ACCENT_DARK,
            font=(
                theme.FONT_UI,
                8,
                "bold",
            ),
        ).pack(
            side="right",
            padx=14,
        )
