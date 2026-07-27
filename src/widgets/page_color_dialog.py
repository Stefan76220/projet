from __future__ import annotations

import customtkinter as ctk

from src.theme.colors import Colors
from src.theme.fonts import Fonts


EDITORIAL_COLORS = [
    {
        "name": "Sable",
        "value": "#C9A66B",
    },
    {
        "name": "Terre cuite",
        "value": "#B76E56",
    },
    {
        "name": "Rouge brique",
        "value": "#9F5147",
    },
    {
        "name": "Rose ancien",
        "value": "#B77A87",
    },
    {
        "name": "Prune",
        "value": "#806078",
    },
    {
        "name": "Violet",
        "value": "#75628A",
    },
    {
        "name": "Bleu ardoise",
        "value": "#607D96",
    },
    {
        "name": "Bleu profond",
        "value": "#496D89",
    },
    {
        "name": "Bleu pétrole",
        "value": "#477C7A",
    },
    {
        "name": "Vert sauge",
        "value": "#718B72",
    },
    {
        "name": "Vert forêt",
        "value": "#52705A",
    },
    {
        "name": "Ocre",
        "value": "#B58A45",
    },
]


class PageColorDialog(ctk.CTkToplevel):
    """
    Fenêtre de sélection de la couleur éditoriale d'une page.
    """

    def __init__(
        self,
        parent,
        current_color: str,
        on_validate,
    ) -> None:

        super().__init__(parent)

        self.on_validate = on_validate
        self.current_color = current_color
        self.selected_color = current_color
        self.color_buttons: dict[str, ctk.CTkButton] = {}

        self.title("Couleur éditoriale")
        self.geometry("560x465")
        self.resizable(False, False)

        self.transient(
            parent.winfo_toplevel(),
        )

        self.grab_set()

        self.configure(
            fg_color=Colors.WINDOW,
        )

        self.protocol(
            "WM_DELETE_WINDOW",
            self.cancel,
        )

        self._create_content()

        self.after(
            50,
            self._center_window,
        )

    # ==========================================================
    # Construction
    # ==========================================================

    def _create_content(self) -> None:

        container = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        container.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=22,
        )

        ctk.CTkLabel(
            container,
            text="Couleur éditoriale",
            font=Fonts.H2,
            text_color=Colors.TEXT,
            anchor="w",
        ).pack(
            fill="x",
            pady=(0, 8),
        )

        ctk.CTkLabel(
            container,
            text=(
                "Choisis la couleur utilisée pour identifier "
                "cette page dans le document."
            ),
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
            justify="left",
            wraplength=500,
        ).pack(
            fill="x",
            pady=(0, 18),
        )

        self.preview_frame = ctk.CTkFrame(
            container,
            height=58,
            fg_color=Colors.CARD,
            border_width=1,
            border_color=Colors.BORDER,
            corner_radius=10,
        )

        self.preview_frame.pack(
            fill="x",
            pady=(0, 18),
        )

        self.preview_frame.pack_propagate(False)

        self.preview_marker = ctk.CTkFrame(
            self.preview_frame,
            width=12,
            fg_color=self.selected_color,
            corner_radius=6,
        )

        self.preview_marker.pack(
            side="left",
            fill="y",
            padx=(14, 12),
            pady=10,
        )

        self.preview_marker.pack_propagate(False)

        self.preview_label = ctk.CTkLabel(
            self.preview_frame,
            text=self._selected_color_text(),
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
            anchor="w",
        )

        self.preview_label.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 14),
        )

        palette = ctk.CTkFrame(
            container,
            fg_color="transparent",
        )

        palette.pack(
            fill="both",
            expand=True,
        )

        for column in range(3):
            palette.grid_columnconfigure(
                column,
                weight=1,
                uniform="color",
            )

        for index, color_data in enumerate(EDITORIAL_COLORS):

            row = index // 3
            column = index % 3

            color_value = color_data["value"]
            color_name = color_data["name"]

            button = ctk.CTkButton(
                palette,
                text=color_name,
                height=52,
                corner_radius=9,
                border_width=3,
                border_color=self._button_border_color(
                    color_value,
                ),
                fg_color=color_value,
                hover_color=color_value,
                text_color=self._text_color_for_background(
                    color_value,
                ),
                font=Fonts.NORMAL,
                command=lambda value=color_value: (
                    self.select_color(value)
                ),
            )

            button.grid(
                row=row,
                column=column,
                sticky="ew",
                padx=5,
                pady=5,
            )

            self.color_buttons[color_value] = button

        buttons = ctk.CTkFrame(
            container,
            fg_color="transparent",
        )

        buttons.pack(
            fill="x",
            pady=(20, 0),
        )

        ctk.CTkButton(
            buttons,
            text="Annuler",
            width=110,
            fg_color=Colors.BUTTON,
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            command=self.cancel,
        ).pack(
            side="right",
            padx=(8, 0),
        )

        ctk.CTkButton(
            buttons,
            text="Valider",
            width=110,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            command=self.validate,
        ).pack(
            side="right",
        )

    # ==========================================================
    # Sélection
    # ==========================================================

    def select_color(
        self,
        color_value: str,
    ) -> None:

        self.selected_color = color_value

        self.preview_marker.configure(
            fg_color=color_value,
        )

        self.preview_label.configure(
            text=self._selected_color_text(),
        )

        for value, button in self.color_buttons.items():

            button.configure(
                border_color=self._button_border_color(
                    value,
                )
            )

    def _button_border_color(
        self,
        color_value: str,
    ) -> str:

        if color_value == self.selected_color:
            return Colors.TEXT

        return color_value

    def _selected_color_text(self) -> str:

        for color_data in EDITORIAL_COLORS:

            if color_data["value"] == self.selected_color:

                return (
                    f'{color_data["name"]}  ·  '
                    f'{color_data["value"]}'
                )

        return self.selected_color

    # ==========================================================
    # Actions
    # ==========================================================

    def validate(self) -> None:

        if not self.selected_color:
            return

        try:
            self.on_validate(
                self.selected_color,
            )

        finally:
            self.destroy()

    def cancel(self) -> None:

        self.destroy()

    # ==========================================================
    # Utilitaires
    # ==========================================================

    @staticmethod
    def _text_color_for_background(
        color_value: str,
    ) -> str:

        value = color_value.lstrip("#")

        try:
            red = int(value[0:2], 16)
            green = int(value[2:4], 16)
            blue = int(value[4:6], 16)

        except (TypeError, ValueError):
            return "#FFFFFF"

        brightness = (
            red * 299
            + green * 587
            + blue * 114
        ) / 1000

        if brightness >= 145:
            return "#202020"

        return "#FFFFFF"

    def _center_window(self) -> None:

        self.update_idletasks()

        parent = self.master.winfo_toplevel()

        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_width = parent.winfo_width()
        parent_height = parent.winfo_height()

        width = self.winfo_width()
        height = self.winfo_height()

        x = parent_x + max(
            0,
            (parent_width - width) // 2,
        )

        y = parent_y + max(
            0,
            (parent_height - height) // 2,
        )

        self.geometry(
            f"+{x}+{y}",
        )