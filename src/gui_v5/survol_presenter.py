from __future__ import annotations

"""Presentation grand public des Situations du Survol V5.

Ce module ne dessine aucun widget et n'execute aucune correction.
Il traduit seulement la Situation courante vers les libelles et choix que
l'interface peut afficher.
"""

from dataclasses import dataclass

from tomelinea.covers import (
    COVER_CHOICE_BLANK,
    COVER_CHOICE_CONTENT,
)
from tomelinea.images import (
    IMAGE_CHOICE_CORRECTED,
    IMAGE_CHOICE_IGNORED,
    IMAGE_QUALITY_CRITICAL,
)
from tomelinea.rules import (
    Decision,
    Situation,
    decide,
)
from tomelinea.survol import SurvolReviewState
from tomelinea.text import (
    TEXT_CHOICE_CORRECTED,
    TEXT_CHOICE_IGNORED,
)


@dataclass(frozen=True, slots=True)
class SurvolChoice:
    choice: str
    label: str
    enabled: bool = True
    accent: bool = False


@dataclass(frozen=True, slots=True)
class SurvolPresentation:
    domain: str
    title: str
    technical_term: str
    why: str
    proposal: str
    choices: tuple[SurvolChoice, ...]


def presentation_for_situation(
    situation: Situation,
) -> SurvolPresentation:
    if not isinstance(
        situation,
        Situation,
    ):
        raise TypeError(
            "Une Situation V5 est requise."
        )

    facts = dict(
        situation.facts
        or {}
    )

    domain = str(
        situation.domain
        or ""
    ).strip()

    title = str(
        facts.get(
            "title",
            "",
        )
        or ""
    ).strip()

    technical_term = str(
        facts.get(
            "technical_term",
            "",
        )
        or ""
    ).strip()

    why = str(
        facts.get(
            "why",
            facts.get(
                "help",
                "",
            ),
        )
        or ""
    ).strip()

    proposal = str(
        facts.get(
            "proposal",
            "",
        )
        or ""
    ).strip()

    if not title:
        title = "Ce point mérite votre attention"

    choices: tuple[SurvolChoice, ...]

    if domain == "text":
        can_correct = bool(
            facts.get(
                "correction_supported",
                False,
            )
        )

        choices = (
            SurvolChoice(
                choice=TEXT_CHOICE_CORRECTED,
                label="Corriger",
                enabled=can_correct,
                accent=can_correct,
            ),
            SurvolChoice(
                choice=TEXT_CHOICE_IGNORED,
                label="Laisser comme ça",
                enabled=True,
                accent=not can_correct,
            ),
        )

    elif domain == "image":
        can_correct = (
            str(
                situation.kind
            )
            == IMAGE_QUALITY_CRITICAL
        )

        choices = (
            SurvolChoice(
                choice=IMAGE_CHOICE_CORRECTED,
                label="Corriger",
                enabled=can_correct,
                accent=can_correct,
            ),
            SurvolChoice(
                choice=IMAGE_CHOICE_IGNORED,
                label="Laisser comme ça",
                enabled=True,
                accent=not can_correct,
            ),
        )

    elif domain == "cover":
        candidate = str(
            facts.get(
                "candidate_page_id",
                "",
            )
            or ""
        ).strip()

        choices = (
            SurvolChoice(
                choice=COVER_CHOICE_CONTENT,
                label="Utiliser cette page",
                enabled=bool(
                    candidate
                ),
                accent=bool(
                    candidate
                ),
            ),
            SurvolChoice(
                choice=COVER_CHOICE_BLANK,
                label="Laisser blanc",
                enabled=True,
                accent=not bool(
                    candidate
                ),
            ),
        )

    else:
        choices = ()

    return SurvolPresentation(
        domain=domain,
        title=title,
        technical_term=technical_term,
        why=why,
        proposal=proposal,
        choices=choices,
    )


def decision_for_current(
    review: SurvolReviewState,
    choice: str,
) -> Decision:
    if not isinstance(
        review,
        SurvolReviewState,
    ):
        raise TypeError(
            "Un SurvolReviewState commun est requis."
        )

    case = review.current_case
    situation = review.current_situation

    if case is None or situation is None:
        raise ValueError(
            "Aucune Situation courante a decider."
        )

    return decide(
        case,
        situation.id,
        str(
            choice
            or ""
        ).strip(),
    )


__all__ = [
    "SurvolChoice",
    "SurvolPresentation",
    "presentation_for_situation",
    "decision_for_current",
]