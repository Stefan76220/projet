from __future__ import annotations


class Spacing:
    """
    Espacements normalisés de l'application.
    """

    # ==========================================================
    # Espacements
    # ==========================================================

    XS = 5
    SM = 10
    MD = 20
    LG = 30
    XL = 40
    XXL = 60

    # ==========================================================
    # Utilitaires
    # ==========================================================

    @classmethod
    def all(cls) -> dict[str, int]:
        """
        Retourne tous les espacements définis.
        """

        return {
            name: value
            for name, value in vars(cls).items()
            if name.isupper()
        }