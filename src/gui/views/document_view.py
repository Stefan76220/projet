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

from src.gui.views.page_editor_view import PageEditorView
from src.library.page_types.page_type_library import PageTypeLibrary
from src.theme.colors import Colors
from src.theme.fonts import Fonts
from src.theme.spacing import Spacing


# Apparence éditoriale commune à l'Atelier et au Centre du projet.
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

    La vue présente en priorité le chemin de fer du livre, les quatre espaces
    de travail, les cinq dernières pages créées et l'accès aux listes
    complètes par type de page.

    Aucun élément n'est créé depuis cette vue : la création reste propre
    à chaque espace de travail.
    """

    NAVY = "#17365D"
    WINDOW_BG = "#F5F7FA"
    CARD_BG = "#FFFFFF"
    BORDER = "#DCE3EA"
    TEXT_MUTED = "#667085"
    TEXT_LIGHT = "#98A2B3"

    ATELIER = "#2F80ED"
    ATELIER_SOFT = "#EAF3FF"

    PRODUCTION = "#34A853"
    PRODUCTION_SOFT = "#EAF7EE"

    COMPOSITION = "#7B61D1"
    COMPOSITION_SOFT = "#F1ECFF"

    FINALISATION = "#F2994A"
    FINALISATION_SOFT = "#FFF1E4"

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

    ATELIER_CREATION_TYPES = (
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
        {
            "type": "Modèle",
            "title": "Modèle",
            "description": "Concevoir une base réutilisable pour d’autres pages.",
        },
    )

    WORKSPACES = (
        {
            "title": "Atelier de conception",
            "short": "Modèles et pages libres",
            "color": ATELIER,
            "soft": ATELIER_SOFT,
            "enabled": True,
        },
        {
            "title": "Production structurée",
            "short": "Fiches et contenus répétitifs",
            "color": PRODUCTION,
            "soft": PRODUCTION_SOFT,
            "enabled": False,
        },
        {
            "title": "Composition textuelle",
            "short": "Chapitres et textes longs",
            "color": COMPOSITION,
            "soft": COMPOSITION_SOFT,
            "enabled": False,
        },
        {
            "title": "Finalisation et export",
            "short": "Contrôle et publication",
            "color": FINALISATION,
            "soft": FINALISATION_SOFT,
            "enabled": False,
        },
    )

    def __init__(
        self,
        parent,
        project,
        application,
        on_open_document=None,
        on_refresh=None,
    ) -> None:

        self.parent = parent
        self.project = project
        self.application = application
        self.on_open_document = on_open_document
        self.on_refresh = on_refresh

        self.pages: list[dict] = []
        self._rail_canvas: tk.Canvas | None = None
        self._rail_inner: ctk.CTkFrame | None = None
        self._rail_cards: list[ctk.CTkButton] = []

        self.page_type_library = PageTypeLibrary()
        self.page_type_library.load()

    # ==========================================================
    # Affichage
    # ==========================================================

    def show(self) -> None:

        self.pages = self._load_project_pages()

        root = ctk.CTkFrame(
            self.parent,
            fg_color=self.WINDOW_BG,
            corner_radius=0,
        )
        root.pack(fill="both", expand=True)

        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(2, weight=1)
        root.grid_rowconfigure(3, weight=1)

        self._create_header(root).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=Spacing.XL,
            pady=(Spacing.MD, Spacing.SM),
        )

        self._create_workspace_bar(root).grid(
            row=1,
            column=0,
            sticky="ew",
            padx=Spacing.XL,
            pady=(0, Spacing.SM),
        )

        self._create_rail_section(root).grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=Spacing.XL,
            pady=(0, Spacing.SM),
        )

        self._create_bottom_section(root).grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=Spacing.XL,
            pady=(0, Spacing.MD),
        )

    # ==========================================================
    # En-tête
    # ==========================================================

    def _create_header(self, parent) -> ctk.CTkFrame:

        frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )
        frame.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            frame,
            text="← Accueil",
            width=112,
            height=38,
            corner_radius=10,
            fg_color=self.CARD_BG,
            hover_color="#E9EEF4",
            text_color=self.NAVY,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.NORMAL,
            command=self._return_home,
        ).grid(
            row=0,
            column=0,
            rowspan=2,
            sticky="w",
            padx=(0, Spacing.MD),
        )

        project_name = str(
            getattr(self.project, "name", "")
            or "Projet sans nom"
        )

        title_area = ctk.CTkFrame(
            frame,
            fg_color="transparent",
        )
        title_area.grid(
            row=0,
            column=1,
            rowspan=2,
            sticky="w",
        )

        ctk.CTkLabel(
            title_area,
            text="Centre du projet",
            font=Fonts.TITLE,
            text_color=self.NAVY,
        ).pack(
            anchor="w",
        )

        ctk.CTkLabel(
            title_area,
            text=project_name,
            font=Fonts.H2,
            text_color=self.TEXT_MUTED,
        ).pack(
            anchor="w",
            pady=(0, 2),
        )

        ctk.CTkLabel(
            frame,
            text=self._project_summary(),
            font=Fonts.NORMAL,
            text_color=self.TEXT_MUTED,
        ).grid(
            row=0,
            column=2,
            rowspan=2,
            sticky="e",
        )

        return frame

    # ==========================================================
    # Espaces de travail
    # ==========================================================

    def _create_workspace_bar(self, parent) -> ctk.CTkFrame:

        bar = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        for column in range(4):
            bar.grid_columnconfigure(
                column,
                weight=1,
                uniform="workspaces",
            )

        for column, workspace in enumerate(self.WORKSPACES):

            enabled = bool(
                workspace["enabled"]
                and getattr(self.project, "documents", [])
            )

            button = ctk.CTkButton(
                bar,
                text=(
                    f"{workspace['title']}\n"
                    f"{workspace['short']}"
                ),
                height=62,
                corner_radius=12,
                fg_color=workspace["soft"],
                hover_color=(
                    self._darken_color(
                        workspace["soft"],
                        amount=0.08,
                    )
                    if enabled
                    else workspace["soft"]
                ),
                text_color=self.NAVY,
                border_width=1,
                border_color=workspace["color"],
                font=Fonts.NORMAL,
                command=(
                    self._open_atelier
                    if workspace["title"] == "Atelier de conception"
                    else None
                ),
                state="normal" if enabled else "disabled",
            )
            button.grid(
                row=0,
                column=column,
                sticky="ew",
                padx=(
                    (0, Spacing.XS)
                    if column == 0
                    else (
                        (Spacing.XS, 0)
                        if column == 3
                        else (Spacing.XS, Spacing.XS)
                    )
                ),
            )

        return bar

    # ==========================================================
    # Chemin de fer
    # ==========================================================

    def _create_rail_section(self, parent) -> ctk.CTkFrame:

        section = ctk.CTkFrame(
            parent,
            fg_color=self.CARD_BG,
            corner_radius=16,
            border_width=1,
            border_color=self.BORDER,
        )
        section.grid_columnconfigure(0, weight=1)
        section.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(
            section,
            fg_color="transparent",
        )
        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=Spacing.LG,
            pady=(Spacing.SM, Spacing.XS),
        )
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Chemin de fer",
            font=Fonts.H1,
            text_color=self.NAVY,
        ).grid(
            row=0,
            column=0,
            sticky="w",
        )

        ctk.CTkLabel(
            header,
            text=(
                "Vue immédiate de l’ordre actuel du livre"
                if self.pages
                else "Aucune page n’est encore enregistrée"
            ),
            font=Fonts.NORMAL,
            text_color=self.TEXT_MUTED,
        ).grid(
            row=0,
            column=1,
            sticky="e",
        )

        rail_host = ctk.CTkFrame(
            section,
            fg_color="#F8FAFC",
            corner_radius=12,
        )
        rail_host.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=Spacing.LG,
            pady=(Spacing.XS, Spacing.SM),
        )
        rail_host.grid_columnconfigure(0, weight=1)
        rail_host.grid_rowconfigure(0, weight=1)

        self._rail_canvas = tk.Canvas(
            rail_host,
            background="#F8FAFC",
            highlightthickness=0,
            height=162,
        )
        self._rail_canvas.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        scrollbar = ctk.CTkScrollbar(
            rail_host,
            orientation="horizontal",
            command=self._rail_canvas.xview,
            height=12,
        )
        scrollbar.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=Spacing.SM,
            pady=(0, Spacing.XS),
        )

        self._rail_canvas.configure(
            xscrollcommand=scrollbar.set,
        )

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
                width=380,
                height=128,
                fg_color=self.CARD_BG,
                corner_radius=12,
                border_width=1,
                border_color=self.BORDER,
            )
            empty.pack(
                side="left",
                padx=Spacing.MD,
                pady=Spacing.SM,
            )
            empty.pack_propagate(False)

            ctk.CTkLabel(
                empty,
                text="Le chemin de fer apparaîtra ici",
                font=Fonts.H2,
                text_color=self.NAVY,
            ).pack(
                pady=(Spacing.MD, Spacing.XS),
            )

            ctk.CTkLabel(
                empty,
                text=(
                    "Les pages créées dans les espaces de travail "
                    "seront présentées dans leur ordre actuel."
                ),
                font=Fonts.NORMAL,
                text_color=self.TEXT_MUTED,
                justify="center",
                wraplength=330,
            ).pack(
                padx=Spacing.MD,
            )
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
                padx=(
                    (6, 3)
                    if index == 0
                    else (3, 3)
                ),
                pady=Spacing.SM,
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
        name = self._truncate(
            str(page.get("nom", "Page sans nom")),
            14,
        )
        page_type = self._truncate(
            self._page_type(page),
            13,
        )
        number = page.get("numero", index + 1)

        button = ctk.CTkButton(
            parent,
            width=88,
            height=126,
            corner_radius=9,
            fg_color=appearance["couleur"],
            hover_color=self._hover_color(
                appearance["couleur"]
            ),
            border_width=2,
            border_color=self._status_color(state),
            text_color=self.NAVY,
            font=(Fonts.FAMILY, 10),
            text=(
                f"{appearance['icone']}  {number}\n"
                f"{name}\n"
                f"{page_type}\n"
                f"{state}"
            ),
            command=lambda data=page: self._open_page(data),
        )

        self._bind_page_context(
            button,
            page,
        )

        return button

    def _on_rail_canvas_configure(
        self,
        window_id: int,
        width: int,
        height: int,
    ) -> None:

        self._keep_rail_height(
            window_id,
            height,
        )
        self._resize_rail_cards(
            width,
        )

    def _resize_rail_cards(
        self,
        canvas_width: int,
    ) -> None:
        """
        Adapte partiellement la largeur des vignettes.

        Sur un écran de portable, l'objectif est de présenter au moins
        dix pages avant de devoir utiliser le défilement horizontal.
        Sur un écran plus large, la largeur maximale reste limitée afin
        d'en afficher davantage.
        """

        if not self._rail_cards:
            return

        target_visible = 10
        horizontal_gaps = 12 + (target_visible * 6)
        available_width = max(
            canvas_width - horizontal_gaps,
            target_visible * 74,
        )

        card_width = available_width // target_visible
        card_width = max(
            74,
            min(96, card_width),
        )

        for card in self._rail_cards:
            card.configure(
                width=card_width,
            )

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
            height=max(height, 142),
        )

    # ==========================================================
    # Zone inférieure
    # ==========================================================

    def _create_bottom_section(self, parent) -> ctk.CTkFrame:

        container = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )
        container.grid_columnconfigure(
            (0, 1),
            weight=1,
            uniform="bottom",
        )
        container.grid_rowconfigure(0, weight=1)

        self._create_recent_pages(container).grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, Spacing.XS),
        )

        self._create_categories(container).grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(Spacing.XS, 0),
        )

        return container

    # ==========================================================
    # Dernières pages créées
    # ==========================================================

    def _create_recent_pages(self, parent) -> ctk.CTkFrame:

        card = ctk.CTkFrame(
            parent,
            fg_color=self.CARD_BG,
            corner_radius=16,
            border_width=1,
            border_color=self.BORDER,
        )
        card.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            card,
            text="5 dernières pages créées",
            font=Fonts.H1,
            text_color=self.NAVY,
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=Spacing.LG,
            pady=(Spacing.MD, Spacing.SM),
        )

        recent_pages = sorted(
            self.pages,
            key=lambda page: self._date_sort_key(
                page.get("date_creation", "")
            ),
            reverse=True,
        )[:5]

        if not recent_pages:

            ctk.CTkLabel(
                card,
                text="Aucune page créée.",
                font=Fonts.NORMAL,
                text_color=self.TEXT_MUTED,
            ).grid(
                row=1,
                column=0,
                sticky="w",
                padx=Spacing.LG,
                pady=(0, Spacing.LG),
            )
            return card

        for row, page in enumerate(
            recent_pages,
            start=1,
        ):
            self._create_recent_row(
                card,
                page,
            ).grid(
                row=row,
                column=0,
                sticky="ew",
                padx=Spacing.LG,
                pady=(0, 4),
            )

        card.grid_rowconfigure(
            len(recent_pages) + 1,
            weight=1,
        )

        return card

    def _create_recent_row(
        self,
        parent,
        page: dict,
    ) -> ctk.CTkButton:

        name = self._truncate(
            str(page.get("nom", "Page sans nom")),
            34,
        )
        page_type = self._page_type(page)
        state = self._page_state(page)
        created = self._format_date(
            page.get("date_creation", "")
        )
        appearance = self._page_appearance(page)

        button = ctk.CTkButton(
            parent,
            height=34,
            corner_radius=8,
            fg_color=appearance["couleur"],
            hover_color=self._hover_color(
                appearance["couleur"]
            ),
            text_color=self.NAVY,
            border_width=1,
            border_color=self._status_color(state),
            font=Fonts.NORMAL,
            anchor="w",
            text=(
                f"{appearance['icone']}  {name}   ·   "
                f"{page_type}   ·   {state}   ·   {created}"
            ),
            command=lambda data=page: self._open_page(data),
        )

        self._bind_page_context(
            button,
            page,
        )

        return button

    # ==========================================================
    # Catégories et listes complètes
    # ==========================================================

    def _create_categories(self, parent) -> ctk.CTkFrame:

        card = ctk.CTkFrame(
            parent,
            fg_color=self.CARD_BG,
            corner_radius=16,
            border_width=1,
            border_color=self.BORDER,
        )
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(1, weight=1)

        title_row = ctk.CTkFrame(
            card,
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
            text="Pages du projet",
            font=Fonts.H1,
            text_color=self.NAVY,
        ).grid(
            row=0,
            column=0,
            sticky="w",
        )

        ctk.CTkLabel(
            title_row,
            text="Cliquer pour afficher la liste complète",
            font=Fonts.NORMAL,
            text_color=self.TEXT_MUTED,
        ).grid(
            row=0,
            column=1,
            sticky="e",
        )

        list_frame = ctk.CTkScrollableFrame(
            card,
            fg_color="transparent",
            corner_radius=0,
        )
        list_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=Spacing.MD,
            pady=(0, Spacing.MD),
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
            background="#E8EDF3",
            icon="☷",
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 4),
        )

        type_counts = Counter(
            self._page_type(page)
            for page in self.pages
        )

        for row, (page_type, count) in enumerate(
            sorted(
                type_counts.items(),
                key=lambda item: (
                    -item[1],
                    item[0].casefold(),
                ),
            ),
            start=1,
        ):

            matching_pages = [
                page
                for page in self.pages
                if self._page_type(page) == page_type
            ]
            appearance = self._appearance_for_type(
                page_type
            )

            self._create_category_row(
                list_frame,
                label=page_type,
                count=count,
                command=lambda title=page_type, pages=matching_pages: (
                    self._show_page_list(
                        title,
                        pages,
                    )
                ),
                background=appearance["couleur"],
                icon=appearance["icone"],
            ).grid(
                row=row,
                column=0,
                sticky="ew",
                pady=(0, 4),
            )

        return card

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
            height=36,
            corner_radius=8,
            fg_color=background,
            hover_color=self._hover_color(
                background
            ),
            text_color=self.NAVY,
            border_width=1,
            border_color=self._darken_color(
                background,
                amount=0.14,
            ),
            font=Fonts.NORMAL,
            anchor="w",
            text=(
                f"{icon}  {label}"
                f"                                      {count}"
            ),
            command=command,
        )

    def _show_page_list(
        self,
        title: str,
        pages: list[dict],
    ) -> None:

        window = ctk.CTkToplevel(
            self.parent,
        )
        window.title(f"{title} — PageMaître")
        window.geometry("900x560")
        window.minsize(720, 440)
        window.transient(
            self.parent.winfo_toplevel()
        )

        window.grid_columnconfigure(0, weight=1)
        window.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(
            window,
            fg_color=self.WINDOW_BG,
            corner_radius=0,
        )
        header.grid(
            row=0,
            column=0,
            sticky="ew",
        )
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text=title,
            font=Fonts.TITLE,
            text_color=self.NAVY,
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=Spacing.XL,
            pady=(Spacing.LG, 0),
        )

        ctk.CTkLabel(
            header,
            text=f"{len(pages)} page(s)",
            font=Fonts.NORMAL,
            text_color=self.TEXT_MUTED,
        ).grid(
            row=1,
            column=0,
            sticky="w",
            padx=Spacing.XL,
            pady=(0, Spacing.LG),
        )

        list_frame = ctk.CTkScrollableFrame(
            window,
            fg_color=self.WINDOW_BG,
            corner_radius=0,
        )
        list_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=Spacing.LG,
            pady=(0, Spacing.LG),
        )
        list_frame.grid_columnconfigure(0, weight=1)

        if not pages:

            ctk.CTkLabel(
                list_frame,
                text="Aucune page dans cette catégorie.",
                font=Fonts.NORMAL,
                text_color=self.TEXT_MUTED,
            ).grid(
                row=0,
                column=0,
                sticky="w",
                padx=Spacing.MD,
                pady=Spacing.MD,
            )
            return

        for row, page in enumerate(pages):

            name = str(
                page.get("nom", "Page sans nom")
            )
            number = page.get("numero", row + 1)
            page_type = self._page_type(page)
            state = self._page_state(page)
            created = self._format_date(
                page.get("date_creation", "")
            )
            document_name = str(
                page.get("_document_name", "")
            )

            appearance = self._page_appearance(page)

            button = ctk.CTkButton(
                list_frame,
                height=52,
                corner_radius=10,
                fg_color=appearance["couleur"],
                hover_color=self._hover_color(
                    appearance["couleur"]
                ),
                border_width=1,
                border_color=self._status_color(state),
                text_color=self.NAVY,
                font=Fonts.NORMAL,
                anchor="w",
                text=(
                    f"{appearance['icone']}  {number:>3}   {name}\n"
                    f"      {page_type}  ·  {state}"
                    f"  ·  créée le {created}"
                    f"  ·  {document_name}"
                ),
                command=lambda data=page, dialog=window: (
                    self._open_page_from_list(
                        data,
                        dialog,
                    )
                ),
            )

            self._bind_page_context(
                button,
                page,
                owner_window=window,
            )
            button.grid(
                row=row,
                column=0,
                sticky="ew",
                pady=(0, Spacing.XS),
            )

    # ==========================================================
    # Menu contextuel et gestion des pages
    # ==========================================================

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
            label="Ouvrir dans l’Atelier",
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
                    "Déverrouille la page dans l’Atelier "
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
                    "Déverrouille la page dans l’Atelier "
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
                    "Déverrouille la page dans l’Atelier "
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

    def _open_atelier(self) -> None:
        """Ouvre l’accueil fonctionnel de l’Atelier de conception."""

        self._show_atelier_home()

    def _show_atelier_home(self) -> None:
        """
        Présente les créations disponibles dans l’Atelier sans exposer
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
            text="Atelier de conception",
            font=Fonts.TITLE,
            text_color=self.ATELIER,
        ).grid(
            row=0,
            column=1,
            sticky="w",
        )

        ctk.CTkLabel(
            header,
            text=(
                "Créer une page, un modèle ou un élément éditorial libre"
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
            text="Créer dans l’Atelier",
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
            self.ATELIER_CREATION_TYPES
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
            text="Les cinq dernières créations de l’Atelier",
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
                    "Aucune création pour le moment. "
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
        """Crée une page dans le conteneur interne puis ouvre l’éditeur."""

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
        """Revient à l’accueil de l’Atelier depuis l’éditeur."""

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
        Ouvre directement la page sélectionnée dans l'Atelier.

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
        """Revient au Centre du projet depuis l'Atelier."""

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