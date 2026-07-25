from __future__ import annotations

from dataclasses import dataclass

from src.engine.foundation import Point, Size


@dataclass(slots=True)
class Transform:
    """
    Décrit la transformation géométrique d'un objet.
    """

    position: Point
    size: Size
    rotation: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0

    def move(self, dx: float, dy: float) -> None:
        self.position = self.position.move(dx, dy)

    def resize(self, width: float, height: float) -> None:
        self.size = Size(width, height)

    def rotate(self, angle: float) -> None:
        self.rotation = angle