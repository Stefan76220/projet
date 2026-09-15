from __future__ import annotations

"""TomeLinea V4 — Phase 2, étape 1.

Construit un document interne prêt à être remis au moteur Canvas à partir du
modèle factuel Phase 1. Aucun Canvas n'est créé ici et aucune pagination n'est
calculée manuellement.
"""

from copy import deepcopy
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
from typing import Any
import json
import os
import sys
import zipfile
import xml.etree.ElementTree as ET

PHASE1_SCHEMA = "tomelinea-source-model-phase1"
PHASE1_VERSION = 4
PHASE2_SCHEMA = "tomelinea-internal-document-phase2"
PHASE2_VERSION = 1
ENGINE_NAME = "tomelinea.source_phase2"
ENGINE_VERSION = "1"

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
FONT_EXTENSIONS = {".ttf", ".otf", ".ttc"}


def _q(name: str) -> str:
    return f"{{{W}}}{name}"


def _key(value: str) -> str:
    return "".join(ch.lower() for ch in str(value or "") if ch.isalnum())


def _style_key(value: str) -> str:
    raw = _key(value)
    bold = any(token in raw for token in ("bold", "semibold", "demibold"))
    italic = any(token in raw for token in ("italic", "oblique"))
    if bold and italic:
        return "bold_italic"
    if bold:
        return "bold"
    if italic:
        return "italic"
    return "regular"


def _json_hash(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(raw.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class Phase2Blocker:
    code: str
    message: str
    details: dict[str, Any]
    solution: str


class Phase2BlockedError(RuntimeError):
    def __init__(self, blockers: list[Phase2Blocker]):
        self.blockers = tuple(blockers)
        super().__init__("Phase 2 bloquée : " + "; ".join(item.message for item in blockers))


@dataclass(frozen=True, slots=True)
class Phase2Result:
    model: dict[str, Any]
    ready_for_canvas: bool
    blockers: tuple[Phase2Blocker, ...]


def _validate_phase1(model: dict[str, Any]) -> None:
    if model.get("schema") != PHASE1_SCHEMA:
        raise ValueError(f"Schéma Phase 1 inattendu : {model.get('schema')!r}")
    if int(model.get("schema_version") or 0) < PHASE1_VERSION:
        raise ValueError(
            f"Phase 1 trop ancienne : version {model.get('schema_version')!r}, "
            f"version minimale {PHASE1_VERSION}."
        )
    document = model.get("document")
    if not isinstance(document, dict):
        raise ValueError("Phase 1 invalide : document absent.")
    if not isinstance(document.get("paragraphs"), list):
        raise ValueError("Phase 1 invalide : paragraphes absents.")
    if not isinstance(document.get("sections"), list) or not document["sections"]:
        raise ValueError("Phase 1 invalide : sections absentes.")


def _source_path(model: dict[str, Any]) -> Path:
    raw = str(model.get("source", {}).get("path") or "").strip()
    if not raw:
        raise ValueError("Phase 1 invalide : chemin source absent.")
    return Path(raw).expanduser().resolve()


def _check_source_fingerprint(model: dict[str, Any], source: Path) -> None:
    expected = str(model.get("source", {}).get("sha256") or "").strip().lower()
    if not expected:
        return
    digest = sha256()
    with source.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    actual = digest.hexdigest().lower()
    if actual != expected:
        raise ValueError("Le DOCX source a changé depuis l'analyse Phase 1.")


def _build_body_flow(model: dict[str, Any]) -> list[dict[str, Any]]:
    """Récupère uniquement l'ordre des blocs du corps DOCX.

    La Phase 1 a déjà normalisé les paragraphes et tableaux. Ici on ne relit
    aucune propriété éditoriale : on rattache seulement les blocs normalisés à
    leur ordre top-level dans word/document.xml.
    """
    source = _source_path(model)
    if not source.is_file():
        raise FileNotFoundError(f"DOCX source introuvable : {source}")
    _check_source_fingerprint(model, source)

    with zipfile.ZipFile(source, "r") as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
    body = root.find(_q("body"))
    if body is None:
        raise ValueError("DOCX sans corps w:body exploitable.")

    paragraph_index = {id(node): index for index, node in enumerate(body.iter(_q("p")), start=1)}
    table_index = {id(node): index for index, node in enumerate(body.iter(_q("tbl")), start=1)}

    paragraphs = {int(item["paragraph"]): item for item in model["document"].get("paragraphs", [])}
    tables = {int(item["table"]): item for item in model["document"].get("tables", [])}

    flow: list[dict[str, Any]] = []
    position = 0
    for child in list(body):
        if child.tag == _q("p"):
            idx = paragraph_index[id(child)]
            source_item = paragraphs.get(idx)
            if source_item is None:
                raise ValueError(f"Paragraphe Phase 1 introuvable : {idx}")
            position += 1
            flow.append({
                "position": position,
                "kind": "paragraph",
                "source_paragraph": idx,
                "text": source_item.get("text", ""),
                "direct": deepcopy(source_item.get("direct", {})),
                "effective": deepcopy(source_item.get("effective", {})),
                "style_chain": deepcopy(source_item.get("paragraph_style_chain", [])),
                "runs": deepcopy(source_item.get("runs", [])),
            })
        elif child.tag == _q("tbl"):
            idx = table_index[id(child)]
            source_item = tables.get(idx)
            if source_item is None:
                raise ValueError(f"Tableau Phase 1 introuvable : {idx}")
            position += 1
            flow.append({
                "position": position,
                "kind": "table",
                "source_table": idx,
                "table": deepcopy(source_item),
            })
        elif child.tag == _q("sectPr"):
            # Propriétés finales déjà normalisées dans document.sections.
            continue
        else:
            position += 1
            flow.append({
                "position": position,
                "kind": "unsupported_body_node",
                "tag": child.tag.rsplit("}", 1)[-1],
            })
    return flow


def _section_contract(model: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in model["document"].get("sections", []):
        props = item.get("properties", {})
        page = props.get("page", {})
        margins = props.get("margins", {})
        width = page.get("width_mm")
        height = page.get("height_mm")
        if not width or not height:
            raise ValueError(f"Section {item.get('section')} : format physique incomplet.")
        required_margins = ("top_mm", "right_mm", "bottom_mm", "left_mm")
        if any(margins.get(name) is None for name in required_margins):
            raise ValueError(f"Section {item.get('section')} : marges physiques incomplètes.")
        columns = deepcopy(props.get("columns", {}))
        columns.setdefault("count", 1)
        result.append({
            "section": item.get("section"),
            "start_paragraph": item.get("start_paragraph"),
            "end_paragraph": item.get("end_paragraph"),
            "page": deepcopy(page),
            "margins": deepcopy(margins),
            "columns": columns,
            "document_grid": deepcopy(props.get("document_grid", {})),
            "section_break_type": props.get("section_break_type"),
            "header_footer_references": deepcopy(props.get("header_footer_references", [])),
        })
    return result


def _font_dirs(project_root: Path) -> list[tuple[str, Path]]:
    dirs: list[tuple[str, Path]] = []
    if sys.platform == "win32":
        windir = Path(os.environ.get("WINDIR", r"C:\Windows"))
        dirs.append(("system", windir / "Fonts"))
        local = os.environ.get("LOCALAPPDATA", "").strip()
        if local:
            dirs.append(("system", Path(local) / "Microsoft" / "Windows" / "Fonts"))
    elif sys.platform == "darwin":
        dirs.extend([
            ("system", Path("/System/Library/Fonts")),
            ("system", Path("/Library/Fonts")),
            ("system", Path.home() / "Library" / "Fonts"),
        ])
    else:
        dirs.extend([
            ("system", Path("/usr/share/fonts")),
            ("system", Path("/usr/local/share/fonts")),
            ("system", Path.home() / ".local" / "share" / "fonts"),
            ("system", Path.home() / ".fonts"),
        ])

    # Ordre volontaire : système -> bibliothèque TL core -> bibliothèque TL user.
    dirs.append(("tomelinea_core", project_root / "resources" / "fonts" / "core"))
    dirs.append(("tomelinea_user", project_root / "resources" / "fonts" / "user"))
    return dirs


@lru_cache(maxsize=8)
def _font_inventory(project_root_text: str) -> tuple[tuple[str, str, str, str], ...]:
    try:
        from PIL import ImageFont
    except ImportError as exc:
        raise RuntimeError("Pillow est requis pour vérifier les polices.") from exc

    project_root = Path(project_root_text)
    result: list[tuple[str, str, str, str]] = []
    seen: set[str] = set()
    for origin, folder in _font_dirs(project_root):
        if not folder.is_dir():
            continue
        try:
            paths = folder.rglob("*")
            for path in paths:
                if not path.is_file() or path.suffix.lower() not in FONT_EXTENSIONS:
                    continue
                marker = str(path).casefold()
                if marker in seen:
                    continue
                seen.add(marker)
                try:
                    font = ImageFont.truetype(str(path), size=12)
                    family, style = font.getname()
                except Exception:
                    continue
                family = str(family or "").strip()
                if not family:
                    continue
                result.append((family, _style_key(str(style or "")), str(path), origin))
        except OSError:
            continue
    return tuple(result)


def clear_font_inventory_cache() -> None:
    """Force un nouveau scan des polices après une intervention utilisateur."""

    _font_inventory.cache_clear()


def list_available_font_faces(project_root: str | Path | None = None) -> list[dict[str, str]]:
    """Liste les faces réellement disponibles pour un choix explicite utilisateur."""

    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd().resolve()
    rows = [
        {"family": family, "style": style, "path": path, "origin": origin}
        for family, style, path, origin in _font_inventory(str(root))
    ]
    rows.sort(key=lambda item: (item["family"].casefold(), item["style"]))
    return rows


def resolve_font_requirements(
    model: dict[str, Any],
    project_root: str | Path | None = None,
    *,
    font_substitutions: dict[str, dict[str, str]] | None = None,
) -> list[dict[str, Any]]:
    root = Path(project_root).expanduser().resolve() if project_root else Path.cwd().resolve()
    inventory = _font_inventory(str(root))
    substitutions = font_substitutions or {}
    requirements = model.get("fonts", {}).get("used_faces", [])
    if not requirements:
        requirements = [
            {"family": family, "style": "regular"}
            for family in model.get("fonts", {}).get("used_families", [])
        ]

    resolved: list[dict[str, Any]] = []
    for requirement in requirements:
        family = str(requirement.get("family") or "").strip()
        style = _style_key(str(requirement.get("style") or "regular"))
        same_family = [item for item in inventory if _key(item[0]) == _key(family)]
        exact = next((item for item in same_family if item[1] == style), None)
        substitution_key = f"{_key(family)}::{style}"
        substitution = substitutions.get(substitution_key) or substitutions.get(_key(family))
        substitution_match = None
        if exact is None and isinstance(substitution, dict):
            target_family = str(substitution.get("family") or "").strip()
            target_style = _style_key(str(substitution.get("style") or style))
            substitution_match = next((
                item for item in inventory
                if _key(item[0]) == _key(target_family) and item[1] == target_style
            ), None)
        if exact is not None:
            status = "exact"
            match = exact
            substituted = False
        elif substitution_match is not None:
            status = "substituted"
            match = substitution_match
            substituted = True
        elif same_family:
            status = "missing_face"
            match = same_family[0]
            substituted = False
        else:
            status = "missing_family"
            match = None
            substituted = False
        resolved.append({
            "family": family,
            "style": style,
            "status": status,
            "resolved_family": match[0] if match else None,
            "resolved_style": match[1] if match else None,
            "path": match[2] if match else None,
            "origin": match[3] if match else None,
            "substituted": substituted,
        })
    return resolved


def build_phase2_model(
    phase1_model: dict[str, Any],
    *,
    project_root: str | Path | None = None,
    enforce_font_gate: bool = True,
    font_substitutions: dict[str, dict[str, str]] | None = None,
) -> Phase2Result:
    _validate_phase1(phase1_model)

    source = _source_path(phase1_model)
    flow = _build_body_flow(phase1_model)
    sections = _section_contract(phase1_model)
    font_resolution = resolve_font_requirements(phase1_model, project_root=project_root, font_substitutions=font_substitutions)

    blockers: list[Phase2Blocker] = []
    unsupported = [item for item in flow if item["kind"] == "unsupported_body_node"]
    # Nouveau contrat d'import : un élément local inconnu n'empêche pas
    # l'ouverture du Livre. Il reste inventorié pour le contrôle d'intégrité et
    # sera présenté au Survol. Seule une impossibilité globale de lecture doit
    # bloquer l'import.

    missing_fonts = [item for item in font_resolution if item["status"] not in {"exact", "substituted"}]
    # Une police absente ne doit plus empêcher l'ouverture du document.
    # Le nom Source reste conservé dans le modèle et le cas sera présenté
    # à l'utilisateur après ouverture, sans substitution silencieuse.
    document = phase1_model["document"]
    model = {
        "schema": PHASE2_SCHEMA,
        "schema_version": PHASE2_VERSION,
        "engine": {"name": ENGINE_NAME, "version": ENGINE_VERSION},
        "source": deepcopy(phase1_model.get("source", {})),
        "phase1_model_sha256": _json_hash(phase1_model),
        "unit_contract": deepcopy(phase1_model.get("unit_contract", {})),
        "readiness": {
            "ready_for_canvas": not blockers,
            "canvas_created": False,
            "pagination_computed_by_tomelinea": False,
            "manual_line_coordinates": False,
            "font_issues": deepcopy(missing_fonts),
            "local_import_issues": deepcopy(unsupported),
            "blockers": [
                {"code": item.code, "message": item.message, "details": item.details, "solution": item.solution}
                for item in blockers
            ],
        },
        "fonts": {
            "requirements": deepcopy(phase1_model.get("fonts", {}).get("used_faces", [])),
            "resolution": font_resolution,
            "ready": not missing_fonts,
        },
        "sections": sections,
        "flow": flow,
        "resources": {
            "images": deepcopy(document.get("images", [])),
            "headers_footers": deepcopy(document.get("headers_footers", [])),
            "footnotes": deepcopy(document.get("footnotes", [])),
            "endnotes": deepcopy(document.get("endnotes", [])),
            "comments": deepcopy(document.get("comments", [])),
            "hyperlinks": deepcopy(document.get("hyperlinks", [])),
            "bookmarks": deepcopy(document.get("bookmarks", [])),
            "content_controls": deepcopy(document.get("content_controls", [])),
            "tracked_changes": deepcopy(document.get("tracked_changes", {})),
            "tracked_change_ranges": deepcopy(document.get("tracked_change_ranges", [])),
        },
        "counts": {
            "top_level_blocks": len(flow),
            "paragraph_blocks": sum(item["kind"] == "paragraph" for item in flow),
            "table_blocks": sum(item["kind"] == "table" for item in flow),
            "sections": len(sections),
            "images": len(document.get("images", [])),
        },
    }

    result = Phase2Result(model=model, ready_for_canvas=not blockers, blockers=tuple(blockers))
    if enforce_font_gate and blockers:
        raise Phase2BlockedError(blockers)
    return result


def analyze_docx_to_phase2(
    source: str | Path,
    *,
    project_root: str | Path | None = None,
    enforce_font_gate: bool = True,
    font_substitutions: dict[str, dict[str, str]] | None = None,
) -> Phase2Result:
    from src.v4.docx_phase1 import analyze_docx_phase1

    phase1 = analyze_docx_phase1(source)
    return build_phase2_model(
        phase1.model,
        project_root=project_root,
        enforce_font_gate=enforce_font_gate,
        font_substitutions=font_substitutions,
    )
