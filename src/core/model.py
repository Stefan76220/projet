from __future__ import annotations

import json
import re
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from src.core.page import Page
from src.core.zone import Zone


class Model:
    """
    Modèle de page réutilisable de PageMaître.

    Un modèle conserve :
    - la géométrie complète de la page ;
    - les marges, fonds perdus et image de fond ;
    - les zones fixes ;
    - les zones remplissables et leurs identifiants de champ ;
    - ses métadonnées et son historique de versions.

    La structure du modèle reste modifiable uniquement dans l'Atelier.
    Les pages produites à partir de ce modèle seront verrouillées
    structurellement dans les autres espaces.
    """

    VERSION = "1.0"

    def __init__(self) -> None:
        # Identité
        self.identifier = str(uuid4())
        self.name = ""
        self.category = ""
        self.description = ""
        self.tags: list[str] = []

        # Version
        self.version_number = 1
        self.version_note = ""

        # Origine
        self.source_page_id = ""
        self.source_page_title = ""

        # Aperçu
        self.thumbnail = ""

        # Structure de page
        self.page_definition: dict[str, Any] = {}
        self.fields: list[dict[str, Any]] = []

        # Dates
        self.created = ""
        self.modified = ""

        # Emplacement
        self.root: Path | None = None

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def is_loaded(self) -> bool:
        return self.root is not None

    @property
    def folder_name(self) -> str:
        slug = self._slugify(self.name or "modele")
        return f"{slug}_{self.identifier[:8]}"

    @property
    def version_label(self) -> str:
        return f"v{self.version_number}"

    @property
    def zone_count(self) -> int:
        return len(self.get_zones())

    @property
    def fillable_zone_count(self) -> int:
        return len(self.fields)

    # ==========================================================
    # Création
    # ==========================================================

    def create_from_page(
        self,
        models_folder: str | Path,
        page: Page,
        name: str,
        *,
        category: str = "",
        description: str = "",
        thumbnail: str = "",
        auto_prepare_zones: bool = False,
    ) -> Path:
        if not isinstance(page, Page):
            raise TypeError(
                "La source du modèle doit être une instance de Page."
            )

        clean_name = name.strip()

        if not clean_name:
            raise ValueError("Le modèle doit posséder un nom.")

        self.name = clean_name
        self.category = category.strip()
        self.description = description.strip()
        self.thumbnail = thumbnail.strip()

        self.source_page_id = page.identifier
        self.source_page_title = page.display_title

        now = datetime.now().isoformat()
        self.created = now
        self.modified = now

        self.page_definition = self._extract_page_definition(
            page,
            auto_prepare_zones=auto_prepare_zones,
        )
        self.fields = self._extract_fields(
            self.page_definition.get("elements", [])
        )

        errors = self.validate()

        if errors:
            raise ValueError(
                "Le modèle ne peut pas être enregistré :\n- "
                + "\n- ".join(errors)
            )

        self.root = Path(models_folder) / self.folder_name
        self._require_root().mkdir(
            parents=True,
            exist_ok=False,
        )

        (self._require_root() / "versions").mkdir(
            exist_ok=True,
        )

        self.save(
            create_snapshot=True,
        )

        return self._require_root()

    def create_blank(
        self,
        models_folder: str | Path,
        name: str,
        *,
        category: str = "",
        description: str = "",
        format_name: str = Page.DEFAULT_FORMAT,
        orientation: str = Page.DEFAULT_ORIENTATION,
    ) -> Path:
        page = Page()
        page.set_format(
            format_name,
            orientation,
        )
        page.page_kind = "modele"
        page.structure_workspace = "atelier"
        page.content_workspace = "atelier"

        return self.create_from_page(
            models_folder=models_folder,
            page=page,
            name=name,
            category=category,
            description=description,
            auto_prepare_zones=False,
        )

    # ==========================================================
    # Chargement
    # ==========================================================

    def load(
        self,
        folder: str | Path,
    ) -> Model:
        self.root = Path(folder)

        model_file = self._require_root() / "modele.json"

        if not model_file.exists():
            raise FileNotFoundError(
                "Le fichier modele.json est introuvable."
            )

        with model_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        identity = data.get("identite", {})
        metadata = data.get("metadonnees", {})
        version = data.get("version_modele", {})
        source = data.get("source", {})

        self.identifier = str(
            identity.get(
                "identifiant",
                str(uuid4()),
            )
        )
        self.name = str(
            identity.get(
                "nom",
                "",
            )
        )
        self.category = str(
            identity.get(
                "categorie",
                "",
            )
        )

        self.description = str(
            metadata.get(
                "description",
                "",
            )
        )
        self.tags = [
            str(tag)
            for tag in metadata.get(
                "mots_cles",
                [],
            )
        ]
        self.thumbnail = str(
            metadata.get(
                "miniature",
                "",
            )
        )
        self.created = str(
            metadata.get(
                "creation",
                "",
            )
        )
        self.modified = str(
            metadata.get(
                "modification",
                "",
            )
        )

        self.version_number = self._safe_positive_int(
            version.get(
                "numero",
                1,
            ),
            default=1,
        )
        self.version_note = str(
            version.get(
                "note",
                "",
            )
        )

        self.source_page_id = str(
            source.get(
                "page_identifiant",
                "",
            )
        )
        self.source_page_title = str(
            source.get(
                "page_nom",
                "",
            )
        )

        self.page_definition = deepcopy(
            data.get(
                "definition_page",
                {},
            )
        )

        loaded_fields = data.get(
            "champs",
            [],
        )

        if isinstance(loaded_fields, list):
            self.fields = [
                dict(field)
                for field in loaded_fields
                if isinstance(field, dict)
            ]
        else:
            self.fields = []

        # La liste des champs est recalculée pour éviter les divergences.
        self.fields = self._extract_fields(
            self.page_definition.get(
                "elements",
                [],
            )
        )

        return self

    # ==========================================================
    # Mise à jour depuis l'Atelier
    # ==========================================================

    def update_from_page(
        self,
        page: Page,
        *,
        version_note: str = "",
        auto_prepare_zones: bool = False,
    ) -> None:
        if not self.is_loaded:
            raise RuntimeError(
                "Le modèle doit être chargé avant d'être modifié."
            )

        if not isinstance(page, Page):
            raise TypeError(
                "La source du modèle doit être une instance de Page."
            )

        self.page_definition = self._extract_page_definition(
            page,
            auto_prepare_zones=auto_prepare_zones,
        )
        self.fields = self._extract_fields(
            self.page_definition.get("elements", [])
        )

        self.source_page_id = page.identifier
        self.source_page_title = page.display_title

        errors = self.validate()

        if errors:
            raise ValueError(
                "Le modèle ne peut pas être mis à jour :\n- "
                + "\n- ".join(errors)
            )

        self.version_number += 1
        self.version_note = version_note.strip()
        self.modified = datetime.now().isoformat()

        self.save(
            create_snapshot=True,
        )

    def set_metadata(
        self,
        *,
        name: str | None = None,
        category: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        thumbnail: str | None = None,
    ) -> None:
        if name is not None:
            clean_name = name.strip()

            if not clean_name:
                raise ValueError(
                    "Le modèle doit posséder un nom."
                )

            self.name = clean_name

        if category is not None:
            self.category = category.strip()

        if description is not None:
            self.description = description.strip()

        if tags is not None:
            self.tags = self._normalize_string_list(tags)

        if thumbnail is not None:
            self.thumbnail = thumbnail.strip()

        self.modified = datetime.now().isoformat()

        self.save(
            create_snapshot=False,
        )

    # ==========================================================
    # Zones et champs
    # ==========================================================

    def get_zones(self) -> list[Zone]:
        zones: list[Zone] = []

        for element in self.page_definition.get(
            "elements",
            [],
        ):
            if not isinstance(element, dict):
                continue

            if element.get("type") != Zone.ELEMENT_TYPE:
                continue

            try:
                zones.append(
                    Zone.from_dict(element)
                )
            except (TypeError, ValueError):
                continue

        return zones

    def get_field(
        self,
        field_id: str,
    ) -> dict[str, Any] | None:
        normalized_id = field_id.strip()

        for field in self.fields:
            if field.get("identifiant") == normalized_id:
                return deepcopy(field)

        return None

    def get_fixed_zones(self) -> list[Zone]:
        return [
            zone
            for zone in self.get_zones()
            if zone.role == "fixe"
        ]

    def get_fillable_zones(self) -> list[Zone]:
        return [
            zone
            for zone in self.get_zones()
            if zone.role == "remplissable"
        ]

    # ==========================================================
    # Définition destinée à la Production
    # ==========================================================

    def production_definition(self) -> dict[str, Any]:
        """
        Retourne une copie indépendante de la structure à utiliser
        pour créer une page produite.

        Les zones de la structure sont verrouillées. Leur contenu reste
        remplissable par la Production lorsque leur rôle l'autorise.
        """
        definition = deepcopy(self.page_definition)

        for element in definition.get(
            "elements",
            [],
        ):
            if element.get("type") != Zone.ELEMENT_TYPE:
                continue

            behavior = element.setdefault(
                "comportement",
                {},
            )
            behavior["verrouillee"] = True

        return {
            "modele_identifiant": self.identifier,
            "modele_version": self.version_label,
            "definition_page": definition,
            "champs": deepcopy(self.fields),
        }

    # ==========================================================
    # Sauvegarde et versions
    # ==========================================================

    def save(
        self,
        *,
        create_snapshot: bool = False,
    ) -> None:
        if not self.is_loaded:
            return

        self.modified = datetime.now().isoformat()

        model_file = self._require_root() / "modele.json"

        with model_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                self.to_dict(),
                file,
                indent=4,
                ensure_ascii=False,
            )

        if create_snapshot:
            self._save_snapshot()

    def list_versions(self) -> list[dict[str, Any]]:
        versions_folder = self._require_root() / "versions"

        if not versions_folder.exists():
            return []

        versions: list[dict[str, Any]] = []

        for version_file in sorted(
            versions_folder.glob("version_*.json")
        ):
            try:
                with version_file.open(
                    "r",
                    encoding="utf-8",
                ) as file:
                    data = json.load(file)

                version = data.get(
                    "version_modele",
                    {},
                )

                versions.append(
                    {
                        "numero": self._safe_positive_int(
                            version.get(
                                "numero",
                                1,
                            ),
                            default=1,
                        ),
                        "note": str(
                            version.get(
                                "note",
                                "",
                            )
                        ),
                        "date": str(
                            data.get(
                                "metadonnees",
                                {},
                            ).get(
                                "modification",
                                "",
                            )
                        ),
                        "fichier": version_file.name,
                    }
                )
            except (OSError, json.JSONDecodeError):
                continue

        return versions

    def load_version(
        self,
        version_number: int,
    ) -> dict[str, Any]:
        number = self._safe_positive_int(
            version_number,
            default=0,
        )

        if number <= 0:
            raise ValueError(
                "Le numéro de version doit être supérieur à zéro."
            )

        version_file = (
            self._require_root()
            / "versions"
            / f"version_{number:04d}.json"
        )

        if not version_file.exists():
            raise FileNotFoundError(
                f"La version {number} est introuvable."
            )

        with version_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    # ==========================================================
    # Données
    # ==========================================================

    def to_summary(self) -> dict[str, Any]:
        return {
            "identifiant": self.identifier,
            "nom": self.name,
            "categorie": self.category,
            "version": self.version_label,
            "miniature": self.thumbnail,
            "nombre_zones": self.zone_count,
            "nombre_champs": self.fillable_zone_count,
            "date_creation": self.created,
            "date_modification": self.modified,
            "dossier": self.folder_name,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "identite": {
                "identifiant": self.identifier,
                "nom": self.name,
                "categorie": self.category,
                "format": self.VERSION,
            },
            "version_modele": {
                "numero": self.version_number,
                "libelle": self.version_label,
                "note": self.version_note,
            },
            "source": {
                "page_identifiant": self.source_page_id,
                "page_nom": self.source_page_title,
            },
            "metadonnees": {
                "description": self.description,
                "mots_cles": list(self.tags),
                "miniature": self.thumbnail,
                "creation": self.created,
                "modification": self.modified,
            },
            "definition_page": deepcopy(
                self.page_definition
            ),
            "champs": deepcopy(
                self.fields
            ),
        }

    # ==========================================================
    # Validation
    # ==========================================================

    def validate(self) -> list[str]:
        errors: list[str] = []

        if not self.name.strip():
            errors.append(
                "Le modèle doit posséder un nom."
            )

        if not self.page_definition:
            errors.append(
                "Le modèle ne contient aucune définition de page."
            )
            return errors

        layout = self.page_definition.get(
            "mise_en_page",
            {},
        )

        if not layout:
            errors.append(
                "Le format de page est absent."
            )

        field_ids: list[str] = []

        for zone in self.get_zones():
            if zone.role == "libre":
                errors.append(
                    f"La zone « {zone.display_name} » doit être "
                    "déclarée fixe ou remplissable."
                )

            if zone.role == "remplissable":
                if not zone.field_id:
                    errors.append(
                        f"La zone « {zone.display_name} » "
                        "ne possède aucun identifiant de champ."
                    )
                    continue

                if zone.field_id in field_ids:
                    errors.append(
                        f"L'identifiant de champ « {zone.field_id} » "
                        "est utilisé plusieurs fois."
                    )
                else:
                    field_ids.append(
                        zone.field_id
                    )

        return errors

    # ==========================================================
    # Construction interne
    # ==========================================================

    def _extract_page_definition(
        self,
        page: Page,
        *,
        auto_prepare_zones: bool,
    ) -> dict[str, Any]:
        page_data = page.to_dict()

        elements = deepcopy(
            page_data.get(
                "elements",
                [],
            )
        )

        if auto_prepare_zones:
            elements = self._prepare_zones_automatically(
                elements
            )

        return {
            "mise_en_page": deepcopy(
                page_data.get(
                    "mise_en_page",
                    {},
                )
            ),
            "editorial": {
                "type": page.page_type,
                "couleur": page.color,
                "icone": page.icon,
            },
            "contenu_fixe": deepcopy(
                page_data.get(
                    "contenu",
                    {},
                )
            ),
            "elements": elements,
        }

    def _prepare_zones_automatically(
        self,
        elements: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        prepared: list[dict[str, Any]] = []
        used_field_ids: set[str] = set()
        automatic_index = 1

        for element in elements:
            if (
                not isinstance(element, dict)
                or element.get("type") != Zone.ELEMENT_TYPE
            ):
                prepared.append(
                    deepcopy(element)
                )
                continue

            zone = Zone.from_dict(
                element
            )

            if zone.role == "libre":
                zone.set_role(
                    "remplissable"
                )

            if zone.role == "remplissable":
                field_id = zone.field_id.strip()

                if not field_id:
                    base = self._slugify(
                        zone.name
                        or f"champ_{automatic_index}"
                    )
                    field_id = base or f"champ_{automatic_index}"

                field_id = self._unique_field_id(
                    field_id,
                    used_field_ids,
                )

                zone.configure_field(
                    field_id=field_id,
                    label=(
                        zone.field_label
                        or zone.display_name
                    ),
                    required=zone.required,
                    allowed_content_types=(
                        zone.allowed_content_types
                    ),
                    allowed_sources=(
                        zone.allowed_sources
                    ),
                )

                used_field_ids.add(
                    field_id
                )
                automatic_index += 1

            prepared.append(
                zone.to_dict()
            )

        return prepared

    def _extract_fields(
        self,
        elements: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        fields: list[dict[str, Any]] = []

        for element in elements:
            if (
                not isinstance(element, dict)
                or element.get("type") != Zone.ELEMENT_TYPE
            ):
                continue

            try:
                zone = Zone.from_dict(
                    element
                )
            except (TypeError, ValueError):
                continue

            if zone.role != "remplissable":
                continue

            fields.append(
                {
                    "identifiant": zone.field_id,
                    "libelle": (
                        zone.field_label
                        or zone.display_name
                    ),
                    "zone_identifiant": zone.identifier,
                    "obligatoire": zone.required,
                    "types_contenu_autorises": list(
                        zone.allowed_content_types
                    ),
                    "sources_autorisees": list(
                        zone.allowed_sources
                    ),
                    "ordre": zone.z_index,
                }
            )

        fields.sort(
            key=lambda field: (
                field.get("ordre", 0),
                field.get("identifiant", ""),
            )
        )

        return fields

    def _save_snapshot(self) -> None:
        versions_folder = self._require_root() / "versions"
        versions_folder.mkdir(
            exist_ok=True,
        )

        version_file = (
            versions_folder
            / f"version_{self.version_number:04d}.json"
        )

        with version_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                self.to_dict(),
                file,
                indent=4,
                ensure_ascii=False,
            )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def _require_root(self) -> Path:
        if self.root is None:
            raise RuntimeError(
                "Le modèle n'a pas encore de dossier."
            )

        return self.root

    @staticmethod
    def _normalize_string_list(
        values: list[str],
    ) -> list[str]:
        normalized: list[str] = []

        for value in values:
            item = str(value).strip()

            if item and item not in normalized:
                normalized.append(item)

        return normalized

    @staticmethod
    def _safe_positive_int(
        value: Any,
        *,
        default: int,
    ) -> int:
        try:
            number = int(value)
        except (TypeError, ValueError):
            return default

        if number <= 0:
            return default

        return number

    @staticmethod
    def _slugify(
        value: str,
    ) -> str:
        normalized = value.strip().lower()
        normalized = re.sub(
            r"[^a-z0-9]+",
            "_",
            normalized,
        )
        return normalized.strip("_")

    @classmethod
    def _unique_field_id(
        cls,
        field_id: str,
        used_ids: set[str],
    ) -> str:
        base = cls._slugify(field_id) or "champ"

        if base not in used_ids:
            return base

        index = 2

        while f"{base}_{index}" in used_ids:
            index += 1

        return f"{base}_{index}"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"identifier={self.identifier!r}, "
            f"name={self.name!r}, "
            f"version={self.version_label!r}, "
            f"zones={self.zone_count}, "
            f"fields={self.fillable_zone_count})"
        )