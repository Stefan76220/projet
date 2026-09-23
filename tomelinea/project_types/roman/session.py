"""Session applicative Roman de TomeLinea V5.

Cette couche est le point de raccord futur de l'interface V5. Elle ne contient
aucun widget et ne remplace aucun moteur deja valide.

Une Session Roman possede exactement :
- le Projet / Livre commun ;
- UN NavigationState commun ;
- UN SurvolState client de cette Navigation ;
- UN SurvolReviewState durable charge depuis le Livre ;
- UNE preparation Roman issue du profil V5-22.

L'interface reste responsable du rendu. Elle appelle ``page_visible`` lorsque
la page demandee est reellement affichee, puis ``advance`` seulement lorsque
la page est terminee.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from tomelinea.navigation import (
    NavigationState,
    NavigationTarget,
)
from tomelinea.rules import Decision
from tomelinea.survol import (
    FinalReviewRequest,
    ReviewSnapshot,
    SurvolDecisionExecution,
    SurvolReviewState,
    SurvolState,
    execute_current_decision,
    load_review_state,
    request_final_review_page,
    save_review_state,
)

from .review import (
    RomanReviewPreparation,
    open_roman_review_page,
    prepare_roman_review,
)


@dataclass(frozen=True, slots=True)
class RomanDecisionResult:
    execution: SurvolDecisionExecution
    review: ReviewSnapshot
    preparation: RomanReviewPreparation


class RomanSession:
    """Coordonne le parcours Roman sans posseder le rendu."""

    __slots__ = (
        "project",
        "book",
        "navigation",
        "survol",
        "review",
        "_preparation",
    )

    def __init__(
        self,
        project: Any,
        *,
        navigation: NavigationState | None = None,
    ) -> None:
        book = getattr(
            project,
            "book",
            None,
        )

        if book is None:
            raise ValueError(
                "Une Session Roman requiert un Projet avec un Livre."
            )

        if (
            navigation is not None
            and not isinstance(
                navigation,
                NavigationState,
            )
        ):
            raise TypeError(
                "navigation doit etre le NavigationState commun."
            )

        self.project = project
        self.book = book
        self.navigation = (
            navigation
            if navigation is not None
            else NavigationState()
        )
        self.survol = SurvolState(
            self.navigation
        )
        self.review = load_review_state(
            self.book
        )
        self._preparation: RomanReviewPreparation | None = None

    @property
    def preparation(
        self,
    ) -> RomanReviewPreparation | None:
        return self._preparation

    @property
    def prepared(
        self,
    ) -> bool:
        return self._preparation is not None

    def _touch(
        self,
    ) -> None:
        touch = getattr(
            self.project,
            "touch",
            None,
        )

        if callable(
            touch
        ):
            touch()

    def prepare(
        self,
    ) -> RomanReviewPreparation:
        """Prepare les detecteurs Roman sans demarrer la Navigation."""

        preparation = prepare_roman_review(
            self.book
        )
        self._preparation = preparation

        if (
            preparation.text_rules_created
            or preparation.automatic_text_corrections
        ):
            self._touch()

        save_review_state(
            self.book,
            self.review,
        )

        return preparation

    def _require_preparation(
        self,
    ) -> RomanReviewPreparation:
        if self._preparation is None:
            return self.prepare()

        return self._preparation

    def start(
        self,
    ) -> NavigationTarget | None:
        """Prepare le Roman puis demande sa premiere page par Navigation."""

        self._require_preparation()

        return self.survol.start(
            self.book
        )

    def page_visible(
        self,
        page_id: str,
    ) -> ReviewSnapshot:
        """A appeler seulement quand l'hote confirme que la page est visible."""

        preparation = self._require_preparation()

        page_id = str(
            page_id
            or ""
        ).strip()

        if page_id not in getattr(
            self.book,
            "pages",
            {},
        ):
            raise KeyError(
                page_id
            )

        if page_id not in getattr(
            self.book,
            "page_order",
            (),
        ):
            raise ValueError(
                "La page visible n'appartient pas a l'ordre physique courant."
            )

        return open_roman_review_page(
            self.review,
            preparation,
            page_id,
        )

    def execute(
        self,
        decision: Decision,
    ) -> RomanDecisionResult:
        """Execute la Situation courante puis recalcule les constats Roman."""

        current_page_id = str(
            self.review.page_id
            or ""
        )

        execution = execute_current_decision(
            self.project,
            self.review,
            decision,
        )

        preparation = prepare_roman_review(
            self.book
        )
        self._preparation = preparation

        if (
            preparation.text_rules_created
            or preparation.automatic_text_corrections
        ):
            self._touch()

        if (
            current_page_id
            and current_page_id
            in getattr(
                self.book,
                "page_order",
                (),
            )
        ):
            snapshot = open_roman_review_page(
                self.review,
                preparation,
                current_page_id,
            )
        else:
            snapshot = self.review.snapshot

        save_review_state(
            self.book,
            self.review,
        )

        return RomanDecisionResult(
            execution=execution,
            review=snapshot,
            preparation=preparation,
        )

    def advance(
        self,
    ) -> NavigationTarget | None:
        """Avance uniquement si tous les Cas de la page visible sont traites."""

        if not self.review.page_complete:
            raise ValueError(
                "La page courante contient encore une Situation a traiter."
            )

        return self.survol.advance(
            self.book
        )

    def pause(
        self,
        *,
        active_page_id: str | None = None,
    ) -> None:
        self.survol.pause(
            self.book,
            active_page_id=active_page_id,
        )

    def resume(
        self,
        *,
        active_page_id: str | None = None,
    ) -> NavigationTarget | None:
        return self.survol.resume(
            self.book,
            active_page_id=active_page_id,
        )

    def stop(
        self,
        *,
        active_page_id: str | None = None,
    ) -> None:
        self.survol.stop(
            self.book,
            active_page_id=active_page_id,
        )

    def final_review(
        self,
        *,
        after_page_id: str | None = None,
    ) -> FinalReviewRequest | None:
        """Demande la prochaine page A revoir via la MEME Navigation."""

        return request_final_review_page(
            self.survol,
            self.book,
            self.review,
            after_page_id=after_page_id,
        )


__all__ = [
    "RomanDecisionResult",
    "RomanSession",
]