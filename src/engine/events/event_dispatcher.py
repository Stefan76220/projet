from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from src.engine.events.event import Event


class EventDispatcher:
    """
    Répartiteur d'événements du moteur.
    """

    def __init__(self) -> None:

        self._listeners: dict[
            type[Event],
            list[Callable[[Event], None]],
        ] = defaultdict(list)

    # ==========================================================
    # Abonnements
    # ==========================================================

    def subscribe(
        self,
        event_type: type[Event],
        listener: Callable[[Event], None],
    ) -> None:

        listeners = self._listeners[event_type]

        if listener not in listeners:
            listeners.append(listener)

    def unsubscribe(
        self,
        event_type: type[Event],
        listener: Callable[[Event], None],
    ) -> None:

        listeners = self._listeners.get(event_type)

        if listeners is None:
            return

        if listener in listeners:
            listeners.remove(listener)

            if not listeners:
                del self._listeners[event_type]

    # ==========================================================
    # Diffusion
    # ==========================================================

    def dispatch(
        self,
        event: Event,
    ) -> None:

        for listener in tuple(self._listeners.get(type(event), ())):

            if event.handled:
                break

            listener(event)

    # ==========================================================
    # Gestion
    # ==========================================================

    def clear(self) -> None:

        self._listeners.clear()

    @property
    def listener_count(self) -> int:

        return sum(
            len(listeners)
            for listeners in self._listeners.values()
        )

    def has_listeners(
        self,
        event_type: type[Event],
    ) -> bool:

        return event_type in self._listeners

    def listeners(
        self,
        event_type: type[Event],
    ) -> tuple[Callable[[Event], None], ...]:

        return tuple(self._listeners.get(event_type, ()))

    def __len__(self) -> int:

        return self.listener_count