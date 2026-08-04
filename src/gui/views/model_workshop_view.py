from __future__ import annotations

import json
import shutil
import tkinter as tk
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from tkinter import messagebox
from typing import Any, Callable
from uuid import uuid4

import customtkinter as ctk

from src.core.model import Model
from src.core.page import Page
from src.gui.views.page_editor_view import PageEditorView
from src.theme.colors import Colors
from src.theme.fonts import Fonts


CUSTOM_FORMAT_LABEL = "Dimensions libres…"
NO_CATEGORY_LABEL = "Sans catégorie"
NEW_CATEGORY_LABEL = "＋ Nouvelle catégorie…"


class ModelCategoryStore:
    """Bibliothèque locale des catégories de gabarits du projet."""

    VERSION = "1.0"

    DEFAULT_CATEGORY_NAMES = (
        "Couverture",
        "Quatrième de couverture",
        "Sommaire",
        "Avant-propos",
        "Ouverture de chapitre",
        "Page de texte",
        "Page fiche",
        "Page illustration",
        "Page de transition",
        "Conclusion",
        "Page blanche",
    )

    def __init__(self, project) -> None:
        self.project = project
        self.file_path = Path(project.models_folder) / "categories.json"
        self._categories: list[dict[str, Any]] = []

    def load(self) -> list[dict[str, Any]]:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

        if not self.file_path.exists():
            self._categories = self._default_categories()
            self.save()
            return self.categories

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            self._categories = self._default_categories()
            self.save()
            return self.categories

        raw_categories = data.get("categories", []) if isinstance(data, dict) else []
        normalized = [
            self._normalize_category(category)
            for category in raw_categories
            if isinstance(category, dict)
        ]
        self._categories = [category for category in normalized if category["nom"]]

        if not self._categories:
            self._categories = self._default_categories()
            self.save()

        return self.categories

    @property
    def categories(self) -> list[dict[str, Any]]:
        return [dict(category) for category in self._categories]

    def names(self) -> list[str]:
        return [category["nom"] for category in self._categories]

    def get(self, name: str) -> dict[str, Any] | None:
        normalized_name = name.strip().casefold()
        for category in self._categories:
            if category["nom"].strip().casefold() == normalized_name:
                return dict(category)
        return None

    def add(self, category: dict[str, Any]) -> dict[str, Any]:
        normalized = self._normalize_category(category)
        name = normalized["nom"]

        if not name:
            raise ValueError("La catégorie doit posséder un nom.")

        if self.get(name) is not None:
            raise ValueError("Une catégorie porte déjà ce nom.")

        normalized["identifiant"] = normalized.get("identifiant") or str(uuid4())
        normalized["personnalisee"] = True
        normalized["date_creation"] = datetime.now().isoformat()
        normalized["date_modification"] = normalized["date_creation"]

        self._categories.append(normalized)
        self._categories.sort(key=lambda item: item["nom"].casefold())
        self.save()
        return dict(normalized)

    def save(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "version": self.VERSION,
            "date_modification": datetime.now().isoformat(),
            "categories": self._categories,
        }

        with self.file_path.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=4, ensure_ascii=False)

    def _default_categories(self) -> list[dict[str, Any]]:
        project_format = str(getattr(self.project, "format", Page.DEFAULT_FORMAT))
        if project_format not in Page.FORMAT_PRESETS:
            project_format = Page.DEFAULT_FORMAT

        width, height = Page.FORMAT_PRESETS[project_format]
        now = datetime.now().isoformat()

        return [
            {
                "identifiant": str(uuid4()),
                "nom": name,
                "description": "",
                "format_mode": "preregle",
                "format": project_format,
                "largeur_mm": width,
                "hauteur_mm": height,
                "orientation": Page.DEFAULT_ORIENTATION,
                "marges": {
                    "haut": 15.0,
                    "bas": 15.0,
                    "interieure": 15.0,
                    "exterieure": 15.0,
                },
                "fonds_perdus": {
                    "haut": 0.0,
                    "droite": 0.0,
                    "bas": 0.0,
                    "gauche": 0.0,
                },
                "personnalisee": False,
                "date_creation": now,
                "date_modification": now,
            }
            for name in self.DEFAULT_CATEGORY_NAMES
        ]

    def _normalize_category(self, category: dict[str, Any]) -> dict[str, Any]:
        format_name = str(category.get("format", Page.DEFAULT_FORMAT)).strip()
        format_mode = str(category.get("format_mode", "preregle")).strip()
        orientation = str(
            category.get("orientation", Page.DEFAULT_ORIENTATION)
        ).strip()

        if format_name not in Page.FORMAT_PRESETS:
            format_name = Page.DEFAULT_FORMAT

        if format_mode not in {"preregle", "libre"}:
            format_mode = "preregle"

        if orientation not in Page.ORIENTATIONS:
            orientation = Page.DEFAULT_ORIENTATION

        preset_width, preset_height = Page.FORMAT_PRESETS[format_name]
        margins = category.get("marges", {})
        bleed = category.get("fonds_perdus", {})

        return {
            "identifiant": str(category.get("identifiant", "")).strip(),
            "nom": str(category.get("nom", "")).strip(),
            "description": str(category.get("description", "")).strip(),
            "format_mode": format_mode,
            "format": format_name,
            "largeur_mm": self._positive_float(
                category.get("largeur_mm", preset_width),
                preset_width,
            ),
            "hauteur_mm": self._positive_float(
                category.get("hauteur_mm", preset_height),
                preset_height,
            ),
            "orientation": orientation,
            "marges": {
                "haut": self._non_negative_float(margins.get("haut", 15.0), 15.0),
                "bas": self._non_negative_float(margins.get("bas", 15.0), 15.0),
                "interieure": self._non_negative_float(
                    margins.get("interieure", 15.0), 15.0
                ),
                "exterieure": self._non_negative_float(
                    margins.get("exterieure", 15.0), 15.0
                ),
            },
            "fonds_perdus": {
                "haut": self._non_negative_float(bleed.get("haut", 0.0), 0.0),
                "droite": self._non_negative_float(bleed.get("droite", 0.0), 0.0),
                "bas": self._non_negative_float(bleed.get("bas", 0.0), 0.0),
                "gauche": self._non_negative_float(bleed.get("gauche", 0.0), 0.0),
            },
            "personnalisee": bool(category.get("personnalisee", False)),
            "date_creation": str(category.get("date_creation", "")),
            "date_modification": str(category.get("date_modification", "")),
        }

    @staticmethod
    def _positive_float(value: Any, default: float) -> float:
        try:
            number = float(str(value).replace(",", "."))
        except (TypeError, ValueError):
            return default
        return number if number > 0 else default

    @staticmethod
    def _non_negative_float(value: Any, default: float) -> float:
        try:
            number = float(str(value).replace(",", "."))
        except (TypeError, ValueError):
            return default
        return number if number >= 0 else default


class FormatFieldsMixin:
    """Champs communs aux fenêtres de catégorie et de gabarit."""

    _format_var: tk.StringVar
    _orientation_var: tk.StringVar
    _width_var: tk.StringVar
    _height_var: tk.StringVar
    _dimension_entries: tuple[ctk.CTkEntry, ctk.CTkEntry]

    def _format_values(self) -> list[str]:
        return [*Page.FORMAT_PRESETS.keys(), CUSTOM_FORMAT_LABEL]

    def _on_format_change(self, selected: str) -> None:
        custom = selected == CUSTOM_FORMAT_LABEL
        state = "normal" if custom else "disabled"

        for entry in self._dimension_entries:
            entry.configure(state=state)

        if not custom:
            self._apply_preset_dimensions(selected)

    def _on_orientation_change(self, _selected: str) -> None:
        if self._format_var.get() != CUSTOM_FORMAT_LABEL:
            self._apply_preset_dimensions(self._format_var.get())

    def _apply_preset_dimensions(self, format_name: str) -> None:
        if format_name not in Page.FORMAT_PRESETS:
            return

        width, height = Page.FORMAT_PRESETS[format_name]
        orientation = self._orientation_var.get()

        if orientation == "Paysage" and height > width:
            width, height = height, width
        elif orientation == "Portrait" and width > height:
            width, height = height, width

        self._width_var.set(self._number_text(width))
        self._height_var.set(self._number_text(height))

    @staticmethod
    def _number_text(value: Any) -> str:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return str(value)

        if number.is_integer():
            return str(int(number))
        return f"{number:.2f}".rstrip("0").rstrip(".")

    @staticmethod
    def _oriented_dimensions(
        width: float,
        height: float,
        orientation: str,
    ) -> tuple[float, float]:
        if orientation == "Paysage" and height > width:
            return height, width
        if orientation == "Portrait" and width > height:
            return height, width
        return width, height

    @staticmethod
    def _parse_number(value: str, label: str, *, allow_zero: bool) -> float:
        normalized = value.strip().replace(",", ".")

        try:
            number = float(normalized)
        except ValueError as error:
            raise ValueError(f"{label.capitalize()} doit être un nombre.") from error

        if allow_zero:
            if number < 0:
                raise ValueError(f"{label.capitalize()} ne peut pas être négatif.")
        elif number <= 0:
            raise ValueError(f"{label.capitalize()} doit être supérieur à zéro.")

        return number


class NewCategoryDialog(FormatFieldsMixin, ctk.CTkToplevel):
    """Création d'une catégorie et de ses caractéristiques réutilisables."""

    def __init__(
        self,
        parent,
        *,
        default_format: str,
        on_validate: Callable[[dict[str, Any]], None],
        on_close: Callable[[], None] | None = None,
    ) -> None:
        super().__init__(parent)

        self._on_validate = on_validate
        self._after_close = on_close
        self._default_format = (
            default_format
            if default_format in Page.FORMAT_PRESETS
            else Page.DEFAULT_FORMAT
        )

        self.title("Nouvelle catégorie")
        self.geometry("620x650")
        self.minsize(620, 650)
        self.resizable(False, False)
        self.configure(fg_color=Colors.WINDOW)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._close)

        self._name_var = tk.StringVar(value="")
        self._description_var = tk.StringVar(value="")
        self._format_var = tk.StringVar(value=self._default_format)
        self._orientation_var = tk.StringVar(value=Page.DEFAULT_ORIENTATION)
        width, height = Page.FORMAT_PRESETS[self._default_format]
        self._width_var = tk.StringVar(value=self._number_text(width))
        self._height_var = tk.StringVar(value=self._number_text(height))
        self._margin_vars = {
            "haut": tk.StringVar(value="15"),
            "bas": tk.StringVar(value="15"),
            "interieure": tk.StringVar(value="15"),
            "exterieure": tk.StringVar(value="15"),
        }
        self._bleed_vars = {
            "haut": tk.StringVar(value="0"),
            "droite": tk.StringVar(value="0"),
            "bas": tk.StringVar(value="0"),
            "gauche": tk.StringVar(value="0"),
        }
        self._error_var = tk.StringVar(value="")

        self._build()
        self.after(60, self._prepare)
        self.after(80, self._center_window)

    def _build(self) -> None:
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=22, pady=18)
        content.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="category")

        ctk.CTkLabel(
            content,
            text="Nouvelle catégorie",
            font=Fonts.H2,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 12))

        self._label(content, "Nom", row=1, column=0, columnspan=4)
        self._name_entry = ctk.CTkEntry(
            content,
            textvariable=self._name_var,
            height=34,
            border_color=Colors.BORDER,
            font=Fonts.NORMAL,
        )
        self._name_entry.grid(
            row=2,
            column=0,
            columnspan=4,
            sticky="ew",
            pady=(3, 10),
        )
        self._name_entry.bind("<Return>", self._validate)
        self._name_entry.bind("<Escape>", self._close)

        self._label(content, "Description facultative", row=3, column=0, columnspan=4)
        ctk.CTkEntry(
            content,
            textvariable=self._description_var,
            height=34,
            border_color=Colors.BORDER,
            font=Fonts.NORMAL,
        ).grid(row=4, column=0, columnspan=4, sticky="ew", pady=(3, 12))

        self._label(content, "Format", row=5, column=0, columnspan=2)
        self._label(content, "Orientation", row=5, column=2, columnspan=2)

        ctk.CTkOptionMenu(
            content,
            values=self._format_values(),
            variable=self._format_var,
            height=34,
            fg_color=Colors.BUTTON,
            button_color=Colors.PRIMARY,
            button_hover_color=Colors.PRIMARY_HOVER,
            text_color=Colors.TEXT,
            font=Fonts.NORMAL,
            dropdown_font=Fonts.NORMAL,
            command=self._on_format_change,
        ).grid(row=6, column=0, columnspan=2, sticky="ew", padx=(0, 5), pady=(3, 10))

        ctk.CTkOptionMenu(
            content,
            values=sorted(Page.ORIENTATIONS),
            variable=self._orientation_var,
            height=34,
            fg_color=Colors.BUTTON,
            button_color=Colors.PRIMARY,
            button_hover_color=Colors.PRIMARY_HOVER,
            text_color=Colors.TEXT,
            font=Fonts.NORMAL,
            dropdown_font=Fonts.NORMAL,
            command=self._on_orientation_change,
        ).grid(row=6, column=2, columnspan=2, sticky="ew", padx=(5, 0), pady=(3, 10))

        self._label(content, "Largeur (mm)", row=7, column=0, columnspan=2)
        self._label(content, "Hauteur (mm)", row=7, column=2, columnspan=2)

        width_entry = ctk.CTkEntry(
            content,
            textvariable=self._width_var,
            height=34,
            border_color=Colors.BORDER,
            font=Fonts.NORMAL,
        )
        width_entry.grid(row=8, column=0, columnspan=2, sticky="ew", padx=(0, 5), pady=(3, 12))

        height_entry = ctk.CTkEntry(
            content,
            textvariable=self._height_var,
            height=34,
            border_color=Colors.BORDER,
            font=Fonts.NORMAL,
        )
        height_entry.grid(row=8, column=2, columnspan=2, sticky="ew", padx=(5, 0), pady=(3, 12))

        self._dimension_entries = (width_entry, height_entry)
        self._on_format_change(self._format_var.get())

        ctk.CTkLabel(
            content,
            text="Marges par défaut (mm)",
            font=(Fonts.FAMILY, 12, "bold"),
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(row=9, column=0, columnspan=4, sticky="ew", pady=(0, 4))

        margin_labels = (
            ("haut", "Haut"),
            ("bas", "Bas"),
            ("interieure", "Intérieure"),
            ("exterieure", "Extérieure"),
        )
        self._create_numeric_row(content, row=10, definitions=margin_labels, variables=self._margin_vars)

        ctk.CTkLabel(
            content,
            text="Fonds perdus par défaut (mm)",
            font=(Fonts.FAMILY, 12, "bold"),
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(row=12, column=0, columnspan=4, sticky="ew", pady=(10, 4))

        bleed_labels = (
            ("haut", "Haut"),
            ("droite", "Droite"),
            ("bas", "Bas"),
            ("gauche", "Gauche"),
        )
        self._create_numeric_row(content, row=13, definitions=bleed_labels, variables=self._bleed_vars)

        ctk.CTkLabel(
            content,
            textvariable=self._error_var,
            font=Fonts.SMALL,
            text_color=Colors.ERROR,
            anchor="w",
        ).grid(row=15, column=0, columnspan=4, sticky="ew", pady=(10, 0))

        actions = ctk.CTkFrame(content, fg_color="transparent")
        actions.grid(row=16, column=0, columnspan=4, sticky="sew", pady=(14, 0))
        content.grid_rowconfigure(16, weight=1)

        ctk.CTkButton(
            actions,
            text="Annuler",
            width=100,
            height=34,
            fg_color=Colors.BUTTON,
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            command=self._close,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            actions,
            text="Enregistrer",
            width=112,
            height=34,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            command=self._validate,
        ).pack(side="right")

    def _label(self, parent, text: str, *, row: int, column: int, columnspan: int = 1) -> None:
        ctk.CTkLabel(
            parent,
            text=text,
            font=Fonts.SMALL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
        ).grid(row=row, column=column, columnspan=columnspan, sticky="ew")

    def _create_numeric_row(
        self,
        parent,
        *,
        row: int,
        definitions: tuple[tuple[str, str], ...],
        variables: dict[str, tk.StringVar],
    ) -> None:
        for column, (key, label) in enumerate(definitions):
            ctk.CTkLabel(
                parent,
                text=label,
                font=(Fonts.FAMILY, 10),
                text_color=Colors.TEXT_LIGHT,
                anchor="w",
            ).grid(row=row, column=column, sticky="ew", padx=(0 if column == 0 else 4, 4))

            ctk.CTkEntry(
                parent,
                textvariable=variables[key],
                height=32,
                border_color=Colors.BORDER,
                font=Fonts.SMALL,
            ).grid(
                row=row + 1,
                column=column,
                sticky="ew",
                padx=(0 if column == 0 else 4, 0 if column == 3 else 4),
                pady=(2, 0),
            )

    def _prepare(self) -> None:
        self._name_entry.focus_set()

    def _center_window(self) -> None:
        self.update_idletasks()
        parent = self.master.winfo_toplevel()
        x = parent.winfo_x() + max(0, (parent.winfo_width() - self.winfo_width()) // 2)
        y = parent.winfo_y() + max(0, (parent.winfo_height() - self.winfo_height()) // 2)
        self.geometry(f"+{x}+{y}")

    def _validate(self, _event=None) -> None:
        name = self._name_var.get().strip()
        if not name:
            self._error_var.set("La catégorie doit posséder un nom.")
            self._name_entry.focus_set()
            return

        try:
            payload = self._build_payload(name)
            self._on_validate(payload)
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            self._error_var.set(str(error))
            return

        self._close()

    def _build_payload(self, name: str) -> dict[str, Any]:
        width = self._parse_number(self._width_var.get(), "largeur", allow_zero=False)
        height = self._parse_number(self._height_var.get(), "hauteur", allow_zero=False)
        margins = {
            key: self._parse_number(variable.get(), f"marge {key}", allow_zero=True)
            for key, variable in self._margin_vars.items()
        }
        bleed = {
            key: self._parse_number(variable.get(), f"fond perdu {key}", allow_zero=True)
            for key, variable in self._bleed_vars.items()
        }

        page_width, page_height = self._oriented_dimensions(
            width,
            height,
            self._orientation_var.get(),
        )
        if margins["haut"] + margins["bas"] >= page_height:
            raise ValueError("Les marges haute et basse occupent toute la hauteur.")
        if margins["interieure"] + margins["exterieure"] >= page_width:
            raise ValueError("Les marges intérieure et extérieure occupent toute la largeur.")

        custom = self._format_var.get() == CUSTOM_FORMAT_LABEL
        return {
            "nom": name,
            "description": self._description_var.get().strip(),
            "format_mode": "libre" if custom else "preregle",
            "format": self._default_format if custom else self._format_var.get(),
            "largeur_mm": width,
            "hauteur_mm": height,
            "orientation": self._orientation_var.get(),
            "marges": margins,
            "fonds_perdus": bleed,
        }

    def _close(self, _event=None) -> None:
        try:
            self.grab_release()
        except tk.TclError:
            pass
        callback = self._after_close
        parent = self.master
        self.destroy()
        if callback is not None and parent is not None:
            parent.after_idle(callback)


class NewModelDialog(FormatFieldsMixin, ctk.CTkToplevel):
    """Prépare une nouvelle création dans l’Atelier."""

    def __init__(
        self,
        parent,
        *,
        default_format: str,
        categories: list[dict[str, Any]],
        on_create_category: Callable[
            [Callable[[dict[str, Any]], None], Callable[[], None]],
            None,
        ],
        on_validate: Callable[[dict[str, Any]], None],
    ) -> None:
        super().__init__(parent)

        self._on_validate = on_validate
        self._on_create_category = on_create_category
        self._default_format = (
            default_format
            if default_format in Page.FORMAT_PRESETS
            else Page.DEFAULT_FORMAT
        )
        self._categories: dict[str, dict[str, Any]] = {}

        self.title("Nouvelle création")
        self.geometry("620x650")
        self.minsize(620, 650)
        self.resizable(False, False)
        self.configure(fg_color=Colors.WINDOW)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._close)

        self._name_var = tk.StringVar(value="")
        self._category_var = tk.StringVar(value=NO_CATEGORY_LABEL)
        self._format_var = tk.StringVar(value=self._default_format)
        self._orientation_var = tk.StringVar(value=Page.DEFAULT_ORIENTATION)
        width, height = Page.FORMAT_PRESETS[self._default_format]
        self._width_var = tk.StringVar(value=self._number_text(width))
        self._height_var = tk.StringVar(value=self._number_text(height))
        self._margin_vars = {
            "haut": tk.StringVar(value="15"),
            "bas": tk.StringVar(value="15"),
            "interieure": tk.StringVar(value="15"),
            "exterieure": tk.StringVar(value="15"),
        }
        self._bleed_vars = {
            "haut": tk.StringVar(value="0"),
            "droite": tk.StringVar(value="0"),
            "bas": tk.StringVar(value="0"),
            "gauche": tk.StringVar(value="0"),
        }
        self._error_var = tk.StringVar(value="")

        self._build()
        self._replace_categories(categories)
        self.after(60, self._prepare)
        self.after(80, self._center_window)

    def _build(self) -> None:
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=22, pady=18)
        content.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="model")

        ctk.CTkLabel(
            content,
            text="Nouvelle création",
            font=Fonts.H2,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 12))

        self._label(content, "Nom de la création", row=1, column=0, columnspan=4)
        self._name_entry = ctk.CTkEntry(
            content,
            textvariable=self._name_var,
            height=34,
            border_color=Colors.BORDER,
            font=Fonts.NORMAL,
        )
        self._name_entry.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(3, 10))
        self._name_entry.bind("<Return>", self._validate)
        self._name_entry.bind("<Escape>", self._close)

        self._label(content, "Catégorie facultative", row=3, column=0, columnspan=4)

        self._category_menu = ctk.CTkOptionMenu(
            content,
            values=[NO_CATEGORY_LABEL],
            variable=self._category_var,
            height=34,
            fg_color=Colors.BUTTON,
            button_color=Colors.PRIMARY,
            button_hover_color=Colors.PRIMARY_HOVER,
            text_color=Colors.TEXT,
            font=Fonts.NORMAL,
            dropdown_font=Fonts.NORMAL,
            command=self._on_category_change,
        )
        self._category_menu.grid(row=4, column=0, columnspan=3, sticky="ew", padx=(0, 5), pady=(3, 12))

        ctk.CTkButton(
            content,
            text="＋ Catégorie",
            height=34,
            corner_radius=7,
            fg_color="#DFECE5",
            hover_color="#D0E3D8",
            text_color="#263E63",
            border_width=1,
            border_color="#82B7A1",
            font=Fonts.SMALL,
            command=self._create_category,
        ).grid(row=4, column=3, sticky="ew", padx=(5, 0), pady=(3, 12))

        self._label(content, "Format", row=5, column=0, columnspan=2)
        self._label(content, "Orientation", row=5, column=2, columnspan=2)

        ctk.CTkOptionMenu(
            content,
            values=self._format_values(),
            variable=self._format_var,
            height=34,
            fg_color=Colors.BUTTON,
            button_color=Colors.PRIMARY,
            button_hover_color=Colors.PRIMARY_HOVER,
            text_color=Colors.TEXT,
            font=Fonts.NORMAL,
            dropdown_font=Fonts.NORMAL,
            command=self._on_format_change,
        ).grid(row=6, column=0, columnspan=2, sticky="ew", padx=(0, 5), pady=(3, 10))

        ctk.CTkOptionMenu(
            content,
            values=sorted(Page.ORIENTATIONS),
            variable=self._orientation_var,
            height=34,
            fg_color=Colors.BUTTON,
            button_color=Colors.PRIMARY,
            button_hover_color=Colors.PRIMARY_HOVER,
            text_color=Colors.TEXT,
            font=Fonts.NORMAL,
            dropdown_font=Fonts.NORMAL,
            command=self._on_orientation_change,
        ).grid(row=6, column=2, columnspan=2, sticky="ew", padx=(5, 0), pady=(3, 10))

        self._label(content, "Largeur (mm)", row=7, column=0, columnspan=2)
        self._label(content, "Hauteur (mm)", row=7, column=2, columnspan=2)

        width_entry = ctk.CTkEntry(
            content,
            textvariable=self._width_var,
            height=34,
            border_color=Colors.BORDER,
            font=Fonts.NORMAL,
        )
        width_entry.grid(row=8, column=0, columnspan=2, sticky="ew", padx=(0, 5), pady=(3, 12))

        height_entry = ctk.CTkEntry(
            content,
            textvariable=self._height_var,
            height=34,
            border_color=Colors.BORDER,
            font=Fonts.NORMAL,
        )
        height_entry.grid(row=8, column=2, columnspan=2, sticky="ew", padx=(5, 0), pady=(3, 12))

        self._dimension_entries = (width_entry, height_entry)
        self._on_format_change(self._format_var.get())

        ctk.CTkLabel(
            content,
            text="Marges de la page (mm)",
            font=(Fonts.FAMILY, 12, "bold"),
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(row=9, column=0, columnspan=4, sticky="ew", pady=(0, 4))

        margin_labels = (
            ("haut", "Haut"),
            ("bas", "Bas"),
            ("interieure", "Intérieure"),
            ("exterieure", "Extérieure"),
        )
        self._create_numeric_row(content, row=10, definitions=margin_labels, variables=self._margin_vars)

        ctk.CTkLabel(
            content,
            text="Fonds perdus de la page (mm)",
            font=(Fonts.FAMILY, 12, "bold"),
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(row=12, column=0, columnspan=4, sticky="ew", pady=(10, 4))

        bleed_labels = (
            ("haut", "Haut"),
            ("droite", "Droite"),
            ("bas", "Bas"),
            ("gauche", "Gauche"),
        )
        self._create_numeric_row(content, row=13, definitions=bleed_labels, variables=self._bleed_vars)

        ctk.CTkLabel(
            content,
            textvariable=self._error_var,
            font=Fonts.SMALL,
            text_color=Colors.ERROR,
            anchor="w",
        ).grid(row=15, column=0, columnspan=4, sticky="ew", pady=(10, 0))

        actions = ctk.CTkFrame(content, fg_color="transparent")
        actions.grid(row=16, column=0, columnspan=4, sticky="sew", pady=(14, 0))
        content.grid_rowconfigure(16, weight=1)

        ctk.CTkButton(
            actions,
            text="Annuler",
            width=100,
            height=34,
            fg_color=Colors.BUTTON,
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            command=self._close,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            actions,
            text="Créer",
            width=100,
            height=34,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            command=self._validate,
        ).pack(side="right")

    def _label(self, parent, text: str, *, row: int, column: int, columnspan: int = 1) -> None:
        ctk.CTkLabel(
            parent,
            text=text,
            font=Fonts.SMALL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
        ).grid(row=row, column=column, columnspan=columnspan, sticky="ew")

    def _create_numeric_row(
        self,
        parent,
        *,
        row: int,
        definitions: tuple[tuple[str, str], ...],
        variables: dict[str, tk.StringVar],
    ) -> None:
        for column, (key, label) in enumerate(definitions):
            ctk.CTkLabel(
                parent,
                text=label,
                font=(Fonts.FAMILY, 10),
                text_color=Colors.TEXT_LIGHT,
                anchor="w",
            ).grid(row=row, column=column, sticky="ew", padx=(0 if column == 0 else 4, 4))

            ctk.CTkEntry(
                parent,
                textvariable=variables[key],
                height=32,
                border_color=Colors.BORDER,
                font=Fonts.SMALL,
            ).grid(
                row=row + 1,
                column=column,
                sticky="ew",
                padx=(0 if column == 0 else 4, 0 if column == 3 else 4),
                pady=(2, 0),
            )

    def _replace_categories(self, categories: list[dict[str, Any]]) -> None:
        self._categories = {
            str(category.get("nom", "")).strip(): dict(category)
            for category in categories
            if str(category.get("nom", "")).strip()
        }
        values = [NO_CATEGORY_LABEL, *sorted(self._categories, key=str.casefold)]
        self._category_menu.configure(values=values)

        if self._category_var.get() not in values:
            self._category_var.set(NO_CATEGORY_LABEL)

    def _on_category_change(self, selected: str) -> None:
        if selected == NO_CATEGORY_LABEL:
            return

        category = self._categories.get(selected)
        if category is None:
            return

        self._apply_category(category)

    def _apply_category(self, category: dict[str, Any]) -> None:
        orientation = str(category.get("orientation", Page.DEFAULT_ORIENTATION))
        self._orientation_var.set(orientation)

        if category.get("format_mode") == "libre":
            self._format_var.set(CUSTOM_FORMAT_LABEL)
        else:
            format_name = str(category.get("format", self._default_format))
            if format_name not in Page.FORMAT_PRESETS:
                format_name = self._default_format
            self._format_var.set(format_name)

        self._width_var.set(self._number_text(category.get("largeur_mm", 148)))
        self._height_var.set(self._number_text(category.get("hauteur_mm", 210)))

        margins = category.get("marges", {})
        for key, variable in self._margin_vars.items():
            variable.set(self._number_text(margins.get(key, 15)))

        bleed = category.get("fonds_perdus", {})
        for key, variable in self._bleed_vars.items():
            variable.set(self._number_text(bleed.get(key, 0)))

        self._on_format_change(self._format_var.get())

        if category.get("format_mode") == "libre":
            self._width_var.set(self._number_text(category.get("largeur_mm", 148)))
            self._height_var.set(self._number_text(category.get("hauteur_mm", 210)))

    def _create_category(self) -> None:
        try:
            self.grab_release()
        except tk.TclError:
            pass

        self._on_create_category(
            self._category_created,
            self._restore_grab,
        )

    def _category_created(self, category: dict[str, Any]) -> None:
        name = str(category.get("nom", "")).strip()
        if not name:
            self._restore_grab()
            return

        self._categories[name] = dict(category)
        self._replace_categories(list(self._categories.values()))
        self._category_var.set(name)
        self._apply_category(category)

    def _restore_grab(self) -> None:
        if not self.winfo_exists():
            return
        try:
            self.grab_set()
        except tk.TclError:
            pass
        self.focus_force()

    def _prepare(self) -> None:
        self._name_entry.focus_set()

    def _center_window(self) -> None:
        self.update_idletasks()
        parent = self.master.winfo_toplevel()
        x = parent.winfo_x() + max(0, (parent.winfo_width() - self.winfo_width()) // 2)
        y = parent.winfo_y() + max(0, (parent.winfo_height() - self.winfo_height()) // 2)
        self.geometry(f"+{x}+{y}")

    def _validate(self, _event=None) -> None:
        name = self._name_var.get().strip()
        if not name:
            self._error_var.set("La création doit posséder un nom.")
            self._name_entry.focus_set()
            return

        try:
            payload = self._build_payload(name)
            self._on_validate(payload)
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            self._error_var.set(str(error))
            return

        self._close()

    def _build_payload(self, name: str) -> dict[str, Any]:
        width = self._parse_number(self._width_var.get(), "largeur", allow_zero=False)
        height = self._parse_number(self._height_var.get(), "hauteur", allow_zero=False)
        margins = {
            key: self._parse_number(variable.get(), f"marge {key}", allow_zero=True)
            for key, variable in self._margin_vars.items()
        }
        bleed = {
            key: self._parse_number(variable.get(), f"fond perdu {key}", allow_zero=True)
            for key, variable in self._bleed_vars.items()
        }

        page_width, page_height = self._oriented_dimensions(
            width,
            height,
            self._orientation_var.get(),
        )
        if margins["haut"] + margins["bas"] >= page_height:
            raise ValueError("Les marges haute et basse occupent toute la hauteur.")
        if margins["interieure"] + margins["exterieure"] >= page_width:
            raise ValueError("Les marges intérieure et extérieure occupent toute la largeur.")

        custom = self._format_var.get() == CUSTOM_FORMAT_LABEL
        category = self._category_var.get()

        return {
            "name": name,
            "category": "" if category == NO_CATEGORY_LABEL else category,
            "format_mode": "libre" if custom else "preregle",
            "format_name": self._default_format if custom else self._format_var.get(),
            "width_mm": width,
            "height_mm": height,
            "orientation": self._orientation_var.get(),
            "margins": margins,
            "bleed": bleed,
        }

    def _close(self, _event=None) -> None:
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()



class SaveProjectModelDialog(ctk.CTkToplevel):
    """Enregistre explicitement la création courante comme gabarit du projet."""

    def __init__(
        self,
        parent,
        *,
        default_name: str,
        default_category: str,
        categories: list[dict[str, Any]],
        on_create_category: Callable[
            [Callable[[dict[str, Any]], None], Callable[[], None]],
            None,
        ],
        on_validate: Callable[[dict[str, Any]], None],
    ) -> None:
        super().__init__(parent)
        self._on_validate = on_validate
        self._on_create_category = on_create_category
        self._categories: dict[str, dict[str, Any]] = {}

        self.title("Enregistrer comme gabarit du projet")
        self.geometry("560x430")
        self.resizable(False, False)
        self.configure(fg_color=Colors.WINDOW)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.bind("<Return>", self._validate)
        self.bind("<Escape>", self._close)

        self._name_var = tk.StringVar(value=default_name.strip())
        self._category_var = tk.StringVar(
            value=default_category.strip() or NO_CATEGORY_LABEL
        )
        self._description_var = tk.StringVar(value="")
        self._version_note_var = tk.StringVar(value="")
        self._error_var = tk.StringVar(value="")

        self._build()
        self._replace_categories(categories)
        self.after(60, self._prepare)
        self.after(80, self._center_window)

    def _build(self) -> None:
        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=20, pady=16)
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            root,
            text="Enregistrer comme gabarit du projet",
            font=Fonts.H2,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", pady=(0, 10))

        form = ctk.CTkFrame(
            root,
            fg_color="#FFFFFF",
            corner_radius=9,
            border_width=1,
            border_color=Colors.BORDER,
        )
        form.grid(row=1, column=0, sticky="nsew")
        form.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._label(form, "Nom du gabarit", row=0)
        self._name_entry = ctk.CTkEntry(
            form,
            textvariable=self._name_var,
            height=31,
            border_color=Colors.BORDER,
            font=Fonts.NORMAL,
        )
        self._name_entry.grid(
            row=1,
            column=0,
            columnspan=4,
            sticky="ew",
            padx=12,
            pady=(2, 7),
        )

        self._label(form, "Catégorie facultative", row=2)
        self._category_menu = ctk.CTkOptionMenu(
            form,
            values=[NO_CATEGORY_LABEL],
            variable=self._category_var,
            height=31,
            fg_color=Colors.BUTTON,
            button_color="#6E927D",
            button_hover_color="#5F806D",
            text_color=Colors.TEXT,
            font=Fonts.SMALL,
            dropdown_font=Fonts.SMALL,
        )
        self._category_menu.grid(
            row=3,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=(12, 4),
            pady=(2, 7),
        )

        ctk.CTkButton(
            form,
            text="＋ Catégorie",
            height=31,
            corner_radius=6,
            fg_color="#FFFFFF",
            hover_color="#DFECE5",
            text_color="#263E63",
            border_width=1,
            border_color="#82B7A1",
            font=Fonts.SMALL,
            command=self._create_category,
        ).grid(
            row=3,
            column=3,
            sticky="ew",
            padx=(4, 12),
            pady=(2, 7),
        )

        self._label(form, "Description facultative", row=4)
        ctk.CTkEntry(
            form,
            textvariable=self._description_var,
            height=31,
            border_color=Colors.BORDER,
            font=Fonts.NORMAL,
        ).grid(
            row=5,
            column=0,
            columnspan=4,
            sticky="ew",
            padx=12,
            pady=(2, 7),
        )

        self._label(form, "Note de version en cas de mise à jour", row=6)
        ctk.CTkEntry(
            form,
            textvariable=self._version_note_var,
            height=31,
            border_color=Colors.BORDER,
            font=Fonts.NORMAL,
        ).grid(
            row=7,
            column=0,
            columnspan=4,
            sticky="ew",
            padx=12,
            pady=(2, 10),
        )

        ctk.CTkLabel(
            root,
            textvariable=self._error_var,
            font=Fonts.SMALL,
            text_color=Colors.ERROR,
            anchor="w",
            height=20,
        ).grid(row=2, column=0, sticky="ew", pady=(5, 2))

        actions = ctk.CTkFrame(root, fg_color="transparent", height=34)
        actions.grid(row=3, column=0, sticky="ew", pady=(4, 0))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_propagate(False)

        ctk.CTkButton(
            actions,
            text="Annuler",
            width=92,
            height=31,
            corner_radius=6,
            fg_color="#FFFFFF",
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            border_width=1,
            border_color=Colors.BORDER,
            font=Fonts.SMALL,
            command=self._close,
        ).grid(row=0, column=1, padx=(0, 6))

        ctk.CTkButton(
            actions,
            text="Enregistrer",
            width=108,
            height=31,
            corner_radius=6,
            fg_color="#82B7A1",
            hover_color="#6FA58F",
            text_color="#FFFFFF",
            font=Fonts.SMALL,
            command=self._validate,
        ).grid(row=0, column=2)

    def _label(self, parent, text: str, *, row: int) -> None:
        ctk.CTkLabel(
            parent,
            text=text,
            font=Fonts.SMALL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
            height=18,
        ).grid(
            row=row,
            column=0,
            columnspan=4,
            sticky="ew",
            padx=12,
            pady=(5 if row else 8, 0),
        )

    def _replace_categories(self, categories: list[dict[str, Any]]) -> None:
        self._categories = {
            str(category.get("nom", "")).strip(): dict(category)
            for category in categories
            if str(category.get("nom", "")).strip()
        }
        values = [NO_CATEGORY_LABEL, *sorted(self._categories, key=str.casefold)]
        self._category_menu.configure(values=values)
        if self._category_var.get() not in values:
            self._category_var.set(NO_CATEGORY_LABEL)

    def _create_category(self) -> None:
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self._on_create_category(self._category_created, self._restore_grab)

    def _category_created(self, category: dict[str, Any]) -> None:
        name = str(category.get("nom", "")).strip()
        if name:
            self._categories[name] = dict(category)
            self._replace_categories(list(self._categories.values()))
            self._category_var.set(name)
        self._restore_grab()

    def _restore_grab(self) -> None:
        if not self.winfo_exists():
            return
        try:
            self.grab_set()
        except tk.TclError:
            pass
        self.focus_force()

    def _prepare(self) -> None:
        self._name_entry.focus_set()
        self._name_entry.select_range(0, "end")

    def _center_window(self) -> None:
        self.update_idletasks()
        parent = self.master.winfo_toplevel()
        x = parent.winfo_x() + max(0, (parent.winfo_width() - self.winfo_width()) // 2)
        y = parent.winfo_y() + max(0, (parent.winfo_height() - self.winfo_height()) // 2)
        self.geometry(f"+{x}+{y}")

    def _validate(self, _event=None) -> None:
        name = self._name_var.get().strip()
        if not name:
            self._error_var.set("Le gabarit doit posséder un nom.")
            self._name_entry.focus_set()
            return

        category = self._category_var.get().strip()
        payload = {
            "name": name,
            "category": "" if category == NO_CATEGORY_LABEL else category,
            "description": self._description_var.get().strip(),
            "version_note": self._version_note_var.get().strip(),
        }
        try:
            self._on_validate(payload)
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            self._error_var.set(str(error))
            return
        self._close()

    def _close(self, _event=None) -> None:
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()


class ModelLibraryDialog(ctk.CTkToplevel):
    """Vue facultative des modèles réutilisables et des gabarits du projet."""

    def __init__(
        self,
        parent,
        *,
        reusable_models: list[Model],
        project_models: list[Model],
        transferred_versions: dict[str, int],
        on_use: Callable[[Model, str], None],
    ) -> None:
        super().__init__(parent)
        self._reusable_models = reusable_models
        self._project_models = project_models
        self._transferred_versions = transferred_versions
        self._on_use = on_use
        self._active_tab = "modeles"
        self._tab_buttons: dict[str, ctk.CTkButton] = {}
        self._content: ctk.CTkFrame | None = None

        self.title("Bibliothèque de l’Atelier")
        self.geometry("860x620")
        self.minsize(760, 520)
        self.configure(fg_color=Colors.WINDOW)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._close)
        self._build()
        self.after(80, self._center_window)

    def _build(self) -> None:
        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=16, pady=14)
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            root,
            text="Bibliothèque de l’Atelier",
            font=Fonts.H2,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew", pady=(0, 8))

        tabs = ctk.CTkFrame(root, fg_color="#F3F5F7", corner_radius=8, height=42)
        tabs.grid(row=1, column=0, sticky="ew", pady=(0, 6))
        tabs.grid_columnconfigure((0, 1), weight=1, uniform="library_tabs")
        tabs.grid_propagate(False)

        definitions = (
            ("modeles", f"Modèles disponibles  {len(self._reusable_models)}"),
            ("gabarits", f"Gabarits du projet  {len(self._project_models)}"),
        )
        for column, (key, label) in enumerate(definitions):
            button = ctk.CTkButton(
                tabs,
                text=label,
                height=30,
                corner_radius=6,
                fg_color="#DFECE5",
                hover_color="#D0E3D8",
                text_color="#263E63",
                border_width=1,
                border_color="#82B7A1",
                font=Fonts.SMALL,
                command=lambda selected=key: self._show_tab(selected),
            )
            button.grid(row=0, column=column, sticky="ew", padx=4, pady=6)
            self._tab_buttons[key] = button

        self._content = ctk.CTkFrame(root, fg_color="#F7F8F9", corner_radius=8)
        self._content.grid(row=2, column=0, sticky="nsew")
        self._content.grid_columnconfigure(0, weight=1)
        self._content.grid_rowconfigure(0, weight=1)

        ctk.CTkButton(
            root,
            text="Fermer",
            width=100,
            height=32,
            fg_color=Colors.BUTTON,
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            command=self._close,
        ).grid(row=3, column=0, sticky="e", pady=(8, 0))

        self._show_tab("modeles")

    def _show_tab(self, key: str) -> None:
        self._active_tab = key
        for tab_key, button in self._tab_buttons.items():
            active = tab_key == key
            button.configure(
                fg_color="#82B7A1" if active else "#DFECE5",
                text_color="#FFFFFF" if active else "#263E63",
            )
        if self._content is None:
            return
        for child in self._content.winfo_children():
            child.destroy()

        models = self._reusable_models if key == "modeles" else self._project_models
        scroll = ctk.CTkScrollableFrame(
            self._content,
            fg_color="#F7F8F9",
            corner_radius=0,
        )
        scroll.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        scroll.grid_columnconfigure(0, weight=1)

        if not models:
            text = (
                "Aucun modèle réutilisable n’est encore installé."
                if key == "modeles"
                else "Aucun gabarit n’est encore enregistré pour ce projet."
            )
            ctk.CTkLabel(
                scroll,
                text=text,
                font=Fonts.NORMAL,
                text_color=Colors.TEXT_LIGHT,
                anchor="w",
            ).grid(row=0, column=0, sticky="ew", padx=12, pady=16)
            return

        for row_index, model in enumerate(models):
            self._create_model_row(scroll, model, key).grid(
                row=row_index,
                column=0,
                sticky="ew",
                padx=3,
                pady=(3 if row_index == 0 else 0, 3),
            )

    def _create_model_row(self, parent, model: Model, source: str) -> ctk.CTkFrame:
        row = ctk.CTkFrame(
            parent,
            height=58,
            fg_color="#FFFFFF",
            corner_radius=8,
            border_width=1,
            border_color="#D5D9DE",
        )
        row.grid_columnconfigure(1, weight=1)
        row.grid_propagate(False)

        ctk.CTkLabel(
            row,
            text="▦",
            width=38,
            font=(Fonts.FAMILY, 19, "bold"),
            text_color="#82B7A1",
        ).grid(row=0, column=0, rowspan=2, padx=(8, 2), pady=5)

        ctk.CTkLabel(
            row,
            text=model.name,
            font=Fonts.NORMAL,
            text_color="#263E63",
            anchor="w",
        ).grid(row=0, column=1, sticky="sew", padx=4, pady=(5, 0))

        category = model.category or NO_CATEGORY_LABEL
        status = ""
        if source == "gabarits":
            transferred = self._transferred_versions.get(model.identifier)
            status = (
                " · Prêt dans la Conception"
                if transferred == model.version_number
                else " · Non transféré"
            )
        details = (
            f"{category} · {model.version_label} · "
            f"{model.zone_count} zone(s){status}"
        )
        ctk.CTkLabel(
            row,
            text=details,
            font=Fonts.SMALL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
        ).grid(row=1, column=1, sticky="new", padx=4, pady=(0, 5))

        ctk.CTkButton(
            row,
            text="Utiliser",
            width=82,
            height=30,
            corner_radius=7,
            fg_color="#DFECE5",
            hover_color="#D0E3D8",
            text_color="#263E63",
            border_width=1,
            border_color="#82B7A1",
            font=Fonts.SMALL,
            command=lambda: self._use(model, source),
        ).grid(row=0, column=2, rowspan=2, padx=8, pady=13)
        return row

    def _use(self, model: Model, source: str) -> None:
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()
        self.master.after_idle(lambda: self._on_use(model, source))

    def _center_window(self) -> None:
        self.update_idletasks()
        parent = self.master.winfo_toplevel()
        x = parent.winfo_x() + max(0, (parent.winfo_width() - self.winfo_width()) // 2)
        y = parent.winfo_y() + max(0, (parent.winfo_height() - self.winfo_height()) // 2)
        self.geometry(f"+{x}+{y}")

    def _close(self) -> None:
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()


class TransferModelsDialog(ctk.CTkToplevel):
    """Sélectionne le lot de gabarits à rendre disponible dans la Conception."""

    def __init__(
        self,
        parent,
        *,
        models: list[Model],
        on_validate: Callable[[list[Model]], None],
    ) -> None:
        super().__init__(parent)
        self._models = models
        self._on_validate = on_validate
        self._variables = {
            model.identifier: tk.BooleanVar(value=True)
            for model in models
        }

        self.title("Transférer vers la Conception")
        self.geometry("680x560")
        self.minsize(620, 480)
        self.configure(fg_color=Colors.WINDOW)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.protocol("WM_DELETE_WINDOW", self._close)
        self._build()
        self.after(80, self._center_window)

    def _build(self) -> None:
        root = ctk.CTkFrame(self, fg_color="transparent")
        root.pack(fill="both", expand=True, padx=18, pady=16)
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            root,
            text="Transférer les gabarits prêts",
            font=Fonts.H2,
            text_color=Colors.TEXT,
            anchor="w",
        ).grid(row=0, column=0, sticky="ew")

        ctk.CTkLabel(
            root,
            text=(
                "Coche les gabarits à rendre disponibles dans le Bureau de conception. "
                "Les originaux restent conservés dans l’Atelier."
            ),
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
            justify="left",
            wraplength=620,
        ).grid(row=1, column=0, sticky="ew", pady=(4, 10))

        scroll = ctk.CTkScrollableFrame(root, fg_color="#F7F8F9", corner_radius=8)
        scroll.grid(row=2, column=0, sticky="nsew")
        scroll.grid_columnconfigure(0, weight=1)

        for row_index, model in enumerate(self._models):
            line = ctk.CTkFrame(
                scroll,
                height=48,
                fg_color="#FFFFFF",
                corner_radius=7,
                border_width=1,
                border_color="#D5D9DE",
            )
            line.grid(
                row=row_index,
                column=0,
                sticky="ew",
                padx=4,
                pady=(4 if row_index == 0 else 0, 4),
            )
            line.grid_columnconfigure(1, weight=1)
            line.grid_propagate(False)

            ctk.CTkCheckBox(
                line,
                text="",
                width=28,
                variable=self._variables[model.identifier],
                fg_color="#82B7A1",
                hover_color="#6FA38E",
            ).grid(row=0, column=0, padx=(10, 4), pady=10)

            ctk.CTkLabel(
                line,
                text=model.name,
                font=Fonts.NORMAL,
                text_color="#263E63",
                anchor="w",
            ).grid(row=0, column=1, sticky="w")

            ctk.CTkLabel(
                line,
                text=f"{model.category or NO_CATEGORY_LABEL} · {model.version_label}",
                font=Fonts.SMALL,
                text_color=Colors.TEXT_LIGHT,
            ).grid(row=0, column=2, sticky="e", padx=10)

        actions = ctk.CTkFrame(root, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="ew", pady=(10, 0))

        ctk.CTkButton(
            actions,
            text="Annuler",
            width=100,
            height=34,
            fg_color=Colors.BUTTON,
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            command=self._close,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            actions,
            text="Transférer",
            width=112,
            height=34,
            fg_color="#82B7A1",
            hover_color="#6FA38E",
            text_color="#FFFFFF",
            command=self._validate,
        ).pack(side="right")

    def _validate(self) -> None:
        selected = [
            model
            for model in self._models
            if self._variables[model.identifier].get()
        ]
        if not selected:
            messagebox.showinfo(
                "Aucun gabarit sélectionné",
                "Coche au moins un gabarit.",
                parent=self,
            )
            return
        try:
            self._on_validate(selected)
        except (OSError, RuntimeError, TypeError, ValueError) as error:
            messagebox.showerror("Transfert impossible", str(error), parent=self)
            return
        self._close()

    def _center_window(self) -> None:
        self.update_idletasks()
        parent = self.master.winfo_toplevel()
        x = parent.winfo_x() + max(0, (parent.winfo_width() - self.winfo_width()) // 2)
        y = parent.winfo_y() + max(0, (parent.winfo_height() - self.winfo_height()) // 2)
        self.geometry(f"+{x}+{y}")

    def _close(self) -> None:
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()


class AtelierPageEditorView(PageEditorView):
    """Adapte l’éditeur existant au travail de l’Atelier."""

    def __init__(self, parent, page, *, on_back=None, on_new=None) -> None:
        super().__init__(parent, page, on_back=on_back)
        self._on_new_creation = on_new

    def _new_page(self) -> None:
        self._save_page_objects(show_status=False)
        if self._on_new_creation is not None:
            self._on_new_creation()

    def _build_page_menu(self) -> tk.Menu:
        parent = self.root if self.root is not None else self.parent
        menu = tk.Menu(parent, tearoff=False)
        menu.add_command(
            label="Renommer la création…",
            command=lambda: self._schedule_page_action(self._rename_page),
        )
        menu.add_separator()
        menu.add_command(
            label="Enregistrer comme gabarit du projet…",
            command=lambda: self._schedule_page_action(
                lambda: self.parent.event_generate("<<AtelierSaveModel>>")
            ),
        )
        self._page_menu = menu
        return menu


class ModelWorkshopView:
    """Atelier direct : récupérer ou créer, enregistrer, puis transférer."""

    WINDOW_BG = Colors.WINDOW
    RIBBON_BG = "#F3F5F7"
    GROUP_BG = "#FFFFFF"
    BORDER = "#D5D9DE"
    INK = "#263E63"
    CELADON = "#82B7A1"
    CELADON_SOFT = "#DFECE5"
    LILAC = "#A997C9"
    LILAC_SOFT = "#E8E1F1"
    CORAL = "#DF806B"
    CORAL_SOFT = "#F2DDD6"
    MUTED = Colors.TEXT_LIGHT

    def __init__(
        self,
        parent,
        project,
        *,
        on_back=None,
        on_open_model=None,
    ) -> None:
        self.parent = parent
        self.project = project
        self.on_back = on_back
        self.on_open_model = on_open_model

        self._category_store = ModelCategoryStore(project)
        self._categories: list[dict[str, Any]] = []
        self._project_models: list[Model] = []
        self._working_page: Page | None = None
        self._working_category = ""
        self._working_model_id = ""
        self._page_editor: AtelierPageEditorView | None = None
        self._editor_host: ctk.CTkFrame | None = None
        self._status_var = tk.StringVar(value="Création en cours non enregistrée")
        self._model_count_var = tk.StringVar(value="0 gabarit")

    @property
    def _drafts_root(self) -> Path:
        return Path(self.project.models_folder) / "_atelier_brouillon"

    @property
    def _draft_page_folder(self) -> Path:
        return self._drafts_root / "page_0001"

    @property
    def _ready_folder(self) -> Path:
        return Path(self.project.models_folder) / "prets_conception"

    @property
    def _manifest_file(self) -> Path:
        return self._ready_folder / "manifest.json"

    @property
    def _reusable_library_folder(self) -> Path:
        return Path(__file__).resolve().parents[3] / "bibliotheque_modeles"

    def show(self) -> None:
        self._clear_parent()
        self._categories = self._category_store.load()
        self._project_models = self._load_project_models()
        self._model_count_var.set(self._count_label(len(self._project_models)))

        root = ctk.CTkFrame(self.parent, fg_color=self.WINDOW_BG, corner_radius=0)
        root.pack(fill="both", expand=True)
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)

        self._create_ribbon(root).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=8,
            pady=(5, 4),
        )

        self._editor_host = ctk.CTkFrame(
            root,
            fg_color="#E7EAEE",
            corner_radius=0,
        )
        self._editor_host.grid(row=1, column=0, sticky="nsew")
        self._editor_host.bind("<<AtelierSaveModel>>", lambda _event: self._save_as_project_model())

        if not self._load_existing_draft():
            self._create_default_working_page()
        self._display_working_page()

    def _create_ribbon(self, parent) -> ctk.CTkFrame:
        ribbon = ctk.CTkFrame(
            parent,
            fg_color=self.RIBBON_BG,
            corner_radius=0,
            height=76,
        )
        ribbon.grid_propagate(False)

        self._create_ribbon_group(
            ribbon,
            title="Créer",
            width=168,
            buttons=(
                ("＋", "Nouveau", self.CELADON, self.CELADON_SOFT, self._new_creation),
                ("▦", "Bibliothèque", self.LILAC, self.LILAC_SOFT, self._open_library),
            ),
        ).pack(side="left", fill="y", padx=(6, 3), pady=5)

        self._create_ribbon_group(
            ribbon,
            title="Gabarit du projet",
            width=92,
            buttons=(
                ("▣", "Enregistrer", self.CELADON, self.CELADON_SOFT, self._save_as_project_model),
            ),
        ).pack(side="left", fill="y", padx=3, pady=5)

        self._create_ribbon_group(
            ribbon,
            title="Conception",
            width=92,
            buttons=(
                ("⇢", "Transférer", self.CORAL, self.CORAL_SOFT, self._open_transfer),
            ),
        ).pack(side="left", fill="y", padx=3, pady=5)

        info = ctk.CTkFrame(
            ribbon,
            fg_color=self.GROUP_BG,
            corner_radius=7,
            height=66,
            border_width=1,
            border_color=self.BORDER,
        )
        info.pack(side="left", fill="both", expand=True, padx=(3, 6), pady=5)
        info.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            info,
            textvariable=self._status_var,
            font=Fonts.SMALL,
            text_color=self.INK,
            anchor="w",
            height=21,
        ).grid(row=0, column=0, sticky="ew", padx=9, pady=(8, 0))
        ctk.CTkLabel(
            info,
            textvariable=self._model_count_var,
            font=(Fonts.FAMILY, 8),
            text_color=self.MUTED,
            anchor="w",
            height=17,
        ).grid(row=1, column=0, sticky="ew", padx=9, pady=(0, 5))
        return ribbon

    def _create_ribbon_group(
        self,
        parent,
        *,
        title: str,
        width: int,
        buttons: tuple[tuple[str, str, str, str, Callable[[], None]], ...],
    ) -> ctk.CTkFrame:
        group = ctk.CTkFrame(
            parent,
            width=width,
            height=66,
            fg_color=self.GROUP_BG,
            corner_radius=7,
            border_width=1,
            border_color=self.BORDER,
        )
        group.pack_propagate(False)

        controls = ctk.CTkFrame(group, fg_color="transparent")
        controls.pack(fill="both", expand=True, padx=4, pady=(4, 15))

        for icon, label, color, soft, command in buttons:
            self._create_ribbon_tool(
                controls,
                icon=icon,
                label=label,
                color=color,
                soft=soft,
                command=command,
            ).pack(side="left", padx=2)

        ctk.CTkLabel(
            group,
            text=title,
            height=13,
            font=(Fonts.FAMILY, 8),
            text_color=self.MUTED,
        ).place(relx=0.5, rely=1.0, anchor="s", y=-1)
        return group

    def _create_ribbon_tool(
        self,
        parent,
        *,
        icon: str,
        label: str,
        color: str,
        soft: str,
        command: Callable[[], None],
    ) -> ctk.CTkFrame:
        tool = ctk.CTkFrame(
            parent,
            width=76,
            height=43,
            fg_color=self.GROUP_BG,
            corner_radius=5,
            border_width=1,
            border_color=color,
        )
        tool.pack_propagate(False)

        icon_label = ctk.CTkLabel(
            tool,
            text=icon,
            height=24,
            font=(Fonts.FAMILY, 16, "bold"),
            text_color=color,
        )
        icon_label.pack(fill="x", padx=2, pady=(1, 0))

        text_label = ctk.CTkLabel(
            tool,
            text=label,
            height=14,
            font=(Fonts.FAMILY, 8),
            text_color=self.INK,
        )
        text_label.pack(fill="x", padx=2, pady=(0, 2))

        def activate(_event=None) -> None:
            command()

        def enter(_event=None) -> None:
            tool.configure(fg_color=soft)

        def leave(_event=None) -> None:
            tool.configure(fg_color=self.GROUP_BG)

        for widget in (tool, icon_label, text_label):
            widget.bind("<Button-1>", activate)
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)
            widget.configure(cursor="hand2")

        return tool

    def _new_creation(self) -> None:
        if self._working_page is not None and self._working_page.elements:
            confirmed = messagebox.askyesno(
                "Nouvelle création",
                "Commencer une nouvelle création ?\n\nLa création courante reste disponible uniquement si elle a été enregistrée comme gabarit.",
                parent=self.parent.winfo_toplevel(),
            )
            if not confirmed:
                return

        NewModelDialog(
            self.parent,
            default_format=str(getattr(self.project, "format", Page.DEFAULT_FORMAT)),
            categories=self._category_store.load(),
            on_create_category=lambda created, closed: self._new_category(created, closed),
            on_validate=self._create_working_page,
        )

    def _create_default_working_page(self) -> None:
        default_format = str(getattr(self.project, "format", Page.DEFAULT_FORMAT))
        if default_format not in Page.FORMAT_PRESETS:
            default_format = Page.DEFAULT_FORMAT
        width, height = Page.FORMAT_PRESETS[default_format]
        self._create_working_page(
            {
                "name": "Création sans titre",
                "category": "",
                "format_mode": "preregle",
                "format_name": default_format,
                "width_mm": width,
                "height_mm": height,
                "orientation": Page.DEFAULT_ORIENTATION,
                "margins": {
                    "haut": 15.0,
                    "bas": 15.0,
                    "interieure": 15.0,
                    "exterieure": 15.0,
                },
                "bleed": {"haut": 0.0, "droite": 0.0, "bas": 0.0, "gauche": 0.0},
            },
            display=False,
        )

    def _create_working_page(self, payload: dict[str, Any], *, display: bool = True) -> None:
        self._reset_draft()
        page = Page()
        orientation = str(payload.get("orientation", Page.DEFAULT_ORIENTATION))
        if str(payload.get("format_mode", "preregle")) == "libre":
            page.set_custom_format(
                float(payload.get("width_mm", 148.0)),
                float(payload.get("height_mm", 210.0)),
                orientation=orientation,
                label="Dimensions libres",
            )
        else:
            page.set_format(
                str(payload.get("format_name", Page.DEFAULT_FORMAT)),
                orientation,
            )

        margins = dict(payload.get("margins", {}))
        page.set_margins(
            top_mm=float(margins.get("haut", 15.0)),
            bottom_mm=float(margins.get("bas", 15.0)),
            inside_mm=float(margins.get("interieure", 15.0)),
            outside_mm=float(margins.get("exterieure", 15.0)),
        )
        bleed = dict(payload.get("bleed", {}))
        page.set_bleed(
            top_mm=float(bleed.get("haut", 0.0)),
            right_mm=float(bleed.get("droite", 0.0)),
            bottom_mm=float(bleed.get("bas", 0.0)),
            left_mm=float(bleed.get("gauche", 0.0)),
        )

        page.page_kind = "brouillon_atelier"
        page.structure_workspace = "atelier"
        page.content_workspace = "atelier"
        page.page_type = "Création Atelier"
        page.icon = "▦"
        page.color = self.CELADON_SOFT
        page.create(
            pages_folder=self._drafts_root,
            number=1,
            page_type="Création Atelier",
            title=str(payload.get("name", "Création sans titre")),
        )

        self._working_page = page
        self._working_category = str(payload.get("category", ""))
        self._working_model_id = ""
        self._status_var.set("Création en cours non enregistrée")
        if display:
            self._display_working_page()

    def _load_existing_draft(self) -> bool:
        if not (self._draft_page_folder / "page.json").exists():
            return False
        try:
            self._working_page = Page().load(self._draft_page_folder)
        except (OSError, RuntimeError, TypeError, ValueError):
            return False
        self._working_category = ""
        self._working_model_id = ""
        self._status_var.set("Brouillon de l’Atelier restauré")
        return True

    def _display_working_page(self) -> None:
        if self._editor_host is None or self._working_page is None:
            return
        for widget in self._editor_host.winfo_children():
            widget.destroy()
        self._page_editor = AtelierPageEditorView(
            self._editor_host,
            self._working_page,
            on_back=self._back,
            on_new=self._new_creation,
        )
        self._page_editor.show()

    def _open_library(self) -> None:
        self._save_editor_state()
        self._project_models = self._load_project_models()
        ModelLibraryDialog(
            self.parent,
            reusable_models=self._load_reusable_models(),
            project_models=self._project_models,
            transferred_versions=self._transferred_versions(),
            on_use=self._use_model,
        )

    def _use_model(self, model: Model, source: str) -> None:
        self._reset_draft()
        definition = deepcopy(model.page_definition)
        page = Page()
        page._load_layout(deepcopy(definition.get("mise_en_page", {})))

        editorial = definition.get("editorial", {})
        page.page_type = "Création Atelier"
        page.color = str(editorial.get("couleur", self.CELADON_SOFT))
        page.icon = "▦"
        page.page_kind = "brouillon_atelier"
        page.structure_workspace = "atelier"
        page.content_workspace = "atelier"
        page.content = deepcopy(definition.get("contenu_fixe", {}))
        page.elements = deepcopy(definition.get("elements", []))
        page.create(
            pages_folder=self._drafts_root,
            number=1,
            page_type="Création Atelier",
            title=model.name,
        )

        self._working_page = page
        self._working_category = model.category
        self._working_model_id = model.identifier if source == "gabarits" else ""
        self._status_var.set(
            "Gabarit du projet ouvert pour modification"
            if source == "gabarits"
            else "Modèle rappelé : enregistrer pour en faire un gabarit du projet"
        )
        self._display_working_page()

    def _save_as_project_model(self) -> None:
        if self._working_page is None:
            return
        self._save_editor_state()
        default_name = self._working_page.display_title
        if default_name == "Création sans titre":
            default_name = ""

        SaveProjectModelDialog(
            self.parent,
            default_name=default_name,
            default_category=self._working_category,
            categories=self._category_store.load(),
            on_create_category=lambda created, closed: self._new_category(created, closed),
            on_validate=self._save_model_payload,
        )

    def _save_model_payload(self, payload: dict[str, Any]) -> None:
        if self._working_page is None:
            raise RuntimeError("Aucune création n’est ouverte.")

        name = str(payload.get("name", "")).strip()
        existing = self._find_project_model_by_name(name)
        model: Model

        if existing is not None:
            confirmed = messagebox.askyesno(
                "Mettre à jour le gabarit",
                f"Le gabarit « {name} » existe déjà.\n\nCréer une nouvelle version à partir de la création courante ?",
                parent=self.parent.winfo_toplevel(),
            )
            if not confirmed:
                raise RuntimeError("Enregistrement annulé.")
            existing.update_from_page(
                self._working_page,
                version_note=str(payload.get("version_note", "")),
                auto_prepare_zones=False,
            )
            existing.set_metadata(
                category=str(payload.get("category", "")),
                description=str(payload.get("description", "")),
            )
            model = existing
        else:
            model = Model()
            model.create_from_page(
                models_folder=self.project.models_folder,
                page=self._working_page,
                name=name,
                category=str(payload.get("category", "")),
                description=str(payload.get("description", "")),
                auto_prepare_zones=False,
            )

        self.project.register_model(model.to_summary())
        self._working_page.title = model.name
        self._working_page.save(update_history=False)
        self._working_category = model.category
        self._working_model_id = model.identifier
        self._project_models = self._load_project_models()
        self._model_count_var.set(self._count_label(len(self._project_models)))
        self._status_var.set(f"Gabarit enregistré : {model.name} ({model.version_label})")

    def _open_transfer(self) -> None:
        self._project_models = self._load_project_models()
        if not self._project_models:
            messagebox.showinfo(
                "Aucun gabarit",
                "Enregistre d’abord au moins un gabarit du projet.",
                parent=self.parent.winfo_toplevel(),
            )
            return
        TransferModelsDialog(
            self.parent,
            models=self._project_models,
            on_validate=self._transfer_models,
        )

    def _transfer_models(self, models: list[Model]) -> None:
        self._ready_folder.mkdir(parents=True, exist_ok=True)
        manifest = self._load_manifest()
        entries = {
            str(entry.get("identifiant", "")): dict(entry)
            for entry in manifest.get("gabarits", [])
            if str(entry.get("identifiant", ""))
        }

        transferred_at = datetime.now().isoformat()
        for model in models:
            if model.root is None:
                continue
            destination = self._ready_folder / model.folder_name
            if destination.exists():
                shutil.rmtree(destination)
            shutil.copytree(Path(model.root), destination)
            entries[model.identifier] = {
                "identifiant": model.identifier,
                "nom": model.name,
                "categorie": model.category,
                "version": model.version_number,
                "version_libelle": model.version_label,
                "dossier": model.folder_name,
                "transfere_le": transferred_at,
            }

        data = {
            "version": "1.0",
            "mis_a_jour_le": transferred_at,
            "gabarits": sorted(entries.values(), key=lambda item: str(item.get("nom", "")).casefold()),
        }
        with self._manifest_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        self._status_var.set(f"{len(models)} gabarit(s) transféré(s) vers la Conception")
        messagebox.showinfo(
            "Transfert terminé",
            f"{len(models)} gabarit(s) sont maintenant disponibles dans le Bureau de conception.",
            parent=self.parent.winfo_toplevel(),
        )

    def _new_category(
        self,
        on_created: Callable[[dict[str, Any]], None] | None = None,
        on_closed: Callable[[], None] | None = None,
    ) -> None:
        def save_category(payload: dict[str, Any]) -> None:
            category = self._category_store.add(payload)
            self._categories = self._category_store.categories
            if on_created is not None:
                on_created(category)

        NewCategoryDialog(
            self.parent,
            default_format=str(getattr(self.project, "format", Page.DEFAULT_FORMAT)),
            on_validate=save_category,
            on_close=on_closed,
        )

    def _save_editor_state(self) -> None:
        if self._page_editor is not None:
            self._page_editor._save_page_objects(show_status=False)

    def _reset_draft(self) -> None:
        if self._drafts_root.exists():
            shutil.rmtree(self._drafts_root)
        self._drafts_root.mkdir(parents=True, exist_ok=True)

    def _load_project_models(self) -> list[Model]:
        models: dict[str, Model] = {}
        folder = Path(self.project.models_folder)
        folder.mkdir(parents=True, exist_ok=True)

        for summary in list(getattr(self.project, "models", [])):
            model_folder = folder / str(summary.get("dossier", ""))
            model = self._load_model_folder(model_folder)
            if model is not None:
                models[model.identifier] = model

        for model_file in folder.glob("*/modele.json"):
            if model_file.parent.name.startswith("_"):
                continue
            model = self._load_model_folder(model_file.parent)
            if model is None:
                continue
            models[model.identifier] = model
            self.project.register_model(model.to_summary())

        return sorted(
            models.values(),
            key=lambda item: (item.modified or item.created, item.name.casefold()),
            reverse=True,
        )

    def _load_reusable_models(self) -> list[Model]:
        self._reusable_library_folder.mkdir(parents=True, exist_ok=True)
        models: list[Model] = []
        for model_file in self._reusable_library_folder.glob("*/modele.json"):
            model = self._load_model_folder(model_file.parent)
            if model is not None:
                models.append(model)
        return sorted(models, key=lambda item: item.name.casefold())

    @staticmethod
    def _load_model_folder(folder: Path) -> Model | None:
        if not folder.is_dir() or not (folder / "modele.json").exists():
            return None
        try:
            return Model().load(folder)
        except (OSError, RuntimeError, TypeError, ValueError):
            return None

    def _find_project_model_by_name(self, name: str) -> Model | None:
        normalized = name.strip().casefold()
        for model in self._load_project_models():
            if model.name.strip().casefold() == normalized:
                return model
        return None

    def _load_manifest(self) -> dict[str, Any]:
        if not self._manifest_file.exists():
            return {"version": "1.0", "gabarits": []}
        try:
            with self._manifest_file.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError, TypeError):
            return {"version": "1.0", "gabarits": []}
        return data if isinstance(data, dict) else {"version": "1.0", "gabarits": []}

    def _transferred_versions(self) -> dict[str, int]:
        versions: dict[str, int] = {}
        for entry in self._load_manifest().get("gabarits", []):
            if not isinstance(entry, dict):
                continue
            identifier = str(entry.get("identifiant", ""))
            try:
                version = int(entry.get("version", 0))
            except (TypeError, ValueError):
                version = 0
            if identifier:
                versions[identifier] = version
        return versions

    @staticmethod
    def _count_label(count: int) -> str:
        return f"{count} gabarit" if count == 1 else f"{count} gabarits"

    @staticmethod
    def _hover_color(color: str) -> str:
        value = color.lstrip("#")
        if len(value) != 6:
            return color
        channels = [int(value[index:index + 2], 16) for index in (0, 2, 4)]
        channels = [max(0, channel - 12) for channel in channels]
        return "#" + "".join(f"{channel:02X}" for channel in channels)

    def _back(self) -> None:
        self._save_editor_state()
        if self.on_back is not None:
            self.on_back()

    def _clear_parent(self) -> None:
        for widget in self.parent.winfo_children():
            widget.destroy()