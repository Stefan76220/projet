from __future__ import annotations

from src.engine.foundation import Rect
from src.engine.graphics.shape import Shape


class Rectangle(Shape):
    """
    Rectangle graphique.
    """

    def __init__(
        self,
        bounds: Rect,
        fill_color: str = "#FFFFFF",
        outline_color: str = "#000000",
        outline_width: int = 1,
    ):

        super().__init__(
            bounds=bounds,
            fill_color=fill_color,
            outline_color=outline_color,
            outline_width=outline_width,
        )

    def draw(self, renderer) -> None:
        renderer.draw_rectangle(self)