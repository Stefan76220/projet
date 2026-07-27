from __future__ import annotations

from .tool import Tool


class ZoomTool(Tool):
    """
    Outil de zoom de la vue.
    """

    @property
    def name(self) -> str:
        return "Zoom"

    # ==========================================================
    # Zoom
    # ==========================================================

    def zoom_in(
        self,
        factor: float = 1.10,
    ) -> None:

        self.workspace.camera.zoom *= factor

    def zoom_out(
        self,
        factor: float = 1.10,
    ) -> None:

        self.workspace.camera.zoom /= factor

    def reset_zoom(self) -> None:

        self.workspace.camera.zoom = 1.0

    # ==========================================================
    # Roulette souris
    # ==========================================================

    def mouse_wheel(
        self,
        delta: int,
        x: float,
        y: float,
    ) -> None:

        if delta > 0:
            self.zoom_in()
        elif delta < 0:
            self.zoom_out()