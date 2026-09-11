from __future__ import annotations

"""TomeLinea V4 — synthèse des décisions après composition.

Cette couche ne modifie jamais la mise en page. Elle classe seulement les
événements produits pendant la composition selon les trois niveaux validés :
correction automatique, décision éditoriale, anomalie bloquante.
"""

from typing import Any


def _table_auto_correction(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "domain": "table",
        "kind": "first_row_isolated",
        "severity": "automatic",
        "table_id": item.get("tableId"),
        "segment": item.get("segment"),
        "rule": item.get("rule") or "first_row_isolated_auto_move",
        "message": "Une seule ligne du tableau était isolée en bas de page ; le début du tableau a été déplacé.",
        "details": {
            "pages_before": item.get("pagesBefore"),
            "row_pages_before": item.get("rowPagesBefore"),
        },
    }


def _table_editorial_decision(item: dict[str, Any]) -> dict[str, Any]:
    reason = item.get("reason") or "table_split_requires_editorial_choice"
    choices = item.get("choices") or [
        "conserver_coupure",
        "deplacer_debut_page_suivante",
    ]
    safe_group = (
        reason == "table_split_requires_editorial_choice"
        and list(choices) == ["conserver_coupure", "deplacer_debut_page_suivante"]
    )
    return {
        "domain": "table",
        "kind": "table_split",
        "severity": "editorial_decision",
        "table_id": item.get("tableId"),
        "segment": item.get("segment"),
        "message": "Ce tableau est partagé entre deux pages. Plusieurs choix éditoriaux sont acceptables.",
        "reason": reason,
        "choices": choices,
        "similarity_safe": safe_group,
        "similarity_key": "table:table_split:standard" if safe_group else None,
        "details": {
            "pages": item.get("pages"),
            "row_pages": item.get("rowPages"),
        },
    }


def build_editorial_review(
    host_snapshot: dict[str, Any] | None,
    *,
    text_review: dict[str, Any] | None = None,
    blocking_anomalies: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Construit la synthèse sans modifier le document ni prendre de décision."""

    host = host_snapshot or {}
    automatic = [
        _table_auto_correction(item)
        for item in host.get("table_first_row_orphan_fixes", [])
        if isinstance(item, dict)
    ]
    editorial = [
        _table_editorial_decision(item)
        for item in host.get("table_editorial_decisions", [])
        if isinstance(item, dict)
    ]
    text = text_review or {}
    automatic.extend(
        dict(item) for item in text.get("automatic_corrections", []) if isinstance(item, dict)
    )
    editorial.extend(
        dict(item) for item in text.get("editorial_decisions", []) if isinstance(item, dict)
    )
    blocking = [
        dict(item) for item in [
            *text.get("blocking_anomalies", []),
            *(blocking_anomalies or []),
        ] if isinstance(item, dict)
    ]

    return {
        "policy": {
            "automatic_only_when_unambiguous": True,
            "editorial_choices_never_block_composition": True,
            "blocking_reserved_for_impossible_or_unsafe_composition": True,
        },
        "automatic_corrections": automatic,
        "editorial_decisions": editorial,
        "blocking_anomalies": blocking,
        "counts": {
            "automatic_corrections": len(automatic),
            "editorial_decisions": len(editorial),
            "blocking_anomalies": len(blocking),
        },
        "composition_can_open": not blocking,
    }
