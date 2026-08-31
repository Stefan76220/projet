from __future__ import annotations

"""
TomeLinea V4 — réanalyse contrôlée.

Ce module compare une nouvelle proposition d'analyse avec le Livre
courant.

Principes :
- aucune correction humaine n'est écrasée ;
- aucune page ne disparaît automatiquement ;
- un changement d'ordre n'est considéré automatique que si l'ordre
  précédent n'a pas été modifié par l'utilisateur ;
- la présence de pages sans origine de proposition protège également
  l'ordre structurel.
"""

from dataclasses import dataclass, field
from typing import Any

from src.v4.domain import BookV4, PageV4
from src.v4.proposal import (
    BookProposal,
    ProposedPage,
    book_order_keys,
    proposed_page_baseline,
    proposal_order_keys,
)


@dataclass(frozen=True, slots=True)
class ReanalysisChange:
    page_id: str
    proposal_key: str
    field_name: str

    baseline_value: Any
    current_value: Any
    proposed_value: Any

    protected_by_human_change: bool


@dataclass(slots=True)
class ReanalysisPlan:
    proposal_id: str

    automatic_changes: list[ReanalysisChange] = field(
        default_factory=list
    )

    protected_changes: list[ReanalysisChange] = field(
        default_factory=list
    )

    new_pages: list[ProposedPage] = field(
        default_factory=list
    )

    missing_page_ids: list[str] = field(
        default_factory=list
    )

    # État structurel
    order_baseline: list[str] = field(default_factory=list)
    order_current: list[str] = field(default_factory=list)
    order_proposed: list[str] = field(default_factory=list)

    order_change_detected: bool = False
    order_protected: bool = False

    manual_page_ids: list[str] = field(default_factory=list)


def _source_value(page: PageV4) -> dict[str, Any] | None:
    if page.source is None:
        return None

    return {
        "source_id": page.source.source_id,
        "source_version_id": page.source.source_version_id,
        "source_page": page.source.source_page,
    }


def current_page_values(
    page: PageV4,
) -> dict[str, Any]:
    """
    Représentation comparable avec analysis_baseline.
    """

    return {
        "page_type": page.page_type,
        "title": page.title,
        "origin": page.origin.value,
        "source": _source_value(page),
        "part_id": page.part_id,
        "model_id": page.model_id,
        "recto_verso": page.recto_verso,
        "spread_id": page.spread_id,
        "spread_side": page.spread_side,
        "is_compensation": page.is_compensation,
    }


def build_reanalysis_plan(
    book: BookV4,
    proposal: BookProposal,
) -> ReanalysisPlan:
    """
    Compare une nouvelle proposition avec le Livre courant.

    Une valeur de page est protégée dès que :
        current != baseline

    L'ordre est protégé dès que :
        ordre courant != baseline d'analyse

    ou si le Livre possède des pages sans proposal_key.
    """

    proposal.validate()
    book.validate()

    plan = ReanalysisPlan(
        proposal_id=proposal.id
    )

    existing_by_key: dict[str, PageV4] = {}

    for page in book.pages.values():
        proposal_key = page.metadata.get("proposal_key")

        if proposal_key:
            existing_by_key[str(proposal_key)] = page
        else:
            plan.manual_page_ids.append(page.id)

    proposed_by_key = {
        page.proposal_key: page
        for page in proposal.pages
    }

    # ----------------------------------------------------------
    # Pages nouvelles
    # ----------------------------------------------------------

    for proposal_key, proposed in proposed_by_key.items():
        if proposal_key not in existing_by_key:
            plan.new_pages.append(proposed)

    # ----------------------------------------------------------
    # Pages absentes de la nouvelle proposition
    #
    # Important :
    # aucune suppression automatique.
    # ----------------------------------------------------------

    for proposal_key, page in existing_by_key.items():
        if proposal_key not in proposed_by_key:
            plan.missing_page_ids.append(page.id)

    # ----------------------------------------------------------
    # Comparaison des propriétés de page
    # ----------------------------------------------------------

    for proposal_key, proposed in proposed_by_key.items():
        page = existing_by_key.get(proposal_key)

        if page is None:
            continue

        baseline = page.metadata.get("analysis_baseline")

        if not isinstance(baseline, dict):
            # En l'absence de baseline, on ne prend aucun risque.
            continue

        current = current_page_values(page)
        new_values = proposed_page_baseline(proposed)

        for field_name, proposed_value in new_values.items():
            baseline_value = baseline.get(field_name)
            current_value = current.get(field_name)

            if proposed_value == baseline_value:
                continue

            human_changed = (
                current_value != baseline_value
            )

            change = ReanalysisChange(
                page_id=page.id,
                proposal_key=proposal_key,
                field_name=field_name,
                baseline_value=baseline_value,
                current_value=current_value,
                proposed_value=proposed_value,
                protected_by_human_change=human_changed,
            )

            if human_changed:
                plan.protected_changes.append(change)
            else:
                plan.automatic_changes.append(change)

    # ----------------------------------------------------------
    # Comparaison structurelle de l'ordre
    # ----------------------------------------------------------

    baseline = book.metadata.get(
        "analysis_order_baseline",
        [],
    )

    if not isinstance(baseline, list):
        baseline = []

    plan.order_baseline = [
        str(value)
        for value in baseline
    ]

    plan.order_current = book_order_keys(book)
    plan.order_proposed = proposal_order_keys(proposal)

    plan.order_change_detected = (
        plan.order_proposed != plan.order_baseline
    )

    human_reordered = (
        plan.order_current != plan.order_baseline
    )

    # Une page manuelle pourrait avoir été insérée entre deux pages
    # issues de l'analyse. On protège donc l'ordre global.
    has_manual_pages = bool(plan.manual_page_ids)

    plan.order_protected = (
        plan.order_change_detected
        and (
            human_reordered
            or has_manual_pages
        )
    )

    return plan


def _apply_page_field(
    page: PageV4,
    field_name: str,
    value: Any,
) -> None:
    """
    Applique une valeur issue de l'analyse sur un champ PageV4.

    Cette fonction n'est appelée que pour un changement préalablement
    classé comme automatique et sûr.
    """

    from src.v4.domain import PageOrigin, SourceLink

    if field_name == "origin":
        page.origin = PageOrigin(value)
        return

    if field_name == "source":
        if value is None:
            page.source = None
        else:
            page.source = SourceLink(
                source_id=value["source_id"],
                source_version_id=value["source_version_id"],
                source_page=value.get("source_page"),
            )
        return

    allowed_fields = {
        "page_type",
        "title",
        "part_id",
        "model_id",
        "recto_verso",
        "spread_id",
        "spread_side",
        "is_compensation",
    }

    if field_name not in allowed_fields:
        raise ValueError(
            f"Champ de réanalyse non applicable automatiquement : "
            f"{field_name}"
        )

    setattr(page, field_name, value)


def apply_safe_reanalysis_changes(
    book: BookV4,
    proposal: BookProposal,
    plan: ReanalysisPlan,
) -> int:
    """
    Applique uniquement les changements de propriétés automatiques sûrs.

    Cette fonction ne traite pas encore :
    - les nouvelles pages ;
    - les pages absentes ;
    - les déplacements structurels.
    """

    if plan.proposal_id != proposal.id:
        raise ValueError(
            "Le plan de réanalyse ne correspond pas à la proposition."
        )

    proposal.validate()
    book.validate()

    proposed_by_key = {
        proposed.proposal_key: proposed
        for proposed in proposal.pages
    }

    applied = 0

    for change in plan.automatic_changes:
        page = book.pages.get(change.page_id)

        if page is None:
            raise KeyError(
                f"Page du plan introuvable : {change.page_id}"
            )

        if change.protected_by_human_change:
            raise ValueError(
                "Un changement protégé ne peut pas être appliqué "
                "automatiquement."
            )

        current = current_page_values(page).get(
            change.field_name
        )

        # Vérifie que la page n'a pas changé après création du plan.
        if current != change.current_value:
            raise RuntimeError(
                f"La page {change.page_id} a changé depuis "
                f"la préparation de la réanalyse."
            )

        _apply_page_field(
            page,
            change.field_name,
            change.proposed_value,
        )

        baseline = page.metadata.get("analysis_baseline")

        if not isinstance(baseline, dict):
            raise ValueError(
                f"Baseline absente pour la page {page.id}"
            )

        baseline[change.field_name] = (
            change.proposed_value
        )

        applied += 1

    for proposed_key, proposed in proposed_by_key.items():
        page = next(
            (
                existing
                for existing in book.pages.values()
                if existing.metadata.get("proposal_key")
                == proposed_key
            ),
            None,
        )

        if page is not None:
            page.metadata["last_reanalysis_refs"] = list(
                proposed.analysis_refs
            )

    book.metadata["last_reanalysis_proposal_id"] = (
        proposal.id
    )

    book.history.append(
        {
            "action": "reanalyse_appliquee_partiellement",
            "proposal_id": proposal.id,
            "automatic_changes_applied": applied,
            "protected_changes_pending": len(
                plan.protected_changes
            ),
            "new_pages_pending": len(
                plan.new_pages
            ),
            "missing_pages_pending": len(
                plan.missing_page_ids
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
