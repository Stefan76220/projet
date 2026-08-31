from __future__ import annotations

"""
TomeLinea V4 — changement sûr du type d'une page.

Principes :
- l'UUID de la page ne change jamais ;
- une page automatique ne peut pas changer de type manuellement ;
- les règles locales restent attachées à l'identité de la page ;
- les règles de type du nouveau type deviennent immédiatement actives ;
- les 2P locales sont conservées ;
- les 2P étendues sont recalculées ;
- l'opération est atomique : en cas d'échec, le Livre revient
  exactement à son état précédent ;
- la baseline d'Analyse n'est jamais modifiée par une correction humaine.
"""

from copy import deepcopy
from dataclasses import dataclass, fields
from datetime import datetime, timezone

from src.v4.domain import BookV4
from src.v4.structure_auto import (
    is_structural_auto_page,
    structure_auto_issues,
)
from src.v4.structure_pair_rules import (
    structure_pair_rule_issues,
)
from src.v4.structure_spreads import (
    structure_spread_issues,
)
from src.v4.structure_sync import (
    StructureSyncResult,
    sync_structure_rules,
)


@dataclass(frozen=True, slots=True)
class StructureTypeChangeResult:
    changed: bool
    page_id: str
    old_type: str
    new_type: str
    sync_result: StructureSyncResult | None = None


def _utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _restore_book(
    book: BookV4,
    snapshot: BookV4,
) -> None:

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


def change_page_type(
    book: BookV4,
    page_id: str,
    new_type: str,
    *,
    change_origin: str = "human",
) -> StructureTypeChangeResult:

    book.validate()

    page = book.pages.get(
        page_id
    )

    if page is None:
        raise KeyError(
            page_id
        )

    if is_structural_auto_page(
        page
    ):
        raise ValueError(
            "Le type d'une page automatique Structure "
            "ne peut pas être modifié directement."
        )

    target = str(
        new_type or ""
    ).strip()

    if not target:
        raise ValueError(
            "Le type de page ne peut pas être vide."
        )

    origin = str(
        change_origin or ""
    ).strip().lower()

    if origin not in {
        "human",
        "automatic",
    }:
        raise ValueError(
            "Origine de modification inconnue : "
            f"{change_origin}"
        )

    old_type = str(
        page.page_type or ""
    ).strip()

    if old_type == target:
        return StructureTypeChangeResult(
            changed=False,
            page_id=page.id,
            old_type=old_type,
            new_type=target,
            sync_result=None,
        )

    snapshot = deepcopy(
        book
    )

    try:
        page.page_type = (
            target
        )

        sync_result = (
            sync_structure_rules(
                book
            )
        )

        book.validate()

        issues = (
            structure_spread_issues(
                book
            )
            + structure_auto_issues(
                book
            )
            + structure_pair_rule_issues(
                book
            )
        )

        if issues:
            raise ValueError(
                "Structure incohérente après "
                "changement de type : "
                + " ; ".join(
                    issues
                )
            )

        date = _utc_now()

        page = book.pages[
            page_id
        ]

        page.modifications.append(
            {
                "action": (
                    "page_type_changed"
                ),
                "origin": origin,
                "old_value": old_type,
                "new_value": target,
                "date": date,
            }
        )

        page.history.append(
            {
                "action": (
                    "type_page_modifie"
                ),
                "origin": origin,
                "old_type": old_type,
                "new_type": target,
                "date": date,
            }
        )

        book.history.append(
            {
                "action": (
                    "type_page_modifie"
                ),
                "page_id": page.id,
                "origin": origin,
                "old_type": old_type,
                "new_type": target,
                "date": date,
            }
        )

        return StructureTypeChangeResult(
            changed=True,
            page_id=page.id,
            old_type=old_type,
            new_type=target,
            sync_result=sync_result,
        )

    except Exception:
        _restore_book(
            book,
            snapshot,
        )
        raise
