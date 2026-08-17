from __future__ import annotations

import importlib.util
import json
import shutil
import tkinter as tk
from dataclasses import dataclass
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Callable

from PIL import Image, ImageEnhance, ImageTk

from src.gui_v3 import theme
from src.gui_v3.book_canvas import BookCanvas


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
        cache_key = (key, size)
        if cache_key in self._type_icon_cache:
            return self._type_icon_cache[cache_key]
        path = TYPE_ICONS.get(key)
        if path is None or not path.exists():
            return None
        image = Image.open(path).convert("RGBA")
        image.thumbnail((size, size), Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        self._type_icon_cache[cache_key] = photo
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
        content = tk.Frame(screen, bg=theme.WINDOW_DEEP)
        content.place(relx=0.055, rely=0.055, relwidth=0.89, relheight=0.89)

        # Le fond du cadre central reste calme et reprend la tonalité V2.
        content.configure(highlightthickness=0)
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(2, weight=1)

        header = tk.Frame(content, bg=theme.WINDOW_DEEP)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)

        brand = tk.Frame(header, bg=theme.WINDOW_DEEP)
        brand.grid(row=0, column=0, sticky="w")
        tk.Label(
            brand,
            text="TomeLinea",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(theme.FONT_TITLE, 25, "bold"),
        ).pack(anchor="w")
        tk.Label(
            brand,
            text="LA LIGNE ÉDITORIALE JUSQU’AU LIVRE",
            bg=theme.WINDOW_DEEP,
            fg=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 8, "bold"),
        ).pack(anchor="w", pady=(1, 0))

        tk.Label(
            header,
            text="V3 — un seul espace de travail, un seul livre",
            bg=theme.WINDOW_DEEP,
            fg=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 9, "bold"),
        ).grid(row=0, column=1, sticky="e")

        intro = tk.Frame(content, bg=theme.WINDOW_DEEP)
        intro.grid(row=1, column=0, sticky="ew", pady=(16, 18))
        tk.Label(
            intro,
            text="Commencer ou reprendre un ouvrage",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(theme.FONT_TITLE, 22, "bold"),
        ).pack(anchor="w")
        tk.Label(
            intro,
            text=(
                "Le travail de l’auteur entre ici. Une fois le projet ouvert, "
                "la vue du livre reste visible pendant toute la production."
            ),
            bg=theme.WINDOW_DEEP,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 10),
        ).pack(anchor="w", pady=(5, 0))

        cards = tk.Frame(content, bg=theme.WINDOW_DEEP)
        cards.grid(row=2, column=0, sticky="nsew")
        for col in range(3):
            cards.grid_columnconfigure(col, weight=1, uniform="home_cards")
        cards.grid_rowconfigure(0, weight=1)

        self._home_card(
            cards,
            0,
            title="Créer un projet",
            subtitle="Choisir le type d’ouvrage, nommer le projet et déposer éventuellement le travail de l’auteur.",
            action="Nouveau projet",
            command=self.open_create_dialog,
        )
        self._home_card(
            cards,
            1,
            title="Ouvrir un projet",
            subtitle="Reprendre un projet TomeLinea existant et retrouver immédiatement sa vue permanente.",
            action="Ouvrir",
            command=self.open_existing_project,
        )
        self.home_recent_panel = self._home_card(
            cards,
            2,
            title="Dernier projet",
            subtitle="Aucun projet récent enregistré pour la V3.",
            action="Reprendre",
            command=self.open_last_project,
            return_panel=True,
        )

        footer = tk.Frame(content, bg=theme.WINDOW_DEEP)
        footer.grid(row=3, column=0, sticky="ew", pady=(18, 0))
        tk.Frame(footer, bg=theme.ACCENT_DARK, height=1).pack(fill="x")
        tk.Label(
            footer,
            text="Structure  •  Gabarits  •  Production  •  Sortie",
            bg=theme.WINDOW_DEEP,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 8),
        ).pack(anchor="e", pady=(7, 0))

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
        self.zone_c = CutPanel(screen, fill=theme.PANEL, border=theme.BORDER, cut=18, padding=(16, 12))

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
                self.zone_b.tk.call("raise", self.zone_b._w)
                self.zone_a.tk.call("raise", self.zone_a._w)
            else:
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
        for tab_key, button in self.tab_buttons.items():
            if tab_key == key:
                button.configure(bg=theme.ACCENT_DARK, fg=theme.WHITE)
            else:
                button.configure(bg=theme.PANEL_SOFT, fg=theme.INK)

    # ------------------------------------------------------------------
    # Projet / import
    # ------------------------------------------------------------------

    def open_create_dialog(self):
        win = tk.Toplevel(self)
        win.title("TomeLinea V3 — Créer un projet")
        win.configure(bg=theme.WINDOW_DEEP)
        win.transient(self)
        win.grab_set()
        win.geometry("920x590")
        win.minsize(820, 540)

        panel = CutPanel(win, fill=theme.PANEL, border=theme.BORDER, cut=18, padding=(24, 20))
        panel.pack(fill="both", expand=True, padx=18, pady=18)
        body = panel.body
        body.grid_columnconfigure(0, weight=1)
        body.grid_rowconfigure(3, weight=1)

        tk.Label(
            body,
            text="Créer un projet",
            bg=theme.PANEL,
            fg=theme.INK,
            font=(theme.FONT_TITLE, 18, "bold"),
        ).grid(row=0, column=0, sticky="w")
        tk.Label(
            body,
            text="Le choix du type oriente l’import, mais l’espace V3 reste le même.",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 9),
        ).grid(row=1, column=0, sticky="w", pady=(4, 14))

        selected_type = tk.StringVar(value="ouvrage_structure")
        type_row = tk.Frame(body, bg=theme.PANEL)
        type_row.grid(row=2, column=0, sticky="ew")
        for col in range(3):
            type_row.grid_columnconfigure(col, weight=1, uniform="types")

        type_buttons = {}

        def refresh_type_cards():
            for key, frame in type_buttons.items():
                active = selected_type.get() == key
                frame.configure(
                    bg=theme.ACCENT_SOFT if active else theme.PANEL_ALT,
                    highlightbackground=theme.ACCENT if active else theme.BORDER_SOFT,
                )
                for child in frame.winfo_children():
                    try:
                        child.configure(bg=frame.cget("bg"))
                    except Exception:
                        pass

        for col, key in enumerate(("ouvrage_structure", "livre_textuel", "bande_dessinee")):
            card = tk.Frame(
                type_row,
                bg=theme.PANEL_ALT,
                highlightthickness=1,
                highlightbackground=theme.BORDER_SOFT,
                padx=12,
                pady=10,
                cursor="hand2",
            )
            card.grid(row=0, column=col, sticky="nsew", padx=(0 if col == 0 else 6, 0 if col == 2 else 6))
            photo = self._type_icon(key, 82)
            icon = tk.Label(card, bg=theme.PANEL_ALT)
            if photo is not None:
                icon.configure(image=photo)
                icon.image = photo
            icon.pack()
            label = tk.Label(
                card,
                text=theme.PROJECT_TYPES[key],
                bg=theme.PANEL_ALT,
                fg=theme.INK,
                font=(theme.FONT_UI, 9, "bold"),
            )
            label.pack(pady=(4, 0))
            for widget in (card, icon, label):
                widget.bind("<Button-1>", lambda _e, k=key: (selected_type.set(k), refresh_type_cards()))
            type_buttons[key] = card
        refresh_type_cards()

        form = tk.Frame(body, bg=theme.PANEL)
        form.grid(row=3, column=0, sticky="nsew", pady=(16, 0))
        form.grid_columnconfigure(1, weight=1)
        form.grid_rowconfigure(2, weight=1)

        tk.Label(form, text="Nom du projet", bg=theme.PANEL, fg=theme.MUTED, font=(theme.FONT_UI, 8, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        name_var = tk.StringVar(value="Nouveau projet")
        tk.Entry(
            form,
            textvariable=name_var,
            bg=theme.PANEL_ALT,
            fg=theme.INK,
            insertbackground=theme.INK,
            relief="flat",
            bd=0,
            font=(theme.FONT_UI, 9),
        ).grid(row=0, column=1, sticky="ew", padx=(14, 0), ipady=7)

        tk.Label(form, text="Emplacement", bg=theme.PANEL, fg=theme.MUTED, font=(theme.FONT_UI, 8, "bold")).grid(row=1, column=0, sticky="w", pady=5)
        location_var = tk.StringVar(value=str(Path.home() / "Documents"))
        location_entry = tk.Entry(
            form,
            textvariable=location_var,
            bg=theme.PANEL_ALT,
            fg=theme.INK,
            insertbackground=theme.INK,
            relief="flat",
            bd=0,
            font=(theme.FONT_UI, 9),
        )
        location_entry.grid(row=1, column=1, sticky="ew", padx=(14, 8), ipady=7)
        V3Button(form, "Parcourir", lambda: self._choose_location(location_var), compact=True).grid(row=1, column=2)

        tk.Label(form, text="Travail de l’auteur", bg=theme.PANEL, fg=theme.MUTED, font=(theme.FONT_UI, 8, "bold")).grid(row=2, column=0, sticky="nw", pady=(10, 0))
        source_box = tk.Frame(form, bg=theme.PANEL_ALT)
        source_box.grid(row=2, column=1, columnspan=2, sticky="nsew", padx=(14, 0), pady=(10, 0))
        source_box.grid_rowconfigure(0, weight=1)
        source_box.grid_columnconfigure(0, weight=1)
        source_list = tk.Listbox(
            source_box,
            bg=theme.PANEL_ALT,
            fg=theme.MUTED,
            selectbackground=theme.ACCENT_SOFT,
            selectforeground=theme.WHITE,
            relief="flat",
            bd=0,
            font=(theme.FONT_UI, 8),
            height=4,
        )
        source_list.grid(row=0, column=0, sticky="nsew", padx=8, pady=6)
        source_files: list[str] = []

        def add_sources():
            paths = filedialog.askopenfilenames(parent=win, title="Ajouter le travail de l’auteur")
            for path in paths:
                if path not in source_files:
                    source_files.append(path)
                    source_list.insert("end", Path(path).name)

        V3Button(source_box, "Ajouter des fichiers…", add_sources, compact=True).grid(row=1, column=0, sticky="w", padx=8, pady=(0, 8))

        actions = tk.Frame(body, bg=theme.PANEL)
        actions.grid(row=4, column=0, sticky="ew", pady=(16, 0))
        V3Button(actions, "Annuler", win.destroy).pack(side="right", padx=(8, 0))

        def create():
            name = name_var.get().strip()
            location = location_var.get().strip()
            if not name or not location:
                messagebox.showerror("TomeLinea", "Le nom et l’emplacement sont nécessaires.", parent=win)
                return
            try:
                project = self.project_manager.new_project(location, name, project_type=selected_type.get())
                self._store_source_files(project, source_files)
            except Exception as exc:
                messagebox.showerror("TomeLinea", str(exc), parent=win)
                return
            win.destroy()
            self._remember_recent(project)
            self.show_workspace(project)

        V3Button(actions, "Créer et ouvrir", create, primary=True).pack(side="right")

    def _choose_location(self, variable: tk.StringVar):
        folder = filedialog.askdirectory(parent=self, title="Choisir l’emplacement du projet")
        if folder:
            variable.set(folder)

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

    def _refresh_home_recent(self):
        panel = getattr(self, "home_recent_panel", None)
        if panel is None:
            return
        recent = self._load_recent()
        if recent:
            item = recent[0]
            label = theme.PROJECT_TYPES.get(item.get("type"), "Projet TomeLinea")
            panel._subtitle_var.set(f"{item.get('name', 'Projet')}\n{label}\n{item.get('path', '')}")
        else:
            panel._subtitle_var.set("Aucun projet récent enregistré pour la V3.")
