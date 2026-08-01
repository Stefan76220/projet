from __future__ import annotations

import json
import re
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
from uuid import uuid4


class ContentItem:
    """
    Élément de contenu ordonné à placer dans une page.

    Un élément ne contient aucune mise en page. Il indique seulement :
    - sa nature ;
    - sa valeur ou sa ressource ;
    - son ordre dans la fiche ;
    - son occurrence parmi les éléments du même type ;
    - le champ du modèle auquel il peut être associé.
    """

    VERSION = "1.0"

    SOURCES = {
        "manuel",
        "bibliotheque",
        "import",
        "ia",
    }

    def __init__(
        self,
        *,
        content_type: str,
        order: int = 1,
        occurrence: int = 1,
        label: str = "",
        value: Any = None,
        resource: str = "",
        field_id: str = "",
        source: str = "manuel",
        enabled: bool = True,
    ) -> None:
        now = datetime.now().isoformat()

        self.identifier = str(uuid4())
        self.content_type = self._normalize_required_text(
            content_type,
            "type de contenu",
        )
        self.order = self._validate_positive_int(
            order,
            "ordre",
        )
        self.occurrence = self._validate_positive_int(
            occurrence,
            "occurrence",
        )

        self.label = label.strip()
        self.value = deepcopy(value)
        self.resource = resource.strip()
        self.field_id = field_id.strip()

        self.source = self._normalize_source(source)
        self.enabled = bool(enabled)

        self.metadata: dict[str, Any] = {}

        self.created = now
        self.modified = now

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def display_name(self) -> str:
        if self.label:
            return self.label

        return (
            f"{self.content_type.capitalize()} "
            f"{self.occurrence:02d}"
        )

    @property
    def has_content(self) -> bool:
        return bool(
            self.resource
            or self.value not in (None, "")
        )

    @property
    def sequence_label(self) -> str:
        return f"{self.order:03d}"

    @property
    def occurrence_label(self) -> str:
        return f"{self.occurrence:02d}"

    # ==========================================================
    # Modification
    # ==========================================================

    def set_content(
        self,
        *,
        value: Any = None,
        resource: str = "",
        source: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        self.value = deepcopy(value)
        self.resource = resource.strip()

        if source is not None:
            self.source = self._normalize_source(source)

        if metadata is not None:
            self.metadata = deepcopy(metadata)

        self._touch()

    def set_field(
        self,
        field_id: str,
    ) -> None:
        self.field_id = field_id.strip()
        self._touch()

    def set_enabled(
        self,
        enabled: bool,
    ) -> None:
        self.enabled = bool(enabled)
        self._touch()

    def set_order(
        self,
        order: int,
    ) -> None:
        self.order = self._validate_positive_int(
            order,
            "ordre",
        )
        self._touch()

    def set_occurrence(
        self,
        occurrence: int,
    ) -> None:
        self.occurrence = self._validate_positive_int(
            occurrence,
            "occurrence",
        )
        self._touch()

    # ==========================================================
    # Duplication
    # ==========================================================

    def clone(self) -> ContentItem:
        clone = ContentItem.from_dict(
            self.to_dict()
        )

        now = datetime.now().isoformat()

        clone.identifier = str(uuid4())
        clone.label = self._copy_name(
            self.display_name
        )
        clone.created = now
        clone.modified = now

        return clone

    # ==========================================================
    # Sérialisation
    # ==========================================================

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.VERSION,
            "identifiant": self.identifier,
            "ordre": self.order,
            "occurrence": self.occurrence,
            "type": self.content_type,
            "libelle": self.label,
            "champ_cible": self.field_id,
            "actif": self.enabled,
            "source": self.source,
            "valeur": deepcopy(self.value),
            "ressource": self.resource,
            "metadonnees": deepcopy(self.metadata),
            "date_creation": self.created,
            "date_modification": self.modified,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> ContentItem:
        item = cls(
            content_type=str(
                data.get(
                    "type",
                    "contenu",
                )
            ),
            order=cls._safe_positive_int(
                data.get(
                    "ordre",
                    1,
                ),
                default=1,
            ),
            occurrence=cls._safe_positive_int(
                data.get(
                    "occurrence",
                    1,
                ),
                default=1,
            ),
            label=str(
                data.get(
                    "libelle",
                    "",
                )
            ),
            value=deepcopy(
                data.get(
                    "valeur"
                )
            ),
            resource=str(
                data.get(
                    "ressource",
                    "",
                )
            ),
            field_id=str(
                data.get(
                    "champ_cible",
                    "",
                )
            ),
            source=str(
                data.get(
                    "source",
                    "manuel",
                )
            ),
            enabled=bool(
                data.get(
                    "actif",
                    True,
                )
            ),
        )

        item.identifier = str(
            data.get(
                "identifiant",
                str(uuid4()),
            )
        )
        item.metadata = deepcopy(
            data.get(
                "metadonnees",
                {},
            )
        )
        item.created = str(
            data.get(
                "date_creation",
                item.created,
            )
        )
        item.modified = str(
            data.get(
                "date_modification",
                item.modified,
            )
        )

        return item

    # ==========================================================
    # Validation
    # ==========================================================

    def validate(self) -> list[str]:
        errors: list[str] = []

        if not self.content_type:
            errors.append(
                "Le type de contenu est obligatoire."
            )

        if self.order <= 0:
            errors.append(
                "L'ordre doit être supérieur à zéro."
            )

        if self.occurrence <= 0:
            errors.append(
                "L'occurrence doit être supérieure à zéro."
            )

        return errors

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def _touch(self) -> None:
        self.modified = datetime.now().isoformat()

    @classmethod
    def _normalize_source(
        cls,
        source: str,
    ) -> str:
        normalized = str(source).strip().lower()

        if normalized not in cls.SOURCES:
            raise ValueError(
                f"Source de contenu inconnue : {source}"
            )

        return normalized

    @staticmethod
    def _normalize_required_text(
        value: str,
        label: str,
    ) -> str:
        normalized = str(value).strip().lower()

        if not normalized:
            raise ValueError(
                f"Le {label} est obligatoire."
            )

        return normalized

    @staticmethod
    def _validate_positive_int(
        value: int,
        label: str,
    ) -> int:
        if isinstance(value, bool):
            raise TypeError(
                f"{label.capitalize()} doit être un entier."
            )

        try:
            number = int(value)
        except (TypeError, ValueError) as error:
            raise TypeError(
                f"{label.capitalize()} doit être un entier."
            ) from error

        if number <= 0:
            raise ValueError(
                f"{label.capitalize()} doit être supérieur à zéro."
            )

        return number

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
    def _copy_name(
        name: str,
    ) -> str:
        clean_name = name.strip() or "Élément"

        if clean_name.endswith(" (copie)"):
            return clean_name

        return f"{clean_name} (copie)"

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"identifier={self.identifier!r}, "
            f"type={self.content_type!r}, "
            f"order={self.order}, "
            f"occurrence={self.occurrence}, "
            f"field={self.field_id!r})"
        )


class ContentSheet:
    """
    Fiche de contenu indépendante de la mise en page.

    Elle contient une liste ordonnée d'éléments pouvant être associée
    à une page unique ou à un modèle réutilisable.
    """

    VERSION = "1.0"

    def __init__(self) -> None:
        # Identité
        self.identifier = str(uuid4())
        self.name = ""
        self.category = ""
        self.description = ""
        self.tags: list[str] = []

        # Ordre dans une collection ou une production en série
        self.sheet_order = 1

        # Liaison éventuelle
        self.preferred_model_id = ""

        # Origine
        self.source = "manuel"
        self.source_reference = ""

        # Contenu
        self.items: list[ContentItem] = []

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
        slug = self._slugify(
            self.name or "fiche"
        )
        return f"{slug}_{self.identifier[:8]}"

    @property
    def item_count(self) -> int:
        return len(self.items)

    @property
    def active_item_count(self) -> int:
        return len(
            self.get_items(
                enabled_only=True
            )
        )

    # ==========================================================
    # Création
    # ==========================================================

    def create(
        self,
        sheets_folder: str | Path,
        name: str,
        *,
        category: str = "",
        description: str = "",
        sheet_order: int = 1,
        source: str = "manuel",
        source_reference: str = "",
    ) -> Path:
        clean_name = name.strip()

        if not clean_name:
            raise ValueError(
                "La fiche doit posséder un nom."
            )

        self.name = clean_name
        self.category = category.strip()
        self.description = description.strip()
        self.sheet_order = self._validate_positive_int(
            sheet_order,
            "ordre de la fiche",
        )
        self.source = ContentItem._normalize_source(
            source
        )
        self.source_reference = source_reference.strip()

        now = datetime.now().isoformat()
        self.created = now
        self.modified = now

        self.root = Path(sheets_folder) / self.folder_name

        self._require_root().mkdir(
            parents=True,
            exist_ok=False,
        )

        self.save()

        return self._require_root()

    # ==========================================================
    # Chargement
    # ==========================================================

    def load(
        self,
        folder: str | Path,
    ) -> ContentSheet:
        self.root = Path(folder)

        sheet_file = self._require_root() / "fiche.json"

        if not sheet_file.exists():
            raise FileNotFoundError(
                "Le fichier fiche.json est introuvable."
            )

        with sheet_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        identity = data.get(
            "identite",
            {},
        )
        metadata = data.get(
            "metadonnees",
            {},
        )
        source = data.get(
            "source",
            {},
        )

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
        self.sheet_order = self._safe_positive_int(
            identity.get(
                "ordre",
                1,
            ),
            default=1,
        )
        self.preferred_model_id = str(
            identity.get(
                "modele_prefere",
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

        self.source = ContentItem._normalize_source(
            source.get(
                "type",
                "manuel",
            )
        )
        self.source_reference = str(
            source.get(
                "reference",
                "",
            )
        )

        self.items = []

        for item_data in data.get(
            "elements",
            [],
        ):
            if not isinstance(item_data, dict):
                continue

            try:
                self.items.append(
                    ContentItem.from_dict(
                        item_data
                    )
                )
            except (TypeError, ValueError):
                continue

        self._sort_items()
        self._normalize_orders()

        return self

    # ==========================================================
    # Métadonnées
    # ==========================================================

    def set_metadata(
        self,
        *,
        name: str | None = None,
        category: str | None = None,
        description: str | None = None,
        tags: list[str] | None = None,
        sheet_order: int | None = None,
        preferred_model_id: str | None = None,
    ) -> None:
        if name is not None:
            clean_name = name.strip()

            if not clean_name:
                raise ValueError(
                    "La fiche doit posséder un nom."
                )

            self.name = clean_name

        if category is not None:
            self.category = category.strip()

        if description is not None:
            self.description = description.strip()

        if tags is not None:
            self.tags = self._normalize_string_list(
                tags
            )

        if sheet_order is not None:
            self.sheet_order = self._validate_positive_int(
                sheet_order,
                "ordre de la fiche",
            )

        if preferred_model_id is not None:
            self.preferred_model_id = (
                preferred_model_id.strip()
            )

        self.save()

    # ==========================================================
    # Gestion des éléments
    # ==========================================================

    def add_item(
        self,
        *,
        content_type: str,
        value: Any = None,
        resource: str = "",
        label: str = "",
        field_id: str = "",
        source: str = "manuel",
        enabled: bool = True,
        order: int | None = None,
        occurrence: int | None = None,
        metadata: dict[str, Any] | None = None,
        save: bool = True,
    ) -> ContentItem:
        item_order = (
            self.item_count + 1
            if order is None
            else self._validate_positive_int(
                order,
                "ordre",
            )
        )

        normalized_type = str(
            content_type
        ).strip().lower()

        item_occurrence = (
            self._next_occurrence(
                normalized_type
            )
            if occurrence is None
            else self._validate_positive_int(
                occurrence,
                "occurrence",
            )
        )

        item = ContentItem(
            content_type=normalized_type,
            order=item_order,
            occurrence=item_occurrence,
            label=label,
            value=value,
            resource=resource,
            field_id=field_id,
            source=source,
            enabled=enabled,
        )

        if metadata is not None:
            item.metadata = deepcopy(
                metadata
            )

        self.items.append(
            item
        )

        self._sort_items()
        self._normalize_orders()
        self._normalize_occurrences(
            normalized_type
        )

        if save:
            self.save()

        return item

    def get_items(
        self,
        *,
        enabled_only: bool = False,
        content_type: str | None = None,
    ) -> list[ContentItem]:
        normalized_type = (
            content_type.strip().lower()
            if content_type is not None
            else None
        )

        items = [
            item
            for item in self.items
            if (
                (not enabled_only or item.enabled)
                and (
                    normalized_type is None
                    or item.content_type == normalized_type
                )
            )
        ]

        return [
            ContentItem.from_dict(
                item.to_dict()
            )
            for item in items
        ]

    def get_item(
        self,
        identifier: str,
    ) -> ContentItem | None:
        for item in self.items:
            if item.identifier == identifier:
                return ContentItem.from_dict(
                    item.to_dict()
                )

        return None

    def update_item(
        self,
        item: ContentItem,
        *,
        save: bool = True,
    ) -> None:
        if not isinstance(item, ContentItem):
            raise TypeError(
                "L'élément doit être une instance de ContentItem."
            )

        for index, existing in enumerate(self.items):
            if existing.identifier != item.identifier:
                continue

            previous_type = existing.content_type
            self.items[index] = ContentItem.from_dict(
                item.to_dict()
            )

            self._sort_items()
            self._normalize_orders()
            self._normalize_occurrences(
                previous_type
            )
            self._normalize_occurrences(
                item.content_type
            )

            if save:
                self.save()

            return

        raise KeyError(
            f"Élément introuvable : {item.identifier}"
        )

    def remove_item(
        self,
        identifier: str,
        *,
        save: bool = True,
    ) -> ContentItem | None:
        for index, item in enumerate(self.items):
            if item.identifier != identifier:
                continue

            removed = self.items.pop(
                index
            )
            removed_type = removed.content_type

            self._normalize_orders()
            self._normalize_occurrences(
                removed_type
            )

            if save:
                self.save()

            return removed

        return None

    def duplicate_item(
        self,
        identifier: str,
        *,
        save: bool = True,
    ) -> ContentItem | None:
        for index, item in enumerate(self.items):
            if item.identifier != identifier:
                continue

            duplicate = item.clone()
            duplicate.order = item.order + 1

            self.items.insert(
                index + 1,
                duplicate,
            )

            self._normalize_orders()
            self._normalize_occurrences(
                duplicate.content_type
            )

            if save:
                self.save()

            return ContentItem.from_dict(
                duplicate.to_dict()
            )

        return None

    def reorder_item(
        self,
        identifier: str,
        new_position: int,
        *,
        save: bool = True,
    ) -> None:
        position = self._validate_positive_int(
            new_position,
            "nouvelle position",
        )

        if not self.items:
            return

        target_index = min(
            position - 1,
            len(self.items) - 1,
        )

        current_index = None

        for index, item in enumerate(self.items):
            if item.identifier == identifier:
                current_index = index
                break

        if current_index is None:
            raise KeyError(
                f"Élément introuvable : {identifier}"
            )

        item = self.items.pop(
            current_index
        )
        self.items.insert(
            target_index,
            item,
        )

        self._normalize_orders()

        if save:
            self.save()

    def set_item_enabled(
        self,
        identifier: str,
        enabled: bool,
        *,
        save: bool = True,
    ) -> None:
        for item in self.items:
            if item.identifier != identifier:
                continue

            item.set_enabled(
                enabled
            )

            if save:
                self.save()

            return

        raise KeyError(
            f"Élément introuvable : {identifier}"
        )

    # ==========================================================
    # Import et export de lignes
    # ==========================================================

    def import_rows(
        self,
        rows: Iterable[dict[str, Any]],
        *,
        replace_existing: bool = False,
        save: bool = True,
    ) -> None:
        if replace_existing:
            self.items.clear()

        for row in rows:
            if not isinstance(row, dict):
                continue

            content_type = str(
                row.get(
                    "type",
                    "",
                )
            ).strip()

            if not content_type:
                continue

            self.add_item(
                content_type=content_type,
                value=deepcopy(
                    row.get(
                        "contenu",
                        row.get(
                            "valeur"
                        ),
                    )
                ),
                resource=str(
                    row.get(
                        "ressource",
                        "",
                    )
                ),
                label=str(
                    row.get(
                        "libelle",
                        "",
                    )
                ),
                field_id=str(
                    row.get(
                        "champ_cible",
                        row.get(
                            "zone_cible",
                            "",
                        ),
                    )
                ),
                source=str(
                    row.get(
                        "source",
                        "import",
                    )
                ),
                enabled=bool(
                    row.get(
                        "actif",
                        True,
                    )
                ),
                order=self._safe_optional_positive_int(
                    row.get(
                        "ordre_element"
                    )
                ),
                occurrence=self._safe_optional_positive_int(
                    row.get(
                        "occurrence"
                    )
                ),
                metadata=deepcopy(
                    row.get(
                        "metadonnees",
                        {},
                    )
                ),
                save=False,
            )

        self._sort_items()
        self._normalize_orders()
        self._normalize_all_occurrences()

        if save:
            self.save()

    def to_rows(self) -> list[dict[str, Any]]:
        return [
            {
                "fiche_id": self.identifier,
                "ordre_fiche": self.sheet_order,
                "ordre_element": item.order,
                "type": item.content_type,
                "occurrence": item.occurrence,
                "libelle": item.label,
                "champ_cible": item.field_id,
                "actif": item.enabled,
                "source": item.source,
                "contenu": deepcopy(
                    item.value
                ),
                "ressource": item.resource,
                "metadonnees": deepcopy(
                    item.metadata
                ),
            }
            for item in self.items
        ]

    # ==========================================================
    # Association avec un modèle
    # ==========================================================

    def validate_against_fields(
        self,
        model_fields: Iterable[dict[str, Any]],
    ) -> list[str]:
        errors: list[str] = []

        fields = [
            dict(field)
            for field in model_fields
            if isinstance(field, dict)
        ]

        known_field_ids = {
            str(
                field.get(
                    "identifiant",
                    "",
                )
            ).strip()
            for field in fields
            if str(
                field.get(
                    "identifiant",
                    "",
                )
            ).strip()
        }

        required_field_ids = {
            str(
                field.get(
                    "identifiant",
                    "",
                )
            ).strip()
            for field in fields
            if bool(
                field.get(
                    "obligatoire",
                    False,
                )
            )
        }

        active_items = self.get_items(
            enabled_only=True
        )

        used_field_ids = {
            item.field_id
            for item in active_items
            if item.field_id
        }

        unknown_field_ids = (
            used_field_ids - known_field_ids
        )

        for field_id in sorted(
            unknown_field_ids
        ):
            errors.append(
                f"Le champ cible « {field_id} » "
                "n'existe pas dans le modèle."
            )

        missing_required = (
            required_field_ids - used_field_ids
        )

        for field_id in sorted(
            missing_required
        ):
            errors.append(
                f"Le champ obligatoire « {field_id} » "
                "ne possède aucun contenu actif."
            )

        return errors

    def production_payload(
        self,
    ) -> dict[str, Any]:
        return {
            "fiche_identifiant": self.identifier,
            "fiche_nom": self.name,
            "ordre_fiche": self.sheet_order,
            "modele_prefere": self.preferred_model_id,
            "elements": [
                item.to_dict()
                for item in self.items
                if item.enabled
            ],
        }

    # ==========================================================
    # Sauvegarde
    # ==========================================================

    def save(self) -> None:
        if not self.is_loaded:
            return

        self.modified = datetime.now().isoformat()

        sheet_file = self._require_root() / "fiche.json"

        with sheet_file.open(
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
    # Données
    # ==========================================================

    def to_summary(self) -> dict[str, Any]:
        return {
            "identifiant": self.identifier,
            "nom": self.name,
            "categorie": self.category,
            "ordre": self.sheet_order,
            "nombre_elements": self.item_count,
            "nombre_elements_actifs": self.active_item_count,
            "modele_prefere": self.preferred_model_id,
            "dossier": self.folder_name,
            "date_creation": self.created,
            "date_modification": self.modified,
        }

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.VERSION,
            "identite": {
                "identifiant": self.identifier,
                "nom": self.name,
                "categorie": self.category,
                "ordre": self.sheet_order,
                "modele_prefere": self.preferred_model_id,
            },
            "source": {
                "type": self.source,
                "reference": self.source_reference,
            },
            "metadonnees": {
                "description": self.description,
                "mots_cles": list(
                    self.tags
                ),
                "creation": self.created,
                "modification": self.modified,
            },
            "elements": [
                item.to_dict()
                for item in self.items
            ],
        }

    # ==========================================================
    # Validation
    # ==========================================================

    def validate(self) -> list[str]:
        errors: list[str] = []

        if not self.name.strip():
            errors.append(
                "La fiche doit posséder un nom."
            )

        identifiers: set[str] = set()
        occurrences: set[tuple[str, int]] = set()

        for item in self.items:
            for error in item.validate():
                errors.append(
                    f"{item.display_name} : {error}"
                )

            if item.identifier in identifiers:
                errors.append(
                    f"L'identifiant d'élément "
                    f"« {item.identifier} » est utilisé plusieurs fois."
                )
            else:
                identifiers.add(
                    item.identifier
                )

            occurrence_key = (
                item.content_type,
                item.occurrence,
            )

            if occurrence_key in occurrences:
                errors.append(
                    f"L'occurrence {item.occurrence} du type "
                    f"« {item.content_type} » est utilisée plusieurs fois."
                )
            else:
                occurrences.add(
                    occurrence_key
                )

        expected_orders = list(
            range(
                1,
                self.item_count + 1,
            )
        )
        actual_orders = [
            item.order
            for item in self.items
        ]

        if actual_orders != expected_orders:
            errors.append(
                "L'ordre des éléments n'est pas continu."
            )

        return errors

    # ==========================================================
    # Normalisation interne
    # ==========================================================

    def _sort_items(self) -> None:
        self.items.sort(
            key=lambda item: (
                item.order,
                item.created,
                item.identifier,
            )
        )

    def _normalize_orders(self) -> None:
        for index, item in enumerate(
            self.items,
            start=1,
        ):
            item.order = index

    def _normalize_occurrences(
        self,
        content_type: str,
    ) -> None:
        normalized_type = str(
            content_type
        ).strip().lower()

        matching_items = [
            item
            for item in self.items
            if item.content_type == normalized_type
        ]

        matching_items.sort(
            key=lambda item: (
                item.order,
                item.identifier,
            )
        )

        for occurrence, item in enumerate(
            matching_items,
            start=1,
        ):
            item.occurrence = occurrence

    def _normalize_all_occurrences(self) -> None:
        content_types = {
            item.content_type
            for item in self.items
        }

        for content_type in content_types:
            self._normalize_occurrences(
                content_type
            )

    def _next_occurrence(
        self,
        content_type: str,
    ) -> int:
        normalized_type = str(
            content_type
        ).strip().lower()

        occurrences = [
            item.occurrence
            for item in self.items
            if item.content_type == normalized_type
        ]

        return (
            max(occurrences) + 1
            if occurrences
            else 1
        )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def _require_root(self) -> Path:
        if self.root is None:
            raise RuntimeError(
                "La fiche n'a pas encore de dossier."
            )

        return self.root

    @staticmethod
    def _validate_positive_int(
        value: int,
        label: str,
    ) -> int:
        return ContentItem._validate_positive_int(
            value,
            label,
        )

    @staticmethod
    def _safe_positive_int(
        value: Any,
        *,
        default: int,
    ) -> int:
        return ContentItem._safe_positive_int(
            value,
            default=default,
        )

    @staticmethod
    def _safe_optional_positive_int(
        value: Any,
    ) -> int | None:
        if value in (None, ""):
            return None

        try:
            number = int(value)
        except (TypeError, ValueError):
            return None

        if number <= 0:
            return None

        return number

    @staticmethod
    def _normalize_string_list(
        values: list[str],
    ) -> list[str]:
        normalized: list[str] = []

        for value in values:
            item = str(value).strip()

            if item and item not in normalized:
                normalized.append(
                    item
                )

        return normalized

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

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"identifier={self.identifier!r}, "
            f"name={self.name!r}, "
            f"order={self.sheet_order}, "
            f"items={self.item_count})"
        )


class ContentCollection:
    """
    Collection ordonnée de fiches destinée à la production en série.

    Elle référence des fiches conservées individuellement. Elle ne copie
    pas leur contenu, ce qui évite les doublons et permet de corriger une
    fiche avant de relancer une production.
    """

    VERSION = "1.0"

    def __init__(self) -> None:
        self.identifier = str(uuid4())
        self.name = ""
        self.description = ""
        self.preferred_model_id = ""

        self.sheets: list[dict[str, Any]] = []

        self.created = ""
        self.modified = ""

        self.root: Path | None = None

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def is_loaded(self) -> bool:
        return self.root is not None

    @property
    def folder_name(self) -> str:
        slug = ContentSheet._slugify(
            self.name or "collection"
        )
        return f"{slug}_{self.identifier[:8]}"

    @property
    def sheet_count(self) -> int:
        return len(self.sheets)

    # ==========================================================
    # Création et chargement
    # ==========================================================

    def create(
        self,
        collections_folder: str | Path,
        name: str,
        *,
        description: str = "",
        preferred_model_id: str = "",
    ) -> Path:
        clean_name = name.strip()

        if not clean_name:
            raise ValueError(
                "La collection doit posséder un nom."
            )

        self.name = clean_name
        self.description = description.strip()
        self.preferred_model_id = (
            preferred_model_id.strip()
        )

        now = datetime.now().isoformat()
        self.created = now
        self.modified = now

        self.root = (
            Path(collections_folder)
            / self.folder_name
        )

        self._require_root().mkdir(
            parents=True,
            exist_ok=False,
        )

        self.save()

        return self._require_root()

    def load(
        self,
        folder: str | Path,
    ) -> ContentCollection:
        self.root = Path(folder)

        collection_file = (
            self._require_root()
            / "collection.json"
        )

        if not collection_file.exists():
            raise FileNotFoundError(
                "Le fichier collection.json est introuvable."
            )

        with collection_file.open(
            "r",
            encoding="utf-8",
        ) as file:
            data = json.load(file)

        identity = data.get(
            "identite",
            {},
        )
        metadata = data.get(
            "metadonnees",
            {},
        )

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
        self.preferred_model_id = str(
            identity.get(
                "modele_prefere",
                "",
            )
        )

        self.description = str(
            metadata.get(
                "description",
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

        self.sheets = [
            dict(sheet)
            for sheet in data.get(
                "fiches",
                [],
            )
            if isinstance(sheet, dict)
        ]

        self._normalize_orders()

        return self

    # ==========================================================
    # Gestion des fiches
    # ==========================================================

    def add_sheet(
        self,
        sheet: ContentSheet,
        *,
        save: bool = True,
    ) -> None:
        if not isinstance(
            sheet,
            ContentSheet,
        ):
            raise TypeError(
                "La fiche doit être une instance de ContentSheet."
            )

        if any(
            entry.get("identifiant")
            == sheet.identifier
            for entry in self.sheets
        ):
            raise ValueError(
                "Cette fiche appartient déjà à la collection."
            )

        self.sheets.append(
            {
                "identifiant": sheet.identifier,
                "nom": sheet.name,
                "ordre": len(self.sheets) + 1,
                "dossier": (
                    str(sheet.root)
                    if sheet.root is not None
                    else ""
                ),
                "actif": True,
            }
        )

        if save:
            self.save()

    def remove_sheet(
        self,
        identifier: str,
        *,
        save: bool = True,
    ) -> dict[str, Any] | None:
        for index, entry in enumerate(
            self.sheets
        ):
            if (
                entry.get("identifiant")
                != identifier
            ):
                continue

            removed = self.sheets.pop(
                index
            )
            self._normalize_orders()

            if save:
                self.save()

            return removed

        return None

    def reorder_sheet(
        self,
        identifier: str,
        new_position: int,
        *,
        save: bool = True,
    ) -> None:
        position = ContentSheet._validate_positive_int(
            new_position,
            "nouvelle position",
        )

        current_index = None

        for index, entry in enumerate(
            self.sheets
        ):
            if (
                entry.get("identifiant")
                == identifier
            ):
                current_index = index
                break

        if current_index is None:
            raise KeyError(
                f"Fiche introuvable : {identifier}"
            )

        target_index = min(
            position - 1,
            len(self.sheets) - 1,
        )

        entry = self.sheets.pop(
            current_index
        )
        self.sheets.insert(
            target_index,
            entry,
        )

        self._normalize_orders()

        if save:
            self.save()

    def set_sheet_enabled(
        self,
        identifier: str,
        enabled: bool,
        *,
        save: bool = True,
    ) -> None:
        for entry in self.sheets:
            if (
                entry.get("identifiant")
                != identifier
            ):
                continue

            entry["actif"] = bool(
                enabled
            )

            if save:
                self.save()

            return

        raise KeyError(
            f"Fiche introuvable : {identifier}"
        )

    # ==========================================================
    # Production
    # ==========================================================

    def production_manifest(
        self,
    ) -> dict[str, Any]:
        return {
            "collection_identifiant": self.identifier,
            "collection_nom": self.name,
            "modele_prefere": self.preferred_model_id,
            "fiches": [
                deepcopy(entry)
                for entry in self.sheets
                if bool(
                    entry.get(
                        "actif",
                        True,
                    )
                )
            ],
        }

    # ==========================================================
    # Sauvegarde
    # ==========================================================

    def save(self) -> None:
        if not self.is_loaded:
            return

        self.modified = datetime.now().isoformat()

        collection_file = (
            self._require_root()
            / "collection.json"
        )

        with collection_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                self.to_dict(),
                file,
                indent=4,
                ensure_ascii=False,
            )

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.VERSION,
            "identite": {
                "identifiant": self.identifier,
                "nom": self.name,
                "modele_prefere": self.preferred_model_id,
            },
            "metadonnees": {
                "description": self.description,
                "creation": self.created,
                "modification": self.modified,
            },
            "fiches": deepcopy(
                self.sheets
            ),
        }

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def _normalize_orders(self) -> None:
        self.sheets.sort(
            key=lambda entry: (
                int(
                    entry.get(
                        "ordre",
                        0,
                    )
                ),
                str(
                    entry.get(
                        "nom",
                        "",
                    )
                ),
            )
        )

        for index, entry in enumerate(
            self.sheets,
            start=1,
        ):
            entry["ordre"] = index

    def _require_root(self) -> Path:
        if self.root is None:
            raise RuntimeError(
                "La collection n'a pas encore de dossier."
            )

        return self.root

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"identifier={self.identifier!r}, "
            f"name={self.name!r}, "
            f"sheets={self.sheet_count})"
        )