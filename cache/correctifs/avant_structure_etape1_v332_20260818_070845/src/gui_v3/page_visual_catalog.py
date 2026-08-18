from __future__ import annotations

"""Catalogue visuel des pages de TomeLinea.

Ce module ne crée pas encore l'interface de l'onglet Structure. Il fournit un
socle commun à B et à la future bibliothèque de types : noms canoniques,
aliases et familles de rendu symbolique. Les entrées ``future=True`` sont
préparées pour le catalogue futur sans être ajoutées automatiquement aux
projets existants.
"""

from typing import Any


PAGE_VISUAL_CATALOG: tuple[dict[str, Any], ...] = (
    # Types déjà employés par TomeLinea / Maquettage.
    {"type": "couverture", "label": "Couverture", "visual": "cover", "family": "ouverture", "current": True},
    {"type": "deuxieme_couverture", "label": "2e de couverture", "visual": "inside_cover", "family": "ouverture", "current": True},
    {"type": "page_titre", "label": "Page de titre", "visual": "title", "family": "ouverture", "current": True},
    {"type": "sommaire", "label": "Sommaire", "visual": "toc", "family": "ouverture", "current": True},
    {"type": "avant_propos", "label": "Avant-propos", "visual": "foreword", "family": "ouverture", "current": True},
    {"type": "tete_partie", "label": "Tête de partie", "visual": "part_head", "family": "corps", "current": True},
    {"type": "chapitre", "label": "Chapitre", "visual": "chapter", "family": "corps", "current": True},
    {"type": "fiche", "label": "Fiche", "visual": "sheet", "family": "corps", "current": True},
    {"type": "texte", "label": "Texte", "visual": "text", "family": "corps", "current": True},
    {"type": "illustration", "label": "Illustration", "visual": "image", "family": "corps", "current": True},
    {"type": "transition", "label": "Transition", "visual": "transition", "family": "corps", "current": True},
    {"type": "page_blanche", "label": "Page blanche", "visual": "blank", "family": "structure", "current": True},
    {"type": "conclusion", "label": "Conclusion", "visual": "conclusion", "family": "fin", "current": True},
    {"type": "troisieme_couverture", "label": "3e de couverture", "visual": "inside_cover", "family": "fin", "current": True},
    {"type": "quatrieme", "label": "4e de couverture", "visual": "back_cover", "family": "fin", "current": True},
    {"type": "personnalisee", "label": "Page personnalisée", "visual": "custom", "family": "corps", "current": True},

    # Catalogue préparé pour Structure : aucune création automatique ici.
    {"type": "faux_titre", "label": "Faux-titre", "visual": "title_light", "family": "ouverture", "future": True},
    {"type": "frontispice", "label": "Frontispice", "visual": "image", "family": "ouverture", "future": True},
    {"type": "mentions_legales", "label": "Mentions légales / Copyright", "visual": "legal", "family": "ouverture", "future": True},
    {"type": "dedicace", "label": "Dédicace", "visual": "dedication", "family": "ouverture", "future": True},
    {"type": "epigraphe", "label": "Épigraphe", "visual": "quote", "family": "ouverture", "future": True},
    {"type": "preface", "label": "Préface", "visual": "foreword", "family": "ouverture", "future": True},
    {"type": "avertissement", "label": "Avertissement", "visual": "foreword", "family": "ouverture", "future": True},
    {"type": "introduction", "label": "Introduction", "visual": "chapter", "family": "ouverture", "future": True},
    {"type": "citation", "label": "Citation", "visual": "quote", "family": "corps", "future": True},
    {"type": "encadre", "label": "Encadré", "visual": "box", "family": "corps", "future": True},
    {"type": "tableau", "label": "Tableau", "visual": "table", "family": "corps", "future": True},
    {"type": "graphique", "label": "Graphique", "visual": "chart", "family": "corps", "future": True},
    {"type": "carte", "label": "Carte", "visual": "map", "family": "corps", "future": True},
    {"type": "chronologie", "label": "Chronologie", "visual": "timeline", "family": "corps", "future": True},
    {"type": "portfolio", "label": "Portfolio", "visual": "portfolio", "family": "corps", "future": True},
    {"type": "double_page", "label": "Double page", "visual": "spread", "family": "corps", "future": True},
    {"type": "annexe", "label": "Annexe", "visual": "appendix", "family": "fin", "future": True},
    {"type": "postface", "label": "Postface", "visual": "foreword", "family": "fin", "future": True},
    {"type": "notes", "label": "Notes", "visual": "notes", "family": "fin", "future": True},
    {"type": "glossaire", "label": "Glossaire", "visual": "glossary", "family": "fin", "future": True},
    {"type": "lexique", "label": "Lexique", "visual": "glossary", "family": "fin", "future": True},
    {"type": "bibliographie", "label": "Bibliographie", "visual": "references", "family": "fin", "future": True},
    {"type": "sources", "label": "Sources", "visual": "references", "family": "fin", "future": True},
    {"type": "index", "label": "Index", "visual": "index", "family": "fin", "future": True},
    {"type": "credits", "label": "Crédits iconographiques", "visual": "credits", "family": "fin", "future": True},
    {"type": "remerciements", "label": "Remerciements", "visual": "dedication", "family": "fin", "future": True},
    {"type": "biographie", "label": "Biographie de l’auteur", "visual": "bio", "family": "fin", "future": True},
    {"type": "autres_ouvrages", "label": "Autres ouvrages", "visual": "portfolio", "family": "fin", "future": True},
)


ALIASES: dict[str, str] = {
    "cover": "couverture", "front_cover": "couverture", "1re de couverture": "couverture",
    "2e_couverture": "deuxieme_couverture", "second_cover": "deuxieme_couverture",
    "inside_front_cover": "deuxieme_couverture", "2e de couverture": "deuxieme_couverture",
    "deuxième de couverture": "deuxieme_couverture", "deuxieme de couverture": "deuxieme_couverture",
    "title_page": "page_titre", "page de titre": "page_titre", "titre": "page_titre",
    "toc": "sommaire", "table des matières": "sommaire", "table des matieres": "sommaire",
    "avant-propos": "avant_propos", "avant propos": "avant_propos",
    "tête de partie": "tete_partie", "tete de partie": "tete_partie", "part_head": "tete_partie",
    "chapter": "chapitre", "page de chapitre": "chapitre", "tête de chapitre": "chapitre", "tete de chapitre": "chapitre",
    "page de texte": "texte", "text": "texte", "page courante": "texte", "page commune": "texte",
    "page image": "illustration", "image": "illustration",
    "blank": "page_blanche", "page blanche": "page_blanche", "page auto": "page_blanche",
    "3e_couverture": "troisieme_couverture", "third_cover": "troisieme_couverture",
    "inside_back_cover": "troisieme_couverture", "3e de couverture": "troisieme_couverture",
    "troisième de couverture": "troisieme_couverture", "troisieme de couverture": "troisieme_couverture",
    "4e_couverture": "quatrieme", "back_cover": "quatrieme", "4e de couverture": "quatrieme",
    "quatrième de couverture": "quatrieme", "quatrieme de couverture": "quatrieme",
    "personnalisée": "personnalisee", "personnalisee": "personnalisee",
    "appendix": "annexe",
}


CATALOG_BY_TYPE: dict[str, dict[str, Any]] = {
    str(entry["type"]): dict(entry) for entry in PAGE_VISUAL_CATALOG
}


def canonical_page_type(value: object) -> str:
    raw = str(value or "").strip().lower().replace("-", "_")
    raw = " ".join(raw.split())
    if not raw:
        return ""
    if raw in ALIASES:
        return ALIASES[raw]
    normalized = raw.replace(" ", "_")
    if normalized in CATALOG_BY_TYPE:
        return normalized
    if raw in CATALOG_BY_TYPE:
        return raw
    return normalized


def page_visual_definition(value: object) -> dict[str, Any] | None:
    return CATALOG_BY_TYPE.get(canonical_page_type(value))


def current_page_visuals() -> tuple[dict[str, Any], ...]:
    return tuple(dict(entry) for entry in PAGE_VISUAL_CATALOG if entry.get("current"))


def future_page_visuals() -> tuple[dict[str, Any], ...]:
    return tuple(dict(entry) for entry in PAGE_VISUAL_CATALOG if entry.get("future"))
