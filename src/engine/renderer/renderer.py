from __future__ import annotations

from abc import ABC, abstractmethod

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

    @abstractmethod
    def begin_frame(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def end_frame(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_page(self, page: Page) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_drawable(self, drawable: Drawable) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_rectangle(self, rectangle: Rectangle) -> None:
        raise NotImplementedError

    @abstractmethod
    def draw_ellipse(self, ellipse: Ellipse) -> None:
        raise NotImplementedError