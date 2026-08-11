from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk, ImageDraw

from src.gui_v2 import theme
from src.gui_v2.components import PMCommandButton


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ACCUEIL_BG = (
    PROJECT_ROOT
    / "assets"
    / "interface"
    / "backgrounds"
    / "editorial_bg_accueil.png"
)


class PageMaitreV2(tk.Tk):
    """Prototype parallèle PageMaître V2 — navigation et apparence."""

    def __init__(self) -> None:
        super().__init__()

        self.title("PageMaître — Interface V2")
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
            "maquettage": "Bureau de maquettage",
            "atelier": "Atelier",
            "conception": "Bureau de conception",
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
        photo = self._get_nav_photo(key, state, 48)
        if photo is not None:
            self._header_canvas_images.append(photo)
            canvas.create_image(
                x, y - 18,
                image=photo,
                anchor="center",
                tags=(f"nav_{key}", "nav_item"),
            )

        canvas.create_text(
            x, y + 18,
            text=label,
            anchor="n",
            fill=theme.INK,
            font=(
                ("Segoe UI", 8, "bold")
                if state == "actif"
                else ("Segoe UI", 8)
            ),
            tags=(f"nav_{key}", "nav_item"),
        )

        canvas.create_text(
            x, y + 39,
            text="•",
            anchor="n",
            fill=accent,
            font=("Segoe UI", 11, "bold"),
            tags=(f"nav_{key}", "nav_item"),
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
        win.title("Gérer — PageMaître V2")
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
        win.title("Visualisation — PageMaître V2")
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
        """Accueil inspiré du visuel PageMaître validé."""

        canvas = tk.Canvas(
            parent,
            bg="#F6F2EA",
            highlightthickness=0,
        )
        canvas.pack(fill="both", expand=True)

        self._accueil_canvas = canvas

        # Sélection du type de projet : aucun choix au départ.
        self._selected_project_type = None
        self._project_type_cards = {}
        self._project_type_images = {}

        if ACCUEIL_BG.exists():
            try:
                image = Image.open(ACCUEIL_BG).convert("RGB")
                image = image.resize(
                    (1600, 900),
                    Image.Resampling.LANCZOS,
                )
                self._accueil_bg_source = image
                self._accueil_bg_photo = ImageTk.PhotoImage(image)
                canvas.create_image(
                    0,
                    0,
                    image=self._accueil_bg_photo,
                    anchor="nw",
                    tags="accueil_bg",
                )
            except Exception:
                pass

        # Le contenu est posé sur un Canvas éditorial afin que le décor reste
        # visible entre les cartes, au lieu d'un grand panneau uni.
        content = tk.Canvas(
            canvas,
            bg="#F6F2EA",
            highlightthickness=0,
            bd=0,
        )
        self._accueil_content = content
        self._accueil_layer_photos = {}

        window_id = canvas.create_window(
            0,
            10,
            window=content,
            anchor="n",
        )

        def paint_layer(target, key):
            if self._accueil_bg_source is None:
                return
            width = max(target.winfo_width(), 1)
            height = max(target.winfo_height(), 1)
            image = self._accueil_bg_source.resize(
                (width, height),
                Image.Resampling.LANCZOS,
            )
            photo = ImageTk.PhotoImage(image)
            self._accueil_layer_photos[key] = photo
            target.delete(f"{key}_bg")
            target.create_image(
                0, 0, image=photo, anchor="nw", tags=f"{key}_bg"
            )
            target.tag_lower(f"{key}_bg")

        def resize_content(event):
            if self._accueil_bg_source is not None:
                image = self._accueil_bg_source.resize(
                    (max(event.width, 1), max(event.height, 1)),
                    Image.Resampling.LANCZOS,
                )
                self._accueil_bg_photo = ImageTk.PhotoImage(image)
                canvas.itemconfigure("accueil_bg", image=self._accueil_bg_photo)
                canvas.tag_lower("accueil_bg")

            content_width = min(max(event.width - 150, 980), 1240)
            content_height = max(event.height - 20, 600)
            canvas.coords(window_id, event.width / 2, 10)
            canvas.itemconfigure(
                window_id,
                width=content_width,
                height=content_height,
            )
            content.after_idle(lambda: paint_layer(content, "content"))

        canvas.bind("<Configure>", resize_content)
        content.bind(
            "<Configure>",
            lambda _event: paint_layer(content, "content"),
            add="+",
        )

        # Zone bienvenue.
        welcome = tk.Frame(content, bg="#F8F4EC")
        welcome.pack(fill="x", padx=150, pady=(10, 6))

        tk.Label(
            welcome,
            text="Bienvenue dans PageMaître",
            bg="#F8F4EC",
            fg="#173B6C",
            font=("Segoe UI", 24, "bold"),
            anchor="w",
        ).pack(anchor="w")

        tagline = tk.Frame(welcome, bg="#F8F4EC")
        tagline.pack(anchor="w", pady=(4, 8))

        for text, color in (
            ("Concevez,", "#3FA47D"),
            (" organisez,", "#8D70C7"),
            (" publiez", "#F06F55"),
        ):
            tk.Label(
                tagline,
                text=text,
                bg="#F8F4EC",
                fg=color,
                font=("Segoe UI", 13, "bold"),
            ).pack(side="left")

        tk.Label(
            welcome,
            text=(
                "Commencez un ouvrage, reprenez votre dernier projet "
                "ou rejoignez directement le bureau dont vous avez besoin."
            ),
            bg="#F8F4EC",
            fg=theme.MUTED,
            font=("Segoe UI", 9),
            anchor="w",
        ).pack(anchor="w")

        grid = tk.Canvas(
            content,
            bg="#F6F2EA",
            highlightthickness=0,
            bd=0,
        )
        grid.pack(fill="both", expand=True, padx=24, pady=(4, 8))
        grid.grid_columnconfigure(0, weight=1, uniform="home")
        grid.grid_columnconfigure(1, weight=1, uniform="home")
        grid.grid_rowconfigure(0, weight=1)
        grid.grid_rowconfigure(1, weight=1)
        grid.bind(
            "<Configure>",
            lambda _event: paint_layer(grid, "grid"),
            add="+",
        )


        # ----------------------------------------------------------
        # ACCUEIL : objets posés directement sur les décors.
        # Aucun conteneur technique visible n'est utilisé ici.
        # ----------------------------------------------------------
        def home_round_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
            r = max(1, min(radius, (x2 - x1) / 2, (y2 - y1) / 2))
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

        # PM_VISUAL_REFERENCE_V1
        def home_command_button(
            canvas,
            *,
            tag: str,
            text: str,
            cx: float,
            cy: float,
            color: str,
            min_width: int = 92,
            height: int = 36,
        ):
            """Bouton de commande : relief doux + brillance verre légère."""
            if not hasattr(self, "_home_interaction_state"):
                self._home_interaction_state = {}

            state = self._home_interaction_state.get(tag, "normal")
            width = max(min_width, int(len(text) * 7.0) + 34)

            press = 1 if state == "pressed" else 0
            shadow_offset = 2 if state == "pressed" else (4 if state == "hover" else 3)

            x1 = cx - width / 2
            x2 = cx + width / 2
            y1 = cy - height / 2 + press
            y2 = cy + height / 2 + press

            shadow = self._mix(
                color,
                "#56615A",
                0.28 if state == "hover" else 0.34,
            )
            rim = self._mix(
                color,
                "#536158",
                0.20 if state != "pressed" else 0.30,
            )
            face_mix = {
                "normal": 0.82,
                "hover": 0.76,
                "pressed": 0.86,
            }.get(state, 0.82)
            face = self._mix(color, "#FFFFFF", face_mix)
            shine = self._mix(color, "#FFFFFF", 0.97)
            ink = self._mix(color, "#273229", 0.58)

            home_round_rect(
                canvas,
                x1 + 1, y1 + shadow_offset,
                x2 + 1, y2 + shadow_offset,
                12,
                fill=shadow,
                outline="",
                tags=(tag, "home_button"),
            )
            home_round_rect(
                canvas,
                x1, y1, x2, y2,
                12,
                fill=rim,
                outline="",
                tags=(tag, "home_button"),
            )
            home_round_rect(
                canvas,
                x1 + 1, y1 + 1,
                x2 - 1, y2 - 1,
                11,
                fill=face,
                outline="",
                tags=(tag, "home_button"),
            )

            canvas.create_line(
                x1 + 14, y1 + 4,
                x2 - 14, y1 + 4,
                fill=shine,
                width=2 if state == "hover" else 1,
                tags=(tag, "home_button"),
            )
            canvas.create_line(
                x1 + 18, y1 + 7,
                x2 - 18, y1 + 7,
                fill=self._mix(face, "#FFFFFF", 0.60),
                width=1,
                tags=(tag, "home_button"),
            )

            canvas.create_text(
                cx,
                cy - 1 + press,
                text=text,
                fill=ink,
                font=("Segoe UI", 9, "bold"),
                anchor="center",
                tags=(tag, "home_button"),
            )
            return x1, y1, x2, y2


        def home_choice_panel(
            canvas,
            *,
            tag: str,
            x1: float,
            y1: float,
            x2: float,
            y2: float,
            color: str,
            selected: bool = False,
        ):
            """Zone de choix : carte éditoriale satinée, distincte d'un bouton."""
            if not hasattr(self, "_home_interaction_state"):
                self._home_interaction_state = {}

            state = self._home_interaction_state.get(tag, "normal")
            pressed = state == "pressed"
            hover = state == "hover"

            lift = 1 if pressed else 0
            shadow_offset = 2 if pressed else (4 if hover else 3)

            base_mix = 0.90
            if hover:
                base_mix = 0.85
            if pressed:
                base_mix = 0.88
            if selected:
                base_mix -= 0.07

            face = self._mix(color, "#FFFFFF", max(0.72, base_mix))
            shadow = self._mix(color, "#77796F", 0.60 if hover else 0.66)
            outline = color if selected else self._mix(color, "#FFFFFF", 0.28)
            inner = self._mix(color, "#FFFFFF", 0.78)
            satin = self._mix(color, "#FFFFFF", 0.96)
            fiber = self._mix(color, "#E7DED2", 0.94)

            y1 += lift
            y2 += lift

            home_round_rect(
                canvas,
                x1 + 2, y1 + shadow_offset,
                x2 + 2, y2 + shadow_offset,
                14,
                fill=shadow,
                outline="",
                tags=(tag, "home_choice"),
            )
            home_round_rect(
                canvas,
                x1, y1, x2, y2,
                14,
                fill=face,
                outline=outline,
                width=2 if selected else 1,
                tags=(tag, "home_choice"),
            )
            home_round_rect(
                canvas,
                x1 + 3, y1 + 3,
                x2 - 3, y2 - 3,
                11,
                fill="",
                outline=inner,
                width=1,
                tags=(tag, "home_choice"),
            )
            canvas.create_line(
                x1 + 18, y1 + 5,
                x2 - 18, y1 + 5,
                fill=satin,
                width=2,
                tags=(tag, "home_choice"),
            )

            h = y2 - y1
            for ratio in (0.30, 0.55, 0.79):
                yy = y1 + h * ratio
                canvas.create_line(
                    x1 + 12, yy,
                    x2 - 12, yy,
                    fill=fiber,
                    width=1,
                    dash=(1, 6),
                    tags=(tag, "home_choice"),
                )

            return lift

        def home_chip(canvas, *, x, y, text, bg, fg, tag):
            """Capsule informative : jamais traitée comme un bouton."""
            width = max(64, int(len(text) * 5.0) + 29)
            height = 20

            home_round_rect(
                canvas,
                x, y,
                x + width, y + height,
                height / 2,
                fill=bg,
                outline=self._mix(bg, "#FFFFFF", 0.35),
                width=1,
                tags=tag,
            )
            canvas.create_line(
                x + 13, y + 3,
                x + width - 10, y + 3,
                fill=self._mix(bg, "#FFFFFF", 0.72),
                width=1,
                tags=tag,
            )
            canvas.create_oval(
                x + 8, y + 7,
                x + 14, y + 13,
                fill=fg,
                outline="",
                tags=tag,
            )
            canvas.create_text(
                x + 19,
                y + height / 2,
                text=text,
                fill=fg,
                font=("Segoe UI", 7),
                anchor="w",
                tags=tag,
            )
            return width


        def home_shortcut_button(
            canvas,
            *,
            tag,
            x1,
            y1,
            x2,
            y2,
            title,
            subtitle,
            color,
        ):
            """Grand bouton raccourci : même famille verre que les commandes."""
            if not hasattr(self, "_home_interaction_state"):
                self._home_interaction_state = {}

            state = self._home_interaction_state.get(tag, "normal")
            press = 1 if state == "pressed" else 0
            shadow_offset = 2 if state == "pressed" else (4 if state == "hover" else 3)

            face_mix = {
                "normal": 0.91,
                "hover": 0.84,
                "pressed": 0.89,
            }.get(state, 0.91)

            y1 += press
            y2 += press
            face = self._mix(color, "#FFFFFF", face_mix)
            shadow = self._mix(color, "#73776F", 0.64)
            rim = self._mix(color, "#FFFFFF", 0.25)

            home_round_rect(
                canvas,
                x1 + 1, y1 + shadow_offset,
                x2 + 1, y2 + shadow_offset,
                12,
                fill=shadow,
                outline="",
                tags=("home_shortcuts", tag),
            )
            home_round_rect(
                canvas,
                x1, y1, x2, y2,
                12,
                fill=face,
                outline=color,
                width=1,
                tags=("home_shortcuts", tag),
            )
            home_round_rect(
                canvas,
                x1 + 3, y1 + 3,
                x2 - 3, y2 - 3,
                9,
                fill="",
                outline=rim,
                width=1,
                tags=("home_shortcuts", tag),
            )
            canvas.create_line(
                x1 + 12, y1 + 4,
                x2 - 12, y1 + 4,
                fill=self._mix(color, "#FFFFFF", 0.96),
                width=2,
                tags=("home_shortcuts", tag),
            )

            canvas.create_text(
                x1 + 10, y1 + 15,
                text=title,
                fill=theme.INK,
                font=("Segoe UI", 8, "bold"),
                anchor="w",
                tags=("home_shortcuts", tag),
            )
            canvas.create_text(
                x1 + 10, y1 + 36,
                text=subtitle,
                fill="#485664",
                font=("Segoe UI", 7),
                anchor="w",
                tags=("home_shortcuts", tag),
            )


        def home_hover_cursor(
            canvas,
            tag,
            *,
            redraw=None,
            action=None,
        ):
            """Rend une zone réellement interactive, même sans action métier."""
            if not hasattr(self, "_home_interaction_state"):
                self._home_interaction_state = {}

            def schedule_redraw():
                if redraw is not None:
                    canvas.after_idle(redraw)

            def enter(_event=None):
                if self._home_interaction_state.get(tag) != "hover":
                    self._home_interaction_state[tag] = "hover"
                    self.configure(cursor="hand2")
                    schedule_redraw()

            def leave(_event=None):
                if self._home_interaction_state.get(tag) != "normal":
                    self._home_interaction_state[tag] = "normal"
                    self.configure(cursor="arrow")
                    schedule_redraw()

            def press(_event=None):
                self._home_interaction_state[tag] = "pressed"
                self.configure(cursor="hand2")
                schedule_redraw()

            def release(_event=None):
                self._home_interaction_state[tag] = "hover"
                self.configure(cursor="hand2")
                if action is not None:
                    action()
                schedule_redraw()

            canvas.tag_bind(tag, "<Enter>", enter)
            canvas.tag_bind(tag, "<Leave>", leave)
            canvas.tag_bind(tag, "<ButtonPress-1>", press)
            canvas.tag_bind(tag, "<ButtonRelease-1>", release)

        def get_project_type_photo(key: str, icon_path: Path):
            photo = self._project_type_images.get(key)
            if photo is not None:
                return photo
            try:
                image = Image.open(icon_path).convert("RGBA")
                image.thumbnail((60, 60), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(image)
                self._project_type_images[key] = photo
                return photo
            except Exception:
                return None

        def get_open_project_types_photo():
            photo = getattr(self, "_open_project_types_photo", None)
            if photo is not None:
                return photo

            specs = (
                (
                    PROJECT_ROOT / "assets" / "gui_v2" / "project_type_icons"
                    / "ouvrage_structure" / "ouvrage_structure_64px.png",
                    (8, 17),
                    54,
                ),
                (
                    PROJECT_ROOT / "assets" / "gui_v2" / "project_type_icons"
                    / "livre_textuel" / "livre_textuel_64px.png",
                    (29, 4),
                    60,
                ),
                (
                    PROJECT_ROOT / "assets" / "gui_v2" / "project_type_icons"
                    / "bande_dessinee" / "bande_dessinee_64px.png",
                    (50, 18),
                    54,
                ),
            )

            try:
                composite = Image.new("RGBA", (112, 80), (0, 0, 0, 0))
                for icon_path, (x, y), size in specs:
                    icon = Image.open(icon_path).convert("RGBA")
                    icon.thumbnail((size, size), Image.Resampling.LANCZOS)
                    composite.alpha_composite(icon, (x, y))

                self._open_project_types_photo = ImageTk.PhotoImage(composite)
                return self._open_project_types_photo
            except Exception:
                return None

        def get_recent_document_photo():
            if getattr(self, "_home_recent_document_photo", None) is not None:
                return self._home_recent_document_photo
            try:
                image = Image.open(
                    PROJECT_ROOT
                    / "assets"
                    / "gui_v2"
                    / "accueil_icons"
                    / "recent_document_64px.png"
                ).convert("RGBA")
                image.thumbnail((48, 48), Image.Resampling.LANCZOS)
                self._home_recent_document_photo = ImageTk.PhotoImage(image)
                return self._home_recent_document_photo
            except Exception:
                return None



        def get_recent_document_photo():
            if getattr(self, "_home_recent_document_photo", None) is not None:
                return self._home_recent_document_photo
            try:
                image = Image.open(
                    PROJECT_ROOT
                    / "assets"
                    / "gui_v2"
                    / "accueil_icons"
                    / "recent_document_64px.png"
                ).convert("RGBA")
                image.thumbnail((48, 48), Image.Resampling.LANCZOS)
                self._home_recent_document_photo = ImageTk.PhotoImage(image)
                return self._home_recent_document_photo
            except Exception:
                return None

        # ---- Créer un nouveau projet
        create_card = self._rounded_home_card(
            grid,
            title="Créer un nouveau projet",
            accent="#75B89E",
            bg="#F5FBF8",
        
                          background_path=Path(__file__).resolve().parents[2] / "assets" / "gui_v2" / "accueil_backgrounds" / "01_creer_un_nouveau_projet" / "01_creer_un_nouveau_projet.png",
                          subtitle='Choisissez le type d’ouvrage que vous souhaitez créer.',)
        create_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 7),
            pady=(0, 7),
        )

        def render_create_content(_event=None):
            canvas = create_card

            # Important : les cartes de choix satinées doivent être supprimées
            # avant chaque redraw, sinon elles s'empilent au survol.
            canvas.delete("home_choice")
            canvas.delete("home_create")
            canvas.delete("create_project_button")

            width = max(canvas.winfo_width(), 420)
            height = max(canvas.winfo_height(), 220)

            margin = 18
            gap = 10
            y1 = 72
            y2 = max(y1 + 92, height - 58)
            button_w = (width - margin * 2 - gap * 2) / 3
            info_color = "#4F5B67"

            project_types = (
                (
                    "ouvrage_structure",
                    "Ouvrage structuré",
                    "Fiches guides, catalogues,\nouvrages organisés",
                    "#6AB08F",
                    PROJECT_ROOT / "assets" / "gui_v2" / "project_type_icons"
                    / "ouvrage_structure" / "ouvrage_structure_64px.png",
                ),
                (
                    "livre_textuel",
                    "Livre textuel",
                    "Roman, récit, essai,\nbiographie",
                    "#A888D2",
                    PROJECT_ROOT / "assets" / "gui_v2" / "project_type_icons"
                    / "livre_textuel" / "livre_textuel_64px.png",
                ),
                (
                    "bande_dessinee",
                    "Bande dessinée",
                    "Planches, cases, bulles,\nnarration visuelle",
                    "#F07D63",
                    PROJECT_ROOT / "assets" / "gui_v2" / "project_type_icons"
                    / "bande_dessinee" / "bande_dessinee_64px.png",
                ),
            )

            for index, (key, title, sub, color, icon_path) in enumerate(project_types):
                x1 = margin + index * (button_w + gap)
                x2 = x1 + button_w
                tag = f"ptype_{key}"
                selected = key == self._selected_project_type

                lift = home_choice_panel(
                    canvas,
                    tag=tag,
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2,
                    color=color,
                    selected=selected,
                )

                seal_y = y1 + 15 + lift
                canvas.create_oval(
                    x1 + 10, seal_y - 6,
                    x1 + 22, seal_y + 6,
                    fill=self._mix(color, "#FFFFFF", 0.88),
                    outline=color,
                    width=1.2,
                    tags=("home_create", tag),
                )
                if selected:
                    canvas.create_oval(
                        x1 + 13, seal_y - 3,
                        x1 + 19, seal_y + 3,
                        fill=color,
                        outline="",
                        tags=("home_create", tag),
                    )

                photo = get_project_type_photo(key, icon_path)
                icon_y = y1 + 38 + lift
                if photo is not None:
                    canvas.create_image(
                        (x1 + x2) / 2,
                        icon_y,
                        image=photo,
                        anchor="center",
                        tags=("home_create", tag),
                    )

                canvas.create_text(
                    (x1 + x2) / 2,
                    y2 - 37 + lift,
                    text=title,
                    fill=color,
                    font=("Segoe UI", 8, "bold"),
                    anchor="center",
                    tags=("home_create", tag),
                )
                canvas.create_text(
                    (x1 + x2) / 2,
                    y2 - 17 + lift,
                    text=sub,
                    fill=info_color,
                    font=("Segoe UI", 7),
                    justify="center",
                    anchor="center",
                    tags=("home_create", tag),
                )

                def choose(chosen=key):
                    self._selected_project_type = chosen

                home_hover_cursor(
                    canvas,
                    tag,
                    redraw=render_create_content,
                    action=choose,
                )

            command_y = height - 25
            home_command_button(
                canvas,
                tag="create_project_button",
                text="Créer un projet",
                cx=width / 2,
                cy=command_y,
                color="#86A978",
                min_width=112,
                height=34,
            )
            home_hover_cursor(
                canvas,
                "create_project_button",
                redraw=render_create_content,
                action=lambda: None,
            )


        create_card.bind(
            "<Configure>",
            lambda _event: create_card.after_idle(render_create_content),
            add="+",
        )
        create_card.after_idle(render_create_content)

        # ---- Ouvrir un projet
        open_card = self._rounded_home_card(
            grid,
            title="Ouvrir un projet",
            accent="#A68BD0",
            bg="#FAF7FD",
        
                        background_path=Path(__file__).resolve().parents[2] / "assets" / "gui_v2" / "accueil_backgrounds" / "02_ouvrir_un_projet" / "02_ouvrir_un_projet.png",)
        open_card.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(7, 0),
            pady=(0, 7),
        )

        def render_open_content(_event=None):
            canvas = open_card
            canvas.delete("home_open")
            canvas.delete("open_project_button")
            width = max(canvas.winfo_width(), 420)
            height = max(canvas.winfo_height(), 220)

            icon_x = max(110, width * 0.30)
            icon_y = height * 0.53
            text_x = width * 0.43

            # Icône composée avec les trois types réels de projet.
            photo = get_open_project_types_photo()
            if photo is not None:
                canvas.create_image(
                    icon_x,
                    icon_y - 1,
                    image=photo,
                    anchor="center",
                    tags="home_open",
                )

            canvas.create_text(
                text_x,
                icon_y - 26,
                text=(
                    "Accédez à un projet existant, même s’il ne figure pas\n"
                    "parmi les projets récents."
                ),
                fill="#45515D",
                font=("Segoe UI", 9),
                justify="left",
                anchor="nw",
                tags="home_open",
            )

            home_command_button(
                canvas,
                tag="open_project_button",
                text="Ouvrir",
                cx=text_x + 48,
                cy=icon_y + 38,
                color="#8F6BC6",
                min_width=92,
                height=34,
            )
            home_hover_cursor(
                canvas,
                "open_project_button",
                redraw=render_open_content,
                action=lambda: None,
            )


        open_card.bind(
            "<Configure>",
            lambda _event: open_card.after_idle(render_open_content),
            add="+",
        )
        open_card.after_idle(render_open_content)

        # ---- Reprendre votre travail
        recent_card = self._rounded_home_card(
            grid,
            title="Reprendre votre travail",
            accent="#7DBBA4",
            bg="#FBFCFA",
            title_align="center",
            title_color=theme.INK,
        
                          background_path=Path(__file__).resolve().parents[2] / "assets" / "gui_v2" / "accueil_backgrounds" / "03_reprendre_votre_travail" / "03_reprendre_votre_travail.png",
                          subtitle='Dernier projet actif et projets ouverts récemment.',)
        recent_card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(0, 9),
            pady=(9, 0),
        )

        def render_recent_content(_event=None):
            canvas = recent_card
            canvas.delete("home_recent")
            canvas.delete("resume_project_button")
            canvas.delete("recent_project_row")
            canvas.delete("recent_secondary_row")
            width = max(canvas.winfo_width(), 420)
            height = max(canvas.winfo_height(), 220)

            icon_x = 37
            top_y = 82
            text_x = 67
            meta_color = "#4D5965"

            # Le projet récent est une information :
            # seul le bouton "Reprendre" est interactif.
            photo = get_recent_document_photo()
            if photo is not None:
                canvas.create_image(
                    icon_x,
                    top_y + 3,
                    image=photo,
                    anchor="center",
                    tags="home_recent",
                )

            canvas.create_text(
                text_x,
                top_y - 15,
                text="projet x",
                fill=theme.INK,
                font=("Segoe UI", 10, "bold"),
                anchor="nw",
                tags="home_recent",
            )
            canvas.create_text(
                text_x,
                top_y + 6,
                text="Aucune page créée   ·   10/08/2026 15:23",
                fill=meta_color,
                font=("Segoe UI", 8),
                anchor="nw",
                tags="home_recent",
            )

            chip_y = top_y + 30
            chip_x = text_x

            chip_x += home_chip(
                canvas,
                x=chip_x, y=chip_y,
                text="Ouvrage structuré",
                bg="#E5F3EC",
                fg="#398360",
                tag="home_recent",
            ) + 5
            chip_x += home_chip(
                canvas,
                x=chip_x, y=chip_y,
                text="En cours",
                bg="#EDF5EF",
                fg="#398360",
                tag="home_recent",
            ) + 5
            home_chip(
                canvas,
                x=chip_x, y=chip_y,
                text="Dernier bureau : Maquettage",
                bg="#F1EFF7",
                fg="#5F4A80",
                tag="home_recent",
            )

            home_command_button(
                canvas,
                tag="resume_project_button",
                text="Reprendre",
                cx=width - 67,
                cy=top_y + 7,
                color="#86A978",
                min_width=94,
                height=34,
            )
            home_hover_cursor(
                canvas,
                "resume_project_button",
                redraw=render_recent_content,
                action=lambda: None,
            )

            separator_y = min(height - 55, top_y + 70)
            canvas.create_line(
                22, separator_y,
                width - 22, separator_y,
                fill=self._mix("#7DBBA4", "#FFFFFF", 0.48),
                width=1,
                tags="home_recent",
            )

            canvas.create_text(
                31,
                separator_y + 19,
                text="▦  nouveau 1",
                fill=theme.INK,
                font=("Segoe UI", 8, "bold"),
                anchor="w",
                tags="home_recent",
            )
            canvas.create_text(
                width - 26,
                separator_y + 19,
                text="Structuré     En cours     0 p.     07/08/2026 16:09",
                fill=meta_color,
                font=("Segoe UI", 8),
                anchor="e",
                tags="home_recent",
            )


        recent_card.bind(
            "<Configure>",
            lambda _event: recent_card.after_idle(render_recent_content),
            add="+",
        )
        recent_card.after_idle(render_recent_content)

        # ---- Repères et accès directs
        shortcuts = self._rounded_home_card(
            grid,
            title="Repères & accès directs",
            accent="#9B7BCB",
            bg="#FBFAFD",
            title_align="center",
            title_color=theme.INK,
        
                        background_path=Path(__file__).resolve().parents[2] / "assets" / "gui_v2" / "accueil_backgrounds" / "04_reperes_et_acces_directs" / "04_reperes_et_acces_directs.png",
                        subtitle='Raccourcis du dernier projet actif.',)
        shortcuts.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(7, 0),
            pady=(7, 0),
        )

        def render_shortcuts_content(_event=None):
            canvas = shortcuts
            canvas.delete("home_shortcuts")
            width = max(canvas.winfo_width(), 420)
            height = max(canvas.winfo_height(), 220)

            margin = 18
            gap = 8
            y1 = 72
            y2 = min(132, max(118, height * 0.56))
            button_w = (width - margin * 2 - gap * 3) / 4

            shortcut_data = (
                ("Maquettage", "Organiser les pages", "#64AEE0", "shortcut_maquettage"),
                ("Atelier", "Préparer les gabarits", "#6DB99D", "shortcut_atelier"),
                ("Conception", "Créer les pages", "#9B7BCB", "shortcut_conception"),
                ("Centre du projet", "Vue d’ensemble", "#F07D63", "shortcut_centre"),
            )

            for index, (title, sub, color, tag) in enumerate(shortcut_data):
                x1 = margin + index * (button_w + gap)
                x2 = x1 + button_w

                home_shortcut_button(
                    canvas,
                    tag=tag,
                    x1=x1,
                    y1=y1,
                    x2=x2,
                    y2=y2,
                    title=title,
                    subtitle=sub,
                    color=color,
                )
                home_hover_cursor(
                    canvas,
                    tag,
                    redraw=render_shortcuts_content,
                    action=lambda: None,
                )

            status_y = max(y2 + 30, height - 46)
            columns = (
                ("État", "En cours", "#317956"),
                ("Étape actuelle", "Maquettage", "#594184"),
                ("Dernière activité", "10/08/2026 15:23", "#2F668C"),
            )
            usable = width - 40
            col_w = usable / 3

            for index, (title, value, color) in enumerate(columns):
                x = 20 + index * col_w
                canvas.create_text(
                    x,
                    status_y,
                    text=title,
                    fill=theme.INK,
                    font=("Segoe UI", 8, "bold"),
                    anchor="nw",
                    tags="home_shortcuts",
                )
                canvas.create_text(
                    x,
                    status_y + 18,
                    text=value,
                    fill=color,
                    font=("Segoe UI", 8, "bold"),
                    anchor="nw",
                    tags="home_shortcuts",
                )

                if index < 2:
                    sep_x = x + col_w - 12
                    canvas.create_line(
                        sep_x, status_y - 2,
                        sep_x, status_y + 30,
                        fill=self._mix("#9B7BCB", "#FFFFFF", 0.62),
                        tags="home_shortcuts",
                    )


        shortcuts.bind(
            "<Configure>",
            lambda _event: shortcuts.after_idle(render_shortcuts_content),
            add="+",
        )
        shortcuts.after_idle(render_shortcuts_content)

        # Bas de prévisualisation.
        footer = tk.Frame(
            content,
            bg="#F7F6F2",
            height=24,
            highlightthickness=1,
            highlightbackground="#E4E2DD",
        )
        footer.pack(fill="x", side="bottom")
        footer.pack_propagate(False)

        tk.Label(
            footer,
            text="PageMaître V2 (interface de prévisualisation)",
            bg="#F7F6F2",
            fg=theme.MUTED,
            font=("Segoe UI", 8),
        ).pack(side="left", padx=14)

        tk.Label(
            footer,
            text="ⓘ  Les fonctions sont désactivées dans cette version.",
            bg="#F7F6F2",
            fg=theme.MUTED,
            font=("Segoe UI", 8),
        ).pack(side="left", padx=22)

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
        self._screen_header(
            parent,
            "Maquettage",
            "1 Structurer   •   2 Visualiser   •   3 Remplir",
            theme.LILAC,
        )

        skeleton = self._card(
            parent,
            "1 — Structurer le livre",
            "Début du livre, parties numérotées, groupes libres et fin du livre.",
            accent=theme.LILAC,
            width=900,
            height=145,
        )
        skeleton.pack(fill="x", padx=22, pady=6)

        ribbon = tk.Canvas(
            skeleton,
            bg=theme.PANEL,
            height=65,
            highlightthickness=0,
        )
        ribbon.pack(fill="x", padx=14, pady=5)

        names = ("Début", "Partie 1", "Annexe", "Partie 2", "Partie 3", "Fin")
        x = 14
        for index, name in enumerate(names):
            color = (
                theme.SKY,
                theme.LILAC,
                theme.CELADON,
                theme.CORAL,
            )[index % 4]
            ribbon.create_rectangle(
                x, 8, x + 125, 55,
                fill="#F6F4F1",
                outline=color,
                width=2,
            )
            ribbon.create_text(
                x + 62,
                31,
                text=name,
                fill=theme.INK,
                font=("Segoe UI", 9, "bold"),
            )
            x += 136

        global_view = self._card(
            parent,
            "2 — Vue globale",
            "Vision métro de la structure et navigation entre groupes.",
            accent=theme.CELADON,
            width=900,
            height=125,
        )
        global_view.pack(fill="x", padx=22, pady=6)

        composition = tk.Frame(parent, bg=theme.WINDOW)
        composition.pack(fill="both", expand=True, padx=22, pady=6)

        left = self._card(
            composition,
            "Types de page",
            "Choix du type, quantité et informations de suivi.",
            accent=theme.SKY,
            width=255,
            height=260,
        )
        left.pack(side="left", fill="y", padx=(0, 6))

        for label in (
            "Couverture",
            "Page de titre",
            "Sommaire",
            "Page standard",
            "Page blanche",
            "Nouveau type",
        ):
            self._disabled_button(left, label).pack(
                fill="x", padx=12, pady=3
            )

        middle = self._card(
            composition,
            "3 — Composition du groupe",
            "Zone centrale destinée à la séquence des pages du groupe sélectionné.",
            accent=theme.INK,
            width=560,
            height=260,
        )
        middle.pack(side="left", fill="both", expand=True, padx=6)

        pages = tk.Frame(middle, bg=theme.PANEL)
        pages.pack(fill="both", expand=True, padx=12, pady=6)
        for index in range(1, 7):
            page = tk.Frame(
                pages,
                bg=theme.WHITE,
                width=62,
                height=88,
                highlightthickness=1,
                highlightbackground=theme.BORDER,
            )
            page.pack(side="left", padx=6, pady=8)
            page.pack_propagate(False)
            tk.Label(
                page,
                text=str(index),
                bg=theme.WHITE,
                fg=theme.MUTED,
                font=("Segoe UI", 8),
            ).pack(side="bottom", pady=5)

        right = self._card(
            composition,
            "Outils",
            "Commandes présentes mais inactives dans le clone.",
            accent=theme.CORAL,
            width=220,
            height=260,
        )
        right.pack(side="left", fill="y", padx=(6, 0))

        for label in ("Monter", "Descendre", "Dupliquer", "Supprimer", "Règles"):
            self._disabled_button(right, label).pack(
                fill="x", padx=12, pady=4
            )

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
