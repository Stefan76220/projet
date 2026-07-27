from __future__ import annotations

from src.engine.commands.command import Command
from src.engine.graphics import Drawable, Layer


class DeleteDrawableCommand(Command):
    """
    Supprime un objet graphique d'un calque.

    Compatible avec le système Undo/Redo.
    """

    def __init__(
        self,
        layer: Layer,
        drawable: Drawable,
    ) -> None:

        super().__init__("Supprimer un objet")

        self._layer = layer
        self._drawable = drawable

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def layer(self) -> Layer:
        return self._layer

    @property
    def drawable(self) -> Drawable:
        return self._drawable

    # ==========================================================
    # Exécution
    # ==========================================================

    def execute(self) -> None:

        self._layer.remove(self._drawable)

    def undo(self) -> None:

        self._layer.add(self._drawable)