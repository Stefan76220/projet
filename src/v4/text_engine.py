from __future__ import annotations

"""Orchestrateur du moteur Texte TomeLinea V4.

Principe transversal TomeLinea :
1. règles générales du livre ;
2. corrections techniques obligatoires ;
3. analyse exhaustive ;
4. correction des écarts après avis ;
5. exception volontaire si l'utilisateur conserve un cas particulier.

Ce module ne contient aucun choix esthétique caché et ne dépend d'aucune IA.
"""

from dataclasses import dataclass
from typing import Any

from src.v4.text_rules import (
    IMMUTABLE_TEXT_KINDS,
    apply_immutable_text_corrections,
    ensure_text_general_rules,
    set_text_rule_exception,
)
from src.v4.text_anomalies import (
    analyze_book_text_anomalies,
    apply_safe_text_correction,
    safe_text_correction_supported,
    text_issue_still_present,
)


ENGINE_VERSION = "1.0"

# Les types ci-dessous correspondent à des décisions éditoriales courantes.
# Ils ne sont jamais corrigés silencieusement : l'utilisateur voit le problème
# et demande explicitement « Corriger ».
RULE_DEVIATION_KINDS = frozenset({
    "text_not_justified",
    "style_outlier",
    "hyphenation",
})

COMPOSITION_REVIEW_KINDS = frozenset({
    "title_orphan",
    "orphan_line",
    "widow",
    "line_spacing",
})

_EXCEPTION_RULE = {
    "text_not_justified": "alignment",
    "style_outlier": "style",
    "hyphenation": "hyphenation",
    "title_orphan": "title_keep",
    "orphan_line": "widow_orphan",
    "widow": "widow_orphan",
    "line_spacing": "justification_quality",
}


@dataclass(frozen=True, slots=True)
class TextEngineReport:
    rules: dict[str, Any]
    rules_created: bool
    automatic_corrections: tuple[dict[str, Any], ...]
    issues: tuple[dict[str, Any], ...]

    @property
    def decision_count(self) -> int:
        return len(self.issues)


def prepare_text(book: Any) -> TextEngineReport:
    """Prépare le texte sans demander de décision inutile.

    Les fautes techniques objectives sont corrigées immédiatement. Les règles
    générales sont seulement déduites ; les choix éditoriaux restent soumis à
    validation dans l'interface.
    """
    rules, created = ensure_text_general_rules(book)
    corrections = tuple(apply_immutable_text_corrections(book))
    issues = tuple(
        issue for issue in analyze_book_text_anomalies(book)
        if str(issue.get("type", "") or "") not in IMMUTABLE_TEXT_KINDS
    )
    return TextEngineReport(dict(rules), bool(created), corrections, issues)


def analyze_text(book: Any) -> tuple[dict[str, Any], ...]:
    """Analyse l'état courant après les corrections objectives."""
    return tuple(
        issue for issue in analyze_book_text_anomalies(book)
        if str(issue.get("type", "") or "") not in IMMUTABLE_TEXT_KINDS
    )


def correction_supported(book: Any, issue: dict[str, Any]) -> bool:
    return bool(safe_text_correction_supported(issue, book))


def correct_after_approval(book: Any, issue: dict[str, Any]) -> dict[str, Any]:
    """Corrige un écart après accord et vérifie réellement le résultat."""
    if not correction_supported(book, issue):
        raise ValueError("TomeLinea ne possède pas encore de correction automatique fiable pour ce cas.")
    result = dict(apply_safe_text_correction(book, issue) or {})
    if text_issue_still_present(book, issue):
        raise ValueError(
            "La modification n'a pas supprimé le problème ; TomeLinea refuse de le déclarer corrigé."
        )
    return result


def _find_element(book: Any, issue: dict[str, Any]) -> dict[str, Any] | None:
    page_id = str(issue.get("page_id", "") or "")
    element_id = str(issue.get("element_id", "") or "")
    page = getattr(book, "pages", {}).get(page_id)
    if page is None or not element_id:
        return None
    for element in getattr(page, "content", ()):
        if isinstance(element, dict) and str(element.get("id", "") or "") == element_id:
            return element
    return None


def accept_specific_exception(book: Any, issue: dict[str, Any]) -> str:
    """Transforme « Laisser comme ça » en exception volontaire traçable.

    Pour un écart lié à une règle générale, l'élément porte explicitement son
    exception. Pour un diagnostic ponctuel, l'identifiant du problème est
    conservé dans les décisions du livre afin de ne plus le reproposer.
    """
    kind = str(issue.get("type", issue.get("kind", "")) or "").lower()
    rule = _EXCEPTION_RULE.get(kind, "")
    element = _find_element(book, issue)
    if rule and element is not None:
        set_text_rule_exception(element, rule, True)

    metadata = getattr(book, "metadata", None)
    if not isinstance(metadata, dict):
        raise ValueError("Le Livre ne possède pas de métadonnées modifiables.")
    states = metadata.setdefault("text_problem_decisions", {})
    if not isinstance(states, dict):
        states = {}
        metadata["text_problem_decisions"] = states
    key = str(issue.get("id", issue.get("key", "")) or "")
    if key:
        states[key] = "ignored"
    return rule
