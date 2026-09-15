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
AUTO_SPREAD_INTENTS_KEY = "automatic_spread_intents"


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

    if (
        bool(left.metadata.get("automatic_structure", False))
        or bool(right.metadata.get("automatic_structure", False))
    ):
        raw = book.metadata.get(AUTO_SPREAD_INTENTS_KEY)
        if not isinstance(raw, dict):
            raw = {}
            book.metadata[AUTO_SPREAD_INTENTS_KEY] = raw
        raw[spread_id] = {
            "spread_id": spread_id,
            "left_page_id": left.id,
            "right_page_id": right.id,
        }

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

    raw_intents = book.metadata.get(AUTO_SPREAD_INTENTS_KEY)
    if isinstance(raw_intents, dict):
        raw_intents.pop(spread_id, None)
        if not raw_intents:
            book.metadata.pop(AUTO_SPREAD_INTENTS_KEY, None)

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



@dataclass(slots=True)
class SuspendedAutoSpread:
    spread_id: str
    left_page: PageV4
    right_page: PageV4
    left_index: int
    right_index: int


def suspend_auto_spreads(book: BookV4) -> list[SuspendedAutoSpread]:
    """Détache temporairement les 2P contenant une page auto avant la reconstruction AV/AP."""
    result: list[SuspendedAutoSpread] = []
    for spread_id in list({p.spread_id for p in book.pages.values() if p.spread_id}):
        members = spread_members(book, spread_id)
        if members is None:
            continue
        left, right = members
        if not (
            bool(left.metadata.get("automatic_structure", False))
            or bool(right.metadata.get("automatic_structure", False))
        ):
            continue
        result.append(SuspendedAutoSpread(
            spread_id=spread_id,
            left_page=left,
            right_page=right,
            left_index=_page_index(book, left.id),
            right_index=_page_index(book, right.id),
        ))
        raw = book.metadata.get(AUTO_SPREAD_INTENTS_KEY)
        if not isinstance(raw, dict):
            raw = {}
            book.metadata[AUTO_SPREAD_INTENTS_KEY] = raw
        raw[spread_id] = {
            "spread_id": spread_id,
            "left_page_id": left.id,
            "right_page_id": right.id,
        }
        left.spread_id = left.spread_side = None
        right.spread_id = right.spread_side = None
    return result


def _retain_missing_auto(page: PageV4) -> None:
    roles = page.metadata.get("automatic_roles")
    if isinstance(roles, list) and roles:
        page.metadata["automatic_origin_roles"] = [dict(r) for r in roles if isinstance(r, dict)]
    page.metadata["automatic_origin"] = True
    page.metadata["automatic_retained"] = True
    page.metadata["automatic_user_protected"] = True
    page.metadata["automatic_structure"] = False
    page.metadata["automatic_kind"] = "retained_editorial"
    page.metadata.pop("automatic_roles", None)
    page.metadata.pop("automatic_markers", None)
    page.metadata.pop("automatic_shared", None)
    page.metadata.pop("source_page_id", None)
    page.auto_before = []
    page.auto_after = []
    page.is_compensation = False


def restore_auto_spreads(book: BookV4, suspended: list[SuspendedAutoSpread]) -> None:
    """Restaure les 2P auto après recalcul; la 2P elle-même protège une auto devenue inutile."""
    for snap in suspended:
        left = book.pages.get(snap.left_page.id)
        right = book.pages.get(snap.right_page.id)

        if left is None:
            left = snap.left_page
            _retain_missing_auto(left)
            book.pages[left.id] = left
        if right is None:
            right = snap.right_page
            _retain_missing_auto(right)
            book.pages[right.id] = right

        # Une 2P explicite est une décision éditoriale : une page auto membre est protégée.
        for page in (left, right):
            if bool(page.metadata.get("automatic_structure", False)):
                page.metadata["automatic_user_protected"] = True
                page.metadata["automatic_origin"] = True

        # Replace les deux membres côte à côte sans déplacer inutilement les
        # frontières AV/AP recalculées. Si _sync_av_ap() les a déjà replacés
        # correctement, leur position courante est l'autorité : revenir à
        # l'ancien index ferait passer un AP situé après la page à l'avant de
        # la double page.
        left_present = left.id in book.page_order
        right_present = right.id in book.page_order
        already_adjacent = False
        if left_present and right_present:
            left_index = book.page_order.index(left.id)
            right_index = book.page_order.index(right.id)
            already_adjacent = right_index == left_index + 1

        if not already_adjacent:
            # Une 2P composée de deux pages automatiques doit conserver la
            # frontière éditoriale où l'utilisateur l'a créée. Les déplacer
            # l'une vers l'autre en suivant seulement l'une des deux autos peut
            # casser l'AP de gauche ou l'AV de droite.
            both_auto = bool(left.metadata.get("automatic_structure", False)) and bool(
                right.metadata.get("automatic_structure", False)
            )
            if both_auto:
                for pid in (left.id, right.id):
                    if pid in book.page_order:
                        book.page_order.remove(pid)
                anchor = min(snap.left_index, len(book.page_order))
                book.page_order[anchor:anchor] = [left.id, right.id]
            # Une moitié automatique suit la moitié éditoriale qui lui donne
            # sa place. Sinon on conserve au mieux la position courante.
            elif right_present and bool(left.metadata.get("automatic_structure", False)):
                if left_present:
                    book.page_order.remove(left.id)
                anchor = book.page_order.index(right.id)
                book.page_order.insert(anchor, left.id)
            elif left_present and bool(right.metadata.get("automatic_structure", False)):
                if right_present:
                    book.page_order.remove(right.id)
                anchor = book.page_order.index(left.id) + 1
                book.page_order.insert(anchor, right.id)
            else:
                current_positions = [
                    book.page_order.index(pid)
                    for pid in (left.id, right.id)
                    if pid in book.page_order
                ]
                anchor = (
                    min(current_positions)
                    if current_positions
                    else min(snap.left_index, len(book.page_order))
                )
                for pid in (left.id, right.id):
                    if pid in book.page_order:
                        book.page_order.remove(pid)
                anchor = min(anchor, len(book.page_order))
                book.page_order[anchor:anchor] = [left.id, right.id]

        left.part_id = right.part_id if left.part_id is None else left.part_id
        right.part_id = left.part_id if right.part_id is None else right.part_id
        if left.part_id != right.part_id:
            # La décision 2P prime sur l'origine technique : la page auto suit la page éditoriale.
            if bool(left.metadata.get("automatic_structure", False)) or left.metadata.get("automatic_retained"):
                left.part_id = right.part_id
            elif bool(right.metadata.get("automatic_structure", False)) or right.metadata.get("automatic_retained"):
                right.part_id = left.part_id
            else:
                raise ValueError("Les deux pages de la double page appartiennent à des parties différentes.")

        left.spread_id = right.spread_id = snap.spread_id
        left.spread_side = SPREAD_LEFT
        right.spread_side = SPREAD_RIGHT

        if bool(left.metadata.get("automatic_structure", False)):
            if left.id not in right.auto_before:
                right.auto_before.append(left.id)
        if bool(right.metadata.get("automatic_structure", False)):
            if right.id not in left.auto_after:
                left.auto_after.append(right.id)

        raw = book.metadata.get(AUTO_SPREAD_INTENTS_KEY)
        if not isinstance(raw, dict):
            raw = {}
            book.metadata[AUTO_SPREAD_INTENTS_KEY] = raw
        raw[snap.spread_id] = {
            "spread_id": snap.spread_id,
            "left_page_id": left.id,
            "right_page_id": right.id,
        }
    book.validate()


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
