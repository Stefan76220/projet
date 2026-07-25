from __future__ import annotations

from src.engine.camera import Camera
from src.engine.graphics.page import Page
from src.engine.selection import SelectionManager


class Workspace:
    """
    Conteneur racine du moteur graphique.
    """

    def __init__(self):

        self._pages: list[Page] = []

        self._camera = Camera()
        self._selection = SelectionManager()

    @property
    def camera(self) -> Camera:
        return self._camera

    @property
    def selection(self) -> SelectionManager:
        return self._selection

    def add_page(self, page: Page) -> None:

        if page not in self._pages:
            self._pages.append(page)

    def remove_page(self, page: Page) -> None:

        if page in self._pages:
            self._pages.remove(page)

    def clear(self) -> None:

        self._pages.clear()
        self._selection.clear()

    def page(self, index: int) -> Page:
        return self._pages[index]

    @property
    def pages(self) -> tuple[Page, ...]:
        return tuple(self._pages)

    def __iter__(self):
        return iter(self._pages)

    def __len__(self):
        return len(self._pages)
    