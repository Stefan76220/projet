from __future__ import annotations

"""Première compréhension éditoriale des éléments d'une page TomeLinea V4.

Cette couche est volontairement séparée de l'inventaire factuel :
- elle ne modifie jamais le Livre ;
- elle ne remplace pas les faits extraits de la Source ;
- elle produit seulement un rôle éditorial proposé, déterministe et explicable.

Une future IA pourra contrôler ou compléter ces propositions sans changer
le contrat de l'inventaire brut.
"""

from dataclasses import dataclass
from typing import Any

from src.v4.domain import BookV4, PageV4
from src.v4.page_content_inventory import page_content_inventory


ROLE_PAGE_TITLE = "Titre de page"
ROLE_SUBTITLE = "Sous-titre / précision"
ROLE_SECTION_HEADING = "Intertitre"
ROLE_BODY = "Corps de texte"
ROLE_CAPTION = "Légende"
ROLE_GALLERY_LABEL = "Libellé d’image"
ROLE_NOTE = "Note / mention"
ROLE_LIST_ITEM = "Élément de liste"
ROLE_TABLE_HEADER = "En-tête de tableau"
ROLE_TABLE_CONTENT = "Contenu de tableau"
ROLE_MAIN_IMAGE = "Image principale"
ROLE_GALLERY_IMAGE = "Image de galerie"
ROLE_FACSIMILE = "Fac-similé"
ROLE_DOCUMENT = "Document"


@dataclass(frozen=True, slots=True)
class ElementEditorialRole:
    element_id: str
    role: str
    confidence: float
    reason: str


def _norm(value: Any) -> str:
    return " ".join(str(value or "").lower().replace("’", "'").split())


def _font_sizes(item: dict[str, Any]) -> list[float]:
    values: list[float] = []
    for fragment in item.get("fragments", []) or []:
        if not isinstance(fragment, dict):
            continue
        try:
            size = float(fragment.get("size_pt", 0.0) or 0.0)
        except (TypeError, ValueError):
            size = 0.0
        if size > 0:
            values.append(size)
    return values


def _max_font(item: dict[str, Any]) -> float:
    values = _font_sizes(item)
    return max(values, default=0.0)


def _is_bold(item: dict[str, Any]) -> bool:
    return any("bold" in str(font or "").lower() for font in item.get("fonts", []) or [])


def _geom(item: dict[str, Any]) -> tuple[float, float, float, float]:
    value = item.get("geometry", {})
    if not isinstance(value, dict):
        value = {}
    try:
        return (
            float(value.get("x_mm", 0.0) or 0.0),
            float(value.get("y_mm", 0.0) or 0.0),
            float(value.get("width_mm", 0.0) or 0.0),
            float(value.get("height_mm", 0.0) or 0.0),
        )
    except (TypeError, ValueError):
        return (0.0, 0.0, 0.0, 0.0)


def _intersection_ratio(item: dict[str, Any], structure: dict[str, Any]) -> float:
    ax, ay, aw, ah = _geom(item)
    bx, by, bw, bh = _geom(structure)
    if aw <= 0 or ah <= 0 or bw <= 0 or bh <= 0:
        return 0.0
    x0 = max(ax, bx)
    y0 = max(ay, by)
    x1 = min(ax + aw, bx + bw)
    y1 = min(ay + ah, by + bh)
    area = max(0.0, x1 - x0) * max(0.0, y1 - y0)
    return area / max(1e-9, aw * ah)


def _source_block_index(page: PageV4, element_id: str) -> int | None:
    for raw in page.content:
        if not isinstance(raw, dict) or str(raw.get("id", "")) != element_id:
            continue
        metadata = raw.get("metadata", {})
        if not isinstance(metadata, dict):
            return None
        value = metadata.get("source_block_index")
        try:
            return int(value) if value is not None else None
        except (TypeError, ValueError):
            return None
    return None


def _list_block_indices(page: PageV4) -> set[int]:
    result: set[int] = set()
    values = page.metadata.get("source_layout_lists", [])
    if not isinstance(values, list):
        return result
    for structure in values:
        if not isinstance(structure, dict):
            continue
        for item in structure.get("items", []) or []:
            if not isinstance(item, dict):
                continue
            value = item.get("block_index")
            try:
                if value is not None:
                    result.add(int(value))
            except (TypeError, ValueError):
                pass
    return result


def _table_role(item: dict[str, Any], structures: list[dict[str, Any]]) -> ElementEditorialRole | None:
    for structure in structures:
        if structure.get("kind") != "table_structure":
            continue
        if _intersection_ratio(item, structure) < 0.70:
            continue
        rows = structure.get("rows", [])
        first_row_text = ""
        if isinstance(rows, list) and rows and isinstance(rows[0], list):
            first_row_text = _norm(" ".join(str(value or "") for value in rows[0]))
        if first_row_text and _norm(item.get("text", "")) == first_row_text:
            return ElementEditorialRole(
                str(item.get("id", "")),
                ROLE_TABLE_HEADER,
                0.98,
                "Le texte correspond à la première ligne d'une structure tabulaire détectée.",
            )
        return ElementEditorialRole(
            str(item.get("id", "")),
            ROLE_TABLE_CONTENT,
            0.96,
            "Le texte se trouve dans une structure tabulaire détectée.",
        )
    return None


def _image_role(page: PageV4, item: dict[str, Any], image_count: int) -> ElementEditorialRole:
    page_type = _norm(page.page_type)
    element_id = str(item.get("id", ""))
    if "fac-sim" in page_type or "facsim" in page_type or "document" in page_type:
        return ElementEditorialRole(
            element_id,
            ROLE_FACSIMILE,
            0.98,
            "La page est identifiée comme document / fac-similé.",
        )
    if image_count >= 2:
        return ElementEditorialRole(
            element_id,
            ROLE_GALLERY_IMAGE,
            0.94,
            "Plusieurs images indépendantes composent la page.",
        )
    return ElementEditorialRole(
        element_id,
        ROLE_MAIN_IMAGE,
        0.90,
        "Il s'agit de l'image principale ou unique de la page.",
    )


def _nearest_image_below_label(
    item: dict[str, Any],
    images: list[dict[str, Any]],
) -> bool:
    x, y, w, _h = _geom(item)
    if w <= 0:
        return False
    center = x + w / 2.0
    for image in images:
        ix, iy, iw, ih = _geom(image)
        if iw <= 0 or ih <= 0:
            continue
        image_bottom = iy + ih
        gap = y - image_bottom
        if -1.5 <= gap <= 9.0 and ix - 3.0 <= center <= ix + iw + 3.0:
            return True
    return False


def page_element_roles(book: BookV4, page_id: str) -> dict[str, ElementEditorialRole]:
    """Retourne une proposition de rôle pour chaque élément réel de la page."""
    page = book.pages.get(page_id)
    if page is None:
        raise KeyError(page_id)

    inventory = page_content_inventory(book, page_id)
    elements = [item for item in inventory.get("elements", []) if isinstance(item, dict)]
    structures = [item for item in inventory.get("structures", []) if isinstance(item, dict)]
    texts = [item for item in elements if item.get("kind") == "text"]
    images = [item for item in elements if item.get("kind") == "image"]
    result: dict[str, ElementEditorialRole] = {}

    for item in images:
        role = _image_role(page, item, len(images))
        if role.element_id:
            result[role.element_id] = role

    for item in elements:
        if item.get("kind") == "document":
            element_id = str(item.get("id", ""))
            if element_id:
                result[element_id] = ElementEditorialRole(
                    element_id,
                    ROLE_DOCUMENT,
                    0.99,
                    "L'élément est un document distinct.",
                )

    if not texts:
        return result

    page_h = max(1.0, float(book.format.height_mm))
    body_sizes = sorted(size for item in texts for size in _font_sizes(item) if size > 0)
    median_size = body_sizes[len(body_sizes) // 2] if body_sizes else 10.0

    page_title_norm = _norm(page.title)
    title_item: dict[str, Any] | None = None
    exact_title = [item for item in texts if _norm(item.get("text")) == page_title_norm and page_title_norm]
    if exact_title:
        title_item = min(exact_title, key=lambda item: _geom(item)[1])
    else:
        top_candidates = [item for item in texts if _geom(item)[1] <= page_h * 0.22]
        if top_candidates:
            title_item = max(top_candidates, key=lambda item: (_max_font(item), -_geom(item)[1]))

    title_id = str(title_item.get("id", "")) if title_item is not None else ""
    title_y = _geom(title_item)[1] if title_item is not None else 0.0
    title_bottom = title_y + (_geom(title_item)[3] if title_item is not None else 0.0)
    title_size = _max_font(title_item) if title_item is not None else 0.0

    visual_texts = sorted(texts, key=lambda item: (_geom(item)[1], _geom(item)[0]))
    immediate_after_title_id = ""
    if title_item is not None:
        try:
            title_position = next(
                index for index, candidate in enumerate(visual_texts)
                if str(candidate.get("id", "")) == title_id
            )
            if title_position + 1 < len(visual_texts):
                immediate_after_title_id = str(visual_texts[title_position + 1].get("id", ""))
        except StopIteration:
            pass

    list_indices = _list_block_indices(page)

    for item in texts:
        element_id = str(item.get("id", ""))
        if not element_id:
            continue
        text = str(item.get("text", "") or "").strip()
        norm = _norm(text)
        x, y, width, height = _geom(item)
        font_size = _max_font(item)
        words = len(text.split())
        block_index = _source_block_index(page, element_id)

        if element_id == title_id:
            result[element_id] = ElementEditorialRole(
                element_id,
                ROLE_PAGE_TITLE,
                0.99 if page_title_norm and norm == page_title_norm else 0.92,
                "Le texte correspond au titre de la page et domine la zone supérieure.",
            )
            continue

        if len(images) >= 2 and words <= 5 and _nearest_image_below_label(item, images):
            result[element_id] = ElementEditorialRole(
                element_id,
                ROLE_GALLERY_LABEL,
                0.96,
                "Texte court placé immédiatement sous une image d'une galerie.",
            )
            continue

        table = _table_role(item, structures)
        if table is not None:
            result[element_id] = table
            continue

        if block_index is not None and block_index in list_indices:
            result[element_id] = ElementEditorialRole(
                element_id,
                ROLE_LIST_ITEM,
                0.98,
                "Le bloc appartient à une structure de liste détectée dans la Source.",
            )
            continue

        if (
            norm.startswith("légende:")
            or norm.startswith("légende :")
            or norm.startswith("legende:")
            or norm.startswith("legende :")
        ):
            result[element_id] = ElementEditorialRole(
                element_id,
                ROLE_CAPTION,
                0.99,
                "Le texte se présente explicitement comme une légende.",
            )
            continue

        if (
            norm.startswith("note:")
            or norm.startswith("note :")
            or norm.startswith("source:")
            or norm.startswith("source :")
        ):
            result[element_id] = ElementEditorialRole(
                element_id,
                ROLE_NOTE,
                0.99,
                "Le texte se présente explicitement comme une note ou une source.",
            )
            continue

        if (
            title_item is not None
            and element_id == immediate_after_title_id
            and y >= title_bottom - 1.0
            and y <= title_bottom + 20.0
            and words <= 14
            and (font_size >= median_size + 1.0 or font_size <= 9.0)
        ):
            result[element_id] = ElementEditorialRole(
                element_id,
                ROLE_SUBTITLE,
                0.82,
                "Texte court immédiatement placé sous le titre principal.",
            )
            continue

        if words <= 12 and (
            font_size >= max(11.0, median_size + 1.0)
            or (_is_bold(item) and font_size >= median_size)
        ):
            result[element_id] = ElementEditorialRole(
                element_id,
                ROLE_SECTION_HEADING,
                0.91,
                "Texte court typographiquement renforcé au sein de la page.",
            )
            continue

        if font_size and font_size <= 8.5:
            result[element_id] = ElementEditorialRole(
                element_id,
                ROLE_NOTE,
                0.78,
                "Texte de petit corps traité comme information secondaire.",
            )
            continue

        result[element_id] = ElementEditorialRole(
            element_id,
            ROLE_BODY,
            0.88,
            "Bloc textuel courant ne présentant pas de signal plus spécifique.",
        )

    return result


def page_element_role_dict(book: BookV4, page_id: str) -> dict[str, dict[str, Any]]:
    """Version sérialisable utile à l'interface et aux futurs contrôles IA."""
    return {
        element_id: {
            "role": value.role,
            "confidence": value.confidence,
            "reason": value.reason,
        }
        for element_id, value in page_element_roles(book, page_id).items()
    }
