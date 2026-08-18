from __future__ import annotations

"""Compatibilité visuelle TomeLinea.

La donnée éditoriale n'est plus dupliquée ici : elle vient exclusivement de
``structure_catalog.py``.
"""

from src.gui_v3.structure_catalog import (
    ALIASES,
    CATALOG_BY_TYPE,
    STRUCTURE_ORDER,
    VISUAL_ORDER,
    structure_builtin_catalog,
    visual_catalog,
)

PAGE_VISUAL_CATALOG = visual_catalog()


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


def page_visual_definition(value: object):
    return CATALOG_BY_TYPE.get(canonical_page_type(value))


def current_page_visuals() -> tuple[dict, ...]:
    return tuple(dict(entry) for entry in PAGE_VISUAL_CATALOG if entry.get("current"))


def future_page_visuals() -> tuple[dict, ...]:
    return tuple(dict(entry) for entry in PAGE_VISUAL_CATALOG if entry.get("future"))
