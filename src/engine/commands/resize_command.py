from __future__ import annotations

from src.engine.commands.command import Command
from src.engine.graphics import Drawable


class ResizeCommand(Command):
    """
    Redimensionne un objet graphique.

    Compatible avec le système Undo/Redo.
    """

    def __init__(
        self,
        drawable: Drawable,
        width: float,
        height: float,
    ) -> None:

        super().__init__("Redimensionner")

        self._drawable = drawable

        self._old_width = drawable.width
        self._old_height = drawable.height

        self._new_width = width
        self._new_height = height

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def drawable(self) -> Drawable:
        return self._drawable

    @property
    def old_size(self) -> tuple[float, float]:
        return self._old_width, self._old_height

    @property
    def new_size(self) -> tuple[float, float]:
        return self._new_width, self._new_height

    # ==========================================================
    # Exécution
    # ==========================================================

    def execute(self) -> None:

        self._drawable.resize(
            self._new_width,
            self._new_height,
        )

    def undo(self) -> None:

        self._drawable.resize(
            self._old_width,
            self._old_height,
        )