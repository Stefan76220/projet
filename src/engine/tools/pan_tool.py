from __future__ import annotations

from .tool import Tool


class PanTool(Tool):
    """
    Outil de déplacement de la vue.
    """

    def __init__(self, workspace) -> None:

        super().__init__(workspace)

        self._dragging = False
        self._last_x = 0.0
        self._last_y = 0.0

    @property
    def name(self) -> str:
        return "Déplacement"

    # ==========================================================
    # Souris
    # ==========================================================

    def mouse_press(
        self,
        x: float,
        y: float,
        button: int,
    ) -> None:

        if button != 2:
            return

        self._dragging = True
        self._last_x = x
        self._last_y = y

    def mouse_move(
        self,
        x: float,
        y: float,
    ) -> None:

        if not self._dragging:
            return

        dx = x - self._last_x
        dy = y - self._last_y

        self.workspace.camera.move(-dx, -dy)

        self._last_x = x
        self._last_y = y

    def mouse_release(
        self,
        x: float,
        y: float,
        button: int,
    ) -> None:

        if button == 2:
            self._dragging = False

    # ==========================================================
    # Utilitaires
    # ==========================================================

    @property
    def dragging(self) -> bool:

        return self._dragging