"""Passage final des objets ``A revoir`` du Survol TomeLinea V5.

Il ne s'agit pas d'un second moteur de Survol.

Le plan est recalcule a chaque demande depuis :
- les identifiants stables marques ``A revoir`` ;
- la position physique ACTUELLE des pages dans le Livre.

Aucune file de navigation n'est conservee. Les demandes passent directement
par le ``NavigationState`` deja partage par le Survol principal.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from tomelinea.navigation import NavigationTarget

from .api import SurvolState
from .review import SurvolReviewState


@dataclass(frozen=True, slots=True)
class FinalReviewTarget:
    page_id: str
    global_index: int
    subject_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FinalReviewPlan:
    targets: tuple[FinalReviewTarget, ...]
    unresolved_subject_ids: tuple[str, ...]

    @property
    def empty(self) -> bool:
        return not self.targets


@dataclass(frozen=True, slots=True)
class FinalReviewRequest:
    target: FinalReviewTarget
    navigation: NavigationTarget


def review_subject_ids(
    review: SurvolReviewState,
) -> tuple[str, ...]:
    if not isinstance(
        review,
        SurvolReviewState,
    ):
        raise TypeError(
            "Un SurvolReviewState est requis."
        )

    payload = review.export_state()

    raw = payload.get(
        "forced_review",
        (),
    )

    if not isinstance(
        raw,
        (list, tuple, set),
    ):
        return ()

    return tuple(
        sorted(
            {
                str(value or "").strip()
                for value in raw
                if str(value or "").strip()
            }
        )
    )


def _element_pages(
    book: Any,
) -> dict[str, str]:
    result: dict[str, str] = {}

    for page_id in getattr(
        book,
        "page_order",
        (),
    ):
        stable_page_id = str(
            page_id
        )

        page = getattr(
            book,
            "pages",
            {},
        ).get(
            stable_page_id
        )

        if page is None:
            continue

        for element in getattr(
            page,
            "content",
            (),
        ):
            if not isinstance(
                element,
                Mapping,
            ):
                continue

            element_id = str(
                element.get(
                    "id",
                    "",
                )
                or ""
            ).strip()

            if (
                element_id
                and element_id not in result
            ):
                result[
                    element_id
                ] = stable_page_id

    return result


def final_review_plan(
    book: Any,
    review: SurvolReviewState,
) -> FinalReviewPlan:
    """Construit un instantane, jamais une file persistante."""

    order = tuple(
        str(value)
        for value in getattr(
            book,
            "page_order",
            (),
        )
    )

    pages = getattr(
        book,
        "pages",
        {},
    )

    index_by_page = {
        page_id: index
        for index, page_id in enumerate(
            order
        )
    }

    element_pages = _element_pages(
        book
    )

    grouped: dict[str, list[str]] = {}
    unresolved: list[str] = []

    for subject_id in review_subject_ids(
        review
    ):
        if (
            subject_id in pages
            and subject_id in index_by_page
        ):
            page_id = subject_id
        else:
            page_id = element_pages.get(
                subject_id,
                "",
            )

        if (
            not page_id
            or page_id not in index_by_page
        ):
            unresolved.append(
                subject_id
            )
            continue

        grouped.setdefault(
            page_id,
            [],
        ).append(
            subject_id
        )

    targets = tuple(
        FinalReviewTarget(
            page_id=page_id,
            global_index=index_by_page[
                page_id
            ],
            subject_ids=tuple(
                sorted(
                    set(
                        grouped[
                            page_id
                        ]
                    )
                )
            ),
        )
        for page_id in sorted(
            grouped,
            key=lambda value: index_by_page[
                value
            ],
        )
    )

    return FinalReviewPlan(
        targets=targets,
        unresolved_subject_ids=tuple(
            sorted(
                set(
                    unresolved
                )
            )
        ),
    )


def next_final_review_target(
    book: Any,
    review: SurvolReviewState,
    *,
    after_page_id: str | None = None,
) -> FinalReviewTarget | None:
    """Retourne la prochaine cible dans l'ordre physique ACTUEL."""

    plan = final_review_plan(
        book,
        review,
    )

    if not plan.targets:
        return None

    after = str(
        after_page_id
        or ""
    ).strip()

    if not after:
        return plan.targets[0]

    order = tuple(
        str(value)
        for value in getattr(
            book,
            "page_order",
            (),
        )
    )

    try:
        after_index = order.index(
            after
        )
    except ValueError as exc:
        raise ValueError(
            "La page de reference n'existe plus dans l'ordre physique."
        ) from exc

    return next(
        (
            target
            for target in plan.targets
            if target.global_index > after_index
        ),
        None,
    )


def request_final_review_page(
    survol: SurvolState,
    book: Any,
    review: SurvolReviewState,
    *,
    after_page_id: str | None = None,
) -> FinalReviewRequest | None:
    """Demande une cible finale par la Navigation commune du Survol."""

    if not isinstance(
        survol,
        SurvolState,
    ):
        raise TypeError(
            "Le SurvolState commun est requis."
        )

    if not survol.completed:
        raise ValueError(
            "Le passage A revoir ne commence qu'apres le Survol principal."
        )

    target = next_final_review_target(
        book,
        review,
        after_page_id=after_page_id,
    )

    if target is None:
        return None

    navigation_target = survol.navigation.request_page(
        book,
        target.page_id,
    )

    return FinalReviewRequest(
        target=target,
        navigation=navigation_target,
    )


__all__ = [
    "FinalReviewTarget",
    "FinalReviewPlan",
    "FinalReviewRequest",
    "review_subject_ids",
    "final_review_plan",
    "next_final_review_target",
    "request_final_review_page",
]