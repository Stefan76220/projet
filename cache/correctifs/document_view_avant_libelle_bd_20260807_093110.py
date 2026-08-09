from __future__ import annotations

import json
import shutil
import tkinter as tk
from tkinter import messagebox
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Callable

import customtkinter as ctk

from src.gui.views.mockup_view import MockupView
from src.gui.views.model_workshop_view import ModelWorkshopView
from src.gui.views.page_editor_view import PageEditorView
from src.library.page_types.page_type_library import PageTypeLibrary
from src.theme.colors import Colors
from src.theme.fonts import Fonts
from src.theme.spacing import Spacing


# Apparence éditoriale commune au Bureau de conception et au Centre du projet.
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
    """Boîte de dialogue utilisée depuis le Centre du projet."""

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

        try:
            self.grab_release()
        except tk.TclError:
            pass

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


class DocumentView:
    """
    Centre du projet PageMaître.

    La vue présente le chemin de fer du livre, les espaces spécialisés
    définis par le scénario directeur, les dernières pages et les listes
    complètes par type de page.

    Aucun élément n'est créé depuis cette vue : le Centre du projet pilote,
    oriente et ouvre le poste de travail adapté.
    """

    # Charte visuelle commune : ruban inspiré de Paint, groupes clairs,
    # boutons compacts et palette PageMaître non agressive.
    WINDOW_BG = Colors.WINDOW
    RIBBON_BG = "#F3F5F7"
    GROUP_BG = "#FFFFFF"
    CARD_BG = "#FCFCFB"
    CANVAS_BG = "#ECEFF2"
    NAVY = "#263E63"
    INK = NAVY
    BORDER = "#D5D9DE"
    TEXT_MUTED = Colors.TEXT_LIGHT
    TEXT_LIGHT = "#8B8E88"

    SKY = "#75B6DB"
    CELADON = "#82B7A1"
    LILAC = "#A997C9"
    CORAL = "#DF806B"
    YELLOW = "#D8B85A"

    MAQUETTAGE = SKY
    MAQUETTAGE_SOFT = "#DDECF4"

    ATELIER = CELADON
    ATELIER_SOFT = "#DFECE5"

    CONCEPTION = LILAC
    CONCEPTION_SOFT = "#E8E1F1"

    ASSEMBLAGE = YELLOW
    ASSEMBLAGE_SOFT = "#F1E8CD"

    VERIFICATION = "#6FA6A5"
    VERIFICATION_SOFT = "#E1EEED"

    FINALISATION = CORAL
    FINALISATION_SOFT = "#F2DDD6"

    PROJECT_TYPE_APPEARANCES = {
        "ouvrage_structure": {
            "label": "Ouvrage structuré",
            "color": CELADON,
            "soft": ATELIER_SOFT,
        },
        "livre_textuel": {
            "label": "Livre textuel",
            "color": LILAC,
            "soft": CONCEPTION_SOFT,
        },
        "bande_dessinee": {
            "label": "Bande dessinée",
            "color": CORAL,
            "soft": FINALISATION_SOFT,
        },
    }

    STATUS_COLORS = {
        "validée": "#34A853",
        "validee": "#34A853",
        "validé": "#34A853",
        "valide": "#34A853",
        "à vérifier": "#F2994A",
        "a verifier": "#F2994A",
        "à valider": "#F2994A",
        "a valider": "#F2994A",
        "brouillon": "#98A2B3",
    }

    CONCEPTION_CREATION_TYPES = (
        {
            "type": "Page vide",
            "title": "Page libre",
            "description": "Composer une page sans structure imposée.",
        },
        {
            "type": "Page de texte",
            "title": "Page de texte",
            "description": "Créer une page principalement textuelle.",
        },
        {
            "type": "Page image",
            "title": "Page image",
            "description": "Créer une page principalement visuelle.",
        },
        {
            "type": "Page de chapitre",
            "title": "Début de chapitre",
            "description": "Créer la première page d’un chapitre.",
        },
        {
            "type": "Couverture",
            "title": "Couverture",
            "description": "Concevoir une couverture complète.",
        },
        {
            "type": "Page de transition",
            "title": "Transition",
            "description": "Créer une séparation entre deux parties.",
        },
        {
            "type": "Page d’illustration",
            "title": "Illustration",
            "description": "Créer une page dédiée à une illustration.",
        },
    )

    WORKSPACES = (
        {
            "key": "maquettage",
            "title": "Maquettage",
            "symbol": "▤",
            "group": "Préparer",
            "color": MAQUETTAGE,
            "soft": MAQUETTAGE_SOFT,
            "enabled": True,
            "requires_document": False,
        },
        {
            "key": "atelier",
            "title": "Atelier",
            "symbol": "▦",
            "group": "Préparer",
            "color": ATELIER,
            "soft": ATELIER_SOFT,
            "enabled": True,
            "requires_document": False,
        },
        {
            "key": "conception",
            "title": "Conception",
            "symbol": "✎",
            "group": "Produire",
            "color": CONCEPTION,
            "soft": CONCEPTION_SOFT,
            "enabled": True,
        },
        {
            "key": "assemblage",
            "title": "Assemblage",
            "symbol": "☷",
            "group": "Produire",
            "color": ASSEMBLAGE,
            "soft": ASSEMBLAGE_SOFT,
            "enabled": False,
        },
        {
            "key": "verification",
            "title": "Vérification",
            "symbol": "✓",
            "group": "Contrôler",
            "color": VERIFICATION,
            "soft": VERIFICATION_SOFT,
            "enabled": False,
        },
        {
            "key": "finalisation",
            "title": "Finalisation",
            "symbol": "⇩",
            "group": "Contrôler",
            "color": FINALISATION,
            "soft": FINALISATION_SOFT,
            "enabled": False,
        },
    )

    TEXTUAL_WORKSPACES = (
        {
            "key": "manuscrit",
            "title": "Manuscrit",
            "symbol": "¶",
            "group": "Préparer",
            "color": LILAC,
            "soft": CONCEPTION_SOFT,
            "enabled": False,
            "requires_document": False,
        },
        {
            "key": "chapitres",
            "title": "Chapitres",
            "symbol": "☰",
            "group": "Préparer",
            "color": SKY,
            "soft": MAQUETTAGE_SOFT,
            "enabled": False,
            "requires_document": False,
        },
        {
            "key": "mise_en_page",
            "title": "Mise en page",
            "symbol": "▤",
            "group": "Produire",
            "color": CELADON,
            "soft": ATELIER_SOFT,
            "enabled": False,
            "requires_document": False,
        },
        {
            "key": "styles",
            "title": "Styles",
            "symbol": "A",
            "group": "Produire",
            "color": ASSEMBLAGE,
            "soft": ASSEMBLAGE_SOFT,
            "enabled": False,
            "requires_document": False,
        },
        {
            "key": "verification",
            "title": "Vérification",
            "symbol": "✓",
            "group": "Contrôler",
            "color": VERIFICATION,
            "soft": VERIFICATION_SOFT,
            "enabled": False,
            "requires_document": False,
        },
        {
            "key": "finalisation",
            "title": "Finalisation",
            "symbol": "⇩",
            "group": "Contrôler",
            "color": FINALISATION,
            "soft": FINALISATION_SOFT,
            "enabled": False,
            "requires_document": False,
        },
    )

    COMIC_WORKSPACES = (
        {
            "key": "storyboard",
            "title": "Storyboard",
            "symbol": "▦",
            "group": "Préparer",
            "color": CORAL,
            "soft": FINALISATION_SOFT,
            "enabled": False,
            "requires_document": False,
        },
        {
            "key": "planches",
            "title": "Planches",
            "symbol": "▧",
            "group": "Préparer",
            "color": SKY,
            "soft": MAQUETTAGE_SOFT,
            "enabled": False,
            "requires_document": False,
        },
        {
            "key": "cases",
            "title": "Cases",
            "symbol": "▥",
            "group": "Produire",
            "color": CELADON,
            "soft": ATELIER_SOFT,
            "enabled": False,
            "requires_document": False,
        },
        {
            "key": "bulles",
            "title": "Bulles",
            "symbol": "◯",
            "group": "Produire",
            "color": LILAC,
            "soft": CONCEPTION_SOFT,
            "enabled": False,
            "requires_document": False,
        },
        {
            "key": "verification",
            "title": "Vérification",
            "symbol": "✓",
            "group": "Contrôler",
            "color": VERIFICATION,
            "soft": VERIFICATION_SOFT,
            "enabled": False,
            "requires_document": False,
        },
        {
            "key": "finalisation",
            "title": "Finalisation",
            "symbol": "⇩",
            "group": "Contrôler",
            "color": FINALISATION,
            "soft": FINALISATION_SOFT,
            "enabled": False,
            "requires_document": False,
        },
    )

    def __init__(
        self,
        parent,
        project,
        application,
        on_open_document=None,
        on_refresh=None,
        on_cleanup=None,
    ) -> None:

        self.parent = parent
        self.project = project
        self.application = application
        self.on_open_document = on_open_document
        self.on_refresh = on_refresh
        self.on_cleanup = on_cleanup

        self.pages: list[dict] = []
        self._rail_canvas: tk.Canvas | None = None
        self._rail_inner: ctk.CTkFrame | None = None
        self._rail_cards: list[ctk.CTkButton] = []
        self._side_content: ctk.CTkFrame | None = None
        self._side_tab_buttons: dict[str, ctk.CTkButton] = {}
        self._model_workshop_view: ModelWorkshopView | None = None
        self._hidden_project_tools: list[tuple[tk.Misc, str, dict]] = []

        self.page_type_library = PageTypeLibrary()
        self.page_type_library.load()

    # ==========================================================
    # Affichage
    # ==========================================================

    def show(self) -> None:
        self.pages = self._load_project_pages()

        # Le Centre est entièrement construit hors affichage. Le conteneur
        # principal n'est rendu visible qu'une fois tous ses éléments prêts,
        # ce qui évite l'apparition successive du bandeau, des outils puis du
        # contenu central.
        root = ctk.CTkFrame(
            self.parent,
            fg_color=self.WINDOW_BG,
            corner_radius=0,
        )
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(2, weight=1)

        header = self._create_header(root)
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=(4, 2),
        )

        workspace_bar = self._create_workspace_bar(root)
        workspace_bar.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=10,
            pady=(0, 5),
        )

        main_workspace = self._create_main_workspace(root)
        main_workspace.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 8),
        )

        # Calcule la disposition pendant que le Centre est encore masqué,
        # puis l'affiche en une seule opération.
        root.update_idletasks()
        root.pack(fill="both", expand=True)
        root.lift()

    def _create_header(self, parent) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            height=36,
        )
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_propagate(False)

        ctk.CTkButton(
            frame,
            text="← Accueil",
            width=92,
            height=30,
            corner_radius=7,
            fg_color=self.GROUP_BG,
            hover_color=Colors.BUTTON_HOVER,
            text_color=self.INK,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.SMALL,
            command=self._return_home,
        ).grid(row=0, column=0, sticky="w", padx=(0, 14))

        ctk.CTkLabel(
            frame,
            text="Centre du projet",
            font=Fonts.H2,
            text_color=self.INK,
        ).grid(row=0, column=1, sticky="w")

        project_name = str(
            getattr(self.project, "name", "")
            or "Projet sans nom"
        )

        project_type = str(
            getattr(
                self.project,
                "project_type",
                "ouvrage_structure",
            )
            or "ouvrage_structure"
        )
        appearance = self.PROJECT_TYPE_APPEARANCES.get(
            project_type,
            self.PROJECT_TYPE_APPEARANCES["ouvrage_structure"],
        )

        badge = ctk.CTkLabel(
            frame,
            text=appearance["label"],
            height=24,
            corner_radius=12,
            fg_color=appearance["soft"],
            text_color=appearance["color"],
            border_width=1,
            border_color=appearance["color"],
            font=(Fonts.FAMILY, 8, "bold"),
            padx=9,
        )
        badge.grid(row=0, column=2, sticky="e", padx=(12, 8))

        ctk.CTkLabel(
            frame,
            text=project_name,
            font=Fonts.SMALL,
            text_color=self.TEXT_MUTED,
        ).grid(row=0, column=3, sticky="e", padx=(0, 2))

        return frame

    def _project_type_key(self) -> str:
        return str(
            getattr(
                self.project,
                "project_type",
                "ouvrage_structure",
            )
            or "ouvrage_structure"
        )

    def _centre_profile(self) -> dict[str, str]:
        project_type = self._project_type_key()

        if project_type == "livre_textuel":
            return {
                "rail_title": "Structure du livre",
                "rail_count": "page(s)",
                "empty": "Aucune page",
                "recent_tab": "Récentes",
                "secondary_tab": "Chapitres",
                "secondary_title": "Organisation du livre",
                "secondary_text": "Manuscrit · Chapitres · Styles · Mise en page",
            }

        if project_type == "bande_dessinee":
            return {
                "rail_title": "Planches du livre",
                "rail_count": "planche(s)",
                "empty": "Aucune planche",
                "recent_tab": "Récentes",
                "secondary_tab": "Storyboard",
                "secondary_title": "Organisation de la BD",
                "secondary_text": "Storyboard · Planches · Cases · Bulles",
            }

        return {
            "rail_title": "Chemin de fer",
            "rail_count": "page(s)",
            "empty": "Aucune page",
            "recent_tab": "Récentes",
            "secondary_tab": "Types",
            "secondary_title": "Types de pages",
            "secondary_text": "",
        }

    def _active_workspaces(self) -> tuple[dict, ...]:
        project_type = str(
            getattr(
                self.project,
                "project_type",
                "ouvrage_structure",
            )
            or "ouvrage_structure"
        )

        if project_type == "livre_textuel":
            return self.TEXTUAL_WORKSPACES

        if project_type == "bande_dessinee":
            return self.COMIC_WORKSPACES

        return self.WORKSPACES

    def _create_workspace_bar(self, parent) -> ctk.CTkFrame:
        """Ruban du Centre construit sur le même modèle que l'Atelier."""

        ribbon = ctk.CTkFrame(
            parent,
            fg_color=self.RIBBON_BG,
            corner_radius=0,
            height=116,
        )
        ribbon.grid_propagate(False)

        content = tk.Frame(ribbon, bg=self.RIBBON_BG)
        content.pack(fill="both", expand=True, padx=8, pady=8)

        def group(
            title: str,
            width: int,
        ) -> tuple[ctk.CTkFrame, ctk.CTkFrame]:
            frame = ctk.CTkFrame(
                content,
                width=width,
                height=98,
                fg_color=self.GROUP_BG,
                corner_radius=10,
            )
            frame.pack(side="left", fill="y", padx=4)
            frame.pack_propagate(False)

            controls = ctk.CTkFrame(
                frame,
                fg_color="transparent",
            )
            controls.pack(
                fill="both",
                expand=True,
                padx=7,
                pady=(7, 1),
            )

            ctk.CTkLabel(
                frame,
                text=title,
                font=Fonts.SMALL,
                text_color=self.TEXT_MUTED,
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
            border_color: str | None = None,
        ) -> ctk.CTkFrame:
            """Petit outil de ruban : icône colorée, libellé sobre."""

            enabled = state == "normal" and callable(command)
            icon_color = (
                border_color or self.NAVY
                if enabled
                else self.TEXT_LIGHT
            )
            outline = (
                border_color or self.BORDER
                if enabled
                else self.BORDER
            )

            tool = ctk.CTkFrame(
                parent_frame,
                width=width,
                height=58,
                corner_radius=7,
                fg_color=self.GROUP_BG,
                border_width=1,
                border_color=outline,
            )
            tool.pack(side="left", padx=3, pady=2)
            tool.pack_propagate(False)

            icon_label = ctk.CTkLabel(
                tool,
                text=icon,
                height=31,
                font=(Fonts.FAMILY, 20, "bold"),
                text_color=icon_color,
            )
            icon_label.pack(fill="x", padx=3, pady=(3, 0))

            text_label = ctk.CTkLabel(
                tool,
                text=label,
                height=18,
                font=(Fonts.FAMILY, 9),
                text_color=self.INK if enabled else self.TEXT_LIGHT,
            )
            text_label.pack(fill="x", padx=3, pady=(0, 3))

            if enabled:
                normal_color = self.GROUP_BG
                hover_color = Colors.BUTTON_HOVER

                def activate(_event=None) -> None:
                    command()

                def enter(_event=None) -> None:
                    tool.configure(fg_color=hover_color)

                def leave(_event=None) -> None:
                    tool.configure(fg_color=normal_color)

                for widget in (tool, icon_label, text_label):
                    widget.bind("<Button-1>", activate)
                    widget.bind("<Enter>", enter)
                    widget.bind("<Leave>", leave)

            return tool

        commands = {
            "maquettage": self._open_mockup,
            "atelier": self._open_model_workshop,
            "conception": self._open_atelier,
        }
        grouped: dict[str, list[dict]] = {
            "Préparer": [],
            "Produire": [],
            "Contrôler": [],
        }
        for workspace in self._active_workspaces():
            grouped[workspace["group"]].append(workspace)

        for group_title in ("Préparer", "Produire", "Contrôler"):
            _, controls = group(group_title, 194)

            for workspace in grouped[group_title]:
                requires_document = bool(
                    workspace.get("requires_document", True)
                )
                has_document = bool(
                    getattr(self.project, "documents", [])
                )
                enabled = bool(
                    workspace["enabled"]
                    and (has_document or not requires_document)
                )

                icon_button(
                    controls,
                    workspace["symbol"],
                    workspace["title"],
                    commands.get(workspace["key"]),
                    width=84,
                    state="normal" if enabled else "disabled",
                    border_color=(
                        workspace["color"]
                        if enabled
                        else self.BORDER
                    ),
                )

        type_count = len({
            self._page_type(page)
            for page in self.pages
        })
        draft_pages = [
            page
            for page in self.pages
            if "brouillon" in self._page_state(page).casefold()
        ]
        validated_pages = [
            page
            for page in self.pages
            if "valid" in self._page_state(page).casefold()
        ]

        _, quick = group("Accès rapide", 282)
        quick_grid = ctk.CTkFrame(quick, fg_color="transparent")
        quick_grid.pack(side="left", padx=1, pady=1)

        quick_links = (
            (
                "☷",
                f"{len(self.pages)} Pages",
                self.MAQUETTAGE,
                self.MAQUETTAGE_SOFT,
                lambda: self._show_page_list(
                    "Toutes les pages",
                    self.pages,
                ),
            ),
            (
                "▦",
                f"{type_count} Types",
                self.ATELIER,
                self.ATELIER_SOFT,
                self._show_type_overview,
            ),
            (
                "✎",
                f"{len(draft_pages)} Brouillons",
                self.CONCEPTION,
                self.CONCEPTION_SOFT,
                lambda pages=draft_pages: self._show_page_list(
                    "Pages en brouillon",
                    pages,
                ),
            ),
            (
                "✓",
                f"{len(validated_pages)} Validées",
                self.VERIFICATION,
                self.VERIFICATION_SOFT,
                lambda pages=validated_pages: self._show_page_list(
                    "Pages validées",
                    pages,
                ),
            ),
        )

        for index, (icon, label, color, soft, command) in enumerate(quick_links):
            link = ctk.CTkFrame(
                quick_grid,
                width=128,
                height=27,
                corner_radius=6,
                fg_color=soft,
                border_width=1,
                border_color=color,
            )
            link.grid(
                row=index // 2,
                column=index % 2,
                padx=2,
                pady=2,
                sticky="ew",
            )
            link.grid_propagate(False)
            link.grid_columnconfigure(1, weight=1)

            icon_label = ctk.CTkLabel(
                link,
                text=icon,
                width=23,
                font=(Fonts.FAMILY, 13, "bold"),
                text_color=color,
            )
            icon_label.grid(row=0, column=0, sticky="nsw", padx=(5, 1))

            text_label = ctk.CTkLabel(
                link,
                text=label,
                font=(Fonts.FAMILY, 9),
                text_color=color,
                anchor="w",
            )
            text_label.grid(row=0, column=1, sticky="nsew", padx=(1, 5))

            def activate(_event=None, callback=command) -> None:
                callback()

            def enter(_event=None, frame=link) -> None:
                frame.configure(fg_color=Colors.BUTTON_HOVER)

            def leave(_event=None, frame=link, base_color=soft) -> None:
                frame.configure(fg_color=base_color)

            for widget in (link, icon_label, text_label):
                widget.bind("<Button-1>", activate)
                widget.bind("<Enter>", enter)
                widget.bind("<Leave>", leave)

        _, project_tools = group("Projet", 108)
        cleanup_state = (
            "normal"
            if callable(self.on_cleanup)
            else "disabled"
        )
        icon_button(
            project_tools,
            "⌫",
            "Nettoyage",
            self.on_cleanup,
            width=84,
            state=cleanup_state,
            border_color=self.NAVY,
        )

        return ribbon

    def _create_quick_access_group(
        self,
        parent,
        column: int,
    ) -> ctk.CTkFrame:
        """Compatibilité avec les anciennes versions du Centre."""
        return ctk.CTkFrame(
            parent,
            fg_color="transparent",
            height=1,
        )

    def _create_main_workspace(self, parent) -> ctk.CTkFrame:
        workspace = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            corner_radius=0,
        )
        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_columnconfigure(1, weight=0, minsize=292)
        workspace.grid_rowconfigure(0, weight=1)

        central = ctk.CTkFrame(
            workspace,
            fg_color="transparent",
            corner_radius=0,
        )
        central.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 6),
        )
        central.grid_columnconfigure(0, weight=1)
        central.grid_rowconfigure(1, weight=1)

        self._create_rail_section(central).grid(
            row=0,
            column=0,
            sticky="ew",
        )

        # Espace volontairement libre : il recevra les futurs outils de
        # pilotage sans alourdir le Centre du projet dès maintenant.
        ctk.CTkFrame(
            central,
            fg_color="transparent",
            corner_radius=0,
        ).grid(
            row=1,
            column=0,
            sticky="nsew",
        )

        self._create_side_navigation(workspace).grid(
            row=0,
            column=1,
            sticky="nsew",
        )
        return workspace

    def _create_side_navigation(self, parent) -> ctk.CTkFrame:
        """Panneau latéral à onglets, cohérent avec l'Atelier."""
        panel = ctk.CTkFrame(
            parent,
            width=292,
            fg_color=self.RIBBON_BG,
            corner_radius=8,
            border_width=1,
            border_color=self.BORDER,
        )
        panel.grid_propagate(False)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        tabs = ctk.CTkFrame(
            panel,
            fg_color="transparent",
            corner_radius=0,
            height=34,
        )
        tabs.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=6,
            pady=(6, 3),
        )
        tabs.grid_columnconfigure((0, 1), weight=1, uniform="centre_tabs")
        tabs.grid_propagate(False)

        profile = self._centre_profile()

        self._side_tab_buttons = {}
        for column, (key, label) in enumerate(
            (
                ("recent", profile["recent_tab"]),
                ("types", profile["secondary_tab"]),
            )
        ):
            button = ctk.CTkButton(
                tabs,
                text=label,
                height=26,
                corner_radius=5,
                fg_color=self.MAQUETTAGE_SOFT,
                hover_color=self._hover_color(self.MAQUETTAGE_SOFT),
                text_color=self.INK,
                border_width=1,
                border_color=self.MAQUETTAGE,
                font=(Fonts.FAMILY, 9),
                command=lambda tab_key=key: self._show_side_tab(tab_key),
            )
            button.grid(
                row=0,
                column=column,
                sticky="ew",
                padx=(0 if column == 0 else 2, 0 if column == 1 else 2),
            )
            self._side_tab_buttons[key] = button

        self._side_content = ctk.CTkFrame(
            panel,
            fg_color=self.CARD_BG,
            corner_radius=7,
        )
        self._side_content.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=6,
            pady=(0, 6),
        )
        self._side_content.grid_columnconfigure(0, weight=1)
        self._side_content.grid_rowconfigure(0, weight=1)

        self._show_side_tab("recent")
        return panel

    def _show_side_tab(self, tab_key: str) -> None:
        if self._side_content is None:
            return

        for key, button in self._side_tab_buttons.items():
            active = key == tab_key
            button.configure(
                fg_color=self.MAQUETTAGE if active else self.MAQUETTAGE_SOFT,
                hover_color=(
                    self._darken_color(self.MAQUETTAGE, amount=0.06)
                    if active
                    else self._hover_color(self.MAQUETTAGE_SOFT)
                ),
                text_color="#FFFFFF" if active else self.INK,
            )

        for child in self._side_content.winfo_children():
            child.destroy()

        if tab_key == "recent":
            content = self._create_recent_pages(self._side_content)
        elif self._project_type_key() == "ouvrage_structure":
            content = self._create_categories(self._side_content)
        else:
            content = self._create_specialized_side_overview(
                self._side_content
            )
        content.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=4,
            pady=4,
        )

    def _create_specialized_side_overview(
        self,
        parent,
    ) -> ctk.CTkFrame:
        profile = self._centre_profile()
        frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            corner_radius=0,
        )
        frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            frame,
            text=profile["secondary_title"],
            font=(Fonts.FAMILY, 11, "bold"),
            text_color=self.INK,
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=8,
            pady=(10, 4),
        )

        ctk.CTkLabel(
            frame,
            text=profile["secondary_text"],
            font=(Fonts.FAMILY, 8),
            text_color=self.TEXT_MUTED,
            justify="left",
            anchor="w",
            wraplength=245,
        ).grid(
            row=1,
            column=0,
            sticky="ew",
            padx=8,
            pady=(0, 10),
        )

        return frame

    def _create_rail_section(self, parent) -> ctk.CTkFrame:
        section = ctk.CTkFrame(
            parent,
            fg_color=self.CARD_BG,
            corner_radius=8,
            border_width=1,
            border_color=self.BORDER,
            height=124,
        )
        section.grid_columnconfigure(0, weight=1)
        section.grid_rowconfigure(1, weight=1)
        section.grid_propagate(False)

        header = ctk.CTkFrame(section, fg_color="transparent", height=20)
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=8,
            pady=(3, 0),
        )
        header.grid_columnconfigure(0, weight=1)
        header.grid_propagate(False)

        ctk.CTkLabel(
            header,
            text=self._centre_profile()["rail_title"],
            font=(Fonts.FAMILY, 11, "bold"),
            text_color=self.INK,
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text=(
                f"{len(self.pages)} "
                f"{self._centre_profile()['rail_count']}"
            ),
            font=(Fonts.FAMILY, 8),
            text_color=self.TEXT_MUTED,
        ).grid(row=0, column=1, sticky="e")

        rail_host = ctk.CTkFrame(
            section,
            fg_color=self.CANVAS_BG,
            corner_radius=5,
        )
        rail_host.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=6,
            pady=(1, 5),
        )
        rail_host.grid_columnconfigure(0, weight=1)
        rail_host.grid_rowconfigure(0, weight=1)

        self._rail_canvas = tk.Canvas(
            rail_host,
            background=self.CANVAS_BG,
            highlightthickness=0,
            height=86,
        )
        self._rail_canvas.grid(row=0, column=0, sticky="nsew")

        scrollbar = ctk.CTkScrollbar(
            rail_host,
            orientation="horizontal",
            command=self._rail_canvas.xview,
            height=7,
        )
        scrollbar.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=5,
            pady=(0, 2),
        )
        self._rail_canvas.configure(xscrollcommand=scrollbar.set)

        self._rail_inner = ctk.CTkFrame(
            self._rail_canvas,
            fg_color="transparent",
        )
        window_id = self._rail_canvas.create_window(
            (0, 0),
            window=self._rail_inner,
            anchor="nw",
        )

        self._rail_inner.bind(
            "<Configure>",
            lambda _event: self._update_rail_scrollregion(),
        )
        self._rail_canvas.bind(
            "<Configure>",
            lambda event: self._on_rail_canvas_configure(
                window_id,
                event.width,
                event.height,
            ),
        )

        self._populate_rail()
        return section

    def _populate_rail(self) -> None:
        if self._rail_inner is None:
            return

        for widget in self._rail_inner.winfo_children():
            widget.destroy()
        self._rail_cards.clear()

        if not self.pages:
            empty = ctk.CTkFrame(
                self._rail_inner,
                width=180,
                height=70,
                fg_color=self.GROUP_BG,
                corner_radius=7,
                border_width=1,
                border_color=self.BORDER,
            )
            empty.pack(side="left", padx=8, pady=6)
            empty.pack_propagate(False)

            ctk.CTkLabel(
                empty,
                text=self._centre_profile()["empty"],
                font=Fonts.SMALL,
                text_color=self.INK,
            ).pack(expand=True)
            return

        for index, page in enumerate(self.pages):
            card = self._create_rail_page(
                self._rail_inner,
                page,
                index,
            )
            self._rail_cards.append(card)
            card.pack(
                side="left",
                padx=((5, 2) if index == 0 else (2, 2)),
                pady=5,
            )

        if self._rail_canvas is not None:
            self._rail_canvas.after_idle(
                lambda: self._resize_rail_cards(
                    self._rail_canvas.winfo_width()
                )
            )

    def _create_rail_page(
        self,
        parent,
        page: dict,
        index: int,
    ) -> ctk.CTkButton:
        state = self._page_state(page)
        appearance = self._page_appearance(page)

        try:
            number_text = f"{int(page.get('numero', index + 1)):03d}"
        except (TypeError, ValueError):
            number_text = str(page.get("numero", index + 1))

        short_type = self._short_page_type(
            self._page_type(page)
        )

        button = ctk.CTkButton(
            parent,
            width=72,
            height=72,
            corner_radius=6,
            fg_color=appearance["couleur"],
            hover_color=self._hover_color(appearance["couleur"]),
            border_width=1,
            border_color=self._status_color(state),
            text_color=self.INK,
            font=(Fonts.FAMILY, 8),
            text=(
                f"{appearance['icone']}  {number_text}\n"
                f"{self._truncate(short_type, 12)}"
            ),
            command=lambda data=page: self._open_page(data),
        )
        self._bind_page_context(button, page)
        return button

    def _on_rail_canvas_configure(
        self,
        window_id: int,
        width: int,
        height: int,
    ) -> None:
        self._keep_rail_height(window_id, height)
        self._resize_rail_cards(width)

    def _resize_rail_cards(self, canvas_width: int) -> None:
        if not self._rail_cards:
            return

        target_visible = 14
        horizontal_gaps = 8 + (target_visible * 4)
        available_width = max(
            canvas_width - horizontal_gaps,
            target_visible * 64,
        )
        card_width = available_width // target_visible
        card_width = max(64, min(82, card_width))

        for card in self._rail_cards:
            card.configure(width=card_width)

        self._update_rail_scrollregion()

    def _update_rail_scrollregion(self) -> None:
        if self._rail_canvas is None:
            return

        self._rail_canvas.configure(
            scrollregion=self._rail_canvas.bbox("all"),
        )

    def _keep_rail_height(
        self,
        window_id: int,
        height: int,
    ) -> None:
        if self._rail_canvas is None:
            return

        self._rail_canvas.itemconfigure(
            window_id,
            height=max(height, 80),
        )

    def _create_project_overview(self, parent) -> ctk.CTkFrame:
        """Compatibilité : les accès sont désormais intégrés au ruban."""
        return ctk.CTkFrame(parent, fg_color="transparent", height=1)

    def _create_recent_pages(self, parent) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            corner_radius=0,
        )
        frame.grid_columnconfigure(0, weight=1)

        recent_pages = sorted(
            self.pages,
            key=lambda page: self._date_sort_key(
                page.get("date_creation", "")
            ),
            reverse=True,
        )[:6]

        if not recent_pages:
            ctk.CTkLabel(
                frame,
                text="Aucune page",
                font=(Fonts.FAMILY, 9),
                text_color=self.TEXT_MUTED,
            ).grid(
                row=0,
                column=0,
                sticky="w",
                padx=4,
                pady=4,
            )
            return frame

        for row, page in enumerate(recent_pages):
            self._create_recent_row(frame, page).grid(
                row=row,
                column=0,
                sticky="ew",
                padx=1,
                pady=(0 if row == 0 else 2, 0),
            )
        return frame

    def _create_recent_row(
        self,
        parent,
        page: dict,
    ) -> ctk.CTkButton:
        name = self._truncate(
            str(page.get("nom", "Page sans nom")),
            21,
        )
        state = self._page_state(page)
        appearance = self._page_appearance(page)

        button = ctk.CTkButton(
            parent,
            height=23,
            corner_radius=4,
            fg_color=appearance["couleur"],
            hover_color=self._hover_color(appearance["couleur"]),
            text_color=self.INK,
            border_width=1,
            border_color=self._status_color(state),
            font=(Fonts.FAMILY, 8),
            anchor="w",
            text=f"{appearance['icone']}  {name}",
            command=lambda data=page: self._open_page(data),
        )
        self._bind_page_context(button, page)
        return button

    def _create_categories(self, parent) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            corner_radius=0,
        )
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=1)

        list_frame = ctk.CTkScrollableFrame(
            frame,
            fg_color="transparent",
            corner_radius=0,
        )
        list_frame.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        list_frame.grid_columnconfigure(0, weight=1)

        self._create_category_row(
            list_frame,
            label="Toutes les pages",
            count=len(self.pages),
            command=lambda: self._show_page_list(
                "Toutes les pages",
                self.pages,
            ),
            background="#E7EEF6",
            icon="☷",
        ).grid(row=0, column=0, sticky="ew", pady=(0, 2))

        type_counts = Counter(self._page_type(page) for page in self.pages)

        for row, (page_type, count) in enumerate(
            sorted(
                type_counts.items(),
                key=lambda item: (-item[1], item[0].casefold()),
            ),
            start=1,
        ):
            matching_pages = [
                page
                for page in self.pages
                if self._page_type(page) == page_type
            ]
            appearance = self._appearance_for_type(page_type)

            self._create_category_row(
                list_frame,
                label=page_type,
                count=count,
                command=lambda title=page_type, pages=matching_pages: (
                    self._show_page_list(title, pages)
                ),
                background=appearance["couleur"],
                icon=appearance["icone"],
            ).grid(row=row, column=0, sticky="ew", pady=(0, 2))
        return frame

    def _create_category_row(
        self,
        parent,
        label: str,
        count: int,
        command: Callable[[], None],
        background: str,
        icon: str,
    ) -> ctk.CTkButton:
        return ctk.CTkButton(
            parent,
            height=23,
            corner_radius=4,
            fg_color=background,
            hover_color=self._hover_color(background),
            text_color=self.INK,
            border_width=1,
            border_color=self._darken_color(background, amount=0.12),
            font=(Fonts.FAMILY, 8),
            anchor="w",
            text=f"{icon}  {label}  ({count})",
            command=command,
        )

    def _show_type_overview(self) -> None:
        """Affiche les types de pages comme liens de triage."""
        window = ctk.CTkToplevel(self.parent)
        window.title("Types de pages — PageMaître")
        window.geometry("760x500")
        window.minsize(620, 380)
        window.configure(fg_color=self.WINDOW_BG)
        window.transient(self.parent.winfo_toplevel())
        window.grid_columnconfigure(0, weight=1)
        window.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(
            window,
            fg_color="transparent",
            corner_radius=0,
            height=36,
        )
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(6, 4))
        header.grid_columnconfigure(0, weight=1)
        header.grid_propagate(False)

        ctk.CTkLabel(
            header,
            text="Types de pages",
            font=Fonts.H2,
            text_color=self.INK,
        ).grid(row=0, column=0, sticky="w")

        type_counts = Counter(self._page_type(page) for page in self.pages)
        ctk.CTkLabel(
            header,
            text=f"{len(type_counts)} type(s)",
            font=Fonts.SMALL,
            text_color=self.TEXT_MUTED,
        ).grid(row=0, column=1, sticky="e")

        list_frame = ctk.CTkScrollableFrame(
            window,
            fg_color=self.CARD_BG,
            corner_radius=10,
            border_width=1,
            border_color=self.BORDER,
        )
        list_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 10),
        )

        columns = 3
        for column in range(columns):
            list_frame.grid_columnconfigure(
                column,
                weight=1,
                uniform="type_links",
            )

        if not type_counts:
            ctk.CTkLabel(
                list_frame,
                text="Aucun type de page",
                font=Fonts.SMALL,
                text_color=self.TEXT_MUTED,
            ).grid(row=0, column=0, sticky="w", padx=10, pady=10)
            return

        for index, (page_type, count) in enumerate(
            sorted(type_counts.items(), key=lambda item: item[0].casefold())
        ):
            matching_pages = [
                page
                for page in self.pages
                if self._page_type(page) == page_type
            ]
            appearance = self._appearance_for_type(page_type)
            row = index // columns
            column = index % columns

            ctk.CTkButton(
                list_frame,
                height=40,
                corner_radius=7,
                fg_color=appearance["couleur"],
                hover_color=self._hover_color(appearance["couleur"]),
                border_width=1,
                border_color=self._darken_color(
                    appearance["couleur"],
                    amount=0.12,
                ),
                text_color=self.INK,
                font=(Fonts.FAMILY, 10),
                anchor="w",
                text=f"{appearance['icone']}  {page_type}  ({count})",
                command=lambda title=page_type, pages=matching_pages: (
                    self._show_page_list(title, pages)
                ),
            ).grid(
                row=row,
                column=column,
                sticky="ew",
                padx=(0 if column == 0 else 3, 0 if column == columns - 1 else 3),
                pady=(0 if row == 0 else 3, 0),
            )

    def _show_page_list(
        self,
        title: str,
        pages: list[dict],
    ) -> None:
        window = ctk.CTkToplevel(self.parent)
        window.title(f"{title} — PageMaître")
        window.geometry("900x560")
        window.minsize(720, 440)
        window.configure(fg_color=self.WINDOW_BG)
        window.transient(self.parent.winfo_toplevel())
        window.grid_columnconfigure(0, weight=1)
        window.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(
            window,
            fg_color="transparent",
            corner_radius=0,
            height=38,
        )
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(6, 4))
        header.grid_columnconfigure(0, weight=1)
        header.grid_propagate(False)

        ctk.CTkLabel(
            header,
            text=title,
            font=Fonts.H2,
            text_color=self.INK,
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text=f"{len(pages)} page(s)",
            font=Fonts.SMALL,
            text_color=self.TEXT_MUTED,
        ).grid(row=0, column=1, sticky="e")

        list_frame = ctk.CTkScrollableFrame(
            window,
            fg_color=self.CARD_BG,
            corner_radius=10,
            border_width=1,
            border_color=self.BORDER,
        )
        list_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 10),
        )
        list_frame.grid_columnconfigure(0, weight=1)

        if not pages:
            ctk.CTkLabel(
                list_frame,
                text="Aucune page",
                font=Fonts.SMALL,
                text_color=self.TEXT_MUTED,
            ).grid(row=0, column=0, sticky="w", padx=10, pady=10)
            return

        for row, page in enumerate(pages):
            name = str(page.get("nom", "Page sans nom"))
            number = page.get("numero", row + 1)
            page_type = self._page_type(page)
            state = self._page_state(page)
            document_name = str(page.get("_document_name", ""))
            appearance = self._page_appearance(page)

            button = ctk.CTkButton(
                list_frame,
                height=40,
                corner_radius=7,
                fg_color=appearance["couleur"],
                hover_color=self._hover_color(appearance["couleur"]),
                border_width=1,
                border_color=self._status_color(state),
                text_color=self.INK,
                font=Fonts.SMALL,
                anchor="w",
                text=(
                    f"{appearance['icone']}  {number:>3}   {name}"
                    f"   ·   {page_type}   ·   {state}"
                    f"   ·   {document_name}"
                ),
                command=lambda data=page, dialog=window: (
                    self._open_page_from_list(data, dialog)
                ),
            )
            self._bind_page_context(
                button,
                page,
                owner_window=window,
            )
            button.grid(row=row, column=0, sticky="ew", pady=(0, 4))

    def _bind_page_context(
        self,
        widget,
        page: dict,
        owner_window=None,
        refresh_mode: str = "centre",
    ) -> None:
        """
        Lie le clic droit à tous les composants internes d'un bouton
        CustomTkinter afin que le menu fonctionne sur le fond et le texte.
        """

        callback = (
            lambda event, data=page, owner=owner_window: (
                self._show_page_context_menu(
                    event,
                    data,
                    owner,
                    refresh_mode,
                )
            )
        )

        targets = [widget]

        for attribute in (
            "_canvas",
            "_text_label",
            "_image_label",
        ):
            target = getattr(
                widget,
                attribute,
                None,
            )
            if target is not None:
                targets.append(target)

        for target in targets:
            try:
                target.bind(
                    "<Button-3>",
                    callback,
                    add="+",
                )
            except (AttributeError, tk.TclError):
                continue

    def _show_page_context_menu(
        self,
        event,
        page: dict,
        owner_window=None,
        refresh_mode: str = "centre",
    ):
        """Ouvre les commandes de la page au point du clic droit."""

        parent = (
            owner_window
            if owner_window is not None
            else self.parent
        )

        menu = tk.Menu(
            parent,
            tearoff=False,
        )

        menu.add_command(
            label="Ouvrir dans le Bureau de conception",
            command=lambda: self._schedule_page_action(
                lambda: self._open_page_from_context(
                    page,
                    owner_window,
                    refresh_mode,
                )
            ),
        )
        menu.add_separator()
        menu.add_command(
            label="Renommer…",
            command=lambda: self._schedule_page_action(
                lambda: self._rename_page_from_centre(
                    page,
                    owner_window,
                    refresh_mode,
                )
            ),
        )

        type_menu = tk.Menu(
            menu,
            tearoff=False,
        )
        current_type = self._page_type(page)

        for page_type in self._available_page_types():
            appearance = self._appearance_for_type(
                page_type
            )
            check = (
                "✓ "
                if page_type == current_type
                else ""
            )

            type_menu.add_command(
                label=(
                    f"{check}{appearance['icone']}  {page_type}"
                ),
                command=lambda selected_type=page_type: (
                    self._schedule_page_action(
                        lambda: self._change_page_type_from_centre(
                            page,
                            selected_type,
                            owner_window,
                            refresh_mode,
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
                lambda: self._duplicate_page_from_centre(
                    page,
                    owner_window,
                    refresh_mode,
                )
            ),
        )
        menu.add_separator()
        menu.add_command(
            label="Supprimer…",
            command=lambda: self._schedule_page_action(
                lambda: self._delete_page_from_centre(
                    page,
                    owner_window,
                    refresh_mode,
                )
            ),
        )

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

    def _schedule_page_action(self, action) -> None:
        """Exécute l'action après la fermeture du menu natif."""

        try:
            self.parent.after(
                40,
                action,
            )
        except tk.TclError:
            return

    def _open_page_from_context(
        self,
        page: dict,
        owner_window=None,
        refresh_mode: str = "centre",
    ) -> None:

        if owner_window is not None:
            try:
                owner_window.destroy()
            except tk.TclError:
                pass

        self._open_page(
            page,
            return_to_atelier=(
                refresh_mode == "atelier"
            ),
        )

    def _rename_page_from_centre(
        self,
        page: dict,
        owner_window=None,
        refresh_mode: str = "centre",
    ) -> None:

        parent = (
            owner_window
            if owner_window is not None
            else self.parent
        )

        RenamePageDialog(
            parent=parent,
            current_name=str(
                page.get(
                    "nom",
                    "Page sans nom",
                )
            ),
            on_validate=lambda new_name: self._apply_page_name_from_centre(
                page,
                new_name,
                owner_window,
                refresh_mode,
            ),
        )

    def _apply_page_name_from_centre(
        self,
        page: dict,
        new_name: str,
        owner_window=None,
        refresh_mode: str = "centre",
    ) -> None:

        clean_name = new_name.strip()

        if not clean_name:
            return

        document, selected_page = self._load_page_for_action(
            page
        )

        if document is None or selected_page is None:
            return

        if getattr(
            selected_page,
            "locked",
            False,
        ):
            messagebox.showwarning(
                title="Page verrouillée",
                message=(
                    "Déverrouille la page dans le Bureau de conception "
                    "avant de la renommer."
                ),
                parent=self._dialog_parent(
                    owner_window
                ),
            )
            return

        try:
            selected_page.rename(
                clean_name
            )
            document.update_page_summary(
                selected_page
            )
        except (
            OSError,
            RuntimeError,
            ValueError,
        ):
            return

        self._refresh_after_page_action(
            owner_window,
            refresh_mode,
        )

    def _change_page_type_from_centre(
        self,
        page: dict,
        page_type: str,
        owner_window=None,
        refresh_mode: str = "centre",
    ) -> None:

        document, selected_page = self._load_page_for_action(
            page
        )

        if document is None or selected_page is None:
            return

        if getattr(
            selected_page,
            "locked",
            False,
        ):
            messagebox.showwarning(
                title="Page verrouillée",
                message=(
                    "Déverrouille la page dans le Bureau de conception "
                    "avant de modifier son type."
                ),
                parent=self._dialog_parent(
                    owner_window
                ),
            )
            return

        appearance = self._appearance_for_type(
            page_type
        )

        try:
            selected_page.set_type(
                page_type
            )
            selected_page.color = appearance["couleur"]
            selected_page.icon = appearance["icone"]
            selected_page.save(
                update_history=False
            )
            document.update_page_summary(
                selected_page
            )
        except (
            OSError,
            RuntimeError,
            ValueError,
        ):
            return

        self._refresh_after_page_action(
            owner_window,
            refresh_mode,
        )

    def _duplicate_page_from_centre(
        self,
        page: dict,
        owner_window=None,
        refresh_mode: str = "centre",
    ) -> None:

        document, selected_page = self._load_page_for_action(
            page
        )

        if document is None or selected_page is None:
            return

        try:
            duplicated_page = document.duplicate_page(
                selected_page.number
            )
        except (
            OSError,
            RuntimeError,
            ValueError,
        ):
            duplicated_page = None

        if duplicated_page is None:
            return

        self._refresh_after_page_action(
            owner_window,
            refresh_mode,
        )

    def _delete_page_from_centre(
        self,
        page: dict,
        owner_window=None,
        refresh_mode: str = "centre",
    ) -> None:

        document, selected_page = self._load_page_for_action(
            page
        )

        if document is None or selected_page is None:
            return

        if getattr(
            selected_page,
            "locked",
            False,
        ):
            messagebox.showwarning(
                title="Page verrouillée",
                message=(
                    "Déverrouille la page dans le Bureau de conception "
                    "avant de la supprimer."
                ),
                parent=self._dialog_parent(
                    owner_window
                ),
            )
            return

        confirmed = messagebox.askyesno(
            title="Supprimer la page",
            message=(
                f"Supprimer définitivement "
                f"« {selected_page.display_title} » ?\n\n"
                "Cette action ne pourra pas être annulée."
            ),
            icon="warning",
            parent=self._dialog_parent(
                owner_window
            ),
        )

        if not confirmed:
            return

        page_index = None

        for index, page_info in enumerate(
            document.pages
        ):
            same_identifier = (
                page_info.get("identifiant")
                and page_info.get("identifiant")
                == selected_page.identifier
            )
            same_number = (
                page_info.get("numero")
                == selected_page.number
            )

            if same_identifier or same_number:
                page_index = index
                break

        if page_index is None:
            return

        page_root = getattr(
            selected_page,
            "root",
            None,
        )

        try:
            if (
                page_root is not None
                and Path(page_root).exists()
            ):
                shutil.rmtree(
                    Path(page_root)
                )

            document.pages.pop(
                page_index
            )
            document.save()
        except OSError:
            return

        self._refresh_after_page_action(
            owner_window,
            refresh_mode,
        )

    def _load_page_for_action(
        self,
        page: dict,
    ):

        document_name = str(
            page.get(
                "_document_name",
                "",
            )
        ).strip()

        page_number = page.get(
            "numero"
        )

        if not document_name or page_number is None:
            return None, None

        try:
            document = (
                self.application.document_manager.load_document(
                    document_name
                )
            )
            selected_page = document.get_page(
                int(page_number)
            )
        except (
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
            KeyError,
        ):
            return None, None

        return document, selected_page

    def _refresh_after_page_action(
        self,
        owner_window=None,
        refresh_mode: str = "centre",
    ) -> None:

        if owner_window is not None:
            try:
                owner_window.destroy()
            except tk.TclError:
                pass

        if refresh_mode == "atelier":
            self._show_atelier_home()
            return

        if self.on_refresh is not None:
            self.on_refresh()

    def _dialog_parent(
        self,
        owner_window=None,
    ):

        if (
            owner_window is not None
            and owner_window.winfo_exists()
        ):
            return owner_window

        return self.parent.winfo_toplevel()

    def _available_page_types(self) -> list[str]:

        names = ["Page vide"]

        try:
            self.page_type_library.load()
            names.extend(
                page_type.name
                for page_type in self.page_type_library.all()
            )
        except (
            OSError,
            ValueError,
            json.JSONDecodeError,
        ):
            pass

        names.extend(
            PAGE_TYPE_APPEARANCES.keys()
        )

        unique_names: list[str] = []

        for name in names:
            clean_name = str(name).strip()

            if clean_name and clean_name not in unique_names:
                unique_names.append(
                    clean_name
                )

        return unique_names

    # ==========================================================
    # Lecture du projet
    # ==========================================================

    def _load_project_pages(self) -> list[dict]:

        project_root = getattr(
            self.project,
            "root",
            None,
        )

        if project_root is None:
            return []

        pages: list[dict] = []

        for document_order, document_info in enumerate(
            getattr(self.project, "documents", [])
        ):

            document_name = str(
                document_info.get("nom", "")
            ).strip()

            if not document_name:
                continue

            document_file = (
                Path(project_root)
                / "documents"
                / document_name
                / "document.json"
            )

            if not document_file.exists():
                continue

            try:
                with document_file.open(
                    "r",
                    encoding="utf-8",
                ) as file:
                    document_data = json.load(file)
            except (OSError, json.JSONDecodeError):
                continue

            for page_order, page_info in enumerate(
                document_data.get("pages", [])
            ):

                page = dict(page_info)
                page["_document_info"] = document_info
                page["_document_name"] = document_name
                page["_document_order"] = document_order
                page["_page_order"] = page_order

                pages.append(page)

        pages.sort(
            key=lambda page: (
                page.get("_document_order", 0),
                page.get("_page_order", 0),
                page.get("numero", 0),
            )
        )

        return pages

    # ==========================================================
    # Actions
    # ==========================================================

    def _return_home(self) -> None:
        """Retourne à l'accueil général de PageMaître."""

        document_manager = getattr(
            self.application,
            "document_manager",
            None,
        )

        if document_manager is not None:
            try:
                document_manager.close_document()
            except Exception:
                pass

        main_window = getattr(
            self.application,
            "main_window",
            None,
        )

        if main_window is None:
            main_window = getattr(
                self.application,
                "window",
                None,
            )

        workspace = getattr(
            main_window,
            "workspace",
            None,
        )

        if (
            workspace is not None
            and hasattr(workspace, "show_dashboard")
        ):
            workspace.show_dashboard()

    def _open_mockup(self) -> None:
        """Ouvre le pré-chemin de fer facultatif du projet."""

        self._hide_project_tools_for_subspace()

        MockupView(
            parent=self.parent,
            project=self.project,
            on_back=self._return_to_project_centre,
        ).show()

    def _open_model_workshop(self) -> None:
        """Ouvre l’Atelier en réutilisant l’éditeur déjà construit."""

        self._hide_project_tools_for_subspace()

        if self._model_workshop_view is None:
            self._model_workshop_view = ModelWorkshopView(
                parent=self.parent,
                project=self.project,
                on_back=self._close_model_workshop,
            )

        self._model_workshop_view.show()

    def _close_model_workshop(self) -> None:
        """Revient au Centre sans reconstruire les deux espaces."""

        view = self._model_workshop_view
        if view is not None:
            view.hide()
        self._restore_project_tools_after_subspace()

    def _hide_project_tools_for_subspace(self) -> None:
        """Masque les outils du Centre tout en mémorisant leur disposition."""

        if self._hidden_project_tools:
            return

        centre = getattr(self.parent, "master", None)

        if centre is None:
            return

        for widget in centre.winfo_children():
            if widget is self.parent:
                continue

            manager = widget.winfo_manager()
            if not manager:
                continue

            geometry: dict = {}
            try:
                if manager == "pack":
                    geometry = dict(widget.pack_info())
                    geometry.pop("in", None)
                    widget.pack_forget()
                elif manager == "grid":
                    geometry = dict(widget.grid_info())
                    geometry.pop("in", None)
                    widget.grid_remove()
                elif manager == "place":
                    geometry = dict(widget.place_info())
                    geometry.pop("in", None)
                    widget.place_forget()
                else:
                    continue
            except tk.TclError:
                continue

            self._hidden_project_tools.append(
                (widget, manager, geometry)
            )

    def _restore_project_tools_after_subspace(self) -> None:
        """Restaure exactement les outils masqués avant l’ouverture."""

        hidden = tuple(self._hidden_project_tools)
        self._hidden_project_tools.clear()

        for widget, manager, geometry in hidden:
            try:
                if not widget.winfo_exists():
                    continue
                if manager == "pack":
                    widget.pack(**geometry)
                elif manager == "grid":
                    widget.grid(**geometry)
                elif manager == "place":
                    widget.place(**geometry)
            except (tk.TclError, TypeError):
                pass

    def _return_to_project_centre(self) -> None:
        """Revient au Centre du projet sans double rafraîchissement visible."""

        if self.on_refresh is not None:
            self.on_refresh()
            return

        self.parent.pack_forget()

        try:
            self._clear_parent_widgets()
            self.show()
            self.parent.update_idletasks()
        finally:
            self.parent.pack(fill="both", expand=True)

    def _open_atelier(self) -> None:
        """Ouvre l’accueil fonctionnel du Bureau de conception."""

        self._show_atelier_home()

    def _show_atelier_home(self) -> None:
        """
        Présente les pages disponibles dans le Bureau de conception sans exposer
        le conteneur technique interne du projet.
        """

        self.pages = self._load_project_pages()
        self._clear_parent_widgets()

        root = ctk.CTkFrame(
            self.parent,
            fg_color=self.WINDOW_BG,
            corner_radius=0,
        )
        root.pack(
            fill="both",
            expand=True,
        )
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(2, weight=1)

        self._create_atelier_header(root).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=Spacing.XL,
            pady=(Spacing.MD, Spacing.SM),
        )

        self._create_atelier_creation_section(root).grid(
            row=1,
            column=0,
            sticky="ew",
            padx=Spacing.XL,
            pady=(0, Spacing.SM),
        )

        self._create_atelier_recent_section(root).grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=Spacing.XL,
            pady=(0, Spacing.MD),
        )

    def _create_atelier_header(
        self,
        parent,
    ) -> ctk.CTkFrame:

        header = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            header,
            text="← Centre du projet",
            width=146,
            height=36,
            corner_radius=9,
            fg_color=self.CARD_BG,
            hover_color="#E9EEF4",
            text_color=self.NAVY,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.NORMAL,
            command=self._back_to_centre,
        ).grid(
            row=0,
            column=0,
            rowspan=2,
            sticky="w",
            padx=(0, Spacing.MD),
        )

        ctk.CTkLabel(
            header,
            text="Bureau de conception",
            font=Fonts.TITLE,
            text_color=self.CONCEPTION,
        ).grid(
            row=0,
            column=1,
            sticky="w",
        )

        ctk.CTkLabel(
            header,
            text=(
                "Remplir les gabarits avec les contenus réels"
            ),
            font=Fonts.NORMAL,
            text_color=self.TEXT_MUTED,
        ).grid(
            row=1,
            column=1,
            sticky="w",
        )

        project_name = str(
            getattr(
                self.project,
                "name",
                "",
            )
            or "Projet sans nom"
        )

        ctk.CTkLabel(
            header,
            text=project_name,
            font=Fonts.H2,
            text_color=self.TEXT_MUTED,
        ).grid(
            row=0,
            column=2,
            rowspan=2,
            sticky="e",
        )

        return header

    def _create_atelier_creation_section(
        self,
        parent,
    ) -> ctk.CTkFrame:

        section = ctk.CTkFrame(
            parent,
            fg_color=self.CARD_BG,
            corner_radius=16,
            border_width=1,
            border_color=self.BORDER,
        )
        section.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            section,
            text="Créer dans le Bureau de conception",
            font=Fonts.H1,
            text_color=self.NAVY,
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=Spacing.LG,
            pady=(Spacing.MD, Spacing.XS),
        )

        ctk.CTkLabel(
            section,
            text=(
                "Choisis la fonction de la nouvelle création. "
                "Elle s’ouvrira immédiatement dans l’éditeur."
            ),
            font=Fonts.NORMAL,
            text_color=self.TEXT_MUTED,
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=Spacing.LG,
            pady=(0, Spacing.SM),
        )

        grid = ctk.CTkFrame(
            section,
            fg_color="transparent",
        )
        grid.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=Spacing.MD,
            pady=(0, Spacing.MD),
        )

        for column in range(4):
            grid.grid_columnconfigure(
                column,
                weight=1,
                uniform="atelier_creations",
            )

        for index, creation in enumerate(
            self.CONCEPTION_CREATION_TYPES
        ):
            page_type = creation["type"]
            appearance = self._appearance_for_type(
                page_type
            )

            button = ctk.CTkButton(
                grid,
                height=86,
                corner_radius=11,
                fg_color=appearance["couleur"],
                hover_color=self._hover_color(
                    appearance["couleur"]
                ),
                text_color=self.NAVY,
                border_width=1,
                border_color=self._darken_color(
                    appearance["couleur"],
                    amount=0.14,
                ),
                font=Fonts.NORMAL,
                text=(
                    f"{appearance['icone']}  {creation['title']}\n"
                    f"{creation['description']}"
                ),
                command=lambda selected_type=page_type: (
                    self._create_atelier_page(
                        selected_type
                    )
                ),
            )
            button.grid(
                row=index // 4,
                column=index % 4,
                sticky="nsew",
                padx=Spacing.XS,
                pady=Spacing.XS,
            )

        return section

    def _create_atelier_recent_section(
        self,
        parent,
    ) -> ctk.CTkFrame:

        section = ctk.CTkFrame(
            parent,
            fg_color=self.CARD_BG,
            corner_radius=16,
            border_width=1,
            border_color=self.BORDER,
        )
        section.grid_columnconfigure(0, weight=1)
        section.grid_rowconfigure(1, weight=1)

        title_row = ctk.CTkFrame(
            section,
            fg_color="transparent",
        )
        title_row.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=Spacing.LG,
            pady=(Spacing.MD, Spacing.SM),
        )
        title_row.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            title_row,
            text="Reprendre une création",
            font=Fonts.H1,
            text_color=self.NAVY,
        ).grid(
            row=0,
            column=0,
            sticky="w",
        )

        ctk.CTkLabel(
            title_row,
            text="Les cinq dernières pages en conception",
            font=Fonts.NORMAL,
            text_color=self.TEXT_MUTED,
        ).grid(
            row=0,
            column=1,
            sticky="e",
        )

        content = ctk.CTkFrame(
            section,
            fg_color="transparent",
        )
        content.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=Spacing.MD,
            pady=(0, Spacing.MD),
        )
        content.grid_columnconfigure(0, weight=1)

        recent_pages = sorted(
            self.pages,
            key=lambda page: str(
                page.get(
                    "date_modification",
                    page.get(
                        "date_creation",
                        "",
                    ),
                )
            ),
            reverse=True,
        )[:5]

        if not recent_pages:
            ctk.CTkLabel(
                content,
                text=(
                    "Aucune page en conception pour le moment. "
                    "Choisis un type ci-dessus pour commencer."
                ),
                font=Fonts.NORMAL,
                text_color=self.TEXT_MUTED,
            ).grid(
                row=0,
                column=0,
                sticky="w",
                padx=Spacing.SM,
                pady=Spacing.SM,
            )
            return section

        for row, page in enumerate(recent_pages):
            appearance = self._page_appearance(
                page
            )
            page_type = self._page_type(
                page
            )
            name = self._truncate(
                str(
                    page.get(
                        "nom",
                        "Page sans nom",
                    )
                ),
                42,
            )
            modified = self._format_date(
                page.get(
                    "date_modification",
                    page.get(
                        "date_creation",
                        "",
                    ),
                )
            )

            button = ctk.CTkButton(
                content,
                height=42,
                corner_radius=9,
                fg_color=appearance["couleur"],
                hover_color=self._hover_color(
                    appearance["couleur"]
                ),
                text_color=self.NAVY,
                border_width=1,
                border_color=self._darken_color(
                    appearance["couleur"],
                    amount=0.14,
                ),
                font=Fonts.NORMAL,
                anchor="w",
                text=(
                    f"{appearance['icone']}  {name}"
                    f"   ·   {page_type}"
                    f"   ·   {modified}"
                ),
                command=lambda data=page: (
                    self._open_page_in_atelier(
                        data
                    )
                ),
            )
            button.grid(
                row=row,
                column=0,
                sticky="ew",
                pady=(0, 5),
            )

            self._bind_page_context(
                button,
                page,
                refresh_mode="atelier",
            )

        return section

    def _create_atelier_page(
        self,
        page_type: str,
    ) -> None:
        """Crée une page réelle puis ouvre l’éditeur de conception."""

        documents = list(
            getattr(
                self.project,
                "documents",
                [],
            )
        )

        if not documents:
            return

        document_name = str(
            documents[0].get(
                "nom",
                "",
            )
        ).strip()

        if not document_name:
            return

        try:
            document = (
                self.application.document_manager.load_document(
                    document_name
                )
            )
            new_page = document.add_page(
                page_type=page_type
            )

            appearance = self._appearance_for_type(
                page_type
            )
            new_page.color = appearance["couleur"]
            new_page.icon = appearance["icone"]
            new_page.save(
                update_history=False
            )
            document.update_page_summary(
                new_page
            )

        except (
            OSError,
            RuntimeError,
            TypeError,
            ValueError,
            KeyError,
        ):
            return

        PageEditorView(
            self.parent,
            new_page,
            on_back=self._back_to_atelier,
        ).show()

    def _open_page_in_atelier(
        self,
        page: dict,
    ) -> None:

        self._open_page(
            page,
            return_to_atelier=True,
        )

    def _back_to_atelier(self) -> None:
        """Revient au Bureau de conception depuis l’éditeur."""

        self._show_atelier_home()

    def _clear_parent_widgets(self) -> None:

        for widget in self.parent.winfo_children():
            widget.destroy()

    def _open_page(
        self,
        page: dict,
        return_to_atelier: bool = False,
    ) -> None:
        """
        Ouvre directement la page sélectionnée dans le Bureau de conception.

        Le Centre du projet charge le document qui contient la page,
        puis affiche immédiatement cette page sans passer par une liste
        intermédiaire.
        """

        document_info = page.get(
            "_document_info"
        )

        if not isinstance(document_info, dict):
            return

        document_name = str(
            document_info.get("nom", "")
        ).strip()

        page_number = page.get(
            "numero"
        )

        if not document_name or page_number is None:
            return

        try:
            document = (
                self.application.document_manager.load_document(
                    document_name
                )
            )

            selected_page = document.get_page(
                int(page_number)
            )

            if selected_page is None:
                return

            PageEditorView(
                self.parent,
                selected_page,
                on_back=(
                    self._back_to_atelier
                    if return_to_atelier
                    else self._back_to_centre
                ),
            ).show()

        except (
            OSError,
            TypeError,
            ValueError,
            KeyError,
        ):
            return

    def _back_to_centre(self) -> None:
        """Revient au Centre du projet depuis le Bureau de conception."""

        if self.on_refresh is not None:
            self.on_refresh()

    def _open_page_from_list(
        self,
        page: dict,
        window: ctk.CTkToplevel,
    ) -> None:

        try:
            window.destroy()
        finally:
            self._open_page(page)

    # ==========================================================
    # Présentation des données
    # ==========================================================

    @classmethod
    def _appearance_for_type(
        cls,
        page_type: str,
    ) -> dict[str, str]:

        clean_type = (
            str(page_type).strip()
            or "Page vide"
        )

        known = PAGE_TYPE_APPEARANCES.get(
            clean_type
        )

        if known is not None:
            return dict(known)

        color_index = sum(
            ord(character)
            for character in clean_type
        ) % len(FALLBACK_EDITORIAL_COLORS)

        return {
            "icone": "📄",
            "couleur": FALLBACK_EDITORIAL_COLORS[
                color_index
            ],
        }

    def _page_appearance(
        self,
        page: dict,
    ) -> dict[str, str]:

        return self._appearance_for_type(
            self._page_type(page)
        )

    @classmethod
    def _hover_color(
        cls,
        color: str,
    ) -> str:

        return cls._blend_color(
            color,
            "#FFFFFF",
            0.22,
        )

    @classmethod
    def _darken_color(
        cls,
        color: str,
        amount: float = 0.12,
    ) -> str:

        return cls._blend_color(
            color,
            "#000000",
            amount,
        )

    @staticmethod
    def _blend_color(
        color: str,
        target: str,
        ratio: float,
    ) -> str:

        try:
            ratio = max(
                0.0,
                min(1.0, float(ratio)),
            )

            source_channels = [
                int(
                    color.lstrip("#")[index:index + 2],
                    16,
                )
                for index in (0, 2, 4)
            ]
            target_channels = [
                int(
                    target.lstrip("#")[index:index + 2],
                    16,
                )
                for index in (0, 2, 4)
            ]

            blended = [
                round(
                    source
                    + (destination - source) * ratio
                )
                for source, destination in zip(
                    source_channels,
                    target_channels,
                )
            ]

            return "#{}".format(
                "".join(
                    f"{channel:02X}"
                    for channel in blended
                )
            )
        except (
            TypeError,
            ValueError,
        ):
            return color

    def _project_summary(self) -> str:

        total = len(self.pages)

        if total == 0:
            return "Aucune page"

        states = Counter(
            self._page_state(page)
            for page in self.pages
        )

        details = [
            f"{total} page(s)",
        ]

        for state_name in (
            "Validée",
            "À vérifier",
            "Brouillon",
        ):
            count = states.get(
                state_name,
                0,
            )
            if count:
                details.append(
                    f"{count} {state_name.lower()}"
                )

        return "  ·  ".join(details)

    @classmethod
    def _status_color(
        cls,
        state: str,
    ) -> str:

        return cls.STATUS_COLORS.get(
            state.strip().casefold(),
            cls.ATELIER,
        )

    @staticmethod
    def _page_type(page: dict) -> str:

        value = str(
            page.get("type", "")
        ).strip()

        return value or "Sans catégorie"

    @staticmethod
    def _short_page_type(page_type: str) -> str:
        """Libellé compact affiché sous chaque vignette du chemin de fer."""

        labels = {
            "Page vide": "Vide",
            "Page de texte": "Texte",
            "Page image": "Image",
            "Page de chapitre": "Chapitre",
            "Couverture": "Couverture",
            "Page de transition": "Transition",
            "Table des matières": "Sommaire",
            "Page d’illustration": "Illustration",
            "Création libre": "Libre",
            "Modèle": "Modèle",
            "Sans catégorie": "Sans type",
        }

        clean_type = str(page_type or "").strip()
        return labels.get(clean_type, clean_type or "Sans type")

    @staticmethod
    def _page_state(page: dict) -> str:

        value = str(
            page.get("etat", "")
        ).strip()

        return value or "Brouillon"

    @staticmethod
    def _truncate(
        value: str,
        maximum: int,
    ) -> str:

        if len(value) <= maximum:
            return value

        return value[: maximum - 1].rstrip() + "…"

    @staticmethod
    def _date_sort_key(value: str) -> datetime:

        try:
            return datetime.fromisoformat(value)
        except (TypeError, ValueError):
            return datetime.min

    @classmethod
    def _format_date(cls, value: str) -> str:

        date_value = cls._date_sort_key(value)

        if date_value == datetime.min:
            return "date inconnue"

        return date_value.strftime(
            "%d/%m/%Y %H:%M"
        )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            "DocumentView("
            f"pages={len(self.pages)})"
        )