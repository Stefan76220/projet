from __future__ import annotations

import importlib.util
import json
import shutil
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Callable

from PIL import Image, ImageEnhance, ImageFilter, ImageTk

from src.gui_v3 import theme
from src.gui_v3.book_canvas import BookCanvas
from src.gui_v3.focus_toolbar import FocusToolbar
from src.gui_v3.hover import GlobalHoverManager


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _load_project_class():
    """Charge Project sans exécuter le __init__ historique de src.core."""
    path = PROJECT_ROOT / "src" / "core" / "project.py"
    spec = importlib.util.spec_from_file_location("tomelinea_v3_project_core", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Impossible de charger {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Project


Project = _load_project_class()


class ProjectManager:
    """Gestionnaire V3 léger, isolé des imports GUI de la V1."""

    def __init__(self):
        self.current_project = None

    def new_project(self, folder: str, name: str, project_type: str):
        project = Project()
        project.create(folder, name, project_type=project_type)
        self.current_project = project
        return project

    def open_project(self, folder: str):
        project = Project()
        project.load(folder)
        self.current_project = project
        return project

BACKGROUND_PATH = (
    PROJECT_ROOT / "assets" / "interface" / "backgrounds" / "editorial_bg_accueil.png"
)
BRAND_ROOT = (
    PROJECT_ROOT
    / "assets"
    / "branding"
    / "tomelinea"
    / "Tomelinea_logo_pack"
)
BRAND_ICON = BRAND_ROOT / "04_windows" / "Tomelinea.ico"
BRAND_ICON_PNG = BRAND_ROOT / "04_windows" / "Tomelinea_Windows_64x64.png"
BRAND_LOGO = BRAND_ROOT / "01_logo_complet" / "Tomelinea_logo_complet_600px.png"
RECENT_FILE = PROJECT_ROOT / "cache" / "tomelinea_v3_recent.json"

TYPE_ICON_DIR = PROJECT_ROOT / "assets" / "gui_v2" / "accueil_realistic_icons"
TYPE_ICONS = {
    "ouvrage_structure": TYPE_ICON_DIR / "ouvrage_structure.png",
    "livre_textuel": TYPE_ICON_DIR / "livre_textuel.png",
    "bande_dessinee": TYPE_ICON_DIR / "bande_dessinee.png",
}


@dataclass
class WorkspaceContext:
    project: Project | None
    name: str
    project_type: str

    @property
    def type_label(self) -> str:
        return theme.PROJECT_TYPES.get(self.project_type, "Projet TomeLinea")


class CutPanel(tk.Canvas):
    """Panneau TomeLinea V3 : sobre, sans spirale, coins coupés discrets."""

    def __init__(
        self,
        parent,
        *,
        fill: str = theme.PANEL,
        border: str = theme.BORDER,
        cut: int = 16,
        padding: tuple[int, int] = (18, 14),
        **kwargs,
    ):
        super().__init__(
            parent,
            bg=theme.WINDOW_DEEP,
            bd=0,
            highlightthickness=0,
            **kwargs,
        )
        self._fill = fill
        self._border = border
        self._cut = cut
        self._pad_x, self._pad_y = padding
        self.body = tk.Frame(self, bg=fill)
        self._body_id = self.create_window(
            self._pad_x,
            self._pad_y,
            anchor="nw",
            window=self.body,
        )
        self.bind("<Configure>", self._redraw, add="+")

    def _redraw(self, _event=None):
        w = max(20, self.winfo_width())
        h = max(20, self.winfo_height())
        c = min(self._cut, max(4, w // 8), max(4, h // 8))
        pts = [
            1, 1,
            w - c, 1,
            w - 1, c,
            w - 1, h - c,
            w - c, h - 1,
            c, h - 1,
            1, h - c,
            1, c,
        ]
        self.delete("panel_shape")
        self.create_polygon(
            pts,
            fill=self._fill,
            outline=self._border,
            width=1,
            tags=("panel_shape",),
        )
        self.tag_lower("panel_shape")
        inner_w = max(1, w - self._pad_x * 2)
        inner_h = max(1, h - self._pad_y * 2)
        self.coords(self._body_id, self._pad_x, self._pad_y)
        self.itemconfigure(self._body_id, width=inner_w, height=inner_h)


class V3Button(tk.Button):
    def __init__(self, parent, text: str, command=None, *, primary=False, compact=False, state="normal"):
        bg = theme.ACCENT_DARK if primary else theme.PANEL_SOFT
        fg = theme.WHITE if primary else theme.INK
        active_bg = theme.ACCENT if primary else theme.ACCENT_SOFT
        active_fg = theme.WINDOW_DEEP if primary else theme.WHITE
        super().__init__(
            parent,
            text=text,
            command=command,
            state=state,
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=active_fg,
            disabledforeground=theme.MUTED_DARK,
            relief="flat",
            bd=0,
            padx=10 if compact else 15,
            pady=5 if compact else 8,
            font=(theme.FONT_UI, 8 if compact else 9, "bold"),
            cursor="hand2" if state != "disabled" else "arrow",
        )
        self.bind("<Enter>", self._enter)
        self.bind("<Leave>", self._leave)
        self._base_bg = bg
        self._hover_bg = active_bg

    def _enter(self, _event=None):
        if str(self.cget("state")) != "disabled":
            self.configure(bg=self._hover_bg)

    def _leave(self, _event=None):
        self.configure(bg=self._base_bg)


class TomeLineaV3(tk.Tk):
    # SURVOL_GLOBAL_INTERACTIF_V3_V1
    # ACCUEIL_MAQUETTE_VALIDEE_V3_V2
    # ACCUEIL_V3_ERGONOMIQUE_V1
    # BARRE_OUTILS_FLOTTANTE_PAGE_V3_V6
    # ZOOM_PAGE_PLEIN_ESPACE_V3_V4
    # CANEVA_LIVRE_UNIQUE_V3_V2
    """TomeLinea V3 — espace projet continu A/B/C."""

    # DEMARRAGE_ATOMIQUE_V3_WINDOWS_V2
    def __init__(self) -> None:
        super().__init__()

        # Sous Windows, on construit toute la V3 hors écran.
        # On n'affiche la fenêtre qu'une fois Accueil + espace A/B/C prêts.
        self.withdraw()

        self.title("TomeLinea — V3")
        self.configure(bg=theme.WINDOW_DEEP)
        self.minsize(1180, 720)

        self._brand_icon = None
        try:
            if BRAND_ICON.exists():
                self.iconbitmap(str(BRAND_ICON))
        except Exception:
            pass
        try:
            if BRAND_ICON_PNG.exists():
                image = Image.open(BRAND_ICON_PNG).convert("RGBA")
                self._brand_icon = ImageTk.PhotoImage(image)
                self.iconphoto(True, self._brand_icon)
        except Exception:
            self._brand_icon = None

        self.project_manager = ProjectManager()
        self.context: WorkspaceContext | None = None
        self.active_tab = "structure"
        self._bg_source = None
        self._bg_cache: dict[tuple[int, int, str], ImageTk.PhotoImage] = {}
        self._logo_cache: dict[int, ImageTk.PhotoImage] = {}
        self._type_icon_cache: dict[tuple[str, int], ImageTk.PhotoImage] = {}
        self._screens: dict[str, tk.Frame] = {}
        # Règle V3 globale : toute zone cliquable réagit au survol.
        self.hover_manager = GlobalHoverManager(self)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.stack = tk.Frame(self, bg=theme.WINDOW_DEEP)
        self.stack.grid(row=0, column=0, sticky="nsew")
        self.stack.grid_rowconfigure(0, weight=1)
        self.stack.grid_columnconfigure(0, weight=1)

        # Construction unique de l'Accueil et de l'espace permanent A/B/C.
        self._build_home()
        self._build_workspace()
        self.show_home()

        # Première passe de géométrie pendant que la fenêtre est cachée.
        self.update_idletasks()

        # Affichage seulement quand la structure existe déjà.
        self.deiconify()
        try:
            self.state("zoomed")
        except tk.TclError:
            sw = max(1180, self.winfo_screenwidth())
            sh = max(720, self.winfo_screenheight())
            self.geometry(f"{sw}x{sh}+0+0")

        # Force le premier vrai calcul Windows : taille, Configure et fond.
        self.update_idletasks()
        self.update()

        # L'Accueil est remis explicitement au premier plan après le calcul.
        self._screens["home"].tkraise()
        self.update_idletasks()

        self.lift()
        self.after_idle(self.lift)

    def _load_bg_source(self):
        if self._bg_source is None and BACKGROUND_PATH.exists():
            image = Image.open(BACKGROUND_PATH).convert("RGB")
            image = ImageEnhance.Color(image).enhance(0.82)
            image = ImageEnhance.Brightness(image).enhance(0.90)
            self._bg_source = image
        return self._bg_source

    def _background_photo(self, width: int, height: int, key: str):
        width = max(400, int(width))
        height = max(300, int(height))
        cache_key = (width, height, key)
        if cache_key in self._bg_cache:
            return self._bg_cache[cache_key]
        source = self._load_bg_source()
        if source is None:
            return None
        src_w, src_h = source.size
        scale = max(width / src_w, height / src_h)
        new_w = max(width, int(src_w * scale))
        new_h = max(height, int(src_h * scale))
        image = source.resize((new_w, new_h), Image.Resampling.LANCZOS)
        left = max(0, (new_w - width) // 2)
        top = max(0, (new_h - height) // 2)
        image = image.crop((left, top, left + width, top + height))
        photo = ImageTk.PhotoImage(image)
        if len(self._bg_cache) > 8:
            self._bg_cache.clear()
        self._bg_cache[cache_key] = photo
        return photo

    def _logo_photo(self, width: int):
        if width in self._logo_cache:
            return self._logo_cache[width]
        if not BRAND_LOGO.exists():
            return None
        image = Image.open(BRAND_LOGO).convert("RGBA")
        ratio = width / image.width
        image = image.resize((width, max(1, int(image.height * ratio))), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self._logo_cache[width] = photo
        return photo

    def _type_icon(self, key: str, size: int):
        cache_key = ("home_exact", key, size)
        if cache_key in self._type_icon_cache:
            return self._type_icon_cache[cache_key]
        path = PROJECT_ROOT / "assets" / "gui_v3" / "home" / f"{key}.png"
        if not path.exists():
            path = TYPE_ICONS.get(key)
        if path is None or not path.exists():
            return None
        image = Image.open(path).convert("RGBA")
        image.thumbnail((size, size), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self._type_icon_cache[cache_key] = photo
        return photo

    def _home_type_icon_glow(self, key: str, size: int, selected: bool = False):
        """Icônes exactes de la maquette avec halo TomeLinea."""
        if not hasattr(self, "_home_glow_icon_cache"):
            self._home_glow_icon_cache = {}
        cache_key = (key, int(size), bool(selected))
        cached = self._home_glow_icon_cache.get(cache_key)
        if cached is not None:
            return cached

        path = PROJECT_ROOT / "assets" / "gui_v3" / "home" / f"{key}.png"
        if not path.exists():
            return self._type_icon(key, size)

        palette = {
            "ouvrage_structure": (121, 180, 156),
            "livre_textuel": (163, 122, 212),
            "bande_dessinee": (211, 123, 85),
        }
        color = palette.get(key, (127, 184, 174))
        icon = Image.open(path).convert("RGBA")
        icon.thumbnail((int(size * 0.74), int(size * 0.74)), Image.Resampling.LANCZOS)
        alpha = icon.getchannel("A")
        result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        x = (size - icon.width) // 2
        y = (size - icon.height) // 2

        # Halo de base, visible mais discret.
        soft_alpha = alpha.filter(ImageFilter.GaussianBlur(11))
        soft_alpha = soft_alpha.point(lambda v: int(v * 0.55))
        soft = Image.new("RGBA", icon.size, color + (0,))
        soft.putalpha(soft_alpha)
        result.alpha_composite(soft, (x, y))

        if selected:
            # L'effet sélection simule une lumière qui s'allume derrière le livre.
            strong_alpha = alpha.filter(ImageFilter.GaussianBlur(20))
            strong_alpha = strong_alpha.point(lambda v: int(v * 0.90))
            strong = Image.new("RGBA", icon.size, color + (0,))
            strong.putalpha(strong_alpha)
            result.alpha_composite(strong, (x, y))

            bloom_alpha = alpha.filter(ImageFilter.GaussianBlur(31))
            bloom_alpha = bloom_alpha.point(lambda v: int(v * 0.42))
            bloom = Image.new("RGBA", icon.size, color + (0,))
            bloom.putalpha(bloom_alpha)
            result.alpha_composite(bloom, (x, y))

        result.alpha_composite(icon, (x, y))
        photo = ImageTk.PhotoImage(result)
        self._home_glow_icon_cache[cache_key] = photo
        return photo

    def _screen_with_background(self, key: str):
        screen = tk.Frame(self.stack, bg=theme.WINDOW_DEEP)
        screen.grid(row=0, column=0, sticky="nsew")
        bg = tk.Label(screen, bg=theme.WINDOW_DEEP, bd=0)
        bg.place(x=0, y=0, relwidth=1, relheight=1)
        screen._bg_label = bg

        def refresh(event):
            photo = self._background_photo(event.width, event.height, key)
            if photo is not None:
                bg.configure(image=photo)
                bg.image = photo

        screen.bind("<Configure>", refresh, add="+")
        self._screens[key] = screen
        return screen

    # ------------------------------------------------------------------
    # Accueil V3
    # ------------------------------------------------------------------

    def _build_home(self):
        screen = self._screen_with_background("home")

        panel = "#252C35"
        panel_alt = "#2B323C"
        border = "#49545E"
        green = "#79B49C"
        purple = "#A37AD4"
        orange = "#D37B55"

        # -----------------------------------------------------------------
        # Identité : mêmes proportions générales que la maquette validée.
        # -----------------------------------------------------------------
        header = tk.Frame(screen, bg=theme.WINDOW_DEEP)
        header.place(relx=0.105, rely=0.055, relwidth=0.78, relheight=0.11)

        tk.Label(
            header,
            text="TL",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(theme.FONT_TITLE, 38, "bold"),
        ).place(relx=0.00, rely=0.00)
        tk.Label(
            header,
            text="TomeLinea",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(theme.FONT_TITLE, 34),
        ).place(relx=0.085, rely=0.00)
        tk.Label(
            header,
            text="V3",
            bg=theme.WINDOW_DEEP,
            fg=green,
            font=(theme.FONT_UI, 12, "bold"),
        ).place(relx=0.385, rely=0.12)
        tk.Label(
            header,
            text="LA LIGNE ÉDITORIALE JUSQU’AU LIVRE",
            bg=theme.WINDOW_DEEP,
            fg=green,
            font=(theme.FONT_UI, 9, "bold"),
        ).place(relx=0.085, rely=0.67)

        tools = tk.Frame(header, bg=theme.WINDOW_DEEP)
        tools.place(relx=0.68, rely=0.12, relwidth=0.32, relheight=0.55)
        tk.Label(
            tools, text="?  Aide", bg=theme.WINDOW_DEEP, fg=theme.INK,
            font=(theme.FONT_UI, 9),
        ).pack(side="left", padx=(0, 20))
        tk.Label(
            tools, text="⚙  Préférences", bg=theme.WINDOW_DEEP, fg=theme.INK,
            font=(theme.FONT_UI, 9),
        ).pack(side="left", padx=(0, 20))
        tk.Label(
            tools, text="TL", bg=theme.ACCENT_DARK, fg=theme.WHITE,
            font=(theme.FONT_UI, 8, "bold"), padx=8, pady=5,
        ).pack(side="left", padx=(0, 7))
        tk.Label(
            tools, text="Profil  ▾", bg=theme.WINDOW_DEEP, fg=theme.INK,
            font=(theme.FONT_UI, 9),
        ).pack(side="left")

        # -----------------------------------------------------------------
        # MES PROJETS — colonne gauche.
        # -----------------------------------------------------------------
        left = tk.Frame(screen, bg=panel, highlightthickness=1, highlightbackground=border)
        left.place(relx=0.105, rely=0.205, relwidth=0.345, relheight=0.61)
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(2, weight=1)

        left_head = tk.Frame(left, bg=panel)
        left_head.grid(row=0, column=0, sticky="ew", padx=28, pady=(18, 6))
        left_head.grid_columnconfigure(1, weight=1)
        left_title = tk.Frame(left_head, bg=panel)
        left_title.grid(row=0, column=0, sticky="w")
        books_icon = tk.Canvas(left_title, width=24, height=24, bg=panel, bd=0, highlightthickness=0)
        books_icon.pack(side="left", padx=(0, 8))
        books_icon.create_rectangle(3, 8, 7, 21, outline=theme.MUTED, width=1)
        books_icon.create_rectangle(9, 5, 14, 21, outline=theme.MUTED, width=1)
        books_icon.create_rectangle(16, 9, 21, 21, outline=theme.MUTED, width=1)
        tk.Label(
            left_title, text="MES PROJETS", bg=panel, fg=theme.INK,
            font=(theme.FONT_UI, 11),
        ).pack(side="left")
        all_projects = tk.Label(
            left_head, text="Tous mes projets  ›", bg=panel, fg=theme.MUTED,
            font=(theme.FONT_UI, 8), cursor="hand2",
        )
        all_projects.grid(row=0, column=2, sticky="e")
        all_projects.bind("<Button-1>", lambda _e: self.open_existing_project())

        tk.Label(
            left, text="Récents", bg=panel, fg=theme.INK,
            font=(theme.FONT_UI, 8, "bold"),
        ).grid(row=1, column=0, sticky="w", padx=28, pady=(0, 8))

        self.home_recent_list = tk.Frame(left, bg=panel)
        self.home_recent_list.grid(row=2, column=0, sticky="nsew", padx=28)
        self.home_recent_list.grid_columnconfigure(0, weight=1)

        open_left = tk.Frame(
            left, bg=panel_alt, highlightthickness=1,
            highlightbackground=border, cursor="hand2",
        )
        open_left.grid(row=3, column=0, sticky="ew", padx=28, pady=(8, 22), ipady=9)
        open_left.grid_columnconfigure(1, weight=1)
        open_left_icon = tk.Label(open_left, text="▱", bg=panel_alt, fg=theme.MUTED, font=(theme.FONT_UI, 16))
        open_left_icon.grid(row=0, column=0, padx=(14, 10))
        open_left_text = tk.Label(
            open_left, text="Ouvrir un projet existant", bg=panel_alt,
            fg=theme.INK, font=(theme.FONT_UI, 9), anchor="w",
        )
        open_left_text.grid(row=0, column=1, sticky="ew")
        open_left_arrow = tk.Label(open_left, text="›", bg=panel_alt, fg=theme.MUTED, font=(theme.FONT_UI, 17))
        open_left_arrow.grid(row=0, column=2, padx=(8, 13))
        for widget in (open_left, open_left_icon, open_left_text, open_left_arrow):
            widget.bind("<Button-1>", lambda _e: self.open_existing_project())

        # -----------------------------------------------------------------
        # DÉMARRER — colonne droite.
        # -----------------------------------------------------------------
        right = tk.Frame(screen, bg=panel, highlightthickness=1, highlightbackground=border)
        right.place(relx=0.465, rely=0.205, relwidth=0.395, relheight=0.61)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(3, weight=1)

        right_head = tk.Frame(right, bg=panel)
        right_head.grid(row=0, column=0, sticky="ew", padx=30, pady=(16, 6))
        right_head.grid_columnconfigure(1, weight=1)
        right_title = tk.Frame(right_head, bg=panel)
        right_title.grid(row=0, column=0, sticky="w")
        rocket_icon = tk.Canvas(right_title, width=24, height=24, bg=panel, bd=0, highlightthickness=0)
        rocket_icon.pack(side="left", padx=(0, 8))
        rocket_icon.create_oval(9, 3, 18, 12, outline=theme.MUTED, width=1)
        rocket_icon.create_line(8, 12, 4, 17, 9, 16, fill=theme.MUTED, width=1)
        rocket_icon.create_line(17, 12, 20, 17, 15, 16, fill=theme.MUTED, width=1)
        rocket_icon.create_line(11, 14, 7, 22, fill=theme.MUTED, width=1)
        tk.Label(
            right_title, text="DÉMARRER", bg=panel, fg=theme.INK,
            font=(theme.FONT_UI, 11),
        ).pack(side="left")
        tk.Frame(right_head, bg=green, height=1).grid(row=0, column=1, sticky="ew", padx=14)

        new_button = tk.Frame(right_head, bg=theme.ACCENT_DARK, cursor="hand2")
        new_button.grid(row=0, column=2, sticky="e", ipadx=14, ipady=7)
        new_button_text = tk.Label(
            new_button, text="＋  Nouveau projet", bg=theme.ACCENT_DARK,
            fg=theme.WHITE, font=(theme.FONT_UI, 10), cursor="hand2",
        )
        new_button_text.pack(padx=10)
        for widget in (new_button, new_button_text):
            widget.bind("<Button-1>", lambda _e: self.open_create_dialog())

        tk.Label(
            right, text="Choisissez le type de projet à créer",
            bg=panel, fg=theme.INK, font=(theme.FONT_UI, 9),
        ).grid(row=1, column=0, sticky="w", padx=30, pady=(10, 8))

        self._home_new_type_var = tk.StringVar(value="ouvrage_structure")
        self._home_new_name_var = tk.StringVar(value="Nouveau projet")
        self._home_new_location_var = tk.StringVar(value=str(Path.home() / "Documents"))
        self._home_new_sources = []
        self._home_source_count_var = tk.StringVar(value="Aucun fichier sélectionné")
        self._home_type_frames = {}
        self._home_type_icon_labels = {}
        self._home_type_radios = {}

        type_row = tk.Frame(right, bg=panel)
        type_row.grid(row=2, column=0, sticky="ew", padx=30)
        for col in range(3):
            type_row.grid_columnconfigure(col, weight=1, uniform="home_types")

        type_data = {
            "ouvrage_structure": ("Livre de fiches", "Fiches, guides,\nréférentiels", green),
            "livre_textuel": ("Livre textuel", "Roman, récit,\nessai", purple),
            "bande_dessinee": ("Bande dessinée", "Planches, cases,\nnarration", orange),
        }

        for col, key in enumerate(("ouvrage_structure", "livre_textuel", "bande_dessinee")):
            title, subtitle, accent = type_data[key]
            card = tk.Frame(
                type_row, bg=panel_alt, highlightthickness=1,
                highlightbackground=border, cursor="hand2",
            )
            card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 7, 0))
            card.grid_columnconfigure(0, weight=1)

            radio = tk.Canvas(card, width=22, height=22, bg=panel_alt, bd=0, highlightthickness=0)
            radio.grid(row=0, column=0, sticky="nw", padx=10, pady=(10, 0))
            self._home_type_radios[key] = radio

            icon = tk.Label(card, bg=panel_alt, bd=0)
            icon.grid(row=1, column=0, pady=(0, 1))
            self._home_type_icon_labels[key] = icon

            title_label = tk.Label(
                card, text=title, bg=panel_alt, fg=accent,
                font=(theme.FONT_UI, 10, "bold"),
            )
            title_label.grid(row=2, column=0, pady=(0, 4))
            subtitle_label = tk.Label(
                card, text=subtitle, bg=panel_alt, fg=theme.MUTED,
                font=(theme.FONT_UI, 8), justify="center",
            )
            subtitle_label.grid(row=3, column=0, pady=(0, 14))

            for widget in (card, radio, icon, title_label, subtitle_label):
                widget.bind("<Button-1>", lambda _e, k=key: self._home_select_type(k))
            self._home_type_frames[key] = card

        # Zone dépôt, volontairement large comme sur la maquette.
        lower = tk.Frame(right, bg=panel)
        lower.grid(row=3, column=0, sticky="nsew", padx=30, pady=(12, 0))
        lower.grid_columnconfigure(0, weight=1)
        lower.grid_rowconfigure(0, weight=1)

        self.home_drop_canvas = tk.Canvas(lower, bg=panel, bd=0, highlightthickness=0, cursor="hand2")
        self.home_drop_canvas.grid(row=0, column=0, sticky="nsew")
        self.home_drop_canvas.bind("<Configure>", lambda _e: self._home_redraw_dropzone())
        self.home_drop_canvas.bind("<Button-1>", lambda _e: self._home_add_sources())

        open_right = tk.Frame(
            right, bg=panel_alt, highlightthickness=1,
            highlightbackground=border, cursor="hand2",
        )
        open_right.grid(row=4, column=0, sticky="ew", padx=30, pady=(10, 22), ipady=10)
        open_right.grid_columnconfigure(1, weight=1)
        open_right_icon = tk.Label(open_right, text="▱", bg=panel_alt, fg=theme.MUTED, font=(theme.FONT_UI, 16))
        open_right_icon.grid(row=0, column=0, padx=(14, 10))
        open_right_text = tk.Label(
            open_right, text="Ouvrir un projet TomeLinea", bg=panel_alt,
            fg=theme.INK, font=(theme.FONT_UI, 9), anchor="w",
        )
        open_right_text.grid(row=0, column=1, sticky="ew")
        open_right_arrow = tk.Label(open_right, text="›", bg=panel_alt, fg=theme.MUTED, font=(theme.FONT_UI, 17))
        open_right_arrow.grid(row=0, column=2, padx=(8, 13))
        for widget in (open_right, open_right_icon, open_right_text, open_right_arrow):
            widget.bind("<Button-1>", lambda _e: self.open_existing_project())

        # -----------------------------------------------------------------
        # Citation basse.
        # -----------------------------------------------------------------
        quote = tk.Frame(screen, bg=theme.WINDOW_DEEP)
        quote.place(relx=0.31, rely=0.845, relwidth=0.39, relheight=0.09)
        tk.Label(
            quote, text="“  Chaque idée a sa forme.  ”",
            bg=theme.WINDOW_DEEP, fg=theme.MUTED,
            font=(theme.FONT_TITLE, 12, "italic"),
        ).pack()
        tk.Label(
            quote,
            text="TomeLinea vous accompagne de la première ligne au livre terminé.",
            bg=theme.WINDOW_DEEP, fg=theme.MUTED_DARK,
            font=(theme.FONT_UI, 8),
        ).pack(pady=(4, 0))
        tk.Frame(quote, bg=theme.ACCENT_DARK, height=1, width=250).pack(pady=(9, 0))

        # -----------------------------------------------------------------
        # Petit panneau de confirmation : uniquement après "Nouveau projet".
        # Il ne change jamais la composition de l'Accueil.
        # -----------------------------------------------------------------
        self.home_creator_frame = tk.Frame(
            screen, bg=theme.PANEL_ALT, highlightthickness=1,
            highlightbackground=theme.ACCENT,
        )
        self.home_creator_frame.place_forget()
        self.home_creator_frame.grid_columnconfigure(1, weight=1)

        tk.Label(
            self.home_creator_frame, text="Créer le projet", bg=theme.PANEL_ALT,
            fg=theme.INK, font=(theme.FONT_TITLE, 14, "bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=18, pady=(14, 10))
        tk.Label(
            self.home_creator_frame, text="Nom", bg=theme.PANEL_ALT, fg=theme.MUTED,
            font=(theme.FONT_UI, 8, "bold"),
        ).grid(row=1, column=0, sticky="w", padx=(18, 8), pady=5)
        tk.Entry(
            self.home_creator_frame, textvariable=self._home_new_name_var,
            bg=theme.PANEL, fg=theme.INK, insertbackground=theme.INK,
            relief="flat", font=(theme.FONT_UI, 9),
        ).grid(row=1, column=1, columnspan=2, sticky="ew", padx=(0, 18), pady=5, ipady=5)
        tk.Label(
            self.home_creator_frame, text="Emplacement", bg=theme.PANEL_ALT,
            fg=theme.MUTED, font=(theme.FONT_UI, 8, "bold"),
        ).grid(row=2, column=0, sticky="w", padx=(18, 8), pady=5)
        tk.Entry(
            self.home_creator_frame, textvariable=self._home_new_location_var,
            bg=theme.PANEL, fg=theme.INK, insertbackground=theme.INK,
            relief="flat", font=(theme.FONT_UI, 9),
        ).grid(row=2, column=1, sticky="ew", pady=5, ipady=5)
        V3Button(
            self.home_creator_frame, "…",
            lambda: self._choose_location(self._home_new_location_var), compact=True,
        ).grid(row=2, column=2, padx=(6, 18), pady=5)
        tk.Label(
            self.home_creator_frame, textvariable=self._home_source_count_var,
            bg=theme.PANEL_ALT, fg=theme.MUTED_DARK,
            font=(theme.FONT_UI, 7),
        ).grid(row=3, column=0, columnspan=3, sticky="w", padx=18, pady=(7, 10))
        overlay_actions = tk.Frame(self.home_creator_frame, bg=theme.PANEL_ALT)
        overlay_actions.grid(row=4, column=0, columnspan=3, sticky="ew", padx=18, pady=(0, 15))
        overlay_actions.grid_columnconfigure(0, weight=1)
        V3Button(overlay_actions, "Annuler", self._home_hide_creator, compact=True).grid(row=0, column=1, padx=(0, 7))
        V3Button(
            overlay_actions, "Créer et ouvrir", self._home_create_project_inline,
            primary=True, compact=True,
        ).grid(row=0, column=2)

        self._home_refresh_type_cards()
        self._refresh_home_recent()
        self.after_idle(self._home_redraw_dropzone)

    def _home_card(self, parent, col, *, title, subtitle, action, command, return_panel=False):
        panel = CutPanel(parent, fill=theme.PANEL, border=theme.BORDER, cut=18, padding=(22, 20))
        panel.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 9, 0 if col == 2 else 9))
        body = panel.body
        body.grid_rowconfigure(1, weight=1)
        body.grid_columnconfigure(0, weight=1)

        tk.Label(
            body,
            text=title,
            bg=theme.PANEL,
            fg=theme.INK,
            font=(theme.FONT_TITLE, 16, "bold"),
        ).grid(row=0, column=0, sticky="w")

        subtitle_var = tk.StringVar(value=subtitle)
        tk.Label(
            body,
            textvariable=subtitle_var,
            bg=theme.PANEL,
            fg=theme.MUTED,
            justify="left",
            anchor="nw",
            wraplength=300,
            font=(theme.FONT_UI, 9),
        ).grid(row=1, column=0, sticky="nsew", pady=(12, 14))

        V3Button(body, action, command, primary=True).grid(row=2, column=0, sticky="w")
        panel._subtitle_var = subtitle_var
        if return_panel:
            return panel
        return None

    # ------------------------------------------------------------------
    # Espace projet unique V3
    # ------------------------------------------------------------------

    def _build_workspace(self):
        screen = self._screen_with_background("workspace")

        # A, B et C ne sont jamais reconstruits. En zoom de page, le même
        # panneau B s'étend simplement devant C pour exploiter l'écran.
        self._book_page_focus = False
        self.zone_a = CutPanel(screen, fill=theme.PANEL, border=theme.BORDER, cut=14, padding=(18, 10))
        self.zone_b = CutPanel(screen, fill=theme.PANEL, border=theme.BORDER, cut=18, padding=(14, 10))
        self.book_canvas = BookCanvas(
            self.zone_b.body,
            on_open_item=self.open_consultation,
            on_change=self._refresh_workspace_state,
            on_focus_change=self._set_book_page_focus,
        )
        self.book_canvas.pack(fill="both", expand=True)
        self.zone_c = CutPanel(screen, fill=theme.PANEL, border=theme.BORDER, cut=18, padding=(16, 12))
        self.focus_toolbar = FocusToolbar(
            screen,
            book_canvas=self.book_canvas,
            tabs=theme.TAB_NAMES,
            on_select_tab=self.select_tab,
        )

        def layout(event=None):
            if event is None:
                w = max(1100, screen.winfo_width())
                h = max(700, screen.winfo_height())
            else:
                w = max(1100, event.width)
                h = max(700, event.height)

            margin_x = max(28, int(w * 0.045))
            margin_y = max(18, int(h * 0.035))
            inner_w = w - margin_x * 2
            gap = 10
            a_h = max(74, min(88, int(h * 0.09)))
            c_h = max(220, min(270, int(h * 0.245)))

            normal_b_h = max(300, h - (margin_y * 2) - (gap * 2) - a_h - c_h)
            normal_c_y = margin_y + a_h + gap + normal_b_h + gap
            b_y = margin_y + a_h + gap

            self.zone_a.place(x=margin_x, y=margin_y, width=inner_w, height=a_h)
            self.zone_c.place(x=margin_x, y=normal_c_y, width=inner_w, height=c_h)

            if self._book_page_focus:
                # Même B, aucune transition d'écran : il couvre simplement C.
                focus_b_h = max(360, h - b_y - margin_y)
                self.zone_b.place(x=margin_x, y=b_y, width=inner_w, height=focus_b_h)

                # Une seule barre flottante conserve les commandes essentielles
                # et l'accès aux quatre contextes de travail, sans reconstruire C.
                toolbar_w = min(760, max(600, inner_w - 70))
                toolbar_h = 48
                toolbar_x = margin_x + max(0, (inner_w - toolbar_w) // 2)
                toolbar_y = b_y + focus_b_h - toolbar_h - 14
                self.focus_toolbar.place(
                    x=toolbar_x,
                    y=toolbar_y,
                    width=toolbar_w,
                    height=toolbar_h,
                )
                self.zone_b.tk.call("raise", self.zone_b._w)
                self.focus_toolbar.tk.call("raise", self.focus_toolbar._w)
                self.zone_a.tk.call("raise", self.zone_a._w)
            else:
                self.focus_toolbar.place_forget()
                self.zone_b.place(x=margin_x, y=b_y, width=inner_w, height=normal_b_h)
                self.zone_b.tk.call("raise", self.zone_b._w)
                self.zone_c.tk.call("raise", self.zone_c._w)
                self.zone_a.tk.call("raise", self.zone_a._w)

        self._workspace_layout_callback = layout
        screen.bind("<Configure>", layout, add="+")
        self._build_zone_a()
        self._build_zone_c()

    def _set_book_page_focus(self, active: bool):
        active = bool(active)
        if active == getattr(self, "_book_page_focus", False):
            return
        self._book_page_focus = active
        callback = getattr(self, "_workspace_layout_callback", None)
        if callback is not None:
            self.after_idle(lambda: callback(None))

    def _build_zone_a(self):
        body = self.zone_a.body
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(0, weight=1)

        left = tk.Frame(body, bg=theme.PANEL)
        left.grid(row=0, column=0, sticky="nsw")
        self.project_name_var = tk.StringVar(value="Aucun projet")
        self.project_meta_var = tk.StringVar(value="")
        tk.Label(
            left,
            textvariable=self.project_name_var,
            bg=theme.PANEL,
            fg=theme.INK,
            font=(theme.FONT_TITLE, 14, "bold"),
        ).pack(anchor="w")
        tk.Label(
            left,
            textvariable=self.project_meta_var,
            bg=theme.PANEL,
            fg=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 8, "bold"),
        ).pack(anchor="w", pady=(3, 0))

        status = tk.Frame(body, bg=theme.PANEL)
        status.grid(row=0, column=1, sticky="nsew", padx=(35, 20))
        self.project_status_var = tk.StringVar(value="")
        tk.Label(
            status,
            textvariable=self.project_status_var,
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 9),
            anchor="w",
        ).pack(fill="both", expand=True)

        actions = tk.Frame(body, bg=theme.PANEL)
        actions.grid(row=0, column=2, sticky="e")
        V3Button(actions, "Accueil", self.show_home, compact=True).pack(side="left", padx=3)
        V3Button(actions, "Importer", self.import_sources, compact=True).pack(side="left", padx=3)
        V3Button(actions, "Annuler", None, compact=True, state="disabled").pack(side="left", padx=3)
        V3Button(actions, "Rétablir", None, compact=True, state="disabled").pack(side="left", padx=3)

    def _build_zone_c(self):
        body = self.zone_c.body
        body.grid_rowconfigure(1, weight=1)
        body.grid_columnconfigure(0, weight=1)

        self.tab_bar = tk.Frame(body, bg=theme.PANEL)
        self.tab_bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.tab_buttons: dict[str, tk.Button] = {}
        for index, (key, label) in enumerate(theme.TAB_NAMES):
            button = tk.Button(
                self.tab_bar,
                text=label,
                command=lambda k=key: self.select_tab(k),
                bg=theme.PANEL_SOFT,
                fg=theme.INK,
                activebackground=theme.ACCENT_SOFT,
                activeforeground=theme.WHITE,
                relief="flat",
                bd=0,
                padx=22,
                pady=7,
                font=(theme.FONT_UI, 9, "bold"),
                cursor="hand2",
            )
            button.pack(side="left", padx=(0 if index == 0 else 4, 0))
            self.tab_buttons[key] = button

        tk.Label(
            self.tab_bar,
            text="A et B restent fixes — seuls les outils changent",
            bg=theme.PANEL,
            fg=theme.MUTED_DARK,
            font=(theme.FONT_UI, 8),
        ).pack(side="right")

        self.tab_host = tk.Frame(body, bg=theme.PANEL)
        self.tab_host.grid(row=1, column=0, sticky="nsew")
        self.tab_host.grid_rowconfigure(0, weight=1)
        self.tab_host.grid_columnconfigure(0, weight=1)

        self.tab_frames: dict[str, tk.Frame] = {}
        for key, _label in theme.TAB_NAMES:
            frame = tk.Frame(self.tab_host, bg=theme.PANEL)
            frame.grid(row=0, column=0, sticky="nsew")
            self.tab_frames[key] = frame

        self._build_structure_tab(self.tab_frames["structure"])
        self._build_gabarits_tab(self.tab_frames["gabarits"])
        self._build_production_tab(self.tab_frames["production"])
        self._build_sortie_tab(self.tab_frames["sortie"])
        self.select_tab("structure")

    def _build_tool_tab(self, parent, *, title: str, intro: str, groups: list[tuple[str, list[str]]], info_title: str, info_text: str):
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(1, weight=1)

        heading = tk.Frame(parent, bg=theme.PANEL)
        heading.grid(row=0, column=0, sticky="ew", pady=(0, 9))
        tk.Label(
            heading,
            text=title,
            bg=theme.PANEL,
            fg=theme.INK,
            font=(theme.FONT_TITLE, 13, "bold"),
        ).pack(side="left")
        tk.Label(
            heading,
            text=intro,
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 8),
        ).pack(side="left", padx=(16, 0))

        area = tk.Frame(parent, bg=theme.PANEL)
        area.grid(row=1, column=0, sticky="nsew")
        area.grid_columnconfigure(0, weight=1)
        area.grid_columnconfigure(1, weight=1)
        area.grid_columnconfigure(2, weight=2)
        area.grid_rowconfigure(0, weight=1)

        for col, (group_title, buttons) in enumerate(groups[:2]):
            box = tk.Frame(area, bg=theme.PANEL_ALT, padx=14, pady=12)
            box.grid(row=0, column=col, sticky="nsew", padx=(0, 8 if col == 0 else 12))
            tk.Label(
                box,
                text=group_title,
                bg=theme.PANEL_ALT,
                fg=theme.ACCENT_BRIGHT,
                font=(theme.FONT_UI, 8, "bold"),
            ).pack(anchor="w", pady=(0, 8))
            for label in buttons:
                V3Button(box, label, self._placeholder_action, compact=True).pack(fill="x", pady=3)

        info = tk.Frame(area, bg=theme.PANEL_ALT, padx=18, pady=14)
        info.grid(row=0, column=2, sticky="nsew")
        tk.Label(
            info,
            text=info_title,
            bg=theme.PANEL_ALT,
            fg=theme.INK,
            font=(theme.FONT_TITLE, 11, "bold"),
        ).pack(anchor="w")
        tk.Frame(info, bg=theme.ACCENT_DARK, height=1).pack(fill="x", pady=(8, 10))
        tk.Label(
            info,
            text=info_text,
            bg=theme.PANEL_ALT,
            fg=theme.MUTED,
            justify="left",
            anchor="nw",
            wraplength=430,
            font=(theme.FONT_UI, 9),
        ).pack(fill="both", expand=True)

    def _build_structure_tab(self, parent):
        self._build_tool_tab(
            parent,
            title="Structure",
            intro="Construire et réorganiser le livre à tout moment.",
            groups=[
                ("Construction", ["Ajouter une page", "Ajouter une partie", "Choisir un type", "Insérer un blanc"]),
                ("Organisation", ["Déplacer", "Dupliquer", "Supprimer", "Règles recto-verso"]),
            ],
            info_title="Informations de structure",
            info_text=(
                "La zone B sera l’unique représentation du livre. Les ajouts, suppressions et déplacements "
                "seront visibles immédiatement et resteront accessibles quelle que soit l’étape du travail."
            ),
        )

    def _build_gabarits_tab(self, parent):
        self._build_tool_tab(
            parent,
            title="Gabarits",
            intro="Préparer les modèles uniquement lorsqu’ils sont nécessaires.",
            groups=[
                ("Gabarits", ["Créer un gabarit", "Ouvrir un gabarit", "Dupliquer", "Bibliothèque"]),
                ("Association", ["Associer au type", "Appliquer à la sélection", "Voir les usages", "Remplacer"]),
            ],
            info_title="Gabarit sélectionné",
            info_text=(
                "Cet onglet n’est pas une étape obligatoire. Si un gabarit existe déjà, la production peut "
                "commencer directement. La zone B montrera progressivement les gabarits associés."
            ),
        )

    def _build_production_tab(self, parent):
        self._build_tool_tab(
            parent,
            title="Production",
            intro="Insérer le contenu de l’auteur et produire les pages.",
            groups=[
                ("Production", ["Page sélectionnée", "Produire en lot", "Mettre à jour", "Marquer comme prêt"]),
                ("Contenu", ["Contenu de l’auteur", "Images", "Ressources", "Éléments non affectés"]),
            ],
            info_title="État de production",
            info_text=(
                "Une même mécanique servira à la page unique et aux lots. À mesure que les pages sont produites, "
                "la zone B remplace les emplacements de structure par leur rendu réel."
            ),
        )

    def _build_sortie_tab(self, parent):
        self._build_tool_tab(
            parent,
            title="Sortie",
            intro="Contrôler, corriger si nécessaire puis préparer le fichier final.",
            groups=[
                ("Contrôles", ["Lancer les contrôles", "Voir les anomalies", "Consulter la sélection", "Revenir au travail"]),
                ("Export", ["Paramètres d’impression", "Couverture / dos", "Générer le PDF", "Créer l’archive"]),
            ],
            info_title="État du livre",
            info_text=(
                "Il n’y a plus de bureau Vérification ni Assemblage. Les contrôles deviennent transversaux et la "
                "consultation détaillée s’ouvre depuis la zone B, sans créer une nouvelle copie du livre."
            ),
        )

    def select_tab(self, key: str):
        if key not in self.tab_frames:
            return
        self.active_tab = key
        self.tab_frames[key].tkraise()
        focus_toolbar = getattr(self, "focus_toolbar", None)
        if focus_toolbar is not None:
            focus_toolbar.set_active_tab(key)
        for tab_key, button in self.tab_buttons.items():
            if tab_key == key:
                button.configure(bg=theme.ACCENT_DARK, fg=theme.WHITE)
            else:
                button.configure(bg=theme.PANEL_SOFT, fg=theme.INK)

    # ------------------------------------------------------------------
    # Projet / import
    # ------------------------------------------------------------------

    def open_create_dialog(self):
        # Le formulaire de confirmation est un panneau interne, jamais une
        # nouvelle fenêtre. Le choix du type et les fichiers restent visibles.
        if not self._home_new_name_var.get().strip():
            self._home_new_name_var.set("Nouveau projet")
        if not self._home_new_location_var.get().strip():
            self._home_new_location_var.set(str(Path.home() / "Documents"))
        self.home_creator_frame.place(
            relx=0.662,
            rely=0.51,
            anchor="center",
            relwidth=0.33,
            relheight=0.255,
        )
        self.home_creator_frame.lift()

    def _choose_location(self, variable: tk.StringVar):
        folder = filedialog.askdirectory(parent=self, title="Choisir l’emplacement du projet")
        if folder:
            variable.set(folder)

    def _home_hide_creator(self):
        self.home_creator_frame.place_forget()

    def _home_select_type(self, key: str):
        self._home_new_type_var.set(key)
        self._home_refresh_type_cards()


    def _home_refresh_type_cards(self):
        selected = self._home_new_type_var.get()
        colors = {
            "ouvrage_structure": "#79B49C",
            "livre_textuel": "#A37AD4",
            "bande_dessinee": "#D37B55",
        }
        for key, frame in getattr(self, "_home_type_frames", {}).items():
            active = key == selected
            accent = colors.get(key, theme.ACCENT)
            selected_bg = {
                "ouvrage_structure": "#2B3A36",
                "livre_textuel": "#34313F",
                "bande_dessinee": "#3B302C",
            }.get(key, "#2B323C")
            bg = selected_bg if active else "#2B323C"
            frame.configure(
                bg=bg,
                highlightthickness=2 if active else 1,
                highlightbackground=accent if active else "#49545E",
            )

            for child in frame.winfo_children():
                if child is getattr(self, "_home_type_radios", {}).get(key):
                    continue
                try:
                    child.configure(bg=bg)
                except Exception:
                    pass

            icon_label = getattr(self, "_home_type_icon_labels", {}).get(key)
            if icon_label is not None:
                photo = self._home_type_icon_glow(key, 118, selected=active)
                if photo is not None:
                    icon_label.configure(image=photo)
                    icon_label.image = photo

            radio = getattr(self, "_home_type_radios", {}).get(key)
            if radio is not None:
                radio.configure(bg=bg)
                radio.delete("all")
                radio.create_oval(3, 3, 19, 19, outline=accent, width=2 if active else 1)
                if active:
                    # Voyant lumineux : l'idée "s'allume" sans ajouter une
                    # nouvelle icône ou un nouvel objet graphique.
                    radio.create_oval(8, 8, 14, 14, fill="#F5F2FF", outline="")
                    radio.create_oval(1, 1, 21, 21, outline=accent, width=1)

    def _home_add_sources(self):
        paths = filedialog.askopenfilenames(
            parent=self,
            title="Ajouter le travail de l’auteur",
        )
        for raw in paths:
            if raw not in self._home_new_sources:
                self._home_new_sources.append(raw)
        count = len(self._home_new_sources)
        if count == 0:
            self._home_source_count_var.set("Aucun fichier sélectionné")
        elif count == 1:
            self._home_source_count_var.set(Path(self._home_new_sources[0]).name)
        else:
            self._home_source_count_var.set(f"{count} fichiers sélectionnés")
        self._home_redraw_dropzone()

    def _home_create_project_inline(self):
        name = self._home_new_name_var.get().strip()
        location = self._home_new_location_var.get().strip()
        if not name or not location:
            messagebox.showerror(
                "TomeLinea",
                "Le nom et l’emplacement sont nécessaires.",
                parent=self,
            )
            return
        try:
            project = self.project_manager.new_project(
                location,
                name,
                project_type=self._home_new_type_var.get(),
            )
            self._store_source_files(project, list(self._home_new_sources))
        except Exception as exc:
            messagebox.showerror("TomeLinea", str(exc), parent=self)
            return

        self._home_hide_creator()
        self._remember_recent(project)
        self.show_workspace(project)


    def _open_recent_path(self, path: str):
        if not path or not Path(path).exists():
            messagebox.showwarning(
                "TomeLinea",
                "Ce projet récent est introuvable.",
                parent=self,
            )
            self._refresh_home_recent()
            return
        try:
            project = self.project_manager.open_project(path)
        except Exception as exc:
            messagebox.showerror("TomeLinea", str(exc), parent=self)
            return
        self._remember_recent(project)
        self.show_workspace(project)

    def open_existing_project(self):
        folder = filedialog.askdirectory(parent=self, title="Ouvrir un projet TomeLinea")
        if not folder:
            return
        try:
            project = self.project_manager.open_project(folder)
        except Exception as exc:
            messagebox.showerror("TomeLinea", str(exc), parent=self)
            return
        self._remember_recent(project)
        self.show_workspace(project)

    def open_last_project(self):
        recent = self._load_recent()
        if not recent:
            messagebox.showinfo("TomeLinea", "Aucun projet récent enregistré pour la V3.", parent=self)
            return
        path = recent[0].get("path", "")
        if not path or not Path(path).exists():
            messagebox.showwarning("TomeLinea", "Le dernier projet enregistré est introuvable.", parent=self)
            return
        try:
            project = self.project_manager.open_project(path)
        except Exception as exc:
            messagebox.showerror("TomeLinea", str(exc), parent=self)
            return
        self.show_workspace(project)

    def import_sources(self):
        if self.context is None or self.context.project is None:
            return
        paths = filedialog.askopenfilenames(parent=self, title="Ajouter le travail de l’auteur")
        if not paths:
            return
        try:
            self._store_source_files(self.context.project, list(paths))
        except Exception as exc:
            messagebox.showerror("TomeLinea", str(exc), parent=self)
            return
        self._refresh_workspace_state()

    def _store_source_files(self, project: Project, paths: list[str]):
        if not paths:
            return
        source_dir = project.root / "sources_originales"
        source_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = source_dir / "manifest.json"
        manifest = {"files": []}
        if manifest_path.exists():
            try:
                existing = json.loads(manifest_path.read_text(encoding="utf-8"))
                if isinstance(existing, dict):
                    manifest = existing
                    manifest.setdefault("files", [])
            except Exception:
                pass
        known = {entry.get("stored") for entry in manifest.get("files", []) if isinstance(entry, dict)}
        for raw in paths:
            src = Path(raw)
            if not src.is_file():
                continue
            target = source_dir / src.name
            stem = src.stem
            suffix = src.suffix
            counter = 2
            while target.name in known or target.exists():
                target = source_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            shutil.copy2(src, target)
            manifest["files"].append({"original": str(src), "stored": target.name})
            known.add(target.name)
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    def _source_count(self, project: Project | None) -> int:
        if project is None or project.root is None:
            return 0
        manifest = project.root / "sources_originales" / "manifest.json"
        if not manifest.exists():
            return 0
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            files = data.get("files", []) if isinstance(data, dict) else []
            return len(files) if isinstance(files, list) else 0
        except Exception:
            return 0

    # ------------------------------------------------------------------
    # Navigation V3
    # ------------------------------------------------------------------

    def show_home(self):
        self._refresh_home_recent()
        self._screens["home"].tkraise()

    def show_workspace(self, project: Project):
        self.context = WorkspaceContext(project=project, name=project.name, project_type=project.project_type)
        self.book_canvas.set_project(project)
        self._refresh_workspace_state()
        self._screens["workspace"].tkraise()

    def _show_workspace_preview(self, name="Projet de démonstration", project_type="ouvrage_structure"):
        """Utilitaire de test visuel interne ; n’écrit rien dans le projet."""
        self.context = WorkspaceContext(project=None, name=name, project_type=project_type)
        self.book_canvas.set_project(None)
        self._refresh_workspace_state()
        self._screens["workspace"].tkraise()

    def _refresh_workspace_state(self):
        if self.context is None:
            return
        self.project_name_var.set(self.context.name)
        self.project_meta_var.set(self.context.type_label)
        page_count = len(self.book_canvas.items)
        source_count = self._source_count(self.context.project)
        self.project_status_var.set(
            f"{page_count} page{'s' if page_count != 1 else ''} dans le livre  •  "
            f"{source_count} source{'s' if source_count != 1 else ''} auteur  •  "
            "contrôles : non lancés"
        )

    def open_consultation(self, item: dict, index: int):
        win = tk.Toplevel(self)
        win.title(f"TomeLinea — Consultation page {index + 1}")
        win.configure(bg=theme.WINDOW_DEEP)
        win.transient(self)
        win.geometry("760x500")

        panel = CutPanel(win, fill=theme.PANEL, border=theme.BORDER, cut=18, padding=(24, 20))
        panel.pack(fill="both", expand=True, padx=18, pady=18)
        body = panel.body
        body.grid_rowconfigure(1, weight=1)
        body.grid_columnconfigure(0, weight=1)

        label = self.book_canvas._item_label(item, index)
        tk.Label(
            body,
            text=f"Page {index + 1} — {label}",
            bg=theme.PANEL,
            fg=theme.INK,
            font=(theme.FONT_TITLE, 17, "bold"),
        ).grid(row=0, column=0, sticky="w")

        preview = tk.Frame(body, bg="#E7E7E3", highlightthickness=1, highlightbackground="#CACCC8")
        preview.grid(row=1, column=0, sticky="nsew", pady=(15, 14))
        tk.Label(
            preview,
            text="Consultation détaillée\n\nLe rendu réel de la page sera branché ici.",
            bg="#E7E7E3",
            fg="#4C555C",
            font=(theme.FONT_UI, 10),
            justify="center",
        ).place(relx=0.5, rely=0.5, anchor="center")

        actions = tk.Frame(body, bg=theme.PANEL)
        actions.grid(row=2, column=0, sticky="ew")
        V3Button(actions, "Fermer", win.destroy).pack(side="right")
        for key, text in reversed((
            ("structure", "Retour Structure"),
            ("gabarits", "Retour Gabarits"),
            ("production", "Retour Production"),
            ("sortie", "Retour Sortie"),
        )):
            V3Button(actions, text, lambda k=key: self._consult_return(win, k), compact=True).pack(side="left", padx=(0, 5))

    def _consult_return(self, win: tk.Toplevel, tab: str):
        win.destroy()
        self.select_tab(tab)
        self._screens["workspace"].tkraise()

    def _placeholder_action(self):
        messagebox.showinfo(
            "TomeLinea V3",
            "La structure générale est en place. Cette commande sera branchée lors du remplissage de l’onglet.",
            parent=self,
        )

    # ------------------------------------------------------------------
    # Récents V3
    # ------------------------------------------------------------------

    def _load_recent(self) -> list[dict]:
        if not RECENT_FILE.exists():
            return []
        try:
            data = json.loads(RECENT_FILE.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception:
            return []

    def _remember_recent(self, project: Project):
        if project.root is None:
            return
        entry = {
            "name": project.name,
            "type": project.project_type,
            "path": str(project.root),
        }
        recent = [r for r in self._load_recent() if r.get("path") != entry["path"]]
        recent.insert(0, entry)
        recent = recent[:8]
        RECENT_FILE.parent.mkdir(parents=True, exist_ok=True)
        RECENT_FILE.write_text(json.dumps(recent, indent=2, ensure_ascii=False), encoding="utf-8")
        self._refresh_home_recent()


    def _home_redraw_dropzone(self):
        canvas = getattr(self, "home_drop_canvas", None)
        if canvas is None:
            return
        canvas.delete("all")
        width = max(260, canvas.winfo_width())
        height = max(92, canvas.winfo_height())
        canvas.create_rectangle(
            2, 2, width - 3, height - 3,
            outline="#6B737B", width=1, dash=(5, 4),
        )

        cx = width * 0.18
        cy = height * 0.47
        # Upload line-icon identique dans son principe à la maquette.
        canvas.create_line(cx, cy + 13, cx, cy - 11, fill=theme.MUTED, width=2)
        canvas.create_line(cx, cy - 11, cx - 8, cy - 3, fill=theme.MUTED, width=2)
        canvas.create_line(cx, cy - 11, cx + 8, cy - 3, fill=theme.MUTED, width=2)
        canvas.create_line(
            cx - 13, cy + 13, cx - 13, cy + 20,
            cx + 13, cy + 20, cx + 13, cy + 13,
            fill=theme.MUTED, width=2,
        )

        count = len(getattr(self, "_home_new_sources", []))
        if count:
            title = f"{count} fichier{'s' if count > 1 else ''} auteur sélectionné{'s' if count > 1 else ''}"
            subtitle = "Cliquez pour modifier la sélection"
        else:
            title = "Déposez ici vos fichiers auteur (facultatif)"
            subtitle = "Documents, images, notes, planches, etc."

        canvas.create_text(
            width * 0.30, height * 0.40, text=title,
            fill=theme.INK, anchor="w", font=(theme.FONT_UI, 9),
        )
        canvas.create_text(
            width * 0.30, height * 0.62, text=subtitle,
            fill=theme.MUTED, anchor="w", font=(theme.FONT_UI, 7),
        )

    def _refresh_home_recent(self):
        host = getattr(self, "home_recent_list", None)
        if host is None:
            return

        for child in host.winfo_children():
            child.destroy()

        recent = self._load_recent()[:4]
        type_labels = {
            "ouvrage_structure": "Ouvrage structuré",
            "livre_textuel": "Livre textuel",
            "bande_dessinee": "Bande dessinée",
        }
        type_colors = {
            "ouvrage_structure": "#79B49C",
            "livre_textuel": "#A37AD4",
            "bande_dessinee": "#D37B55",
        }

        if not recent:
            recent = [{"name": "Votre premier projet", "type": "ouvrage_structure", "path": ""}]

        for row, item in enumerate(recent):
            key = item.get("type", "ouvrage_structure")
            path = item.get("path", "")
            accent = type_colors.get(key, theme.ACCENT)

            card = tk.Frame(
                host, bg="#2B323C", highlightthickness=1,
                highlightbackground="#46505A", cursor="hand2",
            )
            card.grid(row=row, column=0, sticky="ew", pady=(0 if row == 0 else 6, 0), ipady=2)
            card.grid_columnconfigure(1, weight=1)

            photo = self._type_icon(key, 62)
            icon = tk.Label(card, bg="#2B323C", bd=0)
            if photo is not None:
                icon.configure(image=photo)
                icon.image = photo
            icon.grid(row=0, column=0, rowspan=3, padx=(10, 13), pady=4)

            title = tk.Label(
                card, text=item.get("name", "Projet TomeLinea"), bg="#2B323C",
                fg=accent, font=(theme.FONT_UI, 9, "bold"), anchor="w",
            )
            title.grid(row=0, column=1, sticky="ew", pady=(6, 0))
            kind = tk.Label(
                card, text=type_labels.get(key, "Projet TomeLinea"), bg="#2B323C",
                fg=theme.MUTED, font=(theme.FONT_UI, 7), anchor="w",
            )
            kind.grid(row=1, column=1, sticky="ew", pady=(1, 0))
            meta = tk.Label(
                card, text="Projet récent" if path else "Créer ce premier projet",
                bg="#2B323C", fg=theme.MUTED_DARK,
                font=(theme.FONT_UI, 7), anchor="w",
            )
            meta.grid(row=2, column=1, sticky="ew", pady=(1, 6))
            tk.Label(
                card, text="•••", bg="#2B323C", fg=theme.MUTED,
                font=(theme.FONT_UI, 8),
            ).grid(row=0, column=2, rowspan=3, padx=(8, 12))

            command = (lambda p=path: self._open_recent_path(p)) if path else self.open_create_dialog
            for widget in (card, icon, title, kind, meta):
                widget.bind("<Button-1>", lambda _e, fn=command: fn())
