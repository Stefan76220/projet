from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import shutil
import tkinter as tk
from tkinter import colorchooser, filedialog, font as tkfont, messagebox

import customtkinter as ctk

from PIL import Image, ImageOps, ImageTk

from src.core.document import Document
from src.engine.foundation import Point, Rect, Size
from src.engine.page_format import A4, A5, BOOK_16X24, BOOK_17X24
from src.gui.editor_canvas import CanvasObject, EditorCanvas
from src.gui.rulers.horizontal_ruler import HorizontalRuler
from src.gui.rulers.vertical_ruler import VerticalRuler
from src.gui.status_bar import StatusBar
from src.library.page_types.page_type_library import PageTypeLibrary
from src.theme.colors import Colors
from src.theme.fonts import Fonts


PAGE_FORMATS = {
    "A4": A4,
    "A5": A5,
    "16x24": BOOK_16X24,
    "16 × 24": BOOK_16X24,
    "17x24": BOOK_17X24,
    "17 × 24": BOOK_17X24,
}


# Chaque type éditorial reçoit une apparence stable. Ces couleurs sont
# volontairement douces afin de rester lisibles dans le chemin de fer.
PAGE_TYPE_APPEARANCES = {
    "Page vide": {
        "icone": "📄",
        "couleur": "#D9D4C7",
    },
    "Page de texte": {
        "icone": "📝",
        "couleur": "#B8C8D8",
    },
    "Page image": {
        "icone": "🖼",
        "couleur": "#C8B8D8",
    },
    "Page de chapitre": {
        "icone": "📖",
        "couleur": "#D8C3A5",
    },
    "Couverture": {
        "icone": "📕",
        "couleur": "#D8B4A0",
    },
    "Page de transition": {
        "icone": "◇",
        "couleur": "#B8D2C2",
    },
    "Table des matières": {
        "icone": "☷",
        "couleur": "#AFC8C8",
    },
    "Page d’illustration": {
        "icone": "🖼",
        "couleur": "#C6B7D8",
    },
    "Création libre": {
        "icone": "✦",
        "couleur": "#B7CBE0",
    },
    "Modèle": {
        "icone": "▦",
        "couleur": "#C8C8C8",
    },
}

FALLBACK_EDITORIAL_COLORS = (
    "#C4D4DF",
    "#C8D8C2",
    "#D8C7B8",
    "#CDC3DA",
    "#D4C5C5",
    "#C1D4D1",
)


class RenamePageDialog(ctk.CTkToplevel):
    """Boîte de dialogue fiable pour renommer la page courante."""

    def __init__(
        self,
        parent,
        current_name: str,
        on_validate,
    ) -> None:
        super().__init__(parent)

        self.on_validate = on_validate

        self.title("Renommer la page")
        self.geometry("460x220")
        self.resizable(False, False)
        self.configure(fg_color=Colors.WINDOW)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)

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
            text="Renommer la page",
            font=Fonts.H2,
            text_color=Colors.TEXT,
            anchor="w",
        ).pack(
            fill="x",
            pady=(0, 8),
        )

        ctk.CTkLabel(
            container,
            text="Saisis le nouveau nom de la page.",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
        ).pack(
            fill="x",
            pady=(0, 14),
        )

        self.name_entry = ctk.CTkEntry(
            container,
            height=40,
            font=Fonts.NORMAL,
            border_color=Colors.BORDER,
        )
        self.name_entry.pack(fill="x")
        self.name_entry.insert(0, current_name)
        self.name_entry.bind("<Return>", self.validate)
        self.name_entry.bind("<Escape>", self.cancel)

        buttons = ctk.CTkFrame(
            container,
            fg_color="transparent",
        )
        buttons.pack(
            fill="x",
            pady=(18, 0),
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
        ).pack(side="right")

        self.after(60, self._prepare_entry)
        self.after(80, self._center_window)

    def _prepare_entry(self) -> None:
        self.name_entry.focus_set()
        self.name_entry.select_range(0, "end")

    def _center_window(self) -> None:
        self.update_idletasks()

        parent = self.master.winfo_toplevel()
        x = parent.winfo_x() + max(
            0,
            (parent.winfo_width() - self.winfo_width()) // 2,
        )
        y = parent.winfo_y() + max(
            0,
            (parent.winfo_height() - self.winfo_height()) // 2,
        )

        self.geometry(f"+{x}+{y}")

    def validate(self, _event=None) -> None:
        new_name = self.name_entry.get().strip()

        if not new_name:
            self.name_entry.focus_set()
            return

        callback = self.on_validate
        self.grab_release()
        self.destroy()

        self.master.after_idle(
            lambda: callback(new_name)
        )

    def cancel(self, _event=None) -> None:
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()


class PageSetupDialog(ctk.CTkToplevel):
    """Réglages visuels du format, des marges et des fonds perdus."""

    FREE_FORMAT_LABEL = "Format libre"
    PREVIEW_WIDTH = 250
    PREVIEW_HEIGHT = 320

    def __init__(
        self,
        parent,
        page,
        on_validate,
    ) -> None:
        super().__init__(parent)

        self.page = page
        self.on_validate = on_validate
        self._preview_after_id = None
        self._dimension_widgets: dict[str, list[object]] = {}

        self.title("Format de la page")
        self.geometry("1080x680")
        self.minsize(1000, 640)
        self.resizable(True, True)
        self.configure(fg_color=Colors.WINDOW)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        current_format_mode = str(
            getattr(
                page,
                "format_mode",
                "preregle",
            )
        ).strip().lower()

        current_format = str(
            getattr(
                page,
                "format",
                "A5",
            )
        ).strip()

        preset_names = list(
            getattr(
                page,
                "FORMAT_PRESETS",
                {},
            ).keys()
        )

        selected_format = (
            self.FREE_FORMAT_LABEL
            if current_format_mode == "libre"
            else current_format
        )

        if selected_format not in preset_names:
            selected_format = self.FREE_FORMAT_LABEL

        self._format_values = preset_names + [
            self.FREE_FORMAT_LABEL
        ]

        self.format_var = tk.StringVar(
            value=selected_format,
        )
        self.orientation_var = tk.StringVar(
            value=str(
                getattr(
                    page,
                    "orientation",
                    "Portrait",
                )
            )
        )
        self.width_var = tk.StringVar(
            value=self._format_number(
                getattr(
                    page,
                    "width_mm",
                    148.0,
                )
            )
        )
        self.height_var = tk.StringVar(
            value=self._format_number(
                getattr(
                    page,
                    "height_mm",
                    210.0,
                )
            )
        )

        self.margin_top_var = tk.StringVar(
            value=self._format_number(
                getattr(
                    page,
                    "margin_top_mm",
                    15.0,
                )
            )
        )
        self.margin_bottom_var = tk.StringVar(
            value=self._format_number(
                getattr(
                    page,
                    "margin_bottom_mm",
                    15.0,
                )
            )
        )
        self.margin_inside_var = tk.StringVar(
            value=self._format_number(
                getattr(
                    page,
                    "margin_inside_mm",
                    15.0,
                )
            )
        )
        self.margin_outside_var = tk.StringVar(
            value=self._format_number(
                getattr(
                    page,
                    "margin_outside_mm",
                    15.0,
                )
            )
        )

        self.bleed_top_var = tk.StringVar(
            value=self._format_number(
                getattr(
                    page,
                    "bleed_top_mm",
                    0.0,
                )
            )
        )
        self.bleed_right_var = tk.StringVar(
            value=self._format_number(
                getattr(
                    page,
                    "bleed_right_mm",
                    0.0,
                )
            )
        )
        self.bleed_bottom_var = tk.StringVar(
            value=self._format_number(
                getattr(
                    page,
                    "bleed_bottom_mm",
                    0.0,
                )
            )
        )
        self.bleed_left_var = tk.StringVar(
            value=self._format_number(
                getattr(
                    page,
                    "bleed_left_mm",
                    0.0,
                )
            )
        )

        self.error_var = tk.StringVar(value="")
        self.preview_info_var = tk.StringVar(value="")

        self._build()
        self._install_preview_traces()
        self._refresh_dimension_state()
        self._draw_preview()

        self.after(80, self._center_window)

    # ==========================================================
    # Construction
    # ==========================================================

    def _build(self) -> None:
        container = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        container.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=20,
        )
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            container,
            text="Format, marges et fonds perdus",
            font=Fonts.H1,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="ew",
        )

        ctk.CTkLabel(
            container,
            text=(
                "Tous les réglages sont visibles sur une seule fenêtre. "
                "La vignette se met à jour immédiatement."
            ),
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
        ).grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(4, 14),
        )

        body = ctk.CTkFrame(
            container,
            fg_color="transparent",
        )
        body.grid(
            row=2,
            column=0,
            sticky="nsew",
        )
        body.grid_columnconfigure(0, weight=1)
        body.grid_columnconfigure(1, weight=0)
        body.grid_rowconfigure(0, weight=1)

        controls = ctk.CTkFrame(
            body,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color=Colors.BORDER,
        )
        controls.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 16),
        )
        controls.grid_columnconfigure(0, weight=1)
        controls.grid_rowconfigure(1, weight=1)

        self._build_format_section(
            controls,
            row=0,
            column=0,
        )

        lower_controls = ctk.CTkFrame(
            controls,
            fg_color="transparent",
        )
        lower_controls.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=6,
            pady=(0, 6),
        )
        lower_controls.grid_columnconfigure(0, weight=1, uniform="page_setup")
        lower_controls.grid_columnconfigure(1, weight=1, uniform="page_setup")
        lower_controls.grid_rowconfigure(0, weight=1)

        self._build_margins_section(
            lower_controls,
            row=0,
            column=0,
        )
        self._build_bleed_section(
            lower_controls,
            row=0,
            column=1,
        )

        self._build_preview(body)

        footer = ctk.CTkFrame(
            container,
            fg_color="transparent",
        )
        footer.grid(
            row=3,
            column=0,
            sticky="ew",
            pady=(14, 0),
        )
        footer.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            footer,
            textvariable=self.error_var,
            font=Fonts.SMALL,
            text_color="#B42318",
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 12),
        )

        ctk.CTkButton(
            footer,
            text="Annuler",
            width=110,
            height=36,
            fg_color=Colors.BUTTON,
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            command=self.cancel,
        ).grid(
            row=0,
            column=1,
            padx=(0, 8),
        )

        ctk.CTkButton(
            footer,
            text="Appliquer",
            width=120,
            height=36,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            command=self.validate,
        ).grid(
            row=0,
            column=2,
        )

    def _build_format_section(
        self,
        parent,
        *,
        row: int = 0,
        column: int = 0,
    ) -> None:
        section = self._section(
            parent,
            "Format de la page",
            row,
            column,
        )

        self._combo_control(
            section,
            label="Format",
            variable=self.format_var,
            values=self._format_values,
            row=0,
            column=0,
            command=self._on_format_changed,
        )
        self._combo_control(
            section,
            label="Orientation",
            variable=self.orientation_var,
            values=["Portrait", "Paysage"],
            row=0,
            column=1,
            command=self._on_orientation_changed,
        )

        self._number_control(
            section,
            key="width",
            label="Largeur",
            variable=self.width_var,
            row=1,
            column=0,
            minimum=1.0,
            step=1.0,
        )
        self._number_control(
            section,
            key="height",
            label="Hauteur",
            variable=self.height_var,
            row=1,
            column=1,
            minimum=1.0,
            step=1.0,
        )

    def _build_margins_section(
        self,
        parent,
        *,
        row: int = 0,
        column: int = 0,
    ) -> None:
        section = self._section(
            parent,
            "Marges de composition",
            row,
            column,
        )

        values = (
            ("margin_top", "Haute", self.margin_top_var),
            ("margin_bottom", "Basse", self.margin_bottom_var),
            ("margin_inside", "Intérieure", self.margin_inside_var),
            ("margin_outside", "Extérieure", self.margin_outside_var),
        )

        for index, (key, label, variable) in enumerate(values):
            self._number_control(
                section,
                key=key,
                label=label,
                variable=variable,
                row=index // 2,
                column=index % 2,
                minimum=0.0,
                step=1.0,
            )

    def _build_bleed_section(
        self,
        parent,
        *,
        row: int = 0,
        column: int = 0,
    ) -> None:
        section = self._section(
            parent,
            "Fonds perdus",
            row,
            column,
        )

        values = (
            ("bleed_top", "Haut", self.bleed_top_var),
            ("bleed_right", "Droite", self.bleed_right_var),
            ("bleed_bottom", "Bas", self.bleed_bottom_var),
            ("bleed_left", "Gauche", self.bleed_left_var),
        )

        for index, (key, label, variable) in enumerate(values):
            self._number_control(
                section,
                key=key,
                label=label,
                variable=variable,
                row=index // 2,
                column=index % 2,
                minimum=0.0,
                step=1.0,
            )

    def _build_preview(self, parent) -> None:
        preview_frame = ctk.CTkFrame(
            parent,
            width=290,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color=Colors.BORDER,
        )
        preview_frame.grid(
            row=0,
            column=1,
            sticky="ns",
        )
        preview_frame.grid_propagate(False)

        ctk.CTkLabel(
            preview_frame,
            text="Aperçu",
            font=Fonts.H2,
            text_color=Colors.TEXT,
        ).pack(
            pady=(16, 8),
        )

        self.preview_canvas = tk.Canvas(
            preview_frame,
            width=self.PREVIEW_WIDTH,
            height=self.PREVIEW_HEIGHT,
            bg="#E7E9EC",
            highlightthickness=0,
        )
        self.preview_canvas.pack(
            padx=18,
            pady=(0, 8),
        )

        ctk.CTkLabel(
            preview_frame,
            textvariable=self.preview_info_var,
            font=Fonts.SMALL,
            text_color=Colors.TEXT_LIGHT,
            justify="center",
        ).pack(
            padx=14,
            pady=(0, 10),
        )

        legend = ctk.CTkFrame(
            preview_frame,
            fg_color="transparent",
        )
        legend.pack(
            padx=18,
            pady=(0, 14),
            fill="x",
        )

        self._legend_line(
            legend,
            color="#4F7FA3",
            text="Marges / zone de composition",
        )
        self._legend_line(
            legend,
            color="#C97945",
            text="Fonds perdus",
        )

    def _section(
        self,
        parent,
        title: str,
        row: int,
        column: int = 0,
    ) -> ctk.CTkFrame:
        section = ctk.CTkFrame(
            parent,
            fg_color="#F7F8FA",
            corner_radius=10,
        )
        section.grid(
            row=row,
            column=column,
            sticky="nsew",
            padx=6,
            pady=6,
        )
        section.grid_columnconfigure(0, weight=1)
        section.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            section,
            text=title,
            font=Fonts.H2,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=14,
            pady=(12, 6),
        )

        return section

    def _combo_control(
        self,
        parent,
        *,
        label: str,
        variable,
        values: list[str],
        row: int,
        column: int,
        command,
    ) -> None:
        frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )
        frame.grid(
            row=row + 1,
            column=column,
            sticky="ew",
            padx=(14 if column == 0 else 7, 14 if column == 1 else 7),
            pady=7,
        )
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame,
            text=label,
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 4),
        )

        combo = ctk.CTkComboBox(
            frame,
            values=values,
            variable=variable,
            state="readonly",
            command=command,
        )
        combo.grid(
            row=1,
            column=0,
            sticky="ew",
        )

    def _number_control(
        self,
        parent,
        *,
        key: str,
        label: str,
        variable,
        row: int,
        column: int,
        minimum: float,
        step: float,
    ) -> None:
        frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )
        frame.grid(
            row=row + 1,
            column=column,
            sticky="ew",
            padx=(14 if column == 0 else 7, 14 if column == 1 else 7),
            pady=7,
        )
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame,
            text=label,
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=(0, 4),
        )

        entry = ctk.CTkEntry(
            frame,
            textvariable=variable,
            height=36,
        )
        entry.grid(
            row=1,
            column=0,
            sticky="ew",
        )

        ctk.CTkLabel(
            frame,
            text="mm",
            width=28,
            font=Fonts.SMALL,
            text_color=Colors.TEXT_LIGHT,
        ).grid(
            row=1,
            column=1,
            padx=(6, 4),
        )

        buttons = ctk.CTkFrame(
            frame,
            fg_color="transparent",
            width=30,
        )
        buttons.grid(
            row=1,
            column=2,
            sticky="ns",
        )

        up_button = ctk.CTkButton(
            buttons,
            text="▲",
            width=28,
            height=16,
            corner_radius=5,
            fg_color=Colors.BUTTON,
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            font=(Fonts.FAMILY, 9),
            command=lambda: self._adjust_variable(
                variable,
                step,
                minimum,
            ),
        )
        up_button.pack(
            pady=(0, 2),
        )

        down_button = ctk.CTkButton(
            buttons,
            text="▼",
            width=28,
            height=16,
            corner_radius=5,
            fg_color=Colors.BUTTON,
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            font=(Fonts.FAMILY, 9),
            command=lambda: self._adjust_variable(
                variable,
                -step,
                minimum,
            ),
        )
        down_button.pack()

        entry.bind(
            "<MouseWheel>",
            lambda event: self._adjust_from_wheel(
                event,
                variable,
                step,
                minimum,
            ),
            add="+",
        )

        self._dimension_widgets[key] = [
            entry,
            up_button,
            down_button,
        ]

    @staticmethod
    def _legend_line(
        parent,
        *,
        color: str,
        text: str,
    ) -> None:
        row = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )
        row.pack(
            fill="x",
            pady=2,
        )

        mark = tk.Canvas(
            row,
            width=30,
            height=12,
            bg="#FFFFFF",
            highlightthickness=0,
        )
        mark.pack(
            side="left",
            padx=(0, 6),
        )
        mark.create_line(
            2,
            6,
            28,
            6,
            fill=color,
            width=2,
            dash=(5, 3),
        )

        ctk.CTkLabel(
            row,
            text=text,
            font=Fonts.SMALL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
        ).pack(
            side="left",
            fill="x",
            expand=True,
        )

    # ==========================================================
    # Ajustement visuel
    # ==========================================================

    def _install_preview_traces(self) -> None:
        variables = (
            self.format_var,
            self.orientation_var,
            self.width_var,
            self.height_var,
            self.margin_top_var,
            self.margin_bottom_var,
            self.margin_inside_var,
            self.margin_outside_var,
            self.bleed_top_var,
            self.bleed_right_var,
            self.bleed_bottom_var,
            self.bleed_left_var,
        )

        for variable in variables:
            variable.trace_add(
                "write",
                self._schedule_preview,
            )

    def _schedule_preview(self, *_args) -> None:
        if self._preview_after_id is not None:
            try:
                self.after_cancel(
                    self._preview_after_id
                )
            except tk.TclError:
                pass

        self._preview_after_id = self.after(
            20,
            self._draw_preview,
        )

    def _adjust_variable(
        self,
        variable,
        delta: float,
        minimum: float,
    ) -> None:
        try:
            current = self._parse_number(
                variable.get(),
                "valeur",
            )
        except ValueError:
            current = minimum

        value = max(
            minimum,
            current + delta,
        )
        variable.set(
            self._format_number(value)
        )
        self.error_var.set("")

    def _adjust_from_wheel(
        self,
        event,
        variable,
        step: float,
        minimum: float,
    ) -> str:
        delta = step if event.delta > 0 else -step
        self._adjust_variable(
            variable,
            delta,
            minimum,
        )
        return "break"

    def _draw_preview(self) -> None:
        self._preview_after_id = None

        try:
            width = self._parse_positive(
                self.width_var.get(),
                "largeur",
            )
            height = self._parse_positive(
                self.height_var.get(),
                "hauteur",
            )

            margin_top = self._parse_non_negative(
                self.margin_top_var.get(),
                "marge haute",
            )
            margin_bottom = self._parse_non_negative(
                self.margin_bottom_var.get(),
                "marge basse",
            )
            margin_inside = self._parse_non_negative(
                self.margin_inside_var.get(),
                "marge intérieure",
            )
            margin_outside = self._parse_non_negative(
                self.margin_outside_var.get(),
                "marge extérieure",
            )

            bleed_top = self._parse_non_negative(
                self.bleed_top_var.get(),
                "fond perdu haut",
            )
            bleed_right = self._parse_non_negative(
                self.bleed_right_var.get(),
                "fond perdu droit",
            )
            bleed_bottom = self._parse_non_negative(
                self.bleed_bottom_var.get(),
                "fond perdu bas",
            )
            bleed_left = self._parse_non_negative(
                self.bleed_left_var.get(),
                "fond perdu gauche",
            )

        except ValueError:
            return

        canvas = self.preview_canvas
        canvas.delete("all")

        total_width = width + bleed_left + bleed_right
        total_height = height + bleed_top + bleed_bottom

        available_width = self.PREVIEW_WIDTH - 42
        available_height = self.PREVIEW_HEIGHT - 46

        scale = min(
            available_width / max(total_width, 1.0),
            available_height / max(total_height, 1.0),
        )

        outer_width = total_width * scale
        outer_height = total_height * scale
        outer_x = (
            self.PREVIEW_WIDTH - outer_width
        ) / 2
        outer_y = (
            self.PREVIEW_HEIGHT - outer_height
        ) / 2

        page_x = outer_x + bleed_left * scale
        page_y = outer_y + bleed_top * scale
        page_width = width * scale
        page_height = height * scale

        if any(
            value > 0
            for value in (
                bleed_top,
                bleed_right,
                bleed_bottom,
                bleed_left,
            )
        ):
            canvas.create_rectangle(
                outer_x,
                outer_y,
                outer_x + outer_width,
                outer_y + outer_height,
                fill="#F5E5D8",
                outline="#C97945",
                width=2,
                dash=(6, 4),
            )

        canvas.create_rectangle(
            page_x + 5,
            page_y + 6,
            page_x + page_width + 5,
            page_y + page_height + 6,
            fill="#B7BCC2",
            outline="",
        )
        canvas.create_rectangle(
            page_x,
            page_y,
            page_x + page_width,
            page_y + page_height,
            fill="#FFFFFF",
            outline="#4B4F55",
            width=1,
        )

        is_verso = (
            int(
                getattr(
                    self.page,
                    "number",
                    1,
                )
            ) % 2 == 0
        )

        left_margin = (
            margin_outside
            if is_verso
            else margin_inside
        )
        right_margin = (
            margin_inside
            if is_verso
            else margin_outside
        )

        composition_width = (
            width - left_margin - right_margin
        )
        composition_height = (
            height - margin_top - margin_bottom
        )

        valid_composition = (
            composition_width > 0
            and composition_height > 0
        )

        guide_color = (
            "#4F7FA3"
            if valid_composition
            else "#B42318"
        )

        if valid_composition:
            comp_x = page_x + left_margin * scale
            comp_y = page_y + margin_top * scale
            comp_width = composition_width * scale
            comp_height = composition_height * scale

            canvas.create_rectangle(
                comp_x,
                comp_y,
                comp_x + comp_width,
                comp_y + comp_height,
                outline=guide_color,
                width=2,
                dash=(5, 3),
            )
        else:
            canvas.create_line(
                page_x,
                page_y,
                page_x + page_width,
                page_y + page_height,
                fill=guide_color,
                width=2,
            )
            canvas.create_line(
                page_x + page_width,
                page_y,
                page_x,
                page_y + page_height,
                fill=guide_color,
                width=2,
            )

        page_side = (
            "page gauche"
            if is_verso
            else "page droite"
        )

        self.preview_info_var.set(
            f"{self._format_number(width)} × "
            f"{self._format_number(height)} mm\n"
            f"{page_side} — intérieur matérialisé"
        )

    # ==========================================================
    # Format et validation
    # ==========================================================

    def _on_format_changed(self, _value=None) -> None:
        self._refresh_dimension_state()
        self._apply_preset_dimensions()

    def _on_orientation_changed(self, _value=None) -> None:
        if self.format_var.get() != self.FREE_FORMAT_LABEL:
            self._apply_preset_dimensions()
            return

        try:
            width = self._parse_number(
                self.width_var.get(),
                "largeur",
            )
            height = self._parse_number(
                self.height_var.get(),
                "hauteur",
            )
        except ValueError:
            return

        orientation = self.orientation_var.get()

        if orientation == "Paysage" and height > width:
            width, height = height, width
        elif orientation == "Portrait" and width > height:
            width, height = height, width

        self.width_var.set(
            self._format_number(width)
        )
        self.height_var.set(
            self._format_number(height)
        )

    def _refresh_dimension_state(self) -> None:
        is_free = (
            self.format_var.get()
            == self.FREE_FORMAT_LABEL
        )
        state = "normal" if is_free else "disabled"

        for key in ("width", "height"):
            for widget in self._dimension_widgets.get(
                key,
                [],
            ):
                try:
                    widget.configure(
                        state=state
                    )
                except (tk.TclError, ValueError):
                    pass

    def _apply_preset_dimensions(self) -> None:
        format_name = self.format_var.get()

        if format_name == self.FREE_FORMAT_LABEL:
            return

        presets = getattr(
            self.page,
            "FORMAT_PRESETS",
            {},
        )

        if format_name not in presets:
            return

        width, height = presets[format_name]
        orientation = self.orientation_var.get()

        if orientation == "Paysage" and height > width:
            width, height = height, width
        elif orientation == "Portrait" and width > height:
            width, height = height, width

        self.width_var.set(
            self._format_number(width)
        )
        self.height_var.set(
            self._format_number(height)
        )

    def validate(self, _event=None) -> None:
        try:
            settings = {
                "format": self.format_var.get(),
                "orientation": self.orientation_var.get(),
                "width_mm": self._parse_positive(
                    self.width_var.get(),
                    "largeur",
                ),
                "height_mm": self._parse_positive(
                    self.height_var.get(),
                    "hauteur",
                ),
                "margins": {
                    "top_mm": self._parse_non_negative(
                        self.margin_top_var.get(),
                        "marge haute",
                    ),
                    "bottom_mm": self._parse_non_negative(
                        self.margin_bottom_var.get(),
                        "marge basse",
                    ),
                    "inside_mm": self._parse_non_negative(
                        self.margin_inside_var.get(),
                        "marge intérieure",
                    ),
                    "outside_mm": self._parse_non_negative(
                        self.margin_outside_var.get(),
                        "marge extérieure",
                    ),
                },
                "bleed": {
                    "top_mm": self._parse_non_negative(
                        self.bleed_top_var.get(),
                        "fond perdu haut",
                    ),
                    "right_mm": self._parse_non_negative(
                        self.bleed_right_var.get(),
                        "fond perdu droit",
                    ),
                    "bottom_mm": self._parse_non_negative(
                        self.bleed_bottom_var.get(),
                        "fond perdu bas",
                    ),
                    "left_mm": self._parse_non_negative(
                        self.bleed_left_var.get(),
                        "fond perdu gauche",
                    ),
                },
            }

            if (
                settings["margins"]["top_mm"]
                + settings["margins"]["bottom_mm"]
                >= settings["height_mm"]
            ):
                raise ValueError(
                    "Les marges haute et basse occupent toute la hauteur."
                )

            if (
                settings["margins"]["inside_mm"]
                + settings["margins"]["outside_mm"]
                >= settings["width_mm"]
            ):
                raise ValueError(
                    "Les marges intérieure et extérieure "
                    "occupent toute la largeur."
                )

        except (TypeError, ValueError) as error:
            self.error_var.set(str(error))
            return

        callback = self.on_validate

        try:
            self.grab_release()
        except tk.TclError:
            pass

        self.destroy()
        self.master.after_idle(
            lambda: callback(settings)
        )

    def cancel(self, _event=None) -> None:
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()

    def _center_window(self) -> None:
        self.update_idletasks()

        parent = self.master.winfo_toplevel()
        x = parent.winfo_x() + max(
            0,
            (parent.winfo_width() - self.winfo_width()) // 2,
        )
        y = parent.winfo_y() + max(
            0,
            (parent.winfo_height() - self.winfo_height()) // 2,
        )

        self.geometry(f"+{x}+{y}")

    @staticmethod
    def _parse_number(
        value: str,
        label: str,
    ) -> float:
        normalized = str(value).strip().replace(",", ".")

        try:
            return float(normalized)
        except ValueError as error:
            raise ValueError(
                f"La valeur « {label} » n'est pas valide."
            ) from error

    @classmethod
    def _parse_positive(
        cls,
        value: str,
        label: str,
    ) -> float:
        number = cls._parse_number(
            value,
            label,
        )

        if number <= 0:
            raise ValueError(
                f"La valeur « {label} » doit être supérieure à zéro."
            )

        return number

    @classmethod
    def _parse_non_negative(
        cls,
        value: str,
        label: str,
    ) -> float:
        number = cls._parse_number(
            value,
            label,
        )

        if number < 0:
            raise ValueError(
                f"La valeur « {label} » ne peut pas être négative."
            )

        return number

    @staticmethod
    def _format_number(value) -> str:
        try:
            number = float(value)
        except (TypeError, ValueError):
            number = 0.0

        return (
            f"{number:.2f}"
            .rstrip("0")
            .rstrip(".")
        )


class BackgroundImageDialog(ctk.CTkToplevel):
    """Fenêtre flottante de réglage direct du fond sur la page de travail."""

    MODE_LABELS = {
        "Remplir sans déformation": "remplir",
        "Afficher l’image entière": "ajuster",
        "Dimensions et position libres": "manuel",
    }

    SCOPE_LABELS = {
        "Surface entre les marges": "surface_composition",
        "Page entière": "page",
        "Page avec fonds perdus": "fonds_perdus",
    }

    def __init__(
        self,
        parent,
        *,
        current_path: Path | None,
        current_mode: str,
        current_scope: str,
        keep_aspect_ratio: bool,
        page_width_mm: float,
        page_height_mm: float,
        composition_box_mm: dict[str, float],
        bleed_box_mm: dict[str, float],
        current_frame_mm: dict[str, float],
        on_validate,
        on_remove,
        on_close,
        on_center,
        on_reset,
        on_lock_changed,
    ) -> None:
        super().__init__(parent)

        self.on_validate = on_validate
        self.on_remove = on_remove
        self.on_close = on_close
        self.on_center = on_center
        self.on_reset = on_reset
        self.on_lock_changed = on_lock_changed
        self.selected_path = current_path
        self.current_frame_mm = dict(current_frame_mm)
        self._closing = False
        self._live_update_running = False

        # Ces arguments restent acceptés afin de conserver l'interface
        # d'appel existante. L'aperçu séparé est volontairement supprimé :
        # la vraie page de travail devient l'unique aperçu.
        _ = (
            page_width_mm,
            page_height_mm,
            composition_box_mm,
            bleed_box_mm,
        )

        self.title("Image de fond")
        self.geometry("470x650")
        self.minsize(440, 610)
        self.resizable(True, True)
        self.configure(fg_color=Colors.WINDOW)
        self.transient(parent.winfo_toplevel())
        self.protocol("WM_DELETE_WINDOW", self.close)

        reverse_modes = {
            mode: label
            for label, mode in self.MODE_LABELS.items()
        }
        reverse_scopes = {
            scope: label
            for label, scope in self.SCOPE_LABELS.items()
        }

        self.mode_var = tk.StringVar(
            value=reverse_modes.get(
                current_mode,
                "Remplir sans déformation",
            )
        )
        self.scope_var = tk.StringVar(
            value=reverse_scopes.get(
                current_scope,
                "Page entière",
            )
        )
        self.keep_ratio_var = tk.BooleanVar(
            value=bool(keep_aspect_ratio)
        )
        self.temporary_lock_var = tk.BooleanVar(value=False)
        self.file_var = tk.StringVar(
            value=(
                current_path.name
                if current_path is not None
                else "Aucune image sélectionnée"
            )
        )
        self.frame_var = tk.StringVar(
            value=self._format_frame(self.current_frame_mm)
        )
        self.error_var = tk.StringVar(value="")

        self._build()
        self._refresh_controls()
        self.after(80, self._place_window)

    def _build(self) -> None:
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=18, pady=16)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            container,
            text="Image de fond",
            font=Fonts.H1,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            container,
            text=(
                "Les changements sont appliqués immédiatement sur la page. "
                "En mode libre, déplace l’image et utilise ses huit poignées "
                "directement dans l’Atelier."
            ),
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
            justify="left",
            wraplength=420,
        ).grid(row=1, column=0, sticky="ew", pady=(4, 12))

        controls = ctk.CTkFrame(
            container,
            fg_color="#FFFFFF",
            corner_radius=12,
            border_width=1,
            border_color=Colors.BORDER,
        )
        controls.grid(row=2, column=0, sticky="nsew")
        controls.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            controls,
            text="Image utilisée",
            font=Fonts.H2,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 4))

        ctk.CTkLabel(
            controls,
            textvariable=self.file_var,
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
            anchor="w",
            wraplength=385,
        ).grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 8))

        ctk.CTkButton(
            controls,
            text="Choisir ou remplacer l’image…",
            height=36,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            command=self._choose_image,
        ).grid(row=2, column=0, sticky="ew", padx=16, pady=(0, 12))

        ctk.CTkLabel(
            controls,
            text="Surface couverte",
            font=Fonts.H2,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(row=3, column=0, sticky="ew", padx=16, pady=(0, 4))

        self.scope_combo = ctk.CTkComboBox(
            controls,
            values=list(self.SCOPE_LABELS.keys()),
            variable=self.scope_var,
            state="readonly",
            command=self._on_scope_changed,
        )
        self.scope_combo.grid(row=4, column=0, sticky="ew", padx=16, pady=(0, 10))

        ctk.CTkLabel(
            controls,
            text="Adaptation de l’image",
            font=Fonts.H2,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(row=5, column=0, sticky="ew", padx=16, pady=(0, 4))

        self.mode_combo = ctk.CTkComboBox(
            controls,
            values=list(self.MODE_LABELS.keys()),
            variable=self.mode_var,
            state="readonly",
            command=self._on_mode_changed,
        )
        self.mode_combo.grid(row=6, column=0, sticky="ew", padx=16, pady=(0, 8))

        self.keep_ratio_check = ctk.CTkCheckBox(
            controls,
            text="Conserver les proportions en mode libre",
            variable=self.keep_ratio_var,
            command=self._on_keep_ratio_changed,
        )
        self.keep_ratio_check.grid(row=7, column=0, sticky="w", padx=16, pady=(0, 10))

        self.temporary_lock_check = ctk.CTkCheckBox(
            controls,
            text="Verrouiller temporairement pendant le réglage",
            variable=self.temporary_lock_var,
            command=self._on_lock_changed,
        )
        self.temporary_lock_check.grid(
            row=8,
            column=0,
            sticky="w",
            padx=16,
            pady=(0, 12),
        )

        position = ctk.CTkFrame(
            controls,
            fg_color="#F3F5F7",
            corner_radius=8,
        )
        position.grid(row=9, column=0, sticky="ew", padx=16, pady=(0, 10))
        position.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkLabel(
            position,
            text="Position sur la page",
            font=Fonts.H2,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(10, 6))

        self.position_buttons: list[ctk.CTkButton] = []
        for row, column, label, axis in (
            (1, 0, "Centrer horizontalement", "horizontal"),
            (1, 1, "Centrer verticalement", "vertical"),
            (2, 0, "Centrer complètement", "both"),
            (2, 1, "Réinitialiser", "reset"),
        ):
            command = (
                self.on_reset
                if axis == "reset"
                else lambda value=axis: self.on_center(value)
            )
            button = ctk.CTkButton(
                position,
                text=label,
                height=30,
                fg_color=Colors.BUTTON,
                hover_color=Colors.BUTTON_HOVER,
                text_color=Colors.TEXT,
                command=command,
            )
            button.grid(
                row=row,
                column=column,
                sticky="ew",
                padx=(10 if column == 0 else 4, 10 if column == 1 else 4),
                pady=(0, 8),
            )
            self.position_buttons.append(button)

        ctk.CTkLabel(
            position,
            textvariable=self.frame_var,
            font=Fonts.SMALL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
        ).grid(
            row=3,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=12,
            pady=(0, 9),
        )

        footer = ctk.CTkFrame(container, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", pady=(12, 0))
        footer.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            footer,
            text="Supprimer le fond",
            width=150,
            height=36,
            fg_color="#F7E8E8",
            hover_color="#EFD6D6",
            text_color="#8C2F2F",
            command=self._remove,
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            footer,
            textvariable=self.error_var,
            font=Fonts.SMALL,
            text_color="#B42318",
            anchor="w",
        ).grid(row=0, column=1, sticky="ew", padx=10)

        ctk.CTkButton(
            footer,
            text="Terminer",
            width=120,
            height=36,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            command=self.finish,
        ).grid(row=0, column=2)

    def _choose_image(self) -> None:
        selected = filedialog.askopenfilename(
            parent=self,
            title="Choisir une image de fond",
            filetypes=(
                ("Images", "*.png *.jpg *.jpeg *.webp *.bmp *.tif *.tiff"),
                ("Tous les fichiers", "*.*"),
            ),
        )
        if not selected:
            return

        path = Path(selected)
        try:
            with Image.open(path) as image:
                image.verify()
        except (OSError, ValueError):
            self.error_var.set("Le fichier sélectionné n’est pas une image valide.")
            return

        self.selected_path = path
        self.file_var.set(path.name)
        self.error_var.set("")
        self._apply_live()

    def _on_scope_changed(self, _value=None) -> None:
        self._apply_live()

    def _on_mode_changed(self, _value=None) -> None:
        self._refresh_controls()
        self._apply_live()

    def _on_keep_ratio_changed(self) -> None:
        self._apply_live()

    def _on_lock_changed(self) -> None:
        self.on_lock_changed(bool(self.temporary_lock_var.get()))
        self._refresh_controls()

    def _refresh_controls(self) -> None:
        mode = self.MODE_LABELS.get(self.mode_var.get(), "remplir")
        self.keep_ratio_check.configure(
            state="normal" if mode == "manuel" else "disabled"
        )
        position_state = (
            "disabled"
            if self.temporary_lock_var.get()
            else "normal"
        )
        for button in self.position_buttons:
            button.configure(state=position_state)

    def _values(self):
        path = self.selected_path
        if path is None or not path.exists():
            return None
        mode = self.MODE_LABELS.get(self.mode_var.get(), "remplir")
        scope = self.SCOPE_LABELS.get(self.scope_var.get(), "page")
        return path, scope, mode, bool(self.keep_ratio_var.get())

    def _apply_live(self) -> bool:
        if self._live_update_running:
            return True

        values = self._values()
        if values is None:
            return False

        self._live_update_running = True
        try:
            result = self.on_validate(*values)
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            self.error_var.set(str(error))
            return False
        finally:
            self._live_update_running = False

        if result is False:
            self.error_var.set("Le fond n’a pas pu être appliqué.")
            return False

        # Le callback peut renvoyer le chemin de la copie enregistrée dans
        # le projet. On l'utilise ensuite afin d'éviter de recopier le même
        # fichier lors de chaque changement de surface ou d'adaptation.
        if isinstance(result, (str, Path)):
            saved_path = Path(result)
            if saved_path.exists():
                self.selected_path = saved_path

        self.error_var.set("")
        return True

    def set_current_frame(self, frame: dict[str, float]) -> None:
        self.current_frame_mm = dict(frame)
        self.frame_var.set(self._format_frame(self.current_frame_mm))

    @staticmethod
    def _format_frame(frame: dict[str, float]) -> str:
        if not frame:
            return "Position et dimensions : —"
        return (
            f"X {float(frame.get('x', 0.0)):.1f} mm  ·  "
            f"Y {float(frame.get('y', 0.0)):.1f} mm  ·  "
            f"L {float(frame.get('largeur', 0.0)):.1f} mm  ·  "
            f"H {float(frame.get('hauteur', 0.0)):.1f} mm"
        )

    def finish(self) -> None:
        self.close()

    def _remove(self) -> None:
        self.on_remove()
        self.selected_path = None
        self.file_var.set("Aucune image sélectionnée")
        self.current_frame_mm = {}
        self.frame_var.set(self._format_frame({}))
        self.error_var.set("")

    def close(self) -> None:
        if self._closing:
            return
        self._closing = True
        try:
            self.destroy()
        finally:
            self.on_close()

    def _place_window(self) -> None:
        self.update_idletasks()
        parent = self.master.winfo_toplevel()

        desired_x = (
            parent.winfo_x()
            + parent.winfo_width()
            - self.winfo_width()
            - 24
        )
        desired_y = parent.winfo_y() + 78
        max_x = max(0, self.winfo_screenwidth() - self.winfo_width())
        max_y = max(0, self.winfo_screenheight() - self.winfo_height())
        x = min(max(0, desired_x), max_x)
        y = min(max(0, desired_y), max_y)
        self.geometry(f"+{x}+{y}")
        self.bring_to_front()

    def bring_to_front(self) -> None:
        if not self.winfo_exists():
            return
        self.deiconify()
        self.lift()
        try:
            self.attributes("-topmost", True)
            self.after(200, self._release_topmost)
        except tk.TclError:
            pass
        self.focus_force()

    def _release_topmost(self) -> None:
        if not self.winfo_exists():
            return
        try:
            self.attributes("-topmost", False)
        except tk.TclError:
            pass


class PageEditorView:
    """
    Vue d'édition d'une page.
    """

    RULER_SIZE = 30
    MIN_READY_SIZE = 100
    DISPLAY_RETRY_DELAY_MS = 50
    MAX_DISPLAY_RETRIES = 20
    EDITOR_TOOLBAR_WIDTH = 48
    EDITOR_TOOL_BUTTON_SIZE = 38
    EDITOR_TOOLS = (
        ("selection", "S", "Sélection"),
        ("texte", "T", "Texte"),
        ("forme", "F", "Forme"),
    )

    def __init__(
        self,
        parent,
        page,
        on_back=None,
    ) -> None:

        self.parent = parent
        self.page = page
        self.on_back = on_back

        self.root = None
        self.workspace: EditorCanvas | None = None
        self.status_bar: StatusBar | None = None
        self._display_retry_count = 0
        self._save_status_text = tk.StringVar(
            value="",
        )
        self._selection_x_text = tk.StringVar(
            value="X : — mm",
        )
        self._selection_y_text = tk.StringVar(
            value="Y : — mm",
        )
        self._copied_properties: dict[str, object] | None = None
        self._font_family_var = tk.StringVar(value="Arial")
        self._font_size_var = tk.StringVar(value="12")
        self._font_family_combo = None
        self._font_size_entry = None
        self._text_color_button = None
        self._bold_button = None
        self._italic_button = None
        self._text_align_buttons: dict[str, object] = {}
        self._text_controls: list[object] = []
        self._updating_text_controls = False
        self._fill_color_button = None
        self._outline_color_button = None
        self._line_width_var = tk.StringVar(value="2")
        self._line_width_combo = None
        self._shape_controls: list[object] = []
        self._updating_shape_controls = False
        self._lock_button = None
        self._group_button = None
        self._ungroup_button = None
        self._editor_tool_buttons: dict[str, ctk.CTkButton] = {}
        self._active_editor_tool = "selection"
        self._editor_feedback_label: ctk.CTkLabel | None = None
        self._editor_feedback_after_id: str | None = None
        self._shape_menu: tk.Menu | None = None
        self._page_menu: tk.Menu | None = None
        self._page_menu_button: ctk.CTkButton | None = None
        self._page_context_tag = f"PageContextMenu_{id(self)}"
        self._page_context_widgets: list[tk.Misc] = []
        self._right_panel: ctk.CTkFrame | None = None
        self._right_panel_visible = True
        self._toggle_panel_button: ctk.CTkButton | None = None
        self._properties_type_text = tk.StringVar(value="Aucune sélection")
        self._properties_position_text = tk.StringVar(value="Position : —")
        self._properties_size_text = tk.StringVar(value="Taille : —")
        self._properties_rotation_text = tk.StringVar(value="Rotation : —")
        self._page_guide_tag = f"PageGuides_{id(self)}"
        self._workspace_base_redraw = None
        self._background_canvas_tag = f"PageBackground_{id(self)}"
        self._background_bindtag = f"PageBackgroundBindings_{id(self)}"
        self._background_selection_tag = f"PageBackgroundSelection_{id(self)}"
        self._background_frame_tag = f"PageBackgroundFrame_{id(self)}"
        self._background_handle_tag = f"PageBackgroundHandle_{id(self)}"
        self._background_photo = None
        self._background_render_cache_key = None
        self._background_render_cache_image = None
        self._background_selected = False
        self._background_interaction_mode: str | None = None
        self._background_interaction_handle: str | None = None
        self._background_interaction_start_mm: Point | None = None
        self._background_original_frame: dict[str, float] | None = None
        self._background_drag_changed = False
        self._background_history_recorded = False
        self._background_edit_mode = False
        self._background_edit_locked = True
        self._background_dialog: BackgroundImageDialog | None = None
        self._ribbon_action_buttons: list[ctk.CTkButton] = []
        self._ribbon_previous_states: list[tuple[ctk.CTkButton, str]] = []

    def show(self) -> None:

        self._clear_parent()

        self.root = ctk.CTkFrame(
            self.parent,
            fg_color="#E7EAEE",
        )
        self.root.pack(fill="both", expand=True)

        self._create_header(self.root)
        self._create_alignment_toolbar(self.root)

        content_area = tk.Frame(self.root, bg="#E7EAEE")
        content_area.pack(fill="both", expand=True, padx=12, pady=(0, 8))
        content_area.grid_rowconfigure(0, weight=1)
        content_area.grid_columnconfigure(0, weight=1)

        editor_area = tk.Frame(content_area, bg="#909090")
        editor_area.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        editor_area.grid_rowconfigure(1, weight=1)
        editor_area.grid_columnconfigure(1, weight=1)

        self._create_corner(editor_area)
        self._create_canvas(editor_area)
        self._create_rulers(editor_area)

        self._create_properties_panel(content_area)
        self._create_status_bar(self.root)
        self._bind_page_context_menu()

        self._display_retry_count = 0
        self.parent.after_idle(self._prepare_first_display)

    def _create_editor_toolbar(self, parent) -> None:

        toolbar = ctk.CTkFrame(
            parent,
            width=self.EDITOR_TOOLBAR_WIDTH,
            fg_color=Colors.SIDEBAR,
            corner_radius=0,
        )
        toolbar.pack(
            side="left",
            fill="y",
        )
        toolbar.pack_propagate(False)

        self._editor_tool_buttons.clear()

        for key, short_label, tooltip_text in self.EDITOR_TOOLS:
            button = ctk.CTkButton(
                toolbar,
                text=short_label,
                width=self.EDITOR_TOOL_BUTTON_SIZE,
                height=self.EDITOR_TOOL_BUTTON_SIZE,
                corner_radius=7,
                border_width=0,
                fg_color="transparent",
                hover_color=Colors.BUTTON_HOVER,
                text_color=Colors.TEXT,
                font=(Fonts.FAMILY, 14, "bold"),
                command=lambda tool_key=key: self._activate_editor_tool(
                    tool_key,
                ),
            )
            button.pack(
                padx=5,
                pady=(6 if key == "selection" else 3, 3),
            )

            button.bind(
                "<Enter>",
                lambda _event, text=tooltip_text: self._show_editor_tool_name(
                    text,
                ),
                add="+",
            )
            button.bind(
                "<Leave>",
                self._restore_editor_tool_status,
                add="+",
            )

            self._editor_tool_buttons[key] = button

        self._set_active_editor_tool("selection")

    def _activate_editor_tool(self, tool_key: str) -> None:

        if self.workspace is None:
            return

        if tool_key == "selection":
            self.workspace.set_tool("selection")
            self._set_active_editor_tool("selection")
            self._save_status_text.set("Outil Sélection")
            self._show_editor_feedback("Sélection active")

        elif tool_key == "texte":
            self.workspace.set_tool("text")
            self._set_active_editor_tool("texte")
            self._save_status_text.set(
                "Tracez une zone de texte sur la page",
            )
            self._show_editor_feedback(
                "Texte actif — tracez une zone sur la page",
            )

        elif tool_key == "forme":
            self._show_shape_menu()
            return

        self.workspace.focus_set()

    def _show_shape_menu(self) -> None:

        button = self._editor_tool_buttons.get("forme")

        if button is None or self.root is None:
            return

        previous_tool = self._active_editor_tool
        previous_canvas_tool = (
            self.workspace.active_tool
            if self.workspace is not None
            else "selection"
        )

        # Le bouton Forme doit paraître enfoncé dès l'ouverture du menu.
        # Si l'utilisateur ferme le menu sans choisir de forme, on revient
        # simplement à l'outil qui était actif auparavant.
        self._set_active_editor_tool("forme")

        menu = tk.Menu(
            self.root,
            tearoff=False,
        )
        menu.add_command(
            label="Rectangle",
            command=lambda: self._select_shape_tool("rectangle"),
        )
        menu.add_command(
            label="Ellipse",
            command=lambda: self._select_shape_tool("ellipse"),
        )

        self._shape_menu = menu

        try:
            menu.tk_popup(
                button.winfo_rootx() + button.winfo_width(),
                button.winfo_rooty(),
            )
        finally:
            try:
                menu.grab_release()
            except tk.TclError:
                pass

            current_canvas_tool = (
                self.workspace.active_tool
                if self.workspace is not None
                else previous_canvas_tool
            )

            if current_canvas_tool not in {"rectangle", "ellipse"}:
                self._set_active_editor_tool(previous_tool)

    def _select_shape_tool(self, shape: str) -> None:

        if self._background_edit_mode:
            self._save_status_text.set("Terminez le réglage du fond avant d’ajouter une zone")
            return

        if self.workspace is None:
            return

        self.workspace.set_tool(shape)
        self._set_active_editor_tool(shape)

        label = "rectangle" if shape == "rectangle" else "ellipse"
        self._save_status_text.set(
            f"Tracez un {label} sur la page",
        )
        self._show_editor_feedback(
            f"{label.capitalize()} actif — tracez la forme sur la page",
        )
        self.workspace.focus_set()

    def _show_editor_feedback(self, text: str) -> None:
        self._save_status_text.set(text)

    def _hide_editor_feedback(self) -> None:
        return

    def _set_active_editor_tool(self, tool_key: str) -> None:

        self._active_editor_tool = tool_key
        active_key = tool_key if tool_key in {"texte", "rectangle", "ellipse"} else None

        for key, button in self._editor_tool_buttons.items():
            if key == active_key:
                button.configure(
                    fg_color=Colors.PRIMARY,
                    hover_color=Colors.PRIMARY_HOVER,
                    text_color="#FFFFFF",
                )
            else:
                button.configure(
                    fg_color="#FFFFFF",
                    hover_color=Colors.BUTTON_HOVER,
                    text_color=Colors.TEXT,
                )

    def _sync_editor_tool_state(self) -> None:

        if self.workspace is None:
            return

        active_tool = self.workspace.active_tool
        if active_tool == "text":
            self._set_active_editor_tool("texte")
        elif active_tool == "rectangle":
            self._set_active_editor_tool("rectangle")
        elif active_tool == "ellipse":
            self._set_active_editor_tool("ellipse")
        else:
            self._set_active_editor_tool("selection")

    def _show_editor_tool_name(self, text: str) -> None:

        self._save_status_text.set(text)

    def _restore_editor_tool_status(self, _event=None) -> None:

        if self.workspace is None:
            self._save_status_text.set("")
            return

        active_tool = self.workspace.active_tool

        if active_tool == "text":
            self._save_status_text.set(
                "Tracez une zone de texte sur la page",
            )
        elif active_tool == "rectangle":
            self._save_status_text.set(
                "Tracez un rectangle sur la page",
            )
        elif active_tool == "ellipse":
            self._save_status_text.set(
                "Tracez une ellipse sur la page",
            )
        else:
            self._save_status_text.set("Outil Sélection")

    def _create_header(self, parent) -> None:

        header = ctk.CTkFrame(
            parent,
            fg_color="#F7F8FA",
            corner_radius=0,
            height=48,
        )
        header.pack(fill="x", pady=(0, 6))
        header.pack_propagate(False)

        header.grid_columnconfigure(2, weight=1)

        back_button = ctk.CTkButton(
            header,
            text="←",
            width=32,
            height=30,
            corner_radius=8,
            fg_color="#FFFFFF",
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            border_width=1,
            border_color="#D5D9DE",
            font=(Fonts.FAMILY, 16, "bold"),
            command=self.back,
        )
        back_button.grid(
            row=0,
            column=0,
            padx=(12, 8),
            pady=9,
            sticky="w",
        )
        back_button.bind(
            "<Enter>",
            lambda _event: self._show_editor_tool_name(
                "Retour au Centre du projet"
            ),
            add="+",
        )
        back_button.bind(
            "<Leave>",
            self._restore_editor_tool_status,
            add="+",
        )

        page_title = str(
            self.page.display_title
        )
        displayed_title = (
            page_title
            if len(page_title) <= 34
            else f"{page_title[:33]}…"
        )

        ctk.CTkLabel(
            header,
            text=displayed_title,
            width=220,
            anchor="w",
            font=Fonts.H2,
            text_color=Colors.TEXT,
        ).grid(
            row=0,
            column=1,
            padx=(0, 10),
            pady=8,
            sticky="w",
        )

        ctk.CTkLabel(
            header,
            textvariable=self._save_status_text,
            anchor="w",
            font=Fonts.SMALL,
            text_color=Colors.TEXT_LIGHT,
        ).grid(
            row=0,
            column=2,
            padx=(0, 10),
            pady=8,
            sticky="ew",
        )

        page_type = str(
            getattr(
                self.page,
                "page_type",
                "Page vide",
            )
        )
        appearance = self._appearance_for_type(page_type)
        displayed_type = (
            page_type
            if len(page_type) <= 16
            else f"{page_type[:15]}…"
        )

        setup_button = ctk.CTkButton(
            header,
            text="▱",
            width=32,
            height=30,
            corner_radius=8,
            fg_color="#FFFFFF",
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            border_width=1,
            border_color="#D5D9DE",
            font=(Fonts.FAMILY, 16, "bold"),
            command=self._open_page_setup,
        )
        setup_button.grid(
            row=0,
            column=3,
            padx=(0, 6),
            pady=9,
            sticky="e",
        )
        setup_button.bind(
            "<Enter>",
            lambda _event: self._show_editor_tool_name(
                "Format, marges et fonds perdus"
            ),
            add="+",
        )
        setup_button.bind(
            "<Leave>",
            self._restore_editor_tool_status,
            add="+",
        )

        ctk.CTkLabel(
            header,
            text=f"{appearance['icone']}  {displayed_type}",
            width=112,
            height=28,
            corner_radius=8,
            fg_color=appearance["couleur"],
            font=Fonts.SMALL,
            text_color=Colors.TEXT,
        ).grid(
            row=0,
            column=4,
            padx=(0, 6),
            pady=10,
            sticky="e",
        )

        self._page_menu_button = ctk.CTkButton(
            header,
            text="⚙",
            width=32,
            height=30,
            corner_radius=8,
            fg_color="#FFFFFF",
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            border_width=1,
            border_color="#D5D9DE",
            font=(Fonts.FAMILY, 15),
            command=self._show_page_menu,
        )
        self._page_menu_button.grid(
            row=0,
            column=5,
            padx=(0, 6),
            pady=9,
            sticky="e",
        )
        self._page_menu_button.bind(
            "<Enter>",
            lambda _event: self._show_editor_tool_name(
                "Gérer la page"
            ),
            add="+",
        )
        self._page_menu_button.bind(
            "<Leave>",
            self._restore_editor_tool_status,
            add="+",
        )

        new_page_button = ctk.CTkButton(
            header,
            text="+",
            width=32,
            height=30,
            corner_radius=8,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            text_color="#FFFFFF",
            font=(Fonts.FAMILY, 18, "bold"),
            command=self._new_page,
        )
        new_page_button.grid(
            row=0,
            column=6,
            padx=(0, 12),
            pady=9,
            sticky="e",
        )
        new_page_button.bind(
            "<Enter>",
            lambda _event: self._show_editor_tool_name(
                "Nouvelle page"
            ),
            add="+",
        )
        new_page_button.bind(
            "<Leave>",
            self._restore_editor_tool_status,
            add="+",
        )

    def _build_page_menu(self) -> tk.Menu:
        """Construit le menu commun au bouton et au clic droit."""

        parent = (
            self.root
            if self.root is not None
            else self.parent
        )

        menu = tk.Menu(
            parent,
            tearoff=False,
        )
        menu.add_command(
            label="Renommer…",
            command=lambda: self._schedule_page_action(
                self._rename_page
            ),
        )

        type_menu = tk.Menu(
            menu,
            tearoff=False,
        )

        current_type = str(
            getattr(
                self.page,
                "page_type",
                "Page vide",
            )
        )

        for page_type in self._available_page_types():
            appearance = self._appearance_for_type(page_type)
            check = "✓ " if page_type == current_type else ""

            type_menu.add_command(
                label=(
                    f"{check}{appearance['icone']}  {page_type}"
                ),
                command=lambda selected_type=page_type: (
                    self._schedule_page_action(
                        lambda: self._change_page_type(
                            selected_type
                        )
                    )
                ),
            )

        menu.add_cascade(
            label="Type et couleur",
            menu=type_menu,
        )
        menu.add_separator()
        menu.add_command(
            label="Dupliquer",
            command=lambda: self._schedule_page_action(
                self._duplicate_page
            ),
        )
        menu.add_separator()
        menu.add_command(
            label="Supprimer…",
            command=lambda: self._schedule_page_action(
                self._delete_page
            ),
        )

        self._page_menu = menu
        return menu

    def _schedule_page_action(self, action) -> None:
        """
        Lance l'action après la fermeture du menu natif.

        Cette temporisation évite que le menu conserve la souris ou le
        clavier au moment d'ouvrir une boîte de dialogue.
        """

        target = (
            self.root
            if self.root is not None
            else self.parent
        )

        try:
            target.after(
                40,
                action,
            )
        except tk.TclError:
            return

    def _show_page_menu(self) -> None:
        """Ouvre le menu depuis le bouton visible de l'en-tête."""

        button = self._page_menu_button

        if button is None:
            return

        menu = self._build_page_menu()

        try:
            menu.tk_popup(
                button.winfo_rootx(),
                button.winfo_rooty() + button.winfo_height(),
            )
        finally:
            try:
                menu.grab_release()
            except tk.TclError:
                pass

    def _iter_context_widgets(self):
        """Parcourt toute la vue, y compris le canvas et ses sous-widgets."""

        root = self.root

        if root is None:
            return

        pending = [root]
        visited: set[int] = set()

        while pending:
            widget = pending.pop()
            identity = id(widget)

            if identity in visited:
                continue

            visited.add(identity)
            yield widget

            try:
                pending.extend(
                    widget.winfo_children()
                )
            except tk.TclError:
                continue

    def _bind_page_context_menu(self) -> None:
        """
        Place une balise de clic droit prioritaire sur tous les widgets
        de l'Atelier. Le menu fonctionne ainsi même si le canvas possède
        déjà ses propres liaisons de souris.
        """

        self._unbind_page_context_menu()

        root = self.root

        if root is None:
            return

        tag = self._page_context_tag

        try:
            root.bind_class(
                tag,
                "<Button-3>",
                self._show_page_context_menu,
            )
        except tk.TclError:
            return

        self._page_context_widgets = []

        for widget in self._iter_context_widgets():
            try:
                current_tags = tuple(
                    widget.bindtags()
                )
                filtered_tags = tuple(
                    existing_tag
                    for existing_tag in current_tags
                    if existing_tag != tag
                )
                widget.bindtags(
                    (tag,) + filtered_tags
                )
                self._page_context_widgets.append(
                    widget
                )
            except tk.TclError:
                continue

    def _unbind_page_context_menu(self) -> None:

        tag = self._page_context_tag

        for widget in self._page_context_widgets:
            try:
                widget.bindtags(
                    tuple(
                        existing_tag
                        for existing_tag in widget.bindtags()
                        if existing_tag != tag
                    )
                )
            except tk.TclError:
                continue

        self._page_context_widgets = []

        root = self.root

        if root is None:
            return

        try:
            root.unbind_class(
                tag,
                "<Button-3>",
            )
        except tk.TclError:
            pass

    def _show_page_context_menu(self, event):
        """Ouvre les commandes de la page au point du clic droit."""

        root = self.root

        if root is None or not root.winfo_exists():
            return "break"

        menu = self._build_page_menu()

        try:
            menu.tk_popup(
                event.x_root,
                event.y_root,
            )
        finally:
            try:
                menu.grab_release()
            except tk.TclError:
                pass

        return "break"

    def _available_page_types(self) -> list[str]:
        """Retourne les types connus, dans un ordre éditorial stable."""

        names = ["Page vide"]

        try:
            library = PageTypeLibrary()
            library.load()
            names.extend(
                page_type.name
                for page_type in library.all()
            )
        except (OSError, ValueError):
            names.extend(
                [
                    "Page de texte",
                    "Page image",
                    "Page de chapitre",
                ]
            )

        current_type = str(
            getattr(
                self.page,
                "page_type",
                "Page vide",
            )
        ).strip()

        if current_type:
            names.append(current_type)

        ordered_names = []
        known_names = set()

        for name in names:
            clean_name = str(name).strip()

            if not clean_name or clean_name in known_names:
                continue

            known_names.add(clean_name)
            ordered_names.append(clean_name)

        return ordered_names

    @staticmethod
    def _appearance_for_type(page_type: str) -> dict[str, str]:
        """Associe toujours la même couleur au même type éditorial."""

        clean_type = str(page_type).strip() or "Page vide"
        known = PAGE_TYPE_APPEARANCES.get(clean_type)

        if known is not None:
            return dict(known)

        color_index = sum(
            ord(character)
            for character in clean_type
        ) % len(FALLBACK_EDITORIAL_COLORS)

        return {
            "icone": "📄",
            "couleur": FALLBACK_EDITORIAL_COLORS[color_index],
        }

    def _create_alignment_toolbar(self, parent) -> None:

        ribbon = ctk.CTkFrame(
            parent,
            fg_color="#F3F5F7",
            corner_radius=0,
            height=116,
        )
        ribbon.pack(fill="x", padx=12, pady=(0, 8))
        ribbon.pack_propagate(False)

        content = tk.Frame(ribbon, bg="#F3F5F7")
        content.pack(fill="both", expand=True, padx=8, pady=8)

        def group(title: str, width: int) -> tuple[ctk.CTkFrame, ctk.CTkFrame]:
            frame = ctk.CTkFrame(
                content,
                width=width,
                height=98,
                fg_color="#FFFFFF",
                corner_radius=10,
            )
            frame.pack(side="left", fill="y", padx=4)
            frame.pack_propagate(False)

            controls = ctk.CTkFrame(frame, fg_color="transparent")
            controls.pack(fill="both", expand=True, padx=7, pady=(7, 1))

            ctk.CTkLabel(
                frame,
                text=title,
                font=Fonts.SMALL,
                text_color=Colors.TEXT_LIGHT,
                height=18,
            ).pack(side="bottom", fill="x", pady=(0, 4))

            return frame, controls

        def icon_button(
            parent_frame,
            icon: str,
            label: str,
            command,
            width: int = 76,
            state: str = "normal",
        ) -> ctk.CTkButton:
            button = ctk.CTkButton(
                parent_frame,
                text=f"{icon}\n{label}",
                width=width,
                height=58,
                corner_radius=8,
                fg_color="#FFFFFF",
                hover_color=Colors.BUTTON_HOVER,
                text_color=Colors.TEXT,
                border_width=1,
                border_color="#D5D9DE",
                font=(Fonts.FAMILY, 12),
                command=command,
                state=state,
            )
            button.pack(side="left", padx=3, pady=2)
            self._ribbon_action_buttons.append(button)
            button.bind(
                "<Enter>",
                lambda _event, text=label: self._show_editor_tool_name(text),
                add="+",
            )
            button.bind(
                "<Leave>",
                self._restore_editor_tool_status,
                add="+",
            )
            return button

        self._editor_tool_buttons.clear()
        self._ribbon_action_buttons = []

        _, page = group("Page", 176)
        icon_button(
            page,
            "▤",
            "Format",
            self._open_page_setup,
        )
        icon_button(
            page,
            "⛶",
            "Ajuster",
            self._fit_page_to_window,
        )

        _, background = group("Fond", 104)
        icon_button(
            background,
            "▨",
            "Modifier",
            self._open_background_dialog,
            width=84,
        )

        _, add = group("Ajouter une zone", 194)
        self._editor_tool_buttons["rectangle"] = icon_button(
            add,
            "▭",
            "Rectangle",
            lambda: self._select_shape_tool("rectangle"),
            width=84,
        )
        self._editor_tool_buttons["ellipse"] = icon_button(
            add,
            "○",
            "Ellipse",
            lambda: self._select_shape_tool("ellipse"),
        )

        _, organize = group("Organisation", 510)

        alignment_panel = ctk.CTkFrame(
            organize,
            fg_color="transparent",
        )
        alignment_panel.pack(side="left", padx=(0, 3), pady=1)

        alignment_buttons = (
            ("⇤", "Gauche", "left", 0, 0),
            ("↔", "Centre H", "center_horizontal", 0, 1),
            ("⇥", "Droite", "right", 0, 2),
            ("↥", "Haut", "top", 1, 0),
            ("↕", "Centre V", "center_vertical", 1, 1),
            ("↧", "Bas", "bottom", 1, 2),
        )

        for icon, label, mode, row, column in alignment_buttons:
            button = ctk.CTkButton(
                alignment_panel,
                text=f"{icon} {label}",
                width=78,
                height=27,
                corner_radius=7,
                fg_color="#FFFFFF",
                hover_color=Colors.BUTTON_HOVER,
                text_color=Colors.TEXT,
                border_width=1,
                border_color="#D5D9DE",
                font=(Fonts.FAMILY, 10),
                command=lambda value=mode: self._align_selection(value),
            )
            button.grid(
                row=row,
                column=column,
                padx=2,
                pady=2,
                sticky="ew",
            )
            self._ribbon_action_buttons.append(button)

        icon_button(
            organize,
            "↔",
            "Distribuer",
            self._distribute_selection_horizontally,
            width=72,
        )
        self._group_button = icon_button(
            organize,
            "▣",
            "Grouper",
            self._group_selection,
            width=72,
            state="disabled",
        )
        self._ungroup_button = icon_button(
            organize,
            "▢",
            "Dissocier",
            self._ungroup_selection,
            width=72,
            state="disabled",
        )

        self._fill_color_button = None
        self._outline_color_button = None
        self._shape_controls = []

        _, panel = group("Affichage", 108)
        self._toggle_panel_button = icon_button(
            panel,
            "▤",
            "Panneau",
            self._toggle_properties_panel,
            width=84,
        )

        self._refresh_group_controls()
        self._sync_editor_tool_state()
        self._refresh_panel_toggle_state()

    def _open_alignment_menu(self) -> None:
        """Affiche les alignements utiles pour les zones sélectionnées."""
        menu = tk.Menu(self, tearoff=False)
        options = (
            ("Aligner à gauche", "left"),
            ("Centrer horizontalement", "center_horizontal"),
            ("Aligner à droite", "right"),
            ("Aligner en haut", "top"),
            ("Centrer verticalement", "center_vertical"),
            ("Aligner en bas", "bottom"),
        )
        for label, mode in options:
            menu.add_command(
                label=label,
                command=lambda value=mode: self._align_selection(value),
            )
        x = self.winfo_pointerx()
        y = self.winfo_pointery()
        try:
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()

    def _create_properties_panel(self, parent) -> None:

        self._right_panel = ctk.CTkFrame(
            parent,
            width=300,
            fg_color="#F7F8FA",
            corner_radius=12,
        )
        self._right_panel.grid(row=0, column=1, sticky="ns")
        self._right_panel.grid_propagate(False)

        tabs = ctk.CTkFrame(self._right_panel, fg_color="transparent")
        tabs.pack(fill="x", padx=10, pady=(12, 8))
        ctk.CTkButton(tabs, text="Propriétés", width=92, height=30).pack(side="left", padx=2)
        ctk.CTkButton(tabs, text="Pages", width=72, height=30, state="disabled").pack(side="left", padx=2)
        ctk.CTkButton(tabs, text="Calques", width=76, height=30, state="disabled").pack(side="left", padx=2)

        info = ctk.CTkFrame(self._right_panel, fg_color="#FFFFFF", corner_radius=10)
        info.pack(fill="x", padx=10, pady=6)
        ctk.CTkLabel(info, text="Sélection", font=Fonts.H2, text_color=Colors.TEXT).pack(anchor="w", padx=12, pady=(12, 4))
        ctk.CTkLabel(info, textvariable=self._properties_type_text, font=Fonts.NORMAL, text_color=Colors.TEXT).pack(anchor="w", padx=12, pady=2)
        ctk.CTkLabel(info, textvariable=self._properties_position_text, font=Fonts.SMALL, text_color=Colors.TEXT_LIGHT).pack(anchor="w", padx=12, pady=2)
        ctk.CTkLabel(info, textvariable=self._properties_size_text, font=Fonts.SMALL, text_color=Colors.TEXT_LIGHT).pack(anchor="w", padx=12, pady=2)
        ctk.CTkLabel(info, textvariable=self._properties_rotation_text, font=Fonts.SMALL, text_color=Colors.TEXT_LIGHT).pack(anchor="w", padx=12, pady=(2, 12))

        for title, text in (
            ("Dimensions", "Position, taille et rotation"),
            ("Apparence", "Remplissage et contour"),
            ("Texte", "Police, taille et alignement"),
        ):
            card = ctk.CTkFrame(self._right_panel, fg_color="#FFFFFF", corner_radius=10)
            card.pack(fill="x", padx=10, pady=6)
            ctk.CTkLabel(card, text=title, font=Fonts.H2, text_color=Colors.TEXT).pack(anchor="w", padx=12, pady=(10, 2))
            ctk.CTkLabel(card, text=text, font=Fonts.SMALL, text_color=Colors.TEXT_LIGHT).pack(anchor="w", padx=12, pady=(0, 10))

        self._refresh_properties_panel()

    def _toggle_properties_panel(self) -> None:
        if self._right_panel is None:
            return

        self._right_panel_visible = not self._right_panel_visible

        if self._right_panel_visible:
            self._right_panel.grid()
        else:
            self._right_panel.grid_remove()

        self._refresh_panel_toggle_state()

        if self.workspace is not None:
            self.parent.after_idle(self._fit_page_to_window)

    def _refresh_panel_toggle_state(self) -> None:
        button = self._toggle_panel_button

        if button is None:
            return

        if self._right_panel_visible:
            button.configure(
                fg_color=Colors.PRIMARY,
                hover_color=Colors.PRIMARY_HOVER,
                text_color="#FFFFFF",
            )
        else:
            button.configure(
                fg_color="#FFFFFF",
                hover_color=Colors.BUTTON_HOVER,
                text_color=Colors.TEXT,
            )

    def _fit_page_to_window(self) -> None:
        if self.workspace is None:
            return
        self.workspace._fit_page()
        self.workspace.redraw()
        self.workspace.focus_set()
        self._save_status_text.set("Page ajustée à la fenêtre")

    def _refresh_properties_panel(self) -> None:
        if self.workspace is None:
            return

        valid_indices = sorted(
            index
            for index in self.workspace._selected_object_indices
            if 0 <= index < len(self.workspace._objects)
        )

        if not valid_indices:
            index = self.workspace._selected_object_index
            if index is not None and 0 <= index < len(self.workspace._objects):
                valid_indices = [index]

        if not valid_indices:
            self._properties_type_text.set("Aucune sélection")
            self._properties_position_text.set("Position : —")
            self._properties_size_text.set("Taille : —")
            self._properties_rotation_text.set("Rotation : —")
            return

        selected_objects = [
            self.workspace._objects[index]
            for index in valid_indices
        ]

        if len(valid_indices) == 1:
            selected = selected_objects[0]
            labels = {
                "rectangle": "Rectangle",
                "ellipse": "Ellipse",
                "text": "Texte",
            }
            self._properties_type_text.set(
                f"Type : {labels.get(selected.kind, selected.kind.capitalize())}"
            )
            bounds = self.workspace._object_visual_bounds(selected)
        else:
            group_ids = {
                selected.group_id
                for selected in selected_objects
            }
            is_single_group = (
                len(group_ids) == 1
                and None not in group_ids
            )

            if is_single_group:
                self._properties_type_text.set(
                    f"Type : Groupe ({len(valid_indices)} zones)"
                )
            else:
                self._properties_type_text.set(
                    f"Type : Sélection multiple ({len(valid_indices)} zones)"
                )

            bounds = self.workspace._selection_visual_bounds(valid_indices)

        if bounds is None:
            self._properties_position_text.set("Position : —")
            self._properties_size_text.set("Taille : —")
        else:
            self._properties_position_text.set(
                f"Position : X {bounds.left:.2f} mm • Y {bounds.top:.2f} mm"
            )
            self._properties_size_text.set(
                f"Taille : {bounds.width:.2f} × {bounds.height:.2f} mm"
            )

        rotations = [
            float(getattr(selected, "rotation", 0.0))
            for selected in selected_objects
        ]
        first_rotation = rotations[0]
        if all(abs(rotation - first_rotation) < 1e-6 for rotation in rotations[1:]):
            self._properties_rotation_text.set(
                f"Rotation : {first_rotation:.1f}°"
            )
        else:
            self._properties_rotation_text.set("Rotation : multiple")

    def _unlocked_indices(self, indices) -> list[int]:
        """Conserve uniquement les objets existants et déverrouillés."""

        if self.workspace is None:
            return []

        return [
            index
            for index in indices
            if (
                0 <= index < len(self.workspace._objects)
                and not self.workspace._objects[index].locked
            )
        ]

    def _refresh_lock_control(self) -> None:
        """Actualise le bouton de verrouillage selon la sélection courante."""

        if self._lock_button is None:
            return

        if self.workspace is None:
            self._lock_button.configure(
                text="Verrouiller",
                state="disabled",
            )
            return

        state = self.workspace.get_selection_lock_state()

        if state is None:
            self._lock_button.configure(
                text="Verrouiller",
                state="disabled",
            )
        elif state:
            self._lock_button.configure(
                text="Déverrouiller",
                state="normal",
            )
        else:
            self._lock_button.configure(
                text="Verrouiller",
                state="normal",
            )

    def _toggle_selection_lock(self) -> None:
        """Verrouille ou déverrouille les objets actuellement sélectionnés."""

        if self.workspace is None:
            return

        state = self.workspace.get_selection_lock_state()

        if state is None:
            self._save_status_text.set("Sélectionner au moins un objet")
            return

        target_locked_state = not state
        changed = self.workspace.set_selection_locked(target_locked_state)

        if changed:
            if target_locked_state:
                self._save_status_text.set("Objet(s) verrouillé(s)")
            else:
                self._save_status_text.set("Objet(s) déverrouillé(s)")

        self._refresh_lock_control()
        self.workspace.focus_set()

    def _refresh_group_controls(self) -> None:
        """Actualise les commandes de groupement selon la sélection."""

        if self._group_button is None or self._ungroup_button is None:
            return

        if self.workspace is None:
            self._group_button.configure(state="disabled")
            self._ungroup_button.configure(state="disabled")
            return

        self._group_button.configure(
            state=(
                "normal"
                if self.workspace.can_group_selection()
                else "disabled"
            ),
        )
        self._ungroup_button.configure(
            state=(
                "normal"
                if self.workspace.can_ungroup_selection()
                else "disabled"
            ),
        )

    def _group_selection(self) -> None:
        """Groupe les objets bleus sélectionnés."""

        if self.workspace is None:
            return

        if self.workspace.group_selection():
            self._save_status_text.set("Objets groupés")
        else:
            self._save_status_text.set(
                "Sélectionner au moins deux objets déverrouillés",
            )

        self._refresh_group_controls()
        self.workspace.focus_set()

    def _ungroup_selection(self) -> None:
        """Dissocie le ou les groupes sélectionnés."""

        if self.workspace is None:
            return

        if self.workspace.ungroup_selection():
            self._save_status_text.set("Groupe dissocié")
        else:
            self._save_status_text.set(
                "Sélectionner un groupe déverrouillé",
            )

        self._refresh_group_controls()
        self.workspace.focus_set()

    def _selected_order_indices(self) -> list[int]:
        """Retourne les objets bleus concernés par l'ordre d'empilement."""

        if self.workspace is None:
            return []

        selected_indices = self._unlocked_indices(
            sorted(self.workspace._selected_object_indices)
        )

        if not selected_indices:
            primary_index = self.workspace._selected_object_index
            if (
                primary_index is not None
                and 0 <= primary_index < len(self.workspace._objects)
                and not self.workspace._objects[primary_index].locked
            ):
                selected_indices = [primary_index]

        reference_index = self.workspace.get_reference_object_index()
        target_indices = [
            index
            for index in selected_indices
            if index != reference_index
        ]

        return target_indices or selected_indices

    @staticmethod
    def _index_by_identity(objects: list[CanvasObject], target) -> int | None:
        if target is None:
            return None

        for index, graphic_object in enumerate(objects):
            if graphic_object is target:
                return index

        return None

    def _restore_indices_after_reorder(
        self,
        selected_objects: list[CanvasObject],
        primary_object,
        reference_object,
    ) -> None:
        """Rétablit sélection et référence après réorganisation de la liste."""

        if self.workspace is None:
            return

        objects = self.workspace._objects
        selected_indices = {
            index
            for selected_object in selected_objects
            if (
                index := self._index_by_identity(objects, selected_object)
            ) is not None
        }

        primary_index = self._index_by_identity(objects, primary_object)
        if primary_index not in selected_indices:
            primary_index = max(selected_indices) if selected_indices else None

        self.workspace._selected_object_indices = selected_indices
        self.workspace._selected_object_index = primary_index
        self.workspace._reference_object_index = self._index_by_identity(
            objects,
            reference_object,
        )

    def _change_object_order(self, action: str) -> None:
        """Modifie l'ordre d'empilement des objets sélectionnés."""

        if self.workspace is None:
            return

        target_indices = self._selected_order_indices()
        if not target_indices:
            self._save_status_text.set("Sélectionner au moins un objet")
            return

        self.workspace.commit_active_text_edit()

        objects = list(self.workspace._objects)
        target_objects = [objects[index] for index in target_indices]
        target_identities = {id(graphic_object) for graphic_object in target_objects}

        selected_objects = [
            objects[index]
            for index in sorted(self.workspace._selected_object_indices)
            if 0 <= index < len(objects)
        ]
        primary_object = (
            objects[self.workspace._selected_object_index]
            if (
                self.workspace._selected_object_index is not None
                and 0 <= self.workspace._selected_object_index < len(objects)
            )
            else None
        )
        reference_index = self.workspace.get_reference_object_index()
        reference_object = (
            objects[reference_index]
            if reference_index is not None
            else None
        )

        reordered = list(objects)

        if action == "front":
            reordered = [
                graphic_object
                for graphic_object in objects
                if id(graphic_object) not in target_identities
            ] + target_objects
            status_label = "Placé au premier plan"

        elif action == "back":
            reordered = target_objects + [
                graphic_object
                for graphic_object in objects
                if id(graphic_object) not in target_identities
            ]
            status_label = "Placé à l’arrière-plan"

        elif action == "forward":
            for index in range(len(reordered) - 2, -1, -1):
                current_selected = id(reordered[index]) in target_identities
                next_selected = id(reordered[index + 1]) in target_identities
                if current_selected and not next_selected:
                    reordered[index], reordered[index + 1] = (
                        reordered[index + 1],
                        reordered[index],
                    )
            status_label = "Avancé d’un niveau"

        elif action == "backward":
            for index in range(1, len(reordered)):
                current_selected = id(reordered[index]) in target_identities
                previous_selected = id(reordered[index - 1]) in target_identities
                if current_selected and not previous_selected:
                    reordered[index], reordered[index - 1] = (
                        reordered[index - 1],
                        reordered[index],
                    )
            status_label = "Reculé d’un niveau"

        else:
            return

        changed = any(
            before is not after
            for before, after in zip(objects, reordered)
        )

        if not changed:
            self._save_status_text.set("Ordre déjà atteint")
            self.workspace.focus_set()
            return

        self.workspace._remember_current_state()
        self.workspace._objects = reordered
        self._restore_indices_after_reorder(
            selected_objects,
            primary_object,
            reference_object,
        )
        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()
        self._save_status_text.set(
            f"{status_label} : {len(target_objects)} objet(s)"
        )

    def _available_font_families(self) -> list[str]:
        """Retourne les polices installées, avec les plus courantes en tête."""

        preferred = [
            "Arial",
            "Calibri",
            "Cambria",
            "Garamond",
            "Georgia",
            "Times New Roman",
            "Verdana",
            "Courier New",
        ]

        try:
            installed = sorted(
                {
                    name
                    for name in tkfont.families(self.parent)
                    if name and not name.startswith("@")
                },
                key=str.casefold,
            )
        except tk.TclError:
            installed = []

        ordered = [name for name in preferred if name in installed]
        ordered.extend(name for name in installed if name not in ordered)

        return ordered or preferred

    def _selected_shape_indices(self) -> list[int]:
        """Retourne les objets ciblés par les commandes d'apparence.

        Toutes les zones graphiques possèdent un remplissage et un contour,
        y compris les zones de texte. La référence rouge est protégée dès
        qu'une ou plusieurs cibles bleues sont sélectionnées.
        """

        if self.workspace is None:
            return []

        selected_indices = self._unlocked_indices(
            sorted(self.workspace._selected_object_indices)
        )

        # L'index principal ne sert que de secours lorsque le canvas vient de
        # sélectionner un objet et que l'ensemble multiple n'est pas encore
        # renseigné. Il n'est jamais ajouté à une sélection déjà existante.
        if not selected_indices:
            primary_index = self.workspace._selected_object_index
            if (
                primary_index is not None
                and 0 <= primary_index < len(self.workspace._objects)
                and not self.workspace._objects[primary_index].locked
            ):
                selected_indices = [primary_index]

        reference_index = self.workspace.get_reference_object_index()
        target_indices = [
            index
            for index in selected_indices
            if index != reference_index
        ]

        return target_indices or selected_indices

    def _set_shape_controls_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"

        for control in self._shape_controls:
            if control is not None:
                control.configure(state=state)

        if enabled and self._line_width_combo is not None:
            self._line_width_combo.configure(state="readonly")

    def _refresh_shape_controls(self) -> None:
        if self.workspace is None:
            return

        shape_indices = self._selected_shape_indices()
        self._updating_shape_controls = True

        try:
            if not shape_indices:
                self._line_width_var.set("2")
                self._set_shape_controls_enabled(False)
                return

            line_widths = {
                self.workspace._objects[index].line_width
                for index in shape_indices
            }
            if len(line_widths) == 1:
                line_width = next(iter(line_widths))
                self._line_width_var.set(
                    "Sans contour" if line_width == 0 else str(line_width)
                )
            else:
                self._line_width_var.set("")
            self._set_shape_controls_enabled(True)
        finally:
            self._updating_shape_controls = False

    def _apply_shape_changes(self, status_label: str, **changes) -> bool:
        if self.workspace is None or self._updating_shape_controls:
            return False

        shape_indices = self._selected_shape_indices()

        if not shape_indices:
            self._save_status_text.set("Sélectionner au moins un objet")
            return False

        self.workspace.commit_active_text_edit()
        self.workspace._remember_current_state()

        for index in shape_indices:
            self.workspace._objects[index] = replace(
                self.workspace._objects[index],
                **changes,
            )

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()
        self._save_status_text.set(
            f"{status_label} sur {len(shape_indices)} objet(s)"
        )
        return True

    def _selected_text_indices(self) -> list[int]:
        """Retourne les zones de texte réellement sélectionnées.

        Comme pour les formes, la référence rouge est exclue lorsqu'il existe
        des cibles bleues, mais reste modifiable lorsqu'elle est seule.
        """

        if self.workspace is None:
            return []

        selected_indices = set(self.workspace._selected_object_indices)
        primary_index = self.workspace._selected_object_index

        if (
            primary_index is not None
            and 0 <= primary_index < len(self.workspace._objects)
        ):
            selected_indices.add(primary_index)

        text_indices = [
            index
            for index in sorted(selected_indices)
            if (
                0 <= index < len(self.workspace._objects)
                and self.workspace._objects[index].kind == "text"
                and not self.workspace._objects[index].locked
            )
        ]

        reference_index = self.workspace.get_reference_object_index()
        target_indices = [
            index
            for index in text_indices
            if index != reference_index
        ]

        return target_indices or text_indices

    def _set_text_controls_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"

        for control in self._text_controls:
            if control is not None:
                control.configure(state=state)

        if enabled and self._font_family_combo is not None:
            self._font_family_combo.configure(state="readonly")

    @staticmethod
    def _set_toggle_button_state(button, active: bool) -> None:
        if button is None:
            return

        button.configure(
            fg_color="#3874CB" if active else "#AFAFAF",
            hover_color="#2F63AE" if active else "#999999",
            text_color="#FFFFFF" if active else "#222222",
        )

    def _refresh_text_controls(self) -> None:
        if self.workspace is None:
            return

        text_indices = self._selected_text_indices()
        self._updating_text_controls = True

        try:
            if not text_indices:
                self._font_family_var.set("Arial")
                self._font_size_var.set("12")
                self._set_toggle_button_state(self._bold_button, False)
                self._set_toggle_button_state(self._italic_button, False)
                for button in self._text_align_buttons.values():
                    self._set_toggle_button_state(button, False)
                self._set_text_controls_enabled(False)
                return

            text_objects = [
                self.workspace._objects[index]
                for index in text_indices
            ]

            font_families = {obj.font_family for obj in text_objects}
            font_sizes = {obj.font_size for obj in text_objects}
            bold_values = {obj.bold for obj in text_objects}
            italic_values = {obj.italic for obj in text_objects}
            alignments = {obj.align for obj in text_objects}

            self._font_family_var.set(
                next(iter(font_families))
                if len(font_families) == 1
                else ""
            )
            self._font_size_var.set(
                str(next(iter(font_sizes)))
                if len(font_sizes) == 1
                else ""
            )

            self._set_toggle_button_state(
                self._bold_button,
                bold_values == {True},
            )
            self._set_toggle_button_state(
                self._italic_button,
                italic_values == {True},
            )

            active_alignment = (
                next(iter(alignments))
                if len(alignments) == 1
                else None
            )
            for alignment, button in self._text_align_buttons.items():
                self._set_toggle_button_state(
                    button,
                    alignment == active_alignment,
                )

            self._set_text_controls_enabled(True)
        finally:
            self._updating_text_controls = False

    def _apply_text_changes(self, **changes) -> bool:
        if self.workspace is None or self._updating_text_controls:
            return False

        text_indices = self._selected_text_indices()

        if not text_indices:
            self._save_status_text.set("Sélectionner une zone de texte")
            return False

        self.workspace.commit_active_text_edit()
        self.workspace._remember_current_state()

        for index in text_indices:
            self.workspace._objects[index] = replace(
                self.workspace._objects[index],
                **changes,
            )

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()
        self._save_status_text.set(
            f"Texte modifié sur {len(text_indices)} zone(s)"
        )
        return True

    def _change_font_family(self, font_family: str) -> None:
        if font_family:
            self._apply_text_changes(font_family=font_family)

    def _apply_font_size(self, event=None) -> str | None:
        if self._updating_text_controls:
            return None

        value = self._font_size_var.get().strip()

        try:
            font_size = int(value)
        except ValueError:
            self._save_status_text.set("Taille de police invalide")
            self._refresh_text_controls()
            return "break" if event is not None else None

        if not 1 <= font_size <= 500:
            self._save_status_text.set("Taille comprise entre 1 et 500")
            self._refresh_text_controls()
            return "break" if event is not None else None

        self._apply_text_changes(font_size=font_size)
        return "break" if event is not None else None

    def _toggle_text_style(self, property_name: str) -> None:
        if self.workspace is None:
            return

        text_indices = self._selected_text_indices()

        if not text_indices:
            self._save_status_text.set("Sélectionner une zone de texte")
            return

        new_value = not all(
            bool(getattr(self.workspace._objects[index], property_name))
            for index in text_indices
        )
        self._apply_text_changes(**{property_name: new_value})

    def _choose_text_color(self) -> None:
        if self.workspace is None:
            return


        text_indices = self._selected_text_indices()

        if not text_indices:
            self._save_status_text.set("Sélectionner une zone de texte")
            return

        initial_color = self.workspace._objects[text_indices[0]].text_color
        chosen_color = colorchooser.askcolor(
            color=initial_color,
            title="Couleur du texte",
            parent=self.parent.winfo_toplevel(),
        )[1]

        if not chosen_color:
            self.workspace.focus_set()
            return

        self._apply_text_changes(text_color=chosen_color)

    def _set_text_alignment(self, alignment: str) -> None:
        if alignment not in {"left", "center", "right"}:
            return

        self._apply_text_changes(align=alignment)

    def _align_selection(self, alignment: str) -> None:
        """Aligne les zones sur la surface comprise entre les marges."""

        if self.workspace is None:
            return

        selected_indices = self._unlocked_indices(
            sorted(self.workspace._selected_object_indices)
        )

        if not selected_indices:
            primary_index = self.workspace._selected_object_index
            if (
                primary_index is not None
                and 0 <= primary_index < len(self.workspace._objects)
                and not self.workspace._objects[primary_index].locked
            ):
                selected_indices = [primary_index]

        if not selected_indices:
            self._save_status_text.set("Sélectionner au moins une zone")
            return

        if alignment not in {
            "left",
            "center_horizontal",
            "right",
            "top",
            "center_vertical",
            "bottom",
        }:
            return

        page_number = int(getattr(self.page, "number", 1))
        is_verso = page_number % 2 == 0

        if hasattr(self.page, "composition_box_mm"):
            composition = self.page.composition_box_mm(verso=is_verso)
            target_left = float(composition.get("x", 0.0))
            target_top = float(composition.get("y", 0.0))
            target_width = max(
                0.0,
                float(composition.get("largeur", 0.0)),
            )
            target_height = max(
                0.0,
                float(composition.get("hauteur", 0.0)),
            )
        else:
            margin_top = float(getattr(self.page, "margin_top_mm", 15.0))
            margin_bottom = float(
                getattr(self.page, "margin_bottom_mm", 15.0)
            )
            margin_inside = float(
                getattr(self.page, "margin_inside_mm", 15.0)
            )
            margin_outside = float(
                getattr(self.page, "margin_outside_mm", 15.0)
            )

            target_left = margin_outside if is_verso else margin_inside
            right_margin = margin_inside if is_verso else margin_outside
            target_top = margin_top
            target_width = max(
                0.0,
                self.workspace.page_format.width_mm
                - target_left
                - right_margin,
            )
            target_height = max(
                0.0,
                self.workspace.page_format.height_mm
                - margin_top
                - margin_bottom,
            )

        target_right = target_left + target_width
        target_bottom = target_top + target_height
        target_center_x = target_left + target_width / 2.0
        target_center_y = target_top + target_height / 2.0

        self.workspace._remember_current_state()

        for index in selected_indices:
            graphic_object = self.workspace._objects[index]
            bounds = graphic_object.bounds
            new_x = bounds.left
            new_y = bounds.top

            if alignment == "left":
                new_x = target_left
            elif alignment == "center_horizontal":
                new_x = target_center_x - bounds.width / 2.0
            elif alignment == "right":
                new_x = target_right - bounds.width
            elif alignment == "top":
                new_y = target_top
            elif alignment == "center_vertical":
                new_y = target_center_y - bounds.height / 2.0
            elif alignment == "bottom":
                new_y = target_bottom - bounds.height

            self.workspace._objects[index] = replace(
                graphic_object,
                bounds=Rect(Point(new_x, new_y), bounds.size),
            )

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()
        self._save_status_text.set(
            "Zone alignée sur les marges"
            if len(selected_indices) == 1
            else f"{len(selected_indices)} zones alignées sur les marges"
        )


    def _distribute_selection_horizontally(self) -> None:
        """Répartit régulièrement les objets sélectionnés de gauche à droite."""

        if self.workspace is None:
            return

        selected_indices = self._unlocked_indices(
            self.workspace._selected_object_indices
        )

        if len(selected_indices) < 3:
            self._save_status_text.set(
                "Sélectionner au moins trois objets déverrouillés"
            )
            return

        selected_indices.sort(
            key=lambda index: self.workspace._objects[index].bounds.left
        )

        selected_objects = [
            self.workspace._objects[index]
            for index in selected_indices
        ]

        first_bounds = selected_objects[0].bounds
        last_bounds = selected_objects[-1].bounds
        total_width = sum(
            graphic_object.bounds.width
            for graphic_object in selected_objects
        )
        available_width = last_bounds.right - first_bounds.left
        spacing = (available_width - total_width) / (len(selected_objects) - 1)

        self.workspace._remember_current_state()

        current_x = first_bounds.left

        for index, graphic_object in zip(selected_indices, selected_objects):
            bounds = graphic_object.bounds
            self.workspace._objects[index] = replace(
                graphic_object,
                bounds=Rect(
                    Point(current_x, bounds.top),
                    bounds.size,
                ),
            )
            current_x += bounds.width + spacing

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()

    def _distribute_selection_vertically(self) -> None:
        """Répartit régulièrement les objets sélectionnés de haut en bas."""

        if self.workspace is None:
            return

        selected_indices = self._unlocked_indices(
            self.workspace._selected_object_indices
        )

        if len(selected_indices) < 3:
            self._save_status_text.set(
                "Sélectionner au moins trois objets déverrouillés"
            )
            return

        selected_indices.sort(
            key=lambda index: self.workspace._objects[index].bounds.top
        )

        selected_objects = [
            self.workspace._objects[index]
            for index in selected_indices
        ]

        first_bounds = selected_objects[0].bounds
        last_bounds = selected_objects[-1].bounds
        total_height = sum(
            graphic_object.bounds.height
            for graphic_object in selected_objects
        )
        available_height = last_bounds.bottom - first_bounds.top
        spacing = (available_height - total_height) / (len(selected_objects) - 1)

        self.workspace._remember_current_state()

        current_y = first_bounds.top

        for index, graphic_object in zip(selected_indices, selected_objects):
            bounds = graphic_object.bounds
            self.workspace._objects[index] = replace(
                graphic_object,
                bounds=Rect(
                    Point(bounds.left, current_y),
                    bounds.size,
                ),
            )
            current_y += bounds.height + spacing

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()

    def _make_selection_same_width(self) -> None:
        """Donne aux objets cibles la largeur de l'objet rouge."""

        if self.workspace is None:
            return

        reference_index = self.workspace.get_reference_object_index()

        if reference_index is None:
            self._save_status_text.set("Choisir d'abord l'objet rouge")
            return

        selected_indices = [
            index
            for index in sorted(self.workspace._selected_object_indices)
            if (
                0 <= index < len(self.workspace._objects)
                and index != reference_index
                and not self.workspace._objects[index].locked
            )
        ]

        if not selected_indices:
            self._save_status_text.set("Sélectionner au moins un objet cible")
            return

        reference_width = self.workspace._objects[
            reference_index
        ].bounds.width

        self.workspace._remember_current_state()

        for index in selected_indices:
            graphic_object = self.workspace._objects[index]
            bounds = graphic_object.bounds
            self.workspace._objects[index] = replace(
                graphic_object,
                bounds=Rect(
                    bounds.origin,
                    Size(reference_width, bounds.height),
                ),
            )

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()
        self._save_status_text.set(
            f"Largeur appliquée à {len(selected_indices)} objet(s)"
        )

    def _make_selection_same_height(self) -> None:
        """Donne aux objets cibles la hauteur de l'objet rouge."""

        if self.workspace is None:
            return

        reference_index = self.workspace.get_reference_object_index()

        if reference_index is None:
            self._save_status_text.set("Choisir d'abord l'objet rouge")
            return

        selected_indices = [
            index
            for index in sorted(self.workspace._selected_object_indices)
            if (
                0 <= index < len(self.workspace._objects)
                and index != reference_index
                and not self.workspace._objects[index].locked
            )
        ]

        if not selected_indices:
            self._save_status_text.set("Sélectionner au moins un objet cible")
            return

        reference_height = self.workspace._objects[
            reference_index
        ].bounds.height

        self.workspace._remember_current_state()

        for index in selected_indices:
            graphic_object = self.workspace._objects[index]
            bounds = graphic_object.bounds
            self.workspace._objects[index] = replace(
                graphic_object,
                bounds=Rect(
                    bounds.origin,
                    Size(bounds.width, reference_height),
                ),
            )

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()
        self._save_status_text.set(
            f"Hauteur appliquée à {len(selected_indices)} objet(s)"
        )

    def _make_selection_same_size(self) -> None:
        """Donne aux objets cibles la taille de l'objet rouge."""

        if self.workspace is None:
            return

        reference_index = self.workspace.get_reference_object_index()

        if reference_index is None:
            self._save_status_text.set("Choisir d'abord l'objet rouge")
            return

        selected_indices = [
            index
            for index in sorted(self.workspace._selected_object_indices)
            if (
                0 <= index < len(self.workspace._objects)
                and index != reference_index
                and not self.workspace._objects[index].locked
            )
        ]

        if not selected_indices:
            self._save_status_text.set("Sélectionner au moins un objet cible")
            return

        reference_bounds = self.workspace._objects[
            reference_index
        ].bounds

        self.workspace._remember_current_state()

        for index in selected_indices:
            graphic_object = self.workspace._objects[index]
            bounds = graphic_object.bounds
            self.workspace._objects[index] = replace(
                graphic_object,
                bounds=Rect(
                    bounds.origin,
                    Size(
                        reference_bounds.width,
                        reference_bounds.height,
                    ),
                ),
            )

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()
        self._save_status_text.set(
            f"Taille appliquée à {len(selected_indices)} objet(s)"
        )


    def _choose_fill_color(self) -> None:
        """Modifie le remplissage des objets sélectionnés."""

        if self.workspace is None:
            return

        shape_indices = self._selected_shape_indices()

        if not shape_indices:
            self._save_status_text.set("Sélectionner au moins un objet")
            return

        initial_color = self.workspace._objects[shape_indices[0]].fill
        chosen_color = colorchooser.askcolor(
            color=initial_color,
            title="Couleur de remplissage",
            parent=self.parent.winfo_toplevel(),
        )[1]

        if not chosen_color:
            self.workspace.focus_set()
            return

        self._apply_shape_changes(
            "Remplissage modifié",
            fill=chosen_color,
        )

    def _choose_outline_color(self) -> None:
        """Modifie la couleur du contour des objets sélectionnés."""

        if self.workspace is None:
            return

        shape_indices = self._selected_shape_indices()

        if not shape_indices:
            self._save_status_text.set("Sélectionner au moins un objet")
            return

        initial_color = self.workspace._objects[shape_indices[0]].outline
        chosen_color = colorchooser.askcolor(
            color=initial_color,
            title="Couleur du contour",
            parent=self.parent.winfo_toplevel(),
        )[1]

        if not chosen_color:
            self.workspace.focus_set()
            return

        self._apply_shape_changes(
            "Contour modifié",
            outline=chosen_color,
        )

    def _change_line_width(self, value: str) -> None:
        """Modifie l'épaisseur du contour des objets sélectionnés."""

        if self._updating_shape_controls:
            return

        if value == "Sans contour":
            line_width = 0
            status_label = "Contour supprimé"
        else:
            try:
                line_width = int(value)
            except (TypeError, ValueError):
                self._save_status_text.set("Épaisseur de contour invalide")
                self._refresh_shape_controls()
                return

            if not 1 <= line_width <= 50:
                self._save_status_text.set("Épaisseur comprise entre 1 et 50")
                self._refresh_shape_controls()
                return

            status_label = "Épaisseur modifiée"

        self._apply_shape_changes(
            status_label,
            line_width=line_width,
        )

    def _open_copy_properties_dialog(self) -> None:
        """Ouvre le choix des propriétés à copier depuis l'objet rouge."""

        if self.workspace is None:
            return

        reference_index = self.workspace.get_reference_object_index()

        if reference_index is None:
            self._save_status_text.set("Choisir d'abord l'objet rouge")
            return

        if not (0 <= reference_index < len(self.workspace._objects)):
            return

        source = self.workspace._objects[reference_index]

        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Copier les propriétés")
        dialog.geometry("390x520")
        dialog.resizable(False, False)
        dialog.transient(self.parent.winfo_toplevel())
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="Propriétés à copier",
            font=Fonts.H1,
            text_color=Colors.TEXT,
        ).pack(padx=24, pady=(22, 12), anchor="w")

        ctk.CTkLabel(
            dialog,
            text="La forme rouge est utilisée comme modèle.",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
        ).pack(padx=24, pady=(0, 12), anchor="w")

        property_choices = (
            ("fill", "Remplissage", "appearance"),
            ("outline", "Couleur du contour", "appearance"),
            ("line_width", "Épaisseur du contour", "appearance"),
            ("text_color", "Couleur du texte", "text"),
            ("font_family", "Police", "text"),
            ("font_size", "Taille de police", "text"),
            ("bold", "Gras", "text"),
            ("italic", "Italique", "text"),
            ("align", "Alignement du texte", "text"),
        )

        variables: dict[str, tk.BooleanVar] = {}
        source_is_text = source.kind == "text"

        options_frame = ctk.CTkScrollableFrame(
            dialog,
            fg_color="transparent",
            height=330,
        )
        options_frame.pack(fill="both", expand=True, padx=18, pady=(0, 12))

        for property_name, label, property_group in property_choices:
            is_available = property_group == "appearance" or source_is_text
            variable = tk.BooleanVar(value=is_available)
            variables[property_name] = variable

            checkbox_text = label
            if not is_available:
                checkbox_text = f"{label} — réservé aux textes"

            checkbox = ctk.CTkCheckBox(
                options_frame,
                text=checkbox_text,
                variable=variable,
                font=Fonts.NORMAL,
            )
            checkbox.pack(anchor="w", padx=8, pady=7)

            if not is_available:
                checkbox.configure(state="disabled")

        buttons_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 18))

        def confirm_copy() -> None:
            selected_properties = {
                name: getattr(source, name)
                for name, variable in variables.items()
                if variable.get()
            }

            if not selected_properties:
                self._save_status_text.set("Aucune propriété choisie")
                return

            self._copied_properties = selected_properties
            self._save_status_text.set(
                f"{len(selected_properties)} propriété(s) copiée(s)"
            )
            dialog.grab_release()
            dialog.destroy()
            self.workspace.focus_set()

        ctk.CTkButton(
            buttons_frame,
            text="Annuler",
            width=110,
            command=dialog.destroy,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            buttons_frame,
            text="Copier",
            width=110,
            command=confirm_copy,
        ).pack(side="right")

        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        dialog.after(50, dialog.focus_force)

    def _paste_properties(self) -> None:
        """Applique les propriétés mémorisées aux objets sélectionnés."""

        if self.workspace is None:
            return

        if not self._copied_properties:
            self._save_status_text.set("Aucune propriété copiée")
            return

        reference_index = self.workspace.get_reference_object_index()

        selected_indices = [
            index
            for index in sorted(self.workspace._selected_object_indices)
            if (
                0 <= index < len(self.workspace._objects)
                and index != reference_index
                and not self.workspace._objects[index].locked
            )
        ]

        if not selected_indices:
            self._save_status_text.set("Aucun objet cible sélectionné")
            return

        appearance_properties = {
            "fill",
            "outline",
            "line_width",
        }
        text_properties = {
            "text_color",
            "font_family",
            "font_size",
            "bold",
            "italic",
            "align",
        }

        self.workspace._remember_current_state()

        modified_count = 0

        for index in selected_indices:
            graphic_object = self.workspace._objects[index]

            applicable_properties = {
                name: value
                for name, value in self._copied_properties.items()
                if (
                    name in appearance_properties
                    or (
                        name in text_properties
                        and graphic_object.kind == "text"
                    )
                )
            }

            if not applicable_properties:
                continue

            self.workspace._objects[index] = replace(
                graphic_object,
                **applicable_properties,
            )
            modified_count += 1

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()

        if modified_count == 0:
            self._save_status_text.set(
                "Aucune propriété compatible avec les objets cibles"
            )
            return

        self._save_status_text.set(
            f"Propriétés appliquées à {modified_count} objet(s)"
        )

    def _create_corner(self, parent) -> None:

        corner = tk.Frame(
            parent,
            bg="#CFCFCF",
            width=self.RULER_SIZE,
            height=self.RULER_SIZE,
        )
        corner.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        corner.grid_propagate(False)

    def _create_canvas(self, parent) -> None:

        canvas_container = tk.Frame(
            parent,
            bg="#909090",
        )
        canvas_container.grid(
            row=1,
            column=1,
            sticky="nsew",
        )

        self.workspace = EditorCanvas(canvas_container)
        self.workspace.pack(
            fill="both",
            expand=True,
        )

        self.workspace.set_page_format(
            self._resolve_page_format(),
        )

        saved_objects = self._load_page_objects()

        if saved_objects:
            self.workspace._objects = saved_objects

        self.workspace.set_external_history_state(
            self._snapshot_background_history,
            self._restore_background_history,
        )
        self._install_page_guides()

        self.workspace.add_selection_listener(
            self._refresh_selection_label,
        )

        # Les transformations réalisées à la souris (rotation et
        # redimensionnement d'un groupe notamment) ne changent pas la
        # sélection. On déclenche donc explicitement l'enregistrement
        # automatique à la fin de chaque interaction.
        self.workspace.bind(
            "<ButtonRelease-1>",
            self._schedule_canvas_autosave,
            add="+",
        )

        window = self.parent.winfo_toplevel()
        window.bind(
            "<Control-s>",
            self._save_shortcut,
            add="+",
        )
        window.bind(
            "<Control-S>",
            self._save_shortcut,
            add="+",
        )

    def _refresh_selection_label(
        self,
        selected_object: CanvasObject | None,
    ) -> None:

        if selected_object is None:
            self._selection_x_text.set("X : — mm")
            self._selection_y_text.set("Y : — mm")
        else:
            self._selection_x_text.set(
                f"X : {selected_object.bounds.left:.2f} mm",
            )
            self._selection_y_text.set(
                f"Y : {selected_object.bounds.top:.2f} mm",
            )

        self._refresh_shape_controls()
        self._refresh_text_controls()
        self._refresh_lock_control()
        self._refresh_group_controls()
        self._sync_editor_tool_state()
        self._refresh_properties_panel()
        self._save_page_objects(show_status=False)

    def _open_background_dialog(self) -> None:
        """Ouvre la fenêtre flottante du fond et sécurise tout échec."""

        if getattr(self.page, "locked", False):
            self._save_status_text.set("Cette page est verrouillée")
            return

        existing = self._background_dialog
        if existing is not None:
            try:
                if existing.winfo_exists():
                    existing.deiconify()
                    existing.lift()
                    existing.bring_to_front()
                    return
            except tk.TclError:
                self._background_dialog = None

        dialog = None
        try:
            background = getattr(self.page, "background", {})
            composition_box = self._background_scope_box_mm(
                "surface_composition"
            )
            bleed_box = self._background_scope_box_mm(
                "fonds_perdus"
            )
            current_frame = self._background_effective_frame_mm(
                background
            )

            # Une vraie fenêtre principale est utilisée comme propriétaire.
            # Sur Windows, utiliser un simple Frame comme parent peut laisser
            # la fenêtre flottante derrière l'Atelier ou empêcher son affichage.
            if self.root is not None and self.root.winfo_exists():
                dialog_parent = self.root.winfo_toplevel()
            else:
                dialog_parent = self.parent.winfo_toplevel()

            dialog = BackgroundImageDialog(
                parent=dialog_parent,
                current_path=self._resolve_background_resource(),
                current_mode=str(background.get("mode", "remplir")),
                current_scope=str(background.get("portee", "page")),
                keep_aspect_ratio=bool(
                    background.get("conserver_proportions", True)
                ),
                page_width_mm=float(
                    getattr(self.page, "width_mm", 148.0)
                ),
                page_height_mm=float(
                    getattr(self.page, "height_mm", 210.0)
                ),
                composition_box_mm=composition_box,
                bleed_box_mm=bleed_box,
                current_frame_mm=current_frame,
                on_validate=self._apply_background_image,
                on_remove=self._remove_background_image,
                on_close=self._end_background_edit_mode,
                on_center=self._center_background,
                on_reset=self._reset_background_position,
                on_lock_changed=self._set_background_temporary_lock,
            )

            self._background_dialog = dialog
            self._begin_background_edit_mode()

            dialog.update_idletasks()
            dialog.deiconify()
            dialog.lift()
            dialog.bring_to_front()
            dialog.after(120, dialog.bring_to_front)

        except Exception as error:
            if dialog is not None:
                try:
                    dialog.destroy()
                except tk.TclError:
                    pass

            self._background_dialog = None
            self._background_edit_mode = False
            self._background_edit_locked = True
            self._background_selected = False
            self._background_interaction_mode = None
            self._background_interaction_handle = None
            self._ribbon_previous_states = []
            self._refresh_group_controls()
            self._sync_editor_tool_state()
            self._draw_background_controls()

            messagebox.showerror(
                "Image de fond",
                "La fenêtre du fond n’a pas pu s’ouvrir.\n\n"
                f"Détail : {type(error).__name__} : {error}",
                parent=(self.root or self.parent),
            )

    def _begin_background_edit_mode(self) -> None:
        self._background_edit_mode = True
        self._background_edit_locked = False
        self._background_selected = bool(
            getattr(self.page, "background", {}).get("active")
        )
        self._ribbon_previous_states = []
        for button in self._ribbon_action_buttons:
            try:
                self._ribbon_previous_states.append(
                    (button, str(button.cget("state")))
                )
                button.configure(state="disabled")
            except tk.TclError:
                pass
        if self.workspace is not None:
            self.workspace.set_tool("selection")
            try:
                self.workspace._clear_reference_state(
                    clear_selection=True,
                    redraw=True,
                    notify=True,
                )
            except AttributeError:
                pass
            self.workspace.focus_set()
        self._save_status_text.set("Mode Fond — les zones sont désactivées")
        self._draw_background_controls()

    def _end_background_edit_mode(self) -> None:
        self._background_dialog = None
        self._background_edit_mode = False
        self._background_edit_locked = True
        self._background_selected = False
        self._background_interaction_mode = None
        self._background_interaction_handle = None
        self._background_history_recorded = False
        for button, state in self._ribbon_previous_states:
            try:
                button.configure(state=state)
            except tk.TclError:
                pass
        self._ribbon_previous_states = []
        self._refresh_group_controls()
        self._sync_editor_tool_state()
        self._draw_background_controls()
        if self.workspace is not None:
            self.workspace.focus_set()
        self._save_status_text.set("Fond verrouillé — mode mise en page")

    def _set_background_temporary_lock(self, locked: bool) -> None:
        self._background_edit_locked = bool(locked)
        if locked:
            self._background_interaction_mode = None
            self._background_interaction_handle = None
            self._save_status_text.set("Fond temporairement verrouillé")
        else:
            self._save_status_text.set("Fond déverrouillé pour le réglage")
        self._draw_background_controls()

    def _remember_background_state(self) -> None:
        if self.workspace is not None:
            self.workspace._remember_current_state()

    def _snapshot_background_history(self):
        return dict(getattr(self.page, "background", {}))

    def _restore_background_history(self, state) -> None:
        if not isinstance(state, dict):
            return
        try:
            if hasattr(self.page, "_normalize_background"):
                self.page.background = self.page._normalize_background(state)
            else:
                self.page.background = dict(state)
            self.page.save(update_history=False)
            document = self._load_current_document()
            if document is not None:
                document.update_page_summary(self.page)
        except (OSError, RuntimeError, TypeError, ValueError):
            return
        self._background_selected = bool(
            self._background_edit_mode
            and self.page.background.get("active")
        )
        self._invalidate_background_cache()
        if self.workspace is not None:
            self.workspace.redraw()
        if (
            self._background_dialog is not None
            and self._background_dialog.winfo_exists()
        ):
            self._background_dialog.set_current_frame(
                self._background_effective_frame_mm()
            )

    def _apply_background_image(
        self,
        source_path: Path,
        scope: str,
        mode: str,
        keep_aspect_ratio: bool,
    ) -> bool:
        """Copie l'image, applique les réglages et conserve le mode Fond."""

        self._remember_background_state()
        try:
            previous = dict(getattr(self.page, "background", {}))
            preserve_manual_frame = bool(
                previous.get("active")
                and previous.get("mode") == "manuel"
                and mode == "manuel"
                and previous.get("portee", "page") == scope
            )
            resource_value = self._copy_background_resource(source_path)
            self.page.set_background(
                resource_value,
                scope=scope,
                fit_mode=mode,
                keep_aspect_ratio=keep_aspect_ratio,
            )

            if mode == "manuel":
                if preserve_manual_frame:
                    frame = {
                        "x": float(previous.get("x_mm", 0.0)),
                        "y": float(previous.get("y_mm", 0.0)),
                        "largeur": float(previous.get("largeur_mm", getattr(self.page, "width_mm", 148.0))),
                        "hauteur": float(previous.get("hauteur_mm", getattr(self.page, "height_mm", 210.0))),
                    }
                else:
                    frame = self._initial_manual_background_frame(
                        source_path,
                        scope,
                        keep_aspect_ratio,
                    )
                self.page.set_background_transform(
                    x_mm=frame["x"],
                    y_mm=frame["y"],
                    width_mm=frame["largeur"],
                    height_mm=frame["hauteur"],
                    keep_aspect_ratio=keep_aspect_ratio,
                )

            self._background_selected = self._background_edit_mode
            document = self._load_current_document()
            if document is not None:
                document.update_page_summary(self.page)
            self._invalidate_background_cache()
            if self.workspace is not None:
                self.workspace.redraw()
            if (
                self._background_dialog is not None
                and self._background_dialog.winfo_exists()
            ):
                self._background_dialog.set_current_frame(
                    self._background_effective_frame_mm()
                )
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            self._save_status_text.set(f"Image de fond non appliquée : {error}")
            return False

        self._save_status_text.set("Image de fond enregistrée — mode Fond actif")
        saved_path = self._resolve_background_resource()
        return saved_path if saved_path is not None else True

    def _initial_manual_background_frame(
        self,
        source_path: Path,
        scope: str,
        keep_aspect_ratio: bool,
    ) -> dict[str, float]:
        target = self._background_scope_box_mm(scope)

        if not keep_aspect_ratio:
            return dict(target)

        try:
            with Image.open(source_path) as image:
                image_width, image_height = image.size
        except (OSError, ValueError):
            return dict(target)

        if image_width <= 0 or image_height <= 0:
            return dict(target)

        scale = min(
            float(target["largeur"]) / image_width,
            float(target["hauteur"]) / image_height,
        )
        width = max(1.0, image_width * scale)
        height = max(1.0, image_height * scale)

        return {
            "x": float(target["x"])
            + (float(target["largeur"]) - width) / 2,
            "y": float(target["y"])
            + (float(target["hauteur"]) - height) / 2,
            "largeur": width,
            "hauteur": height,
        }

    def _remove_background_image(self) -> None:
        self._remember_background_state()
        try:
            self.page.clear_background()
            self._background_selected = False
            self._background_interaction_mode = None
            self._background_interaction_handle = None
            document = self._load_current_document()
            if document is not None:
                document.update_page_summary(self.page)
            self._invalidate_background_cache()
            if self.workspace is not None:
                self.workspace.redraw()
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            self._save_status_text.set(f"Fond non supprimé : {error}")
            return
        self._save_status_text.set("Image de fond supprimée")

    def _center_background(self, axis: str) -> None:
        background = getattr(self.page, "background", {})
        if not background.get("active"):
            self._save_status_text.set("Aucune image de fond")
            return
        if self._background_edit_locked:
            self._save_status_text.set("Déverrouillez temporairement le fond")
            return
        if str(background.get("mode", "remplir")) != "manuel":
            self._save_status_text.set("Le centrage manuel est disponible en mode libre")
            return

        target = self._background_scope_box_mm(str(background.get("portee", "page")))
        frame = self._background_effective_frame_mm(background)
        x = frame["x"]
        y = frame["y"]
        if axis in {"horizontal", "both"}:
            x = target["x"] + (target["largeur"] - frame["largeur"]) / 2
        if axis in {"vertical", "both"}:
            y = target["y"] + (target["hauteur"] - frame["hauteur"]) / 2

        self._remember_background_state()
        self.page.set_background_transform(
            x_mm=x,
            y_mm=y,
            width_mm=frame["largeur"],
            height_mm=frame["hauteur"],
            keep_aspect_ratio=bool(background.get("conserver_proportions", True)),
        )
        self._invalidate_background_cache()
        if self.workspace is not None:
            self.workspace.redraw()
        if self._background_dialog is not None:
            self._background_dialog.set_current_frame(self._background_effective_frame_mm())

    def _reset_background_position(self) -> None:
        background = getattr(self.page, "background", {})
        image_path = self._resolve_background_resource()
        if not background.get("active") or image_path is None:
            self._save_status_text.set("Aucune image de fond")
            return
        if self._background_edit_locked:
            self._save_status_text.set("Déverrouillez temporairement le fond")
            return

        self._remember_background_state()
        if str(background.get("mode", "remplir")) == "manuel":
            frame = self._initial_manual_background_frame(
                image_path,
                str(background.get("portee", "page")),
                bool(background.get("conserver_proportions", True)),
            )
            self.page.set_background_transform(
                x_mm=frame["x"],
                y_mm=frame["y"],
                width_mm=frame["largeur"],
                height_mm=frame["hauteur"],
                keep_aspect_ratio=bool(background.get("conserver_proportions", True)),
            )
        self._invalidate_background_cache()
        if self.workspace is not None:
            self.workspace.redraw()
        if self._background_dialog is not None:
            self._background_dialog.set_current_frame(self._background_effective_frame_mm())

    def _project_root(self) -> Path | None:
        """Retrouve le dossier racine du projet depuis la page ouverte."""

        page_root = getattr(
            self.page,
            "root",
            None,
        )

        if page_root is not None:
            try:
                current = Path(page_root).resolve()
            except (OSError, RuntimeError, TypeError, ValueError):
                current = Path(page_root)

            for candidate in (current, *current.parents):
                if (candidate / "project.json").is_file():
                    return candidate

            # Structure attendue :
            # projet/documents/<document>/pages/page_XXXX
            if (
                current.parent.name == "pages"
                and len(current.parents) >= 4
            ):
                return current.parents[3]

        widget = self.parent

        while widget is not None:
            project = getattr(widget, "project", None)
            project_root = getattr(project, "root", None)

            if project_root is not None:
                return Path(project_root)

            application = getattr(widget, "application", None)
            project = getattr(application, "project", None)
            project_root = getattr(project, "root", None)

            if project_root is not None:
                return Path(project_root)

            widget = getattr(widget, "master", None)

        return None

    def _copy_background_resource(
        self,
        source_path: Path,
    ) -> str:
        source = Path(source_path).resolve()

        if not source.exists():
            raise FileNotFoundError(
                "L’image sélectionnée est introuvable."
            )

        project_root = self._project_root()

        if project_root is None:
            return str(source)

        try:
            relative_existing = source.relative_to(
                project_root.resolve()
            )
            return relative_existing.as_posix()
        except ValueError:
            pass

        destination_folder = (
            project_root
            / "ressources"
            / "images"
        )
        destination_folder.mkdir(
            parents=True,
            exist_ok=True,
        )

        stem = source.stem.strip() or "fond"
        suffix = source.suffix.lower() or ".png"
        destination = (
            destination_folder
            / f"{stem}{suffix}"
        )

        index = 2

        while destination.exists():
            try:
                if (
                    destination.resolve()
                    == source.resolve()
                ):
                    break
            except OSError:
                pass

            destination = (
                destination_folder
                / f"{stem}_{index}{suffix}"
            )
            index += 1

        if not destination.exists():
            shutil.copy2(
                source,
                destination,
            )

        return destination.relative_to(
            project_root
        ).as_posix()

    def _resolve_background_resource(
        self,
    ) -> Path | None:
        background = getattr(
            self.page,
            "background",
            {},
        )

        if not background.get("active"):
            return None

        resource = str(
            background.get(
                "ressource",
                "",
            )
        ).strip()

        if not resource:
            return None

        path = Path(resource)

        if path.is_absolute():
            return path if path.exists() else None

        project_root = self._project_root()

        if project_root is None:
            return None

        resolved = (
            project_root / path
        ).resolve()

        return resolved if resolved.exists() else None

    def _background_scope_box_mm(
        self,
        scope: str,
    ) -> dict[str, float]:
        if scope == "fonds_perdus":
            left = max(0.0, float(getattr(self.page, "bleed_left_mm", 0.0)))
            top = max(0.0, float(getattr(self.page, "bleed_top_mm", 0.0)))
            right = max(0.0, float(getattr(self.page, "bleed_right_mm", 0.0)))
            bottom = max(0.0, float(getattr(self.page, "bleed_bottom_mm", 0.0)))
            return {
                "x": -left,
                "y": -top,
                "largeur": max(1.0, float(getattr(self.page, "width_mm", 148.0)) + left + right),
                "hauteur": max(1.0, float(getattr(self.page, "height_mm", 210.0)) + top + bottom),
            }

        if (
            scope == "surface_composition"
            and hasattr(self.page, "composition_box_mm")
        ):
            is_verso = (
                int(getattr(self.page, "number", 1)) % 2 == 0
            )
            box = self.page.composition_box_mm(
                verso=is_verso
            )
            return {
                "x": float(box["x"]),
                "y": float(box["y"]),
                "largeur": max(1.0, float(box["largeur"])),
                "hauteur": max(1.0, float(box["hauteur"])),
            }

        return {
            "x": 0.0,
            "y": 0.0,
            "largeur": max(
                1.0,
                float(getattr(self.page, "width_mm", 148.0)),
            ),
            "hauteur": max(
                1.0,
                float(getattr(self.page, "height_mm", 210.0)),
            ),
        }

    def _background_effective_frame_mm(
        self,
        background: dict | None = None,
    ) -> dict[str, float]:
        background = background or getattr(
            self.page,
            "background",
            {},
        )
        scope = str(background.get("portee", "page"))
        target = self._background_scope_box_mm(scope)
        mode = str(background.get("mode", "remplir"))

        if mode == "manuel":
            return {
                "x": float(background.get("x_mm", target["x"])),
                "y": float(background.get("y_mm", target["y"])),
                "largeur": max(
                    1.0,
                    float(
                        background.get(
                            "largeur_mm",
                            target["largeur"],
                        )
                    ),
                ),
                "hauteur": max(
                    1.0,
                    float(
                        background.get(
                            "hauteur_mm",
                            target["hauteur"],
                        )
                    ),
                ),
            }

        if mode == "etirer":
            return dict(target)

        image_path = self._resolve_background_resource()

        if image_path is None:
            return dict(target)

        try:
            with Image.open(image_path) as image:
                image_width, image_height = image.size
        except (OSError, ValueError):
            return dict(target)

        if image_width <= 0 or image_height <= 0:
            return dict(target)

        if mode == "ajuster":
            scale = min(
                target["largeur"] / image_width,
                target["hauteur"] / image_height,
            )
        else:
            scale = max(
                target["largeur"] / image_width,
                target["hauteur"] / image_height,
            )

        width = max(1.0, image_width * scale)
        height = max(1.0, image_height * scale)

        return {
            "x": target["x"] + (target["largeur"] - width) / 2,
            "y": target["y"] + (target["hauteur"] - height) / 2,
            "largeur": width,
            "hauteur": height,
        }

    def _background_event_point_mm(self, event) -> Point:
        canvas = self.workspace
        return Point(
            canvas.viewport.px_to_mm(
                event.x - canvas.page_left
            ),
            canvas.viewport.px_to_mm(
                event.y - canvas.page_top
            ),
        )

    @staticmethod
    def _point_inside_background_frame(
        point: Point,
        frame: dict[str, float],
    ) -> bool:
        return (
            frame["x"] <= point.x <= frame["x"] + frame["largeur"]
            and frame["y"] <= point.y <= frame["y"] + frame["hauteur"]
        )

    def _begin_background_interaction(
        self,
        event,
        *,
        mode: str,
        handle: str | None = None,
    ) -> str | None:
        canvas = self.workspace
        background = getattr(self.page, "background", {})

        if (
            canvas is None
            or getattr(self.page, "locked", False)
            or not self._background_edit_mode
            or self._background_edit_locked
            or str(background.get("mode", "remplir")) != "manuel"
            or not background.get("active")
        ):
            return None

        frame = self._background_effective_frame_mm(background)
        point = self._background_event_point_mm(event)

        self._background_selected = True
        self._background_interaction_mode = mode
        self._background_interaction_handle = handle
        self._background_interaction_start_mm = point
        self._background_original_frame = dict(frame)
        self._background_drag_changed = False
        self._background_history_recorded = False

        try:
            canvas._clear_reference_state(
                clear_selection=True,
                redraw=True,
                notify=True,
            )
        except AttributeError:
            pass

        self._draw_background_controls()
        canvas.focus_set()
        return "break"

    def _on_background_pre_press(self, event):
        canvas = self.workspace
        if canvas is None or not self._background_edit_mode:
            return None

        if self._background_edit_locked:
            return "break"

        current = canvas.find_withtag("current")
        tags = set(canvas.gettags(current[-1])) if current else set()

        if self._background_handle_tag in tags:
            return self._on_background_handle_press(event)
        if self._background_frame_tag in tags:
            return self._on_background_frame_press(event)
        if self._background_canvas_tag in tags:
            self._on_background_image_press(event)
            return "break"

        # En mode Fond, aucun objet de mise en page ne reçoit le clic.
        return "break"

    def _on_background_image_press(self, event):
        background = getattr(self.page, "background", {})
        frame = self._background_effective_frame_mm(background)
        point = self._background_event_point_mm(event)

        if not self._point_inside_background_frame(point, frame):
            return None

        if background.get("portee") == "surface_composition":
            visible_scope = self._background_scope_box_mm(
                "surface_composition"
            )
            if not self._point_inside_background_frame(
                point,
                visible_scope,
            ):
                return None

        return self._begin_background_interaction(
            event,
            mode="move",
        )

    def _on_background_frame_press(self, event):
        return self._begin_background_interaction(
            event,
            mode="move",
        )

    def _on_background_handle_press(self, event):
        canvas = self.workspace

        if canvas is None:
            return None

        current = canvas.find_withtag("current")

        if not current:
            return None

        handle = None
        for tag in canvas.gettags(current[-1]):
            if tag.startswith("background_handle:"):
                handle = tag.split(":", 1)[1]
                break

        if handle is None:
            return None

        return self._begin_background_interaction(
            event,
            mode="resize",
            handle=handle,
        )

    def _on_canvas_background_press(self, event) -> None:
        if self._background_interaction_mode is not None:
            return

        canvas = self.workspace

        if canvas is None:
            return

        current = canvas.find_withtag("current")
        tags = (
            set(canvas.gettags(current[-1]))
            if current
            else set()
        )

        if (
            self._background_canvas_tag in tags
            or self._background_frame_tag in tags
            or self._background_handle_tag in tags
        ):
            return

        if self._background_selected:
            self._background_selected = False
            self._draw_background_controls()

    def _on_background_drag(self, event):
        if (
            not self._background_edit_mode
            or self._background_edit_locked
            or self._background_interaction_mode is None
            or self._background_interaction_start_mm is None
            or self._background_original_frame is None
        ):
            return None

        canvas = self.workspace

        if canvas is None:
            return None

        current = self._background_event_point_mm(event)
        start = self._background_interaction_start_mm
        dx = current.x - start.x
        dy = current.y - start.y
        original = self._background_original_frame

        if abs(dx) < 0.001 and abs(dy) < 0.001:
            return "break"

        if not self._background_history_recorded:
            self._remember_background_state()
            self._background_history_recorded = True

        if self._background_interaction_mode == "move":
            scope = self._background_scope_box_mm(
                str(
                    getattr(
                        self.page,
                        "background",
                        {},
                    ).get("portee", "page")
                )
            )
            minimum_visible = min(
                5.0,
                original["largeur"],
                original["hauteur"],
            )
            new_x = original["x"] + dx
            new_y = original["y"] + dy
            new_x = min(
                scope["x"] + scope["largeur"] - minimum_visible,
                max(
                    scope["x"] - original["largeur"] + minimum_visible,
                    new_x,
                ),
            )
            new_y = min(
                scope["y"] + scope["hauteur"] - minimum_visible,
                max(
                    scope["y"] - original["hauteur"] + minimum_visible,
                    new_y,
                ),
            )
            frame = {
                "x": new_x,
                "y": new_y,
                "largeur": original["largeur"],
                "hauteur": original["hauteur"],
            }
        else:
            frame = self._resize_background_frame(
                original,
                self._background_interaction_handle or "se",
                dx,
                dy,
                bool(
                    getattr(
                        self.page,
                        "background",
                        {},
                    ).get("conserver_proportions", True)
                ),
            )

        background = self.page.background
        background.update(
            {
                "mode": "manuel",
                "cadre_automatique": False,
                "x_mm": frame["x"],
                "y_mm": frame["y"],
                "largeur_mm": frame["largeur"],
                "hauteur_mm": frame["hauteur"],
            }
        )
        self._background_drag_changed = True
        self._invalidate_background_cache()
        canvas.redraw()
        return "break"

    @staticmethod
    def _resize_background_frame(
        frame: dict[str, float],
        handle: str,
        dx: float,
        dy: float,
        keep_aspect_ratio: bool,
    ) -> dict[str, float]:
        x = float(frame["x"])
        y = float(frame["y"])
        width = max(1.0, float(frame["largeur"]))
        height = max(1.0, float(frame["hauteur"]))
        minimum = 3.0

        if not keep_aspect_ratio:
            left = x + (dx if "w" in handle else 0.0)
            right = x + width + (dx if "e" in handle else 0.0)
            top = y + (dy if "n" in handle else 0.0)
            bottom = y + height + (dy if "s" in handle else 0.0)

            if right - left < minimum:
                if "w" in handle:
                    left = right - minimum
                else:
                    right = left + minimum
            if bottom - top < minimum:
                if "n" in handle:
                    top = bottom - minimum
                else:
                    bottom = top + minimum

            return {
                "x": left,
                "y": top,
                "largeur": right - left,
                "hauteur": bottom - top,
            }

        aspect = width / height
        min_width = max(minimum, minimum * aspect)
        min_height = max(minimum, minimum / max(aspect, 0.001))

        if handle in {"e", "w"}:
            proposed_width = (
                width + dx
                if handle == "e"
                else width - dx
            )
            new_width = max(min_width, proposed_width)
            new_height = new_width / aspect
            new_x = x if handle == "e" else x + width - new_width
            new_y = y + (height - new_height) / 2
        elif handle in {"n", "s"}:
            proposed_height = (
                height + dy
                if handle == "s"
                else height - dy
            )
            new_height = max(min_height, proposed_height)
            new_width = new_height * aspect
            new_x = x + (width - new_width) / 2
            new_y = y if handle == "s" else y + height - new_height
        else:
            proposed_width = width + (dx if "e" in handle else -dx)
            proposed_height = height + (dy if "s" in handle else -dy)
            width_change = abs(proposed_width - width) / width
            height_change = abs(proposed_height - height) / height

            if width_change >= height_change:
                new_width = max(min_width, proposed_width)
                new_height = new_width / aspect
            else:
                new_height = max(min_height, proposed_height)
                new_width = new_height * aspect

            new_x = x if "e" in handle else x + width - new_width
            new_y = y if "s" in handle else y + height - new_height

        return {
            "x": new_x,
            "y": new_y,
            "largeur": new_width,
            "hauteur": new_height,
        }

    def _on_background_release(self, _event):
        if self._background_interaction_mode is None:
            return None

        changed = self._background_drag_changed
        self._background_interaction_mode = None
        self._background_interaction_handle = None
        self._background_interaction_start_mm = None
        self._background_original_frame = None
        self._background_drag_changed = False
        self._background_history_recorded = False

        if not changed:
            self._draw_background_controls()
            return "break"

        background = getattr(self.page, "background", {})

        try:
            self.page.set_background_transform(
                x_mm=float(background.get("x_mm", 0.0)),
                y_mm=float(background.get("y_mm", 0.0)),
                width_mm=float(background.get("largeur_mm", 1.0)),
                height_mm=float(background.get("hauteur_mm", 1.0)),
                keep_aspect_ratio=bool(
                    background.get("conserver_proportions", True)
                ),
            )

            document = self._load_current_document()
            if document is not None:
                document.update_page_summary(self.page)

            self._save_status_text.set(
                "Position et dimensions du fond enregistrées"
            )
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            self._save_status_text.set(
                f"Fond non enregistré : {error}"
            )

        self._invalidate_background_cache()
        if self.workspace is not None:
            self.workspace.redraw()
        if (
            self._background_dialog is not None
            and self._background_dialog.winfo_exists()
        ):
            self._background_dialog.set_current_frame(
                self._background_effective_frame_mm()
            )
        return "break"

    def _move_background_with_keyboard(self, event):
        if not self._background_edit_mode:
            return None
        background = getattr(self.page, "background", {})
        if (
            self._background_edit_locked
            or not background.get("active")
            or str(background.get("mode", "remplir")) != "manuel"
        ):
            return "break"

        frame = self._background_effective_frame_mm(background)
        step = 10.0 if (event.state & 0x0001) else 1.0
        dx = dy = 0.0
        if event.keysym == "Left":
            dx = -step
        elif event.keysym == "Right":
            dx = step
        elif event.keysym == "Up":
            dy = -step
        elif event.keysym == "Down":
            dy = step
        else:
            return None

        self._remember_background_state()
        self.page.set_background_transform(
            x_mm=frame["x"] + dx,
            y_mm=frame["y"] + dy,
            width_mm=frame["largeur"],
            height_mm=frame["hauteur"],
            keep_aspect_ratio=bool(background.get("conserver_proportions", True)),
        )
        self._invalidate_background_cache()
        if self.workspace is not None:
            self.workspace.redraw()
        if self._background_dialog is not None:
            self._background_dialog.set_current_frame(self._background_effective_frame_mm())
        return "break"

    def _draw_background_controls(self) -> None:
        canvas = self.workspace

        if canvas is None:
            return

        try:
            canvas.delete(self._background_selection_tag)
        except tk.TclError:
            return

        background = getattr(self.page, "background", {})

        if not (
            self._background_edit_mode
            and self._background_selected
            and background.get("active")
            and background.get("ressource")
        ):
            return

        frame = self._background_effective_frame_mm(background)
        left = canvas.page_left + canvas.viewport.mm_to_px(frame["x"])
        top = canvas.page_top + canvas.viewport.mm_to_px(frame["y"])
        right = left + canvas.viewport.mm_to_px(frame["largeur"])
        bottom = top + canvas.viewport.mm_to_px(frame["hauteur"])

        canvas.create_rectangle(
            left,
            top,
            right,
            bottom,
            fill="",
            outline="#2D7FF9",
            width=2,
            tags=(
                self._background_selection_tag,
                self._background_frame_tag,
            ),
        )

        if (
            self._background_edit_locked
            or str(background.get("mode", "remplir")) != "manuel"
        ):
            canvas.tag_raise(self._background_selection_tag)
            return

        middle_x = (left + right) / 2
        middle_y = (top + bottom) / 2
        positions = {
            "nw": (left, top),
            "n": (middle_x, top),
            "ne": (right, top),
            "e": (right, middle_y),
            "se": (right, bottom),
            "s": (middle_x, bottom),
            "sw": (left, bottom),
            "w": (left, middle_y),
        }
        half = 5

        for handle, (x, y) in positions.items():
            canvas.create_rectangle(
                x - half,
                y - half,
                x + half,
                y + half,
                fill="#FFFFFF",
                outline="#2D7FF9",
                width=2,
                tags=(
                    self._background_selection_tag,
                    self._background_handle_tag,
                    f"background_handle:{handle}",
                ),
            )

        canvas.tag_raise(self._background_selection_tag)

    def _invalidate_background_cache(self) -> None:
        self._background_photo = None
        self._background_render_cache_key = None
        self._background_render_cache_image = None

    def _draw_page_background(self, *_args) -> None:
        """Affiche le fond sur sa surface réelle, fonds perdus compris."""

        canvas = self.workspace
        if canvas is None:
            return

        try:
            if not canvas.winfo_exists():
                return
            canvas.delete(self._background_canvas_tag)
            background = getattr(self.page, "background", {})
            if not (background.get("active") and background.get("ressource")):
                self._background_photo = None
                return

            image_path = self._resolve_background_resource()
            if image_path is None:
                self._background_photo = None
                return

            scope = str(background.get("portee", "page"))
            scope_box = self._background_scope_box_mm(scope)
            scope_width_px = max(
                1,
                int(round(canvas.viewport.mm_to_px(scope_box["largeur"]))),
            )
            scope_height_px = max(
                1,
                int(round(canvas.viewport.mm_to_px(scope_box["hauteur"]))),
            )

            cache_key = (
                str(image_path),
                image_path.stat().st_mtime_ns,
                scope_width_px,
                scope_height_px,
                tuple(sorted((key, float(value)) for key, value in scope_box.items())),
                str(background.get("mode", "remplir")),
                bool(background.get("conserver_proportions", True)),
                float(background.get("opacite", 1.0)),
                float(background.get("x_mm", 0.0)),
                float(background.get("y_mm", 0.0)),
                float(background.get("largeur_mm", scope_box["largeur"])),
                float(background.get("hauteur_mm", scope_box["hauteur"])),
            )

            if cache_key != self._background_render_cache_key:
                self._background_render_cache_image = self._render_background_scope_image(
                    image_path=image_path,
                    scope_box_mm=scope_box,
                    output_width_px=scope_width_px,
                    output_height_px=scope_height_px,
                )
                self._background_render_cache_key = cache_key

            rendered = self._background_render_cache_image
            if rendered is None:
                return

            existing_items = canvas.find_all()
            self._background_photo = ImageTk.PhotoImage(rendered)
            background_item = canvas.create_image(
                canvas.page_left + canvas.viewport.mm_to_px(scope_box["x"]),
                canvas.page_top + canvas.viewport.mm_to_px(scope_box["y"]),
                anchor="nw",
                image=self._background_photo,
                tags=(self._background_canvas_tag, "image_de_fond"),
            )
            if len(existing_items) >= 3:
                canvas.tag_lower(background_item, existing_items[2])

        except (
            AttributeError,
            OSError,
            RuntimeError,
            tk.TclError,
            TypeError,
            ValueError,
        ):
            self._background_photo = None

    def _render_background_scope_image(
        self,
        *,
        image_path: Path,
        scope_box_mm: dict[str, float],
        output_width_px: int,
        output_height_px: int,
    ) -> Image.Image:
        background = getattr(self.page, "background", {})
        with Image.open(image_path) as source:
            original = source.convert("RGBA")

        output = Image.new(
            "RGBA",
            (output_width_px, output_height_px),
            (255, 255, 255, 0),
        )
        scale_x = output_width_px / max(float(scope_box_mm["largeur"]), 0.001)
        scale_y = output_height_px / max(float(scope_box_mm["hauteur"]), 0.001)
        mode = str(background.get("mode", "remplir"))

        if mode == "manuel":
            frame = self._background_effective_frame_mm(background)
            target_x = int(round((frame["x"] - scope_box_mm["x"]) * scale_x))
            target_y = int(round((frame["y"] - scope_box_mm["y"]) * scale_y))
            target_width = max(1, int(round(frame["largeur"] * scale_x)))
            target_height = max(1, int(round(frame["hauteur"] * scale_y)))
            rendered = original.resize(
                (target_width, target_height),
                Image.Resampling.LANCZOS,
            )
        elif mode == "ajuster":
            contained = ImageOps.contain(
                original,
                (output_width_px, output_height_px),
                Image.Resampling.LANCZOS,
            )
            rendered = contained
            target_x = (output_width_px - contained.width) // 2
            target_y = (output_height_px - contained.height) // 2
        else:
            rendered = ImageOps.fit(
                original,
                (output_width_px, output_height_px),
                Image.Resampling.LANCZOS,
                centering=(0.5, 0.5),
            )
            target_x = 0
            target_y = 0

        opacity = max(0.0, min(1.0, float(background.get("opacite", 1.0))))
        if opacity < 1.0:
            alpha = rendered.getchannel("A").point(lambda value: int(value * opacity))
            rendered.putalpha(alpha)

        output.alpha_composite(rendered, (target_x, target_y))
        return output

    def _install_page_guides(self) -> None:
        """Maintient le fond et les repères visibles sur le canvas."""

        if self.workspace is None:
            return

        base_redraw = self.workspace.redraw
        self._workspace_base_redraw = base_redraw

        def redraw_with_overlays(*args, **kwargs):
            result = base_redraw(
                *args,
                **kwargs,
            )
            self._draw_page_overlays()
            return result

        self.workspace.redraw = redraw_with_overlays

        # Le Viewport conserve déjà le redraw d'origine. Ce second écouteur
        # replace ensuite le fond et les guides après le zoom ou le déplacement.
        self.workspace.viewport.add_listener(
            self._draw_page_overlays,
        )

        self.workspace.bind(
            "<Configure>",
            lambda _event: self.parent.after_idle(
                self._draw_page_overlays
            ),
            add="+",
        )

        bindtags = list(self.workspace.bindtags())
        if self._background_bindtag not in bindtags:
            bindtags.insert(0, self._background_bindtag)
            self.workspace.bindtags(tuple(bindtags))

        self.workspace.bind_class(
            self._background_bindtag,
            "<ButtonPress-1>",
            self._on_background_pre_press,
        )
        self.workspace.bind_class(
            self._background_bindtag,
            "<B1-Motion>",
            self._on_background_drag,
        )
        self.workspace.bind_class(
            self._background_bindtag,
            "<ButtonRelease-1>",
            self._on_background_release,
        )
        for key in ("<Left>", "<Right>", "<Up>", "<Down>"):
            self.workspace.bind_class(
                self._background_bindtag,
                key,
                self._move_background_with_keyboard,
            )

    def _draw_page_overlays(self, *_args) -> None:
        self._draw_page_background()
        self._draw_page_guides()
        self._draw_background_controls()

    def _draw_page_guides(self, *_args) -> None:
        """Dessine les limites de composition et de fond perdu."""

        canvas = self.workspace

        if canvas is None:
            return

        try:
            if not canvas.winfo_exists():
                return

            canvas.delete(
                self._page_guide_tag
            )

            page_left = float(
                canvas.page_left
            )
            page_top = float(
                canvas.page_top
            )

            page_width_px = canvas.viewport.mm_to_px(
                canvas.page_format.width_mm
            )
            page_height_px = canvas.viewport.mm_to_px(
                canvas.page_format.height_mm
            )

            bleed_top = max(
                0.0,
                float(
                    getattr(
                        self.page,
                        "bleed_top_mm",
                        0.0,
                    )
                ),
            )
            bleed_right = max(
                0.0,
                float(
                    getattr(
                        self.page,
                        "bleed_right_mm",
                        0.0,
                    )
                ),
            )
            bleed_bottom = max(
                0.0,
                float(
                    getattr(
                        self.page,
                        "bleed_bottom_mm",
                        0.0,
                    )
                ),
            )
            bleed_left = max(
                0.0,
                float(
                    getattr(
                        self.page,
                        "bleed_left_mm",
                        0.0,
                    )
                ),
            )

            if any(
                value > 0
                for value in (
                    bleed_top,
                    bleed_right,
                    bleed_bottom,
                    bleed_left,
                )
            ):
                bleed_x1 = (
                    page_left
                    - canvas.viewport.mm_to_px(
                        bleed_left
                    )
                )
                bleed_y1 = (
                    page_top
                    - canvas.viewport.mm_to_px(
                        bleed_top
                    )
                )
                bleed_x2 = (
                    page_left
                    + page_width_px
                    + canvas.viewport.mm_to_px(
                        bleed_right
                    )
                )
                bleed_y2 = (
                    page_top
                    + page_height_px
                    + canvas.viewport.mm_to_px(
                        bleed_bottom
                    )
                )

                canvas.create_rectangle(
                    bleed_x1,
                    bleed_y1,
                    bleed_x2,
                    bleed_y2,
                    outline="#C97945",
                    width=2,
                    dash=(7, 4),
                    tags=(
                        self._page_guide_tag,
                        "fond_perdu",
                    ),
                )
                canvas.create_text(
                    bleed_x1 + 5,
                    bleed_y1 + 5,
                    text="Fond perdu",
                    anchor="nw",
                    fill="#9A562D",
                    font=(Fonts.FAMILY, 9, "bold"),
                    tags=(
                        self._page_guide_tag,
                        "fond_perdu",
                    ),
                )

            is_verso = (
                int(
                    getattr(
                        self.page,
                        "number",
                        1,
                    )
                ) % 2 == 0
            )

            if hasattr(
                self.page,
                "composition_box_mm",
            ):
                composition = self.page.composition_box_mm(
                    verso=is_verso
                )
            else:
                margin_top = float(
                    getattr(
                        self.page,
                        "margin_top_mm",
                        15.0,
                    )
                )
                margin_bottom = float(
                    getattr(
                        self.page,
                        "margin_bottom_mm",
                        15.0,
                    )
                )
                margin_inside = float(
                    getattr(
                        self.page,
                        "margin_inside_mm",
                        15.0,
                    )
                )
                margin_outside = float(
                    getattr(
                        self.page,
                        "margin_outside_mm",
                        15.0,
                    )
                )

                left_margin = (
                    margin_outside
                    if is_verso
                    else margin_inside
                )
                right_margin = (
                    margin_inside
                    if is_verso
                    else margin_outside
                )

                composition = {
                    "x": left_margin,
                    "y": margin_top,
                    "largeur": (
                        canvas.page_format.width_mm
                        - left_margin
                        - right_margin
                    ),
                    "hauteur": (
                        canvas.page_format.height_mm
                        - margin_top
                        - margin_bottom
                    ),
                }

            composition_width = max(
                0.0,
                float(
                    composition.get(
                        "largeur",
                        0.0,
                    )
                ),
            )
            composition_height = max(
                0.0,
                float(
                    composition.get(
                        "hauteur",
                        0.0,
                    )
                ),
            )

            if (
                composition_width > 0
                and composition_height > 0
            ):
                margin_x1 = (
                    page_left
                    + canvas.viewport.mm_to_px(
                        float(
                            composition.get(
                                "x",
                                0.0,
                            )
                        )
                    )
                )
                margin_y1 = (
                    page_top
                    + canvas.viewport.mm_to_px(
                        float(
                            composition.get(
                                "y",
                                0.0,
                            )
                        )
                    )
                )
                margin_x2 = (
                    margin_x1
                    + canvas.viewport.mm_to_px(
                        composition_width
                    )
                )
                margin_y2 = (
                    margin_y1
                    + canvas.viewport.mm_to_px(
                        composition_height
                    )
                )

                canvas.create_rectangle(
                    margin_x1,
                    margin_y1,
                    margin_x2,
                    margin_y2,
                    outline="#4F7FA3",
                    width=2,
                    dash=(6, 4),
                    tags=(
                        self._page_guide_tag,
                        "marges",
                    ),
                )
                canvas.create_text(
                    margin_x1 + 5,
                    margin_y1 + 5,
                    text="Zone de composition",
                    anchor="nw",
                    fill="#365F7B",
                    font=(Fonts.FAMILY, 9, "bold"),
                    tags=(
                        self._page_guide_tag,
                        "marges",
                    ),
                )

            canvas.tag_raise(
                self._page_guide_tag
            )

        except (
            AttributeError,
            RuntimeError,
            tk.TclError,
            TypeError,
            ValueError,
        ):
            return

    def _create_rulers(self, parent) -> None:

        if self.workspace is None:
            return

        horizontal_ruler = HorizontalRuler(
            parent,
            self.workspace,
        )
        horizontal_ruler.grid(
            row=0,
            column=1,
            sticky="ew",
        )

        vertical_ruler = VerticalRuler(
            parent,
            self.workspace,
        )
        vertical_ruler.grid(
            row=1,
            column=0,
            sticky="ns",
        )

        self.workspace.viewport.add_listener(
            horizontal_ruler.redraw,
        )

        self.workspace.viewport.add_listener(
            vertical_ruler.redraw,
        )

    def _create_status_bar(self, parent) -> None:

        if self.workspace is None:
            return

        self.status_bar = StatusBar(parent)
        self.status_bar.pack(
            fill="x",
            side="bottom",
        )

        self.status_bar.attach(self.workspace)

        self.workspace.add_mouse_listener(
            self.status_bar.refresh,
        )

    def _prepare_first_display(self) -> None:

        if self.workspace is None:
            return

        if not self.workspace.winfo_exists():
            return

        self.workspace.update_idletasks()

        width = self.workspace.winfo_width()
        height = self.workspace.winfo_height()

        if (
            width < self.MIN_READY_SIZE
            or height < self.MIN_READY_SIZE
        ):
            self._display_retry_count += 1

            if self._display_retry_count <= self.MAX_DISPLAY_RETRIES:
                self.parent.after(
                    self.DISPLAY_RETRY_DELAY_MS,
                    self._prepare_first_display,
                )
            return

        self.workspace._fit_page()
        self.workspace.redraw()

    def _resolve_page_format(self):

        format_name = str(
            getattr(
                self.page,
                "format",
                "A5",
            )
        ).strip() or "A5"

        width_mm = getattr(
            self.page,
            "width_mm",
            None,
        )
        height_mm = getattr(
            self.page,
            "height_mm",
            None,
        )

        try:
            width_value = float(width_mm)
            height_value = float(height_mm)
        except (TypeError, ValueError):
            width_value = 0.0
            height_value = 0.0

        if width_value > 0 and height_value > 0:
            return type(A5)(
                name=format_name,
                width_mm=width_value,
                height_mm=height_value,
            )

        page_format = PAGE_FORMATS.get(
            format_name,
            A5,
        )

        orientation = str(
            getattr(
                self.page,
                "orientation",
                "Portrait",
            )
        ).strip().lower()

        if orientation == "paysage":
            return type(page_format)(
                name=page_format.name,
                width_mm=page_format.height_mm,
                height_mm=page_format.width_mm,
            )

        return page_format

    def _load_page_objects(self) -> list[CanvasObject]:

        objects: list[CanvasObject] = []

        for element in getattr(self.page, "elements", []):
            if element.get("type") != "canvas_object":
                continue

            bounds = element.get("bounds", {})

            try:
                objects.append(
                    CanvasObject(
                        kind=str(element.get("kind", "rectangle")),
                        bounds=Rect(
                            Point(
                                float(bounds.get("x", 0.0)),
                                float(bounds.get("y", 0.0)),
                            ),
                            Size(
                                float(bounds.get("width", 0.0)),
                                float(bounds.get("height", 0.0)),
                            ),
                        ),
                        fill=str(element.get("fill", "#F4F4F4")),
                        outline=str(element.get("outline", "#222222")),
                        line_width=int(element.get("line_width", 2)),
                        text=str(element.get("text", "Bloc de texte")),
                        text_color=str(element.get("text_color", "#222222")),
                        font_family=str(element.get("font_family", "Arial")),
                        font_size=int(element.get("font_size", 12)),
                        bold=bool(element.get("bold", False)),
                        italic=bool(element.get("italic", False)),
                        align=str(element.get("align", "left")),
                        rotation=float(element.get("rotation", 0.0)),
                        locked=bool(element.get("locked", False)),
                        group_id=(
                            int(element["group_id"])
                            if element.get("group_id") is not None
                            else None
                        ),
                    )
                )
            except (TypeError, ValueError):
                continue

        if objects:
            return objects

        saved_objects = getattr(
            self.page,
            "_editor_objects",
            None,
        )

        return list(saved_objects or [])

    @staticmethod
    def _serialize_object(canvas_object: CanvasObject) -> dict:

        return {
            "type": "canvas_object",
            "kind": canvas_object.kind,
            "bounds": {
                "x": canvas_object.bounds.left,
                "y": canvas_object.bounds.top,
                "width": canvas_object.bounds.width,
                "height": canvas_object.bounds.height,
            },
            "fill": canvas_object.fill,
            "outline": canvas_object.outline,
            "line_width": canvas_object.line_width,
            "text": canvas_object.text,
            "text_color": canvas_object.text_color,
            "font_family": canvas_object.font_family,
            "font_size": canvas_object.font_size,
            "bold": canvas_object.bold,
            "italic": canvas_object.italic,
            "align": canvas_object.align,
            "rotation": canvas_object.rotation,
            "locked": canvas_object.locked,
            "group_id": canvas_object.group_id,
        }

    def _schedule_canvas_autosave(self, event=None) -> None:

        if self.root is None or self.workspace is None:
            return

        # after_idle garantit que le canvas a terminé de calculer la rotation
        # ou les nouvelles dimensions avant la sérialisation.
        self.root.after_idle(
            lambda: self._save_page_objects(show_status=False),
        )

    def _save_shortcut(self, event=None) -> str:

        self._save_page_objects(show_status=True)
        return "break"

    def _save_page_objects(
        self,
        show_status: bool = False,
    ) -> None:

        if self.workspace is None:
            return

        current_objects = list(self.workspace._objects)
        self.page._editor_objects = current_objects

        preserved_elements = [
            element
            for element in getattr(self.page, "elements", [])
            if element.get("type") != "canvas_object"
        ]

        self.page.elements = preserved_elements + [
            self._serialize_object(canvas_object)
            for canvas_object in current_objects
        ]

        save_page = getattr(self.page, "save", None)

        if callable(save_page):
            save_page(update_history=False)

        if show_status:
            self._save_status_text.set("Enregistré")
            if self.root is not None:
                self.root.after(
                    1500,
                    lambda: self._save_status_text.set(""),
                )

    def _document_root(self) -> Path | None:
        """Retrouve le dossier du livre qui contient la page courante."""

        page_root = getattr(
            self.page,
            "root",
            None,
        )

        if page_root is None:
            return None

        document_root = Path(page_root).parent.parent

        if not (document_root / "document.json").exists():
            return None

        return document_root

    def _load_current_document(self) -> Document | None:
        """Charge le livre auquel appartient la page courante."""

        document_root = self._document_root()

        if document_root is None:
            return None

        try:
            return Document().load(document_root)
        except (
            OSError,
            RuntimeError,
            ValueError,
        ):
            return None

    def _open_page_setup(self) -> None:
        """Ouvre les réglages physiques de la page."""

        if getattr(self.page, "locked", False):
            self._save_status_text.set(
                "Cette page est verrouillée"
            )
            return

        PageSetupDialog(
            parent=self.parent,
            page=self.page,
            on_validate=self._apply_page_setup,
        )

    def _apply_page_setup(
        self,
        settings: dict,
    ) -> None:
        """Applique le format, les marges et les fonds perdus."""

        try:
            self._save_page_objects(
                show_status=False,
            )

            if settings["format"] == PageSetupDialog.FREE_FORMAT_LABEL:
                self.page.set_custom_format(
                    settings["width_mm"],
                    settings["height_mm"],
                    orientation=settings["orientation"],
                    label="Format libre",
                )
            else:
                self.page.set_format(
                    settings["format"],
                    settings["orientation"],
                )

            self.page.set_margins(
                **settings["margins"],
            )
            self.page.set_bleed(
                **settings["bleed"],
            )

            document = self._load_current_document()

            if document is not None:
                document.update_page_summary(
                    self.page
                )

        except (
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
        ) as error:
            self._save_status_text.set(
                f"Réglages non appliqués : {error}"
            )
            return

        self.show()
        self._save_status_text.set(
            "Format de page enregistré"
        )

    def _rename_page(self) -> None:
        """Ouvre la boîte de renommage de la page courante."""

        if getattr(self.page, "locked", False):
            self._save_status_text.set(
                "Cette page est verrouillée"
            )
            return

        RenamePageDialog(
            parent=self.parent,
            current_name=self.page.display_title,
            on_validate=self._apply_page_name,
        )

    def _apply_page_name(self, new_name: str) -> None:
        """Enregistre le nouveau nom dans la page et dans le livre."""

        clean_name = new_name.strip()

        if not clean_name:
            self._save_status_text.set(
                "Le nom ne peut pas être vide"
            )
            return

        try:
            self._save_page_objects()
            self.page.rename(clean_name)

            document = self._load_current_document()

            if document is None:
                raise RuntimeError(
                    "Livre introuvable"
                )

            document.update_page_summary(
                self.page
            )

        except (
            OSError,
            RuntimeError,
            ValueError,
        ):
            self._save_status_text.set(
                "La page n’a pas pu être renommée"
            )
            return

        self.show()

    def _change_page_type(self, page_type: str) -> None:
        """Change le type et applique sa couleur éditoriale officielle."""

        if getattr(self.page, "locked", False):
            self._save_status_text.set(
                "Cette page est verrouillée"
            )
            return

        appearance = self._appearance_for_type(page_type)

        try:
            self._save_page_objects()
            self.page.set_type(page_type)
            self.page.color = appearance["couleur"]
            self.page.icon = appearance["icone"]
            self.page.save(update_history=False)

            document = self._load_current_document()

            if document is not None:
                document.update_page_summary(self.page)

        except (
            OSError,
            RuntimeError,
            ValueError,
        ):
            self._save_status_text.set(
                "Le type de page n’a pas pu être modifié"
            )
            return

        self.show()

    def _duplicate_page(self) -> None:
        """Duplique la page courante et ouvre immédiatement sa copie."""

        self._save_page_objects()
        document = self._load_current_document()

        if document is None:
            self._save_status_text.set(
                "Duplication impossible : livre introuvable"
            )
            return

        try:
            duplicated_page = document.duplicate_page(
                self.page.number
            )
        except (
            OSError,
            RuntimeError,
            ValueError,
        ):
            duplicated_page = None

        if duplicated_page is None:
            self._save_status_text.set(
                "La page n’a pas pu être dupliquée"
            )
            return

        self.page = duplicated_page
        self.workspace = None
        self.status_bar = None
        self.root = None
        self.show()

    def _delete_page(self) -> None:
        """Supprime la page après confirmation, puis ouvre la page voisine."""

        if getattr(self.page, "locked", False):
            self._save_status_text.set(
                "Déverrouille la page avant de la supprimer"
            )
            return

        confirmed = messagebox.askyesno(
            title="Supprimer la page",
            message=(
                f"Supprimer définitivement « {self.page.display_title} » ?\n\n"
                "Cette action ne pourra pas être annulée."
            ),
            icon="warning",
            parent=self.parent.winfo_toplevel(),
        )

        if not confirmed:
            return

        document = self._load_current_document()

        if document is None:
            self._save_status_text.set(
                "Suppression impossible : livre introuvable"
            )
            return

        page_index = None

        for index, page_info in enumerate(document.pages):
            same_identifier = (
                page_info.get("identifiant")
                and page_info.get("identifiant") == self.page.identifier
            )
            same_number = page_info.get("numero") == self.page.number

            if same_identifier or same_number:
                page_index = index
                break

        if page_index is None:
            self._save_status_text.set(
                "La page n’a pas été retrouvée dans le livre"
            )
            return

        page_root = getattr(self.page, "root", None)

        try:
            if page_root is not None and Path(page_root).exists():
                shutil.rmtree(Path(page_root))

            document.pages.pop(page_index)
            document.save()

        except OSError:
            self._save_status_text.set(
                "La page n’a pas pu être supprimée"
            )
            return

        if document.pages:
            next_index = min(
                page_index,
                len(document.pages) - 1,
            )
            next_number = document.pages[next_index].get("numero")
            next_page = (
                document.get_page(next_number)
                if next_number is not None
                else None
            )

            if next_page is not None:
                self.page = next_page
                self.workspace = None
                self.status_bar = None
                self.root = None
                self.show()
                return

        self.workspace = None
        self.status_bar = None
        self.root = None

        if self.on_back is not None:
            self.on_back()

    def _new_page(self) -> None:
        """Crée une page vide dans le même livre et l’ouvre immédiatement."""

        self._save_page_objects()
        document = self._load_current_document()

        if document is None:
            self._save_status_text.set(
                "Création impossible : livre introuvable"
            )
            return

        try:
            new_page = document.add_page(
                page_type="Page vide",
            )

            appearance = self._appearance_for_type(
                "Page vide"
            )
            new_page.color = appearance["couleur"]
            new_page.icon = appearance["icone"]
            new_page.save(update_history=False)
            document.update_page_summary(new_page)

        except (
            OSError,
            RuntimeError,
            ValueError,
        ):
            self._save_status_text.set(
                "La nouvelle page n’a pas pu être créée"
            )
            return

        self.page = new_page
        self.workspace = None
        self.status_bar = None
        self.root = None
        self.show()

    def back(self) -> None:

        self._save_page_objects()

        self.workspace = None
        self.status_bar = None
        self.root = None

        if self.on_back is not None:
            self.on_back()

    def _clear_parent(self) -> None:

        self._unbind_page_context_menu()

        for widget in self.parent.winfo_children():
            widget.destroy()

    def __repr__(self) -> str:

        return (
            "PageEditorView("
            f"page={self.page.display_title!r})"
        )