from __future__ import annotations

from customtkinter import CTkCanvas

from src.engine.camera.viewport import Viewport
from src.engine.document import Document
from src.engine.foundation import Point, Rect, Size
from src.engine.graphics import Rectangle
from src.engine.page_format import A5
from src.gui.renderer.canvas_renderer import CanvasRenderer


class EditorCanvas(CTkCanvas):
    """
    Canvas principal de l'éditeur.
    """

    SHADOW_OFFSET = 8
    MIN_OBJECT_SIZE_MM = 1.0

    def __init__(
        self,
        master,
        **kwargs,
    ) -> None:

        super().__init__(
            master,
            highlightthickness=0,
            bg="#808080",
            **kwargs,
        )

        self.document = Document(
            "Page en cours",
        )

        self.document.create_page()

        self.workspace = self.document.workspace

        self.viewport = Viewport(
            self.workspace.camera,
        )

        self.viewport.add_listener(
            self.redraw,
        )

        self.renderer = CanvasRenderer(
            self,
            viewport=self.viewport,
        )

        self.page_format = A5

        self.page_left = 0.0
        self.page_top = 0.0

        self.mouse_x_px = 0.0
        self.mouse_y_px = 0.0

        self.mouse_x_mm = 0.0
        self.mouse_y_mm = 0.0

        self._mouse_listeners: list = []

        self._dragging = False
        self._last_x = 0
        self._last_y = 0

        self._active_tool = "selection"
        self._page_selected = False
        self._created_rectangles: list[Rect] = []

        self._drawing = False
        self._drawing_start_mm: Point | None = None
        self._preview_rectangle_id: int | None = None

        self._bind_events()

    # ==========================================================
    # Initialisation
    # ==========================================================

    def _bind_events(self) -> None:

        self.bind(
            "<Configure>",
            self._on_resize,
        )

        self.bind(
            "<Motion>",
            self._mouse_move,
        )

        self.bind(
            "<ButtonPress-1>",
            self._on_left_press,
        )

        self.bind(
            "<B1-Motion>",
            self._on_left_drag,
        )

        self.bind(
            "<ButtonRelease-1>",
            self._on_left_release,
        )

        self.bind(
            "<ButtonPress-2>",
            self._start_pan,
        )

        self.bind(
            "<B2-Motion>",
            self._pan,
        )

        self.bind(
            "<ButtonRelease-2>",
            self._stop_pan,
        )

        self.bind(
            "<MouseWheel>",
            self._on_mousewheel,
        )

        self.focus_set()

        self.bind(
            "<Control-0>",
            self._fit_page,
        )

        self.bind(
            "<Key-r>",
            self._activate_rectangle_tool,
        )

        self.bind(
            "<Key-R>",
            self._activate_rectangle_tool,
        )

        self.bind(
            "<Escape>",
            self._activate_selection_tool,
        )

    # ==========================================================
    # Observateurs
    # ==========================================================

    def add_mouse_listener(
        self,
        callback,
    ) -> None:

        if callback not in self._mouse_listeners:
            self._mouse_listeners.append(
                callback,
            )

    def _notify_mouse(self) -> None:

        for callback in self._mouse_listeners:
            callback()

    # ==========================================================
    # Configuration
    # ==========================================================

    def set_page_format(
        self,
        page_format,
    ) -> None:

        self.page_format = page_format
        self.redraw()

    def set_tool(
        self,
        tool_name: str,
    ) -> None:

        normalized_name = str(tool_name).strip().lower()

        if normalized_name not in {
            "selection",
            "rectangle",
        }:
            normalized_name = "selection"

        self._active_tool = normalized_name
        self._cancel_drawing()

        cursor = (
            "crosshair"
            if self._active_tool == "rectangle"
            else "arrow"
        )

        self.configure(
            cursor=cursor,
        )

    @property
    def active_tool(self) -> str:
        return self._active_tool

    # ==========================================================
    # Dessin
    # ==========================================================

    def redraw(self) -> None:

        self.delete(
            "all",
        )

        page_width = self.viewport.mm_to_px(
            self.page_format.width_mm,
        )

        page_height = self.viewport.mm_to_px(
            self.page_format.height_mm,
        )

        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()

        self.page_left = (
            (canvas_width - page_width) / 2
            + self.viewport.offset_x_px
        )

        self.page_top = (
            (canvas_height - page_height) / 2
            + self.viewport.offset_y_px
        )

        self.renderer.set_origin(
            self.page_left,
            self.page_top,
        )

        self._draw_shadow(
            page_width,
            page_height,
        )

        self._draw_page(
            page_width,
            page_height,
        )

        self._draw_workspace()
        self._draw_created_rectangles()

    def _draw_shadow(
        self,
        width: float,
        height: float,
    ) -> None:

        self.create_rectangle(
            self.page_left + self.SHADOW_OFFSET,
            self.page_top + self.SHADOW_OFFSET,
            self.page_left + width + self.SHADOW_OFFSET,
            self.page_top + height + self.SHADOW_OFFSET,
            fill="#666666",
            width=0,
        )

    def _draw_page(
        self,
        width: float,
        height: float,
    ) -> None:

        self.create_rectangle(
            self.page_left,
            self.page_top,
            self.page_left + width,
            self.page_top + height,
            fill="white",
            outline="#3874CB" if self._page_selected else "#BBBBBB",
            width=2 if self._page_selected else 1,
        )

    def _draw_workspace(self) -> None:

        for page in self.workspace.document:

            self.renderer.draw_page(
                page,
            )

            for layer in page:

                for drawable in layer:

                    self.renderer.draw_drawable(
                        drawable,
                    )

    def _draw_created_rectangles(self) -> None:

        for bounds in self._created_rectangles:

            self.create_rectangle(
                self.page_left + self.viewport.mm_to_px(bounds.left),
                self.page_top + self.viewport.mm_to_px(bounds.top),
                self.page_left + self.viewport.mm_to_px(bounds.right),
                self.page_top + self.viewport.mm_to_px(bounds.bottom),
                fill="#F4F4F4",
                outline="#222222",
                width=2,
            )

    # ==========================================================
    # Outils graphiques
    # ==========================================================

    def _activate_rectangle_tool(
        self,
        event=None,
    ) -> str:

        self.set_tool(
            "rectangle",
        )

        return "break"

    def _activate_selection_tool(
        self,
        event=None,
    ) -> str:

        self.set_tool(
            "selection",
        )

        return "break"

    def _on_left_press(
        self,
        event,
    ) -> None:

        self.focus_set()

        start = self._event_to_page_mm(
            event,
        )

        self._page_selected = start is not None

        if self._active_tool != "rectangle":
            self.redraw()
            return

        if start is None:
            return

        self._drawing = True
        self._drawing_start_mm = start

        self._preview_rectangle_id = self.create_rectangle(
            event.x,
            event.y,
            event.x,
            event.y,
            outline="#3874CB",
            width=2,
            dash=(5, 3),
        )

    def _on_left_drag(
        self,
        event,
    ) -> None:

        if not self._drawing:
            return

        if self._preview_rectangle_id is None:
            return

        if self._drawing_start_mm is None:
            return

        current = self._event_to_page_mm(
            event,
            clamp_to_page=True,
        )

        if current is None:
            return

        start_x = (
            self.page_left
            + self.viewport.mm_to_px(
                self._drawing_start_mm.x,
            )
        )

        start_y = (
            self.page_top
            + self.viewport.mm_to_px(
                self._drawing_start_mm.y,
            )
        )

        current_x = (
            self.page_left
            + self.viewport.mm_to_px(
                current.x,
            )
        )

        current_y = (
            self.page_top
            + self.viewport.mm_to_px(
                current.y,
            )
        )

        self.coords(
            self._preview_rectangle_id,
            start_x,
            start_y,
            current_x,
            current_y,
        )

    def _on_left_release(
        self,
        event,
    ) -> None:

        if not self._drawing:
            return

        start = self._drawing_start_mm

        current = self._event_to_page_mm(
            event,
            clamp_to_page=True,
        )

        self._cancel_preview()

        if start is None or current is None:
            self._finish_drawing()
            return

        left = min(
            start.x,
            current.x,
        )

        top = min(
            start.y,
            current.y,
        )

        width = abs(
            current.x - start.x,
        )

        height = abs(
            current.y - start.y,
        )

        if (
            width < self.MIN_OBJECT_SIZE_MM
            or height < self.MIN_OBJECT_SIZE_MM
        ):
            self._finish_drawing()
            return

        bounds = Rect(
            Point(
                left,
                top,
            ),
            Size(
                width,
                height,
            ),
        )

        self._created_rectangles.append(
            bounds,
        )

        self._finish_drawing()
        self.redraw()

    def _event_to_page_mm(
        self,
        event,
        clamp_to_page: bool = False,
    ) -> Point | None:

        x_mm = self.viewport.px_to_mm(
            event.x - self.page_left,
        )

        y_mm = self.viewport.px_to_mm(
            event.y - self.page_top,
        )

        if clamp_to_page:
            x_mm = min(
                max(
                    x_mm,
                    0.0,
                ),
                self.page_format.width_mm,
            )

            y_mm = min(
                max(
                    y_mm,
                    0.0,
                ),
                self.page_format.height_mm,
            )

        elif not (
            0.0 <= x_mm <= self.page_format.width_mm
            and 0.0 <= y_mm <= self.page_format.height_mm
        ):
            return None

        return Point(
            x_mm,
            y_mm,
        )

    def _cancel_preview(self) -> None:

        if self._preview_rectangle_id is not None:

            self.delete(
                self._preview_rectangle_id,
            )

            self._preview_rectangle_id = None

    def _finish_drawing(self) -> None:

        self._drawing = False
        self._drawing_start_mm = None

    def _cancel_drawing(self) -> None:

        self._cancel_preview()
        self._finish_drawing()

    # ==========================================================
    # Évènements
    # ==========================================================

    def _on_resize(
        self,
        event,
    ) -> None:

        self.redraw()

    def _mouse_move(
        self,
        event,
    ) -> None:

        self.mouse_x_px = event.x
        self.mouse_y_px = event.y

        self.mouse_x_mm = self.viewport.px_to_mm(
            event.x - self.page_left,
        )

        self.mouse_y_mm = self.viewport.px_to_mm(
            event.y - self.page_top,
        )

        self._notify_mouse()

    def _start_pan(
        self,
        event,
    ) -> None:

        self._dragging = True

        self._last_x = event.x
        self._last_y = event.y

    def _pan(
        self,
        event,
    ) -> None:

        if not self._dragging:
            return

        dx = event.x - self._last_x
        dy = event.y - self._last_y

        self.viewport.move(
            dx,
            dy,
        )

        self._last_x = event.x
        self._last_y = event.y

    def _stop_pan(
        self,
        event,
    ) -> None:

        self._dragging = False

    def _on_mousewheel(
        self,
        event,
    ) -> None:

        factor = 1.1 if event.delta > 0 else 0.9

        old_x = self.viewport.px_to_mm(
            event.x - self.page_left,
        )

        old_y = self.viewport.px_to_mm(
            event.y - self.page_top,
        )

        self.viewport.zoom_at(
            factor,
        )

        new_page_x = (
            event.x
            - self.viewport.mm_to_px(
                old_x,
            )
        )

        new_page_y = (
            event.y
            - self.viewport.mm_to_px(
                old_y,
            )
        )

        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()

        page_width = self.viewport.mm_to_px(
            self.page_format.width_mm,
        )

        page_height = self.viewport.mm_to_px(
            self.page_format.height_mm,
        )

        self.viewport.set_offset(
            new_page_x
            - (canvas_width - page_width) / 2,
            new_page_y
            - (canvas_height - page_height) / 2,
        )

    def _fit_page(
        self,
        event=None,
    ) -> None:

        width = self.winfo_width()
        height = self.winfo_height()

        if width <= 0 or height <= 0:
            return

        base = self.viewport.pixels_per_mm

        zoom_x = (
            width * 0.85
        ) / (
            self.page_format.width_mm * base
        )

        zoom_y = (
            height * 0.85
        ) / (
            self.page_format.height_mm * base
        )

        self.viewport.set_zoom(
            min(
                zoom_x,
                zoom_y,
            )
        )

        self.viewport.set_offset(
            0,
            0,
        )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            "EditorCanvas("
            f"tool={self._active_tool!r})"
        )