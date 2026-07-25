from __future__ import annotations

from src.engine.events.event import Event
from src.engine.graphics.drawable import Drawable


class SelectionChangedEvent(Event):
    """
    Événement émis lorsque la sélection change.
    """

    def __init__(self, selected: Drawable | None):

        self._selected = selected

    @property
    def selected(self) -> Drawable | None:
        return self._selected