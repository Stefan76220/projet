from __future__ import annotations

from typing import Optional

from src.engine.events import (
    EventDispatcher,
    SelectionChangedEvent,
)
from src.engine.graphics import Drawable


class SelectionManager:
    """
    Gère la sélection courante du moteur graphique.
    """

    def __init__(self) -> None:

        self._selected: Optional[Drawable] = None
        self._dispatcher = EventDispatcher()

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def selected(self) -> Optional[Drawable]:

        return self._selected

    @property
    def dispatcher(self) -> EventDispatcher:

        return self._dispatcher

    @property
    def has_selection(self) -> bool:

        return self._selected is not None

    # ==========================================================
    # Gestion de la sélection
    # ==========================================================

    def select(
        self,
        drawable: Drawable,
    ) -> None:

        if drawable is self._selected:
            return

        self.clear(dispatch=False)

        self._selected = drawable
        drawable.select()

        self._notify()

    def clear(
        self,
        dispatch: bool = True,
    ) -> None:

        if self._selected is not None:
            self._selected.unselect()

        self._selected = None

        if dispatch:
            self._notify()

    def toggle(
        self,
        drawable: Drawable,
    ) -> None:

        if self.is_selected(drawable):
            self.clear()
        else:
            self.select(drawable)

    def is_selected(
        self,
        drawable: Drawable,
    ) -> bool:

        return drawable is self._selected

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __bool__(self) -> bool:

        return self.has_selection

    def __repr__(self) -> str:

        return (
            f"SelectionManager("
            f"selected={self._selected!r})"
        )

    # ==========================================================
    # Évènements
    # ==========================================================

    def _notify(self) -> None:

        self._dispatcher.dispatch(
            SelectionChangedEvent(self._selected)
        )