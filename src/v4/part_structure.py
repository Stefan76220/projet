from __future__ import annotations

"""
TomeLinea V4 — application structurelle des réanalyses de parties.

Règles :
- une nouvelle partie reçoit un UUID permanent ;
- aucune partie disparue de l'Analyse n'est supprimée ;
- un ordre modifié humainement n'est jamais écrasé ;
- une partie manuelle correctement ancrée est conservée pendant
  l'évolution automatique du reste de la structure ;
- son UUID reste inchangé ;
- son ancre est recalculée après une évolution automatique ;
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


# ==============================================================
# Ancres des parties manuelles
# ==============================================================

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


def _refresh_manual_anchors(
    book: BookV4,
    manual_part_ids: list[str],
) -> None:

    for part_id in manual_part_ids:
        part = book.parts.get(
            part_id
        )

        if part is None:
            continue

        part.metadata[
            "manual_anchor"
        ] = _current_manual_anchor(
            book,
            part_id,
        )


def _build_order_with_manual_parts(
    book: BookV4,
    proposal_keys: list[str],
    parts_by_key: dict[str, PartV4],
    manual_part_ids: list[str],
) -> list[str]:
    """
    Reconstruit l'ordre réel en conservant les parties manuelles.

    Politique :
    - priorité à l'ancienne borne droite ;
    - une insertion automatique dans un ancien intervalle se place
      donc avant la partie manuelle ;
    - en fin de livre, la borne gauche est utilisée ;
    - plusieurs parties manuelles du même intervalle gardent leur
      ordre relatif.
    """

    manual_set = set(
        manual_part_ids
    )

    manual_in_current_order = [
        part_id
        for part_id in book.part_order
        if part_id in manual_set
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

    for part_id in manual_in_current_order:
        part = book.parts[
            part_id
        ]

        anchor = _stored_manual_anchor(
            part
        )

        if anchor is None:
            detached.append(
                part_id
            )
            continue

        before_key = anchor[
            "before_proposal_key"
        ]

        after_key = anchor[
            "after_proposal_key"
        ]

        # Priorité à la borne droite.
        if (
            after_key is not None
            and after_key in proposal_key_set
        ):
            before_buckets.setdefault(
                after_key,
                [],
            ).append(
                part_id
            )

            continue

        # Cas de fin de structure.
        if (
            before_key is not None
            and before_key in proposal_key_set
        ):
            after_buckets.setdefault(
                before_key,
                [],
            ).append(
                part_id
            )

            continue

        detached.append(
            part_id
        )

    if detached:
        raise RuntimeError(
            "Une ou plusieurs parties manuelles "
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
            parts_by_key[
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
# Validation de la hiérarchie
# ==============================================================

def _validate_parent_graph(
    book: BookV4,
) -> None:

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

    part.metadata[
        "proposal_key"
    ] = proposed.proposal_key

    part.metadata[
        "proposal_id"
    ] = proposal_id

    part.metadata[
        "analysis_refs"
    ] = list(
        proposed.analysis_refs
    )

    part.metadata[
        "analysis_baseline"
    ] = proposed_part_baseline(
        proposed
    )

    return part


# ==============================================================
# Application structurelle
# ==============================================================

def apply_safe_part_structural_changes(
    book: BookV4,
    proposal: BookProposal,
    plan: PartReanalysisPlan,
) -> PartStructuralApplyResult:

    if plan.proposal_id != proposal.id:
        raise ValueError(
            "Le plan ne correspond pas à la proposition."
        )

    proposal.validate()
    book.validate()

    # Contrôle complet :
    # aucune partie, y compris manuelle, ne doit avoir bougé
    # depuis la préparation du plan.
    if list(book.part_order) != (
        plan.full_order_current
    ):
        raise RuntimeError(
            "L'ordre complet des parties a changé "
            "depuis la création du plan."
        )

    if (
        proposal_part_order_keys(
            proposal
        )
        != plan.order_proposed
    ):
        raise RuntimeError(
            "La proposition a changé depuis "
            "la création du plan."
        )

    # Jamais de suppression automatique.
    if plan.missing_part_ids:
        return PartStructuralApplyResult(
            applied=False,
            reason="parties_absentes_a_verifier",
        )

    if plan.manual_anchor_issues:
        return PartStructuralApplyResult(
            applied=False,
            reason="ancre_partie_manuelle_modifiee",
        )

    if plan.order_protected:
        return PartStructuralApplyResult(
            applied=False,
            reason="ordre_parties_protege",
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

    parts_by_key = (
        _parts_by_proposal_key(
            book
        )
    )

    added = 0

    # ==========================================================
    # 1. Création des nouvelles parties
    # ==============================================================

    for proposed in plan.new_parts:
        if (
            proposed.proposal_key
            in parts_by_key
        ):
            continue

        part = _new_part_from_proposal(
            proposed,
            proposal.id,
        )

        # Ajout temporaire en fin de structure.
        book.add_part(
            part
        )

        parts_by_key[
            proposed.proposal_key
        ] = part

        added += 1

    # ==========================================================
    # 2. Parents des nouvelles parties
    # ==============================================================

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
    # 3. Changements de parent différés
    # ==============================================================

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

            new_parent_id = (
                parent.id
            )

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

        baseline[
            "parent_key"
        ] = change.proposed_value

        deferred_applied += 1

    _validate_parent_graph(
        book
    )

    # ==========================================================
    # 4. Reconstruction de l'ordre
    # ==============================================================

    expected_keys = set(
        plan.order_proposed
    )

    actual_keys = set(
        parts_by_key
    )

    if expected_keys != actual_keys:
        raise RuntimeError(
            "Les parties issues de l'Analyse ne correspondent "
            "pas à la nouvelle proposition."
        )

    old_order = list(
        book.part_order
    )

    new_order = (
        _build_order_with_manual_parts(
            book,
            plan.order_proposed,
            parts_by_key,
            plan.manual_part_ids,
        )
    )

    if set(new_order) != set(
        book.parts
    ):
        raise RuntimeError(
            "Le nouvel ordre ne contient pas exactement "
            "toutes les parties du Livre."
        )

    if len(new_order) != len(
        book.parts
    ):
        raise RuntimeError(
            "Le nouvel ordre contient un nombre "
            "incohérent de parties."
        )

    book.part_order = (
        new_order
    )

    reordered = (
        old_order
        != book.part_order
    )

    # Nouvelle référence automatique.
    book.metadata[
        "analysis_part_order_baseline"
    ] = list(
        plan.order_proposed
    )

    # Les parties manuelles adoptent leur nouvel environnement
    # comme référence, sans changer d'identité.
    _refresh_manual_anchors(
        book,
        plan.manual_part_ids,
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
            "manual_parts_preserved": len(
                plan.manual_part_ids
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


# ==============================================================
# Parties absentes
# ==============================================================

def update_missing_part_status(
    book: BookV4,
    proposal: BookProposal,
    plan: PartReanalysisPlan,
) -> int:

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

        # Partie manuelle : hors Analyse.
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
