from __future__ import annotations

from abc import ABC, abstractmethod


class Command(ABC):
    """
    Classe de base de toutes les commandes du moteur.
    """

    def __init__(
        self,
        name: str = "",
    ) -> None:

        self._name = name or self.__class__.__name__

    # ==========================================================
    # Informations
    # ==========================================================

    @property
    def name(self) -> str:
        return self._name

    # ==========================================================
    # Cycle de vie
    # ==========================================================

    @abstractmethod
    def execute(self) -> None:
        """
        Exécute la commande.
        """
        raise NotImplementedError

    @abstractmethod
    def undo(self) -> None:
        """
        Annule la commande.
        """
        raise NotImplementedError

    def redo(self) -> None:
        """
        Réexécute la commande.
        """

        self.execute()

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __str__(self) -> str:

        return self.name

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(name={self.name!r})"
        )