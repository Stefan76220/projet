from __future__ import annotations

"""Présentation utilisateur des anomalies bloquantes TomeLinea.

Cette couche ne corrige rien et ne substitue jamais silencieusement une
ressource. Elle transforme un blocage technique en explication courte,
compréhensible et orientée vers une solution. Tous les blocages utilisent le
même chemin utilisateur : attente/analyse -> composition suspendue -> action ->
nouvelle analyse.
"""

from typing import Any


def _missing_font_names(details: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for item in details.get("fonts", []) if isinstance(details, dict) else []:
        if not isinstance(item, dict):
            continue
        family = str(item.get("family") or "").strip()
        style = str(item.get("style") or "").strip()
        if not family:
            continue
        label = family
        if style and style != "regular":
            label = f"{family} ({style})"
        if label not in names:
            names.append(label)
    return names


def _one_blocking_user_view(item: dict[str, Any]) -> dict[str, Any]:
    first = dict(item)
    kind = str(first.get("kind") or "").strip()
    details = first.get("details") if isinstance(first.get("details"), dict) else {}
    proposed = str(first.get("proposed_solution") or first.get("solution") or "").strip()

    actions: list[dict[str, str]] = []
    if kind == "missing_fonts":
        names = _missing_font_names(details)
        detail = "Police manquante : " + ", ".join(names) if names else "Une police nécessaire est absente."
        problem = "Une police nécessaire au document est absente."
        why = "TomeLinea ne peut pas garantir une recomposition fidèle avec une autre police."
        actions.append({"id": "add_font", "label": "Ajouter la police…"})
        actions.append({"id": "choose_font_substitute", "label": "Choisir une police de remplacement…"})
    elif kind == "unsupported_body_nodes":
        detail = "Le DOCX contient un élément que TomeLinea ne sait pas encore convertir sans risque."
        problem = "Un élément du document n'est pas encore pris en charge."
        why = "Continuer pourrait modifier ou perdre une partie du contenu."
    else:
        detail = str(first.get("message") or "Un problème empêche une composition fiable.").strip()
        problem = "TomeLinea ne peut pas poursuivre cette composition en toute sécurité."
        why = "Le document est arrêté avant toute transformation incertaine."

    # Tous les blocages peuvent être revérifiés après intervention de l'utilisateur.
    actions.append({"id": "retry", "label": "Relancer l’analyse"})

    return {
        "blocked": True,
        "kind": kind or "blocking_anomaly",
        "title": "TomeLinea a besoin de votre intervention",
        "problem": problem,
        "detail": detail,
        "why": why,
        "solution": proposed or "Corriger le problème indiqué puis relancer l'analyse.",
        "source_preserved": True,
        "actions": actions,
        "raw": first,
    }


def build_blocking_user_views(blocking_anomalies: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Retourne une vue utilisateur par blocage, dans l'ordre de détection."""

    return [
        _one_blocking_user_view(item)
        for item in blocking_anomalies
        if isinstance(item, dict)
    ]


def build_blocking_user_view(blocking_anomalies: list[dict[str, Any]]) -> dict[str, Any]:
    """Prépare la vue principale de Composition suspendue.

    Compatibilité : l'API historique renvoie toujours un seul dictionnaire, mais
    expose désormais aussi ``views`` pour permettre la navigation quand plusieurs
    blocages sont présents.
    """

    items = [dict(item) for item in blocking_anomalies if isinstance(item, dict)]
    views = build_blocking_user_views(items)
    if not views:
        return {
            "blocked": False,
            "title": "Aucun blocage",
            "problem": "",
            "detail": "",
            "why": "",
            "solution": "",
            "source_preserved": True,
            "count": 0,
            "views": [],
            "items": [],
            "actions": [],
        }

    result = dict(views[0])
    result.update({
        "count": len(views),
        "views": views,
        "items": items,
    })
    return result
