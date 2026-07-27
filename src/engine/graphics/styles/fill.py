from __future__ import annotations

from dataclasses import dataclass

from .style import Style


@dataclass(slots=True, frozen=True)
class Fill(Style):
    """
    Décrit le remplissage d'un objet graphique.
    """

    color: str = "#FFFFFF"

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def with_color(
        self,
        color: str,
    ) -> "Fill":

        return self.copy(color=color)