from __future__ import annotations

import json
import tkinter as tk
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Callable

import customtkinter as ctk

from src.theme.colors import Colors
from src.theme.fonts import Fonts
from src.theme.spacing import Spacing


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
                    workspace["color"]
                    if enabled
                    else workspace["soft"]
                ),
                text_color=workspace["color"],
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
        border_color = self._status_color(state)
        name = self._truncate(
            str(page.get("nom", "Page sans nom")),
            14,
        )
        page_type = self._truncate(
            self._page_type(page),
            13,
        )
        number = page.get("numero", index + 1)

        return ctk.CTkButton(
            parent,
            width=88,
            height=126,
            corner_radius=9,
            fg_color=self.CARD_BG,
            hover_color=self.ATELIER_SOFT,
            border_width=2,
            border_color=border_color,
            text_color=self.NAVY,
            font=(Fonts.FAMILY, 10),
            text=(
                f"{number}\n"
                f"{name}\n"
                f"{page_type}\n"
                f"{state}"
            ),
            command=lambda data=page: self._open_page(data),
        )

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

        return ctk.CTkButton(
            parent,
            height=34,
            corner_radius=8,
            fg_color="#F8FAFC",
            hover_color=self.ATELIER_SOFT,
            text_color=self.NAVY,
            font=Fonts.NORMAL,
            anchor="w",
            text=(
                f"{name}   ·   {page_type}   ·   "
                f"{state}   ·   {created}"
            ),
            command=lambda data=page: self._open_page(data),
        )

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
            color=self.NAVY,
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
                color=self.ATELIER,
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
        color: str,
    ) -> ctk.CTkButton:

        return ctk.CTkButton(
            parent,
            height=36,
            corner_radius=8,
            fg_color="#F8FAFC",
            hover_color=self.ATELIER_SOFT,
            text_color=color,
            font=Fonts.NORMAL,
            anchor="w",
            text=f"{label}                                      {count}",
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

            button = ctk.CTkButton(
                list_frame,
                height=52,
                corner_radius=10,
                fg_color=self.CARD_BG,
                hover_color=self.ATELIER_SOFT,
                border_width=1,
                border_color=self._status_color(state),
                text_color=self.NAVY,
                font=Fonts.NORMAL,
                anchor="w",
                text=(
                    f"{number:>3}   {name}\n"
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
            button.grid(
                row=row,
                column=0,
                sticky="ew",
                pady=(0, Spacing.XS),
            )

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

        documents = list(
            getattr(self.project, "documents", [])
        )

        if not documents:
            return

        if self.on_open_document is not None:
            self.on_open_document(
                documents[0]
            )

    def _open_page(self, page: dict) -> None:

        document_info = page.get(
            "_document_info"
        )

        if (
            document_info is not None
            and self.on_open_document is not None
        ):
            self.on_open_document(
                document_info
            )

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