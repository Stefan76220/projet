"""Contrat d'architecture TomeLinea V5.

La V4 gelée reste la référence fonctionnelle, mais V5-28 ouvre le nouveau
parcours séquentiel : Source -> TLDocument -> métiers successifs -> Book.

``TLDocument`` est le manuscrit logique éditable, indépendant des pages et du
moteur d'affichage. ``Book`` devient l'état composé/paginé produit plus tard.

Chaque métier agit seul, avec une responsabilité limitée. Une décision tardive
invalide seulement les étapes qui en dépendent.
"""

V5_ARCHITECTURE_VERSION = 2

PRINCIPLES = (
    "single_book_truth",
    "stable_ids",
    "shared_navigation",
    "survol_uses_navigation",
    "source_separate_from_composition",
    "deterministic_rule_engine",
    "multi_project_types",
    "logical_document_before_book",
    "sequential_editorial_pipeline",
    "stage_scoped_mutations",
    "targeted_invalidation",
)
