from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.engine.workspace import Workspace


class Tool(ABC):
    """
    Classe de base de tous les outils du moteur.
    """

    def __init__(
        self,
        workspace: "Workspace",
    ) -> None:

        self._workspace = workspace

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def workspace(self) -> "Workspace":
        return self._workspace

    @property
    def name(self) -> str:
        return self.__class__.__name__

    # ==========================================================
    # Cycle de vie
    # ==========================================================

    def activate(self) -> None:
        """
        Appelé lorsque l'outil devient actif.
        """

    def deactivate(self) -> None:
        """
        Appelé lorsque l'outil cesse d'être actif.
        """

    # ==========================================================
    # Évènements souris
    # ==========================================================

    def mouse_press(
        self,
        x: float,
        y: float,
        button: int,
    ) -> None:
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
    # Clavier
    # ==========================================================

    def key_press(
        self,
        key: str,
    ) -> None:
        ...

    def key_release(
        self,
        key: str,
    ) -> None:
        ...

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __str__(self) -> str:
        return self.name