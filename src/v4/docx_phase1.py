from __future__ import annotations

"""
TomeLinea V4 — Phase 1 DOCX.

Analyse factuelle OOXML d'un document Word, sans Canvas, sans pagination
TomeLinea et sans règle éditoriale. Le résultat constitue le modèle Source
interne qui servira plus tard au moteur de composition et aux contrôles
éditoriaux.

Le module n'utilise volontairement pas Word, LibreOffice ni python-docx :
les valeurs natives OOXML sont lues directement et les unités physiques sont
conservées en parallèle de leur valeur source.
"""

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
import json
import re
import zipfile
import xml.etree.ElementTree as ET


PHASE1_SCHEMA = "tomelinea-source-model-phase1"
PHASE1_VERSION = 4
ENGINE_NAME = "tomelinea.docx_phase1"
ENGINE_VERSION = "4"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
WP = "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
PIC = "http://schemas.openxmlformats.org/drawingml/2006/picture"
V = "urn:schemas-microsoft-com:vml"
W14 = "http://schemas.microsoft.com/office/word/2010/wordml"
PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"
CP = "http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
DC = "http://purl.org/dc/elements/1.1/"
DCTERMS = "http://purl.org/dc/terms/"
EP = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
VT = "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"

NS = {
    "w": W,
    "r": R,
    "wp": WP,
    "a": A,
    "pic": PIC,
    "v": V,
    "w14": W14,
    "rel": PKG_REL,
    "cp": CP,
    "dc": DC,
    "dcterms": DCTERMS,
    "ep": EP,
    "vt": VT,
}


def _q(ns: str, name: str) -> str:
    return f"{{{NS[ns]}}}{name}"


def _attr(element: ET.Element | None, ns: str, name: str) -> str | None:
    if element is None:
        return None
    return element.get(_q(ns, name))


def _first(element: ET.Element | None, path: str) -> ET.Element | None:
    if element is None:
        return None
    return element.find(path, NS)


def _text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return "".join(element.itertext())


def _bool_value(element: ET.Element | None) -> bool | None:
    if element is None:
        return None
    raw = _attr(element, "w", "val")
    if raw is None:
        return True
    return str(raw).strip().lower() not in {"0", "false", "off", "no"}


def _int(raw: str | None) -> int | None:
    if raw is None:
        return None
    try:
        return int(str(raw).strip())
    except (TypeError, ValueError):
        return None


def _float(raw: str | None) -> float | None:
    if raw is None:
        return None
    try:
        return float(str(raw).strip())
    except (TypeError, ValueError):
        return None


def _round(value: float, digits: int = 4) -> float:
    return round(float(value), digits)


def twips_to_mm(value: int | float | None) -> float | None:
    if value is None:
        return None
    return _round(float(value) * 25.4 / 1440.0, 4)


def twips_to_pt(value: int | float | None) -> float | None:
    if value is None:
        return None
    return _round(float(value) / 20.0, 4)


def half_points_to_pt(value: int | float | None) -> float | None:
    if value is None:
        return None
    return _round(float(value) / 2.0, 4)


def emu_to_mm(value: int | float | None) -> float | None:
    if value is None:
        return None
    return _round(float(value) * 25.4 / 914400.0, 4)


def emu_to_pt(value: int | float | None) -> float | None:
    if value is None:
        return None
    return _round(float(value) * 72.0 / 914400.0, 4)


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _xml(archive: zipfile.ZipFile, name: str, *, required: bool = False) -> ET.Element | None:
    try:
        return ET.fromstring(archive.read(name))
    except KeyError:
        if required:
            raise ValueError(f"DOCX incomplet : {name} absent.")
        return None
    except ET.ParseError as exc:
        raise ValueError(f"XML DOCX invalide : {name}") from exc


def _part_target(base_part: str, target: str) -> str:
    target = str(target or "").replace("\\", "/")
    if target.startswith("/"):
        return target.lstrip("/")
    base = PurePosixPath(base_part).parent
    combined = base / target
    parts: list[str] = []
    for part in combined.parts:
        if part in {"", "."}:
            continue
        if part == "..":
            if parts:
                parts.pop()
            continue
        parts.append(part)
    return "/".join(parts)


def _relationships(archive: zipfile.ZipFile, part: str) -> dict[str, dict[str, str]]:
    path = PurePosixPath(part)
    rel_name = str(path.parent / "_rels" / f"{path.name}.rels")
    root = _xml(archive, rel_name)
    if root is None:
        return {}
    result: dict[str, dict[str, str]] = {}
    for rel in root.findall("rel:Relationship", NS):
        rel_id = rel.get("Id")
        if not rel_id:
            continue
        target = rel.get("Target", "")
        target_mode = rel.get("TargetMode", "Internal")
        resolved = target if target_mode == "External" else _part_target(part, target)
        result[rel_id] = {
            "id": rel_id,
            "type": rel.get("Type", ""),
            "target": target,
            "target_mode": target_mode,
            "resolved_target": resolved,
        }
    return result


def _simple_value(parent: ET.Element | None, tag: str) -> str | None:
    node = _first(parent, f"w:{tag}")
    return _attr(node, "w", "val")


def _parse_tabs(ppr: ET.Element | None) -> list[dict[str, Any]]:
    tabs = _first(ppr, "w:tabs")
    if tabs is None:
        return []
    result: list[dict[str, Any]] = []
    for tab in tabs.findall("w:tab", NS):
        pos = _int(_attr(tab, "w", "pos"))
        result.append({
            "type": _attr(tab, "w", "val"),
            "leader": _attr(tab, "w", "leader"),
            "position_twips": pos,
            "position_mm": twips_to_mm(pos),
        })
    return result


def _parse_paragraph_props(ppr: ET.Element | None) -> dict[str, Any]:
    if ppr is None:
        return {}

    spacing = _first(ppr, "w:spacing")
    ind = _first(ppr, "w:ind")
    numpr = _first(ppr, "w:numPr")
    line = _int(_attr(spacing, "w", "line"))
    line_rule = _attr(spacing, "w", "lineRule")

    result: dict[str, Any] = {
        "style_id": _simple_value(ppr, "pStyle"),
        "alignment": _simple_value(ppr, "jc"),
        "keep_next": _bool_value(_first(ppr, "w:keepNext")),
        "keep_lines": _bool_value(_first(ppr, "w:keepLines")),
        "page_break_before": _bool_value(_first(ppr, "w:pageBreakBefore")),
        "widow_control": _bool_value(_first(ppr, "w:widowControl")),
        "contextual_spacing": _bool_value(_first(ppr, "w:contextualSpacing")),
        "suppress_line_numbers": _bool_value(_first(ppr, "w:suppressLineNumbers")),
        "bidi": _bool_value(_first(ppr, "w:bidi")),
        "outline_level": _int(_simple_value(ppr, "outlineLvl")),
        "tabs": _parse_tabs(ppr),
    }

    if spacing is not None:
        before = _int(_attr(spacing, "w", "before"))
        after = _int(_attr(spacing, "w", "after"))
        result["spacing"] = {
            "before_twips": before,
            "before_pt": twips_to_pt(before),
            "before_mm": twips_to_mm(before),
            "after_twips": after,
            "after_pt": twips_to_pt(after),
            "after_mm": twips_to_mm(after),
            "before_lines": _int(_attr(spacing, "w", "beforeLines")),
            "after_lines": _int(_attr(spacing, "w", "afterLines")),
            "before_auto": (_attr(spacing, "w", "beforeAutospacing") or "").lower() in {"1", "true", "on"} if _attr(spacing, "w", "beforeAutospacing") is not None else None,
            "after_auto": (_attr(spacing, "w", "afterAutospacing") or "").lower() in {"1", "true", "on"} if _attr(spacing, "w", "afterAutospacing") is not None else None,
            "line_raw": line,
            "line_rule": line_rule,
            "line_pt": twips_to_pt(line) if line_rule in {"exact", "atLeast"} else None,
            "line_multiple": _round(line / 240.0, 4) if line is not None and line_rule in {None, "auto"} else None,
        }

    if ind is not None:
        left = _int(_attr(ind, "w", "left") or _attr(ind, "w", "start"))
        right = _int(_attr(ind, "w", "right") or _attr(ind, "w", "end"))
        first = _int(_attr(ind, "w", "firstLine"))
        hanging = _int(_attr(ind, "w", "hanging"))
        result["indent"] = {
            "left_twips": left,
            "left_mm": twips_to_mm(left),
            "right_twips": right,
            "right_mm": twips_to_mm(right),
            "first_line_twips": first,
            "first_line_mm": twips_to_mm(first),
            "hanging_twips": hanging,
            "hanging_mm": twips_to_mm(hanging),
        }

    if numpr is not None:
        result["numbering"] = {
            "num_id": _int(_simple_value(numpr, "numId")),
            "level": _int(_simple_value(numpr, "ilvl")),
        }

    return _drop_empty(result)


def _parse_run_fonts(rpr: ET.Element | None) -> dict[str, Any]:
    node = _first(rpr, "w:rFonts")
    if node is None:
        return {}
    return _drop_empty({
        "ascii": _attr(node, "w", "ascii"),
        "hansi": _attr(node, "w", "hAnsi"),
        "east_asia": _attr(node, "w", "eastAsia"),
        "complex_script": _attr(node, "w", "cs"),
        "ascii_theme": _attr(node, "w", "asciiTheme"),
        "hansi_theme": _attr(node, "w", "hAnsiTheme"),
        "east_asia_theme": _attr(node, "w", "eastAsiaTheme"),
        "complex_script_theme": _attr(node, "w", "cstheme"),
        "hint": _attr(node, "w", "hint"),
    })


def _parse_run_props(rpr: ET.Element | None) -> dict[str, Any]:
    if rpr is None:
        return {}
    size = _int(_simple_value(rpr, "sz"))
    size_cs = _int(_simple_value(rpr, "szCs"))
    spacing = _int(_simple_value(rpr, "spacing"))
    position = _int(_simple_value(rpr, "position"))
    kern = _int(_simple_value(rpr, "kern"))
    color = _first(rpr, "w:color")
    underline = _first(rpr, "w:u")
    lang = _first(rpr, "w:lang")

    result = {
        "style_id": _simple_value(rpr, "rStyle"),
        "fonts": _parse_run_fonts(rpr),
        "size_half_points": size,
        "size_pt": half_points_to_pt(size),
        "size_cs_half_points": size_cs,
        "size_cs_pt": half_points_to_pt(size_cs),
        "bold": _bool_value(_first(rpr, "w:b")),
        "bold_cs": _bool_value(_first(rpr, "w:bCs")),
        "italic": _bool_value(_first(rpr, "w:i")),
        "italic_cs": _bool_value(_first(rpr, "w:iCs")),
        "underline": (_attr(underline, "w", "val") or "single") if underline is not None else None,
        "strike": _bool_value(_first(rpr, "w:strike")),
        "double_strike": _bool_value(_first(rpr, "w:dstrike")),
        "caps": _bool_value(_first(rpr, "w:caps")),
        "small_caps": _bool_value(_first(rpr, "w:smallCaps")),
        "vanish": _bool_value(_first(rpr, "w:vanish")),
        "color": _drop_empty({
            "value": _attr(color, "w", "val"),
            "theme": _attr(color, "w", "themeColor"),
            "theme_tint": _attr(color, "w", "themeTint"),
            "theme_shade": _attr(color, "w", "themeShade"),
        }) if color is not None else None,
        "highlight": _simple_value(rpr, "highlight"),
        "vertical_align": _simple_value(rpr, "vertAlign"),
        "spacing_twips": spacing,
        "spacing_pt": twips_to_pt(spacing),
        "position_half_points": position,
        "position_pt": half_points_to_pt(position),
        "kerning_half_points": kern,
        "kerning_pt": half_points_to_pt(kern),
        "language": _drop_empty({
            "latin": _attr(lang, "w", "val"),
            "east_asia": _attr(lang, "w", "eastAsia"),
            "complex_script": _attr(lang, "w", "bidi"),
        }) if lang is not None else None,
    }
    return _drop_empty(result)


def _drop_empty(value: Any) -> Any:
    if isinstance(value, dict):
        result = {}
        for key, item in value.items():
            cleaned = _drop_empty(item)
            if cleaned in ({}, [], None, ""):
                continue
            result[key] = cleaned
        return result
    if isinstance(value, list):
        return [_drop_empty(item) for item in value]
    return value


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    result = json.loads(json.dumps(base, ensure_ascii=False)) if base else {}
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _styles(styles_root: ET.Element | None) -> dict[str, Any]:
    if styles_root is None:
        return {
            "doc_defaults": {"paragraph": {}, "run": {}},
            "styles": {},
        }

    defaults = _first(styles_root, "w:docDefaults")
    p_default = _first(defaults, "w:pPrDefault/w:pPr")
    r_default = _first(defaults, "w:rPrDefault/w:rPr")

    styles: dict[str, dict[str, Any]] = {}
    for style in styles_root.findall("w:style", NS):
        style_id = _attr(style, "w", "styleId")
        if not style_id:
            continue
        styles[style_id] = _drop_empty({
            "style_id": style_id,
            "type": _attr(style, "w", "type"),
            "name": _simple_value(style, "name") or style_id,
            "based_on": _simple_value(style, "basedOn"),
            "next": _simple_value(style, "next"),
            "link": _simple_value(style, "link"),
            "default": (_attr(style, "w", "default") or "").lower() in {"1", "true", "on"},
            "custom": (_attr(style, "w", "customStyle") or "").lower() in {"1", "true", "on"},
            "qformat": _bool_value(_first(style, "w:qFormat")),
            "ui_priority": _int(_simple_value(style, "uiPriority")),
            "paragraph": _parse_paragraph_props(_first(style, "w:pPr")),
            "run": _parse_run_props(_first(style, "w:rPr")),
        })

    latent = _first(styles_root, "w:latentStyles")
    latent_info: dict[str, Any] = {}
    if latent is not None:
        latent_info = _drop_empty({
            "default_locked_state": _attr(latent, "w", "defLockedState"),
            "default_ui_priority": _int(_attr(latent, "w", "defUIPriority")),
            "default_semi_hidden": _attr(latent, "w", "defSemiHidden"),
            "default_unhide_when_used": _attr(latent, "w", "defUnhideWhenUsed"),
            "default_qformat": _attr(latent, "w", "defQFormat"),
            "count": _int(_attr(latent, "w", "count")),
        })

    default_paragraph_style_id = next((
        style_id for style_id, item in styles.items()
        if item.get("type") == "paragraph" and item.get("default")
    ), None)
    default_character_style_id = next((
        style_id for style_id, item in styles.items()
        if item.get("type") == "character" and item.get("default")
    ), None)

    return {
        "doc_defaults": {
            "paragraph": _parse_paragraph_props(p_default),
            "run": _parse_run_props(r_default),
        },
        "default_paragraph_style_id": default_paragraph_style_id,
        "default_character_style_id": default_character_style_id,
        "styles": styles,
        "latent_styles": latent_info,
    }


def _style_chain(styles: dict[str, dict[str, Any]], style_id: str | None) -> list[str]:
    if not style_id or style_id not in styles:
        return []
    result: list[str] = []
    seen: set[str] = set()
    current = style_id
    while current and current not in seen and current in styles:
        seen.add(current)
        result.append(current)
        current = styles[current].get("based_on")
    result.reverse()
    return result


def _effective_paragraph_props(style_data: dict[str, Any], direct: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    styles = style_data["styles"]
    style_id = direct.get("style_id") or style_data.get("default_paragraph_style_id")
    chain = _style_chain(styles, style_id)
    result = style_data["doc_defaults"].get("paragraph", {})
    for item in chain:
        result = _deep_merge(result, styles[item].get("paragraph", {}))
    result = _deep_merge(result, direct)
    return result, chain


def _effective_run_props(
    style_data: dict[str, Any],
    paragraph_chain: list[str],
    direct: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    styles = style_data["styles"]
    result = style_data["doc_defaults"].get("run", {})
    for item in paragraph_chain:
        result = _deep_merge(result, styles[item].get("run", {}))
    char_style = direct.get("style_id")
    char_chain = _style_chain(styles, char_style)
    for item in char_chain:
        if styles[item].get("type") == "character":
            result = _deep_merge(result, styles[item].get("run", {}))
    result = _deep_merge(result, direct)
    return result, char_chain


def _theme_fonts(theme_root: ET.Element | None) -> dict[str, Any]:
    if theme_root is None:
        return {}
    theme_ns = {"a": A}
    result: dict[str, Any] = {}
    for family_key, path in (
        ("major", ".//a:themeElements/a:fontScheme/a:majorFont"),
        ("minor", ".//a:themeElements/a:fontScheme/a:minorFont"),
    ):
        node = theme_root.find(path, theme_ns)
        if node is None:
            continue
        latin = node.find("a:latin", theme_ns)
        ea = node.find("a:ea", theme_ns)
        cs = node.find("a:cs", theme_ns)
        result[family_key] = _drop_empty({
            "latin": latin.get("typeface") if latin is not None else None,
            "east_asia": ea.get("typeface") if ea is not None else None,
            "complex_script": cs.get("typeface") if cs is not None else None,
        })
    return result


def _resolve_theme_font(token: str | None, theme_fonts: dict[str, Any]) -> str | None:
    if not token:
        return None
    raw = token.lower()
    family = "major" if raw.startswith("major") else "minor" if raw.startswith("minor") else None
    if not family:
        return None
    script = "east_asia" if "eastasia" in raw else "complex_script" if "bidi" in raw or "cs" in raw else "latin"
    return theme_fonts.get(family, {}).get(script)


def _preferred_font(effective_run: dict[str, Any], theme_fonts: dict[str, Any]) -> str | None:
    fonts = effective_run.get("fonts", {})
    for key in ("ascii", "hansi", "east_asia", "complex_script"):
        value = fonts.get(key)
        if value:
            return value
    for key in ("ascii_theme", "hansi_theme", "east_asia_theme", "complex_script_theme"):
        value = _resolve_theme_font(fonts.get(key), theme_fonts)
        if value:
            return value
    return None


def _font_table(font_root: ET.Element | None) -> list[dict[str, Any]]:
    if font_root is None:
        return []
    result = []
    for font in font_root.findall("w:font", NS):
        name = _attr(font, "w", "name")
        if not name:
            continue
        result.append(_drop_empty({
            "name": name,
            "alt_name": _simple_value(font, "altName"),
            "family": _simple_value(font, "family"),
            "pitch": _simple_value(font, "pitch"),
            "charset": _simple_value(font, "charset"),
            "panose1": _simple_value(font, "panose1"),
            "signature": _drop_empty({
                "usb0": _attr(_first(font, "w:sig"), "w", "usb0"),
                "usb1": _attr(_first(font, "w:sig"), "w", "usb1"),
                "usb2": _attr(_first(font, "w:sig"), "w", "usb2"),
                "usb3": _attr(_first(font, "w:sig"), "w", "usb3"),
            }),
        }))
    return result


def _numbering(numbering_root: ET.Element | None) -> dict[str, Any]:
    if numbering_root is None:
        return {"abstract": {}, "instances": {}}
    abstracts: dict[str, Any] = {}
    for abstract in numbering_root.findall("w:abstractNum", NS):
        abstract_id = _attr(abstract, "w", "abstractNumId")
        if abstract_id is None:
            continue
        levels: dict[str, Any] = {}
        for lvl in abstract.findall("w:lvl", NS):
            ilvl = _attr(lvl, "w", "ilvl") or "0"
            ppr = _first(lvl, "w:pPr")
            rpr = _first(lvl, "w:rPr")
            levels[ilvl] = _drop_empty({
                "level": _int(ilvl),
                "start": _int(_simple_value(lvl, "start")),
                "format": _simple_value(lvl, "numFmt"),
                "text": _simple_value(lvl, "lvlText"),
                "suffix": _simple_value(lvl, "suff"),
                "alignment": _simple_value(lvl, "lvlJc"),
                "paragraph_style": _simple_value(lvl, "pStyle"),
                "paragraph": _parse_paragraph_props(ppr),
                "run": _parse_run_props(rpr),
            })
        abstracts[abstract_id] = _drop_empty({
            "id": _int(abstract_id),
            "multi_level_type": _simple_value(abstract, "multiLevelType"),
            "name": _simple_value(abstract, "name"),
            "style_link": _simple_value(abstract, "styleLink"),
            "num_style_link": _simple_value(abstract, "numStyleLink"),
            "levels": levels,
        })

    instances: dict[str, Any] = {}
    for num in numbering_root.findall("w:num", NS):
        num_id = _attr(num, "w", "numId")
        if num_id is None:
            continue
        overrides = []
        for override in num.findall("w:lvlOverride", NS):
            overrides.append(_drop_empty({
                "level": _int(_attr(override, "w", "ilvl")),
                "start_override": _int(_simple_value(override, "startOverride")),
            }))
        instances[num_id] = _drop_empty({
            "id": _int(num_id),
            "abstract_num_id": _int(_simple_value(num, "abstractNumId")),
            "overrides": overrides,
        })
    return {"abstract": abstracts, "instances": instances}


def _resolved_numbering(numbering: dict[str, Any], num_info: dict[str, Any] | None) -> dict[str, Any] | None:
    if not num_info:
        return None
    num_id = num_info.get("num_id")
    level = num_info.get("level", 0)
    if num_id is None:
        return None
    instance = numbering.get("instances", {}).get(str(num_id), {})
    abstract_id = instance.get("abstract_num_id")
    level_info = numbering.get("abstract", {}).get(str(abstract_id), {}).get("levels", {}).get(str(level), {})
    return _drop_empty({
        **num_info,
        "abstract_num_id": abstract_id,
        "format": level_info.get("format"),
        "text": level_info.get("text"),
        "start": level_info.get("start"),
        "paragraph": level_info.get("paragraph"),
    })


def _run_text(run: ET.Element) -> tuple[str, list[dict[str, Any]]]:
    parts: list[str] = []
    controls: list[dict[str, Any]] = []
    for node in run.iter():
        if node.tag in {_q("w", "t"), _q("w", "delText")}:
            parts.append(node.text or "")
        elif node.tag == _q("w", "tab"):
            parts.append("\t")
            controls.append({"type": "tab"})
        elif node.tag in {_q("w", "br"), _q("w", "cr")}:
            br_type = _attr(node, "w", "type") or "line"
            if br_type == "page":
                controls.append({"type": "page_break"})
            elif br_type == "column":
                controls.append({"type": "column_break"})
            else:
                controls.append({"type": "line_break"})
            parts.append("\n")
        elif node.tag == _q("w", "noBreakHyphen"):
            parts.append("‑")
            controls.append({"type": "no_break_hyphen"})
        elif node.tag == _q("w", "softHyphen"):
            parts.append("\u00ad")
            controls.append({"type": "soft_hyphen"})
        elif node.tag == _q("w", "instrText"):
            controls.append({"type": "field_instruction", "value": node.text or ""})
        elif node.tag == _q("w", "fldChar"):
            controls.append({"type": "field_char", "value": _attr(node, "w", "fldCharType")})
    return "".join(parts), controls


def _image_from_run(
    run: ET.Element,
    relationships: dict[str, dict[str, str]],
    *,
    paragraph_index: int,
    run_index: int,
) -> list[dict[str, Any]]:
    images: list[dict[str, Any]] = []
    for drawing in run.findall(".//w:drawing", NS):
        container = drawing.find("wp:inline", NS)
        mode = "inline"
        if container is None:
            container = drawing.find("wp:anchor", NS)
            mode = "floating"
        if container is None:
            continue
        extent = container.find("wp:extent", NS)
        cx = _int(extent.get("cx")) if extent is not None else None
        cy = _int(extent.get("cy")) if extent is not None else None
        docpr = container.find("wp:docPr", NS)
        blip = container.find(".//a:blip", NS)
        rel_id = blip.get(_q("r", "embed")) if blip is not None else None
        rel = relationships.get(rel_id or "", {})
        wrap = None
        if mode == "floating":
            for child in list(container):
                local = child.tag.rsplit("}", 1)[-1]
                if local.startswith("wrap"):
                    wrap = local
                    break
        pos_h = container.find("wp:positionH", NS)
        pos_v = container.find("wp:positionV", NS)
        off_h = _int(_text(pos_h.find("wp:posOffset", NS))) if pos_h is not None else None
        off_v = _int(_text(pos_v.find("wp:posOffset", NS))) if pos_v is not None else None
        images.append(_drop_empty({
            "paragraph_index": paragraph_index,
            "run_index": run_index,
            "mode": mode,
            "relationship_id": rel_id,
            "part": rel.get("resolved_target"),
            "name": docpr.get("name") if docpr is not None else None,
            "description": docpr.get("descr") if docpr is not None else None,
            "title": docpr.get("title") if docpr is not None else None,
            "width_emu": cx,
            "height_emu": cy,
            "width_mm": emu_to_mm(cx),
            "height_mm": emu_to_mm(cy),
            "wrap": wrap,
            "behind_doc": container.get("behindDoc") if mode == "floating" else None,
            "allow_overlap": container.get("allowOverlap") if mode == "floating" else None,
            "distance_top_emu": _int(container.get("distT")),
            "distance_bottom_emu": _int(container.get("distB")),
            "distance_left_emu": _int(container.get("distL")),
            "distance_right_emu": _int(container.get("distR")),
            "position_h_relative_to": pos_h.get("relativeFrom") if pos_h is not None else None,
            "position_h_offset_emu": off_h,
            "position_h_offset_mm": emu_to_mm(off_h),
            "position_v_relative_to": pos_v.get("relativeFrom") if pos_v is not None else None,
            "position_v_offset_emu": off_v,
            "position_v_offset_mm": emu_to_mm(off_v),
            "advanced": _drawing_advanced(container),
        }))

    for imagedata in run.findall(".//v:imagedata", NS):
        rel_id = imagedata.get(_q("r", "id"))
        rel = relationships.get(rel_id or "", {})
        images.append(_drop_empty({
            "paragraph_index": paragraph_index,
            "run_index": run_index,
            "mode": "vml",
            "relationship_id": rel_id,
            "part": rel.get("resolved_target"),
            "title": imagedata.get("title"),
        }))
    return images


def _section_props(sect: ET.Element | None, relationships: dict[str, dict[str, str]]) -> dict[str, Any]:
    if sect is None:
        return {}
    size = _first(sect, "w:pgSz")
    margins = _first(sect, "w:pgMar")
    cols = _first(sect, "w:cols")
    pgnum = _first(sect, "w:pgNumType")
    doc_grid = _first(sect, "w:docGrid")
    width = _int(_attr(size, "w", "w"))
    height = _int(_attr(size, "w", "h"))
    margin_names = ("top", "right", "bottom", "left", "header", "footer", "gutter")
    margin_data: dict[str, Any] = {}
    if margins is not None:
        for name in margin_names:
            raw = _int(_attr(margins, "w", name))
            margin_data[f"{name}_twips"] = raw
            margin_data[f"{name}_mm"] = twips_to_mm(raw)

    refs = []
    for tag, kind in (("headerReference", "header"), ("footerReference", "footer")):
        for ref in sect.findall(f"w:{tag}", NS):
            rel_id = _attr(ref, "r", "id")
            rel = relationships.get(rel_id or "", {})
            refs.append(_drop_empty({
                "kind": kind,
                "type": _attr(ref, "w", "type"),
                "relationship_id": rel_id,
                "part": rel.get("resolved_target"),
            }))

    col_items = []
    if cols is not None:
        for col in cols.findall("w:col", NS):
            w = _int(_attr(col, "w", "w"))
            space = _int(_attr(col, "w", "space"))
            col_items.append({
                "width_twips": w,
                "width_mm": twips_to_mm(w),
                "space_twips": space,
                "space_mm": twips_to_mm(space),
            })

    return _drop_empty({
        "page": {
            "width_twips": width,
            "width_mm": twips_to_mm(width),
            "height_twips": height,
            "height_mm": twips_to_mm(height),
            "orientation": _attr(size, "w", "orient") or ("landscape" if width and height and width > height else "portrait" if width and height else None),
            "code": _int(_attr(size, "w", "code")),
        },
        "margins": margin_data,
        "section_break_type": _simple_value(sect, "type") or "nextPage",
        "title_page": _bool_value(_first(sect, "w:titlePg")),
        "bidi": _bool_value(_first(sect, "w:bidi")),
        "rtl_gutter": _bool_value(_first(sect, "w:rtlGutter")),
        "vertical_alignment": _simple_value(sect, "vAlign"),
        "columns": {
            "count": _int(_attr(cols, "w", "num")) if cols is not None else None,
            "space_twips": _int(_attr(cols, "w", "space")) if cols is not None else None,
            "space_mm": twips_to_mm(_int(_attr(cols, "w", "space"))) if cols is not None else None,
            "separator": _attr(cols, "w", "sep") if cols is not None else None,
            "equal_width": _attr(cols, "w", "equalWidth") if cols is not None else None,
            "items": col_items,
        } if cols is not None else None,
        "page_numbering": {
            "start": _int(_attr(pgnum, "w", "start")),
            "format": _attr(pgnum, "w", "fmt"),
            "chapter_style": _int(_attr(pgnum, "w", "chapStyle")),
            "chapter_separator": _attr(pgnum, "w", "chapSep"),
        } if pgnum is not None else None,
        "document_grid": {
            "type": _attr(doc_grid, "w", "type"),
            "line_pitch_twips": _int(_attr(doc_grid, "w", "linePitch")),
            "line_pitch_pt": twips_to_pt(_int(_attr(doc_grid, "w", "linePitch"))),
            "line_pitch_mm": twips_to_mm(_int(_attr(doc_grid, "w", "linePitch"))),
            "char_space_raw": _int(_attr(doc_grid, "w", "charSpace")),
        } if doc_grid is not None else None,
        "header_footer_references": refs,
    })


def _table_props(table: ET.Element, table_index: int) -> dict[str, Any]:
    tblpr = _first(table, "w:tblPr")
    grid = _first(table, "w:tblGrid")
    width = _first(tblpr, "w:tblW")
    indent = _first(tblpr, "w:tblInd")
    layout = _first(tblpr, "w:tblLayout")
    rows = []
    for row_index, row in enumerate(table.findall("w:tr", NS), start=1):
        cells = []
        for cell_index, cell in enumerate(row.findall("w:tc", NS), start=1):
            tcpr = _first(cell, "w:tcPr")
            tcw = _first(tcpr, "w:tcW")
            grid_span = _int(_simple_value(tcpr, "gridSpan")) if tcpr is not None else None
            vmerge = _first(tcpr, "w:vMerge") if tcpr is not None else None
            cell_text = "\n".join(_paragraph_plain_text(p) for p in cell.findall(".//w:p", NS))
            cells.append(_drop_empty({
                "cell": cell_index,
                "text": cell_text,
                "width_type": _attr(tcw, "w", "type") if tcw is not None else None,
                "width_raw": _int(_attr(tcw, "w", "w")) if tcw is not None else None,
                "grid_span": grid_span,
                "vertical_merge": (_attr(vmerge, "w", "val") or "continue") if vmerge is not None else None,
                "vertical_align": _simple_value(tcpr, "vAlign") if tcpr is not None else None,
                "margins": _cell_margins(tcpr),
                "borders": _side_props(tcpr, "tcBorders"),
                "shading": _drop_empty({
                    "fill": _attr(_first(tcpr, "w:shd"), "w", "fill"),
                    "color": _attr(_first(tcpr, "w:shd"), "w", "color"),
                    "value": _attr(_first(tcpr, "w:shd"), "w", "val"),
                }) if tcpr is not None else None,
                "text_direction": _simple_value(tcpr, "textDirection") if tcpr is not None else None,
                "no_wrap": _bool_value(_first(tcpr, "w:noWrap")) if tcpr is not None else None,
            }))
        trpr = _first(row, "w:trPr")
        height = _first(trpr, "w:trHeight")
        hraw = _int(_attr(height, "w", "val")) if height is not None else None
        rows.append(_drop_empty({
            "row": row_index,
            "height_twips": hraw,
            "height_mm": twips_to_mm(hraw),
            "height_rule": _attr(height, "w", "hRule") if height is not None else None,
            "repeat_header": _bool_value(_first(trpr, "w:tblHeader")),
            "cant_split": _bool_value(_first(trpr, "w:cantSplit")),
            "cells": cells,
        }))
    grid_cols = []
    if grid is not None:
        for col in grid.findall("w:gridCol", NS):
            raw = _int(_attr(col, "w", "w"))
            grid_cols.append({"width_twips": raw, "width_mm": twips_to_mm(raw)})
    return _drop_empty({
        "table": table_index,
        "style_id": _simple_value(tblpr, "tblStyle"),
        "alignment": _simple_value(tblpr, "jc"),
        "layout": _attr(layout, "w", "type") if layout is not None else None,
        "width_type": _attr(width, "w", "type") if width is not None else None,
        "width_raw": _int(_attr(width, "w", "w")) if width is not None else None,
        "indent_type": _attr(indent, "w", "type") if indent is not None else None,
        "indent_raw": _int(_attr(indent, "w", "w")) if indent is not None else None,
        "borders": _side_props(tblpr, "tblBorders"),
        "cell_margins": _cell_margins(tblpr),
        "shading": _drop_empty({
            "fill": _attr(_first(tblpr, "w:shd"), "w", "fill"),
            "color": _attr(_first(tblpr, "w:shd"), "w", "color"),
            "value": _attr(_first(tblpr, "w:shd"), "w", "val"),
        }) if tblpr is not None else None,
        "look": _drop_empty(dict(_first(tblpr, "w:tblLook").attrib)) if _first(tblpr, "w:tblLook") is not None else None,
        "grid": grid_cols,
        "row_count": len(rows),
        "rows": rows,
    })


def _paragraph_plain_text(paragraph: ET.Element) -> str:
    parts = []
    for run in paragraph.findall(".//w:r", NS):
        text, _ = _run_text(run)
        parts.append(text)
    return "".join(parts)



def _paragraph_structural_ranges(
    paragraph: ET.Element,
    relationships: dict[str, dict[str, str]],
    *,
    paragraph_index: int,
) -> dict[str, list[dict[str, Any]]]:
    """Return exact character ranges for hyperlinks/bookmarks/changes/SDTs.

    Offsets are zero-based in the paragraph text reconstructed by _run_text.
    They describe Source facts only; no editing decision is made here.
    """
    hyperlinks: list[dict[str, Any]] = []
    markers: list[dict[str, Any]] = []
    changes: list[dict[str, Any]] = []
    controls: list[dict[str, Any]] = []
    offset = 0

    def walk(node: ET.Element) -> None:
        nonlocal offset
        for child in list(node):
            local = child.tag.rsplit("}", 1)[-1]
            if child.tag == _q("w", "r"):
                text, _ = _run_text(child)
                offset += len(text)
                continue
            if child.tag == _q("w", "bookmarkStart"):
                markers.append(_drop_empty({
                    "kind": "start",
                    "id": _attr(child, "w", "id"),
                    "name": _attr(child, "w", "name"),
                    "paragraph": paragraph_index,
                    "offset": offset,
                    "col_first": _int(_attr(child, "w", "colFirst")),
                    "col_last": _int(_attr(child, "w", "colLast")),
                }))
                continue
            if child.tag == _q("w", "bookmarkEnd"):
                markers.append(_drop_empty({
                    "kind": "end",
                    "id": _attr(child, "w", "id"),
                    "paragraph": paragraph_index,
                    "offset": offset,
                }))
                continue
            if child.tag == _q("w", "hyperlink"):
                start = offset
                walk(child)
                rel_id = _attr(child, "r", "id")
                rel = relationships.get(rel_id or "", {})
                hyperlinks.append(_drop_empty({
                    "paragraph": paragraph_index,
                    "start_offset": start,
                    "end_offset": offset,
                    "text": _paragraph_plain_text(child),
                    "relationship_id": rel_id,
                    "target": rel.get("resolved_target"),
                    "target_mode": rel.get("target_mode"),
                    "anchor": _attr(child, "w", "anchor"),
                    "history": _attr(child, "w", "history"),
                    "tooltip": _attr(child, "w", "tooltip"),
                    "doc_location": _attr(child, "w", "docLocation"),
                }))
                continue
            if child.tag in {_q("w", "ins"), _q("w", "del"), _q("w", "moveFrom"), _q("w", "moveTo")}:
                start = offset
                walk(child)
                changes.append(_drop_empty({
                    "type": local,
                    "paragraph": paragraph_index,
                    "start_offset": start,
                    "end_offset": offset,
                    "text": _paragraph_plain_text(child),
                    "id": _attr(child, "w", "id"),
                    "author": _attr(child, "w", "author"),
                    "date": _attr(child, "w", "date"),
                }))
                continue
            if child.tag == _q("w", "sdt"):
                start = offset
                pr = _first(child, "w:sdtPr")
                walk(child)
                controls.append(_drop_empty({
                    "paragraph": paragraph_index,
                    "start_offset": start,
                    "end_offset": offset,
                    "text": _paragraph_plain_text(child),
                    "id": _int(_simple_value(pr, "id")),
                    "tag": _simple_value(pr, "tag"),
                    "alias": _simple_value(pr, "alias"),
                    "lock": _simple_value(pr, "lock"),
                    "appearance": _simple_value(pr, "appearance"),
                    "temporary": _bool_value(_first(pr, "w:temporary")),
                    "showing_placeholder": _bool_value(_first(pr, "w:showingPlcHdr")),
                }))
                continue
            walk(child)

    walk(paragraph)
    return {
        "hyperlinks": hyperlinks,
        "bookmark_markers": markers,
        "tracked_changes": changes,
        "content_controls": controls,
    }


def _pair_bookmarks(paragraph_ranges: list[dict[str, Any]]) -> list[dict[str, Any]]:
    starts: dict[str, dict[str, Any]] = {}
    result: list[dict[str, Any]] = []
    for item in paragraph_ranges:
        bid = str(item.get("id", ""))
        if item.get("kind") == "start":
            starts[bid] = item
        elif item.get("kind") == "end" and bid in starts:
            start = starts.pop(bid)
            result.append(_drop_empty({
                "id": item.get("id"),
                "name": start.get("name"),
                "start_paragraph": start.get("paragraph"),
                "start_offset": start.get("offset"),
                "end_paragraph": item.get("paragraph"),
                "end_offset": item.get("offset"),
                "col_first": start.get("col_first"),
                "col_last": start.get("col_last"),
            }))
    for start in starts.values():
        result.append(_drop_empty({
            "id": start.get("id"),
            "name": start.get("name"),
            "start_paragraph": start.get("paragraph"),
            "start_offset": start.get("offset"),
            "unclosed": True,
        }))
    return result


def _side_props(parent: ET.Element | None, tag: str) -> dict[str, Any]:
    node = _first(parent, f"w:{tag}")
    if node is None:
        return {}
    result: dict[str, Any] = {}
    for side in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = _first(node, f"w:{side}")
        if el is None:
            continue
        result[side] = _drop_empty({
            "value": _attr(el, "w", "val"),
            "size_eighth_points": _int(_attr(el, "w", "sz")),
            "size_pt": _round(_int(_attr(el, "w", "sz")) / 8.0, 4) if _int(_attr(el, "w", "sz")) is not None else None,
            "space_pt": _int(_attr(el, "w", "space")),
            "color": _attr(el, "w", "color"),
            "theme_color": _attr(el, "w", "themeColor"),
        })
    return result


def _cell_margins(tcpr: ET.Element | None) -> dict[str, Any]:
    mar = _first(tcpr, "w:tcMar")
    if mar is None:
        return {}
    result: dict[str, Any] = {}
    for side in ("top", "left", "bottom", "right"):
        el = _first(mar, f"w:{side}")
        if el is None:
            continue
        raw = _int(_attr(el, "w", "w"))
        result[side] = _drop_empty({
            "type": _attr(el, "w", "type"),
            "raw": raw,
            "mm": twips_to_mm(raw) if (_attr(el, "w", "type") or "dxa") == "dxa" else None,
        })
    return result


def _drawing_advanced(container: ET.Element) -> dict[str, Any]:
    src_rect = container.find(".//a:srcRect", NS)
    xfrm = container.find(".//a:xfrm", NS)
    effect = container.find("wp:effectExtent", NS)
    simple = container.find("wp:simplePos", NS)
    wrap_node = next((child for child in list(container) if child.tag.rsplit("}", 1)[-1].startswith("wrap")), None)
    wrap_polygon = wrap_node.find("wp:wrapPolygon", NS) if wrap_node is not None else None
    points = []
    if wrap_polygon is not None:
        start = wrap_polygon.find("wp:start", NS)
        if start is not None:
            points.append({"kind": "start", "x": _int(start.get("x")), "y": _int(start.get("y"))})
        for pt in wrap_polygon.findall("wp:lineTo", NS):
            points.append({"kind": "lineTo", "x": _int(pt.get("x")), "y": _int(pt.get("y"))})
    return _drop_empty({
        "relative_height": _int(container.get("relativeHeight")),
        "layout_in_cell": container.get("layoutInCell"),
        "locked": container.get("locked"),
        "hidden": container.get("hidden"),
        "simple_pos": {
            "x_emu": _int(simple.get("x")) if simple is not None else None,
            "y_emu": _int(simple.get("y")) if simple is not None else None,
        } if simple is not None else None,
        "effect_extent_emu": {
            side: _int(effect.get(side)) if effect is not None else None
            for side in ("l", "t", "r", "b")
        },
        "crop_percent_thousandths": {
            side: _int(src_rect.get(side)) if src_rect is not None else None
            for side in ("l", "t", "r", "b")
        } if src_rect is not None else None,
        "transform": {
            "rotation_60000_deg": _int(xfrm.get("rot")) if xfrm is not None else None,
            "rotation_deg": _round(_int(xfrm.get("rot")) / 60000.0, 4) if xfrm is not None and _int(xfrm.get("rot")) is not None else None,
            "flip_h": xfrm.get("flipH") if xfrm is not None else None,
            "flip_v": xfrm.get("flipV") if xfrm is not None else None,
        } if xfrm is not None else None,
        "wrap_geometry": {
            "type": wrap_node.tag.rsplit("}", 1)[-1] if wrap_node is not None else None,
            "attributes": dict(wrap_node.attrib) if wrap_node is not None else None,
            "polygon": points,
        } if wrap_node is not None else None,
    })

def _settings(settings_root: ET.Element | None) -> dict[str, Any]:
    if settings_root is None:
        return {}
    default_tab = _int(_simple_value(settings_root, "defaultTabStop"))
    hyphen_zone = _int(_simple_value(settings_root, "hyphenationZone"))
    compat_modes = []
    compat = _first(settings_root, "w:compat")
    if compat is not None:
        for setting in compat.findall("w:compatSetting", NS):
            compat_modes.append(_drop_empty({
                "name": _attr(setting, "w", "name"),
                "uri": _attr(setting, "w", "uri"),
                "value": _attr(setting, "w", "val"),
            }))
    return _drop_empty({
        "default_tab_stop_twips": default_tab,
        "default_tab_stop_mm": twips_to_mm(default_tab),
        "mirror_margins": _bool_value(_first(settings_root, "w:mirrorMargins")),
        "even_and_odd_headers": _bool_value(_first(settings_root, "w:evenAndOddHeaders")),
        "gutter_at_top": _bool_value(_first(settings_root, "w:gutterAtTop")),
        "auto_hyphenation": _bool_value(_first(settings_root, "w:autoHyphenation")),
        "do_not_hyphenate_caps": _bool_value(_first(settings_root, "w:doNotHyphenateCaps")),
        "consecutive_hyphen_limit": _int(_simple_value(settings_root, "consecutiveHyphenLimit")),
        "hyphenation_zone_twips": hyphen_zone,
        "hyphenation_zone_mm": twips_to_mm(hyphen_zone),
        "track_revisions": _bool_value(_first(settings_root, "w:trackRevisions")),
        "update_fields": _bool_value(_first(settings_root, "w:updateFields")),
        "compatibility": compat_modes,
    })


def _core_properties(core_root: ET.Element | None) -> dict[str, Any]:
    if core_root is None:
        return {}
    def value(path: str) -> str | None:
        node = core_root.find(path, NS)
        return (node.text or "").strip() if node is not None and node.text else None
    return _drop_empty({
        "title": value("dc:title"),
        "subject": value("dc:subject"),
        "creator": value("dc:creator"),
        "description": value("dc:description"),
        "last_modified_by": value("cp:lastModifiedBy"),
        "created": value("dcterms:created"),
        "modified": value("dcterms:modified"),
        "revision": value("cp:revision"),
        "keywords": value("cp:keywords"),
        "category": value("cp:category"),
    })


def _extended_properties(app_root: ET.Element | None) -> dict[str, Any]:
    if app_root is None:
        return {}
    def value(name: str) -> str | None:
        node = app_root.find(f"ep:{name}", NS)
        return (node.text or "").strip() if node is not None and node.text else None
    def number(name: str) -> int | None:
        return _int(value(name))
    return _drop_empty({
        "application": value("Application"),
        "app_version": value("AppVersion"),
        "cached_pages": number("Pages"),
        "words": number("Words"),
        "characters": number("Characters"),
        "characters_with_spaces": number("CharactersWithSpaces"),
        "lines": number("Lines"),
        "paragraphs": number("Paragraphs"),
        "company": value("Company"),
    })


def _notes_part(root: ET.Element | None, item_tag: str) -> list[dict[str, Any]]:
    if root is None:
        return []
    result = []
    for item in root.findall(f"w:{item_tag}", NS):
        item_id = _int(_attr(item, "w", "id"))
        if item_id is not None and item_id < 0:
            continue
        text = "\n".join(_paragraph_plain_text(p) for p in item.findall(".//w:p", NS)).strip()
        result.append(_drop_empty({"id": item_id, "text": text}))
    return result


def _headers_footers(
    archive: zipfile.ZipFile,
    relationships: dict[str, dict[str, str]],
    *,
    style_data: dict[str, Any],
    theme_fonts: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], set[str], set[tuple[str, str]]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    all_images: list[dict[str, Any]] = []
    used_fonts: set[str] = set()
    used_faces: set[tuple[str, str]] = set()
    for rel in relationships.values():
        rel_type = rel.get("type", "")
        if not (rel_type.endswith("/header") or rel_type.endswith("/footer")):
            continue
        part = rel.get("resolved_target")
        if not part or part in seen:
            continue
        seen.add(part)
        root = _xml(archive, part)
        if root is None:
            continue
        part_relationships = _relationships(archive, part)
        paragraphs, images, part_fonts, part_faces = _analyze_auxiliary_paragraphs(
            root,
            style_data=style_data,
            theme_fonts=theme_fonts,
            relationships=part_relationships,
        )
        all_images.extend(images)
        used_fonts.update(part_fonts)
        used_faces.update(part_faces)
        text = "\n".join(p.get("text", "") for p in paragraphs).strip()
        fields = [(_text(node) or "").strip() for node in root.findall(".//w:instrText", NS)]
        result.append(_drop_empty({
            "kind": "header" if rel_type.endswith("/header") else "footer",
            "part": part,
            "text": text,
            "field_instructions": [item for item in fields if item],
            "paragraph_count": len(paragraphs),
            "paragraphs": paragraphs,
            "relationship_count": len(part_relationships),
        }))
    return result, all_images, used_fonts, used_faces



def _font_style_from_props(effective_run: dict[str, Any]) -> str:
    bold = bool(effective_run.get("bold"))
    italic = bool(effective_run.get("italic"))
    if bold and italic:
        return "bold_italic"
    if bold:
        return "bold"
    if italic:
        return "italic"
    return "regular"


def _font_key(value: str) -> str:
    return "".join(ch.lower() for ch in str(value or "") if ch.isalnum())


def _audit_font_faces(requirements: Iterable[tuple[str, str]]) -> list[dict[str, Any]]:
    unique = sorted({(str(f).strip(), str(s).strip() or "regular") for f, s in requirements if str(f).strip()}, key=lambda x: (_font_key(x[0]), x[1]))
    try:
        from src.v4.font_availability import installed_fonts
        inventory = installed_fonts()
    except Exception:
        return [{"family": family, "style": style, "status": "non_verifiee"} for family, style in unique]

    result: list[dict[str, Any]] = []
    for family, style in unique:
        same_family = [item for item in inventory if _font_key(item.family) == _font_key(family)]
        exact = next((item for item in same_family if item.style == style), None)
        chosen = exact or (same_family[0] if same_family else None)
        result.append(_drop_empty({
            "family": family,
            "style": style,
            "status": "exact" if exact else "family_only" if same_family else "missing",
            "installed_family": chosen.family if chosen else None,
            "installed_style": chosen.style if chosen else None,
            "installed_path": chosen.path if chosen else None,
            "origin": chosen.origin if chosen else None,
        }))
    return result


def _analyze_auxiliary_paragraphs(
    root: ET.Element,
    *,
    style_data: dict[str, Any],
    theme_fonts: dict[str, Any],
    relationships: dict[str, dict[str, str]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], set[str], set[tuple[str, str]]]:
    paragraphs: list[dict[str, Any]] = []
    images: list[dict[str, Any]] = []
    used_fonts: set[str] = set()
    used_faces: set[tuple[str, str]] = set()
    for paragraph_index, paragraph in enumerate(root.findall(".//w:p", NS), start=1):
        direct_p = _parse_paragraph_props(_first(paragraph, "w:pPr"))
        effective_p, p_style_chain = _effective_paragraph_props(style_data, direct_p)
        runs = []
        para_text: list[str] = []
        for run_index, run in enumerate(paragraph.findall(".//w:r", NS), start=1):
            direct_r = _parse_run_props(_first(run, "w:rPr"))
            effective_r, char_style_chain = _effective_run_props(style_data, p_style_chain, direct_r)
            preferred_font = _preferred_font(effective_r, theme_fonts)
            if preferred_font:
                effective_r["resolved_font_family"] = preferred_font
            run_text, controls = _run_text(run)
            if preferred_font and (run_text or controls):
                used_fonts.add(preferred_font)
                used_faces.add((preferred_font, _font_style_from_props(effective_r)))
            para_text.append(run_text)
            run_images = _image_from_run(run, relationships, paragraph_index=paragraph_index, run_index=run_index)
            images.extend(run_images)
            runs.append(_drop_empty({
                "run": run_index,
                "text": run_text,
                "direct": direct_r,
                "effective": effective_r,
                "character_style_chain": char_style_chain,
                "controls": controls,
                "image_count": len(run_images),
            }))
        paragraphs.append(_drop_empty({
            "paragraph": paragraph_index,
            "text": "".join(para_text),
            "direct": direct_p,
            "effective": effective_p,
            "paragraph_style_chain": p_style_chain,
            "run_count": len(runs),
            "runs": runs,
        }))
    return paragraphs, images, used_fonts, used_faces


def _audit_fonts(families: Iterable[str]) -> list[dict[str, Any]]:
    unique = sorted({str(item).strip() for item in families if str(item).strip()}, key=str.casefold)
    try:
        from src.v4.font_availability import match_pdf_font
    except Exception:
        return [{"family": family, "status": "non_verifiee"} for family in unique]
    result = []
    for family in unique:
        try:
            match = match_pdf_font(family)
            result.append(_drop_empty({
                "family": family,
                "status": match.status,
                "installed_family": match.installed_family,
                "installed_style": match.installed_style,
                "installed_path": match.installed_path,
                "origin": match.installed_origin,
            }))
        except Exception as exc:
            result.append({"family": family, "status": "erreur_controle", "detail": str(exc)})
    return result


@dataclass(frozen=True, slots=True)
class DocxPhase1Result:
    source_path: str
    fingerprint: str
    model: dict[str, Any]

    @property
    def paragraph_count(self) -> int:
        return len(self.model.get("document", {}).get("paragraphs", []))

    @property
    def section_count(self) -> int:
        return len(self.model.get("document", {}).get("sections", []))


def analyze_docx_phase1(path: str | Path) -> DocxPhase1Result:
    source = Path(path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.suffix.lower() != ".docx":
        raise ValueError("La Phase 1 DOCX attend un fichier .docx.")

    with zipfile.ZipFile(source) as archive:
        document_root = _xml(archive, "word/document.xml", required=True)
        styles_root = _xml(archive, "word/styles.xml")
        numbering_root = _xml(archive, "word/numbering.xml")
        settings_root = _xml(archive, "word/settings.xml")
        font_root = _xml(archive, "word/fontTable.xml")
        theme_root = _xml(archive, "word/theme/theme1.xml")
        core_root = _xml(archive, "docProps/core.xml")
        app_root = _xml(archive, "docProps/app.xml")
        footnotes_root = _xml(archive, "word/footnotes.xml")
        endnotes_root = _xml(archive, "word/endnotes.xml")
        comments_root = _xml(archive, "word/comments.xml")

        relationships = _relationships(archive, "word/document.xml")
        style_data = _styles(styles_root)
        numbering = _numbering(numbering_root)
        theme_fonts = _theme_fonts(theme_root)

        body = _first(document_root, "w:body")
        if body is None:
            raise ValueError("DOCX sans corps w:body exploitable.")

        paragraphs: list[dict[str, Any]] = []
        images: list[dict[str, Any]] = []
        used_fonts: set[str] = set()
        used_faces: set[tuple[str, str]] = set()
        explicit_page_breaks = 0
        rendered_page_breaks = 0
        line_breaks = 0
        column_breaks = 0
        tab_count = 0
        field_instructions: list[str] = []
        hyperlink_ranges: list[dict[str, Any]] = []
        bookmark_markers: list[dict[str, Any]] = []
        tracked_change_ranges: list[dict[str, Any]] = []
        content_control_ranges: list[dict[str, Any]] = []
        section_markers: list[tuple[int, ET.Element]] = []

        for paragraph_index, paragraph in enumerate(body.iter(_q("w", "p")), start=1):
            ppr = _first(paragraph, "w:pPr")
            direct_p = _parse_paragraph_props(ppr)
            effective_p, p_style_chain = _effective_paragraph_props(style_data, direct_p)
            if effective_p.get("numbering"):
                effective_p["numbering"] = _resolved_numbering(numbering, effective_p.get("numbering"))

            runs = []
            para_text: list[str] = []
            for run_index, run in enumerate(paragraph.findall(".//w:r", NS), start=1):
                direct_r = _parse_run_props(_first(run, "w:rPr"))
                effective_r, char_style_chain = _effective_run_props(style_data, p_style_chain, direct_r)
                preferred_font = _preferred_font(effective_r, theme_fonts)
                if preferred_font:
                    effective_r["resolved_font_family"] = preferred_font

                run_text, controls = _run_text(run)
                if preferred_font and (run_text or controls):
                    used_fonts.add(preferred_font)
                    used_faces.add((preferred_font, _font_style_from_props(effective_r)))
                para_text.append(run_text)
                for control in controls:
                    kind = control.get("type")
                    if kind == "page_break":
                        explicit_page_breaks += 1
                    elif kind == "line_break":
                        line_breaks += 1
                    elif kind == "column_break":
                        column_breaks += 1
                    elif kind == "tab":
                        tab_count += 1
                    elif kind == "field_instruction" and control.get("value"):
                        field_instructions.append(str(control["value"]).strip())

                run_images = _image_from_run(
                    run,
                    relationships,
                    paragraph_index=paragraph_index,
                    run_index=run_index,
                )
                images.extend(run_images)

                runs.append(_drop_empty({
                    "run": run_index,
                    "text": run_text,
                    "direct": direct_r,
                    "effective": effective_r,
                    "character_style_chain": char_style_chain,
                    "controls": controls,
                    "image_count": len(run_images),
                }))

            structural = _paragraph_structural_ranges(paragraph, relationships, paragraph_index=paragraph_index)
            hyperlink_ranges.extend(structural["hyperlinks"])
            bookmark_markers.extend(structural["bookmark_markers"])
            tracked_change_ranges.extend(structural["tracked_changes"])
            content_control_ranges.extend(structural["content_controls"])

            rendered_page_breaks += len(paragraph.findall(".//w:lastRenderedPageBreak", NS))
            para_id = paragraph.get(_q("w14", "paraId"))
            text_id = paragraph.get(_q("w14", "textId"))
            sect = _first(ppr, "w:sectPr")
            if sect is not None:
                section_markers.append((paragraph_index, sect))

            paragraphs.append(_drop_empty({
                "paragraph": paragraph_index,
                "para_id": para_id,
                "text_id": text_id,
                "text": "".join(para_text),
                "direct": direct_p,
                "effective": effective_p,
                "paragraph_style_chain": p_style_chain,
                "run_count": len(runs),
                "runs": runs,
                "bookmark_names": [node.get(_q("w", "name")) for node in paragraph.findall(".//w:bookmarkStart", NS) if node.get(_q("w", "name"))],
            }))

        final_sect = _first(body, "w:sectPr")
        sections: list[dict[str, Any]] = []
        start_para = 1
        for section_index, (end_para, sect) in enumerate(section_markers, start=1):
            sections.append({
                "section": section_index,
                "start_paragraph": start_para,
                "end_paragraph": end_para,
                "properties": _section_props(sect, relationships),
            })
            start_para = end_para + 1
        if final_sect is not None:
            sections.append({
                "section": len(sections) + 1,
                "start_paragraph": start_para,
                "end_paragraph": len(paragraphs),
                "properties": _section_props(final_sect, relationships),
            })
        if not sections:
            sections.append({
                "section": 1,
                "start_paragraph": 1,
                "end_paragraph": len(paragraphs),
                "properties": {},
            })

        tables = [_table_props(table, index) for index, table in enumerate(body.iter(_q("w", "tbl")), start=1)]
        font_table = _font_table(font_root)
        media_parts = []
        for info in archive.infolist():
            if info.filename.startswith("word/media/") and not info.is_dir():
                media_parts.append({
                    "part": info.filename,
                    "compressed_bytes": info.compress_size,
                    "uncompressed_bytes": info.file_size,
                })

        comments = _notes_part(comments_root, "comment")
        footnotes = _notes_part(footnotes_root, "footnote")
        endnotes = _notes_part(endnotes_root, "endnote")
        headers_footers, header_footer_images, header_footer_fonts, header_footer_faces = _headers_footers(
            archive, relationships, style_data=style_data, theme_fonts=theme_fonts
        )
        images.extend(header_footer_images)
        used_fonts.update(header_footer_fonts)
        used_faces.update(header_footer_faces)

        tracked = {
            "insertions": len(document_root.findall(".//w:ins", NS)),
            "deletions": len(document_root.findall(".//w:del", NS)),
            "moves_from": len(document_root.findall(".//w:moveFrom", NS)),
            "moves_to": len(document_root.findall(".//w:moveTo", NS)),
        }
        content_controls = len(document_root.findall(".//w:sdt", NS))
        hyperlinks = len(document_root.findall(".//w:hyperlink", NS))
        bookmarks = len(document_root.findall(".//w:bookmarkStart", NS))
        bookmark_ranges = _pair_bookmarks(bookmark_markers)

        core = _core_properties(core_root)
        extended = _extended_properties(app_root)
        settings = _settings(settings_root)
        font_audit = _audit_fonts(used_fonts)
        missing_fonts = [item["family"] for item in font_audit if item.get("status") == "missing"]
        face_audit = _audit_font_faces(used_faces)
        missing_faces = [f"{item.get('family')} ({item.get('style')})" for item in face_audit if item.get("status") == "missing"]

        package_parts = sorted(info.filename for info in archive.infolist() if not info.is_dir())

        model = {
            "schema": PHASE1_SCHEMA,
            "schema_version": PHASE1_VERSION,
            "engine": {"name": ENGINE_NAME, "version": ENGINE_VERSION},
            "source": {
                "name": source.name,
                "path": str(source),
                "size_bytes": source.stat().st_size,
                "sha256": _sha256(source),
                "file_type": "docx",
            },
            "unit_contract": {
                "word_twip": "1/1440 inch",
                "word_half_point": "1/2 pt",
                "drawing_emu": "1/914400 inch",
                "conversions": {
                    "1440_twips_mm": twips_to_mm(1440),
                    "720_twips_pt": twips_to_pt(720),
                    "21_half_points_pt": half_points_to_pt(21),
                    "914400_emu_mm": emu_to_mm(914400),
                },
                "line_multiple_rule": "w:spacing/@w:line / 240 quand lineRule=auto",
            },
            "package": {
                "part_count": len(package_parts),
                "parts": package_parts,
                "main_relationships": list(relationships.values()),
                "media_parts": media_parts,
            },
            "properties": {
                "core": core,
                "extended": extended,
                "cached_page_count_is_authoring_metadata_only": True,
            },
            "document": {
                "paragraph_count": len(paragraphs),
                "paragraphs": paragraphs,
                "section_count": len(sections),
                "sections": sections,
                "table_count": len(tables),
                "tables": tables,
                "placed_image_count": len(images),
                "images": images,
                "explicit_page_break_count": explicit_page_breaks,
                "last_rendered_page_break_count": rendered_page_breaks,
                "line_break_count": line_breaks,
                "column_break_count": column_breaks,
                "tab_count": tab_count,
                "field_instructions": [item for item in field_instructions if item],
                "hyperlink_count": hyperlinks,
                "hyperlinks": hyperlink_ranges,
                "bookmark_count": bookmarks,
                "bookmarks": bookmark_ranges,
                "content_control_count": content_controls,
                "content_controls": content_control_ranges,
                "tracked_changes": tracked,
                "tracked_change_ranges": tracked_change_ranges,
                "headers_footers": headers_footers,
                "footnotes": footnotes,
                "endnotes": endnotes,
                "comments": comments,
            },
            "styles": style_data,
            "numbering": numbering,
            "fonts": {
                "theme": theme_fonts,
                "font_table": font_table,
                "used_families": sorted(used_fonts, key=str.casefold),
                "used_faces": [{"family": family, "style": style} for family, style in sorted(used_faces, key=lambda item: (_font_key(item[0]), item[1]))],
                "availability": font_audit,
                "face_availability": face_audit,
                "missing_families": missing_fonts,
                "missing_faces": missing_faces,
            },
            "settings": settings,
            "future_editorial_support": {
                "status": "facts_only_no_rule_applied",
                "captured_for_later": [
                    "paragraph_and_run_boundaries",
                    "direct_and_inherited_typography",
                    "paragraph_spacing_and_indents",
                    "keep_next_keep_lines_widow_control",
                    "page_and_section_breaks",
                    "list_numbering_and_levels",
                    "tabs_and_field_instructions",
                    "tables_and_cells_basic_geometry",
                    "images_inline_or_floating_and_anchors",
                    "section_format_margins_columns_and_document_grid",
                    "header_footer_paragraphs_runs_and_fields",
                    "notes_comments_ids_and_text",
                    "font_family_and_face_requirements",
                    "hyperlink_targets_and_ranges",
                    "bookmark_exact_ranges",
                    "content_control_metadata_and_ranges",
                    "tracked_change_metadata_and_ranges",
                    "advanced_table_borders_shading_cell_margins",
                    "advanced_drawing_crop_rotation_and_wrap_geometry",
                ],
                "inventoried_but_not_fully_normalized": [],
            },
            "warnings": [],
        }

        if extended.get("cached_pages") is not None:
            model["warnings"].append(
                "Le nombre de pages des propriétés Word est conservé comme métadonnée de contrôle, jamais comme pagination TomeLinea."
            )
        if missing_fonts:
            model["warnings"].append(
                "Police(s) requise(s) absente(s) du système/bibliothèque TomeLinea : " + ", ".join(missing_fonts)
            )
        if any(tracked.values()):
            model["warnings"].append(
                "Le DOCX contient des modifications suivies ; elles sont inventoriées mais aucune décision n'est prise en Phase 1."
            )

    return DocxPhase1Result(
        source_path=str(source),
        fingerprint=model["source"]["sha256"],
        model=model,
    )
