from __future__ import annotations

from src.engine.foundation import Point, Rect, Size
from src.engine.graphics import Layer, Page
from src.engine.workspace import Workspace


class Document:
    """
    Représente un document éditable.

    Le Document est le propriétaire des données du document :
    - nom
    - pages

    Le Workspace ne contient que les services de travail.
    """

    DEFAULT_PAGE_WIDTH = 420
    DEFAULT_PAGE_HEIGHT = 595

    def __init__(
        self,
        name: str,
    ) -> None:

        self._name = name
        self._pages: list[Page] = []

        self._workspace = Workspace(self)

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def name(self) -> str:
        return self._name

    @property
    def workspace(self) -> Workspace:
        return self._workspace

    @property
    def pages(self) -> list[Page]:
        return self._pages

    @property
    def page_count(self) -> int:
        return len(self._pages)

    # ==========================================================
    # Pages
    # ==========================================================

    def create_page(self) -> Page:

        page = Page(
            Rect(
                Point(0, 0),
                Size(
                    self.DEFAULT_PAGE_WIDTH,
                    self.DEFAULT_PAGE_HEIGHT,
                ),
            )
        )

        page.add_layer(Layer())

        self.add_page(page)

        return page

    def add_page(
        self,
        page: Page,
    ) -> None:

        if page not in self._pages:
            self._pages.append(page)

    def remove_page(
        self,
        page: Page,
    ) -> None:

        if page in self._pages:
            self._pages.remove(page)

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __len__(self) -> int:
        return self.page_count

    def __iter__(self):
        return iter(self._pages)

    def __repr__(self) -> str:

        return (
            f"Document("
            f"name={self._name!r}, "
            f"pages={self.page_count})"
        )