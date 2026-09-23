"""Catalogue des Situations Pagination de TomeLinea V5.

La V4 ne possede pas un detecteur global d'anomalies de pagination.
Elle possede cinq decisions physiques explicites et un moteur de parite
deterministe. V5-11 expose ces contrats comme Situations V5 sans recreer
ni appliquer les regles.

Toute mutation du Livre reste la responsabilite des moteurs Structure V4.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable

from src.v4.structure_editorial import (
    BLANK_AFTER,
    BLANK_BEFORE,
    CONSTRAINT_HELP,
    CONSTRAINT_LABELS,
    DOUBLE_PAGE,
    KNOWN_CONSTRAINTS,
    PAGE_LEFT,
    PAGE_RIGHT,
    SIMILARITY_THRESHOLD,
    constraint_enabled,
    double_page_selection_reason,
    similar_page_ids,
)
from src.v4.structure_parity import physical_side
from src.v4.structure_spreads import page_spread

from tomelinea.rules import Situation


class PaginationSituationClass(str, Enum):
    POSITION = "position"
    AROUND = "around"
    SPREAD = "spread"


PAGINATION_SITUATION_KINDS = tuple(KNOWN_CONSTRAINTS)

PAGINATION_CLASSES = {
    PAGE_RIGHT: PaginationSituationClass.POSITION,
    PAGE_LEFT: PaginationSituationClass.POSITION,
    BLANK_BEFORE: PaginationSituationClass.AROUND,
    BLANK_AFTER: PaginationSituationClass.AROUND,
    DOUBLE_PAGE: PaginationSituationClass.SPREAD,
}


def pagination_situation_class(kind: str) -> PaginationSituationClass:
    value = str(kind or "").strip()

    if value not in PAGINATION_CLASSES:
        raise ValueError(f"Contrainte Pagination inconnue : {kind}")

    return PAGINATION_CLASSES[value]


def pagination_situation(
    book: Any,
    page_id: str,
    kind: str,
) -> Situation:
    """Traduit UNE regle physique possible sur UNE page stable."""

    page_id = str(page_id or "").strip()
    kind = str(kind or "").strip()

    if page_id not in getattr(book, "pages", {}):
        raise KeyError(page_id)

    if kind not in PAGINATION_SITUATION_KINDS:
        raise ValueError(f"Contrainte Pagination inconnue : {kind}")

    if kind == DOUBLE_PAGE:
        raise ValueError(
            "Une double page porte sur deux pages explicites. "
            "Utilisez double_page_situation()."
        )

    return Situation(
        domain="pagination",
        kind=kind,
        subject_id=page_id,
        page_id=page_id,
        facts={
            "classification": pagination_situation_class(kind).value,
            "label": CONSTRAINT_LABELS[kind],
            "help": CONSTRAINT_HELP[kind],
            "enabled": bool(
                constraint_enabled(
                    book,
                    page_id,
                    kind,
                )
            ),
            "physical_side": physical_side(
                book,
                page_id,
            ),
        },
    )


def double_page_situation(
    book: Any,
    page_ids: Iterable[str],
) -> Situation:
    """Situation relationnelle creee uniquement depuis deux UUID choisis."""

    wanted = [
        str(value).strip()
        for value in page_ids
        if str(value).strip()
    ]

    ordered = [
        page_id
        for page_id in getattr(book, "page_order", ())
        if page_id in wanted
    ]

    # Le moteur V4 reste l'autorite pour expliquer toute incompatibilite.
    reason = double_page_selection_reason(
        book,
        wanted,
    )

    if len(ordered) != 2:
        subject_id = "double_page:" + ":".join(wanted)
        page_id = wanted[0] if wanted else None
        members = tuple(wanted)
    else:
        left_id, right_id = ordered
        subject_id = f"double_page:{left_id}:{right_id}"
        page_id = left_id
        members = (left_id, right_id)

    enabled = False

    if len(members) == 2:
        left_spread = page_spread(
            book,
            members[0],
        )
        enabled = bool(
            left_spread is not None
            and {
                str(left_spread.left_page_id),
                str(left_spread.right_page_id),
            }
            == set(members)
        )

    facts = {
        "classification": PaginationSituationClass.SPREAD.value,
        "label": CONSTRAINT_LABELS[DOUBLE_PAGE],
        "help": CONSTRAINT_HELP[DOUBLE_PAGE],
        "member_page_ids": members,
        "valid": not bool(reason),
        "enabled": enabled,
    }

    if reason:
        facts["reason"] = reason

    return Situation(
        domain="pagination",
        kind=DOUBLE_PAGE,
        subject_id=subject_id,
        page_id=page_id,
        facts=facts,
    )


def similar_pagination_page_ids(
    project: Any,
    anchor_page_id: str,
    kind: str,
    *,
    threshold: float = SIMILARITY_THRESHOLD,
) -> tuple[str, ...]:
    """Delegue la similarite au moteur V4 ; ne modifie aucune page."""

    kind = str(kind or "").strip()

    if kind not in PAGINATION_SITUATION_KINDS:
        raise ValueError(f"Contrainte Pagination inconnue : {kind}")

    if kind == DOUBLE_PAGE:
        raise ValueError(
            "Une double page ne s'etend jamais automatiquement par similarite."
        )

    return tuple(
        similar_page_ids(
            project,
            str(anchor_page_id),
            threshold=float(threshold),
        )
    )


__all__ = [
    "PAGE_RIGHT",
    "PAGE_LEFT",
    "BLANK_BEFORE",
    "BLANK_AFTER",
    "DOUBLE_PAGE",
    "CONSTRAINT_LABELS",
    "CONSTRAINT_HELP",
    "SIMILARITY_THRESHOLD",
    "PaginationSituationClass",
    "PAGINATION_SITUATION_KINDS",
    "PAGINATION_CLASSES",
    "pagination_situation_class",
    "pagination_situation",
    "double_page_situation",
    "similar_pagination_page_ids",
]