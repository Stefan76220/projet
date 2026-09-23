"""Orchestration d'une Decision depuis le Survol TomeLinea V5.

Cette couche ne corrige rien et ne navigue jamais.

Elle prend uniquement la Situation courante de ``SurvolReviewState`` :
1. photographie les objets stables deja vus ;
2. delegue l'execution au moteur specialise deja valide ;
3. marque A revoir les objets deja vus reellement impactes ;
4. avance d'une Situation uniquement si l'execution reussit ;
5. persiste immediatement la revue dans ``Book.metadata``.

Le passage a la page suivante reste exclusivement la responsabilite de
``SurvolState`` et de la Navigation commune.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from tomelinea.images import (
    execute_image_decision,
)
from tomelinea.pagination import (
    execute_pagination_decision,
)
from tomelinea.rules import (
    Decision,
    Situation,
)
from tomelinea.text import (
    execute_text_decision,
)

from .impact import (
    book_impact_snapshot,
    impacted_seen_subject_ids,
)
from .persistence import (
    save_review_state,
)
from .review import (
    ReviewSnapshot,
    SurvolReviewState,
)


@dataclass(frozen=True, slots=True)
class SurvolDecisionExecution:
    domain: str
    situation_id: str
    subject_id: str
    decision_id: str
    domain_result: Any
    impacted_subject_ids: tuple[str, ...]
    review: ReviewSnapshot
    persisted_state: Mapping[str, object]

    @property
    def page_complete(self) -> bool:
        return bool(
            self.review.page_complete
        )


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


def _validate_current_decision(
    review: SurvolReviewState,
    decision: Decision,
) -> Situation:
    if not isinstance(
        review,
        SurvolReviewState,
    ):
        raise TypeError(
            "Un SurvolReviewState est requis."
        )

    if not isinstance(
        decision,
        Decision,
    ):
        raise TypeError(
            "Une Decision V5 est requise."
        )

    situation = review.current_situation

    if situation is None:
        raise ValueError(
            "Aucune Situation courante a traiter."
        )

    if decision.situation_id != situation.id:
        raise ValueError(
            "La Decision ne vise pas la Situation courante du Survol."
        )

    if str(
        decision.subject_id
    ) != str(
        situation.subject_id
    ):
        raise ValueError(
            "La Decision ne vise pas l'objet stable du Cas courant."
        )

    return situation


def _execute_domain(
    project: Any,
    situation: Situation,
    decision: Decision,
) -> Any:
    domain = str(
        situation.domain
        or ""
    ).strip()

    if domain == "text":
        return execute_text_decision(
            _book(project),
            situation,
            decision,
        )

    if domain == "pagination":
        return execute_pagination_decision(
            project,
            situation,
            decision,
        )

    if domain == "image":
        return execute_image_decision(
            _book(project),
            situation,
            decision,
        )

    raise ValueError(
        "Domaine de Situation non executable par le Survol : "
        + domain
    )


def execute_current_decision(
    project: Any,
    review: SurvolReviewState,
    decision: Decision,
) -> SurvolDecisionExecution:
    """Execute UNE Decision sans retour automatique vers les impacts anciens."""

    book = _book(
        project
    )

    situation = _validate_current_decision(
        review,
        decision,
    )

    before = book_impact_snapshot(
        book
    )

    # Si le moteur specialise leve une erreur, la revue n'avance pas.
    result = _execute_domain(
        project,
        situation,
        decision,
    )

    after = book_impact_snapshot(
        book
    )

    impacted = impacted_seen_subject_ids(
        review,
        before,
        after,
        exclude=(
            str(
                situation.subject_id
            ),
        ),
    )

    if impacted:
        review.mark_for_review(
            impacted
        )

    snapshot = review.complete_current_situation()

    persisted = save_review_state(
        book,
        review,
    )

    return SurvolDecisionExecution(
        domain=str(situation.domain),
        situation_id=situation.id,
        subject_id=str(situation.subject_id),
        decision_id=decision.id,
        domain_result=result,
        impacted_subject_ids=impacted,
        review=snapshot,
        persisted_state=persisted,
    )


__all__ = [
    "SurvolDecisionExecution",
    "execute_current_decision",
]