"""Detection deterministe des objets deja vus impactes par une mutation.

Le moteur ne devine pas les impacts. Il photographie les objets stables du
Livre juste avant et juste apres une Decision :

- pages : position physique, cote, relations Structure et contenu ;
- elements : page porteuse, position physique de la page et donnees de
  Composition de l'element.

Seuls les sujets deja ``Vu`` sont candidats a ``A revoir``.
Le sujet que l'utilisateur vient de traiter peut etre explicitement exclu.
Aucune navigation n'est effectuee ici.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from typing import Any, Iterable, Mapping

from src.v4.structure_parity import physical_side

from .review import (
    ReviewStatus,
    SurvolReviewState,
)


def _stable_json(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    )


@dataclass(frozen=True, slots=True)
class BookImpactSnapshot:
    page_signatures: Mapping[str, str]
    element_signatures: Mapping[str, str]


def book_impact_snapshot(
    book: Any,
) -> BookImpactSnapshot:
    pages = getattr(
        book,
        "pages",
        {},
    )

    order = tuple(
        str(value)
        for value in getattr(
            book,
            "page_order",
            (),
        )
    )

    index_by_page = {
        page_id: index
        for index, page_id in enumerate(order)
    }

    page_signatures: dict[str, str] = {}
    element_signatures: dict[str, str] = {}

    for page_id, page in pages.items():
        stable_page_id = str(
            page_id
        )

        try:
            side = physical_side(
                book,
                stable_page_id,
            )
        except Exception:
            side = ""

        content = tuple(
            item
            for item in getattr(
                page,
                "content",
                (),
            )
            if isinstance(
                item,
                dict,
            )
        )

        element_ids = tuple(
            str(
                item.get(
                    "id",
                    "",
                )
                or ""
            )
            for item in content
            if str(
                item.get(
                    "id",
                    "",
                )
                or ""
            )
        )

        page_signatures[
            stable_page_id
        ] = _stable_json(
            {
                "index": index_by_page.get(
                    stable_page_id,
                    -1,
                ),
                "physical_side": side,
                "page_type": str(
                    getattr(
                        page,
                        "page_type",
                        "",
                    )
                    or ""
                ),
                "recto_verso": getattr(
                    page,
                    "recto_verso",
                    None,
                ),
                "spread_id": getattr(
                    page,
                    "spread_id",
                    None,
                ),
                "spread_side": getattr(
                    page,
                    "spread_side",
                    None,
                ),
                "auto_before": tuple(
                    str(value)
                    for value in getattr(
                        page,
                        "auto_before",
                        (),
                    )
                ),
                "auto_after": tuple(
                    str(value)
                    for value in getattr(
                        page,
                        "auto_after",
                        (),
                    )
                ),
                "is_compensation": bool(
                    getattr(
                        page,
                        "is_compensation",
                        False,
                    )
                ),
                "element_ids": element_ids,
            }
        )

        for element in content:
            element_id = str(
                element.get(
                    "id",
                    "",
                )
                or ""
            ).strip()

            if not element_id:
                continue

            element_signatures[
                element_id
            ] = _stable_json(
                {
                    "page_id": stable_page_id,
                    "page_index": index_by_page.get(
                        stable_page_id,
                        -1,
                    ),
                    "physical_side": side,
                    "element": element,
                }
            )

    return BookImpactSnapshot(
        page_signatures=page_signatures,
        element_signatures=element_signatures,
    )


def _subject_signature(
    snapshot: BookImpactSnapshot,
    subject_id: str,
) -> tuple[str | None, str | None]:
    subject_id = str(
        subject_id
        or ""
    ).strip()

    return (
        snapshot.page_signatures.get(
            subject_id
        ),
        snapshot.element_signatures.get(
            subject_id
        ),
    )


def seen_subject_ids(
    review: SurvolReviewState,
) -> tuple[str, ...]:
    payload = review.export_state()

    raw = payload.get(
        "known_situations",
        {},
    )

    if not isinstance(
        raw,
        Mapping,
    ):
        return ()

    result = []

    for subject_id in raw:
        value = str(
            subject_id
            or ""
        ).strip()

        if (
            value
            and review.status(
                value
            ) == ReviewStatus.SEEN
        ):
            result.append(
                value
            )

    return tuple(
        sorted(
            result
        )
    )


def changed_subject_ids(
    before: BookImpactSnapshot,
    after: BookImpactSnapshot,
    subject_ids: Iterable[str],
    *,
    exclude: Iterable[str] = (),
) -> tuple[str, ...]:
    excluded = {
        str(value or "").strip()
        for value in exclude
        if str(value or "").strip()
    }

    changed: list[str] = []

    for raw in subject_ids:
        subject_id = str(
            raw
            or ""
        ).strip()

        if (
            not subject_id
            or subject_id in excluded
        ):
            continue

        before_signature = _subject_signature(
            before,
            subject_id,
        )
        after_signature = _subject_signature(
            after,
            subject_id,
        )

        if before_signature != after_signature:
            changed.append(
                subject_id
            )

    return tuple(
        sorted(
            set(
                changed
            )
        )
    )


def impacted_seen_subject_ids(
    review: SurvolReviewState,
    before: BookImpactSnapshot,
    after: BookImpactSnapshot,
    *,
    exclude: Iterable[str] = (),
) -> tuple[str, ...]:
    return changed_subject_ids(
        before,
        after,
        seen_subject_ids(
            review
        ),
        exclude=exclude,
    )


__all__ = [
    "BookImpactSnapshot",
    "book_impact_snapshot",
    "seen_subject_ids",
    "changed_subject_ids",
    "impacted_seen_subject_ids",
]