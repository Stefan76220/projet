from __future__ import annotations

import shutil
from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any

from src.core.content_sheet import ContentItem, ContentSheet
from src.core.document import Document
from src.core.model import Model
from src.core.page import Page
from src.core.zone import Zone


class ProductionError(RuntimeError):
    """
    Erreur empêchant la création d'une page produite.
    """


@dataclass
class ProductionResult:
    """
    Résultat d'une production unitaire.
    """

    page: Page
    filled_fields: list[str] = field(default_factory=list)
    automatic_mappings: list[dict[str, str]] = field(default_factory=list)
    ignored_items: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_summary(self) -> dict[str, Any]:
        return {
            "page_identifiant": self.page.identifier,
            "page_numero": self.page.number,
            "page_nom": self.page.display_title,
            "modele_identifiant": self.page.source_model_id,
            "version_modele": self.page.source_model_version,
            "fiche_identifiant": self.page.source_content_id,
            "champs_remplis": list(self.filled_fields),
            "associations_automatiques": deepcopy(
                self.automatic_mappings
            ),
            "elements_ignores": deepcopy(
                self.ignored_items
            ),
            "avertissements": list(self.warnings),
        }


class ProductionEngine:
    """
    Associe un modèle et une fiche de contenu pour produire une page.

    Première étape prise en charge :
        1 modèle + 1 fiche = 1 page produite.

    La structure issue du modèle est verrouillée.
    Le contenu reste modifiable dans l'espace Production.
    """

    MAPPING_MODES = {
        "explicite",
        "automatique",
    }

    def produce_page(
        self,
        document: Document,
        model: Model,
        sheet: ContentSheet,
        *,
        title: str | None = None,
        mapping_mode: str = "automatique",
    ) -> ProductionResult:
        self._validate_inputs(
            document=document,
            model=model,
            sheet=sheet,
        )

        normalized_mapping_mode = self._normalize_mapping_mode(
            mapping_mode
        )

        model_errors = model.validate()

        if model_errors:
            raise ProductionError(
                "Le modèle ne peut pas être utilisé :\n- "
                + "\n- ".join(model_errors)
            )

        sheet_errors = sheet.validate()

        if sheet_errors:
            raise ProductionError(
                "La fiche de contenu est invalide :\n- "
                + "\n- ".join(sheet_errors)
            )

        production_definition = model.production_definition()
        page_definition = deepcopy(
            production_definition["definition_page"]
        )
        model_fields = deepcopy(
            production_definition["champs"]
        )

        (
            assignments,
            automatic_mappings,
            ignored_items,
            warnings,
        ) = self._build_assignments(
            sheet=sheet,
            model_fields=model_fields,
            mapping_mode=normalized_mapping_mode,
        )

        validation_errors = self._validate_assignments(
            assignments=assignments,
            model_fields=model_fields,
        )

        if validation_errors:
            raise ProductionError(
                "La fiche ne peut pas remplir ce modèle :\n- "
                + "\n- ".join(validation_errors)
            )

        editorial = page_definition.get(
            "editorial",
            {},
        )

        page_type = str(
            editorial.get(
                "type",
                "Page produite",
            )
        ).strip() or "Page produite"

        page = document.add_page(
            page_type=page_type,
        )

        try:
            self._apply_page_definition(
                page=page,
                page_definition=page_definition,
                model=model,
                sheet=sheet,
                title=title,
                assignments=assignments,
            )

            page.save(
                update_history=False,
            )
            document.update_page_summary(
                page
            )

        except Exception:
            self._rollback_page_creation(
                document=document,
                page=page,
            )
            raise

        return ProductionResult(
            page=page,
            filled_fields=[
                assignment["field_id"]
                for assignment in assignments
            ],
            automatic_mappings=automatic_mappings,
            ignored_items=ignored_items,
            warnings=warnings,
        )

    # ==========================================================
    # Association des contenus aux champs
    # ==========================================================

    def _build_assignments(
        self,
        *,
        sheet: ContentSheet,
        model_fields: list[dict[str, Any]],
        mapping_mode: str,
    ) -> tuple[
        list[dict[str, Any]],
        list[dict[str, str]],
        list[dict[str, Any]],
        list[str],
    ]:
        fields_by_id = {
            str(field.get("identifiant", "")).strip(): dict(field)
            for field in model_fields
            if str(field.get("identifiant", "")).strip()
        }

        ordered_fields = sorted(
            fields_by_id.values(),
            key=lambda item: (
                int(item.get("ordre", 0)),
                str(item.get("identifiant", "")),
            ),
        )

        used_fields: set[str] = set()
        assignments: list[dict[str, Any]] = []
        automatic_mappings: list[dict[str, str]] = []
        ignored_items: list[dict[str, Any]] = []
        warnings: list[str] = []

        active_items = sheet.get_items(
            enabled_only=True
        )

        for item in active_items:
            requested_field_id = item.field_id.strip()

            if requested_field_id:
                if requested_field_id not in fields_by_id:
                    raise ProductionError(
                        f"L'élément « {item.display_name} » cible "
                        f"le champ inconnu « {requested_field_id} »."
                    )

                if requested_field_id in used_fields:
                    raise ProductionError(
                        f"Plusieurs éléments ciblent le champ "
                        f"« {requested_field_id} »."
                    )

                field_definition = fields_by_id[
                    requested_field_id
                ]

                self._ensure_type_allowed(
                    item=item,
                    field_definition=field_definition,
                )

                assignments.append(
                    self._assignment(
                        item=item,
                        field_definition=field_definition,
                    )
                )
                used_fields.add(
                    requested_field_id
                )
                continue

            if mapping_mode == "explicite":
                ignored_items.append(
                    item.to_dict()
                )
                warnings.append(
                    f"« {item.display_name} » a été ignoré : "
                    "aucun champ cible n'est indiqué."
                )
                continue

            field_definition = self._find_automatic_field(
                item=item,
                ordered_fields=ordered_fields,
                used_fields=used_fields,
            )

            if field_definition is None:
                ignored_items.append(
                    item.to_dict()
                )
                warnings.append(
                    f"« {item.display_name} » a été ignoré : "
                    "aucune zone compatible n'est disponible."
                )
                continue

            field_id = str(
                field_definition["identifiant"]
            )

            assignments.append(
                self._assignment(
                    item=item,
                    field_definition=field_definition,
                )
            )
            used_fields.add(
                field_id
            )
            automatic_mappings.append(
                {
                    "element_identifiant": item.identifier,
                    "element": item.display_name,
                    "champ": field_id,
                }
            )

        return (
            assignments,
            automatic_mappings,
            ignored_items,
            warnings,
        )

    def _find_automatic_field(
        self,
        *,
        item: ContentItem,
        ordered_fields: list[dict[str, Any]],
        used_fields: set[str],
    ) -> dict[str, Any] | None:
        compatible_fields = []

        for field_definition in ordered_fields:
            field_id = str(
                field_definition.get(
                    "identifiant",
                    "",
                )
            )

            if not field_id or field_id in used_fields:
                continue

            allowed_types = {
                str(content_type).strip().lower()
                for content_type in field_definition.get(
                    "types_contenu_autorises",
                    [],
                )
                if str(content_type).strip()
            }

            if (
                allowed_types
                and item.content_type not in allowed_types
            ):
                continue

            compatible_fields.append(
                field_definition
            )

        if not compatible_fields:
            return None

        # Les champs explicitement limités au bon type sont prioritaires.
        compatible_fields.sort(
            key=lambda field_definition: (
                0
                if field_definition.get(
                    "types_contenu_autorises"
                )
                else 1,
                int(field_definition.get("ordre", 0)),
                str(field_definition.get("identifiant", "")),
            )
        )

        return compatible_fields[0]

    def _assignment(
        self,
        *,
        item: ContentItem,
        field_definition: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "field_id": str(
                field_definition["identifiant"]
            ),
            "field_definition": deepcopy(
                field_definition
            ),
            "item": item,
        }

    # ==========================================================
    # Validation des associations
    # ==========================================================

    def _validate_assignments(
        self,
        *,
        assignments: list[dict[str, Any]],
        model_fields: list[dict[str, Any]],
    ) -> list[str]:
        errors: list[str] = []

        assigned_field_ids = {
            assignment["field_id"]
            for assignment in assignments
        }

        for field_definition in model_fields:
            field_id = str(
                field_definition.get(
                    "identifiant",
                    "",
                )
            ).strip()

            if not field_id:
                continue

            if (
                bool(field_definition.get("obligatoire", False))
                and field_id not in assigned_field_ids
            ):
                errors.append(
                    f"Le champ obligatoire « {field_id} » "
                    "ne possède aucun contenu."
                )

        return errors

    def _ensure_type_allowed(
        self,
        *,
        item: ContentItem,
        field_definition: dict[str, Any],
    ) -> None:
        allowed_types = {
            str(content_type).strip().lower()
            for content_type in field_definition.get(
                "types_contenu_autorises",
                [],
            )
            if str(content_type).strip()
        }

        if (
            allowed_types
            and item.content_type not in allowed_types
        ):
            field_id = str(
                field_definition.get(
                    "identifiant",
                    "",
                )
            )

            raise ProductionError(
                f"Le contenu « {item.display_name} » de type "
                f"« {item.content_type} » n'est pas autorisé "
                f"dans le champ « {field_id} »."
            )

    # ==========================================================
    # Construction de la page
    # ==========================================================

    def _apply_page_definition(
        self,
        *,
        page: Page,
        page_definition: dict[str, Any],
        model: Model,
        sheet: ContentSheet,
        title: str | None,
        assignments: list[dict[str, Any]],
    ) -> None:
        page.title = (
            title.strip()
            if title and title.strip()
            else sheet.name
        )

        editorial = page_definition.get(
            "editorial",
            {},
        )

        page.page_type = str(
            editorial.get(
                "type",
                page.page_type,
            )
        )
        page.color = str(
            editorial.get(
                "couleur",
                page.color,
            )
        )
        page.icon = str(
            editorial.get(
                "icone",
                page.icon,
            )
        )

        page.page_kind = "page_produite"
        page.structure_workspace = ""
        page.content_workspace = "production"
        page.locked = False

        page.source_model_id = model.identifier
        page.source_model_version = model.version_label
        page.source_content_id = sheet.identifier

        page._load_layout(
            deepcopy(
                page_definition.get(
                    "mise_en_page",
                    {},
                )
            )
        )

        page.content = deepcopy(
            page_definition.get(
                "contenu_fixe",
                {},
            )
        )

        elements = deepcopy(
            page_definition.get(
                "elements",
                [],
            )
        )

        assignments_by_field = {
            assignment["field_id"]: assignment
            for assignment in assignments
        }

        produced_elements: list[dict[str, Any]] = []

        for element in elements:
            if (
                not isinstance(element, dict)
                or element.get("type") != Zone.ELEMENT_TYPE
            ):
                produced_elements.append(
                    deepcopy(element)
                )
                continue

            zone = Zone.from_dict(
                element
            )
            zone.locked = True

            if zone.role == "remplissable":
                assignment = assignments_by_field.get(
                    zone.field_id
                )

                if assignment is not None:
                    self._fill_zone(
                        zone=zone,
                        item=assignment["item"],
                    )
                else:
                    zone.clear_content()
                    zone.locked = True

            produced_elements.append(
                zone.to_dict()
            )

        page.elements = produced_elements

        page._add_history(
            action="production",
            description=(
                f"Page produite depuis le modèle "
                f"« {model.name} » {model.version_label} "
                f"avec la fiche « {sheet.name} »."
            ),
        )

    def _fill_zone(
        self,
        *,
        zone: Zone,
        item: ContentItem,
    ) -> None:
        metadata = deepcopy(
            item.metadata
        )
        metadata.update(
            {
                "element_identifiant": item.identifier,
                "ordre": item.order,
                "occurrence": item.occurrence,
                "libelle": item.label,
                "fiche_source": True,
            }
        )

        zone.set_content(
            content_type=item.content_type,
            value=deepcopy(item.value),
            resource=item.resource,
            source=item.source,
            metadata=metadata,
        )
        zone.locked = True

    # ==========================================================
    # Sécurité et retour arrière
    # ==========================================================

    def _validate_inputs(
        self,
        *,
        document: Document,
        model: Model,
        sheet: ContentSheet,
    ) -> None:
        if not isinstance(document, Document):
            raise TypeError(
                "Le document doit être une instance de Document."
            )

        if not document.is_loaded:
            raise ProductionError(
                "Le document de destination n'est pas chargé."
            )

        if not isinstance(model, Model):
            raise TypeError(
                "Le modèle doit être une instance de Model."
            )

        if not isinstance(sheet, ContentSheet):
            raise TypeError(
                "La fiche doit être une instance de ContentSheet."
            )

    def _rollback_page_creation(
        self,
        *,
        document: Document,
        page: Page,
    ) -> None:
        page_root = page.root

        document.pages = [
            page_info
            for page_info in document.pages
            if (
                page_info.get("identifiant")
                != page.identifier
                and page_info.get("numero")
                != page.number
            )
        ]

        document.save()

        if page_root is not None and page_root.exists():
            shutil.rmtree(
                page_root,
                ignore_errors=True,
            )

    @classmethod
    def _normalize_mapping_mode(
        cls,
        mapping_mode: str,
    ) -> str:
        normalized = str(
            mapping_mode
        ).strip().lower()

        if normalized not in cls.MAPPING_MODES:
            raise ValueError(
                f"Mode d'association inconnu : {mapping_mode}"
            )

        return normalized