from __future__ import annotations

from abc import ABC, abstractmethod


class Command(ABC):
    """
    Classe de base de toutes les commandes du moteur.
    """

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