from __future__ import annotations

"""Application déterministe des règles générales du texte aux plans Canvas.

Phase 2.40G : règles générales du Livre entier. Les paragraphes de titre
(Heading/Titre/Chapitre/Title) restent inchangés.
"""

from copy import deepcopy
from typing import Any

PX_PER_MM = 96.0 / 25.4
PX_PER_PT = 96.0 / 72.0


def _tl(element: dict[str, Any]) -> dict[str, Any]:
    ext = element.get("extension")
    if not isinstance(ext, dict):
        return {}
    tl = ext.get("tomelinea")
    return tl if isinstance(tl, dict) else {}


def _paragraph_info(element: dict[str, Any]) -> tuple[str | None, str | None]:
    tl = _tl(element)
    paragraph = tl.get("paragraph")
    if not isinstance(paragraph, dict):
        paragraph = {}
    fmt = paragraph.get("format")
    if not isinstance(fmt, dict):
        fmt = {}
    pid = paragraph.get("id")
    style = fmt.get("style_id")

    if pid is None and tl.get("paragraphEnd") is not None:
        pid = f"p:{tl.get('paragraphEnd')}"
        fmt2 = tl.get("format")
        if isinstance(fmt2, dict):
            style = fmt2.get("style_id")

    return (
        str(pid) if pid is not None else None,
        str(style) if style is not None else None,
    )


def _is_heading_style(style_id: str | None) -> bool:
    value = " ".join(str(style_id or "").replace("_", " ").replace("-", " ").casefold().split())
    compact = value.replace(" ", "")
    if compact in {"heading1", "heading2", "heading3", "heading4", "heading5", "heading6", "titre1", "titre2", "titre3", "titre4", "titre5", "titre6"}:
        return True
    return any(token in value for token in ("heading", "titre", "chapitre", "chapter", "title"))


def _is_generated(element: dict[str, Any], kind: str | None = None) -> bool:
    marker = _tl(element).get("generalTextRuleGenerated")
    if kind is None:
        return bool(marker)
    return str(marker or "") == str(kind)


def _clean_generated(main: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [deepcopy(item) for item in main if not (isinstance(item, dict) and _is_generated(item))]


def _body_paragraph_ids(main: list[dict[str, Any]]) -> set[str]:
    result: set[str] = set()
    for item in main:
        if not isinstance(item, dict):
            continue
        pid, style = _paragraph_info(item)
        if not pid or _is_heading_style(style):
            continue
        typ = str(item.get("type") or "").lower()
        if typ in {"image", "table", "pagebreak"}:
            continue
        value = str(item.get("value") or "")
        if value and value != "\n":
            result.add(pid)
    return result


def _format_number(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def normalize_general_text_rules(rules: dict[str, Any]) -> dict[str, Any]:
    font = str(rules.get("font_family") or "Arial").strip() or "Arial"
    size_pt = max(6.0, min(72.0, _format_number(rules.get("font_size_pt"), 11.0)))
    alignment = str(rules.get("alignment") or "justify").lower()
    if alignment not in {"justify", "left"}:
        alignment = "justify"
    first_indent = max(0.0, min(30.0, _format_number(rules.get("first_line_indent_mm"), 0.0)))
    line_multiple = max(0.8, min(3.0, _format_number(rules.get("line_spacing_multiple"), 1.15)))
    gap_mm = max(0.0, min(20.0, _format_number(rules.get("paragraph_gap_mm"), 0.0)))
    hyphenation = str(rules.get("hyphenation") or "forbid").lower()
    if hyphenation not in {"forbid", "controlled"}:
        hyphenation = "forbid"
    line_pitch_mm = size_pt * 25.4 / 72.0 * line_multiple
    return {
        "font_family": font,
        "font_size_pt": round(size_pt, 2),
        "alignment": alignment,
        "first_line_indent_mm": round(first_indent, 2),
        "line_spacing_multiple": round(line_multiple, 2),
        "line_pitch_mm": round(line_pitch_mm, 2),
        "paragraph_gap_mm": round(gap_mm, 2),
        "hyphenation": hyphenation,
        "confirmed": True,
    }


def apply_rules_to_plan(plan: dict[str, Any], rules: dict[str, Any]) -> dict[str, int]:
    """Applique les règles au texte courant d'un plan Canvas en mémoire.

    Le retrait de première ligne est matérialisé par un TAB généré dont la
    largeur est fixée au niveau des options du segment. C'est déterministe et
    supprimable lors d'une nouvelle application. L'espace après paragraphe est
    matérialisé par une ligne technique générée de hauteur contrôlée.
    """
    normalized = normalize_general_text_rules(rules)
    changed_elements = 0
    changed_paragraphs: set[str] = set()

    for segment in list(plan.get("render_segments") or []):
        if not isinstance(segment, dict):
            continue
        data = segment.get("data")
        if not isinstance(data, dict):
            continue
        raw_main = data.get("main")
        if not isinstance(raw_main, list):
            continue
        main = _clean_generated(raw_main)
        body_ids = _body_paragraph_ids(main)
        if not body_ids:
            data["main"] = main
            continue

        options = segment.setdefault("options", {})
        if not isinstance(options, dict):
            options = {}
            segment["options"] = options
        size_px = normalized["font_size_pt"] * PX_PER_PT
        # Ces valeurs sont les valeurs de repli du corps de texte. Les titres
        # conservent leurs propriétés explicites traduites depuis la Source.
        options["defaultFont"] = normalized["font_family"]
        options["defaultSize"] = size_px
        if normalized["first_line_indent_mm"] > 0:
            options["defaultTabWidth"] = normalized["first_line_indent_mm"] * PX_PER_MM

        output: list[dict[str, Any]] = []
        indent_done: set[str] = set()
        gap_done: set[str] = set()
        row_flex = "alignment" if normalized["alignment"] == "justify" else "left"

        for original in main:
            if not isinstance(original, dict):
                output.append(original)
                continue
            item = deepcopy(original)
            pid, _style = _paragraph_info(item)
            is_body = bool(pid and pid in body_ids)

            if is_body and pid not in indent_done:
                value = str(item.get("value") or "")
                if value and value != "\n" and normalized["first_line_indent_mm"] > 0:
                    output.append({
                        "type": "tab",
                        "value": "",
                        "extension": {
                            "tomelinea": {
                                "generalTextRuleGenerated": "indent",
                                "paragraphId": pid,
                            }
                        },
                    })
                    indent_done.add(pid)

            if is_body:
                typ = str(item.get("type") or "").lower()
                value = str(item.get("value") or "")
                if typ not in {"image", "table", "pagebreak", "tab"}:
                    item["font"] = normalized["font_family"]
                    item["size"] = size_px
                    item["rowFlex"] = row_flex
                    item["rowMargin"] = normalized["line_spacing_multiple"]
                    changed_elements += 1
                    changed_paragraphs.add(pid)

            output.append(item)

            if is_body and pid not in gap_done:
                tl = _tl(item)
                is_end = tl.get("paragraphEnd") is not None or str(item.get("value") or "") == "\n"
                if is_end:
                    gap_done.add(pid)
                    gap = normalized["paragraph_gap_mm"]
                    if gap > 0:
                        output.append({
                            "value": "\n",
                            "size": max(1.0, gap * PX_PER_MM),
                            "rowMargin": 0.2,
                            "extension": {
                                "tomelinea": {
                                    "generalTextRuleGenerated": "paragraph_gap",
                                    "paragraphId": pid,
                                }
                            },
                        })

        data["main"] = output

    return {
        "paragraphs": len(changed_paragraphs),
        "elements": changed_elements,
    }


def infer_rules_from_plans(plans: list[dict[str, Any]]) -> dict[str, Any]:
    """Repli robuste quand l'analyse du Livre n'a pas encore fourni de valeurs."""
    from collections import Counter

    fonts: Counter[str] = Counter()
    sizes: Counter[float] = Counter()
    row_margins: list[float] = []
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
                if value and value != "\n":
                    if item.get("font"):
                        fonts[str(item["font"])] += max(1, len(value))
                    try:
                        size = float(item.get("size")) / PX_PER_PT
                        if size > 0:
                            sizes[round(size, 2)] += max(1, len(value))
                    except (TypeError, ValueError):
                        pass
                try:
                    margin = float(item.get("rowMargin"))
                    if margin > 0:
                        row_margins.append(margin)
                except (TypeError, ValueError):
                    pass
                if item.get("rowFlex"):
                    aligns[str(item.get("rowFlex"))] += 1
                tl = _tl(item)
                paragraph = tl.get("paragraph") if isinstance(tl.get("paragraph"), dict) else {}
                fmt = paragraph.get("format") if isinstance(paragraph.get("format"), dict) else {}
                try:
                    val = fmt.get("first_line_mm")
                    if val is not None:
                        first_indents.append(float(val))
                except (TypeError, ValueError):
                    pass
                try:
                    after_pt = fmt.get("spacing_after_pt")
                    if after_pt is not None:
                        gaps.append(float(after_pt) * 25.4 / 72.0)
                except (TypeError, ValueError):
                    pass

    def median(values: list[float], default: float) -> float:
        values = sorted(values)
        if not values:
            return default
        return values[len(values)//2]

    font = fonts.most_common(1)[0][0] if fonts else "Arial"
    size = sizes.most_common(1)[0][0] if sizes else 11.0
    row = median(row_margins, 1.15)
    indent = median(first_indents, 0.0)
    gap = median(gaps, 0.0)
    align_raw = aligns.most_common(1)[0][0] if aligns else "alignment"
    alignment = "left" if align_raw == "left" else "justify"
    return normalize_general_text_rules({
        "font_family": font,
        "font_size_pt": size,
        "alignment": alignment,
        "first_line_indent_mm": indent,
        "line_spacing_multiple": row,
        "paragraph_gap_mm": gap,
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
    """Applique format + marges au vrai plan Canvas en mémoire.

    2.40D : l'écran Format ne modifie plus seulement le modèle Livre. Les
    options réellement consommées par Canvas Editor sont mises à jour avant le
    rechargement du document. Toutes les sections du plan reçoivent le même
    format cible choisi par l'utilisateur.
    """
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
    # Canvas Editor expose des marges gauche/droite, pas une notion éditoriale
    # recto/verso. Le Livre conserve malgré tout intérieur/extérieur comme
    # information canonique ; le rendu courant utilise intérieur à gauche et
    # extérieur à droite. L'alternance miroir sera traitée dans une étape
    # dédiée, sans bloquer la validation fonctionnelle de ce panneau.
    margins_px = [
        top * PX_PER_MM,
        outside * PX_PER_MM,
        bottom * PX_PER_MM,
        inside * PX_PER_MM,
    ]

    segments = 0
    page_breaks = 0
    for segment in list(plan.get("render_segments") or []):
        if not isinstance(segment, dict):
            continue
        options = segment.setdefault("options", {})
        if not isinstance(options, dict):
            options = {}
            segment["options"] = options
        options["width"] = width_px
        options["height"] = height_px
        options["paperDirection"] = direction
        options["margins"] = list(margins_px)
        segments += 1

        data = segment.get("data")
        main = data.get("main") if isinstance(data, dict) else None
        if not isinstance(main, list):
            continue
        for item in main:
            if not isinstance(item, dict) or str(item.get("type") or "").lower() != "pagebreak":
                continue
            item["paperDirection"] = direction
            tl = _tl(item)
            next_options = tl.get("nextSectionOptions")
            if isinstance(next_options, dict):
                next_options["width"] = width_px
                next_options["height"] = height_px
                next_options["paperDirection"] = direction
                next_options["margins"] = list(margins_px)
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
    """Applique en une fois les réglages globaux aux plans Canvas."""
    report = {
        "plans": 0,
        "segments": 0,
        "page_breaks": 0,
        "paragraphs": 0,
        "elements": 0,
    }
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

def set_plan_mode(plan: dict[str, Any], mode: str = "readonly") -> int:
    """Force le mode Canvas pour tous les segments d'un plan."""
    wanted = "edit" if str(mode).lower() == "edit" else "readonly"
    changed = 0
    for segment in list(plan.get("render_segments") or []):
        if not isinstance(segment, dict):
            continue
        options = segment.setdefault("options", {})
        if not isinstance(options, dict):
            options = {}
            segment["options"] = options
        if options.get("mode") != wanted:
            options["mode"] = wanted
            changed += 1
    return changed


def set_plans_mode(plans: list[dict[str, Any]], mode: str = "readonly") -> int:
    """Force le mode Canvas de toutes les unités de composition."""
    return sum(set_plan_mode(plan, mode) for plan in list(plans or ()) if isinstance(plan, dict))

