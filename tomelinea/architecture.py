"""Contrat d'architecture TomeLinea V5.

V5 est maintenant séquentielle :

Source intacte -> copie de travail -> TLDocument -> métiers successifs ->
moteur bureautique -> projection rendue.

TLDocument porte la compréhension logique et les identifiants stables.
Le document de travail porte les modifications réelles.
LibreOffice calcule la mise en page et la pagination derrière un adaptateur TL.
Le rendu PDF est une projection d'affichage, jamais le document de travail.

Structure logique et position physique sont distinctes :
reclasser une page (ex. Corps -> Liminaires) ne déplace pas son contenu et ne
déclenche pas de recomposition. Un déplacement physique dans le livre, lui,
modifie le document de travail et invalide la composition/pagination concernée.
"""

V5_ARCHITECTURE_VERSION = 3

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
    "logical_structure_independent_of_layout",
    "office_layout_engine_behind_adapter",
    "render_is_projection_not_truth",
)