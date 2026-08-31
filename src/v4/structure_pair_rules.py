from __future__ import annotations

"""
TomeLinea V4 — règles étendues de doubles pages.

Principe :
    2P locale
        -> Étendre sur une paire ORDONNÉE de types
        -> application exacte, de gauche à droite, sans chevauchement
        -> Scinder global

Une vraie 2P reste constituée de deux PageV4 existantes.
Aucune page n'est recréée.
"""

from dataclasses import dataclass
from typing import Any

from src.v4.domain import BookV4, PageV4
from src.v4.structure_auto import is_structural_auto_page
from src.v4.structure_rules import (
    AFTER,
    BEFORE,
    STRUCTURE_RULES_KEY,
    effective_page_auto_rule,
)
from src.v4.structure_spreads import (
    pair_pages,
    split_spread,
    spread_members,
    structure_spread_issues,
)


PAIR_RULES_KEY = "double_page_pair_rules"

PAIR_RULE_MARKER = "double_page_pair_rule_key"
PAIR_CONFLICT_MARKER = "double_page_pair_conflict"


@dataclass(frozen=True, slots=True)
class PairRuleSyncResult:
    created_pairs: int
    reused_pairs: int
    removed_pairs: int
    conflicts: int


def _page_type(
    page: PageV4,
) -> str:

    return str(
        page.page_type or ""
    ).strip().lower()


def pair_rule_key(
    left_type: str,
    right_type: str,
) -> str:

    left = str(
        left_type or ""
    ).strip().lower()

    right = str(
        right_type or ""
    ).strip().lower()

    if not left or not right:
        return ""

    return f"{left}||{right}"


def _rules_root(
    book: BookV4,
    *,
    create: bool = False,
) -> dict[str, Any]:

    raw = book.metadata.get(
        STRUCTURE_RULES_KEY
    )

    if isinstance(raw, dict):
        return raw

    if raw is not None:
        raise ValueError(
            "structure_rules invalide."
        )

    if not create:
        return {}

    root: dict[str, Any] = {}

    book.metadata[
        STRUCTURE_RULES_KEY
    ] = root

    return root


def double_page_pair_rules(
    book: BookV4,
) -> dict[str, dict[str, str]]:

    root = _rules_root(book)

    raw = root.get(
        PAIR_RULES_KEY,
        {},
    )

    if not isinstance(raw, dict):
        return {}

    result: dict[
        str,
        dict[str, str],
    ] = {}

    for _stored_key, record in raw.items():
        if not isinstance(record, dict):
            continue

        left = str(
            record.get("left_type")
            or ""
        ).strip().lower()

        right = str(
            record.get("right_type")
            or ""
        ).strip().lower()

        key = pair_rule_key(
            left,
            right,
        )

        if not key:
            continue

        result[key] = {
            "left_type": left,
            "right_type": right,
        }

    return result


def _managed_key(
    page: PageV4,
) -> str:

    return str(
        page.metadata.get(
            PAIR_RULE_MARKER
        )
        or ""
    ).strip()


def _conflict_key(
    page: PageV4,
) -> str:

    return str(
        page.metadata.get(
            PAIR_CONFLICT_MARKER
        )
        or ""
    ).strip()


def _mark_managed(
    left: PageV4,
    right: PageV4,
    key: str,
) -> None:

    left.metadata[
        PAIR_RULE_MARKER
    ] = key

    right.metadata[
        PAIR_RULE_MARKER
    ] = key

    left.metadata.pop(
        PAIR_CONFLICT_MARKER,
        None,
    )

    right.metadata.pop(
        PAIR_CONFLICT_MARKER,
        None,
    )


def _clear_managed(
    left: PageV4,
    right: PageV4,
) -> None:

    for page in (
        left,
        right,
    ):
        page.metadata.pop(
            PAIR_RULE_MARKER,
            None,
        )

        page.metadata.pop(
            PAIR_CONFLICT_MARKER,
            None,
        )


def _mark_conflict(
    left: PageV4,
    right: PageV4,
    key: str,
) -> None:

    left.metadata[
        PAIR_CONFLICT_MARKER
    ] = key

    right.metadata[
        PAIR_CONFLICT_MARKER
    ] = key


def _spread_ids(
    book: BookV4,
) -> list[str]:

    result: list[str] = []

    for page_id in book.page_order:
        page = book.pages[
            page_id
        ]

        if (
            page.spread_id
            and page.spread_id
            not in result
        ):
            result.append(
                page.spread_id
            )

    return result


def _definition_issues(
    book: BookV4,
) -> list[str]:

    issues: list[str] = []

    root = book.metadata.get(
        STRUCTURE_RULES_KEY,
        {},
    )

    if not isinstance(root, dict):
        return [
            "structure_rules invalide"
        ]

    raw = root.get(
        PAIR_RULES_KEY,
        {},
    )

    if not isinstance(raw, dict):
        return [
            "double_page_pair_rules invalide"
        ]

    for stored_key, record in raw.items():
        if not isinstance(record, dict):
            issues.append(
                "règle 2P invalide : "
                f"{stored_key}"
            )
            continue

        left = str(
            record.get("left_type")
            or ""
        ).strip().lower()

        right = str(
            record.get("right_type")
            or ""
        ).strip().lower()

        canonical = pair_rule_key(
            left,
            right,
        )

        if not canonical:
            issues.append(
                "règle 2P avec type vide"
            )

        elif str(stored_key) != canonical:
            issues.append(
                "clé de règle 2P non canonique : "
                f"{stored_key}"
            )

    return issues


def structure_pair_rule_issues(
    book: BookV4,
) -> list[str]:

    issues = list(
        _definition_issues(
            book
        )
    )

    rules = double_page_pair_rules(
        book
    )

    for page in book.pages.values():

        managed = _managed_key(
            page
        )

        if managed:
            if managed not in rules:
                issues.append(
                    "page liée à une règle 2P "
                    f"inconnue : {page.id}"
                )

            if not page.spread_id:
                issues.append(
                    "page gérée par une règle 2P "
                    f"mais non soudée : {page.id}"
                )

        conflict = _conflict_key(
            page
        )

        if (
            conflict
            and conflict not in rules
        ):
            issues.append(
                "conflit lié à une règle 2P "
                f"inconnue : {page.id}"
            )

    for spread_id in _spread_ids(
        book
    ):
        members = spread_members(
            book,
            spread_id,
        )

        if members is None:
            continue

        left, right = members

        left_key = _managed_key(
            left
        )

        right_key = _managed_key(
            right
        )

        if left_key != right_key:
            issues.append(
                f"2P {spread_id} : règle gérée différente "
                "entre gauche et droite"
            )
            continue

        if left_key:
            expected = pair_rule_key(
                _page_type(left),
                _page_type(right),
            )

            if left_key != expected:
                issues.append(
                    f"2P {spread_id} : types incompatibles "
                    "avec sa règle étendue"
                )

    return issues


def sync_double_page_pair_rules(
    book: BookV4,
) -> PairRuleSyncResult:

    book.validate()

    definition_issues = (
        _definition_issues(
            book
        )
    )

    if definition_issues:
        raise ValueError(
            "Règles 2P invalides : "
            + " ; ".join(
                definition_issues
            )
        )

    spread_issues = (
        structure_spread_issues(
            book
        )
    )

    if spread_issues:
        raise ValueError(
            "Double page invalide : "
            + " ; ".join(
                spread_issues
            )
        )

    rules = double_page_pair_rules(
        book
    )

    created = 0
    reused = 0
    removed = 0
    conflicts = 0

    # ----------------------------------------------------------
    # 1 — Une paire précédemment gérée dont la règle n'existe
    # plus ou dont les types ont changé redevient simple.
    # ----------------------------------------------------------

    for spread_id in list(
        _spread_ids(
            book
        )
    ):
        members = spread_members(
            book,
            spread_id,
        )

        if members is None:
            continue

        left, right = members

        left_key = _managed_key(
            left
        )

        right_key = _managed_key(
            right
        )

        if (
            left_key
            and right_key
            and left_key != right_key
        ):
            raise ValueError(
                "Une 2P porte deux règles "
                "étendues différentes."
            )

        managed = (
            left_key
            or right_key
        )

        if not managed:
            continue

        expected = pair_rule_key(
            _page_type(left),
            _page_type(right),
        )

        if (
            managed not in rules
            or managed != expected
        ):
            _clear_managed(
                left,
                right,
            )

            split_spread(
                book,
                spread_id,
            )

            removed += 1

    # Les conflits sont recalculés à chaque passage.
    for page in book.pages.values():
        page.metadata.pop(
            PAIR_CONFLICT_MARKER,
            None,
        )

    # ----------------------------------------------------------
    # 2 — Application exacte et non chevauchante.
    # Les pages automatiques ne participent jamais aux règles.
    # ----------------------------------------------------------

    base_order = [
        page_id
        for page_id in book.page_order
        if not is_structural_auto_page(
            book.pages[
                page_id
            ]
        )
    ]

    pos = 0

    while pos + 1 < len(
        base_order
    ):
        left = book.pages[
            base_order[pos]
        ]

        right = book.pages[
            base_order[pos + 1]
        ]

        if left.part_id != right.part_id:
            pos += 1
            continue

        key = pair_rule_key(
            _page_type(left),
            _page_type(right),
        )

        if key not in rules:
            pos += 1
            continue

        # Paire déjà existante.
        if (
            left.spread_id
            and left.spread_id
            == right.spread_id
        ):
            members = spread_members(
                book,
                left.spread_id,
            )

            if members is not None:
                _mark_managed(
                    left,
                    right,
                    key,
                )

                reused += 1
                pos += 2
                continue

        # Une autre 2P locale occupe déjà l'une des pages.
        if (
            left.spread_id
            or right.spread_id
        ):
            pos += 1
            continue

        # AV/AP entre les deux pages : la vraie 2P ne peut
        # physiquement pas être créée.
        internal_auto_rule = bool(
            effective_page_auto_rule(
                book,
                left.id,
                AFTER,
            )
            or effective_page_auto_rule(
                book,
                right.id,
                BEFORE,
            )
        )

        internal_auto_page = bool(
            left.auto_after
            or right.auto_before
        )

        left_index = book.page_order.index(
            left.id
        )

        right_index = book.page_order.index(
            right.id
        )

        physically_adjacent = (
            right_index
            == left_index + 1
        )

        if (
            internal_auto_rule
            or internal_auto_page
            or not physically_adjacent
        ):
            _mark_conflict(
                left,
                right,
                key,
            )

            conflicts += 1
            pos += 2
            continue

        pair_pages(
            book,
            left.id,
            right.id,
        )

        _mark_managed(
            left,
            right,
            key,
        )

        created += 1
        pos += 2

    book.validate()

    final_issues = (
        structure_spread_issues(
            book
        )
        + structure_pair_rule_issues(
            book
        )
    )

    if final_issues:
        raise ValueError(
            "Structure 2P incohérente : "
            + " ; ".join(
                final_issues
            )
        )

    book.history.append(
        {
            "action": "regles_2p_synchronisees",
            "created_pairs": created,
            "reused_pairs": reused,
            "removed_pairs": removed,
            "conflicts": conflicts,
        }
    )

    return PairRuleSyncResult(
        created_pairs=created,
        reused_pairs=reused,
        removed_pairs=removed,
        conflicts=conflicts,
    )


def extend_spread_rule(
    book: BookV4,
    spread_id: str,
) -> PairRuleSyncResult:
    """
    Étend une 2P locale à toutes les suites exactes
    gauche_type + droite_type.
    """

    book.validate()

    members = spread_members(
        book,
        spread_id,
    )

    if members is None:
        raise ValueError(
            "La double page à étendre "
            "est invalide ou inconnue."
        )

    left, right = members

    left_type = _page_type(
        left
    )

    right_type = _page_type(
        right
    )

    key = pair_rule_key(
        left_type,
        right_type,
    )

    if not key:
        raise ValueError(
            "Les deux pages doivent avoir "
            "un type pour étendre la règle 2P."
        )

    root = _rules_root(
        book,
        create=True,
    )

    raw = root.get(
        PAIR_RULES_KEY
    )

    if raw is None:
        raw = {}
        root[
            PAIR_RULES_KEY
        ] = raw

    if not isinstance(raw, dict):
        raise ValueError(
            "double_page_pair_rules invalide."
        )

    raw[key] = {
        "left_type": left_type,
        "right_type": right_type,
    }

    # La 2P d'origine appartient désormais
    # à la règle étendue.
    _mark_managed(
        left,
        right,
        key,
    )

    book.history.append(
        {
            "action": "regle_2p_etendue",
            "rule_key": key,
            "left_type": left_type,
            "right_type": right_type,
            "source_spread_id": spread_id,
        }
    )

    return sync_double_page_pair_rules(
        book
    )


def scind_extended_spread_rule(
    book: BookV4,
    spread_id: str,
) -> int:
    """
    Scinder 2P est global :
    la règle disparaît et toutes les paires qu'elle gérait
    sont dissociées.

    Les autres 2P locales restent intactes.
    """

    book.validate()

    members = spread_members(
        book,
        spread_id,
    )

    if members is None:
        raise ValueError(
            "La double page est invalide "
            "ou inconnue."
        )

    left, right = members

    key = (
        _managed_key(left)
        or _managed_key(right)
    )

    rules = double_page_pair_rules(
        book
    )

    if (
        not key
        or key not in rules
    ):
        raise ValueError(
            "Cette double page n'appartient "
            "pas à une règle 2P étendue."
        )

    root = _rules_root(
        book,
        create=True,
    )

    raw = root.get(
        PAIR_RULES_KEY
    )

    if not isinstance(raw, dict):
        raise ValueError(
            "double_page_pair_rules invalide."
        )

    raw.pop(
        key,
        None,
    )

    removed = 0

    for current_spread_id in list(
        _spread_ids(
            book
        )
    ):
        current = spread_members(
            book,
            current_spread_id,
        )

        if current is None:
            continue

        current_left, current_right = (
            current
        )

        managed = (
            _managed_key(
                current_left
            )
            or _managed_key(
                current_right
            )
        )

        if managed != key:
            continue

        _clear_managed(
            current_left,
            current_right,
        )

        split_spread(
            book,
            current_spread_id,
        )

        removed += 1

    # Nettoie les conflits de la règle supprimée.
    for page in book.pages.values():
        if _conflict_key(page) == key:
            page.metadata.pop(
                PAIR_CONFLICT_MARKER,
                None,
            )

    book.history.append(
        {
            "action": "regle_2p_scindee",
            "rule_key": key,
            "removed_pairs": removed,
        }
    )

    book.validate()

    issues = (
        structure_spread_issues(
            book
        )
        + structure_pair_rule_issues(
            book
        )
    )

    if issues:
        raise ValueError(
            "Structure incohérente après "
            "Scinder 2P : "
            + " ; ".join(
                issues
            )
        )

    return removed
