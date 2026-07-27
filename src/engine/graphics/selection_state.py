from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class SelectionState:
    """
    État de sélection d'un objet graphique.
    """

    # ==========================================================
    # États
    # ==========================================================

    selected: bool = False
    hovered: bool = False
    focused: bool = False

    handles_visible: bool = False
    editing: bool = False

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def clear(self) -> None:

        self.selected = False
        self.hovered = False
        self.focused = False
        self.handles_visible = False
        self.editing = False

    def begin_edit(self) -> None:

        self.editing = True

    def end_edit(self) -> None:

        self.editing = False

    def show_handles(self) -> None:

        self.handles_visible = True

    def hide_handles(self) -> None:

        self.handles_visible = False