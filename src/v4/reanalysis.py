from __future__ import annotations

"""
TomeLinea V4 — comparaison d'une réanalyse avec le Livre courant.

Ce module ne modifie jamais le Livre.
Il produit uniquement un plan de synchronisation contrôlé.
"""

from dataclasses import dataclass, field
from typing import Any

from src.v4.domain import BookV4, PageV4
from src.v4.proposal import (
    BookProposal,
    ProposedPage,
    proposed_page_baseline,
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

    Règle fondamentale :

    current == baseline
        => l'utilisateur n'a pas modifié ce champ ;
           TomeLinea peut proposer une mise à jour automatique.

    current != baseline
        => le champ a évolué depuis la proposition précédente ;
           TomeLinea le protège.
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

    proposed_by_key = {
        page.proposal_key: page
        for page in proposal.pages
    }

    # Pages nouvelles dans la nouvelle analyse.
    for proposal_key, proposed in proposed_by_key.items():
        if proposal_key not in existing_by_key:
            plan.new_pages.append(proposed)

    # Pages du Livre qui ne sont plus présentes dans la proposition.
    # Elles ne sont surtout pas supprimées automatiquement.
    for proposal_key, page in existing_by_key.items():
        if proposal_key not in proposed_by_key:
            plan.missing_page_ids.append(page.id)

    # Comparaison champ par champ.
    for proposal_key, proposed in proposed_by_key.items():
        page = existing_by_key.get(proposal_key)

        if page is None:
            continue

        baseline = page.metadata.get("analysis_baseline")

        if not isinstance(baseline, dict):
            # Une page sans baseline est considérée comme protégée.
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

    return plan
