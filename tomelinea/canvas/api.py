"""Contrat Canvas commun de TomeLinea V5.

Cette couche traduit un document interne vers l'entree Canvas.
Elle ne cree aucun widget, ne calcule aucune pagination et ne devient
jamais une seconde verite du Livre.

V5-04 conserve l'implementation V4 gelee par equivalence.
"""

from src.v4.canvas_contract import (
    CANVAS_SCHEMA,
    CANVAS_SCHEMA_VERSION,
    ENGINE_NAME,
    ENGINE_VERSION,
    PHASE2_SCHEMA,
    CanvasContractResult as ContractResult,
    build_canvas_contract as build_contract,
)

__all__ = [
    "PHASE2_SCHEMA",
    "CANVAS_SCHEMA",
    "CANVAS_SCHEMA_VERSION",
    "ENGINE_NAME",
    "ENGINE_VERSION",
    "ContractResult",
    "build_contract",
]