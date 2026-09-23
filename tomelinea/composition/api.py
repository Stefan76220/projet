"""API Composition commune de TomeLinea V5.

V5-04 ne cree pas un second modele de composition.
Le Livre reste l'unique autorite : les elements sont stockes dans
Page.content avec identifiants stables et geometrie en millimetres.

L'implementation V4 gelee reste utilisee par equivalence.
"""

from src.v4.composition import (
    BLEED,
    COMPOSITION_SCHEMA,
    COMPOSITION_VERSION,
    DOCUMENT,
    ELEMENT_KINDS,
    IMAGE,
    MARGINS,
    PAGE,
    REFERENCE_FRAMES,
    TEXT,
    add_element,
    composition_issues,
    element_by_id,
    frame_bounds,
    new_element,
    normalize_kind,
    normalize_reference_frame,
    remove_element,
    source_reference,
    update_element_geometry,
    validate_element,
)

__all__ = [
    "COMPOSITION_SCHEMA",
    "COMPOSITION_VERSION",
    "TEXT",
    "IMAGE",
    "DOCUMENT",
    "ELEMENT_KINDS",
    "MARGINS",
    "PAGE",
    "BLEED",
    "REFERENCE_FRAMES",
    "normalize_kind",
    "normalize_reference_frame",
    "frame_bounds",
    "source_reference",
    "new_element",
    "validate_element",
    "element_by_id",
    "add_element",
    "update_element_geometry",
    "remove_element",
    "composition_issues",
]