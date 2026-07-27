from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class InteractionState:
    """
    État d'interaction d'un objet graphique.
    """

    # ==========================================================
    # États
    # ==========================================================

    moving: bool = False
    resizing: bool = False
    rotating: bool = False
    editing: bool = False
    dragging: bool = False

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def clear(self) -> None:

        self.moving = False
        self.resizing = False
        self.rotating = False
        self.editing = False
        self.dragging = False

    def begin_move(self) -> None:

        self.moving = True

    def end_move(self) -> None:

        self.moving = False

    def begin_resize(self) -> None:

        self.resizing = True

    def end_resize(self) -> None:

        self.resizing = False

    def begin_rotation(self) -> None:

        self.rotating = True

    def end_rotation(self) -> None:

        self.rotating = False

    def begin_drag(self) -> None:

        self.dragging = True

    def end_drag(self) -> None:

        self.dragging = False

    def begin_edit(self) -> None:

        self.editing = True

    def end_edit(self) -> None:

        self.editing = False