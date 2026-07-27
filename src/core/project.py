from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class Project:
    """
    Représentation d'un projet.
    """

    VERSION = "1.0"

    def __init__(self) -> None:

        self.name = ""
        self.format = "A5"
        self.book_model_id = ""

        self.root: Path | None = None

        self.documents: list[dict] = []
        self.ressources: list[dict] = []

        self.creation_date: str = ""
        self.modification_date: str = ""

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
        folder: str,
        name: str,
    ) -> Path:

        self.name = name
        self.root = Path(folder) / name

        now = datetime.now().isoformat()

        self.creation_date = now
        self.modification_date = now

        self.documents.clear()
        self.ressources.clear()

        self._create_folders()

        self.save()

        return self.root

    def load(
        self,
        project_folder: str,
    ) -> Project:

        self.root = Path(project_folder)

        project_file = self.root / "projet.json"

        if not project_file.exists():
            raise FileNotFoundError(
                "Le fichier projet.json est introuvable."
            )

        with project_file.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        self.name = data.get("nom", "")
        self.format = data.get("format", "A5")
        self.book_model_id = data.get("book_model", "")

        self.creation_date = data.get(
            "date_creation",
            "",
        )

        self.modification_date = data.get(
            "date_modification",
            "",
        )

        self.documents = list(
            data.get("documents", [])
        )

        self.ressources = list(
            data.get("ressources", [])
        )

        return self

    # ==========================================================
    # Sauvegarde
    # ==========================================================

    def save(self) -> None:

        self.modification_date = datetime.now().isoformat()

        project_file = self._require_root() / "projet.json"

        with project_file.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                self._project_data(),
                file,
                indent=4,
                ensure_ascii=False,
            )

    # ==========================================================
    # Documents
    # ==========================================================

    def add_document(
        self,
        name: str,
        document_type: str = "Livre",
    ) -> None:

        self.documents.append(
            {
                "nom": name,
                "type": document_type,
            }
        )

        self.save()

    # ==========================================================
    # Construction
    # ==========================================================

    def _create_folders(self) -> None:

        root = self._require_root()

        folders = (
            "documents",
            "ressources",
            "ressources/images",
            "ressources/illustrations",
            "ressources/icones",
            "ressources/logos",
            "modeles",
            "exports",
            "cache",
        )

        for folder in folders:

            (root / folder).mkdir(
                parents=True,
                exist_ok=True,
            )

    def _project_data(self) -> dict:

        return {
            "nom": self.name,
            "version": self.VERSION,
            "format": self.format,
            "book_model": self.book_model_id,
            "date_creation": self.creation_date,
            "date_modification": self.modification_date,
            "documents": self.documents,
            "ressources": self.ressources,
        }

    def _require_root(self) -> Path:

        if self.root is None:
            raise RuntimeError(
                "Le projet n'a pas encore de dossier racine."
            )

        return self.root

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"documents={len(self.documents)})"
        )