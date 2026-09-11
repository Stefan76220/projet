from __future__ import annotations

"""Adaptation du contenu des pages non repaginées lors d'un changement de format.

Le changement de format n'est pas un simple redimensionnement du canevas :
- le texte est recomposé à sa nouvelle largeur ;
- les images changent de taille avec un facteur uniforme, sans déformation ;
- les images ancrées suivent le texte auquel l’analyse les a rattachées ;
- le texte courant qui ne tient plus crée des pages de continuation ;
- les pages à mise en page intrinsèquement fixe (couvertures, tableaux,
  fac-similés) restent en mode « contenir la Source » plutôt que d'être
  tronquées ou artificiellement désassemblées.
"""

from copy import deepcopy
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from src.v4.composition import IMAGE, PAGE, TEXT, new_element
from src.v4.domain import BookFormat, BookV4, PageOrigin, PageV4
from src.v4.format_text_layout import measure_text_layout, remember_source_metrics
from src.v4.content_anchors import (
    ANCHOR_ELEMENT_ID,
    ANCHOR_GAP_MM,
    ANCHOR_OFFSET_RATIO,
    ANCHOR_RELATION,
    infer_page_content_anchors,
)
from src.v4.page_element_roles import ROLE_BODY, page_element_roles
from src.v4.structure_covers import is_cover_face
from src.v4.structure_parity import physical_side


_CONTINUATION = "format_content_continuation"
_ORIGIN_ELEMENT = "format_content_origin_element_id"
_SEGMENT_INDEX = "format_content_segment_index"
_ADAPTED = "format_content_adapted"
_KEEP_SOURCE = "format_keep_source_visual"


@dataclass(frozen=True, slots=True)
class FormatContentAdaptationResult:
    adapted_pages: int
    adapted_texts: int
    adapted_images: int
    continuation_pages: int
    overflow_blocks: int
    fixed_layout_pages: int


def _kind(element: Any) -> str:
    if not isinstance(element, dict):
        return ""
    return str(element.get("kind", "") or "").strip().lower()


def _geometry(element: dict[str, Any]) -> dict[str, Any] | None:
    value = element.get("geometry")
    return value if isinstance(value, dict) else None


def _payload(element: dict[str, Any]) -> dict[str, Any]:
    value = element.get("payload")
    if isinstance(value, dict):
        return value
    value = {}
    element["payload"] = value
    return value


def _metadata(element: dict[str, Any]) -> dict[str, Any]:
    value = element.get("metadata")
    if isinstance(value, dict):
        return value
    value = {}
    element["metadata"] = value
    return value


def _fixed_layout_page(page: PageV4) -> bool:
    if is_cover_face(page):
        return True
    value = " ".join(str(page.page_type or "").lower().replace("/", " ").split())
    return any(token in value for token in ("tableau", "fac-simil", "facsim", "document"))


def _rect_overlap_x(a: dict[str, float], b: dict[str, float]) -> bool:
    left = max(a["x_mm"], b["x_mm"])
    right = min(a["x_mm"] + a["width_mm"], b["x_mm"] + b["width_mm"])
    overlap = max(0.0, right - left)
    return overlap >= min(a["width_mm"], b["width_mm"]) * 0.12


def _rects_intersect(a: dict[str, float], b: dict[str, float]) -> bool:
    if not _rect_overlap_x(a, b):
        return False
    return not (
        a["y_mm"] + a["height_mm"] <= b["y_mm"] + 0.15
        or b["y_mm"] + b["height_mm"] <= a["y_mm"] + 0.15
    )


def _frame_for_format(
    book: BookV4,
    page: PageV4,
    fmt: BookFormat,
    reference_frame: str,
) -> tuple[float, float, float, float]:
    frame = str(reference_frame or PAGE).strip().lower()
    if frame == "bleed":
        return (
            -float(fmt.bleed_left_mm),
            -float(fmt.bleed_top_mm),
            float(fmt.width_mm + fmt.bleed_left_mm + fmt.bleed_right_mm),
            float(fmt.height_mm + fmt.bleed_top_mm + fmt.bleed_bottom_mm),
        )
    if frame == "margins":
        side = physical_side(book, page.id)
        if side == "recto":
            left = float(fmt.margin_inside_mm)
            right = float(fmt.margin_outside_mm)
        else:
            left = float(fmt.margin_outside_mm)
            right = float(fmt.margin_inside_mm)
        top = float(fmt.margin_top_mm)
        bottom = float(fmt.margin_bottom_mm)
        return (
            left,
            top,
            max(1.0, float(fmt.width_mm) - left - right),
            max(1.0, float(fmt.height_mm) - top - bottom),
        )
    return (0.0, 0.0, float(fmt.width_mm), float(fmt.height_mm))


def _map_geometry(
    book: BookV4,
    page: PageV4,
    element: dict[str, Any],
    old_fmt: BookFormat,
    new_fmt: BookFormat,
    *,
    preserve_aspect: bool = False,
) -> dict[str, float] | None:
    geometry = _geometry(element)
    if geometry is None:
        return None
    try:
        x = float(geometry.get("x_mm", 0.0) or 0.0)
        y = float(geometry.get("y_mm", 0.0) or 0.0)
        width = max(0.1, float(geometry.get("width_mm", 0.1) or 0.1))
        height = max(0.1, float(geometry.get("height_mm", 0.1) or 0.1))
    except (TypeError, ValueError):
        return None

    reference = str(element.get("reference_frame", PAGE) or PAGE)
    ox, oy, ow, oh = _frame_for_format(book, page, old_fmt, reference)
    nx, ny, nw, nh = _frame_for_format(book, page, new_fmt, reference)
    ow = max(1e-6, ow)
    oh = max(1e-6, oh)

    if preserve_aspect:
        # Une image n'est jamais étirée indépendamment en largeur et hauteur.
        # Sa taille suit un facteur uniforme, puis son centre conserve sa
        # position relative dans le cadre de référence.
        sx = nw / ow
        sy = nh / oh
        scale = max(1e-6, min(sx, sy))
        mapped_w = max(0.5, width * scale)
        mapped_h = max(0.5, height * scale)
        center_x_norm = ((x + width / 2.0) - ox) / ow
        center_y_norm = ((y + height / 2.0) - oy) / oh
        center_x = nx + center_x_norm * nw
        center_y = ny + center_y_norm * nh
        return {
            "x_mm": center_x - mapped_w / 2.0,
            "y_mm": center_y - mapped_h / 2.0,
            "width_mm": mapped_w,
            "height_mm": mapped_h,
            "rotation_deg": float(geometry.get("rotation_deg", 0.0) or 0.0),
        }

    return {
        "x_mm": nx + ((x - ox) / ow) * nw,
        "y_mm": ny + ((y - oy) / oh) * nh,
        "width_mm": max(0.5, width / ow * nw),
        "height_mm": max(0.5, height / oh * nh),
        "rotation_deg": float(geometry.get("rotation_deg", 0.0) or 0.0),
    }


def _set_geometry(element: dict[str, Any], geometry: dict[str, float]) -> None:
    current = _geometry(element)
    if current is None:
        element["geometry"] = dict(geometry)
        return
    current.update(geometry)


def _find_element(book: BookV4, element_id: str) -> dict[str, Any] | None:
    for page in book.pages.values():
        for element in page.content:
            if isinstance(element, dict) and str(element.get("id", "")) == element_id:
                return element
    return None


def _clamp_geometry_to_page(geometry: dict[str, float], fmt: BookFormat) -> dict[str, float]:
    result = dict(geometry)
    width = min(max(0.5, float(result.get("width_mm", 0.5))), float(fmt.width_mm))
    height = min(max(0.5, float(result.get("height_mm", 0.5))), float(fmt.height_mm))
    result["width_mm"] = width
    result["height_mm"] = height
    result["x_mm"] = max(0.0, min(float(result.get("x_mm", 0.0)), float(fmt.width_mm) - width))
    result["y_mm"] = max(0.0, min(float(result.get("y_mm", 0.0)), float(fmt.height_mm) - height))
    return result


def _apply_same_page_image_anchor(
    page: PageV4,
    element: dict[str, Any],
    mapped: dict[str, float],
    old_fmt: BookFormat,
    new_fmt: BookFormat,
) -> dict[str, float]:
    """Fait suivre une image à son texte ancré quand ce texte reste sur la page.

    Les passages vers une autre page seront traités par le moteur de flux
    complet ; ici on garantit déjà qu'un paragraphe qui grandit ou rétrécit
    entraîne l'image qui lui est logiquement attachée.
    """
    meta = _metadata(element)
    anchor_id = str(meta.get(ANCHOR_ELEMENT_ID, "") or "")
    relation = str(meta.get(ANCHOR_RELATION, "") or "")
    if not anchor_id or relation not in {"after", "before", "left_of", "right_of"}:
        return _clamp_geometry_to_page(mapped, new_fmt)

    anchor = next(
        (candidate for candidate in page.content if isinstance(candidate, dict) and str(candidate.get("id", "")) == anchor_id),
        None,
    )
    anchor_geom = _geometry(anchor) if isinstance(anchor, dict) else None
    if anchor_geom is None:
        return _clamp_geometry_to_page(mapped, new_fmt)

    try:
        gap = max(0.0, float(meta.get(ANCHOR_GAP_MM, 0.0) or 0.0))
        offset = float(meta.get(ANCHOR_OFFSET_RATIO, 0.0) or 0.0)
    except (TypeError, ValueError):
        gap, offset = 0.0, 0.0

    # Les distances autour de l'ancre suivent un facteur uniforme lié à la
    # page, comme l'image elle-même.
    scale = min(
        float(new_fmt.width_mm) / max(1e-6, float(old_fmt.width_mm)),
        float(new_fmt.height_mm) / max(1e-6, float(old_fmt.height_mm)),
    )
    gap *= max(0.01, scale)

    result = dict(mapped)
    ax = float(anchor_geom.get("x_mm", 0.0) or 0.0)
    ay = float(anchor_geom.get("y_mm", 0.0) or 0.0)
    aw = max(1.0, float(anchor_geom.get("width_mm", 1.0) or 1.0))
    ah = max(0.5, float(anchor_geom.get("height_mm", 0.5) or 0.5))

    if relation == "after":
        result["x_mm"] = ax + offset * aw
        result["y_mm"] = ay + ah + gap
    elif relation == "before":
        result["x_mm"] = ax + offset * aw
        result["y_mm"] = ay - float(result["height_mm"]) - gap
    elif relation == "right_of":
        result["x_mm"] = ax + aw + gap
        result["y_mm"] = ay + offset * ah
    elif relation == "left_of":
        result["x_mm"] = ax - float(result["width_mm"]) - gap
        result["y_mm"] = ay + offset * ah

    return _clamp_geometry_to_page(result, new_fmt)


def restore_format_content_continuations(book: BookV4) -> int:
    """Réunit les morceaux de texte créés par le changement de format précédent."""
    continuation_ids = [
        page_id
        for page_id in book.page_order
        if bool(book.pages[page_id].metadata.get(_CONTINUATION, False))
    ]
    if not continuation_ids:
        return 0

    pieces: dict[str, list[tuple[int, str]]] = {}
    for page_id in continuation_ids:
        page = book.pages[page_id]
        for element in page.content:
            if not isinstance(element, dict) or _kind(element) != TEXT:
                continue
            meta = _metadata(element)
            origin = str(meta.get(_ORIGIN_ELEMENT, "") or "")
            if not origin:
                continue
            try:
                index = int(meta.get(_SEGMENT_INDEX, 1) or 1)
            except (TypeError, ValueError):
                index = 1
            text = " ".join(str(_payload(element).get("text", "") or "").split())
            if text:
                pieces.setdefault(origin, []).append((index, text))

    for origin_id, values in pieces.items():
        origin = _find_element(book, origin_id)
        if origin is None:
            continue
        payload = _payload(origin)
        first = " ".join(str(payload.get("text", "") or "").split())
        ordered = [text for _index, text in sorted(values)]
        payload["text"] = " ".join([value for value in [first, *ordered] if value]).strip()
        meta = _metadata(origin)
        meta.pop("format_content_split", None)
        meta.pop("format_content_hidden_origin", None)

    for page_id in continuation_ids:
        if page_id in book.page_order:
            book.page_order.remove(page_id)
        book.pages.pop(page_id, None)

    book.validate()
    return len(continuation_ids)


def _split_lines(lines: tuple[str, ...], count: int) -> tuple[str, str]:
    count = max(0, min(int(count), len(lines)))
    first = " ".join(lines[:count]).strip()
    rest = " ".join(lines[count:]).strip()
    return first, rest


def _continuation_chunks(
    template: dict[str, Any],
    text: str,
    usable_width: float,
    usable_height: float,
) -> list[tuple[str, float]]:
    probe = deepcopy(template)
    _payload(probe)["text"] = text
    layout = measure_text_layout(probe, usable_width, source_geometry=_geometry(template))
    max_lines = max(1, int((usable_height - 0.4) // max(0.5, layout.line_height_mm)))
    result: list[tuple[str, float]] = []
    lines = list(layout.lines)
    while lines:
        take = min(max_lines, len(lines))
        value = " ".join(lines[:take]).strip()
        lines = lines[take:]
        height = min(
            usable_height,
            layout.line_height_mm * max(1, take) + 0.4,
        )
        result.append((value, height))
    return result or [(text, min(usable_height, layout.required_height_mm))]


def _build_continuation_pages(
    book: BookV4,
    source_page: PageV4,
    overflow: list[tuple[dict[str, Any], str]],
    fmt: BookFormat,
) -> list[PageV4]:
    if not overflow:
        return []

    usable_width = max(
        1.0,
        float(fmt.width_mm) - float(fmt.margin_inside_mm) - float(fmt.margin_outside_mm),
    )
    usable_height = max(
        1.0,
        float(fmt.height_mm) - float(fmt.margin_top_mm) - float(fmt.margin_bottom_mm),
    )

    # Préparer les segments avant de connaître la parité exacte des nouvelles pages.
    segments: list[tuple[dict[str, Any], str, float, int]] = []
    segment_index_by_origin: dict[str, int] = {}
    for template, text in overflow:
        origin_id = str(template.get("id", "") or "")
        for chunk, height in _continuation_chunks(template, text, usable_width, usable_height):
            next_index = segment_index_by_origin.get(origin_id, 0) + 1
            segment_index_by_origin[origin_id] = next_index
            segments.append((template, chunk, height, next_index))

    pages: list[PageV4] = []
    current: PageV4 | None = None
    current_y = float(fmt.margin_top_mm)
    bottom = float(fmt.height_mm) - float(fmt.margin_bottom_mm)

    for template, text, height, segment_index in segments:
        # Chaque bloc peut partager une page de continuation avec le suivant.
        if current is None or current_y + height > bottom + 0.01:
            current = PageV4(
                page_type="Page texte",
                title=(f"{source_page.title} — suite" if source_page.title else "Suite"),
                origin=PageOrigin.AUTHOR,
                source=None,
                part_id=source_page.part_id,
                metadata={
                    _CONTINUATION: True,
                    "format_reflow_generated": True,
                    "format_content_origin_page_id": source_page.id,
                    "source_visual_preserved": False,
                },
            )
            pages.append(current)
            current_y = float(fmt.margin_top_mm)

        payload = deepcopy(_payload(template))
        payload["text"] = text
        meta = deepcopy(_metadata(template))
        meta.update({
            "origin": "format_content_reflow",
            _ADAPTED: True,
            _ORIGIN_ELEMENT: str(template.get("id", "") or ""),
            _SEGMENT_INDEX: segment_index,
            "source_visual_preserved": False,
        })
        meta.pop(_KEEP_SOURCE, None)

        element = new_element(
            kind=TEXT,
            x_mm=float(fmt.margin_inside_mm),  # corrigé après insertion selon recto/verso
            y_mm=current_y,
            width_mm=usable_width,
            height_mm=height,
            reference_frame=PAGE,
            source_ref=deepcopy(template.get("source_ref")),
            payload=payload,
            metadata=meta,
        )
        current.content.append(element)
        current_y += height + 2.0

    return pages


def _insert_continuations(
    book: BookV4,
    plans: list[tuple[str, list[PageV4]]],
    fmt: BookFormat,
) -> int:
    created_ids: list[str] = []
    # Insertion en partant de la fin pour garder les ancres stables.
    order_index = {page_id: index for index, page_id in enumerate(book.page_order)}
    for source_page_id, pages in sorted(
        plans,
        key=lambda value: order_index.get(value[0], -1),
        reverse=True,
    ):
        if not pages or source_page_id not in book.page_order:
            continue
        insert_at = book.page_order.index(source_page_id) + 1
        for page in pages:
            book.pages[page.id] = page
            book.page_order.insert(insert_at, page.id)
            insert_at += 1
            created_ids.append(page.id)

    # Les marges intérieur/extérieur dépendent de la parité obtenue après insertion.
    for page_id in created_ids:
        page = book.pages[page_id]
        side = physical_side(book, page_id)
        left = float(fmt.margin_inside_mm if side == "recto" else fmt.margin_outside_mm)
        width = max(
            1.0,
            float(fmt.width_mm) - float(fmt.margin_inside_mm) - float(fmt.margin_outside_mm),
        )
        for element in page.content:
            if not isinstance(element, dict) or _kind(element) != TEXT:
                continue
            geometry = _geometry(element)
            if geometry is not None:
                geometry["x_mm"] = left
                geometry["width_mm"] = width

    book.validate()
    return len(created_ids)



def _reference_matches(book: BookV4, fmt: BookFormat) -> bool:
    raw = book.metadata.get("format_content_reference_format")
    if not isinstance(raw, dict):
        return False
    for key in (
        "width_mm",
        "height_mm",
        "margin_top_mm",
        "margin_bottom_mm",
        "margin_inside_mm",
        "margin_outside_mm",
    ):
        try:
            if abs(float(raw[key]) - float(getattr(fmt, key))) > 0.05:
                return False
        except (KeyError, TypeError, ValueError):
            return False
    return True


def _restore_reference_source_pages(book: BookV4) -> tuple[int, int, int]:
    pages = texts = images = 0
    for page in book.pages.values():
        if bool(page.metadata.get("format_reflow_generated", False)):
            continue
        if bool(page.metadata.get(_CONTINUATION, False)):
            continue
        changed = False
        for element in page.content:
            if not isinstance(element, dict):
                continue
            meta = _metadata(element)
            reference = meta.get("format_reference_geometry")
            if isinstance(reference, dict) and not page.modifications:
                _set_geometry(element, deepcopy(reference))
                changed = True
            meta.pop(_ADAPTED, None)
            meta.pop(_KEEP_SOURCE, None)
            meta.pop("format_image_fit", None)
            meta.pop("format_content_split", None)
            meta.pop("format_content_hidden_origin", None)
            if str(meta.get("origin", "")) == "analysis_source":
                meta["source_visual_preserved"] = True
            if _kind(element) == TEXT:
                texts += 1
            elif _kind(element) == IMAGE:
                images += 1
        if changed:
            pages += 1
        page.metadata.pop(_ADAPTED, None)
        page.metadata.pop("format_fixed_layout_contain", None)
        if page.source is not None:
            page.metadata["source_visual_preserved"] = True
    return pages, texts, images

def adapt_book_content_for_format(
    book: BookV4,
    *,
    old_format: BookFormat,
    new_format: BookFormat,
) -> FormatContentAdaptationResult:
    """Adapte les pages qui n'ont pas été entièrement repaginées."""

    # Si l'utilisateur revient exactement au format de référence et que la
    # page n'a pas été retouchée manuellement, retrouver la géométrie Source
    # plutôt que recalculer une approximation.
    if _reference_matches(book, new_format):
        pages, texts, images = _restore_reference_source_pages(book)
        return FormatContentAdaptationResult(
            adapted_pages=pages,
            adapted_texts=texts,
            adapted_images=images,
            continuation_pages=0,
            overflow_blocks=0,
            fixed_layout_pages=0,
        )

    adapted_pages = 0
    adapted_texts = 0
    adapted_images = 0
    fixed_layout_pages = 0
    overflow_blocks = 0
    continuation_plans: list[tuple[str, list[PageV4]]] = []

    for page_id in list(book.page_order):
        page = book.pages.get(page_id)
        if page is None:
            continue
        if bool(page.metadata.get("format_reflow_generated", False)):
            continue
        if bool(page.metadata.get(_CONTINUATION, False)):
            continue

        # Les projets créés avant l'introduction des ancres sont enrichis au
        # premier changement de format ; les nouveaux projets les possèdent
        # déjà dès l'analyse Source.
        try:
            infer_page_content_anchors(book, page.id, overwrite=False)
        except Exception:
            pass

        if _fixed_layout_page(page):
            fixed_layout_pages += 1
            page.metadata["format_fixed_layout_contain"] = True
            page.metadata.pop(_ADAPTED, None)
            # Même si le rendu de ces pages reste un fac-similé contenu (et non
            # désassemblé), conserver une géométrie logique au nouveau format.
            # Ainsi un élément que l'utilisateur détachera ensuite repart d'un
            # cadre cohérent au lieu de l'ancienne taille de page.
            for element in page.content:
                if not isinstance(element, dict):
                    continue
                meta = _metadata(element)
                geometry_before = _geometry(element)
                if isinstance(geometry_before, dict):
                    meta.setdefault("format_reference_geometry", deepcopy(geometry_before))
                    mapped = _map_geometry(
                        book,
                        page,
                        element,
                        old_format,
                        new_format,
                        preserve_aspect=(_kind(element) == IMAGE),
                    )
                    if mapped is not None:
                        _set_geometry(element, _clamp_geometry_to_page(mapped, new_format))
                        if _kind(element) == IMAGE:
                            meta["format_image_aspect_preserved"] = True
                meta[_KEEP_SOURCE] = True
                meta.pop(_ADAPTED, None)
            continue

        page.metadata.pop("format_fixed_layout_contain", None)
        try:
            roles = page_element_roles(book, page_id)
        except Exception:
            roles = {}

        body_records: list[dict[str, Any]] = []
        blockers: list[dict[str, float]] = []
        changed = False

        # 1. Adapter les cadres et mesurer les textes.
        for element in page.content:
            if not isinstance(element, dict):
                continue
            geometry_before = deepcopy(_geometry(element))
            if not isinstance(geometry_before, dict):
                continue
            _metadata(element).setdefault(
                "format_reference_geometry",
                deepcopy(geometry_before),
            )
            kind = _kind(element)
            mapped = _map_geometry(
                book,
                page,
                element,
                old_format,
                new_format,
                preserve_aspect=(kind == IMAGE),
            )
            if mapped is None:
                continue

            meta = _metadata(element)
            meta.pop(_KEEP_SOURCE, None)
            meta[_ADAPTED] = True
            meta["source_visual_preserved"] = False
            changed = True

            if kind == IMAGE:
                # Première géométrie proportionnelle. L'ancre est appliquée
                # après la recomposition des textes, lorsque leur hauteur
                # définitive est connue.
                _set_geometry(element, _clamp_geometry_to_page(mapped, new_format))
                meta["format_image_fit"] = "contain"
                meta["format_image_aspect_preserved"] = True
                blockers.append({
                    "x_mm": mapped["x_mm"],
                    "y_mm": mapped["y_mm"],
                    "width_mm": mapped["width_mm"],
                    "height_mm": mapped["height_mm"],
                })
                adapted_images += 1
                continue

            if kind != TEXT:
                _set_geometry(element, mapped)
                blockers.append({
                    "x_mm": mapped["x_mm"],
                    "y_mm": mapped["y_mm"],
                    "width_mm": mapped["width_mm"],
                    "height_mm": mapped["height_mm"],
                })
                continue

            remember_source_metrics(element, geometry_before)
            layout = measure_text_layout(
                element,
                mapped["width_mm"],
                source_geometry=geometry_before,
            )
            mapped["height_mm"] = max(0.8, layout.required_height_mm)
            role_obj = roles.get(str(element.get("id", "") or ""))
            role = getattr(role_obj, "role", "") if role_obj is not None else ""
            record = {
                "element": element,
                "geometry": mapped,
                "layout": layout,
                "role": role,
                "source_y": float(geometry_before.get("y_mm", 0.0) or 0.0),
            }
            if role == ROLE_BODY:
                body_records.append(record)
            else:
                # Les titres, légendes et notes conservent leur ancrage, mais leur
                # hauteur suit réellement le texte recomposé.
                mapped["y_mm"] = max(
                    0.0,
                    min(mapped["y_mm"], float(new_format.height_mm) - mapped["height_mm"]),
                )
                _set_geometry(element, mapped)
                blockers.append({
                    "x_mm": mapped["x_mm"],
                    "y_mm": mapped["y_mm"],
                    "width_mm": mapped["width_mm"],
                    "height_mm": mapped["height_mm"],
                })
                adapted_texts += 1

        if not changed:
            continue

        page.metadata[_ADAPTED] = True
        page.metadata["source_visual_preserved"] = False
        adapted_pages += 1

        # 2. Flux de corps : résoudre les collisions verticales puis déborder
        # proprement vers une page de continuation, jamais hors du format.
        body_records.sort(key=lambda item: (item["source_y"], item["geometry"]["x_mm"]))
        placed_body: list[dict[str, float]] = []
        overflow: list[tuple[dict[str, Any], str]] = []
        bottom = float(new_format.height_mm) - float(new_format.margin_bottom_mm)
        gap = 1.5

        for record in body_records:
            element = record["element"]
            geometry = dict(record["geometry"])
            layout = record["layout"]
            geometry["y_mm"] = max(float(new_format.margin_top_mm), geometry["y_mm"])

            # N'avancer que devant les objets qui occupent réellement la même colonne.
            moved = True
            while moved:
                moved = False
                candidate = {
                    "x_mm": geometry["x_mm"],
                    "y_mm": geometry["y_mm"],
                    "width_mm": geometry["width_mm"],
                    "height_mm": geometry["height_mm"],
                }
                for blocker in [*blockers, *placed_body]:
                    if _rects_intersect(candidate, blocker):
                        geometry["y_mm"] = blocker["y_mm"] + blocker["height_mm"] + gap
                        moved = True
                        break

            available = bottom - geometry["y_mm"]
            if geometry["height_mm"] <= available + 0.01:
                _set_geometry(element, geometry)
                placed_body.append({
                    "x_mm": geometry["x_mm"],
                    "y_mm": geometry["y_mm"],
                    "width_mm": geometry["width_mm"],
                    "height_mm": geometry["height_mm"],
                })
                adapted_texts += 1
                continue

            allowed_lines = int(max(0.0, available - 0.4) // max(0.5, layout.line_height_mm))
            first_text, rest_text = _split_lines(layout.lines, allowed_lines)
            payload = _payload(element)
            if first_text:
                payload["text"] = first_text
                geometry["height_mm"] = min(
                    max(0.8, layout.line_height_mm * allowed_lines + 0.4),
                    max(0.8, available),
                )
                _set_geometry(element, geometry)
                placed_body.append({
                    "x_mm": geometry["x_mm"],
                    "y_mm": geometry["y_mm"],
                    "width_mm": geometry["width_mm"],
                    "height_mm": geometry["height_mm"],
                })
            else:
                # L'identité du bloc reste sur sa page d'origine pour permettre
                # la réunion au prochain changement de format, mais il n'est pas
                # dessiné dans une zone impossible.
                payload["text"] = ""
                geometry["height_mm"] = 0.8
                geometry["y_mm"] = max(float(new_format.margin_top_mm), bottom - 0.8)
                _set_geometry(element, geometry)
                _metadata(element)["format_content_hidden_origin"] = True

            if rest_text:
                _metadata(element)["format_content_split"] = True
                overflow.append((element, rest_text))
                overflow_blocks += 1
            adapted_texts += 1

        # 3. Les images suivent maintenant leur ancre logique après que le
        # texte a pris sa hauteur finale. La taille de l'image reste strictement
        # proportionnelle ; seule sa position peut suivre le texte.
        for element in page.content:
            if not isinstance(element, dict) or _kind(element) != IMAGE:
                continue
            reference = _metadata(element).get("format_reference_geometry")
            if not isinstance(reference, dict):
                reference = _geometry(element)
            if not isinstance(reference, dict):
                continue
            mapped_image = _map_geometry(
                book,
                page,
                {**element, "geometry": reference},
                old_format,
                new_format,
                preserve_aspect=True,
            )
            if mapped_image is None:
                continue
            anchored = _apply_same_page_image_anchor(
                page,
                element,
                mapped_image,
                old_format,
                new_format,
            )
            _set_geometry(element, anchored)

        if overflow:
            continuation_plans.append(
                (page.id, _build_continuation_pages(book, page, overflow, new_format))
            )

    continuation_pages = _insert_continuations(book, continuation_plans, new_format)
    book.history.append({
        "action": "adaptation_contenu_format",
        "adapted_pages": adapted_pages,
        "adapted_texts": adapted_texts,
        "adapted_images": adapted_images,
        "continuation_pages": continuation_pages,
        "overflow_blocks": overflow_blocks,
        "fixed_layout_pages": fixed_layout_pages,
    })
    book.validate()

    return FormatContentAdaptationResult(
        adapted_pages=adapted_pages,
        adapted_texts=adapted_texts,
        adapted_images=adapted_images,
        continuation_pages=continuation_pages,
        overflow_blocks=overflow_blocks,
        fixed_layout_pages=fixed_layout_pages,
    )
