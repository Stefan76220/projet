from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk, ImageDraw

from src.gui_v2 import theme
from src.gui_v2.tomelinea_controls import TLCommandButton, TLChoiceCard, TLShortcutCard
from src.gui_v2.components import PMCommandButton


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ACCUEIL_BG = (
    PROJECT_ROOT
    / "assets"
    / "interface"
    / "backgrounds"
    / "editorial_bg_accueil.png"
)

BRAND_ROOT = (
    PROJECT_ROOT
    / "assets"
    / "branding"
    / "tomelinea"
    / "Tomelinea_logo_pack"
)
BRAND_SYMBOL = (
    BRAND_ROOT
    / "02_symbole_TL_livre"
    / "Tomelinea_TL_livre_transparent.png"
)
BRAND_ICON = (
    BRAND_ROOT
    / "04_windows"
    / "Tomelinea.ico"
)
BRAND_ICON_PNG = (
    BRAND_ROOT
    / "04_windows"
    / "Tomelinea_Windows_64x64.png"
)


class PageMaitreV2(tk.Tk):
    """Prototype parallèle TomeLinea V2 — navigation et apparence."""

    def __init__(self) -> None:
        super().__init__()

        self.title("TomeLinea — Interface V2")

        # Identité officielle TomeLinea : icône de fenêtre Windows.
        self._brand_window_icon = None
        try:
            if BRAND_ICON.exists():
                self.iconbitmap(str(BRAND_ICON))
        except Exception:
            pass
        try:
            if BRAND_ICON_PNG.exists():
                icon_image = Image.open(BRAND_ICON_PNG).convert("RGBA")
                self._brand_window_icon = ImageTk.PhotoImage(icon_image)
                self.iconphoto(True, self._brand_window_icon)
        except Exception:
            self._brand_window_icon = None

        self.configure(bg=theme.WINDOW)
        self.minsize(1180, 720)
        self.geometry("1400x860")

        self._screens: dict[str, tk.Frame] = {}
        self._nav_buttons: dict[str, tk.Button] = {}
        self._active = "accueil"

        self._accueil_bg_source = None
        self._accueil_bg_photo = None
        self._header_bg_source = None
        self._header_bg_photo = None

        self._configure_style()
        self._build_shell()
        self._build_all_screens_once()
        self.show_screen("accueil")

        try:
            self.state("zoomed")
        except tk.TclError:
            pass

    # ==========================================================
    # SOCLE COMMUN
    # ==========================================================

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "V2.Horizontal.TScrollbar",
            troughcolor=theme.PANEL_ALT,
            background=theme.INK,
            bordercolor=theme.PANEL_ALT,
            arrowcolor=theme.INK,
        )

    def _build_shell(self) -> None:
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Un seul Canvas pour tout le ruban :
        # le décor et les icônes partagent la même surface.
        # Il n'y a donc plus de rectangles opaques derrière les icônes.
        self.header = tk.Canvas(
            self,
            bg="#F8F4EC",
            height=108,
            highlightthickness=0,
            bd=0,
        )
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.bind("<Configure>", self._render_header_canvas)

        self._header_nav_hitboxes = {}
        self._header_side_hitboxes = {}
        self._header_canvas_images = []
        self._header_ready = False

        self.host = tk.Frame(self, bg=theme.WINDOW)
        self.host.grid(row=1, column=0, sticky="nsew")
        self.host.grid_rowconfigure(0, weight=1)
        self.host.grid_columnconfigure(0, weight=1)

        self.after_idle(self._render_header_canvas)

    def _nav_icon_file(self, key: str, state: str, size: int) -> Path:
        return (
            PROJECT_ROOT / "assets" / "gui_v2" / "navigation_icons"
            / key / f"{key}_{state}_{size}px.png"
        )

    def _get_nav_photo(self, key: str, state: str, size: int = 48):
        if not hasattr(self, "_nav_photo_cache"):
            self._nav_photo_cache = {}
        cache_key = (key, state, size)
        if cache_key in self._nav_photo_cache:
            return self._nav_photo_cache[cache_key]

        path = self._nav_icon_file(key, state, size)
        if not path.exists():
            return None

        image = Image.open(path).convert("RGBA")
        photo = ImageTk.PhotoImage(image)
        self._nav_photo_cache[cache_key] = photo
        return photo

    def _make_nav_icon(self, parent, *, key: str, label: str, accent: str):
        frame = tk.Frame(parent, bg="#F8F4EC", padx=4, pady=2, cursor="hand2")

        image_label = tk.Label(frame, bg="#F8F4EC", bd=0, cursor="hand2")
        image_label.pack(pady=(1, 0))

        text_label = tk.Label(
            frame, text=label, bg="#F8F4EC", fg=theme.INK,
            font=("Segoe UI", 8), cursor="hand2"
        )
        text_label.pack()

        dot = tk.Label(
            frame, text="•", bg="#F8F4EC", fg=accent,
            font=("Segoe UI", 11, "bold"), cursor="hand2"
        )
        dot.pack()

        self._nav_icon_labels[key] = image_label
        self._nav_text_labels[key] = text_label
        self._nav_dot_labels[key] = dot

        def click(_event=None):
            self.show_screen(key)

        def enter(_event=None):
            if self._active != key:
                self._set_nav_state(key, "survol")

        def leave(_event=None):
            self._set_nav_state(
                key, "actif" if self._active == key else "normal"
            )

        for widget in (frame, image_label, text_label, dot):
            widget.bind("<Button-1>", click)
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)

        return frame

    def _set_nav_state(self, key: str, state: str) -> None:
        frame = self._nav_buttons.get(key)
        image_label = self._nav_icon_labels.get(key)
        text_label = self._nav_text_labels.get(key)
        if frame is None or image_label is None:
            return

        photo = self._get_nav_photo(key, state, 48)
        if photo is not None:
            image_label.configure(image=photo)
            image_label.image = photo

        bg = "#FBFAF6"
        if state == "survol":
            bg = "#F3F7F4"
        elif state == "actif":
            bg = "#EEF5F0"

        frame.configure(bg=bg)
        for child in frame.winfo_children():
            child.configure(bg=bg)

        if text_label is not None:
            text_label.configure(
                font=("Segoe UI", 8, "bold") if state == "actif"
                else ("Segoe UI", 8)
            )

    def _make_side_icon(
        self, parent, *, key: str, label: str, command, enabled: bool
    ):
        frame = tk.Frame(parent, bg="#F8F4EC")

        image_label = tk.Label(frame, bg="#F8F4EC", bd=0)
        image_label.pack()

        text_label = tk.Label(
            frame, text=label, bg="#F8F4EC",
            fg=theme.MUTED, font=("Segoe UI", 8)
        )
        text_label.pack()

        frame._pm_key = key
        frame._pm_command = command
        frame._pm_enabled = enabled
        frame._pm_image_label = image_label
        frame._pm_text_label = text_label

        def set_state(state):
            photo = self._get_nav_photo(key, state, 32)
            if photo is not None:
                image_label.configure(image=photo)
                image_label.image = photo
            text_label.configure(
                fg="#A6ADB5" if state == "indisponible" else theme.MUTED
            )

        frame._pm_set_state = set_state
        set_state("normal" if enabled else "indisponible")

        def click(_event=None):
            if frame._pm_enabled and frame._pm_command:
                frame._pm_command()

        def enter(_event=None):
            if frame._pm_enabled:
                set_state("survol")

        def leave(_event=None):
            set_state("normal" if frame._pm_enabled else "indisponible")

        for widget in (frame, image_label, text_label):
            widget.bind("<Button-1>", click)
            widget.bind("<Enter>", enter)
            widget.bind("<Leave>", leave)
            if enabled:
                widget.configure(cursor="hand2")

        return frame

    def _set_side_enabled(self, frame, enabled: bool) -> None:
        frame._pm_enabled = enabled
        setter = getattr(frame, "_pm_set_state", None)
        if setter is not None:
            setter("normal" if enabled else "indisponible")

    def _render_header_canvas(self, _event=None) -> None:
        canvas = self.header
        if not canvas.winfo_exists():
            return

        width = max(canvas.winfo_width(), 1180)
        height = 108
        canvas.delete("all")
        self._header_canvas_images = []
        self._header_nav_hitboxes = {}
        self._header_side_hitboxes = {}

        # Décor léger du bandeau, conforme à la version validée.
        if ACCUEIL_BG.exists():
            try:
                source = Image.open(ACCUEIL_BG).convert("RGB")
                sw, sh = source.size
                crop_h = max(1, min(sh, int(sh * 0.18)))
                source = source.crop((0, 0, sw, crop_h))
                source = source.resize(
                    (width, height),
                    Image.Resampling.LANCZOS,
                )
                bg_photo = ImageTk.PhotoImage(source)
                self._header_canvas_images.append(bg_photo)
                canvas.create_image(
                    0, 0,
                    image=bg_photo,
                    anchor="nw",
                )
            except Exception:
                canvas.create_rectangle(
                    0, 0, width, height,
                    fill="#F8F4EC",
                    outline="",
                )
        else:
            canvas.create_rectangle(
                0, 0, width, height,
                fill="#F8F4EC",
                outline="",
            )

        # Voile clair d'origine pour garder la lecture nette des commandes.
        canvas.create_rectangle(
            0, 0, width, height,
            fill="#FFFDFC",
            stipple="gray75",
            outline="",
        )

        # Titre du bureau
        labels = {
            "accueil": "Accueil",
            "centre": "Centre du projet",
            "maquettage": "Maquettage",
            "atelier": "Atelier",
            "conception": "Conception",
            "assemblage": "Assemblage",
            "verification": "Vérification",
            "finalisation": "Finalisation",
        }
        current_title = labels.get(
            getattr(self, "_active", "accueil"),
            "Accueil",
        )

        # Commandes latérales gauche
        self._draw_side_canvas_item(
            key="visualisation",
            label="Visualisation",
            x=62,
            y=57,
            enabled=getattr(self, "_active", "accueil") != "accueil",
            command=self.open_visualisation_window,
        )
        self._draw_side_canvas_item(
            key="suivi_du_livre",
            label="Suivi du livre",
            x=168,
            y=57,
            enabled=False,
            command=None,
        )

        # Symbole officiel TomeLinea, posé directement sur le décor du ruban.
        if BRAND_SYMBOL.exists():
            try:
                brand_image = Image.open(BRAND_SYMBOL).convert("RGBA")
                brand_image.thumbnail((58, 58), Image.Resampling.LANCZOS)
                brand_photo = ImageTk.PhotoImage(brand_image)
                self._header_canvas_images.append(brand_photo)
                canvas.create_image(292, 53, image=brand_photo, anchor="center")
            except Exception:
                pass

        # PM_WORKSPACE_NAME_UNDER_LOGO
        # Le nom du bureau actif est intégré au ruban afin de libérer
        # la hauteur de travail des pages.
        canvas.create_text(
            292,
            92,
            text=current_title,
            anchor="center",
            fill=theme.INK,
            font=("Segoe UI", 8, "bold"),
        )

        # Navigation centrale
        items = list(theme.NAV_ITEMS)
        nav_left = 420
        nav_right = max(nav_left + 760, width - 420)
        available = nav_right - nav_left
        step = available / max(len(items), 1)

        for index, (key, _old_icon, label, accent) in enumerate(items):
            x = nav_left + step * index + step / 2
            state = "actif" if key == getattr(self, "_active", "accueil") else "normal"
            self._draw_nav_canvas_item(
                key=key,
                label=label,
                accent=accent,
                x=x,
                y=47,
                state=state,
            )

        # Bloc projet + fermeture à droite.
        current = labels.get(
            getattr(self, "_active", "accueil"),
            "Accueil",
        )
        canvas.create_text(
            width - 150,
            15,
            text="projet x",
            anchor="ne",
            fill=theme.MUTED,
            font=("Segoe UI", 8),
        )

        self._draw_side_canvas_item(
            key="fermer",
            label="Fermer",
            x=width - 42,
            y=56,
            enabled=True,
            command=self.destroy,
        )

        canvas.create_line(
            0, height - 1,
            width, height - 1,
            fill=theme.BORDER,
        )

        self._bind_header_canvas_events()
        self._header_ready = True

    def _draw_nav_canvas_item(
        self,
        *,
        key: str,
        label: str,
        accent: str,
        x: float,
        y: float,
        state: str,
    ) -> None:
        canvas = self.header
        tag = f"nav_{key}"

        # L'élément actif reçoit seulement un halo doux :
        # aucune modification de taille, d'icône ou de disposition.
        if state == "actif":
            halo_outer = self._mix(accent, "#FFFFFF", 0.90)
            halo_inner = self._mix(accent, "#FFFFFF", 0.82)

            canvas.create_oval(
                x - 31, y - 48,
                x + 31, y + 14,
                fill=halo_outer,
                outline="",
                tags=(tag, "nav_item"),
            )
            canvas.create_oval(
                x - 27, y - 44,
                x + 27, y + 10,
                fill=halo_inner,
                outline=self._mix(accent, "#FFFFFF", 0.50),
                width=1,
                tags=(tag, "nav_item"),
            )

        photo = self._get_nav_photo(key, state, 48)
        if photo is not None:
            self._header_canvas_images.append(photo)
            canvas.create_image(
                x, y - 18,
                image=photo,
                anchor="center",
                tags=(tag, "nav_item"),
            )

        canvas.create_text(
            x, y + 18,
            text=label,
            anchor="n",
            fill=(
                self._mix(accent, theme.INK, 0.34)
                if state == "actif"
                else theme.INK
            ),
            font=(
                ("Segoe UI", 8, "bold")
                if state == "actif"
                else ("Segoe UI", 8)
            ),
            tags=(tag, "nav_item"),
        )

        canvas.create_text(
            x, y + 39,
            text="●" if state == "actif" else "•",
            anchor="n",
            fill=accent,
            font=(
                ("Segoe UI", 9, "bold")
                if state == "actif"
                else ("Segoe UI", 11, "bold")
            ),
            tags=(tag, "nav_item"),
        )

        half_w = 44
        self._header_nav_hitboxes[key] = (
            x - half_w,
            y - 47,
            x + half_w,
            y + 55,
        )


    def _draw_side_canvas_item(
        self,
        *,
        key: str,
        label: str,
        x: float,
        y: float,
        enabled: bool,
        command,
    ) -> None:
        canvas = self.header
        state = "normal" if enabled else "indisponible"
        photo = self._get_nav_photo(key, state, 32)

        if photo is not None:
            self._header_canvas_images.append(photo)
            canvas.create_image(
                x, y - 10,
                image=photo,
                anchor="center",
                tags=(f"side_{key}",),
            )

        canvas.create_text(
            x, y + 15,
            text=label,
            anchor="n",
            fill=theme.MUTED if enabled else "#A6ADB5",
            font=("Segoe UI", 8),
            tags=(f"side_{key}",),
        )

        self._header_side_hitboxes[key] = {
            "box": (x - 48, y - 34, x + 48, y + 38),
            "enabled": enabled,
            "command": command,
            "label": label,
            "x": x,
            "y": y,
        }

    def _bind_header_canvas_events(self) -> None:
        canvas = self.header
        canvas.unbind("<Motion>")
        canvas.unbind("<Leave>")
        canvas.unbind("<Button-1>")

        self._header_hover_key = None
        self._header_hover_side = None

        canvas.bind("<Motion>", self._header_canvas_motion)
        canvas.bind("<Leave>", self._header_canvas_leave)
        canvas.bind("<Button-1>", self._header_canvas_click)

    @staticmethod
    def _point_in_box(x, y, box) -> bool:
        x1, y1, x2, y2 = box
        return x1 <= x <= x2 and y1 <= y <= y2

    def _header_canvas_motion(self, event) -> None:
        nav_key = None
        for key, box in self._header_nav_hitboxes.items():
            if self._point_in_box(event.x, event.y, box):
                nav_key = key
                break

        side_key = None
        for key, data in self._header_side_hitboxes.items():
            if self._point_in_box(event.x, event.y, data["box"]):
                side_key = key
                break

        cursor = "arrow"

        if nav_key is not None:
            cursor = "hand2"
            if nav_key != getattr(self, "_active", "accueil"):
                if self._header_hover_key != nav_key:
                    self._header_hover_key = nav_key
                    self._redraw_header_hover(nav_key, None)
        elif side_key is not None:
            data = self._header_side_hitboxes[side_key]
            if data["enabled"]:
                cursor = "hand2"
                if self._header_hover_side != side_key:
                    self._header_hover_side = side_key
                    self._redraw_header_hover(None, side_key)
        else:
            if (
                self._header_hover_key is not None
                or self._header_hover_side is not None
            ):
                self._header_hover_key = None
                self._header_hover_side = None
                self._render_header_canvas()

        canvas = self.header
        self.configure(cursor=cursor)

    def _redraw_header_hover(self, nav_key, side_key) -> None:
        # Recrée le ruban d'un coup ; le Canvas ne montre aucune reconstruction.
        self._render_header_canvas()

        if nav_key is not None and nav_key != self._active:
            box = self._header_nav_hitboxes.get(nav_key)
            if box:
                x1, y1, x2, y2 = box
                self.header.create_rectangle(
                    x1 + 4, y1 + 2, x2 - 4, y2 - 2,
                    fill="#FFFFFF",
                    stipple="gray75",
                    outline="",
                    tags=("hover_bg",),
                )
                self.header.tag_lower("hover_bg")
                self._render_header_canvas()
                # The actual icon hover state is displayed on next redraw call
                # through an explicit overlay below.
                data = next(
                    (
                        item for item in theme.NAV_ITEMS
                        if item[0] == nav_key
                    ),
                    None,
                )
                if data:
                    key, _old, label, accent = data
                    x = (x1 + x2) / 2
                    self._draw_nav_canvas_item(
                        key=key,
                        label=label,
                        accent=accent,
                        x=x,
                        y=47,
                        state="survol",
                    )

        if side_key is not None:
            data = self._header_side_hitboxes.get(side_key)
            if data and data["enabled"]:
                photo = self._get_nav_photo(side_key, "survol", 32)
                if photo is not None:
                    self._header_canvas_images.append(photo)
                    self.header.create_image(
                        data["x"],
                        data["y"] - 10,
                        image=photo,
                        anchor="center",
                    )

    def _header_canvas_leave(self, _event=None) -> None:
        self._header_hover_key = None
        self._header_hover_side = None
        self.configure(cursor="arrow")
        self._render_header_canvas()

    def _header_canvas_click(self, event) -> None:
        for key, box in self._header_nav_hitboxes.items():
            if self._point_in_box(event.x, event.y, box):
                self.show_screen(key)
                return

        for key, data in self._header_side_hitboxes.items():
            if (
                data["enabled"]
                and self._point_in_box(event.x, event.y, data["box"])
            ):
                command = data["command"]
                if command is not None:
                    command()
                return

    def _build_header_background(self) -> None:
        """Décor très léger du bandeau, sans recalcul à chaque navigation."""
        if not ACCUEIL_BG.exists():
            return

        try:
            image = Image.open(ACCUEIL_BG).convert("RGB")
            w, h = image.size
            crop_h = max(1, min(h, int(h * 0.18)))
            image = image.crop((0, 0, w, crop_h))
            image = image.resize((1600, 108), Image.Resampling.LANCZOS)
            self._header_bg_source = image
            self._header_bg_photo = ImageTk.PhotoImage(image)

            label = tk.Label(
                self.header,
                image=self._header_bg_photo,
                bd=0,
                bg="#F8F4EC",
            )
            label.place(x=0, y=0, relwidth=1, relheight=1)
        except Exception:
            pass

    def _header_tool(
        self,
        parent,
        icon: str,
        label: str,
        command,
    ) -> tk.Frame:
        box = tk.Frame(parent, bg="#F8F4EC")
        button = tk.Button(
            box,
            text=icon,
            command=command,
            state="normal" if command else "disabled",
            relief="flat",
            bd=0,
            bg="#F8F4EC",
            fg=theme.INK,
            disabledforeground="#9AA0A6",
            activebackground="#F8F4EC",
            font=("Segoe UI Symbol", 17),
            cursor="hand2" if command else "arrow",
        )
        button.pack()
        tk.Label(
            box,
            text=label,
            bg="#F8F4EC",
            fg=theme.MUTED if command else "#9AA0A6",
            font=("Segoe UI", 8),
        ).pack()
        return box

    def _build_all_screens_once(self) -> None:
        builders = {
            "accueil": self._build_accueil,
            "centre": self._build_centre,
            "maquettage": self._build_maquettage,
            "atelier": self._build_atelier,
            "conception": self._build_conception,
            "assemblage": self._build_assemblage,
            "verification": self._build_verification,
            "finalisation": self._build_finalisation,
        }

        for name, builder in builders.items():
            screen = tk.Frame(self.host, bg=theme.WINDOW)
            screen.grid(row=0, column=0, sticky="nsew")
            self._screens[name] = screen
            builder(screen)

    def show_screen(self, name: str) -> None:
        screen = self._screens.get(name)
        if screen is None:
            return

        self._active = name
        screen.tkraise()

        # Le Canvas du ruban est redessiné en une seule opération.
        self._render_header_canvas()

    def _set_header_tool_state(
        self, box: tk.Frame, *, enabled: bool
    ) -> None:
        self._set_side_enabled(box, enabled)

    def open_manage_window(self) -> None:
        win = tk.Toplevel(self)
        win.title("Gérer — TomeLinea V2")
        win.configure(bg=theme.WINDOW)
        win.geometry("760x520")
        win.transient(self)

        shell = tk.Frame(
            win,
            bg=theme.PANEL,
            highlightthickness=1,
            highlightbackground=theme.BORDER,
        )
        shell.pack(fill="both", expand=True, padx=18, pady=18)

        tk.Label(
            shell,
            text="Gérer",
            bg=theme.PANEL,
            fg=theme.INK,
            font=("Segoe UI", 18, "bold"),
        ).pack(anchor="w", padx=22, pady=(20, 4))

        tk.Label(
            shell,
            text="Fenêtre active de démonstration — fonctions métier non branchées.",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", padx=22, pady=(0, 18))

        self._placeholder_columns(
            shell,
            (
                ("Projet", ("Informations", "Structure", "Ressources")),
                ("Pages", ("Types", "Groupes", "Éléments supprimés")),
                ("Réglages", ("Affichage", "Préférences", "Bibliothèque")),
            ),
        )

        tk.Button(
            shell,
            text="Fermer",
            command=win.destroy,
            relief="flat",
            bd=0,
            padx=18,
            pady=9,
            bg=theme.INK,
            fg=theme.WHITE,
            activebackground=theme.CORAL,
            activeforeground=theme.WHITE,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        ).pack(side="bottom", pady=18)

    def open_visualisation_window(self) -> None:
        win = tk.Toplevel(self)
        win.title("Visualisation — TomeLinea V2")
        win.configure(bg=theme.WINDOW)
        win.geometry("980x680")
        win.transient(self)

        header = tk.Frame(win, bg=theme.PANEL, height=58)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Visualisation du livre",
            bg=theme.PANEL,
            fg=theme.INK,
            font=("Segoe UI", 15, "bold"),
        ).pack(side="left", padx=18, pady=16)

        tk.Button(
            header,
            text="Fermer",
            command=win.destroy,
            relief="flat",
            bd=0,
            bg=theme.INK,
            fg=theme.WHITE,
            padx=14,
            pady=7,
            cursor="hand2",
        ).pack(side="right", padx=16, pady=12)

        canvas = tk.Canvas(
            win,
            bg="#EAE8E2",
            highlightthickness=0,
        )
        canvas.pack(fill="both", expand=True, padx=18, pady=18)
        canvas.create_rectangle(
            180, 70, 470, 570,
            fill=theme.WHITE,
            outline=theme.BORDER,
        )
        canvas.create_rectangle(
            490, 70, 780, 570,
            fill=theme.WHITE,
            outline=theme.BORDER,
        )
        canvas.create_text(
            480,
            620,
            text="Double page — aperçu V2",
            fill=theme.MUTED,
            font=("Segoe UI", 10),
        )

    # ==========================================================
    # ACCUEIL — PREMIÈRE PAGE DE RÉFÉRENCE V2
    # ==========================================================

    def _build_accueil(self, parent: tk.Frame) -> None:
        """Accueil TomeLinea — atelier éditorial professionnel à angles coupés."""

        canvas = tk.Canvas(
            parent,
            bg="#F5F1E9",
            highlightthickness=0,
            bd=0,
        )
        canvas.pack(fill="both", expand=True)
        self._accueil_canvas = canvas

        self._selected_project_type = None
        self._accueil_prof_state = {}
        self._accueil_prof_photos = {}

        if ACCUEIL_BG.exists():
            try:
                self._accueil_bg_source = Image.open(ACCUEIL_BG).convert("RGB")
            except Exception:
                self._accueil_bg_source = None
        else:
            self._accueil_bg_source = None

        realistic_dir = PROJECT_ROOT / "assets" / "gui_v2" / "accueil_realistic_icons"
        fallback_dir = PROJECT_ROOT / "assets" / "gui_v2" / "project_type_icons"

        icon_paths = {
            "ouvrage_structure": realistic_dir / "ouvrage_structure.png",
            "livre_textuel": realistic_dir / "livre_textuel.png",
            "bande_dessinee": realistic_dir / "bande_dessinee.png",
            "trio": realistic_dir / "trio.png",
        }

        fallback_paths = {
            "ouvrage_structure": fallback_dir / "ouvrage_structure" / "ouvrage_structure_128px.png",
            "livre_textuel": fallback_dir / "livre_textuel" / "livre_textuel_128px.png",
            "bande_dessinee": fallback_dir / "bande_dessinee" / "bande_dessinee_128px.png",
        }

        def source_for(key: str):
            path = icon_paths.get(key)
            if path is not None and path.exists():
                return path
            fallback = fallback_paths.get(key)
            if fallback is not None and fallback.exists():
                return fallback
            return None

        def cover(source, width: int, height: int):
            sw, sh = source.size
            scale = max(width / sw, height / sh)
            rw = max(width, int(round(sw * scale)))
            rh = max(height, int(round(sh * scale)))
            image = source.resize((rw, rh), Image.Resampling.LANCZOS)
            left = max(0, (rw - width) // 2)
            top = max(0, (rh - height) // 2)
            return image.crop((left, top, left + width, top + height))

        def photo_for(key: str, max_w: int, max_h: int):
            cache_key = (key, max_w, max_h)
            cached = self._accueil_prof_photos.get(cache_key)
            if cached is not None:
                return cached

            path = icon_paths.get(key) if key == "trio" else source_for(key)
            if path is None or not path.exists():
                return None

            try:
                image = Image.open(path).convert("RGBA")
                image.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self._accueil_prof_photos[cache_key] = photo
                return photo
            except Exception:
                return None

        def mix(c1: str, c2: str, ratio: float) -> str:
            return self._mix(c1, c2, ratio)

        def cut_panel_points(
            x1, y1, x2, y2,
            *, cut_tl=0, cut_tr=22, cut_br=22, cut_bl=22,
        ):
            return [
                x1 + cut_tl, y1,
                x2 - cut_tr, y1,
                x2, y1 + cut_tr,
                x2, y2 - cut_br,
                x2 - cut_br, y2,
                x1 + cut_bl, y2,
                x1, y2 - cut_bl,
                x1, y1 + cut_tl,
            ]

        def cut_panel(
            x1, y1, x2, y2,
            *, fill="#FFFEFC", outline="#D9D5CF", accent=None,
            rail="left", cut_tl=0, cut_tr=22, cut_br=22, cut_bl=22,
            tags=(), shadow=True,
        ):
            pts = cut_panel_points(
                x1, y1, x2, y2,
                cut_tl=cut_tl, cut_tr=cut_tr,
                cut_br=cut_br, cut_bl=cut_bl,
            )

            if shadow:
                shadow_pts = []
                for i, value in enumerate(pts):
                    shadow_pts.append(value + (4 if i % 2 else 2))
                canvas.create_polygon(
                    shadow_pts,
                    fill="#D8D2C9",
                    outline="",
                    tags=tags,
                )

            panel_id = canvas.create_polygon(
                pts,
                fill=fill,
                outline=outline,
                width=1,
                tags=tags,
            )

            if accent:
                if rail == "left":
                    canvas.create_line(
                        x1 + 3, y1 + 18,
                        x1 + 3, y2 - 18,
                        fill=accent,
                        width=4,
                        tags=tags,
                    )
                elif rail == "top":
                    canvas.create_line(
                        x1 + 18, y1 + 3,
                        x2 - 36, y1 + 3,
                        fill=accent,
                        width=3,
                        tags=tags,
                    )

            return panel_id

        def choice_box_points(x1, y1, x2, y2, cut=11):
            return [
                x1, y1,
                x2 - cut, y1,
                x2, y1 + cut,
                x2, y2,
                x1 + cut, y2,
                x1, y2 - cut,
            ]

        def choice_box(
            tag,
            x1, y1, x2, y2,
            *,
            accent,
            selected=False,
            hovered=False,
        ):
            # Entourage éditorial interrompu :
            # même forme et même emplacement, sans cadre continu type cellule.
            if selected:
                fill = mix(accent, "#FFFFFF", 0.935)
                mark = accent
                shadow = "#D5D1CA"
            elif hovered:
                fill = mix(accent, "#FFFFFF", 0.972)
                mark = mix(accent, "#FFFFFF", 0.22)
                shadow = "#D9D5CE"
            else:
                fill = "#FFFDFC"
                mark = "#BFC4C6"
                shadow = "#DDD9D2"

            canvas.create_polygon(
                choice_box_points(x1 + 1, y1 + 3, x2 + 1, y2 + 3),
                fill=shadow,
                outline="",
                tags=(tag,),
            )
            canvas.create_polygon(
                choice_box_points(x1, y1, x2, y2),
                fill=fill,
                outline="",
                tags=(tag,),
            )

            # Repères courts : langage de montage éditorial.
            canvas.create_line(
                x1 + 3, y1 + 2,
                x1 + 38, y1 + 2,
                fill=mark,
                width=2 if (selected or hovered) else 1,
                tags=(tag,),
            )
            canvas.create_line(
                x1 + 2, y1 + 3,
                x1 + 2, y1 + 31,
                fill=mark,
                width=2 if (selected or hovered) else 1,
                tags=(tag,),
            )
            canvas.create_line(
                x2 - 42, y1 + 2,
                x2 - 15, y1 + 2,
                fill=mark,
                width=1,
                tags=(tag,),
            )
            canvas.create_line(
                x2 - 36, y2 - 2,
                x2 - 3, y2 - 2,
                fill=mark,
                width=1,
                tags=(tag,),
            )
            canvas.create_line(
                x2 - 2, y2 - 29,
                x2 - 2, y2 - 3,
                fill=mark,
                width=1,
                tags=(tag,),
            )

            rail_y1 = y1 + (y2 - y1) * 0.42
            rail_y2 = y1 + (y2 - y1) * 0.67
            canvas.create_line(
                x1 + 3, rail_y1,
                x1 + 3, rail_y2,
                fill=accent if (selected or hovered) else mix(accent, "#FFFFFF", 0.46),
                width=3 if selected else 2,
                tags=(tag,),
            )

            # Pin : position inchangée, état de sélection réellement visible.
            pin_fill = accent if selected else "#FFFDFC"
            pin_outline = accent if (selected or hovered) else mix(accent, "#FFFFFF", 0.32)

            if hovered and not selected:
                canvas.create_oval(
                    x1 + 11, y1 + 11,
                    x1 + 31, y1 + 31,
                    fill=mix(accent, "#FFFFFF", 0.88),
                    outline="",
                    tags=(tag,),
                )

            canvas.create_oval(
                x1 + 14, y1 + 14,
                x1 + 28, y1 + 28,
                fill=pin_fill,
                outline=pin_outline,
                width=2 if selected else 1,
                tags=(tag,),
            )

            if selected:
                canvas.create_oval(
                    x1 + 18.5, y1 + 18.5,
                    x1 + 23.5, y1 + 23.5,
                    fill="#FFFFFF",
                    outline="",
                    tags=(tag,),
                )

        def round_rect(x1, y1, x2, y2, radius, **kwargs):
            r = max(1, min(radius, (x2 - x1) / 2, (y2 - y1) / 2))
            pts = [
                x1 + r, y1,
                x2 - r, y1,
                x2, y1,
                x2, y1 + r,
                x2, y2 - r,
                x2, y2,
                x2 - r, y2,
                x1 + r, y2,
                x1, y2,
                x1, y2 - r,
                x1, y1 + r,
                x1, y1,
            ]
            return canvas.create_polygon(
                pts,
                smooth=True,
                splinesteps=24,
                **kwargs,
            )

        def bind_interaction(tag, *, command=None):
            # Gestion globale par coordonnées :
            # un redraw ne détruit plus le survol ou le clic en cours.
            if not hasattr(self, "_accueil_prof_hitboxes"):
                self._accueil_prof_hitboxes = {}
            if not hasattr(self, "_accueil_prof_actions"):
                self._accueil_prof_actions = {}

            bbox = canvas.bbox(tag)
            if bbox is not None:
                self._accueil_prof_hitboxes[tag] = bbox
            self._accueil_prof_actions[tag] = command

            if getattr(canvas, "_tomelinea_interactions_bound", False):
                return

            canvas._tomelinea_interactions_bound = True
            self._accueil_prof_hovered = None
            self._accueil_prof_pressed = None

            def tag_at(x, y):
                hitboxes = getattr(self, "_accueil_prof_hitboxes", {})
                for candidate, box in reversed(list(hitboxes.items())):
                    x1, y1, x2, y2 = box
                    if x1 <= x <= x2 and y1 <= y <= y2:
                        return candidate
                return None

            def rerender():
                canvas.after_idle(render)

            def on_motion(event):
                current = tag_at(event.x, event.y)
                previous = getattr(self, "_accueil_prof_hovered", None)

                if current == previous:
                    return

                if previous is not None and previous != self._accueil_prof_pressed:
                    self._accueil_prof_state[previous] = "normal"

                self._accueil_prof_hovered = current

                if current is not None and current != self._accueil_prof_pressed:
                    self._accueil_prof_state[current] = "hover"
                    canvas.configure(cursor="hand2")
                elif current is None:
                    canvas.configure(cursor="arrow")

                rerender()

            def on_leave(_event=None):
                hovered = getattr(self, "_accueil_prof_hovered", None)
                pressed = getattr(self, "_accueil_prof_pressed", None)

                if hovered is not None and hovered != pressed:
                    self._accueil_prof_state[hovered] = "normal"

                self._accueil_prof_hovered = None
                canvas.configure(cursor="arrow")
                rerender()

            def on_press(event):
                current = tag_at(event.x, event.y)
                self._accueil_prof_pressed = current

                if current is not None:
                    self._accueil_prof_state[current] = "pressed"
                    canvas.configure(cursor="hand2")
                    rerender()

            def on_release(event):
                pressed = getattr(self, "_accueil_prof_pressed", None)
                current = tag_at(event.x, event.y)

                self._accueil_prof_pressed = None
                self._accueil_prof_hovered = current

                if pressed is not None:
                    self._accueil_prof_state[pressed] = (
                        "hover" if current == pressed else "normal"
                    )

                if current is not None and current != pressed:
                    self._accueil_prof_state[current] = "hover"

                if pressed is not None and current == pressed:
                    action = getattr(self, "_accueil_prof_actions", {}).get(pressed)
                    if action is not None:
                        action()

                canvas.configure(cursor="hand2" if current else "arrow")
                rerender()

            canvas.bind("<Motion>", on_motion, add="+")
            canvas.bind("<Leave>", on_leave, add="+")
            canvas.bind("<ButtonPress-1>", on_press, add="+")
            canvas.bind("<ButtonRelease-1>", on_release, add="+")

        def draw_primary_button(tag, text, cx, cy, width=205):
            state = self._accueil_prof_state.get(tag, "normal")
            hover = state == "hover"
            pressed = state == "pressed"
            h = 38
            yoff = 1 if pressed else 0
            fill = "#173E70"
            if hover:
                fill = "#24558A"
            if pressed:
                fill = "#12345F"

            round_rect(
                cx - width / 2 + 1, cy - h / 2 + 3,
                cx + width / 2 + 1, cy + h / 2 + 3,
                8,
                fill="#D2CEC8",
                outline="",
                tags=(tag,),
            )
            round_rect(
                cx - width / 2, cy - h / 2 + yoff,
                cx + width / 2, cy + h / 2 + yoff,
                8,
                fill=fill,
                outline="",
                tags=(tag,),
            )
            canvas.create_text(
                cx - 7, cy + yoff,
                text=text,
                fill="#FFFFFF",
                font=("Segoe UI", 9, "bold"),
                tags=(tag,),
            )
            canvas.create_text(
                cx + width / 2 - 23, cy + yoff,
                text="›",
                fill="#FFFFFF",
                font=("Segoe UI", 17),
                tags=(tag,),
            )

        def draw_secondary_button(tag, text, cx, cy, width=138):
            state = self._accueil_prof_state.get(tag, "normal")
            hover = state == "hover"
            pressed = state == "pressed"
            h = 38
            yoff = 1 if pressed else 0
            fill = "#FFFDFC" if not hover else "#F3F7FB"
            border = "#BFC7D0" if not hover else "#496D94"

            round_rect(
                cx - width / 2 + 1, cy - h / 2 + 3,
                cx + width / 2 + 1, cy + h / 2 + 3,
                8,
                fill="#D6D2CC",
                outline="",
                tags=(tag,),
            )
            round_rect(
                cx - width / 2, cy - h / 2 + yoff,
                cx + width / 2, cy + h / 2 + yoff,
                8,
                fill=fill,
                outline=border,
                width=1,
                tags=(tag,),
            )
            canvas.create_text(
                cx - 5, cy + yoff,
                text=text,
                fill="#173E70",
                font=("Segoe UI", 9, "bold"),
                tags=(tag,),
            )
            canvas.create_text(
                cx + width / 2 - 20, cy + yoff,
                text="›",
                fill="#56708A",
                font=("Segoe UI", 16),
                tags=(tag,),
            )

        def draw_chip(x, y, text, bg, fg, width):
            # Information pure : noire, sans couleur et sans cadre.
            canvas.create_text(
                x,
                y + 12,
                text=text,
                fill="#2B3137",
                font=("Segoe UI", 7),
                anchor="w",
            )

        def render(_event=None):
            width = max(canvas.winfo_width(), 1180)
            height = max(canvas.winfo_height(), 620)
            canvas.delete("all")
            self._accueil_prof_hitboxes = {}
            self._accueil_prof_actions = {}

            sx = width / 1600
            sy = height / 760
            scale = min(sx, sy)

            def X(value):
                return value * sx

            def Y(value):
                return value * sy

            def F(value):
                return max(7, int(round(value * scale)))

            if self._accueil_bg_source is not None:
                try:
                    image = cover(self._accueil_bg_source, max(1, width), max(1, height))
                    cream = Image.new("RGB", image.size, (248, 245, 238))
                    image = Image.blend(image, cream, 0.20)
                    self._accueil_bg_photo = ImageTk.PhotoImage(image)
                    canvas.create_image(0, 0, image=self._accueil_bg_photo, anchor="nw")
                except Exception:
                    canvas.configure(bg="#F5F1E9")

            canvas.create_text(
                X(105), Y(48),
                text="Bienvenue dans TomeLinea",
                fill="#173553",
                font=("Georgia", F(23), "bold"),
                anchor="nw",
            )
            canvas.create_text(
                X(107), Y(84),
                text="LA LIGNE ÉDITORIALE JUSQU’AU LIVRE",
                fill="#4C936D",
                font=("Segoe UI", F(9), "bold"),
                anchor="nw",
            )
            canvas.create_text(
                X(107), Y(112),
                text=(
                    "Créez un ouvrage, reprenez le dernier projet "
                    "ou accédez directement au bureau dont vous avez besoin."
                ),
                fill="#5C6670",
                font=("Segoe UI", F(8)),
                anchor="nw",
            )

            line_y = Y(92)
            canvas.create_line(X(665), line_y, X(1320), line_y, fill="#B8C3B7", width=1)
            for x0, color in (
                (865, "#6EB18F"),
                (1060, "#8E70C5"),
                (1235, "#E48767"),
            ):
                canvas.create_oval(
                    X(x0) - 3, line_y - 3,
                    X(x0) + 3, line_y + 3,
                    fill=color,
                    outline="",
                )

            cut_panel(
                X(95), Y(160), X(805), Y(430),
                fill="#FFFEFC",
                outline="#D8D4CE",
                accent="#6FB293",
                rail="left",
                cut_tr=X(28),
                cut_bl=X(26),
                cut_br=X(10),
                tags=("zone_create",),
            )
            canvas.create_text(
                X(145), Y(185),
                text="Créer un nouveau projet",
                fill="#173553",
                font=("Georgia", F(14), "bold"),
                anchor="nw",
            )
            canvas.create_text(
                X(145), Y(216),
                text="Choisissez le type d’ouvrage à créer.",
                fill="#68717A",
                font=("Segoe UI", F(8)),
                anchor="nw",
            )

            choices = (
                ("ouvrage_structure", "Ouvrage structuré", "Fiches, guides,\ncatalogues", "#579B73", 125),
                ("livre_textuel", "Livre textuel", "Roman, récit,\nessai", "#8564B1", 350),
                ("bande_dessinee", "Bande dessinée", "Planches, cases,\nnarration", "#E06B4E", 575),
            )

            for key, title, subtitle, accent, x0 in choices:
                tag = f"choice_{key}"
                state = self._accueil_prof_state.get(tag, "normal")
                hovered = state == "hover"
                selected = self._selected_project_type == key

                bx1 = X(x0)
                by1 = Y(238)
                bx2 = X(x0 + 190)
                by2 = Y(365)

                choice_box(
                    tag, bx1, by1, bx2, by2,
                    accent=accent,
                    selected=selected,
                    hovered=hovered,
                )

                photo = photo_for(key, int(X(92)), int(Y(82)))
                if photo is not None:
                    canvas.create_image(
                        (bx1 + bx2) / 2, Y(285),
                        image=photo,
                        anchor="center",
                        tags=(tag,),
                    )

                canvas.create_text(
                    (bx1 + bx2) / 2, Y(326),
                    text=title,
                    fill=accent,
                    font=("Segoe UI", F(8), "bold"),
                    anchor="center",
                    tags=(tag,),
                )
                canvas.create_text(
                    (bx1 + bx2) / 2, Y(348),
                    text=subtitle,
                    fill="#56616B",
                    font=("Segoe UI", F(7)),
                    justify="center",
                    anchor="center",
                    tags=(tag,),
                )

                def choose(chosen=key):
                    self._selected_project_type = chosen

                bind_interaction(tag, command=choose)

            draw_primary_button(
                "create_project_button",
                "Créer un projet",
                X(450), Y(399),
                width=X(205),
            )
            bind_interaction("create_project_button")

            cut_panel(
                X(825), Y(160), X(1490), Y(430),
                fill="#FFFEFC",
                outline="#D8D4CE",
                accent="#4A98D0",
                rail="left",
                cut_tr=X(28),
                cut_br=X(30),
                cut_bl=X(8),
                tags=("zone_open",),
            )
            canvas.create_text(
                X(875), Y(185),
                text="Ouvrir un projet",
                fill="#173553",
                font=("Georgia", F(14), "bold"),
                anchor="nw",
            )
            canvas.create_line(
                X(875), Y(217), X(905), Y(217),
                fill="#4A98D0", width=2,
            )

            trio = photo_for("trio", int(X(230)), int(Y(150)))
            if trio is not None:
                canvas.create_image(
                    X(1010), Y(295),
                    image=trio,
                    anchor="center",
                )

            canvas.create_text(
                X(1160), Y(246),
                text=(
                    "Accédez à un projet existant,\n"
                    "même s’il ne figure pas parmi\n"
                    "les projets récents."
                ),
                fill="#45515D",
                font=("Segoe UI", F(9)),
                justify="left",
                anchor="nw",
            )
            draw_secondary_button(
                "open_project_button",
                "Ouvrir",
                X(1245), Y(348),
                width=X(140),
            )
            bind_interaction("open_project_button")

            cut_panel(
                X(95), Y(448), X(805), Y(645),
                fill="#FFFEFC",
                outline="#D8D4CE",
                accent="#8B6AB8",
                rail="left",
                cut_tr=X(28),
                cut_br=X(18),
                cut_bl=X(24),
                tags=("zone_recent",),
            )
            canvas.create_text(
                X(145), Y(470),
                text="Reprendre votre travail",
                fill="#173553",
                font=("Georgia", F(13), "bold"),
                anchor="nw",
            )
            canvas.create_line(
                X(360), Y(482), X(755), Y(482),
                fill="#B8A5CF", width=1,
            )
            canvas.create_oval(
                X(750), Y(478), X(758), Y(486),
                fill="#FFFDFC",
                outline="#8B6AB8",
                width=1,
            )
            canvas.create_text(
                X(145), Y(500),
                text="Dernier projet actif et projets ouverts récemment.",
                fill="#68717A",
                font=("Segoe UI", F(8)),
                anchor="nw",
            )

            recent_photo_path = (
                PROJECT_ROOT / "assets" / "gui_v2" / "accueil_icons"
                / "recent_document_64px.png"
            )
            recent_photo = None
            try:
                cache_key = ("recent", 44)
                recent_photo = self._accueil_prof_photos.get(cache_key)
                if recent_photo is None and recent_photo_path.exists():
                    image = Image.open(recent_photo_path).convert("RGBA")
                    image.thumbnail((44, 44), Image.Resampling.LANCZOS)
                    recent_photo = ImageTk.PhotoImage(image)
                    self._accueil_prof_photos[cache_key] = recent_photo
            except Exception:
                recent_photo = None

            if recent_photo is not None:
                canvas.create_image(
                    X(137), Y(553),
                    image=recent_photo,
                    anchor="center",
                )

            canvas.create_text(
                X(175), Y(536),
                text="projet x",
                fill="#173553",
                font=("Segoe UI", F(9), "bold"),
                anchor="nw",
            )
            canvas.create_text(
                X(175), Y(558),
                text="Ouvrage structuré",
                fill="#606B75",
                font=("Segoe UI", F(7)),
                anchor="nw",
            )
            canvas.create_text(
                X(325), Y(548),
                text="▧  22 pages   ●  Maquettage en cours   ◷  10/08/2026 15:23",
                fill="#5E6873",
                font=("Segoe UI", F(7)),
                anchor="w",
            )
            draw_secondary_button(
                "resume_project_button",
                "Reprendre",
                X(705), Y(550),
                width=X(142),
            )
            bind_interaction("resume_project_button")

            canvas.create_line(
                X(125), Y(586), X(765), Y(586),
                fill="#E4E0DA", width=1,
            )
            canvas.create_text(
                X(135), Y(615),
                text="●  nouveau 1",
                fill="#244055",
                font=("Segoe UI", F(8), "bold"),
                anchor="w",
            )
            draw_chip(X(270), Y(603), "Ouvrage structuré", "#F5FAF7", "#4D9870", X(120))
            draw_chip(X(402), Y(603), "En cours", "#F6FAF7", "#4D9870", X(78))
            draw_chip(X(492), Y(603), "Dernier bureau : Maquettage", "#F8F5FB", "#8063A4", X(172))
            canvas.create_text(
                X(765), Y(615),
                text="07/08/2026 16:09",
                fill="#67717B",
                font=("Segoe UI", F(7)),
                anchor="e",
            )

            cut_panel(
                X(825), Y(448), X(1490), Y(645),
                fill="#FFFEFC",
                outline="#D8D4CE",
                accent="#E06B4E",
                rail="left",
                cut_tr=X(28),
                cut_br=X(28),
                cut_bl=X(8),
                tags=("zone_shortcuts",),
            )
            canvas.create_text(
                X(875), Y(470),
                text="Repères & accès directs",
                fill="#173553",
                font=("Georgia", F(13), "bold"),
                anchor="nw",
            )
            canvas.create_text(
                X(875), Y(500),
                text="Raccourcis du dernier projet actif.",
                fill="#68717A",
                font=("Segoe UI", F(8)),
                anchor="nw",
            )

            shortcuts = (
                ("maquettage", "Maquettage", "Organiser les pages", "#579B73", 935),
                ("atelier", "Atelier", "Préparer les gabarits", "#4C9ED0", 1090),
                ("conception", "Conception", "Créer les pages", "#8A69BE", 1245),
                ("centre", "Centre du projet", "Vue d’ensemble", "#E06B4E", 1400),
            )

            for key, title, subtitle, accent, cx0 in shortcuts:
                tag = f"shortcut_{key}"
                state = self._accueil_prof_state.get(tag, "normal")
                hover = state == "hover"
                pressed = state == "pressed"

                cy0 = 548 + (-2 if hover else (1 if pressed else 0))
                radius = 36 if hover else 33

                if hover:
                    canvas.create_oval(
                        X(cx0 - radius - 7), Y(cy0 - radius - 7),
                        X(cx0 + radius + 7), Y(cy0 + radius + 7),
                        fill=mix(accent, "#FFFFFF", 0.92),
                        outline="",
                        tags=(tag,),
                    )

                canvas.create_oval(
                    X(cx0 - radius), Y(cy0 - radius),
                    X(cx0 + radius), Y(cy0 + radius),
                    fill="#FFFDFC",
                    outline=mix(accent, "#FFFFFF", 0.52),
                    width=2 if hover else 1,
                    tags=(tag,),
                )

                state_name = "survol" if hover else "normal"
                photo = self._get_nav_photo(key, state_name, 48)
                if photo is None:
                    photo = self._get_nav_photo(key, "normal", 48)
                if photo is not None:
                    canvas.create_image(
                        X(cx0), Y(cy0),
                        image=photo,
                        anchor="center",
                        tags=(tag,),
                    )

                canvas.create_text(
                    X(cx0), Y(592),
                    text=title,
                    fill=accent if hover else "#173553",
                    font=("Segoe UI", F(8), "bold"),
                    anchor="center",
                    tags=(tag,),
                )
                canvas.create_text(
                    X(cx0), Y(614),
                    text=subtitle,
                    fill="#68717A",
                    font=("Segoe UI", F(7)),
                    anchor="center",
                    tags=(tag,),
                )

                bind_interaction(tag, command=lambda target=key: self.show_screen(target))

            canvas.create_text(
                X(105), Y(742),
                text="TomeLinea V2 (interface de prévisualisation)",
                fill="#7A817E",
                font=("Segoe UI", F(7)),
                anchor="w",
            )
            canvas.create_text(
                X(420), Y(742),
                text="ⓘ  Les fonctions sont désactivées dans cette version.",
                fill="#7A817E",
                font=("Segoe UI", F(7)),
                anchor="w",
            )

        canvas.bind("<Configure>", render, add="+")
        canvas.after_idle(render)


    def _rounded_home_card(
        self,
        parent,
        *,
        title: str,
        accent: str,
        bg: str,
        title_align: str = "center",
        title_color: str | None = None,
        subtitle: str | None = None,
        background_path: Path | None = None,
    ) -> tk.Canvas:
        """Grande zone : fond réellement découpé dans une forme arrondie."""

        parent_bg = parent.cget("bg")
        card = tk.Canvas(
            parent,
            bg=parent_bg,
            bd=0,
            highlightthickness=0,
        )

        radius = 22
        card._pm_bg_source = None
        card._pm_bg_photo = None
        card._pm_composed_pil = None

        if background_path is not None and Path(background_path).exists():
            try:
                card._pm_bg_source = Image.open(background_path).convert("RGBA")
            except Exception:
                card._pm_bg_source = None

        def cover_image(source, width: int, height: int):
            sw, sh = source.size
            scale = max(width / sw, height / sh)
            rw = max(width, int(round(sw * scale)))
            rh = max(height, int(round(sh * scale)))
            image = source.resize((rw, rh), Image.Resampling.LANCZOS)
            left = max(0, (rw - width) // 2)
            top = max(0, (rh - height) // 2)
            return image.crop((left, top, left + width, top + height))

        def redraw(_event=None):
            width = max(card.winfo_width(), 4)
            height = max(card.winfo_height(), 4)
            card.delete("pm_card_bg")

            composed = Image.new("RGBA", (width, height), parent_bg)

            if card._pm_bg_source is not None:
                image = cover_image(card._pm_bg_source, width, height)
            else:
                image = Image.new("RGBA", (width, height), bg)

            mask = Image.new("L", (width, height), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.rounded_rectangle(
                (1, 1, width - 2, height - 2),
                radius=radius,
                fill=255,
            )
            composed.paste(image, (0, 0), mask)

            draw = ImageDraw.Draw(composed)
            draw.rounded_rectangle(
                (1, 1, width - 2, height - 2),
                radius=radius,
                outline=accent,
                width=1,
            )

            # Garde une copie PIL du rendu final afin que les sous-zones
            # puissent reprendre exactement le décor situé derrière elles.
            card._pm_composed_pil = composed.copy()

            card._pm_bg_photo = ImageTk.PhotoImage(composed)
            card.create_image(
                0,
                0,
                image=card._pm_bg_photo,
                anchor="nw",
                tags="pm_card_bg",
            )
            card.tag_lower("pm_card_bg")

            x = 18 if title_align == "left" else width / 2
            anchor = "w" if title_align == "left" else "center"

            card.create_text(
                x,
                24,
                text=title,
                fill=(
                    title_color
                    if title_color is not None
                    else (accent if title_align == "center" else theme.INK)
                ),
                font=("Segoe UI", 12, "bold"),
                anchor=anchor,
                tags="pm_card_bg",
            )

            if subtitle:
                card.create_text(
                    x,
                    51,
                    text=subtitle,
                    fill="#4E5A66",
                    font=("Segoe UI", 8),
                    anchor=anchor,
                    tags="pm_card_bg",
                )

        card.bind("<Configure>", redraw, add="+")
        card.after_idle(redraw)

        spacer = tk.Frame(
            card,
            bg=parent_bg,
            width=1,
            height=64 if subtitle else 46,
            bd=0,
            highlightthickness=0,
        )
        spacer.pack(anchor="w")
        spacer.pack_propagate(False)

        return card

    def _home_card(
        self,
        parent,
        *,
        title: str,
        accent: str,
        bg: str,
        title_align: str = "center",
        subtitle: str | None = None,
        background_path: Path | None = None,
    ) -> tk.Frame:
        """Grande zone de l'accueil avec décor pleine surface."""

        card = tk.Frame(
            parent,
            bg=parent.cget("bg"),
            bd=0,
            highlightthickness=0,
        )

        background = tk.Canvas(
            card,
            bg=bg,
            bd=0,
            highlightthickness=0,
        )
        background.place(x=0, y=0, relwidth=1, relheight=1)

        radius = 18
        card._home_bg_source = None
        card._home_bg_photo = None

        if background_path is not None and Path(background_path).exists():
            try:
                card._home_bg_source = Image.open(background_path).convert("RGBA")
            except Exception:
                card._home_bg_source = None

        def rounded_points(width: int, height: int, r: int):
            return [
                r, 1,
                width - r, 1,
                width - 1, 1,
                width - 1, r,
                width - 1, height - r,
                width - 1, height - 1,
                width - r, height - 1,
                r, height - 1,
                1, height - 1,
                1, height - r,
                1, r,
                1, 1,
            ]

        def cover_image(source, width: int, height: int):
            sw, sh = source.size
            scale = max(width / sw, height / sh)
            rw = max(width, int(round(sw * scale)))
            rh = max(height, int(round(sh * scale)))

            image = source.resize((rw, rh), Image.Resampling.LANCZOS)

            left = max(0, (rw - width) // 2)
            top = max(0, (rh - height) // 2)
            return image.crop((left, top, left + width, top + height))

        def redraw(_event=None):
            background.delete("all")
            width = max(card.winfo_width(), 2)
            height = max(card.winfo_height(), 2)

            # Le décor remplit réellement TOUT le rectangle du widget.
            # Pas de masque alpha : aucun coin blanc possible.
            if card._home_bg_source is not None:
                try:
                    image = cover_image(card._home_bg_source, width, height)
                    card._home_bg_photo = ImageTk.PhotoImage(image)
                    background.create_image(
                        0,
                        0,
                        anchor="nw",
                        image=card._home_bg_photo,
                    )
                except Exception:
                    background.create_rectangle(
                        0, 0, width, height,
                        fill=bg,
                        outline="",
                    )
            else:
                background.create_rectangle(
                    0, 0, width, height,
                    fill=bg,
                    outline="",
                )

            # Le contour arrondi reste dessiné au-dessus du décor.
            background.create_polygon(
                rounded_points(width, height, radius),
                smooth=True,
                splinesteps=36,
                fill="",
                outline=accent,
                width=1,
            )

            x = 18 if title_align == "left" else width / 2
            anchor = "w" if title_align == "left" else "center"

            background.create_text(
                x,
                24,
                text=title,
                fill=accent if title_align == "center" else theme.INK,
                font=("Segoe UI", 12, "bold"),
                anchor=anchor,
            )

            if subtitle:
                background.create_text(
                    x,
                    51,
                    text=subtitle,
                    fill=theme.MUTED,
                    font=("Segoe UI", 8),
                    anchor=anchor,
                )

        card.bind("<Configure>", redraw, add="+")
        card.after_idle(redraw)

        # Réserve uniquement l'espace vertical des textes.
        # 1 px de large : aucune bande opaque sur le décor.
        spacer = tk.Frame(
            card,
            bg=parent.cget("bg"),
            width=1,
            height=64 if subtitle else 46,
            bd=0,
            highlightthickness=0,
        )
        spacer.pack(anchor="w")
        spacer.pack_propagate(False)

        return card


    def _project_type_card(
        self,
        parent,
        *,
        key: str,
        title: str,
        subtitle: str,
        color: str,
        icon_path: Path,
    ) -> tk.Frame:
        """Grand bouton arrondi de choix du type de projet."""

        base_bg = self._mix(color, "#FFFFFF", 0.92)
        hover_bg = self._mix(color, "#FFFFFF", 0.86)
        selected_bg = self._mix(color, "#FFFFFF", 0.82)
        shadow_color = self._mix(color, "#7B817A", 0.62)
        parent_bg = parent.cget("bg")

        shell = tk.Frame(
            parent,
            bg=parent_bg,
            width=165,
            height=119,
            cursor="hand2",
            bd=0,
            highlightthickness=0,
        )
        shell.pack_propagate(False)

        canvas = tk.Canvas(
            shell,
            bg=parent_bg,
            width=165,
            height=119,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        canvas.pack(fill="both", expand=True)

        def rounded_polygon(x1, y1, x2, y2, radius, **kwargs):
            points = [
                x1 + radius, y1,
                x2 - radius, y1,
                x2, y1,
                x2, y1 + radius,
                x2, y2 - radius,
                x2, y2,
                x2 - radius, y2,
                x1 + radius, y2,
                x1, y2,
                x1, y2 - radius,
                x1, y1 + radius,
                x1, y1,
            ]
            return canvas.create_polygon(
                points,
                smooth=True,
                splinesteps=24,
                **kwargs,
            )

        shadow_id = rounded_polygon(
            4, 4, 161, 116,
            12,
            fill=shadow_color,
            outline="",
        )

        card_id = rounded_polygon(
            1, 1, 164, 113,
            12,
            fill=base_bg,
            outline=self._mix(color, "#FFFFFF", 0.36),
            width=1,
        )

        indicator_id = canvas.create_oval(
            10, 9, 21, 20,
            outline=color,
            width=1.4,
            fill="",
        )

        photo = None
        try:
            image = Image.open(icon_path).convert("RGBA")
            image.thumbnail((60, 60), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
        except Exception:
            photo = None

        if photo is not None:
            self._project_type_images[key] = photo
            canvas.create_image(
                82,
                39,
                image=photo,
                anchor="center",
            )
        else:
            canvas.create_text(
                82,
                39,
                text="□",
                fill=color,
                font=("Segoe UI Symbol", 24),
                anchor="center",
            )

        canvas.create_text(
            82,
            76,
            text=title,
            fill=color,
            font=("Segoe UI", 8, "bold"),
            anchor="center",
        )

        canvas.create_text(
            82,
            96,
            text=subtitle,
            fill=theme.MUTED,
            font=("Segoe UI", 7),
            justify="center",
            anchor="center",
        )

        data = {
            "shell": shell,
            "canvas": canvas,
            "color": color,
            "base_bg": base_bg,
            "hover_bg": hover_bg,
            "selected_bg": selected_bg,
            "card_id": card_id,
            "shadow_id": shadow_id,
            "indicator_id": indicator_id,
        }
        self._project_type_cards[key] = data

        def refresh() -> None:
            selected = key == self._selected_project_type

            if selected:
                canvas.itemconfigure(
                    card_id,
                    fill=selected_bg,
                    outline=color,
                    width=2,
                )
                canvas.itemconfigure(
                    indicator_id,
                    fill=color,
                    outline=color,
                )
            else:
                canvas.itemconfigure(
                    card_id,
                    fill=base_bg,
                    outline=self._mix(color, "#FFFFFF", 0.36),
                    width=1,
                )
                canvas.itemconfigure(
                    indicator_id,
                    fill="",
                    outline=color,
                )

        def select(_event=None) -> None:
            self._selected_project_type = key
            for item in self._project_type_cards.values():
                callback = item.get("refresh")
                if callback:
                    callback()

        def enter(_event=None) -> None:
            if key != self._selected_project_type:
                canvas.itemconfigure(card_id, fill=hover_bg)

        def leave(_event=None) -> None:
            refresh()

        data["refresh"] = refresh

        canvas.bind("<Button-1>", select)
        canvas.bind("<Enter>", enter)
        canvas.bind("<Leave>", leave)

        refresh()
        return shell

    def _soft_button(
        self,
        parent,
        text: str,
        color: str,
        *,
        compact: bool = False,
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            state="disabled",
            relief="flat",
            bd=0,
            bg=color,
            fg="#FFFFFF",
            disabledforeground="#FFFFFF",
            padx=14 if compact else 22,
            pady=6 if compact else 7,
            font=("Segoe UI", 8, "bold"),
        )

    def _chip(
        self,
        parent,
        text: str,
        bg: str,
        fg: str,
    ) -> None:
        tk.Label(
            parent,
            text=text,
            bg=bg,
            fg=fg,
            font=("Segoe UI", 7),
            padx=9,
            pady=3,
        ).pack(side="left", padx=(0, 5))

    def _shortcut_box(
        self,
        parent,
        title: str,
        subtitle: str,
        color: str,
    ) -> tk.Frame:
        box = tk.Frame(
            parent,
            bg=self._mix(color, "#FFFFFF", 0.93),
            highlightthickness=1,
            highlightbackground=color,
            height=58,
        )
        box.pack_propagate(False)

        tk.Label(
            box,
            text=title,
            bg=self._mix(color, "#FFFFFF", 0.93),
            fg=theme.INK,
            font=("Segoe UI", 8, "bold"),
            anchor="w",
        ).pack(anchor="w", padx=9, pady=(7, 0))

        tk.Label(
            box,
            text=subtitle,
            bg=self._mix(color, "#FFFFFF", 0.93),
            fg=theme.MUTED,
            font=("Segoe UI", 7),
            anchor="w",
        ).pack(anchor="w", padx=9)

        return box

    # ==========================================================
    # AUTRES ÉCRANS — structure du clone conservée
    # ==========================================================

    def _screen_header(
        self,
        parent: tk.Widget,
        title: str,
        subtitle: str,
        accent: str,
        *,
        visualisation: bool = True,
    ) -> tk.Frame:
        block = tk.Frame(parent, bg=theme.WINDOW)
        block.pack(fill="x", padx=22, pady=(18, 10))

        marker = tk.Frame(block, bg=accent, width=7, height=52)
        marker.pack(side="left", padx=(0, 12))
        marker.pack_propagate(False)

        texts = tk.Frame(block, bg=theme.WINDOW)
        texts.pack(side="left")

        tk.Label(
            texts,
            text=title,
            bg=theme.WINDOW,
            fg=theme.INK,
            font=("Segoe UI", 20, "bold"),
        ).pack(anchor="w")

        tk.Label(
            texts,
            text=subtitle,
            bg=theme.WINDOW,
            fg=theme.MUTED,
            font=("Segoe UI", 10),
        ).pack(anchor="w", pady=(2, 0))

        if visualisation:
            tk.Button(
                block,
                text="◫  Visualisation",
                command=self.open_visualisation_window,
                relief="flat",
                bd=0,
                padx=14,
                pady=8,
                bg=theme.PANEL,
                fg=theme.INK,
                activebackground=accent,
                highlightthickness=1,
                highlightbackground=theme.BORDER,
                font=("Segoe UI", 9, "bold"),
                cursor="hand2",
            ).pack(side="right", padx=4)

        return block

    def _disabled_button(
        self,
        parent: tk.Widget,
        text: str,
        *,
        width: int | None = None,
    ) -> tk.Button:
        return tk.Button(
            parent,
            text=text,
            state="disabled",
            relief="flat",
            bd=0,
            bg=theme.PANEL_ALT,
            fg="#8A8F95",
            disabledforeground="#8A8F95",
            padx=12,
            pady=8,
            width=width,
            font=("Segoe UI", 9),
        )

    def _card(
        self,
        parent: tk.Widget,
        title: str,
        subtitle: str = "",
        *,
        accent: str = theme.SKY,
        width: int = 260,
        height: int = 150,
    ) -> tk.Frame:
        card = tk.Frame(
            parent,
            bg=theme.PANEL,
            width=width,
            height=height,
            highlightthickness=1,
            highlightbackground=theme.BORDER,
        )
        card.pack_propagate(False)

        tk.Frame(card, bg=accent, height=5).pack(fill="x")
        tk.Label(
            card,
            text=title,
            bg=theme.PANEL,
            fg=theme.INK,
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        ).pack(fill="x", padx=14, pady=(12, 4))

        if subtitle:
            tk.Label(
                card,
                text=subtitle,
                bg=theme.PANEL,
                fg=theme.MUTED,
                font=("Segoe UI", 9),
                justify="left",
                anchor="nw",
                wraplength=width - 28,
            ).pack(fill="both", expand=True, padx=14, pady=(0, 10))

        return card

    def _placeholder_columns(
        self,
        parent: tk.Widget,
        columns,
    ) -> None:
        row = tk.Frame(parent, bg=parent.cget("bg"))
        row.pack(fill="both", expand=True, padx=18, pady=8)

        for title, items in columns:
            box = self._card(
                row,
                title,
                accent=theme.CELADON,
                width=210,
                height=250,
            )
            box.pack(side="left", fill="both", expand=True, padx=6)

            for item in items:
                self._disabled_button(box, item).pack(
                    fill="x",
                    padx=12,
                    pady=4,
                )

    def _build_centre(self, parent: tk.Frame) -> None:
        self._screen_header(
            parent,
            "Centre de projet",
            "Pilotage, orientation et vision globale du livre",
            theme.CELADON,
        )

        stats = tk.Frame(parent, bg=theme.WINDOW)
        stats.pack(fill="x", padx=22, pady=7)

        for title, value, accent in (
            ("Pages", "24", theme.SKY),
            ("Parties", "6", theme.LILAC),
            ("Modèles", "8", theme.CELADON),
            ("À vérifier", "3", theme.CORAL),
        ):
            card = self._card(
                stats,
                title,
                value,
                accent=accent,
                width=190,
                height=105,
            )
            card.pack(side="left", fill="x", expand=True, padx=5)

        book = self._card(
            parent,
            "Vue du livre",
            "Synoptique simplifié — les futurs clics pourront orienter vers les bureaux concernés.",
            accent=theme.INK,
            width=900,
            height=310,
        )
        book.pack(fill="both", expand=True, padx=22, pady=8)

        rail = tk.Canvas(
            book,
            bg=theme.PANEL,
            highlightthickness=0,
            height=170,
        )
        rail.pack(fill="both", expand=True, padx=14, pady=8)

        colors = [
            theme.SKY, theme.LILAC, theme.CELADON,
            theme.CORAL, theme.SKY, theme.YELLOW,
        ]
        x = 60
        for index, color in enumerate(colors, start=1):
            rail.create_line(
                x,
                85,
                x + 115,
                85,
                fill="#B8C2C9",
                width=4,
            )
            rail.create_oval(
                x - 13,
                72,
                x + 13,
                98,
                fill=color,
                outline=theme.INK,
            )
            rail.create_text(
                x,
                118,
                text=f"Partie {index}",
                fill=theme.INK,
                font=("Segoe UI", 9, "bold"),
            )
            x += 120

    def _build_maquettage(self, parent: tk.Frame) -> None:
        """Maquettage TomeLinea — structure du livre puis composition des pages."""

        canvas = tk.Canvas(
            parent,
            bg="#F6F2EA",
            highlightthickness=0,
            bd=0,
        )
        canvas.pack(fill="both", expand=True)
        self._maquettage_canvas = canvas

        # ----------------------------------------------------------
        # Modèle visuel provisoire.
        # Plus tard, ce tableau sera remplacé par le modèle métier réel.
        # Structure et composition liront LA MÊME source de données.
        # ----------------------------------------------------------
        structure_model = [
            {"name": "Début", "pages": 3, "color": "#75B89E"},
            {"name": "Partie 1", "pages": 12, "color": "#8D70C7"},
            {"name": "Partie 2", "pages": None, "color": "#72AFCB"},
            {"name": "Partie 3", "pages": None, "color": "#E28A6D"},
            {"name": "Fin", "pages": 3, "color": "#75B89E"},
        ]
        selected_index = 1
        selected_group = structure_model[selected_index]

        self._maquettage_bg_source = None
        self._maquettage_bg_photo = None

        maquettage_bg_path = (
            PROJECT_ROOT
            / "assets"
            / "gui_v2"
            / "maquettage_backgrounds"
            / "maquettage_studio_pro.png"
        )

        if maquettage_bg_path.exists():
            try:
                self._maquettage_bg_source = Image.open(
                    maquettage_bg_path
                ).convert("RGB")
            except Exception:
                self._maquettage_bg_source = None

        def rounded(x1, y1, x2, y2, radius, **kwargs):
            r = max(
                1,
                min(
                    radius,
                    (x2 - x1) / 2,
                    (y2 - y1) / 2,
                ),
            )
            points = [
                x1 + r, y1,
                x2 - r, y1,
                x2, y1,
                x2, y1 + r,
                x2, y2 - r,
                x2, y2,
                x2 - r, y2,
                x1 + r, y2,
                x1, y2,
                x1, y2 - r,
                x1, y1 + r,
                x1, y1,
            ]
            return canvas.create_polygon(
                points,
                smooth=True,
                splinesteps=28,
                **kwargs,
            )

        def zone(
            x1,
            y1,
            x2,
            y2,
            *,
            accent,
            fill,
            title,
            subtitle="",
            **_ignored,
        ):
            # Zone TomeLinea : langage Accueil, géométrie métier inchangée.
            cut = 18

            def panel_points(dx=0, dy=0):
                return [
                    x1 + dx, y1 + dy,
                    x2 - cut + dx, y1 + dy,
                    x2 + dx, y1 + cut + dy,
                    x2 + dx, y2 + dy,
                    x1 + cut + dx, y2 + dy,
                    x1 + dx, y2 - cut + dy,
                ]

            canvas.create_polygon(
                panel_points(2, 4),
                fill="#D3CEC5",
                outline="",
                tags="maquettage_ui",
            )

            canvas.create_polygon(
                panel_points(),
                fill="#FFFEFC",
                outline="#D5D1CA",
                width=1,
                tags="maquettage_ui",
            )

            canvas.create_line(
                x1 + 3,
                y1 + 17,
                x1 + 3,
                y2 - 18,
                fill=accent,
                width=4,
                tags="maquettage_ui",
            )

            canvas.create_line(
                x1 + 20,
                y1 + 43,
                x1 + 48,
                y1 + 43,
                fill=accent,
                width=2,
                tags="maquettage_ui",
            )

            canvas.create_text(
                x1 + 20,
                y1 + 19,
                text=title,
                fill=theme.INK,
                font=("Georgia", 12, "bold"),
                anchor="nw",
                tags="maquettage_ui",
            )

            if subtitle:
                canvas.create_text(
                    x1 + 20,
                    y1 + 51,
                    text=subtitle,
                    fill="#505A64",
                    font=("Segoe UI", 8),
                    anchor="nw",
                    tags="maquettage_ui",
                )

        # ----------------------------------------------------------
        # Interactions des boutons du Maquettage.
        # Elles restent locales à ce bureau afin de ne pas toucher à sa logique.
        # Les zones de clic sont reconstruites à chaque rendu : le survol reste
        # donc stable même lorsque le Canvas est redessiné.
        # ----------------------------------------------------------
        maquettage_button_state: dict[str, str] = {}
        maquettage_button_regions: list[tuple[str, float, float, float, float]] = []
        maquettage_hovered: str | None = None
        maquettage_pressed: str | None = None

        def maquettage_button_id(text, x1, y1, x2, y2):
            return (
                f"{text}|{int(round(x1))}|{int(round(y1))}|"
                f"{int(round(x2))}|{int(round(y2))}"
            )

        def register_maquettage_button(button_id, x1, y1, x2, y2):
            maquettage_button_regions.append((button_id, x1, y1, x2, y2))

        def maquettage_button_at(x, y):
            for button_id, x1, y1, x2, y2 in reversed(maquettage_button_regions):
                if x1 <= x <= x2 and y1 <= y <= y2:
                    return button_id
            return None

        def secondary_button(
            x1,
            y1,
            x2,
            y2,
            text,
            color=None,
            *,
            muted=False,
        ):
            """Bouton secondaire TomeLinea, calé sur le bouton Ouvrir de l'Accueil."""
            radius = 7
            button_id = maquettage_button_id(text, x1, y1, x2, y2)
            register_maquettage_button(button_id, x1, y1, x2, y2)

            state = maquettage_button_state.get(button_id, "normal")
            hover = state == "hover"
            pressed = state == "pressed"
            yoff = 1 if pressed else 0

            if pressed:
                fill = "#E9F0F7"
                border = "#355C85"
            elif hover:
                fill = "#F3F7FB"
                border = "#496D94"
            else:
                fill = "#FFFDFC"
                border = "#BFC7D0"

            rounded(
                x1 + 1,
                y1 + 3,
                x2 + 1,
                y2 + 3,
                radius,
                fill="#D6D2CC",
                outline="",
                tags="maquettage_ui",
            )
            rounded(
                x1,
                y1 + yoff,
                x2,
                y2 + yoff,
                radius,
                fill=fill,
                outline=border,
                width=1,
                tags="maquettage_ui",
            )

            button_width = x2 - x1
            text_shift = 5 if button_width >= 82 else 4
            chevron_inset = 16 if button_width >= 82 else 9
            canvas.create_text(
                (x1 + x2) / 2 - text_shift,
                (y1 + y2) / 2 + yoff,
                text=text,
                fill="#173E70",
                font=("Segoe UI", 8, "bold"),
                anchor="center",
                tags="maquettage_ui",
            )
            canvas.create_text(
                x2 - chevron_inset,
                (y1 + y2) / 2 + yoff,
                text="›",
                fill="#56708A",
                font=("Segoe UI", 14),
                anchor="center",
                tags="maquettage_ui",
            )

        def primary_button(
            x1,
            y1,
            x2,
            y2,
            text,
        ):
            """Bouton principal TomeLinea, calé sur Créer un projet de l'Accueil."""
            radius = 7
            button_id = maquettage_button_id(text, x1, y1, x2, y2)
            register_maquettage_button(button_id, x1, y1, x2, y2)

            state = maquettage_button_state.get(button_id, "normal")
            hover = state == "hover"
            pressed = state == "pressed"
            yoff = 1 if pressed else 0

            fill = "#173E70"
            if hover:
                fill = "#24558A"
            if pressed:
                fill = "#12345F"

            rounded(
                x1 + 1,
                y1 + 3,
                x2 + 1,
                y2 + 3,
                radius,
                fill="#D2CEC8",
                outline="",
                tags="maquettage_ui",
            )
            rounded(
                x1,
                y1 + yoff,
                x2,
                y2 + yoff,
                radius,
                fill=fill,
                outline="",
                tags="maquettage_ui",
            )
            canvas.create_text(
                (x1 + x2) / 2 - 6,
                (y1 + y2) / 2 + yoff,
                text=text,
                fill="#FFFFFF",
                font=("Segoe UI", 8, "bold"),
                anchor="center",
                tags="maquettage_ui",
            )
            canvas.create_text(
                x2 - 17,
                (y1 + y2) / 2 + yoff,
                text="›",
                fill="#FFFFFF",
                font=("Segoe UI", 15),
                anchor="center",
                tags="maquettage_ui",
            )

        def divider(x, y1, y2):
            canvas.create_line(
                x,
                y1,
                x,
                y2,
                fill="#DCD6CE",
                width=1,
                tags="maquettage_ui",
            )

        def render(_event=None):
            width = max(canvas.winfo_width(), 1180)
            height = max(canvas.winfo_height(), 720)

            maquettage_button_regions.clear()
            canvas.delete("all")

            # ------------------------------------------------------
            # Décor éditorial continu : aucun panneau technique
            # ajouté derrière l'interface.
            # ------------------------------------------------------
            if self._maquettage_bg_source is not None:
                image = self._maquettage_bg_source.resize(
                    (width, height),
                    Image.Resampling.LANCZOS,
                )
                self._maquettage_bg_photo = ImageTk.PhotoImage(image)
                canvas.create_image(
                    0,
                    0,
                    image=self._maquettage_bg_photo,
                    anchor="nw",
                    tags="maquettage_bg",
                )
            else:
                canvas.create_rectangle(
                    0,
                    0,
                    width,
                    height,
                    fill="#F6F2EA",
                    outline="",
                    tags="maquettage_bg",
                )

            # ------------------------------------------------------
            # PÔLE 1 — STRUCTURE DU LIVRE
            # Fusion de l'ancienne barre des groupes et de la vue globale.
            # ------------------------------------------------------
            margin = 44
            top_y1 = 14
            top_y2 = 188

            zone(
                margin,
                top_y1,
                width - margin,
                top_y2,
                accent="#8D70C7",
                fill="#FBF8FD",
                title="Structure du livre",
                subtitle="Groupes, ordre et nombre de pages du livre.",
            )

            tools_width = 292
            tools_left = width - margin - tools_width

            track_left = margin + 32
            track_right = tools_left - 24
            track_y = top_y1 + 102

            # Variante B — Fil + repères (référence visuelle validée).
            node_count = len(structure_model)

            skeleton_left = track_left + 36
            skeleton_right = track_right - 36
            if node_count > 1:
                node_step = (skeleton_right - skeleton_left) / (node_count - 1)
            else:
                node_step = 0

            node_centers = [
                skeleton_left + index * node_step
                for index in range(node_count)
            ]

            if not hasattr(self, "_maquettage_structure_photos"):
                self._maquettage_structure_photos = {}

            structure_icon_dir = (
                PROJECT_ROOT / "assets" / "gui_v2" / "structure_line_icons"
            )
            structure_icon_paths = [
                structure_icon_dir / "debut.png",
                structure_icon_dir / "partie_1.png",
                structure_icon_dir / "partie_2.png",
                structure_icon_dir / "partie_3.png",
                structure_icon_dir / "fin.png",
            ]

            def structure_photo(path, max_w, max_h):
                key = (str(path), max_w, max_h)
                cached = self._maquettage_structure_photos.get(key)
                if cached is not None:
                    return cached
                if not path.exists():
                    return None
                try:
                    image = Image.open(path).convert("RGBA")
                    image.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(image)
                    self._maquettage_structure_photos[key] = photo
                    return photo
                except Exception:
                    return None

            # Fil neutre continu.
            canvas.create_line(
                skeleton_left,
                track_y,
                skeleton_right,
                track_y,
                fill="#BEB9B1",
                width=1,
                tags="maquettage_ui",
            )

            for index, group in enumerate(structure_model):
                cx = node_centers[index]
                color = group["color"]
                is_selected = index == selected_index

                # Repère coloré : segment court + petite barre verticale.
                segment_half = min(58, max(34, node_step * 0.22))
                canvas.create_line(
                    cx - segment_half,
                    track_y,
                    cx + segment_half,
                    track_y,
                    fill=self._mix(color, "#FFFFFF", 0.12),
                    width=3 if is_selected else 2,
                    capstyle="round",
                    tags="maquettage_ui",
                )
                canvas.create_line(
                    cx,
                    track_y,
                    cx,
                    track_y - 12,
                    fill=self._mix(color, theme.INK, 0.22),
                    width=2,
                    tags="maquettage_ui",
                )

                # Icône réaliste, sans disque ni cadre.
                photo_index = min(index, len(structure_icon_paths) - 1)
                photo = structure_photo(
                    structure_icon_paths[photo_index],
                    50 if 0 < index < node_count - 1 else 38,
                    44,
                )
                if photo is not None:
                    canvas.create_image(
                        cx,
                        track_y - 31,
                        image=photo,
                        anchor="center",
                        tags="maquettage_ui",
                    )

                pages = group["pages"]
                pages_label = (
                    f"{pages} pages"
                    if isinstance(pages, int)
                    else "— pages"
                )

                # Libellé sous la ligne, comme sur la référence.
                canvas.create_text(
                    cx,
                    track_y + 27,
                    text=group["name"],
                    fill=self._mix(color, theme.INK, 0.34),
                    font=("Georgia", 10, "bold"),
                    anchor="center",
                    tags="maquettage_ui",
                )
                canvas.create_text(
                    cx,
                    track_y + 48,
                    text=pages_label,
                    fill="#4E5964",
                    font=("Segoe UI", 8),
                    anchor="center",
                    tags="maquettage_ui",
                )

                # Sélection : simple soulignement, jamais de carré de fond.
                if is_selected:
                    canvas.create_line(
                        cx - 28,
                        track_y + 65,
                        cx + 28,
                        track_y + 65,
                        fill=color,
                        width=3,
                        capstyle="round",
                        tags="maquettage_ui",
                    )

            # Outils de structure : espace réservé à droite du linéaire.
            canvas.create_line(
                tools_left - 12,
                top_y1 + 18,
                tools_left - 12,
                top_y2 - 18,
                fill="#D9D3CB",
                width=1,
                tags="maquettage_ui",
            )

            canvas.create_text(
                tools_left + 8,
                top_y1 + 23,
                text="Outils de structure",
                fill=theme.INK,
                font=("Georgia", 10, "bold"),
                anchor="nw",
                tags="maquettage_ui",
            )

            tool_x1 = tools_left + 8
            tool_x2 = width - margin - 10
            tool_gap = 8
            tool_half = (tool_x2 - tool_x1 - tool_gap) / 2

            secondary_button(
                tool_x1,
                top_y1 + 50,
                tool_x1 + tool_half,
                top_y1 + 83,
                "+ Partie",
                "#75B89E",
                muted=True,
            )
            secondary_button(
                tool_x1 + tool_half + tool_gap,
                top_y1 + 50,
                tool_x2,
                top_y1 + 83,
                "Renommer",
                "#72AFCB",
                muted=True,
            )

            arrow_w = 48
            delete_w = max(
                92,
                tool_x2 - tool_x1 - arrow_w * 2 - tool_gap * 2,
            )
            secondary_button(
                tool_x1,
                top_y1 + 94,
                tool_x1 + arrow_w,
                top_y1 + 127,
                "←",
                "#8D70C7",
                muted=True,
            )
            secondary_button(
                tool_x1 + arrow_w + tool_gap,
                top_y1 + 94,
                tool_x1 + arrow_w * 2 + tool_gap,
                top_y1 + 127,
                "→",
                "#8D70C7",
                muted=True,
            )
            secondary_button(
                tool_x2 - delete_w,
                top_y1 + 94,
                tool_x2,
                top_y1 + 127,
                "Supprimer",
                "#E28A6D",
                muted=True,
            )

            # ------------------------------------------------------
            # PÔLE 2 — COMPOSITION DE LA PARTIE SÉLECTIONNÉE
            # ------------------------------------------------------
            work_y1 = top_y2 + 12
            work_y2 = height - 52

            left_w = 250
            right_w = 300
            gap = 12

            left_x1 = margin
            left_x2 = left_x1 + left_w

            center_x1 = left_x2 + gap
            center_x2 = width - margin - right_w - gap

            right_x1 = center_x2 + gap
            right_x2 = width - margin

            zone(
                left_x1,
                work_y1,
                left_x2,
                work_y2,
                accent="#75B89E",
                fill="#F7FBF8",
                title="Détail de la partie",
                subtitle=selected_group["name"],
            )

            zone(
                center_x1,
                work_y1,
                center_x2,
                work_y2,
                accent="#8D70C7",
                fill="#FBF8FD",
                title=f"Composition de {selected_group['name']}",
                subtitle=(
                    "Attribuez un type aux pages et construisez leur ordre."
                ),
            )

            zone(
                right_x1,
                work_y1,
                right_x2,
                work_y2,
                accent="#E28A6D",
                fill="#FDF8F5",
                title="Propriétés de la page",
                subtitle="Caractéristiques de l’élément sélectionné.",
            )

            # Le choix des types est intégré au bandeau de Composition.
            type_button_w = 172
            type_button_x2 = center_x2 - 18
            type_button_x1 = type_button_x2 - type_button_w

            canvas.create_text(
                type_button_x1 - 12,
                work_y1 + 27,
                text="Types : 0",
                fill="#6E5A89",
                font=("Segoe UI", 8, "bold"),
                anchor="e",
                tags="maquettage_ui",
            )
            primary_button(
                type_button_x1,
                work_y1 + 12,
                type_button_x2,
                work_y1 + 45,
                "+ Créer / choisir un type",
            )

            # ------------------------------------------------------
            # COLONNE GAUCHE — détail de la partie
            # ------------------------------------------------------
            lx = left_x1 + 22
            ly = work_y1 + 90

            canvas.create_text(
                lx,
                ly,
                text=selected_group["name"],
                fill="#173B6C",
                font=("Segoe UI", 15, "bold"),
                anchor="nw",
                tags="maquettage_ui",
            )

            ly += 38

            metrics = (
                (
                    "Pages prévues",
                    str(selected_group["pages"]),
                    "#173B6C",
                ),
                ("Pages définies", "0 / 12", "#72AFCB"),
                ("Types distincts", "0", "#8D70C7"),
                ("Gabarits minimum", "0", "#75B89E"),
                ("Gabarits prévus", "—", "#E28A6D"),
            )

            for label, value, color in metrics:
                canvas.create_text(
                    lx,
                    ly,
                    text=label,
                    fill="#59646E",
                    font=("Segoe UI", 8),
                    anchor="nw",
                    tags="maquettage_ui",
                )
                canvas.create_text(
                    left_x2 - 22,
                    ly,
                    text=value,
                    fill=color,
                    font=("Segoe UI", 10, "bold"),
                    anchor="ne",
                    tags="maquettage_ui",
                )
                ly += 34

            canvas.create_line(
                left_x1 + 20,
                ly + 2,
                left_x2 - 20,
                ly + 2,
                fill="#DDD8D1",
                width=1,
                tags="maquettage_ui",
            )

            canvas.create_text(
                lx,
                ly + 20,
                text=(
                    "Ces valeurs suivront automatiquement\n"
                    "la composition réelle de cette partie."
                ),
                fill="#66717B",
                font=("Segoe UI", 8),
                anchor="nw",
                justify="left",
                tags="maquettage_ui",
            )

            # ------------------------------------------------------
            # CENTRE — pages de la partie sélectionnée
            # ------------------------------------------------------
            cx1 = center_x1 + 22
            cx2 = center_x2 - 22
            pages_top = work_y1 + 86

            page_count = int(selected_group["pages"] or 0)

            # Disposition responsive, maximum 6 par ligne.
            available = max(cx2 - cx1, 320)
            page_w = 64
            page_h = 86
            page_gap = 12
            cols = max(
                4,
                min(
                    6,
                    int(
                        (available + page_gap)
                        // (page_w + page_gap)
                    ),
                ),
            )

            for index in range(page_count):
                row = index // cols
                col = index % cols
                px1 = cx1 + col * (page_w + page_gap)
                py1 = pages_top + row * (page_h + 16)
                px2 = px1 + page_w
                py2 = py1 + page_h

                rounded(
                    px1 + 1,
                    py1 + 3,
                    px2 + 1,
                    py2 + 3,
                    11,
                    fill="#D8D2CA",
                    outline="",
                    tags="maquettage_ui",
                )
                rounded(
                    px1,
                    py1,
                    px2,
                    py2,
                    11,
                    fill="#FFFDF9",
                    outline="#D9D3CB",
                    width=1,
                    tags="maquettage_ui",
                )

                canvas.create_rectangle(
                    px1 + 13,
                    py1 + 15,
                    px2 - 13,
                    py2 - 24,
                    outline="#DDD7CF",
                    width=1,
                    tags="maquettage_ui",
                )
                canvas.create_text(
                    (px1 + px2) / 2,
                    py2 - 13,
                    text=str(index + 1),
                    fill="#6A7480",
                    font=("Segoe UI", 8, "bold"),
                    anchor="center",
                    tags="maquettage_ui",
                )

            # ------------------------------------------------------
            # DROITE — propriétés de la page
            # ------------------------------------------------------
            rx = right_x1 + 22

            # Outils immédiatement sous l'en-tête de la zone.
            action_y = work_y1 + 78
            half = (right_x2 - right_x1 - 52) / 2
            ax1 = right_x1 + 20
            ax2 = ax1 + half

            secondary_button(
                ax1,
                action_y,
                ax2,
                action_y + 32,
                "Monter",
                "#72AFCB",
                muted=True,
            )
            secondary_button(
                ax2 + 12,
                action_y,
                right_x2 - 20,
                action_y + 32,
                "Descendre",
                "#72AFCB",
                muted=True,
            )
            secondary_button(
                ax1,
                action_y + 40,
                ax2,
                action_y + 72,
                "Dupliquer",
                "#8D70C7",
                muted=True,
            )
            secondary_button(
                ax2 + 12,
                action_y + 40,
                right_x2 - 20,
                action_y + 72,
                "Supprimer",
                "#E28A6D",
                muted=True,
            )

            # Informations sur la page sous les outils.
            ry = work_y1 + 174

            canvas.create_text(
                rx,
                ry,
                text="Aucune page sélectionnée",
                fill="#173B6C",
                font=("Segoe UI", 12, "bold"),
                anchor="nw",
                tags="maquettage_ui",
            )
            canvas.create_text(
                rx,
                ry + 28,
                text=(
                    "Sélectionnez une page dans la composition\n"
                    "pour afficher ses caractéristiques."
                ),
                fill="#66717B",
                font=("Segoe UI", 8),
                anchor="nw",
                justify="left",
                tags="maquettage_ui",
            )

            ry += 82
            divider(right_x1 + 20, ry - 10, ry + 140)

            properties = (
                ("Type", "—"),
                ("Nom / repère", "—"),
                ("Gabarit prévu", "—"),
                ("Recto-verso", "—"),
            )

            for label, value in properties:
                canvas.create_text(
                    rx + 12,
                    ry,
                    text=label,
                    fill="#59646E",
                    font=("Segoe UI", 8),
                    anchor="nw",
                    tags="maquettage_ui",
                )
                canvas.create_text(
                    right_x2 - 22,
                    ry,
                    text=value,
                    fill="#173B6C",
                    font=("Segoe UI", 9, "bold"),
                    anchor="ne",
                    tags="maquettage_ui",
                )
                ry += 34

        def on_maquettage_motion(event):
            nonlocal maquettage_hovered

            current = maquettage_button_at(event.x, event.y)
            previous = maquettage_hovered
            if current == previous:
                canvas.configure(cursor="hand2" if current else "arrow")
                return

            if previous is not None and previous != maquettage_pressed:
                maquettage_button_state[previous] = "normal"

            maquettage_hovered = current

            if current is not None and current != maquettage_pressed:
                maquettage_button_state[current] = "hover"

            canvas.configure(cursor="hand2" if current else "arrow")
            render()

        def on_maquettage_leave(_event=None):
            nonlocal maquettage_hovered

            if (
                maquettage_hovered is not None
                and maquettage_hovered != maquettage_pressed
            ):
                maquettage_button_state[maquettage_hovered] = "normal"

            maquettage_hovered = None
            canvas.configure(cursor="arrow")
            render()

        def on_maquettage_press(event):
            nonlocal maquettage_pressed, maquettage_hovered

            current = maquettage_button_at(event.x, event.y)
            maquettage_pressed = current
            maquettage_hovered = current

            if current is not None:
                maquettage_button_state[current] = "pressed"
                canvas.configure(cursor="hand2")
                render()

        def on_maquettage_release(event):
            nonlocal maquettage_pressed, maquettage_hovered

            pressed = maquettage_pressed
            current = maquettage_button_at(event.x, event.y)

            maquettage_pressed = None
            maquettage_hovered = current

            if pressed is not None:
                maquettage_button_state[pressed] = (
                    "hover" if current == pressed else "normal"
                )

            if current is not None and current != pressed:
                maquettage_button_state[current] = "hover"

            canvas.configure(cursor="hand2" if current else "arrow")
            render()

        canvas.bind("<Motion>", on_maquettage_motion, add="+")
        canvas.bind("<Leave>", on_maquettage_leave, add="+")
        canvas.bind("<ButtonPress-1>", on_maquettage_press, add="+")
        canvas.bind("<ButtonRelease-1>", on_maquettage_release, add="+")

        canvas.bind("<Configure>", render)
        canvas.after_idle(render)

    def _build_atelier(self, parent: tk.Frame) -> None:
        self._screen_header(
            parent,
            "Atelier",
            "Structure des gabarits et préparation des modèles",
            theme.SKY,
        )

        stages = (
            ("0", "Modèle", "Rappel du modèle ou création libre"),
            ("1", "Format", "Format, fond perdu, fond fixe ou variable"),
            ("2", "Marges", "Marges et zones de sécurité"),
            ("3", "Zones", "Création des zones de remplissage"),
            ("4", "Attribution", "Rôle de chaque zone"),
            ("5", "Modèle", "Création du modèle"),
            ("6", "Enregistrer", "Enregistrement"),
            ("7", "Conception", "Mise à disposition"),
        )

        grid = tk.Frame(parent, bg=theme.WINDOW)
        grid.pack(fill="both", expand=True, padx=22, pady=8)

        for idx, (num, title, subtitle) in enumerate(stages):
            card = self._card(
                grid,
                f"{num} — {title}",
                subtitle,
                accent=(
                    theme.SKY,
                    theme.CELADON,
                    theme.LILAC,
                    theme.CORAL,
                )[idx % 4],
                width=250,
                height=135,
            )
            card.grid(
                row=idx // 4,
                column=idx % 4,
                sticky="nsew",
                padx=5,
                pady=5,
            )
            grid.grid_columnconfigure(idx % 4, weight=1)
            grid.grid_rowconfigure(idx // 4, weight=1)

            self._disabled_button(card, "Commande").pack(
                fill="x", padx=12, pady=8
            )

    def _build_conception(self, parent: tk.Frame) -> None:
        self._screen_header(
            parent,
            "Conception",
            "Production des pages réelles — page par page ou en lots",
            theme.CORAL,
        )

        body = tk.Frame(parent, bg=theme.WINDOW)
        body.pack(fill="both", expand=True, padx=22, pady=8)

        resources = self._card(
            body,
            "1 — Import et vérification",
            "Ressources du projet, état, conformité et disponibilité.",
            accent=theme.CELADON,
            width=250,
            height=520,
        )
        resources.pack(side="left", fill="y", padx=(0, 6))

        for label in ("Images", "Textes", "Logos", "Icônes", "Polices"):
            self._disabled_button(resources, label).pack(
                fill="x", padx=12, pady=4
            )

        editor = self._card(
            body,
            "2 — Conception page à page",
            "Surface de page centrale. Les outils seront rebranchés ultérieurement.",
            accent=theme.CORAL,
            width=620,
            height=520,
        )
        editor.pack(side="left", fill="both", expand=True, padx=6)

        page = tk.Frame(
            editor,
            bg=theme.WHITE,
            width=330,
            height=430,
            highlightthickness=1,
            highlightbackground=theme.BORDER,
        )
        page.pack(pady=16)
        page.pack_propagate(False)

        batch = self._card(
            body,
            "3 — Lots",
            "Production répétée ou semi-automatique à partir d'un modèle.",
            accent=theme.LILAC,
            width=235,
            height=520,
        )
        batch.pack(side="left", fill="y", padx=(6, 0))

        for label in (
            "Créer un lot",
            "Associer des données",
            "Prévisualiser",
            "Valider les pages",
            "Retour Atelier",
        ):
            self._disabled_button(batch, label).pack(
                fill="x", padx=12, pady=4
            )

    def _build_assemblage(self, parent: tk.Frame) -> None:
        self._screen_header(
            parent,
            "Assemblage",
            "Ordre du livre, double-pages et chemin de fer",
            theme.CELADON,
        )

        toolbar = tk.Frame(parent, bg=theme.WINDOW)
        toolbar.pack(fill="x", padx=22, pady=8)

        for label in (
            "Mode double-pages",
            "Zoom -",
            "Zoom +",
            "Déplacer",
            "Retour Atelier",
            "Retour Conception",
            "Enregistrer",
        ):
            self._disabled_button(toolbar, label).pack(
                side="left", padx=(0, 6)
            )

        book = self._card(
            parent,
            "Livre assemblé",
            "Surface de contrôle visuel de l'ordre des pages.",
            accent=theme.CELADON,
            width=1000,
            height=520,
        )
        book.pack(fill="both", expand=True, padx=22, pady=8)

        canvas = tk.Canvas(
            book,
            bg="#ECEAE4",
            highlightthickness=0,
        )
        canvas.pack(fill="both", expand=True, padx=14, pady=10)

        x = 38
        y = 45
        for spread in range(5):
            for side in range(2):
                canvas.create_rectangle(
                    x,
                    y,
                    x + 125,
                    y + 180,
                    fill=theme.WHITE,
                    outline=theme.BORDER,
                )
                canvas.create_text(
                    x + 62,
                    y + 90,
                    text=f"Page {spread * 2 + side + 1}",
                    fill=theme.MUTED,
                    font=("Segoe UI", 8),
                )
                x += 132
            x += 26

    def _build_verification(self, parent: tk.Frame) -> None:
        self._screen_header(
            parent,
            "Vérification",
            "Contrôle global avant finalisation",
            theme.YELLOW,
        )

        body = tk.Frame(parent, bg=theme.WINDOW)
        body.pack(fill="both", expand=True, padx=22, pady=8)

        control = self._card(
            body,
            "Contrôles",
            "Fenêtre de contrôle basée sur la visualisation.",
            accent=theme.YELLOW,
            width=280,
            height=520,
        )
        control.pack(side="left", fill="y", padx=(0, 6))

        for label in (
            "Dimensions",
            "Marges",
            "Images",
            "Ressources",
            "Pages manquantes",
            "Cohérence",
            "Retour Atelier",
            "Retour Conception",
        ):
            self._disabled_button(control, label).pack(
                fill="x", padx=12, pady=4
            )

        viewer = self._card(
            body,
            "Mode pleine page",
            "Défilement des pages et contrôle visuel.",
            accent=theme.INK,
            width=700,
            height=520,
        )
        viewer.pack(side="left", fill="both", expand=True, padx=(6, 0))

        page = tk.Frame(
            viewer,
            bg=theme.WHITE,
            width=330,
            height=435,
            highlightthickness=1,
            highlightbackground=theme.BORDER,
        )
        page.pack(pady=15)
        page.pack_propagate(False)

    def _build_finalisation(self, parent: tk.Frame) -> None:
        self._screen_header(
            parent,
            "Finalisation & Export",
            "Production des fichiers définitifs",
            theme.LILAC,
        )

        body = tk.Frame(parent, bg=theme.WINDOW)
        body.pack(fill="both", expand=True, padx=22, pady=8)

        cols = (
            (
                "Contenu",
                (
                    "PDF intérieur",
                    "Contrôle final",
                    "Profil d'impression",
                ),
            ),
            (
                "Couverture",
                (
                    "Couverture",
                    "Dos",
                    "Quatrième",
                ),
            ),
            (
                "Exports",
                (
                    "Créer les 3 PDF",
                    "Format e-book",
                    "Archive projet",
                ),
            ),
        )

        for title, items in cols:
            card = self._card(
                body,
                title,
                "Commandes présentes mais non branchées.",
                accent=theme.LILAC,
                width=320,
                height=360,
            )
            card.pack(side="left", fill="both", expand=True, padx=6)

            for item in items:
                self._disabled_button(card, item).pack(
                    fill="x", padx=14, pady=7
                )

    # ==========================================================
    # OUTILS COULEURS
    # ==========================================================

    @staticmethod
    def _mix(a: str, b: str, ratio: float) -> str:
        ratio = max(0.0, min(1.0, ratio))

        def rgb(value: str):
            value = value.lstrip("#")
            return tuple(
                int(value[i:i + 2], 16)
                for i in (0, 2, 4)
            )

        ar, ag, ab = rgb(a)
        br, bg, bb = rgb(b)

        r = round(ar * (1 - ratio) + br * ratio)
        g = round(ag * (1 - ratio) + bg * ratio)
        bl = round(ab * (1 - ratio) + bb * ratio)

        return f"#{r:02X}{g:02X}{bl:02X}"
