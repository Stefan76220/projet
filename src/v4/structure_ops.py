from __future__ import annotations

from copy import deepcopy

"""
TomeLinea V4 — opérations structurelles manuelles.

Une page créée manuellement :
- appartient pleinement au Livre ;
- possède un UUID permanent ;
- n'est pas rattachée artificiellement à une Source ;
- n'est pas possédée par l'Analyse ;
- mémorise son emplacement logique ;
- ne peut être insérée à l'intérieur d'aucun bloc atomique
  (2P ou AV/source/AP).
"""

from dataclasses import fields
from datetime import datetime, timezone

from src.v4.domain import (
    BookV4,
    PageOrigin,
    PageV4,
)
from src.v4.structure_blocks import (
    structure_insertion_boundary_allowed,
)
from src.v4.structure_parts import (
    boundary_part_id,
)
from src.v4.structure_sync import (
    sync_structure_rules,
)


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _proposal_key(
    page: PageV4,
) -> str | None:

    value = page.metadata.get(
        "proposal_key"
    )

    return (
        str(value)
        if value is not None
        else None
    )


def _nearest_proposal_before(
    book: BookV4,
    index: int,
) -> str | None:

    for page_id in reversed(
        book.page_order[:index]
    ):
        key = _proposal_key(
            book.pages[
                page_id
            ]
        )

        if key is not None:
            return key

    return None


def _nearest_proposal_after(
    book: BookV4,
    index: int,
) -> str | None:

    for page_id in (
        book.page_order[index:]
    ):
        key = _proposal_key(
            book.pages[
                page_id
            ]
        )

        if key is not None:
            return key

    return None


def insert_manual_page(
    book: BookV4,
    *,
    index: int,
    page_type: str = "Page",
    title: str = "",
    is_compensation: bool = False,
    target_part_id: str | None = None,
) -> PageV4:
    """
    Ins?re une page manuelle dans une transaction Structure compl?te.

    Apr?s cr?ation, toutes les r?gles Structure sont imm?diatement
    remat?rialis?es. En cas d'?chec, le Livre entier est restaur?.
    """

    book.validate()

    if (
        index < 0
        or index > len(
            book.page_order
        )
    ):
        raise IndexError(
            "Position d'insertion invalide : "
            f"{index}"
        )

    if not (
        structure_insertion_boundary_allowed(
            book,
            index,
        )
    ):
        raise ValueError(
            "Impossible d'ins?rer une page "
            "? l'int?rieur d'un bloc structurel."
        )

    resolved_part_id = (
        boundary_part_id(
            book,
            index,
            requested_part_id=target_part_id,
        )
    )

    before_key = (
        _nearest_proposal_before(
            book,
            index,
        )
    )

    after_key = (
        _nearest_proposal_after(
            book,
            index,
        )
    )

    snapshot = deepcopy(
        book
    )

    try:
        page = PageV4(
            page_type=page_type,
            title=title,
            origin=PageOrigin.TOMELINEA,
            source=None,
            part_id=resolved_part_id,
            is_compensation=(
                is_compensation
            ),
        )

        page.metadata[
            "creation_kind"
        ] = "manual"

        page.metadata[
            "created_at"
        ] = utc_now()

        page.metadata[
            "manual_anchor"
        ] = {
            "before_proposal_key": (
                before_key
            ),
            "after_proposal_key": (
                after_key
            ),
        }

        book.add_page(
            page,
            index=index,
        )

        book.history.append(
            {
                "action": (
                    "page_manuelle_ajoutee"
                ),
                "page_id": page.id,
                "index": index,
                "part_id": resolved_part_id,
                "before_proposal_key": (
                    before_key
                ),
                "after_proposal_key": (
                    after_key
                ),
                "date": utc_now(),
            }
        )

        # L'insertion peut modifier imm?diatement :
        # - AV/AP ;
        # - r?gles de doubles pages ;
        # - Recto/Verso ;
        # - compensations.
        sync_structure_rules(
            book
        )

        book.validate()

        return book.pages[
            page.id
        ]

    except Exception:
        for field_info in fields(
            BookV4
        ):
            setattr(
                book,
                field_info.name,
                deepcopy(
                    getattr(
                        snapshot,
                        field_info.name,
                    )
                ),
            )

        raise

