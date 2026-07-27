from __future__ import annotations

from dataclasses import dataclass

from .point import Point
from .size import Size


@dataclass(frozen=True, slots=True)
class Rect:
    origin: Point
    size: Size

    # ==========================================================
    # Coordonnées
    # ==========================================================

    @property
    def left(self) -> float:
        return self.origin.x

    @property
    def top(self) -> float:
        return self.origin.y

    @property
    def right(self) -> float:
        return self.origin.x + self.size.width

    @property
    def bottom(self) -> float:
        return self.origin.y + self.size.height

    @property
    def width(self) -> float:
        return self.size.width

    @property
    def height(self) -> float:
        return self.size.height

    @property
    def center(self) -> Point:
        return Point(
            self.left + self.width / 2,
            self.top + self.height / 2,
        )

    # ==========================================================
    # Géométrie
    # ==========================================================

    def contains(
        self,
        point: Point,
    ) -> bool:

        return (
            self.left <= point.x <= self.right
            and self.top <= point.y <= self.bottom
        )

    def intersects(
        self,
        other: "Rect",
    ) -> bool:

        return not (
            self.right < other.left
            or self.left > other.right
            or self.bottom < other.top
            or self.top > other.bottom
        )

    def move(
        self,
        dx: float,
        dy: float,
    ) -> "Rect":

        return Rect(
            self.origin.move(dx, dy),
            self.size,
        )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __iter__(self):

        yield self.origin
        yield self.size