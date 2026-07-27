from __future__ import annotations


class Fonts:
    """
    Polices utilisées dans toute l'application.
    """

    FAMILY = "Segoe UI"

    # ==========================================================
    # Titres
    # ==========================================================

    TITLE = (FAMILY, 28, "bold")
    H1 = (FAMILY, 22, "bold")
    H2 = (FAMILY, 18, "bold")

    # ==========================================================
    # Texte courant
    # ==========================================================

    NORMAL = (FAMILY, 14)
    SMALL = (FAMILY, 12)

    # ==========================================================
    # Utilitaires
    # ==========================================================

    @classmethod
    def all(cls) -> dict[str, tuple]:
        """
        Retourne toutes les polices définies.
        """

        return {
            name: value
            for name, value in vars(cls).items()
            if name.isupper()
        }