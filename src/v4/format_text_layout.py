from __future__ import annotations

"""Mesure déterministe du texte lors d'un changement de format.

Le moteur utilise la police exacte installée lorsqu'elle est disponible. En
absence de cette police (tests ou machine incomplète), il retombe sur les
mesures factuelles extraites de la Source : nombre de lignes, largeur et
hauteur du bloc d'origine.
"""

from dataclasses import dataclass
import math
from typing import Any


@dataclass(frozen=True, slots=True)
class FormatTextLayout:
    lines: tuple[str, ...]
    line_height_mm: float
    required_height_mm: float
    exact_font: bool
    font_size_pt: float
    # Indique les traits de césure introduits uniquement pour la composition.
    # Ils ne doivent jamais devenir des caractères du contenu logique.
    line_hyphenated: tuple[bool, ...] = ()


def _payload(element: dict[str, Any]) -> dict[str, Any]:
    value = element.get("payload", {})
    return value if isinstance(value, dict) else {}


def _first_span(element: dict[str, Any]) -> dict[str, Any] | None:
    spans = _payload(element).get("spans", [])
    if not isinstance(spans, list):
        return None
    for span in spans:
        if isinstance(span, dict) and str(span.get("text", "") or "").strip():
            return span
    for span in spans:
        if isinstance(span, dict):
            return span
    return None


def normalized_text(element: dict[str, Any]) -> str:
    return " ".join(str(_payload(element).get("text", "") or "").split())


def join_layout_lines(lines: tuple[str, ...] | list[str], hyphenated: tuple[bool, ...] | list[bool] = ()) -> str:
    """Reconstruit le texte logique sans figer les césures de composition."""
    parts: list[str] = []
    flags = list(hyphenated or ())
    for index, raw in enumerate(lines):
        value = str(raw or "")
        inserted_hyphen = index < len(flags) and bool(flags[index]) and value.endswith("-")
        if inserted_hyphen:
            value = value[:-1]
        if not parts:
            parts.append(value)
            continue
        if index - 1 < len(flags) and bool(flags[index - 1]):
            parts[-1] += value
        else:
            parts.append(value)
    return " ".join(part for part in parts if part).strip()


def _font_size(element: dict[str, Any]) -> float:
    span = _first_span(element)
    try:
        value = float((span or {}).get("size", 10.0) or 10.0)
    except (TypeError, ValueError):
        value = 10.0
    return max(0.1, value)


def _wrap_by_character_capacity(text: str, capacity: int) -> tuple[str, ...]:
    words = str(text or "").split()
    if not words:
        return ("",)
    capacity = max(1, int(capacity))
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if not current or len(candidate) <= capacity:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return tuple(lines or [""])


def _fallback_layout(
    element: dict[str, Any],
    width_mm: float,
    *,
    source_geometry: dict[str, Any] | None = None,
) -> FormatTextLayout:
    payload = _payload(element)
    raw_text = str(payload.get("text", "") or "")
    text = raw_text if raw_text.strip() else normalized_text(element)
    width_mm = max(1.0, float(width_mm))
    font_size = _font_size(element)

    geometry = source_geometry if isinstance(source_geometry, dict) else element.get("geometry", {})
    if not isinstance(geometry, dict):
        geometry = {}
    try:
        source_width = max(1.0, float(geometry.get("width_mm", width_mm) or width_mm))
    except (TypeError, ValueError):
        source_width = width_mm
    try:
        source_height = max(0.1, float(geometry.get("height_mm", 1.0) or 1.0))
    except (TypeError, ValueError):
        source_height = 1.0

    spans = _payload(element).get("spans", [])
    line_indices: list[int] = []
    if isinstance(spans, list):
        for span in spans:
            if not isinstance(span, dict):
                continue
            try:
                line_indices.append(int(span.get("line_index", 0) or 0))
            except (TypeError, ValueError):
                pass
    source_lines = max(line_indices, default=0) + 1
    source_lines = max(1, source_lines)

    metadata = element.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}

    try:
        cached_line_height = float(metadata.get("format_text_line_height_mm", 0.0) or 0.0)
    except (TypeError, ValueError):
        cached_line_height = 0.0
    font_line_height = font_size * 25.4 / 72.0 * 1.12
    source_line_height = (
        source_height / source_lines
        if source_lines > 1
        else min(source_height, font_line_height * 1.35)
    )
    line_height = max(
        1.0,
        cached_line_height,
        source_line_height,
        font_line_height,
    )

    try:
        cached_density = float(metadata.get("format_text_char_density", 0.0) or 0.0)
    except (TypeError, ValueError):
        cached_density = 0.0
    if cached_density > 0:
        density = cached_density
    else:
        average_chars = max(1.0, len(text) / source_lines)
        density = average_chars / source_width
        density = max(0.15, density)

    capacity = max(4, int(math.floor(density * width_mm)))
    lines = _wrap_by_character_capacity(text, capacity)
    required = line_height * len(lines) + 0.4
    return FormatTextLayout(
        lines=lines,
        line_height_mm=line_height,
        required_height_mm=required,
        exact_font=False,
        font_size_pt=font_size,
        line_hyphenated=tuple(False for _ in lines),
    )


def measure_text_layout(
    element: dict[str, Any],
    width_mm: float,
    *,
    source_geometry: dict[str, Any] | None = None,
    rules: dict[str, Any] | None = None,
) -> FormatTextLayout:
    """Mesure le texte à largeur donnée sans modifier l'élément.

    La voie exacte utilise désormais Pillow/FreeType et le même compositeur que
    l'onglet Texte. Le moteur de changement de format ne dépend donc plus de
    MuPDF pour la mesure typographique.
    """

    text = normalized_text(element)
    width_mm = max(1.0, float(width_mm))
    if not text:
        return FormatTextLayout(("",), 1.0, 1.0, False, _font_size(element))

    span = _first_span(element)
    pdf_font = str((span or {}).get("font", "") or "")
    font_size = _font_size(element)

    try:
        from src.v4.font_availability import match_pdf_font
        from src.v4.text_compositor import compose_text, pillow_text_metrics

        match = match_pdf_font(pdf_font)
        if match.status == "exact" and match.installed_path:
            metrics = pillow_text_metrics(str(match.installed_path), font_size)
            width_pt = width_mm * 72.0 / 25.4

            metadata = element.get("metadata", {})
            if not isinstance(metadata, dict):
                metadata = {}
            active_rules = rules if isinstance(rules, dict) else {}
            alignment = str(
                metadata.get("text_alignment", active_rules.get("alignment", "justify"))
                or "justify"
            ).lower()
            # Le changement de format ne doit jamais inventer une césure si la
            # règle du livre n'est pas disponible dans cet appel bas niveau.
            hyphenation = str(
                active_rules.get("hyphenation", metadata.get("hyphenation_policy", "forbid"))
                or "forbid"
            ).lower()
            if hyphenation not in {"forbid", "controlled"}:
                hyphenation = "forbid"
            try:
                indent_mm = max(0.0, float(active_rules.get("first_line_indent_mm") or 0.0))
            except (TypeError, ValueError):
                indent_mm = 0.0
            if bool(metadata.get("format_flow_continuation", False)):
                indent_mm = 0.0

            composed = compose_text(
                text,
                width=width_pt,
                measure=metrics.measure,
                alignment=alignment,
                hyphenation=hyphenation,
                min_word_length=int(active_rules.get("hyphen_min_word_length", 7) or 7),
                min_left=int(active_rules.get("hyphen_min_left", 3) or 3),
                min_right=int(active_rules.get("hyphen_min_right", 3) or 3),
                max_consecutive_hyphens=int(active_rules.get("hyphen_max_consecutive", 2) or 2),
                first_line_indent=indent_mm * 72.0 / 25.4,
            )
            lines = tuple(line.text for line in composed.lines) or ("",)
            natural_line_height_mm = max(font_size, float(metrics.line_height_pt)) * 25.4 / 72.0
            try:
                line_pitch_mm = max(0.0, float(active_rules.get("line_pitch_mm") or 0.0))
            except (TypeError, ValueError):
                line_pitch_mm = 0.0
            line_height_mm = max(natural_line_height_mm, line_pitch_mm)
            try:
                paragraph_gap_mm = max(0.0, float(active_rules.get("paragraph_gap_mm") or 0.0))
            except (TypeError, ValueError):
                paragraph_gap_mm = 0.0
            paragraph_breaks = sum(1 for line in composed.lines[:-1] if line.paragraph_end)
            return FormatTextLayout(
                lines=lines,
                line_height_mm=line_height_mm,
                required_height_mm=(
                    line_height_mm * len(lines)
                    + paragraph_gap_mm * paragraph_breaks
                    + 0.4
                ),
                exact_font=True,
                font_size_pt=font_size,
                line_hyphenated=tuple(bool(line.hyphenated) for line in composed.lines),
            )
    except Exception:
        pass

    return _fallback_layout(
        element,
        width_mm,
        source_geometry=source_geometry,
    )


def remember_source_metrics(element: dict[str, Any], geometry: dict[str, Any]) -> None:
    """Mémorise seulement des mesures, jamais le contenu lui-même."""
    metadata = element.setdefault("metadata", {})
    if not isinstance(metadata, dict):
        return
    if "format_text_line_height_mm" in metadata and "format_text_char_density" in metadata:
        return

    text = normalized_text(element)
    spans = _payload(element).get("spans", [])
    line_indices: list[int] = []
    if isinstance(spans, list):
        for span in spans:
            if isinstance(span, dict):
                try:
                    line_indices.append(int(span.get("line_index", 0) or 0))
                except (TypeError, ValueError):
                    pass
    source_lines = max(line_indices, default=0) + 1
    source_lines = max(1, source_lines)
    try:
        width = max(1.0, float(geometry.get("width_mm", 1.0) or 1.0))
        height = max(0.1, float(geometry.get("height_mm", 0.1) or 0.1))
    except (TypeError, ValueError):
        return

    font_line_height = _font_size(element) * 25.4 / 72.0 * 1.12
    source_line_height = (
        height / source_lines
        if source_lines > 1
        else min(height, font_line_height * 1.35)
    )
    metadata.setdefault(
        "format_text_line_height_mm",
        max(1.0, source_line_height, font_line_height),
    )
    average_chars = max(1.0, len(text) / source_lines)
    metadata.setdefault(
        "format_text_char_density",
        max(0.15, average_chars / width),
    )
