from __future__ import annotations

"""Prototype TomeLinea — découpage logique du payload Canvas par chapitre.

Ce module ne modifie ni la Source ni le moteur Canvas. Il fabrique des vues de
travail plus petites à partir du payload Canvas Editor déjà validé.
"""

from copy import deepcopy
from dataclasses import dataclass
import re
from typing import Any


_CHAPTER_STYLE_RE = re.compile(
    r"(?:^|[_\-\s])(?:tl[_\-\s]*)?(?:chapitre|chapter|heading\s*1|titre\s*1|titre1)(?:$|[_\-\s])",
    re.IGNORECASE,
)


def _tl(element: dict[str, Any]) -> dict[str, Any]:
    ext = element.get("extension")
    if not isinstance(ext, dict):
        return {}
    tl = ext.get("tomelinea")
    return tl if isinstance(tl, dict) else {}


def _paragraph_info(element: dict[str, Any]) -> tuple[str | None, str | None, int | None]:
    tl = _tl(element)
    trace = tl.get("sourceTrace")
    if not isinstance(trace, dict):
        trace = {}
    # Le traducteur Phase 2 place les métadonnées de paragraphe à côté de
    # sourceTrace dans extension.tomelinea. Garder un fallback imbriqué pour
    # compatibilité avec d'anciens payloads.
    paragraph = tl.get("paragraph")
    if not isinstance(paragraph, dict):
        paragraph = trace.get("paragraph")
    if not isinstance(paragraph, dict):
        paragraph = {}
    fmt = paragraph.get("format")
    if not isinstance(fmt, dict):
        fmt = {}

    para_id = paragraph.get("id")
    style_id = fmt.get("style_id")
    source_para = paragraph.get("sourceParagraph")

    # Les marqueurs de fin de paragraphe n'ont pas toujours sourceTrace.
    if para_id is None and tl.get("paragraphEnd") is not None:
        source_para = tl.get("paragraphEnd")
        para_id = f"p:{source_para}"
        fmt2 = tl.get("format")
        if isinstance(fmt2, dict):
            style_id = fmt2.get("style_id")

    return (
        str(para_id) if para_id is not None else None,
        str(style_id) if style_id is not None else None,
        int(source_para) if isinstance(source_para, int) else None,
    )


def _is_chapter_style(style_id: str | None) -> bool:
    if not style_id:
        return False
    normalized = style_id.replace("_", " ").replace("-", " ").strip()
    low = " ".join(normalized.casefold().split())
    if "chapitre" in low or "chapter" in low:
        return True
    compact = low.replace(" ", "")
    return compact in {"heading1", "titre1"} or low in {"heading 1", "titre 1"}


def _element_text(element: dict[str, Any]) -> str:
    value = element.get("value")
    return value if isinstance(value, str) else ""


@dataclass(frozen=True, slots=True)
class ChapterSlice:
    index: int
    title: str
    start_global: int
    end_global: int
    start_paragraph: int | None
    end_paragraph: int | None
    detected_by: str


@dataclass(frozen=True, slots=True)
class ChapterDetection:
    chapters: tuple[ChapterSlice, ...]
    mode: str


def detect_chapters(payload: dict[str, Any], *, fallback_paragraphs: int = 24) -> ChapterDetection:
    sections = payload.get("sections") or []
    flat: list[tuple[int, int, dict[str, Any]]] = []
    for section_index, section in enumerate(sections):
        main = section.get("data", {}).get("main", [])
        for element_index, element in enumerate(main):
            if isinstance(element, dict):
                flat.append((section_index, element_index, element))

    if not flat:
        return ChapterDetection(chapters=(), mode="empty")

    # Première position de chaque paragraphe et titre complet du paragraphe.
    para_first: dict[str, int] = {}
    para_style: dict[str, str | None] = {}
    para_source: dict[str, int | None] = {}
    para_text: dict[str, list[str]] = {}
    para_order: list[str] = []

    for global_index, (_, _, element) in enumerate(flat):
        para_id, style_id, source_para = _paragraph_info(element)
        if not para_id:
            continue
        if para_id not in para_first:
            para_first[para_id] = global_index
            para_style[para_id] = style_id
            para_source[para_id] = source_para
            para_text[para_id] = []
            para_order.append(para_id)
        text = _element_text(element)
        if text and text != "\n":
            para_text[para_id].append(text)

    chapter_para_ids = [pid for pid in para_order if _is_chapter_style(para_style.get(pid))]
    starts: list[tuple[int, str, int | None, str]] = []

    # Conserver la matière liminaire comme bloc autonome si elle existe.
    if chapter_para_ids:
        first_chapter_global = para_first[chapter_para_ids[0]]
        if first_chapter_global > 0:
            starts.append((0, "Début du livre", None, "prelude"))
        for pid in chapter_para_ids:
            title = "".join(para_text.get(pid, [])).strip() or "Chapitre"
            starts.append((para_first[pid], title, para_source.get(pid), "style"))
        mode = "chapter_styles"
    else:
        # Fallback de diagnostic uniquement : blocs de N paragraphes.
        # Il permet de tester l'hypothèse performance même si le DOCX ne porte
        # pas de style de chapitre identifiable.
        mode = "paragraph_blocks"
        for offset in range(0, len(para_order), max(1, fallback_paragraphs)):
            pid = para_order[offset]
            starts.append((
                para_first[pid],
                f"Bloc test {offset // max(1, fallback_paragraphs) + 1}",
                para_source.get(pid),
                "fallback",
            ))

    starts = sorted({start: (start, title, para, by) for start, title, para, by in starts}.values())
    chapters: list[ChapterSlice] = []
    for i, (start, title, start_para, detected_by) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(flat)
        # Dernier numéro de paragraphe présent dans la tranche.
        end_para = None
        for _, _, element in reversed(flat[start:end]):
            _, _, source_para = _paragraph_info(element)
            if source_para is not None:
                end_para = source_para
                break
        chapters.append(ChapterSlice(
            index=i + 1,
            title=title,
            start_global=start,
            end_global=end,
            start_paragraph=start_para,
            end_paragraph=end_para,
            detected_by=detected_by,
        ))

    return ChapterDetection(chapters=tuple(chapters), mode=mode)


def slice_payload(payload: dict[str, Any], chapter: ChapterSlice) -> dict[str, Any]:
    """Retourne un payload Canvas autonome limité à une tranche contiguë."""
    result = deepcopy(payload)
    sections = payload.get("sections") or []

    cursor = 0
    selected_sections: list[dict[str, Any]] = []
    for section in sections:
        main = section.get("data", {}).get("main", [])
        section_start = cursor
        section_end = cursor + len(main)
        cursor = section_end

        local_start = max(0, chapter.start_global - section_start)
        local_end = min(len(main), chapter.end_global - section_start)
        if local_start >= local_end:
            continue

        copied = deepcopy(section)
        copied.setdefault("data", {})["main"] = deepcopy(main[local_start:local_end])
        selected_sections.append(copied)

    result["sections"] = selected_sections
    result.setdefault("source", {})["tomelinea_chapter_slice"] = {
        "index": chapter.index,
        "title": chapter.title,
        "start_paragraph": chapter.start_paragraph,
        "end_paragraph": chapter.end_paragraph,
        "detected_by": chapter.detected_by,
    }
    return result
