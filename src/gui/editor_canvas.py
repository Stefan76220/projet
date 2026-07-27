from __future__ import annotations

from customtkinter import CTkCanvas

from src.engine.camera.viewport import Viewport
from src.engine.graphics.workspace import Workspace
from src.engine.page_format import A5
from src.gui.renderer.canvas_renderer import CanvasRenderer


class EditorCanvas(CTkCanvas):
    """
    Canvas principal de l'éditeur.
    """

    SHADOW_OFFSET = 8

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

        self.workspace = Workspace()

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

        self._bind_events()

    # ==========================================================
    # Initialisation
    # ==========================================================

    def _bind_events(self) -> None:

        self.bind("<Configure>", self._on_resize)

        self.bind("<Motion>", self._mouse_move)

        self.bind("<ButtonPress-2>", self._start_pan)
        self.bind("<B2-Motion>", self._pan)
        self.bind("<ButtonRelease-2>", self._stop_pan)

        self.bind("<MouseWheel>", self._on_mousewheel)

        self.focus_set()

        self.bind("<Control-0>", self._fit_page)

    # ==========================================================
    # Observateurs
    # ==========================================================

    def add_mouse_listener(
        self,
        callback,
    ) -> None:

        if callback not in self._mouse_listeners:
            self._mouse_listeners.append(callback)

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

    # ==========================================================
    # Dessin
    # ==========================================================

    def redraw(self) -> None:

        self.delete("all")

        page_width = self.viewport.mm_to_px(
            self.page_format.width_mm
        )

        page_height = self.viewport.mm_to_px(
            self.page_format.height_mm
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
            outline="#BBBBBB",
        )

    def _draw_workspace(self) -> None:

        for page in self.workspace:

            self.renderer.draw_page(page)

            for layer in page:

                for drawable in layer:

                    self.renderer.draw_drawable(
                        drawable,
                    )

    # ==========================================================
    # Evènements
    # ==========================================================

    def _on_resize(self, event) -> None:

        self.redraw()

    def _mouse_move(self, event) -> None:

        self.mouse_x_px = event.x
        self.mouse_y_px = event.y

        self.mouse_x_mm = self.viewport.px_to_mm(
            event.x - self.page_left,
        )

        self.mouse_y_mm = self.viewport.px_to_mm(
            event.y - self.page_top,
        )

        self._notify_mouse()

    def _start_pan(self, event) -> None:

        self._dragging = True

        self._last_x = event.x
        self._last_y = event.y

    def _pan(self, event) -> None:

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

    def _stop_pan(self, event) -> None:

        self._dragging = False

    def _on_mousewheel(self, event) -> None:

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
            - self.viewport.mm_to_px(old_x)
        )

        new_page_y = (
            event.y
            - self.viewport.mm_to_px(old_y)
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
            new_page_x - (canvas_width - page_width) / 2,
            new_page_y - (canvas_height - page_height) / 2,
        )

    def _fit_page(self, event=None) -> None:

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

        return "EditorCanvas()"