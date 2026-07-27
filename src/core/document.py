from __future__ import annotations

import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from uuid import uuid4

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

    def duplicate_page(
        self,
        numero: int,
    ) -> Page | None:
        """
        Duplique intégralement une page.

        La copie reçoit :
        - un nouveau numéro ;
        - un nouvel identifiant ;
        - un nouveau dossier ;
        - de nouvelles dates ;
        - un nom de copie unique.

        Les fichiers éventuellement présents dans le dossier de la page
        sont également copiés.
        """

        source_page = self.get_page(
            numero,
        )

        if source_page is None:
            return None

        source_root = source_page.root

        if source_root is None or not source_root.exists():
            return None

        new_number = self._next_page_number()
        new_title = self._next_copy_title(
            source_page.display_title,
        )

        pages_folder = self._require_root() / "pages"
        destination_root = pages_folder / f"page_{new_number:04d}"

        if destination_root.exists():
            raise FileExistsError(
                f"Le dossier {destination_root.name} existe déjà."
            )

        shutil.copytree(
            source_root,
            destination_root,
        )

        duplicated_page = Page()
        duplicated_page.load(
            destination_root,
        )

        now = datetime.now().isoformat()

        duplicated_page.identifier = str(uuid4())
        duplicated_page.number = new_number
        duplicated_page.title = new_title

        duplicated_page.created = now
        duplicated_page.modified = now

        # Une copie doit pouvoir être modifiée immédiatement.
        duplicated_page.locked = False

        duplicated_page.history = []

        duplicated_page._add_history(
            action="duplication",
            description=(
                f"Page créée par duplication de "
                f"« {source_page.display_title} »."
            ),
        )

        duplicated_page.save(
            update_history=False,
        )

        source_index = self._find_page_index(
            numero,
        )

        duplicated_summary = duplicated_page.to_summary()

        if source_index is None:
            self.pages.append(
                duplicated_summary,
            )

        else:
            self.pages.insert(
                source_index + 1,
                duplicated_summary,
            )

        self.save()

        return duplicated_page

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
    # Noms des copies
    # ==========================================================

    def _next_copy_title(
        self,
        original_title: str,
    ) -> str:

        base_title = self._copy_base_title(
            original_title,
        )

        existing_titles = {
            str(page.get("nom", "")).strip().casefold()
            for page in self.pages
        }

        first_copy = f"{base_title} (copie)"

        if first_copy.casefold() not in existing_titles:
            return first_copy

        copy_number = 2

        while True:

            candidate = (
                f"{base_title} "
                f"(copie {copy_number})"
            )

            if candidate.casefold() not in existing_titles:
                return candidate

            copy_number += 1

    @staticmethod
    def _copy_base_title(
        title: str,
    ) -> str:

        clean_title = title.strip()

        copy_pattern = re.compile(
            r"\s+\(copie(?:\s+\d+)?\)$",
            flags=re.IGNORECASE,
        )

        base_title = copy_pattern.sub(
            "",
            clean_title,
        ).strip()

        return base_title or "Page"

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
                refreshed_pages.append(
                    page_info,
                )
                continue

            try:

                page = Page()
                page.load(
                    folder,
                )

                refreshed_pages.append(
                    page.to_summary()
                )

            except Exception:

                refreshed_pages.append(
                    page_info,
                )

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

    def _find_page_index(
        self,
        numero: int,
    ) -> int | None:

        for index, page_info in enumerate(self.pages):

            if page_info.get("numero") == numero:
                return index

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