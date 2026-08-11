from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import ttk

from PIL import Image, ImageTk

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
            height=126,
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
        height = 126
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
            y=68,
            enabled=getattr(self, "_active", "accueil") != "accueil",
            command=self.open_visualisation_window,
        )
        self._draw_side_canvas_item(
            key="suivi_du_livre",
            label="Suivi du livre",
            x=168,
            y=68,
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
                y=55,
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
            y=66,
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
        canvas.configure(cursor=cursor)

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
                        y=55,
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
        self.header.configure(cursor="arrow")
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
            image = image.resize((1600, 126), Image.Resampling.LANCZOS)
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

        # ---- Créer un nouveau projet
        create_card = self._home_card(
            grid,
            title="Créer un nouveau projet",
            accent="#75B89E",
            bg="#F5FBF8",
        )
        create_card.grid(
            row=0,
            column=0,
            sticky="nsew",
            padx=(0, 7),
            pady=(0, 7),
        )

        tk.Label(
            create_card,
            text="Choisissez le type d’ouvrage que vous souhaitez créer.",
            bg="#F5FBF8",
            fg=theme.MUTED,
            font=("Segoe UI", 8),
        ).pack(pady=(0, 12))

        type_row = tk.Frame(create_card, bg="#F5FBF8")
        type_row.pack(fill="x", padx=18)

        self._project_type_card(
            type_row,
            key="ouvrage_structure",
            title="Ouvrage structuré",
            subtitle="Fiches guides, catalogues,\nouvrages organisés",
            color="#6AB08F",
            icon_path=(
                PROJECT_ROOT / "assets" / "gui_v2" / "project_type_icons"
                / "ouvrage_structure" / "ouvrage_structure_64px.png"
            ),
        ).pack(side="left", fill="both", expand=True, padx=(0, 5))

        self._project_type_card(
            type_row,
            key="livre_textuel",
            title="Livre textuel",
            subtitle="Roman, récit, essai,\nbiographie",
            color="#A888D2",
            icon_path=(
                PROJECT_ROOT / "assets" / "gui_v2" / "project_type_icons"
                / "livre_textuel" / "livre_textuel_64px.png"
            ),
        ).pack(side="left", fill="both", expand=True, padx=5)

        self._project_type_card(
            type_row,
            key="bande_dessinee",
            title="Bande dessinée",
            subtitle="Planches, cases, bulles,\nnarration visuelle",
            color="#F07D63",
            icon_path=(
                PROJECT_ROOT / "assets" / "gui_v2" / "project_type_icons"
                / "bande_dessinee" / "bande_dessinee_64px.png"
            ),
        ).pack(side="left", fill="both", expand=True, padx=(5, 0))

        PMCommandButton(
            create_card,
            text="Créer un projet",
            color="green",
            size="md",
            icon=None,
            width=122,
            command=None,
        ).pack(pady=13)

        # ---- Ouvrir un projet
        open_card = self._home_card(
            grid,
            title="Ouvrir un projet",
            accent="#A68BD0",
            bg="#FAF7FD",
        )
        open_card.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=(7, 0),
            pady=(0, 7),
        )

        open_body = tk.Frame(open_card, bg="#FAF7FD")
        open_body.pack(fill="both", expand=True, padx=40, pady=(10, 20))
        open_body.grid_columnconfigure(0, weight=1)
        open_body.grid_columnconfigure(1, weight=2)

        folder = tk.Label(
            open_body,
            text="▱\n▱\n▰",
            bg="#FAF7FD",
            fg="#8C6DC5",
            font=("Segoe UI Symbol", 28, "bold"),
            justify="center",
        )
        folder.grid(row=0, column=0, rowspan=2, sticky="e", padx=(0, 25))

        tk.Label(
            open_body,
            text=(
                "Accédez à un projet existant, même s’il ne figure pas\n"
                "encore parmi les projets récents."
            ),
            bg="#FAF7FD",
            fg=theme.INK,
            font=("Segoe UI", 9),
            justify="left",
            anchor="w",
        ).grid(row=0, column=1, sticky="sw", pady=(10, 8))

        self._soft_button(
            open_body,
            "▢  Ouvrir",
            "#8F6BC6",
        ).grid(row=1, column=1, sticky="nw")

        # ---- Reprendre votre travail
        recent_card = self._home_card(
            grid,
            title="Reprendre votre travail",
            accent="#7DBBA4",
            bg="#FBFCFA",
            title_align="left",
        )
        recent_card.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=(0, 7),
            pady=(7, 0),
        )

        tk.Label(
            recent_card,
            text="Dernier projet actif et projets ouverts récemment.",
            bg="#FBFCFA",
            fg=theme.MUTED,
            font=("Segoe UI", 8),
            anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 8))

        project = tk.Frame(
            recent_card,
            bg="#FFFFFF",
            highlightthickness=1,
            highlightbackground="#83BFA9",
        )
        project.pack(fill="x", padx=14, pady=(0, 8))

        tk.Label(
            project,
            text="▭",
            bg="#FFFFFF",
            fg="#69AEE0",
            font=("Segoe UI Symbol", 30),
            width=4,
        ).pack(side="left", padx=(10, 0), pady=9)

        details = tk.Frame(project, bg="#FFFFFF")
        details.pack(side="left", fill="both", expand=True, padx=7, pady=10)

        tk.Label(
            details,
            text="projet x",
            bg="#FFFFFF",
            fg=theme.INK,
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        ).pack(anchor="w")

        tk.Label(
            details,
            text="Aucune page créée   ·   10/08/2026 15:23",
            bg="#FFFFFF",
            fg=theme.MUTED,
            font=("Segoe UI", 8),
            anchor="w",
        ).pack(anchor="w", pady=(4, 5))

        chips = tk.Frame(details, bg="#FFFFFF")
        chips.pack(anchor="w")
        self._chip(chips, "Ouvrage structuré", "#E5F3EC", "#4C9E7B")
        self._chip(chips, "En cours", "#EDF5EF", "#4C9E7B")
        self._chip(
            chips,
            "Dernier bureau : Maquettage",
            "#F2F1F6",
            theme.INK,
        )

        self._soft_button(
            project,
            "↗\nReprendre",
            "#6FB293",
            compact=True,
        ).pack(side="right", padx=10, pady=10)

        small = tk.Frame(
            recent_card,
            bg="#FFFFFF",
            highlightthickness=1,
            highlightbackground=theme.BORDER,
        )
        small.pack(fill="x", padx=14, pady=(0, 10))

        tk.Label(
            small,
            text="▦   nouveau 1",
            bg="#FFFFFF",
            fg=theme.INK,
            font=("Segoe UI", 8, "bold"),
            anchor="w",
        ).pack(side="left", padx=12, pady=8)

        tk.Label(
            small,
            text="Structuré     En cours     0 p.     07/08/2026 16:09",
            bg="#FFFFFF",
            fg=theme.MUTED,
            font=("Segoe UI", 8),
        ).pack(side="right", padx=12)

        # ---- Repères et accès directs
        shortcuts = self._home_card(
            grid,
            title="Repères & accès directs",
            accent="#9B7BCB",
            bg="#FBFAFD",
            title_align="left",
        )
        shortcuts.grid(
            row=1,
            column=1,
            sticky="nsew",
            padx=(7, 0),
            pady=(7, 0),
        )

        tk.Label(
            shortcuts,
            text="Raccourcis du dernier projet actif.",
            bg="#FBFAFD",
            fg=theme.MUTED,
            font=("Segoe UI", 8),
            anchor="w",
        ).pack(fill="x", padx=16, pady=(0, 8))

        shortcuts_row = tk.Frame(shortcuts, bg="#FBFAFD")
        shortcuts_row.pack(fill="x", padx=14, pady=(0, 8))

        for text, sub, color in (
            ("Maquettage", "Organiser les pages", "#64AEE0"),
            ("Atelier", "Préparer les gabarits", "#6DB99D"),
            ("Conception", "Créer les pages", "#9B7BCB"),
            ("Centre du projet", "Vue d’ensemble", "#F07D63"),
        ):
            self._shortcut_box(
                shortcuts_row,
                text,
                sub,
                color,
            ).pack(
                side="left",
                fill="both",
                expand=True,
                padx=4,
            )

        status = tk.Frame(
            shortcuts,
            bg="#F5F6F6",
            highlightthickness=1,
            highlightbackground="#E2E2E0",
        )
        status.pack(fill="x", padx=14, pady=(0, 10))

        for title, value, color in (
            ("État", "En cours", "#4C9E7B"),
            ("Étape actuelle", "Maquettage", "#8D70C7"),
            ("Dernière activité", "10/08/2026 15:23", "#4C9CCB"),
        ):
            block = tk.Frame(status, bg="#F5F6F6")
            block.pack(side="left", fill="x", expand=True, padx=10, pady=8)

            tk.Label(
                block,
                text=title,
                bg="#F5F6F6",
                fg=theme.INK,
                font=("Segoe UI", 8, "bold"),
                anchor="w",
            ).pack(anchor="w")

            tk.Label(
                block,
                text=value,
                bg="#F5F6F6",
                fg=color,
                font=("Segoe UI", 8),
                anchor="w",
            ).pack(anchor="w")

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

    def _home_card(
        self,
        parent,
        *,
        title: str,
        accent: str,
        bg: str,
        title_align: str = "center",
    ) -> tk.Frame:
        card = tk.Frame(
            parent,
            bg=bg,
            highlightthickness=1,
            highlightbackground=accent,
            bd=0,
        )

        tk.Label(
            card,
            text=title,
            bg=bg,
            fg=accent if title_align == "center" else theme.INK,
            font=("Segoe UI", 12, "bold"),
            anchor="w" if title_align == "left" else "center",
        ).pack(
            fill="x",
            padx=16,
            pady=(10, 6),
        )

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
