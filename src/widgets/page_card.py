from __future__ import annotations

import traceback
from datetime import datetime

import customtkinter as ctk

from src.theme.colors import Colors
from src.theme.fonts import Fonts


class PageCard(ctk.CTkFrame):
    """
    Carte éditoriale représentant une page du document.
    """

    def __init__(
        self,
        parent,
        page: dict,
        on_open=None,
    ) -> None:

        super().__init__(
            parent,
            fg_color=Colors.CARD,
            border_width=1,
            border_color=Colors.BORDER,
            corner_radius=12,
        )

        self.page = page
        self.on_open = on_open

        self.grid_columnconfigure(1, weight=1)

        self._create_color_marker()
        self._create_identity_block()
        self._create_information_block()
        self._create_actions()

    # ==========================================================
    # Construction
    # ==========================================================

    def _create_color_marker(self) -> None:

        color = self.page.get(
            "couleur",
            "#D9D4C7",
        )

        marker = ctk.CTkFrame(
            self,
            width=8,
            fg_color=color,
            corner_radius=8,
        )

        marker.grid(
            row=0,
            column=0,
            rowspan=3,
            sticky="ns",
            padx=(12, 10),
            pady=12,
        )

        marker.grid_propagate(False)

    def _create_identity_block(self) -> None:

        identity = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        identity.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(0, 15),
            pady=(14, 4),
        )

        identity.grid_columnconfigure(0, weight=1)

        number = self._page_number()

        title = self.page.get(
            "nom",
            f"Page {number:03d}",
        )

        icon = self.page.get(
            "icone",
            "📄",
        )

        locked = bool(
            self.page.get(
                "verrouillee",
                False,
            )
        )

        lock_icon = "  🔒" if locked else ""

        ctk.CTkLabel(
            identity,
            text=f"{icon}  {title}{lock_icon}",
            font=Fonts.H2,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="ew",
        )

        page_type = self.page.get(
            "type",
            "Page vide",
        )

        ctk.CTkLabel(
            identity,
            text=page_type,
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
        ).grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(2, 0),
        )

    def _create_information_block(self) -> None:

        information = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        information.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(0, 15),
            pady=(5, 12),
        )

        information.grid_columnconfigure(1, weight=1)
        information.grid_columnconfigure(3, weight=1)

        state = self.page.get(
            "etat",
            "Brouillon",
        )

        modified = self._format_date(
            self.page.get(
                "date_modification",
                "",
            )
        )

        created = self._format_date(
            self.page.get(
                "date_creation",
                "",
            )
        )

        self._create_info_pair(
            information,
            row=0,
            column=0,
            label="État",
            value=state,
        )

        self._create_info_pair(
            information,
            row=0,
            column=2,
            label="Modification",
            value=modified,
        )

        self._create_info_pair(
            information,
            row=1,
            column=0,
            label="Création",
            value=created,
        )

        self._create_info_pair(
            information,
            row=1,
            column=2,
            label="Numéro",
            value=f"{self._page_number():03d}",
        )

    def _create_info_pair(
        self,
        parent,
        row: int,
        column: int,
        label: str,
        value: str,
    ) -> None:

        ctk.CTkLabel(
            parent,
            text=f"{label} :",
            font=Fonts.SMALL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
        ).grid(
            row=row,
            column=column,
            sticky="w",
            padx=(0, 6),
            pady=2,
        )

        ctk.CTkLabel(
            parent,
            text=value,
            font=Fonts.SMALL,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(
            row=row,
            column=column + 1,
            sticky="w",
            padx=(0, 24),
            pady=2,
        )

    def _create_actions(self) -> None:

        actions = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        actions.grid(
            row=0,
            column=2,
            rowspan=2,
            sticky="e",
            padx=(0, 18),
            pady=18,
        )

        ctk.CTkButton(
            actions,
            text="Ouvrir",
            width=110,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            command=self.open_page,
        ).grid(
            row=0,
            column=0,
            pady=(0, 8),
        )

        ctk.CTkButton(
            actions,
            text="⋯",
            width=110,
            fg_color=Colors.BUTTON,
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            command=self._future_actions,
        ).grid(
            row=1,
            column=0,
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

    def _future_actions(self) -> None:
        """
        Emplacement réservé aux futures actions :
        renommer, dupliquer, verrouiller et supprimer.
        """

        return

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def _page_number(self) -> int:

        try:
            return int(
                self.page.get(
                    "numero",
                    0,
                )
            )

        except (TypeError, ValueError):
            return 0

    @staticmethod
    def _format_date(value: str) -> str:

        if not value:
            return "Non renseignée"

        try:
            parsed = datetime.fromisoformat(value)
            return parsed.strftime("%d/%m/%Y à %H:%M")

        except (TypeError, ValueError):
            return str(value)

    def __repr__(self) -> str:

        return (
            f"PageCard("
            f"numero={self._page_number()})"
        )