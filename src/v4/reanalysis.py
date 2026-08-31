from __future__ import annotations

"""
TomeLinea V4 — réanalyse contrôlée.

Principes :
- aucune correction humaine n'est écrasée ;
- aucune page ne disparaît automatiquement ;
- les nouvelles pages peuvent être intégrées automatiquement lorsque
  l'ordre issu de l'analyse n'a pas été modifié volontairement ;
- les pages manuelles correctement ancrées sont conservées dans leur
  secteur logique ;
- une page manuelle déplacée hors de son ancre protège l'ordre ;
- une page absente de la nouvelle analyse bloque toute modification
  structurelle automatique ;
- les références de parties provenant de l'Analyse sont toujours
  résolues vers les UUID permanents PartV4 du Livre.
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

    full_order_current: list[str] = field(default_factory=list)

    order_change_detected: bool = False
    order_protected: bool = False
    order_blocked_by_missing_pages: bool = False

    manual_page_ids: list[str] = field(default_factory=list)
    manual_anchor_issues: list[str] = field(default_factory=list)


def _source_value(
    page: PageV4,
) -> dict[str, Any] | None:

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


def _proposal_key(
    page: PageV4,
) -> str | None:

    value = page.metadata.get("proposal_key")

    if value is None:
        return None

    return str(value)


# ==============================================================
# Résolution des parties
# ==============================================================

def _part_ids_by_proposal_key(
    book: BookV4,
) -> dict[str, str]:
    """
    Traduit les clés de parties de l'Analyse vers les UUID permanents
    des PartV4 déjà présentes dans le Livre.
    """

    result: dict[str, str] = {}

    for part in book.parts.values():
        proposal_key = part.metadata.get(
            "proposal_key"
        )

        if proposal_key is None:
            continue

        key = str(proposal_key)

        if key in result:
            raise ValueError(
                "Plusieurs parties du Livre utilisent la même "
                f"clé d'analyse : {key}"
            )

        result[key] = part.id

    return result


def _resolve_part_id(
    book: BookV4,
    part_key: str | None,
) -> str | None:
    """
    Transforme ProposedPage.part_key en véritable PartV4.id.

    Une clé nouvelle n'est pas inventée silencieusement.
    La création automatique des nouvelles parties sera traitée
    explicitement dans l'étape suivante.
    """

    if part_key is None:
        return None

    mapping = _part_ids_by_proposal_key(
        book
    )

    if part_key not in mapping:
        raise ValueError(
            "La réanalyse référence une partie qui n'existe "
            f"pas encore dans le Livre : {part_key}"
        )

    return mapping[part_key]


def _proposed_page_values(
    book: BookV4,
    proposed: ProposedPage,
) -> dict[str, Any]:
    """
    Valeurs proposées exprimées dans le référentiel réel du Livre.
    """

    resolved_part_id = _resolve_part_id(
        book,
        proposed.part_key,
    )

    return proposed_page_baseline(
        proposed,
        resolved_part_id=resolved_part_id,
    )


# ==============================================================
# Pages manuelles et ancres
# ==============================================================

def _current_manual_anchor(
    book: BookV4,
    page_id: str,
) -> dict[str, str | None]:

    if page_id not in book.pages:
        raise KeyError(page_id)

    try:
        index = book.page_order.index(
            page_id
        )
    except ValueError as exc:
        raise ValueError(
            f"Page absente de l'ordre : {page_id}"
        ) from exc

    before_key: str | None = None
    after_key: str | None = None

    for candidate_id in reversed(
        book.page_order[:index]
    ):
        candidate = book.pages[
            candidate_id
        ]

        key = _proposal_key(
            candidate
        )

        if key is not None:
            before_key = key
            break

    for candidate_id in book.page_order[index + 1:]:
        candidate = book.pages[
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
    page: PageV4,
) -> dict[str, str | None] | None:

    value = page.metadata.get(
        "manual_anchor"
    )

    if not isinstance(value, dict):
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
    page: PageV4,
) -> bool:

    stored = _stored_manual_anchor(
        page
    )

    if stored is None:
        return False

    current = _current_manual_anchor(
        book,
        page.id,
    )

    return stored == current


def _refresh_manual_anchors(
    book: BookV4,
    manual_page_ids: list[str],
) -> None:

    for page_id in manual_page_ids:
        page = book.pages.get(
            page_id
        )

        if page is None:
            continue

        page.metadata["manual_anchor"] = (
            _current_manual_anchor(
                book,
                page_id,
            )
        )


# ==============================================================
# Construction du plan
# ==============================================================

def build_reanalysis_plan(
    book: BookV4,
    proposal: BookProposal,
) -> ReanalysisPlan:

    proposal.validate()
    book.validate()

    plan = ReanalysisPlan(
        proposal_id=proposal.id
    )

    plan.full_order_current = list(
        book.page_order
    )

    existing_by_key: dict[str, PageV4] = {}

    for page in book.pages.values():
        proposal_key = _proposal_key(
            page
        )

        if proposal_key is not None:
            existing_by_key[
                proposal_key
            ] = page

        else:
            plan.manual_page_ids.append(
                page.id
            )

            if not _manual_anchor_is_current(
                book,
                page,
            ):
                plan.manual_anchor_issues.append(
                    page.id
                )

    proposed_by_key = {
        page.proposal_key: page
        for page in proposal.pages
    }

    # ----------------------------------------------------------
    # Nouvelles pages
    # ----------------------------------------------------------

    for proposal_key, proposed in proposed_by_key.items():
        if proposal_key not in existing_by_key:
            plan.new_pages.append(
                proposed
            )

    # ----------------------------------------------------------
    # Pages absentes
    # ----------------------------------------------------------

    for proposal_key, page in existing_by_key.items():
        if proposal_key not in proposed_by_key:
            plan.missing_page_ids.append(
                page.id
            )

    # ----------------------------------------------------------
    # Propriétés des pages existantes
    # ----------------------------------------------------------

    for proposal_key, proposed in proposed_by_key.items():
        page = existing_by_key.get(
            proposal_key
        )

        if page is None:
            continue

        baseline = page.metadata.get(
            "analysis_baseline"
        )

        if not isinstance(baseline, dict):
            continue

        current = current_page_values(
            page
        )

        # Important :
        # part_key est résolu ici vers PartV4.id.
        new_values = _proposed_page_values(
            book,
            proposed,
        )

        for field_name, proposed_value in new_values.items():
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

            change = ReanalysisChange(
                page_id=page.id,
                proposal_key=proposal_key,
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

            else:
                plan.automatic_changes.append(
                    change
                )

    # ----------------------------------------------------------
    # Ordre structurel des pages
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

    plan.order_current = book_order_keys(
        book
    )

    plan.order_proposed = proposal_order_keys(
        proposal
    )

    plan.order_change_detected = (
        plan.order_proposed
        != plan.order_baseline
    )

    human_reordered_analysis_pages = (
        plan.order_current
        != plan.order_baseline
    )

    manual_structure_changed = bool(
        plan.manual_anchor_issues
    )

    plan.order_protected = (
        plan.order_change_detected
        and (
            human_reordered_analysis_pages
            or manual_structure_changed
        )
    )

    plan.order_blocked_by_missing_pages = bool(
        plan.missing_page_ids
    )

    return plan


# ==============================================================
# Application des propriétés
# ==============================================================

def _apply_page_field(
    page: PageV4,
    field_name: str,
    value: Any,
) -> None:

    from src.v4.domain import (
        PageOrigin,
        SourceLink,
    )

    if field_name == "origin":
        page.origin = PageOrigin(
            value
        )
        return

    if field_name == "source":
        if value is None:
            page.source = None
        else:
            page.source = SourceLink(
                source_id=value[
                    "source_id"
                ],
                source_version_id=value[
                    "source_version_id"
                ],
                source_page=value.get(
                    "source_page"
                ),
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
            "Champ non applicable automatiquement : "
            f"{field_name}"
        )

    setattr(
        page,
        field_name,
        value,
    )


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
        page = book.pages.get(
            change.page_id
        )

        if page is None:
            raise KeyError(
                change.page_id
            )

        current = current_page_values(
            page
        ).get(
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

        baseline[
            change.field_name
        ] = change.proposed_value

        applied += 1

    book.metadata[
        "last_reanalysis_proposal_id"
    ] = proposal.id

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


# ==============================================================
# Création d'une nouvelle page depuis une proposition
# ==============================================================

def _new_page_from_proposal(
    book: BookV4,
    proposed: ProposedPage,
    proposal_id: str,
) -> PageV4:

    resolved_part_id = _resolve_part_id(
        book,
        proposed.part_key,
    )

    page = PageV4(
        page_type=proposed.page_type,
        title=proposed.title,
        origin=proposed.origin,
        source=proposed.source,
        part_id=resolved_part_id,
        model_id=proposed.model_key,
        recto_verso=proposed.recto_verso,
        spread_id=proposed.spread_key,
        spread_side=proposed.spread_side,
        is_compensation=(
            proposed.is_compensation
        ),
    )

    page.metadata[
        "proposal_key"
    ] = proposed.proposal_key

    page.metadata[
        "proposal_id"
    ] = proposal_id

    page.metadata[
        "analysis_refs"
    ] = list(
        proposed.analysis_refs
    )

    page.metadata[
        "analysis_baseline"
    ] = proposed_page_baseline(
        proposed,
        resolved_part_id=resolved_part_id,
    )

    return page


# ==============================================================
# Reconstruction de l'ordre avec pages manuelles
# ==============================================================

def _build_order_with_manual_pages(
    book: BookV4,
    proposal_keys: list[str],
    pages_by_key: dict[str, PageV4],
    manual_page_ids: list[str],
) -> list[str]:

    manual_set = set(
        manual_page_ids
    )

    manual_in_current_order = [
        page_id
        for page_id in book.page_order
        if page_id in manual_set
    ]

    before_buckets: dict[
        str,
        list[str],
    ] = {}

    after_buckets: dict[
        str,
        list[str],
    ] = {}

    detached: list[str] = []

    proposal_key_set = set(
        proposal_keys
    )

    for page_id in manual_in_current_order:
        page = book.pages[
            page_id
        ]

        anchor = _stored_manual_anchor(
            page
        )

        if anchor is None:
            detached.append(
                page_id
            )
            continue

        before_key = anchor[
            "before_proposal_key"
        ]

        after_key = anchor[
            "after_proposal_key"
        ]

        if (
            after_key is not None
            and after_key in proposal_key_set
        ):
            before_buckets.setdefault(
                after_key,
                [],
            ).append(
                page_id
            )

            continue

        if (
            before_key is not None
            and before_key in proposal_key_set
        ):
            after_buckets.setdefault(
                before_key,
                [],
            ).append(
                page_id
            )

            continue

        detached.append(
            page_id
        )

    if detached:
        raise RuntimeError(
            "Une ou plusieurs pages manuelles "
            "n'ont plus d'ancre exploitable."
        )

    result: list[str] = []

    for key in proposal_keys:
        result.extend(
            before_buckets.get(
                key,
                [],
            )
        )

        result.append(
            pages_by_key[
                key
            ].id
        )

        result.extend(
            after_buckets.get(
                key,
                [],
            )
        )

    return result


# ==============================================================
# Application structurelle
# ==============================================================

def apply_safe_structural_changes(
    book: BookV4,
    proposal: BookProposal,
    plan: ReanalysisPlan,
) -> StructuralApplyResult:

    if plan.proposal_id != proposal.id:
        raise ValueError(
            "Le plan ne correspond pas à la proposition."
        )

    proposal.validate()
    book.validate()

    if list(book.page_order) != (
        plan.full_order_current
    ):
        raise RuntimeError(
            "L'ordre complet du Livre a changé "
            "depuis la création du plan."
        )

    if proposal_order_keys(
        proposal
    ) != plan.order_proposed:
        raise RuntimeError(
            "La proposition a changé depuis "
            "la création du plan."
        )

    if plan.order_protected:
        return StructuralApplyResult(
            applied=False,
            reason="ordre_protege",
        )

    if plan.manual_anchor_issues:
        return StructuralApplyResult(
            applied=False,
            reason="ancre_manuelle_modifiee",
        )

    if plan.order_blocked_by_missing_pages:
        return StructuralApplyResult(
            applied=False,
            reason="pages_absentes_a_verifier",
        )

    if (
        not plan.new_pages
        and not plan.order_change_detected
    ):
        return StructuralApplyResult(
            applied=False,
            reason="aucun_changement_structurel",
        )

    pages_by_key: dict[
        str,
        PageV4,
    ] = {}

    for page in book.pages.values():
        key = _proposal_key(
            page
        )

        if key is not None:
            pages_by_key[
                key
            ] = page

    added = 0

    for proposed in plan.new_pages:
        if proposed.proposal_key in pages_by_key:
            continue

        page = _new_page_from_proposal(
            book,
            proposed,
            proposal.id,
        )

        book.add_page(
            page
        )

        pages_by_key[
            proposed.proposal_key
        ] = page

        added += 1

    expected_keys = set(
        plan.order_proposed
    )

    actual_keys = set(
        pages_by_key
    )

    if expected_keys != actual_keys:
        raise RuntimeError(
            "Impossible d'appliquer le nouvel ordre : "
            "les ensembles de pages ne correspondent pas."
        )

    old_order = list(
        book.page_order
    )

    new_order = (
        _build_order_with_manual_pages(
            book,
            plan.order_proposed,
            pages_by_key,
            plan.manual_page_ids,
        )
    )

    if set(new_order) != set(book.pages):
        raise RuntimeError(
            "Le nouvel ordre structurel ne contient "
            "pas exactement toutes les pages du Livre."
        )

    if len(new_order) != len(book.pages):
        raise RuntimeError(
            "Le nouvel ordre structurel contient "
            "un nombre incohérent de pages."
        )

    book.page_order = new_order

    reordered = (
        book.page_order != old_order
    )

    book.metadata[
        "analysis_order_baseline"
    ] = list(
        plan.order_proposed
    )

    _refresh_manual_anchors(
        book,
        plan.manual_page_ids,
    )

    book.metadata[
        "last_structural_proposal_id"
    ] = proposal.id

    book.history.append(
        {
            "action": "reanalyse_structure_appliquee",
            "proposal_id": proposal.id,
            "pages_added": added,
            "order_updated": reordered,
            "manual_pages_preserved": len(
                plan.manual_page_ids
            ),
        }
    )

    book.validate()

    return StructuralApplyResult(
        applied=True,
        added_pages=added,
        reordered=reordered,
    )


# ==============================================================
# Pages absentes
# ==============================================================

MISSING_PAGE_STATUS = (
    "absente_de_la_derniere_analyse"
)


def update_missing_page_status(
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

    missing_ids = set(
        plan.missing_page_ids
    )

    proposed_keys = {
        proposed.proposal_key
        for proposed in proposal.pages
    }

    flagged = 0

    for page in book.pages.values():
        proposal_key = _proposal_key(
            page
        )

        if proposal_key is None:
            continue

        if page.id in missing_ids:
            page.metadata[
                "reanalysis_status"
            ] = MISSING_PAGE_STATUS

            page.metadata[
                "missing_since_proposal_id"
            ] = proposal.id

            page.metadata[
                "requires_review"
            ] = True

            flagged += 1
            continue

        if proposal_key in proposed_keys:
            if (
                page.metadata.get(
                    "reanalysis_status"
                )
                == MISSING_PAGE_STATUS
            ):
                page.metadata.pop(
                    "reanalysis_status",
                    None,
                )

                page.metadata.pop(
                    "missing_since_proposal_id",
                    None,
                )

                page.metadata.pop(
                    "requires_review",
                    None,
                )

    book.history.append(
        {
            "action": "statut_pages_absentes_actualise",
            "proposal_id": proposal.id,
            "pages_missing": flagged,
        }
    )

    book.validate()

    return flagged
