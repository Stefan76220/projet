from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from src.core.page import Page


class Document:
    """
    Représentation d'un document et de ses pages éditoriales.
    """

    VERSION = "2.0"

    def __init__(self) -> None:

        self.name = ""
        self.type = "Livre"

        self.root: Path | None = None

        self.pages: list[dict] = []

        self.creation_date = ""
        self.modification_date = ""

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def is_loaded(self) -> bool:
        return self.root is not None

    @property
    def page_count(self) -> int:
        return len(self.pages)

    # ==========================================================
    # Création
    # ==========================================================

    def create(
        self,
        documents_folder: str | Path,
        name: str,
    ) -> Document:

        self.name = name
        self.root = Path(documents_folder) / name

        root = self._require_root()

        root.mkdir(
            parents=True,
            exist_ok=True,
        )

        (root / "pages").mkdir(
            exist_ok=True,
        )

        now = datetime.now().isoformat()

        self.creation_date = now
        self.modification_date = now

        self.pages.clear()

        self.save()

        return self

    # ==========================================================
    # Chargement
    # ==========================================================

    def load(
        self,
        folder: str | Path,
    ) -> Document:

        self.root = Path(folder)

        document_file = self._require_root() / "document.json"

        with document_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        self.name = data.get(
            "nom",
            self._require_root().name,
        )

        self.type = data.get(
            "type",
            "Livre",
        )

        self.creation_date = data.get(
            "date_creation",
            "",
        )

        self.modification_date = data.get(
            "date_modification",
            "",
        )

        self.pages = list(
            data.get(
                "pages",
                [],
            )
        )

        self._refresh_page_summaries()

        return self

    # ==========================================================
    # Sauvegarde
    # ==========================================================

    def save(self) -> None:

        if not self.is_loaded:
            return

        self.modification_date = datetime.now().isoformat()

        document_file = self._require_root() / "document.json"

        with document_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                self._document_data(),
                file,
                indent=4,
                ensure_ascii=False,
            )

    # ==========================================================
    # Pages
    # ==========================================================

    def add_page(
        self,
        page_type: str | None = None,
    ) -> Page:

        page_type = page_type or Page.DEFAULT_TYPE
        number = self._next_page_number()

        page = Page()

        page.create(
            pages_folder=self._require_root() / "pages",
            number=number,
            page_type=page_type,
        )

        self.pages.append(
            page.to_summary()
        )

        self.save()

        return page

    def get_page(
        self,
        numero: int,
    ) -> Page | None:

        page_info = self._find_page_info(
            numero,
        )

        if page_info is None:
            return None

        folder_name = page_info.get(
            "dossier",
            f"page_{numero:04d}",
        )

        folder = (
            self._require_root()
            / "pages"
            / folder_name
        )

        if not folder.exists():
            return None

        page = Page()
        page.load(folder)

        return page

    def update_page_summary(
        self,
        page: Page,
    ) -> None:

        for index, page_info in enumerate(self.pages):

            same_identifier = (
                page_info.get("identifiant")
                and page_info.get("identifiant") == page.identifier
            )

            same_number = (
                page_info.get("numero") == page.number
            )

            if same_identifier or same_number:

                self.pages[index] = page.to_summary()
                self.save()
                return

        self.pages.append(
            page.to_summary()
        )

        self.save()

    # ==========================================================
    # Synchronisation
    # ==========================================================

    def _refresh_page_summaries(self) -> None:
        """
        Met à niveau automatiquement les anciens documents.
        """

        refreshed_pages: list[dict] = []

        for page_info in self.pages:

            number = page_info.get(
                "numero",
                0,
            )

            folder_name = page_info.get(
                "dossier",
                f"page_{number:04d}",
            )

            folder = (
                self._require_root()
                / "pages"
                / folder_name
            )

            page_file = folder / "page.json"

            if not page_file.exists():
                refreshed_pages.append(page_info)
                continue

            try:

                page = Page()
                page.load(folder)

                refreshed_pages.append(
                    page.to_summary()
                )

            except Exception:

                refreshed_pages.append(page_info)

        self.pages = refreshed_pages
        self.save()

    # ==========================================================
    # Recherche
    # ==========================================================

    def _find_page_info(
        self,
        numero: int,
    ) -> dict | None:

        for page_info in self.pages:

            if page_info.get("numero") == numero:
                return page_info

        return None

    def _next_page_number(self) -> int:

        if not self.pages:
            return 1

        numbers = [
            page.get("numero", 0)
            for page in self.pages
        ]

        return max(numbers) + 1

    # ==========================================================
    # Construction
    # ==========================================================

    def _document_data(self) -> dict:

        return {
            "nom": self.name,
            "type": self.type,
            "version": self.VERSION,
            "date_creation": self.creation_date,
            "date_modification": self.modification_date,
            "pages": self.pages,
        }

    def _require_root(self) -> Path:

        if self.root is None:
            raise RuntimeError(
                "Le document n'a pas encore de dossier."
            )

        return self.root

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"pages={self.page_count})"
        )