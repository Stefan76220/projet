from __future__ import annotations

"""Structure physique du Livre pour le moteur DOCX interne TomeLinea.

Cette couche relie trois autorités qui existaient déjà séparément :
- le Livre V4 possède les vraies pages physiques et les couvertures ;
- Canvas Editor possède la pagination du texte, chapitre par chapitre ;
- Structure expose la hiérarchie éditoriale réelle sans créer de faux niveaux.

Aucune donnée de la Source DOCX n'est réécrite ici.
"""

from dataclasses import dataclass
import re
import unicodedata
from typing import Any

from src.v4.domain import PageOrigin, PageV4, PartV4
from src.v4.structure_covers import (
    BACK_COVER,
    FRONT_COVER,
    INSIDE_BACK_COVER,
    INSIDE_FRONT_COVER,
    cover_ids,
    ensure_physical_cover_faces,
    is_generated_cover_placeholder,
    normalize_cover_structure,
)


_GENERATED_PART_KEY = "canvas_structure_generated"
_STRUCTURE_ROLE_KEY = "tomelinea_structure_role"
_CHAPTER_KEY = "canvas_chapter_key"


@dataclass(frozen=True, slots=True)
class InternalStructureSyncResult:
    changed: bool
    body_page_count: int
    physical_page_count: int
    chapter_count: int
    created_pages: int = 0
    removed_pages: int = 0


def _norm(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = "".join(
        ch
        for ch in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(ch)
    )
    return " ".join(text.split())


def _looks_like_real_part(title: str) -> bool:
    """Vrai uniquement pour un intitulé qui annonce réellement une Partie."""

    value = _norm(title)
    if not value or value in {"sans partie", "corps", "ouverture"}:
        return False

    if re.match(r"^(partie|part)\b", value):
        return True

    return bool(
        re.match(
            r"^(premi(?:e|è)re|deuxi(?:e|è)me|troisi(?:e|è)me|"
            r"quatri(?:e|è)me|cinqui(?:e|è)me|sixi(?:e|è)me|"
            r"septi(?:e|è)me|huiti(?:e|è)me|neuvi(?:e|è)me|"
            r"dixi(?:e|è)me)\s+(partie|part)\b",
            value,
            flags=re.IGNORECASE,
        )
    )


def _ensure_role_part(book: Any, role: str, title: str, part_type: str) -> PartV4:
    for part in getattr(book, "parts", {}).values():
        metadata = getattr(part, "metadata", None)
        if isinstance(metadata, dict) and metadata.get(_STRUCTURE_ROLE_KEY) == role:
            part.title = title
            part.part_type = part_type
            part.parent_id = None
            return part

    part = PartV4(title=title, part_type=part_type)
    part.metadata[_STRUCTURE_ROLE_KEY] = role
    book.parts[part.id] = part
    if part.id not in book.part_order:
        book.part_order.append(part.id)
    return part


def _fixed_structure_parts(book: Any) -> dict[str, PartV4]:
    """Cinq zones stables : couvertures séparées de l'intérieur du livre."""
    return {
        "cover_front": _ensure_role_part(
            book, "couverture_avant", "Couverture avant", "couverture_avant"
        ),
        "frontmatter": _ensure_role_part(
            book, "preliminaires", "Pages liminaires", "preliminaires"
        ),
        "body": _ensure_role_part(
            book, "corps", "Corps", "corps"
        ),
        "backmatter": _ensure_role_part(
            book, "fin_ouvrage", "Fin d’ouvrage", "fin_ouvrage"
        ),
        "cover_back": _ensure_role_part(
            book, "couverture_arriere", "Couverture arrière", "couverture_arriere"
        ),
    }


def ensure_physical_cover_frame(book: Any) -> bool:
    """Garantit les quatre faces physiques sans les mélanger à l'intérieur."""

    changed = False
    fixed = _fixed_structure_parts(book)

    if ensure_physical_cover_faces(book):
        changed = True

    ids = cover_ids(book)
    for face in (FRONT_COVER, INSIDE_FRONT_COVER, INSIDE_BACK_COVER, BACK_COVER):
        page_id = ids.get(face)
        if page_id is None:
            continue
        page = book.pages.get(page_id)
        if page is None:
            continue

        wanted_part = (
            fixed["cover_front"].id
            if face in {FRONT_COVER, INSIDE_FRONT_COVER}
            else fixed["cover_back"].id
        )
        if page.part_id != wanted_part:
            page.part_id = wanted_part
            changed = True

        if face in {INSIDE_FRONT_COVER, INSIDE_BACK_COVER} and is_generated_cover_placeholder(page):
            metadata = page.metadata
            before = (
                metadata.get("automatic_origin"),
                metadata.get("automatic_kind"),
                metadata.get("creation_kind"),
            )
            metadata["automatic_origin"] = True
            metadata["automatic_kind"] = "physical_cover"
            metadata["creation_kind"] = "automatic_physical_cover"
            metadata["automatic_page"] = True
            after = (
                metadata.get("automatic_origin"),
                metadata.get("automatic_kind"),
                metadata.get("creation_kind"),
            )
            if before != after:
                changed = True

    if normalize_cover_structure(book):
        changed = True

    # Migration 2.38A -> 2.39A : les anciennes zones Début / Fin peuvent
    # contenir des pages intérieures. Les couvertures viennent d'être retirées ;
    # le reste va respectivement dans Pages liminaires / Fin d'ouvrage.
    for page in getattr(book, "pages", {}).values():
        if page.part_id is None:
            continue
        part = book.parts.get(page.part_id)
        if part is None:
            continue
        ptype = _norm(getattr(part, "part_type", ""))
        if ptype == "debut" and page.part_id != fixed["cover_front"].id:
            page.part_id = fixed["frontmatter"].id
            changed = True
        elif ptype == "fin" and page.part_id != fixed["cover_back"].id:
            page.part_id = fixed["backmatter"].id
            changed = True

    return changed


def _chapter_key(chapter: Any, index: int) -> str:
    start_para = getattr(chapter, "start_paragraph", None)
    detected_by = str(getattr(chapter, "detected_by", "") or "")
    title = _norm(getattr(chapter, "title", ""))
    return f"{index}:{start_para}:{detected_by}:{title}"


def _existing_generated_parts(book: Any) -> dict[str, PartV4]:
    result: dict[str, PartV4] = {}
    for part in getattr(book, "parts", {}).values():
        metadata = getattr(part, "metadata", None)
        if not isinstance(metadata, dict) or not metadata.get(_GENERATED_PART_KEY):
            continue
        key = str(metadata.get(_CHAPTER_KEY) or "")
        if key:
            result[key] = part
    return result


def _ensure_generated_part(
    book: Any,
    existing: dict[str, PartV4],
    *,
    key: str,
    title: str,
    part_type: str,
    parent_id: str | None,
    chapter_index: int | None,
) -> PartV4:
    part = existing.get(key)
    if part is None:
        part = PartV4(title=title, part_type=part_type, parent_id=parent_id)
        book.parts[part.id] = part
    part.title = title
    part.part_type = part_type
    part.parent_id = parent_id
    part.metadata[_GENERATED_PART_KEY] = True
    part.metadata[_CHAPTER_KEY] = key
    if chapter_index is not None:
        part.metadata["canvas_chapter_index"] = int(chapter_index)
    return part


def _ordered_rich_ids(book: Any) -> list[str]:
    result: list[str] = []
    for page_id in list(getattr(book, "page_order", ())):
        page = book.pages.get(page_id)
        metadata = getattr(page, "metadata", None) if page is not None else None
        if isinstance(metadata, dict) and metadata.get("internal_rich_page"):
            result.append(str(page_id))
    return result


def _insert_rich_page_at_chapter_end(
    book: Any,
    groups: list[list[str]],
    chapter_index: int,
) -> str:
    page = PageV4(
        page_type="Page texte",
        title="Page",
        origin=PageOrigin.AUTHOR,
        source=None,
    )
    page.metadata["internal_rich_page"] = True
    page.metadata["canvas_chapter_index"] = int(chapter_index)
    book.pages[page.id] = page

    group = groups[chapter_index]
    if group:
        insert_at = book.page_order.index(group[-1]) + 1
    else:
        insert_at = None
        for next_index in range(chapter_index + 1, len(groups)):
            if groups[next_index]:
                insert_at = book.page_order.index(groups[next_index][0])
                break
        if insert_at is None:
            ids = cover_ids(book)
            inside_back = ids.get(INSIDE_BACK_COVER)
            back = ids.get(BACK_COVER)
            anchor = inside_back or back
            insert_at = (
                book.page_order.index(anchor)
                if anchor in book.page_order
                else len(book.page_order)
            )

    book.page_order.insert(int(insert_at), page.id)
    group.append(page.id)
    return page.id


def synchronize_internal_docx_structure(
    book: Any,
    detection: Any,
    page_counts: list[int] | tuple[int, ...],
    editorial_analysis: dict[str, Any] | None = None,
) -> InternalStructureSyncResult:
    """Synchronise pagination Canvas et structure éditoriale typée du Livre."""

    changed = ensure_physical_cover_frame(book)
    created_pages = 0
    removed_pages = 0

    chapters = list(getattr(detection, "chapters", ()) or ())
    counts = [max(1, int(value)) for value in page_counts]
    if not chapters or len(chapters) != len(counts):
        raise ValueError("Découpage Canvas incomplet pour synchroniser Structure.")

    fixed = _fixed_structure_parts(book)
    existing = _existing_generated_parts(book)
    desired_generated_ids: list[str] = []
    chapter_part_ids: list[str] = []
    unit_descriptors: list[dict[str, Any]] = []

    analysis_units = []
    if isinstance(editorial_analysis, dict):
        analysis_units = list(editorial_analysis.get("units") or [])
    analysis_by_index = {
        int(item.get("canvas_index")): item
        for item in analysis_units
        if isinstance(item, dict) and isinstance(item.get("canvas_index"), int)
    }

    mode = str(getattr(detection, "mode", "") or "")
    current_parent_id: str | None = None
    last_body_part_id: str | None = fixed["body"].id

    for index, chapter in enumerate(chapters):
        title = str(getattr(chapter, "title", "") or "").strip() or f"Unité {index + 1}"
        unit = analysis_by_index.get(index, {})
        zone = str(unit.get("zone") or "")
        editorial_type = str(unit.get("editorial_type") or "")
        editorial_label = str(unit.get("editorial_label") or title).strip() or title

        # Repli compatible avec l'ancien moteur si l'analyse éditoriale n'est
        # pas disponible : le découpage technique ne doit jamais inventer des
        # pages liminaires ni de fin d'ouvrage.
        if not unit:
            detected_by = str(getattr(chapter, "detected_by", "") or "")
            if detected_by == "prelude":
                zone = "frontmatter"
                editorial_type = "frontmatter_bundle"
            elif mode == "chapter_styles" and _looks_like_real_part(title):
                zone = "bodymatter"
                editorial_type = "part"
            elif mode == "chapter_styles":
                zone = "bodymatter"
                editorial_type = "chapter"
            else:
                zone = "bodymatter"
                editorial_type = "technical_unit"

        part: PartV4
        if zone == "frontmatter":
            part = fixed["frontmatter"]
        elif zone == "backmatter":
            part = fixed["backmatter"]
        elif editorial_type == "part":
            key = _chapter_key(chapter, index)
            part = _ensure_generated_part(
                book,
                existing,
                key=key,
                title=title,
                part_type="partie",
                parent_id=None,
                chapter_index=index,
            )
            part.metadata["editorial_type"] = editorial_type
            part.metadata["editorial_zone"] = "bodymatter"
            desired_generated_ids.append(part.id)
            current_parent_id = part.id
            last_body_part_id = part.id
        elif editorial_type == "chapter":
            key = _chapter_key(chapter, index)
            part = _ensure_generated_part(
                book,
                existing,
                key=key,
                title=title,
                part_type="chapitre",
                parent_id=current_parent_id,
                chapter_index=index,
            )
            part.metadata["editorial_type"] = editorial_type
            part.metadata["editorial_zone"] = "bodymatter"
            desired_generated_ids.append(part.id)
            last_body_part_id = part.id
        elif editorial_type in {"custom_section", "interlude", "introduction", "prologue"}:
            key = _chapter_key(chapter, index)
            part = _ensure_generated_part(
                book,
                existing,
                key=key,
                title=editorial_label,
                part_type="section",
                parent_id=current_parent_id,
                chapter_index=index,
            )
            part.metadata["editorial_type"] = editorial_type
            part.metadata["editorial_zone"] = "bodymatter"
            desired_generated_ids.append(part.id)
            last_body_part_id = part.id
        elif editorial_type == "merge_previous":
            part = book.parts.get(last_body_part_id) or fixed["body"]
        else:
            part = fixed["body"]
            last_body_part_id = part.id

        chapter_part_ids.append(part.id)
        unit_descriptors.append({
            "title": title,
            "label": editorial_label,
            "zone": zone or "bodymatter",
            "editorial_type": editorial_type or "unknown",
            "confidence": int(unit.get("confidence", 0) or 0) if unit else 0,
        })

    rich_ids = _ordered_rich_ids(book)
    tagged = any(
        isinstance(book.pages[page_id].metadata.get("canvas_chapter_index"), int)
        for page_id in rich_ids
    )

    groups: list[list[str]] = [[] for _ in chapters]
    unassigned: list[str] = []

    if tagged:
        for page_id in rich_ids:
            raw = book.pages[page_id].metadata.get("canvas_chapter_index")
            try:
                chapter_index = int(raw)
            except (TypeError, ValueError):
                unassigned.append(page_id)
                continue
            if 0 <= chapter_index < len(groups):
                groups[chapter_index].append(page_id)
            else:
                unassigned.append(page_id)
    else:
        cursor = 0
        for chapter_index, wanted in enumerate(counts):
            take = min(wanted, max(0, len(rich_ids) - cursor))
            groups[chapter_index].extend(rich_ids[cursor:cursor + take])
            cursor += take
        unassigned.extend(rich_ids[cursor:])

    for chapter_index, wanted in enumerate(counts):
        while len(groups[chapter_index]) < wanted and unassigned:
            page_id = unassigned.pop(0)
            groups[chapter_index].append(page_id)
            book.pages[page_id].metadata["canvas_chapter_index"] = chapter_index
            changed = True

    for chapter_index, wanted in enumerate(counts):
        while len(groups[chapter_index]) > wanted:
            page_id = groups[chapter_index].pop()
            if page_id in book.page_order:
                book.page_order.remove(page_id)
            book.pages.pop(page_id, None)
            removed_pages += 1
            changed = True

    for page_id in list(unassigned):
        if page_id in book.page_order:
            book.page_order.remove(page_id)
        book.pages.pop(page_id, None)
        removed_pages += 1
        changed = True

    for chapter_index, wanted in enumerate(counts):
        while len(groups[chapter_index]) < wanted:
            _insert_rich_page_at_chapter_end(book, groups, chapter_index)
            created_pages += 1
            changed = True

    global_index = 0
    for chapter_index, group in enumerate(groups):
        part_id = chapter_part_ids[chapter_index]
        descriptor = unit_descriptors[chapter_index]
        zone = descriptor["zone"]
        unit_title = descriptor["label"] or descriptor["title"]
        for local_index, page_id in enumerate(group):
            page = book.pages[page_id]
            metadata = page.metadata
            before = (
                page.part_id,
                page.title,
                page.page_type,
                metadata.get("internal_rich_page_index"),
                metadata.get("canvas_chapter_index"),
                metadata.get("canvas_chapter_local_page_index"),
                metadata.get("editorial_zone"),
                metadata.get("editorial_type"),
            )
            page.part_id = part_id
            if zone == "frontmatter":
                page.page_type = "Page liminaire"
                page.title = unit_title if local_index == 0 else f"{unit_title} — suite"
            elif zone == "backmatter":
                page.page_type = "Page de fin"
                page.title = unit_title if local_index == 0 else f"{unit_title} — suite"
            else:
                page.page_type = "Page texte"
                page.title = f"Page {global_index + 1}"
            metadata["internal_rich_page"] = True
            metadata["internal_rich_page_index"] = global_index
            metadata["internal_rich_page_start"] = global_index
            metadata["canvas_chapter_index"] = chapter_index
            metadata["canvas_chapter_local_page_index"] = local_index
            metadata["editorial_zone"] = zone
            metadata["editorial_type"] = descriptor["editorial_type"]
            metadata["editorial_unit_title"] = unit_title
            metadata["editorial_confidence"] = descriptor["confidence"]
            after = (
                page.part_id,
                page.title,
                page.page_type,
                metadata.get("internal_rich_page_index"),
                metadata.get("canvas_chapter_index"),
                metadata.get("canvas_chapter_local_page_index"),
                metadata.get("editorial_zone"),
                metadata.get("editorial_type"),
            )
            if before != after:
                changed = True
            global_index += 1

    fixed_ids = {part.id for part in fixed.values()}
    for part in list(book.parts.values()):
        metadata = getattr(part, "metadata", None)
        if not isinstance(metadata, dict) or not metadata.get(_GENERATED_PART_KEY):
            continue
        if part.id in desired_generated_ids:
            continue
        if any(page.part_id == part.id for page in book.pages.values()):
            continue
        book.parts.pop(part.id, None)
        if part.id in book.part_order:
            book.part_order.remove(part.id)
        changed = True

    # Supprime les anciens conteneurs 2.38A Début/Fin une fois qu'ils ne sont
    # plus utilisés. Les autres parties utilisateur restent intactes.
    for part in list(book.parts.values()):
        if part.id in fixed_ids or part.id in desired_generated_ids:
            continue
        ptype = _norm(getattr(part, "part_type", ""))
        if ptype not in {"debut", "fin"}:
            continue
        if any(page.part_id == part.id for page in book.pages.values()):
            continue
        book.parts.pop(part.id, None)
        if part.id in book.part_order:
            book.part_order.remove(part.id)
        changed = True

    retained = [
        part_id
        for part_id in book.part_order
        if part_id in book.parts
        and part_id not in fixed_ids
        and part_id not in desired_generated_ids
        and not bool(getattr(book.parts[part_id], "metadata", {}).get(_GENERATED_PART_KEY))
    ]
    wanted_part_order = [
        fixed["cover_front"].id,
        fixed["frontmatter"].id,
        fixed["body"].id,
        *retained,
        *desired_generated_ids,
        fixed["backmatter"].id,
        fixed["cover_back"].id,
    ]
    # dédoublonnage stable
    unique_order: list[str] = []
    for part_id in wanted_part_order:
        if part_id in book.parts and part_id not in unique_order:
            unique_order.append(part_id)
    if unique_order != list(book.part_order):
        book.part_order = unique_order
        changed = True

    book.metadata["canvas_structure_mode"] = mode
    book.metadata["canvas_chapter_count"] = len(chapters)
    book.metadata["canvas_chapter_page_counts"] = list(counts)
    book.metadata["canvas_structure_version"] = "2.39A"
    if isinstance(editorial_analysis, dict):
        book.metadata["editorial_structure_summary"] = dict(editorial_analysis.get("summary") or {})
        book.metadata["editorial_structure_schema"] = str(editorial_analysis.get("schema") or "")

    normalize_cover_structure(book)
    book.validate()

    return InternalStructureSyncResult(
        changed=changed,
        body_page_count=sum(counts),
        physical_page_count=len(book.page_order),
        chapter_count=len(chapters),
        created_pages=created_pages,
        removed_pages=removed_pages,
    )
