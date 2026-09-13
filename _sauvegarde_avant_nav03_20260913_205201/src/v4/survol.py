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


def _bucket_ratio(value: float | None, total: float | None, *, step: float = 0.05) -> str:
    if value is None or not total:
        return "na"
    ratio = max(0.0, min(2.0, float(value) / float(total)))
    bucket = round(ratio / step) * step
    return f"{bucket:.2f}"


def _image_family(element: dict[str, Any], book) -> tuple[str, str]:
    """Signature de construction, pas seulement « image intégrée ».

    Deux images ne deviennent similaires que si leur emprise et leur position
    sont proches. Cela évite qu'une décision de placement prise sur une petite
    illustration s'étende à toutes les images du livre.
    """

    geometry = element.get("geometry")
    if not isinstance(geometry, dict):
        geometry = {}

    width = _geometry_value(geometry, "width_mm", "w_mm", "width", "w")
    height = _geometry_value(geometry, "height_mm", "h_mm", "height", "h")
    x = _geometry_value(geometry, "x_mm", "left_mm", "x", "left")
    y = _geometry_value(geometry, "y_mm", "top_mm", "y", "top")

    fmt = getattr(book, "format", None)
    page_width = _number(getattr(fmt, "width_mm", None))
    page_height = _number(getattr(fmt, "height_mm", None))

    full_page = bool(
        width is not None
        and height is not None
        and page_width
        and page_height
        and width >= page_width * 0.82
        and height >= page_height * 0.82
    )
    kind = "full_page" if full_page else "integrated"
    title = "Image pleine page" if full_page else "Image intégrée"

    family = (
        f"image:{kind}:"
        f"x{_bucket_ratio(x, page_width)}:"
        f"y{_bucket_ratio(y, page_height)}:"
        f"w{_bucket_ratio(width, page_width)}:"
        f"h{_bucket_ratio(height, page_height)}"
    )
    return family, title


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
                "semantic_family": _structure_semantic_family(unit),
                "presentation_family": _structure_presentation_family(unit),
                "similarity_reason": _structure_similarity_reason(unit),
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
                        "presentation_family": family,
                        "similarity_reason": (
                            "même type d'image, emprise et position proches sur la page"
                        ),
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

def _structure_semantic_family(unit: dict[str, Any]) -> str:
    editorial_type = _norm(unit.get("editorial_type") or "unknown")
    candidate = "aucun"
    candidates = unit.get("candidates")
    if isinstance(candidates, list) and candidates and isinstance(candidates[0], dict):
        candidate = _norm(candidates[0].get("type") or "aucun")
    return f"semantic:{editorial_type}:{candidate}"


def _structure_presentation_family(unit: dict[str, Any]) -> str:
    """Famille visuelle indépendante du rôle éditorial.

    Glossaire, index et remerciements peuvent donc partager une présentation
    sans que TomeLinea prétende qu'ils ont le même sens.
    """

    style = _norm(unit.get("style_id") or "sans_style").replace(" ", "_")
    detected_by = _norm(unit.get("detected_by") or "inconnu").replace(" ", "_")
    zone = _norm(unit.get("zone") or "bodymatter").replace(" ", "_")
    return f"presentation:{style}:{detected_by}:{zone}"


def _structure_similarity_reason(unit: dict[str, Any]) -> str:
    style = str(unit.get("style_id") or "").strip()
    detected_by = str(unit.get("detected_by") or "").strip()
    zone = str(unit.get("zone") or "").strip()

    parts = []
    if style:
        parts.append(f"même style source « {style} »")
    if detected_by:
        parts.append("même manière de marquer la rupture")
    if zone:
        parts.append("même zone générale du livre")

    return ", ".join(parts) if parts else "même construction de rupture"


def _structure_family(unit: dict[str, Any]) -> str:
    """Famille d'extension d'une décision de *division*.

    La portée est fondée sur la construction de la rupture et non sur son nom
    éditorial. Valider qu'une rupture existe peut donc s'étendre à un Index et
    à des Remerciements construits de la même façon, sans confondre leur rôle.
    Le sens éditorial reste conservé dans ``semantic_family``.
    """

    return "boundary:" + _structure_presentation_family(unit).removeprefix("presentation:")

def marker_fingerprint(marker: SurvolMarker) -> str:
    """Empreinte stable de ce qui rend un repère éditorialement significatif.

    Elle sert au Survol vivant : si un élément déjà vu conserve son identifiant
    mais change réellement de construction ou de rôle, TomeLinea peut le remettre
    dans la petite file « À revoir » au lieu de considérer l'ancien avis comme
    toujours valable.
    """

    metadata = marker.metadata if isinstance(marker.metadata, dict) else {}
    semantic = str(metadata.get("semantic_family") or "")
    presentation = str(metadata.get("presentation_family") or "")
    element_id = str(metadata.get("element_id") or "")
    return "|".join((
        str(marker.kind or ""),
        str(marker.family or ""),
        "1" if bool(marker.doubtful) else "0",
        str(marker.unit_key or ""),
        semantic,
        presentation,
        element_id,
    ))


# ==============================================================
# Phase 2.40A — état vivant du Survol
# ==============================================================

SURVOL_STATE_SCHEMA = "tomelinea.survol.v4"


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
        # 2.39F : les parcours v1/v2 peuvent avoir été calculés avant la
        # pagination finale (ex. 26/26 pour un Livre final de 53 pages) et
        # leurs repères pouvaient être absents du cache. Leur curseur n'est
        # donc pas fiable. Les décisions éditoriales elles-mêmes restent
        # enregistrées ailleurs dans le projet ; seul l'état de Survol repart
        # proprement de la première vraie page.
        return {
            "schema": SURVOL_STATE_SCHEMA,
            "cursor": 0,
            "reviewed_marker_ids": [],
            "rules": {},
            "completed": False,
            "review_mode": "full",
            "targeted_marker_ids": [],
            "reviewed_marker_fingerprints": {},
        }

    reviewed = source.get("reviewed_marker_ids")
    if not isinstance(reviewed, list):
        reviewed = []

    rules = source.get("rules")
    if not isinstance(rules, dict):
        rules = {}

    targeted = source.get("targeted_marker_ids")
    if not isinstance(targeted, list):
        targeted = []
    mode = str(source.get("review_mode") or "full").strip().lower()
    if mode not in {"full", "targeted"}:
        mode = "full"

    fingerprints = source.get("reviewed_marker_fingerprints")
    if not isinstance(fingerprints, dict):
        fingerprints = {}

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
        "review_mode": mode,
        "targeted_marker_ids": [str(value) for value in targeted if str(value)],
        "reviewed_marker_fingerprints": {
            str(key): str(value)
            for key, value in fingerprints.items()
            if str(key) and str(value)
        },
    }


def evaluate_page_markers(
    markers: Iterable[SurvolMarker],
    reviewed_marker_ids: Iterable[str],
    rules: dict[str, dict[str, Any]] | None,
) -> tuple[SurvolMarker | None, dict[str, Any] | None, SurvolMarker | None, set[str]]:
    """Décide si une page doit arrêter le Survol.

    Retourne :
    - le premier repère qui exige encore une décision ;
    - la première règle déjà applicable sur cette page ;
    - le repère auquel cette règle s'applique ;
    - l'ensemble mis à jour des repères déjà consommés par une règle.

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
