from __future__ import annotations

from dataclasses import dataclass
from math import hypot


@dataclass(frozen=True, slots=True)
class Point:
    x: float
    y: float

    # ==========================================================
    # Géométrie
    # ==========================================================

    def move(
        self,
        dx: float,
        dy: float,
    ) -> "Point":

        return Point(
            self.x + dx,
            self.y + dy,
        )

    def distance_to(
        self,
        other: "Point",
    ) -> float:

        return hypot(
            other.x - self.x,
            other.y - self.y,
        )

    # ==========================================================
    # Opérateurs
    # ==========================================================

    def __add__(
        self,
        other: "Point",
    ) -> "Point":

        return Point(
            self.x + other.x,
            self.y + other.y,
        )

    def __sub__(
        self,
        other: "Point",
    ) -> "Point":

        return Point(
            self.x - other.x,
            self.y - other.y,
        )

    def __iter__(self):

        yield self.x
        yield self.y