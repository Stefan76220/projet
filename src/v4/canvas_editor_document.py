from __future__ import annotations

"""TomeLinea V4 — Phase 2.5 : document logique Canvas Editor.

Canvas Editor possède des réglages de page en partie globaux (marges, colonnes,
header/footer) mais sait porter une direction de papier sur un saut de page.
TomeLinea garde donc UN document logique continu et prépare des segments de rendu
uniquement quand une propriété non sectionnable du moteur l'exige.

Ce module ne crée aucun WebView et ne lance aucun rendu.
"""

from copy import deepcopy
from dataclasses import dataclass
from typing import Any

from src.v4.canvas_editor_payload import PAYLOAD_SCHEMA

ENGINE_NAME = "tomelinea.canvas_editor_document"
ENGINE_VERSION = "1"
DOCUMENT_SCHEMA = "tomelinea-canvas-editor-document-plan"
DOCUMENT_SCHEMA_VERSION = 1


def _direction(section: dict[str, Any]) -> str:
    value = str(section.get("options", {}).get("paperDirection") or "vertical")
    return "horizontal" if value == "horizontal" else "vertical"


def _layout_signature(section: dict[str, Any]) -> dict[str, Any]:
    options = section.get("options", {})
    data = section.get("data", {})
    return {
        "width": options.get("width"),
        "height": options.get("height"),
        "margins": deepcopy(options.get("margins", [])),
        "column": deepcopy(options.get("column", {})),
        # Les en-têtes/pieds sont des données d'éditeur globales pour une instance.
        # On compare leur contenu, pas seulement leur présence.
        "header": deepcopy(data.get("header", [])),
        "footer": deepcopy(data.get("footer", [])),
    }


def _boundary_reasons(previous: dict[str, Any], following: dict[str, Any]) -> list[str]:
    before = _layout_signature(previous)
    after = _layout_signature(following)
    reasons: list[str] = []

    # Le changement portrait/paysage peut être porté nativement par le pageBreak,
    # donc il ne force pas à lui seul un nouveau segment de rendu.
    if before["width"] != after["width"] or before["height"] != after["height"]:
        prev_dir = _direction(previous)
        next_dir = _direction(following)
        rotated_same_sheet = (
            prev_dir != next_dir
            and before["width"] == after["height"]
            and before["height"] == after["width"]
        )
        if not rotated_same_sheet:
            reasons.append("paper_size")

    if before["margins"] != after["margins"]:
        reasons.append("margins")
    if before["column"] != after["column"]:
        reasons.append("columns")
    if before["header"] != after["header"]:
        reasons.append("header")
    if before["footer"] != after["footer"]:
        reasons.append("footer")

    return reasons


def _section_break_element(section: dict[str, Any], following: dict[str, Any]) -> dict[str, Any]:
    """Saut de section logique, représentable comme pageBreak Canvas Editor.

    paperDirection est une propriété officiellement portée par les éléments
    pageBreak du moteur. Les autres propriétés restent dans extension.tomelinea
    et servent au host TL pour sélectionner le segment de rendu suivant.
    """
    return {
        "type": "pageBreak",
        # Canvas Editor attend WRAP ("\n") pour effectuer réellement le saut.
        "value": "\n",
        "paperDirection": _direction(following),
        "extension": {
            "tomelinea": {
                "kind": "sectionBreak",
                "fromSection": section.get("section"),
                "toSection": following.get("section"),
                "sourceBreakType": following.get("source", {}).get("section_break_type"),
                "nextSectionOptions": deepcopy(following.get("options", {})),
            }
        },
    }


def _segment_sections(sections: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    if not sections:
        return [], []

    boundaries: list[dict[str, Any]] = []
    groups: list[list[dict[str, Any]]] = [[sections[0]]]

    for previous, following in zip(sections, sections[1:]):
        reasons = _boundary_reasons(previous, following)
        boundary = {
            "from_section": previous.get("section"),
            "to_section": following.get("section"),
            "paper_direction": _direction(following),
            "native_page_break": True,
            "requires_new_render_segment": bool(reasons),
            "segment_reasons": reasons,
        }
        boundaries.append(boundary)
        if reasons:
            groups.append([following])
        else:
            groups[-1].append(following)

    segments: list[dict[str, Any]] = []
    for index, group in enumerate(groups, start=1):
        first = group[0]
        last = group[-1]
        main: list[dict[str, Any]] = []
        for group_index, section in enumerate(group):
            if group_index:
                main.append(_section_break_element(group[group_index - 1], section))
            main.extend(deepcopy(section.get("data", {}).get("main", [])))

        segments.append({
            "segment": index,
            "section_start": first.get("section"),
            "section_end": last.get("section"),
            "sections": [item.get("section") for item in group],
            "data": {
                "header": deepcopy(first.get("data", {}).get("header", [])),
                "main": main,
                "footer": deepcopy(first.get("data", {}).get("footer", [])),
            },
            "options": deepcopy(first.get("options", {})),
        })

    return boundaries, segments


@dataclass(frozen=True, slots=True)
class CanvasEditorDocumentResult:
    plan: dict[str, Any]
    valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def build_canvas_editor_document(payload: dict[str, Any]) -> CanvasEditorDocumentResult:
    if payload.get("schema") != PAYLOAD_SCHEMA:
        raise ValueError(f"Payload Canvas Editor inattendu : {payload.get('schema')!r}")
    if not payload.get("readiness", {}).get("payload_valid"):
        raise ValueError("Le payload Canvas Editor n'est pas valide.")

    sections = list(payload.get("sections", []))
    errors: list[str] = []
    warnings: list[str] = []

    if not sections:
        errors.append("aucune_section")

    logical_main: list[dict[str, Any]] = []
    section_breaks = 0
    source_page_breaks = 0

    for index, section in enumerate(sections):
        main = deepcopy(section.get("data", {}).get("main", []))
        source_page_breaks += sum(1 for item in main if item.get("type") == "pageBreak")
        logical_main.extend(main)
        if index + 1 < len(sections):
            logical_main.append(_section_break_element(section, sections[index + 1]))
            section_breaks += 1

    boundaries, segments = _segment_sections(sections)

    # Chaque section source doit être couverte exactement une fois par le plan.
    planned_sections = [section for segment in segments for section in segment.get("sections", [])]
    expected_sections = [section.get("section") for section in sections]
    if planned_sections != expected_sections:
        errors.append("couverture_sections_invalide")

    # Un saut de section est nécessaire entre chaque section Word successive.
    expected_section_breaks = max(0, len(sections) - 1)
    if section_breaks != expected_section_breaks:
        errors.append("nombre_sauts_section_invalide")

    # Le document reste logique et continu même si le host doit utiliser plusieurs
    # instances cachées pour respecter les options globales non sectionnables.
    if len(segments) > 1:
        warnings.append("render_segments_required")

    plan = {
        "schema": DOCUMENT_SCHEMA,
        "schema_version": DOCUMENT_SCHEMA_VERSION,
        "engine": {"name": ENGINE_NAME, "version": ENGINE_VERSION},
        "target": deepcopy(payload.get("target", {})),
        "source": deepcopy(payload.get("source", {})),
        "logical_document": {
            "continuous": True,
            "main": logical_main,
            "section_count": len(sections),
            "source_page_break_count": source_page_breaks,
            "section_break_count": section_breaks,
            "total_page_break_elements": source_page_breaks + section_breaks,
        },
        "boundaries": boundaries,
        "render_segments": segments,
        "render_strategy": {
            "one_logical_document": True,
            "segment_count": len(segments),
            "segments_hidden_until_ready": True,
            "global_navigation_after_pagination": True,
            "pagination_owner": "canvas-editor",
            "line_break_owner": "canvas-editor",
            "manual_line_coordinates": False,
        },
        "translated_counts": deepcopy(payload.get("translated_counts", {})),
        "preserved_metadata": deepcopy(payload.get("preserved_metadata", {})),
        "deferred_visual_properties": deepcopy(payload.get("deferred_visual_properties", {})),
        "readiness": {
            "document_plan_valid": not errors,
            "webview_created": False,
            "editor_created": False,
            "render_started": False,
            "errors": list(errors),
            "warnings": list(warnings),
        },
    }

    return CanvasEditorDocumentResult(
        plan=plan,
        valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
