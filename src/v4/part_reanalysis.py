from __future__ import annotations

"""
TomeLinea V4 — réanalyse contrôlée des parties.

Principes :
- PartV4.id reste l'identité permanente ;
- l'Analyse travaille avec proposal_key ;
- une modification humaine n'est jamais écrasée ;
- les nouvelles parties sont détectées mais pas encore créées ici ;
- les parties disparues ne sont jamais supprimées ici ;
- les changements d'ordre sont détectés séparément ;
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

    order_baseline: list[str] = field(
        default_factory=list
    )

    order_current: list[str] = field(
        default_factory=list
    )

    order_proposed: list[str] = field(
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

    # Un parent créé manuellement doit être distingué
    # de toute clé issue de l'Analyse.
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


def build_part_reanalysis_plan(
    book: BookV4,
    proposal: BookProposal,
) -> PartReanalysisPlan:

    proposal.validate()
    book.validate()

    plan = PartReanalysisPlan(
        proposal_id=proposal.id
    )

    existing_by_key = (
        _parts_by_proposal_key(
            book
        )
    )

    for part in book.parts.values():
        if _proposal_key(part) is None:
            plan.manual_part_ids.append(
                part.id
            )

    proposed_by_key = {
        proposed.proposal_key: proposed
        for proposed in proposal.parts
    }

    # ==========================================================
    # Nouvelles parties
    # ==========================================================

    for key, proposed in proposed_by_key.items():
        if key not in existing_by_key:
            plan.new_parts.append(
                proposed
            )

    # ==========================================================
    # Parties disparues de la nouvelle analyse
    # ==========================================================

    for key, part in existing_by_key.items():
        if key not in proposed_by_key:
            plan.missing_part_ids.append(
                part.id
            )

    # ==========================================================
    # Modifications des parties existantes
    # ==========================================================

    for key, proposed in proposed_by_key.items():
        part = existing_by_key.get(
            key
        )

        if part is None:
            continue

        baseline = part.metadata.get(
            "analysis_baseline"
        )

        if not isinstance(baseline, dict):
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
                current_value
                != baseline_value
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

            # Un changement de parent vers une partie nouvelle
            # doit attendre sa création structurelle.
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
    # Ordre des parties
    # ==========================================================

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

    human_reordered = (
        plan.order_current
        != plan.order_baseline
    )

    # Pour l'instant une partie manuelle protège l'ordre.
    # Nous lui donnerons des ancres comme aux pages dans
    # une étape ultérieure.
    plan.order_protected = (
        plan.order_change_detected
        and (
            human_reordered
            or bool(plan.manual_part_ids)
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
    """
    Vérifie l'absence de cycles avant toute modification réelle.
    """

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
    """
    Applique uniquement les propriétés automatiques sûres.

    Ne crée, ne supprime et ne réordonne aucune partie.
    """

    if plan.proposal_id != proposal.id:
        raise ValueError(
            "Le plan ne correspond pas "
            "à la proposition."
        )

    proposal.validate()
    book.validate()

    # ==========================================================
    # Projection préalable des parents
    # ==========================================================

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

    # ==========================================================
    # Application
    # ==========================================================

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

        # Protection contre une modification entre la
        # préparation du plan et son application.
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
        }
    )

    book.validate()

    return applied
