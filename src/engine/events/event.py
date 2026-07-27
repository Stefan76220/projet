from __future__ import annotations

from abc import ABC


class Event(ABC):
    """
    Classe de base de tous les événements du moteur.
    """

    def __init__(self) -> None:

        self._handled = False

    # ==========================================================
    # État
    # ==========================================================

    @property
    def handled(self) -> bool:
        return self._handled

    @property
    def is_handled(self) -> bool:
        return self._handled

    # ==========================================================
    # Gestion
    # ==========================================================

    def mark_as_handled(self) -> None:

        self._handled = True

    def reset(self) -> None:

        self._handled = False

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __bool__(self) -> bool:

        return self._handled

    # ==========================================================
    # Représentation
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(handled={self._handled})"
        )