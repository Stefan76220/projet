from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class Page:
    """
    Représentation d'une page.
    """

    VERSION = "1.0"

    def __init__(self) -> None:

        self.number = 1
        self.title = ""

        self.page_type = "Page vide"
        self.state = "Brouillon"

        self.author = ""
        self.description = ""

        self.format = "A5"
        self.orientation = "Portrait"

        self.elements: list = []
        self.history: list = []

        self.created = ""
        self.modified = ""

        self.root: Path | None = None

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def is_loaded(self) -> bool:

        return self.root is not None

    # ==========================================================
    # Création / Chargement
    # ==========================================================

    def create(
        self,
        pages_folder: str | Path,
        number: int,
    ) -> Path:

        self.number = number

        now = datetime.now().isoformat()

        self.created = now
        self.modified = now

        self.root = (
            Path(pages_folder)
            / f"page_{number:04d}"
        )

        self._require_root().mkdir(
            parents=True,
            exist_ok=True,
        )

        self.save()

        return self._require_root()

    def load(
        self,
        folder: str | Path,
    ) -> Page:

        self.root = Path(folder)

        page_file = self._require_root() / "page.json"

        with page_file.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        identity = data.get("identite", {})
        metadata = data.get("metadonnees", {})
        layout = data.get("mise_en_page", {})

        self.number = identity.get("numero", 1)
        self.title = identity.get("nom", "")
        self.page_type = identity.get("type", "Page vide")
        self.state = identity.get("etat", "Brouillon")

        self.author = metadata.get("auteur", "")
        self.created = metadata.get("creation", "")
        self.modified = metadata.get("modification", "")
        self.description = metadata.get("description", "")

        self.format = layout.get("format", "A5")
        self.orientation = layout.get("orientation", "Portrait")

        self.elements = list(
            data.get("elements", [])
        )

        self.history = list(
            data.get("historique", [])
        )

        return self

    # ==========================================================
    # Sauvegarde
    # ==========================================================

    def save(self) -> None:

        if not self.is_loaded:
            return

        self.modified = datetime.now().isoformat()

        page_file = self._require_root() / "page.json"

        with page_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                self._page_data(),
                file,
                indent=4,
                ensure_ascii=False,
            )

    # ==========================================================
    # Construction
    # ==========================================================

    def _page_data(self) -> dict:

        return {

            "identite": {

                "numero": self.number,
                "nom": self.title or f"Page {self.number:03d}",
                "type": self.page_type,
                "etat": self.state,
                "version": self.VERSION,

            },

            "metadonnees": {

                "auteur": self.author,
                "creation": self.created,
                "modification": self.modified,
                "description": self.description,

            },

            "mise_en_page": {

                "format": self.format,
                "orientation": self.orientation,

            },

            "elements": self.elements,

            "historique": self.history,

        }

    def _require_root(self) -> Path:

        if self.root is None:
            raise RuntimeError(
                "La page n'a pas encore de dossier."
            )

        return self.root

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"number={self.number}, "
            f"type={self.page_type!r})"
        )