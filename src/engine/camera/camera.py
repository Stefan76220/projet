from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Camera:
    """
    Représente la vue de l'utilisateur sur le document.

    La caméra ne dessine rien.
    Elle mémorise uniquement la position de la vue
    et le niveau de zoom.
    """

    x: float = 0.0
    y: float = 0.0

    zoom: float = 1.0

    MIN_ZOOM = 0.10
    MAX_ZOOM = 8.00

    # ---------------------------------------------------------

    def move(self, dx: float, dy: float) -> None:
        """Déplace la caméra relativement à sa position actuelle."""

        self.x += dx
        self.y += dy

    # ---------------------------------------------------------

    def set_position(self, x: float, y: float) -> None:
        """Positionne la caméra à des coordonnées absolues."""

        self.x = x
        self.y = y

    # ---------------------------------------------------------

    def set_zoom(self, zoom: float) -> None:
        """Définit le niveau de zoom en respectant les limites."""

        self.zoom = max(
            self.MIN_ZOOM,
            min(self.MAX_ZOOM, zoom)
        )

    # ---------------------------------------------------------

    def zoom_in(self, factor: float = 1.10) -> None:
        """Augmente le niveau de zoom."""

        self.set_zoom(self.zoom * factor)

    # ---------------------------------------------------------

    def zoom_out(self, factor: float = 1.10) -> None:
        """Diminue le niveau de zoom."""

        self.set_zoom(self.zoom / factor)

    # ---------------------------------------------------------

    def reset(self) -> None:
        """Réinitialise complètement la caméra."""

        self.set_position(0.0, 0.0)
        self.zoom = 1.0