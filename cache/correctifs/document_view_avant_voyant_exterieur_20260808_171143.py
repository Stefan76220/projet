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

        # CENTRE_REGULATION_V1
        # Le ruban permanent assure seul la navigation. Le reste de la page
        # devient le poste de régulation du projet.
        root = ctk.CTkFrame(
            self.parent,
            fg_color=self.WINDOW_BG,
            corner_radius=0,
        )
        root.grid_columnconfigure(0, weight=1)
        root.grid_rowconfigure(1, weight=1)

        navigation = self._create_internal_navigation_ribbon(root)
        navigation.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=(5, 3),
        )

        main_workspace = self._create_main_workspace(root)
        main_workspace.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 8),
        )

        root.update_idletasks()
        root.pack(fill="both", expand=True)
        root.lift()

    def _create_internal_navigation_ribbon(
        self,
        parent,
    ) -> ctk.CTkFrame:
        """Bandeau décoratif permanent de navigation PageMaître.

        V6 :
        - aucun fond de widget derrière les icônes ;
        - tout est dessiné directement sur un seul Canvas ;
        - le décor PageMaître est donc visible sous les icônes ;
        - Accueil précède Centre dans le parcours ;
        - le nom de la page est intégré au ruban.
        """
        ribbon = ctk.CTkFrame(
            parent,
            height=98,
            fg_color="transparent",
            corner_radius=0,
            border_width=0,
        )
        ribbon.grid_propagate(False)
        ribbon.grid_columnconfigure(0, weight=1)
        ribbon.grid_rowconfigure(0, weight=1)

        canvas = tk.Canvas(
            ribbon,
            background=self.WINDOW_BG,
            borderwidth=0,
            highlightthickness=0,
            takefocus=False,
            cursor="arrow",
        )
        canvas.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        ribbon._nav_background_photo = None
        ribbon._nav_click_regions = []

        background_path = (
            Path(__file__).resolve().parents[3]
            / "assets"
            / "interface"
            / "backgrounds"
            / "editorial_bg_accueil.png"
        )

        def hex_to_rgb(value: str) -> tuple[int, int, int]:
            value = value.lstrip("#")
            return tuple(
                int(value[index:index + 2], 16)
                for index in (0, 2, 4)
            )

        def draw_icon(
            kind: str,
            cx: float,
            cy: float,
            color: str,
        ) -> None:
            """Dessine une icône directement sur le décor, sans fond."""
            stroke = color
            # CORRECTION_ICÔNES_CANVAS_V6
            # Éclaircissement local de la couleur, sans dépendre d'une
            # méthode utilitaire externe au bandeau.
            rgb = hex_to_rgb(color)
            soft_rgb = tuple(
                int(round(channel + (255 - channel) * 0.35))
                for channel in rgb
            )
            soft = "#{:02X}{:02X}{:02X}".format(*soft_rgb)
            w = 2

            if kind == "door":
                # Accueil : porte + flèche de retour.
                canvas.create_rectangle(
                    cx - 7, cy - 10,
                    cx + 6, cy + 10,
                    outline=stroke,
                    width=w,
                )
                canvas.create_line(
                    cx - 14, cy,
                    cx - 4, cy,
                    fill=stroke,
                    width=w,
                    arrow=tk.LAST,
                    arrowshape=(7, 8, 3),
                )
                canvas.create_oval(
                    cx + 2, cy - 1,
                    cx + 4, cy + 1,
                    fill=stroke,
                    outline=stroke,
                )

            elif kind == "eye":
                canvas.create_arc(
                    cx - 15, cy - 8,
                    cx + 15, cy + 8,
                    start=200,
                    extent=140,
                    style=tk.ARC,
                    outline=stroke,
                    width=w,
                )
                canvas.create_arc(
                    cx - 15, cy - 8,
                    cx + 15, cy + 8,
                    start=20,
                    extent=140,
                    style=tk.ARC,
                    outline=stroke,
                    width=w,
                )
                canvas.create_oval(
                    cx - 5, cy - 5,
                    cx + 5, cy + 5,
                    outline=stroke,
                    width=w,
                )
                canvas.create_oval(
                    cx - 1.5, cy - 1.5,
                    cx + 1.5, cy + 1.5,
                    fill=stroke,
                    outline=stroke,
                )

            elif kind == "sprout":
                canvas.create_line(
                    cx, cy + 11,
                    cx, cy - 3,
                    fill=stroke,
                    width=w,
                )
                canvas.create_arc(
                    cx - 12, cy - 10,
                    cx, cy + 1,
                    start=180,
                    extent=170,
                    style=tk.ARC,
                    outline=stroke,
                    width=w,
                )
                canvas.create_line(
                    cx - 9, cy - 7,
                    cx, cy - 1,
                    fill=soft,
                    width=1,
                )
                canvas.create_arc(
                    cx, cy - 12,
                    cx + 12, cy,
                    start=10,
                    extent=170,
                    style=tk.ARC,
                    outline=stroke,
                    width=w,
                )
                canvas.create_line(
                    cx, cy - 2,
                    cx + 9, cy - 8,
                    fill=soft,
                    width=1,
                )

            elif kind == "home":
                # Centre : maison, comme dans la proposition visuelle validée.
                canvas.create_line(
                    cx - 11, cy - 1,
                    cx, cy - 11,
                    cx + 11, cy - 1,
                    fill=stroke,
                    width=w,
                    joinstyle=tk.ROUND,
                )
                canvas.create_rectangle(
                    cx - 8, cy - 1,
                    cx + 8, cy + 11,
                    outline=stroke,
                    width=w,
                )
                canvas.create_rectangle(
                    cx - 2.5, cy + 4,
                    cx + 2.5, cy + 11,
                    outline=soft,
                    width=1,
                )

            elif kind == "pencil":
                canvas.create_line(
                    cx - 9, cy + 9,
                    cx + 7, cy - 7,
                    fill=stroke,
                    width=3,
                )
                canvas.create_line(
                    cx + 5, cy - 9,
                    cx + 10, cy - 4,
                    fill=stroke,
                    width=2,
                )
                canvas.create_polygon(
                    cx - 11, cy + 11,
                    cx - 7, cy + 9,
                    cx - 9, cy + 7,
                    fill="",
                    outline=stroke,
                    width=1,
                )

            elif kind == "tools":
                canvas.create_line(
                    cx - 9, cy + 9,
                    cx + 8, cy - 8,
                    fill=stroke,
                    width=3,
                )
                canvas.create_line(
                    cx - 8, cy - 8,
                    cx + 9, cy + 9,
                    fill=stroke,
                    width=3,
                )
                canvas.create_rectangle(
                    cx - 12, cy + 7,
                    cx - 7, cy + 12,
                    outline=stroke,
                    width=1,
                )
                canvas.create_arc(
                    cx + 5, cy - 12,
                    cx + 12, cy - 5,
                    start=20,
                    extent=190,
                    style=tk.ARC,
                    outline=stroke,
                    width=2,
                )

            elif kind == "quill":
                canvas.create_arc(
                    cx - 8, cy - 12,
                    cx + 11, cy + 8,
                    start=120,
                    extent=190,
                    style=tk.ARC,
                    outline=stroke,
                    width=w,
                )
                canvas.create_line(
                    cx - 9, cy + 11,
                    cx + 7, cy - 7,
                    fill=stroke,
                    width=w,
                )
                canvas.create_line(
                    cx - 2, cy + 4,
                    cx + 6, cy + 3,
                    fill=soft,
                    width=1,
                )
                canvas.create_line(
                    cx + 2, cy,
                    cx + 8, cy - 2,
                    fill=soft,
                    width=1,
                )

            elif kind == "puzzle":
                points = (
                    cx - 10, cy - 8,
                    cx - 3, cy - 8,
                    cx - 3, cy - 11,
                    cx, cy - 13,
                    cx + 3, cy - 11,
                    cx + 3, cy - 8,
                    cx + 10, cy - 8,
                    cx + 10, cy - 1,
                    cx + 7, cy - 1,
                    cx + 5, cy + 2,
                    cx + 7, cy + 5,
                    cx + 10, cy + 5,
                    cx + 10, cy + 10,
                    cx - 10, cy + 10,
                    cx - 10, cy + 3,
                    cx - 7, cy + 3,
                    cx - 5, cy,
                    cx - 7, cy - 3,
                    cx - 10, cy - 3,
                )
                canvas.create_line(
                    *points,
                    cx - 10, cy - 8,
                    fill=stroke,
                    width=w,
                    joinstyle=tk.ROUND,
                )

            elif kind == "verify":
                canvas.create_oval(
                    cx - 11, cy - 11,
                    cx + 5, cy + 5,
                    outline=stroke,
                    width=w,
                )
                canvas.create_line(
                    cx + 3, cy + 3,
                    cx + 12, cy + 12,
                    fill=stroke,
                    width=3,
                )
                canvas.create_line(
                    cx - 7, cy - 2,
                    cx - 3, cy + 2,
                    cx + 2, cy - 5,
                    fill=soft,
                    width=2,
                )

            elif kind == "flag":
                canvas.create_line(
                    cx - 7, cy - 12,
                    cx - 7, cy + 12,
                    fill=stroke,
                    width=w,
                )
                canvas.create_line(
                    cx - 7, cy - 10,
                    cx + 7, cy - 8,
                    cx + 3, cy - 3,
                    cx + 8, cy + 1,
                    cx - 7, cy,
                    fill=stroke,
                    width=w,
                    joinstyle=tk.ROUND,
                )

            elif kind == "close":
                canvas.create_line(
                    cx - 8, cy - 8,
                    cx + 8, cy + 8,
                    fill=stroke,
                    width=3,
                )
                canvas.create_line(
                    cx + 8, cy - 8,
                    cx - 8, cy + 8,
                    fill=stroke,
                    width=3,
                )

        def build_background(width: int, height: int):
            try:
                from PIL import Image, ImageDraw
            except Exception:
                return None

            if background_path.is_file():
                try:
                    source = Image.open(background_path).convert("RGBA")

                    # Important : on garde tout le dessin du fond général.
                    # On le comprime en hauteur au lieu de recadrer sa zone
                    # centrale vide ; les références éditoriales restent donc
                    # visibles aux extrémités du ruban.
                    source = source.resize(
                        (width, height),
                        Image.Resampling.LANCZOS,
                    )

                    veil = Image.new(
                        "RGBA",
                        (width, height),
                        (255, 255, 255, 105),
                    )
                    image = Image.alpha_composite(source, veil)

                except Exception:
                    image = Image.new(
                        "RGBA",
                        (width, height),
                        (248, 247, 244, 255),
                    )
            else:
                image = Image.new(
                    "RGBA",
                    (width, height),
                    (248, 247, 244, 255),
                )

            # Quelques repères supplémentaires, strictement rectilignes.
            draw = ImageDraw.Draw(image)
            pale_blue = (117, 182, 219, 78)
            pale_teal = (130, 183, 161, 72)
            pale_lilac = (169, 151, 201, 66)
            pale_coral = (223, 128, 107, 65)

            y = height - 7
            draw.line(
                (18, y, width - 18, y),
                fill=(77, 96, 118, 48),
                width=1,
            )

            for x in (26, width // 2, width - 26):
                draw.line(
                    (x - 7, y, x + 7, y),
                    fill=pale_blue,
                    width=1,
                )
                draw.line(
                    (x, y - 7, x, y + 1),
                    fill=pale_blue,
                    width=1,
                )

            sx = 214
            for color in (
                pale_teal,
                pale_blue,
                pale_lilac,
                pale_coral,
            ):
                draw.rectangle(
                    (sx, y - 4, sx + 9, y),
                    outline=color,
                    width=1,
                )
                sx += 14

            return image

        def add_click_region(
            x1: float,
            x2: float,
            command,
            enabled: bool,
        ) -> None:
            if enabled and callable(command):
                ribbon._nav_click_regions.append(
                    (float(x1), float(x2), command)
                )

        def on_click(event) -> None:
            x = float(event.x)
            for x1, x2, command in ribbon._nav_click_regions:
                if x1 <= x <= x2:
                    command()
                    return

        canvas.bind("<Button-1>", on_click)

        def draw_item(
            *,
            cx: float,
            icon_kind: str,
            label: str,
            color: str,
            command=None,
            active: bool = False,
            enabled: bool = True,
            width: float = 86,
        ) -> None:
            # ETAPE_ACTIVE_DIFFUSE_V7
            # L'étape courante est un repère, pas un bouton :
            # elle est plus claire, non cliquable et reçoit un halo
            # tramé qui laisse réellement voir le décor principal.
            if active:
                rgb = hex_to_rgb(color)
                active_rgb = tuple(
                    int(round(channel + (255 - channel) * 0.30))
                    for channel in rgb
                )
                item_color = "#{:02X}{:02X}{:02X}".format(*active_rgb)

                halo_rgb = tuple(
                    int(round(channel + (255 - channel) * 0.72))
                    for channel in rgb
                )
                halo_color = "#{:02X}{:02X}{:02X}".format(*halo_rgb)

                canvas.create_oval(
                    cx - width * 0.43,
                    24,
                    cx + width * 0.43,
                    86,
                    fill=halo_color,
                    outline="",
                    stipple="gray25",
                )
            else:
                item_color = color if enabled else self.TEXT_LIGHT

            draw_icon(
                icon_kind,
                cx,
                45,
                item_color,
            )

            canvas.create_text(
                cx,
                69,
                text=label,
                fill=item_color,
                font=(
                    Fonts.FAMILY,
                    9,
                    "bold" if active else "normal",
                ),
                anchor="center",
            )

            if active:
                canvas.create_line(
                    cx - 16, 82,
                    cx + 16, 82,
                    fill=item_color,
                    width=2,
                )
            else:
                canvas.create_oval(
                    cx - 1.5, 81,
                    cx + 1.5, 84,
                    fill=item_color,
                    outline="",
                )

            # Une étape active n'est jamais cliquable, même si une
            # commande lui était attribuée par erreur plus tard.
            add_click_region(
                cx - width / 2,
                cx + width / 2,
                None if active else command,
                enabled and not active,
            )

        def redraw(_event=None) -> None:
            width = max(1, int(canvas.winfo_width()))
            height = max(1, int(canvas.winfo_height()))

            if width <= 2 or height <= 2:
                return

            canvas.delete("all")
            ribbon._nav_click_regions = []

            background = build_background(width, height)
            if background is not None:
                try:
                    from PIL import ImageTk

                    photo = ImageTk.PhotoImage(background)
                    ribbon._nav_background_photo = photo
                    canvas.create_image(
                        0,
                        0,
                        image=photo,
                        anchor="nw",
                    )
                except Exception:
                    pass

            # --------------------------------------------------
            # Titre de la page intégré au bandeau
            # --------------------------------------------------

            project_name = str(
                getattr(self.project, "name", "")
                or "Projet sans nom"
            )
            project_type = self._project_type_key()
            appearance = self.PROJECT_TYPE_APPEARANCES.get(
                project_type,
                self.PROJECT_TYPE_APPEARANCES["ouvrage_structure"],
            )

            canvas.create_text(
                20,
                10,
                text="Centre du projet",
                fill=self.INK,
                font=(Fonts.FAMILY, 11, "bold"),
                anchor="nw",
            )

            canvas.create_text(
                width - 20,
                11,
                text=f"{project_name}  ·  {appearance['label']}",
                fill=self.TEXT_MUTED,
                font=(Fonts.FAMILY, 8),
                anchor="ne",
            )

            # --------------------------------------------------
            # Gauche : accès permanents
            # --------------------------------------------------

            draw_item(
                cx=78,
                icon_kind="eye",
                label="Visualisation",
                color=self.LILAC,
                enabled=False,
                width=104,
            )

            draw_item(
                cx=190,
                icon_kind="sprout",
                label="Suivi du livre",
                color=self.CELADON,
                enabled=False,
                width=106,
            )

            # Séparation discrète avant le parcours.
            canvas.create_line(
                252, 30,
                252, 78,
                fill="#D7DEE4",
                width=1,
            )

            # --------------------------------------------------
            # Centre : Accueil puis parcours
            # --------------------------------------------------

            steps = (
                (
                    "door",
                    "Accueil",
                    self.NAVY,
                    self._return_home,
                    False,
                    True,
                    72,
                ),
                (
                    "home",
                    "Centre",
                    self.NAVY,
                    None,
                    True,
                    True,
                    72,
                ),
                (
                    "pencil",
                    "Maquettage",
                    self.MAQUETTAGE,
                    self._open_mockup,
                    False,
                    True,
                    92,
                ),
                (
                    "tools",
                    "Atelier",
                    self.ATELIER,
                    self._open_model_workshop,
                    False,
                    True,
                    76,
                ),
                (
                    "quill",
                    "Conception",
                    self.CONCEPTION,
                    self._open_atelier,
                    False,
                    True,
                    92,
                ),
                (
                    "puzzle",
                    "Assemblage",
                    self.ASSEMBLAGE,
                    None,
                    False,
                    False,
                    94,
                ),
                (
                    "verify",
                    "Vérification",
                    self.VERIFICATION,
                    None,
                    False,
                    False,
                    94,
                ),
                (
                    "flag",
                    "Finalisation",
                    self.FINALISATION,
                    None,
                    False,
                    False,
                    90,
                ),
            )

            total_width = sum(step[6] for step in steps)
            total_width += max(0, len(steps) - 1) * 2

            available_left = 278
            available_right = width - 100
            available_width = max(
                total_width,
                available_right - available_left,
            )
            flow_left = (
                available_left
                + max(0, (available_width - total_width) / 2)
            )

            cursor = flow_left

            for step in steps:
                (
                    icon_kind,
                    label,
                    color,
                    command,
                    active,
                    enabled,
                    item_width,
                ) = step

                cx = cursor + item_width / 2

                draw_item(
                    cx=cx,
                    icon_kind=icon_kind,
                    label=label,
                    color=color,
                    command=command,
                    active=active,
                    enabled=enabled,
                    width=item_width,
                )

                cursor += item_width + 2

            # --------------------------------------------------
            # Droite : Fermer
            # --------------------------------------------------

            canvas.create_line(
                width - 88, 30,
                width - 88, 78,
                fill="#D7DEE4",
                width=1,
            )

            draw_item(
                cx=width - 43,
                icon_kind="close",
                label="Fermer",
                color=self.CORAL,
                command=self._return_home,
                enabled=True,
                width=76,
            )

        canvas.bind(
            "<Configure>",
            redraw,
            add="+",
        )
        canvas.after_idle(redraw)

        return ribbon

    def _create_header(self, parent) -> ctk.CTkFrame:
        """Contexte du Centre, sous le bandeau permanent."""
        frame = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            height=30,
        )
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_propagate(False)

        ctk.CTkLabel(
            frame,
            text="Centre du projet",
            font=Fonts.H2,
            text_color=self.INK,
        ).grid(row=0, column=0, sticky="w")

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
            height=22,
            corner_radius=11,
            fg_color=appearance["soft"],
            text_color=appearance["color"],
            border_width=1,
            border_color=appearance["color"],
            font=(Fonts.FAMILY, 8, "bold"),
            padx=9,
        )
        badge.grid(row=0, column=1, sticky="e", padx=(12, 8))

        ctk.CTkLabel(
            frame,
            text=project_name,
            font=Fonts.SMALL,
            text_color=self.TEXT_MUTED,
        ).grid(row=0, column=2, sticky="e", padx=(0, 2))

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

    def _load_regulation_snapshot(self) -> dict:
        """Source commune du Centre et de la future fenêtre Visualisation."""
        snapshot = {
            "items": [],
            "page_types": {},
            "groups": {},
            "updated_at": "",
            "planned_pages": 0,
            "automatic_pages": 0,
            "produced_pages": len(self.pages),
            "validated_pages": sum(
                1
                for page in self.pages
                if "valid" in self._page_state(page).casefold()
            ),
        }

        if self._project_type_key() != "ouvrage_structure":
            return snapshot

        configured = getattr(self.project, "mockup_file", None)
        if configured is not None:
            path = Path(configured)
        else:
            root = getattr(self.project, "root", None)
            if root is None:
                return snapshot
            path = Path(root) / "maquettage" / "premaquette.json"

        if not path.exists():
            return snapshot

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return snapshot

        if not isinstance(data, dict):
            return snapshot

        items = data.get("items", [])
        page_types = data.get("page_types", [])
        groups = data.get("groups", [])

        if not isinstance(items, list):
            items = []
        if not isinstance(page_types, list):
            page_types = []
        if not isinstance(groups, list):
            groups = []

        snapshot["items"] = [
            item for item in items if isinstance(item, dict)
        ]
        snapshot["page_types"] = {
            str(definition.get("type", "")): definition
            for definition in page_types
            if isinstance(definition, dict)
            and str(definition.get("type", ""))
        }
        snapshot["groups"] = {
            str(group.get("id", "")): group
            for group in groups
            if isinstance(group, dict)
            and str(group.get("id", ""))
        }
        snapshot["updated_at"] = str(data.get("updated_at", ""))

        def count_of(item: dict) -> int:
            try:
                return max(1, int(item.get("count", 1) or 1))
            except (TypeError, ValueError):
                return 1

        snapshot["planned_pages"] = sum(
            count_of(item) for item in snapshot["items"]
        )
        snapshot["automatic_pages"] = sum(
            count_of(item)
            for item in snapshot["items"]
            if bool(item.get("automatic_recto_verso", False))
        )

        return snapshot

    def _create_main_workspace(self, parent) -> ctk.CTkFrame:
        # CENTRE_VISUALISATION_DOUBLE_PAGE_V2
        workspace = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            corner_radius=0,
        )
        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_columnconfigure(1, weight=0, minsize=314)
        workspace.grid_rowconfigure(0, weight=1)

        snapshot = self._load_regulation_snapshot()

        wall_shell = ctk.CTkFrame(
            workspace,
            fg_color="transparent",
            corner_radius=0,
        )
        wall_shell.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 7),
        )
        wall_shell.grid_columnconfigure(0, weight=1)
        wall_shell.grid_rowconfigure(0, weight=1)

        wall = tk.Canvas(
            wall_shell,
            background=self.WINDOW_BG,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.BORDER,
            cursor="arrow",
        )
        wall.grid(row=0, column=0, sticky="nsew")

        scrollbar = ctk.CTkScrollbar(
            wall_shell,
            orientation="vertical",
            command=wall.yview,
            width=11,
        )
        scrollbar.grid(
            row=0,
            column=1,
            sticky="ns",
            padx=(3, 0),
        )
        wall.configure(yscrollcommand=scrollbar.set)

        self._regulation_wall = wall
        wall._regulation_bg_photo = None
        # BULLE_TYPE_PAGE_V10
        wall._type_tooltip_after = None
        # MINIATURES_MAQUETTAGE_CENTRE_V5
        # Les PhotoImage des pages doivent rester référencées tant que
        # le Canvas les affiche.
        wall._page_thumb_photos = []

        background_path = (
            Path(__file__).resolve().parents[3]
            / "assets"
            / "interface"
            / "backgrounds"
            / "editorial_bg_accueil.png"
        )

        def blend(color: str, amount: float = 0.72) -> str:
            color = str(color or "").lstrip("#")
            try:
                rgb = [
                    int(color[index:index + 2], 16)
                    for index in (0, 2, 4)
                ]
            except (TypeError, ValueError):
                rgb = [117, 182, 219]

            mixed = [
                int(round(channel + (255 - channel) * amount))
                for channel in rgb
            ]
            return "#{:02X}{:02X}{:02X}".format(*mixed)

        def item_title(item: dict) -> str:
            page_type = str(item.get("type", ""))
            definition = snapshot["page_types"].get(page_type, {})
            return str(
                item.get("title")
                or definition.get("title")
                or page_type.replace("_", " ").title()
                or "Page"
            )

        def item_accent(item: dict) -> str:
            # PAGE_RESPIRATION_AUTO_V3
            # Une page automatique conserve la couleur de son groupe :
            # "automatique" décrit son origine, pas son identité graphique.
            group_id = str(
                item.get("plan_group")
                or item.get("group_id")
                or ""
            )
            group = snapshot["groups"].get(group_id, {})
            accent = str(
                group.get("accent")
                or group.get("color")
                or ""
            )
            if accent.startswith("#") and len(accent) == 7:
                return accent

            page_type = str(item.get("type", ""))
            definition = snapshot["page_types"].get(page_type, {})
            accent = str(
                definition.get("accent")
                or definition.get("color")
                or ""
            )
            if accent.startswith("#") and len(accent) == 7:
                return accent

            if page_type in {"couverture", "deuxieme_couverture"}:
                return "#E88972"
            if page_type in {"quatrieme", "troisieme_couverture"}:
                return "#7DB99D"

            return self.MAQUETTAGE

        def thumbnail_filename_for_type(page_type: str) -> str:
            mapping = {
                "couverture": "type_page_couverture.png",
                "deuxieme_couverture": "type_page_deuxieme_couverture.png",
                "page_titre": "type_page_titre.png",
                "sommaire": "type_page_sommaire.png",
                "avant_propos": "type_page_avant_propos.png",
                "chapitre": "type_page_chapitre.png",
                "fiche": "type_page_fiche.png",
                "texte": "type_page_texte.png",
                "illustration": "type_page_illustration.png",
                "transition": "type_page_transition.png",
                "page_blanche": "type_page_blanche.png",
                "conclusion": "type_page_conclusion.png",
                "troisieme_couverture": "type_page_troisieme_couverture.png",
                "quatrieme": "type_page_quatrieme_couverture.png",
            }
            return mapping.get(
                page_type,
                "type_page_personnalisee.png",
            )

        def thumbnail_path_for_item(item: dict) -> Path | None:
            page_type = str(item.get("type", ""))
            definition = snapshot["page_types"].get(page_type, {})

            # Les types personnalisés utilisent d'abord leur miniature
            # propre enregistrée par le Maquettage.
            if bool(definition.get("custom", False)):
                stored = str(
                    definition.get("thumbnail", "")
                ).strip()
                if stored:
                    path = Path(stored)
                    if not path.is_absolute():
                        project_root = getattr(
                            self.project,
                            "root",
                            None,
                        )
                        if project_root is not None:
                            path = Path(project_root) / path
                    if path.is_file():
                        return path

            library = (
                Path(__file__).resolve().parents[3]
                / "assets"
                / "page_thumbnails"
            )

            standard = (
                library
                / thumbnail_filename_for_type(page_type)
            )
            if standard.is_file():
                return standard

            generic = library / "type_page_personnalisee.png"
            return generic if generic.is_file() else None

        def type_code_for_item(item: dict) -> str:
            # CODE_TYPE_PAGE_V8
            # Code très court intégré au bandeau de couleur pour identifier
            # le type sans ajouter de cartouche ni de hauteur.
            page_type = str(item.get("type", ""))

            mapping = {
                "couverture": "COUV",
                "deuxieme_couverture": "2C",
                "page_titre": "TITRE",
                "sommaire": "SOM",
                "avant_propos": "AVP",
                "chapitre": "CHAP",
                "fiche": "FICHE",
                "texte": "TXT",
                "illustration": "ILL",
                "transition": "TRANS",
                "page_blanche": "BL",
                "conclusion": "CONCL",
                "troisieme_couverture": "3C",
                "quatrieme": "4C",
            }

            if page_type in mapping:
                return mapping[page_type]

            definition = snapshot["page_types"].get(page_type, {})
            short = str(
                definition.get("short")
                or definition.get("title")
                or page_type
                or "PAGE"
            ).strip()

            compact = "".join(
                character
                for character in short.upper()
                if character.isalnum()
            )

            return compact[:5] or "PAGE"

        def type_label_for_item(item: dict) -> str:
            page_type = str(item.get("type", ""))

            labels = {
                "couverture": "Couverture",
                "deuxieme_couverture": "Deuxième de couverture",
                "page_titre": "Page de titre",
                "sommaire": "Sommaire",
                "avant_propos": "Avant-propos",
                "chapitre": "Chapitre",
                "fiche": "Fiche",
                "texte": "Page de texte",
                "illustration": "Illustration",
                "transition": "Page de transition",
                "page_blanche": "Page blanche",
                "conclusion": "Conclusion",
                "troisieme_couverture": "Troisième de couverture",
                "quatrieme": "Quatrième de couverture",
            }

            if page_type in labels:
                return labels[page_type]

            definition = snapshot["page_types"].get(page_type, {})
            return str(
                definition.get("title")
                or definition.get("short")
                or page_type.replace("_", " ").title()
                or "Page"
            )

        def hide_type_tooltip() -> None:
            pending = getattr(
                wall,
                "_type_tooltip_after",
                None,
            )
            if pending is not None:
                try:
                    wall.after_cancel(pending)
                except tk.TclError:
                    pass
                wall._type_tooltip_after = None

            wall.delete("type_page_tooltip")

        def show_type_tooltip(
            event,
            item: dict,
        ) -> None:
            hide_type_tooltip()

            code = type_code_for_item(item)
            label = type_label_for_item(item)
            accent = item_accent(item)

            canvas_x = wall.canvasx(event.x)
            canvas_y = wall.canvasy(event.y)

            def display() -> None:
                wall._type_tooltip_after = None
                wall.delete("type_page_tooltip")

                text = f"{code}  ·  {label}"

                text_id = wall.create_text(
                    canvas_x + 14,
                    canvas_y - 15,
                    text=text,
                    fill=self.INK,
                    font=(Fonts.FAMILY, 8, "bold"),
                    anchor="sw",
                    tags=("type_page_tooltip",),
                )

                bbox = wall.bbox(text_id)
                if bbox is None:
                    return

                x1, y1, x2, y2 = bbox
                pad_x = 8
                pad_y = 5

                # Reste dans la zone visible lorsque le pointeur est près
                # du bord droit ou du haut.
                view_left = wall.canvasx(0)
                view_top = wall.canvasy(0)
                view_right = wall.canvasx(wall.winfo_width())
                view_bottom = wall.canvasy(wall.winfo_height())

                shift_x = 0
                shift_y = 0

                if x2 + pad_x > view_right - 5:
                    shift_x = (view_right - 5) - (x2 + pad_x)
                if x1 - pad_x < view_left + 5:
                    shift_x = (view_left + 5) - (x1 - pad_x)

                if y1 - pad_y < view_top + 5:
                    shift_y = (view_top + 5) - (y1 - pad_y)
                if y2 + pad_y > view_bottom - 5:
                    shift_y = (view_bottom - 5) - (y2 + pad_y)

                if shift_x or shift_y:
                    wall.move(
                        text_id,
                        shift_x,
                        shift_y,
                    )
                    bbox = wall.bbox(text_id)
                    if bbox is None:
                        return
                    x1, y1, x2, y2 = bbox

                shadow = wall.create_rectangle(
                    x1 - pad_x + 2,
                    y1 - pad_y + 2,
                    x2 + pad_x + 2,
                    y2 + pad_y + 2,
                    fill="#D7DBD8",
                    outline="",
                    tags=("type_page_tooltip",),
                )

                bubble = wall.create_rectangle(
                    x1 - pad_x,
                    y1 - pad_y,
                    x2 + pad_x,
                    y2 + pad_y,
                    fill="#FFFDFC",
                    outline=accent,
                    width=1,
                    tags=("type_page_tooltip",),
                )

                wall.tag_lower(shadow, bubble)
                wall.tag_raise(text_id, bubble)

            wall._type_tooltip_after = wall.after(
                320,
                display,
            )

        def expand_items() -> list[dict]:
            expanded: list[dict] = []

            for source_index, item in enumerate(snapshot["items"]):
                try:
                    count = max(1, int(item.get("count", 1) or 1))
                except (TypeError, ValueError):
                    count = 1

                for occurrence in range(count):
                    clone = dict(item)
                    clone["_source_index"] = source_index
                    clone["_occurrence"] = occurrence + 1
                    clone["_occurrence_count"] = count
                    expanded.append(clone)

            return expanded

        physical_pages = expand_items()

        def page_status(item: dict) -> tuple[str, str]:
            # SYNOPTIQUE_VISUEL_EPURE_V7
            # La phase d'avancement est indépendante de la nature de la page.
            # Une page automatique reste donc "Maquettage" tant qu'elle
            # n'a pas progressé vers l'Atelier/Conception.
            return "Maquettage", self.MAQUETTAGE

        def make_background(width: int, height: int):
            try:
                from PIL import Image, ImageDraw
            except Exception:
                return None

            width = max(1, int(width))
            height = max(1, int(height))

            if background_path.is_file():
                try:
                    source = Image.open(background_path).convert("RGBA")
                    source_ratio = source.width / source.height
                    target_ratio = width / max(1, height)

                    if target_ratio > source_ratio:
                        rw = width
                        rh = max(height, int(round(width / source_ratio)))
                    else:
                        rh = height
                        rw = max(width, int(round(height * source_ratio)))

                    source = source.resize(
                        (rw, rh),
                        Image.Resampling.LANCZOS,
                    )

                    left = max(0, (rw - width) // 2)
                    top = max(0, (rh - height) // 2)
                    image = source.crop(
                        (left, top, left + width, top + height)
                    )

                    veil = Image.new(
                        "RGBA",
                        (width, height),
                        (255, 255, 255, 112),
                    )
                    image = Image.alpha_composite(image, veil)
                except Exception:
                    image = Image.new(
                        "RGBA",
                        (width, height),
                        (247, 247, 244, 255),
                    )
            else:
                image = Image.new(
                    "RGBA",
                    (width, height),
                    (247, 247, 244, 255),
                )

            draw = ImageDraw.Draw(image)
            line = (72, 92, 112, 34)
            blue = (117, 182, 219, 68)
            teal = (130, 183, 161, 58)

            draw.line(
                (22, height - 22, width - 22, height - 22),
                fill=line,
                width=1,
            )

            for x in (34, width // 2, max(34, width - 34)):
                draw.line(
                    (x - 8, height - 22, x + 8, height - 22),
                    fill=blue,
                    width=1,
                )
                draw.line(
                    (x, height - 30, x, height - 14),
                    fill=teal,
                    width=1,
                )

            return image

        def draw_page(
            x: float,
            y: float,
            item: dict,
            *,
            page_side: str,
            page_number: int | None,
            scale: float = 1.0,
        ) -> tuple[float, float]:
            automatic = bool(
                item.get("automatic_recto_verso", False)
            )

            nominal_w = 101 * scale
            nominal_h = 143 * scale

            visual_ratio = 0.90 if automatic else 1.0
            page_w = nominal_w * visual_ratio
            page_h = nominal_h * visual_ratio

            if automatic:
                x += (nominal_w - page_w) / 2
                y += (nominal_h - page_h) / 2

            accent = item_accent(item)
            phase_text, phase_color = page_status(item)

            tag = (
                f"visual_page_"
                f"{item.get('_source_index', 0)}_"
                f"{item.get('_occurrence', 1)}"
            )

            wall.create_rectangle(
                x,
                y,
                x + page_w,
                y + page_h,
                fill="#FFFDFC",
                outline=accent,
                width=1,
                tags=(tag,),
            )

            image_x1 = x + 1
            image_y1 = y + 1
            image_x2 = x + page_w - 1
            image_y2 = y + page_h - 1

            thumbnail_path = thumbnail_path_for_item(item)
            thumbnail_drawn = False

            if thumbnail_path is not None:
                try:
                    from PIL import Image, ImageTk

                    source = Image.open(thumbnail_path).convert("RGBA")
                    available_w = max(
                        1,
                        int(round(image_x2 - image_x1)),
                    )
                    available_h = max(
                        1,
                        int(round(image_y2 - image_y1)),
                    )

                    source = source.resize(
                        (available_w, available_h),
                        Image.Resampling.LANCZOS,
                    )

                    photo = ImageTk.PhotoImage(source)
                    wall._page_thumb_photos.append(photo)

                    wall.create_image(
                        image_x1,
                        image_y1,
                        image=photo,
                        anchor="nw",
                        tags=(tag,),
                    )
                    thumbnail_drawn = True
                except Exception:
                    thumbnail_drawn = False

            if not thumbnail_drawn:
                wall.create_rectangle(
                    image_x1,
                    image_y1,
                    image_x2,
                    image_y2,
                    fill=blend(accent, 0.90),
                    outline="",
                    tags=(tag,),
                )
                for index in range(5):
                    yy = image_y1 + 18 * scale + index * 12 * scale
                    wall.create_line(
                        image_x1 + 12 * scale,
                        yy,
                        image_x2 - 12 * scale,
                        yy,
                        fill=blend(accent, 0.48),
                        width=1,
                        tags=(tag,),
                    )

            # CODE_TYPE_PAGE_LISIBLE_V9
            # Bandeau légèrement plus haut pour une lecture immédiate
            # sans alourdir la miniature.
            band_h = 9 * scale
            wall.create_rectangle(
                x,
                y,
                x + page_w,
                y + band_h,
                fill=accent,
                outline="",
                tags=(tag,),
            )

            wall.create_text(
                x + 5 * scale,
                y + band_h / 2,
                text=type_code_for_item(item),
                fill="#FFFFFF",
                font=(
                    Fonts.FAMILY,
                    max(7, int(7.5 * scale)),
                    "bold",
                ),
                anchor="w",
                tags=(tag,),
            )

            if automatic:
                wall.create_text(
                    x + page_w - 5 * scale,
                    y + band_h / 2,
                    text="✦",
                    fill="#FFFFFF",
                    font=(
                        Fonts.FAMILY,
                        max(7, int(8 * scale)),
                        "bold",
                    ),
                    anchor="e",
                    tags=(tag,),
                )

            phase_y = y + page_h + 10 * scale
            dot_r = 2.7 * scale
            phase_center_x = x + page_w / 2
            estimated_text_w = 46 * scale
            dot_x = phase_center_x - estimated_text_w / 2

            wall.create_oval(
                dot_x - dot_r,
                phase_y - dot_r,
                dot_x + dot_r,
                phase_y + dot_r,
                fill=phase_color,
                outline="",
                tags=(tag,),
            )
            wall.create_text(
                dot_x + 7 * scale,
                phase_y,
                text=phase_text,
                fill=phase_color,
                font=(
                    Fonts.FAMILY,
                    max(6, int(7 * scale)),
                    "bold",
                ),
                anchor="w",
                tags=(tag,),
            )

            if page_number is not None:
                number_x = (
                    x
                    if page_side == "left"
                    else x + page_w
                )
                number_anchor = (
                    "nw"
                    if page_side == "left"
                    else "ne"
                )
                wall.create_text(
                    number_x,
                    phase_y + 9 * scale,
                    text=str(page_number),
                    fill=self.TEXT_MUTED,
                    font=(Fonts.FAMILY, max(6, int(7 * scale))),
                    anchor=number_anchor,
                    tags=(tag,),
                )

            # VOYANT_PAGE_OUVERTE_ATELIER_V1
            # Le voyant décrit un état de session, pas l'avancement :
            # il apparaît uniquement si le gabarit associé est réellement
            # chargé dans l'Atelier persistant.
            workshop = self._model_workshop_view
            active_model_id = (
                str(getattr(workshop, "active_model_id", "") or "")
                if workshop is not None
                else ""
            )
            associated_model_id = (
                self._associated_model_id_for_synoptic_item(item)
            )

            if (
                active_model_id
                and associated_model_id
                and active_model_id == associated_model_id
            ):
                activity_tag = f"{tag}_atelier_active"
                tab_x1 = x + page_w - 1
                tab_y1 = y + 31 * scale
                tab_x2 = x + page_w + 13 * scale
                tab_y2 = y + 56 * scale

                wall.create_rectangle(
                    tab_x1,
                    tab_y1,
                    tab_x2,
                    tab_y2,
                    fill=self.ATELIER,
                    outline="#FFFFFF",
                    width=1,
                    tags=(activity_tag,),
                )
                wall.create_text(
                    (tab_x1 + tab_x2) / 2,
                    (tab_y1 + tab_y2) / 2,
                    text="A",
                    fill="#FFFFFF",
                    font=(
                        Fonts.FAMILY,
                        max(7, int(8 * scale)),
                        "bold",
                    ),
                    anchor="center",
                    tags=(activity_tag,),
                )

                def show_atelier_activity_tip(event) -> None:
                    wall.delete("atelier_activity_tooltip")
                    cx = wall.canvasx(event.x) + 14
                    cy = wall.canvasy(event.y) - 12

                    text_id = wall.create_text(
                        cx,
                        cy,
                        text="Atelier · gabarit actuellement ouvert",
                        fill=self.INK,
                        font=(Fonts.FAMILY, 8, "bold"),
                        anchor="sw",
                        tags=("atelier_activity_tooltip",),
                    )
                    bbox = wall.bbox(text_id)
                    if bbox is None:
                        return

                    x1, y1, x2, y2 = bbox
                    bubble = wall.create_rectangle(
                        x1 - 8,
                        y1 - 5,
                        x2 + 8,
                        y2 + 5,
                        fill="#FFFDFC",
                        outline=self.ATELIER,
                        width=1,
                        tags=("atelier_activity_tooltip",),
                    )
                    wall.tag_lower(bubble, text_id)

                def hide_atelier_activity_tip(_event=None) -> None:
                    wall.delete("atelier_activity_tooltip")

                wall.tag_bind(
                    activity_tag,
                    "<Enter>",
                    show_atelier_activity_tip,
                )
                wall.tag_bind(
                    activity_tag,
                    "<Leave>",
                    hide_atelier_activity_tip,
                )
                wall.tag_bind(
                    activity_tag,
                    "<Button-1>",
                    lambda _evt, current_item=item: self._route_synoptic_page(
                        current_item
                    ),
                )

            # CIBLAGE_CENTRE_MAQUETTAGE_V1
            wall.tag_bind(
                tag,
                "<Button-1>",
                lambda _evt, current_item=item: self._route_synoptic_page(
                    current_item
                ),
            )
            def enter_page(
                event,
                current_item=item,
            ) -> None:
                wall.configure(cursor="hand2")
                show_type_tooltip(
                    event,
                    current_item,
                )

            def leave_page(_event) -> None:
                wall.configure(cursor="arrow")
                hide_type_tooltip()

            wall.tag_bind(
                tag,
                "<Enter>",
                enter_page,
            )
            wall.tag_bind(
                tag,
                "<Leave>",
                leave_page,
            )

            return page_w, page_h

        def make_display_units() -> list[dict]:
            units: list[dict] = []

            if not physical_pages:
                return units

            work = list(physical_pages)

            if work and str(work[0].get("type", "")) == "couverture":
                units.append(
                    {
                        "kind": "single_cover",
                        "pages": [work.pop(0)],
                    }
                )

            back_cover = None
            if work and str(work[-1].get("type", "")) == "quatrieme":
                back_cover = work.pop()

            page_number = 1
            cursor = 0

            while cursor < len(work):
                left = work[cursor]
                right = (
                    work[cursor + 1]
                    if cursor + 1 < len(work)
                    else None
                )

                units.append(
                    {
                        "kind": "spread",
                        "pages": [left, right],
                        "left_number": page_number,
                        "right_number": (
                            page_number + 1
                            if right is not None
                            else None
                        ),
                    }
                )

                cursor += 2
                page_number += 2

            if back_cover is not None:
                units.append(
                    {
                        "kind": "single_back",
                        "pages": [back_cover],
                    }
                )

            return units

        display_units = make_display_units()

        def draw_wall(_event=None) -> None:
            width = max(1, int(wall.winfo_width()))
            viewport_h = max(1, int(wall.winfo_height()))

            if width <= 4 or viewport_h <= 4:
                return

            wall.delete("all")
            wall._page_thumb_photos = []

            left_margin = 22
            top_margin = 78
            bottom_margin = 34

            unit_w = 246
            unit_h = 187
            gap_x = 15
            gap_y = 18

            usable_w = max(
                unit_w,
                width - left_margin * 2,
            )
            columns = max(
                1,
                int(
                    (usable_w + gap_x)
                    // (unit_w + gap_x)
                ),
            )

            rows = max(
                1,
                (len(display_units) + columns - 1)
                // columns,
            )

            content_h = max(
                viewport_h,
                top_margin
                + rows * unit_h
                + max(0, rows - 1) * gap_y
                + bottom_margin,
            )

            background = make_background(width, content_h)

            if background is not None:
                try:
                    from PIL import ImageTk

                    photo = ImageTk.PhotoImage(background)
                    wall._regulation_bg_photo = photo
                    wall.create_image(
                        0,
                        0,
                        image=photo,
                        anchor="nw",
                    )
                except Exception:
                    pass

            wall.create_text(
                22,
                18,
                text="Synoptique du livre",
                fill=self.INK,
                font=(Fonts.FAMILY, 13, "bold"),
                anchor="nw",
            )

            wall.create_text(
                width - 22,
                20,
                text=(
                    f"{snapshot['planned_pages']} pages prévues"
                    if snapshot["planned_pages"]
                    else "Structure non définie"
                ),
                fill=self.TEXT_MUTED,
                font=(Fonts.FAMILY, 9),
                anchor="ne",
            )

            wall.create_text(
                22,
                45,
                text=(
                    "Vue livre ouvert · base de la future "
                    "fenêtre Visualisation"
                ),
                fill=self.TEXT_MUTED,
                font=(Fonts.FAMILY, 8),
                anchor="nw",
            )

            if not display_units:
                wall.create_text(
                    width / 2,
                    max(130, viewport_h / 2 - 10),
                    text="Le plan du livre n'est pas encore disponible.",
                    fill=self.INK,
                    font=(Fonts.FAMILY, 12, "bold"),
                    anchor="center",
                )
                wall.create_text(
                    width / 2,
                    max(155, viewport_h / 2 + 18),
                    text=(
                        "Le Maquettage alimentera automatiquement "
                        "ce synoptique."
                    ),
                    fill=self.TEXT_MUTED,
                    font=(Fonts.FAMILY, 9),
                    anchor="center",
                )
            else:
                for index, unit in enumerate(display_units):
                    row = index // columns
                    column = index % columns

                    ux = (
                        left_margin
                        + column * (unit_w + gap_x)
                    )
                    uy = (
                        top_margin
                        + row * (unit_h + gap_y)
                    )

                    kind = unit["kind"]

                    if kind in {"single_cover", "single_back"}:
                        item = unit["pages"][0]

                        draw_page(
                            ux + (unit_w - 111) / 2,
                            uy + 10,
                            item,
                            page_side="right",
                            page_number=None,
                            scale=1.10,
                        )

                    else:
                        left_page, right_page = unit["pages"]

                        # Un seul cadre léger matérialise la double page.
                        # Aucun fond : le décor PageMaître reste visible.
                        wall.create_rectangle(
                            ux + 5,
                            uy + 4,
                            ux + unit_w - 5,
                            uy + unit_h - 4,
                            fill="",
                            outline=blend("#718096", 0.64),
                            width=1,
                        )

                        page_y = uy + 10
                        page_scale = 1.05
                        page_w = 101 * page_scale

                        left_x = ux + 15
                        right_x = ux + unit_w - 15 - page_w

                        draw_page(
                            left_x,
                            page_y,
                            left_page,
                            page_side="left",
                            page_number=unit["left_number"],
                            scale=page_scale,
                        )

                        if right_page is not None:
                            draw_page(
                                right_x,
                                page_y,
                                right_page,
                                page_side="right",
                                page_number=unit["right_number"],
                                scale=page_scale,
                            )
                        else:
                            wall.create_rectangle(
                                right_x,
                                page_y,
                                right_x + page_w,
                                page_y + 143 * page_scale,
                                fill="",
                                outline=blend("#AEB5BC", 0.35),
                                dash=(3, 3),
                                width=1,
                            )

                        center_x = ux + unit_w / 2
                        wall.create_line(
                            center_x,
                            page_y + 4,
                            center_x,
                            page_y + 143 * page_scale - 4,
                            fill=blend("#6B7280", 0.55),
                            width=1,
                        )

            wall.configure(
                scrollregion=(0, 0, width, content_h)
            )

        def on_mousewheel(event) -> None:
            try:
                delta = int(event.delta)
            except Exception:
                return

            if delta == 0:
                return

            wall.yview_scroll(
                -1 if delta > 0 else 1,
                "units",
            )

        wall._redraw_regulation = draw_wall
        wall.bind("<Configure>", draw_wall, add="+")
        wall.bind("<MouseWheel>", on_mousewheel, add="+")
        wall.after_idle(draw_wall)

        side = ctk.CTkFrame(
            workspace,
            width=314,
            fg_color=self.CARD_BG,
            corner_radius=9,
            border_width=1,
            border_color=self.BORDER,
        )
        side.grid(row=0, column=1, sticky="nsew")
        side.grid_propagate(False)
        side.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            side,
            text="Régulation",
            font=(Fonts.FAMILY, 12, "bold"),
            text_color=self.INK,
            anchor="w",
        ).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=14,
            pady=(13, 2),
        )

        ctk.CTkLabel(
            side,
            text="Informations utiles au pilotage du livre.",
            font=(Fonts.FAMILY, 8),
            text_color=self.TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=278,
        ).grid(
            row=1,
            column=0,
            sticky="ew",
            padx=14,
            pady=(0, 10),
        )

        def metric(row: int, label: str, value: str, color: str) -> None:
            frame = ctk.CTkFrame(
                side,
                height=39,
                fg_color=blend(color, 0.87),
                corner_radius=7,
                border_width=1,
                border_color=blend(color, 0.50),
            )
            frame.grid(
                row=row,
                column=0,
                sticky="ew",
                padx=12,
                pady=(0, 5),
            )
            frame.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                frame,
                text=label,
                font=(Fonts.FAMILY, 8),
                text_color=self.TEXT_MUTED,
                anchor="w",
            ).grid(
                row=0,
                column=0,
                sticky="w",
                padx=(10, 4),
                pady=7,
            )

            ctk.CTkLabel(
                frame,
                text=value,
                font=(Fonts.FAMILY, 10, "bold"),
                text_color=color,
            ).grid(
                row=0,
                column=1,
                sticky="e",
                padx=(4, 10),
                pady=7,
            )

        metric(
            2,
            "Pages prévues",
            str(snapshot["planned_pages"]),
            self.MAQUETTAGE,
        )
        metric(
            3,
            "Pages automatiques",
            str(snapshot["automatic_pages"]),
            self.ATELIER,
        )
        metric(
            4,
            "Pages produites",
            str(snapshot["produced_pages"]),
            self.CONCEPTION,
        )
        metric(
            5,
            "Pages validées",
            str(snapshot["validated_pages"]),
            self.VERIFICATION,
        )

        ctk.CTkLabel(
            side,
            text="À traiter",
            font=(Fonts.FAMILY, 10, "bold"),
            text_color=self.INK,
            anchor="w",
        ).grid(
            row=6,
            column=0,
            sticky="ew",
            padx=14,
            pady=(12, 5),
        )

        work_pages = max(
            0,
            snapshot["planned_pages"] - snapshot["automatic_pages"]
        )
        remaining_to_produce = max(
            0,
            work_pages - snapshot["produced_pages"]
        )

        alerts: list[tuple[str, str]] = []

        if not snapshot["items"]:
            alerts.append(
                (
                    "Plan du livre",
                    "Le Maquettage doit encore définir la structure.",
                )
            )
        elif remaining_to_produce:
            alerts.append(
                (
                    "Production",
                    f"{remaining_to_produce} page(s) restent à produire.",
                )
            )

        if (
            snapshot["produced_pages"] > snapshot["validated_pages"]
            and snapshot["produced_pages"] > 0
        ):
            alerts.append(
                (
                    "Validation",
                    (
                        f"{snapshot['produced_pages'] - snapshot['validated_pages']} "
                        "page(s) produite(s) non validée(s)."
                    ),
                )
            )

        if not alerts:
            alerts.append(
                (
                    "Aucune alerte",
                    "Le projet ne demande pas d'intervention immédiate.",
                )
            )

        for offset, (title, text) in enumerate(alerts[:3]):
            alert = ctk.CTkFrame(
                side,
                fg_color="#F7F8F6",
                corner_radius=7,
                border_width=1,
                border_color=self.BORDER,
            )
            alert.grid(
                row=7 + offset,
                column=0,
                sticky="ew",
                padx=12,
                pady=(0, 5),
            )
            alert.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(
                alert,
                text=title,
                font=(Fonts.FAMILY, 8, "bold"),
                text_color=self.INK,
                anchor="w",
            ).grid(
                row=0,
                column=0,
                sticky="ew",
                padx=9,
                pady=(6, 0),
            )

            ctk.CTkLabel(
                alert,
                text=text,
                font=(Fonts.FAMILY, 8),
                text_color=self.TEXT_MUTED,
                anchor="w",
                justify="left",
                wraplength=260,
            ).grid(
                row=1,
                column=0,
                sticky="ew",
                padx=9,
                pady=(1, 7),
            )

        if callable(self.on_cleanup):
            ctk.CTkButton(
                side,
                text="Nettoyage du projet",
                height=30,
                corner_radius=6,
                fg_color="transparent",
                hover_color=Colors.BUTTON_HOVER,
                text_color=self.INK,
                border_width=1,
                border_color=self.BORDER,
                font=(Fonts.FAMILY, 8),
                command=self.on_cleanup,
            ).grid(
                row=11,
                column=0,
                sticky="ew",
                padx=12,
                pady=(12, 10),
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
                text=(
                    "Aucune planche"
                    if self._project_type_key() == "bande_dessinee"
                    else "Aucune page"
                ),
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

    def _associated_model_id_for_synoptic_item(
        self,
        item: dict,
    ) -> str:
        # ROUTEUR_CENTRE_MAQUETTAGE_ATELIER_V1
        page_type = str(item.get("type", "")).strip()
        if not page_type:
            return ""

        path = (
            Path(self.project.models_folder)
            / "maquettage_associations.json"
        )
        if not path.is_file():
            return ""

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return ""

        associations = (
            data.get("associations", {})
            if isinstance(data, dict)
            else {}
        )
        if not isinstance(associations, dict):
            return ""

        return str(associations.get(page_type, "")).strip()

    def _route_synoptic_page(self, item: dict) -> None:
        """Ouvre la page dans l'espace correspondant à son état réel."""
        model_id = self._associated_model_id_for_synoptic_item(item)

        if model_id:
            self._hide_project_tools_for_subspace()

            if self._model_workshop_view is None:
                self._model_workshop_view = ModelWorkshopView(
                    parent=self.parent,
                    project=self.project,
                    on_back=self._close_model_workshop,
                )

            if self._model_workshop_view.focus_model(model_id):
                return

            # Association devenue invalide : on revient sans bloquer
            # au comportement de base du Maquettage.
            try:
                self._model_workshop_view.hide()
            except Exception:
                pass

        self._open_mockup_page(item)

    def _open_mockup_page(self, item: dict) -> None:
        """Ouvre le Maquettage directement sur la page issue du synoptique."""
        item_id = str(item.get("id", "")).strip()

        try:
            occurrence = max(
                1,
                int(item.get("_occurrence", 1) or 1),
            )
        except (TypeError, ValueError):
            occurrence = 1

        self._hide_project_tools_for_subspace()

        view = MockupView(
            parent=self.parent,
            project=self.project,
            on_back=self._return_to_project_centre,
        )
        view.show()

        if not item_id:
            return

        # Le ciblage est confié au Maquettage lui-même. Cela conserve une
        # seule logique de sélection et prépare le futur routeur Centre :
        # Maquettage -> Atelier -> Conception selon l'état réel de la page.
        view.focus_page(
            item_id,
            occurrence=occurrence,
        )

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

        # Le Centre existe déjà derrière l'Atelier : on ne le reconstruit pas.
        # On redessine seulement son Canvas afin que l'état "gabarit ouvert"
        # soit immédiatement visible au retour.
        wall = getattr(self, "_regulation_wall", None)
        if wall is not None:
            try:
                if wall.winfo_exists():
                    redraw = getattr(
                        wall,
                        "_redraw_regulation",
                        None,
                    )
                    if callable(redraw):
                        wall.after_idle(redraw)
            except tk.TclError:
                pass

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