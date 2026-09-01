from __future__ import annotations

"""
TomeLinea V4 — modèles de Composition.

Un modèle n'est pas une seconde version du Livre.
Il décrit un ensemble réutilisable d'éléments de Composition.

Principes :
- modèle = UUID stable ;
- éléments du modèle = UUID stables ;
- chaque page reçoit de vraies copies ;
- chaque copie possède son propre UUID ;
- la correspondance modèle/copie est mémorisée ;
- une propagation conserve l'UUID des copies déjà existantes ;
- une page peut être détachée et devenir une exception locale ;
- un modèle lié à un type est hérité par les nouvelles pages de ce type.
"""

from copy import deepcopy
from dataclasses import dataclass, fields
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from src.v4.domain import (
    BookV4,
    PageV4,
)

from src.v4.composition import (
    COMPOSITION_SCHEMA,
    validate_element,
)


MODEL_SCHEMA = "tomelinea-composition-model"
MODEL_VERSION = 1

TYPE_BINDINGS_KEY = (
    "composition_model_by_type"
)

MODEL_ID_KEY = (
    "composition_model_id"
)

MODEL_ELEMENT_ID_KEY = (
    "composition_model_element_id"
)

DETACHED_TYPE_KEY = (
    "composition_model_detached_for_type"
)


@dataclass(frozen=True, slots=True)
class ModelApplyResult:
    model_id: str
    page_id: str
    reused_elements: int
    created_elements: int
    removed_elements: int


@dataclass(frozen=True, slots=True)
class ModelPropagationResult:
    model_id: str
    page_type: str
    applied_pages: int


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def new_id() -> str:
    return str(
        uuid4()
    )


def _restore_book(
    book: BookV4,
    snapshot: BookV4,
) -> None:

    for field_info in fields(
        BookV4
    ):
        setattr(
            book,
            field_info.name,
            deepcopy(
                getattr(
                    snapshot,
                    field_info.name,
                )
            ),
        )


def _page(
    book: BookV4,
    page_id: str,
) -> PageV4:

    page = book.pages.get(
        page_id
    )

    if page is None:
        raise KeyError(
            page_id
        )

    return page


def _page_type(
    page: PageV4,
) -> str:

    value = str(
        page.page_type or ""
    ).strip().lower()

    if not value:
        raise ValueError(
            "Le type de page est vide."
        )

    return value


def _is_composition_element(
    value: Any,
) -> bool:

    return (
        isinstance(
            value,
            dict,
        )
        and value.get(
            "schema"
        ) == COMPOSITION_SCHEMA
    )


def _is_structural_auto(
    page: PageV4,
) -> bool:

    return bool(
        page.metadata.get(
            "automatic_structure",
            False,
        )
    )


def type_model_bindings(
    book: BookV4,
) -> dict[str, str]:

    raw = book.metadata.get(
        TYPE_BINDINGS_KEY,
        {},
    )

    if not isinstance(
        raw,
        dict,
    ):
        return {}

    return {
        str(key): str(value)
        for key, value
        in raw.items()
        if str(key).strip()
        and str(value).strip()
    }


def _bindings_root(
    book: BookV4,
) -> dict[str, str]:

    raw = book.metadata.get(
        TYPE_BINDINGS_KEY
    )

    if isinstance(
        raw,
        dict,
    ):
        return raw

    result: dict[
        str,
        str,
    ] = {}

    book.metadata[
        TYPE_BINDINGS_KEY
    ] = result

    return result


def model_by_id(
    book: BookV4,
    model_id: str,
) -> dict[str, Any]:

    model = book.models.get(
        model_id
    )

    if not isinstance(
        model,
        dict,
    ):
        raise KeyError(
            model_id
        )

    validate_model(
        model
    )

    return model


def validate_model(
    model: dict[str, Any],
) -> None:

    if not isinstance(
        model,
        dict,
    ):
        raise ValueError(
            "Modèle Composition invalide."
        )

    if model.get(
        "schema"
    ) != MODEL_SCHEMA:
        raise ValueError(
            "Schéma de modèle Composition inconnu."
        )

    if model.get(
        "version"
    ) != MODEL_VERSION:
        raise ValueError(
            "Version de modèle Composition inconnue."
        )

    if not str(
        model.get(
            "id"
        )
        or ""
    ).strip():
        raise ValueError(
            "UUID de modèle absent."
        )

    elements = model.get(
        "elements"
    )

    if not isinstance(
        elements,
        list,
    ):
        raise ValueError(
            "Éléments du modèle invalides."
        )

    ids: list[str] = []

    for element in elements:
        validate_element(
            element
        )

        ids.append(
            str(
                element["id"]
            )
        )

    if len(ids) != len(
        set(ids)
    ):
        raise ValueError(
            "UUID d'élément de modèle dupliqué."
        )


def _template_from_instance(
    element: dict[str, Any],
    *,
    template_id: str | None = None,
) -> dict[str, Any]:

    template = deepcopy(
        element
    )

    metadata = template.setdefault(
        "metadata",
        {},
    )

    existing_template_id = (
        metadata.get(
            MODEL_ELEMENT_ID_KEY
        )
    )

    resolved_id = (
        str(template_id)
        if template_id is not None
        else (
            str(existing_template_id)
            if existing_template_id
            else new_id()
        )
    )

    template[
        "id"
    ] = resolved_id

    metadata.pop(
        MODEL_ID_KEY,
        None,
    )

    metadata.pop(
        MODEL_ELEMENT_ID_KEY,
        None,
    )

    validate_element(
        template
    )

    return template


def _instance_from_template(
    model_id: str,
    template: dict[str, Any],
    *,
    instance_id: str | None = None,
    preserved_metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:

    instance = deepcopy(
        template
    )

    template_id = str(
        template[
            "id"
        ]
    )

    instance[
        "id"
    ] = (
        str(instance_id)
        if instance_id is not None
        else new_id()
    )

    metadata = deepcopy(
        template.get(
            "metadata",
            {},
        )
    )

    if preserved_metadata:
        for key, value in (
            preserved_metadata.items()
        ):
            if key not in {
                MODEL_ID_KEY,
                MODEL_ELEMENT_ID_KEY,
            }:
                metadata.setdefault(
                    key,
                    deepcopy(value),
                )

    metadata[
        MODEL_ID_KEY
    ] = model_id

    metadata[
        MODEL_ELEMENT_ID_KEY
    ] = template_id

    instance[
        "metadata"
    ] = metadata

    validate_element(
        instance
    )

    return instance


def create_model_from_page(
    book: BookV4,
    page_id: str,
    *,
    title: str = "",
) -> dict[str, Any]:
    """
    Crée un modèle à partir de l'état réel d'une page.

    Les éléments de la page conservent leur UUID.
    Ils deviennent les premières instances liées au modèle.
    """

    book.validate()

    page = _page(
        book,
        page_id,
    )

    if _is_structural_auto(
        page
    ):
        raise ValueError(
            "Une page automatique Structure "
            "ne peut pas devenir source de modèle."
        )

    snapshot = deepcopy(
        book
    )

    try:
        model_id = new_id()

        templates: list[
            dict[str, Any]
        ] = []

        for element in page.content:
            if not _is_composition_element(
                element
            ):
                continue

            template = (
                _template_from_instance(
                    element
                )
            )

            templates.append(
                template
            )

            metadata = element.setdefault(
                "metadata",
                {},
            )

            metadata[
                MODEL_ID_KEY
            ] = model_id

            metadata[
                MODEL_ELEMENT_ID_KEY
            ] = template[
                "id"
            ]

        date = utc_now()

        model = {
            "schema": MODEL_SCHEMA,
            "version": MODEL_VERSION,
            "id": model_id,
            "title": str(
                title or page.title or ""
            ),
            "source_page_type": (
                _page_type(
                    page
                )
            ),
            "elements": templates,
            "created_at": date,
            "updated_at": date,
        }

        validate_model(
            model
        )

        book.models[
            model_id
        ] = model

        page.model_id = (
            model_id
        )

        page.metadata.pop(
            DETACHED_TYPE_KEY,
            None,
        )

        book.history.append(
            {
                "action": (
                    "composition_model_created"
                ),
                "model_id": model_id,
                "page_id": page.id,
                "date": date,
            }
        )

        book.validate()

        return model

    except Exception:
        _restore_book(
            book,
            snapshot,
        )
        raise


def apply_model_to_page(
    book: BookV4,
    page_id: str,
    model_id: str,
) -> ModelApplyResult:
    """
    Synchronise une vraie instance du modèle sur une page.

    Les éléments non gérés par un modèle sont conservés.
    Les instances déjà présentes gardent leur UUID.
    """

    book.validate()

    page = _page(
        book,
        page_id,
    )

    model = model_by_id(
        book,
        model_id,
    )

    snapshot = deepcopy(
        book
    )

    try:
        existing_managed: dict[
            str,
            dict[str, Any],
        ] = {}

        old_managed_count = 0
        unmanaged: list[Any] = []

        for element in page.content:
            if not _is_composition_element(
                element
            ):
                unmanaged.append(
                    element
                )
                continue

            metadata = element.get(
                "metadata",
                {},
            )

            existing_model_id = str(
                metadata.get(
                    MODEL_ID_KEY,
                    "",
                )
            )

            template_id = str(
                metadata.get(
                    MODEL_ELEMENT_ID_KEY,
                    "",
                )
            )

            if existing_model_id:
                old_managed_count += 1

            if (
                existing_model_id
                == model_id
                and template_id
            ):
                existing_managed[
                    template_id
                ] = element
            elif not existing_model_id:
                unmanaged.append(
                    element
                )

        instances: list[
            dict[str, Any]
        ] = []

        reused = 0
        created = 0

        for template in model[
            "elements"
        ]:
            template_id = str(
                template[
                    "id"
                ]
            )

            existing = (
                existing_managed.get(
                    template_id
                )
            )

            if existing is not None:
                instance = (
                    _instance_from_template(
                        model_id,
                        template,
                        instance_id=str(
                            existing[
                                "id"
                            ]
                        ),
                        preserved_metadata=(
                            existing.get(
                                "metadata",
                                {},
                            )
                        ),
                    )
                )

                reused += 1

            else:
                instance = (
                    _instance_from_template(
                        model_id,
                        template,
                    )
                )

                created += 1

            instances.append(
                instance
            )

        # Les éléments du modèle constituent le fond logique
        # de la page ; les éléments locaux restent au-dessus.
        page.content = (
            instances
            + unmanaged
        )

        page.model_id = (
            model_id
        )

        page.metadata.pop(
            DETACHED_TYPE_KEY,
            None,
        )

        removed = max(
            0,
            old_managed_count
            - reused,
        )

        book.history.append(
            {
                "action": (
                    "composition_model_applied"
                ),
                "model_id": model_id,
                "page_id": page.id,
                "reused_elements": reused,
                "created_elements": created,
                "removed_elements": removed,
                "date": utc_now(),
            }
        )

        book.validate()

        return ModelApplyResult(
            model_id=model_id,
            page_id=page.id,
            reused_elements=reused,
            created_elements=created,
            removed_elements=removed,
        )

    except Exception:
        _restore_book(
            book,
            snapshot,
        )
        raise


def extend_model_to_type(
    book: BookV4,
    page_id: str,
) -> ModelPropagationResult:
    """
    Équivalent moteur de « Toutes du type ».

    Le modèle de la page devient le modèle par défaut du type
    et est copié réellement sur toutes les pages concernées.
    """

    book.validate()

    page = _page(
        book,
        page_id,
    )

    if not page.model_id:
        raise ValueError(
            "La page ne possède aucun modèle."
        )

    model_id = str(
        page.model_id
    )

    model_by_id(
        book,
        model_id,
    )

    source_type = _page_type(
        page
    )

    snapshot = deepcopy(
        book
    )

    try:
        bindings = _bindings_root(
            book
        )

        bindings[
            source_type
        ] = model_id

        applied = 0

        for candidate_id in list(
            book.page_order
        ):
            candidate = book.pages[
                candidate_id
            ]

            if _is_structural_auto(
                candidate
            ):
                continue

            if _page_type(
                candidate
            ) != source_type:
                continue

            apply_model_to_page(
                book,
                candidate.id,
                model_id,
            )

            applied += 1

        book.history.append(
            {
                "action": (
                    "composition_model_extended_to_type"
                ),
                "model_id": model_id,
                "page_type": source_type,
                "pages_applied": applied,
                "date": utc_now(),
            }
        )

        book.validate()

        return ModelPropagationResult(
            model_id=model_id,
            page_type=source_type,
            applied_pages=applied,
        )

    except Exception:
        _restore_book(
            book,
            snapshot,
        )
        raise


def refresh_model_from_page(
    book: BookV4,
    page_id: str,
    *,
    propagate: bool = True,
) -> ModelPropagationResult:
    """
    Met à jour le modèle depuis une page liée.

    Les éléments déjà connus gardent leur identité de modèle.
    Les nouveaux éléments obtiennent une nouvelle identité de modèle.
    Puis les copies liées sont mises à jour en conservant leurs UUID.
    """

    book.validate()

    page = _page(
        book,
        page_id,
    )

    if not page.model_id:
        raise ValueError(
            "La page n'est liée à aucun modèle."
        )

    model_id = str(
        page.model_id
    )

    model = model_by_id(
        book,
        model_id,
    )

    snapshot = deepcopy(
        book
    )

    try:
        templates: list[
            dict[str, Any]
        ] = []

        for element in page.content:
            if not _is_composition_element(
                element
            ):
                continue

            metadata = element.setdefault(
                "metadata",
                {},
            )

            linked_model_id = str(
                metadata.get(
                    MODEL_ID_KEY,
                    "",
                )
            )

            template_id = (
                metadata.get(
                    MODEL_ELEMENT_ID_KEY
                )
            )

            if (
                linked_model_id != model_id
                or not template_id
            ):
                template_id = new_id()

                metadata[
                    MODEL_ID_KEY
                ] = model_id

                metadata[
                    MODEL_ELEMENT_ID_KEY
                ] = template_id

            template = (
                _template_from_instance(
                    element,
                    template_id=str(
                        template_id
                    ),
                )
            )

            templates.append(
                template
            )

        model[
            "elements"
        ] = templates

        model[
            "source_page_type"
        ] = _page_type(
            page
        )

        model[
            "updated_at"
        ] = utc_now()

        validate_model(
            model
        )

        applied = 0

        if propagate:
            for candidate_id in list(
                book.page_order
            ):
                if candidate_id == page.id:
                    continue

                candidate = book.pages[
                    candidate_id
                ]

                if (
                    candidate.model_id
                    == model_id
                ):
                    apply_model_to_page(
                        book,
                        candidate.id,
                        model_id,
                    )

                    applied += 1

        book.history.append(
            {
                "action": (
                    "composition_model_refreshed"
                ),
                "model_id": model_id,
                "source_page_id": page.id,
                "propagated_pages": applied,
                "date": utc_now(),
            }
        )

        book.validate()

        return ModelPropagationResult(
            model_id=model_id,
            page_type=_page_type(
                page
            ),
            applied_pages=applied,
        )

    except Exception:
        _restore_book(
            book,
            snapshot,
        )
        raise


def detach_page_from_model(
    book: BookV4,
    page_id: str,
) -> bool:
    """
    Transforme les copies du modèle en éléments locaux réels.

    Leur UUID et leur contenu ne changent pas.
    """

    book.validate()

    page = _page(
        book,
        page_id,
    )

    if not page.model_id:
        return False

    old_model_id = str(
        page.model_id
    )

    page_type = _page_type(
        page
    )

    for element in page.content:
        if not _is_composition_element(
            element
        ):
            continue

        metadata = element.get(
            "metadata",
            {},
        )

        metadata.pop(
            MODEL_ID_KEY,
            None,
        )

        metadata.pop(
            MODEL_ELEMENT_ID_KEY,
            None,
        )

    page.model_id = None

    page.metadata[
        DETACHED_TYPE_KEY
    ] = page_type

    book.history.append(
        {
            "action": (
                "composition_model_detached"
            ),
            "page_id": page.id,
            "old_model_id": old_model_id,
            "page_type": page_type,
            "date": utc_now(),
        }
    )

    book.validate()

    return True


def apply_type_model_if_any(
    book: BookV4,
    page_id: str,
    *,
    force: bool = False,
) -> bool:
    """
    Applique le modèle de type s'il existe.

    Utilisé notamment lors de la création ou du changement
    de type d'une page.
    """

    page = _page(
        book,
        page_id,
    )

    if _is_structural_auto(
        page
    ):
        return False

    page_type = _page_type(
        page
    )

    model_id = (
        type_model_bindings(
            book
        ).get(
            page_type
        )
    )

    if not model_id:
        return False

    detached_type = str(
        page.metadata.get(
            DETACHED_TYPE_KEY,
            "",
        )
    ).strip().lower()

    if (
        not force
        and detached_type == page_type
    ):
        return False

    if (
        not force
        and page.model_id
        and page.model_id != model_id
    ):
        return False

    apply_model_to_page(
        book,
        page.id,
        model_id,
    )

    return True


def clear_type_model_binding(
    book: BookV4,
    page_type: str,
) -> bool:
    """
    Arrête seulement l'héritage futur.

    Les copies déjà présentes dans les pages restent réelles
    et liées à leur modèle jusqu'à détachement explicite.
    """

    normalized = str(
        page_type or ""
    ).strip().lower()

    if not normalized:
        raise ValueError(
            "Type de page vide."
        )

    bindings = _bindings_root(
        book
    )

    if normalized not in bindings:
        return False

    old_model_id = bindings.pop(
        normalized
    )

    book.history.append(
        {
            "action": (
                "composition_model_type_binding_removed"
            ),
            "page_type": normalized,
            "model_id": old_model_id,
            "date": utc_now(),
        }
    )

    return True


def composition_model_issues(
    book: BookV4,
) -> list[str]:

    issues: list[str] = []

    for model_id, model in (
        book.models.items()
    ):
        try:
            validate_model(
                model
            )

            if str(
                model.get(
                    "id"
                )
            ) != str(
                model_id
            ):
                issues.append(
                    f"Identité modèle incohérente : {model_id}"
                )

        except Exception as exc:
            issues.append(
                f"Modèle {model_id} : {exc}"
            )

    bindings = type_model_bindings(
        book
    )

    for page_type, model_id in (
        bindings.items()
    ):
        if model_id not in book.models:
            issues.append(
                "Modèle de type inconnu : "
                f"{page_type}/{model_id}"
            )

    for page in book.pages.values():
        if (
            page.model_id is not None
            and page.model_id not in book.models
        ):
            issues.append(
                "Page liée à un modèle inconnu : "
                f"{page.id}/{page.model_id}"
            )

    return issues
