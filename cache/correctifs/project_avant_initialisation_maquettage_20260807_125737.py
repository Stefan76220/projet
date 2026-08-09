from __future__ import annotations

import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any


class Project:
    """
    Représentation d'un projet PageMaître.

    Le projet centralise les emplacements nécessaires à :
    - la conception des pages et des modèles ;
    - la conservation des fiches et collections de contenus ;
    - les productions générées ;
    - les ressources graphiques ;
    - les exports et fichiers temporaires.

    Les anciens projets sont mis à niveau automatiquement lors du chargement
    sans supprimer ni déplacer leurs fichiers existants.
    """

    VERSION = "1.5"
    MOCKUP_VERSION = 6

    DEFAULT_PROJECT_TYPE = "ouvrage_structure"
    PROJECT_TYPES = {
        "ouvrage_structure",
        "livre_textuel",
        "bande_dessinee",
    }

    PROJECT_FOLDERS = (
        "documents",
        "ressources",
        "ressources/images",
        "ressources/illustrations",
        "ressources/icones",
        "ressources/logos",
        "ressources/visuels_temoins",
        "modeles",
        "contenus",
        "contenus/fiches",
        "contenus/collections",
        "productions",
        "exports",
        "cache",
        "corbeille",
        "maquettage",
    )

    def __init__(self) -> None:
        self.name = ""
        self.format = "A5"
        self.book_model_id = ""
        self.project_type = self.DEFAULT_PROJECT_TYPE

        self.root: Path | None = None

        self.documents: list[dict[str, Any]] = []
        self.ressources: list[dict[str, Any]] = []

        # Index légers destinés aux futures bibliothèques.
        # Les fichiers complets restent stockés dans leurs propres dossiers.
        self.models: list[dict[str, Any]] = []
        self.content_sheets: list[dict[str, Any]] = []
        self.content_collections: list[dict[str, Any]] = []
        self.visual_references: list[dict[str, Any]] = []
        self.productions: list[dict[str, Any]] = []

        self.creation_date: str = ""
        self.modification_date: str = ""

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def is_loaded(self) -> bool:
        return self.root is not None

    @property
    def documents_folder(self) -> Path:
        return self._require_root() / "documents"

    @property
    def resources_folder(self) -> Path:
        return self._require_root() / "ressources"

    @property
    def visual_references_folder(self) -> Path:
        return self.resources_folder / "visuels_temoins"

    @property
    def models_folder(self) -> Path:
        return self._require_root() / "modeles"

    @property
    def content_folder(self) -> Path:
        return self._require_root() / "contenus"

    @property
    def content_sheets_folder(self) -> Path:
        return self.content_folder / "fiches"

    @property
    def content_collections_folder(self) -> Path:
        return self.content_folder / "collections"

    @property
    def productions_folder(self) -> Path:
        return self._require_root() / "productions"

    @property
    def exports_folder(self) -> Path:
        return self._require_root() / "exports"

    @property
    def cache_folder(self) -> Path:
        return self._require_root() / "cache"

    @property
    def trash_folder(self) -> Path:
        return self._require_root() / "corbeille"

    @property
    def mockup_folder(self) -> Path:
        """Dossier réservé au brouillon visuel du livre."""

        return self._require_root() / "maquettage"

    @property
    def mockup_file(self) -> Path:
        """Fichier persistant du pré-chemin de fer."""

        return self.mockup_folder / "premaquette.json"

    # ==========================================================
    # Création / Chargement
    # ==========================================================

    def create(
        self,
        folder: str,
        name: str,
        project_type: str = DEFAULT_PROJECT_TYPE,
    ) -> Path:
        self.name = name
        self.project_type = self._normalize_project_type(project_type)
        self.root = Path(folder) / name

        now = datetime.now().isoformat()

        self.creation_date = now
        self.modification_date = now

        self.documents.clear()
        self.ressources.clear()
        self.models.clear()
        self.content_sheets.clear()
        self.content_collections.clear()
        self.visual_references.clear()
        self.productions.clear()

        self._create_folders()
        self._ensure_mockup_file()
        self.save()

        return self._require_root()

    def load(
        self,
        project_folder: str,
    ) -> Project:
        self.root = Path(project_folder)

        project_file = self._require_root() / "projet.json"

        if not project_file.exists():
            raise FileNotFoundError(
                "Le fichier projet.json est introuvable."
            )

        with project_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        self.name = str(data.get("nom", ""))
        self.format = str(data.get("format", "A5"))
        self.book_model_id = str(data.get("book_model", ""))
        self.project_type = self._normalize_project_type(
            data.get("type_projet", self.DEFAULT_PROJECT_TYPE)
        )

        self.creation_date = str(
            data.get(
                "date_creation",
                "",
            )
        )

        self.modification_date = str(
            data.get(
                "date_modification",
                "",
            )
        )

        self.documents = self._normalize_index(
            data.get("documents", [])
        )

        self.ressources = self._normalize_index(
            data.get("ressources", [])
        )

        libraries = data.get(
            "bibliotheques",
            {},
        )

        self.models = self._normalize_index(
            libraries.get(
                "modeles",
                data.get("modeles", []),
            )
        )

        self.content_sheets = self._normalize_index(
            libraries.get(
                "fiches",
                data.get("fiches", []),
            )
        )

        self.content_collections = self._normalize_index(
            libraries.get(
                "collections",
                data.get("collections", []),
            )
        )

        self.visual_references = self._normalize_index(
            libraries.get(
                "visuels_temoins",
                data.get("visuels_temoins", []),
            )
        )

        self.productions = self._normalize_index(
            data.get("productions", [])
        )

        # Mise à niveau silencieuse des anciens projets.
        self._create_folders()
        self._ensure_mockup_file()
        self.save()

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
    # Bibliothèques
    # ==========================================================

    def register_model(
        self,
        summary: dict[str, Any],
    ) -> None:
        self._register_summary(
            self.models,
            summary,
        )
        self.save()

    def register_content_sheet(
        self,
        summary: dict[str, Any],
    ) -> None:
        self._register_summary(
            self.content_sheets,
            summary,
        )
        self.save()

    def register_content_collection(
        self,
        summary: dict[str, Any],
    ) -> None:
        self._register_summary(
            self.content_collections,
            summary,
        )
        self.save()

    def register_visual_reference(
        self,
        summary: dict[str, Any],
    ) -> None:
        """Ajoute ou met à jour un visuel témoin du projet."""

        self._register_summary(
            self.visual_references,
            summary,
        )
        self.save()

    def register_production(
        self,
        summary: dict[str, Any],
    ) -> None:
        self._register_summary(
            self.productions,
            summary,
        )
        self.save()

    def unregister_model(
        self,
        identifier: str,
    ) -> bool:
        removed = self._unregister_summary(
            self.models,
            identifier,
        )

        if removed:
            self.save()

        return removed

    def unregister_content_sheet(
        self,
        identifier: str,
    ) -> bool:
        removed = self._unregister_summary(
            self.content_sheets,
            identifier,
        )

        if removed:
            self.save()

        return removed

    def unregister_content_collection(
        self,
        identifier: str,
    ) -> bool:
        removed = self._unregister_summary(
            self.content_collections,
            identifier,
        )

        if removed:
            self.save()

        return removed

    def unregister_visual_reference(
        self,
        identifier: str,
    ) -> bool:
        """Retire un visuel témoin de l'index du projet."""

        removed = self._unregister_summary(
            self.visual_references,
            identifier,
        )

        if removed:
            self.save()

        return removed

    def unregister_production(
        self,
        identifier: str,
    ) -> bool:
        removed = self._unregister_summary(
            self.productions,
            identifier,
        )

        if removed:
            self.save()

        return removed


    # ==========================================================
    # Pré-chemin de fer
    # ==========================================================

    def load_mockup(self) -> dict[str, Any]:
        """Charge le maquettage sans réduire ni perdre son schéma actuel."""

        self._ensure_mockup_file()

        try:
            with self.mockup_file.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            data = self._default_mockup_data()
            self._write_mockup_data(data)
            return deepcopy(data)

        normalized = self._normalize_mockup_data(data)
        if normalized != data:
            self._write_mockup_data(normalized)

        return deepcopy(normalized)

    def save_mockup(
        self,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Enregistre atomiquement le maquettage complet du projet."""

        normalized = self._normalize_mockup_data(data)
        normalized["updated_at"] = datetime.now().isoformat()
        self._write_mockup_data(normalized)
        return deepcopy(normalized)

    def _ensure_mockup_file(self) -> None:
        self.mockup_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        if self.mockup_file.exists():
            return

        self._write_mockup_data(
            self._default_mockup_data()
        )

    @classmethod
    def _default_mockup_data(cls) -> dict[str, Any]:
        """Crée un conteneur compatible avec le Maquettage actuel."""

        now = datetime.now().isoformat()

        return {
            "version": cls.MOCKUP_VERSION,
            "created_at": now,
            "updated_at": now,
            "groups": [],
            "page_types": [],
            "recto_verso_rules": [],
            "items": [],
        }

    @classmethod
    def _normalize_mockup_data(
        cls,
        data: Any,
    ) -> dict[str, Any]:
        """Préserve le schéma 6 et migre l'ancien schéma sans perte."""

        if not isinstance(data, dict):
            return cls._default_mockup_data()

        now = datetime.now().isoformat()
        has_current_schema = any(
            key in data
            for key in (
                "groups",
                "page_types",
                "recto_verso_rules",
                "items",
            )
        )

        # Les premières versions utilisaient seulement ``elements``.
        # Ils sont conservés à part afin qu'aucune ancienne donnée ne soit
        # silencieusement supprimée pendant la migration.
        if not has_current_schema and "elements" in data:
            normalized = cls._default_mockup_data()
            normalized["created_at"] = str(
                data.get("date_creation") or now
            )
            normalized["updated_at"] = str(
                data.get("date_modification")
                or normalized["created_at"]
            )

            elements = data.get("elements", [])
            if isinstance(elements, list):
                legacy_elements = [
                    deepcopy(element)
                    for element in elements
                    if isinstance(element, dict)
                ]
                if legacy_elements:
                    normalized["legacy_elements"] = legacy_elements

            return normalized

        normalized = deepcopy(data)
        created_at = str(
            data.get("created_at")
            or data.get("date_creation")
            or now
        )
        updated_at = str(
            data.get("updated_at")
            or data.get("date_modification")
            or created_at
        )

        normalized["version"] = cls.MOCKUP_VERSION
        normalized["created_at"] = created_at
        normalized["updated_at"] = updated_at

        for key in (
            "groups",
            "page_types",
            "recto_verso_rules",
            "items",
        ):
            values = data.get(key, [])
            normalized[key] = (
                [
                    deepcopy(value)
                    for value in values
                    if isinstance(value, dict)
                ]
                if isinstance(values, list)
                else []
            )

        elements = normalized.pop("elements", None)
        if isinstance(elements, list) and elements:
            normalized.setdefault(
                "legacy_elements",
                [
                    deepcopy(element)
                    for element in elements
                    if isinstance(element, dict)
                ],
            )

        normalized.pop("date_creation", None)
        normalized.pop("date_modification", None)
        return normalized

    def _write_mockup_data(
        self,
        data: dict[str, Any],
    ) -> None:
        """Écrit le JSON par remplacement atomique du fichier précédent."""

        self.mockup_folder.mkdir(
            parents=True,
            exist_ok=True,
        )
        temporary = self.mockup_file.with_suffix(".tmp")

        with temporary.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

        temporary.replace(self.mockup_file)

    # ==========================================================
    # Construction
    # ==========================================================

    def _create_folders(self) -> None:
        root = self._require_root()

        for folder in self.PROJECT_FOLDERS:
            (root / folder).mkdir(
                parents=True,
                exist_ok=True,
            )

    def _project_data(self) -> dict[str, Any]:
        return {
            "nom": self.name,
            "version": self.VERSION,
            "type_projet": self.project_type,
            "format": self.format,
            "book_model": self.book_model_id,
            "date_creation": self.creation_date,
            "date_modification": self.modification_date,
            "documents": self.documents,
            "ressources": self.ressources,
            "bibliotheques": {
                "modeles": self.models,
                "fiches": self.content_sheets,
                "collections": self.content_collections,
                "visuels_temoins": self.visual_references,
            },
            "productions": self.productions,
        }

    @classmethod
    def _normalize_project_type(cls, value: Any) -> str:
        normalized = str(value or "").strip().casefold()

        aliases = {
            "ouvrage_structuré": "ouvrage_structure",
            "ouvrage structure": "ouvrage_structure",
            "structure": "ouvrage_structure",
            "livre textuel": "livre_textuel",
            "textuel": "livre_textuel",
            "bande dessinée": "bande_dessinee",
            "bande dessinee": "bande_dessinee",
            "bd": "bande_dessinee",
        }

        normalized = aliases.get(normalized, normalized)

        if normalized not in cls.PROJECT_TYPES:
            return cls.DEFAULT_PROJECT_TYPE

        return normalized

    # ==========================================================
    # Index internes
    # ==========================================================

    @staticmethod
    def _normalize_index(
        values: Any,
    ) -> list[dict[str, Any]]:
        if not isinstance(values, list):
            return []

        return [
            dict(value)
            for value in values
            if isinstance(value, dict)
        ]

    @staticmethod
    def _register_summary(
        index: list[dict[str, Any]],
        summary: dict[str, Any],
    ) -> None:
        normalized = dict(summary)
        identifier = str(
            normalized.get(
                "identifiant",
                "",
            )
        ).strip()

        if not identifier:
            raise ValueError(
                "Le résumé doit posséder un identifiant."
            )

        for position, existing in enumerate(index):
            if str(
                existing.get(
                    "identifiant",
                    "",
                )
            ) == identifier:
                index[position] = normalized
                return

        index.append(normalized)

    @staticmethod
    def _unregister_summary(
        index: list[dict[str, Any]],
        identifier: str,
    ) -> bool:
        normalized_identifier = identifier.strip()

        for position, existing in enumerate(index):
            if str(
                existing.get(
                    "identifiant",
                    "",
                )
            ) == normalized_identifier:
                index.pop(position)
                return True

        return False

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
            f"project_type={self.project_type!r}, "
            f"documents={len(self.documents)}, "
            f"models={len(self.models)}, "
            f"sheets={len(self.content_sheets)}, "
            f"collections={len(self.content_collections)}, "
            f"visual_references={len(self.visual_references)}, "
            f"productions={len(self.productions)})"
        )