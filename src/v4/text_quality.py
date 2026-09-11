from __future__ import annotations

"""TomeLinea V4 — règles typographiques sûres avant composition.

Le modèle source reste intact. Ce module travaille sur une copie du contrat
Canvas et ne corrige automatiquement que les cas non ambigus. Les cas de style
ou de rédaction ne deviennent décisions éditoriales que lorsqu’une interprétation est réellement nécessaire.
"""

from copy import deepcopy
from dataclasses import dataclass
import re
from typing import Any

ENGINE_NAME = "tomelinea.text_quality"
ENGINE_VERSION = "1"
NBSP = "\u00a0"

_LETTER = r"A-Za-zÀ-ÖØ-öø-ÿŒœÆæ"
_UPPER = r"A-ZÀ-ÖØ-ÞŒÆ"
_LOWER = r"a-zà-öø-ÿœæ"

# Un point après ces abréviations ne suffit pas, à lui seul, à prouver qu’une
# nouvelle phrase commence. TL ne transforme donc pas ce cas ambigu en
# correction automatique.
_AMBIGUOUS_DOT_ABBREVIATIONS = {
    "m", "mme", "mlle", "dr", "pr", "etc", "ex", "p", "pp", "cf",
    "env", "av", "apr", "vol", "chap", "fig", "n", "no", "st", "ste",
}


@dataclass(frozen=True, slots=True)
class TextQualityResult:
    contract: dict[str, Any]
    automatic_corrections: tuple[dict[str, Any], ...]
    editorial_decisions: tuple[dict[str, Any], ...]
    blocking_anomalies: tuple[dict[str, Any], ...]

    @property
    def counts(self) -> dict[str, int]:
        return {
            "automatic_corrections": len(self.automatic_corrections),
            "editorial_decisions": len(self.editorial_decisions),
            "blocking_anomalies": len(self.blocking_anomalies),
        }


def _auto_item(*, paragraph: int | None, run: int | None, kind: str, before: str, after: str, message: str) -> dict[str, Any]:
    return {
        "domain": "text",
        "kind": kind,
        "severity": "automatic",
        "source_paragraph": paragraph,
        "source_run": run,
        "message": message,
        "before": before,
        "after": after,
    }


def _editorial_item(*, paragraph: int | None, run: int | None, kind: str, excerpt: str, message: str, proposed_solution: str) -> dict[str, Any]:
    return {
        "domain": "text",
        "kind": kind,
        "severity": "editorial_decision",
        "source_paragraph": paragraph,
        "source_run": run,
        "message": message,
        "excerpt": excerpt,
        "proposed_solution": proposed_solution,
        "choices": ["conserver", "appliquer_solution"],
    }


def _context(text: str, start: int, end: int, radius: int = 34) -> str:
    return text[max(0, start - radius): min(len(text), end + radius)]


def _apply_rule(
    text: str,
    *,
    pattern: re.Pattern[str],
    replacement: str,
    kind: str,
    message: str,
    paragraph: int | None,
    run: int | None,
    corrections: list[dict[str, Any]],
) -> str:
    while True:
        match = pattern.search(text)
        if not match:
            return text
        before = _context(text, match.start(), match.end())
        changed = pattern.sub(replacement, text, count=1)
        delta = len(changed) - len(text)
        after_end = max(match.start(), match.end() + delta)
        after = _context(changed, match.start(), after_end)
        corrections.append(_auto_item(
            paragraph=paragraph,
            run=run,
            kind=kind,
            before=before,
            after=after,
            message=message,
        ))
        text = changed


def _normalize_run_text(
    text: str,
    *,
    paragraph: int | None,
    run: int | None,
    corrections: list[dict[str, Any]],
) -> str:
    # Espaces ordinaires répétés à l'intérieur du texte courant.
    text = _apply_rule(
        text,
        pattern=re.compile(r"(?<=\S) {2,}(?=\S)"),
        replacement=" ",
        kind="double_space",
        message="Des espaces consécutifs inutiles ont été réduits à un seul espace.",
        paragraph=paragraph,
        run=run,
        corrections=corrections,
    )

    # Jamais d'espace avant virgule ou point en français courant.
    text = _apply_rule(
        text,
        pattern=re.compile(r"[ \u00a0\u202f]+([,.])"),
        replacement=r"\1",
        kind="space_before_comma_or_period",
        message="Un espace parasite avant une virgule ou un point a été supprimé.",
        paragraph=paragraph,
        run=run,
        corrections=corrections,
    )

    # Virgule directement suivie d'une lettre : espace certain.
    text = _apply_rule(
        text,
        pattern=re.compile(rf",(?=[{_LETTER}])"),
        replacement=", ",
        kind="missing_space_after_comma",
        message="Un espace manquant après une virgule a été ajouté.",
        paragraph=paragraph,
        run=run,
        corrections=corrections,
    )

    # Point de fin de phrase directement suivi d'une majuscule : espace certain.
    text = _apply_rule(
        text,
        pattern=re.compile(rf"\.(?=[{_UPPER}])"),
        replacement=". ",
        kind="missing_space_after_period",
        message="Un espace manquant après un point a été ajouté.",
        paragraph=paragraph,
        run=run,
        corrections=corrections,
    )

    # Typographie française : espace insécable avant ; : ? ! quand la ponctuation
    # est suivie d'un séparateur de phrase. On évite ainsi URL, heures et ratios.
    for symbol, kind in ((";", "french_space_before_semicolon"), (":", "french_space_before_colon"), ("?", "french_space_before_question"), ("!", "french_space_before_exclamation")):
        pattern = re.compile(rf"(?<=[{_LETTER}0-9»”'\)]){re.escape(symbol)}(?=\s|$|[«“\"'])")
        text = _apply_rule(
            text,
            pattern=pattern,
            replacement=NBSP + symbol,
            kind=kind,
            message=f"L’espace typographique français avant « {symbol} » a été ajoutée.",
            paragraph=paragraph,
            run=run,
            corrections=corrections,
        )

    return text


def _dot_is_unambiguous_sentence_end(text: str, dot_index: int) -> bool:
    """Le point est retenu seulement si rien n’indique une abréviation."""

    if text[max(0, dot_index - 2): dot_index + 1] == "...":
        return False
    left = text[:dot_index]
    match = re.search(rf"([{_LETTER}]+)$", left)
    if not match:
        return True
    token = match.group(1)
    if token.casefold() in _AMBIGUOUS_DOT_ABBREVIATIONS:
        return False
    # Une initiale suivie d’un point est ambiguë (nom, prénom, référence…).
    if len(token) == 1 and token.isalpha():
        return False
    return True


def _sentence_initial_positions(text: str) -> list[int]:
    """Positions des minuscules qui doivent sûrement ouvrir une phrase."""

    positions: list[int] = []
    pattern = re.compile(rf"([.!?])[ \u00a0\u202f]+([{_LOWER}])")
    for match in pattern.finditer(text):
        punctuation = match.group(1)
        if punctuation == "." and not _dot_is_unambiguous_sentence_end(text, match.start(1)):
            continue
        positions.append(match.start(2))
    return positions


def _capitalize_required_sentence_starts(
    run_items: list[dict[str, Any]],
    *,
    paragraph: int | None,
    corrections: list[dict[str, Any]],
) -> None:
    """Rétablit les majuscules grammaticalement obligatoires sans toucher aux autres."""

    texts = [str(item.get("text") or "") for item in run_items]
    full_text = "".join(texts)
    positions = _sentence_initial_positions(full_text)
    if not positions:
        return

    offsets: list[tuple[int, int, dict[str, Any]]] = []
    cursor = 0
    for item, text in zip(run_items, texts):
        offsets.append((cursor, cursor + len(text), item))
        cursor += len(text)

    chars = list(full_text)
    for pos in positions:
        old = chars[pos]
        new = old.upper()
        if old == new:
            continue
        before = _context("".join(chars), pos, pos + 1)
        chars[pos] = new
        after = _context("".join(chars), pos, pos + 1)

        source_run = None
        for start, end, item in offsets:
            if start <= pos < end:
                local = pos - start
                run_text = str(item.get("text") or "")
                item["text"] = run_text[:local] + new + run_text[local + 1:]
                source_run = item.get("source_run")
                break

        corrections.append(_auto_item(
            paragraph=paragraph,
            run=source_run,
            kind="sentence_initial_capital",
            before=before,
            after=after,
            message="Une phrase commençait par une minuscule ; la majuscule obligatoire a été rétablie.",
        ))


def apply_text_quality_rules(contract: dict[str, Any]) -> TextQualityResult:
    """Retourne une copie corrigée pour la composition, sans toucher au modèle source."""

    corrected = deepcopy(contract)
    automatic: list[dict[str, Any]] = []
    editorial: list[dict[str, Any]] = []
    blocking: list[dict[str, Any]] = []

    for block in corrected.get("content", []):
        if block.get("kind") != "paragraph":
            continue
        paragraph = block.get("source_paragraph")
        run_items = block.get("runs", [])
        for run_item in run_items:
            run = run_item.get("source_run")
            original = str(run_item.get("text") or "")
            run_item["text"] = _normalize_run_text(
                original,
                paragraph=paragraph,
                run=run,
                corrections=automatic,
            )

        # La majuscule de début de phrase est une règle grammaticale certaine.
        # Elle est appliquée sur le paragraphe complet pour fonctionner même si
        # le point et le mot suivant appartiennent à deux runs de styles différents.
        _capitalize_required_sentence_starts(
            run_items,
            paragraph=paragraph,
            corrections=automatic,
        )

        # Le texte de paragraphe est une vue dérivée ; les runs restent la source
        # de rendu afin de préserver les styles.
        block["text"] = "".join(str(item.get("text") or "") for item in run_items)

    corrected.setdefault("composition_quality", {})["text"] = {
        "engine": {"name": ENGINE_NAME, "version": ENGINE_VERSION},
        "policy": {
            "automatic_only_when_unambiguous": True,
            "grammar_and_typography_certain_rules_are_automatic": True,
            "existing_mid_sentence_capitals_are_preserved": True,
            "editorial_when_interpretation_required": True,
            "blocking_only_when_composition_cannot_be_trusted": True,
        },
        "automatic_corrections": deepcopy(automatic),
        "editorial_decisions": deepcopy(editorial),
        "blocking_anomalies": deepcopy(blocking),
    }

    return TextQualityResult(
        contract=corrected,
        automatic_corrections=tuple(automatic),
        editorial_decisions=tuple(editorial),
        blocking_anomalies=tuple(blocking),
    )
