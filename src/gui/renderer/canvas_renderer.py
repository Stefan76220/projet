from __future__ import annotations

import tkinter as tk

from src.engine.camera import Viewport
from src.engine.document import Document
from src.engine.graphics import (
    Drawable,
    Ellipse,
    Page,
    Rectangle,
)
from src.engine.renderer import Renderer


class CanvasRenderer(Renderer):
    """
    Renderer utilisant un tk.Canvas.

    Toutes les coordonnées du moteur sont exprimées en
    millimètres. Le Viewport assure leur conversion en pixels.
    """

    def __init__(
        self,
        canvas: tk.Canvas,
        viewport: Viewport | None = None,
        origin_x: float = 0.0,
        origin_y: float = 0.0,
    ) -> None:

        self._canvas = canvas
        self._viewport = viewport

        self.origin_x = origin_x
        self.origin_y = origin_y

        self._clear_enabled = True

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def canvas(self) -> tk.Canvas:

        return self._canvas

    @property
    def viewport(self) -> Viewport | None:

        return self._viewport

    # ==========================================================
    # Configuration
    # ==========================================================

    def set_viewport(
        self,
        viewport: Viewport | None,
    ) -> None:

        self._viewport = viewport

    def set_origin(
        self,
        x: float,
        y: float,
    ) -> None:

        self.origin_x = x
        self.origin_y = y

    def enable_clear(
        self,
        value: bool = True,
    ) -> None:

        self._clear_enabled = value

    # ==========================================================
    # Cycle de rendu
    # ==========================================================

    def begin_frame(self) -> None:

        if self._clear_enabled:
            self._canvas.delete("all")

    def end_frame(self) -> None:

        pass

    # ==========================================================
    # Dessin
    # ==========================================================

    def draw_document(
        self,
        document: Document,
    ) -> None:

        self.begin_frame()

        for page in document:

            self.draw_page(page)

        self.end_frame()

    def draw_page(
        self,
        page: Page,
    ) -> None:

        for layer in page:

            for drawable in layer:

                self.draw_drawable(drawable)

    def draw_drawable(
        self,
        drawable: Drawable,
    ) -> None:

        drawable.draw(self)

    # ==========================================================
    # Conversions
    # ==========================================================

    def _x(
        self,
        value: float,
    ) -> float:

        if self._viewport is None:
            return value

        return (
            self.origin_x
            + self._viewport.mm_to_px(value)
        )

    def _y(
        self,
        value: float,
    ) -> float:

        if self._viewport is None:
            return value

        return (
            self.origin_y
            + self._viewport.mm_to_px(value)
        )

    # ==========================================================
    # Primitives
    # ==========================================================

    def draw_rectangle(
        self,
        rectangle: Rectangle,
    ) -> None:

        bounds = rectangle.bounds
        style = rectangle.style

        self._canvas.create_rectangle(
            self._x(bounds.left),
            self._y(bounds.top),
            self._x(bounds.right),
            self._y(bounds.bottom),
            fill=style.fill.color,
            outline=style.stroke.color,
            width=style.stroke.width,
        )

    def draw_ellipse(
        self,
        ellipse: Ellipse,
    ) -> None:

        bounds = ellipse.bounds
        style = ellipse.style

        self._canvas.create_oval(
            self._x(bounds.left),
            self._y(bounds.top),
            self._x(bounds.right),
            self._y(bounds.bottom),
            fill=style.fill.color,
            outline=style.stroke.color,
            width=style.stroke.width,
        )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"CanvasRenderer("
            f"origin=({self.origin_x}, {self.origin_y}), "
            f"viewport={self._viewport!r})"
        )