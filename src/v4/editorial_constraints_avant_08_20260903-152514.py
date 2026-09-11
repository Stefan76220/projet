from __future__ import annotations

"""
TomeLinea V4 — contraintes éditoriales de pages.

Ce module enregistre uniquement des DECISIONS HUMAINES.
TomeLinea ne crée aucune contrainte éditoriale par défaut.

L'utilisateur exprime le résultat attendu :
- page à droite (recto) ;
- page à gauche (verso).

La mécanique de parité et les éventuelles pages de compensation
restent internes et sont déléguées au moteur structure_parity.

La portée d'une décision peut être :
- la page courante ;
- une sélection explicite de pages ;
- les pages Source similaires à un seuil choisi (88 % par défaut).

Une règle étendue par similarité reste dynamique : les pages candidates
sont retrouvées à partir des résultats d'Analyse, et une page peut être
exclue individuellement sans supprimer la règle étendue.
"""

from datetime import datetime, timezone
from typing import Any, Iterable
from uuid import uuid4

from src.v4.project import ProjectV4
from src.v4.structure_auto import is_structural_auto_page
from src.v4.structure_parity import (
    RECTO,
    VERSO,
    sync_structure_parity,
)


RULES_KEY = "editorial_constraint_rules"
RULES_SCHEMA = "tomelinea.editorial_constraints.v1"
DEFAULT_SIMILARITY_THRESHOLD = 0.88

PAGE_RIGHT = "page_right"
PAGE_LEFT = "page_left"

SCOPE_PAGE = "page"
SCOPE_SELECTION = "selection"
SCOPE_SIMILAR = "similar"

CONSTRAINT_LABELS = {
    PAGE_RIGHT: "Page à droite (recto)",
    PAGE_LEFT: "Page à gauche (verso)",
}

KNOWN_CONSTRAINTS = tuple(CONSTRAINT_LABELS)

CONFLICTS = {
    PAGE_RIGHT: {PAGE_LEFT},
    PAGE_LEFT: {PAGE_RIGHT},
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_id() -> str:
    return str(uuid4())


def _book(project: ProjectV4):
    if project.book is None:
        raise ValueError("Le Projet ne possède aucun Livre.")
    return project.book


def _page(project: ProjectV4, page_id: str):
    book = _book(project)
    page = book.pages.get(str(page_id))
    if page is None:
        raise KeyError(page_id)
    return page


def _ensure_user_page(project: ProjectV4, page_id: str):
    page = _page(project, page_id)
    if is_structural_auto_page(page):
        raise ValueError(
            "Une page automatique de TomeLinea ne reçoit pas "
            "directement de contrainte éditoriale."
        )
    return page


def _clean_kind(kind: str) -> str:
    value = str(kind or "").strip().lower()
    if value not in KNOWN_CONSTRAINTS:
        raise ValueError(f"Contrainte éditoriale inconnue : {kind}")
    return value


def _clean_scope(scope: str) -> str:
    value = str(scope or "").strip().lower()
    if value not in {SCOPE_PAGE, SCOPE_SELECTION, SCOPE_SIMILAR}:
        raise ValueError(f"Portée de contrainte inconnue : {scope}")
    return value


def _rules_root(project: ProjectV4, *, create: bool = True) -> dict[str, Any]:
    raw = project.metadata.get(RULES_KEY)

    if isinstance(raw, dict):
        schema = raw.get("schema")
        rules = raw.get("rules")
        if schema == RULES_SCHEMA and isinstance(rules, list):
            return raw

    if not create:
        return {"schema": RULES_SCHEMA, "rules": []}

    root = {
        "schema": RULES_SCHEMA,
        "rules": [],
    }
    project.metadata[RULES_KEY] = root
    return root


def _rules(project: ProjectV4, *, create: bool = True) -> list[dict[str, Any]]:
    return _rules_root(project, create=create)["rules"]


def _normalize_ids(project: ProjectV4, page_ids: Iterable[str]) -> list[str]:
    book = _book(project)
    result: list[str] = []
    seen: set[str] = set()

    for raw in page_ids:
        page_id = str(raw)
        if page_id in seen:
            continue
        page = book.pages.get(page_id)
        if page is None:
            raise KeyError(page_id)
        if is_structural_auto_page(page):
            continue
        seen.add(page_id)
        result.append(page_id)

    order = {page_id: index for index, page_id in enumerate(book.page_order)}
    result.sort(key=lambda page_id: order.get(page_id, 10**9))
    return result


def _pair_score_index(project: ProjectV4) -> dict[tuple[str, int, int], float]:
    result: dict[tuple[str, int, int], float] = {}

    for finding in project.analysis.findings.values():
        if finding.target_type != "source_page_pair":
            continue
        if finding.key != "similarity.score":
            continue

        target_id = str(finding.target_id or "")
        marker = ":pair:"
        if marker not in target_id:
            continue

        version_id, pair = target_id.rsplit(marker, 1)
        if "-" not in pair:
            continue

        left_raw, right_raw = pair.split("-", 1)
        try:
            left = int(left_raw)
            right = int(right_raw)
            score = float(finding.value)
        except (TypeError, ValueError):
            continue

        key = (version_id, min(left, right), max(left, right))
        result[key] = score

    return result


def similar_page_ids(
    project: ProjectV4,
    anchor_page_id: str,
    *,
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> list[str]:
    """Retourne l'ancre + les pages Source atteignant le seuil demandé."""

    anchor = _ensure_user_page(project, anchor_page_id)
    threshold = float(threshold)

    if not (0.0 <= threshold <= 1.0):
        raise ValueError("Le seuil de similarité doit être compris entre 0 et 1.")

    source = anchor.source
    if source is None or source.source_page is None:
        return [anchor.id]

    version_id = str(source.source_version_id)
    anchor_number = int(source.source_page)
    scores = _pair_score_index(project)

    result = [anchor.id]
    book = _book(project)

    for page_id in book.page_order:
        if page_id == anchor.id:
            continue

        candidate = book.pages[page_id]
        if is_structural_auto_page(candidate):
            continue

        candidate_source = candidate.source
        if candidate_source is None or candidate_source.source_page is None:
            continue
        if str(candidate_source.source_version_id) != version_id:
            continue

        candidate_number = int(candidate_source.source_page)
        key = (
            version_id,
            min(anchor_number, candidate_number),
            max(anchor_number, candidate_number),
        )

        score = scores.get(key)
        if score is not None and score >= threshold:
            result.append(page_id)

    return _normalize_ids(project, result)


def _rule_applies(project: ProjectV4, rule: dict[str, Any], page_id: str) -> bool:
    excluded = {str(value) for value in rule.get("excluded_page_ids", [])}
    if page_id in excluded:
        return False

    scope = str(rule.get("scope") or "")

    if scope in {SCOPE_PAGE, SCOPE_SELECTION}:
        return page_id in {str(value) for value in rule.get("page_ids", [])}

    if scope == SCOPE_SIMILAR:
        anchor_page_id = str(rule.get("anchor_page_id") or "")
        if not anchor_page_id:
            return False
        try:
            candidates = similar_page_ids(
                project,
                anchor_page_id,
                threshold=float(
                    rule.get("similarity_threshold", DEFAULT_SIMILARITY_THRESHOLD)
                ),
            )
        except (KeyError, ValueError):
            return False
        return page_id in candidates

    return False


def rules_for_page(project: ProjectV4, page_id: str) -> list[dict[str, Any]]:
    _ensure_user_page(project, page_id)
    result: list[dict[str, Any]] = []

    for rule in _rules(project, create=False):
        if not isinstance(rule, dict):
            continue
        if _rule_applies(project, rule, page_id):
            result.append(rule)

    return result


def active_constraint_kinds(project: ProjectV4, page_id: str) -> set[str]:
    return {
        str(rule.get("kind"))
        for rule in rules_for_page(project, page_id)
        if str(rule.get("kind")) in KNOWN_CONSTRAINTS
    }


def constraint_labels_for_page(project: ProjectV4, page_id: str) -> list[str]:
    kinds = active_constraint_kinds(project, page_id)
    return [
        CONSTRAINT_LABELS[kind]
        for kind in KNOWN_CONSTRAINTS
        if kind in kinds
    ]


def has_constraints(project: ProjectV4, page_id: str) -> bool:
    return bool(active_constraint_kinds(project, page_id))


def conflicting_kinds(kind: str) -> set[str]:
    return set(CONFLICTS.get(_clean_kind(kind), set()))


def can_apply_constraint(
    project: ProjectV4,
    kind: str,
    page_ids: Iterable[str],
) -> tuple[bool, str]:
    kind = _clean_kind(kind)
    ids = _normalize_ids(project, page_ids)

    if not ids:
        return False, "Aucune page sélectionnée."

    blocked: list[str] = []
    conflicts = conflicting_kinds(kind)

    for page_id in ids:
        active = active_constraint_kinds(project, page_id)
        if active & conflicts:
            blocked.append(page_id)

    if blocked:
        return (
            False,
            "Une contrainte incompatible est déjà active sur "
            f"{len(blocked)} page(s).",
        )

    return True, ""


def _new_rule(
    *,
    kind: str,
    scope: str,
    anchor_page_id: str,
    page_ids: Iterable[str] = (),
    threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> dict[str, Any]:
    return {
        "id": _new_id(),
        "kind": kind,
        "scope": scope,
        "anchor_page_id": str(anchor_page_id),
        "page_ids": [str(value) for value in page_ids],
        "similarity_threshold": float(threshold),
        "excluded_page_ids": [],
        "created_at": _now(),
    }


def _remember_base_side(page) -> None:
    key = "editorial_constraint_base_recto_verso"
    if key not in page.metadata:
        page.metadata[key] = page.recto_verso


def _restore_base_sides(project: ProjectV4) -> None:
    book = _book(project)
    key = "editorial_constraint_base_recto_verso"

    for page in book.pages.values():
        if is_structural_auto_page(page):
            continue
        if key in page.metadata:
            page.recto_verso = page.metadata.get(key)


def _sync_effective_page_sides(project: ProjectV4) -> None:
    book = _book(project)
    _restore_base_sides(project)

    for page_id in list(book.page_order):
        page = book.pages[page_id]
        if is_structural_auto_page(page):
            continue

        kinds = active_constraint_kinds(project, page_id)
        if PAGE_RIGHT in kinds and PAGE_LEFT in kinds:
            raise ValueError(
                "Contraintes incompatibles sur une même page : "
                "Page à droite et Page à gauche."
            )

        _remember_base_side(page)

        if PAGE_RIGHT in kinds:
            page.recto_verso = RECTO
        elif PAGE_LEFT in kinds:
            page.recto_verso = VERSO

    sync_structure_parity(book)


def apply_constraint(
    project: ProjectV4,
    kind: str,
    *,
    anchor_page_id: str,
    scope: str = SCOPE_PAGE,
    selected_page_ids: Iterable[str] = (),
    similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
) -> dict[str, Any]:
    """Ajoute une décision humaine puis recalcule le Livre une seule fois."""

    project.validate()
    kind = _clean_kind(kind)
    scope = _clean_scope(scope)
    anchor = _ensure_user_page(project, anchor_page_id)

    if scope == SCOPE_PAGE:
        target_ids = [anchor.id]
    elif scope == SCOPE_SELECTION:
        target_ids = _normalize_ids(project, selected_page_ids)
        if anchor.id not in target_ids:
            target_ids.append(anchor.id)
            target_ids = _normalize_ids(project, target_ids)
    else:
        target_ids = similar_page_ids(
            project,
            anchor.id,
            threshold=similarity_threshold,
        )

    allowed, reason = can_apply_constraint(project, kind, target_ids)
    if not allowed:
        raise ValueError(reason)

    # Si la même règle est déjà active sur toutes les cibles, on ne duplique rien.
    if target_ids and all(
        kind in active_constraint_kinds(project, page_id)
        for page_id in target_ids
    ):
        return {
            "changed": False,
            "kind": kind,
            "scope": scope,
            "page_ids": target_ids,
            "rule_id": None,
        }

    if scope == SCOPE_SIMILAR:
        rule = _new_rule(
            kind=kind,
            scope=scope,
            anchor_page_id=anchor.id,
            threshold=similarity_threshold,
        )
    else:
        rule = _new_rule(
            kind=kind,
            scope=scope,
            anchor_page_id=anchor.id,
            page_ids=target_ids,
            threshold=similarity_threshold,
        )

    _rules(project).append(rule)
    _sync_effective_page_sides(project)

    project.history.append(
        {
            "action": "contrainte_editoriale_ajoutee",
            "rule_id": rule["id"],
            "kind": kind,
            "scope": scope,
            "anchor_page_id": anchor.id,
            "page_count": len(target_ids),
            "date": _now(),
        }
    )
    project.touch()
    project.validate()

    return {
        "changed": True,
        "kind": kind,
        "scope": scope,
        "page_ids": target_ids,
        "rule_id": rule["id"],
    }


def remove_constraint(
    project: ProjectV4,
    kind: str,
    *,
    page_ids: Iterable[str],
) -> dict[str, Any]:
    """
    Retire la contrainte des pages indiquées.

    Pour une règle étendue par similarité, cela crée une exception locale.
    La règle étendue elle-même reste en place.
    """

    project.validate()
    kind = _clean_kind(kind)
    ids = _normalize_ids(project, page_ids)
    if not ids:
        return {"changed": False, "page_ids": []}

    changed = False
    rules = _rules(project)

    for rule in list(rules):
        if not isinstance(rule, dict) or str(rule.get("kind")) != kind:
            continue

        scope = str(rule.get("scope") or "")

        if scope in {SCOPE_PAGE, SCOPE_SELECTION}:
            current = [str(value) for value in rule.get("page_ids", [])]
            new_ids = [page_id for page_id in current if page_id not in ids]
            if new_ids != current:
                rule["page_ids"] = new_ids
                changed = True
            if not new_ids:
                rules.remove(rule)

        elif scope == SCOPE_SIMILAR:
            excluded = {str(value) for value in rule.get("excluded_page_ids", [])}
            for page_id in ids:
                if _rule_applies(project, rule, page_id):
                    excluded.add(page_id)
                    changed = True
            rule["excluded_page_ids"] = sorted(excluded)

    if changed:
        _sync_effective_page_sides(project)
        project.history.append(
            {
                "action": "contrainte_editoriale_retiree",
                "kind": kind,
                "page_ids": list(ids),
                "date": _now(),
            }
        )
        project.touch()
        project.validate()

    return {
        "changed": changed,
        "page_ids": list(ids),
    }


def remove_similar_rule(project: ProjectV4, rule_id: str) -> bool:
    """Supprime entièrement une règle étendue, exceptions comprises."""

    project.validate()
    rules = _rules(project)
    wanted = str(rule_id)

    for rule in list(rules):
        if str(rule.get("id")) != wanted:
            continue
        if str(rule.get("scope")) != SCOPE_SIMILAR:
            raise ValueError("Cette règle n'est pas une règle étendue par similarité.")

        rules.remove(rule)
        _sync_effective_page_sides(project)
        project.history.append(
            {
                "action": "contrainte_editoriale_extension_supprimee",
                "rule_id": wanted,
                "date": _now(),
            }
        )
        project.touch()
        project.validate()
        return True

    return False


def restore_similar_exception(
    project: ProjectV4,
    rule_id: str,
    page_id: str,
) -> bool:
    """Réintègre une page précédemment exclue d'une règle étendue."""

    project.validate()
    _ensure_user_page(project, page_id)
    wanted = str(rule_id)

    for rule in _rules(project):
        if str(rule.get("id")) != wanted:
            continue
        if str(rule.get("scope")) != SCOPE_SIMILAR:
            return False

        excluded = {str(value) for value in rule.get("excluded_page_ids", [])}
        if page_id not in excluded:
            return False

        excluded.remove(page_id)
        rule["excluded_page_ids"] = sorted(excluded)
        _sync_effective_page_sides(project)
        project.touch()
        project.validate()
        return True

    return False


def similar_rules_for_page(project: ProjectV4, page_id: str) -> list[dict[str, Any]]:
    _ensure_user_page(project, page_id)
    result = []

    for rule in _rules(project, create=False):
        if not isinstance(rule, dict):
            continue
        if str(rule.get("scope")) != SCOPE_SIMILAR:
            continue
        if _rule_applies(project, rule, page_id):
            result.append(rule)

    return result


def similar_rule_statuses_for_page(
    project: ProjectV4,
    page_id: str,
) -> list[dict[str, Any]]:
    """Décrit les règles similaires qui ciblent une page, même exclue."""

    _ensure_user_page(project, page_id)
    result: list[dict[str, Any]] = []

    for rule in _rules(project, create=False):
        if not isinstance(rule, dict):
            continue
        if str(rule.get("scope")) != SCOPE_SIMILAR:
            continue

        anchor_page_id = str(rule.get("anchor_page_id") or "")
        if not anchor_page_id:
            continue

        try:
            candidates = similar_page_ids(
                project,
                anchor_page_id,
                threshold=float(
                    rule.get(
                        "similarity_threshold",
                        DEFAULT_SIMILARITY_THRESHOLD,
                    )
                ),
            )
        except (KeyError, TypeError, ValueError):
            continue

        if page_id not in candidates:
            continue

        excluded = {
            str(value)
            for value in rule.get("excluded_page_ids", [])
        }
        active_ids = [
            candidate_id
            for candidate_id in candidates
            if candidate_id not in excluded
        ]

        kind = str(rule.get("kind") or "")
        result.append(
            {
                "id": str(rule.get("id") or ""),
                "kind": kind,
                "label": CONSTRAINT_LABELS.get(kind, "Contrainte"),
                "anchor_page_id": anchor_page_id,
                "similarity_threshold": float(
                    rule.get(
                        "similarity_threshold",
                        DEFAULT_SIMILARITY_THRESHOLD,
                    )
                ),
                "candidate_count": len(candidates),
                "active_count": len(active_ids),
                "excluded": page_id in excluded,
            }
        )

    return result


def constraint_state_for_pages(
    project: ProjectV4,
    kind: str,
    page_ids: Iterable[str],
) -> str:
    """Retourne ``all``, ``none`` ou ``mixed`` pour une sélection."""

    kind = _clean_kind(kind)
    ids = _normalize_ids(project, page_ids)
    if not ids:
        return "none"

    values = [
        kind in active_constraint_kinds(project, page_id)
        for page_id in ids
    ]

    if all(values):
        return "all"
    if any(values):
        return "mixed"
    return "none"


def has_constraint_context(project: ProjectV4, page_id: str) -> bool:
    """Vrai si la page a une contrainte active ou une exception étendue."""

    return bool(
        active_constraint_kinds(project, page_id)
        or similar_rule_statuses_for_page(project, page_id)
    )


def constraint_context_labels_for_page(
    project: ProjectV4,
    page_id: str,
) -> list[str]:
    labels = constraint_labels_for_page(project, page_id)

    for status in similar_rule_statuses_for_page(project, page_id):
        if not status["excluded"]:
            continue
        labels.append(
            "Exception : " + str(status["label"])
        )

    return labels


def editorial_constraint_issues(project: ProjectV4) -> list[str]:
    issues: list[str] = []
    book = _book(project)

    for rule in _rules(project, create=False):
        if not isinstance(rule, dict):
            issues.append("Règle de contrainte éditoriale invalide.")
            continue

        kind = str(rule.get("kind") or "")
        scope = str(rule.get("scope") or "")
        anchor = str(rule.get("anchor_page_id") or "")

        if kind not in KNOWN_CONSTRAINTS:
            issues.append(f"Contrainte inconnue : {kind}")
        if scope not in {SCOPE_PAGE, SCOPE_SELECTION, SCOPE_SIMILAR}:
            issues.append(f"Portée inconnue : {scope}")
        if anchor not in book.pages:
            issues.append(f"Page d'ancrage inconnue : {anchor}")

    for page_id in book.page_order:
        page = book.pages[page_id]
        if is_structural_auto_page(page):
            continue
        kinds = active_constraint_kinds(project, page_id)
        if PAGE_RIGHT in kinds and PAGE_LEFT in kinds:
            issues.append(
                f"Page {page_id} : Page à droite et Page à gauche simultanées."
            )

    return issues
