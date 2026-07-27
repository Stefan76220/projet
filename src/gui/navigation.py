from __future__ import annotations

import customtkinter as ctk

from src.theme.colors import Colors
from src.theme.fonts import Fonts
from src.theme.spacing import Spacing
from src.widgets.sidebar_button import SidebarButton


class Navigation:
    """
    Barre de navigation principale.
    """

    def __init__(self, parent) -> None:

        self.frame = ctk.CTkFrame(
            parent,
            width=250,
            fg_color=Colors.SIDEBAR,
            corner_radius=0,
        )

        self.frame.grid(
            row=0,
            column=0,
            sticky="ns",
        )

        self.frame.grid_propagate(False)

        self._create_header()
        self._create_menu()

    # ==========================================================
    # Construction
    # ==========================================================

    def _create_header(self) -> None:

        ctk.CTkLabel(
            self.frame,
            text="Générateur",
            font=Fonts.H1,
            text_color=Colors.TEXT,
        ).pack(
            pady=(Spacing.XL, 2),
        )

        ctk.CTkLabel(
            self.frame,
            text="de livres",
            font=Fonts.SMALL,
            text_color=Colors.TEXT_LIGHT,
        ).pack(
            pady=(0, Spacing.XL),
        )

    def _create_menu(self) -> None:

        buttons = (
            "📁 Projet",
            "🌿 Fiches",
            "🖼 Images",
            "📄 Mise en page",
            "✔ Vérification",
            "📦 Export",
        )

        for text in buttons:

            SidebarButton(
                self.frame,
                text=text,
            ).pack(
                fill="x",
                padx=Spacing.SM,
                pady=5,
            )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return "Navigation()"