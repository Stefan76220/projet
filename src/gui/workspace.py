import customtkinter as ctk

from src.theme.colors import Colors
from src.theme.fonts import Fonts
from src.theme.spacing import Spacing


class Workspace:

    def __init__(self, parent):

        print(">>> NOUVEAU WORKSPACE CHARGÉ <<<")

        self.frame = ctk.CTkFrame(
            parent,
            fg_color=Colors.WINDOW,
            corner_radius=0
        )

        self.frame.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.create_dashboard()

    def create_dashboard(self):

        header = ctk.CTkFrame(
            self.frame,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=Spacing.XL,
            pady=(Spacing.XL, Spacing.LG)
        )

        ctk.CTkLabel(
            header,
            text="Bienvenue",
            font=Fonts.TITLE,
            text_color=Colors.TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Sélectionnez un module pour commencer votre travail.",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT
        ).pack(anchor="w", pady=(5, 0))

        grid = ctk.CTkFrame(
            self.frame,
            fg_color="transparent"
        )

        grid.pack(
            fill="both",
            expand=True,
            padx=Spacing.XL,
            pady=(0, Spacing.XL)
        )

        modules = [
            ("📁", "Projet", "Créer, ouvrir ou enregistrer un projet"),
            ("📚", "Documents", "Créer et organiser les documents"),
            ("🖼️", "Ressources", "Images, illustrations, icônes..."),
            ("🎨", "Modèles", "Choisir la présentation graphique"),
            ("📄", "Génération", "Construire les pages"),
            ("📦", "Export", "PDF, images et impression")
        ]

        for i, module in enumerate(modules):

            ligne = i // 2
            colonne = i % 2

            carte = self.create_card(
                grid,
                *module
            )

            carte.grid(
                row=ligne,
                column=colonne,
                padx=15,
                pady=15,
                sticky="nsew"
            )

        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        grid.grid_rowconfigure(0, weight=1)
        grid.grid_rowconfigure(1, weight=1)
        grid.grid_rowconfigure(2, weight=1)

    def create_card(self, parent, icon, title, description):

        card = ctk.CTkFrame(
            parent,
            fg_color=Colors.CARD,
            corner_radius=15,
            border_width=1,
            border_color=Colors.BORDER
        )

        ctk.CTkLabel(
            card,
            text=icon,
            font=("Segoe UI Emoji", 34)
        ).pack(
            anchor="w",
            padx=25,
            pady=(20, 5)
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=Fonts.H2,
            text_color=Colors.TEXT
        ).pack(
            anchor="w",
            padx=25
        )

        ctk.CTkLabel(
            card,
            text=description,
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
            justify="left",
            wraplength=260
        ).pack(
            anchor="w",
            padx=25,
            pady=(10, 20)
        )

        return card