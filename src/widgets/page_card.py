from __future__ import annotations

import traceback

from src.widgets.card import Card


class PageCard(Card):
    """
    Carte représentant une page.
    """

    def __init__(
        self,
        parent,
        page,
        on_open=None,
    ) -> None:

        self.page = page
        self.on_open = on_open

        number = page.get(
            "numero",
            0,
        )

        super().__init__(
            parent=parent,
            icon="📄",
            title=f"Page {number:03d}",
            subtitle="Page vide",
            infos=[
                "État : Brouillon",
            ],
            action_text="Ouvrir",
            action_command=self.open_page,
        )

    # ==========================================================
    # Actions
    # ==========================================================

    def open_page(self) -> None:

        if self.on_open is None:
            return

        try:

            self.on_open(
                self.page,
            )

        except Exception:

            traceback.print_exc()

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"PageCard("
            f"numero={self.page.get('numero', 0)})"
        )