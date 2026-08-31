from __future__ import annotations

"""
TomeLinea V4 — opérations manuelles sur les parties.

Une partie créée manuellement :
- appartient pleinement au Livre ;
- possède un UUID permanent ;
- n'est pas attribuée artificiellement à l'Analyse ;
- peut avoir un parent réel PartV4 ;
- mémorise sa position logique par rapport aux parties issues
  de l'Analyse.
"""

from datetime import datetime, timezone

from src.v4.domain import (
    BookV4,
    PartV4,
)


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _proposal_key(
    part: PartV4,
) -> str | None:

    value = part.metadata.get(
        "proposal_key"
    )

    if value is None:
        return None

    return str(value)


def _nearest_proposal_before(
    book: BookV4,
    index: int,
) -> str | None:

    for part_id in reversed(
        book.part_order[:index]
    ):
        key = _proposal_key(
            book.parts[part_id]
        )

        if key is not None:
            return key

    return None


def _nearest_proposal_after(
    book: BookV4,
    index: int,
) -> str | None:

    for part_id in book.part_order[index:]:
        key = _proposal_key(
            book.parts[part_id]
        )

        if key is not None:
            return key

    return None


def insert_manual_part(
    book: BookV4,
    *,
    index: int,
    title: str = "",
    part_type: str = "partie",
    parent_id: str | None = None,
) -> PartV4:
    """
    Insère une partie créée manuellement.

    L'ancre indique les deux parties issues de l'Analyse
    qui entouraient cette partie au moment de sa création.
    """

    book.validate()

    if (
        index < 0
        or index > len(book.part_order)
    ):
        raise IndexError(
            f"Position d'insertion invalide : {index}"
        )

    if (
        parent_id is not None
        and parent_id not in book.parts
    ):
        raise ValueError(
            f"Partie parente inconnue : {parent_id}"
        )

    before_key = _nearest_proposal_before(
        book,
        index,
    )

    after_key = _nearest_proposal_after(
        book,
        index,
    )

    part = PartV4(
        title=title,
        part_type=part_type,
        parent_id=parent_id,
    )

    part.metadata[
        "creation_kind"
    ] = "manual"

    part.metadata[
        "created_at"
    ] = utc_now()

    part.metadata[
        "manual_anchor"
    ] = {
        "before_proposal_key": before_key,
        "after_proposal_key": after_key,
    }

    book.add_part(
        part,
        index=index,
    )

    book.history.append(
        {
            "action": "partie_manuelle_ajoutee",
            "part_id": part.id,
            "index": index,
            "before_proposal_key": before_key,
            "after_proposal_key": after_key,
            "parent_id": parent_id,
            "date": utc_now(),
        }
    )

    book.validate()

    return part
