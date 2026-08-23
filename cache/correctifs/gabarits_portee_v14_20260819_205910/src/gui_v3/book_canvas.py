from __future__ import annotations

import tkinter as tk
import tkinter.font as tkfont
from copy import deepcopy
import shutil
from pathlib import Path
from typing import Callable
from uuid import uuid4

from src.gui_v3 import theme
from src.gui_v3.page_visual_catalog import canonical_page_type, page_visual_definition, structure_builtin_catalog
from src.gui_v3.structure_core import migrate_structure_data
# STRUCTURE_ETAPE1_V332 : socle nettoyé, moteur Page auto unique, catalogue canonique.

try:
    from PIL import Image, ImageTk
except Exception:  # Pillow reste optionnel pour les aperçus réels.
    Image = None
    ImageTk = None


class TLScrollbar(tk.Canvas):
    """Curseur TomeLinea léger et indépendant du thème Windows."""

    def __init__(self, parent, *, orient: str, command):
        self.orient = orient
        self.command = command
        width = 12 if orient == "vertical" else 1
        height = 1 if orient == "vertical" else 12
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=theme.WINDOW_DEEP,
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        self._first = 0.0
        self._last = 1.0
        self._drag_offset = 0.0
        self._dragging = False
        self.bind("<Configure>", self._redraw)
        self.bind("<Button-1>", self._press)
        self.bind("<B1-Motion>", self._drag)
        self.bind("<ButtonRelease-1>", self._release)

    def set(self, first, last):
        try:
            self._first = max(0.0, min(1.0, float(first)))
            self._last = max(self._first, min(1.0, float(last)))
        except (TypeError, ValueError):
            self._first, self._last = 0.0, 1.0
        self._redraw()

    def _axis_length(self) -> int:
        return max(1, self.winfo_height() if self.orient == "vertical" else self.winfo_width())

    def _cross_length(self) -> int:
        return max(1, self.winfo_width() if self.orient == "vertical" else self.winfo_height())

    def _thumb_geometry(self) -> tuple[float, float]:
        length = self._axis_length()
        start = self._first * length
        end = self._last * length
        min_thumb = min(length, 28)
        if end - start < min_thumb:
            center = (start + end) / 2.0
            start = max(0.0, min(length - min_thumb, center - min_thumb / 2.0))
            end = min(length, start + min_thumb)
        return start, end

    def _redraw(self, _event=None):
        self.delete("all")
        length = self._axis_length()
        cross = self._cross_length()
        # Rail graphite, trait céladon et petite touche or rappelant la signature TomeLinea.
        if self.orient == "vertical":
            cx = cross / 2.0
            self.create_line(cx, 5, cx, max(5, length - 5), fill=theme.BORDER_SOFT, width=2)
        else:
            cy = cross / 2.0
            self.create_line(5, cy, max(5, length - 5), cy, fill=theme.BORDER_SOFT, width=2)

        if self._last >= 0.999 and self._first <= 0.001:
            return

        start, end = self._thumb_geometry()
        pad = 3
        if self.orient == "vertical":
            x1, x2 = pad, max(pad + 2, cross - pad)
            self.create_rectangle(x1, start, x2, end, fill=theme.ACCENT_DARK, outline=theme.ACCENT_BRIGHT, width=1)
            self.create_line(x1 + 1, start + 2, x2 - 1, start + 2, fill="#E7C37A", width=1)
        else:
            y1, y2 = pad, max(pad + 2, cross - pad)
            self.create_rectangle(start, y1, end, y2, fill=theme.ACCENT_DARK, outline=theme.ACCENT_BRIGHT, width=1)
            self.create_line(start + 2, y1 + 1, start + 2, y2 - 1, fill="#E7C37A", width=1)

    def _coord(self, event) -> float:
        return float(event.y if self.orient == "vertical" else event.x)

    def _press(self, event):
        if self._last >= 0.999 and self._first <= 0.001:
            return "break"
        pos = self._coord(event)
        start, end = self._thumb_geometry()
        if start <= pos <= end:
            self._dragging = True
            self._drag_offset = pos - start
        else:
            thumb = max(1.0, end - start)
            target = (pos - thumb / 2.0) / max(1.0, self._axis_length() - thumb)
            self.command("moveto", max(0.0, min(1.0, target)))
        return "break"

    def _drag(self, event):
        if not self._dragging:
            return "break"
        start, end = self._thumb_geometry()
        thumb = max(1.0, end - start)
        target = (self._coord(event) - self._drag_offset) / max(1.0, self._axis_length() - thumb)
        self.command("moveto", max(0.0, min(1.0, target)))
        return "break"

    def _release(self, _event=None):
        self._dragging = False
        return "break"


class TLBookNavigator(tk.Canvas):
    """Commande horizontale TomeLinea : point central à retour automatique."""

    TICK_MS = 46

    def __init__(self, parent, *, command):
        super().__init__(
            parent,
            width=390,
            height=50,
            bg=theme.WINDOW_DEEP,
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        self.command = command
        self._velocity = 0.0
        self._dragging = False
        self._enabled = False
        self._part_text = ""
        self._tick_job = None
        self.bind("<Configure>", self._redraw)
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<B1-Motion>", self._drag)
        self.bind("<ButtonRelease-1>", self._release)
        self.bind("<Leave>", self._leave)

    def set_enabled(self, enabled: bool):
        self._enabled = bool(enabled)
        if not self._enabled:
            self._velocity = 0.0
            self._cancel_tick()
        self._redraw()

    def set_part(self, text: str):
        text = str(text or "").strip()
        if text == self._part_text:
            return
        self._part_text = text
        self._redraw()

    def _geometry(self) -> tuple[float, float, float]:
        width = max(180.0, float(self.winfo_width()))
        center = width / 2.0
        half = max(70.0, min(160.0, width * 0.38))
        return center, center - half, center + half

    def _redraw(self, _event=None):
        self.delete("all")
        width = max(1, self.winfo_width())
        center, x1, x2 = self._geometry()
        label = self._part_text or "Partie visible"
        self.create_text(
            width / 2.0,
            10,
            text=label,
            fill=theme.ACCENT_BRIGHT if self._enabled else theme.MUTED_DARK,
            font=(theme.FONT_UI, 10, "bold"),
            anchor="center",
        )
        y = 34
        self.create_line(x1, y, x2, y, fill=theme.BORDER_SOFT, width=2)
        self.create_line(center - 18, y, center + 18, y, fill=theme.ACCENT_DARK, width=2)
        # Repère central discret.
        self.create_line(center, y - 7, center, y + 7, fill="#E7C37A", width=1)
        knob_x = center + self._velocity * (x2 - center)
        if not self._enabled:
            knob_x = center
        # Halo rétro-éclairé, sans gros cadre.
        self.create_oval(knob_x - 10, y - 10, knob_x + 10, y + 10, fill=theme.ACCENT_SOFT, outline="")
        self.create_oval(knob_x - 6, y - 6, knob_x + 6, y + 6, fill=theme.ACCENT_DARK, outline=theme.ACCENT_BRIGHT, width=1)
        self.create_oval(knob_x - 2, y - 2, knob_x + 2, y + 2, fill="#E7C37A", outline="")
        if self._enabled:
            self.create_text(x1 - 14, y, text="‹", fill=theme.MUTED_DARK, font=(theme.FONT_UI, 13), anchor="center")
            self.create_text(x2 + 14, y, text="›", fill=theme.MUTED_DARK, font=(theme.FONT_UI, 13), anchor="center")

    def _velocity_from_x(self, x: float) -> float:
        center, x1, x2 = self._geometry()
        if x >= center:
            denom = max(1.0, x2 - center)
        else:
            denom = max(1.0, center - x1)
        value = max(-1.0, min(1.0, (x - center) / denom))
        # Petite zone neutre pour viser précisément le centre.
        if abs(value) < 0.08:
            return 0.0
        sign = 1.0 if value > 0 else -1.0
        return sign * ((abs(value) - 0.08) / 0.92)

    def _press(self, event):
        if not self._enabled:
            return "break"
        self._dragging = True
        self._set_velocity(self._velocity_from_x(float(event.x)))
        return "break"

    def _drag(self, event):
        if not self._dragging or not self._enabled:
            return "break"
        self._set_velocity(self._velocity_from_x(float(event.x)))
        return "break"

    def _release(self, _event=None):
        self._dragging = False
        self._set_velocity(0.0)
        return "break"

    def _leave(self, _event=None):
        if not self._dragging:
            return
        # Si la souris sort pendant un glisser, on conserve la commande :
        # ButtonRelease remettra le point au centre.

    def _set_velocity(self, value: float):
        self._velocity = max(-1.0, min(1.0, float(value))) if self._enabled else 0.0
        self._redraw()
        if self._velocity == 0.0:
            self._cancel_tick()
        elif self._tick_job is None:
            self._tick_job = self.after(self.TICK_MS, self._tick)

    def _tick(self):
        self._tick_job = None
        if not self._enabled or not self._dragging or self._velocity == 0.0:
            return
        self.command(self._velocity)
        self._tick_job = self.after(self.TICK_MS, self._tick)

    def _cancel_tick(self):
        job = self._tick_job
        self._tick_job = None
        if job is not None:
            try:
                self.after_cancel(job)
            except Exception:
                pass


class TLZoomNavigator(tk.Canvas):
    """Commande de zoom TomeLinea : même geste que le navigateur de ligne."""

    TICK_MS = 46

    def __init__(self, parent, *, command):
        super().__init__(parent, width=220, height=50, bg=theme.WINDOW_DEEP, bd=0, highlightthickness=0, cursor="hand2")
        self.command = command
        self._velocity = 0.0
        self._dragging = False
        self._enabled = True
        self._caption = "Zoom"
        self._tick_job = None
        self.bind("<Configure>", self._redraw)
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<B1-Motion>", self._drag)
        self.bind("<ButtonRelease-1>", self._release)

    def set_caption(self, text: str):
        self._caption = str(text or "Zoom")
        self._redraw()

    def set_enabled(self, enabled: bool):
        self._enabled = bool(enabled)
        if not self._enabled:
            self._velocity = 0.0
            self._cancel_tick()
        self._redraw()

    def _geometry(self) -> tuple[float, float, float]:
        # Le navigateur historique doit aussi pouvoir vivre dans l’inspecteur
        # compact de Gabarits. Les grandes versions conservent exactement leur
        # amplitude, les petites réduisent simplement la course du bouton.
        width = max(90.0, float(self.winfo_width()))
        center = width / 2.0
        half = max(30.0, min(102.0, width * 0.34))
        return center, center - half, center + half

    def _redraw(self, _event=None):
        self.delete("all")
        width = max(1, self.winfo_width())
        center, x1, x2 = self._geometry()
        self.create_text(width / 2.0, 10, text=self._caption, fill=theme.ACCENT_BRIGHT if self._enabled else theme.MUTED_DARK, font=(theme.FONT_UI, 9, "bold"), anchor="center")
        y = 34
        self.create_line(x1, y, x2, y, fill=theme.BORDER_SOFT, width=2)
        self.create_line(center - 18, y, center + 18, y, fill=theme.ACCENT_DARK, width=2)
        self.create_line(center, y - 7, center, y + 7, fill="#E7C37A", width=1)
        knob_x = center + self._velocity * (x2 - center)
        if not self._enabled:
            knob_x = center
        self.create_oval(knob_x - 10, y - 10, knob_x + 10, y + 10, fill=theme.ACCENT_SOFT, outline="")
        self.create_oval(knob_x - 6, y - 6, knob_x + 6, y + 6, fill=theme.ACCENT_DARK, outline=theme.ACCENT_BRIGHT, width=1)
        self.create_oval(knob_x - 2, y - 2, knob_x + 2, y + 2, fill="#E7C37A", outline="")
        self.create_text(x1 - 10, y, text="−", fill=theme.MUTED_DARK, font=(theme.FONT_UI, 12, "bold"), anchor="center")
        self.create_text(x2 + 10, y, text="+", fill=theme.MUTED_DARK, font=(theme.FONT_UI, 12, "bold"), anchor="center")

    def _velocity_from_x(self, x: float) -> float:
        center, x1, x2 = self._geometry()
        denom = max(1.0, (x2 - center) if x >= center else (center - x1))
        value = max(-1.0, min(1.0, (x - center) / denom))
        if abs(value) < 0.08:
            return 0.0
        sign = 1.0 if value > 0 else -1.0
        return sign * ((abs(value) - 0.08) / 0.92)

    def _press(self, event):
        if not self._enabled:
            return "break"
        self._dragging = True
        self._set_velocity(self._velocity_from_x(float(event.x)))
        return "break"

    def _drag(self, event):
        if not self._dragging or not self._enabled:
            return "break"
        self._set_velocity(self._velocity_from_x(float(event.x)))
        return "break"

    def _release(self, _event=None):
        self._dragging = False
        self._set_velocity(0.0)
        return "break"

    def _set_velocity(self, value: float):
        self._velocity = max(-1.0, min(1.0, float(value))) if self._enabled else 0.0
        self._redraw()
        if self._velocity == 0.0:
            self._cancel_tick()
        elif self._tick_job is None:
            self._tick_job = self.after(self.TICK_MS, self._tick)

    def _tick(self):
        self._tick_job = None
        if not self._enabled or not self._dragging or self._velocity == 0.0:
            return
        self.command(self._velocity)
        self._tick_job = self.after(self.TICK_MS, self._tick)

    def _cancel_tick(self):
        job = self._tick_job
        self._tick_job = None
        if job is not None:
            try:
                self.after_cancel(job)
            except Exception:
                pass


class BookCanvas(tk.Frame):
    """Zone B TomeLinea : structure du livre en deux niveaux, parties puis pages."""

    MIN_ZOOM = 20
    MAX_ZOOM = 800
    BASE_PAGE_W = 420
    BASE_PAGE_H = 594
    BASE_GAP = 34
    BASE_GROUP_GAP = 76
    MARGIN = 34
    GROUP_H = 58
    GROUP_TO_PAGE = 16
    EMPTY_SLOT_W = 260

    START_GROUP_ID = "debut_livre"
    DEFAULT_GROUP_ID = "pages_interieures"
    END_GROUP_ID = "fin_livre"

    GOLD = "#E7C37A"
    ORANGE = "#E47A45"
    BOOK_GREEN = "#86A98C"

    DEFAULT_GROUPS = (
        {
            "id": START_GROUP_ID,
            "title": "Début du livre",
            "part_title": "",
            "symbol": "flag",
            "accent": GOLD,
            "protected": True,
        },
        {
            "id": DEFAULT_GROUP_ID,
            "title": "Partie 1",
            "part_title": "",
            "symbol": "book",
            "accent": theme.ACCENT_BRIGHT,
            "protected": False,
        },
        {
            "id": END_GROUP_ID,
            "title": "Fin du livre",
            "part_title": "",
            "symbol": "book_end",
            "accent": BOOK_GREEN,
            "protected": True,
        },
    )

    COVER_TYPES = {"couverture", "cover", "front_cover"}
    BACK_COVER_TYPES = {"quatrieme", "quatrieme_couverture", "4e_couverture", "back_cover"}
    SECOND_COVER_TYPES = {
        "deuxieme_couverture", "2e_couverture", "second_cover", "inside_front_cover",
        "2e de couverture", "deuxieme de couverture", "deuxième de couverture",
    }
    THIRD_COVER_TYPES = {
        "troisieme_couverture", "3e_couverture", "third_cover", "inside_back_cover",
        "3e de couverture", "troisieme de couverture", "troisième de couverture",
    }

    # Zone C — quelques types vraiment structurels manquaient au catalogue historique.
    # Ils restent volontairement peu nombreux : un élément de composition (schéma,
    # encadré, graphique...) n'est pas un type de page Structure.
    STRUCTURE_EXTRA_PAGE_TYPES = (
        {
            "type": "planche", "label": "Planche", "short_label": "Planche",
            "visual": "text", "family": "corps", "custom": False,
            "duplicable": True, "structure_builtin": True,
        },
        {
            "type": "mode_emploi", "label": "Mode d’emploi", "short_label": "Mode d’emploi",
            "visual": "text", "family": "ouverture", "custom": False,
            "duplicable": True, "structure_builtin": True,
        },
        {
            "type": "resume_precedent", "label": "Résumé précédent", "short_label": "Résumé précédent",
            "visual": "text", "family": "ouverture", "custom": False,
            "duplicable": True, "structure_builtin": True,
        },
        {
            "type": "presentation_personnages", "label": "Personnages", "short_label": "Personnages",
            "visual": "text", "family": "ouverture", "custom": False,
            "duplicable": True, "structure_builtin": True,
        },
        {
            "type": "bonus", "label": "Bonus / annexe", "short_label": "Bonus",
            "visual": "text", "family": "fin", "custom": False,
            "duplicable": True, "structure_builtin": True,
        },
    )

    # Petite zone « Courants » + grande zone « Autres types ».
    # Les listes sont adaptées au type de livre et volontairement resserrées.
    STRUCTURE_PALETTE_DEFAULTS = {
        "livre_textuel": {
            "current": ("texte", "chapitre", "tete_partie", "illustration", "page_blanche"),
            "other": (
                "page_titre", "mentions_legales", "dedicace", "sommaire",
                "carte", "remerciements", "a_propos_auteur", "autres_ouvrages",
            ),
        },
        "ouvrage_structure": {
            "current": ("fiche", "tete_partie", "texte", "illustration", "annexe"),
            "other": (
                "page_titre", "mentions_legales", "sommaire", "mode_emploi",
                "carte", "page_blanche", "glossaire", "index", "sources",
                "bibliographie", "a_propos_auteur",
            ),
        },
        "bande_dessinee": {
            "current": ("planche", "tete_partie", "illustration", "page_blanche"),
            "other": (
                "page_titre", "mentions_legales", "resume_precedent",
                "presentation_personnages", "carte", "bonus", "remerciements",
                "a_propos_auteur", "autres_ouvrages",
            ),
        },
    }
    STRUCTURE_PALETTE_KEY = "structure_type_palette"

    # Défilement de bord volontairement progressif : précis près de la cible,
    # encore assez vif pour traverser une longue partie.
    AUTO_SCROLL_EDGE = 88
    AUTO_SCROLL_INTERVAL_MS = 46
    AUTO_SCROLL_MAX_SPEED = 3

    # Quatre niveaux visuels indépendants de la partie active.
    PAGE_SIZE_AUTO = 0.26
    PAGE_AUTO_REST_W = 0.12
    PAGE_AUTO_REST_H = 0.50
    # Déployée, la page auto redevient une vraie miniature : même ratio que la page source.
    PAGE_AUTO_DEPLOY_W = 0.56
    PAGE_AUTO_DEPLOY_H = 0.56
    PAGE_SIZE_NORMAL = 0.82
    PAGE_SIZE_PART_HEAD = 0.98
    PAGE_SIZE_SELECTED = 1.16
    PAGE_LABEL_H = 20
    PAGE_NAME_H = 0

    def __init__(
        self,
        parent,
        *,
        on_open_item: Callable[[dict, int], None],
        on_change: Callable[[], None] | None = None,
        on_focus_change: Callable[[bool], None] | None = None,
        on_history_change: Callable[[bool, bool], None] | None = None,
    ):
        super().__init__(parent, bg=theme.PANEL)
        self.on_open_item = on_open_item
        self.on_change = on_change
        self.on_focus_change = on_focus_change
        self.on_history_change = on_history_change
        self.project = None
        self.items: list[dict] = []
        self.groups: list[dict] = [dict(group) for group in self.DEFAULT_GROUPS]
        self._data: dict = {}

        self._selected_index: int | None = None
        self._selected_group_id: str | None = None
        # V24 — sélection multiple : on mémorise les pages principales par ID.
        # Les pages automatiques liées suivent visuellement et fonctionnellement leur source.
        self._selected_page_ids: set[str] = set()
        # V25 — Page auto n'est plus une insertion locale : c'est un mode
        # temporaire qui crée une règle générale pour un type de page.
        self._structure_page_auto_mode: dict | None = None
        self._structure_last_auto_type: str = ""
        self._selection_box_start: tuple[float, float] | None = None
        self._selection_box_current: tuple[float, float] | None = None
        self._selection_box_active = False
        self._page_hitboxes: dict[int, tuple[float, float, float, float]] = {}
        self._group_hitboxes: dict[str, tuple[float, float, float, float]] = {}
        self._group_page_bounds: dict[str, tuple[float, float]] = {}
        self._visual_indices: list[int] = []

        self._drag_kind: str | None = None
        self._drag_start_index: int | None = None
        self._drag_selected_page_ids: set[str] = set()
        self._drag_target_index: int | None = None
        self._drag_target_group_id: str | None = None
        self._drag_target_local_pos: int | None = None
        self._drag_group_id: str | None = None
        self._drag_group_target: int | None = None
        self._drag_start_xy: tuple[int, int] | None = None
        self._dragging = False
        self._drag_pointer_xy: tuple[int, int] | None = None
        self._drag_autoscroll_direction = 0
        self._drag_autoscroll_speed = 0
        self._drag_autoscroll_job = None
        self._render_pending = None
        self._page_focus = False
        self._book_zoom_cap = 100
        self._hover_index: int | None = None
        self._hover_group_id: str | None = None
        self._v_scroll_needed = False
        self._h_scroll_needed = False
        self._sticky_part_job = None
        self._title_editor = None
        self._title_editor_window = None
        self._editing_group_id: str | None = None
        self._page_name_editor = None
        self._page_name_editor_window = None
        self._editing_page_index: int | None = None
        self._page_name_hitboxes: dict[int, tuple[float, float, float, float]] = {}
        self._image_refs: list[object] = []

        # Le zoom du livre reste interne et stable. Les commandes visibles
        # pilotent uniquement la page en surimpression : la ligne ne bouge plus.
        self._book_zoom = 36
        self.viewer_zoom_var = tk.IntVar(value=100)
        self.zoom_text_var = tk.StringVar(value="100 %")
        self._overlay_active = False
        self._overlay_page_index: int | None = None
        self._overlay_pan_x = 0.0
        self._overlay_pan_y = 0.0
        self._overlay_drag_origin: tuple[float, float] | None = None
        self._overlay_pan_origin: tuple[float, float] | None = None
        self._overlay_page_box: tuple[float, float, float, float] | None = None
        self._overlay_render_job = None
        self._overlay_quality_job = None
        self._overlay_fast = False
        self._overlay_image_refs: list[object] = []
        self._overlay_source_cache: dict[str, object] = {}
        self._overlay_brand_refs: list[object] = []
        self._overlay_bg_photo = None
        self._overlay_zoom_anchor: tuple[float, float] | None = None
        self._overlay_zoom_ratio: tuple[float, float] = (0.5, 0.5)
        self.status_var = tk.StringVar(value="Livre en attente")
        self._work_mode = "structure"
        self.work_title_var = tk.StringVar(value="Structure du livre")

        # Gabarits : on travaille directement sur une vraie page, jamais sur le squelette.
        # 100 % signifie « ajusté au plus grand format entièrement visible dans B ».
        self._gabarit_zoom = 100
        self._gabarit_zoom_text_var = tk.StringVar(value="100 %")
        self._gabarit_pan_x = 0.0
        self._gabarit_pan_y = 0.0
        # Mécanique de zoom reprise de la visionneuse Structure validée :
        # l'ancre reste sous la souris et la page peut dépasser B sans être réajustée.
        self._gabarit_zoom_anchor = None
        self._gabarit_zoom_ratio = (0.5, 0.5)
        self._gabarit_page_box: tuple[float, float, float, float] | None = None
        self._gabarit_hitboxes: dict[str, tuple[float, float, float, float]] = {}
        self._gabarit_context_hitboxes: dict[int, tuple[float, float, float, float]] = {}
        self._gabarit_drag_origin: tuple[float, float] | None = None
        self._gabarit_pan_origin: tuple[float, float] | None = None
        self._gabarit_scope = "page"
        self._gabarit_zone_hitboxes: dict[str, tuple[float, float, float, float]] = {}
        self._gabarit_zone_handle_hitboxes: dict[str, tuple[float, float, float, float]] = {}
        self._gabarit_selected_zone_id: str = ""
        self._gabarit_snap_enabled: bool = True
        self._gabarit_zone_drag: dict | None = None

        # Visionneuse globale Gabarits : reprise du comportement historique de
        # Structure. Le zoom n'est plus enfermé dans B : dès qu'on zoome, la
        # page passe sur une couche soeur couvrant l'espace de travail.
        self._gabarit_overlay_active = False
        self._gabarit_overlay_zoom = 100
        self._gabarit_overlay_pan_x = 0.0
        self._gabarit_overlay_pan_y = 0.0
        self._gabarit_overlay_page_box = None
        self._gabarit_overlay_drag_origin = None
        self._gabarit_overlay_pan_origin = None
        self._gabarit_overlay_render_job = None

        # Etat visuel des commandes de navigation autour de la page.
        # Comme les autres boutons TomeLinea : survol visible + pression avec léger relief.
        self._gabarit_hover_control: str = ""
        self._gabarit_pressed_control: str = ""
        self._structure_pending_kind = None
        self._structure_pending_payload = None
        self._structure_hover_target = None
        # Bande verticale réellement cliquable pour le dépôt de pages dans B.
        # Un clic ailleurs dans B désarme le dépôt multiple au lieu d'ajouter
        # accidentellement une page sur la cible horizontale la plus proche.
        self._structure_page_line_bounds = None
        self._structure_selection_kind = "page"
        # V10 — action → cible dans B → confirmation locale dans le bandeau.
        self._structure_action_mode = None
        self._structure_action_target_kind = None
        self._structure_action_target_id = None
        self._structure_action_target_ids: list[str] = []
        # Recto/Verso : la sélection d’une page arme le choix en deux clics.
        self._structure_recto_verso_armed = False
        # Règle actuellement ciblée par la zone d’actions commune du bandeau.
        # Valeurs : AV, AP, R, V, 2P.
        self._structure_rule_target: str = ""
        # 2P manuel : deux pages existantes peuvent être soudées en une double page.
        # Le premier clic arme l'action, le second la confirme.
        self._structure_double_pair_pending: dict | None = None
        # Règles structurelles : la synchronisation est globale afin qu'une seule
        # page automatique puisse satisfaire plusieurs contraintes compatibles.
        self._structure_rule_sync_in_progress = False

        # Historique Structure : un état correspond à une décision utilisateur complète.
        # Les recalculs automatiques AV/AP/R/V/2P restent intégrés à cette même étape.
        self._history_undo: list[dict] = []
        self._history_redo: list[dict] = []
        self._history_current: dict | None = None
        self._history_replaying = False
        self._history_limit = 100

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_toolbar()
        self._build_canvas()
        try:
            top = self.winfo_toplevel()
            top.bind("<Button-1>", self._structure_global_click, add="+")
            top.bind("<Escape>", self._structure_escape, add="+")
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Historique Structure — Annuler / Rétablir
    # ------------------------------------------------------------------

    @staticmethod
    def _history_compare_data(data: dict | None) -> dict:
        comparable = deepcopy(data) if isinstance(data, dict) else {}
        # updated_at change à chaque écriture et ne constitue pas une action.
        comparable.pop("updated_at", None)
        return comparable

    def _history_notify(self) -> None:
        callback = getattr(self, "on_history_change", None)
        if callback is not None:
            try:
                callback(bool(self._history_undo), bool(self._history_redo))
            except Exception:
                pass

    def _history_reset(self, data: dict | None) -> None:
        self._history_undo.clear()
        self._history_redo.clear()
        self._history_current = deepcopy(data) if isinstance(data, dict) else {}
        self._history_notify()

    def _history_record_saved(self, data: dict | None) -> None:
        snapshot = deepcopy(data) if isinstance(data, dict) else {}
        if self._history_replaying:
            self._history_current = snapshot
            self._history_notify()
            return
        if self._history_current is None:
            self._history_current = snapshot
            self._history_notify()
            return
        if self._history_compare_data(snapshot) == self._history_compare_data(self._history_current):
            self._history_current = snapshot
            self._history_notify()
            return
        self._history_undo.append(deepcopy(self._history_current))
        if len(self._history_undo) > self._history_limit:
            del self._history_undo[:-self._history_limit]
        self._history_redo.clear()
        self._history_current = snapshot
        self._history_notify()

    def can_undo(self) -> bool:
        return bool(self._history_undo)

    def can_redo(self) -> bool:
        return bool(self._history_redo)

    def _history_restore(self, data: dict, *, status: str) -> bool:
        if self.project is None or not isinstance(data, dict):
            return False

        # Ferme proprement les éventuels éditeurs avant de restaurer le modèle.
        if getattr(self, "_title_editor", None) is not None:
            self._close_title_editor(commit=False)
        if getattr(self, "_page_name_editor", None) is not None:
            self._close_page_name_editor(commit=False)

        selection_snapshot = self._structure_selection_snapshot()
        self._history_replaying = True
        try:
            saved = self.project.save_mockup(deepcopy(data))
            if not isinstance(saved, dict):
                saved = deepcopy(data)
            saved, _changed = self._ensure_minimum_structure(saved)
            self._data = deepcopy(saved)
            self.groups = [dict(group) for group in saved.get("groups", []) if isinstance(group, dict)]
            self.items = [dict(item) for item in saved.get("items", []) if isinstance(item, dict)]

            # L'état historique contient déjà les pages automatiques calculées.
            # Undo reste une seule décision, jamais une série de micro-actions.
            self._history_current = deepcopy(saved)
            self._structure_restore_selection_snapshot(selection_snapshot)

            self.render()
            self.status_var.set(status)
            try:
                self.event_generate("<<StructurePaletteChanged>>", when="tail")
            except Exception:
                pass
            if self.on_change is not None:
                self.on_change()
            return True
        finally:
            self._history_replaying = False
            self._history_notify()

    def structure_undo(self) -> bool:
        if not self._history_undo:
            self.status_var.set("Rien à annuler.")
            self._history_notify()
            return False
        current = deepcopy(self._history_current) if isinstance(self._history_current, dict) else {}
        target = self._history_undo.pop()
        self._history_redo.append(current)
        if not self._history_restore(target, status="Action annulée."):
            self._history_undo.append(target)
            self._history_redo.pop()
            self._history_notify()
            return False
        return True

    def structure_redo(self) -> bool:
        if not self._history_redo:
            self.status_var.set("Rien à rétablir.")
            self._history_notify()
            return False
        current = deepcopy(self._history_current) if isinstance(self._history_current, dict) else {}
        target = self._history_redo.pop()
        self._history_undo.append(current)
        if len(self._history_undo) > self._history_limit:
            del self._history_undo[:-self._history_limit]
        if not self._history_restore(target, status="Action rétablie."):
            self._history_redo.append(target)
            self._history_undo.pop()
            self._history_notify()
            return False
        return True

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build_toolbar(self):
        bar = tk.Frame(self, bg=theme.PANEL)
        bar.grid(row=0, column=0, sticky="ew", pady=(0, 7))
        bar.grid_columnconfigure(1, weight=1)

        tk.Label(
            bar,
            textvariable=self.work_title_var,
            bg=theme.PANEL,
            fg=theme.INK,
            font=(theme.FONT_TITLE, 13, "bold"),
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            bar,
            textvariable=self.status_var,
            bg=theme.PANEL,
            fg=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 8, "bold"),
        ).grid(row=0, column=1, sticky="w", padx=(16, 12))

        # Les commandes de zoom sont volontairement regroupées avec la
        # navigation horizontale, au bas de B. La main reste ainsi dans la
        # même zone pour naviguer, sélectionner, renommer et zoomer.

    def _tool_button(self, parent, text, command, width=None):
        return tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            bg=theme.PANEL_SOFT,
            fg=theme.INK,
            activebackground=theme.ACCENT_SOFT,
            activeforeground=theme.WHITE,
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
            font=(theme.FONT_UI, 8, "bold"),
            cursor="hand2",
        )

    def _structure_bar_button(self, parent, text, command, *, danger=False):
        """Commande Structure : même mécanisme de survol que les tk.Button de TomeLinea."""
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg="#162A38",
            fg="#F2F3F1",
            activebackground="#203B4B",
            activeforeground="#F2F3F1",
            relief="flat",
            bd=0,
            padx=10,
            pady=3,
            font=(theme.FONT_UI, 9, "bold"),
            cursor="hand2",
        )

    def _structure_page_auto_visual_step(self) -> int:
        """État visuel dérivé de l'état fonctionnel réel."""
        mode = getattr(self, "_structure_page_auto_mode", None)
        if isinstance(mode, dict):
            return 2
        indices = self._selected_source_indices()
        if len(indices) == 1:
            try:
                if self.structure_auto_source_allowed(self.items[indices[0]]):
                    return 1
            except Exception:
                pass
        return 0

    def _structure_update_page_auto_visuals(self) -> None:
        """Guide visuellement les 3 clics sans modifier le moteur Page auto."""
        step = self._structure_page_auto_visual_step()
        panel = getattr(self, "structure_auto_panel", None)
        before = getattr(self, "structure_auto_before_btn", None)
        after = getattr(self, "structure_auto_after_btn", None)

        if panel is not None:
            try:
                panel.configure(
                    highlightthickness=2 if step == 1 else 1,
                    highlightbackground="#E7C37A" if step == 1 else "#385264",
                )
            except Exception:
                pass

        normal = {
            "bg": "#162A38",
            "fg": "#F2F3F1",
            "activebackground": "#203B4B",
            "activeforeground": "#F2F3F1",
            "relief": "flat",
            "bd": 0,
        }
        for button in (before, after):
            if button is not None:
                try:
                    button.configure(**normal)
                except Exception:
                    pass

        mode = getattr(self, "_structure_page_auto_mode", None)
        if step == 2 and isinstance(mode, dict):
            chosen = before if str(mode.get("position") or "") == "before" else after
            if chosen is not None:
                try:
                    chosen.configure(
                        bg="#C39A4A",
                        fg="#102633",
                        activebackground="#D8B66B",
                        activeforeground="#102633",
                        relief="sunken",
                        bd=1,
                    )
                except Exception:
                    pass
        try:
            self._structure_refresh_page_auto_buttons()
        except Exception:
            pass

    def _source_index_for_index(self, index: int | None) -> int | None:
        if index is None or not 0 <= int(index) < len(self.items):
            return None
        index = int(index)
        item = self.items[index]
        if not self._is_automatic_page(item):
            return index
        source_ids = self._automatic_source_ids(item)
        if not source_ids:
            return index
        # Une auto partagée n'appartient visuellement à aucune source : choisit
        # la source la plus proche uniquement pour permettre une sélection utile.
        candidates = [
            (abs(i-index), i) for i, candidate in enumerate(self.items)
            if str(candidate.get("id") or "") in source_ids
        ]
        return min(candidates)[1] if candidates else index

    def _set_single_page_selection(self, index: int | None) -> None:
        self._structure_double_pair_pending = None
        source_index = self._source_index_for_index(index)
        if source_index is None:
            self._selected_index = None
            self._selected_page_ids.clear()
            self._structure_rule_target = ""
            return
        previous_id = ""
        if self._selected_index is not None and 0 <= int(self._selected_index) < len(self.items):
            previous_id = str(self.items[int(self._selected_index)].get("id") or "")
        new_id = str(self.items[source_index].get("id") or "")
        if previous_id and new_id != previous_id:
            self._structure_rule_target = ""
        self._selected_index = source_index
        source = self.items[source_index]
        source_id = str(source.get("id") or "").strip()
        self._selected_page_ids = {source_id} if source_id else set()
        self._selected_group_id = self._item_group_id(source)
        self._structure_selection_kind = "page"
        self._structure_recto_verso_armed = self.structure_recto_verso_source_allowed(source)

    def _set_multi_page_selection(self, indices) -> None:
        self._structure_double_pair_pending = None
        self._structure_rule_target = ""
        ordered: list[int] = []
        seen: set[int] = set()
        for raw in indices or []:
            source_index = self._source_index_for_index(raw)
            if source_index is None or source_index in seen:
                continue
            seen.add(source_index)
            ordered.append(source_index)
        ordered.sort()
        if not ordered:
            self._selected_index = None
            self._selected_page_ids.clear()
            self._selected_group_id = None
            self._structure_selection_kind = "page"
            self._structure_recto_verso_armed = False
            return
        ids = {
            str(self.items[index].get("id") or "").strip()
            for index in ordered
            if str(self.items[index].get("id") or "").strip()
        }
        self._selected_page_ids = ids
        self._selected_index = ordered[0]
        self._selected_group_id = self._item_group_id(self.items[ordered[0]])
        self._structure_selection_kind = "page"
        self._structure_recto_verso_armed = (
            len(ordered) == 1 and self.structure_recto_verso_source_allowed(self.items[ordered[0]])
        )

    def _selected_source_indices(self) -> list[int]:
        """Pages principales actuellement sélectionnées, dans l'ordre du livre."""
        if str(getattr(self, "_structure_selection_kind", "") or "") != "page":
            return []
        ids = {str(value or "").strip() for value in getattr(self, "_selected_page_ids", set()) if str(value or "").strip()}
        if not ids and self._selected_index is not None:
            source_index = self._source_index_for_index(self._selected_index)
            if source_index is not None:
                source_id = str(self.items[source_index].get("id") or "").strip()
                if source_id:
                    ids.add(source_id)
        result: list[int] = []
        for index, item in enumerate(self.items):
            if self._is_automatic_page(item):
                continue
            if str(item.get("id") or "").strip() in ids:
                result.append(index)
        if not result and self._selected_index is not None:
            source_index = self._source_index_for_index(self._selected_index)
            if source_index is not None and not self._is_automatic_page(self.items[source_index]):
                result = [source_index]
        return result

    def _is_page_index_selected(self, index: int) -> bool:
        if str(getattr(self, "_structure_selection_kind", "") or "") != "page":
            return False
        source_index = self._source_index_for_index(index)
        if source_index is None:
            return False
        source_id = str(self.items[source_index].get("id") or "").strip()
        selected_ids = getattr(self, "_selected_page_ids", set())
        if selected_ids:
            return source_id in selected_ids
        return source_index == self._selected_index

    def _selected_pages_label(self) -> str:
        count = len(self._selected_source_indices())
        if count <= 1:
            index = self._selected_source_indices()[0] if count else self._selected_index
            if index is not None and 0 <= index < len(self.items):
                return self._page_display_name(self.items[index], index) or self._page_type_label(self.items[index], index)
            return "page"
        return f"{count} pages"

    def _structure_selection_snapshot(self) -> dict:
        """Capture une sélection stable à travers les recalculs qui changent les index."""
        kind = str(getattr(self, "_structure_selection_kind", "page") or "page")
        selected_ids = {
            str(value or "").strip()
            for value in getattr(self, "_selected_page_ids", set())
            if str(value or "").strip()
        }
        primary_id = ""
        index = getattr(self, "_selected_index", None)
        if index is not None:
            try:
                source_index = self._source_index_for_index(int(index))
            except Exception:
                source_index = None
            if source_index is not None and 0 <= source_index < len(self.items):
                primary_id = str(self.items[source_index].get("id") or "").strip()
                if primary_id:
                    selected_ids.add(primary_id)
        return {
            "kind": kind,
            "page_ids": set(selected_ids),
            "primary_page_id": primary_id,
            "group_id": str(getattr(self, "_selected_group_id", "") or ""),
        }


    def _structure_restore_selection_snapshot(self, snapshot: dict | None) -> None:
        """Restaure la sélection à partir des identifiants persistants des pages/parties."""
        snapshot = snapshot if isinstance(snapshot, dict) else {}
        kind = str(snapshot.get("kind") or "page")
        valid_groups = {str(group.get("id") or "") for group in self.groups if isinstance(group, dict)}

        if kind == "group":
            group_id = str(snapshot.get("group_id") or "")
            self._structure_selection_kind = "group"
            self._selected_page_ids.clear()
            self._selected_index = None
            self._selected_group_id = group_id if group_id in valid_groups else None
            self._structure_recto_verso_armed = False
            return

        requested = {
            str(value or "").strip()
            for value in snapshot.get("page_ids", set())
            if str(value or "").strip()
        }
        primary_id = str(snapshot.get("primary_page_id") or "").strip()
        source_by_id = {
            str(item.get("id") or "").strip(): index
            for index, item in enumerate(self.items)
            if not self._is_automatic_page(item) and str(item.get("id") or "").strip()
        }
        kept = {page_id for page_id in requested if page_id in source_by_id}
        if primary_id and primary_id in source_by_id:
            kept.add(primary_id)

        self._structure_selection_kind = "page"
        self._selected_page_ids = kept
        if not kept:
            self._selected_index = None
            self._selected_group_id = None
            self._structure_recto_verso_armed = False
            return

        if primary_id not in kept:
            primary_id = min(kept, key=lambda page_id: source_by_id[page_id])
        self._selected_index = source_by_id[primary_id]
        source = self.items[self._selected_index]
        self._selected_group_id = self._item_group_id(source)
        self._structure_recto_verso_armed = (
            len(kept) == 1 and self.structure_recto_verso_source_allowed(source)
        )

    def _structure_new_part_command(self):
        self.structure_cancel_page_auto_mode(silent=True)
        self._structure_reset_action()
        self.structure_arm_tool("group", {"type": "partie", "label": "Nouvelle partie"})

    def _structure_duplicate_count(self) -> int:
        var = getattr(self, "structure_duplicate_count_var", None)
        try:
            value = int(str(var.get()).strip()) if var is not None else 1
        except (TypeError, ValueError, tk.TclError):
            value = 1
        return max(1, min(50, value))

    def _structure_duplicate_count_changed(self):
        value = self._structure_duplicate_count()
        var = getattr(self, "structure_duplicate_count_var", None)
        if var is not None:
            try:
                var.set(str(value))
            except tk.TclError:
                pass
        return value

    def _structure_action_button(self, mode: str):
        # V24 — sélection → commande → Confirmer, y compris pour plusieurs pages.
        # V24_LIGNE_STRUCTURE_IMMOBILE_CONSERVEE : aucune action ne recentre automatiquement B.
        mode = str(mode or "")
        if mode not in {"duplicate", "delete"}:
            return

        self.structure_cancel_page_auto_mode(silent=True)

        if self._structure_action_mode == mode and self._structure_action_target_kind:
            self._structure_execute_action()
            return

        self.structure_cancel_tool()
        self._structure_reset_action()

        kind = str(getattr(self, "_structure_selection_kind", "") or "")
        if kind == "page":
            indices = self._selected_source_indices()
            if not indices:
                self.status_var.set("Sélectionnez d'abord une ou plusieurs pages dans B.")
                return
            ids = [str(self.items[index].get("id") or "").strip() for index in indices]
            ids = [value for value in ids if value]
            if not ids:
                return
            self._structure_action_target_kind = "pages"
            self._structure_action_target_ids = ids
            self._structure_action_target_id = ids[0]
        elif kind == "group":
            group_id = str(self._selected_group_id or "")
            if not group_id or not any(str(g.get("id") or "") == group_id for g in self.groups):
                self.status_var.set("Sélectionnez d'abord une partie dans B.")
                return
            self._structure_action_target_kind = "group"
            self._structure_action_target_id = group_id
            self._structure_action_target_ids = []
        else:
            self.status_var.set("Sélectionnez d'abord une page ou une partie dans B.")
            return

        self._structure_action_mode = mode
        self._structure_update_action_buttons()
        verb = "Dupliquer" if mode == "duplicate" else "Supprimer"
        self.status_var.set(
            f"{verb}  •  {self._structure_action_target_label()}  •  cliquez sur Confirmer"
        )

    def _structure_reset_action(self):
        self._structure_action_mode = None
        self._structure_action_target_kind = None
        self._structure_action_target_id = None
        self._structure_action_target_ids = []
        self._structure_update_action_buttons()

    def _structure_update_action_buttons(self):
        duplicate = getattr(self, "structure_duplicate_btn", None)
        delete = getattr(self, "structure_delete_btn", None)
        mode = getattr(self, "_structure_action_mode", None)
        target = getattr(self, "_structure_action_target_kind", None)
        if duplicate is not None and duplicate.winfo_exists():
            duplicate.configure(
                text="Confirmer" if mode == "duplicate" and target else "Dupliquer",
                bg="#244354" if mode == "duplicate" else "#162A38",
                fg="#F2F3F1",
            )
        if delete is not None and delete.winfo_exists():
            delete.configure(
                text="Confirmer" if mode == "delete" and target else "Supprimer",
                bg="#4A2C2A" if mode == "delete" else "#162A38",
                fg="#F2F3F1",
            )

    def _structure_action_target_label(self) -> str:
        kind = self._structure_action_target_kind
        target_id = str(self._structure_action_target_id or "")
        if kind == "pages":
            ids = [str(value or "").strip() for value in getattr(self, "_structure_action_target_ids", []) if str(value or "").strip()]
            if len(ids) > 1:
                return f"{len(ids)} pages"
            if ids:
                target_id = ids[0]
            for index, item in enumerate(self.items):
                if str(item.get("id") or "") == target_id:
                    return self._page_display_name(item, index) or self._page_type_label(item, index)
        if kind == "page":
            for index, item in enumerate(self.items):
                if str(item.get("id") or "") == target_id:
                    return self._page_display_name(item, index) or self._page_type_label(item, index)
        if kind == "group":
            group = next((g for g in self.groups if str(g.get("id") or "") == target_id), None)
            if group is not None:
                title = self._group_part_title(group)
                return title if title and title != "Titre à définir" else self._group_name(group)
        return "élément"

    def _structure_pick_action_target(self, event):
        mode = getattr(self, "_structure_action_mode", None)
        if mode not in {"duplicate", "delete"}:
            return None
        index = self._index_at(event)
        group_id = None if index is not None else self._group_at(event)
        if index is None and group_id is None:
            self._structure_reset_action()
            self.status_var.set("Action annulée")
            return "break"
        if index is not None:
            item = self.items[index]
            self._structure_selection_kind = "page"
            self._selected_index = index
            self._selected_group_id = self._item_group_id(item)
            self._structure_action_target_kind = "page"
            self._structure_action_target_id = str(item.get("id") or "")
        else:
            self._structure_selection_kind = "group"
            self._selected_group_id = str(group_id)
            self._structure_action_target_kind = "group"
            self._structure_action_target_id = str(group_id)
        self.render()
        self._structure_update_action_buttons()
        verb = "Dupliquer" if mode == "duplicate" else "Supprimer"
        self.status_var.set(f"{verb}  •  {self._structure_action_target_label()}  •  cliquez sur Confirmer")
        return "break"

    def _structure_restore_action_selection(self) -> bool:
        kind = self._structure_action_target_kind
        target_id = str(self._structure_action_target_id or "")
        if kind == "pages":
            ids = [str(value or "").strip() for value in getattr(self, "_structure_action_target_ids", []) if str(value or "").strip()]
            indices = [
                index for index, item in enumerate(self.items)
                if not self._is_automatic_page(item) and str(item.get("id") or "").strip() in ids
            ]
            if not indices:
                return False
            self._set_multi_page_selection(indices)
            return True
        if kind == "page":
            for index, item in enumerate(self.items):
                if str(item.get("id") or "") == target_id:
                    self._set_single_page_selection(index)
                    return True
            return False
        if kind == "group":
            if any(str(g.get("id") or "") == target_id for g in self.groups):
                self._selected_group_id = target_id
                self._selected_page_ids.clear()
                self._structure_selection_kind = "group"
                return True
        return False

    def _structure_execute_action(self):
        mode = self._structure_action_mode
        label = self._structure_action_target_label()
        if not self._structure_restore_action_selection():
            self._structure_reset_action()
            self.status_var.set("La cible n’est plus disponible.")
            return
        ok = False
        if mode == "duplicate":
            ok = self.structure_duplicate_selected(self._structure_duplicate_count())
        elif mode == "delete":
            ok = self.structure_delete_selected()
        self._structure_reset_action()
        if ok:
            verb = "Dupliqué" if mode == "duplicate" else "Supprimé"
            self.status_var.set(f"{verb}  •  {label}")

    def _build_canvas(self):
        viewer = tk.Frame(self, bg=theme.WINDOW_DEEP)
        viewer.grid(row=1, column=0, sticky="nsew")
        viewer.grid_rowconfigure(0, weight=1)
        viewer.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            viewer,
            bg=theme.WINDOW_DEEP,
            bd=0,
            highlightthickness=0,
            cursor="arrow",
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas._tl_item_hover_only = True

        self.v_scroll = TLScrollbar(viewer, orient="vertical", command=self.canvas.yview)
        self.v_scroll.grid(row=0, column=1, sticky="ns")

        # Gabarits — zoom local à B. De vrais widgets Tk sont utilisés ici :
        # un clic sur +/− agit immédiatement, sans hitbox dessinée ni surcouche.
        self.gabarit_zoom_controls = tk.Frame(
            viewer, bg=theme.WINDOW_DEEP, bd=0, highlightthickness=0,
        )

        def _gabarit_zoom_button(text, command, *, width=5):
            return tk.Button(
                self.gabarit_zoom_controls, text=text, command=command,
                width=width, bg="#20313B", fg="#B8CFD1",
                activebackground="#314752", activeforeground="#FFFFFF",
                relief="flat", bd=0, highlightthickness=1,
                highlightbackground="#3D515B", highlightcolor="#78AFA6",
                padx=2, pady=2, font=(theme.FONT_UI, 8, "bold"),
                cursor="hand2", takefocus=False,
            )

        self.gabarit_zoom_plus_btn = _gabarit_zoom_button("+", self.gabarit_zoom_in)
        self.gabarit_zoom_plus_btn.pack(fill="x")
        self.gabarit_zoom_label = tk.Label(
            self.gabarit_zoom_controls, textvariable=self._gabarit_zoom_text_var,
            width=7, anchor="center", bg=theme.WINDOW_DEEP, fg="#8FB4B4",
            font=(theme.FONT_UI, 7, "bold"),
        )
        self.gabarit_zoom_label.pack(fill="x", pady=(2, 2))
        self.gabarit_zoom_minus_btn = _gabarit_zoom_button("−", self.gabarit_zoom_out)
        self.gabarit_zoom_minus_btn.pack(fill="x")
        self.gabarit_zoom_fit_btn = _gabarit_zoom_button("Adapter", self.gabarit_reset_zoom, width=7)
        self.gabarit_zoom_fit_btn.pack(fill="x", pady=(4, 0))
        self.gabarit_zoom_controls.place_forget()

        # Visionneuse globale : la ligne de B reste parfaitement immobile,
        # mais la page est rendue sur une couche soeur des écrans TomeLinea.
        # Elle peut donc exploiter presque toute la fenêtre sans créer de
        # nouvelle fenêtre Windows.
        root = self.winfo_toplevel()
        self._overlay_host = getattr(root, "stack", root)
        self.page_overlay_frame = tk.Frame(
            self._overlay_host,
            bg=theme.WINDOW_DEEP,
            bd=0,
            highlightthickness=0,
        )
        self.page_overlay = tk.Canvas(
            self.page_overlay_frame,
            bg=theme.WINDOW_DEEP,
            bd=0,
            highlightthickness=0,
            cursor="arrow",
        )
        self.page_overlay.place(x=0, y=0, relwidth=1, relheight=1)

        # Commandes flottantes et légères de la visionneuse. Elles restent
        # au-dessus du décor, mais n'enferment pas la page dans un panneau.
        overlay_dock = tk.Frame(self.page_overlay_frame, bg=theme.WINDOW_DEEP)
        overlay_dock.place(relx=0.5, rely=1.0, y=-20, anchor="s")

        self._tool_button(overlay_dock, "Livre", self.close_page_overlay, width=5).pack(side="left", padx=(0, 8))
        self._tool_button(overlay_dock, "Page entière", self.fit_selected, width=10).pack(side="left", padx=(0, 14))
        self.overlay_zoom_nav = TLZoomNavigator(overlay_dock, command=self._overlay_zoom_navigate)
        self.overlay_zoom_nav.set_caption("Zoom page")
        self.overlay_zoom_nav.pack(side="left")
        tk.Label(overlay_dock, textvariable=self.zoom_text_var, bg=theme.WINDOW_DEEP, fg=theme.INK, font=(theme.FONT_UI, 9, "bold"), width=5).pack(side="left", padx=(8, 0))
        self._tool_button(overlay_dock, "Fermer", self.close_page_overlay, width=6).pack(side="left", padx=(14, 0))

        self.page_overlay.bind("<Configure>", self._schedule_overlay_render)
        self.page_overlay.bind("<ButtonPress-1>", self._overlay_press)
        self.page_overlay.bind("<B1-Motion>", self._overlay_drag)
        self.page_overlay.bind("<ButtonRelease-1>", self._overlay_release)
        self.page_overlay.bind("<Double-Button-1>", lambda _e: self.close_page_overlay())
        self.page_overlay.bind("<MouseWheel>", self._overlay_mousewheel)
        self.page_overlay.bind("<Motion>", self._overlay_motion)
        self.page_overlay.bind("<Escape>", lambda _e: self.close_page_overlay())
        self.page_overlay_frame.place_forget()

        # Visionneuse globale dédiée à Gabarits. Elle reprend le principe de
        # l'ancienne visionneuse Structure : la page sort de B sans nouvelle
        # fenêtre Windows, avec zoom ancré sous la souris et déplacement libre.
        self.gabarit_overlay_frame = tk.Frame(
            self._overlay_host, bg=theme.WINDOW_DEEP, bd=0, highlightthickness=0,
        )
        self.gabarit_overlay = tk.Canvas(
            self.gabarit_overlay_frame, bg=theme.WINDOW_DEEP, bd=0,
            highlightthickness=0, cursor="arrow",
        )
        self.gabarit_overlay.place(x=0, y=0, relwidth=1, relheight=1)

        gabarit_overlay_dock = tk.Frame(self.gabarit_overlay_frame, bg=theme.WINDOW_DEEP)
        gabarit_overlay_dock.place(relx=0.5, rely=1.0, y=-18, anchor="s")
        self._tool_button(
            gabarit_overlay_dock, "Retour", self.close_gabarit_overlay, width=6
        ).pack(side="left", padx=(0, 10))
        self.gabarit_overlay_zoom_nav = TLZoomNavigator(
            gabarit_overlay_dock, command=self._gabarit_overlay_zoom_navigate,
        )
        self.gabarit_overlay_zoom_nav.set_caption("Zoom")
        self.gabarit_overlay_zoom_nav.pack(side="left")
        self.gabarit_overlay_zoom_label = tk.Label(
            gabarit_overlay_dock, textvariable=self._gabarit_zoom_text_var,
            width=6, anchor="w", bg=theme.WINDOW_DEEP, fg=theme.INK,
            font=(theme.FONT_UI, 8, "bold"),
        )
        self.gabarit_overlay_zoom_label.pack(side="left", padx=(8, 8))
        self._tool_button(
            gabarit_overlay_dock, "Adapter", self.gabarit_reset_zoom, width=7
        ).pack(side="left")

        self.gabarit_overlay.bind("<Configure>", self._schedule_gabarit_overlay_render)
        self.gabarit_overlay.bind("<MouseWheel>", self._gabarit_overlay_mousewheel)
        self.gabarit_overlay.bind("<ButtonPress-1>", self._gabarit_overlay_press)
        self.gabarit_overlay.bind("<B1-Motion>", self._gabarit_overlay_drag)
        self.gabarit_overlay.bind("<ButtonRelease-1>", self._gabarit_overlay_release)
        self.gabarit_overlay.bind("<Escape>", lambda _e: self.close_gabarit_overlay())
        self.gabarit_overlay_frame.place_forget()

        # Dock inférieur de B : navigation au-dessus, bandeau de commandes en dessous.
        # Le bandeau reste proche du bas avec une petite respiration.
        self.structure_bottom_controls = tk.Frame(viewer, bg=theme.WINDOW_DEEP)
        self.structure_bottom_controls.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        self.structure_bottom_controls.grid_columnconfigure(0, weight=1)

        # V23 : un seul ruban Structure centré. Page auto est lié directement
        # à la page sélectionnée ; les commandes d'édition restent à droite.
        self.structure_command_bar = tk.Frame(
            self.structure_bottom_controls, bg="#102633",
            highlightthickness=1, highlightbackground="#C39A4A",
            padx=8, pady=4,
        )
        # Le bandeau est la dernière ligne du dock inférieur.
        self.structure_command_bar.grid(row=1, column=0, pady=(2, 2))

        # Groupe édition à gauche : Partie / Dupliquer / quantité / Supprimer.
        self.structure_new_part_btn = self._structure_bar_button(
            self.structure_command_bar, "+ Partie", self._structure_new_part_command
        )
        self.structure_new_part_btn.pack(side="left", padx=3, pady=1)

        self.structure_duplicate_btn = self._structure_bar_button(
            self.structure_command_bar, "Dupliquer", lambda: self._structure_action_button("duplicate")
        )
        self.structure_duplicate_btn.pack(side="left", padx=(3, 1), pady=1)

        tk.Label(
            self.structure_command_bar, text="×",
            bg="#102633", fg="#B7C2C8",
            font=(theme.FONT_UI, 9, "bold"),
        ).pack(side="left", padx=(2, 1))
        self.structure_duplicate_count_var = tk.StringVar(value="1")
        self.structure_duplicate_count_spin = tk.Spinbox(
            self.structure_command_bar,
            from_=1, to=50, increment=1,
            textvariable=self.structure_duplicate_count_var,
            width=3, justify="center",
            bg="#162A38", fg="#F2F3F1",
            buttonbackground="#244354",
            insertbackground="#F2F3F1",
            relief="groove", bd=1,
            highlightthickness=0,
            font=(theme.FONT_UI, 8, "bold"),
            command=self._structure_duplicate_count_changed,
        )
        self.structure_duplicate_count_spin.pack(side="left", padx=(0, 4), pady=1)
        self.structure_duplicate_count_spin.bind("<FocusOut>", lambda _e: self._structure_duplicate_count_changed(), add="+")
        self.structure_duplicate_count_spin.bind("<Return>", lambda _e: self._structure_duplicate_count_changed(), add="+")

        self.structure_delete_btn = self._structure_bar_button(
            self.structure_command_bar, "Supprimer", lambda: self._structure_action_button("delete"), danger=True
        )
        self.structure_delete_btn.pack(side="left", padx=3, pady=1)

        separator = tk.Frame(self.structure_command_bar, bg="#5D6D76", width=1, height=22)
        separator.pack(side="left", padx=10, pady=3)
        separator.pack_propagate(False)

        # Page auto.
        self.structure_auto_panel = tk.Frame(
            self.structure_command_bar,
            bg="#102633",
            highlightthickness=1,
            highlightbackground="#385264",
            padx=3,
            pady=1,
        )
        self.structure_auto_panel.pack(side="left", padx=(0, 2), pady=0)
        tk.Label(
            self.structure_auto_panel, text="Page auto :",
            bg="#102633", fg="#D7C08A",
            font=(theme.FONT_UI, 8, "bold"),
        ).pack(side="left", padx=(3, 5))
        self.structure_auto_before_btn = self._structure_bar_button(
            self.structure_auto_panel, "AV",
            lambda: self.structure_select_page_auto_rule("before"),
        )
        self.structure_auto_before_btn.configure(width=4)
        self.structure_auto_before_btn.pack(side="left", padx=2, pady=1)
        self.structure_auto_after_btn = self._structure_bar_button(
            self.structure_auto_panel, "AP",
            lambda: self.structure_select_page_auto_rule("after"),
        )
        self.structure_auto_after_btn.configure(width=4)
        self.structure_auto_after_btn.pack(side="left", padx=2, pady=1)

        action_separator = tk.Frame(self.structure_command_bar, bg="#5D6D76", width=1, height=22)
        action_separator.pack(side="left", padx=10, pady=3)
        action_separator.pack_propagate(False)

        # Actions communes à la règle ciblée.
        self.structure_rule_action_panel = tk.Frame(
            self.structure_command_bar,
            bg="#102633",
            highlightthickness=1,
            highlightbackground="#385264",
            padx=3,
            pady=1,
        )
        self.structure_rule_action_panel.pack(side="left", padx=(0, 8), pady=0)
        tk.Label(
            self.structure_rule_action_panel, text="Règle :",
            bg="#102633", fg="#B7C2C8",
            font=(theme.FONT_UI, 8, "bold"),
        ).pack(side="left", padx=(3, 4))
        self.structure_rule_target_badge = tk.Label(
            self.structure_rule_action_panel,
            text="—", width=3,
            bg="#162A38", fg="#D7C08A",
            relief="groove", bd=1,
            font=(theme.FONT_UI, 8, "bold"),
        )
        self.structure_rule_target_badge.pack(side="left", padx=(0, 5), pady=1)
        self.structure_rule_exception_btn = self._structure_bar_button(
            self.structure_rule_action_panel, "Exception", self.structure_toggle_target_rule_exception,
        )
        self.structure_rule_exception_btn.configure(width=10, state="disabled")
        self.structure_rule_exception_btn.pack(side="left", padx=2, pady=1)
        self.structure_rule_remove_btn = self._structure_bar_button(
            self.structure_rule_action_panel, "Retirer règle", self.structure_remove_target_rule,
        )
        self.structure_rule_remove_btn.configure(width=12, state="disabled")
        self.structure_rule_remove_btn.pack(side="left", padx=2, pady=1)

        side_separator = tk.Frame(self.structure_command_bar, bg="#5D6D76", width=1, height=22)
        side_separator.pack(side="left", padx=10, pady=3)
        side_separator.pack_propagate(False)

        # Position : Recto / Verso / Double page.
        self.structure_recto_verso_panel = tk.Frame(
            self.structure_command_bar,
            bg="#102633",
            highlightthickness=1,
            highlightbackground="#385264",
            padx=3,
            pady=1,
        )
        self.structure_recto_verso_panel.pack(side="left", padx=(2, 0), pady=0)
        tk.Label(
            self.structure_recto_verso_panel, text="Position :",
            bg="#102633", fg="#D7C08A",
            font=(theme.FONT_UI, 8, "bold"),
        ).pack(side="left", padx=(3, 5))
        self.structure_recto_btn = self._structure_bar_button(
            self.structure_recto_verso_panel, "R",
            lambda: self.structure_select_recto_verso_rule("recto"),
        )
        self.structure_recto_btn.configure(width=4)
        self.structure_recto_btn.pack(side="left", padx=2, pady=1)
        self.structure_verso_btn = self._structure_bar_button(
            self.structure_recto_verso_panel, "V",
            lambda: self.structure_select_recto_verso_rule("verso"),
        )
        self.structure_verso_btn.configure(width=4)
        self.structure_verso_btn.pack(side="left", padx=2, pady=1)
        self.structure_double_page_btn = self._structure_bar_button(
            self.structure_recto_verso_panel, "2P", self.structure_select_double_page_rule,
        )
        self.structure_double_page_btn.configure(width=5)
        self.structure_double_page_btn.pack(side="left", padx=2, pady=1)

        nav_row = tk.Frame(self.structure_bottom_controls, bg=theme.WINDOW_DEEP, height=46)
        nav_row.grid(row=0, column=0, sticky="ew")
        nav_row.grid_propagate(False)

        # Le zoom Gabarits reste local à B ; Structure conserve son comportement propre.
        nav_dock = tk.Frame(nav_row, bg=theme.WINDOW_DEEP)
        nav_dock.place(relx=0.5, rely=0.5, anchor="center")

        self.h_nav = TLBookNavigator(nav_dock, command=self._navigate_horizontal)
        self.h_nav.pack(side="left")

        self.structure_auto_counter = tk.Label(
            nav_row, text="Auto : 0 / 0 pages  •  blanches : 0",
            width=42, anchor="e",
            bg=theme.WINDOW_DEEP, fg="#AEB8B5",
            font=(theme.FONT_UI, 8, "bold"),
            cursor="hand2",
        )
        self.structure_auto_counter.place(relx=0.985, rely=0.5, anchor="e")
        self.structure_auto_counter._tl_local_hover = True
        self.structure_auto_counter.bind("<Enter>", self._structure_auto_counter_enter)
        self.structure_auto_counter.bind("<Leave>", self._structure_auto_counter_leave)

        self.canvas.configure(xscrollcommand=self._on_canvas_xview, yscrollcommand=self._on_canvas_yview)

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)
        self.canvas.bind("<Control-MouseWheel>", self._on_ctrl_mousewheel)
        self.canvas.bind("<Configure>", self._schedule_render)
        self.canvas.bind("<Motion>", self._on_hover_motion)
        self.canvas.bind("<Leave>", self._on_hover_leave)

    # ------------------------------------------------------------------
    # Projet / données
    # ------------------------------------------------------------------

    def set_work_mode(self, mode: str):
        mode = str(mode or "structure")
        previous = str(getattr(self, "_work_mode", "structure") or "structure")
        self._work_mode = mode
        titles = {
            "structure": "Structure du livre",
            "gabarits": "Gabarit — page",
            "production": "Production — page",
            "sortie": "Sortie — contrôle",
        }
        self.work_title_var.set(titles.get(mode, "Livre"))

        bottom = getattr(self, "structure_bottom_controls", None)
        bar = getattr(self, "structure_command_bar", None)
        if mode == "structure":
            if bottom is not None:
                bottom.grid()
            if bar is not None:
                bar.grid()
        else:
            # Les commandes du squelette disparaissent complètement hors Structure.
            if bottom is not None:
                bottom.grid_remove()

        if mode != "structure":
            self._drag_kind = None
            self._dragging = False
            self.structure_cancel_page_auto_mode(silent=True)
            self.structure_cancel_tool()
            self._structure_reset_action()
            try:
                self._cancel_drag_autoscroll()
            except Exception:
                pass

        zoom_controls = getattr(self, "gabarit_zoom_controls", None)
        if zoom_controls is not None and mode != "gabarits":
            zoom_controls.place_forget()
        if mode != "gabarits" and getattr(self, "_gabarit_overlay_active", False):
            self.close_gabarit_overlay()

        if mode == "gabarits":
            # Première entrée : page ajustée. Revenir ensuite dans Gabarits conserve
            # le niveau de zoom de travail, exactement comme un poste de mise en page.
            if previous != "gabarits" and not hasattr(self, "_gabarit_has_been_opened"):
                self._gabarit_zoom = 100
                self._gabarit_pan_x = 0.0
                self._gabarit_pan_y = 0.0
                self._gabarit_has_been_opened = True
            if self._selected_index is None and self.items:
                self._selected_index = 0
            self._gabarit_normalize_selected_index()

        self.render()
        if mode == "gabarits":
            self._emit_gabarit_page_changed()


    # ------------------------------------------------------------------
    # Gabarits — page réelle, contexte local et zoom persistant
    # ------------------------------------------------------------------

    def _emit_gabarit_page_changed(self) -> None:
        try:
            self.event_generate("<<GabaritPageChanged>>", when="tail")
        except Exception:
            pass

    def _emit_gabarit_selection_changed(self) -> None:
        try:
            self.event_generate("<<GabaritSelectionChanged>>", when="tail")
        except Exception:
            pass


    def gabarit_selected_zone_info(self) -> dict:
        item = self._gabarit_active_item()
        zone = self._gabarit_find_zone(item, zone_id=self._gabarit_selected_zone_id) if item else None
        if not isinstance(zone, dict):
            return {}
        x = float(zone.get("x", 0.0))
        y = float(zone.get("y", 0.0))
        w = float(zone.get("w", 0.0))
        h = float(zone.get("h", 0.0))
        spread = self._gabarit_active_is_spread()
        spread_position = self._gabarit_zone_spread_position(zone) if spread else ""
        page_w_mm, page_h_mm = self._gabarit_page_mm()
        width_mm = page_w_mm * 2.0 if spread and spread_position == "center" else page_w_mm
        return {
            "id": str(zone.get("id") or ""),
            "kind": str(zone.get("kind") or "document"),
            "locked": bool(zone.get("locked", False)),
            "occupation": str(zone.get("occupation") or "free"),
            "spread": spread,
            "spread_position": spread_position,
            "rect_mm": {
                "x": round(x * width_mm, 2),
                "y": round(y * page_h_mm, 2),
                "w": round(w * width_mm, 2),
                "h": round(h * page_h_mm, 2),
            },
        }

    def gabarit_toggle_snap(self) -> bool:
        self._gabarit_snap_enabled = not bool(getattr(self, "_gabarit_snap_enabled", True))
        self.status_var.set("Accrochage activé" if self._gabarit_snap_enabled else "Accrochage désactivé")
        self._emit_gabarit_selection_changed()
        return self._gabarit_snap_enabled

    def gabarit_snap_enabled(self) -> bool:
        return bool(getattr(self, "_gabarit_snap_enabled", True))


    def gabarit_snap_profile(self) -> dict:
        raw = getattr(self, "_gabarit_snap_profile", None)
        if not isinstance(raw, dict):
            raw = {
                "reference": "page",
                "anchors": ["left", "right", "top", "bottom", "hcenter", "vcenter"],
            }
            self._gabarit_snap_profile = raw
        return {
            "reference": str(raw.get("reference") or "page"),
            "anchors": list(raw.get("anchors") or ()),
        }

    def gabarit_set_snap_profile(self, reference: str, anchors) -> bool:
        reference = "margins" if str(reference or "").strip().lower() == "margins" else "page"
        allowed = {"left", "right", "top", "bottom", "hcenter", "vcenter", "both_centers"}
        clean = []
        for value in anchors or ():
            value = str(value or "").strip().lower()
            if value in allowed and value not in clean:
                clean.append(value)
        self._gabarit_snap_profile = {"reference": reference, "anchors": clean}
        self._gabarit_snap_enabled = True
        self.status_var.set("Accrochage préparé sur les marges" if reference == "margins" else "Accrochage préparé sur la page")
        self._emit_gabarit_selection_changed()
        return True

    def gabarit_set_selected_zone_rect_mm(self, x_mm: float, y_mm: float, w_mm: float, h_mm: float) -> bool:
        active = self._gabarit_active_item()
        zone = self._gabarit_find_zone(active, zone_id=self._gabarit_selected_zone_id) if active else None
        if zone is None:
            self.status_var.set("Sélectionnez d’abord une zone dans la page.")
            return False
        if bool(zone.get("locked", False)):
            self.status_var.set("Déverrouillez la zone avant de modifier ses dimensions.")
            return False
        x_mm, y_mm, w_mm, h_mm = map(float, (x_mm, y_mm, w_mm, h_mm))
        if w_mm <= 0 or h_mm <= 0:
            return False
        spread_position = self._gabarit_zone_spread_position(zone) if self._gabarit_active_is_spread() else ""
        page_w_mm, page_h_mm = self._gabarit_page_mm()
        width_mm = page_w_mm * 2.0 if spread_position == "center" else page_w_mm
        # Une zone libre peut volontairement dépasser légèrement sa surface.
        if not (-30.0 <= x_mm <= width_mm + 30.0 and -30.0 <= y_mm <= page_h_mm + 30.0 and w_mm <= width_mm + 60.0 and h_mm <= page_h_mm + 60.0):
            return False
        zone["occupation"] = "free"
        return self._gabarit_commit_zone_rect(
            zone,
            (x_mm / width_mm, y_mm / page_h_mm, w_mm / width_mm, h_mm / page_h_mm),
            "Position et dimensions mises à jour",
        )

    def gabarit_set_selected_zone_occupation(self, mode: str) -> bool:
        active = self._gabarit_active_item()
        zone = self._gabarit_find_zone(active, zone_id=self._gabarit_selected_zone_id) if active else None
        if zone is None:
            self.status_var.set("Sélectionnez d’abord une zone dans la page.")
            return False
        if bool(zone.get("locked", False)):
            self.status_var.set("Déverrouillez la zone avant de modifier son occupation.")
            return False

        mode = str(mode or "free").strip().lower()
        if mode not in {"free", "margins", "page", "bleed"}:
            return False
        if mode == "free":
            zone["occupation"] = "free"
            self._gabarit_mark_edited(active)
            self._save_order()
            self.render()
            self._emit_gabarit_page_changed()
            self._emit_gabarit_selection_changed()
            self.status_var.set("Zone en placement libre")
            return True

        settings = self.gabarit_current_settings() or {}
        spread_position = self._gabarit_zone_spread_position(zone) if self._gabarit_active_is_spread() else ""
        page_w_mm, page_h_mm = self._gabarit_page_mm()
        width_mm = page_w_mm * 2.0 if spread_position == "center" else page_w_mm
        if mode == "margins":
            margins = dict(settings.get("margins_mm") or {})
            left = float(margins.get("inside", 15.0)) / width_mm
            right = float(margins.get("outside", 15.0)) / width_mm
            top = float(margins.get("top", 15.0)) / page_h_mm
            bottom = float(margins.get("bottom", 15.0)) / page_h_mm
            rect = (left, top, max(0.001, 1.0-left-right), max(0.001, 1.0-top-bottom))
            status = "Zone ajustée aux marges"
        elif mode == "page":
            rect = (0.0, 0.0, 1.0, 1.0)
            status = "Zone ajustée à la page"
        else:
            bleed = dict(settings.get("bleed_mm") or {})
            left = float(bleed.get("left", 3.0)) / width_mm
            right = float(bleed.get("right", 3.0)) / width_mm
            top = float(bleed.get("top", 3.0)) / page_h_mm
            bottom = float(bleed.get("bottom", 3.0)) / page_h_mm
            rect = (-left, -top, 1.0 + left + right, 1.0 + top + bottom)
            status = "Zone étendue jusqu’au fond perdu"

        # Le mode est conservé dans la zone : Production saura si le placement
        # était libre, aux marges, pleine page ou jusqu'au fond perdu.
        slot_key = str(zone.get("slot_key") or zone.get("id") or "")
        for idx in self._gabarit_zone_target_indices():
            item = self.items[idx]
            target = self._gabarit_find_zone(item, slot_key=slot_key)
            if target is None and idx == self._selected_index:
                target = self._gabarit_find_zone(item, zone_id=self._gabarit_selected_zone_id)
            if target is not None:
                target["occupation"] = mode
        changed = self._gabarit_commit_zone_rect(zone, rect, status)
        if changed:
            self._emit_gabarit_selection_changed()
        return changed

    def _gabarit_status(self, item: dict | None) -> str:
        if not isinstance(item, dict):
            return "non_commence"
        raw = str(item.get("gabarit_status") or "").strip().lower()
        if raw in {"termine", "terminé", "done", "fini"} or bool(item.get("gabarit_done")):
            return "termine"
        if raw in {"en_cours", "encours", "progress", "in_progress"}:
            return "en_cours"
        zones = item.get("gabarit_zones")
        if isinstance(zones, list) and zones:
            return "en_cours"
        if any(str(item.get(key) or "").strip() for key in ("gabarit_preview", "template_preview", "layout_preview")):
            return "en_cours"
        return "non_commence"

    def gabarit_toggle_finished(self) -> bool:
        if self._selected_index is None or not (0 <= self._selected_index < len(self.items)):
            return False
        indices = self._gabarit_active_unit_indices()
        if not indices:
            return False
        all_done = all(self._gabarit_status(self.items[index]) == "termine" for index in indices)
        for index in indices:
            item = self.items[index]
            if all_done:
                item["gabarit_status"] = "en_cours"
                item["gabarit_done"] = False
            else:
                item["gabarit_status"] = "termine"
                item["gabarit_done"] = True
        self._save_order()
        self.render()
        self._emit_gabarit_page_changed()
        self.status_var.set("Gabarit rouvert" if all_done else "Gabarit marqué terminé")
        return True

    def gabarit_set_scope(self, scope: str) -> None:
        scope = str(scope or "page").strip().lower()
        self._gabarit_scope = "type" if scope == "type" else "page"
        if getattr(self, "_work_mode", "") == "gabarits":
            self.render()

    def _gabarit_navigation_units(self) -> list[dict]:
        """Unités de navigation : une paire 2P soudée reste un seul arrêt."""
        units: list[dict] = []
        consumed: set[int] = set()
        for index, item in enumerate(self.items):
            if index in consumed:
                continue
            pair_id = self._double_page_pair_id(item) if not self._is_automatic_page(item) else ""
            indices = [index]
            if pair_id:
                members = sorted(i for i, _candidate in self._double_page_pair_members(pair_id))
                if len(members) == 2:
                    indices = members
                    consumed.update(members)
            first = indices[0]
            last = indices[-1]
            first_from, _first_to = self._structure_work_number_span(first)
            _last_from, last_to = self._structure_work_number_span(last)
            number_text = str(first_from) if first_from == last_to else f"{first_from}–{last_to}"
            labels = [self._page_type_label(self.items[i], i) for i in indices]
            label = labels[0] if len(set(labels)) == 1 else " + ".join(labels)
            units.append({
                "indices": tuple(indices),
                "primary": first,
                "label": label,
                "number": number_text,
                "automatic": all(self._is_automatic_page(self.items[i]) for i in indices),
                "double": len(indices) == 2 or self._effective_double_page_rule(self.items[first]),
            })
            consumed.update(indices)
        return units

    def _gabarit_unit_position(self, index: int | None = None) -> tuple[list[dict], int]:
        units = self._gabarit_navigation_units()
        if not units:
            return units, 0
        if index is None:
            index = self._selected_index if self._selected_index is not None else 0
        for pos, unit in enumerate(units):
            if int(index) in unit["indices"]:
                return units, pos
        return units, max(0, min(len(units) - 1, int(index)))

    def _gabarit_normalize_selected_index(self) -> None:
        if not self.items:
            self._selected_index = None
            return
        if self._selected_index is None or not (0 <= int(self._selected_index) < len(self.items)):
            self._selected_index = 0
        units, pos = self._gabarit_unit_position(self._selected_index)
        if units:
            self._selected_index = int(units[pos]["primary"])
            self._selected_group_id = self._item_group_id(self.items[self._selected_index])

    def _gabarit_active_unit_indices(self) -> list[int]:
        units, pos = self._gabarit_unit_position()
        return list(units[pos]["indices"]) if units else []

    def gabarit_navigation_data(self) -> dict:
        """Données légères pour la zone C : types présents et pages de chaque type."""
        pages = []
        type_order: list[tuple[str, str]] = []
        seen_types: set[str] = set()
        for unit in self._gabarit_navigation_units():
            index = int(unit["primary"])
            item = self.items[index]
            type_key = self._type_of(item)
            label = self._page_type_label(item, index)
            if type_key not in seen_types:
                seen_types.add(type_key)
                type_order.append((type_key, label))
            pages.append({
                "id": str(item.get("id") or ""),
                "type": type_key,
                "label": label,
                "number": unit["number"],
                "structure_index": index,
                "status": self._gabarit_status(item),
                "automatic": bool(unit["automatic"]),
                "double": bool(unit["double"]),
            })
        active_id = ""
        active_type = ""
        if self._selected_index is not None and 0 <= self._selected_index < len(self.items):
            active = self.items[self._selected_index]
            active_id = str(active.get("id") or "")
            active_type = self._type_of(active)
        return {
            "types": [{"type": key, "label": label} for key, label in type_order],
            "pages": pages,
            "active_page_id": active_id,
            "active_type": active_type,
            "project_type": self._structure_project_type(),
        }

    def gabarit_select_page_by_id(self, page_id: str) -> bool:
        page_id = str(page_id or "").strip()
        if not page_id:
            return False
        index = next((i for i, item in enumerate(self.items) if str(item.get("id") or "").strip() == page_id), None)
        if index is None:
            return False
        return self.gabarit_select_index(index)

    def gabarit_select_index(self, index: int, *, preserve_zoom: bool = True) -> bool:
        if not 0 <= int(index) < len(self.items):
            return False
        zoom = int(getattr(self, "_gabarit_zoom", 100))
        pan_x = float(getattr(self, "_gabarit_pan_x", 0.0))
        pan_y = float(getattr(self, "_gabarit_pan_y", 0.0))
        self._selected_index = int(index)
        self._gabarit_normalize_selected_index()
        if preserve_zoom:
            self._gabarit_zoom = zoom
            self._gabarit_pan_x = pan_x
            self._gabarit_pan_y = pan_y
        else:
            self._gabarit_zoom = 100
            self._gabarit_pan_x = 0.0
            self._gabarit_pan_y = 0.0
        self.render()
        self._emit_gabarit_page_changed()
        return True

    def gabarit_navigate(self, delta: int) -> bool:
        units, pos = self._gabarit_unit_position()
        if not units:
            return False
        target = pos + (-1 if int(delta) < 0 else 1)
        if target < 0 or target >= len(units):
            return False
        return self.gabarit_select_index(int(units[target]["primary"]), preserve_zoom=True)

    def _gabarit_sync_zoom_widget(self) -> None:
        """Synchronise l'affichage du zoom local de B."""
        value = max(100, min(900, int(getattr(self, "_gabarit_zoom", 100))))
        try:
            self._gabarit_zoom_text_var.set(f"{value} %")
        except Exception:
            pass

    def open_gabarit_overlay(self, *, zoom: int = 100) -> None:
        """Compatibilité V7 : aucun overlay n'est ouvert ; le zoom reste dans B."""
        self._gabarit_overlay_active = False
        self.gabarit_set_zoom(max(100, int(zoom)), anchor=self._gabarit_button_zoom_anchor())

    def close_gabarit_overlay(self) -> None:
        """Compatibilité avec les anciens appels : aucune visionneuse Gabarits séparée."""
        self._gabarit_overlay_active = False
        try:
            self.gabarit_overlay_frame.place_forget()
        except Exception:
            pass

    def _gabarit_zoom_navigate(self, velocity: float) -> None:
        """Compatibilité : transforme une commande continue en zoom local de B."""
        velocity = float(velocity)
        if abs(velocity) < 0.001:
            return
        current = int(getattr(self, "_gabarit_zoom", 100))
        base = 7 if current < 180 else (12 if current < 320 else 20)
        delta = int(round(base * velocity))
        if delta == 0:
            delta = 1 if velocity > 0 else -1
        self.gabarit_set_zoom(current + delta, anchor=self._gabarit_button_zoom_anchor())

    def _gabarit_overlay_zoom_navigate(self, velocity: float) -> None:
        velocity = float(velocity)
        if abs(velocity) < 0.001:
            return
        current = int(getattr(self, "_gabarit_overlay_zoom", 100))
        base = 8 if current < 160 else (14 if current < 300 else 24)
        delta = int(round(base * velocity))
        if delta == 0:
            delta = 1 if velocity > 0 else -1
        self._gabarit_overlay_set_zoom(current + delta)

    def gabarit_zoom_in(self) -> None:
        current = int(getattr(self, "_gabarit_zoom", 100))
        step = 12 if current < 220 else 20
        self.gabarit_set_zoom(current + step, anchor=self._gabarit_button_zoom_anchor())

    def gabarit_zoom_out(self) -> None:
        current = int(getattr(self, "_gabarit_zoom", 100))
        step = 12 if current <= 220 else 20
        self.gabarit_set_zoom(max(100, current - step), anchor=self._gabarit_button_zoom_anchor())

    def gabarit_reset_zoom(self) -> None:
        """Adapter : remet la page entière dans la surface de travail B."""
        self._gabarit_zoom = 100
        self._gabarit_pan_x = 0.0
        self._gabarit_pan_y = 0.0
        self._gabarit_zoom_anchor = None
        self._gabarit_zoom_ratio = (0.5, 0.5)
        self._gabarit_sync_zoom_widget()
        if getattr(self, "_work_mode", "") == "gabarits":
            self.render()

    def _schedule_gabarit_overlay_render(self, _event=None) -> None:
        if not getattr(self, "_gabarit_overlay_active", False):
            return
        if self._gabarit_overlay_render_job is None:
            self._gabarit_overlay_render_job = self.after(12, self._render_gabarit_overlay)

    def _gabarit_overlay_fit_scale(self) -> float:
        width = max(1.0, float(self.gabarit_overlay.winfo_width()))
        height = max(1.0, float(self.gabarit_overlay.winfo_height()) - 76.0)
        page_w_mm, page_h_mm = self._gabarit_page_mm()
        spread = self._gabarit_active_is_spread()
        total_mm_w = page_w_mm * (2.0 if spread else 1.0)
        # 12 % de respiration autour de la page, comme l'ancienne visionneuse.
        return max(0.01, min((width * 0.82) / total_mm_w, (height * 0.86) / page_h_mm))

    def _gabarit_overlay_dimensions(self, zoom: int | None = None) -> tuple[float, float, float]:
        value = int(getattr(self, "_gabarit_overlay_zoom", 100) if zoom is None else zoom)
        scale = self._gabarit_overlay_fit_scale() * max(0.45, float(value) / 100.0)
        page_w_mm, page_h_mm = self._gabarit_page_mm()
        spread = self._gabarit_active_is_spread()
        return page_w_mm * (2.0 if spread else 1.0) * scale, page_h_mm * scale, scale

    def _gabarit_overlay_clamp_pan(self) -> None:
        if not getattr(self, "_gabarit_overlay_active", False):
            return
        width = max(1.0, float(self.gabarit_overlay.winfo_width()))
        height = max(1.0, float(self.gabarit_overlay.winfo_height()) - 76.0)
        page_w, page_h, _ = self._gabarit_overlay_dimensions()
        # Une bande de page reste toujours récupérable, sans recentrage forcé.
        visible_edge = 72.0
        max_x = max(0.0, (page_w + width) / 2.0 - visible_edge)
        max_y = max(0.0, (page_h + height) / 2.0 - visible_edge)
        if page_w <= width:
            max_x = max(0.0, (width - page_w) * 0.15)
        if page_h <= height:
            max_y = max(0.0, (height - page_h) * 0.15)
        self._gabarit_overlay_pan_x = max(-max_x, min(max_x, float(self._gabarit_overlay_pan_x)))
        self._gabarit_overlay_pan_y = max(-max_y, min(max_y, float(self._gabarit_overlay_pan_y)))

    def _gabarit_overlay_set_zoom(self, value: int, *, anchor: tuple[float, float] | None = None) -> None:
        if not getattr(self, "_gabarit_overlay_active", False):
            self.open_gabarit_overlay(zoom=value)
            return
        value = max(45, min(600, int(value)))
        current = int(getattr(self, "_gabarit_overlay_zoom", 100))
        if value == current:
            return
        width = max(1.0, float(self.gabarit_overlay.winfo_width()))
        usable_h = max(1.0, float(self.gabarit_overlay.winfo_height()) - 76.0)
        old_w, old_h, _ = self._gabarit_overlay_dimensions(current)
        cx = width / 2.0 + float(self._gabarit_overlay_pan_x)
        cy = usable_h / 2.0 + float(self._gabarit_overlay_pan_y)
        if anchor is None:
            anchor = (width / 2.0, usable_h / 2.0)
        ax, ay = float(anchor[0]), float(anchor[1])
        rx = 0.5 if old_w <= 0 else (ax - (cx - old_w / 2.0)) / old_w
        ry = 0.5 if old_h <= 0 else (ay - (cy - old_h / 2.0)) / old_h
        rx = max(0.0, min(1.0, rx)); ry = max(0.0, min(1.0, ry))
        self._gabarit_overlay_zoom = value
        new_w, new_h, _ = self._gabarit_overlay_dimensions(value)
        new_cx = ax + new_w * (0.5 - rx)
        new_cy = ay + new_h * (0.5 - ry)
        self._gabarit_overlay_pan_x = new_cx - width / 2.0
        self._gabarit_overlay_pan_y = new_cy - usable_h / 2.0
        self._gabarit_overlay_clamp_pan()
        self._gabarit_sync_zoom_widget()
        self._schedule_gabarit_overlay_render()

    def _gabarit_overlay_mousewheel(self, event):
        box = getattr(self, "_gabarit_overlay_page_box", None)
        if box is None:
            return "break"
        x, y = float(event.x), float(event.y)
        if not self._gabarit_point_in(box, x, y):
            return "break"
        step = 12 if int(getattr(self, "_gabarit_overlay_zoom", 100)) < 220 else 20
        value = int(self._gabarit_overlay_zoom) + (step if event.delta > 0 else -step)
        self._gabarit_overlay_set_zoom(value, anchor=(x, y))
        return "break"

    def _gabarit_overlay_press(self, event):
        if not self._gabarit_point_in(getattr(self, "_gabarit_overlay_page_box", None), float(event.x), float(event.y)):
            return "break"
        self._gabarit_overlay_drag_origin = (float(event.x), float(event.y))
        self._gabarit_overlay_pan_origin = (float(self._gabarit_overlay_pan_x), float(self._gabarit_overlay_pan_y))
        try:
            self.gabarit_overlay.configure(cursor="fleur")
        except Exception:
            pass
        return "break"

    def _gabarit_overlay_drag(self, event):
        if self._gabarit_overlay_drag_origin is None or self._gabarit_overlay_pan_origin is None:
            return "break"
        dx = float(event.x) - self._gabarit_overlay_drag_origin[0]
        dy = float(event.y) - self._gabarit_overlay_drag_origin[1]
        self._gabarit_overlay_pan_x = self._gabarit_overlay_pan_origin[0] + dx
        self._gabarit_overlay_pan_y = self._gabarit_overlay_pan_origin[1] + dy
        self._gabarit_overlay_clamp_pan()
        self._schedule_gabarit_overlay_render()
        return "break"

    def _gabarit_overlay_release(self, _event=None):
        self._gabarit_overlay_drag_origin = None
        self._gabarit_overlay_pan_origin = None
        try:
            self.gabarit_overlay.configure(cursor="arrow")
        except Exception:
            pass
        return "break"

    def _render_gabarit_overlay(self) -> None:
        self._gabarit_overlay_render_job = None
        if not getattr(self, "_gabarit_overlay_active", False):
            return
        target = self.gabarit_overlay
        target.delete("all")
        width = max(1.0, float(target.winfo_width()))
        usable_h = max(1.0, float(target.winfo_height()) - 76.0)
        target.create_rectangle(0, 0, width, float(target.winfo_height()), fill=theme.WINDOW_DEEP, outline="")
        if not self.items:
            return
        self._gabarit_normalize_selected_index()
        units, active_pos = self._gabarit_unit_position()
        if not units:
            return
        active_unit = units[active_pos]
        active_index = int(active_unit["primary"])
        active_item = self.items[active_index]
        spread = bool(active_unit["double"])
        page_w, page_h, scale = self._gabarit_overlay_dimensions()
        self._gabarit_overlay_clamp_pan()
        cx = width / 2.0 + float(self._gabarit_overlay_pan_x)
        cy = usable_h / 2.0 + float(self._gabarit_overlay_pan_y)
        x1, y1 = cx - page_w / 2.0, cy - page_h / 2.0
        x2, y2 = x1 + page_w, y1 + page_h
        self._gabarit_overlay_page_box = (x1, y1, x2, y2)
        shadow = max(5.0, min(16.0, 7.0 * max(1.0, self._gabarit_overlay_zoom / 100.0)))
        target.create_rectangle(x1 + shadow, y1 + shadow, x2 + shadow, y2 + shadow, fill="#10161B", outline="")
        single_w = page_w / (2.0 if spread else 1.0)
        if spread:
            unit_indices = list(active_unit.get("indices", (active_index,)))
            left_item = self.items[unit_indices[0]] if unit_indices else active_item
            right_item = self.items[unit_indices[1]] if len(unit_indices) > 1 else active_item
            self._gabarit_draw_sheet_guides(target, x1, y1, single_w, page_h, item=left_item, fold_side="right")
            self._gabarit_draw_sheet_guides(target, x1 + single_w, y1, single_w, page_h, item=right_item, fold_side="left")
            target.create_line(x1 + single_w, y1 + 4, x1 + single_w, y2 - 4, fill="#697775", width=2)
        else:
            self._gabarit_draw_sheet_guides(target, x1, y1, single_w, page_h, item=active_item)

        # Zones : lecture fidèle du gabarit, sans modifier les hitboxes de B.
        colors = {"texte": "#B69452", "image": "#6F9F9A", "document": "#9A7AA8", "libre": "#C47F69"}
        labels = {"texte": "TEXTE", "image": "IMAGE", "document": "DOCUMENT", "libre": "LIBRE"}
        selected_id = str(getattr(self, "_gabarit_selected_zone_id", "") or "")
        for zone in self._gabarit_active_zones():
            kind = str(zone.get("kind") or "document")
            zid = str(zone.get("id") or "")
            sx, sy, sw, sh = self._gabarit_zone_surface_box(zone, x1, y1, page_w, page_h)
            zx1 = sx + max(0.0, min(1.0, float(zone.get("x", 0.1)))) * sw
            zy1 = sy + max(0.0, min(1.0, float(zone.get("y", 0.1)))) * sh
            zw = max(0.04, min(1.0, float(zone.get("w", 0.3)))) * sw
            zh = max(0.04, min(1.0, float(zone.get("h", 0.2)))) * sh
            zx2 = min(sx + sw, zx1 + zw); zy2 = min(sy + sh, zy1 + zh)
            color = colors.get(kind, "#C39A4A")
            target.create_rectangle(zx1, zy1, zx2, zy2, outline=color, width=3 if zid == selected_id else 1)
            if (zx2-zx1) > 70 and (zy2-zy1) > 26:
                target.create_text((zx1+zx2)/2, (zy1+zy2)/2, text=labels.get(kind, kind.upper()), fill=color, font=(theme.FONT_UI, 8, "bold"), anchor="center")

        active_type = self._page_type_label(active_item, active_index)
        target.create_text(18, 18, text=f"Gabarit · {active_type}", anchor="nw", fill="#DCE4E2", font=(theme.FONT_TITLE, 11, "bold"))
        target.create_text(18, 40, text="Molette : zoom  ·  Glisser : déplacer  ·  Échap : retour", anchor="nw", fill="#829398", font=(theme.FONT_UI, 7))

    def _gabarit_work_rect(self) -> tuple[float, float, float, float]:
        """Surface réellement disponible pour la page, hors ligne et inspecteur."""
        width = max(1.0, float(self.canvas.winfo_width()))
        height = max(1.0, float(self.canvas.winfo_height()))
        info_w = 210.0 if width >= 1000 else 188.0
        work_left = 12.0
        work_right = max(work_left + 1.0, width - info_w - 12.0)
        work_top = 82.0
        work_bottom = max(work_top + 1.0, height - 14.0)
        return work_left, work_top, work_right, work_bottom

    def _gabarit_view_center(self) -> tuple[float, float]:
        work_left, work_top, work_right, work_bottom = self._gabarit_work_rect()
        return (work_left + work_right) / 2.0, (work_top + work_bottom) / 2.0

    def _gabarit_dimensions_for_zoom(self, value: int | None = None) -> tuple[float, float, float]:
        """Dimensions affichées à un niveau de zoom donné.

        100 % correspond exactement à Adapter. Au-delà, aucune nouvelle mise à
        l'échelle de confort n'est calculée : on agrandit réellement cette base.
        """
        viewport_w = max(1.0, float(self.canvas.winfo_width()))
        viewport_h = max(1.0, float(self.canvas.winfo_height()))
        fit = self._gabarit_fit_scale(viewport_w, viewport_h)
        zoom = int(getattr(self, "_gabarit_zoom", 100) if value is None else value)
        factor = max(1.0, float(zoom) / 100.0)
        scale = fit * factor
        spread = self._gabarit_active_is_spread()
        page_w_mm, page_h_mm = self._gabarit_page_mm()
        single_w = page_w_mm * 2.0 * scale
        page_h = page_h_mm * 2.0 * scale
        return single_w * (2.0 if spread else 1.0), page_h, scale

    def _gabarit_button_zoom_anchor(self) -> tuple[float, float]:
        """Centre de la portion actuellement visible de la page.

        Les boutons +/− utilisent ce point : ils reproduisent ainsi le comportement
        fiable de l'ancienne visionneuse, même lorsque la feuille dépasse B.
        """
        cx, cy = self._gabarit_view_center()
        box = getattr(self, "_gabarit_page_box", None)
        if box is None or not hasattr(self, "canvas"):
            return cx, cy
        work_left, work_top, work_right, work_bottom = self._gabarit_work_rect()
        x1, y1, x2, y2 = box
        ix1, ix2 = max(work_left, x1), min(work_right, x2)
        iy1, iy2 = max(work_top, y1), min(work_bottom, y2)
        if ix2 > ix1 and iy2 > iy1:
            return (ix1 + ix2) / 2.0, (iy1 + iy2) / 2.0
        return cx, cy

    def _gabarit_update_zoom_anchor(self, x: float, y: float) -> None:
        box = getattr(self, "_gabarit_page_box", None)
        if box is None:
            return
        x1, y1, x2, y2 = box
        if not (x1 <= x <= x2 and y1 <= y <= y2) or x2 <= x1 or y2 <= y1:
            return
        self._gabarit_zoom_anchor = (float(x), float(y))
        self._gabarit_zoom_ratio = (
            max(0.0, min(1.0, (float(x) - x1) / (x2 - x1))),
            max(0.0, min(1.0, (float(y) - y1) / (y2 - y1))),
        )

    def _gabarit_draw_context_overlay(
        self, units: list[dict], active_pos: int, viewport_w: float,
        *, work_left: float = 12.0, work_right: float | None = None,
    ) -> None:
        """Ligne de contexte centrée sur la surface de travail, hors inspecteur."""
        self._gabarit_context_hitboxes = {}
        if work_right is None:
            work_right = viewport_w - 12.0
        span = max(120.0, float(work_right) - float(work_left))
        positions = [float(work_left) + span * ratio for ratio in (0.12, 0.31, 0.50, 0.69, 0.88)]
        # Pas de panneau : uniquement une ligne et les stations, en surimpression.
        self.canvas.create_line(positions[0], 50, positions[-1], 50, fill="#56646C", width=1)
        window_start = active_pos - 2
        for slot, x in enumerate(positions):
            pos = window_start + slot
            if not (0 <= pos < len(units)):
                continue
            unit = units[pos]
            idx = int(unit["primary"])
            item = self.items[idx]
            status = self._gabarit_status(item)
            active = pos == active_pos
            automatic = bool(unit["automatic"])
            label = str(unit["label"] or "Page")
            if len(label) > 24:
                label = label[:22] + "…"
            fg = "#F2F3F1" if active else "#D1D7D6"
            # Ombre minuscule pour rester lisible sur une page claire sans fond opaque.
            self.canvas.create_text(x + 1, 23, text=label.upper() if active else label, fill="#10161B", font=(theme.FONT_UI, 8 if active else 7, "bold" if active else "normal"), anchor="center")
            self.canvas.create_text(x, 22, text=label.upper() if active else label, fill=fg, font=(theme.FONT_UI, 8 if active else 7, "bold" if active else "normal"), anchor="center")
            self.canvas.create_text(x + 1, 39, text=str(unit["number"]), fill="#10161B", font=(theme.FONT_UI, 7, "bold"), anchor="center")
            self.canvas.create_text(x, 38, text=str(unit["number"]), fill="#E0E4E2" if active else "#9DA7AA", font=(theme.FONT_UI, 7, "bold"), anchor="center")
            if automatic:
                self.canvas.create_rectangle(x - 5, 45, x + 5, 55, fill="#465450", outline="#C0C9C6")
            else:
                if status == "termine":
                    fill, outline = "#6FAF9A", "#A5D4C3"
                elif status == "en_cours":
                    fill, outline = "#C39A4A", "#E1C27B"
                else:
                    fill, outline = "#202B35", "#A0AAAE"
                radius = 7 if active else 6
                self.canvas.create_oval(x-radius, 50-radius, x+radius, 50+radius, fill=fill, outline=outline, width=2 if active else 1)
            if active:
                self.canvas.create_line(x - 58, 68, x + 58, 68, fill=theme.ACCENT_BRIGHT, width=2)
            self._gabarit_context_hitboxes[idx] = (x - 68, 7, x + 68, 70)

    def gabarit_set_zoom(self, value: int, *, anchor: tuple[float, float] | None = None) -> None:
        """Zoom Gabarits fondé sur la visionneuse de page historique de TomeLinea.

        100 % = Adapter. Au-delà, la page grandit réellement et peut dépasser B.
        Le point d'ancrage reste stable, comme dans l'ancienne visionneuse Structure.
        """
        value = max(100, min(900, int(value)))
        current = int(getattr(self, "_gabarit_zoom", 100))
        if value == current:
            return
        if not hasattr(self, "canvas"):
            self._gabarit_zoom = value
            self._gabarit_sync_zoom_widget()
            if value <= 100:
                self._gabarit_pan_x = 0.0
                self._gabarit_pan_y = 0.0
            if getattr(self, "_work_mode", "") == "gabarits" and hasattr(self, "render"):
                self.render()
            return

        viewport_w = max(1.0, float(self.canvas.winfo_width()))
        viewport_h = max(1.0, float(self.canvas.winfo_height()))
        cx, cy = self._gabarit_view_center()
        box = getattr(self, "_gabarit_page_box", None)
        rx, ry = getattr(self, "_gabarit_zoom_ratio", (0.5, 0.5))

        if anchor is None:
            anchor = getattr(self, "_gabarit_zoom_anchor", None)
        if anchor is None:
            ax, ay = self._gabarit_button_zoom_anchor()
        else:
            ax, ay = float(anchor[0]), float(anchor[1])

        if box is not None:
            x1, y1, x2, y2 = box
            if x2 > x1 and y2 > y1:
                rx = max(0.0, min(1.0, (ax - x1) / (x2 - x1)))
                ry = max(0.0, min(1.0, (ay - y1) / (y2 - y1)))

        self._gabarit_zoom_anchor = (ax, ay)
        self._gabarit_zoom_ratio = (rx, ry)
        self._gabarit_zoom = value
        self._gabarit_sync_zoom_widget()

        if value <= 100:
            self._gabarit_pan_x = 0.0
            self._gabarit_pan_y = 0.0
        else:
            page_w, page_h, _scale = self._gabarit_dimensions_for_zoom(value)
            self._gabarit_pan_x = ax - cx + page_w * (0.5 - rx)
            self._gabarit_pan_y = ay - cy + page_h * (0.5 - ry)
            self._gabarit_clamp_pan(viewport_w, viewport_h, page_w, page_h)

        if getattr(self, "_work_mode", "") == "gabarits":
            self.render()

    def gabarit_step_zoom(self, delta: int, *, anchor: tuple[float, float] | None = None) -> None:
        """Un cran de zoom dans B, ancré au point fourni (typiquement la souris)."""
        current = int(getattr(self, "_gabarit_zoom", 100))
        step = 12 if current < 220 else 20
        value = current + (step if int(delta) > 0 else -step)
        self.gabarit_set_zoom(max(100, value), anchor=anchor)

    def _gabarit_active_item(self) -> dict | None:
        if self._selected_index is None or not (0 <= int(self._selected_index) < len(self.items)):
            return None
        return self.items[int(self._selected_index)]

    def _gabarit_target_indices(self) -> list[int]:
        """Pages réellement touchées par une action Gabarits selon la portée choisie."""
        active = self._gabarit_active_item()
        if active is None:
            return []
        if str(getattr(self, "_gabarit_scope", "page")) != "type":
            indices = self._gabarit_active_unit_indices()
            return indices or [int(self._selected_index)]
        type_key = self._type_of(active)
        targets: list[int] = []
        for unit in self._gabarit_navigation_units():
            idx = int(unit["primary"])
            item = self.items[idx]
            if self._type_of(item) == type_key and not self._is_automatic_page(item):
                targets.append(idx)
        return targets or [int(self._selected_index)]

    def _gabarit_zone_target_indices(self) -> list[int]:
        """Les zones appartiennent à la surface active ; une paire 2P reste une seule surface."""
        active = self._gabarit_active_item()
        if active is None:
            return []
        if str(getattr(self, "_gabarit_scope", "page")) != "type":
            return [int(self._selected_index)]
        type_key = self._type_of(active)
        return [
            int(unit["primary"]) for unit in self._gabarit_navigation_units()
            if self._type_of(self.items[int(unit["primary"])]) == type_key
            and not self._is_automatic_page(self.items[int(unit["primary"])])
        ] or [int(self._selected_index)]

    GABARIT_STANDARD_FORMATS = (
        ("A4", "A4", 210.0, 297.0),
        ("A5", "A5", 148.0, 210.0),
        ("A6", "A6", 105.0, 148.0),
        ("roman_140x210", "Roman 140 × 210", 140.0, 210.0),
        ("roman_150x230", "Roman 150 × 230", 150.0, 230.0),
        ("grand_170x240", "Grand livre 170 × 240", 170.0, 240.0),
        ("carre_148", "Carré 148 × 148", 148.0, 148.0),
        ("carre_210", "Carré 210 × 210", 210.0, 210.0),
    )

    def gabarit_format_catalog(self) -> list[dict]:
        return [
            {"id": key, "label": label, "width_mm": width, "height_mm": height}
            for key, label, width, height in self.GABARIT_STANDARD_FORMATS
        ]

    def gabarit_has_explicit_format(self) -> bool:
        data = getattr(self, "_data", None)
        raw = data.get("gabarit_book_settings") if isinstance(data, dict) else None
        return bool(
            isinstance(raw, dict)
            and float(raw.get("page_width_mm", 0.0) or 0.0) > 0
            and float(raw.get("page_height_mm", 0.0) or 0.0) > 0
        )

    def gabarit_book_format(self) -> dict:
        layout = self._gabarit_effective_book_layout()
        return {
            "id": str(layout.get("format_id") or "A4"),
            "label": str(layout.get("format_label") or "A4"),
            "width_mm": float(layout.get("page_width_mm", 210.0)),
            "height_mm": float(layout.get("page_height_mm", 297.0)),
            "explicit": self.gabarit_has_explicit_format(),
        }

    def _gabarit_page_mm(self) -> tuple[float, float]:
        layout = self._gabarit_effective_book_layout()
        return (
            max(40.0, float(layout.get("page_width_mm", 210.0))),
            max(40.0, float(layout.get("page_height_mm", 297.0))),
        )

    @staticmethod
    def _gabarit_default_settings() -> dict:
        return {
            "margins_mm": {"top": 15.0, "bottom": 15.0, "inside": 15.0, "outside": 15.0},
            "bleed_mm": {"top": 3.0, "right": 3.0, "bottom": 3.0, "left": 3.0},
            "show_guides": True,
            "background": "#F1F1EE",
        }

    def _gabarit_effective_book_layout(self) -> dict:
        """Format, marges et fond perdu : réglages uniques au niveau du livre."""
        defaults = self._gabarit_default_settings()
        result = {
            "format_id": "A4",
            "format_label": "A4",
            "page_width_mm": 210.0,
            "page_height_mm": 297.0,
            "margins_mm": dict(defaults["margins_mm"]),
            "bleed_mm": dict(defaults["bleed_mm"]),
        }
        data = getattr(self, "_data", None)
        raw = data.get("gabarit_book_settings") if isinstance(data, dict) else None
        if not isinstance(raw, dict):
            # Migration douce des anciennes marges/fonds perdus enregistrés par page.
            raw = None
            for item in getattr(self, "items", []):
                if not isinstance(item, dict) or self._is_automatic_page(item):
                    continue
                candidate = item.get("gabarit_page_settings")
                if isinstance(candidate, dict) and (
                    isinstance(candidate.get("margins_mm"), dict)
                    or isinstance(candidate.get("bleed_mm"), dict)
                ):
                    raw = candidate
                    break
        if isinstance(raw, dict):
            for key in ("margins_mm", "bleed_mm"):
                source = raw.get(key)
                if isinstance(source, dict):
                    result[key].update({
                        k: float(v) for k, v in source.items() if k in result[key]
                    })
            try:
                width = float(raw.get("page_width_mm", 0.0) or 0.0)
                height = float(raw.get("page_height_mm", 0.0) or 0.0)
            except Exception:
                width = height = 0.0
            if width >= 40.0 and height >= 40.0:
                result["page_width_mm"] = width
                result["page_height_mm"] = height
                result["format_id"] = str(raw.get("format_id") or "custom")
                result["format_label"] = str(raw.get("format_label") or "Personnalisé")
        return result

    def gabarit_current_settings(self) -> dict:
        item = self._gabarit_active_item()
        defaults = self._gabarit_default_settings()
        result = deepcopy(defaults)
        layout = self._gabarit_effective_book_layout()
        result["margins_mm"].update(layout["margins_mm"])
        result["bleed_mm"].update(layout["bleed_mm"])

        # Affichage des guides et fond de page restent des propriétés de gabarit.
        raw = item.get("gabarit_page_settings", {}) if isinstance(item, dict) else {}
        if isinstance(raw, dict):
            if "show_guides" in raw:
                result["show_guides"] = bool(raw.get("show_guides"))
            bg = str(raw.get("background") or "").strip()
            if bg:
                result["background"] = bg
        return result

    def _gabarit_mark_edited(self, item: dict) -> None:
        item["gabarit_status"] = "en_cours"
        item["gabarit_done"] = False

    def _gabarit_apply_settings_patch(self, patch: dict, status: str) -> bool:
        targets = self._gabarit_target_indices()
        if not targets:
            return False
        for idx in targets:
            item = self.items[idx]
            settings = self._gabarit_default_settings()
            existing = item.get("gabarit_page_settings")
            if isinstance(existing, dict):
                # Les anciennes valeurs de marges/fond perdu sont conservées dans le
                # fichier pour compatibilité, mais l'affichage utilise le réglage livre.
                for key in ("margins_mm", "bleed_mm"):
                    if isinstance(existing.get(key), dict):
                        settings[key].update(existing[key])
                for key in ("show_guides", "background"):
                    if key in existing:
                        settings[key] = existing[key]
            for key, value in patch.items():
                if key in {"margins_mm", "bleed_mm"} and isinstance(value, dict):
                    settings[key].update(value)
                else:
                    settings[key] = value
            item["gabarit_page_settings"] = settings
            self._gabarit_mark_edited(item)
        self._save_order()
        self.render()
        self._emit_gabarit_page_changed()
        self.status_var.set(status)
        return True

    def _gabarit_persist_book_layout(self, layout: dict, status: str) -> bool:
        if getattr(self, "project", None) is None or not isinstance(getattr(self, "_data", None), dict):
            return False
        data = deepcopy(self._data)
        data["gabarit_book_settings"] = {
            "format_id": str(layout.get("format_id") or "custom"),
            "format_label": str(layout.get("format_label") or "Personnalisé"),
            "page_width_mm": float(layout.get("page_width_mm", 210.0)),
            "page_height_mm": float(layout.get("page_height_mm", 297.0)),
            "margins_mm": dict(layout["margins_mm"]),
            "bleed_mm": dict(layout["bleed_mm"]),
        }
        data["groups"] = [dict(group) for group in self.groups]
        data["items"] = [dict(item) for item in self.items]
        data, _ = self._ensure_minimum_structure(data)
        try:
            saved = self.project.save_mockup(data)
        except Exception:
            return False
        if not isinstance(saved, dict):
            saved = data
        self._data = deepcopy(saved)
        self.groups = [dict(group) for group in saved.get("groups", []) if isinstance(group, dict)]
        self.items = [dict(item) for item in saved.get("items", []) if isinstance(item, dict)]
        self._history_record_saved(saved)
        self.render()
        self._emit_gabarit_page_changed()
        self.status_var.set(status)
        if self.on_change is not None:
            self.on_change()
        return True

    def _gabarit_save_book_layout(self, key: str, values: dict, status: str) -> bool:
        """Persiste marges/fond perdu une seule fois au niveau du livre."""
        if getattr(self, "project", None) is None or not isinstance(getattr(self, "_data", None), dict):
            return self._gabarit_apply_settings_patch({key: values}, status)
        layout = self._gabarit_effective_book_layout()
        layout[key].update(values)
        return self._gabarit_persist_book_layout(layout, status)

    def gabarit_set_book_format(self, format_id: str, label: str, width_mm: float, height_mm: float) -> bool:
        try:
            width_mm = float(width_mm)
            height_mm = float(height_mm)
        except Exception:
            return False
        if not (40.0 <= width_mm <= 600.0 and 40.0 <= height_mm <= 600.0):
            return False
        layout = self._gabarit_effective_book_layout()
        margins = layout.get("margins_mm", {})
        if (
            float(margins.get("inside", 0.0)) + float(margins.get("outside", 0.0)) >= width_mm
            or float(margins.get("top", 0.0)) + float(margins.get("bottom", 0.0)) >= height_mm
        ):
            return False
        layout["format_id"] = str(format_id or "custom")
        layout["format_label"] = str(label or "Personnalisé")
        layout["page_width_mm"] = width_mm
        layout["page_height_mm"] = height_mm
        ok = self._gabarit_persist_book_layout(layout, "Format du livre mis à jour")
        if ok:
            self._gabarit_zoom = 100
            self._gabarit_pan_x = 0.0
            self._gabarit_pan_y = 0.0
            try:
                if self.project is not None:
                    self.project.format = str(label or format_id or "Personnalisé")
                    self.project.save()
            except Exception:
                pass
            self.render()
        return ok

    def gabarit_set_margins(self, top: float, bottom: float, inside: float, outside: float) -> bool:
        values = {"top": float(top), "bottom": float(bottom), "inside": float(inside), "outside": float(outside)}
        page_w_mm, page_h_mm = self._gabarit_page_mm()
        if any(v < 0 for v in values.values()) or values["top"] + values["bottom"] >= page_h_mm or values["inside"] + values["outside"] >= page_w_mm:
            return False
        return self._gabarit_save_book_layout("margins_mm", values, "Marges du livre mises à jour")

    def gabarit_set_bleed(self, top: float, right: float, bottom: float, left: float) -> bool:
        values = {"top": float(top), "right": float(right), "bottom": float(bottom), "left": float(left)}
        if any(v < 0 or v > 30 for v in values.values()):
            return False
        return self._gabarit_save_book_layout("bleed_mm", values, "Fond perdu du livre mis à jour")

    def gabarit_toggle_guides(self) -> bool:
        current = bool(self.gabarit_current_settings().get("show_guides", True))
        return self._gabarit_apply_settings_patch({"show_guides": not current}, "Guides affichés" if not current else "Guides masqués")

    def gabarit_set_background(self, color: str) -> bool:
        color = str(color or "").strip()
        if not color.startswith("#") or len(color) != 7:
            return False
        return self._gabarit_apply_settings_patch({"background": color}, "Fond de page mis à jour")

    def gabarit_active_is_spread(self) -> bool:
        """Expose à C si la surface active est une double page."""
        return self._gabarit_active_is_spread()

    def _gabarit_zone_spread_position(self, zone: dict | None) -> str:
        """Surface horizontale utilisée par une zone dans une double page.

        Les anciennes zones n'avaient pas ce champ : elles restent au centre afin
        de préserver exactement leur rendu historique. Les nouvelles zones utilisent
        la dernière cible choisie, gauche par défaut.
        """
        if not isinstance(zone, dict):
            return "center"
        value = str(zone.get("spread_position") or "").strip().lower()
        return value if value in {"left", "center", "right"} else "center"

    def gabarit_spread_target(self) -> str:
        value = str(getattr(self, "_gabarit_spread_target", "left") or "left").strip().lower()
        return value if value in {"left", "center", "right"} else "left"

    def gabarit_set_selected_zone_spread_position(self, position: str) -> bool:
        """Place une zone sur la page gauche, la double page ou la page droite."""
        if not self._gabarit_active_is_spread():
            self.status_var.set("Ce réglage est disponible uniquement sur une double page.")
            return False
        position = str(position or "left").strip().lower()
        if position not in {"left", "center", "right"}:
            return False
        self._gabarit_spread_target = position
        active = self._gabarit_active_item()
        zone = self._gabarit_find_zone(active, zone_id=self._gabarit_selected_zone_id) if active else None
        if zone is None:
            labels = {"left": "gauche", "center": "centre", "right": "droite"}
            self.status_var.set(f"Prochaine zone 2P : {labels[position]}")
            self._emit_gabarit_selection_changed()
            return True
        slot_key = str(zone.get("slot_key") or zone.get("id") or "")
        changed = False
        for idx in self._gabarit_zone_target_indices():
            item = self.items[idx]
            target = self._gabarit_find_zone(item, slot_key=slot_key)
            if target is None and idx == self._selected_index:
                target = self._gabarit_find_zone(item, zone_id=self._gabarit_selected_zone_id)
            if target is None:
                continue
            target["spread_position"] = position
            self._gabarit_mark_edited(item)
            changed = True
        if changed:
            labels = {"left": "gauche", "center": "centre", "right": "droite"}
            self._save_order()
            self.render()
            self._emit_gabarit_page_changed()
            self._emit_gabarit_selection_changed()
            self.status_var.set(f"Zone placée sur la {labels[position] if position != 'center' else 'double page'}")
        return changed

    def _gabarit_zone_surface_box(
        self, zone: dict, x1: float, y1: float, total_w: float, page_h: float,
    ) -> tuple[float, float, float, float]:
        """Rectangle écran de référence de la zone (gauche / double / droite)."""
        if not self._gabarit_active_is_spread():
            return x1, y1, total_w, page_h
        position = self._gabarit_zone_spread_position(zone)
        half = total_w / 2.0
        if position == "left":
            return x1, y1, half, page_h
        if position == "right":
            return x1 + half, y1, half, page_h
        return x1, y1, total_w, page_h

    def _gabarit_active_zones(self) -> list[dict]:
        item = self._gabarit_active_item()
        if not isinstance(item, dict):
            return []
        zones = item.get("gabarit_zones")
        return zones if isinstance(zones, list) else []

    def _gabarit_find_zone(self, item: dict, zone_id: str = "", slot_key: str = "") -> dict | None:
        zones = item.get("gabarit_zones")
        if not isinstance(zones, list):
            return None
        for zone in zones:
            if not isinstance(zone, dict):
                continue
            if zone_id and str(zone.get("id") or "") == zone_id:
                return zone
            if slot_key and str(zone.get("slot_key") or "") == slot_key:
                return zone
        return None

    def gabarit_add_zone(self, kind: str) -> bool:
        kind = str(kind or "").strip().lower()
        if kind not in {"text", "image", "document"}:
            return False
        targets = self._gabarit_zone_target_indices()
        if not targets:
            return False
        defaults = {
            "text": (0.12, 0.68, 0.76, 0.14),
            "image": (0.12, 0.12, 0.76, 0.48),
            "document": (0.15, 0.15, 0.70, 0.70),
        }
        x, y, w, h = defaults[kind]
        active_zones = self._gabarit_active_zones()
        offset = min(0.12, 0.025 * sum(1 for z in active_zones if isinstance(z, dict) and z.get("kind") == kind))
        x = min(0.92 - w, x + offset)
        y = min(0.92 - h, y + offset)
        slot_key = f"GZ-{uuid4().hex[:10].upper()}"
        active_id = ""
        for idx in targets:
            zone = {
                "id": f"GZ-{uuid4().hex[:12].upper()}",
                "slot_key": slot_key,
                "kind": kind,
                "x": x, "y": y, "w": w, "h": h,
            }
            if self._gabarit_active_is_spread():
                zone["spread_position"] = self.gabarit_spread_target()
            item = self.items[idx]
            zones = item.get("gabarit_zones")
            if not isinstance(zones, list):
                zones = []
                item["gabarit_zones"] = zones
            zones.append(zone)
            self._gabarit_mark_edited(item)
            if idx == self._selected_index:
                active_id = zone["id"]
        self._gabarit_selected_zone_id = active_id
        self._save_order()
        self.render()
        self._emit_gabarit_page_changed(); self._emit_gabarit_selection_changed()
        labels = {"text": "Zone texte créée", "image": "Zone image créée", "document": "Zone document créée"}
        self.status_var.set(labels[kind])
        return True

    def gabarit_duplicate_selected_zone(self) -> bool:
        active = self._gabarit_active_item()
        zone = self._gabarit_find_zone(active, zone_id=self._gabarit_selected_zone_id) if active else None
        if zone is None:
            self.status_var.set("Sélectionnez d’abord une zone dans la page.")
            return False
        slot_key = str(zone.get("slot_key") or zone.get("id") or "")
        new_slot = f"GZ-{uuid4().hex[:10].upper()}"
        active_new_id = ""
        for idx in self._gabarit_zone_target_indices():
            item = self.items[idx]
            source = self._gabarit_find_zone(item, slot_key=slot_key)
            if source is None and idx == self._selected_index:
                source = zone
            if source is None:
                continue
            clone = dict(source)
            clone["id"] = f"GZ-{uuid4().hex[:12].upper()}"
            clone["slot_key"] = new_slot
            clone["x"] = min(0.95 - float(clone.get("w", .2)), float(clone.get("x", 0)) + 0.03)
            clone["y"] = min(0.95 - float(clone.get("h", .2)), float(clone.get("y", 0)) + 0.03)
            zones = item.setdefault("gabarit_zones", [])
            zones.append(clone)
            self._gabarit_mark_edited(item)
            if idx == self._selected_index:
                active_new_id = clone["id"]
        if not active_new_id:
            return False
        self._gabarit_selected_zone_id = active_new_id
        self._save_order(); self.render(); self._emit_gabarit_page_changed(); self._emit_gabarit_selection_changed()
        self.status_var.set("Zone dupliquée")
        return True

    def gabarit_delete_selected_zone(self) -> bool:
        active = self._gabarit_active_item()
        zone = self._gabarit_find_zone(active, zone_id=self._gabarit_selected_zone_id) if active else None
        if zone is None:
            self.status_var.set("Sélectionnez d’abord une zone dans la page.")
            return False
        slot_key = str(zone.get("slot_key") or zone.get("id") or "")
        changed = False
        for idx in self._gabarit_zone_target_indices():
            item = self.items[idx]
            zones = item.get("gabarit_zones")
            if not isinstance(zones, list):
                continue
            kept = [z for z in zones if not (isinstance(z, dict) and (str(z.get("slot_key") or "") == slot_key or (idx == self._selected_index and str(z.get("id") or "") == self._gabarit_selected_zone_id)))]
            if len(kept) != len(zones):
                item["gabarit_zones"] = kept
                self._gabarit_mark_edited(item)
                changed = True
        if not changed:
            return False
        self._gabarit_selected_zone_id = ""
        self._save_order(); self.render(); self._emit_gabarit_page_changed(); self._emit_gabarit_selection_changed()
        self.status_var.set("Zone supprimée")
        return True

    def gabarit_center_selected_zone(self) -> bool:
        active = self._gabarit_active_item()
        zone = self._gabarit_find_zone(active, zone_id=self._gabarit_selected_zone_id) if active else None
        if zone is None:
            self.status_var.set("Sélectionnez d’abord une zone dans la page.")
            return False
        rect = (max(0.0, (1.0 - float(zone.get("w", .2))) / 2.0), max(0.0, (1.0 - float(zone.get("h", .2))) / 2.0), float(zone.get("w", .2)), float(zone.get("h", .2)))
        return self._gabarit_commit_zone_rect(zone, rect, "Zone centrée")

    def gabarit_toggle_selected_zone_lock(self) -> bool:
        active = self._gabarit_active_item()
        zone = self._gabarit_find_zone(active, zone_id=self._gabarit_selected_zone_id) if active else None
        if zone is None:
            self.status_var.set("Sélectionnez d’abord une zone dans la page.")
            return False
        slot_key = str(zone.get("slot_key") or zone.get("id") or "")
        new_state = not bool(zone.get("locked", False))
        changed = False
        for idx in self._gabarit_zone_target_indices():
            item = self.items[idx]
            target = self._gabarit_find_zone(item, slot_key=slot_key)
            if target is None and idx == self._selected_index:
                target = self._gabarit_find_zone(item, zone_id=self._gabarit_selected_zone_id)
            if target is None:
                continue
            target["locked"] = new_state
            self._gabarit_mark_edited(item)
            changed = True
        if changed:
            self._save_order(); self.render(); self._emit_gabarit_selection_changed()
            self.status_var.set("Zone verrouillée" if new_state else "Zone déverrouillée")
        return changed

    def gabarit_move_selected_zone_layer(self, direction: str) -> bool:
        active = self._gabarit_active_item()
        zone = self._gabarit_find_zone(active, zone_id=self._gabarit_selected_zone_id) if active else None
        if zone is None:
            self.status_var.set("Sélectionnez d’abord une zone dans la page.")
            return False
        slot_key = str(zone.get("slot_key") or zone.get("id") or "")
        forward = str(direction or "").lower() in {"front", "avant", "forward"}
        changed = False
        for idx in self._gabarit_zone_target_indices():
            item = self.items[idx]
            zones = item.get("gabarit_zones")
            if not isinstance(zones, list) or len(zones) < 2:
                continue
            pos = next((i for i,z in enumerate(zones) if isinstance(z,dict) and (str(z.get("slot_key") or "") == slot_key or (idx == self._selected_index and str(z.get("id") or "") == self._gabarit_selected_zone_id))), None)
            if pos is None:
                continue
            new_pos = min(len(zones)-1, pos+1) if forward else max(0, pos-1)
            if new_pos == pos:
                continue
            moved = zones.pop(pos); zones.insert(new_pos, moved)
            self._gabarit_mark_edited(item); changed = True
        if changed:
            self._save_order(); self.render(); self._emit_gabarit_selection_changed()
            self.status_var.set("Zone avancée" if forward else "Zone reculée")
        return changed


    def gabarit_align_selected_zone(self, mode: str, reference: str = "page") -> bool:
        active = self._gabarit_active_item()
        zone = self._gabarit_find_zone(active, zone_id=self._gabarit_selected_zone_id) if active else None
        if zone is None:
            self.status_var.set("Sélectionnez d’abord une zone dans la page.")
            return False
        if bool(zone.get("locked", False)):
            self.status_var.set("Déverrouillez la zone avant de l’aligner.")
            return False

        reference = str(reference or "page").strip().lower()
        spread_position = self._gabarit_zone_spread_position(zone) if self._gabarit_active_is_spread() else ""
        page_w_mm, page_h_mm = self._gabarit_page_mm()
        width_mm = page_w_mm * 2.0 if spread_position == "center" else page_w_mm
        if reference == "margins":
            settings = self.gabarit_current_settings() or {}
            margins = dict(settings.get("margins_mm") or {})
            rx = float(margins.get("inside", 15.0)) / width_mm
            ry = float(margins.get("top", 15.0)) / page_h_mm
            rw = max(0.001, 1.0 - (float(margins.get("inside", 15.0)) + float(margins.get("outside", 15.0))) / width_mm)
            rh = max(0.001, 1.0 - (float(margins.get("top", 15.0)) + float(margins.get("bottom", 15.0))) / page_h_mm)
        else:
            rx, ry, rw, rh = 0.0, 0.0, 1.0, 1.0

        x = float(zone.get("x", 0))
        y = float(zone.get("y", 0))
        w = float(zone.get("w", .2))
        h = float(zone.get("h", .2))
        mode = str(mode or "center").lower()

        if mode == "left":
            x = rx
        elif mode in {"center", "hcenter"}:
            x = rx + max(0.0, (rw - w) / 2.0)
        elif mode == "right":
            x = rx + max(0.0, rw - w)
        elif mode == "top":
            y = ry
        elif mode in {"middle", "vcenter"}:
            y = ry + max(0.0, (rh - h) / 2.0)
        elif mode == "bottom":
            y = ry + max(0.0, rh - h)
        else:
            return False

        label = "marges" if reference == "margins" else "page"
        return self._gabarit_commit_zone_rect(zone, (x, y, w, h), f"Zone alignée sur la {label}")

    def _gabarit_commit_zone_rect(self, active_zone: dict, rect: tuple[float, float, float, float], status: str = "Zone modifiée") -> bool:
        slot_key = str(active_zone.get("slot_key") or active_zone.get("id") or "")
        x, y, w, h = rect
        changed = False
        for idx in self._gabarit_zone_target_indices():
            item = self.items[idx]
            zone = self._gabarit_find_zone(item, slot_key=slot_key)
            if zone is None and idx == self._selected_index:
                zone = self._gabarit_find_zone(item, zone_id=self._gabarit_selected_zone_id)
            if zone is None:
                continue
            zone.update({"x": float(x), "y": float(y), "w": float(w), "h": float(h)})
            self._gabarit_mark_edited(item)
            changed = True
        if changed:
            self._save_order(); self.render(); self._emit_gabarit_page_changed()
            self.status_var.set(status)
        return changed

    def _gabarit_active_is_spread(self) -> bool:
        """Indique si la surface active est une double page, y compris en test léger."""
        try:
            indices = self._gabarit_active_unit_indices()
        except Exception:
            return False
        if len(indices) == 2:
            return True
        try:
            return bool(indices and self._effective_double_page_rule(self.items[indices[0]]))
        except Exception:
            return False

    def _gabarit_fit_scale(self, viewport_w: float, viewport_h: float) -> float:
        spread = self._gabarit_active_is_spread()
        page_w_mm, page_h_mm = self._gabarit_page_mm()
        logical_w = page_w_mm * 2.0 * (2.0 if spread else 1.0)
        logical_h = page_h_mm * 2.0
        # B est désormais asymétrique : inspecteur compact à droite, aucune réserve
        # artificielle à gauche. La page s'adapte à la vraie surface restante.
        info_w = 210.0 if viewport_w >= 1000 else 188.0
        work_left = 12.0
        work_right = max(work_left + 1.0, viewport_w - info_w - 12.0)
        top_h = 82.0
        bottom_h = 16.0
        # Réserve latérale uniquement pour laisser respirer les flèches de navigation.
        usable_w = max(180.0, (work_right - work_left) - 150.0)
        usable_h = max(160.0, viewport_h - top_h - bottom_h - 24.0)
        return max(0.08, min(usable_w / logical_w, usable_h / logical_h))

    def _gabarit_clamp_pan(self, viewport_w: float, viewport_h: float, page_w: float, page_h: float) -> None:
        """Limite le déplacement sans casser l'ancrage du zoom sous la souris.

        Le principe est celui d'un viewport de Canvas : si la page dépasse, elle peut
        défiler jusqu'à ce qu'une petite bande reste récupérable. Si elle tient encore
        dans un axe, elle reste entièrement à l'intérieur de la surface de travail.
        """
        if int(getattr(self, "_gabarit_zoom", 100)) <= 100:
            self._gabarit_pan_x = 0.0
            self._gabarit_pan_y = 0.0
            return
        if hasattr(self, "canvas"):
            work_left, work_top, work_right, work_bottom = self._gabarit_work_rect()
        else:
            work_left, work_top, work_right, work_bottom = 0.0, 0.0, float(viewport_w), float(viewport_h)
        work_w = max(1.0, work_right - work_left)
        work_h = max(1.0, work_bottom - work_top)
        visible_edge = 56.0

        def axis_limit(page: float, view: float) -> float:
            page = max(1.0, float(page)); view = max(1.0, float(view))
            if page <= view:
                # Même lorsqu'elle tient encore dans l'axe, une petite marge de
                # surdéplacement est autorisée : c'est ce qui permet de garder
                # exactement le point sous la souris pendant les premiers crans.
                return max(0.0, (view - page) / 2.0 + min(72.0, view * 0.12))
            # Quand elle dépasse, seul un ruban minimal doit rester visible.
            return max(0.0, (page + view) / 2.0 - min(visible_edge, view * 0.25))

        max_x = axis_limit(page_w, work_w)
        max_y = axis_limit(page_h, work_h)
        self._gabarit_pan_x = max(-max_x, min(max_x, float(self._gabarit_pan_x)))
        self._gabarit_pan_y = max(-max_y, min(max_y, float(self._gabarit_pan_y)))

    @staticmethod
    def _gabarit_point_in(box, x: float, y: float) -> bool:
        return bool(box and box[0] <= x <= box[2] and box[1] <= y <= box[3])

    def _gabarit_sheet_settings(self, item: dict | None = None) -> dict:
        """Réunit les réglages utilisés par le rendu de B."""
        settings = self._gabarit_default_settings()
        layout = self._gabarit_effective_book_layout()
        settings["margins_mm"].update(layout["margins_mm"])
        settings["bleed_mm"].update(layout["bleed_mm"])
        raw = item.get("gabarit_page_settings") if isinstance(item, dict) else None
        if isinstance(raw, dict):
            for key in ("show_guides", "background"):
                if key in raw:
                    settings[key] = raw[key]
        return settings

    def _gabarit_bleed_pixels(self, w: float, h: float, settings: dict) -> tuple[float, float, float, float]:
        """Convertit le fond perdu en pixels autour du format fini.

        Un minimum visuel très léger est conservé à faible zoom pour que la
        couronne reste lisible, sans modifier les valeurs enregistrées.
        """
        bleed = dict(settings.get("bleed_mm") or {})

        def px(mm: float, dimension: float, reference_mm: float) -> float:
            mm = max(0.0, float(mm))
            if mm <= 0.0:
                return 0.0
            # À faible zoom les 3 mm réels tomberaient à 2–3 pixels.
            # On conserve donc une épaisseur d'écran minimale clairement perceptible.
            return max(7.0, float(dimension) * mm / reference_mm)

        page_w_mm, page_h_mm = self._gabarit_page_mm()
        left = px(bleed.get("left", 3.0), w, page_w_mm)
        right = px(bleed.get("right", 3.0), w, page_w_mm)
        top = px(bleed.get("top", 3.0), h, page_h_mm)
        bottom = px(bleed.get("bottom", 3.0), h, page_h_mm)
        return left, right, top, bottom

    def _gabarit_draw_bleed_halo(
        self, target, x: float, y: float, w: float, h: float,
        *, settings: dict, fold_side: str = "",
    ) -> None:
        """Dessine le fond perdu comme une couronne extérieure semi-transparente."""
        if not bool(settings.get("show_guides", True)):
            return
        left, right, top, bottom = self._gabarit_bleed_pixels(w, h, settings)
        # Dans une double page, la jonction centrale n'est pas un bord extérieur.
        if fold_side == "right":
            right = 0.0
        elif fold_side == "left":
            left = 0.0
        if max(left, right, top, bottom) <= 0.0:
            return

        fill = "#70494D"      # rouge brique fumé : effet de halo sans trame pointillée
        outline = "#B07173"
        stipple = ""          # Tk n’a pas d’alpha : la teinte sourde simule la transparence

        if top > 0.0:
            target.create_rectangle(
                x - left, y - top, x + w + right, y,
                fill=fill, outline="", stipple=stipple,
            )
        if bottom > 0.0:
            target.create_rectangle(
                x - left, y + h, x + w + right, y + h + bottom,
                fill=fill, outline="", stipple=stipple,
            )
        if left > 0.0:
            target.create_rectangle(
                x - left, y, x, y + h,
                fill=fill, outline="", stipple=stipple,
            )
        if right > 0.0:
            target.create_rectangle(
                x + w, y, x + w + right, y + h,
                fill=fill, outline="", stipple=stipple,
            )
        target.create_rectangle(
            x - left, y - top, x + w + right, y + h + bottom,
            fill="", outline=outline, width=2,
        )

    def _gabarit_draw_sheet_guides(self, target, x: float, y: float, w: float, h: float, *, item: dict | None = None, fold_side: str = "") -> None:
        settings = self._gabarit_sheet_settings(item)
        bg = str(settings.get("background") or "#F1F1EE")

        # Le fond perdu est volontairement hors du format fini : il apparaît
        # comme une couronne douce autour de la feuille, jamais comme un cadre
        # pointillé à l'intérieur de celle-ci.
        self._gabarit_draw_bleed_halo(
            target, x, y, w, h, settings=settings, fold_side=fold_side,
        )

        # Format fini : c'est le repère principal de la page.
        target.create_rectangle(
            x, y, x + w, y + h,
            fill=bg, outline="#C8CECB", width=2,
        )
        if bool(settings.get("show_guides", True)):
            margins = settings["margins_mm"]
            page_w_mm, page_h_mm = self._gabarit_page_mm()
            # À ce stade le côté physique n'est pas encore un réglage de gabarit :
            # on affiche intérieur à gauche, extérieur à droite, puis Production
            # pourra inverser automatiquement selon Recto/Verso.
            mx1 = x + w * float(margins.get("inside", 15.0)) / page_w_mm
            mx2 = x + w - w * float(margins.get("outside", 15.0)) / page_w_mm
            my1 = y + h * float(margins.get("top", 15.0)) / page_h_mm
            my2 = y + h - h * float(margins.get("bottom", 15.0)) / page_h_mm
            # Un seul repère intérieur : les anciens cadres pointillés et la
            # pseudo-zone de sécurité supplémentaire brouillaient la lecture.
            target.create_rectangle(
                mx1, my1, mx2, my2,
                outline="#71928C", width=1,
            )
        if fold_side == "right":
            target.create_line(x + w, y, x + w, y + h, fill="#7D8986", width=2)
        elif fold_side == "left":
            target.create_line(x, y, x, y + h, fill="#7D8986", width=2)

    def _gabarit_draw_zones(self, x1: float, y1: float, total_w: float, page_h: float) -> None:
        self._gabarit_zone_hitboxes = {}
        self._gabarit_zone_handle_hitboxes = {}
        zones = self._gabarit_active_zones()
        if not zones:
            return
        colors = {"text": "#6FAF9A", "image": "#779BC2", "document": "#C39A4A"}
        labels = {"text": "TEXTE", "image": "IMAGE", "document": "DOCUMENT"}
        selected_id = str(getattr(self, "_gabarit_selected_zone_id", "") or "")
        for zone in zones:
            if not isinstance(zone, dict):
                continue
            zid = str(zone.get("id") or "")
            kind = str(zone.get("kind") or "document")
            sx, sy, sw, sh = self._gabarit_zone_surface_box(zone, x1, y1, total_w, page_h)
            zx1 = sx + max(0.0, min(1.0, float(zone.get("x", 0.1)))) * sw
            zy1 = sy + max(0.0, min(1.0, float(zone.get("y", 0.1)))) * sh
            zw = max(0.04, min(1.0, float(zone.get("w", 0.3)))) * sw
            zh = max(0.04, min(1.0, float(zone.get("h", 0.2)))) * sh
            zx2 = min(sx + sw, zx1 + zw)
            zy2 = min(sy + sh, zy1 + zh)
            selected = zid == selected_id
            color = colors.get(kind, "#C39A4A")
            self.canvas.create_rectangle(zx1, zy1, zx2, zy2, outline=color, width=3 if selected else 1)
            if (zx2 - zx1) > 74 and (zy2 - zy1) > 28:
                self.canvas.create_text((zx1+zx2)/2, (zy1+zy2)/2, text=labels.get(kind, kind.upper()), fill=color, font=(theme.FONT_UI, 8, "bold"), anchor="center")
            self._gabarit_zone_hitboxes[zid] = (zx1, zy1, zx2, zy2)
            if selected:
                if bool(zone.get("locked", False)):
                    self.canvas.create_text(zx1 + 7, zy1 + 7, text="VERROUILLÉ", anchor="nw", fill=color, font=(theme.FONT_UI, 6, "bold"))
                else:
                    hs = 7.0
                    self.canvas.create_rectangle(zx2-hs, zy2-hs, zx2+hs, zy2+hs, fill=color, outline="#F5F6F4", width=1)
                    self._gabarit_zone_handle_hitboxes[zid] = (zx2-hs-3, zy2-hs-3, zx2+hs+3, zy2+hs+3)

    def _render_gabarit_workspace(self, viewport_w: float, viewport_h: float) -> None:
        self.canvas.delete("all")
        self._gabarit_hitboxes = {}
        self._gabarit_context_hitboxes = {}
        self._gabarit_zone_hitboxes = {}
        self._gabarit_zone_handle_hitboxes = {}
        self._gabarit_page_box = None
        self._v_scroll_needed = False
        self._h_scroll_needed = False
        try:
            self.v_scroll.grid_remove()
        except Exception:
            pass
        self.canvas.configure(scrollregion=(0, 0, viewport_w, viewport_h))
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        if not self.items:
            self.status_var.set("Aucune page dans le livre")
            return
        self._gabarit_normalize_selected_index()
        units, active_pos = self._gabarit_unit_position()
        if not units:
            return
        active_unit = units[active_pos]
        active_index = int(active_unit["primary"])
        active_item = self.items[active_index]
        group_id = self._item_group_id(active_item)
        group = next((g for g in self.groups if str(g.get("id") or "") == group_id), {})
        part = self._group_name(group)
        part_title = self._group_part_title(group)
        part_text = part if not part_title or part_title == "Titre à définir" else f"{part} — {part_title}"
        active_type = self._page_type_label(active_item, active_index)
        total = self._structure_work_page_count()
        number = active_unit["number"]
        self.status_var.set(f"{number} / {total}  •  {active_type}  •  {part_text}")

        # La ligne de contexte sera dessinée en dernier, en transparence, au-dessus de la page.

        # ----- zone de travail -----
        # L'inspecteur occupe toute la hauteur à droite. La ligne de contexte et la
        # page sont recentrées sur tout l'espace réellement restant.
        # L'inspecteur garde sa largeur lisible, mais reste entierement dans la
        # surface utile de B : on reserve une petite gouttiere au bord coupe.
        info_w = 210.0 if viewport_w >= 1000 else 188.0
        edge_gutter = 8.0
        info_x1 = viewport_w - info_w - edge_gutter
        work_left = 12.0
        work_right = info_x1 - 12.0
        work_top = 82.0
        work_bottom = viewport_h - 14.0
        work_center_x = (work_left + work_right) / 2.0
        work_center_y = (work_top + work_bottom) / 2.0
        spread = bool(active_unit["double"])
        total_w, page_h, scale = self._gabarit_dimensions_for_zoom()
        zoom_factor = max(1.0, float(getattr(self, "_gabarit_zoom", 100)) / 100.0)
        single_w = total_w / (2.0 if spread else 1.0)
        self._gabarit_clamp_pan(viewport_w, viewport_h, total_w, page_h)
        cx = work_center_x + self._gabarit_pan_x
        cy = work_center_y + self._gabarit_pan_y
        x1 = cx - total_w / 2.0
        y1 = cy - page_h / 2.0
        x2 = x1 + total_w
        y2 = y1 + page_h
        self._gabarit_page_box = (x1, y1, x2, y2)

        shadow = max(3.0, min(13.0, 5.0 * zoom_factor))
        self.canvas.create_rectangle(x1 + shadow, y1 + shadow, x2 + shadow, y2 + shadow, fill="#10161B", outline="")
        if spread:
            unit_indices = list(active_unit.get("indices", (active_index,)))
            left_item = self.items[unit_indices[0]] if unit_indices else active_item
            right_item = self.items[unit_indices[1]] if len(unit_indices) > 1 else active_item
            self._gabarit_draw_sheet_guides(self.canvas, x1, y1, single_w, page_h, item=left_item, fold_side="right")
            self._gabarit_draw_sheet_guides(self.canvas, x1 + single_w, y1, single_w, page_h, item=right_item, fold_side="left")
            self.canvas.create_line(x1 + single_w, y1 + 4, x1 + single_w, y2 - 4, fill="#697775", width=2)
        else:
            self._gabarit_draw_sheet_guides(self.canvas, x1, y1, single_w, page_h, item=active_item)

        self._gabarit_draw_zones(x1, y1, total_w, page_h)

        if scale >= 0.35 and not self._gabarit_active_zones():
            self.canvas.create_text(cx, cy, text=str(active_type), fill="#68706E", font=(theme.FONT_TITLE, max(10, int(13 * min(zoom_factor, 2.0))), "bold"), anchor="center")
            self.canvas.create_text(cx, cy + 22, text="Page prête pour le gabarit", fill="#8B9290", font=(theme.FONT_UI, max(7, int(8 * min(zoom_factor, 1.6)))), anchor="center")

        # ----- navigation page précédente / suivante -----
        # Chaque bouton suit réellement le bord de la feuille. Il reste visible tant
        # que son propre carré tient dans B ; quand le bord de page sort, il disparaît.
        arrow_gap = 14.0
        arrow_size = 46.0
        arrow_half = arrow_size / 2.0
        info_x1_for_arrows = info_x1

        def draw_page_nav_button(key: str, cx_btn: float, cy_btn: float, glyph: str) -> None:
            hovered = str(getattr(self, "_gabarit_hover_control", "")) == key
            pressed = str(getattr(self, "_gabarit_pressed_control", "")) == key
            shift_y = 2.0 if pressed else 0.0
            bx1 = cx_btn - arrow_half
            by1 = cy_btn - arrow_half + shift_y
            bx2 = cx_btn + arrow_half
            by2 = cy_btn + arrow_half + shift_y
            if pressed:
                fill, outline = "#1B2932", theme.ACCENT_BRIGHT
            elif hovered:
                fill, outline = "#314752", theme.ACCENT_BRIGHT
            else:
                fill, outline = "#263640", "#53656D"
            if not pressed:
                self.canvas.create_rectangle(bx1 + 2, by1 + 3, bx2 + 2, by2 + 3, fill="#121A20", outline="")
            self.canvas.create_rectangle(bx1, by1, bx2, by2, fill=fill, outline=outline, width=2 if hovered or pressed else 1)
            if not pressed:
                self.canvas.create_line(bx1 + 4, by1 + 3, bx2 - 4, by1 + 3, fill="#71858B" if hovered else "#485961", width=1)
            self.canvas.create_text(cx_btn, cy_btn + shift_y - 1, text=glyph, fill="#DDE8E5" if hovered or pressed else "#A6C8C2", font=(theme.FONT_UI, 23, "bold"), anchor="center")
            self._gabarit_hitboxes[key] = (cx_btn-arrow_half-4, cy_btn-arrow_half-4, cx_btn+arrow_half+4, cy_btn+arrow_half+4)

        ay = cy
        left_cx = x1 - arrow_gap - arrow_half
        right_cx = x2 + arrow_gap + arrow_half
        vertical_ok = work_top + arrow_half <= ay <= work_bottom - arrow_half
        left_ok = vertical_ok and left_cx - arrow_half >= work_left and left_cx + arrow_half <= work_right
        right_ok = vertical_ok and right_cx - arrow_half >= work_left and right_cx + arrow_half <= info_x1_for_arrows - 8.0
        if active_pos > 0 and left_ok:
            draw_page_nav_button("prev", left_cx, ay, "‹")
        if active_pos < len(units) - 1 and right_ok:
            draw_page_nav_button("next", right_cx, ay, "›")

        # ----- zoom historique, discret à gauche de B -----
        zoom_controls = getattr(self, "gabarit_zoom_controls", None)
        if zoom_controls is not None:
            try:
                zoom_controls.place(x=9, rely=0.54, anchor="w")
                zoom_controls.lift()
            except Exception:
                pass

        # ----- inspecteur contextuel : pleine hauteur, sans cadre -----
        # Le panneau conserve des polices lisibles mais adapte son rythme vertical
        # à la hauteur REELLEMENT disponible dans B. C'est indispensable avec la
        # mise à l'échelle Windows : des espacements fixes pouvaient faire sortir
        # Marges / Fond perdu alors que le panneau paraissait correct à 100 %.
        info_y1 = 0.0
        info_x2 = viewport_w - edge_gutter
        info_y2 = viewport_h
        self.canvas.create_line(info_x1, 8.0, info_x1, max(8.0, info_y2 - 8.0), fill="#465A63", width=1)
        tx = info_x1 + 16.0
        inner_right = info_x2 - 12.0
        inner_w = max(112.0, inner_right - tx)

        # Interpolation douce entre une disposition compacte (petit B / DPI élevé)
        # et la disposition aérée. Les caractères ne changent jamais de taille :
        # seuls les blancs et, très légèrement, la hauteur des commandes varient.
        room = max(0.0, min(1.0, (float(viewport_h) - 370.0) / 150.0))
        def mix(compact: float, relaxed: float) -> float:
            return compact + (relaxed - compact) * room

        top_pad = mix(10.0, 22.0)
        section_step = mix(18.0, 24.0)
        separator_step = mix(8.0, 17.0)
        page_part_step = mix(19.0, 29.0)
        scope_h = mix(28.0, 34.0)
        between_controls = mix(6.0, 14.0)
        status_h = mix(30.0, 38.0)
        after_status = mix(6.0, 18.0)
        book_control_h = mix(34.0, 42.0)
        book_gap = mix(5.0, 10.0)

        def section_label(y: float, text: str) -> float:
            self.canvas.create_text(
                tx, y, text=text, anchor="w", fill="#A8BCC0",
                font=(theme.FONT_UI, 9, "bold"),
            )
            return y + section_step

        def separator(y: float) -> float:
            self.canvas.create_line(tx, y, inner_right, y, fill="#40525B", width=1)
            return y + separator_step

        def control_box(
            key: str, y: float, h: float, *, selected: bool = False,
            x1: float | None = None, x2: float | None = None,
        ) -> tuple[float, float, float, float]:
            bx1 = tx if x1 is None else float(x1)
            bx2 = inner_right if x2 is None else float(x2)
            hovered = str(getattr(self, "_gabarit_hover_control", "")) == key
            pressed = str(getattr(self, "_gabarit_pressed_control", "")) == key
            fill = "#314752" if hovered or pressed else ("#2B4249" if selected else "#202D36")
            outline = theme.ACCENT_BRIGHT if hovered or selected else "#465963"
            self.canvas.create_rectangle(
                bx1, y, bx2, y + h, fill=fill, outline=outline,
                width=2 if hovered or selected else 1,
            )
            self._gabarit_hitboxes[key] = (bx1, y, bx2, y + h)
            return bx1, y, bx2, y + h

        y = info_y1 + top_pad
        y = section_label(y, "PAGE ACTIVE")
        title_id = self.canvas.create_text(
            tx, y, text=f"{number} — {active_type}", anchor="nw",
            fill="#F0F2F0", font=(theme.FONT_TITLE, 10, "bold"),
            width=inner_w,
        )
        bbox = self.canvas.bbox(title_id)
        y = float((bbox[3] if bbox else y + 20.0) + mix(4.0, 7.0))
        self.canvas.create_text(
            tx, y, text=part_text, anchor="nw", fill="#BFC9C7",
            font=(theme.FONT_UI, 8), width=inner_w,
        )
        y += page_part_step
        y = separator(y)

        y = section_label(y, "GABARIT")
        self.canvas.create_text(tx, y, text="Portée", anchor="w", fill="#C3CDCB", font=(theme.FONT_UI, 9, "bold"))
        y += mix(16.0, 18.0)
        page_scope = str(getattr(self, "_gabarit_scope", "page")) != "type"
        type_scope = not page_scope
        scope_gap = 4.0
        scope_mid = tx + (inner_w - scope_gap) / 2.0
        control_box("scope_page", y, scope_h, selected=page_scope, x1=tx, x2=scope_mid)
        self.canvas.create_text((tx + scope_mid) / 2.0, y + scope_h / 2.0, text="Cette page", anchor="center", fill="#F1F3F2", font=(theme.FONT_UI, 8, "bold" if page_scope else "normal"))
        type_x1 = scope_mid + scope_gap
        control_box("scope_type", y, scope_h, selected=type_scope, x1=type_x1, x2=inner_right)
        self.canvas.create_text((type_x1 + inner_right) / 2.0, y + scope_h / 2.0, text="Tout le type", anchor="center", fill="#F1F3F2", font=(theme.FONT_UI, 8, "bold" if type_scope else "normal"))
        y += scope_h + between_controls

        # Rythme visuel : le libellé Statut était légèrement trop proche du
        # sélecteur Portée. On décale Statut et TOUT ce qui le suit de 6 px
        # (environ 1,5 mm à 96 dpi), sans modifier aucun espacement interne.
        y += 6.0
        self.canvas.create_text(tx, y, text="Statut", anchor="w", fill="#C3CDCB", font=(theme.FONT_UI, 9, "bold"))
        y += mix(16.0, 18.0)
        status = self._gabarit_status(active_item)
        status_text = {"termine": "Terminé", "en_cours": "En cours", "non_commence": "Non commencé"}[status]
        status_color = {"termine": "#79B49C", "en_cours": "#C39A4A", "non_commence": "#8A969B"}[status]
        control_box("toggle_status", y, status_h)
        dot_cy = y + status_h / 2.0
        self.canvas.create_oval(tx + 10, dot_cy - 6.0, tx + 22, dot_cy + 6.0, fill=status_color, outline="")
        self.canvas.create_text(tx + 30, dot_cy, text=status_text, anchor="w", fill=status_color, font=(theme.FONT_UI, 9, "bold"))
        self.canvas.create_text(inner_right - 9, dot_cy, text="›", anchor="e", fill="#A6B7BA", font=(theme.FONT_UI, 12, "bold"))
        y += status_h + after_status
        y = separator(y)

        y = section_label(y, "LIVRE")
        fmt = self.gabarit_book_format()
        control_box("edit_format", y, book_control_h)
        self.canvas.create_text(tx + 10, y + mix(10.0, 12.0), text="Format fini", anchor="w", fill="#F0F2F0", font=(theme.FONT_UI, 9, "bold"))
        self.canvas.create_text(
            tx + 10, y + book_control_h - mix(9.0, 13.0),
            text=f"{fmt['label']} · {fmt['width_mm']:g} × {fmt['height_mm']:g} mm",
            anchor="w", fill="#B8C6C3", font=(theme.FONT_UI, 8),
        )
        self.canvas.create_text(inner_right - 9, y + book_control_h / 2.0, text="›", anchor="e", fill="#A6B7BA", font=(theme.FONT_UI, 11, "bold"))
        y += book_control_h + book_gap

        settings = self.gabarit_current_settings() or {}
        margins = dict(settings.get("margins_mm") or {})
        bleed = dict(settings.get("bleed_mm") or {})

        def compact_values(values: dict, keys: tuple[str, ...], labels: tuple[str, ...]) -> str:
            vals = [float(values.get(k, 0.0)) for k in keys]
            if vals and max(vals) - min(vals) < 0.001:
                return f"{vals[0]:g} mm"
            return " · ".join(f"{lab}{val:g}" for lab, val in zip(labels, vals))

        control_box("edit_margins", y, book_control_h)
        self.canvas.create_text(tx + 10, y + mix(10.0, 12.0), text="Marges", anchor="w", fill="#F0F2F0", font=(theme.FONT_UI, 9, "bold"))
        self.canvas.create_text(tx + 10, y + book_control_h - mix(9.0, 13.0), text=compact_values(margins, ("top", "bottom", "inside", "outside"), ("H", "B", "I", "E")), anchor="w", fill="#B8C6C3", font=(theme.FONT_UI, 8))
        self.canvas.create_text(inner_right - 9, y + book_control_h / 2.0, text="›", anchor="e", fill="#A6B7BA", font=(theme.FONT_UI, 11, "bold"))
        y += book_control_h + book_gap

        control_box("edit_bleed", y, book_control_h)
        self.canvas.create_text(tx + 10, y + mix(10.0, 12.0), text="Fond perdu", anchor="w", fill="#F0F2F0", font=(theme.FONT_UI, 9, "bold"))
        self.canvas.create_text(tx + 10, y + book_control_h - mix(9.0, 13.0), text=compact_values(bleed, ("top", "bottom", "left", "right"), ("H", "B", "G", "D")), anchor="w", fill="#D1AAAA", font=(theme.FONT_UI, 8))
        self.canvas.create_text(inner_right - 9, y + book_control_h / 2.0, text="›", anchor="e", fill="#A6B7BA", font=(theme.FONT_UI, 11, "bold"))
        y += book_control_h

        # Le poste historique reste au-dessus du Canvas, à gauche de B.
        zoom_controls = getattr(self, "gabarit_zoom_controls", None)
        if zoom_controls is not None:
            try:
                zoom_controls.place(x=9, rely=0.54, anchor="w")
                zoom_controls.lift()
            except Exception:
                pass

        # Toujours en dernier : la ligne reste lisible par-dessus une page très agrandie.
        self._gabarit_draw_context_overlay(
            units, active_pos, viewport_w, work_left=work_left, work_right=work_right,
        )
        self._gabarit_sync_zoom_widget()

        self.canvas.configure(cursor="fleur" if int(self._gabarit_zoom) > 100 and self._gabarit_point_in(self._gabarit_page_box, self.canvas.winfo_pointerx() - self.canvas.winfo_rootx(), self.canvas.winfo_pointery() - self.canvas.winfo_rooty()) else "arrow")

    def _gabarit_press(self, event):
        x, y = float(event.x), float(event.y)
        for key, box in self._gabarit_hitboxes.items():
            if self._gabarit_point_in(box, x, y):
                if key in {"prev", "next", "zoom_plus", "zoom_minus", "zoom_fit"}:
                    # Navigation et zoom s'exécutent dès l'appui. Le rendu complet
                    # peut reconstruire les hitboxes avant le relâchement : ne jamais
                    # attendre ButtonRelease pour lancer ces commandes.
                    self._gabarit_pressed_control = key
                    self._gabarit_hover_control = key
                    if key == "prev":
                        self.gabarit_navigate(-1)
                    elif key == "next":
                        self.gabarit_navigate(1)
                    elif key == "zoom_plus":
                        self.gabarit_zoom_in()
                    elif key == "zoom_minus":
                        self.gabarit_zoom_out()
                    else:
                        self.gabarit_reset_zoom()
                    try:
                        self.after(85, self._gabarit_clear_pressed_control)
                    except Exception:
                        self._gabarit_pressed_control = ""
                    return "break"
                if key == "scope_page":
                    self.gabarit_set_scope("page")
                elif key == "scope_type":
                    self.gabarit_set_scope("type")
                elif key == "toggle_status":
                    self.gabarit_toggle_finished()
                elif key == "edit_format":
                    callback = getattr(self, "on_gabarit_edit_format", None)
                    if callable(callback):
                        callback()
                elif key == "edit_margins":
                    callback = getattr(self, "on_gabarit_edit_margins", None)
                    if callable(callback):
                        callback()
                elif key == "edit_bleed":
                    callback = getattr(self, "on_gabarit_edit_bleed", None)
                    if callable(callback):
                        callback()
                return "break"
        for index, box in self._gabarit_context_hitboxes.items():
            if self._gabarit_point_in(box, x, y):
                self._gabarit_selected_zone_id = ""
                self.gabarit_select_index(index, preserve_zoom=True)
                return "break"
        for zid, box in self._gabarit_zone_handle_hitboxes.items():
            if self._gabarit_point_in(box, x, y):
                active = self._gabarit_active_item()
                zone = self._gabarit_find_zone(active, zone_id=zid) if active else None
                if zone is not None:
                    self._gabarit_selected_zone_id = zid
                    if not bool(zone.get("locked", False)):
                        self._gabarit_zone_drag = {"mode": "resize", "start": (x, y), "rect": (float(zone.get("x",0)), float(zone.get("y",0)), float(zone.get("w",.2)), float(zone.get("h",.2))), "zone": zone}
                    self._emit_gabarit_selection_changed()
                    return "break"
        for zid, box in reversed(list(self._gabarit_zone_hitboxes.items())):
            if self._gabarit_point_in(box, x, y):
                active = self._gabarit_active_item()
                zone = self._gabarit_find_zone(active, zone_id=zid) if active else None
                self._gabarit_selected_zone_id = zid
                if zone is not None and not bool(zone.get("locked", False)):
                    self._gabarit_zone_drag = {"mode": "move", "start": (x, y), "rect": (float(zone.get("x",0)), float(zone.get("y",0)), float(zone.get("w",.2)), float(zone.get("h",.2))), "zone": zone}
                self.render()
                self._emit_gabarit_selection_changed()
                return "break"
        if self._gabarit_point_in(self._gabarit_page_box, x, y):
            self._gabarit_update_zoom_anchor(x, y)
            if self._gabarit_selected_zone_id:
                self._gabarit_selected_zone_id = ""
                self.render()
                self._emit_gabarit_selection_changed()
                return "break"
            if int(getattr(self, "_gabarit_zoom", 100)) > 100:
                self._gabarit_drag_origin = (x, y)
                self._gabarit_pan_origin = (float(self._gabarit_pan_x), float(self._gabarit_pan_y))
                self.canvas.configure(cursor="fleur")
        return "break"

    def _gabarit_drag(self, event):
        if self._gabarit_zone_drag is not None and self._gabarit_page_box:
            x1, y1, x2, y2 = self._gabarit_page_box
            state = self._gabarit_zone_drag
            zone = state["zone"]
            surface_x, surface_y, pw, ph = self._gabarit_zone_surface_box(
                zone, x1, y1, max(1.0, x2 - x1), max(1.0, y2 - y1),
            )
            pw = max(1.0, pw); ph = max(1.0, ph)
            sx, sy = state["start"]
            ox, oy, ow, oh = state["rect"]
            dx = (float(event.x) - sx) / pw
            dy = (float(event.y) - sy) / ph
            snap = bool(getattr(self, "_gabarit_snap_enabled", True))
            def snap_value(value, candidates, threshold=0.012):
                if not snap:
                    return value
                best = min(candidates, key=lambda c: abs(value-c))
                return best if abs(value-best) <= threshold else value
            if state["mode"] == "resize":
                nw = max(0.05, min(1.0 - ox, ow + dx))
                nh = max(0.05, min(1.0 - oy, oh + dy))
                right = snap_value(ox + nw, [0.25, 0.5, 0.75, 1.0])
                bottom = snap_value(oy + nh, [0.25, 0.5, 0.75, 1.0])
                nw = max(0.05, min(1.0-ox, right-ox)); nh = max(0.05, min(1.0-oy, bottom-oy))
                zone.update({"x": ox, "y": oy, "w": nw, "h": nh})
            else:
                nx = max(0.0, min(1.0 - ow, ox + dx))
                ny = max(0.0, min(1.0 - oh, oy + dy))
                # accroche bords et centres de la zone à la page
                nx = snap_value(nx, [0.0, 0.25, 0.5, 0.75, max(0.0,1.0-ow)])
                ny = snap_value(ny, [0.0, 0.25, 0.5, 0.75, max(0.0,1.0-oh)])
                center_x = nx + ow/2.0; center_y = ny + oh/2.0
                if snap and abs(center_x-0.5) <= 0.012: nx = 0.5 - ow/2.0
                if snap and abs(center_y-0.5) <= 0.012: ny = 0.5 - oh/2.0
                zone.update({"x": nx, "y": ny, "w": ow, "h": oh})
            self.render()
            return "break"
        if self._gabarit_drag_origin is None or self._gabarit_pan_origin is None:
            return "break"
        dx = float(event.x) - self._gabarit_drag_origin[0]
        dy = float(event.y) - self._gabarit_drag_origin[1]
        self._gabarit_pan_x = self._gabarit_pan_origin[0] + dx
        self._gabarit_pan_y = self._gabarit_pan_origin[1] + dy
        self.render()
        return "break"

    def _gabarit_clear_pressed_control(self) -> None:
        if not str(getattr(self, "_gabarit_pressed_control", "") or ""):
            return
        self._gabarit_pressed_control = ""
        if getattr(self, "_work_mode", "") == "gabarits":
            self.render()

    def _gabarit_release(self, _event=None):
        pressed = str(getattr(self, "_gabarit_pressed_control", "") or "")
        if pressed in {"prev", "next", "zoom_plus", "zoom_minus", "zoom_fit"}:
            # L'action a déjà été exécutée à l'appui : le relâchement ne doit
            # jamais la rejouer. Il ne sert qu'à rendre l'état visuel neutre.
            self._gabarit_pressed_control = ""
            x = float(getattr(_event, "x", -9999))
            y = float(getattr(_event, "y", -9999))
            box = self._gabarit_hitboxes.get(pressed)
            self._gabarit_hover_control = pressed if self._gabarit_point_in(box, x, y) else ""
            self.render()
            return "break"
        if self._gabarit_zone_drag is not None:
            state = self._gabarit_zone_drag
            zone = state.get("zone")
            self._gabarit_zone_drag = None
            if isinstance(zone, dict):
                rect = (float(zone.get("x",0)), float(zone.get("y",0)), float(zone.get("w",.2)), float(zone.get("h",.2)))
                self._gabarit_commit_zone_rect(zone, rect)
            return "break"
        self._gabarit_drag_origin = None
        self._gabarit_pan_origin = None
        self.canvas.configure(cursor="arrow")
        return "break"

    # ------------------------------------------------------------------
    # Structure V5 : C = outils / B = zone de travail
    # ------------------------------------------------------------------


    def structure_builtin_page_type_catalog(self) -> list[dict]:
        """Catalogue Structure resserré : catalogue courant + vrais types utiles aux 3 familles."""
        result = [dict(item) for item in structure_builtin_catalog() if isinstance(item, dict)]
        seen = {str(item.get("type") or "").strip() for item in result}

        # Certains vrais types de pages existent déjà dans le catalogue éditorial
        # mais étaient encore marqués « futurs ». On ne promeut ici que ceux qui
        # appartiennent aux listes resserrées de C, jamais les éléments de gabarit.
        promoted = []
        for preset in self.STRUCTURE_PALETTE_DEFAULTS.values():
            promoted.extend(preset.get("current", ()))
            promoted.extend(preset.get("other", ()))
        for type_key in promoted:
            type_key = str(type_key or "").strip()
            if not type_key or type_key in seen or type_key == "page_blanche":
                continue
            definition = page_visual_definition(type_key)
            if isinstance(definition, dict):
                item = dict(definition)
                item["structure_builtin"] = True
                item.setdefault("custom", False)
                item.setdefault("duplicable", True)
                result.append(item)
                seen.add(type_key)

        for definition in self.STRUCTURE_EXTRA_PAGE_TYPES:
            type_key = str(definition.get("type") or "").strip()
            if type_key and type_key not in seen:
                result.append(dict(definition))
                seen.add(type_key)
        return result

    def structure_available_page_types(self) -> list[tuple[str, str, bool]]:
        protected = self.COVER_TYPES | self.BACK_COVER_TYPES | self.SECOND_COVER_TYPES | self.THIRD_COVER_TYPES
        defaults: list[tuple[str, str, bool]] = []
        seen: set[str] = set()
        for definition in self.structure_builtin_page_type_catalog():
            if not isinstance(definition, dict):
                continue
            type_key = str(definition.get("type") or "").strip()
            if not type_key or type_key in seen or type_key == "page_blanche":
                continue
            if type_key.lower() in protected:
                continue
            label = str(
                definition.get("short_label")
                or definition.get("label")
                or definition.get("title")
                or definition.get("name")
                or type_key
            ).strip() or type_key
            defaults.append((type_key, label, False))
            seen.add(type_key)

        result = list(defaults)
        data = self._data if isinstance(self._data, dict) else {}
        definitions = data.get("page_types", [])
        if isinstance(definitions, list):
            for definition in definitions:
                if not isinstance(definition, dict):
                    continue
                type_key = str(definition.get("type") or definition.get("id") or "").strip()
                if not type_key or type_key in seen:
                    continue
                if type_key.lower() in protected:
                    continue
                label = str(
                    definition.get("short_label")
                    or definition.get("label")
                    or definition.get("title")
                    or definition.get("name")
                    or type_key
                ).strip() or type_key
                result.append((type_key, label, bool(definition.get("custom", True))))
                seen.add(type_key)
        return result

    def _structure_project_type(self) -> str:
        value = str(getattr(self.project, "project_type", "") or "").strip()
        if value not in self.STRUCTURE_PALETTE_DEFAULTS:
            value = "ouvrage_structure"
        return value

    def _structure_palette_available_map(self) -> dict[str, tuple[str, bool]]:
        result: dict[str, tuple[str, bool]] = {"page_blanche": ("Page blanche", False)}
        for key, label, custom in self.structure_available_page_types():
            key = str(key or "").strip()
            if key:
                result[key] = (str(label or key), bool(custom))
        return result

    def _structure_palette_state(self, data: dict | None = None) -> dict:
        data = data if isinstance(data, dict) else (self._data if isinstance(self._data, dict) else {})
        project_type = self._structure_project_type()
        defaults = self.STRUCTURE_PALETTE_DEFAULTS.get(project_type, self.STRUCTURE_PALETTE_DEFAULTS["ouvrage_structure"])
        available = self._structure_palette_available_map()
        raw = data.get(self.STRUCTURE_PALETTE_KEY, {})
        compatible = isinstance(raw, dict) and str(raw.get("project_type") or "") == project_type

        hidden = {str(v or "").strip() for v in (raw.get("hidden", []) if compatible else []) if str(v or "").strip()}
        current_source = raw.get("current", []) if compatible else defaults.get("current", ())
        other_source = raw.get("other", []) if compatible else defaults.get("other", ())

        current: list[str] = []
        other: list[str] = []
        seen: set[str] = set()
        for value in current_source:
            key = str(value or "").strip()
            if key in available and key not in hidden and key not in seen:
                current.append(key); seen.add(key)
        for value in other_source:
            key = str(value or "").strip()
            if key in available and key not in hidden and key not in seen:
                other.append(key); seen.add(key)

        # Un type créé par l'utilisateur reste toujours visible et arrive dans
        # « Autres types » tant qu'il n'a pas été déplacé.
        for key, (_label, custom) in available.items():
            if custom and key not in seen and key not in hidden:
                other.append(key); seen.add(key)

        return {
            "project_type": project_type,
            "current": current,
            "other": other,
            "hidden": sorted(hidden),
        }

    def structure_page_type_palette(self) -> dict:
        state = self._structure_palette_state()
        available = self._structure_palette_available_map()
        def rows(keys):
            return [
                (key, available[key][0], available[key][1])
                for key in keys if key in available
            ]
        return {
            **state,
            "current_types": rows(state["current"]),
            "other_types": rows(state["other"]),
        }

    def _structure_save_palette_state(self, state: dict, *, status: str) -> bool:
        if self.project is None:
            return False
        try:
            data = self.project.load_mockup()
        except Exception:
            data = deepcopy(self._data)
        if not isinstance(data, dict):
            data = {}
        data[self.STRUCTURE_PALETTE_KEY] = {
            "project_type": self._structure_project_type(),
            "current": [str(v) for v in state.get("current", []) if str(v)],
            "other": [str(v) for v in state.get("other", []) if str(v)],
            "hidden": [str(v) for v in state.get("hidden", []) if str(v)],
        }
        saved = self.project.save_mockup(data)
        if not isinstance(saved, dict):
            saved = data
        self._data = deepcopy(saved)
        self._history_record_saved(saved)
        self.status_var.set(status)
        try:
            self.event_generate("<<StructurePaletteChanged>>", when="tail")
        except Exception:
            pass
        if self.on_change is not None:
            self.on_change()
        return True

    def structure_move_page_type(self, type_key: str, destination: str, index: int | None = None) -> bool:
        type_key = str(type_key or "").strip()
        destination = "current" if str(destination or "") == "current" else "other"
        available = self._structure_palette_available_map()
        if not type_key or type_key not in available:
            return False
        state = self._structure_palette_state()
        current = [key for key in state["current"] if key != type_key]
        other = [key for key in state["other"] if key != type_key]
        target = current if destination == "current" else other
        try:
            position = len(target) if index is None else max(0, min(len(target), int(index)))
        except (TypeError, ValueError):
            position = len(target)
        target.insert(position, type_key)
        state["current"] = current
        state["other"] = other
        state["hidden"] = [key for key in state.get("hidden", []) if key != type_key]
        label = available[type_key][0]
        zone = "Courants" if destination == "current" else "Autres types"
        return self._structure_save_palette_state(state, status=f"{label}  •  déplacé dans {zone}")

    def _structure_type_usage(self, type_key: str, data: dict | None = None) -> tuple[int, int]:
        data = data if isinstance(data, dict) else (self._data if isinstance(self._data, dict) else {})
        type_key = str(type_key or "").strip()
        pages = sum(1 for item in data.get("items", []) if isinstance(item, dict) and self._type_of(item) == type_key)
        rules = 0
        auto_rules = data.get("page_auto_type_rules", {})
        if isinstance(auto_rules, dict):
            if type_key in auto_rules:
                rules += 1
            for value in auto_rules.values():
                if isinstance(value, dict) and type_key in {str(value.get("before") or ""), str(value.get("after") or "")}:
                    rules += 1
        side_rules = data.get("recto_verso_type_rules", {})
        if isinstance(side_rules, dict) and type_key in side_rules:
            rules += 1
        double_rules = data.get("double_page_type_rules", {})
        if isinstance(double_rules, dict) and bool(double_rules.get(type_key)):
            rules += 1
        return pages, rules

    def structure_delete_page_type(self, type_key: str) -> bool:
        type_key = str(type_key or "").strip()
        if not type_key:
            self.status_var.set("Sélectionnez d’abord un type dans C.")
            return False
        available = self._structure_palette_available_map()
        if type_key not in available:
            return False
        try:
            data = self.project.load_mockup() if self.project is not None else deepcopy(self._data)
        except Exception:
            data = deepcopy(self._data)
        if not isinstance(data, dict):
            data = {}
        pages, rules = self._structure_type_usage(type_key, data)
        label, custom = available[type_key]
        if pages or rules:
            detail = []
            if pages:
                detail.append(f"{pages} page{'s' if pages > 1 else ''}")
            if rules:
                detail.append(f"{rules} règle{'s' if rules > 1 else ''}")
            self.status_var.set(f"Impossible de supprimer « {label} »  •  utilisé par " + " et ".join(detail))
            return False

        state = self._structure_palette_state(data)
        state["current"] = [key for key in state["current"] if key != type_key]
        state["other"] = [key for key in state["other"] if key != type_key]
        if custom:
            definitions = data.get("page_types", [])
            if isinstance(definitions, list):
                data["page_types"] = [
                    definition for definition in definitions
                    if not (isinstance(definition, dict) and str(definition.get("type") or definition.get("id") or "").strip() == type_key)
                ]
        else:
            hidden = {str(v or "").strip() for v in state.get("hidden", []) if str(v or "").strip()}
            hidden.add(type_key)
            state["hidden"] = sorted(hidden)

        data[self.STRUCTURE_PALETTE_KEY] = {
            "project_type": self._structure_project_type(),
            "current": state["current"],
            "other": state["other"],
            "hidden": state.get("hidden", []),
        }
        if self.project is None:
            return False
        saved = self.project.save_mockup(data)
        if not isinstance(saved, dict):
            saved = data
        self._data = deepcopy(saved)
        self._history_record_saved(saved)
        self.status_var.set(f"Type supprimé de C  •  {label}")
        try:
            self.event_generate("<<StructurePaletteChanged>>", when="tail")
        except Exception:
            pass
        if self.on_change is not None:
            self.on_change()
        return True

    def structure_reset_page_type_palette(self) -> bool:
        if self.project is None:
            return False
        defaults = self.STRUCTURE_PALETTE_DEFAULTS.get(
            self._structure_project_type(), self.STRUCTURE_PALETTE_DEFAULTS["ouvrage_structure"]
        )
        state = {
            "current": list(defaults.get("current", ())),
            "other": list(defaults.get("other", ())),
            "hidden": [],
        }
        # Les types personnels déjà créés sont conservés et rangés dans Autres.
        available = self._structure_palette_available_map()
        for key, (_label, custom) in available.items():
            if custom and key not in state["current"] and key not in state["other"]:
                state["other"].append(key)
        return self._structure_save_palette_state(state, status="Organisation de C réinitialisée pour ce type de livre.")

    def _structure_type_definition(self, type_key: str) -> dict:
        type_key = str(type_key or "").strip()
        if not type_key:
            return {
                "type": "",
                "label": "Sans type",
                "short_label": "Sans type",
                "visual": "custom",
                "custom": False,
                "untyped": True,
                "duplicable": True,
            }
        for definition in self.structure_builtin_page_type_catalog():
            if isinstance(definition, dict) and str(definition.get("type") or "").strip() == type_key:
                return dict(definition)
        data = self._data if isinstance(self._data, dict) else {}
        definitions = data.get("page_types", [])
        if isinstance(definitions, list):
            for definition in definitions:
                if isinstance(definition, dict) and str(
                    definition.get("type") or definition.get("id") or ""
                ).strip() == type_key:
                    return dict(definition)
        return {"type": type_key, "label": type_key.replace("_", " ").strip().capitalize()}

    def structure_create_custom_type(self, definition) -> tuple[str, str] | None:
        if self.project is None:
            return None

        if isinstance(definition, str):
            definition = {"name": definition}
        if not isinstance(definition, dict):
            return None

        name = str(
            definition.get("name") or definition.get("label") or definition.get("title") or ""
        ).strip()
        if not name:
            self.status_var.set("Donnez un nom au nouveau type.")
            return None

        short_label = str(definition.get("short_label") or definition.get("label") or name).strip() or name
        existing = self.structure_available_page_types()
        for type_key, label, _custom in existing:
            if label.casefold() == short_label.casefold() or str(
                self._structure_type_definition(type_key).get("name") or ""
            ).casefold() == name.casefold():
                self.status_var.set(f"Type déjà disponible  •  {label}")
                return None

        type_key = f"personnalisee_{uuid4().hex[:10]}"
        try:
            data = self.project.load_mockup()
        except Exception:
            data = deepcopy(self._data)
        if not isinstance(data, dict):
            data = {}

        definitions = data.setdefault("page_types", [])
        if not isinstance(definitions, list):
            definitions = []
            data["page_types"] = definitions

        preview_image_value = str(definition.get("preview_image") or "").strip()
        preview_image_rel = ""
        if preview_image_value:
            source = Path(preview_image_value)
            if source.is_file():
                try:
                    project_root = Path(getattr(self.project, "root", "") or "")
                    target_dir = project_root / "ressources" / "types_de_pages"
                    target_dir.mkdir(parents=True, exist_ok=True)
                    target_name = f"{type_key}{source.suffix.lower() or '.png'}"
                    target_path = target_dir / target_name
                    shutil.copy2(source, target_path)
                    preview_image_rel = str(target_path.relative_to(project_root)).replace("\\", "/")
                except Exception:
                    preview_image_rel = preview_image_value
            else:
                preview_image_rel = preview_image_value

        saved = {
            "type": type_key,
            "label": name,
            "title": name,
            "name": name,
            "short_label": short_label,
            "visual": str(definition.get("visual") or "custom"),
            "side": str(definition.get("side") or "libre"),
            "blank_before": bool(definition.get("blank_before", False)),
            "blank_after": bool(definition.get("blank_after", False)),
            "duplicable": bool(definition.get("duplicable", True)),
            "group": self.DEFAULT_GROUP_ID,
            "custom": True,
            "preview_image": preview_image_rel,
        }
        definitions.append(saved)
        saved = self.project.save_mockup(data)
        if not isinstance(saved, dict):
            saved = data
        self._data = deepcopy(saved)
        self._history_record_saved(saved)
        if self.on_change is not None:
            self.on_change()
        self.status_var.set(f"Nouveau type  •  {short_label}")
        try:
            self.event_generate("<<StructurePaletteChanged>>", when="tail")
        except Exception:
            pass
        return type_key, short_label

    def structure_auto_source_allowed(self, item: dict | None) -> bool:
        if not isinstance(item, dict):
            return False
        return not self._is_locked_page(item) and not self._is_automatic_page(item)

    def _structure_clear_rule_target(self) -> None:
        self._structure_rule_target = ""
        self._structure_rule_remove_pending = ""
        self._structure_update_common_rule_actions()

    def _structure_set_rule_target(self, code: str) -> None:
        code = str(code or "").strip().upper()
        new_target = code if code in {"AV", "AP", "R", "V", "2P"} else ""
        if new_target != str(getattr(self, "_structure_rule_target", "") or ""):
            self._structure_rule_remove_pending = ""
        self._structure_rule_target = new_target
        self._structure_update_common_rule_actions()

    def _structure_target_rule_context(self) -> dict:
        code = str(getattr(self, "_structure_rule_target", "") or "").upper()
        indices = self._selected_source_indices()
        source = self.items[indices[0]] if len(indices) == 1 else None
        if source is None or code not in {"AV", "AP", "R", "V", "2P"}:
            return {"code": code, "source": source, "has_rule": False, "excluded": False}
        source_type = self._type_of(source)
        has_rule = False
        excluded = False
        if code in {"AV", "AP"}:
            position = "before" if code == "AV" else "after"
            has_rule = bool(self.structure_get_page_auto_type_rule(source_type, position))
            excluded = has_rule and self._page_auto_override_value(source, position) == "__none__"
        elif code in {"R", "V"}:
            side = "recto" if code == "R" else "verso"
            has_rule = self.structure_get_recto_verso_type_rule(source_type) == side
            excluded = has_rule and self._recto_verso_override_value(source) == "__none__"
        elif code == "2P":
            has_rule = bool(self.structure_get_double_page_type_rule(source_type))
            excluded = has_rule and self._double_page_override_value(source) == "__none__"
        return {"code": code, "source": source, "source_type": source_type, "has_rule": has_rule, "excluded": excluded}

    def _structure_update_common_rule_actions(self) -> None:
        panel = getattr(self, "structure_rule_action_panel", None)
        badge = getattr(self, "structure_rule_target_badge", None)
        exception_btn = getattr(self, "structure_rule_exception_btn", None)
        remove_btn = getattr(self, "structure_rule_remove_btn", None)
        if panel is None or badge is None or exception_btn is None or remove_btn is None:
            return
        context = self._structure_target_rule_context()
        code = str(context.get("code") or "")
        active = bool(code)
        has_rule = bool(context.get("has_rule"))
        excluded = bool(context.get("excluded"))
        try:
            panel.configure(
                highlightthickness=2 if active else 1,
                highlightbackground="#C39A4A" if active else "#385264",
            )
            badge.configure(
                text=code or "—",
                bg="#6E5B32" if active else "#162A38",
                fg="#FFF0C4" if active else "#7F9099",
            )
            exception_btn.configure(
                state="normal" if has_rule else "disabled",
                text="Réintégrer" if has_rule and excluded else "Exception",
            )
            pending_key = str(getattr(self, "_structure_rule_remove_pending", "") or "")
            current_key = f"{code}:{context.get('source_type', '')}" if has_rule else ""
            pending = bool(has_rule and pending_key == current_key)
            remove_btn.configure(
                state="normal" if has_rule else "disabled",
                text="Confirmer" if pending else "Retirer règle",
                bg="#4A2C2A" if pending else "#162A38",
                fg="#FFF0F0" if pending else "#F2F3F1",
            )
            if not has_rule:
                self._structure_rule_remove_pending = ""
        except Exception:
            pass

    def structure_select_page_auto_rule(self, position: str) -> bool:
        position = str(position or "").strip().lower()
        code = "AV" if position == "before" else "AP" if position == "after" else ""
        if not code:
            return False
        self._structure_set_rule_target(code)
        ok = self.structure_begin_page_auto_rule(position)
        if not ok:
            self._structure_clear_rule_target()
        return ok

    def structure_select_recto_verso_rule(self, side: str) -> bool:
        if getattr(self, "_structure_pending_kind", None):
            self.structure_cancel_tool()
        side = str(side or "").strip().lower()
        code = "R" if side == "recto" else "V" if side == "verso" else ""
        if not code:
            return False
        indices = self._selected_source_indices()
        source = self.items[indices[0]] if len(indices) == 1 else None
        if source is None:
            return False
        self._structure_set_rule_target(code)
        current = self.structure_get_recto_verso_type_rule(self._type_of(source))
        # Si cette règle existe déjà, le clic la cible seulement : il ne doit
        # surtout pas réintégrer automatiquement une occurrence en exception.
        if current == side:
            self.status_var.set(f"Règle {code} ciblée  •  Exception / Annuler disponibles")
            self._structure_update_recto_verso_visuals()
            return True
        return self.structure_toggle_recto_verso_rule(side)

    def structure_select_double_page_rule(self) -> bool:
        if getattr(self, "_structure_pending_kind", None):
            self.structure_cancel_tool()
        indices = self._selected_source_indices()
        if len(indices) == 2:
            self._structure_rule_target = ""
            self._structure_rule_remove_pending = ""
            return self.structure_toggle_selected_double_page_pair()
        source = self.items[indices[0]] if len(indices) == 1 else None
        if source is None:
            self.status_var.set("2P : sélectionnez une page, ou exactement deux pages voisines à souder.")
            return False
        if self._double_page_pair_id(source):
            self.status_var.set("Cette page appartient déjà à une double page soudée. Sélectionnez les deux pages pour la dissocier.")
            return False
        self._structure_set_rule_target("2P")
        if self.structure_get_double_page_type_rule(self._type_of(source)):
            self.status_var.set("Règle 2P ciblée  •  Exception / Annuler disponibles")
            self._structure_update_double_page_visuals()
            return True
        return self.structure_apply_double_page_rule()

    def structure_toggle_target_rule_exception(self) -> bool:
        if getattr(self, "_structure_pending_kind", None):
            self.structure_cancel_tool()
        self._structure_rule_remove_pending = ""
        context = self._structure_target_rule_context()
        if not context.get("has_rule"):
            return False
        code = str(context.get("code") or "")
        if code in {"AV", "AP"}:
            position = "before" if code == "AV" else "after"
            if context.get("excluded"):
                ok = self.structure_reset_selected_page_auto_override(position)
            else:
                ok = self.structure_set_selected_page_auto(position, "", scope="local")
            self.structure_cancel_page_auto_mode(silent=True)
        elif code in {"R", "V"}:
            ok = self.structure_toggle_recto_verso_exception()
        elif code == "2P":
            ok = self.structure_toggle_double_page_exception()
        else:
            return False
        self._structure_set_rule_target(code)
        self._structure_update_common_rule_actions()
        return bool(ok)

    def structure_remove_target_rule(self) -> bool:
        if getattr(self, "_structure_pending_kind", None):
            self.structure_cancel_tool()
        context = self._structure_target_rule_context()
        if not context.get("has_rule"):
            self._structure_rule_remove_pending = ""
            self._structure_update_common_rule_actions()
            return False

        code = str(context.get("code") or "")
        source_type = str(context.get("source_type") or "")
        definition = self._structure_type_definition(source_type)
        source_label = str(
            definition.get("short_label")
            or definition.get("label")
            or source_type.replace("_", " ").strip().capitalize()
            or "ce type"
        )
        pending_key = f"{code}:{source_type}"

        # Même principe que Supprimer/Dupliquer :
        # 1er clic = armement visuel ; 2e clic = exécution.
        if str(getattr(self, "_structure_rule_remove_pending", "") or "") != pending_key:
            self._structure_rule_remove_pending = pending_key
            self._structure_update_common_rule_actions()
            self.status_var.set(
                f"Retirer {code} pour tous les {source_label}  •  cliquez une seconde fois pour confirmer"
            )
            return False

        self._structure_rule_remove_pending = ""

        if code in {"AV", "AP"}:
            position = "before" if code == "AV" else "after"
            ok = self.structure_remove_page_auto_type_rule(source_type, position)
            self.structure_cancel_page_auto_mode(silent=True)
        elif code in {"R", "V"}:
            ok = self.structure_remove_recto_verso_rule()
        elif code == "2P":
            ok = self.structure_remove_double_page_rule()
        else:
            return False

        if ok:
            self.status_var.set(f"Règle {code} retirée pour tous les {source_label}.")
        self._structure_update_common_rule_actions()
        return bool(ok)

    def structure_double_page_source_allowed(self, item: dict | None) -> bool:
        if not isinstance(item, dict):
            return False
        return not self._is_locked_page(item) and not self._is_automatic_page(item) and bool(self._type_of(item))

    def structure_double_page_type_rules(self) -> dict[str, bool]:
        """Règles générales Double page par type ; absence = page simple."""
        data = self._data if isinstance(self._data, dict) else {}
        raw = data.get("double_page_type_rules", {})
        result: dict[str, bool] = {}
        if isinstance(raw, dict):
            for source_type, enabled in raw.items():
                source = str(source_type or "").strip().lower()
                if source and bool(enabled):
                    result[source] = True
        return result

    def structure_get_double_page_type_rule(self, source_type: str) -> bool:
        source = str(source_type or "").strip().lower()
        return bool(self.structure_double_page_type_rules().get(source, False))

    def _double_page_override_value(self, item: dict | None):
        if not isinstance(item, dict):
            return None
        if "double_page_override" in item:
            return item.get("double_page_override")
        return None

    def _effective_double_page_rule(self, item: dict | None) -> bool:
        if not isinstance(item, dict) or self._is_automatic_page(item) or self._is_locked_page(item):
            return False
        # Une page soudée possède déjà sa seconde moitié comme vraie page voisine.
        # Une règle 2P par type ne doit jamais la faire occuper deux positions en plus.
        if self._double_page_pair_id(item):
            return False
        if not self.structure_get_double_page_type_rule(self._type_of(item)):
            return False
        return self._double_page_override_value(item) != "__none__"

    @staticmethod
    def _double_page_pair_id(item: dict | None) -> str:
        return str(item.get("double_page_pair_id") or "").strip() if isinstance(item, dict) else ""

    @staticmethod
    def _double_page_pair_role(item: dict | None) -> str:
        role = str(item.get("double_page_pair_role") or "").strip().lower() if isinstance(item, dict) else ""
        return role if role in {"left", "right"} else ""

    @staticmethod
    def _double_page_pair_peer_id(item: dict | None) -> str:
        return str(item.get("double_page_pair_peer_id") or "").strip() if isinstance(item, dict) else ""

    @staticmethod
    def _clear_double_page_pair_metadata(item: dict | None) -> None:
        if not isinstance(item, dict):
            return
        for key in (
            "double_page_pair_id", "double_page_pair_role", "double_page_pair_peer_id",
            "double_page_pair_conflict",
        ):
            item.pop(key, None)

    def _double_page_pair_members(self, pair_id: str) -> list[tuple[int, dict]]:
        pair_id = str(pair_id or "").strip()
        if not pair_id:
            return []
        return [
            (index, item) for index, item in enumerate(self.items)
            if not self._is_automatic_page(item) and self._double_page_pair_id(item) == pair_id
        ]

    def _double_page_pair_peer(self, item: dict | None) -> dict | None:
        pair_id = self._double_page_pair_id(item)
        peer_id = self._double_page_pair_peer_id(item)
        if not pair_id or not peer_id:
            return None
        return next(
            (
                candidate for candidate in self.items
                if not self._is_automatic_page(candidate)
                and str(candidate.get("id") or "").strip() == peer_id
                and self._double_page_pair_id(candidate) == pair_id
            ),
            None,
        )

    def _valid_double_page_pair_members(self, pair_id: str) -> tuple[dict, dict] | None:
        members = self._double_page_pair_members(pair_id)
        if len(members) != 2:
            return None
        members.sort(key=lambda row: row[0])
        left, right = members[0][1], members[1][1]
        if self._item_group_id(left) != self._item_group_id(right):
            return None
        base_group = [
            candidate for candidate in self.items
            if not self._is_automatic_page(candidate) and self._item_group_id(candidate) == self._item_group_id(left)
        ]
        try:
            lp = base_group.index(left)
            rp = base_group.index(right)
        except ValueError:
            return None
        if rp != lp + 1:
            return None
        if self._double_page_pair_role(left) != "left" or self._double_page_pair_role(right) != "right":
            return None
        if self._double_page_pair_peer_id(left) != str(right.get("id") or "").strip():
            return None
        if self._double_page_pair_peer_id(right) != str(left.get("id") or "").strip():
            return None
        return left, right

    def _sanitize_double_page_pairs(self, base_items: list[dict] | None = None) -> bool:
        """Maintient l'invariant : une paire = deux pages manuelles voisines, même partie."""
        pages = list(base_items) if isinstance(base_items, list) else [
            item for item in self.items if not self._is_automatic_page(item)
        ]
        changed = False
        by_pair: dict[str, list[dict]] = {}
        for item in pages:
            pair_id = self._double_page_pair_id(item)
            if pair_id:
                by_pair.setdefault(pair_id, []).append(item)

        for pair_id, members in by_pair.items():
            valid = len(members) == 2
            if valid:
                ordered = [item for item in pages if item in members]
                left, right = ordered[0], ordered[1]
                same_group = self._item_group_id(left) == self._item_group_id(right)
                group_pages = [item for item in pages if self._item_group_id(item) == self._item_group_id(left)]
                try:
                    adjacent = group_pages.index(right) == group_pages.index(left) + 1
                except ValueError:
                    adjacent = False
                valid = same_group and adjacent and not any(
                    self._is_locked_page(item) or self._is_automatic_page(item) for item in (left, right)
                )
            if not valid:
                for item in members:
                    if self._double_page_pair_id(item):
                        self._clear_double_page_pair_metadata(item)
                        changed = True
                continue

            left, right = [item for item in pages if item in members]
            expected = (
                (left, "left", right),
                (right, "right", left),
            )
            for item, role, peer in expected:
                peer_id = str(peer.get("id") or "").strip()
                if self._double_page_pair_role(item) != role:
                    item["double_page_pair_role"] = role
                    changed = True
                if self._double_page_pair_peer_id(item) != peer_id:
                    item["double_page_pair_peer_id"] = peer_id
                    changed = True
                item.pop("double_page_pair_conflict", None)
        return changed

    def _selected_double_page_pair_context(self) -> dict:
        indices = self._selected_source_indices()
        if len(indices) != 2:
            return {"valid": False, "reason": "Sélectionnez exactement deux pages."}
        indices = sorted(indices)
        left, right = self.items[indices[0]], self.items[indices[1]]
        if any(self._is_locked_page(item) or self._is_automatic_page(item) for item in (left, right)):
            return {"valid": False, "reason": "Les pages automatiques et les couvertures ne peuvent pas être soudées."}
        if self._item_group_id(left) != self._item_group_id(right):
            return {"valid": False, "reason": "Les deux pages doivent appartenir à la même partie."}
        group_sources = [
            item for item in self.items
            if not self._is_automatic_page(item) and self._item_group_id(item) == self._item_group_id(left)
        ]
        try:
            adjacent = group_sources.index(right) == group_sources.index(left) + 1
        except ValueError:
            adjacent = False
        if not adjacent:
            return {"valid": False, "reason": "Les deux pages doivent être voisines dans le squelette."}

        left_pair = self._double_page_pair_id(left)
        right_pair = self._double_page_pair_id(right)
        if left_pair or right_pair:
            if left_pair and left_pair == right_pair and self._valid_double_page_pair_members(left_pair):
                return {"valid": True, "action": "unpair", "left": left, "right": right, "pair_id": left_pair}
            return {"valid": False, "reason": "Une des pages appartient déjà à une autre double page."}

        if any(
            self.structure_get_double_page_type_rule(self._type_of(item))
            and self._double_page_override_value(item) != "__none__"
            for item in (left, right)
        ):
            return {"valid": False, "reason": "Une des pages utilise déjà la règle 2P par type. Désactivez-la ou créez une exception d’abord."}

        # Une double page soudée doit rester physiquement contiguë : aucune AV/AP
        # ne peut être exigée entre les deux pages.
        if self._structure_page_auto_type(left, "after") or self._structure_page_auto_type(right, "before"):
            return {"valid": False, "reason": "Une règle AV/AP exige une page entre ces deux pages. Créez une exception avant de les souder."}

        left_side = self._effective_recto_verso_rule(left)
        right_side = self._effective_recto_verso_rule(right)
        if left_side == "recto":
            return {"valid": False, "reason": "La première page de la double page doit être Verso, pas Recto."}
        if right_side == "verso":
            return {"valid": False, "reason": "La seconde page de la double page doit être Recto, pas Verso."}

        return {"valid": True, "action": "pair", "left": left, "right": right, "pair_id": ""}

    def structure_toggle_selected_double_page_pair(self) -> bool:
        context = self._selected_double_page_pair_context()
        if not context.get("valid"):
            self._structure_double_pair_pending = None
            self._structure_update_double_page_visuals()
            self.status_var.set(str(context.get("reason") or "Impossible de créer cette double page."))
            return False

        left = context["left"]
        right = context["right"]
        left_id = str(left.get("id") or "").strip()
        right_id = str(right.get("id") or "").strip()
        action = str(context.get("action") or "pair")
        pending_key = f"{action}:{left_id}:{right_id}"
        pending = getattr(self, "_structure_double_pair_pending", None)
        if not isinstance(pending, dict) or str(pending.get("key") or "") != pending_key:
            self._structure_double_pair_pending = {"key": pending_key, "action": action, "ids": [left_id, right_id]}
            self._structure_update_double_page_visuals()
            if action == "unpair":
                self.status_var.set("Dissocier cette double page  •  cliquez une seconde fois sur Confirmer")
            else:
                self.status_var.set("Souder ces deux pages en double page  •  cliquez une seconde fois sur Confirmer")
            return False

        self._structure_double_pair_pending = None
        selection_snapshot = self._structure_selection_snapshot()
        if action == "unpair":
            self._clear_double_page_pair_metadata(left)
            self._clear_double_page_pair_metadata(right)
            message = "Double page dissociée : les deux pages redeviennent indépendantes."
        else:
            pair_id = f"DP-{uuid4().hex[:12].upper()}"
            left["double_page_pair_id"] = pair_id
            left["double_page_pair_role"] = "left"
            left["double_page_pair_peer_id"] = right_id
            left.pop("double_page_pair_conflict", None)
            right["double_page_pair_id"] = pair_id
            right["double_page_pair_role"] = "right"
            right["double_page_pair_peer_id"] = left_id
            right.pop("double_page_pair_conflict", None)
            message = "Double page créée : les deux pages sont soudées Verso | Recto."

        self._sync_structural_automatic_pages()
        self._save_order()
        self._structure_restore_selection_snapshot(selection_snapshot)
        self.render()
        self.status_var.set(message)
        return True

    def _rewire_cloned_double_page_pairs(self, originals: list[dict], clones: list[dict]) -> None:
        """Dupliquer deux pages soudées conserve leur paire sans réutiliser les anciens ID."""
        if len(originals) != len(clones):
            for clone in clones:
                self._clear_double_page_pair_metadata(clone)
            return
        original_by_id = {str(item.get("id") or "").strip(): item for item in originals}
        clone_by_original_id = {
            str(original.get("id") or "").strip(): clone
            for original, clone in zip(originals, clones)
        }
        processed: set[str] = set()
        for original in originals:
            pair_id = self._double_page_pair_id(original)
            if not pair_id or pair_id in processed:
                if not pair_id:
                    self._clear_double_page_pair_metadata(clone_by_original_id.get(str(original.get("id") or "")))
                continue
            processed.add(pair_id)
            members = [item for item in originals if self._double_page_pair_id(item) == pair_id]
            if len(members) != 2:
                for member in members:
                    self._clear_double_page_pair_metadata(clone_by_original_id.get(str(member.get("id") or "")))
                continue
            left_original = next((item for item in members if self._double_page_pair_role(item) == "left"), members[0])
            right_original = next((item for item in members if item is not left_original), members[-1])
            left_clone = clone_by_original_id.get(str(left_original.get("id") or ""))
            right_clone = clone_by_original_id.get(str(right_original.get("id") or ""))
            if left_clone is None or right_clone is None:
                for member in members:
                    self._clear_double_page_pair_metadata(clone_by_original_id.get(str(member.get("id") or "")))
                continue
            new_pair_id = f"DP-{uuid4().hex[:12].upper()}"
            left_clone["double_page_pair_id"] = new_pair_id
            left_clone["double_page_pair_role"] = "left"
            left_clone["double_page_pair_peer_id"] = str(right_clone.get("id") or "")
            left_clone.pop("double_page_pair_conflict", None)
            right_clone["double_page_pair_id"] = new_pair_id
            right_clone["double_page_pair_role"] = "right"
            right_clone["double_page_pair_peer_id"] = str(left_clone.get("id") or "")
            right_clone.pop("double_page_pair_conflict", None)

    def structure_apply_double_page_rule(self) -> bool:
        indices = self._selected_source_indices()
        if len(indices) != 1:
            self.status_var.set("Double page : sélectionnez une seule page dans B.")
            return False
        source = self.items[indices[0]]
        if self._double_page_pair_id(source):
            self.status_var.set("Cette page appartient déjà à une double page soudée. Sélectionnez les deux pages pour la dissocier.")
            return False
        if not self.structure_double_page_source_allowed(source):
            self.status_var.set("Cette page ne peut pas devenir une double page.")
            return False
        source_type = self._type_of(source)
        if self.structure_get_recto_verso_type_rule(source_type) == "recto":
            self.status_var.set("Double page incompatible avec une règle Recto : une double page commence à gauche.")
            return False

        data = deepcopy(self._data) if isinstance(self._data, dict) else {}
        if self.project is not None:
            try:
                loaded = self.project.load_mockup()
                if isinstance(loaded, dict):
                    data = loaded
            except Exception:
                pass
        raw = data.get("double_page_type_rules", {})
        rules = dict(raw) if isinstance(raw, dict) else {}
        had_rule = bool(rules.get(source_type, False))
        rules[source_type] = True
        data["double_page_type_rules"] = rules

        for item in self.items:
            if self._is_automatic_page(item) or self._type_of(item) != source_type:
                continue
            if self._double_page_pair_id(item):
                item["double_page_override"] = "__none__"
            elif not had_rule:
                item.pop("double_page_override", None)
            item.pop("double_page_conflict", None)
        if isinstance(data.get("items"), list):
            for item in data["items"]:
                if not isinstance(item, dict) or self._is_automatic_page(item) or self._type_of(item) != source_type:
                    continue
                if self._double_page_pair_id(item):
                    item["double_page_override"] = "__none__"
                elif not had_rule:
                    item.pop("double_page_override", None)
                item.pop("double_page_conflict", None)

        source.pop("double_page_override", None)
        self._data = data
        if self.project is not None:
            self.project.save_mockup(data)
        self._sync_structural_automatic_pages()
        self._save_order()
        self._structure_set_rule_target("2P")
        self.status_var.set("Double page appliquée à ce type.")
        self.render()
        return True

    def structure_toggle_double_page_exception(self) -> bool:
        indices = self._selected_source_indices()
        if len(indices) != 1:
            return False
        source = self.items[indices[0]]
        source_type = self._type_of(source)
        if not self.structure_get_double_page_type_rule(source_type):
            self.status_var.set("Aucune règle Double page à désolidariser.")
            return False
        if self._double_page_override_value(source) == "__none__":
            source.pop("double_page_override", None)
            message = "Page réintégrée à la règle Double page."
        else:
            source["double_page_override"] = "__none__"
            message = "Cette page est une exception Double page."
        self._sync_structural_automatic_pages()
        self._save_order()
        self.status_var.set(message)
        self.render()
        return True

    def structure_remove_double_page_rule(self) -> bool:
        indices = self._selected_source_indices()
        if len(indices) != 1:
            return False
        source = self.items[indices[0]]
        source_type = self._type_of(source)
        if not self.structure_get_double_page_type_rule(source_type):
            return False
        data = deepcopy(self._data) if isinstance(self._data, dict) else {}
        if self.project is not None:
            try:
                loaded = self.project.load_mockup()
                if isinstance(loaded, dict):
                    data = loaded
            except Exception:
                pass
        raw = data.get("double_page_type_rules", {})
        rules = dict(raw) if isinstance(raw, dict) else {}
        rules.pop(source_type, None)
        data["double_page_type_rules"] = rules
        for item in self.items:
            if self._is_automatic_page(item) or self._type_of(item) != source_type:
                continue
            item.pop("double_page_override", None)
            item.pop("double_page_conflict", None)
        if isinstance(data.get("items"), list):
            for item in data["items"]:
                if not isinstance(item, dict) or self._is_automatic_page(item) or self._type_of(item) != source_type:
                    continue
                item.pop("double_page_override", None)
                item.pop("double_page_conflict", None)
        self._data = data
        if self.project is not None:
            self.project.save_mockup(data)
        self._sync_structural_automatic_pages()
        self._save_order()
        self.status_var.set("Règle Double page annulée pour ce type.")
        self.render()
        return True

    def _structure_update_double_page_visuals(self) -> None:
        button = getattr(self, "structure_double_page_btn", None)
        if button is None:
            return
        indices = self._selected_source_indices()
        pending = getattr(self, "_structure_double_pair_pending", None)
        if len(indices) == 2:
            context = self._selected_double_page_pair_context()
            allowed = bool(context.get("valid"))
            action = str(context.get("action") or "")
            ids = [str(self.items[i].get("id") or "").strip() for i in sorted(indices)]
            pending_key = f"{action}:{ids[0]}:{ids[1]}" if action and len(ids) == 2 else ""
            armed = bool(isinstance(pending, dict) and str(pending.get("key") or "") == pending_key)
            text = "Confirmer" if armed else ("Dissocier" if action == "unpair" else "2P")
            try:
                button.configure(
                    text=text,
                    width=9 if text in {"Confirmer", "Dissocier"} else 5,
                    state="normal" if allowed else "disabled",
                )
            except Exception:
                pass
            self._structure_update_common_rule_actions()
            return

        source = self.items[indices[0]] if len(indices) == 1 else None
        allowed = self.structure_double_page_source_allowed(source) if source is not None and not self._double_page_pair_id(source) else False
        current = self.structure_get_double_page_type_rule(self._type_of(source)) if source is not None else False
        excluded = self._double_page_override_value(source) == "__none__" if source is not None else False
        try:
            button.configure(
                text=("2P —" if current and excluded else "2P ✓" if current else "2P"),
                width=5,
                state="normal" if allowed else "disabled",
            )
        except Exception:
            pass
        self._structure_update_common_rule_actions()

    def structure_recto_verso_source_allowed(self, item: dict | None) -> bool:
        if not isinstance(item, dict):
            return False
        return not self._is_locked_page(item) and not self._is_automatic_page(item) and bool(self._type_of(item))

    def structure_recto_verso_type_rules(self) -> dict[str, str]:
        """Règle générale de côté par type : recto/verso ; absence = libre."""
        data = self._data if isinstance(self._data, dict) else {}
        raw = data.get("recto_verso_type_rules", {})
        result: dict[str, str] = {}
        if isinstance(raw, dict):
            for source_type, side in raw.items():
                source = str(source_type or "").strip().lower()
                value = str(side or "").strip().lower()
                if source and value in {"recto", "verso"}:
                    result[source] = value
        return result

    def structure_get_recto_verso_type_rule(self, source_type: str) -> str:
        source = str(source_type or "").strip().lower()
        return self.structure_recto_verso_type_rules().get(source, "")

    def structure_toggle_recto_verso_rule(self, side: str) -> bool:
        """Applique Recto/Verso au type sélectionné ; Annuler est une commande séparée."""
        side = str(side or "").strip().lower()
        if side not in {"recto", "verso"}:
            return False
        indices = self._selected_source_indices()
        if len(indices) != 1:
            self.status_var.set("Recto/Verso : sélectionnez une seule page dans B.")
            return False
        source = self.items[indices[0]]
        pair_role = self._double_page_pair_role(source)
        if pair_role == "left" and side == "recto":
            self.status_var.set("Cette page est la page gauche d’une double page soudée : elle doit rester Verso.")
            return False
        if pair_role == "right" and side == "verso":
            self.status_var.set("Cette page est la page droite d’une double page soudée : elle doit rester Recto.")
            return False
        if not self.structure_recto_verso_source_allowed(source):
            self.status_var.set("Cette page ne peut pas recevoir de règle Recto/Verso.")
            return False
        source_type = self._type_of(source)
        if side == "recto" and self.structure_get_double_page_type_rule(source_type):
            self.status_var.set("Recto incompatible avec Double page : une double page commence sur la page de gauche.")
            return False
        definition = self._structure_type_definition(source_type)
        source_label = str(definition.get("short_label") or definition.get("label") or source_type.replace("_", " ").capitalize())

        data = deepcopy(self._data) if isinstance(self._data, dict) else {}
        if self.project is not None:
            try:
                loaded = self.project.load_mockup()
                if isinstance(loaded, dict):
                    data = loaded
            except Exception:
                pass
        raw = data.get("recto_verso_type_rules", {})
        rules = dict(raw) if isinstance(raw, dict) else {}
        had_rule = str(rules.get(source_type) or "").strip().lower() in {"recto", "verso"}
        rules[source_type] = side
        data["recto_verso_type_rules"] = rules

        # Une nouvelle règle repart proprement. Un simple changement R↔V garde
        # les exceptions existantes ; une ancienne exception orpheline ne survit pas.
        for item in self.items:
            if self._is_automatic_page(item) or self._type_of(item) != source_type:
                continue
            if not had_rule:
                item.pop("recto_verso_override", None)
            item["structure_side"] = side if item.get("recto_verso_override") != "__none__" else "libre"
        if isinstance(data.get("items"), list):
            for item in data["items"]:
                if not isinstance(item, dict) or self._is_automatic_page(item) or self._type_of(item) != source_type:
                    continue
                if not had_rule:
                    item.pop("recto_verso_override", None)
                item["structure_side"] = side if item.get("recto_verso_override") != "__none__" else "libre"

        # Le clic sur R/V réintègre explicitement l'occurrence choisie.
        source.pop("recto_verso_override", None)
        self._data = data
        # Persiste la règle AVANT la synchronisation : _save_order recharge le
        # fichier projet et ne doit pas pouvoir réintroduire l'ancien état.
        if self.project is not None:
            self.project.save_mockup(data)
        self._sync_structural_automatic_pages()
        self._structure_recto_verso_armed = False
        self._save_order()
        self._structure_set_rule_target("R" if side == "recto" else "V")
        self.status_var.set(f"{source_label}  •  règle {side.capitalize()}")
        self.render()
        return True

    def _recto_verso_override_value(self, item: dict | None):
        if not isinstance(item, dict):
            return None
        if "recto_verso_override" in item:
            return item.get("recto_verso_override")
        return None

    def _effective_recto_verso_rule(self, item: dict | None) -> str:
        if not isinstance(item, dict) or self._is_automatic_page(item):
            return ""
        rule = self.structure_get_recto_verso_type_rule(self._type_of(item))
        if not rule:
            return ""
        if self._recto_verso_override_value(item) == "__none__":
            return ""
        return rule

    def structure_toggle_recto_verso_exception(self) -> bool:
        indices = self._selected_source_indices()
        if len(indices) != 1:
            return False
        source = self.items[indices[0]]
        source_type = self._type_of(source)
        rule = self.structure_get_recto_verso_type_rule(source_type)
        if not rule:
            self.status_var.set("Aucune règle Recto/Verso à désolidariser.")
            return False
        if self._recto_verso_override_value(source) == "__none__":
            source.pop("recto_verso_override", None)
            message = "Page réintégrée à la règle Recto/Verso."
        else:
            source["recto_verso_override"] = "__none__"
            source["structure_side"] = "libre"
            message = "Cette page est une exception Recto/Verso."
        self._sync_structural_automatic_pages()
        self._save_order()
        self.status_var.set(message)
        self.render()
        return True

    def structure_remove_recto_verso_rule(self) -> bool:
        indices = self._selected_source_indices()
        if len(indices) != 1:
            return False
        source = self.items[indices[0]]
        source_type = self._type_of(source)
        current = self.structure_get_recto_verso_type_rule(source_type)
        if not current:
            return False
        data = deepcopy(self._data) if isinstance(self._data, dict) else {}
        if self.project is not None:
            try:
                loaded = self.project.load_mockup()
                if isinstance(loaded, dict):
                    data = loaded
            except Exception:
                pass
        rules = dict(data.get("recto_verso_type_rules", {})) if isinstance(data.get("recto_verso_type_rules", {}), dict) else {}
        rules.pop(source_type, None)
        data["recto_verso_type_rules"] = rules
        for item in self.items:
            if self._is_automatic_page(item) or self._type_of(item) != source_type:
                continue
            item.pop("recto_verso_override", None)
            item.pop("recto_verso_conflict", None)
            item["structure_side"] = "libre"
        if isinstance(data.get("items"), list):
            for item in data["items"]:
                if not isinstance(item, dict) or self._is_automatic_page(item) or self._type_of(item) != source_type:
                    continue
                item.pop("recto_verso_override", None)
                item.pop("recto_verso_conflict", None)
                item["structure_side"] = "libre"
        self._data = data
        # Même principe pour l'annulation : supprimer la règle sur disque avant
        # que le recalcul structurel ne recharge le projet.
        if self.project is not None:
            self.project.save_mockup(data)
        self._sync_structural_automatic_pages()
        self._save_order()
        self.status_var.set("Règle Recto/Verso annulée pour ce type.")
        self.render()
        return True

    def _structure_update_recto_verso_visuals(self) -> None:
        panel = getattr(self, "structure_recto_verso_panel", None)
        recto_btn = getattr(self, "structure_recto_btn", None)
        verso_btn = getattr(self, "structure_verso_btn", None)
        if panel is None or recto_btn is None or verso_btn is None:
            return
        indices = self._selected_source_indices()
        source = self.items[indices[0]] if len(indices) == 1 else None
        allowed = self.structure_recto_verso_source_allowed(source) if source is not None else False
        armed = bool(getattr(self, "_structure_recto_verso_armed", False)) and allowed
        try:
            panel.configure(highlightthickness=2 if armed else 1, highlightbackground="#E7C37A" if armed else "#385264")
        except Exception:
            pass
        current = self.structure_get_recto_verso_type_rule(self._type_of(source)) if source is not None else ""
        excluded = self._recto_verso_override_value(source) == "__none__" if source is not None else False
        try:
            recto_btn.configure(text=("R —" if current == "recto" and excluded else "R ✓" if current == "recto" else "R"))
            verso_btn.configure(text=("V —" if current == "verso" and excluded else "V ✓" if current == "verso" else "V"))
            state = "normal" if allowed else "disabled"
            recto_btn.configure(state=state)
            verso_btn.configure(state=state)
        except Exception:
            pass
        self._structure_update_common_rule_actions()

    def _is_recto_verso_correction(self, item: dict | None) -> bool:
        if not isinstance(item, dict):
            return False
        if bool(item.get("automatic_recto_verso", False)):
            return True
        return any(role.get("code") in {"R", "V"} for role in self._automatic_roles(item))

    def _recto_verso_target_side(self, item: dict | None) -> str:
        if not isinstance(item, dict):
            return ""
        for role in self._automatic_roles(item):
            if role.get("code") == "R":
                return "recto"
            if role.get("code") == "V":
                return "verso"
        value = str(item.get("recto_target_side") or item.get("recto_verso_side") or "").strip().lower()
        return value if value in {"recto", "verso"} else ""

    def _new_recto_verso_correction(self, source: dict, side: str, existing: dict | None = None) -> dict:
        """Compatibilité : fabrique une page auto spéciale portant R/V."""
        code = "R" if str(side).lower() == "recto" else "V"
        return self._prepare_structural_auto_item(
            existing,
            roles=[{"code": code, "source_id": str(source.get("id") or ""), "target_type": "page_blanche"}],
            group_id=self._item_group_id(source),
        )

    def _sync_recto_verso_corrections(self) -> bool:
        """Compatibilité : Recto/Verso est désormais réconcilié avec Page auto en une seule passe."""
        return self._sync_structural_automatic_pages()

    def structure_auto_target_options(self) -> list[tuple[str, str]]:
        """Types autorisés comme page automatique associée."""
        result: list[tuple[str, str]] = [("page_blanche", "Page blanche")]
        seen = {"page_blanche"}
        for key, label, _custom in self.structure_available_page_types():
            key = str(key or "").strip()
            if not key or key in seen:
                continue
            low = key.lower()
            protected = self.COVER_TYPES | self.BACK_COVER_TYPES | self.SECOND_COVER_TYPES | self.THIRD_COVER_TYPES
            if low in protected:
                continue
            result.append((key, str(label or key)))
            seen.add(key)
        return result

    def structure_page_auto_type_rules(self) -> dict[str, dict[str, str]]:
        """Règles générales Page auto, séparées pour Avant et Après."""
        data = self._data if isinstance(self._data, dict) else {}
        raw = data.get("page_auto_type_rules", {})
        allowed = {key for key, _label in self.structure_auto_target_options()}
        result: dict[str, dict[str, str]] = {}
        if isinstance(raw, dict):
            for source_type, value in raw.items():
                source = str(source_type or "").strip()
                if not source or not isinstance(value, dict):
                    continue
                before = str(value.get("before") or "").strip()
                after = str(value.get("after") or "").strip()
                entry = {}
                if before in allowed:
                    entry["before"] = before
                if after in allowed:
                    entry["after"] = after
                if entry:
                    result[source] = entry
        return result

    def structure_get_page_auto_type_rule(self, source_type: str, position: str) -> str:
        source = str(source_type or "").strip()
        position = str(position or "").strip().lower()
        if position not in {"before", "after"}:
            return ""
        return self.structure_page_auto_type_rules().get(source, {}).get(position, "")

    def _clear_page_auto_position_state(
        self, source_type: str, position: str, *, data: dict | None = None, keep_exclusions: bool = False
    ) -> bool:
        """Nettoie l'ancien état local d'une position Page auto.

        Depuis V25, une association Page auto est une règle générale par type.
        La seule exception locale encore valable est « désolidarisée » (__none__)
        et seulement tant que la règle correspondante existe.
        """
        source = str(source_type or "").strip().lower()
        position = str(position or "").strip().lower()
        if position not in {"before", "after"} or not source:
            return False
        keys = (f"page_auto_{position}_override", f"page_auto_{position}_type")
        changed = False

        for item in getattr(self, "items", []):
            if self._type_of(item) != source or self._is_automatic_page(item):
                continue
            for key in keys:
                if key not in item:
                    continue
                if keep_exclusions and key.endswith("_override") and item.get(key) == "__none__":
                    continue
                item.pop(key, None)
                changed = True

        if isinstance(data, dict) and isinstance(data.get("items"), list):
            cleaned = []
            data_changed = False
            for raw in data.get("items", []):
                if not isinstance(raw, dict):
                    cleaned.append(raw)
                    continue
                item = dict(raw)
                if self._type_of(item) == source and not self._is_automatic_page(item):
                    for key in keys:
                        if key not in item:
                            continue
                        if keep_exclusions and key.endswith("_override") and item.get(key) == "__none__":
                            continue
                        item.pop(key, None)
                        data_changed = True
                cleaned.append(item)
            if data_changed:
                data["items"] = cleaned
                changed = True
        return changed

    def structure_set_page_auto_type_rule(self, source_type: str, position: str, target_type: str) -> bool:
        source = str(source_type or "").strip().lower()
        position = str(position or "").strip().lower()
        target = str(target_type or "").strip()
        if position not in {"before", "after"} or not source:
            return False
        allowed = {key for key, _label in self.structure_auto_target_options()}
        if target not in allowed:
            return False
        protected = self.COVER_TYPES | self.BACK_COVER_TYPES | self.SECOND_COVER_TYPES | self.THIRD_COVER_TYPES
        if source in protected:
            return False

        data = deepcopy(self._data) if isinstance(self._data, dict) else {}
        if self.project is not None:
            try:
                loaded = self.project.load_mockup()
                if isinstance(loaded, dict):
                    data = loaded
            except Exception:
                pass
        rules = data.get("page_auto_type_rules", {})
        if not isinstance(rules, dict):
            rules = {}
        entry = dict(rules.get(source, {})) if isinstance(rules.get(source, {}), dict) else {}
        had_rule = bool(str(entry.get(position) or "").strip())

        # Une nouvelle règle repart d'un état propre. Lors d'un remplacement,
        # seules les vraies exclusions « désolidarisées » sont conservées ; les
        # anciens overrides locaux de V23/V24 ne peuvent plus prendre le dessus.
        self._clear_page_auto_position_state(
            source, position, data=data, keep_exclusions=had_rule
        )

        entry[position] = target
        rules[source] = entry
        data["page_auto_type_rules"] = rules
        self._data = data
        if self.project is not None:
            self.project.save_mockup(data)

        self._sync_all_page_auto(source_type=source, save=True)
        return True

    def structure_remove_page_auto_type_rule(self, source_type: str, position: str) -> bool:
        source = str(source_type or "").strip().lower()
        position = str(position or "").strip().lower()
        if position not in {"before", "after"} or not source:
            return False
        data = deepcopy(self._data) if isinstance(self._data, dict) else {}
        if self.project is not None:
            try:
                loaded = self.project.load_mockup()
                if isinstance(loaded, dict):
                    data = loaded
            except Exception:
                pass
        rules = data.get("page_auto_type_rules", {})
        if not isinstance(rules, dict) or source not in rules:
            return False
        rules = dict(rules)
        entry = dict(rules.get(source, {})) if isinstance(rules.get(source, {}), dict) else {}
        if not str(entry.get(position) or "").strip():
            return False
        entry.pop(position, None)
        if entry:
            rules[source] = entry
        else:
            rules.pop(source, None)
        data["page_auto_type_rules"] = rules

        # Une exception appartient à une règle. Quand la règle disparaît, ses
        # exceptions disparaissent aussi afin qu'une future règle s'applique à
        # nouveau à toutes les occurrences du type.
        self._clear_page_auto_position_state(source, position, data=data)

        self._data = data
        if self.project is not None:
            self.project.save_mockup(data)
        self._sync_all_page_auto(source_type=source, save=True)
        return True

    def _page_auto_override_value(self, item: dict, position: str):
        position = str(position or "").strip().lower()
        override_key = f"page_auto_{position}_override"
        if override_key in item:
            return item.get(override_key)
        # Compatibilité V23 : une association locale existante devient une exception locale.
        legacy_key = f"page_auto_{position}_type"
        if legacy_key in item:
            return item.get(legacy_key)
        return None

    def _structure_page_auto_type(self, item: dict, position: str) -> str:
        position = str(position or "").strip().lower()
        if position not in {"before", "after"}:
            return ""
        allowed = {type_key for type_key, _label in self.structure_auto_target_options()}
        override = self._page_auto_override_value(item, position)
        if override is not None:
            value = str(override or "").strip()
            if value == "__none__":
                return ""
            return value if value in allowed else ""
        source_type = self._type_of(item)
        value = self.structure_get_page_auto_type_rule(source_type, position) if source_type else ""
        return value if value in allowed else ""

    def _sync_page_auto_for_source(self, item: dict) -> bool:
        """Page auto et Recto/Verso sont synchronisés ensemble pour éviter les doublons."""
        if not isinstance(item, dict) or self._is_automatic_page(item):
            return False
        return self._sync_structural_automatic_pages()

    def _prune_orphan_page_auto(self) -> bool:
        """La passe globale reconstruit les pages automatiques et élimine les orphelines."""
        return self._sync_structural_automatic_pages()

    def _page_auto_materialized_for_source(self, item: dict, position: str) -> bool:
        position = str(position or "").strip().lower()
        expected = self._structure_page_auto_type(item, position)
        if not expected:
            return True
        source_id = str(item.get("id") or "")
        code = "AV" if position == "before" else "AP"
        for candidate in self.items:
            if not self._is_automatic_page(candidate):
                continue
            for role in self._automatic_roles(candidate):
                if role.get("code") == code and role.get("source_id") == source_id:
                    return True
        return False

    def _sync_all_page_auto(self, *, source_type: str = "", save: bool = False) -> bool:
        changed = self._sync_structural_automatic_pages()
        if changed and save:
            self._save_order()
            self.render()
        elif changed:
            self.render()
        return changed

    def _automatic_roles(self, item: dict | None) -> list[dict]:
        """Retourne les fonctions structurelles portées par une page automatique."""
        if not isinstance(item, dict):
            return []
        raw = item.get("automatic_roles")
        result: list[dict] = []
        if isinstance(raw, list):
            seen = set()
            for entry in raw:
                if not isinstance(entry, dict):
                    continue
                code = str(entry.get("code") or "").strip().upper()
                source_id = str(entry.get("source_id") or "").strip()
                target_type = str(entry.get("target_type") or "").strip()
                if code not in {"AV", "AP", "R", "V", "DP"} or not source_id:
                    continue
                key = (code, source_id, target_type)
                if key in seen:
                    continue
                seen.add(key)
                result.append({"code": code, "source_id": source_id, "target_type": target_type})
            if result:
                return result
        # Migration transparente des pages automatiques historiques.
        parent = str(item.get("recto_target_id") or item.get("parent_id") or item.get("source_page_id") or "").strip()
        kind = str(item.get("automatic_kind") or "").strip()
        if not parent:
            return []
        if kind == "page_auto_before":
            return [{"code": "AV", "source_id": parent, "target_type": self._type_of(item)}]
        if kind == "page_auto_after":
            return [{"code": "AP", "source_id": parent, "target_type": self._type_of(item)}]
        if kind == "recto_verso_before" or bool(item.get("automatic_recto_verso", False)):
            side = str(item.get("recto_target_side") or "recto").strip().lower()
            return [{"code": "V" if side == "verso" else "R", "source_id": parent, "target_type": "page_blanche"}]
        if kind == "double_page_before" or bool(item.get("automatic_double_page", False)):
            return [{"code": "DP", "source_id": parent, "target_type": "page_blanche"}]
        return []

    def _automatic_source_ids(self, item: dict | None) -> list[str]:
        result = []
        for role in self._automatic_roles(item):
            source_id = str(role.get("source_id") or "")
            if source_id and source_id not in result:
                result.append(source_id)
        return result

    def _automatic_is_shared(self, item: dict | None) -> bool:
        return len(self._automatic_source_ids(item)) > 1

    def _prepare_structural_auto_item(self, existing: dict | None, *, roles: list[dict], group_id: str) -> dict:
        item = existing if isinstance(existing, dict) else {"id": f"AUTO-{uuid4().hex[:12].upper()}", "count": 1, "done": False}
        normalized = []
        target_types = []
        for role in roles:
            code = str(role.get("code") or "").strip().upper()
            source_id = str(role.get("source_id") or "").strip()
            target_type = str(role.get("target_type") or "").strip()
            if code not in {"AV", "AP", "R", "V", "DP"} or not source_id:
                continue
            normalized.append({"code": code, "source_id": source_id, "target_type": target_type})
            if target_type and code in {"AV", "AP"} and target_type not in target_types:
                target_types.append(target_type)
        if not target_types:
            target_types = ["page_blanche"]
        chosen_type = target_types[0]
        definition = self._structure_type_definition(chosen_type)
        label = str(definition.get("short_label") or definition.get("label") or chosen_type.replace("_", " ").capitalize())
        self._structure_apply_type_metadata(item, chosen_type, label)
        source_ids = []
        for role in normalized:
            if role["source_id"] not in source_ids:
                source_ids.append(role["source_id"])
        item["plan_group"] = group_id
        item["automatic"] = True
        item["auto_generated"] = True
        item["automatic_structure"] = True
        item["automatic_roles"] = normalized
        item["automatic_markers"] = [role["code"] for role in normalized]
        item["automatic_target_types"] = target_types
        item["automatic_type_conflict"] = len(target_types) > 1
        item["automatic_shared"] = len(source_ids) > 1
        if len(normalized) == 1 and normalized[0]["code"] == "AV":
            item["automatic_kind"] = "page_auto_before"
            item["automatic_position"] = "before"
        elif len(normalized) == 1 and normalized[0]["code"] == "AP":
            item["automatic_kind"] = "page_auto_after"
            item["automatic_position"] = "after"
        elif len(normalized) == 1 and normalized[0]["code"] in {"R", "V"}:
            item["automatic_kind"] = "recto_verso_before"
            item["automatic_position"] = "before"
        elif len(normalized) == 1 and normalized[0]["code"] == "DP":
            item["automatic_kind"] = "double_page_before"
            item["automatic_position"] = "before"
        else:
            item["automatic_kind"] = "structure_auto_shared" if len(source_ids) > 1 else "structure_auto_combined"
            item["automatic_position"] = "shared" if len(source_ids) > 1 else "before"
        parent_id = source_ids[0] if len(source_ids) == 1 else ""
        item["parent_id"] = parent_id
        item["source_page_id"] = parent_id
        item["recto_target_id"] = parent_id
        rv = next((role["code"] for role in normalized if role["code"] in {"R", "V"}), "")
        item["automatic_recto_verso"] = bool(rv)
        item["recto_target_side"] = "recto" if rv == "R" else "verso" if rv == "V" else ""
        item["automatic_double_page"] = any(role["code"] == "DP" for role in normalized)
        item["structure_side"] = "libre"
        item["structure_duplicable"] = False
        return item

    def _sync_structural_automatic_pages(self) -> bool:
        """Réconcilie AV/AP, Recto/Verso et 2P sans fusionner des types incompatibles."""
        if getattr(self, "_structure_rule_sync_in_progress", False):
            return False

        selection_snapshot = self._structure_selection_snapshot()
        self._structure_rule_sync_in_progress = True
        try:
            old_items = list(self.items)
            old_snapshot = [dict(item) for item in old_items]
            existing_autos = [item for item in old_items if self._is_automatic_page(item)]
            base_items = [item for item in old_items if not self._is_automatic_page(item)]
            pair_sanitized = self._sanitize_double_page_pairs(base_items)
            if not base_items:
                changed = bool(self.items)
                if changed:
                    self.items = []
                return changed

            for item in base_items:
                item.pop("recto_verso_conflict", None)
                item.pop("double_page_conflict", None)
                item.pop("double_page_pair_conflict", None)

            by_group: dict[str, list[dict]] = {}
            group_order: list[str] = []
            for item in base_items:
                gid = self._item_group_id(item)
                if gid not in by_group:
                    by_group[gid] = []
                    group_order.append(gid)
                by_group[gid].append(item)

            # Un slot représente l'intervalle physique entre deux pages sources.
            slot_roles: dict[tuple[str, str, str], list[dict]] = {}
            before_slot: dict[str, tuple[str, str, str]] = {}
            after_slot: dict[str, tuple[str, str, str]] = {}

            def slot(gid: str, left_id: str, right_id: str):
                key = (gid, left_id or "", right_id or "")
                slot_roles.setdefault(key, [])
                return key

            def add_role_to_list(target: list[dict], code: str, source: dict, target_type: str = ""):
                source_id = str(source.get("id") or "").strip()
                if not source_id:
                    source_id = f"MAQUETTE-{uuid4().hex[:12].upper()}"
                    source["id"] = source_id
                role = {"code": code, "source_id": source_id, "target_type": target_type}
                if role not in target:
                    target.append(role)

            def add_slot_role(key, code: str, source: dict, target_type: str = ""):
                add_role_to_list(slot_roles[key], code, source, target_type)

            for gid in group_order:
                pages = by_group[gid]
                for pos, source in enumerate(pages):
                    sid = str(source.get("id") or "").strip()
                    if not sid:
                        sid = f"MAQUETTE-{uuid4().hex[:12].upper()}"
                        source["id"] = sid
                    left_id = str(pages[pos - 1].get("id") or "") if pos > 0 else ""
                    right_id = str(pages[pos + 1].get("id") or "") if pos + 1 < len(pages) else ""
                    bkey = slot(gid, left_id, sid)
                    akey = slot(gid, sid, right_id)
                    before_slot[sid] = bkey
                    after_slot[sid] = akey
                    before_type = self._structure_page_auto_type(source, "before") if self.structure_auto_source_allowed(source) else ""
                    after_type = self._structure_page_auto_type(source, "after") if self.structure_auto_source_allowed(source) else ""
                    pair_role = self._double_page_pair_role(source)
                    peer_id = self._double_page_pair_peer_id(source)
                    internal_before = pair_role == "right" and left_id and left_id == peer_id
                    internal_after = pair_role == "left" and right_id and right_id == peer_id
                    if before_type and internal_before:
                        source["double_page_pair_conflict"] = True
                        peer = next((p for p in pages if str(p.get("id") or "") == peer_id), None)
                        if peer is not None:
                            peer["double_page_pair_conflict"] = True
                    elif before_type:
                        add_slot_role(bkey, "AV", source, before_type)
                    if after_type and internal_after:
                        source["double_page_pair_conflict"] = True
                        peer = next((p for p in pages if str(p.get("id") or "") == peer_id), None)
                        if peer is not None:
                            peer["double_page_pair_conflict"] = True
                    elif after_type:
                        add_slot_role(akey, "AP", source, after_type)

            # Séquence pages + intervalles AV/AP.
            sequence: list[tuple[str, object]] = []
            emitted_slots: set[tuple[str, str, str]] = set()
            for gid in group_order:
                for source in by_group[gid]:
                    sid = str(source.get("id") or "")
                    bkey = before_slot[sid]
                    if bkey not in emitted_slots and slot_roles.get(bkey):
                        sequence.append(("slot", bkey))
                        emitted_slots.add(bkey)
                    sequence.append(("page", source))
                    akey = after_slot[sid]
                    if not akey[2] and akey not in emitted_slots and slot_roles.get(akey):
                        sequence.append(("slot", akey))
                        emitted_slots.add(akey)

            # A une frontière de partie, deux intervalles sans page entre eux constituent
            # le même espace physique. On réunit leurs demandes avant de décider si elles
            # sont compatibles ou si deux pages sont réellement nécessaires.
            slot_group_override: dict[tuple[str, str, str], str] = {}
            consolidated: list[tuple[str, object]] = []
            for kind, payload in sequence:
                if kind == "slot" and consolidated and consolidated[-1][0] == "slot":
                    previous = consolidated[-1][1]
                    for role in slot_roles.get(payload, []):
                        if role not in slot_roles[previous]:
                            slot_roles[previous].append(role)
                    slot_group_override[previous] = payload[0] or previous[0]
                    slot_roles[payload] = []
                    continue
                consolidated.append((kind, payload))

            # Chaque intervalle peut maintenant produire plusieurs autos, mais seulement
            # lorsque les types AV/AP sont incompatibles. AP reste côté gauche et AV côté droit.
            auto_roles: dict[tuple, list[dict]] = {}
            auto_groups: dict[tuple, str] = {}
            expanded: list[tuple[str, object]] = []

            def split_av_ap_roles(roles: list[dict]) -> list[list[dict]]:
                ordered = [r for r in roles if str(r.get("code") or "").upper() == "AP"]
                ordered += [r for r in roles if str(r.get("code") or "").upper() == "AV"]
                buckets: list[list[dict]] = []
                bucket_types: list[str] = []
                for role in ordered:
                    target_type = str(role.get("target_type") or "page_blanche").strip() or "page_blanche"
                    if buckets and bucket_types[-1] == target_type:
                        if role not in buckets[-1]:
                            buckets[-1].append(role)
                    else:
                        buckets.append([role])
                        bucket_types.append(target_type)
                return buckets

            for kind, payload in consolidated:
                if kind == "page":
                    expanded.append((kind, payload))
                    continue
                key = payload
                buckets = split_av_ap_roles(slot_roles.get(key, []))
                for bucket_index, roles in enumerate(buckets):
                    token = ("slot", key, bucket_index)
                    auto_roles[token] = list(roles)
                    auto_groups[token] = slot_group_override.get(key, key[0])
                    expanded.append(("auto", token))

            # Recto/Verso et Double page : couvertures hors parité. Une auto AV/AP
            # déjà présente peut satisfaire la contrainte si sa présence donne la bonne
            # parité. Si l'intervalle contient déjà une auto et que la parité reste fausse,
            # on conserve le conflit plutôt que d'empiler des blancs correctifs inutiles.
            physical_index = 0
            revised: list[tuple[str, object]] = []
            for kind, payload in expanded:
                if kind == "auto":
                    revised.append((kind, payload))
                    physical_index += 1
                    continue

                source = payload
                if self._is_locked_page(source):
                    revised.append((kind, source))
                    continue

                source.pop("recto_verso_conflict", None)
                source.pop("double_page_conflict", None)
                rule = self._effective_recto_verso_rule(source)
                double_page = self._effective_double_page_rule(source)
                pair_role = self._double_page_pair_role(source)
                pair_left = pair_role == "left" and bool(self._double_page_pair_peer_id(source))
                pair_right = pair_role == "right" and bool(self._double_page_pair_peer_id(source))
                actual = "recto" if physical_index % 2 == 0 else "verso"
                previous_auto = revised[-1][1] if revised and revised[-1][0] == "auto" else None

                if double_page and rule == "recto":
                    source["recto_verso_conflict"] = True
                    rule = ""
                if pair_left and rule == "recto":
                    source["recto_verso_conflict"] = True
                    source["double_page_pair_conflict"] = True
                    rule = ""
                if pair_right and rule == "verso":
                    source["recto_verso_conflict"] = True
                    source["double_page_pair_conflict"] = True
                    rule = ""

                needed_roles: list[tuple[str, str]] = []
                satisfied_roles: list[tuple[str, str]] = []
                if double_page or pair_left:
                    (satisfied_roles if actual == "verso" else needed_roles).append(("DP", "page_blanche"))
                if pair_right and actual != "recto":
                    # On ne casse jamais une paire en insérant une correction entre ses deux pages.
                    source["double_page_pair_conflict"] = True
                    source["recto_verso_conflict"] = bool(rule)
                elif rule:
                    code = "R" if rule == "recto" else "V"
                    (satisfied_roles if actual == rule else needed_roles).append((code, "page_blanche"))

                if needed_roles:
                    if pair_right:
                        source["double_page_pair_conflict"] = True
                        if any(code in {"R", "V"} for code, _target in needed_roles):
                            source["recto_verso_conflict"] = True
                    else:
                        # Une auto AV/AP déjà présente est réutilisée lorsqu'elle donne
                        # la bonne parité. Si la parité reste fausse, une seconde page
                        # corrective est réellement nécessaire : on l'ajoute au lieu
                        # de laisser un faux conflit.
                        source_id = str(source.get("id") or "")
                        token = ("correction", source_id, physical_index)
                        roles: list[dict] = []
                        for code, target_type in needed_roles:
                            add_role_to_list(roles, code, source, target_type)
                        auto_roles[token] = roles
                        auto_groups[token] = self._item_group_id(source)
                        revised.append(("auto", token))
                        previous_auto = token
                        physical_index += 1

                # Une auto existante qui donne déjà la bonne parité porte aussi R/V/2P.
                if previous_auto is not None:
                    for code, target_type in satisfied_roles:
                        add_role_to_list(auto_roles.setdefault(previous_auto, []), code, source, target_type)

                revised.append(("page", source))
                # Une règle 2P par type représente une seule source sur deux positions.
                # Une paire soudée contient déjà deux vraies pages : chacune compte pour une position.
                physical_index += 2 if double_page else 1

            active_tokens = [payload for kind, payload in revised if kind == "auto" and auto_roles.get(payload)]

            # Réutilise les IDs des autos existantes lorsqu'elles représentent encore
            # la même relation. Le type cible participe au score pour éviter les échanges
            # d'identité entre deux autos incompatibles du même intervalle.
            existing_with_roles = [(item, self._automatic_roles(item)) for item in existing_autos]
            used_existing: set[int] = set()
            built_for_token: dict[tuple, dict] = {}
            for token in active_tokens:
                roles = auto_roles[token]
                role_keys = {
                    (str(r.get("code") or ""), str(r.get("source_id") or ""), str(r.get("target_type") or ""))
                    for r in roles
                }
                desired_type = next(
                    (str(r.get("target_type") or "") for r in roles if str(r.get("code") or "").upper() in {"AV", "AP"}),
                    "page_blanche",
                ) or "page_blanche"
                best = None
                best_score = -1
                for candidate, candidate_roles in existing_with_roles:
                    if id(candidate) in used_existing:
                        continue
                    candidate_keys = {
                        (str(r.get("code") or ""), str(r.get("source_id") or ""), str(r.get("target_type") or ""))
                        for r in candidate_roles
                    }
                    score = len(role_keys & candidate_keys) * 10
                    if self._type_of(candidate) == desired_type:
                        score += 2
                    if score > best_score:
                        best, best_score = candidate, score
                if best_score <= 0:
                    best = None
                if best is not None:
                    used_existing.add(id(best))
                built_for_token[token] = self._prepare_structural_auto_item(
                    best,
                    roles=roles,
                    group_id=auto_groups.get(token, self.DEFAULT_GROUP_ID),
                )

            rebuilt: list[dict] = []
            for kind, payload in revised:
                if kind == "page":
                    rebuilt.append(payload)
                else:
                    auto = built_for_token.get(payload)
                    if auto is not None:
                        rebuilt.append(auto)

            self.items = rebuilt
            new_snapshot = [dict(item) for item in self.items]
            if len(old_items) != len(self.items):
                return True
            if [str(item.get("id") or "") for item in old_items] != [str(item.get("id") or "") for item in self.items]:
                return True
            return old_snapshot != new_snapshot
        finally:
            self._structure_rule_sync_in_progress = False
            self._structure_restore_selection_snapshot(selection_snapshot)

    def structure_set_selected_page_auto(self, position: str, target_type: str = "", scope: str = "local") -> bool:
        """Associe Avant/Après aux pages sélectionnées ou à toutes les pages de leur type."""
        position = str(position or "").strip().lower()
        scope = str(scope or "local").strip().lower()
        if position not in {"before", "after"}:
            return False
        indices = self._selected_source_indices()
        if not indices:
            self.status_var.set("Sélectionnez d'abord une page principale dans B.")
            return False

        target = str(target_type or "").strip()
        allowed = {key for key, _label in self.structure_auto_target_options()}
        if target and target not in allowed:
            return False

        sources = [self.items[index] for index in indices if 0 <= index < len(self.items)]
        if not sources or any(not self.structure_auto_source_allowed(item) for item in sources):
            self.status_var.set("La sélection contient une page qui ne peut pas recevoir de page automatique.")
            return False

        side = "Avant" if position == "before" else "Après"
        if scope == "type":
            source_types = {self._type_of(item) for item in sources if self._type_of(item)}
            if len(source_types) != 1:
                self.status_var.set("Pour appliquer à un type, sélectionnez des pages du même type.")
                return False
            source_type = next(iter(source_types))
            if not target:
                ok = self.structure_remove_page_auto_type_rule(source_type, position)
                if ok:
                    self.status_var.set(f"Règle générale Page auto {side.lower()} supprimée.")
                return ok

            # La page qui sert à créer la règle revient au comportement général.
            for item in sources:
                item.pop(f"page_auto_{position}_override", None)
                item.pop(f"page_auto_{position}_type", None)
            ok = self.structure_set_page_auto_type_rule(source_type, position, target)
            if not ok:
                return False
            source_label = self._structure_type_definition(source_type).get("label") or source_type.replace("_", " ").strip().capitalize()
            target_label = self._structure_type_definition(target).get("label") or target.replace("_", " ").strip().capitalize()
            self.status_var.set(f"Tous les {source_label}  •  {side} → {target_label}")
            return True

        # Portée locale : toutes les pages sélectionnées reçoivent la même exception.
        override_key = f"page_auto_{position}_override"
        legacy_key = f"page_auto_{position}_type"
        source_ids = []
        for item in sources:
            source_ids.append(str(item.get("id") or ""))
            item.pop(legacy_key, None)
            if target:
                item[override_key] = target
            else:
                # Si une règle générale existe, "__none__" signifie exception sans page auto.
                general = self.structure_get_page_auto_type_rule(self._type_of(item), position)
                if general:
                    item[override_key] = "__none__"
                else:
                    item.pop(override_key, None)
            self._sync_page_auto_for_source(item)

        self._save_order()
        restored = [
            index for index, item in enumerate(self.items)
            if str(item.get("id") or "") in set(source_ids)
        ]
        self._set_multi_page_selection(restored)
        self.render()

        if target:
            label = self._structure_type_definition(target).get("label") or target.replace("_", " ").strip().capitalize()
            prefix = "Pages sélectionnées" if len(sources) > 1 else "Page"
            self.status_var.set(f"{prefix}  •  {side} → {label}")
        else:
            self.status_var.set(f"Page auto {side.lower()} retirée de la sélection.")
        return True

    def structure_reset_selected_page_auto_override(self, position: str) -> bool:
        position = str(position or "").strip().lower()
        if position not in {"before", "after"}:
            return False
        indices = self._selected_source_indices()
        if not indices:
            return False
        source_ids = []
        changed = False
        for index in indices:
            item = self.items[index]
            source_ids.append(str(item.get("id") or ""))
            for key in (f"page_auto_{position}_override", f"page_auto_{position}_type"):
                if key in item:
                    item.pop(key, None)
                    changed = True
            self._sync_page_auto_for_source(item)
        if changed:
            self._save_order()
            restored = [i for i, item in enumerate(self.items) if str(item.get("id") or "") in set(source_ids)]
            self._set_multi_page_selection(restored)
            self.render()
        return changed

    # ------------------------------------------------------------------
    # V25 — Page auto : une règle générale par type, choisie directement
    # dans les briques de C. Aucun menu imbriqué, aucune insertion locale.
    # ------------------------------------------------------------------

    def _structure_emit_page_auto_mode(self) -> None:
        try:
            self.event_generate("<<StructurePageAutoModeChanged>>", when="tail")
        except Exception:
            pass

    def structure_page_auto_context(self) -> dict:
        mode = getattr(self, "_structure_page_auto_mode", None)
        if not isinstance(mode, dict):
            return {"active": False, "step": self._structure_page_auto_visual_step()}
        position = str(mode.get("position") or "")
        source_type = str(mode.get("source_type") or "")
        source_id = str(mode.get("source_id") or "")
        source_label = str(mode.get("source_label") or source_type)
        target_type = self.structure_get_page_auto_type_rule(source_type, position)
        target_label = ""
        if target_type:
            definition = self._structure_type_definition(target_type)
            target_label = str(definition.get("short_label") or definition.get("label") or target_type)
        source = next((item for item in self.items if str(item.get("id") or "") == source_id), None)
        override = self._page_auto_override_value(source, position) if source is not None else None
        return {
            "active": True,
            "step": self._structure_page_auto_visual_step(),
            "position": position,
            "side_label": "Avant" if position == "before" else "Après",
            "source_type": source_type,
            "source_label": source_label,
            "source_id": source_id,
            "target_type": target_type,
            "target_label": target_label,
            "has_rule": bool(target_type),
            "excluded": override == "__none__",
        }

    def structure_begin_page_auto_rule(self, position: str) -> bool:
        position = str(position or "").strip().lower()
        if position not in {"before", "after"}:
            return False
        indices = self._selected_source_indices()
        if len(indices) != 1:
            self.status_var.set("Page auto : sélectionnez une seule page principale dans B.")
            return False
        item = self.items[indices[0]]
        if not self.structure_auto_source_allowed(item):
            self.status_var.set("Cette page ne peut pas servir de source à une règle Page auto.")
            return False
        source_type = self._type_of(item)
        if not source_type:
            self.status_var.set("Page auto : attribuez d'abord un type à cette page.")
            return False
        source_id = str(item.get("id") or "").strip()
        definition = self._structure_type_definition(source_type)
        source_label = str(definition.get("short_label") or definition.get("label") or source_type.replace("_", " ").capitalize())

        current = getattr(self, "_structure_page_auto_mode", None)
        if isinstance(current, dict) and current.get("position") == position and current.get("source_id") == source_id:
            self.structure_cancel_page_auto_mode()
            return True

        self.structure_cancel_tool()
        self._structure_reset_action()
        self._structure_page_auto_mode = {
            "position": position,
            "source_type": source_type,
            "source_label": source_label,
            "source_id": source_id,
        }
        self._structure_update_page_auto_visuals()
        side = "avant" if position == "before" else "après"
        current_rule = self.structure_get_page_auto_type_rule(source_type, position)
        if current_rule:
            target_def = self._structure_type_definition(current_rule)
            target_label = str(target_def.get("short_label") or target_def.get("label") or current_rule)
            self.status_var.set(
                f"Page auto  •  tous les {source_label}  •  {side} : {target_label}  •  choisissez une brique dans C pour remplacer"
            )
        else:
            self.status_var.set(
                f"Page auto  •  tous les {source_label}  •  choisissez dans C la page à placer {side}"
            )
        self._structure_emit_page_auto_mode()
        return True

    def structure_cancel_page_auto_mode(self, *, silent: bool = False) -> bool:
        if not isinstance(getattr(self, "_structure_page_auto_mode", None), dict):
            return False
        self._structure_page_auto_mode = None
        self._structure_update_page_auto_visuals()
        if not silent:
            self.status_var.set("Page auto annulée.")
        self._structure_emit_page_auto_mode()
        return True

    def structure_consume_page_auto_choice(self, target_type: str) -> bool:
        """Consomme un clic sur une brique de C lorsque Page auto est actif."""
        mode = getattr(self, "_structure_page_auto_mode", None)
        if not isinstance(mode, dict):
            return False
        target = str(target_type or "").strip()
        allowed = {key for key, _label in self.structure_auto_target_options()}
        if target not in allowed:
            self.status_var.set("Page auto : choisissez un type de page utilisable comme page associée.")
            return True

        position = str(mode.get("position") or "")
        source_id = str(mode.get("source_id") or "")

        # Le troisième clic se rattache à la page réellement sélectionnée, pas à
        # un type mémorisé au deuxième clic. Cela évite qu'une règle Avant soit
        # enregistrée sur un ancien type qui n'existe plus dans B.
        source = next((item for item in self.items if str(item.get("id") or "") == source_id), None)
        if source is None or not self.structure_auto_source_allowed(source):
            self.status_var.set("Page auto : la page source n'est plus disponible.")
            self.structure_cancel_page_auto_mode(silent=True)
            return True

        source_type = self._type_of(source)
        if not source_type:
            self.status_var.set("Page auto : la page source n'a plus de type.")
            self.structure_cancel_page_auto_mode(silent=True)
            return True
        definition = self._structure_type_definition(source_type)
        source_label = str(
            definition.get("short_label")
            or definition.get("label")
            or source_type.replace("_", " ").capitalize()
        )

        source.pop(f"page_auto_{position}_override", None)
        source.pop(f"page_auto_{position}_type", None)

        if not self.structure_set_page_auto_type_rule(source_type, position, target):
            self.status_var.set("Impossible de créer cette règle Page auto.")
            return True

        self._structure_last_auto_type = target
        target_def = self._structure_type_definition(target)
        target_label = str(target_def.get("short_label") or target_def.get("label") or target)
        side = "Avant" if position == "before" else "Après"

        # Restaure la sélection de la page source sans déplacer la ligne.
        source_index = next(
            (i for i, item in enumerate(self.items) if str(item.get("id") or "") == source_id),
            None,
        )
        if source_index is not None:
            self._set_single_page_selection(source_index)
            self.render()

        self._structure_page_auto_mode = None
        self._structure_set_rule_target("AV" if position == "before" else "AP")
        self._structure_update_page_auto_visuals()
        self._structure_emit_page_auto_mode()
        self.status_var.set(f"Règle Page auto  •  tous les {source_label}  •  {side} → {target_label}")
        return True

    def structure_toggle_page_auto_exception(self) -> bool:
        """Exclut ou réintègre uniquement la page source de la règle générale active."""
        context = self.structure_page_auto_context()
        if not context.get("active") or not context.get("has_rule"):
            return False
        source_id = str(context.get("source_id") or "")
        position = str(context.get("position") or "")
        source = next((item for item in self.items if str(item.get("id") or "") == source_id), None)
        if source is None:
            self.structure_cancel_page_auto_mode(silent=True)
            return False

        key = f"page_auto_{position}_override"
        if context.get("excluded"):
            source.pop(key, None)
            message = "Page réintégrée à la règle générale."
        else:
            source[key] = "__none__"
            message = "Cette page est maintenant une exception à la règle générale."
        source.pop(f"page_auto_{position}_type", None)
        self._sync_page_auto_for_source(source)
        self._save_order()
        source_index = next(
            (i for i, item in enumerate(self.items) if str(item.get("id") or "") == source_id),
            None,
        )
        if source_index is not None:
            self._set_single_page_selection(source_index)
        self.render()
        self._structure_page_auto_mode = None
        self._structure_update_page_auto_visuals()
        self._structure_emit_page_auto_mode()
        self.status_var.set(message)
        return True

    def structure_remove_active_page_auto_rule(self) -> bool:
        context = self.structure_page_auto_context()
        if not context.get("active") or not context.get("has_rule"):
            return False
        source_type = str(context.get("source_type") or "")
        position = str(context.get("position") or "")
        source_label = str(context.get("source_label") or source_type)
        side = str(context.get("side_label") or "")
        ok = self.structure_remove_page_auto_type_rule(source_type, position)
        if not ok:
            return False
        self._structure_page_auto_mode = None
        self._structure_update_page_auto_visuals()
        self._structure_emit_page_auto_mode()
        self.status_var.set(f"Règle Page auto retirée  •  {source_label}  •  {side}")
        return True

    def _structure_open_auto_menu(self, position: str, widget=None) -> None:
        # Compatibilité interne : l'ancien menu est volontairement supprimé.
        self.structure_begin_page_auto_rule(position)

    @staticmethod
    def _structure_normalize_page_payload(payload) -> tuple[str, str]:
        if isinstance(payload, dict):
            page_type = payload.get("type")
            label = payload.get("label") or payload.get("name") or "Sans type"
            return str(page_type or ""), str(label or "Sans type")
        try:
            page_type, label = payload
        except Exception:
            return "", "Sans type"
        return str(page_type or ""), str(label or "Sans type")

    def structure_arm_tool(self, kind: str, payload) -> None:
        if getattr(self, "_work_mode", "structure") != "structure":
            return
        self.structure_cancel_page_auto_mode(silent=True)
        self._structure_pending_kind = str(kind or "")
        self._structure_pending_payload = payload
        self._structure_hover_target = None
        label = "brique"
        if isinstance(payload, dict):
            label = str(payload.get("label") or payload.get("name") or label)
        elif isinstance(payload, (tuple, list)) and len(payload) > 1:
            label = str(payload[1])
        if self._structure_pending_kind == "page":
            self.status_var.set(
                f"{label}  •  dépôt multiple actif  •  cliquez sur la ligne des pages  •  clic hors ligne ou Échap pour terminer"
            )
        else:
            self.status_var.set(
                f"{label}  •  déplacez la souris dans B puis cliquez à l’emplacement voulu"
            )
        try:
            self.canvas.configure(cursor="crosshair")
        except Exception:
            pass
        try:
            self.event_generate("<<StructureToolChanged>>", when="tail")
        except Exception:
            pass
        self.render()

    def structure_pending_page_type(self) -> str:
        if str(getattr(self, "_structure_pending_kind", "") or "") != "page":
            return ""
        page_type, _label = self._structure_normalize_page_payload(
            getattr(self, "_structure_pending_payload", None)
        )
        return str(page_type or "").strip()

    def structure_register_palette_widget(self, widget) -> None:
        """Enregistre la zone C pour distinguer un clic de choix d'un vrai clic extérieur."""
        self._structure_palette_widget = widget

    def structure_cancel_tool(self) -> None:
        self._structure_pending_kind = None
        self._structure_pending_payload = None
        self._structure_hover_target = None
        try:
            self.canvas.configure(cursor="arrow")
        except Exception:
            pass
        try:
            self.event_generate("<<StructureToolChanged>>", when="tail")
        except Exception:
            pass
        self.render()

    def _structure_escape(self, _event=None):
        if getattr(self, "_work_mode", "structure") != "structure":
            return None
        if getattr(self, "_structure_pending_kind", None):
            self.structure_cancel_tool()
            self.status_var.set("Dépôt multiple terminé.")
            return "break"
        if getattr(self, "_structure_page_auto_mode", None):
            self.structure_cancel_page_auto_mode()
            return "break"
        if getattr(self, "_structure_action_mode", None):
            self._structure_reset_action()
            self.status_var.set("Commande annulée.")
            return "break"
        return None

    def _structure_global_click(self, event):
        """Valide les éditeurs au clic extérieur puis gère l'annulation des outils."""
        widget = getattr(event, "widget", None)

        # Le Canvas ne prend pas forcément le focus : un clic extérieur doit
        # néanmoins valider le nom de partie sans exiger la touche Entrée.
        title_editor = getattr(self, "_title_editor", None)
        if title_editor is not None and widget is not title_editor:
            try:
                self._close_title_editor(commit=True)
            except Exception:
                pass

        pending = bool(getattr(self, "_structure_pending_kind", None))
        action = bool(getattr(self, "_structure_action_mode", None))
        if not pending and not action:
            return
        try:
            widget_path = str(widget)
            canvas_path = str(self.canvas)
            bar = getattr(self, "structure_command_bar", None)
            bar_path = str(bar) if bar is not None else ""
            palette = getattr(self, "_structure_palette_widget", None)
            palette_path = str(palette) if palette is not None else ""
            inside_canvas = widget is self.canvas or widget_path.startswith(canvas_path)
            inside_bar = bool(bar_path) and (widget is bar or widget_path.startswith(bar_path))
            inside_palette = bool(palette_path) and (widget is palette or widget_path.startswith(palette_path))
        except Exception:
            inside_canvas = widget is self.canvas
            inside_bar = False
            inside_palette = widget is getattr(self, "_structure_palette_widget", None)
        if not inside_canvas and not inside_bar and not inside_palette:
            # Sécurité ergonomique : le dépôt multiple reste actif uniquement tant
            # que l'utilisateur travaille dans B ou choisit une brique dans C.
            # Un clic réellement extérieur désarme immédiatement le type actif.
            if pending:
                self.after_idle(self.structure_cancel_tool)
            if action:
                self.after_idle(self._structure_reset_action)

    @staticmethod
    def _structure_event(x: float, y: float):
        class Event:
            pass
        event = Event()
        event.x = x
        event.y = y
        return event


    def _structure_apply_type_metadata(self, item: dict, page_type: str, label: str) -> None:
        definition = self._structure_type_definition(page_type)
        if page_type:
            item["type"] = page_type
            item["type_name"] = label
            item["attribute"] = label
            item["title"] = label
            item.pop("untyped", None)
        else:
            item["type"] = ""
            item["type_name"] = "Sans type"
            item["attribute"] = ""
            item["title"] = ""
            item["untyped"] = True

        visual = str(definition.get("visual") or "").strip()
        if visual:
            item["visual"] = visual
        else:
            item.pop("visual", None)

        preview_image = str(definition.get("preview_image") or "").strip()
        if preview_image:
            item["type_preview_image"] = preview_image
        else:
            item.pop("type_preview_image", None)

        item["structure_side"] = self.structure_get_recto_verso_type_rule(page_type) or str(definition.get("side") or "libre")
        item["structure_blank_before"] = bool(definition.get("blank_before", False))
        item["structure_blank_after"] = bool(definition.get("blank_after", False))
        item["structure_duplicable"] = bool(definition.get("duplicable", True))

        if page_type == "tete_partie":
            item["part_head"] = True
        else:
            item.pop("part_head", None)
            item.pop("is_part_head", None)
            item.pop("tete_partie", None)

    def _structure_insert_page(self, page_type: str, label: str, group_id: str, local_pos: int) -> int | None:
        if self.project is None:
            return None
        page_type = str(page_type or "")
        label = str(label or ("Sans type" if not page_type else "Page")).strip() or (
            "Sans type" if not page_type else "Page"
        )
        item = {
            "id": f"MAQUETTE-{uuid4().hex[:12].upper()}",
            "count": 1,
            "done": False,
            "plan_group": group_id,
        }
        self._structure_apply_type_metadata(item, page_type, label)
        self.items.append(item)
        self._move_page_to_group_position(item, group_id, local_pos)
        try:
            index = self.items.index(item)
        except ValueError:
            index = None
        self._selected_index = index
        self._selected_group_id = group_id
        self._structure_selection_kind = "page"
        if item in self.items:
            self._sync_page_auto_for_source(item)
        self._save_order()
        self.render()
        return index

    def _structure_change_page_type(self, index: int, page_type: str, label: str) -> bool:
        if not 0 <= int(index) < len(self.items):
            return False
        item = self.items[int(index)]
        if self._is_locked_page(item) or self._is_automatic_page(item):
            self.status_var.set("Cette page est verrouillée : son type ne peut pas être remplacé.")
            return False

        page_type = str(page_type or "").strip()
        label = str(label or ("Sans type" if not page_type else "Page")).strip() or (
            "Sans type" if not page_type else "Page"
        )
        source_id = str(item.get("id") or "").strip()
        old_type = self._type_of(item)
        if old_type == page_type:
            self.status_var.set(f"Type déjà appliqué  •  {label}")
            return False

        for key in (
            "page_auto_before_override", "page_auto_after_override",
            "page_auto_before_type", "page_auto_after_type",
            "recto_verso_override", "recto_verso_conflict",
            "double_page_override", "double_page_conflict",
        ):
            item.pop(key, None)

        self._structure_apply_type_metadata(item, page_type, label)
        self._sync_structural_automatic_pages()
        self._save_order()
        restored = next((i for i, candidate in enumerate(self.items) if str(candidate.get("id") or "") == source_id), None)
        if restored is not None:
            self._set_single_page_selection(restored)
        self.render()
        self.status_var.set(f"Type remplacé  •  {label}")
        return True

    def structure_replace_selected_page_type(self, type_key: str) -> bool:
        """Remplace le type des pages manuelles sélectionnées sans changer leur ID."""
        type_key = str(type_key or "").strip()
        available = {key: label for key, label, _custom in self.structure_available_page_types()}
        if type_key not in available:
            self.status_var.set("Type de page indisponible.")
            return False

        indices = self._selected_source_indices()
        if not indices:
            self.status_var.set("Sélectionnez d’abord une page dans B.")
            return False
        sources = [self.items[index] for index in indices if 0 <= index < len(self.items)]
        if not sources or any(self._is_locked_page(item) or self._is_automatic_page(item) for item in sources):
            self.status_var.set("Une page automatique ou protégée ne peut pas changer de type.")
            return False

        label = str(available[type_key] or type_key.replace("_", " ").capitalize())
        if all(self._type_of(item) == type_key for item in sources):
            self.status_var.set(f"Type déjà appliqué  •  {label}")
            return False

        source_ids = [str(item.get("id") or "").strip() for item in sources]
        for item in sources:
            for key in (
                "page_auto_before_override", "page_auto_after_override",
                "page_auto_before_type", "page_auto_after_type",
                "recto_verso_override", "recto_verso_conflict",
                "double_page_override", "double_page_conflict",
            ):
                item.pop(key, None)
            self._structure_apply_type_metadata(item, type_key, label)

        self._sync_structural_automatic_pages()
        self._save_order()
        restored = [
            index for index, item in enumerate(self.items)
            if str(item.get("id") or "").strip() in set(source_ids) and not self._is_automatic_page(item)
        ]
        self._set_multi_page_selection(restored)
        self.render()
        count = len(restored)
        self.status_var.set(
            f"Type remplacé  •  {label}" if count <= 1
            else f"Type remplacé  •  {count} pages → {label}"
        )
        return True

    def structure_gabarits_snapshot(self) -> dict:
        """Photographie en lecture seule du squelette destinée à Gabarits/Production."""
        group_map = {
            str(group.get("id") or ""): {
                "id": str(group.get("id") or ""),
                "name": self._group_name(group),
                "title": self._group_part_title(group),
                "order": order,
            }
            for order, group in enumerate(self.groups)
            if isinstance(group, dict)
        }

        pages: list[dict] = []
        physical_index = 0
        group_page_order: dict[str, int] = {}
        conflict_count = 0
        for structure_index, item in enumerate(self.items):
            if not isinstance(item, dict):
                continue
            group_id = self._item_group_id(item)
            group_page_order[group_id] = group_page_order.get(group_id, 0) + 1
            automatic = self._is_automatic_page(item)
            locked = self._is_locked_page(item)
            double_page = False if automatic else bool(self._effective_double_page_rule(item))
            pair_id = "" if automatic else self._double_page_pair_id(item)
            pair_role = "" if automatic else self._double_page_pair_role(item)
            pair_peer_id = "" if automatic else self._double_page_pair_peer_id(item)

            if locked:
                physical_side = "hors_parite"
                physical_from = None
                physical_to = None
            else:
                physical_from = physical_index + 1
                physical_side = "verso_recto" if double_page else ("recto" if physical_index % 2 == 0 else "verso")
                physical_index += 2 if double_page else 1
                physical_to = physical_index

            conflicts = []
            if bool(item.get("recto_verso_conflict")):
                conflicts.append("recto_verso")
            if bool(item.get("double_page_conflict")):
                conflicts.append("double_page")
            if bool(item.get("double_page_pair_conflict")):
                conflicts.append("double_page_pair")
            if bool(item.get("automatic_type_conflict")):
                conflicts.append("type_auto")
            if conflicts:
                conflict_count += 1

            roles = [dict(role) for role in self._automatic_roles(item)] if automatic else []
            pages.append({
                "id": str(item.get("id") or ""),
                "type": self._type_of(item),
                "label": self._page_type_label(item, structure_index),
                "group_id": group_id,
                "group_name": group_map.get(group_id, {}).get("name", ""),
                "group_title": group_map.get(group_id, {}).get("title", ""),
                "group_order": group_map.get(group_id, {}).get("order"),
                "order_in_group": group_page_order[group_id] - 1,
                "structure_index": structure_index,
                "automatic": automatic,
                "manual": not automatic,
                "automatic_roles": roles,
                "automatic_shared": bool(item.get("automatic_shared", False)) if automatic else False,
                "physical_side": physical_side,
                "physical_from": physical_from,
                "physical_to": physical_to,
                "double_page": double_page,
                "paired_double_page": bool(pair_id),
                "double_page_pair_id": pair_id,
                "double_page_pair_role": pair_role,
                "double_page_pair_peer_id": pair_peer_id,
                "recto_verso_rule": "" if automatic else self._effective_recto_verso_rule(item),
                "conflicts": conflicts,
            })

        return {
            "schema": "tomelinea.structure.gabarits.v1",
            "project_type": self._structure_project_type(),
            "groups": [dict(group_map[str(group.get("id") or "")]) for group in self.groups if str(group.get("id") or "") in group_map],
            "pages": pages,
            "physical_page_count": physical_index,
            "conflict_count": conflict_count,
        }

    def _structure_renumber_parts(self) -> bool:
        """Maintient les noms structurels Partie 1, Partie 2... selon l’ordre réel."""
        changed = False
        number = 1
        for group in self.groups:
            group_id = str(group.get("id") or "")
            if group_id in {self.START_GROUP_ID, self.END_GROUP_ID}:
                continue
            expected = f"Partie {number}"
            if str(group.get("title") or "") != expected:
                group["title"] = expected
                changed = True
            number += 1
        return changed

    def _structure_insert_group_at_position(self, target: int) -> str | None:
        if self.project is None:
            return None
        middle = [
            dict(group) for group in self.groups
            if str(group.get("id", "")) not in {self.START_GROUP_ID, self.END_GROUP_ID}
        ]
        target = max(0, min(len(middle), int(target)))
        number = len(middle) + 1
        group_id = f"partie_{uuid4().hex[:10]}"
        group = {
            "id": group_id,
            "title": f"Partie {number}",
            "part_title": "",
            "symbol": "book",
            "accent": theme.ACCENT_BRIGHT,
            "protected": False,
        }
        middle.insert(target, group)
        start_group = next(
            (dict(g) for g in self.groups if str(g.get("id", "")) == self.START_GROUP_ID),
            dict(self.DEFAULT_GROUPS[0]),
        )
        end_group = next(
            (dict(g) for g in self.groups if str(g.get("id", "")) == self.END_GROUP_ID),
            dict(self.DEFAULT_GROUPS[-1]),
        )
        self.groups = [start_group, *middle, end_group]
        self._structure_renumber_parts()
        actual_number = next(
            (i for i, g in enumerate(self._movable_group_ids(), start=1) if g == group_id),
            number,
        )
        self._selected_group_id = group_id
        self._structure_selection_kind = "group"
        self._save_order()
        self.render()
        # La partie nouvellement créée devient le point de travail.
        # Si elle est déjà confortablement visible, on évite un grand saut horizontal.
        self.after_idle(self._structure_focus_new_group)
        self.status_var.set(f"Partie créée  •  Partie {actual_number}")
        return group_id

    def _structure_insert_group(self, canvas_x: float) -> str | None:
        return self._structure_insert_group_at_position(self._target_movable_group_index(canvas_x))

    def _structure_valid_local_positions(self, group_id: str) -> list[int]:
        indexes = self._group_items(group_id)
        positions = list(range(len(indexes) + 1))
        if group_id == self.START_GROUP_ID and indexes:
            last_locked = -1
            for local_pos, index in enumerate(indexes):
                if self._is_cover(self.items[index]) or self._is_second_cover(self.items[index]):
                    last_locked = max(last_locked, local_pos)
            positions = [pos for pos in positions if pos >= last_locked + 1]
        elif group_id == self.END_GROUP_ID and indexes:
            first_locked = len(indexes)
            for local_pos, index in enumerate(indexes):
                if self._is_third_cover(self.items[index]) or self._is_back_cover(self.items[index]):
                    first_locked = min(first_locked, local_pos)
            positions = [pos for pos in positions if pos <= first_locked]
        return positions

    def _structure_page_target_x(self, group_id: str, local_pos: int) -> float:
        indexes = self._group_items(group_id)
        bounds = self._group_page_bounds.get(group_id)
        if not indexes:
            if bounds is not None:
                return (bounds[0] + bounds[1]) / 2.0
            return 0.0
        if local_pos <= 0:
            first = self._page_hitboxes.get(indexes[0])
            return (first[0] - 10) if first else (bounds[0] + 8 if bounds else 0.0)
        if local_pos >= len(indexes):
            last = self._page_hitboxes.get(indexes[-1])
            return (last[2] + 10) if last else (bounds[1] - 8 if bounds else 0.0)
        left = self._page_hitboxes.get(indexes[local_pos - 1])
        right = self._page_hitboxes.get(indexes[local_pos])
        if left is not None and right is not None:
            return (left[2] + right[0]) / 2.0
        if right is not None:
            return right[0] - 8
        if left is not None:
            return left[2] + 8
        return (bounds[0] + bounds[1]) / 2.0 if bounds else 0.0

    def _structure_group_target_x(self, target: int) -> float:
        middle_ids = [
            str(group.get("id", "")) for group in self.groups
            if str(group.get("id", "")) not in {self.START_GROUP_ID, self.END_GROUP_ID}
        ]
        start_box = self._group_hitboxes.get(self.START_GROUP_ID)
        end_box = self._group_hitboxes.get(self.END_GROUP_ID)
        if not middle_ids:
            if start_box is not None and end_box is not None:
                return (start_box[2] + end_box[0]) / 2.0
            return 0.0
        if target <= 0:
            first = self._group_hitboxes.get(middle_ids[0])
            if start_box is not None and first is not None:
                return (start_box[2] + first[0]) / 2.0
            return (first[0] - 12) if first else 0.0
        if target >= len(middle_ids):
            last = self._group_hitboxes.get(middle_ids[-1])
            if last is not None and end_box is not None:
                return (last[2] + end_box[0]) / 2.0
            return (last[2] + 12) if last else 0.0
        left = self._group_hitboxes.get(middle_ids[target - 1])
        right = self._group_hitboxes.get(middle_ids[target])
        if left is not None and right is not None:
            return (left[2] + right[0]) / 2.0
        return 0.0

    def _structure_page_line_contains_event(self, event) -> bool:
        """Vrai uniquement dans la bande visuelle occupée par la ligne des pages.

        Le dépôt multiple doit rester très volontaire : B est grand, mais seule
        la ligne du squelette est une zone de dépôt. Un clic au-dessus ou au-
        dessous sert donc à quitter le mode, pas à insérer une page.
        """
        bounds = getattr(self, "_structure_page_line_bounds", None)
        if not bounds:
            return False
        try:
            cy = float(self.canvas.canvasy(event.y))
            y1, y2 = float(bounds[0]), float(bounds[1])
        except Exception:
            return False
        return y1 <= cy <= y2

    def _structure_page_hover_target(self, event):
        if not self._structure_page_line_contains_event(event):
            return None
        cx = self.canvas.canvasx(event.x)
        # La partie de destination est d'abord déterminée par la position du pointeur.
        # Dans l'espace entre deux parties, le milieu de l'espace fait la séparation :
        # moitié gauche = fin de la première, moitié droite = début de la suivante.
        group_id = self._group_id_at_x(cx)
        positions = self._structure_valid_local_positions(group_id)
        if not positions:
            return None
        candidates = []
        for local_pos in positions:
            tx = self._structure_page_target_x(group_id, local_pos)
            candidates.append((abs(cx - tx), int(local_pos), tx))
        _distance, local_pos, tx = min(candidates, key=lambda item: item[0])
        return ("page", group_id, local_pos, tx)

    def _structure_group_hover_target(self, event):
        cx = self.canvas.canvasx(event.x)
        middle_count = sum(
            1 for group in self.groups
            if str(group.get("id", "")) not in {self.START_GROUP_ID, self.END_GROUP_ID}
        )
        candidates = []
        for position in range(middle_count + 1):
            tx = self._structure_group_target_x(position)
            candidates.append((abs(cx - tx), int(position), tx))
        if not candidates:
            return None
        _distance, position, tx = min(candidates, key=lambda item: item[0])
        return ("group", position, tx)

    def _structure_update_hover_target(self, event):
        kind = getattr(self, "_structure_pending_kind", None)
        target = None
        if kind == "page":
            target = self._structure_page_hover_target(event)
        elif kind == "group":
            target = self._structure_group_hover_target(event)
        if target != getattr(self, "_structure_hover_target", None):
            self._structure_hover_target = target
            self.render()
        return target

    def _draw_structure_placement_preview(self) -> None:
        """Un seul repère mobile : la future page/partie suit la souris dans B."""
        target = getattr(self, "_structure_hover_target", None)
        kind = getattr(self, "_structure_pending_kind", None)
        if not target or not kind or self._page_focus:
            return
        if target[0] == "page":
            _kind, group_id, local_pos, cx = target
            boxes = [self._page_hitboxes[i] for i in self._group_items(group_id) if i in self._page_hitboxes]
            if boxes:
                y1 = min(box[1] for box in boxes)
                y2 = max(box[3] for box in boxes)
                h = min(88.0, max(58.0, (y2 - y1) * 0.56))
                cy = (y1 + y2) / 2.0
            else:
                bounds = self._group_page_bounds.get(group_id)
                cy = max(110.0, self.canvas.winfo_height() * 0.58)
                h = 76.0
                if bounds:
                    cx = min(max(cx, bounds[0] + 18), bounds[1] - 18)
            w = max(38.0, h * 0.66)
            x1, x2 = cx - w / 2.0, cx + w / 2.0
            py1, py2 = cy - h / 2.0, cy + h / 2.0
            self.canvas.create_rectangle(
                x1, py1, x2, py2,
                fill="#8FB8A8", stipple="gray50", outline=self.GOLD, width=2,
                tags=("structure_ghost",),
            )
            self.canvas.create_line(cx, py1 - 9, cx, py2 + 9, fill=self.GOLD, width=2, tags=("structure_ghost",))
            group = next((g for g in self.groups if str(g.get("id", "")) == group_id), {})
            label = self._group_name(group)
            title = self._group_part_title(group)
            if title and title != "Titre à définir":
                label = f"{label} — {title}"
            self.canvas.create_text(
                cx, py1 - 17, text=f"Insérer ici  •  {label}",
                fill=theme.ACCENT_BRIGHT, font=(theme.FONT_UI, 7, "bold"),
                tags=("structure_ghost",),
            )
        elif target[0] == "group":
            _kind, position, cx = target
            header_boxes = list(self._group_hitboxes.values())
            if header_boxes:
                y1 = min(box[1] for box in header_boxes)
                y2 = max(box[3] for box in header_boxes)
                cy = (y1 + y2) / 2.0
                h = max(44.0, y2 - y1 - 8)
            else:
                cy, h = 48.0, 46.0
            w = 126.0
            self.canvas.create_rectangle(
                cx - w/2, cy - h/2, cx + w/2, cy + h/2,
                fill="#29463D", stipple="gray50", outline=self.GOLD, width=2,
                tags=("structure_ghost",),
            )
            self.canvas.create_text(
                cx, cy, text="Nouvelle partie", fill=theme.INK,
                font=(theme.FONT_UI, 8, "bold"), tags=("structure_ghost",),
            )

    def _structure_apply_pending_event(self, event):
        kind = getattr(self, "_structure_pending_kind", None)
        payload = getattr(self, "_structure_pending_payload", None)
        if not kind:
            return None
        target = self._structure_update_hover_target(event)
        success = False
        created_group_id = None
        page_label = "Page"
        if kind == "page" and target and target[0] == "page":
            _kind, group_id, local_pos, _tx = target
            page_type, page_label = self._structure_normalize_page_payload(payload)
            success = self._structure_insert_page(page_type, page_label, group_id, local_pos) is not None
        elif kind == "group" and target and target[0] == "group":
            _kind, position, _tx = target
            created_group_id = self._structure_insert_group_at_position(position)
            success = created_group_id is not None

        if kind == "page":
            if target is None:
                # Sécurité : même à l'intérieur de B, un clic hors de la ligne
                # des pages termine immédiatement le dépôt multiple.
                self.structure_cancel_tool()
                self.status_var.set("Dépôt multiple terminé.")
                return "break"

            # Dépôt multiple : une insertion réussie ne désarme jamais la brique.
            # L'utilisateur peut immédiatement cliquer à un autre emplacement
            # de la ligne du squelette.
            self._structure_hover_target = None
            if success:
                self.status_var.set(
                    f"{page_label} ajouté  •  dépôt multiple actif  •  cliquez sur la ligne pour continuer  •  clic hors ligne ou Échap pour terminer"
                )
            try:
                self.canvas.configure(cursor="crosshair")
            except Exception:
                pass
            self.render()
        else:
            self.structure_cancel_tool()

        # Dès qu'une partie est créée, proposer immédiatement son nommage.
        if success and created_group_id:
            self.after_idle(
                lambda gid=created_group_id: self._begin_group_title_edit(gid)
            )
        return "break"

    def structure_drop_from_root(self, kind: str, payload, root_x: int, root_y: int) -> bool:
        if getattr(self, "_work_mode", "structure") != "structure":
            return False
        try:
            left = self.canvas.winfo_rootx()
            top = self.canvas.winfo_rooty()
            width = self.canvas.winfo_width()
            height = self.canvas.winfo_height()
        except Exception:
            return False
        x = int(root_x) - int(left)
        y = int(root_y) - int(top)
        if x < 0 or y < 0 or x > width or y > height:
            return False
        success = self._structure_apply_at(str(kind), payload, x, y, direct_drop=True)
        if success:
            self.structure_cancel_tool()
        return bool(success)

    def structure_rename_selected(self) -> bool:
        kind = getattr(self, "_structure_selection_kind", "page")
        if kind == "group" and self._selected_group_id:
            self._begin_group_title_edit(self._selected_group_id)
            return True
        if self._selected_index is not None and 0 <= self._selected_index < len(self.items):
            self._begin_page_name_edit(self._selected_index)
            return True
        if self._selected_group_id:
            self._begin_group_title_edit(self._selected_group_id)
            return True
        self.status_var.set("Sélectionnez d'abord une page ou une partie dans B.")
        return False

    def structure_duplicate_selected(self, count: int = 1) -> bool:
        count = max(1, min(50, int(count or 1)))
        kind = getattr(self, "_structure_selection_kind", "page")
        if kind == "group":
            group_id = str(self._selected_group_id or "")
            if group_id in {self.START_GROUP_ID, self.END_GROUP_ID}:
                self.status_var.set("Le début et la fin du livre sont protégés.")
                return False
            source_group = next((g for g in self.groups if str(g.get("id") or "") == group_id), None)
            if source_group is None:
                return False
            try:
                source_pos = next(i for i, g in enumerate(self.groups) if str(g.get("id") or "") == group_id)
            except StopIteration:
                return False

            originals = [
                item for item in self.items
                if self._item_group_id(item) == group_id and not self._is_automatic_page(item)
            ]
            created_groups = []
            all_clones = []
            for copy_no in range(1, count + 1):
                new_group = deepcopy(source_group)
                new_group_id = f"partie_{uuid4().hex[:10]}"
                new_group["id"] = new_group_id
                part_title = str(new_group.get("part_title") or "").strip()
                if part_title:
                    suffix = "copie" if count == 1 else f"copie {copy_no}"
                    new_group["part_title"] = f"{part_title} {suffix}"
                self.groups.insert(source_pos + copy_no, new_group)
                created_groups.append(new_group_id)

                clones = []
                for item in originals:
                    clone = deepcopy(item)
                    clone["id"] = f"MAQUETTE-{uuid4().hex[:12].upper()}"
                    clone["plan_group"] = new_group_id
                    for key in (
                        "automatic_recto_verso", "automatic", "auto_generated", "automatic_kind",
                        "recto_target_id", "linked_to", "parent_id", "source_page_id",
                    ):
                        clone.pop(key, None)
                    clones.append(clone)
                self._rewire_cloned_double_page_pairs(originals, clones)
                self.items.extend(clones)
                all_clones.extend(clones)

            self._structure_renumber_parts()
            for clone in list(all_clones):
                self._sync_page_auto_for_source(clone)
            self._selected_group_id = created_groups[-1]
            self._selected_index = None
            self._selected_page_ids.clear()
            self._structure_selection_kind = "group"
            self._save_order()
            self.render()
            self.status_var.set(f"Partie dupliquée ×{count}." if count > 1 else "Partie dupliquée.")
            return True

        indices = self._selected_source_indices()
        if not indices:
            self.status_var.set("Sélectionnez une ou plusieurs pages à dupliquer.")
            return False
        sources = [self.items[index] for index in indices]
        for item in sources:
            if self._is_locked_page(item):
                self.status_var.set("La sélection contient une page structurelle protégée.")
                return False
            if item.get("structure_duplicable", True) is False:
                self.status_var.set("La sélection contient un type de page non duplicable.")
                return False

        source_ids = {id(item) for item in sources}
        clones_by_group: dict[str, list[dict]] = {}
        insertion_after_by_group: dict[str, int] = {}

        for group in self.groups:
            group_id = str(group.get("id") or "")
            grouped = [item for item in self.items if self._item_group_id(item) == group_id]
            group_sources = [item for item in grouped if id(item) in source_ids]
            if not group_sources:
                continue

            last_pos = -1
            for source in group_sources:
                linked_ids = {id(auto) for auto in self._linked_automatic_items(source)}
                for pos, candidate in enumerate(grouped):
                    if candidate is source or id(candidate) in linked_ids:
                        last_pos = max(last_pos, pos)

            clones = []
            for copy_no in range(1, count + 1):
                copy_clones = []
                for source in group_sources:
                    source_index = self.items.index(source)
                    clone = deepcopy(source)
                    clone["id"] = f"MAQUETTE-{uuid4().hex[:12].upper()}"
                    for key in (
                        "automatic_recto_verso", "automatic", "auto_generated", "automatic_kind",
                        "recto_target_id", "linked_to", "parent_id", "source_page_id",
                    ):
                        clone.pop(key, None)
                    name = self._page_display_name(source, source_index)
                    if name:
                        suffix = "copie" if count == 1 else f"copie {copy_no}"
                        clone["page_name"] = f"{name} {suffix}"
                    copy_clones.append(clone)
                self._rewire_cloned_double_page_pairs(group_sources, copy_clones)
                clones.extend(copy_clones)
            clones_by_group[group_id] = clones
            insertion_after_by_group[group_id] = last_pos

        rebuilt: list[dict] = []
        all_clones: list[dict] = []
        for group in self.groups:
            group_id = str(group.get("id") or "")
            grouped = [item for item in self.items if self._item_group_id(item) == group_id]
            clones = clones_by_group.get(group_id, [])
            if not clones:
                rebuilt.extend(grouped)
                continue
            insert_at = max(0, min(len(grouped), insertion_after_by_group[group_id] + 1))
            grouped = [*grouped[:insert_at], *clones, *grouped[insert_at:]]
            rebuilt.extend(grouped)
            all_clones.extend(clones)

        self.items = rebuilt
        for clone in list(all_clones):
            if clone in self.items:
                self._sync_page_auto_for_source(clone)

        self._save_order()
        clone_ids = {str(clone.get("id") or "") for clone in all_clones}
        clone_indices = [
            index for index, item in enumerate(self.items)
            if str(item.get("id") or "") in clone_ids
        ]
        self._set_multi_page_selection(clone_indices)
        self.render()
        total = len(all_clones)
        if count > 1:
            self.status_var.set(f"Duplication ×{count} terminée  •  {total} page(s) créée(s) avec leurs pages auto.")
        else:
            self.status_var.set(
                "Pages dupliquées avec leurs pages auto."
                if total > 1 else
                "Page dupliquée avec ses pages auto."
            )
        return True

    def structure_delete_selected(self) -> bool:
        kind = getattr(self, "_structure_selection_kind", "page")
        if kind == "group" and self._selected_group_id:
            group_id = self._selected_group_id
            if group_id in {self.START_GROUP_ID, self.END_GROUP_ID}:
                self.status_var.set("Le début et la fin du livre sont protégés.")
                return False

            try:
                group_pos = next(
                    i for i, group in enumerate(self.groups)
                    if str(group.get("id", "")) == group_id
                )
            except StopIteration:
                return False

            # Une partie est un bloc structurel : la supprimer supprime aussi
            # toutes les pages qu'elle contient, y compris les pages auto liées.
            self.items = [
                item for item in self.items
                if self._item_group_id(item) != group_id
            ]
            self.groups = [
                group for group in self.groups
                if str(group.get("id", "")) != group_id
            ]
            self._structure_renumber_parts()

            # On conserve une sélection structurelle valide sans recentrer B.
            if self.groups:
                neighbor_pos = min(max(0, group_pos - 1), len(self.groups) - 1)
                self._selected_group_id = str(self.groups[neighbor_pos].get("id", ""))
            else:
                self._selected_group_id = None
            self._selected_index = None
            self._selected_page_ids.clear()
            self._structure_selection_kind = "group"
            self._save_order()
            self.render()
            self.status_var.set("Partie supprimée avec son contenu.")
            return True

        indices = self._selected_source_indices()
        if not indices:
            self.status_var.set("Sélectionnez une ou plusieurs pages à supprimer.")
            return False
        if any(self._is_locked_page(self.items[index]) for index in indices):
            self.status_var.set("La sélection contient une page structurelle protégée.")
            return False

        first_index = min(indices)
        block: set[int] = set()
        for index in indices:
            block.update(self._drag_block_indices(index))
        self.items = [item for i, item in enumerate(self.items) if i not in block]

        # Après une suppression, ne pas agrandir automatiquement la page voisine :
        # cela décalait visuellement toute la ligne alors que l'utilisateur
        # n'avait demandé qu'une suppression.
        self._selected_page_ids.clear()
        self._selected_index = None
        self._structure_selection_kind = "page"
        self._save_order()
        self.render()
        self.status_var.set("Pages supprimées." if len(indices) > 1 else "Page supprimée.")
        return True

    def structure_insert_blank_relative(self, position: str) -> bool:
        index = self._selected_index
        if index is None or not 0 <= index < len(self.items):
            self.status_var.set("Sélectionnez d'abord une page dans B.")
            return False
        item = self.items[index]
        group_id = self._item_group_id(item)
        group_indexes = self._group_items(group_id)
        if index not in group_indexes:
            return False
        local_pos = group_indexes.index(index) + (1 if str(position) == "after" else 0)
        valid = self._structure_valid_local_positions(group_id)
        if local_pos not in valid:
            self.status_var.set("Impossible d’insérer une page à cet endroit structurel.")
            return False
        return self._structure_insert_page("page_blanche", "Page blanche", group_id, local_pos) is not None

    def set_project(self, project):
        if getattr(self, "_overlay_active", False):
            self.close_page_overlay()
        self.project = project
        self.items = []
        self.groups = [dict(group) for group in self.DEFAULT_GROUPS]
        self._data = {}

        if project is not None:
            try:
                data = project.load_mockup()
                if not isinstance(data, dict):
                    data = {}
            except Exception:
                data = {}

            data, changed = self._ensure_minimum_structure(data)
            self._data = data
            self.groups = [dict(group) for group in data.get("groups", []) if isinstance(group, dict)]
            self.items = [dict(item) for item in data.get("items", []) if isinstance(item, dict)]
            # Toutes les règles structurelles sont réconciliées ensemble :
            # une seule page auto peut satisfaire AV/AP et R/V.
            auto_changed = self._sync_structural_automatic_pages()
            if auto_changed:
                data["groups"] = [dict(group) for group in self.groups]
                data["items"] = [dict(item) for item in self.items]
                data, normalized = self._ensure_minimum_structure(data)
                changed = changed or normalized or auto_changed
                self._data = data
                self.groups = [dict(group) for group in data.get("groups", []) if isinstance(group, dict)]
                self.items = [dict(item) for item in data.get("items", []) if isinstance(item, dict)]

            if changed:
                try:
                    saved = project.save_mockup(data)
                    if isinstance(saved, dict):
                        data = saved
                        self._data = deepcopy(saved)
                        self.groups = [dict(group) for group in saved.get("groups", []) if isinstance(group, dict)]
                        self.items = [dict(item) for item in saved.get("items", []) if isinstance(item, dict)]
                except Exception:
                    pass
            else:
                # Recharge l'état réellement persisté afin que l'historique parte
                # exactement de la version visible à l'ouverture.
                try:
                    loaded = project.load_mockup()
                    if isinstance(loaded, dict):
                        data = loaded
                        self._data = deepcopy(loaded)
                except Exception:
                    pass

        self._history_reset(self._data if isinstance(self._data, dict) else {})
        self._selected_index = 0 if self.items else None
        self._selected_group_id = None
        self._selected_page_ids.clear()
        if self.items:
            source_index = self._source_index_for_index(0)
            if source_index is not None:
                source_id = str(self.items[source_index].get("id") or "").strip()
                if source_id:
                    self._selected_page_ids = {source_id}
                    self._selected_index = source_index
        self._page_focus = False
        self.render()
        try:
            self.event_generate("<<StructurePaletteChanged>>", when="tail")
        except Exception:
            pass
        if self.items:
            self.after_idle(self._open_default_view)

    def _ensure_minimum_structure(self, source: dict) -> tuple[dict, bool]:
        data = deepcopy(source) if isinstance(source, dict) else {}
        changed = False

        defaults = {str(group["id"]): dict(group) for group in self.DEFAULT_GROUPS}
        raw_groups = data.get("groups", [])
        middle: list[dict] = []
        seen: set[str] = set()
        structural_titles: dict[str, str] = {}
        if isinstance(raw_groups, list):
            for raw in raw_groups:
                if not isinstance(raw, dict) or bool(raw.get("deleted", False)):
                    continue
                group_id = str(raw.get("id", "")).strip()
                if not group_id or group_id in seen:
                    continue
                if group_id in {self.START_GROUP_ID, self.END_GROUP_ID}:
                    structural_titles[group_id] = str(
                        raw.get("part_title") or raw.get("titre_partie") or raw.get("subtitle") or ""
                    ).strip()
                    seen.add(group_id)
                    continue
                title = str(raw.get("title") or raw.get("name") or "Partie").strip() or "Partie"
                part_title = str(
                    raw.get("part_title")
                    or raw.get("titre_partie")
                    or raw.get("subtitle")
                    or ""
                ).strip()
                accent = str(raw.get("accent") or theme.ACCENT_BRIGHT)
                middle.append(
                    {
                        **raw,
                        "id": group_id,
                        "title": title,
                        "part_title": part_title,
                        "symbol": str(raw.get("symbol") or "book"),
                        "accent": accent,
                        "protected": False,
                    }
                )
                seen.add(group_id)

        if self.DEFAULT_GROUP_ID not in seen:
            middle.insert(0, dict(defaults[self.DEFAULT_GROUP_ID]))

        start_group = dict(defaults[self.START_GROUP_ID])
        end_group = dict(defaults[self.END_GROUP_ID])
        if self.START_GROUP_ID in structural_titles:
            start_group["part_title"] = structural_titles[self.START_GROUP_ID]
        if self.END_GROUP_ID in structural_titles:
            end_group["part_title"] = structural_titles[self.END_GROUP_ID]
        groups = [start_group, *middle, end_group]
        if data.get("groups") != groups:
            data["groups"] = groups
            changed = True

        valid_group_ids = [str(group.get("id", "")) for group in groups]
        valid_group_set = set(valid_group_ids)
        page_type_group: dict[str, str] = {}
        raw_defs = data.get("page_types", [])
        if isinstance(raw_defs, list):
            for definition in raw_defs:
                if not isinstance(definition, dict):
                    continue
                page_type = str(definition.get("type", "")).strip()
                group_id = str(definition.get("group", "")).strip()
                if page_type and group_id in valid_group_set:
                    page_type_group[page_type] = group_id

        raw_items = data.get("items", [])
        items = [dict(item) for item in raw_items if isinstance(item, dict)] if isinstance(raw_items, list) else []

        cover = next((item for item in items if self._is_cover(item)), None)
        back = next((item for item in items if self._is_back_cover(item)), None)
        if cover is None:
            cover = {
                "id": f"MAQUETTE-{uuid4().hex[:12].upper()}",
                "type": "couverture",
                "title": "Couverture",
                "count": 1,
                "done": False,
                "plan_group": self.START_GROUP_ID,
            }
            items.insert(0, cover)
            changed = True
        if back is None:
            back = {
                "id": f"MAQUETTE-{uuid4().hex[:12].upper()}",
                "type": "quatrieme",
                "title": "Quatrième de couverture",
                "count": 1,
                "done": False,
                "plan_group": self.END_GROUP_ID,
            }
            items.append(back)
            changed = True

        for item in items:
            # Les anciens champs sont conservés, mais B n'affiche plus de catégorie
            # générique « Page intérieure ». Le libellé visible est le vrai type
            # éditorial (Sommaire, Texte, Illustration, Chapitre, etc.).
            if not str(item.get("attribute", "")).strip():
                item["attribute"] = self._legacy_page_attribute(item)
                changed = True

            old_group = str(item.get("plan_group", "")).strip()
            if self._is_cover(item) or self._is_second_cover(item):
                group_id = self.START_GROUP_ID
            elif self._is_third_cover(item) or self._is_back_cover(item):
                group_id = self.END_GROUP_ID
            elif old_group in valid_group_set:
                group_id = old_group
            else:
                page_type = str(item.get("type", "")).strip()
                group_id = page_type_group.get(page_type, self.DEFAULT_GROUP_ID)
                if group_id not in valid_group_set:
                    group_id = self.DEFAULT_GROUP_ID
            if old_group != group_id:
                item["plan_group"] = group_id
                changed = True

        ordered: list[dict] = []
        for group in groups:
            group_id = str(group.get("id", ""))
            grouped = [item for item in items if str(item.get("plan_group", "")) == group_id]
            if group_id == self.START_GROUP_ID:
                grouped.sort(key=self._start_group_sort_key)
            elif group_id == self.END_GROUP_ID:
                grouped.sort(key=self._end_group_sort_key)
            ordered.extend(grouped)

        # Conserve sans perte un éventuel item dont le groupe serait incohérent.
        known_ids = {id(item) for item in ordered}
        ordered.extend(item for item in items if id(item) not in known_ids)
        if ordered != items:
            changed = True
        data["items"] = ordered
        data.setdefault("page_types", [])
        data.setdefault("recto_verso_rules", [])
        data.setdefault("recto_verso_type_rules", {})
        data.setdefault("page_auto_type_rules", {})
        raw_side_rules = data.get("recto_verso_type_rules", {})
        side_rules = {}
        if isinstance(raw_side_rules, dict):
            for source_type, side in raw_side_rules.items():
                source = str(source_type or "").strip().lower()
                value = str(side or "").strip().lower()
                if source and value in {"recto", "verso"}:
                    side_rules[source] = value
        if raw_side_rules != side_rules:
            data["recto_verso_type_rules"] = side_rules
            changed = True
        for item in data.get("items", []):
            if not isinstance(item, dict) or self._is_automatic_page(item):
                continue
            side = side_rules.get(self._type_of(item))
            effective_side = side if side and item.get("recto_verso_override") != "__none__" else "libre"
            if item.get("structure_side") != effective_side:
                item["structure_side"] = effective_side
                changed = True
        data, legacy_changed = migrate_structure_data(data)
        changed = changed or legacy_changed
        return data, changed

    def _save_order(self):
        if self.project is None:
            return
        selection_snapshot = self._structure_selection_snapshot()
        self._sync_recto_verso_corrections()
        try:
            data = self.project.load_mockup()
        except Exception:
            data = deepcopy(self._data)
        if not isinstance(data, dict):
            data = {}
        data["groups"] = [dict(group) for group in self.groups]
        data["items"] = [dict(item) for item in self.items]
        data, _ = self._ensure_minimum_structure(data)
        self.groups = [dict(group) for group in data.get("groups", []) if isinstance(group, dict)]
        self.items = [dict(item) for item in data.get("items", []) if isinstance(item, dict)]
        saved = self.project.save_mockup(data)
        if not isinstance(saved, dict):
            saved = data
        self._data = deepcopy(saved)
        self.groups = [dict(group) for group in saved.get("groups", []) if isinstance(group, dict)]
        self.items = [dict(item) for item in saved.get("items", []) if isinstance(item, dict)]
        self._structure_restore_selection_snapshot(selection_snapshot)
        self._history_record_saved(saved)
        if self.on_change is not None:
            self.on_change()

    @staticmethod
    def _type_of(item: dict) -> str:
        return str(item.get("type") or item.get("kind") or item.get("page_type") or "").strip().lower()

    def _is_cover(self, item: dict) -> bool:
        return self._type_of(item) in self.COVER_TYPES

    def _is_back_cover(self, item: dict) -> bool:
        return self._type_of(item) in self.BACK_COVER_TYPES

    def _is_second_cover(self, item: dict) -> bool:
        return self._type_of(item) in self.SECOND_COVER_TYPES

    def _is_third_cover(self, item: dict) -> bool:
        return self._type_of(item) in self.THIRD_COVER_TYPES

    def _is_locked_page(self, item: dict) -> bool:
        return self._is_cover(item) or self._is_second_cover(item) or self._is_third_cover(item) or self._is_back_cover(item)

    def _start_group_sort_key(self, item: dict) -> tuple[int]:
        if self._is_cover(item):
            return (0,)
        if self._is_second_cover(item):
            return (1,)
        return (2,)

    def _end_group_sort_key(self, item: dict) -> tuple[int]:
        if self._is_back_cover(item):
            return (2,)
        if self._is_third_cover(item):
            return (1,)
        return (0,)

    def _item_group_id(self, item: dict) -> str:
        if self._is_cover(item) or self._is_second_cover(item):
            return self.START_GROUP_ID
        if self._is_third_cover(item) or self._is_back_cover(item):
            return self.END_GROUP_ID
        group_id = str(item.get("plan_group", "")).strip()
        valid = {str(group.get("id", "")) for group in self.groups}
        return group_id if group_id in valid else self.DEFAULT_GROUP_ID

    def _item_label(self, item: dict, index: int) -> str:
        for key in ("name", "nom", "title", "titre", "label", "type_name", "page_type_name"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        kind = item.get("type") or item.get("kind") or item.get("page_type")
        if isinstance(kind, str) and kind.strip():
            return kind.replace("_", " ").strip().capitalize()
        return f"Page {index + 1}"

    def _legacy_page_attribute(self, item: dict) -> str:
        """Déduit l'attribut éditorial d'un ancien item sans perdre son libellé."""
        if self._is_cover(item):
            return "1re de couverture"
        if self._is_second_cover(item):
            return "2e de couverture"
        if self._is_third_cover(item):
            return "3e de couverture"
        if self._is_back_cover(item):
            return "4e de couverture"
        for key in ("attribut", "role", "fonction", "title", "titre", "name", "nom", "label", "type_name", "page_type_name"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        kind = item.get("type") or item.get("kind") or item.get("page_type")
        if isinstance(kind, str) and kind.strip():
            return kind.replace("_", " ").strip().capitalize()
        return "À définir"

    def _page_type_key(self, item: dict) -> str:
        if self._is_cover(item):
            return "couverture"
        if self._is_second_cover(item):
            return "deuxieme_couverture"
        if self._is_third_cover(item):
            return "troisieme_couverture"
        if self._is_back_cover(item):
            return "quatrieme"
        for key in ("type", "kind", "page_type", "type_name", "page_type_name", "attribute", "attribut"):
            value = item.get(key)
            canonical = canonical_page_type(value)
            if page_visual_definition(canonical) is not None:
                return canonical
        raw = self._type_of(item)
        return canonical_page_type(raw) or raw or "personnalisee"

    def _page_type_label(self, item: dict, index: int | None = None) -> str:
        """Type éditorial visible sous la miniature."""
        definition = page_visual_definition(self._page_type_key(item))
        if definition is not None:
            return str(definition.get("label") or "Page")
        # Type personnalisé existant : ne pas le masquer derrière « Page ».
        for key in ("type_name", "page_type_name", "attribute", "attribut", "role", "fonction"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                value = value.strip()
                if value.lower() not in {"page intérieure", "page interieur", "page interior"}:
                    return value
        raw_type = self._type_of(item)
        if raw_type and raw_type not in {"page", "page_interieure", "page intérieure"}:
            return raw_type.replace("_", " ").strip().capitalize()
        return "Page personnalisée" if index is not None else "Page"

    def _page_attribute_label(self, item: dict, index: int) -> str:
        return self._page_type_label(item, index)

    def _is_automatic_page(self, item: dict) -> bool:
        if bool(item.get("automatic_recto_verso", False) or item.get("automatic", False) or item.get("auto_generated", False)):
            return True
        raw = str(item.get("type") or item.get("kind") or item.get("page_type") or "").strip().lower().replace("_", " ")
        return raw in {"page auto", "page automatique", "auto"}

    def _is_part_head_page(self, item: dict) -> bool:
        if bool(item.get("part_head", False) or item.get("is_part_head", False) or item.get("tete_partie", False)):
            return True
        return self._page_type_key(item) == "tete_partie"

    def _page_display_name(self, item: dict, index: int) -> str:
        for key in ("page_name", "nom_page", "display_name"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        # Les anciens titres ne deviennent un nom que s'ils apportent vraiment
        # une information différente du type de page.
        title = str(item.get("title") or item.get("titre") or "").strip()
        page_type = self._page_type_label(item, index)
        generic = {
            page_type.lower(), "page", "page blanche automatique", "pages blanches automatiques",
            "deuxième de couverture", "troisième de couverture", "quatrième de couverture",
        }
        if title and title.lower() not in generic:
            return title
        return ""

    def _automatic_parent_id(self, item: dict) -> str:
        source_ids = self._automatic_source_ids(item) if isinstance(item, dict) else []
        if len(source_ids) == 1:
            return source_ids[0]
        for key in ("recto_target_id", "linked_to", "parent_id", "source_page_id"):
            value = str(item.get(key) or "").strip()
            if value:
                return value
        return ""

    def _linked_automatic_items(self, item: dict) -> list[dict]:
        item_id = str(item.get("id") or "").strip()
        if not item_id:
            return []
        return [candidate for candidate in self.items if self._is_automatic_page(candidate) and item_id in self._automatic_source_ids(candidate)]

    @staticmethod
    def _group_name(group: dict) -> str:
        return str(group.get("title") or group.get("name") or "Partie").strip() or "Partie"

    @staticmethod
    def _group_part_title(group: dict) -> str:
        value = str(
            group.get("part_title")
            or group.get("titre_partie")
            or group.get("subtitle")
            or ""
        ).strip()
        return value or "Titre à définir"

    # ------------------------------------------------------------------
    # Zoom continu
    # ------------------------------------------------------------------

    @property
    def zoom(self) -> int:
        return max(self.MIN_ZOOM, min(self.MAX_ZOOM, int(self._book_zoom)))

    @property
    def page_focus(self) -> bool:
        return bool(self._page_focus)

    def _normal_page_available_height(self) -> int:
        if not hasattr(self, "canvas"):
            return 180
        viewport_h = max(180, self.canvas.winfo_height())
        reserved = self.MARGIN * 2 + self.GROUP_H + self.GROUP_TO_PAGE + self.PAGE_LABEL_H + self.PAGE_NAME_H
        return max(120, viewport_h - reserved)

    def _book_height_cap(self) -> int:
        # Le plus grand des quatre formats doit tenir entièrement dans B en vue livre.
        value = int(
            self._normal_page_available_height()
            / float(self.BASE_PAGE_H * self.PAGE_SIZE_SELECTED)
            * 100
        )
        return max(self.MIN_ZOOM, min(self.MAX_ZOOM, value))

    def _open_default_view(self):
        """Ouverture confortable : pages plus grandes, sans forcer tout le livre à l'écran."""
        if not self.items or not self.canvas.winfo_exists():
            return
        # L'appel initial peut arriver avant que Tk ait attribué sa vraie hauteur à B.
        # On attend alors le premier vrai Configure au lieu de figer le zoom au minimum.
        if self.canvas.winfo_height() < 280:
            self.after(60, self._open_default_view)
            return
        if self._page_focus:
            self._set_page_focus(False)
        target = min(38, self._book_height_cap())
        self.set_zoom(max(self.MIN_ZOOM, target), center_selected=False)
        self.canvas.yview_moveto(0)
        # À l’ouverture, présenter la première page au centre de B au lieu de
        # plaquer toute la structure contre le bord gauche.
        self.after_idle(self.center_selected)
        self.after_idle(self._update_visible_part_marker)

    def _active_group_id(self) -> str:
        if self._selected_group_id and any(str(g.get("id", "")) == self._selected_group_id for g in self.groups):
            return self._selected_group_id
        if self._selected_index is not None and 0 <= self._selected_index < len(self.items):
            return self._item_group_id(self.items[self._selected_index])
        return self.START_GROUP_ID

    def _structural_auto_is_deployed(self, index: int) -> bool:
        """Une page auto se déploie lorsque l'une de ses pages de référence est sélectionnée."""
        if not 0 <= index < len(self.items):
            return False
        item = self.items[index]
        if not self._is_automatic_page(item):
            return False
        selected_ids = set(getattr(self, "_selected_page_ids", set()) or set())
        if self._selected_index is not None and 0 <= self._selected_index < len(self.items):
            selected_id = str(self.items[self._selected_index].get("id") or "").strip()
            if selected_id:
                selected_ids.add(selected_id)
        return bool(selected_ids.intersection(self._automatic_source_ids(item)))

    def _page_size_factor(self, index: int, active_group_id: str | None = None) -> float:
        """Trois tailles utiles : sélectionnée, page normale et page automatique rétractée."""
        if not 0 <= index < len(self.items):
            return self.PAGE_SIZE_NORMAL
        item = self.items[index]
        if index == self._selected_index:
            return self.PAGE_SIZE_SELECTED
        if self._is_automatic_page(item):
            return self.PAGE_SIZE_AUTO
        return self.PAGE_SIZE_NORMAL

    def _set_page_focus(self, active: bool):
        active = bool(active)
        if active == self._page_focus:
            return
        if active and self._selected_index is None:
            if not self.items:
                return
            self._selected_index = 0
        self._page_focus = active
        if self.on_focus_change is not None:
            self.on_focus_change(active)

    def _on_viewer_scale(self, value):
        """Le curseur visible zoome uniquement la page en surimpression."""
        try:
            value = int(float(value))
        except (TypeError, ValueError):
            return
        self.set_viewer_zoom(value, fast=True)

    def set_zoom(self, value: int, *, center_selected=True):
        """Zoom interne de la ligne du livre (non piloté par l'utilisateur)."""
        value = max(self.MIN_ZOOM, min(self.MAX_ZOOM, int(value)))
        if self._page_focus:
            self._set_page_focus(False)
        if value == self.zoom:
            return
        self._book_zoom = value
        self.render()
        if center_selected and self._selected_index is not None:
            self.after_idle(self.center_selected)

    def step_zoom(self, delta: int):
        """Zoom de la page seule ; ouvre la surimpression si nécessaire."""
        if not self._overlay_active:
            self.open_page_overlay()
            if not self._overlay_active:
                return
        current = int(self.viewer_zoom_var.get())
        if current < 160:
            step = 10
        elif current < 300:
            step = 20
        else:
            step = 40
        self.set_viewer_zoom(current + (step if delta > 0 else -step), fast=False)

    # ------------------------------------------------------------------
    # Visionneuse locale de page (surimpression dans B)
    # ------------------------------------------------------------------

    def open_page_overlay(self, index: int | None = None, *, reset_zoom: bool = True):
        if not self.items:
            return
        if index is None:
            index = self._selected_index if self._selected_index is not None else 0
        if not (0 <= int(index) < len(self.items)):
            return
        index = int(index)
        self._selected_index = index
        self._selected_group_id = self._item_group_id(self.items[index])
        self._overlay_page_index = index
        self._overlay_active = True
        self._overlay_pan_x = 0.0
        self._overlay_pan_y = 0.0
        self._overlay_zoom_anchor = None
        self._overlay_zoom_ratio = (0.5, 0.5)
        if reset_zoom:
            self.viewer_zoom_var.set(100)
            self.zoom_text_var.set("100 %")
        self.page_overlay_frame.place(x=0, y=0, relwidth=1, relheight=1)
        # La couche est un simple widget Tk dans la fenêtre TomeLinea :
        # aucun Toplevel, aucun changement de géométrie de B.
        self.page_overlay_frame.tk.call("raise", self.page_overlay_frame._w)
        try:
            self.page_overlay.focus_set()
        except Exception:
            pass
        self._schedule_overlay_render()

    def close_page_overlay(self):
        if not getattr(self, "_overlay_active", False):
            return
        self._overlay_active = False
        self._overlay_page_index = None
        self._overlay_pan_x = 0.0
        self._overlay_pan_y = 0.0
        self._overlay_page_box = None
        self._overlay_drag_origin = None
        self._overlay_pan_origin = None
        self._overlay_zoom_anchor = None
        if self._overlay_render_job is not None:
            try:
                self.after_cancel(self._overlay_render_job)
            except Exception:
                pass
            self._overlay_render_job = None
        if self._overlay_quality_job is not None:
            try:
                self.after_cancel(self._overlay_quality_job)
            except Exception:
                pass
            self._overlay_quality_job = None
        self.page_overlay_frame.place_forget()
        self._overlay_image_refs = []
        self._overlay_brand_refs = []
        self._overlay_bg_photo = None
        self.zoom_text_var.set("100 %")
        self.viewer_zoom_var.set(100)
        try:
            self.canvas.focus_set()
        except Exception:
            pass

    def set_viewer_zoom(self, value: int, *, fast: bool = False):
        if not self._overlay_active:
            self.open_page_overlay(reset_zoom=True)
            if not self._overlay_active:
                return
        value = max(100, min(500, int(value)))
        current = int(self.viewer_zoom_var.get())
        if value == current and bool(fast) == bool(self._overlay_fast):
            return

        width = max(1.0, float(self.page_overlay.winfo_width()))
        height = max(1.0, float(self.page_overlay.winfo_height()))
        center_y = (height - 34.0) / 2.0
        anchor = self._overlay_zoom_anchor
        box = self._overlay_page_box
        rx, ry = self._overlay_zoom_ratio
        if anchor is None or box is None:
            ax, ay = width / 2.0, center_y
        else:
            ax, ay = anchor
            x1, y1, x2, y2 = box
            if x2 > x1 and y2 > y1:
                rx = max(0.0, min(1.0, (ax - x1) / (x2 - x1)))
                ry = max(0.0, min(1.0, (ay - y1) / (y2 - y1)))
        self._overlay_zoom_ratio = (rx, ry)

        self.viewer_zoom_var.set(value)
        self.zoom_text_var.set(f"{value} %")
        self._overlay_fast = bool(fast)

        page_w, page_h, _scale = self._overlay_dimensions()
        self._overlay_pan_x = ax - width / 2.0 + page_w * (0.5 - rx)
        self._overlay_pan_y = ay - center_y + page_h * (0.5 - ry)
        self._clamp_overlay_pan()
        self._schedule_overlay_render()
        if fast:
            if self._overlay_quality_job is not None:
                try:
                    self.after_cancel(self._overlay_quality_job)
                except Exception:
                    pass
            self._overlay_quality_job = self.after(110, self._overlay_finish_quality)

    def _overlay_finish_quality(self):
        self._overlay_quality_job = None
        if not self._overlay_active:
            return
        self._overlay_fast = False
        self._schedule_overlay_render()

    def _overlay_zoom_release(self, _event=None):
        self._overlay_fast = False
        self._overlay_finish_quality()

    def _overlay_motion(self, event):
        if not self._overlay_active:
            return
        box = self._overlay_page_box
        if box is None:
            return
        x1, y1, x2, y2 = box
        if x1 <= event.x <= x2 and y1 <= event.y <= y2:
            self._overlay_zoom_anchor = (float(event.x), float(event.y))
            width = max(1.0, x2 - x1)
            height = max(1.0, y2 - y1)
            self._overlay_zoom_ratio = ((float(event.x) - x1) / width, (float(event.y) - y1) / height)

    def _overlay_zoom_navigate(self, velocity: float):
        velocity = float(velocity)
        current = int(self.viewer_zoom_var.get())
        if abs(velocity) < 0.001:
            return
        if current < 160:
            base = 8
        elif current < 260:
            base = 14
        else:
            base = 24
        delta = int(round(base * velocity))
        if delta == 0:
            delta = 1 if velocity > 0 else -1
        self.set_viewer_zoom(current + delta, fast=True)

    def _schedule_overlay_render(self, _event=None):
        if not getattr(self, "_overlay_active", False):
            return
        if self._overlay_render_job is None:
            self._overlay_render_job = self.after(16, self._render_page_overlay)

    def _overlay_fit_scale(self) -> float:
        width = max(420, self.page_overlay.winfo_width())
        height = max(320, self.page_overlay.winfo_height())
        # La visionneuse utilise maintenant presque toute la fenêtre. On garde
        # seulement une respiration latérale et l'espace du petit poste de zoom.
        usable_h = max(240, height - 78)
        # 88 % laisse encore la page entièrement visible au premier cran de zoom
        # (110 %) tout en exploitant nettement plus d'espace que l'ancien B.
        return min((width * 0.88) / self.BASE_PAGE_W, (usable_h * 0.82) / self.BASE_PAGE_H)

    def _overlay_dimensions(self) -> tuple[float, float, float]:
        fit = self._overlay_fit_scale()
        factor = max(1.0, float(self.viewer_zoom_var.get()) / 100.0)
        scale = fit * factor
        return self.BASE_PAGE_W * scale, self.BASE_PAGE_H * scale, scale

    def _clamp_overlay_pan(self):
        if not getattr(self, "_overlay_active", False):
            return
        width = max(1, self.page_overlay.winfo_width())
        height = max(1, self.page_overlay.winfo_height())
        page_w, page_h, _scale = self._overlay_dimensions()
        max_x = max(0.0, (page_w - width * 0.94) / 2.0)
        max_y = max(0.0, (page_h - height * 0.94) / 2.0)
        if max_x <= 0.0:
            self._overlay_pan_x = 0.0
        else:
            self._overlay_pan_x = max(-max_x, min(max_x, self._overlay_pan_x))
        if max_y <= 0.0:
            self._overlay_pan_y = 0.0
        else:
            self._overlay_pan_y = max(-max_y, min(max_y, self._overlay_pan_y))

    def _overlay_press(self, event):
        if not self._overlay_active:
            return "break"
        box = self._overlay_page_box
        if box is None:
            return "break"
        x1, y1, x2, y2 = box
        if not (x1 <= event.x <= x2 and y1 <= event.y <= y2):
            self.close_page_overlay()
            return "break"
        self._overlay_drag_origin = (float(event.x), float(event.y))
        self._overlay_pan_origin = (self._overlay_pan_x, self._overlay_pan_y)
        if int(self.viewer_zoom_var.get()) > 112:
            self.page_overlay.configure(cursor="fleur")
        return "break"

    def _overlay_drag(self, event):
        if self._overlay_drag_origin is None or self._overlay_pan_origin is None:
            return "break"
        if int(self.viewer_zoom_var.get()) <= 112:
            return "break"
        dx = float(event.x) - self._overlay_drag_origin[0]
        dy = float(event.y) - self._overlay_drag_origin[1]
        # On déplace la page sous la main, comme une feuille sur une table.
        self._overlay_pan_x = self._overlay_pan_origin[0] + dx
        self._overlay_pan_y = self._overlay_pan_origin[1] + dy
        self._clamp_overlay_pan()
        self._schedule_overlay_render()
        return "break"

    def _overlay_release(self, _event=None):
        self._overlay_drag_origin = None
        self._overlay_pan_origin = None
        self.page_overlay.configure(cursor="arrow")
        return "break"

    def _overlay_mousewheel(self, event):
        if event.delta == 0:
            return "break"
        self._overlay_motion(event)
        self.step_zoom(1 if event.delta > 0 else -1)
        return "break"

    def _draw_overlay_book_icon(self, target: tk.Canvas, x: float, y: float, accent: str):
        target.create_polygon(x - 11, y - 7, x - 1, y - 4, x - 1, y + 8, x - 11, y + 5, fill="", outline=accent, width=2)
        target.create_polygon(x + 1, y - 4, x + 11, y - 7, x + 11, y + 5, x + 1, y + 8, fill="", outline=accent, width=2)
        target.create_line(x, y - 4, x, y + 8, fill=self.GOLD, width=1)

    def _draw_overlay_background(self, target: tk.Canvas, width: float, height: float):
        """Réutilise exactement le fond général TomeLinea déjà géré par l'application."""
        root = self.winfo_toplevel()
        photo = None
        background_factory = getattr(root, "_background_photo", None)
        if callable(background_factory):
            try:
                photo = background_factory(int(width), int(height), "workspace")
            except Exception:
                photo = None
        self._overlay_bg_photo = photo
        if photo is not None:
            target.create_image(0, 0, image=photo, anchor="nw")
        else:
            target.create_rectangle(0, 0, width, height, fill=theme.WINDOW_DEEP, outline="")


    def _draw_overlay_branding(self, target: tk.Canvas, width: float, height: float):
        """Identité TomeLinea fidèle à l'Accueil : grand logo et titre couleur exact."""
        self._overlay_brand_refs = []
        root = Path(__file__).resolve().parents[2]
        logo_path = root / "assets" / "branding" / "tomelinea" / "logo_pack_visibilite" / "TomeLinea_512x512.png"
        title_path = root / "assets" / "branding" / "tomelinea" / "logo_pack_visibilite" / "TomeLinea_titre_relief.png"

        if Image is not None and ImageTk is not None:
            try:
                with Image.open(logo_path) as src:
                    image = src.convert("RGBA")
                    image.thumbnail((104, 104), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                self._overlay_brand_refs.append(photo)
                target.create_image(72, 68, image=photo, anchor="center")
            except Exception:
                pass
            try:
                with Image.open(title_path) as src:
                    image = src.convert("RGBA")
                    target_w = 320
                    ratio = target_w / max(1, image.width)
                    image = image.resize((target_w, max(1, int(image.height * ratio))), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                self._overlay_brand_refs.append(photo)
                target.create_image(width / 2.0, 38, image=photo, anchor="center")
            except Exception:
                target.create_text(width / 2.0, 36, text="TomeLinea", fill=theme.INK, font=(theme.FONT_TITLE, 22, "bold"), anchor="center")

        target.create_text(
            width / 2.0, 66,
            text="LA LIGNE ÉDITORIALE JUSQU’AU LIVRE",
            fill=theme.MUTED_DARK, font=(theme.FONT_UI, 8, "bold"), anchor="center"
        )

    def _overlay_real_preview(self, target: tk.Canvas, item: dict, x: float, y: float, w: float, h: float, scale: float) -> str:
        path, stage = self._resolve_preview_path(item)
        if path is None or Image is None or ImageTk is None:
            return "attribut"
        inset = max(8, min(36, int(16 * min(scale, 2.2))))
        target_w = max(20, int(w - inset * 2))
        target_h = max(20, int(h - inset * 2.4))
        try:
            key = str(path)
            source = self._overlay_source_cache.get(key)
            if source is None:
                with Image.open(path) as opened:
                    source = opened.convert("RGB").copy()
                self._overlay_source_cache[key] = source
            image = source.copy()
            resample = Image.Resampling.BILINEAR if self._overlay_fast else Image.Resampling.LANCZOS
            image.thumbnail((target_w, target_h), resample)
            photo = ImageTk.PhotoImage(image)
        except Exception:
            return "attribut"
        self._overlay_image_refs.append(photo)
        target.create_image(x + w / 2.0, y + h / 2.0, image=photo, anchor="center")
        badge = "PROD" if stage == "production" else "GAB."
        target.create_text(x + inset, y + h - inset * .55, text=badge, anchor="sw", fill=theme.ACCENT_DARK, font=(theme.FONT_UI, 8, "bold"))
        return stage

    def _draw_overlay_attribute(self, target: tk.Canvas, item: dict, x: float, y: float, w: float, h: float, scale: float):
        if self._overlay_real_preview(target, item, x, y, w, h, scale) != "attribut":
            return
        inset = max(10, min(44, int(19 * min(scale, 2.4))))
        x1, y1, x2, y2 = x + inset, y + inset * 1.35, x + w - inset, y + h - inset * 1.45
        if x2 <= x1 or y2 <= y1:
            return
        definition = page_visual_definition(self._page_type_key(item)) or {}
        visual = str(item.get("visual") or definition.get("visual") or "custom")
        line = "#8B918F"
        pale = "#DDE5E1"
        accent = self.GOLD if self._is_locked_page(item) else theme.ACCENT_DARK
        ww, hh = x2 - x1, y2 - y1
        cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0

        if visual in {"cover", "back_cover", "inside_cover"}:
            fill = "#263833" if visual != "inside_cover" else "#E7EBE7"
            target.create_rectangle(x1, y1, x2, y2, fill=fill, outline=accent, width=2)
            if visual == "inside_cover":
                target.create_line(x1 + ww*.18, cy, x2 - ww*.18, cy, fill="#A7AEA9", width=1)
                target.create_oval(cx-4, cy-4, cx+4, cy+4, fill=accent, outline="")
            else:
                self._draw_overlay_book_icon(target, cx, cy - max(8, 18 * min(scale, 2.0)), self.GOLD)
                target.create_line(x1 + 14, y2 - max(18, 28 * min(scale, 2.0)), x2 - 14, y2 - max(18, 28 * min(scale, 2.0)), fill=self.GOLD, width=1)
            return

        if visual in {"image", "portfolio", "frontispice"}:
            target.create_rectangle(x1, y1, x2, y2, fill=pale, outline="#BFC9C5", width=1)
            horizon = y1 + hh * 0.68
            target.create_polygon(x1, horizon, x1 + ww*.28, y1 + hh*.42, x1 + ww*.48, horizon, fill="#A6B8AF", outline="")
            target.create_polygon(x1 + ww*.30, horizon, x1 + ww*.65, y1 + hh*.30, x2, horizon, fill="#8FA79B", outline="")
            target.create_oval(x2 - max(18, 30 * min(scale, 2.0)), y1 + 12, x2 - 8, y1 + max(24, 36 * min(scale, 2.0)), fill="#D7BE7C", outline="")
            return

        if visual == "toc":
            target.create_line(x1 + 8, y1 + hh*.12, x2 - 8, y1 + hh*.12, fill=accent, width=2)
            for r in range(7):
                yy = y1 + hh * (0.23 + r * 0.095)
                target.create_line(x1 + 8, yy, x2 - 28, yy, fill=line, width=1)
                target.create_oval(x2 - 16, yy - 2, x2 - 12, yy + 2, fill=accent, outline="")
            return

        if visual in {"title", "title_light", "chapter", "part_head", "conclusion", "foreword"}:
            token = "PARTIE" if visual == "part_head" else ("CHAPITRE" if visual == "chapter" else "TITRE")
            if visual == "conclusion":
                token = "FIN"
            target.create_text(cx, y1 + hh*.27, text=token, fill="#59615F", font=(theme.FONT_TITLE, max(11, int(13 * min(scale, 2.2))), "bold"))
            target.create_line(x1 + ww*.20, y1 + hh*.47, x2 - ww*.20, y1 + hh*.47, fill=accent, width=2)
            if visual in {"foreword", "chapter"}:
                for r in range(4):
                    yy = y1 + hh*(.60 + r*.075)
                    target.create_line(x1 + ww*.20, yy, x2 - ww*(.18 + .05*(r%2)), yy, fill=line, width=1)
            return

        if visual == "sheet":
            target.create_rectangle(x1, y1, x2, y2, fill="#E5ECE8", outline="#C5CECA")
            target.create_rectangle(x1+ww*.08, y1+hh*.10, x1+ww*.45, y1+hh*.42, fill="#B7C9C0", outline="")
            for r in range(5):
                yy=y1+hh*(.53+r*.075)
                target.create_line(x1+ww*.08, yy, x2-ww*.08, yy, fill=line, width=1)
            target.create_line(cx, y1+hh*.10, cx, y1+hh*.42, fill=accent, width=1)
            return

        if visual in {"transition", "dedication", "quote"}:
            target.create_line(x1 + ww*.23, cy, x2 - ww*.23, cy, fill=accent, width=2)
            target.create_oval(cx-4, cy-4, cx+4, cy+4, fill=self.GOLD, outline="")
            if visual == "quote":
                target.create_text(cx, y1+hh*.33, text="“ ”", fill="#6F7774", font=(theme.FONT_TITLE, max(12, int(17*min(scale,2.0))), "bold"))
            return

        if visual == "blank":
            if self._is_automatic_page(item):
                target.create_text(cx, cy, text="AUTO", fill=theme.ACCENT_DARK, font=(theme.FONT_UI, max(10, int(10*min(scale,2.0))), "bold"))
            return

        if visual in {"map", "appendix"}:
            target.create_rectangle(x1, y1, x2, y2, fill="#E6E8E3", outline="#C8CEC9", width=1)
            for frac in (.28, .52, .74):
                xx = x1 + ww * frac
                target.create_line(xx, y1 + 6, xx - 8, y2 - 6, fill="#A5AAA6", width=1)
            target.create_line(x1 + 8, y2 - 12, x1 + ww*.42, y1 + hh*.44, x2 - 8, y1 + 14, fill=accent, width=2, smooth=True)
            return

        if visual in {"table", "index", "glossary"}:
            rows, cols = 7, 3 if visual == "table" else 2
            for r in range(rows+1):
                yy=y1+hh*r/rows
                target.create_line(x1, yy, x2, yy, fill=line, width=1)
            for c in range(1, cols):
                xx=x1+ww*c/cols
                target.create_line(xx, y1, xx, y2, fill=line, width=1)
            return

        if visual == "chart":
            target.create_line(x1+ww*.12, y2-hh*.12, x2-ww*.08, y2-hh*.12, fill=line)
            target.create_line(x1+ww*.12, y2-hh*.12, x1+ww*.12, y1+hh*.12, fill=line)
            pts=[]
            for fx,fy in ((.15,.70),(.34,.52),(.50,.60),(.68,.30),(.86,.42)):
                pts.extend((x1+ww*fx,y1+hh*fy))
            target.create_line(*pts, fill=accent, width=2, smooth=True)
            return

        if visual == "timeline":
            target.create_line(x1+ww*.12, cy, x2-ww*.12, cy, fill=line, width=2)
            for frac in (.18,.38,.60,.82):
                xx=x1+ww*frac
                target.create_oval(xx-4,cy-4,xx+4,cy+4,fill=accent,outline="")
            return

        if visual == "spread":
            target.create_rectangle(x1, y1, cx-3, y2, fill="#EEF0ED", outline="#C9CECA")
            target.create_rectangle(cx+3, y1, x2, y2, fill="#EEF0ED", outline="#C9CECA")
            target.create_line(cx, y1, cx, y2, fill=accent, width=2)
            return

        # Texte et derniers recours.
        if visual == "box":
            target.create_rectangle(x1+ww*.10,y1+hh*.18,x2-ww*.10,y2-hh*.18,outline=accent,width=1)
            x1 += ww*.14; x2 -= ww*.14; y1 += hh*.22; y2 -= hh*.22
        yy = y1 + 12
        step = max(7, 12 * min(scale, 2.0))
        first = True
        while yy < y2 - 6:
            left = x1 + (18 if first else 5)
            right = x2 - (max(12, 20 * min(scale, 2.0)) if int((yy - y1) / step) % 4 == 3 else 5)
            target.create_line(left, yy, right, yy, fill=line, width=1)
            first = False
            yy += step

    def _render_page_overlay(self):
        self._overlay_render_job = None
        if not self._overlay_active or self._overlay_page_index is None:
            return
        if not (0 <= self._overlay_page_index < len(self.items)):
            self.close_page_overlay()
            return
        target = self.page_overlay
        width = max(260, target.winfo_width())
        height = max(220, target.winfo_height())
        self._clamp_overlay_pan()
        page_w, page_h, scale = self._overlay_dimensions()
        cx = width / 2.0 + self._overlay_pan_x
        cy = (height - 12) / 2.0 + self._overlay_pan_y
        x = cx - page_w / 2.0
        y = cy - page_h / 2.0
        self._overlay_page_box = (x, y, x + page_w, y + page_h)
        self._overlay_image_refs = []
        target.delete("all")

        self._draw_overlay_background(target, width, height)
        index = self._overlay_page_index
        item = self.items[index]
        group_id = self._item_group_id(item)
        group = next((grp for grp in self.groups if str(grp.get("id", "")) == group_id), {})
        page_title = self._page_display_name(item, index) or self._page_type_label(item, index)
        page_type = self._page_type_label(item, index)
        part_name = self._group_name(group)
        part_title = self._group_part_title(group)
        _preview_path, stage_key = self._resolve_preview_path(item)
        stage_text = {"attribut": "Structure", "gabarit": "Gabarit", "production": "Production", "type": "Structure"}.get(stage_key, "Structure")

        self._draw_overlay_branding(target, width, height)

        shadow = max(4, min(18, int(scale * 3)))
        target.create_rectangle(x + shadow, y + shadow, x + page_w + shadow, y + page_h + shadow, fill="#11161B", outline="")
        target.create_rectangle(x, y, x + page_w, y + page_h, fill="#F0F1EE", outline=self.GOLD, width=2)
        rail_pad = max(8, min(30, int(9 * min(scale, 2.2))))
        rail_h = max(3, min(10, int(5 * min(scale, 2.0))))
        rail_color = self.GOLD if self._is_locked_page(item) else theme.ACCENT_DARK
        target.create_rectangle(x + rail_pad, y + rail_pad, x + page_w - rail_pad, y + rail_pad + rail_h, fill=rail_color, outline="")
        self._draw_overlay_attribute(target, item, x, y, page_w, page_h, scale)

        part_value = part_name
        if part_title and part_title != "Titre à définir":
            part_value = f"{part_name} — {part_title}"

        panel_h = 92.0
        left_w = min(226.0, max(180.0, width * 0.19))
        right_w = min(236.0, max(188.0, width * 0.20))
        gap = 26.0
        left_x2 = max(34.0 + left_w, min(x - gap, width * 0.30))
        left_x1 = left_x2 - left_w
        right_x1 = min(width - 34.0 - right_w, max(x + page_w + gap, width * 0.70 - right_w))
        right_x2 = right_x1 + right_w
        panel_cy = height * 0.50
        panel_y1 = panel_cy - panel_h / 2.0
        panel_y2 = panel_cy + panel_h / 2.0

        target.create_rectangle(left_x1, panel_y1, left_x2, panel_y2, fill="#22303A", stipple="gray50", outline="")
        target.create_rectangle(right_x1, panel_y1, right_x2, panel_y2, fill="#22303A", stipple="gray50", outline="")

        target.create_text(left_x1 + 12, panel_y1 + 15, text="TITRE", anchor="w", fill=self.GOLD, font=(theme.FONT_UI, 7, "bold"))
        target.create_text(left_x1 + 12, panel_y1 + 31, text=page_title, anchor="w", fill=theme.INK, font=(theme.FONT_TITLE, 11, "bold"), width=max(130, left_w - 24))
        target.create_text(left_x1 + 12, panel_y1 + 57, text="TYPE", anchor="w", fill=self.GOLD, font=(theme.FONT_UI, 7, "bold"))
        target.create_text(left_x1 + 12, panel_y1 + 73, text=page_type, anchor="w", fill=theme.ACCENT_BRIGHT, font=(theme.FONT_UI, 9, "bold"), width=max(120, left_w - 24))

        target.create_text(right_x1 + 12, panel_y1 + 15, text="PARTIE", anchor="w", fill=self.GOLD, font=(theme.FONT_UI, 7, "bold"))
        target.create_text(right_x1 + 12, panel_y1 + 31, text=part_value, anchor="w", fill=theme.INK, font=(theme.FONT_TITLE, 11, "bold"), width=max(130, right_w - 24))
        target.create_text(right_x1 + 12, panel_y1 + 57, text="AVANCEMENT", anchor="w", fill=self.GOLD, font=(theme.FONT_UI, 7, "bold"))
        target.create_text(right_x1 + 12, panel_y1 + 73, text=f"{stage_text}  •  Page {index + 1}/{len(self.items)}", anchor="w", fill=theme.ACCENT_BRIGHT, font=(theme.FONT_UI, 9, "bold"), width=max(130, right_w - 24))

        if int(self.viewer_zoom_var.get()) > 112:
            target.configure(cursor="fleur")
        else:
            target.configure(cursor="arrow")

    def _logical_slots(self) -> int:
        count = 0
        for group in self.groups:
            group_id = str(group.get("id", ""))
            group_items = [item for item in self.items if self._item_group_id(item) == group_id]
            count += max(1, len(group_items))
        return max(1, count)

    def fit_book(self):
        """Ajuste réellement le zoom pour montrer le livre dans B."""
        if not self.items or not self.canvas.winfo_exists():
            return

        viewport_w = max(300, self.canvas.winfo_width() - 20)
        viewport_h = max(180, self.canvas.winfo_height() - 12)
        active_group_id = self._active_group_id()
        group_count = max(1, len(self.groups))

        logical_w = 0.0
        for group in self.groups:
            group_id = str(group.get("id", ""))
            indexes = self._group_items(group_id)
            if indexes:
                widths = [self.BASE_PAGE_W * self._page_size_factor(i, active_group_id) for i in indexes]
                logical_w += sum(widths) + self.BASE_GAP * max(0, len(indexes) - 1)
            else:
                logical_w += self.EMPTY_SLOT_W
        logical_w += self.BASE_GROUP_GAP * max(0, group_count - 1)

        logical_h = self.BASE_PAGE_H * self.PAGE_SIZE_SELECTED + self.GROUP_H + self.GROUP_TO_PAGE + self.PAGE_LABEL_H + self.PAGE_NAME_H
        zoom_x = int(viewport_w / max(1, logical_w + self.MARGIN * 2) * 100)
        zoom_y = int((viewport_h - self.GROUP_H - self.GROUP_TO_PAGE - self.MARGIN * 2 - self.PAGE_LABEL_H - self.PAGE_NAME_H) / (self.BASE_PAGE_H * self.PAGE_SIZE_SELECTED) * 100)
        self._book_zoom_cap = self._book_height_cap()
        value = max(self.MIN_ZOOM, min(self._book_zoom_cap, zoom_x, zoom_y))
        self.set_zoom(value, center_selected=False)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

    def fit_selected(self):
        """Affiche la page sélectionnée entière, au-dessus de B, sans toucher au livre."""
        self.open_page_overlay(reset_zoom=True)

    def _structure_focus_new_group(self):
        """Amène doucement la nouvelle partie dans la zone centrale de B."""
        group_id = str(self._selected_group_id or "")
        box = self._group_hitboxes.get(group_id)
        if not group_id or box is None:
            return
        self.canvas.update_idletasks()
        view_left = float(self.canvas.canvasx(0))
        view_w = max(1.0, float(self.canvas.winfo_width()))
        group_center = (float(box[0]) + float(box[2])) / 2.0
        screen_x = group_center - view_left

        # Zone confortable : entre 30 % et 70 % de la largeur visible.
        if view_w * 0.30 <= screen_x <= view_w * 0.70:
            return

        region = self.canvas.cget("scrollregion")
        if not region:
            return
        try:
            rx1, _ry1, rx2, _ry2 = map(float, str(region).split())
        except Exception:
            return
        total_w = max(1.0, rx2 - rx1)
        if total_w <= view_w + 2:
            return

        # Viser légèrement à droite du centre conserve davantage de contexte à gauche.
        desired_screen_x = view_w * 0.55
        target_left = group_center - desired_screen_x - rx1
        denominator = max(1.0, total_w - view_w)
        self.canvas.xview_moveto(max(0.0, min(1.0, target_left / denominator)))

    def center_selected_group(self):
        """Centre horizontalement la partie sélectionnée sans modifier le zoom."""
        group_id = str(self._selected_group_id or "")
        if not group_id or group_id not in self._group_hitboxes:
            return
        self.canvas.update_idletasks()
        box = self._group_hitboxes.get(group_id)
        if box is None:
            return
        region = self.canvas.cget("scrollregion")
        if not region:
            return
        try:
            rx1, _ry1, rx2, _ry2 = map(float, str(region).split())
        except Exception:
            return
        total_w = max(1.0, rx2 - rx1)
        view_w = max(1.0, self.canvas.winfo_width())
        if total_w <= view_w + 2:
            self.canvas.xview_moveto(0)
            return
        target_center = (float(box[0]) + float(box[2])) / 2.0
        target_left = target_center - view_w / 2.0 - rx1
        self.canvas.xview_moveto(
            max(0.0, min(1.0, target_left / max(1.0, total_w - view_w)))
        )

    def _structure_recenter_selection(self):
        kind = str(getattr(self, "_structure_selection_kind", "") or "")
        if kind == "page" and self._selected_index is not None:
            self.center_selected()
        elif kind == "group" and self._selected_group_id:
            self.center_selected_group()

    def center_selected(self):
        index = self._selected_index
        if index is None or index not in self._page_hitboxes:
            return
        self.canvas.update_idletasks()
        x1, y1, x2, y2 = self._page_hitboxes[index]
        region = self.canvas.cget("scrollregion")
        if not region:
            return
        try:
            rx1, ry1, rx2, ry2 = map(float, str(region).split())
        except Exception:
            return
        total_w = max(1.0, rx2 - rx1)
        total_h = max(1.0, ry2 - ry1)
        view_w = max(1.0, self.canvas.winfo_width())
        view_h = max(1.0, self.canvas.winfo_height())
        target_left = ((x1 + x2) / 2.0) - view_w / 2.0
        target_top = ((y1 + y2) / 2.0) - view_h / 2.0
        if total_w > view_w + 2:
            self.canvas.xview_moveto(max(0.0, min(1.0, target_left / max(1.0, total_w - view_w))))
        else:
            self.canvas.xview_moveto(0)
        if total_h > view_h + 2:
            self.canvas.yview_moveto(max(0.0, min(1.0, target_top / max(1.0, total_h - view_h))))
        else:
            self.canvas.yview_moveto(0)

    # ------------------------------------------------------------------
    # Rendu
    # ------------------------------------------------------------------

    def _schedule_render(self, _event=None):
        if self._render_pending is not None:
            try:
                self.after_cancel(self._render_pending)
            except Exception:
                pass
        self._render_pending = self.after(35, self.render)

    def _group_items(self, group_id: str) -> list[int]:
        return [index for index, item in enumerate(self.items) if self._item_group_id(item) == group_id]

    def _draw_group_icon(self, x: float, y: float, kind: str, accent: str, *, tags=()):
        if kind == "flag":
            self.canvas.create_line(x - 7, y - 9, x - 7, y + 8, fill=self.GOLD, width=2, tags=tags)
            self.canvas.create_polygon(x - 6, y - 8, x + 7, y - 4, x - 6, y + 1, fill=self.ORANGE, outline=self.GOLD, width=1, tags=tags)
            return
        # Livre ouvert, dessiné comme le petit livre du monogramme : deux pages et une ligne centrale.
        self.canvas.create_polygon(x - 9, y - 6, x - 1, y - 3, x - 1, y + 7, x - 9, y + 4, fill="", outline=accent, width=2, tags=tags)
        self.canvas.create_polygon(x + 1, y - 3, x + 9, y - 6, x + 9, y + 4, x + 1, y + 7, fill="", outline=accent, width=2, tags=tags)
        self.canvas.create_line(x, y - 3, x, y + 7, fill=self.GOLD, width=1, tags=tags)
        if kind == "book_end":
            self.canvas.create_line(x - 8, y + 7, x + 8, y + 7, fill=self.ORANGE, width=1, tags=tags)

    def _draw_group_header(self, group: dict, x1: float, x2: float, y1: float, y2: float):
        group_id = str(group.get("id", ""))
        selected = group_id == self._selected_group_id
        hovered = group_id == self._hover_group_id and not self._dragging
        protected = group_id in {self.START_GROUP_ID, self.END_GROUP_ID} or bool(group.get("protected", False))
        accent = str(group.get("accent") or theme.ACCENT_BRIGHT)
        fill = theme.PANEL_ALT if not (selected or hovered) else theme.ACCENT_SOFT
        outline = self.GOLD if selected else (theme.ACCENT_BRIGHT if hovered else theme.BORDER_SOFT)
        width = 2 if selected or hovered else 1
        tag = (f"group:{group_id}", "group")

        self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=width, tags=tag)
        self.canvas.create_line(x1 + 1, y2 - 2, x2 - 1, y2 - 2, fill=accent, width=2, tags=tag)
        icon_x = x1 + 18
        icon_y = (y1 + y2) / 2.0
        kind = str(group.get("symbol") or "book")
        if group_id == self.START_GROUP_ID:
            kind = "flag"
        elif group_id == self.END_GROUP_ID:
            kind = "book_end"
        else:
            kind = "book"
        self._draw_group_icon(icon_x, icon_y, kind, accent, tags=tag)

        name = self._group_name(group)
        part_title = self._group_part_title(group)
        count = len(self._group_items(group_id))
        # Le nom structurel reste secondaire ; le titre donné par l'utilisateur
        # devient l'information principale et doit rester lisible en un coup d'œil.
        self.canvas.create_text(
            x1 + 34,
            icon_y - 9,
            anchor="w",
            text=name,
            fill=theme.MUTED,
            font=(theme.FONT_UI, 7, "bold"),
            tags=tag,
        )
        self.canvas.create_text(
            x1 + 34,
            icon_y + 8,
            anchor="w",
            text=part_title,
            fill=theme.ACCENT_BRIGHT if part_title != "Titre à définir" else theme.MUTED_DARK,
            font=(theme.FONT_UI, 9, "bold" if part_title != "Titre à définir" else "italic"),
            tags=tag,
        )
        self.canvas.create_text(
            x2 - 8,
            icon_y - 8,
            anchor="e",
            text=str(count),
            fill=theme.MUTED_DARK,
            font=(theme.FONT_UI, 6),
            tags=tag,
        )

    def _draw_waiting_slot(self, x1: float, y1: float, x2: float, y2: float, group: dict):
        accent = str(group.get("accent") or theme.ACCENT_BRIGHT)
        self.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill=theme.WINDOW_DEEP,
            outline=theme.BORDER,
            width=1,
            dash=(6, 5),
            tags=("waiting",),
        )
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        self._draw_group_icon(cx, cy - 18, "book", accent, tags=("waiting",))
        self.canvas.create_text(
            cx,
            cy + 5,
            text="Pages à ajouter",
            fill=theme.MUTED,
            font=(theme.FONT_UI, 8, "bold"),
            tags=("waiting",),
        )
        self.canvas.create_text(
            cx,
            cy + 23,
            text="Le livre attend son contenu",
            fill=theme.MUTED_DARK,
            font=(theme.FONT_UI, 7),
            tags=("waiting",),
        )

    def _resolve_preview_path(self, item: dict) -> tuple[Path | None, str]:
        """Cherche d'abord la production, puis le gabarit, sinon l'attribut visuel."""
        stages = (
            ("production", ("production_preview", "production_thumbnail", "rendered_preview", "content_preview", "page_render_path")),
            ("gabarit", ("gabarit_preview", "template_preview", "layout_preview", "model_preview", "gabarit_image")),
            ("type", ("type_preview_image", "preview_image")),
        )
        roots: list[Path] = []
        project_root = getattr(self.project, "root", None) if self.project is not None else None
        if project_root:
            roots.append(Path(project_root))
        roots.append(Path(__file__).resolve().parents[2])
        for stage, keys in stages:
            for key in keys:
                value = str(item.get(key) or "").strip()
                if not value:
                    continue
                candidate = Path(value)
                candidates = [candidate] if candidate.is_absolute() else [root / candidate for root in roots]
                for path in candidates:
                    try:
                        if path.is_file():
                            return path, stage
                    except OSError:
                        continue
        return None, "attribut"

    def _draw_real_preview(self, item: dict, x: float, y: float, w: float, h: float, scale: float) -> str:
        path, stage = self._resolve_preview_path(item)
        if path is None or Image is None or ImageTk is None:
            return "attribut"
        inset = max(5, min(18, int(14 * scale)))
        target_w = max(8, int(w - inset * 2))
        target_h = max(8, int(h - inset * 2.6))
        try:
            with Image.open(path) as source:
                image = source.convert("RGB")
                image.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
        except Exception:
            return "attribut"
        self._image_refs.append(photo)
        self.canvas.create_image(x + w / 2.0, y + h / 2.0, image=photo, anchor="center")
        badge = "PROD" if stage == "production" else "GAB."
        self.canvas.create_text(
            x + max(5, 8 * scale), y + h - max(5, 8 * scale),
            text=badge, anchor="sw", fill=theme.ACCENT_DARK,
            font=(theme.FONT_UI, max(5, int(6 * scale)), "bold"),
        )
        return stage

    def _draw_type_preview(self, item: dict, x: float, y: float, w: float, h: float, label: str, scale: float):
        """Attribut symbolique ; remplacé automatiquement par gabarit/production si disponibles."""
        if self._draw_real_preview(item, x, y, w, h, scale) != "attribut":
            return

        inset = max(5, min(18, int(18 * scale)))
        x1, y1, x2, y2 = x + inset, y + inset * 1.4, x + w - inset, y + h - inset * 1.5
        if x2 <= x1 or y2 <= y1:
            return
        definition = page_visual_definition(self._page_type_key(item)) or {}
        visual = str(item.get("visual") or definition.get("visual") or "custom")
        line = "#8B918F"
        pale = "#DDE5E1"
        accent = self.GOLD if self._is_locked_page(item) else theme.ACCENT_DARK
        ww, hh = x2 - x1, y2 - y1
        cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0

        if visual in {"cover", "back_cover", "inside_cover"}:
            fill = "#263833" if visual != "inside_cover" else "#E7EBE7"
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=accent, width=max(1, int(2 * scale)))
            if visual == "inside_cover":
                self.canvas.create_line(x1 + ww*.18, cy, x2 - ww*.18, cy, fill="#A7AEA9", width=1)
                self.canvas.create_oval(cx-3, cy-3, cx+3, cy+3, fill=accent, outline="")
            else:
                self._draw_group_icon(cx, cy - max(4, 12 * scale), "book", self.GOLD)
                self.canvas.create_line(x1 + 8, y2 - max(12, 22 * scale), x2 - 8, y2 - max(12, 22 * scale), fill=self.GOLD, width=1)
            return

        if visual in {"image", "portfolio", "frontispice"}:
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=pale, outline="#BFC9C5", width=1)
            horizon = y1 + hh * 0.68
            self.canvas.create_polygon(x1, horizon, x1 + ww*.28, y1 + hh*.42, x1 + ww*.48, horizon, fill="#A6B8AF", outline="")
            self.canvas.create_polygon(x1 + ww*.30, horizon, x1 + ww*.65, y1 + hh*.30, x2, horizon, fill="#8FA79B", outline="")
            self.canvas.create_oval(x2 - max(10, 24 * scale), y1 + max(5, 10 * scale), x2 - max(4, 10 * scale), y1 + max(11, 24 * scale), fill="#D7BE7C", outline="")
            return

        if visual == "toc":
            self.canvas.create_line(x1 + 4, y1 + hh*.12, x2 - 4, y1 + hh*.12, fill=accent, width=2)
            for r in range(5):
                yy = y1 + hh * (0.27 + r * 0.12)
                self.canvas.create_line(x1 + 5, yy, x2 - 16, yy, fill=line, width=1)
                self.canvas.create_oval(x2 - 10, yy - 1, x2 - 8, yy + 1, fill=accent, outline="")
            return

        if visual in {"title", "title_light", "chapter", "part_head", "conclusion", "foreword"}:
            token = "PARTIE" if visual == "part_head" else ("CH." if visual == "chapter" else "TITRE")
            if visual == "conclusion":
                token = "FIN"
            self.canvas.create_text(cx, y1 + hh*.28, text=token, fill="#59615F", font=(theme.FONT_TITLE, max(7, int(10 * scale)), "bold"))
            self.canvas.create_line(x1 + ww*.20, y1 + hh*.48, x2 - ww*.20, y1 + hh*.48, fill=accent, width=2)
            if visual in {"foreword", "chapter"}:
                for r in range(3):
                    yy = y1 + hh*(.62 + r*.09)
                    self.canvas.create_line(x1 + ww*.20, yy, x2 - ww*(.18 + .05*(r%2)), yy, fill=line, width=1)
            return

        if visual == "sheet":
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#E5ECE8", outline="#C5CECA")
            self.canvas.create_rectangle(x1+ww*.08, y1+hh*.10, x1+ww*.45, y1+hh*.42, fill="#B7C9C0", outline="")
            for r in range(4):
                yy=y1+hh*(.54+r*.09)
                self.canvas.create_line(x1+ww*.08, yy, x2-ww*.08, yy, fill=line, width=1)
            self.canvas.create_line(cx, y1+hh*.10, cx, y1+hh*.42, fill=accent, width=1)
            return

        if visual in {"transition", "dedication", "quote"}:
            self.canvas.create_line(x1 + ww*.23, cy, x2 - ww*.23, cy, fill=accent, width=2)
            self.canvas.create_oval(cx-3, cy-3, cx+3, cy+3, fill=self.GOLD, outline="")
            if visual == "quote":
                self.canvas.create_text(cx, y1+hh*.33, text="“ ”", fill="#6F7774", font=(theme.FONT_TITLE, max(8, int(13*scale)), "bold"))
            return

        if visual == "blank":
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#F7F7F3", outline="#D9DCD7")
            if self._is_automatic_page(item) and not self._is_recto_verso_correction(item):
                self.canvas.create_text(cx, cy, text="AUTO", fill=theme.ACCENT_DARK, font=(theme.FONT_UI, max(5, int(7*scale)), "bold"))
            return

        if visual in {"map", "appendix"}:
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#E6E8E3", outline="#C8CEC9", width=1)
            for frac in (.28, .52, .74):
                xx = x1 + ww * frac
                self.canvas.create_line(xx, y1 + 4, xx - 5, y2 - 4, fill="#A5AAA6", width=1)
            self.canvas.create_line(x1 + 5, y2 - 8, x1 + ww*.42, y1 + hh*.44, x2 - 5, y1 + 10, fill=accent, width=2, smooth=True)
            return

        if visual in {"table", "index", "glossary"}:
            rows, cols = 5, 3 if visual == "table" else 2
            for r in range(rows+1):
                yy=y1+hh*r/rows
                self.canvas.create_line(x1, yy, x2, yy, fill=line, width=1)
            for c in range(1, cols):
                xx=x1+ww*c/cols
                self.canvas.create_line(xx, y1, xx, y2, fill=line, width=1)
            return

        if visual == "chart":
            self.canvas.create_line(x1+ww*.12, y2-hh*.12, x2-ww*.08, y2-hh*.12, fill=line)
            self.canvas.create_line(x1+ww*.12, y2-hh*.12, x1+ww*.12, y1+hh*.12, fill=line)
            pts=[]
            for fx,fy in ((.15,.70),(.34,.52),(.50,.60),(.68,.30),(.86,.42)):
                pts.extend((x1+ww*fx,y1+hh*fy))
            self.canvas.create_line(*pts, fill=accent, width=2, smooth=True)
            return

        if visual == "timeline":
            self.canvas.create_line(x1+ww*.12, cy, x2-ww*.12, cy, fill=line, width=2)
            for frac in (.18,.38,.60,.82):
                xx=x1+ww*frac
                self.canvas.create_oval(xx-3,cy-3,xx+3,cy+3,fill=accent,outline="")
            return

        if visual == "spread":
            self.canvas.create_rectangle(x1, y1, cx-2, y2, fill="#EEF0ED", outline="#C9CECA")
            self.canvas.create_rectangle(cx+2, y1, x2, y2, fill="#EEF0ED", outline="#C9CECA")
            self.canvas.create_line(cx, y1, cx, y2, fill=accent, width=2)
            return

        if visual in {"legal", "notes", "references", "credits", "bio", "text", "box", "custom"}:
            if visual == "box":
                self.canvas.create_rectangle(x1+ww*.10,y1+hh*.18,x2-ww*.10,y2-hh*.18,outline=accent,width=1)
                x1 += ww*.14; x2 -= ww*.14; y1 += hh*.22; y2 -= hh*.22
            yy = y1 + max(4, 8 * scale)
            step = max(4, 10 * scale)
            first = True
            while yy < y2 - 3:
                left = x1 + (10 if first else 3)
                right = x2 - (max(7, 16 * scale) if int((yy - y1) / step) % 4 == 3 else 3)
                self.canvas.create_line(left, yy, right, yy, fill=line, width=1)
                first = False
                yy += step
            return

        # Dernier recours : silhouette de texte.
        yy = y1 + max(4, 8 * scale)
        while yy < y2 - 3:
            self.canvas.create_line(x1 + 3, yy, x2 - 3, yy, fill=line, width=1)
            yy += max(4, 10 * scale)

    def _draw_structural_auto_preview(self, item: dict, x: float, y: float, w: float, h: float, scale: float) -> None:
        """Page automatique : présence structurelle discrète au repos, détail seulement si sélectionnée."""
        deployed = False
        for index, candidate in enumerate(self.items):
            if candidate is item:
                deployed = self._structural_auto_is_deployed(index)
                break

        pad = max(2.0, 3.0 * scale)
        x1, y1, x2, y2 = x + pad, y + pad, x + w - pad, y + h - pad
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill="#4B5854" if not deployed else "#5D6965",
            outline="#6D7C77" if not deployed else self.GOLD,
            width=1 if not deployed else 2,
        )
        if not deployed:
            return

        target_types = [str(v) for v in item.get("automatic_target_types", []) if str(v)]
        if target_types:
            definition = self._structure_type_definition(target_types[0])
            label = str(definition.get("short_label") or definition.get("label") or target_types[0]).strip()
        else:
            label = self._page_type_label(item)
        if len(label) > 18:
            label = label[:17] + "…"
        self.canvas.create_text(
            (x1+x2)/2, (y1+y2)/2, text=label,
            fill="#26363B", justify="center", width=max(20, x2-x1-6),
            font=(theme.FONT_UI, max(6, int(8*scale)), "bold"),
        )

    def _source_rule_tokens(self, item: dict) -> list[tuple[str, bool]]:
        """Repères portés uniquement par la page d'origine : AV, AP, R ou V."""
        if self._is_automatic_page(item) or self._is_locked_page(item):
            return []
        source_type = self._type_of(item)
        if not source_type:
            return []
        tokens: list[tuple[str, bool]] = []
        for position, code in (("before", "AV"), ("after", "AP")):
            if self.structure_get_page_auto_type_rule(source_type, position):
                tokens.append((code, self._page_auto_override_value(item, position) == "__none__"))
        side = self.structure_get_recto_verso_type_rule(source_type)
        if side in {"recto", "verso"}:
            tokens.append(("R" if side == "recto" else "V", self._recto_verso_override_value(item) == "__none__"))
        if self._double_page_pair_role(item) == "left":
            tokens.append(("2P", False))
        elif self.structure_get_double_page_type_rule(source_type) and self._double_page_override_value(item) == "__none__":
            tokens.append(("2P", True))
        return tokens

    def _draw_source_rule_tokens(self, item: dict, x: float, y: float, w: float, h: float, scale: float) -> None:
        tokens = self._source_rule_tokens(item)
        if not tokens:
            return
        font_size = max(6, min(10, int(7 + scale * 2)))
        gap = max(4.0, 6.0 * scale)
        widths = [max(15.0, (len(code) * 7 + 6) * max(0.75, scale)) for code, _excluded in tokens]
        total = sum(widths) + gap * max(0, len(widths)-1)
        cx = x + w/2.0 - total/2.0
        cy = y + h - max(10.0, 13.0 * scale)
        for (code, excluded), tw in zip(tokens, widths):
            tx = cx + tw/2.0
            color = "#7B8587" if excluded else self.GOLD
            self.canvas.create_text(tx, cy, text=code, fill=color, font=(theme.FONT_UI, font_size, "bold"))
            if excluded:
                self.canvas.create_line(cx+2, cy, cx+tw-2, cy, fill="#7B8587", width=1)
            cx += tw + gap

    def _draw_recto_verso_reference_marker(self, item: dict, x: float, y: float, w: float, h: float, scale: float) -> None:
        if self._is_automatic_page(item) or self._is_locked_page(item):
            return
        rule = self.structure_get_recto_verso_type_rule(self._type_of(item))
        if rule not in {"recto", "verso"}:
            return
        excluded = self._recto_verso_override_value(item) == "__none__"
        conflict = bool(item.get("recto_verso_conflict", False))
        band_w = max(13.0, min(w * 0.18, 22.0 * max(0.8, scale)))
        if rule == "recto":
            bx1, bx2, token = x + w - band_w, x + w, "R"
        else:
            bx1, bx2, token = x, x + band_w, "V"
        if conflict:
            fill, fg, outline = "#A84A42", "#FFFFFF", "#D77A70"
        elif excluded:
            fill, fg, outline = "#4B555A", "#C8CCCA", "#7D878B"
        else:
            fill, fg, outline = self.GOLD, "#18242A", self.GOLD
        self.canvas.create_rectangle(bx1, y, bx2, y + h, fill=fill, outline=outline, width=1)
        self.canvas.create_text((bx1+bx2)/2, y+h*0.50, text=token, fill=fg, font=(theme.FONT_UI, max(10, min(18, int(12 + self.zoom/100))), "bold"))
        if excluded:
            self.canvas.create_line(bx1+2, y+h*0.36, bx2-2, y+h*0.64, fill="#D6D8D6", width=max(1, int(scale)))
        if conflict:
            self.canvas.create_text((bx1+bx2)/2, y+h*0.69, text="!", fill=fg, font=(theme.FONT_UI, max(7, int(8*scale)), "bold"))

    def _draw_page_auto_rule_markers(
        self, item: dict, x: float, y: float, page_w: float, page_h: float, scale: float,
    ) -> None:
        """Exception locale : fantôme simple, discret et toujours accroché à sa page."""
        if self._is_automatic_page(item) or self._is_locked_page(item):
            return
        source_type = self._type_of(item)
        if not source_type:
            return
        before_auto_ghost = False
        for position in ("before", "after"):
            if not self.structure_get_page_auto_type_rule(source_type, position):
                continue
            if self._page_auto_override_value(item, position) != "__none__":
                continue
            # Le fantôme est une vraie miniature au même ratio que la page,
            # placée presque en haut sans toucher l'angle.
            ghost_h = max(34.0, float(page_h) * 0.46)
            ghost_w = ghost_h * (self.BASE_PAGE_W / self.BASE_PAGE_H)
            gy = y + max(5.0, 8.0 * scale)
            # Le fantôme appartient sans ambiguïté à sa page de référence :
            # trois quarts sont posés sur la page, un quart seulement dépasse.
            outside = ghost_w * 0.25
            gx = x - outside if position == "before" else x + float(page_w) - ghost_w + outside
            self.canvas.create_rectangle(
                gx, gy, gx+ghost_w, gy+ghost_h,
                fill="#74817E", outline="#97A39F", width=1, dash=(3, 3),
                stipple="gray50", tags=("structure_auto_ghost",),
            )
            if position == "before":
                before_auto_ghost = True

        # Exception Recto/Verso : même langage que Page auto, mais dans une
        # tonalité ardoise bleutée. La correction R/V, lorsqu'elle est utile,
        # se place toujours avant la page de référence.
        side = self.structure_get_recto_verso_type_rule(source_type)
        if side in {"recto", "verso"} and self._recto_verso_override_value(item) == "__none__":
            ghost_h = max(34.0, float(page_h) * 0.46)
            ghost_w = ghost_h * (self.BASE_PAGE_W / self.BASE_PAGE_H)
            gy = y + max(5.0, 8.0 * scale)
            outside = ghost_w * 0.25
            gx = x - outside
            # Si AV et R/V sont tous deux suspendus sur la même occurrence,
            # les deux fantômes restent lisibles sans former un gros bloc.
            if before_auto_ghost:
                gx += max(3.0, 4.0 * scale)
                gy += max(5.0, 7.0 * scale)
            self.canvas.create_rectangle(
                gx, gy, gx+ghost_w, gy+ghost_h,
                fill="#596A78", outline="#7C91A0", width=1, dash=(3, 3),
                stipple="gray50", tags=("structure_auto_ghost",),
            )

        self.canvas.after_idle(lambda: self.canvas.tag_raise("structure_auto_ghost"))

    def _structure_page_type_font(self, text: str, page_w: float, scale: float):
        """Réduit seulement la taille du texte pour garder le type entier dans la page."""
        label = str(text or "Page").strip() or "Page"
        available = max(18.0, float(page_w) - 10.0)
        start = max(7, min(13, int(9 * max(0.8, scale))))
        for size in range(start, 4, -1):
            try:
                font = tkfont.Font(family=theme.FONT_UI, size=size, weight="bold")
                if font.measure(label) <= available:
                    return (theme.FONT_UI, size, "bold")
            except Exception:
                break
        return (theme.FONT_UI, 5, "bold")

    def _structure_work_number_span(self, index: int) -> tuple[int, int]:
        """Numérotation de travail : une double page occupe deux positions."""
        number = 1
        for pos, item in enumerate(self.items):
            width = 2 if self._effective_double_page_rule(item) else 1
            if pos == index:
                return number, number + width - 1
            number += width
        return number, number

    def _structure_work_page_count(self) -> int:
        return sum(2 if self._effective_double_page_rule(item) else 1 for item in self.items)

    def _draw_page(self, index: int, x: float, y: float, page_w: float, page_h: float, scale: float, *, show_label: bool = True):
        item = self.items[index]
        selected = self._is_page_index_selected(index)
        hovered = index == self._hover_index and not self._dragging
        automatic = self._is_automatic_page(item)
        type_key = self._page_type_key(item)
        page_type = self._page_type_label(item, index)

        if automatic:
            fill = "#4B5854" if not selected else "#5D6965"
            outline = self.GOLD if selected else (theme.ACCENT_BRIGHT if hovered else "#6D7C77")
            outline_width = 2 if selected or hovered else 1
            shadow = 0
        else:
            cover = type_key in {"couverture", "premiere_couverture"}
            back = type_key in {"quatrieme", "quatrieme_couverture", "4e_couverture"}
            if cover:
                fill, outline = "#263833", self.GOLD
            elif back:
                fill, outline = "#303A3A", self.GOLD
            else:
                # Carte de structure TomeLinea : ardoise fumée, calme et peu lumineuse.
                # L'information reste très contrastée sans donner l'impression d'une page blanche.
                if selected:
                    fill = "#465154"
                elif hovered:
                    fill = "#404B4E"
                else:
                    fill = "#374145"
                outline = self.GOLD if selected else (theme.ACCENT_BRIGHT if hovered else "#667570")
            outline_width = 3 if selected else (2 if hovered else 1)
            shadow = 0 if self._double_page_pair_id(item) else max(1, min(7, int(2 * scale)))

        if shadow:
            self.canvas.create_rectangle(x+shadow, y+shadow, x+page_w+shadow, y+page_h+shadow, fill="#151B21", outline="")
        self.canvas.create_rectangle(x, y, x+page_w, y+page_h, fill=fill, outline=outline, width=outline_width)
        if not automatic and type_key not in {"couverture", "premiere_couverture", "quatrieme", "quatrieme_couverture", "4e_couverture"}:
            inset = max(2.0, min(4.0, 2.5 * scale))
            if page_w > inset * 4 and page_h > inset * 4:
                self.canvas.create_rectangle(
                    x+inset, y+inset, x+page_w-inset, y+page_h-inset,
                    fill="", outline="#56635F", width=1,
                )

        if not automatic and self._double_page_pair_role(item) == "right":
            fold_x = x
            pair_conflict = bool(item.get("double_page_pair_conflict", False))
            peer = self._double_page_pair_peer(item)
            if isinstance(peer, dict):
                pair_conflict = pair_conflict or bool(peer.get("double_page_pair_conflict", False))
            fold_color = "#B76A61" if pair_conflict else "#7C8985"
            self.canvas.create_line(fold_x, y+4, fold_x, y+page_h*0.34, fill=fold_color, width=2)
            self.canvas.create_line(fold_x, y+page_h*0.60, fold_x, y+page_h-4, fill=fold_color, width=2)
            if pair_conflict:
                self.canvas.create_text(
                    fold_x, y+page_h*0.48, text="!", fill="#D88980",
                    font=(theme.FONT_UI, max(8, int(9*scale)), "bold"),
                )

        if not automatic and self._effective_double_page_rule(item):
            fold_x = x + page_w / 2.0
            fold_color = "#B76A61" if bool(item.get("double_page_conflict", False)) else "#7C8985"
            self.canvas.create_line(fold_x, y+4, fold_x, y+page_h*0.34, fill=fold_color, width=1)
            self.canvas.create_line(fold_x, y+page_h*0.60, fold_x, y+page_h-4, fill=fold_color, width=1)
            if bool(item.get("double_page_conflict", False)):
                self.canvas.create_text(
                    fold_x, y+page_h*0.48, text="!", fill="#D88980",
                    font=(theme.FONT_UI, max(8, int(9*scale)), "bold"),
                )

        if automatic:
            self._draw_structural_auto_preview(item, x, y, page_w, page_h, scale)
        else:
            text_color = "#F3E8C8" if type_key in {"couverture", "premiere_couverture", "quatrieme", "quatrieme_couverture", "4e_couverture"} else "#ECE9E1"
            label = str(page_type or "Page").strip()
            type_font = self._structure_page_type_font(label, page_w, scale)
            self.canvas.create_text(
                x+page_w/2.0, y+page_h*0.46, text=label, fill=text_color,
                justify="center", font=type_font,
            )
            self._draw_source_rule_tokens(item, x, y, page_w, page_h, scale)
            self._draw_page_auto_rule_markers(item, x, y, page_w, page_h, scale)

        if show_label:
            label_y = y + page_h + max(8, 13*scale)
            number_from, number_to = self._structure_work_number_span(index)
            number_text = str(number_from) if number_from == number_to else f"{number_from}–{number_to}"
            self.canvas.create_text(
                x+page_w/2.0, label_y, text=number_text, fill=theme.INK,
                font=(theme.FONT_UI, max(6, int(8*scale)), "bold"),
            )

        self._page_hitboxes[index] = (x, y, x+page_w, y+page_h)
        item_id = str(item.get("id") or "").strip()
        if item_id:
            self._page_hitbox_ids[item_id] = index

    def _structure_view_anchor_snapshot(self):
        """Mémorise des repères stables avant chaque rendu Structure.

        Les repères utilisent le bord gauche, pas le centre : une page qui
        change de taille parce qu’elle devient sélectionnée ne pousse plus la
        ligne sous le curseur. Les pages non sélectionnées sont prioritaires.
        """
        if getattr(self, "_work_mode", "structure") != "structure" or not hasattr(self, "canvas"):
            return None
        try:
            view_w = max(1.0, float(self.canvas.winfo_width()))
            left = float(self.canvas.canvasx(0))
        except Exception:
            return None
        center_world = left + view_w / 2.0
        selected_ids = set(getattr(self, "_selected_page_ids", set()) or set())
        if self._selected_index is not None and 0 <= self._selected_index < len(self.items):
            selected_ids.add(str(self.items[self._selected_index].get("id") or ""))

        page_anchors = []
        for index, box in getattr(self, "_page_hitboxes", {}).items():
            x1, _y1, x2, _y2 = box
            page_id = str(getattr(self, "_page_hitbox_ids", {}).get(int(index)) or "").strip()
            if not page_id:
                continue
            center = (float(x1) + float(x2)) / 2.0
            page_anchors.append({
                "id": page_id,
                "screen_x": float(x1) - left,
                "distance": abs(center - center_world),
                "selected": page_id in selected_ids,
            })
        page_anchors.sort(key=lambda a: (1 if a["selected"] else 0, a["distance"]))

        group_anchors = []
        for group_id, box in getattr(self, "_group_hitboxes", {}).items():
            x1, _y1, x2, _y2 = box
            center = (float(x1) + float(x2)) / 2.0
            group_anchors.append({
                "id": str(group_id or ""),
                "screen_x": float(x1) - left,
                "distance": abs(center - center_world),
            })
        group_anchors.sort(key=lambda a: a["distance"])
        return {"left": left, "pages": page_anchors[:12], "groups": group_anchors[:12]}

    def _structure_restore_view_anchor(self, snapshot) -> None:
        """Restaure la ligne à la même position visuelle après une commande."""
        if not isinstance(snapshot, dict) or getattr(self, "_work_mode", "structure") != "structure":
            return
        try:
            view_w = max(1.0, float(self.canvas.winfo_width()))
            region = [float(v) for v in str(self.canvas.cget("scrollregion")).split()]
            total_w = max(view_w, region[2] - region[0]) if len(region) >= 4 else view_w
        except Exception:
            return

        target_left = float(snapshot.get("left") or 0.0)
        restored = False
        for anchor in snapshot.get("pages", []):
            page_id = str(anchor.get("id") or "")
            desired = anchor.get("screen_x")
            if not page_id or desired is None:
                continue
            new_index = next((i for i, item in enumerate(self.items) if str(item.get("id") or "") == page_id), None)
            if new_index is None or new_index not in self._page_hitboxes:
                continue
            x1, _y1, _x2, _y2 = self._page_hitboxes[new_index]
            target_left = float(x1) - float(desired)
            restored = True
            break

        if not restored:
            for anchor in snapshot.get("groups", []):
                group_id = str(anchor.get("id") or "")
                desired = anchor.get("screen_x")
                box = self._group_hitboxes.get(group_id)
                if not group_id or desired is None or box is None:
                    continue
                target_left = float(box[0]) - float(desired)
                restored = True
                break

        max_left = max(0.0, total_w - view_w)
        target_left = max(0.0, min(max_left, target_left))
        if total_w <= view_w + 1:
            self.canvas.xview_moveto(0)
        else:
            self.canvas.xview_moveto(target_left / total_w)
        self.after_idle(self._update_visible_part_marker)

    def _structure_refresh_page_auto_buttons(self) -> None:
        before_btn = getattr(self, "structure_auto_before_btn", None)
        after_btn = getattr(self, "structure_auto_after_btn", None)
        if before_btn is None or after_btn is None:
            return
        before_text, after_text = "AV", "AP"
        indices = self._selected_source_indices()
        source = self.items[indices[0]] if len(indices) == 1 else None
        if source is not None:
            source_type = self._type_of(source)
            for position, base in (("before", "AV"), ("after", "AP")):
                rule = self.structure_get_page_auto_type_rule(source_type, position) if source_type else ""
                override = self._page_auto_override_value(source, position)
                if rule:
                    label = f"{base} —" if override == "__none__" else f"{base} ✓"
                    if position == "before":
                        before_text = label
                    else:
                        after_text = label
        try:
            before_btn.configure(text=before_text)
            after_btn.configure(text=after_text)
        except Exception:
            pass
        self._structure_update_common_rule_actions()

    def render(self):
        self._render_pending = None
        if not hasattr(self, "canvas"):
            return

        # Ne jamais effacer le Canvas pendant une saisie directe : l'ancien
        # comportement refermait l'éditeur dès qu'un survol déclenchait render().
        if self._title_editor is not None or self._page_name_editor is not None:
            return

        structure_view_snapshot = self._structure_view_anchor_snapshot()
        self._structure_renumber_parts()

        viewport_w = max(300, self.canvas.winfo_width())
        viewport_h = max(180, self.canvas.winfo_height())
        self.canvas.delete("all")
        self._page_hitboxes = {}
        self._page_hitbox_ids = {}
        self._page_name_hitboxes = {}
        self._image_refs = []
        self._group_hitboxes = {}
        self._group_page_bounds = {}
        self._structure_page_line_bounds = None
        self._visual_indices = []

        if not self.items:
            self.status_var.set("Aucun projet chargé")
            self.canvas.create_text(viewport_w / 2, viewport_h / 2, text="Ouvrez un projet pour afficher son livre.", fill=theme.MUTED, font=(theme.FONT_UI, 10))
            self.canvas.configure(scrollregion=(0, 0, viewport_w, viewport_h))
            self._update_scrollbars(viewport_w, viewport_h)
            return

        if self._selected_index is None or not (0 <= self._selected_index < len(self.items)):
            self._selected_index = 0

        if str(getattr(self, "_work_mode", "structure") or "structure") == "gabarits":
            self._render_gabarit_workspace(viewport_w, viewport_h)
            return

        selected_from, selected_to = self._structure_work_number_span(self._selected_index)
        selected_page_number = str(selected_from) if selected_from == selected_to else f"{selected_from}–{selected_to}"
        work_page_count = self._structure_work_page_count()
        middle_count = sum(1 for group in self.groups if str(group.get("id", "")) not in {self.START_GROUP_ID, self.END_GROUP_ID})
        if self._page_focus:
            self.status_var.set(f"Page {selected_page_number} sur {work_page_count}  •  travail détaillé")
        else:
            self.status_var.set(f"{middle_count} partie{'s' if middle_count != 1 else ''}  •  {work_page_count} page{'s' if work_page_count != 1 else ''}")

        scale = self.zoom / 100.0
        gap = max(8, self.BASE_GAP * scale)
        group_gap = max(20, self.BASE_GROUP_GAP * scale)
        margin = max(20, self.MARGIN * min(scale, 1.0))

        if self._page_focus:
            page_w = max(16, self.BASE_PAGE_W * scale)
            page_h = max(22, self.BASE_PAGE_H * scale)
            total_w = max(viewport_w, page_w + margin * 2)
            total_h = max(viewport_h, page_h + self.PAGE_LABEL_H + self.PAGE_NAME_H + margin * 2)
            x = max(margin, (total_w - page_w) / 2.0)
            y = max(margin + self.PAGE_NAME_H, (total_h - page_h - self.PAGE_LABEL_H + self.PAGE_NAME_H) / 2.0)
            self._draw_page(self._selected_index, x, y, page_w, page_h, scale)
        else:
            active_group_id = self._active_group_id()
            specs: dict[int, tuple[float, float]] = {}
            for index in range(len(self.items)):
                item = self.items[index]
                if self._is_automatic_page(item):
                    deployed = self._structural_auto_is_deployed(index)
                    width_factor = self.PAGE_AUTO_DEPLOY_W if deployed else self.PAGE_AUTO_REST_W
                    height_factor = self.PAGE_AUTO_DEPLOY_H if deployed else self.PAGE_AUTO_REST_H
                    specs[index] = (
                        max(14, self.BASE_PAGE_W * scale * width_factor),
                        max(30, self.BASE_PAGE_H * scale * height_factor),
                    )
                else:
                    factor = self._page_size_factor(index, active_group_id)
                    single_w = max(16, self.BASE_PAGE_W * scale * factor)
                    page_h = max(22, self.BASE_PAGE_H * scale * factor)
                    if self._effective_double_page_rule(item):
                        specs[index] = (single_w * 2.0, page_h)
                    else:
                        specs[index] = (single_w, page_h)

            # Les pages auto et leur page source forment un seul bloc visuel.
            # Aucun espace à l'intérieur du bloc ; l'espace normal reste entre les blocs.
            group_layout: list[tuple[dict, list[list[int]], float]] = []
            for group in self.groups:
                group_id = str(group.get("id", ""))
                blocks = self._page_blocks_in_group(group_id)
                if blocks:
                    body_w = sum(sum(specs[i][0] for i in block) for block in blocks)
                    body_w += gap * max(0, len(blocks) - 1)
                else:
                    body_w = max(90, self.EMPTY_SLOT_W * scale)
                min_header = max(150, min(300, 174 + max(len(self._group_name(group)), len(self._group_part_title(group))) * 2))
                group_layout.append((group, blocks, max(body_w, min_header)))

            content_w = sum(width for _g, _i, width in group_layout) + group_gap * max(0, len(group_layout) - 1)
            # Aux deux extrémités, Début/Fin peuvent arriver exactement au centre
            # du champ visible. Cela évite une fin de parcours coincée sur un bord.
            if group_layout and content_w + margin * 2 > viewport_w:
                first_w = group_layout[0][2]
                last_w = group_layout[-1][2]
                left_pad = max(margin, viewport_w / 2.0 - first_w / 2.0)
                right_pad = max(margin, viewport_w / 2.0 - last_w / 2.0)
                x = left_pad
            else:
                # Quand toute la structure tient dans B, on la centre visuellement
                # au lieu de la plaquer à gauche. On conserve une petite respiration
                # de navigation sans provoquer un déplacement brutal.
                nav_pad = max(margin, min(150.0, viewport_w * 0.09)) if len(group_layout) >= 4 else margin
                centered_pad = max(0.0, (viewport_w - content_w) / 2.0)
                left_pad = right_pad = max(nav_pad, centered_pad)
                x = left_pad
            group_y1 = margin
            group_y2 = group_y1 + self.GROUP_H

            max_page_h = max((h for _w, h in specs.values()), default=self.BASE_PAGE_H * scale)
            row_needed = self.PAGE_NAME_H + max_page_h + self.PAGE_LABEL_H
            available_top = group_y2 + self.GROUP_TO_PAGE
            available_h = max(0, viewport_h - available_top - margin)
            page_row_top = available_top + max(0, (available_h - row_needed) / 2.0)
            page_bottom = page_row_top + row_needed

            # Seule cette bande est une zone de dépôt de page. Le petit débord
            # permet de viser confortablement entre deux cartes sans transformer
            # tout B en surface d'insertion.
            line_y1 = page_row_top + self.PAGE_NAME_H - 10.0
            line_y2 = page_row_top + self.PAGE_NAME_H + max_page_h + 10.0
            self._structure_page_line_bounds = (line_y1, line_y2)

            for group_pos, (group, blocks, group_width) in enumerate(group_layout):
                group_id = str(group.get("id", ""))
                start_x = x
                cursor_x = start_x
                if blocks:
                    for block_pos, block in enumerate(blocks):
                        # Le bloc [Auto Avant + source + Auto Après] est dessiné bord à bord.
                        for index in block:
                            self._visual_indices.append(index)
                            page_w, page_h = specs[index]
                            page_y = page_row_top + self.PAGE_NAME_H + (max_page_h - page_h)
                            self._draw_page(index, cursor_x, page_y, page_w, page_h, scale)
                            cursor_x += page_w
                        if block_pos < len(blocks) - 1:
                            cursor_x += gap
                else:
                    empty_w = max(90, self.EMPTY_SLOT_W * scale)
                    if group_id not in {self.START_GROUP_ID, self.END_GROUP_ID}:
                        slot_h = min(max_page_h, max(100, self.BASE_PAGE_H * scale * self.PAGE_SIZE_AUTO))
                        slot_y = page_row_top + self.PAGE_NAME_H + (max_page_h - slot_h)
                        self._draw_waiting_slot(cursor_x, slot_y, cursor_x + empty_w, slot_y + slot_h, group)
                    cursor_x += empty_w

                end_x = start_x + group_width
                self._group_hitboxes[group_id] = (start_x, group_y1, end_x, group_y2)
                self._group_page_bounds[group_id] = (start_x, end_x)
                self._draw_group_header(group, start_x, end_x, group_y1, group_y2)
                x = end_x
                if group_pos < len(group_layout) - 1:
                    separator_x = x + group_gap / 2.0
                    self.canvas.create_line(separator_x, group_y1 + 4, separator_x, page_row_top + max_page_h, fill=theme.BORDER_SOFT, width=1, dash=(3, 5))
                    x += group_gap

            total_w = max(viewport_w, content_w + left_pad + right_pad)
            required_h = page_bottom + margin
            total_h = viewport_h if required_h <= viewport_h + 1 else required_h

        self.canvas.configure(scrollregion=(0, 0, total_w, total_h))
        self._update_scrollbars(total_w, total_h)

        if self._dragging and not self._page_focus:
            if self._drag_kind == "group" and self._drag_group_target is not None:
                self._draw_group_drop_indicator(self._drag_group_target)
            elif self._drag_kind == "page" and self._drag_target_group_id is not None:
                self._draw_page_drop_indicator()

        if (
            getattr(self, "_work_mode", "structure") == "structure"
            and getattr(self, "_structure_pending_kind", None)
            and not self._page_focus
        ):
            self._draw_structure_placement_preview()

        self._structure_refresh_page_auto_buttons()
        self._structure_update_page_auto_visuals()
        self._structure_update_double_page_visuals()
        self._structure_update_recto_verso_visuals()
        self._structure_update_common_rule_actions()
        self._structure_update_auto_counter()
        self._structure_restore_view_anchor(structure_view_snapshot)
        self.after_idle(self._update_visible_part_marker)

    def _update_scrollbars(self, total_w: float, total_h: float):
        view_w = max(1, self.canvas.winfo_width())
        view_h = max(1, self.canvas.winfo_height())
        need_h = total_w > view_w + 2
        need_v = total_h > view_h + 2

        if need_h != self._h_scroll_needed:
            self._h_scroll_needed = need_h
            self.h_nav.set_enabled(need_h)
            if not need_h:
                self.canvas.xview_moveto(0)
        else:
            self.h_nav.set_enabled(need_h)
        if need_v != self._v_scroll_needed:
            self._v_scroll_needed = need_v
            if need_v:
                self.v_scroll.grid()
            else:
                self.v_scroll.grid_remove()
                self.canvas.yview_moveto(0)

    # ------------------------------------------------------------------
    # Repère de partie et édition directe du titre
    # ------------------------------------------------------------------

    def _structure_auto_counter_values(self) -> dict[str, int]:
        autos = [item for item in self.items if self._is_automatic_page(item)]

        # Total physique projeté : chaque élément compte pour une page,
        # une double page compte pour deux. Les pages auto mutualisées ne
        # sont comptées qu'une fois puisqu'elles n'existent qu'une fois dans self.items.
        total_pages = 0
        for item in self.items:
            if self._is_automatic_page(item):
                total_pages += 1
            elif self._effective_double_page_rule(item):
                total_pages += 2
            else:
                total_pages += 1

        values = {
            "auto": len(autos),
            "total": total_pages,
            "blank": sum(1 for item in autos if self._type_of(item) == "page_blanche"),
            "AV": 0, "AP": 0, "RV": 0, "DP": 0, "shared": 0,
        }
        for item in autos:
            roles = self._automatic_roles(item)
            codes = {str(role.get("code") or "") for role in roles}
            values["AV"] += int("AV" in codes)
            values["AP"] += int("AP" in codes)
            values["RV"] += int(bool(codes.intersection({"R", "V"})))
            values["DP"] += int("DP" in codes)
            values["shared"] += int(self._automatic_is_shared(item))
        return values

    def _structure_update_auto_counter(self, *, detailed: bool | None = None) -> None:
        label = getattr(self, "structure_auto_counter", None)
        if label is None:
            return
        values = self._structure_auto_counter_values()
        if detailed is None:
            detailed = bool(getattr(self, "_structure_auto_counter_hover", False))
        if detailed:
            text = (
                f"{values['auto']} auto / {values['total']} pages  •  "
                f"AV {values['AV']} • AP {values['AP']} • R/V {values['RV']} • "
                f"Double {values['DP']} • partagées {values['shared']}"
            )
            fg, bg = "#E7C37A", "#162A38"
        else:
            text = (
                f"Auto : {values['auto']} / {values['total']} pages"
                f"  •  blanches : {values['blank']}"
            )
            fg, bg = "#AEB8B5", theme.WINDOW_DEEP
        try:
            label.configure(text=text, fg=fg, bg=bg)
        except Exception:
            pass

    def _structure_auto_counter_enter(self, _event=None):
        self._structure_auto_counter_hover = True
        self._structure_update_auto_counter(detailed=True)

    def _structure_auto_counter_leave(self, _event=None):
        self._structure_auto_counter_hover = False
        self._structure_update_auto_counter(detailed=False)

    def _navigate_horizontal(self, velocity: float):
        """Défilement continu piloté par le point central du navigateur."""
        if not self._h_scroll_needed or abs(float(velocity)) < 0.001:
            return
        first, last = self.canvas.xview()
        visible = max(0.01, float(last) - float(first))
        # Déplacement modéré : précis près du centre, plus soutenu aux extrémités.
        magnitude = abs(float(velocity))
        step = (0.0025 + 0.0105 * (magnitude ** 1.6)) * (1.0 + visible * 0.35)
        target = float(first) + (step if velocity > 0 else -step)
        max_first = max(0.0, 1.0 - visible)
        self.canvas.xview_moveto(max(0.0, min(max_first, target)))
        self.after_idle(self._update_visible_part_marker)

    def _on_canvas_xview(self, first, last):
        if self._sticky_part_job is None:
            self._sticky_part_job = self.after_idle(self._update_visible_part_marker)

    def _on_canvas_yview(self, first, last):
        self.v_scroll.set(first, last)
        if self._sticky_part_job is None:
            self._sticky_part_job = self.after_idle(self._update_visible_part_marker)

    def _visible_group_id(self) -> str:
        if not self._group_page_bounds or self._page_focus:
            return self._active_group_id()
        center_x = self.canvas.canvasx(max(1, self.canvas.winfo_width()) / 2.0)
        return self._group_id_at_x(center_x)

    def _update_visible_part_marker(self):
        """Repère fixe dans la barre de B : uniquement pour Structure."""
        self._sticky_part_job = None
        if getattr(self, "_work_mode", "structure") != "structure":
            return
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists() or not self.groups:
            return
        if self._page_focus:
            if self._selected_index is not None:
                self.status_var.set(f"Page {self._selected_index + 1} sur {len(self.items)}  •  travail détaillé")
            return
        group_id = self._visible_group_id()
        group = next((g for g in self.groups if str(g.get("id", "")) == group_id), None)
        if group is None:
            return
        name = self._group_name(group)
        title = self._group_part_title(group)
        nav_text = name if title == "Titre à définir" else f"{name} — {title}"
        self.h_nav.set_part(nav_text)
        self.status_var.set(f"Partie visible  •  {nav_text}")

    def _group_id_from_current_tags(self) -> str | None:
        current = self.canvas.find_withtag("current")
        if not current:
            return None
        for tag in self.canvas.gettags(current[-1]):
            if tag.startswith("group:"):
                return tag.split(":", 1)[1]
            if tag.startswith("sticky_group:"):
                return tag.split(":", 1)[1]
        return None

    def _begin_group_title_edit(self, group_id: str):
        group = next((g for g in self.groups if str(g.get("id", "")) == group_id), None)
        box = self._group_hitboxes.get(group_id)
        if group is None or box is None:
            return
        self._close_page_name_editor(commit=True)
        self._close_title_editor(commit=True)

        view_left = self.canvas.canvasx(0)
        view_right = self.canvas.canvasx(max(1, self.canvas.winfo_width()))
        visible_left = max(box[0], view_left + 10)
        visible_right = min(box[2], view_right - 10)
        if visible_right - visible_left < 120:
            visible_left = max(box[0], view_left + 10)
            visible_right = min(box[2], visible_left + 220)

        entry = tk.Entry(
            self.canvas,
            bg=theme.PANEL_ALT, fg=theme.INK, insertbackground=self.GOLD,
            selectbackground=theme.ACCENT_DARK, selectforeground=theme.WHITE,
            relief="flat", bd=0, font=(theme.FONT_UI, 9, "bold"),
        )
        value = str(group.get("part_title") or group.get("titre_partie") or group.get("subtitle") or "").strip()
        entry.insert(0, value)

        # L'Entry est un vrai widget superposé au Canvas et non un item Canvas.
        # Un simple rafraîchissement graphique ne peut donc plus le détruire
        # pendant la saisie.
        world_x = visible_left + 35
        world_y = box[1] + self.GROUP_H - 17
        screen_x = world_x - self.canvas.canvasx(0)
        screen_y = world_y - self.canvas.canvasy(0)
        width = max(110, min(260, visible_right - world_x - 8))
        entry.place(x=screen_x, y=screen_y, anchor="w", width=width, height=22)
        self._title_editor = entry
        self._title_editor_window = None
        self._editing_group_id = group_id
        entry.bind("<Return>", lambda _e: (self._close_title_editor(commit=True), "break")[-1])
        entry.bind("<Escape>", lambda _e: (self._close_title_editor(commit=False), "break")[-1])
        entry.bind("<FocusOut>", lambda _e: self._close_title_editor(commit=True))
        entry.focus_force()
        entry.selection_range(0, "end")

    def _close_title_editor(self, *, commit: bool):
        entry = self._title_editor
        group_id = self._editing_group_id
        window = self._title_editor_window
        if entry is None:
            return
        value = entry.get().strip() if commit else None
        self._title_editor = None
        self._title_editor_window = None
        self._editing_group_id = None
        try:
            entry.place_forget()
            entry.destroy()
        except Exception:
            pass
        if commit and group_id is not None:
            group = next((g for g in self.groups if str(g.get("id", "")) == group_id), None)
            if group is not None:
                group["part_title"] = value or ""
                self._selected_group_id = group_id
                self._save_order()
                self.after_idle(self.render)

    def _page_name_at(self, event) -> int | None:
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        for index, (x1, y1, x2, y2) in self._page_name_hitboxes.items():
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                return index
        return None

    def _begin_page_name_edit(self, index: int):
        if not 0 <= index < len(self.items):
            return
        box = self._page_hitboxes.get(index)
        if box is None:
            return
        self._close_page_name_editor(commit=True)
        self._close_title_editor(commit=True)
        entry = tk.Entry(
            self.canvas,
            bg=theme.PANEL_ALT, fg=theme.INK, insertbackground=self.GOLD,
            selectbackground=theme.ACCENT_DARK, selectforeground=theme.WHITE,
            relief="flat", bd=0, font=(theme.FONT_UI, 9, "bold"),
            justify="center",
        )
        value = self._page_display_name(self.items[index], index)
        entry.insert(0, value)
        x1, y1, x2, _y2 = box
        world_x = (x1 + x2) / 2.0
        world_y = y1 - self.PAGE_NAME_H / 2.0
        screen_x = world_x - self.canvas.canvasx(0)
        screen_y = world_y - self.canvas.canvasy(0)
        width = max(90, min(260, (x2 - x1) + 50))
        entry.place(x=screen_x, y=screen_y, anchor="center", width=width, height=22)
        self._page_name_editor = entry
        self._page_name_editor_window = None
        self._editing_page_index = index
        entry.bind("<Return>", lambda _e: (self._close_page_name_editor(commit=True), "break")[-1])
        entry.bind("<Escape>", lambda _e: (self._close_page_name_editor(commit=False), "break")[-1])
        entry.bind("<FocusOut>", lambda _e: self._close_page_name_editor(commit=True))
        entry.focus_force()
        entry.selection_range(0, "end")

    def _close_page_name_editor(self, *, commit: bool):
        entry = self._page_name_editor
        index = self._editing_page_index
        window = self._page_name_editor_window
        if entry is None:
            return
        value = entry.get().strip() if commit else None
        self._page_name_editor = None
        self._page_name_editor_window = None
        self._editing_page_index = None
        try:
            entry.place_forget()
            entry.destroy()
        except Exception:
            pass
        if commit and index is not None and 0 <= index < len(self.items):
            if value:
                self.items[index]["page_name"] = value
            else:
                self.items[index].pop("page_name", None)
                self.items[index].pop("nom_page", None)
                self.items[index].pop("display_name", None)
            self._set_single_page_selection(index)
            self._save_order()
            self.after_idle(self.render)

    # ------------------------------------------------------------------
    # Sélection / glisser-déposer
    # ------------------------------------------------------------------

    def _index_at(self, event) -> int | None:
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        for index, (x1, y1, x2, y2) in self._page_hitboxes.items():
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                return index
        return None

    def _group_title_at(self, event) -> str | None:
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        for group_id, (x1, y1, x2, y2) in self._group_hitboxes.items():
            # Ligne basse du bandeau = titre éditable ; la moitié haute reste
            # disponible pour sélectionner/déplacer la partie.
            if x1 <= cx <= x2 and (y1 + (y2 - y1) * 0.46) <= cy <= y2:
                return group_id
        return None

    def _group_at(self, event) -> str | None:
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        for group_id, (x1, y1, x2, y2) in self._group_hitboxes.items():
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                return group_id
        return None

    def _group_id_at_x(self, canvas_x: float) -> str:
        """Retourne la partie correspondant à x, y compris dans les espaces entre parties."""
        if not self._group_page_bounds:
            return self.DEFAULT_GROUP_ID
        ordered = []
        for group in self.groups:
            group_id = str(group.get("id", ""))
            bounds = self._group_page_bounds.get(group_id)
            if bounds is not None:
                ordered.append((group_id, bounds[0], bounds[1]))
        if not ordered:
            return self.DEFAULT_GROUP_ID
        if canvas_x <= ordered[0][1]:
            return ordered[0][0]
        for pos, (group_id, x1, x2) in enumerate(ordered):
            if x1 <= canvas_x <= x2:
                return group_id
            if pos < len(ordered) - 1:
                next_id, next_x1, _next_x2 = ordered[pos + 1]
                boundary = (x2 + next_x1) / 2.0
                if canvas_x < boundary:
                    return group_id
                if canvas_x < next_x1:
                    return next_id
        return ordered[-1][0]

    def _drag_block_indices(self, index: int | None) -> list[int]:
        if index is None or not 0 <= index < len(self.items):
            return []
        item = self.items[index]
        if self._is_automatic_page(item):
            if self._automatic_is_shared(item):
                return [index]
            parent_id = self._automatic_parent_id(item)
            parent_index = next((i for i, candidate in enumerate(self.items) if str(candidate.get("id") or "") == parent_id), None)
            if parent_index is not None:
                index = parent_index
                item = self.items[index]
        item_id = str(item.get("id") or "")
        linked = {
            id(candidate) for candidate in self.items
            if self._is_automatic_page(candidate)
            and not self._automatic_is_shared(candidate)
            and item_id in self._automatic_source_ids(candidate)
        }
        return [i for i, candidate in enumerate(self.items) if i == index or id(candidate) in linked]

    def _drag_selected_source_ids(self) -> list[str]:
        selected = {
            str(value or "").strip()
            for value in getattr(self, "_drag_selected_page_ids", set())
            if str(value or "").strip()
        }
        if not selected:
            index = getattr(self, "_drag_start_index", None)
            source_index = self._source_index_for_index(index)
            if source_index is not None:
                source_id = str(self.items[source_index].get("id") or "").strip()
                if source_id:
                    selected.add(source_id)
        # Une double page soudée est un bloc de déplacement : tirer une moitié entraîne l'autre.
        for item in list(self.items):
            item_id = str(item.get("id") or "").strip()
            if item_id not in selected or self._is_automatic_page(item):
                continue
            pair_id = self._double_page_pair_id(item)
            if not pair_id:
                continue
            for _index, member in self._double_page_pair_members(pair_id):
                member_id = str(member.get("id") or "").strip()
                if member_id:
                    selected.add(member_id)
        return [
            str(item.get("id") or "").strip()
            for item in self.items
            if not self._is_automatic_page(item) and str(item.get("id") or "").strip() in selected
        ]


    def _drag_excluded_indices(self) -> set[int]:
        source_ids = set(self._drag_selected_source_ids())
        if not source_ids:
            return set(self._drag_block_indices(getattr(self, "_drag_start_index", None)))
        excluded: set[int] = set()
        for index, item in enumerate(self.items):
            if not self._is_automatic_page(item) and str(item.get("id") or "").strip() in source_ids:
                excluded.add(index)
            elif self._is_automatic_page(item) and source_ids.intersection(self._automatic_source_ids(item)):
                excluded.add(index)
        return excluded

    def _page_blocks_in_group(self, group_id: str, *, exclude_indices: set[int] | None = None) -> list[list[int]]:
        exclude_indices = exclude_indices or set()
        indexes = [i for i in self._group_items(group_id) if i not in exclude_indices]
        index_set = set(indexes)
        by_id = {str(self.items[i].get("id") or ""): i for i in indexes}
        consumed: set[int] = set()
        blocks: list[list[int]] = []
        for index in indexes:
            if index in consumed:
                continue
            item = self.items[index]
            if self._is_automatic_page(item):
                if self._automatic_is_shared(item):
                    # Deux références : la page reprend une position centrale.
                    blocks.append([index])
                    consumed.add(index)
                    continue
                parent_index = by_id.get(self._automatic_parent_id(item))
                if parent_index is not None and parent_index in index_set:
                    continue
                blocks.append([index])
                consumed.add(index)
                continue
            item_id = str(item.get("id") or "")
            block = [index]
            source_ids = {item_id} if item_id else set()
            if self._double_page_pair_role(item) == "left":
                peer_id = self._double_page_pair_peer_id(item)
                peer_index = by_id.get(peer_id)
                if peer_index is not None and peer_index in index_set:
                    block.append(peer_index)
                    source_ids.add(peer_id)
            if source_ids:
                linked = [
                    i for i in indexes
                    if self._is_automatic_page(self.items[i])
                    and not self._automatic_is_shared(self.items[i])
                    and bool(source_ids.intersection(self._automatic_source_ids(self.items[i])))
                ]
                block.extend(linked)
            block = sorted(set(block))
            consumed.update(block)
            blocks.append(block)
        for index in indexes:
            if index not in consumed:
                blocks.append([index])
        blocks.sort(key=lambda block: min(block))
        return blocks

    def _target_local_pos_from_x(self, canvas_x: float, group_id: str, *, dragged_index: int | None = None) -> int:
        """Position d'insertion parmi les pages sources, indépendante des autos visibles."""
        excluded = self._drag_excluded_indices() if getattr(self, "_drag_kind", None) == "page" else set()
        source_indexes = [
            index for index in self._group_items(group_id)
            if index not in excluded and not self._is_automatic_page(self.items[index])
        ]
        if not source_indexes:
            return 0
        for local_pos, index in enumerate(source_indexes):
            block = self._drag_block_indices(index)
            boxes = [self._page_hitboxes[i] for i in block if i in self._page_hitboxes and i not in excluded]
            if not boxes and index in self._page_hitboxes:
                boxes = [self._page_hitboxes[index]]
            if not boxes:
                continue
            x1 = min(box[0] for box in boxes)
            x2 = max(box[2] for box in boxes)
            if canvas_x < (x1 + x2) / 2.0:
                return local_pos
        return len(source_indexes)

    def _refresh_drag_target(self):
        if not self._dragging or self._drag_pointer_xy is None:
            return
        pointer_x, _pointer_y = self._drag_pointer_xy
        canvas_x = self.canvas.canvasx(pointer_x)
        if self._drag_kind == "group":
            self._drag_group_target = self._target_movable_group_index(canvas_x)
        elif self._drag_kind == "page" and self._drag_start_index is not None:
            group_id = self._group_id_at_x(canvas_x)
            self._drag_target_group_id = group_id
            self._drag_target_local_pos = self._target_local_pos_from_x(
                canvas_x,
                group_id,
                dragged_index=self._drag_start_index,
            )

    def _redraw_drop_indicator_only(self):
        self.canvas.delete("drop_indicator")
        if not self._dragging or self._page_focus:
            return
        if self._drag_kind == "group" and self._drag_group_target is not None:
            self._draw_group_drop_indicator(self._drag_group_target)
        elif self._drag_kind == "page" and self._drag_target_group_id is not None:
            self._draw_page_drop_indicator()

    def _set_drag_autoscroll(self, pointer_x: int):
        if not self._dragging or not self._h_scroll_needed:
            self._drag_autoscroll_direction = 0
            self._drag_autoscroll_speed = 0
            self._cancel_drag_autoscroll()
            return
        width = max(1, self.canvas.winfo_width())
        edge = min(self.AUTO_SCROLL_EDGE, max(36, width // 5))
        direction = 0
        speed = 0
        if pointer_x < edge:
            direction = -1
            proximity = max(0.0, min(1.0, (edge - pointer_x) / edge))
            speed = 1 + int((proximity ** 1.8) * (self.AUTO_SCROLL_MAX_SPEED - 1))
        elif pointer_x > width - edge:
            direction = 1
            proximity = max(0.0, min(1.0, (pointer_x - (width - edge)) / edge))
            speed = 1 + int((proximity ** 1.8) * (self.AUTO_SCROLL_MAX_SPEED - 1))
        self._drag_autoscroll_direction = direction
        self._drag_autoscroll_speed = speed
        if direction == 0:
            self._cancel_drag_autoscroll()
        elif self._drag_autoscroll_job is None:
            self._drag_autoscroll_job = self.after(self.AUTO_SCROLL_INTERVAL_MS, self._drag_autoscroll_tick)

    def _cancel_drag_autoscroll(self):
        job = self._drag_autoscroll_job
        self._drag_autoscroll_job = None
        if job is not None:
            try:
                self.after_cancel(job)
            except Exception:
                pass

    def _drag_autoscroll_tick(self):
        self._drag_autoscroll_job = None
        if not self._dragging or self._drag_autoscroll_direction == 0 or not self._h_scroll_needed:
            return
        first, last = self.canvas.xview()
        direction = self._drag_autoscroll_direction
        if (direction < 0 and first <= 0.0001) or (direction > 0 and last >= 0.9999):
            return
        self.canvas.xview_scroll(direction * max(1, self._drag_autoscroll_speed), "units")
        self._refresh_drag_target()
        self._redraw_drop_indicator_only()
        self._drag_autoscroll_job = self.after(self.AUTO_SCROLL_INTERVAL_MS, self._drag_autoscroll_tick)

    def _on_hover_motion(self, event):
        if getattr(self, "_work_mode", "structure") == "gabarits":
            x, y = float(event.x), float(event.y)
            hovered = ""
            for key in (
                "prev", "next", "scope_page", "scope_type", "toggle_status",
                "edit_margins", "edit_bleed", "zoom_minus", "zoom_plus", "zoom_fit",
            ):
                if self._gabarit_point_in(self._gabarit_hitboxes.get(key), x, y):
                    hovered = key
                    break
            if not hovered and self._gabarit_point_in(getattr(self, "_gabarit_page_box", None), x, y):
                self._gabarit_update_zoom_anchor(x, y)
            old_hover = str(getattr(self, "_gabarit_hover_control", "") or "")
            self._gabarit_hover_control = hovered
            if hovered:
                cursor = "hand2"
            elif self._gabarit_point_in(getattr(self, "_gabarit_page_box", None), x, y) and int(getattr(self, "_gabarit_zoom", 100)) > 100:
                cursor = "fleur"
            else:
                cursor = "arrow"
            try:
                self.canvas.configure(cursor=cursor)
            except Exception:
                pass
            if old_hover != hovered:
                self.render()
            return
        if getattr(self, "_work_mode", "structure") == "structure" and getattr(self, "_structure_pending_kind", None):
            target = self._structure_update_hover_target(event)
            try:
                self.canvas.configure(cursor="crosshair" if target is not None else "arrow")
            except Exception:
                pass
            return
        if self._title_editor is not None or self._page_name_editor is not None:
            return
        if self._dragging or (getattr(event, "state", 0) & 0x0100):
            return
        index = self._index_at(event)
        group_id = None if index is not None else self._group_at(event)
        cursor = "hand2" if index is not None or group_id is not None else "arrow"
        self.canvas.configure(cursor=cursor)
        if index == self._hover_index and group_id == self._hover_group_id:
            return
        self._hover_index = index
        self._hover_group_id = group_id
        self.render()

    def _on_hover_leave(self, _event=None):
        if getattr(self, "_work_mode", "structure") == "gabarits":
            if getattr(self, "_gabarit_hover_control", ""):
                self._gabarit_hover_control = ""
                self.render()
            try:
                self.canvas.configure(cursor="arrow")
            except Exception:
                pass
            return
        if getattr(self, "_structure_pending_kind", None):
            self._structure_hover_target = None
            try:
                self.canvas.configure(cursor="arrow")
            except Exception:
                pass
            self.render()
            return
        if self._hover_index is None and self._hover_group_id is None:
            return
        self._hover_index = None
        self._hover_group_id = None
        try:
            self.canvas.configure(cursor="arrow")
        except Exception:
            pass
        self.render()

    def _on_press(self, event):
        if getattr(self, "_work_mode", "structure") == "gabarits":
            return self._gabarit_press(event)
        if getattr(self, "_title_editor", None) is not None:
            self._close_title_editor(commit=True)

        if getattr(self, "_work_mode", "structure") == "structure" and getattr(self, "_structure_page_auto_mode", None):
            self.structure_cancel_page_auto_mode(silent=True)
        if getattr(self, "_work_mode", "structure") == "structure" and getattr(self, "_structure_action_mode", None):
            self._structure_reset_action()
        if getattr(self, "_work_mode", "structure") == "structure" and getattr(self, "_structure_pending_kind", None):
            return self._structure_apply_pending_event(event)

        if getattr(self, "_work_mode", "structure") != "structure":
            index = self._index_at(event)
            group_id = self._group_at(event)
            self._drag_kind = None
            self._dragging = False
            self._drag_start_xy = None
            self._drag_selected_page_ids.clear()
            if index is not None:
                self._set_single_page_selection(index)
            elif group_id is not None:
                self._selected_group_id = group_id
                self._selected_page_ids.clear()
            self.render()
            return "break"

        name_index = self._page_name_at(event)
        if name_index is not None:
            self._drag_selected_page_ids.clear()
            self._set_single_page_selection(name_index)
            self.after_idle(lambda idx=self._selected_index: self._begin_page_name_edit(idx) if idx is not None else None)
            return "break"

        title_group_id = self._group_title_at(event)
        if title_group_id is not None and not self._page_focus:
            self._drag_selected_page_ids.clear()
            self._structure_selection_kind = "group"
            self._selected_page_ids.clear()
            self._selected_group_id = title_group_id
            self.after_idle(lambda gid=title_group_id: self._begin_group_title_edit(gid))
            return "break"

        if self._page_focus:
            index = self._index_at(event)
            if index is not None:
                self._set_single_page_selection(index)
                self.render()
            return "break"

        group_id = self._group_at(event)
        index = self._index_at(event)

        if index is None and group_id is not None:
            self._selection_box_start = None
            self._selection_box_current = None
            self._selection_box_active = False
            self.canvas.delete("selection_box")
            self._drag_selected_page_ids.clear()
            self._structure_selection_kind = "group"
            self._selected_page_ids.clear()
            self._selected_index = None
            self._selected_group_id = group_id
            self._drag_start_xy = (event.x, event.y)
            self._dragging = False
            self._drag_target_index = None
            self._drag_target_group_id = None
            self._drag_target_local_pos = None
            self._drag_pointer_xy = (event.x, event.y)
            if group_id not in {self.START_GROUP_ID, self.END_GROUP_ID}:
                self._drag_kind = "group"
                self._drag_group_id = group_id
                ids = self._movable_group_ids()
                self._drag_group_target = ids.index(group_id) if group_id in ids else None
            else:
                self._drag_kind = None
                self._drag_group_id = None
                self._drag_group_target = None
            self.render()
            return "break"

        if index is None:
            cx = self.canvas.canvasx(event.x)
            cy = self.canvas.canvasy(event.y)
            self._selection_box_start = (cx, cy)
            self._selection_box_current = (cx, cy)
            self._selection_box_active = False
            self._drag_kind = None
            self._drag_selected_page_ids.clear()
            self._drag_start_xy = (event.x, event.y)
            self._dragging = False
            self.canvas.delete("selection_box")
            return "break"

        self._selection_box_start = None
        self._selection_box_current = None
        self._selection_box_active = False
        self.canvas.delete("selection_box")

        self._drag_start_xy = (event.x, event.y)
        self._dragging = False
        self._drag_target_index = None
        self._drag_target_group_id = None
        self._drag_target_local_pos = None
        self._drag_group_target = None
        self._drag_pointer_xy = (event.x, event.y)
        self._drag_autoscroll_direction = 0
        self._drag_autoscroll_speed = 0
        self._cancel_drag_autoscroll()

        if group_id is not None:
            self._drag_selected_page_ids.clear()
            self._structure_selection_kind = "group"
            self._selected_page_ids.clear()
            self._selected_group_id = group_id
            if group_id not in {self.START_GROUP_ID, self.END_GROUP_ID}:
                self._drag_kind = "group"
                self._drag_group_id = group_id
                self._drag_group_target = self._movable_group_ids().index(group_id) if group_id in self._movable_group_ids() else None
            else:
                self._drag_kind = None
                self._drag_group_id = None
            self.render()
            return "break"

        self._drag_kind = "page"
        source_index = self._source_index_for_index(index)
        self._drag_start_index = source_index
        if source_index is not None:
            source_id = str(self.items[source_index].get("id") or "").strip()
            current_ids = {
                str(value or "").strip() for value in getattr(self, "_selected_page_ids", set())
                if str(value or "").strip()
            }
            if source_id and source_id in current_ids and len(current_ids) > 1:
                # Cliquer-glisser une page déjà dans le lasso déplace tout le groupe.
                self._drag_selected_page_ids = set(current_ids)
                self._structure_selection_kind = "page"
                self._selected_index = source_index
                self._selected_group_id = self._item_group_id(self.items[source_index])
            else:
                self._set_single_page_selection(source_index)
                self._drag_selected_page_ids = set(self._selected_page_ids)
            self._drag_target_index = source_index
            self._drag_target_group_id = self._item_group_id(self.items[source_index])
            self._drag_target_local_pos = self._target_local_pos_from_x(
                self.canvas.canvasx(event.x), self._drag_target_group_id, dragged_index=source_index
            )
            self.render()
        return "break"

    def _movable_group_ids(self) -> list[str]:
        return [str(group.get("id", "")) for group in self.groups if str(group.get("id", "")) not in {self.START_GROUP_ID, self.END_GROUP_ID}]

    def _on_drag(self, event):
        if getattr(self, "_work_mode", "structure") == "gabarits":
            return self._gabarit_drag(event)
        if self._selection_box_start is not None and self._drag_kind is None:
            if self._drag_start_xy is None:
                return "break"
            dx = abs(event.x - self._drag_start_xy[0])
            dy = abs(event.y - self._drag_start_xy[1])
            if not self._selection_box_active and max(dx, dy) < 5:
                return "break"
            self._selection_box_active = True
            cx = self.canvas.canvasx(event.x)
            cy = self.canvas.canvasy(event.y)
            self._selection_box_current = (cx, cy)
            x1, y1 = self._selection_box_start
            x2, y2 = self._selection_box_current
            self.canvas.delete("selection_box")
            self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline=self.GOLD, width=2, dash=(5, 3),
                tags=("selection_box",),
            )
            return "break"

        if self._drag_kind is None or self._drag_start_xy is None:
            return "break"
        self._drag_pointer_xy = (event.x, event.y)
        dx = abs(event.x - self._drag_start_xy[0])
        dy = abs(event.y - self._drag_start_xy[1])
        if not self._dragging and max(dx, dy) < 6:
            return "break"

        if self._drag_kind == "page":
            selected_ids = set(self._drag_selected_source_ids())
            selected_sources = [
                item for item in self.items
                if not self._is_automatic_page(item) and str(item.get("id") or "").strip() in selected_ids
            ]
            if not selected_sources or any(self._is_locked_page(item) for item in selected_sources):
                self._dragging = False
                self._cancel_drag_autoscroll()
                return "break"

        self._dragging = True
        self._refresh_drag_target()
        self._set_drag_autoscroll(event.x)
        self.render()
        return "break"

    def _target_movable_group_index(self, canvas_x: float) -> int:
        ids = self._movable_group_ids()
        if not ids:
            return 0
        for pos, group_id in enumerate(ids):
            box = self._group_hitboxes.get(group_id)
            if box and canvas_x < (box[0] + box[2]) / 2.0:
                return pos
        return len(ids)

    def _target_index_from_x(self, canvas_x: float, group_id: str) -> int:
        indexes = self._group_items(group_id)
        if not indexes:
            # Insertion à la frontière du groupe : avant le premier groupe suivant.
            group_order = [str(group.get("id", "")) for group in self.groups]
            pos = group_order.index(group_id) if group_id in group_order else 0
            following = set(group_order[pos + 1 :])
            for index, item in enumerate(self.items):
                if self._item_group_id(item) in following:
                    return index
            return len(self.items)
        for index in indexes:
            box = self._page_hitboxes.get(index)
            if box and canvas_x < (box[0] + box[2]) / 2.0:
                return index
        return indexes[-1] + 1

    def _draw_group_drop_indicator(self, target: int):
        ids = self._movable_group_ids()
        if not ids:
            return
        if target >= len(ids):
            box = self._group_hitboxes.get(ids[-1])
            x = (box[2] + 12) if box else 0
        else:
            box = self._group_hitboxes.get(ids[target])
            x = (box[0] - 12) if box else 0
        y1 = min(box_[1] for box_ in self._group_hitboxes.values()) if self._group_hitboxes else 0
        y2 = max((box_[3] for box_ in self._page_hitboxes.values()), default=y1 + 100)
        self.canvas.create_line(x, y1 - 3, x, y2 + 6, fill=self.GOLD, width=4, tags=("drop_indicator",))

    def _draw_page_drop_indicator(self):
        group_id = self._drag_target_group_id
        local_pos = self._drag_target_local_pos
        if group_id is None or local_pos is None:
            return
        excluded = self._drag_excluded_indices()
        source_indexes = [
            index for index in self._group_items(group_id)
            if index not in excluded and not self._is_automatic_page(self.items[index])
        ]
        y1 = min((box[1] for box in self._page_hitboxes.values()), default=self.MARGIN + self.GROUP_H)
        y2 = max((box[3] for box in self._page_hitboxes.values()), default=y1 + 100)
        if local_pos < len(source_indexes) and source_indexes[local_pos] in self._page_hitboxes:
            x = self._page_hitboxes[source_indexes[local_pos]][0] - 7
        elif source_indexes and source_indexes[-1] in self._page_hitboxes:
            x = self._page_hitboxes[source_indexes[-1]][2] + 7
        else:
            bounds = self._group_page_bounds.get(group_id)
            x = bounds[0] + 6 if bounds else 0
        self.canvas.create_line(x, y1 - 8, x, y2 + 8, fill=self.GOLD, width=4, tags=("drop_indicator",))

    def _reorder_items_by_group_order(self):
        ordered: list[dict] = []
        for group in self.groups:
            group_id = str(group.get("id", ""))
            grouped = [item for item in self.items if self._item_group_id(item) == group_id]
            if group_id == self.START_GROUP_ID:
                grouped.sort(key=self._start_group_sort_key)
            elif group_id == self.END_GROUP_ID:
                grouped.sort(key=self._end_group_sort_key)
            ordered.extend(grouped)
        self.items = ordered

    def _move_page_to_group_position(self, item: dict, target_group: str, target_local_pos: int) -> None:
        """Déplace une page principale et toutes ses pages automatiques comme un seul bloc."""
        try:
            anchor_index = self.items.index(item)
        except ValueError:
            return
        block_indices = self._drag_block_indices(anchor_index)
        if not block_indices:
            return
        block = [self.items[i] for i in block_indices]
        block_ids = {id(candidate) for candidate in block}

        # Supprime le bloc de la séquence avant de calculer l'insertion cible.
        remaining = [candidate for candidate in self.items if id(candidate) not in block_ids]
        for candidate in block:
            candidate["plan_group"] = target_group

        target_items = [candidate for candidate in remaining if self._item_group_id(candidate) == target_group]
        target_local_pos = max(0, min(len(target_items), int(target_local_pos)))
        target_items[target_local_pos:target_local_pos] = block

        rebuilt: list[dict] = []
        for group in self.groups:
            group_id = str(group.get("id", ""))
            if group_id == target_group:
                grouped = list(target_items)
            else:
                grouped = [candidate for candidate in remaining if self._item_group_id(candidate) == group_id]
            if group_id == self.START_GROUP_ID:
                grouped.sort(key=self._start_group_sort_key)
            elif group_id == self.END_GROUP_ID:
                grouped.sort(key=self._end_group_sort_key)
            rebuilt.extend(grouped)
        self.items = rebuilt

    def _move_selected_pages_to_group_position(self, source_ids, target_group: str, target_local_pos: int) -> list[str]:
        """Déplace en une seule opération les pages sources sélectionnées, ordre conservé."""
        requested = {str(value or "").strip() for value in source_ids or [] if str(value or "").strip()}
        if not requested:
            return []

        # Les autos sont dérivées de la structure. On les garde toutefois comme
        # réserve d'identités : la passe globale pourra réutiliser leurs ID lorsque
        # la même relation existe après le déplacement.
        existing_autos = [item for item in self.items if self._is_automatic_page(item)]
        base_items = [item for item in self.items if not self._is_automatic_page(item)]
        selected = [item for item in base_items if str(item.get("id") or "").strip() in requested]
        if not selected or any(self._is_locked_page(item) for item in selected):
            return []
        selected_ids = [str(item.get("id") or "").strip() for item in selected]
        selected_identity = {id(item) for item in selected}
        remaining = [item for item in base_items if id(item) not in selected_identity]

        for item in selected:
            item["plan_group"] = target_group

        target_sources = [item for item in remaining if self._item_group_id(item) == target_group]
        target_local_pos = max(0, min(len(target_sources), int(target_local_pos)))
        target_sources[target_local_pos:target_local_pos] = selected

        rebuilt: list[dict] = []
        for group in self.groups:
            group_id = str(group.get("id", ""))
            if group_id == target_group:
                grouped = list(target_sources)
            else:
                grouped = [item for item in remaining if self._item_group_id(item) == group_id]
            if group_id == self.START_GROUP_ID:
                grouped.sort(key=self._start_group_sort_key)
            elif group_id == self.END_GROUP_ID:
                grouped.sort(key=self._end_group_sort_key)
            rebuilt.extend(grouped)
        # Les autos sont provisoirement conservées ; la synchronisation suivante
        # les repositionne et réutilise leurs ID selon leurs rôles.
        self.items = [*rebuilt, *existing_autos]
        return selected_ids

    def _on_release(self, _event):
        if getattr(self, "_work_mode", "structure") == "gabarits":
            return self._gabarit_release(_event)
        if self._selection_box_start is not None:
            start = self._selection_box_start
            current = self._selection_box_current or start
            active = bool(self._selection_box_active)
            self._selection_box_start = None
            self._selection_box_current = None
            self._selection_box_active = False
            self._drag_start_xy = None
            self.canvas.delete("selection_box")

            if active:
                x1, x2 = sorted((start[0], current[0]))
                y1, y2 = sorted((start[1], current[1]))
                hits = []
                for index, (px1, py1, px2, py2) in self._page_hitboxes.items():
                    if px2 < x1 or px1 > x2 or py2 < y1 or py1 > y2:
                        continue
                    hits.append(index)
                self._set_multi_page_selection(hits)
                count = len(self._selected_source_indices())
                self.status_var.set(
                    f"{count} pages sélectionnées" if count > 1
                    else ("1 page sélectionnée" if count == 1 else "Sélection vide")
                )
            else:
                self._selected_page_ids.clear()
                self._selected_index = None
                self._selected_group_id = None
                self._structure_selection_kind = "page"
            self.render()
            return "break"

        kind = self._drag_kind
        dragged = self._dragging
        start = self._drag_start_index
        target_group = self._drag_target_group_id
        target_local_pos = self._drag_target_local_pos
        drag_group_id = self._drag_group_id
        group_target = self._drag_group_target
        drag_selected_ids = list(self._drag_selected_source_ids())

        self._drag_kind = None
        self._drag_start_index = None
        self._drag_selected_page_ids.clear()
        self._drag_target_index = None
        self._drag_target_group_id = None
        self._drag_target_local_pos = None
        self._drag_group_id = None
        self._drag_group_target = None
        self._drag_start_xy = None
        self._drag_pointer_xy = None
        self._dragging = False
        self._drag_autoscroll_direction = 0
        self._drag_autoscroll_speed = 0
        self._cancel_drag_autoscroll()

        if not dragged:
            self.render()
            return "break"

        if kind == "group" and drag_group_id and group_target is not None:
            middle = [group for group in self.groups if str(group.get("id", "")) not in {self.START_GROUP_ID, self.END_GROUP_ID}]
            source_pos = next((i for i, group in enumerate(middle) if str(group.get("id", "")) == drag_group_id), None)
            if source_pos is not None:
                group = middle.pop(source_pos)
                if group_target > source_pos:
                    group_target -= 1
                group_target = max(0, min(len(middle), group_target))
                middle.insert(group_target, group)
                start_group = next(group for group in self.groups if str(group.get("id", "")) == self.START_GROUP_ID)
                end_group = next(group for group in self.groups if str(group.get("id", "")) == self.END_GROUP_ID)
                self.groups = [start_group, *middle, end_group]
                self._structure_renumber_parts()
                self._reorder_items_by_group_order()
                self._selected_group_id = drag_group_id
                self._save_order()
            self.render()
            return "break"

        if kind == "page" and start is not None and target_group is not None and target_local_pos is not None:
            moved_ids = self._move_selected_pages_to_group_position(drag_selected_ids, target_group, target_local_pos)
            if moved_ids:
                self._save_order()
                restored = [
                    index for index, item in enumerate(self.items)
                    if not self._is_automatic_page(item) and str(item.get("id") or "").strip() in set(moved_ids)
                ]
                self._set_multi_page_selection(restored)
                self.status_var.set(
                    "Page déplacée" if len(restored) == 1 else f"{len(restored)} pages déplacées ensemble"
                )
            self.render()
            return "break"

        self.render()
        return "break"

    def _on_double_click(self, event):
        if getattr(self, "_work_mode", "structure") == "gabarits":
            # Double-clic = retour immédiat au plus grand affichage contenu dans B.
            self.gabarit_reset_zoom()
            return "break"
        # Structure sert à construire le squelette du livre : une page n'y
        # possède plus de mode d'agrandissement. Le double-clic reste réservé
        # au nom des parties pour conserver le renommage rapide.
        index = self._index_at(event)
        if index is not None:
            return "break"
        group_id = self._group_id_from_current_tags() or self._group_at(event)
        if group_id is not None:
            self._selected_group_id = group_id
            self._selected_page_ids.clear()
            self._structure_selection_kind = "group"
            self.render()
            self.after_idle(lambda gid=group_id: self._begin_group_title_edit(gid))
        return "break"

    def _on_ctrl_mousewheel(self, event):
        if getattr(self, "_work_mode", "structure") == "gabarits":
            x, y = float(event.x), float(event.y)
            work_left, work_top, work_right, work_bottom = self._gabarit_work_rect()
            if work_left <= x <= work_right and work_top <= y <= work_bottom:
                self.gabarit_step_zoom(1 if event.delta > 0 else -1, anchor=(x, y))
            return "break"
        return "break"

    def _on_shift_mousewheel(self, event):
        if getattr(self, "_work_mode", "structure") == "gabarits":
            if int(getattr(self, "_gabarit_zoom", 100)) > 100:
                self._gabarit_pan_x += 42.0 if event.delta > 0 else -42.0
                page_w, page_h, _ = self._gabarit_dimensions_for_zoom()
                self._gabarit_clamp_pan(self.canvas.winfo_width(), self.canvas.winfo_height(), page_w, page_h)
                self.render()
            return "break"
        if self._h_scroll_needed:
            delta = -1 if event.delta > 0 else 1
            self.canvas.xview_scroll(delta * 4, "units")
            self.after_idle(self._update_visible_part_marker)
        return "break"

    def _on_mousewheel(self, event):
        if getattr(self, "_work_mode", "structure") == "gabarits":
            x, y = float(event.x), float(event.y)
            work_left, work_top, work_right, work_bottom = self._gabarit_work_rect()
            # Le zoom reste dans B et utilise exactement la position du pointeur
            # comme origine. Il fonctionne aussi près du bord inférieur.
            if work_left <= x <= work_right and work_top <= y <= work_bottom:
                self.gabarit_step_zoom(1 if event.delta > 0 else -1, anchor=(x, y))
            return "break"
        delta = -1 if event.delta > 0 else 1
        if self._v_scroll_needed:
            self.canvas.yview_scroll(delta * 4, "units")
        elif self._h_scroll_needed:
            self.canvas.xview_scroll(delta * 4, "units")
            self.after_idle(self._update_visible_part_marker)
        return "break"

