from __future__ import annotations

"""Règles générales du texte TomeLinea V4.

Le module sépare trois niveaux :
- les règles immuables, corrigées sans décision utilisateur ;
- les règles générales du livre, choisies une fois puis contrôlées partout ;
- les exceptions volontaires portées par une sélection.

Aucune IA n'est nécessaire : ces règles sont déterministes et sérialisables dans
les métadonnées du Livre.
"""

from collections import Counter
from statistics import median
from typing import Any


IMMUTABLE_TEXT_KINDS = frozenset({
    "double_space",
    "space_before_punctuation",
    "missing_space_after_punctuation",
    "french_nonbreaking_space",
})

HYPHENATION_POLICIES = frozenset({"undecided", "forbid", "controlled"})


def _num(value: Any) -> float | None:
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _round_or_none(value: Any, digits: int = 2) -> float | None:
    number = _num(value)
    return None if number is None else round(number, digits)


def infer_text_general_rules(book: Any) -> dict[str, Any]:
    """Déduit les réglages généraux depuis la Source sans modifier le Livre."""
    fonts: Counter[str] = Counter()
    sizes: Counter[float] = Counter()
    line_pitches: list[float] = []
    first_indents: list[float] = []
    block_gaps: list[float] = []

    try:
        from src.v4.text_flow import analyze_text_flows, flow_typography_profile
        analysis = analyze_text_flows(book)
        for flow in analysis.flows:
            profile = flow_typography_profile(book, flow.id)
            if profile is None:
                continue
            weight = max(1, int(profile.measured_fragment_count or 0))
            if profile.dominant_font:
                fonts[str(profile.dominant_font)] += weight
            if profile.dominant_size_pt is not None:
                sizes[round(float(profile.dominant_size_pt), 2)] += weight
            if profile.line_pitch_mm is not None:
                line_pitches.append(float(profile.line_pitch_mm))
            if profile.first_line_indent_mm is not None:
                first_indents.append(float(profile.first_line_indent_mm))
            if profile.block_gap_mm is not None:
                block_gaps.append(float(profile.block_gap_mm))
    except Exception:
        pass

    # Repli simple sur les spans si aucun flux exploitable n'a été reconnu.
    if not fonts or not sizes:
        for page in getattr(book, "ordered_pages", lambda: ())():
            for element in getattr(page, "content", ()):
                if not isinstance(element, dict) or str(element.get("kind", "")).lower() != "text":
                    continue
                payload = element.get("payload", {})
                if not isinstance(payload, dict):
                    continue
                spans = payload.get("spans", ())
                if not isinstance(spans, (list, tuple)):
                    continue
                for span in spans:
                    if not isinstance(span, dict):
                        continue
                    text = str(span.get("text", "") or "").strip()
                    weight = max(1, len(text))
                    font = str(span.get("font", "") or "").strip()
                    size = _num(span.get("size"))
                    if font:
                        fonts[font] += weight
                    if size and size > 0:
                        sizes[round(size, 2)] += weight

    return {
        "version": 1,
        "confirmed": False,
        # Règles fondamentales du texte courant.
        "alignment": "justify",
        "inside_margins": True,
        # Une décision éditoriale doit être prise une seule fois.
        "hyphenation": "undecided",
        # Réglages professionnels internes des césures contrôlées. Ils ne sont
        # pas imposés à l'utilisateur dans l'interface courante.
        "hyphen_min_word_length": 7,
        "hyphen_min_left": 3,
        "hyphen_min_right": 3,
        "hyphen_max_consecutive": 2,
        "hyphen_last_word": False,
        "hyphen_across_page": False,
        "widow_min_lines": 2,
        "orphan_min_lines": 2,
        "heading_keep_lines": 2,
        # La police et les mesures sont héritées de l'auteur/import.
        "font_family": fonts.most_common(1)[0][0] if fonts else "",
        "font_size_pt": sizes.most_common(1)[0][0] if sizes else None,
        "line_pitch_mm": _round_or_none(median(line_pitches) if line_pitches else None),
        "first_line_indent_mm": _round_or_none(median(first_indents) if first_indents else None),
        "paragraph_gap_mm": _round_or_none(median(block_gaps) if block_gaps else None),
        "origin": "source",
    }


def text_general_rules(book: Any, *, create: bool = False) -> dict[str, Any]:
    metadata = getattr(book, "metadata", None)
    if not isinstance(metadata, dict):
        return infer_text_general_rules(book)
    current = metadata.get("text_general_rules")
    if isinstance(current, dict):
        return current
    inferred = infer_text_general_rules(book)
    if create:
        metadata["text_general_rules"] = inferred
        return metadata["text_general_rules"]
    return inferred


def ensure_text_general_rules(book: Any) -> tuple[dict[str, Any], bool]:
    metadata = getattr(book, "metadata", None)
    if not isinstance(metadata, dict):
        raise ValueError("Le Livre ne possède pas de métadonnées modifiables.")
    current = metadata.get("text_general_rules")
    if isinstance(current, dict):
        return current, False
    current = infer_text_general_rules(book)
    metadata["text_general_rules"] = current
    return current, True


def update_text_general_rules(book: Any, **changes: Any) -> dict[str, Any]:
    rules, _created = ensure_text_general_rules(book)
    allowed = {
        "confirmed", "alignment", "inside_margins", "hyphenation",
        "font_family", "font_size_pt", "line_pitch_mm",
        "first_line_indent_mm", "paragraph_gap_mm",
        "hyphen_min_word_length", "hyphen_min_left", "hyphen_min_right",
        "hyphen_max_consecutive", "hyphen_last_word", "hyphen_across_page",
        "widow_min_lines", "orphan_min_lines", "heading_keep_lines",
    }
    for key, value in changes.items():
        if key not in allowed:
            continue
        if key == "hyphenation":
            value = str(value or "undecided").lower()
            if value not in HYPHENATION_POLICIES:
                raise ValueError("Règle de césure inconnue.")
        if key == "alignment":
            value = str(value or "justify").lower()
            if value not in {"justify", "left"}:
                raise ValueError("Alignement général inconnu.")
        if key in {"font_size_pt", "line_pitch_mm", "first_line_indent_mm", "paragraph_gap_mm"}:
            value = _round_or_none(value)
        rules[key] = value
    return rules


def text_rule_exception(element: Any, rule: str) -> bool:
    if not isinstance(element, dict):
        return False
    metadata = element.get("metadata", {})
    if not isinstance(metadata, dict):
        return False
    values = metadata.get("text_rule_exceptions", ())
    if isinstance(values, dict):
        return bool(values.get(str(rule)))
    if isinstance(values, (list, tuple, set, frozenset)):
        return str(rule) in {str(item) for item in values}
    return False


def set_text_rule_exception(element: dict[str, Any], rule: str, enabled: bool = True) -> None:
    metadata = element.setdefault("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
        element["metadata"] = metadata
    values = metadata.setdefault("text_rule_exceptions", {})
    if not isinstance(values, dict):
        values = {str(item): True for item in values} if isinstance(values, (list, tuple, set)) else {}
        metadata["text_rule_exceptions"] = values
    if enabled:
        values[str(rule)] = True
    else:
        values.pop(str(rule), None)


def immutable_text_issues(book: Any) -> list[dict[str, Any]]:
    from src.v4.text_anomalies import analyze_book_text_anomalies
    return [
        issue for issue in analyze_book_text_anomalies(book)
        if str(issue.get("type", "") or "") in IMMUTABLE_TEXT_KINDS
    ]


def apply_immutable_text_corrections(book: Any) -> list[dict[str, Any]]:
    """Corrige toutes les erreurs objectives sans demander une décision inutile."""
    from src.v4.text_anomalies import analyze_book_text_anomalies, apply_safe_text_correction

    results: list[dict[str, Any]] = []
    # Une correction peut déplacer les identifiants de ligne ; on réanalyse après
    # chaque modification plutôt que d'utiliser une liste devenue obsolète.
    guard = 0
    while guard < 10000:
        guard += 1
        issue = next(
            (
                item for item in analyze_book_text_anomalies(book)
                if str(item.get("type", "") or "") in IMMUTABLE_TEXT_KINDS
            ),
            None,
        )
        if issue is None:
            break
        result = apply_safe_text_correction(book, issue)
        results.append(result)
    return results
