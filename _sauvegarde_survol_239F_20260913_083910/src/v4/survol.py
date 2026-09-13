from __future__ import annotations

"""Repères du Survol guidé TomeLinea V4.

Ce module reste indépendant de Tkinter : il décrit uniquement les points
d'attention rattachés aux vraies pages du Livre.
"""

from dataclasses import dataclass, field
import re
from typing import Any, Iterable


@dataclass(frozen=True)
class SurvolMarker:
    marker_id: str
    page_id: str
    kind: str
    family: str
    title: str
    message: str
    priority: int = 100
    doubtful: bool = False
    unit_key: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict, compare=False)


def _norm(value: Any) -> str:
    text = str(value or "").strip().casefold()
    return re.sub(r"\s+", " ", text)


def _number(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _geometry_value(geometry: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        if key not in geometry:
            continue
        value = _number(geometry.get(key))
        if value is not None:
            return value
    return None


def _image_family(element: dict[str, Any], book) -> tuple[str, str]:
    geometry = element.get("geometry")
    if not isinstance(geometry, dict):
        geometry = {}

    width = _geometry_value(
        geometry,
        "width_mm",
        "w_mm",
        "width",
        "w",
    )
    height = _geometry_value(
        geometry,
        "height_mm",
        "h_mm",
        "height",
        "h",
    )

    fmt = getattr(book, "format", None)
    page_width = _number(getattr(fmt, "width_mm", None))
    page_height = _number(getattr(fmt, "height_mm", None))

    if (
        width is not None
        and height is not None
        and page_width
        and page_height
        and width >= page_width * 0.82
        and height >= page_height * 0.82
    ):
        return "image:full_page", "Image pleine page"

    return "image:integrated", "Image intégrée"


def _structure_family(unit: dict[str, Any]) -> str:
    """Signature stricte des cas structuraux pouvant partager une règle.

    Une décision prise sur un chapitre ne vaut pas pour tous les chapitres :
    type, niveau/style, mode de détection, zone et meilleur candidat doivent
    rester cohérents.
    """

    editorial_type = _norm(unit.get("editorial_type") or "unknown")
    style = _norm(unit.get("style_id") or "sans_style").replace(" ", "_")
    detected_by = _norm(unit.get("detected_by") or "inconnu").replace(" ", "_")
    zone = _norm(unit.get("zone") or "bodymatter").replace(" ", "_")

    candidate = "aucun"
    candidates = unit.get("candidates")
    if isinstance(candidates, list) and candidates:
        first = candidates[0]
        if isinstance(first, dict):
            candidate = _norm(first.get("type") or "aucun").replace(" ", "_")

    return (
        "structure:"
        f"{editorial_type}:"
        f"{style}:"
        f"{detected_by}:"
        f"{zone}:"
        f"{candidate}"
    )


def build_survol_markers(
    book,
    editorial_analysis: dict[str, Any] | None,
    structure_page_ids: dict[str, str] | None,
    *,
    cover_page_ids: Iterable[str] = (),
) -> dict[str, list[SurvolMarker]]:
    """Construit les repères dans l'ordre physique du Livre."""

    if book is None:
        return {}

    order = [
        str(page_id)
        for page_id in list(getattr(book, "page_order", ()) or ())
    ]
    order_index = {
        page_id: index
        for index, page_id in enumerate(order)
    }
    covers = {
        str(page_id)
        for page_id in cover_page_ids
    }
    by_page: dict[str, list[SurvolMarker]] = {}

    analysis = (
        editorial_analysis
        if isinstance(editorial_analysis, dict)
        else {}
    )
    unit_pages = (
        structure_page_ids
        if isinstance(structure_page_ids, dict)
        else {}
    )

    for unit in list(analysis.get("units") or []):
        if not isinstance(unit, dict):
            continue

        editorial_type = str(
            unit.get("editorial_type")
            or "unknown"
        )
        decision = str(
            unit.get("decision")
            or ""
        )

        if editorial_type in {
            "technical_unit",
            "merge_previous",
        }:
            continue

        if decision in {
            "technical",
            "automatic_merge",
        }:
            continue

        key = str(unit.get("key") or "")
        page_id = str(unit_pages.get(key) or "")
        if not page_id or page_id not in order_index:
            continue

        doubtful = (
            bool(unit.get("ask_user"))
            or decision == "ask"
        )
        label = str(
            unit.get("editorial_label")
            or unit.get("title")
            or "Division du livre"
        ).strip()

        if doubtful:
            title = "Structure à confirmer"
            message = (
                "TomeLinea a repéré ici une rupture importante, "
                "mais il n'est pas assez sûr pour décider seul "
                "comment la classer."
            )
            priority = 0
        else:
            title = label
            message = (
                "TomeLinea s'est servi de cet élément pour "
                f"construire la structure du livre : {label}."
            )
            priority = 1

        marker = SurvolMarker(
            marker_id=f"structure:{key}",
            page_id=page_id,
            kind="structure",
            family=_structure_family(unit),
            title=title,
            message=message,
            priority=priority,
            doubtful=doubtful,
            unit_key=(key or None),
            metadata={
                "unit": dict(unit),
            },
        )
        by_page.setdefault(
            page_id,
            [],
        ).append(marker)

    for page_id in order:
        if page_id in covers:
            continue

        page = getattr(
            book,
            "pages",
            {},
        ).get(page_id)

        if page is None:
            continue

        for index, element in enumerate(
            list(
                getattr(
                    page,
                    "content",
                    (),
                )
                or ()
            )
        ):
            if not isinstance(element, dict):
                continue

            kind = str(
                element.get("kind")
                or ""
            ).strip().lower()

            element_id = str(
                element.get("id")
                or index
            )

            if kind == "image":
                family, title = _image_family(
                    element,
                    book,
                )
                marker = SurvolMarker(
                    marker_id=(
                        f"content:{page_id}:"
                        f"{element_id}:image"
                    ),
                    page_id=page_id,
                    kind="image",
                    family=family,
                    title=title,
                    message=(
                        "Cette image fait partie des éléments "
                        "visuels que TomeLinea doit avoir vus "
                        "pendant le Survol."
                    ),
                    priority=(
                        2
                        if family.endswith(
                            "full_page"
                        )
                        else 3
                    ),
                    metadata={
                        "element_id": element_id,
                    },
                )
                by_page.setdefault(
                    page_id,
                    [],
                ).append(marker)

            elif kind in {
                "document",
                "embedded_document",
                "object",
            }:
                marker = SurvolMarker(
                    marker_id=(
                        f"content:{page_id}:"
                        f"{element_id}:document"
                    ),
                    page_id=page_id,
                    kind="document",
                    family="document",
                    title="Document inséré",
                    message=(
                        "Ce document inséré est un repère visuel "
                        "du livre et doit être vu pendant le Survol."
                    ),
                    priority=4,
                    metadata={
                        "element_id": element_id,
                    },
                )
                by_page.setdefault(
                    page_id,
                    [],
                ).append(marker)

            elif kind in {
                "table",
                "table_structure",
            }:
                marker = SurvolMarker(
                    marker_id=(
                        f"content:{page_id}:"
                        f"{element_id}:table"
                    ),
                    page_id=page_id,
                    kind="table",
                    family="table",
                    title="Tableau",
                    message=(
                        "Ce tableau crée une rupture de composition "
                        "que TomeLinea doit montrer pendant le Survol."
                    ),
                    priority=5,
                    metadata={
                        "element_id": element_id,
                    },
                )
                by_page.setdefault(
                    page_id,
                    [],
                ).append(marker)

    for markers in by_page.values():
        markers.sort(
            key=lambda marker: (
                marker.priority,
                marker.marker_id,
            )
        )

    return by_page


def future_similar_markers(
    markers_by_page: dict[str, list[SurvolMarker]],
    page_order: Iterable[str],
    marker: SurvolMarker,
    *,
    after_page_id: str,
    reviewed_marker_ids: Iterable[str] = (),
    excluded_page_ids: Iterable[str] = (),
) -> list[SurvolMarker]:
    """Retourne les cas similaires situés plus loin dans le Livre."""

    order = [
        str(page_id)
        for page_id in page_order
    ]

    try:
        start = (
            order.index(
                str(after_page_id)
            )
            + 1
        )
    except ValueError:
        start = 0

    reviewed = {
        str(value)
        for value in reviewed_marker_ids
    }
    excluded = {
        str(value)
        for value in excluded_page_ids
    }

    result: list[SurvolMarker] = []

    for page_id in order[start:]:
        if page_id in excluded:
            continue

        for candidate in markers_by_page.get(
            page_id,
            (),
        ):
            if (
                candidate.marker_id
                in reviewed
            ):
                continue

            if (
                candidate.family
                == marker.family
            ):
                result.append(
                    candidate
                )

    return result

# ==============================================================
# Phase 2.39E — état fiable et décision de parcours testable
# ==============================================================

SURVOL_STATE_SCHEMA = "tomelinea.survol.v2"


def normalize_survol_state(raw: dict[str, Any] | None) -> dict[str, Any]:
    """Normalise l'état persistant du Survol.

    Les états antérieurs à v2 utilisaient des règles trop larges et pouvaient
    mémoriser des repères comme déjà parcourus alors qu'ils devaient encore
    provoquer un arrêt. À la migration on conserve seulement la position de
    lecture ; règles et repères consommés repartent propres.
    """

    source = raw if isinstance(raw, dict) else {}
    schema = str(source.get("schema") or "")

    try:
        cursor = max(0, int(source.get("cursor", 0) or 0))
    except (TypeError, ValueError):
        cursor = 0

    if schema != SURVOL_STATE_SCHEMA:
        return {
            "schema": SURVOL_STATE_SCHEMA,
            "cursor": cursor,
            "reviewed_marker_ids": [],
            "rules": {},
            "completed": False,
        }

    reviewed = source.get("reviewed_marker_ids")
    if not isinstance(reviewed, list):
        reviewed = []

    rules = source.get("rules")
    if not isinstance(rules, dict):
        rules = {}

    return {
        "schema": SURVOL_STATE_SCHEMA,
        "cursor": cursor,
        "reviewed_marker_ids": [str(value) for value in reviewed if str(value)],
        "rules": {
            str(key): dict(value)
            for key, value in rules.items()
            if isinstance(value, dict)
        },
        "completed": bool(source.get("completed", False)),
    }


def evaluate_page_markers(
    markers: Iterable[SurvolMarker],
    reviewed_marker_ids: Iterable[str],
    rules: dict[str, dict[str, Any]] | None,
) -> tuple[SurvolMarker | None, dict[str, Any] | None, SurvolMarker | None, set[str]]:
    """Décide si une page doit arrêter le Survol.

    Une règle applicable au premier repère n'empêche jamais un second repère
    différent, présent sur la même page, de provoquer un arrêt.
    """

    reviewed = {str(value) for value in reviewed_marker_ids if str(value)}
    rule_map = rules if isinstance(rules, dict) else {}

    current_marker: SurvolMarker | None = None
    applied_rule: dict[str, Any] | None = None
    applied_rule_marker: SurvolMarker | None = None

    for marker in markers:
        if marker.marker_id in reviewed:
            continue

        raw_rule = rule_map.get(marker.family)
        rule = raw_rule if isinstance(raw_rule, dict) else None

        if rule is not None:
            excluded = {
                str(value)
                for value in list(rule.get("excluded_page_ids", []) or [])
            }
            if marker.page_id in excluded:
                rule = None

        if rule is not None:
            reviewed.add(marker.marker_id)
            if applied_rule is None:
                applied_rule = dict(rule)
                applied_rule_marker = marker
            continue

        current_marker = marker
        break

    return current_marker, applied_rule, applied_rule_marker, reviewed

