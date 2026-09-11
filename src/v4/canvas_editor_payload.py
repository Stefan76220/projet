from __future__ import annotations

"""TomeLinea V4 — Phase 2.4 : contrat TL -> @hufe921/canvas-editor.

Le module fabrique uniquement les données d'entrée de Canvas Editor.
Aucun WebView, aucun rendu et aucune pagination TomeLinea ne sont exécutés ici.
Canvas Editor reste propriétaire des retours à la ligne et de la pagination.
"""

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any
import base64
import mimetypes
import zipfile

from src.v4.canvas_contract import CANVAS_SCHEMA

ENGINE_NAME = "tomelinea.canvas_editor_payload"
ENGINE_VERSION = "1"
PAYLOAD_SCHEMA = "tomelinea-canvas-editor-payload"
PAYLOAD_SCHEMA_VERSION = 1
PX_PER_MM = 96.0 / 25.4
PX_PER_PT = 96.0 / 72.0

# Canvas Editor ne protège un mot que pour les caractères déclarés dans
# ``letterClass``. Sa valeur par défaut est limitée à A-Z/a-z : les accents
# français étaient donc vus comme des frontières de mot (ex. familiè/re,
# faç/ades, dé/cision). Les apostrophes font aussi partie du mot typographique
# français pour empêcher une coupure après « l’ », « d’ », etc.
FRENCH_LETTER_CLASS = (
    "A-Za-z"
    "ÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸ"
    "àâäçéèêëîïôöùûüÿ"
    "ŒœÆæ"
    "’'"
)


def mm_to_px(value: Any) -> float | None:
    if not isinstance(value, (int, float)):
        return None
    return round(float(value) * PX_PER_MM, 4)


def pt_to_px(value: Any) -> float | None:
    if not isinstance(value, (int, float)):
        return None
    return round(float(value) * PX_PER_PT, 4)


def _hex_color(value: Any) -> str | None:
    raw = str(value or "").strip()
    if not raw:
        return None
    if raw.startswith("#"):
        return raw
    if len(raw) in {3, 6, 8} and all(ch in "0123456789abcdefABCDEF" for ch in raw):
        return "#" + raw
    return raw


def _row_flex(value: Any) -> str | None:
    raw = str(value or "").strip().lower()
    # Canvas Editor distingue :
    # - "alignment" = justification classique (équivalent Word "both")
    # - "justify"   = justification distribuée, qui espace aussi les caractères.
    # Le mapping précédent envoyait la justification Word vers "justify" et
    # provoquait l'étirement visible lettre par lettre.
    return {
        "both": "alignment",
        "justify": "alignment",
        "justify_distributed": "justify",
        "distributed": "justify",
        "distribute": "justify",
        "start": "left",
        "end": "right",
    }.get(raw, raw or None)


def _section_for_paragraph(sections: list[dict[str, Any]], paragraph: int) -> int:
    for index, section in enumerate(sections):
        span = section.get("paragraph_range", {})
        start = int(span.get("start") or 0)
        end = int(span.get("end") or 0)
        if start <= paragraph <= end:
            return index
    return max(0, len(sections) - 1)


def _split_content_by_section(contract: dict[str, Any]) -> list[list[dict[str, Any]]]:
    sections = contract.get("sections", [])
    result = [[] for _ in sections]
    current = 0
    for block in contract.get("content", []):
        if block.get("kind") == "paragraph":
            paragraph = int(block.get("source_paragraph") or 0)
            current = _section_for_paragraph(sections, paragraph)
        if result:
            result[current].append(block)
    return result


def _read_media_data_uri(source: Path, part: str, cache: dict[str, str]) -> str:
    if part in cache:
        return cache[part]
    with zipfile.ZipFile(source, "r") as archive:
        raw = archive.read(part)
    mime = mimetypes.guess_type(part)[0] or "application/octet-stream"
    uri = f"data:{mime};base64,{base64.b64encode(raw).decode('ascii')}"
    cache[part] = uri
    return uri


def _character_element(run: dict[str, Any], text: str) -> dict[str, Any]:
    fmt = run.get("character_format", {})
    item: dict[str, Any] = {
        "value": text,
        "extension": {
            "tomelinea": {
                "sourceRun": run.get("source_run"),
                "sourceTrace": deepcopy(run.get("source_trace", {})),
            }
        },
    }
    if fmt.get("font_family"):
        item["font"] = fmt["font_family"]
    size = pt_to_px(fmt.get("size_pt"))
    if size is not None:
        item["size"] = size
    if fmt.get("bold"):
        item["bold"] = True
    if fmt.get("italic"):
        item["italic"] = True
    if fmt.get("underline"):
        item["underline"] = True
    color = _hex_color(fmt.get("color"))
    if color:
        item["color"] = color
    return item


def _paragraph_row_style(block: dict[str, Any]) -> dict[str, Any]:
    fmt = block.get("paragraph_format", {})
    result: dict[str, Any] = {}
    align = _row_flex(fmt.get("alignment"))
    if align:
        result["rowFlex"] = align
    line = fmt.get("line_spacing", {})
    if line.get("mode") == "multiple" and isinstance(line.get("value"), (int, float)):
        result["rowMargin"] = float(line["value"])
    return result


def _list_meta(block: dict[str, Any]) -> tuple[str, str, int] | None:
    numbering = block.get("paragraph_format", {}).get("numbering")
    if not isinstance(numbering, dict):
        return None
    fmt = str(numbering.get("format") or "").lower()
    list_type = "ul" if fmt == "bullet" else "ol"
    list_style = "disc" if list_type == "ul" else "decimal"
    indent = numbering.get("paragraph", {}).get("indent", {})
    left_mm = float(indent.get("left_mm") or 0.0)
    # Le fixture utilise 6,35 mm par niveau. Le niveau est metadata Canvas Editor,
    # pas un calcul de position de ligne.
    level = max(0, int(round(left_mm / 6.35)) - 1) if left_mm else 0
    return list_type, list_style, level


def _image_element(
    image: dict[str, Any],
    *,
    source: Path,
    media_cache: dict[str, str],
    anchor_text: str = "",
) -> dict[str, Any]:
    part = str(image.get("part") or "")
    tl_extension = deepcopy(image)
    item: dict[str, Any] = {
        "type": "image",
        "value": _read_media_data_uri(source, part, media_cache),
        "width": mm_to_px(image.get("width_mm")),
        "height": mm_to_px(image.get("height_mm")),
        "extension": {"tomelinea": tl_extension},
    }
    if image.get("mode") == "floating":
        # Phase 2.14 : premier calcul en ligne, puis conversion en flottant
        # APRES que Canvas Editor ait calculé la position réelle du paragraphe
        # d'ancrage. TomeLinea traduit seulement la relation OOXML + les offsets.
        paragraph_index = int(image.get("paragraph_index") or 0)
        run_index = int(image.get("run_index") or 0)
        image_id = f"tl-float-p{paragraph_index}-r{run_index}"
        item["id"] = image_id
        item["imgDisplay"] = "inline"
        tl_extension["floating_request"] = {
            "image_id": image_id,
            "anchor_text": str(anchor_text or ""),
            "paragraph_index": paragraph_index,
            "horizontal_relative_to": image.get("position_h_relative_to"),
            "horizontal_offset_px": mm_to_px(image.get("position_h_offset_mm")),
            "vertical_relative_to": image.get("position_v_relative_to"),
            "vertical_offset_px": mm_to_px(image.get("position_v_offset_mm")),
            "target_display": "surround",
        }
    else:
        item["imgDisplay"] = "inline"
    return item


def _translate_paragraph(
    block: dict[str, Any],
    *,
    source: Path,
    media_cache: dict[str, str],
) -> list[dict[str, Any]]:
    row_style = _paragraph_row_style(block)
    list_info = _list_meta(block)
    body: list[dict[str, Any]] = []

    for run in block.get("runs", []):
        text = str(run.get("text") or "")
        controls = list(run.get("controls", []))

        # Les contrôles sont injectés dans l'ordre connu du run. Le texte Phase 1
        # contient déjà \t / \n pour tab et saut de ligne ; on ne les duplique pas.
        plain = text.replace("\t", "").replace("\n", "")
        if plain:
            body.append(_character_element(run, plain))

        for control in controls:
            kind = str(control.get("type") or "")
            if kind == "tab":
                body.append({"type": "tab", "value": "", "extension": {"tomelinea": deepcopy(control)}})
            elif kind == "line_break":
                body.append({"value": "\n", "extension": {"tomelinea": deepcopy(control)}})
            elif kind == "page_break":
                body.append({
                    "type": "pageBreak",
                    # Canvas Editor utilise WRAP ("\n") pour un vrai saut de page.
                    # Une valeur vide n'affiche que le marqueur sans forcer la page suivante.
                    "value": "\n",
                    "extension": {"tomelinea": deepcopy(control)},
                })

        for image in run.get("images", []):
            body.append(_image_element(image, source=source, media_cache=media_cache, anchor_text=str(block.get("text") or "")))

    if not body and block.get("text"):
        body.append({"value": str(block.get("text"))})

    # Applique les propriétés de ligne à chaque élément de la ligne afin que le
    # moteur Canvas Editor puisse les reprendre sans coordonnées manuelles.
    for item in body:
        for key, value in row_style.items():
            item.setdefault(key, value)
        ext = item.setdefault("extension", {}).setdefault("tomelinea", {})
        ext.setdefault("paragraph", {
            "id": block.get("id"),
            "sourceParagraph": block.get("source_paragraph"),
            "format": deepcopy(block.get("paragraph_format", {})),
            "styleChain": deepcopy(block.get("style_chain", [])),
        })

    if list_info:
        list_type, list_style, list_level = list_info
        list_id = f"tl-list-{block.get('paragraph_format', {}).get('numbering', {}).get('num_id', 'x')}"
        return [{
            "type": "list",
            "value": "",
            "valueList": body or [{"value": ""}],
            "listType": list_type,
            "listStyle": list_style,
            "listId": list_id,
            "listLevel": list_level,
            "extension": {
                "tomelinea": {
                    "paragraph": block.get("source_paragraph"),
                    "numbering": deepcopy(block.get("paragraph_format", {}).get("numbering")),
                }
            },
        }]

    body.append({
        "value": "\n",
        **row_style,
        "extension": {
            "tomelinea": {
                "paragraphEnd": block.get("source_paragraph"),
                "format": deepcopy(block.get("paragraph_format", {})),
            }
        },
    })
    return body


def _cell_value(text: str) -> list[dict[str, Any]]:
    return [{"value": str(text or "")}, {"value": "\n"}]


def _translate_table(block: dict[str, Any]) -> dict[str, Any]:
    grid = block.get("table_format", {}).get("grid", [])
    colgroup = [{"width": mm_to_px(item.get("width_mm")) or 0.0} for item in grid]
    rows = []
    source_table = int(block.get("source_table") or 0)
    table_id = f"tl-table-{source_table or str(block.get('id') or 'x').replace(':', '-')}"
    for row in block.get("rows", []):
        cells = []
        for cell in row.get("cells", []):
            shading = cell.get("shading", {}) if isinstance(cell.get("shading"), dict) else {}
            td: dict[str, Any] = {
                "colspan": int(cell.get("grid_span") or 1),
                "rowspan": 1,
                "value": _cell_value(cell.get("text", "")),
                "extension": {"tomelinea": deepcopy(cell)},
            }
            fill = shading.get("fill")
            if fill and str(fill).lower() not in {"auto", "none"}:
                td["backgroundColor"] = _hex_color(fill)
            valign = str(cell.get("vertical_align") or "").lower()
            if valign in {"top", "center", "bottom"}:
                td["verticalAlign"] = valign
            cells.append(td)
        rows.append({"height": 0, "tdList": cells, "extension": {"tomelinea": {"sourceRow": row.get("row")}}})
    tl_meta = deepcopy(block)
    tl_meta["table_pagination_policy"] = {
        "enabled": True,
        "table_id": table_id,
        "automatic_fix": "move_table_start_if_first_row_isolated",
        "otherwise": "editorial_decision_required",
    }
    return {
        "id": table_id,
        "type": "table",
        "value": "",
        "colgroup": colgroup,
        "trList": rows,
        "extension": {"tomelinea": tl_meta},
    }


def _translate_header_footer(
    entry: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    if not entry:
        return []
    result: list[dict[str, Any]] = []
    for paragraph in entry.get("paragraphs", []):
        effective = paragraph.get("effective", {})
        row = _row_flex(effective.get("alignment"))
        for run in paragraph.get("runs", []):
            fmt = run.get("effective", {})
            fonts = fmt.get("fonts", {}) if isinstance(fmt.get("fonts"), dict) else {}
            item: dict[str, Any] = {
                "value": str(run.get("text") or ""),
                "font": fmt.get("resolved_font_family") or fonts.get("ascii") or fonts.get("hansi"),
                "size": pt_to_px(fmt.get("size_pt")),
            }
            if fmt.get("bold"):
                item["bold"] = True
            if fmt.get("italic"):
                item["italic"] = True
            if row:
                item["rowFlex"] = row
            result.append({k: v for k, v in item.items() if v is not None})
        result.append({"value": "\n", **({"rowFlex": row} if row else {})})
    return result


def _page_number_from_footer(
    entry: dict[str, Any] | None,
    *,
    footer_bottom_mm: Any,
) -> tuple[list[dict[str, Any]], dict[str, Any] | None]:
    """Traduit un pied simple contenant le champ Word PAGE.

    Canvas Editor possède un moteur natif de numérotation. Utiliser ce moteur
    évite de transformer le champ PAGE en deux fragments visuels superposés
    ("Page" puis le numéro sur la ligne suivante).
    """
    if not entry:
        return [], None

    paragraphs = list(entry.get("paragraphs", []))
    if len(paragraphs) != 1:
        return _translate_header_footer(entry), None

    paragraph = paragraphs[0]
    runs = list(paragraph.get("runs", []))
    has_page = False
    format_parts: list[str] = []
    style_run: dict[str, Any] | None = None

    for run in runs:
        text = str(run.get("text") or "")
        if text:
            format_parts.append(text)
            if style_run is None:
                style_run = run
        controls = list(run.get("controls", []))
        is_page_field = any(
            str(control.get("type") or "") == "field_instruction"
            and str(control.get("value") or "").strip().upper() == "PAGE"
            for control in controls
        )
        if is_page_field:
            has_page = True
            format_parts.append("{pageNo}")
            if style_run is None:
                style_run = run

    if not has_page:
        return _translate_header_footer(entry), None

    effective = paragraph.get("effective", {})
    row = _row_flex(effective.get("alignment")) or "center"
    run_fmt = (style_run or {}).get("effective", {})
    fonts = run_fmt.get("fonts", {}) if isinstance(run_fmt.get("fonts"), dict) else {}
    size = pt_to_px(run_fmt.get("size_pt")) or 12.0
    font = run_fmt.get("resolved_font_family") or fonts.get("ascii") or fonts.get("hansi") or "Arial"
    bottom = mm_to_px(footer_bottom_mm)

    page_number = {
        "disabled": False,
        "format": "".join(format_parts) or "{pageNo}",
        "rowFlex": row,
        "font": font,
        "size": size,
        "bottom": bottom if bottom is not None else 30.0,
    }
    # Le paragraphe du footer est entièrement remplacé par le moteur natif de
    # pageNumber pour ne pas afficher deux fois le libellé.
    return [], page_number


def _header_footer_for_section(
    contract: dict[str, Any],
    section: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, Any] | None]:
    by_part = {item.get("part"): item for item in contract.get("annotations", {}).get("headers_footers", [])}
    header = None
    footer = None
    for ref in section.get("header_footer_references", []):
        item = by_part.get(ref.get("part"))
        if ref.get("kind") == "header" and header is None:
            header = item
        elif ref.get("kind") == "footer" and footer is None:
            footer = item

    footer_mm = section.get("page_setup", {}).get("margins_mm", {}).get("footer")
    footer_data, page_number = _page_number_from_footer(footer, footer_bottom_mm=footer_mm)
    return _translate_header_footer(header), footer_data, page_number


def _options_for_section(
    section: dict[str, Any],
    default_font: str,
    default_size: float,
    page_number: dict[str, Any] | None = None,
) -> dict[str, Any]:
    setup = section.get("page_setup", {})
    margins = setup.get("margins_mm", {})
    columns = setup.get("columns", {})
    width = mm_to_px(setup.get("width_mm"))
    height = mm_to_px(setup.get("height_mm"))
    options = {
        "mode": "edit",
        "defaultFont": default_font,
        "defaultSize": default_size,
        "width": width,
        "height": height,
        "margins": [
            mm_to_px(margins.get("top")) or 0.0,
            mm_to_px(margins.get("right")) or 0.0,
            mm_to_px(margins.get("bottom")) or 0.0,
            mm_to_px(margins.get("left")) or 0.0,
        ],
        "pageMode": "paging",
        "paperDirection": "horizontal" if setup.get("orientation") == "landscape" else "vertical",
        "scale": 1,
        "wordBreak": "break-word",
        "letterClass": [FRENCH_LETTER_CLASS],
        "column": {
            "count": int(columns.get("count") or 1),
            "gap": mm_to_px(columns.get("gap_mm")) or 0.0,
        },
    }
    if page_number:
        options["pageNumber"] = deepcopy(page_number)
    return options


def _default_text_style(contract: dict[str, Any]) -> tuple[str, float]:
    for block in contract.get("content", []):
        if block.get("kind") != "paragraph":
            continue
        for run in block.get("runs", []):
            fmt = run.get("character_format", {})
            family = str(fmt.get("font_family") or "").strip()
            size = pt_to_px(fmt.get("size_pt"))
            if family and size:
                return family, size
    return "Arial", 16.0


@dataclass(frozen=True, slots=True)
class CanvasEditorPayloadResult:
    payload: dict[str, Any]
    valid: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]


def build_canvas_editor_payload(contract: dict[str, Any]) -> CanvasEditorPayloadResult:
    if contract.get("schema") != CANVAS_SCHEMA:
        raise ValueError(f"Contrat TL Canvas inattendu : {contract.get('schema')!r}")
    if not contract.get("readiness", {}).get("valid_contract"):
        raise ValueError("Le contrat TL Canvas n'est pas valide.")

    sections = contract.get("sections", [])
    content_by_section = _split_content_by_section(contract)
    source = Path(str(contract.get("source", {}).get("path") or "")).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"DOCX source introuvable : {source}")

    default_font, default_size = _default_text_style(contract)
    media_cache: dict[str, str] = {}
    section_payloads = []
    errors: list[str] = []
    warnings: list[str] = []

    translated_counts = {"paragraphs": 0, "tables": 0, "images": 0, "page_breaks": 0, "lists": 0}

    for index, section in enumerate(sections):
        main: list[dict[str, Any]] = []
        for block in content_by_section[index]:
            if block.get("kind") == "paragraph":
                items = _translate_paragraph(block, source=source, media_cache=media_cache)
                main.extend(items)
                translated_counts["paragraphs"] += 1
                translated_counts["images"] += sum(1 for item in items if item.get("type") == "image")
                translated_counts["page_breaks"] += sum(1 for item in items if item.get("type") == "pageBreak")
                translated_counts["lists"] += sum(1 for item in items if item.get("type") == "list")
            elif block.get("kind") == "table":
                main.append(_translate_table(block))
                translated_counts["tables"] += 1
            else:
                errors.append(f"Bloc Phase 2.4 non traduit : {block.get('kind')!r}")

        header, footer, page_number = _header_footer_for_section(contract, section)
        section_payloads.append({
            "section": section.get("section"),
            "paragraphRange": deepcopy(section.get("paragraph_range", {})),
            "data": {"header": header, "main": main, "footer": footer},
            "options": _options_for_section(section, default_font, default_size, page_number),
            "source": deepcopy(section.get("source_trace", {})),
        })

    expected = contract.get("coverage", {})
    for key in ("paragraphs", "tables", "images"):
        if translated_counts[key] != int(expected.get(key, translated_counts[key])):
            errors.append(f"Couverture {key}: {translated_counts[key]} / {expected.get(key)}")

    # Canvas Editor a des options de page globales. Pour conserver les sections
    # Word hétérogènes (portrait/paysage/colonnes), TL les remet donc comme
    # segments Canvas distincts dans un seul document logique TomeLinea.
    if len(section_payloads) > 1:
        warnings.append("sections_canvas_segmentees")

    deferred = {
        "paragraph_spacing_before_after": True,
        "paragraph_first_line_and_hanging_indent": True,
        "keep_next_keep_lines_widow_control": True,
        "tracked_changes_visualization": True,
        "content_controls_interaction": True,
        "comments_visualization": True,
    }

    payload = {
        "schema": PAYLOAD_SCHEMA,
        "schema_version": PAYLOAD_SCHEMA_VERSION,
        "engine": {"name": ENGINE_NAME, "version": ENGINE_VERSION},
        "target": {
            "package": "@hufe921/canvas-editor",
            "page_mode": "paging",
            "pagination_owner": "canvas-editor",
            "line_break_owner": "canvas-editor",
        },
        "source": deepcopy(contract.get("source", {})),
        "sections": section_payloads,
        "translated_counts": translated_counts,
        "preserved_metadata": deepcopy(contract.get("annotations", {})),
        "deferred_visual_properties": deferred,
        "readiness": {
            "payload_valid": not errors,
            "webview_created": False,
            "editor_created": False,
            "render_started": False,
            "errors": list(errors),
            "warnings": list(warnings),
        },
    }
    return CanvasEditorPayloadResult(
        payload=payload,
        valid=not errors,
        errors=tuple(errors),
        warnings=tuple(warnings),
    )
