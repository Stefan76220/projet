from customtkinter import CTkCanvas

from src.engine.page_format import A5
from src.engine.camera.viewport import Viewport


class EditorCanvas(CTkCanvas):

    SHADOW_OFFSET = 8

    def __init__(self, master, **kwargs):

        super().__init__(
            master,
            highlightthickness=0,
            bg="#808080",
            **kwargs,
        )

        self.viewport = Viewport()
        self.viewport.add_listener(self.redraw)

        # Document affiché
        self.page_format = A5

        # Position de la souris dans le document (mm)
        self.mouse_x_mm = 0.0
        self.mouse_y_mm = 0.0

        # Dernière position de la souris sur le canevas (pixels)
        self.mouse_x_px = 0.0
        self.mouse_y_px = 0.0

        # Composants abonnés aux déplacements de la souris
        self._mouse_listeners = []

        self.bind("<Configure>", self._on_resize)
        self.bind("<Motion>", self._mouse_move)

        self._dragging = False
        self._last_x = 0
        self._last_y = 0

        self.bind("<ButtonPress-2>", self._start_pan)
        self.bind("<B2-Motion>", self._pan)
        self.bind("<ButtonRelease-2>", self._stop_pan)

        self.bind("<MouseWheel>", self._on_mousewheel)

        self.focus_set()
        self.bind("<Control-0>", self._fit_page)

    # ------------------------------------------------------------------

    def add_mouse_listener(self, callback):

        if callback not in self._mouse_listeners:
            self._mouse_listeners.append(callback)

    # ------------------------------------------------------------------

    def _notify_mouse(self):

        for callback in self._mouse_listeners:
            callback()

    # ------------------------------------------------------------------

    def set_page_format(self, page_format):

        self.page_format = page_format
        self.redraw()

    # ------------------------------------------------------------------

    def _on_resize(self, event):

        self.redraw()

    # ------------------------------------------------------------------

    def redraw(self):

        self.delete("all")

        width_px = self.viewport.mm_to_px(self.page_format.width_mm)
        height_px = self.viewport.mm_to_px(self.page_format.height_mm)

        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()

        x = (canvas_width - width_px) / 2 + self.viewport.offset_x_px
        y = (canvas_height - height_px) / 2 + self.viewport.offset_y_px

        self.page_left = x
        self.page_top = y

        self.create_rectangle(
            x + self.SHADOW_OFFSET,
            y + self.SHADOW_OFFSET,
            x + width_px + self.SHADOW_OFFSET,
            y + height_px + self.SHADOW_OFFSET,
            fill="#666666",
            width=0,
        )

        self.create_rectangle(
            x,
            y,
            x + width_px,
            y + height_px,
            fill="white",
            outline="#BBBBBB",
        )

    # ------------------------------------------------------------------

    def _mouse_move(self, event):

        self.mouse_x_px = event.x
        self.mouse_y_px = event.y

        self.mouse_x_mm = self.viewport.px_to_mm(event.x - self.page_left)
        self.mouse_y_mm = self.viewport.px_to_mm(event.y - self.page_top)

        self._notify_mouse()

    # ------------------------------------------------------------------

    def _start_pan(self, event):

        self._dragging = True
        self._last_x = event.x
        self._last_y = event.y

    # ------------------------------------------------------------------

    def _pan(self, event):

        if not self._dragging:
            return

        dx = event.x - self._last_x
        dy = event.y - self._last_y

        self.viewport.move(dx, dy)

        self._last_x = event.x
        self._last_y = event.y

    # ------------------------------------------------------------------

    def _stop_pan(self, event):

        self._dragging = False

    # ------------------------------------------------------------------

    def _on_mousewheel(self, event):

        factor = 1.1 if event.delta > 0 else 0.9

        self.viewport.zoom_at(
            factor,
            self.mouse_x_px,
            self.mouse_y_px,
        )

    # ------------------------------------------------------------------

    def _fit_page(self, event=None):

        w = self.winfo_width()
        h = self.winfo_height()

        if w <= 0 or h <= 0:
            return

        zoom_x = (w * 0.85) / self.viewport.mm_to_px(self.page_format.width_mm)
        zoom_y = (h * 0.85) / self.viewport.mm_to_px(self.page_format.height_mm)

        self.viewport.zoom *= min(zoom_x, zoom_y)

        self.viewport.offset_x_px = 0
        self.viewport.offset_y_px = 0

        self.viewport.notify()