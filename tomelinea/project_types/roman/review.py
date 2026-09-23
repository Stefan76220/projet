"""Profil Roman du Survol commun TomeLinea V5.

Le Roman ne possede pas son propre moteur de navigation ou de revue.

Ce profil raccorde seulement les detecteurs deja valides :
- Texte : preparation V4 + corrections techniques automatiques ;
- Images : qualite d'impression ;
- Couvertures : decisions 2e / 3e encore en attente.

Les Situations sont ensuite triees dans l'ordre PHYSIQUE du Livre. Ainsi le
Survol ne fait jamais un passage Texte puis Images puis Couvertures : il avance
page par page et traite sur chaque page tous les Cas presents.

Les contraintes de Pagination ne sont pas generees automatiquement ici :
la V4 n'a pas de detecteur global qui justifierait de les inventer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from tomelinea.covers import cover_situations
from tomelinea.images import image_quality_situations
from tomelinea.rules import Situation
from tomelinea.survol import ReviewSnapshot, SurvolReviewState
from tomelinea.text import prepare_text_review


@dataclass(frozen=True, slots=True)
class RomanReviewPreparation:
    text_rules: Mapping[str, Any]
    text_rules_created: bool
    automatic_text_corrections: tuple[dict[str, Any], ...]
    situations: tuple[Situation, ...]
    unresolved_situations: tuple[Situation, ...]

    def situations_for_page(
        self,
        page_id: str,
    ) -> tuple[Situation, ...]:
        wanted = str(
            page_id
            or ""
        ).strip()

        return tuple(
            situation
            for situation in self.situations
            if str(
                situation.page_id
                or ""
            ) == wanted
        )


def _page_index(
    book: Any,
) -> dict[str, int]:
    return {
        str(page_id): index
        for index, page_id in enumerate(
            getattr(
                book,
                "page_order",
                (),
            )
        )
    }


def _element_geometry(
    book: Any,
    page_id: str,
    subject_id: str,
) -> tuple[float, float]:
    page = getattr(
        book,
        "pages",
        {},
    ).get(
        str(page_id)
    )

    if page is None:
        return (
            float("inf"),
            float("inf"),
        )

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

        if str(
            element.get(
                "id",
                "",
            )
            or ""
        ) != str(
            subject_id
        ):
            continue

        geometry = element.get(
            "geometry",
            {},
        )

        if not isinstance(
            geometry,
            Mapping,
        ):
            break

        try:
            return (
                float(
                    geometry.get(
                        "y_mm",
                        float("inf"),
                    )
                ),
                float(
                    geometry.get(
                        "x_mm",
                        float("inf"),
                    )
                ),
            )
        except (
            TypeError,
            ValueError,
        ):
            break

    return (
        float("inf"),
        float("inf"),
    )


def _situation_position(
    book: Any,
    situation: Situation,
) -> tuple[float, float]:
    facts = dict(
        situation.facts
        or {}
    )

    geometry = facts.get(
        "geometry"
    )

    if isinstance(
        geometry,
        Mapping,
    ):
        try:
            return (
                float(
                    geometry.get(
                        "y_mm",
                        float("inf"),
                    )
                ),
                float(
                    geometry.get(
                        "x_mm",
                        float("inf"),
                    )
                ),
            )
        except (
            TypeError,
            ValueError,
        ):
            pass

    return _element_geometry(
        book,
        str(
            situation.page_id
            or ""
        ),
        str(
            situation.subject_id
        ),
    )


def _domain_priority(
    situation: Situation,
) -> int:
    # Une decision Couverture porte sur le statut de la page candidate entiere
    # et doit donc etre presentee avant ses objets internes.
    if str(
        situation.domain
    ) == "cover":
        return 0

    return 1


def _ordered_situations(
    book: Any,
    situations: Iterable[Situation],
) -> tuple[
    tuple[Situation, ...],
    tuple[Situation, ...],
]:
    indices = _page_index(
        book
    )

    located: list[Situation] = []
    unresolved: list[Situation] = []
    seen: set[str] = set()

    for situation in situations:
        if not isinstance(
            situation,
            Situation,
        ):
            raise TypeError(
                "Le profil Roman attend uniquement des Situation."
            )

        if situation.id in seen:
            continue

        seen.add(
            situation.id
        )

        page_id = str(
            situation.page_id
            or ""
        ).strip()

        if page_id not in indices:
            unresolved.append(
                situation
            )
            continue

        located.append(
            situation
        )

    located.sort(
        key=lambda situation: (
            indices[
                str(
                    situation.page_id
                )
            ],
            _domain_priority(
                situation
            ),
            *_situation_position(
                book,
                situation,
            ),
            str(
                situation.subject_id
            ),
            str(
                situation.kind
            ),
            situation.id,
        )
    )

    unresolved.sort(
        key=lambda situation: (
            str(
                situation.domain
            ),
            str(
                situation.subject_id
            ),
            situation.id,
        )
    )

    return (
        tuple(
            located
        ),
        tuple(
            unresolved
        ),
    )


def prepare_roman_review(
    book: Any,
) -> RomanReviewPreparation:
    """Prepare une seule revue Roman, sans lancer ni posseder le Survol."""

    text = prepare_text_review(
        book
    )

    combined = (
        tuple(
            text.situations
        )
        + tuple(
            image_quality_situations(
                book
            )
        )
        + tuple(
            cover_situations(
                book
            )
        )
    )

    ordered, unresolved = _ordered_situations(
        book,
        combined,
    )

    return RomanReviewPreparation(
        text_rules=dict(
            text.rules
        ),
        text_rules_created=bool(
            text.rules_created
        ),
        automatic_text_corrections=tuple(
            dict(item)
            for item in text.automatic_corrections
        ),
        situations=ordered,
        unresolved_situations=unresolved,
    )


def open_roman_review_page(
    review: SurvolReviewState,
    preparation: RomanReviewPreparation,
    page_id: str,
) -> ReviewSnapshot:
    """Alimente la revue commune pour UNE page physique."""

    if not isinstance(
        review,
        SurvolReviewState,
    ):
        raise TypeError(
            "Un SurvolReviewState commun est requis."
        )

    if not isinstance(
        preparation,
        RomanReviewPreparation,
    ):
        raise TypeError(
            "Une preparation Roman V5 est requise."
        )

    return review.open_page(
        str(
            page_id
        ),
        preparation.situations_for_page(
            str(
                page_id
            )
        ),
    )


__all__ = [
    "RomanReviewPreparation",
    "prepare_roman_review",
    "open_roman_review_page",
]