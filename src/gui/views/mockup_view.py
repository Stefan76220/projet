from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

import customtkinter as ctk

from src.theme.colors import Colors
from src.theme.fonts import Fonts


class MockupView:
    """Pré-chemin de fer visuel, simple et facultatif."""

    # Palette PageMaître : bleu-encre, céladon, bleu ciel, lilas,
    # corail et jaune doux. Les teintes restent claires et non agressives.
    WINDOW_BG = Colors.WINDOW
    RIBBON_BG = "#F3F5F7"
    GROUP_BG = "#FFFFFF"
    CARD_BG = "#FCFCFB"
    CANVAS_BG = "#ECEFF2"
    INK = "#263E63"
    BORDER = "#D5D9DE"
    TEXT_MUTED = Colors.TEXT_LIGHT
    TEXT_LIGHT = "#8B8E88"
    SKY = "#75B6DB"
    CELADON = "#82B7A1"
    LILAC = "#A997C9"
    CORAL = "#DF806B"
    YELLOW = "#D8B85A"
    ACCENT = INK
    ACCENT_SOFT = "#E7EEF6"
    DONE = Colors.SUCCESS
    DANGER = Colors.ERROR

    PAGE_LIBRARY: tuple[dict[str, Any], ...] = (
        {
            "type": "couverture",
            "title": "Couverture",
            "short": "Couverture",
            "symbol": "▧",
            "color": "#DDECF4",
            "accent": SKY,
            "single": True,
        },
        {
            "type": "page_titre",
            "title": "Page de titre",
            "short": "Titre",
            "symbol": "T",
            "color": "#F1E7E2",
            "accent": CORAL,
        },
        {
            "type": "sommaire",
            "title": "Sommaire",
            "short": "Sommaire",
            "symbol": "☷",
            "color": "#E1EEE9",
            "accent": CELADON,
        },
        {
            "type": "avant_propos",
            "title": "Avant-propos",
            "short": "Avant-propos",
            "symbol": "¶",
            "color": "#E3EBF2",
            "accent": SKY,
        },
        {
            "type": "chapitre",
            "title": "Chapitre",
            "short": "Chapitre",
            "symbol": "CH",
            "color": "#F2DDD6",
            "accent": CORAL,
        },
        {
            "type": "fiche",
            "title": "Page fiche",
            "short": "Fiche",
            "symbol": "▦",
            "color": "#DFECE5",
            "accent": CELADON,
        },
        {
            "type": "texte",
            "title": "Page de texte",
            "short": "Texte",
            "symbol": "≡",
            "color": "#DFEAF3",
            "accent": SKY,
        },
        {
            "type": "illustration",
            "title": "Illustration",
            "short": "Illustration",
            "symbol": "▣",
            "color": "#E8E1F1",
            "accent": LILAC,
        },
        {
            "type": "transition",
            "title": "Transition",
            "short": "Transition",
            "symbol": "◇",
            "color": "#F1E8CD",
            "accent": YELLOW,
        },
        {
            "type": "page_blanche",
            "title": "Page blanche",
            "short": "Blanche",
            "symbol": "□",
            "color": "#FAF9F5",
            "accent": "#A4A8A2",
        },
        {
            "type": "conclusion",
            "title": "Conclusion",
            "short": "Conclusion",
            "symbol": "✓",
            "color": "#E7EDD9",
            "accent": "#8AA55C",
        },
        {
            "type": "quatrieme",
            "title": "Quatrième",
            "short": "Quatrième",
            "symbol": "◁",
            "color": "#ECDCD8",
            "accent": CORAL,
            "single": True,
        },
        {
            "type": "autre",
            "title": "Autre page",
            "short": "Autre",
            "symbol": "✦",
            "color": "#E6E8ED",
            "accent": INK,
        },
    )

    def __init__(
        self,
        parent,
        project,
        on_back: Callable[[], None] | None = None,
    ) -> None:
        self.parent = parent
        self.project = project
        self.on_back = on_back

        self.data: dict[str, Any] = self._load_data()
        self._root: ctk.CTkFrame | None = None
        self._sequence_frame: ctk.CTkScrollableFrame | None = None
        self._summary_label: ctk.CTkLabel | None = None
        self._progress_label: ctk.CTkLabel | None = None
        self._preview_window: ctk.CTkToplevel | None = None
        self._preview_body: ctk.CTkFrame | None = None
        self._preview_nav: ctk.CTkFrame | None = None
        self._preview_position_label: ctk.CTkLabel | None = None
        self._preview_previous_button: ctk.CTkButton | None = None
        self._preview_next_button: ctk.CTkButton | None = None
        self._preview_large_button: ctk.CTkButton | None = None
        self._preview_overview_button: ctk.CTkButton | None = None
        self._preview_mode = "large"
        self._preview_index = 0
        self._preview_spreads: list[
            tuple[
                dict[str, Any] | None,
                dict[str, Any] | None,
                int | None,
                int | None,
            ]
        ] = []

    # ==========================================================
    # Affichage principal
    # ==========================================================

    def show(self) -> None:
        self._clear_parent()

        self._root = ctk.CTkFrame(
            self.parent,
            fg_color=self.WINDOW_BG,
            corner_radius=0,
        )
        self._root.pack(fill="both", expand=True)
        self._root.grid_columnconfigure(0, weight=1)
        self._root.grid_rowconfigure(2, weight=1)

        self._create_header(self._root).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=12,
            pady=(6, 4),
        )

        self._create_ribbon(self._root).grid(
            row=1,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 8),
        )

        self._create_sequence_panel(self._root).grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 10),
        )

        self._refresh_sequence()

    def _create_header(self, parent) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(parent, fg_color="transparent", height=32)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_propagate(False)

        ctk.CTkButton(
            frame,
            text="← Centre",
            width=92,
            height=28,
            corner_radius=7,
            fg_color=self.GROUP_BG,
            hover_color=Colors.BUTTON_HOVER,
            text_color=self.INK,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.SMALL,
            command=self._go_back,
        ).grid(row=0, column=0, sticky="w", padx=(0, 12))

        ctk.CTkLabel(
            frame,
            text="Bureau de maquettage",
            font=Fonts.H2,
            text_color=self.INK,
        ).grid(row=0, column=1, sticky="w")

        project_name = str(getattr(self.project, "name", "") or "Projet sans nom")
        ctk.CTkLabel(
            frame,
            text=project_name,
            font=Fonts.SMALL,
            text_color=self.TEXT_MUTED,
        ).grid(row=0, column=2, sticky="e")

        return frame

    def _create_ribbon(self, parent) -> ctk.CTkFrame:
        ribbon = ctk.CTkFrame(
            parent,
            fg_color=self.RIBBON_BG,
            corner_radius=0,
            height=112,
        )
        ribbon.grid_columnconfigure(0, weight=1)
        ribbon.grid_propagate(False)

        scroll = ctk.CTkScrollableFrame(
            ribbon,
            fg_color="transparent",
            corner_radius=0,
            orientation="horizontal",
            height=104,
        )
        scroll.grid(row=0, column=0, sticky="ew", padx=4, pady=4)

        groups = (
            (
                "Début du livre",
                {"couverture", "page_titre", "sommaire", "avant_propos"},
            ),
            (
                "Pages intérieures",
                {
                    "chapitre",
                    "fiche",
                    "texte",
                    "illustration",
                    "transition",
                    "page_blanche",
                },
            ),
            (
                "Fin du livre",
                {"conclusion", "quatrieme", "autre"},
            ),
        )

        column = 0
        for title, page_types in groups:
            definitions = [
                definition
                for definition in self.PAGE_LIBRARY
                if definition["type"] in page_types
            ]
            group = self._create_ribbon_group(scroll, title, definitions)
            group.grid(row=0, column=column, sticky="ns", padx=(0, 5))
            column += 1

        display_group = ctk.CTkFrame(
            scroll,
            width=88,
            height=94,
            fg_color=self.GROUP_BG,
            corner_radius=10,
        )
        display_group.grid(row=0, column=column, sticky="ns", padx=(0, 4))
        display_group.grid_propagate(False)
        display_group.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            display_group,
            text="▣\nAperçu",
            width=68,
            height=58,
            corner_radius=8,
            fg_color=self.ACCENT_SOFT,
            hover_color=self.GROUP_BG,
            text_color=self.INK,
            border_width=1,
            border_color=self.SKY,
            font=(Fonts.FAMILY, 11),
            command=self._open_preview,
        ).grid(row=0, column=0, padx=8, pady=(7, 1))

        ctk.CTkLabel(
            display_group,
            text="Affichage",
            font=Fonts.SMALL,
            text_color=self.TEXT_MUTED,
            height=18,
        ).grid(row=1, column=0, sticky="s", padx=5, pady=(0, 4))

        return ribbon

    def _create_ribbon_group(
        self,
        parent,
        title: str,
        definitions: list[dict[str, Any]],
    ) -> ctk.CTkFrame:
        width = max(86, 14 + len(definitions) * 70)
        group = ctk.CTkFrame(
            parent,
            width=width,
            height=94,
            fg_color=self.GROUP_BG,
            corner_radius=10,
        )
        group.grid_propagate(False)

        controls = ctk.CTkFrame(group, fg_color="transparent")
        controls.pack(fill="both", expand=True, padx=5, pady=(5, 1))

        for column, definition in enumerate(definitions):
            accent = str(definition.get("accent", self.INK))
            button = ctk.CTkButton(
                controls,
                text=f"{definition['symbol']}\n{definition.get('short', definition['title'])}",
                width=66,
                height=58,
                corner_radius=8,
                fg_color=str(definition["color"]),
                hover_color=self.GROUP_BG,
                text_color=accent,
                border_width=1,
                border_color=accent,
                font=(Fonts.FAMILY, 11),
                command=lambda selected=definition: self._add_item(selected),
            )
            button.grid(
                row=0,
                column=column,
                padx=(2 if column else 1, 2),
                pady=2,
            )

        ctk.CTkLabel(
            group,
            text=title,
            font=Fonts.SMALL,
            text_color=self.TEXT_MUTED,
            height=18,
        ).pack(side="bottom", fill="x", pady=(0, 4))

        return group

    def _create_sequence_panel(self, parent) -> ctk.CTkFrame:
        panel = ctk.CTkFrame(
            parent,
            fg_color=self.CARD_BG,
            corner_radius=8,
            border_width=1,
            border_color=self.BORDER,
        )
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        title_row = ctk.CTkFrame(panel, fg_color="transparent", height=32)
        title_row.grid(row=0, column=0, sticky="ew", padx=10, pady=(4, 3))
        title_row.grid_columnconfigure(0, weight=1)
        title_row.grid_propagate(False)

        ctk.CTkLabel(
            title_row,
            text="Pré-chemin de fer",
            font=Fonts.H2,
            text_color=self.INK,
        ).grid(row=0, column=0, sticky="w")

        self._progress_label = ctk.CTkLabel(
            title_row,
            text="",
            font=Fonts.SMALL,
            text_color=self.DONE,
        )
        self._progress_label.grid(row=0, column=1, sticky="e", padx=(8, 10))

        self._summary_label = ctk.CTkLabel(
            title_row,
            text="",
            font=Fonts.SMALL,
            text_color=self.INK,
        )
        self._summary_label.grid(row=0, column=2, sticky="e")

        self._sequence_frame = ctk.CTkScrollableFrame(
            panel,
            fg_color=self.RIBBON_BG,
            corner_radius=6,
        )
        self._sequence_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=7,
            pady=(0, 7),
        )
        self._sequence_frame.grid_columnconfigure(0, weight=1)

        return panel

    def _refresh_sequence(self) -> None:
        if self._sequence_frame is None:
            return

        for child in self._sequence_frame.winfo_children():
            child.destroy()

        items = self._items()

        if not items:
            ctk.CTkLabel(
                self._sequence_frame,
                text="Clique sur une page pour commencer.",
                font=Fonts.NORMAL,
                text_color=self.TEXT_LIGHT,
            ).grid(row=0, column=0, sticky="nsew", padx=20, pady=28)
        else:
            for index, item in enumerate(items):
                self._create_sequence_row(
                    self._sequence_frame,
                    item,
                    index,
                    len(items),
                ).grid(
                    row=index,
                    column=0,
                    sticky="ew",
                    padx=4,
                    pady=3,
                )

        self._update_summary()

    def _create_sequence_row(
        self,
        parent,
        item: dict[str, Any],
        index: int,
        total_items: int,
    ) -> ctk.CTkFrame:
        definition = self._definition_for(item.get("type", "autre"))
        count = max(1, int(item.get("count", 1)))
        done = bool(item.get("done", False))
        accent = str(definition.get("accent", self.INK))

        row = ctk.CTkFrame(
            parent,
            height=54,
            fg_color=self.CARD_BG,
            corner_radius=7,
            border_width=1,
            border_color=(self.DONE if done else self.BORDER),
        )
        row.grid_columnconfigure(1, weight=1)
        row.grid_propagate(False)

        thumbnail = ctk.CTkFrame(
            row,
            width=38,
            height=44,
            fg_color=definition["color"],
            corner_radius=5,
            border_width=1,
            border_color=accent,
        )
        thumbnail.grid(row=0, column=0, padx=(5, 7), pady=4)
        thumbnail.grid_propagate(False)

        ctk.CTkLabel(
            thumbnail,
            text=str(definition["symbol"]),
            font=(Fonts.FAMILY, 14, "bold"),
            text_color=accent,
        ).place(relx=0.5, rely=0.37, anchor="center")

        ctk.CTkLabel(
            thumbnail,
            text=(f"×{count}" if count > 1 else "1"),
            font=(Fonts.FAMILY, 10),
            text_color=self.INK,
        ).place(relx=0.5, rely=0.78, anchor="center")

        ctk.CTkLabel(
            row,
            text=str(item.get("title") or definition["title"]),
            font=Fonts.NORMAL,
            text_color=(self.DONE if done else self.INK),
            anchor="w",
        ).grid(row=0, column=1, sticky="w", padx=(0, 8))

        controls = ctk.CTkFrame(row, fg_color="transparent")
        controls.grid(row=0, column=2, sticky="e", padx=(4, 5))

        self._small_button(
            controls,
            "↑",
            lambda: self._move_item(index, -1),
            disabled=index == 0,
        ).grid(row=0, column=0, padx=1)

        self._small_button(
            controls,
            "↓",
            lambda: self._move_item(index, 1),
            disabled=index >= total_items - 1,
        ).grid(row=0, column=1, padx=1)

        single = bool(definition.get("single", False))

        self._small_button(
            controls,
            "−",
            lambda: self._change_count(index, -1),
            disabled=single or count <= 1,
        ).grid(row=0, column=2, padx=(7, 1))

        ctk.CTkLabel(
            controls,
            text=str(count),
            width=24,
            font=Fonts.SMALL,
            text_color=self.INK,
        ).grid(row=0, column=3)

        self._small_button(
            controls,
            "+",
            lambda: self._change_count(index, 1),
            disabled=single,
        ).grid(row=0, column=4, padx=1)

        done_var = ctk.BooleanVar(value=done)
        ctk.CTkCheckBox(
            controls,
            text="Fait",
            width=52,
            checkbox_width=16,
            checkbox_height=16,
            variable=done_var,
            font=Fonts.SMALL,
            text_color=self.INK,
            fg_color=self.CELADON,
            hover_color=self.DONE,
            command=lambda: self._set_done(index, done_var.get()),
        ).grid(row=0, column=5, padx=(7, 3))

        ctk.CTkButton(
            controls,
            text="×",
            width=24,
            height=24,
            corner_radius=6,
            fg_color=self.GROUP_BG,
            hover_color="#F3E4E1",
            text_color=self.DANGER,
            border_width=1,
            border_color="#E0B9B0",
            font=Fonts.NORMAL,
            command=lambda: self._remove_item(index),
        ).grid(row=0, column=6, padx=(3, 0))

        return row

    def _small_button(
        self,
        parent,
        text: str,
        command,
        disabled: bool = False,
    ) -> ctk.CTkButton:
        return ctk.CTkButton(
            parent,
            text=text,
            width=24,
            height=24,
            corner_radius=6,
            fg_color=self.GROUP_BG,
            hover_color=Colors.BUTTON_HOVER,
            text_color=self.INK,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.SMALL,
            state="disabled" if disabled else "normal",
            command=command,
        )

    def _open_preview(self) -> None:
        if self._preview_window is not None:
            try:
                if self._preview_window.winfo_exists():
                    self._preview_window.focus_force()
                    self._preview_window.lift()
                    return
            except Exception:
                self._preview_window = None

        window = ctk.CTkToplevel(self.parent)
        self._preview_window = window
        window.title("Projet envisagé")
        window.geometry("1000x720")
        window.minsize(800, 560)
        window.configure(fg_color=self.WINDOW_BG)
        window.protocol("WM_DELETE_WINDOW", self._close_preview)
        window.grid_columnconfigure(0, weight=1)
        window.grid_rowconfigure(2, weight=1)
        window.bind("<Left>", lambda _event: self._show_previous_spread())
        window.bind("<Right>", lambda _event: self._show_next_spread())

        header = ctk.CTkFrame(window, fg_color="transparent", height=32)
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(6, 4))
        header.grid_columnconfigure(0, weight=1)
        header.grid_propagate(False)

        ctk.CTkLabel(
            header,
            text="Projet envisagé",
            font=Fonts.H2,
            text_color=self.INK,
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text=self._preview_summary_text(),
            font=Fonts.SMALL,
            text_color=self.TEXT_MUTED,
        ).grid(row=0, column=1, sticky="e")

        ribbon = ctk.CTkFrame(
            window,
            fg_color=self.RIBBON_BG,
            corner_radius=0,
            height=104,
        )
        ribbon.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 8))
        ribbon.grid_propagate(False)

        def preview_group(title: str, width: int) -> tuple[ctk.CTkFrame, ctk.CTkFrame]:
            group = ctk.CTkFrame(
                ribbon,
                width=width,
                height=94,
                fg_color=self.GROUP_BG,
                corner_radius=10,
            )
            group.pack(side="left", fill="y", padx=(4, 1), pady=5)
            group.pack_propagate(False)

            controls = ctk.CTkFrame(group, fg_color="transparent")
            controls.pack(fill="both", expand=True, padx=5, pady=(5, 1))

            ctk.CTkLabel(
                group,
                text=title,
                font=Fonts.SMALL,
                text_color=self.TEXT_MUTED,
                height=18,
            ).pack(side="bottom", fill="x", pady=(0, 4))
            return group, controls

        def preview_button(
            parent_frame,
            icon: str,
            label: str,
            command,
            width: int = 70,
            accent: str | None = None,
        ) -> ctk.CTkButton:
            border = accent or self.BORDER
            text_color = accent or self.INK
            button = ctk.CTkButton(
                parent_frame,
                text=f"{icon}\n{label}",
                width=width,
                height=58,
                corner_radius=8,
                fg_color=self.GROUP_BG,
                hover_color=self.ACCENT_SOFT,
                text_color=text_color,
                border_width=1,
                border_color=border,
                font=(Fonts.FAMILY, 11),
                command=command,
            )
            button.pack(side="left", padx=2, pady=2)
            return button

        _, view_controls = preview_group("Vue", 164)
        self._preview_large_button = preview_button(
            view_controls,
            "▣",
            "Grande vue",
            lambda: self._set_preview_mode("large"),
            width=72,
            accent=self.SKY,
        )
        self._preview_overview_button = preview_button(
            view_controls,
            "▦",
            "Ensemble",
            lambda: self._set_preview_mode("overview"),
            width=72,
            accent=self.LILAC,
        )

        _, navigation_controls = preview_group("Navigation", 164)
        self._preview_previous_button = preview_button(
            navigation_controls,
            "◀",
            "Précédent",
            self._show_previous_spread,
            width=72,
        )
        self._preview_next_button = preview_button(
            navigation_controls,
            "▶",
            "Suivant",
            self._show_next_spread,
            width=72,
        )

        _, window_controls = preview_group("Fenêtre", 88)
        preview_button(
            window_controls,
            "×",
            "Fermer",
            self._close_preview,
            width=68,
            accent=self.CORAL,
        )

        self._preview_body = ctk.CTkFrame(
            window,
            fg_color=self.CANVAS_BG,
            corner_radius=8,
            border_width=1,
            border_color=self.BORDER,
        )
        self._preview_body.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 5),
        )
        self._preview_body.grid_columnconfigure(0, weight=1)
        self._preview_body.grid_rowconfigure(0, weight=1)

        self._preview_nav = ctk.CTkFrame(
            window,
            fg_color=self.GROUP_BG,
            corner_radius=6,
            height=30,
            border_width=1,
            border_color=self.BORDER,
        )
        self._preview_nav.grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 8))
        self._preview_nav.grid_columnconfigure(0, weight=1)
        self._preview_nav.grid_propagate(False)

        self._preview_position_label = ctk.CTkLabel(
            self._preview_nav,
            text="",
            font=Fonts.SMALL,
            text_color=self.INK,
        )
        self._preview_position_label.grid(row=0, column=0)

        self._preview_spreads = self._build_preview_spreads(list(self._items()))
        self._preview_index = 0
        self._set_preview_mode("large")
        window.after(100, window.focus_force)

    def _close_preview(self) -> None:
        if self._preview_window is not None:
            try:
                self._preview_window.destroy()
            except Exception:
                pass

        self._preview_window = None
        self._preview_body = None
        self._preview_nav = None
        self._preview_position_label = None
        self._preview_previous_button = None
        self._preview_next_button = None
        self._preview_large_button = None
        self._preview_overview_button = None
        self._preview_spreads = []
        self._preview_index = 0

    def _set_preview_mode(self, mode: str) -> None:
        if self._preview_body is None:
            return

        self._preview_mode = "overview" if mode == "overview" else "large"

        if self._preview_large_button is not None:
            active = self._preview_mode == "large"
            self._preview_large_button.configure(
                fg_color=self.ACCENT_SOFT if active else self.GROUP_BG,
                hover_color=self.ACCENT_SOFT,
                text_color=self.INK if active else self.SKY,
                border_color=self.INK if active else self.SKY,
            )

        if self._preview_overview_button is not None:
            active = self._preview_mode == "overview"
            self._preview_overview_button.configure(
                fg_color="#EEEAF5" if active else self.GROUP_BG,
                hover_color="#EEEAF5",
                text_color=self.INK if active else self.LILAC,
                border_color=self.INK if active else self.LILAC,
            )

        for child in self._preview_body.winfo_children():
            child.destroy()

        if self._preview_mode == "overview":
            if self._preview_nav is not None:
                self._preview_nav.grid_remove()
            self._render_preview_overview()
        else:
            if self._preview_nav is not None:
                self._preview_nav.grid()
            self._render_preview_current_spread()

    def _build_preview_spreads(
        self,
        items: list[dict[str, Any]],
    ) -> list[
        tuple[
            dict[str, Any] | None,
            dict[str, Any] | None,
            int | None,
            int | None,
        ]
    ]:
        spreads: list[
            tuple[
                dict[str, Any] | None,
                dict[str, Any] | None,
                int | None,
                int | None,
            ]
        ] = []

        covers = [item for item in items if item.get("type") == "couverture"]
        fourths = [item for item in items if item.get("type") == "quatrieme"]
        interiors = [
            item
            for item in items
            if item.get("type") not in {"couverture", "quatrieme"}
        ]

        if covers:
            spreads.append((None, covers[0], None, None))

        expanded_pages: list[dict[str, Any]] = []
        for item in interiors:
            count = max(1, int(item.get("count", 1)))
            expanded_pages.extend([item] * count)

        index = 0
        page_number = 1
        while index < len(expanded_pages):
            left_item = expanded_pages[index]
            left_number = page_number
            index += 1
            page_number += 1

            right_item: dict[str, Any] | None = None
            right_number: int | None = None
            if index < len(expanded_pages):
                right_item = expanded_pages[index]
                right_number = page_number
                index += 1
                page_number += 1

            spreads.append(
                (left_item, right_item, left_number, right_number)
            )

        if fourths:
            spreads.append((fourths[-1], None, None, None))

        return spreads

    def _render_preview_current_spread(self) -> None:
        if self._preview_body is None:
            return

        for child in self._preview_body.winfo_children():
            child.destroy()

        if not self._preview_spreads:
            ctk.CTkLabel(
                self._preview_body,
                text="Aucune page.",
                font=Fonts.NORMAL,
                text_color=self.TEXT_LIGHT,
            ).grid(row=0, column=0)
            self._update_preview_navigation()
            return

        self._preview_index = max(
            0,
            min(self._preview_index, len(self._preview_spreads) - 1),
        )
        left_item, right_item, left_number, right_number = (
            self._preview_spreads[self._preview_index]
        )

        spread = ctk.CTkFrame(
            self._preview_body,
            fg_color="transparent",
            corner_radius=0,
        )
        spread.grid(row=0, column=0)
        spread.grid_columnconfigure(0, weight=1)
        spread.grid_columnconfigure(1, weight=1)

        self._create_preview_large_page(
            spread,
            left_item,
            left_number,
        ).grid(row=0, column=0, padx=(8, 5), pady=16)

        self._create_preview_large_page(
            spread,
            right_item,
            right_number,
        ).grid(row=0, column=1, padx=(5, 8), pady=16)

        self._update_preview_navigation()

    def _create_preview_large_page(
        self,
        parent,
        item: dict[str, Any] | None,
        page_number: int | None = None,
    ) -> ctk.CTkFrame:
        if item is None:
            empty = ctk.CTkFrame(
                parent,
                width=300,
                height=420,
                fg_color="transparent",
                corner_radius=0,
            )
            empty.grid_propagate(False)
            return empty

        definition = self._definition_for(str(item.get("type", "autre")))
        done = bool(item.get("done", False))
        accent = str(definition.get("accent", self.INK))

        page = ctk.CTkFrame(
            parent,
            width=300,
            height=420,
            fg_color=definition["color"],
            corner_radius=7,
            border_width=2 if done else 1,
            border_color=self.DONE if done else accent,
        )
        page.grid_propagate(False)
        page.grid_columnconfigure(0, weight=1)
        page.grid_rowconfigure(2, weight=1)

        band = ctk.CTkFrame(
            page,
            height=8,
            fg_color=self.DONE if done else accent,
            corner_radius=4,
        )
        band.grid(row=0, column=0, sticky="ew", padx=7, pady=(7, 0))
        band.grid_propagate(False)

        if done:
            ctk.CTkLabel(
                page,
                text="✓ Fait",
                font=Fonts.SMALL,
                text_color=self.DONE,
            ).grid(row=1, column=0, sticky="ne", padx=12, pady=(7, 0))

        center = ctk.CTkFrame(page, fg_color="transparent")
        center.grid(row=2, column=0)

        ctk.CTkLabel(
            center,
            text=str(definition["symbol"]),
            font=(Fonts.FAMILY, 52, "bold"),
            text_color=accent,
        ).pack(pady=(0, 16))

        ctk.CTkLabel(
            center,
            text=str(item.get("title") or definition["title"]),
            font=Fonts.H2,
            text_color=self.INK,
            wraplength=245,
            justify="center",
        ).pack(padx=16)

        if page_number is not None:
            ctk.CTkLabel(
                page,
                text=f"Page {page_number}",
                font=Fonts.NORMAL,
                text_color=self.TEXT_MUTED,
            ).grid(row=3, column=0, pady=(0, 12))

        return page

    def _show_previous_spread(self) -> None:
        if self._preview_mode != "large" or self._preview_index <= 0:
            return
        self._preview_index -= 1
        self._render_preview_current_spread()

    def _show_next_spread(self) -> None:
        if (
            self._preview_mode != "large"
            or self._preview_index >= len(self._preview_spreads) - 1
        ):
            return
        self._preview_index += 1
        self._render_preview_current_spread()

    def _update_preview_navigation(self) -> None:
        total = len(self._preview_spreads)

        if self._preview_previous_button is not None:
            self._preview_previous_button.configure(
                state="normal" if self._preview_index > 0 else "disabled"
            )

        if self._preview_next_button is not None:
            self._preview_next_button.configure(
                state=(
                    "normal"
                    if self._preview_index < total - 1
                    else "disabled"
                )
            )

        if self._preview_position_label is None:
            return

        if total == 0:
            self._preview_position_label.configure(text="0 / 0")
            return

        left_item, right_item, left_number, right_number = (
            self._preview_spreads[self._preview_index]
        )
        position = self._preview_spread_title(
            left_item,
            right_item,
            left_number,
            right_number,
        )
        self._preview_position_label.configure(
            text=f"{position}   ·   {self._preview_index + 1} / {total}"
        )

    @staticmethod
    def _preview_spread_title(
        left_item: dict[str, Any] | None,
        right_item: dict[str, Any] | None,
        left_number: int | None,
        right_number: int | None,
    ) -> str:
        if right_item is not None and right_item.get("type") == "couverture":
            return "Couverture"
        if left_item is not None and left_item.get("type") == "quatrieme":
            return "Quatrième"
        if left_number is not None and right_number is not None:
            return f"Pages {left_number}–{right_number}"
        if left_number is not None:
            return f"Page {left_number}"
        if right_number is not None:
            return f"Page {right_number}"
        return "Double page"

    def _render_preview_overview(self) -> None:
        if self._preview_body is None:
            return

        scroll = ctk.CTkScrollableFrame(
            self._preview_body,
            fg_color="transparent",
            corner_radius=0,
        )
        scroll.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        scroll.grid_columnconfigure(0, weight=1)

        if not self._preview_spreads:
            ctk.CTkLabel(
                scroll,
                text="Aucune page.",
                font=Fonts.NORMAL,
                text_color=self.TEXT_LIGHT,
            ).grid(row=0, column=0, padx=20, pady=30)
            return

        for row_number, spread in enumerate(self._preview_spreads):
            left_item, right_item, left_number, right_number = spread
            self._create_preview_spread(
                scroll,
                left_item=left_item,
                right_item=right_item,
                left_page_number=left_number,
                right_page_number=right_number,
            ).grid(row=row_number, column=0, pady=4)

    def _create_preview_spread(
        self,
        parent,
        left_item: dict[str, Any] | None,
        right_item: dict[str, Any] | None,
        left_page_number: int | None = None,
        right_page_number: int | None = None,
    ) -> ctk.CTkFrame:
        frame = ctk.CTkFrame(
            parent,
            width=300,
            height=126,
            fg_color=self.GROUP_BG,
            corner_radius=7,
            border_width=1,
            border_color=self.BORDER,
        )
        frame.grid_propagate(False)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        self._create_preview_page(
            frame,
            left_item,
            left_page_number,
        ).grid(row=0, column=0, padx=(8, 3), pady=7)

        self._create_preview_page(
            frame,
            right_item,
            right_page_number,
        ).grid(row=0, column=1, padx=(3, 8), pady=7)

        return frame

    def _create_preview_page(
        self,
        parent,
        item: dict[str, Any] | None,
        page_number: int | None = None,
    ) -> ctk.CTkFrame:
        if item is None:
            empty = ctk.CTkFrame(
                parent,
                width=132,
                height=110,
                fg_color=self.RIBBON_BG,
                corner_radius=5,
                border_width=1,
                border_color=self.BORDER,
            )
            empty.grid_propagate(False)
            return empty

        definition = self._definition_for(str(item.get("type", "autre")))
        done = bool(item.get("done", False))
        accent = str(definition.get("accent", self.INK))

        page = ctk.CTkFrame(
            parent,
            width=132,
            height=110,
            fg_color=definition["color"],
            corner_radius=5,
            border_width=2 if done else 1,
            border_color=self.DONE if done else accent,
        )
        page.grid_propagate(False)

        ctk.CTkFrame(
            page,
            height=5,
            fg_color=self.DONE if done else accent,
            corner_radius=3,
        ).pack(fill="x", padx=5, pady=(5, 2))

        ctk.CTkLabel(
            page,
            text=str(definition["symbol"]),
            font=(Fonts.FAMILY, 18, "bold"),
            text_color=accent,
        ).pack(pady=(4, 1))

        ctk.CTkLabel(
            page,
            text=str(item.get("title") or definition["title"]),
            font=Fonts.SMALL,
            text_color=self.INK,
            wraplength=112,
            justify="center",
        ).pack(padx=6)

        if page_number is not None:
            ctk.CTkLabel(
                page,
                text=f"p. {page_number}",
                font=(Fonts.FAMILY, 10),
                text_color=self.TEXT_MUTED,
            ).pack(side="bottom", pady=(1, 4))

        return page

    def _preview_summary_text(self) -> str:
        items = self._items()
        interior_pages = sum(
            max(1, int(item.get("count", 1)))
            for item in items
            if item.get("type") not in {"couverture", "quatrieme"}
        )
        cover_count = sum(
            1 for item in items if item.get("type") == "couverture"
        )
        fourth_count = sum(
            1 for item in items if item.get("type") == "quatrieme"
        )
        distinct_types = len({str(item.get("type", "autre")) for item in items})

        parts = [
            f"{interior_pages} page{'s' if interior_pages != 1 else ''} intérieures"
        ]
        if cover_count:
            parts.append("couverture")
        if fourth_count:
            parts.append("quatrième")
        parts.append(f"{distinct_types} type{'s' if distinct_types != 1 else ''}")
        return " · ".join(parts)


    # ==========================================================
    # Actions utilisateur
    # ==========================================================

    def _add_item(self, definition: dict[str, Any]) -> None:
        item = {
            "id": f"MAQUETTE-{uuid4().hex[:12].upper()}",
            "type": str(definition["type"]),
            "title": str(definition["title"]),
            "count": 1,
            "done": False,
        }
        self._items().append(item)
        self._save_data()
        self._refresh_sequence()

    def _move_item(self, index: int, delta: int) -> None:
        items = self._items()
        target = index + delta

        if not (0 <= index < len(items) and 0 <= target < len(items)):
            return

        items[index], items[target] = items[target], items[index]
        self._save_data()
        self._refresh_sequence()

    def _change_count(self, index: int, delta: int) -> None:
        items = self._items()
        if not 0 <= index < len(items):
            return

        definition = self._definition_for(items[index].get("type", "autre"))
        if definition.get("single"):
            return

        current = max(1, int(items[index].get("count", 1)))
        items[index]["count"] = max(1, min(9999, current + delta))
        self._save_data()
        self._refresh_sequence()

    def _set_done(self, index: int, done: bool) -> None:
        items = self._items()
        if not 0 <= index < len(items):
            return

        items[index]["done"] = bool(done)
        self._save_data()
        self._refresh_sequence()

    def _remove_item(self, index: int) -> None:
        items = self._items()
        if not 0 <= index < len(items):
            return

        del items[index]
        self._save_data()
        self._refresh_sequence()

    def _go_back(self) -> None:
        if self.on_back is not None:
            self.on_back()

    # ==========================================================
    # Données
    # ==========================================================

    def _items(self) -> list[dict[str, Any]]:
        items = self.data.setdefault("items", [])
        if not isinstance(items, list):
            items = []
            self.data["items"] = items
        return items

    def _load_data(self) -> dict[str, Any]:
        path = self._mockup_file()

        if not path.exists():
            data = self._empty_data()
            self._write_json(path, data)
            return data

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            data = self._empty_data()
            self._write_json(path, data)
            return data

        if not isinstance(data, dict):
            data = self._empty_data()

        items = data.get("items", [])
        if not isinstance(items, list):
            items = []

        data["version"] = 1
        data["items"] = [
            self._normalize_item(item)
            for item in items
            if isinstance(item, dict)
        ]
        data.setdefault("created_at", datetime.now().isoformat())
        data.setdefault("updated_at", datetime.now().isoformat())

        return data

    def _save_data(self) -> None:
        self.data["version"] = 1
        self.data["updated_at"] = datetime.now().isoformat()
        self._write_json(self._mockup_file(), self.data)

    def _mockup_file(self) -> Path:
        configured = getattr(self.project, "mockup_file", None)
        if configured is not None:
            return Path(configured)

        root = getattr(self.project, "root", None)
        if root is None:
            raise RuntimeError("Aucun projet n’est chargé.")

        return Path(root) / "maquettage" / "premaquette.json"

    @staticmethod
    def _empty_data() -> dict[str, Any]:
        now = datetime.now().isoformat()
        return {
            "version": 1,
            "created_at": now,
            "updated_at": now,
            "items": [],
        }

    @classmethod
    def _normalize_item(cls, item: dict[str, Any]) -> dict[str, Any]:
        page_type = str(item.get("type", "autre"))
        definition = cls._definition_for(page_type)
        count = item.get("count", 1)

        try:
            normalized_count = max(1, int(count))
        except (TypeError, ValueError):
            normalized_count = 1

        if definition.get("single"):
            normalized_count = 1

        return {
            "id": str(item.get("id") or f"MAQUETTE-{uuid4().hex[:12].upper()}"),
            "type": page_type,
            "title": str(item.get("title") or definition["title"]),
            "count": normalized_count,
            "done": bool(item.get("done", False)),
        }

    @staticmethod
    def _write_json(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")

        with temporary.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        temporary.replace(path)

    # ==========================================================
    # Résumé et utilitaires
    # ==========================================================

    def _update_summary(self) -> None:
        items = self._items()
        total_pages = sum(max(1, int(item.get("count", 1))) for item in items)
        done_pages = sum(
            max(1, int(item.get("count", 1)))
            for item in items
            if bool(item.get("done", False))
        )
        distinct_types = len({str(item.get("type", "autre")) for item in items})

        if self._summary_label is not None:
            self._summary_label.configure(
                text=(
                    f"{total_pages} p. · "
                    f"{distinct_types} type{'s' if distinct_types != 1 else ''}"
                )
            )

        if self._progress_label is not None:
            self._progress_label.configure(
                text=(f"Fait : {done_pages}/{total_pages}" if total_pages else "")
            )

    @classmethod
    def _definition_for(cls, page_type: str) -> dict[str, Any]:
        for definition in cls.PAGE_LIBRARY:
            if definition["type"] == page_type:
                return definition
        return cls.PAGE_LIBRARY[-1]

    def _clear_parent(self) -> None:
        for child in self.parent.winfo_children():
            child.destroy()

    @staticmethod
    def _darken_color(color: str, amount: float) -> str:
        value = color.lstrip("#")
        if len(value) != 6:
            return color

        red = int(value[0:2], 16)
        green = int(value[2:4], 16)
        blue = int(value[4:6], 16)
        factor = max(0.0, min(1.0, 1.0 - amount))

        return f"#{int(red * factor):02X}{int(green * factor):02X}{int(blue * factor):02X}"

    def __repr__(self) -> str:
        return f"MockupView(project={getattr(self.project, 'name', '')!r})"