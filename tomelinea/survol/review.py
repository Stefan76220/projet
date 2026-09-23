"""Revue des Cas pendant le Survol TomeLinea V5.

Ce module ne navigue jamais. Il ne connait ni Tk, ni Canvas, ni WebView.

Responsabilites :
- regrouper les Situations d'une page en Cas par identifiant stable ;
- presenter les Situations d'un Cas une par une ;
- ne declarer la page traitee qu'apres tous ses Cas ;
- conserver l'etat Nouveau / Vu / A revoir par identifiant stable ;
- ne pas reproposer un Cas deja Vu si rien de nouveau n'est apparu ;
- reproposer un objet marque A revoir sans provoquer de retour automatique.

La Navigation reste exclusivement la responsabilite de SurvolState /
NavigationState.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable, Mapping

from tomelinea.rules import Case, Situation, group_cases


REVIEW_SCHEMA = "tomelinea.survol_review.v1"


class ReviewStatus(str, Enum):
    NEW = "new"
    SEEN = "seen"
    REVIEW = "review"


REVIEW_STATUS_LABELS = {
    ReviewStatus.NEW: "Nouveau",
    ReviewStatus.SEEN: "Vu",
    ReviewStatus.REVIEW: "À revoir",
}


@dataclass(frozen=True, slots=True)
class ReviewSnapshot:
    page_id: str
    case_index: int
    case_count: int
    situation_index: int
    situation_count: int
    current_case: Case | None
    current_situation: Situation | None
    page_complete: bool


class SurvolReviewState:
    """Etat de revue local au Survol, sans moteur de navigation."""

    __slots__ = (
        "_page_id",
        "_cases",
        "_case_index",
        "_situation_index",
        "_known_situations",
        "_forced_review",
    )

    def __init__(self) -> None:
        self._page_id = ""
        self._cases: tuple[Case, ...] = ()
        self._case_index = 0
        self._situation_index = 0
        self._known_situations: dict[str, set[str]] = {}
        self._forced_review: set[str] = set()

    @property
    def page_id(self) -> str:
        return self._page_id

    @property
    def current_case(self) -> Case | None:
        if not self._cases:
            return None

        if not 0 <= self._case_index < len(self._cases):
            return None

        return self._cases[self._case_index]

    @property
    def current_situation(self) -> Situation | None:
        case = self.current_case

        if case is None:
            return None

        if not 0 <= self._situation_index < len(case.situations):
            return None

        return case.situations[self._situation_index]

    @property
    def page_complete(self) -> bool:
        return self.current_case is None

    @property
    def snapshot(self) -> ReviewSnapshot:
        case = self.current_case
        situation = self.current_situation

        return ReviewSnapshot(
            page_id=self._page_id,
            case_index=self._case_index,
            case_count=len(self._cases),
            situation_index=self._situation_index,
            situation_count=(
                len(case.situations)
                if case is not None
                else 0
            ),
            current_case=case,
            current_situation=situation,
            page_complete=case is None,
        )

    def status(self, subject_id: str) -> ReviewStatus:
        subject_id = str(subject_id or "").strip()

        if subject_id in self._forced_review:
            return ReviewStatus.REVIEW

        if subject_id in self._known_situations:
            return ReviewStatus.SEEN

        return ReviewStatus.NEW

    def status_label(self, subject_id: str) -> str:
        return REVIEW_STATUS_LABELS[
            self.status(subject_id)
        ]

    def case_status(self, case: Case) -> ReviewStatus:
        subject_id = str(case.subject_id)

        if subject_id in self._forced_review:
            return ReviewStatus.REVIEW

        known = self._known_situations.get(
            subject_id,
            set(),
        )

        if not known:
            return ReviewStatus.NEW

        current_ids = {
            situation.id
            for situation in case.situations
        }

        if current_ids.issubset(known):
            return ReviewStatus.SEEN

        return ReviewStatus.NEW

    def _pending_cases(
        self,
        cases: Iterable[Case],
    ) -> tuple[Case, ...]:
        pending: list[Case] = []

        for case in cases:
            status = self.case_status(case)

            if status == ReviewStatus.SEEN:
                continue

            known = self._known_situations.get(
                str(case.subject_id),
                set(),
            )

            if status == ReviewStatus.REVIEW:
                situations = case.situations
            else:
                situations = tuple(
                    situation
                    for situation in case.situations
                    if situation.id not in known
                )

            if not situations:
                continue

            pending.append(
                Case(
                    subject_id=case.subject_id,
                    situations=tuple(situations),
                )
            )

        return tuple(pending)

    def open_page(
        self,
        page_id: str,
        situations: Iterable[Situation],
    ) -> ReviewSnapshot:
        """Charge uniquement les Cas de la page physique courante."""

        page_id = str(page_id or "").strip()

        if not page_id:
            raise ValueError("Le Survol doit ouvrir une page stable.")

        page_situations = tuple(
            situation
            for situation in situations
            if str(situation.page_id or "") == page_id
        )

        self._page_id = page_id
        self._cases = self._pending_cases(
            group_cases(page_situations)
        )
        self._case_index = 0
        self._situation_index = 0

        return self.snapshot

    def complete_current_situation(self) -> ReviewSnapshot:
        """Valide UNE Situation puis avance dans le meme Cas avant la page."""

        case = self.current_case
        situation = self.current_situation

        if case is None or situation is None:
            return self.snapshot

        subject_id = str(case.subject_id)

        known = self._known_situations.setdefault(
            subject_id,
            set(),
        )
        known.add(
            situation.id
        )

        next_situation = self._situation_index + 1

        if next_situation < len(case.situations):
            self._situation_index = next_situation
            return self.snapshot

        self._forced_review.discard(
            subject_id
        )

        self._case_index += 1
        self._situation_index = 0

        return self.snapshot

    def mark_seen(
        self,
        situations: Iterable[Situation],
    ) -> None:
        """Marque comme deja traitees des Situations couvertes par une regle."""

        grouped = group_cases(
            situations
        )

        for case in grouped:
            subject_id = str(case.subject_id)

            known = self._known_situations.setdefault(
                subject_id,
                set(),
            )

            known.update(
                situation.id
                for situation in case.situations
            )

            self._forced_review.discard(
                subject_id
            )

    def mark_for_review(
        self,
        subject_ids: Iterable[str],
    ) -> None:
        """Marque A revoir sans changer la page courante ni naviguer."""

        for raw in subject_ids:
            subject_id = str(raw or "").strip()

            if not subject_id:
                continue

            self._forced_review.add(
                subject_id
            )

    def clear_review_flag(
        self,
        subject_id: str,
    ) -> None:
        self._forced_review.discard(
            str(subject_id or "").strip()
        )

    def export_state(self) -> dict[str, object]:
        """Exporte uniquement l'etat durable, jamais le curseur de navigation."""

        return {
            "schema": REVIEW_SCHEMA,
            "known_situations": {
                subject_id: sorted(situation_ids)
                for subject_id, situation_ids
                in sorted(self._known_situations.items())
                if subject_id and situation_ids
            },
            "forced_review": sorted(
                subject_id
                for subject_id in self._forced_review
                if subject_id
            ),
        }

    def restore_state(
        self,
        payload: Mapping[str, object] | None,
    ) -> None:
        """Restaure l'etat durable et remet le curseur transitoire a zero."""

        self._page_id = ""
        self._cases = ()
        self._case_index = 0
        self._situation_index = 0
        self._known_situations = {}
        self._forced_review = set()

        if not isinstance(payload, Mapping):
            return

        if str(payload.get("schema") or "") != REVIEW_SCHEMA:
            return

        raw_known = payload.get(
            "known_situations",
            {},
        )

        if isinstance(raw_known, Mapping):
            for raw_subject_id, raw_ids in raw_known.items():
                subject_id = str(raw_subject_id or "").strip()

                if not subject_id:
                    continue

                if not isinstance(raw_ids, (list, tuple, set)):
                    continue

                values = {
                    str(value or "").strip()
                    for value in raw_ids
                    if str(value or "").strip()
                }

                if values:
                    self._known_situations[subject_id] = values

        raw_review = payload.get(
            "forced_review",
            (),
        )

        if isinstance(raw_review, (list, tuple, set)):
            self._forced_review = {
                str(value or "").strip()
                for value in raw_review
                if str(value or "").strip()
            }

    @classmethod
    def from_state(
        cls,
        payload: Mapping[str, object] | None,
    ) -> "SurvolReviewState":
        state = cls()
        state.restore_state(
            payload
        )
        return state


__all__ = [
    "REVIEW_SCHEMA",
    "ReviewStatus",
    "REVIEW_STATUS_LABELS",
    "ReviewSnapshot",
    "SurvolReviewState",
]