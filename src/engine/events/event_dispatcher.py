from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from src.engine.events.event import Event


class EventDispatcher:
    """
    Répartiteur d'événements du moteur.
    """

    def __init__(self):

        self._listeners: dict[type[Event], list[Callable[[Event], None]]] = defaultdict(list)

    def subscribe(
        self,
        event_type: type[Event],
        listener: Callable[[Event], None],
    ) -> None:

        if listener not in self._listeners[event_type]:
            self._listeners[event_type].append(listener)

    def unsubscribe(
        self,
        event_type: type[Event],
        listener: Callable[[Event], None],
    ) -> None:

        if listener in self._listeners[event_type]:
            self._listeners[event_type].remove(listener)

    def dispatch(self, event: Event) -> None:

        for listener in self._listeners[type(event)]:
            listener(event)

    def clear(self) -> None:

        self._listeners.clear()