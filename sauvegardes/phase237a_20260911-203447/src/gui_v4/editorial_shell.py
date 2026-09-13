from __future__ import annotations

"""
TomeLinea V4 — habillage éditorial.

IMPORTANT :
ce module ne contient aucune logique métier.

Il habille TomeLineaV4 sans :
- créer de Livre ;
- choisir un type de livre ;
- modifier Source / Analyse / Structure ;
- importer gui_v3 ;
- toucher au Visionneur.

La logique reste dans src.gui_v4.app.TomeLineaV4.
"""

from pathlib import Path
import base64
import hashlib
import queue
import threading
import ctypes
from ctypes import wintypes
import re
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import zipfile
import xml.etree.ElementTree as ET

from PIL import (
    Image,
    ImageColor,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageTk,
)

from src.gui_v4 import theme

# Le moteur Phase 2.35 doit toujours utiliser le runtime tkwry/WebView2
# embarque par TomeLinea. Sans ceci, un ancien tkwry installe dans Python
# peut etre importe en premier et rester en cache dans sys.modules.
_TL_RUNTIME_PYTHON = Path(__file__).resolve().parents[2] / "runtime" / "python"
if _TL_RUNTIME_PYTHON.is_dir():
    _tl_runtime_value = str(_TL_RUNTIME_PYTHON)
    if _tl_runtime_value not in sys.path:
        sys.path.insert(0, _tl_runtime_value)

from src.gui_v4.canvas_page_host import TLCanvasPageHost
from src.gui_v4.canvas_editor_host import CanvasEditorWebHost
from src.v4.canvas_loading import prepare_canvas_load
from src.v4.canvas_editor_payload import build_canvas_editor_payload
from src.v4.canvas_editor_document import build_canvas_editor_document
from src.v4.source_phase2 import Phase2BlockedError
from src.v4.editorial_persistence import (
    load_editorial_state,
    persisted_choices_for_plan,
    record_editorial_choice,
)
from src.gui_v4.app import (
    TomeLineaV4 as TomeLineaV4Logic,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

BACKGROUND_HOME = (
    PROJECT_ROOT
    / "assets"
    / "interface"
    / "backgrounds"
    / "editorial_bg_accueil.png"
)

BACKGROUND_SOFT = (
    PROJECT_ROOT
    / "assets"
    / "interface"
    / "backgrounds"
    / "editorial_bg_soft.png"
)

VISIBILITY_ROOT = (
    PROJECT_ROOT
    / "assets"
    / "branding"
    / "tomelinea"
    / "logo_pack_visibilite"
)

BRAND_ICON = (
    VISIBILITY_ROOT
    / "TomeLinea_512x512.png"
)

BRAND_TITLE = (
    VISIBILITY_ROOT
    / "TomeLinea_titre_relief.png"
)




# ==============================================================
# DOCUMENT DOCX INTERNE + MICROSOFT RICH EDIT
# ==============================================================

_TL_W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
_TL_W = {"w": _TL_W_NS}


def _tl_w(name: str) -> str:
    return f"{{{_TL_W_NS}}}{name}"


def _tl_ooxml_val(node, name: str = "val", default=None):
    if node is None:
        return default
    return node.get(_tl_w(name), default)


def _tl_onoff(node, default: bool = False) -> bool:
    if node is None:
        return default
    raw = str(_tl_ooxml_val(node, default="1") or "1").strip().lower()
    return raw not in {"0", "false", "off", "no"}


def _tl_int(value, default=0):
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return int(default)


def _tl_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _tl_merge_dict(base: dict, extra: dict) -> dict:
    result = dict(base or {})
    for key, value in (extra or {}).items():
        if value is not None:
            result[key] = value
    return result


def _tl_read_rpr(node) -> dict:
    if node is None:
        return {}

    result = {}

    fonts = node.find("w:rFonts", _TL_W)
    if fonts is not None:
        for attr in ("ascii", "hAnsi", "eastAsia", "cs"):
            value = _tl_ooxml_val(fonts, attr, None)
            if value:
                result["font"] = str(value)
                break

    size = node.find("w:sz", _TL_W)
    if size is not None:
        raw = _tl_ooxml_val(size, default=None)
        if raw is not None:
            result["size_half_points"] = max(1, _tl_int(raw, 22))

    bold = node.find("w:b", _TL_W)
    if bold is not None:
        result["bold"] = _tl_onoff(bold, True)

    italic = node.find("w:i", _TL_W)
    if italic is not None:
        result["italic"] = _tl_onoff(italic, True)

    underline = node.find("w:u", _TL_W)
    if underline is not None:
        value = str(_tl_ooxml_val(underline, default="single") or "single").lower()
        result["underline"] = value not in {"none", "0", "false"}

    color = node.find("w:color", _TL_W)
    if color is not None:
        value = str(_tl_ooxml_val(color, default="") or "").strip().upper()
        if re.fullmatch(r"[0-9A-F]{6}", value):
            result["color"] = value

    return result


def _tl_read_ppr(node) -> dict:
    if node is None:
        return {}

    result = {}

    align = node.find("w:jc", _TL_W)
    if align is not None:
        value = str(_tl_ooxml_val(align, default="") or "").lower()
        align_map = {
            "left": "left",
            "start": "left",
            "center": "center",
            "right": "right",
            "end": "right",
            "both": "justify",
            "distribute": "justify",
        }
        if value in align_map:
            result["align"] = align_map[value]

    ind = node.find("w:ind", _TL_W)
    if ind is not None:
        left = _tl_ooxml_val(ind, "left", None)
        if left is None:
            left = _tl_ooxml_val(ind, "start", None)
        right = _tl_ooxml_val(ind, "right", None)
        if right is None:
            right = _tl_ooxml_val(ind, "end", None)
        first = _tl_ooxml_val(ind, "firstLine", None)
        hanging = _tl_ooxml_val(ind, "hanging", None)

        if left is not None:
            result["left_twips"] = _tl_int(left)
        if right is not None:
            result["right_twips"] = _tl_int(right)
        if first is not None:
            result["first_twips"] = _tl_int(first)
        elif hanging is not None:
            result["first_twips"] = -abs(_tl_int(hanging))

    spacing = node.find("w:spacing", _TL_W)
    if spacing is not None:
        before = _tl_ooxml_val(spacing, "before", None)
        after = _tl_ooxml_val(spacing, "after", None)
        line = _tl_ooxml_val(spacing, "line", None)
        line_rule = str(_tl_ooxml_val(spacing, "lineRule", "") or "").lower()

        if before is not None:
            result["before_twips"] = _tl_int(before)
        if after is not None:
            result["after_twips"] = _tl_int(after)
        if line is not None:
            result["line"] = _tl_int(line)
            result["line_rule"] = line_rule

    if node.find("w:pageBreakBefore", _TL_W) is not None:
        result["page_break_before"] = _tl_onoff(
            node.find("w:pageBreakBefore", _TL_W),
            True,
        )

    return result


def _tl_parse_styles(styles_root):
    styles = {}

    default_p = {}
    default_r = {}

    if styles_root is not None:
        p_default = styles_root.find(
            ".//w:docDefaults/w:pPrDefault/w:pPr",
            _TL_W,
        )
        r_default = styles_root.find(
            ".//w:docDefaults/w:rPrDefault/w:rPr",
            _TL_W,
        )
        default_p = _tl_read_ppr(p_default)
        default_r = _tl_read_rpr(r_default)

        for style in styles_root.findall("w:style", _TL_W):
            style_id = str(style.get(_tl_w("styleId"), "") or "")
            if not style_id:
                continue
            based_on = style.find("w:basedOn", _TL_W)
            styles[style_id] = {
                "based_on": (
                    str(_tl_ooxml_val(based_on, default="") or "")
                    if based_on is not None
                    else ""
                ),
                "p": _tl_read_ppr(style.find("w:pPr", _TL_W)),
                "r": _tl_read_rpr(style.find("w:rPr", _TL_W)),
            }

    cache = {}

    def resolve(style_id: str) -> dict:
        style_id = str(style_id or "")
        if not style_id:
            return {"p": dict(default_p), "r": dict(default_r)}
        if style_id in cache:
            return cache[style_id]

        raw = styles.get(style_id)
        if raw is None:
            value = {"p": dict(default_p), "r": dict(default_r)}
            cache[style_id] = value
            return value

        parent_id = str(raw.get("based_on", "") or "")
        if parent_id and parent_id != style_id:
            parent = resolve(parent_id)
        else:
            parent = {"p": dict(default_p), "r": dict(default_r)}

        value = {
            "p": _tl_merge_dict(parent.get("p", {}), raw.get("p", {})),
            "r": _tl_merge_dict(parent.get("r", {}), raw.get("r", {})),
        }
        cache[style_id] = value
        return value

    return styles, cache, default_p, default_r, resolve


def _tl_rtf_escape(value: str) -> str:
    result = []
    for ch in str(value or ""):
        code = ord(ch)
        if ch == "\\":
            result.append(r"\\")
        elif ch == "{":
            result.append(r"\{")
        elif ch == "}":
            result.append(r"\}")
        elif ch == "\t":
            result.append(r"\tab ")
        elif ch == "\n":
            result.append(r"\line ")
        elif 32 <= code <= 126:
            result.append(ch)
        elif code <= 0xFFFF:
            signed = code if code < 0x8000 else code - 0x10000
            result.append(rf"\u{signed}?")
        else:
            code -= 0x10000
            high = 0xD800 + ((code >> 10) & 0x3FF)
            low = 0xDC00 + (code & 0x3FF)
            for item in (high, low):
                signed = item if item < 0x8000 else item - 0x10000
                result.append(rf"\u{signed}?")
    return "".join(result)


def _tl_run_text(run) -> tuple[str, bool]:
    parts = []
    has_page_break = False

    for node in list(run):
        local = node.tag.rsplit("}", 1)[-1]
        if local == "t":
            parts.append(node.text or "")
        elif local == "tab":
            parts.append("\t")
        elif local == "br":
            break_type = str(_tl_ooxml_val(node, "type", "") or "").lower()
            if break_type == "page":
                has_page_break = True
                parts.append("\n")
            else:
                parts.append("\n")
        elif local == "noBreakHyphen":
            parts.append("‑")
        elif local == "softHyphen":
            parts.append("\u00ad")

    return "".join(parts), has_page_break


def _tl_docx_internal_document(path: Path) -> dict:
    """Lit le DOCX directement en OOXML puis produit le document RTF interne.

    Aucun Word, LibreOffice, imprimante virtuelle ni convertisseur externe.
    Le RTF est uniquement le format de travail transmis au moteur Rich Edit.
    """

    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(source)

    with zipfile.ZipFile(source) as archive:
        document_root = ET.fromstring(archive.read("word/document.xml"))
        try:
            styles_root = ET.fromstring(archive.read("word/styles.xml"))
        except KeyError:
            styles_root = None

    _styles, _cache, default_p, default_r, resolve_style = _tl_parse_styles(
        styles_root
    )

    body = document_root.find("w:body", _TL_W)
    if body is None:
        raise ValueError("DOCX sans corps de document exploitable.")

    sect = body.find("w:sectPr", _TL_W)
    if sect is None:
        all_sect = body.findall(".//w:sectPr", _TL_W)
        sect = all_sect[-1] if all_sect else None

    page_w_twips = 8391  # environ A5
    page_h_twips = 11906
    margin_left_twips = 1020
    margin_right_twips = 1020
    margin_top_twips = 850
    margin_bottom_twips = 850

    if sect is not None:
        pg_sz = sect.find("w:pgSz", _TL_W)
        pg_mar = sect.find("w:pgMar", _TL_W)

        if pg_sz is not None:
            page_w_twips = max(1, _tl_int(_tl_ooxml_val(pg_sz, "w", page_w_twips), page_w_twips))
            page_h_twips = max(1, _tl_int(_tl_ooxml_val(pg_sz, "h", page_h_twips), page_h_twips))

        if pg_mar is not None:
            margin_left_twips = max(0, _tl_int(_tl_ooxml_val(pg_mar, "left", margin_left_twips), margin_left_twips))
            margin_right_twips = max(0, _tl_int(_tl_ooxml_val(pg_mar, "right", margin_right_twips), margin_right_twips))
            margin_top_twips = max(0, _tl_int(_tl_ooxml_val(pg_mar, "top", margin_top_twips), margin_top_twips))
            margin_bottom_twips = max(0, _tl_int(_tl_ooxml_val(pg_mar, "bottom", margin_bottom_twips), margin_bottom_twips))

    def twips_to_mm(value: int) -> float:
        return round(float(value) * 25.4 / 1440.0, 3)

    paragraphs = []
    fonts = set()
    colors = set()
    plain_parts = []

    def paragraph_record(p):
        ppr = p.find("w:pPr", _TL_W)
        p_style_node = ppr.find("w:pStyle", _TL_W) if ppr is not None else None
        p_style_id = str(_tl_ooxml_val(p_style_node, default="") or "")
        style_value = resolve_style(p_style_id)

        p_props = _tl_merge_dict(
            _tl_merge_dict(default_p, style_value.get("p", {})),
            _tl_read_ppr(ppr),
        )
        base_r = _tl_merge_dict(default_r, style_value.get("r", {}))

        runs = []
        paragraph_text = []
        paragraph_page_break = bool(p_props.get("page_break_before", False))

        for run in p.iter(_tl_w("r")):
            rpr = run.find("w:rPr", _TL_W)
            r_style_node = rpr.find("w:rStyle", _TL_W) if rpr is not None else None
            r_style_id = str(_tl_ooxml_val(r_style_node, default="") or "")
            char_style = resolve_style(r_style_id).get("r", {}) if r_style_id else {}

            props = _tl_merge_dict(
                _tl_merge_dict(base_r, char_style),
                _tl_read_rpr(rpr),
            )
            value, page_break = _tl_run_text(run)
            if not value and not page_break:
                continue

            paragraph_page_break = paragraph_page_break or page_break
            paragraph_text.append(value)
            runs.append({"text": value, "props": props, "page_break": page_break})

            if props.get("font"):
                fonts.add(str(props["font"]))
            if props.get("color"):
                colors.add(str(props["color"]))

        value = "".join(paragraph_text)
        plain_parts.append(value)
        return {
            "p": p_props,
            "runs": runs,
            "page_break_before": paragraph_page_break and bool(p_props.get("page_break_before", False)),
        }

    def walk_blocks(parent):
        for child in list(parent):
            local = child.tag.rsplit("}", 1)[-1]
            if local == "p":
                yield child
            elif local == "tbl":
                for row in child.findall("w:tr", _TL_W):
                    first_cell = True
                    for cell in row.findall("w:tc", _TL_W):
                        if not first_cell:
                            spacer = ET.Element(_tl_w("p"))
                            run = ET.SubElement(spacer, _tl_w("r"))
                            value = ET.SubElement(run, _tl_w("t"))
                            value.text = "\t"
                            yield spacer
                        first_cell = False
                        for item in walk_blocks(cell):
                            yield item

    for p in walk_blocks(body):
        paragraphs.append(paragraph_record(p))

    default_font = str(default_r.get("font") or "Times New Roman")
    fonts.add(default_font)

    ordered_fonts = [default_font] + sorted(font for font in fonts if font != default_font)
    font_ids = {font: index for index, font in enumerate(ordered_fonts)}

    ordered_colors = sorted(colors)
    color_ids = {value: index + 1 for index, value in enumerate(ordered_colors)}

    font_table = "".join(
        rf"{{\f{index} {_tl_rtf_escape(font)};}}"
        for index, font in enumerate(ordered_fonts)
    )

    color_table = ";"
    for value in ordered_colors:
        color_table += (
            rf"\red{int(value[0:2], 16)}"
            rf"\green{int(value[2:4], 16)}"
            rf"\blue{int(value[4:6], 16)};"
        )

    rtf_parts = [
        r"{\rtf1\ansi\ansicpg1252\uc1",
        "{\\fonttbl" + font_table + "}",
        "{\\colortbl" + color_table + "}",
        rf"\paperw{page_w_twips}\paperh{page_h_twips}",
        rf"\margl{margin_left_twips}\margr{margin_right_twips}",
        rf"\margt{margin_top_twips}\margb{margin_bottom_twips}",
        rf"\deff{font_ids[default_font]} ",
    ]

    align_rtf = {
        "left": r"\ql",
        "center": r"\qc",
        "right": r"\qr",
        "justify": r"\qj",
    }

    for paragraph in paragraphs:
        p = paragraph["p"]
        if bool(p.get("page_break_before", False)):
            rtf_parts.append(r"\page ")

        controls = [r"\pard"]
        controls.append(align_rtf.get(str(p.get("align", "left")), r"\ql"))

        if "left_twips" in p:
            controls.append(rf"\li{_tl_int(p['left_twips'])}")
        if "right_twips" in p:
            controls.append(rf"\ri{_tl_int(p['right_twips'])}")
        if "first_twips" in p:
            controls.append(rf"\fi{_tl_int(p['first_twips'])}")
        if "before_twips" in p:
            controls.append(rf"\sb{max(0, _tl_int(p['before_twips']))}")
        if "after_twips" in p:
            controls.append(rf"\sa{max(0, _tl_int(p['after_twips']))}")

        line = p.get("line")
        line_rule = str(p.get("line_rule", "") or "").lower()
        if line is not None:
            if line_rule == "auto":
                controls.append(rf"\sl{_tl_int(line)}\slmult1")
            else:
                controls.append(rf"\sl{_tl_int(line)}\slmult0")

        rtf_parts.append("".join(controls) + " ")

        if not paragraph["runs"]:
            rtf_parts.append(r"\par ")
            continue

        for run in paragraph["runs"]:
            props = run["props"]
            font = str(props.get("font") or default_font)
            size = max(1, _tl_int(props.get("size_half_points", 22), 22))

            run_controls = [
                rf"\f{font_ids.get(font, font_ids[default_font])}",
                rf"\fs{size}",
                r"\b" if bool(props.get("bold", False)) else r"\b0",
                r"\i" if bool(props.get("italic", False)) else r"\i0",
                r"\ul" if bool(props.get("underline", False)) else r"\ul0",
            ]

            color = str(props.get("color") or "")
            if color in color_ids:
                run_controls.append(rf"\cf{color_ids[color]}")
            else:
                run_controls.append(r"\cf0")

            value = str(run.get("text", "") or "")
            if run.get("page_break"):
                pieces = value.split("\n")
                for index, piece in enumerate(pieces):
                    if index:
                        rtf_parts.append(r"\page ")
                    if piece:
                        rtf_parts.append(
                            "{" + "".join(run_controls) + " " + _tl_rtf_escape(piece) + "}"
                        )
            else:
                rtf_parts.append(
                    "{" + "".join(run_controls) + " " + _tl_rtf_escape(value) + "}"
                )

        rtf_parts.append(r"\par ")

    rtf_parts.append("}")
    rtf = "".join(rtf_parts).encode("ascii", errors="strict")

    return {
        "engine": "msftedit",
        "kind": "docx_internal_v1",
        "source_path": str(source),
        "rtf_b64": base64.b64encode(rtf).decode("ascii"),
        "plain_text": "\n".join(plain_parts),
        "paragraph_count": len(paragraphs),
        "format": {
            "width_mm": twips_to_mm(page_w_twips),
            "height_mm": twips_to_mm(page_h_twips),
            "margin_top_mm": twips_to_mm(margin_top_twips),
            "margin_bottom_mm": twips_to_mm(margin_bottom_twips),
            "margin_inside_mm": twips_to_mm(margin_left_twips),
            "margin_outside_mm": twips_to_mm(margin_right_twips),
        },
        "page_starts": [0],
    }


class _TLCharRange(ctypes.Structure):
    _fields_ = [
        ("cpMin", ctypes.c_long),
        ("cpMax", ctypes.c_long),
    ]


class _TLRect(ctypes.Structure):
    _fields_ = [
        ("left", ctypes.c_long),
        ("top", ctypes.c_long),
        ("right", ctypes.c_long),
        ("bottom", ctypes.c_long),
    ]


class _TLFormatRange(ctypes.Structure):
    _fields_ = [
        ("hdc", wintypes.HDC),
        ("hdcTarget", wintypes.HDC),
        ("rc", _TLRect),
        ("rcPage", _TLRect),
        ("chrg", _TLCharRange),
    ]


class _TLSetTextEx(ctypes.Structure):
    _fields_ = [
        ("flags", wintypes.DWORD),
        ("codepage", wintypes.UINT),
    ]


class _TLGetTextLengthEx(ctypes.Structure):
    _fields_ = [
        ("flags", wintypes.DWORD),
        ("codepage", wintypes.UINT),
    ]


class _TLPoint(ctypes.Structure):
    _fields_ = [
        ("x", ctypes.c_long),
        ("y", ctypes.c_long),
    ]


_TL_CALLBACK_FACTORY = getattr(ctypes, "WINFUNCTYPE", ctypes.CFUNCTYPE)

_TL_STREAM_CALLBACK = _TL_CALLBACK_FACTORY(
    wintypes.DWORD,
    ctypes.c_size_t,
    ctypes.c_void_p,
    ctypes.c_long,
    ctypes.POINTER(ctypes.c_long),
)


class _TLEditStream(ctypes.Structure):
    _fields_ = [
        ("dwCookie", ctypes.c_size_t),
        ("dwError", wintypes.DWORD),
        ("pfnCallback", ctypes.c_void_p),
    ]


class _TLRichEditAPI:
    WM_USER = 0x0400
    WM_SETREDRAW = 0x000B
    WM_MOUSEWHEEL = 0x020A

    EM_GETLINECOUNT = 0x00BA
    EM_LINESCROLL = 0x00B6
    EM_GETMODIFY = 0x00B8
    EM_SETMODIFY = 0x00B9
    EM_GETFIRSTVISIBLELINE = 0x00CE
    EM_FORMATRANGE = WM_USER + 57
    EM_EXLINEFROMCHAR = WM_USER + 54
    EM_EXGETSEL = WM_USER + 52
    EM_EXSETSEL = WM_USER + 55
    EM_SETTARGETDEVICE = WM_USER + 72
    EM_STREAMIN = WM_USER + 73
    EM_STREAMOUT = WM_USER + 74
    EM_GETTEXTLENGTHEX = WM_USER + 95
    EM_SETTEXTEX = WM_USER + 97
    EM_GETSCROLLPOS = WM_USER + 221
    EM_SETSCROLLPOS = WM_USER + 222
    EM_SETZOOM = WM_USER + 225
    EM_SETBKGNDCOLOR = WM_USER + 67

    GTL_PRECISE = 0x0002
    GTL_NUMCHARS = 0x0008
    CP_UNICODE = 1200
    CP_ACP = 0
    ST_DEFAULT = 0
    SF_RTF = 0x0002

    WS_CHILD = 0x40000000
    WS_VISIBLE = 0x10000000
    WS_TABSTOP = 0x00010000
    WS_HSCROLL = 0x00100000
    WS_VSCROLL = 0x00200000
    ES_MULTILINE = 0x0004
    ES_AUTOVSCROLL = 0x0040
    ES_AUTOHSCROLL = 0x0080
    ES_WANTRETURN = 0x1000
    ES_NOHIDESEL = 0x0100

    SW_HIDE = 0
    SW_SHOW = 5

    def __init__(self):
        if sys.platform != "win32":
            raise RuntimeError("Microsoft Rich Edit nécessite Windows.")

        self.user32 = ctypes.WinDLL("user32", use_last_error=True)
        self.gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
        ctypes.WinDLL("Msftedit.dll", use_last_error=True)
        self.comctl32 = ctypes.WinDLL("comctl32", use_last_error=True)

        self.SUBCLASSPROC = ctypes.WINFUNCTYPE(
            ctypes.c_ssize_t,
            wintypes.HWND,
            wintypes.UINT,
            ctypes.c_size_t,
            ctypes.c_ssize_t,
            ctypes.c_size_t,
            ctypes.c_size_t,
        )

        self.comctl32.SetWindowSubclass.argtypes = [
            wintypes.HWND,
            self.SUBCLASSPROC,
            ctypes.c_size_t,
            ctypes.c_size_t,
        ]
        self.comctl32.SetWindowSubclass.restype = wintypes.BOOL
        self.comctl32.RemoveWindowSubclass.argtypes = [
            wintypes.HWND,
            self.SUBCLASSPROC,
            ctypes.c_size_t,
        ]
        self.comctl32.RemoveWindowSubclass.restype = wintypes.BOOL
        self.comctl32.DefSubclassProc.argtypes = [
            wintypes.HWND,
            wintypes.UINT,
            ctypes.c_size_t,
            ctypes.c_ssize_t,
        ]
        self.comctl32.DefSubclassProc.restype = ctypes.c_ssize_t

        self.user32.CreateWindowExW.argtypes = [
            wintypes.DWORD,
            wintypes.LPCWSTR,
            wintypes.LPCWSTR,
            wintypes.DWORD,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.HWND,
            wintypes.HMENU,
            wintypes.HINSTANCE,
            wintypes.LPVOID,
        ]
        self.user32.CreateWindowExW.restype = wintypes.HWND

        self.user32.SendMessageW.argtypes = [
            wintypes.HWND,
            wintypes.UINT,
            ctypes.c_size_t,
            ctypes.c_ssize_t,
        ]
        self.user32.SendMessageW.restype = ctypes.c_ssize_t

        self.user32.MoveWindow.argtypes = [
            wintypes.HWND,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            wintypes.BOOL,
        ]
        self.user32.MoveWindow.restype = wintypes.BOOL

        self.user32.DestroyWindow.argtypes = [wintypes.HWND]
        self.user32.DestroyWindow.restype = wintypes.BOOL

        self.user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
        self.user32.ShowWindow.restype = wintypes.BOOL

        self.user32.ShowScrollBar.argtypes = [
            wintypes.HWND,
            ctypes.c_int,
            wintypes.BOOL,
        ]
        self.user32.ShowScrollBar.restype = wintypes.BOOL

        self.user32.InvalidateRect.argtypes = [
            wintypes.HWND,
            ctypes.c_void_p,
            wintypes.BOOL,
        ]
        self.user32.InvalidateRect.restype = wintypes.BOOL

        self.user32.GetDesktopWindow.argtypes = []
        self.user32.GetDesktopWindow.restype = wintypes.HWND

        try:
            self.user32.GetDpiForWindow.argtypes = [wintypes.HWND]
            self.user32.GetDpiForWindow.restype = wintypes.UINT
            self.has_dpi = True
        except AttributeError:
            self.has_dpi = False

        self.gdi32.CreateDCW.argtypes = [
            wintypes.LPCWSTR,
            wintypes.LPCWSTR,
            wintypes.LPCWSTR,
            wintypes.LPVOID,
        ]
        self.gdi32.CreateDCW.restype = wintypes.HDC
        self.gdi32.DeleteDC.argtypes = [wintypes.HDC]
        self.gdi32.DeleteDC.restype = wintypes.BOOL


    @staticmethod
    def twips(mm: float) -> int:
        return int(round(float(mm) * 1440.0 / 25.4))

    def display_dc(self):
        hdc = self.gdi32.CreateDCW("DISPLAY", None, None, None)
        if not hdc:
            raise RuntimeError("Impossible de préparer le contexte d'affichage Rich Edit.")
        return hdc

    def create_control(self, parent_hwnd: int, *, visible: bool = True):
        style = (
            self.WS_CHILD
            | self.WS_TABSTOP
            | self.ES_MULTILINE
            | self.ES_AUTOVSCROLL
            | self.ES_WANTRETURN
            | self.ES_NOHIDESEL
        )
        if visible:
            style |= self.WS_VISIBLE

        hwnd = self.user32.CreateWindowExW(
            0,
            "RICHEDIT50W",
            "",
            style,
            0,
            0,
            20,
            20,
            int(parent_hwnd),
            None,
            None,
            None,
        )
        if not hwnd:
            raise RuntimeError(
                f"Impossible de créer Microsoft Rich Edit ({ctypes.get_last_error()})."
            )

        # Les capacites de defilement restent actives pour EM_SETSCROLLPOS,
        # mais les barres natives sont masquees : TomeLinea affiche ses propres
        # barres de viewport autour de la page.
        try:
            self.user32.ShowScrollBar(hwnd, 3, False)
        except Exception:
            pass

        return hwnd

    def load_rtf(self, hwnd, rtf_bytes: bytes) -> None:
        opts = _TLSetTextEx(self.ST_DEFAULT, self.CP_ACP)
        payload = bytes(rtf_bytes or b"")
        if not payload.endswith(b"\x00"):
            payload += b"\x00"
        buf = ctypes.create_string_buffer(payload)
        result = int(
            self.user32.SendMessageW(
                hwnd,
                self.EM_SETTEXTEX,
                ctypes.addressof(opts),
                ctypes.addressof(buf),
            )
        )
        if result == 0 and len(rtf_bytes or b"") > 0:
            raise RuntimeError("Microsoft Rich Edit a refusé le document interne.")

    def text_length(self, hwnd) -> int:
        opts = _TLGetTextLengthEx(
            self.GTL_PRECISE | self.GTL_NUMCHARS,
            self.CP_UNICODE,
        )
        return int(
            self.user32.SendMessageW(
                hwnd,
                self.EM_GETTEXTLENGTHEX,
                ctypes.addressof(opts),
                0,
            )
        )

    def set_target_width(self, hwnd, hdc, width_mm: float) -> None:
        self.user32.SendMessageW(
            hwnd,
            self.EM_SETTARGETDEVICE,
            int(hdc),
            self.twips(max(1.0, float(width_mm))),
        )

    def paginate(self, hwnd, hdc, fmt) -> list[int]:
        total = self.text_length(hwnd)
        if total <= 0:
            return [0]

        width = float(fmt.width_mm)
        height = float(fmt.height_mm)
        top = max(0.0, float(fmt.margin_top_mm))
        bottom = max(0.0, float(fmt.margin_bottom_mm))
        inside = max(0.0, float(fmt.margin_inside_mm))
        outside = max(0.0, float(fmt.margin_outside_mm))

        self.set_target_width(hwnd, hdc, width - inside - outside)

        page_rect = _TLRect(
            0,
            0,
            self.twips(width),
            self.twips(height),
        )
        text_rect = _TLRect(
            self.twips(inside),
            self.twips(top),
            self.twips(width - outside),
            self.twips(height - bottom),
        )

        starts = [0]
        pos = 0

        while pos < total:
            fr = _TLFormatRange(
                hdc=hdc,
                hdcTarget=hdc,
                rc=text_rect,
                rcPage=page_rect,
                chrg=_TLCharRange(pos, total),
            )
            nxt = int(
                self.user32.SendMessageW(
                    hwnd,
                    self.EM_FORMATRANGE,
                    0,
                    ctypes.addressof(fr),
                )
            )
            if nxt <= pos:
                self.user32.SendMessageW(hwnd, self.EM_FORMATRANGE, 0, 0)
                raise RuntimeError(
                    f"La pagination Rich Edit s'est arrêtée à {pos} / {total}."
                )
            if nxt >= total:
                pos = total
                break
            starts.append(nxt)
            pos = nxt
            if len(starts) > 10000:
                self.user32.SendMessageW(hwnd, self.EM_FORMATRANGE, 0, 0)
                raise RuntimeError("Pagination Rich Edit anormalement longue.")

        self.user32.SendMessageW(hwnd, self.EM_FORMATRANGE, 0, 0)

        if pos != total:
            raise RuntimeError(f"Pagination Rich Edit incomplète : {pos} / {total}.")
        return starts

    def paginate_rtf(self, rtf_bytes: bytes, fmt) -> list[int]:
        desktop = self.user32.GetDesktopWindow()
        hwnd = self.create_control(desktop, visible=False)
        hdc = self.display_dc()
        try:
            self.load_rtf(hwnd, rtf_bytes)
            return self.paginate(hwnd, hdc, fmt)
        finally:
            try:
                self.user32.DestroyWindow(hwnd)
            finally:
                self.gdi32.DeleteDC(hdc)


_TL_RICH_API = None


def _tl_rich_api() -> _TLRichEditAPI:
    global _TL_RICH_API
    if _TL_RICH_API is None:
        _TL_RICH_API = _TLRichEditAPI()
    return _TL_RICH_API


class _TLRichEditHost:
    """Document Rich Edit dans un vrai viewport TomeLinea.

    Regle fondamentale :
    - EM_SETTARGETDEVICE fixe la largeur logique du texte ;
    - EM_SETZOOM ne modifie que l'affichage ;
    - l'HWND Rich Edit reste toujours dans la zone visible du Canvas ;
    - EM_SETSCROLLPOS montre la portion du texte correspondant a la portion
      visible de la page quand celle-ci depasse le viewport.

    Le Rich Edit n'est donc plus un grand enfant Windows coupe par son parent.
    """

    _SUBCLASS_ID = 0x544C01

    def __init__(self, app, canvas, rtf_bytes: bytes, fmt) -> None:
        self.app = app
        self.canvas = canvas
        self.api = _tl_rich_api()
        self.hdc = self.api.display_dc()
        self.hwnd = self.api.create_control(int(canvas.winfo_id()), visible=True)
        self.rtf_bytes = bytes(rtf_bytes)
        self.page_starts = [0]
        self.rect = (0, 0, 20, 20)
        self._subclass_callback = None
        self._wheel_delta = 0
        self._wheel_after = None
        self._destroyed = False

        self.api.load_rtf(self.hwnd, self.rtf_bytes)
        self.page_starts = self.api.paginate(self.hwnd, self.hdc, fmt)
        self.api.user32.SendMessageW(
            self.hwnd,
            self.api.EM_SETBKGNDCOLOR,
            0,
            0x00FFFFFF,
        )
        self.clear_modified()
        self._install_safe_wheel_subclass()
        self._schedule_wheel_pump()

    def _install_safe_wheel_subclass(self) -> None:
        api = self.api

        @api.SUBCLASSPROC
        def proc(hwnd, msg, wparam, lparam, _subclass_id, _ref_data):
            # Aucun appel Tk depuis la procedure Windows : on ne fait
            # qu'accumuler les crans. Le mainloop les traite ensuite.
            if msg == api.WM_MOUSEWHEEL:
                raw = (int(wparam) >> 16) & 0xFFFF
                delta = raw - 0x10000 if raw & 0x8000 else raw
                self._wheel_delta += int(delta)
                return 0

            return int(
                api.comctl32.DefSubclassProc(
                    hwnd,
                    msg,
                    wparam,
                    lparam,
                )
            )

        self._subclass_callback = proc
        ok = bool(
            api.comctl32.SetWindowSubclass(
                self.hwnd,
                proc,
                self._SUBCLASS_ID,
                0,
            )
        )
        if not ok:
            self._subclass_callback = None
            raise RuntimeError(
                "Impossible de relier la molette Rich Edit au zoom TomeLinea."
            )

    def _schedule_wheel_pump(self) -> None:
        if self._destroyed:
            return
        try:
            self._wheel_after = self.app.after(24, self._pump_wheel)
        except Exception:
            self._wheel_after = None

    def _pump_wheel(self) -> None:
        self._wheel_after = None
        if self._destroyed or not self.hwnd:
            return

        # Le zoom continu est volontairement supprime pour Rich Edit.
        # La molette ne change donc jamais l'echelle du document.
        # En vue agrandie (200 %), elle sert uniquement a parcourir la page.
        delta = int(self._wheel_delta)
        self._wheel_delta = 0

        if delta:
            direction = 1 if delta > 0 else -1
            try:
                self.app._rich_pan_wheel(direction)
            except Exception:
                pass

        self._schedule_wheel_pump()

    def destroy(self):
        if self._destroyed:
            return
        self._destroyed = True

        if self._wheel_after is not None:
            try:
                self.app.after_cancel(self._wheel_after)
            except Exception:
                pass
            self._wheel_after = None

        if self.hwnd and self._subclass_callback is not None:
            try:
                self.api.comctl32.RemoveWindowSubclass(
                    self.hwnd,
                    self._subclass_callback,
                    self._SUBCLASS_ID,
                )
            except Exception:
                pass

        try:
            if self.hwnd:
                self.api.user32.DestroyWindow(self.hwnd)
        except Exception:
            pass

        try:
            if self.hdc:
                self.api.gdi32.DeleteDC(self.hdc)
        except Exception:
            pass

        self.hwnd = None
        self.hdc = None
        self._subclass_callback = None

    def hide(self):
        if self.hwnd:
            self.api.user32.ShowWindow(self.hwnd, self.api.SW_HIDE)

    def show(self):
        if self.hwnd:
            self.api.user32.ShowWindow(self.hwnd, self.api.SW_SHOW)

    def is_modified(self) -> bool:
        if not self.hwnd:
            return False
        return bool(
            self.api.user32.SendMessageW(
                self.hwnd,
                self.api.EM_GETMODIFY,
                0,
                0,
            )
        )

    def clear_modified(self):
        if self.hwnd:
            self.api.user32.SendMessageW(
                self.hwnd,
                self.api.EM_SETMODIFY,
                0,
                0,
            )

    def get_rtf_bytes(self) -> bytes:
        chunks = []

        @_TL_STREAM_CALLBACK
        def callback(_cookie, buffer_ptr, count, processed_ptr):
            try:
                if count > 0:
                    chunks.append(ctypes.string_at(buffer_ptr, count))
                processed_ptr[0] = int(count)
                return 0
            except Exception:
                processed_ptr[0] = 0
                return 1

        stream = _TLEditStream(
            0,
            0,
            ctypes.cast(callback, ctypes.c_void_p).value,
        )

        self.api.user32.SendMessageW(
            self.hwnd,
            self.api.EM_STREAMOUT,
            self.api.SF_RTF,
            ctypes.addressof(stream),
        )

        if stream.dwError:
            raise RuntimeError(
                f"Impossible de relire le document Rich Edit ({stream.dwError})."
            )

        return b"".join(chunks)

    def repaginate(self, fmt) -> list[int]:
        self.page_starts = self.api.paginate(self.hwnd, self.hdc, fmt)
        return list(self.page_starts)

    def _screen_px_per_mm(self) -> float:
        dpi = 96.0
        if self.api.has_dpi:
            try:
                value = int(
                    self.api.user32.GetDpiForWindow(int(self.canvas.winfo_id()))
                )
                if value > 0:
                    dpi = float(value)
            except Exception:
                pass
        return dpi / 25.4

    def _set_display_scale(self, scale_px_per_mm: float) -> None:
        base = max(0.01, self._screen_px_per_mm())
        ratio = max(
            1.0 / 64.0,
            min(63.0, float(scale_px_per_mm) / base),
        )
        denominator = 1000
        numerator = max(1, int(round(ratio * denominator)))

        ok = int(
            self.api.user32.SendMessageW(
                self.hwnd,
                self.api.EM_SETZOOM,
                numerator,
                denominator,
            )
        )
        if not ok:
            denominator = 100
            numerator = max(2, int(round(ratio * denominator)))
            ok = int(
                self.api.user32.SendMessageW(
                    self.hwnd,
                    self.api.EM_SETZOOM,
                    numerator,
                    denominator,
                )
            )
        if not ok:
            raise RuntimeError("Microsoft Rich Edit a refuse le zoom d'affichage.")

    def _move_to_page_start(self, page_index: int) -> _TLPoint:
        index = max(0, min(int(page_index), len(self.page_starts) - 1))
        start = int(self.page_starts[index])
        selection = _TLCharRange(start, start)

        self.api.user32.SendMessageW(
            self.hwnd,
            self.api.EM_EXSETSEL,
            0,
            ctypes.addressof(selection),
        )

        target_line = int(
            self.api.user32.SendMessageW(
                self.hwnd,
                self.api.EM_EXLINEFROMCHAR,
                0,
                start,
            )
        )
        current_line = int(
            self.api.user32.SendMessageW(
                self.hwnd,
                self.api.EM_GETFIRSTVISIBLELINE,
                0,
                0,
            )
        )
        delta = target_line - current_line
        if delta:
            self.api.user32.SendMessageW(
                self.hwnd,
                self.api.EM_LINESCROLL,
                0,
                delta,
            )

        point = _TLPoint(0, 0)
        self.api.user32.SendMessageW(
            self.hwnd,
            self.api.EM_GETSCROLLPOS,
            0,
            ctypes.addressof(point),
        )
        return point

    def _set_view_scroll(
        self,
        page_index: int,
        hidden_x: float,
        hidden_y: float,
    ) -> None:
        base = self._move_to_page_start(page_index)
        point = _TLPoint(
            max(0, int(round(hidden_x))),
            max(0, int(round(float(base.y) + hidden_y))),
        )
        self.api.user32.SendMessageW(
            self.hwnd,
            self.api.EM_SETSCROLLPOS,
            0,
            ctypes.addressof(point),
        )

    def layout(self, page, view: dict, fmt, page_index: int) -> None:
        if not self.hwnd:
            return

        scale = max(0.01, float(view.get("scale", 1.0) or 1.0))
        page_x = float(view.get("x", 0.0) or 0.0)
        page_y = float(view.get("y", 0.0) or 0.0)

        side = str(getattr(page, "recto_verso", "") or "").strip().lower()
        if side not in {"recto", "verso"}:
            side = "recto" if int(page_index) % 2 == 0 else "verso"

        inside = max(0.0, float(fmt.margin_inside_mm))
        outside = max(0.0, float(fmt.margin_outside_mm))
        top = max(0.0, float(fmt.margin_top_mm))
        bottom = max(0.0, float(fmt.margin_bottom_mm))

        left = inside if side == "recto" else outside
        right = outside if side == "recto" else inside

        logical_width = max(1.0, float(fmt.width_mm) - left - right)
        logical_height = max(1.0, float(fmt.height_mm) - top - bottom)

        # Rectangle virtuel de la zone texte dans la page zoomee.
        virtual_x = page_x + left * scale
        virtual_y = page_y + top * scale
        virtual_w = logical_width * scale
        virtual_h = logical_height * scale

        canvas_w = max(1.0, float(self.canvas.winfo_width()))
        canvas_h = max(1.0, float(self.canvas.winfo_height()))

        # Intersection avec le vrai viewport. Le HWND ne depasse jamais
        # de son parent Windows : c'est la difference essentielle.
        visible_left = max(0.0, virtual_x)
        visible_top = max(0.0, virtual_y)
        visible_right = min(canvas_w, virtual_x + virtual_w)
        visible_bottom = min(canvas_h, virtual_y + virtual_h)

        if visible_right <= visible_left or visible_bottom <= visible_top:
            self.hide()
            return

        control_x = int(round(visible_left))
        control_y = int(round(visible_top))
        control_w = max(1, int(round(visible_right - visible_left)))
        control_h = max(1, int(round(visible_bottom - visible_top)))

        hidden_x = max(0.0, visible_left - virtual_x)
        hidden_y = max(0.0, visible_top - virtual_y)

        self.api.user32.SendMessageW(
            self.hwnd,
            self.api.WM_SETREDRAW,
            0,
            0,
        )
        try:
            self.api.set_target_width(self.hwnd, self.hdc, logical_width)
            self._set_display_scale(scale)

            self.rect = (control_x, control_y, control_w, control_h)
            self.api.user32.MoveWindow(
                self.hwnd,
                control_x,
                control_y,
                control_w,
                control_h,
                False,
            )

            self._set_view_scroll(
                page_index,
                hidden_x,
                hidden_y,
            )
            self.show()
        finally:
            self.api.user32.SendMessageW(
                self.hwnd,
                self.api.WM_SETREDRAW,
                1,
                0,
            )
            self.api.user32.InvalidateRect(self.hwnd, None, True)



# ==============================================================
# PANNEAU TOMELINEA
# ==============================================================

class CutPanel(tk.Canvas):

    def __init__(
        self,
        parent,
        *,
        fill: str = theme.PANEL,
        border: str = theme.BORDER_SOFT,
        cut: int = 15,
        padding: tuple[int, int] = (
            20,
            18,
        ),
        **kwargs,
    ):

        try:
            parent_bg = parent.cget(
                "bg"
            )
        except Exception:
            parent_bg = theme.WINDOW_DEEP

        super().__init__(
            parent,
            bg=parent_bg,
            bd=0,
            highlightthickness=0,
            **kwargs,
        )

        self._fill = fill
        self._border = border
        self._cut = cut

        self._pad_x = padding[0]
        self._pad_y = padding[1]

        self.body = tk.Frame(
            self,
            bg=fill,
        )

        self._body_id = (
            self.create_window(
                self._pad_x,
                self._pad_y,
                anchor="nw",
                window=self.body,
            )
        )

        self.bind(
            "<Configure>",
            self._redraw,
            add="+",
        )


    def _redraw(
        self,
        _event=None,
    ) -> None:

        width = max(
            30,
            self.winfo_width(),
        )

        height = max(
            30,
            self.winfo_height(),
        )

        cut = min(
            self._cut,
            max(
                5,
                width // 10,
            ),
            max(
                5,
                height // 10,
            ),
        )

        points = [
            1, 1,
            width - cut, 1,
            width - 1, cut,
            width - 1, height - cut,
            width - cut, height - 1,
            cut, height - 1,
            1, height - cut,
            1, cut,
        ]

        self.delete(
            "panel_shape"
        )

        self.create_polygon(
            points,
            fill=self._fill,
            outline=self._border,
            width=1,
            tags=(
                "panel_shape",
            ),
        )

        self.tag_lower(
            "panel_shape"
        )

        inner_width = max(
            1,
            width
            - self._pad_x * 2,
        )

        inner_height = max(
            1,
            height
            - self._pad_y * 2,
        )

        self.coords(
            self._body_id,
            self._pad_x,
            self._pad_y,
        )

        self.itemconfigure(
            self._body_id,
            width=inner_width,
            height=inner_height,
        )


# ==============================================================
# BOUTON TOMELINEA
# ==============================================================

class TLButton(tk.Button):

    def __init__(
        self,
        parent,
        text: str,
        command=None,
        *,
        primary: bool = False,
        compact: bool = False,
        state: str = "normal",
        width: int | None = None,
    ):

        if primary:
            base_bg = theme.ACCENT_DARK
            hover_bg = theme.ACCENT
            fg = theme.WHITE
            active_fg = theme.WINDOW_DEEP

        else:
            base_bg = theme.PANEL_SOFT
            hover_bg = theme.ACCENT_SOFT
            fg = theme.INK
            active_fg = theme.WHITE

        kwargs = {}

        if width is not None:
            kwargs[
                "width"
            ] = width

        super().__init__(
            parent,
            text=text,
            command=command,
            state=state,
            bg=base_bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground=active_fg,
            disabledforeground=theme.MUTED_DARK,
            relief="flat",
            bd=0,
            padx=(
                11
                if compact
                else 16
            ),
            pady=(
                6
                if compact
                else 9
            ),
            font=(
                theme.FONT_UI,
                9,
                "bold",
            ),
            cursor=(
                "hand2"
                if state != "disabled"
                else "arrow"
            ),
            **kwargs,
        )

        self._base_bg = base_bg
        self._hover_bg = hover_bg

        self.bind(
            "<Enter>",
            self._enter,
            add="+",
        )

        self.bind(
            "<Leave>",
            self._leave,
            add="+",
        )


    def _enter(
        self,
        _event=None,
    ) -> None:

        if str(
            self.cget(
                "state"
            )
        ) != "disabled":
            self.configure(
                bg=self._hover_bg
            )


    def _leave(
        self,
        _event=None,
    ) -> None:

        self.configure(
            bg=self._base_bg
        )


# ==============================================================
# COUCHE GRAPHIQUE V4
# ==============================================================

class TomeLineaV4Editorial(
    TomeLineaV4Logic
):

    def __init__(
        self,
        *,
        defer_show: bool = False,
    ) -> None:

        # Caches graphiques indépendants.
        self._editorial_bg_sources = {}
        self._editorial_bg_cache = {}

        self._brand_icon_cache = {}
        self._brand_title_cache = {}

        self._line_icon_cache = {}

        # Document DOCX interne / moteur Microsoft Rich Edit.
        self._rich_host = None
        self._rich_document_key = None
        self._rich_poll_after = None
        self._rich_hscroll = None
        self._rich_vscroll = None
        self._rich_scroll_canvas = None
        self._rich_view_toolbar_saved = None
        self._canvas_page_host = None
        self._canvas_page_key = None
        self._canvas_last_page_count = 0
        self._canvas_zoom_label = None
        self._canvas_zoom_saved_pack = None

        # Phase 2.36B : moteur Canvas 2.35 intégré dans la vraie zone centrale
        # de Composition. Le moteur de test séparé n'est plus nécessaire pour
        # l'affichage : le même plan validé est hébergé ici.
        self._phase2_canvas_host = None
        self._phase2_canvas_key = None
        self._phase2_canvas_state = "idle"
        self._phase2_canvas_generation = 0
        self._phase2_canvas_queue = queue.Queue()
        self._phase2_canvas_poll_after = None
        self._phase2_canvas_overlay = None
        self._phase2_canvas_overlay_title = None
        self._phase2_canvas_overlay_detail = None
        self._phase2_canvas_syncing_page = False
        self._phase2_canvas_last_failure = None

        # Toute la fenêtre est construite hors écran. Le Tk racine n'est
        # affiché qu'une fois l'habillage, la géométrie et l'Accueil prêts :
        # aucun flash intermédiaire ni reconstruction visible au démarrage.
        super().__init__(start_hidden=True)

        try:
            self.overrideredirect(
                True
            )
        except tk.TclError:
            pass

        self._fit_to_work_area()
        self.update_idletasks()

        if not defer_show:
            self.show_prepared_window()

    def show_prepared_window(self) -> None:
        """Affiche la fenêtre V4 uniquement lorsqu'elle est entièrement prête."""
        try:
            self.deiconify()
            self.lift()
            self.update_idletasks()
        except tk.TclError:
            pass


    # ==========================================================
    # DOCX INTERNE / RICH EDIT
    # ==========================================================

    def _rich_document_metadata(self):
        session = getattr(self, "session", None)
        project = getattr(session, "project", None) if session is not None else None
        if project is None:
            return None
        value = project.metadata.get("internal_rich_document")
        if not isinstance(value, dict):
            return None
        if value.get("engine") != "msftedit":
            return None
        return value

    def _rich_page_index(self, page) -> int | None:
        metadata = getattr(page, "metadata", None)
        if not isinstance(metadata, dict):
            return None
        if not metadata.get("internal_rich_page"):
            return None
        try:
            return max(0, int(metadata.get("internal_rich_page_index", 0)))
        except (TypeError, ValueError):
            return 0

    def _rich_is_active_page(self) -> bool:
        if self._rich_document_metadata() is None:
            return False
        session = getattr(self, "session", None)
        if session is None:
            return False
        page = session.active_page
        return page is not None and self._rich_page_index(page) is not None

    def _rich_rtf_bytes(self) -> bytes:
        metadata = self._rich_document_metadata()
        if metadata is None:
            return b""
        raw = str(metadata.get("rtf_b64", "") or "")
        if not raw:
            return b""
        return base64.b64decode(raw.encode("ascii"))

    def _rich_destroy_host(self, *, save: bool = True) -> None:
        host = getattr(self, "_rich_host", None)
        if host is None:
            return

        if save:
            try:
                self._rich_commit_edits(repaginate=False)
            except Exception:
                pass

        try:
            host.destroy()
        except Exception:
            pass

        self._rich_host = None
        self._rich_document_key = None

        after_id = getattr(self, "_rich_poll_after", None)
        if after_id is not None:
            try:
                self.after_cancel(after_id)
            except Exception:
                pass
            self._rich_poll_after = None

    def _clear(self) -> None:
        self._phase2_destroy_host()
        self._phase2_cancel_poll()
        self._rich_destroy_host(save=True)
        for bar in (self._rich_hscroll, self._rich_vscroll):
            if bar is not None:
                try:
                    bar.destroy()
                except Exception:
                    pass
        self._rich_hscroll = None
        self._rich_vscroll = None
        self._rich_scroll_canvas = None
        super()._clear()

    def _rich_sync_pages(self, starts: list[int]) -> None:
        metadata = self._rich_document_metadata()
        if metadata is None or self.session is None:
            return

        book = self.session.book
        starts = [int(value) for value in (starts or [0])]
        if not starts:
            starts = [0]

        rich_ids = [
            page_id
            for page_id in list(book.page_order)
            if bool(getattr(book.pages.get(page_id), "metadata", {}).get("internal_rich_page"))
        ]

        from src.v4.domain import PageOrigin, PageV4

        while len(rich_ids) < len(starts):
            index = len(rich_ids)
            page = PageV4(
                page_type="Page texte",
                title=f"Page {index + 1}",
                origin=PageOrigin.AUTHOR,
                source=None,
            )
            page.metadata["internal_rich_page"] = True
            page.metadata["internal_rich_page_index"] = index
            page.metadata["internal_rich_page_start"] = int(starts[index])
            book.add_page(page)
            rich_ids.append(page.id)

        while len(rich_ids) > len(starts):
            page_id = rich_ids.pop()
            if page_id in book.page_order:
                book.page_order.remove(page_id)
            book.pages.pop(page_id, None)

        for index, page_id in enumerate(rich_ids):
            page = book.pages[page_id]
            page.title = f"Page {index + 1}"
            page.page_type = "Page texte"
            page.metadata["internal_rich_page"] = True
            page.metadata["internal_rich_page_index"] = index
            page.metadata["internal_rich_page_start"] = int(starts[index])

        metadata["page_starts"] = list(starts)
        metadata["page_count"] = len(starts)
        self.session.refresh_context()

    def _rich_commit_edits(self, *, repaginate: bool = True) -> None:
        host = getattr(self, "_rich_host", None)
        metadata = self._rich_document_metadata()
        if host is None or metadata is None:
            return
        if not host.hwnd:
            return

        rtf_bytes = host.get_rtf_bytes()
        metadata["rtf_b64"] = base64.b64encode(rtf_bytes).decode("ascii")

        if repaginate:
            starts = host.repaginate(self.session.book.format)
            self._rich_sync_pages(starts)

        host.clear_modified()
        try:
            self.session.project.touch()
        except Exception:
            pass

    def _rich_poll_modified(self) -> None:
        self._rich_poll_after = None
        host = getattr(self, "_rich_host", None)

        if host is None or not host.hwnd:
            return

        try:
            if host.is_modified():
                self._rich_commit_edits(repaginate=True)
        except Exception:
            pass

        try:
            self._rich_poll_after = self.after(800, self._rich_poll_modified)
        except Exception:
            self._rich_poll_after = None

    def _rich_ensure_host(self, canvas):
        metadata = self._rich_document_metadata()
        if metadata is None:
            self._rich_destroy_host(save=False)
            return None

        key = (
            str(metadata.get("source_path", "")),
            str(metadata.get("kind", "")),
        )

        host = getattr(self, "_rich_host", None)
        if (
            host is not None
            and getattr(host, "canvas", None) is canvas
            and self._rich_document_key == key
            and getattr(host, "hwnd", None)
        ):
            return host

        self._rich_destroy_host(save=True)

        host = _TLRichEditHost(
            self,
            canvas,
            self._rich_rtf_bytes(),
            self.session.book.format,
        )
        self._rich_host = host
        self._rich_document_key = key
        self._rich_sync_pages(host.page_starts)

        # Pas de repagination periodique pendant le travail : le moteur reste
        # stable et la pagination est recalculee au moment de sauvegarder.
        return host

    def _rich_ensure_scrollbars(self, canvas) -> None:
        if (
            self._rich_scroll_canvas is canvas
            and self._rich_hscroll is not None
            and self._rich_vscroll is not None
        ):
            return

        for bar in (self._rich_hscroll, self._rich_vscroll):
            if bar is not None:
                try:
                    bar.destroy()
                except Exception:
                    pass

        self._rich_scroll_canvas = canvas
        self._rich_hscroll = tk.Scrollbar(
            canvas,
            orient="horizontal",
            command=lambda *args: self._rich_scroll_command("x", *args),
        )
        self._rich_vscroll = tk.Scrollbar(
            canvas,
            orient="vertical",
            command=lambda *args: self._rich_scroll_command("y", *args),
        )

    def _rich_hide_scrollbars(self) -> None:
        for bar in (self._rich_hscroll, self._rich_vscroll):
            if bar is not None:
                try:
                    bar.place_forget()
                except Exception:
                    pass

    def _rich_axis_geometry(self, axis: str):
        canvas = getattr(self, "_composition_editor_canvas", None)
        view = getattr(self, "_composition_page_view", None)
        if canvas is None or not isinstance(view, dict):
            return None

        if axis == "x":
            viewport = max(1.0, float(canvas.winfo_width()))
            content = max(1.0, float(view.get("page_w", 1.0) or 1.0))
            pan = float(getattr(self, "_composition_pan_x", 0.0) or 0.0)
        else:
            viewport = max(1.0, float(canvas.winfo_height()))
            content = max(1.0, float(view.get("page_h", 1.0) or 1.0))
            pan = float(getattr(self, "_composition_pan_y", 0.0) or 0.0)

        maximum = max(0.0, (content - viewport) / 2.0)
        return canvas, viewport, content, pan, maximum

    def _rich_clamp_pan(self, canvas, page_w: float, page_h: float) -> None:
        width = max(1.0, float(canvas.winfo_width()))
        height = max(1.0, float(canvas.winfo_height()))

        max_x = max(0.0, (float(page_w) - width) / 2.0)
        max_y = max(0.0, (float(page_h) - height) / 2.0)

        pan_x = float(getattr(self, "_composition_pan_x", 0.0) or 0.0)
        pan_y = float(getattr(self, "_composition_pan_y", 0.0) or 0.0)

        self._composition_pan_x = max(-max_x, min(max_x, pan_x))
        self._composition_pan_y = max(-max_y, min(max_y, pan_y))

    def _rich_scroll_command(self, axis: str, *args) -> None:
        geometry = self._rich_axis_geometry(axis)
        if geometry is None or not args:
            return

        canvas, viewport, content, pan, maximum = geometry
        if maximum <= 0.0:
            return

        # offset 0 = bord gauche/haut de la page ; offset max = bord droit/bas.
        current_offset = maximum - pan
        maximum_offset = max(0.0, content - viewport)

        if args[0] == "moveto" and len(args) >= 2:
            try:
                fraction = float(args[1])
            except (TypeError, ValueError):
                return
            offset = fraction * content
        elif args[0] == "scroll" and len(args) >= 3:
            try:
                count = int(args[1])
            except (TypeError, ValueError):
                return
            unit = str(args[2])
            step = viewport * (0.82 if unit == "pages" else 0.09)
            offset = current_offset + count * step
        else:
            return

        offset = max(0.0, min(maximum_offset, offset))
        new_pan = maximum - offset

        if axis == "x":
            self._composition_pan_x = new_pan
        else:
            self._composition_pan_y = new_pan

        self._draw_rich_page(canvas)

    def _rich_update_scrollbars(self, canvas, view: dict) -> None:
        self._rich_ensure_scrollbars(canvas)

        width = max(1.0, float(canvas.winfo_width()))
        height = max(1.0, float(canvas.winfo_height()))
        page_w = max(1.0, float(view.get("page_w", 1.0) or 1.0))
        page_h = max(1.0, float(view.get("page_h", 1.0) or 1.0))

        pan_x = float(getattr(self, "_composition_pan_x", 0.0) or 0.0)
        pan_y = float(getattr(self, "_composition_pan_y", 0.0) or 0.0)

        bar_size = 15

        if page_w > width + 1.0:
            max_pan_x = (page_w - width) / 2.0
            first = (max_pan_x - pan_x) / page_w
            last = first + width / page_w
            first = max(0.0, min(1.0, first))
            last = max(first, min(1.0, last))
            self._rich_hscroll.set(first, last)
            self._rich_hscroll.place(
                x=0,
                rely=1.0,
                y=-bar_size,
                relwidth=1.0,
                width=-bar_size,
                height=bar_size,
            )
            self._rich_hscroll.lift()
        else:
            self._rich_hscroll.place_forget()

        if page_h > height + 1.0:
            max_pan_y = (page_h - height) / 2.0
            first = (max_pan_y - pan_y) / page_h
            last = first + height / page_h
            first = max(0.0, min(1.0, first))
            last = max(first, min(1.0, last))
            self._rich_vscroll.set(first, last)
            self._rich_vscroll.place(
                relx=1.0,
                x=-bar_size,
                y=0,
                width=bar_size,
                relheight=1.0,
                height=-bar_size,
            )
            self._rich_vscroll.lift()
        else:
            self._rich_vscroll.place_forget()

    def _composition_pan_motion(self, event):
        return super()._composition_pan_motion(event)

    def _rich_view_is_enlarged(self) -> bool:
        return float(
            getattr(self, "_composition_zoom_factor", 1.0) or 1.0
        ) >= 1.5

    def _rich_set_view_mode(self, enlarged: bool) -> None:
        if not self._rich_is_active_page():
            return

        canvas = getattr(self, "_composition_editor_canvas", None)
        if canvas is None:
            return

        # Deux etats seulement :
        # - 1.0 : Vue normale / Adapter
        # - 2.0 : Vue agrandie
        self._composition_zoom_factor = 2.0 if enlarged else 1.0

        # On repart centre. Le deplacement reste ensuite independant
        # via les barres / le panoramique deja presents.
        self._composition_pan_x = 0.0
        self._composition_pan_y = 0.0

        self._rich_update_view_controls()
        self._draw_rich_page(canvas)

    def _rich_toggle_view(self) -> None:
        self._rich_set_view_mode(
            not self._rich_view_is_enlarged()
        )

    def _rich_update_view_controls(self) -> None:
        """Remplace les commandes de zoom Rich Edit par un seul bouton."""
        fit_button = getattr(
            self,
            "_composition_zoom_fit_button",
            None,
        )
        if fit_button is None:
            return

        bar = getattr(fit_button, "master", None)
        if bar is None:
            return

        # Memorise la barre de zoom TomeLinea une seule fois afin de pouvoir
        # la restaurer sur les pages qui n'utilisent pas Rich Edit.
        if getattr(self, "_rich_view_toolbar_saved", None) is None:
            saved = []
            try:
                for child in bar.pack_slaves():
                    info = dict(child.pack_info())
                    info.pop("in", None)
                    saved.append((child, info))
            except Exception:
                saved = []
            self._rich_view_toolbar_saved = saved

        # En mode Rich Edit il n'existe plus de +, -, pourcentage ou Ajuster :
        # un seul bouton bascule entre les deux vues stables.
        try:
            for child in bar.pack_slaves():
                child.pack_forget()
        except Exception:
            pass

        try:
            fit_button.configure(
                text=(
                    "Vue normale"
                    if self._rich_view_is_enlarged()
                    else "Agrandir"
                ),
                command=self._rich_toggle_view,
                state="normal",
                width=12,
            )
            fit_button.pack(
                side="left",
                padx=(0, 0),
            )
        except Exception:
            pass

        zoom_var = getattr(self, "_composition_zoom_var", None)
        if zoom_var is not None:
            zoom_var.set(
                "Agrandie"
                if self._rich_view_is_enlarged()
                else "Normale"
            )

    def _rich_restore_view_controls(self) -> None:
        saved = getattr(self, "_rich_view_toolbar_saved", None)
        fit_button = getattr(
            self,
            "_composition_zoom_fit_button",
            None,
        )
        if not saved or fit_button is None:
            return

        bar = getattr(fit_button, "master", None)
        if bar is None:
            return

        try:
            for child in bar.pack_slaves():
                child.pack_forget()

            # Retablit les commandes et libelles originaux.
            zoom_out = getattr(
                self,
                "_composition_zoom_out_button",
                None,
            )
            zoom_in = getattr(
                self,
                "_composition_zoom_in_button",
                None,
            )
            if zoom_out is not None:
                zoom_out.configure(
                    text="−",
                    command=self._composition_zoom_out,
                    width=3,
                    state="normal",
                )
            if zoom_in is not None:
                zoom_in.configure(
                    text="+",
                    command=self._composition_zoom_in,
                    width=3,
                    state="normal",
                )
            fit_button.configure(
                text="Ajuster",
                command=self._composition_zoom_reset,
                width=0,
                state="normal",
            )

            for child, info in saved:
                child.pack(**info)
        except Exception:
            pass

    def _rich_pan_wheel(self, direction: int) -> None:
        """La molette parcourt la page uniquement en vue agrandie."""
        if not self._rich_is_active_page():
            return
        if not self._rich_view_is_enlarged():
            return

        canvas = getattr(self, "_composition_editor_canvas", None)
        view = getattr(self, "_composition_page_view", None)
        if canvas is None or not isinstance(view, dict):
            return

        # Une molette vers le haut remonte dans la page :
        # on deplace donc la page vers le bas.
        step = max(
            48.0,
            min(
                110.0,
                float(canvas.winfo_height()) * 0.10,
            ),
        )
        self._composition_pan_y = float(
            getattr(self, "_composition_pan_y", 0.0) or 0.0
        ) + (step if int(direction) > 0 else -step)

        self._rich_clamp_pan(
            canvas,
            float(view.get("page_w", 1.0) or 1.0),
            float(view.get("page_h", 1.0) or 1.0),
        )
        self._draw_rich_page(canvas)

    def _composition_zoom_wheel(self, event):
        if self._phase2_can_render():
            # La surface Canvas 2.35 gère sa propre molette.
            return None
        if self._canvas_editor_is_active_page():
            # Canvas Editor gère lui-même la molette dans la surface WebView2.
            return None
        if not self._rich_is_active_page():
            return super()._composition_zoom_wheel(event)

        # Plus aucun zoom a la molette.
        # En vue agrandie elle devient simplement un deplacement vertical.
        delta = int(getattr(event, "delta", 0) or 0)
        if delta > 0:
            self._rich_pan_wheel(1)
        elif delta < 0:
            self._rich_pan_wheel(-1)

        return "break"

    def _composition_zoom_in(self) -> None:
        if self._phase2_can_render():
            return
        if self._canvas_editor_is_active_page():
            self._canvas_set_view_mode(True)
            return
        if self._rich_is_active_page():
            self._rich_set_view_mode(True)
            return
        super()._composition_zoom_in()

    def _composition_zoom_out(self) -> None:
        if self._phase2_can_render():
            return
        if self._canvas_editor_is_active_page():
            self._canvas_set_view_mode(False)
            return
        if self._rich_is_active_page():
            self._rich_set_view_mode(False)
            return
        super()._composition_zoom_out()

    def _composition_zoom_reset(self) -> None:
        if self._phase2_can_render():
            return
        if self._canvas_editor_is_active_page():
            self._canvas_set_view_mode(False)
            return
        if self._rich_is_active_page():
            self._rich_set_view_mode(False)
            return
        super()._composition_zoom_reset()

    def _composition_set_zoom(
        self,
        value,
        *,
        anchor_x=None,
        anchor_y=None,
    ) -> None:
        if self._phase2_can_render():
            return
        if self._canvas_editor_is_active_page():
            self._canvas_set_view_mode(float(value) > 1.0)
            return

        if not self._rich_is_active_page():
            return super()._composition_set_zoom(
                value,
                anchor_x=anchor_x,
                anchor_y=anchor_y,
            )

        canvas = getattr(self, "_composition_editor_canvas", None)
        if canvas is None:
            return

        # Rich Edit n'accepte plus de valeurs intermediaires.
        # Toute demande devient soit Vue normale, soit Vue agrandie 200 %.
        new_zoom = 2.0 if float(value) >= 1.5 else 1.0
        self._composition_zoom_factor = new_zoom
        self._composition_pan_x = 0.0
        self._composition_pan_y = 0.0

        self._rich_update_view_controls()
        self._draw_rich_page(canvas)

    def _draw_rich_page(self, canvas) -> None:
        canvas.delete("all")

        page = self.session.active_page
        if page is None:
            self._rich_destroy_host(save=True)
            return

        page_index = self._rich_page_index(page)
        if page_index is None:
            self._rich_destroy_host(save=True)
            super()._draw_page(canvas)
            return

        book = self.session.book
        fmt = book.format

        width = max(canvas.winfo_width(), 100)
        height = max(canvas.winfo_height(), 100)

        fit_scale = min(
            (width - 140) / max(1.0, float(fmt.width_mm)),
            (height - 100) / max(1.0, float(fmt.height_mm)),
        )
        fit_scale = max(0.2, fit_scale)

        # Deux geometries fixes seulement. Aucun recalcul progressif.
        zoom = (
            2.0
            if float(
                getattr(self, "_composition_zoom_factor", 1.0) or 1.0
            ) >= 1.5
            else 1.0
        )
        self._composition_zoom_factor = zoom
        scale = fit_scale * zoom
        self._rich_update_view_controls()

        page_w = float(fmt.width_mm) * scale
        page_h = float(fmt.height_mm) * scale

        self._rich_clamp_pan(canvas, page_w, page_h)

        pan_x = float(getattr(self, "_composition_pan_x", 0.0) or 0.0)
        pan_y = float(getattr(self, "_composition_pan_y", 0.0) or 0.0)

        x = width / 2.0 - page_w / 2.0 + pan_x
        y = height / 2.0 - page_h / 2.0 + pan_y

        view = {
            "page_id": page.id,
            "x": x,
            "y": y,
            "page_w": page_w,
            "page_h": page_h,
            "scale": scale,
        }
        self._composition_page_view = view
        self._composition_page_views = {page.id: view}

        self._rich_update_scrollbars(canvas, view)

        # Même moteur d'interaction que la page Composition existante.
        canvas.bind("<Button-1>", self._composition_pointer_press)
        canvas.bind("<MouseWheel>", self._composition_zoom_wheel)
        canvas.bind("<Motion>", self._composition_pointer_hover)
        canvas.bind("<KeyPress-space>", self._composition_space_pan_press)
        canvas.bind("<KeyRelease-space>", self._composition_space_pan_release)
        canvas.bind("<B1-Motion>", self._composition_pointer_motion)
        canvas.bind("<ButtonRelease-1>", self._composition_pointer_release)
        canvas.bind("<plus>", lambda _event: self._composition_zoom_in())
        canvas.bind("<minus>", lambda _event: self._composition_zoom_out())
        canvas.bind("<KP_Add>", lambda _event: self._composition_zoom_in())
        canvas.bind("<KP_Subtract>", lambda _event: self._composition_zoom_out())

        canvas.create_rectangle(
            x,
            y,
            x + page_w,
            y + page_h,
            fill=theme.PAGE,
            outline=theme.PAGE_BORDER,
        )

        self._composition_draw_layout_guides(canvas, page, view)

        host = self._rich_ensure_host(canvas)
        if host is not None:
            host.layout(page, view, fmt, page_index)

        canvas.create_rectangle(
            x,
            y,
            x + page_w,
            y + page_h,
            fill="",
            outline=theme.PAGE_BORDER,
            width=1,
        )



    # ==========================================================
    # PHASE 2.36B — CANVAS 2.35 DANS LA VRAIE COMPOSITION
    # ==========================================================

    def _phase2_source_path(self) -> Path | None:
        """Retrouve la Source DOCX du Livre sans dépendre du moteur d'affichage."""
        session = getattr(self, "session", None)
        project = getattr(session, "project", None) if session is not None else None
        if project is None:
            return None

        # Compatibilité avec l'import DOCX interne actuellement présent dans la
        # coque restaurée. Cette métadonnée ne sert ici qu'à retrouver la Source.
        internal = project.metadata.get("internal_rich_document")
        if isinstance(internal, dict):
            raw = str(internal.get("source_path") or "").strip()
            if raw:
                candidate = Path(raw).expanduser()
                if candidate.suffix.lower() == ".docx" and candidate.is_file():
                    return candidate.resolve()

        # Chemin générique : la Source enregistrée dans le projet reste la
        # référence permanente, indépendamment de Rich Edit / Canvas.
        element_id = str(project.metadata.get("primary_source_element_id") or "")
        source_store = getattr(project, "source", None)
        elements = getattr(source_store, "elements", {}) if source_store is not None else {}
        element = elements.get(element_id) if element_id else None
        version = getattr(element, "active_version", None) if element is not None else None
        raw = str(getattr(version, "original_path", "") or "").strip()
        if raw:
            candidate = Path(raw).expanduser()
            if candidate.suffix.lower() == ".docx" and candidate.is_file():
                return candidate.resolve()
        return None

    def _phase2_active_page_index(self) -> int | None:
        session = getattr(self, "session", None)
        book = getattr(session, "book", None) if session is not None else None
        page = getattr(session, "active_page", None) if session is not None else None
        if book is None or page is None:
            return None

        metadata = getattr(page, "metadata", None)
        if isinstance(metadata, dict) and metadata.get("internal_rich_page"):
            try:
                return max(0, int(metadata.get("internal_rich_page_index", 0)))
            except (TypeError, ValueError):
                pass

        try:
            return list(book.page_order).index(str(page.id))
        except (ValueError, AttributeError):
            return None

    def _phase2_can_render(self) -> bool:
        return (
            str(getattr(self, "current_workspace", "")) == "composition"
            and getattr(self, "session", None) is not None
            and getattr(self.session, "book", None) is not None
            and self._phase2_source_path() is not None
            and self._phase2_active_page_index() is not None
        )

    def _phase2_state_file(self, source: Path) -> Path:
        marker = hashlib.sha256(str(source.resolve()).casefold().encode("utf-8")).hexdigest()[:20]
        return PROJECT_ROOT / ".tomelinea_runtime" / "editorial_state" / f"{marker}.json"

    def _phase2_cancel_poll(self) -> None:
        after_id = getattr(self, "_phase2_canvas_poll_after", None)
        if after_id is not None:
            try:
                self.after_cancel(after_id)
            except Exception:
                pass
        self._phase2_canvas_poll_after = None

    def _phase2_destroy_overlay(self) -> None:
        overlay = getattr(self, "_phase2_canvas_overlay", None)
        if overlay is not None:
            try:
                overlay.destroy()
            except Exception:
                pass
        self._phase2_canvas_overlay = None
        self._phase2_canvas_overlay_title = None
        self._phase2_canvas_overlay_detail = None

    def _phase2_show_overlay(self, canvas, title: str, detail: str = "") -> None:
        overlay = getattr(self, "_phase2_canvas_overlay", None)
        try:
            valid = overlay is not None and overlay.winfo_exists() and overlay.master is canvas
        except Exception:
            valid = False
        if not valid:
            self._phase2_destroy_overlay()
            overlay = tk.Frame(canvas, bg=theme.WINDOW_DEEP, bd=0, highlightthickness=0)
            overlay.place(x=0, y=0, relwidth=1, relheight=1)
            self._phase2_canvas_overlay = overlay
            self._phase2_canvas_overlay_title = tk.Label(
                overlay,
                text="",
                bg=theme.WINDOW_DEEP,
                fg=theme.INK,
                font=(theme.FONT_TITLE, 17, "bold"),
            )
            self._phase2_canvas_overlay_title.place(relx=0.5, rely=0.44, anchor="center")
            self._phase2_canvas_overlay_detail = tk.Label(
                overlay,
                text="",
                bg=theme.WINDOW_DEEP,
                fg=theme.MUTED,
                font=(theme.FONT_UI, 10),
                justify="center",
                wraplength=520,
            )
            self._phase2_canvas_overlay_detail.place(relx=0.5, rely=0.51, anchor="center")
        try:
            self._phase2_canvas_overlay_title.configure(text=str(title))
            self._phase2_canvas_overlay_detail.configure(text=str(detail or ""))
            overlay.lift()
        except Exception:
            pass

    def _phase2_destroy_host(self) -> None:
        host = getattr(self, "_phase2_canvas_host", None)
        if host is not None:
            try:
                host.shutdown()
            except Exception:
                pass
            try:
                host.destroy()
            except Exception:
                pass
        self._phase2_canvas_host = None
        self._phase2_canvas_key = None
        self._phase2_canvas_state = "idle"
        self._phase2_canvas_last_failure = None
        self._phase2_destroy_overlay()

    def _phase2_persist_choice(self, source: Path, event: dict) -> None:
        try:
            record_editorial_choice(self._phase2_state_file(source), source, event)
        except Exception:
            return
        try:
            self.session.project.touch()
        except Exception:
            pass

    def _phase2_sync_page_count(self, count: int) -> None:
        try:
            count = max(1, int(count))
        except (TypeError, ValueError):
            return

        metadata = self._rich_document_metadata()
        if metadata is not None:
            # Réutilise la mécanique Structure déjà stable de TomeLinea. Les
            # valeurs sont factices : Canvas reste seul propriétaire de la
            # pagination et des retours de ligne.
            self._rich_sync_pages(list(range(count)))
            metadata["canvas_page_count"] = count

        try:
            active_id = str(self.session.active_page_id or "")
            self._composition_render_plan(focus_page_id=(active_id or None), animate=False)
            self._composition_update_plan_selection()
            self._composition_refresh_center_navigation()
        except Exception:
            pass

    def _phase2_on_page_changed(self, event: dict) -> None:
        if self._phase2_canvas_syncing_page:
            return
        try:
            page_no = int(event.get("pageNo") or event.get("page_no") or 0)
        except (TypeError, ValueError):
            return
        if page_no < 1:
            return
        book = getattr(self.session, "book", None)
        if book is None:
            return
        order = list(book.page_order)
        if page_no > len(order):
            return
        page_id = str(order[page_no - 1])
        if page_id == str(self.session.active_page_id or ""):
            return
        self._phase2_canvas_syncing_page = True
        try:
            # Appelle directement la logique TomeLinea : le callback provient
            # du Canvas, il ne doit pas renvoyer immédiatement la même commande
            # au Canvas.
            TomeLineaV4Logic._activate_page(self, page_id)
        finally:
            self._phase2_canvas_syncing_page = False

    def _phase2_worker(self, generation: int, source: Path) -> None:
        try:
            project = getattr(getattr(self, "session", None), "project", None)
            substitutions = {}
            if project is not None:
                raw = project.metadata.get("font_substitutions")
                if isinstance(raw, dict):
                    substitutions = {str(k): dict(v) for k, v in raw.items() if isinstance(v, dict)}

            prepared = prepare_canvas_load(
                source,
                project_root=PROJECT_ROOT,
                font_substitutions=substitutions,
            )
            translated = build_canvas_editor_payload(prepared.canvas.contract)
            document = build_canvas_editor_document(translated.payload)
            if not prepared.ready or not translated.valid or not document.valid:
                raise RuntimeError("Préparation Canvas invalide avant rendu réel.")

            state = load_editorial_state(self._phase2_state_file(source), source)
            document.plan["persisted_editorial_choices"] = persisted_choices_for_plan(state)
            document.plan["visual_review"] = {
                "automatic_corrections": list(prepared.text_quality.automatic_corrections),
                "editorial_decisions": list(prepared.text_quality.editorial_decisions),
                "blocking_anomalies": list(prepared.text_quality.blocking_anomalies),
            }
            # Le contrôle éditorial sera raccordé à la colonne droite de TL à
            # l'étape suivante. Pour ce jalon, le panneau HTML du banc de test
            # est masqué afin de ne pas créer une seconde interface dans le centre.
            document.plan["tomelinea_ui"] = {"mode": "embedded_composition"}

            self._phase2_canvas_queue.put((generation, "ready", source, prepared, document))
        except Phase2BlockedError as exc:
            blockers = [
                {
                    "kind": item.code,
                    "message": item.message,
                    "solution": item.solution,
                    "details": item.details,
                }
                for item in exc.blockers
            ]
            self._phase2_canvas_queue.put((generation, "blocked", source, blockers))
        except Exception as exc:
            self._phase2_canvas_queue.put((
                generation,
                "error",
                source,
                {"stage": "preparation", "message": f"{type(exc).__name__}: {exc}"},
            ))

    def _phase2_start_analysis(self, canvas) -> None:
        source = self._phase2_source_path()
        if source is None:
            return
        key = str(source.resolve())
        if self._phase2_canvas_state in {"preparing", "rendering", "ready"} and self._phase2_canvas_key == key:
            return

        self._phase2_destroy_host()
        self._phase2_canvas_key = key
        self._phase2_canvas_state = "preparing"
        self._phase2_canvas_generation += 1
        generation = self._phase2_canvas_generation
        self._phase2_show_overlay(
            canvas,
            "Préparation de Composition",
            "Analyse du document, corrections certaines et préparation du moteur de page…",
        )
        threading.Thread(
            target=self._phase2_worker,
            args=(generation, source),
            daemon=True,
        ).start()
        self._phase2_schedule_poll(canvas)

    def _phase2_schedule_poll(self, canvas) -> None:
        self._phase2_cancel_poll()
        try:
            self._phase2_canvas_poll_after = self.after(60, lambda: self._phase2_poll(canvas))
        except Exception:
            self._phase2_canvas_poll_after = None

    def _phase2_poll(self, canvas) -> None:
        self._phase2_canvas_poll_after = None
        handled = False
        while True:
            try:
                item = self._phase2_canvas_queue.get_nowait()
            except queue.Empty:
                break
            generation, kind, source, payload, *rest = item
            if generation != self._phase2_canvas_generation:
                continue
            handled = True
            if kind == "ready":
                prepared = payload
                document = rest[0]
                self._phase2_begin_render(canvas, source, prepared, document)
            elif kind == "blocked":
                self._phase2_canvas_state = "blocked"
                blockers = payload if isinstance(payload, list) else []
                first = blockers[0] if blockers else {}
                self._phase2_show_overlay(
                    canvas,
                    "Composition suspendue",
                    str(first.get("message") or "TomeLinea a besoin d'une correction avant de poursuivre.")
                    + ("\n\n" + str(first.get("solution") or "") if first.get("solution") else ""),
                )
            else:
                self._phase2_canvas_state = "failed"
                self._phase2_canvas_last_failure = payload
                self._phase2_show_overlay(
                    canvas,
                    "Composition impossible",
                    str((payload or {}).get("message") or "Le moteur de composition n'a pas pu être préparé."),
                )
        if self._phase2_canvas_state == "preparing" and not handled:
            self._phase2_schedule_poll(canvas)

    def _phase2_begin_render(self, canvas, source: Path, prepared, document) -> None:
        self._phase2_canvas_state = "rendering"
        self._phase2_show_overlay(
            canvas,
            "Préparation de Composition",
            "Mise en page, pagination et vérification du livre…",
        )

        host = CanvasEditorWebHost(
            canvas,
            project_root=PROJECT_ROOT,
            on_ready=lambda snapshot: self._phase2_on_ready(canvas, snapshot),
            on_failed=lambda failure: self._phase2_on_failed(canvas, failure),
            on_editorial_choice=lambda event, src=source: self._phase2_persist_choice(src, event),
            on_page_changed=self._phase2_on_page_changed,
            background=theme.WINDOW_DEEP,
        )
        self._phase2_canvas_host = host
        # Le WebView2 a besoin d'une vraie géométrie pendant son rendu, mais il
        # reste sous l'écran de préparation jusqu'au signal render_complete.
        host.place(x=0, y=0, relwidth=1, relheight=1)
        try:
            host.lower()
        except Exception:
            pass
        try:
            host.load_document(document.plan, prepared.session)
        except Exception as exc:
            self._phase2_on_failed(
                canvas,
                {"stage": "load_document", "message": f"{type(exc).__name__}: {exc}"},
            )
            return
        try:
            self._phase2_canvas_overlay.lift()
        except Exception:
            pass

    def _phase2_on_ready(self, canvas, snapshot: dict) -> None:
        if str(getattr(self, "current_workspace", "")) != "composition":
            return
        self._phase2_canvas_state = "ready"
        page_count = snapshot.get("page_count") if isinstance(snapshot, dict) else None
        if page_count:
            self._phase2_sync_page_count(page_count)

        host = getattr(self, "_phase2_canvas_host", None)
        if host is None:
            return
        try:
            self._phase2_destroy_overlay()
            host.show_when_ready(x=0, y=0, relwidth=1, relheight=1)
        except Exception as exc:
            self._phase2_on_failed(canvas, {"stage": "show", "message": str(exc)})
            return

        index = self._phase2_active_page_index()
        if index is not None:
            host.go_to_page(index + 1, smooth=False)

    def _phase2_on_failed(self, canvas, failure: dict) -> None:
        self._phase2_canvas_state = "failed"
        self._phase2_canvas_last_failure = dict(failure or {})
        self._phase2_show_overlay(
            canvas,
            "Composition impossible",
            str((failure or {}).get("message") or "Le rendu Canvas n'a pas pu être terminé."),
        )

    def _draw_phase2_canvas_page(self, canvas) -> None:
        canvas.delete("all")
        self._rich_hide_scrollbars()

        source = self._phase2_source_path()
        if source is None:
            return
        key = str(source.resolve())

        host = getattr(self, "_phase2_canvas_host", None)
        if self._phase2_canvas_key != key:
            self._phase2_destroy_host()
            host = None

        if host is not None and self._phase2_canvas_state == "ready" and host.ready:
            try:
                host.place(x=0, y=0, relwidth=1, relheight=1)
                host.tk.call("raise", host._w)
                if host._web is not None:
                    host._web.sync_bounds()
            except Exception:
                pass
            index = self._phase2_active_page_index()
            if index is not None and not self._phase2_canvas_syncing_page:
                host.go_to_page(index + 1, smooth=False)
            return

        if self._phase2_canvas_state == "blocked":
            return
        if self._phase2_canvas_state == "failed":
            return
        if self._phase2_canvas_state in {"preparing", "rendering"}:
            self._phase2_show_overlay(
                canvas,
                "Préparation de Composition",
                "Mise en page et pagination du livre…",
            )
            return

        self.after_idle(lambda c=canvas: self._phase2_start_analysis(c))
        self._phase2_show_overlay(
            canvas,
            "Préparation de Composition",
            "Analyse du document avant affichage…",
        )

    # ==========================================================
    # CANVAS EDITOR / VRAIE PAGE
    # ==========================================================

    def _activate_page(
        self,
        page_id: str,
        *,
        preserve_page_selection: bool = False,
    ) -> None:
        """Navigation TomeLinea d'origine + affichage de la même page dans Canvas.

        Toutes les commandes existantes de TomeLinea convergent déjà vers
        _activate_page : clic Structure, Aller, Précédente et Suivante.
        On ne remplace donc aucune de ces fonctions. On laisse d'abord app.py
        faire tout son travail, puis Canvas affiche simplement la page active.
        """
        super()._activate_page(
            page_id,
            preserve_page_selection=preserve_page_selection,
        )

        if self.current_workspace != "composition":
            return

        if self._phase2_can_render():
            host = getattr(self, "_phase2_canvas_host", None)
            index = self._phase2_active_page_index()
            if (
                host is not None
                and host.ready
                and index is not None
                and not self._phase2_canvas_syncing_page
            ):
                host.go_to_page(index + 1, smooth=False)
            return

        host = getattr(self, "_canvas_page_host", None)
        if host is None:
            return

        page = self.session.active_page
        page_index = self._rich_page_index(page) if page is not None else None
        if page_index is None:
            return

        # Réponse immédiate.
        host.show_page(page_index)

        # Le redessin central de app.py peut se terminer juste après l'appel
        # à super(). On réaffirme donc UNE FOIS la page active au prochain
        # cycle Tk, sans modifier la sélection ni la navigation.
        try:
            self.after_idle(
                lambda h=host, i=int(page_index): h.show_page(i)
            )
        except Exception:
            pass

    def _canvas_view_is_enlarged(self) -> bool:
        return float(
            getattr(self, "_composition_zoom_factor", 1.0) or 1.0
        ) > 1.0

    def _canvas_set_view_mode(self, enlarged: bool) -> None:
        self._composition_zoom_factor = 1.5 if enlarged else 1.0

        host = getattr(self, "_canvas_page_host", None)
        if host is not None:
            host.set_scale(self._composition_zoom_factor)

        self._canvas_update_zoom_controls()

    def _canvas_toggle_view(self) -> None:
        self._canvas_set_view_mode(
            not self._canvas_view_is_enlarged()
        )

    def _canvas_find_zoom_label(self):
        label = getattr(self, "_canvas_zoom_label", None)
        if label is not None:
            try:
                if label.winfo_exists():
                    return label
            except Exception:
                pass

        fit_button = getattr(
            self,
            "_composition_zoom_fit_button",
            None,
        )
        zoom_var = getattr(
            self,
            "_composition_zoom_var",
            None,
        )
        if fit_button is None or zoom_var is None:
            return None

        bar = getattr(fit_button, "master", None)
        if bar is None:
            return None

        target_name = str(zoom_var)
        try:
            for child in bar.winfo_children():
                if not isinstance(child, tk.Label):
                    continue
                try:
                    if str(child.cget("textvariable")) == target_name:
                        self._canvas_zoom_label = child
                        return child
                except Exception:
                    continue
        except Exception:
            pass

        return None

    def _canvas_update_zoom_controls(self) -> None:
        """Canvas : un seul bouton, sans toucher aux autres outils du bandeau."""
        zoom_out = getattr(
            self,
            "_composition_zoom_out_button",
            None,
        )
        zoom_in = getattr(
            self,
            "_composition_zoom_in_button",
            None,
        )
        fit_button = getattr(
            self,
            "_composition_zoom_fit_button",
            None,
        )
        zoom_label = self._canvas_find_zoom_label()

        if fit_button is None:
            return

        if getattr(self, "_canvas_zoom_saved_pack", None) is None:
            saved = {}
            for name, widget in (
                ("out", zoom_out),
                ("label", zoom_label),
                ("in", zoom_in),
            ):
                if widget is None:
                    continue
                try:
                    info = dict(widget.pack_info())
                    info.pop("in", None)
                    saved[name] = (widget, info)
                except Exception:
                    pass
            self._canvas_zoom_saved_pack = saved

        # On masque UNIQUEMENT -, le pourcentage et +.
        # Le bouton Anomalies et tout le reste du bandeau restent intacts.
        for widget in (zoom_out, zoom_label, zoom_in):
            if widget is not None:
                try:
                    widget.pack_forget()
                except Exception:
                    pass

        try:
            fit_button.configure(
                text=(
                    "Vue normale"
                    if self._canvas_view_is_enlarged()
                    else "Agrandir"
                ),
                command=self._canvas_toggle_view,
                state=tk.NORMAL,
                width=12,
            )
        except Exception:
            pass

        zoom_var = getattr(self, "_composition_zoom_var", None)
        if zoom_var is not None:
            try:
                zoom_var.set(
                    "150 %"
                    if self._canvas_view_is_enlarged()
                    else "100 %"
                )
            except Exception:
                pass

    def _canvas_restore_zoom_controls(self) -> None:
        saved = getattr(self, "_canvas_zoom_saved_pack", None)
        if not saved:
            return

        fit_button = getattr(
            self,
            "_composition_zoom_fit_button",
            None,
        )
        if fit_button is not None:
            try:
                fit_button.configure(
                    text="Ajuster",
                    command=self._composition_zoom_reset,
                    width=0,
                    state=tk.NORMAL,
                )
            except Exception:
                pass

        # Réinstalle les trois éléments masqués avec leurs options d'origine.
        # On les replace avant le bouton Ajuster pour retrouver le bandeau TL.
        bar = getattr(fit_button, "master", None) if fit_button is not None else None
        if bar is not None:
            try:
                # Le plus sûr est de repacker dans l'ordre d'origine avant fit_button.
                for name in ("out", "label", "in"):
                    item = saved.get(name)
                    if item is None:
                        continue
                    widget, info = item
                    widget.pack(**info)
            except Exception:
                pass

    def _canvas_document_metadata(self):
        # Pendant la transition, on réutilise le document interne déjà
        # extrait du DOCX. Le moteur visuel devient Canvas Editor.
        return self._rich_document_metadata()

    def _canvas_editor_is_active_page(self) -> bool:
        page = getattr(self.session, "active_page", None)
        return (
            page is not None
            and self._rich_page_index(page) is not None
            and self._canvas_document_metadata() is not None
        )

    def _canvas_destroy_host(self) -> None:
        host = getattr(self, "_canvas_page_host", None)
        if host is not None:
            try:
                host.request_snapshot()
            except Exception:
                pass
            try:
                host.destroy()
            except Exception:
                pass
        self._canvas_page_host = None
        self._canvas_page_key = None

    def _canvas_snapshot_changed(self, _message=None) -> None:
        try:
            self.session.project.touch()
        except Exception:
            pass

    def _canvas_sync_page_count(self, count: int) -> None:
        count = max(1, int(count))
        if count == int(getattr(self, "_canvas_last_page_count", 0) or 0):
            return

        metadata = self._canvas_document_metadata()
        if metadata is None:
            return

        # _rich_sync_pages contient déjà la mécanique stable TomeLinea qui
        # crée/supprime les pages de Structure. Les valeurs n'ont désormais
        # plus le rôle de coupures Rich Edit : seul leur nombre est utilisé.
        self._rich_sync_pages(list(range(count)))
        metadata["canvas_page_count"] = count
        self._canvas_last_page_count = count

        try:
            active_id = str(self.session.active_page_id or "")
            self._composition_render_plan(
                focus_page_id=(active_id or None),
                animate=False,
            )
            self._composition_update_plan_selection()
            self._composition_refresh_center_navigation()
        except Exception:
            pass

    def _canvas_ensure_host(self, canvas):
        metadata = self._canvas_document_metadata()
        if metadata is None:
            self._canvas_destroy_host()
            return None

        key = (
            str(metadata.get("source_path", "")),
            str(metadata.get("kind", "")),
        )

        host = getattr(self, "_canvas_page_host", None)
        if host is not None and self._canvas_page_key == key:
            try:
                host.show()
                host.set_format(self.session.book.format)
            except Exception:
                pass
            return host

        self._canvas_destroy_host()

        # Le Rich Edit n'est plus la surface d'édition centrale.
        try:
            self._rich_destroy_host(save=False)
        except Exception:
            pass

        host = TLCanvasPageHost(
            self,
            canvas,
            metadata,
            self.session.book.format,
            on_snapshot=self._canvas_snapshot_changed,
            on_page_count=self._canvas_sync_page_count,
        )
        self._canvas_page_host = host
        self._canvas_page_key = key

        count = max(
            1,
            int(metadata.get("canvas_page_count", 1) or 1),
        )
        self._canvas_sync_page_count(count)
        return host

    def _draw_canvas_editor_page(self, canvas) -> None:
        # Le Canvas Tk reste uniquement le conteneur de la surface native
        # WebView2. La page blanche, les marges, le texte et la pagination
        # sont tous rendus par Canvas Editor.
        canvas.delete("all")
        self._rich_hide_scrollbars()

        host = self._canvas_ensure_host(canvas)
        if host is None:
            return

        page = self.session.active_page
        page_index = self._rich_page_index(page)
        if page_index is not None:
            host.show_page(page_index)

        # Géométrie TomeLinea -> moteur de page.
        host.set_format(self.session.book.format)

        zoom = 1.5 if self._canvas_view_is_enlarged() else 1.0
        self._composition_zoom_factor = zoom
        host.set_scale(zoom)
        self._canvas_update_zoom_controls()
        host.show()

    def _canvas_apply_current_format(self) -> None:
        host = getattr(self, "_canvas_page_host", None)
        if host is None:
            return
        try:
            host.set_format(self.session.book.format)
        except Exception:
            pass

    def _canvas_request_snapshot(self) -> None:
        host = getattr(self, "_canvas_page_host", None)
        if host is not None:
            try:
                host.request_snapshot()
            except Exception:
                pass

    def _draw_page(self, canvas) -> None:
        if self._phase2_can_render():
            self._draw_phase2_canvas_page(canvas)
            return

        if self._canvas_editor_is_active_page():
            self._draw_canvas_editor_page(canvas)
            return

        self._canvas_restore_zoom_controls()

        host = getattr(self, "_canvas_page_host", None)
        if host is not None:
            try:
                host.hide()
            except Exception:
                pass

        if self._rich_is_active_page():
            self._draw_rich_page(canvas)
            return

        self._rich_restore_view_controls()
        self._rich_hide_scrollbars()

        host = getattr(self, "_rich_host", None)
        if host is not None:
            try:
                host.hide()
            except Exception:
                pass

        super()._draw_page(canvas)

    def _composition_apply_general_settings(
        self,
        *,
        margin_top_mm=None,
        margin_bottom_mm=None,
        margin_inside_mm=None,
        margin_outside_mm=None,
        bleed_mm=None,
        composition_extent=None,
    ):
        result = super()._composition_apply_general_settings(
            margin_top_mm=margin_top_mm,
            margin_bottom_mm=margin_bottom_mm,
            margin_inside_mm=margin_inside_mm,
            margin_outside_mm=margin_outside_mm,
            bleed_mm=bleed_mm,
            composition_extent=composition_extent,
        )
        if result:
            self._canvas_apply_current_format()
        return result

    def _save_project(self) -> None:
        # Canvas Editor diffuse son état à chaque modification. On demande
        # aussi un instantané explicite au clic Enregistrer.
        self._canvas_request_snapshot()
        try:
            self._rich_commit_edits(repaginate=True)
        except Exception:
            pass
        super()._save_project()

    def _docx_source_dialog(self, title: str):
        return filedialog.askopenfilename(
            parent=self,
            title=title,
            filetypes=(
                ("Documents pris en charge", "*.docx *.pdf *.odt"),
                ("Document Word DOCX", "*.docx"),
                ("Document PDF", "*.pdf"),
                ("OpenDocument Texte", "*.odt"),
            ),
        )

    def _create_project_from_source(self) -> None:
        from src.v4.project import ProjectV4
        from src.v4.workspace import WorkspaceSessionV4

        filename = self._docx_source_dialog("Créer un livre TomeLinea")
        if not filename:
            return

        source_path = Path(filename)
        clean_title = " ".join(source_path.stem.replace("_", " ").strip().split()) or "Nouveau livre"

        self._begin_project_transition()
        try:
            project = ProjectV4(title=clean_title)
            self.session = WorkspaceSessionV4(project)
            self.project_path = None
            self.current_workspace = "composition"

            if not self._source_import_file(str(source_path)):
                self._rollback_project_transition()
        except Exception as exc:
            self._rollback_project_transition()
            messagebox.showerror(
                "TomeLinea V4",
                f"Le nouveau projet n'a pas pu être préparé.\n\n{exc}",
                parent=self,
            )

    def _source_import(self) -> None:
        if self.session.project.book is not None:
            messagebox.showinfo(
                "TomeLinea V4",
                "Le Livre existe déjà.\n\nL'ajout de contenu complémentaire sera traité séparément.",
                parent=self,
            )
            return

        filename = self._docx_source_dialog("Choisir la Source du livre")
        if not filename:
            return
        self._source_import_file(filename)

    def _source_import_file(self, filename: str) -> bool:
        if Path(filename).suffix.lower() != ".docx":
            return super()._source_import_file(filename)

        project = self.session.project
        source_path = Path(filename)

        try:
            element = project.source.register_file(source_path)
            version = element.active_version
            if version is None:
                raise RuntimeError("La version DOCX importée est introuvable.")

            internal = _tl_docx_internal_document(source_path)

            from src.v4.domain import BookFormat, BookKind, BookV4, PageOrigin, PageV4

            fmt_data = internal["format"]
            fmt = BookFormat(
                width_mm=float(fmt_data["width_mm"]),
                height_mm=float(fmt_data["height_mm"]),
                margin_top_mm=float(fmt_data["margin_top_mm"]),
                margin_bottom_mm=float(fmt_data["margin_bottom_mm"]),
                margin_inside_mm=float(fmt_data["margin_inside_mm"]),
                margin_outside_mm=float(fmt_data["margin_outside_mm"]),
            )

            starts = _tl_rich_api().paginate_rtf(
                base64.b64decode(internal["rtf_b64"]),
                fmt,
            )
            internal["page_starts"] = list(starts)
            internal["page_count"] = len(starts)
            internal["source_element_id"] = element.id
            internal["source_version_id"] = version.id

            book = BookV4(
                title=project.title,
                kind=BookKind.UNKNOWN,
                format=fmt,
            )
            book.metadata["internal_rich_document"] = True
            book.metadata["source_kind"] = "docx"

            for index, start in enumerate(starts):
                page = PageV4(
                    page_type="Page texte",
                    title=f"Page {index + 1}",
                    origin=PageOrigin.AUTHOR,
                    source=None,
                )
                page.metadata["internal_rich_page"] = True
                page.metadata["internal_rich_page_index"] = index
                page.metadata["internal_rich_page_start"] = int(start)
                book.add_page(page)

            project.metadata["primary_source_element_id"] = element.id
            project.metadata["internal_rich_document"] = internal
            project.metadata["source_import_mode"] = "docx_internal_simple"
            project.set_book(book)

            self.session.refresh_context()
            self.current_workspace = "composition"
            self._composition_book_state_open = False
            self._composition_text_flow_open = False
            self._composition_book_state_edit = False
            self._finish_project_transition()
            self.show_workspace("composition")

            return True

        except Exception as exc:
            messagebox.showerror(
                "TomeLinea V4",
                "Impossible d'importer le DOCX dans le document interne.\n\n" + str(exc),
                parent=self,
            )
            return False


    # ==========================================================
    # FENETRE
    # ==========================================================

    def _fit_to_work_area(
        self,
    ) -> None:

        try:
            import ctypes

            class RECT(
                ctypes.Structure
            ):
                _fields_ = [
                    (
                        "left",
                        ctypes.c_long,
                    ),
                    (
                        "top",
                        ctypes.c_long,
                    ),
                    (
                        "right",
                        ctypes.c_long,
                    ),
                    (
                        "bottom",
                        ctypes.c_long,
                    ),
                ]

            rect = RECT()

            SPI_GETWORKAREA = (
                0x0030
            )

            ok = (
                ctypes.windll.user32.SystemParametersInfoW(
                    SPI_GETWORKAREA,
                    0,
                    ctypes.byref(
                        rect
                    ),
                    0,
                )
            )

            if ok:
                width = max(
                    1100,
                    rect.right
                    - rect.left,
                )

                height = max(
                    700,
                    rect.bottom
                    - rect.top,
                )

                self.geometry(
                    (
                        f"{width}x{height}"
                        f"+{rect.left}"
                        f"+{rect.top}"
                    )
                )

                return

        except Exception:
            pass

        width = max(
            1100,
            self.winfo_screenwidth(),
        )

        height = max(
            700,
            self.winfo_screenheight()
            - 48,
        )

        self.geometry(
            f"{width}x{height}+0+0"
        )


    # ==========================================================
    # IMAGES
    # ==========================================================

    def _background_source(
        self,
        path: Path,
    ):

        key = str(
            path
        )

        cached = (
            self._editorial_bg_sources.get(
                key
            )
        )

        if cached is not None:
            return cached

        if not path.exists():
            return None

        image = Image.open(
            path
        ).convert(
            "RGB"
        )

        # Traitement doux validé dans l'esprit TomeLinea :
        # on évite le fond criard ou trop contrasté.
        image = (
            ImageEnhance.Color(
                image
            ).enhance(
                0.82
            )
        )

        image = (
            ImageEnhance.Brightness(
                image
            ).enhance(
                0.90
            )
        )

        self._editorial_bg_sources[
            key
        ] = image

        return image


    def _background_photo(
        self,
        path: Path,
        width: int,
        height: int,
        key: str,
    ):

        width = max(
            400,
            int(width),
        )

        height = max(
            300,
            int(height),
        )

        cache_key = (
            str(path),
            width,
            height,
            key,
        )

        cached = (
            self._editorial_bg_cache.get(
                cache_key
            )
        )

        if cached is not None:
            return cached

        source = (
            self._background_source(
                path
            )
        )

        if source is None:
            return None

        source_width, source_height = (
            source.size
        )

        scale = max(
            width / source_width,
            height / source_height,
        )

        resized_width = max(
            width,
            int(
                source_width
                * scale
            ),
        )

        resized_height = max(
            height,
            int(
                source_height
                * scale
            ),
        )

        image = source.resize(
            (
                resized_width,
                resized_height,
            ),
            Image.Resampling.LANCZOS,
        )

        left = max(
            0,
            (
                resized_width
                - width
            ) // 2,
        )

        top = max(
            0,
            (
                resized_height
                - height
            ) // 2,
        )

        image = image.crop(
            (
                left,
                top,
                left + width,
                top + height,
            )
        )

        photo = ImageTk.PhotoImage(
            image
        )

        if len(
            self._editorial_bg_cache
        ) > 10:
            self._editorial_bg_cache.clear()

        self._editorial_bg_cache[
            cache_key
        ] = photo

        return photo


    def _brand_icon_photo(
        self,
        size: int,
    ):

        size = int(
            size
        )

        cached = (
            self._brand_icon_cache.get(
                size
            )
        )

        if cached is not None:
            return cached

        if not BRAND_ICON.exists():
            return None

        image = Image.open(
            BRAND_ICON
        ).convert(
            "RGBA"
        )

        image.thumbnail(
            (
                size,
                size,
            ),
            Image.Resampling.LANCZOS,
        )

        photo = ImageTk.PhotoImage(
            image
        )

        self._brand_icon_cache[
            size
        ] = photo

        return photo


    def _brand_title_photo(
        self,
        width: int,
    ):

        width = int(
            width
        )

        cached = (
            self._brand_title_cache.get(
                width
            )
        )

        if cached is not None:
            return cached

        if not BRAND_TITLE.exists():
            return None

        image = Image.open(
            BRAND_TITLE
        ).convert(
            "RGBA"
        )

        ratio = (
            width
            / max(
                1,
                image.width,
            )
        )

        image = image.resize(
            (
                width,
                max(
                    1,
                    int(
                        image.height
                        * ratio
                    ),
                ),
            ),
            Image.Resampling.LANCZOS,
        )

        photo = ImageTk.PhotoImage(
            image
        )

        self._brand_title_cache[
            width
        ] = photo

        return photo


    # ==========================================================
    # ICONES LIGNE TOMELINEA
    # ==========================================================

    def _line_icon(
        self,
        kind: str,
        size: int = 34,
        color: str | None = None,
    ):
        """
        Pictogrammes TomeLinea V4.

        Trait fin, sans halo.
        Les trois couleurs rappellent les stations du logo :
        céladon, bleu doux et orang?.
        """

        cache_key = (
            "tl_v4_refined",
            kind,
            int(size),
        )

        cached = self._line_icon_cache.get(
            cache_key
        )

        if cached is not None:
            return cached

        scale = 4
        side = max(
            22,
            int(size),
        ) * scale

        image = Image.new(
            "RGBA",
            (side, side),
            (0, 0, 0, 0),
        )

        draw = ImageDraw.Draw(
            image
        )

        celadon = (
            127,
            184,
            174,
            255,
        )

        blue = (
            125,
            151,
            181,
            255,
        )

        orange = (
            210,
            132,
            94,
            255,
        )

        pale = (
            205,
            211,
            213,
            235,
        )

        quiet = (
            125,
            137,
            147,
            175,
        )

        stroke = max(
            4,
            int(side * 0.018),
        )

        thin = max(
            3,
            int(side * 0.012),
        )

        def p(x, y):
            return (
                int(x * side),
                int(y * side),
            )

        # ------------------------------------------------------
        # Ligne éditoriale commune aux trois pictogrammes.
        # ------------------------------------------------------

        draw.line(
            [
                p(0.15, 0.82),
                p(0.85, 0.82),
            ],
            fill=quiet,
            width=thin,
        )

        stations = (
            (0.30, celadon),
            (0.50, blue),
            (0.70, orange),
        )

        radius = max(
            4,
            int(side * 0.025),
        )

        for x, station_color in stations:
            cx, cy = p(
                x,
                0.82,
            )

            draw.ellipse(
                (
                    cx - radius,
                    cy - radius,
                    cx + radius,
                    cy + radius,
                ),
                fill=station_color,
            )

        # ------------------------------------------------------
        # CRÉER
        # Feuille éditoriale + ajout.
        # ------------------------------------------------------

        if kind == "create":

            draw.rounded_rectangle(
                [
                    p(0.25, 0.16),
                    p(0.63, 0.67),
                ],
                radius=max(
                    5,
                    int(side * 0.025),
                ),
                outline=pale,
                width=stroke,
            )

            # Deux lignes de composition.
            draw.line(
                [
                    p(0.33, 0.31),
                    p(0.54, 0.31),
                ],
                fill=blue,
                width=thin,
            )

            draw.line(
                [
                    p(0.33, 0.40),
                    p(0.50, 0.40),
                ],
                fill=celadon,
                width=thin,
            )

            # Petit + TomeLinea, détaché de la page.
            draw.line(
                [
                    p(0.70, 0.30),
                    p(0.70, 0.52),
                ],
                fill=orange,
                width=stroke,
            )

            draw.line(
                [
                    p(0.59, 0.41),
                    p(0.81, 0.41),
                ],
                fill=orange,
                width=stroke,
            )

        # ------------------------------------------------------
        # OUVRIR
        # Deux feuillets qui s'écartent.
        # ------------------------------------------------------

        elif kind == "open":

            draw.line(
                [
                    p(0.20, 0.25),
                    p(0.44, 0.18),
                    p(0.49, 0.63),
                    p(0.25, 0.67),
                    p(0.20, 0.25),
                ],
                fill=pale,
                width=stroke,
                joint="curve",
            )

            draw.line(
                [
                    p(0.49, 0.63),
                    p(0.54, 0.18),
                    p(0.78, 0.25),
                    p(0.73, 0.67),
                    p(0.49, 0.63),
                ],
                fill=pale,
                width=stroke,
                joint="curve",
            )

            draw.line(
                [
                    p(0.30, 0.34),
                    p(0.41, 0.31),
                ],
                fill=celadon,
                width=thin,
            )

            draw.line(
                [
                    p(0.58, 0.31),
                    p(0.69, 0.34),
                ],
                fill=orange,
                width=thin,
            )

            draw.line(
                [
                    p(0.49, 0.21),
                    p(0.49, 0.61),
                ],
                fill=blue,
                width=thin,
            )

        # ------------------------------------------------------
        # PROJET ACTIF
        # Petit livre assemblé / progression.
        # ------------------------------------------------------

        elif kind == "active":

            draw.rounded_rectangle(
                [
                    p(0.23, 0.17),
                    p(0.72, 0.66),
                ],
                radius=max(
                    5,
                    int(side * 0.025),
                ),
                outline=pale,
                width=stroke,
            )

            draw.line(
                [
                    p(0.33, 0.17),
                    p(0.33, 0.66),
                ],
                fill=blue,
                width=thin,
            )

            draw.line(
                [
                    p(0.42, 0.31),
                    p(0.62, 0.31),
                ],
                fill=celadon,
                width=thin,
            )

            draw.line(
                [
                    p(0.42, 0.42),
                    p(0.59, 0.42),
                ],
                fill=orange,
                width=thin,
            )

            # Marque-page très discret.
            draw.line(
                [
                    p(0.62, 0.17),
                    p(0.62, 0.40),
                    p(0.67, 0.35),
                    p(0.72, 0.40),
                    p(0.72, 0.18),
                ],
                fill=orange,
                width=thin,
            )

        else:

            draw.ellipse(
                [
                    p(0.28, 0.22),
                    p(0.72, 0.66),
                ],
                outline=pale,
                width=stroke,
            )

        image = image.resize(
            (
                int(size),
                int(size),
            ),
            Image.Resampling.LANCZOS,
        )

        photo = ImageTk.PhotoImage(
            image
        )

        self._line_icon_cache[
            cache_key
        ] = photo

        return photo

    # ==========================================================
    # BOUTON GLOBAL
    # ==========================================================

    def _button(
        self,
        parent,
        text: str,
        command,
        *,
        accent: bool = False,
        enabled: bool = True,
        compact: bool = False,
        width: int | None = None,
    ):

        return TLButton(
            parent,
            text,
            command,
            primary=accent,
            compact=compact,
            state=(
                "normal"
                if enabled
                else "disabled"
            ),
            width=width,
        )


    # ==========================================================
    # ACCUEIL
    # ==========================================================

    def show_home(
        self,
    ) -> None:

        self._clear()

        screen = tk.Frame(
            self,
            bg=theme.WINDOW_DEEP,
        )

        screen.pack(
            fill="both",
            expand=True,
        )

        background = tk.Label(
            screen,
            bg=theme.WINDOW_DEEP,
            bd=0,
        )

        background.place(
            x=0,
            y=0,
            relwidth=1,
            relheight=1,
        )

        def refresh_background(
            event,
        ):

            photo = (
                self._background_photo(
                    BACKGROUND_HOME,
                    event.width,
                    event.height,
                    "home",
                )
            )

            if photo is not None:
                background.configure(
                    image=photo
                )

                background.image = (
                    photo
                )

        screen.bind(
            "<Configure>",
            refresh_background,
            add="+",
        )

        # ------------------------------------------------------
        # IDENTITE
        # ------------------------------------------------------

        header = tk.Frame(
            screen,
            bg=theme.WINDOW_DEEP,
        )

        header.place(
            relx=0.085,
            rely=0.045,
            relwidth=0.83,
            relheight=0.145,
        )

        brand = tk.Frame(
            header,
            bg=theme.WINDOW_DEEP,
        )

        brand.place(
            relx=0,
            rely=0,
            relwidth=0.68,
            relheight=1,
        )

        icon = (
            self._brand_icon_photo(
                92
            )
        )

        if icon is not None:

            label = tk.Label(
                brand,
                image=icon,
                bg=theme.WINDOW_DEEP,
                bd=0,
            )

            label.image = icon

            label.place(
                x=0,
                y=2,
            )

        title = (
            self._brand_title_photo(
                455
            )
        )

        if title is not None:

            label = tk.Label(
                brand,
                image=title,
                bg=theme.WINDOW_DEEP,
                bd=0,
            )

            label.image = title

            label.place(
                x=110,
                y=8,
            )

        else:

            tk.Label(
                brand,
                text="TomeLinea",
                bg=theme.WINDOW_DEEP,
                fg=theme.INK,
                font=(
                    theme.FONT_TITLE,
                    34,
                ),
            ).place(
                x=110,
                y=10,
            )

        tk.Label(
            brand,
            text="V4",
            bg=theme.WINDOW_DEEP,
            fg=theme.ACCENT,
            font=(
                theme.FONT_UI,
                13,
                "bold",
            ),
        ).place(
            x=575,
            y=16,
        )

        tk.Label(
            brand,
            text=(
                "LA LIGNE ÉDITORIALE "
                "JUSQU’AU LIVRE"
            ),
            bg=theme.WINDOW_DEEP,
            fg=theme.ACCENT,
            font=(
                theme.FONT_UI,
                9,
                "bold",
            ),
        ).place(
            x=114,
            y=75,
        )

        # Aide et Préférences ne sont pas affichées tant que leurs
        # fonctions ne sont pas réellement disponibles. Sur l’Accueil,
        # tout élément qui ressemble à une commande doit être actionnable.

        close = tk.Label(
            header,
            text="✕",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(
                theme.FONT_UI,
                15,
                "bold",
            ),
            cursor="hand2",
            padx=8,
            pady=2,
        )

        close.place(
            relx=0.995,
            y=7,
            anchor="ne",
        )

        close.bind(
            "<Button-1>",
            lambda _event: (
                self.destroy()
            ),
        )

        close.bind(
            "<Enter>",
            lambda _event: (
                close.configure(
                    fg=theme.ERROR
                )
            ),
        )

        close.bind(
            "<Leave>",
            lambda _event: (
                close.configure(
                    fg=theme.INK
                )
            ),
        )

        # ------------------------------------------------------
        # TITRE ACCUEIL
        # ------------------------------------------------------

        intro = tk.Frame(
            screen,
            bg=theme.WINDOW_DEEP,
        )

        intro.place(
            relx=0.105,
            rely=0.235,
            relwidth=0.77,
            relheight=0.105,
        )

        tk.Label(
            intro,
            text="VOTRE LIVRE",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(
                theme.FONT_UI,
                14,
                "bold",
            ),
        ).pack(
            anchor="w"
        )

        tk.Label(
            intro,
            text=(
                "Un projet TomeLinea commence "
                "par sa Source. "
                "Le livre sera compris avant "
                "d'être organisé."
            ),
            bg=theme.WINDOW_DEEP,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                9,
            ),
        ).pack(
            anchor="w",
            pady=(5, 0),
        )

        # Ligne éditoriale / stations.
        line = tk.Canvas(
            intro,
            bg=theme.WINDOW_DEEP,
            height=15,
            bd=0,
            highlightthickness=0,
        )

        line.pack(
            fill="x",
            pady=(12, 0),
        )

        line.create_line(
            0,
            7,
            520,
            7,
            fill=theme.BORDER,
            width=1,
        )

        station_colors = (
            theme.ACCENT,
            "#8DA7C4",
            "#D28A6E",
        )

        for index, color in enumerate(
            station_colors
        ):
            x = (
                80
                + index * 175
            )

            line.create_oval(
                x - 4,
                3,
                x + 4,
                11,
                fill=color,
                outline="",
            )

        # ------------------------------------------------------
        # 3 ACTIONS — NOUVELLE LOGIQUE V4
        # ------------------------------------------------------

        # Les trois entrées sont pos?es directement
        # sur l'écran afin que le fond éditorial reste
        # visible entre elles.
        cards = screen

        active = (
            self.session is not None
        )

        active_name = (
            self.session.project.title
            if active
            else "Aucun projet actif"
        )

        self._home_action_panel(
            cards,
            column=0,
            icon_kind="create",
            title="Créer un projet",
            text=(
                "Créer l'espace de travail, "
                "puis apporter la Source du livre."
            ),
            button="Créer",
            command=(
                self._create_project_dialog
            ),
            primary=True,
        )

        self._home_action_panel(
            cards,
            column=1,
            icon_kind="open",
            title="Ouvrir",
            text=(
                "Ouvrir un projet TomeLinea V4 "
                "déjà enregistré."
            ),
            button="Ouvrir un projet",
            command=self._open_project,
        )

        self._home_action_panel(
            cards,
            column=2,
            icon_kind="active",
            title="Projet actif",
            text=active_name,
            button="Accéder au projet",
            command=lambda: (
                self.show_workspace(
                    self.current_workspace
                )
            ),
            enabled=active,
        )



    def _home_action_panel(
        self,
        parent,
        *,
        column: int,
        icon_kind: str,
        title: str,
        text: str,
        button: str,
        command,
        primary: bool = False,
        enabled: bool = True,
    ) -> None:

        # Même matière pour les trois entrées :
        # l'action principale est indiqu?e par le contenu,
        # pas par un énorme encadrement coloré.
        panel = CutPanel(
            parent,
            fill="#252C35",
            border="#44505A",
            cut=10,
            padding=(
                18,
                15,
            ),
        )

        positions = {
            0: 0.120,
            1: 0.385,
            2: 0.650,
        }

        panel.place(
            relx=positions[column],
            rely=0.405,
            relwidth=0.230,
            relheight=0.285,
        )

        body = panel.body

        # Petit bandeau supérieur, plus proche d'une station
        # que d'une carte d'application.
        top = tk.Frame(
            body,
            bg="#252C35",
        )

        top.pack(
            fill="x",
            pady=(0, 9),
        )

        icon = self._line_icon(
            icon_kind,
            36,
        )

        icon_label = tk.Label(
            top,
            image=icon,
            bg="#252C35",
            bd=0,
        )

        icon_label.image = icon

        icon_label.pack(
            side="left"
        )

        # Trait éditorial discret.
        rule = tk.Canvas(
            top,
            width=72,
            height=12,
            bg="#252C35",
            bd=0,
            highlightthickness=0,
        )

        rule.pack(
            side="left",
            padx=(11, 0),
        )

        rule.create_line(
            1,
            6,
            68,
            6,
            fill=(
                theme.ACCENT
                if primary
                else theme.BORDER
            ),
            width=1,
        )

        rule.create_oval(
            30,
            3,
            36,
            9,
            fill=(
                theme.ACCENT
                if primary
                else theme.MUTED_DARK
            ),
            outline="",
        )


        tk.Label(
            body,
            text=title,
            bg="#252C35",
            fg=theme.INK,
            font=(
                theme.FONT_TITLE,
                15,
                "bold",
            ),
        ).pack(
            anchor="w",
            pady=(3, 6),
        )

        tk.Label(
            body,
            text=text,
            bg="#252C35",
            fg=theme.MUTED,
            justify="left",
            wraplength=230,
            font=(
                theme.FONT_UI,
                8,
            ),
        ).pack(
            anchor="w"
        )

        tk.Frame(
            body,
            bg="#252C35",
            height=9,
        ).pack(
            fill="x"
        )

        tk.Frame(
            body,
            bg="#252C35",
        ).pack(
            fill="both",
            expand=True,
        )

        self._button(
            body,
            button,
            command,
            accent=primary,
            enabled=enabled,
            compact=True,
        ).pack(
            anchor="w",
            pady=(5, 2),
        )

    # ==========================================================
    # CREATION — AUCUN TYPE DE LIVRE
    # ==========================================================

    def _create_project_dialog(
        self,
    ) -> None:

        # Le cas normal ne nécessite plus
        # de dialogue de création.
        #
        # L'utilisateur choisit directement
        # le document original.
        self._create_project_from_source()

    def _build_workspace_header(
        self,
        parent,
    ) -> None:

        has_book = (
            self.session.project.book
            is not None
        )

        bar = tk.Frame(
            parent,
            bg=theme.WINDOW_DEEP,
            height=68,
        )

        bar.pack(
            fill="x"
        )

        bar.pack_propagate(
            False
        )

        # Accueil.
        left = tk.Frame(
            bar,
            bg=theme.WINDOW_DEEP,
        )

        left.pack(
            side="left",
            fill="y",
            padx=(18, 10),
        )

        self._button(
            left,
            "Accueil",
            self.show_home,
            compact=True,
        ).pack(
            side="left",
            pady=17,
        )

        # Marque compacte.
        brand = tk.Frame(
            left,
            bg=theme.WINDOW_DEEP,
        )

        brand.pack(
            side="left",
            padx=(17, 20),
            pady=8,
        )

        icon = self._brand_icon_photo(
            42
        )

        if icon is not None:

            label = tk.Label(
                brand,
                image=icon,
                bg=theme.WINDOW_DEEP,
                bd=0,
            )

            label.image = icon

            label.pack(
                side="left"
            )

        title = (
            self._brand_title_photo(
                150
            )
        )

        if title is not None:

            label = tk.Label(
                brand,
                image=title,
                bg=theme.WINDOW_DEEP,
                bd=0,
            )

            label.image = title

            label.pack(
                side="left",
                padx=(7, 0),
            )

        # Navigation.
        nav = tk.Frame(
            bar,
            bg=theme.WINDOW_DEEP,
        )

        nav.pack(
            side="left",
            fill="y",
        )

        for key, label in theme.NAV_ITEMS:

            enabled = (
                key == "source"
                or has_book
            )

            active = (
                key
                == self.current_workspace
            )

            wrap = tk.Frame(
                nav,
                bg=theme.WINDOW_DEEP,
            )

            wrap.pack(
                side="left",
                fill="y",
                padx=3,
            )

            button = tk.Button(
                wrap,
                text=label,
                command=lambda k=key: (
                    self.show_workspace(
                        k
                    )
                ),
                state=(
                    tk.NORMAL
                    if enabled
                    else tk.DISABLED
                ),
                bg=theme.WINDOW_DEEP,
                fg=(
                    theme.ACCENT_BRIGHT
                    if active
                    else theme.MUTED
                ),
                disabledforeground=theme.MUTED_DARK,
                activebackground=theme.WINDOW_DEEP,
                activeforeground=theme.WHITE,
                relief="flat",
                bd=0,
                padx=12,
                pady=8,
                font=(
                    theme.FONT_UI,
                    9,
                    (
                        "bold"
                        if active
                        else "normal"
                    ),
                ),
                cursor=(
                    "hand2"
                    if enabled
                    else "arrow"
                ),
            )

            button.pack(
                pady=(13, 0),
            )

            tk.Frame(
                wrap,
                bg=(
                    theme.ACCENT
                    if active
                    else theme.WINDOW_DEEP
                ),
                height=2,
            ).pack(
                fill="x",
                padx=8,
            )

        # Outils à droite.
        right = tk.Frame(
            bar,
            bg=theme.WINDOW_DEEP,
        )

        right.pack(
            side="right",
            fill="y",
            padx=(10, 18),
        )

        close = tk.Label(
            right,
            text="✕",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(
                theme.FONT_UI,
                13,
                "bold",
            ),
            cursor="hand2",
            padx=8,
        )

        close.pack(
            side="right",
            pady=20,
            padx=(8, 0),
        )

        close.bind(
            "<Button-1>",
            lambda _event: (
                self.destroy()
            ),
        )

        close.bind(
            "<Enter>",
            lambda _event: (
                close.configure(
                    fg=theme.ERROR
                )
            ),
        )

        close.bind(
            "<Leave>",
            lambda _event: (
                close.configure(
                    fg=theme.INK
                )
            ),
        )

        self._button(
            right,
            "Enregistrer",
            self._save_project,
            accent=True,
            compact=True,
        ).pack(
            side="right",
            pady=17,
            padx=4,
        )

        # IMPORTANT : le bandeau éditorial remplace entièrement celui de
        # TomeLineaV4. Il doit donc conserver les références aux mêmes
        # commandes d'historique et raccorder explicitement la session.
        # Sans cela, les boutons restent dans l'état calculé à l'ouverture
        # et ne voient jamais les nouvelles entrées Undo/Redo.
        self._workspace_redo_button = self._button(
            right,
            "Rétablir",
            self._redo,
            compact=True,
            enabled=True,
        )
        self._workspace_redo_button.pack(
            side="right",
            pady=17,
            padx=3,
        )

        self._workspace_undo_button = self._button(
            right,
            "Annuler",
            self._undo,
            compact=True,
            enabled=True,
        )
        self._workspace_undo_button.pack(
            side="right",
            pady=17,
            padx=3,
        )

        # Le moteur d'historique notifie immédiatement le bandeau après
        # chaque transaction, y compris Ajouter/Supprimer une page, les
        # contraintes et les futures modifications de texte.
        self.session.set_history_change_callback(
            self._refresh_history_buttons
        )

        # Synchronisation initiale après construction des widgets.
        self._refresh_history_buttons()


    # ==========================================================
    # SOURCE — PEAU TOMELINEA
    # ==============================================================


    def _build_source(
        self,
        parent,
    ) -> None:
        """
        Compatibilité interne uniquement.

        Source n'est plus un bureau utilisateur.
        Le moteur Source reste actif dans src.v4.
        """

        project = self.session.project

        if project.book is not None:
            self.current_workspace = "composition"

            self.after_idle(
                lambda: self.show_workspace(
                    "composition"
                )
            )

            return

        # Ce cas ne doit normalement plus être visible :
        # la création attend simplement que l'analyse construise
        # le Livre avant d'ouvrir Composition.
        tk.Label(
            parent,
            text="Préparation du livre\u2026",
            bg=theme.WINDOW_DEEP,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                10,
            ),
        ).pack(
            expand=True,
        )

    def _summary_value(
        self,
        parent,
        label: str,
        value: str,
    ) -> None:

        tk.Label(
            parent,
            text=label,
            bg="#252C35",
            fg=theme.MUTED_DARK,
            font=(
                theme.FONT_UI,
                8,
                "bold",
            ),
        ).pack(
            anchor="w",
            pady=(12, 2),
        )

        tk.Label(
            parent,
            text=value,
            bg="#252C35",
            fg=theme.INK,
            font=(
                theme.FONT_UI,
                10,
            ),
        ).pack(
            anchor="w"
        )


    # ==========================================================
    # HISTORIQUE — RAFRAICHISSEMENT SANS RECONSTRUCTION COMPLETE
    # ==============================================================

    def _undo(
        self,
    ) -> None:

        # Dans Composition, utiliser le rafraichissement ciblé de
        # TomeLineaV4. Le chemin générique appelle show_workspace(),
        # détruit le bureau puis le reconstruit entièrement et provoque
        # le flash visible lors d'Annuler/Rétablir.
        if self.current_workspace == "composition":
            self._composition_undo()
            return

        super()._undo()


    def _redo(
        self,
    ) -> None:

        if self.current_workspace == "composition":
            self._composition_redo()
            return

        super()._redo()


    # ==========================================================
    # BARRE BASSE
    # ==============================================================

    def _build_status(
        self,
        parent,
    ) -> None:

        bar = tk.Frame(
            parent,
            bg="#1E242C",
            height=27,
        )

        bar.pack(
            fill="x",
            side="bottom",
        )

        bar.pack_propagate(
            False
        )

        path_text = (
            str(
                self.project_path
            )
            if self.project_path
            else "Projet non enregistré"
        )

        tk.Label(
            bar,
            text=path_text,
            bg="#1E242C",
            fg=theme.MUTED_DARK,
            font=(
                theme.FONT_UI,
                8,
            ),
        ).pack(
            side="left",
            padx=14,
        )

        phase = (
            "Source · Analyse"
            if self.session.project.book
            is None
            else (
                self.current_workspace.capitalize()
            )
        )

        tk.Label(
            bar,
            text=(
                f"TomeLinea V4   •   {phase}"
            ),
            bg="#1E242C",
            fg=theme.ACCENT_DARK,
            font=(
                theme.FONT_UI,
                8,
                "bold",
            ),
        ).pack(
            side="right",
            padx=14,
        )
