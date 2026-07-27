from __future__ import annotations

import customtkinter as ctk

from src.theme.colors import Colors
from src.theme.fonts import Fonts
from src.theme.spacing import Spacing


class DashboardView:
    """
    Vue d'accueil de l'application.
    """

    MODULES = (
        ("📁", "Projet", "Créer, ouvrir ou enregistrer un projet"),
        ("📚", "Documents", "Créer et organiser les documents"),
        ("🖼️", "Ressources", "Images, illustrations, icônes..."),
        ("🎨", "Modèles", "Choisir la présentation graphique"),
        ("📄", "Génération", "Construire les pages"),
        ("📦", "Export", "PDF, images et impression"),
    )

    def __init__(
        self,
        parent,
    ) -> None:

        self.parent = parent

    # ==========================================================
    # Affichage
    # ==========================================================

    def show(self) -> None:

        header = self._create_header()
        header.pack(
            fill="x",
            padx=Spacing.XL,
            pady=(Spacing.XL, Spacing.LG),
        )

        grid = self._create_grid()
        grid.pack(
            fill="both",
            expand=True,
            padx=Spacing.XL,
            pady=(0, Spacing.XL),
        )

    # ==========================================================
    # Construction
    # ==========================================================

    def _create_header(self) -> ctk.CTkFrame:

        header = ctk.CTkFrame(
            self.parent,
            fg_color="transparent",
        )

        ctk.CTkLabel(
            header,
            text="Bienvenue",
            font=Fonts.TITLE,
            text_color=Colors.TEXT,
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Sélectionnez un module pour commencer votre travail.",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
        ).pack(
            anchor="w",
            pady=(5, 0),
        )

        return header

    def _create_grid(self) -> ctk.CTkFrame:

        grid = ctk.CTkFrame(
            self.parent,
            fg_color="transparent",
        )

        for index, module in enumerate(self.MODULES):

            row = index // 2
            column = index % 2

            card = self._create_card(
                grid,
                *module,
            )

            card.grid(
                row=row,
                column=column,
                padx=15,
                pady=15,
                sticky="nsew",
            )

        for column in range(2):
            grid.grid_columnconfigure(
                column,
                weight=1,
            )

        for row in range(3):
            grid.grid_rowconfigure(
                row,
                weight=1,
            )

        return grid

    def _create_card(
        self,
        parent,
        icon: str,
        title: str,
        description: str,
    ) -> ctk.CTkFrame:

        card = ctk.CTkFrame(
            parent,
            fg_color=Colors.CARD,
            corner_radius=15,
            border_width=1,
            border_color=Colors.BORDER,
        )

        ctk.CTkLabel(
            card,
            text=icon,
            font=("Segoe UI Emoji", 34),
        ).pack(
            anchor="w",
            padx=25,
            pady=(20, 5),
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=Fonts.H2,
            text_color=Colors.TEXT,
        ).pack(
            anchor="w",
            padx=25,
        )

        ctk.CTkLabel(
            card,
            text=description,
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
            justify="left",
            wraplength=260,
        ).pack(
            anchor="w",
            padx=25,
            pady=(10, 20),
        )

        return card

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return "DashboardView()"