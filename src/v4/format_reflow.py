from __future__ import annotations

"""Recomposition du flux Roman lors d'un changement de format.

FORMAT_05 ne répartit plus un texte complet par simple quantité de mots. Le
moteur conserve les blocs et leurs styles : titres / sous-titres de la première
page, en-tête courant éventuel et corps de texte sont traités séparément. Le
corps est recomposé à la largeur utile et peut changer réellement de page.
"""

from copy import deepcopy
from dataclasses import dataclass
import math
from typing import Any
from uuid import uuid4

from src.v4.composition import PAGE, TEXT, new_element
from src.v4.domain import BookFormat, BookKind, BookV4, PageOrigin, PageV4
from src.v4.format_text_layout import measure_text_layout, normalized_text, remember_source_metrics
from src.v4.page_element_roles import (
    ROLE_BODY,
    ROLE_PAGE_TITLE,
    ROLE_SECTION_HEADING,
    ROLE_SUBTITLE,
    page_element_roles,
)
from src.v4.structure_auto import is_structural_auto_page
from src.v4.structure_covers import is_cover_face
from src.v4.structure_parity import physical_side


_GROUP_ID = "format_reflow_group_id"
_CAPACITY_UNITS = "format_reflow_capacity_units"
_GENERATED = "format_reflow_generated"
_SOURCE_PAGES = "format_reflow_source_pages"
_SOURCE_PAGE_IDS = "format_reflow_source_page_ids"
_REFLOW_VERSION = "format_reflow_version"
_FLOW_ROLE = "format_flow_role"
_ORIGIN_BLOCK = "format_origin_block_id"


@dataclass(frozen=True, slots=True)
class FormatReflowResult:
    kind: str
    old_page_count: int
    new_page_count: int
    changed_groups: int
    created_pages: int
    removed_pages: int
    reflowed_pages: int

    @property
    def page_count_changed(self) -> bool:
        return self.old_page_count != self.new_page_count


def _usable_area(fmt: BookFormat) -> float:
    width = max(1.0, float(fmt.width_mm) - float(fmt.margin_inside_mm) - float(fmt.margin_outside_mm))
    height = max(1.0, float(fmt.height_mm) - float(fmt.margin_top_mm) - float(fmt.margin_bottom_mm))
    return width * height


def _element_kind(element: Any) -> str:
    if not isinstance(element, dict):
        return ""
    return str(element.get("kind", "") or "").strip().lower()


def _has_local_structure_rule(page: PageV4) -> bool:
    raw = page.metadata.get("structure_rule_overrides")
    return bool(isinstance(raw, dict) and raw)


def _reflowable_text_page(page: PageV4) -> bool:
    if is_cover_face(page) or is_structural_auto_page(page):
        return False
    if page.spread_id or page.auto_before or page.auto_after:
        return False
    if page.recto_verso:
        return False
    if _has_local_structure_rule(page):
        return False
    if page.modifications:
        return False
    if str(page.page_type or "").strip().lower() != "page texte":
        return False
    if not page.content:
        return False
    return all(_element_kind(element) == TEXT for element in page.content)


def _group_id(page: PageV4) -> str | None:
    value = str(page.metadata.get(_GROUP_ID, "") or "").strip()
    return value or None


def _collect_groups(book: BookV4) -> list[list[str]]:
    groups: list[list[str]] = []
    current: list[str] = []
    current_part: str | None = None
    current_group: str | None = None

    def flush() -> None:
        nonlocal current, current_part, current_group
        if current:
            groups.append(current)
        current = []
        current_part = None
        current_group = None

    for page_id in book.page_order:
        page = book.pages[page_id]
        if not _reflowable_text_page(page):
            flush()
            continue
        page_group = _group_id(page)
        if current:
            if page.part_id != current_part:
                flush()
            elif current_group is not None or page_group is not None:
                if current_group != page_group:
                    flush()
        if not current:
            current_part = page.part_id
            current_group = page_group
        current.append(page_id)
    flush()
    return groups


def _sorted_text_elements(page: PageV4) -> list[dict[str, Any]]:
    values = [element for element in page.content if isinstance(element, dict) and _element_kind(element) == TEXT]

    def key(element: dict[str, Any]) -> tuple[float, float]:
        geometry = element.get("geometry", {})
        if not isinstance(geometry, dict):
            return (0.0, 0.0)
        try:
            return (
                float(geometry.get("y_mm", 0.0) or 0.0),
                float(geometry.get("x_mm", 0.0) or 0.0),
            )
        except (TypeError, ValueError):
            return (0.0, 0.0)

    return sorted(values, key=key)


def _source_pages(page: PageV4) -> list[int]:
    values: list[int] = []
    if page.source is not None and page.source.source_page is not None:
        values.append(int(page.source.source_page))
    raw = page.metadata.get(_SOURCE_PAGES, ())
    if isinstance(raw, (list, tuple)):
        for value in raw:
            try:
                values.append(int(value))
            except (TypeError, ValueError):
                pass
    return values


def _roles_for_page(book: BookV4, page: PageV4) -> dict[str, str]:
    result: dict[str, str] = {}
    generated_roles = False
    for element in page.content:
        if not isinstance(element, dict):
            continue
        metadata = element.get("metadata", {})
        if isinstance(metadata, dict) and metadata.get(_FLOW_ROLE):
            result[str(element.get("id", ""))] = str(metadata.get(_FLOW_ROLE))
            generated_roles = True
    if generated_roles:
        return result
    try:
        return {
            element_id: value.role
            for element_id, value in page_element_roles(book, page.id).items()
        }
    except Exception:
        return result


def _font_size(element: dict[str, Any]) -> float:
    payload = element.get("payload", {})
    spans = payload.get("spans", []) if isinstance(payload, dict) else []
    if isinstance(spans, list):
        for span in spans:
            if not isinstance(span, dict):
                continue
            try:
                value = float(span.get("size", 0.0) or 0.0)
            except (TypeError, ValueError):
                value = 0.0
            if value > 0:
                return value
    return 10.0


def _collect_material(book: BookV4, group: list[str]) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    dict[str, Any] | None,
    list[int],
    list[str],
]:
    """Retourne corps, préfixe de première page et en-tête courant."""
    body_by_origin: dict[str, dict[str, Any]] = {}
    body_order: list[str] = []
    prefix: list[dict[str, Any]] = []
    running_header: dict[str, Any] | None = None
    source_pages: list[int] = []
    source_page_ids: list[str] = []

    for page_index, page_id in enumerate(group):
        page = book.pages[page_id]
        source_page_ids.extend(page.metadata.get(_SOURCE_PAGE_IDS, []) if isinstance(page.metadata.get(_SOURCE_PAGE_IDS), list) else [])
        source_page_ids.append(page_id)
        source_pages.extend(_source_pages(page))
        roles = _roles_for_page(book, page)
        elements = _sorted_text_elements(page)

        for element in elements:
            metadata = element.get("metadata", {})
            role = roles.get(str(element.get("id", "")), "")
            if isinstance(metadata, dict) and metadata.get(_FLOW_ROLE):
                role = str(metadata.get(_FLOW_ROLE))

            if role == ROLE_BODY:
                origin = str(
                    (metadata.get(_ORIGIN_BLOCK) if isinstance(metadata, dict) else None)
                    or element.get("id", "")
                    or uuid4()
                )
                if origin not in body_by_origin:
                    clone = deepcopy(element)
                    if not isinstance(clone.get("metadata"), dict):
                        clone["metadata"] = {}
                    clone["metadata"][_ORIGIN_BLOCK] = origin
                    body_by_origin[origin] = clone
                    body_order.append(origin)
                else:
                    existing = body_by_origin[origin]
                    existing_payload = existing.get("payload", {})
                    incoming_payload = element.get("payload", {})
                    if isinstance(existing_payload, dict) and isinstance(incoming_payload, dict):
                        current = normalized_text(existing)
                        incoming = normalized_text(element)
                        existing_payload["text"] = " ".join(value for value in (current, incoming) if value)
                continue

            # Ne garder sur la première page que la titraille supérieure, jamais
            # les folios / notes de bas de page.
            if page_index == 0 and role in {ROLE_PAGE_TITLE, ROLE_SUBTITLE, ROLE_SECTION_HEADING}:
                clone = deepcopy(element)
                if not isinstance(clone.get("metadata"), dict):
                    clone["metadata"] = {}
                clone["metadata"][_FLOW_ROLE] = role
                prefix.append(clone)
                continue

            # Un petit titre supérieur des pages suivantes sert d'en-tête courant.
            if page_index > 0 and role == ROLE_PAGE_TITLE and running_header is None:
                geometry = element.get("geometry", {})
                try:
                    y = float(geometry.get("y_mm", 9999.0) or 9999.0) if isinstance(geometry, dict) else 9999.0
                except (TypeError, ValueError):
                    y = 9999.0
                text_words = len(normalized_text(element).split())
                try:
                    source_height = float(geometry.get("height_mm", 9999.0) or 9999.0) if isinstance(geometry, dict) else 9999.0
                except (TypeError, ValueError):
                    source_height = 9999.0
                if (
                    y <= float(book.format.height_mm) * 0.15
                    and _font_size(element) <= 11.0
                    and text_words <= 12
                    and source_height <= 15.0
                ):
                    running_header = deepcopy(element)
                    if not isinstance(running_header.get("metadata"), dict):
                        running_header["metadata"] = {}
                    running_header["metadata"][_FLOW_ROLE] = "running_header"

    # Si l'analyse de rôle d'un ancien rendu généré n'a rien retrouvé, considérer
    # le texte non marqué comme corps plutôt que de le perdre.
    if not body_order:
        # Analyse éditoriale insuffisante : mieux vaut traiter tout le groupe
        # comme un flux de corps que dupliquer un faux titre gigantesque.
        prefix = []
        running_header = None
        for page_id in group:
            for element in _sorted_text_elements(book.pages[page_id]):
                metadata = element.get("metadata", {})
                role = str(metadata.get(_FLOW_ROLE, "")) if isinstance(metadata, dict) else ""
                if role in {ROLE_PAGE_TITLE, ROLE_SUBTITLE, ROLE_SECTION_HEADING, "running_header"}:
                    continue
                origin = str((metadata.get(_ORIGIN_BLOCK) if isinstance(metadata, dict) else None) or element.get("id", "") or uuid4())
                clone = deepcopy(element)
                clone.setdefault("metadata", {})[_ORIGIN_BLOCK] = origin
                body_by_origin[origin] = clone
                body_order.append(origin)

    body = [body_by_origin[origin] for origin in body_order]
    return (
        body,
        prefix,
        running_header,
        list(dict.fromkeys(source_pages)),
        list(dict.fromkeys(source_page_ids)),
    )


def _target_count(group: list[str], book: BookV4, old_fmt: BookFormat, new_fmt: BookFormat) -> tuple[int, str, float]:
    first = book.pages[group[0]]
    existing_group_id = _group_id(first)
    group_id = existing_group_id or str(uuid4())
    raw_units = first.metadata.get(_CAPACITY_UNITS) if existing_group_id else None
    try:
        capacity_units = float(raw_units)
    except (TypeError, ValueError):
        capacity_units = float(len(group)) * _usable_area(old_fmt)
    new_area = _usable_area(new_fmt)
    count = max(1, int(math.floor(capacity_units / new_area + 0.5)))
    return count, group_id, capacity_units


def _map_template_geometry(element: dict[str, Any], old_fmt: BookFormat, new_fmt: BookFormat) -> dict[str, float]:
    geometry = element.get("geometry", {})
    if not isinstance(geometry, dict):
        geometry = {}
    try:
        x = float(geometry.get("x_mm", 0.0) or 0.0)
        y = float(geometry.get("y_mm", 0.0) or 0.0)
        width = max(1.0, float(geometry.get("width_mm", 1.0) or 1.0))
        height = max(1.0, float(geometry.get("height_mm", 1.0) or 1.0))
    except (TypeError, ValueError):
        x = y = 0.0
        width = height = 1.0
    sx = float(new_fmt.width_mm) / max(1.0, float(old_fmt.width_mm))
    sy = float(new_fmt.height_mm) / max(1.0, float(old_fmt.height_mm))
    return {
        "x_mm": x * sx,
        "y_mm": y * sy,
        "width_mm": width * sx,
        "height_mm": height * sy,
    }


def _clone_text_element(
    template: dict[str, Any],
    *,
    text: str,
    x: float,
    y: float,
    width: float,
    height: float,
    role: str,
    group_id: str,
    origin_block_id: str,
    source_pages: list[int],
) -> dict[str, Any]:
    payload = deepcopy(template.get("payload", {}))
    if not isinstance(payload, dict):
        payload = {}
    payload["text"] = text
    payload["flow_id"] = f"format-reflow:{group_id}"

    metadata = deepcopy(template.get("metadata", {}))
    if not isinstance(metadata, dict):
        metadata = {}
    metadata.update({
        "origin": "format_reflow",
        _GENERATED: True,
        _GROUP_ID: group_id,
        _SOURCE_PAGES: list(source_pages),
        "source_visual_preserved": False,
        "text_layout_mode": "fixed_font",
        _FLOW_ROLE: role,
        _ORIGIN_BLOCK: origin_block_id,
    })

    return new_element(
        kind=TEXT,
        x_mm=x,
        y_mm=y,
        width_mm=width,
        height_mm=height,
        reference_frame=PAGE,
        source_ref=deepcopy(template.get("source_ref")),
        payload=payload,
        metadata=metadata,
    )


def _prefix_elements(
    templates: list[dict[str, Any]],
    *,
    old_fmt: BookFormat,
    new_fmt: BookFormat,
    group_id: str,
    source_pages: list[int],
) -> tuple[list[dict[str, Any]], float]:
    result: list[dict[str, Any]] = []
    bottom = float(new_fmt.margin_top_mm)
    for index, template in enumerate(templates):
        mapped = _map_template_geometry(template, old_fmt, new_fmt)
        remember_source_metrics(template, template.get("geometry", {}) if isinstance(template.get("geometry"), dict) else {})
        layout = measure_text_layout(template, mapped["width_mm"], source_geometry=template.get("geometry") if isinstance(template.get("geometry"), dict) else None)
        mapped["height_mm"] = max(mapped["height_mm"], layout.required_height_mm)
        mapped["y_mm"] = max(0.0, min(mapped["y_mm"], float(new_fmt.height_mm) - mapped["height_mm"]))
        role = str(template.get("metadata", {}).get(_FLOW_ROLE, ROLE_PAGE_TITLE)) if isinstance(template.get("metadata"), dict) else ROLE_PAGE_TITLE
        origin = str(template.get("metadata", {}).get(_ORIGIN_BLOCK, template.get("id", f"prefix-{index}"))) if isinstance(template.get("metadata"), dict) else str(template.get("id", f"prefix-{index}"))
        result.append(_clone_text_element(
            template,
            text=normalized_text(template),
            x=mapped["x_mm"],
            y=mapped["y_mm"],
            width=mapped["width_mm"],
            height=mapped["height_mm"],
            role=role,
            group_id=group_id,
            origin_block_id=origin,
            source_pages=source_pages,
        ))
        bottom = max(bottom, mapped["y_mm"] + mapped["height_mm"])
    return result, bottom


def _running_header_element(
    template: dict[str, Any] | None,
    *,
    old_fmt: BookFormat,
    new_fmt: BookFormat,
    group_id: str,
    source_pages: list[int],
) -> tuple[dict[str, Any] | None, float]:
    if template is None:
        return None, float(new_fmt.margin_top_mm)
    mapped = _map_template_geometry(template, old_fmt, new_fmt)
    remember_source_metrics(template, template.get("geometry", {}) if isinstance(template.get("geometry"), dict) else {})
    layout = measure_text_layout(template, mapped["width_mm"], source_geometry=template.get("geometry") if isinstance(template.get("geometry"), dict) else None)
    mapped["height_mm"] = max(mapped["height_mm"], layout.required_height_mm)
    origin = str(template.get("id", "running-header"))
    element = _clone_text_element(
        template,
        text=normalized_text(template),
        x=mapped["x_mm"],
        y=mapped["y_mm"],
        width=mapped["width_mm"],
        height=mapped["height_mm"],
        role="running_header",
        group_id=group_id,
        origin_block_id=origin,
        source_pages=source_pages,
    )
    return element, max(float(new_fmt.margin_top_mm), mapped["y_mm"] + mapped["height_mm"])


def _paginate_body(
    body: list[dict[str, Any]],
    *,
    prefix: list[dict[str, Any]],
    running_header: dict[str, Any] | None,
    old_fmt: BookFormat,
    new_fmt: BookFormat,
    group_id: str,
    source_pages: list[int],
    minimum_pages: int,
) -> list[list[dict[str, Any]]]:
    usable_width = max(1.0, float(new_fmt.width_mm) - float(new_fmt.margin_inside_mm) - float(new_fmt.margin_outside_mm))
    bottom = float(new_fmt.height_mm) - float(new_fmt.margin_bottom_mm)
    gap = 2.0

    first_prefix, prefix_bottom = _prefix_elements(
        prefix,
        old_fmt=old_fmt,
        new_fmt=new_fmt,
        group_id=group_id,
        source_pages=source_pages,
    )
    header_template, header_bottom = _running_header_element(
        running_header,
        old_fmt=old_fmt,
        new_fmt=new_fmt,
        group_id=group_id,
        source_pages=source_pages,
    )

    pages: list[list[dict[str, Any]]] = []
    current: list[dict[str, Any]] = list(first_prefix)
    y = max(float(new_fmt.margin_top_mm), prefix_bottom + (6.0 if first_prefix else 0.0))
    page_index = 0

    def start_new_page() -> None:
        nonlocal current, y, page_index
        pages.append(current)
        page_index += 1
        current = []
        if header_template is not None:
            current.append(deepcopy(header_template))
            y = max(float(new_fmt.margin_top_mm), header_bottom + 5.0)
        else:
            y = float(new_fmt.margin_top_mm)

    for block_index, template in enumerate(body):
        full_text = normalized_text(template)
        if not full_text:
            continue
        origin_meta = template.get("metadata", {})
        origin_id = str(origin_meta.get(_ORIGIN_BLOCK, template.get("id", f"body-{block_index}"))) if isinstance(origin_meta, dict) else str(template.get("id", f"body-{block_index}"))
        remember_source_metrics(template, template.get("geometry", {}) if isinstance(template.get("geometry"), dict) else {})
        probe = deepcopy(template)
        probe.setdefault("payload", {})["text"] = full_text
        layout = measure_text_layout(probe, usable_width, source_geometry=template.get("geometry") if isinstance(template.get("geometry"), dict) else None)
        lines = list(layout.lines)

        while lines:
            available = bottom - y
            max_lines = int(max(0.0, available - 0.4) // max(0.5, layout.line_height_mm))
            if max_lines <= 0:
                start_new_page()
                continue
            take = min(max_lines, len(lines))
            text = " ".join(lines[:take]).strip()
            lines = lines[take:]
            height = min(available, layout.line_height_mm * max(1, take) + 0.4)
            current.append(_clone_text_element(
                template,
                text=text,
                x=float(new_fmt.margin_inside_mm),  # corrigé selon parité après insertion
                y=y,
                width=usable_width,
                height=height,
                role=ROLE_BODY,
                group_id=group_id,
                origin_block_id=origin_id,
                source_pages=source_pages,
            ))
            y += height + gap
            if lines:
                start_new_page()

    if current or not pages:
        pages.append(current)

    # Le calcul surfacique historique reste un garde-fou minimal : il empêche
    # une recomposition de devenir artificiellement plus compacte que la
    # quantité de matière mesurée au premier changement de format.
    while len(pages) < max(1, minimum_pages):
        # Scinder la page la plus chargée en deux, uniquement entre blocs.
        candidate_index = max(range(len(pages)), key=lambda idx: len([e for e in pages[idx] if isinstance(e, dict) and e.get("metadata", {}).get(_FLOW_ROLE) == ROLE_BODY]))
        body_elements = [e for e in pages[candidate_index] if isinstance(e, dict) and e.get("metadata", {}).get(_FLOW_ROLE) == ROLE_BODY]
        if len(body_elements) < 2:
            break
        split_at = len(body_elements) // 2
        first_ids = {id(e) for e in body_elements[:split_at]}
        second_ids = {id(e) for e in body_elements[split_at:]}
        fixed = [e for e in pages[candidate_index] if id(e) not in first_ids and id(e) not in second_ids]
        first = fixed + body_elements[:split_at]
        second: list[dict[str, Any]] = []
        if header_template is not None:
            second.append(deepcopy(header_template))
        second.extend(body_elements[split_at:])
        pages[candidate_index:candidate_index + 1] = [first, second]
        # Repositionnement vertical simple des corps de la page créée.
        for local_page_index in (candidate_index, candidate_index + 1):
            fixed_bottom = float(new_fmt.margin_top_mm)
            for e in pages[local_page_index]:
                meta = e.get("metadata", {}) if isinstance(e, dict) else {}
                if isinstance(meta, dict) and meta.get(_FLOW_ROLE) != ROLE_BODY:
                    g = e.get("geometry", {})
                    if isinstance(g, dict):
                        fixed_bottom = max(fixed_bottom, float(g.get("y_mm", 0.0) or 0.0) + float(g.get("height_mm", 0.0) or 0.0))
            cy = fixed_bottom + (5.0 if fixed_bottom > float(new_fmt.margin_top_mm) else 0.0)
            for e in pages[local_page_index]:
                meta = e.get("metadata", {}) if isinstance(e, dict) else {}
                if not (isinstance(meta, dict) and meta.get(_FLOW_ROLE) == ROLE_BODY):
                    continue
                g = e.get("geometry", {})
                if isinstance(g, dict):
                    g["y_mm"] = cy
                    cy += float(g.get("height_mm", 0.0) or 0.0) + gap

    return pages


def _page_metadata(
    *,
    prototype: PageV4,
    group_id: str,
    capacity_units: float,
    source_pages: list[int],
    source_page_ids: list[str],
) -> dict[str, Any]:
    metadata = deepcopy(prototype.metadata)
    metadata.pop("structure_rule_overrides", None)
    metadata[_GENERATED] = True
    metadata[_GROUP_ID] = group_id
    metadata[_CAPACITY_UNITS] = float(capacity_units)
    metadata[_SOURCE_PAGES] = list(source_pages)
    metadata[_SOURCE_PAGE_IDS] = list(source_page_ids)
    metadata[_REFLOW_VERSION] = 2
    metadata["source_visual_preserved"] = False
    return metadata


def _replace_group(
    book: BookV4,
    group: list[str],
    *,
    target_count: int,
    group_id: str,
    capacity_units: float,
    old_fmt: BookFormat,
    new_fmt: BookFormat,
) -> tuple[int, int, int]:
    prototype = book.pages[group[0]]
    body, prefix, running_header, source_pages, source_page_ids = _collect_material(book, group)
    page_contents = _paginate_body(
        body,
        prefix=prefix,
        running_header=running_header,
        old_fmt=old_fmt,
        new_fmt=new_fmt,
        group_id=group_id,
        source_pages=source_pages,
        minimum_pages=target_count,
    )
    target_count = max(1, len(page_contents))

    old_pages = [book.pages[page_id] for page_id in group]
    pages: list[PageV4] = []
    for index in range(target_count):
        if index < len(old_pages):
            page = old_pages[index]
        else:
            page = PageV4(
                page_type="Page texte",
                title=prototype.title,
                origin=PageOrigin.AUTHOR,
                part_id=prototype.part_id,
            )
        page.page_type = "Page texte"
        page.title = prototype.title
        page.part_id = prototype.part_id
        page.source = None
        page.spread_id = None
        page.spread_side = None
        page.auto_before = []
        page.auto_after = []
        page.is_compensation = False
        page.recto_verso = None
        page.content = page_contents[index]
        page.metadata = _page_metadata(
            prototype=prototype,
            group_id=group_id,
            capacity_units=capacity_units,
            source_pages=source_pages,
            source_page_ids=source_page_ids,
        )
        pages.append(page)

    first_index = book.page_order.index(group[0])
    new_ids = [page.id for page in pages]
    for page_id in group:
        if page_id not in new_ids:
            book.pages.pop(page_id, None)
    for page in pages:
        book.pages[page.id] = page
    book.page_order[first_index:first_index + len(group)] = new_ids

    # Corriger la marge gauche des corps selon le côté physique obtenu.
    width = max(1.0, float(new_fmt.width_mm) - float(new_fmt.margin_inside_mm) - float(new_fmt.margin_outside_mm))
    for page in pages:
        side = physical_side(book, page.id)
        left = float(new_fmt.margin_inside_mm if side == "recto" else new_fmt.margin_outside_mm)
        for element in page.content:
            if not isinstance(element, dict):
                continue
            metadata = element.get("metadata", {})
            if not (isinstance(metadata, dict) and metadata.get(_FLOW_ROLE) == ROLE_BODY):
                continue
            geometry = element.get("geometry", {})
            if isinstance(geometry, dict):
                geometry["x_mm"] = left
                geometry["width_mm"] = width

    created = max(0, target_count - len(group))
    removed = max(0, len(group) - target_count)
    return created, removed, target_count


def repaginate_book_for_format(
    book: BookV4,
    *,
    old_format: BookFormat,
    new_format: BookFormat,
) -> FormatReflowResult:
    old_count = len(book.page_order)
    if book.kind != BookKind.ROMAN:
        return FormatReflowResult(
            kind=str(getattr(book.kind, "value", book.kind)),
            old_page_count=old_count,
            new_page_count=old_count,
            changed_groups=0,
            created_pages=0,
            removed_pages=0,
            reflowed_pages=0,
        )

    groups = _collect_groups(book)
    changed_groups = 0
    created = 0
    removed = 0
    reflowed_pages = 0

    for group in reversed(groups):
        target_count, group_id, capacity_units = _target_count(group, book, old_format, new_format)
        group_created, group_removed, actual_count = _replace_group(
            book,
            group,
            target_count=target_count,
            group_id=group_id,
            capacity_units=capacity_units,
            old_fmt=old_format,
            new_fmt=new_format,
        )
        if actual_count != len(group) or not _group_id(book.pages[book.page_order[book.page_order.index(group[0])]]):
            changed_groups += 1
        created += group_created
        removed += group_removed
        reflowed_pages += actual_count

    book.history.append({
        "action": "repagination_format",
        "kind": str(getattr(book.kind, "value", book.kind)),
        "old_page_count": old_count,
        "new_page_count_before_structure_sync": len(book.page_order),
        "changed_groups": changed_groups,
        "created_pages": created,
        "removed_pages": removed,
        "reflowed_pages": reflowed_pages,
        "version": 2,
    })
    book.validate()

    return FormatReflowResult(
        kind=str(getattr(book.kind, "value", book.kind)),
        old_page_count=old_count,
        new_page_count=len(book.page_order),
        changed_groups=changed_groups,
        created_pages=created,
        removed_pages=removed,
        reflowed_pages=reflowed_pages,
    )
