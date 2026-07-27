from __future__ import annotations

from abc import ABC

from src.engine.foundation import Rect

from .drawable import Drawable
from .styles import ShapeStyle


class Shape(Drawable, ABC):
    """
    Classe de base de toutes les formes géométriques.
    """

    def __init__(
        self,
        bounds: Rect,
        style: ShapeStyle | None = None,
    ) -> None:

        super().__init__(
            bounds=bounds,
            style=style or ShapeStyle(),
        )

    @property
    def style(self) -> ShapeStyle:
        return super().style

    def set_style(
        self,
        style: ShapeStyle,
    ) -> None:

        super().set_style(style)