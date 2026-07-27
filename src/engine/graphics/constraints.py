from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Constraints:
    """
    Contraintes appliquées à un objet graphique.
    """

    # ==========================================================
    # Manipulation
    # ==========================================================

    movable: bool = True
    resizable: bool = True
    rotatable: bool = True

    # ==========================================================
    # Interaction
    # ==========================================================

    selectable: bool = True
    editable: bool = True
    deletable: bool = True

    # ==========================================================
    # Affichage
    # ==========================================================

    visible: bool = True
    locked: bool = False

    # ==========================================================
    # Géométrie
    # ==========================================================

    keep_aspect_ratio: bool = False
    clip_to_page: bool = False

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def lock(self) -> None:

        self.locked = True

    def unlock(self) -> None:

        self.locked = False

    def hide(self) -> None:

        self.visible = False

    def show(self) -> None:

        self.visible = True

    def enable_editing(self) -> None:

        self.editable = True

    def disable_editing(self) -> None:

        self.editable = False

    def enable_selection(self) -> None:

        self.selectable = True

    def disable_selection(self) -> None:

        self.selectable = False