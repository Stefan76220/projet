# TOMELINEA_GABARITS_REGLAGES_SIMPLIFIES_V59
from __future__ import annotations

import importlib.util
import json
import shutil
import queue
import threading
from datetime import datetime
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog
from typing import Callable

from PIL import Image, ImageColor, ImageDraw, ImageEnhance, ImageFilter, ImageTk

from src.core.book_source import (
    inspect_pdf,
    load_project_source,
    source_cache_folder,
    store_source_in_project,
)
from src.gui_v3 import theme
from src.gui_v3.book_canvas import BookCanvas
from src.gui_v3.focus_toolbar import FocusToolbar
from src.gui_v3.hover import GlobalHoverManager
from src.gui_v3.source_book_viewer import SourceBookViewer
from src.gui_v3.viewer3d_panel import Viewer3DOverlay


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
    # ACCUEIL_SOURCE_AVANT_CREATION_V4
    # BARRE_OUTILS_FLOTTANTE_PAGE_V3_V6
    # ZOOM_PAGE_PLEIN_ESPACE_V3_V4
    # CANEVA_LIVRE_UNIQUE_V3_V2
    """TomeLinea V3 — espace projet continu A/B/C."""

    # DEMARRAGE_ATOMIQUE_V3_WINDOWS_V2
    def __init__(self, *, startup_progress: Callable[[str, str], None] | None = None) -> None:
        super().__init__()

        # La fenêtre de préparation existe encore pendant le préchauffage.
        # TomeLinea doit donc devenir explicitement la racine Tk par défaut
        # pour que toutes ses PhotoImage et variables Tk appartiennent au
        # bon interpréteur.
        try:
            tk._default_root = self
        except Exception:
            pass

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
        # Visionneur plein écran : un véritable enfant de la pile TomeLinea.
        # Aucun Chrome/Edge séparé n'est lancé par cette intégration.
        self.viewer3d_overlay = Viewer3DOverlay(
            self.stack,
            on_return=self._return_from_viewer,
            on_action=self._viewer_action,
            on_navigate=self._navigate_from_viewer,
            bg=theme.WINDOW_DEEP,
        )
        self.bind_all("<Control-z>", self._workspace_keyboard_undo, add="+")
        self.bind_all("<Control-y>", self._workspace_keyboard_redo, add="+")
        self.bind_all("<Control-Shift-Z>", self._workspace_keyboard_redo, add="+")
        self.show_home()

        # Première passe de géométrie pendant que la fenêtre est cachée.
        self.update_idletasks()

        # PRECHAUFFAGE_GLOBAL_TOMELINEA_V1
        # La fenêtre de préparation ne sert plus seulement au Visionneur :
        # elle réalise aussi, hors écran, les géométries des quatre bureaux.
        # Au clic, on bascule donc vers des panneaux déjà construits et mesurés.
        if callable(startup_progress):
            try:
                self.geometry("1280x800+-16000+-16000")
                self.deiconify()
                self.update_idletasks()
                self.update()

                startup_progress("Bureaux", "Préparation de Structure, Gabarits, Production et Sortie…")
                self._prewarm_workspace_shells()

                startup_progress("Visionneur", "Préparation du moteur intégré…")
                self.viewer3d_overlay.prewarm(
                    timeout_ms=12000,
                    progress=startup_progress,
                )
                self.withdraw()
                startup_progress("TomeLinea est prêt", "Ouverture du logiciel…")
            except Exception:
                try:
                    self.withdraw()
                except Exception:
                    pass

        # Affichage seulement quand la structure existe déjà et que le
        # Visionneur a eu l'occasion de se préchauffer.
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
            left, text="Projet actif et récents", bg=panel, fg=theme.INK,
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
            ("ouvrage_structure", "Livre structuré", green),
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
        self._home_source_path_var = tk.StringVar(value="")
        self._home_source_status_var = tk.StringVar(value="Choisissez d’abord le type de livre.")
        self._home_source_formats_var = tk.StringVar(value="")
        self._home_source_info = None
        self._home_source_analysis_token = 0
        self._home_source_analysis_queue = queue.Queue()
        self._home_source_wait_step = 0
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
            "ouvrage_structure": ("Livre structuré", green),
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

        # ----------------------------------------------------------
        # Source du projet — apparaît seulement après le choix du type.
        # Le garde-fou reflète les moteurs réellement disponibles :
        # aujourd’hui le PDF est analysé avant toute création du projet.
        # ----------------------------------------------------------
        self.home_source_panel = tk.Frame(
            self.home_creator_frame, bg=panel_alt, highlightthickness=1,
            highlightbackground=border,
        )
        self.home_source_panel.grid(row=3, column=0, sticky="ew", padx=18, pady=(9, 0), ipady=6)
        self.home_source_panel.grid_columnconfigure(0, weight=1)
        self.home_source_panel.grid_remove()

        source_head = tk.Frame(self.home_source_panel, bg=panel_alt)
        source_head.grid(row=0, column=0, sticky="ew", padx=12, pady=(7, 2))
        source_head.grid_columnconfigure(0, weight=1)
        tk.Label(
            source_head, text="SOURCE DU PROJET", bg=panel_alt, fg=theme.INK,
            font=(theme.FONT_UI, 8, "bold"), anchor="w",
        ).grid(row=0, column=0, sticky="w")
        self._home_source_button = V3Button(
            source_head, "Importer la source",
            self._home_choose_initial_source, primary=True, compact=True,
        )
        self._home_source_button.grid(row=0, column=1, sticky="e", padx=(10, 0))

        tk.Label(
            self.home_source_panel, textvariable=self._home_source_formats_var,
            bg=panel_alt, fg=theme.MUTED, font=(theme.FONT_UI, 7),
            justify="left", anchor="w", wraplength=610,
        ).grid(row=1, column=0, sticky="ew", padx=12, pady=(2, 2))
        self._home_source_status_label = tk.Label(
            self.home_source_panel, textvariable=self._home_source_status_var,
            bg=panel_alt, fg=theme.MUTED_DARK, font=(theme.FONT_UI, 8, "bold"),
            justify="left", anchor="w", wraplength=610,
        )
        self._home_source_status_label.grid(row=2, column=0, sticky="ew", padx=12, pady=(2, 6))

        or_row = tk.Frame(self.home_creator_frame, bg=theme.PANEL_ALT)
        or_row.grid(row=4, column=0, sticky="ew", padx=18, pady=(7, 6))
        or_row.grid_columnconfigure((0, 2), weight=1)
        tk.Frame(or_row, bg=border, height=1).grid(row=0, column=0, sticky="ew")
        tk.Label(or_row, text="  ou  ", bg=theme.PANEL_ALT, fg=theme.MUTED_DARK, font=(theme.FONT_UI, 7)).grid(row=0, column=1)
        tk.Frame(or_row, bg=border, height=1).grid(row=0, column=2, sticky="ew")

        model_card = tk.Frame(
            self.home_creator_frame, bg=panel_alt, highlightthickness=1,
            highlightbackground=border, cursor="hand2",
        )
        model_card.grid(row=5, column=0, sticky="ew", padx=18, ipady=5)
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
        self.home_model_picker.grid(row=6, column=0, sticky="ew", padx=18, pady=(5, 0))
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
        details.grid(row=7, column=0, sticky="ew", padx=18, pady=(8, 0))
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

        actions = tk.Frame(self.home_creator_frame, bg=theme.PANEL_ALT)
        actions.grid(row=8, column=0, sticky="ew", padx=18, pady=(7, 10))
        actions.grid_columnconfigure(0, weight=1)
        V3Button(actions, "Annuler", self._home_hide_creator, compact=True).grid(row=0, column=1, padx=(0, 7))
        self._home_create_button = V3Button(
            actions, "Créer le projet", self._home_create_project_inline,
            primary=True, compact=True, state="disabled",
        )
        self._home_create_button.grid(row=0, column=2)

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

            # V104 — le bandeau porteur des onglets reste AU-DESSUS de la surface
            # de travail en Structure/Gabarits. Pour Production/Sortie, C conserve
            # son rôle de panneau de commandes sous B.
            compact_tabs = active_tab in {"gabarits", "structure", "production"}
            if compact_tabs:
                c_h = 48
                c_y = margin_y + a_h + gap
                b_y = c_y + c_h + gap
                normal_b_h = max(290, h - b_y - margin_y)
            else:
                c_h = max(255, min(320, int(h * 0.285)))
                b_y = margin_y + a_h + gap
                normal_b_h = max(290, h - (margin_y * 2) - (gap * 2) - a_h - c_h)
                c_y = b_y + normal_b_h + gap

            self.zone_a.place(x=margin_x, y=margin_y, width=inner_w, height=a_h)
            self.zone_c.place(x=margin_x, y=c_y, width=inner_w, height=c_h)

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
                viewer = getattr(self, "viewer3d_overlay", None)
                viewer_active = bool(getattr(viewer, "active", False)) if viewer is not None else False
                if viewer_active:
                    # Une WebView native ne doit jamais être recouverte par la
                    # barre flottante Tk de la page, même après un Configure.
                    self.focus_toolbar.place_forget()
                else:
                    self.focus_toolbar.place(
                        x=toolbar_x,
                        y=toolbar_y,
                        width=toolbar_w,
                        height=toolbar_h,
                    )
                self.zone_b.tk.call("raise", self.zone_b._w)
                if not viewer_active:
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

    def _prewarm_workspace_shells(self) -> None:
        """Réalise une fois les quatre bureaux pendant la préouverture.

        Aucun projet n'est nécessaire ici : on prépare uniquement les widgets,
        géométries et panneaux persistants. Les données du livre restent chargées
        normalement quand l'utilisateur ouvre son projet.
        """
        canvas = getattr(self, "book_canvas", None)
        previous_suspend = bool(getattr(canvas, "_transition_render_suspended", False)) if canvas is not None else False
        if canvas is not None:
            canvas._transition_render_suspended = True

        previous_tab = str(getattr(self, "active_tab", "structure") or "structure")
        try:
            workspace = self._screens.get("workspace")
            if workspace is not None:
                workspace.tkraise()

            layout = getattr(self, "_workspace_layout_callback", None)
            for key, _label in theme.TAB_NAMES:
                self.active_tab = key
                frame = self.tab_frames.get(key)
                if frame is not None:
                    frame.tkraise()
                try:
                    if key in {"gabarits", "production"}:
                        self.tab_host.grid_remove()
                    else:
                        self.tab_host.grid()
                except Exception:
                    pass
                if callable(layout):
                    layout(None)
                self.update_idletasks()

            self.active_tab = previous_tab if previous_tab in self.tab_frames else "structure"
            self.tab_frames[self.active_tab].tkraise()
            try:
                if self.active_tab in {"gabarits", "production"}:
                    self.tab_host.grid_remove()
                else:
                    self.tab_host.grid()
            except Exception:
                pass
            if callable(layout):
                layout(None)
            self.update_idletasks()
        finally:
            if canvas is not None:
                # Supprime une éventuelle demande de rendu héritée d'un Configure
                # survenu juste avant la suspension, puis rend la main normalement.
                pending = getattr(canvas, "_render_pending", None)
                if pending is not None:
                    try:
                        canvas.after_cancel(pending)
                    except Exception:
                        pass
                    canvas._render_pending = None
                canvas._transition_render_suspended = previous_suspend
            home = self._screens.get("home")
            if home is not None:
                home.tkraise()

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

        # Actions contextuelles :
        # - Structure / Gabarits : consultation de la Source du livre ;
        # - Production : vrai Visionneur du livre composé.
        # Elles ne doivent jamais être présentées côte à côte.
        self.source_book_button = V3Button(
            actions, "Source du livre", self.open_source_book_viewer, compact=True, primary=True
        )
        # Source complémentaire : cette commande n'altère jamais la Source du
        # projet initiale. Elle n'apparaît qu'en Production et applique les
        # mêmes garde-fous que l'import proposé lors de la reprise d'un projet.
        self.add_to_book_button = V3Button(
            actions, "Importer une nouvelle source", self.add_to_book, compact=True
        )

        self.viewer3d_button = V3Button(
            actions, "Visionneur", self.open_viewer3d, compact=True, primary=True
        )

        self.undo_button = V3Button(actions, "Annuler", self._workspace_undo, compact=True, state="disabled")
        self.undo_button.pack(side="left", padx=3)
        self.redo_button = V3Button(actions, "Rétablir", self._workspace_redo, compact=True, state="disabled")
        self.redo_button.pack(side="left", padx=3)
        V3Button(actions, "Fermer", self.destroy, compact=True).pack(side="left", padx=(10, 0))
        self._update_history_buttons(False, False)
        self._update_workspace_context_actions("structure")

    def _update_workspace_context_actions(self, key: str | None = None):
        """Affiche uniquement les actions utiles au bureau actif."""
        active = str(key or getattr(self, "active_tab", "structure") or "structure")
        source_button = getattr(self, "source_book_button", None)
        add_button = getattr(self, "add_to_book_button", None)
        viewer_button = getattr(self, "viewer3d_button", None)
        undo_button = getattr(self, "undo_button", None)

        for button in (source_button, add_button, viewer_button):
            if button is not None:
                try:
                    button.pack_forget()
                except Exception:
                    pass

        pack_options = {"side": "left", "padx": 3}
        if undo_button is not None:
            pack_options["before"] = undo_button

        if active in {"structure", "gabarits"}:
            if source_button is not None:
                source_button.pack(**pack_options)
        elif active == "production":
            # Production est le lieu des nouvelles sources complémentaires et du vrai
            # Visionneur. Ces commandes n’encombrent pas les autres bureaux.
            if viewer_button is not None:
                viewer_button.pack(**pack_options)
            if add_button is not None:
                add_button.pack(**pack_options)

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

                # Structure — remplacement direct en 2 clics :
                # 1) sélectionner une ou plusieurs pages dans B ;
                # 2) cliquer le nouveau type dans C.
                # Tant qu'un dépôt multiple est déjà armé, un clic sur un autre
                # type continue toutefois de changer l'outil d'insertion.
                if not pending_type and canvas is not None:
                    try:
                        selected = (
                            list(canvas._selected_source_indices())
                            if hasattr(canvas, "_selected_source_indices")
                            else []
                        )
                    except Exception:
                        selected = []
                    if selected and str(getattr(canvas, "_structure_selection_kind", "") or "") == "page":
                        try:
                            replaced = bool(
                                hasattr(canvas, "structure_replace_selected_page_type")
                                and canvas.structure_replace_selected_page_type(str(type_key or ""))
                            )
                        except Exception:
                            replaced = False
                        reset_active_brick()
                        refresh_page_auto_ui()
                        # Même si la page est protégée ou si le type est déjà appliqué,
                        # le clic reste une tentative de remplacement et ne doit pas
                        # armer accidentellement un dépôt de page.
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
        """Gabarits : gauche = créer, centre = manipuler, droite = régler."""
        side_host = getattr(getattr(self, "book_canvas", None), "gabarit_tools_host", None)
        if side_host is not None:
            parent = side_host

        WORK_BG = "#102633"
        CARD_BORDER = "#385264"
        TEAL = "#78B8B1"
        TEXT = "#F0F2F0"
        MUTED = "#A9B4B8"

        parent.grid_rowconfigure(0, weight=1)
        parent.grid_columnconfigure(0, weight=1)

        atelier = tk.Frame(parent, bg=WORK_BG, highlightthickness=0, padx=10, pady=10)
        atelier.grid(row=0, column=0, sticky="nsew")
        atelier.grid_columnconfigure(0, weight=1)

        head = tk.Frame(atelier, bg=WORK_BG)
        head.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        tk.Label(
            head, text="OUTILS", bg=WORK_BG, fg=TEXT,
            font=(theme.FONT_TITLE, 10, "bold"),
        ).pack(anchor="w")
        state_var = tk.StringVar(value="Créer une zone")
        tk.Label(
            head, textvariable=state_var, bg=WORK_BG, fg=MUTED,
            font=(theme.FONT_UI, 7), anchor="w", justify="left", wraplength=180,
        ).pack(fill="x", pady=(3, 0))
        tk.Frame(atelier, bg=CARD_BORDER, height=1).grid(row=1, column=0, sticky="ew", pady=(0, 10))

        # ----------------------------------------------------------
        # GAUCHE = CRÉER. Rien d'autre : aucune navette centre→gauche→centre.
        # ----------------------------------------------------------
        create_card = tk.Frame(atelier, bg=WORK_BG, padx=8, pady=6)
        create_card.grid(row=2, column=0, sticky="new")
        create_card.grid_columnconfigure(0, weight=1)

        title_row = tk.Frame(create_card, bg=WORK_BG)
        title_row.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        tk.Label(
            title_row, text="1", bg=WORK_BG, fg=TEAL,
            font=(theme.FONT_TITLE, 11, "bold"),
        ).pack(side="left")
        tk.Label(
            title_row, text="CRÉER", bg=WORK_BG, fg=TEXT,
            font=(theme.FONT_TITLE, 8, "bold"),
        ).pack(side="left", padx=(7, 0))

        tk.Label(
            create_card,
            text="Le type choisi devient la nature attendue du contenu en Production.",
            bg=WORK_BG, fg=MUTED, font=(theme.FONT_UI, 7), justify="left",
            wraplength=175, anchor="w",
        ).grid(row=1, column=0, sticky="ew", pady=(0, 8))

        def book():
            return getattr(self, "book_canvas", None)

        for row, (kind, label) in enumerate((("text", "Texte"), ("image", "Image"), ("document", "Document")), start=2):
            def create_zone(k=kind):
                canvas = book()
                if canvas is not None:
                    canvas.gabarit_add_zone(k)
                    refresh_gabarit_tools()
            V3Button(create_card, label, create_zone, compact=True).grid(
                row=row, column=0, sticky="ew", pady=(0 if row == 2 else 4, 0),
            )

        tk.Label(
            create_card,
            text="Maj + clic dans la page : sélection multiple",
            bg=WORK_BG, fg=TEAL, font=(theme.FONT_UI, 7), justify="left",
            wraplength=175, anchor="w",
        ).grid(row=5, column=0, sticky="ew", pady=(12, 0))

        # ----------------------------------------------------------
        # Réglages globaux du livre : un seul accès dans l'inspecteur droit.
        # ----------------------------------------------------------
        def open_book_settings():
            if self._show_gabarit_book_settings_dialog(reopen=True):
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

        # ----------------------------------------------------------
        # Édition numérique précise : appelée depuis l'inspecteur contextuel droit.
        # Une seule petite palette, uniquement quand la précision en mm est voulue.
        # ----------------------------------------------------------
        self._gabarit_geometry_dialog = None

        def close_geometry_dialog():
            win = getattr(self, "_gabarit_geometry_dialog", None)
            self._gabarit_geometry_dialog = None
            if win is not None:
                try:
                    win.destroy()
                except Exception:
                    pass

        def open_zone_geometry():
            canvas = book()
            info = canvas.gabarit_selected_zone_info() if canvas is not None else {}
            if not info:
                return
            close_geometry_dialog()
            rect = dict(info.get("rect_mm") or {})

            win = tk.Toplevel(self)
            self._gabarit_geometry_dialog = win
            win.title("Position et dimensions")
            win.configure(bg=theme.WINDOW_DEEP)
            win.transient(self)
            win.resizable(False, False)
            try:
                win.attributes("-topmost", True)
            except tk.TclError:
                pass
            win.bind("<Escape>", lambda _e: close_geometry_dialog())

            panel = CutPanel(win, fill=theme.PANEL, border=theme.BORDER, cut=14, padding=(14, 12))
            panel.pack(fill="both", expand=True, padx=7, pady=7)
            body = panel.body
            body.grid_columnconfigure(1, weight=1)

            tk.Label(
                body, text="POSITION & DIMENSIONS", bg=theme.PANEL, fg=theme.INK,
                font=(theme.FONT_TITLE, 9, "bold"),
            ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 9))

            vars_ = {}
            entries = []
            for r, (key, label) in enumerate((("x","X"),("y","Y"),("w","Largeur"),("h","Hauteur")), start=1):
                tk.Label(
                    body, text=label, bg=theme.PANEL, fg=theme.INK_SOFT,
                    font=(theme.FONT_UI, 8),
                ).grid(row=r, column=0, sticky="w", pady=3, padx=(0, 10))
                var = tk.StringVar(value=f"{float(rect.get(key,0)):g}")
                vars_[key] = var
                entry = tk.Entry(
                    body, textvariable=var, width=10, justify="right",
                    bg="#182936", fg="#F2F3F1", insertbackground="#F2F3F1",
                    relief="flat", bd=0, highlightthickness=1,
                    highlightbackground=theme.BORDER, font=(theme.FONT_UI, 9),
                )
                entry.grid(row=r, column=1, sticky="ew", pady=3)
                entries.append(entry)
                tk.Label(
                    body, text="mm", bg=theme.PANEL, fg=theme.MUTED,
                    font=(theme.FONT_UI, 8),
                ).grid(row=r, column=2, sticky="w", padx=(5,0))

            error_var = tk.StringVar(value="")
            tk.Label(
                body, textvariable=error_var, bg=theme.PANEL, fg="#D99A9A",
                font=(theme.FONT_UI, 7), anchor="w",
            ).grid(row=5, column=0, columnspan=3, sticky="ew", pady=(5,0))

            def apply_geometry():
                try:
                    values = {k: float(v.get().strip().replace(",", ".")) for k,v in vars_.items()}
                except Exception:
                    error_var.set("Valeurs numériques uniquement")
                    return
                if not canvas.gabarit_set_selected_zone_rect_mm(values["x"], values["y"], values["w"], values["h"]):
                    error_var.set("Valeurs incompatibles avec la page")
                    return
                close_geometry_dialog()
                refresh_gabarit_tools()

            actions = tk.Frame(body, bg=theme.PANEL)
            actions.grid(row=6, column=0, columnspan=3, sticky="ew", pady=(9,0))
            actions.grid_columnconfigure(0, weight=1)
            V3Button(actions, "Annuler", close_geometry_dialog, compact=True).grid(row=0, column=0, sticky="ew", padx=(0,5))
            V3Button(actions, "Valider", apply_geometry, compact=True, primary=True).grid(row=0, column=1, sticky="ew")
            for entry in entries:
                entry.bind("<Return>", lambda _e: apply_geometry())
            if entries:
                entries[0].focus_set(); entries[0].selection_range(0, "end")

            win.update_idletasks()
            ww = max(320, win.winfo_reqwidth()); wh = max(230, win.winfo_reqheight())
            try:
                inspector = getattr(canvas, "gabarit_inspector_host", None)
                ix = inspector.winfo_rootx() if inspector is not None else self.winfo_rootx()+self.winfo_width()-240
                iy = inspector.winfo_rooty() if inspector is not None else self.winfo_rooty()+100
                x = max(self.winfo_rootx()+20, int(ix-ww-10))
                y = max(self.winfo_rooty()+70, int(iy+80))
            except Exception:
                x = self.winfo_rootx()+self.winfo_width()-ww-280
                y = self.winfo_rooty()+120
            win.geometry(f"{ww}x{wh}+{x}+{y}")
            win.lift()

        try:
            self.book_canvas.on_gabarit_edit_book_settings = open_book_settings
            self.book_canvas.on_gabarit_confirm_type_scope = confirm_type_scope
            self.book_canvas.on_gabarit_edit_zone_geometry = open_zone_geometry
            self.book_canvas.bind("<<GabaritEditBookSettings>>", lambda _e: open_book_settings(), add="+")
            self.book_canvas.bind("<<GabaritEditZoneGeometry>>", lambda _e: open_zone_geometry(), add="+")
        except Exception:
            pass

        def refresh_gabarit_tools(_event=None):
            canvas = book()
            if canvas is None:
                return
            try:
                infos = canvas.gabarit_selected_zone_infos()
            except Exception:
                infos = []
            if len(infos) == 1:
                kind = {"text":"Texte", "image":"Image", "document":"Document"}.get(str(infos[0].get("kind") or ""), "Zone")
                state_var.set(f"{kind} sélectionnée · réglez à droite")
            elif len(infos) > 1:
                state_var.set(f"{len(infos)} zones sélectionnées · actions à droite")
            else:
                state_var.set("Créer une zone")
            try:
                canvas._gabarit_inspector_signature = None
                canvas._render_gabarit_inspector_overlay(force=True)
            except Exception:
                pass

        self._refresh_gabarit_panel = refresh_gabarit_tools
        try:
            self.book_canvas.bind("<<GabaritPageChanged>>", refresh_gabarit_tools, add="+")
            self.book_canvas.bind("<<GabaritSelectionChanged>>", refresh_gabarit_tools, add="+")
            self.book_canvas.bind("<<StructurePaletteChanged>>", refresh_gabarit_tools, add="+")
        except Exception:
            pass
        self.after_idle(refresh_gabarit_tools)

    def _build_production_tab(self, parent):
        """Production partage désormais le même atelier plein B que Gabarits.

        Ce Frame reste uniquement un repli technique : les commandes visibles
        de Production sont portées par le rail latéral persistant de BookCanvas.
        Cela évite de reconstruire un deuxième poste de travail et garantit les
        mêmes repères, zooms et transitions.
        """
        parent.configure(bg=theme.PANEL)
        tk.Label(
            parent,
            text="Production — atelier commun avec Gabarits",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 8),
        ).pack(anchor="w", padx=12, pady=12)

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

    def _show_gabarit_book_settings_dialog(self, *, reopen: bool = False) -> bool:
        """Fenêtre unique des réglages globaux : format, marges et fond perdu.

        Elle s'ouvre une seule fois à la première entrée dans Gabarits pour une
        confirmation rapide, puis reste rappelable depuis l'unique bouton LIVRE.
        """
        canvas = getattr(self, "book_canvas", None)
        if canvas is None:
            return False

        current = canvas.gabarit_book_format()
        settings = canvas.gabarit_current_settings() or {}
        current_margins = dict(settings.get("margins_mm") or {})
        current_bleed = dict(settings.get("bleed_mm") or {})
        current_frame = "page" if str(settings.get("frame_reference") or "margins") == "page" else "margins"
        result = {"ok": False}

        win = tk.Toplevel(self)
        win.title("Réglages du livre")
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
            body, text="RÉGLAGES DU LIVRE", bg=theme.PANEL, fg=theme.INK,
            font=(theme.FONT_TITLE, 13, "bold"),
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            body,
            text=(
                "Ces valeurs sont communes à tout le livre. Elles sont définies au départ, "
                "puis rarement modifiées pendant le travail courant."
            ),
            bg=theme.PANEL, fg=theme.MUTED, justify="left", wraplength=590,
            font=(theme.FONT_UI, 8),
        ).grid(row=1, column=0, sticky="w", pady=(7, 14))

        # ---------- Format ----------
        format_card = tk.Frame(body, bg="#202D36", highlightthickness=1, highlightbackground="#465963")
        format_card.grid(row=2, column=0, sticky="ew", pady=(0, 9))
        format_card.grid_columnconfigure(1, weight=1)
        tk.Label(
            format_card, text="FORMAT FINI", bg="#202D36", fg=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 8, "bold"),
        ).grid(row=0, column=0, columnspan=5, sticky="w", padx=12, pady=(9, 6))

        catalog = canvas.gabarit_format_catalog()
        labels = [f"{item['label']} — {item['width_mm']:g} × {item['height_mm']:g} mm" for item in catalog]
        labels.append("Personnalisé")
        by_label = {label: item for label, item in zip(labels[:-1], catalog)}
        selected = tk.StringVar(value="Personnalisé")
        for choice, item in by_label.items():
            if (
                abs(float(item["width_mm"]) - float(current["width_mm"])) < .01
                and abs(float(item["height_mm"]) - float(current["height_mm"])) < .01
            ):
                selected.set(choice)
                break

        tk.Label(format_card, text="Format", bg="#202D36", fg=theme.INK, font=(theme.FONT_UI, 8, "bold")).grid(
            row=1, column=0, sticky="w", padx=(12, 10), pady=4,
        )
        menu = tk.OptionMenu(format_card, selected, *labels)
        menu.configure(
            bg=theme.PANEL_SOFT, fg=theme.INK, activebackground=theme.ACCENT_SOFT,
            activeforeground=theme.WHITE, relief="flat", bd=0, highlightthickness=0,
            font=(theme.FONT_UI, 8), width=31,
        )
        menu["menu"].configure(bg=theme.PANEL_SOFT, fg=theme.INK, font=(theme.FONT_UI, 8))
        menu.grid(row=1, column=1, columnspan=4, sticky="ew", padx=(0, 12), pady=4)

        width_var = tk.StringVar(value=f"{float(current['width_mm']):g}")
        height_var = tk.StringVar(value=f"{float(current['height_mm']):g}")
        tk.Label(format_card, text="Largeur", bg="#202D36", fg=theme.MUTED, font=(theme.FONT_UI, 8)).grid(row=2, column=0, sticky="w", padx=(12, 5), pady=(4, 10))
        width_entry = tk.Entry(format_card, textvariable=width_var, width=8, justify="right", bg=theme.PANEL_SOFT, fg=theme.INK, insertbackground=theme.INK, relief="flat", bd=0)
        width_entry.grid(row=2, column=1, sticky="ew", pady=(4, 10))
        tk.Label(format_card, text="mm   Hauteur", bg="#202D36", fg=theme.MUTED, font=(theme.FONT_UI, 8)).grid(row=2, column=2, sticky="w", padx=(6, 5), pady=(4, 10))
        height_entry = tk.Entry(format_card, textvariable=height_var, width=8, justify="right", bg=theme.PANEL_SOFT, fg=theme.INK, insertbackground=theme.INK, relief="flat", bd=0)
        height_entry.grid(row=2, column=3, sticky="ew", pady=(4, 10))
        tk.Label(format_card, text="mm", bg="#202D36", fg=theme.MUTED, font=(theme.FONT_UI, 8)).grid(row=2, column=4, sticky="w", padx=(5, 12), pady=(4, 10))

        # ---------- Marges + fond perdu ----------
        values_card = tk.Frame(body, bg=theme.PANEL)
        values_card.grid(row=3, column=0, sticky="ew", pady=(0, 7))
        values_card.grid_columnconfigure(0, weight=1, uniform="book_values")
        values_card.grid_columnconfigure(1, weight=1, uniform="book_values")

        def values_group(parent, title, specs, initial):
            box = tk.Frame(parent, bg="#202D36", highlightthickness=1, highlightbackground="#465963")
            tk.Label(box, text=title, bg="#202D36", fg=theme.ACCENT_BRIGHT, font=(theme.FONT_UI, 8, "bold")).grid(
                row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(9, 6),
            )
            box.grid_columnconfigure(1, weight=1)
            vars_ = {}
            for row, (key, label) in enumerate(specs, start=1):
                tk.Label(box, text=label, bg="#202D36", fg=theme.MUTED, font=(theme.FONT_UI, 8)).grid(row=row, column=0, sticky="w", padx=(12, 8), pady=3)
                var = tk.StringVar(value=f"{float(initial.get(key, 0.0)):g}")
                vars_[key] = var
                tk.Entry(box, textvariable=var, width=8, justify="right", bg=theme.PANEL_SOFT, fg=theme.INK, insertbackground=theme.INK, relief="flat", bd=0).grid(row=row, column=1, sticky="ew", pady=3)
                tk.Label(box, text="mm", bg="#202D36", fg=theme.MUTED, font=(theme.FONT_UI, 8)).grid(row=row, column=2, sticky="w", padx=(5, 12), pady=3)
            tk.Frame(box, bg="#202D36", height=5).grid(row=len(specs)+1, column=0)
            return box, vars_

        margins_box, margin_vars = values_group(
            values_card, "MARGES",
            (("top", "Haut"), ("bottom", "Bas"), ("inside", "Intérieure"), ("outside", "Extérieure")),
            current_margins,
        )
        margins_box.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        bleed_box, bleed_vars = values_group(
            values_card, "FOND PERDU",
            (("top", "Haut"), ("right", "Droite"), ("bottom", "Bas"), ("left", "Gauche")),
            current_bleed,
        )
        bleed_box.grid(row=0, column=1, sticky="nsew", padx=(5, 0))

        # ---------- Cadre de travail général ----------
        frame_card = tk.Frame(body, bg="#202D36", highlightthickness=1, highlightbackground="#465963")
        frame_card.grid(row=4, column=0, sticky="ew", pady=(2, 9))
        frame_card.grid_columnconfigure(1, weight=1)
        tk.Label(
            frame_card, text="CADRE DE TRAVAIL PAR DÉFAUT", bg="#202D36", fg=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 8, "bold"),
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=12, pady=(9, 4))
        tk.Label(
            frame_card, text="Limite normale de composition du livre", bg="#202D36", fg=theme.MUTED,
            font=(theme.FONT_UI, 7),
        ).grid(row=1, column=0, sticky="w", padx=(12, 12), pady=(0, 8))
        frame_var = tk.StringVar(value=current_frame)
        choices = tk.Frame(frame_card, bg="#202D36")
        choices.grid(row=1, column=1, columnspan=2, sticky="e", padx=(8, 12), pady=(0, 8))
        for label, value in (("Marges", "margins"), ("Page", "page")):
            tk.Radiobutton(
                choices, text=label, variable=frame_var, value=value,
                bg="#202D36", fg=theme.INK, activebackground="#202D36",
                activeforeground=theme.WHITE, selectcolor=theme.PANEL_SOFT,
                font=(theme.FONT_UI, 8), cursor="hand2",
            ).pack(side="left", padx=(0, 12))

        # ---------- Adaptation si le format change ----------
        adapt_frame = tk.Frame(body, bg="#282E31", highlightthickness=1, highlightbackground="#5B5547")
        adapt_frame.grid(row=5, column=0, sticky="ew", pady=(3, 7))
        adapt_frame.grid_columnconfigure(0, weight=1)
        tk.Label(
            adapt_frame, text="CHANGEMENT DE FORMAT", bg="#282E31", fg="#D1B979",
            font=(theme.FONT_UI, 8, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=12, pady=(8, 4))
        tk.Label(
            adapt_frame,
            text=(
                "Des gabarits ou contenus existent déjà. Choisissez comment les adapter. "
                "Les images gardent leurs proportions ; le texte reste attaché à sa zone."
            ),
            bg="#282E31", fg=theme.MUTED, justify="left", wraplength=555,
            font=(theme.FONT_UI, 7),
        ).grid(row=1, column=0, sticky="w", padx=12, pady=(0, 5))
        adapt_mode = tk.StringVar(value="proportional")
        tk.Radiobutton(
            adapt_frame, text="Adapter proportionnellement au nouveau format — recommandé",
            variable=adapt_mode, value="proportional", bg="#282E31", fg=theme.INK,
            activebackground="#282E31", activeforeground=theme.WHITE, selectcolor=theme.PANEL_SOFT,
            font=(theme.FONT_UI, 8), anchor="w",
        ).grid(row=2, column=0, sticky="ew", padx=10)
        tk.Radiobutton(
            adapt_frame, text="Conserver les dimensions physiques des objets",
            variable=adapt_mode, value="physical", bg="#282E31", fg=theme.INK,
            activebackground="#282E31", activeforeground=theme.WHITE, selectcolor=theme.PANEL_SOFT,
            font=(theme.FONT_UI, 8), anchor="w",
        ).grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 7))

        note = tk.Label(
            body,
            text="Marges et fond perdu restent toujours des valeurs physiques en millimètres.",
            bg=theme.PANEL, fg=theme.MUTED, font=(theme.FONT_UI, 7),
        )
        note.grid(row=6, column=0, sticky="w", pady=(2, 0))

        error = tk.StringVar(value="")
        tk.Label(body, textvariable=error, bg=theme.PANEL, fg="#E1A0A0", font=(theme.FONT_UI, 8)).grid(
            row=7, column=0, sticky="w", pady=(5, 0),
        )
        actions = tk.Frame(body, bg=theme.PANEL)
        actions.grid(row=8, column=0, sticky="e", pady=(12, 0))

        has_composition = bool(canvas.gabarit_has_existing_composition())

        def selected_dimensions():
            item = by_label.get(selected.get())
            if item is not None:
                return float(item["width_mm"]), float(item["height_mm"])
            try:
                return float(width_var.get().replace(",", ".")), float(height_var.get().replace(",", "."))
            except Exception:
                return None

        def refresh_format_state(*_):
            item = by_label.get(selected.get())
            is_custom = item is None
            width_entry.configure(state="normal" if is_custom else "disabled")
            height_entry.configure(state="normal" if is_custom else "disabled")
            if item is not None:
                target_w = f"{float(item['width_mm']):g}"
                target_h = f"{float(item['height_mm']):g}"
                if width_var.get() != target_w:
                    width_var.set(target_w)
                if height_var.get() != target_h:
                    height_var.set(target_h)
            dims = selected_dimensions()
            changed = bool(
                dims is not None
                and (
                    abs(dims[0] - float(current["width_mm"])) > .01
                    or abs(dims[1] - float(current["height_mm"])) > .01
                )
            )
            if changed and has_composition:
                adapt_frame.grid()
            else:
                adapt_frame.grid_remove()

        def close_cancel():
            result["ok"] = False
            try:
                win.grab_release()
            except Exception:
                pass
            win.destroy()

        def confirm():
            try:
                dims = selected_dimensions()
                if dims is None:
                    raise ValueError
                width, height = dims
                margins = {k: float(v.get().replace(",", ".")) for k, v in margin_vars.items()}
                bleed = {k: float(v.get().replace(",", ".")) for k, v in bleed_vars.items()}
            except Exception:
                error.set("Vérifiez les valeurs numériques.")
                return

            catalog_item = by_label.get(selected.get())
            if catalog_item is None:
                format_id, label = "custom", "Personnalisé"
            else:
                format_id, label = str(catalog_item["id"]), str(catalog_item["label"])

            if not canvas.gabarit_apply_book_settings(
                format_id, label, width, height, margins, bleed, adapt_mode.get(),
                frame_reference=frame_var.get(),
            ):
                error.set("Réglages incompatibles : vérifiez format, marges et fond perdu.")
                return

            result["ok"] = True
            try:
                win.grab_release()
            except Exception:
                pass
            win.destroy()

        V3Button(actions, "Annuler", close_cancel, compact=True).pack(side="right", padx=(6, 0))
        V3Button(actions, "Confirmer", confirm, compact=True, primary=True).pack(side="right")

        selected.trace_add("write", refresh_format_state)
        width_var.trace_add("write", refresh_format_state)
        height_var.trace_add("write", refresh_format_state)
        refresh_format_state()

        win.protocol("WM_DELETE_WINDOW", close_cancel)
        win.bind("<Escape>", lambda _e: close_cancel())
        win.update_idletasks()
        w, h = 650, 690
        x = self.winfo_rootx() + max(0, (self.winfo_width() - w) // 2)
        y = self.winfo_rooty() + max(0, (self.winfo_height() - h) // 2)
        win.geometry(f"{w}x{h}+{x}+{y}")
        win.wait_window()
        return bool(result["ok"])

    # Ancien nom conservé uniquement pour compatibilité interne avec d'éventuels
    # appels historiques. Il ouvre désormais la fenêtre unique.
    def _show_gabarit_format_dialog(self, *, force_change: bool = False) -> bool:
        return self._show_gabarit_book_settings_dialog(reopen=bool(force_change))

    def _ensure_gabarit_format_for_session(self) -> bool:
        key = self._gabarit_format_session_key()
        if getattr(self, "_gabarit_format_session_confirmed", None) == key:
            return True
        if not self._show_gabarit_book_settings_dialog(reopen=False):
            return False
        self._gabarit_format_session_confirmed = key
        return True

    def select_tab(self, key: str):
        if key not in self.tab_frames:
            return
        if key == "gabarits" and not self._ensure_gabarit_format_for_session():
            return

        previous = str(getattr(self, "active_tab", "structure") or "structure")
        if key == previous:
            # Un clic sur le bureau déjà actif ne doit jamais provoquer un rendu,
            # mais on synchronise quand même l'état visuel des onglets (notamment
            # pendant la construction initiale de l'interface).
            focus_toolbar = getattr(self, "focus_toolbar", None)
            if focus_toolbar is not None:
                focus_toolbar.set_active_tab(key)
            for tab_key, button in self.tab_buttons.items():
                if tab_key == key:
                    button.configure(bg=theme.ACCENT_DARK, fg=theme.WHITE)
                else:
                    button.configure(bg=theme.PANEL_SOFT, fg=theme.INK)
            self._update_workspace_context_actions(key)
            return

        book_canvas = getattr(self, "book_canvas", None)
        if book_canvas is not None:
            book_canvas._transition_render_suspended = True
            pending = getattr(book_canvas, "_render_pending", None)
            if pending is not None:
                try:
                    book_canvas.after_cancel(pending)
                except Exception:
                    pass
                book_canvas._render_pending = None

        try:
            # TRANSITIONS_PRECHAUFFEES_V1
            # 1) On place d'abord le bureau demandé dans sa géométrie FINALE.
            # 2) Le Canvas ne rend qu'une seule fois, une fois cette géométrie fixée.
            # Ainsi aucune étape intermédiaire n'est peinte à l'écran.
            self.active_tab = key
            self.tab_frames[key].tkraise()

            tab_host = getattr(self, "tab_host", None)
            if tab_host is not None:
                try:
                    if key in {"gabarits", "production"}:
                        tab_host.grid_remove()
                    else:
                        tab_host.grid()
                except Exception:
                    pass

            layout = getattr(self, "_workspace_layout_callback", None)
            if callable(layout):
                layout(None)

            if book_canvas is not None and hasattr(book_canvas, "set_work_mode"):
                book_canvas.set_work_mode(key)

            if key == "gabarits":
                refresher = getattr(self, "_refresh_gabarit_panel", None)
                if callable(refresher):
                    try:
                        refresher()
                    except Exception:
                        pass
        finally:
            if book_canvas is not None:
                book_canvas._transition_render_suspended = False

        focus_toolbar = getattr(self, "focus_toolbar", None)
        if focus_toolbar is not None:
            focus_toolbar.set_active_tab(key)
        for tab_key, button in self.tab_buttons.items():
            if tab_key == key:
                button.configure(bg=theme.ACCENT_DARK, fg=theme.WHITE)
            else:
                button.configure(bg=theme.PANEL_SOFT, fg=theme.INK)
        self._update_workspace_context_actions(key)

    # ------------------------------------------------------------------
    # Visionneur 3D intégré
    # ------------------------------------------------------------------

    def _viewer_current_page_number(self) -> int:
        canvas = getattr(self, "book_canvas", None)
        items = list(getattr(canvas, "items", []) or []) if canvas is not None else []
        if not items:
            return 1
        index = getattr(canvas, "_selected_index", None)
        try:
            index = int(index) if index is not None else 0
        except Exception:
            index = 0
        index = max(0, min(len(items) - 1, index))
        return index + 1

    def _viewer_page_count(self) -> int:
        canvas = getattr(self, "book_canvas", None)
        items = list(getattr(canvas, "items", []) or []) if canvas is not None else []
        return max(1, len(items))

    def _viewer_pages_info(self) -> list[dict]:
        """Données des deux panneaux « Règles appliquées » du Visionneur.

        Le dessin reprend le panneau validé du prototype autonome V4.21 ; ici,
        contrairement au prototype, les valeurs sont alimentées par l'état réel
        de Structure et de Gabarits.
        """
        canvas = getattr(self, "book_canvas", None)
        items = list(getattr(canvas, "items", []) or []) if canvas is not None else []
        groups = list(getattr(canvas, "groups", []) or []) if canvas is not None else []
        if canvas is None or not items:
            return []

        group_by_id = {
            str(group.get("id") or ""): group
            for group in groups
            if isinstance(group, dict)
        }
        number_by_id = {
            str(item.get("id") or ""): index + 1
            for index, item in enumerate(items)
            if isinstance(item, dict) and str(item.get("id") or "")
        }

        def _type_label(type_key: str) -> str:
            key = str(type_key or "").strip()
            if not key:
                return ""
            try:
                definition = canvas._structure_type_definition(key)
                label = str(definition.get("short_label") or definition.get("label") or "").strip()
                if label:
                    return label
            except Exception:
                pass
            return key.replace("_", " ").strip().capitalize()

        infos: list[dict] = []
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                item = {}
            page_number = index + 1

            # TOMELINEA_VISIONNEUR_4_FACES_RECTO_VERSO_V1
            # Les quatre faces physiques de la couverture ne dépendent pas
            # de la parité de leur position dans la Structure.
            raw_page_type = str(
                item.get("type")
                or item.get("kind")
                or item.get("page_type")
                or ""
            ).strip().lower()

            cover_physical_sides = {
                "couverture": "recto",
                "cover": "recto",
                "front_cover": "recto",

                "deuxieme_couverture": "verso",
                "2e_couverture": "verso",
                "second_cover": "verso",
                "inside_front_cover": "verso",

                "troisieme_couverture": "recto",
                "3e_couverture": "recto",
                "third_cover": "recto",
                "inside_back_cover": "recto",

                "quatrieme": "verso",
                "quatrieme_couverture": "verso",
                "4e_couverture": "verso",
                "back_cover": "verso",
            }

            physical_side = cover_physical_sides.get(
                raw_page_type,
                "recto" if index % 2 == 0 else "verso",
            )

            try:
                page_type = str(canvas._page_type_label(item, index) or "Page")
            except Exception:
                page_type = str(item.get("type") or item.get("kind") or "Page").replace("_", " ").strip().capitalize()

            try:
                page_name = str(canvas._page_display_name(item, index) or "")
            except Exception:
                page_name = str(item.get("page_name") or item.get("display_name") or "").strip()

            try:
                group_id = str(canvas._item_group_id(item) or "")
            except Exception:
                group_id = str(item.get("plan_group") or item.get("group_id") or "")
            group = group_by_id.get(group_id, {})
            try:
                part_name = str(canvas._group_name(group) or "") if group else ""
                part_title = str(canvas._group_part_title(group) or "") if group else ""
            except Exception:
                part_name = str(group.get("title") or group.get("name") or "").strip() if group else ""
                part_title = str(group.get("part_title") or group.get("titre_partie") or "").strip() if group else ""
            if part_title in {"", "Titre à définir"}:
                part_text = part_name
            elif part_name:
                part_text = f"{part_name} — {part_title}"
            else:
                part_text = part_title

            source_type = ""
            try:
                source_type = str(canvas._type_of(item) or "")
            except Exception:
                source_type = str(item.get("type") or item.get("kind") or "")

            # Recto / Verso : côté physique + éventuelle règle imposée.
            try:
                effective_side = str(canvas._effective_recto_verso_rule(item) or "")
                general_side = str(canvas.structure_get_recto_verso_type_rule(source_type) or "") if source_type else ""
                rv_override = canvas._recto_verso_override_value(item)
            except Exception:
                effective_side = str(item.get("structure_side") or "").strip().lower()
                general_side = ""
                rv_override = item.get("recto_verso_override") if "recto_verso_override" in item else None
            rv_rule = effective_side if effective_side in {"recto", "verso"} else ""
            rv_exception = bool(general_side in {"recto", "verso"} and rv_override == "__none__")

            # Pages automatiques AV / AP : valeur réelle de la règle et exceptions locales.
            auto_rows = {}
            auto_exceptions: list[str] = []
            for position, code in (("before", "AV"), ("after", "AP")):
                try:
                    general_target = str(canvas.structure_get_page_auto_type_rule(source_type, position) or "") if source_type else ""
                    override = canvas._page_auto_override_value(item, position)
                    effective_target = str(canvas._structure_page_auto_type(item, position) or "")
                except Exception:
                    general_target = ""
                    override = item.get(f"page_auto_{position}_override") if f"page_auto_{position}_override" in item else None
                    effective_target = "" if override == "__none__" else str(override or "")
                excluded = bool(general_target and override == "__none__")
                if excluded:
                    auto_exceptions.append(code)
                auto_rows[code] = {
                    "target": _type_label(effective_target),
                    "excluded": excluded,
                    "general": _type_label(general_target),
                }

            # Double page : paire réelle, rôle gauche/droite et ancienne exception si rencontrée.
            try:
                pair_id = str(canvas._double_page_pair_id(item) or "")
                pair_role = str(canvas._double_page_pair_role(item) or "")
                dp_general = bool(canvas.structure_get_double_page_type_rule(source_type)) if source_type else False
                dp_override = canvas._double_page_override_value(item)
            except Exception:
                pair_id = str(item.get("double_page_pair_id") or "")
                pair_role = str(item.get("double_page_role") or "")
                dp_general = False
                dp_override = item.get("double_page_override") if "double_page_override" in item else None
            double_page = bool(pair_id)
            dp_exception = bool(dp_general and dp_override == "__none__")

            # Gabarit : état, portée et exception locale réelle.
            try:
                gabarit_status = str(canvas._gabarit_status(item) or "non_commence")
                gabarit_scope = str(canvas._gabarit_item_last_scope(item) or "")
                gabarit_exception = bool(canvas._gabarit_is_local_exception(item, index))
            except Exception:
                gabarit_status = str(item.get("gabarit_status") or "non_commence")
                gabarit_scope = str(item.get("gabarit_scope_last") or "")
                gabarit_exception = bool(item.get("gabarit_local_override"))
            status_labels = {"termine": "Terminé", "en_cours": "En cours", "non_commence": "Non commencé"}
            scope_labels = {"type": "Toutes du type", "page": "Cette page"}
            try:
                production_status = str(canvas._production_status(item) or "vierge")
                production_validation_exception = bool(canvas.production_validation_exception(item))
            except Exception:
                production_status = str(item.get("production_status") or "vierge").strip().lower()
                production_validation_exception = bool(item.get("production_validation_exception", False))
            production_status_labels = {
                "vierge": "Vierge",
                "en_cours": "En cours",
                "validee": "Validée",
            }
            gabarit_text = page_type
            if gabarit_scope in scope_labels:
                gabarit_text = f"{gabarit_text} · {scope_labels[gabarit_scope]}"
            elif gabarit_status == "non_commence":
                gabarit_text = "Non défini"

            exceptions: list[str] = []
            if rv_exception:
                exceptions.append("Recto / Verso")
            exceptions.extend(f"Page auto {code}" for code in auto_exceptions)
            if dp_exception:
                exceptions.append("Double page")
            if gabarit_exception:
                exceptions.append("Gabarit local")

            # Cas particulier d'une page matérielle générée automatiquement.
            try:
                is_auto = bool(canvas._is_automatic_page(item))
                auto_roles = list(canvas._automatic_roles(item)) if is_auto else []
            except Exception:
                is_auto = bool(item.get("automatic") or item.get("auto_generated") or item.get("automatic_recto_verso"))
                auto_roles = list(item.get("automatic_roles") or []) if isinstance(item.get("automatic_roles"), list) else []

            automatic_origin = ""
            automatic_reason = ""
            if is_auto:
                role_labels: list[str] = []
                source_numbers: list[int] = []
                for role in auto_roles:
                    if not isinstance(role, dict):
                        continue
                    code = str(role.get("code") or "").upper()
                    if code and code not in role_labels:
                        role_labels.append(code)
                    source_no = number_by_id.get(str(role.get("source_id") or ""))
                    if source_no and source_no not in source_numbers:
                        source_numbers.append(source_no)
                readable_roles = {
                    "AV": "Page auto avant", "AP": "Page auto après",
                    "R": "Recto", "V": "Verso", "DP": "Double page",
                }
                automatic_origin = " + ".join(readable_roles.get(code, code) for code in role_labels) or "Règle structurelle"
                if source_numbers:
                    target_text = ", ".join(f"page {n}" for n in source_numbers)
                    automatic_reason = f"Créée automatiquement pour {target_text} afin de respecter {automatic_origin.lower()}."
                else:
                    automatic_reason = f"Créée automatiquement afin de respecter {automatic_origin.lower()}."

            badges: list[str] = []
            if rv_rule:
                badges.append("R" if rv_rule == "recto" else "V")
            if double_page:
                badges.append("2P")
            for code in ("AV", "AP"):
                if auto_rows[code]["target"]:
                    badges.append(code)
            if is_auto:
                badges.append("AUTO")
            badges = list(dict.fromkeys(badges))



            page_snapshot = ""
            try:
                from src.gui_v3.viewer_page_snapshot import build_page_snapshot
                page_snapshot = build_page_snapshot(
                    canvas, item, page_number, width=1400, quality=92
                )
            except Exception:
                page_snapshot = ""

            infos.append({
                "number": page_number,
                "physicalSide": physical_side,
                "type": page_type,
                "name": page_name,
                "part": part_text,
                "badges": badges,
                "rectoVersoRule": rv_rule,
                "rectoVersoException": rv_exception,
                "autoBefore": auto_rows["AV"],
                "autoAfter": auto_rows["AP"],
                "doublePage": double_page,
                "doublePageRole": pair_role,
                "exceptions": exceptions,
                "gabarit": gabarit_text,
                "gabaritStatus": status_labels.get(gabarit_status, gabarit_status.replace("_", " ").capitalize()),
                "gabaritException": gabarit_exception,
                "productionStatus": production_status_labels.get(production_status, production_status.replace("_", " ").capitalize()),
                "productionStatusKey": production_status,
                "productionValidationException": production_validation_exception,
                "snapshot": page_snapshot,
                "automatic": is_auto,
                "automaticOrigin": automatic_origin,
                "automaticReason": automatic_reason,
            })
        return infos

    def open_viewer3d(self) -> None:
        if self.context is None:
            return
        viewer = getattr(self, "viewer3d_overlay", None)
        if viewer is None:
            return

        # Une WebView native peut passer sous certains widgets Tk déjà mappés.
        # On masque explicitement les surimpressions de page pendant le
        # Visionneur, puis on les restaure seulement lors d'un Retour normal.
        canvas = getattr(self, "book_canvas", None)
        self._viewer_restore_page_overlay = False
        if canvas is not None:
            overlay_frame = getattr(canvas, "page_overlay_frame", None)
            overlay_active = bool(getattr(canvas, "_overlay_active", False))
            overlay_mapped = False
            if overlay_frame is not None:
                try:
                    overlay_mapped = bool(overlay_frame.winfo_ismapped())
                except Exception:
                    overlay_mapped = False
            self._viewer_restore_page_overlay = bool(overlay_active and overlay_mapped)
            if self._viewer_restore_page_overlay and overlay_frame is not None:
                try:
                    overlay_frame.place_forget()
                except Exception:
                    pass

        focus_toolbar = getattr(self, "focus_toolbar", None)
        if focus_toolbar is not None:
            try:
                focus_toolbar.place_forget()
            except Exception:
                pass

        # Annuler dans le Visionneur ne doit jamais remonter dans l'historique
        # d'une action réalisée auparavant dans Structure/Gabarits. La session
        # commence donc avec zéro action locale annulable.
        self._viewer_session_undo_steps = 0
        self._viewer_session_redo_steps = 0
        viewer.show(
            origin_tab=str(getattr(self, "active_tab", "structure") or "structure"),
            page=self._viewer_current_page_number(),
            page_count=self._viewer_page_count(),
            pages_info=self._viewer_pages_info(),
            can_undo=False,
            can_redo=False,
        )

    def _viewer_action(self, action: str, page_number: int) -> dict:
        canvas = getattr(self, "book_canvas", None)
        if canvas is None or self.context is None:
            return {"ok": False, "message": "Aucun projet actif."}

        items = list(getattr(canvas, "items", []) or [])
        if not items:
            return {"ok": False, "message": "Le livre ne contient aucune page."}
        try:
            index = max(0, min(len(items) - 1, int(page_number) - 1))
        except Exception:
            index = 0

        ok = False
        message = ""
        target_index = index

        if action in {"insert_blank_before", "insert_blank_after"}:
            # L'ajout AV/AP conserve la page source affichée. Si l'insertion est
            # faite avant, son numéro physique change mais pas la page suivie.
            source_id = str(items[index].get("id") or "") if 0 <= index < len(items) else ""
            position = "before" if action.endswith("before") else "after"
            result = canvas.viewer_insert_blank_relative(index, position)
            ok = bool(result.get("ok"))
            message = str(result.get("message") or "")
            if ok:
                self._viewer_session_undo_steps = int(getattr(self, "_viewer_session_undo_steps", 0) or 0) + 1
                self._viewer_session_redo_steps = 0
            if ok and source_id:
                target_index = next(
                    (
                        i for i, candidate in enumerate(getattr(canvas, "items", []) or [])
                        if str(candidate.get("id") or "") == source_id
                    ),
                    index,
                )
            else:
                try:
                    target_index = int(result.get("page_index", index))
                except Exception:
                    target_index = index

        elif action == "delete_page":
            info = next((row for row in self._viewer_pages_info() if int(row.get("number") or 0) == index + 1), {})
            label = str(info.get("type") or "Page")
            if bool(info.get("automatic")):
                label += " · automatique"
            confirmed = messagebox.askyesno(
                "Supprimer la page",
                f"Supprimer la page {index + 1} — {label} ?\n\n"
                "TomeLinea recalculera immédiatement la Structure, les pages automatiques et les Gabarits.\n"
                "Tu pourras utiliser Annuler dans le Visionneur si nécessaire.",
                parent=self,
            )
            if not confirmed:
                return {
                    "ok": False,
                    "message": "Suppression annulée.",
                    "page": index + 1,
                    "page_count": len(items),
                    "pages_info": self._viewer_pages_info(),
                    "can_undo": bool(getattr(self, "_viewer_session_undo_steps", 0)),
                    "can_redo": bool(getattr(self, "_viewer_session_redo_steps", 0)),
                }
            result = canvas.viewer_delete_physical_page(index)
            ok = bool(result.get("ok"))
            message = str(result.get("message") or "")
            if ok:
                self._viewer_session_undo_steps = int(getattr(self, "_viewer_session_undo_steps", 0) or 0) + 1
                self._viewer_session_redo_steps = 0
            if ok:
                # Seule une suppression fait reculer automatiquement d'une page.
                target_index = max(0, index - 1)
            else:
                try:
                    target_index = int(result.get("page_index", index))
                except Exception:
                    target_index = index

        elif action == "undo":
            steps = int(getattr(self, "_viewer_session_undo_steps", 0) or 0)
            if steps <= 0:
                return {
                    "ok": False,
                    "message": "Rien à annuler dans cette session du Visionneur.",
                    "page": index + 1,
                    "page_count": len(items),
                    "pages_info": self._viewer_pages_info(),
                    "can_undo": False,
                    "can_redo": bool(getattr(self, "_viewer_session_redo_steps", 0)),
                }
            ok = bool(canvas.structure_undo())
            if ok:
                self._viewer_session_undo_steps = max(0, steps - 1)
                self._viewer_session_redo_steps = int(getattr(self, "_viewer_session_redo_steps", 0) or 0) + 1
            message = "Dernière modification du Visionneur annulée." if ok else "Impossible d’annuler cette modification."
            target_index = max(0, min(index, max(0, len(getattr(canvas, "items", []) or []) - 1)))

        elif action == "redo":
            steps = int(getattr(self, "_viewer_session_redo_steps", 0) or 0)
            if steps <= 0:
                return {
                    "ok": False,
                    "message": "Rien à rétablir dans cette session du Visionneur.",
                    "page": index + 1,
                    "page_count": len(items),
                    "pages_info": self._viewer_pages_info(),
                    "can_undo": bool(getattr(self, "_viewer_session_undo_steps", 0)),
                    "can_redo": False,
                }
            ok = bool(canvas.structure_redo())
            if ok:
                self._viewer_session_redo_steps = max(0, steps - 1)
                self._viewer_session_undo_steps = int(getattr(self, "_viewer_session_undo_steps", 0) or 0) + 1
            message = "Dernière modification du Visionneur rétablie." if ok else "Impossible de rétablir cette modification."
            target_index = max(0, min(index, max(0, len(getattr(canvas, "items", []) or []) - 1)))
        else:
            return {"ok": False, "message": "Action inconnue."}

        # Le même modèle alimente Structure, Gabarits et Visionneur. Après
        # l'action, on renvoie simplement l'état central recalculé au WebView.
        self._refresh_workspace_state()
        self._update_history_buttons()
        page_count = self._viewer_page_count()
        if page_count > 0:
            target_index = max(0, min(page_count - 1, target_index))
            try:
                canvas._set_single_page_selection(target_index)
            except Exception:
                pass
        return {
            "ok": ok,
            "message": message or ("Action effectuée." if ok else "Action impossible."),
            "page": target_index + 1 if page_count else 1,
            "page_count": max(1, page_count),
            "pages_info": self._viewer_pages_info(),
            "can_undo": bool(getattr(self, "_viewer_session_undo_steps", 0)),
            "can_redo": bool(getattr(self, "_viewer_session_redo_steps", 0)),
        }

    def _navigate_from_viewer(self, target_tab: str, page_number: int) -> None:
        """Quitte le Visionneur vers la page exacte dans le bureau demandé."""
        self._viewer_restore_page_overlay = False
        canvas = getattr(self, "book_canvas", None)
        if canvas is not None and bool(getattr(canvas, "_overlay_active", False)):
            try:
                canvas.close_page_overlay()
            except Exception:
                pass
        self._return_from_viewer(str(target_tab or "structure"), int(page_number or 1))

    def _return_from_viewer(self, origin_tab: str, page_number: int) -> None:
        # Le retour rétablit le bureau d'origine puis sélectionne la page
        # réellement suivie par le Visionneur.
        if self.context is None:
            return
        origin_tab = str(origin_tab or "structure")
        if origin_tab not in getattr(self, "tab_frames", {}):
            origin_tab = "structure"

        self._screens["workspace"].tkraise()
        self.select_tab(origin_tab)

        canvas = getattr(self, "book_canvas", None)
        items = list(getattr(canvas, "items", []) or []) if canvas is not None else []
        if canvas is None or not items:
            return
        try:
            index = max(0, min(len(items) - 1, int(page_number) - 1))
        except Exception:
            index = 0

        selected = False
        if origin_tab == "gabarits" and hasattr(canvas, "gabarit_select_index"):
            try:
                selected = bool(canvas.gabarit_select_index(index, preserve_zoom=True))
            except Exception:
                selected = False

        if not selected:
            try:
                canvas._set_single_page_selection(index)
                canvas.render()
                canvas.after_idle(canvas.center_selected)
                selected = True
            except Exception:
                selected = False

        if bool(getattr(self, "_viewer_restore_page_overlay", False)) and selected:
            overlay_frame = getattr(canvas, "page_overlay_frame", None)
            if overlay_frame is not None and bool(getattr(canvas, "_overlay_active", False)):
                try:
                    canvas._overlay_page_index = index
                    overlay_frame.place(x=0, y=0, relwidth=1, relheight=1)
                    overlay_frame.tk.call("raise", overlay_frame._w)
                    canvas._schedule_overlay_render()
                except Exception:
                    pass
        self._viewer_restore_page_overlay = False

        # La barre flottante de page ne revient qu'après disparition de la WebView.
        layout = getattr(self, "_workspace_layout_callback", None)
        if callable(layout):
            try:
                self.after_idle(lambda: layout(None))
            except Exception:
                pass

    def destroy(self) -> None:
        viewer = getattr(self, "viewer3d_overlay", None)
        if viewer is not None:
            try:
                viewer.shutdown()
            except Exception:
                pass
        super().destroy()

    # ------------------------------------------------------------------
    # Projet / import
    # ------------------------------------------------------------------

    def open_create_dialog(self):
        self._home_new_type_var.set("")
        self._home_new_origin_var.set("")
        self._home_new_name_var.set("")
        self._home_model_path_var.set("")
        self._home_reset_initial_source(hide_panel=True)
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
        self._home_reset_initial_source(hide_panel=True)

    def _home_select_type(self, key: str):
        self._home_new_origin_var.set("type")
        self._home_new_type_var.set(key)
        self._home_model_path_var.set("")
        self.home_model_picker.grid_remove()
        self._home_reset_initial_source(hide_panel=False)
        self._home_refresh_source_panel()
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
                photo = self._home_type_icon_glow(key, 72, selected=active)
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

    def _home_effective_project_type(self) -> str:
        origin = self._home_new_origin_var.get()
        if origin == "type":
            return self._home_new_type_var.get()
        if origin == "modele":
            model_path = self._home_model_path_var.get().strip()
            for item in getattr(self, "_home_models", []):
                if item.get("path") == model_path:
                    return str(item.get("type") or "")
        return ""

    def _home_source_format_text(self, project_type: str) -> str:
        future = {
            "ouvrage_structure": "ODT, DOCX, ODP, PPTX",
            "livre_textuel": "DOCX, ODT, TXT, RTF",
            "bande_dessinee": "PNG, JPG, WEBP, TIFF",
        }.get(project_type, "autres formats")
        return f"Disponible : PDF   •   À venir : {future}   •   Format inconnu : refusé"

    def _home_reset_initial_source(self, *, hide_panel: bool = False):
        self._home_source_analysis_token += 1
        self._home_source_path_var.set("")
        self._home_source_info = None
        self._home_source_wait_step = 0
        if hasattr(self, "_home_source_status_var"):
            self._home_source_status_var.set("Choisissez une Source à analyser.")
        if hasattr(self, "_home_create_button"):
            self._home_create_button.configure(state="disabled", cursor="arrow")
        if hasattr(self, "_home_source_button"):
            self._home_source_button.configure(
                state="normal", cursor="hand2", text="Importer la source"
            )
        panel = getattr(self, "home_source_panel", None)
        if panel is not None:
            if hide_panel:
                panel.grid_remove()
            else:
                panel.grid()

    def _home_refresh_source_panel(self):
        project_type = self._home_effective_project_type()
        panel = getattr(self, "home_source_panel", None)
        if panel is None:
            return
        if not project_type:
            panel.grid_remove()
            return
        self._home_source_formats_var.set(self._home_source_format_text(project_type))
        panel.grid()

    def _home_choose_initial_source(self):
        project_type = self._home_effective_project_type()
        if project_type not in {"ouvrage_structure", "livre_textuel", "bande_dessinee"}:
            messagebox.showinfo("Source du projet", "Choisissez d’abord le type de livre.", parent=self)
            return

        raw = filedialog.askopenfilename(
            parent=self,
            title="Importer la source du projet",
            filetypes=(("PDF — disponible maintenant", "*.pdf"), ("Tous les fichiers", "*.*")),
        )
        if not raw:
            return
        source = Path(raw)
        if not source.is_file():
            messagebox.showerror("Source du projet", "Le fichier sélectionné est introuvable.", parent=self)
            return
        if source.suffix.lower() != ".pdf":
            self._home_reset_initial_source(hide_panel=False)
            self._home_source_status_var.set(
                f"Format {source.suffix.upper() or 'inconnu'} refusé : le moteur correspondant n’est pas encore disponible."
            )
            self._home_source_status_label.configure(fg=theme.ERROR)
            messagebox.showwarning(
                "Format non pris en charge",
                "TomeLinea refuse ce fichier avant de créer le projet.\n\n"
                "Le moteur PDF est disponible aujourd’hui. Les autres formats affichés sont prévus mais ne sont pas encore activés.",
                parent=self,
            )
            return
        if source.stat().st_size <= 0:
            messagebox.showerror("Source du projet", "Le fichier sélectionné est vide.", parent=self)
            return

        self._home_begin_source_analysis(source)

    def _home_begin_source_analysis(self, source: Path):
        self._home_source_analysis_token += 1
        token = self._home_source_analysis_token
        self._home_source_analysis_queue = queue.Queue()
        self._home_source_path_var.set("")
        self._home_source_info = None
        self._home_source_wait_step = 0
        self._home_source_status_label.configure(fg=theme.MUTED)
        self._home_source_button.configure(state="disabled", cursor="arrow")
        self._home_create_button.configure(state="disabled", cursor="arrow")
        self._home_source_status_var.set("Lecture de la source…")

        def worker():
            try:
                info = inspect_pdf(source)
                result = (token, True, source, info, "")
            except Exception as exc:
                result = (token, False, source, None, str(exc))
            self._home_source_analysis_queue.put(result)

        threading.Thread(target=worker, name="TomeLineaSourceAnalyse", daemon=True).start()
        self.after(140, lambda: self._home_poll_source_analysis(token))

    def _home_poll_source_analysis(self, token: int):
        if token != self._home_source_analysis_token:
            return
        try:
            result = self._home_source_analysis_queue.get_nowait()
        except queue.Empty:
            steps = (
                "Lecture de la source…",
                "Vérification du document…",
                "Préparation du format interne de consultation…",
            )
            self._home_source_wait_step += 1
            self._home_source_status_var.set(steps[(self._home_source_wait_step // 5) % len(steps)])
            self.after(140, lambda: self._home_poll_source_analysis(token))
            return

        result_token, ok, source, info, error = result
        if result_token != self._home_source_analysis_token:
            return
        self._home_source_button.configure(state="normal", cursor="hand2", text="Changer la source")
        if not ok or info is None:
            self._home_source_status_label.configure(fg=theme.ERROR)
            self._home_source_status_var.set("Source refusée : TomeLinea ne peut pas préparer ce fichier.")
            messagebox.showerror("Source du projet", error or "Source incompatible.", parent=self)
            return

        self._home_source_path_var.set(str(source))
        self._home_source_info = info
        self._home_source_status_label.configure(fg=theme.ACCENT_BRIGHT)
        self._home_source_status_var.set(
            f"✓ Source compatible — {source.name} — {info.page_count} page{'s' if info.page_count != 1 else ''} détectée{'s' if info.page_count != 1 else ''}."
        )
        self._home_create_button.configure(state="normal", cursor="hand2")

    def _home_add_sources(self):
        # Compatibilité avec les anciens appels : le choix de la Source se fait
        # désormais avant la création du projet, directement depuis l’Accueil.
        self._home_choose_initial_source()

    def _home_create_project_inline(self):
        name = self._home_new_name_var.get().strip()
        origin = self._home_new_origin_var.get()
        source_raw = self._home_source_path_var.get().strip()
        source_path = Path(source_raw) if source_raw else None
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
        if source_path is None or not source_path.is_file() or self._home_source_info is None:
            messagebox.showerror(
                "TomeLinea",
                "Importez et validez la Source du projet avant de créer le livre.",
                parent=self,
            )
            return

        project = None
        created_root = None
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
            created_root = Path(project.root) if project is not None and project.root is not None else None

            # La Source est enregistrée immédiatement après la création du
            # conteneur projet. Elle a déjà été inspectée et validée à l’Accueil.
            store_source_in_project(project.root, source_path)
        except Exception as exc:
            # Garde-fou : un échec d’intégration de la Source ne laisse pas un
            # nouveau projet incomplet dans le dossier de l’utilisateur.
            if created_root is not None and created_root.exists():
                try:
                    shutil.rmtree(created_root)
                except Exception:
                    pass
            messagebox.showerror("TomeLinea", str(exc), parent=self)
            return

        self._home_hide_creator()
        self._remember_recent(project)
        # La Source est déjà présente : pas de second écran « ajouter les
        # sources ». Structure construit sa base uniquement pour le mode
        # structuré ; les autres parcours seront définis séparément.
        self.show_workspace(project, first_open=False)

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
        self._show_existing_project_actions(project)

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
        self._show_existing_project_actions(project)

    def _show_existing_project_actions(self, project: Project):
        """Choix contextuel après sélection d'un projet existant.

        Ouvrir un projet ne déclenche aucun nouvel import automatiquement.
        L'utilisateur peut soit reprendre immédiatement son travail, soit
        importer une nouvelle Source complémentaire avant d'entrer dans le
        projet. La Source initiale n'est jamais remplacée ici.
        """
        dialog = tk.Toplevel(self)
        dialog.title("Reprendre un projet")
        dialog.configure(bg=theme.PANEL)
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        width, height = 560, 292
        self.update_idletasks()
        x = self.winfo_rootx() + max(0, (self.winfo_width() - width) // 2)
        y = self.winfo_rooty() + max(0, (self.winfo_height() - height) // 2)
        dialog.geometry(f"{width}x{height}+{x}+{y}")

        type_labels = {
            "ouvrage_structure": "Livre structuré",
            "livre_textuel": "Livre textuel",
            "bande_dessinee": "Bande dessinée",
        }
        project_type = str(getattr(project, "project_type", "") or "")

        tk.Label(
            dialog, text="PROJET EXISTANT", bg=theme.PANEL, fg=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 9, "bold"),
        ).pack(anchor="w", padx=28, pady=(22, 3))
        tk.Label(
            dialog, text=str(getattr(project, "name", "Projet TomeLinea")),
            bg=theme.PANEL, fg=theme.INK, font=(theme.FONT_TITLE, 16, "bold"),
        ).pack(anchor="w", padx=28)
        tk.Label(
            dialog, text=type_labels.get(project_type, "Projet TomeLinea"),
            bg=theme.PANEL, fg=theme.MUTED, font=(theme.FONT_UI, 8),
        ).pack(anchor="w", padx=28, pady=(2, 16))

        tk.Label(
            dialog,
            text="Reprenez le travail tel qu'il était, ou ajoutez une nouvelle source auteur au projet.",
            bg=theme.PANEL, fg=theme.INK, font=(theme.FONT_UI, 9),
            wraplength=500, justify="left",
        ).pack(anchor="w", padx=28, pady=(0, 16))

        buttons = tk.Frame(dialog, bg=theme.PANEL)
        buttons.pack(fill="x", padx=28)

        def resume():
            try:
                dialog.grab_release()
            except Exception:
                pass
            dialog.destroy()
            self._remember_recent(project)
            self.show_workspace(project)

        def import_new_source():
            try:
                dialog.grab_release()
            except Exception:
                pass
            dialog.destroy()
            self._choose_additional_source(project, open_after=True)

        V3Button(
            buttons, "Reprendre le projet", resume, primary=True, compact=False
        ).pack(side="left", padx=(0, 10))
        V3Button(
            buttons, "Importer une nouvelle source", import_new_source, compact=False
        ).pack(side="left")

        tk.Label(
            dialog,
            text="La nouvelle source est ajoutée au projet : la Source initiale reste inchangée.",
            bg=theme.PANEL, fg=theme.MUTED_DARK, font=(theme.FONT_UI, 7),
        ).pack(anchor="w", padx=28, pady=(16, 0))

        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)

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

    def add_to_book(self):
        """Importe une nouvelle Source complémentaire depuis Production."""
        if self.context is None or self.context.project is None:
            return False
        return self._choose_additional_source(self.context.project, open_after=False)

    def _choose_additional_source(self, project: Project, *, open_after: bool = False):
        """Sélectionne, contrôle puis ajoute une Source sans remplacer l'initiale.

        Le moteur réellement disponible aujourd'hui est le PDF. Les autres
        formats restent refusés tant que leur lecteur n'est pas activé.
        """
        raw = filedialog.askopenfilename(
            parent=self,
            title="Importer une nouvelle source",
            filetypes=(("PDF — disponible maintenant", "*.pdf"), ("Tous les fichiers", "*.*")),
        )
        if not raw:
            return False

        source = Path(raw)
        if not source.is_file():
            messagebox.showerror(
                "Importer une nouvelle source",
                "Le fichier sélectionné est introuvable.",
                parent=self,
            )
            return False
        if source.suffix.lower() != ".pdf":
            messagebox.showwarning(
                "Format non pris en charge",
                f"Format {source.suffix.upper() or 'inconnu'} refusé.\n\n"
                "TomeLinea n'importe pas un fichier tant que son moteur de lecture n'est pas disponible. "
                "Le PDF est pris en charge actuellement.",
                parent=self,
            )
            return False
        if source.stat().st_size <= 0:
            messagebox.showerror(
                "Importer une nouvelle source",
                "Le fichier sélectionné est vide.",
                parent=self,
            )
            return False

        return self._begin_additional_source_analysis(project, source, open_after=open_after)

    def _begin_additional_source_analysis(self, project: Project, source: Path, *, open_after: bool):
        """Analyse la nouvelle Source en arrière-plan avant validation finale."""
        wait = tk.Toplevel(self)
        wait.title("Préparation de la source")
        wait.configure(bg=theme.PANEL)
        wait.resizable(False, False)
        wait.transient(self)
        wait.grab_set()

        width, height = 500, 190
        self.update_idletasks()
        x = self.winfo_rootx() + max(0, (self.winfo_width() - width) // 2)
        y = self.winfo_rooty() + max(0, (self.winfo_height() - height) // 2)
        wait.geometry(f"{width}x{height}+{x}+{y}")

        tk.Label(
            wait, text="IMPORT D'UNE NOUVELLE SOURCE", bg=theme.PANEL,
            fg=theme.ACCENT_BRIGHT, font=(theme.FONT_UI, 9, "bold"),
        ).pack(pady=(24, 5))
        tk.Label(
            wait, text=source.name, bg=theme.PANEL, fg=theme.INK,
            font=(theme.FONT_UI, 10, "bold"),
        ).pack()
        status = tk.StringVar(value="Lecture de la source…")
        tk.Label(
            wait, textvariable=status, bg=theme.PANEL, fg=theme.MUTED,
            font=(theme.FONT_UI, 9),
        ).pack(pady=(18, 0))

        result_queue = queue.Queue()
        state = {"step": 0}

        def worker():
            try:
                info = inspect_pdf(source)
                result_queue.put((True, info, ""))
            except Exception as exc:
                result_queue.put((False, None, str(exc)))

        def poll():
            if not wait.winfo_exists():
                return
            try:
                ok, info, error = result_queue.get_nowait()
            except queue.Empty:
                steps = (
                    "Lecture de la source…",
                    "Vérification du document…",
                    "Préparation du format interne de consultation…",
                )
                state["step"] += 1
                status.set(steps[(state["step"] // 5) % len(steps)])
                wait.after(140, poll)
                return

            try:
                wait.grab_release()
            except Exception:
                pass
            wait.destroy()

            if not ok or info is None:
                messagebox.showerror(
                    "Importer une nouvelle source",
                    error or "TomeLinea ne peut pas préparer ce fichier.",
                    parent=self,
                )
                return

            page_count = int(getattr(info, "page_count", 0) or 0)
            confirmed = messagebox.askyesno(
                "Nouvelle source prête",
                f"Source compatible : {source.name}\n"
                f"{page_count} page{'s' if page_count != 1 else ''} détectée{'s' if page_count != 1 else ''}.\n\n"
                "Importer cette nouvelle source dans le projet ?\n"
                "La Source initiale restera inchangée.",
                parent=self,
            )
            if not confirmed:
                return

            try:
                self._store_source_files(project, [str(source)])
            except Exception as exc:
                messagebox.showerror("Importer une nouvelle source", str(exc), parent=self)
                return

            if open_after:
                self._remember_recent(project)
                self.show_workspace(project)
            else:
                self._refresh_workspace_state()

            messagebox.showinfo(
                "Nouvelle source importée",
                f"{source.name} a été ajouté au projet.\n\n"
                "La Source initiale n'a pas été remplacée.",
                parent=self,
            )

        threading.Thread(
            target=worker, name="TomeLineaAdditionalSourceAnalyse", daemon=True
        ).start()
        wait.after(140, poll)
        return True

    def import_sources(self):
        if self.context is None or self.context.project is None:
            return False

        project = self.context.project
        paths = filedialog.askopenfilenames(
            parent=self,
            title="Ajouter les sources de l’auteur",
            filetypes=(
                ("Documents pris en charge", "*.pdf *.odt *.docx *.odp *.pptx"),
                ("PDF", "*.pdf"),
                ("Tous les fichiers", "*.*"),
            ),
        )
        if not paths:
            return False

        selected = [Path(raw) for raw in paths if Path(raw).is_file()]
        if not selected:
            return False

        imported_primary_source = False
        try:
            # Première brique du nouveau parcours : pour un Livre structuré,
            # le premier PDF sélectionné devient la Source du livre centrale.
            # Les éventuels autres fichiers restent des sources complémentaires.
            remaining = list(selected)
            if project.project_type == "ouvrage_structure":
                primary_pdf = next(
                    (path for path in remaining if path.suffix.lower() == ".pdf"),
                    None,
                )
                if primary_pdf is not None:
                    store_source_in_project(project.root, primary_pdf)
                    imported_primary_source = True
                    remaining.remove(primary_pdf)
                    # La Source n'est pas un simple fichier joint : elle crée
                    # immédiatement la Structure de départ lorsqu'elle est vide.
                    self.book_canvas.structure_build_from_book_source(only_if_empty=True)

            if remaining:
                self._store_source_files(project, [str(path) for path in remaining])
        except Exception as exc:
            messagebox.showerror("TomeLinea", str(exc), parent=self)
            return False

        self._refresh_workspace_state()
        if imported_primary_source:
            # Retour visuel immédiat : l’utilisateur voit que l’import a réussi
            # et peut contrôler les pages sans chercher une commande cachée.
            self.after_idle(self.open_source_book_viewer)
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
            manifest["files"].append({"original": str(src), "stored": target.name, "role": "source_complementaire", "imported_at": datetime.now().isoformat()})
            known.add(target.name)
        manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    def _source_count(self, project: Project | None) -> int:
        if project is None or project.root is None:
            return 0

        count = 0
        source_dir = project.root / "sources_originales"
        if (source_dir / "source_livre.json").is_file():
            count += 1

        manifest = source_dir / "manifest.json"
        if manifest.exists():
            try:
                data = json.loads(manifest.read_text(encoding="utf-8"))
                files = data.get("files", []) if isinstance(data, dict) else []
                if isinstance(files, list):
                    count += len(files)
            except Exception:
                pass
        return count

    # ------------------------------------------------------------------
    # Navigation V3
    # ------------------------------------------------------------------

    def show_home(self):
        viewer = getattr(self, "viewer3d_overlay", None)
        if viewer is not None and viewer.active:
            try:
                viewer.hide(return_to_origin=False)
            except Exception:
                pass
        # Les rails Gabarits utilisent des Toplevel transparents sous Windows :
        # ils doivent être explicitement masqués avant de revenir à l'Accueil.
        canvas = getattr(self, "book_canvas", None)
        if canvas is not None:
            try:
                canvas._hide_gabarit_tools_host()
                canvas._hide_gabarit_inspector_host()
                if getattr(canvas, "_gabarit_overlay_active", False):
                    canvas.close_gabarit_overlay()
            except Exception:
                pass
        self._refresh_home_recent()
        self._screens["home"].tkraise()

    def show_workspace(self, project: Project, first_open: bool = False):
        self._gabarit_format_session_confirmed = None
        self.context = WorkspaceContext(project=project, name=project.name, project_type=project.project_type)
        self.book_canvas.set_project(project)
        # Si une Source du livre est déjà enregistrée et que Structure ne
        # contient encore que ses faces physiques de base, construire
        # automatiquement la Structure liée. Cette passe est non destructive.
        if str(project.project_type or "") == "ouvrage_structure":
            try:
                self.book_canvas.structure_build_from_book_source(only_if_empty=True)
            except Exception:
                pass
        self.select_tab("structure")
        self._refresh_workspace_state()
        self._screens["workspace"].tkraise()

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

    def close_source_book_viewer(self):
        overlay = getattr(self, "_source_book_overlay", None)
        if overlay is not None:
            try:
                overlay.destroy()
            except Exception:
                pass
        self._source_book_overlay = None
        self._source_book_viewer = None

    def _selected_book_source_page_number(self) -> int | None:
        """Retourne la page de la Source du livre liée à la sélection courante.

        La correspondance est portée par ``book_source_page_number`` dans les
        éléments Structure construits depuis la Source du livre. Les pages
        créées par TomeLinea sans équivalent source (par exemple un Blanc de
        compensation) retournent ``None`` au lieu d'ouvrir une page arbitraire.
        """
        canvas = getattr(self, "book_canvas", None)
        if canvas is None:
            return None

        selected_index = getattr(canvas, "_selected_index", None)
        if selected_index is None:
            return None

        try:
            source_index = canvas._source_index_for_index(selected_index)
        except Exception:
            source_index = selected_index

        try:
            if source_index is None or not 0 <= int(source_index) < len(canvas.items):
                return None
            item = canvas.items[int(source_index)]
        except Exception:
            return None

        if not isinstance(item, dict):
            return None

        raw = item.get("book_source_page_number")
        try:
            page_number = int(raw)
        except (TypeError, ValueError):
            return None
        return page_number if page_number >= 1 else None

    def _book_source_type_trace(self, page_number: int) -> dict | None:
        """Retourne le type actuel et le type d'origine d'une page source."""
        canvas = getattr(self, "book_canvas", None)
        if canvas is None:
            return None
        try:
            number = int(page_number)
        except (TypeError, ValueError):
            return None

        item = next(
            (
                candidate
                for candidate in getattr(canvas, "items", [])
                if isinstance(candidate, dict)
                and candidate.get("book_source_page_number") == number
            ),
            None,
        )
        if not isinstance(item, dict):
            return None

        try:
            canvas._structure_record_book_source_type_state(item)
        except Exception:
            try:
                canvas._structure_ensure_book_source_initial_type(item)
            except Exception:
                pass

        current = str(item.get("book_source_current_type_name") or "").strip()
        if not current:
            current = str(
                item.get("type_name")
                or item.get("attribute")
                or item.get("title")
                or ""
            ).strip()
        if not current:
            raw_type = str(item.get("type") or "").strip()
            current = raw_type.replace("_", " ").capitalize() if raw_type else "Sans type"

        initial = str(item.get("book_source_initial_type_name") or "").strip()
        if not initial:
            role = str(item.get("book_source_role") or "").strip().lower()
            initial = "Sans type" if role == "content" else current

        return {
            "current": current,
            "initial": initial,
            "modified": bool(item.get("book_source_type_modified", current.casefold() != initial.casefold())),
            "origin": str(item.get("book_source_type_change_origin") or "").strip(),
        }

    def open_source_book_viewer(self, initial_page: int | None = None):
        if self.context is None or self.context.project is None:
            return False

        project = self.context.project
        try:
            source_path, info = load_project_source(project.root)
        except FileNotFoundError:
            messagebox.showinfo(
                "Source du livre",
                "Aucune Source du livre n’est encore enregistrée dans ce projet.\n\n"
                "La Source du livre se choisit lors de la création du projet, "
                "à l’étape « Ajouter les sources de l’auteur ».",
                parent=self,
            )
            return False
        except Exception as exc:
            messagebox.showerror("Source du livre", str(exc), parent=self)
            return False

        # Depuis Structure/Gabarits, ouvrir directement la page auteur liée à
        # la page TomeLinea sélectionnée. Ne jamais retomber silencieusement
        # sur la couverture lorsqu'une page sélectionnée n'a pas de source.
        if initial_page is None:
            selected_index = getattr(getattr(self, "book_canvas", None), "_selected_index", None)
            if selected_index is not None:
                initial_page = self._selected_book_source_page_number()
                if initial_page is None:
                    messagebox.showinfo(
                        "Source du livre",
                        "La page sélectionnée a été créée par TomeLinea et n’a pas de page correspondante dans la Source du livre.",
                        parent=self,
                    )
                    return False

        self.close_source_book_viewer()

        host = getattr(self, "stack", self)
        overlay = tk.Frame(host, bg=theme.WINDOW_DEEP)
        overlay.place(x=0, y=0, relwidth=1, relheight=1)
        overlay.lift()
        self._source_book_overlay = overlay

        overlay.grid_rowconfigure(1, weight=1)
        overlay.grid_columnconfigure(0, weight=1)

        head = tk.Frame(overlay, bg=theme.PANEL, height=52)
        head.grid(row=0, column=0, sticky="ew")
        head.grid_columnconfigure(1, weight=1)

        tk.Label(
            head,
            text="SOURCE DU LIVRE",
            bg=theme.PANEL,
            fg=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 9, "bold"),
        ).grid(row=0, column=0, padx=(18, 12), pady=12, sticky="w")

        tk.Label(
            head,
            text=f"{info.source_name}  •  {info.page_count} pages",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 9),
        ).grid(row=0, column=1, padx=8, pady=12, sticky="w")

        close = tk.Label(
            head,
            text="×",
            bg=theme.PANEL,
            fg=theme.INK,
            font=(theme.FONT_UI, 20, "bold"),
            cursor="hand2",
            padx=14,
        )
        close.grid(row=0, column=2, sticky="e")
        close.bind("<Button-1>", lambda _e: self.close_source_book_viewer())

        body = tk.Frame(overlay, bg=theme.WINDOW_DEEP)
        body.grid(row=1, column=0, sticky="nsew", padx=14, pady=(0, 14))
        body.grid_rowconfigure(0, weight=1)
        body.grid_columnconfigure(0, weight=1)

        page = 1 if initial_page is None else int(initial_page)
        viewer = SourceBookViewer(
            body,
            source_path,
            cache_dir=source_cache_folder(project.root),
            initial_page=page,
            bg=theme.WINDOW_DEEP,
            panel_bg=theme.PANEL_ALT,
            fg=theme.INK,
            muted=theme.MUTED,
            accent=theme.ACCENT_BRIGHT,
            page_trace_provider=self._book_source_type_trace,
        )
        viewer.grid(row=0, column=0, sticky="nsew")
        self._source_book_viewer = viewer

        overlay.bind("<Escape>", lambda _e: self.close_source_book_viewer())
        viewer.after_idle(viewer.focus_set)
        return True

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
                "ouvrage_structure": "Structuré",
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
        self._home_reset_initial_source(hide_panel=True)
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
        self._home_new_type_var.set(str(item.get("type") or ""))
        self._home_reset_initial_source(hide_panel=False)
        self._home_refresh_source_panel()
        type_labels = {
            "ouvrage_structure": "Livre structuré",
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
            "ouvrage_structure": "Livre structuré",
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

