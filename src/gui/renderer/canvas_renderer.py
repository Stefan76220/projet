from __future__ import annotations

import tkinter as tk

from src.engine.renderer import Renderer
from src.engine.graphics import (
    Drawable,
    Ellipse,
    Page,
    Rectangle,
)


class CanvasRenderer(Renderer):
    """
    Renderer utilisant un tk.Canvas.
    """

    def __init__(self, canvas: tk.Canvas):

        self._canvas = canvas

    def begin_frame(self) -> None:

        self._canvas.delete("all")

    def end_frame(self) -> None:

        pass

    def draw_page(self, page: Page) -> None:

        # La page est déjà représentée par le Canvas lui-même.
        pass

    def draw_drawable(self, drawable: Drawable) -> None:

        drawable.draw(self)

    def draw_rectangle(self, rectangle: Rectangle) -> None:

        b = rectangle.bounds

        self._canvas.create_rectangle(
            b.left,
            b.top,
            b.right,
            b.bottom,
            fill=rectangle.fill_color,
            outline=rectangle.outline_color,
            width=rectangle.outline_width,
        )

    def draw_ellipse(self, ellipse: Ellipse) -> None:

        b = ellipse.bounds

        self._canvas.create_oval(
            b.left,
            b.top,
            b.right,
            b.bottom,
            fill=ellipse.fill_color,
            outline=ellipse.outline_color,
            width=ellipse.outline_width,
        )