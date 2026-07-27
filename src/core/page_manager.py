from __future__ import annotations

from pathlib import Path

from src.core.page import Page


class PageManager:
    """
    Gestionnaire des pages.
    """

    def __init__(self) -> None:

        self.current_page: Page | None = None

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def has_page(self) -> bool:

        return self.current_page is not None

    # ==========================================================
    # Création
    # ==========================================================

    def new_page(
        self,
        document_folder: str | Path,
        number: int,
        page_type: str = "Page vide",
    ) -> Page:

        pages_folder = Path(document_folder) / "pages"

        pages_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        page = Page()
        page.page_type = page_type

        page.create(
            pages_folder,
            number,
        )

        self.current_page = page

        return page

    # ==========================================================
    # Chargement
    # ==========================================================

    def load_page(
        self,
        page_folder: str | Path,
    ) -> Page:

        page = Page()

        page.load(
            page_folder,
        )

        self.current_page = page

        return page

    # ==========================================================
    # Accès
    # ==========================================================

    def get_page(self) -> Page | None:

        return self.current_page

    def close_page(self) -> None:

        self.current_page = None

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"current_page={self.current_page!r})"
        )