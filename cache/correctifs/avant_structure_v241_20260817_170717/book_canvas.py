from __future__ import annotations

import tkinter as tk
from copy import deepcopy
import shutil
from pathlib import Path
from typing import Callable
from uuid import uuid4

from src.gui_v3 import theme
from src.gui_v3.page_visual_catalog import canonical_page_type, page_visual_definition

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
        width = max(150.0, float(self.winfo_width()))
        center = width / 2.0
        half = max(56.0, min(102.0, width * 0.34))
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

    # Défilement de bord volontairement progressif : précis près de la cible,
    # encore assez vif pour traverser une longue partie.
    AUTO_SCROLL_EDGE = 88
    AUTO_SCROLL_INTERVAL_MS = 46
    AUTO_SCROLL_MAX_SPEED = 3

    # Quatre niveaux visuels indépendants de la partie active.
    PAGE_SIZE_AUTO = 0.58
    PAGE_SIZE_NORMAL = 0.82
    PAGE_SIZE_PART_HEAD = 0.98
    PAGE_SIZE_SELECTED = 1.16
    PAGE_LABEL_H = 28
    PAGE_NAME_H = 24

    def __init__(
        self,
        parent,
        *,
        on_open_item: Callable[[dict, int], None],
        on_change: Callable[[], None] | None = None,
        on_focus_change: Callable[[bool], None] | None = None,
    ):
        super().__init__(parent, bg=theme.PANEL)
        self.on_open_item = on_open_item
        self.on_change = on_change
        self.on_focus_change = on_focus_change
        self.project = None
        self.items: list[dict] = []
        self.groups: list[dict] = [dict(group) for group in self.DEFAULT_GROUPS]
        self._data: dict = {}

        self._selected_index: int | None = None
        self._selected_group_id: str | None = None
        # V24 — sélection multiple : on mémorise les pages principales par ID.
        # Les pages automatiques liées suivent visuellement et fonctionnellement leur source.
        self._selected_page_ids: set[str] = set()
        self._selection_box_start: tuple[float, float] | None = None
        self._selection_box_current: tuple[float, float] | None = None
        self._selection_box_active = False
        self._page_hitboxes: dict[int, tuple[float, float, float, float]] = {}
        self._group_hitboxes: dict[str, tuple[float, float, float, float]] = {}
        self._group_page_bounds: dict[str, tuple[float, float]] = {}
        self._visual_indices: list[int] = []

        self._drag_kind: str | None = None
        self._drag_start_index: int | None = None
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
        self._structure_pending_kind = None
        self._structure_pending_payload = None
        self._structure_hover_target = None
        self._structure_selection_kind = "page"
        # V10 — action → cible dans B → confirmation locale dans le bandeau.
        self._structure_action_mode = None
        self._structure_action_target_kind = None
        self._structure_action_target_id = None
        self._structure_action_target_ids: list[str] = []

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_toolbar()
        self._build_canvas()
        try:
            self.winfo_toplevel().bind("<Button-1>", self._structure_global_click, add="+")
        except Exception:
            pass

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
        """Outil Structure V11 : petite commande d'atelier, distincte des boutons/onglets."""
        base = "#162A38"
        hover = "#203B4B"
        pressed = "#10232E"
        edge = "#C39A4A"
        fg = "#F2F3F1"
        label = tk.Label(
            parent, text=text, bg=base, fg=fg,
            font=(theme.FONT_UI, 9, "bold"), padx=10, pady=3,
            highlightthickness=0,
            cursor="hand2",
        )
        def enter(_e=None): label.configure(bg=hover)
        def leave(_e=None): label.configure(bg=base)
        def press(_e=None): label.configure(bg=pressed)
        def release(_e=None):
            label.configure(bg=hover)
            command()
            return "break"
        label.bind("<Enter>", enter)
        label.bind("<Leave>", leave)
        label.bind("<ButtonPress-1>", press)
        label.bind("<ButtonRelease-1>", release)
        return label

    def _source_index_for_index(self, index: int | None) -> int | None:
        """Ramène une page automatique à sa page principale."""
        if index is None or not 0 <= int(index) < len(self.items):
            return None
        index = int(index)
        item = self.items[index]
        if not self._is_automatic_page(item):
            return index
        parent_id = self._automatic_parent_id(item)
        if not parent_id:
            return index
        return next(
            (i for i, candidate in enumerate(self.items) if str(candidate.get("id") or "") == parent_id),
            index,
        )

    def _set_single_page_selection(self, index: int | None) -> None:
        source_index = self._source_index_for_index(index)
        if source_index is None:
            self._selected_index = None
            self._selected_page_ids.clear()
            return
        self._selected_index = source_index
        source = self.items[source_index]
        source_id = str(source.get("id") or "").strip()
        self._selected_page_ids = {source_id} if source_id else set()
        self._selected_group_id = self._item_group_id(source)
        self._structure_selection_kind = "page"

    def _set_multi_page_selection(self, indices) -> None:
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

    def _structure_new_part_command(self):
        self._structure_reset_action()
        self.structure_arm_tool("group", {"type": "partie", "label": "Nouvelle partie"})

    def _structure_action_button(self, mode: str):
        # V24 — sélection → commande → Confirmer, y compris pour plusieurs pages.
        # V24_LIGNE_STRUCTURE_IMMOBILE_CONSERVEE : aucune action ne recentre automatiquement B.
        mode = str(mode or "")
        if mode not in {"duplicate", "delete"}:
            return

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
            ok = self.structure_duplicate_selected()
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

        # V23 : un seul ruban Structure centré. Page auto est lié directement
        # à la page sélectionnée ; les commandes d'édition restent à droite.
        self.structure_command_bar = tk.Frame(
            viewer, bg="#102633",
            highlightthickness=1, highlightbackground="#C39A4A",
            padx=8, pady=4,
        )
        self.structure_command_bar.grid(row=1, column=0, pady=(2, 2))

        tk.Label(
            self.structure_command_bar, text="Page auto :",
            bg="#102633", fg="#D7C08A",
            font=(theme.FONT_UI, 8, "bold"),
        ).pack(side="left", padx=(3, 5))

        self.structure_auto_before_btn = self._structure_bar_button(
            self.structure_command_bar, "Avant",
            lambda: self._structure_open_auto_menu("before", self.structure_auto_before_btn),
        )
        self.structure_auto_before_btn.pack(side="left", padx=3, pady=1)
        self.structure_auto_after_btn = self._structure_bar_button(
            self.structure_command_bar, "Après",
            lambda: self._structure_open_auto_menu("after", self.structure_auto_after_btn),
        )
        self.structure_auto_after_btn.pack(side="left", padx=3, pady=1)

        separator = tk.Frame(self.structure_command_bar, bg="#5D6D76", width=1, height=22)
        separator.pack(side="left", padx=10, pady=3)
        separator.pack_propagate(False)

        self.structure_new_part_btn = self._structure_bar_button(
            self.structure_command_bar, "+ Partie", self._structure_new_part_command
        )
        self.structure_new_part_btn.pack(side="left", padx=3, pady=1)
        self.structure_duplicate_btn = self._structure_bar_button(
            self.structure_command_bar, "Dupliquer", lambda: self._structure_action_button("duplicate")
        )
        self.structure_duplicate_btn.pack(side="left", padx=3, pady=1)
        self.structure_delete_btn = self._structure_bar_button(
            self.structure_command_bar, "Supprimer", lambda: self._structure_action_button("delete"), danger=True
        )
        self.structure_delete_btn.pack(side="left", padx=3, pady=1)

        nav_row = tk.Frame(viewer, bg=theme.WINDOW_DEEP, height=46)
        nav_row.grid(row=2, column=0, sticky="ew")
        nav_row.grid_propagate(False)

        # Dans B, on ne garde plus de commande de zoom générale.
        # Le zoom appartient désormais à la visionneuse de page seulement.
        nav_dock = tk.Frame(nav_row, bg=theme.WINDOW_DEEP)
        nav_dock.place(relx=0.5, rely=0.5, anchor="center")

        self.h_nav = TLBookNavigator(nav_dock, command=self._navigate_horizontal)
        self.h_nav.pack(side="left")

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
        self._work_mode = mode
        titles = {
            "structure": "Structure du livre",
            "gabarits": "Gabarit — page",
            "production": "Production — page",
            "sortie": "Sortie — contrôle",
        }
        self.work_title_var.set(titles.get(mode, "Livre"))
        bar = getattr(self, "structure_command_bar", None)
        if bar is not None:
            if mode == "structure":
                bar.grid()
            else:
                bar.grid_remove()
        if mode != "structure":
            self._drag_kind = None
            self._dragging = False
            self.structure_cancel_tool()
            self._structure_reset_action()
            try:
                self._cancel_drag_autoscroll()
            except Exception:
                pass
        self.render()

    # ------------------------------------------------------------------
    # Structure V5 : C = outils / B = zone de travail
    # ------------------------------------------------------------------

    def structure_available_page_types(self) -> list[tuple[str, str, bool]]:
        defaults = [
            ("page_titre", "Page de titre", False),
            ("sommaire", "Sommaire", False),
            ("avant_propos", "Avant-propos", False),
            ("tete_partie", "Tête de partie", False),
            ("chapitre", "Chapitre", False),
            ("texte", "Texte", False),
            ("illustration", "Illustration", False),
            ("fiche", "Fiche", False),
            ("transition", "Transition", False),
            ("annexe", "Annexe", False),
            ("conclusion", "Conclusion", False),
            ("remerciements", "Remerciements", False),
        ]
        result = list(defaults)
        seen = {key for key, _label, _custom in result}
        data = self._data if isinstance(self._data, dict) else {}
        definitions = data.get("page_types", [])
        if isinstance(definitions, list):
            for definition in definitions:
                if not isinstance(definition, dict):
                    continue
                type_key = str(definition.get("type") or definition.get("id") or "").strip()
                if not type_key or type_key in seen:
                    continue
                if type_key.lower() in self.COVER_TYPES | self.BACK_COVER_TYPES | self.SECOND_COVER_TYPES | self.THIRD_COVER_TYPES:
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
        self._data = data
        self.project.save_mockup(data)
        if self.on_change is not None:
            self.on_change()
        self.status_var.set(f"Nouveau type  •  {short_label}")
        return type_key, short_label

    def structure_auto_source_allowed(self, item: dict | None) -> bool:
        if not isinstance(item, dict):
            return False
        return not self._is_locked_page(item) and not self._is_automatic_page(item)

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

    def structure_set_page_auto_type_rule(self, source_type: str, position: str, target_type: str) -> bool:
        source = str(source_type or "").strip()
        position = str(position or "").strip().lower()
        target = str(target_type or "").strip()
        if position not in {"before", "after"} or not source:
            return False
        allowed = {key for key, _label in self.structure_auto_target_options()}
        if target not in allowed:
            return False
        protected = self.COVER_TYPES | self.BACK_COVER_TYPES | self.SECOND_COVER_TYPES | self.THIRD_COVER_TYPES
        if source.lower() in protected:
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
        entry[position] = target
        rules[source] = entry
        data["page_auto_type_rules"] = rules
        self._data = data
        if self.project is not None:
            self.project.save_mockup(data)

        self._sync_all_page_auto(source_type=source, save=True)
        return True

    def structure_remove_page_auto_type_rule(self, source_type: str, position: str) -> bool:
        source = str(source_type or "").strip()
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
        entry.pop(position, None)
        if entry:
            rules[source] = entry
        else:
            rules.pop(source, None)
        data["page_auto_type_rules"] = rules
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
        # Synchronise les pages auto locales Avant / Après d'une page principale.
        if item not in self.items or not self.structure_auto_source_allowed(item):
            return False
        item_id = str(item.get("id") or "").strip()
        if not item_id:
            item_id = f"MAQUETTE-{uuid4().hex[:12].upper()}"
            item["id"] = item_id

        generated_kinds = {"page_auto_before", "page_auto_after"}
        previous = [
            candidate for candidate in self.items
            if str(candidate.get("automatic_kind") or "") in generated_kinds
            and self._automatic_parent_id(candidate) == item_id
        ]
        if previous:
            previous_ids = {id(candidate) for candidate in previous}
            self.items = [candidate for candidate in self.items if id(candidate) not in previous_ids]

        before_type = self._structure_page_auto_type(item, "before")
        after_type = self._structure_page_auto_type(item, "after")
        changed = bool(previous)

        def make_auto(target_type: str, position: str) -> dict:
            definition = self._structure_type_definition(target_type)
            label = str(
                definition.get("short_label")
                or definition.get("label")
                or target_type.replace("_", " ").strip().capitalize()
            )
            auto_item = {
                "id": f"AUTO-{uuid4().hex[:12].upper()}",
                "count": 1,
                "done": False,
                "plan_group": self._item_group_id(item),
                "automatic": True,
                "auto_generated": True,
                "automatic_kind": f"page_auto_{position}",
                "automatic_position": position,
                "parent_id": item_id,
                "source_page_id": item_id,
                "structure_duplicable": False,
            }
            self._structure_apply_type_metadata(auto_item, target_type, label)
            auto_item["automatic"] = True
            auto_item["auto_generated"] = True
            auto_item["automatic_kind"] = f"page_auto_{position}"
            auto_item["automatic_position"] = position
            auto_item["parent_id"] = item_id
            auto_item["source_page_id"] = item_id
            auto_item["structure_duplicable"] = False
            return auto_item

        if before_type:
            source_index = self.items.index(item)
            self.items.insert(source_index, make_auto(before_type, "before"))
            changed = True
        if after_type:
            source_index = self.items.index(item)
            self.items.insert(source_index + 1, make_auto(after_type, "after"))
            changed = True
        return changed

    def _sync_all_page_auto(self, *, source_type: str = "", save: bool = False) -> bool:
        source_type = str(source_type or "").strip().lower()
        changed = False
        sources = [
            item for item in list(self.items)
            if self.structure_auto_source_allowed(item)
            and (not source_type or self._type_of(item) == source_type)
        ]
        for item in sources:
            if item in self.items:
                changed = self._sync_page_auto_for_source(item) or changed
        if changed and save:
            self._save_order()
            self.render()
        elif changed:
            self.render()
        return changed

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

    def _structure_open_auto_menu(self, position: str, widget) -> None:
        position = str(position or "").strip().lower()
        if position not in {"before", "after"}:
            return
        indices = self._selected_source_indices()
        if not indices:
            self.status_var.set("Sélectionnez d'abord une page principale dans B.")
            return
        sources = [self.items[index] for index in indices]
        if any(not self.structure_auto_source_allowed(item) for item in sources):
            self.status_var.set("Sélectionnez uniquement des pages principales.")
            return

        options = list(self.structure_auto_target_options())
        last = str(getattr(self, "_structure_last_auto_type", "") or "")
        if last:
            options.sort(key=lambda entry: 0 if entry[0] == last else 1)

        source_types = {self._type_of(item) for item in sources if self._type_of(item)}
        same_type = len(source_types) == 1
        source_type = next(iter(source_types)) if same_type else ""
        source_label = (
            self._structure_type_definition(source_type).get("label")
            or source_type.replace("_", " ").strip().capitalize()
        ) if source_type else ""
        local_scope_label = "Cette page" if len(sources) == 1 else f"Les {len(sources)} pages sélectionnées"

        menu = tk.Menu(
            self, tearoff=False,
            bg="#102633", fg="#F2F3F1",
            activebackground="#203B4B", activeforeground="#FFFFFF",
            bd=0, relief="flat",
            font=(theme.FONT_UI, 9),
        )

        effective = {self._structure_page_auto_type(item, position) for item in sources}
        current = next(iter(effective)) if len(effective) == 1 else ""

        def choose(type_key: str, scope: str):
            self._structure_last_auto_type = type_key
            self.structure_set_selected_page_auto(position, type_key, scope=scope)

        for type_key, label in options:
            visible = f"✓  {label}" if type_key == current else str(label)
            scope_menu = tk.Menu(
                menu, tearoff=False,
                bg="#102633", fg="#F2F3F1",
                activebackground="#203B4B", activeforeground="#FFFFFF",
                bd=0, relief="flat",
                font=(theme.FONT_UI, 9),
            )
            scope_menu.add_command(
                label=local_scope_label,
                command=lambda key=type_key: choose(key, "local"),
            )
            if same_type and source_type:
                scope_menu.add_command(
                    label=f'Toutes les pages « {source_label} »',
                    command=lambda key=type_key: choose(key, "type"),
                )
            menu.add_cascade(label=visible, menu=scope_menu)

        menu.add_separator()
        menu.add_command(
            label="Retirer pour cette sélection" if len(sources) > 1 else "Retirer pour cette page",
            command=lambda: self.structure_set_selected_page_auto(position, "", scope="local"),
        )

        has_override = any(
            self._page_auto_override_value(item, position) is not None
            for item in sources
        )
        if has_override and same_type and self.structure_get_page_auto_type_rule(source_type, position):
            menu.add_command(
                label="Suivre la règle générale",
                command=lambda: self.structure_reset_selected_page_auto_override(position),
            )

        if same_type and source_type and self.structure_get_page_auto_type_rule(source_type, position):
            menu.add_command(
                label=f'Retirer la règle « {source_label} »',
                command=lambda: self.structure_set_selected_page_auto(position, "", scope="type"),
            )

        try:
            menu.tk_popup(widget.winfo_rootx(), widget.winfo_rooty() + widget.winfo_height())
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass

    def structure_general_auto_rules(self) -> dict[str, str]:
        data = self._data if isinstance(self._data, dict) else {}
        raw = data.get("automatic_follow_rules", {})
        if not isinstance(raw, dict):
            return {}
        allowed_targets = {key for key, _label in self.structure_auto_target_options()}
        result: dict[str, str] = {}
        for source, target in raw.items():
            source_key = str(source or "").strip()
            target_key = str(target or "").strip()
            if source_key and target_key in allowed_targets:
                result[source_key] = target_key
        return result

    def structure_get_general_auto_rule(self, source_type: str) -> str:
        return self.structure_general_auto_rules().get(str(source_type or "").strip(), "")

    def structure_set_general_auto_rule(self, source_type: str, target_type: str) -> bool:
        source = str(source_type or "").strip()
        target = str(target_type or "").strip()
        if not source or target not in {key for key, _label in self.structure_auto_target_options()}:
            self.status_var.set("Choisissez une page source et une page automatique associée.")
            return False
        protected = self.COVER_TYPES | self.BACK_COVER_TYPES | self.SECOND_COVER_TYPES | self.THIRD_COVER_TYPES
        if source.lower() in protected:
            self.status_var.set("Les couvertures ne peuvent pas déclencher de page automatique.")
            return False
        if self.project is None:
            return False
        try:
            data = self.project.load_mockup()
        except Exception:
            data = deepcopy(self._data)
        if not isinstance(data, dict):
            data = {}
        rules = data.get("automatic_follow_rules", {})
        if not isinstance(rules, dict):
            rules = {}
        rules[str(source)] = target
        data["automatic_follow_rules"] = rules
        self._data = data
        self.project.save_mockup(data)
        self._sync_all_auto_follow(save=True)
        source_label = self._structure_type_definition(source).get("label") or source.replace("_", " ").strip().capitalize()
        target_label = self._structure_type_definition(target).get("label") or target.replace("_", " ").strip().capitalize()
        self.status_var.set(f"Règle générale  •  {source_label} → {target_label}")
        return True

    def structure_remove_general_auto_rule(self, source_type: str) -> bool:
        source = str(source_type or "").strip()
        if not source or self.project is None:
            return False
        try:
            data = self.project.load_mockup()
        except Exception:
            data = deepcopy(self._data)
        if not isinstance(data, dict):
            data = {}
        rules = data.get("automatic_follow_rules", {})
        if not isinstance(rules, dict) or source not in rules:
            return False
        rules = dict(rules)
        rules.pop(source, None)
        data["automatic_follow_rules"] = rules
        self._data = data
        self.project.save_mockup(data)
        self._sync_all_auto_follow(save=True)
        self.status_var.set("Règle générale supprimée.")
        return True

    def _auto_follow_rule_target_for_item(self, item: dict) -> str:
        if not self.structure_auto_source_allowed(item):
            return ""
        override = item.get("auto_follow_override", None)
        if override is not None:
            value = str(override or "").strip()
            return "" if value == "__none__" else value
        source = self._type_of(item)
        return self.structure_get_general_auto_rule(source) if source else ""

    def _auto_follow_generated_for_parent(self, parent_id: str) -> list[dict]:
        parent_id = str(parent_id or "").strip()
        return [
            candidate for candidate in self.items
            if str(candidate.get("automatic_kind") or "") == "follow_rule"
            and self._automatic_parent_id(candidate) == parent_id
        ]

    def _sync_auto_follow_for_source(self, item: dict) -> bool:
        if item not in self.items or not self.structure_auto_source_allowed(item):
            return False
        item_id = str(item.get("id") or "").strip()
        if not item_id:
            item_id = f"MAQUETTE-{uuid4().hex[:12].upper()}"
            item["id"] = item_id
        target_type = self._auto_follow_rule_target_for_item(item)
        existing = self._auto_follow_generated_for_parent(item_id)
        changed = False
        keep = None
        if target_type:
            for candidate in existing:
                if self._type_of(candidate) == target_type.lower() and keep is None:
                    keep = candidate
                else:
                    try:
                        self.items.remove(candidate)
                        changed = True
                    except ValueError:
                        pass
        else:
            for candidate in existing:
                try:
                    self.items.remove(candidate)
                    changed = True
                except ValueError:
                    pass
            return changed

        if keep is None and target_type:
            definition = self._structure_type_definition(target_type)
            label = str(definition.get("short_label") or definition.get("label") or target_type.replace("_", " ").strip().capitalize())
            auto_item = {
                "id": f"AUTO-{uuid4().hex[:12].upper()}",
                "count": 1,
                "done": False,
                "plan_group": self._item_group_id(item),
                "automatic": True,
                "auto_generated": True,
                "automatic_kind": "follow_rule",
                "parent_id": item_id,
                "source_page_id": item_id,
            }
            self._structure_apply_type_metadata(auto_item, target_type, label)
            auto_item["automatic"] = True
            auto_item["auto_generated"] = True
            auto_item["automatic_kind"] = "follow_rule"
            auto_item["parent_id"] = item_id
            auto_item["source_page_id"] = item_id
            auto_item["structure_duplicable"] = False
            try:
                source_index = self.items.index(item)
            except ValueError:
                return changed
            # Une page automatique est insérée juste derrière sa page source.
            # Ne pas utiliser _move_page_to_group_position ici : cette méthode
            # traite volontairement source + autos comme un bloc lors des déplacements.
            self.items.insert(source_index + 1, auto_item)
            changed = True
        return changed

    def _sync_all_auto_follow(self, *, save: bool = False) -> bool:
        # Reconstruit seulement les pages automatiques créées par ce nouveau système.
        originals = [item for item in self.items if str(item.get("automatic_kind") or "") != "follow_rule"]
        changed = len(originals) != len(self.items)
        self.items = originals
        for item in list(originals):
            if self.structure_auto_source_allowed(item):
                changed = self._sync_auto_follow_for_source(item) or changed
        if changed and save:
            self._save_order()
            self.render()
        elif changed:
            self.render()
        return changed

    def structure_selected_auto_context(self) -> dict:
        index = self._selected_index
        if index is None or not (0 <= index < len(self.items)):
            return {"selected": False}
        item = self.items[index]
        if self._is_automatic_page(item):
            return {
                "selected": True, "allowed": False, "automatic_page": True,
                "page_label": self._page_type_label(item, index),
            }
        allowed = self.structure_auto_source_allowed(item)
        source_type = self._type_of(item)
        general = self.structure_get_general_auto_rule(source_type) if source_type else ""
        override = item.get("auto_follow_override", None)
        if override is None:
            mode = "inherit"
            local_target = ""
        else:
            raw = str(override or "").strip()
            if raw == "__none__":
                mode, local_target = "none", ""
            else:
                mode, local_target = "local", raw
        effective = self._auto_follow_rule_target_for_item(item) if allowed else ""
        return {
            "selected": True, "allowed": allowed, "automatic_page": False,
            "index": index, "page_label": self._page_type_label(item, index),
            "source_type": source_type, "general_target": general,
            "mode": mode, "local_target": local_target, "effective_target": effective,
        }

    def structure_set_selected_auto_override(self, mode: str, target_type: str = "") -> bool:
        index = self._selected_index
        if index is None or not (0 <= index < len(self.items)):
            return False
        item = self.items[index]
        if not self.structure_auto_source_allowed(item):
            self.status_var.set("Cette page ne peut pas déclencher de page automatique.")
            return False
        mode = str(mode or "inherit")
        if mode == "inherit":
            item.pop("auto_follow_override", None)
        elif mode == "none":
            item["auto_follow_override"] = "__none__"
        else:
            target = str(target_type or "").strip()
            if target not in {key for key, _label in self.structure_auto_target_options()}:
                return False
            item["auto_follow_override"] = target
        self._sync_auto_follow_for_source(item)
        self._save_order()
        self.render()
        return True

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
        self._structure_pending_kind = str(kind or "")
        self._structure_pending_payload = payload
        self._structure_hover_target = None
        label = "brique"
        if isinstance(payload, dict):
            label = str(payload.get("label") or payload.get("name") or label)
        elif isinstance(payload, (tuple, list)) and len(payload) > 1:
            label = str(payload[1])
        self.status_var.set(
            f"{label}  •  déplacez la souris dans B puis cliquez à l’emplacement voulu"
        )
        try:
            self.canvas.configure(cursor="crosshair")
        except Exception:
            pass
        self.render()

    def structure_cancel_tool(self) -> None:
        self._structure_pending_kind = None
        self._structure_pending_payload = None
        self._structure_hover_target = None
        try:
            self.canvas.configure(cursor="arrow")
        except Exception:
            pass
        self.render()

    def _structure_global_click(self, event):
        """Un clic hors de B/bandeau annule l'outil ou l'action en cours."""
        pending = bool(getattr(self, "_structure_pending_kind", None))
        action = bool(getattr(self, "_structure_action_mode", None))
        if not pending and not action:
            return
        widget = getattr(event, "widget", None)
        try:
            widget_path = str(widget)
            canvas_path = str(self.canvas)
            bar = getattr(self, "structure_command_bar", None)
            bar_path = str(bar) if bar is not None else ""
            inside_canvas = widget is self.canvas or widget_path.startswith(canvas_path)
            inside_bar = bool(bar_path) and (widget is bar or widget_path.startswith(bar_path))
        except Exception:
            inside_canvas = widget is self.canvas
            inside_bar = False
        if not inside_canvas and not inside_bar:
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

        item["structure_side"] = str(definition.get("side") or "libre")
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
            self._sync_auto_follow_for_source(item)
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
        page_type = str(page_type or "")
        label = str(label or ("Sans type" if not page_type else "Page")).strip() or (
            "Sans type" if not page_type else "Page"
        )
        self._structure_apply_type_metadata(item, page_type, label)
        self._selected_index = int(index)
        self._selected_group_id = self._item_group_id(item)
        self._structure_selection_kind = "page"
        item.pop("auto_follow_override", None)
        for key in ("page_auto_before_override", "page_auto_after_override", "page_auto_before_type", "page_auto_after_type"):
            item.pop(key, None)
        self._sync_auto_follow_for_source(item)
        self._sync_page_auto_for_source(item)
        self._save_order()
        self.render()
        self.status_var.set(f"Type remplacé  •  {label}")
        return True

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
        self._selected_group_id = group_id
        self._structure_selection_kind = "group"
        self._save_order()
        self.render()
        self.status_var.set(f"Partie créée  •  Partie {number}")
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

    def _structure_page_hover_target(self, event):
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
        if kind == "page" and target and target[0] == "page":
            _kind, group_id, local_pos, _tx = target
            page_type, label = self._structure_normalize_page_payload(payload)
            success = self._structure_insert_page(page_type, label, group_id, local_pos) is not None
        elif kind == "group" and target and target[0] == "group":
            _kind, position, _tx = target
            success = self._structure_insert_group_at_position(position) is not None
        if success:
            self.structure_cancel_tool()
        else:
            self.structure_cancel_tool()
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

    def structure_duplicate_selected(self) -> bool:
        kind = getattr(self, "_structure_selection_kind", "page")
        if kind == "group":
            group_id = str(self._selected_group_id or "")
            if group_id in {self.START_GROUP_ID, self.END_GROUP_ID}:
                self.status_var.set("Le début et la fin du livre sont protégés.")
                return False
            source_group = next((g for g in self.groups if str(g.get("id") or "") == group_id), None)
            if source_group is None:
                return False
            new_group = deepcopy(source_group)
            new_group_id = f"partie_{uuid4().hex[:10]}"
            new_group["id"] = new_group_id
            part_title = str(new_group.get("part_title") or "").strip()
            if part_title:
                new_group["part_title"] = f"{part_title} copie"
            try:
                source_pos = next(i for i, g in enumerate(self.groups) if str(g.get("id") or "") == group_id)
            except StopIteration:
                return False
            self.groups.insert(source_pos + 1, new_group)

            originals = [item for item in self.items if self._item_group_id(item) == group_id and not self._is_automatic_page(item)]
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
            self.items.extend(clones)
            self._selected_group_id = new_group_id
            self._selected_index = None
            self._selected_page_ids.clear()
            self._structure_selection_kind = "group"
            self._sync_all_auto_follow(save=False)
            for clone in list(clones):
                self._sync_page_auto_for_source(clone)
            self._save_order()
            self.render()
            self.status_var.set("Partie dupliquée.")
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

        # Les copies de chaque partie sont insérées ensemble après le dernier bloc sélectionné.
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
                    clone["page_name"] = f"{name} copie"
                clones.append(clone)
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
                self._sync_auto_follow_for_source(clone)
                self._sync_page_auto_for_source(clone)

        self._save_order()
        clone_ids = {str(clone.get("id") or "") for clone in all_clones}
        clone_indices = [
            index for index, item in enumerate(self.items)
            if str(item.get("id") or "") in clone_ids
        ]
        self._set_multi_page_selection(clone_indices)
        self.render()
        self.status_var.set(
            "Pages dupliquées avec leurs pages auto."
            if len(all_clones) > 1 else
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
            if self._group_items(group_id):
                self.status_var.set("Partie non vide : déplacez d'abord ses pages dans B.")
                return False
            self.groups = [
                group for group in self.groups if str(group.get("id", "")) != group_id
            ]
            self._selected_group_id = self.DEFAULT_GROUP_ID
            self._selected_page_ids.clear()
            self._structure_selection_kind = "group"
            self._save_order()
            self.render()
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

        self._selected_page_ids.clear()
        if self.items:
            self._set_single_page_selection(min(first_index, len(self.items) - 1))
        else:
            self._selected_index = None
            self._selected_group_id = None
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
            if changed:
                try:
                    project.save_mockup(data)
                except Exception:
                    pass

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
        data.setdefault("automatic_follow_rules", {})
        data.setdefault("page_auto_type_rules", {})
        return data, changed

    def _save_order(self):
        if self.project is None:
            return
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
        self._data = data
        self.project.save_mockup(data)
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
        for key in ("recto_target_id", "linked_to", "parent_id", "source_page_id"):
            value = str(item.get(key) or "").strip()
            if value:
                return value
        return ""

    def _linked_automatic_items(self, item: dict) -> list[dict]:
        item_id = str(item.get("id") or "").strip()
        if not item_id:
            return []
        return [
            candidate for candidate in self.items
            if self._is_automatic_page(candidate) and self._automatic_parent_id(candidate) == item_id
        ]

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
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.after_idle(self._update_visible_part_marker)

    def _active_group_id(self) -> str:
        if self._selected_group_id and any(str(g.get("id", "")) == self._selected_group_id for g in self.groups):
            return self._selected_group_id
        if self._selected_index is not None and 0 <= self._selected_index < len(self.items):
            return self._item_group_id(self.items[self._selected_index])
        return self.START_GROUP_ID

    def _page_size_factor(self, index: int, active_group_id: str | None = None) -> float:
        """Quatre tailles : tête de partie, page, automatique, sélectionnée."""
        if not 0 <= index < len(self.items):
            return self.PAGE_SIZE_NORMAL
        item = self.items[index]
        if index == self._selected_index:
            return self.PAGE_SIZE_SELECTED
        if self._is_automatic_page(item):
            return self.PAGE_SIZE_AUTO
        if self._is_part_head_page(item):
            return self.PAGE_SIZE_PART_HEAD
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
            if self._is_automatic_page(item):
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

    def _draw_page(self, index: int, x: float, y: float, page_w: float, page_h: float, scale: float, *, show_label: bool = True):
        item = self.items[index]
        selected = self._is_page_index_selected(index)
        hovered = index == self._hover_index and not self._dragging
        automatic = self._is_automatic_page(item)
        if selected:
            fill = "#EDF1EE"
            outline = self.GOLD if hovered else theme.ACCENT
            outline_width = 4 if hovered else 3
        elif hovered:
            fill = "#F0F3F1"
            outline = theme.ACCENT_BRIGHT
            outline_width = 2
        elif automatic:
            fill = "#E8ECE9"
            outline = theme.ACCENT_DARK
            outline_width = 1
        else:
            fill = "#F0F1EE"
            outline = "#D5D7D3"
            outline_width = 1

        shadow = max(1, min(10, int(3 * scale)))
        self.canvas.create_rectangle(x + shadow, y + shadow, x + page_w + shadow, y + page_h + shadow, fill="#151B21", outline="")
        self.canvas.create_rectangle(x, y, x + page_w, y + page_h, fill=fill, outline=outline, width=outline_width)

        rail_h = max(2, min(9, int(5 * scale)))
        top_pad = max(2, 8 * scale)
        rail_color = self.GOLD if self._is_locked_page(item) else theme.ACCENT_DARK
        self.canvas.create_rectangle(x + top_pad, y + top_pad, x + page_w - top_pad, y + top_pad + rail_h, fill=rail_color, outline="")

        page_type = self._page_type_label(item, index)
        self._draw_type_preview(item, x, y, page_w, page_h, page_type, scale)

        if automatic:
            # La petite liaison rappelle que cette page appartient à une autre page.
            self.canvas.create_oval(
                x + max(4, 7 * scale), y + max(4, 7 * scale),
                x + max(10, 16 * scale), y + max(10, 16 * scale),
                fill=theme.ACCENT_SOFT, outline=theme.ACCENT_BRIGHT, width=1,
            )

        if page_w >= 34:
            number_size = max(6, min(18, int(6 + self.zoom / 65)))
            self.canvas.create_text(
                x + page_w - max(8, 13 * scale),
                y + page_h - max(7, 12 * scale),
                anchor="se",
                text=str(index + 1),
                fill="#737B78",
                font=(theme.FONT_UI, number_size),
            )

        # Nom libre de la page AU-DESSUS ; clic direct pour le modifier.
        name = self._page_display_name(item, index)
        name_text = name or ("Cliquer pour nommer" if selected or hovered else "")
        name_y1 = y - self.PAGE_NAME_H
        name_y2 = y - 2
        self._page_name_hitboxes[index] = (x, name_y1, x + page_w, name_y2)
        if name_text:
            self.canvas.create_text(
                x + page_w / 2.0,
                y - 5,
                anchor="s",
                text=name_text,
                fill=theme.INK if name else theme.MUTED_DARK,
                width=max(50, page_w + 24),
                font=(theme.FONT_UI, max(6, min(13, int(7 + self.zoom / 100))), "bold" if name else "italic"),
                justify="center",
                tags=(f"page_name:{index}", "page_name"),
            )

        if show_label:
            label_size = max(6, min(15, int(7 + self.zoom / 80)))
            self.canvas.create_text(
                x + page_w / 2.0,
                y + page_h + max(9, 14 * scale),
                anchor="n",
                text=page_type,
                fill=theme.INK,
                width=max(50, page_w + 26),
                font=(theme.FONT_UI, label_size, "bold" if selected else "normal"),
                justify="center",
            )
        self._page_hitboxes[index] = (x, y, x + page_w, y + page_h)

    def render(self):
        self._render_pending = None
        if not hasattr(self, "canvas"):
            return

        # Ne jamais effacer le Canvas pendant une saisie directe : l'ancien
        # comportement refermait l'éditeur dès qu'un survol déclenchait render().
        if self._title_editor is not None or self._page_name_editor is not None:
            return

        viewport_w = max(300, self.canvas.winfo_width())
        viewport_h = max(180, self.canvas.winfo_height())
        self.canvas.delete("all")
        self._page_hitboxes = {}
        self._page_name_hitboxes = {}
        self._image_refs = []
        self._group_hitboxes = {}
        self._group_page_bounds = {}
        self._visual_indices = []

        if not self.items:
            self.status_var.set("Aucun projet chargé")
            self.canvas.create_text(viewport_w / 2, viewport_h / 2, text="Ouvrez un projet pour afficher son livre.", fill=theme.MUTED, font=(theme.FONT_UI, 10))
            self.canvas.configure(scrollregion=(0, 0, viewport_w, viewport_h))
            self._update_scrollbars(viewport_w, viewport_h)
            return

        if self._selected_index is None or not (0 <= self._selected_index < len(self.items)):
            self._selected_index = 0

        selected_page_number = self._selected_index + 1
        middle_count = sum(1 for group in self.groups if str(group.get("id", "")) not in {self.START_GROUP_ID, self.END_GROUP_ID})
        if self._page_focus:
            self.status_var.set(f"Page {selected_page_number} sur {len(self.items)}  •  travail détaillé")
        else:
            self.status_var.set(f"{middle_count} partie{'s' if middle_count != 1 else ''}  •  {len(self.items)} page{'s' if len(self.items) != 1 else ''}")

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
                factor = self._page_size_factor(index, active_group_id)
                specs[index] = (
                    max(16, self.BASE_PAGE_W * scale * factor),
                    max(22, self.BASE_PAGE_H * scale * factor),
                )

            # On calcule d'abord toutes les largeurs pour pouvoir centrer un livre court.
            group_layout: list[tuple[dict, list[int], float]] = []
            for group in self.groups:
                group_id = str(group.get("id", ""))
                indexes = self._group_items(group_id)
                if indexes:
                    body_w = sum(specs[i][0] for i in indexes) + gap * max(0, len(indexes) - 1)
                else:
                    body_w = max(90, self.EMPTY_SLOT_W * scale)
                min_header = max(150, min(300, 174 + max(len(self._group_name(group)), len(self._group_part_title(group))) * 2))
                group_layout.append((group, indexes, max(body_w, min_header)))

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
                left_pad = right_pad = margin
                x = (viewport_w - content_w) / 2.0
            group_y1 = margin
            group_y2 = group_y1 + self.GROUP_H

            max_page_h = max((h for _w, h in specs.values()), default=self.BASE_PAGE_H * scale)
            row_needed = self.PAGE_NAME_H + max_page_h + self.PAGE_LABEL_H
            available_top = group_y2 + self.GROUP_TO_PAGE
            available_h = max(0, viewport_h - available_top - margin)
            page_row_top = available_top + max(0, (available_h - row_needed) / 2.0)
            page_bottom = page_row_top + row_needed

            for group_pos, (group, indexes, group_width) in enumerate(group_layout):
                group_id = str(group.get("id", ""))
                start_x = x
                cursor_x = start_x
                if indexes:
                    for local_pos, index in enumerate(indexes):
                        self._visual_indices.append(index)
                        page_w, page_h = specs[index]
                        page_y = page_row_top + self.PAGE_NAME_H + (max_page_h - page_h)
                        self._draw_page(index, cursor_x, page_y, page_w, page_h, scale)
                        cursor_x += page_w
                        if local_pos < len(indexes) - 1:
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
        """Repère fixe dans la barre de B : la partie sous le centre de la vue."""
        self._sticky_part_job = None
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
            parent_id = self._automatic_parent_id(item)
            parent_index = next((i for i, candidate in enumerate(self.items) if str(candidate.get("id") or "") == parent_id), None)
            if parent_index is not None:
                index = parent_index
                item = self.items[index]
        linked = set(id(candidate) for candidate in self._linked_automatic_items(item))
        return [i for i, candidate in enumerate(self.items) if i == index or id(candidate) in linked]

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
                parent_index = by_id.get(self._automatic_parent_id(item))
                if parent_index is not None and parent_index in index_set:
                    # Le bloc sera créé depuis la page principale.
                    continue
                blocks.append([index])
                consumed.add(index)
                continue
            item_id = str(item.get("id") or "")
            block = [index]
            if item_id:
                linked = [
                    i for i in indexes
                    if self._is_automatic_page(self.items[i]) and self._automatic_parent_id(self.items[i]) == item_id
                ]
                block.extend(linked)
            block = sorted(set(block))
            consumed.update(block)
            blocks.append(block)
        # Autos orphelines éventuellement sautées.
        for index in indexes:
            if index not in consumed:
                blocks.append([index])
        blocks.sort(key=lambda block: min(block))
        return blocks

    def _target_local_pos_from_x(self, canvas_x: float, group_id: str, *, dragged_index: int | None = None) -> int:
        excluded = set(self._drag_block_indices(dragged_index))
        visible_indexes = [i for i in self._group_items(group_id) if i not in excluded]
        blocks = self._page_blocks_in_group(group_id, exclude_indices=excluded)
        if not blocks:
            return 0
        for block in blocks:
            boxes = [self._page_hitboxes[i] for i in block if i in self._page_hitboxes]
            if not boxes:
                continue
            x1 = min(box[0] for box in boxes)
            x2 = max(box[2] for box in boxes)
            if canvas_x < (x1 + x2) / 2.0:
                first_index = min(block)
                return sum(1 for i in visible_indexes if i < first_index)
        return len(visible_indexes)

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
        if getattr(self, "_work_mode", "structure") == "structure" and getattr(self, "_structure_pending_kind", None):
            try:
                self.canvas.configure(cursor="crosshair")
            except Exception:
                pass
            self._structure_update_hover_target(event)
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
            if index is not None:
                self._set_single_page_selection(index)
            elif group_id is not None:
                self._selected_group_id = group_id
                self._selected_page_ids.clear()
            self.render()
            return "break"

        name_index = self._page_name_at(event)
        if name_index is not None:
            self._set_single_page_selection(name_index)
            self.after_idle(lambda idx=self._selected_index: self._begin_page_name_edit(idx) if idx is not None else None)
            return "break"

        title_group_id = self._group_title_at(event)
        if title_group_id is not None and not self._page_focus:
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

        # Glisser depuis un espace vide = cadre de sélection multiple à la souris.
        if group_id is None and index is None:
            cx = self.canvas.canvasx(event.x)
            cy = self.canvas.canvasy(event.y)
            self._selection_box_start = (cx, cy)
            self._selection_box_current = (cx, cy)
            self._selection_box_active = False
            self._drag_kind = None
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

        self._drag_kind = "page" if index is not None else None
        source_index = self._source_index_for_index(index)
        self._drag_start_index = source_index
        if source_index is not None:
            self._set_single_page_selection(source_index)
            self._drag_target_index = source_index
            self._drag_target_group_id = self._item_group_id(self.items[source_index])
            group_indexes = self._group_items(self._drag_target_group_id)
            self._drag_target_local_pos = group_indexes.index(source_index) if source_index in group_indexes else 0
            self.render()
        return "break"

    def _movable_group_ids(self) -> list[str]:
        return [str(group.get("id", "")) for group in self.groups if str(group.get("id", "")) not in {self.START_GROUP_ID, self.END_GROUP_ID}]

    def _on_drag(self, event):
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

        if self._drag_kind == "page" and self._drag_start_index is not None:
            if self._is_locked_page(self.items[self._drag_start_index]):
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
        excluded = set(self._drag_block_indices(self._drag_start_index))
        group_indexes = [index for index in self._group_items(group_id) if index not in excluded]
        y1 = min((box[1] for box in self._page_hitboxes.values()), default=self.MARGIN + self.GROUP_H)
        y2 = max((box[3] for box in self._page_hitboxes.values()), default=y1 + 100)
        if local_pos < len(group_indexes) and group_indexes[local_pos] in self._page_hitboxes:
            x = self._page_hitboxes[group_indexes[local_pos]][0] - 7
        elif group_indexes and group_indexes[-1] in self._page_hitboxes:
            x = self._page_hitboxes[group_indexes[-1]][2] + 7
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

    def _on_release(self, _event):
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
        target = self._drag_target_index
        target_group = self._drag_target_group_id
        target_local_pos = self._drag_target_local_pos
        drag_group_id = self._drag_group_id
        group_target = self._drag_group_target

        self._drag_kind = None
        self._drag_start_index = None
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
                self._reorder_items_by_group_order()
                self._selected_group_id = drag_group_id
                self._save_order()
            self.render()
            return "break"

        if kind == "page" and start is not None and target_group is not None and target_local_pos is not None:
            if start >= len(self.items) or self._is_locked_page(self.items[start]):
                self.render()
                return "break"
            item = self.items[start]
            self._move_page_to_group_position(item, target_group, target_local_pos)
            try:
                moved_index = self.items.index(item)
            except ValueError:
                moved_index = 0
            self._set_single_page_selection(moved_index)
            self._save_order()
            self.render()
            return "break"

        self.render()
        return "break"

    def _on_double_click(self, event):
        index = self._index_at(event)
        if index is not None:
            source_index = self._source_index_for_index(index)
            if source_index is None:
                return "break"
            self._set_single_page_selection(source_index)
            self.render()
            self.after_idle(lambda idx=source_index: self.open_page_overlay(index=idx, reset_zoom=True))
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
        # Zoom retire de la vue principale B : on neutralise ce raccourci ici.
        return "break"

    def _on_shift_mousewheel(self, event):
        if self._h_scroll_needed:
            delta = -1 if event.delta > 0 else 1
            self.canvas.xview_scroll(delta * 4, "units")
            self.after_idle(self._update_visible_part_marker)
        return "break"

    def _on_mousewheel(self, event):
        delta = -1 if event.delta > 0 else 1
        if self._v_scroll_needed:
            self.canvas.yview_scroll(delta * 4, "units")
        elif self._h_scroll_needed:
            self.canvas.xview_scroll(delta * 4, "units")
            self.after_idle(self._update_visible_part_marker)
        return "break"
