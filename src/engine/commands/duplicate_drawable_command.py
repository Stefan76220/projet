from __future__ import annotations

from src.engine.commands.command import Command
from src.engine.graphics import Drawable, Layer


class DuplicateDrawableCommand(Command):
    """
    Duplique un objet graphique.

    Compatible avec le système Undo/Redo.
    """

    def __init__(
        self,
        layer: Layer,
        drawable: Drawable,
    ) -> None:

        super().__init__("Dupliquer un objet")

        self._layer = layer
        self._source = drawable
        self._copy: Drawable | None = None

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def layer(self) -> Layer:
        return self._layer

    @property
    def source(self) -> Drawable:
        return self._source

    @property
    def copy(self) -> Drawable | None:
        return self._copy

    # ==========================================================
    # Exécution
    # ==========================================================

    def execute(self) -> None:

        if self._copy is None:
            self._copy = self._source.clone()

        self._layer.add(self._copy)

    def undo(self) -> None:

        if self._copy is not None:
            self._layer.remove(self._copy)