from __future__ import annotations

"""Règles générales du Livre appliquées aux plans Canvas.

Cette couche ne simule pas un traitement de texte. Elle n'invente ni TAB,
ni ligne vide, ni coordonnées pour reproduire Word. Elle applique uniquement
les propriétés que Canvas Editor sait porter proprement et conserve le reste
comme règles TomeLinea à appliquer/contrôler par le moteur de composition.
"""

from collections import Counter
from typing import Any

PX_PER_MM = 96.0 / 25.4
PX_PER_PT = 96.0 / 72.0


def _tl(element: dict[str, Any]) -> dict[str, Any]:
    ext = element.get("extension")
    if not isinstance(ext, dict):
        return {}
    value = ext.get("tomelinea")
    return value if isinstance(value, dict) else {}


def _paragraph_info(element: dict[str, Any]) -> tuple[str | None, str | None]:
    tl = _tl(element)
    paragraph = tl.get("paragraph") if isinstance(tl.get("paragraph"), dict) else {}
    fmt = paragraph.get("format") if isinstance(paragraph.get("format"), dict) else {}
    pid = paragraph.get("id")
    style = fmt.get("style_id")
    if pid is None and tl.get("paragraphEnd") is not None:
        pid = f"p:{tl.get('paragraphEnd')}"
        end_fmt = tl.get("format") if isinstance(tl.get("format"), dict) else {}
        style = end_fmt.get("style_id")
    return (
        str(pid) if pid is not None else None,
        str(style) if style is not None else None,
    )


def _is_heading_style(style_id: str | None) -> bool:
    value = " ".join(str(style_id or "").replace("_", " ").replace("-", " ").casefold().split())
    compact = value.replace(" ", "")
    if compact in {
        "heading1", "heading2", "heading3", "heading4", "heading5", "heading6",
        "titre1", "titre2", "titre3", "titre4", "titre5", "titre6",
    }:
        return True
    return any(token in value for token in ("heading", "titre", "chapitre", "chapter", "title"))


def _body_paragraph_ids(main: list[dict[str, Any]]) -> set[str]:
    result: set[str] = set()
    for item in main:
        if not isinstance(item, dict):
            continue
        pid, style = _paragraph_info(item)
        if not pid or _is_heading_style(style):
            continue
        typ = str(item.get("type") or "").casefold()
        if typ in {"image", "table", "pagebreak", "list"}:
            continue
        value = str(item.get("value") or "")
        if value and value != "\n":
            result.add(pid)
    return result


def _number(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def normalize_general_text_rules(rules: dict[str, Any]) -> dict[str, Any]:
    font = str(rules.get("font_family") or "Arial").strip() or "Arial"
    size_pt = max(6.0, min(72.0, _number(rules.get("font_size_pt"), 11.0)))
    alignment = str(rules.get("alignment") or "justify").casefold()
    if alignment not in {"justify", "left"}:
        alignment = "justify"
    first_indent = max(0.0, min(30.0, _number(rules.get("first_line_indent_mm"), 0.0)))
    line_multiple = max(0.8, min(3.0, _number(rules.get("line_spacing_multiple"), 1.15)))
    gap_mm = max(0.0, min(20.0, _number(rules.get("paragraph_gap_mm"), 0.0)))
    hyphenation = str(rules.get("hyphenation") or "forbid").casefold()
    if hyphenation not in {"forbid", "controlled"}:
        hyphenation = "forbid"
    return {
        "font_family": font,
        "font_size_pt": round(size_pt, 2),
        "alignment": alignment,
        "first_line_indent_mm": round(first_indent, 2),
        "line_spacing_multiple": round(line_multiple, 2),
        "line_pitch_mm": round(size_pt * 25.4 / 72.0 * line_multiple, 2),
        "paragraph_gap_mm": round(gap_mm, 2),
        "hyphenation": hyphenation,
        "confirmed": bool(rules.get("confirmed", True)),
    }


def apply_rules_to_plan(plan: dict[str, Any], rules: dict[str, Any]) -> dict[str, int]:
    """Applique seulement les propriétés sûres supportées par Canvas.

    Le retrait de première ligne, l'espace après paragraphe, la césure et le
    multiplicateur d'interligne sont conservés dans ``tomelinea_rules``. Ils ne
    sont jamais simulés par des caractères artificiels.
    """
    normalized = normalize_general_text_rules(rules)
    changed_elements = 0
    changed_paragraphs: set[str] = set()
    size_px = normalized["font_size_pt"] * PX_PER_PT
    row_flex = "alignment" if normalized["alignment"] == "justify" else "left"

    plan["tomelinea_rules"] = {
        "general_text": dict(normalized),
        "deferred_to_composition_engine": [
            "first_line_indent_mm",
            "line_spacing_multiple",
            "paragraph_gap_mm",
            "hyphenation",
        ],
    }

    for segment in list(plan.get("render_segments") or []):
        if not isinstance(segment, dict):
            continue
        data = segment.get("data")
        main = data.get("main") if isinstance(data, dict) else None
        if not isinstance(main, list):
            continue
        body_ids = _body_paragraph_ids(main)
        for item in main:
            if not isinstance(item, dict):
                continue
            pid, style = _paragraph_info(item)
            if not pid or pid not in body_ids or _is_heading_style(style):
                continue
            typ = str(item.get("type") or "").casefold()
            if typ in {"image", "table", "pagebreak", "tab", "list"}:
                continue
            value = str(item.get("value") or "")
            if not value or value == "\n":
                continue
            item["font"] = normalized["font_family"]
            item["size"] = size_px
            item["rowFlex"] = row_flex
            # Ne pas écrire rowMargin ici : sa sémantique Canvas n'est pas le
            # multiplicateur éditorial de l'interligne.
            changed_elements += 1
            changed_paragraphs.add(pid)

    return {"paragraphs": len(changed_paragraphs), "elements": changed_elements}


def infer_rules_from_plans(plans: list[dict[str, Any]]) -> dict[str, Any]:
    """Propose des valeurs à partir des métadonnées Source, sans les imposer."""
    fonts: Counter[str] = Counter()
    sizes: Counter[float] = Counter()
    source_line: list[float] = []
    first_indents: list[float] = []
    gaps: list[float] = []
    aligns: Counter[str] = Counter()

    for plan in plans:
        for segment in list(plan.get("render_segments") or []):
            data = segment.get("data") if isinstance(segment, dict) else None
            main = data.get("main") if isinstance(data, dict) else None
            if not isinstance(main, list):
                continue
            body_ids = _body_paragraph_ids(main)
            for item in main:
                if not isinstance(item, dict):
                    continue
                pid, style = _paragraph_info(item)
                if not pid or pid not in body_ids or _is_heading_style(style):
                    continue
                value = str(item.get("value") or "")
                tl = _tl(item)
                paragraph = tl.get("paragraph") if isinstance(tl.get("paragraph"), dict) else {}
                fmt = paragraph.get("format") if isinstance(paragraph.get("format"), dict) else {}
                char = tl.get("sourceCharacterFormat") if isinstance(tl.get("sourceCharacterFormat"), dict) else {}
                if value and value != "\n":
                    source_family = str(char.get("font_family") or tl.get("sourceFontFamily") or "").strip()
                    if source_family:
                        fonts[source_family] += max(1, len(value))
                    try:
                        pt = float(char.get("size_pt"))
                        if pt > 0:
                            sizes[round(pt, 2)] += max(1, len(value))
                    except (TypeError, ValueError):
                        pass
                try:
                    line = fmt.get("line_spacing") if isinstance(fmt.get("line_spacing"), dict) else {}
                    if line.get("mode") == "multiple" and line.get("value") is not None:
                        source_line.append(float(line["value"]))
                except (TypeError, ValueError):
                    pass
                try:
                    if fmt.get("first_line_mm") is not None:
                        first_indents.append(float(fmt["first_line_mm"]))
                except (TypeError, ValueError):
                    pass
                try:
                    if fmt.get("spacing_after_pt") is not None:
                        gaps.append(float(fmt["spacing_after_pt"]) * 25.4 / 72.0)
                except (TypeError, ValueError):
                    pass
                if item.get("rowFlex"):
                    aligns[str(item.get("rowFlex"))] += 1

    def median(values: list[float], default: float) -> float:
        values = sorted(values)
        return values[len(values) // 2] if values else default

    return normalize_general_text_rules({
        "font_family": fonts.most_common(1)[0][0] if fonts else "Arial",
        "font_size_pt": sizes.most_common(1)[0][0] if sizes else 11.0,
        "alignment": "left" if (aligns.most_common(1)[0][0] if aligns else "alignment") == "left" else "justify",
        "first_line_indent_mm": median(first_indents, 0.0),
        "line_spacing_multiple": median(source_line, 1.15),
        "paragraph_gap_mm": median(gaps, 0.0),
        "hyphenation": "forbid",
    })


def apply_layout_to_plan(
    plan: dict[str, Any],
    *,
    width_mm: float,
    height_mm: float,
    margin_top_mm: float,
    margin_bottom_mm: float,
    margin_inside_mm: float,
    margin_outside_mm: float,
) -> dict[str, int]:
    width_mm = float(width_mm)
    height_mm = float(height_mm)
    top = float(margin_top_mm)
    bottom = float(margin_bottom_mm)
    inside = float(margin_inside_mm)
    outside = float(margin_outside_mm)
    if width_mm <= 0 or height_mm <= 0:
        raise ValueError("Le format doit avoir des dimensions positives.")
    if min(top, bottom, inside, outside) < 0:
        raise ValueError("Les marges ne peuvent pas être négatives.")
    if inside + outside >= width_mm or top + bottom >= height_mm:
        raise ValueError("Les marges ne laissent aucune zone de composition utilisable.")

    width_px = width_mm * PX_PER_MM
    height_px = height_mm * PX_PER_MM
    direction = "horizontal" if width_mm > height_mm else "vertical"
    margins_px = [top * PX_PER_MM, outside * PX_PER_MM, bottom * PX_PER_MM, inside * PX_PER_MM]
    segments = 0
    page_breaks = 0

    for segment in list(plan.get("render_segments") or []):
        if not isinstance(segment, dict):
            continue
        options = segment.setdefault("options", {})
        if not isinstance(options, dict):
            options = {}
            segment["options"] = options
        options.update({
            "width": width_px,
            "height": height_px,
            "paperDirection": direction,
            "margins": list(margins_px),
        })
        segments += 1
        data = segment.get("data")
        main = data.get("main") if isinstance(data, dict) else None
        if not isinstance(main, list):
            continue
        for item in main:
            if not isinstance(item, dict) or str(item.get("type") or "").casefold() != "pagebreak":
                continue
            item["paperDirection"] = direction
            tl = _tl(item)
            next_options = tl.get("nextSectionOptions")
            if isinstance(next_options, dict):
                next_options.update({
                    "width": width_px,
                    "height": height_px,
                    "paperDirection": direction,
                    "margins": list(margins_px),
                })
            page_breaks += 1
    return {"segments": segments, "page_breaks": page_breaks}


def apply_global_settings_to_plans(
    plans: list[dict[str, Any]],
    *,
    width_mm: float,
    height_mm: float,
    margin_top_mm: float,
    margin_bottom_mm: float,
    margin_inside_mm: float,
    margin_outside_mm: float,
    text_rules: dict[str, Any],
) -> dict[str, int]:
    report = {"plans": 0, "segments": 0, "page_breaks": 0, "paragraphs": 0, "elements": 0}
    for plan in plans:
        if not isinstance(plan, dict):
            continue
        layout = apply_layout_to_plan(
            plan,
            width_mm=width_mm,
            height_mm=height_mm,
            margin_top_mm=margin_top_mm,
            margin_bottom_mm=margin_bottom_mm,
            margin_inside_mm=margin_inside_mm,
            margin_outside_mm=margin_outside_mm,
        )
        text = apply_rules_to_plan(plan, text_rules)
        report["plans"] += 1
        report["segments"] += int(layout.get("segments", 0))
        report["page_breaks"] += int(layout.get("page_breaks", 0))
        report["paragraphs"] += int(text.get("paragraphs", 0))
        report["elements"] += int(text.get("elements", 0))
    return report


def set_plans_mode(plans: list[dict[str, Any]], mode: str) -> None:
    """Déclare le mode UI du plan sans toucher au contenu."""
    value = "readonly" if str(mode).casefold() == "readonly" else "edit"
    for plan in plans:
        if not isinstance(plan, dict):
            continue
        ui = plan.setdefault("tomelinea_ui", {})
        if not isinstance(ui, dict):
            ui = {}
            plan["tomelinea_ui"] = ui
        ui["mode"] = value
