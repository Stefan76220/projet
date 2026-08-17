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

    # DEMARRAGE_ATOMIQUE_ET_NAVIGATION_STABLE_V3
    def __init__(self) -> None:
        super().__init__()

        # La fenêtre principale existe dès maintenant, mais reste totalement
        # invisible pendant sa mise à la bonne taille et le préchauffage.
        self._startup_hidden_mode = "alpha"
        try:
            self.attributes("-alpha", 0.0)
        except tk.TclError:
            self._startup_hidden_mode = "withdraw"
            self.withdraw()

        self.title("TomeLinea — Interface V2")

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

        # On demande la taille finale AVANT de construire les vues.
        # Sur Windows, zoomed correspond à la vraie zone maximisée.
        try:
            self.state("zoomed")
        except tk.TclError:
            sw = max(1180, self.winfo_screenwidth())
            sh = max(720, self.winfo_screenheight())
            self.geometry(f"{sw}x{sh}+0+0")

        self.update_idletasks()

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

        # Termine tous les Configure / redraw du premier affichage pendant
        # que la fenêtre est encore invisible.
        self.update_idletasks()
        self.update()
        self.accueil_host.tkraise()
        self.update_idletasks()

        # Une seule apparition : directement dans l'état final.
        if self._startup_hidden_mode == "alpha":
            try:
                self.attributes("-alpha", 1.0)
            except tk.TclError:
                pass
        else:
            self.deiconify()
            try:
                self.state("zoomed")
            except tk.TclError:
                pass

        self.lift()


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

    # VISUALISATION_SUPPRIMEE_REPART_ZERO_V1
    # VISUALISATION_VIERGE_RUBAN_V1
    # VISUALISATION_FOND_OUTILS_V1
    # VISUALISATION_GLOBALE_HAUT_SANS_RUBAN_V1
    # VISUALISATION_TROIS_ZONES_V1
    # NAVIGATION_PROPRE_CENTRE_CANVAS_V1
    def _build_shell(self) -> None:
        """Structure stable : Accueil et Espace Projet sont séparés."""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.app_stack = tk.Frame(self, bg=theme.WINDOW)
        self.app_stack.grid(row=0, column=0, sticky="nsew")
        self.app_stack.grid_rowconfigure(0, weight=1)
        self.app_stack.grid_columnconfigure(0, weight=1)

        # Accueil : aucun ruban, aucune modification de géométrie à l'entrée/sortie.
        self.accueil_host = tk.Frame(self.app_stack, bg=theme.WINDOW)
        self.accueil_host.grid(row=0, column=0, sticky="nsew")
        self.accueil_host.grid_rowconfigure(0, weight=1)
        self.accueil_host.grid_columnconfigure(0, weight=1)

        # Projet : ruban toujours attaché au même conteneur.
        self.project_shell = tk.Frame(self.app_stack, bg=theme.WINDOW)
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

        self.project_host = tk.Frame(self.project_shell, bg=theme.WINDOW)
        self.project_host.grid(row=1, column=0, sticky="nsew")
        self.project_host.grid_rowconfigure(0, weight=1)
        self.project_host.grid_columnconfigure(0, weight=1)

        # Compatibilité avec le reste du prototype.
        self.host = self.project_host

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
            "visualisation": "Visualisation",
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
            command=lambda: self.show_screen("visualisation"),
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
        # Accueil dans son propre conteneur plein écran.
        accueil_screen = tk.Frame(self.accueil_host, bg=theme.WINDOW)
        accueil_screen.grid(row=0, column=0, sticky="nsew")
        self._screens["accueil"] = accueil_screen
        self._build_accueil(accueil_screen)

        # L'Accueil reste devant pendant toute la préparation des bureaux.
        self.accueil_host.tkraise()

        builders = {
            "centre": self._build_centre,
            "maquettage": self._build_maquettage,
            "atelier": self._build_atelier,
            "conception": self._build_conception,
            "assemblage": self._build_assemblage,
            "verification": self._build_verification,
            "finalisation": self._build_finalisation,
            "visualisation": self._build_visualisation_vierge,
        }

        for name, builder in builders.items():
            screen = tk.Frame(self.project_host, bg=theme.WINDOW)
            screen.grid(row=0, column=0, sticky="nsew")
            self._screens[name] = screen
            builder(screen)

        # NAVIGATION_PRECHAUFFAGE_VUES_V2
        # Principe utilisé dans les interfaces à vues empilées : toutes les
        # vues sont réalisées et calculées une première fois hors écran.
        # Ainsi, le premier accès direct n'est plus un premier affichage.
        warm_order = (
            "centre",
            "maquettage",
            "atelier",
            "conception",
            "assemblage",
            "verification",
            "finalisation",
            "visualisation",
        )

        for name in warm_order:
            screen = self._screens[name]
            screen.tkraise()

            if name == "centre":
                render_centre = getattr(self, "_centre_render", None)
                if callable(render_centre):
                    render_centre()

            # Les Canvas différés (notamment Maquettage) et les widgets natifs
            # terminent ici leur premier cycle de géométrie et de dessin, tout
            # en restant cachés derrière l'Accueil.
            self._render_header_canvas()
            screen.update_idletasks()
            self.project_host.update_idletasks()
            self.project_shell.update_idletasks()
            self.update_idletasks()
            self.update()

            # L'Accueil reste explicitement au-dessus après chaque passage.
            self.accueil_host.tkraise()

        self._screens["centre"].tkraise()
        self._render_header_canvas()
        self.project_shell.update_idletasks()
        self.accueil_host.tkraise()


    def _build_visualisation_vierge(self, parent: tk.Frame) -> None:
        """Visualisation — fond + Vue globale exacte en haut + Outils sous la vue."""
        parent.configure(bg="#D8D4CD")

        PANEL = "#FFFEFC"
        INK = "#111111"
        VIOLET = "#8D70C7"
        MOUNT = "#F1EFE9"
        GRID = "#E5E1DA"

        # Fond général : directement sur la page.
        bg_canvas = tk.Canvas(
            parent,
            bg="#D8D4CD",
            bd=0,
            highlightthickness=0,
        )
        bg_canvas.place(x=0, y=0, relwidth=1.0, relheight=1.0)
        self._visualisation_bg_canvas = bg_canvas
        self._visualisation_bg_photo = None
        self._visualisation_bg_size = None

        def draw_background(_event=None):
            from PIL import ImageFilter

            width = max(parent.winfo_width(), 1180)
            height = max(parent.winfo_height(), 720)
            size = (width, height)

            if self._visualisation_bg_size != size:
                base = Image.new("RGBA", size, "#D8D4CD")
                haze = Image.new("RGBA", size, (0, 0, 0, 0))
                draw = ImageDraw.Draw(haze, "RGBA")

                draw.ellipse(
                    (-int(width * 0.18), -int(height * 0.18),
                     int(width * 0.38), int(height * 0.38)),
                    fill=(250, 247, 240, 116),
                )
                draw.ellipse(
                    (int(width * 0.67), -int(height * 0.15),
                     int(width * 1.10), int(height * 0.35)),
                    fill=(245, 243, 237, 100),
                )
                draw.ellipse(
                    (-int(width * 0.14), int(height * 0.62),
                     int(width * 0.34), int(height * 1.12)),
                    fill=(244, 239, 231, 86),
                )
                draw.ellipse(
                    (int(width * 0.72), int(height * 0.52),
                     int(width * 1.12), int(height * 1.10)),
                    fill=(101, 112, 118, 34),
                )
                draw.ellipse(
                    (-int(width * 0.12), int(height * 0.20),
                     int(width * 0.20), int(height * 0.72)),
                    fill=(113, 105, 96, 24),
                )

                haze = haze.filter(
                    ImageFilter.GaussianBlur(
                        max(28, int(min(width, height) * 0.045))
                    )
                )
                base = Image.alpha_composite(base, haze)

                details = Image.new("RGBA", size, (0, 0, 0, 0))
                d = ImageDraw.Draw(details, "RGBA")
                accent = (63, 99, 118, 28)
                for offset in (0, 15, 30):
                    d.arc(
                        (-110 - offset, 35 + offset,
                         170 + offset, 315 + offset),
                        start=278, end=82, fill=accent, width=1,
                    )
                for offset in (0, 18, 36):
                    d.arc(
                        (width - 175 - offset, height - 250 - offset,
                         width + 105 + offset, height + 30 + offset),
                        start=96, end=258, fill=accent, width=1,
                    )

                base = Image.alpha_composite(base, details).convert("RGB")
                self._visualisation_bg_photo = ImageTk.PhotoImage(base)
                self._visualisation_bg_size = size

            bg_canvas.delete("visualisation_bg")
            bg_canvas.create_image(
                0, 0,
                image=self._visualisation_bg_photo,
                anchor="nw",
                tags=("visualisation_bg",),
            )

        # Vue globale : une zone TomeLinea directe, posée sur le fond.
        # Son contenu reste le panorama validé du Maquettage.
        global_panel = tk.Canvas(
            parent,
            bg="#D8D4CD",
            highlightthickness=0,
            bd=0,
        )
        self._visualisation_global_panel = global_panel

        def _panel_points(x1, y1, x2, y2, cut=18, dx=0, dy=0):
            return [
                x1 + dx, y1 + dy,
                x2 - cut + dx, y1 + dy,
                x2 + dx, y1 + cut + dy,
                x2 + dx, y2 + dy,
                x1 + cut + dx, y2 + dy,
                x1 + dx, y2 - cut + dy,
            ]

        def draw_global_panel(_event=None):
            global_panel.delete("panel_decor")
            w = max(1, global_panel.winfo_width())
            h = max(1, global_panel.winfo_height())
            if w < 80 or h < 80:
                return
            global_panel.create_polygon(
                _panel_points(0, 0, w - 3, h - 4, dx=2, dy=4),
                fill="#BDB7AE",
                outline="",
                tags=("panel_decor",),
            )
            global_panel.create_polygon(
                _panel_points(0, 0, w - 3, h - 4),
                fill="#FFFEFC",
                outline="#D5D1CA",
                width=1,
                tags=("panel_decor",),
            )
            global_panel.create_line(
                3, 17, 3, h - 22,
                fill="#75B89E",
                width=4,
                tags=("panel_decor",),
            )
            global_panel.create_text(
                20, 17,
                text="Vue globale",
                fill=INK,
                font=("Georgia", 12, "bold"),
                anchor="nw",
                tags=("panel_decor",),
            )
            line_x1 = 128
            line_x2 = max(line_x1 + 20, w - 28)
            global_panel.create_line(
                line_x1, 28, line_x2, 28,
                fill="#A8A29A",
                width=1,
                tags=("panel_decor",),
            )
            global_panel.create_oval(
                line_x2 - 3, 25, line_x2 + 3, 31,
                fill="#FFFEFC",
                outline="#A8A29A",
                width=1,
                tags=("panel_decor",),
            )

        global_panel.bind("<Configure>", draw_global_panel)

        panorama = tk.Canvas(
            global_panel,
            bg=PANEL,
            highlightthickness=0,
            bd=0,
            xscrollincrement=18,
        )
        self._visualisation_global_canvas = panorama
        self._visualisation_global_photo_cache = {}
        self._visualisation_global_structure_cache = {}

        page_thumb_root = PROJECT_ROOT / "assets" / "page_thumbnails"
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

        def mix_hex(color_a, color_b, ratio):
            ratio = max(0.0, min(1.0, float(ratio)))

            def rgb(value):
                value = str(value).lstrip("#")
                if len(value) != 6:
                    return (128, 128, 128)
                try:
                    return tuple(
                        int(value[index:index + 2], 16)
                        for index in (0, 2, 4)
                    )
                except Exception:
                    return (128, 128, 128)

            a = rgb(color_a)
            b = rgb(color_b)
            mixed = tuple(
                int(round(a[index] * (1.0 - ratio) + b[index] * ratio))
                for index in range(3)
            )
            return "#{:02X}{:02X}{:02X}".format(*mixed)

        def polygon_points(x1, y1, x2, y2, cut=16, dx=0, dy=0):
            return [
                x1 + dx, y1 + dy,
                x2 - cut + dx, y1 + dy,
                x2 + dx, y1 + cut + dy,
                x2 + dx, y2 + dy,
                x1 + cut + dx, y2 + dy,
                x1 + dx, y2 - cut + dy,
            ]

        def rounded(canvas, x1, y1, x2, y2, radius, **kwargs):
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

        def normalized_type_name(page):
            for key in ("type_name", "page_type", "type", "kind"):
                value = page.get(key)
                if value:
                    return str(value).strip()
            return "Page courante"

        def thumbnail_path_for_type(type_name):
            low = str(type_name).strip().lower()
            aliases = {
                "couverture": "type_page_couverture.png",
                "2e de couverture": "type_page_deuxieme_couverture.png",
                "deuxième de couverture": "type_page_deuxieme_couverture.png",
                "deuxieme de couverture": "type_page_deuxieme_couverture.png",
                "page de titre": "type_page_titre.png",
                "titre": "type_page_titre.png",
                "avant-propos": "type_page_avant_propos.png",
                "avant propos": "type_page_avant_propos.png",
                "sommaire": "type_page_sommaire.png",
                "chapitre": "type_page_chapitre.png",
                "tête de chapitre": "type_page_chapitre.png",
                "tete de chapitre": "type_page_chapitre.png",
                "tête de partie": "type_page_chapitre.png",
                "tete de partie": "type_page_chapitre.png",
                "texte": "type_page_texte.png",
                "page courante": "type_page_texte.png",
                "page commune": "type_page_texte.png",
                "fiche": "type_page_fiche.png",
                "illustration": "type_page_illustration.png",
                "transition": "type_page_transition.png",
                "conclusion": "type_page_conclusion.png",
                "page blanche": "type_page_blanche.png",
                "3e de couverture": "type_page_troisieme_couverture.png",
                "troisième de couverture": "type_page_troisieme_couverture.png",
                "troisieme de couverture": "type_page_troisieme_couverture.png",
                "4e de couverture": "type_page_quatrieme_couverture.png",
                "quatrième de couverture": "type_page_quatrieme_couverture.png",
                "quatrieme de couverture": "type_page_quatrieme_couverture.png",
                "personnalisée": "type_page_personnalisee.png",
                "personnalisee": "type_page_personnalisee.png",
                "page auto": "type_page_sommaire.png",
            }

            filename = aliases.get(low)
            if filename:
                candidate = page_thumb_root / filename
                if candidate.exists():
                    return candidate

            for item in getattr(self, "_maquettage_custom_page_types", []):
                if not isinstance(item, dict):
                    continue
                if str(item.get("name", "")).strip().lower() == low:
                    image_value = str(item.get("image", "") or "").strip()
                    if image_value:
                        candidate = Path(image_value)
                        if candidate.exists():
                            return candidate

            fallback = page_thumb_root / "type_page_texte.png"
            return fallback if fallback.exists() else None

        def page_photo(page, width, height):
            type_name = normalized_type_name(page)
            path = thumbnail_path_for_type(type_name)
            key = (
                str(path) if path else "",
                int(width),
                int(height),
            )
            if key in self._visualisation_global_photo_cache:
                return self._visualisation_global_photo_cache[key]

            photo = None
            if path is not None:
                try:
                    image = Image.open(path).convert("RGBA")
                    image = image.resize(
                        (max(1, int(width)), max(1, int(height))),
                        Image.Resampling.LANCZOS,
                    )
                    photo = ImageTk.PhotoImage(image)
                except Exception:
                    photo = None

            self._visualisation_global_photo_cache[key] = photo
            return photo

        def structure_photo(path, max_w, max_h, *, green_flag=False):
            key = (
                str(path),
                int(max_w),
                int(max_h),
                bool(green_flag),
            )
            cached = self._visualisation_global_structure_cache.get(key)
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
                                luminosity = max(0.52, min(1.18, r / 205.0))
                                pixels[xx, yy] = (
                                    int(max(0, min(255, 83 * luminosity))),
                                    int(max(0, min(255, 151 * luminosity))),
                                    int(max(0, min(255, 105 * luminosity))),
                                    a,
                                )

                image.thumbnail(
                    (max_w, max_h),
                    Image.Resampling.LANCZOS,
                )
                photo = ImageTk.PhotoImage(image)
                self._visualisation_global_structure_cache[key] = photo
                return photo
            except Exception:
                return None

        def page_visual_size(page):
            low = normalized_type_name(page).lower()
            if low in (
                "couverture",
                "4e de couverture",
                "tête de partie",
                "tete de partie",
                "tête de chapitre",
                "tete de chapitre",
                "chapitre",
            ):
                return 84, int(84 * 1.40), "large"

            if low == "page auto":
                return 58, int(58 * 1.40), "auto"

            return 68, int(68 * 1.40), "normal"

        def draw_structure_tile(
            canvas,
            cx,
            icon_anchor_y,
            *,
            book=False,
            accent=VIOLET,
        ):
            tile_w = 98 if book else 86
            tile_h = 62 if book else 58
            x1 = cx - tile_w / 2
            x2 = cx + tile_w / 2
            y2 = icon_anchor_y + 7
            y1 = y2 - tile_h
            cut = 8

            def points(dx=0, dy=0):
                return [
                    x1 + dx, y1 + dy,
                    x2 - cut + dx, y1 + dy,
                    x2 + dx, y1 + cut + dy,
                    x2 + dx, y2 + dy,
                    x1 + cut + dx, y2 + dy,
                    x1 + dx, y2 - cut + dy,
                ]

            canvas.create_polygon(
                points(2, 3),
                fill="#D8D4CD",
                outline="",
            )

            if book:
                fill = mix_hex(accent, "#FFFFFF", 0.86)
                outline = mix_hex(accent, "#BDB8B0", 0.62)
                grid = mix_hex(accent, "#FFFFFF", 0.91)
            else:
                fill = "#F4F1E9"
                outline = "#D3CEC5"
                grid = "#E0E4E0"

            canvas.create_polygon(
                points(),
                fill=fill,
                outline=outline,
                width=1,
            )
            canvas.create_line(
                x1 + tile_w * 0.34,
                y1 + 8,
                x1 + tile_w * 0.34,
                y2 - 8,
                fill=grid,
                width=1,
            )
            canvas.create_line(
                x1 + tile_w * 0.67,
                y1 + 8,
                x1 + tile_w * 0.67,
                y2 - 8,
                fill=grid,
                width=1,
            )
            canvas.create_line(
                x1 + 8,
                y1 + tile_h * 0.5,
                x2 - 8,
                y1 + tile_h * 0.5,
                fill=grid,
                width=1,
            )

        def draw_global(_event=None):
            panorama.delete("all")

            pages = self._tomelinea_collect_book_pages()
            model = getattr(self, "_maquettage_structure_model", None) or [
                {"name": "Début", "pages": 3, "color": "#75B89E"},
                {"name": "Partie 1", "pages": 12, "color": "#8D70C7"},
                {"name": "Partie 2", "pages": None, "color": "#72AFCB"},
                {"name": "Partie 3", "pages": None, "color": "#E28A6D"},
                {"name": "Fin", "pages": 3, "color": "#75B89E"},
            ]

            pages_by_group = {}
            for page in pages:
                pages_by_group.setdefault(
                    str(page.get("group", "Partie")),
                    [],
                ).append(page)

            view_w = max(900, panorama.winfo_width())
            view_h = max(245, panorama.winfo_height())

            page_gap = 24
            group_gap = 70
            left_pad = 72
            right_pad = 72

            marker_y = int(view_h * 0.22)
            guide_y = int(view_h * 0.34)
            page_baseline = int(view_h * 0.68)

            groups_layout = []
            cursor_x = left_pad

            for group_index, group in enumerate(model):
                group_name = str(group.get("name", "Partie"))
                group_pages = pages_by_group.get(group_name, [])
                start_x = cursor_x
                layouts = []

                for page_index, page in enumerate(group_pages):
                    pw, ph, size_kind = page_visual_size(page)
                    layouts.append({
                        "page": page,
                        "x": cursor_x,
                        "w": pw,
                        "h": ph,
                        "size_kind": size_kind,
                    })
                    cursor_x += pw
                    if page_index < len(group_pages) - 1:
                        cursor_x += page_gap

                end_x = cursor_x if layouts else start_x + 44
                if not layouts:
                    cursor_x = end_x

                groups_layout.append({
                    "index": group_index,
                    "group": group,
                    "name": group_name,
                    "layouts": layouts,
                    "start_x": start_x,
                    "end_x": end_x,
                })

                if group_index < len(model) - 1:
                    cursor_x += group_gap

            natural_total = cursor_x + right_pad
            content_offset = (
                (view_w - natural_total) / 2
                if natural_total < view_w
                else 0
            )

            if content_offset > 0:
                for group_data in groups_layout:
                    group_data["start_x"] += content_offset
                    group_data["end_x"] += content_offset
                    for layout in group_data["layouts"]:
                        layout["x"] += content_offset
                natural_total = view_w

            band_x1 = 18
            band_x2 = max(view_w - 18, natural_total - 18)
            band_y1 = max(12, marker_y - 75)
            band_y2 = min(view_h - 20, page_baseline + 95)

            panorama.create_polygon(
                polygon_points(
                    band_x1, band_y1, band_x2, band_y2,
                    cut=14, dx=2, dy=4,
                ),
                fill="#D7D2CA",
                outline="",
            )
            panorama.create_polygon(
                polygon_points(
                    band_x1, band_y1, band_x2, band_y2,
                    cut=14,
                ),
                fill=MOUNT,
                outline="#D8D3CB",
                width=1,
            )

            gx = band_x1 + 38
            while gx < band_x2 - 20:
                panorama.create_line(
                    gx,
                    band_y1 + 14,
                    gx,
                    band_y2 - 14,
                    fill=GRID,
                    width=1,
                )
                gx += 96

            gy = band_y1 + 28
            while gy < band_y2 - 16:
                panorama.create_line(
                    band_x1 + 14,
                    gy,
                    band_x2 - 14,
                    gy,
                    fill=GRID,
                    width=1,
                )
                gy += 44

            previous_box = None

            for group_data in groups_layout:
                index = group_data["index"]
                group = group_data["group"]
                layouts = group_data["layouts"]
                accent = str(group.get("color", VIOLET) or VIOLET)

                if layouts:
                    marker_x = layouts[0]["x"]
                else:
                    marker_x = (
                        group_data["start_x"] + group_data["end_x"]
                    ) / 2

                is_start = index == 0
                is_end = index == len(groups_layout) - 1

                if is_start:
                    marker_center = marker_x + 10
                    icon_path = (
                        ribbon_flag_path
                        if ribbon_flag_path.exists()
                        else fallback_flag_path
                    )
                    photo = structure_photo(
                        icon_path,
                        56,
                        48,
                        green_flag=True,
                    )
                    draw_structure_tile(
                        panorama,
                        marker_center,
                        marker_y + 4,
                        book=False,
                        accent=accent,
                    )
                elif is_end:
                    marker_center = (
                        group_data["end_x"] - 10
                        if layouts
                        else marker_x
                    )
                    icon_path = (
                        ribbon_flag_path
                        if ribbon_flag_path.exists()
                        else fallback_flag_path
                    )
                    photo = structure_photo(
                        icon_path,
                        56,
                        48,
                        green_flag=False,
                    )
                    draw_structure_tile(
                        panorama,
                        marker_center,
                        marker_y + 4,
                        book=False,
                        accent=accent,
                    )
                else:
                    marker_center = marker_x
                    icon_path = book_icon_paths[
                        (index - 1) % len(book_icon_paths)
                    ]
                    photo = structure_photo(
                        icon_path,
                        70,
                        50,
                    )
                    draw_structure_tile(
                        panorama,
                        marker_center,
                        marker_y + 4,
                        book=True,
                        accent=accent,
                    )

                if photo is not None:
                    panorama.create_image(
                        marker_center,
                        marker_y,
                        image=photo,
                        anchor="s",
                    )

                diamond_r = 4
                panorama.create_polygon(
                    marker_center,
                    guide_y - diamond_r,
                    marker_center + diamond_r,
                    guide_y,
                    marker_center,
                    guide_y + diamond_r,
                    marker_center - diamond_r,
                    guide_y,
                    fill="#FFFFFF",
                    outline="#111111",
                    width=1,
                )
                panorama.create_text(
                    marker_center,
                    guide_y + 21,
                    text=group_data["name"],
                    fill=INK,
                    font=("Georgia", 9, "bold"),
                    anchor="center",
                )
                panorama.create_line(
                    marker_center,
                    guide_y + 33,
                    marker_center,
                    page_baseline - 72,
                    fill="#D8D2CA",
                    width=1,
                    dash=(2, 3),
                )

                for layout in layouts:
                    page = layout["page"]
                    px = layout["x"]
                    pw = layout["w"]
                    ph = layout["h"]
                    py = page_baseline - ph / 2

                    rounded(
                        panorama,
                        px + 2,
                        py + 4,
                        px + pw + 2,
                        py + ph + 4,
                        7,
                        fill="#D0CBC3",
                        outline="",
                    )
                    rounded(
                        panorama,
                        px,
                        py,
                        px + pw,
                        py + ph,
                        7,
                        fill="#FFFEFB",
                        outline="#CDC8C0",
                        width=1,
                    )

                    photo_page = page_photo(
                        page,
                        pw - 4,
                        ph - 4,
                    )
                    if photo_page is not None:
                        panorama.create_image(
                            px + pw / 2,
                            py + ph / 2,
                            image=photo_page,
                            anchor="center",
                        )
                    else:
                        panorama.create_text(
                            px + pw / 2,
                            py + ph / 2,
                            text=normalized_type_name(page),
                            fill="#5E666D",
                            font=("Segoe UI", 6),
                            justify="center",
                        )

                    box = {
                        "x1": px,
                        "x2": px + pw,
                        "y1": py,
                        "y2": py + ph,
                    }

                    if previous_box is not None:
                        x1 = previous_box["x2"] + 5
                        x2 = box["x1"] - 5
                        if x2 > x1:
                            yy = page_baseline
                            panorama.create_line(
                                x1,
                                yy,
                                x2,
                                yy,
                                fill="#B7B1A8",
                                width=1,
                            )
                            dot = (x1 + x2) / 2
                            panorama.create_oval(
                                dot - 3,
                                yy - 3,
                                dot + 3,
                                yy + 3,
                                fill=MOUNT,
                                outline="#9F988F",
                                width=1,
                            )

                    previous_box = box

            panorama.configure(
                scrollregion=(
                    0,
                    0,
                    max(view_w, natural_total),
                    view_h,
                )
            )

        pan_state = {
            "active": False,
            "moved": False,
            "press_x": 0,
            "press_y": 0,
            "y_origin": 0.0,
        }

        def panorama_pan_press(event):
            pan_state["active"] = True
            pan_state["moved"] = False
            pan_state["press_x"] = event.x
            pan_state["press_y"] = event.y
            try:
                pan_state["y_origin"] = float(panorama.yview()[0])
            except Exception:
                pan_state["y_origin"] = 0.0

            panorama.scan_mark(event.x, event.y)
            panorama.configure(cursor="hand2")

        def panorama_pan_drag(event):
            if not pan_state["active"]:
                return None

            if abs(event.x - pan_state["press_x"]) >= 3:
                pan_state["moved"] = True

            panorama.scan_dragto(
                event.x,
                pan_state["press_y"],
                gain=1,
            )
            try:
                panorama.yview_moveto(pan_state["y_origin"])
            except Exception:
                pass
            return "break"

        def panorama_pan_release(_event=None):
            if not pan_state["active"]:
                return
            pan_state["active"] = False
            panorama.configure(cursor="arrow")

        def global_wheel(event):
            if getattr(event, "delta", 0):
                panorama.xview_scroll(
                    -3 if event.delta > 0 else 3,
                    "units",
                )
                return "break"
            return None

        panorama.bind("<Configure>", draw_global)
        panorama.bind("<ButtonPress-1>", panorama_pan_press)
        panorama.bind("<B1-Motion>", panorama_pan_drag)
        panorama.bind("<ButtonRelease-1>", panorama_pan_release)
        panorama.bind(
            "<Leave>",
            lambda _e: (
                panorama_pan_release()
                if pan_state["active"]
                else None
            ),
        )
        panorama.bind("<MouseWheel>", global_wheel)

        self._visualisation_global_render = draw_global

        # ----------------------------------------------------------
        # Vue feuilletée : contenu et réactions repris du Maquettage.
        # ----------------------------------------------------------
        feuillet_panel = tk.Canvas(
            parent,
            bg="#D8D4CD",
            highlightthickness=0,
            bd=0,
        )
        self._visualisation_feuillet_panel = feuillet_panel

        def draw_feuillet_panel(_event=None):
            feuillet_panel.delete("panel_decor")
            w = max(1, feuillet_panel.winfo_width())
            h = max(1, feuillet_panel.winfo_height())
            if w < 80 or h < 80:
                return
            feuillet_panel.create_polygon(
                _panel_points(0, 0, w - 3, h - 4, dx=2, dy=4),
                fill="#BDB7AE",
                outline="",
                tags=("panel_decor",),
            )
            feuillet_panel.create_polygon(
                _panel_points(0, 0, w - 3, h - 4),
                fill="#FFFEFC",
                outline="#D5D1CA",
                width=1,
                tags=("panel_decor",),
            )
            feuillet_panel.create_line(
                3, 17, 3, h - 22,
                fill="#8D70C7",
                width=4,
                tags=("panel_decor",),
            )
            feuillet_panel.create_text(
                20, 17,
                text="Vue feuilletée",
                fill=INK,
                font=("Georgia", 12, "bold"),
                anchor="nw",
                tags=("panel_decor",),
            )
            line_x1 = 145
            line_x2 = max(line_x1 + 20, w - 28)
            feuillet_panel.create_line(
                line_x1, 28, line_x2, 28,
                fill="#A8A29A",
                width=1,
                tags=("panel_decor",),
            )
            feuillet_panel.create_oval(
                line_x2 - 3, 25, line_x2 + 3, 31,
                fill="#FFFEFC",
                outline="#A8A29A",
                width=1,
                tags=("panel_decor",),
            )

        feuillet_panel.bind("<Configure>", draw_feuillet_panel)

        book_canvas = tk.Canvas(
            feuillet_panel,
            bg=PANEL,
            highlightthickness=0,
            bd=0,
        )
        self._visualisation_book_canvas = book_canvas
        self._visualisation_book_source_cache = {}
        self._visualisation_book_turn_frames = []
        self._visualisation_book_support_cache = {}

        spread_left = [-1]
        flip_state = {
            "active": False,
            "after": None,
            "direction": 0,
        }

        def page_source_image(page):
            if page is None:
                return None
            type_name = normalized_type_name(page)
            path = thumbnail_path_for_type(type_name)
            key = str(path) if path is not None else ""
            if key in self._visualisation_book_source_cache:
                return self._visualisation_book_source_cache[key]
            image = None
            if path is not None:
                try:
                    image = Image.open(path).convert("RGBA")
                except Exception:
                    image = None
            self._visualisation_book_source_cache[key] = image
            return image

        def animated_page_photo(page, width, height, *, shade=0.0):
            width = max(2, int(width))
            height = max(2, int(height))
            source = page_source_image(page)
            if source is None:
                image = Image.new(
                    "RGBA",
                    (width, height),
                    (245, 242, 235, 255),
                )
            else:
                image = source.resize(
                    (width, height),
                    Image.Resampling.BILINEAR,
                )
            shade = max(0.0, min(0.38, float(shade)))
            if shade > 0:
                veil = Image.new(
                    "RGBA",
                    image.size,
                    (92, 84, 76, 255),
                )
                image = Image.blend(image, veil, shade)
            photo = ImageTk.PhotoImage(image)
            self._visualisation_book_turn_frames = [photo]
            return photo

        def draw_large_page(canvas, page, x1, y1, x2, y2, *, blank=False):
            if blank or page is None:
                canvas.create_rectangle(
                    x1 + 3, y1 + 5, x2 + 3, y2 + 5,
                    fill="#B9B1A8", outline="",
                )
                canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill="#EEEAE3", outline="#CFC8BF", width=1,
                )
                return

            canvas.create_rectangle(
                x1 + 4, y1 + 6, x2 + 4, y2 + 6,
                fill="#A69D93", outline="",
            )
            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill="#FFFEFB", outline="#C9C2BA", width=1,
            )
            photo = page_photo(
                page,
                max(1, int(x2 - x1 - 8)),
                max(1, int(y2 - y1 - 8)),
            )
            if photo is not None:
                canvas.create_image(
                    (x1 + x2) / 2,
                    (y1 + y2) / 2,
                    image=photo,
                    anchor="center",
                )
            else:
                canvas.create_text(
                    (x1 + x2) / 2,
                    (y1 + y2) / 2,
                    text=normalized_type_name(page),
                    fill="#4E565D",
                    font=("Georgia", 13, "bold"),
                    justify="center",
                )

        def book_geometry():
            # Même proportion de livre que le Maquettage, mais dimensionnée
            # dans l'espace réellement disponible de Visualisation.
            w = max(500, book_canvas.winfo_width())
            h = max(260, book_canvas.winfo_height())
            gap = 15

            by_height = max(180, h - 78)
            by_width = max(180, ((w - 120 - gap) / 2) * 1.40)
            page_h = max(180, min(520, by_height, by_width))
            page_w = page_h / 1.40
            total_w = page_w * 2 + gap

            left_x = (w - total_w) / 2
            right_x = left_x + page_w + gap
            y1 = (h - page_h) / 2 + 2
            gutter_x = left_x + page_w + gap / 2

            return {
                "w": w,
                "h": h,
                "page_w": page_w,
                "page_h": page_h,
                "gap": gap,
                "total_w": total_w,
                "left_x": left_x,
                "right_x": right_x,
                "y1": y1,
                "gutter_x": gutter_x,
            }

        def support_photo(width, height):
            from PIL import ImageFilter as _ImageFilter

            width = max(220, int(width))
            height = max(180, int(height))
            key = (width, height)
            cached = self._visualisation_book_support_cache.get(key)
            if cached is not None:
                return cached

            scale = 2
            sw = width * scale
            sh = height * scale
            image = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))

            shadow = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
            sd = ImageDraw.Draw(shadow)
            pad = 22 * scale
            sd.rounded_rectangle(
                (pad, pad + 8 * scale, sw - pad, sh - pad + 5 * scale),
                radius=18 * scale,
                fill=(95, 82, 68, 70),
            )
            shadow = shadow.filter(_ImageFilter.GaussianBlur(12 * scale))
            image.alpha_composite(shadow)

            plate = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
            pd = ImageDraw.Draw(plate)
            outer = (
                20 * scale,
                16 * scale,
                sw - 20 * scale,
                sh - 25 * scale,
            )
            pd.rounded_rectangle(
                outer,
                radius=17 * scale,
                fill=(223, 214, 202, 255),
                outline=(194, 183, 169, 255),
                width=1 * scale,
            )

            bevel_colors = (
                (226, 217, 205, 255),
                (232, 224, 213, 255),
                (238, 231, 221, 255),
                (244, 239, 232, 255),
            )
            for i, color in enumerate(bevel_colors, start=1):
                inset = (20 + i * 3) * scale
                pd.rounded_rectangle(
                    (
                        inset,
                        (16 + i * 3) * scale,
                        sw - inset,
                        sh - (25 + i * 3) * scale,
                    ),
                    radius=max(5, (17 - i * 2) * scale),
                    fill=color,
                )

            texture = Image.effect_noise((sw, sh), 10.0).convert("L")
            texture = texture.point(
                lambda value: int(232 + (value - 128) * 0.08)
            )
            texture_rgba = Image.merge(
                "RGBA",
                (
                    texture,
                    texture,
                    texture,
                    Image.new("L", (sw, sh), 30),
                ),
            )
            mask = Image.new("L", (sw, sh), 0)
            md = ImageDraw.Draw(mask)
            md.rounded_rectangle(
                (
                    30 * scale,
                    26 * scale,
                    sw - 30 * scale,
                    sh - 35 * scale,
                ),
                radius=12 * scale,
                fill=255,
            )
            texture_rgba.putalpha(
                Image.eval(mask, lambda a: int(a * 0.12))
            )
            plate.alpha_composite(texture_rgba)
            pd = ImageDraw.Draw(plate)

            pd.rounded_rectangle(
                (
                    38 * scale,
                    34 * scale,
                    sw - 38 * scale,
                    sh - 48 * scale,
                ),
                radius=10 * scale,
                fill=(248, 245, 239, 236),
                outline=(236, 230, 221, 255),
                width=1 * scale,
            )
            pd.line(
                (
                    52 * scale,
                    42 * scale,
                    sw - 52 * scale,
                    42 * scale,
                ),
                fill=(255, 255, 255, 210),
                width=1 * scale,
            )

            lip_y = sh - 52 * scale
            pd.rounded_rectangle(
                (
                    48 * scale,
                    lip_y,
                    sw - 48 * scale,
                    lip_y + 16 * scale,
                ),
                radius=5 * scale,
                fill=(211, 200, 186, 255),
                outline=(190, 178, 163, 255),
                width=1 * scale,
            )
            pd.line(
                (
                    58 * scale,
                    lip_y + 2 * scale,
                    sw - 58 * scale,
                    lip_y + 2 * scale,
                ),
                fill=(252, 249, 244, 220),
                width=1 * scale,
            )

            stop_y = sh - 78 * scale
            stop_w = 55 * scale
            stop_h = 13 * scale
            for center_x in (int(sw * 0.29), int(sw * 0.71)):
                pd.rounded_rectangle(
                    (
                        center_x - stop_w // 2,
                        stop_y,
                        center_x + stop_w // 2,
                        stop_y + stop_h,
                    ),
                    radius=4 * scale,
                    fill=(218, 208, 195, 255),
                    outline=(195, 183, 168, 255),
                    width=1 * scale,
                )
                pd.line(
                    (
                        center_x - stop_w // 2 + 8 * scale,
                        stop_y + 2 * scale,
                        center_x + stop_w // 2 - 8 * scale,
                        stop_y + 2 * scale,
                    ),
                    fill=(252, 250, 246, 235),
                    width=1 * scale,
                )

            center_x = sw // 2
            pd.rounded_rectangle(
                (
                    center_x - 9 * scale,
                    47 * scale,
                    center_x + 9 * scale,
                    sh - 72 * scale,
                ),
                radius=5 * scale,
                fill=(226, 218, 207, 180),
                outline=(205, 195, 182, 190),
                width=1 * scale,
            )
            image.alpha_composite(plate)
            image = image.resize((width, height), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(image)
            self._visualisation_book_support_cache[key] = photo
            return photo

        def draw_book_background(geometry):
            w = geometry["w"]
            h = geometry["h"]
            left_x = geometry["left_x"]
            right_x = geometry["right_x"]
            y1 = geometry["y1"]
            page_w = geometry["page_w"]
            page_h = geometry["page_h"]

            margin = 20
            x1 = margin
            y_top = 10
            x2 = w - margin
            y2 = h - 12

            book_canvas.create_polygon(
                polygon_points(x1, y_top, x2, y2, cut=14, dx=2, dy=4),
                fill="#D7D2CA",
                outline="",
            )
            book_canvas.create_polygon(
                polygon_points(x1, y_top, x2, y2, cut=14),
                fill=MOUNT,
                outline="#D8D3CB",
                width=1,
            )

            gx = x1 + 38
            while gx < x2 - 20:
                book_canvas.create_line(
                    gx, y_top + 14, gx, y2 - 14,
                    fill=GRID, width=1,
                )
                gx += 96
            gy = y_top + 28
            while gy < y2 - 16:
                book_canvas.create_line(
                    x1 + 14, gy, x2 - 14, gy,
                    fill=GRID, width=1,
                )
                gy += 44

            stand_x = left_x - 42
            stand_y = y1 - 28
            stand_w = int((right_x + page_w + 42) - stand_x)
            stand_h = int(page_h + 70)
            photo = support_photo(stand_w, stand_h)
            book_canvas.create_image(
                stand_x, stand_y, image=photo, anchor="nw"
            )
            book_canvas.create_oval(
                left_x + 24,
                y1 + page_h - 7,
                right_x + page_w - 24,
                y1 + page_h + 13,
                fill="#D9D1C6",
                outline="",
            )

        def draw_gutter(geometry):
            gutter_x = geometry["gutter_x"]
            y1 = geometry["y1"]
            page_h = geometry["page_h"]
            book_canvas.create_line(
                gutter_x, y1 + 4, gutter_x, y1 + page_h - 4,
                fill="#6F655C", width=3,
            )
            book_canvas.create_line(
                gutter_x - 5, y1 + 8,
                gutter_x - 2, y1 + page_h - 8,
                fill="#B7AEA5", width=1,
            )
            book_canvas.create_line(
                gutter_x + 2, y1 + 8,
                gutter_x + 5, y1 + page_h - 8,
                fill="#B7AEA5", width=1,
            )

        def current_pages():
            return self._tomelinea_collect_book_pages()

        def page_at(index, pages=None):
            if pages is None:
                pages = current_pages()
            if 0 <= index < len(pages):
                return pages[index]
            return None

        def draw_spread(left_page, right_page):
            geometry = book_geometry()
            draw_book_background(geometry)
            left_x = geometry["left_x"]
            right_x = geometry["right_x"]
            y1 = geometry["y1"]
            page_w = geometry["page_w"]
            page_h = geometry["page_h"]
            draw_large_page(
                book_canvas, left_page,
                left_x, y1,
                left_x + page_w, y1 + page_h,
                blank=left_page is None,
            )
            draw_large_page(
                book_canvas, right_page,
                right_x, y1,
                right_x + page_w, y1 + page_h,
                blank=right_page is None,
            )
            draw_gutter(geometry)
            return geometry

        def render_book(_event=None):
            if flip_state["active"]:
                return
            pages = current_pages()
            if spread_left[0] > len(pages) - 1:
                spread_left[0] = max(-1, len(pages) - 2)
                if spread_left[0] % 2 == 0:
                    spread_left[0] -= 1
            book_canvas.delete("all")
            li = spread_left[0]
            draw_spread(
                page_at(li, pages),
                page_at(li + 1, pages),
            )

        def draw_turning_page(
            page, x1, y1, x2, y2, *, shade=0.0, edge_x=None
        ):
            width = max(1.0, x2 - x1)
            height = max(1.0, y2 - y1)
            if width <= 3:
                xx = edge_x if edge_x is not None else (x1 + x2) / 2
                book_canvas.create_line(
                    xx, y1 + 2, xx, y2 - 2,
                    fill="#6B6259", width=3,
                )
                return
            book_canvas.create_rectangle(
                x1 + 3, y1 + 5, x2 + 3, y2 + 5,
                fill="#81786F", outline="",
            )
            book_canvas.create_rectangle(
                x1, y1, x2, y2,
                fill="#FFFEFB", outline="#AFA79F", width=1,
            )
            photo = animated_page_photo(
                page,
                max(2, int(width - 4)),
                max(2, int(height - 4)),
                shade=shade,
            )
            book_canvas.create_image(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                image=photo,
                anchor="center",
            )
            if edge_x is not None:
                for offset, color in (
                    (0, "#625A52"),
                    (2, "#8A8178"),
                    (4, "#B0A79D"),
                ):
                    book_canvas.create_line(
                        edge_x + offset,
                        y1 + 2,
                        edge_x + offset,
                        y2 - 2,
                        fill=color,
                        width=1,
                    )

        def animate_page_turn(direction):
            if flip_state["active"]:
                return

            pages = current_pages()
            current = spread_left[0]
            if direction > 0:
                target = current + 2
                if target > len(pages) - 1:
                    return
            else:
                target = current - 2
                if target < -1:
                    return

            current_left = page_at(current, pages)
            current_right = page_at(current + 1, pages)
            target_left = page_at(target, pages)
            target_right = page_at(target + 1, pages)

            flip_state["active"] = True
            flip_state["direction"] = 1 if direction > 0 else -1
            if flip_state["after"] is not None:
                try:
                    parent.after_cancel(flip_state["after"])
                except Exception:
                    pass
                flip_state["after"] = None

            frames = 22
            frame_ms = 15

            def frame(index):
                try:
                    if not parent.winfo_exists():
                        return
                except Exception:
                    return

                t = index / frames
                eased = t * t * t * (t * (t * 6.0 - 15.0) + 10.0)
                book_canvas.delete("all")
                geometry = book_geometry()
                left_x = geometry["left_x"]
                right_x = geometry["right_x"]
                y1 = geometry["y1"]
                page_w = geometry["page_w"]
                page_h = geometry["page_h"]
                gutter_left = left_x + page_w
                gutter_right = right_x

                if direction > 0:
                    if eased < 0.5:
                        phase = eased / 0.5
                        draw_spread(current_left, target_right)
                        fraction = max(0.0, 1.0 - phase)
                        moving_w = page_w * fraction
                        bend = int(13 * (1.0 - fraction))
                        x1 = gutter_right
                        x2 = gutter_right + moving_w
                        draw_turning_page(
                            current_right,
                            x1,
                            y1 + bend,
                            x2,
                            y1 + page_h - bend,
                            shade=0.20 * (1.0 - fraction),
                            edge_x=x2,
                        )
                    else:
                        phase = (eased - 0.5) / 0.5
                        draw_spread(current_left, target_right)
                        fraction = max(0.0, min(1.0, phase))
                        moving_w = page_w * fraction
                        bend = int(13 * (1.0 - fraction))
                        x2 = gutter_left
                        x1 = gutter_left - moving_w
                        draw_turning_page(
                            target_left,
                            x1,
                            y1 + bend,
                            x2,
                            y1 + page_h - bend,
                            shade=0.20 * (1.0 - fraction),
                            edge_x=x1,
                        )
                else:
                    if eased < 0.5:
                        phase = eased / 0.5
                        draw_spread(target_left, current_right)
                        fraction = max(0.0, 1.0 - phase)
                        moving_w = page_w * fraction
                        bend = int(13 * (1.0 - fraction))
                        x2 = gutter_left
                        x1 = gutter_left - moving_w
                        draw_turning_page(
                            current_left,
                            x1,
                            y1 + bend,
                            x2,
                            y1 + page_h - bend,
                            shade=0.20 * (1.0 - fraction),
                            edge_x=x1,
                        )
                    else:
                        phase = (eased - 0.5) / 0.5
                        draw_spread(target_left, current_right)
                        fraction = max(0.0, min(1.0, phase))
                        moving_w = page_w * fraction
                        bend = int(13 * (1.0 - fraction))
                        x1 = gutter_right
                        x2 = gutter_right + moving_w
                        draw_turning_page(
                            target_right,
                            x1,
                            y1 + bend,
                            x2,
                            y1 + page_h - bend,
                            shade=0.20 * (1.0 - fraction),
                            edge_x=x2,
                        )

                shadow_strength = 1.0 - abs(eased - 0.5) * 2.0
                shadow_strength = max(0.0, min(1.0, shadow_strength))
                gutter = geometry["gutter_x"]
                for offset, color in (
                    (0, "#5F564E"),
                    (3, "#7A7067"),
                    (6, "#A59B92"),
                ):
                    book_canvas.create_line(
                        gutter + (offset if direction > 0 else -offset),
                        y1 + 8,
                        gutter + (offset if direction > 0 else -offset),
                        y1 + page_h - 8,
                        fill=color,
                        width=2 if shadow_strength > 0.45 else 1,
                    )

                if index < frames:
                    flip_state["after"] = parent.after(
                        frame_ms,
                        lambda: frame(index + 1),
                    )
                else:
                    spread_left[0] = target
                    flip_state["active"] = False
                    flip_state["direction"] = 0
                    flip_state["after"] = None
                    self._visualisation_book_turn_frames = []
                    render_book()

            frame(0)

        def turn(step):
            animate_page_turn(1 if step > 0 else -1)

        def book_click(event):
            if flip_state["active"]:
                return
            book_canvas.focus_set()
            w = max(1, book_canvas.winfo_width())
            if event.x >= w / 2:
                turn(1)
            else:
                turn(-1)

        def book_wheel(event):
            if getattr(event, "delta", 0):
                turn(1 if event.delta < 0 else -1)
                return "break"
            return None

        book_canvas.bind("<Configure>", render_book)
        book_canvas.bind("<Button-1>", book_click)
        book_canvas.bind("<MouseWheel>", book_wheel)
        book_canvas.bind("<Right>", lambda _e: turn(1))
        book_canvas.bind("<Left>", lambda _e: turn(-1))
        self._visualisation_book_render = render_book

        # ----------------------------------------------------------
        # Outils : zone TomeLinea vide, à droite de la Vue feuilletée.
        # ----------------------------------------------------------
        tools_canvas = tk.Canvas(
            parent,
            bg="#D8D4CD",
            highlightthickness=0,
            bd=0,
        )
        self._visualisation_tools_canvas = tools_canvas

        def draw_tools(_event=None):
            tools_canvas.delete("all")
            w = max(1, tools_canvas.winfo_width())
            h = max(1, tools_canvas.winfo_height())
            if w < 40 or h < 40:
                return
            tools_canvas.create_polygon(
                _panel_points(0, 0, w - 3, h - 4, dx=2, dy=4),
                fill="#BDB7AE",
                outline="",
            )
            tools_canvas.create_polygon(
                _panel_points(0, 0, w - 3, h - 4),
                fill="#FFFEFC",
                outline="#D5D1CA",
                width=1,
            )
            tools_canvas.create_line(
                3, 17, 3, h - 22,
                fill="#E28A6D",
                width=4,
            )
            tools_canvas.create_text(
                20, 17,
                text="Outils",
                fill=INK,
                font=("Georgia", 12, "bold"),
                anchor="nw",
            )
            line_x1 = 80
            line_x2 = max(line_x1 + 20, w - 28)
            tools_canvas.create_line(
                line_x1, 28, line_x2, 28,
                fill="#A8A29A",
                width=1,
            )
            tools_canvas.create_oval(
                line_x2 - 3, 25, line_x2 + 3, 31,
                fill="#FFFEFC",
                outline="#A8A29A",
                width=1,
            )

        tools_canvas.bind("<Configure>", draw_tools)

        # ----------------------------------------------------------
        # Placement direct sur le fond :
        # haut = Vue globale pleine largeur ; bas = Feuilletée + Outils.
        # ----------------------------------------------------------
        def layout_visualisation(_event=None):
            width = max(parent.winfo_width(), 1180)
            height = max(parent.winfo_height(), 720)
            draw_background()

            margin_x = 16
            margin_y = 14
            gap = 14

            # Vue globale volontairement moins haute ; le panorama interne
            # conserve tous ses éléments grâce à son cadrage vertical adapté.
            global_h = min(360, max(320, int(height * 0.34)))
            global_w = max(900, width - margin_x * 2)

            global_panel.place(
                x=margin_x,
                y=margin_y,
                width=global_w,
                height=global_h,
            )
            panorama.place(
                x=12,
                y=46,
                width=max(820, global_w - 24),
                height=max(245, global_h - 58),
            )

            bottom_y = margin_y + global_h + gap
            bottom_h = max(260, height - bottom_y - margin_y)
            tools_w = min(310, max(270, int(width * 0.16)))
            bottom_gap = 14
            feuillet_w = max(
                680,
                width - margin_x * 2 - tools_w - bottom_gap,
            )

            feuillet_panel.place(
                x=margin_x,
                y=bottom_y,
                width=feuillet_w,
                height=bottom_h,
            )
            book_canvas.place(
                x=12,
                y=46,
                width=max(620, feuillet_w - 24),
                height=max(200, bottom_h - 58),
            )

            tools_canvas.place(
                x=margin_x + feuillet_w + bottom_gap,
                y=bottom_y,
                width=tools_w,
                height=bottom_h,
            )

            global_panel.after_idle(draw_global_panel)
            panorama.after_idle(draw_global)
            feuillet_panel.after_idle(draw_feuillet_panel)
            book_canvas.after_idle(render_book)
            tools_canvas.after_idle(draw_tools)

        self._visualisation_layout = layout_visualisation
        parent.bind("<Configure>", layout_visualisation, add="+")
        parent.after_idle(layout_visualisation)
    def show_screen(self, name: str) -> None:
        screen = self._screens.get(name)
        if screen is None:
            return

        previous = getattr(self, "_active", None)

        # Visualisation est une vraie page sans ruban.
        # Le bureau Projet prend toute la hauteur de la fenêtre.
        if name == "visualisation":
            if previous not in (None, "accueil", "visualisation"):
                self._visualisation_return_screen = previous

            self._active = "visualisation"
            self.header.grid_remove()
            self.project_host.grid_configure(
                row=0,
                column=0,
                rowspan=2,
                sticky="nsew",
            )

            screen.tkraise()
            self.project_host.update_idletasks()

            layout_visualisation = getattr(
                self,
                "_visualisation_layout",
                None,
            )
            if callable(layout_visualisation):
                layout_visualisation()

            render_global = getattr(
                self,
                "_visualisation_global_render",
                None,
            )
            if callable(render_global):
                render_global()

            self.project_shell.tkraise()
            return

        # Tous les autres bureaux Projet retrouvent le ruban validé.
        self.project_host.grid_configure(
            row=1,
            column=0,
            rowspan=1,
            sticky="nsew",
        )
        self.header.grid(
            row=0,
            column=0,
            sticky="ew",
        )

        if name == "accueil":
            if previous != "accueil":
                self._reset_accueil_project_selection()
            self._active = "accueil"
            self.accueil_host.tkraise()
            return

        self._active = name

        # Navigation interne au projet : comportement immédiat validé.
        if previous != "accueil":
            screen.tkraise()
            if name == "centre":
                render_centre = getattr(self, "_centre_render", None)
                if callable(render_centre):
                    render_centre()
            self._render_header_canvas()
            self.project_shell.tkraise()
            return

        # NAVIGATION_PRECHAUFFAGE_VUES_V2
        # Depuis l'Accueil, le bureau demandé a déjà été réalisé une première
        # fois au démarrage. Il n'y a donc plus de phase de construction à
        # attendre : bureau + ruban sont révélés par un seul changement de pile.
        self.accueil_host.tkraise()
        screen.tkraise()

        if name == "centre":
            render_centre = getattr(self, "_centre_render", None)
            if callable(render_centre):
                render_centre()

        self._render_header_canvas()
        screen.update_idletasks()
        self.project_host.update_idletasks()
        self.project_shell.update_idletasks()

        # Révélation atomique de l'espace Projet déjà préparé.
        self.project_shell.tkraise()




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
    # FENETRES_ACCUEIL_ATOMIQUES_V3
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

        # Plus aucun redraw de première ouverture n'est laissé à after_idle.
        # La finalisation de la fenêtre appellera cette fonction explicitement
        # pendant que la Toplevel est encore invisible.
        win._tomelinea_dialog_canvas = canvas
        win._tomelinea_dialog_redraw = redraw

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

    # FENETRES_ACCUEIL_ATOMIQUES_V3
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

        # La Toplevel est masquée AVANT géométrie et AVANT création du contenu.
        win._tomelinea_hidden_mode = "alpha"
        try:
            win.attributes("-alpha", 0.0)
        except tk.TclError:
            win._tomelinea_hidden_mode = "withdraw"
            win.withdraw()

        def _clear_dialog(*_args):
            if getattr(self, "_active_accueil_dialog", None) is win:
                self._active_accueil_dialog = None

        def _close():
            try:
                win.grab_release()
            except Exception:
                pass
            _clear_dialog()
            try:
                win.destroy()
            except Exception:
                pass

        win.protocol("WM_DELETE_WINDOW", _close)
        win.bind("<Destroy>", _clear_dialog, add="+")
        win.transient(self)
        win.resizable(False, False)
        return win

    def _reveal_accueil_dialog(self, win: tk.Toplevel) -> None:
        """Révèle une Toplevel seulement lorsque son rendu est terminé."""
        try:
            if not win.winfo_exists():
                return

            # 1. géométrie native des widgets
            win.update_idletasks()

            # 2. dessin Canvas final à sa vraie taille
            redraw = getattr(win, "_tomelinea_dialog_redraw", None)
            if callable(redraw):
                redraw()

            # 3. termine les Configure/Expose pendant que l'alpha est nul
            win.update_idletasks()
            win.update()

            # 4. une seule apparition visuelle
            mode = getattr(win, "_tomelinea_hidden_mode", "alpha")
            if mode == "alpha":
                try:
                    win.attributes("-alpha", 1.0)
                except tk.TclError:
                    pass
            else:
                win.deiconify()

            win.lift()
            win.update_idletasks()

            try:
                win.grab_set()
            except tk.TclError:
                pass
            try:
                win.focus_force()
            except Exception:
                pass
        except tk.TclError:
            pass


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

        self._reveal_accueil_dialog(win)
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
        self._reveal_accueil_dialog(win)


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
        self._reveal_accueil_dialog(win)


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
        """Centre de projet sur une seule surface Canvas pour un affichage atomique."""
        canvas = tk.Canvas(
            parent,
            bg=theme.WINDOW,
            highlightthickness=0,
            bd=0,
        )
        canvas.pack(fill="both", expand=True)
        self._centre_canvas = canvas

        def render(_event=None):
            w = max(canvas.winfo_width(), 1180)
            h = max(canvas.winfo_height(), 680)
            canvas.delete("all")

            # En-tête
            canvas.create_rectangle(
                22, 18, 29, 70,
                fill=theme.CELADON,
                outline="",
            )
            canvas.create_text(
                41, 22,
                text="Centre de projet",
                fill=theme.INK,
                font=("Segoe UI", 20, "bold"),
                anchor="nw",
            )
            canvas.create_text(
                41, 57,
                text="Pilotage, orientation et vision globale du livre",
                fill=theme.MUTED,
                font=("Segoe UI", 10),
                anchor="nw",
            )

            # Cartes statistiques
            top = 105
            gap = 10
            left = 22
            right = w - 22
            card_w = (right - left - gap * 3) / 4
            card_h = 105

            stats = (
                ("Pages", "24", theme.SKY),
                ("Parties", "6", theme.LILAC),
                ("Modèles", "8", theme.CELADON),
                ("À vérifier", "3", theme.CORAL),
            )

            for index, (title, value, accent) in enumerate(stats):
                x1 = left + index * (card_w + gap)
                x2 = x1 + card_w
                y1 = top
                y2 = top + card_h

                canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=theme.PANEL,
                    outline=theme.BORDER,
                    width=1,
                )
                canvas.create_rectangle(
                    x1, y1, x2, y1 + 5,
                    fill=accent,
                    outline="",
                )
                canvas.create_text(
                    x1 + 14, y1 + 22,
                    text=title,
                    fill=theme.INK,
                    font=("Segoe UI", 11, "bold"),
                    anchor="nw",
                )
                canvas.create_text(
                    x1 + 14, y1 + 56,
                    text=value,
                    fill=theme.INK,
                    font=("Segoe UI", 19, "bold"),
                    anchor="nw",
                )

            # Grande carte Vue du livre
            book_y1 = top + card_h + 16
            book_y2 = max(book_y1 + 310, h - 24)
            canvas.create_rectangle(
                left, book_y1, right, book_y2,
                fill=theme.PANEL,
                outline=theme.BORDER,
                width=1,
            )
            canvas.create_rectangle(
                left, book_y1, right, book_y1 + 5,
                fill=theme.INK,
                outline="",
            )
            canvas.create_text(
                left + 14, book_y1 + 20,
                text="Vue du livre",
                fill=theme.INK,
                font=("Segoe UI", 11, "bold"),
                anchor="nw",
            )
            canvas.create_text(
                left + 14, book_y1 + 48,
                text=(
                    "Synoptique simplifié — les futurs clics pourront orienter "
                    "vers les bureaux concernés."
                ),
                fill=theme.MUTED,
                font=("Segoe UI", 9),
                anchor="nw",
            )

            # Ligne synoptique
            rail_y = book_y1 + 155
            rail_left = left + 65
            rail_right = right - 65
            colors = [
                theme.SKY,
                theme.LILAC,
                theme.CELADON,
                theme.CORAL,
                theme.SKY,
                theme.YELLOW,
            ]
            step = (rail_right - rail_left) / max(1, len(colors) - 1)

            canvas.create_line(
                rail_left,
                rail_y,
                rail_right,
                rail_y,
                fill="#B8C2C9",
                width=4,
            )

            for index, color in enumerate(colors, start=1):
                x = rail_left + (index - 1) * step
                canvas.create_oval(
                    x - 13,
                    rail_y - 13,
                    x + 13,
                    rail_y + 13,
                    fill=color,
                    outline=theme.INK,
                )
                canvas.create_text(
                    x,
                    rail_y + 34,
                    text=f"Partie {index}",
                    fill=theme.INK,
                    font=("Segoe UI", 9, "bold"),
                    anchor="n",
                )

        canvas.bind("<Configure>", render)
        self._centre_render = render
        canvas.after_idle(render)


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

    # VUE_GLOBALE_PANORAMIQUE_BORNES_V3_FOND_ET_FERMETURE
    # VUE_DU_LIVRE_DEUX_ONGLETS_DYNAMIQUES_V1
    # VUE_DU_LIVRE_DEUX_ONGLETS_DYNAMIQUES_V2_FLUIDE_ET_FEUILLETAGE
    # VUE_DU_LIVRE_DEUX_ONGLETS_DYNAMIQUES_V3_GLISSER_ET_DECO_UNIFIEE
    # VUE_DU_LIVRE_DEUX_ONGLETS_DYNAMIQUES_V13_ARCHITECTURE_SEPAREE
    # VUE_DU_LIVRE_DEUX_ONGLETS_DYNAMIQUES_V14_PANNEAUX_INTERNES_FIXES
    # VUE_DU_LIVRE_DEUX_ONGLETS_DYNAMIQUES_V14_PANNEAUX_INTERNES_FIXES
    def _tomelinea_open_book_views(self, initial_tab="global"):
        """Visionneuse Maquettage : structure globale + feuilletage.

        Cette fenêtre est volontairement sans fonction de travail.
        Dans Maquettage, une page est représentée par la vignette de son type.
        Le futur bureau Visualisation pourra utiliser une représentation
        différente selon l'état réel d'avancement de la page.
        """
        pages = self._tomelinea_collect_book_pages()
        model = getattr(self, "_maquettage_structure_model", None) or [
            {"name": "Début", "pages": 3, "color": "#75B89E"},
            {"name": "Partie 1", "pages": 12, "color": "#8D70C7"},
            {"name": "Partie 2", "pages": None, "color": "#72AFCB"},
            {"name": "Partie 3", "pages": None, "color": "#E28A6D"},
            {"name": "Fin", "pages": 3, "color": "#75B89E"},
        ]

        win = tk.Toplevel(self)
        win.title("TomeLinea — Vue du livre")

        if hasattr(self, "_prepare_accueil_dialog"):
            self._prepare_accueil_dialog(win)
        else:
            try:
                win.attributes("-alpha", 0.0)
            except tk.TclError:
                win.withdraw()

        screen_w = max(1180, self.winfo_screenwidth())
        screen_h = max(720, self.winfo_screenheight())

        # Architecture V14 : la Toplevel ne change JAMAIS de taille.
        # Les deux dimensions historiques deviennent des dimensions VISUELLES
        # de panneau interne. Le cadre natif reste fixe au maximum requis.
        global_size = (
            max(1120, screen_w - 36),
            min(620, max(500, int(screen_h * 0.63))),
        )
        book_size = (
            min(1050, max(850, int(screen_w * 0.60))),
            min(720, max(590, int(screen_h * 0.72))),
        )
        fixed_size = (
            max(global_size[0], book_size[0]),
            max(global_size[1], book_size[1]),
        )
        initial_size = fixed_size

        if hasattr(self, "_accueil_center_base_window"):
            self._accueil_center_base_window(
                win,
                initial_size[0],
                initial_size[1],
            )
        else:
            self._tomelinea_center_toplevel(
                win,
                initial_size[0],
                initial_size[1],
            )

        win.configure(bg="#F6F2EA")
        win.transient(self)
        # Les relations WM sont fixées avant de retirer les décorations.
        # La croix TomeLinea interne devient l'unique fermeture visible.
        try:
            win.overrideredirect(True)
        except tk.TclError:
            pass

        PANEL = "#FFFEFC"
        PANEL_ALT = "#F7F4ED"
        INK = "#111111"
        MUTED = "#626B73"
        NAVY = "#173E70"
        VIOLET = "#8D70C7"
        BORDER = "#D5D1CA"
        MOUNT = "#F1EFE9"
        GRID = "#E5E1DA"

        # ----------------------------------------------------------
        # Ressources partagées.
        # ----------------------------------------------------------
        bg_path = (
            PROJECT_ROOT
            / "assets"
            / "gui_v2"
            / "maquettage_backgrounds"
            / "maquettage_studio_pro.png"
        )

        page_thumb_root = PROJECT_ROOT / "assets" / "page_thumbnails"
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

        win._book_views_bg_source = None
        win._book_views_bg_photo = None
        win._book_views_photo_cache = {}
        win._book_views_structure_cache = {}
        win._book_views_close_cache = {}
        win._book_views_source_cache = {}
        win._book_views_turn_frames = []

        try:
            if bg_path.exists():
                win._book_views_bg_source = Image.open(
                    bg_path
                ).convert("RGB")
        except Exception:
            win._book_views_bg_source = None

        def mix_hex(color_a, color_b, ratio):
            ratio = max(0.0, min(1.0, float(ratio)))

            def rgb(value):
                value = str(value).lstrip("#")
                if len(value) != 6:
                    return (128, 128, 128)
                try:
                    return tuple(
                        int(value[index:index + 2], 16)
                        for index in (0, 2, 4)
                    )
                except Exception:
                    return (128, 128, 128)

            a = rgb(color_a)
            b = rgb(color_b)
            mixed = tuple(
                int(round(
                    a[index] * (1.0 - ratio)
                    + b[index] * ratio
                ))
                for index in range(3)
            )
            return "#{:02X}{:02X}{:02X}".format(*mixed)

        def polygon_points(x1, y1, x2, y2, cut=16, dx=0, dy=0):
            return [
                x1 + dx, y1 + dy,
                x2 - cut + dx, y1 + dy,
                x2 + dx, y1 + cut + dy,
                x2 + dx, y2 + dy,
                x1 + cut + dx, y2 + dy,
                x1 + dx, y2 - cut + dy,
            ]

        def rounded(canvas, x1, y1, x2, y2, radius, **kwargs):
            r = max(
                1,
                min(
                    radius,
                    (x2 - x1) / 2,
                    (y2 - y1) / 2,
                ),
            )
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

        def normalized_type_name(page):
            # Préparation au futur vrai système d'affectation des types :
            # s'il existe déjà une information plus précise, elle est prioritaire.
            for key in (
                "type_name",
                "page_type",
                "type",
                "kind",
            ):
                value = page.get(key)
                if value:
                    return str(value).strip()
            return "Page courante"

        def thumbnail_path_for_type(type_name):
            low = str(type_name).strip().lower()

            aliases = {
                "couverture": "type_page_couverture.png",
                "2e de couverture": "type_page_deuxieme_couverture.png",
                "deuxième de couverture": "type_page_deuxieme_couverture.png",
                "deuxieme de couverture": "type_page_deuxieme_couverture.png",
                "page de titre": "type_page_titre.png",
                "titre": "type_page_titre.png",
                "avant-propos": "type_page_avant_propos.png",
                "avant propos": "type_page_avant_propos.png",
                "sommaire": "type_page_sommaire.png",
                "chapitre": "type_page_chapitre.png",
                "tête de chapitre": "type_page_chapitre.png",
                "tete de chapitre": "type_page_chapitre.png",
                "tête de partie": "type_page_chapitre.png",
                "tete de partie": "type_page_chapitre.png",
                "texte": "type_page_texte.png",
                "page courante": "type_page_texte.png",
                "page commune": "type_page_texte.png",
                "fiche": "type_page_fiche.png",
                "illustration": "type_page_illustration.png",
                "transition": "type_page_transition.png",
                "conclusion": "type_page_conclusion.png",
                "page blanche": "type_page_blanche.png",
                "3e de couverture": "type_page_troisieme_couverture.png",
                "troisième de couverture": "type_page_troisieme_couverture.png",
                "troisieme de couverture": "type_page_troisieme_couverture.png",
                "4e de couverture": "type_page_quatrieme_couverture.png",
                "quatrième de couverture": "type_page_quatrieme_couverture.png",
                "quatrieme de couverture": "type_page_quatrieme_couverture.png",
                "personnalisée": "type_page_personnalisee.png",
                "personnalisee": "type_page_personnalisee.png",
                # Tant que les vraies affectations de type ne sont pas
                # enregistrées page par page, Page auto utilise la vignette
                # Sommaire comme identité visuelle provisoire.
                "page auto": "type_page_sommaire.png",
            }

            filename = aliases.get(low)
            if filename:
                candidate = page_thumb_root / filename
                if candidate.exists():
                    return candidate

            # Types personnalisés déjà créés dans la session.
            for item in getattr(
                self,
                "_maquettage_custom_page_types",
                [],
            ):
                if not isinstance(item, dict):
                    continue
                if (
                    str(item.get("name", "")).strip().lower()
                    == low
                ):
                    image_value = str(
                        item.get("image", "") or ""
                    ).strip()
                    if image_value:
                        candidate = Path(image_value)
                        if candidate.exists():
                            return candidate

            fallback = page_thumb_root / "type_page_texte.png"
            return fallback if fallback.exists() else None

        def page_photo(page, width, height):
            type_name = normalized_type_name(page)
            path = thumbnail_path_for_type(type_name)
            key = (
                str(path) if path else "",
                int(width),
                int(height),
            )

            if key in win._book_views_photo_cache:
                return win._book_views_photo_cache[key]

            photo = None
            if path is not None:
                try:
                    image = Image.open(path).convert("RGBA")
                    image = image.resize(
                        (
                            max(1, int(width)),
                            max(1, int(height)),
                        ),
                        Image.Resampling.LANCZOS,
                    )
                    photo = ImageTk.PhotoImage(image)
                except Exception:
                    photo = None

            win._book_views_photo_cache[key] = photo
            return photo

        def page_source_image(page):
            """Image source du type de page, conservée pour les animations."""
            if page is None:
                return None

            type_name = normalized_type_name(page)
            path = thumbnail_path_for_type(type_name)
            key = str(path) if path is not None else ""

            if key in win._book_views_source_cache:
                return win._book_views_source_cache[key]

            image = None
            if path is not None:
                try:
                    image = Image.open(path).convert("RGBA")
                except Exception:
                    image = None

            win._book_views_source_cache[key] = image
            return image

        def animated_page_photo(
            page,
            width,
            height,
            *,
            shade=0.0,
        ):
            """Image temporaire légère pour simuler une feuille en rotation."""
            width = max(2, int(width))
            height = max(2, int(height))

            source = page_source_image(page)

            if source is None:
                image = Image.new(
                    "RGBA",
                    (width, height),
                    (245, 242, 235, 255),
                )
            else:
                image = source.resize(
                    (width, height),
                    Image.Resampling.BILINEAR,
                )

            shade = max(0.0, min(0.38, float(shade)))
            if shade > 0:
                veil = Image.new(
                    "RGBA",
                    image.size,
                    (92, 84, 76, 255),
                )
                image = Image.blend(
                    image,
                    veil,
                    shade,
                )

            photo = ImageTk.PhotoImage(image)
            win._book_views_turn_frames = [photo]
            return photo

        def structure_photo(
            path,
            max_w,
            max_h,
            *,
            green_flag=False,
        ):
            key = (
                str(path),
                int(max_w),
                int(max_h),
                bool(green_flag),
            )
            cached = win._book_views_structure_cache.get(key)
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
                                pixels[xx, yy] = (
                                    int(max(
                                        0,
                                        min(
                                            255,
                                            83 * luminosity,
                                        ),
                                    )),
                                    int(max(
                                        0,
                                        min(
                                            255,
                                            151 * luminosity,
                                        ),
                                    )),
                                    int(max(
                                        0,
                                        min(
                                            255,
                                            105 * luminosity,
                                        ),
                                    )),
                                    a,
                                )

                image.thumbnail(
                    (max_w, max_h),
                    Image.Resampling.LANCZOS,
                )
                photo = ImageTk.PhotoImage(image)
                win._book_views_structure_cache[key] = photo
                return photo
            except Exception:
                return None

        # ----------------------------------------------------------
        # Shell de la fenêtre.
        # ----------------------------------------------------------
        outer = tk.Canvas(
            win,
            bg="#F6F2EA",
            highlightthickness=0,
            bd=0,
        )
        outer.pack(fill="both", expand=True)

        viewport = tk.Frame(
            outer,
            bg=PANEL,
            bd=0,
            highlightthickness=0,
        )
        viewport_id = outer.create_window(
            46,
            36,
            window=viewport,
            anchor="nw",
        )

        resize_fx = {
            "active": False,
        }

        visual_state = {
            "mode": (
                "feuilleter"
                if str(initial_tab).lower().startswith("feuil")
                else "global"
            ),
        }

        def redraw_shell(_event=None):
            """Dessine le panneau visuel sans toucher à la Toplevel.

            Vue globale et Feuilleter gardent leurs dimensions historiques,
            mais uniquement à l'intérieur de la fenêtre native fixe.
            """
            w = max(outer.winfo_width(), 780)
            h = max(outer.winfo_height(), 460)

            outer.delete("bookviews_bg")
            outer.delete("bookviews_panel")

            if win._book_views_bg_source is not None:
                try:
                    cache_key = (w, h)
                    cached = getattr(
                        win,
                        "_book_views_fixed_bg_cache",
                        {},
                    ).get(cache_key)
                    if cached is None:
                        image = win._book_views_bg_source.resize(
                            (w, h),
                            Image.Resampling.LANCZOS,
                        )
                        image = Image.blend(
                            image.convert("RGB"),
                            Image.new(
                                "RGB",
                                image.size,
                                "#D6D7D6",
                            ),
                            0.08,
                        )
                        cached = ImageTk.PhotoImage(image)
                        if not hasattr(
                            win,
                            "_book_views_fixed_bg_cache",
                        ):
                            win._book_views_fixed_bg_cache = {}
                        win._book_views_fixed_bg_cache[cache_key] = cached
                    win._book_views_bg_photo = cached
                    outer.create_image(
                        0,
                        0,
                        image=cached,
                        anchor="nw",
                        tags=("bookviews_bg",),
                    )
                except Exception:
                    outer.create_rectangle(
                        0,
                        0,
                        w,
                        h,
                        fill="#EEEDEA",
                        outline="",
                        tags=("bookviews_bg",),
                    )
            else:
                outer.create_rectangle(
                    0,
                    0,
                    w,
                    h,
                    fill="#EEEDEA",
                    outline="",
                    tags=("bookviews_bg",),
                )

            visual_w, visual_h = (
                global_size
                if visual_state["mode"] == "global"
                else book_size
            )
            visual_w = min(w, int(visual_w))
            visual_h = min(h, int(visual_h))

            origin_x = int((w - visual_w) / 2)
            origin_y = int((h - visual_h) / 2)

            x1 = origin_x + 22
            y1 = origin_y + 18
            x2 = origin_x + visual_w - 22
            y2 = origin_y + visual_h - 18

            outer.create_polygon(
                polygon_points(
                    x1,
                    y1,
                    x2,
                    y2,
                    dx=2,
                    dy=4,
                ),
                fill="#D1CCC4",
                outline="",
                tags=("bookviews_panel",),
            )
            outer.create_polygon(
                polygon_points(x1, y1, x2, y2),
                fill=PANEL,
                outline=BORDER,
                width=1,
                tags=("bookviews_panel",),
            )
            outer.create_line(
                x1 + 4,
                y1 + 18,
                x1 + 4,
                y2 - 18,
                fill=VIOLET,
                width=4,
                tags=("bookviews_panel",),
            )

            outer.coords(
                viewport_id,
                x1 + 25,
                y1 + 18,
            )
            outer.itemconfigure(
                viewport_id,
                width=max(720, x2 - x1 - 50),
                height=max(390, y2 - y1 - 36),
            )

            outer.tag_lower("bookviews_panel")
            outer.tag_lower("bookviews_bg")

        outer.bind("<Configure>", redraw_shell)

        # ----------------------------------------------------------
        # En-tête TomeLinea.
        # ----------------------------------------------------------
        header = tk.Frame(
            viewport,
            bg=PANEL,
            height=111,
        )
        header.pack(fill="x")
        header.pack_propagate(False)

        title_row = tk.Frame(
            header,
            bg=PANEL,
            height=32,
        )
        title_row.place(
            x=8,
            y=4,
            relwidth=1.0,
            width=-70,
            height=32,
        )

        title_label = tk.Label(
            title_row,
            text="Vue du livre",
            bg=PANEL,
            fg=theme.INK,
            font=("Georgia", 15, "bold"),
        )
        title_label.pack(
            side="left",
            anchor="center",
        )

        title_line = tk.Canvas(
            title_row,
            bg=PANEL,
            highlightthickness=0,
            bd=0,
            height=26,
        )
        title_line.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(20, 0),
        )

        def draw_title_line(_event=None):
            title_line.delete("all")
            line_w = max(60, title_line.winfo_width())
            yy = 13
            end_x = max(24, line_w - 18)

            title_line.create_line(
                0,
                yy,
                end_x - 5,
                yy,
                fill="#202020",
                width=1,
            )
            title_line.create_oval(
                end_x - 5,
                yy - 4,
                end_x + 3,
                yy + 4,
                fill=PANEL,
                outline="#202020",
                width=1,
            )

        title_line.bind("<Configure>", draw_title_line)

        subtitle_label = tk.Label(
            header,
            text=(
                "Deux façons de contrôler la construction "
                "du livre sans la modifier."
            ),
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 8),
        )
        subtitle_label.place(x=10, y=39)

        # Fermer = icône du ruban.
        close = tk.Canvas(
            header,
            width=44,
            height=42,
            bg=PANEL,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        close.place(
            relx=1.0,
            x=-8,
            y=0,
            anchor="ne",
        )

        close_state = {
            "hover": False,
            "pressed": False,
        }

        def get_close_photo(state):
            cached = win._book_views_close_cache.get(state)
            if cached is not None:
                return cached

            photo = None
            try:
                photo = self._get_nav_photo(
                    "fermer",
                    state,
                    32,
                )
            except Exception:
                photo = None

            win._book_views_close_cache[state] = photo
            return photo

        def draw_close():
            close.delete("all")

            if close_state["pressed"]:
                state = "actif"
            elif close_state["hover"]:
                state = "survol"
            else:
                state = "normal"

            photo = get_close_photo(state)
            if photo is not None:
                close.create_image(
                    22,
                    20,
                    image=photo,
                    anchor="center",
                )
            else:
                close.create_oval(
                    8,
                    6,
                    36,
                    34,
                    fill="#D94A43",
                    outline="#B53B36",
                )
                close.create_text(
                    22,
                    20,
                    text="×",
                    fill="#FFFFFF",
                    font=("Segoe UI", 14, "bold"),
                )

        close.bind(
            "<Enter>",
            lambda _e: (
                close_state.update(hover=True),
                draw_close(),
            ),
        )
        close.bind(
            "<Leave>",
            lambda _e: (
                close_state.update(
                    hover=False,
                    pressed=False,
                ),
                draw_close(),
            ),
        )
        close.bind(
            "<ButtonPress-1>",
            lambda _e: (
                close_state.update(pressed=True),
                draw_close(),
            ),
        )
        close.bind(
            "<ButtonRelease-1>",
            lambda _e: win.destroy(),
        )
        draw_close()

        # ----------------------------------------------------------
        # Onglets.
        # ----------------------------------------------------------
        tabs = tk.Canvas(
            header,
            bg=PANEL,
            highlightthickness=0,
            bd=0,
            height=40,
        )
        tabs.place(
            x=8,
            y=67,
            width=310,
            height=38,
        )

        state = {
            "tab": (
                "feuilleter"
                if str(initial_tab).lower().startswith("feuil")
                else "global"
            ),
            "tab_hover": None,
        }

        tab_regions = {
            "global": (0, 2, 145, 35),
            "feuilleter": (153, 2, 298, 35),
        }

        def draw_tabs():
            tabs.delete("all")

            for key, text in (
                ("global", "Vue globale"),
                ("feuilleter", "Feuilleter"),
            ):
                x1, y1, x2, y2 = tab_regions[key]
                selected = state["tab"] == key
                hovered = state["tab_hover"] == key

                if selected:
                    fill = "#F1EDF8"
                    border = "#B9AAD0"
                elif hovered:
                    fill = "#F5F7F8"
                    border = "#CAD2D9"
                else:
                    fill = "#FFFDFC"
                    border = "#D6D1CA"

                rounded(
                    tabs,
                    x1,
                    y1,
                    x2,
                    y2,
                    8,
                    fill=fill,
                    outline=border,
                    width=1,
                )

                tabs.create_text(
                    (x1 + x2) / 2,
                    (y1 + y2) / 2 - (1 if selected else 0),
                    text=text,
                    fill=(
                        "#173E70"
                        if selected
                        else "#4F5962"
                    ),
                    font=(
                        "Segoe UI",
                        9,
                        "bold" if selected else "normal",
                    ),
                    anchor="center",
                )

                if selected:
                    tabs.create_line(
                        x1 + 18,
                        y2 - 3,
                        x2 - 18,
                        y2 - 3,
                        fill=VIOLET,
                        width=2,
                    )

        def tab_at(x, y):
            for key, box in tab_regions.items():
                x1, y1, x2, y2 = box
                if x1 <= x <= x2 and y1 <= y <= y2:
                    return key
            return None

        # ----------------------------------------------------------
        # Conteneurs des deux vues.
        # ----------------------------------------------------------
        content_stack = tk.Frame(
            viewport,
            bg=PANEL,
        )
        content_stack.pack(
            fill="both",
            expand=True,
            padx=(4, 4),
            pady=(0, 4),
        )

        global_host = tk.Frame(
            content_stack,
            bg=PANEL,
        )
        book_host = tk.Frame(
            content_stack,
            bg=PANEL,
        )

        global_host.place(
            x=0,
            y=0,
            relwidth=1.0,
            relheight=1.0,
        )
        book_host.place(
            x=0,
            y=0,
            relwidth=1.0,
            relheight=1.0,
        )

        # ----------------------------------------------------------
        # VUE GLOBALE.
        # ----------------------------------------------------------
        panorama = tk.Canvas(
            global_host,
            bg=PANEL,
            highlightthickness=0,
            bd=0,
            xscrollincrement=18,
        )
        # VUE_GLOBALE_SANS_BARRE_NI_CONSIGNE_V16
        panorama.pack(
            fill="both",
            expand=True,
        )

        pan_state = {
            "active": False,
            "moved": False,
            "press_x": 0,
        }

        pages_by_group = {}
        for page in pages:
            pages_by_group.setdefault(
                str(page.get("group", "Partie")),
                [],
            ).append(page)

        def page_visual_size(page):
            low = normalized_type_name(page).lower()

            if low in (
                "couverture",
                "4e de couverture",
                "tête de partie",
                "tete de partie",
                "tête de chapitre",
                "tete de chapitre",
                "chapitre",
            ):
                return 84, int(84 * 1.40), "large"

            if low == "page auto":
                return 58, int(58 * 1.40), "auto"

            return 68, int(68 * 1.40), "normal"

        def draw_structure_tile(
            canvas,
            cx,
            icon_anchor_y,
            *,
            book=False,
            accent=VIOLET,
        ):
            tile_w = 98 if book else 86
            tile_h = 62 if book else 58
            x1 = cx - tile_w / 2
            x2 = cx + tile_w / 2
            y2 = icon_anchor_y + 7
            y1 = y2 - tile_h
            cut = 8

            def points(dx=0, dy=0):
                return [
                    x1 + dx, y1 + dy,
                    x2 - cut + dx, y1 + dy,
                    x2 + dx, y1 + cut + dy,
                    x2 + dx, y2 + dy,
                    x1 + cut + dx, y2 + dy,
                    x1 + dx, y2 - cut + dy,
                ]

            canvas.create_polygon(
                points(2, 3),
                fill="#D8D4CD",
                outline="",
            )

            if book:
                fill = mix_hex(
                    accent,
                    "#FFFFFF",
                    0.86,
                )
                outline = mix_hex(
                    accent,
                    "#BDB8B0",
                    0.62,
                )
                grid = mix_hex(
                    accent,
                    "#FFFFFF",
                    0.91,
                )
            else:
                fill = "#F4F1E9"
                outline = "#D3CEC5"
                grid = "#E0E4E0"

            canvas.create_polygon(
                points(),
                fill=fill,
                outline=outline,
                width=1,
            )

            canvas.create_line(
                x1 + tile_w * 0.34,
                y1 + 8,
                x1 + tile_w * 0.34,
                y2 - 8,
                fill=grid,
                width=1,
            )
            canvas.create_line(
                x1 + tile_w * 0.67,
                y1 + 8,
                x1 + tile_w * 0.67,
                y2 - 8,
                fill=grid,
                width=1,
            )
            canvas.create_line(
                x1 + 8,
                y1 + tile_h * 0.5,
                x2 - 8,
                y1 + tile_h * 0.5,
                fill=grid,
                width=1,
            )

        def draw_global(_event=None):
            if resize_fx["active"]:
                return
            panorama.delete("all")

            view_w = max(900, panorama.winfo_width())
            view_h = max(350, panorama.winfo_height())

            page_gap = 24
            group_gap = 70
            left_pad = 72
            right_pad = 72

            marker_y = int(view_h * 0.22)
            guide_y = int(view_h * 0.34)
            page_baseline = int(view_h * 0.68)

            groups_layout = []
            cursor_x = left_pad

            for group_index, group in enumerate(model):
                group_name = str(group.get("name", "Partie"))
                group_pages = pages_by_group.get(group_name, [])
                start_x = cursor_x
                layouts = []

                for page_index, page in enumerate(group_pages):
                    pw, ph, size_kind = page_visual_size(page)
                    layouts.append({
                        "page": page,
                        "x": cursor_x,
                        "w": pw,
                        "h": ph,
                        "size_kind": size_kind,
                    })
                    cursor_x += pw
                    if page_index < len(group_pages) - 1:
                        cursor_x += page_gap

                end_x = (
                    cursor_x
                    if layouts
                    else start_x + 44
                )
                if not layouts:
                    cursor_x = end_x

                groups_layout.append({
                    "index": group_index,
                    "group": group,
                    "name": group_name,
                    "layouts": layouts,
                    "start_x": start_x,
                    "end_x": end_x,
                })

                if group_index < len(model) - 1:
                    cursor_x += group_gap

            natural_total = cursor_x + right_pad
            content_offset = (
                (view_w - natural_total) / 2
                if natural_total < view_w
                else 0
            )

            if content_offset > 0:
                for group_data in groups_layout:
                    group_data["start_x"] += content_offset
                    group_data["end_x"] += content_offset
                    for layout in group_data["layouts"]:
                        layout["x"] += content_offset
                natural_total = view_w

            # Table de montage continue derrière les livres ET les pages.
            band_x1 = 18
            band_x2 = max(
                view_w - 18,
                natural_total - 18,
            )
            band_y1 = max(12, marker_y - 75)
            band_y2 = min(
                view_h - 20,
                page_baseline + 95,
            )

            panorama.create_polygon(
                polygon_points(
                    band_x1,
                    band_y1,
                    band_x2,
                    band_y2,
                    cut=14,
                    dx=2,
                    dy=4,
                ),
                fill="#D7D2CA",
                outline="",
            )
            panorama.create_polygon(
                polygon_points(
                    band_x1,
                    band_y1,
                    band_x2,
                    band_y2,
                    cut=14,
                ),
                fill=MOUNT,
                outline="#D8D3CB",
                width=1,
            )

            gx = band_x1 + 38
            while gx < band_x2 - 20:
                panorama.create_line(
                    gx,
                    band_y1 + 14,
                    gx,
                    band_y2 - 14,
                    fill=GRID,
                    width=1,
                )
                gx += 96

            gy = band_y1 + 28
            while gy < band_y2 - 16:
                panorama.create_line(
                    band_x1 + 14,
                    gy,
                    band_x2 - 14,
                    gy,
                    fill=GRID,
                    width=1,
                )
                gy += 44

            previous_box = None

            for group_data in groups_layout:
                index = group_data["index"]
                group = group_data["group"]
                layouts = group_data["layouts"]
                accent = str(
                    group.get("color", VIOLET) or VIOLET
                )

                if layouts:
                    marker_x = layouts[0]["x"]
                else:
                    marker_x = (
                        group_data["start_x"]
                        + group_data["end_x"]
                    ) / 2

                is_start = index == 0
                is_end = index == len(groups_layout) - 1

                if is_start:
                    marker_center = marker_x + 10
                    icon_path = (
                        ribbon_flag_path
                        if ribbon_flag_path.exists()
                        else fallback_flag_path
                    )
                    photo = structure_photo(
                        icon_path,
                        56,
                        48,
                        green_flag=True,
                    )
                    draw_structure_tile(
                        panorama,
                        marker_center,
                        marker_y + 4,
                        book=False,
                        accent=accent,
                    )
                elif is_end:
                    marker_center = (
                        group_data["end_x"] - 10
                        if layouts
                        else marker_x
                    )
                    icon_path = (
                        ribbon_flag_path
                        if ribbon_flag_path.exists()
                        else fallback_flag_path
                    )
                    photo = structure_photo(
                        icon_path,
                        56,
                        48,
                        green_flag=False,
                    )
                    draw_structure_tile(
                        panorama,
                        marker_center,
                        marker_y + 4,
                        book=False,
                        accent=accent,
                    )
                else:
                    marker_center = marker_x
                    icon_path = book_icon_paths[
                        (index - 1) % len(book_icon_paths)
                    ]
                    photo = structure_photo(
                        icon_path,
                        70,
                        50,
                    )
                    draw_structure_tile(
                        panorama,
                        marker_center,
                        marker_y + 4,
                        book=True,
                        accent=accent,
                    )

                if photo is not None:
                    panorama.create_image(
                        marker_center,
                        marker_y,
                        image=photo,
                        anchor="s",
                    )

                diamond_r = 4
                panorama.create_polygon(
                    marker_center,
                    guide_y - diamond_r,
                    marker_center + diamond_r,
                    guide_y,
                    marker_center,
                    guide_y + diamond_r,
                    marker_center - diamond_r,
                    guide_y,
                    fill="#FFFFFF",
                    outline="#111111",
                    width=1,
                )
                panorama.create_text(
                    marker_center,
                    guide_y + 21,
                    text=group_data["name"],
                    fill=INK,
                    font=("Georgia", 9, "bold"),
                    anchor="center",
                )

                panorama.create_line(
                    marker_center,
                    guide_y + 33,
                    marker_center,
                    page_baseline - 72,
                    fill="#D8D2CA",
                    width=1,
                    dash=(2, 3),
                )

                for layout in layouts:
                    page = layout["page"]
                    px = layout["x"]
                    pw = layout["w"]
                    ph = layout["h"]
                    py = page_baseline - ph / 2

                    rounded(
                        panorama,
                        px + 2,
                        py + 4,
                        px + pw + 2,
                        py + ph + 4,
                        7,
                        fill="#D0CBC3",
                        outline="",
                    )
                    rounded(
                        panorama,
                        px,
                        py,
                        px + pw,
                        py + ph,
                        7,
                        fill="#FFFEFB",
                        outline="#CDC8C0",
                        width=1,
                    )

                    photo_page = page_photo(
                        page,
                        pw - 4,
                        ph - 4,
                    )
                    if photo_page is not None:
                        panorama.create_image(
                            px + pw / 2,
                            py + ph / 2,
                            image=photo_page,
                            anchor="center",
                        )
                    else:
                        panorama.create_text(
                            px + pw / 2,
                            py + ph / 2,
                            text=normalized_type_name(page),
                            fill="#5E666D",
                            font=("Segoe UI", 6),
                            justify="center",
                        )

                    box = {
                        "x1": px,
                        "x2": px + pw,
                        "y1": py,
                        "y2": py + ph,
                    }

                    if previous_box is not None:
                        x1 = previous_box["x2"] + 5
                        x2 = box["x1"] - 5
                        if x2 > x1:
                            yy = page_baseline
                            panorama.create_line(
                                x1,
                                yy,
                                x2,
                                yy,
                                fill="#B7B1A8",
                                width=1,
                            )
                            dot = (x1 + x2) / 2
                            panorama.create_oval(
                                dot - 3,
                                yy - 3,
                                dot + 3,
                                yy + 3,
                                fill=MOUNT,
                                outline="#9F988F",
                                width=1,
                            )

                    previous_box = box

            panorama.configure(
                scrollregion=(
                    0,
                    0,
                    max(view_w, natural_total),
                    view_h,
                )
            )

        def global_wheel(event):
            if state["tab"] != "global":
                return None
            if getattr(event, "delta", 0):
                panorama.xview_scroll(
                    -3 if event.delta > 0 else 3,
                    "units",
                )
                return "break"
            return None

        # VUE_GLOBALE_PAN_HORIZONTAL_SEUL_V15
        def panorama_pan_press(event):
            if state["tab"] != "global" or resize_fx["active"]:
                return
            pan_state["active"] = True
            pan_state["moved"] = False
            pan_state["press_x"] = event.x
            pan_state["press_y"] = event.y

            try:
                pan_state["y_origin"] = float(
                    panorama.yview()[0]
                )
            except Exception:
                pan_state["y_origin"] = 0.0

            panorama.scan_mark(
                event.x,
                event.y,
            )
            panorama.configure(cursor="hand2")

        def panorama_pan_drag(event):
            if not pan_state["active"] or state["tab"] != "global":
                return

            if abs(event.x - pan_state["press_x"]) >= 3:
                pan_state["moved"] = True

            # Verrou horizontal : le Y reste celui du clic initial.
            panorama.scan_dragto(
                event.x,
                pan_state["press_y"],
                gain=1,
            )

            # Sécurité contre les arrondis internes de Tk.
            try:
                panorama.yview_moveto(
                    pan_state["y_origin"]
                )
            except Exception:
                pass

            return "break"

        def panorama_pan_release(_event=None):
            if not pan_state["active"]:
                return
            pan_state["active"] = False
            panorama.configure(cursor="arrow")

        panorama.bind(
            "<Configure>",
            lambda event: (
                draw_global(event)
                if state["tab"] == "global"
                else None
            ),
        )
        panorama.bind("<ButtonPress-1>", panorama_pan_press)
        panorama.bind("<B1-Motion>", panorama_pan_drag)
        panorama.bind("<ButtonRelease-1>", panorama_pan_release)
        panorama.bind(
            "<Leave>",
            lambda _e: (
                panorama_pan_release()
                if pan_state["active"]
                else None
            ),
        )

        # ----------------------------------------------------------
        # FEUILLETAGE.
        # ----------------------------------------------------------
        book_canvas = tk.Canvas(
            book_host,
            bg=PANEL,
            highlightthickness=0,
            bd=0,
        )
        book_canvas.pack(fill="both", expand=True)

        spread_left = [-1]

        flip_state = {
            "active": False,
            "after": None,
            "direction": 0,
        }

        def draw_large_page(
            canvas,
            page,
            x1,
            y1,
            x2,
            y2,
            *,
            blank=False,
        ):
            if blank or page is None:
                canvas.create_rectangle(
                    x1 + 3,
                    y1 + 5,
                    x2 + 3,
                    y2 + 5,
                    fill="#B9B1A8",
                    outline="",
                )
                canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill="#EEEAE3",
                    outline="#CFC8BF",
                    width=1,
                )
                return

            canvas.create_rectangle(
                x1 + 4,
                y1 + 6,
                x2 + 4,
                y2 + 6,
                fill="#A69D93",
                outline="",
            )
            canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill="#FFFEFB",
                outline="#C9C2BA",
                width=1,
            )

            photo = page_photo(
                page,
                max(1, int(x2 - x1 - 8)),
                max(1, int(y2 - y1 - 8)),
            )
            if photo is not None:
                canvas.create_image(
                    (x1 + x2) / 2,
                    (y1 + y2) / 2,
                    image=photo,
                    anchor="center",
                )
            else:
                canvas.create_text(
                    (x1 + x2) / 2,
                    (y1 + y2) / 2,
                    text=normalized_type_name(page),
                    fill="#4E565D",
                    font=("Georgia", 13, "bold"),
                    justify="center",
                )

        def book_geometry():
            w = max(740, book_canvas.winfo_width())
            h = max(420, book_canvas.winfo_height())

            page_h = max(
                280,
                min(
                    h - 110,
                    520,
                ),
            )
            page_w = page_h / 1.40
            gap = 15
            total_w = page_w * 2 + gap

            left_x = (w - total_w) / 2
            right_x = left_x + page_w + gap
            y1 = (h - page_h) / 2 + 2
            gutter_x = left_x + page_w + gap / 2

            return {
                "w": w,
                "h": h,
                "page_w": page_w,
                "page_h": page_h,
                "gap": gap,
                "total_w": total_w,
                "left_x": left_x,
                "right_x": right_x,
                "y1": y1,
                "gutter_x": gutter_x,
            }

        def support_photo(width, height):
            """Crée un présentoir rasterisé, vu du dessus.

            Le rendu est volontairement plus proche d'un objet photographié
            que d'une forme Tk : ombre floue, matière légèrement texturée,
            chanfrein clair et lèvres de maintien.
            """
            from PIL import ImageFilter as _ImageFilter

            width = max(220, int(width))
            height = max(180, int(height))
            key = (width, height)

            cached = getattr(
                win,
                "_book_views_support_cache",
                {},
            ).get(key)
            if cached is not None:
                return cached

            if not hasattr(win, "_book_views_support_cache"):
                win._book_views_support_cache = {}

            scale = 2
            sw = width * scale
            sh = height * scale

            image = Image.new(
                "RGBA",
                (sw, sh),
                (0, 0, 0, 0),
            )

            # Ombre très douce sous le socle.
            shadow = Image.new(
                "RGBA",
                (sw, sh),
                (0, 0, 0, 0),
            )
            sd = ImageDraw.Draw(shadow)
            pad = 22 * scale
            sd.rounded_rectangle(
                (
                    pad,
                    pad + 8 * scale,
                    sw - pad,
                    sh - pad + 5 * scale,
                ),
                radius=18 * scale,
                fill=(95, 82, 68, 70),
            )
            shadow = shadow.filter(
                _ImageFilter.GaussianBlur(12 * scale)
            )
            image.alpha_composite(shadow)

            # Corps du socle : ivoire chaud / bois laqué clair.
            plate = Image.new(
                "RGBA",
                (sw, sh),
                (0, 0, 0, 0),
            )
            pd = ImageDraw.Draw(plate)

            outer = (
                20 * scale,
                16 * scale,
                sw - 20 * scale,
                sh - 25 * scale,
            )
            pd.rounded_rectangle(
                outer,
                radius=17 * scale,
                fill=(223, 214, 202, 255),
                outline=(194, 183, 169, 255),
                width=1 * scale,
            )

            # Chanfrein progressif.
            bevel_colors = (
                (226, 217, 205, 255),
                (232, 224, 213, 255),
                (238, 231, 221, 255),
                (244, 239, 232, 255),
            )
            for i, color in enumerate(bevel_colors, start=1):
                inset = (20 + i * 3) * scale
                pd.rounded_rectangle(
                    (
                        inset,
                        (16 + i * 3) * scale,
                        sw - inset,
                        sh - (25 + i * 3) * scale,
                    ),
                    radius=max(5, (17 - i * 2) * scale),
                    fill=color,
                )

            # Texture très fine : irrégularités de matière, non décoratives.
            texture = Image.effect_noise(
                (sw, sh),
                10.0,
            ).convert("L")
            texture = texture.point(
                lambda value: int(232 + (value - 128) * 0.08)
            )
            texture_rgba = Image.merge(
                "RGBA",
                (
                    texture,
                    texture,
                    texture,
                    Image.new("L", (sw, sh), 30),
                ),
            )

            mask = Image.new("L", (sw, sh), 0)
            md = ImageDraw.Draw(mask)
            md.rounded_rectangle(
                (
                    30 * scale,
                    26 * scale,
                    sw - 30 * scale,
                    sh - 35 * scale,
                ),
                radius=12 * scale,
                fill=255,
            )
            texture_rgba.putalpha(
                Image.eval(
                    mask,
                    lambda a: int(a * 0.12)
                )
            )
            plate.alpha_composite(texture_rgba)

            pd = ImageDraw.Draw(plate)

            # Zone centrale légèrement satinée où repose le livre.
            pd.rounded_rectangle(
                (
                    38 * scale,
                    34 * scale,
                    sw - 38 * scale,
                    sh - 48 * scale,
                ),
                radius=10 * scale,
                fill=(248, 245, 239, 236),
                outline=(236, 230, 221, 255),
                width=1 * scale,
            )

            # Reflet supérieur doux.
            pd.line(
                (
                    52 * scale,
                    42 * scale,
                    sw - 52 * scale,
                    42 * scale,
                ),
                fill=(255, 255, 255, 210),
                width=1 * scale,
            )

            # Lèvre frontale du présentoir vue du dessus.
            lip_y = sh - 52 * scale
            pd.rounded_rectangle(
                (
                    48 * scale,
                    lip_y,
                    sw - 48 * scale,
                    lip_y + 16 * scale,
                ),
                radius=5 * scale,
                fill=(211, 200, 186, 255),
                outline=(190, 178, 163, 255),
                width=1 * scale,
            )
            pd.line(
                (
                    58 * scale,
                    lip_y + 2 * scale,
                    sw - 58 * scale,
                    lip_y + 2 * scale,
                ),
                fill=(252, 249, 244, 220),
                width=1 * scale,
            )

            # Deux petites retenues, comme sur un présentoir de librairie.
            stop_y = sh - 78 * scale
            stop_w = 55 * scale
            stop_h = 13 * scale
            for center_x in (
                int(sw * 0.29),
                int(sw * 0.71),
            ):
                pd.rounded_rectangle(
                    (
                        center_x - stop_w // 2,
                        stop_y,
                        center_x + stop_w // 2,
                        stop_y + stop_h,
                    ),
                    radius=4 * scale,
                    fill=(218, 208, 195, 255),
                    outline=(195, 183, 168, 255),
                    width=1 * scale,
                )
                pd.line(
                    (
                        center_x - stop_w // 2 + 8 * scale,
                        stop_y + 2 * scale,
                        center_x + stop_w // 2 - 8 * scale,
                        stop_y + 2 * scale,
                    ),
                    fill=(252, 250, 246, 235),
                    width=1 * scale,
                )

            # Relief central sous la reliure.
            center_x = sw // 2
            pd.rounded_rectangle(
                (
                    center_x - 9 * scale,
                    47 * scale,
                    center_x + 9 * scale,
                    sh - 72 * scale,
                ),
                radius=5 * scale,
                fill=(226, 218, 207, 180),
                outline=(205, 195, 182, 190),
                width=1 * scale,
            )

            image.alpha_composite(plate)

            image = image.resize(
                (width, height),
                Image.Resampling.LANCZOS,
            )

            photo = ImageTk.PhotoImage(image)
            win._book_views_support_cache[key] = photo
            return photo

        def draw_book_background(geometry):
            """Table de montage TomeLinea + socle de librairie vu du dessus."""
            w = geometry["w"]
            h = geometry["h"]
            left_x = geometry["left_x"]
            right_x = geometry["right_x"]
            y1 = geometry["y1"]
            page_w = geometry["page_w"]
            page_h = geometry["page_h"]

            margin = 34
            x1 = margin
            y_top = 18
            x2 = w - margin
            y2 = h - 24

            # Même table de montage que l'onglet Vue globale.
            book_canvas.create_polygon(
                polygon_points(
                    x1,
                    y_top,
                    x2,
                    y2,
                    cut=14,
                    dx=2,
                    dy=4,
                ),
                fill="#D7D2CA",
                outline="",
            )
            book_canvas.create_polygon(
                polygon_points(
                    x1,
                    y_top,
                    x2,
                    y2,
                    cut=14,
                ),
                fill=MOUNT,
                outline="#D8D3CB",
                width=1,
            )

            gx = x1 + 38
            while gx < x2 - 20:
                book_canvas.create_line(
                    gx,
                    y_top + 14,
                    gx,
                    y2 - 14,
                    fill=GRID,
                    width=1,
                )
                gx += 96

            gy = y_top + 28
            while gy < y2 - 16:
                book_canvas.create_line(
                    x1 + 14,
                    gy,
                    x2 - 14,
                    gy,
                    fill=GRID,
                    width=1,
                )
                gy += 44

            # Le socle est une vraie image raster texturée, et non plus
            # un assemblage de polygones Tk.
            stand_x = left_x - 42
            stand_y = y1 - 28
            stand_w = int((right_x + page_w + 42) - stand_x)
            stand_h = int(page_h + 70)

            photo = support_photo(
                stand_w,
                stand_h,
            )
            book_canvas.create_image(
                stand_x,
                stand_y,
                image=photo,
                anchor="nw",
            )

            # Ombre très locale du livre sur le plateau.
            book_canvas.create_oval(
                left_x + 24,
                y1 + page_h - 7,
                right_x + page_w - 24,
                y1 + page_h + 13,
                fill="#D9D1C6",
                outline="",
            )

        def draw_gutter(geometry):
            gutter_x = geometry["gutter_x"]
            y1 = geometry["y1"]
            page_h = geometry["page_h"]

            book_canvas.create_line(
                gutter_x,
                y1 + 4,
                gutter_x,
                y1 + page_h - 4,
                fill="#6F655C",
                width=3,
            )
            book_canvas.create_line(
                gutter_x - 5,
                y1 + 8,
                gutter_x - 2,
                y1 + page_h - 8,
                fill="#B7AEA5",
                width=1,
            )
            book_canvas.create_line(
                gutter_x + 2,
                y1 + 8,
                gutter_x + 5,
                y1 + page_h - 8,
                fill="#B7AEA5",
                width=1,
            )

        def page_at(index):
            if 0 <= index < len(pages):
                return pages[index]
            return None

        def draw_spread(
            left_page,
            right_page,
            *,
            show_controls=True,
        ):
            geometry = book_geometry()
            draw_book_background(geometry)

            left_x = geometry["left_x"]
            right_x = geometry["right_x"]
            y1 = geometry["y1"]
            page_w = geometry["page_w"]
            page_h = geometry["page_h"]
            h = geometry["h"]
            w = geometry["w"]

            draw_large_page(
                book_canvas,
                left_page,
                left_x,
                y1,
                left_x + page_w,
                y1 + page_h,
                blank=left_page is None,
            )
            draw_large_page(
                book_canvas,
                right_page,
                right_x,
                y1,
                right_x + page_w,
                y1 + page_h,
                blank=right_page is None,
            )

            draw_gutter(geometry)

            return geometry

        # FEUILLETER_PAGINATION_RETIRÉE_SOURCE_V18
        # Maquettage : aucune pagination affichée dans Feuilleter.
        # Elle sera gérée plus tard par le bureau Visualisation.
        def render_book(_event=None):
            if resize_fx["active"] or flip_state["active"]:
                return

            book_canvas.delete("all")

            li = spread_left[0]
            ri = li + 1
            left_page = page_at(li)
            right_page = page_at(ri)

            draw_spread(
                left_page,
                right_page,
                show_controls=True,
            )

        def draw_turning_page(
            page,
            x1,
            y1,
            x2,
            y2,
            *,
            shade=0.0,
            edge_x=None,
        ):
            width = max(1.0, x2 - x1)
            height = max(1.0, y2 - y1)

            if width <= 3:
                xx = (
                    edge_x
                    if edge_x is not None
                    else (x1 + x2) / 2
                )
                book_canvas.create_line(
                    xx,
                    y1 + 2,
                    xx,
                    y2 - 2,
                    fill="#6B6259",
                    width=3,
                )
                return

            book_canvas.create_rectangle(
                x1 + 3,
                y1 + 5,
                x2 + 3,
                y2 + 5,
                fill="#81786F",
                outline="",
            )
            book_canvas.create_rectangle(
                x1,
                y1,
                x2,
                y2,
                fill="#FFFEFB",
                outline="#AFA79F",
                width=1,
            )

            photo = animated_page_photo(
                page,
                max(2, int(width - 4)),
                max(2, int(height - 4)),
                shade=shade,
            )
            book_canvas.create_image(
                (x1 + x2) / 2,
                (y1 + y2) / 2,
                image=photo,
                anchor="center",
            )

            # Bord mobile plus sombre : donne l'impression d'épaisseur.
            if edge_x is not None:
                for offset, color in (
                    (0, "#625A52"),
                    (2, "#8A8178"),
                    (4, "#B0A79D"),
                ):
                    book_canvas.create_line(
                        edge_x + offset,
                        y1 + 2,
                        edge_x + offset,
                        y2 - 2,
                        fill=color,
                        width=1,
                    )

        def animate_page_turn(direction):
            if (
                flip_state["active"]
                or resize_fx["active"]
                or state["tab"] != "feuilleter"
            ):
                return

            current = spread_left[0]

            if direction > 0:
                target = current + 2
                if target > len(pages) - 1:
                    return
            else:
                target = current - 2
                if target < -1:
                    return

            current_left = page_at(current)
            current_right = page_at(current + 1)
            target_left = page_at(target)
            target_right = page_at(target + 1)

            flip_state["active"] = True
            flip_state["direction"] = 1 if direction > 0 else -1

            if flip_state["after"] is not None:
                try:
                    win.after_cancel(flip_state["after"])
                except Exception:
                    pass
                flip_state["after"] = None

            frames = 22
            frame_ms = 15

            def frame(index):
                if not win.winfo_exists():
                    return

                t = index / frames
                # Accélération/décélération douce du geste.
                eased = (
                    t * t * t
                    * (
                        t * (t * 6.0 - 15.0)
                        + 10.0
                    )
                )

                book_canvas.delete("all")
                geometry = book_geometry()

                left_x = geometry["left_x"]
                right_x = geometry["right_x"]
                y1 = geometry["y1"]
                page_w = geometry["page_w"]
                page_h = geometry["page_h"]
                gutter_left = left_x + page_w
                gutter_right = right_x

                if direction > 0:
                    if eased < 0.5:
                        phase = eased / 0.5

                        # La page droite actuelle se referme vers la reliure.
                        draw_spread(
                            current_left,
                            target_right,
                            show_controls=False,
                        )

                        fraction = max(0.0, 1.0 - phase)
                        moving_w = page_w * fraction
                        bend = int(
                            13 * (1.0 - fraction)
                        )

                        x1 = gutter_right
                        x2 = gutter_right + moving_w

                        draw_turning_page(
                            current_right,
                            x1,
                            y1 + bend,
                            x2,
                            y1 + page_h - bend,
                            shade=0.20 * (1.0 - fraction),
                            edge_x=x2,
                        )
                    else:
                        phase = (eased - 0.5) / 0.5

                        # Le verso devient la nouvelle page gauche.
                        draw_spread(
                            current_left,
                            target_right,
                            show_controls=False,
                        )

                        fraction = max(0.0, min(1.0, phase))
                        moving_w = page_w * fraction
                        bend = int(
                            13 * (1.0 - fraction)
                        )

                        x2 = gutter_left
                        x1 = gutter_left - moving_w

                        draw_turning_page(
                            target_left,
                            x1,
                            y1 + bend,
                            x2,
                            y1 + page_h - bend,
                            shade=0.20 * (1.0 - fraction),
                            edge_x=x1,
                        )

                else:
                    if eased < 0.5:
                        phase = eased / 0.5

                        # La page gauche actuelle revient vers la reliure.
                        draw_spread(
                            target_left,
                            current_right,
                            show_controls=False,
                        )

                        fraction = max(0.0, 1.0 - phase)
                        moving_w = page_w * fraction
                        bend = int(
                            13 * (1.0 - fraction)
                        )

                        x2 = gutter_left
                        x1 = gutter_left - moving_w

                        draw_turning_page(
                            current_left,
                            x1,
                            y1 + bend,
                            x2,
                            y1 + page_h - bend,
                            shade=0.20 * (1.0 - fraction),
                            edge_x=x1,
                        )
                    else:
                        phase = (eased - 0.5) / 0.5

                        # Le verso redevient la page droite précédente.
                        draw_spread(
                            target_left,
                            current_right,
                            show_controls=False,
                        )

                        fraction = max(0.0, min(1.0, phase))
                        moving_w = page_w * fraction
                        bend = int(
                            13 * (1.0 - fraction)
                        )

                        x1 = gutter_right
                        x2 = gutter_right + moving_w

                        draw_turning_page(
                            target_right,
                            x1,
                            y1 + bend,
                            x2,
                            y1 + page_h - bend,
                            shade=0.20 * (1.0 - fraction),
                            edge_x=x2,
                        )

                # Ombre dynamique dans la reliure.
                shadow_strength = 1.0 - abs(eased - 0.5) * 2.0
                shadow_strength = max(
                    0.0,
                    min(1.0, shadow_strength),
                )
                gutter = geometry["gutter_x"]

                for offset, color in (
                    (0, "#5F564E"),
                    (3, "#7A7067"),
                    (6, "#A59B92"),
                ):
                    book_canvas.create_line(
                        gutter + (
                            offset
                            if direction > 0
                            else -offset
                        ),
                        y1 + 8,
                        gutter + (
                            offset
                            if direction > 0
                            else -offset
                        ),
                        y1 + page_h - 8,
                        fill=color,
                        width=(
                            2
                            if shadow_strength > 0.45
                            else 1
                        ),
                    )

                if index < frames:
                    flip_state["after"] = win.after(
                        frame_ms,
                        lambda: frame(index + 1),
                    )
                else:
                    spread_left[0] = target
                    flip_state["active"] = False
                    flip_state["direction"] = 0
                    flip_state["after"] = None
                    win._book_views_turn_frames = []
                    render_book()

            frame(0)

        def turn(step):
            animate_page_turn(
                1 if step > 0 else -1
            )

        def book_click(event):
            if flip_state["active"] or resize_fx["active"]:
                return

            w = max(740, book_canvas.winfo_width())

            # Toute la moitié droite avance, toute la moitié gauche recule.
            if event.x >= w / 2:
                turn(1)
            else:
                turn(-1)

        def book_wheel(event):
            if state["tab"] != "feuilleter":
                return None
            if getattr(event, "delta", 0):
                turn(
                    1
                    if event.delta < 0
                    else -1
                )
                return "break"
            return None

        book_canvas.bind(
            "<Configure>",
            lambda event: (
                render_book(event)
                if state["tab"] == "feuilleter"
                else None
            ),
        )
        book_canvas.bind("<Button-1>", book_click)

        # ----------------------------------------------------------
        # Changement de vue V14 : responsabilités réellement séparées.
        #
        # - set_visual_panel() ne modifie QUE le panneau interne.
        # - show_book_view() ne modifie QUE l'onglet et l'empilement.
        # - la Toplevel native ne reçoit AUCUNE geometry() au clic.
        # ----------------------------------------------------------
        switch_state = {
            "active": False,
        }

        def set_visual_panel(key):
            """Responsabilité unique : taille visuelle interne."""
            visual_state["mode"] = key
            redraw_shell()

        def show_book_view(key):
            """Responsabilité unique : sélection de l'onglet."""
            state["tab"] = key

            if key == "global":
                subtitle_label.configure(
                    text=(
                        "Vue panoramique de l’ordre des pages et des parties. "
                        "Cliquez-glissez pour parcourir le livre."
                    )
                )
                global_host.tkraise()
            else:
                subtitle_label.configure(
                    text=(
                        "Cliquez à gauche ou à droite sur le livre "
                        "pour tourner les pages."
                    )
                )
                book_host.tkraise()

            draw_tabs()

        def render_active_view():
            """Rend uniquement la vue visible, après layout interne."""
            draw_title_line()
            if state["tab"] == "global":
                draw_global()
            else:
                render_book()

        def change_book_mode(key):
            if key not in ("global", "feuilleter"):
                return
            if (
                switch_state["active"]
                or flip_state["active"]
                or key == state["tab"]
            ):
                return

            switch_state["active"] = True
            try:
                # 1. changement d'onglet ; 2. layout interne ;
                # jamais de redimensionnement de la fenêtre Windows.
                show_book_view(key)
                set_visual_panel(key)
                win.update_idletasks()
                render_active_view()
            finally:
                switch_state["active"] = False

        def show_tab(key, *, animate=True):
            change_book_mode(key)

        def tabs_motion(event):
            key = tab_at(event.x, event.y)
            if key != state["tab_hover"]:
                state["tab_hover"] = key
                tabs.configure(
                    cursor="hand2" if key else "arrow"
                )
                draw_tabs()

        def tabs_leave(_event=None):
            state["tab_hover"] = None
            tabs.configure(cursor="arrow")
            draw_tabs()

        def tabs_click(event):
            key = tab_at(event.x, event.y)
            if key is not None and key != state["tab"]:
                show_tab(key, animate=True)

        tabs.bind("<Motion>", tabs_motion)
        tabs.bind("<Leave>", tabs_leave)
        tabs.bind("<Button-1>", tabs_click)

        win.bind("<MouseWheel>", global_wheel, add="+")
        win.bind("<MouseWheel>", book_wheel, add="+")
        win.bind(
            "<Right>",
            lambda _e: (
                turn(1)
                if state["tab"] == "feuilleter"
                else panorama.xview_scroll(5, "units")
            ),
        )
        win.bind(
            "<Left>",
            lambda _e: (
                turn(-1)
                if state["tab"] == "feuilleter"
                else panorama.xview_scroll(-5, "units")
            ),
        )
        win.bind(
            "<Next>",
            lambda _e: (
                turn(1)
                if state["tab"] == "feuilleter"
                else None
            ),
        )
        win.bind(
            "<Prior>",
            lambda _e: (
                turn(-1)
                if state["tab"] == "feuilleter"
                else None
            ),
        )
        win.bind("<Escape>", lambda _e: win.destroy())

        # ----------------------------------------------------------
        # Première apparition : préchauffage des DEUX layouts internes.
        # La Toplevel reste fixe pendant toute cette phase invisible.
        # ----------------------------------------------------------
        initial_key = state["tab"]

        # Prépare Vue globale.
        show_book_view("global")
        set_visual_panel("global")
        win.update_idletasks()
        draw_global()

        # Prépare Feuilleter.
        show_book_view("feuilleter")
        set_visual_panel("feuilleter")
        win.update_idletasks()
        render_book()

        # Restaure l'onglet demandé avant révélation.
        show_book_view(initial_key)
        set_visual_panel(initial_key)
        win.update_idletasks()
        render_active_view()

        if hasattr(self, "_reveal_accueil_dialog"):
            self._reveal_accueil_dialog(win)
        else:
            win.deiconify()
            try:
                win.attributes("-alpha", 1.0)
            except tk.TclError:
                pass

        win.focus_force()
        return win
    def _tomelinea_open_global_view(self):
        """Compatibilité : ouvre la fenêtre unifiée sur Vue globale."""
        return self._tomelinea_open_book_views("global")

    def _tomelinea_open_book_view(self):
        """Compatibilité : ouvre la fenêtre unifiée sur Feuilleter."""
        return self._tomelinea_open_book_views("feuilleter")


    # FENETRES_BASE_PARTIE_TYPE_V1
    # Fenêtres volontairement minimales : elles servent uniquement de base
    # aux futures fonctions du Maquettage.

    # FENETRE_AJOUT_PARTIE_NATIVE_MAQUETTAGE_V1
    def _tomelinea_open_add_part_window(self):
        win = tk.Toplevel(self)
        win.title("TomeLinea — Ajouter une partie")

        # Même cycle d'apparition atomique que les autres fenêtres validées.
        self._prepare_accueil_dialog(win)
        self._accueil_center_base_window(win, 650, 430)
        win.configure(bg="#F6F2EA")

        canvas = tk.Canvas(
            win,
            bg="#F6F2EA",
            highlightthickness=0,
            bd=0,
        )
        canvas.pack(fill="both", expand=True)

        # --------------------------------------------------------------
        # Fond identique au bureau Maquettage.
        # --------------------------------------------------------------
        bg_path = (
            PROJECT_ROOT
            / "assets"
            / "gui_v2"
            / "maquettage_backgrounds"
            / "maquettage_studio_pro.png"
        )

        win._tomelinea_add_part_bg_source = None
        win._tomelinea_add_part_bg_photo = None

        try:
            if bg_path.exists():
                win._tomelinea_add_part_bg_source = Image.open(
                    bg_path
                ).convert("RGB")
        except Exception:
            win._tomelinea_add_part_bg_source = None

        PANEL = "#FFFEFC"
        FIELD = "#FBFAF7"
        INK = "#25323E"
        MUTED = "#68717A"
        NAVY = "#173E70"
        BORDER = "#BFC7D0"

        panel = tk.Frame(
            canvas,
            bg=PANEL,
            bd=0,
            highlightthickness=0,
        )
        panel_id = canvas.create_window(
            48,
            34,
            anchor="nw",
            window=panel,
        )

        def _panel_points(x1, y1, x2, y2, cut=18, dx=0, dy=0):
            return [
                x1 + dx, y1 + dy,
                x2 - cut + dx, y1 + dy,
                x2 + dx, y1 + cut + dy,
                x2 + dx, y2 + dy,
                x1 + cut + dx, y2 + dy,
                x1 + dx, y2 - cut + dy,
            ]

        def _redraw(_event=None):
            width = max(canvas.winfo_width(), 650)
            height = max(canvas.winfo_height(), 430)

            canvas.delete("add_part_bg")
            canvas.delete("add_part_panel")

            if win._tomelinea_add_part_bg_source is not None:
                try:
                    image = win._tomelinea_add_part_bg_source.resize(
                        (width, height),
                        Image.Resampling.LANCZOS,
                    )
                    image = Image.blend(
                        image.convert("RGB"),
                        Image.new("RGB", image.size, "#D7D9DC"),
                        0.10,
                    )
                    win._tomelinea_add_part_bg_photo = ImageTk.PhotoImage(image)
                    canvas.create_image(
                        0,
                        0,
                        image=win._tomelinea_add_part_bg_photo,
                        anchor="nw",
                        tags=("add_part_bg",),
                    )
                except Exception:
                    canvas.create_rectangle(
                        0, 0, width, height,
                        fill="#EEEDEA",
                        outline="",
                        tags=("add_part_bg",),
                    )
            else:
                canvas.create_rectangle(
                    0, 0, width, height,
                    fill="#EEEDEA",
                    outline="",
                    tags=("add_part_bg",),
                )

            x1, y1 = 22, 18
            x2, y2 = width - 22, height - 18

            canvas.create_polygon(
                _panel_points(x1, y1, x2, y2, dx=2, dy=4),
                fill="#D3CEC5",
                outline="",
                tags=("add_part_panel",),
            )
            canvas.create_polygon(
                _panel_points(x1, y1, x2, y2),
                fill=PANEL,
                outline="#D5D1CA",
                width=1,
                tags=("add_part_panel",),
            )

            # Rail violet = Maquettage / Structure.
            canvas.create_line(
                x1 + 4,
                y1 + 19,
                x1 + 4,
                y2 - 19,
                fill="#8D70C7",
                width=4,
                tags=("add_part_panel",),
            )

            canvas.coords(panel_id, x1 + 28, y1 + 20)
            canvas.itemconfigure(
                panel_id,
                width=max(500, x2 - x1 - 56),
                height=max(320, y2 - y1 - 40),
            )

            canvas.tag_lower("add_part_panel")
            canvas.tag_lower("add_part_bg")

        canvas.bind("<Configure>", _redraw)
        win._tomelinea_dialog_redraw = _redraw

        # --------------------------------------------------------------
        # Petits composants TomeLinea locaux.
        # --------------------------------------------------------------
        def _round_rect(c, x1, y1, x2, y2, radius, **kwargs):
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
            return c.create_polygon(
                pts,
                smooth=True,
                splinesteps=22,
                **kwargs,
            )

        def _make_button(
            parent,
            *,
            text,
            command,
            primary=False,
            min_width=112,
            enabled=True,
        ):
            width = max(min_width, int(len(text) * 7.2) + 34)
            height = 36

            btn = tk.Canvas(
                parent,
                width=width + 5,
                height=height + 6,
                bg=PANEL,
                highlightthickness=0,
                bd=0,
                cursor="hand2" if enabled else "arrow",
                takefocus=0,
            )

            state = {
                "enabled": bool(enabled),
                "hover": False,
                "pressed": False,
                "command": command,
            }

            def draw():
                btn.delete("all")

                active = state["enabled"]
                hover = state["hover"] and active
                pressed = state["pressed"] and active
                dy = 1 if pressed else 0

                if primary:
                    if not active:
                        face, outline, fg = "#D9DEE4", "#C9CFD5", "#9299A0"
                        shadow, shadow_y = "#E0E2E4", 1
                    elif pressed:
                        face, outline, fg = "#12345F", "#12345F", "#FFFFFF"
                        shadow, shadow_y = "#AEB7C0", 1
                    elif hover:
                        face, outline, fg = "#24558A", "#24558A", "#FFFFFF"
                        shadow, shadow_y = "#B9C0C7", 3
                    else:
                        face, outline, fg = "#173E70", "#173E70", "#FFFFFF"
                        shadow, shadow_y = "#C6CBD0", 2
                else:
                    if not active:
                        face, outline, fg = "#F1F0ED", "#DDDAD4", "#A0A5AA"
                        shadow, shadow_y = "#E5E2DD", 1
                    elif pressed:
                        face, outline, fg = "#E9F0F7", "#355C85", "#173E70"
                        shadow, shadow_y = "#BFC7CF", 1
                    elif hover:
                        face, outline, fg = "#F3F7FB", "#496D94", "#173E70"
                        shadow, shadow_y = "#C4CBD2", 3
                    else:
                        face, outline, fg = "#FFFDFC", "#BFC7D0", "#173E70"
                        shadow, shadow_y = "#CDD2D6", 2

                x1, y1 = 2, 1 + dy
                x2, y2 = width + 1, height + dy

                _round_rect(
                    btn,
                    x1 + 1,
                    y1 + shadow_y,
                    x2 + 1,
                    y2 + shadow_y,
                    8,
                    fill=shadow,
                    outline="",
                )
                _round_rect(
                    btn,
                    x1,
                    y1,
                    x2,
                    y2,
                    8,
                    fill=face,
                    outline=outline,
                    width=1,
                )
                btn.create_text(
                    (x1 + x2) / 2,
                    (y1 + y2) / 2,
                    text=text,
                    fill=fg,
                    font=("Segoe UI", 9, "bold" if primary else "normal"),
                    anchor="center",
                )

            def set_enabled(value):
                state["enabled"] = bool(value)
                state["hover"] = False
                state["pressed"] = False
                btn.configure(
                    cursor="hand2" if state["enabled"] else "arrow"
                )
                draw()

            def enter(_event=None):
                if state["enabled"]:
                    state["hover"] = True
                    draw()

            def leave(_event=None):
                state["hover"] = False
                state["pressed"] = False
                draw()

            def press(_event=None):
                if state["enabled"]:
                    state["pressed"] = True
                    draw()

            def release(_event=None):
                if not state["enabled"]:
                    return
                state["pressed"] = False
                state["hover"] = True
                draw()
                action = state.get("command")
                if callable(action):
                    action()

            btn.bind("<Enter>", enter)
            btn.bind("<Leave>", leave)
            btn.bind("<ButtonPress-1>", press)
            btn.bind("<ButtonRelease-1>", release)
            btn.set_enabled = set_enabled
            draw()
            return btn

        def _title_row(parent, text):
            row = tk.Frame(parent, bg=PANEL)
            row.pack(fill="x")

            label = tk.Label(
                row,
                text=text,
                bg=PANEL,
                fg=theme.INK,
                font=("Georgia", 15, "bold"),
            )
            label.pack(side="left")

            line = tk.Canvas(
                row,
                height=22,
                bg=PANEL,
                highlightthickness=0,
                bd=0,
            )
            line.pack(side="left", fill="x", expand=True, padx=(16, 0))

            def draw_line(_event=None):
                line.delete("all")
                w = max(line.winfo_width(), 40)
                y = 11
                line.create_line(
                    0,
                    y,
                    max(0, w - 8),
                    y,
                    fill="#202020",
                    width=1,
                )
                line.create_oval(
                    max(0, w - 9),
                    y - 3,
                    max(0, w - 3),
                    y + 3,
                    fill=PANEL,
                    outline="#202020",
                    width=1,
                )

            line.bind("<Configure>", draw_line)
            line.after_idle(draw_line)

        def _field(parent, label_text, initial=""):
            holder = tk.Frame(parent, bg=PANEL)
            holder.pack(fill="x", pady=(0, 10))

            tk.Label(
                holder,
                text=label_text,
                bg=PANEL,
                fg="#4F5963",
                font=("Segoe UI", 8, "bold"),
            ).pack(anchor="w")

            field_frame = tk.Frame(
                holder,
                bg=FIELD,
                highlightthickness=1,
                highlightbackground=BORDER,
                padx=8,
                pady=6,
            )
            field_frame.pack(fill="x", pady=(4, 0))

            var = tk.StringVar(value=initial)
            entry = tk.Entry(
                field_frame,
                textvariable=var,
                bg=FIELD,
                fg=INK,
                insertbackground=NAVY,
                relief="flat",
                bd=0,
                highlightthickness=0,
                font=("Segoe UI", 9),
            )
            entry.pack(fill="x")
            return var, entry

        # --------------------------------------------------------------
        # Titre / intro.
        # --------------------------------------------------------------
        _title_row(panel, "Ajouter une partie")

        tk.Label(
            panel,
            text="Ajoutez une nouvelle partie à la structure du livre.",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 8),
        ).pack(anchor="w", pady=(5, 18))

        # --------------------------------------------------------------
        # Formulaire.
        # --------------------------------------------------------------
        form = tk.Frame(panel, bg=PANEL)
        form.pack(fill="x")

        name_var, name_entry = _field(
            form,
            "Nom de la partie",
            "Nouvelle partie",
        )

        pages_var, _pages_entry = _field(
            form,
            "Pages prévues",
            "12",
        )

        # Position : champ visuel TomeLinea + menu contextuel simple.
        position_holder = tk.Frame(form, bg=PANEL)
        position_holder.pack(fill="x", pady=(0, 10))

        tk.Label(
            position_holder,
            text="Position",
            bg=PANEL,
            fg="#4F5963",
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w")

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

        selector = tk.Frame(
            position_holder,
            bg=FIELD,
            highlightthickness=1,
            highlightbackground=BORDER,
            height=34,
        )
        selector.pack(fill="x", pady=(4, 0))
        selector.pack_propagate(False)

        position_label = tk.Label(
            selector,
            textvariable=position_var,
            bg=FIELD,
            fg=INK,
            font=("Segoe UI", 9),
            anchor="w",
            padx=9,
            cursor="hand2",
        )
        position_label.pack(side="left", fill="both", expand=True)

        arrow_label = tk.Label(
            selector,
            text="⌄",
            bg=FIELD,
            fg="#56708A",
            font=("Segoe UI", 11, "bold"),
            width=3,
            cursor="hand2",
        )
        arrow_label.pack(side="right", fill="y")

        menu = tk.Menu(
            win,
            tearoff=False,
            bg="#FFFEFC",
            fg=INK,
            activebackground="#F3F7FB",
            activeforeground=NAVY,
            bd=1,
            relief="solid",
            font=("Segoe UI", 9),
        )

        for choice in choices:
            menu.add_command(
                label=choice,
                command=lambda value=choice: position_var.set(value),
            )

        def _open_position_menu(event=None):
            try:
                x = selector.winfo_rootx()
                y = selector.winfo_rooty() + selector.winfo_height()
                menu.tk_popup(x, y)
            finally:
                try:
                    menu.grab_release()
                except Exception:
                    pass

        position_label.bind("<Button-1>", _open_position_menu)
        arrow_label.bind("<Button-1>", _open_position_menu)
        selector.bind("<Button-1>", _open_position_menu)

        # Repère fonctionnel discret.
        note = tk.Frame(panel, bg=PANEL)
        note.pack(fill="x", pady=(7, 0))

        tk.Frame(
            note,
            bg="#DDD8D1",
            height=1,
        ).pack(fill="x", pady=(0, 10))

        tk.Label(
            note,
            text="Début et Fin restent les bornes fixes du livre.",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 8),
        ).pack(anchor="w")

        # --------------------------------------------------------------
        # Actions.
        # --------------------------------------------------------------
        actions = tk.Frame(panel, bg=PANEL)
        actions.pack(side="bottom", fill="x", pady=(16, 0))

        close_button = _make_button(
            actions,
            text="Fermer",
            command=win.destroy,
            primary=False,
            min_width=100,
            enabled=True,
        )
        close_button.pack(side="right")

        # La logique métier n'est toujours pas active : bouton volontairement inactif.
        add_button = _make_button(
            actions,
            text="Ajouter la partie   ›",
            command=lambda: None,
            primary=True,
            min_width=150,
            enabled=False,
        )
        add_button.pack(side="right", padx=(0, 10))

        self._reveal_accueil_dialog(win)
        try:
            name_entry.focus_set()
            name_entry.selection_range(0, "end")
        except Exception:
            pass


    # FENETRE_TYPE_PAGE_TOMELINEA_V1
    # FENETRE_TYPE_PAGE_NATIVE_MAQUETTAGE_V4
    def _tomelinea_open_page_type_window(self, group_name="Partie"):
        # Fenêtre native Maquettage :
        # même fond, mêmes panneaux, mêmes boutons, mêmes aperçus de pages.
        from tkinter import filedialog as _filedialog

        win = tk.Toplevel(self)
        win.title("TomeLinea — Créer / choisir un type")
        self._prepare_accueil_dialog(win)
        self._accueil_center_base_window(win, 940, 620)
        win.configure(bg="#F6F2EA")

        # ------------------------------------------------------------------
        # Fond Maquettage identique au bureau : image + même voile gris doux.
        # ------------------------------------------------------------------
        canvas = tk.Canvas(
            win,
            bg="#F6F2EA",
            highlightthickness=0,
            bd=0,
        )
        canvas.pack(fill="both", expand=True)

        maquettage_bg_path = (
            PROJECT_ROOT
            / "assets"
            / "gui_v2"
            / "maquettage_backgrounds"
            / "maquettage_studio_pro.png"
        )

        win._tomelinea_type_bg_source = None
        win._tomelinea_type_bg_photo = None

        try:
            if maquettage_bg_path.exists():
                win._tomelinea_type_bg_source = Image.open(
                    maquettage_bg_path
                ).convert("RGB")
        except Exception:
            win._tomelinea_type_bg_source = None

        # ------------------------------------------------------------------
        # Panneau principal : copie du langage des zones du Maquettage.
        # ------------------------------------------------------------------
        panel = tk.Frame(
            canvas,
            bg="#FFFEFC",
            bd=0,
            highlightthickness=0,
        )
        panel_id = canvas.create_window(
            54,
            38,
            anchor="nw",
            window=panel,
        )

        def _panel_points(x1, y1, x2, y2, cut=20, dx=0, dy=0):
            return [
                x1 + dx, y1 + dy,
                x2 - cut + dx, y1 + dy,
                x2 + dx, y1 + cut + dy,
                x2 + dx, y2 + dy,
                x1 + cut + dx, y2 + dy,
                x1 + dx, y2 - cut + dy,
            ]

        def _redraw_dialog(_event=None):
            width = max(canvas.winfo_width(), 940)
            height = max(canvas.winfo_height(), 620)

            canvas.delete("type_dialog_bg")
            canvas.delete("type_dialog_panel")

            if win._tomelinea_type_bg_source is not None:
                try:
                    image = win._tomelinea_type_bg_source.resize(
                        (width, height),
                        Image.Resampling.LANCZOS,
                    )
                    image = Image.blend(
                        image.convert("RGB"),
                        Image.new("RGB", image.size, "#D7D9DC"),
                        0.10,
                    )
                    win._tomelinea_type_bg_photo = ImageTk.PhotoImage(image)
                    canvas.create_image(
                        0,
                        0,
                        image=win._tomelinea_type_bg_photo,
                        anchor="nw",
                        tags=("type_dialog_bg",),
                    )
                except Exception:
                    canvas.create_rectangle(
                        0, 0, width, height,
                        fill="#EEEDEA",
                        outline="",
                        tags=("type_dialog_bg",),
                    )
            else:
                canvas.create_rectangle(
                    0, 0, width, height,
                    fill="#EEEDEA",
                    outline="",
                    tags=("type_dialog_bg",),
                )

            x1, y1 = 24, 18
            x2, y2 = width - 24, height - 18

            canvas.create_polygon(
                _panel_points(x1, y1, x2, y2, dx=2, dy=4),
                fill="#D3CEC5",
                outline="",
                tags=("type_dialog_panel",),
            )
            canvas.create_polygon(
                _panel_points(x1, y1, x2, y2),
                fill="#FFFEFC",
                outline="#D5D1CA",
                width=1,
                tags=("type_dialog_panel",),
            )

            # Rail violet = Maquettage / Composition.
            canvas.create_line(
                x1 + 4,
                y1 + 20,
                x1 + 4,
                y2 - 20,
                fill="#8D70C7",
                width=4,
                tags=("type_dialog_panel",),
            )

            canvas.coords(panel_id, x1 + 28, y1 + 20)
            canvas.itemconfigure(
                panel_id,
                width=max(760, x2 - x1 - 56),
                height=max(430, y2 - y1 - 40),
            )

            canvas.tag_lower("type_dialog_panel")
            canvas.tag_lower("type_dialog_bg")

        canvas.bind("<Configure>", _redraw_dialog)
        win._tomelinea_dialog_redraw = _redraw_dialog

        # ------------------------------------------------------------------
        # Palette / composants locaux.
        # ------------------------------------------------------------------
        PANEL = "#FFFEFC"
        SOFT = "#F8F6F2"
        FIELD = "#FBFAF7"
        INK = "#25323E"
        MUTED = "#68717A"
        NAVY = "#173E70"
        BORDER = "#D2CEC7"
        BORDER_STRONG = "#BFC7D0"

        def _round_rect(c, x1, y1, x2, y2, radius, **kwargs):
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
            return c.create_polygon(
                pts,
                smooth=True,
                splinesteps=22,
                **kwargs,
            )

        def _make_tl_button(
            parent,
            *,
            text,
            command,
            primary=False,
            min_width=118,
            enabled=True,
        ):
            width = max(min_width, int(len(text) * 7.2) + 34)
            height = 36

            btn = tk.Canvas(
                parent,
                width=width + 5,
                height=height + 6,
                bg=PANEL,
                highlightthickness=0,
                bd=0,
                cursor="hand2" if enabled else "arrow",
                takefocus=0,
            )

            state = {
                "enabled": bool(enabled),
                "hover": False,
                "pressed": False,
                "command": command,
            }

            def draw():
                btn.delete("all")

                active = state["enabled"]
                hover = state["hover"] and active
                pressed = state["pressed"] and active
                dy = 1 if pressed else 0

                if primary:
                    if not active:
                        face, outline, fg = "#D9DEE4", "#C9CFD5", "#9299A0"
                        shadow, shadow_y = "#E0E2E4", 1
                    elif pressed:
                        face, outline, fg = "#12345F", "#12345F", "#FFFFFF"
                        shadow, shadow_y = "#AEB7C0", 1
                    elif hover:
                        face, outline, fg = "#24558A", "#24558A", "#FFFFFF"
                        shadow, shadow_y = "#B9C0C7", 3
                    else:
                        face, outline, fg = "#173E70", "#173E70", "#FFFFFF"
                        shadow, shadow_y = "#C6CBD0", 2
                else:
                    if not active:
                        face, outline, fg = "#F1F0ED", "#DDDAD4", "#A0A5AA"
                        shadow, shadow_y = "#E5E2DD", 1
                    elif pressed:
                        face, outline, fg = "#E9F0F7", "#355C85", "#173E70"
                        shadow, shadow_y = "#BFC7CF", 1
                    elif hover:
                        face, outline, fg = "#F3F7FB", "#496D94", "#173E70"
                        shadow, shadow_y = "#C4CBD2", 3
                    else:
                        face, outline, fg = "#FFFDFC", "#BFC7D0", "#173E70"
                        shadow, shadow_y = "#CDD2D6", 2

                x1, y1 = 2, 1 + dy
                x2, y2 = width + 1, height + dy

                _round_rect(
                    btn,
                    x1 + 1,
                    y1 + shadow_y,
                    x2 + 1,
                    y2 + shadow_y,
                    8,
                    fill=shadow,
                    outline="",
                )
                _round_rect(
                    btn,
                    x1,
                    y1,
                    x2,
                    y2,
                    8,
                    fill=face,
                    outline=outline,
                    width=1,
                )
                btn.create_text(
                    (x1 + x2) / 2,
                    (y1 + y2) / 2,
                    text=text,
                    fill=fg,
                    font=("Segoe UI", 9, "bold" if primary else "normal"),
                    anchor="center",
                )

            def set_enabled(value):
                state["enabled"] = bool(value)
                state["hover"] = False
                state["pressed"] = False
                btn.configure(
                    cursor="hand2" if state["enabled"] else "arrow"
                )
                draw()

            def enter(_event=None):
                if state["enabled"]:
                    state["hover"] = True
                    draw()

            def leave(_event=None):
                state["hover"] = False
                state["pressed"] = False
                draw()

            def press(_event=None):
                if state["enabled"]:
                    state["pressed"] = True
                    draw()

            def release(_event=None):
                if not state["enabled"]:
                    return
                state["pressed"] = False
                state["hover"] = True
                draw()
                action = state.get("command")
                if callable(action):
                    action()

            btn.bind("<Enter>", enter)
            btn.bind("<Leave>", leave)
            btn.bind("<ButtonPress-1>", press)
            btn.bind("<ButtonRelease-1>", release)
            btn.set_enabled = set_enabled
            draw()
            return btn

        def _title_row(parent, text):
            row = tk.Frame(parent, bg=PANEL)
            row.pack(fill="x")

            label = tk.Label(
                row,
                text=text,
                bg=PANEL,
                fg=theme.INK,
                font=("Georgia", 15, "bold"),
            )
            label.pack(side="left")

            line = tk.Canvas(
                row,
                height=22,
                bg=PANEL,
                highlightthickness=0,
                bd=0,
            )
            line.pack(side="left", fill="x", expand=True, padx=(16, 0))

            def draw_line(_event=None):
                line.delete("all")
                w = max(line.winfo_width(), 40)
                y = 11
                line.create_line(
                    0, y, max(0, w - 8), y,
                    fill="#202020",
                    width=1,
                )
                line.create_oval(
                    max(0, w - 9),
                    y - 3,
                    max(0, w - 3),
                    y + 3,
                    fill=PANEL,
                    outline="#202020",
                    width=1,
                )

            line.bind("<Configure>", draw_line)
            line.after_idle(draw_line)
            return row

        def _section_title(parent, text):
            tk.Label(
                parent,
                text=text,
                bg=PANEL,
                fg=theme.INK,
                font=("Georgia", 10, "bold"),
            ).pack(anchor="w")

        def _field_label(parent, text):
            tk.Label(
                parent,
                text=text,
                bg=PANEL,
                fg="#4F5963",
                font=("Segoe UI", 8, "bold"),
            ).pack(anchor="w")

        def _make_page_preview(parent, *, label_text="Aucune image associée"):
            holder = tk.Frame(parent, bg=PANEL)

            card = tk.Canvas(
                holder,
                width=118,
                height=160,
                bg=PANEL,
                highlightthickness=0,
                bd=0,
            )
            card.pack(anchor="center")

            card._photo = None
            card._label = label_text

            def draw():
                card.delete("all")

                page_w = 78
                page_h = 110
                x1 = 20
                y1 = 10
                x2 = x1 + page_w
                y2 = y1 + page_h

                card.create_rectangle(
                    x1 + 3, y1 + 4, x2 + 3, y2 + 4,
                    fill="#D2CEC6",
                    outline="",
                )
                card.create_rectangle(
                    x1, y1, x2, y2,
                    fill="#FFFEFC",
                    outline="#C9C5BE",
                    width=1,
                )

                if card._photo is not None:
                    card.create_image(
                        (x1 + x2) / 2,
                        (y1 + y2) / 2,
                        image=card._photo,
                        anchor="center",
                    )
                else:
                    # Miniature neutre identique à l'esprit Composition.
                    card.create_rectangle(
                        x1 + 13, y1 + 18,
                        x2 - 13, y1 + 42,
                        fill="#E9ECE7",
                        outline="",
                    )
                    for offset in (57, 65, 73, 81):
                        card.create_line(
                            x1 + 15, y1 + offset,
                            x2 - 15, y1 + offset,
                            fill="#D6D0C6",
                            width=1,
                        )

                tag_w = max(78, min(112, int(len(card._label) * 5.2) + 18))
                tag_x1 = (118 - tag_w) / 2
                tag_x2 = tag_x1 + tag_w
                tag_y1 = 130
                tag_y2 = 149

                _round_rect(
                    card,
                    tag_x1, tag_y1, tag_x2, tag_y2,
                    4,
                    fill="#F1EEE8",
                    outline="#D8D2C9",
                    width=1,
                )
                card.create_text(
                    59,
                    (tag_y1 + tag_y2) / 2,
                    text=card._label,
                    fill="#65707A",
                    font=("Segoe UI", 7),
                    anchor="center",
                )

            def set_image(path_text, label_text=None):
                photo = None
                path = Path(path_text) if path_text else None

                try:
                    if path is not None and path.exists():
                        image = Image.open(path).convert("RGBA")
                        image.thumbnail(
                            (68, 100),
                            Image.Resampling.LANCZOS,
                        )
                        photo = ImageTk.PhotoImage(image)
                except Exception:
                    photo = None

                card._photo = photo
                if label_text is not None:
                    card._label = label_text
                draw()

            card.set_image = set_image
            draw()
            return holder, card

        def _make_scrollbar(parent, listbox):
            bar = tk.Canvas(
                parent,
                width=10,
                bg=SOFT,
                highlightthickness=0,
                bd=0,
                cursor="hand2",
            )

            state = {
                "first": 0.0,
                "last": 1.0,
                "dragging": False,
                "offset": 0.0,
                "hover": False,
            }

            def geometry():
                h = max(1, bar.winfo_height())
                top, bottom = 4, h - 4
                track_h = max(1, bottom - top)
                first = max(0.0, min(1.0, state["first"]))
                last = max(first, min(1.0, state["last"]))
                thumb_h = max(28, track_h * (last - first))
                thumb_h = min(track_h, thumb_h)
                travel = max(0.0, track_h - thumb_h)
                y1 = top + travel * first
                y2 = y1 + thumb_h
                return top, bottom, y1, y2, travel, thumb_h

            def draw():
                bar.delete("all")
                top, bottom, y1, y2, _travel, _thumb_h = geometry()

                _round_rect(
                    bar,
                    4, top, 7, bottom,
                    2,
                    fill="#E4E0D9",
                    outline="",
                )
                _round_rect(
                    bar,
                    2, y1, 9, y2,
                    4,
                    fill="#8799AA" if state["hover"] else "#AAB5BF",
                    outline="",
                )

            def set_view(first, last):
                state["first"] = float(first)
                state["last"] = float(last)
                draw()

            def press(event):
                top, bottom, y1, y2, travel, thumb_h = geometry()
                state["hover"] = True

                if y1 <= event.y <= y2:
                    state["dragging"] = True
                    state["offset"] = event.y - y1
                    draw()
                    return

                target = event.y - thumb_h / 2
                target = max(top, min(bottom - thumb_h, target))
                frac = 0.0 if travel <= 0 else (target - top) / travel
                listbox.yview_moveto(frac)

            def drag(event):
                if not state["dragging"]:
                    return

                top, bottom, _y1, _y2, travel, thumb_h = geometry()
                target = event.y - state["offset"]
                target = max(top, min(bottom - thumb_h, target))
                frac = 0.0 if travel <= 0 else (target - top) / travel
                listbox.yview_moveto(frac)

            def release(_event=None):
                state["dragging"] = False

            def enter(_event=None):
                state["hover"] = True
                draw()

            def leave(_event=None):
                if not state["dragging"]:
                    state["hover"] = False
                    draw()

            bar.bind("<Configure>", lambda _e: draw())
            bar.bind("<Enter>", enter)
            bar.bind("<Leave>", leave)
            bar.bind("<ButtonPress-1>", press)
            bar.bind("<B1-Motion>", drag)
            bar.bind("<ButtonRelease-1>", release)

            listbox.configure(yscrollcommand=set_view)
            return bar

        # ------------------------------------------------------------------
        # Titre / sous-titre.
        # ------------------------------------------------------------------
        _title_row(panel, "Créer / choisir un type de page")

        tk.Label(
            panel,
            text=f"Partie concernée : {group_name}",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 8),
        ).pack(anchor="w", pady=(5, 16))

        # ------------------------------------------------------------------
        # Corps : deux fonctions côte à côte, comme une vraie zone Maquettage.
        # ------------------------------------------------------------------
        content = tk.Frame(
            panel,
            bg=PANEL,
            height=410,
        )
        content.pack(fill="x")
        content.pack_propagate(False)

        left = tk.Frame(
            content,
            bg=PANEL,
            width=350,
        )
        left.pack(side="left", fill="both", expand=True, padx=(0, 20))

        separator = tk.Frame(
            content,
            bg="#D6D1CA",
            width=1,
        )
        separator.pack(side="left", fill="y", padx=(0, 20))

        right = tk.Frame(
            content,
            bg=PANEL,
            width=420,
        )
        right.pack(side="left", fill="both", expand=True)

        # ------------------------------------------------------------------
        # Types existants : liste de noms + aperçu à droite, comme Ouvrir projet.
        # ------------------------------------------------------------------
        _section_title(left, "Types existants")

        tk.Label(
            left,
            text=(
                "Sélectionnez un nom. L’image associée s’affiche "
                "pour le type choisi."
            ),
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 8),
            justify="left",
            wraplength=330,
        ).pack(anchor="w", pady=(4, 10))

        existing_row = tk.Frame(left, bg=PANEL)
        existing_row.pack(fill="x")

        list_box_frame = tk.Frame(
            existing_row,
            bg=SOFT,
            highlightthickness=1,
            highlightbackground=BORDER,
            padx=6,
            pady=6,
            width=190,
            height=232,
        )
        list_box_frame.pack(side="left", fill="y")
        list_box_frame.pack_propagate(False)

        list_inner = tk.Frame(list_box_frame, bg=SOFT)
        list_inner.pack(fill="both", expand=True)

        type_list = tk.Listbox(
            list_inner,
            bg=SOFT,
            fg=INK,
            selectbackground="#E8EEF5",
            selectforeground=NAVY,
            activestyle="none",
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 8),
            exportselection=False,
        )
        type_list.pack(side="left", fill="both", expand=True)

        scroll = _make_scrollbar(list_inner, type_list)
        scroll.pack(side="right", fill="y", padx=(4, 0))

        preview_column = tk.Frame(
            existing_row,
            bg=PANEL,
            padx=12,
        )
        preview_column.pack(side="left", fill="both", expand=True)

        existing_preview_holder, existing_preview = _make_page_preview(
            preview_column,
            label_text="Aucune image",
        )
        existing_preview_holder.pack(anchor="center", pady=(1, 4))

        selected_name = tk.Label(
            preview_column,
            text="Aucun type sélectionné",
            bg=PANEL,
            fg=theme.INK,
            font=("Segoe UI", 8, "bold"),
            justify="center",
            wraplength=135,
        )
        selected_name.pack(anchor="center", pady=(2, 3))

        selected_info = tk.Label(
            preview_column,
            text="Cliquez sur un nom.",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 7),
            justify="center",
            wraplength=135,
        )
        selected_info.pack(anchor="center")

        thumb_root = PROJECT_ROOT / "assets" / "page_thumbnails"
        standard_types = [
            ("Couverture", thumb_root / "type_page_couverture.png"),
            ("2e de couverture", thumb_root / "type_page_deuxieme_couverture.png"),
            ("Page de titre", thumb_root / "type_page_titre.png"),
            ("Avant-propos", thumb_root / "type_page_avant_propos.png"),
            ("Sommaire", thumb_root / "type_page_sommaire.png"),
            ("Chapitre", thumb_root / "type_page_chapitre.png"),
            ("Texte", thumb_root / "type_page_texte.png"),
            ("Fiche", thumb_root / "type_page_fiche.png"),
            ("Illustration", thumb_root / "type_page_illustration.png"),
            ("Transition", thumb_root / "type_page_transition.png"),
            ("Conclusion", thumb_root / "type_page_conclusion.png"),
            ("Page blanche", thumb_root / "type_page_blanche.png"),
            ("3e de couverture", thumb_root / "type_page_troisieme_couverture.png"),
            ("4e de couverture", thumb_root / "type_page_quatrieme_couverture.png"),
            ("Personnalisée", thumb_root / "type_page_personnalisee.png"),
        ]

        custom_types = getattr(
            self,
            "_maquettage_custom_page_types",
            [],
        )

        available_types = [
            {
                "name": name,
                "image": str(path) if path.exists() else "",
                "builtin": True,
            }
            for name, path in standard_types
        ]

        for item in custom_types:
            if not isinstance(item, dict):
                continue
            name = str(item.get("name", "")).strip()
            if not name:
                continue
            available_types.append(
                {
                    "name": name,
                    "image": str(item.get("image", "") or ""),
                    "builtin": False,
                    "head": bool(item.get("head", False)),
                    "description": str(item.get("description", "") or ""),
                }
            )

        for item in available_types:
            type_list.insert("end", item["name"])

        selected_existing = {"item": None}

        def _use_existing():
            item = selected_existing.get("item")
            if not item:
                return

            self._maquettage_selected_page_type = dict(item)
            win.destroy()

        use_button = _make_tl_button(
            left,
            text="Utiliser ce type   ›",
            command=_use_existing,
            primary=True,
            min_width=150,
            enabled=False,
        )
        use_button.pack(anchor="e", pady=(12, 0))

        def _select_existing(_event=None):
            selection = type_list.curselection()
            if not selection:
                return

            index = int(selection[0])
            if index < 0 or index >= len(available_types):
                return

            item = available_types[index]
            selected_existing["item"] = item

            selected_name.configure(text=item["name"])

            image_path = str(item.get("image", "") or "")
            if image_path and Path(image_path).exists():
                existing_preview.set_image(
                    image_path,
                    item["name"],
                )
                selected_info.configure(text="Image associée au type.")
            else:
                existing_preview.set_image(
                    "",
                    item["name"],
                )
                selected_info.configure(text="Aucune image associée.")

            use_button.set_enabled(True)

        type_list.bind("<<ListboxSelect>>", _select_existing)
        type_list.bind(
            "<Double-Button-1>",
            lambda _event: _use_existing(),
        )

        # ------------------------------------------------------------------
        # Nouveau type.
        # ------------------------------------------------------------------
        _section_title(right, "Créer un nouveau type")

        tk.Label(
            right,
            text="Définissez son identité et son image associée.",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 8),
        ).pack(anchor="w", pady=(4, 10))

        _field_label(right, "Nom du type")

        name_var = tk.StringVar()

        name_frame = tk.Frame(
            right,
            bg=FIELD,
            highlightthickness=1,
            highlightbackground=BORDER_STRONG,
            padx=8,
            pady=5,
        )
        name_frame.pack(fill="x", pady=(4, 9))

        name_entry = tk.Entry(
            name_frame,
            textvariable=name_var,
            bg=FIELD,
            fg=INK,
            insertbackground=NAVY,
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 9),
        )
        name_entry.pack(fill="x")

        # Case personnalisée TomeLinea, pas de checkbox Windows brute.
        head_var = tk.BooleanVar(value=False)

        check_row = tk.Frame(right, bg=PANEL)
        check_row.pack(fill="x", pady=(0, 10))

        check_canvas = tk.Canvas(
            check_row,
            width=18,
            height=18,
            bg=PANEL,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        check_canvas.pack(side="left")

        check_label = tk.Label(
            check_row,
            text="Traiter comme tête de partie",
            bg=PANEL,
            fg=INK,
            font=("Segoe UI", 8),
            cursor="hand2",
        )
        check_label.pack(side="left", padx=(5, 0))

        def _draw_check():
            check_canvas.delete("all")
            check_canvas.create_rectangle(
                2, 2, 15, 15,
                fill="#FFFDFC",
                outline="#AEB9C3",
                width=1,
            )
            if head_var.get():
                check_canvas.create_rectangle(
                    5, 5, 12, 12,
                    fill="#173E70",
                    outline="",
                )

        def _toggle_check(_event=None):
            head_var.set(not head_var.get())
            _draw_check()

        check_canvas.bind("<Button-1>", _toggle_check)
        check_label.bind("<Button-1>", _toggle_check)
        _draw_check()

        _field_label(right, "Image associée")

        image_row = tk.Frame(right, bg=PANEL)
        image_row.pack(fill="x", pady=(5, 9))

        new_preview_holder, new_preview = _make_page_preview(
            image_row,
            label_text="Nouvelle image",
        )
        new_preview_holder.pack(side="left", anchor="n")

        image_tools = tk.Frame(
            image_row,
            bg=PANEL,
            padx=10,
        )
        image_tools.pack(side="left", fill="both", expand=True)

        image_path_var = tk.StringVar(value="")

        image_name_label = tk.Label(
            image_tools,
            text="Aucune image choisie",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 7),
            justify="left",
            wraplength=250,
        )
        image_name_label.pack(anchor="w", pady=(8, 8))

        def _choose_image():
            path = _filedialog.askopenfilename(
                parent=win,
                title="Choisir l’image associée au type",
                filetypes=(
                    ("Images", "*.png *.jpg *.jpeg *.webp *.bmp"),
                    ("PNG", "*.png"),
                    ("JPEG", "*.jpg *.jpeg"),
                    ("Tous les fichiers", "*.*"),
                ),
            )
            if not path:
                return

            image_path_var.set(path)
            image_name_label.configure(text=Path(path).name)
            new_preview.set_image(path, "Image associée")

        choose_image = _make_tl_button(
            image_tools,
            text="Choisir une image…   ›",
            command=_choose_image,
            primary=False,
            min_width=165,
            enabled=True,
        )
        choose_image.pack(anchor="w")

        _field_label(right, "Description")

        description_frame = tk.Frame(
            right,
            bg=FIELD,
            highlightthickness=1,
            highlightbackground=BORDER_STRONG,
            padx=7,
            pady=6,
        )
        description_frame.pack(fill="x", pady=(4, 0))

        description = tk.Text(
            description_frame,
            height=3,
            wrap="word",
            bg=FIELD,
            fg=INK,
            insertbackground=NAVY,
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=("Segoe UI", 8),
        )
        description.pack(fill="x")

        def _create_type():
            name = name_var.get().strip()
            if not name:
                return

            item = {
                "name": name,
                "image": image_path_var.get().strip(),
                "head": bool(head_var.get()),
                "description": description.get("1.0", "end-1c").strip(),
                "builtin": False,
            }

            library = getattr(
                self,
                "_maquettage_custom_page_types",
                None,
            )
            if library is None:
                library = []
                self._maquettage_custom_page_types = library

            replaced = False
            for index, existing_item in enumerate(library):
                if (
                    isinstance(existing_item, dict)
                    and str(existing_item.get("name", "")).strip().lower()
                    == name.lower()
                ):
                    library[index] = item
                    replaced = True
                    break

            if not replaced:
                library.append(item)

            self._maquettage_selected_page_type = dict(item)
            win.destroy()

        create_button = _make_tl_button(
            right,
            text="Créer le type   ›",
            command=_create_type,
            primary=True,
            min_width=140,
            enabled=False,
        )
        create_button.place(relx=1.0, rely=1.0, anchor="se")

        def _update_create_state(*_args):
            create_button.set_enabled(bool(name_var.get().strip()))

        name_var.trace_add("write", _update_create_state)

        # ------------------------------------------------------------------
        # Pied de fenêtre : même logique que Ouvrir un projet.
        # ------------------------------------------------------------------
        footer = tk.Frame(panel, bg=PANEL)
        footer.pack(fill="x", pady=(13, 0))

        tk.Frame(
            footer,
            bg="#DDD8D1",
            height=1,
        ).pack(fill="x", pady=(0, 9))

        close_row = tk.Frame(footer, bg=PANEL)
        close_row.pack(fill="x")

        close_button = _make_tl_button(
            close_row,
            text="Fermer",
            command=win.destroy,
            primary=False,
            min_width=100,
            enabled=True,
        )
        close_button.pack(side="right")

        self._reveal_accueil_dialog(win)
        return win



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

        # STRUCTURE_GLISSER_DEPOSER_PARTIES_V1
        # Début et Fin restent fixes. Les parties intermédiaires sont
        # manipulées directement sur la ligne.
        maquettage_structure_pressed: int | None = None
        maquettage_structure_press_xy: tuple[float, float] | None = None
        maquettage_structure_dragging = False
        maquettage_structure_drop_slot: int | None = None
        maquettage_structure_editor = None

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

        def maquettage_structure_drop_slot_at(x, y):
            """Slot d'insertion d'une partie, toujours entre Début et Fin."""
            if len(structure_model) < 3:
                return 1

            regions = sorted(
                maquettage_structure_regions,
                key=lambda item: int(item["index"]),
            )
            if len(regions) != len(structure_model):
                return None

            centers = [
                (item["x1"] + item["x2"]) / 2
                for item in regions
            ]

            # Les slots valides sont 1 .. len(model)-1 :
            # 1 = juste après Début ; dernier = juste avant Fin.
            for slot in range(1, len(centers)):
                boundary = (centers[slot - 1] + centers[slot]) / 2
                if x < boundary:
                    return slot

            return len(structure_model) - 1

        def maquettage_structure_center(index):
            """Recalcule le centre visuel d'un nœud de structure."""
            width = max(canvas.winfo_width(), 1180)
            margin = 44
            tools_width = 292
            tools_left = width - margin - tools_width
            track_left = margin + 32
            track_right = tools_left - 24

            fixed_start_x = track_left + 52
            fixed_end_x = track_right - 52

            count = len(structure_model)
            if count <= 1:
                centers = [fixed_start_x]
            elif count == 2:
                centers = [fixed_start_x, fixed_end_x]
            else:
                internal_count = count - 2
                step = (
                    fixed_end_x - fixed_start_x
                ) / (internal_count + 1)
                centers = [fixed_start_x]
                centers.extend(
                    fixed_start_x + step * (i + 1)
                    for i in range(internal_count)
                )
                centers.append(fixed_end_x)

            if 0 <= index < len(centers):
                return centers[index]
            return fixed_start_x

        def close_structure_editor(*, commit=True):
            nonlocal maquettage_structure_editor
            editor = maquettage_structure_editor
            if editor is None:
                return

            try:
                group = editor._tomelinea_group
                old_name = str(group.get("name", "Partie"))
                new_name = editor.get().strip()

                if commit and new_name:
                    group["name"] = new_name

                    # Si un ordre de pages existait déjà sous l'ancien nom,
                    # il suit automatiquement le nouveau nom.
                    if (
                        old_name != new_name
                        and old_name in self._maquettage_page_orders
                        and new_name not in self._maquettage_page_orders
                    ):
                        self._maquettage_page_orders[new_name] = (
                            self._maquettage_page_orders.pop(old_name)
                        )
            except Exception:
                pass

            try:
                editor.destroy()
            except Exception:
                pass

            maquettage_structure_editor = None
            render()

        def start_structure_editor(index):
            """Édition directe du nom, exactement sous le livre sélectionné."""
            nonlocal maquettage_structure_editor

            if not (1 <= index < len(structure_model) - 1):
                return

            if maquettage_structure_editor is not None:
                close_structure_editor(commit=True)

            render()

            group = structure_model[index]
            cx = maquettage_structure_center(index)

            # Le nom est dessiné à track_y + 27. On pose le champ dessus.
            top_y1 = 14
            track_y = top_y1 + 102

            editor = tk.Entry(
                canvas,
                bg="#FFFEFC",
                fg="#111111",
                insertbackground="#173E70",
                relief="solid",
                bd=1,
                highlightthickness=1,
                highlightbackground="#8D70C7",
                highlightcolor="#8D70C7",
                justify="center",
                font=("Georgia", 10, "bold"),
            )
            editor.insert(0, str(group.get("name", "Partie")))
            editor._tomelinea_group = group
            editor.place(
                x=cx - 65,
                y=track_y + 15,
                width=130,
                height=25,
            )
            maquettage_structure_editor = editor

            def validate(_event=None):
                close_structure_editor(commit=True)
                return "break"

            def cancel(_event=None):
                close_structure_editor(commit=False)
                return "break"

            def focus_lost(_event=None):
                canvas.after_idle(
                    lambda: (
                        close_structure_editor(commit=True)
                        if maquettage_structure_editor is editor
                        else None
                    )
                )

            editor.bind("<Return>", validate)
            editor.bind("<Escape>", cancel)
            editor.bind("<FocusOut>", focus_lost)

            editor.focus_set()
            editor.selection_range(0, "end")

        def add_part_directly():
            """+ Partie : création immédiate juste après Début."""
            nonlocal selected_index, selected_group

            if maquettage_structure_editor is not None:
                close_structure_editor(commit=True)

            used_names = {
                str(group.get("name", "")).strip().lower()
                for group in structure_model
            }
            number = 1
            while f"partie {number}".lower() in used_names:
                number += 1

            colors = (
                "#8D70C7",
                "#72AFCB",
                "#E28A6D",
                "#75B89E",
            )
            internal_count = max(0, len(structure_model) - 2)

            new_group = {
                "name": f"Partie {number}",
                "pages": 0,
                "color": colors[internal_count % len(colors)],
            }

            structure_model.insert(1, new_group)
            selected_index = 1
            selected_group = new_group
            self._maquettage_structure_model = structure_model

            render()
            canvas.after_idle(lambda: start_structure_editor(1))

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

            if (
                maquettage_structure_dragging
                and maquettage_structure_drop_slot is not None
                and 1 <= maquettage_structure_drop_slot < node_count
            ):
                slot = int(maquettage_structure_drop_slot)
                marker_x = (
                    node_centers[slot - 1] + node_centers[slot]
                ) / 2
                canvas.create_line(
                    marker_x,
                    track_y - 31,
                    marker_x,
                    track_y + 13,
                    fill="#173E70",
                    width=2,
                    tags="maquettage_ui",
                )
                canvas.create_polygon(
                    marker_x,
                    track_y - 36,
                    marker_x + 5,
                    track_y - 31,
                    marker_x,
                    track_y - 26,
                    marker_x - 5,
                    track_y - 31,
                    fill="#173E70",
                    outline="",
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
                        "x1": cx - max(icon_w / 2 + 5, 46),
                        "y1": icon_anchor_y - icon_h - 7,
                        "x2": cx + max(icon_w / 2 + 5, 46),
                        "y2": track_y + 58,
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
                command=add_part_directly,
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

            # Troisième ligne : une seule visionneuse, deux onglets internes.
            view_y1 = top_y1 + 138
            view_y2 = top_y1 + 171
            secondary_button(
                tool_x1,
                view_y1,
                tool_x2,
                view_y2,
                "Vue du livre",
                "#8D70C7",
                muted=True,
                command=self._tomelinea_open_book_views,
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
            nonlocal maquettage_structure_dragging
            nonlocal maquettage_structure_drop_slot

            # Une partie interne maintenue devient un glisser-déposer.
            if maquettage_structure_pressed is not None:
                if maquettage_structure_press_xy is not None:
                    dx = event.x - maquettage_structure_press_xy[0]
                    dy = event.y - maquettage_structure_press_xy[1]
                    if dx * dx + dy * dy >= 36:
                        maquettage_structure_dragging = True

                if maquettage_structure_dragging:
                    new_slot = maquettage_structure_drop_slot_at(
                        event.x,
                        event.y,
                    )
                    if new_slot != maquettage_structure_drop_slot:
                        maquettage_structure_drop_slot = new_slot
                        render()
                    canvas.configure(cursor="hand2")
                    return

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
            nonlocal maquettage_structure_pressed
            nonlocal maquettage_structure_press_xy
            nonlocal maquettage_structure_dragging
            nonlocal maquettage_structure_drop_slot
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

                    if 1 <= new_index < len(structure_model) - 1:
                        maquettage_structure_pressed = new_index
                        maquettage_structure_press_xy = (
                            event.x,
                            event.y,
                        )
                        maquettage_structure_dragging = False
                        maquettage_structure_drop_slot = new_index
                    else:
                        maquettage_structure_pressed = None
                        maquettage_structure_press_xy = None
                        maquettage_structure_dragging = False
                        maquettage_structure_drop_slot = None

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
            nonlocal selected_index, selected_group
            nonlocal maquettage_pressed, maquettage_hovered
            nonlocal maquettage_structure_pressed
            nonlocal maquettage_structure_press_xy
            nonlocal maquettage_structure_dragging
            nonlocal maquettage_structure_drop_slot
            nonlocal maquettage_page_pressed
            nonlocal maquettage_page_pressed_slot
            nonlocal maquettage_page_press_xy
            nonlocal maquettage_page_dragging
            nonlocal maquettage_page_drop_slot
            nonlocal maquettage_page_hovered

            if maquettage_structure_pressed is not None:
                source_index = int(maquettage_structure_pressed)
                was_dragging = bool(maquettage_structure_dragging)
                drop_slot = maquettage_structure_drop_slot

                if (
                    was_dragging
                    and drop_slot is not None
                    and 1 <= source_index < len(structure_model) - 1
                ):
                    moving = structure_model[source_index]
                    target = max(
                        1,
                        min(len(structure_model) - 1, int(drop_slot)),
                    )

                    structure_model.pop(source_index)
                    if target > source_index:
                        target -= 1

                    target = max(
                        1,
                        min(len(structure_model) - 1, target),
                    )
                    structure_model.insert(target, moving)

                    selected_group = moving
                    selected_index = structure_model.index(moving)
                    self._maquettage_structure_model = structure_model

                maquettage_structure_pressed = None
                maquettage_structure_press_xy = None
                maquettage_structure_dragging = False
                maquettage_structure_drop_slot = None
                canvas.configure(cursor="arrow")
                render()
                return

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
