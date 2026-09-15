from __future__ import annotations

"""Relations logiques texte / image détectées dans la Composition V4.

Le PDF donne des coordonnées. TomeLinea a besoin d'une relation éditoriale pour
pouvoir recomposer un livre : une image insérée dans un texte doit suivre le
paragraphe / titre auquel elle appartient plutôt que rester attachée à une
ancienne coordonnée de page.

Cette couche ne déplace rien. Elle enregistre seulement des ancres proposées,
déterministes et explicables, que le moteur Format peut ensuite utiliser.
"""

from dataclasses import dataclass
from typing import Any

from src.v4.composition import IMAGE, TEXT
from src.v4.domain import BookV4, PageV4
from src.v4.page_element_roles import (
    ROLE_BODY,
    ROLE_PAGE_TITLE,
    ROLE_SECTION_HEADING,
    ROLE_SUBTITLE,
    page_element_roles,
)

ANCHOR_TYPE = "content_anchor_type"
ANCHOR_ELEMENT_ID = "content_anchor_element_id"
ANCHOR_RELATION = "content_anchor_relation"
ANCHOR_GAP_MM = "content_anchor_gap_mm"
ANCHOR_OFFSET_RATIO = "content_anchor_offset_ratio"
ANCHOR_CONFIDENCE = "content_anchor_confidence"
ANCHOR_REASON = "content_anchor_reason"
ANCHOR_ORIGIN = "content_anchor_origin"

_ANCHORABLE_ROLES = {
    ROLE_BODY,
    ROLE_PAGE_TITLE,
    ROLE_SECTION_HEADING,
    ROLE_SUBTITLE,
}


@dataclass(frozen=True, slots=True)
class ContentAnchorResult:
    pages_analyzed: int
    images_seen: int
    images_anchored: int


def _kind(element: Any) -> str:
    return str(element.get("kind", "") or "").strip().lower() if isinstance(element, dict) else ""


def _metadata(element: dict[str, Any]) -> dict[str, Any]:
    value = element.get("metadata")
    if isinstance(value, dict):
        return value
    value = {}
    element["metadata"] = value
    return value


def _geometry(element: dict[str, Any]) -> tuple[float, float, float, float] | None:
    value = element.get("geometry")
    if not isinstance(value, dict):
        return None
    try:
        x = float(value.get("x_mm", 0.0) or 0.0)
        y = float(value.get("y_mm", 0.0) or 0.0)
        w = float(value.get("width_mm", 0.0) or 0.0)
        h = float(value.get("height_mm", 0.0) or 0.0)
    except (TypeError, ValueError):
        return None
    if w <= 0.0 or h <= 0.0:
        return None
    return x, y, w, h


def _overlap_1d(a0: float, a1: float, b0: float, b1: float) -> float:
    return max(0.0, min(a1, b1) - max(a0, b0))


def _candidate_score(
    image_geom: tuple[float, float, float, float],
    text_geom: tuple[float, float, float, float],
    role: str,
) -> tuple[float, str, float, float, str] | None:
    ix, iy, iw, ih = image_geom
    tx, ty, tw, th = text_geom
    ib = iy + ih
    ir = ix + iw
    tb = ty + th
    tr = tx + tw

    overlap_x = _overlap_1d(ix, ir, tx, tr) / max(1e-6, min(iw, tw))
    overlap_y = _overlap_1d(iy, ib, ty, tb) / max(1e-6, min(ih, th))
    role_bonus = 0.10 if role == ROLE_BODY else 0.05

    # Texte au-dessus : cas le plus courant d'une image insérée après un paragraphe.
    if tb <= iy + 0.8:
        gap = max(0.0, iy - tb)
        if gap <= 45.0 and overlap_x >= 0.12:
            proximity = max(0.0, 1.0 - gap / 45.0)
            score = 0.45 * proximity + 0.45 * min(1.0, overlap_x) + role_bonus
            offset = (ix - tx) / max(1.0, tw)
            return score, "after", gap, offset, "Image située après un bloc textuel proche et aligné."

    # Texte au-dessous : illustration placée avant son paragraphe / titre associé.
    if ib <= ty + 0.8:
        gap = max(0.0, ty - ib)
        if gap <= 32.0 and overlap_x >= 0.12:
            proximity = max(0.0, 1.0 - gap / 32.0)
            score = 0.38 * proximity + 0.47 * min(1.0, overlap_x) + role_bonus
            offset = (ix - tx) / max(1.0, tw)
            return score, "before", gap, offset, "Image située avant un bloc textuel proche et aligné."

    # Mise en page latérale : on mémorise la relation mais le moteur Format peut
    # choisir de la simplifier s'il n'y a plus assez de largeur.
    if overlap_y >= 0.30:
        if tr <= ix + 1.0:
            gap = max(0.0, ix - tr)
            if gap <= 25.0:
                score = 0.36 * (1.0 - gap / 25.0) + 0.48 * min(1.0, overlap_y) + role_bonus
                offset = (iy - ty) / max(1.0, th)
                return score, "right_of", gap, offset, "Image placée à droite d'un bloc textuel proche."
        if ir <= tx + 1.0:
            gap = max(0.0, tx - ir)
            if gap <= 25.0:
                score = 0.36 * (1.0 - gap / 25.0) + 0.48 * min(1.0, overlap_y) + role_bonus
                offset = (iy - ty) / max(1.0, th)
                return score, "left_of", gap, offset, "Image placée à gauche d'un bloc textuel proche."

    return None


def infer_page_content_anchors(
    book: BookV4,
    page_id: str,
    *,
    overwrite: bool = False,
) -> tuple[int, int]:
    """Déduit les ancres des images d'une page sans déplacer le contenu."""

    page = book.pages.get(page_id)
    if page is None:
        raise KeyError(page_id)

    try:
        roles = page_element_roles(book, page_id)
    except Exception:
        roles = {}

    text_candidates: list[tuple[dict[str, Any], str, tuple[float, float, float, float]]] = []
    for element in page.content:
        if not isinstance(element, dict) or _kind(element) != TEXT:
            continue
        geom = _geometry(element)
        if geom is None:
            continue
        role_obj = roles.get(str(element.get("id", "") or ""))
        role = getattr(role_obj, "role", "") if role_obj is not None else ""
        if role not in _ANCHORABLE_ROLES:
            continue
        text_candidates.append((element, role, geom))

    seen = 0
    anchored = 0
    for image in page.content:
        if not isinstance(image, dict) or _kind(image) != IMAGE:
            continue
        seen += 1
        meta = _metadata(image)
        # Une correction utilisateur doit toujours gagner sur l'analyse automatique.
        if str(meta.get(ANCHOR_ORIGIN, "") or "") == "user" and not overwrite:
            if meta.get(ANCHOR_ELEMENT_ID):
                anchored += 1
            continue
        if meta.get(ANCHOR_ELEMENT_ID) and not overwrite:
            anchored += 1
            continue

        image_geom = _geometry(image)
        if image_geom is None:
            continue

        best: tuple[float, dict[str, Any], str, float, float, str] | None = None
        for text, role, text_geom in text_candidates:
            candidate = _candidate_score(image_geom, text_geom, role)
            if candidate is None:
                continue
            score, relation, gap, offset, reason = candidate
            if best is None or score > best[0]:
                best = (score, text, relation, gap, offset, reason)

        if best is None or best[0] < 0.42:
            # Sans relation suffisamment sûre, l'image reste ancrée à la page.
            meta[ANCHOR_TYPE] = "page"
            meta[ANCHOR_ORIGIN] = "analysis"
            meta[ANCHOR_CONFIDENCE] = 0.0
            meta[ANCHOR_REASON] = "Aucun bloc textuel suffisamment proche pour proposer une ancre fiable."
            meta.pop(ANCHOR_ELEMENT_ID, None)
            meta.pop(ANCHOR_RELATION, None)
            meta.pop(ANCHOR_GAP_MM, None)
            meta.pop(ANCHOR_OFFSET_RATIO, None)
            continue

        score, text, relation, gap, offset, reason = best
        text_id = str(text.get("id", "") or "")
        if not text_id:
            continue
        meta[ANCHOR_TYPE] = "text"
        meta[ANCHOR_ELEMENT_ID] = text_id
        meta[ANCHOR_RELATION] = relation
        meta[ANCHOR_GAP_MM] = round(float(gap), 4)
        meta[ANCHOR_OFFSET_RATIO] = round(float(offset), 6)
        meta[ANCHOR_CONFIDENCE] = round(min(0.99, max(0.0, float(score))), 4)
        meta[ANCHOR_REASON] = reason
        meta[ANCHOR_ORIGIN] = "analysis"
        anchored += 1

    page.metadata["content_anchor_analysis_done"] = True
    page.metadata["content_anchor_image_count"] = seen
    page.metadata["content_anchor_assigned_count"] = anchored
    return seen, anchored


def infer_book_content_anchors(book: BookV4, *, overwrite: bool = False) -> ContentAnchorResult:
    pages = images = anchored = 0
    for page_id in book.page_order:
        page = book.pages.get(page_id)
        if page is None:
            continue
        pages += 1
        seen, assigned = infer_page_content_anchors(book, page_id, overwrite=overwrite)
        images += seen
        anchored += assigned

    book.metadata["content_anchor_analysis_version"] = 1
    book.metadata["content_anchor_images_seen"] = images
    book.metadata["content_anchor_images_assigned"] = anchored
    return ContentAnchorResult(pages, images, anchored)
