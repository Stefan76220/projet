from __future__ import annotations

import importlib.util
import json
import shutil
from datetime import datetime
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog
from typing import Callable

from PIL import Image, ImageColor, ImageDraw, ImageEnhance, ImageFilter, ImageTk

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

    def new_project_from_model(self, model_folder: str, folder: str, name: str):
        source = Path(model_folder)
        target = Path(folder) / name
        if not (source / "projet.json").exists():
            raise FileNotFoundError("Le modèle sélectionné n’est pas un projet TomeLinea valide.")
        if target.exists():
            raise FileExistsError(f"Un projet nommé « {name} » existe déjà.")

        # Un modèle transmet la structure éditoriale, jamais les fichiers
        # personnels de l'auteur ni les sorties d'un ancien ouvrage.
        shutil.copytree(
            source,
            target,
            ignore=shutil.ignore_patterns(
                "sources_originales", "exports", "cache", "corbeille", "productions"
            ),
        )
        project = Project()
        project.load(str(target))
        project.name = name
        project.root = target
        now = datetime.now().isoformat()
        project.creation_date = now
        project.modification_date = now
        project.save()
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
TOMELINEA_HOME = Path.home() / "Documents" / "TomeLinea"
PROJECTS_HOME = TOMELINEA_HOME / "Projets"
PROJECT_MODELS_HOME = TOMELINEA_HOME / "Modeles"

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
    # ACCUEIL_LOGIQUE_STABLE_V3_V3
    # HABILLAGE_FENETRES_ET_ICONES_V3_V4
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

        # TomeLinea possède ses propres commandes de fermeture : la barre de
        # titre Windows n'apporte rien à l'interface et est masquée partout.
        try:
            self.overrideredirect(True)
        except tk.TclError:
            pass

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
        self._tl_ui_icon_cache: dict[tuple[str, int, str, bool], ImageTk.PhotoImage] = {}
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
        # CONSERVER_BARRE_TACHES_WINDOWS_V3_V5
        # Fenêtre TomeLinea sans barre de titre Windows, mais limitée à la
        # zone de travail réelle de Windows afin de laisser la barre des tâches visible.
        self._fit_to_windows_work_area()

        # Force le premier vrai calcul Windows : taille, Configure et fond.
        self.update_idletasks()
        self.update()

        # L'Accueil est remis explicitement au premier plan après le calcul.
        self._screens["home"].tkraise()
        self.update_idletasks()

        self.lift()
        self.after_idle(self.lift)

    def _fit_to_windows_work_area(self):
        """Occupe l'espace disponible sans recouvrir la barre des tâches Windows."""
        try:
            import ctypes

            class RECT(ctypes.Structure):
                _fields_ = [
                    ("left", ctypes.c_long),
                    ("top", ctypes.c_long),
                    ("right", ctypes.c_long),
                    ("bottom", ctypes.c_long),
                ]

            rect = RECT()
            SPI_GETWORKAREA = 0x0030
            ok = ctypes.windll.user32.SystemParametersInfoW(
                SPI_GETWORKAREA, 0, ctypes.byref(rect), 0
            )
            if ok:
                width = max(1180, rect.right - rect.left)
                height = max(720, rect.bottom - rect.top)
                self.state("normal")
                self.geometry(
                    f"{width}x{height}+{rect.left}+{rect.top}"
                )
                return
        except Exception:
            pass

        # Repli uniquement si l'API Windows n'est pas disponible.
        self.state("normal")
        width = max(1180, self.winfo_screenwidth())
        height = max(720, self.winfo_screenheight() - 48)
        self.geometry(f"{width}x{height}+0+0")

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



    def _home_brand_icon_photo(self, size: int):
        if not hasattr(self, "_home_brand_icon_cache"):
            self._home_brand_icon_cache = {}
        size = int(size)
        if size in self._home_brand_icon_cache:
            return self._home_brand_icon_cache[size]
        path = PROJECT_ROOT / "assets" / "branding" / "tomelinea" / "logo_pack_visibilite" / "TomeLinea_512x512.png"
        if not path.exists():
            return None
        image = Image.open(path).convert("RGBA")
        image.thumbnail((size, size), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self._home_brand_icon_cache[size] = photo
        return photo

    def _home_brand_title_photo(self, width: int):
        if not hasattr(self, "_home_brand_title_cache"):
            self._home_brand_title_cache = {}
        width = int(width)
        if width in self._home_brand_title_cache:
            return self._home_brand_title_cache[width]
        path = PROJECT_ROOT / "assets" / "branding" / "tomelinea" / "logo_pack_visibilite" / "TomeLinea_titre_relief.png"
        if not path.exists():
            return None
        image = Image.open(path).convert("RGBA")
        ratio = width / max(1, image.width)
        image = image.resize((width, max(1, int(image.height * ratio))), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self._home_brand_title_cache[width] = photo
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

    def _tl_ui_icon(self, kind: str, size: int = 28, color: str | None = None, glow: bool = True):
        """Petites icônes ligne TomeLinea, transparentes et rétro-éclairées."""
        color = color or theme.ACCENT_BRIGHT
        cache_key = (kind, int(size), str(color), bool(glow))
        cached = self._tl_ui_icon_cache.get(cache_key)
        if cached is not None:
            return cached

        scale = 4
        side = max(16, int(size)) * scale
        stroke = max(4, int(size * 0.065 * scale))
        mask = Image.new("L", (side, side), 0)
        draw = ImageDraw.Draw(mask)

        def xy(x, y):
            return int(x * side), int(y * side)

        if kind == "search":
            draw.ellipse([xy(0.18, 0.16), xy(0.64, 0.62)], outline=255, width=stroke)
            draw.line([xy(0.56, 0.56), xy(0.82, 0.82)], fill=255, width=stroke)
            draw.ellipse([xy(0.28, 0.26), xy(0.34, 0.32)], fill=255)
        elif kind == "projects":
            draw.rounded_rectangle([xy(0.14, 0.28), xy(0.32, 0.78)], radius=stroke, outline=255, width=stroke)
            draw.rounded_rectangle([xy(0.38, 0.18), xy(0.58, 0.78)], radius=stroke, outline=255, width=stroke)
            draw.rounded_rectangle([xy(0.64, 0.32), xy(0.84, 0.78)], radius=stroke, outline=255, width=stroke)
            draw.line([xy(0.10, 0.84), xy(0.88, 0.84)], fill=255, width=max(3, stroke // 2))
            draw.line([xy(0.42, 0.30), xy(0.54, 0.30)], fill=255, width=max(3, stroke // 2))
        elif kind == "start":
            draw.ellipse([xy(0.18, 0.18), xy(0.76, 0.76)], outline=255, width=stroke)
            draw.line([xy(0.34, 0.66), xy(0.70, 0.30)], fill=255, width=stroke)
            draw.line([xy(0.51, 0.30), xy(0.70, 0.30), xy(0.70, 0.49)], fill=255, width=stroke)
            draw.ellipse([xy(0.24, 0.66), xy(0.34, 0.76)], fill=255)
        elif kind == "model":
            draw.rounded_rectangle([xy(0.18, 0.30), xy(0.66, 0.76)], radius=stroke, outline=255, width=stroke)
            draw.rounded_rectangle([xy(0.31, 0.18), xy(0.79, 0.64)], radius=stroke, outline=255, width=stroke)
            draw.line([xy(0.42, 0.33), xy(0.68, 0.33)], fill=255, width=max(3, stroke // 2))
            draw.line([xy(0.42, 0.44), xy(0.63, 0.44)], fill=255, width=max(3, stroke // 2))
            draw.arc([xy(0.53, 0.49), xy(0.87, 0.84)], start=205, end=355, fill=255, width=max(3, stroke // 2))
            draw.line([xy(0.80, 0.66), xy(0.86, 0.75), xy(0.76, 0.77)], fill=255, width=max(3, stroke // 2))
        else:
            draw.ellipse([xy(0.20, 0.20), xy(0.80, 0.80)], outline=255, width=stroke)

        rgb = ImageColor.getrgb(color)
        result = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        if glow:
            halo_mask = mask.filter(ImageFilter.GaussianBlur(max(7, int(side * 0.055))))
            halo_mask = halo_mask.point(lambda v: int(v * 0.48))
            halo = Image.new("RGBA", (side, side), rgb + (0,))
            halo.putalpha(halo_mask)
            result.alpha_composite(halo)

        line = Image.new("RGBA", (side, side), rgb + (0,))
        line.putalpha(mask)
        result.alpha_composite(line)
        result = result.resize((size, size), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(result)
        self._tl_ui_icon_cache[cache_key] = photo
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
        icon.thumbnail((int(size * 0.82), int(size * 0.82)), Image.Resampling.LANCZOS)
        alpha = icon.getchannel("A")
        result = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        x = (size - icon.width) // 2
        y = (size - icon.height) // 2

        # Halo de base, visible mais discret.
        soft_alpha = alpha.filter(ImageFilter.GaussianBlur(max(11, int(size * 0.10))))
        soft_alpha = soft_alpha.point(lambda v: int(v * 0.62))
        soft = Image.new("RGBA", icon.size, color + (0,))
        soft.putalpha(soft_alpha)
        result.alpha_composite(soft, (x, y))

        if selected:
            # L'effet sélection simule une lumière qui s'allume derrière le livre.
            strong_alpha = alpha.filter(ImageFilter.GaussianBlur(max(20, int(size * 0.15))))
            strong_alpha = strong_alpha.point(lambda v: int(v * 0.90))
            strong = Image.new("RGBA", icon.size, color + (0,))
            strong.putalpha(strong_alpha)
            result.alpha_composite(strong, (x, y))

            bloom_alpha = alpha.filter(ImageFilter.GaussianBlur(max(31, int(size * 0.22))))
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

        PROJECTS_HOME.mkdir(parents=True, exist_ok=True)
        PROJECT_MODELS_HOME.mkdir(parents=True, exist_ok=True)

        # --------------------------------------------------------------
        # Identité / commandes générales
        # --------------------------------------------------------------
        # ACCUEIL_LOGO_STYLE_FERMETURE_V3_V3
        header = tk.Frame(screen, bg=theme.WINDOW_DEEP)
        header.place(relx=0.105, rely=0.048, relwidth=0.78, relheight=0.132)

        brand_wrap = tk.Frame(header, bg=theme.WINDOW_DEEP)
        brand_wrap.place(relx=0.00, rely=0.00, relwidth=0.64, relheight=1.00)

        icon_photo = self._home_brand_icon_photo(94)
        if icon_photo is not None:
            icon_label = tk.Label(brand_wrap, image=icon_photo, bg=theme.WINDOW_DEEP, bd=0)
            icon_label.image = icon_photo
            icon_label.place(x=0, y=2)

        title_photo = self._home_brand_title_photo(455)
        if title_photo is not None:
            title_label = tk.Label(brand_wrap, image=title_photo, bg=theme.WINDOW_DEEP, bd=0)
            title_label.image = title_photo
            title_label.place(x=112, y=9)
        else:
            tk.Label(
                brand_wrap,
                text="TomeLinea",
                bg=theme.WINDOW_DEEP,
                fg=theme.INK,
                font=(theme.FONT_TITLE, 34),
            ).place(x=112, y=10)

        tk.Label(
            brand_wrap,
            text="V3",
            bg=theme.WINDOW_DEEP,
            fg=green,
            font=(theme.FONT_UI, 14, "bold"),
        ).place(x=575, y=16)

        tk.Label(
            brand_wrap,
            text="LA LIGNE ÉDITORIALE JUSQU’AU LIVRE",
            bg=theme.WINDOW_DEEP,
            fg=green,
            font=(theme.FONT_UI, 10, "bold"),
        ).place(x=115, y=74)

        tools = tk.Frame(header, bg=theme.WINDOW_DEEP)
        tools.place(relx=0.73, rely=0.14, relwidth=0.20, relheight=0.52)
        help_label = tk.Label(
            tools, text="?  Aide", bg=theme.WINDOW_DEEP, fg=theme.INK,
            font=(theme.FONT_UI, 9), cursor="hand2",
        )
        help_label.pack(side="left", padx=(0, 24))
        help_label.bind("<Button-1>", lambda _e: self._show_general_help())
        prefs_label = tk.Label(
            tools, text="⚙  Préférences", bg=theme.WINDOW_DEEP, fg=theme.MUTED,
            font=(theme.FONT_UI, 9), cursor="hand2",
        )
        prefs_label.pack(side="left")
        prefs_label.bind("<Button-1>", lambda _e: self._show_preferences_waiting())

        close_label = tk.Label(
            header,
            text="✕",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(theme.FONT_UI, 15, "bold"),
            cursor="hand2",
            padx=8,
            pady=2,
        )
        close_label.place(relx=0.985, y=10, anchor="ne")
        close_label.bind("<Button-1>", lambda _e: self.destroy())
        close_label.bind("<Enter>", lambda _e: close_label.configure(fg=theme.ERROR))
        close_label.bind("<Leave>", lambda _e: close_label.configure(fg=theme.INK))

        # --------------------------------------------------------------
        # MES PROJETS — récents uniquement.
        # --------------------------------------------------------------
        left = tk.Frame(screen, bg=panel, highlightthickness=1, highlightbackground=border)
        left.place(relx=0.105, rely=0.205, relwidth=0.345, relheight=0.61)
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(2, weight=1)

        left_head = tk.Frame(left, bg=panel)
        left_head.grid(row=0, column=0, sticky="ew", padx=28, pady=(18, 6))
        left_title = tk.Frame(left_head, bg=panel)
        left_title.pack(side="left")
        books_photo = self._tl_ui_icon("projects", 30, green, glow=True)
        books_icon = tk.Label(left_title, image=books_photo, bg=panel, bd=0)
        books_icon.image = books_photo
        books_icon.pack(side="left", padx=(0, 9))
        tk.Label(
            left_title, text="MES PROJETS", bg=panel, fg=theme.INK,
            font=(theme.FONT_UI, 11),
        ).pack(side="left")

        tk.Label(
            left, text="Récents", bg=panel, fg=theme.INK,
            font=(theme.FONT_UI, 8, "bold"),
        ).grid(row=1, column=0, sticky="w", padx=28, pady=(0, 8))

        self.home_recent_list = tk.Frame(left, bg=panel)
        self.home_recent_list.grid(row=2, column=0, sticky="nsew", padx=28)
        self.home_recent_list.grid_columnconfigure(0, weight=1)

        # Action indépendante des projets récents : même commande pour le
        # dossier TomeLinea, un autre disque ou un support externe.
        other = tk.Frame(left, bg=panel)
        other.grid(row=3, column=0, sticky="ew", padx=28, pady=(14, 22))
        other.grid_columnconfigure(0, weight=1)
        separator = tk.Frame(other, bg=border, height=1)
        separator.grid(row=0, column=0, sticky="ew", pady=(0, 11))
        tk.Label(
            other, text="AUTRE PROJET", bg=panel, fg=theme.MUTED_DARK,
            font=(theme.FONT_UI, 7, "bold"),
        ).grid(row=1, column=0, sticky="w", pady=(0, 6))
        open_other = tk.Frame(
            other, bg=panel_alt, highlightthickness=1,
            highlightbackground=border, cursor="hand2",
        )
        open_other.grid(row=2, column=0, sticky="ew", ipady=8)
        open_other.grid_columnconfigure(1, weight=1)
        search_photo = self._tl_ui_icon("search", 34, green, glow=True)
        open_icon = tk.Label(open_other, image=search_photo, bg=panel_alt, bd=0)
        open_icon.image = search_photo
        open_icon.grid(row=0, column=0, rowspan=2, padx=(14, 10))
        open_title = tk.Label(
            open_other, text="Chercher / ouvrir un autre projet", bg=panel_alt,
            fg=theme.INK, font=(theme.FONT_UI, 9, "bold"), anchor="w",
        )
        open_title.grid(row=0, column=1, sticky="ew", pady=(5, 0))
        open_sub = tk.Label(
            open_other, text="Dossier TomeLinea, autre disque ou support externe",
            bg=panel_alt, fg=theme.MUTED_DARK, font=(theme.FONT_UI, 7), anchor="w",
        )
        open_sub.grid(row=1, column=1, sticky="ew", pady=(1, 5))
        open_arrow = tk.Label(open_other, text="›", bg=panel_alt, fg=theme.MUTED, font=(theme.FONT_UI, 17))
        open_arrow.grid(row=0, column=2, rowspan=2, padx=(8, 13))
        for widget in (open_other, open_icon, open_title, open_sub, open_arrow):
            widget.bind("<Button-1>", lambda _e: self.open_existing_project())

        # --------------------------------------------------------------
        # DÉMARRER — un seul point d'entrée : Nouveau projet.
        # --------------------------------------------------------------
        right = tk.Frame(screen, bg=panel, highlightthickness=1, highlightbackground=border)
        right.place(relx=0.465, rely=0.205, relwidth=0.395, relheight=0.61)
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(2, weight=1)

        right_head = tk.Frame(right, bg=panel)
        right_head.grid(row=0, column=0, sticky="ew", padx=30, pady=(16, 6))
        right_head.grid_columnconfigure(1, weight=1)
        right_title = tk.Frame(right_head, bg=panel)
        right_title.grid(row=0, column=0, sticky="w")
        start_photo = self._tl_ui_icon("start", 30, green, glow=True)
        rocket_icon = tk.Label(right_title, image=start_photo, bg=panel, bd=0)
        rocket_icon.image = start_photo
        rocket_icon.pack(side="left", padx=(0, 9))
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
            right,
            text="Créez une nouvelle base éditoriale ou partez d’un projet modèle.",
            bg=panel, fg=theme.MUTED, font=(theme.FONT_UI, 9),
        ).grid(row=1, column=0, sticky="w", padx=30, pady=(10, 8))

        preview = tk.Frame(right, bg=panel)
        preview.grid(row=2, column=0, sticky="nsew", padx=30, pady=(8, 20))
        preview.grid_columnconfigure((0, 1, 2), weight=1, uniform="preview")
        preview.grid_rowconfigure(0, weight=1)
        for col, (key, title, accent) in enumerate((
            ("ouvrage_structure", "Livre de fiches", green),
            ("livre_textuel", "Livre textuel", purple),
            ("bande_dessinee", "Bande dessinée", orange),
        )):
            holder = tk.Frame(preview, bg=panel)
            holder.grid(row=0, column=col, sticky="nsew")
            icon = tk.Label(holder, bg=panel, bd=0)
            photo = self._home_type_icon_glow(key, 182, selected=False)
            if photo is not None:
                icon.configure(image=photo)
                icon.image = photo
            icon.pack(expand=True, pady=(0, 0))
            tk.Label(
                holder, text=title, bg=panel, fg=accent,
                font=(theme.FONT_UI, 10, "bold"),
            ).pack(pady=(0, 10))
        model_hint = tk.Frame(right, bg=panel)
        model_hint.grid(row=3, column=0, sticky="ew", padx=30, pady=(0, 22), ipady=5)
        model_photo = self._tl_ui_icon("model", 31, green, glow=True)
        model_icon = tk.Label(model_hint, image=model_photo, bg=panel, bd=0)
        model_icon.image = model_photo
        model_icon.pack(side="left", padx=(4, 10))
        tk.Label(
            model_hint, text="Ou repartir d’un modèle de projet déjà construit",
            bg=panel, fg=theme.MUTED, font=(theme.FONT_UI, 8),
        ).pack(side="left")

        # --------------------------------------------------------------
        # Créateur interne : visible uniquement après Nouveau projet.
        # --------------------------------------------------------------
        self._home_new_type_var = tk.StringVar(value="")
        self._home_new_origin_var = tk.StringVar(value="")
        self._home_new_name_var = tk.StringVar(value="")
        self._home_model_path_var = tk.StringVar(value="")
        self._home_type_frames = {}
        self._home_type_icon_labels = {}
        self._home_type_radios = {}
        self._home_models = []

        self.home_creator_frame = tk.Frame(
            right, bg=theme.PANEL_ALT, highlightthickness=1,
            highlightbackground=theme.ACCENT,
        )
        self.home_creator_frame.place_forget()
        self.home_creator_frame.grid_columnconfigure(0, weight=1)

        creator_head = tk.Frame(self.home_creator_frame, bg=theme.PANEL_ALT)
        creator_head.grid(row=0, column=0, sticky="ew", padx=18, pady=(13, 7))
        creator_head.grid_columnconfigure(0, weight=1)
        tk.Label(
            creator_head, text="NOUVEAU PROJET", bg=theme.PANEL_ALT,
            fg=theme.INK, font=(theme.FONT_TITLE, 14, "bold"),
        ).grid(row=0, column=0, sticky="w")
        close_creator = tk.Label(
            creator_head, text="×", bg=theme.PANEL_ALT, fg=theme.MUTED,
            font=(theme.FONT_UI, 16), cursor="hand2",
        )
        close_creator.grid(row=0, column=1, sticky="e")
        close_creator.bind("<Button-1>", lambda _e: self._home_hide_creator())
        tk.Label(
            self.home_creator_frame, text="Choisissez votre point de départ",
            bg=theme.PANEL_ALT, fg=theme.MUTED, font=(theme.FONT_UI, 8),
        ).grid(row=1, column=0, sticky="w", padx=18, pady=(0, 7))

        type_row = tk.Frame(self.home_creator_frame, bg=theme.PANEL_ALT)
        type_row.grid(row=2, column=0, sticky="ew", padx=18)
        for col in range(3):
            type_row.grid_columnconfigure(col, weight=1, uniform="home_create_types")
        type_data = {
            "ouvrage_structure": ("Livre de fiches", green),
            "livre_textuel": ("Livre textuel", purple),
            "bande_dessinee": ("Bande dessinée", orange),
        }
        for col, key in enumerate(("ouvrage_structure", "livre_textuel", "bande_dessinee")):
            title, accent = type_data[key]
            card = tk.Frame(
                type_row, bg=panel_alt, highlightthickness=1,
                highlightbackground=border, cursor="hand2",
            )
            card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 6, 0))
            card.grid_columnconfigure(0, weight=1)
            radio = tk.Canvas(card, width=18, height=18, bg=panel_alt, bd=0, highlightthickness=0)
            radio.grid(row=0, column=0, sticky="nw", padx=7, pady=(7, 0))
            self._home_type_radios[key] = radio
            icon = tk.Label(card, bg=panel_alt, bd=0)
            icon.grid(row=1, column=0)
            self._home_type_icon_labels[key] = icon
            title_label = tk.Label(
                card, text=title, bg=panel_alt, fg=accent,
                font=(theme.FONT_UI, 8, "bold"),
            )
            title_label.grid(row=2, column=0, pady=(0, 8))
            for widget in (card, radio, icon, title_label):
                widget.bind("<Button-1>", lambda _e, k=key: self._home_select_type(k))
            self._home_type_frames[key] = card

        or_row = tk.Frame(self.home_creator_frame, bg=theme.PANEL_ALT)
        or_row.grid(row=3, column=0, sticky="ew", padx=18, pady=(7, 6))
        or_row.grid_columnconfigure((0, 2), weight=1)
        tk.Frame(or_row, bg=border, height=1).grid(row=0, column=0, sticky="ew")
        tk.Label(or_row, text="  ou  ", bg=theme.PANEL_ALT, fg=theme.MUTED_DARK, font=(theme.FONT_UI, 7)).grid(row=0, column=1)
        tk.Frame(or_row, bg=border, height=1).grid(row=0, column=2, sticky="ew")

        model_card = tk.Frame(
            self.home_creator_frame, bg=panel_alt, highlightthickness=1,
            highlightbackground=border, cursor="hand2",
        )
        model_card.grid(row=4, column=0, sticky="ew", padx=18, ipady=5)
        model_card.grid_columnconfigure(1, weight=1)
        creator_model_photo = self._tl_ui_icon("model", 28, green, glow=True)
        model_icon = tk.Label(model_card, image=creator_model_photo, bg=panel_alt, bd=0)
        model_icon.image = creator_model_photo
        model_icon.grid(row=0, column=0, padx=(12, 9))
        model_title = tk.Label(
            model_card, text="Partir d’un projet modèle", bg=panel_alt,
            fg=theme.INK, font=(theme.FONT_UI, 9, "bold"), anchor="w",
        )
        model_title.grid(row=0, column=1, sticky="ew")
        model_arrow = tk.Label(model_card, text="›", bg=panel_alt, fg=theme.MUTED, font=(theme.FONT_UI, 15))
        model_arrow.grid(row=0, column=2, padx=(8, 12))
        for widget in (model_card, model_icon, model_title, model_arrow):
            widget.bind("<Button-1>", lambda _e: self._home_select_model_origin())
        self._home_model_card = model_card

        self.home_model_picker = tk.Frame(self.home_creator_frame, bg=theme.PANEL_ALT)
        self.home_model_picker.grid(row=5, column=0, sticky="ew", padx=18, pady=(5, 0))
        self.home_model_picker.grid_columnconfigure(0, weight=1)
        self._home_model_list = tk.Listbox(
            self.home_model_picker, height=3, exportselection=False,
            bg=theme.PANEL, fg=theme.INK, selectbackground=theme.ACCENT_DARK,
            selectforeground=theme.WHITE, relief="flat", bd=0,
            highlightthickness=1, highlightbackground=border,
            font=(theme.FONT_UI, 8),
        )
        self._home_model_list.grid(row=0, column=0, sticky="ew")
        self._home_model_list.bind("<<ListboxSelect>>", self._home_model_selected)
        self._home_model_status = tk.Label(
            self.home_model_picker, text="", bg=theme.PANEL_ALT,
            fg=theme.MUTED_DARK, font=(theme.FONT_UI, 7), anchor="w",
        )
        self._home_model_status.grid(row=1, column=0, sticky="ew", pady=(3, 0))
        self.home_model_picker.grid_remove()

        details = tk.Frame(self.home_creator_frame, bg=theme.PANEL_ALT)
        details.grid(row=6, column=0, sticky="ew", padx=18, pady=(8, 0))
        details.grid_columnconfigure(1, weight=1)
        tk.Label(
            details, text="Nom", bg=theme.PANEL_ALT, fg=theme.MUTED,
            font=(theme.FONT_UI, 8, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=(0, 8))
        name_entry = tk.Entry(
            details, textvariable=self._home_new_name_var,
            bg=theme.PANEL, fg=theme.INK, insertbackground=theme.INK,
            relief="flat", font=(theme.FONT_UI, 9),
        )
        name_entry.grid(row=0, column=1, sticky="ew", ipady=5)
        self._home_name_entry = name_entry
        tk.Label(
            details,
            text=f"Enregistrement automatique : {PROJECTS_HOME}",
            bg=theme.PANEL_ALT, fg=theme.MUTED_DARK,
            font=(theme.FONT_UI, 7), anchor="w",
        ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))

        tk.Label(
            self.home_creator_frame,
            text="Les sources de l’auteur seront proposées après la création du projet.",
            bg=theme.PANEL_ALT, fg=theme.MUTED_DARK,
            font=(theme.FONT_UI, 7), anchor="w",
        ).grid(row=7, column=0, sticky="ew", padx=18, pady=(8, 0))

        actions = tk.Frame(self.home_creator_frame, bg=theme.PANEL_ALT)
        actions.grid(row=8, column=0, sticky="ew", padx=18, pady=(9, 14))
        actions.grid_columnconfigure(0, weight=1)
        V3Button(actions, "Annuler", self._home_hide_creator, compact=True).grid(row=0, column=1, padx=(0, 7))
        V3Button(
            actions, "Créer le projet", self._home_create_project_inline,
            primary=True, compact=True,
        ).grid(row=0, column=2)

        # --------------------------------------------------------------
        # Citation basse
        # --------------------------------------------------------------
        quote = tk.Frame(screen, bg=theme.WINDOW_DEEP)
        quote.place(relx=0.31, rely=0.845, relwidth=0.39, relheight=0.09)
        tk.Label(
            quote, text="“  Chaque idée a sa forme.  ”",
            bg=theme.WINDOW_DEEP, fg=theme.MUTED,
            font=(theme.FONT_TITLE, 12, "italic"),
        ).pack()
        tk.Label(
            quote, text="TomeLinea vous accompagne de la première ligne au livre terminé.",
            bg=theme.WINDOW_DEEP, fg=theme.MUTED_DARK,
            font=(theme.FONT_UI, 8),
        ).pack(pady=(4, 0))
        tk.Frame(quote, bg=theme.ACCENT_DARK, height=1, width=250).pack(pady=(9, 0))

        self._home_refresh_type_cards()
        self._refresh_home_recent()

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
        self.zone_b_info = tk.Label(
            self.zone_b.body, text="ⓘ", bg=theme.PANEL, fg=theme.MUTED,
            font=(theme.FONT_UI, 11, "bold"), cursor="hand2", padx=5, pady=2,
        )
        self.zone_b_info.place(relx=1.0, x=-8, y=7, anchor="ne")
        self.zone_b_info.bind("<Button-1>", lambda _e: self._show_zone_info("b"))
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
            left, textvariable=self.project_name_var, bg=theme.PANEL,
            fg=theme.INK, font=(theme.FONT_TITLE, 14, "bold"),
        ).pack(anchor="w")
        tk.Label(
            left, textvariable=self.project_meta_var, bg=theme.PANEL,
            fg=theme.ACCENT_BRIGHT, font=(theme.FONT_UI, 8, "bold"),
        ).pack(anchor="w", pady=(3, 0))

        status = tk.Frame(body, bg=theme.PANEL)
        status.grid(row=0, column=1, sticky="nsew", padx=(35, 20))
        self.project_status_var = tk.StringVar(value="")
        tk.Label(
            status, textvariable=self.project_status_var, bg=theme.PANEL,
            fg=theme.MUTED, font=(theme.FONT_UI, 9), anchor="w",
        ).pack(fill="both", expand=True)

        actions = tk.Frame(body, bg=theme.PANEL)
        actions.grid(row=0, column=2, sticky="e")
        info = tk.Label(
            actions, text="ⓘ", bg=theme.PANEL, fg=theme.MUTED,
            font=(theme.FONT_UI, 11, "bold"), cursor="hand2", padx=6,
        )
        info.pack(side="left", padx=(0, 3))
        info.bind("<Button-1>", lambda _e: self._show_zone_info("a"))
        V3Button(actions, "Aide", self._show_general_help, compact=True).pack(side="left", padx=3)
        V3Button(actions, "Accueil", self.show_home, compact=True).pack(side="left", padx=3)
        V3Button(actions, "Importer", self.import_sources, compact=True).pack(side="left", padx=3)
        V3Button(actions, "Annuler", None, compact=True, state="disabled").pack(side="left", padx=3)
        V3Button(actions, "Rétablir", None, compact=True, state="disabled").pack(side="left", padx=3)
        V3Button(actions, "Fermer", self.destroy, compact=True).pack(side="left", padx=(10, 0))

    def _build_zone_c(self):
        body = self.zone_c.body
        body.grid_rowconfigure(1, weight=1)
        body.grid_columnconfigure(0, weight=1)

        self.tab_bar = tk.Frame(body, bg=theme.PANEL)
        self.tab_bar.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.tab_buttons: dict[str, tk.Button] = {}
        for index, (key, label) in enumerate(theme.TAB_NAMES):
            button = tk.Button(
                self.tab_bar, text=label, command=lambda k=key: self.select_tab(k),
                bg=theme.PANEL_SOFT, fg=theme.INK,
                activebackground=theme.ACCENT_SOFT, activeforeground=theme.WHITE,
                relief="flat", bd=0, padx=22, pady=7,
                font=(theme.FONT_UI, 9, "bold"), cursor="hand2",
            )
            button.pack(side="left", padx=(0 if index == 0 else 4, 0))
            self.tab_buttons[key] = button

        info = tk.Label(
            self.tab_bar, text="ⓘ", bg=theme.PANEL, fg=theme.MUTED,
            font=(theme.FONT_UI, 11, "bold"), cursor="hand2", padx=6,
        )
        info.pack(side="right")
        info.bind("<Button-1>", lambda _e: self._show_zone_info("c"))
        tk.Label(
            self.tab_bar, text="A et B restent fixes — seuls les outils changent",
            bg=theme.PANEL, fg=theme.MUTED_DARK, font=(theme.FONT_UI, 8),
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
        """Structure V6 : C fournit les outils ; B est l'unique zone de construction."""
        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=0, minsize=88)
        parent.grid_columnconfigure(1, weight=1)

        rail = tk.Frame(parent, bg=theme.PANEL_ALT, width=88, padx=5, pady=6)
        rail.grid(row=0, column=0, sticky="nsw", padx=(0, 7))
        rail.grid_propagate(False)

        tk.Label(
            rail, text="STRUCTURE", bg=theme.PANEL_ALT, fg=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 7, "bold"),
        ).pack(anchor="w", padx=2, pady=(0, 5))

        palette = tk.Frame(parent, bg=theme.PANEL_ALT, padx=9, pady=6)
        palette.grid(row=0, column=1, sticky="nsew")
        palette.grid_rowconfigure(2, weight=1)
        palette.grid_columnconfigure(0, weight=1)

        def book():
            return getattr(self, "book_canvas", None)

        def close_structure_modal():
            overlay = getattr(self, "_structure_modal_overlay", None)
            if overlay is not None:
                try:
                    overlay.destroy()
                except Exception:
                    pass
            self._structure_modal_overlay = None
            self._structure_modal_bg_ref = None
            self._structure_modal_brand_refs = []

        def show_structure_modal(
            title: str,
            *,
            message: str = "",
            confirm_label: str = "Valider",
            on_confirm=None,
            danger: bool = False,
            body_builder=None,
            width: int = 760,
            height: int = 470,
        ):
            """Fenêtre TomeLinea intégrée, habillée comme la visionneuse."""
            close_structure_modal()

            host = getattr(self, "stack", self)
            overlay = tk.Canvas(host, bg=theme.WINDOW_DEEP, bd=0, highlightthickness=0)
            overlay.place(x=0, y=0, relwidth=1, relheight=1)
            overlay.lift()
            self._structure_modal_overlay = overlay
            self._structure_modal_brand_refs = []

            width_host = max(600, host.winfo_width() or self.winfo_width() or 1280)
            height_host = max(420, host.winfo_height() or self.winfo_height() or 720)
            bg_photo = None
            background_factory = getattr(self, "_background_photo", None)
            if callable(background_factory):
                try:
                    bg_photo = background_factory(int(width_host), int(height_host), "workspace")
                except Exception:
                    bg_photo = None
            self._structure_modal_bg_ref = bg_photo
            if bg_photo is not None:
                overlay.create_image(0, 0, image=bg_photo, anchor="nw")
            else:
                overlay.create_rectangle(0, 0, width_host, height_host, fill=theme.WINDOW_DEEP, outline="")
            overlay.create_rectangle(0, 0, width_host, height_host, fill="#0E141A", stipple="gray50", outline="")

            brand_root = PROJECT_ROOT / "assets" / "branding" / "tomelinea" / "logo_pack_visibilite"
            try:
                icon_path = brand_root / "TomeLinea_512x512.png"
                with Image.open(icon_path) as src:
                    image = src.convert("RGBA")
                    image.thumbnail((44, 44), Image.Resampling.LANCZOS)
                    icon = ImageTk.PhotoImage(image)
                self._structure_modal_brand_refs.append(icon)
                overlay.create_image(width_host * 0.5 - 150, 36, image=icon, anchor="center")
            except Exception:
                pass
            overlay.create_text(
                width_host * 0.5 + 20, 34,
                text="TomeLinea", fill=theme.INK,
                font=(theme.FONT_TITLE, 22, "bold"), anchor="center"
            )
            overlay.create_text(
                width_host * 0.5 + 22, 58,
                text="LA LIGNE ÉDITORIALE JUSQU’AU LIVRE",
                fill=theme.MUTED_DARK, font=(theme.FONT_UI, 8, "bold"), anchor="center"
            )

            card = tk.Frame(
                overlay, bg=theme.PANEL_ALT, bd=0,
                highlightthickness=1, highlightbackground=theme.BORDER,
            )
            card.place(relx=0.5, rely=0.53, anchor="center", width=width, height=height)
            card.grid_columnconfigure(0, weight=1)
            card.grid_rowconfigure(2, weight=1)

            head = tk.Frame(card, bg=theme.PANEL_ALT)
            head.grid(row=0, column=0, sticky="ew", padx=22, pady=(16, 8))
            head.grid_columnconfigure(0, weight=1)
            tk.Label(
                head, text=title, bg=theme.PANEL_ALT, fg=theme.INK,
                font=(theme.FONT_TITLE, 14, "bold"),
            ).grid(row=0, column=0, sticky="w")
            close = tk.Label(
                head, text="×", bg=theme.PANEL_ALT, fg=theme.MUTED,
                font=(theme.FONT_UI, 18, "bold"), cursor="hand2",
            )
            close.grid(row=0, column=1, sticky="e")
            close.bind("<Button-1>", lambda _e: close_structure_modal())

            tk.Frame(card, bg=theme.ACCENT_DARK, height=1).grid(
                row=1, column=0, sticky="ew", padx=22
            )

            body = tk.Frame(card, bg=theme.PANEL_ALT)
            body.grid(row=2, column=0, sticky="nsew", padx=22, pady=14)
            body.grid_columnconfigure(0, weight=1)
            body.grid_rowconfigure(0, weight=1)

            if message:
                tk.Label(
                    body, text=message, bg=theme.PANEL_ALT, fg=theme.INK,
                    justify="left", anchor="w", wraplength=max(260, width - 90),
                    font=(theme.FONT_UI, 9),
                ).grid(row=0, column=0, sticky="ew", pady=(0, 10))

            if body_builder is not None:
                body_builder(body)

            foot = tk.Frame(card, bg=theme.PANEL_ALT)
            foot.grid(row=3, column=0, sticky="ew", padx=22, pady=(8, 16))
            foot.grid_columnconfigure(0, weight=1)

            tk.Button(
                foot, text="Annuler", command=close_structure_modal,
                bg=theme.PANEL_SOFT, fg=theme.INK,
                activebackground=theme.ACCENT_SOFT, activeforeground=theme.WHITE,
                relief="flat", bd=0, padx=16, pady=7,
                font=(theme.FONT_UI, 8, "bold"), cursor="hand2",
            ).grid(row=0, column=1, padx=(0, 8))

            def confirm():
                if on_confirm is None:
                    close_structure_modal()
                    return
                keep_open = bool(on_confirm())
                if not keep_open:
                    close_structure_modal()

            tk.Button(
                foot, text=confirm_label, command=confirm,
                bg="#6A3029" if danger else theme.ACCENT_DARK,
                fg=theme.WHITE,
                activebackground="#8B4036" if danger else theme.ACCENT_SOFT,
                activeforeground=theme.WHITE,
                relief="flat", bd=0, padx=18, pady=7,
                font=(theme.FONT_UI, 8, "bold"), cursor="hand2",
            ).grid(row=0, column=2)

            overlay.bind("<Escape>", lambda _e: close_structure_modal())
            overlay.focus_set()
            return body

        action_bar = tk.Frame(palette, bg=theme.PANEL_ALT)
        action_bar.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        tk.Label(
            action_bar, text="Sélection dans B", bg=theme.PANEL_ALT, fg=theme.MUTED,
            font=(theme.FONT_UI, 7, "bold"),
        ).pack(side="left", padx=(0, 7))

        def rename_selected():
            canvas = book()
            if canvas is not None and hasattr(canvas, "structure_rename_selected"):
                canvas.structure_rename_selected()

        def duplicate_selected():
            canvas = book()
            if canvas is not None and hasattr(canvas, "structure_duplicate_selected"):
                canvas.structure_duplicate_selected()

        def delete_selected():
            canvas = book()
            if canvas is None or not hasattr(canvas, "structure_delete_selected"):
                return
            def confirmed():
                canvas.structure_delete_selected()
                return False
            show_structure_modal(
                "Supprimer l’élément",
                message=(
                    "Supprimer l’élément sélectionné ?\n\n"
                    "Les couvertures et les parties contenant encore des pages restent protégées."
                ),
                confirm_label="Supprimer",
                on_confirm=confirmed,
                danger=True,
                width=580,
                height=300,
            )

        def cancel_tool():
            canvas = book()
            if canvas is not None and hasattr(canvas, "structure_cancel_tool"):
                canvas.structure_cancel_tool()

        for text, command in (
            ("Nommer", rename_selected),
            ("Dupliquer", duplicate_selected),
            ("Supprimer", delete_selected),
            ("Annuler outil", cancel_tool),
        ):
            tk.Button(
                action_bar, text=text, command=command,
                bg=theme.PANEL_SOFT, fg=theme.INK,
                activebackground=theme.ACCENT_SOFT, activeforeground=theme.WHITE,
                relief="flat", bd=0, padx=9, pady=4,
                font=(theme.FONT_UI, 7, "bold"), cursor="hand2",
            ).pack(side="left", padx=(0, 5))

        palette_head = tk.Frame(palette, bg=theme.PANEL_ALT)
        palette_head.grid(row=1, column=0, sticky="ew", pady=(0, 5))
        palette_head.grid_columnconfigure(2, weight=1)
        palette_title_var = tk.StringVar(value="Pages")
        palette_hint_var = tk.StringVar(
            value="Clic : choisir la brique  •  les + apparaissent dans B  •  glisser sur une page : remplacer"
        )
        tk.Label(
            palette_head, textvariable=palette_title_var,
            bg=theme.PANEL_ALT, fg=theme.INK,
            font=(theme.FONT_TITLE, 10, "bold"),
        ).grid(row=0, column=0, sticky="w")
        head_action_slot = tk.Frame(palette_head, bg=theme.PANEL_ALT)
        head_action_slot.grid(row=0, column=1, sticky="w", padx=(10, 0))
        tk.Label(
            palette_head, textvariable=palette_hint_var,
            bg=theme.PANEL_ALT, fg=theme.MUTED_DARK,
            font=(theme.FONT_UI, 7),
        ).grid(row=0, column=2, sticky="e")

        palette_body = tk.Frame(palette, bg=theme.PANEL_ALT)
        palette_body.grid(row=2, column=0, sticky="nsew")

        family_buttons: dict[str, tk.Button] = {}
        current_family = {"name": "Pages"}

        def arm(kind: str, payload):
            canvas = book()
            if canvas is not None and hasattr(canvas, "structure_arm_tool"):
                canvas.structure_arm_tool(kind, payload)

        def external_drop(kind: str, payload, event) -> bool:
            canvas = book()
            if canvas is None or not hasattr(canvas, "structure_drop_from_root"):
                return False
            return bool(canvas.structure_drop_from_root(kind, payload, event.x_root, event.y_root))

        def make_brick(parent_, label: str, kind: str, payload, *, accent=False):
            btn = tk.Button(
                parent_, text=label,
                bg=theme.ACCENT_DARK if accent else theme.PANEL_SOFT,
                fg=theme.WHITE if accent else theme.INK,
                activebackground=theme.ACCENT_SOFT,
                activeforeground=theme.WHITE,
                relief="flat", bd=0,
                padx=12, pady=8,
                font=(theme.FONT_UI, 8, "bold"),
                cursor="hand2",
            )
            drag = {"x": 0, "y": 0, "moved": False}
            def press(event):
                drag["x"], drag["y"], drag["moved"] = event.x_root, event.y_root, False
                btn.configure(relief="sunken")
                return "break"
            def motion(event):
                if abs(event.x_root - drag["x"]) > 5 or abs(event.y_root - drag["y"]) > 5:
                    drag["moved"] = True
                return "break"
            def release(event):
                btn.configure(relief="flat")
                if drag["moved"] and external_drop(kind, payload, event):
                    return "break"
                arm(kind, payload)
                return "break"
            btn.bind("<ButtonPress-1>", press)
            btn.bind("<B1-Motion>", motion)
            btn.bind("<ButtonRelease-1>", release)
            return btn

        def small_action(parent_, label: str, command, *, danger=False):
            return tk.Button(
                parent_, text=label, command=command,
                bg=theme.PANEL_SOFT,
                fg="#E4876E" if danger else theme.INK,
                activebackground=theme.ACCENT_SOFT,
                activeforeground=theme.WHITE,
                relief="flat", bd=0, padx=10, pady=7,
                font=(theme.FONT_UI, 8, "bold"), cursor="hand2",
            )

        def page_types():
            canvas = book()
            if canvas is not None and hasattr(canvas, "structure_available_page_types"):
                return canvas.structure_available_page_types()
            return [
                ("page_titre", "Page de titre", False),
                ("sommaire", "Sommaire", False),
                ("avant_propos", "Avant-propos", False),
                ("chapitre", "Chapitre", False),
                ("texte", "Texte", False),
                ("illustration", "Illustration", False),
                ("fiche", "Fiche", False),
                ("transition", "Transition", False),
                ("conclusion", "Conclusion", False),
            ]

        def type_catalog():
            defaults = [
                ("couverture", "Couverture"),
                ("deuxieme_couverture", "2e de couverture"),
                ("troisieme_couverture", "3e de couverture"),
                ("quatrieme_couverture", "4e de couverture"),
                ("page_blanche", "Page blanche"),
            ]
            seen = {key for key, _ in defaults}
            for key, label, _custom in page_types():
                if key not in seen:
                    defaults.append((key, label))
                    seen.add(key)
            return defaults

        thumbnail_refs = []
        def thumbnail_for_type(type_key: str, definition: dict | None = None) -> object | None:
            mapping = {
                "couverture": "type_page_couverture.png",
                "deuxieme_couverture": "type_page_deuxieme_couverture.png",
                "troisieme_couverture": "type_page_troisieme_couverture.png",
                "quatrieme_couverture": "type_page_quatrieme_couverture.png",
                "page_blanche": "type_page_blanche.png",
                "page_titre": "type_page_titre.png",
                "sommaire": "type_page_sommaire.png",
                "avant_propos": "type_page_avant_propos.png",
                "tete_partie": "type_page_chapitre.png",
                "chapitre": "type_page_chapitre.png",
                "texte": "type_page_texte.png",
                "illustration": "type_page_illustration.png",
                "fiche": "type_page_fiche.png",
                "transition": "type_page_transition.png",
                "annexe": "type_page_illustration.png",
                "conclusion": "type_page_conclusion.png",
                "remerciements": "type_page_titre.png",
            }
            candidate = None
            if isinstance(definition, dict):
                preview = str(definition.get("preview_image") or "").strip()
                if preview:
                    path = Path(preview)
                    if not path.is_absolute():
                        project_root = None
                        canvas = book()
                        if canvas is not None and getattr(canvas, "project", None) is not None:
                            project_root = Path(getattr(canvas.project, "root", "") or "")
                        path = (project_root / preview) if project_root else (PROJECT_ROOT / preview)
                    if path.is_file():
                        candidate = path
            if candidate is None:
                filename = mapping.get(type_key)
                if filename:
                    path = PROJECT_ROOT / "assets" / "page_thumbnails" / filename
                    if path.is_file():
                        candidate = path
            if candidate is None:
                return None
            try:
                with Image.open(candidate) as img:
                    image = img.convert("RGBA")
                    image.thumbnail((78, 112), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                thumbnail_refs.append(photo)
                return photo
            except Exception:
                return None

        def bind_click_drag(widget, kind: str, payload, press_visual=None, release_visual=None):
            drag = {"x": 0, "y": 0, "moved": False}
            def press(event):
                drag["x"], drag["y"], drag["moved"] = event.x_root, event.y_root, False
                if callable(press_visual):
                    press_visual()
                return "break"
            def motion(event):
                if abs(event.x_root - drag["x"]) > 5 or abs(event.y_root - drag["y"]) > 5:
                    drag["moved"] = True
                return "break"
            def release(event):
                if callable(release_visual):
                    release_visual()
                if drag["moved"] and external_drop(kind, payload, event):
                    return "break"
                arm(kind, payload)
                return "break"
            for target in (widget, *widget.winfo_children()):
                target.bind("<ButtonPress-1>", press)
                target.bind("<B1-Motion>", motion)
                target.bind("<ButtonRelease-1>", release)
                target.configure(cursor="hand2")

        def make_type_card(parent_, label: str, kind: str, payload, definition: dict | None = None):
            card = tk.Frame(parent_, bg="#254239", highlightthickness=1, highlightbackground="#39584D", padx=8, pady=8)
            preview = tk.Label(card, bg="#DCE5DF", width=78, height=112)
            photo = thumbnail_for_type(str(payload.get("type") or ""), definition)
            if photo is not None:
                preview.configure(image=photo)
                preview.image = photo
            else:
                preview.configure(text=label[:18], fg=theme.ACCENT_DARK, font=(theme.FONT_UI, 8, "bold"), wraplength=70, justify="center")
            preview.pack(anchor="n")
            tk.Label(card, text=label, bg="#254239", fg=theme.WHITE, font=(theme.FONT_UI, 8, "bold"), wraplength=120, justify="center").pack(fill="x", pady=(6, 1))
            tk.Label(card, text="type de page", bg="#254239", fg="#9CC9B8", font=(theme.FONT_UI, 7)).pack(fill="x")
            def press_visual():
                card.configure(bg="#2E5448", highlightbackground=theme.ACCENT_BRIGHT)
                for child in card.winfo_children():
                    try: child.configure(bg="#2E5448")
                    except Exception: pass
            def release_visual():
                card.configure(bg="#254239", highlightbackground="#39584D")
                for child in card.winfo_children():
                    try:
                        if child is preview:
                            child.configure(bg="#DCE5DF")
                        else:
                            child.configure(bg="#254239")
                    except Exception:
                        pass
            bind_click_drag(card, kind, payload, press_visual, release_visual)
            return card

        def create_custom_type():
            canvas = book()
            if canvas is None or not hasattr(canvas, "structure_create_custom_type"):
                return
            state = {
                "visual": tk.StringVar(value="custom"),
                "duplicable": tk.BooleanVar(value=True),
                "image_mode": tk.StringVar(value="none"),
                "preview_image": None,
                "library_frame": None,
            }
            entries = {}
            preview_refs = []
            selected_image_var = tk.StringVar(value="Aucune image")

            def make_preview_photo(path: Path | None):
                if path is None or not path.is_file():
                    return None
                try:
                    with Image.open(path) as img:
                        image = img.convert("RGBA")
                        image.thumbnail((190, 270), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(image)
                    preview_refs.append(photo)
                    return photo
                except Exception:
                    return None

            def library_candidates() -> list[tuple[str, Path]]:
                folder = PROJECT_ROOT / "assets" / "page_thumbnails"
                labels = {
                    "type_page_couverture.png": "Couverture",
                    "type_page_deuxieme_couverture.png": "2e de couverture",
                    "type_page_troisieme_couverture.png": "3e de couverture",
                    "type_page_quatrieme_couverture.png": "4e de couverture",
                    "type_page_sommaire.png": "Sommaire",
                    "type_page_chapitre.png": "Chapitre",
                    "type_page_titre.png": "Page de titre",
                    "type_page_texte.png": "Texte",
                    "type_page_illustration.png": "Illustration",
                    "type_page_fiche.png": "Fiche",
                    "type_page_transition.png": "Transition",
                    "type_page_blanche.png": "Page blanche",
                    "type_page_conclusion.png": "Conclusion",
                    "type_page_avant_propos.png": "Avant-propos",
                }
                found = []
                for filename, label in labels.items():
                    path = folder / filename
                    if path.is_file():
                        found.append((label, path))
                return found

            def build_body(body):
                body.grid_columnconfigure(0, weight=0, minsize=240)
                body.grid_columnconfigure(1, weight=1)
                body.grid_rowconfigure(0, weight=1)

                preview_box = tk.Frame(body, bg=theme.WINDOW_DEEP, highlightthickness=1, highlightbackground=theme.BORDER)
                preview_box.grid(row=0, column=0, sticky="nsw", padx=(0, 18))
                tk.Label(preview_box, text="Aperçu dans B", bg=theme.WINDOW_DEEP, fg=theme.ACCENT_BRIGHT, font=(theme.FONT_UI, 8, "bold")).pack(anchor="w", padx=10, pady=(10, 4))
                preview_label = tk.Label(preview_box, bg="#EEF1EC", width=190, height=270)
                preview_label.pack(padx=10, pady=(0, 10))
                preview_text = tk.Label(preview_box, text="Nouveau type", bg=theme.WINDOW_DEEP, fg=theme.INK, font=(theme.FONT_TITLE, 11, "bold"))
                preview_text.pack(anchor="center", pady=(0, 4))
                preview_sub = tk.Label(preview_box, text="Type de page", bg=theme.WINDOW_DEEP, fg=theme.MUTED, font=(theme.FONT_UI, 8))
                preview_sub.pack(anchor="center", pady=(0, 12))

                def refresh_preview(*_args):
                    label = entries.get("short").get().strip() if entries.get("short") and entries.get("short").get().strip() else (entries.get("name").get().strip() if entries.get("name") else "")
                    preview_text.configure(text=label or "Nouveau type")
                    photo = make_preview_photo(state.get("preview_image"))
                    if photo is not None:
                        preview_label.configure(image=photo, text="")
                        preview_label.image = photo
                    else:
                        preview_label.configure(image="", text=(label or "TYPE"), fg=theme.ACCENT_DARK, font=(theme.FONT_UI, 13, "bold"))
                        preview_label.image = None

                form = tk.Frame(body, bg=theme.PANEL_ALT)
                form.grid(row=0, column=1, sticky="nsew")
                form.grid_columnconfigure(1, weight=1)

                def field(row, label, key, initial=""):
                    tk.Label(form, text=label, bg=theme.PANEL_ALT, fg=theme.MUTED, font=(theme.FONT_UI, 8, "bold")).grid(row=row, column=0, sticky="w", padx=(0, 12), pady=5)
                    entry = tk.Entry(form, bg=theme.WINDOW_DEEP, fg=theme.INK, insertbackground=theme.ACCENT_BRIGHT, relief="flat", bd=0, font=(theme.FONT_UI, 9))
                    entry.insert(0, initial)
                    entry.grid(row=row, column=1, sticky="ew", pady=5, ipady=6)
                    entry.bind("<KeyRelease>", refresh_preview)
                    entries[key] = entry

                field(0, "Nom du type", "name")
                field(1, "Libellé court", "short")

                tk.Label(form, text="Image de base", bg=theme.PANEL_ALT, fg=theme.MUTED, font=(theme.FONT_UI, 8, "bold")).grid(row=2, column=0, sticky="nw", padx=(0, 12), pady=(10, 5))
                image_box = tk.Frame(form, bg=theme.PANEL_ALT)
                image_box.grid(row=2, column=1, sticky="ew", pady=(10, 5))
                image_box.grid_columnconfigure(0, weight=1)
                controls = tk.Frame(image_box, bg=theme.PANEL_ALT)
                controls.grid(row=0, column=0, sticky="w")

                def choose_none():
                    state["image_mode"].set("none")
                    state["preview_image"] = None
                    selected_image_var.set("Aucune image")
                    refresh_preview()
                    if state.get("library_frame") is not None:
                        state["library_frame"].grid_remove()

                def choose_library():
                    state["image_mode"].set("library")
                    if state.get("library_frame") is not None:
                        state["library_frame"].grid()

                def choose_external():
                    filename = filedialog.askopenfilename(
                        title="Choisir une image de base",
                        filetypes=[("Images", "*.png *.jpg *.jpeg *.webp *.bmp")],
                    )
                    if not filename:
                        return
                    state["image_mode"].set("external")
                    state["preview_image"] = Path(filename)
                    selected_image_var.set(Path(filename).name)
                    refresh_preview()
                    if state.get("library_frame") is not None:
                        state["library_frame"].grid_remove()

                for txt, cmd in (("Aucune", choose_none), ("Bibliothèque", choose_library), ("Image externe", choose_external)):
                    tk.Button(
                        controls, text=txt, command=cmd,
                        bg=theme.PANEL_SOFT, fg=theme.INK,
                        activebackground=theme.ACCENT_SOFT, activeforeground=theme.WHITE,
                        relief="flat", bd=0, padx=10, pady=6,
                        font=(theme.FONT_UI, 8, "bold"), cursor="hand2",
                    ).pack(side="left", padx=(0, 5))
                tk.Label(image_box, textvariable=selected_image_var, bg=theme.PANEL_ALT, fg=theme.MUTED_DARK, font=(theme.FONT_UI, 8)).grid(row=1, column=0, sticky="w", pady=(6, 0))

                lib_holder = tk.Frame(image_box, bg=theme.WINDOW_DEEP, highlightthickness=1, highlightbackground=theme.BORDER)
                lib_holder.grid(row=2, column=0, sticky="ew", pady=(8, 0))
                state["library_frame"] = lib_holder
                tk.Label(lib_holder, text="Bibliothèque TomeLinea", bg=theme.WINDOW_DEEP, fg=theme.ACCENT_BRIGHT, font=(theme.FONT_UI, 8, "bold")).pack(anchor="w", padx=8, pady=(8, 4))
                lib_inner = tk.Frame(lib_holder, bg=theme.WINDOW_DEEP)
                lib_inner.pack(fill="x", padx=8, pady=(0, 8))
                row = 0
                col = 0
                for title, path in library_candidates():
                    btn = tk.Frame(lib_inner, bg=theme.PANEL_SOFT, highlightthickness=1, highlightbackground=theme.BORDER, padx=5, pady=5)
                    btn.grid(row=row, column=col, padx=4, pady=4, sticky="nsew")
                    photo = make_preview_photo(path)
                    if photo is not None:
                        lbl = tk.Label(btn, image=photo, bg=theme.PANEL_SOFT)
                        lbl.image = photo
                        lbl.pack()
                    tk.Label(btn, text=title, bg=theme.PANEL_SOFT, fg=theme.INK, font=(theme.FONT_UI, 7, "bold"), wraplength=82, justify="center").pack(pady=(4,0))
                    def select_lib(_e=None, p=path, t=title):
                        state["preview_image"] = p
                        selected_image_var.set(t)
                        refresh_preview()
                    for target in (btn, *btn.winfo_children()):
                        target.bind("<Button-1>", select_lib)
                        target.configure(cursor="hand2")
                    col += 1
                    if col >= 4:
                        col = 0
                        row += 1
                lib_holder.grid_remove()

                tk.Label(form, text="Comportement", bg=theme.PANEL_ALT, fg=theme.MUTED, font=(theme.FONT_UI, 8, "bold")).grid(row=3, column=0, sticky="nw", padx=(0, 12), pady=(12, 5))
                options = tk.Frame(form, bg=theme.PANEL_ALT)
                options.grid(row=3, column=1, sticky="w", pady=(12, 5))
                tk.Checkbutton(
                    options, text="Ce type peut être dupliqué",
                    variable=state["duplicable"], bg=theme.PANEL_ALT, fg=theme.INK,
                    activebackground=theme.PANEL_ALT, activeforeground=theme.INK,
                    selectcolor=theme.WINDOW_DEEP, font=(theme.FONT_UI, 8), cursor="hand2",
                ).pack(side="left")
                tk.Label(
                    form, text="Le type créé devient immédiatement une brique réutilisable dans Structure.",
                    bg=theme.PANEL_ALT, fg=theme.MUTED_DARK, font=(theme.FONT_UI, 7), anchor="w",
                ).grid(row=4, column=1, sticky="w", pady=(8, 0))
                entries["name"].focus_set()
                refresh_preview()

            def confirm_new_type():
                name = entries.get("name").get().strip() if entries.get("name") else ""
                short = entries.get("short").get().strip() if entries.get("short") else ""
                if not name:
                    if entries.get("name") is not None:
                        entries["name"].configure(highlightthickness=1, highlightbackground="#A94F43")
                        entries["name"].focus_set()
                    return True
                created = canvas.structure_create_custom_type({
                    "name": name,
                    "short_label": short or name,
                    "visual": state["visual"].get(),
                    "duplicable": bool(state["duplicable"].get()),
                    "preview_image": str(state["preview_image"]) if state.get("preview_image") else "",
                })
                if not created:
                    return True
                self.after_idle(lambda: select_family("Types"))
                return False

            show_structure_modal(
                "Nouveau type de page",
                confirm_label="Créer le type",
                on_confirm=confirm_new_type,
                body_builder=build_body,
                width=920,
                height=560,
            )

        def insert_blank_relative(position: str):
            canvas = book()
            if canvas is not None and hasattr(canvas, "structure_insert_blank_relative"):
                canvas.structure_insert_blank_relative(position)

        def clear_head_actions():
            for child in head_action_slot.winfo_children():
                child.destroy()

        def clear_palette_body():
            for child in palette_body.winfo_children():
                child.destroy()

        def build_type_scroll_area(items: list[tuple[str, str]]):
            holder = tk.Frame(palette_body, bg=theme.PANEL_ALT)
            holder.pack(fill="both", expand=True)
            canvas_widget = tk.Canvas(holder, bg=theme.PANEL_ALT, bd=0, highlightthickness=0)
            vscroll = tk.Scrollbar(holder, orient="vertical", command=canvas_widget.yview)
            inner = tk.Frame(canvas_widget, bg=theme.PANEL_ALT)
            window_id = canvas_widget.create_window((0, 0), window=inner, anchor="nw")
            canvas_widget.configure(yscrollcommand=vscroll.set)
            canvas_widget.pack(side="left", fill="both", expand=True)
            vscroll.pack(side="right", fill="y")

            def on_inner_config(_e=None):
                canvas_widget.configure(scrollregion=canvas_widget.bbox("all"))
            inner.bind("<Configure>", on_inner_config)
            def on_canvas_config(event):
                canvas_widget.itemconfigure(window_id, width=event.width)
            canvas_widget.bind("<Configure>", on_canvas_config)
            def on_mousewheel(event):
                canvas_widget.yview_scroll(int(-1 * (event.delta / 120)), "units")
                return "break"
            def bind_wheel(widget):
                widget.bind("<MouseWheel>", on_mousewheel)
                for child in widget.winfo_children():
                    bind_wheel(child)
            columns = 5
            row = col = 0
            canvas_obj = book()
            for type_key, label in items:
                definition = None
                if canvas_obj is not None and hasattr(canvas_obj, "_structure_type_definition"):
                    try:
                        definition = canvas_obj._structure_type_definition(type_key)
                    except Exception:
                        definition = None
                card = make_type_card(inner, label, "page", {"type": type_key, "label": label}, definition)
                card.grid(row=row, column=col, padx=6, pady=6, sticky="n")
                col += 1
                if col >= columns:
                    col = 0
                    row += 1
            bind_wheel(holder)

        def select_family(name: str):
            current_family["name"] = name
            palette_title_var.set(name)
            clear_head_actions()
            clear_palette_body()
            thumbnail_refs.clear()
            for family, button in family_buttons.items():
                active = family == name
                button.configure(
                    bg=theme.ACCENT_DARK if active else theme.PANEL_SOFT,
                    fg=theme.WHITE if active else theme.INK,
                )
            row = tk.Frame(palette_body, bg=theme.PANEL_ALT)

            if name == "Pages":
                row.pack(anchor="nw", fill="x")
                make_brick(row, "Page sans type", "page", {"type": "", "label": "Sans type", "untyped": True}, accent=True).pack(side="left", padx=(0, 7), pady=(0, 6))
                for type_key, label, _custom in page_types():
                    make_brick(row, label, "page", {"type": type_key, "label": label}).pack(side="left", padx=(0, 6), pady=(0, 6))
                palette_hint_var.set("Clic : choisissez une brique, puis cliquez sur un + dans B  •  glissez sur une page pour remplacer son type")

            elif name == "Parties":
                row.pack(anchor="nw", fill="x")
                make_brick(row, "+ Partie", "group", {"type": "partie", "label": "+ Partie"}, accent=True).pack(side="left", padx=(0, 7), pady=(0, 6))
                small_action(row, "Renommer la sélection", rename_selected).pack(side="left", padx=(0, 6), pady=(0, 6))
                small_action(row, "Supprimer la partie vide", delete_selected, danger=True).pack(side="left", padx=(0, 6), pady=(0, 6))
                palette_hint_var.set("Cliquez + Partie puis sur un + entre deux parties dans B. Déplacement ensuite par glisser-déposer.")

            elif name == "Blancs":
                row.pack(anchor="nw", fill="x")
                make_brick(row, "Page blanche", "page", {"type": "page_blanche", "label": "Page blanche"}).pack(side="left", padx=(0, 7), pady=(0, 6))
                small_action(row, "Blanc avant", lambda: insert_blank_relative("before")).pack(side="left", padx=(0, 6), pady=(0, 6))
                small_action(row, "Blanc après", lambda: insert_blank_relative("after")).pack(side="left", padx=(0, 6), pady=(0, 6))
                palette_hint_var.set("Page blanche : clic puis + dans B, ou insertion directe avant/après la page sélectionnée.")

            elif name == "Types":
                tk.Button(
                    head_action_slot, text="+ Nouveau type", command=create_custom_type,
                    bg=theme.ACCENT_DARK, fg=theme.WHITE,
                    activebackground=theme.ACCENT_SOFT, activeforeground=theme.WHITE,
                    relief="flat", bd=0, padx=10, pady=5,
                    font=(theme.FONT_UI, 8, "bold"), cursor="hand2",
                ).pack(side="left")
                build_type_scroll_area(type_catalog())
                palette_hint_var.set("Les briques de type servent à attribuer ou changer un type de page. Molette : défilement vertical.")

            elif name == "Règles":
                row.pack(anchor="nw", fill="x")
                small_action(row, "Blanc avant", lambda: insert_blank_relative("before")).pack(side="left", padx=(0, 6), pady=(0, 6))
                small_action(row, "Blanc après", lambda: insert_blank_relative("after")).pack(side="left", padx=(0, 6), pady=(0, 6))
                tk.Label(row, text="Recto / verso complet : étape suivante.", bg=theme.PANEL_ALT, fg=theme.MUTED_DARK, font=(theme.FONT_UI, 8)).pack(side="left", padx=(10, 0), pady=7)
                palette_hint_var.set("Ici uniquement les règles qui modifient le squelette du livre.")

        for family in ("Pages", "Parties", "Blancs", "Types", "Règles"):
            button = tk.Button(
                rail, text=family, command=lambda n=family: select_family(n),
                bg=theme.PANEL_SOFT, fg=theme.INK,
                activebackground=theme.ACCENT_SOFT, activeforeground=theme.WHITE,
                relief="flat", bd=0, padx=5, pady=7,
                anchor="w", font=(theme.FONT_UI, 7, "bold"), cursor="hand2",
            )
            button.pack(fill="x", pady=2)
            family_buttons[family] = button

        tk.Label(
            rail, text="B = travail", bg=theme.PANEL_ALT, fg=theme.MUTED_DARK,
            font=(theme.FONT_UI, 6, "bold"),
        ).pack(side="bottom", anchor="w", padx=2, pady=(8, 1))

        select_family("Pages")

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
        book_canvas = getattr(self, "book_canvas", None)
        if book_canvas is not None and hasattr(book_canvas, "set_work_mode"):
            book_canvas.set_work_mode(key)
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
        self._home_new_type_var.set("")
        self._home_new_origin_var.set("")
        self._home_new_name_var.set("")
        self._home_model_path_var.set("")
        self.home_model_picker.grid_remove()
        self._home_refresh_type_cards()
        self._home_reload_models()
        self.home_creator_frame.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.home_creator_frame.lift()
        self.after_idle(lambda: self._home_name_entry.focus_set())

    def _choose_location(self, variable: tk.StringVar):
        # Conservé uniquement pour compatibilité avec d'anciens appels V3.
        # La création de projet est désormais figée dans PROJECTS_HOME.
        variable.set(str(PROJECTS_HOME))

    def _home_hide_creator(self):
        self.home_creator_frame.place_forget()
        self._home_new_type_var.set("")
        self._home_new_origin_var.set("")
        self._home_model_path_var.set("")

    def _home_select_type(self, key: str):
        self._home_new_origin_var.set("type")
        self._home_new_type_var.set(key)
        self._home_model_path_var.set("")
        self.home_model_picker.grid_remove()
        self._home_refresh_type_cards()

    def _home_refresh_type_cards(self):
        selected = self._home_new_type_var.get() if self._home_new_origin_var.get() == "type" else ""
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
                bg=bg, highlightthickness=2 if active else 1,
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
                photo = self._home_type_icon_glow(key, 90, selected=active)
                if photo is not None:
                    icon_label.configure(image=photo)
                    icon_label.image = photo
            radio = getattr(self, "_home_type_radios", {}).get(key)
            if radio is not None:
                radio.configure(bg=bg)
                radio.delete("all")
                radio.create_oval(2, 2, 16, 16, outline=accent, width=2 if active else 1)
                if active:
                    radio.create_oval(6, 6, 12, 12, fill="#F5F2FF", outline="")
                    radio.create_oval(0, 0, 18, 18, outline=accent, width=1)
        model_active = self._home_new_origin_var.get() == "modele"
        if hasattr(self, "_home_model_card"):
            self._home_model_card.configure(
                bg="#2B3A36" if model_active else "#2B323C",
                highlightthickness=2 if model_active else 1,
                highlightbackground="#79B49C" if model_active else "#49545E",
            )
            for child in self._home_model_card.winfo_children():
                try:
                    child.configure(bg="#2B3A36" if model_active else "#2B323C")
                except Exception:
                    pass

    def _home_add_sources(self):
        # Les sources auteur ne sont plus sélectionnées avant la création.
        # Elles sont proposées dans C quand le projet existe réellement.
        self._show_first_project_prompt()

    def _home_create_project_inline(self):
        name = self._home_new_name_var.get().strip()
        origin = self._home_new_origin_var.get()
        if not name:
            messagebox.showerror("TomeLinea", "Donnez un nom au nouveau projet.", parent=self)
            return
        if any(ch in name for ch in '<>:"/\\|?*') or name.endswith(".") or name.endswith(" "):
            messagebox.showerror(
                "TomeLinea", "Ce nom contient un caractère non autorisé par Windows.", parent=self,
            )
            return
        PROJECTS_HOME.mkdir(parents=True, exist_ok=True)
        existing_names = {p.name.casefold() for p in PROJECTS_HOME.iterdir() if p.is_dir()}
        if name.casefold() in existing_names:
            messagebox.showerror(
                "TomeLinea", f"Un projet nommé « {name} » existe déjà.\nChoisissez un autre nom.", parent=self,
            )
            return
        if origin not in {"type", "modele"}:
            messagebox.showerror(
                "TomeLinea", "Choisissez un type de livre ou un projet modèle.", parent=self,
            )
            return
        try:
            if origin == "modele":
                model_path = self._home_model_path_var.get().strip()
                if not model_path:
                    messagebox.showerror("TomeLinea", "Choisissez d’abord un modèle.", parent=self)
                    return
                project = self.project_manager.new_project_from_model(
                    model_path, str(PROJECTS_HOME), name,
                )
            else:
                project_type = self._home_new_type_var.get()
                if project_type not in {"ouvrage_structure", "livre_textuel", "bande_dessinee"}:
                    messagebox.showerror("TomeLinea", "Choisissez le type du livre.", parent=self)
                    return
                project = self.project_manager.new_project(
                    str(PROJECTS_HOME), name, project_type=project_type,
                )
        except Exception as exc:
            messagebox.showerror("TomeLinea", str(exc), parent=self)
            return

        self._home_hide_creator()
        self._remember_recent(project)
        self.show_workspace(project, first_open=True)

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
        PROJECTS_HOME.mkdir(parents=True, exist_ok=True)
        folder = filedialog.askdirectory(
            parent=self,
            title="Chercher / ouvrir un projet TomeLinea",
            initialdir=str(PROJECTS_HOME),
            mustexist=True,
        )
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
            return False
        paths = filedialog.askopenfilenames(parent=self, title="Ajouter les sources de l’auteur")
        if not paths:
            return False
        try:
            self._store_source_files(self.context.project, list(paths))
        except Exception as exc:
            messagebox.showerror("TomeLinea", str(exc), parent=self)
            return False
        self._refresh_workspace_state()
        return True

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

    def show_workspace(self, project: Project, first_open: bool = False):
        self.context = WorkspaceContext(project=project, name=project.name, project_type=project.project_type)
        self.book_canvas.set_project(project)
        self.select_tab("structure")
        self._refresh_workspace_state()
        self._screens["workspace"].tkraise()
        if first_open:
            self.after_idle(self._show_first_project_prompt)

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
        win.withdraw()
        win.title(f"TomeLinea — Consultation page {index + 1}")
        win.configure(bg=theme.WINDOW_DEEP)
        win.transient(self)
        try:
            win.overrideredirect(True)
        except tk.TclError:
            pass
        win.geometry("760x500")
        win.bind("<Escape>", lambda _e: win.destroy())

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

        # Fenêtre interne sans barre Windows : elle possède déjà son bouton Fermer.
        win.update_idletasks()
        try:
            x = self.winfo_rootx() + max(20, (self.winfo_width() - 760) // 2)
            y = self.winfo_rooty() + max(20, (self.winfo_height() - 500) // 2)
            win.geometry(f"760x500+{x}+{y}")
        except Exception:
            pass
        win.deiconify()
        win.lift()

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
            "last_opened": datetime.now().isoformat(timespec="minutes"),
        }
        recent = [r for r in self._load_recent() if r.get("path") != entry["path"]]
        recent.insert(0, entry)
        recent = recent[:8]
        RECENT_FILE.parent.mkdir(parents=True, exist_ok=True)
        RECENT_FILE.write_text(json.dumps(recent, indent=2, ensure_ascii=False), encoding="utf-8")
        self._refresh_home_recent()

    def _show_general_help(self):
        messagebox.showinfo(
            "Aide TomeLinea",
            "L’aide générale de TomeLinea sera rédigée lorsque les fonctions seront stabilisées.\n\n"
            "Elle proposera un mode d’emploi simple, avec accès à des explications plus détaillées.",
            parent=self,
        )

    def _show_preferences_waiting(self):
        messagebox.showinfo(
            "Préférences — bientôt disponible",
            "Les préférences seront activées quand l’interface et ses réglages auront été stabilisés.",
            parent=self,
        )

    def _show_zone_info(self, zone: str):
        texts = {
            "a": (
                "Zone A — Projet",
                "Cette zone reste visible pendant le travail. Elle indique le projet ouvert et donne accès aux commandes générales, à l’aide et à l’import des sources auteur.",
            ),
            "b": (
                "Zone B — Livre",
                "Cette zone est le livre lui-même. Elle sert à voir, sélectionner, déplacer et agrandir les pages sans changer d’espace de travail.",
            ),
            "c": (
                "Zone C — Outils",
                "Cette zone regroupe les outils selon le besoin du moment : Structure, Gabarits, Production et Sortie.",
            ),
        }
        title, body = texts.get(zone, ("TomeLinea", "Zone de travail TomeLinea."))
        messagebox.showinfo(title, body, parent=self)

    def _home_reload_models(self):
        PROJECT_MODELS_HOME.mkdir(parents=True, exist_ok=True)
        models = []
        for folder in sorted(PROJECT_MODELS_HOME.iterdir(), key=lambda p: p.name.casefold()):
            if not folder.is_dir() or not (folder / "projet.json").exists():
                continue
            try:
                data = json.loads((folder / "projet.json").read_text(encoding="utf-8"))
            except Exception:
                continue
            ptype = str(data.get("type_projet", "ouvrage_structure"))
            models.append({
                "name": str(data.get("nom") or folder.name),
                "type": ptype,
                "path": str(folder),
            })
        self._home_models = models
        box = getattr(self, "_home_model_list", None)
        if box is not None:
            box.delete(0, "end")
            type_labels = {
                "ouvrage_structure": "Fiches",
                "livre_textuel": "Textuel",
                "bande_dessinee": "BD",
            }
            for item in models:
                box.insert("end", f"{item['name']}   —   {type_labels.get(item['type'], 'Projet')}")
        status = getattr(self, "_home_model_status", None)
        if status is not None:
            if models:
                status.configure(text=f"{len(models)} modèle{'s' if len(models) > 1 else ''} disponible{'s' if len(models) > 1 else ''}")
            else:
                status.configure(text="Aucun modèle enregistré pour l’instant.")

    def _home_select_model_origin(self):
        self._home_new_origin_var.set("modele")
        self._home_new_type_var.set("")
        self._home_model_path_var.set("")
        self._home_reload_models()
        self.home_model_picker.grid()
        self._home_refresh_type_cards()

    def _home_model_selected(self, _event=None):
        selection = self._home_model_list.curselection()
        if not selection:
            self._home_model_path_var.set("")
            return
        index = int(selection[0])
        if index >= len(self._home_models):
            self._home_model_path_var.set("")
            return
        item = self._home_models[index]
        self._home_model_path_var.set(item["path"])
        type_labels = {
            "ouvrage_structure": "Livre de fiches",
            "livre_textuel": "Livre textuel",
            "bande_dessinee": "Bande dessinée",
        }
        self._home_model_status.configure(
            text=f"Sélectionné : {item['name']}  •  {type_labels.get(item['type'], 'Projet TomeLinea')}"
        )

    def _show_first_project_prompt(self):
        if self.context is None or self.context.project is None:
            return
        old = getattr(self, "_first_project_prompt", None)
        if old is not None:
            try:
                old.destroy()
            except Exception:
                pass
        self.select_tab("structure")
        host = self.tab_frames["structure"]
        prompt = tk.Frame(
            host, bg=theme.PANEL_ALT, highlightthickness=1,
            highlightbackground=theme.ACCENT,
        )
        prompt.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.70, relheight=0.72)
        self._first_project_prompt = prompt
        prompt.grid_columnconfigure(0, weight=1)
        prompt.grid_rowconfigure(1, weight=1)
        tk.Label(
            prompt, text="PROJET CRÉÉ", bg=theme.PANEL_ALT, fg=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 8, "bold"),
        ).grid(row=0, column=0, pady=(16, 4))
        tk.Label(
            prompt, text="Votre projet est prêt.", bg=theme.PANEL_ALT, fg=theme.INK,
            font=(theme.FONT_TITLE, 16, "bold"),
        ).grid(row=1, column=0, sticky="s", pady=(0, 4))
        tk.Label(
            prompt,
            text="Vous pouvez ajouter les sources de l’auteur maintenant, ou commencer par construire la structure du livre.",
            bg=theme.PANEL_ALT, fg=theme.MUTED, font=(theme.FONT_UI, 9),
            justify="center", wraplength=610,
        ).grid(row=2, column=0, pady=(0, 14))
        actions = tk.Frame(prompt, bg=theme.PANEL_ALT)
        actions.grid(row=3, column=0, pady=(0, 17))
        V3Button(
            actions, "Ajouter les sources de l’auteur",
            self._first_project_import_sources, primary=True, compact=True,
        ).pack(side="left", padx=(0, 8))
        V3Button(
            actions, "Commencer sans sources",
            self._close_first_project_prompt, compact=True,
        ).pack(side="left")

    def _first_project_import_sources(self):
        if self.import_sources():
            self._close_first_project_prompt()

    def _close_first_project_prompt(self):
        prompt = getattr(self, "_first_project_prompt", None)
        if prompt is not None:
            try:
                prompt.destroy()
            except Exception:
                pass
        self._first_project_prompt = None

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

        recent = self._load_recent()[:3]
        type_labels = {
            "ouvrage_structure": "Livre de fiches",
            "livre_textuel": "Livre textuel",
            "bande_dessinee": "Bande dessinée",
        }
        type_colors = {
            "ouvrage_structure": "#79B49C",
            "livre_textuel": "#A37AD4",
            "bande_dessinee": "#D37B55",
        }
        if not recent:
            tk.Label(
                host,
                text="Aucun projet récent.\nCréez votre premier projet depuis la zone Démarrer.",
                bg="#252C35", fg=theme.MUTED_DARK, justify="left",
                font=(theme.FONT_UI, 8),
            ).grid(row=0, column=0, sticky="nw", pady=10)
            return

        for row, item in enumerate(recent):
            key = item.get("type", "ouvrage_structure")
            path = item.get("path", "")
            accent = type_colors.get(key, theme.ACCENT)
            card = tk.Frame(
                host, bg="#2B323C", highlightthickness=1,
                highlightbackground="#46505A", cursor="hand2",
            )
            card.grid(row=row, column=0, sticky="ew", pady=(0 if row == 0 else 8, 0), ipady=3)
            card.grid_columnconfigure(1, weight=1)

            photo = self._type_icon(key, 60)
            icon = tk.Label(card, bg="#2B323C", bd=0)
            if photo is not None:
                icon.configure(image=photo)
                icon.image = photo
            icon.grid(row=0, column=0, rowspan=3, padx=(10, 13), pady=4)

            title = tk.Label(
                card, text=item.get("name", "Projet TomeLinea"), bg="#2B323C",
                fg=accent, font=(theme.FONT_UI, 9, "bold"), anchor="w",
            )
            title.grid(row=0, column=1, sticky="ew", pady=(6, 0), padx=(0, 10))
            kind = tk.Label(
                card, text=type_labels.get(key, "Projet TomeLinea"), bg="#2B323C",
                fg=theme.MUTED, font=(theme.FONT_UI, 7), anchor="w",
            )
            kind.grid(row=1, column=1, sticky="ew", pady=(1, 0), padx=(0, 10))

            raw_date = item.get("last_opened", "")
            display_date = "Dernière ouverture : date inconnue"
            if raw_date:
                try:
                    stamp = datetime.fromisoformat(raw_date)
                    display_date = stamp.strftime("Dernière ouverture : %d/%m/%Y à %H:%M")
                except Exception:
                    pass
            meta = tk.Label(
                card, text=display_date, bg="#2B323C", fg=theme.MUTED_DARK,
                font=(theme.FONT_UI, 7), anchor="w",
            )
            meta.grid(row=2, column=1, sticky="ew", pady=(1, 6), padx=(0, 10))

            command = lambda p=path: self._open_recent_path(p)
            for widget in (card, icon, title, kind, meta):
                widget.bind("<Button-1>", lambda _e, fn=command: fn())

