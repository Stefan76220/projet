from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Point:
    x: float
    y: float

    def move(self, dx: float, dy: float) -> "Point":
        return Point(
            self.x + dx,
            self.y + dy,
        )

    def distance_to(self, other: "Point") -> float:
        dx = other.x - self.x
        dy = other.y - self.y
        return (dx * dx + dy * dy) ** 0.5

    def __add__(self, other: "Point") -> "Point":
        return Point(
            self.x + other.x,
            self.y + other.y,
        )

    def __sub__(self, other: "Point") -> "Point":
        return Point(
            self.x - other.x,
            self.y - other.y,
        )