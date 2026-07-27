from __future__ import annotations

from src.engine.commands.command import Command
from src.engine.graphics import Drawable


class MoveCommand(Command):
    """
    Déplace un objet graphique.

    Compatible avec le système Undo/Redo.
    """

    def __init__(
        self,
        drawable: Drawable,
        dx: float,
        dy: float,
    ) -> None:

        super().__init__("Déplacer")

        self._drawable = drawable
        self._dx = dx
        self._dy = dy

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def drawable(self) -> Drawable:
        return self._drawable

    @property
    def delta(self) -> tuple[float, float]:
        return self._dx, self._dy

    # ==========================================================
    # Exécution
    # ==========================================================

    def execute(self) -> None:

        self._drawable.move(
            self._dx,
            self._dy,
        )

    def undo(self) -> None:

        self._drawable.move(
            -self._dx,
            -self._dy,
        )