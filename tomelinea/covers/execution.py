"""Execution des Decisions Couvertures de TomeLinea V5.

Les deux choix sont exactement ceux de la V4 :
- ``content`` : affecter explicitement la page candidate a la 2e/3e ;
- ``blank`` : conserver/remettre cette face en blanc.

Aucune affectation automatique et aucune similarite.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.v4.structure_covers import (
    assign_page_as_inside_cover,
    blank_inside_cover,
    cover_ids,
    inside_cover_confirmation_issues,
    inside_cover_confirmation_status,
)

from tomelinea.rules import (
    Decision,
    DecisionScope,
    Situation,
)

from .api import (
    INSIDE_COVER_CONFIRMATION,
)


COVER_CHOICE_CONTENT = "content"
COVER_CHOICE_BLANK = "blank"
COVER_DECISION_CHOICES = (
    COVER_CHOICE_CONTENT,
    COVER_CHOICE_BLANK,
)


@dataclass(frozen=True, slots=True)
class CoverDecisionExecution:
    situation_id: str
    subject_id: str
    face: str
    choice: str
    result_page_id: str
    candidate_page_id: str | None


def _book(
    project: Any,
) -> Any:
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


def _touch(
    project: Any,
) -> None:
    touch = getattr(
        project,
        "touch",
        None,
    )

    if callable(
        touch
    ):
        touch()


def _validate(
    situation: Situation,
    decision: Decision,
) -> str:
    if not isinstance(
        situation,
        Situation,
    ):
        raise TypeError(
            "Une Situation Couverture V5 est requise."
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
    ) != "cover":
        raise ValueError(
            "Cette Situation n'appartient pas au domaine Couverture."
        )

    if str(
        situation.kind
    ) != INSIDE_COVER_CONFIRMATION:
        raise ValueError(
            "Situation Couverture non prise en charge."
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
            "La Decision ne vise pas la meme face physique."
        )

    if decision.scope != DecisionScope.LOCAL:
        raise ValueError(
            "Une decision de couverture ne s'etend jamais par similarite."
        )

    choice = str(
        decision.choice
        or ""
    ).strip()

    if choice not in COVER_DECISION_CHOICES:
        raise ValueError(
            "Choix Couverture inconnu : "
            + choice
        )

    return choice


def _current_issue(
    book: Any,
    situation: Situation,
) -> dict[str, Any]:
    facts = dict(
        situation.facts
        or {}
    )

    expected_face = str(
        facts.get(
            "face",
            "",
        )
        or ""
    )

    expected_cover_id = str(
        facts.get(
            "cover_page_id",
            "",
        )
        or ""
    )

    expected_candidate = str(
        facts.get(
            "candidate_page_id",
            "",
        )
        or ""
    )

    for issue in inside_cover_confirmation_issues(
        book
    ):
        if str(
            issue.get(
                "face",
                "",
            )
            or ""
        ) != expected_face:
            continue

        if str(
            issue.get(
                "cover_page_id",
                "",
            )
            or ""
        ) != expected_cover_id:
            raise ValueError(
                "La face de couverture a change depuis la Decision."
            )

        current_candidate = str(
            issue.get(
                "candidate_page_id",
                "",
            )
            or ""
        )

        if current_candidate != expected_candidate:
            raise ValueError(
                "La page candidate a change depuis la Decision."
            )

        return issue

    raise ValueError(
        "Cette decision de couverture n'est plus en attente."
    )


def execute_cover_decision(
    project: Any,
    situation: Situation,
    decision: Decision,
) -> CoverDecisionExecution:
    choice = _validate(
        situation,
        decision,
    )

    book = _book(
        project
    )

    issue = _current_issue(
        book,
        situation,
    )

    face = str(
        issue[
            "face"
        ]
    )

    candidate = (
        str(
            issue.get(
                "candidate_page_id",
                "",
            )
            or ""
        )
        or None
    )

    if choice == COVER_CHOICE_CONTENT:
        if not candidate:
            raise ValueError(
                "Aucune page candidate n'est disponible pour cette face."
            )

        result_page_id = assign_page_as_inside_cover(
            book,
            face,
            candidate,
        )
    else:
        result_page_id = blank_inside_cover(
            book,
            face,
        )

    current_ids = cover_ids(
        book
    )

    active_cover_id = current_ids.get(
        face
    )

    if active_cover_id is None:
        raise ValueError(
            "La face de couverture a disparu apres la Decision."
        )

    active_page = book.pages[
        active_cover_id
    ]

    expected_status = (
        "content"
        if choice == COVER_CHOICE_CONTENT
        else "blank"
    )

    if inside_cover_confirmation_status(
        active_page
    ) != expected_status:
        raise ValueError(
            "La Decision Couverture n'a pas ete materialisee correctement."
        )

    remaining = {
        str(
            item.get(
                "face",
                "",
            )
            or ""
        )
        for item in inside_cover_confirmation_issues(
            book
        )
    }

    if face in remaining:
        raise ValueError(
            "La face reste en attente apres la Decision."
        )

    _touch(
        project
    )

    return CoverDecisionExecution(
        situation_id=situation.id,
        subject_id=situation.subject_id,
        face=face,
        choice=choice,
        result_page_id=str(
            result_page_id
        ),
        candidate_page_id=candidate,
    )


__all__ = [
    "COVER_CHOICE_CONTENT",
    "COVER_CHOICE_BLANK",
    "COVER_DECISION_CHOICES",
    "CoverDecisionExecution",
    "execute_cover_decision",
]