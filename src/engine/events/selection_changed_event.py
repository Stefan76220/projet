from __future__ import annotations

from src.engine.events.event import Event
from src.engine.graphics.drawable import Drawable


class SelectionChangedEvent(Event):
    """
    Événement émis lorsque la sélection change.
    """

    def __init__(
        self,
        selected: Drawable | None,
    ):

        super().__init__()

        self._selected = selected

    # ==========================================================
    # Données
    # ==========================================================

    @property
    def selected(self) -> Drawable | None:
        return self._selected

    @property
    def has_selection(self) -> bool:
        return self._selected is not None

    # ==========================================================
    # Représentation
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(selected={self._selected!r})"
        )