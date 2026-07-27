from __future__ import annotations

from abc import ABC, abstractmethod

from src.engine.document import Document
from src.engine.graphics import (
    Drawable,
    Ellipse,
    Page,
    Rectangle,
)


class Renderer(ABC):
    """
    Interface de rendu du moteur graphique.
    """

    # ==========================================================
    # Cycle de rendu
    # ==========================================================

    @abstractmethod
    def begin_frame(self) -> None:
        """
        Début d'une passe de rendu.
        """
        raise NotImplementedError

    @abstractmethod
    def end_frame(self) -> None:
        """
        Fin d'une passe de rendu.
        """
        raise NotImplementedError

    # ==========================================================
    # Rendu haut niveau
    # ==========================================================

    @abstractmethod
    def draw_document(
        self,
        document: Document,
    ) -> None:
        """
        Dessine un document complet.
        """
        raise NotImplementedError

    @abstractmethod
    def draw_page(
        self,
        page: Page,
    ) -> None:
        """
        Dessine une page.
        """
        raise NotImplementedError

    @abstractmethod
    def draw_drawable(
        self,
        drawable: Drawable,
    ) -> None:
        """
        Dessine un objet graphique.
        """
        raise NotImplementedError

    # ==========================================================
    # Primitives graphiques
    # ==========================================================

    @abstractmethod
    def draw_rectangle(
        self,
        rectangle: Rectangle,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_ellipse(
        self,
        ellipse: Ellipse,
    ) -> None:
        raise NotImplementedError