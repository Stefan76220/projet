from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from src.core.page import Page


class Document:
    """
    Représentation d'un document.
    """

    VERSION = "1.0"

    def __init__(self) -> None:

        self.name = ""
        self.type = "Livre"

        self.root: Path | None = None

        self.pages: list[dict] = []

        self.creation_date: str = ""
        self.modification_date: str = ""

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
    # Création / Chargement
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
            data.get("pages", [])
        )

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

        page_type = page_type or "Page vide"

        number = self.page_count + 1

        page = Page()
        page.page_type = page_type

        page.create(
            self._require_root() / "pages",
            number,
        )

        self.pages.append(
            {
                "numero": number,
                "dossier": f"page_{number:04d}",
            }
        )

        self.save()

        return page

    def get_page(
        self,
        numero: int,
    ) -> Page | None:

        folder = (
            self._require_root()
            / "pages"
            / f"page_{numero:04d}"
        )

        if not folder.exists():
            return None

        page = Page()

        page.load(
            folder,
        )

        return page

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