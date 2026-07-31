from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

import customtkinter as ctk

from src.theme.colors import Colors
from src.theme.fonts import Fonts
from src.theme.spacing import Spacing


class DashboardView:
    """
    Écran d'accueil de PageMaître.

    Cet écran est volontairement limité aux actions utiles avant
    l'ouverture d'un projet : créer, ouvrir ou reprendre un travail récent.
    Les boutons utilisent les commandes existantes du menu « Fichier » afin
    qu'il n'existe qu'un seul fonctionnement dans l'application.
    """

    MAX_RECENT_PROJECTS = 5

    def __init__(
        self,
        parent,
        recent_projects: list[dict] | None = None,
        on_open_recent=None,
    ) -> None:

        self.parent = parent
        self.recent_projects = list(
            recent_projects or []
        )[: self.MAX_RECENT_PROJECTS]
        self.on_open_recent = on_open_recent

    # ==========================================================
    # Affichage
    # ==========================================================

    def show(self) -> None:

        container = ctk.CTkFrame(
            self.parent,
            fg_color="transparent",
        )
        container.pack(
            fill="both",
            expand=True,
            padx=Spacing.XXL,
            pady=Spacing.XL,
        )

        container.grid_columnconfigure(
            0,
            weight=1,
        )
        container.grid_rowconfigure(
            2,
            weight=1,
        )

        self._create_brand_block(
            container,
        ).grid(
            row=0,
            column=0,
            sticky="ew",
        )

        self._create_actions_block(
            container,
        ).grid(
            row=1,
            column=0,
            sticky="ew",
            pady=(Spacing.XL, Spacing.LG),
        )

        self._create_recent_projects_block(
            container,
        ).grid(
            row=2,
            column=0,
            sticky="nsew",
        )

    # ==========================================================
    # En-tête PageMaître
    # ==========================================================

    def _create_brand_block(
        self,
        parent,
    ) -> ctk.CTkFrame:

        block = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        ctk.CTkLabel(
            block,
            text="PageMaître",
            font=(Fonts.FAMILY, 38, "bold"),
            text_color=Colors.TEXT,
        ).pack(
            anchor="center",
        )

        ctk.CTkLabel(
            block,
            text=(
                "Créez, organisez et mettez en page vos livres "
                "dans un espace de travail unique."
            ),
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
            justify="center",
            wraplength=720,
        ).pack(
            anchor="center",
            pady=(Spacing.SM, 0),
        )

        return block

    # ==========================================================
    # Actions principales
    # ==========================================================

    def _create_actions_block(
        self,
        parent,
    ) -> ctk.CTkFrame:

        block = ctk.CTkFrame(
            parent,
            fg_color=Colors.CARD,
            corner_radius=18,
            border_width=1,
            border_color=Colors.BORDER,
        )

        block.grid_columnconfigure(
            (0, 1),
            weight=1,
            uniform="actions",
        )

        ctk.CTkLabel(
            block,
            text="Commencer",
            font=Fonts.H1,
            text_color=Colors.TEXT,
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            pady=(Spacing.LG, Spacing.MD),
        )

        self._create_action_card(
            block,
            title="Nouveau projet",
            description=(
                "Créer un livre à partir d’un modèle "
                "ou commencer une création libre."
            ),
            button_text="Créer un nouveau projet",
            command=lambda: self._invoke_file_command(
                "Nouveau projet"
            ),
            primary=True,
        ).grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(Spacing.LG, Spacing.SM),
            pady=(0, Spacing.LG),
        )

        self._create_action_card(
            block,
            title="Ouvrir un projet",
            description=(
                "Retrouver un projet en cours, terminé "
                "ou conservé sur cet ordinateur."
            ),
            button_text="Ouvrir un projet existant",
            command=lambda: self._invoke_file_command(
                "Ouvrir un projet"
            ),
            primary=False,
        ).grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(Spacing.SM, Spacing.LG),
            pady=(0, Spacing.LG),
        )

        return block

    def _create_action_card(
        self,
        parent,
        title: str,
        description: str,
        button_text: str,
        command,
        primary: bool,
    ) -> ctk.CTkFrame:

        card = ctk.CTkFrame(
            parent,
            fg_color=Colors.PANEL,
            corner_radius=14,
            border_width=1,
            border_color=Colors.BORDER,
        )

        card.grid_columnconfigure(
            0,
            weight=1,
        )
        card.grid_rowconfigure(
            1,
            weight=1,
        )

        ctk.CTkLabel(
            card,
            text=title,
            font=Fonts.H2,
            text_color=Colors.TEXT,
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=Spacing.LG,
            pady=(Spacing.LG, Spacing.SM),
        )

        ctk.CTkLabel(
            card,
            text=description,
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
            justify="left",
            anchor="nw",
            wraplength=360,
        ).grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=Spacing.LG,
        )

        button_options = {
            "text": button_text,
            "command": command,
            "height": 46,
            "corner_radius": 10,
            "font": Fonts.NORMAL,
        }

        if primary:
            button_options.update(
                {
                    "fg_color": Colors.PRIMARY,
                    "hover_color": Colors.PRIMARY_HOVER,
                    "text_color": "white",
                }
            )
        else:
            button_options.update(
                {
                    "fg_color": Colors.BUTTON,
                    "hover_color": Colors.BUTTON_HOVER,
                    "text_color": Colors.TEXT,
                    "border_width": 1,
                    "border_color": Colors.BORDER,
                }
            )

        ctk.CTkButton(
            card,
            **button_options,
        ).grid(
            row=2,
            column=0,
            sticky="ew",
            padx=Spacing.LG,
            pady=Spacing.LG,
        )

        return card

    # ==========================================================
    # Projets récents
    # ==========================================================

    def _create_recent_projects_block(
        self,
        parent,
    ) -> ctk.CTkFrame:

        block = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        block.grid_columnconfigure(
            0,
            weight=1,
        )

        ctk.CTkLabel(
            block,
            text="Projets récents",
            font=Fonts.H1,
            text_color=Colors.TEXT,
        ).grid(
            row=0,
            column=0,
            sticky="w",
            pady=(0, Spacing.MD),
        )

        if not self.recent_projects:
            self._create_empty_recent_state(
                block,
            ).grid(
                row=1,
                column=0,
                sticky="ew",
            )
            return block

        list_frame = ctk.CTkFrame(
            block,
            fg_color="transparent",
        )
        list_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
        )
        list_frame.grid_columnconfigure(
            0,
            weight=1,
        )

        for row, project in enumerate(
            self.recent_projects
        ):
            self._create_recent_project_card(
                list_frame,
                project,
            ).grid(
                row=row,
                column=0,
                sticky="ew",
                pady=(0, Spacing.SM),
            )

        return block

    def _create_empty_recent_state(
        self,
        parent,
    ) -> ctk.CTkFrame:

        empty = ctk.CTkFrame(
            parent,
            fg_color=Colors.CARD,
            corner_radius=14,
            border_width=1,
            border_color=Colors.BORDER,
        )

        ctk.CTkLabel(
            empty,
            text="Aucun projet récent",
            font=Fonts.H2,
            text_color=Colors.TEXT,
        ).pack(
            pady=(Spacing.LG, Spacing.XS),
        )

        ctk.CTkLabel(
            empty,
            text=(
                "Les derniers projets ouverts apparaîtront ici "
                "pour permettre un accès direct."
            ),
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
            justify="center",
            wraplength=620,
        ).pack(
            pady=(0, Spacing.LG),
            padx=Spacing.LG,
        )

        return empty

    def _create_recent_project_card(
        self,
        parent,
        project: dict,
    ) -> ctk.CTkButton:

        name = str(
            project.get("nom", "Projet sans nom")
        )
        status = str(
            project.get("statut", "En cours")
        )
        modified = str(
            project.get("date_modification", "")
        )

        details = status
        if modified:
            details += f" · Dernière ouverture : {modified}"

        return ctk.CTkButton(
            parent,
            text=f"{name}\n{details}",
            command=lambda data=project: self._open_recent_project(
                data
            ),
            height=62,
            corner_radius=12,
            fg_color=Colors.CARD,
            hover_color=Colors.PANEL,
            text_color=Colors.TEXT,
            font=Fonts.NORMAL,
            anchor="w",
            border_width=1,
            border_color=Colors.BORDER,
        )

    # ==========================================================
    # Commandes
    # ==========================================================

    def _invoke_file_command(
        self,
        command_label: str,
    ) -> None:

        try:
            root = self.parent.winfo_toplevel()
            menu_name = root.cget("menu")

            if not menu_name:
                raise RuntimeError(
                    "Le menu Fichier n’est pas disponible."
                )

            menu_bar = root.nametowidget(
                menu_name
            )
            file_menu = self._find_submenu(
                root,
                menu_bar,
                "Fichier",
            )

            if file_menu is None:
                raise RuntimeError(
                    "Le menu Fichier est introuvable."
                )

            command_index = self._find_entry_index(
                file_menu,
                command_label,
            )

            if command_index is None:
                raise RuntimeError(
                    f"La commande « {command_label} » est introuvable."
                )

            file_menu.invoke(
                command_index
            )

        except Exception as exc:
            messagebox.showerror(
                "Commande indisponible",
                str(exc),
                parent=self.parent.winfo_toplevel(),
            )

    def _open_recent_project(
        self,
        project: dict,
    ) -> None:

        if self.on_open_recent is None:
            return

        self.on_open_recent(
            project
        )

    # ==========================================================
    # Utilitaires Tk
    # ==========================================================

    @staticmethod
    def _find_submenu(
        root,
        menu_bar: tk.Menu,
        label: str,
    ) -> tk.Menu | None:

        index_end = menu_bar.index("end")
        if index_end is None:
            return None

        for index in range(index_end + 1):
            try:
                if menu_bar.type(index) != "cascade":
                    continue

                if menu_bar.entrycget(index, "label") != label:
                    continue

                submenu_name = menu_bar.entrycget(
                    index,
                    "menu",
                )
                return root.nametowidget(
                    submenu_name
                )
            except tk.TclError:
                continue

        return None

    @staticmethod
    def _find_entry_index(
        menu: tk.Menu,
        label: str,
    ) -> int | None:

        index_end = menu.index("end")
        if index_end is None:
            return None

        for index in range(index_end + 1):
            try:
                if menu.type(index) != "command":
                    continue

                if menu.entrycget(index, "label") == label:
                    return index
            except tk.TclError:
                continue

        return None

    def __repr__(self) -> str:

        return (
            "DashboardView("
            f"recent_projects={len(self.recent_projects)})"
        )