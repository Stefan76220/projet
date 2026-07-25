from __future__ import annotations

from src.engine.foundation import Point, Rect, Size
from src.engine.graphics import Layer, Page, Workspace


class Document:
    """
    Représente un document éditable.
    """

    PAGE_WIDTH = 420
    PAGE_HEIGHT = 595

    def __init__(self, name: str):

        self._name = name
        self._workspace = Workspace()

    @property
    def name(self) -> str:
        return self._name

    @property
    def workspace(self) -> Workspace:
        return self._workspace

    @property
    def pages(self) -> tuple[Page, ...]:
        return self._workspace.pages

    def create_page(self) -> Page:
        """
        Crée une nouvelle page avec une couche par défaut.
        """

        page = Page(
            Rect(
                Point(0, 0),
                Size(
                    self.PAGE_WIDTH,
                    self.PAGE_HEIGHT,
                ),
            )
        )

        page.add_layer(Layer())

        self._workspace.add_page(page)

        return page