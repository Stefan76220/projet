from __future__ import annotations

"""
TomeLinea V4 — application structurelle des réanalyses de parties.

Règles :
- une nouvelle partie reçoit un UUID permanent ;
- aucune partie disparue de l'Analyse n'est supprimée ;
- un ordre modifié humainement n'est jamais écrasé ;
- les changements de parent différés sont appliqués seulement
  lorsque leur nouvelle partie parente existe ;
- une partie disparue est simplement signalée à vérifier.
"""

from dataclasses import dataclass

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
from src.v4.part_reanalysis import (
    PartReanalysisPlan,
    current_part_values,
)


MISSING_PART_STATUS = (
    "absente_de_la_derniere_analyse"
)


@dataclass(frozen=True, slots=True)
class PartStructuralApplyResult:
    applied: bool

    added_parts: int = 0
    reordered: bool = False
    deferred_parent_changes_applied: int = 0

    reason: str | None = None


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
                "Clé d'analyse de partie dupliquée : "
                f"{key}"
            )

        result[key] = part

    return result


def _validate_parent_graph(
    book: BookV4,
) -> None:
    """
    Vérifie l'absence de boucle dans la hiérarchie réelle du Livre.
    """

    parent_by_id = {
        part.id: part.parent_id
        for part in book.parts.values()
    }

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


def _new_part_from_proposal(
    proposed: ProposedPart,
    proposal_id: str,
) -> PartV4:

    part = PartV4(
        title=proposed.title,
        part_type=proposed.part_type,
    )

    part.metadata["proposal_key"] = (
        proposed.proposal_key
    )

    part.metadata["proposal_id"] = (
        proposal_id
    )

    part.metadata["analysis_refs"] = list(
        proposed.analysis_refs
    )

    part.metadata["analysis_baseline"] = (
        proposed_part_baseline(
            proposed
        )
    )

    return part


def apply_safe_part_structural_changes(
    book: BookV4,
    proposal: BookProposal,
    plan: PartReanalysisPlan,
) -> PartStructuralApplyResult:
    """
    Applique uniquement une évolution structurelle non ambiguë.

    Une partie disparue ou un ordre protégé bloque l'application
    structurelle automatique.
    """

    if plan.proposal_id != proposal.id:
        raise ValueError(
            "Le plan ne correspond pas à la proposition."
        )

    proposal.validate()
    book.validate()

    # Le Livre ne doit pas avoir changé depuis la création du plan.
    if (
        book_part_order_keys(book)
        != plan.order_current
    ):
        raise RuntimeError(
            "L'ordre des parties du Livre a changé "
            "depuis la création du plan."
        )

    current_manual_ids = {
        part.id
        for part in book.parts.values()
        if _proposal_key(part) is None
    }

    if current_manual_ids != set(
        plan.manual_part_ids
    ):
        raise RuntimeError(
            "Les parties manuelles ont changé "
            "depuis la création du plan."
        )

    if (
        proposal_part_order_keys(proposal)
        != plan.order_proposed
    ):
        raise RuntimeError(
            "La proposition a changé depuis "
            "la création du plan."
        )

    # Une disparition est ambiguë :
    # aucune suppression et aucun réordonnancement automatique.
    if plan.missing_part_ids:
        return PartStructuralApplyResult(
            applied=False,
            reason="parties_absentes_a_verifier",
        )

    if plan.order_protected:
        return PartStructuralApplyResult(
            applied=False,
            reason="ordre_parties_protege",
        )

    if plan.manual_part_ids:
        return PartStructuralApplyResult(
            applied=False,
            reason="parties_manuelles_presentes",
        )

    if (
        not plan.new_parts
        and not plan.deferred_changes
        and not plan.order_change_detected
    ):
        return PartStructuralApplyResult(
            applied=False,
            reason="aucun_changement_structurel",
        )

    proposed_by_key = {
        part.proposal_key: part
        for part in proposal.parts
    }

    parts_by_key = (
        _parts_by_proposal_key(
            book
        )
    )

    added = 0

    # ==========================================================
    # 1. Création des nouvelles parties
    #
    # Elles sont d'abord créées sans parent afin que toutes les
    # identités existent avant de construire la hiérarchie.
    # ==========================================================

    for proposed in plan.new_parts:
        if proposed.proposal_key in parts_by_key:
            continue

        part = _new_part_from_proposal(
            proposed,
            proposal.id,
        )

        book.add_part(
            part
        )

        parts_by_key[
            proposed.proposal_key
        ] = part

        added += 1

    # ==========================================================
    # 2. Parents des nouvelles parties
    # ==========================================================

    for proposed in plan.new_parts:
        part = parts_by_key[
            proposed.proposal_key
        ]

        if proposed.parent_key is None:
            part.parent_id = None
            continue

        parent = parts_by_key.get(
            proposed.parent_key
        )

        if parent is None:
            raise RuntimeError(
                "Parent proposé introuvable après création : "
                f"{proposed.parent_key}"
            )

        part.parent_id = (
            parent.id
        )

    # ==========================================================
    # 3. Changements de parent qui attendaient une nouvelle partie
    # ==========================================================

    deferred_applied = 0

    for change in plan.deferred_changes:
        if change.field_name != "parent_key":
            raise ValueError(
                "Seuls les changements de parent peuvent "
                "être différés ici."
            )

        part = book.parts.get(
            change.part_id
        )

        if part is None:
            raise KeyError(
                change.part_id
            )

        current_value = current_part_values(
            book,
            part,
        )["parent_key"]

        if current_value != change.current_value:
            raise RuntimeError(
                "Une partie a changé depuis "
                "la création du plan."
            )

        if change.proposed_value is None:
            new_parent_id = None

        else:
            parent = parts_by_key.get(
                change.proposed_value
            )

            if parent is None:
                raise RuntimeError(
                    "Nouvelle partie parente introuvable : "
                    f"{change.proposed_value}"
                )

            new_parent_id = parent.id

        part.parent_id = (
            new_parent_id
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

        baseline["parent_key"] = (
            change.proposed_value
        )

        deferred_applied += 1

    _validate_parent_graph(
        book
    )

    # ==========================================================
    # 4. Nouvel ordre
    # ==========================================================

    expected_keys = set(
        plan.order_proposed
    )

    actual_keys = set(
        parts_by_key
    )

    if expected_keys != actual_keys:
        raise RuntimeError(
            "Les parties du Livre ne correspondent pas "
            "à la nouvelle proposition."
        )

    old_order = list(
        book.part_order
    )

    book.part_order = [
        parts_by_key[key].id
        for key in plan.order_proposed
    ]

    reordered = (
        old_order != book.part_order
    )

    book.metadata[
        "analysis_part_order_baseline"
    ] = list(
        plan.order_proposed
    )

    book.metadata[
        "last_part_structural_proposal_id"
    ] = proposal.id

    book.history.append(
        {
            "action": (
                "reanalyse_parties_structure"
            ),
            "proposal_id": proposal.id,
            "parts_added": added,
            "order_updated": reordered,
            "deferred_parent_changes_applied": (
                deferred_applied
            ),
        }
    )

    book.validate()

    return PartStructuralApplyResult(
        applied=True,
        added_parts=added,
        reordered=reordered,
        deferred_parent_changes_applied=(
            deferred_applied
        ),
    )


def update_missing_part_status(
    book: BookV4,
    proposal: BookProposal,
    plan: PartReanalysisPlan,
) -> int:
    """
    Signale les parties non retrouvées sans jamais les supprimer.

    Si une partie réapparaît plus tard, le signalement disparaît.
    """

    if plan.proposal_id != proposal.id:
        raise ValueError(
            "Le plan ne correspond pas à la proposition."
        )

    proposal.validate()
    book.validate()

    missing_ids = set(
        plan.missing_part_ids
    )

    proposed_keys = {
        proposed.proposal_key
        for proposed in proposal.parts
    }

    flagged = 0

    for part in book.parts.values():
        key = _proposal_key(
            part
        )

        # Partie créée manuellement : hors Analyse.
        if key is None:
            continue

        if part.id in missing_ids:
            part.metadata[
                "reanalysis_status"
            ] = MISSING_PART_STATUS

            part.metadata[
                "missing_since_proposal_id"
            ] = proposal.id

            part.metadata[
                "requires_review"
            ] = True

            flagged += 1
            continue

        if key in proposed_keys:
            if (
                part.metadata.get(
                    "reanalysis_status"
                )
                == MISSING_PART_STATUS
            ):
                part.metadata.pop(
                    "reanalysis_status",
                    None,
                )

                part.metadata.pop(
                    "missing_since_proposal_id",
                    None,
                )

                part.metadata.pop(
                    "requires_review",
                    None,
                )

    book.history.append(
        {
            "action": (
                "statut_parties_absentes_actualise"
            ),
            "proposal_id": proposal.id,
            "parts_missing": flagged,
        }
    )

    book.validate()

    return flagged
