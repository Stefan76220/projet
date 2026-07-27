from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(slots=True, frozen=True)
class Style:
    """
    Classe de base de tous les styles du moteur graphique.

    Un style est une valeur immuable décrivant uniquement
    l'apparence d'un objet graphique.
    """

    enabled: bool = True
    visible: bool = True
    opacity: float = 1.0

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def copy(
        self,
        **changes,
    ) -> "Style":

        return replace(self, **changes)

    def with_opacity(
        self,
        opacity: float,
    ) -> "Style":

        return self.copy(opacity=opacity)

    def enable(self) -> "Style":

        return self.copy(enabled=True)

    def disable(self) -> "Style":

        return self.copy(enabled=False)

    def show(self) -> "Style":

        return self.copy(visible=True)

    def hide(self) -> "Style":

        return self.copy(visible=False)