from __future__ import annotations

from src.core.application import Application


def main() -> None:
    """
    Point d'entrée de l'application.
    """

    application = Application()
    application.run()


if __name__ == "__main__":
    main()