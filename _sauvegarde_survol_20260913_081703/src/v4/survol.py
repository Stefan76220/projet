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
    editorial_type = str(unit.get("editorial_type") or "unknown")
    if editorial_type != "unknown":
        return f"structure:{editorial_type}"

    style = _norm(unit.get("style_id")).replace(" ", "_")
    detected_by = _norm(unit.get("detected_by")).replace(" ", "_")
    signature = style or detected_by or "unknown"
    return f"structure:unknown:{signature}"


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
# Phase 2.39D — signature stricte des règles de Survol
# ==============================================================

def _structure_family(unit: dict[str, Any]) -> str:
    """Signature d'extension suffisamment précise pour éviter les faux groupes.

    Une décision sur un chapitre ne devient plus automatiquement la règle de
    toutes les divisions du même type. Le type, le niveau/style, la zone du
    livre et l'indice de détection doivent rester cohérents.
    """

    editorial_type = _norm(unit.get("editorial_type") or "unknown")
    style = _norm(unit.get("style_id") or "sans_style").replace(" ", "_")
    detected_by = _norm(unit.get("detected_by") or "inconnu").replace(" ", "_")
    zone = _norm(unit.get("zone") or "bodymatter").replace(" ", "_")

    # Une unité encore inconnue peut avoir un meilleur candidat sémantique.
    # On l'intègre à la signature sans prétendre qu'il s'agit déjà d'une
    # décision éditoriale validée.
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
