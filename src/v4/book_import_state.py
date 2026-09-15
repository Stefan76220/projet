from __future__ import annotations

"""TomeLinea V4 — état du livre après première analyse.

Cette couche décrit le livre tel qu'il a été fourni avant toute décision
éditoriale supplémentaire. Elle ne remplace ni l'Analyse ni le Livre.

Principes :
- le format de Source est factuel ;
- les marges ODT sont déclarées par la Source ;
- les marges PDF sont seulement estimées à partir des placements récurrents ;
- les exceptions sont signalées, jamais corrigées automatiquement ;
- une modification explicite du format/marges devient une décision du Livre.
"""

from dataclasses import dataclass
from pathlib import Path
from statistics import median
from typing import Any, Iterable

from src.v4.domain import BookFormat, BookV4
from src.v4.project import ProjectV4


FACT = "fact."


# Le format de la Source n'est volontairement pas limité au catalogue.
# Un PDF existant peut avoir une géométrie inhabituelle : TomeLinea la conserve
# factuellement puis propose une conversion vers un format cible standard.


@dataclass(frozen=True, slots=True)
class BookImportState:
    source_file_type: str
    source_page_count: int
    book_page_count: int
    part_count: int

    source_width_mm: float | None
    source_height_mm: float | None
    format_exception_pages: tuple[int, ...]

    margin_top_mm: float | None
    margin_bottom_mm: float | None
    margin_inside_mm: float | None
    margin_outside_mm: float | None
    margins_origin: str
    margin_exception_pages: tuple[int, ...]

    bleed_top_mm: float | None
    bleed_right_mm: float | None
    bleed_bottom_mm: float | None
    bleed_left_mm: float | None
    bleed_origin: str

    @property
    def exception_pages(self) -> tuple[int, ...]:
        return tuple(sorted(set(self.format_exception_pages) | set(self.margin_exception_pages)))


def _primary_version(project: ProjectV4):
    element_id = str(project.metadata.get("primary_source_element_id", "") or "")
    element = project.source.elements.get(element_id) if element_id else None
    if element is None and project.source.elements:
        element = next(iter(project.source.elements.values()))
    if element is None:
        return None
    return element.active_version


def _effective(project: ProjectV4, target_id: str, key: str, default=None):
    value = project.analysis.effective_value(
        target_type="source_page" if ":page:" in target_id else "source_version",
        target_id=target_id,
        key=(key if key.startswith(FACT) else FACT + key),
    )
    return default if value is None else value


def _mode_pair(values: Iterable[tuple[float, float]]) -> tuple[float | None, float | None, tuple[int, ...]]:
    rounded: list[tuple[float, float]] = [
        (round(float(w), 1), round(float(h), 1)) for w, h in values if float(w) > 0 and float(h) > 0
    ]
    if not rounded:
        return None, None, ()
    counts: dict[tuple[float, float], int] = {}
    for pair in rounded:
        counts[pair] = counts.get(pair, 0) + 1
    dominant = max(counts.items(), key=lambda item: (item[1], -rounded.index(item[0])))[0]
    exceptions = tuple(index + 1 for index, pair in enumerate(rounded) if pair != dominant)
    return float(dominant[0]), float(dominant[1]), exceptions


def _percentile_low(values: list[float], fraction: float = 0.22) -> float | None:
    values = sorted(float(v) for v in values if v >= 0)
    if not values:
        return None
    index = max(0, min(len(values) - 1, int(round((len(values) - 1) * fraction))))
    return float(values[index])


def _pdf_margin_estimate(project: ProjectV4, version_id: str, page_count: int, width: float, height: float):
    lefts: list[float] = []
    rights: list[float] = []
    tops: list[float] = []
    bottoms: list[float] = []
    page_bounds: dict[int, tuple[float, float, float, float]] = {}

    for number in range(1, page_count + 1):
        target = f"{version_id}:page:{number}"
        blocks = _effective(project, target, "layout.text_blocks", [])
        if not isinstance(blocks, list) or not blocks:
            continue
        boxes = [item.get("bbox_norm") for item in blocks if isinstance(item, dict) and item.get("bbox_norm")]
        if not boxes:
            continue
        x0 = min(float(box[0]) for box in boxes) * width
        y0 = min(float(box[1]) for box in boxes) * height
        right = (1.0 - max(float(box[2]) for box in boxes)) * width
        bottom = (1.0 - max(float(box[3]) for box in boxes)) * height
        page_bounds[number] = (x0, y0, right, bottom)
        lefts.append(x0); tops.append(y0); rights.append(right); bottoms.append(bottom)

    left = _percentile_low(lefts)
    right = _percentile_low(rights)
    top = _percentile_low(tops)
    bottom = _percentile_low(bottoms)

    # Un document court ne remplit pas nécessairement le bas de page. Lorsque
    # trois côtés donnent une valeur récurrente voisine, on privilégie cette
    # cohérence plutôt qu'une fausse grande « marge basse ».
    trusted = [v for v in (left, right, top) if v is not None and v <= min(width, height) * 0.20]
    if trusted:
        typical = median(trusted)
        if bottom is None or bottom > typical * 2.5:
            bottom = typical

    def clean(value: float | None) -> float | None:
        if value is None:
            return None
        return round(max(0.0, value), 1)

    left, right, top, bottom = map(clean, (left, right, top, bottom))

    # Recto = page impaire : intérieur à gauche. Verso = page paire : intérieur à droite.
    inside_candidates: list[float] = []
    outside_candidates: list[float] = []
    for number, (lft, _top, rgt, _bottom) in page_bounds.items():
        if number % 2:
            inside_candidates.append(lft); outside_candidates.append(rgt)
        else:
            inside_candidates.append(rgt); outside_candidates.append(lft)
    inside = clean(_percentile_low(inside_candidates)) or left
    outside = clean(_percentile_low(outside_candidates)) or right

    # Une exception de marge est un contenu réel qui dépasse nettement la zone
    # générale estimée. On regarde tous les objets, pas seulement le texte.
    exceptions: list[int] = []
    mt = float(top or 0.0); mb = float(bottom or 0.0)
    for number in range(1, page_count + 1):
        target = f"{version_id}:page:{number}"
        boxes: list[list[float]] = []
        for key in ("layout.text_blocks", "image.placements", "layout.tables"):
            items = _effective(project, target, key, [])
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict) and isinstance(item.get("bbox_norm"), (list, tuple)):
                        box = item["bbox_norm"]
                        if len(box) >= 4:
                            boxes.append([float(v) for v in box[:4]])
        if not boxes:
            continue
        lft = min(box[0] for box in boxes) * width
        tp = min(box[1] for box in boxes) * height
        rgt = (1 - max(box[2] for box in boxes)) * width
        btm = (1 - max(box[3] for box in boxes)) * height
        expected_left = float(inside if number % 2 else outside or 0.0)
        expected_right = float(outside if number % 2 else inside or 0.0)
        tolerance = 2.0
        if (
            lft < expected_left - tolerance
            or rgt < expected_right - tolerance
            or tp < mt - tolerance
            or btm < mb - tolerance
        ):
            exceptions.append(number)

    return top, bottom, inside, outside, tuple(exceptions)


def _pdf_bleed_from_file(path: str, width_mm: float | None, height_mm: float | None):
    try:
        import pymupdf
        source = Path(path)
        if not source.is_file():
            return (None, None, None, None, "indisponible")
        doc = pymupdf.open(source)
        try:
            if doc.page_count < 1:
                return (None, None, None, None, "indisponible")
            page = doc[0]
            trim = page.trimbox
            bleed = page.bleedbox
            factor = 25.4 / 72.0
            top = max(0.0, (float(trim.y0) - float(bleed.y0)) * factor)
            left = max(0.0, (float(trim.x0) - float(bleed.x0)) * factor)
            right = max(0.0, (float(bleed.x1) - float(trim.x1)) * factor)
            bottom = max(0.0, (float(bleed.y1) - float(trim.y1)) * factor)
            return tuple(round(v, 1) for v in (top, right, bottom, left)) + ("déclaré dans le PDF",)
        finally:
            doc.close()
    except Exception:
        return (None, None, None, None, "indisponible")


def detect_book_import_state(project: ProjectV4) -> BookImportState:
    version = _primary_version(project)
    book = project.book
    if version is None:
        return BookImportState("", 0, len(book.page_order) if book else 0, len(book.part_order) if book else 0,
                               None, None, (), None, None, None, None, "indisponible", (),
                               None, None, None, None, "indisponible")

    page_count = int(_effective(project, version.id, "document.page_count", 0) or 0)
    sizes: list[tuple[float, float]] = []
    for number in range(1, page_count + 1):
        target = f"{version.id}:page:{number}"
        w = _effective(project, target, "page.width_mm", None)
        h = _effective(project, target, "page.height_mm", None)
        if w is not None and h is not None:
            sizes.append((float(w), float(h)))

    width, height, format_exceptions = _mode_pair(sizes)

    mt = mb = mi = mo = None
    margin_exceptions: tuple[int, ...] = ()
    margins_origin = "indisponible"

    file_type = str(version.file_type or "").lower()
    if file_type == "odt":
        layout = _effective(project, version.id, "document.page_layout", {})
        if isinstance(layout, dict):
            width = float(layout.get("width_mm", width)) if layout.get("width_mm") is not None else width
            height = float(layout.get("height_mm", height)) if layout.get("height_mm") is not None else height
            mt = layout.get("margin_top_mm")
            mb = layout.get("margin_bottom_mm")
            left = layout.get("margin_left_mm")
            right = layout.get("margin_right_mm")
            mi = left; mo = right
            for name in ("mt", "mb", "mi", "mo"):
                pass
            mt = round(float(mt), 1) if mt is not None else None
            mb = round(float(mb), 1) if mb is not None else None
            mi = round(float(mi), 1) if mi is not None else None
            mo = round(float(mo), 1) if mo is not None else None
            margins_origin = "déclarées dans la Source"
    elif file_type == "pdf" and width is not None and height is not None:
        mt, mb, mi, mo, margin_exceptions = _pdf_margin_estimate(project, version.id, page_count, width, height)
        margins_origin = "estimées à partir de la Source"

    bt = br = bb = bl = None
    bleed_origin = "indisponible"
    if file_type == "pdf":
        bt, br, bb, bl, bleed_origin = _pdf_bleed_from_file(version.original_path, width, height)
    elif file_type == "odt":
        bt = br = bb = bl = 0.0
        bleed_origin = "aucun fond perdu déclaré"

    return BookImportState(
        source_file_type=file_type,
        source_page_count=page_count,
        book_page_count=len(book.page_order) if book else 0,
        part_count=len(book.part_order) if book else 0,
        source_width_mm=width,
        source_height_mm=height,
        format_exception_pages=format_exceptions,
        margin_top_mm=mt,
        margin_bottom_mm=mb,
        margin_inside_mm=mi,
        margin_outside_mm=mo,
        margins_origin=margins_origin,
        margin_exception_pages=margin_exceptions,
        bleed_top_mm=bt,
        bleed_right_mm=br,
        bleed_bottom_mm=bb,
        bleed_left_mm=bl,
        bleed_origin=bleed_origin,
    )


def source_format_for_new_book(project: ProjectV4) -> BookFormat | None:
    state = detect_book_import_state(project)
    if state.source_width_mm is None or state.source_height_mm is None:
        return None
    margin_values = (state.margin_top_mm, state.margin_bottom_mm, state.margin_inside_mm, state.margin_outside_mm)
    fallback = 15.0
    mt, mb, mi, mo = [fallback if value is None else float(value) for value in margin_values]
    # Le format Source reste factuel, même s'il n'appartient pas encore au
    # catalogue TomeLinea. L'utilisateur le normalise ensuite dans Format.
    width_mm = float(state.source_width_mm)
    height_mm = float(state.source_height_mm)
    return BookFormat(
        width_mm=width_mm,
        height_mm=height_mm,
        margin_top_mm=mt,
        margin_bottom_mm=mb,
        margin_inside_mm=mi,
        margin_outside_mm=mo,
        bleed_top_mm=float(state.bleed_top_mm or 0.0),
        bleed_right_mm=float(state.bleed_right_mm or 0.0),
        bleed_bottom_mm=float(state.bleed_bottom_mm or 0.0),
        bleed_left_mm=float(state.bleed_left_mm or 0.0),
    )


def apply_detected_format_to_new_book(project: ProjectV4, book: BookV4) -> None:
    detected = source_format_for_new_book(project)
    if detected is None:
        return
    book.format = detected
    book.metadata.setdefault("composition_extent", "margins")
    book.metadata["initial_format_origin"] = "source_analysis"
    book.history.append({"action": "format_initial_depuis_source", "width_mm": detected.width_mm, "height_mm": detected.height_mm})
    book.validate()


def apply_book_layout_settings(
    project: ProjectV4,
    *,
    width_mm: float,
    height_mm: float,
    margin_top_mm: float,
    margin_bottom_mm: float,
    margin_inside_mm: float,
    margin_outside_mm: float,
    bleed_mm: float | None = None,
    composition_extent: str = "margins",
):
    """Applique le format au Livre et lance la recomposition adaptee.

    FORMAT_07 : le Roman est repaginé, le texte conserve son corps et les
    images sont redimensionnées proportionnellement. Les relations texte/image
    issues de l’analyse servent d’ancrages de recomposition. Le point d'entrée
    n'accepte que les formats éditoriaux du catalogue TomeLinea.
    """
    from copy import deepcopy

    from src.v4.format_reflow import repaginate_book_for_format
    from src.v4.format_content_adapter import (
        adapt_book_content_for_format,
        restore_format_content_continuations,
    )

    if project.book is None:
        raise ValueError("Aucun Livre à modifier.")

    book = project.book
    old_format = deepcopy(book.format)
    old_w = float(old_format.width_mm)
    old_h = float(old_format.height_mm)

    # Le premier format réellement affiché sert de référence géométrique aux
    # éléments issus de la Source. Cela permet notamment de revenir au format
    # d'origine sans accumuler les transformations successives.
    book.metadata.setdefault(
        "format_content_reference_format",
        {
            "width_mm": float(old_format.width_mm),
            "height_mm": float(old_format.height_mm),
            "margin_top_mm": float(old_format.margin_top_mm),
            "margin_bottom_mm": float(old_format.margin_bottom_mm),
            "margin_inside_mm": float(old_format.margin_inside_mm),
            "margin_outside_mm": float(old_format.margin_outside_mm),
        },
    )

    from src.v4.format_catalog import require_standard_format

    standard_format = require_standard_format(width_mm, height_mm)

    new_format = BookFormat(
        width_mm=float(width_mm),
        height_mm=float(height_mm),
        margin_top_mm=float(margin_top_mm),
        margin_bottom_mm=float(margin_bottom_mm),
        margin_inside_mm=float(margin_inside_mm),
        margin_outside_mm=float(margin_outside_mm),
        bleed_top_mm=float(old_format.bleed_top_mm if bleed_mm is None else bleed_mm),
        bleed_right_mm=float(old_format.bleed_right_mm if bleed_mm is None else bleed_mm),
        bleed_bottom_mm=float(old_format.bleed_bottom_mm if bleed_mm is None else bleed_mm),
        bleed_left_mm=float(old_format.bleed_left_mm if bleed_mm is None else bleed_mm),
    )
    new_format.validate()

    if composition_extent not in {"margins", "page", "bleed"}:
        raise ValueError("Étendue de composition inconnue.")

    # Un format precedent a pu creer des pages de continuation pour un texte
    # mixte. On reunit d'abord ces morceaux afin que chaque nouveau calcul
    # reparte du contenu complet, sans perte cumulative.
    restored_continuations = restore_format_content_continuations(book)

    reflow_result = repaginate_book_for_format(
        book,
        old_format=old_format,
        new_format=new_format,
    )

    # Toutes les pages qui ne relèvent pas de la repagination continue sont
    # réellement adaptées : texte recomposé, images recadrées et débordement
    # textuel envoyé vers une page de continuation plutôt que tronqué.
    content_result = adapt_book_content_for_format(
        book,
        old_format=old_format,
        new_format=new_format,
    )

    book.format = new_format
    book.metadata["format_catalog_key"] = standard_format.key
    book.metadata["format_catalog_label"] = standard_format.label
    book.metadata["format_platforms"] = list(standard_format.platforms)
    book.metadata["composition_extent"] = composition_extent
    book.metadata["format_user_modified"] = True
    book.metadata["layout_reflow_check_required"] = True
    book.metadata["format_reflow_applied"] = bool(reflow_result.reflowed_pages)
    book.metadata["format_reflow_last_result"] = {
        "old_page_count": reflow_result.old_page_count,
        "new_page_count_before_structure_sync": reflow_result.new_page_count,
        "changed_groups": reflow_result.changed_groups,
        "created_pages": reflow_result.created_pages,
        "removed_pages": reflow_result.removed_pages,
        "reflowed_pages": reflow_result.reflowed_pages,
        "restored_continuations": restored_continuations,
        "content_adapted_pages": content_result.adapted_pages,
        "content_adapted_texts": content_result.adapted_texts,
        "content_adapted_images": content_result.adapted_images,
        "content_continuation_pages": content_result.continuation_pages,
        "content_overflow_blocks": content_result.overflow_blocks,
        "fixed_layout_pages": content_result.fixed_layout_pages,
    }
    book.history.append({
        "action": "reglages_generaux_livre_modifies",
        "width_mm": float(width_mm),
        "height_mm": float(height_mm),
        "margin_top_mm": float(margin_top_mm),
        "margin_bottom_mm": float(margin_bottom_mm),
        "margin_inside_mm": float(margin_inside_mm),
        "margin_outside_mm": float(margin_outside_mm),
        "composition_extent": composition_extent,
        "page_count_before": reflow_result.old_page_count,
        "page_count_after_reflow": reflow_result.new_page_count,
    })
    project.metadata["book_import_state_reviewed"] = True
    project.touch()
    project.validate()
    return reflow_result
