"""Catalogue des Situations Texte de TomeLinea V5.

Aucun detecteur n'est recree ici. V5 reutilise le moteur V4 valide
``analyze_book_text_anomalies`` puis traduit ses resultats vers le contrat
Situation de V5-09.

Les scores internes de confiance V4 servent seulement au dedoublonnage du
detecteur. Ils ne sont volontairement pas transmis au moteur de decisions V5.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Iterable, Mapping

from src.v4.text_anomalies import (
    AUTOMATIC_TEXT_CORRECTION_KINDS,
    SAFE_TEXT_CORRECTION_KINDS,
    analyze_book_text_anomalies,
    safe_text_correction_supported,
)

from tomelinea.rules import Situation


class TextSituationClass(str, Enum):
    TECHNICAL = "technical"
    RECOMMENDED = "recommended"
    LOCAL = "local"


TECHNICAL_TEXT_KINDS = frozenset(SAFE_TEXT_CORRECTION_KINDS)

RECOMMENDED_TEXT_KINDS = frozenset({
    "text_not_justified",
    "style_outlier",
    "hyphenation",
    "title_orphan",
    "orphan_line",
    "widow",
})

TEXT_SITUATION_KINDS = frozenset(
    set(TECHNICAL_TEXT_KINDS)
    | set(RECOMMENDED_TEXT_KINDS)
)


def text_situation_class(kind: str) -> TextSituationClass:
    value = str(kind or "").strip().lower()

    if value in TECHNICAL_TEXT_KINDS:
        return TextSituationClass.TECHNICAL

    if value in RECOMMENDED_TEXT_KINDS:
        return TextSituationClass.RECOMMENDED

    return TextSituationClass.LOCAL


def _clean_geometry(value: object) -> dict[str, float]:
    if not isinstance(value, Mapping):
        return {}

    result: dict[str, float] = {}

    for key in ("x_mm", "y_mm", "width_mm", "height_mm"):
        raw = value.get(key)
        try:
            if raw is not None:
                result[key] = float(raw)
        except (TypeError, ValueError):
            continue

    return result


def _subject_id(issue: Mapping[str, Any]) -> str:
    element_id = str(issue.get("element_id") or "").strip()
    if element_id:
        return element_id

    page_id = str(issue.get("page_id") or "").strip()
    if page_id:
        return page_id

    issue_id = str(issue.get("id") or issue.get("key") or "").strip()
    if issue_id:
        return issue_id

    raise ValueError("Anomalie Texte sans identifiant stable exploitable.")


def text_issue_to_situation(
    issue: Mapping[str, Any],
    *,
    book: Any = None,
) -> Situation:
    """Traduit une anomalie V4 sans inventer ni corriger quoi que ce soit."""

    if not isinstance(issue, Mapping):
        raise TypeError("Une anomalie Texte doit etre un dictionnaire.")

    kind = str(
        issue.get("type", issue.get("kind", ""))
        or ""
    ).strip().lower()

    if not kind:
        raise ValueError("Anomalie Texte sans type.")

    issue_id = str(
        issue.get("id", issue.get("key", ""))
        or ""
    ).strip()

    element_ids = tuple(
        str(value).strip()
        for value in issue.get("element_ids", ())
        if str(value).strip()
    ) if isinstance(issue.get("element_ids", ()), (list, tuple)) else ()

    facts = {
        "issue_id": issue_id,
        "classification": text_situation_class(kind).value,
        "title": str(issue.get("title") or "").strip(),
        "technical_term": str(issue.get("technical_term") or "").strip(),
        "why": str(issue.get("why") or "").strip(),
        "proposal": str(issue.get("proposal") or "").strip(),
        "geometry": _clean_geometry(issue.get("geometry")),
        "source_page": issue.get("source_page"),
        "element_ids": element_ids,
        "automatic_correction_kind": kind in AUTOMATIC_TEXT_CORRECTION_KINDS,
        "correction_supported": bool(
            safe_text_correction_supported(dict(issue), book)
        ),
        "source_engine": str(issue.get("engine") or "").strip(),
        "source_engine_version": str(issue.get("engine_version") or "").strip(),
    }

    # Le score "confidence" de V4 n'entre jamais dans Situation.
    facts = {
        key: value
        for key, value in facts.items()
        if value not in ("", (), {}, None)
    }

    return Situation(
        domain="text",
        kind=kind,
        subject_id=_subject_id(issue),
        page_id=str(issue.get("page_id") or "").strip() or None,
        qualifier=issue_id,
        facts=facts,
    )


def text_situations_from_issues(
    issues: Iterable[Mapping[str, Any]],
    *,
    book: Any = None,
) -> tuple[Situation, ...]:
    return tuple(
        text_issue_to_situation(issue, book=book)
        for issue in issues
    )


def detect_text_situations(book: Any) -> tuple[Situation, ...]:
    """Lance le detecteur Texte V4 valide puis traduit ses sorties."""

    issues = analyze_book_text_anomalies(book)
    return text_situations_from_issues(
        issues,
        book=book,
    )


__all__ = [
    "TextSituationClass",
    "TECHNICAL_TEXT_KINDS",
    "RECOMMENDED_TEXT_KINDS",
    "TEXT_SITUATION_KINDS",
    "text_situation_class",
    "text_issue_to_situation",
    "text_situations_from_issues",
    "detect_text_situations",
    "analyze_book_text_anomalies",
]