from __future__ import annotations

from src.engine.graphics import Drawable

from .tool import Tool


class SelectTool(Tool):
    """
    Outil de sélection.

    Pour le moment, cet outil expose uniquement les opérations
    de sélection. Le hit-test sera ajouté lorsque le moteur
    de rendu pourra retrouver un objet sous le pointeur.
    """

    @property
    def name(self) -> str:
        return "Sélection"

    # ==========================================================
    # Sélection
    # ==========================================================

    def select(
        self,
        drawable: Drawable | None,
    ) -> None:

        if drawable is None:
            self.workspace.selection.clear()
        else:
            self.workspace.selection.select(drawable)

    def clear_selection(self) -> None:

        self.workspace.selection.clear()

    # ==========================================================
    # Évènements souris
    # ==========================================================

    def mouse_press(
        self,
        x: float,
        y: float,
        button: int,
    ) -> None:
        """
        Le hit-test sera ajouté ultérieurement.
        """
        ...

    def mouse_move(
        self,
        x: float,
        y: float,
    ) -> None:
        ...

    def mouse_release(
        self,
        x: float,
        y: float,
        button: int,
    ) -> None:
        ...

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def deselect(self) -> None:

        self.clear_selection()