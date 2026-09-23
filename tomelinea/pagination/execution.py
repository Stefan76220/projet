"""Execution des Decisions Pagination de TomeLinea V5.

Aucun moteur physique n'est recree ici. Ce module raccorde les Decisions V5
aux fonctions Structure V4 deja validees :

- ``set_constraint_on_pages`` applique ou retire une contrainte locale ;
- ``extend_constraint_to_similar`` applique volontairement une contrainte
  aux pages similaires calculees par le moteur 88 % ;
- ``sync_structure_rules`` materialise AV/AP, doubles pages et compensations
  de parite dans le Livre.

La double page reste une relation explicite entre deux UUID choisis.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from src.v4.structure_editorial import (
    DOUBLE_PAGE,
    extend_constraint_to_similar,
    set_constraint_on_pages,
)
from src.v4.structure_sync import (
    sync_structure_rules,
)

from tomelinea.rules import (
    Decision,
    DecisionScope,
    Situation,
)

from .api import (
    PAGINATION_SITUATION_KINDS,
    similar_pagination_page_ids,
)


PAGINATION_CHOICE_ENABLED = "enabled"
PAGINATION_CHOICE_DISABLED = "disabled"
PAGINATION_DECISION_CHOICES = (
    PAGINATION_CHOICE_ENABLED,
    PAGINATION_CHOICE_DISABLED,
)


@dataclass(frozen=True, slots=True)
class PaginationDecisionExecution:
    situation_id: str
    subject_id: str
    kind: str
    choice: str
    scope: DecisionScope
    changed_page_ids: tuple[str, ...]
    extension_id: str = ""
    extension: Mapping[str, Any] | None = None


def _book(project: Any) -> Any:
    book = getattr(
        project,
        "book",
        None,
    )

    if book is None:
        raise ValueError(
            "Le Projet ne possede pas de Livre."
        )

    return book


def _touch(project: Any) -> None:
    touch = getattr(
        project,
        "touch",
        None,
    )

    if callable(touch):
        touch()


def _validate_pagination_decision(
    situation: Situation,
    decision: Decision,
) -> str:
    if not isinstance(
        situation,
        Situation,
    ):
        raise TypeError(
            "Une Situation V5 est requise."
        )

    if not isinstance(
        decision,
        Decision,
    ):
        raise TypeError(
            "Une Decision V5 est requise."
        )

    if str(
        situation.domain
    ) != "pagination":
        raise ValueError(
            "Cette Situation n'appartient pas au domaine Pagination."
        )

    if str(
        situation.kind
    ) not in PAGINATION_SITUATION_KINDS:
        raise ValueError(
            "Contrainte Pagination inconnue."
        )

    if decision.situation_id != situation.id:
        raise ValueError(
            "La Decision ne correspond pas a cette Situation."
        )

    if str(
        decision.subject_id
    ) != str(
        situation.subject_id
    ):
        raise ValueError(
            "La Decision ne vise pas le meme objet stable."
        )

    choice = str(
        decision.choice
        or ""
    ).strip()

    if choice not in PAGINATION_DECISION_CHOICES:
        raise ValueError(
            "Choix Pagination inconnu : "
            + choice
        )

    if (
        decision.scope == DecisionScope.SIMILAR
        and str(situation.kind) == DOUBLE_PAGE
    ):
        raise ValueError(
            "Une double page ne s'etend jamais automatiquement par similarite."
        )

    if (
        decision.scope == DecisionScope.SIMILAR
        and choice != PAGINATION_CHOICE_ENABLED
    ):
        raise ValueError(
            "Le retrait d'une extension similaire reste une action distincte "
            "dans le moteur V4 ; une Decision SIMILAR ne peut qu'activer."
        )

    return choice


def _double_page_members(
    situation: Situation,
) -> tuple[str, str]:
    raw = dict(
        situation.facts
        or {}
    ).get(
        "member_page_ids",
        (),
    )

    if not isinstance(
        raw,
        (list, tuple),
    ):
        raise ValueError(
            "Situation Double page sans deux UUID explicites."
        )

    members = tuple(
        str(value).strip()
        for value in raw
        if str(value).strip()
    )

    if len(members) != 2:
        raise ValueError(
            "Situation Double page sans deux UUID explicites."
        )

    return (
        members[0],
        members[1],
    )


def _normalized_similar_ids(
    values: tuple[str, ...],
    anchor_page_id: str,
) -> tuple[str, ...]:
    result: list[str] = []
    seen: set[str] = set()

    for raw in values:
        value = str(
            raw
            or ""
        ).strip()

        if (
            not value
            or value == anchor_page_id
            or value in seen
        ):
            continue

        seen.add(
            value
        )
        result.append(
            value
        )

    return tuple(
        result
    )


def execute_pagination_decision(
    project: Any,
    situation: Situation,
    decision: Decision,
) -> PaginationDecisionExecution:
    """Execute une Decision Pagination via les moteurs V4 existants."""

    choice = _validate_pagination_decision(
        situation,
        decision,
    )

    book = _book(
        project
    )

    kind = str(
        situation.kind
    )

    enabled = (
        choice
        == PAGINATION_CHOICE_ENABLED
    )

    if decision.scope == DecisionScope.LOCAL:
        if kind == DOUBLE_PAGE:
            targets = _double_page_members(
                situation
            )
        else:
            targets = (
                str(
                    situation.subject_id
                ),
            )

        changed = tuple(
            str(value)
            for value in set_constraint_on_pages(
                book,
                targets,
                kind,
                enabled,
            )
        )

        sync_structure_rules(
            book
        )
        _touch(
            project
        )

        return PaginationDecisionExecution(
            situation_id=situation.id,
            subject_id=situation.subject_id,
            kind=kind,
            choice=choice,
            scope=decision.scope,
            changed_page_ids=changed,
        )

    anchor_page_id = str(
        situation.subject_id
    )

    requested = _normalized_similar_ids(
        decision.similar_subject_ids,
        anchor_page_id,
    )

    current = _normalized_similar_ids(
        tuple(
            similar_pagination_page_ids(
                project,
                anchor_page_id,
                kind,
                threshold=decision.threshold,
            )
        ),
        anchor_page_id,
    )

    if requested != current:
        raise ValueError(
            "La famille de pages similaires a change depuis la Decision. "
            "TomeLinea refuse d'appliquer une portee devenue obsolete."
        )

    set_constraint_on_pages(
        book,
        (anchor_page_id,),
        kind,
        True,
    )

    extension = dict(
        extend_constraint_to_similar(
            project,
            anchor_page_id,
            kind,
            threshold=decision.threshold,
        )
        or {}
    )

    sync_structure_rules(
        book
    )
    _touch(
        project
    )

    changed = tuple(
        str(value)
        for value in extension.get(
            "applied_page_ids",
            (),
        )
    )

    return PaginationDecisionExecution(
        situation_id=situation.id,
        subject_id=situation.subject_id,
        kind=kind,
        choice=choice,
        scope=decision.scope,
        changed_page_ids=changed,
        extension_id=str(
            extension.get(
                "extension_id",
                "",
            )
            or ""
        ),
        extension=extension,
    )


__all__ = [
    "PAGINATION_CHOICE_ENABLED",
    "PAGINATION_CHOICE_DISABLED",
    "PAGINATION_DECISION_CHOICES",
    "PaginationDecisionExecution",
    "execute_pagination_decision",
]