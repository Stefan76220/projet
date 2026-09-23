"""Execution des Decisions Texte de TomeLinea V5.

Ce module ne contient aucun correcteur de texte. Il raccorde le contrat
Situation/Decision V5 aux fonctions V4 deja validees :

- ``prepare_text`` corrige automatiquement les fautes techniques immuables ;
- ``correct_after_approval`` execute le bouton « Corriger » puis verifie
  que l'anomalie a reellement disparu ;
- ``accept_specific_exception`` execute « Laisser comme ca » et memorise
  l'exception volontaire.

Aucune navigation, aucun widget et aucune logique de similarite ne vivent ici.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from src.v4.text_engine import (
    TextEngineReport,
    accept_specific_exception,
    correct_after_approval,
    correction_supported,
    prepare_text,
)

from tomelinea.rules import Decision, DecisionScope, Situation

from .api import text_situations_from_issues


TEXT_CHOICE_CORRECTED = "corrected"
TEXT_CHOICE_IGNORED = "ignored"
TEXT_DECISION_CHOICES = (
    TEXT_CHOICE_CORRECTED,
    TEXT_CHOICE_IGNORED,
)


@dataclass(frozen=True, slots=True)
class TextReviewPreparation:
    """Etat obtenu apres les corrections techniques automatiques."""

    rules: Mapping[str, Any]
    rules_created: bool
    automatic_corrections: tuple[dict[str, Any], ...]
    situations: tuple[Situation, ...]


@dataclass(frozen=True, slots=True)
class TextDecisionExecution:
    """Resultat factuel de l'execution d'une Decision Texte."""

    situation_id: str
    subject_id: str
    choice: str
    changed: bool
    correction: Mapping[str, Any] | None = None
    exception_rule: str = ""


def prepare_text_review(book: Any) -> TextReviewPreparation:
    """Prepare le Texte V5 en deleguant entierement au moteur V4."""

    report: TextEngineReport = prepare_text(book)

    return TextReviewPreparation(
        rules=dict(report.rules),
        rules_created=bool(report.rules_created),
        automatic_corrections=tuple(
            dict(item)
            for item in report.automatic_corrections
        ),
        situations=text_situations_from_issues(
            report.issues,
            book=book,
        ),
    )


def text_issue_from_situation(
    situation: Situation,
) -> dict[str, Any]:
    """Reconstruit le contrat minimal attendu par le moteur Texte V4."""

    if not isinstance(situation, Situation):
        raise TypeError("Une Situation Texte V5 est requise.")

    if str(situation.domain) != "text":
        raise ValueError("Cette Situation n'appartient pas au domaine Texte.")

    facts = dict(situation.facts or {})

    issue_id = str(
        facts.get("issue_id")
        or situation.qualifier
        or situation.id
    ).strip()

    page_id = str(
        situation.page_id
        or ""
    ).strip()

    element_id = str(
        situation.subject_id
        or ""
    ).strip()

    if not page_id:
        raise ValueError("Situation Texte sans page stable.")

    if not element_id:
        raise ValueError("Situation Texte sans element stable.")

    raw_element_ids = facts.get("element_ids", ())
    if isinstance(raw_element_ids, (list, tuple)):
        element_ids = tuple(
            str(value).strip()
            for value in raw_element_ids
            if str(value).strip()
        )
    else:
        element_ids = ()

    if not element_ids:
        element_ids = (element_id,)

    issue = {
        "id": issue_id,
        "key": issue_id,
        "type": str(situation.kind),
        "kind": str(situation.kind),
        "page_id": page_id,
        "element_id": element_id,
        "element_ids": element_ids,
        "title": str(facts.get("title") or ""),
        "technical_term": str(
            facts.get("technical_term")
            or ""
        ),
        "why": str(facts.get("why") or ""),
        "proposal": str(
            facts.get("proposal")
            or ""
        ),
        "geometry": dict(
            facts.get("geometry")
            or {}
        ),
        "source_page": facts.get("source_page"),
        "engine": str(
            facts.get("source_engine")
            or "tomelinea.text_anomalies"
        ),
        "engine_version": str(
            facts.get("source_engine_version")
            or ""
        ),
    }

    return issue


def _validate_text_decision(
    situation: Situation,
    decision: Decision,
) -> str:
    if not isinstance(decision, Decision):
        raise TypeError("Une Decision V5 est requise.")

    if decision.situation_id != situation.id:
        raise ValueError(
            "La Decision ne correspond pas a cette Situation."
        )

    if str(decision.subject_id) != str(situation.subject_id):
        raise ValueError(
            "La Decision ne vise pas le meme objet stable."
        )

    if decision.scope != DecisionScope.LOCAL:
        raise ValueError(
            "L'extension similaire des Decisions Texte "
            "n'est pas encore un moteur valide."
        )

    choice = str(decision.choice or "").strip()

    if choice not in TEXT_DECISION_CHOICES:
        raise ValueError(
            "Choix Texte inconnu : "
            + choice
        )

    return choice


def _text_decision_states(
    book: Any,
) -> dict[str, str]:
    metadata = getattr(
        book,
        "metadata",
        None,
    )

    if not isinstance(metadata, dict):
        raise ValueError(
            "Le Livre ne possede pas de metadonnees modifiables."
        )

    states = metadata.setdefault(
        "text_problem_decisions",
        {},
    )

    if not isinstance(states, dict):
        states = {}
        metadata[
            "text_problem_decisions"
        ] = states

    return states


def execute_text_decision(
    book: Any,
    situation: Situation,
    decision: Decision,
) -> TextDecisionExecution:
    """Execute exactement Corriger ou Laisser comme ca."""

    choice = _validate_text_decision(
        situation,
        decision,
    )

    issue = text_issue_from_situation(
        situation,
    )

    if choice == TEXT_CHOICE_CORRECTED:
        if not correction_supported(
            book,
            issue,
        ):
            raise ValueError(
                "TomeLinea ne possede pas encore de "
                "correction automatique fiable pour ce cas."
            )

        correction = dict(
            correct_after_approval(
                book,
                issue,
            )
            or {}
        )

        issue_id = str(
            issue.get("id")
            or issue.get("key")
            or ""
        )

        if issue_id:
            _text_decision_states(
                book,
            )[issue_id] = TEXT_CHOICE_CORRECTED

        metadata = getattr(
            book,
            "metadata",
            None,
        )

        if isinstance(metadata, dict):
            metadata[
                "text_reflow_requested"
            ] = True

        return TextDecisionExecution(
            situation_id=situation.id,
            subject_id=situation.subject_id,
            choice=choice,
            changed=bool(
                correction.get(
                    "changed",
                    True,
                )
            ),
            correction=correction,
        )

    exception_rule = str(
        accept_specific_exception(
            book,
            issue,
        )
        or ""
    )

    return TextDecisionExecution(
        situation_id=situation.id,
        subject_id=situation.subject_id,
        choice=choice,
        changed=False,
        correction=None,
        exception_rule=exception_rule,
    )


__all__ = [
    "TEXT_CHOICE_CORRECTED",
    "TEXT_CHOICE_IGNORED",
    "TEXT_DECISION_CHOICES",
    "TextReviewPreparation",
    "TextDecisionExecution",
    "prepare_text_review",
    "text_issue_from_situation",
    "execute_text_decision",
]