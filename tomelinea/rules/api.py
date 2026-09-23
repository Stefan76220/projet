"""Moteur deterministe Situation -> Cas -> Decision -> Regle de TomeLinea V5.

Les moteurs specialises produisent des Situations factuelles. Ce noyau :
- groupe les situations d'un meme objet stable dans un seul Cas ;
- cree une Decision explicite pour une Situation ;
- transforme exactement cette Decision en Regle ;
- n'etend jamais une Regle par similarite sans demande explicite.

La similarite reste calculee par le moteur specialise. Le seuil commun V4
valide est conserve a 88 %.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Iterable, Mapping

from src.v4.structure_editorial import (
    SIMILARITY_THRESHOLD as V4_SIMILARITY_THRESHOLD,
)

SIMILARITY_THRESHOLD = V4_SIMILARITY_THRESHOLD


class DecisionScope(str, Enum):
    LOCAL = "local"
    SIMILAR = "similar"


def _clean(value: object) -> str:
    return str(value or "").strip()


def _unique_ids(values: Iterable[object]) -> tuple[str, ...]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        item = _clean(value)
        if not item or item in seen:
            continue
        seen.add(item)
        result.append(item)
    return tuple(result)


@dataclass(frozen=True, slots=True)
class Situation:
    domain: str
    kind: str
    subject_id: str
    page_id: str | None = None
    qualifier: str = ""
    facts: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not _clean(self.domain):
            raise ValueError("Une Situation doit avoir un domaine.")
        if not _clean(self.kind):
            raise ValueError("Une Situation doit avoir un type.")
        if not _clean(self.subject_id):
            raise ValueError("Une Situation doit viser un identifiant stable.")

    @property
    def id(self) -> str:
        parts = [_clean(self.domain), _clean(self.kind), _clean(self.subject_id)]
        qualifier = _clean(self.qualifier)
        if qualifier:
            parts.append(qualifier)
        return ":".join(parts)


@dataclass(frozen=True, slots=True)
class Case:
    subject_id: str
    situations: tuple[Situation, ...]

    def __post_init__(self) -> None:
        subject_id = _clean(self.subject_id)
        if not subject_id:
            raise ValueError("Un Cas doit viser un identifiant stable.")
        if not self.situations:
            raise ValueError("Un Cas doit contenir au moins une Situation.")
        if any(_clean(item.subject_id) != subject_id for item in self.situations):
            raise ValueError("Toutes les Situations d'un Cas doivent viser le meme objet.")

    @property
    def id(self) -> str:
        return f"case:{_clean(self.subject_id)}"


@dataclass(frozen=True, slots=True)
class Decision:
    case_id: str
    situation_id: str
    subject_id: str
    choice: str
    scope: DecisionScope = DecisionScope.LOCAL
    similar_subject_ids: tuple[str, ...] = ()
    threshold: float = SIMILARITY_THRESHOLD

    def __post_init__(self) -> None:
        if not _clean(self.case_id):
            raise ValueError("Une Decision doit appartenir a un Cas.")
        if not _clean(self.situation_id):
            raise ValueError("Une Decision doit viser une Situation.")
        if not _clean(self.subject_id):
            raise ValueError("Une Decision doit viser un objet stable.")
        if not _clean(self.choice):
            raise ValueError("Une Decision doit contenir un choix explicite.")

        scope = DecisionScope(self.scope)
        object.__setattr__(self, "scope", scope)

        threshold = float(self.threshold)
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("Le seuil de similarite doit etre compris entre 0 et 1.")
        object.__setattr__(self, "threshold", threshold)

        similar = _unique_ids(self.similar_subject_ids)
        object.__setattr__(self, "similar_subject_ids", similar)

        if scope == DecisionScope.LOCAL and similar:
            raise ValueError("Une Decision locale ne peut pas contenir de cibles similaires.")

    @property
    def id(self) -> str:
        return (
            f"decision:{_clean(self.situation_id)}:"
            f"{_clean(self.choice)}:{self.scope.value}"
        )


@dataclass(frozen=True, slots=True)
class Rule:
    domain: str
    kind: str
    choice: str
    anchor_subject_id: str
    member_subject_ids: tuple[str, ...]
    scope: DecisionScope
    threshold: float
    source_decision_id: str

    @property
    def id(self) -> str:
        return (
            f"rule:{_clean(self.domain)}:{_clean(self.kind)}:"
            f"{_clean(self.anchor_subject_id)}:{self.scope.value}"
        )

    def applies_to(self, situation: Situation) -> bool:
        return bool(
            _clean(situation.domain) == _clean(self.domain)
            and _clean(situation.kind) == _clean(self.kind)
            and _clean(situation.subject_id) in self.member_subject_ids
        )


def group_cases(situations: Iterable[Situation]) -> tuple[Case, ...]:
    grouped: dict[str, list[Situation]] = {}
    order: list[str] = []

    for situation in situations:
        if not isinstance(situation, Situation):
            raise TypeError("group_cases attend uniquement des Situation.")
        key = _clean(situation.subject_id)
        if key not in grouped:
            grouped[key] = []
            order.append(key)
        grouped[key].append(situation)

    return tuple(
        Case(subject_id=subject_id, situations=tuple(grouped[subject_id]))
        for subject_id in order
    )


def decide(
    case: Case,
    situation_id: str,
    choice: str,
    *,
    scope: DecisionScope = DecisionScope.LOCAL,
    similar_subject_ids: Iterable[str] = (),
    threshold: float = SIMILARITY_THRESHOLD,
) -> Decision:
    wanted = _clean(situation_id)
    situation = next((item for item in case.situations if item.id == wanted), None)
    if situation is None:
        raise KeyError(situation_id)

    selected_scope = DecisionScope(scope)
    targets = _unique_ids(similar_subject_ids)

    if selected_scope == DecisionScope.LOCAL and targets:
        raise ValueError("Les cibles similaires exigent scope=DecisionScope.SIMILAR.")

    return Decision(
        case_id=case.id,
        situation_id=situation.id,
        subject_id=situation.subject_id,
        choice=_clean(choice),
        scope=selected_scope,
        similar_subject_ids=targets,
        threshold=float(threshold),
    )


def rule_from_decision(case: Case, decision: Decision) -> Rule:
    if decision.case_id != case.id:
        raise ValueError("La Decision n'appartient pas a ce Cas.")

    situation = next(
        (item for item in case.situations if item.id == decision.situation_id),
        None,
    )
    if situation is None:
        raise KeyError(decision.situation_id)

    members = [situation.subject_id]
    if decision.scope == DecisionScope.SIMILAR:
        members.extend(decision.similar_subject_ids)

    return Rule(
        domain=situation.domain,
        kind=situation.kind,
        choice=decision.choice,
        anchor_subject_id=situation.subject_id,
        member_subject_ids=_unique_ids(members),
        scope=decision.scope,
        threshold=decision.threshold,
        source_decision_id=decision.id,
    )


def persistence_event(situation: Situation, decision: Decision) -> dict[str, Any]:
    if decision.situation_id != situation.id:
        raise ValueError("La Decision ne correspond pas a cette Situation.")
    return {
        "domain": _clean(situation.domain),
        "stable_id": _clean(situation.subject_id),
        "choice": _clean(decision.choice),
    }


__all__ = [
    "SIMILARITY_THRESHOLD",
    "DecisionScope",
    "Situation",
    "Case",
    "Decision",
    "Rule",
    "group_cases",
    "decide",
    "rule_from_decision",
    "persistence_event",
]