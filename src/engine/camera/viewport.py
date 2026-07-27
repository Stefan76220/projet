from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from src.engine.camera.camera import Camera


@dataclass(slots=True)
class Viewport:
    """
    Interface entre la caméra et le moteur graphique.

    Les coordonnées document sont exprimées en millimètres.
    Les coordonnées écran sont exprimées en pixels.
    """

    camera: Camera = field(default_factory=Camera)

    pixels_per_mm: float = 3.7795275591

    _listeners: list[Callable[[], None]] = field(
        default_factory=list,
        init=False,
        repr=False,
    )

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def zoom(self) -> float:
        return self.camera.zoom

    @zoom.setter
    def zoom(
        self,
        value: float,
    ) -> None:

        self.set_zoom(value)

    @property
    def offset_x_px(self) -> float:
        return self.camera.x

    @offset_x_px.setter
    def offset_x_px(
        self,
        value: float,
    ) -> None:

        self.camera.set_position(
            value,
            self.camera.y,
        )

    @property
    def offset_y_px(self) -> float:
        return self.camera.y

    @offset_y_px.setter
    def offset_y_px(
        self,
        value: float,
    ) -> None:

        self.camera.set_position(
            self.camera.x,
            value,
        )

    # ==========================================================
    # Observateurs
    # ==========================================================

    def add_listener(
        self,
        callback: Callable[[], None],
    ) -> None:

        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(
        self,
        callback: Callable[[], None],
    ) -> None:

        if callback in self._listeners:
            self._listeners.remove(callback)

    def clear_listeners(self) -> None:

        self._listeners.clear()

    def notify(self) -> None:

        for callback in tuple(self._listeners):
            callback()

    # ==========================================================
    # Conversions
    # ==========================================================

    def mm_to_px(
        self,
        value_mm: float,
    ) -> float:

        return (
            value_mm
            * self.pixels_per_mm
            * self.camera.zoom
        )

    def px_to_mm(
        self,
        value_px: float,
    ) -> float:

        return value_px / (
            self.pixels_per_mm
            * self.camera.zoom
        )

    # ==========================================================
    # Transformations
    # ==========================================================

    def document_to_screen(
        self,
        x_mm: float,
        y_mm: float,
    ) -> tuple[float, float]:

        return (
            self.mm_to_px(x_mm) + self.camera.x,
            self.mm_to_px(y_mm) + self.camera.y,
        )

    def screen_to_document(
        self,
        x_px: float,
        y_px: float,
    ) -> tuple[float, float]:

        return (
            self.px_to_mm(x_px - self.camera.x),
            self.px_to_mm(y_px - self.camera.y),
        )

    # ==========================================================
    # Déplacements
    # ==========================================================

    def move(
        self,
        dx_px: float,
        dy_px: float,
    ) -> None:

        self.camera.move(dx_px, dy_px)
        self.notify()

    def set_offset(
        self,
        x_px: float,
        y_px: float,
    ) -> None:

        self.camera.set_position(
            x_px,
            y_px,
        )
        self.notify()

    # ==========================================================
    # Zoom
    # ==========================================================

    def set_zoom(
        self,
        zoom: float,
    ) -> None:

        previous = self.camera.zoom

        self.camera.set_zoom(zoom)

        if self.camera.zoom != previous:
            self.notify()

    def zoom_in(
        self,
        factor: float = 1.10,
    ) -> None:

        self.set_zoom(self.camera.zoom * factor)

    def zoom_out(
        self,
        factor: float = 1.10,
    ) -> None:

        self.set_zoom(self.camera.zoom / factor)

    def zoom_at(
        self,
        factor: float,
        center_x_px: float = 0.0,
        center_y_px: float = 0.0,
    ) -> None:
        """
        Le recentrage autour du pointeur est géré par EditorCanvas.
        """

        self.set_zoom(self.camera.zoom * factor)

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def copy(self) -> "Viewport":

        return Viewport(
            camera=self.camera.copy(),
            pixels_per_mm=self.pixels_per_mm,
        )

    def reset(self) -> None:

        self.camera.reset()
        self.notify()

    def __repr__(self) -> str:

        return (
            f"Viewport("
            f"zoom={self.zoom}, "
            f"offset=({self.offset_x_px}, {self.offset_y_px}))"
        )