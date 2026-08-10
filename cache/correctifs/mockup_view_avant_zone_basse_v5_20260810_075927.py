from __future__ import annotations

import json
import re
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

import customtkinter as ctk

from src.gui.shortcut_manager import get_global_shortcut_manager
from src.theme.colors import Colors
from src.theme.fonts import Fonts


class MockupView:
    """Pré-chemin de fer visuel, simple et facultatif."""

    # Palette PageMaître : bleu-encre, céladon, bleu ciel, lilas,
    # corail et jaune doux. Les teintes restent claires et non agressives.
    WINDOW_BG = Colors.WINDOW
    RIBBON_BG = "#F8FAFB"
    GROUP_BG = "#FFFFFF"
    CARD_BG = "#FDFEFE"
    CANVAS_BG = "#F2F5F7"
    INK = "#263E63"
    BORDER = "#DCE3E8"
    TEXT_MUTED = Colors.TEXT_LIGHT
    TEXT_LIGHT = "#8B8E88"
    SKY = "#75B6DB"
    CELADON = "#82B7A1"
    LILAC = "#A997C9"
    CORAL = "#DF806B"
    YELLOW = "#D8B85A"
    NAVY = INK
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
    TEXT_LIGHT = "#8B8E88"
    PROJECT_TYPE_APPEARANCES = {
        "ouvrage_structure": {"label": "Maquettage", "color": SKY, "soft": MAQUETTAGE_SOFT},
    }
    ACCENT = INK
    ACCENT_SOFT = "#E7EEF6"
    DONE = Colors.SUCCESS
    DANGER = Colors.ERROR

    DEFAULT_GROUPS: tuple[dict[str, Any], ...] = (
        {
            "id": "debut_livre",
            "title": "Début du livre",
            "symbol": "◁",
            "accent": CORAL,
            "protected": True,
        },
        {
            "id": "pages_interieures",
            "title": "Partie 1",
            "symbol": "▦",
            "accent": SKY,
            "protected": True,
        },
        {
            "id": "fin_livre",
            "title": "Fin du livre",
            "symbol": "▷",
            "accent": CELADON,
            "protected": True,
        },
    )

    START_STRUCTURAL_TYPES: tuple[str, ...] = (
        "couverture",
        "deuxieme_couverture",
    )
    END_STRUCTURAL_TYPES: tuple[str, ...] = (
        "troisieme_couverture",
        "quatrieme",
    )
    STRUCTURAL_TYPES: frozenset[str] = frozenset(
        START_STRUCTURAL_TYPES + END_STRUCTURAL_TYPES
    )
    REQUIRED_STRUCTURAL_TYPES: frozenset[str] = frozenset(
        {"couverture", "quatrieme"}
    )

    PAGE_LIBRARY: tuple[dict[str, Any], ...] = (
        {
            "type": "couverture",
            "title": "Couverture",
            "short": "Couverture",
            "symbol": "▧",
            "color": "#DDECF4",
            "accent": SKY,
            "group": "debut_livre",
            "single": True,
            "locked_position": True,
            "required": True,
        },
        {
            "type": "deuxieme_couverture",
            "title": "Deuxième de couverture",
            "short": "2e couverture",
            "symbol": "2e",
            "color": "#E7EEF6",
            "accent": INK,
            "group": "debut_livre",
            "single": True,
            "locked_position": True,
            "required": False,
        },
        {
            "type": "page_titre",
            "title": "Page de titre",
            "short": "Titre",
            "symbol": "T",
            "color": "#F1E7E2",
            "accent": CORAL,
            "group": "debut_livre",
        },
        {
            "type": "sommaire",
            "title": "Sommaire",
            "short": "Sommaire",
            "symbol": "☷",
            "color": "#E1EEE9",
            "accent": CELADON,
            "group": "debut_livre",
        },
        {
            "type": "avant_propos",
            "title": "Avant-propos",
            "short": "Avant-propos",
            "symbol": "¶",
            "color": "#E3EBF2",
            "accent": SKY,
            "group": "debut_livre",
        },
        {
            "type": "chapitre",
            "title": "Chapitre",
            "short": "Chapitre",
            "symbol": "CH",
            "color": "#F2DDD6",
            "accent": CORAL,
            "group": "pages_interieures",
        },
        {
            "type": "fiche",
            "title": "Page fiche",
            "short": "Fiche",
            "symbol": "▦",
            "color": "#DFECE5",
            "accent": CELADON,
            "group": "pages_interieures",
        },
        {
            "type": "texte",
            "title": "Page de texte",
            "short": "Texte",
            "symbol": "≡",
            "color": "#DFEAF3",
            "accent": SKY,
            "group": "pages_interieures",
        },
        {
            "type": "illustration",
            "title": "Illustration",
            "short": "Illustration",
            "symbol": "▣",
            "color": "#E8E1F1",
            "accent": LILAC,
            "group": "pages_interieures",
        },
        {
            "type": "transition",
            "title": "Transition",
            "short": "Transition",
            "symbol": "◇",
            "color": "#F1E8CD",
            "accent": YELLOW,
            "group": "pages_interieures",
        },
        {
            "type": "page_blanche",
            "title": "Page blanche",
            "short": "Blanche",
            "symbol": "□",
            "color": "#FAF9F5",
            "accent": "#A4A8A2",
            "group": "pages_interieures",
        },
        {
            "type": "conclusion",
            "title": "Conclusion",
            "short": "Conclusion",
            "symbol": "✓",
            "color": "#E7EDD9",
            "accent": "#8AA55C",
            "group": "fin_livre",
        },
        {
            "type": "troisieme_couverture",
            "title": "Troisième de couverture",
            "short": "3e couverture",
            "symbol": "3e",
            "color": "#E1EEE9",
            "accent": CELADON,
            "group": "fin_livre",
            "single": True,
            "locked_position": True,
            "required": False,
        },
        {
            "type": "quatrieme",
            "title": "Quatrième de couverture",
            "short": "Quatrième",
            "symbol": "◁",
            "color": "#ECDCD8",
            "accent": CORAL,
            "group": "fin_livre",
            "single": True,
            "locked_position": True,
            "required": True,
        },
    )

    UNKNOWN_PAGE: dict[str, Any] = {
        "type": "inconnu",
        "title": "Type de page inconnu",
        "short": "Inconnu",
        "symbol": "?",
        "color": "#E6E8ED",
        "accent": INK,
        "group": "pages_interieures",
    }

    TYPE_COLOR_CHOICES: dict[str, tuple[str, str]] = {
        "Bleu ciel": ("#DFEAF3", SKY),
        "Vert céladon": ("#DFECE5", CELADON),
        "Lilas": ("#E8E1F1", LILAC),
        "Corail": ("#F2DDD6", CORAL),
        "Jaune doux": ("#F1E8CD", YELLOW),
        "Bleu encre": ("#E7EEF6", INK),
        "Gris doux": ("#EEF0F2", "#7C838D"),
    }

    GROUP_COLOR_CHOICES: dict[str, str] = {
        "Bleu ciel": SKY,
        "Vert céladon": CELADON,
        "Lilas": LILAC,
        "Corail": CORAL,
        "Jaune doux": YELLOW,
        "Bleu encre": INK,
    }

    ICON_CHOICES: tuple[str, ...] = (
        "▦",
        "▧",
        "◇",
        "○",
        "□",
        "T",
        "CH",
        "¶",
        "≡",
        "✓",
        "✦",
    )


    def __init__(
        self,
        parent,
        project,
        on_back: Callable[[], None] | None = None,
        on_home: Callable[[], None] | None = None,
        on_workshop: Callable[[], None] | None = None,
        on_conception: Callable[[], None] | None = None,
    ) -> None:
        self.parent = parent
        self.project = project
        self.on_back = on_back
        self.on_home = on_home
        self.on_workshop = on_workshop
        self.on_conception = on_conception

        self._last_structure_issues: list[dict[str, str]] = []
        self.data: dict[str, Any] = self._load_data()
        self._clear_legacy_manual_done_flags()
        self._run_silent_structure_check()
        self._root: ctk.CTkFrame | None = None
        self._sequence_frame: ctk.CTkScrollableFrame | None = None
        self._summary_label: ctk.CTkLabel | None = None
        self._progress_label: ctk.CTkLabel | None = None
        self._preview_window: ctk.CTkToplevel | None = None
        self._manage_window: ctk.CTkToplevel | None = None
        self._recto_verso_window: ctk.CTkToplevel | None = None
        self._recto_rule_editor_id: str | None = None
        self._ribbon_frame: ctk.CTkFrame | None = None
        self._ribbon_group_widgets: dict[str, ctk.CTkFrame] = {}
        self._dragged_group_id: str | None = None
        self._drag_group_start_x = 0
        self._drag_group_has_moved = False
        self._group_drop_indicator: ctk.CTkFrame | None = None
        self._dragged_page_id: str | None = None
        self._dragged_page_ids: tuple[str, ...] = ()
        self._drag_page_start_y = 0
        self._drag_page_has_moved = False
        self._drag_page_press_state = 0
        self._page_drop_indicator: ctk.CTkFrame | None = None
        self._selected_page_ids: set[str] = set()
        self._rendered_selected_page_ids: set[str] = set()
        self._selection_anchor_id: str | None = None
        self._selection_bar: ctk.CTkFrame | None = None
        self._selection_label: ctk.CTkLabel | None = None
        self._selection_duplicate_button: ctk.CTkButton | None = None
        self._selection_delete_button: ctk.CTkButton | None = None
        self._page_type_buttons: dict[str, ctk.CTkButton] = {}
        self._sequence_row_widgets: dict[str, dict[str, Any]] = {}
        self._sequence_row_signatures: dict[str, tuple[Any, ...]] = {}
        self._sequence_empty_label: ctk.CTkLabel | None = None
        self._page_type_button_states: dict[str, str] = {}
        self._selection_controls_cache: tuple[int, int, int] | None = None
        self._summary_text_cache: str | None = None
        self._progress_text_cache: str | None = None
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
        self._undo_stack: list[dict[str, Any]] = []
        self._redo_stack: list[dict[str, Any]] = []
        self._history_limit = 50
        self._undo_button: ctk.CTkButton | None = None
        self._redo_button: ctk.CTkButton | None = None
        self._selected_ribbon_group_id = "debut_livre"
        self._ribbon_groups_panel: ctk.CTkFrame | None = None
        self._ribbon_types_panel: ctk.CTkFrame | None = None
        self._drag_group_start_y = 0
        self._shortcut_manager = None
        self._thumbnail_image_cache: dict[tuple[str, int], tk.PhotoImage] = {}

    # ==========================================================
    # Affichage principal
    # ==========================================================

    def show(self) -> None:
        self._deactivate_global_shortcuts()
        self._clear_parent()

        # Les références aux widgets appartiennent à l'écran courant.
        self._page_type_buttons.clear()
        self._page_type_button_states.clear()
        self._selection_controls_cache = None
        self._summary_text_cache = None
        self._progress_text_cache = None
        self._sequence_row_widgets.clear()
        self._sequence_row_signatures.clear()
        self._rendered_selected_page_ids.clear()
        self._sequence_empty_label = None

        # FOND_DISCRET_MAQUETTAGE_V1
        # Le fond léger de l'accueil est posé derrière tout le Bureau de
        # maquettage. Les panneaux existants restent inchangés par-dessus.
        self._root = ctk.CTkFrame(
            self.parent,
            fg_color=self.WINDOW_BG,
            corner_radius=0,
        )
        self._root.pack(fill="both", expand=True)
        self._root.grid_columnconfigure(0, weight=1)
        self._root.grid_rowconfigure(2, weight=1)
        self._root.bind("<Destroy>", self._on_root_destroyed, add="+")
        self._activate_global_shortcuts()

        self._mockup_background_label = None
        self._mockup_background_source = None
        self._mockup_background_photo = None

        background_path = (
            Path(__file__).resolve().parents[3]
            / "assets"
            / "interface"
            / "backgrounds"
            / "editorial_bg_soft.png"
        )
        if background_path.is_file():
            try:
                from PIL import Image, ImageTk

                self._mockup_background_source = Image.open(background_path).convert("RGB")

                bg_label = tk.Label(
                    self._root,
                    borderwidth=0,
                    highlightthickness=0,
                    background=self.WINDOW_BG,
                )
                bg_label.place(x=0, y=0, relwidth=1, relheight=1)
                bg_label.lower()
                self._mockup_background_label = bg_label

                def redraw_background(_event=None) -> None:
                    label = self._mockup_background_label
                    source = self._mockup_background_source
                    if label is None or source is None:
                        return
                    try:
                        width = max(1, int(self._root.winfo_width()))
                        height = max(1, int(self._root.winfo_height()))
                        if width <= 2 or height <= 2:
                            return

                        source_ratio = source.width / source.height
                        target_ratio = width / height
                        if target_ratio > source_ratio:
                            new_width = width
                            new_height = max(1, int(round(width / source_ratio)))
                        else:
                            new_height = height
                            new_width = max(1, int(round(height * source_ratio)))

                        resized = source.resize(
                            (new_width, new_height),
                            Image.Resampling.LANCZOS,
                        )

                        left = max(0, (new_width - width) // 2)
                        top = max(0, (new_height - height) // 2)
                        cropped = resized.crop(
                            (left, top, left + width, top + height)
                        )

                        photo = ImageTk.PhotoImage(cropped)
                        self._mockup_background_photo = photo
                        label.configure(image=photo)
                    except Exception:
                        pass

                self._root.bind(
                    "<Configure>",
                    redraw_background,
                    add="+",
                )
                self._root.after_idle(redraw_background)
            except Exception:
                # Le Bureau reste parfaitement utilisable avec son fond uni.
                self._mockup_background_label = None
                self._mockup_background_source = None
                self._mockup_background_photo = None

        self._create_internal_navigation_ribbon(self._root).grid(
            row=0,
            column=0,
            sticky="ew",
            padx=10,
            pady=(5, 3),
        )

        # REFONTE_MAQUETTAGE_STRUCTURE_V1
        self._ribbon_frame = self._create_ribbon(self._root)
        self._ribbon_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 6),
        )

        self._create_book_overview_panel(self._root).grid(
            row=2,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 6),
        )

        self._create_sequence_panel(self._root).grid(
            row=3,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 10),
        )

        self._root.grid_rowconfigure(2, weight=0)
        self._root.grid_rowconfigure(3, weight=1)

        self._refresh_sequence()


    def focus_page(
        self,
        item_id: str,
        occurrence: int = 1,
    ) -> bool:
        """Sélectionne une page du Maquettage et la place au centre de la vue.

        Cette méthode publique est destinée au Centre de régulation et à la
        future fenêtre Visualisation. Elle ne reconstruit pas le Maquettage :
        elle s'appuie sur la ligne déjà rendue et sur son identifiant stable.

        ``occurrence`` est conservé pour les types présents plusieurs fois.
        Aujourd'hui le Maquettage les regroupe encore dans une même ligne ;
        le paramètre prépare donc le ciblage individuel futur sans casser
        l'interface actuelle.
        """
        page_id = str(item_id or "").strip()
        if not page_id:
            return False

        item = next(
            (
                candidate
                for candidate in self._items()
                if str(candidate.get("id", "")) == page_id
            ),
            None,
        )
        if item is None:
            return False

        try:
            occurrence_value = max(1, int(occurrence))
        except (TypeError, ValueError):
            occurrence_value = 1

        self._external_focus_occurrence = occurrence_value
        self._selected_page_ids = {page_id}
        self._selection_anchor_id = page_id

        self._refresh_selection_visuals()
        self._update_selection_controls()

        frame = self._sequence_frame
        if frame is None:
            return True

        # Le défilement est différé : Tk doit avoir calculé la géométrie
        # exacte des cartes avant de pouvoir centrer la cible.
        try:
            frame.after_idle(
                lambda selected=page_id: self._scroll_to_page_id(selected)
            )
        except tk.TclError:
            pass

        return True

    def _scroll_to_page_id(self, item_id: str) -> None:
        """Centre dans le Plan du livre la ligne correspondant à ``item_id``."""
        frame = self._sequence_frame
        record = self._sequence_row_widgets.get(str(item_id))

        if frame is None or record is None:
            return

        row = record.get("row")
        if row is None:
            return

        try:
            frame.update_idletasks()
            row.update_idletasks()

            canvas = getattr(frame, "_parent_canvas", None)
            if canvas is None:
                return

            viewport_height = max(1, int(canvas.winfo_height()))
            row_y = int(row.winfo_y())
            row_height = max(1, int(row.winfo_height()))

            # La frame intérieure porte toutes les cartes.
            content_height = max(
                int(frame.winfo_height()),
                int(frame.winfo_reqheight()),
                row_y + row_height,
            )

            maximum_scroll = max(0, content_height - viewport_height)
            if maximum_scroll <= 0:
                canvas.yview_moveto(0.0)
                return

            target_top = (
                row_y
                - max(0, (viewport_height - row_height) // 2)
            )
            fraction = max(
                0.0,
                min(1.0, target_top / maximum_scroll),
            )
            canvas.yview_moveto(fraction)

            # Une seconde passe stabilise le centrage sur certains facteurs
            # d'échelle Windows/CustomTkinter.
            canvas.update_idletasks()
        except (tk.TclError, TypeError, ValueError):
            return

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

                text="Bureau de maquettage",

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
                    self.on_home,
                    False,
                    self.on_home is not None,
                    72,
                ),
                (
                    "home",
                    "Centre",
                    self.NAVY,
                    self.on_back,
                    False,
                    self.on_back is not None,
                    72,
                ),
                (
                    "pencil",
                    "Maquettage",
                    self.MAQUETTAGE,
                    None,
                    True,
                    True,
                    92,
                ),
                (
                    "tools",
                    "Atelier",
                    self.ATELIER,
                    self.on_workshop,
                    False,
                    self.on_workshop is not None,
                    76,
                ),
                (
                    "quill",
                    "Conception",
                    self.CONCEPTION,
                    self.on_conception,
                    False,
                    self.on_conception is not None,
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

                command=self.on_home,

                enabled=self.on_home is not None,

                width=76,

            )



        canvas.bind(

            "<Configure>",

            redraw,

            add="+",

        )

        canvas.after_idle(redraw)



        return ribbon




    def _project_type_key(self) -> str:
        return "ouvrage_structure"

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

    def _install_ribbon_background(self, ribbon) -> None:
        """Pose le même fond léger derrière toute la surface du ruban."""
        background_path = (
            Path(__file__).resolve().parents[3]
            / "assets"
            / "interface"
            / "backgrounds"
            / "editorial_bg_soft.png"
        )
        if not background_path.is_file():
            return

        try:
            from PIL import Image, ImageTk

            source = Image.open(background_path).convert("RGB")
            label = tk.Label(
                ribbon,
                image="",
                text="",
                borderwidth=0,
                highlightthickness=0,
                background=self.RIBBON_BG,
                takefocus=False,
            )
            label.place(x=0, y=0, relwidth=1, relheight=1)
            label.lower()

            # Références conservées pour éviter la libération des images Tk.
            ribbon._soft_background_source = source
            ribbon._soft_background_label = label
            ribbon._soft_background_photo = None

            def redraw(_event=None) -> None:
                try:
                    width = max(1, int(ribbon.winfo_width()))
                    height = max(1, int(ribbon.winfo_height()))
                    if width <= 2 or height <= 2:
                        return

                    source_ratio = source.width / source.height
                    target_ratio = width / height

                    if target_ratio > source_ratio:
                        resize_width = width
                        resize_height = max(
                            height,
                            int(round(width / source_ratio)),
                        )
                    else:
                        resize_height = height
                        resize_width = max(
                            width,
                            int(round(height * source_ratio)),
                        )

                    resized = source.resize(
                        (resize_width, resize_height),
                        Image.Resampling.LANCZOS,
                    )
                    left = max(0, (resize_width - width) // 2)
                    top = max(0, (resize_height - height) // 2)
                    cropped = resized.crop(
                        (left, top, left + width, top + height)
                    )

                    photo = ImageTk.PhotoImage(cropped)
                    ribbon._soft_background_photo = photo
                    label.configure(image=photo)
                    label.place(
                        x=0,
                        y=0,
                        width=width,
                        height=height,
                    )
                    label.lower()
                except Exception:
                    pass

            ribbon.bind("<Configure>", redraw, add="+")
            ribbon.after_idle(redraw)
        except Exception:
            pass

    def _create_soft_background_container(self, parent):
        """Conteneur Tk affichant réellement le décor léger en arrière-plan."""
        container = tk.Label(
            parent,
            image="",
            text="",
            borderwidth=0,
            highlightthickness=0,
            background=self.RIBBON_BG,
        )
        container._soft_background_source = None
        container._soft_background_photo = None

        background_path = (
            Path(__file__).resolve().parents[3]
            / "assets"
            / "interface"
            / "backgrounds"
            / "editorial_bg_soft.png"
        )

        if background_path.is_file():
            try:
                from PIL import Image, ImageTk

                source = Image.open(background_path).convert("RGB")
                container._soft_background_source = source

                def redraw(_event=None) -> None:
                    try:
                        width = max(1, int(container.winfo_width()))
                        height = max(1, int(container.winfo_height()))
                        if width <= 2 or height <= 2:
                            return

                        source_ratio = source.width / source.height
                        target_ratio = width / height
                        if target_ratio > source_ratio:
                            resize_width = width
                            resize_height = max(
                                height,
                                int(round(width / source_ratio)),
                            )
                        else:
                            resize_height = height
                            resize_width = max(
                                width,
                                int(round(height * source_ratio)),
                            )

                        resized = source.resize(
                            (resize_width, resize_height),
                            Image.Resampling.LANCZOS,
                        )
                        left = max(0, (resize_width - width) // 2)
                        top = max(0, (resize_height - height) // 2)
                        cropped = resized.crop(
                            (left, top, left + width, top + height)
                        )
                        photo = ImageTk.PhotoImage(cropped)
                        container._soft_background_photo = photo
                        container.configure(image=photo)
                    except Exception:
                        pass

                container.bind("<Configure>", redraw, add="+")
                container.after_idle(redraw)
            except Exception:
                pass

        return container


    def _create_book_overview_panel(self, parent) -> ctk.CTkFrame:
        """Vue globale compacte du livre, inspirée d'un plan de métro."""
        shell = ctk.CTkFrame(
            parent,
            height=88,
            fg_color=self.CARD_BG,
            corner_radius=8,
            border_width=1,
            border_color=self.BORDER,
        )
        shell.grid_propagate(False)
        shell.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(
            shell,
            height=24,
            fg_color="transparent",
            corner_radius=0,
        )
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(5, 0))
        header.grid_columnconfigure(0, weight=1)
        header.grid_propagate(False)

        ctk.CTkLabel(
            header,
            text="Vue globale du livre",
            font=(Fonts.FAMILY, 10, "bold"),
            text_color=self.INK,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text="Cliquez sur un groupe pour vous y rendre",
            font=(Fonts.FAMILY, 8),
            text_color=self.TEXT_MUTED,
            anchor="e",
        ).grid(row=0, column=1, sticky="e")

        viewport = ctk.CTkScrollableFrame(
            shell,
            height=46,
            orientation="horizontal",
            fg_color="transparent",
            corner_radius=0,
        )
        viewport.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 5))

        rail = ctk.CTkFrame(viewport, fg_color="transparent", corner_radius=0)
        rail.pack(side="left", padx=8, pady=2)

        active_groups = [
            group for group in self._groups()
            if not bool(group.get("deleted", False))
        ]

        for index, group in enumerate(active_groups):
            group_id = str(group.get("id", ""))
            title = str(group.get("title", "Groupe"))
            accent = str(group.get("accent", self.SKY))
            symbol = str(group.get("symbol", "•"))
            selected = group_id == self._selected_ribbon_group_id

            if index:
                ctk.CTkFrame(
                    rail,
                    width=30,
                    height=2,
                    fg_color="#B8C5D2",
                    corner_radius=0,
                ).pack(side="left", pady=(12, 0))

            station = ctk.CTkFrame(
                rail,
                width=76,
                height=42,
                fg_color="transparent",
                corner_radius=0,
            )
            station.pack(side="left")
            station.pack_propagate(False)

            ctk.CTkButton(
                station,
                text=symbol if symbol.strip() else "•",
                width=25 if selected else 22,
                height=25 if selected else 22,
                corner_radius=13,
                fg_color=accent,
                hover_color=self._mix_color_with_white(accent, 0.18),
                text_color="#FFFFFF",
                border_width=2 if selected else 0,
                border_color=self.INK,
                font=(Fonts.FAMILY, 8, "bold"),
                command=lambda gid=group_id: self._select_ribbon_group(gid),
            ).pack(pady=(0, 1))

            ctk.CTkButton(
                station,
                text=title,
                width=74,
                height=14,
                corner_radius=0,
                fg_color="transparent",
                hover_color=self.ACCENT_SOFT,
                text_color=self.INK if selected else self.TEXT_MUTED,
                font=(Fonts.FAMILY, 7, "bold" if selected else "normal"),
                command=lambda gid=group_id: self._select_ribbon_group(gid),
            ).pack()

        return shell


    def _create_ribbon(self, parent) -> ctk.CTkFrame:
        """Ruban V2 : Début fixe | groupes défilants | Fin + historiques + outils fixes."""
        self._page_type_buttons.clear()
        self._page_type_button_states.clear()
        self._ribbon_group_widgets.clear()
        self._ribbon_types_panel = None

        groups = self._groups()
        active_groups = [
            group for group in groups
            if not bool(group.get("deleted", False))
        ]

        start_group = next(
            (
                group for group in active_groups
                if str(group.get("id", "")) == "debut_livre"
            ),
            None,
        )
        end_group = next(
            (
                group for group in active_groups
                if str(group.get("id", "")) == "fin_livre"
            ),
            None,
        )
        middle_groups = [
            group for group in active_groups
            if str(group.get("id", "")) not in {"debut_livre", "fin_livre"}
        ]

        deleted_groups = [
            group for group in groups
            if bool(group.get("deleted", False))
        ]
        deleted_page_types = [
            definition
            for definition in self._page_types()
            if bool(definition.get("deleted", False))
        ]

        def group_width(group_definition: dict[str, Any]) -> int:
            group_id = str(group_definition.get("id", ""))
            type_count = sum(
                1
                for definition in self._page_types()
                if (
                    str(definition.get("group", "")) == group_id
                    and not bool(definition.get("deleted", False))
                )
            )
            columns = max(1, (type_count + 1) // 2)
            return max(
                82,
                columns * 66 + max(0, columns - 1) * 3 + 10,
                min(
                    230,
                    len(str(group_definition.get("title", ""))) * 7 + 24,
                ),
            )

        ribbon = ctk.CTkFrame(
            parent,
            fg_color=self.RIBBON_BG,
            corner_radius=8,
            border_width=1,
            border_color=self.BORDER,
        )
        ribbon.grid_columnconfigure(0, weight=0)
        ribbon.grid_columnconfigure(1, weight=1)
        ribbon.grid_columnconfigure(2, weight=0)
        ribbon.grid_rowconfigure(0, weight=1)

        # ------------------------------------------------------
        # Gauche : Début du livre, toujours visible.
        # ------------------------------------------------------
        left = self._create_soft_background_container(ribbon)
        left.grid(
            row=0,
            column=0,
            sticky="nsw",
            padx=(5, 3),
            pady=4,
        )

        if start_group is not None:
            width = group_width(start_group)
            start_block = self._create_group_block(
                left,
                start_group,
                width=width,
            )
            start_block.pack(side="left", padx=1)
            self._ribbon_group_widgets["debut_livre"] = start_block

        # ------------------------------------------------------
        # Centre : toutes les Parties + groupes libres.
        # Défilement horizontal indépendant.
        # ------------------------------------------------------
        middle_shell = ctk.CTkFrame(
            ribbon,
            fg_color="transparent",
            corner_radius=0,
        )
        middle_shell.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=2,
            pady=4,
        )
        middle_shell.grid_columnconfigure(0, weight=1)
        middle_shell.grid_rowconfigure(0, weight=1)

        middle_scroll = ctk.CTkScrollableFrame(
            middle_shell,
            orientation="horizontal",
            fg_color="transparent",
            corner_radius=0,
            height=154,
        )
        middle_scroll.grid(
            row=0,
            column=0,
            sticky="nsew",
        )

        flow = ctk.CTkFrame(
            middle_scroll,
            fg_color="transparent",
            corner_radius=0,
        )
        flow.pack(side="left", padx=2, pady=(0, 2))

        for index, group_definition in enumerate(middle_groups):
            if index:
                ctk.CTkFrame(
                    flow,
                    width=1,
                    height=100,
                    fg_color=self.BORDER,
                    corner_radius=0,
                ).pack(side="left", fill="y", padx=2, pady=3)

            group_id = str(group_definition.get("id", ""))
            block = self._create_group_block(
                flow,
                group_definition,
                width=group_width(group_definition),
            )
            block.pack(side="left", padx=1)
            self._ribbon_group_widgets[group_id] = block

        # ------------------------------------------------------
        # Droite : Fin + historiques + outils, toujours visibles.
        # ------------------------------------------------------
        right = self._create_soft_background_container(ribbon)
        right.grid(
            row=0,
            column=2,
            sticky="nse",
            padx=(3, 5),
            pady=4,
        )

        def separator() -> None:
            ctk.CTkFrame(
                right,
                width=1,
                height=100,
                fg_color=self.BORDER,
                corner_radius=0,
            ).pack(side="left", fill="y", padx=2, pady=3)

        right_has_item = False

        if end_group is not None:
            end_block = self._create_group_block(
                right,
                end_group,
                width=group_width(end_group),
            )
            end_block.pack(side="left", padx=1)
            self._ribbon_group_widgets["fin_livre"] = end_block
            right_has_item = True

        if deleted_groups:
            if right_has_item:
                separator()
            history = self._create_deleted_history_block(
                right,
                deleted_groups,
                width=116,
                title="Groupes supprimés",
                item_kind="group",
            )
            history.pack(side="left", padx=1)
            right_has_item = True

        if deleted_page_types:
            if right_has_item:
                separator()
            history = self._create_deleted_history_block(
                right,
                deleted_page_types,
                width=116,
                title="Types supprimés",
                item_kind="type",
            )
            history.pack(side="left", padx=1)
            right_has_item = True

        if right_has_item:
            separator()

        tools = self._create_fixed_tools_panel(right)
        tools.pack(side="left", padx=1)

        self._ribbon_groups_panel = middle_scroll
        self._update_page_type_button_states()
        self._update_history_buttons()
        return ribbon


    def _create_deleted_history_block(
        self,
        parent,
        deleted_items: list[dict[str, Any]],
        width: int,
        title: str,
        item_kind: str,
    ) -> ctk.CTkFrame:
        """Historique compact, préparé pour la future restauration au clic."""
        block = ctk.CTkFrame(
            parent,
            width=width,
            height=104,
            fg_color="#F5F5F4",
            corner_radius=5,
            border_width=1,
            border_color="#D9DBDE",
        )
        block.pack_propagate(False)
        block.grid_propagate(False)
        block.grid_columnconfigure((0, 1), weight=1)
        block.grid_rowconfigure(0, weight=1)

        history_area = ctk.CTkFrame(
            block,
            fg_color="transparent",
            corner_radius=0,
        )
        history_area.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky="nsew",
            padx=5,
            pady=(4, 2),
        )
        history_area.grid_columnconfigure((0, 1), weight=1)

        visible_items = deleted_items[:6]
        for index, item in enumerate(visible_items):
            if item_kind == "group":
                raw_label = str(
                    item.get("deleted_label")
                    or item.get("deleted_original_title")
                    or ""
                ).strip()
                if not raw_label:
                    current = str(item.get("title", "")).split("—", 1)[0].strip()
                    raw_label = current or "Groupe"
            else:
                raw_label = str(
                    item.get("deleted_label")
                    or item.get("deleted_original_title")
                    or item.get("short")
                    or item.get("title")
                    or "Type"
                ).strip()

            label = raw_label if len(raw_label) <= 11 else raw_label[:10] + "…"

            item_id = (
                str(item.get("id", ""))
                if item_kind == "group"
                else str(item.get("type", ""))
            )

            chip = ctk.CTkLabel(
                history_area,
                text=label,
                width=50,
                height=21,
                corner_radius=5,
                fg_color="#E9EAEC",
                text_color="#8C9198",
                font=(Fonts.FAMILY, 8),
                anchor="center",
                cursor="hand2",
            )
            chip.grid(
                row=index // 2,
                column=index % 2,
                padx=2,
                pady=2,
                sticky="n",
            )
            chip.bind(
                "<Button-1>",
                lambda _event, kind=item_kind, identifier=item_id: (
                    self._confirm_restore_deleted(kind, identifier)
                ),
            )

        if len(deleted_items) > 6:
            ctk.CTkLabel(
                history_area,
                text=f"+{len(deleted_items) - 6}",
                width=50,
                height=18,
                text_color="#8C9198",
                font=(Fonts.FAMILY, 8, "bold"),
                anchor="center",
            ).grid(row=3, column=1, padx=2, pady=1)

        title_bar = ctk.CTkFrame(
            block,
            height=18,
            fg_color="#E7E8EA",
            corner_radius=0,
        )
        title_bar.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky="ew",
            padx=1,
            pady=(0, 1),
        )
        title_bar.grid_propagate(False)
        title_bar.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            title_bar,
            text=title,
            font=(Fonts.FAMILY, 8, "bold"),
            text_color="#7E838A",
            anchor="center",
        ).grid(row=0, column=0, sticky="nsew", padx=3)

        return block

    def _confirm_restore_deleted(
        self,
        item_kind: str,
        identifier: str,
    ) -> None:
        """Demande confirmation avant restauration d'un élément supprimé."""
        if not identifier:
            return

        if item_kind == "group":
            item = next(
                (
                    group
                    for group in self._groups()
                    if (
                        str(group.get("id", "")) == identifier
                        and bool(group.get("deleted", False))
                    )
                ),
                None,
            )
        else:
            item = next(
                (
                    definition
                    for definition in self._page_types()
                    if (
                        str(definition.get("type", "")) == identifier
                        and bool(definition.get("deleted", False))
                    )
                ),
                None,
            )

        if item is None:
            return

        label = str(
            item.get("deleted_original_title")
            or item.get("deleted_label")
            or item.get("title")
            or identifier
        ).strip()

        parent_group = None
        if item_kind == "type":
            parent_id = str(
                item.get("deleted_original_group")
                or item.get("group")
                or ""
            )
            parent_group = next(
                (
                    group
                    for group in self._groups()
                    if (
                        str(group.get("id", "")) == parent_id
                        and bool(group.get("deleted", False))
                    )
                ),
                None,
            )

        message = f"Rétablir « {label} » ?"
        if parent_group is not None:
            parent_label = str(
                parent_group.get("deleted_original_title")
                or parent_group.get("deleted_label")
                or parent_group.get("title")
                or "son groupe"
            ).split("—", 1)[0].strip()
            message += (
                f"\n\nLe groupe « {parent_label} » est également supprimé."
                "\nIl sera rétabli automatiquement."
            )

        window = self._new_dialog("Rétablir", "430x225")
        ctk.CTkLabel(
            window,
            text=message,
            font=Fonts.NORMAL,
            text_color=self.INK,
            justify="center",
            wraplength=370,
        ).pack(padx=24, pady=(34, 24))

        actions = ctk.CTkFrame(window, fg_color="transparent")
        actions.pack(pady=(0, 24))

        ctk.CTkButton(
            actions,
            text="Annuler",
            width=110,
            height=34,
            corner_radius=7,
            fg_color=self.GROUP_BG,
            hover_color=Colors.BUTTON_HOVER,
            text_color=self.INK,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.SMALL,
            command=window.destroy,
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            actions,
            text="Rétablir",
            width=110,
            height=34,
            corner_radius=7,
            fg_color="#E1EEE9",
            hover_color="#D8E9E1",
            text_color=self.INK,
            border_width=1,
            border_color=self.CELADON,
            font=Fonts.SMALL,
            command=lambda: self._restore_deleted_item(
                item_kind,
                identifier,
                window,
            ),
        ).pack(side="left", padx=6)

    def _restore_deleted_group_data(self, group: dict[str, Any]) -> None:
        """Restaure un groupe supprimé et sa position logique d'origine."""
        groups = self._groups()
        if group not in groups:
            return

        original_title = str(
            group.get("deleted_original_title")
            or group.get("title")
            or "Groupe"
        ).split("—", 1)[0].strip()

        group["deleted"] = False
        group["title"] = original_title

        current_index = groups.index(group)
        original_index = group.get("deleted_original_index")
        try:
            original_index = int(original_index)
        except (TypeError, ValueError):
            original_index = current_index

        groups.pop(current_index)

        # Fin du livre doit rester le dernier groupe structurel.
        fin_index = next(
            (
                index
                for index, candidate in enumerate(groups)
                if str(candidate.get("id", "")) == "fin_livre"
            ),
            len(groups),
        )
        target_index = max(1, min(original_index, fin_index))
        groups.insert(target_index, group)

    def _restore_deleted_item(
        self,
        item_kind: str,
        identifier: str,
        owner,
    ) -> None:
        """Restaure un groupe ou un type, avec son groupe parent si nécessaire."""
        if item_kind == "group":
            item = next(
                (
                    group
                    for group in self._groups()
                    if (
                        str(group.get("id", "")) == identifier
                        and bool(group.get("deleted", False))
                    )
                ),
                None,
            )
            if item is None:
                return

            self._record_history()
            self._restore_deleted_group_data(item)

        else:
            item = next(
                (
                    definition
                    for definition in self._page_types()
                    if (
                        str(definition.get("type", "")) == identifier
                        and bool(definition.get("deleted", False))
                    )
                ),
                None,
            )
            if item is None:
                return

            self._record_history()

            parent_id = str(
                item.get("deleted_original_group")
                or item.get("group")
                or ""
            )
            parent_group = next(
                (
                    group
                    for group in self._groups()
                    if str(group.get("id", "")) == parent_id
                ),
                None,
            )

            if parent_group is not None and bool(
                parent_group.get("deleted", False)
            ):
                self._restore_deleted_group_data(parent_group)

            item["deleted"] = False
            item["group"] = parent_id

            definitions = self._page_types()
            current_index = definitions.index(item)
            original_index = item.get("deleted_original_index")
            try:
                original_index = int(original_index)
            except (TypeError, ValueError):
                original_index = current_index

            definitions.pop(current_index)
            target_index = max(0, min(original_index, len(definitions)))
            definitions.insert(target_index, item)

        self._save_data()
        self._close_dialog(owner)
        self._refresh_ribbon()

    def _create_group_block(
        self,
        parent,
        group_definition: dict[str, Any],
        width: int,
    ) -> ctk.CTkFrame:
        """Carte compacte V3 : contenu vertical interne + identité du groupe."""
        group_id = str(group_definition.get("id", ""))
        title = str(group_definition.get("title", "Groupe"))
        symbol = str(group_definition.get("symbol", "▦"))
        accent = str(group_definition.get("accent", self.INK))
        protected = bool(group_definition.get("protected", False))
        deleted = bool(group_definition.get("deleted", False))

        if deleted:
            block = ctk.CTkFrame(
                parent,
                width=52,
                height=154,
                fg_color="transparent",
                corner_radius=0,
            )
            block.pack_propagate(False)
            return block

        group_soft = self._mix_color_with_white(accent, 0.92)
        group_title_soft = self._mix_color_with_white(accent, 0.84)

        # Largeur volontairement compacte : on privilégie le nombre
        # de groupes visibles, le contenu abondant défile verticalement.
        compact_width = max(96, min(148, width))

        block = ctk.CTkFrame(
            parent,
            width=compact_width,
            height=154,
            fg_color=group_soft,
            corner_radius=7,
            border_width=2 if group_id == self._selected_ribbon_group_id else 1,
            border_color=accent if group_id == self._selected_ribbon_group_id else group_title_soft,
        )
        block.pack_propagate(False)
        block.grid_propagate(False)
        block.grid_columnconfigure(0, weight=1)
        block.grid_rowconfigure(1, weight=1)

        title_bar = ctk.CTkFrame(
            block,
            height=22,
            fg_color=group_title_soft,
            corner_radius=6,
        )
        title_bar.grid(row=0, column=0, sticky="ew", padx=1, pady=1)
        title_bar.grid_propagate(False)
        title_bar.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            title_bar,
            text=f"{symbol}  {title}",
            font=(Fonts.FAMILY, 9, "bold"),
            text_color=accent,
            anchor="center",
        )
        title_label.grid(row=0, column=0, sticky="nsew", padx=4)

        definitions = [
            definition
            for definition in self._page_types()
            if (
                str(definition.get("group", "")) == group_id
                and not bool(definition.get("deleted", False))
            )
        ]

        if definitions:
            types_frame = ctk.CTkScrollableFrame(
                block,
                width=compact_width - 8,
                height=118,
                fg_color="transparent",
                corner_radius=0,
            )
            types_frame.grid(
                row=1,
                column=0,
                sticky="nsew",
                padx=2,
                pady=(0, 2),
            )
            types_frame.grid_columnconfigure((0, 1), weight=1)

            for index, definition in enumerate(definitions):
                row = index // 2
                column = index % 2
                button = self._create_page_type_button(types_frame, definition)
                try:
                    button.configure(width=54, height=27)
                except Exception:
                    pass
                button.grid(
                    row=row,
                    column=column,
                    sticky="nsew",
                    padx=1,
                    pady=1,
                )
        else:
            empty = ctk.CTkFrame(
                block,
                fg_color="transparent",
                corner_radius=0,
            )
            empty.grid(row=1, column=0, sticky="nsew", padx=3, pady=2)
            ctk.CTkLabel(
                empty,
                text="Aucun type",
                font=(Fonts.FAMILY, 8),
                text_color=self.TEXT_LIGHT,
            ).place(relx=0.5, rely=0.5, anchor="center")

        # Un clic sur l'en-tête sélectionne le groupe ; le déplacement
        # existant reste disponible pour les groupes non protégés.
        title_bar.bind(
            "<Button-1>",
            lambda _event, gid=group_id: self._select_ribbon_group(gid),
            add="+",
        )
        title_label.bind(
            "<Button-1>",
            lambda _event, gid=group_id: self._select_ribbon_group(gid),
            add="+",
        )

        if not protected:
            self._bind_custom_group_drag(title_bar, title_label, group_id)

        return block


    def _create_page_type_button(
        self,
        parent,
        definition: dict[str, Any],
    ) -> ctk.CTkButton:
        page_type = str(definition.get("type", ""))
        full_title = str(definition.get("title", "Page"))
        short_title = str(definition.get("short", full_title))
        symbol = str(definition.get("symbol", "?"))
        group_id = str(definition.get("group", "pages_interieures"))
        group = self._group_for(group_id)
        group_accent = str(group.get("accent", self.INK))

        # Chaque type garde sa personnalité par son symbole et son libellé,
        # mais sa couleur appartient clairement à son groupe.
        definitions = [
            item
            for item in self._page_types()
            if str(item.get("group", "")) == group_id
        ]
        try:
            position = next(
                index
                for index, item in enumerate(definitions)
                if str(item.get("type", "")) == page_type
            )
        except StopIteration:
            position = 0

        tone_factors = (0.84, 0.79, 0.74, 0.87)
        factor = tone_factors[position % len(tone_factors)]
        button_color = self._mix_color_with_white(group_accent, factor)
        hover_color = self._mix_color_with_white(
            group_accent,
            max(0.58, factor - 0.14),
        )
        border_color = self._mix_color_with_white(group_accent, 0.60)

        button = ctk.CTkButton(
            parent,
            text=f"{symbol}\n{short_title}",
            width=66,
            height=39,
            corner_radius=5,
            fg_color=button_color,
            hover_color=hover_color,
            text_color=group_accent,
            border_width=1,
            border_color=border_color,
            font=(Fonts.FAMILY, 9),
            command=lambda selected=definition: self._add_item(selected),
        )
        self._attach_tooltip(button, full_title)
        if page_type:
            self._page_type_buttons[page_type] = button
        return button

    @staticmethod
    def _mix_color_with_white(color: str, white_ratio: float) -> str:
        """Éclaircit une couleur sans changer sa famille chromatique."""
        value = str(color).lstrip("#")
        if len(value) != 6:
            return color
        try:
            red = int(value[0:2], 16)
            green = int(value[2:4], 16)
            blue = int(value[4:6], 16)
        except ValueError:
            return color

        ratio = max(0.0, min(1.0, float(white_ratio)))
        red = int(red + (255 - red) * ratio)
        green = int(green + (255 - green) * ratio)
        blue = int(blue + (255 - blue) * ratio)
        return f"#{red:02X}{green:02X}{blue:02X}"

    def _create_fixed_tools_panel(self, parent) -> ctk.CTkFrame:
        """Bloc distinct des groupes : outils de gestion du Maquettage."""
        tools = ctk.CTkFrame(
            parent,
            width=218,
            height=104,
            fg_color="#E7ECF2",
            corner_radius=6,
            border_width=1,
            border_color="#C6D0DB",
        )
        tools.pack_propagate(False)
        tools.grid_propagate(False)
        for column in range(3):
            tools.grid_columnconfigure(column, weight=1, uniform="tools")
        tools.grid_rowconfigure(0, weight=0, minsize=40)
        tools.grid_rowconfigure(1, weight=0, minsize=40)
        tools.grid_rowconfigure(2, weight=0, minsize=18)

        self._undo_button = self._make_ribbon_tool_button(
            tools,
            text="↶\nAnnuler",
            color="#F1E7E2",
            accent=self.CORAL,
            command=self._undo,
        )
        self._undo_button.grid(row=0, column=0, sticky="nsew", padx=2, pady=(2, 1))

        self._redo_button = self._make_ribbon_tool_button(
            tools,
            text="↷\nRétablir",
            color="#E8E1F1",
            accent=self.LILAC,
            command=self._redo,
        )
        self._redo_button.grid(row=1, column=0, sticky="nsew", padx=2, pady=(1, 1))

        self._make_ribbon_tool_button(
            tools,
            text="＋\nCréer",
            color="#E1EEE9",
            accent=self.CELADON,
            command=self._open_create_menu,
        ).grid(row=0, column=1, sticky="nsew", padx=1, pady=(2, 1))

        self._make_ribbon_tool_button(
            tools,
            text="⚙\nGérer",
            color="#F1E8CD",
            accent=self.YELLOW,
            command=self._open_manage_dialog,
        ).grid(row=1, column=1, sticky="nsew", padx=1, pady=(1, 1))

        self._make_ribbon_tool_button(
            tools,
            text="▣\nAperçu",
            color=self.ACCENT_SOFT,
            accent=self.SKY,
            command=self._open_preview,
        ).grid(row=0, column=2, sticky="nsew", padx=(1, 2), pady=(2, 1))

        self._make_ribbon_tool_button(
            tools,
            text="⇄\nRecto-verso",
            color="#E7EEF6",
            accent=self.INK,
            command=self._open_recto_verso_dialog,
        ).grid(row=1, column=2, sticky="nsew", padx=(1, 2), pady=(1, 1))

        tools_title = ctk.CTkFrame(
            tools,
            height=18,
            fg_color="#DCE4EC",
            corner_radius=0,
        )
        tools_title.grid(
            row=2,
            column=0,
            columnspan=3,
            sticky="ew",
            padx=1,
            pady=(1, 1),
        )
        tools_title.grid_propagate(False)
        tools_title.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            tools_title,
            text="Outils de gestion",
            font=(Fonts.FAMILY, 9, "bold"),
            text_color=self.INK,
        ).place(relx=0, rely=0, relwidth=1, relheight=1)

        return tools

    def _make_ribbon_tool_button(
        self,
        parent,
        text: str,
        color: str,
        accent: str,
        command: Callable[[], None] | None,
        state: str = "normal",
    ) -> ctk.CTkButton:
        button = ctk.CTkButton(
            parent,
            text=text,
            height=39,
            corner_radius=5,
            fg_color=self.GROUP_BG,
            hover_color=color,
            text_color=accent,
            border_width=1,
            border_color=self.BORDER,
            font=(Fonts.FAMILY, 9),
            command=command,
            state=state,
        )
        return button

    def _attach_tooltip(self, widget, text: str) -> None:
        """Affiche le libellé complet après un court survol."""
        state: dict[str, Any] = {"after": None, "window": None}

        def hide(_event=None) -> None:
            after_id = state.get("after")
            if after_id is not None:
                try:
                    widget.after_cancel(after_id)
                except Exception:
                    pass
                state["after"] = None

            window = state.get("window")
            if window is not None:
                try:
                    window.destroy()
                except Exception:
                    pass
                state["window"] = None

        def show() -> None:
            state["after"] = None
            try:
                if not widget.winfo_exists():
                    return
                x = int(widget.winfo_pointerx()) + 12
                y = int(widget.winfo_pointery()) + 18
                window = ctk.CTkToplevel(widget)
                window.withdraw()
                window.overrideredirect(True)
                try:
                    window.attributes("-topmost", True)
                except Exception:
                    pass
                tip_frame = ctk.CTkFrame(
                    window,
                    fg_color=self.INK,
                    corner_radius=5,
                    border_width=0,
                )
                tip_frame.pack()
                ctk.CTkLabel(
                    tip_frame,
                    text=text,
                    text_color="#FFFFFF",
                    font=(Fonts.FAMILY, 9),
                ).pack(padx=7, pady=4)
                window.geometry(f"+{x}+{y}")
                window.deiconify()
                state["window"] = window
            except Exception:
                hide()

        def schedule(_event=None) -> None:
            hide()
            try:
                state["after"] = widget.after(550, show)
            except Exception:
                state["after"] = None

        widget.bind("<Enter>", schedule, add="+")
        widget.bind("<Leave>", hide, add="+")
        widget.bind("<ButtonPress-1>", hide, add="+")

    def _select_ribbon_group(self, group_id: str) -> None:
        if not any(
            str(group.get("id", "")) == group_id
            for group in self._groups()
        ):
            return
        if group_id == self._selected_ribbon_group_id:
            return
        self._selected_ribbon_group_id = group_id
        self.show()

    def _refresh_ribbon(self) -> None:
        """Remplace le ruban sans créer de frame vide entre les deux états."""
        self._hide_group_drop_indicator()
        if self._root is None or not self._root.winfo_exists():
            return

        old_ribbon = self._ribbon_frame
        new_ribbon = self._create_ribbon(self._root)

        # Le nouveau ruban est posé AVANT de retirer l'ancien.
        # Cela évite le flash blanc visible lors d'un déplacement.
        self._ribbon_frame = new_ribbon
        new_ribbon.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 8),
        )
        try:
            new_ribbon.lift()
        except Exception:
            pass

        if old_ribbon is not None:
            try:
                self._root.after_idle(old_ribbon.destroy)
            except Exception:
                try:
                    old_ribbon.destroy()
                except Exception:
                    pass

    # ==========================================================
    # Déplacement des groupes personnalisés
    # ==========================================================

    def _bind_custom_group_drag(
        self,
        group_widget: ctk.CTkFrame,
        title_widget: ctk.CTkLabel,
        group_id: str,
    ) -> None:
        """Déplacement des groupes neutralisé provisoirement."""
        return

    def _start_group_drag(self, event, group_id: str) -> None:
        group = self._group_for(group_id)
        if bool(group.get("protected", False)):
            return

        self._dragged_group_id = group_id
        self._drag_group_start_x = int(getattr(event, "x_root", 0))
        self._drag_group_start_y = int(getattr(event, "y_root", 0))
        self._drag_group_has_moved = False

        widget = self._ribbon_group_widgets.get(group_id)
        if widget is not None:
            try:
                widget.configure(
                    border_width=2,
                    border_color=str(group.get("accent", self.INK)),
                )
            except Exception:
                pass

    def _continue_group_drag(self, event) -> None:
        group_id = self._dragged_group_id
        if group_id is None:
            return

        current_x = int(getattr(event, "x_root", self._drag_group_start_x))
        current_y = int(getattr(event, "y_root", self._drag_group_start_y))
        if (
            abs(current_x - self._drag_group_start_x) >= 5
            or abs(current_y - self._drag_group_start_y) >= 5
        ):
            self._drag_group_has_moved = True

        if self._drag_group_has_moved:
            self._show_group_drop_indicator(group_id, current_x, current_y)

    def _finish_group_drag(self, event) -> None:
        group_id = self._dragged_group_id
        moved = self._drag_group_has_moved
        self._dragged_group_id = None
        self._drag_group_has_moved = False
        self._hide_group_drop_indicator()

        if group_id is None:
            return

        widget = self._ribbon_group_widgets.get(group_id)
        if widget is not None and not moved:
            try:
                widget.configure(border_width=0)
            except Exception:
                pass

        if moved:
            pointer_x = int(getattr(event, "x_root", self._drag_group_start_x))
            pointer_y = int(getattr(event, "y_root", self._drag_group_start_y))
            self._place_custom_group_at_pointer(group_id, pointer_x, pointer_y)

    def _custom_group_drop_plan(
        self,
        group_id: str,
        pointer_x: int,
        pointer_y: int,
    ) -> tuple[dict[str, Any], list[dict[str, Any]], int] | None:
        groups = self._groups()
        source = next(
            (
                group
                for group in groups
                if str(group.get("id", "")) == group_id
                and not bool(group.get("protected", False))
            ),
            None,
        )
        if source is None:
            return None

        remaining = [
            group
            for group in groups
            if str(group.get("id", "")) != group_id
        ]

        visual_entries: list[dict[str, Any]] = []
        for logical_index, group in enumerate(remaining):
            candidate_id = str(group.get("id", ""))
            widget = self._ribbon_group_widgets.get(candidate_id)
            if widget is None:
                continue
            try:
                left = int(widget.winfo_rootx())
                top = int(widget.winfo_rooty())
                width = int(widget.winfo_width())
                height = int(widget.winfo_height())
            except Exception:
                continue
            visual_entries.append(
                {
                    "logical_index": logical_index,
                    "left": left,
                    "right": left + width,
                    "top": top,
                    "bottom": top + height,
                    "center_x": left + width / 2,
                    "center_y": top + height / 2,
                }
            )

        insert_at = len(remaining)
        if visual_entries:
            visual_entries.sort(key=lambda entry: (entry["top"], entry["left"]))
            rows: list[list[dict[str, Any]]] = []
            for entry in visual_entries:
                if not rows:
                    rows.append([entry])
                    continue
                row_center = sum(
                    item["center_y"] for item in rows[-1]
                ) / len(rows[-1])
                if abs(entry["center_y"] - row_center) <= 12:
                    rows[-1].append(entry)
                else:
                    rows.append([entry])

            def vertical_distance(row: list[dict[str, Any]]) -> float:
                top = min(item["top"] for item in row)
                bottom = max(item["bottom"] for item in row)
                if top <= pointer_y <= bottom:
                    return 0.0
                return min(abs(pointer_y - top), abs(pointer_y - bottom))

            selected_row = min(rows, key=vertical_distance)
            selected_row.sort(key=lambda entry: entry["left"])

            insert_at = selected_row[-1]["logical_index"] + 1
            for entry in selected_row:
                if pointer_x < entry["center_x"]:
                    insert_at = entry["logical_index"]
                    break

        start_index = next(
            (
                index
                for index, group in enumerate(remaining)
                if str(group.get("id", "")) == "debut_livre"
            ),
            0,
        )
        end_index = next(
            (
                index
                for index, group in enumerate(remaining)
                if str(group.get("id", "")) == "fin_livre"
            ),
            len(remaining),
        )

        insert_at = max(start_index + 1, min(insert_at, end_index))
        return source, remaining, insert_at

    @staticmethod
    def _screen_geometry_for_place(
        parent,
        root_x: float,
        root_y: float,
        width: float,
        height: float,
    ) -> tuple[int, int, int, int]:
        """Convertit les pixels écran en unités de placement CustomTkinter."""
        local_x = float(root_x) - float(parent.winfo_rootx())
        local_y = float(root_y) - float(parent.winfo_rooty())

        reverse_scaling = getattr(parent, "_reverse_widget_scaling", None)
        if callable(reverse_scaling):
            try:
                local_x = float(reverse_scaling(local_x))
                local_y = float(reverse_scaling(local_y))
                width = float(reverse_scaling(width))
                height = float(reverse_scaling(height))
            except Exception:
                pass

        return (
            int(round(local_x)),
            int(round(local_y)),
            max(1, int(round(width))),
            max(1, int(round(height))),
        )

    def _show_group_drop_indicator(
        self,
        group_id: str,
        pointer_x: int,
        pointer_y: int,
    ) -> None:
        """Affiche la ligne sur la frontière réelle entre deux groupes."""
        plan = self._custom_group_drop_plan(group_id, pointer_x, pointer_y)
        overlay = self._root
        if plan is None or overlay is None:
            self._hide_group_drop_indicator()
            return

        _, remaining, insert_at = plan
        if not (0 < insert_at < len(remaining)):
            self._hide_group_drop_indicator()
            return

        previous_id = str(remaining[insert_at - 1].get("id", ""))
        next_id = str(remaining[insert_at].get("id", ""))
        previous_widget = self._ribbon_group_widgets.get(previous_id)
        next_widget = self._ribbon_group_widgets.get(next_id)
        source_widget = self._ribbon_group_widgets.get(group_id)
        if previous_widget is None or next_widget is None:
            self._hide_group_drop_indicator()
            return

        marker_width_px = 4
        try:
            overlay.update_idletasks()
            previous_left = previous_widget.winfo_rootx()
            previous_right = previous_left + previous_widget.winfo_width()
            previous_top = previous_widget.winfo_rooty()
            previous_bottom = previous_top + previous_widget.winfo_height()

            next_left = next_widget.winfo_rootx()
            next_right = next_left + next_widget.winfo_width()
            next_top = next_widget.winfo_rooty()
            next_bottom = next_top + next_widget.winfo_height()

            same_row = abs(previous_top - next_top) <= 12
            if same_row:
                left_widget = previous_widget
                right_widget = next_widget

                if source_widget is not None:
                    source_left = source_widget.winfo_rootx()
                    source_right = source_left + source_widget.winfo_width()
                    source_top = source_widget.winfo_rooty()
                    if (
                        abs(source_top - previous_top) <= 12
                        and previous_right <= source_left
                        and source_right <= next_left
                    ):
                        source_middle = (source_left + source_right) / 2
                        if pointer_x < source_middle:
                            right_widget = source_widget
                            next_left = source_left
                        else:
                            left_widget = source_widget
                            previous_right = source_right

                gap_center = (previous_right + next_left) / 2
                marker_root_x = gap_center - marker_width_px / 2
                marker_top = max(
                    left_widget.winfo_rooty(),
                    right_widget.winfo_rooty(),
                ) + 4
                marker_bottom = min(
                    left_widget.winfo_rooty() + left_widget.winfo_height(),
                    right_widget.winfo_rooty() + right_widget.winfo_height(),
                ) - 4
                marker_height_px = max(18, marker_bottom - marker_top)
            else:
                # À un retour de ligne, l'insertion se matérialise juste avant
                # le premier groupe de la ligne suivante.
                marker_root_x = next_left - 5
                marker_top = next_top + 4
                marker_height_px = max(18, next_bottom - next_top - 8)

            local_x, local_y, marker_width, marker_height = (
                self._screen_geometry_for_place(
                    overlay,
                    marker_root_x,
                    marker_top,
                    marker_width_px,
                    marker_height_px,
                )
            )
        except Exception:
            self._hide_group_drop_indicator()
            return

        if self._group_drop_indicator is None:
            self._group_drop_indicator = ctk.CTkFrame(
                overlay,
                width=marker_width,
                height=marker_height,
                fg_color=self.CORAL,
                corner_radius=2,
                border_width=1,
                border_color=self.INK,
            )

        try:
            self._group_drop_indicator.configure(
                width=marker_width,
                height=marker_height,
            )
            self._group_drop_indicator.place(x=local_x, y=local_y)
            self._group_drop_indicator.lift()
        except Exception:
            self._hide_group_drop_indicator()

    def _hide_group_drop_indicator(self) -> None:
        indicator = self._group_drop_indicator
        self._group_drop_indicator = None
        if indicator is not None:
            try:
                indicator.destroy()
            except Exception:
                pass

    def _place_custom_group_at_pointer(
        self,
        group_id: str,
        pointer_x: int,
        pointer_y: int,
    ) -> None:
        groups = self._groups()
        plan = self._custom_group_drop_plan(group_id, pointer_x, pointer_y)
        if plan is None:
            return

        source, remaining, insert_at = plan
        old_order = [str(group.get("id", "")) for group in groups]
        remaining.insert(insert_at, source)
        new_order = [str(group.get("id", "")) for group in remaining]
        self._selected_ribbon_group_id = group_id

        if new_order == old_order:
            self._refresh_ribbon()
            return

        self._record_history()
        groups[:] = remaining
        self._save_data()
        self._refresh_ribbon()

    # ==========================================================
    # Création de groupes et de types de pages
    # ==========================================================

    def _open_create_menu(self) -> None:
        window = self._new_dialog("Créer", "650x270")

        ctk.CTkLabel(
            window,
            text="Que souhaitez-vous créer ?",
            font=Fonts.H2,
            text_color=self.INK,
        ).pack(pady=(24, 18))

        buttons = ctk.CTkFrame(window, fg_color="transparent")
        buttons.pack(fill="x", padx=28)
        buttons.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkButton(
            buttons,
            text="▦\nNouveau type de page",
            height=92,
            corner_radius=10,
            fg_color=self.MAQUETTAGE_SOFT,
            hover_color="#DCE7F2",
            text_color=self.INK,
            border_width=1,
            border_color=self.SKY,
            font=Fonts.NORMAL,
            command=lambda: self._replace_dialog(
                window,
                self._open_create_page_type_dialog,
            ),
        ).grid(row=0, column=0, sticky="ew", padx=(0, 6))

        ctk.CTkButton(
            buttons,
            text=f"＋\nPartie {self._next_part_number()}",
            height=92,
            corner_radius=10,
            fg_color="#E1EEE9",
            hover_color="#D8E9E1",
            text_color=self.INK,
            border_width=1,
            border_color=self.CELADON,
            font=Fonts.NORMAL,
            command=lambda: self._create_next_part(window),
        ).grid(row=0, column=1, sticky="ew", padx=6)

        ctk.CTkButton(
            buttons,
            text="◇\nGroupe libre",
            height=92,
            corner_radius=10,
            fg_color="#EEE8F5",
            hover_color="#E6DFF0",
            text_color=self.INK,
            border_width=1,
            border_color=self.LILAC,
            font=Fonts.NORMAL,
            command=lambda: self._replace_dialog(
                window,
                self._open_create_group_dialog,
            ),
        ).grid(row=0, column=2, sticky="ew", padx=(6, 0))

        ctk.CTkButton(
            window,
            text="Annuler",
            width=100,
            height=30,
            corner_radius=7,
            fg_color=self.GROUP_BG,
            hover_color=Colors.BUTTON_HOVER,
            text_color=self.INK,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.SMALL,
            command=window.destroy,
        ).pack(pady=(22, 18))

    def _open_manage_dialog(self) -> None:
        """Ouvre le rangement volontaire de la palette de pages."""

        if self._manage_window is not None:
            try:
                if self._manage_window.winfo_exists():
                    self._manage_window.deiconify()
                    self._manage_window.lift()
                    self._manage_window.focus_set()
                    return
            except Exception:
                self._manage_window = None

        # Fenêtre volontairement simple et stable sous Windows :
        # pas de retrait/réapparition, pas de bascule topmost.
        owner = self.parent.winfo_toplevel()
        window = ctk.CTkToplevel(owner)
        self._manage_window = window
        window.title("Gérer les types et groupes")
        window.geometry("720x620")
        window.minsize(620, 500)
        window.resizable(True, True)
        window.configure(fg_color=self.WINDOW_BG)
        window.transient(owner)
        window.protocol("WM_DELETE_WINDOW", self._close_manage_dialog)

        header = ctk.CTkFrame(window, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 10))
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            header,
            text="Nettoyer la palette",
            font=Fonts.H2,
            text_color=self.INK,
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            header,
            text=(
                "Seuls les groupes et types créés par l’utilisateur "
                "peuvent être supprimés."
            ),
            font=Fonts.SMALL,
            text_color=self.TEXT_MUTED,
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))

        body = ctk.CTkScrollableFrame(
            window,
            fg_color=self.RIBBON_BG,
            corner_radius=8,
        )
        body.pack(fill="both", expand=True, padx=24, pady=(0, 12))
        body.grid_columnconfigure(0, weight=1)

        custom_types = [
            definition
            for definition in self._page_types()
            if (
                bool(definition.get("custom", False))
                and not bool(definition.get("deleted", False))
            )
        ]
        custom_groups = [
            group
            for group in self._groups()
            if (
                not bool(group.get("protected", False))
                and not bool(group.get("deleted", False))
            )
        ]

        row = 0
        ctk.CTkLabel(
            body,
            text="Types de pages personnalisés",
            font=Fonts.NORMAL,
            text_color=self.INK,
        ).grid(row=row, column=0, sticky="w", padx=10, pady=(12, 6))
        row += 1

        if custom_types:
            for definition in custom_types:
                self._create_manage_type_row(
                    body,
                    definition,
                    window,
                ).grid(
                    row=row,
                    column=0,
                    sticky="ew",
                    padx=8,
                    pady=3,
                )
                row += 1
        else:
            ctk.CTkLabel(
                body,
                text="Aucun type personnalisé à retirer.",
                font=Fonts.SMALL,
                text_color=self.TEXT_LIGHT,
            ).grid(row=row, column=0, sticky="w", padx=16, pady=(2, 10))
            row += 1

        ctk.CTkFrame(
            body,
            height=1,
            fg_color=self.BORDER,
            corner_radius=0,
        ).grid(row=row, column=0, sticky="ew", padx=10, pady=12)
        row += 1

        ctk.CTkLabel(
            body,
            text="Groupes personnalisés",
            font=Fonts.NORMAL,
            text_color=self.INK,
        ).grid(row=row, column=0, sticky="w", padx=10, pady=(0, 6))
        row += 1

        if custom_groups:
            for group in custom_groups:
                self._create_manage_group_row(
                    body,
                    group,
                    window,
                ).grid(
                    row=row,
                    column=0,
                    sticky="ew",
                    padx=8,
                    pady=3,
                )
                row += 1
        else:
            ctk.CTkLabel(
                body,
                text="Aucun groupe personnalisé à retirer.",
                font=Fonts.SMALL,
                text_color=self.TEXT_LIGHT,
            ).grid(row=row, column=0, sticky="w", padx=16, pady=(2, 10))

        ctk.CTkButton(
            window,
            text="Fermer",
            width=104,
            height=32,
            corner_radius=7,
            fg_color=self.GROUP_BG,
            hover_color=Colors.BUTTON_HOVER,
            text_color=self.INK,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.SMALL,
            command=self._close_manage_dialog,
        ).pack(pady=(0, 20))

        # Le grab est posé seulement après la construction complète.
        def activate() -> None:
            try:
                if window.winfo_exists():
                    window.lift()
                    window.focus_set()
                    window.grab_set()
            except Exception:
                pass

        window.after(120, activate)

    def _create_manage_type_row(
        self,
        parent,
        definition: dict[str, Any],
        owner,
    ) -> ctk.CTkFrame:
        row = ctk.CTkFrame(
            parent,
            height=56,
            fg_color=self.GROUP_BG,
            corner_radius=7,
            border_width=1,
            border_color=self.BORDER,
        )
        row.grid_columnconfigure(1, weight=1)
        row.grid_propagate(False)

        accent = str(definition.get("accent", self.INK))
        ctk.CTkLabel(
            row,
            text=str(definition.get("symbol", "▦")),
            width=34,
            font=(Fonts.FAMILY, 14, "bold"),
            text_color=accent,
        ).grid(row=0, column=0, padx=(7, 3))

        group = self._group_for(str(definition.get("group", "")))
        thumbnail_mode = (
            "Image personnalisée"
            if str(definition.get("thumbnail", "")).strip()
            else "Image générique"
        )
        ctk.CTkLabel(
            row,
            text=(
                f"{definition.get('title', 'Type de page')}"
                f"   ·   {group.get('title', 'Groupe')}"
                f"   ·   {thumbnail_mode}"
            ),
            font=Fonts.SMALL,
            text_color=self.INK,
            anchor="w",
        ).grid(row=0, column=1, sticky="ew", padx=5)

        page_type = str(definition.get("type", ""))
        used_count = sum(
            max(1, int(item.get("count", 1)))
            for item in self._items()
            if str(item.get("type", "")) == page_type
        )
        status = "Non utilisé" if used_count == 0 else f"Utilisé : {used_count} p."
        ctk.CTkLabel(
            row,
            text=status,
            width=82,
            font=Fonts.SMALL,
            text_color=self.TEXT_MUTED,
        ).grid(row=0, column=2, padx=4)

        ctk.CTkButton(
            row,
            text="Image…",
            width=64,
            height=28,
            corner_radius=6,
            fg_color=self.GROUP_BG,
            hover_color=self.ACCENT_SOFT,
            text_color=self.INK,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.SMALL,
            command=lambda: self._replace_custom_thumbnail(
                page_type,
                owner,
            ),
        ).grid(row=0, column=3, padx=2)

        ctk.CTkButton(
            row,
            text="Générique",
            width=70,
            height=28,
            corner_radius=6,
            fg_color=self.GROUP_BG,
            hover_color=Colors.BUTTON_HOVER,
            text_color=self.TEXT_MUTED,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.SMALL,
            command=lambda: self._reset_custom_thumbnail(
                page_type,
                owner,
            ),
        ).grid(row=0, column=4, padx=2)

        ctk.CTkButton(
            row,
            text="Supprimer",
            width=76,
            height=28,
            corner_radius=6,
            fg_color=self.GROUP_BG,
            hover_color="#F3E4E1",
            text_color=self.DANGER,
            border_width=1,
            border_color="#E0B9B0",
            font=Fonts.SMALL,
            state="normal" if used_count == 0 else "disabled",
            command=lambda: self._delete_custom_page_type(page_type, owner),
        ).grid(row=0, column=5, padx=(2, 7))

        return row

    def _create_manage_group_row(
        self,
        parent,
        group: dict[str, Any],
        owner,
    ) -> ctk.CTkFrame:
        row = ctk.CTkFrame(
            parent,
            height=48,
            fg_color=self.GROUP_BG,
            corner_radius=7,
            border_width=1,
            border_color=self.BORDER,
        )
        row.grid_columnconfigure(1, weight=1)
        row.grid_propagate(False)

        accent = str(group.get("accent", self.INK))
        ctk.CTkLabel(
            row,
            text=str(group.get("symbol", "▦")),
            width=38,
            font=(Fonts.FAMILY, 15, "bold"),
            text_color=accent,
        ).grid(row=0, column=0, padx=(8, 3))

        ctk.CTkLabel(
            row,
            text=str(group.get("title", "Groupe")),
            font=Fonts.SMALL,
            text_color=self.INK,
            anchor="w",
        ).grid(row=0, column=1, sticky="ew", padx=5)

        group_id = str(group.get("id", ""))
        type_count = sum(
            1
            for definition in self._page_types()
            if (
                str(definition.get("group", "")) == group_id
                and not bool(definition.get("deleted", False))
            )
        )
        status = "Vide" if type_count == 0 else f"{type_count} type(s)"
        ctk.CTkLabel(
            row,
            text=status,
            width=92,
            font=Fonts.SMALL,
            text_color=self.TEXT_MUTED,
        ).grid(row=0, column=2, padx=6)

        movable = self._can_reorder_group(group)

        ctk.CTkButton(
            row, text="↑", width=32, height=28, corner_radius=6,
            fg_color=self.GROUP_BG, hover_color=Colors.BUTTON_HOVER,
            text_color=self.INK, border_width=1, border_color=self.BORDER,
            font=Fonts.SMALL, state="normal" if movable else "disabled",
            command=lambda: self._move_group_step(group_id, -1, owner),
        ).grid(row=0, column=3, padx=(2, 1))

        ctk.CTkButton(
            row, text="↓", width=32, height=28, corner_radius=6,
            fg_color=self.GROUP_BG, hover_color=Colors.BUTTON_HOVER,
            text_color=self.INK, border_width=1, border_color=self.BORDER,
            font=Fonts.SMALL, state="normal" if movable else "disabled",
            command=lambda: self._move_group_step(group_id, 1, owner),
        ).grid(row=0, column=4, padx=1)

        ctk.CTkButton(
            row,
            text="Supprimer",
            width=82,
            height=28,
            corner_radius=6,
            fg_color=self.GROUP_BG,
            hover_color="#F3E4E1",
            text_color=self.DANGER,
            border_width=1,
            border_color="#E0B9B0",
            font=Fonts.SMALL,
            state="normal" if type_count == 0 else "disabled",
            command=lambda: self._delete_custom_group(group_id, owner),
        ).grid(row=0, column=5, padx=(4, 8))

        return row

    def _delete_custom_page_type(self, page_type: str, owner) -> None:
        if any(
            str(item.get("type", "")) == page_type
            for item in self._items()
        ):
            return

        definitions = self._page_types()
        target_index = next(
            (
                index
                for index, definition in enumerate(definitions)
                if (
                    str(definition.get("type", "")) == page_type
                    and bool(definition.get("custom", False))
                    and not bool(definition.get("deleted", False))
                )
            ),
            None,
        )
        if target_index is None:
            return

        target = definitions[target_index]
        self._record_history()

        target["deleted"] = True
        target["deleted_kind"] = "page_type"
        target["deleted_original_index"] = target_index
        target["deleted_original_group"] = str(target.get("group", ""))
        target["deleted_original_title"] = str(target.get("title", "")).strip()
        target["deleted_label"] = str(
            target.get("short")
            or target.get("title")
            or "Type"
        ).strip()

        self._save_data()
        self._close_dialog(owner)
        self._refresh_ribbon()

    def _can_reorder_group(self, group: dict[str, Any]) -> bool:
        return not bool(group.get("deleted", False)) and not bool(group.get("protected", False))

    def _move_group_step(self, group_id: str, delta: int, owner=None) -> None:
        groups = self._groups()
        current_index = next((i for i, g in enumerate(groups) if str(g.get("id", "")) == group_id and not bool(g.get("deleted", False))), None)
        if current_index is None or not self._can_reorder_group(groups[current_index]):
            return
        direction = -1 if delta < 0 else 1
        target_index = current_index + direction
        while 0 <= target_index < len(groups):
            target = groups[target_index]
            if bool(target.get("deleted", False)):
                target_index += direction
                continue
            if bool(target.get("protected", False)):
                return
            if self._can_reorder_group(target):
                self._record_history()
                groups[current_index], groups[target_index] = groups[target_index], groups[current_index]
                self._save_data()
                if owner is not None:
                    self._close_dialog(owner)
                self._refresh_ribbon()
                return
            target_index += direction

    def _delete_custom_group(self, group_id: str, owner) -> None:
        if any(
            (
                str(definition.get("group", "")) == group_id
                and not bool(definition.get("deleted", False))
            )
            for definition in self._page_types()
        ):
            return

        groups = self._groups()
        target = next(
            (
                group
                for group in groups
                if str(group.get("id", "")) == group_id
                and not bool(group.get("protected", False))
            ),
            None,
        )
        if target is None:
            return

        title = str(target.get("title", "")).strip()

        # Un ouvrage doit toujours conserver au moins une Partie active.
        if title.startswith("Partie "):
            active_parts = [
                group
                for group in groups
                if (
                    str(group.get("title", "")).strip().startswith("Partie ")
                    and not bool(group.get("deleted", False))
                )
            ]
            if len(active_parts) <= 1:
                self._close_dialog(owner)
                warning = self._new_dialog(
                    "Suppression impossible",
                    "430x205",
                )
                ctk.CTkLabel(
                    warning,
                    text=(
                        "Le livre doit conserver au moins une Partie active.\n\n"
                        "Créez une nouvelle Partie avant de supprimer celle-ci."
                    ),
                    font=Fonts.NORMAL,
                    text_color=self.INK,
                    justify="center",
                    wraplength=365,
                ).pack(padx=24, pady=(38, 24))
                ctk.CTkButton(
                    warning,
                    text="Fermer",
                    width=110,
                    height=34,
                    corner_radius=7,
                    fg_color=self.GROUP_BG,
                    hover_color=Colors.BUTTON_HOVER,
                    text_color=self.INK,
                    border_width=1,
                    border_color=self.BORDER,
                    font=Fonts.SMALL,
                    command=warning.destroy,
                ).pack()
                return

        self._record_history()

        original_index = groups.index(target)
        target["deleted"] = True
        target["deleted_original_index"] = original_index
        target["deleted_original_title"] = title

        if title.startswith("Partie "):
            number_text = title.removeprefix("Partie ").split("—", 1)[0].strip()
            target["deleted_kind"] = "partie"
            target["deleted_label"] = (
                f"P{number_text}" if number_text.isdigit() else title
            )
            target["title"] = (
                f"Partie {number_text} — supprimée"
                if number_text.isdigit()
                else f"{title} — supprimée"
            )
        else:
            # Le groupe libre conserve son nom pour l'historique.
            target["deleted_kind"] = "groupe_libre"
            target["deleted_label"] = title
            target["title"] = f"{title} — supprimé"

        self._save_data()
        self._close_dialog(owner)
        self._refresh_ribbon()

    def _group_for(self, group_id: str) -> dict[str, Any]:
        for group in self._groups():
            if str(group.get("id", "")) == group_id:
                return group
        return {
            "id": "",
            "title": "Groupe inconnu",
            "symbol": "?",
            "accent": self.INK,
            "protected": True,
        }

    def _next_part_number(self) -> int:
        """Retourne le prochain numéro de Partie, y compris après suppression."""
        highest = 1
        for group in self._groups():
            title = str(group.get("title", "")).strip()
            if not title.startswith("Partie "):
                continue
            suffix = title.removeprefix("Partie ").strip()
            number_text = suffix.split("—", 1)[0].strip()
            if number_text.isdigit():
                highest = max(highest, int(number_text))
        return highest + 1

    def _create_next_part(self, owner) -> None:
        """Crée Partie N immédiatement après Partie N-1."""
        number = self._next_part_number()
        previous_number = number - 1
        groups = self._groups()

        previous_index = None
        for index, group in enumerate(groups):
            title = str(group.get("title", "")).strip()
            if not title.startswith("Partie "):
                continue
            number_text = (
                title.removeprefix("Partie ")
                .split("—", 1)[0]
                .strip()
            )
            if number_text.isdigit() and int(number_text) == previous_number:
                previous_index = index
                break

        if previous_index is None:
            return

        existing_ids = {str(group.get("id", "")) for group in groups}
        base_id = f"partie_{number}"
        group_id = base_id
        suffix = 2
        while group_id in existing_ids:
            group_id = f"{base_id}_{suffix}"
            suffix += 1

        previous_group = groups[previous_index]
        new_group = {
            "id": group_id,
            "title": f"Partie {number}",
            "symbol": str(previous_group.get("symbol") or "▦"),
            "accent": str(previous_group.get("accent") or self.SKY),
            "protected": False,
        }

        self._record_history()
        groups.insert(previous_index + 1, new_group)
        self._save_data()
        try:
            owner.destroy()
        except Exception:
            pass
        self._selected_ribbon_group_id = group_id
        self._refresh_ribbon()

    def _open_create_group_dialog(self) -> None:
        window = self._new_dialog("Nouveau groupe de pages", "560x520")
        body = self._dialog_body(window)

        name_entry = self._dialog_entry(body, 0, "Nom du groupe")

        color_names = list(self.GROUP_COLOR_CHOICES)
        color_var = ctk.StringVar(value=color_names[0])
        self._dialog_option(body, 1, "Couleur", color_var, color_names)

        icon_var = ctk.StringVar(value=self.ICON_CHOICES[0])
        self._dialog_option(
            body,
            2,
            "Icône",
            icon_var,
            list(self.ICON_CHOICES),
        )

        movable_predecessors = [
            group
            for group in self._groups()
            if (
                str(group.get("id", "")) != "fin_livre"
                and not bool(group.get("deleted", False))
            )
        ]
        group_titles = [
            str(group.get("title", "Groupe"))
            for group in movable_predecessors
        ]
        position_values = ["À la fin"] + [
            f"Après : {title}"
            for title in group_titles
        ]
        position_var = ctk.StringVar(value="À la fin")
        self._dialog_option(
            body,
            3,
            "Position",
            position_var,
            position_values,
        )

        message = self._dialog_message(body, 4)

        self._dialog_actions(
            window,
            on_cancel=window.destroy,
            on_validate=lambda: self._create_group_from_dialog(
                window,
                name_entry.get(),
                color_var.get(),
                icon_var.get(),
                position_var.get(),
                message,
            ),
        )

    def _open_create_page_type_dialog(self) -> None:
        window = self._new_dialog("Nouveau type de page", "610x760")
        body = self._dialog_body(window)

        name_entry = self._dialog_entry(body, 0, "Nom du type de page")
        short_entry = self._dialog_entry(body, 1, "Nom court dans le bouton")

        groups = [
            group
            for group in self._groups()
            if not bool(group.get("deleted", False))
        ]
        group_titles = [str(group.get("title", "Groupe")) for group in groups]
        group_var = ctk.StringVar(value=group_titles[0] if group_titles else "")
        self._dialog_option(body, 2, "Groupe", group_var, group_titles)

        color_names = list(self.TYPE_COLOR_CHOICES)
        color_var = ctk.StringVar(value=color_names[0])
        self._dialog_option(body, 3, "Couleur", color_var, color_names)

        icon_var = ctk.StringVar(value=self.ICON_CHOICES[0])
        self._dialog_option(
            body,
            4,
            "Icône",
            icon_var,
            list(self.ICON_CHOICES),
        )

        thumbnail_source = ctk.StringVar(value="")
        ctk.CTkLabel(
            body,
            text="Miniature de page",
            font=Fonts.SMALL,
            text_color=self.INK,
        ).grid(row=10, column=0, sticky="w", pady=(10, 4))

        thumbnail_box = ctk.CTkFrame(
            body,
            fg_color="#F1F6F9",
            corner_radius=7,
            border_width=1,
            border_color=self.BORDER,
        )
        thumbnail_box.grid(row=11, column=0, sticky="ew")
        thumbnail_box.grid_columnconfigure(0, weight=1)

        thumbnail_status = ctk.CTkLabel(
            thumbnail_box,
            text="Image générique PageMaître · PNG 300 × 424 px",
            font=Fonts.SMALL,
            text_color=self.TEXT_MUTED,
            anchor="w",
        )
        thumbnail_status.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=9,
            pady=7,
        )

        ctk.CTkButton(
            thumbnail_box,
            text="Choisir…",
            width=82,
            height=26,
            corner_radius=5,
            fg_color=self.GROUP_BG,
            hover_color=self.ACCENT_SOFT,
            text_color=self.INK,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.SMALL,
            command=lambda: self._choose_thumbnail_for_dialog(
                window,
                thumbnail_source,
                thumbnail_status,
            ),
        ).grid(row=0, column=1, padx=(4, 3), pady=5)

        ctk.CTkButton(
            thumbnail_box,
            text="Générique",
            width=82,
            height=26,
            corner_radius=5,
            fg_color=self.GROUP_BG,
            hover_color=Colors.BUTTON_HOVER,
            text_color=self.TEXT_MUTED,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.SMALL,
            command=lambda: self._reset_thumbnail_dialog_choice(
                thumbnail_source,
                thumbnail_status,
            ),
        ).grid(row=0, column=2, padx=(3, 7), pady=5)

        ctk.CTkLabel(
            body,
            text="Description",
            font=Fonts.SMALL,
            text_color=self.INK,
        ).grid(row=12, column=0, sticky="w", pady=(10, 4))

        description = ctk.CTkTextbox(
            body,
            height=70,
            corner_radius=7,
            border_width=1,
            border_color=self.BORDER,
            fg_color=self.GROUP_BG,
            text_color=self.INK,
            font=Fonts.SMALL,
        )
        description.grid(row=13, column=0, sticky="ew")

        single_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            body,
            text="Ce type ne peut apparaître qu’une seule fois",
            variable=single_var,
            checkbox_width=18,
            checkbox_height=18,
            fg_color=self.CELADON,
            hover_color=self.DONE,
            text_color=self.INK,
            font=Fonts.SMALL,
        ).grid(row=14, column=0, sticky="w", pady=(12, 0))

        message = self._dialog_message(body, 8)

        self._dialog_actions(
            window,
            on_cancel=window.destroy,
            on_validate=lambda: self._create_page_type_from_dialog(
                window,
                name_entry.get(),
                short_entry.get(),
                group_var.get(),
                color_var.get(),
                icon_var.get(),
                description.get("1.0", "end").strip(),
                single_var.get(),
                thumbnail_source.get(),
                message,
            ),
        )

    def _create_group_from_dialog(
        self,
        window,
        name: str,
        color_name: str,
        symbol: str,
        position: str,
        message: ctk.CTkLabel,
    ) -> None:
        title = name.strip()
        if not title:
            message.configure(text="Indiquez un nom pour le groupe.")
            return

        if any(
            str(group.get("title", "")).casefold() == title.casefold()
            for group in self._groups()
        ):
            message.configure(text="Un groupe porte déjà ce nom.")
            return

        group_id = self._unique_identifier(
            title,
            {str(group.get("id")) for group in self._groups()},
        )
        new_group = {
            "id": group_id,
            "title": title,
            "symbol": symbol or "▦",
            "accent": self.GROUP_COLOR_CHOICES.get(color_name, self.SKY),
            "protected": False,
        }

        groups = self._groups()
        fin_index = next(
            (
                index
                for index, group in enumerate(groups)
                if str(group.get("id", "")) == "fin_livre"
            ),
            len(groups),
        )
        insert_at = fin_index
        if position.startswith("Après : "):
            selected_title = position.removeprefix("Après : ")
            for index, group in enumerate(groups):
                if str(group.get("title", "")) == selected_title:
                    insert_at = min(index + 1, fin_index)
                    break

        # Début du livre reste toujours le premier groupe et Fin du livre
        # reste toujours le dernier.
        insert_at = max(1, min(insert_at, fin_index))
        self._record_history()
        groups.insert(insert_at, new_group)
        self._save_data()
        self._close_dialog(window)
        self._refresh_ribbon()

    def _create_page_type_from_dialog(
        self,
        window,
        name: str,
        short_name: str,
        group_title: str,
        color_name: str,
        symbol: str,
        description: str,
        single: bool,
        thumbnail_source: str,
        message: ctk.CTkLabel,
    ) -> None:
        title = name.strip()
        if not title:
            message.configure(text="Indiquez un nom pour le type de page.")
            return

        if any(
            str(definition.get("title", "")).casefold() == title.casefold()
            for definition in self._page_types()
        ):
            message.configure(text="Un type de page porte déjà ce nom.")
            return

        selected_group = next(
            (
                group
                for group in self._groups()
                if str(group.get("title", "")) == group_title
            ),
            None,
        )
        if selected_group is None:
            message.configure(text="Choisissez un groupe valide.")
            return

        existing_ids = {str(item.get("type")) for item in self._page_types()}
        page_type_id = self._unique_identifier(title, existing_ids)
        background, accent = self.TYPE_COLOR_CHOICES.get(
            color_name,
            self.TYPE_COLOR_CHOICES["Bleu ciel"],
        )

        thumbnail_value = ""
        if thumbnail_source.strip():
            imported, error = self._import_custom_thumbnail(
                thumbnail_source.strip(),
                page_type_id,
            )
            if error:
                message.configure(text=error)
                return
            thumbnail_value = imported

        definition = {
            "type": page_type_id,
            "title": title,
            "short": (short_name.strip() or title)[:18],
            "symbol": symbol or "▦",
            "color": background,
            "accent": accent,
            "group": str(selected_group.get("id")),
            "single": bool(single),
            "description": description,
            "thumbnail": thumbnail_value,
            "custom": True,
        }

        self._record_history()
        self._page_types().append(definition)
        self._save_data()
        self._close_dialog(window)
        self._refresh_ribbon()
        self._refresh_sequence()

    def _new_dialog(
        self,
        title: str,
        geometry: str,
        *,
        modal: bool = True,
    ) -> ctk.CTkToplevel:
        owner = self.parent.winfo_toplevel()
        window = ctk.CTkToplevel(owner)
        window.withdraw()
        window.title(title)
        window.geometry(geometry)
        window.resizable(False, False)
        window.configure(fg_color=self.WINDOW_BG)
        window.transient(owner)
        window.protocol(
            "WM_DELETE_WINDOW",
            lambda current=window: self._close_dialog(current),
        )
        window.bind(
            "<Destroy>",
            lambda event, current=window: self._dialog_destroyed(
                event,
                current,
            ),
            add="+",
        )

        self._center_dialog(window, owner, geometry)
        window.deiconify()
        window.after_idle(
            lambda current=window, use_grab=modal: self._activate_dialog(
                current,
                use_grab,
            )
        )
        return window

    def _activate_dialog(self, window, modal: bool) -> None:
        if not self._dialog_exists(window):
            return

        self._bring_dialog_to_front(window)
        if modal:
            try:
                window.grab_set()
            except Exception:
                # La fenêtre reste utilisable même si Windows refuse
                # momentanément la prise de focus.
                pass

    def _bring_dialog_to_front(self, window) -> None:
        if not self._dialog_exists(window):
            return

        try:
            window.deiconify()
            window.lift()
            window.attributes("-topmost", True)
            window.after(120, lambda: self._remove_temporary_topmost(window))
            window.focus_force()
        except Exception:
            pass

    def _remove_temporary_topmost(self, window) -> None:
        if not self._dialog_exists(window):
            return
        try:
            window.attributes("-topmost", False)
        except Exception:
            pass

    def _close_manage_dialog(self) -> None:
        window = self._manage_window
        self._manage_window = None
        if window is not None:
            self._close_dialog(window)

    def _close_dialog(self, window) -> None:
        if window is None:
            return

        try:
            if window.grab_current() is window:
                window.grab_release()
        except Exception:
            pass

        if self._manage_window is window:
            self._manage_window = None

        try:
            if window.winfo_exists():
                window.destroy()
        except Exception:
            pass

    def _dialog_destroyed(self, event, window) -> None:
        if getattr(event, "widget", None) is not window:
            return
        if self._manage_window is window:
            self._manage_window = None

    @staticmethod
    def _dialog_exists(window) -> bool:
        try:
            return bool(window is not None and window.winfo_exists())
        except Exception:
            return False

    @staticmethod
    def _center_dialog(window, owner, geometry: str) -> None:
        match = re.match(r"^(\d+)x(\d+)", geometry)
        if match is None:
            return

        width = int(match.group(1))
        height = int(match.group(2))
        try:
            owner.update_idletasks()
            x = owner.winfo_rootx() + max(0, (owner.winfo_width() - width) // 2)
            y = owner.winfo_rooty() + max(0, (owner.winfo_height() - height) // 2)
            window.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            pass

    def _replace_dialog(self, window, callback) -> None:
        self._close_dialog(window)
        self.parent.after_idle(callback)

    def _dialog_body(self, window) -> ctk.CTkFrame:
        body = ctk.CTkFrame(window, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=28, pady=(22, 8))
        body.grid_columnconfigure(0, weight=1)
        return body

    def _dialog_entry(self, parent, row: int, label: str) -> ctk.CTkEntry:
        ctk.CTkLabel(
            parent,
            text=label,
            font=Fonts.SMALL,
            text_color=self.INK,
        ).grid(row=row * 2, column=0, sticky="w", pady=(7 if row else 0, 4))

        entry = ctk.CTkEntry(
            parent,
            height=34,
            corner_radius=7,
            border_width=1,
            border_color=self.BORDER,
            fg_color=self.GROUP_BG,
            text_color=self.INK,
            font=Fonts.NORMAL,
        )
        entry.grid(row=row * 2 + 1, column=0, sticky="ew")
        return entry

    def _dialog_option(
        self,
        parent,
        row: int,
        label: str,
        variable: ctk.StringVar,
        values: list[str],
    ) -> None:
        base_row = row * 2
        ctk.CTkLabel(
            parent,
            text=label,
            font=Fonts.SMALL,
            text_color=self.INK,
        ).grid(row=base_row, column=0, sticky="w", pady=(10, 4))

        ctk.CTkOptionMenu(
            parent,
            variable=variable,
            values=values or [""],
            height=34,
            corner_radius=7,
            fg_color=self.ACCENT_SOFT,
            button_color=self.SKY,
            button_hover_color=self.INK,
            text_color=self.INK,
            font=Fonts.SMALL,
            dropdown_font=Fonts.SMALL,
        ).grid(row=base_row + 1, column=0, sticky="ew")

    def _dialog_message(self, parent, row: int) -> ctk.CTkLabel:
        label = ctk.CTkLabel(
            parent,
            text="",
            font=Fonts.SMALL,
            text_color=self.DANGER,
            anchor="w",
        )
        label.grid(row=row * 2, column=0, sticky="ew", pady=(8, 0))
        return label

    def _dialog_actions(self, window, on_cancel, on_validate) -> None:
        actions = ctk.CTkFrame(window, fg_color="transparent")
        actions.pack(fill="x", padx=28, pady=(0, 22))
        actions.grid_columnconfigure(0, weight=1)

        ctk.CTkButton(
            actions,
            text="Annuler",
            width=100,
            height=32,
            corner_radius=7,
            fg_color=self.GROUP_BG,
            hover_color=Colors.BUTTON_HOVER,
            text_color=self.INK,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.SMALL,
            command=on_cancel,
        ).grid(row=0, column=0, sticky="e", padx=(0, 8))

        ctk.CTkButton(
            actions,
            text="Créer",
            width=108,
            height=32,
            corner_radius=7,
            fg_color=self.CELADON,
            hover_color=self.DONE,
            text_color="#FFFFFF",
            font=Fonts.SMALL,
            command=on_validate,
        ).grid(row=0, column=1, sticky="e")

    @staticmethod
    def _unique_identifier(label: str, existing: set[str]) -> str:
        base = re.sub(r"[^a-z0-9]+", "_", label.casefold()).strip("_")
        base = base or "element"
        candidate = base
        suffix = 2
        while candidate in existing:
            candidate = f"{base}_{suffix}"
            suffix += 1
        return candidate

    def _create_sequence_panel(self, parent) -> ctk.CTkFrame:
        """Plan du livre : rail de cartes + panneau contextuel à droite."""
        panel = ctk.CTkFrame(
            parent,
            fg_color=self.CARD_BG,
            corner_radius=8,
            border_width=1,
            border_color=self.BORDER,
        )
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        title_row = ctk.CTkFrame(panel, fg_color="transparent", height=36)
        title_row.grid(row=0, column=0, sticky="ew", padx=12, pady=(6, 5))
        title_row.grid_columnconfigure(0, weight=1)
        title_row.grid_propagate(False)

        ctk.CTkLabel(
            title_row,
            text="Plan du livre",
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

        workspace = ctk.CTkFrame(
            panel,
            fg_color="transparent",
            corner_radius=0,
        )
        workspace.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=10,
            pady=(0, 8),
        )
        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_columnconfigure(1, weight=0)
        workspace.grid_rowconfigure(0, weight=1)

        rail_shell = ctk.CTkFrame(
            workspace,
            fg_color=self.RIBBON_BG,
            corner_radius=7,
            border_width=1,
            border_color=self.BORDER,
        )
        rail_shell.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 8),
        )
        rail_shell.grid_columnconfigure(0, weight=1)
        rail_shell.grid_rowconfigure(1, weight=1)

        rail_hint = ctk.CTkFrame(
            rail_shell,
            height=30,
            fg_color="#F1F6F9",
            corner_radius=6,
        )
        rail_hint.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=6,
            pady=(6, 2),
        )
        rail_hint.grid_propagate(False)

        ctk.CTkLabel(
            rail_hint,
            text="Glisser-déposer pour déplacer · Ctrl pour ajouter · Maj pour une plage",
            font=Fonts.SMALL,
            text_color=self.TEXT_MUTED,
            anchor="w",
        ).pack(side="left", padx=9)

        self._sequence_frame = ctk.CTkScrollableFrame(
            rail_shell,
            fg_color=self.RIBBON_BG,
            corner_radius=6,
        )
        self._sequence_frame.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=4,
            pady=(2, 4),
        )
        self._sequence_frame.grid_columnconfigure(0, weight=1)

        # FOND_DISCRET_PLAN_LIVRE_V1
        self._install_plan_background()

        # Panneau contextuel : les commandes ne flottent plus au bout de l'écran.
        context = ctk.CTkFrame(
            workspace,
            width=350,
            fg_color="#FBFCFD",
            corner_radius=8,
            border_width=1,
            border_color="#D8E2E9",
        )
        context.grid(
            row=0,
            column=1,
            sticky="ns",
        )
        context.grid_propagate(False)
        context.grid_columnconfigure(0, weight=1)

        context_header = ctk.CTkFrame(
            context,
            height=42,
            fg_color=self.MAQUETTAGE_SOFT,
            corner_radius=7,
        )
        context_header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=6,
            pady=6,
        )
        context_header.grid_columnconfigure(0, weight=1)
        context_header.grid_propagate(False)

        self._selection_label = ctk.CTkLabel(
            context_header,
            text="Aucune page sélectionnée",
            font=(Fonts.FAMILY, 10, "bold"),
            text_color=self.INK,
            anchor="w",
        )
        self._selection_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=(10, 5),
        )

        self._context_clear_button = ctk.CTkButton(
            context_header,
            text="×",
            width=26,
            height=24,
            corner_radius=5,
            fg_color=self.GROUP_BG,
            hover_color=Colors.BUTTON_HOVER,
            text_color=self.TEXT_MUTED,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.SMALL,
            command=self._clear_page_selection,
        )
        self._context_clear_button.grid(
            row=0,
            column=1,
            padx=(2, 6),
        )

        self._context_title_label = ctk.CTkLabel(
            context,
            text="Sélectionnez une page",
            font=Fonts.NORMAL,
            text_color=self.INK,
            anchor="w",
            justify="left",
        )
        self._context_title_label.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=14,
            pady=(10, 2),
        )

        self._context_detail_label = ctk.CTkLabel(
            context,
            text="Les commandes de la page apparaîtront ici.",
            font=Fonts.SMALL,
            text_color=self.TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=310,
        )
        self._context_detail_label.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=14,
            pady=(0, 12),
        )

        self._context_quantity_frame = ctk.CTkFrame(
            context,
            fg_color="#F1F6F9",
            corner_radius=6,
            border_width=1,
            border_color=self.BORDER,
        )
        self._context_quantity_frame.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=12,
            pady=(2, 8),
        )
        self._context_quantity_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            self._context_quantity_frame,
            text="Quantité",
            font=Fonts.SMALL,
            text_color=self.INK,
        ).grid(row=0, column=0, padx=(9, 8), pady=7)

        self._context_minus_button = ctk.CTkButton(
            self._context_quantity_frame,
            text="−",
            width=28,
            height=26,
            corner_radius=5,
            fg_color=self.GROUP_BG,
            hover_color=Colors.BUTTON_HOVER,
            text_color=self.INK,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.NORMAL,
        )
        self._context_minus_button.grid(row=0, column=2, padx=2, pady=5)

        self._context_count_label = ctk.CTkLabel(
            self._context_quantity_frame,
            text="1",
            width=34,
            font=(Fonts.FAMILY, 10, "bold"),
            text_color=self.INK,
        )
        self._context_count_label.grid(row=0, column=3, padx=2)

        self._context_plus_button = ctk.CTkButton(
            self._context_quantity_frame,
            text="+",
            width=28,
            height=26,
            corner_radius=5,
            fg_color=self.GROUP_BG,
            hover_color=Colors.BUTTON_HOVER,
            text_color=self.INK,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.NORMAL,
        )
        self._context_plus_button.grid(row=0, column=4, padx=(2, 7), pady=5)

        move_frame = ctk.CTkFrame(context, fg_color="transparent")
        move_frame.grid(
            row=4,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 7),
        )
        move_frame.grid_columnconfigure(0, weight=1)
        move_frame.grid_columnconfigure(1, weight=1)

        self._context_up_button = ctk.CTkButton(
            move_frame,
            text="↑  Monter",
            height=30,
            corner_radius=6,
            fg_color=self.GROUP_BG,
            hover_color=Colors.BUTTON_HOVER,
            text_color=self.INK,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.SMALL,
        )
        self._context_up_button.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 3),
        )

        self._context_down_button = ctk.CTkButton(
            move_frame,
            text="↓  Descendre",
            height=30,
            corner_radius=6,
            fg_color=self.GROUP_BG,
            hover_color=Colors.BUTTON_HOVER,
            text_color=self.INK,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.SMALL,
        )
        self._context_down_button.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(3, 0),
        )

        self._selection_duplicate_button = ctk.CTkButton(
            context,
            text="⧉  Dupliquer",
            height=32,
            corner_radius=6,
            fg_color=self.GROUP_BG,
            hover_color=self.ACCENT_SOFT,
            text_color=self.INK,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.SMALL,
            command=self._duplicate_selected_pages,
        )
        self._selection_duplicate_button.grid(
            row=5,
            column=0,
            sticky="ew",
            padx=12,
            pady=(2, 5),
        )

        self._selection_delete_button = ctk.CTkButton(
            context,
            text="Supprimer",
            height=32,
            corner_radius=6,
            fg_color=self.GROUP_BG,
            hover_color="#F3E4E1",
            text_color=self.DANGER,
            border_width=1,
            border_color="#E0B9B0",
            font=Fonts.SMALL,
            command=self._delete_selected_pages,
        )
        self._selection_delete_button.grid(
            row=6,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 8),
        )

        self._context_info_box = ctk.CTkFrame(
            context,
            fg_color="#F5F8FA",
            corner_radius=6,
            border_width=1,
            border_color=self.BORDER,
        )
        self._context_info_box.grid(
            row=7,
            column=0,
            sticky="ew",
            padx=12,
            pady=(4, 10),
        )

        self._context_info_label = ctk.CTkLabel(
            self._context_info_box,
            text="",
            font=Fonts.SMALL,
            text_color=self.TEXT_MUTED,
            anchor="w",
            justify="left",
            wraplength=300,
        )
        self._context_info_label.pack(
            fill="x",
            padx=9,
            pady=8,
        )

        self._selection_bar = context
        return panel

    def _install_plan_background(self) -> None:
        """Pose le décor léger dans l'espace libre du Plan du livre."""
        self._plan_background_label = None
        self._plan_background_source = None
        self._plan_background_photo = None

        if self._sequence_frame is None:
            return

        background_path = (
            Path(__file__).resolve().parents[3]
            / "assets"
            / "interface"
            / "backgrounds"
            / "editorial_bg_soft.png"
        )
        if not background_path.is_file():
            return

        try:
            from PIL import Image

            self._plan_background_source = Image.open(
                background_path
            ).convert("RGB")

            label = tk.Label(
                self._sequence_frame,
                image="",
                text="",
                borderwidth=0,
                highlightthickness=0,
                background=self.RIBBON_BG,
                takefocus=False,
            )
            self._plan_background_label = label

            self._sequence_frame.bind(
                "<Configure>",
                self._refresh_plan_background,
                add="+",
            )
            self._sequence_frame.after_idle(
                self._refresh_plan_background
            )
        except Exception:
            self._plan_background_label = None
            self._plan_background_source = None
            self._plan_background_photo = None

    def _refresh_plan_background(self, _event=None) -> None:
        """Affiche le décor sur toute la surface libre derrière les cartes."""
        frame = self._sequence_frame
        label = getattr(self, "_plan_background_label", None)
        source = getattr(self, "_plan_background_source", None)
        if frame is None or label is None or source is None:
            return

        try:
            from PIL import Image, ImageTk

            width = max(1, int(frame.winfo_width()))
            height = max(1, int(frame.winfo_height()))
            if width <= 2 or height <= 2:
                return

            source_ratio = source.width / source.height
            target_ratio = width / height
            if target_ratio > source_ratio:
                resize_width = width
                resize_height = max(height, int(round(width / source_ratio)))
            else:
                resize_height = height
                resize_width = max(width, int(round(height * source_ratio)))

            resized = source.resize(
                (resize_width, resize_height),
                Image.Resampling.LANCZOS,
            )
            left = max(0, (resize_width - width) // 2)
            top = max(0, (resize_height - height) // 2)
            cropped = resized.crop((left, top, left + width, top + height))

            photo = ImageTk.PhotoImage(cropped)
            self._plan_background_photo = photo
            label.configure(image=photo)
            label.place(x=0, y=0, width=width, height=height)

            label.lift()
            for record in self._sequence_row_widgets.values():
                row = record.get("row")
                if row is not None:
                    try:
                        row.lift()
                    except Exception:
                        pass

            if self._sequence_empty_label is not None:
                try:
                    self._sequence_empty_label.lift()
                except Exception:
                    pass
        except Exception:
            try:
                label.place_forget()
            except Exception:
                pass

    def _refresh_sequence(self) -> None:
        """Synchronise les lignes sans effacer puis reconstruire la page."""
        self._hide_page_drop_indicator()
        if self._sequence_frame is None:
            return

        items = self._items()
        active_ids = {str(item.get("id", "")) for item in items}
        self._sanitize_page_selection(active_ids)

        # Retire uniquement les lignes réellement supprimées.
        for item_id in list(self._sequence_row_widgets):
            if item_id in active_ids:
                continue
            record = self._sequence_row_widgets.pop(item_id)
            self._sequence_row_signatures.pop(item_id, None)
            self._rendered_selected_page_ids.discard(item_id)
            try:
                record["row"].destroy()
            except Exception:
                pass

        if not items:
            if self._sequence_empty_label is None:
                self._sequence_empty_label = ctk.CTkLabel(
                    self._sequence_frame,
                    text="Clique sur une page pour commencer.",
                    font=Fonts.NORMAL,
                    text_color=self.TEXT_LIGHT,
                )
            self._sequence_empty_label.grid(
                row=0,
                column=0,
                sticky="nsew",
                padx=20,
                pady=28,
            )
        else:
            if self._sequence_empty_label is not None:
                self._sequence_empty_label.grid_remove()

            total = len(items)
            for index, item in enumerate(items):
                item_id = str(item.get("id", ""))
                if item_id not in self._sequence_row_widgets:
                    row = self._create_sequence_row(
                        self._sequence_frame,
                        item,
                        index,
                        total,
                    )
                    row.grid(
                        row=index,
                        column=0,
                        sticky="w",
                        padx=4,
                        pady=3,
                    )
                    self._sequence_row_widgets[item_id]["grid_index"] = index
                else:
                    signature = self._sequence_row_signature(
                        item,
                        index,
                        total,
                    )
                    if (
                        self._sequence_row_signatures.get(item_id)
                        != signature
                    ):
                        self._update_sequence_row(item, index, total)

                    record = self._sequence_row_widgets[item_id]
                    if record.get("grid_index") != index:
                        record["row"].grid_configure(
                            row=index,
                            column=0,
                            sticky="w",
                            padx=4,
                            pady=3,
                        )
                        record["grid_index"] = index

        self._rendered_selected_page_ids = set(
            self._selected_page_ids
        )
        self._update_summary()
        self._update_page_type_button_states()
        self._update_selection_controls()
        self._refresh_plan_background()

    def _thumbnail_filename_for_type(self, page_type: str) -> str:
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
        return mapping.get(page_type, "type_page_personnalisee.png")

    def _application_thumbnail_dir(self) -> Path:
        return Path(__file__).resolve().parents[3] / "assets" / "page_thumbnails"

    def _project_root_path(self) -> Path:
        root = getattr(self.project, "root", None)
        if root:
            return Path(root)
        return Path.cwd()

    def _thumbnail_path_for_definition(
        self,
        definition: dict[str, Any],
    ) -> Path | None:
        if bool(definition.get("custom", False)):
            stored = str(definition.get("thumbnail", "")).strip()
            if stored:
                path = Path(stored)
                if not path.is_absolute():
                    path = self._project_root_path() / path
                if path.is_file():
                    return path

        page_type = str(definition.get("type", ""))
        filename = self._thumbnail_filename_for_type(page_type)
        path = self._application_thumbnail_dir() / filename
        if path.is_file():
            return path

        generic = (
            self._application_thumbnail_dir()
            / "type_page_personnalisee.png"
        )
        return generic if generic.is_file() else None

    def _thumbnail_photo_for_definition(
        self,
        definition: dict[str, Any],
        subsample: int = 7,
    ):
        path = self._thumbnail_path_for_definition(definition)
        if path is None:
            return None

        key = (str(path.resolve()), int(subsample))
        cached = self._thumbnail_image_cache.get(key)
        if cached is not None:
            return cached

        try:
            source = tk.PhotoImage(file=str(path))
            photo = source.subsample(max(1, int(subsample)))
        except Exception:
            return None

        self._thumbnail_image_cache[key] = photo
        return photo

    def _validate_thumbnail_file(
        self,
        source_path: str,
    ) -> tuple[bool, str]:
        path = Path(source_path)
        if path.suffix.casefold() != ".png":
            return False, "La miniature doit être un fichier PNG."
        if not path.is_file():
            return False, "Le fichier de miniature est introuvable."

        try:
            image = tk.PhotoImage(file=str(path))
            width = int(image.width())
            height = int(image.height())
        except Exception:
            return False, "Impossible de lire cette image PNG."

        if (width, height) != (300, 424):
            return (
                False,
                f"Format incorrect : {width} × {height} px. "
                "Format obligatoire : 300 × 424 px.",
            )
        return True, ""

    def _choose_thumbnail_for_dialog(
        self,
        owner,
        path_var,
        status_label,
    ) -> None:
        selected = filedialog.askopenfilename(
            parent=owner,
            title="Choisir une miniature de page",
            filetypes=[("Image PNG", "*.png")],
        )
        if not selected:
            return

        valid, message = self._validate_thumbnail_file(selected)
        if not valid:
            path_var.set("")
            status_label.configure(
                text=message,
                text_color=self.DANGER,
            )
            return

        path_var.set(selected)
        status_label.configure(
            text=f"{Path(selected).name} · PNG 300 × 424 px",
            text_color=self.DONE,
        )

    def _reset_thumbnail_dialog_choice(
        self,
        path_var,
        status_label,
    ) -> None:
        path_var.set("")
        status_label.configure(
            text="Image générique PageMaître · PNG 300 × 424 px",
            text_color=self.TEXT_MUTED,
        )

    def _import_custom_thumbnail(
        self,
        source_path: str,
        page_type: str,
    ) -> tuple[str, str]:
        valid, message = self._validate_thumbnail_file(source_path)
        if not valid:
            return "", message

        project_root = self._project_root_path()
        destination_dir = (
            project_root / "ressources" / "images" / "types_pages"
        )
        destination_dir.mkdir(parents=True, exist_ok=True)
        destination = destination_dir / f"type_page_{page_type}.png"

        try:
            source = Path(source_path).resolve()
            target = destination.resolve()
            if source != target:
                shutil.copy2(source, target)
        except OSError as exc:
            return "", f"Impossible d’importer la miniature : {exc}"

        try:
            relative = destination.relative_to(project_root).as_posix()
        except ValueError:
            relative = str(destination)

        self._thumbnail_image_cache.clear()
        return relative, ""

    def _replace_custom_thumbnail(self, page_type: str, owner) -> None:
        definition = next(
            (
                item
                for item in self._page_types()
                if str(item.get("type", "")) == page_type
                and bool(item.get("custom", False))
            ),
            None,
        )
        if definition is None:
            return

        selected = filedialog.askopenfilename(
            parent=owner,
            title="Remplacer la miniature",
            filetypes=[("Image PNG", "*.png")],
        )
        if not selected:
            return

        imported, error = self._import_custom_thumbnail(
            selected,
            page_type,
        )
        if error:
            messagebox.showerror(
                "Miniature non valide",
                error,
                parent=owner,
            )
            return

        self._record_history()
        definition["thumbnail"] = imported
        self._save_data()
        self._thumbnail_image_cache.clear()
        self._sequence_row_signatures.clear()
        self._refresh_sequence()
        self._close_manage_dialog()
        self._open_manage_dialog()

    def _reset_custom_thumbnail(self, page_type: str, owner) -> None:
        definition = next(
            (
                item
                for item in self._page_types()
                if str(item.get("type", "")) == page_type
                and bool(item.get("custom", False))
            ),
            None,
        )
        if definition is None:
            return
        if not str(definition.get("thumbnail", "")).strip():
            return

        self._record_history()
        definition["thumbnail"] = ""
        self._save_data()
        self._thumbnail_image_cache.clear()
        self._sequence_row_signatures.clear()
        self._refresh_sequence()
        self._close_manage_dialog()
        self._open_manage_dialog()

    def _create_sequence_row(
        self,
        parent,
        item: dict[str, Any],
        index: int,
        total_items: int,
    ) -> tk.Frame:
        """Carte visuelle utilisant la bibliothèque de miniatures réalistes."""
        item_id = str(item.get("id", ""))
        definition = self._definition_for(item.get("type", "inconnu"))
        automatic_blank = bool(item.get("automatic_recto_verso", False))
        plan_group = self._plan_group_id(item)
        group = self._group_for(plan_group)
        group_accent = str(group.get("accent", self.INK))
        type_accent = str(definition.get("accent", self.INK))
        page_color = self._plan_group_page_color(
            plan_group,
            str(definition.get("color", self.GROUP_BG)),
        )

        row_height = 92
        card_height = 80
        card_width = 820 if not automatic_blank else 700
        card_padx = (8, 6) if not automatic_blank else (54, 6)
        row_width = card_width + (66 if automatic_blank else 18)

        row = tk.Frame(
            parent,
            width=row_width,
            height=row_height,
            background="#FBFAF6",
            borderwidth=0,
            highlightthickness=0,
        )
        row.grid_columnconfigure(0, weight=0)
        row.grid_propagate(False)

        card = tk.Frame(
            row,
            width=card_width,
            height=card_height,
            background=self.CARD_BG,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.BORDER,
            highlightcolor=self.BORDER,
        )
        card.grid(row=0, column=0, sticky="w", padx=card_padx, pady=5)
        card.grid_propagate(False)
        card.grid_columnconfigure(3, weight=1)

        group_strip = tk.Frame(
            card,
            width=6,
            height=card_height - 10,
            background=group_accent,
            borderwidth=0,
        )
        group_strip.grid(row=0, column=0, padx=(5, 5), pady=5, sticky="ns")

        thumbnail = tk.Frame(
            card,
            width=48,
            height=66,
            background=page_color,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=group_accent,
            highlightcolor=group_accent,
        )
        thumbnail.grid(row=0, column=1, padx=(0, 10), pady=6)
        thumbnail.grid_propagate(False)

        thumbnail_image_label = tk.Label(
            thumbnail,
            image="",
            text="",
            background=page_color,
            borderwidth=0,
            highlightthickness=0,
        )
        thumbnail_image_label.place(relx=0.5, rely=0.5, anchor="center")

        symbol_label = tk.Label(
            thumbnail,
            text=str(definition.get("symbol", "?")),
            font=(Fonts.FAMILY, 12, "bold"),
            foreground=type_accent,
            background=page_color,
            borderwidth=0,
        )
        symbol_label.place(relx=0.5, rely=0.5, anchor="center")

        count_badge = tk.Label(
            thumbnail,
            text="",
            font=(Fonts.FAMILY, 8, "bold"),
            foreground=self.INK,
            background="#F7F9FB",
            borderwidth=1,
            relief="solid",
            padx=2,
            pady=0,
        )
        count_badge.place(relx=0.98, rely=0.98, anchor="se")

        info = tk.Frame(
            card,
            width=610 if not automatic_blank else 560,
            height=card_height - 10,
            background=self.CARD_BG,
            borderwidth=0,
        )
        info.grid(row=0, column=2, sticky="w", pady=5)
        info.grid_propagate(False)
        info.grid_columnconfigure(0, weight=1)

        title_label = tk.Label(
            info,
            text="",
            font=Fonts.NORMAL,
            foreground=self.INK,
            background=self.CARD_BG,
            anchor="w",
            borderwidth=0,
        )
        title_label.grid(row=0, column=0, sticky="w", pady=(8, 0))

        detail_label = tk.Label(
            info,
            text="",
            font=Fonts.SMALL,
            foreground=self.TEXT_MUTED,
            background=self.CARD_BG,
            anchor="w",
            borderwidth=0,
        )
        detail_label.grid(row=1, column=0, sticky="w", pady=(3, 4))

        auto_badge = tk.Label(
            card,
            text="AUTO",
            font=(Fonts.FAMILY, 9, "bold"),
            foreground=self.INK,
            background="#E7EEF6",
            padx=8,
            pady=4,
            borderwidth=0,
        )
        auto_badge.grid(row=0, column=3, sticky="e", padx=(8, 10))
        if not automatic_blank:
            auto_badge.grid_remove()

        self._sequence_row_widgets[item_id] = {
            "row": row,
            "card": card,
            "group_strip": group_strip,
            "thumbnail": thumbnail,
            "thumbnail_image_label": thumbnail_image_label,
            "symbol_label": symbol_label,
            "count_badge": count_badge,
            "info": info,
            "title_label": title_label,
            "detail_label": detail_label,
            "auto_badge": auto_badge,
            "grid_index": index,
            "display_state": {},
            "selection_state": None,
            "photo_ref": None,
        }

        self._bind_sequence_page_drag(
            item_id,
            row,
            card,
            group_strip,
            thumbnail,
            thumbnail_image_label,
            symbol_label,
            count_badge,
            info,
            title_label,
            detail_label,
        )
        self._update_sequence_row(item, index, total_items)
        return row

    def _sequence_progress_counts(
        self,
        item: dict[str, Any],
    ) -> tuple[int, int]:
        """Retourne (fait, reste) et accepte déjà un futur compteur Conception."""
        total = max(1, int(item.get("count", 1)))
        completed: int | None = None
        for key in ("done_count", "validated_count", "completed_count"):
            if key not in item:
                continue
            try:
                completed = int(item.get(key, 0))
            except (TypeError, ValueError):
                completed = 0
            break

        if completed is None:
            completed = total if bool(item.get("done", False)) else 0

        completed = max(0, min(total, completed))
        return completed, total - completed

    def _sequence_item_by_id(self, item_id: str) -> dict[str, Any] | None:
        for candidate in self._items():
            if str(candidate.get("id", "")) == item_id:
                return candidate
        return None

    def _associated_automatic_blank_count(self, item_id: str) -> int:
        total = 0
        for candidate in self._items():
            if not bool(candidate.get("automatic_recto_verso", False)):
                continue
            if str(candidate.get("recto_target_id", "")) != item_id:
                continue
            total += max(1, int(candidate.get("count", 1)))
        return total

    def _sequence_button(
        self,
        parent,
        text: str,
        command,
        *,
        foreground: str | None = None,
        active_background: str | None = None,
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            width=2,
            height=1,
            padx=0,
            pady=0,
            relief="flat",
            borderwidth=1,
            highlightthickness=0,
            background=self.GROUP_BG,
            activebackground=active_background or Colors.BUTTON_HOVER,
            foreground=foreground or self.INK,
            activeforeground=foreground or self.INK,
            disabledforeground=self.TEXT_LIGHT,
            font=Fonts.SMALL,
            cursor="hand2",
            takefocus=False,
            command=command,
        )

    def _bind_sequence_page_drag(
        self,
        item_id: str,
        *widgets,
    ) -> None:
        """Rend la partie descriptive d'une ligne déplaçable verticalement."""
        for widget in widgets:
            widget.bind(
                "<ButtonPress-1>",
                lambda event, current=item_id: self._start_page_drag(
                    event,
                    current,
                ),
            )
            widget.bind("<B1-Motion>", self._continue_page_drag)
            widget.bind("<ButtonRelease-1>", self._finish_page_drag)

    def _start_page_drag(self, event, item_id: str) -> None:
        index = self._item_index(item_id)
        if index is None:
            return

        current_item = self._items()[index]
        if bool(current_item.get("automatic_recto_verso", False)):
            return

        self._drag_page_press_state = int(getattr(event, "state", 0) or 0)
        self._update_page_selection_from_event(item_id, event)

        page_type = str(current_item.get("type", ""))
        if self._is_locked_structural_type(page_type):
            self._dragged_page_id = None
            self._dragged_page_ids = ()
            return

        movable_ids = self._selected_movable_page_ids()
        if item_id not in movable_ids:
            movable_ids = (item_id,)

        self._dragged_page_id = item_id
        self._dragged_page_ids = movable_ids
        self._drag_page_start_y = int(getattr(event, "y_root", 0))
        self._drag_page_has_moved = False
        self._refresh_selection_visuals()

    def _continue_page_drag(self, event) -> None:
        item_id = self._dragged_page_id
        if item_id is None:
            return

        current_y = int(getattr(event, "y_root", self._drag_page_start_y))
        if abs(current_y - self._drag_page_start_y) >= 5:
            self._drag_page_has_moved = True

        if self._drag_page_has_moved:
            self._show_page_drop_indicator(item_id, current_y)

    def _finish_page_drag(self, event) -> None:
        item_id = self._dragged_page_id
        moved = self._drag_page_has_moved
        press_state = self._drag_page_press_state
        self._dragged_page_id = None
        self._drag_page_has_moved = False
        self._drag_page_press_state = 0
        self._hide_page_drop_indicator()

        if item_id is None:
            return

        if moved:
            pointer_y = int(getattr(event, "y_root", self._drag_page_start_y))
            self._place_page_at_pointer(item_id, pointer_y)
        else:
            self._dragged_page_ids = ()
            if not (press_state & 0x0001) and not (press_state & 0x0004):
                if item_id in self._selected_page_ids and len(self._selected_page_ids) > 1:
                    self._selected_page_ids = {item_id}
                    self._selection_anchor_id = item_id
            self._refresh_selection_visuals()
            self._update_selection_controls()

    def _page_drop_plan(
        self,
        item_id: str,
        pointer_y: int,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], int] | None:
        items = self._items()
        dragged_ids = set(self._dragged_page_ids or (item_id,))
        dragged_items = [
            item
            for item in items
            if str(item.get("id", "")) in dragged_ids
            and not bool(item.get("automatic_recto_verso", False))
            and not self._is_locked_structural_type(
                str(item.get("type", ""))
            )
        ]
        if not dragged_items:
            return None

        dragged_ids = {
            str(item.get("id", ""))
            for item in dragged_items
        }
        remaining_regular = [
            item
            for item in items
            if str(item.get("id", "")) not in dragged_ids
            and not bool(item.get("automatic_recto_verso", False))
            and not self._is_locked_structural_type(
                str(item.get("type", ""))
            )
        ]

        insertion_index = len(remaining_regular)
        for position, item in enumerate(remaining_regular):
            other_id = str(item.get("id", ""))
            record = self._sequence_row_widgets.get(other_id)
            if record is None:
                continue
            try:
                row = record["row"]
                row_middle = row.winfo_rooty() + (row.winfo_height() / 2)
            except Exception:
                continue
            if pointer_y < row_middle:
                insertion_index = position
                break

        return dragged_items, remaining_regular, insertion_index

    def _show_page_drop_indicator(
        self,
        item_id: str,
        pointer_y: int,
    ) -> None:
        """Affiche la ligne sur la frontière réelle entre deux blocs de pages."""
        plan = self._page_drop_plan(item_id, pointer_y)
        overlay = self._root
        if plan is None or overlay is None:
            self._hide_page_drop_indicator()
            return

        # INDICATEUR_DEPOT_BLOCS_AUTO_V1
        # Le calcul logique du déplacement reste strictement inchangé.
        # Ici, on corrige uniquement l'endroit où la ligne est dessinée :
        # une page et ses blancs automatiques associés forment un même bloc
        # visuel. La ligne ne peut donc plus traverser un blanc automatique.
        dragged_items, remaining_regular, insertion_index = plan
        items = self._items()

        dragged_ids = {
            str(dragged.get("id", ""))
            for dragged in dragged_items
        }

        previous_item = None
        next_item = None
        if insertion_index > 0:
            previous_item = remaining_regular[insertion_index - 1]
        else:
            start_items = [
                item
                for item in items
                if str(item.get("id", "")) not in dragged_ids
                and str(item.get("type", "")) in self.START_STRUCTURAL_TYPES
            ]
            if start_items:
                previous_item = start_items[-1]

        if insertion_index < len(remaining_regular):
            next_item = remaining_regular[insertion_index]
        else:
            end_items = [
                item
                for item in items
                if str(item.get("id", "")) not in dragged_ids
                and str(item.get("type", "")) in self.END_STRUCTURAL_TYPES
            ]
            if end_items:
                next_item = end_items[0]

        if previous_item is None or next_item is None:
            self._hide_page_drop_indicator()
            return

        def block_rows(page_item: dict[str, Any]) -> list[Any]:
            """Retourne la page et ses blancs automatiques réellement associés."""
            page_id = str(page_item.get("id", ""))
            rows: list[Any] = []

            page_record = self._sequence_row_widgets.get(page_id)
            if page_record is not None and page_record.get("row") is not None:
                rows.append(page_record["row"])

            for candidate in items:
                if not bool(candidate.get("automatic_recto_verso", False)):
                    continue
                if str(candidate.get("recto_target_id", "")) != page_id:
                    continue
                record = self._sequence_row_widgets.get(
                    str(candidate.get("id", ""))
                )
                if record is not None and record.get("row") is not None:
                    rows.append(record["row"])

            return rows

        def block_bounds(
            page_item: dict[str, Any],
        ) -> tuple[Any, Any, int, int] | None:
            rows = block_rows(page_item)
            if not rows:
                return None
            try:
                upper = min(rows, key=lambda row: row.winfo_rooty())
                lower = max(
                    rows,
                    key=lambda row: row.winfo_rooty() + row.winfo_height(),
                )
                top = min(row.winfo_rooty() for row in rows)
                bottom = max(
                    row.winfo_rooty() + row.winfo_height()
                    for row in rows
                )
            except Exception:
                return None
            return upper, lower, int(top), int(bottom)

        previous_bounds = block_bounds(previous_item)
        next_bounds = block_bounds(next_item)
        if previous_bounds is None or next_bounds is None:
            self._hide_page_drop_indicator()
            return

        previous_upper, previous_lower, _, previous_bottom = previous_bounds
        next_upper, next_lower, next_top, _ = next_bounds

        # Si le bloc source se trouve encore entre les deux blocs cibles,
        # son bord supérieur/inférieur devient la frontière affichée.
        source_blocks = []
        for dragged_item in dragged_items:
            bounds = block_bounds(dragged_item)
            if bounds is not None:
                source_blocks.append(bounds)

        source_bounds = None
        if source_blocks:
            try:
                source_bounds = min(
                    source_blocks,
                    key=lambda bounds: abs(
                        ((bounds[2] + bounds[3]) / 2) - pointer_y
                    ),
                )
            except Exception:
                source_bounds = source_blocks[0]

        marker_height_px = 4
        try:
            overlay.update_idletasks()

            upper_row = previous_lower
            lower_row = next_upper

            if source_bounds is not None:
                source_upper, source_lower, source_top, source_bottom = (
                    source_bounds
                )
                if (
                    previous_bottom <= source_top
                    and source_bottom <= next_top
                ):
                    source_middle = (source_top + source_bottom) / 2
                    if pointer_y < source_middle:
                        lower_row = source_upper
                        next_top = source_top
                    else:
                        upper_row = source_lower
                        previous_bottom = source_bottom

            gap_center = (previous_bottom + next_top) / 2
            marker_root_y = gap_center - marker_height_px / 2

            left_px = max(
                upper_row.winfo_rootx(),
                lower_row.winfo_rootx(),
            )
            right_px = min(
                upper_row.winfo_rootx() + upper_row.winfo_width(),
                lower_row.winfo_rootx() + lower_row.winfo_width(),
            )
            marker_width_px = max(80, right_px - left_px)

            local_x, local_y, marker_width, marker_height = (
                self._screen_geometry_for_place(
                    overlay,
                    left_px,
                    marker_root_y,
                    marker_width_px,
                    marker_height_px,
                )
            )
        except Exception:
            self._hide_page_drop_indicator()
            return

        if self._page_drop_indicator is None:
            self._page_drop_indicator = ctk.CTkFrame(
                overlay,
                width=marker_width,
                height=marker_height,
                fg_color=self.CORAL,
                corner_radius=2,
                border_width=1,
                border_color=self.INK,
            )

        try:
            self._page_drop_indicator.configure(
                width=marker_width,
                height=marker_height,
            )
            self._page_drop_indicator.place(x=local_x, y=local_y)
            self._page_drop_indicator.lift()
        except Exception:
            self._hide_page_drop_indicator()

    def _hide_page_drop_indicator(self) -> None:
        indicator = self._page_drop_indicator
        self._page_drop_indicator = None
        if indicator is not None:
            try:
                indicator.destroy()
            except Exception:
                pass

    def _place_page_at_pointer(self, item_id: str, pointer_y: int) -> None:
        """Déplace les pages et leur attribue le groupe visuel rejoint."""
        items = self._items()
        plan = self._page_drop_plan(item_id, pointer_y)
        if plan is None:
            self._dragged_page_ids = ()
            self._refresh_sequence()
            return

        dragged_items, remaining_regular, insertion_index = plan
        old_regular = [
            item
            for item in items
            if not bool(item.get("automatic_recto_verso", False))
            and not self._is_locked_structural_type(
                str(item.get("type", ""))
            )
        ]
        old_regular_order = [
            str(item.get("id", ""))
            for item in old_regular
        ]
        dragged_ids = {
            str(item.get("id", ""))
            for item in dragged_items
        }
        old_positions = [
            index
            for index, existing_id in enumerate(old_regular_order)
            if existing_id in dragged_ids
        ]
        moving_down = bool(old_positions) and insertion_index > min(old_positions)

        old_groups = {
            str(item.get("id", "")): self._plan_group_id(item)
            for item in dragged_items
        }
        destination_group = self._plan_destination_group(
            dragged_items,
            remaining_regular,
            insertion_index,
            moving_down,
        )

        remaining_regular[insertion_index:insertion_index] = dragged_items
        new_regular_order = [
            str(item.get("id", ""))
            for item in remaining_regular
        ]
        group_changed = any(
            old_groups.get(str(item.get("id", "")), "") != destination_group
            for item in dragged_items
        )
        self._dragged_page_ids = ()

        if new_regular_order == old_regular_order and not group_changed:
            self._refresh_sequence()
            return

        structural_items = [
            item
            for item in items
            if self._is_locked_structural_type(
                str(item.get("type", ""))
            )
        ]

        # L'historique est pris AVANT le changement de groupe.
        self._record_history()
        for dragged in dragged_items:
            dragged["plan_group"] = destination_group

        items[:] = remaining_regular + structural_items
        self._enforce_structural_order()
        self._save_data()
        self._refresh_sequence()

    def _update_sequence_row(
        self,
        item: dict[str, Any],
        index: int,
        total_items: int,
    ) -> None:
        item_id = str(item.get("id", ""))
        record = self._sequence_row_widgets.get(item_id)
        if record is None:
            return

        definition = self._definition_for(item.get("type", "inconnu"))
        count = max(1, int(item.get("count", 1)))
        completed, remaining = self._sequence_progress_counts(item)
        done = remaining == 0
        automatic_blank = bool(item.get("automatic_recto_verso", False))
        type_accent = str(definition.get("accent", self.INK))
        symbol = str(definition.get("symbol", "?"))
        plan_group = self._plan_group_id(item)
        group = self._group_for(plan_group)
        group_accent = str(group.get("accent", type_accent))
        thumbnail_color = self._plan_group_page_color(
            plan_group,
            str(definition.get("color", self.GROUP_BG)),
        )

        title_text = str(item.get("title") or definition.get("title", "Page"))
        auto_count = self._associated_automatic_blank_count(item_id)

        if automatic_blank:
            position_text = (
                "avant" if item.get("recto_position") == "before" else "après"
            )
            title_text = (
                "Pages blanches automatiques"
                if count > 1
                else "Page blanche automatique"
            )
            target = self._sequence_item_by_id(
                str(item.get("recto_target_id", ""))
            )
            target_title = ""
            target_remaining = count
            if target is not None:
                target_definition = self._definition_for(
                    str(target.get("type", "inconnu"))
                )
                target_title = str(
                    target.get("title")
                    or target_definition.get("title", "Page")
                )
                _, target_remaining = self._sequence_progress_counts(target)

            detail_text = f"Auto ×{count} · {position_text}"
            if target_title:
                detail_text += f" · liée à {target_title} · reste {target_remaining}"
            elif count > 1:
                detail_text += f" · reste {count}"
            if bool(item.get("recto_shared", False)):
                detail_text += " · partagé"
            title_color = self.TEXT_MUTED
        else:
            if count > 1:
                detail_text = f"Fait {completed}/{count} · Reste {remaining}"
            else:
                detail_text = "Fait" if done else "À faire"
            if auto_count:
                detail_text += (
                    f" · Auto associée ×{auto_count}"
                    if auto_count == 1
                    else f" · Auto associées ×{auto_count}"
                )
            title_color = self.DONE if done else self.INK

        thumbnail_path = self._thumbnail_path_for_definition(definition)
        thumbnail_key = str(thumbnail_path) if thumbnail_path is not None else ""

        previous = record.get("display_state", {})
        definition_state = (
            thumbnail_color,
            group_accent,
            type_accent,
            symbol,
            plan_group,
            thumbnail_key,
        )
        if previous.get("definition") != definition_state:
            record["thumbnail"].configure(
                background=thumbnail_color,
                highlightbackground=group_accent,
                highlightcolor=group_accent,
            )
            record["thumbnail_image_label"].configure(background=thumbnail_color)
            record["symbol_label"].configure(
                text=symbol,
                foreground=type_accent,
                background=thumbnail_color,
            )
            record["group_strip"].configure(background=group_accent)

            photo = self._thumbnail_photo_for_definition(definition, subsample=7)
            record["photo_ref"] = photo
            if photo is not None:
                record["thumbnail_image_label"].configure(image=photo)
                record["symbol_label"].place_forget()
            else:
                record["thumbnail_image_label"].configure(image="")
                record["symbol_label"].place(
                    relx=0.5,
                    rely=0.5,
                    anchor="center",
                )

        if previous.get("count") != count:
            if count > 1:
                record["count_badge"].configure(text=f"×{count}")
                record["count_badge"].place(
                    relx=0.98,
                    rely=0.98,
                    anchor="se",
                )
            else:
                record["count_badge"].place_forget()

        title_state = (title_text, title_color, detail_text)
        if previous.get("title") != title_state:
            record["title_label"].configure(
                text=title_text,
                foreground=title_color,
            )
            record["detail_label"].configure(
                text=detail_text,
                foreground=(
                    self.DONE
                    if done and not automatic_blank
                    else self.TEXT_MUTED
                ),
            )

        record["display_state"] = {
            "definition": definition_state,
            "count": count,
            "title": title_state,
            "automatic": automatic_blank,
            "completed": completed,
            "remaining": remaining,
            "auto_count": auto_count,
        }
        self._update_sequence_row_selection(item)
        self._sequence_row_signatures[item_id] = self._sequence_row_signature(
            item,
            index,
            total_items,
        )

    def _sequence_row_signature(
        self,
        item: dict[str, Any],
        index: int,
        total_items: int,
    ) -> tuple[Any, ...]:
        """État utile d'une carte, miniature et groupe visuel compris."""
        definition = self._definition_for(item.get("type", "inconnu"))
        item_id = str(item.get("id", ""))
        completed, remaining = self._sequence_progress_counts(item)
        plan_group = self._plan_group_id(item)

        target_progress: tuple[int, int] | None = None
        if bool(item.get("automatic_recto_verso", False)):
            target = self._sequence_item_by_id(
                str(item.get("recto_target_id", ""))
            )
            if target is not None:
                target_progress = self._sequence_progress_counts(target)

        return (
            str(item.get("type", "")),
            str(item.get("title", "")),
            max(1, int(item.get("count", 1))),
            completed,
            remaining,
            bool(item.get("done", False)),
            str(item.get("done_source", "")),
            plan_group,
            bool(item.get("automatic_recto_verso", False)),
            str(item.get("recto_position", "")),
            str(item.get("recto_target_id", "")),
            bool(item.get("recto_shared", False)),
            target_progress,
            self._associated_automatic_blank_count(item_id),
            str(definition.get("title", "")),
            str(definition.get("symbol", "")),
            str(definition.get("color", "")),
            str(definition.get("accent", "")),
            str(definition.get("thumbnail", "")),
            bool(definition.get("single", False)),
            bool(definition.get("required", False)),
            self._can_move_item(index, -1),
            self._can_move_item(index, 1),
        )

    def _update_sequence_row_selection(
        self,
        item: dict[str, Any],
    ) -> None:
        """Met à jour uniquement la carte visible, pas toute la ligne."""
        item_id = str(item.get("id", ""))
        record = self._sequence_row_widgets.get(item_id)
        if record is None:
            return

        selected = item_id in self._selected_page_ids
        _, remaining = self._sequence_progress_counts(item)
        done = remaining == 0
        state = (selected, done)
        if record.get("selection_state") == state:
            return

        background = "#EEF4FA" if selected else self.CARD_BG
        border = self.ACCENT if selected else self.DONE if done else self.BORDER

        record["card"].configure(
            background=background,
            highlightbackground=border,
            highlightcolor=border,
            highlightthickness=2 if selected else 1,
        )
        record["info"].configure(background=background)
        record["title_label"].configure(background=background)
        record["detail_label"].configure(background=background)
        record["selection_state"] = state

    def _selectable_page_ids(self) -> tuple[str, ...]:
        return tuple(
            str(item.get("id", ""))
            for item in self._items()
            if str(item.get("id", ""))
            and not bool(item.get("automatic_recto_verso", False))
        )

    def _sanitize_page_selection(self, active_ids: set[str] | None = None) -> None:
        valid_ids = active_ids if active_ids is not None else {
            str(item.get("id", "")) for item in self._items()
        }
        self._selected_page_ids.intersection_update(valid_ids)
        if self._selection_anchor_id not in valid_ids:
            self._selection_anchor_id = None

    def _update_page_selection_from_event(self, item_id: str, event) -> None:
        selectable_ids = self._selectable_page_ids()
        if item_id not in selectable_ids:
            return

        state = int(getattr(event, "state", 0) or 0)
        shift_pressed = bool(state & 0x0001)
        control_pressed = bool(state & 0x0004)

        if shift_pressed and self._selection_anchor_id in selectable_ids:
            anchor_index = selectable_ids.index(self._selection_anchor_id)
            current_index = selectable_ids.index(item_id)
            start = min(anchor_index, current_index)
            end = max(anchor_index, current_index) + 1
            range_ids = set(selectable_ids[start:end])
            if control_pressed:
                self._selected_page_ids.update(range_ids)
            else:
                self._selected_page_ids = range_ids
        elif control_pressed:
            if item_id in self._selected_page_ids:
                self._selected_page_ids.remove(item_id)
                if self._selection_anchor_id == item_id:
                    self._selection_anchor_id = None
            else:
                self._selected_page_ids.add(item_id)
                self._selection_anchor_id = item_id
        elif item_id not in self._selected_page_ids:
            self._selected_page_ids = {item_id}
            self._selection_anchor_id = item_id
        elif len(self._selected_page_ids) == 1:
            self._selection_anchor_id = item_id

        self._refresh_selection_visuals()
        self._update_selection_controls()

    def _refresh_selection_visuals(self) -> None:
        current_ids = set(self._selected_page_ids)
        changed_ids = (
            current_ids
            ^ self._rendered_selected_page_ids
        )
        if not changed_ids:
            return

        items_by_id = {
            str(item.get("id", "")): item
            for item in self._items()
        }
        for item_id in changed_ids:
            item = items_by_id.get(item_id)
            if item is not None:
                self._update_sequence_row_selection(item)

        self._rendered_selected_page_ids = current_ids

    def _selected_items(self) -> list[dict[str, Any]]:
        return [
            item
            for item in self._items()
            if str(item.get("id", "")) in self._selected_page_ids
        ]

    def _selected_movable_page_ids(self) -> tuple[str, ...]:
        return tuple(
            str(item.get("id", ""))
            for item in self._selected_items()
            if not bool(item.get("automatic_recto_verso", False))
            and not self._is_locked_structural_type(
                str(item.get("type", ""))
            )
        )

    def _selected_duplicable_items(self) -> list[dict[str, Any]]:
        duplicable: list[dict[str, Any]] = []
        for item in self._selected_items():
            definition = self._definition_for(str(item.get("type", "")))
            if bool(item.get("automatic_recto_verso", False)):
                continue
            if bool(definition.get("single", False)):
                continue
            if self._is_locked_structural_type(str(item.get("type", ""))):
                continue
            duplicable.append(item)
        return duplicable

    def _selected_deletable_ids(self) -> set[str]:
        deletable: set[str] = set()
        for item in self._selected_items():
            definition = self._definition_for(str(item.get("type", "")))
            if bool(item.get("automatic_recto_verso", False)):
                continue
            if bool(definition.get("required", False)):
                continue
            deletable.add(str(item.get("id", "")))
        return deletable

    def _update_selection_controls(self) -> None:
        context = self._selection_bar
        if context is None:
            return

        selected_items = self._selected_items()
        count = len(selected_items)
        duplicable_count = len(self._selected_duplicable_items()) if count else 0
        deletable_count = len(self._selected_deletable_ids()) if count else 0

        single_item = selected_items[0] if count == 1 else None
        single_id = str(single_item.get("id", "")) if single_item else ""
        single_count = max(1, int(single_item.get("count", 1))) if single_item else 0
        single_done = self._sequence_progress_counts(single_item) if single_item else (0, 0)
        single_auto = self._associated_automatic_blank_count(single_id) if single_id else 0
        single_index = self._item_index(single_id) if single_id else None

        can_up = (
            self._can_move_item(single_index, -1)
            if single_index is not None
            else False
        )
        can_down = (
            self._can_move_item(single_index, 1)
            if single_index is not None
            else False
        )
        current_group = self._plan_group_id(single_item) if single_item else ""

        state = (
            tuple(sorted(self._selected_page_ids)),
            duplicable_count,
            deletable_count,
            single_count,
            single_done,
            single_auto,
            can_up,
            can_down,
            current_group,
        )
        if self._selection_controls_cache == state:
            return
        self._selection_controls_cache = state

        if count == 0:
            self._selection_label.configure(text="Aucune page sélectionnée")
            self._context_title_label.configure(text="Sélectionnez une page")
            self._context_detail_label.configure(
                text=(
                    "Cliquez sur une carte pour afficher ici ses commandes. "
                    "Le déplacement direct se fait par glisser-déposer."
                )
            )
            self._context_info_label.configure(
                text=(
                    "Astuce\n"
                    "Ctrl : ajouter à la sélection\n"
                    "Maj : sélectionner une plage\n"
                    "Ctrl+A : sélectionner les pages déplaçables"
                )
            )
            self._context_clear_button.configure(state="disabled")
            self._context_quantity_frame.grid_remove()
            self._context_up_button.configure(state="disabled")
            self._context_down_button.configure(state="disabled")
            self._selection_duplicate_button.configure(state="disabled")
            self._selection_delete_button.configure(state="disabled")
            return

        self._context_clear_button.configure(state="normal")

        if count > 1:
            self._selection_label.configure(text=f"{count} pages sélectionnées")
            self._context_title_label.configure(
                text=f"Sélection multiple · {count} pages"
            )
            self._context_detail_label.configure(
                text=(
                    "Glissez une des cartes sélectionnées pour déplacer "
                    "l'ensemble en une seule opération."
                )
            )
            self._context_info_label.configure(
                text=(
                    f"Pages duplicables : {duplicable_count}\n"
                    f"Pages supprimables : {deletable_count}"
                )
            )
            self._context_quantity_frame.grid_remove()
            self._context_up_button.configure(state="disabled")
            self._context_down_button.configure(state="disabled")
            self._selection_duplicate_button.configure(
                text=(
                    f"⧉  Dupliquer les {duplicable_count}"
                    if duplicable_count
                    else "⧉  Dupliquer"
                ),
                state="normal" if duplicable_count else "disabled",
            )
            self._selection_delete_button.configure(
                text=(
                    f"Supprimer les {deletable_count}"
                    if deletable_count
                    else "Supprimer"
                ),
                state="normal" if deletable_count else "disabled",
            )
            return

        item = single_item
        definition = self._definition_for(str(item.get("type", "inconnu")))
        title = str(item.get("title") or definition.get("title", "Page"))
        completed, remaining = self._sequence_progress_counts(item)
        item_count = max(1, int(item.get("count", 1)))
        automatic_blank = bool(item.get("automatic_recto_verso", False))
        single_page = bool(definition.get("single", False))

        self._selection_label.configure(text="Page sélectionnée")
        self._context_title_label.configure(text=title)
        self._context_detail_label.configure(
            text=(
                f"Fait {completed}/{item_count} · Reste {remaining}"
                if item_count > 1
                else ("Fait" if remaining == 0 else "À faire")
            )
        )

        info_parts = []
        group = self._group_for(current_group)
        group_title = str(group.get("title", ""))
        if group_title:
            info_parts.append(f"Groupe actuel : {group_title}")
        if single_auto:
            info_parts.append(
                f"Pages blanches automatiques associées : {single_auto}"
            )
        if len(info_parts) == 1:
            info_parts.append("Aucune page automatique associée.")
        self._context_info_label.configure(text="\n".join(info_parts))

        if not automatic_blank and not single_page:
            self._context_quantity_frame.grid()
            self._context_count_label.configure(text=str(item_count))
            self._context_minus_button.configure(
                state="normal" if item_count > 1 else "disabled",
                command=lambda current=single_id: self._change_count_by_id(current, -1),
            )
            self._context_plus_button.configure(
                state="normal",
                command=lambda current=single_id: self._change_count_by_id(current, 1),
            )
        else:
            self._context_quantity_frame.grid_remove()

        self._context_up_button.configure(
            state="normal" if can_up else "disabled",
            command=lambda current=single_id: self._move_item_by_id(current, -1),
        )
        self._context_down_button.configure(
            state="normal" if can_down else "disabled",
            command=lambda current=single_id: self._move_item_by_id(current, 1),
        )

        self._selection_duplicate_button.configure(
            text="⧉  Dupliquer",
            state="normal" if duplicable_count else "disabled",
        )
        self._selection_delete_button.configure(
            text="Supprimer",
            state="normal" if deletable_count else "disabled",
        )

    def _clear_page_selection(self) -> None:
        if not self._selected_page_ids:
            return
        self._selected_page_ids.clear()
        self._selection_anchor_id = None
        self._refresh_selection_visuals()
        self._update_selection_controls()

    def _select_all_movable_pages(self) -> None:
        """Sélectionne toutes les pages réellement déplaçables."""
        movable_ids = tuple(
            str(item.get("id", ""))
            for item in self._items()
            if str(item.get("id", ""))
            and not bool(item.get("automatic_recto_verso", False))
            and not self._is_locked_structural_type(
                str(item.get("type", ""))
            )
        )

        new_selection = set(movable_ids)
        if new_selection == self._selected_page_ids:
            return

        self._selected_page_ids = new_selection
        self._selection_anchor_id = movable_ids[0] if movable_ids else None
        self._refresh_selection_visuals()
        self._update_selection_controls()

    def _duplicate_selected_pages(self) -> None:
        duplicable_ids = {
            str(item.get("id", ""))
            for item in self._selected_duplicable_items()
        }
        if not duplicable_ids:
            return

        self._record_history()
        rebuilt: list[dict[str, Any]] = []
        duplicate_ids: list[str] = []
        for item in self._items():
            rebuilt.append(item)
            if str(item.get("id", "")) not in duplicable_ids:
                continue

            duplicate = deepcopy(item)
            duplicate_id = f"MAQUETTE-{uuid4().hex[:12].upper()}"
            duplicate["id"] = duplicate_id
            duplicate["done"] = False
            duplicate.pop("automatic_recto_verso", None)
            duplicate.pop("recto_target_id", None)
            duplicate.pop("recto_position", None)
            rebuilt.append(duplicate)
            duplicate_ids.append(duplicate_id)

        self._items()[:] = rebuilt
        self._selected_page_ids = set(duplicate_ids)
        self._selection_anchor_id = duplicate_ids[0] if duplicate_ids else None
        self._enforce_structural_order()
        self._save_data()
        self._refresh_sequence()

    def _delete_selected_pages(self) -> None:
        deletable_ids = self._selected_deletable_ids()
        if not deletable_ids:
            return

        self._record_history()
        self._items()[:] = [
            item
            for item in self._items()
            if str(item.get("id", "")) not in deletable_ids
        ]
        self._selected_page_ids.difference_update(deletable_ids)
        if self._selection_anchor_id in deletable_ids:
            self._selection_anchor_id = None
        self._enforce_structural_order()
        self._save_data()
        self._refresh_sequence()

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

    def _update_page_type_button_states(self) -> None:
        present_types = {
            str(item.get("type", ""))
            for item in self._items()
        }

        for page_type, button in self._page_type_buttons.items():
            definition = self._definition_for(page_type)
            is_single = bool(definition.get("single", False))
            state = (
                "disabled"
                if is_single and page_type in present_types
                else "normal"
            )
            if self._page_type_button_states.get(page_type) == state:
                continue
            button.configure(state=state)
            self._page_type_button_states[page_type] = state

    def _is_locked_structural_type(self, page_type: str) -> bool:
        definition = self._definition_for(page_type)
        return bool(definition.get("locked_position", False))

    def _can_move_item(self, index: int, delta: int) -> bool:
        items = self._items()
        if not 0 <= index < len(items):
            return False

        current = items[index]
        current_type = str(current.get("type", ""))
        if bool(current.get("automatic_recto_verso", False)):
            return False
        if self._is_locked_structural_type(current_type):
            return False

        base_items = [
            item
            for item in items
            if not bool(item.get("automatic_recto_verso", False))
        ]
        current_id = str(current.get("id", ""))
        base_index = next(
            (
                position
                for position, item in enumerate(base_items)
                if str(item.get("id", "")) == current_id
            ),
            None,
        )
        if base_index is None:
            return False

        target_index = base_index + delta
        if not 0 <= target_index < len(base_items):
            return False

        target = base_items[target_index]
        target_type = str(target.get("type", ""))
        if not self._is_locked_structural_type(target_type):
            return True

        # À la frontière d'un groupe structurel, Monter/Descendre peut changer
        # l'appartenance visuelle sans franchir la couverture verrouillée.
        target_group = self._plan_group_id(target)
        current_group = self._plan_group_id(current)
        if delta < 0 and target_type in self.START_STRUCTURAL_TYPES:
            return current_group != target_group
        if delta > 0 and target_type in self.END_STRUCTURAL_TYPES:
            return current_group != target_group
        return False

    def _new_item_from_definition(
        self,
        definition: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "id": f"MAQUETTE-{uuid4().hex[:12].upper()}",
            "type": str(definition["type"]),
            "title": str(definition["title"]),
            "count": 1,
            "done": False,
            "plan_group": str(definition.get("group", "pages_interieures")),
        }

    def _plan_group_id(self, item: dict[str, Any]) -> str:
        """Groupe visuel d'une occurrence dans le Plan du livre."""
        valid_groups = {
            str(group.get("id", ""))
            for group in self._groups()
            if str(group.get("id", ""))
        }

        if bool(item.get("automatic_recto_verso", False)):
            target_id = str(item.get("recto_target_id", ""))
            for candidate in self._items():
                if str(candidate.get("id", "")) == target_id:
                    return self._plan_group_id(candidate)

        stored = str(item.get("plan_group", ""))
        if stored in valid_groups:
            return stored

        definition = self._definition_for(str(item.get("type", "inconnu")))
        default_group = str(definition.get("group", "pages_interieures"))
        if default_group in valid_groups:
            return default_group
        return default_group

    def _plan_group_rank(self, group_id: str) -> int:
        for index, group in enumerate(self._groups()):
            if str(group.get("id", "")) == group_id:
                return index
        return len(self._groups())

    def _plan_group_page_color(self, group_id: str, fallback: str) -> str:
        """Crée une nuance claire à partir de la couleur du groupe."""
        group = self._group_for(group_id)
        color = str(group.get("accent", fallback))
        value = color.lstrip("#")
        if len(value) != 6:
            return fallback
        try:
            red = int(value[0:2], 16)
            green = int(value[2:4], 16)
            blue = int(value[4:6], 16)
        except ValueError:
            return fallback

        # 82 % de blanc : couleur du groupe visible mais douce.
        factor = 0.82
        red = int(red + (255 - red) * factor)
        green = int(green + (255 - green) * factor)
        blue = int(blue + (255 - blue) * factor)
        return f"#{red:02X}{green:02X}{blue:02X}"

    def _plan_group_insert_index(
        self,
        base_items: list[dict[str, Any]],
        group_id: str,
    ) -> int:
        """Insère une nouvelle page à la suite des pages de son groupe."""
        last_same = -1
        for index, item in enumerate(base_items):
            page_type = str(item.get("type", ""))
            if page_type in self.END_STRUCTURAL_TYPES:
                continue
            if self._plan_group_id(item) == group_id:
                last_same = index

        if last_same >= 0:
            return last_same + 1

        target_rank = self._plan_group_rank(group_id)
        for index, item in enumerate(base_items):
            page_type = str(item.get("type", ""))
            if page_type in self.END_STRUCTURAL_TYPES:
                return index
            if self._plan_group_rank(self._plan_group_id(item)) > target_rank:
                return index
        return len(base_items)

    def _plan_destination_group(
        self,
        dragged_items: list[dict[str, Any]],
        remaining_regular: list[dict[str, Any]],
        insertion_index: int,
        moving_down: bool,
    ) -> str:
        """Détermine le groupe rejoint lors d'un glisser-déposer."""
        source_group = (
            self._plan_group_id(dragged_items[0])
            if dragged_items
            else "pages_interieures"
        )

        before_group = None
        after_group = None
        if insertion_index > 0:
            before_group = self._plan_group_id(
                remaining_regular[insertion_index - 1]
            )
        if insertion_index < len(remaining_regular):
            after_group = self._plan_group_id(
                remaining_regular[insertion_index]
            )

        # Aux deux bornes, les couvertures servent de groupe de destination.
        if before_group is None:
            starts = [
                item
                for item in self._items()
                if not bool(item.get("automatic_recto_verso", False))
                and str(item.get("type", "")) in self.START_STRUCTURAL_TYPES
            ]
            if starts:
                before_group = self._plan_group_id(starts[-1])

        if after_group is None:
            ends = [
                item
                for item in self._items()
                if not bool(item.get("automatic_recto_verso", False))
                and str(item.get("type", "")) in self.END_STRUCTURAL_TYPES
            ]
            if ends:
                after_group = self._plan_group_id(ends[0])

        if before_group == after_group and before_group:
            return before_group
        if before_group and before_group != source_group and after_group == source_group:
            return before_group
        if after_group and after_group != source_group and before_group == source_group:
            return after_group
        if before_group and after_group and before_group != after_group:
            return after_group if moving_down else before_group
        return before_group or after_group or source_group

    def _enforce_structural_order(self) -> None:
        items = self._items()

        # La couverture et la quatrième sont les deux bornes obligatoires
        # de tout projet. Elles sont recréées si un ancien fichier ou une
        # donnée endommagée ne les contient pas.
        present_types = {str(item.get("type", "")) for item in items}
        for page_type in ("couverture", "quatrieme"):
            if page_type not in present_types:
                definition = self._definition_for(page_type)
                items.append(self._new_item_from_definition(definition))
                present_types.add(page_type)

        seen_single_types: set[str] = set()
        unique_items: list[dict[str, Any]] = []

        for item in items:
            page_type = str(item.get("type", ""))
            definition = self._definition_for(page_type)
            if bool(definition.get("single", False)):
                if page_type in seen_single_types:
                    continue
                seen_single_types.add(page_type)
            unique_items.append(item)

        structural_items: dict[str, dict[str, Any]] = {}
        regular_items: list[dict[str, Any]] = []
        for item in unique_items:
            page_type = str(item.get("type", ""))
            if page_type in self.STRUCTURAL_TYPES:
                structural_items[page_type] = item
            else:
                regular_items.append(item)

        ordered: list[dict[str, Any]] = []
        for page_type in self.START_STRUCTURAL_TYPES:
            item = structural_items.get(page_type)
            if item is not None:
                ordered.append(item)

        ordered.extend(regular_items)

        for page_type in self.END_STRUCTURAL_TYPES:
            item = structural_items.get(page_type)
            if item is not None:
                ordered.append(item)

        items[:] = ordered
        self._apply_recto_verso_rules()

    # ==========================================================
    # Règles recto-verso
    # ==========================================================

    def _recto_verso_rules(self) -> list[dict[str, Any]]:
        rules = self.data.setdefault("recto_verso_rules", [])
        if not isinstance(rules, list):
            rules = []
            self.data["recto_verso_rules"] = rules
        return rules

    def _eligible_recto_verso_types(self) -> list[dict[str, Any]]:
        # Couvertures et règles autorisées :
        # - 2e de couverture : blanc après uniquement ;
        # - 3e de couverture : blanc avant uniquement ;
        # - 4e de couverture : blanc avant uniquement.
        # La couverture reste exclue.
        excluded = {
            "couverture",
            "page_blanche",
        }
        return [
            definition
            for definition in self._page_types()
            if str(definition.get("type", "")) not in excluded
        ]

    def _open_recto_verso_dialog(self) -> None:
        if self._recto_verso_window is not None:
            try:
                if self._recto_verso_window.winfo_exists():
                    self._recto_verso_window.deiconify()
                    self._recto_verso_window.lift()
                    self._recto_verso_window.focus_set()
                    return
            except Exception:
                self._recto_verso_window = None

        owner = self.parent.winfo_toplevel()
        window = ctk.CTkToplevel(owner)
        self._recto_verso_window = window
        self._recto_rule_editor_id = None
        window.title("Règles recto-verso")
        window.geometry("900x650")
        window.minsize(760, 560)
        window.configure(fg_color=self.WINDOW_BG)
        window.transient(owner)
        window.protocol("WM_DELETE_WINDOW", self._close_recto_verso_dialog)

        header = ctk.CTkFrame(window, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 10))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header,
            text="Règles recto-verso du projet",
            font=Fonts.H2,
            text_color=self.INK,
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header,
            text=(
                "Sélectionnez plusieurs types de pages, puis choisissez "
                "l’ajout d’une page blanche avant ou après."
            ),
            font=Fonts.SMALL,
            text_color=self.TEXT_MUTED,
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=(3, 0))

        body = ctk.CTkFrame(window, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=24, pady=(0, 12))
        body.grid_columnconfigure(0, weight=1, uniform="recto")
        body.grid_columnconfigure(1, weight=1, uniform="recto")
        body.grid_rowconfigure(0, weight=1)

        rules_panel = ctk.CTkFrame(
            body,
            fg_color=self.RIBBON_BG,
            corner_radius=8,
            border_width=1,
            border_color=self.BORDER,
        )
        rules_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        rules_panel.grid_columnconfigure(0, weight=1)
        rules_panel.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(
            rules_panel,
            text="Règles enregistrées",
            font=Fonts.NORMAL,
            text_color=self.INK,
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 7))
        rules_scroll = ctk.CTkScrollableFrame(
            rules_panel,
            fg_color="transparent",
            corner_radius=0,
        )
        rules_scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, 8))
        rules_scroll.grid_columnconfigure(0, weight=1)

        editor_panel = ctk.CTkFrame(
            body,
            fg_color=self.RIBBON_BG,
            corner_radius=8,
            border_width=1,
            border_color=self.BORDER,
        )
        editor_panel.grid(row=0, column=1, sticky="nsew", padx=(6, 0))
        editor_panel.grid_columnconfigure(0, weight=1)
        editor_panel.grid_rowconfigure(2, weight=1)

        editor_title = ctk.CTkLabel(
            editor_panel,
            text="Nouvelle règle",
            font=Fonts.NORMAL,
            text_color=self.INK,
        )
        editor_title.grid(row=0, column=0, sticky="w", padx=14, pady=(12, 7))

        position_var = ctk.StringVar(value="before")
        position_frame = ctk.CTkFrame(editor_panel, fg_color="transparent")
        position_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 6))
        ctk.CTkRadioButton(
            position_frame,
            text="Page blanche avant",
            value="before",
            variable=position_var,
            font=Fonts.SMALL,
            text_color=self.INK,
            fg_color=self.SKY,
            hover_color=self.INK,
        ).pack(side="left", padx=(0, 12))
        ctk.CTkRadioButton(
            position_frame,
            text="Page blanche après",
            value="after",
            variable=position_var,
            font=Fonts.SMALL,
            text_color=self.INK,
            fg_color=self.SKY,
            hover_color=self.INK,
        ).pack(side="left")

        types_scroll = ctk.CTkScrollableFrame(
            editor_panel,
            fg_color=self.GROUP_BG,
            corner_radius=6,
            border_width=1,
            border_color=self.BORDER,
        )
        types_scroll.grid(row=2, column=0, sticky="nsew", padx=12, pady=(0, 8))
        types_scroll.grid_columnconfigure(0, weight=1)

        type_vars: dict[str, ctk.BooleanVar] = {}
        type_checks: dict[str, ctk.CTkCheckBox] = {}
        row_index = 0
        for group in self._groups():
            group_id = str(group.get("id", ""))
            definitions = [
                definition
                for definition in self._eligible_recto_verso_types()
                if str(definition.get("group", "")) == group_id
            ]
            if not definitions:
                continue
            ctk.CTkLabel(
                types_scroll,
                text=str(group.get("title", "Groupe")),
                font=(Fonts.FAMILY, 10, "bold"),
                text_color=str(group.get("accent", self.INK)),
            ).grid(row=row_index, column=0, sticky="w", padx=8, pady=(8, 3))
            row_index += 1
            for definition in definitions:
                page_type = str(definition.get("type", ""))
                variable = ctk.BooleanVar(value=False)
                type_vars[page_type] = variable
                checkbox_text = str(definition.get("title", "Page"))
                if page_type == "deuxieme_couverture":
                    checkbox_text += " — après uniquement"
                elif page_type in {"troisieme_couverture", "quatrieme"}:
                    checkbox_text += " — avant uniquement"
                checkbox = ctk.CTkCheckBox(
                    types_scroll,
                    text=checkbox_text,
                    variable=variable,
                    checkbox_width=17,
                    checkbox_height=17,
                    font=Fonts.SMALL,
                    text_color=self.INK,
                    fg_color=str(definition.get("accent", self.CELADON)),
                    hover_color=self.INK,
                )
                checkbox.grid(
                    row=row_index,
                    column=0,
                    sticky="w",
                    padx=14,
                    pady=2,
                )
                type_checks[page_type] = checkbox
                row_index += 1

        def update_position_constraints(*_args: Any) -> None:
            position = position_var.get()
            restrictions = {
                "deuxieme_couverture": "after",
                "troisieme_couverture": "before",
                "quatrieme": "before",
            }
            for page_type, allowed_position in restrictions.items():
                variable = type_vars.get(page_type)
                checkbox = type_checks.get(page_type)
                if variable is None or checkbox is None:
                    continue
                if position != allowed_position:
                    variable.set(False)
                    checkbox.configure(state="disabled")
                else:
                    checkbox.configure(state="normal")

        position_var.trace_add("write", update_position_constraints)
        update_position_constraints()

        status_label = ctk.CTkLabel(
            editor_panel,
            text="",
            font=Fonts.SMALL,
            text_color=self.CORAL,
            anchor="w",
        )
        status_label.grid(row=3, column=0, sticky="ew", padx=14, pady=(0, 4))

        actions = ctk.CTkFrame(editor_panel, fg_color="transparent")
        actions.grid(row=4, column=0, sticky="ew", padx=12, pady=(0, 12))
        actions.grid_columnconfigure(0, weight=1)
        save_button = ctk.CTkButton(
            actions,
            text="Ajouter la règle",
            height=32,
            corner_radius=7,
            fg_color=self.INK,
            hover_color="#35537E",
            text_color="#FFFFFF",
            font=Fonts.SMALL,
        )
        save_button.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        cancel_edit_button = ctk.CTkButton(
            actions,
            text="Annuler la modification",
            width=150,
            height=32,
            corner_radius=7,
            fg_color=self.GROUP_BG,
            hover_color=Colors.BUTTON_HOVER,
            text_color=self.INK,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.SMALL,
            state="disabled",
        )
        cancel_edit_button.grid(row=0, column=1, padx=(5, 0))

        def clear_editor() -> None:
            self._recto_rule_editor_id = None
            for variable in type_vars.values():
                variable.set(False)
            position_var.set("before")
            editor_title.configure(text="Nouvelle règle")
            save_button.configure(text="Ajouter la règle")
            cancel_edit_button.configure(state="disabled")
            status_label.configure(text="")

        def render_rules() -> None:
            for child in rules_scroll.winfo_children():
                child.destroy()
            rules = self._recto_verso_rules()
            if not rules:
                ctk.CTkLabel(
                    rules_scroll,
                    text="Aucune règle définie pour ce projet.",
                    font=Fonts.SMALL,
                    text_color=self.TEXT_LIGHT,
                ).grid(row=0, column=0, sticky="w", padx=8, pady=10)
                return
            for row, rule in enumerate(rules):
                rule_id = str(rule.get("id", ""))
                names = [
                    str(self._definition_for(page_type).get("short", page_type))
                    for page_type in rule.get("page_types", [])
                ]
                position_text = (
                    "Page blanche avant" if rule.get("position") == "before"
                    else "Page blanche après"
                )
                card = ctk.CTkFrame(
                    rules_scroll,
                    fg_color=self.GROUP_BG,
                    corner_radius=7,
                    border_width=1,
                    border_color=self.BORDER,
                )
                card.grid(row=row, column=0, sticky="ew", padx=2, pady=3)
                card.grid_columnconfigure(0, weight=1)
                ctk.CTkLabel(
                    card,
                    text=position_text,
                    font=(Fonts.FAMILY, 10, "bold"),
                    text_color=self.INK,
                    anchor="w",
                ).grid(row=0, column=0, sticky="w", padx=10, pady=(7, 1))
                ctk.CTkLabel(
                    card,
                    text=", ".join(names),
                    font=Fonts.SMALL,
                    text_color=self.TEXT_MUTED,
                    anchor="w",
                    wraplength=260,
                    justify="left",
                ).grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 7))
                buttons = ctk.CTkFrame(card, fg_color="transparent")
                buttons.grid(row=0, column=1, rowspan=2, padx=7, pady=6)
                ctk.CTkButton(
                    buttons,
                    text="Modifier",
                    width=68,
                    height=25,
                    corner_radius=6,
                    fg_color=self.GROUP_BG,
                    hover_color=Colors.BUTTON_HOVER,
                    text_color=self.INK,
                    border_width=1,
                    border_color=self.BORDER,
                    font=(Fonts.FAMILY, 9),
                    command=lambda current=rule_id: edit_rule(current),
                ).pack(pady=(0, 3))
                ctk.CTkButton(
                    buttons,
                    text="Supprimer",
                    width=68,
                    height=25,
                    corner_radius=6,
                    fg_color=self.GROUP_BG,
                    hover_color="#F3E4E1",
                    text_color=self.DANGER,
                    border_width=1,
                    border_color="#E0B9B0",
                    font=(Fonts.FAMILY, 9),
                    command=lambda current=rule_id: delete_rule(current),
                ).pack()

        def edit_rule(rule_id: str) -> None:
            rule = next(
                (item for item in self._recto_verso_rules()
                 if str(item.get("id", "")) == rule_id),
                None,
            )
            if rule is None:
                return
            clear_editor()
            self._recto_rule_editor_id = rule_id
            for page_type in rule.get("page_types", []):
                variable = type_vars.get(str(page_type))
                if variable is not None:
                    variable.set(True)
            position_var.set(str(rule.get("position", "before")))
            editor_title.configure(text="Modifier la règle")
            save_button.configure(text="Enregistrer")
            cancel_edit_button.configure(state="normal")

        def delete_rule(rule_id: str) -> None:
            rules = self._recto_verso_rules()
            new_rules = [
                rule for rule in rules
                if str(rule.get("id", "")) != rule_id
            ]
            if len(new_rules) == len(rules):
                return
            self._record_history()
            self.data["recto_verso_rules"] = new_rules
            self._enforce_structural_order()
            self._save_data()
            self._refresh_sequence()
            clear_editor()
            render_rules()

        def save_rule() -> None:
            selected = [
                page_type
                for page_type, variable in type_vars.items()
                if variable.get()
            ]
            if not selected:
                status_label.configure(
                    text="Sélectionnez au moins un type de page."
                )
                return
            position = position_var.get()
            invalid = (
                (
                    position == "before"
                    and "deuxieme_couverture" in selected
                )
                or (
                    position == "after"
                    and (
                        "troisieme_couverture" in selected
                        or "quatrieme" in selected
                    )
                )
            )
            if invalid:
                status_label.configure(
                    text=(
                        "Position non autorisée : "
                        "2e = après uniquement ; "
                        "3e et 4e = avant uniquement."
                    )
                )
                return
            editing_id = self._recto_rule_editor_id
            rules = deepcopy(self._recto_verso_rules())

            # Une même page ne reçoit qu’une fois la même consigne.
            for rule in rules:
                if str(rule.get("id", "")) == str(editing_id or ""):
                    continue
                if str(rule.get("position", "")) != position:
                    continue
                overlap = set(rule.get("page_types", [])) & set(selected)
                if overlap:
                    labels = [
                        str(self._definition_for(value).get("short", value))
                        for value in sorted(overlap)
                    ]
                    status_label.configure(
                        text=(
                            "Règle déjà présente pour : "
                            + ", ".join(labels)
                        )
                    )
                    return

            rule_value = {
                "id": editing_id or f"RECTO-{uuid4().hex[:10].upper()}",
                "page_types": selected,
                "position": position,
            }
            if editing_id:
                rules = [
                    rule_value
                    if str(rule.get("id", "")) == editing_id
                    else rule
                    for rule in rules
                ]
            else:
                rules.append(rule_value)

            self._record_history()
            self.data["recto_verso_rules"] = rules
            self._enforce_structural_order()
            self._save_data()
            self._refresh_sequence()
            clear_editor()
            render_rules()

        save_button.configure(command=save_rule)
        cancel_edit_button.configure(command=clear_editor)
        render_rules()

        footer = ctk.CTkFrame(window, fg_color="transparent")
        footer.pack(fill="x", padx=24, pady=(0, 18))
        ctk.CTkLabel(
            footer,
            text=(
                "Les pages blanches automatiques restent liées à leur règle "
                "et ne sont pas déplaçables manuellement."
            ),
            font=Fonts.SMALL,
            text_color=self.TEXT_MUTED,
        ).pack(side="left")
        ctk.CTkButton(
            footer,
            text="Fermer",
            width=100,
            height=32,
            corner_radius=7,
            fg_color=self.GROUP_BG,
            hover_color=Colors.BUTTON_HOVER,
            text_color=self.INK,
            border_width=1,
            border_color=self.BORDER,
            font=Fonts.SMALL,
            command=self._close_recto_verso_dialog,
        ).pack(side="right")

        def activate() -> None:
            try:
                if window.winfo_exists():
                    window.lift()
                    window.focus_set()
                    window.grab_set()
            except Exception:
                pass
        window.after(120, activate)

    def _close_recto_verso_dialog(self) -> None:
        window = self._recto_verso_window
        self._recto_verso_window = None
        self._recto_rule_editor_id = None
        if window is None:
            return
        try:
            window.grab_release()
        except Exception:
            pass
        try:
            if window.winfo_exists():
                window.destroy()
        except Exception:
            pass

    def _normalize_recto_verso_rules(
        self,
        raw_rules: Any,
    ) -> list[dict[str, Any]]:
        eligible = {
            str(definition.get("type", ""))
            for definition in self._eligible_recto_verso_types()
        }
        normalized: list[dict[str, Any]] = []
        if not isinstance(raw_rules, list):
            return normalized
        occupied: set[tuple[str, str]] = set()
        for raw in raw_rules:
            if not isinstance(raw, dict):
                continue
            position = str(raw.get("position", "before"))
            if position not in {"before", "after"}:
                position = "before"
            values: list[str] = []
            for value in raw.get("page_types", []):
                page_type = str(value)
                key = (position, page_type)
                if (
                    page_type == "deuxieme_couverture"
                    and position != "after"
                ):
                    continue
                if (
                    page_type in {"troisieme_couverture", "quatrieme"}
                    and position != "before"
                ):
                    continue
                if page_type in eligible and key not in occupied:
                    values.append(page_type)
                    occupied.add(key)
            if not values:
                continue
            normalized.append(
                {
                    "id": str(raw.get("id") or f"RECTO-{uuid4().hex[:10].upper()}"),
                    "page_types": values,
                    "position": position,
                }
            )
        return normalized

    def _new_automatic_blank(
        self,
        target_id: str,
        position: str,
        count: int = 1,
    ) -> dict[str, Any]:
        definition = self._definition_for("page_blanche")
        item = self._new_item_from_definition(definition)
        normalized_count = max(1, int(count))
        item["count"] = normalized_count
        item["automatic_recto_verso"] = True
        item["recto_target_id"] = target_id
        item["recto_position"] = position
        item["title"] = (
            "Page blanche automatique"
            if normalized_count == 1
            else "Pages blanches automatiques"
        )
        return item

    def _recto_rule_type_sets(self) -> tuple[set[str], set[str]]:
        before_types: set[str] = set()
        after_types: set[str] = set()
        for rule in self._recto_verso_rules():
            destination = (
                before_types
                if str(rule.get("position", "before")) == "before"
                else after_types
            )
            destination.update(
                str(value) for value in rule.get("page_types", [])
            )
        # Sécurité structurelle des couvertures.
        before_types.discard("deuxieme_couverture")
        after_types.discard("troisieme_couverture")
        after_types.discard("quatrieme")
        return before_types, after_types

    def _apply_recto_verso_rules(self) -> None:
        before_types, after_types = self._recto_rule_type_sets()

        base_items = [
            item
            for item in self._items()
            if not bool(item.get("automatic_recto_verso", False))
        ]
        rebuilt: list[dict[str, Any]] = []

        for index, item in enumerate(base_items):
            page_type = str(item.get("type", ""))
            item_id = str(item.get("id", ""))
            count = max(1, int(item.get("count", 1)))
            previous_type = (
                str(base_items[index - 1].get("type", ""))
                if index > 0
                else ""
            )
            next_type = (
                str(base_items[index + 1].get("type", ""))
                if index + 1 < len(base_items)
                else ""
            )

            # Une règle visant la quatrième se place avant tout le bloc de fin.
            # Si la troisième existe, elle reste donc immédiatement accolée à la
            # quatrième, conformément à sa position structurelle verrouillée.
            fourth_rule_before_end_block = (
                page_type == "troisieme_couverture"
                and next_type == "quatrieme"
                and "quatrieme" in before_types
            )
            wants_before = page_type in before_types or fourth_rule_before_end_block
            if page_type == "quatrieme" and previous_type == "troisieme_couverture":
                wants_before = False

            if wants_before:
                # Pour une page répétée, la règle concerne chaque occurrence.
                # Lorsque la même page reçoit aussi une règle « après », les
                # blancs intermédiaires sont partagés : un seul blanc initial
                # reste à représenter avant le bloc.
                before_count = 1 if page_type in after_types else count

                previous_base_type = previous_type
                previous_has_after = previous_base_type in after_types
                if previous_has_after and previous_base_type != "page_blanche":
                    # Le dernier blanc « après » de la page précédente satisfait
                    # aussi le premier blanc « avant » de la page courante.
                    before_count = max(0, before_count - 1)

                if before_count > 0:
                    if rebuilt and bool(
                        rebuilt[-1].get("automatic_recto_verso", False)
                    ):
                        merged_count = (
                            max(1, int(rebuilt[-1].get("count", 1)))
                            + before_count
                        )
                        rebuilt[-1]["count"] = merged_count
                        rebuilt[-1]["title"] = "Pages blanches automatiques"
                        rebuilt[-1]["recto_shared"] = True
                    else:
                        rebuilt.append(
                            self._new_automatic_blank(
                                item_id,
                                "before",
                                before_count,
                            )
                        )

            rebuilt.append(item)

            if page_type in after_types:
                rebuilt.append(
                    self._new_automatic_blank(item_id, "after", count)
                )

        # Sécurité finale : deux blocs automatiques voisins sont fusionnés.
        compacted: list[dict[str, Any]] = []
        for item in rebuilt:
            if (
                compacted
                and bool(item.get("automatic_recto_verso", False))
                and bool(compacted[-1].get("automatic_recto_verso", False))
            ):
                merged_count = (
                    max(1, int(compacted[-1].get("count", 1)))
                    + max(1, int(item.get("count", 1)))
                )
                compacted[-1]["count"] = merged_count
                compacted[-1]["title"] = "Pages blanches automatiques"
                compacted[-1]["recto_shared"] = True
                continue
            compacted.append(item)

        self._items()[:] = compacted

    def _create_preview_background_canvas(
        self,
        parent,
        *,
        fixed_height: int | None = None,
    ) -> tk.Canvas:
        """Fond stable de l'Aperçu : l'image reste un item du Canvas.

        Les widgets sont de vraies fenêtres enfants du Canvas et ne peuvent
        donc plus être recouverts par le redessin du fond.
        """
        canvas = tk.Canvas(
            parent,
            background=self.WINDOW_BG,
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.BORDER,
        )
        if fixed_height is not None:
            canvas.configure(height=fixed_height)

        canvas._preview_background_source = None
        canvas._preview_background_photo = None
        canvas._preview_background_item = None
        canvas._preview_background_job = None

        background_path = (
            Path(__file__).resolve().parents[3]
            / "assets"
            / "interface"
            / "backgrounds"
            / "editorial_bg_soft.png"
        )

        if not background_path.is_file():
            return canvas

        try:
            from PIL import Image, ImageTk

            source = Image.open(background_path).convert("RGB")
            canvas._preview_background_source = source
            canvas._preview_background_item = canvas.create_image(
                0,
                0,
                anchor="nw",
            )

            def redraw_now() -> None:
                canvas._preview_background_job = None
                try:
                    width = max(1, int(canvas.winfo_width()))
                    height = max(1, int(canvas.winfo_height()))
                    if width <= 2 or height <= 2:
                        return

                    source_ratio = source.width / source.height
                    target_ratio = width / height

                    if target_ratio > source_ratio:
                        resize_width = width
                        resize_height = max(
                            height,
                            int(round(width / source_ratio)),
                        )
                    else:
                        resize_height = height
                        resize_width = max(
                            width,
                            int(round(height * source_ratio)),
                        )

                    resized = source.resize(
                        (resize_width, resize_height),
                        Image.Resampling.LANCZOS,
                    )
                    left = max(0, (resize_width - width) // 2)
                    top = max(0, (resize_height - height) // 2)
                    cropped = resized.crop(
                        (left, top, left + width, top + height)
                    )

                    photo = ImageTk.PhotoImage(cropped)
                    canvas._preview_background_photo = photo
                    canvas.itemconfigure(
                        canvas._preview_background_item,
                        image=photo,
                    )
                    canvas.coords(
                        canvas._preview_background_item,
                        0,
                        0,
                    )
                    canvas.tag_lower(canvas._preview_background_item)
                except Exception:
                    pass

            def schedule_redraw(_event=None) -> None:
                job = getattr(
                    canvas,
                    "_preview_background_job",
                    None,
                )
                if job is not None:
                    try:
                        canvas.after_cancel(job)
                    except Exception:
                        pass
                canvas._preview_background_job = canvas.after(
                    35,
                    redraw_now,
                )

            canvas.bind("<Configure>", schedule_redraw, add="+")
            canvas.after_idle(redraw_now)
        except Exception:
            pass

        return canvas

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

        # APERCU_GRANDE_VUE_V3
        # APERCU_MAQUETTAGE_GRANDE_VUE_SEULE_V1
        # APERCU_CADRAGE_VERTICAL_CENTRE_V1
        # APERCU_FOND_CONTINU_CENTRAGE_V1
        # APERCU_OUTILS_RESPIRATION_V1
        # APERCU_COMMANDES_EPUREES_SANS_FLASH_V2
        # APERCU_FINITION_VISUELLE_V3
        # APERCU_FENETRE_CENTREE_V1
        preview_width = 840
        preview_height = 650
        window.minsize(740, 560)
        window.update_idletasks()

        screen_width = int(window.winfo_screenwidth())
        screen_height = int(window.winfo_screenheight())
        pos_x = max(0, (screen_width - preview_width) // 2)
        pos_y = max(0, (screen_height - preview_height) // 2)

        window.geometry(
            f"{preview_width}x{preview_height}+{pos_x}+{pos_y}"
        )
        window.configure(fg_color=self.WINDOW_BG)
        window.protocol("WM_DELETE_WINDOW", self._close_preview)
        window.grid_columnconfigure(0, weight=1)
        window.grid_rowconfigure(2, weight=1)
        window.bind("<Left>", lambda _event: self._show_previous_spread())
        window.bind("<Right>", lambda _event: self._show_next_spread())

        self._preview_animating = False
        self._preview_turn_photo = None
        self._preview_turn_overlay = None
        self._preview_turn_shadow = None
        self._preview_static_widgets: list[tk.Widget] = []
        self._preview_static_canvas_items: list[int] = []

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

        # Les trois commandes universelles sont posées directement
        # sur le décor PageMaître, sans groupe ni bandeau coloré.
        ribbon = self._create_preview_background_canvas(
            window,
            fixed_height=66,
        )
        ribbon.configure(highlightthickness=0)
        ribbon.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=12,
            pady=(0, 6),
        )
        ribbon.grid_propagate(False)

        def preview_icon_button(
            icon: str,
            command,
            x_offset: int,
            *,
            accent: str | None = None,
            tooltip: str,
        ) -> ctk.CTkButton:
            text_color = accent or self.INK
            border = self._mix_color_with_white(text_color, 0.55)
            hover = self._mix_color_with_white(text_color, 0.88)
            button = ctk.CTkButton(
                ribbon,
                text=icon,
                width=66,
                height=39,
                corner_radius=5,
                fg_color=self.GROUP_BG,
                hover_color=hover,
                text_color=text_color,
                border_width=1,
                border_color=border,
                font=(Fonts.FAMILY, 14, "bold"),
                command=command,
            )
            button.place(
                relx=0.5,
                rely=0.5,
                x=x_offset,
                anchor="center",
            )
            self._attach_tooltip(button, tooltip)
            return button

        self._preview_previous_button = preview_icon_button(
            "◀",
            self._show_previous_spread,
            -70,
            tooltip="Précédent",
        )
        self._preview_next_button = preview_icon_button(
            "▶",
            self._show_next_spread,
            0,
            tooltip="Suivant",
        )
        preview_icon_button(
            "×",
            self._close_preview,
            70,
            accent=self.CORAL,
            tooltip="Fermer",
        )

        # Une seule surface décorée reçoit directement les pages et leurs noms.
        # Aucun panneau intermédiaire n'est visible sous le livre.
        self._preview_body = self._create_preview_background_canvas(window)
        self._preview_body.configure(highlightthickness=0)
        self._preview_body.grid(
            row=2,
            column=0,
            sticky="nsew",
            padx=12,
            pady=(0, 5),
        )

        # Aucune barre d'état opaque : les informations de position sont
        # dessinées directement sur le décor général, sous le livre.
        self._preview_nav = None
        self._preview_position_label = None

        self._preview_spreads = self._build_preview_spreads(
            list(self._items())
        )
        self._preview_index = 0
        self._preview_mode = "large"
        self._preview_large_button = None
        self._preview_overview_button = None
        # Laisse Tk calculer la largeur réelle du Canvas avant de placer
        # la couverture. Cela évite qu'elle utilise la largeur de secours
        # de 640 px et apparaisse décalée vers la gauche au premier affichage.
        window.update_idletasks()
        window.after(40, self._render_preview_current_spread)
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

        base_items = [
            item
            for item in items
            if not bool(item.get("automatic_recto_verso", False))
        ]
        covers = [
            item for item in base_items if item.get("type") == "couverture"
        ]
        fourths = [
            item for item in base_items if item.get("type") == "quatrieme"
        ]

        if covers:
            spreads.append((None, covers[0], None, None))

        before_types, after_types = self._recto_rule_type_sets()
        expanded_pages: list[dict[str, Any]] = []

        def append_preview_blank(target: dict[str, Any], position: str) -> None:
            # Deux blancs automatiques ne se suivent jamais. Un blanc manuel
            # reste en revanche un choix explicite et peut créer un doublon.
            if (
                expanded_pages
                and bool(
                    expanded_pages[-1].get("automatic_recto_verso", False)
                )
            ):
                return
            expanded_pages.append(
                self._new_automatic_blank(
                    str(target.get("id", "")),
                    position,
                    1,
                )
            )

        third_present = any(
            str(item.get("type", "")) == "troisieme_couverture"
            for item in base_items
        )

        for item in base_items:
            page_type = str(item.get("type", ""))
            if page_type == "couverture":
                continue

            count = max(1, int(item.get("count", 1)))
            for _occurrence in range(count):
                wants_before = page_type in before_types
                if (
                    page_type == "troisieme_couverture"
                    and third_present
                    and "quatrieme" in before_types
                ):
                    wants_before = True
                if page_type == "quatrieme" and third_present:
                    wants_before = False

                if wants_before:
                    append_preview_blank(item, "before")

                if page_type == "quatrieme":
                    continue

                expanded_pages.append(item)

                if page_type in after_types:
                    append_preview_blank(item, "after")

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
        body = self._preview_body
        if body is None:
            return

        body.update_idletasks()
        body_width = max(640, int(body.winfo_width()))
        body_height = max(460, int(body.winfo_height()))

        old_widgets = list(
            getattr(self, "_preview_static_widgets", [])
        )
        old_items = list(
            getattr(self, "_preview_static_canvas_items", [])
        )
        new_widgets: list[tk.Widget] = []
        new_items: list[int] = []

        def caption_for(
            item: dict[str, Any],
            number: int | None,
        ) -> tuple[str, str]:
            definition = self._definition_for(
                str(item.get("type", "autre"))
            )
            title = str(
                item.get("title")
                or definition.get("title", "Page")
            )
            caption = title
            if number is not None:
                caption = f"p. {number} · {title}"
            done = bool(item.get("done", False))
            if done:
                caption = f"✓ {caption}"
            return caption, self.DONE if done else self.INK

        if not self._preview_spreads:
            new_items.append(
                body.create_text(
                    body_width // 2,
                    body_height // 2,
                    text="Aucune page.",
                    fill=self.TEXT_LIGHT,
                    font=Fonts.NORMAL,
                    anchor="center",
                )
            )
        else:
            self._preview_index = max(
                0,
                min(self._preview_index, len(self._preview_spreads) - 1),
            )
            left_item, right_item, left_number, right_number = (
                self._preview_spreads[self._preview_index]
            )

            visible_pages = [
                (left_item, left_number),
                (right_item, right_number),
            ]
            visible_pages = [
                (item, number)
                for item, number in visible_pages
                if item is not None
            ]

            page_width = 300
            page_height = 424
            caption_gap = 19
            block_height = page_height + 38
            top_y = max(4, (body_height - block_height) // 2)

            if len(visible_pages) == 1:
                item, number = visible_pages[0]
                page = self._create_preview_large_page(
                    body,
                    item,
                    number,
                )
                x = (body_width - page_width) // 2
                new_widgets.append(page)
                new_items.append(
                    body.create_window(
                        x,
                        top_y,
                        window=page,
                        anchor="nw",
                        width=page_width,
                        height=page_height,
                    )
                )

                caption, color = caption_for(item, number)
                new_items.append(
                    body.create_text(
                        body_width // 2,
                        top_y + page_height + caption_gap,
                        text=caption,
                        fill=color,
                        font=Fonts.SMALL,
                        anchor="center",
                        width=page_width,
                    )
                )
            else:
                gap = 14
                total_width = page_width * 2 + gap
                left_x = (body_width - total_width) // 2
                right_x = left_x + page_width + gap

                for item, number, x in (
                    (left_item, left_number, left_x),
                    (right_item, right_number, right_x),
                ):
                    if item is None:
                        continue

                    page = self._create_preview_large_page(
                        body,
                        item,
                        number,
                    )
                    new_widgets.append(page)
                    new_items.append(
                        body.create_window(
                            x,
                            top_y,
                            window=page,
                            anchor="nw",
                            width=page_width,
                            height=page_height,
                        )
                    )

                    caption, color = caption_for(item, number)
                    new_items.append(
                        body.create_text(
                            x + page_width // 2,
                            top_y + page_height + caption_gap,
                            text=caption,
                            fill=color,
                            font=Fonts.SMALL,
                            anchor="center",
                            width=page_width,
                        )
                    )

        # Position dans le livre : directement sur le décor général,
        # sans bandeau ni fond opaque.
        if self._preview_spreads:
            position = self._preview_spread_title(
                left_item,
                right_item,
                left_number,
                right_number,
            )
            new_items.append(
                body.create_text(
                    body_width // 2,
                    max(12, body_height - 12),
                    text=(
                        f"{position}   ·   "
                        f"{self._preview_index + 1} / "
                        f"{len(self._preview_spreads)}"
                    ),
                    fill=self.INK,
                    font=Fonts.SMALL,
                    anchor="s",
                )
            )

        # Double tampon : le nouvel état est entièrement créé avant que
        # l'ancien disparaisse. Lors d'une rotation, la feuille animée reste
        # au-dessus pendant cette bascule, ce qui supprime le flash blanc.
        body.update_idletasks()

        for widget in old_widgets:
            try:
                widget.destroy()
            except Exception:
                pass
        for item_id in old_items:
            try:
                body.delete(item_id)
            except Exception:
                pass

        self._preview_static_widgets = new_widgets
        self._preview_static_canvas_items = new_items
        self._update_preview_navigation()

    def _create_preview_large_page(
        self,
        parent,
        item: dict[str, Any] | None,
        page_number: int | None = None,
    ) -> tk.Frame:
        # La page est désormais posée directement sur le Canvas général.
        # Son nom est dessiné séparément sur ce même fond par le rendu principal.
        page = tk.Frame(
            parent,
            width=300,
            height=424,
            background="#FFFFFF",
            borderwidth=0,
            highlightthickness=0,
        )
        page.pack_propagate(False)
        page.grid_propagate(False)

        if item is None:
            return page

        definition = self._definition_for(
            str(item.get("type", "autre"))
        )
        done = bool(item.get("done", False))
        plan_group = self._plan_group_id(item)
        group = self._group_for(plan_group)
        accent = str(group.get("accent", self.INK))

        page.configure(
            highlightthickness=2 if done else 1,
            highlightbackground=self.DONE if done else accent,
            highlightcolor=self.DONE if done else accent,
        )

        photo = self._thumbnail_photo_for_definition(
            definition,
            subsample=1,
        )

        if photo is not None:
            image_label = tk.Label(
                page,
                image=photo,
                text="",
                background="#FFFFFF",
                borderwidth=0,
                highlightthickness=0,
            )
            image_label.place(x=0, y=0, relwidth=1, relheight=1)
            page._preview_page_photo = photo
        else:
            fallback_color = self._plan_group_page_color(
                plan_group,
                str(definition.get("color", self.GROUP_BG)),
            )
            page.configure(background=fallback_color)
            tk.Label(
                page,
                text=str(definition.get("symbol", "?")),
                font=(Fonts.FAMILY, 40, "bold"),
                foreground=accent,
                background=fallback_color,
                borderwidth=0,
            ).place(relx=0.5, rely=0.45, anchor="center")

        return page

    def _animate_preview_turn(
        self,
        direction: int,
        target_index: int,
    ) -> None:
        """Tourne une feuille autour de la reliure avec ombre et verso."""
        # APERCU_ROTATION_SANS_FLASH_V2
        if self._preview_body is None:
            return
        if bool(getattr(self, "_preview_animating", False)):
            return

        current = self._preview_spreads[self._preview_index]
        target = self._preview_spreads[target_index]

        current_left, current_right, _, _ = current
        target_left, target_right, _, _ = target

        if direction > 0:
            front_item = current_right or current_left
            back_item = target_left or target_right
        else:
            front_item = current_left or current_right
            back_item = target_right or target_left

        if front_item is None:
            self._preview_index = target_index
            self._render_preview_current_spread()
            return

        def image_for(item):
            if item is None:
                return None
            definition = self._definition_for(
                str(item.get("type", "autre"))
            )
            path = self._thumbnail_path_for_definition(definition)
            if path is None:
                return None
            try:
                from PIL import Image
                return Image.open(path).convert("RGB")
            except Exception:
                return None

        front = image_for(front_item)
        back = image_for(back_item)
        if front is None:
            self._preview_index = target_index
            self._render_preview_current_spread()
            return
        if back is None:
            back = front

        try:
            from PIL import Image, ImageEnhance, ImageTk

            body = self._preview_body
            body.update_idletasks()

            body_width = max(640, int(body.winfo_width()))
            body_height = max(460, int(body.winfo_height()))

            page_height = min(424, max(320, body_height - 70))
            page_width = max(
                1,
                int(round(page_height * 300 / 424)),
            )
            spine_x = body_width // 2

            # APERCU_ROTATION_ALIGNEE_V1
            # L'animation démarre exactement à la hauteur de la page
            # réellement affichée, au lieu d'estimer sa position à partir
            # du centre de la fenêtre.
            top_y = max(0, (body_height - page_height) // 2)
            try:
                body.update_idletasks()

                def descendants(widget):
                    for child in widget.winfo_children():
                        yield child
                        yield from descendants(child)

                page_candidates = []
                for widget in descendants(body):
                    try:
                        width = int(widget.winfo_width())
                        height = int(widget.winfo_height())
                        if (
                            widget.winfo_ismapped()
                            and abs(width - 300) <= 4
                            and abs(height - 424) <= 4
                        ):
                            page_candidates.append(widget)
                    except Exception:
                        pass

                if page_candidates:
                    top_y = min(
                        int(widget.winfo_rooty() - body.winfo_rooty())
                        for widget in page_candidates
                    )
                    page_height = int(page_candidates[0].winfo_height())
                    page_width = int(page_candidates[0].winfo_width())
            except Exception:
                pass

            overlay = tk.Label(
                body,
                image="",
                text="",
                borderwidth=0,
                highlightthickness=1,
                highlightbackground="#B9B0A2",
                background="#FFFFFF",
            )
            shadow = tk.Frame(
                body,
                background="#A69E93",
                borderwidth=0,
                highlightthickness=0,
            )

            self._preview_turn_overlay = overlay
            self._preview_turn_shadow = shadow
            self._preview_animating = True

            if self._preview_previous_button is not None:
                self._preview_previous_button.configure(state="disabled")
            if self._preview_next_button is not None:
                self._preview_next_button.configure(state="disabled")

            # Plus lent et plus progressif que V2.
            widths = [
                1.00, 0.91, 0.80, 0.67, 0.53, 0.39, 0.26, 0.14, 0.06,
                0.14, 0.26, 0.39, 0.53, 0.67, 0.80, 0.91, 1.00,
            ]
            middle = 8
            delay = 24

            def finish() -> None:
                # La cible est construite derrière la feuille encore visible.
                # On ne retire l'overlay qu'après que Tk a réellement peint
                # la nouvelle double page : aucun passage par une zone vide.
                self._preview_index = target_index
                self._render_preview_current_spread()
                try:
                    body.update_idletasks()
                except Exception:
                    pass

                try:
                    overlay.destroy()
                except Exception:
                    pass
                try:
                    shadow.destroy()
                except Exception:
                    pass

                self._preview_turn_overlay = None
                self._preview_turn_shadow = None
                self._preview_animating = False

            def draw(frame_index: int) -> None:
                if frame_index >= len(widths):
                    finish()
                    return

                ratio = widths[frame_index]
                folded = 1.0 - ratio
                width = max(10, int(round(page_width * ratio)))
                height_loss = int(round(18 * folded))
                height = max(40, page_height - height_loss)

                use_back = frame_index > middle
                source = back if use_back else front

                page_image = source.resize(
                    (width, height),
                    Image.Resampling.LANCZOS,
                )

                # Assombrissement progressif vers la reliure.
                brightness = 1.0 - 0.22 * folded
                page_image = ImageEnhance.Brightness(
                    page_image
                ).enhance(brightness)

                photo = ImageTk.PhotoImage(page_image)
                self._preview_turn_photo = photo
                overlay.configure(image=photo)

                if direction > 0:
                    x = spine_x if frame_index <= middle else spine_x - width
                else:
                    x = spine_x - width if frame_index <= middle else spine_x

                y = top_y + max(0, (page_height - height) // 2)

                shadow_width = max(
                    2,
                    min(16, int(round(16 * folded))),
                )
                if direction > 0:
                    shadow_x = spine_x - shadow_width
                else:
                    shadow_x = spine_x

                shadow.place(
                    x=shadow_x,
                    y=top_y + 3,
                    width=shadow_width,
                    height=page_height - 6,
                )
                overlay.place(
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                )
                shadow.lift()
                overlay.lift()

                body.after(
                    delay,
                    lambda: draw(frame_index + 1),
                )

            draw(0)
        except Exception:
            self._preview_turn_overlay = None
            self._preview_turn_shadow = None
            self._preview_animating = False
            self._preview_index = target_index
            self._render_preview_current_spread()

    def _show_previous_spread(self) -> None:
        if (
            self._preview_mode != "large"
            or self._preview_index <= 0
            or bool(getattr(self, "_preview_animating", False))
        ):
            return
        self._animate_preview_turn(-1, self._preview_index - 1)

    def _show_next_spread(self) -> None:
        if (
            self._preview_mode != "large"
            or self._preview_index >= len(self._preview_spreads) - 1
            or bool(getattr(self, "_preview_animating", False))
        ):
            return
        self._animate_preview_turn(1, self._preview_index + 1)

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
    # Raccourcis clavier globaux
    # ==========================================================

    def _activate_global_shortcuts(self) -> None:
        """Raccorde le Maquettage au gestionnaire général de PageMaître."""
        if self._root is None:
            return

        manager = get_global_shortcut_manager(self.parent)
        self._shortcut_manager = manager
        if manager is None:
            return

        manager.activate(
            owner=self._root,
            undo=self._undo_from_global_shortcut,
            redo=self._redo_from_global_shortcut,
            select_all=self._select_all_from_global_shortcut,
            name="Maquettage",
        )

    def _deactivate_global_shortcuts(self) -> None:
        """Retire uniquement le contexte appartenant à cet écran."""
        manager = self._shortcut_manager
        root = self._root

        if manager is not None and root is not None:
            manager.deactivate(root)

        self._shortcut_manager = None

    def _on_root_destroyed(self, event) -> None:
        if getattr(event, "widget", None) is self._root:
            self._deactivate_global_shortcuts()

    def _undo_from_global_shortcut(self) -> bool:
        if not self._undo_stack:
            return False
        self._undo()
        return True

    def _redo_from_global_shortcut(self) -> bool:
        if not self._redo_stack:
            return False
        self._redo()
        return True

    def _select_all_from_global_shortcut(self) -> bool:
        movable_exists = any(
            str(item.get("id", ""))
            and not bool(item.get("automatic_recto_verso", False))
            and not self._is_locked_structural_type(
                str(item.get("type", ""))
            )
            for item in self._items()
        )
        if not movable_exists:
            return False

        self._select_all_movable_pages()
        return True

    # ==========================================================
    # Historique Annuler / Rétablir
    # ==========================================================

    def _record_history(self) -> None:
        """Mémorise l'état courant avant une modification utilisateur."""
        self._undo_stack.append(deepcopy(self.data))
        if len(self._undo_stack) > self._history_limit:
            del self._undo_stack[0]
        self._redo_stack.clear()
        self._update_history_buttons()

    @staticmethod
    def _ribbon_state_signature(
        data: dict[str, Any],
    ) -> str:
        """Détecte si l'historique exige réellement de reconstruire le ruban."""
        return json.dumps(
            {
                "groups": data.get("groups", []),
                "page_types": data.get("page_types", []),
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

    def _undo(self) -> None:
        if not self._undo_stack:
            return

        self._close_manage_dialog()
        self._close_recto_verso_dialog()
        self._close_preview()

        current_data = self.data
        restored_data = self._undo_stack.pop()
        ribbon_changed = (
            self._ribbon_state_signature(current_data)
            != self._ribbon_state_signature(restored_data)
        )

        self._redo_stack.append(deepcopy(current_data))
        self.data = restored_data
        self._selected_page_ids.clear()
        self._selection_anchor_id = None
        self._enforce_structural_order()
        self._save_data()

        if ribbon_changed:
            self._refresh_ribbon()
        self._refresh_sequence()
        self._update_history_buttons()

    def _redo(self) -> None:
        if not self._redo_stack:
            return

        self._close_manage_dialog()
        self._close_recto_verso_dialog()
        self._close_preview()

        current_data = self.data
        restored_data = self._redo_stack.pop()
        ribbon_changed = (
            self._ribbon_state_signature(current_data)
            != self._ribbon_state_signature(restored_data)
        )

        self._undo_stack.append(deepcopy(current_data))
        self.data = restored_data
        self._selected_page_ids.clear()
        self._selection_anchor_id = None
        self._enforce_structural_order()
        self._save_data()

        if ribbon_changed:
            self._refresh_ribbon()
        self._refresh_sequence()
        self._update_history_buttons()

    def _update_history_buttons(self) -> None:
        if self._undo_button is not None:
            try:
                self._undo_button.configure(
                    state="normal" if self._undo_stack else "disabled"
                )
            except Exception:
                pass

        if self._redo_button is not None:
            try:
                self._redo_button.configure(
                    state="normal" if self._redo_stack else "disabled"
                )
            except Exception:
                pass

    # ==========================================================
    # Actions utilisateur
    # ==========================================================

    def _add_item(self, definition: dict[str, Any]) -> None:
        page_type = str(definition.get("type", ""))
        if not page_type:
            return

        if bool(definition.get("single", False)) and any(
            str(item.get("type", "")) == page_type
            for item in self._items()
        ):
            return

        self._record_history()
        new_item = self._new_item_from_definition(definition)
        group_id = self._plan_group_id(new_item)

        # Les blancs automatiques sont recalculés ensuite : on travaille d'abord
        # sur la structure réelle du livre.
        base_items = [
            item
            for item in self._items()
            if not bool(item.get("automatic_recto_verso", False))
        ]
        insert_at = self._plan_group_insert_index(base_items, group_id)
        base_items.insert(insert_at, new_item)
        self._items()[:] = base_items

        self._enforce_structural_order()
        self._save_data()
        self._refresh_sequence()

    def _item_index(self, item_id: str) -> int | None:
        for index, item in enumerate(self._items()):
            if str(item.get("id", "")) == item_id:
                return index
        return None

    def _move_item_by_id(self, item_id: str, delta: int) -> None:
        index = self._item_index(item_id)
        if index is not None:
            self._move_item(index, delta)

    def _change_count_by_id(self, item_id: str, delta: int) -> None:
        index = self._item_index(item_id)
        if index is not None:
            self._change_count(index, delta)

    def _set_done_by_id(self, item_id: str, done: bool) -> None:
        index = self._item_index(item_id)
        if index is not None:
            self._set_done(index, done)

    def _remove_item_by_id(self, item_id: str) -> None:
        index = self._item_index(item_id)
        if index is not None:
            self._remove_item(index)

    def _move_item(self, index: int, delta: int) -> None:
        items = self._items()
        if not 0 <= index < len(items):
            return
        if not self._can_move_item(index, delta):
            return

        current = items[index]
        current_id = str(current.get("id", ""))
        current_group = self._plan_group_id(current)

        base_items = [
            item
            for item in items
            if not bool(item.get("automatic_recto_verso", False))
        ]
        base_index = next(
            (
                position
                for position, item in enumerate(base_items)
                if str(item.get("id", "")) == current_id
            ),
            None,
        )
        if base_index is None:
            return

        target_index = base_index + delta
        if not 0 <= target_index < len(base_items):
            return

        target = base_items[target_index]
        target_type = str(target.get("type", ""))
        target_group = self._plan_group_id(target)

        self._record_history()

        if target_group != current_group:
            # Franchir une frontière de groupe ne doit PAS sauter la première
            # ou la dernière page du groupe voisin :
            # - Descendre => la page devient la première du groupe suivant.
            # - Monter    => la page devient la dernière du groupe précédent.
            # L'ordre physique ne change donc pas ici ; seule l'appartenance
            # au groupe change.
            current["plan_group"] = target_group
        elif self._is_locked_structural_type(target_type):
            # Même groupe mais borne structurelle verrouillée : pas d'échange.
            return
        else:
            # À l'intérieur d'un même groupe, Monter/Descendre reste un échange
            # classique avec la page voisine.
            base_items[base_index], base_items[target_index] = (
                base_items[target_index],
                base_items[base_index],
            )

        self._items()[:] = base_items
        self._enforce_structural_order()
        self._save_data()
        self._refresh_sequence()

    def _change_count(self, index: int, delta: int) -> None:
        items = self._items()
        if not 0 <= index < len(items):
            return

        if bool(items[index].get("automatic_recto_verso", False)):
            return
        definition = self._definition_for(items[index].get("type", "autre"))
        if definition.get("single"):
            return

        current = max(1, int(items[index].get("count", 1)))
        new_count = max(1, min(9999, current + delta))
        if new_count == current:
            return

        self._record_history()
        items[index]["count"] = new_count
        # Le nombre de blancs automatiques liés doit suivre immédiatement le
        # nombre d’occurrences de la page concernée.
        self._enforce_structural_order()
        self._save_data()
        self._refresh_sequence()

    def _set_done(self, index: int, done: bool) -> None:
        items = self._items()
        if not 0 <= index < len(items):
            return

        new_value = bool(done)
        if bool(items[index].get("done", False)) == new_value:
            return

        self._record_history()
        items[index]["done"] = new_value
        self._save_data()
        self._refresh_sequence()

    def _remove_item(self, index: int) -> None:
        items = self._items()
        if not 0 <= index < len(items):
            return

        if bool(items[index].get("automatic_recto_verso", False)):
            return
        definition = self._definition_for(str(items[index].get("type", "")))
        if bool(definition.get("required", False)):
            return

        removed_id = str(items[index].get("id", ""))
        self._record_history()
        del items[index]
        self._selected_page_ids.discard(removed_id)
        if self._selection_anchor_id == removed_id:
            self._selection_anchor_id = None
        self._enforce_structural_order()
        self._save_data()
        self._refresh_sequence()

    def _go_back(self) -> None:
        self._close_manage_dialog()
        self._close_recto_verso_dialog()
        self._close_preview()
        self._deactivate_global_shortcuts()
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

    def _groups(self) -> list[dict[str, Any]]:
        groups = self.data.setdefault("groups", [])
        if not isinstance(groups, list):
            groups = []
            self.data["groups"] = groups
        return groups

    def _page_types(self) -> list[dict[str, Any]]:
        definitions = self.data.setdefault("page_types", [])
        if not isinstance(definitions, list):
            definitions = []
            self.data["page_types"] = definitions
        return definitions

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

        groups = self._normalize_groups(data.get("groups"))
        page_types = self._normalize_page_types(data.get("page_types"), groups)

        self.data = data
        self.data["groups"] = groups
        self.data["page_types"] = page_types
        self.data["recto_verso_rules"] = self._normalize_recto_verso_rules(
            data.get("recto_verso_rules")
        )

        items = data.get("items", [])
        if not isinstance(items, list):
            items = []

        data["version"] = 6
        data["groups"] = groups
        data["page_types"] = page_types
        data["items"] = [
            self._normalize_item(item)
            for item in items
            if isinstance(item, dict)
        ]
        self._enforce_structural_order()
        data.setdefault("created_at", datetime.now().isoformat())
        data.setdefault("updated_at", datetime.now().isoformat())

        self._write_json(path, data)
        return data

    def _save_data(self) -> None:
        self.data["version"] = 6
        self.data["updated_at"] = datetime.now().isoformat()
        self._run_silent_structure_check()
        self._write_json(self._mockup_file(), self.data)

    def _mockup_file(self) -> Path:
        configured = getattr(self.project, "mockup_file", None)
        if configured is not None:
            return Path(configured)

        root = getattr(self.project, "root", None)
        if root is None:
            raise RuntimeError("Aucun projet n’est chargé.")

        return Path(root) / "maquettage" / "premaquette.json"

    @classmethod
    def _empty_data(cls) -> dict[str, Any]:
        now = datetime.now().isoformat()
        definitions = {
            str(definition["type"]): definition
            for definition in cls.PAGE_LIBRARY
        }

        required_items: list[dict[str, Any]] = []
        for page_type in ("couverture", "quatrieme"):
            definition = definitions[page_type]
            required_items.append(
                {
                    "id": f"MAQUETTE-{uuid4().hex[:12].upper()}",
                    "type": page_type,
                    "title": str(definition["title"]),
                    "count": 1,
                    "done": False,
                }
            )

        return {
            "version": 6,
            "created_at": now,
            "updated_at": now,
            "groups": [dict(group) for group in cls.DEFAULT_GROUPS],
            "page_types": [dict(definition) for definition in cls.PAGE_LIBRARY],
            "recto_verso_rules": [],
            "items": required_items,
        }

    @classmethod
    def _normalize_groups(cls, raw_groups) -> list[dict[str, Any]]:
        defaults = {
            str(group["id"]): dict(group)
            for group in cls.DEFAULT_GROUPS
        }
        middle: list[dict[str, Any]] = []
        known_ids: set[str] = {"debut_livre", "fin_livre"}
        pages_interieures_seen = False

        if isinstance(raw_groups, list):
            for raw in raw_groups:
                if not isinstance(raw, dict):
                    continue

                group_id = str(raw.get("id", "")).strip()
                title = str(raw.get("title", "")).strip()
                if not group_id or not title:
                    continue

                if group_id in {"debut_livre", "fin_livre"}:
                    continue

                if group_id == "pages_interieures":
                    if not pages_interieures_seen:
                        middle.append(dict(defaults["pages_interieures"]))
                        pages_interieures_seen = True
                    continue

                if group_id in known_ids:
                    continue

                middle.append(
                    {
                        "id": group_id,
                        "title": title,
                        "symbol": str(raw.get("symbol") or "▦"),
                        "accent": str(raw.get("accent") or cls.SKY),
                        "protected": False,
                        "deleted": bool(raw.get("deleted", False)),
                        "deleted_kind": str(raw.get("deleted_kind") or ""),
                        "deleted_label": str(raw.get("deleted_label") or ""),
                        "deleted_original_index": raw.get("deleted_original_index"),
                        "deleted_original_title": str(
                            raw.get("deleted_original_title") or ""
                        ),
                    }
                )
                known_ids.add(group_id)

        if not pages_interieures_seen:
            # Ancien projet sans ordre personnalisé : le groupe standard
            # conserve sa position habituelle au début de la zone centrale.
            middle.insert(0, dict(defaults["pages_interieures"]))

        return [
            dict(defaults["debut_livre"]),
            *middle,
            dict(defaults["fin_livre"]),
        ]

    @classmethod
    def _normalize_page_types(
        cls,
        raw_definitions,
        groups: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        definitions = [dict(definition) for definition in cls.PAGE_LIBRARY]
        known_types = {str(definition["type"]) for definition in definitions}
        group_ids = {str(group["id"]) for group in groups}

        if isinstance(raw_definitions, list):
            for raw in raw_definitions:
                if not isinstance(raw, dict):
                    continue
                page_type = str(raw.get("type", "")).strip()
                title = str(raw.get("title", "")).strip()
                group_id = str(raw.get("group", "")).strip()
                if (
                    not page_type
                    or not title
                    or page_type in known_types
                    or group_id not in group_ids
                ):
                    continue

                definitions.append(
                    {
                        "type": page_type,
                        "title": title,
                        "short": str(raw.get("short") or title)[:18],
                        "symbol": str(raw.get("symbol") or "▦"),
                        "color": str(raw.get("color") or "#EEF0F2"),
                        "accent": str(raw.get("accent") or cls.INK),
                        "group": group_id,
                        "single": bool(raw.get("single", False)),
                        "description": str(raw.get("description") or ""),
                        "thumbnail": str(raw.get("thumbnail") or ""),
                        "custom": True,
                        "deleted": bool(raw.get("deleted", False)),
                        "deleted_kind": str(raw.get("deleted_kind") or ""),
                        "deleted_label": str(raw.get("deleted_label") or ""),
                        "deleted_original_index": raw.get("deleted_original_index"),
                        "deleted_original_group": str(
                            raw.get("deleted_original_group") or group_id
                        ),
                        "deleted_original_title": str(
                            raw.get("deleted_original_title") or title
                        ),
                    }
                )
                known_types.add(page_type)

        return definitions

    def _normalize_item(self, item: dict[str, Any]) -> dict[str, Any]:
        page_type = str(item.get("type", "inconnu"))
        definition = self._definition_for(page_type)
        count = item.get("count", 1)

        try:
            normalized_count = max(1, int(count))
        except (TypeError, ValueError):
            normalized_count = 1

        if definition.get("single"):
            normalized_count = 1

        valid_groups = {
            str(group.get("id", ""))
            for group in self._groups()
            if str(group.get("id", ""))
        }
        default_group = str(definition.get("group", "pages_interieures"))
        stored_group = str(item.get("plan_group", ""))
        plan_group = stored_group if stored_group in valid_groups else default_group

        normalized = {
            "id": str(item.get("id") or f"MAQUETTE-{uuid4().hex[:12].upper()}"),
            "type": page_type,
            "title": str(item.get("title") or definition["title"]),
            "count": normalized_count,
            "done": bool(item.get("done", False)),
            "plan_group": plan_group,
        }

        done_source = str(item.get("done_source", ""))
        if done_source:
            normalized["done_source"] = done_source

        for key in ("done_count", "validated_count", "completed_count"):
            if key in item:
                try:
                    normalized[key] = max(0, int(item.get(key, 0)))
                except (TypeError, ValueError):
                    normalized[key] = 0

        if bool(item.get("automatic_recto_verso", False)):
            normalized["automatic_recto_verso"] = True
            normalized["recto_target_id"] = str(item.get("recto_target_id", ""))
            normalized["recto_position"] = str(item.get("recto_position", "before"))
            if bool(item.get("recto_shared", False)):
                normalized["recto_shared"] = True
        return normalized

    @staticmethod
    def _write_json(path: Path, data: dict[str, Any]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_suffix(".tmp")

        with temporary.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

        temporary.replace(path)

    # ==========================================================
    # Contrôle automatique de la structure
    # ==========================================================

    def _structure_issues(self) -> list[dict[str, str]]:
        """Retourne les incohérences détectées sans modifier le projet."""
        issues: list[dict[str, str]] = []
        items = list(self._items())
        page_types = {
            str(definition.get("type", ""))
            for definition in self._page_types()
            if str(definition.get("type", ""))
        }
        groups = {
            str(group.get("id", ""))
            for group in self._groups()
            if str(group.get("id", ""))
        }

        def add(level: str, title: str, detail: str) -> None:
            issues.append(
                {
                    "level": level,
                    "title": title,
                    "detail": detail,
                }
            )

        item_types = [str(item.get("type", "")) for item in items]

        for required_type, label in (
            ("couverture", "Couverture"),
            ("quatrieme", "Quatrième de couverture"),
        ):
            count = item_types.count(required_type)
            if count == 0:
                add(
                    "error",
                    f"{label} absente",
                    "Cette page obligatoire doit toujours être présente.",
                )
            elif count > 1:
                add(
                    "error",
                    f"{label} présente plusieurs fois",
                    "Une seule occurrence est autorisée.",
                )

        if items and item_types[0] != "couverture":
            add(
                "error",
                "La couverture n’est pas en première position",
                "Elle doit rester la première page du projet.",
            )

        if items and item_types[-1] != "quatrieme":
            add(
                "error",
                "La quatrième n’est pas en dernière position",
                "Elle doit rester la dernière page du projet.",
            )

        if item_types.count("deuxieme_couverture") > 1:
            add(
                "error",
                "Deuxième de couverture dupliquée",
                "Cette page facultative ne peut apparaître qu’une seule fois.",
            )
        elif "deuxieme_couverture" in item_types:
            second_index = item_types.index("deuxieme_couverture")
            if second_index != 1:
                add(
                    "error",
                    "Deuxième de couverture mal placée",
                    "Elle doit être immédiatement après la couverture.",
                )

        if item_types.count("troisieme_couverture") > 1:
            add(
                "error",
                "Troisième de couverture dupliquée",
                "Cette page facultative ne peut apparaître qu’une seule fois.",
            )
        elif "troisieme_couverture" in item_types:
            third_index = item_types.index("troisieme_couverture")
            fourth_index = (
                item_types.index("quatrieme")
                if "quatrieme" in item_types
                else len(item_types)
            )
            if third_index != fourth_index - 1:
                add(
                    "error",
                    "Troisième de couverture mal placée",
                    "Elle doit être immédiatement avant la quatrième.",
                )

        for definition in self._page_types():
            page_type = str(definition.get("type", ""))
            if not page_type or not bool(definition.get("single", False)):
                continue
            count = item_types.count(page_type)
            if count > 1:
                add(
                    "error",
                    f"« {definition.get('title', page_type)} » est dupliquée",
                    "Ce type de page est limité à un seul exemplaire.",
                )

        unknown_types = sorted(
            {
                page_type
                for page_type in item_types
                if page_type and page_type not in page_types
            }
        )
        for page_type in unknown_types:
            add(
                "error",
                "Type de page inconnu",
                f"Le type « {page_type} » n’existe plus dans la palette.",
            )

        seen_ids: set[str] = set()
        for item in items:
            item_id = str(item.get("id", ""))
            if not item_id:
                add(
                    "warning",
                    "Page sans identifiant",
                    "Cette page devra recevoir un identifiant interne.",
                )
                continue
            if item_id in seen_ids:
                add(
                    "error",
                    "Identifiant de page dupliqué",
                    f"L’identifiant interne « {item_id} » est utilisé plusieurs fois.",
                )
            seen_ids.add(item_id)

        for previous, current in zip(items, items[1:]):
            if (
                bool(previous.get("automatic_recto_verso", False))
                and bool(current.get("automatic_recto_verso", False))
            ):
                add(
                    "error",
                    "Deux blancs automatiques consécutifs",
                    "Ils doivent être fusionnés en une seule page blanche automatique.",
                )
                break

        for definition in self._page_types():
            page_type = str(definition.get("type", ""))
            group_id = str(definition.get("group", ""))
            if page_type and group_id not in groups:
                add(
                    "warning",
                    f"Groupe introuvable pour « {definition.get('title', page_type)} »",
                    "Ce type de page doit être rattaché à un groupe existant.",
                )

        valid_rule_types = page_types - {
            "couverture",
            "deuxieme_couverture",
            "troisieme_couverture",
            "page_blanche",
        }
        for rule in self._recto_verso_rules():
            position = str(rule.get("position", "before"))
            for page_type in rule.get("page_types", []):
                page_type = str(page_type)
                if page_type not in valid_rule_types:
                    add(
                        "warning",
                        "Règle recto-verso devenue invalide",
                        f"Le type « {page_type} » n’est plus disponible pour cette règle.",
                    )
                elif (
                    page_type == "deuxieme_couverture"
                    and position == "before"
                ):
                    add(
                        "error",
                        "Règle impossible avant la deuxième",
                        "La deuxième de couverture accepte uniquement un blanc après.",
                    )
                elif (
                    page_type == "troisieme_couverture"
                    and position == "after"
                ):
                    add(
                        "error",
                        "Règle impossible après la troisième",
                        "La troisième de couverture accepte uniquement un blanc avant.",
                    )
                elif page_type == "quatrieme" and position == "after":
                    add(
                        "error",
                        "Règle impossible après la quatrième",
                        "La quatrième étant la dernière page, seul un blanc avant est autorisé.",
                    )

        return issues

    def _clear_legacy_manual_done_flags(self) -> None:
        """Supprime les anciens « Fait » cochés manuellement.

        À l'avenir, seul le Bureau de conception pourra fournir un état
        marqué done_source='conception'.
        """
        changed = False
        for item in self._items():
            if str(item.get("done_source", "")).casefold() == "conception":
                continue
            if bool(item.get("done", False)):
                item["done"] = False
                changed = True

        if changed:
            self.data["updated_at"] = datetime.now().isoformat()
            self._write_json(self._mockup_file(), self.data)

    def _run_silent_structure_check(self) -> list[dict[str, str]]:
        """Mémorise les anomalies techniques sans ajouter de bouton à l’écran."""
        self._last_structure_issues = self._structure_issues()
        return list(self._last_structure_issues)

    # ==========================================================
    # Résumé et utilitaires
    # ==========================================================

    def _update_summary(self) -> None:
        items = self._items()
        total_pages = sum(max(1, int(item.get("count", 1))) for item in items)
        automatic_pages = sum(
            max(1, int(item.get("count", 1)))
            for item in items
            if bool(item.get("automatic_recto_verso", False))
        )
        work_items = [
            item
            for item in items
            if not bool(item.get("automatic_recto_verso", False))
        ]
        work_total = sum(
            max(1, int(item.get("count", 1)))
            for item in work_items
        )
        done_pages = sum(
            self._sequence_progress_counts(item)[0]
            for item in work_items
        )
        distinct_types = len({str(item.get("type", "autre")) for item in items})

        auto_text = f" · {automatic_pages} auto" if automatic_pages else ""
        summary_text = (
            f"{total_pages} p.{auto_text} · "
            f"{distinct_types} type{'s' if distinct_types != 1 else ''}"
        )
        progress_text = (
            f"Fait : {done_pages}/{work_total}" if work_total else ""
        )

        if (
            self._summary_label is not None
            and self._summary_text_cache != summary_text
        ):
            self._summary_label.configure(text=summary_text)
            self._summary_text_cache = summary_text

        if (
            self._progress_label is not None
            and self._progress_text_cache != progress_text
        ):
            self._progress_label.configure(text=progress_text)
            self._progress_text_cache = progress_text

    def _definition_for(self, page_type: str) -> dict[str, Any]:
        for definition in self._page_types():
            if str(definition.get("type")) == page_type:
                return definition
        return dict(self.UNKNOWN_PAGE)

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