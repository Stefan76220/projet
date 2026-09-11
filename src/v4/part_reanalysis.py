from __future__ import annotations

"""
TomeLinea V4 — réanalyse contrôlée des parties.

Principes :
- PartV4.id reste l'identité permanente ;
- l'Analyse travaille avec proposal_key ;
- une modification humaine n'est jamais écrasée ;
- les nouvelles parties sont détectées avant création ;
- les parties disparues ne sont jamais supprimées automatiquement ;
- une partie manuelle correctement ancrée ne bloque pas, à elle seule,
  l'évolution automatique de l'ordre ;
- le déplacement manuel d'une partie est détecté et protège l'ordre ;
- les changements de parent sont contrôlés contre les cycles.
"""

from dataclasses import dataclass, field
from typing import Any

from src.v4.domain import (
    BookV4,
    PartV4,
)
from src.v4.proposal import (
    BookProposal,
    ProposedPart,
    book_part_order_keys,
    proposal_part_order_keys,
    proposed_part_baseline,
)


@dataclass(frozen=True, slots=True)
class PartReanalysisChange:
    part_id: str
    proposal_key: str
    field_name: str

    baseline_value: Any
    current_value: Any
    proposed_value: Any

    protected_by_human_change: bool


@dataclass(slots=True)
class PartReanalysisPlan:
    proposal_id: str

    automatic_changes: list[
        PartReanalysisChange
    ] = field(default_factory=list)

    protected_changes: list[
        PartReanalysisChange
    ] = field(default_factory=list)

    deferred_changes: list[
        PartReanalysisChange
    ] = field(default_factory=list)

    new_parts: list[
        ProposedPart
    ] = field(default_factory=list)

    missing_part_ids: list[str] = field(
        default_factory=list
    )

    manual_part_ids: list[str] = field(
        default_factory=list
    )

    manual_anchor_issues: list[str] = field(
        default_factory=list
    )

    order_baseline: list[str] = field(
        default_factory=list
    )

    order_current: list[str] = field(
        default_factory=list
    )

    order_proposed: list[str] = field(
        default_factory=list
    )

    # Ordre réel complet, parties manuelles comprises.
    full_order_current: list[str] = field(
        default_factory=list
    )

    order_change_detected: bool = False
    order_protected: bool = False


def _proposal_key(
    part: PartV4,
) -> str | None:

    value = part.metadata.get(
        "proposal_key"
    )

    if value is None:
        return None

    return str(value)


def _parts_by_proposal_key(
    book: BookV4,
) -> dict[str, PartV4]:

    result: dict[str, PartV4] = {}

    for part in book.parts.values():
        key = _proposal_key(
            part
        )

        if key is None:
            continue

        if key in result:
            raise ValueError(
                "Plusieurs parties utilisent la même "
                f"clé d'analyse : {key}"
            )

        result[key] = part

    return result


def _part_ids_by_proposal_key(
    book: BookV4,
) -> dict[str, str]:

    return {
        key: part.id
        for key, part
        in _parts_by_proposal_key(
            book
        ).items()
    }


def _current_parent_key(
    book: BookV4,
    part: PartV4,
) -> str | None:

    if part.parent_id is None:
        return None

    parent = book.parts.get(
        part.parent_id
    )

    if parent is None:
        raise ValueError(
            f"Parent introuvable : {part.parent_id}"
        )

    parent_key = _proposal_key(
        parent
    )

    if parent_key is not None:
        return parent_key

    return f"@manuel:{parent.id}"


def current_part_values(
    book: BookV4,
    part: PartV4,
) -> dict[str, Any]:

    return {
        "title": part.title,
        "part_type": part.part_type,
        "parent_key": _current_parent_key(
            book,
            part,
        ),
    }


# ==============================================================
# Ancres des parties manuelles
# ==============================================================

def _current_manual_anchor(
    book: BookV4,
    part_id: str,
) -> dict[str, str | None]:

    if part_id not in book.parts:
        raise KeyError(
            part_id
        )

    try:
        index = book.part_order.index(
            part_id
        )
    except ValueError as exc:
        raise ValueError(
            f"Partie absente de l'ordre : {part_id}"
        ) from exc

    before_key: str | None = None
    after_key: str | None = None

    for candidate_id in reversed(
        book.part_order[:index]
    ):
        candidate = book.parts[
            candidate_id
        ]

        key = _proposal_key(
            candidate
        )

        if key is not None:
            before_key = key
            break

    for candidate_id in book.part_order[index + 1:]:
        candidate = book.parts[
            candidate_id
        ]

        key = _proposal_key(
            candidate
        )

        if key is not None:
            after_key = key
            break

    return {
        "before_proposal_key": before_key,
        "after_proposal_key": after_key,
    }


def _stored_manual_anchor(
    part: PartV4,
) -> dict[str, str | None] | None:

    value = part.metadata.get(
        "manual_anchor"
    )

    if not isinstance(
        value,
        dict,
    ):
        return None

    before = value.get(
        "before_proposal_key"
    )

    after = value.get(
        "after_proposal_key"
    )

    return {
        "before_proposal_key": (
            str(before)
            if before is not None
            else None
        ),
        "after_proposal_key": (
            str(after)
            if after is not None
            else None
        ),
    }


def _manual_anchor_is_current(
    book: BookV4,
    part: PartV4,
) -> bool:

    stored = _stored_manual_anchor(
        part
    )

    if stored is None:
        return False

    current = _current_manual_anchor(
        book,
        part.id,
    )

    return stored == current


# ==============================================================
# Construction du plan
# ==============================================================

def build_part_reanalysis_plan(
    book: BookV4,
    proposal: BookProposal,
) -> PartReanalysisPlan:

    proposal.validate()
    book.validate()

    plan = PartReanalysisPlan(
        proposal_id=proposal.id
    )

    plan.full_order_current = list(
        book.part_order
    )

    existing_by_key = (
        _parts_by_proposal_key(
            book
        )
    )

    for part in book.parts.values():
        if _proposal_key(part) is not None:
            continue

        plan.manual_part_ids.append(
            part.id
        )

        if not _manual_anchor_is_current(
            book,
            part,
        ):
            plan.manual_anchor_issues.append(
                part.id
            )

    proposed_by_key = {
        proposed.proposal_key: proposed
        for proposed in proposal.parts
    }

    # ==========================================================
    # Nouvelles parties
    # ==============================================================

    for key, proposed in proposed_by_key.items():
        if key not in existing_by_key:
            plan.new_parts.append(
                proposed
            )

    # ==========================================================
    # Parties disparues
    # ==============================================================

    for key, part in existing_by_key.items():
        if key not in proposed_by_key:
            plan.missing_part_ids.append(
                part.id
            )

    # ==========================================================
    # Modifications des parties existantes
    # ==============================================================

    for key, proposed in proposed_by_key.items():
        part = existing_by_key.get(
            key
        )

        if part is None:
            continue

        baseline = part.metadata.get(
            "analysis_baseline"
        )

        if not isinstance(
            baseline,
            dict,
        ):
            continue

        current = current_part_values(
            book,
            part,
        )

        proposed_values = (
            proposed_part_baseline(
                proposed
            )
        )

        for field_name, proposed_value in (
            proposed_values.items()
        ):
            baseline_value = baseline.get(
                field_name
            )

            current_value = current.get(
                field_name
            )

            if proposed_value == baseline_value:
                continue

            human_changed = (
                current_value != baseline_value
            )

            change = PartReanalysisChange(
                part_id=part.id,
                proposal_key=key,
                field_name=field_name,
                baseline_value=baseline_value,
                current_value=current_value,
                proposed_value=proposed_value,
                protected_by_human_change=(
                    human_changed
                ),
            )

            if human_changed:
                plan.protected_changes.append(
                    change
                )
                continue

            if (
                field_name == "parent_key"
                and proposed_value is not None
                and proposed_value
                not in existing_by_key
            ):
                plan.deferred_changes.append(
                    change
                )
                continue

            plan.automatic_changes.append(
                change
            )

    # ==========================================================
    # Ordre
    # ==============================================================

    baseline_order = book.metadata.get(
        "analysis_part_order_baseline",
        [],
    )

    if not isinstance(
        baseline_order,
        list,
    ):
        baseline_order = []

    plan.order_baseline = [
        str(value)
        for value in baseline_order
    ]

    # Cette fonction ignore volontairement les parties manuelles.
    plan.order_current = (
        book_part_order_keys(
            book
        )
    )

    plan.order_proposed = (
        proposal_part_order_keys(
            proposal
        )
    )

    plan.order_change_detected = (
        plan.order_proposed
        != plan.order_baseline
    )

    human_reordered_analysis_parts = (
        plan.order_current
        != plan.order_baseline
    )

    manual_structure_changed = bool(
        plan.manual_anchor_issues
    )

    # La simple présence d'une partie manuelle ne protège plus
    # tout l'ordre. Seul un déplacement hors de son ancre le fait.
    plan.order_protected = (
        plan.order_change_detected
        and (
            human_reordered_analysis_parts
            or manual_structure_changed
        )
    )

    return plan


def _resolve_parent_id(
    book: BookV4,
    parent_key: str | None,
) -> str | None:

    if parent_key is None:
        return None

    mapping = _part_ids_by_proposal_key(
        book
    )

    if parent_key not in mapping:
        raise ValueError(
            "Partie parente non disponible dans "
            f"le Livre : {parent_key}"
        )

    return mapping[
        parent_key
    ]


def _validate_parent_graph(
    parent_by_id: dict[str, str | None],
) -> None:

    for start_id in parent_by_id:
        seen: set[str] = set()
        current: str | None = start_id

        while current is not None:
            if current in seen:
                raise ValueError(
                    "Cycle détecté dans la hiérarchie "
                    "des parties."
                )

            seen.add(
                current
            )

            current = parent_by_id.get(
                current
            )


def apply_safe_part_reanalysis_changes(
    book: BookV4,
    proposal: BookProposal,
    plan: PartReanalysisPlan,
) -> int:

    if plan.proposal_id != proposal.id:
        raise ValueError(
            "Le plan ne correspond pas "
            "à la proposition."
        )

    proposal.validate()
    book.validate()

    projected_parents = {
        part.id: part.parent_id
        for part in book.parts.values()
    }

    for change in plan.automatic_changes:
        if change.field_name != "parent_key":
            continue

        projected_parents[
            change.part_id
        ] = _resolve_parent_id(
            book,
            change.proposed_value,
        )

    _validate_parent_graph(
        projected_parents
    )

    applied = 0

    for change in plan.automatic_changes:
        part = book.parts.get(
            change.part_id
        )

        if part is None:
            raise KeyError(
                change.part_id
            )

        current = current_part_values(
            book,
            part,
        ).get(
            change.field_name
        )

        if current != change.current_value:
            raise RuntimeError(
                "La partie a changé depuis "
                "la création du plan."
            )

        if change.field_name == "title":
            part.title = (
                change.proposed_value
            )

        elif change.field_name == "part_type":
            part.part_type = (
                change.proposed_value
            )

        elif change.field_name == "parent_key":
            part.parent_id = (
                _resolve_parent_id(
                    book,
                    change.proposed_value,
                )
            )

        else:
            raise ValueError(
                "Champ de partie inconnu : "
                f"{change.field_name}"
            )

        baseline = part.metadata.get(
            "analysis_baseline"
        )

        if not isinstance(
            baseline,
            dict,
        ):
            raise ValueError(
                f"Baseline absente : {part.id}"
            )

        baseline[
            change.field_name
        ] = change.proposed_value

        applied += 1

    book.metadata[
        "last_part_reanalysis_proposal_id"
    ] = proposal.id

    book.history.append(
        {
            "action": (
                "reanalyse_parties_proprietes"
            ),
            "proposal_id": proposal.id,
            "automatic_changes_applied": applied,
            "protected_changes_pending": len(
                plan.protected_changes
            ),
            "deferred_changes_pending": len(
                plan.deferred_changes
            ),
            "new_parts_pending": len(
                plan.new_parts
            ),
            "missing_parts_pending": len(
                plan.missing_part_ids
            ),
            "order_change_pending": (
                plan.order_change_detected
            ),
            "order_change_protected": (
                plan.order_protected
            ),
            "manual_anchor_issues": len(
                plan.manual_anchor_issues
            ),
        }
    )

    book.validate()

    return applied
