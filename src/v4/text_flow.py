from __future__ import annotations

"""Analyse déterministe des flux de texte TomeLinea V4.

Cette couche relie les zones de texte qui semblent appartenir au même texte
continu, sans modifier le Livre ni repaginer quoi que ce soit.

Principes :
- l'inventaire factuel reste la source des objets ;
- les rôles éditoriaux servent de garde-fou ;
- titres, listes, tableaux, légendes et notes ne sont jamais injectés dans le
  corps du texte ;
- une page automatique structurelle peut être traversée logiquement par un
  flux ; une page volontaire / auteur vide constitue au contraire une rupture ;
- une frontière de partie ou un titre explicite ouvre un nouveau flux.
"""

from collections import Counter
from dataclasses import dataclass
import re
from statistics import median
from typing import Any

from src.v4.domain import BookV4, PageV4
from src.v4.page_content_inventory import page_content_inventory
from src.v4.page_element_roles import (
    ROLE_BODY,
    ROLE_PAGE_TITLE,
    ROLE_SECTION_HEADING,
    ROLE_SUBTITLE,
    ElementEditorialRole,
    page_element_roles,
)
from src.v4.structure_auto import is_structural_auto_page


FLOW_BODY = "Corps de texte continu"


@dataclass(frozen=True, slots=True)
class TextFlowSegment:
    page_id: str
    element_id: str
    text: str
    role: str
    page_order_index: int
    local_order_index: int


@dataclass(frozen=True, slots=True)
class TextFlow:
    id: str
    kind: str
    segments: tuple[TextFlowSegment, ...]

    @property
    def page_ids(self) -> tuple[str, ...]:
        result: list[str] = []
        for segment in self.segments:
            if segment.page_id not in result:
                result.append(segment.page_id)
        return tuple(result)

    @property
    def spans_pages(self) -> bool:
        return len(self.page_ids) > 1


@dataclass(frozen=True, slots=True)
class TextFlowTypography:
    """Mesures typographiques factuelles du corps d'un flux.

    Elles décrivent la Source telle qu'elle a été importée. Elles ne constituent
    ni un style imposé ni une décision de mise en page.
    """

    dominant_font: str | None
    dominant_size_pt: float | None
    line_pitch_mm: float | None
    first_line_indent_mm: float | None
    block_gap_mm: float | None
    measured_fragment_count: int


@dataclass(frozen=True, slots=True)
class TextFlowMembership:
    flow_id: str
    element_id: str
    page_id: str
    position: str
    previous_element_id: str | None
    next_element_id: str | None
    previous_page_id: str | None
    next_page_id: str | None


@dataclass(slots=True)
class TextFlowAnalysis:
    flows: tuple[TextFlow, ...]
    membership_by_element: dict[str, TextFlowMembership]

    def flow_for_element(self, element_id: str) -> TextFlow | None:
        membership = self.membership_by_element.get(str(element_id or ""))
        if membership is None:
            return None
        return next((flow for flow in self.flows if flow.id == membership.flow_id), None)

    def flows_for_page(self, page_id: str) -> tuple[TextFlow, ...]:
        value = str(page_id or "")
        return tuple(flow for flow in self.flows if value in flow.page_ids)


@dataclass(frozen=True, slots=True)
class _TextNode:
    page_id: str
    element_id: str
    text: str
    role: str
    role_confidence: float
    page_order_index: int
    local_order_index: int
    size_pt: float
    fonts: tuple[str, ...]
    y_mm: float
    height_mm: float
    exact_page_title: bool


@dataclass(slots=True)
class _PageText:
    page: PageV4
    page_order_index: int
    nodes: list[_TextNode]
    local_groups: list[list[_TextNode]]
    starts_with_boundary: bool = False
    has_body: bool = False


def _norm(value: Any) -> str:
    return " ".join(str(value or "").lower().replace("’", "'").split())


def _font_family(value: str) -> str:
    text = str(value or "").strip().lower()
    if "+" in text and len(text.split("+", 1)[0]) <= 8:
        text = text.split("+", 1)[1]
    for token in ("bolditalic", "bold-italic", "bold", "italic", "regular", "roman"):
        text = text.replace(token, "")
    return " ".join(text.replace("-", " ").replace("_", " ").split())


def _max_size(item: dict[str, Any]) -> float:
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
    return max(values, default=0.0)


def _geometry(item: dict[str, Any]) -> tuple[float, float, float, float]:
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


def _body_signature(
    page_items: list[tuple[PageV4, dict[str, Any], ElementEditorialRole]],
) -> tuple[float, str]:
    sizes: list[float] = []
    families: list[str] = []
    for _page, item, role in page_items:
        if role.role != ROLE_BODY:
            continue
        size = _max_size(item)
        if size > 0:
            sizes.append(size)
        for font in item.get("fonts", []) or []:
            family = _font_family(str(font))
            if family:
                families.append(family)
    body_size = float(median(sizes)) if sizes else 10.0
    body_family = Counter(families).most_common(1)[0][0] if families else ""
    return body_size, body_family


def _looks_like_running_margin_text(
    node: _TextNode,
    *,
    page_height_mm: float,
    repeated_margin_texts: set[str],
) -> bool:
    norm = _norm(node.text)
    if not norm:
        return False
    top = node.y_mm <= page_height_mm * 0.07
    bottom = node.y_mm + node.height_mm >= page_height_mm * 0.93
    if not (top or bottom):
        return False
    if norm in repeated_margin_texts:
        return True
    if re.fullmatch(r"[\[(]?\s*\d{1,4}\s*[\])]?$", norm):
        return True
    return False


def _candidate_body(
    node: _TextNode,
    *,
    body_size: float,
    body_family: str,
    page_height_mm: float,
    repeated_margin_texts: set[str],
) -> bool:
    if _looks_like_running_margin_text(
        node,
        page_height_mm=page_height_mm,
        repeated_margin_texts=repeated_margin_texts,
    ):
        return False

    if node.role == ROLE_BODY:
        return True

    # Garde-fou Roman : sur une page courante sans titre explicite, la première
    # zone de corps peut avoir été proposée comme « Titre de page » par la
    # première couche de compréhension. On la récupère uniquement si son style
    # est réellement celui du corps du livre.
    if (
        node.role == ROLE_PAGE_TITLE
        and node.role_confidence <= 0.93
        and not node.exact_page_title
    ):
        size_ok = node.size_pt <= max(body_size * 1.18, body_size + 1.2)
        families = {_font_family(font) for font in node.fonts if _font_family(font)}
        family_ok = not body_family or not families or body_family in families
        return bool(size_ok and family_ok)

    return False


def _hard_boundary_role(node: _TextNode) -> bool:
    if node.role == ROLE_PAGE_TITLE:
        return node.exact_page_title or node.role_confidence >= 0.95
    return node.role in {ROLE_SECTION_HEADING, ROLE_SUBTITLE}


def _physical_gap_allows_continuation(
    book: BookV4,
    previous_page_index: int,
    next_page_index: int,
) -> bool:
    if next_page_index <= previous_page_index:
        return False
    for index in range(previous_page_index + 1, next_page_index):
        page = book.pages[book.page_order[index]]
        if is_structural_auto_page(page) and not page.content:
            continue
        return False
    return True


def _source_sequence_allows(previous: PageV4, current: PageV4) -> bool:
    if previous.source is None or current.source is None:
        return previous.source is current.source
    if previous.source.source_id != current.source.source_id:
        return False
    if previous.source.source_version_id != current.source.source_version_id:
        return False
    if previous.source.source_page is None or current.source.source_page is None:
        return True
    return current.source.source_page == previous.source.source_page + 1


def _can_join_pages(book: BookV4, previous: _PageText, current: _PageText) -> bool:
    if not previous.local_groups or not current.local_groups:
        return False
    if previous.page.part_id != current.page.part_id:
        return False
    if current.starts_with_boundary:
        return False
    if not _source_sequence_allows(previous.page, current.page):
        return False
    if not _physical_gap_allows_continuation(
        book,
        previous.page_order_index,
        current.page_order_index,
    ):
        return False
    return True


def analyze_text_flows(book: BookV4) -> TextFlowAnalysis:
    """Construit les flux de corps de texte sans modifier ``book``."""
    book.validate()

    raw_pages: list[tuple[PageV4, dict[str, Any], dict[str, ElementEditorialRole]]] = []
    role_items: list[tuple[PageV4, dict[str, Any], ElementEditorialRole]] = []
    margin_occurrences: Counter[str] = Counter()

    for page in book.ordered_pages():
        inventory = page_content_inventory(book, page.id)
        roles = page_element_roles(book, page.id)
        raw_pages.append((page, inventory, roles))
        page_h = max(1.0, float(book.format.height_mm))
        for item in inventory.get("elements", []) or []:
            if not isinstance(item, dict) or item.get("kind") != "text":
                continue
            role = roles.get(str(item.get("id", "")))
            if role is not None:
                role_items.append((page, item, role))
            _x, y, _w, h = _geometry(item)
            if y <= page_h * 0.07 or y + h >= page_h * 0.93:
                norm = _norm(item.get("text", ""))
                if norm:
                    margin_occurrences[norm] += 1

    body_size, body_family = _body_signature(role_items)
    repeated_margin_texts = {
        text for text, count in margin_occurrences.items() if count >= 2
    }

    page_texts: list[_PageText] = []
    for page_order_index, (page, inventory, roles) in enumerate(raw_pages):
        by_id = {
            str(item.get("id", "")): item
            for item in inventory.get("elements", []) or []
            if isinstance(item, dict)
        }
        ordered_items: list[dict[str, Any]] = []
        for element_id in inventory.get("visual_order", []) or []:
            item = by_id.get(str(element_id))
            if item is not None and item.get("kind") == "text":
                ordered_items.append(item)

        nodes: list[_TextNode] = []
        page_title_norm = _norm(page.title)
        for local_order_index, item in enumerate(ordered_items):
            element_id = str(item.get("id", ""))
            role = roles.get(element_id)
            if role is None:
                continue
            _x, y, _w, h = _geometry(item)
            text = str(item.get("text", "") or "")
            nodes.append(
                _TextNode(
                    page_id=page.id,
                    element_id=element_id,
                    text=text,
                    role=role.role,
                    role_confidence=float(role.confidence),
                    page_order_index=page_order_index,
                    local_order_index=local_order_index,
                    size_pt=_max_size(item),
                    fonts=tuple(str(font) for font in item.get("fonts", []) or []),
                    y_mm=y,
                    height_mm=h,
                    exact_page_title=bool(page_title_norm and _norm(text) == page_title_norm),
                )
            )

        groups: list[list[_TextNode]] = []
        current_group: list[_TextNode] = []
        first_body_position: int | None = None
        starts_with_boundary = False
        for index, node in enumerate(nodes):
            is_body = _candidate_body(
                node,
                body_size=body_size,
                body_family=body_family,
                page_height_mm=max(1.0, float(book.format.height_mm)),
                repeated_margin_texts=repeated_margin_texts,
            )
            if is_body:
                if first_body_position is None:
                    first_body_position = index
                    starts_with_boundary = any(_hard_boundary_role(n) for n in nodes[:index])
                current_group.append(node)
                continue

            if current_group:
                groups.append(current_group)
                current_group = []
        if current_group:
            groups.append(current_group)

        page_texts.append(
            _PageText(
                page=page,
                page_order_index=page_order_index,
                nodes=nodes,
                local_groups=groups,
                starts_with_boundary=starts_with_boundary,
                has_body=bool(groups),
            )
        )

    # Fusion des groupes locaux entre pages lorsqu'aucune frontière éditoriale
    # ou physique volontaire ne s'interpose.
    flow_groups: list[list[_TextNode]] = []
    last_page_with_body: _PageText | None = None
    for page_text in page_texts:
        if not page_text.local_groups:
            if is_structural_auto_page(page_text.page) and not page_text.page.content:
                continue
            last_page_with_body = None
            continue

        for local_group_index, group in enumerate(page_text.local_groups):
            can_join_previous = (
                local_group_index == 0
                and last_page_with_body is not None
                and _can_join_pages(book, last_page_with_body, page_text)
                and bool(flow_groups)
            )
            if can_join_previous:
                flow_groups[-1].extend(group)
            else:
                flow_groups.append(list(group))

        last_page_with_body = page_text

    flows: list[TextFlow] = []
    membership: dict[str, TextFlowMembership] = {}
    for flow_index, group in enumerate(flow_groups, 1):
        if not group:
            continue
        first = group[0]
        flow_id = f"text-flow:{first.page_id}:{first.element_id}"
        segments = tuple(
            TextFlowSegment(
                page_id=node.page_id,
                element_id=node.element_id,
                text=node.text,
                role=node.role,
                page_order_index=node.page_order_index,
                local_order_index=node.local_order_index,
            )
            for node in group
        )
        flow = TextFlow(flow_id, FLOW_BODY, segments)
        flows.append(flow)

        for index, segment in enumerate(segments):
            previous = segments[index - 1] if index > 0 else None
            following = segments[index + 1] if index + 1 < len(segments) else None
            if len(segments) == 1:
                position = "isolé"
            elif index == 0:
                position = "début"
            elif index == len(segments) - 1:
                position = "fin"
            else:
                position = "suite"
            membership[segment.element_id] = TextFlowMembership(
                flow_id=flow_id,
                element_id=segment.element_id,
                page_id=segment.page_id,
                position=position,
                previous_element_id=(previous.element_id if previous else None),
                next_element_id=(following.element_id if following else None),
                previous_page_id=(previous.page_id if previous and previous.page_id != segment.page_id else None),
                next_page_id=(following.page_id if following and following.page_id != segment.page_id else None),
            )

    return TextFlowAnalysis(tuple(flows), membership)



def _display_font_name(value: str) -> str:
    text = str(value or "").strip()
    if "+" in text and len(text.split("+", 1)[0]) <= 8:
        text = text.split("+", 1)[1]
    return text or ""


def _flow_typography_profile(book: BookV4, flow: TextFlow) -> TextFlowTypography:
    """Mesure le profil typographique du corps présent dans ``flow``.

    Le calcul s'appuie uniquement sur les fragments déjà extraits de la Source.
    Les valeurs sont donc descriptives : aucune normalisation du Livre n'est
    effectuée ici.
    """

    items_by_id: dict[str, dict[str, Any]] = {}
    for page_id in flow.page_ids:
        inventory = page_content_inventory(book, page_id)
        for item in inventory.get("elements", []) or []:
            if isinstance(item, dict) and item.get("kind") == "text":
                items_by_id[str(item.get("id", ""))] = item

    font_weights: Counter[str] = Counter()
    size_weights: Counter[float] = Counter()
    line_pitches: list[float] = []
    first_line_indents: list[float] = []
    block_gaps: list[float] = []
    fragment_count = 0

    for segment in flow.segments:
        item = items_by_id.get(segment.element_id)
        if item is None:
            continue
        fragments = [
            fragment
            for fragment in (item.get("fragments", []) or [])
            if isinstance(fragment, dict)
        ]
        fragment_count += len(fragments)

        lines: dict[int, list[dict[str, Any]]] = {}
        for fragment in fragments:
            text = str(fragment.get("text", "") or "")
            weight = max(1, len(text.strip()))
            font = _display_font_name(str(fragment.get("font", "") or ""))
            if font:
                font_weights[font] += weight
            try:
                size = round(float(fragment.get("size_pt", 0.0) or 0.0), 2)
            except (TypeError, ValueError):
                size = 0.0
            if size > 0:
                size_weights[size] += weight
            try:
                line_index = int(fragment.get("line_index", 0) or 0)
            except (TypeError, ValueError):
                line_index = 0
            lines.setdefault(line_index, []).append(fragment)

        line_metrics: list[tuple[int, float, float]] = []
        for line_index, line_fragments in lines.items():
            xs: list[float] = []
            ys: list[float] = []
            for fragment in line_fragments:
                geometry = fragment.get("geometry")
                if not isinstance(geometry, dict):
                    continue
                try:
                    xs.append(float(geometry.get("x_mm", 0.0) or 0.0))
                    ys.append(float(geometry.get("y_mm", 0.0) or 0.0))
                except (TypeError, ValueError):
                    continue
            if xs and ys:
                line_metrics.append((line_index, min(xs), min(ys)))
        line_metrics.sort(key=lambda value: value[0])

        if len(line_metrics) >= 2:
            for previous, current in zip(line_metrics, line_metrics[1:]):
                pitch = current[2] - previous[2]
                if 1.0 <= pitch <= 20.0:
                    line_pitches.append(pitch)
            continuation_x = median(value[1] for value in line_metrics[1:])
            indent = line_metrics[0][1] - float(continuation_x)
            if -20.0 <= indent <= 20.0:
                first_line_indents.append(indent)

    for previous, current in zip(flow.segments, flow.segments[1:]):
        if previous.page_id != current.page_id:
            continue
        previous_item = items_by_id.get(previous.element_id)
        current_item = items_by_id.get(current.element_id)
        if previous_item is None or current_item is None:
            continue
        prev_geo = previous_item.get("geometry")
        curr_geo = current_item.get("geometry")
        if not isinstance(prev_geo, dict) or not isinstance(curr_geo, dict):
            continue
        try:
            prev_bottom = float(prev_geo.get("y_mm", 0.0) or 0.0) + float(
                prev_geo.get("height_mm", 0.0) or 0.0
            )
            current_top = float(curr_geo.get("y_mm", 0.0) or 0.0)
        except (TypeError, ValueError):
            continue
        gap = current_top - prev_bottom
        if 0.0 <= gap <= 30.0:
            block_gaps.append(gap)

    dominant_font = font_weights.most_common(1)[0][0] if font_weights else None
    dominant_size = size_weights.most_common(1)[0][0] if size_weights else None
    return TextFlowTypography(
        dominant_font=dominant_font,
        dominant_size_pt=(float(dominant_size) if dominant_size is not None else None),
        line_pitch_mm=(float(median(line_pitches)) if line_pitches else None),
        first_line_indent_mm=(
            float(median(first_line_indents)) if first_line_indents else None
        ),
        block_gap_mm=(float(median(block_gaps)) if block_gaps else None),
        measured_fragment_count=fragment_count,
    )


def flow_typography_profile(book: BookV4, flow_id: str) -> TextFlowTypography | None:
    """Retourne le profil typographique d'un flux identifié, sans mutation."""
    analysis = analyze_text_flows(book)
    flow = next((item for item in analysis.flows if item.id == str(flow_id or "")), None)
    if flow is None:
        return None
    return _flow_typography_profile(book, flow)


def page_text_flow_entries(book: BookV4, page_id: str) -> list[dict[str, Any]]:
    """Résumé sérialisable des flux présents sur une page, pour l'interface."""
    if page_id not in book.pages:
        raise KeyError(page_id)
    analysis = analyze_text_flows(book)
    result: list[dict[str, Any]] = []
    for flow_number, flow in enumerate(analysis.flows, 1):
        page_segments = [segment for segment in flow.segments if segment.page_id == page_id]
        if not page_segments:
            continue
        first_membership = analysis.membership_by_element.get(page_segments[0].element_id)
        last_membership = analysis.membership_by_element.get(page_segments[-1].element_id)
        typography = _flow_typography_profile(book, flow)
        result.append(
            {
                "flow_id": flow.id,
                "flow_number": flow_number,
                "kind": flow.kind,
                "segment_count": len(page_segments),
                "total_segment_count": len(flow.segments),
                "spans_pages": flow.spans_pages,
                "typography": {
                    "dominant_font": typography.dominant_font,
                    "dominant_size_pt": typography.dominant_size_pt,
                    "line_pitch_mm": typography.line_pitch_mm,
                    "first_line_indent_mm": typography.first_line_indent_mm,
                    "block_gap_mm": typography.block_gap_mm,
                    "measured_fragment_count": typography.measured_fragment_count,
                },
                "previous_page_id": (
                    first_membership.previous_page_id if first_membership else None
                ),
                "next_page_id": (
                    last_membership.next_page_id if last_membership else None
                ),
                "segments": [
                    {
                        "element_id": segment.element_id,
                        "text": segment.text,
                        "position": analysis.membership_by_element[segment.element_id].position,
                    }
                    for segment in page_segments
                ],
            }
        )
    return result
