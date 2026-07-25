from __future__ import annotations

from abc import ABC

from src.engine.foundation import Rect
from src.engine.graphics.drawable import Drawable


class Shape(Drawable, ABC):
    """
    Classe de base de toutes les formes géométriques.
    """

    def __init__(
        self,
        bounds: Rect,
        fill_color: str = "#FFFFFF",
        outline_color: str = "#000000",
        outline_width: int = 1,
    ):

        super().__init__(bounds)

        self._fill_color = fill_color
        self._outline_color = outline_color
        self._outline_width = outline_width

    @property
    def fill_color(self) -> str:
        return self._fill_color

    @property
    def outline_color(self) -> str:
        return self._outline_color

    @property
    def outline_width(self) -> int:
        return self._outline_width

    def set_fill_color(self, color: str) -> None:
        self._fill_color = color

    def set_outline_color(self, color: str) -> None:
        self._outline_color = color

    def set_outline_width(self, width: int) -> None:
        self._outline_width = max(0, width)