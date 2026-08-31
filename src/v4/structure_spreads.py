from __future__ import annotations

"""
TomeLinea V4 — doubles pages structurelles (2P).

Une double page réelle est un bloc atomique de deux PageV4 :
    gauche = verso
    droite = recto

Principes repris du moteur Structure V3 validé :
- exactement deux pages ;
- pages voisines ;
- même partie ;
- aucune insertion autorisée entre elles ;
- une page ne peut appartenir qu'à une seule 2P ;
- l'identité des pages ne change pas ;
- la 2P possède sa propre identité stable ;
- les règles R/V propres aux pages pourront rester mémorisées,
  mais seront suspendues tant que la paire existe.
"""

from dataclasses import dataclass
from uuid import uuid4

from src.v4.domain import (
    BookV4,
    PageV4,
)


SPREAD_LEFT = "left"
SPREAD_RIGHT = "right"


def new_spread_id() -> str:
    return str(uuid4())


@dataclass(frozen=True, slots=True)
class SpreadPair:
    spread_id: str

    left_page_id: str
    right_page_id: str


def _page_index(
    book: BookV4,
    page_id: str,
) -> int:

    try:
        return book.page_order.index(
            page_id
        )
    except ValueError as exc:
        raise ValueError(
            f"Page absente de l'ordre : {page_id}"
        ) from exc


def spread_members(
    book: BookV4,
    spread_id: str,
) -> tuple[PageV4, PageV4] | None:
    """
    Retourne gauche/droite seulement si la 2P est réellement valide.
    """

    members = [
        page
        for page in book.pages.values()
        if page.spread_id == spread_id
    ]

    if len(members) != 2:
        return None

    left = next(
        (
            page
            for page in members
            if page.spread_side == SPREAD_LEFT
        ),
        None,
    )

    right = next(
        (
            page
            for page in members
            if page.spread_side == SPREAD_RIGHT
        ),
        None,
    )

    if left is None or right is None:
        return None

    left_index = _page_index(
        book,
        left.id,
    )

    right_index = _page_index(
        book,
        right.id,
    )

    if right_index != left_index + 1:
        return None

    if left.part_id != right.part_id:
        return None

    return left, right


def page_spread(
    book: BookV4,
    page_id: str,
) -> SpreadPair | None:

    page = book.pages.get(
        page_id
    )

    if page is None:
        raise KeyError(
            page_id
        )

    if not page.spread_id:
        return None

    members = spread_members(
        book,
        page.spread_id,
    )

    if members is None:
        return None

    left, right = members

    return SpreadPair(
        spread_id=page.spread_id,
        left_page_id=left.id,
        right_page_id=right.id,
    )


def pair_pages(
    book: BookV4,
    left_page_id: str,
    right_page_id: str,
) -> SpreadPair:
    """
    Soude deux pages existantes en une vraie double page.
    """

    book.validate()

    if left_page_id == right_page_id:
        raise ValueError(
            "Une double page nécessite deux pages distinctes."
        )

    left = book.pages.get(
        left_page_id
    )

    right = book.pages.get(
        right_page_id
    )

    if left is None:
        raise KeyError(
            left_page_id
        )

    if right is None:
        raise KeyError(
            right_page_id
        )

    if (
        bool(
            left.metadata.get(
                "automatic_structure",
                False,
            )
        )
        or bool(
            right.metadata.get(
                "automatic_structure",
                False,
            )
        )
    ):
        raise ValueError(
            "Une page automatique ne peut pas "
            "faire partie d'une double page."
        )

    if left.auto_after or right.auto_before:
        raise ValueError(
            "Une page AV/AP est requise entre ces deux pages. "
            "La double page ne peut pas ?tre cr??e."
        )

    left_index = _page_index(
        book,
        left.id,
    )

    right_index = _page_index(
        book,
        right.id,
    )

    if right_index != left_index + 1:
        raise ValueError(
            "Les deux pages doivent être voisines "
            "et fournies dans l'ordre gauche puis droite."
        )

    if left.part_id != right.part_id:
        raise ValueError(
            "Les deux pages doivent appartenir "
            "à la même partie."
        )

    if left.spread_id or right.spread_id:
        raise ValueError(
            "Une des pages appartient déjà "
            "à une double page."
        )

    spread_id = new_spread_id()

    left.spread_id = spread_id
    left.spread_side = SPREAD_LEFT

    right.spread_id = spread_id
    right.spread_side = SPREAD_RIGHT

    left.history.append(
        {
            "action": "double_page_associee",
            "spread_id": spread_id,
            "side": SPREAD_LEFT,
            "peer_page_id": right.id,
        }
    )

    right.history.append(
        {
            "action": "double_page_associee",
            "spread_id": spread_id,
            "side": SPREAD_RIGHT,
            "peer_page_id": left.id,
        }
    )

    book.history.append(
        {
            "action": "double_page_creee",
            "spread_id": spread_id,
            "left_page_id": left.id,
            "right_page_id": right.id,
        }
    )

    book.validate()

    return SpreadPair(
        spread_id=spread_id,
        left_page_id=left.id,
        right_page_id=right.id,
    )


def split_spread(
    book: BookV4,
    spread_id: str,
) -> SpreadPair:
    """
    Dissocie une 2P sans supprimer ni recréer ses pages.
    """

    book.validate()

    members = spread_members(
        book,
        spread_id,
    )

    if members is None:
        raise ValueError(
            f"Double page invalide ou inconnue : {spread_id}"
        )

    left, right = members

    result = SpreadPair(
        spread_id=spread_id,
        left_page_id=left.id,
        right_page_id=right.id,
    )

    left.spread_id = None
    left.spread_side = None

    right.spread_id = None
    right.spread_side = None

    left.history.append(
        {
            "action": "double_page_scindee",
            "spread_id": spread_id,
        }
    )

    right.history.append(
        {
            "action": "double_page_scindee",
            "spread_id": spread_id,
        }
    )

    book.history.append(
        {
            "action": "double_page_scindee",
            "spread_id": spread_id,
            "left_page_id": left.id,
            "right_page_id": right.id,
        }
    )

    book.validate()

    return result


def insertion_boundary_allowed(
    book: BookV4,
    index: int,
) -> bool:
    """
    Indique si une page peut être insérée à cet index.

    index représente une frontière de page_order :
        0 = avant la première page
        len(page_order) = après la dernière.

    La seule frontière interdite est l'intérieur d'une 2P.
    """

    book.validate()

    if (
        index < 0
        or index > len(book.page_order)
    ):
        raise IndexError(
            f"Position d'insertion invalide : {index}"
        )

    if (
        index == 0
        or index == len(book.page_order)
    ):
        return True

    before = book.pages[
        book.page_order[index - 1]
    ]

    after = book.pages[
        book.page_order[index]
    ]

    return not (
        before.spread_id
        and before.spread_id == after.spread_id
        and before.spread_side == SPREAD_LEFT
        and after.spread_side == SPREAD_RIGHT
    )


def structure_spread_issues(
    book: BookV4,
) -> list[str]:
    """
    Contrôle indépendant de l'interface.
    """

    issues: list[str] = []

    spread_ids = {
        page.spread_id
        for page in book.pages.values()
        if page.spread_id
    }

    for spread_id in spread_ids:
        members = [
            page
            for page in book.pages.values()
            if page.spread_id == spread_id
        ]

        if len(members) != 2:
            issues.append(
                f"2P {spread_id} : nombre de pages incorrect"
            )
            continue

        left = next(
            (
                page
                for page in members
                if page.spread_side == SPREAD_LEFT
            ),
            None,
        )

        right = next(
            (
                page
                for page in members
                if page.spread_side == SPREAD_RIGHT
            ),
            None,
        )

        if left is None or right is None:
            issues.append(
                f"2P {spread_id} : côtés gauche/droite invalides"
            )
            continue

        if (
            bool(
                left.metadata.get(
                    "automatic_structure",
                    False,
                )
            )
            or bool(
                right.metadata.get(
                    "automatic_structure",
                    False,
                )
            )
        ):
            issues.append(
                f"2P {spread_id} : page automatique membre"
            )

        if left.auto_after or right.auto_before:
            issues.append(
                f"2P {spread_id} : AV/AP interne"
            )

        if left.part_id != right.part_id:
            issues.append(
                f"2P {spread_id} : parties différentes"
            )

        try:
            left_index = _page_index(
                book,
                left.id,
            )
            right_index = _page_index(
                book,
                right.id,
            )

            if right_index != left_index + 1:
                issues.append(
                    f"2P {spread_id} : pages non contiguës"
                )

        except ValueError:
            issues.append(
                f"2P {spread_id} : page absente de l'ordre"
            )

    return issues
