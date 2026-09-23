"""Situations Couvertures de TomeLinea V5.

La V4 possede deja le detecteur exact des decisions restantes sur les 2e et
3e de couverture : ``inside_cover_confirmation_issues``.

La V5 traduit ces constats en Situations sans changer le Livre.
"""

from __future__ import annotations

from typing import Any

from src.v4.structure_covers import (
    INSIDE_BACK_COVER,
    INSIDE_FRONT_COVER,
    inside_cover_confirmation_issues,
)

from tomelinea.rules import Situation


INSIDE_COVER_CONFIRMATION = "inside_cover_confirmation"
COVER_SITUATION_KINDS = (
    INSIDE_COVER_CONFIRMATION,
)


def cover_issue_to_situation(
    issue: dict[str, Any],
) -> Situation:
    if str(
        issue.get(
            "kind",
            "",
        )
        or ""
    ) != INSIDE_COVER_CONFIRMATION:
        raise ValueError(
            "Type de controle Couverture inconnu."
        )

    face = str(
        issue.get(
            "face",
            "",
        )
        or ""
    ).strip()

    if face not in {
        INSIDE_FRONT_COVER,
        INSIDE_BACK_COVER,
    }:
        raise ValueError(
            "Seules les 2e et 3e de couverture sont concernees."
        )

    cover_page_id = str(
        issue.get(
            "cover_page_id",
            "",
        )
        or ""
    ).strip()

    if not cover_page_id:
        raise ValueError(
            "Decision Couverture sans page physique stable."
        )

    candidate_page_id = str(
        issue.get(
            "candidate_page_id",
            "",
        )
        or ""
    ).strip()

    # Le Survol montre prioritairement la page candidate, car c'est elle que
    # l'utilisateur doit regarder avant de choisir. S'il n'y en a pas, il
    # reste sur la face physique de couverture.
    display_page_id = (
        candidate_page_id
        or cover_page_id
    )

    return Situation(
        domain="cover",
        kind=INSIDE_COVER_CONFIRMATION,
        subject_id=cover_page_id,
        page_id=display_page_id,
        qualifier=face,
        facts={
            "face": face,
            "cover_page_id": cover_page_id,
            "candidate_page_id": (
                candidate_page_id
                or None
            ),
            "candidate_part_id": issue.get(
                "candidate_part_id"
            ),
            "candidate_page_number": issue.get(
                "candidate_page_number"
            ),
            "title": str(
                issue.get(
                    "label",
                    "",
                )
                or ""
            ),
            "why": str(
                issue.get(
                    "message",
                    "",
                )
                or ""
            ),
            "proposal": (
                "Utiliser la page candidate comme contenu de cette face "
                "ou laisser cette face blanche."
            ),
            "choices": (
                "content",
                "blank",
            ),
        },
    )


def cover_situations(
    book: Any,
) -> tuple[Situation, ...]:
    return tuple(
        cover_issue_to_situation(
            issue
        )
        for issue in inside_cover_confirmation_issues(
            book
        )
    )


__all__ = [
    "INSIDE_FRONT_COVER",
    "INSIDE_BACK_COVER",
    "INSIDE_COVER_CONFIRMATION",
    "COVER_SITUATION_KINDS",
    "inside_cover_confirmation_issues",
    "cover_issue_to_situation",
    "cover_situations",
]