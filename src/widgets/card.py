from __future__ import annotations

import customtkinter as ctk

from src.theme.colors import Colors
from src.theme.fonts import Fonts


class Card(ctk.CTkFrame):
    """
    Carte générique utilisée dans l'interface.
    """

    def __init__(
        self,
        parent,
        icon: str = "",
        title: str = "",
        subtitle: str = "",
        infos=None,
        action_text: str = "Ouvrir",
        action_command=None,
    ) -> None:

        super().__init__(
            parent,
            fg_color=Colors.CARD,
            border_width=1,
            border_color=Colors.BORDER,
            corner_radius=12,
        )

        self.grid_columnconfigure(
            0,
            weight=1,
        )

        infos = infos or []

        self._create_title(
            icon,
            title,
        )

        self._create_subtitle(
            subtitle,
        )

        self._create_infos(
            infos,
        )

        self._create_button(
            action_text,
            action_command,
            len(infos),
        )

    # ==========================================================
    # Construction
    # ==========================================================

    def _create_title(
        self,
        icon: str,
        title: str,
    ) -> None:

        ctk.CTkLabel(
            self,
            text=f"{icon} {title}",
            font=Fonts.H2,
            text_color=Colors.TEXT,
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=20,
            pady=(15, 5),
        )

    def _create_subtitle(
        self,
        subtitle: str,
    ) -> None:

        ctk.CTkLabel(
            self,
            text=subtitle,
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=20,
        )

    def _create_infos(
        self,
        infos: list[str],
    ) -> None:

        row = 2

        for info in infos:

            ctk.CTkLabel(
                self,
                text=info,
                font=Fonts.NORMAL,
                text_color=Colors.TEXT_LIGHT,
            ).grid(
                row=row,
                column=0,
                sticky="w",
                padx=20,
            )

            row += 1

    def _create_button(
        self,
        text: str,
        command,
        info_count: int,
    ) -> None:

        ctk.CTkButton(
            self,
            text=text,
            width=120,
            command=command,
        ).grid(
            row=0,
            column=1,
            rowspan=max(3, info_count + 2),
            padx=20,
            pady=20,
        )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return f"{self.__class__.__name__}()"