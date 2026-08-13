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
        self._install_tomelinea_button_reactions()
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

    # TEXTE_DYNAMIQUE_ET_BOUTONS_GLOBAUX_V5
    def _install_tomelinea_button_reactions(self) -> None:
        """Réaction visuelle commune à tous les tk.Button de TomeLinea."""
        if getattr(self, "_tomelinea_button_reactions_installed", False):
            return

        self._tomelinea_button_reactions_installed = True

        def _disabled(widget):
            try:
                return str(widget.cget("state")) == "disabled"
            except Exception:
                return False

        def _remember(widget):
            data = getattr(widget, "_tomelinea_button_base", None)
            if data is not None:
                return data

            try:
                data = {
                    "bg": widget.cget("background"),
                    "fg": widget.cget("foreground"),
                    "relief": widget.cget("relief"),
                    "bd": widget.cget("borderwidth"),
                }
                widget._tomelinea_button_base = data
                return data
            except Exception:
                return None

        def _role(widget, base):
            explicit = getattr(widget, "_tomelinea_button_role", None)
            if explicit in ("primary", "secondary"):
                return explicit

            try:
                fg = str(base["fg"]).lower().replace(" ", "")
                bg = str(base["bg"]).lower().replace(" ", "")
                if fg in ("white", "#ffffff", "#fff") and bg not in (
                    "white", "#ffffff", "#fff"
                ):
                    return "primary"
            except Exception:
                pass
            return "secondary"

        def _inside(widget):
            try:
                px, py = self.winfo_pointerxy()
                return self.winfo_containing(px, py) is widget
            except Exception:
                return False

        def _normal(widget):
            base = _remember(widget)
            if base is None:
                return
            try:
                widget.configure(
                    background=base["bg"],
                    foreground=base["fg"],
                    relief=base["relief"],
                    borderwidth=base["bd"],
                )
            except Exception:
                pass

        def _hover(widget):
            if _disabled(widget):
                return
            base = _remember(widget)
            if base is None:
                return
            role = _role(widget, base)
            try:
                if role == "primary":
                    widget.configure(
                        background="#24558A",
                        foreground="#FFFFFF",
                        relief="raised",
                    )
                else:
                    widget.configure(
                        background="#F3F7FB",
                        foreground="#173E70",
                        relief="raised",
                    )
            except Exception:
                pass

        def _pressed(widget):
            if _disabled(widget):
                return
            base = _remember(widget)
            if base is None:
                return
            role = _role(widget, base)
            try:
                if role == "primary":
                    widget.configure(
                        background="#12345F",
                        foreground="#FFFFFF",
                        relief="sunken",
                    )
                else:
                    widget.configure(
                        background="#E9F0F7",
                        foreground="#173E70",
                        relief="sunken",
                    )
            except Exception:
                pass

        def on_enter(event):
            _hover(event.widget)

        def on_leave(event):
            _normal(event.widget)

        def on_press(event):
            _pressed(event.widget)

        def on_release(event):
            if _inside(event.widget):
                _hover(event.widget)
            else:
                _normal(event.widget)

        self.bind_class("Button", "<Enter>", on_enter, add="+")
        self.bind_class("Button", "<Leave>", on_leave, add="+")
        self.bind_class("Button", "<ButtonPress-1>", on_press, add="+")
        self.bind_class("Button", "<ButtonRelease-1>", on_release, add="+")

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

    # SHELL_ACCUEIL_PROJET_STABLE_V1
    def _build_shell(self) -> None:
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Pile racine : Accueil et espace Projet restent construits
        # et dimensionnés en permanence dans la même cellule.
        self.app_stack = tk.Frame(self, bg=theme.WINDOW)
        self.app_stack.grid(row=0, column=0, sticky="nsew")
        self.app_stack.grid_rowconfigure(0, weight=1)
        self.app_stack.grid_columnconfigure(0, weight=1)

        # ACCUEIL — plein écran, sans ruban.
        self.accueil_host = tk.Frame(
            self.app_stack,
            bg=theme.WINDOW,
        )
        self.accueil_host.grid(row=0, column=0, sticky="nsew")
        self.accueil_host.grid_rowconfigure(0, weight=1)
        self.accueil_host.grid_columnconfigure(0, weight=1)

        # ESPACE PROJET — ruban permanent + bureau actif.
        self.project_shell = tk.Frame(
            self.app_stack,
            bg=theme.WINDOW,
        )
        self.project_shell.grid(row=0, column=0, sticky="nsew")
        self.project_shell.grid_rowconfigure(1, weight=1)
        self.project_shell.grid_columnconfigure(0, weight=1)

        self.header = tk.Canvas(
            self.project_shell,
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

        self.project_host = tk.Frame(
            self.project_shell,
            bg=theme.WINDOW,
        )
        self.project_host.grid(row=1, column=0, sticky="nsew")
        self.project_host.grid_rowconfigure(0, weight=1)
        self.project_host.grid_columnconfigure(0, weight=1)

        # Alias conservé pour compatibilité avec les autres méthodes.
        self.host = self.project_host

        # Le ruban est préparé derrière l'Accueil avant toute navigation.
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
        # L'Accueil possède son propre conteneur plein écran.
        accueil_screen = tk.Frame(
            self.accueil_host,
            bg=theme.WINDOW,
        )
        accueil_screen.grid(row=0, column=0, sticky="nsew")
        self._screens["accueil"] = accueil_screen
        self._build_accueil(accueil_screen)

        # Les bureaux de projet partagent le même espace sous le ruban.
        builders = {
            "centre": self._build_centre,
            "maquettage": self._build_maquettage,
            "atelier": self._build_atelier,
            "conception": self._build_conception,
            "assemblage": self._build_assemblage,
            "verification": self._build_verification,
            "finalisation": self._build_finalisation,
        }

        for name, builder in builders.items():
            screen = tk.Frame(
                self.project_host,
                bg=theme.WINDOW,
            )
            screen.grid(row=0, column=0, sticky="nsew")
            self._screens[name] = screen
            builder(screen)


    # ACCES_DIRECT_REVELATION_PROPRE_V1
    def show_screen(self, name: str) -> None:
        screen = self._screens.get(name)
        if screen is None:
            return

        previous = getattr(self, "_active", None)

        if name == "accueil":
            if previous != "accueil":
                self._reset_accueil_project_selection()

            self._active = "accueil"
            self.accueil_host.tkraise()
            return

        self._active = name

        if previous != "accueil":
            screen.tkraise()
            self.project_shell.tkraise()
            self._render_header_canvas()
            return

        self.accueil_host.tkraise()

        screen.tkraise()
        self._render_header_canvas()
        self.project_shell.update_idletasks()

        target_name = name

        def _prepare_second_pass():
            if getattr(self, "_active", None) != target_name:
                return

            target = self._screens.get(target_name)
            if target is None:
                return

            target.tkraise()
            self._render_header_canvas()

            self.project_shell.update_idletasks()
            self.project_host.update_idletasks()

            self.after_idle(_reveal_project)

        def _reveal_project():
            if getattr(self, "_active", None) != target_name:
                return

            target = self._screens.get(target_name)
            if target is None:
                return

            # CENTRE_ACCES_DIRECT_REPAINT_V1
            if target_name == "centre":
                self.project_shell.tkraise()
                target.tkraise()
                self._render_header_canvas()

                self.project_shell.update_idletasks()
                self.project_host.update_idletasks()
                self.header.update_idletasks()
                target.update_idletasks()
                self.update_idletasks()

                self.update()
                return

            target.tkraise()
            self._render_header_canvas()
            self.project_shell.update_idletasks()
            self.project_shell.tkraise()

        self.after_idle(_prepare_second_pass)





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

    # ACCUEIL_FENETRES_BASE_V1
    # Fenêtres de base de l'Accueil.
    # Elles restent volontairement simples et sans fonctions métier.

    def _accueil_center_base_window(self, win, width, height):
        self.update_idletasks()
        sw = max(self.winfo_screenwidth(), width)
        sh = max(self.winfo_screenheight(), height)
        x = max(0, (sw - width) // 2)
        y = max(0, (sh - height) // 2)
        win.geometry(f"{width}x{height}+{x}+{y}")

    def _accueil_base_action_label(self, parent, text):
        return tk.Label(
            parent,
            text=f"{text}   ›",
            bg="#173B6C",
            fg="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
            padx=16,
            pady=9,
            cursor="arrow",
        )

    def _accueil_base_secondary_label(self, parent, text):
        return tk.Label(
            parent,
            text=text,
            bg="#FFFEFC",
            fg="#24313C",
            font=("Segoe UI", 9, "bold"),
            padx=14,
            pady=8,
            relief="solid",
            bd=1,
            cursor="arrow",
        )

    # ACCUEIL_FENETRES_COMPACTES_V3
    def _accueil_base_shell(
        self,
        win,
        *,
        title,
        subtitle,
        accent,
    ):
        win.configure(bg="#F5F1E9")

        canvas = tk.Canvas(
            win,
            bg="#F5F1E9",
            highlightthickness=0,
            bd=0,
        )
        canvas.pack(fill="both", expand=True)

        bg_photo = None
        try:
            cache = getattr(self, "_accueil_window_photos", None)
            if cache is None:
                cache = {}
                self._accueil_window_photos = cache

            key = ("accueil_dialog_bg_v3", 900, 560)
            bg_photo = cache.get(key)
            if bg_photo is None and ACCUEIL_BG.exists():
                image = Image.open(ACCUEIL_BG).convert("RGB")
                image = image.resize((900, 560), Image.Resampling.LANCZOS)
                bg_photo = ImageTk.PhotoImage(image)
                cache[key] = bg_photo

            if bg_photo is not None:
                canvas.create_image(
                    0, 0,
                    image=bg_photo,
                    anchor="nw",
                    tags=("dialog_bg",),
                )
        except Exception:
            bg_photo = None

        body = tk.Frame(
            canvas,
            bg="#FFFEFC",
            padx=22,
            pady=18,
        )
        body_id = canvas.create_window(
            52, 40,
            anchor="nw",
            window=body,
        )

        def redraw(_event=None):
            w = max(canvas.winfo_width(), 620)
            h = max(canvas.winfo_height(), 360)

            canvas.delete("dialog_panel")

            x1, y1 = 24, 20
            x2, y2 = w - 24, h - 20
            cut = 22

            points = [
                x1, y1,
                x2 - cut, y1,
                x2, y1 + cut,
                x2, y2 - cut,
                x2 - cut, y2,
                x1 + cut, y2,
                x1, y2 - cut,
                x1, y1,
            ]

            shadow = []
            for i, value in enumerate(points):
                shadow.append(value + (4 if i % 2 else 3))

            canvas.create_polygon(
                shadow,
                fill="#D8D2C9",
                outline="",
                tags=("dialog_panel",),
            )
            canvas.create_polygon(
                points,
                fill="#FFFEFC",
                outline="#D7D1C7",
                width=1,
                tags=("dialog_panel",),
            )
            canvas.create_rectangle(
                x1 + 2,
                y1 + 2,
                x1 + 7,
                y2 - 2,
                fill=accent,
                outline="",
                tags=("dialog_panel",),
            )

            canvas.coords(body_id, x1 + 28, y1 + 20)
            canvas.itemconfigure(
                body_id,
                width=max(420, x2 - x1 - 56),
                height=max(250, y2 - y1 - 40),
            )

            canvas.tag_lower("dialog_panel")
            if bg_photo is not None:
                canvas.tag_lower("dialog_bg")

        canvas.bind("<Configure>", redraw)
        canvas.after_idle(redraw)

        tk.Label(
            body,
            text=title,
            bg="#FFFEFC",
            fg="#173553",
            font=("Georgia", 15, "bold"),
        ).pack(anchor="w")

        tk.Label(
            body,
            text=subtitle,
            bg="#FFFEFC",
            fg="#68717A",
            font=("Segoe UI", 8),
            justify="left",
            wraplength=650,
        ).pack(anchor="w", pady=(4, 13))

        return body


    # ACCUEIL_CREATION_3_FENETRES_V2
    # "Créer un projet" devient uniquement un sélecteur.
    # Chaque type ouvre ensuite sa propre fenêtre de base.

    # ACCUEIL_CREATION_SELECTION_CONFIRMATION_V3
    # Le choix se fait directement dans les trois cartes de l'Accueil.
    # "Créer un projet" reste inactif tant qu'aucune carte n'est choisie.
    # Une fois un type choisi, il ouvre sa fenêtre descriptive de confirmation.

    # ACCUEIL_CREATION_SELECTION_CONFIRMATION_V3
    # ACCUEIL_VALIDATION_VERS_MAQUETTAGE_V4
    # Le type de projet est choisi une seule fois dans l'Accueil.
    # Après validation, le Maquettage reste commun aux trois types.
    # Le choix est conservé afin d'orienter plus tard automatiquement
    # vers la bonne Conception, sans redemander sa direction à l'utilisateur.

    # ACCUEIL_FENETRES_HARMONISEES_V1

    def _prepare_accueil_dialog(self, win: tk.Toplevel) -> tk.Toplevel:
        previous = getattr(self, "_active_accueil_dialog", None)
        if previous is not None and previous is not win:
            try:
                if previous.winfo_exists():
                    previous.grab_release()
                    previous.destroy()
            except Exception:
                pass

        self._active_accueil_dialog = win

        def _clear_dialog(*_args):
            if getattr(self, "_active_accueil_dialog", None) is win:
                self._active_accueil_dialog = None

        def _close():
            try:
                win.grab_release()
            except Exception:
                pass
            _clear_dialog()
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", _close)
        win.bind("<Destroy>", _clear_dialog, add="+")
        win.transient(self)
        win.resizable(False, False)
        win.grab_set()
        try:
            win.focus_force()
        except Exception:
            pass
        return win

    def _accueil_get_type_icon_photo(self, key: str, size: int = 140):
        cache = getattr(self, "_accueil_window_photos", None)
        if cache is None:
            cache = {}
            self._accueil_window_photos = cache

        cache_key = (key, size)
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        realistic_dir = (
            PROJECT_ROOT / "assets" / "gui_v2" / "accueil_realistic_icons"
        )
        fallback_dir = (
            PROJECT_ROOT / "assets" / "gui_v2" / "project_type_icons"
        )

        direct = {
            "ouvrage_structure": realistic_dir / "ouvrage_structure.png",
            "livre_textuel": realistic_dir / "livre_textuel.png",
            "bande_dessinee": realistic_dir / "bande_dessinee.png",
            "trio": realistic_dir / "trio.png",
        }
        fallback = {
            "ouvrage_structure": (
                fallback_dir / "ouvrage_structure"
                / "ouvrage_structure_128px.png"
            ),
            "livre_textuel": (
                fallback_dir / "livre_textuel"
                / "livre_textuel_128px.png"
            ),
            "bande_dessinee": (
                fallback_dir / "bande_dessinee"
                / "bande_dessinee_128px.png"
            ),
        }

        path = direct.get(key)
        if path is None or not path.exists():
            path = fallback.get(key)

        if path is None or not path.exists():
            return None

        try:
            image = Image.open(path).convert("RGBA")
            image.thumbnail((size, size), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            cache[cache_key] = photo
            return photo
        except Exception:
            return None

    def _accueil_make_dialog_button(
        self,
        parent,
        *,
        text: str,
        command,
        primary: bool,
        min_width: int = 0,
    ):
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg="#173B6C" if primary else "#FFFEFC",
            fg="#FFFFFF" if primary else "#26313A",
            activebackground="#24558A" if primary else "#F3F7FB",
            activeforeground="#FFFFFF" if primary else "#173E70",
            relief="flat" if primary else "solid",
            bd=1,
            padx=16,
            pady=9,
            font=("Segoe UI", 9, "bold" if primary else "normal"),
            cursor="hand2",
        )
        button._tomelinea_button_role = "primary" if primary else "secondary"
        if min_width > 0:
            try:
                button.configure(width=min_width)
            except Exception:
                pass
        return button


    def _open_accueil_create_project_window(self):
        selected = getattr(self, "_selected_project_type", None)

        if selected == "ouvrage_structure":
            self._open_accueil_create_structured_window()
        elif selected == "livre_textuel":
            self._open_accueil_create_textual_window()
        elif selected == "bande_dessinee":
            self._open_accueil_create_comic_window()

    def _reset_accueil_project_selection(self):
        # Remet seulement l'Accueil en état neutre, sans oublier le projet validé.
        self._selected_project_type = None
        self._accueil_prof_state = {}

        render = getattr(self, "_accueil_render", None)
        if callable(render):
            try:
                render()
            except Exception:
                pass

    # CONFIRMATION_TEXTE_NON_COUPE_V4
    def _accueil_project_confirmation_window(
        self,
        *,
        window_title,
        choice_key,
        choice_name,
        accent,
        description,
        points,
        conception_name,
    ):
        win = tk.Toplevel(self)
        win.title(window_title)
        self._prepare_accueil_dialog(win)
        self._accueil_center_base_window(win, 760, 430)

        body = self._accueil_base_shell(
            win,
            title="Confirmer le projet",
            subtitle="Vérifiez le type d’ouvrage choisi avant de poursuivre.",
            accent=accent,
        )

        actions = tk.Frame(body, bg="#FFFEFC")
        actions.pack(side="bottom", fill="x", pady=(12, 0))

        def return_to_home():
            try:
                win.grab_release()
            except Exception:
                pass
            win.destroy()
            self._reset_accueil_project_selection()
            self.show_screen("accueil")

        def validate_and_continue():
            self._project_type_choice = choice_key
            self._confirmed_project_type = choice_key
            try:
                win.grab_release()
            except Exception:
                pass
            win.destroy()
            self.show_screen("maquettage")

        self._accueil_make_dialog_button(
            actions,
            text="‹  Retour à l'accueil",
            command=return_to_home,
            primary=False,
            min_width=18,
        ).pack(side="left")

        self._accueil_make_dialog_button(
            actions,
            text="Valider et passer au Maquettage   ›",
            command=validate_and_continue,
            primary=True,
            min_width=28,
        ).pack(side="right")

        content = tk.Frame(body, bg="#FFFEFC")
        content.pack(fill="both", expand=True)

        visual = tk.Frame(
            content,
            bg="#FAF8F4",
            highlightthickness=1,
            highlightbackground="#DDD8D1",
            padx=15,
            pady=14,
            width=215,
        )
        visual.pack(side="left", fill="y", padx=(0, 15))
        visual.pack_propagate(False)

        photo = self._accueil_get_type_icon_photo(choice_key, 135)
        icon_box = tk.Label(visual, bg="#FAF8F4", text="")
        if photo is not None:
            icon_box.configure(image=photo)
            icon_box.image = photo
        icon_box.pack(pady=(2, 8))

        tk.Label(
            visual,
            text=choice_name,
            bg="#FAF8F4",
            fg="#173553",
            font=("Georgia", 14, "bold"),
            wraplength=175,
            justify="center",
        ).pack()

        text_zone = tk.Frame(content, bg="#FFFEFC")
        text_zone.pack(side="left", fill="both", expand=True)

        description_box = tk.Frame(
            text_zone,
            bg="#FAF8F4",
            highlightthickness=1,
            highlightbackground="#DDD8D1",
            padx=15,
            pady=13,
        )
        description_box.pack(fill="x")

        tk.Label(
            description_box,
            text="À quoi correspond ce type de livre ?",
            bg="#FAF8F4",
            fg="#173553",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")

        description_label = tk.Label(
            description_box,
            text=description,
            bg="#FAF8F4",
            fg="#46525D",
            font=("Segoe UI", 9),
            justify="left",
            anchor="w",
        )
        description_label.pack(anchor="w", fill="x", pady=(7, 0))

        orientation_label = tk.Label(
            text_zone,
            text=(
                "Ce choix sera conservé pour adapter automatiquement "
                "la Conception du projet."
            ),
            bg="#FFFEFC",
            fg="#68717A",
            font=("Segoe UI", 8),
            justify="left",
            anchor="w",
        )
        orientation_label.pack(anchor="w", fill="x", pady=(12, 0))

        # Le retour à la ligne suit la largeur RÉELLE disponible au lieu
        # d'une valeur fixe. Le texte ne peut donc plus sortir de sa zone.
        def resize_description(event):
            try:
                description_label.configure(
                    wraplength=max(180, int(event.width) - 34)
                )
            except Exception:
                pass

        def resize_orientation(event):
            try:
                orientation_label.configure(
                    wraplength=max(180, int(event.width) - 8)
                )
            except Exception:
                pass

        description_box.bind("<Configure>", resize_description, add="+")
        text_zone.bind("<Configure>", resize_orientation, add="+")

        return win





    def _open_accueil_create_structured_window(self):
        self._accueil_project_confirmation_window(
            window_title="TomeLinea — Ouvrage structuré",
            choice_key="ouvrage_structure",
            choice_name="Ouvrage structuré",
            accent="#579B73",
            description=(
                "Un ouvrage composé de pages organisées par types, "
                "répétables et structurées : fiches, catalogues, guides, "
                "collections ou documents modulaires."
            ),
            points=(
                "Le livre pourra être découpé en parties et groupes de pages.",
                "Des types de pages pourront être créés puis réutilisés.",
                "Le Maquettage construira l'ordre général du livre.",
            ),
            conception_name="Conception — Ouvrage structuré",
        )

    def _open_accueil_create_textual_window(self):
        self._accueil_project_confirmation_window(
            window_title="TomeLinea — Livre textuel",
            choice_key="livre_textuel",
            choice_name="Livre textuel",
            accent="#8564B1",
            description=(
                "Un ouvrage principalement composé de texte continu : "
                "roman, récit, essai, biographie ou livre pratique, "
                "organisé autour de chapitres et de sections."
            ),
            points=(
                "Le Maquettage conservera la même logique générale du livre.",
                "La Conception sera ensuite adaptée au travail de texte continu.",
                "Le choix du type ne sera plus demandé après l'Accueil.",
            ),
            conception_name="Conception — Livre textuel",
        )

    def _open_accueil_create_comic_window(self):
        self._accueil_project_confirmation_window(
            window_title="TomeLinea — Bande dessinée",
            choice_key="bande_dessinee",
            choice_name="Bande dessinée",
            accent="#E06B4E",
            description=(
                "Un ouvrage construit autour de planches et de séquences : "
                "bande dessinée, manga, comics, roman graphique ou album "
                "narratif illustré."
            ),
            points=(
                "Le Maquettage reste le passage commun pour organiser le livre.",
                "La Conception sera ensuite adaptée aux planches et aux cases.",
                "Le choix du type ne sera plus demandé après l'Accueil.",
            ),
            conception_name="Conception — Bande dessinée",
        )

    def _open_accueil_open_project_window(self):
        win = tk.Toplevel(self)
        win.title("TomeLinea — Ouvrir un projet")
        self._prepare_accueil_dialog(win)
        self._accueil_center_base_window(win, 760, 430)

        body = self._accueil_base_shell(
            win,
            title="Ouvrir un projet",
            subtitle=(
                "Sélectionnez un projet TomeLinea existant. "
                "Un aperçu du type choisi s'affiche immédiatement."
            ),
            accent="#4A98D0",
        )

        actions = tk.Frame(body, bg="#FFFEFC", height=52)
        actions.pack(side="bottom", fill="x", pady=(16, 0))
        actions.pack_propagate(False)

        def close_window():
            try:
                win.grab_release()
            except Exception:
                pass
            win.destroy()

        selection = {
            "title": "projet x",
            "kind": "Ouvrage structuré",
            "date": "10/08/2026 15:23",
            "path": r"C:\...\projet",
            "key": "ouvrage_structure",
            "summary": "Projet structuré composé de pages types réutilisables.",
        }

        def open_selected_project():
            self._confirmed_project_type = selection["key"]
            try:
                win.grab_release()
            except Exception:
                pass
            win.destroy()
            self.show_screen("centre")

        self._accueil_make_dialog_button(
            actions,
            text="Fermer",
            command=close_window,
            primary=False,
            min_width=14,
        ).pack(side="right")

        self._accueil_make_dialog_button(
            actions,
            text="Ouvrir le projet   ›",
            command=open_selected_project,
            primary=True,
            min_width=18,
        ).pack(side="right", padx=(0, 10))

        content = tk.Frame(body, bg="#FFFEFC")
        content.pack(fill="both", expand=True)

        left = tk.Frame(content, bg="#FFFEFC")
        left.pack(side="left", fill="both", expand=True, padx=(0, 16))

        right = tk.Frame(
            content,
            bg="#FAF8F4",
            highlightthickness=1,
            highlightbackground="#DDD8D1",
            padx=18,
            pady=18,
            width=245,
        )
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        tk.Label(
            left,
            text="Emplacement du projet",
            bg="#FFFEFC",
            fg="#25323E",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w")

        path_row = tk.Frame(left, bg="#FFFEFC")
        path_row.pack(fill="x", pady=(8, 18))

        path_var = tk.StringVar(value=selection["path"])
        path_label = tk.Label(
            path_row,
            textvariable=path_var,
            bg="#F6F3EE",
            fg="#65707A",
            font=("Segoe UI", 9),
            anchor="w",
            padx=10,
            pady=9,
            relief="solid",
            bd=1,
        )
        path_label.pack(side="left", fill="x", expand=True)

        recent_projects = [
            {
                "title": "projet x",
                "kind": "Ouvrage structuré",
                "date": "10/08/2026 15:23",
                "path": r"C:\...\projet",
                "key": "ouvrage_structure",
                "summary": "Projet structuré composé de pages types réutilisables.",
            },
            {
                "title": "nouveau 1",
                "kind": "Livre textuel",
                "date": "07/08/2026 16:09",
                "path": r"C:\...\nouveau_1",
                "key": "livre_textuel",
                "summary": "Projet centré sur du texte continu et des chapitres.",
            },
        ]

        row_widgets = []
        icon_label = None
        title_var = tk.StringVar()
        kind_var = tk.StringVar()
        date_var = tk.StringVar()
        summary_var = tk.StringVar()

        def apply_selection(data):
            selection.update(data)
            path_var.set(data["path"])
            title_var.set(data["title"])
            kind_var.set(data["kind"])
            date_var.set(data["date"])
            summary_var.set(data["summary"])

            for row, payload in row_widgets:
                active = payload["title"] == data["title"]
                bg = "#F4F7FB" if active else "#FAF8F4"
                border = "#94B9D7" if active else "#DDD8D1"
                row.configure(bg=bg, highlightbackground=border)
                for child in row.winfo_children():
                    try:
                        child.configure(bg=bg)
                    except Exception:
                        pass

            if icon_label is not None:
                photo = self._accueil_get_type_icon_photo(data["key"], 170)
                if photo is not None:
                    icon_label.configure(image=photo, text="")
                    icon_label.image = photo
                else:
                    icon_label.configure(image="", text="Aperçu")
                    icon_label.image = None

        def browse_project():
            apply_selection(recent_projects[0])

        self._accueil_make_dialog_button(
            path_row,
            text="Parcourir…",
            command=browse_project,
            primary=False,
            min_width=12,
        ).pack(side="left", padx=(10, 0))

        tk.Label(
            left,
            text="Projets récents",
            bg="#FFFEFC",
            fg="#25323E",
            font=("Segoe UI", 9, "bold"),
        ).pack(anchor="w", pady=(0, 8))

        recent = tk.Frame(
            left,
            bg="#FAF8F4",
            highlightthickness=1,
            highlightbackground="#DDD8D1",
        )
        recent.pack(fill="both", expand=True)

        for data in recent_projects:
            row = tk.Frame(
                recent,
                bg="#FAF8F4",
                highlightthickness=1,
                highlightbackground="#DDD8D1",
                padx=14,
                pady=10,
                cursor="hand2",
            )
            row.pack(fill="x", padx=8, pady=6)

            l1 = tk.Label(
                row,
                text=data["title"],
                bg="#FAF8F4",
                fg="#173553",
                font=("Segoe UI", 9, "bold"),
            )
            l1.pack(side="left")

            l2 = tk.Label(
                row,
                text=data["kind"],
                bg="#FAF8F4",
                fg="#65707A",
                font=("Segoe UI", 8),
            )
            l2.pack(side="left", padx=(18, 0))

            l3 = tk.Label(
                row,
                text=data["date"],
                bg="#FAF8F4",
                fg="#65707A",
                font=("Segoe UI", 8),
            )
            l3.pack(side="right")

            for widget in (row, l1, l2, l3):
                widget.bind(
                    "<Button-1>",
                    lambda _event, payload=data: apply_selection(payload),
                )

            row_widgets.append((row, data))

        tk.Label(
            right,
            text="Aperçu du projet",
            bg="#FAF8F4",
            fg="#6A737C",
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")

        icon_label = tk.Label(right, bg="#FAF8F4", text="")
        icon_label.pack(pady=(10, 12))

        tk.Label(
            right,
            textvariable=title_var,
            bg="#FAF8F4",
            fg="#173553",
            font=("Georgia", 14, "bold"),
            wraplength=180,
            justify="center",
        ).pack()

        tk.Label(
            right,
            textvariable=kind_var,
            bg="#FAF8F4",
            fg="#4D6273",
            font=("Segoe UI", 9, "bold"),
            wraplength=180,
            justify="center",
        ).pack(pady=(6, 2))

        meta = tk.Frame(
            right,
            bg="#FFFEFC",
            highlightthickness=1,
            highlightbackground="#D8D3CC",
            padx=10,
            pady=8,
        )
        meta.pack(fill="x", pady=(12, 10))

        tk.Label(
            meta,
            text="Dernière activité",
            bg="#FFFEFC",
            fg="#6A737C",
            font=("Segoe UI", 8),
        ).pack(anchor="w")
        tk.Label(
            meta,
            textvariable=date_var,
            bg="#FFFEFC",
            fg="#173553",
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", pady=(2, 0))

        tk.Label(
            right,
            textvariable=summary_var,
            bg="#FAF8F4",
            fg="#5F6973",
            font=("Segoe UI", 8),
            justify="left",
            wraplength=180,
        ).pack(anchor="w")

        apply_selection(recent_projects[0])


    def _open_accueil_resume_project_window(self):
        win = tk.Toplevel(self)
        win.title("TomeLinea — Reprendre votre travail")
        self._prepare_accueil_dialog(win)
        self._accueil_center_base_window(win, 760, 470)

        body = self._accueil_base_shell(
            win,
            title="Reprendre votre travail",
            subtitle=(
                "Retrouvez le dernier projet actif et reprenez-le "
                "dans un habillage cohérent avec l'Accueil."
            ),
            accent="#8B6AB8",
        )

        actions = tk.Frame(body, bg="#FFFEFC", height=52)
        actions.pack(side="bottom", fill="x", pady=(16, 0))
        actions.pack_propagate(False)

        def close_window():
            try:
                win.grab_release()
            except Exception:
                pass
            win.destroy()

        def go_to_centre():
            try:
                win.grab_release()
            except Exception:
                pass
            win.destroy()
            self.show_screen("centre")

        self._accueil_make_dialog_button(
            actions,
            text="Fermer",
            command=close_window,
            primary=False,
            min_width=12,
        ).pack(side="right")

        self._accueil_make_dialog_button(
            actions,
            text="Centre du projet   ›",
            command=go_to_centre,
            primary=True,
            min_width=18,
        ).pack(side="right", padx=(0, 10))

        content = tk.Frame(body, bg="#FFFEFC")
        content.pack(fill="both", expand=True)

        left = tk.Frame(
            content,
            bg="#FAF8F4",
            highlightthickness=1,
            highlightbackground="#DDD8D1",
            padx=18,
            pady=18,
            width=225,
        )
        left.pack(side="left", fill="y", padx=(0, 16))
        left.pack_propagate(False)

        photo = self._accueil_get_type_icon_photo("ouvrage_structure", 160)
        icon_label = tk.Label(left, bg="#FAF8F4", text="")
        if photo is not None:
            icon_label.configure(image=photo)
            icon_label.image = photo
        icon_label.pack(pady=(4, 12))

        tk.Label(
            left,
            text="projet x",
            bg="#FAF8F4",
            fg="#173553",
            font=("Georgia", 14, "bold"),
        ).pack()
        tk.Label(
            left,
            text="Ouvrage structuré",
            bg="#FAF8F4",
            fg="#5F6973",
            font=("Segoe UI", 9, "bold"),
        ).pack(pady=(5, 0))

        right = tk.Frame(content, bg="#FFFEFC")
        right.pack(side="left", fill="both", expand=True)

        project = tk.Frame(
            right,
            bg="#FAF8F4",
            highlightthickness=1,
            highlightbackground="#DDD8D1",
            padx=18,
            pady=16,
        )
        project.pack(fill="x", pady=(2, 12))

        tk.Label(
            project,
            text="Dernier état enregistré",
            bg="#FAF8F4",
            fg="#6A737C",
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")

        for label, value in (
            ("Étape actuelle", "Maquettage"),
            ("Dernier bureau", "Maquettage"),
            ("Dernière activité", "10/08/2026 15:23"),
            ("Nombre de pages", "22 pages"),
        ):
            line = tk.Frame(project, bg="#FAF8F4")
            line.pack(fill="x", pady=5)
            tk.Label(
                line,
                text=label,
                bg="#FAF8F4",
                fg="#68717A",
                font=("Segoe UI", 8),
            ).pack(side="left")
            tk.Label(
                line,
                text=value,
                bg="#FAF8F4",
                fg="#26313A",
                font=("Segoe UI", 8, "bold"),
            ).pack(side="right")

        note = tk.Frame(
            right,
            bg="#FCFAF6",
            highlightthickness=1,
            highlightbackground="#DED9D1",
            padx=12,
            pady=10,
        )
        note.pack(fill="x")

        tk.Label(
            note,
            text=(
                "Cette fenêtre reste une base d'apparence. "
                "Les options précises de reprise directe seront détaillées plus tard."
            ),
            bg="#FCFAF6",
            fg="#5F6973",
            font=("Segoe UI", 8),
            justify="left",
            wraplength=420,
        ).pack(anchor="w")


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

        def draw_primary_button_disabled(tag, text, cx, cy, width=205):
            h = 38

            round_rect(
                cx - width / 2 + 1, cy - h / 2 + 3,
                cx + width / 2 + 1, cy + h / 2 + 3,
                8,
                fill="#DEDAD4",
                outline="",
                tags=(tag,),
            )
            round_rect(
                cx - width / 2, cy - h / 2,
                cx + width / 2, cy + h / 2,
                8,
                fill="#E9E7E3",
                outline="#D2CEC8",
                width=1,
                tags=(tag,),
            )
            canvas.create_text(
                cx - 7, cy,
                text=text,
                fill="#92979B",
                font=("Segoe UI", 9, "bold"),
                tags=(tag,),
            )
            canvas.create_text(
                cx + width / 2 - 23, cy,
                text="›",
                fill="#B0B4B7",
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
            canvas.create_line(
                X(445), Y(197), X(755), Y(197),
                fill="#111111", width=1,
            )
            canvas.create_oval(
                X(750), Y(193), X(758), Y(201),
                fill="#FFFDFC",
                outline="#111111",
                width=1,
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

            if self._selected_project_type is None:
                # Aucun choix : le bouton reste visiblement indisponible
                # et ne possède volontairement aucune zone cliquable.
                draw_primary_button_disabled(
                    "create_project_button",
                    "Créer un projet",
                    X(450), Y(399),
                    width=X(205),
                )
            else:
                draw_primary_button(
                    "create_project_button",
                    "Créer un projet",
                    X(450), Y(399),
                    width=X(205),
                )
                bind_interaction(
                    "create_project_button",
                    command=self._open_accueil_create_project_window,
                )

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
                X(1095), Y(197), X(1440), Y(197),
                fill="#111111", width=1,
            )
            canvas.create_oval(
                X(1435), Y(193), X(1443), Y(201),
                fill="#FFFDFC",
                outline="#111111",
                width=1,
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
            bind_interaction(
                "open_project_button",
                command=self._open_accueil_open_project_window,
            )

            # ACCUEIL_FUSION_MODELE_PRECEDENT_V2
            # Fusion simple des deux anciennes zones :
            # - à gauche : ancien contenu "Reprendre votre travail"
            # - à droite : ancien contenu "Repères & accès directs"
            # Le bouton Reprendre est supprimé ; Centre reste dans les accès directs.
            cut_panel(
                X(95), Y(448), X(1490), Y(645),
                fill="#FFFEFC",
                outline="#D8D4CE",
                accent="#8B6AB8",
                rail="left",
                cut_tr=X(28),
                cut_br=X(28),
                cut_bl=X(24),
                tags=("zone_last_project",),
            )

            # -------------------------
            # Partie gauche
            # -------------------------
            canvas.create_text(
                X(145), Y(470),
                text="Dernier projet actif",
                fill="#173553",
                font=("Georgia", F(13), "bold"),
                anchor="nw",
            )
            canvas.create_line(
                X(320), Y(482), X(770), Y(482),
                fill="#B8A5CF",
                width=1,
            )
            canvas.create_oval(
                X(765), Y(478), X(773), Y(486),
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

            # Le bouton Reprendre n'existe plus.
            canvas.create_line(
                X(125), Y(586), X(770), Y(586),
                fill="#E4E0DA",
                width=1,
            )
            canvas.create_text(
                X(135), Y(615),
                text="●  nouveau 1",
                fill="#244055",
                font=("Segoe UI", F(8), "bold"),
                anchor="w",
            )
            draw_chip(
                X(270), Y(603),
                "Ouvrage structuré",
                "#F5FAF7", "#4D9870", X(120),
            )
            draw_chip(
                X(402), Y(603),
                "En cours",
                "#F6FAF7", "#4D9870", X(78),
            )
            draw_chip(
                X(492), Y(603),
                "Dernier bureau : Maquettage",
                "#F8F5FB", "#8063A4", X(172),
            )
            canvas.create_text(
                X(770), Y(615),
                text="07/08/2026 16:09",
                fill="#67717B",
                font=("Segoe UI", F(7)),
                anchor="e",
            )

            # Séparation discrète entre les deux anciens contenus.
            canvas.create_line(
                X(812), Y(475), X(812), Y(620),
                fill="#E1DDD7",
                width=1,
            )

            # -------------------------
            # Partie droite
            # -------------------------
            canvas.create_text(
                X(855), Y(470),
                text="Repères & accès directs",
                fill="#173553",
                font=("Georgia", F(13), "bold"),
                anchor="nw",
            )
            canvas.create_line(
                X(1055), Y(482), X(1445), Y(482),
                fill="#E4B6A8",
                width=1,
            )
            canvas.create_oval(
                X(1440), Y(478), X(1448), Y(486),
                fill="#FFFDFC",
                outline="#E06B4E",
                width=1,
            )
            canvas.create_text(
                X(855), Y(500),
                text="Raccourcis du dernier projet actif.",
                fill="#68717A",
                font=("Segoe UI", F(8)),
                anchor="nw",
            )

            # EXACTEMENT les quatre accès de l'ancien modèle,
            # avec leurs icônes 48 px.
            shortcuts = (
                (
                    "maquettage",
                    "Maquettage",
                    "Organiser les pages",
                    "#579B73",
                    920,
                ),
                (
                    "atelier",
                    "Atelier",
                    "Préparer les gabarits",
                    "#4C9ED0",
                    1085,
                ),
                (
                    "conception",
                    "Conception",
                    "Créer les pages",
                    "#8A69BE",
                    1250,
                ),
                (
                    "centre",
                    "Centre du projet",
                    "Vue d’ensemble",
                    "#E06B4E",
                    1410,
                ),
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

                bind_interaction(
                    tag,
                    command=lambda target=key: self.show_screen(target),
                )

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

        self._accueil_render = render
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

    # INTERACTIONS_PAGES_ET_VUES_V1
    # Navigation de pages depuis le Maquettage + deux vues de lecture.
    def _tomelinea_collect_book_pages(self):
        model = getattr(self, "_maquettage_structure_model", None) or [
            {"name": "Début", "pages": 3},
            {"name": "Partie 1", "pages": 12},
            {"name": "Partie 2", "pages": None},
            {"name": "Partie 3", "pages": None},
            {"name": "Fin", "pages": 3},
        ]
        orders = getattr(self, "_maquettage_page_orders", {})
        pages = []
        global_number = 1

        for group in model:
            group_name = str(group.get("name", "Partie"))
            count = int(group.get("pages") or 0)
            if count <= 0:
                continue

            order = list(orders.get(group_name, range(count)))
            if len(order) != count or set(order) != set(range(count)):
                order = list(range(count))

            low = group_name.strip().lower()
            head_id = count - 1 if low == "fin" else 0

            for position, page_id in enumerate(order, start=1):
                if page_id == head_id:
                    if low in ("début", "debut"):
                        kind = "Couverture"
                    elif low == "fin":
                        kind = "4e de couverture"
                    else:
                        kind = "Tête de partie"
                elif page_id % 4 == 3:
                    kind = "Page auto"
                else:
                    kind = "Page courante"

                pages.append(
                    {
                        "group": group_name,
                        "position": position,
                        "page_id": page_id,
                        "kind": kind,
                        "global": global_number,
                    }
                )
                global_number += 1

        return pages

    def _tomelinea_draw_reader_page(self, canvas, page, x1, y1, x2, y2):
        canvas.create_rectangle(
            x1 + 8,
            y1 + 10,
            x2 + 8,
            y2 + 10,
            fill="#8D8379",
            outline="",
        )
        canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill="#FFFEFC",
            outline="#CFC8BF",
            width=1,
        )

        canvas.create_text(
            x1 + 28,
            y1 + 26,
            text=page["group"],
            fill="#111111",
            font=("Georgia", 13, "bold"),
            anchor="nw",
        )
        canvas.create_text(
            x2 - 28,
            y1 + 28,
            text=f'Page {page["position"]}',
            fill="#4D4A46",
            font=("Segoe UI", 9, "bold"),
            anchor="ne",
        )
        canvas.create_line(
            x1 + 28,
            y1 + 58,
            x2 - 28,
            y1 + 58,
            fill="#CFC9C1",
            width=1,
        )

        kind = page["kind"]
        if kind in ("Couverture", "4e de couverture", "Tête de partie"):
            canvas.create_rectangle(
                x1 + 48,
                y1 + 92,
                x2 - 48,
                y2 - 90,
                fill="#F0ECE4",
                outline="",
            )
            canvas.create_text(
                (x1 + x2) / 2,
                (y1 + y2) / 2 - 20,
                text=kind.upper(),
                fill="#2E2B28",
                font=("Georgia", 19, "bold"),
                anchor="center",
                justify="center",
            )
        else:
            canvas.create_rectangle(
                x1 + 48,
                y1 + 92,
                x2 - 48,
                y1 + 180,
                fill="#E9ECE7",
                outline="",
            )
            yy = y1 + 215
            while yy < y2 - 78:
                right = x2 - 48 if int((yy - y1) / 21) % 5 else x1 + (x2 - x1) * 0.68
                canvas.create_line(
                    x1 + 48,
                    yy,
                    right,
                    yy,
                    fill="#D0CBC4",
                    width=2,
                )
                yy += 21

        canvas.create_text(
            (x1 + x2) / 2,
            y2 - 38,
            text=kind,
            fill="#5C5751",
            font=("Segoe UI", 9),
            anchor="center",
        )
        canvas.create_text(
            (x1 + x2) / 2,
            y2 - 18,
            text=str(page["global"]),
            fill="#7A746D",
            font=("Segoe UI", 8),
            anchor="center",
        )

    def _tomelinea_center_toplevel(self, window, width, height):
        screen_w = max(self.winfo_screenwidth(), width)
        screen_h = max(self.winfo_screenheight(), height)
        width = min(width, screen_w - 20)
        height = min(height, screen_h - 80)
        x = max(0, int((screen_w - width) / 2))
        y = max(0, int((screen_h - height) / 2))
        window.geometry(f"{int(width)}x{int(height)}+{x}+{y}")

    def _tomelinea_open_global_view(self):
        pages = self._tomelinea_collect_book_pages()
        if not pages:
            return

        win = tk.Toplevel(self)
        win.title("TomeLinea — Vue globale")
        win.configure(bg="#C8BDB1")
        win.transient(self)

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        width = max(980, screen_w - 30)
        height = max(640, screen_h - 130)
        self._tomelinea_center_toplevel(win, width, height)

        header = tk.Frame(win, bg="#FBFAF6", height=56)
        header.pack(fill="x")
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="Vue globale · toutes les pages",
            bg="#FBFAF6",
            fg="#111111",
            font=("Georgia", 14, "bold"),
        )
        title.pack(side="left", padx=22, pady=15)

        info_var = tk.StringVar()
        info = tk.Label(
            header,
            textvariable=info_var,
            bg="#FBFAF6",
            fg="#55514C",
            font=("Segoe UI", 9),
        )
        info.pack(side="left", padx=18)

        tk.Button(
            header,
            text="Fermer",
            command=win.destroy,
            relief="flat",
            bd=0,
            bg="#173E70",
            fg="#FFFFFF",
            activebackground="#24558A",
            activeforeground="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
            padx=18,
            pady=7,
            cursor="hand2",
        ).pack(side="right", padx=18, pady=10)

        body = tk.Canvas(win, bg="#C8BDB1", highlightthickness=0)
        body.pack(fill="both", expand=True)

        index = [0]

        def render_reader(_event=None):
            body.delete("all")
            w = max(body.winfo_width(), 900)
            h = max(body.winfo_height(), 520)
            current = pages[index[0]]

            page_h = min(h - 76, 680)
            page_w = page_h / 1.40
            x1 = (w - page_w) / 2
            y1 = (h - page_h) / 2
            self._tomelinea_draw_reader_page(
                body,
                current,
                x1,
                y1,
                x1 + page_w,
                y1 + page_h,
            )
            info_var.set(
                f'{index[0] + 1} / {len(pages)}  ·  '
                f'{current["group"]} · page {current["position"]}'
            )

            body.create_text(
                34,
                h / 2,
                text="‹",
                fill="#625950" if index[0] > 0 else "#AFA79F",
                font=("Segoe UI", 42),
                anchor="w",
            )
            body.create_text(
                w - 34,
                h / 2,
                text="›",
                fill="#625950" if index[0] < len(pages) - 1 else "#AFA79F",
                font=("Segoe UI", 42),
                anchor="e",
            )

        def move(step):
            new_index = max(0, min(len(pages) - 1, index[0] + step))
            if new_index != index[0]:
                index[0] = new_index
                render_reader()

        def wheel(event):
            move(1 if event.delta < 0 else -1)
            return "break"

        body.bind("<Configure>", render_reader)
        win.bind("<MouseWheel>", wheel)
        win.bind("<Right>", lambda _e: move(1))
        win.bind("<Down>", lambda _e: move(1))
        win.bind("<Left>", lambda _e: move(-1))
        win.bind("<Up>", lambda _e: move(-1))
        win.bind("<Next>", lambda _e: move(1))
        win.bind("<Prior>", lambda _e: move(-1))
        win.bind("<Escape>", lambda _e: win.destroy())
        win.after_idle(render_reader)
        win.focus_force()

    def _tomelinea_open_book_view(self):
        pages = self._tomelinea_collect_book_pages()
        if not pages:
            return

        win = tk.Toplevel(self)
        win.title("TomeLinea — Vue livre")
        win.configure(bg="#BDB1A5")
        win.transient(self)

        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        width = min(1180, max(940, int(screen_w * 0.78)))
        height = min(760, max(620, int(screen_h * 0.78)))
        self._tomelinea_center_toplevel(win, width, height)

        header = tk.Frame(win, bg="#FBFAF6", height=56)
        header.pack(fill="x")
        header.pack_propagate(False)

        tk.Label(
            header,
            text="Vue livre · feuilletage",
            bg="#FBFAF6",
            fg="#111111",
            font=("Georgia", 14, "bold"),
        ).pack(side="left", padx=22, pady=15)

        info_var = tk.StringVar()
        tk.Label(
            header,
            textvariable=info_var,
            bg="#FBFAF6",
            fg="#55514C",
            font=("Segoe UI", 9),
        ).pack(side="left", padx=18)

        tk.Button(
            header,
            text="Fermer",
            command=win.destroy,
            relief="flat",
            bd=0,
            bg="#173E70",
            fg="#FFFFFF",
            activebackground="#24558A",
            activeforeground="#FFFFFF",
            font=("Segoe UI", 9, "bold"),
            padx=18,
            pady=7,
            cursor="hand2",
        ).pack(side="right", padx=18, pady=10)

        body = tk.Canvas(win, bg="#BDB1A5", highlightthickness=0)
        body.pack(fill="both", expand=True)

        spread_left = [-1]

        def render_book(_event=None):
            body.delete("all")
            w = max(body.winfo_width(), 860)
            h = max(body.winfo_height(), 520)

            page_h = min(h - 84, 610)
            page_w = page_h / 1.40
            gap = 18
            total_w = page_w * 2 + gap
            left_x = (w - total_w) / 2
            y1 = (h - page_h) / 2

            body.create_rectangle(
                left_x - 18,
                y1 - 18,
                left_x + total_w + 18,
                y1 + page_h + 18,
                fill="#8E8277",
                outline="",
            )

            li = spread_left[0]
            ri = li + 1

            if 0 <= li < len(pages):
                self._tomelinea_draw_reader_page(
                    body,
                    pages[li],
                    left_x,
                    y1,
                    left_x + page_w,
                    y1 + page_h,
                )
            else:
                body.create_rectangle(
                    left_x,
                    y1,
                    left_x + page_w,
                    y1 + page_h,
                    fill="#E9E3DB",
                    outline="#CFC8BF",
                )

            right_x = left_x + page_w + gap
            if 0 <= ri < len(pages):
                self._tomelinea_draw_reader_page(
                    body,
                    pages[ri],
                    right_x,
                    y1,
                    right_x + page_w,
                    y1 + page_h,
                )
            else:
                body.create_rectangle(
                    right_x,
                    y1,
                    right_x + page_w,
                    y1 + page_h,
                    fill="#E9E3DB",
                    outline="#CFC8BF",
                )

            gutter_x = left_x + page_w + gap / 2
            body.create_line(
                gutter_x,
                y1 + 4,
                gutter_x,
                y1 + page_h - 4,
                fill="#70665D",
                width=3,
            )

            visible = []
            if 0 <= li < len(pages):
                visible.append(str(pages[li]["global"]))
            if 0 <= ri < len(pages):
                visible.append(str(pages[ri]["global"]))
            info_var.set("Pages " + " – ".join(visible) if visible else "Couverture")

            body.create_text(
                30,
                h / 2,
                text="‹",
                fill="#625950" if li > -1 else "#A59C94",
                font=("Segoe UI", 42),
                anchor="w",
            )
            body.create_text(
                w - 30,
                h / 2,
                text="›",
                fill="#625950" if ri < len(pages) - 1 else "#A59C94",
                font=("Segoe UI", 42),
                anchor="e",
            )

        def turn(step):
            current = spread_left[0]
            if step > 0:
                candidate = current + 2
                if candidate <= len(pages) - 1:
                    spread_left[0] = candidate
            else:
                candidate = current - 2
                if candidate >= -1:
                    spread_left[0] = candidate
            render_book()

        def wheel(event):
            turn(1 if event.delta < 0 else -1)
            return "break"

        body.bind("<Configure>", render_book)
        win.bind("<MouseWheel>", wheel)
        win.bind("<Right>", lambda _e: turn(1))
        win.bind("<Left>", lambda _e: turn(-1))
        win.bind("<Next>", lambda _e: turn(1))
        win.bind("<Prior>", lambda _e: turn(-1))
        win.bind("<Escape>", lambda _e: win.destroy())
        win.after_idle(render_book)
        win.focus_force()


    # FENETRES_BASE_PARTIE_TYPE_V1
    # Fenêtres volontairement minimales : elles servent uniquement de base
    # aux futures fonctions du Maquettage.

    def _tomelinea_open_add_part_window(self):
        win = tk.Toplevel(self)
        win.title("TomeLinea — Ajouter une partie")
        win.transient(self)
        win.resizable(False, False)
        self._tomelinea_center_toplevel(win, 540, 360)

        shell = tk.Frame(win, padx=22, pady=20)
        shell.pack(fill="both", expand=True)

        tk.Label(
            shell,
            text="Ajouter une partie",
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w")

        tk.Label(
            shell,
            text=(
                "Base de la future commande. "
                "Les réglages seront définis plus tard."
            ),
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(4, 18))

        form = tk.Frame(shell)
        form.pack(fill="x")

        tk.Label(
            form,
            text="Nom de la partie",
            width=22,
            anchor="w",
        ).grid(row=0, column=0, sticky="w", pady=7)

        name_entry = tk.Entry(form)
        name_entry.insert(0, "Nouvelle partie")
        name_entry.grid(
            row=0,
            column=1,
            sticky="ew",
            pady=7,
        )

        tk.Label(
            form,
            text="Pages prévues",
            width=22,
            anchor="w",
        ).grid(row=1, column=0, sticky="w", pady=7)

        pages_entry = tk.Spinbox(
            form,
            from_=1,
            to=999,
            width=10,
        )
        pages_entry.delete(0, "end")
        pages_entry.insert(0, "12")
        pages_entry.grid(
            row=1,
            column=1,
            sticky="w",
            pady=7,
        )

        tk.Label(
            form,
            text="Position",
            width=22,
            anchor="w",
        ).grid(row=2, column=0, sticky="w", pady=7)

        model = getattr(
            self,
            "_maquettage_structure_model",
            [],
        )
        choices = [
            f'Après {group.get("name", "Partie")}'
            for group in model[:-1]
        ]
        if not choices:
            choices = ["Avant Fin"]

        position_var = tk.StringVar(value=choices[-1])
        tk.OptionMenu(
            form,
            position_var,
            *choices,
        ).grid(
            row=2,
            column=1,
            sticky="ew",
            pady=7,
        )

        form.columnconfigure(1, weight=1)

        tk.Label(
            shell,
            text="Début et Fin restent les bornes fixes du livre.",
            font=("Segoe UI", 8),
        ).pack(anchor="w", pady=(15, 8))

        actions = tk.Frame(shell)
        actions.pack(side="bottom", fill="x", pady=(18, 0))

        tk.Button(
            actions,
            text="Fermer",
            command=win.destroy,
            width=12,
        ).pack(side="right")

        tk.Button(
            actions,
            text="Ajouter",
            state="disabled",
            width=12,
        ).pack(side="right", padx=(0, 8))

        win.after_idle(name_entry.focus_set)

    def _tomelinea_open_page_type_window(self, group_name="Partie"):
        win = tk.Toplevel(self)
        win.title("TomeLinea — Créer / choisir un type")
        win.transient(self)
        win.resizable(False, False)
        self._tomelinea_center_toplevel(win, 700, 470)

        shell = tk.Frame(win, padx=22, pady=20)
        shell.pack(fill="both", expand=True)

        tk.Label(
            shell,
            text="Créer / choisir un type de page",
            font=("Segoe UI", 15, "bold"),
        ).pack(anchor="w")

        tk.Label(
            shell,
            text=f"Partie concernée : {group_name}",
            font=("Segoe UI", 9),
        ).pack(anchor="w", pady=(4, 16))

        content = tk.Frame(shell)
        content.pack(fill="both", expand=True)

        existing = tk.LabelFrame(
            content,
            text="Choisir un type existant",
            padx=12,
            pady=12,
        )
        existing.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(0, 8),
        )

        type_list = tk.Listbox(
            existing,
            height=10,
        )
        type_list.pack(fill="both", expand=True)
        type_list.insert(
            "end",
            "Aucun type défini pour le moment",
        )
        type_list.configure(state="disabled")

        create = tk.LabelFrame(
            content,
            text="Créer un nouveau type",
            padx=12,
            pady=12,
        )
        create.pack(
            side="left",
            fill="both",
            expand=True,
            padx=(8, 0),
        )

        tk.Label(
            create,
            text="Nom du type",
            anchor="w",
        ).pack(fill="x")
        tk.Entry(create).pack(
            fill="x",
            pady=(3, 10),
        )

        tk.Label(
            create,
            text="Nom court",
            anchor="w",
        ).pack(fill="x")
        tk.Entry(create).pack(
            fill="x",
            pady=(3, 10),
        )

        head_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            create,
            text="Traiter comme tête de partie",
            variable=head_var,
        ).pack(anchor="w", pady=(2, 10))

        tk.Label(
            create,
            text="Description",
            anchor="w",
        ).pack(fill="x")
        tk.Text(
            create,
            height=4,
            wrap="word",
        ).pack(fill="both", expand=True, pady=(3, 0))

        actions = tk.Frame(shell)
        actions.pack(fill="x", pady=(18, 0))

        tk.Button(
            actions,
            text="Fermer",
            command=win.destroy,
            width=12,
        ).pack(side="right")

        tk.Button(
            actions,
            text="Utiliser / créer",
            state="disabled",
            width=14,
        ).pack(side="right", padx=(0, 8))

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
        self._maquettage_structure_model = structure_model
        if not hasattr(self, "_maquettage_page_orders"):
            self._maquettage_page_orders = {}

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
        maquettage_button_actions: dict[str, object] = {}
        maquettage_hovered: str | None = None
        maquettage_pressed: str | None = None

        # Interactions des vignettes de pages.
        maquettage_page_regions: list[dict] = []
        maquettage_page_hovered: int | None = None
        maquettage_page_pressed: int | None = None
        maquettage_page_pressed_slot: int | None = None
        maquettage_page_press_xy: tuple[float, float] | None = None
        maquettage_page_dragging = False
        maquettage_page_drop_slot: int | None = None

        # STRUCTURE_CLIQUABLE_DRAPEAUX_RUBAN_V1
        maquettage_structure_regions: list[dict] = []
        maquettage_structure_hovered: int | None = None

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

        def maquettage_structure_at(x, y):
            for region in reversed(maquettage_structure_regions):
                if (
                    region["x1"] <= x <= region["x2"]
                    and region["y1"] <= y <= region["y2"]
                ):
                    return region
            return None

        def maquettage_page_at(x, y):
            for region in reversed(maquettage_page_regions):
                if (
                    region["x1"] <= x <= region["x2"]
                    and region["y1"] <= y <= region["y2"]
                ):
                    return region
            return None

        def maquettage_drop_slot_at(x, y):
            if not maquettage_page_regions:
                return None

            direct = maquettage_page_at(x, y)
            if direct is not None:
                center_x = (direct["x1"] + direct["x2"]) / 2
                return direct["slot"] + (1 if x > center_x else 0)

            nearest = min(
                maquettage_page_regions,
                key=lambda region: (
                    ((region["x1"] + region["x2"]) / 2 - x) ** 2
                    + ((region["y1"] + region["y2"]) / 2 - y) ** 2
                ),
            )
            center_x = (nearest["x1"] + nearest["x2"]) / 2
            return nearest["slot"] + (1 if x > center_x else 0)

        def secondary_button(
            x1,
            y1,
            x2,
            y2,
            text,
            color=None,
            *,
            muted=False,
            command=None,
        ):
            """Bouton secondaire TomeLinea, calé sur le bouton Ouvrir de l'Accueil."""
            radius = 7
            button_id = maquettage_button_id(text, x1, y1, x2, y2)
            register_maquettage_button(button_id, x1, y1, x2, y2)
            if command is not None:
                maquettage_button_actions[button_id] = command

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
            *,
            command=None,
        ):
            """Bouton principal TomeLinea, calé sur Créer un projet de l'Accueil."""
            radius = 7
            button_id = maquettage_button_id(text, x1, y1, x2, y2)
            register_maquettage_button(button_id, x1, y1, x2, y2)
            if command is not None:
                maquettage_button_actions[button_id] = command

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
            maquettage_button_actions.clear()
            maquettage_page_regions.clear()
            maquettage_structure_regions.clear()
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

                # FOND_MAQUETTAGE_GRIS_DOUX_V1
                # Léger voile gris TomeLinea pour mieux détacher les plages
                # de travail blanches, sans assombrir réellement l'interface.
                image = Image.blend(
                    image.convert("RGB"),
                    Image.new("RGB", image.size, "#D7D9DC"),
                    0.10,
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
                    fill="#EEEDEA",
                    outline="",
                    tags="maquettage_bg",
                )

            # ------------------------------------------------------
            # PÔLE 1 — STRUCTURE DU LIVRE
            # Fusion de l'ancienne barre des groupes et de la vue globale.
            # ------------------------------------------------------
            # FOND_MAQUETTAGE_BRUN_FUME_V3
            # Brun chaud dérivé de l'ivoire de l'Accueil, mais plus soutenu.
            # Volutes plus visibles que dans la version grise précédente.
            from PIL import ImageDraw, ImageFilter

            bg_size = (width, height)
            if getattr(self, "_maquettage_smoke_v3_size", None) != bg_size:
                # Base brun-taupe : contraste proche du gris validé,
                # mais raccordée à la palette chaude de l'Accueil.
                smoke_bg = Image.new("RGBA", bg_size, "#C2B6A8")

                smoke_layer = Image.new(
                    "RGBA",
                    bg_size,
                    (0, 0, 0, 0),
                )
                smoke_draw = ImageDraw.Draw(smoke_layer, "RGBA")

                # Grandes volutes ivoire chaudes.
                light_clouds = (
                    (
                        -int(width * 0.10),
                        -int(height * 0.05),
                        int(width * 0.46),
                        int(height * 0.33),
                        (248, 242, 232, 82),
                    ),
                    (
                        int(width * 0.12),
                        int(height * 0.16),
                        int(width * 0.63),
                        int(height * 0.48),
                        (243, 236, 226, 66),
                    ),
                    (
                        int(width * 0.54),
                        -int(height * 0.03),
                        int(width * 1.05),
                        int(height * 0.36),
                        (250, 244, 235, 76),
                    ),
                    (
                        -int(width * 0.08),
                        int(height * 0.57),
                        int(width * 0.46),
                        int(height * 0.97),
                        (242, 235, 224, 62),
                    ),
                    (
                        int(width * 0.48),
                        int(height * 0.53),
                        int(width * 1.07),
                        int(height * 1.03),
                        (247, 240, 230, 70),
                    ),
                )
                for cloud in light_clouds:
                    smoke_draw.ellipse(cloud[:4], fill=cloud[4])

                # Volutes brunes plus profondes pour créer le relief.
                dark_clouds = (
                    (
                        int(width * 0.02),
                        int(height * 0.27),
                        int(width * 0.39),
                        int(height * 0.70),
                        (105, 88, 72, 40),
                    ),
                    (
                        int(width * 0.31),
                        -int(height * 0.09),
                        int(width * 0.75),
                        int(height * 0.27),
                        (111, 94, 78, 34),
                    ),
                    (
                        int(width * 0.67),
                        int(height * 0.25),
                        int(width * 1.08),
                        int(height * 0.76),
                        (101, 84, 70, 39),
                    ),
                    (
                        int(width * 0.28),
                        int(height * 0.58),
                        int(width * 0.70),
                        int(height * 1.05),
                        (116, 99, 83, 30),
                    ),
                )
                for cloud in dark_clouds:
                    smoke_draw.ellipse(cloud[:4], fill=cloud[4])

                # Flou moins fort que dans la V2 : les volutes restent perceptibles
                # tout en gardant l'effet de fumée diffuse.
                blur_radius = max(
                    24,
                    int(min(width, height) * 0.028),
                )
                smoke_layer = smoke_layer.filter(
                    ImageFilter.GaussianBlur(blur_radius)
                )

                smoke_bg = Image.alpha_composite(
                    smoke_bg,
                    smoke_layer,
                ).convert("RGB")

                self._maquettage_smoke_v3_photo = ImageTk.PhotoImage(
                    smoke_bg
                )
                self._maquettage_smoke_v3_size = bg_size

            canvas.create_image(
                0,
                0,
                image=self._maquettage_smoke_v3_photo,
                anchor="nw",
                tags="maquettage_smoke_v3",
            )

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

            # Variante finale — bornes fixes + parties internes.
            # STRUCTURE_CLIQUABLE_DRAPEAUX_RUBAN_V1
            # Les livres et drapeaux sélectionnent directement la partie
            # affichée dans Composition.
            node_count = len(structure_model)

            fixed_start_x = track_left + 52
            fixed_end_x = track_right - 52

            if node_count <= 1:
                node_centers = [fixed_start_x]
            elif node_count == 2:
                node_centers = [fixed_start_x, fixed_end_x]
            else:
                internal_count = node_count - 2
                internal_step = (
                    fixed_end_x - fixed_start_x
                ) / (internal_count + 1)
                node_centers = [fixed_start_x]
                node_centers.extend(
                    fixed_start_x + internal_step * (index + 1)
                    for index in range(internal_count)
                )
                node_centers.append(fixed_end_x)

            if not hasattr(self, "_maquettage_structure_photos"):
                self._maquettage_structure_photos = {}

            structure_icon_dir = (
                PROJECT_ROOT / "assets" / "gui_v2" / "structure_line_icons"
            )

            ribbon_flag_path = (
                PROJECT_ROOT
                / "assets"
                / "gui_v2"
                / "navigation_icons_photorealistes"
                / "10_finalisation"
                / "10_finalisation_64px.png"
            )
            fallback_flag_path = structure_icon_dir / "debut_final.png"

            book_icon_paths = [
                structure_icon_dir / "partie_1.png",
                structure_icon_dir / "partie_2.png",
                structure_icon_dir / "partie_3.png",
            ]

            def structure_photo(
                path,
                max_w,
                max_h,
                *,
                green_flag=False,
            ):
                key = (
                    str(path),
                    max_w,
                    max_h,
                    bool(green_flag),
                )
                cached = self._maquettage_structure_photos.get(key)
                if cached is not None:
                    return cached
                if not path.exists():
                    return None

                try:
                    image = Image.open(path).convert("RGBA")
                    alpha = image.getchannel("A")
                    bbox = alpha.getbbox()
                    if bbox:
                        image = image.crop(bbox)

                    if green_flag:
                        pixels = image.load()
                        for yy in range(image.height):
                            for xx in range(image.width):
                                r, g, b, a = pixels[xx, yy]
                                if (
                                    a > 0
                                    and r > 95
                                    and r > g * 1.22
                                    and r > b * 1.18
                                ):
                                    luminosity = max(
                                        0.52,
                                        min(1.18, r / 205.0),
                                    )
                                    nr = int(max(0, min(255, 83 * luminosity)))
                                    ng = int(max(0, min(255, 151 * luminosity)))
                                    nb = int(max(0, min(255, 105 * luminosity)))
                                    pixels[xx, yy] = (nr, ng, nb, a)

                    image.thumbnail(
                        (max_w, max_h),
                        Image.Resampling.LANCZOS,
                    )
                    photo = ImageTk.PhotoImage(image)
                    self._maquettage_structure_photos[key] = photo
                    return photo
                except Exception:
                    return None

            canvas.create_line(
                fixed_start_x,
                track_y,
                fixed_end_x,
                track_y,
                fill="#B7B4AE",
                width=1,
                tags="maquettage_ui",
            )

            for index, group in enumerate(structure_model):
                cx = node_centers[index]
                is_selected = index == selected_index
                is_hovered = index == maquettage_structure_hovered

                diamond_r = 5 if is_selected else 4
                canvas.create_polygon(
                    cx,
                    track_y - diamond_r,
                    cx + diamond_r,
                    track_y,
                    cx,
                    track_y + diamond_r,
                    cx - diamond_r,
                    track_y,
                    fill="#111111" if is_selected else "#FFFFFF",
                    outline="#111111",
                    width=1,
                    tags="maquettage_ui",
                )

                green_flag = False

                if index == 0:
                    icon_path = (
                        ribbon_flag_path
                        if ribbon_flag_path.exists()
                        else fallback_flag_path
                    )
                    icon_w, icon_h = 48, 38
                    icon_anchor_y = track_y - 4
                    green_flag = True
                elif index == node_count - 1:
                    icon_path = (
                        ribbon_flag_path
                        if ribbon_flag_path.exists()
                        else fallback_flag_path
                    )
                    icon_w, icon_h = 48, 38
                    icon_anchor_y = track_y - 4
                else:
                    icon_path = book_icon_paths[
                        (index - 1) % len(book_icon_paths)
                    ]
                    icon_w, icon_h = 62, 42
                    icon_anchor_y = track_y - 12

                hover_lift = 1 if is_hovered else 0

                photo = structure_photo(
                    icon_path,
                    icon_w,
                    icon_h,
                    green_flag=green_flag,
                )
                if photo is not None:
                    canvas.create_image(
                        cx,
                        icon_anchor_y - hover_lift,
                        image=photo,
                        anchor="s",
                        tags="maquettage_ui",
                    )

                maquettage_structure_regions.append(
                    {
                        "index": index,
                        "x1": cx - icon_w / 2 - 5,
                        "y1": icon_anchor_y - icon_h - 7,
                        "x2": cx + icon_w / 2 + 5,
                        "y2": icon_anchor_y + 5,
                    }
                )

                pages = group["pages"]
                pages_label = (
                    f"{pages} pages"
                    if isinstance(pages, int)
                    else "— pages"
                )

                canvas.create_text(
                    cx,
                    track_y + 27,
                    text=group["name"],
                    fill="#111111",
                    font=("Georgia", 10, "bold"),
                    anchor="center",
                    tags="maquettage_ui",
                )
                canvas.create_text(
                    cx,
                    track_y + 48,
                    text=pages_label,
                    fill="#111111",
                    font=("Segoe UI", 8),
                    anchor="center",
                    tags="maquettage_ui",
                )

                if is_selected:
                    canvas.create_line(
                        cx - 27,
                        track_y + 65,
                        cx + 27,
                        track_y + 65,
                        fill="#111111",
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
                command=self._tomelinea_open_add_part_window,
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

            # Troisième ligne : deux modes de visualisation du livre.
            view_y1 = top_y1 + 138
            view_y2 = top_y1 + 171
            secondary_button(
                tool_x1,
                view_y1,
                tool_x1 + tool_half,
                view_y2,
                "Vue globale",
                "#8D70C7",
                muted=True,
                command=self._tomelinea_open_global_view,
            )
            secondary_button(
                tool_x1 + tool_half + tool_gap,
                view_y1,
                tool_x2,
                view_y2,
                "Vue livre",
                "#8D70C7",
                muted=True,
                command=self._tomelinea_open_book_view,
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

            # TRAITS_CIBLES_MAQUETTAGE_V2
            # Trait noir + petit cercle uniquement derrière les titres demandés.
            # Aucun changement de structure, de zone ou de rendu métier.

            def _titre_trait(x1, x2, y):
                if x2 - x1 < 24:
                    return
                canvas.create_line(
                    x1, y, x2, y,
                    fill="#111111",
                    width=1,
                    tags="maquettage_ui",
                )
                canvas.create_oval(
                    x2 - 4, y - 4,
                    x2 + 4, y + 4,
                    fill="#FFFEFC",
                    outline="#111111",
                    width=1,
                    tags="maquettage_ui",
                )

            # Structure du livre : le trait s'arrête avant la zone Outils.
            _titre_trait(
                margin + 232,
                tools_left - 30,
                top_y1 + 31,
            )

            # Outils de structure.
            _titre_trait(
                tools_left + 158,
                width - margin - 24,
                top_y1 + 31,
            )

            # Détail de la partie.
            _titre_trait(
                left_x1 + 180,
                left_x2 - 24,
                work_y1 + 31,
            )

            # Composition : le trait se termine avant "Types".
            _titre_trait(
                center_x1 + 288,
                type_button_x1 - 78,
                work_y1 + 31,
            )

            # Propriétés de la page.
            _titre_trait(
                right_x1 + 208,
                right_x2 - 24,
                work_y1 + 31,
            )

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
                command=(
                    lambda group_name=str(selected_group["name"]):
                    self._tomelinea_open_page_type_window(group_name)
                ),
            )

            # ------------------------------------------------------
            # COLONNE GAUCHE — détail de la partie
            # DETAIL_PARTIE_TEXTE_NOIR_V2
            # ------------------------------------------------------
            lx = left_x1 + 22
            ly = work_y1 + 90

            canvas.create_text(
                lx,
                ly,
                text=selected_group["name"],
                fill="#111111",
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
                    fill="#111111",
                    font=("Segoe UI", 8),
                    anchor="nw",
                    tags="maquettage_ui",
                )
                canvas.create_text(
                    left_x2 - 22,
                    ly,
                    text=value,
                    fill="#111111",
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
                fill="#111111",
                font=("Segoe UI", 8),
                anchor="nw",
                justify="left",
                tags="maquettage_ui",
            )

            # ------------------------------------------------------
            # ------------------------------------------------------
            # CENTRE — pages de la partie sélectionnée
            # COMPOSITION_3_TAILLES_V1
            #
            # Une seule partie est affichée à la fois.
            # 3 tailles, toutes avec exactement la même proportion :
            # - grande  : tête de partie
            # - moyenne : page courante
            # - petite  : page automatique
            #
            # Début / Partie : la première page est la tête de partie.
            # Fin             : la dernière page est la tête de partie.
            # Les commandes restent volontairement inactives.
            # ------------------------------------------------------
            cx1 = center_x1 + 22
            cx2 = center_x2 - 22
            pages_top = work_y1 + 82
            pages_bottom = work_y2 - 28

            page_count = int(selected_group["pages"] or 0)
            group_name_low = str(selected_group["name"]).strip().lower()
            group_key = str(selected_group["name"])
            page_order = list(
                self._maquettage_page_orders.get(group_key, range(page_count))
            )
            if (
                len(page_order) != page_count
                or set(page_order) != set(range(page_count))
            ):
                page_order = list(range(page_count))
            self._maquettage_page_orders[group_key] = page_order

            # Une proportion unique pour toutes les vignettes.
            page_ratio = 1.40

            large_w = 84
            large_h = int(large_w * page_ratio)

            normal_w = 68
            normal_h = int(normal_w * page_ratio)

            auto_w = 58
            auto_h = int(auto_w * page_ratio)

            # Une seule grande vignette par partie.
            if page_count > 0:
                if group_name_low == "fin":
                    head_index = page_count - 1
                else:
                    head_index = 0
            else:
                head_index = -1

            # Pour cette prévisualisation, les types ne sont pas encore pilotés
            # par les commandes. Quelques pages auto sont simulées visuellement.
            def visual_page_kind(index):
                if index == head_index:
                    return "head"
                if index % 4 == 3:
                    return "auto"
                return "normal"

            # Maximum 7 vignettes par ligne pour garantir une lecture confortable
            # et conserver au minimum deux lignes visibles avec une partie longue.
            max_per_row = 7
            total_rows = (
                (page_count + max_per_row - 1) // max_per_row
                if page_count
                else 0
            )

            visible_rows = min(total_rows, 2)
            row_height = large_h + 48
            row_gap = 18

            def draw_page_preview(px1, py1, pw, ph, kind, page_id, display_number, slot_index):
                px2 = px1 + pw
                py2 = py1 + ph

                # Ombre douce.
                rounded(
                    px1 + 2,
                    py1 + 4,
                    px2 + 2,
                    py2 + 4,
                    7,
                    fill="#D8D3CB",
                    outline="",
                    tags="maquettage_ui",
                )

                # Carte page.
                rounded(
                    px1,
                    py1,
                    px2,
                    py2,
                    7,
                    fill="#FFFEFB",
                    outline="#D8D3CB",
                    width=1,
                    tags="maquettage_ui",
                )

                # Numéro discret.
                canvas.create_text(
                    px1 + 7,
                    py1 + 7,
                    text=str(display_number),
                    fill="#58636D",
                    font=("Segoe UI", 7, "bold"),
                    anchor="nw",
                    tags="maquettage_ui",
                )

                # Habillage miniature différent selon la classe,
                # sans changer les proportions de page.
                if kind == "head":
                    canvas.create_rectangle(
                        px1 + 8,
                        py1 + 10,
                        px2 - 8,
                        py2 - 10,
                        fill="#F1EEE7",
                        outline="",
                        tags="maquettage_ui",
                    )
                    canvas.create_line(
                        px1 + 13,
                        py1 + 18,
                        px2 - 13,
                        py1 + 18,
                        fill="#C8C2B8",
                        width=1,
                        tags="maquettage_ui",
                    )
                    canvas.create_text(
                        (px1 + px2) / 2,
                        py1 + ph * 0.42,
                        text=(
                            "FIN"
                            if group_name_low == "fin"
                            else "TÊTE DE\nPARTIE"
                        ),
                        fill="#343434",
                        font=("Georgia", 8, "bold"),
                        justify="center",
                        anchor="center",
                        tags="maquettage_ui",
                    )
                    canvas.create_polygon(
                        px1 + 8, py2 - 30,
                        px1 + pw * 0.34, py2 - 45,
                        px1 + pw * 0.58, py2 - 34,
                        px2 - 8, py2 - 48,
                        px2 - 8, py2 - 10,
                        px1 + 8, py2 - 10,
                        fill="#E4E7DD",
                        outline="",
                        tags="maquettage_ui",
                    )

                elif kind == "auto":
                    canvas.create_text(
                        (px1 + px2) / 2,
                        py1 + 24,
                        text="AUTO",
                        fill="#6B737A",
                        font=("Segoe UI", 6, "bold"),
                        anchor="center",
                        tags="maquettage_ui",
                    )
                    for line_i in range(5):
                        yy = py1 + 36 + line_i * max(5, int(ph * 0.07))
                        canvas.create_line(
                            px1 + 12,
                            yy,
                            px2 - 12,
                            yy,
                            fill="#D9D5CE",
                            width=1,
                            tags="maquettage_ui",
                        )

                else:
                    canvas.create_rectangle(
                        px1 + 10,
                        py1 + 18,
                        px2 - 10,
                        py1 + ph * 0.42,
                        fill="#E9ECE7",
                        outline="",
                        tags="maquettage_ui",
                    )
                    for line_i in range(5):
                        yy = py1 + ph * 0.50 + line_i * max(
                            4,
                            int(ph * 0.055),
                        )
                        line_right = (
                            px2 - 16
                            if line_i < 4
                            else px1 + pw * 0.68
                        )
                        canvas.create_line(
                            px1 + 11,
                            yy,
                            line_right,
                            yy,
                            fill="#D2CEC7",
                            width=1,
                            tags="maquettage_ui",
                        )

                # Libellé de type sous la vignette.
                if kind == "head":
                    if group_name_low == "début" or group_name_low == "debut":
                        label = "Couverture"
                    elif group_name_low == "fin":
                        label = "4e de couverture"
                    else:
                        label = "Tête de partie"
                    label_fill = "#F0EAF7"
                elif kind == "auto":
                    label = "Page auto"
                    label_fill = "#EDF2F6"
                else:
                    label = "Page courante"
                    label_fill = "#F3EFE7"

                label_y = py2 + 11
                label_w = max(48, min(88, 10 + len(label) * 5))

                rounded(
                    (px1 + px2) / 2 - label_w / 2,
                    label_y - 8,
                    (px1 + px2) / 2 + label_w / 2,
                    label_y + 8,
                    7,
                    fill=label_fill,
                    outline="#DDD8D1",
                    width=1,
                    tags="maquettage_ui",
                )
                canvas.create_text(
                    (px1 + px2) / 2,
                    label_y,
                    text=label,
                    fill="#4F5962",
                    font=("Segoe UI", 6),
                    anchor="center",
                    tags="maquettage_ui",
                )

                # Région cliquable : vignette + libellé.
                maquettage_page_regions.append(
                    {
                        "page_id": page_id,
                        "slot": slot_index,
                        "x1": px1 - 3,
                        "y1": py1 - 3,
                        "x2": px2 + 3,
                        "y2": label_y + 12,
                    }
                )

                # Même grammaire de réaction que les boutons : contour plus
                # net au survol, puis accent plus franc à l'appui / au glisser.
                page_is_pressed = page_id == maquettage_page_pressed
                page_is_hovered = (
                    page_id == maquettage_page_hovered
                    and not maquettage_page_dragging
                )
                if page_is_pressed or page_is_hovered:
                    rounded(
                        px1 - 2,
                        py1 - 2,
                        px2 + 2,
                        py2 + 2,
                        8,
                        fill="",
                        outline=(
                            "#173E70" if page_is_pressed else "#496D94"
                        ),
                        width=2,
                        tags="maquettage_ui",
                    )

            # Deux lignes visibles au maximum dans cette première mise en place.
            # Si davantage de lignes sont nécessaires, un indicateur de
            # défilement vertical est affiché, sans rendre le défilement actif.
            #
            # CONNECTEURS_COMPOSITION_V1
            # Les pages sont reliées par un trait fin avec un petit rond
            # au centre de chaque intervalle. Entre deux rangées, une ligne
            # de retour matérialise la continuité de lecture.

            row_layouts = []

            for row in range(visible_rows):
                row_start = row * max_per_row
                row_end = min(page_count, row_start + max_per_row)
                row_count = row_end - row_start

                if row_count <= 0:
                    continue

                row_y = pages_top + row * (row_height + row_gap)
                slot_w = (cx2 - cx1) / row_count
                base_y = row_y + large_h

                row_items = []

                for local_col, slot_index in enumerate(
                    range(row_start, row_end)
                ):
                    page_id = page_order[slot_index]
                    kind = visual_page_kind(page_id)

                    if kind == "head":
                        pw, ph = large_w, large_h
                    elif kind == "auto":
                        pw, ph = auto_w, auto_h
                    else:
                        pw, ph = normal_w, normal_h

                    center_x = cx1 + slot_w * (local_col + 0.5)
                    px1 = center_x - pw / 2
                    py1 = base_y - ph

                    row_items.append(
                        {
                            "index": page_id,
                            "slot": slot_index,
                            "display_number": slot_index + 1,
                            "kind": kind,
                            "px1": px1,
                            "py1": py1,
                            "pw": pw,
                            "ph": ph,
                            "px2": px1 + pw,
                            "base_y": base_y,
                        }
                    )

                row_layouts.append(row_items)

            connector_color = "#B8B3AB"
            connector_circle_outline = "#8E8981"

            # Traits horizontaux entre chaque page.
            for row_items in row_layouts:
                if not row_items:
                    continue

                connector_y = row_items[0]["base_y"] - 18

                for left_item, right_item in zip(
                    row_items,
                    row_items[1:],
                ):
                    line_x1 = left_item["px2"] + 5
                    line_x2 = right_item["px1"] - 5

                    if line_x2 <= line_x1:
                        continue

                    canvas.create_line(
                        line_x1,
                        connector_y,
                        line_x2,
                        connector_y,
                        fill=connector_color,
                        width=1,
                        tags="maquettage_ui",
                    )

                    circle_x = (line_x1 + line_x2) / 2
                    circle_r = 3

                    canvas.create_oval(
                        circle_x - circle_r,
                        connector_y - circle_r,
                        circle_x + circle_r,
                        connector_y + circle_r,
                        fill="#FFFEFC",
                        outline=connector_circle_outline,
                        width=1,
                        tags="maquettage_ui",
                    )

            # RETOUR_COMPOSITION_V5
            # Continuité logique : dernière page de la ligne du haut ->
            # première page de la ligne suivante, à gauche.
            # Le trajet passe entre les deux rangées et le petit rond est
            # centré sur le long segment horizontal intermédiaire.
            if len(row_layouts) >= 2:
                first_row = row_layouts[0]
                second_row = row_layouts[1]

                if first_row and second_row:
                    last_item = first_row[-1]
                    next_item = second_row[0]

                    y_top = last_item["base_y"] - 18
                    y_bottom = next_item["base_y"] - 18
                    y_mid = (y_top + y_bottom) / 2

                    start_x = last_item["px2"] + 5
                    end_x = next_item["px1"] - 5

                    # Petits segments de sortie/entrée puis grand pont central.
                    right_turn_x = min(cx2 - 10, start_x + 22)
                    left_turn_x = max(cx1 + 10, end_x - 22)

                    canvas.create_line(
                        start_x,
                        y_top,
                        right_turn_x,
                        y_top,
                        right_turn_x,
                        y_mid,
                        left_turn_x,
                        y_mid,
                        left_turn_x,
                        y_bottom,
                        end_x,
                        y_bottom,
                        fill=connector_color,
                        width=1,
                        joinstyle="round",
                        tags="maquettage_ui",
                    )

                    # Rond au milieu du pont horizontal entre les rangées.
                    circle_x = (right_turn_x + left_turn_x) / 2
                    circle_r = 3
                    canvas.create_oval(
                        circle_x - circle_r,
                        y_mid - circle_r,
                        circle_x + circle_r,
                        y_mid + circle_r,
                        fill="#FFFEFC",
                        outline=connector_circle_outline,
                        width=1,
                        tags="maquettage_ui",
                    )

            # Les vignettes sont dessinées après les connecteurs afin que
            # les traits restent visuellement derrière les pages.
            if maquettage_page_dragging and maquettage_page_drop_slot is not None:
                all_items = [
                    item
                    for current_row in row_layouts
                    for item in current_row
                ]
                if all_items:
                    drop_slot = max(0, min(page_count, maquettage_page_drop_slot))
                    if drop_slot >= page_count:
                        marker_item = all_items[-1]
                        marker_x = marker_item["px2"] + 8
                    else:
                        marker_item = next(
                            (
                                item for item in all_items
                                if item["slot"] == drop_slot
                            ),
                            all_items[-1],
                        )
                        marker_x = marker_item["px1"] - 8
                    canvas.create_line(
                        marker_x,
                        marker_item["py1"] - 5,
                        marker_x,
                        marker_item["base_y"] + 18,
                        fill="#173E70",
                        width=3,
                        capstyle="round",
                        tags="maquettage_ui",
                    )

            for row_items in row_layouts:
                for item in row_items:
                    draw_page_preview(
                        item["px1"],
                        item["py1"],
                        item["pw"],
                        item["ph"],
                        item["kind"],
                        item["index"],
                        item["display_number"],
                        item["slot"],
                    )

            # Indication visuelle du futur défilement vertical.
            if total_rows > 2:
                scroll_x = cx2 - 4
                scroll_y1 = pages_top
                scroll_y2 = min(
                    pages_bottom,
                    pages_top + 2 * row_height + row_gap,
                )

                canvas.create_line(
                    scroll_x,
                    scroll_y1,
                    scroll_x,
                    scroll_y2,
                    fill="#DDD8D1",
                    width=3,
                    tags="maquettage_ui",
                )
                thumb_h = max(
                    30,
                    (scroll_y2 - scroll_y1) * (2 / total_rows),
                )
                canvas.create_line(
                    scroll_x,
                    scroll_y1,
                    scroll_x,
                    scroll_y1 + thumb_h,
                    fill="#A9A39B",
                    width=5,
                    capstyle="round",
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
            nonlocal maquettage_page_hovered
            nonlocal maquettage_page_dragging
            nonlocal maquettage_page_drop_slot
            nonlocal maquettage_structure_hovered

            # Une page maintenue devient un glisser dès que le pointeur
            # s'écarte de quelques pixels du point d'appui.
            if maquettage_page_pressed is not None:
                if maquettage_page_press_xy is not None:
                    dx = event.x - maquettage_page_press_xy[0]
                    dy = event.y - maquettage_page_press_xy[1]
                    if dx * dx + dy * dy >= 36:
                        maquettage_page_dragging = True

                if maquettage_page_dragging:
                    new_slot = maquettage_drop_slot_at(event.x, event.y)
                    if new_slot != maquettage_page_drop_slot:
                        maquettage_page_drop_slot = new_slot
                        render()
                    canvas.configure(cursor="hand2")
                    return

            page_region = maquettage_page_at(event.x, event.y)
            page_current = (
                page_region["page_id"] if page_region is not None else None
            )

            if page_current is not None:
                changed = page_current != maquettage_page_hovered
                maquettage_page_hovered = page_current

                if maquettage_hovered is not None:
                    if maquettage_hovered != maquettage_pressed:
                        maquettage_button_state[maquettage_hovered] = "normal"
                    maquettage_hovered = None
                    changed = True

                canvas.configure(cursor="hand2")
                if changed:
                    render()
                return

            page_changed = maquettage_page_hovered is not None
            maquettage_page_hovered = None

            structure_region = maquettage_structure_at(
                event.x,
                event.y,
            )
            structure_current = (
                structure_region["index"]
                if structure_region is not None
                else None
            )

            if structure_current is not None:
                changed = (
                    structure_current
                    != maquettage_structure_hovered
                )
                maquettage_structure_hovered = structure_current

                if maquettage_hovered is not None:
                    if maquettage_hovered != maquettage_pressed:
                        maquettage_button_state[
                            maquettage_hovered
                        ] = "normal"
                    maquettage_hovered = None
                    changed = True

                canvas.configure(cursor="hand2")
                if changed or page_changed:
                    render()
                return

            structure_changed = (
                maquettage_structure_hovered is not None
            )
            maquettage_structure_hovered = None

            current = maquettage_button_at(event.x, event.y)
            previous = maquettage_hovered
            if (
                current == previous
                and not page_changed
                and not structure_changed
            ):
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
            nonlocal maquettage_hovered, maquettage_page_hovered
            nonlocal maquettage_structure_hovered

            if (
                maquettage_hovered is not None
                and maquettage_hovered != maquettage_pressed
            ):
                maquettage_button_state[maquettage_hovered] = "normal"

            maquettage_hovered = None
            maquettage_page_hovered = None
            maquettage_structure_hovered = None
            canvas.configure(cursor="arrow")
            if maquettage_page_pressed is None:
                render()

        def on_maquettage_press(event):
            nonlocal selected_index, selected_group
            nonlocal maquettage_pressed, maquettage_hovered
            nonlocal maquettage_structure_hovered
            nonlocal maquettage_page_pressed
            nonlocal maquettage_page_pressed_slot
            nonlocal maquettage_page_press_xy
            nonlocal maquettage_page_dragging
            nonlocal maquettage_page_drop_slot
            nonlocal maquettage_page_hovered

            page_region = maquettage_page_at(event.x, event.y)
            if page_region is not None:
                maquettage_page_pressed = page_region["page_id"]
                maquettage_page_pressed_slot = page_region["slot"]
                maquettage_page_press_xy = (event.x, event.y)
                maquettage_page_dragging = False
                maquettage_page_drop_slot = page_region["slot"]
                maquettage_page_hovered = page_region["page_id"]
                maquettage_pressed = None
                maquettage_hovered = None
                canvas.configure(cursor="hand2")
                render()
                return

            structure_region = maquettage_structure_at(
                event.x,
                event.y,
            )
            if structure_region is not None:
                new_index = int(structure_region["index"])
                if 0 <= new_index < len(structure_model):
                    selected_index = new_index
                    selected_group = structure_model[selected_index]
                    maquettage_structure_hovered = selected_index
                    maquettage_pressed = None
                    maquettage_hovered = None
                    canvas.configure(cursor="hand2")
                    render()
                return

            current = maquettage_button_at(event.x, event.y)
            maquettage_pressed = current
            maquettage_hovered = current

            if current is not None:
                maquettage_button_state[current] = "pressed"
                canvas.configure(cursor="hand2")
                render()

        def on_maquettage_release(event):
            nonlocal maquettage_pressed, maquettage_hovered
            nonlocal maquettage_page_pressed
            nonlocal maquettage_page_pressed_slot
            nonlocal maquettage_page_press_xy
            nonlocal maquettage_page_dragging
            nonlocal maquettage_page_drop_slot
            nonlocal maquettage_page_hovered

            if maquettage_page_pressed is not None:
                page_id = maquettage_page_pressed
                source_slot = maquettage_page_pressed_slot
                was_dragging = maquettage_page_dragging
                drop_slot = maquettage_page_drop_slot
                if was_dragging and source_slot is not None and drop_slot is not None:
                    group_key = str(selected_group["name"])
                    order = self._maquettage_page_orders.get(group_key, [])
                    if page_id in order:
                        source = order.index(page_id)
                        target = max(0, min(len(order), int(drop_slot)))
                        moving = order.pop(source)
                        if target > source:
                            target -= 1
                        target = max(0, min(len(order), target))
                        order.insert(target, moving)
                        self._maquettage_page_orders[group_key] = order
                maquettage_page_pressed = None
                maquettage_page_pressed_slot = None
                maquettage_page_press_xy = None
                maquettage_page_dragging = False
                maquettage_page_drop_slot = None
                maquettage_page_hovered = None
                canvas.configure(cursor="arrow")
                render()

                return

            pressed = maquettage_pressed
            current = maquettage_button_at(event.x, event.y)
            action = (
                maquettage_button_actions.get(pressed)
                if pressed is not None and pressed == current
                else None
            )

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
            if action is not None:
                canvas.after_idle(action)

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
