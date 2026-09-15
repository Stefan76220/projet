from __future__ import annotations

"""TomeLinea V4 — unités Canvas limitées au chapitre actif.

Ce module ne modifie ni la Source ni Canvas Editor. Il découpe le payload déjà
validé en unités de composition cohérentes et maintient la correspondance entre
les pages locales d'un chapitre et les pages globales du Livre TomeLinea.
"""

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Any


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

    # Le marqueur de fin de paragraphe porte parfois seulement paragraphEnd.
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


@dataclass(slots=True)
class ChapterBookLayout:
    """Pagination globale construite à partir des paginations Canvas locales."""

    chapters: tuple[ChapterSlice, ...]
    page_counts: list[int] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.page_counts:
            self.page_counts = [1 for _ in self.chapters]
        if len(self.page_counts) != len(self.chapters):
            raise ValueError("page_counts doit avoir exactement une valeur par chapitre")
        self.page_counts = [max(1, int(value)) for value in self.page_counts]

    @property
    def total_pages(self) -> int:
        return max(1, sum(self.page_counts))

    def set_page_count(self, chapter_index: int, count: int) -> None:
        if not (0 <= int(chapter_index) < len(self.page_counts)):
            raise IndexError(chapter_index)
        self.page_counts[int(chapter_index)] = max(1, int(count))

    def chapter_start_page(self, chapter_index: int) -> int:
        """Numéro global 1-based de la première page d'un chapitre."""
        index = max(0, min(int(chapter_index), len(self.page_counts) - 1))
        return 1 + sum(self.page_counts[:index])

    def locate_global_index(self, global_index: int) -> tuple[int, int]:
        """Retourne (chapitre 0-based, page locale 0-based)."""
        if not self.page_counts:
            return 0, 0
        target = max(0, min(int(global_index), self.total_pages - 1))
        cursor = 0
        for chapter_index, count in enumerate(self.page_counts):
            if target < cursor + count:
                return chapter_index, target - cursor
            cursor += count
        last = len(self.page_counts) - 1
        return last, self.page_counts[last] - 1

    def global_index(self, chapter_index: int, local_index: int) -> int:
        chapter_index = max(0, min(int(chapter_index), len(self.page_counts) - 1))
        local_index = max(0, min(int(local_index), self.page_counts[chapter_index] - 1))
        return sum(self.page_counts[:chapter_index]) + local_index


def detect_chapters(payload: dict[str, Any], *, fallback_paragraphs: int = 24) -> ChapterDetection:
    """Détecte les chapitres dans le payload traduit.

    Les styles Chapitre/Heading 1/Titre 1 sont prioritaires. Si la Source ne
    fournit aucun repère exploitable, TomeLinea crée des unités techniques de
    composition de taille bornée. Elles ne changent pas la Structure éditoriale :
    elles servent uniquement à éviter un Canvas géant pendant la frappe.
    """
    sections = payload.get("sections") or []
    flat: list[tuple[int, int, dict[str, Any]]] = []
    for section_index, section in enumerate(sections):
        main = section.get("data", {}).get("main", [])
        for element_index, element in enumerate(main):
            if isinstance(element, dict):
                flat.append((section_index, element_index, element))

    if not flat:
        return ChapterDetection(chapters=(), mode="empty")

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

    if not para_order:
        # Le payload peut contenir des objets sans métadonnées de paragraphe.
        return ChapterDetection(
            chapters=(
                ChapterSlice(
                    index=1,
                    title="Livre",
                    start_global=0,
                    end_global=len(flat),
                    start_paragraph=None,
                    end_paragraph=None,
                    detected_by="whole_document",
                ),
            ),
            mode="whole_document",
        )

    chapter_para_ids = [pid for pid in para_order if _is_chapter_style(para_style.get(pid))]
    starts: list[tuple[int, str, int | None, str]] = []

    if chapter_para_ids:
        first_chapter_global = para_first[chapter_para_ids[0]]
        if first_chapter_global > 0:
            starts.append((0, "Début du livre", None, "prelude"))
        for pid in chapter_para_ids:
            title = "".join(para_text.get(pid, [])).strip() or "Chapitre"
            starts.append((para_first[pid], title, para_source.get(pid), "style"))
        mode = "chapter_styles"
    else:
        # Unité technique de repli : limitée, déterministe et invisible pour la
        # logique éditoriale. Ce n'est PAS un faux chapitre ajouté au Livre.
        size = max(8, int(fallback_paragraphs))
        mode = "technical_units"
        for offset in range(0, len(para_order), size):
            pid = para_order[offset]
            starts.append((
                para_first[pid],
                f"Unité de composition {offset // size + 1}",
                para_source.get(pid),
                "technical_fallback",
            ))

    starts = sorted({start: (start, title, para, by) for start, title, para, by in starts}.values())
    chapters: list[ChapterSlice] = []
    for i, (start, title, start_para, detected_by) in enumerate(starts):
        end = starts[i + 1][0] if i + 1 < len(starts) else len(flat)
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
    """Construit un payload autonome limité à l'unité de composition donnée."""
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


def apply_exported_state(plan: dict[str, Any], exported: dict[str, Any]) -> bool:
    """Réinjecte l'état édité d'un Canvas local dans son plan en mémoire."""
    if not isinstance(plan, dict) or not isinstance(exported, dict):
        return False
    segments = exported.get("segments")
    if not isinstance(segments, list):
        return False
    by_number: dict[int, dict[str, Any]] = {}
    for item in segments:
        if not isinstance(item, dict) or not isinstance(item.get("data"), dict):
            continue
        try:
            number = int(item.get("segment"))
        except (TypeError, ValueError):
            continue
        by_number[number] = deepcopy(item["data"])

    changed = False
    for segment in plan.get("render_segments", []):
        try:
            number = int(segment.get("segment"))
        except (TypeError, ValueError):
            continue
        if number in by_number:
            segment["data"] = deepcopy(by_number[number])
            changed = True
    return changed
