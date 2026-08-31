from __future__ import annotations

"""
TomeLinea V4 — blocs atomiques de Structure.

Un bloc peut être :
    page simple

ou :
    AV + page + AP

ou :
    AV + gauche 2P + droite 2P + AP

Aucune opération de Structure ne doit pouvoir déposer un élément
à l'intérieur d'un tel bloc.
"""

from dataclasses import dataclass

from src.v4.domain import (
    BookV4,
    PageV4,
)
from src.v4.structure_auto import (
    is_structural_auto_page,
    structural_auto_source_ids,
    structure_auto_issues,
)
from src.v4.structure_spreads import (
    spread_members,
    structure_spread_issues,
)
from src.v4.structure_parts import (
    boundary_part_id,
)


@dataclass(frozen=True, slots=True)
class AtomicPageBlock:
    page_ids: tuple[str, ...]

    @property
    def size(self) -> int:
        return len(
            self.page_ids
        )


def _source_for_auto(
    book: BookV4,
    page: PageV4,
) -> PageV4:

    source_ids = (
        structural_auto_source_ids(
            page
        )
    )

    if len(source_ids) != 1:
        raise ValueError(
            "Cette page automatique n'a pas "
            "exactement une source structurelle."
        )

    source = book.pages.get(
        source_ids[0]
    )

    if source is None:
        raise ValueError(
            "Source de page automatique inconnue : "
            f"{source_ids[0]}"
        )

    return source


def _base_pages(
    book: BookV4,
    source: PageV4,
) -> tuple[PageV4, ...]:

    if not source.spread_id:
        return (
            source,
        )

    members = spread_members(
        book,
        source.spread_id,
    )

    if members is None:
        raise ValueError(
            "Double page invalide."
        )

    left, right = members

    return (
        left,
        right,
    )


def atomic_block_for_page(
    book: BookV4,
    page_id: str,
) -> AtomicPageBlock:

    book.validate()

    page = book.pages.get(
        page_id
    )

    if page is None:
        raise KeyError(
            page_id
        )

    source = (
        _source_for_auto(
            book,
            page,
        )
        if is_structural_auto_page(
            page
        )
        else page
    )

    base = _base_pages(
        book,
        source,
    )

    left = base[0]
    right = base[-1]

    # Sur une 2P les associations internes sont interdites.
    if len(base) == 2:
        if (
            left.auto_after
            or right.auto_before
        ):
            raise ValueError(
                "Une page AV/AP est placée "
                "à l'intérieur d'une double page."
            )

    ids = (
        tuple(
            left.auto_before
        )
        + tuple(
            current.id
            for current in base
        )
        + tuple(
            right.auto_after
        )
    )

    if len(ids) != len(
        set(ids)
    ):
        raise ValueError(
            "Un bloc structurel contient "
            "plusieurs fois la même page."
        )

    for current_id in ids:
        if current_id not in book.pages:
            raise ValueError(
                "Page inconnue dans le bloc : "
                f"{current_id}"
            )

    positions = [
        book.page_order.index(
            current_id
        )
        for current_id in ids
    ]

    start = min(
        positions
    )

    expected = book.page_order[
        start:
        start + len(ids)
    ]

    if expected != list(
        ids
    ):
        raise ValueError(
            "Le bloc structurel n'est plus contigu."
        )

    return AtomicPageBlock(
        page_ids=ids
    )


def atomic_blocks(
    book: BookV4,
) -> tuple[AtomicPageBlock, ...]:

    book.validate()

    result: list[
        AtomicPageBlock
    ] = []

    consumed: set[str] = set()

    for page_id in book.page_order:
        if page_id in consumed:
            continue

        block = atomic_block_for_page(
            book,
            page_id,
        )

        result.append(
            block
        )

        consumed.update(
            block.page_ids
        )

    if consumed != set(
        book.page_order
    ):
        raise ValueError(
            "Certaines pages ne sont dans "
            "aucun bloc structurel."
        )

    return tuple(
        result
    )


def protected_structure_boundaries(
    book: BookV4,
) -> set[int]:
    """
    Frontières d'index interdites.

    Une frontière située entre deux éléments d'un bloc
    atomique ne peut recevoir aucune insertion.
    """

    protected: set[int] = set()

    for block in atomic_blocks(
        book
    ):
        positions = [
            book.page_order.index(
                page_id
            )
            for page_id in block.page_ids
        ]

        start = min(
            positions
        )

        for offset in range(
            1,
            len(
                block.page_ids
            ),
        ):
            protected.add(
                start + offset
            )

    return protected


def structure_insertion_boundary_allowed(
    book: BookV4,
    index: int,
) -> bool:

    book.validate()

    if (
        index < 0
        or index > len(
            book.page_order
        )
    ):
        raise IndexError(
            f"Position d'insertion invalide : {index}"
        )

    return (
        index
        not in protected_structure_boundaries(
            book
        )
    )


def move_atomic_block(
    book: BookV4,
    page_id: str,
    target_index: int,
    *,
    target_part_id: str | None = None,
) -> bool:
    """
    Déplace le bloc contenant page_id.

    Les AV/AP et les deux moitiés d'une 2P suivent ensemble.
    """

    book.validate()

    if (
        target_index < 0
        or target_index > len(
            book.page_order
        )
    ):
        raise IndexError(
            "Position de déplacement invalide : "
            f"{target_index}"
        )

    block = atomic_block_for_page(
        book,
        page_id,
    )

    positions = [
        book.page_order.index(
            current_id
        )
        for current_id in block.page_ids
    ]

    start = min(
        positions
    )

    end_exclusive = (
        max(
            positions
        )
        + 1
    )

    if (
        start
        <= target_index
        <= end_exclusive
    ):
        return False

    if not (
        structure_insertion_boundary_allowed(
            book,
            target_index,
        )
    ):
        raise ValueError(
            "Impossible de déposer un bloc "
            "à l'intérieur d'un autre bloc atomique."
        )

    old_order = list(
        book.page_order
    )

    block_ids = list(
        block.page_ids
    )

    remaining = [
        current_id
        for current_id in old_order
        if current_id not in block_ids
    ]

    removed_before_target = sum(
        1
        for position in positions
        if position < target_index
    )

    adjusted_target = (
        target_index
        - removed_before_target
    )

    resolved_part_id = (
        boundary_part_id(
            book,
            adjusted_target,
            page_order=remaining,
            requested_part_id=target_part_id,
        )
    )

    new_order = list(
        remaining
    )

    new_order[
        adjusted_target:
        adjusted_target
    ] = block_ids

    if new_order == old_order:
        return False

    old_part_ids = {
        current_id: (
            book.pages[
                current_id
            ].part_id
        )
        for current_id in block_ids
    }

    book.page_order = (
        new_order
    )

    for current_id in block_ids:
        book.pages[
            current_id
        ].part_id = (
            resolved_part_id
        )

    try:
        book.validate()

        issues = (
            structure_spread_issues(
                book
            )
            + structure_auto_issues(
                book
            )
        )

        if issues:
            raise ValueError(
                "Le déplacement casserait "
                "la Structure : "
                + " ; ".join(
                    issues
                )
            )

    except Exception:
        book.page_order = (
            old_order
        )

        for current_id, old_part_id in (
            old_part_ids.items()
        ):
            book.pages[
                current_id
            ].part_id = (
                old_part_id
            )

        raise

    book.history.append(
        {
            "action": (
                "bloc_structure_deplace"
            ),
            "page_ids": list(
                block.page_ids
            ),
            "from_index": start,
            "target_index": (
                target_index
            ),
            "final_index": (
                adjusted_target
            ),
            "target_part_id": (
                resolved_part_id
            ),
            "previous_part_ids": (
                old_part_ids
            ),
        }
    )

    return True
