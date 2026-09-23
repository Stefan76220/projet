"""Persistance de la revue Survol dans l'unique Livre TomeLinea."""

from __future__ import annotations

from typing import Any, Mapping

from .review import (
    REVIEW_SCHEMA,
    SurvolReviewState,
)


REVIEW_METADATA_KEY = "survol_review_state"


def _metadata(book: Any) -> dict[str, Any]:
    metadata = getattr(
        book,
        "metadata",
        None,
    )

    if not isinstance(metadata, dict):
        raise ValueError(
            "Le Livre ne possede pas de metadonnees modifiables."
        )

    return metadata


def save_review_state(
    book: Any,
    review: SurvolReviewState,
) -> dict[str, object]:
    """Ecrit uniquement l'etat durable dans Book.metadata."""

    if not isinstance(
        review,
        SurvolReviewState,
    ):
        raise TypeError(
            "Un SurvolReviewState est requis."
        )

    payload = review.export_state()

    _metadata(
        book
    )[REVIEW_METADATA_KEY] = payload

    return payload


def load_review_state(
    book: Any,
) -> SurvolReviewState:
    """Recharge la revue sans restaurer de curseur de page transitoire."""

    raw = _metadata(
        book
    ).get(
        REVIEW_METADATA_KEY
    )

    payload = (
        raw
        if isinstance(raw, Mapping)
        else None
    )

    return SurvolReviewState.from_state(
        payload
    )


def clear_review_state(
    book: Any,
) -> None:
    _metadata(
        book
    ).pop(
        REVIEW_METADATA_KEY,
        None,
    )


__all__ = [
    "REVIEW_SCHEMA",
    "REVIEW_METADATA_KEY",
    "save_review_state",
    "load_review_state",
    "clear_review_state",
]