"""API de persistance des decisions de TomeLinea V5.

V5-03 n'ajoute aucun nouveau moteur de stockage.
Elle expose le moteur V4 gele derriere des noms V5 neutres.

Le contrat conserve :
- decisions indexees par identifiants stables ;
- empreinte de la Source ;
- aucun changement de la Source ;
- ecriture atomique de l'etat ;
- remise a zero des decisions si la Source ne correspond plus.
"""

from src.v4.editorial_persistence import (
    SCHEMA as EDITORIAL_STATE_SCHEMA,
    decision_key,
    load_editorial_state as load_decision_state,
    persisted_choices_for_plan as choices_for_plan,
    record_editorial_choice as record_choice,
    save_editorial_state as save_decision_state,
    source_fingerprint,
)

__all__ = [
    "EDITORIAL_STATE_SCHEMA",
    "source_fingerprint",
    "decision_key",
    "load_decision_state",
    "save_decision_state",
    "record_choice",
    "choices_for_plan",
]