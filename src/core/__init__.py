from __future__ import annotations

"""Noyau TomeLinea.

Le package ``src.core`` ne doit avoir aucun effet de bord à l'import.
Les anciennes classes restent accessibles via ``from src.core import ...``,
mais elles sont chargées uniquement lorsqu'elles sont réellement demandées.
Cela permet aux briques modernes (par exemple ``book_source``) d'être utilisées
sans démarrer ni importer l'ancienne interface graphique.
"""

from importlib import import_module


_EXPORTS: dict[str, tuple[str, str]] = {
    "Application": (".application", "Application"),
    "ApplicationController": (".application_controller", "ApplicationController"),
    "Document": (".document", "Document"),
    "DocumentManager": (".document_manager", "DocumentManager"),
    "GraphicObject": (".graphic_object", "GraphicObject"),
    "Page": (".page", "Page"),
    "PageController": (".page_controller", "PageController"),
    "PageManager": (".page_manager", "PageManager"),
    "PageReference": (".page_reference", "PageReference"),
    "Project": (".project", "Project"),
    "ProjectManager": (".project_manager", "ProjectManager"),
}

__all__: list[str] = list(_EXPORTS)


def __getattr__(name: str):
    try:
        module_name, attribute = _EXPORTS[name]
    except KeyError as exc:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}") from exc

    value = getattr(import_module(module_name, __name__), attribute)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    return sorted(set(globals()) | set(__all__))
