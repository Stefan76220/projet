from __future__ import annotations

"""TomeLinea V4 — Phase 2.2 : contrat d'entrée du moteur Canvas.

Ce module traduit le document interne Phase 2 vers un contrat de rendu
explicite. Il ne crée aucun widget, ne calcule aucune pagination et ne fabrique
aucune coordonnée de ligne. Le moteur Canvas reste seul responsable de la mise
en page finale.
"""

from copy import deepcopy
from dataclasses import dataclass
from hashlib import sha256
from typing import Any
import json

PHASE2_SCHEMA = "tomelinea-internal-document-phase2"
CANVAS_SCHEMA = "tomelinea-canvas-input"
CANVAS_SCHEMA_VERSION = 1
ENGINE_NAME = "tomelinea.canvas_contract"
ENGINE_VERSION = "1"


def _json_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(raw.encode("utf-8")).hexdigest()


def _style_key(*, bold: bool = False, italic: bool = False) -> str:
    if bold and italic:
        return "bold_italic"
    if bold:
        return "bold"
    if italic:
        return "italic"
    return "regular"


def _alignment(value: Any) -> str | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    return {
        "both": "justify",
        "distribute": "justify_distributed",
        "start": "left",
        "end": "right",
    }.get(raw, raw)


def _first_number(*values: Any) -> float | int | None:
    for value in values:
        if isinstance(value, (int, float)):
            return value
    return None


def _font_index(model: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    result: dict[tuple[str, str], dict[str, Any]] = {}
    for item in model.get("fonts", {}).get("resolution", []):
        family = str(item.get("family") or "").strip().casefold()
        style = str(item.get("style") or "regular").strip().casefold()
        if family:
            result[(family, style)] = item
    return result


def _run_contract(
    run: dict[str, Any],
    *,
    source_paragraph: int,
    font_index: dict[tuple[str, str], dict[str, Any]],
    images_by_run: dict[tuple[int, int], list[dict[str, Any]]],
) -> dict[str, Any]:
    effective = deepcopy(run.get("effective", {}))
    direct = deepcopy(run.get("direct", {}))
    bold = bool(effective.get("bold", False))
    italic = bool(effective.get("italic", False))
    style = _style_key(bold=bold, italic=italic)

    fonts = effective.get("fonts", {}) if isinstance(effective.get("fonts"), dict) else {}
    family = str(
        effective.get("resolved_font_family")
        or fonts.get("ascii")
        or fonts.get("hansi")
        or ""
    ).strip()
    resolved = font_index.get((family.casefold(), style), {})

    size_pt = _first_number(effective.get("size_pt"), direct.get("size_pt"))
    color = effective.get("color")
    if isinstance(color, dict):
        color_value = color.get("value") or color.get("theme")
    else:
        color_value = color

    run_index = int(run.get("run") or 0)
    return {
        "source_run": run_index,
        "text": str(run.get("text") or ""),
        "character_format": {
            "font_family": (resolved.get("resolved_family") or family) or None,
            "font_style": style,
            "font_path": resolved.get("path"),
            "font_origin": resolved.get("origin"),
            "size_pt": size_pt,
            "bold": bold,
            "italic": italic,
            "underline": effective.get("underline"),
            "color": color_value,
            "language": deepcopy(effective.get("language", {})),
        },
        "controls": deepcopy(run.get("controls", [])),
        "images": deepcopy(images_by_run.get((source_paragraph, run_index), [])),
        "source_trace": {
            "direct": direct,
            "effective": effective,
        },
    }


def _paragraph_contract(
    block: dict[str, Any],
    *,
    font_index: dict[tuple[str, str], dict[str, Any]],
    images_by_run: dict[tuple[int, int], list[dict[str, Any]]],
) -> dict[str, Any]:
    source_paragraph = int(block.get("source_paragraph") or 0)
    effective = deepcopy(block.get("effective", {}))
    direct = deepcopy(block.get("direct", {}))
    spacing = effective.get("spacing", {}) if isinstance(effective.get("spacing"), dict) else {}
    indent = effective.get("indent", {}) if isinstance(effective.get("indent"), dict) else {}

    if spacing.get("line_multiple") is not None:
        line_spacing = {"mode": "multiple", "value": spacing.get("line_multiple")}
    elif spacing.get("line_pt") is not None:
        line_spacing = {
            "mode": spacing.get("line_rule") or "exact",
            "value_pt": spacing.get("line_pt"),
        }
    else:
        line_spacing = {"mode": "inherit"}

    runs = [
        _run_contract(
            run,
            source_paragraph=source_paragraph,
            font_index=font_index,
            images_by_run=images_by_run,
        )
        for run in block.get("runs", [])
    ]

    return {
        "id": f"p:{source_paragraph}",
        "kind": "paragraph",
        "source_paragraph": source_paragraph,
        "text": str(block.get("text") or ""),
        "style_chain": deepcopy(block.get("style_chain", [])),
        "paragraph_format": {
            "style_id": effective.get("style_id") or direct.get("style_id"),
            "alignment": _alignment(effective.get("alignment")),
            "spacing_before_pt": spacing.get("before_pt"),
            "spacing_after_pt": spacing.get("after_pt"),
            "line_spacing": line_spacing,
            "indent_left_mm": indent.get("left_mm"),
            "indent_right_mm": indent.get("right_mm"),
            "first_line_mm": indent.get("first_line_mm"),
            "hanging_mm": indent.get("hanging_mm"),
            "keep_next": effective.get("keep_next"),
            "keep_lines": effective.get("keep_lines"),
            "page_break_before": effective.get("page_break_before"),
            "widow_control": effective.get("widow_control"),
            "contextual_spacing": effective.get("contextual_spacing"),
            "tabs": deepcopy(effective.get("tabs", direct.get("tabs", []))),
            "numbering": deepcopy(effective.get("numbering")),
        },
        "runs": runs,
        "source_trace": {
            "direct": direct,
            "effective": effective,
        },
    }


def _table_contract(block: dict[str, Any]) -> dict[str, Any]:
    source_table = int(block.get("source_table") or 0)
    table = deepcopy(block.get("table", {}))
    return {
        "id": f"t:{source_table}",
        "kind": "table",
        "source_table": source_table,
        "table_format": {
            "style_id": table.get("style_id"),
            "alignment": table.get("alignment"),
            "width_type": table.get("width_type"),
            "width_raw": table.get("width_raw"),
            "look": deepcopy(table.get("look", {})),
            "grid": deepcopy(table.get("grid", [])),
        },
        "rows": deepcopy(table.get("rows", [])),
        "source_trace": table,
    }


def _section_contract(section: dict[str, Any]) -> dict[str, Any]:
    page = section.get("page", {})
    margins = section.get("margins", {})
    columns = section.get("columns", {})
    return {
        "section": section.get("section"),
        "paragraph_range": {
            "start": section.get("start_paragraph"),
            "end": section.get("end_paragraph"),
        },
        "page_setup": {
            "width_mm": page.get("width_mm"),
            "height_mm": page.get("height_mm"),
            "orientation": page.get("orientation"),
            "margins_mm": {
                "top": margins.get("top_mm"),
                "right": margins.get("right_mm"),
                "bottom": margins.get("bottom_mm"),
                "left": margins.get("left_mm"),
                "header": margins.get("header_mm"),
                "footer": margins.get("footer_mm"),
                "gutter": margins.get("gutter_mm"),
            },
            "columns": {
                "count": columns.get("count", 1),
                "gap_mm": columns.get("space_mm"),
            },
            "document_grid": deepcopy(section.get("document_grid", {})),
        },
        "section_break_type": section.get("section_break_type"),
        "header_footer_references": deepcopy(section.get("header_footer_references", [])),
        "source_trace": deepcopy(section),
    }


@dataclass(frozen=True, slots=True)
class CanvasContractResult:
    contract: dict[str, Any]
    valid: bool
    errors: tuple[str, ...]


def build_canvas_contract(phase2_model: dict[str, Any]) -> CanvasContractResult:
    if phase2_model.get("schema") != PHASE2_SCHEMA:
        raise ValueError(f"Schéma Phase 2 inattendu : {phase2_model.get('schema')!r}")
    readiness = phase2_model.get("readiness", {})
    if not readiness.get("ready_for_canvas"):
        raise ValueError("Le modèle Phase 2 n'est pas prêt pour Canvas.")
    if readiness.get("canvas_created"):
        raise ValueError("Le modèle fourni indique qu'un Canvas a déjà été créé.")

    font_index = _font_index(phase2_model)
    images = phase2_model.get("resources", {}).get("images", [])
    images_by_run: dict[tuple[int, int], list[dict[str, Any]]] = {}
    for image in images:
        key = (int(image.get("paragraph_index") or 0), int(image.get("run_index") or 0))
        images_by_run.setdefault(key, []).append(deepcopy(image))

    content: list[dict[str, Any]] = []
    errors: list[str] = []
    paragraph_count = 0
    table_count = 0
    run_count = 0
    attached_image_count = 0

    for block in phase2_model.get("flow", []):
        kind = block.get("kind")
        if kind == "paragraph":
            translated = _paragraph_contract(
                block,
                font_index=font_index,
                images_by_run=images_by_run,
            )
            paragraph_count += 1
            run_count += len(translated["runs"])
            attached_image_count += sum(len(run["images"]) for run in translated["runs"])
            content.append(translated)
        elif kind == "table":
            content.append(_table_contract(block))
            table_count += 1
        else:
            errors.append(f"Bloc non traduisible vers Canvas : {kind!r}")

    sections = [_section_contract(item) for item in phase2_model.get("sections", [])]
    resources = phase2_model.get("resources", {})

    expected = phase2_model.get("counts", {})
    if paragraph_count != int(expected.get("paragraph_blocks", paragraph_count)):
        errors.append("Nombre de paragraphes différent entre Phase 2 et contrat Canvas.")
    if table_count != int(expected.get("table_blocks", table_count)):
        errors.append("Nombre de tableaux différent entre Phase 2 et contrat Canvas.")
    if len(sections) != int(expected.get("sections", len(sections))):
        errors.append("Nombre de sections différent entre Phase 2 et contrat Canvas.")
    if attached_image_count != len(images):
        errors.append(
            f"Images rattachées aux runs : {attached_image_count}; images source : {len(images)}."
        )

    for item in phase2_model.get("fonts", {}).get("resolution", []):
        if item.get("status") not in {"exact", "substituted"} or not item.get("path"):
            errors.append(
                f"Police non résolue : {item.get('family')} / {item.get('style')}."
            )

    annotations = {
        "hyperlinks": deepcopy(resources.get("hyperlinks", [])),
        "bookmarks": deepcopy(resources.get("bookmarks", [])),
        "content_controls": deepcopy(resources.get("content_controls", [])),
        "tracked_changes": deepcopy(resources.get("tracked_changes", {})),
        "tracked_change_ranges": deepcopy(resources.get("tracked_change_ranges", [])),
        "footnotes": deepcopy(resources.get("footnotes", [])),
        "endnotes": deepcopy(resources.get("endnotes", [])),
        "comments": deepcopy(resources.get("comments", [])),
        "headers_footers": deepcopy(resources.get("headers_footers", [])),
    }

    coverage = {
        "sections": len(sections),
        "paragraphs": paragraph_count,
        "runs": run_count,
        "tables": table_count,
        "images": attached_image_count,
        "hyperlinks": len(annotations["hyperlinks"]),
        "bookmarks": len(annotations["bookmarks"]),
        "content_controls": len(annotations["content_controls"]),
        "tracked_change_ranges": len(annotations["tracked_change_ranges"]),
        "footnotes": len(annotations["footnotes"]),
        "comments": len(annotations["comments"]),
        "headers_footers": len(annotations["headers_footers"]),
    }

    contract = {
        "schema": CANVAS_SCHEMA,
        "schema_version": CANVAS_SCHEMA_VERSION,
        "engine": {"name": ENGINE_NAME, "version": ENGINE_VERSION},
        "source": deepcopy(phase2_model.get("source", {})),
        "phase2_model_sha256": _json_hash(phase2_model),
        "layout_policy": {
            "canvas_owns_line_breaking": True,
            "canvas_owns_pagination": True,
            "manual_line_coordinates": False,
            "precomputed_page_count": False,
            "preserve_explicit_page_breaks": True,
            "preserve_section_breaks": True,
            "show_composition_only_after": [
                "fonts_loaded",
                "layout_complete",
                "pagination_stable",
                "render_complete",
            ],
        },
        "sections": sections,
        "content": content,
        "annotations": annotations,
        "coverage": coverage,
        "readiness": {
            "valid_contract": not errors,
            "canvas_created": False,
            "layout_started": False,
            "pagination_started": False,
            "composition_visible": False,
            "errors": list(errors),
        },
    }
    return CanvasContractResult(contract=contract, valid=not errors, errors=tuple(errors))
