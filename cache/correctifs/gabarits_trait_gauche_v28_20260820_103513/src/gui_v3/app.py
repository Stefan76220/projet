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
        self.bind_all("<Control-z>", self._workspace_keyboard_undo, add="+")
        self.bind_all("<Control-y>", self._workspace_keyboard_redo, add="+")
        self.bind_all("<Control-Shift-Z>", self._workspace_keyboard_redo, add="+")
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
        self.zone_a = CutPanel(screen, fill=theme.PANEL, border=theme.BORDER, cut=14, padding=(18, 8))
        self.zone_b = CutPanel(screen, fill=theme.PANEL, border=theme.BORDER, cut=18, padding=(14, 8))
        self.book_canvas = BookCanvas(
            self.zone_b.body,
            on_open_item=self.open_consultation,
            on_change=self._refresh_workspace_state,
            on_focus_change=self._set_book_page_focus,
            on_history_change=self._update_history_buttons,
        )
        self.book_canvas.pack(fill="both", expand=True)
        self.zone_b_info = tk.Label(
            self.zone_b.body, text="ⓘ", bg=theme.PANEL, fg=theme.MUTED,
            font=(theme.FONT_UI, 11, "bold"), cursor="hand2", padx=5, pady=2,
        )
        self.zone_b_info.place(relx=1.0, x=-8, y=7, anchor="ne")
        self.zone_b_info.bind("<Button-1>", lambda _e: self._show_zone_info("b"))
        self.zone_c = CutPanel(screen, fill=theme.PANEL, border=theme.BORDER, cut=18, padding=(12, 8))
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
            margin_y = max(14, int(h * 0.024))
            inner_w = w - margin_x * 2
            gap = 7
            a_h = max(66, min(74, int(h * 0.075)))
            active_tab = str(getattr(self, "active_tab", "structure") or "structure")

            # Structure conserve l'atelier horizontal de C. Gabarits, au contraire,
            # transforme C en simple barre de navigation : les outils vivent
            # verticalement dans B afin que la page récupère presque toute la hauteur.
            if active_tab == "gabarits":
                c_h = 48
            else:
                c_h = max(255, min(320, int(h * 0.285)))

            normal_b_h = max(290, h - (margin_y * 2) - (gap * 2) - a_h - c_h)
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
        self.undo_button = V3Button(actions, "Annuler", self._workspace_undo, compact=True, state="disabled")
        self.undo_button.pack(side="left", padx=3)
        self.redo_button = V3Button(actions, "Rétablir", self._workspace_redo, compact=True, state="disabled")
        self.redo_button.pack(side="left", padx=3)
        V3Button(actions, "Fermer", self.destroy, compact=True).pack(side="left", padx=(10, 0))
        self._update_history_buttons(False, False)

    def _build_zone_c(self):
        body = self.zone_c.body
        body.grid_rowconfigure(1, weight=1)
        body.grid_columnconfigure(0, weight=1)

        self.tab_bar = tk.Frame(body, bg=theme.PANEL)
        self.tab_bar.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        self.tab_buttons: dict[str, tk.Button] = {}
        for index, (key, label) in enumerate(theme.TAB_NAMES):
            button = tk.Button(
                self.tab_bar, text=label, command=lambda k=key: self.select_tab(k),
                bg=theme.PANEL_SOFT, fg=theme.INK,
                activebackground=theme.ACCENT_SOFT, activeforeground=theme.WHITE,
                relief="flat", bd=0, padx=20, pady=5,
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
            self.tab_bar, text="B = surface de travail",
            bg=theme.PANEL, fg=theme.MUTED_DARK, font=(theme.FONT_UI, 7),
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
        """Structure V11 : un atelier unique dans C, source -> page automatique."""
        # Structure : identité interne inspirée de la référence validée.
        # Les dimensions et les comportements restent inchangés.
        WORK_BG = "#102633"
        WORK_BG_2 = "#0E202B"
        WORK_TILE = "#1A3140"
        WORK_TILE_HOVER = "#223E50"
        WORK_TILE_ACTIVE = "#284A5C"
        WORK_BORDER = "#385264"
        WORK_GOLD = "#C39A4A"
        WORK_TEAL = "#78B8B1"
        WORK_BLUE = "#7E9FB4"
        WORK_ORANGE = "#C88462"
        WORK_TEXT = "#F0F2F0"
        WORK_MUTED = "#A9B4B8"

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        atelier = tk.Frame(
            parent, bg=WORK_BG,
            highlightthickness=1, highlightbackground=WORK_BORDER,
            padx=10, pady=7,
        )
        atelier.grid(row=0, column=0, sticky="nsew")
        atelier.grid_columnconfigure(0, weight=1)
        atelier.grid_rowconfigure(1, weight=1)

        def book():
            return getattr(self, "book_canvas", None)

        # --------------------------------------------------------------
        # Petites commandes d'atelier : ni bouton classique, ni onglet.
        # --------------------------------------------------------------
        def command_chip(parent_, text, command, *, accent=WORK_TEAL, danger=False, compact=False):
            bg = "#172D3A"
            hover = "#213E4D"
            pressed = "#10242F"
            fg = WORK_TEXT
            edge = WORK_GOLD if not danger else "#B66B5B"
            lbl = tk.Label(
                parent_, text=text, bg=bg, fg=fg,
                font=(theme.FONT_UI, 7 if compact else 8, "bold"),
                padx=8 if compact else 10, pady=3 if compact else 4,
                highlightthickness=1, highlightbackground=edge,
                cursor="hand2",
            )
            def enter(_e=None): lbl.configure(bg=hover)
            def leave(_e=None): lbl.configure(bg=bg)
            def press(_e=None): lbl.configure(bg=pressed)
            def release(_e=None):
                lbl.configure(bg=hover)
                command()
                return "break"
            lbl.bind("<Enter>", enter)
            lbl.bind("<Leave>", leave)
            lbl.bind("<ButtonPress-1>", press)
            lbl.bind("<ButtonRelease-1>", release)
            return lbl

        # --------------------------------------------------------------
        # Fenêtre TomeLinea intégrée : seulement pour créer un nouveau type.
        # --------------------------------------------------------------
        def close_structure_modal():
            overlay = getattr(self, "_structure_modal_overlay", None)
            if overlay is not None:
                try:
                    overlay.destroy()
                except Exception:
                    pass
            self._structure_modal_overlay = None
            self._structure_modal_brand_refs = []

        def show_structure_modal(
            title: str, *, confirm_label="Valider", on_confirm=None,
            body_builder=None, width=960, height=560,
        ):
            close_structure_modal()
            host = getattr(self, "stack", self)
            overlay = tk.Frame(host, bg=theme.WINDOW_DEEP)
            overlay.place(x=0, y=0, relwidth=1, relheight=1)
            overlay.lift()
            self._structure_modal_overlay = overlay
            self._structure_modal_brand_refs = []

            bg = tk.Label(overlay, bg=theme.WINDOW_DEEP, bd=0)
            bg.place(x=0, y=0, relwidth=1, relheight=1)
            def refresh_background(event):
                try:
                    photo = self._background_photo(event.width, event.height, "workspace")
                except Exception:
                    photo = None
                if photo is not None:
                    bg.configure(image=photo)
                    bg.image = photo
            overlay.bind("<Configure>", refresh_background, add="+")

            icon = self._home_brand_icon_photo(108)
            title_photo = self._home_brand_title_photo(340)
            if icon is not None:
                self._structure_modal_brand_refs.append(icon)
                tk.Label(overlay, image=icon, bg=theme.WINDOW_DEEP, bd=0).place(x=28, y=12)
            if title_photo is not None:
                self._structure_modal_brand_refs.append(title_photo)
                tk.Label(overlay, image=title_photo, bg=theme.WINDOW_DEEP, bd=0).place(relx=0.5, y=16, anchor="n")
            tk.Label(
                overlay, text="LA LIGNE ÉDITORIALE JUSQU’AU LIVRE",
                bg=theme.WINDOW_DEEP, fg=theme.MUTED_DARK,
                font=(theme.FONT_UI, 8, "bold"),
            ).place(relx=0.5, y=61, anchor="n")

            card = tk.Frame(overlay, bg=theme.PANEL_ALT, highlightthickness=1, highlightbackground=theme.BORDER)
            card.place(relx=0.5, rely=0.55, anchor="center", width=width, height=height)
            card.grid_columnconfigure(0, weight=1)
            card.grid_rowconfigure(2, weight=1)

            head = tk.Frame(card, bg=theme.PANEL_ALT)
            head.grid(row=0, column=0, sticky="ew", padx=22, pady=(14, 7))
            head.grid_columnconfigure(0, weight=1)
            tk.Label(head, text=title, bg=theme.PANEL_ALT, fg=theme.INK, font=(theme.FONT_TITLE, 15, "bold")).grid(row=0, column=0, sticky="w")
            close = tk.Label(head, text="×", bg=theme.PANEL_ALT, fg=theme.MUTED, font=(theme.FONT_UI, 18, "bold"), cursor="hand2")
            close.grid(row=0, column=1, sticky="e")
            close.bind("<Button-1>", lambda _e: close_structure_modal())
            tk.Frame(card, bg=theme.ACCENT_DARK, height=1).grid(row=1, column=0, sticky="ew", padx=22)

            body = tk.Frame(card, bg=theme.PANEL_ALT)
            body.grid(row=2, column=0, sticky="nsew", padx=22, pady=12)
            body.grid_columnconfigure(0, weight=1)
            body.grid_rowconfigure(0, weight=1)
            if body_builder is not None:
                body_builder(body)

            foot = tk.Frame(card, bg=theme.PANEL_ALT)
            foot.grid(row=3, column=0, sticky="ew", padx=22, pady=(6, 14))
            foot.grid_columnconfigure(0, weight=1)
            tk.Button(
                foot, text="Annuler", command=close_structure_modal,
                bg=theme.PANEL_SOFT, fg=theme.INK,
                activebackground=theme.ACCENT_SOFT, activeforeground=theme.WHITE,
                relief="flat", bd=0, padx=14, pady=6,
                font=(theme.FONT_UI, 8, "bold"), cursor="hand2",
            ).grid(row=0, column=1, padx=(0, 7))
            def confirm():
                if on_confirm is None or not bool(on_confirm()):
                    close_structure_modal()
            tk.Button(
                foot, text=confirm_label, command=confirm,
                bg=theme.ACCENT_DARK, fg=theme.WHITE,
                activebackground=theme.ACCENT_SOFT, activeforeground=theme.WHITE,
                relief="flat", bd=0, padx=16, pady=6,
                font=(theme.FONT_UI, 8, "bold"), cursor="hand2",
            ).grid(row=0, column=2)
            overlay.bind("<Escape>", lambda _e: close_structure_modal())
            overlay.focus_set()

        # --------------------------------------------------------------
        # En-tête de l'atelier.
        # --------------------------------------------------------------
        head = tk.Frame(atelier, bg=WORK_BG)
        head.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        head.grid_columnconfigure(3, weight=1)
        structure_head_var = tk.StringVar(value="TYPES DE PAGE")
        structure_hint_var = tk.StringVar(value="sélectionner → déposer dans B")
        structure_head_label = tk.Label(
            head, textvariable=structure_head_var, bg=WORK_BG, fg=WORK_TEXT,
            font=(theme.FONT_TITLE, 10, "bold"),
        )
        structure_head_label.grid(row=0, column=0, sticky="w", pady=(1, 2))

        # V23 : Nouveau type prolonge directement le titre Briques de pages.
        # Le catalogue commence légèrement plus bas, sans changer la hauteur de C.
        new_type_slot = tk.Frame(head, bg=WORK_BG)
        new_type_slot.grid(row=0, column=1, sticky="w", padx=(12, 0))

        structure_hint_label = tk.Label(
            head, textvariable=structure_hint_var, bg=WORK_BG, fg=WORK_MUTED,
            font=(theme.FONT_UI, 7),
        )
        structure_hint_label.grid(row=0, column=2, sticky="w", padx=(12, 0))

        # --------------------------------------------------------------
        # Zone C — deux palettes adaptées au type de livre.
        # Petite zone « Courants » à gauche, grande zone « Autres types » à droite.
        # Le contenu se réordonne et se transfère par glisser-déposer.
        # --------------------------------------------------------------
        catalog_host = tk.Frame(atelier, bg=WORK_BG_2)
        catalog_host.grid(row=1, column=0, sticky="nsew")
        catalog_host.grid_rowconfigure(0, weight=1)
        catalog_host.grid_columnconfigure(0, weight=2, uniform="structure_palette")
        catalog_host.grid_columnconfigure(1, weight=3, uniform="structure_palette")

        active_brick = {"widget": None, "normalizer": None, "type_key": ""}
        catalog_refs = {"current": None, "other": None}
        zone_widgets = {"current": [], "other": []}
        drag_state = {
            "type_key": "", "start_x": 0, "start_y": 0, "moved": False, "widget": None,
        }
        delete_pending = {"type_key": ""}
        new_type_editor = {"outside_bind": None}

        def reset_active_brick():
            normalizer = active_brick.get("normalizer")
            if callable(normalizer):
                try:
                    normalizer()
                except Exception:
                    pass
            active_brick["widget"] = None
            active_brick["normalizer"] = None
            active_brick["type_key"] = ""
            canvas = book()
            if canvas is not None and hasattr(canvas, "structure_register_palette_widget"):
                try:
                    canvas.structure_register_palette_widget(None)
                except Exception:
                    pass

        def arm(kind, payload):
            canvas = book()
            if canvas is not None and hasattr(canvas, "structure_arm_tool"):
                canvas.structure_arm_tool(kind, payload)

        def page_types():
            canvas = book()
            if canvas is not None and hasattr(canvas, "structure_available_page_types"):
                return canvas.structure_available_page_types()
            return []

        def brick_style(type_key):
            key = str(type_key or "")
            if key in {"illustration", "fiche", "annexe", "planche", "bonus"}:
                return WORK_ORANGE
            if key in {"chapitre", "tete_partie", "transition", "resume_precedent"}:
                return WORK_TEAL
            if key in {"texte", "avant_propos", "conclusion", "remerciements", "mode_emploi"}:
                return WORK_BLUE
            return WORK_GOLD

        def brick_icon(type_key):
            return {
                "page_blanche": "▫",
                "page_titre": "T",
                "mentions_legales": "§",
                "sommaire": "≡",
                "avant_propos": "¶",
                "dedicace": "D",
                "preface": "P",
                "tete_partie": "◆",
                "chapitre": "C",
                "texte": "☰",
                "illustration": "▧",
                "carte": "◎",
                "fiche": "▤",
                "planche": "▦",
                "mode_emploi": "?",
                "resume_precedent": "↶",
                "presentation_personnages": "●",
                "bonus": "+",
                "glossaire": "G",
                "bibliographie": "B",
                "sources": "S",
                "index": "I",
                "annexe": "↗",
                "a_propos_auteur": "@",
                "autres_ouvrages": "＋",
                "remerciements": "♡",
            }.get(str(type_key or ""), "◇")

        def point_inside(widget, root_x, root_y):
            try:
                x = widget.winfo_rootx(); y = widget.winfo_rooty()
                return x <= root_x <= x + widget.winfo_width() and y <= root_y <= y + widget.winfo_height()
            except Exception:
                return False

        def drop_destination(root_x, root_y):
            for zone in ("current", "other"):
                ref = catalog_refs.get(zone)
                panel = ref.get("panel") if isinstance(ref, dict) else None
                if panel is not None and point_inside(panel, root_x, root_y):
                    return zone
            return None

        def drop_index(zone, root_x, root_y, moving_type):
            cards = [entry for entry in zone_widgets.get(zone, []) if entry[0] != moving_type]
            if not cards:
                return 0
            geometries = []
            for _type_key, widget in cards:
                try:
                    cx = widget.winfo_rootx() + widget.winfo_width() / 2
                    cy = widget.winfo_rooty() + widget.winfo_height() / 2
                    geometries.append((cx, cy, widget))
                except Exception:
                    pass
            if not geometries:
                return len(cards)
            nearest = min(range(len(geometries)), key=lambda idx: (geometries[idx][1]-root_y)**2 * 2 + (geometries[idx][0]-root_x)**2)
            cx, cy, _widget = geometries[nearest]
            before = root_y < cy - 3 or (abs(root_y-cy) <= 8 and root_x < cx)
            return nearest if before else nearest + 1

        def move_brick(type_key, root_x, root_y):
            destination = drop_destination(root_x, root_y)
            if destination is None:
                return False
            canvas = book()
            if canvas is None or not hasattr(canvas, "structure_move_page_type"):
                return False
            index = drop_index(destination, root_x, root_y, str(type_key or ""))
            ok = bool(canvas.structure_move_page_type(str(type_key or ""), destination, index))
            if ok:
                delete_pending["type_key"] = ""
                rebuild_catalog()
            return ok

        def make_brick(parent_, label, type_key, *, custom=False, zone="other"):
            width, height = 112, 32
            card = tk.Canvas(
                parent_, width=width, height=height, bg=WORK_BG_2,
                bd=0, highlightthickness=0, cursor="hand2",
            )
            display = str(label or "Page")
            accent = brick_style(type_key)
            icon = brick_icon(type_key)

            def draw(fill=WORK_TILE, outline=WORK_BORDER, active=False):
                card.delete("all")
                card.create_rectangle(
                    1, 1, width-1, height-1, fill=fill, outline=outline,
                    width=2 if active else 1,
                )
                card.create_text(
                    10, height/2, text=icon, anchor="w",
                    fill=accent, font=(theme.FONT_UI, 8, "bold"),
                )
                card.create_text(
                    25, height/2, text=display, anchor="w", justify="left",
                    fill=WORK_TEXT, font=(theme.FONT_UI, 7, "bold"), width=width-31,
                )

            def normal():
                draw()
            normal()

            def enter(_e=None):
                if active_brick.get("widget") is not card:
                    draw(WORK_TILE_HOVER, "#557184")
            def leave(_e=None):
                if active_brick.get("widget") is not card:
                    normal()
            def press(event):
                drag_state.update({
                    "type_key": str(type_key or ""), "start_x": event.x_root,
                    "start_y": event.y_root, "moved": False, "widget": card,
                })
                draw("#102735", WORK_GOLD)
                return "break"
            def motion(event):
                canvas = book()
                if canvas is not None and hasattr(canvas, "structure_page_auto_context"):
                    try:
                        if canvas.structure_page_auto_context().get("active"):
                            return "break"
                    except Exception:
                        pass
                if drag_state.get("widget") is not card:
                    return None
                dx = int(event.x_root) - int(drag_state.get("start_x") or 0)
                dy = int(event.y_root) - int(drag_state.get("start_y") or 0)
                if abs(dx) + abs(dy) >= 10:
                    drag_state["moved"] = True
                    card.configure(cursor="fleur")
                    draw("#203B4B", WORK_GOLD, active=True)
                return "break"
            def release(event):
                card.configure(cursor="hand2")
                moved = bool(drag_state.get("widget") is card and drag_state.get("moved"))
                drag_state.update({"type_key": "", "start_x": 0, "start_y": 0, "moved": False, "widget": None})
                if moved:
                    reset_active_brick()
                    move_brick(type_key, event.x_root, event.y_root)
                    return "break"

                canvas = book()
                if canvas is not None and hasattr(canvas, "structure_consume_page_auto_choice"):
                    try:
                        if canvas.structure_consume_page_auto_choice(str(type_key or "")):
                            reset_active_brick()
                            return "break"
                    except Exception:
                        pass
                if delete_pending.get("type_key") and delete_pending.get("type_key") != str(type_key or ""):
                    delete_pending["type_key"] = ""

                # Second clic sur la même brique : termine volontairement le dépôt multiple.
                pending_type = ""
                if canvas is not None and hasattr(canvas, "structure_pending_page_type"):
                    try:
                        pending_type = str(canvas.structure_pending_page_type() or "")
                    except Exception:
                        pending_type = ""
                if active_brick.get("widget") is card and pending_type == str(type_key or ""):
                    if hasattr(canvas, "structure_cancel_tool"):
                        canvas.structure_cancel_tool()
                    reset_active_brick()
                    return "break"

                reset_active_brick()
                active_brick["widget"] = card
                active_brick["normalizer"] = normal
                active_brick["type_key"] = str(type_key or "")
                if canvas is not None and hasattr(canvas, "structure_register_palette_widget"):
                    try:
                        canvas.structure_register_palette_widget(card)
                    except Exception:
                        pass
                draw(WORK_TILE_ACTIVE, WORK_GOLD, active=True)
                arm("page", {"type": str(type_key or ""), "label": str(label or "Page")})
                return "break"

            card.bind("<Enter>", enter)
            card.bind("<Leave>", leave)
            card.bind("<ButtonPress-1>", press)
            card.bind("<B1-Motion>", motion)
            card.bind("<ButtonRelease-1>", release)
            return card

        def install_wheel(widget, cv):
            def wheel(event):
                bbox = cv.bbox("all")
                if not bbox or bbox[3] <= cv.winfo_height() + 2:
                    return None
                delta = getattr(event, "delta", 0)
                if delta:
                    cv.yview_scroll(-1 if delta > 0 else 1, "units")
                else:
                    cv.yview_scroll(-1 if getattr(event, "num", 0) == 4 else 1, "units")
                return "break"
            def bind_tree(node):
                node.bind("<MouseWheel>", wheel, add="+")
                node.bind("<Button-4>", wheel, add="+")
                node.bind("<Button-5>", wheel, add="+")
                for child in node.winfo_children():
                    bind_tree(child)
            bind_tree(widget)

        def build_zone(parent_, zone, title, rows, columns):
            panel = tk.Frame(parent_, bg=WORK_BG_2, highlightthickness=1, highlightbackground=WORK_BORDER)
            panel.grid_rowconfigure(1, weight=1)
            panel.grid_columnconfigure(0, weight=1)
            title_row = tk.Frame(panel, bg=WORK_BG_2)
            title_row.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 3))
            title_row.grid_columnconfigure(0, weight=1)
            tk.Label(
                title_row, text=title, bg=WORK_BG_2,
                fg=WORK_GOLD if zone == "current" else WORK_MUTED,
                font=(theme.FONT_UI, 8, "bold"),
            ).grid(row=0, column=0, sticky="w")
            tk.Label(
                title_row, text=str(len(rows)), bg=WORK_BG_2, fg="#73858F",
                font=(theme.FONT_UI, 7, "bold"),
            ).grid(row=0, column=1, sticky="e")

            holder = tk.Frame(panel, bg=WORK_BG_2)
            holder.grid(row=1, column=0, sticky="nsew", padx=4, pady=(0, 4))
            cv = tk.Canvas(holder, bg=WORK_BG_2, bd=0, highlightthickness=0)
            inner = tk.Frame(cv, bg=WORK_BG_2)
            win = cv.create_window((0, 0), window=inner, anchor="nw")
            cv.pack(fill="both", expand=True)
            for col in range(max(1, columns)):
                inner.grid_columnconfigure(col, weight=0)
            zone_widgets[zone] = []
            for i, (key, label, custom) in enumerate(rows):
                card = make_brick(inner, label, key, custom=bool(custom), zone=zone)
                card.grid(row=i//columns, column=i%columns, padx=3, pady=3, sticky="nw")
                zone_widgets[zone].append((str(key or ""), card))
            def sync_region(_e=None):
                bbox = cv.bbox("all")
                if bbox:
                    cv.configure(scrollregion=bbox)
            inner.bind("<Configure>", sync_region)
            cv.bind("<Configure>", lambda e: cv.itemconfigure(win, width=e.width))
            install_wheel(holder, cv)
            catalog_refs[zone] = {"panel": panel, "holder": holder, "canvas": cv, "inner": inner}
            return panel

        def rebuild_catalog(_event=None):
            for child in catalog_host.winfo_children():
                try:
                    child.destroy()
                except Exception:
                    pass
            reset_active_brick()
            canvas = book()
            palette = (
                canvas.structure_page_type_palette()
                if canvas is not None and hasattr(canvas, "structure_page_type_palette")
                else {"current_types": [], "other_types": []}
            )
            current_rows = list(palette.get("current_types", []))
            other_rows = list(palette.get("other_types", []))
            current_panel = build_zone(catalog_host, "current", "COURANTS", current_rows, 3)
            other_panel = build_zone(catalog_host, "other", "AUTRES TYPES", other_rows, 5)
            current_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 4))
            other_panel.grid(row=0, column=1, sticky="nsew", padx=(4, 0))

        def replace_selected_page_type():
            type_key = str(active_brick.get("type_key") or "").strip()
            canvas = book()
            if not type_key or canvas is None:
                if canvas is not None:
                    canvas.status_var.set("Sélectionnez un type dans C puis une page dans B.")
                return
            try:
                if hasattr(canvas, "structure_cancel_tool"):
                    canvas.structure_cancel_tool()
                ok = bool(
                    hasattr(canvas, "structure_replace_selected_page_type")
                    and canvas.structure_replace_selected_page_type(type_key)
                )
            except Exception:
                ok = False
            if ok:
                delete_pending["type_key"] = ""
                reset_active_brick()
            refresh_page_auto_ui()

        def delete_selected_type():
            type_key = str(active_brick.get("type_key") or "").strip()
            canvas = book()
            if not type_key or canvas is None:
                if canvas is not None:
                    canvas.status_var.set("Sélectionnez d’abord un type dans C.")
                return
            if delete_pending.get("type_key") != type_key:
                delete_pending["type_key"] = type_key
                canvas.status_var.set("Suppression du type  •  cliquez à nouveau sur Confirmer suppression")
                refresh_page_auto_ui()
                return
            delete_pending["type_key"] = ""
            if hasattr(canvas, "structure_delete_page_type") and canvas.structure_delete_page_type(type_key):
                rebuild_catalog()
            refresh_page_auto_ui()

        def reset_palette():
            canvas = book()
            delete_pending["type_key"] = ""
            if canvas is not None and hasattr(canvas, "structure_reset_page_type_palette"):
                if canvas.structure_reset_page_type_palette():
                    rebuild_catalog()
            refresh_page_auto_ui()

        # --------------------------------------------------------------
        # Création d'un nouveau type : nouvelle page dédiée, puis retour catalogue.
        # --------------------------------------------------------------
        def create_custom_type():
            canvas = book()
            if canvas is None or not hasattr(canvas, "structure_create_custom_type"):
                return

            previous_bind = new_type_editor.get("outside_bind")
            if previous_bind:
                try:
                    self.unbind("<Button-1>", previous_bind)
                except Exception:
                    pass
                new_type_editor["outside_bind"] = None

            for child in new_type_slot.winfo_children():
                try:
                    child.destroy()
                except Exception:
                    pass

            name_var = tk.StringVar()
            entry = tk.Entry(
                new_type_slot, textvariable=name_var, width=20,
                bg="#172D3A", fg=WORK_TEXT, insertbackground=WORK_TEXT,
                relief="flat", bd=0, highlightthickness=1,
                highlightbackground=WORK_GOLD, highlightcolor=WORK_GOLD,
                font=(theme.FONT_UI, 8),
            )
            entry.pack(side="left", padx=(0, 5), ipady=3)

            def stop_outside_watch():
                bind_id = new_type_editor.get("outside_bind")
                if bind_id:
                    try:
                        self.unbind("<Button-1>", bind_id)
                    except Exception:
                        pass
                    new_type_editor["outside_bind"] = None

            def cancel(_e=None):
                stop_outside_watch()
                refresh_page_auto_ui()
                return "break"

            def confirm(_e=None):
                name = name_var.get().strip()
                if not name:
                    entry.focus_set()
                    return "break"
                created = canvas.structure_create_custom_type({"name": name})
                if created:
                    stop_outside_watch()
                    rebuild_catalog()
                    refresh_page_auto_ui()
                return "break"

            command_chip(new_type_slot, "Créer", confirm, accent=WORK_GOLD, compact=True).pack(side="left", padx=(0, 4))
            command_chip(new_type_slot, "×", cancel, compact=True).pack(side="left")
            entry.bind("<Return>", confirm)
            entry.bind("<Escape>", cancel)

            def dismiss_on_outside_click(event):
                if point_inside(new_type_slot, event.x_root, event.y_root):
                    return None
                self.after_idle(cancel)
                return None

            new_type_editor["outside_bind"] = self.bind(
                "<Button-1>", dismiss_on_outside_click, add="+"
            )
            entry.focus_set()

        # V25 : la même ligne d'en-tête devient contextuelle pendant Page auto.
        # En temps normal elle contient + Nouveau type. Pendant le choix Page auto,
        # elle affiche uniquement les actions utiles à la règle en cours.
        def refresh_page_auto_ui(_event=None):
            def later():
                for child in new_type_slot.winfo_children():
                    try:
                        child.destroy()
                    except Exception:
                        pass

                canvas = book()
                context = (
                    canvas.structure_page_auto_context()
                    if canvas is not None and hasattr(canvas, "structure_page_auto_context")
                    else {"active": False}
                )
                step = int(context.get("step") or 0)
                if not context.get("active"):
                    atelier.configure(highlightthickness=1, highlightbackground=WORK_BORDER)
                    structure_head_label.configure(fg=WORK_TEXT)
                    structure_hint_label.configure(fg=WORK_MUTED)
                    structure_head_var.set("TYPES DE PAGE")
                    structure_hint_var.set("sélectionner → déposer dans B")
                    command_chip(
                        new_type_slot,
                        "+ Nouveau type",
                        create_custom_type,
                        accent=WORK_GOLD,
                        compact=False,
                    ).pack(side="left")
                    delete_text = (
                        "Confirmer suppression"
                        if delete_pending.get("type_key") and delete_pending.get("type_key") == active_brick.get("type_key")
                        else "Supprimer type"
                    )
                    command_chip(
                        new_type_slot, "Remplacer", replace_selected_page_type,
                        accent=WORK_GOLD, compact=True,
                    ).pack(side="left", padx=(6, 0))
                    command_chip(
                        new_type_slot, delete_text, delete_selected_type,
                        accent=WORK_ORANGE, danger=True, compact=True,
                    ).pack(side="left", padx=(6, 0))
                    command_chip(
                        new_type_slot, "Réinitialiser", reset_palette,
                        accent=WORK_MUTED, compact=True,
                    ).pack(side="left", padx=(6, 0))
                    return

                side = str(context.get("side_label") or "")
                source_label = str(context.get("source_label") or "page")
                if step == 2:
                    atelier.configure(highlightthickness=3, highlightbackground=WORK_GOLD)
                    structure_head_label.configure(fg=WORK_GOLD)
                    structure_hint_label.configure(fg=WORK_TEXT)
                else:
                    atelier.configure(highlightthickness=1, highlightbackground=WORK_BORDER)
                    structure_head_label.configure(fg=WORK_TEXT)
                    structure_hint_label.configure(fg=WORK_MUTED)
                structure_head_var.set(f"PAGE AUTO — {side.upper()} DES « {source_label.upper()} »")
                target_label = str(context.get("target_label") or "")
                if target_label:
                    structure_hint_var.set(
                        f"règle actuelle : {target_label}  •  choisir un autre type pour la remplacer"
                    )
                else:
                    structure_hint_var.set("choisir le type à associer  •  ce clic valide la règle")


            self.after_idle(later)

        self.bind_all("<<StructurePageAutoModeChanged>>", refresh_page_auto_ui, add="+")
        refresh_page_auto_ui()

        def sync_brick_state(_event=None):
            def later():
                canvas = book()
                if canvas is None or not getattr(canvas, "_structure_pending_kind", None):
                    reset_active_brick()
            self.after_idle(later)
        self.bind_all("<ButtonRelease-1>", sync_brick_state, add="+")
        self.bind_all("<<StructureToolChanged>>", sync_brick_state, add="+")
        self.bind_all("<<StructurePaletteChanged>>", rebuild_catalog, add="+")

        rebuild_catalog()


    def _build_gabarits_tab(self, parent):
        """Gabarits : outils verticaux dans B ; C ne garde que la navigation."""
        side_host = getattr(getattr(self, "book_canvas", None), "gabarit_tools_host", None)
        if side_host is not None:
            parent = side_host
        WORK_BG = "#102633"
        # Le fond des familles utilise la clé transparente du rail : seuls les
        # contrôles eux-mêmes restent opaques au-dessus de la page.
        CARD_BG = WORK_BG
        CARD_BORDER = "#385264"
        TEAL = "#78B8B1"
        TEXT = "#F0F2F0"
        MUTED = "#A9B4B8"
        VALUE = "#D7E5E2"

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        atelier = tk.Frame(
            parent, bg=WORK_BG, highlightthickness=0, padx=10, pady=10,
        )
        atelier.grid(row=0, column=0, sticky="nsew")
        atelier.grid_columnconfigure(0, weight=1)

        head = tk.Frame(atelier, bg=WORK_BG)
        head.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        tk.Label(
            head, text="OUTILS", bg=WORK_BG, fg=TEXT,
            font=(theme.FONT_TITLE, 10, "bold"),
        ).pack(anchor="w")
        state_var = tk.StringVar(value="Page prête")
        tk.Label(
            head, textvariable=state_var, bg=WORK_BG, fg=MUTED,
            font=(theme.FONT_UI, 7), anchor="w", justify="left",
            wraplength=180,
        ).pack(fill="x", pady=(3, 0))
        tk.Frame(atelier, bg=CARD_BORDER, height=1).grid(row=1, column=0, sticky="ew", pady=(0, 8))

        families = tk.Frame(atelier, bg=WORK_BG)
        families.grid(row=2, column=0, sticky="nsew")
        families.grid_columnconfigure(0, weight=1)
        families.grid_rowconfigure(1, weight=1)
        atelier.grid_rowconfigure(2, weight=1)

        family_selector = tk.Frame(families, bg=WORK_BG)
        family_selector.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        for col in range(3):
            family_selector.grid_columnconfigure(col, weight=1, uniform="gabarit_family_select")

        def book():
            return getattr(self, "book_canvas", None)

        # ----------------------------------------------------------
        # Un seul panneau volant à la fois.
        # Il se ferme par validation, Échap ou clic extérieur.
        # ----------------------------------------------------------
        self._gabarit_tool_dialog = None
        self._gabarit_tool_outside_bind = None

        def close_tool_panel():
            bind_id = getattr(self, "_gabarit_tool_outside_bind", None)
            if bind_id:
                try:
                    self.unbind("<Button-1>", bind_id)
                except Exception:
                    pass
            self._gabarit_tool_outside_bind = None
            win = getattr(self, "_gabarit_tool_dialog", None)
            self._gabarit_tool_dialog = None
            if win is not None:
                try:
                    win.destroy()
                except Exception:
                    pass

        def _panel_fade_in(win, alpha=0.0):
            try:
                if not win.winfo_exists():
                    return
                alpha = min(1.0, alpha + 0.18)
                win.attributes("-alpha", alpha)
                if alpha < 1.0:
                    win.after(12, lambda: _panel_fade_in(win, alpha))
            except Exception:
                pass

        def open_tool_panel(opener, title, builder, *, min_width=320):
            close_tool_panel()
            win = tk.Toplevel(self)
            self._gabarit_tool_dialog = win
            win.withdraw()
            win.configure(bg=theme.WINDOW_DEEP)
            win.transient(self)
            try:
                win.overrideredirect(True)
                win.attributes("-alpha", 0.05)
            except tk.TclError:
                pass
            win.bind("<Escape>", lambda _e: close_tool_panel())

            panel = CutPanel(
                win, fill=theme.PANEL, border=theme.BORDER,
                cut=14, padding=(14, 12),
            )
            panel.pack(fill="both", expand=True, padx=7, pady=7)
            pbody = panel.body
            pbody.grid_columnconfigure(0, weight=1)

            top = tk.Frame(pbody, bg=theme.PANEL)
            top.grid(row=0, column=0, sticky="ew", pady=(0, 8))
            top.grid_columnconfigure(0, weight=1)
            tk.Label(
                top, text=title, bg=theme.PANEL, fg=theme.INK,
                font=(theme.FONT_TITLE, 10, "bold"),
            ).grid(row=0, column=0, sticky="w")
            close_label = tk.Label(
                top, text="×", bg=theme.PANEL, fg=theme.MUTED,
                font=(theme.FONT_UI, 12, "bold"), cursor="hand2", padx=4,
            )
            close_label.grid(row=0, column=1, sticky="e")
            close_label.bind("<Button-1>", lambda _e: close_tool_panel())

            content = tk.Frame(pbody, bg=theme.PANEL)
            content.grid(row=1, column=0, sticky="nsew")
            builder(content, close_tool_panel)

            win.update_idletasks()
            w = max(min_width, win.winfo_reqwidth())
            h = max(100, win.winfo_reqheight())
            try:
                ox = opener.winfo_rootx()
                oy = opener.winfo_rooty()
                ow = opener.winfo_width()
            except Exception:
                ox, oy, ow = self.winfo_pointerx(), self.winfo_pointery(), 1

            # Le panneau contextuel reste indépendant du rail transparent : il est
            # opaque, lisible et toujours limité à la surface centrale de B.
            canvas_widget = getattr(getattr(self, "book_canvas", None), "canvas", None)
            if canvas_widget is not None:
                try:
                    canvas_widget.update_idletasks()
                    cx = int(canvas_widget.winfo_rootx())
                    cy = int(canvas_widget.winfo_rooty())
                    cw = int(canvas_widget.winfo_width())
                    ch = int(canvas_widget.winfo_height())
                    work = self.book_canvas._gabarit_work_rect()
                    left = cx + int(work[0])
                    top = cy + int(work[1])
                    right = cx + int(work[2])
                    bottom = cy + int(work[3])
                    x = max(left + 6, min(ox + ow + 8, right - w - 6))
                    y = max(top + 4, min(oy - 8, bottom - h - 4))
                except Exception:
                    x = int(max(self.winfo_rootx() + 10, min(
                        ox + (ow - w) / 2,
                        self.winfo_rootx() + self.winfo_width() - w - 10,
                    )))
                    y = int(max(self.winfo_rooty() + 58, oy - h - 9))
            else:
                x = int(max(self.winfo_rootx() + 10, min(
                    ox + (ow - w) / 2,
                    self.winfo_rootx() + self.winfo_width() - w - 10,
                )))
                y = int(max(self.winfo_rooty() + 58, oy - h - 9))
            win.geometry(f"{w}x{h}+{x}+{y}")
            win.deiconify()
            win.lift()
            _panel_fade_in(win)

            def bind_outside():
                def outside(event):
                    current = getattr(self, "_gabarit_tool_dialog", None)
                    if current is None:
                        return
                    try:
                        widget = event.widget
                        path = str(widget)
                        if path.startswith(str(current)):
                            return
                        if widget is opener or path.startswith(str(opener)):
                            return
                    except Exception:
                        pass
                    close_tool_panel()
                try:
                    self._gabarit_tool_outside_bind = self.bind("<Button-1>", outside, add="+")
                except Exception:
                    self._gabarit_tool_outside_bind = None
            self.after_idle(bind_outside)
            return win

        family_cards = {}
        family_selector_buttons = {}

        def family_card(key, number, title, subtitle):
            card = tk.Frame(
                families, bg=CARD_BG, highlightthickness=0,
                padx=9, pady=8,
            )
            card.grid(row=1, column=0, sticky="nsew")
            card.grid_columnconfigure(0, weight=1)
            title_row = tk.Frame(card, bg=CARD_BG)
            title_row.grid(row=0, column=0, sticky="ew", pady=(0, 5))
            tk.Label(
                title_row, text=str(number), bg=CARD_BG, fg=TEAL,
                font=(theme.FONT_TITLE, 11, "bold"),
            ).pack(side="left")
            tk.Label(
                title_row, text=title, bg=CARD_BG, fg=TEXT,
                font=(theme.FONT_TITLE, 8, "bold"),
            ).pack(side="left", padx=(6, 0))
            tk.Label(
                card, text=subtitle, bg=CARD_BG, fg=MUTED,
                font=(theme.FONT_UI, 7), anchor="w",
            ).grid(row=1, column=0, sticky="ew", pady=(0, 7))
            content = tk.Frame(card, bg=CARD_BG)
            content.grid(row=2, column=0, sticky="ew")
            family_cards[key] = card
            return card, content

        content_card, content_box = family_card("content", "1", "CONTENU", "préparer Production")
        place_card, place_box = family_card("placement", "2", "PLACEMENT", "positionner et dimensionner")
        align_card, align_box = family_card("align", "3", "ALIGNEMENT", "ordonner précisément")

        def show_family(key):
            card = family_cards.get(key)
            if card is not None:
                card.tkraise()
            for family_key, btn in family_selector_buttons.items():
                active = family_key == key
                btn.configure(
                    bg="#315A5A" if active else "#20313B",
                    fg="#F2F3F1" if active else "#B9C6C6",
                    activebackground="#3B6867" if active else "#314752",
                    activeforeground="#FFFFFF",
                )

        for col, (key, label) in enumerate((("content", "Contenu"), ("placement", "Placement"), ("align", "Align."))):
            btn = tk.Button(
                family_selector, text=label, command=lambda k=key: show_family(k),
                bg="#20313B", fg="#B9C6C6",
                activebackground="#314752", activeforeground="#FFFFFF",
                relief="flat", bd=0, highlightthickness=1,
                highlightbackground="#465963", padx=2, pady=4,
                font=(theme.FONT_UI, 7, "bold"), cursor="hand2",
            )
            btn.grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 3, 0))
            family_selector_buttons[key] = btn

        show_family("content")

        # ----------------------------------------------------------
        # Réglages du livre — appelés depuis l'inspecteur de B.
        # C ne répète plus format / marges / fond perdu.
        # ----------------------------------------------------------
        settings_anchor = tk.Frame(atelier, bg=WORK_BG, width=1, height=1)
        settings_anchor.place(relx=1.0, rely=0.0, x=-6, y=0, anchor="ne")

        def numeric_panel(opener, title, rows, values, apply_callback):
            def build(host, close):
                host.grid_columnconfigure(1, weight=1)
                vars_ = {}
                for r, (key, label) in enumerate(rows):
                    tk.Label(
                        host, text=label, bg=theme.PANEL, fg=theme.INK_SOFT,
                        font=(theme.FONT_UI, 9),
                    ).grid(row=r, column=0, sticky="w", pady=4, padx=(0, 12))
                    var = tk.StringVar(value=f"{float(values.get(key, 0)):g}")
                    vars_[key] = var
                    entry = tk.Entry(
                        host, textvariable=var, width=10, justify="right",
                        bg="#182936", fg="#F2F3F1", insertbackground="#F2F3F1",
                        relief="flat", bd=0, highlightthickness=1,
                        highlightbackground=theme.BORDER,
                    )
                    entry.grid(row=r, column=1, sticky="ew", pady=4)
                    tk.Label(
                        host, text="mm", bg=theme.PANEL, fg=theme.MUTED,
                        font=(theme.FONT_UI, 8),
                    ).grid(row=r, column=2, sticky="w", padx=(5, 0))
                error = tk.StringVar(value="")
                tk.Label(
                    host, textvariable=error, bg=theme.PANEL, fg="#E1A0A0",
                    font=(theme.FONT_UI, 8),
                ).grid(row=len(rows), column=0, columnspan=3, sticky="w", pady=(5, 2))
                actions = tk.Frame(host, bg=theme.PANEL)
                actions.grid(row=len(rows)+1, column=0, columnspan=3, sticky="e", pady=(7, 0))
                V3Button(actions, "Annuler", close, compact=True).pack(side="right", padx=(5, 0))
                def apply():
                    try:
                        parsed = {k: float(v.get().replace(",", ".")) for k, v in vars_.items()}
                    except Exception:
                        error.set("Valeurs numériques uniquement.")
                        return
                    if not bool(apply_callback(parsed)):
                        error.set("Valeurs incompatibles avec la page.")
                        return
                    refresh_gabarit_tools()
                    close()
                V3Button(actions, "Appliquer", apply, compact=True, primary=True).pack(side="right")
            open_tool_panel(opener, title, build, min_width=360)

        def open_margins():
            canvas = book()
            if canvas is None:
                return
            values = dict((canvas.gabarit_current_settings() or {}).get("margins_mm", {}))
            numeric_panel(
                settings_anchor, "Marges du livre — millimètres",
                [("top", "Haut"), ("bottom", "Bas"), ("inside", "Intérieure"), ("outside", "Extérieure")],
                values,
                lambda v: canvas.gabarit_set_margins(v["top"], v["bottom"], v["inside"], v["outside"]),
            )

        def open_bleed():
            canvas = book()
            if canvas is None:
                return
            values = dict((canvas.gabarit_current_settings() or {}).get("bleed_mm", {}))
            numeric_panel(
                settings_anchor, "Fond perdu du livre — millimètres",
                [("top", "Haut"), ("right", "Droite"), ("bottom", "Bas"), ("left", "Gauche")],
                values,
                lambda v: canvas.gabarit_set_bleed(v["top"], v["right"], v["bottom"], v["left"]),
            )

        def open_format():
            if self._show_gabarit_format_dialog(force_change=True):
                self._gabarit_format_session_confirmed = self._gabarit_format_session_key()
                refresh_gabarit_tools()

        def confirm_type_scope(page_type_label: str, page_count: int) -> bool:
            count = max(0, int(page_count))
            plural = "pages" if count > 1 else "page"
            return bool(messagebox.askyesno(
                "Portée du gabarit",
                (
                    f"Appliquer le gabarit de cette page aux {count} {plural} « {page_type_label} » ?\n\n"
                    "Les pages normales seront mises à jour. Les exceptions existantes resteront protégées."
                ),
                parent=self,
            ))

        try:
            self.book_canvas.on_gabarit_edit_format = open_format
            self.book_canvas.on_gabarit_edit_margins = open_margins
            self.book_canvas.on_gabarit_edit_bleed = open_bleed
            self.book_canvas.on_gabarit_confirm_type_scope = confirm_type_scope
        except Exception:
            pass

        # ----------------------------------------------------------
        # 1 — CONTENU
        # ----------------------------------------------------------
        content_box.grid_columnconfigure(0, weight=1)
        content_buttons = {}
        for row, (kind, label) in enumerate((("text", "Texte"), ("image", "Image"), ("document", "Document"))):
            def create_zone(k=kind):
                canvas = book()
                if canvas is not None:
                    canvas.gabarit_add_zone(k)
                    refresh_gabarit_tools()
            btn = V3Button(content_box, label, create_zone, compact=True)
            btn.grid(row=row, column=0, sticky="ew", pady=(0 if row == 0 else 4, 0))
            content_buttons[kind] = btn

        def delete_selected_zone():
            canvas = book()
            if canvas is not None and canvas.gabarit_delete_selected_zone():
                refresh_gabarit_tools()

        content_hint = tk.Label(
            content_box, text="Le type choisi devient la nature attendue du contenu en Production.",
            bg=CARD_BG, fg=MUTED, font=(theme.FONT_UI, 7), justify="left",
            wraplength=175, anchor="w",
        )
        content_hint.configure(wraplength=175)
        content_hint.grid(row=3, column=0, sticky="ew", pady=(7, 0))
        delete_zone_btn = V3Button(content_box, "Supprimer", delete_selected_zone, compact=True, state="disabled")
        delete_zone_btn.grid(row=4, column=0, sticky="ew", pady=(6, 0))

        def copy_page_template():
            canvas = book()
            if canvas is not None and canvas.gabarit_copy_current_template():
                refresh_gabarit_tools()

        def apply_page_template():
            canvas = book()
            if canvas is not None and canvas.gabarit_apply_copied_template():
                refresh_gabarit_tools()

        template_row = tk.Frame(content_box, bg=CARD_BG)
        template_row.grid(row=5, column=0, sticky="ew", pady=(7, 0))
        template_row.grid_columnconfigure(0, weight=1)
        copy_template_btn = V3Button(template_row, "Copier gabarit", copy_page_template, compact=True)
        copy_template_btn.grid(row=0, column=0, sticky="ew")
        apply_template_btn = V3Button(template_row, "Appliquer", apply_page_template, compact=True, state="disabled")
        apply_template_btn.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        # ----------------------------------------------------------
        # 2 — PLACEMENT
        # ----------------------------------------------------------
        place_box.grid_columnconfigure(0, weight=1)
        occupation_btn = V3Button(place_box, "Occupation", compact=True)
        dimensions_btn = V3Button(place_box, "Dimensions", compact=True)
        snap_btn = V3Button(place_box, "Accrochage", compact=True)
        occupation_btn.grid(row=0, column=0, sticky="ew")
        dimensions_btn.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        snap_btn.grid(row=2, column=0, sticky="ew", pady=(4, 0))

        placement_info = tk.StringVar(value="Sélectionnez une zone")
        tk.Label(
            place_box, textvariable=placement_info, bg=CARD_BG, fg=VALUE,
            font=(theme.FONT_UI, 7, "bold"), anchor="w", justify="left", wraplength=175,
        ).grid(row=3, column=0, sticky="ew", pady=(7, 0))

        def open_occupation():
            canvas = book()
            if canvas is None or not canvas.gabarit_selected_zone_info():
                return
            def build(host, close):
                tk.Label(
                    host, text="La zone occupe :", bg=theme.PANEL, fg=theme.INK_SOFT,
                    font=(theme.FONT_UI, 8),
                ).pack(anchor="w", pady=(0, 7))
                row = tk.Frame(host, bg=theme.PANEL)
                row.pack(fill="x")
                for label, mode in (
                    ("Libre", "free"),
                    ("Dans les marges", "margins"),
                    ("Pleine page", "page"),
                    ("Fond perdu", "bleed"),
                ):
                    def apply(m=mode):
                        if canvas.gabarit_set_selected_zone_occupation(m):
                            refresh_gabarit_tools()
                        close()
                    V3Button(row, label, apply, compact=True).pack(side="left", padx=(0, 5))
                if canvas.gabarit_active_is_spread():
                    tk.Label(
                        host, text="Position dans la double page", bg=theme.PANEL, fg=theme.INK_SOFT,
                        font=(theme.FONT_UI, 8, "bold"),
                    ).pack(anchor="w", pady=(12, 6))
                    spread_row = tk.Frame(host, bg=theme.PANEL)
                    spread_row.pack(fill="x")
                    for label, position in (("Gauche", "left"), ("Centre", "center"), ("Droite", "right")):
                        def place(p=position):
                            if canvas.gabarit_set_selected_zone_spread_position(p):
                                refresh_gabarit_tools()
                            close()
                        V3Button(spread_row, label, place, compact=True).pack(side="left", padx=(0, 5))
            open_tool_panel(occupation_btn, "Occupation de la zone", build, min_width=470)

        def open_dimensions():
            canvas = book()
            if canvas is None:
                return
            info = canvas.gabarit_selected_zone_info()
            if not info:
                return
            rect = dict(info.get("rect_mm") or {})
            numeric_panel(
                dimensions_btn, "Position et dimensions",
                [("x", "X depuis la gauche"), ("y", "Y depuis le haut"), ("w", "Largeur"), ("h", "Hauteur")],
                rect,
                lambda v: canvas.gabarit_set_selected_zone_rect_mm(v["x"], v["y"], v["w"], v["h"]),
            )

        def open_snap():
            canvas = book()
            if canvas is None or not canvas.gabarit_selected_zone_info():
                return
            profile = canvas.gabarit_snap_profile()
            def build(host, close):
                ref_var = tk.StringVar(value=str(profile.get("reference") or "page"))
                tk.Label(
                    host, text="Référence", bg=theme.PANEL, fg=theme.INK_SOFT,
                    font=(theme.FONT_UI, 8, "bold"),
                ).grid(row=0, column=0, sticky="w", pady=(0, 5))
                refs = tk.Frame(host, bg=theme.PANEL)
                refs.grid(row=1, column=0, sticky="ew", pady=(0, 8))
                for label, value in (("Page", "page"), ("Marges", "margins")):
                    V3Button(
                        refs, label,
                        lambda v=value: ref_var.set(v),
                        compact=True,
                    ).pack(side="left", padx=(0, 5))
                tk.Label(
                    host, text="Points d’accrochage", bg=theme.PANEL, fg=theme.INK_SOFT,
                    font=(theme.FONT_UI, 8, "bold"),
                ).grid(row=2, column=0, sticky="w", pady=(0, 5))
                points = tk.Frame(host, bg=theme.PANEL)
                points.grid(row=3, column=0, sticky="ew")
                options = [
                    ("Gauche", "left"), ("Centre H", "hcenter"), ("Droite", "right"),
                    ("Haut", "top"), ("Centre V", "vcenter"), ("Bas", "bottom"),
                    ("Deux centres", "both_centers"),
                ]
                selected = set(profile.get("anchors") or ())
                vars_ = {}
                for i, (label, key) in enumerate(options):
                    var = tk.BooleanVar(value=key in selected); vars_[key] = var
                    cb = tk.Checkbutton(
                        points, text=label, variable=var,
                        bg=theme.PANEL, fg=theme.INK_SOFT,
                        activebackground=theme.PANEL, activeforeground=theme.INK,
                        selectcolor="#182936", font=(theme.FONT_UI, 8),
                    )
                    cb.grid(row=i//4, column=i%4, sticky="w", padx=(0, 8), pady=2)
                actions = tk.Frame(host, bg=theme.PANEL)
                actions.grid(row=4, column=0, sticky="e", pady=(9, 0))
                def apply():
                    anchors = [k for k, v in vars_.items() if v.get()]
                    canvas.gabarit_set_snap_profile(ref_var.get(), anchors)
                    refresh_gabarit_tools()
                    close()
                V3Button(actions, "Appliquer", apply, compact=True, primary=True).pack(side="right")
            open_tool_panel(snap_btn, "Accrochage", build, min_width=520)

        occupation_btn.configure(command=open_occupation)
        dimensions_btn.configure(command=open_dimensions)
        snap_btn.configure(command=open_snap)

        # ----------------------------------------------------------
        # 3 — ALIGNEMENT
        # ----------------------------------------------------------
        align_box.grid_columnconfigure(0, weight=1)
        align_btn = V3Button(align_box, "Aligner", compact=True)
        distribute_btn = V3Button(align_box, "Équilibrer", compact=True)
        align_btn.grid(row=0, column=0, sticky="ew")
        distribute_btn.grid(row=1, column=0, sticky="ew", pady=(4, 0))
        align_info = tk.StringVar(value="Page · Marges · Sélection")
        tk.Label(
            align_box, textvariable=align_info, bg=CARD_BG, fg=MUTED,
            font=(theme.FONT_UI, 7), anchor="w", justify="left", wraplength=175,
        ).grid(row=2, column=0, sticky="ew", pady=(7, 0))

        def open_align():
            canvas = book()
            if canvas is None or not canvas.gabarit_selected_zone_info():
                return
            def build(host, close):
                ref_var = tk.StringVar(value="page")
                ref_row = tk.Frame(host, bg=theme.PANEL)
                ref_row.pack(fill="x", pady=(0, 8))
                tk.Label(
                    ref_row, text="Référence :", bg=theme.PANEL, fg=theme.INK_SOFT,
                    font=(theme.FONT_UI, 8, "bold"),
                ).pack(side="left", padx=(0, 7))
                for label, value in (("Page", "page"), ("Marges", "margins")):
                    V3Button(ref_row, label, lambda v=value: ref_var.set(v), compact=True).pack(side="left", padx=(0, 5))
                grid = tk.Frame(host, bg=theme.PANEL)
                grid.pack(fill="x")
                actions = (
                    ("←", "left"), ("↔", "center"), ("→", "right"),
                    ("↑", "top"), ("↕", "middle"), ("↓", "bottom"),
                )
                for i, (glyph, mode) in enumerate(actions):
                    def apply(m=mode):
                        canvas.gabarit_align_selected_zone(m, reference=ref_var.get())
                        refresh_gabarit_tools()
                        close()
                    V3Button(grid, glyph, apply, compact=True).grid(
                        row=i//3, column=i%3, sticky="ew", padx=(0 if i%3 == 0 else 5, 0), pady=(0 if i < 3 else 5, 0),
                    )
                    grid.grid_columnconfigure(i%3, weight=1, uniform="align")
            open_tool_panel(align_btn, "Alignement", build, min_width=340)

        def open_distribute():
            canvas = book()
            if canvas is None:
                return
            def build(host, close):
                tk.Label(
                    host,
                    text="Équilibrage collectif — prévu pour la sélection multiple.",
                    bg=theme.PANEL, fg=theme.INK_SOFT, font=(theme.FONT_UI, 8),
                ).pack(anchor="w", pady=(0, 8))
                row = tk.Frame(host, bg=theme.PANEL)
                row.pack(fill="x")
                for label in ("Largeur", "Hauteur", "Les deux"):
                    btn = V3Button(row, label, compact=True, state="disabled")
                    btn.pack(side="left", padx=(0, 5))
                tk.Label(
                    host, text="Les commandes seront activées avec la sélection collective de zones.",
                    bg=theme.PANEL, fg=theme.MUTED, font=(theme.FONT_UI, 7),
                ).pack(anchor="w", pady=(8, 0))
            open_tool_panel(distribute_btn, "Équilibrage", build, min_width=430)

        align_btn.configure(command=open_align)
        distribute_btn.configure(command=open_distribute)

        def refresh_gabarit_tools(_event=None):
            canvas = book()
            if canvas is None:
                return
            try:
                selected = canvas.gabarit_selected_zone_info()
            except Exception:
                selected = {}
            active = bool(selected)
            state = "normal" if active else "disabled"
            for btn in (occupation_btn, dimensions_btn, snap_btn, align_btn, delete_zone_btn):
                btn.configure(state=state, cursor="hand2" if active else "arrow")
            try:
                has_copy = bool(canvas.gabarit_has_copied_template())
            except Exception:
                has_copy = False
            apply_template_btn.configure(
                state="normal" if has_copy else "disabled",
                cursor="hand2" if has_copy else "arrow",
            )
            if active:
                kind = {"text": "Texte", "image": "Image", "document": "Document"}.get(
                    str(selected.get("kind") or ""), "Zone"
                )
                mode = {
                    "free": "Libre", "margins": "Dans les marges",
                    "page": "Pleine page", "bleed": "Fond perdu",
                }.get(str(selected.get("occupation") or "free"), "Libre")
                rect = dict(selected.get("rect_mm") or {})
                spread_position = str(selected.get("spread_position") or "")
                spread_text = {"left": "2P gauche", "center": "2P centre", "right": "2P droite"}.get(spread_position, "")
                placement_info.set(
                    f"{kind} · " + (f"{spread_text} · " if spread_text else "") + f"{mode} · "
                    f"{float(rect.get('w', 0)):g} × {float(rect.get('h', 0)):g} mm"
                )
                state_var.set(f"Zone {kind} sélectionnée")
            else:
                placement_info.set("Sélectionnez une zone dans B")
                state_var.set("Page prête")

        self._refresh_gabarit_panel = refresh_gabarit_tools
        try:
            self.book_canvas.bind("<<GabaritPageChanged>>", refresh_gabarit_tools, add="+")
            self.book_canvas.bind("<<GabaritSelectionChanged>>", refresh_gabarit_tools, add="+")
            self.book_canvas.bind("<<StructurePaletteChanged>>", refresh_gabarit_tools, add="+")
        except Exception:
            pass
        self.after_idle(refresh_gabarit_tools)

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

    def _gabarit_format_session_key(self) -> str:
        project = getattr(getattr(self, "context", None), "project", None)
        root = getattr(project, "root", None) if project is not None else None
        return str(root or id(project) or "preview")

    def _show_gabarit_format_dialog(self, *, force_change: bool = False) -> bool:
        """Dialogue modal : choisir au premier passage, confirmer ensuite.

        Il n’apparaît qu’une fois par ouverture de projet. Le bouton Format fini de
        l’inspecteur peut toutefois le rouvrir explicitement pour changer de format.
        """
        canvas = getattr(self, "book_canvas", None)
        if canvas is None:
            return False
        explicit = bool(canvas.gabarit_has_explicit_format())
        current = canvas.gabarit_book_format()
        result = {"ok": False}

        win = tk.Toplevel(self)
        win.title("Format du livre")
        win.configure(bg=theme.WINDOW_DEEP)
        win.transient(self)
        win.resizable(False, False)
        try:
            win.iconbitmap(str(BRAND_ICON))
        except Exception:
            pass
        win.grab_set()

        shell = CutPanel(win, fill=theme.PANEL, border=theme.BORDER, cut=16, padding=(20, 16))
        shell.pack(fill="both", expand=True, padx=10, pady=10)
        body = shell.body
        body.grid_columnconfigure(0, weight=1)

        tk.Label(
            body, text="FORMAT DU LIVRE", bg=theme.PANEL, fg=theme.INK,
            font=(theme.FONT_TITLE, 13, "bold"),
        ).grid(row=0, column=0, sticky="w")
        intro = (
            "Ce format est commun à tout le livre. Il détermine la forme réelle des pages, "
            "des marges et des doubles pages."
        )
        tk.Label(
            body, text=intro, bg=theme.PANEL, fg=theme.MUTED,
            justify="left", wraplength=470, font=(theme.FONT_UI, 8),
        ).grid(row=1, column=0, sticky="w", pady=(7, 12))

        current_frame = tk.Frame(body, bg="#202D36", highlightthickness=1, highlightbackground="#465963")
        current_frame.grid(row=2, column=0, sticky="ew", pady=(0, 12))
        tk.Label(current_frame, text="Format actuel", bg="#202D36", fg=theme.MUTED, font=(theme.FONT_UI, 7, "bold")).pack(anchor="w", padx=12, pady=(8, 2))
        current_var = tk.StringVar(value=f"{current['label']}  —  {current['width_mm']:g} × {current['height_mm']:g} mm")
        tk.Label(current_frame, textvariable=current_var, bg="#202D36", fg=theme.INK, font=(theme.FONT_TITLE, 11, "bold")).pack(anchor="w", padx=12, pady=(0, 9))

        chooser = tk.Frame(body, bg=theme.PANEL)
        chooser.grid(row=3, column=0, sticky="ew")
        chooser.grid_columnconfigure(1, weight=1)

        catalog = canvas.gabarit_format_catalog()
        labels = [f"{item['label']} — {item['width_mm']:g} × {item['height_mm']:g} mm" for item in catalog]
        labels.append("Personnalisé")
        by_label = {label: item for label, item in zip(labels[:-1], catalog)}
        selected = tk.StringVar(value=labels[0])
        for label, item in by_label.items():
            if abs(float(item['width_mm']) - float(current['width_mm'])) < .01 and abs(float(item['height_mm']) - float(current['height_mm'])) < .01:
                selected.set(label)
                break
        if str(current.get('id')) == 'custom':
            selected.set("Personnalisé")

        tk.Label(chooser, text="Format", bg=theme.PANEL, fg=theme.INK, font=(theme.FONT_UI, 8, "bold")).grid(row=0, column=0, sticky="w", padx=(0, 10), pady=4)
        menu = tk.OptionMenu(chooser, selected, *labels)
        menu.configure(
            bg=theme.PANEL_SOFT, fg=theme.INK, activebackground=theme.ACCENT_SOFT,
            activeforeground=theme.WHITE, relief="flat", bd=0, highlightthickness=0,
            font=(theme.FONT_UI, 8), width=31,
        )
        menu["menu"].configure(bg=theme.PANEL_SOFT, fg=theme.INK, font=(theme.FONT_UI, 8))
        menu.grid(row=0, column=1, sticky="ew", pady=4)

        width_var = tk.StringVar(value=f"{float(current['width_mm']):g}")
        height_var = tk.StringVar(value=f"{float(current['height_mm']):g}")
        custom = tk.Frame(chooser, bg=theme.PANEL)
        custom.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 0))
        for c in (1, 3):
            custom.grid_columnconfigure(c, weight=1)
        tk.Label(custom, text="Largeur", bg=theme.PANEL, fg=theme.MUTED, font=(theme.FONT_UI, 8)).grid(row=0, column=0, sticky="w")
        width_entry = tk.Entry(custom, textvariable=width_var, bg=theme.PANEL_SOFT, fg=theme.INK, insertbackground=theme.INK, relief="flat", font=(theme.FONT_UI, 8), width=8)
        width_entry.grid(row=0, column=1, sticky="ew", padx=(6, 5))
        tk.Label(custom, text="mm   Hauteur", bg=theme.PANEL, fg=theme.MUTED, font=(theme.FONT_UI, 8)).grid(row=0, column=2, sticky="w")
        height_entry = tk.Entry(custom, textvariable=height_var, bg=theme.PANEL_SOFT, fg=theme.INK, insertbackground=theme.INK, relief="flat", font=(theme.FONT_UI, 8), width=8)
        height_entry.grid(row=0, column=3, sticky="ew", padx=(6, 5))
        tk.Label(custom, text="mm", bg=theme.PANEL, fg=theme.MUTED, font=(theme.FONT_UI, 8)).grid(row=0, column=4, sticky="w")

        error = tk.StringVar(value="")
        tk.Label(body, textvariable=error, bg=theme.PANEL, fg="#E1A0A0", font=(theme.FONT_UI, 8)).grid(row=4, column=0, sticky="w", pady=(7, 0))
        warn = tk.StringVar(value="")
        tk.Label(body, textvariable=warn, bg=theme.PANEL, fg="#C9B27D", justify="left", wraplength=470, font=(theme.FONT_UI, 7)).grid(row=5, column=0, sticky="w", pady=(2, 0))

        actions = tk.Frame(body, bg=theme.PANEL)
        actions.grid(row=6, column=0, sticky="e", pady=(13, 0))

        editing = {"value": force_change or not explicit}

        def sync_custom(*_):
            is_custom = selected.get() == "Personnalisé"
            state = "normal" if is_custom and editing["value"] else "disabled"
            width_entry.configure(state=state)
            height_entry.configure(state=state)
            if not is_custom:
                item = by_label.get(selected.get())
                if item:
                    width_var.set(f"{float(item['width_mm']):g}")
                    height_var.set(f"{float(item['height_mm']):g}")
            warn.set("Changer le format redimensionne proportionnellement les gabarits déjà créés." if explicit and editing["value"] else "")

        def set_editing(value: bool):
            editing["value"] = bool(value)
            menu.configure(state="normal" if editing["value"] else "disabled")
            sync_custom()

        def close_without_change():
            result["ok"] = False
            try:
                win.grab_release()
            except Exception:
                pass
            win.destroy()

        def confirm_current():
            result["ok"] = True
            try:
                win.grab_release()
            except Exception:
                pass
            win.destroy()

        def validate():
            try:
                width = float(width_var.get().replace(",", "."))
                height = float(height_var.get().replace(",", "."))
            except Exception:
                error.set("Largeur et hauteur doivent être numériques.")
                return
            item = by_label.get(selected.get())
            if item is None:
                format_id = "custom"
                label = "Personnalisé"
            else:
                format_id = str(item["id"])
                label = str(item["label"])
                width = float(item["width_mm"])
                height = float(item["height_mm"])
            if not canvas.gabarit_set_book_format(format_id, label, width, height):
                error.set("Format incompatible avec les marges actuelles ou dimensions invalides.")
                return
            result["ok"] = True
            try:
                win.grab_release()
            except Exception:
                pass
            win.destroy()

        if explicit and not force_change:
            set_editing(False)
            V3Button(actions, "Annuler", close_without_change, compact=True).pack(side="right", padx=(6, 0))
            V3Button(actions, "Changer de format", lambda: set_editing(True), compact=True).pack(side="right", padx=(6, 0))
            V3Button(actions, "Confirmer ce format", confirm_current, compact=True, primary=True).pack(side="right")
        else:
            set_editing(True)
            V3Button(actions, "Annuler", close_without_change, compact=True).pack(side="right", padx=(6, 0))
            V3Button(actions, "Valider le format", validate, compact=True, primary=True).pack(side="right")

        # Quand « Changer » est choisi dans le mode confirmation, le bouton principal
        # devient Valider sans ouvrir une seconde fenêtre.
        def watch_editing():
            if not win.winfo_exists():
                return
            if explicit and not force_change and editing["value"]:
                for child in list(actions.winfo_children()):
                    child.destroy()
                V3Button(actions, "Annuler", close_without_change, compact=True).pack(side="right", padx=(6, 0))
                V3Button(actions, "Valider le format", validate, compact=True, primary=True).pack(side="right")
                return
            win.after(80, watch_editing)
        if explicit and not force_change:
            win.after(80, watch_editing)

        selected.trace_add("write", sync_custom)
        win.protocol("WM_DELETE_WINDOW", close_without_change)
        win.bind("<Escape>", lambda _e: close_without_change())
        win.update_idletasks()
        w, h = 540, 390
        x = self.winfo_rootx() + max(0, (self.winfo_width() - w) // 2)
        y = self.winfo_rooty() + max(0, (self.winfo_height() - h) // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.wait_window()
        return bool(result["ok"])

    def _ensure_gabarit_format_for_session(self) -> bool:
        key = self._gabarit_format_session_key()
        if getattr(self, "_gabarit_format_session_confirmed", None) == key:
            return True
        if not self._show_gabarit_format_dialog(force_change=False):
            return False
        self._gabarit_format_session_confirmed = key
        return True

    def select_tab(self, key: str):
        if key not in self.tab_frames:
            return
        if key == "gabarits" and not self._ensure_gabarit_format_for_session():
            return
        self.active_tab = key
        self.tab_frames[key].tkraise()
        book_canvas = getattr(self, "book_canvas", None)
        if book_canvas is not None and hasattr(book_canvas, "set_work_mode"):
            book_canvas.set_work_mode(key)
        tab_host = getattr(self, "tab_host", None)
        if tab_host is not None:
            try:
                if key == "gabarits":
                    tab_host.grid_remove()
                else:
                    tab_host.grid()
            except Exception:
                pass
        if key == "gabarits":
            refresher = getattr(self, "_refresh_gabarit_panel", None)
            if callable(refresher):
                try:
                    refresher()
                except Exception:
                    pass
        # Le changement de bureau peut changer complètement la géométrie B/C.
        # On recalcule donc immédiatement la place disponible.
        layout = getattr(self, "_workspace_layout_callback", None)
        if callable(layout):
            self.after_idle(lambda: layout(None))
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
        self._gabarit_format_session_confirmed = None
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

    def _update_history_buttons(self, can_undo=None, can_redo=None):
        if can_undo is None:
            can_undo = bool(getattr(self, "book_canvas", None) and self.book_canvas.can_undo())
        if can_redo is None:
            can_redo = bool(getattr(self, "book_canvas", None) and self.book_canvas.can_redo())
        undo = getattr(self, "undo_button", None)
        redo = getattr(self, "redo_button", None)
        if undo is not None:
            undo.configure(state="normal" if can_undo else "disabled", cursor="hand2" if can_undo else "arrow")
        if redo is not None:
            redo.configure(state="normal" if can_redo else "disabled", cursor="hand2" if can_redo else "arrow")

    def _workspace_undo(self):
        canvas = getattr(self, "book_canvas", None)
        if canvas is not None:
            canvas.structure_undo()

    def _workspace_redo(self):
        canvas = getattr(self, "book_canvas", None)
        if canvas is not None:
            canvas.structure_redo()

    def _workspace_keyboard_undo(self, event=None):
        widget = getattr(event, "widget", None) if event is not None else None
        if isinstance(widget, (tk.Entry, tk.Text)):
            return None
        self._workspace_undo()
        return "break"

    def _workspace_keyboard_redo(self, event=None):
        widget = getattr(event, "widget", None) if event is not None else None
        if isinstance(widget, (tk.Entry, tk.Text)):
            return None
        self._workspace_redo()
        return "break"

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

