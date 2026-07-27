from __future__ import annotations

from src.engine.foundation import Rect
from .shape import Shape
from src.engine.graphics.styles import ShapeStyle


class Ellipse(Shape):
    """
    Ellipse graphique.
    """

    def __init__(
        self,
        bounds: Rect,
        style: ShapeStyle | None = None,
    ) -> None:

        super().__init__(
            bounds=bounds,
            style=style,
        )

    # ==========================================================
    # Duplication
    # ==========================================================

    def clone(self) -> "Ellipse":

        return Ellipse(
            bounds=self.bounds,
            style=self.style.copy(),
        )

    # ==========================================================
    # Rendu
    # ==========================================================

    def draw(
        self,
        renderer,
    ) -> None:

        renderer.draw_ellipse(self)