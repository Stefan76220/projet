from __future__ import annotations

import tkinter as tk
from copy import deepcopy
from typing import Callable
from uuid import uuid4

from src.gui_v3 import theme


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


class BookCanvas(tk.Frame):
    """Zone B TomeLinea : structure du livre en deux niveaux, parties puis pages."""

    MIN_ZOOM = 20
    MAX_ZOOM = 800
    BASE_PAGE_W = 420
    BASE_PAGE_H = 594
    BASE_GAP = 34
    BASE_GROUP_GAP = 76
    MARGIN = 34
    GROUP_H = 48
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
            "symbol": "flag",
            "accent": GOLD,
            "protected": True,
        },
        {
            "id": DEFAULT_GROUP_ID,
            "title": "Partie 1",
            "symbol": "book",
            "accent": theme.ACCENT_BRIGHT,
            "protected": False,
        },
        {
            "id": END_GROUP_ID,
            "title": "Fin du livre",
            "symbol": "book_end",
            "accent": BOOK_GREEN,
            "protected": True,
        },
    )

    COVER_TYPES = {"couverture", "cover", "front_cover"}
    BACK_COVER_TYPES = {"quatrieme", "quatrieme_couverture", "4e_couverture", "back_cover"}

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
        self._page_hitboxes: dict[int, tuple[float, float, float, float]] = {}
        self._group_hitboxes: dict[str, tuple[float, float, float, float]] = {}
        self._group_page_bounds: dict[str, tuple[float, float]] = {}
        self._visual_indices: list[int] = []

        self._drag_kind: str | None = None
        self._drag_start_index: int | None = None
        self._drag_target_index: int | None = None
        self._drag_target_group_id: str | None = None
        self._drag_group_id: str | None = None
        self._drag_group_target: int | None = None
        self._drag_start_xy: tuple[int, int] | None = None
        self._dragging = False
        self._render_pending = None
        self._page_focus = False
        self._book_zoom_cap = 100
        self._hover_index: int | None = None
        self._hover_group_id: str | None = None
        self._v_scroll_needed = False
        self._h_scroll_needed = False

        self.zoom_var = tk.IntVar(value=26)
        self.zoom_text_var = tk.StringVar(value="26 %")
        self.status_var = tk.StringVar(value="Livre en attente")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_toolbar()
        self._build_canvas()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build_toolbar(self):
        bar = tk.Frame(self, bg=theme.PANEL)
        bar.grid(row=0, column=0, sticky="ew", pady=(0, 7))
        bar.grid_columnconfigure(1, weight=1)

        tk.Label(
            bar,
            text="Structure du livre",
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

        controls = tk.Frame(bar, bg=theme.PANEL)
        controls.grid(row=0, column=2, sticky="e")
        self._tool_button(controls, "−", lambda: self.step_zoom(-10), width=3).pack(side="left", padx=(0, 4))

        self.zoom_scale = tk.Scale(
            controls,
            from_=self.MIN_ZOOM,
            to=self.MAX_ZOOM,
            orient="horizontal",
            variable=self.zoom_var,
            command=self._on_scale,
            showvalue=False,
            length=175,
            resolution=1,
            bg=theme.PANEL,
            fg=theme.INK,
            troughcolor=theme.PANEL_SOFT,
            activebackground=theme.ACCENT,
            highlightthickness=0,
            bd=0,
            sliderrelief="flat",
        )
        self.zoom_scale.pack(side="left")
        self._tool_button(controls, "+", lambda: self.step_zoom(10), width=3).pack(side="left", padx=(4, 7))

        tk.Label(
            controls,
            textvariable=self.zoom_text_var,
            width=6,
            anchor="e",
            bg=theme.PANEL,
            fg=theme.INK,
            font=(theme.FONT_UI, 8, "bold"),
        ).pack(side="left", padx=(0, 8))

        self._tool_button(controls, "Tout le livre", self.fit_book).pack(side="left", padx=(0, 4))
        self._tool_button(controls, "Page", self.fit_selected).pack(side="left")

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
        self.h_scroll = TLScrollbar(viewer, orient="horizontal", command=self.canvas.xview)
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)

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

    def set_project(self, project):
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
        self._page_focus = False
        self.render()
        if self.items:
            self.after_idle(self.fit_book)

    def _ensure_minimum_structure(self, source: dict) -> tuple[dict, bool]:
        data = deepcopy(source) if isinstance(source, dict) else {}
        changed = False

        defaults = {str(group["id"]): dict(group) for group in self.DEFAULT_GROUPS}
        raw_groups = data.get("groups", [])
        middle: list[dict] = []
        seen: set[str] = set()
        if isinstance(raw_groups, list):
            for raw in raw_groups:
                if not isinstance(raw, dict) or bool(raw.get("deleted", False)):
                    continue
                group_id = str(raw.get("id", "")).strip()
                if not group_id or group_id in {self.START_GROUP_ID, self.END_GROUP_ID} or group_id in seen:
                    continue
                title = str(raw.get("title") or raw.get("name") or "Partie").strip() or "Partie"
                accent = str(raw.get("accent") or theme.ACCENT_BRIGHT)
                middle.append(
                    {
                        **raw,
                        "id": group_id,
                        "title": title,
                        "symbol": str(raw.get("symbol") or "book"),
                        "accent": accent,
                        "protected": False,
                    }
                )
                seen.add(group_id)

        if self.DEFAULT_GROUP_ID not in seen:
            middle.insert(0, dict(defaults[self.DEFAULT_GROUP_ID]))

        groups = [dict(defaults[self.START_GROUP_ID]), *middle, dict(defaults[self.END_GROUP_ID])]
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
            old_group = str(item.get("plan_group", "")).strip()
            if self._is_cover(item):
                group_id = self.START_GROUP_ID
            elif self._is_back_cover(item):
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
                grouped.sort(key=lambda item: (0 if self._is_cover(item) else 1))
            elif group_id == self.END_GROUP_ID:
                grouped.sort(key=lambda item: (1 if self._is_back_cover(item) else 0))
            ordered.extend(grouped)

        # Conserve sans perte un éventuel item dont le groupe serait incohérent.
        known_ids = {id(item) for item in ordered}
        ordered.extend(item for item in items if id(item) not in known_ids)
        if ordered != items:
            changed = True
        data["items"] = ordered
        data.setdefault("page_types", [])
        data.setdefault("recto_verso_rules", [])
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

    def _is_locked_page(self, item: dict) -> bool:
        return self._is_cover(item) or self._is_back_cover(item)

    def _item_group_id(self, item: dict) -> str:
        if self._is_cover(item):
            return self.START_GROUP_ID
        if self._is_back_cover(item):
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

    # ------------------------------------------------------------------
    # Zoom continu
    # ------------------------------------------------------------------

    @property
    def zoom(self) -> int:
        return max(self.MIN_ZOOM, min(self.MAX_ZOOM, int(self.zoom_var.get())))

    @property
    def page_focus(self) -> bool:
        return bool(self._page_focus)

    def _normal_page_available_height(self) -> int:
        if not hasattr(self, "canvas"):
            return 180
        viewport_h = max(180, self.canvas.winfo_height())
        reserved = self.MARGIN * 2 + self.GROUP_H + self.GROUP_TO_PAGE
        return max(120, viewport_h - reserved)

    def _book_height_cap(self) -> int:
        value = int(self._normal_page_available_height() / float(self.BASE_PAGE_H) * 100)
        return max(self.MIN_ZOOM, min(self.MAX_ZOOM, value))

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

    def _on_scale(self, value):
        self.set_zoom(int(float(value)))

    def set_zoom(self, value: int, *, center_selected=True):
        requested = max(self.MIN_ZOOM, min(self.MAX_ZOOM, int(value)))
        if not self._page_focus:
            cap = self._book_height_cap()
            self._book_zoom_cap = cap
            if requested > cap and self._selected_index is not None:
                self._set_page_focus(True)
                value = requested
            else:
                value = min(requested, cap)
        else:
            if requested <= self._book_zoom_cap:
                self._set_page_focus(False)
                value = requested
            else:
                value = requested

        value = max(self.MIN_ZOOM, min(self.MAX_ZOOM, int(value)))
        if value == self.zoom and self.zoom_text_var.get() == f"{value} %":
            return
        self.zoom_var.set(value)
        self.zoom_text_var.set(f"{value} %")
        self.render()
        if center_selected and self._selected_index is not None:
            self.after_idle(self.center_selected)

    def step_zoom(self, delta: int):
        current = self.zoom
        if current < 100:
            step = 10
        elif current < 300:
            step = 25
        else:
            step = 50
        self.set_zoom(current + (step if delta > 0 else -step))

    def _logical_slots(self) -> int:
        count = 0
        for group in self.groups:
            group_id = str(group.get("id", ""))
            group_items = [item for item in self.items if self._item_group_id(item) == group_id]
            count += max(1, len(group_items))
        return max(1, count)

    def fit_book(self):
        if not self.items or not self.canvas.winfo_exists():
            return
        if self._page_focus:
            self._set_page_focus(False)
            self.after_idle(self.fit_book)
            return

        viewport_w = max(300, self.canvas.winfo_width() - 20)
        viewport_h = max(180, self.canvas.winfo_height() - 12)
        slots = self._logical_slots()
        group_count = max(1, len(self.groups))
        logical_w = slots * self.BASE_PAGE_W + max(0, slots - group_count) * self.BASE_GAP + max(0, group_count - 1) * self.BASE_GROUP_GAP
        logical_h = self.BASE_PAGE_H + self.GROUP_H + self.GROUP_TO_PAGE
        zoom_x = int(viewport_w / max(1, logical_w + self.MARGIN * 2) * 100)
        zoom_y = int((viewport_h - self.GROUP_H - self.GROUP_TO_PAGE - self.MARGIN * 2) / self.BASE_PAGE_H * 100)
        self._book_zoom_cap = self._book_height_cap()
        value = max(self.MIN_ZOOM, min(self._book_zoom_cap, zoom_x, zoom_y))
        self.set_zoom(value, center_selected=False)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

    def fit_selected(self):
        if self._selected_index is None:
            if self.items:
                self._selected_index = 0
            else:
                return
        if not self._page_focus:
            self._book_zoom_cap = self._book_height_cap()
            self._set_page_focus(True)
            self.after_idle(self.fit_selected)
            return

        viewport_w = max(300, self.canvas.winfo_width() - 70)
        viewport_h = max(180, self.canvas.winfo_height() - 70)
        zoom_x = int(viewport_w / self.BASE_PAGE_W * 100)
        zoom_y = int(viewport_h / self.BASE_PAGE_H * 100)
        value = max(self.MIN_ZOOM, min(self.MAX_ZOOM, zoom_x, zoom_y))
        self.set_zoom(value)

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

        title = str(group.get("title") or "Partie")
        count = len(self._group_items(group_id))
        self.canvas.create_text(
            x1 + 34,
            icon_y - 5,
            anchor="w",
            text=title,
            fill=theme.INK,
            font=(theme.FONT_UI, 8, "bold"),
            tags=tag,
        )
        state = f"{count} page" + ("s" if count != 1 else "")
        if not protected:
            state += "  ·  déplacer"
        self.canvas.create_text(
            x1 + 34,
            icon_y + 8,
            anchor="w",
            text=state,
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

    def _draw_page(self, index: int, x: float, y: float, page_w: float, page_h: float, scale: float):
        item = self.items[index]
        selected = index == self._selected_index
        hovered = index == self._hover_index and not self._dragging
        if selected:
            fill = "#E1ECE8"
            outline = self.GOLD if hovered else theme.ACCENT
            outline_width = 4 if hovered else 3
        elif hovered:
            fill = "#E7EFEC"
            outline = theme.ACCENT_BRIGHT
            outline_width = 2
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

        font_size = max(6, min(24, int(8 + self.zoom / 45)))
        number_size = max(6, min(22, int(7 + self.zoom / 55)))
        label = self._item_label(item, index)
        if page_w >= 55 and page_h >= 80:
            self.canvas.create_text(
                x + page_w / 2,
                y + page_h / 2 - max(0, 8 * scale),
                text=label,
                fill="#303740",
                width=max(30, page_w - max(18, 32 * scale)),
                font=(theme.FONT_UI, font_size, "bold"),
                justify="center",
            )
        if page_w >= 34:
            self.canvas.create_text(
                x + page_w / 2,
                y + page_h - max(8, 18 * scale),
                text=str(index + 1),
                fill="#6A737A",
                font=(theme.FONT_UI, number_size),
            )
        self._page_hitboxes[index] = (x, y, x + page_w, y + page_h)

    def render(self):
        self._render_pending = None
        if not hasattr(self, "canvas"):
            return

        viewport_w = max(300, self.canvas.winfo_width())
        viewport_h = max(180, self.canvas.winfo_height())
        self.canvas.delete("all")
        self._page_hitboxes = {}
        self._group_hitboxes = {}
        self._group_page_bounds = {}
        self._visual_indices = []

        if not self._page_focus:
            cap = self._book_height_cap()
            self._book_zoom_cap = cap
            if self.zoom > cap:
                self.zoom_var.set(cap)
        self.zoom_text_var.set(f"{self.zoom} %")

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
        page_w = max(16, self.BASE_PAGE_W * scale)
        page_h = max(22, self.BASE_PAGE_H * scale)
        gap = max(8, self.BASE_GAP * scale)
        group_gap = max(20, self.BASE_GROUP_GAP * scale)
        margin = max(20, self.MARGIN * min(scale, 1.0))

        if self._page_focus:
            total_w = max(viewport_w, page_w + margin * 2)
            total_h = max(viewport_h, page_h + margin * 2)
            x = max(margin, (total_w - page_w) / 2.0)
            y = max(margin, (total_h - page_h) / 2.0)
            self._draw_page(self._selected_index, x, y, page_w, page_h, scale)
        else:
            group_y1 = margin
            group_y2 = group_y1 + self.GROUP_H
            page_y = group_y2 + self.GROUP_TO_PAGE
            x = margin
            page_bottom = page_y + page_h

            for group_pos, group in enumerate(self.groups):
                group_id = str(group.get("id", ""))
                indexes = self._group_items(group_id)
                start_x = x
                if indexes:
                    for local_pos, index in enumerate(indexes):
                        self._visual_indices.append(index)
                        self._draw_page(index, x, page_y, page_w, page_h, scale)
                        x += page_w
                        if local_pos < len(indexes) - 1:
                            x += gap
                else:
                    empty_w = max(90, self.EMPTY_SLOT_W * scale)
                    # La zone d'attente n'a de sens que dans une partie centrale vide.
                    if group_id not in {self.START_GROUP_ID, self.END_GROUP_ID}:
                        self._draw_waiting_slot(x, page_y, x + empty_w, page_bottom, group)
                    x += empty_w

                end_x = x
                min_header = max(128, min(220, 155 + len(str(group.get("title", ""))) * 2))
                if end_x - start_x < min_header:
                    end_x = start_x + min_header
                    x = end_x
                self._group_hitboxes[group_id] = (start_x, group_y1, end_x, group_y2)
                self._group_page_bounds[group_id] = (start_x, end_x)
                self._draw_group_header(group, start_x, end_x, group_y1, group_y2)
                if group_pos < len(self.groups) - 1:
                    separator_x = x + group_gap / 2.0
                    self.canvas.create_line(separator_x, group_y1 + 4, separator_x, page_bottom, fill=theme.BORDER_SOFT, width=1, dash=(3, 5))
                    x += group_gap

            content_w = x - group_gap if self.groups else x
            total_w = max(viewport_w, content_w + margin)
            # Tant que la page entière tient sous le niveau des parties, aucun défilement vertical.
            required_h = page_bottom + margin
            total_h = viewport_h if required_h <= viewport_h + 1 else required_h

        self.canvas.configure(scrollregion=(0, 0, total_w, total_h))
        self._update_scrollbars(total_w, total_h)

        if self._dragging and not self._page_focus:
            if self._drag_kind == "group" and self._drag_group_target is not None:
                self._draw_group_drop_indicator(self._drag_group_target)
            elif self._drag_kind == "page" and self._drag_target_group_id is not None:
                self._draw_page_drop_indicator()

    def _update_scrollbars(self, total_w: float, total_h: float):
        view_w = max(1, self.canvas.winfo_width())
        view_h = max(1, self.canvas.winfo_height())
        need_h = total_w > view_w + 2
        need_v = total_h > view_h + 2

        if need_h != self._h_scroll_needed:
            self._h_scroll_needed = need_h
            if need_h:
                self.h_scroll.grid()
            else:
                self.h_scroll.grid_remove()
                self.canvas.xview_moveto(0)
        if need_v != self._v_scroll_needed:
            self._v_scroll_needed = need_v
            if need_v:
                self.v_scroll.grid()
            else:
                self.v_scroll.grid_remove()
                self.canvas.yview_moveto(0)

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

    def _group_at(self, event) -> str | None:
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        for group_id, (x1, y1, x2, y2) in self._group_hitboxes.items():
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                return group_id
        return None

    def _group_id_at_x(self, canvas_x: float) -> str:
        if not self._group_page_bounds:
            return self.DEFAULT_GROUP_ID
        nearest_id = self.DEFAULT_GROUP_ID
        nearest_distance = float("inf")
        for group_id, (x1, x2) in self._group_page_bounds.items():
            if x1 <= canvas_x <= x2:
                return group_id
            center = (x1 + x2) / 2.0
            distance = abs(canvas_x - center)
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_id = group_id
        return nearest_id

    def _on_hover_motion(self, event):
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
        if self._page_focus:
            index = self._index_at(event)
            if index is not None:
                self._selected_index = index
                self.render()
            return "break"

        group_id = self._group_at(event)
        index = self._index_at(event)
        self._drag_start_xy = (event.x, event.y)
        self._dragging = False
        self._drag_target_index = None
        self._drag_target_group_id = None
        self._drag_group_target = None

        if group_id is not None:
            self._selected_group_id = group_id
            self._selected_index = self._selected_index
            if group_id not in {self.START_GROUP_ID, self.END_GROUP_ID}:
                self._drag_kind = "group"
                self._drag_group_id = group_id
                self._drag_group_target = self._movable_group_ids().index(group_id) if group_id in self._movable_group_ids() else None
            else:
                self._drag_kind = None
                self._drag_group_id = None
            self.render()
            return "break"

        self._selected_group_id = None
        self._drag_kind = "page" if index is not None else None
        self._drag_start_index = index
        if index is not None:
            self._selected_index = index
            self._drag_target_index = index
            self._drag_target_group_id = self._item_group_id(self.items[index])
            self.render()
        return "break"

    def _movable_group_ids(self) -> list[str]:
        return [str(group.get("id", "")) for group in self.groups if str(group.get("id", "")) not in {self.START_GROUP_ID, self.END_GROUP_ID}]

    def _on_drag(self, event):
        if self._drag_kind is None or self._drag_start_xy is None:
            return "break"
        dx = abs(event.x - self._drag_start_xy[0])
        dy = abs(event.y - self._drag_start_xy[1])
        if not self._dragging and max(dx, dy) < 6:
            return "break"

        if self._drag_kind == "page" and self._drag_start_index is not None:
            if self._is_locked_page(self.items[self._drag_start_index]):
                self._dragging = False
                return "break"

        self._dragging = True
        canvas_x = self.canvas.canvasx(event.x)
        if self._drag_kind == "group":
            self._drag_group_target = self._target_movable_group_index(canvas_x)
        elif self._drag_kind == "page":
            self._drag_target_group_id = self._group_id_at_x(canvas_x)
            self._drag_target_index = self._target_index_from_x(canvas_x, self._drag_target_group_id)
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
        target = self._drag_target_index
        if group_id is None or target is None:
            return
        group_indexes = self._group_items(group_id)
        y1 = min((box[1] for box in self._page_hitboxes.values()), default=self.MARGIN + self.GROUP_H)
        y2 = max((box[3] for box in self._page_hitboxes.values()), default=y1 + 100)
        if target < len(self.items) and target in self._page_hitboxes:
            x = self._page_hitboxes[target][0] - 7
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
                grouped.sort(key=lambda item: (0 if self._is_cover(item) else 1))
            elif group_id == self.END_GROUP_ID:
                grouped.sort(key=lambda item: (1 if self._is_back_cover(item) else 0))
            ordered.extend(grouped)
        self.items = ordered

    def _on_release(self, _event):
        kind = self._drag_kind
        dragged = self._dragging
        start = self._drag_start_index
        target = self._drag_target_index
        target_group = self._drag_target_group_id
        drag_group_id = self._drag_group_id
        group_target = self._drag_group_target

        self._drag_kind = None
        self._drag_start_index = None
        self._drag_target_index = None
        self._drag_target_group_id = None
        self._drag_group_id = None
        self._drag_group_target = None
        self._drag_start_xy = None
        self._dragging = False

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

        if kind == "page" and start is not None and target is not None and target_group is not None:
            if start >= len(self.items) or self._is_locked_page(self.items[start]):
                self.render()
                return "break"
            item = self.items.pop(start)
            if target > start:
                target -= 1
            # Début et fin restent réservés à leurs pages structurelles.
            if target_group in {self.START_GROUP_ID, self.END_GROUP_ID}:
                target_group = self.DEFAULT_GROUP_ID
            item["plan_group"] = target_group
            target = max(0, min(len(self.items), target))
            self.items.insert(target, item)
            self._reorder_items_by_group_order()
            try:
                self._selected_index = self.items.index(item)
            except ValueError:
                self._selected_index = 0
            self._save_order()
            self.render()
            self.after_idle(self.center_selected)
            return "break"

        self.render()
        return "break"

    def _on_double_click(self, event):
        index = self._index_at(event)
        if index is not None:
            self._selected_index = index
            self.render()
            self.on_open_item(self.items[index], index)
        return "break"

    # ------------------------------------------------------------------
    # Souris
    # ------------------------------------------------------------------

    def _on_ctrl_mousewheel(self, event):
        if event.delta == 0:
            return "break"
        self.step_zoom(1 if event.delta > 0 else -1)
        return "break"

    def _on_shift_mousewheel(self, event):
        if self._h_scroll_needed:
            delta = -1 if event.delta > 0 else 1
            self.canvas.xview_scroll(delta * 4, "units")
        return "break"

    def _on_mousewheel(self, event):
        delta = -1 if event.delta > 0 else 1
        if self._v_scroll_needed:
            self.canvas.yview_scroll(delta * 4, "units")
        elif self._h_scroll_needed:
            self.canvas.xview_scroll(delta * 4, "units")
        return "break"
