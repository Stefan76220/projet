from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Camera:
    """
    Représente la vue de l'utilisateur sur le document.

    La caméra ne connaît ni le document, ni le renderer,
    ni le viewport. Elle gère uniquement la position et le
    niveau de zoom.
    """

    MIN_ZOOM: float = 0.10
    MAX_ZOOM: float = 8.00

    x: float = 0.0
    y: float = 0.0
    zoom: float = 1.0

    # ==========================================================
    # Position
    # ==========================================================

    @property
    def position(self) -> tuple[float, float]:

        return self.x, self.y

    def move(
        self,
        dx: float,
        dy: float,
    ) -> None:

        self.x += dx
        self.y += dy

    def set_position(
        self,
        x: float,
        y: float,
    ) -> None:

        self.x = x
        self.y = y

    # ==========================================================
    # Zoom
    # ==========================================================

    def set_zoom(
        self,
        zoom: float,
    ) -> None:

        self.zoom = max(
            self.MIN_ZOOM,
            min(self.MAX_ZOOM, zoom),
        )

    def zoom_in(
        self,
        factor: float = 1.10,
    ) -> None:

        self.set_zoom(self.zoom * factor)

    def zoom_out(
        self,
        factor: float = 1.10,
    ) -> None:

        self.set_zoom(self.zoom / factor)

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def copy(self) -> "Camera":

        return Camera(
            x=self.x,
            y=self.y,
            zoom=self.zoom,
        )

    def reset(self) -> None:

        self.x = 0.0
        self.y = 0.0
        self.zoom = 1.0

    def __repr__(self) -> str:

        return (
            f"Camera(x={self.x}, "
            f"y={self.y}, "
            f"zoom={self.zoom})"
        )