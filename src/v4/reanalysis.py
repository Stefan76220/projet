from __future__ import annotations

"""
TomeLinea V4 — réanalyse contrôlée.

Principes :
- aucune correction humaine n'est écrasée ;
- aucune page ne disparaît automatiquement ;
- les nouvelles pages ne sont insérées automatiquement que lorsque
  l'ordre du livre est encore celui de la dernière analyse ;
- une page manuelle protège l'ordre ;
- une page absente de la nouvelle analyse bloque toute modification
  structurelle automatique jusqu'à décision humaine.
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


@dataclass(frozen=True, slots=True)
class StructuralApplyResult:
    applied: bool
    added_pages: int = 0
    reordered: bool = False
    reason: str | None = None


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

    order_baseline: list[str] = field(default_factory=list)
    order_current: list[str] = field(default_factory=list)
    order_proposed: list[str] = field(default_factory=list)

    order_change_detected: bool = False
    order_protected: bool = False
    order_blocked_by_missing_pages: bool = False

    manual_page_ids: list[str] = field(default_factory=list)


def _source_value(page: PageV4) -> dict[str, Any] | None:
    if page.source is None:
        return None

    return {
        "source_id": page.source.source_id,
        "source_version_id": page.source.source_version_id,
        "source_page": page.source.source_page,
    }


def current_page_values(page: PageV4) -> dict[str, Any]:
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

    # Nouvelles pages
    for proposal_key, proposed in proposed_by_key.items():
        if proposal_key not in existing_by_key:
            plan.new_pages.append(proposed)

    # Pages qui ne sont plus retrouvées.
    # Elles ne seront jamais supprimées automatiquement.
    for proposal_key, page in existing_by_key.items():
        if proposal_key not in proposed_by_key:
            plan.missing_page_ids.append(page.id)

    # Propriétés des pages existantes
    for proposal_key, proposed in proposed_by_key.items():
        page = existing_by_key.get(proposal_key)

        if page is None:
            continue

        baseline = page.metadata.get("analysis_baseline")

        if not isinstance(baseline, dict):
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

    # Ordre structurel
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

    has_manual_pages = bool(plan.manual_page_ids)

    plan.order_protected = (
        plan.order_change_detected
        and (
            human_reordered
            or has_manual_pages
        )
    )

    # Une disparition rend l'interprétation du nouvel ordre ambiguë.
    plan.order_blocked_by_missing_pages = bool(
        plan.missing_page_ids
    )

    return plan


def _apply_page_field(
    page: PageV4,
    field_name: str,
    value: Any,
) -> None:

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
            f"Champ non applicable automatiquement : {field_name}"
        )

    setattr(page, field_name, value)


def apply_safe_reanalysis_changes(
    book: BookV4,
    proposal: BookProposal,
    plan: ReanalysisPlan,
) -> int:

    if plan.proposal_id != proposal.id:
        raise ValueError(
            "Le plan ne correspond pas à la proposition."
        )

    proposal.validate()
    book.validate()

    applied = 0

    for change in plan.automatic_changes:
        page = book.pages.get(change.page_id)

        if page is None:
            raise KeyError(change.page_id)

        current = current_page_values(page).get(
            change.field_name
        )

        if current != change.current_value:
            raise RuntimeError(
                "Le Livre a changé depuis la création du plan."
            )

        _apply_page_field(
            page,
            change.field_name,
            change.proposed_value,
        )

        baseline = page.metadata.get(
            "analysis_baseline"
        )

        if not isinstance(baseline, dict):
            raise ValueError(
                f"Baseline absente : {page.id}"
            )

        baseline[change.field_name] = (
            change.proposed_value
        )

        applied += 1

    book.metadata["last_reanalysis_proposal_id"] = (
        proposal.id
    )

    book.history.append(
        {
            "action": "reanalyse_proprietes",
            "proposal_id": proposal.id,
            "automatic_changes_applied": applied,
            "protected_changes_pending": len(
                plan.protected_changes
            ),
        }
    )

    book.validate()

    return applied


def _new_page_from_proposal(
    proposed: ProposedPage,
    proposal_id: str,
) -> PageV4:
    """
    Crée une nouvelle PageV4 issue d'une réanalyse.
    """

    page = PageV4(
        page_type=proposed.page_type,
        title=proposed.title,
        origin=proposed.origin,
        source=proposed.source,
        part_id=proposed.part_key,
        model_id=proposed.model_key,
        recto_verso=proposed.recto_verso,
        spread_id=proposed.spread_key,
        spread_side=proposed.spread_side,
        is_compensation=proposed.is_compensation,
    )

    page.metadata["proposal_key"] = (
        proposed.proposal_key
    )
    page.metadata["proposal_id"] = proposal_id
    page.metadata["analysis_refs"] = list(
        proposed.analysis_refs
    )
    page.metadata["analysis_baseline"] = (
        proposed_page_baseline(proposed)
    )

    return page


def apply_safe_structural_changes(
    book: BookV4,
    proposal: BookProposal,
    plan: ReanalysisPlan,
) -> StructuralApplyResult:
    """
    Applique uniquement une évolution structurelle non ambiguë.

    Autorisé :
    - ajout de nouvelles pages ;
    - repositionnement suivant le nouvel ordre proposé.

    Interdit automatiquement :
    - suppression d'une page ;
    - modification d'un ordre déjà changé par l'utilisateur ;
    - modification si une page manuelle existe ;
    - modification si une ancienne page n'est plus retrouvée.
    """

    if plan.proposal_id != proposal.id:
        raise ValueError(
            "Le plan ne correspond pas à la proposition."
        )

    proposal.validate()
    book.validate()

    # Le plan doit encore correspondre à l'état réel du Livre.
    if book_order_keys(book) != plan.order_current:
        raise RuntimeError(
            "L'ordre du Livre a changé depuis la création du plan."
        )

    if proposal_order_keys(proposal) != plan.order_proposed:
        raise RuntimeError(
            "La proposition a changé depuis la création du plan."
        )

    if plan.order_protected:
        return StructuralApplyResult(
            applied=False,
            reason="ordre_protege",
        )

    if plan.order_blocked_by_missing_pages:
        return StructuralApplyResult(
            applied=False,
            reason="pages_absentes_a_verifier",
        )

    if plan.manual_page_ids:
        return StructuralApplyResult(
            applied=False,
            reason="pages_manuelles_presentes",
        )

    if (
        not plan.new_pages
        and not plan.order_change_detected
    ):
        return StructuralApplyResult(
            applied=False,
            reason="aucun_changement_structurel",
        )

    pages_by_key: dict[str, PageV4] = {}

    for page in book.pages.values():
        key = page.metadata.get("proposal_key")

        if key is not None:
            pages_by_key[str(key)] = page

    added = 0

    # Ajouter d'abord les nouvelles pages sans imposer encore l'ordre.
    for proposed in plan.new_pages:
        if proposed.proposal_key in pages_by_key:
            continue

        page = _new_page_from_proposal(
            proposed,
            proposal.id,
        )

        book.add_page(page)

        pages_by_key[proposed.proposal_key] = page
        added += 1

    # À ce stade aucune page ne doit manquer.
    expected_keys = set(plan.order_proposed)
    actual_keys = set(pages_by_key)

    if expected_keys != actual_keys:
        raise RuntimeError(
            "Impossible d'appliquer automatiquement le nouvel ordre : "
            "les ensembles de pages ne correspondent pas."
        )

    old_order = list(book.page_order)

    book.page_order = [
        pages_by_key[key].id
        for key in plan.order_proposed
    ]

    reordered = (
        book.page_order != old_order
    )

    # Le nouvel ordre automatique devient la nouvelle référence.
    book.metadata["analysis_order_baseline"] = list(
        plan.order_proposed
    )

    book.metadata["last_structural_proposal_id"] = (
        proposal.id
    )

    book.history.append(
        {
            "action": "reanalyse_structure_appliquee",
            "proposal_id": proposal.id,
            "pages_added": added,
            "order_updated": reordered,
        }
    )

    book.validate()

    return StructuralApplyResult(
        applied=True,
        added_pages=added,
        reordered=reordered,
    )
