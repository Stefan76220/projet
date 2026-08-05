from __future__ import annotations

import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox
from typing import Callable

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageTk

from src.theme.fonts import Fonts


class DashboardView:
    """Accueil PageMaître : entrée de l'atelier éditorial."""

    MAX_RECENT_PROJECTS = 5
    CONTENT_PAD_X = 150

    WINDOW_BG = "#FBFAF7"
    GROUP_BG = "#FFFFFF"
    PANEL_BG = "#F7F8F9"
    BORDER = "#D7DCE1"
    INK = "#263E63"
    MUTED = "#687386"
    TEXT_LIGHT = "#9298A1"

    SKY = "#75B6DB"
    SKY_SOFT = "#E5F1F7"
    CELADON = "#82B7A1"
    CELADON_SOFT = "#E5F1EB"
    LILAC = "#A997C9"
    LILAC_SOFT = "#EEE8F5"
    CORAL = "#DF806B"
    CORAL_SOFT = "#F7E8E3"
    YELLOW = "#D8B85A"
    YELLOW_SOFT = "#F7EFD7"

    CREATE_CARD_BG = "#F7FCFA"
    OPEN_CARD_BG = "#FBF8FD"

    STATUS_STYLES = {
        "En cours": (CELADON, CELADON_SOFT),
        "À vérifier": (CORAL, CORAL_SOFT),
        "Validé": (SKY, SKY_SOFT),
        "Prêt à clôturer": (YELLOW, YELLOW_SOFT),
        "Clôturé": (LILAC, LILAC_SOFT),
    }

    WORKSPACE_TILES = (
        (
            "maquettage",
            "▤",
            "Maquettage",
            "Organiser les pages",
            SKY,
            SKY_SOFT,
        ),
        (
            "atelier",
            "▦",
            "Atelier",
            "Préparer les gabarits",
            CELADON,
            CELADON_SOFT,
        ),
        (
            "conception",
            "✎",
            "Conception",
            "Créer les pages",
            LILAC,
            LILAC_SOFT,
        ),
        (
            "centre",
            "⌂",
            "Centre du projet",
            "Vue d'ensemble",
            CORAL,
            CORAL_SOFT,
        ),
    )

    def __init__(
        self,
        parent,
        recent_projects: list[dict] | None = None,
        active_project: dict | None = None,
        on_open_recent=None,
        on_open_workspace=None,
    ) -> None:
        self.parent = parent
        self.recent_projects = list(
            recent_projects or []
        )[: self.MAX_RECENT_PROJECTS]
        self.active_project = active_project
        if self.active_project is None and self.recent_projects:
            self.active_project = self.recent_projects[0]

        self.on_open_recent = on_open_recent
        self.on_open_workspace = on_open_workspace
        self._images: dict[str, ctk.CTkImage] = {}
        self._home_root: ctk.CTkFrame | None = None
        self._stored_menu_name = ""
        self._stored_menu_widget: tk.Menu | None = None
        self._menu_hidden = False

        self._canvas: tk.Canvas | None = None
        self._canvas_background_id: int | None = None
        self._canvas_background_image: ImageTk.PhotoImage | None = None
        self._background_source: Image.Image | None = None
        self._layout_job: str | None = None
        self._window_ids: dict[str, int] = {}
        self._content_widgets: dict[str, tk.Widget] = {}

    # ==========================================================
    # Affichage
    # ==========================================================

    def show(self) -> None:
        root = ctk.CTkFrame(
            self.parent,
            fg_color=self.WINDOW_BG,
            corner_radius=0,
        )
        self._home_root = root
        self._hide_application_menu()
        root.bind("<Destroy>", self._on_home_destroy, add="+")

        canvas = tk.Canvas(
            root,
            background=self.WINDOW_BG,
            borderwidth=0,
            highlightthickness=0,
            relief="flat",
        )
        canvas.pack(fill="both", expand=True)
        self._canvas = canvas
        self._background_source = self._load_background_source()

        header = self._create_header(canvas)
        create = self._create_entry_card(
            canvas,
            title="Créer un nouveau projet",
            description=(
                "Démarrez un projet éditorial depuis une page blanche "
                "et construisez son espace de travail."
            ),
            button_label="Créer",
            command=lambda: self._invoke_file_command("Nouveau projet"),
            accent=self.CELADON,
            soft=self.CELADON_SOFT,
            background=self.CREATE_CARD_BG,
            illustration="accueil_creation.png",
            command_icon="＋",
        )
        open_project = self._create_entry_card(
            canvas,
            title="Ouvrir un projet",
            description=(
                "Accédez à un projet existant, même s'il ne figure pas "
                "encore parmi les projets récents."
            ),
            button_label="Ouvrir",
            command=lambda: self._invoke_file_command("Ouvrir un projet"),
            accent=self.LILAC,
            soft=self.LILAC_SOFT,
            background=self.OPEN_CARD_BG,
            illustration="accueil_ouverture.png",
            command_icon="⌂",
        )
        recent = self._create_recent_panel(canvas)
        active = self._create_active_project_panel(canvas)

        self._content_widgets = {
            "header": header,
            "create": create,
            "open": open_project,
            "recent": recent,
            "active": active,
        }
        for key, widget in self._content_widgets.items():
            self._window_ids[key] = canvas.create_window(
                0,
                0,
                window=widget,
                anchor="nw",
            )

        canvas.bind("<Configure>", self._schedule_layout, add="+")
        root.pack(fill="both", expand=True)
        root.update_idletasks()
        self._layout_now()

        # Le menu peut être créé après l'accueil : on le retire aussi
        # après les premiers cycles d'affichage.
        root.after_idle(self._hide_application_menu)
        root.after(120, self._hide_application_menu)
        root.after(400, self._hide_application_menu)

    def _create_header(self, parent) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(
            parent,
            fg_color=self.WINDOW_BG,
            corner_radius=0,
        )
        frame.grid_columnconfigure(1, weight=1)

        logo_label = ctk.CTkLabel(
            frame,
            text="",
            width=352,
            height=102,
            anchor="w",
            fg_color=self.WINDOW_BG,
        )
        logo_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=(18, 26),
            pady=5,
        )
        self._set_official_logo(logo_label)

        welcome = ctk.CTkFrame(
            frame,
            fg_color=self.WINDOW_BG,
            corner_radius=0,
        )
        welcome.grid(
            row=0,
            column=1,
            sticky="w",
            padx=(0, 20),
            pady=13,
        )

        ctk.CTkLabel(
            welcome,
            text="Bienvenue dans votre atelier éditorial",
            font=(Fonts.FAMILY, 22, "bold"),
            text_color=self.INK,
            anchor="w",
            fg_color=self.WINDOW_BG,
        ).pack(anchor="w")

        baseline = ctk.CTkFrame(
            welcome,
            fg_color=self.WINDOW_BG,
            corner_radius=0,
        )
        baseline.pack(anchor="w", pady=(3, 0))

        for text, color in (
            ("Concevez,", self.CELADON),
            (" organisez,", self.LILAC),
            (" publiez", self.CORAL),
        ):
            ctk.CTkLabel(
                baseline,
                text=text,
                font=(Fonts.FAMILY, 14, "bold"),
                text_color=color,
                fg_color=self.WINDOW_BG,
            ).pack(side="left")

        ctk.CTkLabel(
            welcome,
            text=(
                "Commencez un ouvrage, reprenez votre dernier projet "
                "ou rejoignez directement le bureau dont vous avez besoin."
            ),
            font=(Fonts.FAMILY, 9),
            text_color=self.MUTED,
            anchor="w",
            justify="left",
            wraplength=610,
            fg_color=self.WINDOW_BG,
        ).pack(anchor="w", pady=(7, 0))

        self._create_decorative_rule(welcome).pack(
            anchor="w",
            pady=(10, 0),
        )

        ctk.CTkButton(
            frame,
            text="Fermer  ×",
            command=self._close_application,
            width=84,
            height=30,
            corner_radius=15,
            fg_color="#E6E9ED",
            hover_color="#D7DCE2",
            text_color="#44505E",
            border_width=1,
            border_color="#CBD2DA",
            font=(Fonts.FAMILY, 8, "bold"),
        ).grid(
            row=0,
            column=2,
            sticky="ne",
            padx=(12, 18),
            pady=(10, 0),
        )

        return frame

    def _create_decorative_rule(self, parent) -> ctk.CTkFrame:
        line = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            height=8,
            width=470,
        )
        line.pack_propagate(False)

        for color, width in (
            (self.BORDER, 62),
            (self.CELADON, 42),
            (self.SKY, 32),
            (self.LILAC, 42),
            (self.BORDER, 58),
            (self.CORAL, 25),
            (self.BORDER, 54),
        ):
            ctk.CTkFrame(
                line,
                width=width,
                height=2,
                corner_radius=1,
                fg_color=color,
            ).pack(side="left", padx=(0, 6), pady=3)

        ctk.CTkLabel(
            line,
            text="▱",
            width=25,
            text_color=self.MUTED,
            font=(Fonts.FAMILY, 12),
        ).pack(side="left", padx=(0, 6))

        return line

    def _set_official_logo(self, label: ctk.CTkLabel) -> None:
        # Le format 360 × 108 respecte exactement le ratio 10:3
        # du logo officiel ; aucune déformation n'est appliquée.
        image = self._asset_image(
            "pagemaitre_logo_officiel.png",
            size=(330, 99),
        )
        if image is None:
            label.configure(
                text="PageMaître",
                font=(Fonts.FAMILY, 30, "bold"),
                text_color=self.INK,
            )
            return

        label.configure(image=image, text="")

    # ==========================================================
    # Créer / ouvrir
    # ==========================================================

    def _create_entry_card(
        self,
        parent,
        *,
        title: str,
        description: str,
        button_label: str,
        command: Callable[[], None],
        accent: str,
        soft: str,
        background: str,
        illustration: str,
        command_icon: str,
    ) -> ctk.CTkFrame:
        # Le fond arrondi est dessiné dans l'image générale. Ce cadre ne
        # contient que le contenu et reste largement à l'intérieur des coins.
        content = ctk.CTkFrame(
            parent,
            fg_color=background,
            corner_radius=0,
        )
        content.grid_columnconfigure(1, weight=1)

        image = self._asset_image(
            illustration,
            size=(176, 132),
        )
        if image is not None:
            ctk.CTkLabel(
                content,
                text="",
                image=image,
                fg_color=background,
                width=186,
                height=144,
            ).grid(
                row=0,
                column=0,
                rowspan=2,
                padx=(2, 8),
                pady=0,
            )
        else:
            ctk.CTkLabel(
                content,
                text=command_icon,
                width=136,
                height=128,
                corner_radius=15,
                fg_color=soft,
                text_color=accent,
                font=(Fonts.FAMILY, 42, "bold"),
            ).grid(
                row=0,
                column=0,
                rowspan=2,
                padx=(2, 14),
                pady=4,
            )

        text_area = ctk.CTkFrame(
            content,
            fg_color=background,
            corner_radius=0,
        )
        text_area.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(2, 6),
            pady=(4, 0),
        )

        ctk.CTkLabel(
            text_area,
            text=title,
            font=(Fonts.FAMILY, 16, "bold"),
            text_color=accent,
            anchor="w",
            fg_color=background,
        ).pack(anchor="w")

        ctk.CTkFrame(
            text_area,
            width=52,
            height=2,
            corner_radius=1,
            fg_color=accent,
        ).pack(anchor="w", pady=(7, 8))

        ctk.CTkLabel(
            text_area,
            text=description,
            font=(Fonts.FAMILY, 10),
            text_color=self.MUTED,
            justify="left",
            anchor="w",
            wraplength=285,
            fg_color=background,
        ).pack(anchor="w")

        self._create_square_command(
            text_area,
            icon=command_icon,
            label=button_label,
            command=command,
            accent=accent,
            soft=soft,
            size=50,
        ).pack(anchor="w", pady=(10, 0))

        return content

    def _create_recent_panel(self, parent) -> ctk.CTkFrame:
        panel = ctk.CTkFrame(
            parent,
            fg_color=self.GROUP_BG,
            corner_radius=0,
        )
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        self._create_panel_heading(
            panel,
            icon="◷",
            title="Reprendre votre travail",
            subtitle="Dernier projet actif et projets ouverts récemment.",
            accent=self.CELADON,
            soft=self.CELADON_SOFT,
            count=len(self.recent_projects),
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=2,
            pady=(0, 6),
        )

        body = ctk.CTkFrame(
            panel,
            fg_color=self.GROUP_BG,
            corner_radius=0,
        )
        body.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=0,
            pady=(0, 0),
        )
        body.grid_columnconfigure(0, weight=1)

        if not self.recent_projects:
            self._create_empty_recent(body).grid(
                row=0,
                column=0,
                sticky="ew",
            )
            return panel

        self._create_featured_project(
            body,
            self.recent_projects[0],
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            pady=(0, 6),
        )

        others = self.recent_projects[1:4]
        if others:
            for index, project in enumerate(others, start=1):
                self._create_recent_row(body, project).grid(
                    row=index,
                    column=0,
                    sticky="ew",
                    pady=(0, 5),
                )
        else:
            self._create_no_other_recent(body).grid(
                row=1,
                column=0,
                sticky="ew",
            )

        return panel

    def _create_featured_project(
        self,
        parent,
        project: dict,
    ) -> ctk.CTkFrame:
        status = self._status(project)
        accent, soft = self.STATUS_STYLES.get(
            status,
            (self.CELADON, self.CELADON_SOFT),
        )

        card = ctk.CTkFrame(
            parent,
            height=98,
            fg_color="#FBFEFD",
            corner_radius=9,
            border_width=1,
            border_color=accent,
        )
        card.grid_propagate(False)
        card.grid_columnconfigure(1, weight=1)

        thumbnail = self._asset_image(
            "accueil_projet.png",
            size=(92, 61),
        )
        if thumbnail is not None:
            ctk.CTkLabel(
                card,
                text="",
                image=thumbnail,
                fg_color="transparent",
                width=98,
                height=64,
            ).grid(
                row=0,
                column=0,
                rowspan=3,
                padx=(9, 10),
                pady=12,
            )
        else:
            ctk.CTkLabel(
                card,
                text="▤",
                width=52,
                height=52,
                corner_radius=10,
                fg_color=soft,
                text_color=accent,
                font=(Fonts.FAMILY, 20, "bold"),
            ).grid(
                row=0,
                column=0,
                rowspan=3,
                padx=(10, 12),
                pady=18,
            )

        ctk.CTkLabel(
            card,
            text=str(project.get("nom", "Projet sans nom")),
            font=(Fonts.FAMILY, 12, "bold"),
            text_color=self.INK,
            anchor="w",
        ).grid(
            row=0,
            column=1,
            sticky="sw",
            pady=(9, 0),
        )

        ctk.CTkLabel(
            card,
            text=self._project_info(project),
            font=(Fonts.FAMILY, 8),
            text_color=self.MUTED,
            anchor="w",
        ).grid(
            row=1,
            column=1,
            sticky="w",
            pady=(2, 0),
        )

        badges = ctk.CTkFrame(
            card,
            fg_color="transparent",
        )
        badges.grid(
            row=2,
            column=1,
            sticky="sw",
            pady=(5, 10),
        )
        self._create_status_badge(
            badges,
            status,
        ).pack(side="left", padx=(0, 5))

        bureau = str(
            project.get("dernier_bureau", "Centre du projet")
        )
        ctk.CTkLabel(
            badges,
            text=f"Dernier bureau : {bureau}",
            height=22,
            corner_radius=11,
            fg_color=self.PANEL_BG,
            text_color=self.INK,
            font=(Fonts.FAMILY, 8),
            padx=8,
        ).pack(side="left")

        self._create_square_command(
            card,
            icon="↗",
            label="Reprendre",
            command=lambda data=project: self._open_recent_project(data),
            accent=accent,
            soft=soft,
            size=48,
        ).grid(
            row=0,
            column=2,
            rowspan=3,
            padx=10,
            pady=18,
        )

        return card

    def _create_recent_row(
        self,
        parent,
        project: dict,
    ) -> ctk.CTkFrame:
        status = self._status(project)
        accent, soft = self.STATUS_STYLES.get(
            status,
            (self.SKY, self.SKY_SOFT),
        )

        row = ctk.CTkFrame(
            parent,
            height=33,
            fg_color=self.GROUP_BG,
            corner_radius=7,
            border_width=1,
            border_color=self.BORDER,
        )
        row.grid_propagate(False)
        row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            row,
            text="▤",
            width=26,
            text_color=accent,
            font=(Fonts.FAMILY, 11, "bold"),
        ).grid(row=0, column=0, padx=(8, 4))

        ctk.CTkLabel(
            row,
            text=str(project.get("nom", "Projet sans nom")),
            font=(Fonts.FAMILY, 8, "bold"),
            text_color=self.INK,
            anchor="w",
        ).grid(row=0, column=1, sticky="ew")

        self._create_status_badge(
            row,
            status,
            compact=True,
        ).grid(row=0, column=2, padx=4)

        ctk.CTkLabel(
            row,
            text=f"{int(project.get('pages', 0) or 0)} p.",
            width=38,
            font=(Fonts.FAMILY, 7),
            text_color=self.MUTED,
        ).grid(row=0, column=3)

        ctk.CTkLabel(
            row,
            text=self._short_date(
                project.get("date_modification", "")
            ),
            width=104,
            font=(Fonts.FAMILY, 7),
            text_color=self.MUTED,
        ).grid(row=0, column=4)

        self._create_small_action(
            row,
            command=lambda data=project: self._open_recent_project(data),
            accent=accent,
            soft=soft,
        ).grid(row=0, column=5, padx=(4, 6), pady=2)

        return row

    def _create_no_other_recent(self, parent) -> ctk.CTkFrame:
        row = ctk.CTkFrame(
            parent,
            height=34,
            fg_color=self.PANEL_BG,
            corner_radius=7,
        )
        row.grid_propagate(False)
        row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            row,
            text="◇",
            width=30,
            text_color=self.YELLOW,
            font=(Fonts.FAMILY, 11, "bold"),
        ).grid(row=0, column=0, padx=(8, 2))

        ctk.CTkLabel(
            row,
            text="Aucun autre projet récent pour le moment.",
            font=(Fonts.FAMILY, 8),
            text_color=self.MUTED,
            anchor="w",
        ).grid(row=0, column=1, sticky="w")

        return row

    def _create_empty_recent(self, parent) -> ctk.CTkFrame:
        row = ctk.CTkFrame(
            parent,
            height=74,
            fg_color=self.PANEL_BG,
            corner_radius=9,
            border_width=1,
            border_color=self.BORDER,
        )
        row.grid_propagate(False)
        row.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            row,
            text="◇",
            width=44,
            height=44,
            corner_radius=10,
            fg_color=self.YELLOW_SOFT,
            text_color=self.YELLOW,
            font=(Fonts.FAMILY, 19, "bold"),
        ).grid(row=0, column=0, rowspan=2, padx=(12, 12), pady=15)

        ctk.CTkLabel(
            row,
            text="Aucun projet récent",
            font=(Fonts.FAMILY, 11, "bold"),
            text_color=self.INK,
            anchor="w",
        ).grid(row=0, column=1, sticky="sw")

        ctk.CTkLabel(
            row,
            text="Créez un projet ou ouvrez un ouvrage existant.",
            font=(Fonts.FAMILY, 9),
            text_color=self.MUTED,
            anchor="w",
        ).grid(row=1, column=1, sticky="nw", pady=(2, 0))

        return row

    # ==========================================================
    # Projet actif et accès directs
    # ==========================================================

    def _create_active_project_panel(self, parent) -> ctk.CTkFrame:
        panel = ctk.CTkFrame(
            parent,
            fg_color=self.GROUP_BG,
            corner_radius=0,
        )
        panel.grid_columnconfigure(0, weight=1)

        self._create_panel_heading(
            panel,
            icon="▦",
            title="Repères & accès directs",
            subtitle="Raccourcis du dernier projet actif.",
            accent=self.LILAC,
            soft=self.LILAC_SOFT,
            count=None,
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=2,
            pady=(0, 6),
        )

        active_line = self._create_active_project_line(panel)
        active_line.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=0,
            pady=(0, 5),
        )

        tile_area = ctk.CTkFrame(
            panel,
            fg_color=self.GROUP_BG,
            corner_radius=0,
            height=52,
        )
        tile_area.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=0,
            pady=(0, 5),
        )
        tile_area.grid_propagate(False)
        tile_area.grid_columnconfigure(0, weight=1)
        tile_area.grid_columnconfigure(5, weight=1)
        tile_area.grid_rowconfigure(0, weight=1)

        for index, tile in enumerate(self.WORKSPACE_TILES):
            key, icon, title, subtitle, accent, soft = tile
            enabled = self.active_project is not None
            command = (
                lambda workspace_key=key: self._open_active_workspace(
                    workspace_key
                )
                if enabled
                else None
            )
            self._create_workspace_tile(
                tile_area,
                icon=icon,
                title=title,
                subtitle=subtitle,
                accent=accent,
                soft=soft,
                command=command,
                enabled=enabled,
                highlighted=(
                    enabled
                    and str(
                        self.active_project.get(
                            "dernier_bureau_key",
                            "",
                        )
                    )
                    == key
                ),
            ).grid(
                row=0,
                column=index + 1,
                sticky="ns",
                padx=3,
            )

        self._create_information_strip(panel).grid(
            row=3,
            column=0,
            sticky="ew",
            padx=0,
            pady=(0, 0),
        )

        return panel

    def _workspace_key_from_project(self, project: dict | None) -> str:
        if not project:
            return "centre"

        key = str(project.get("dernier_bureau_key", "")).strip().lower()
        if key:
            return key

        bureau = str(project.get("dernier_bureau", "")).strip().lower()
        mapping = {
            "maquettage": "maquettage",
            "atelier": "atelier",
            "conception": "conception",
            "centre": "centre",
            "centre du projet": "centre",
        }
        return mapping.get(bureau, "centre")

    def _workspace_visuals(self, project: dict | None) -> tuple[str, str, str]:
        key = self._workspace_key_from_project(project)
        for item in self.WORKSPACE_TILES:
            if item[0] == key:
                return item[4], item[5], item[2]
        return self.CELADON, self.CELADON_SOFT, "Centre du projet"

    def _create_active_project_line(self, parent) -> ctk.CTkFrame:
        line = ctk.CTkFrame(
            parent,
            height=30,
            fg_color=self.PANEL_BG,
            corner_radius=8,
        )
        line.grid_propagate(False)
        line.grid_columnconfigure(1, weight=1)

        if self.active_project is None:
            ctk.CTkLabel(
                line,
                text="○",
                width=28,
                text_color=self.TEXT_LIGHT,
                font=(Fonts.FAMILY, 12, "bold"),
            ).grid(row=0, column=0, padx=(7, 2))
            ctk.CTkLabel(
                line,
                text="Aucun projet actif",
                font=(Fonts.FAMILY, 8, "bold"),
                text_color=self.MUTED,
                anchor="w",
            ).grid(row=0, column=1, sticky="w")
            return line

        accent, soft, bureau_title = self._workspace_visuals(self.active_project)

        ctk.CTkLabel(
            line,
            text="●",
            width=28,
            text_color=accent,
            font=(Fonts.FAMILY, 11, "bold"),
        ).grid(row=0, column=0, padx=(7, 2))

        ctk.CTkLabel(
            line,
            text=str(
                self.active_project.get("nom", "Projet sans nom")
            ),
            font=(Fonts.FAMILY, 8, "bold"),
            text_color=self.INK,
            anchor="w",
        ).grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(
            line,
            text=f"Dernier bureau : {bureau_title}",
            height=18,
            corner_radius=9,
            fg_color=soft,
            text_color=accent,
            font=(Fonts.FAMILY, 7, "bold"),
            anchor="e",
            padx=8,
        ).grid(row=0, column=2, sticky="e", padx=(8, 10))

        return line

    def _create_workspace_tile(
        self,
        parent,
        *,
        icon: str,
        title: str,
        subtitle: str,
        accent: str,
        soft: str,
        command: Callable[[], None] | None,
        enabled: bool,
        highlighted: bool,
    ) -> ctk.CTkFrame:
        border = accent if enabled else self.BORDER
        background = soft if highlighted else self.GROUP_BG
        text_color = self.INK if enabled else self.TEXT_LIGHT
        icon_color = accent if enabled else self.TEXT_LIGHT

        tile = ctk.CTkFrame(
            parent,
            width=114,
            height=48,
            fg_color=background,
            corner_radius=9,
            border_width=2 if highlighted else 1,
            border_color=border,
        )
        tile.grid_propagate(False)
        tile.pack_propagate(False)

        content = ctk.CTkFrame(
            tile,
            fg_color="transparent",
        )
        content.pack(fill="both", expand=True, padx=5, pady=3)
        content.grid_columnconfigure(1, weight=1)

        icon_label = ctk.CTkLabel(
            content,
            text=icon,
            width=22,
            height=22,
            font=(Fonts.FAMILY, 12, "bold"),
            text_color=icon_color,
        )
        icon_label.grid(
            row=0,
            column=0,
            rowspan=2,
            sticky="w",
            padx=(0, 4),
        )

        title_label = ctk.CTkLabel(
            content,
            text=title,
            font=(Fonts.FAMILY, 7, "bold"),
            text_color=text_color,
            height=12,
            anchor="w",
        )
        title_label.grid(row=0, column=1, sticky="sw")

        subtitle_label = ctk.CTkLabel(
            content,
            text=subtitle,
            font=(Fonts.FAMILY, 6),
            text_color=self.MUTED if enabled else self.TEXT_LIGHT,
            height=11,
            anchor="w",
        )
        subtitle_label.grid(row=1, column=1, sticky="nw")

        if enabled and command is not None:
            def activate(_event=None) -> None:
                command()

            def enter(_event=None) -> None:
                tile.configure(fg_color=soft)

            def leave(_event=None) -> None:
                tile.configure(fg_color=background)

            for widget in (
                tile,
                content,
                icon_label,
                title_label,
                subtitle_label,
            ):
                widget.bind("<Button-1>", activate)
                widget.bind("<Enter>", enter)
                widget.bind("<Leave>", leave)
                widget.configure(cursor="hand2")

        return tile

    def _create_information_strip(self, parent) -> ctk.CTkFrame:
        strip = ctk.CTkFrame(
            parent,
            height=56,
            fg_color=self.PANEL_BG,
            corner_radius=8,
            border_width=1,
            border_color=self.BORDER,
        )
        strip.grid_propagate(False)
        strip.grid_columnconfigure((0, 1, 2), weight=1, uniform="info")
        strip.grid_rowconfigure(0, weight=1)

        if self.active_project is None:
            values = (
                ("◇", "Projet", "Aucun projet actif", self.CELADON),
                ("⌂", "Étape", "Aucune", self.LILAC),
                ("◷", "Activité", "Aucune", self.SKY),
            )
        else:
            values = (
                (
                    "✓",
                    "État",
                    self._status(self.active_project),
                    self.STATUS_STYLES.get(
                        self._status(self.active_project),
                        (self.CELADON, self.CELADON_SOFT),
                    )[0],
                ),
                (
                    "⌂",
                    "Étape actuelle",
                    str(
                        self.active_project.get(
                            "dernier_bureau",
                            "Centre du projet",
                        )
                    ),
                    self.LILAC,
                ),
                (
                    "◷",
                    "Dernière activité",
                    self._short_date(
                        self.active_project.get(
                            "date_modification",
                            self.active_project.get(
                                "derniere_ouverture",
                                "",
                            ),
                        )
                    ),
                    self.SKY,
                ),
            )

        for index, value in enumerate(values):
            icon, title, text, accent = value
            cell = ctk.CTkFrame(
                strip,
                fg_color="transparent",
            )
            cell.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=(8 if index == 0 else 4, 8 if index == 2 else 4),
                pady=4,
            )
            cell.grid_columnconfigure(1, weight=1)
            cell.grid_rowconfigure((0, 1), weight=1, uniform="info_rows")

            ctk.CTkLabel(
                cell,
                text=icon,
                width=22,
                text_color=accent,
                font=(Fonts.FAMILY, 11, "bold"),
            ).grid(row=0, column=0, rowspan=2, padx=(0, 4))

            ctk.CTkLabel(
                cell,
                text=title,
                height=16,
                font=(Fonts.FAMILY, 7, "bold"),
                text_color=self.INK,
                anchor="sw",
            ).grid(row=0, column=1, sticky="nsew")

            ctk.CTkLabel(
                cell,
                text=text,
                height=16,
                font=(Fonts.FAMILY, 7),
                text_color=accent,
                anchor="nw",
            ).grid(row=1, column=1, sticky="nsew")

            if index < 2:
                ctk.CTkFrame(
                    strip,
                    width=1,
                    height=30,
                    fg_color=self.BORDER,
                ).grid(row=0, column=index, sticky="e", pady=8)

        return strip

    # ==========================================================
    # Éléments communs
    # ==========================================================

    def _create_panel_heading(
        self,
        parent,
        *,
        icon: str,
        title: str,
        subtitle: str,
        accent: str,
        soft: str,
        count: int | None,
    ) -> ctk.CTkFrame:
        heading = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )
        heading.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            heading,
            text=icon,
            width=30,
            height=30,
            corner_radius=7,
            fg_color=soft,
            text_color=accent,
            font=(Fonts.FAMILY, 13, "bold"),
        ).grid(row=0, column=0, rowspan=2, padx=(0, 8))

        ctk.CTkLabel(
            heading,
            text=title,
            font=(Fonts.FAMILY, 12, "bold"),
            text_color=self.INK,
            anchor="w",
        ).grid(row=0, column=1, sticky="sw")

        ctk.CTkLabel(
            heading,
            text=subtitle,
            font=(Fonts.FAMILY, 7),
            text_color=self.MUTED,
            anchor="w",
        ).grid(row=1, column=1, sticky="nw", pady=(2, 0))

        if count is not None:
            ctk.CTkLabel(
                heading,
                text=str(count),
                width=26,
                height=22,
                corner_radius=11,
                fg_color=soft,
                text_color=self.INK,
                font=(Fonts.FAMILY, 8, "bold"),
            ).grid(row=0, column=2, rowspan=2, padx=(8, 0))

        return heading

    def _create_square_command(
        self,
        parent,
        *,
        icon: str,
        label: str,
        command: Callable[[], None],
        accent: str,
        soft: str,
        size: int,
    ) -> ctk.CTkFrame:
        tool = ctk.CTkFrame(
            parent,
            width=size,
            height=size,
            fg_color=accent,
            corner_radius=8,
            border_width=1,
            border_color=accent,
        )
        tool.pack_propagate(False)
        tool.grid_propagate(False)

        icon_label = ctk.CTkLabel(
            tool,
            text=icon,
            height=max(22, int(size * 0.45)),
            font=(Fonts.FAMILY, max(13, int(size * 0.27)), "bold"),
            text_color="white",
        )
        icon_label.pack(fill="x", padx=3, pady=(4, 0))

        label_widget = ctk.CTkLabel(
            tool,
            text=label,
            height=max(16, int(size * 0.24)),
            font=(Fonts.FAMILY, max(7, int(size * 0.12)), "bold"),
            text_color="white",
        )
        label_widget.pack(fill="x", padx=3, pady=(0, 4))

        def activate(_event=None) -> None:
            command()

        def enter(_event=None) -> None:
            tool.configure(fg_color=soft)
            icon_label.configure(text_color=accent)
            label_widget.configure(text_color=self.INK)

        def leave(_event=None) -> None:
            tool.configure(fg_color=accent)
            icon_label.configure(text_color="white")
            label_widget.configure(text_color="white")

        for widget in (
            tool,
            icon_label,
            label_widget,
        ):
            widget.bind("<Button-1>", activate)
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)
            widget.configure(cursor="hand2")

        return tool

    def _create_small_action(
        self,
        parent,
        *,
        command: Callable[[], None],
        accent: str,
        soft: str,
    ) -> ctk.CTkFrame:
        action = ctk.CTkFrame(
            parent,
            width=28,
            height=28,
            fg_color=soft,
            corner_radius=7,
            border_width=1,
            border_color=accent,
        )
        action.grid_propagate(False)

        label = ctk.CTkLabel(
            action,
            text="›",
            font=(Fonts.FAMILY, 15, "bold"),
            text_color=accent,
        )
        label.place(relx=0.5, rely=0.48, anchor="center")

        def activate(_event=None) -> None:
            command()

        def enter(_event=None) -> None:
            action.configure(fg_color=self.GROUP_BG)

        def leave(_event=None) -> None:
            action.configure(fg_color=soft)

        for widget in (action, label):
            widget.bind("<Button-1>", activate)
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)
            widget.configure(cursor="hand2")

        return action

    def _create_status_badge(
        self,
        parent,
        status: str,
        compact: bool = False,
    ) -> ctk.CTkLabel:
        accent, soft = self.STATUS_STYLES.get(
            status,
            (self.CELADON, self.CELADON_SOFT),
        )
        return ctk.CTkLabel(
            parent,
            text=status,
            height=18 if compact else 22,
            corner_radius=9 if compact else 11,
            fg_color=soft,
            text_color=accent,
            border_width=1,
            border_color=accent,
            font=(Fonts.FAMILY, 7 if compact else 8, "bold"),
            padx=7,
        )

    # ==========================================================
    # Fond unique et grandes cartes arrondies
    # ==========================================================

    def _schedule_layout(self, _event=None) -> None:
        canvas = self._canvas
        if canvas is None or not canvas.winfo_exists():
            return
        if self._layout_job is not None:
            try:
                canvas.after_cancel(self._layout_job)
            except tk.TclError:
                pass
        self._layout_job = canvas.after(80, self._layout_now)

    def _layout_now(self) -> None:
        self._layout_job = None
        canvas = self._canvas
        if canvas is None or not canvas.winfo_exists():
            return

        canvas.update_idletasks()
        width = max(canvas.winfo_width(), 1000)
        height = max(canvas.winfo_height(), 680)

        content_width = min(1420, max(980, width - 120))
        left = (width - content_width) / 2
        gap = 24
        column_width = (content_width - gap) / 2

        # Hauteurs calculées d'après le contenu réel des panneaux.
        # Le bandeau et les deux zones inférieures ne sont plus rognés.
        header_top = 12
        header_height = 140
        header_bottom = header_top + header_height

        top_height = 230
        row_gap = 20
        bottom_margin = 18
        minimum_header_gap = 18

        # La zone « Repères & accès directs » contient une bande
        # d'informations supplémentaire. Les deux panneaux inférieurs
        # reçoivent donc davantage de hauteur, tout en restant adaptés
        # aux fenêtres moins hautes.
        available_lower_height = (
            height
            - header_bottom
            - minimum_header_gap
            - top_height
            - row_gap
            - bottom_margin
        )
        lower_height = max(
            236,
            min(276, available_lower_height),
        )

        group_height = top_height + row_gap + lower_height
        free_height = (
            height
            - header_bottom
            - bottom_margin
            - group_height
        )
        group_top = header_bottom + max(
            minimum_header_gap,
            free_height / 2,
        )

        lower_top = group_top + top_height + row_gap

        rects = {
            "create": (
                left,
                group_top,
                left + column_width,
                group_top + top_height,
            ),
            "open": (
                left + column_width + gap,
                group_top,
                left + content_width,
                group_top + top_height,
            ),
            "recent": (
                left,
                lower_top,
                left + column_width,
                lower_top + lower_height,
            ),
            "active": (
                left + column_width + gap,
                lower_top,
                left + content_width,
                lower_top + lower_height,
            ),
        }

        composed = self._compose_background(width, height, rects)
        photo = ImageTk.PhotoImage(composed)
        self._canvas_background_image = photo

        if self._canvas_background_id is None:
            self._canvas_background_id = canvas.create_image(
                0,
                0,
                image=photo,
                anchor="nw",
            )
        else:
            canvas.itemconfigure(
                self._canvas_background_id,
                image=photo,
            )
            canvas.coords(
                self._canvas_background_id,
                0,
                0,
            )

        canvas.tag_lower(self._canvas_background_id)

        self._place_window(
            "header",
            left,
            header_top,
            content_width,
            header_height,
        )

        for key, rect in rects.items():
            x1, y1, x2, y2 = rect
            inset = 16 if key in ("create", "open") else 14
            self._place_window(
                key,
                x1 + inset,
                y1 + inset,
                (x2 - x1) - inset * 2,
                (y2 - y1) - inset * 2,
            )

    def _place_window(
        self,
        key: str,
        x: float,
        y: float,
        width: float,
        height: float,
    ) -> None:
        canvas = self._canvas
        item = self._window_ids.get(key)
        if canvas is None or item is None:
            return
        canvas.coords(item, int(x), int(y))
        canvas.itemconfigure(
            item,
            width=max(int(width), 1),
            height=max(int(height), 1),
        )

    def _compose_background(
        self,
        width: int,
        height: int,
        rects: dict[str, tuple[float, float, float, float]],
    ) -> Image.Image:
        if self._background_source is None:
            base = Image.new("RGB", (width, height), self.WINDOW_BG)
        else:
            base = self._background_source.resize(
                (width, height),
                Image.Resampling.LANCZOS,
            ).convert("RGB")

        styles = {
            "create": (self.CREATE_CARD_BG, self.CELADON),
            "open": (self.OPEN_CARD_BG, self.LILAC),
            "recent": (self.GROUP_BG, self.BORDER),
            "active": (self.GROUP_BG, self.BORDER),
        }
        for key, rect in rects.items():
            fill, outline = styles[key]
            self._paint_rounded_card(
                base,
                rect,
                radius=18,
                fill=fill,
                outline=outline,
                border_width=1,
            )
        return base

    @staticmethod
    def _paint_rounded_card(
        image: Image.Image,
        rect: tuple[float, float, float, float],
        *,
        radius: int,
        fill: str,
        outline: str,
        border_width: int,
    ) -> None:
        x1, y1, x2, y2 = (int(round(value)) for value in rect)
        card_width = max(x2 - x1, 1)
        card_height = max(y2 - y1, 1)
        scale = 4

        mask = Image.new("L", (card_width * scale, card_height * scale), 0)
        drawer = ImageDraw.Draw(mask)
        drawer.rounded_rectangle(
            (0, 0, card_width * scale - 1, card_height * scale - 1),
            radius=radius * scale,
            fill=255,
        )
        mask = mask.resize(
            (card_width, card_height),
            Image.Resampling.LANCZOS,
        )
        fill_layer = Image.new("RGB", (card_width, card_height), fill)
        image.paste(fill_layer, (x1, y1), mask)

        if border_width <= 0:
            return

        outer = mask
        inset = border_width
        inner_width = max(card_width - inset * 2, 1)
        inner_height = max(card_height - inset * 2, 1)
        inner_mask = Image.new("L", (inner_width * scale, inner_height * scale), 0)
        inner_drawer = ImageDraw.Draw(inner_mask)
        inner_drawer.rounded_rectangle(
            (0, 0, inner_width * scale - 1, inner_height * scale - 1),
            radius=max((radius - inset) * scale, 1),
            fill=255,
        )
        inner_mask = inner_mask.resize(
            (inner_width, inner_height),
            Image.Resampling.LANCZOS,
        )
        border_mask = outer.copy()
        border_mask.paste(
            Image.new("L", (inner_width, inner_height), 0),
            (inset, inset),
            inner_mask,
        )
        border_layer = Image.new("RGB", (card_width, card_height), outline)
        image.paste(border_layer, (x1, y1), border_mask)

    def _load_background_source(self) -> Image.Image | None:
        path = self._find_asset_path("editorial_bg_accueil.png")
        if path is None:
            return None
        try:
            return Image.open(path).convert("RGB")
        except Exception:
            return None

    # ==========================================================
    # Images et données
    # ==========================================================

    def _asset_image(
        self,
        filename: str,
        *,
        size: tuple[int, int],
    ) -> ctk.CTkImage | None:
        key = f"{filename}:{size[0]}x{size[1]}"
        if key in self._images:
            return self._images[key]

        path = self._find_asset_path(filename)
        if path is None:
            return None

        try:
            source = Image.open(path).convert("RGBA")
            image = ctk.CTkImage(
                light_image=source,
                dark_image=source,
                size=size,
            )
        except Exception:
            return None

        self._images[key] = image
        return image

    @staticmethod
    def _find_asset_path(filename: str) -> Path | None:
        project_root = Path(__file__).resolve().parents[3]

        candidates = (
            project_root / "assets" / "interface" / filename,
            project_root
            / "assets"
            / "interface"
            / "backgrounds"
            / filename,
            project_root / "assets" / "logos" / filename,
            project_root / filename,
            Path.cwd() / "assets" / "interface" / filename,
            Path.cwd()
            / "assets"
            / "interface"
            / "backgrounds"
            / filename,
            Path.cwd() / "assets" / "logos" / filename,
        )

        for path in candidates:
            if path.is_file():
                return path

        return None

    @staticmethod
    def _status(project: dict) -> str:
        value = str(project.get("statut", "En cours")).strip()
        return value or "En cours"

    def _project_info(self, project: dict) -> str:
        pages = int(project.get("pages", 0) or 0)
        validated = int(project.get("pages_validees", 0) or 0)
        modified = self._short_date(
            project.get(
                "date_modification",
                project.get("derniere_ouverture", ""),
            )
        )

        if pages:
            return (
                f"{pages} page(s)  ·  {validated} validée(s)  ·  "
                f"{modified}"
            )
        return f"Aucune page créée  ·  {modified}"

    @staticmethod
    def _short_date(value) -> str:
        text = str(value or "").strip()
        if not text:
            return "date inconnue"

        try:
            parsed = datetime.fromisoformat(text)
            return parsed.strftime("%d/%m/%Y %H:%M")
        except (TypeError, ValueError):
            return text

    # ==========================================================
    # Commandes
    # ==========================================================

    def _open_active_workspace(self, workspace_key: str) -> None:
        if self.active_project is None:
            return
        if self.on_open_workspace is None:
            self._open_recent_project(self.active_project)
            return
        self._restore_application_menu()
        self.on_open_workspace(
            self.active_project,
            workspace_key,
        )

    def _invoke_file_command(self, command_label: str) -> None:
        try:
            root = self.parent.winfo_toplevel()
            menu_bar = self._stored_menu_widget

            if menu_bar is None:
                menu_name = str(root.cget("menu") or self._stored_menu_name)
                if not menu_name:
                    raise RuntimeError(
                        "Le menu Fichier n’est pas disponible."
                    )
                menu_bar = root.nametowidget(menu_name)

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

            file_menu.invoke(command_index)

        except Exception as exc:
            messagebox.showerror(
                "Commande indisponible",
                str(exc),
                parent=self.parent.winfo_toplevel(),
            )

    def _open_recent_project(self, project: dict) -> None:
        if self.on_open_recent is not None:
            self._restore_application_menu()
            self.on_open_recent(project)

    # ==========================================================
    # Accueil sans barre de menu
    # ==========================================================

    def _hide_application_menu(self) -> None:
        try:
            root = self.parent.winfo_toplevel()
            menu_name = str(root.cget("menu") or "")
            if not menu_name:
                return

            self._stored_menu_name = menu_name
            try:
                self._stored_menu_widget = root.nametowidget(menu_name)
            except (KeyError, tk.TclError):
                self._stored_menu_widget = None

            root.configure(menu="")
            self._menu_hidden = True
        except tk.TclError:
            self._menu_hidden = False

    def _restore_application_menu(self) -> None:
        if not self._menu_hidden or not self._stored_menu_name:
            return

        try:
            root = self.parent.winfo_toplevel()
            root.configure(menu=self._stored_menu_name)
            self._menu_hidden = False
        except tk.TclError:
            pass

    def _on_home_destroy(self, event) -> None:
        if self._home_root is None or event.widget is not self._home_root:
            return
        self._restore_application_menu()

    def _close_application(self) -> None:
        try:
            self.parent.winfo_toplevel().destroy()
        except tk.TclError:
            pass

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
                submenu_name = menu_bar.entrycget(index, "menu")
                return root.nametowidget(submenu_name)
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
            f"recent_projects={len(self.recent_projects)}, "
            f"active_project={self.active_project is not None})"
        )