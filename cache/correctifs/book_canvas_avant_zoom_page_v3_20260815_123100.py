from __future__ import annotations

import tkinter as tk
from typing import Callable

from src.gui_v3 import theme


class BookCanvas(tk.Frame):
    """Canevas permanent V3 : un seul livre, du chemin de fer au détail."""

    MIN_ZOOM = 20
    MAX_ZOOM = 800
    BASE_PAGE_W = 420
    BASE_PAGE_H = 594
    BASE_GAP = 42
    MARGIN = 40

    def __init__(
        self,
        parent,
        *,
        on_open_item: Callable[[dict, int], None],
        on_change: Callable[[], None] | None = None,
    ):
        super().__init__(parent, bg=theme.PANEL)
        self.on_open_item = on_open_item
        self.on_change = on_change
        self.project = None
        self.items: list[dict] = []
        self._selected_index: int | None = None
        self._page_hitboxes: dict[int, tuple[float, float, float, float]] = {}
        self._drag_start_index: int | None = None
        self._drag_target_index: int | None = None
        self._drag_start_xy: tuple[int, int] | None = None
        self._dragging = False
        self._render_pending = None

        self.zoom_var = tk.IntVar(value=26)
        self.zoom_text_var = tk.StringVar(value="26 %")
        self.status_var = tk.StringVar(value="Structure à construire")

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
            text="Le livre — canevas permanent",
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

        self.v_scroll = tk.Scrollbar(
            viewer,
            orient="vertical",
            command=self.canvas.yview,
            bg=theme.PANEL_SOFT,
            troughcolor=theme.WINDOW_DEEP,
            activebackground=theme.ACCENT_DARK,
            bd=0,
            highlightthickness=0,
        )
        self.v_scroll.grid(row=0, column=1, sticky="ns")

        self.h_scroll = tk.Scrollbar(
            viewer,
            orient="horizontal",
            command=self.canvas.xview,
            bg=theme.PANEL_SOFT,
            troughcolor=theme.WINDOW_DEEP,
            activebackground=theme.ACCENT_DARK,
            bd=0,
            highlightthickness=0,
        )
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(
            xscrollcommand=self.h_scroll.set,
            yscrollcommand=self.v_scroll.set,
        )

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)
        self.canvas.bind("<Control-MouseWheel>", self._on_ctrl_mousewheel)
        self.canvas.bind("<Configure>", self._schedule_render)

    # ------------------------------------------------------------------
    # Projet / données
    # ------------------------------------------------------------------

    def set_project(self, project):
        self.project = project
        self.items = []
        if project is not None:
            try:
                data = project.load_mockup()
                raw = data.get("items", [])
                if isinstance(raw, list):
                    self.items = [dict(item) for item in raw if isinstance(item, dict)]
            except Exception:
                self.items = []
        self._selected_index = 0 if self.items else None
        self.render()
        if self.items:
            self.after_idle(self.fit_book)

    def _save_order(self):
        if self.project is None:
            return
        data = self.project.load_mockup()
        data["items"] = [dict(item) for item in self.items]
        self.project.save_mockup(data)
        if self.on_change is not None:
            self.on_change()

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

    def _on_scale(self, value):
        self.set_zoom(int(float(value)))

    def set_zoom(self, value: int, *, center_selected=True):
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

    def fit_book(self):
        if not self.items or not self.canvas.winfo_exists():
            return
        viewport_w = max(300, self.canvas.winfo_width() - 28)
        viewport_h = max(180, self.canvas.winfo_height() - 28)
        count = len(self.items)

        logical_w = count * self.BASE_PAGE_W + max(0, count - 1) * self.BASE_GAP
        logical_h = self.BASE_PAGE_H
        if logical_w <= 0 or logical_h <= 0:
            return

        zoom_x = int(viewport_w / logical_w * 100)
        zoom_y = int(viewport_h / logical_h * 100)
        value = max(self.MIN_ZOOM, min(100, zoom_x, zoom_y))
        self.set_zoom(value, center_selected=False)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

    def fit_selected(self):
        if self._selected_index is None:
            if self.items:
                self._selected_index = 0
            else:
                return
        viewport_w = max(300, self.canvas.winfo_width() - 60)
        viewport_h = max(180, self.canvas.winfo_height() - 60)
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
        self.canvas.xview_moveto(max(0.0, min(1.0, target_left / max(1.0, total_w - view_w))))
        self.canvas.yview_moveto(max(0.0, min(1.0, target_top / max(1.0, total_h - view_h))))

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

    def render(self):
        self._render_pending = None
        if not hasattr(self, "canvas"):
            return

        viewport_w = max(300, self.canvas.winfo_width())
        viewport_h = max(180, self.canvas.winfo_height())
        self.canvas.delete("all")
        self._page_hitboxes = {}

        self.zoom_text_var.set(f"{self.zoom} %")

        if not self.items:
            self.status_var.set("Aucune page — la structure apparaîtra ici")
            self.canvas.create_text(
                viewport_w / 2,
                viewport_h / 2 - 12,
                text="Le livre reste ici pendant tout le projet.",
                fill=theme.INK,
                font=(theme.FONT_TITLE, 13, "bold"),
            )
            self.canvas.create_text(
                viewport_w / 2,
                viewport_h / 2 + 18,
                text="Structure → gabarits → contenu réel → sortie",
                fill=theme.MUTED,
                font=(theme.FONT_UI, 9),
            )
            self.canvas.create_text(
                viewport_w / 2,
                viewport_h / 2 + 44,
                text="Ctrl + molette : zoom  •  molette : déplacement  •  glisser une page : réorganiser",
                fill=theme.MUTED_DARK,
                font=(theme.FONT_UI, 8),
            )
            self.canvas.configure(scrollregion=(0, 0, viewport_w, viewport_h))
            return

        self.status_var.set(
            f"{len(self.items)} page{'s' if len(self.items) > 1 else ''}  •  "
            f"page {self._selected_index + 1 if self._selected_index is not None else '—'} sélectionnée"
        )

        scale = self.zoom / 100.0
        page_w = max(16, self.BASE_PAGE_W * scale)
        page_h = max(22, self.BASE_PAGE_H * scale)
        gap = max(8, self.BASE_GAP * scale)
        margin = max(20, self.MARGIN * min(scale, 1.0))
        content_w = len(self.items) * page_w + max(0, len(self.items) - 1) * gap
        total_w = max(viewport_w, content_w + margin * 2)
        total_h = max(viewport_h, page_h + margin * 2)
        x = margin
        y = max(margin, (total_h - page_h) / 2.0)

        font_size = max(6, min(24, int(8 + self.zoom / 45)))
        number_size = max(6, min(22, int(7 + self.zoom / 55)))

        for index, item in enumerate(self.items):
            selected = index == self._selected_index
            fill = "#F0F1EE" if not selected else "#E1ECE8"
            outline = theme.ACCENT if selected else "#D5D7D3"

            # Ombre très discrète : améliore la lecture sans transformer B en décor.
            shadow = max(1, min(10, int(3 * scale)))
            self.canvas.create_rectangle(
                x + shadow,
                y + shadow,
                x + page_w + shadow,
                y + page_h + shadow,
                fill="#151B21",
                outline="",
            )
            self.canvas.create_rectangle(
                x,
                y,
                x + page_w,
                y + page_h,
                fill=fill,
                outline=outline,
                width=3 if selected else 1,
            )

            # Repère supérieur : futur état de page/gabarit/production.
            rail_h = max(2, min(9, int(5 * scale)))
            self.canvas.create_rectangle(
                x + max(2, 8 * scale),
                y + max(2, 8 * scale),
                x + page_w - max(2, 8 * scale),
                y + max(2, 8 * scale) + rail_h,
                fill=theme.ACCENT_DARK,
                outline="",
            )

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
            x += page_w + gap

        self.canvas.configure(scrollregion=(0, 0, total_w, total_h))

        if self._dragging and self._drag_target_index is not None:
            self._draw_drop_indicator(self._drag_target_index)

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

    def _on_press(self, event):
        index = self._index_at(event)
        self._drag_start_index = index
        self._drag_target_index = index
        self._drag_start_xy = (event.x, event.y)
        self._dragging = False
        if index is not None:
            self._selected_index = index
            self.render()
        return "break"

    def _on_drag(self, event):
        if self._drag_start_index is None or self._drag_start_xy is None:
            return "break"
        dx = abs(event.x - self._drag_start_xy[0])
        dy = abs(event.y - self._drag_start_xy[1])
        if not self._dragging and max(dx, dy) < 6:
            return "break"
        self._dragging = True
        self._drag_target_index = self._target_index_from_x(self.canvas.canvasx(event.x))
        self.render()
        return "break"

    def _target_index_from_x(self, canvas_x: float) -> int:
        """Renvoie un indice d'insertion de 0 à len(items)."""
        if not self._page_hitboxes:
            return 0
        for index in range(len(self.items)):
            x1, _y1, x2, _y2 = self._page_hitboxes[index]
            if canvas_x < (x1 + x2) / 2.0:
                return index
        return len(self.items)

    def _draw_drop_indicator(self, target_index: int):
        if not self._page_hitboxes:
            return
        if target_index >= len(self.items):
            last = len(self.items) - 1
            _x1, y1, x2, y2 = self._page_hitboxes[last]
            x = x2 + 7
        else:
            x1, y1, _x2, y2 = self._page_hitboxes[target_index]
            x = x1 - 7
        self.canvas.create_line(
            x, y1 - 8, x, y2 + 8,
            fill=theme.ACCENT,
            width=4,
            tags=("drop_indicator",),
        )

    def _on_release(self, _event):
        start = self._drag_start_index
        target = self._drag_target_index
        dragged = self._dragging
        self._drag_start_index = None
        self._drag_target_index = None
        self._drag_start_xy = None
        self._dragging = False

        if not dragged or start is None or target is None or start == target:
            self.render()
            return "break"

        item = self.items.pop(start)
        if target > start:
            target -= 1
        target = max(0, min(len(self.items), target))
        self.items.insert(target, item)
        self._selected_index = target
        self._save_order()
        self.render()
        self.after_idle(self.center_selected)
        return "break"

    def _on_double_click(self, event):
        index = self._index_at(event)
        if index is not None:
            self._selected_index = index
            self.render()
            self.on_open_item(self.items[index], index)
        return "break"

    # ------------------------------------------------------------------
    # Souris / accessibilité
    # ------------------------------------------------------------------

    def _on_ctrl_mousewheel(self, event):
        if event.delta == 0:
            return "break"
        direction = 1 if event.delta > 0 else -1
        self.step_zoom(direction)
        return "break"

    def _on_shift_mousewheel(self, event):
        delta = -1 if event.delta > 0 else 1
        self.canvas.xview_scroll(delta * 4, "units")
        return "break"

    def _on_mousewheel(self, event):
        delta = -1 if event.delta > 0 else 1
        region = self.canvas.cget("scrollregion")
        try:
            _x1, _y1, _x2, y2 = map(float, str(region).split())
        except Exception:
            y2 = 0
        if y2 > self.canvas.winfo_height() + 6:
            self.canvas.yview_scroll(delta * 4, "units")
        else:
            self.canvas.xview_scroll(delta * 4, "units")
        return "break"
