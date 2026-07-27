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

    # ==========================================================
    # Position
    # ==========================================================

    def move(
        self,
        dx: float,
        dy: float,
    ) -> None:

        self.position = self.position.move(dx, dy)

    def set_position(
        self,
        position: Point,
    ) -> None:

        self.position = position

    # ==========================================================
    # Taille
    # ==========================================================

    def resize(
        self,
        width: float,
        height: float,
    ) -> None:

        self.size = Size(width, height)

    def set_size(
        self,
        size: Size,
    ) -> None:

        self.size = size

    # ==========================================================
    # Rotation
    # ==========================================================

    def rotate(
        self,
        angle: float,
    ) -> None:

        self.rotation = angle

    def reset_rotation(self) -> None:

        self.rotation = 0.0

    # ==========================================================
    # Échelle
    # ==========================================================

    def set_scale(
        self,
        scale_x: float,
        scale_y: float,
    ) -> None:

        self.scale_x = scale_x
        self.scale_y = scale_y

    def reset_scale(self) -> None:

        self.scale_x = 1.0
        self.scale_y = 1.0