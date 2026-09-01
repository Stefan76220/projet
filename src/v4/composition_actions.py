from __future__ import annotations

"""
TomeLinea V4 — Actions de Composition.

Actions utilisateur sûres :
- duplication d'un ou plusieurs éléments ;
- duplication atomique des associations ;
- nouveaux UUID pour toutes les copies ;
- conservation de la traçabilité Source ;
- les copies deviennent locales et ne dupliquent jamais
  artificiellement une liaison de modèle ;
- suppression atomique d'une sélection ou association ;
- refus de supprimer directement une instance encore
  gérée par un modèle ;
- respect du verrouillage de l'espace de travail.

Les duplications sont placées au premier plan tout en
conservant leur ordre relatif.
"""

from copy import deepcopy
from dataclasses import fields
from datetime import datetime, timezone
from typing import Iterable, Any
from uuid import uuid4

from src.v4.project import (
    ProjectV4,
)

from src.v4.composition import (
    COMPOSITION_SCHEMA,
    element_by_id,
    remove_element,
    validate_element,
)

from src.v4.composition_arrange import (
    GROUP_KEY,
    normalize_selection,
)

from src.v4.composition_constraints import (
    locked_element_ids,
)

from src.v4.composition_models import (
    MODEL_ID_KEY,
    MODEL_ELEMENT_ID_KEY,
)


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def new_id() -> str:
    return str(
        uuid4()
    )


def _restore_project(
    project: ProjectV4,
    snapshot: ProjectV4,
) -> None:

    for field_info in fields(
        ProjectV4
    ):
        setattr(
            project,
            field_info.name,
            deepcopy(
                getattr(
                    snapshot,
                    field_info.name,
                )
            ),
        )


def _book(
    project: ProjectV4,
):
    if project.book is None:
        raise ValueError(
            "Le Projet ne possède aucun Livre."
        )

    return project.book


def _page(
    project: ProjectV4,
    page_id: str,
):
    book = _book(
        project
    )

    page = book.pages.get(
        page_id
    )

    if page is None:
        raise KeyError(
            page_id
        )

    return page


def _selection(
    project: ProjectV4,
    page_id: str,
    element_ids: Iterable[str],
) -> list[str]:

    book = _book(
        project
    )

    selected = normalize_selection(
        book,
        page_id,
        element_ids,
        include_associated=True,
    )

    if not selected:
        raise ValueError(
            "Sélection vide."
        )

    locked = locked_element_ids(
        project,
        page_id,
    )

    blocked = [
        element_id
        for element_id in selected
        if element_id in locked
    ]

    if blocked:
        raise ValueError(
            "Un ou plusieurs éléments sont verrouillés : "
            + ", ".join(
                blocked
            )
        )

    return selected


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


def duplicate_selection(
    project: ProjectV4,
    page_id: str,
    element_ids: Iterable[str],
    *,
    dx_mm: float = 0.0,
    dy_mm: float = 0.0,
) -> list[dict[str, Any]]:
    """
    Duplique la sélection réelle.

    - une association est dupliquée entièrement ;
    - chaque copie obtient son propre UUID ;
    - une association dupliquée obtient un nouvel UUID de groupe ;
    - source_ref est conservé ;
    - les identifiants de modèle sont supprimés ;
    - les copies sont donc des éléments locaux indépendants ;
    - les copies sont ajoutées au premier plan.
    """

    project.validate()

    book = _book(
        project
    )

    page = _page(
        project,
        page_id,
    )

    selected = _selection(
        project,
        page_id,
        element_ids,
    )

    snapshot = deepcopy(
        project
    )

    try:
        group_mapping: dict[
            str,
            str,
        ] = {}

        copies: list[
            dict[str, Any]
        ] = []

        for element_id in selected:
            original = element_by_id(
                page,
                element_id,
            )

            copy = deepcopy(
                original
            )

            copy[
                "id"
            ] = new_id()

            geometry = copy[
                "geometry"
            ]

            geometry[
                "x_mm"
            ] = (
                float(
                    geometry[
                        "x_mm"
                    ]
                )
                + float(
                    dx_mm
                )
            )

            geometry[
                "y_mm"
            ] = (
                float(
                    geometry[
                        "y_mm"
                    ]
                )
                + float(
                    dy_mm
                )
            )

            metadata = copy.setdefault(
                "metadata",
                {},
            )

            # Une duplication utilisateur est toujours locale.
            metadata.pop(
                MODEL_ID_KEY,
                None,
            )

            metadata.pop(
                MODEL_ELEMENT_ID_KEY,
                None,
            )

            original_group = (
                original.get(
                    "metadata",
                    {},
                ).get(
                    GROUP_KEY
                )
            )

            if original_group:
                old_group_id = str(
                    original_group
                )

                new_group_id = (
                    group_mapping.setdefault(
                        old_group_id,
                        new_id(),
                    )
                )

                metadata[
                    GROUP_KEY
                ] = new_group_id
            else:
                metadata.pop(
                    GROUP_KEY,
                    None,
                )

            metadata[
                "duplicated_from_element_id"
            ] = str(
                original[
                    "id"
                ]
            )

            metadata[
                "duplicated_at"
            ] = utc_now()

            validate_element(
                copy
            )

            copies.append(
                copy
            )

        # Premier plan, ordre relatif conservé.
        page.content.extend(
            copies
        )

        date = utc_now()

        page.modifications.append(
            {
                "action": (
                    "composition_elements_duplicated"
                ),
                "source_element_ids": list(
                    selected
                ),
                "new_element_ids": [
                    copy["id"]
                    for copy in copies
                ],
                "date": date,
            }
        )

        book.history.append(
            {
                "action": (
                    "composition_elements_duplicated"
                ),
                "page_id": page.id,
                "source_element_ids": list(
                    selected
                ),
                "new_element_ids": [
                    copy["id"]
                    for copy in copies
                ],
                "date": date,
            }
        )

        project.touch()
        book.validate()
        project.validate()

        return copies

    except Exception:
        _restore_project(
            project,
            snapshot,
        )
        raise


def delete_selection(
    project: ProjectV4,
    page_id: str,
    element_ids: Iterable[str],
) -> list[dict[str, Any]]:
    """
    Suppression utilisateur atomique.

    Une association entière est supprimée ensemble.

    Une instance encore gérée par un modèle ne peut pas être
    supprimée directement : la page doit d'abord être détachée
    du modèle. Cela évite une suppression illusoire qui serait
    annulée lors de la prochaine propagation.
    """

    project.validate()

    book = _book(
        project
    )

    page = _page(
        project,
        page_id,
    )

    selected = _selection(
        project,
        page_id,
        element_ids,
    )

    for element_id in selected:
        element = element_by_id(
            page,
            element_id,
        )

        metadata = element.get(
            "metadata",
            {},
        )

        if (
            metadata.get(
                MODEL_ID_KEY
            )
            or metadata.get(
                MODEL_ELEMENT_ID_KEY
            )
        ):
            raise ValueError(
                "Impossible de supprimer directement "
                "un élément encore géré par un modèle. "
                "Détachez d'abord la page du modèle."
            )

    snapshot = deepcopy(
        project
    )

    try:
        removed: list[
            dict[str, Any]
        ] = []

        # remove_element cherche par UUID :
        # l'ordre n'a donc pas d'importance pour l'intégrité.
        for element_id in selected:
            removed.append(
                remove_element(
                    book,
                    page_id,
                    element_id,
                )
            )

        date = utc_now()

        book.history.append(
            {
                "action": (
                    "composition_selection_deleted"
                ),
                "page_id": page_id,
                "element_ids": list(
                    selected
                ),
                "date": date,
            }
        )

        project.touch()
        book.validate()
        project.validate()

        return removed

    except Exception:
        _restore_project(
            project,
            snapshot,
        )
        raise


def composition_action_issues(
    project: ProjectV4,
) -> list[str]:
    """
    Vérifie les invariants utiles aux Actions.
    """

    issues: list[str] = []

    if project.book is None:
        return issues

    seen: set[str] = set()

    for page in (
        project.book.pages.values()
    ):
        for element in page.content:
            if not _is_composition_element(
                element
            ):
                continue

            element_id = str(
                element.get(
                    "id",
                    "",
                )
            )

            if not element_id:
                issues.append(
                    "Élément Composition sans UUID."
                )

                continue

            if element_id in seen:
                issues.append(
                    "UUID Composition dupliqué : "
                    f"{element_id}"
                )

            seen.add(
                element_id
            )

            try:
                validate_element(
                    element
                )
            except Exception as exc:
                issues.append(
                    f"Élément {element_id} invalide : {exc}"
                )

    return issues
