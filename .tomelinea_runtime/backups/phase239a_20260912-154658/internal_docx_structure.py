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
            return part

    # Réutilise les anciens Début / Fin lorsqu'ils existent déjà.
    for part in getattr(book, "parts", {}).values():
        if str(getattr(part, "part_type", "") or "").strip().lower() == part_type:
            metadata = getattr(part, "metadata", None)
            if isinstance(metadata, dict):
                metadata[_STRUCTURE_ROLE_KEY] = role
            return part

    part = PartV4(title=title, part_type=part_type)
    part.metadata[_STRUCTURE_ROLE_KEY] = role
    book.parts[part.id] = part
    if part.id not in book.part_order:
        book.part_order.append(part.id)
    return part


def ensure_physical_cover_frame(book: Any) -> bool:
    """Garantit les quatre faces physiques autour d'un Livre DOCX interne.

    2e et 3e sont de vraies pages automatiques TomeLinea si la Source ne les
    fournit pas. 1re et 4e sont des emplacements physiques obligatoires mais
    restent marquées comme contenu extérieur à fournir lorsque la Source DOCX
    n'en possède pas.
    """

    changed = False
    debut = _ensure_role_part(book, "debut", "Début", "debut")
    fin = _ensure_role_part(book, "fin", "Fin", "fin")

    # Le moteur physique commun garantit les quatre faces. Il crée 1re/4e
    # comme emplacements obligatoires si elles sont absentes, et 2e/3e comme
    # vraies pages automatiques TomeLinea.
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

        wanted_part = debut.id if face in {FRONT_COVER, INSIDE_FRONT_COVER} else fin.id
        if page.part_id != wanted_part:
            page.part_id = wanted_part
            changed = True

        if face in {INSIDE_FRONT_COVER, INSIDE_BACK_COVER} and is_generated_cover_placeholder(page):
            # Ces deux faces existent physiquement même sans contenu auteur :
            # elles appartiennent explicitement à la famille des pages auto.
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

    # Les racines Début / Fin restent aux extrémités de l'ordre des parties.
    middle = [
        part_id
        for part_id in book.part_order
        if part_id not in {debut.id, fin.id}
    ]
    wanted_order = [debut.id, *middle, fin.id]
    if wanted_order != list(book.part_order):
        book.part_order = wanted_order
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
) -> InternalStructureSyncResult:
    """Synchronise pages Canvas, chapitres et couvertures avec le Livre V4."""

    changed = ensure_physical_cover_frame(book)
    created_pages = 0
    removed_pages = 0

    chapters = list(getattr(detection, "chapters", ()) or ())
    counts = [max(1, int(value)) for value in page_counts]
    if not chapters or len(chapters) != len(counts):
        raise ValueError("Découpage Canvas incomplet pour synchroniser Structure.")

    debut = _ensure_role_part(book, "debut", "Début", "debut")
    fin = _ensure_role_part(book, "fin", "Fin", "fin")
    existing = _existing_generated_parts(book)
    desired_generated_ids: list[str] = []
    chapter_part_ids: list[str] = []

    mode = str(getattr(detection, "mode", "") or "")
    current_parent_id: str | None = None

    if mode != "chapter_styles":
        key = "canvas:corps"
        body = _ensure_generated_part(
            book,
            existing,
            key=key,
            title="Corps",
            part_type="corps",
            parent_id=None,
            chapter_index=None,
        )
        desired_generated_ids.append(body.id)
        chapter_part_ids = [body.id for _ in chapters]
    else:
        for index, chapter in enumerate(chapters):
            detected_by = str(getattr(chapter, "detected_by", "") or "")
            if detected_by == "prelude":
                chapter_part_ids.append(debut.id)
                continue

            title = str(getattr(chapter, "title", "") or "").strip() or f"Chapitre {index + 1}"
            key = _chapter_key(chapter, index)

            if _looks_like_real_part(title):
                part = _ensure_generated_part(
                    book,
                    existing,
                    key=key,
                    title=title,
                    part_type="partie",
                    parent_id=None,
                    chapter_index=index,
                )
                current_parent_id = part.id
            else:
                part = _ensure_generated_part(
                    book,
                    existing,
                    key=key,
                    title=title,
                    part_type="chapitre",
                    parent_id=current_parent_id,
                    chapter_index=index,
                )

            desired_generated_ids.append(part.id)
            chapter_part_ids.append(part.id)

    # Chapitre prelude absent : la liste doit toujours correspondre 1:1.
    if len(chapter_part_ids) != len(chapters):
        raise RuntimeError("Correspondance chapitre/partie invalide.")

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

    # Réutiliser d'abord toute page non attribuée avant d'en créer une.
    for chapter_index, wanted in enumerate(counts):
        while len(groups[chapter_index]) < wanted and unassigned:
            page_id = unassigned.pop(0)
            groups[chapter_index].append(page_id)
            book.pages[page_id].metadata["canvas_chapter_index"] = chapter_index
            changed = True

    # Supprimer les pages en trop à la fin de chaque chapitre.
    for chapter_index, wanted in enumerate(counts):
        while len(groups[chapter_index]) > wanted:
            page_id = groups[chapter_index].pop()
            if page_id in book.page_order:
                book.page_order.remove(page_id)
            book.pages.pop(page_id, None)
            removed_pages += 1
            changed = True

    # Une ancienne page non attribuée restante n'appartient plus à la pagination.
    for page_id in list(unassigned):
        if page_id in book.page_order:
            book.page_order.remove(page_id)
        book.pages.pop(page_id, None)
        removed_pages += 1
        changed = True

    # Créer les nouvelles pages exactement à la fin du chapitre concerné.
    for chapter_index, wanted in enumerate(counts):
        while len(groups[chapter_index]) < wanted:
            _insert_rich_page_at_chapter_end(book, groups, chapter_index)
            created_pages += 1
            changed = True

    # Numérotation interne continue + rattachement au chapitre réel.
    global_index = 0
    for chapter_index, group in enumerate(groups):
        part_id = chapter_part_ids[chapter_index]
        for local_index, page_id in enumerate(group):
            page = book.pages[page_id]
            metadata = page.metadata
            before = (
                page.part_id,
                metadata.get("internal_rich_page_index"),
                metadata.get("canvas_chapter_index"),
                metadata.get("canvas_chapter_local_page_index"),
            )
            page.part_id = part_id
            page.page_type = "Page texte"
            page.title = f"Page {global_index + 1}"
            metadata["internal_rich_page"] = True
            metadata["internal_rich_page_index"] = global_index
            metadata["internal_rich_page_start"] = global_index
            metadata["canvas_chapter_index"] = chapter_index
            metadata["canvas_chapter_local_page_index"] = local_index
            after = (
                page.part_id,
                metadata.get("internal_rich_page_index"),
                metadata.get("canvas_chapter_index"),
                metadata.get("canvas_chapter_local_page_index"),
            )
            if before != after:
                changed = True
            global_index += 1

    # Les parties Canvas devenues inutiles ne sont supprimées que si aucune
    # page (par exemple une page auto éditoriale) ne les référence encore.
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

    # Ordre logique : Début -> vraies parties/chapitres -> Fin.
    retained = [
        part_id
        for part_id in book.part_order
        if part_id in book.parts
        and part_id not in {debut.id, fin.id}
        and part_id not in desired_generated_ids
        and not bool(getattr(book.parts[part_id], "metadata", {}).get(_GENERATED_PART_KEY))
    ]
    wanted_part_order = [debut.id, *retained, *desired_generated_ids, fin.id]
    if wanted_part_order != list(book.part_order):
        book.part_order = wanted_part_order
        changed = True

    book.metadata["canvas_structure_mode"] = mode
    book.metadata["canvas_chapter_count"] = len(chapters)
    book.metadata["canvas_chapter_page_counts"] = list(counts)
    book.metadata["canvas_structure_version"] = "2.38A"

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
