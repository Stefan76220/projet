from __future__ import annotations

from typing import Optional

from src.engine.events import (
    EventDispatcher,
    SelectionChangedEvent,
)
from src.engine.graphics import Drawable


class SelectionManager:
    """
    Gère la sélection unique du moteur.
    """

    def __init__(self):

        self._selected: Optional[Drawable] = None
        self._dispatcher = EventDispatcher()

    @property
    def selected(self) -> Optional[Drawable]:
        return self._selected

    @property
    def dispatcher(self) -> EventDispatcher:
        return self._dispatcher

    def clear(self) -> None:

        if self._selected is not None:
            self._selected.unselect()

        self._selected = None

        self._dispatcher.dispatch(
            SelectionChangedEvent(None)
        )

    def select(self, drawable: Drawable) -> None:

        if drawable is self._selected:
            return

        if self._selected is not None:
            self._selected.unselect()

        self._selected = drawable
        drawable.select()

        self._dispatcher.dispatch(
            SelectionChangedEvent(drawable)
        )