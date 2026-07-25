import customtkinter as ctk

from src.theme.colors import Colors
from src.theme.fonts import Fonts


class Card(ctk.CTkFrame):

    def __init__(
        self,
        parent,
        icon="",
        title="",
        subtitle="",
        infos=None,
        action_text="Ouvrir",
        action_command=None
    ):

        super().__init__(
            parent,
            fg_color=Colors.CARD,
            border_width=1,
            border_color=Colors.BORDER,
            corner_radius=12
        )

        if infos is None:
            infos = []

        self.grid_columnconfigure(0, weight=1)

        # ------------------------------
        # Titre
        # ------------------------------

        ctk.CTkLabel(
            self,
            text=f"{icon} {title}",
            font=Fonts.H2,
            text_color=Colors.TEXT
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=(15, 5)
        )

        # ------------------------------
        # Sous-titre
        # ------------------------------

        ctk.CTkLabel(
            self,
            text=subtitle,
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=20
        )

        # ------------------------------
        # Informations
        # ------------------------------

        ligne = 2

        for info in infos:

            ctk.CTkLabel(
                self,
                text=info,
                font=Fonts.NORMAL,
                text_color=Colors.TEXT_LIGHT
            ).grid(
                row=ligne,
                column=0,
                sticky="w",
                padx=20
            )

            ligne += 1

        # ------------------------------
        # Bouton
        # ------------------------------

        ctk.CTkButton(
            self,
            text=action_text,
            width=120,
            command=action_command
        ).grid(
            row=0,
            column=1,
            rowspan=max(3, ligne),
            padx=20,
            pady=20
        )