from __future__ import annotations

from src.interface import InterfacePrincipale


class GenerateurFichesApp:
    """
    Point d'entrée de l'application.
    """

    def __init__(self) -> None:

        self.interface = InterfacePrincipale()

    # ==========================================================
    # Exécution
    # ==========================================================

    def lancer(self) -> None:

        self.interface.lancer()

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return "GenerateurFichesApp()"


def main() -> None:

    GenerateurFichesApp().lancer()


if __name__ == "__main__":
    main()