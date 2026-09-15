from __future__ import annotations

"""Inventaire factuel du contenu d'une page TomeLinea V4.

Cette couche ne classe pas éditorialement la page et ne modifie rien.
Elle rassemble seulement ce qui est déjà connu du Livre / de la Source :
éléments de Composition, fragments typographiques et structures Source.
"""

from typing import Any

from src.v4.domain import BookV4, PageV4
from src.v4.image_quality import effective_dpi


def _number(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _geometry(value: Any) -> dict[str, float]:
    data = value if isinstance(value, dict) else {}
    return {
        "x_mm": _number(data.get("x_mm")),
        "y_mm": _number(data.get("y_mm")),
        "width_mm": _number(data.get("width_mm")),
        "height_mm": _number(data.get("height_mm")),
    }


def _norm_bbox_to_mm(book: BookV4, bbox: Any) -> dict[str, float] | None:
    if not isinstance(bbox, (list, tuple)) or len(bbox) != 4:
        return None
    try:
        x0, y0, x1, y1 = (float(item) for item in bbox)
    except (TypeError, ValueError):
        return None
    width = float(book.format.width_mm)
    height = float(book.format.height_mm)
    return {
        "x_mm": x0 * width,
        "y_mm": y0 * height,
        "width_mm": max(0.0, (x1 - x0) * width),
        "height_mm": max(0.0, (y1 - y0) * height),
    }


def _preview(text: Any, limit: int = 58) -> str:
    value = " ".join(str(text or "").split())
    if len(value) <= limit:
        return value
    return value[: max(1, limit - 1)].rstrip() + "…"


def _text_fragments(book: BookV4, element: dict[str, Any]) -> list[dict[str, Any]]:
    payload = element.get("payload", {})
    if not isinstance(payload, dict):
        return []
    spans = payload.get("spans", [])
    if not isinstance(spans, list):
        return []
    element_id = str(element.get("id", ""))
    result: list[dict[str, Any]] = []
    for index, span in enumerate(spans):
        if not isinstance(span, dict):
            continue
        line_index = int(span.get("line_index", 0) or 0)
        span_index = int(span.get("span_index", index) or 0)
        result.append(
            {
                "id": f"{element_id}:fragment:{line_index}:{span_index}",
                "text": str(span.get("text", "") or ""),
                "font": str(span.get("font", "") or ""),
                "size_pt": _number(span.get("size")),
                "flags": int(span.get("flags", 0) or 0),
                "color": span.get("color"),
                "geometry": _norm_bbox_to_mm(book, span.get("bbox_norm")),
                "line_index": line_index,
                "span_index": span_index,
            }
        )
    return result


def _element_item(book: BookV4, element: dict[str, Any], index: int) -> dict[str, Any] | None:
    kind = str(element.get("kind", "") or "").lower()
    if kind not in {"text", "image", "document"}:
        return None
    element_id = str(element.get("id", "") or f"element:{index}")
    geometry = _geometry(element.get("geometry"))
    payload = element.get("payload", {})
    if not isinstance(payload, dict):
        payload = {}
    metadata = element.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}

    item: dict[str, Any] = {
        "id": element_id,
        "kind": kind,
        "geometry": geometry,
        "source": element.get("source_ref"),
        "origin": str(metadata.get("origin", "") or ""),
        "content_index": index,
    }

    if kind == "text":
        fragments = _text_fragments(book, element)
        text = str(payload.get("text", "") or "")
        fonts = sorted({str(fragment.get("font", "")) for fragment in fragments if fragment.get("font")})
        item.update(
            {
                "label": _preview(text) or "Texte",
                "text": text,
                "fragment_count": len(fragments),
                "fragments": fragments,
                "fonts": fonts,
            }
        )

    elif kind == "image":
        width_px = int(payload.get("width_px", 0) or 0)
        height_px = int(payload.get("height_px", 0) or 0)
        quality = None
        if width_px > 0 and height_px > 0 and geometry["width_mm"] > 0 and geometry["height_mm"] > 0:
            try:
                q = effective_dpi(
                    width_px=width_px,
                    height_px=height_px,
                    width_mm=geometry["width_mm"],
                    height_mm=geometry["height_mm"],
                )
                quality = {
                    "effective_dpi": q.effective_dpi,
                    "status": q.status,
                    "dpi_x": q.dpi_x,
                    "dpi_y": q.dpi_y,
                }
            except Exception:
                quality = None
        item.update(
            {
                "label": f"Image {width_px} × {height_px} px" if width_px and height_px else "Image",
                "width_px": width_px,
                "height_px": height_px,
                "xref": int(payload.get("xref", 0) or 0),
                "quality": quality,
            }
        )

    else:
        item.update({"label": str(payload.get("name", "") or "Document")})

    return item


def _table_structures(book: BookV4, page: PageV4) -> list[dict[str, Any]]:
    values = page.metadata.get("source_layout_tables", [])
    if not isinstance(values, list):
        return []
    result = []
    for index, table in enumerate(values):
        if not isinstance(table, dict):
            continue
        table_index = int(table.get("table_index", index) or index)
        rows = table.get("rows", [])
        if not isinstance(rows, list):
            rows = []
        result.append(
            {
                "id": f"{page.id}:table:{table_index}",
                "kind": "table_structure",
                "label": f"Structure tabulaire {int(table.get('row_count', len(rows)) or 0)} × {int(table.get('col_count', 0) or 0)}",
                "geometry": _norm_bbox_to_mm(book, table.get("bbox_norm")),
                "row_count": int(table.get("row_count", len(rows)) or 0),
                "col_count": int(table.get("col_count", 0) or 0),
                "rows": rows,
                "structure_index": table_index,
            }
        )
    return result


def _list_structures(page: PageV4) -> list[dict[str, Any]]:
    values = page.metadata.get("source_layout_lists", [])
    if not isinstance(values, list):
        return []
    result = []
    for index, value in enumerate(values):
        if not isinstance(value, dict):
            continue
        items = value.get("items", [])
        if not isinstance(items, list):
            items = []
        kind = str(value.get("kind", "") or "")
        label = "Liste structurée"
        if kind == "two_column":
            label = "Liste structurée à deux colonnes"
        elif kind == "checklist":
            label = "Liste à cases"
        result.append(
            {
                "id": f"{page.id}:list:{index}",
                "kind": "list_structure",
                "label": label,
                "item_count": int(value.get("item_count", len(items)) or 0),
                "items": items,
                "structure_index": index,
                "source_kind": kind,
            }
        )
    return result


def page_content_inventory(book: BookV4, page_id: str) -> dict[str, Any]:
    """Retourne l'inventaire factuel, sans modifier le Livre."""
    page = book.pages.get(page_id)
    if page is None:
        raise KeyError(page_id)

    elements: list[dict[str, Any]] = []
    for index, raw in enumerate(page.content):
        if not isinstance(raw, dict):
            continue
        item = _element_item(book, raw, index)
        if item is not None:
            elements.append(item)

    # Ordre visuel purement géométrique : haut -> bas, puis gauche -> droite.
    visual_order = sorted(
        (item["id"] for item in elements),
        key=lambda item_id: next(
            (
                (
                    float(item["geometry"].get("y_mm", 0.0)),
                    float(item["geometry"].get("x_mm", 0.0)),
                    int(item.get("content_index", 0)),
                )
                for item in elements
                if item["id"] == item_id
            ),
            (0.0, 0.0, 0),
        ),
    )

    tables = _table_structures(book, page)
    lists = _list_structures(page)
    counts = {
        "text": sum(1 for item in elements if item["kind"] == "text"),
        "image": sum(1 for item in elements if item["kind"] == "image"),
        "document": sum(1 for item in elements if item["kind"] == "document"),
        "text_fragments": sum(int(item.get("fragment_count", 0)) for item in elements if item["kind"] == "text"),
        "table_structure": len(tables),
        "list_structure": len(lists),
    }
    fonts = sorted(
        {
            font
            for item in elements
            if item["kind"] == "text"
            for font in item.get("fonts", [])
            if font
        }
    )

    return {
        "page_id": page.id,
        "page_title": page.title,
        "page_type": page.page_type,
        "source_page": page.source.source_page if page.source is not None else None,
        "counts": counts,
        "fonts": fonts,
        "elements": elements,
        "structures": tables + lists,
        "visual_order": visual_order,
    }


def book_content_inventory(book: BookV4) -> dict[str, dict[str, Any]]:
    return {page_id: page_content_inventory(book, page_id) for page_id in book.page_order}
