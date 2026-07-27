from __future__ import annotations

import customtkinter as ctk

from src.theme.colors import Colors
from src.theme.fonts import Fonts


class SidebarButton(ctk.CTkButton):
    """
    Bouton utilisé dans la barre latérale.
    """

    HEIGHT = 44
    CORNER_RADIUS = 10

    def __init__(
        self,
        parent,
        text: str,
        command=None,
    ) -> None:

        super().__init__(
            parent,
            text=text,
            command=command,
            height=self.HEIGHT,
            corner_radius=self.CORNER_RADIUS,
            fg_color=Colors.BUTTON,
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            font=Fonts.NORMAL,
            anchor="w",
        )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"SidebarButton("
            f"text={self.cget('text')!r})"
        )