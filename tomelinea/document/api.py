from __future__ import annotations

"""Document logique TomeLinea V5.

V5-28A introduit le premier état éditable du manuscrit avant Book et avant
toute pagination. Le module ne crée aucun Canvas, aucune page et n'applique
aucune règle éditoriale.

La Source DOCX reste intacte. ``TLDocument`` conserve :
- le texte et l'ordre logique ;
- les paragraphes, runs, tableaux, images et sections ;
- les propriétés Source nécessaires au futur jumeau visuel ;
- une provenance stable pour chaque objet ;
- les objets auxiliaires (notes, commentaires, en-têtes/pieds, etc.).

Le contrôle d'intégrité compare aussi le modèle directement au OOXML brut afin
qu'une omission de l'ancien analyseur Phase 1 ne puisse pas être masquée.
"""

from copy import deepcopy
from dataclasses import dataclass, field
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import Any
import json
import zipfile
import xml.etree.ElementTree as ET

from src.v4.docx_phase1 import analyze_docx_phase1


TLDOCUMENT_SCHEMA = "tomelinea-logical-document"
TLDOCUMENT_VERSION = 1

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
V = "urn:schemas-microsoft-com:vml"
PKG_REL = "http://schemas.openxmlformats.org/package/2006/relationships"

NS = {
    "w": W,
    "r": R,
    "a": A,
    "v": V,
    "rel": PKG_REL,
}

_TRANSPARENT_CONTAINERS = {
    "sdt",
    "sdtContent",
    "customXml",
    "smartTag",
    "ins",
    "del",
    "moveFrom",
    "moveTo",
}


def _q(ns: str, name: str) -> str:
    return f"{{{NS[ns]}}}{name}"


def _local(tag: str) -> str:
    return str(tag).rsplit("}", 1)[-1]


def _deepcopy_dict(value: Any) -> dict[str, Any]:
    return deepcopy(value) if isinstance(value, dict) else {}


def _raw_run_text(run: ET.Element) -> str:
    parts: list[str] = []
    for node in run.iter():
        if node.tag in {_q("w", "t"), _q("w", "delText")}:
            parts.append(node.text or "")
        elif node.tag == _q("w", "tab"):
            parts.append("\t")
        elif node.tag in {_q("w", "br"), _q("w", "cr")}:
            parts.append("\n")
        elif node.tag == _q("w", "noBreakHyphen"):
            parts.append("‑")
        elif node.tag == _q("w", "softHyphen"):
            parts.append("\u00ad")
    return "".join(parts)


def _raw_paragraph_text(paragraph: ET.Element) -> str:
    return "".join(_raw_run_text(run) for run in paragraph.findall(".//w:r", NS))


def _resolve_relationship_part(base_part: str, target: str) -> str:
    target = str(target or "").replace("\\", "/")
    if target.startswith("/"):
        return target.lstrip("/")
    base = PurePosixPath(base_part).parent
    combined = base / target
    parts: list[str] = []
    for item in combined.parts:
        if item in {"", "."}:
            continue
        if item == "..":
            if parts:
                parts.pop()
            continue
        parts.append(item)
    return "/".join(parts)


def _document_relationships(archive: zipfile.ZipFile) -> dict[str, dict[str, str]]:
    name = "word/_rels/document.xml.rels"
    try:
        root = ET.fromstring(archive.read(name))
    except KeyError:
        return {}
    result: dict[str, dict[str, str]] = {}
    for rel in root.findall("rel:Relationship", NS):
        rel_id = str(rel.get("Id") or "")
        if not rel_id:
            continue
        target = str(rel.get("Target") or "")
        mode = str(rel.get("TargetMode") or "Internal")
        result[rel_id] = {
            "target": target,
            "target_mode": mode,
            "part": target if mode == "External" else _resolve_relationship_part("word/document.xml", target),
        }
    return result


@dataclass(slots=True)
class TLRun:
    id: str
    source_paragraph: int
    source_run: int
    text: str
    direct: dict[str, Any] = field(default_factory=dict)
    effective: dict[str, Any] = field(default_factory=dict)
    character_style_chain: list[str] = field(default_factory=list)
    controls: list[dict[str, Any]] = field(default_factory=list)
    image_ids: list[str] = field(default_factory=list)


@dataclass(slots=True)
class TLParagraph:
    id: str
    source_paragraph: int
    text: str
    para_id: str | None = None
    text_id: str | None = None
    direct: dict[str, Any] = field(default_factory=dict)
    effective: dict[str, Any] = field(default_factory=dict)
    style_chain: list[str] = field(default_factory=list)
    runs: list[TLRun] = field(default_factory=list)
    bookmark_names: list[str] = field(default_factory=list)
    container_path: str | None = None


@dataclass(slots=True)
class TLTable:
    id: str
    source_table: int
    source_facts: dict[str, Any]
    container_path: str | None = None
    cell_children: dict[str, list[str]] = field(default_factory=dict)


@dataclass(slots=True)
class TLImage:
    id: str
    source_index: int
    scope: str
    facts: dict[str, Any]


@dataclass(slots=True)
class TLSection:
    id: str
    source_section: int
    start_paragraph: int | None
    end_paragraph: int | None
    properties: dict[str, Any]


@dataclass(slots=True)
class TLDocument:
    """Manuscrit logique indépendant de la pagination et du moteur de rendu."""

    source_path: str
    source_name: str
    source_sha256: str
    paragraphs: dict[str, TLParagraph]
    tables: dict[str, TLTable]
    images: dict[str, TLImage]
    sections: dict[str, TLSection]
    body_order: list[str]
    unsupported_nodes: list[dict[str, Any]]
    auxiliary: dict[str, Any]
    source_metadata: dict[str, Any]
    source_warnings: list[str]
    schema: str = TLDOCUMENT_SCHEMA
    schema_version: int = TLDOCUMENT_VERSION

    @property
    def counts(self) -> dict[str, int]:
        return {
            "paragraphs": len(self.paragraphs),
            "tables": len(self.tables),
            "images": len(self.images),
            "body_images": sum(image.scope == "body" for image in self.images.values()),
            "sections": len(self.sections),
            "body_blocks": len(self.body_order),
        }

    def validate(self) -> None:
        if self.schema != TLDOCUMENT_SCHEMA:
            raise ValueError(f"Schéma TLDocument inattendu : {self.schema!r}")
        if self.schema_version != TLDOCUMENT_VERSION:
            raise ValueError(f"Version TLDocument inattendue : {self.schema_version!r}")
        if not self.source_sha256:
            raise ValueError("TLDocument sans empreinte Source.")

        all_ids = set(self.paragraphs) | set(self.tables) | set(self.images) | set(self.sections)
        expected = (
            len(self.paragraphs)
            + len(self.tables)
            + len(self.images)
            + len(self.sections)
        )
        if len(all_ids) != expected:
            raise ValueError("Identifiants TLDocument non uniques.")

        valid_body_ids = set(self.paragraphs) | set(self.tables)
        unknown = [item for item in self.body_order if item not in valid_body_ids]
        if unknown:
            raise ValueError(f"body_order contient des objets inconnus : {unknown[:5]}")

        for paragraph in self.paragraphs.values():
            for run in paragraph.runs:
                if run.source_paragraph != paragraph.source_paragraph:
                    raise ValueError(f"Run {run.id} rattaché au mauvais paragraphe.")

    def paragraph_texts_in_source_order(self) -> list[str]:
        return [
            self.paragraphs[key].text
            for key in sorted(
                self.paragraphs,
                key=lambda item: self.paragraphs[item].source_paragraph,
            )
        ]


@dataclass(frozen=True, slots=True)
class RawDocxProbe:
    paragraph_texts: tuple[str, ...]
    paragraph_count: int
    table_count: int
    body_image_count: int
    linked_image_count: int
    body_order: tuple[str, ...]
    unsupported_nodes: tuple[dict[str, Any], ...]
    relationships: dict[str, dict[str, str]]


@dataclass(frozen=True, slots=True)
class IntegrityReport:
    source_path: str
    checks: dict[str, bool]
    raw_counts: dict[str, int]
    phase1_counts: dict[str, int]
    tl_counts: dict[str, int]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    unplaced_paragraphs: tuple[str, ...]
    unplaced_tables: tuple[str, ...]
    unsupported_nodes: tuple[dict[str, Any], ...]

    @property
    def ready_for_visual_twin(self) -> bool:
        return not self.blockers and all(self.checks.values())

    def to_text(self) -> str:
        def ok(value: bool) -> str:
            return "OK" if value else "ECHEC"

        lines = [
            "TOMELINEA V5-28A — TLDOCUMENT / INTEGRITE DOCX",
            "=" * 62,
            f"Source : {self.source_path}",
            "",
            "COMPTAGES",
            f"  Paragraphes : OOXML {self.raw_counts.get('paragraphs', 0)} | "
            f"Phase1 {self.phase1_counts.get('paragraphs', 0)} | "
            f"TLDocument {self.tl_counts.get('paragraphs', 0)}",
            f"  Tableaux     : OOXML {self.raw_counts.get('tables', 0)} | "
            f"Phase1 {self.phase1_counts.get('tables', 0)} | "
            f"TLDocument {self.tl_counts.get('tables', 0)}",
            f"  Images corps : OOXML {self.raw_counts.get('body_images', 0)} | "
            f"Phase1 {self.phase1_counts.get('body_images', 0)} | "
            f"TLDocument {self.tl_counts.get('body_images', 0)}",
            f"  Images total : Phase1 {self.phase1_counts.get('images', 0)} | "
            f"TLDocument {self.tl_counts.get('images', 0)}",
            f"  Sections     : Phase1 {self.phase1_counts.get('sections', 0)} | "
            f"TLDocument {self.tl_counts.get('sections', 0)}",
            "",
            "CONTROLES",
        ]
        for name, value in self.checks.items():
            lines.append(f"  {ok(value):5s}  {name}")

        if self.unplaced_paragraphs:
            lines.extend([
                "",
                "PARAGRAPHES SANS POSITION LOGIQUE",
                "  " + ", ".join(self.unplaced_paragraphs[:30]),
            ])
        if self.unplaced_tables:
            lines.extend([
                "",
                "TABLEAUX SANS POSITION LOGIQUE",
                "  " + ", ".join(self.unplaced_tables[:30]),
            ])
        if self.unsupported_nodes:
            lines.extend(["", "NOEUDS OOXML HORS PROFIL"])
            for item in self.unsupported_nodes[:30]:
                lines.append(
                    "  - "
                    + str(item.get("tag") or "?")
                    + " @ "
                    + str(item.get("path") or "?")
                )

        if self.blockers:
            lines.extend(["", "BLOCAGES AVANT JUMEAU VISUEL"])
            lines.extend(f"  - {item}" for item in self.blockers)

        if self.warnings:
            lines.extend(["", "AVERTISSEMENTS"])
            lines.extend(f"  - {item}" for item in self.warnings)

        lines.extend([
            "",
            "VERDICT",
            "  PRET POUR LE JUMEAU VISUEL"
            if self.ready_for_visual_twin
            else "  A TRAITER AVANT DE CONSTRUIRE LE JUMEAU VISUEL",
            "",
            "Aucune pagination TomeLinea, aucune correction et aucune règle "
            "éditoriale n'ont été exécutées par ce banc.",
        ])
        return "\n".join(lines)


def _probe_docx(source: Path) -> tuple[RawDocxProbe, dict[str, str], dict[str, dict[str, list[str]]]]:
    with zipfile.ZipFile(source, "r") as archive:
        root = ET.fromstring(archive.read("word/document.xml"))
        relationships = _document_relationships(archive)

    body = root.find("w:body", NS)
    if body is None:
        raise ValueError("DOCX sans corps w:body exploitable.")

    paragraphs = list(body.iter(_q("w", "p")))
    tables = list(body.iter(_q("w", "tbl")))
    paragraph_index = {id(node): index for index, node in enumerate(paragraphs, start=1)}
    table_index = {id(node): index for index, node in enumerate(tables, start=1)}

    locations: dict[str, str] = {}
    table_cell_children: dict[str, dict[str, list[str]]] = {}
    unsupported: list[dict[str, Any]] = []
    body_order: list[str] = []

    def walk_children(children: list[ET.Element], path: str, sink: list[str]) -> None:
        for child in children:
            local = _local(child.tag)

            if child.tag == _q("w", "p"):
                key = f"p:{paragraph_index[id(child)]:06d}"
                locations.setdefault(key, path)
                sink.append(key)
                continue

            if child.tag == _q("w", "tbl"):
                key = f"t:{table_index[id(child)]:06d}"
                locations.setdefault(key, path)
                sink.append(key)
                walk_table(child, key, path)
                continue

            if child.tag in {_q("w", "sectPr"), _q("w", "tcPr")}:
                continue

            if local in _TRANSPARENT_CONTAINERS:
                walk_children(list(child), f"{path}/{local}", sink)
                continue

            has_content = (
                child.find(".//w:p", NS) is not None
                or child.find(".//w:tbl", NS) is not None
            )
            unsupported.append({
                "tag": local,
                "path": path,
                "reason": "conteneur_non_normalise" if has_content else "noeud_non_pris_en_charge",
            })
            if has_content:
                walk_children(list(child), f"{path}/{local}", sink)

    def walk_table(table: ET.Element, table_key: str, parent_path: str) -> None:
        cells_map: dict[str, list[str]] = {}
        for row_no, row in enumerate(table.findall("w:tr", NS), start=1):
            for cell_no, cell in enumerate(row.findall("w:tc", NS), start=1):
                cell_key = f"r{row_no}:c{cell_no}"
                sink: list[str] = []
                cells_map[cell_key] = sink
                walk_children(
                    list(cell),
                    f"{parent_path}/{table_key}/{cell_key}",
                    sink,
                )
        table_cell_children[table_key] = cells_map

    walk_children(list(body), "body", body_order)

    paragraph_texts = tuple(_raw_paragraph_text(item) for item in paragraphs)
    body_image_count = (
        len(body.findall(".//w:drawing", NS))
        + len(body.findall(".//v:imagedata", NS))
    )
    linked_image_count = 0
    for blip in body.findall(".//a:blip", NS):
        if blip.get(_q("r", "link")):
            linked_image_count += 1

    return (
        RawDocxProbe(
            paragraph_texts=paragraph_texts,
            paragraph_count=len(paragraphs),
            table_count=len(tables),
            body_image_count=body_image_count,
            linked_image_count=linked_image_count,
            body_order=tuple(body_order),
            unsupported_nodes=tuple(unsupported),
            relationships=relationships,
        ),
        locations,
        table_cell_children,
    )


def build_tldocument_from_docx(path: str | Path) -> tuple[TLDocument, IntegrityReport]:
    source = Path(path).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.suffix.lower() != ".docx":
        raise ValueError("V5-28A attend un fichier DOCX.")

    raw_probe, locations, table_cell_children = _probe_docx(source)
    phase1 = analyze_docx_phase1(source)
    model = phase1.model
    document_facts = model.get("document", {})

    phase1_paragraphs = list(document_facts.get("paragraphs", []))
    phase1_tables = list(document_facts.get("tables", []))
    phase1_images = list(document_facts.get("images", []))
    phase1_sections = list(document_facts.get("sections", []))

    main_image_count = sum(
        int(run.get("image_count") or 0)
        for paragraph in phase1_paragraphs
        for run in paragraph.get("runs", [])
    )

    images: dict[str, TLImage] = {}
    body_image_ids_by_anchor: dict[tuple[int, int], list[str]] = {}
    for index, facts in enumerate(phase1_images, start=1):
        image_id = f"img:{index:06d}"
        scope = "body" if index <= main_image_count else "auxiliary"
        images[image_id] = TLImage(
            id=image_id,
            source_index=index,
            scope=scope,
            facts=deepcopy(facts),
        )
        if scope == "body":
            key = (
                int(facts.get("paragraph_index") or 0),
                int(facts.get("run_index") or 0),
            )
            body_image_ids_by_anchor.setdefault(key, []).append(image_id)

    paragraphs: dict[str, TLParagraph] = {}
    for facts in phase1_paragraphs:
        source_paragraph = int(facts.get("paragraph") or 0)
        paragraph_id = f"p:{source_paragraph:06d}"
        runs: list[TLRun] = []
        for run_facts in facts.get("runs", []):
            source_run = int(run_facts.get("run") or 0)
            run_id = f"{paragraph_id}:r:{source_run:04d}"
            runs.append(
                TLRun(
                    id=run_id,
                    source_paragraph=source_paragraph,
                    source_run=source_run,
                    text=str(run_facts.get("text") or ""),
                    direct=_deepcopy_dict(run_facts.get("direct")),
                    effective=_deepcopy_dict(run_facts.get("effective")),
                    character_style_chain=list(
                        deepcopy(run_facts.get("character_style_chain", []))
                    ),
                    controls=list(deepcopy(run_facts.get("controls", []))),
                    image_ids=list(
                        body_image_ids_by_anchor.get(
                            (source_paragraph, source_run),
                            [],
                        )
                    ),
                )
            )

        paragraphs[paragraph_id] = TLParagraph(
            id=paragraph_id,
            source_paragraph=source_paragraph,
            text=str(facts.get("text") or ""),
            para_id=facts.get("para_id"),
            text_id=facts.get("text_id"),
            direct=_deepcopy_dict(facts.get("direct")),
            effective=_deepcopy_dict(facts.get("effective")),
            style_chain=list(deepcopy(facts.get("paragraph_style_chain", []))),
            runs=runs,
            bookmark_names=list(deepcopy(facts.get("bookmark_names", []))),
            container_path=locations.get(paragraph_id),
        )

    tables: dict[str, TLTable] = {}
    for facts in phase1_tables:
        source_table = int(facts.get("table") or 0)
        table_id = f"t:{source_table:06d}"
        tables[table_id] = TLTable(
            id=table_id,
            source_table=source_table,
            source_facts=deepcopy(facts),
            container_path=locations.get(table_id),
            cell_children=deepcopy(table_cell_children.get(table_id, {})),
        )

    sections: dict[str, TLSection] = {}
    for facts in phase1_sections:
        source_section = int(facts.get("section") or 0)
        section_id = f"sec:{source_section:04d}"
        sections[section_id] = TLSection(
            id=section_id,
            source_section=source_section,
            start_paragraph=facts.get("start_paragraph"),
            end_paragraph=facts.get("end_paragraph"),
            properties=_deepcopy_dict(facts.get("properties")),
        )

    auxiliary = {
        "headers_footers": deepcopy(document_facts.get("headers_footers", [])),
        "footnotes": deepcopy(document_facts.get("footnotes", [])),
        "endnotes": deepcopy(document_facts.get("endnotes", [])),
        "comments": deepcopy(document_facts.get("comments", [])),
        "hyperlinks": deepcopy(document_facts.get("hyperlinks", [])),
        "bookmarks": deepcopy(document_facts.get("bookmarks", [])),
        "content_controls": deepcopy(document_facts.get("content_controls", [])),
        "tracked_changes": deepcopy(document_facts.get("tracked_changes", {})),
        "tracked_change_ranges": deepcopy(document_facts.get("tracked_change_ranges", [])),
        "field_instructions": deepcopy(document_facts.get("field_instructions", [])),
    }

    source_metadata = {
        "package": deepcopy(model.get("package", {})),
        "properties": deepcopy(model.get("properties", {})),
        "styles": deepcopy(model.get("styles", {})),
        "numbering": deepcopy(model.get("numbering", {})),
        "fonts": deepcopy(model.get("fonts", {})),
        "settings": deepcopy(model.get("settings", {})),
        "unit_contract": deepcopy(model.get("unit_contract", {})),
    }

    logical = TLDocument(
        source_path=str(source),
        source_name=source.name,
        source_sha256=str(model.get("source", {}).get("sha256") or ""),
        paragraphs=paragraphs,
        tables=tables,
        images=images,
        sections=sections,
        body_order=list(raw_probe.body_order),
        unsupported_nodes=list(deepcopy(raw_probe.unsupported_nodes)),
        auxiliary=auxiliary,
        source_metadata=source_metadata,
        source_warnings=list(deepcopy(model.get("warnings", []))),
    )
    logical.validate()

    phase1_paragraph_texts = tuple(
        str(item.get("text") or "")
        for item in phase1_paragraphs
    )
    tl_paragraph_texts = tuple(logical.paragraph_texts_in_source_order())

    unplaced_paragraphs = tuple(
        paragraph.id
        for paragraph in logical.paragraphs.values()
        if not paragraph.container_path
    )
    unplaced_tables = tuple(
        table.id
        for table in logical.tables.values()
        if not table.container_path
    )

    phase1_counts = {
        "paragraphs": len(phase1_paragraphs),
        "tables": len(phase1_tables),
        "images": len(phase1_images),
        "body_images": main_image_count,
        "sections": len(phase1_sections),
    }
    raw_counts = {
        "paragraphs": raw_probe.paragraph_count,
        "tables": raw_probe.table_count,
        "body_images": raw_probe.body_image_count,
        "linked_images": raw_probe.linked_image_count,
        "body_blocks": len(raw_probe.body_order),
    }
    tl_counts = logical.counts

    checks = {
        "OOXML -> Phase1 : nombre de paragraphes": raw_counts["paragraphs"] == phase1_counts["paragraphs"],
        "OOXML -> Phase1 : texte exact des paragraphes": raw_probe.paragraph_texts == phase1_paragraph_texts,
        "OOXML -> Phase1 : nombre de tableaux": raw_counts["tables"] == phase1_counts["tables"],
        "OOXML -> Phase1 : nombre d'images du corps": raw_counts["body_images"] == phase1_counts["body_images"],
        "Phase1 -> TLDocument : paragraphes": phase1_counts["paragraphs"] == tl_counts["paragraphs"],
        "Phase1 -> TLDocument : texte exact": phase1_paragraph_texts == tl_paragraph_texts,
        "Phase1 -> TLDocument : tableaux": phase1_counts["tables"] == tl_counts["tables"],
        "Phase1 -> TLDocument : images": phase1_counts["images"] == tl_counts["images"],
        "Phase1 -> TLDocument : sections": phase1_counts["sections"] == tl_counts["sections"],
        "TLDocument : tous les paragraphes ont une position logique": not unplaced_paragraphs,
        "TLDocument : tous les tableaux ont une position logique": not unplaced_tables,
        "TLDocument : aucun conteneur OOXML non normalisé": not raw_probe.unsupported_nodes,
    }

    blockers: list[str] = []
    warnings: list[str] = list(logical.source_warnings)

    failed = [name for name, passed in checks.items() if not passed]
    blockers.extend(failed)

    tracked = auxiliary.get("tracked_changes", {})
    if isinstance(tracked, dict) and any(int(value or 0) for value in tracked.values()):
        blockers.append(
            "Le DOCX contient des modifications suivies : leur état visible doit être décidé avant un jumeau visuel fiable."
        )

    if raw_probe.linked_image_count:
        blockers.append(
            f"{raw_probe.linked_image_count} image(s) liée(s) externe(s) détectée(s) : TL doit localiser la ressource avant reconstruction."
        )

    missing_fonts = source_metadata.get("fonts", {}).get("missing_families", [])
    if missing_fonts:
        blockers.append(
            "Police(s) Source absente(s) : " + ", ".join(str(item) for item in missing_fonts)
        )

    if auxiliary.get("comments"):
        warnings.append(
            "Commentaires Word présents : conservés comme faits Source, non interprétés à cette étape."
        )
    if auxiliary.get("content_controls"):
        warnings.append(
            "Contrôles de contenu Word présents : conservés et à qualifier avant édition avancée."
        )

    report = IntegrityReport(
        source_path=str(source),
        checks=checks,
        raw_counts=raw_counts,
        phase1_counts=phase1_counts,
        tl_counts=tl_counts,
        blockers=tuple(dict.fromkeys(blockers)),
        warnings=tuple(dict.fromkeys(str(item) for item in warnings if str(item).strip())),
        unplaced_paragraphs=unplaced_paragraphs,
        unplaced_tables=unplaced_tables,
        unsupported_nodes=raw_probe.unsupported_nodes,
    )
    return logical, report


__all__ = [
    "TLDOCUMENT_SCHEMA",
    "TLDOCUMENT_VERSION",
    "TLRun",
    "TLParagraph",
    "TLTable",
    "TLImage",
    "TLSection",
    "TLDocument",
    "IntegrityReport",
    "build_tldocument_from_docx",
]
