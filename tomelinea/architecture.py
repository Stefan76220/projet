"""Contrat minimal du socle TomeLinea V5.

Ce fichier ne contient aucune logique metier.
Il fige uniquement les principes de migration valides :
- la V4 gelee reste la reference fonctionnelle ;
- une seule verite pour le Livre ;
- identifiants stables independants des numeros de page ;
- Navigation partagee par tous les outils ;
- Survol client de Navigation, jamais moteur de page ;
- Source distincte des decisions de composition ;
- aucune dependance obligatoire a une IA.
"""

V5_ARCHITECTURE_VERSION = 1

PRINCIPLES = (
    "single_book_truth",
    "stable_ids",
    "shared_navigation",
    "survol_uses_navigation",
    "source_separate_from_composition",
    "deterministic_rule_engine",
    "multi_project_types",
)