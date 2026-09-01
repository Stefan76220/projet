from __future__ import annotations

"""
TomeLinea V4 — habillage éditorial.

IMPORTANT :
ce module ne contient aucune logique métier.

Il habille TomeLineaV4 sans :
- créer de Livre ;
- choisir un type de livre ;
- modifier Source / Analyse / Structure ;
- importer gui_v3 ;
- toucher au Visionneur.

La logique reste dans src.gui_v4.app.TomeLineaV4.
"""

from pathlib import Path
import tkinter as tk

from PIL import (
    Image,
    ImageColor,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageTk,
)

from src.gui_v4 import theme
from src.gui_v4.app import (
    TomeLineaV4 as TomeLineaV4Logic,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

BACKGROUND_HOME = (
    PROJECT_ROOT
    / "assets"
    / "interface"
    / "backgrounds"
    / "editorial_bg_accueil.png"
)

BACKGROUND_SOFT = (
    PROJECT_ROOT
    / "assets"
    / "interface"
    / "backgrounds"
    / "editorial_bg_soft.png"
)

VISIBILITY_ROOT = (
    PROJECT_ROOT
    / "assets"
    / "branding"
    / "tomelinea"
    / "logo_pack_visibilite"
)

BRAND_ICON = (
    VISIBILITY_ROOT
    / "TomeLinea_512x512.png"
)

BRAND_TITLE = (
    VISIBILITY_ROOT
    / "TomeLinea_titre_relief.png"
)


# ==============================================================
# PANNEAU TOMELINEA
# ==============================================================

class CutPanel(tk.Canvas):

    def __init__(
        self,
        parent,
        *,
        fill: str = theme.PANEL,
        border: str = theme.BORDER_SOFT,
        cut: int = 15,
        padding: tuple[int, int] = (
            20,
            18,
        ),
        **kwargs,
    ):

        try:
            parent_bg = parent.cget(
                "bg"
            )
        except Exception:
            parent_bg = theme.WINDOW_DEEP

        super().__init__(
            parent,
            bg=parent_bg,
            bd=0,
            highlightthickness=0,
            **kwargs,
        )

        self._fill = fill
        self._border = border
        self._cut = cut

        self._pad_x = padding[0]
        self._pad_y = padding[1]

        self.body = tk.Frame(
            self,
            bg=fill,
        )

        self._body_id = (
            self.create_window(
                self._pad_x,
                self._pad_y,
                anchor="nw",
                window=self.body,
            )
        )

        self.bind(
            "<Configure>",
            self._redraw,
            add="+",
        )


    def _redraw(
        self,
        _event=None,
    ) -> None:

        width = max(
            30,
            self.winfo_width(),
        )

        height = max(
            30,
            self.winfo_height(),
        )

        cut = min(
            self._cut,
            max(
                5,
                width // 10,
            ),
            max(
                5,
                height // 10,
            ),
        )

        points = [
            1, 1,
            width - cut, 1,
            width - 1, cut,
            width - 1, height - cut,
            width - cut, height - 1,
            cut, height - 1,
            1, height - cut,
            1, cut,
        ]

        self.delete(
            "panel_shape"
        )

        self.create_polygon(
            points,
            fill=self._fill,
            outline=self._border,
            width=1,
            tags=(
                "panel_shape",
            ),
        )

        self.tag_lower(
            "panel_shape"
        )

        inner_width = max(
            1,
            width
            - self._pad_x * 2,
        )

        inner_height = max(
            1,
            height
            - self._pad_y * 2,
        )

        self.coords(
            self._body_id,
            self._pad_x,
            self._pad_y,
        )

        self.itemconfigure(
            self._body_id,
            width=inner_width,
            height=inner_height,
        )


# ==============================================================
# BOUTON TOMELINEA
# ==============================================================

class TLButton(tk.Button):

    def __init__(
        self,
        parent,
        text: str,
        command=None,
        *,
        primary: bool = False,
        compact: bool = False,
        state: str = "normal",
        width: int | None = None,
    ):

        if primary:
            base_bg = theme.ACCENT_DARK
            hover_bg = theme.ACCENT
            fg = theme.WHITE
            active_fg = theme.WINDOW_DEEP

        else:
            base_bg = theme.PANEL_SOFT
            hover_bg = theme.ACCENT_SOFT
            fg = theme.INK
            active_fg = theme.WHITE

        kwargs = {}

        if width is not None:
            kwargs[
                "width"
            ] = width

        super().__init__(
            parent,
            text=text,
            command=command,
            state=state,
            bg=base_bg,
            fg=fg,
            activebackground=hover_bg,
            activeforeground=active_fg,
            disabledforeground=theme.MUTED_DARK,
            relief="flat",
            bd=0,
            padx=(
                11
                if compact
                else 16
            ),
            pady=(
                6
                if compact
                else 9
            ),
            font=(
                theme.FONT_UI,
                9,
                "bold",
            ),
            cursor=(
                "hand2"
                if state != "disabled"
                else "arrow"
            ),
            **kwargs,
        )

        self._base_bg = base_bg
        self._hover_bg = hover_bg

        self.bind(
            "<Enter>",
            self._enter,
            add="+",
        )

        self.bind(
            "<Leave>",
            self._leave,
            add="+",
        )


    def _enter(
        self,
        _event=None,
    ) -> None:

        if str(
            self.cget(
                "state"
            )
        ) != "disabled":
            self.configure(
                bg=self._hover_bg
            )


    def _leave(
        self,
        _event=None,
    ) -> None:

        self.configure(
            bg=self._base_bg
        )


# ==============================================================
# COUCHE GRAPHIQUE V4
# ==============================================================

class TomeLineaV4Editorial(
    TomeLineaV4Logic
):

    def __init__(
        self,
    ) -> None:

        # Caches graphiques indépendants.
        self._editorial_bg_sources = {}
        self._editorial_bg_cache = {}

        self._brand_icon_cache = {}
        self._brand_title_cache = {}

        self._line_icon_cache = {}

        super().__init__()

        # TomeLinea retrouve sa propre fenêtre,
        # sans la grosse barre Windows blanche.
        try:
            self.withdraw()
            self.overrideredirect(
                True
            )
        except tk.TclError:
            pass

        self._fit_to_work_area()

        # On reconstruit une dernière fois l'Accueil
        # après application du vrai cadre TomeLinea.
        self.show_home()

        self.deiconify()
        self.update_idletasks()
        self.lift()


    # ==========================================================
    # FENETRE
    # ==========================================================

    def _fit_to_work_area(
        self,
    ) -> None:

        try:
            import ctypes

            class RECT(
                ctypes.Structure
            ):
                _fields_ = [
                    (
                        "left",
                        ctypes.c_long,
                    ),
                    (
                        "top",
                        ctypes.c_long,
                    ),
                    (
                        "right",
                        ctypes.c_long,
                    ),
                    (
                        "bottom",
                        ctypes.c_long,
                    ),
                ]

            rect = RECT()

            SPI_GETWORKAREA = (
                0x0030
            )

            ok = (
                ctypes.windll.user32.SystemParametersInfoW(
                    SPI_GETWORKAREA,
                    0,
                    ctypes.byref(
                        rect
                    ),
                    0,
                )
            )

            if ok:
                width = max(
                    1100,
                    rect.right
                    - rect.left,
                )

                height = max(
                    700,
                    rect.bottom
                    - rect.top,
                )

                self.geometry(
                    (
                        f"{width}x{height}"
                        f"+{rect.left}"
                        f"+{rect.top}"
                    )
                )

                return

        except Exception:
            pass

        width = max(
            1100,
            self.winfo_screenwidth(),
        )

        height = max(
            700,
            self.winfo_screenheight()
            - 48,
        )

        self.geometry(
            f"{width}x{height}+0+0"
        )


    # ==========================================================
    # IMAGES
    # ==========================================================

    def _background_source(
        self,
        path: Path,
    ):

        key = str(
            path
        )

        cached = (
            self._editorial_bg_sources.get(
                key
            )
        )

        if cached is not None:
            return cached

        if not path.exists():
            return None

        image = Image.open(
            path
        ).convert(
            "RGB"
        )

        # Traitement doux validé dans l'esprit TomeLinea :
        # on évite le fond criard ou trop contrasté.
        image = (
            ImageEnhance.Color(
                image
            ).enhance(
                0.82
            )
        )

        image = (
            ImageEnhance.Brightness(
                image
            ).enhance(
                0.90
            )
        )

        self._editorial_bg_sources[
            key
        ] = image

        return image


    def _background_photo(
        self,
        path: Path,
        width: int,
        height: int,
        key: str,
    ):

        width = max(
            400,
            int(width),
        )

        height = max(
            300,
            int(height),
        )

        cache_key = (
            str(path),
            width,
            height,
            key,
        )

        cached = (
            self._editorial_bg_cache.get(
                cache_key
            )
        )

        if cached is not None:
            return cached

        source = (
            self._background_source(
                path
            )
        )

        if source is None:
            return None

        source_width, source_height = (
            source.size
        )

        scale = max(
            width / source_width,
            height / source_height,
        )

        resized_width = max(
            width,
            int(
                source_width
                * scale
            ),
        )

        resized_height = max(
            height,
            int(
                source_height
                * scale
            ),
        )

        image = source.resize(
            (
                resized_width,
                resized_height,
            ),
            Image.Resampling.LANCZOS,
        )

        left = max(
            0,
            (
                resized_width
                - width
            ) // 2,
        )

        top = max(
            0,
            (
                resized_height
                - height
            ) // 2,
        )

        image = image.crop(
            (
                left,
                top,
                left + width,
                top + height,
            )
        )

        photo = ImageTk.PhotoImage(
            image
        )

        if len(
            self._editorial_bg_cache
        ) > 10:
            self._editorial_bg_cache.clear()

        self._editorial_bg_cache[
            cache_key
        ] = photo

        return photo


    def _brand_icon_photo(
        self,
        size: int,
    ):

        size = int(
            size
        )

        cached = (
            self._brand_icon_cache.get(
                size
            )
        )

        if cached is not None:
            return cached

        if not BRAND_ICON.exists():
            return None

        image = Image.open(
            BRAND_ICON
        ).convert(
            "RGBA"
        )

        image.thumbnail(
            (
                size,
                size,
            ),
            Image.Resampling.LANCZOS,
        )

        photo = ImageTk.PhotoImage(
            image
        )

        self._brand_icon_cache[
            size
        ] = photo

        return photo


    def _brand_title_photo(
        self,
        width: int,
    ):

        width = int(
            width
        )

        cached = (
            self._brand_title_cache.get(
                width
            )
        )

        if cached is not None:
            return cached

        if not BRAND_TITLE.exists():
            return None

        image = Image.open(
            BRAND_TITLE
        ).convert(
            "RGBA"
        )

        ratio = (
            width
            / max(
                1,
                image.width,
            )
        )

        image = image.resize(
            (
                width,
                max(
                    1,
                    int(
                        image.height
                        * ratio
                    ),
                ),
            ),
            Image.Resampling.LANCZOS,
        )

        photo = ImageTk.PhotoImage(
            image
        )

        self._brand_title_cache[
            width
        ] = photo

        return photo


    # ==========================================================
    # ICONES LIGNE TOMELINEA
    # ==========================================================

    def _line_icon(
        self,
        kind: str,
        size: int = 34,
        color: str | None = None,
    ):
        """
        Pictogrammes TomeLinea V4.

        Trait fin, sans halo.
        Les trois couleurs rappellent les stations du logo :
        c?ladon, bleu doux et orang?.
        """

        cache_key = (
            "tl_v4_refined",
            kind,
            int(size),
        )

        cached = self._line_icon_cache.get(
            cache_key
        )

        if cached is not None:
            return cached

        scale = 4
        side = max(
            22,
            int(size),
        ) * scale

        image = Image.new(
            "RGBA",
            (side, side),
            (0, 0, 0, 0),
        )

        draw = ImageDraw.Draw(
            image
        )

        celadon = (
            127,
            184,
            174,
            255,
        )

        blue = (
            125,
            151,
            181,
            255,
        )

        orange = (
            210,
            132,
            94,
            255,
        )

        pale = (
            205,
            211,
            213,
            235,
        )

        quiet = (
            125,
            137,
            147,
            175,
        )

        stroke = max(
            4,
            int(side * 0.018),
        )

        thin = max(
            3,
            int(side * 0.012),
        )

        def p(x, y):
            return (
                int(x * side),
                int(y * side),
            )

        # ------------------------------------------------------
        # Ligne ?ditoriale commune aux trois pictogrammes.
        # ------------------------------------------------------

        draw.line(
            [
                p(0.15, 0.82),
                p(0.85, 0.82),
            ],
            fill=quiet,
            width=thin,
        )

        stations = (
            (0.30, celadon),
            (0.50, blue),
            (0.70, orange),
        )

        radius = max(
            4,
            int(side * 0.025),
        )

        for x, station_color in stations:
            cx, cy = p(
                x,
                0.82,
            )

            draw.ellipse(
                (
                    cx - radius,
                    cy - radius,
                    cx + radius,
                    cy + radius,
                ),
                fill=station_color,
            )

        # ------------------------------------------------------
        # CR?ER
        # Feuille ?ditoriale + ajout.
        # ------------------------------------------------------

        if kind == "create":

            draw.rounded_rectangle(
                [
                    p(0.25, 0.16),
                    p(0.63, 0.67),
                ],
                radius=max(
                    5,
                    int(side * 0.025),
                ),
                outline=pale,
                width=stroke,
            )

            # Deux lignes de composition.
            draw.line(
                [
                    p(0.33, 0.31),
                    p(0.54, 0.31),
                ],
                fill=blue,
                width=thin,
            )

            draw.line(
                [
                    p(0.33, 0.40),
                    p(0.50, 0.40),
                ],
                fill=celadon,
                width=thin,
            )

            # Petit + TomeLinea, d?tach? de la page.
            draw.line(
                [
                    p(0.70, 0.30),
                    p(0.70, 0.52),
                ],
                fill=orange,
                width=stroke,
            )

            draw.line(
                [
                    p(0.59, 0.41),
                    p(0.81, 0.41),
                ],
                fill=orange,
                width=stroke,
            )

        # ------------------------------------------------------
        # OUVRIR
        # Deux feuillets qui s'?cartent.
        # ------------------------------------------------------

        elif kind == "open":

            draw.line(
                [
                    p(0.20, 0.25),
                    p(0.44, 0.18),
                    p(0.49, 0.63),
                    p(0.25, 0.67),
                    p(0.20, 0.25),
                ],
                fill=pale,
                width=stroke,
                joint="curve",
            )

            draw.line(
                [
                    p(0.49, 0.63),
                    p(0.54, 0.18),
                    p(0.78, 0.25),
                    p(0.73, 0.67),
                    p(0.49, 0.63),
                ],
                fill=pale,
                width=stroke,
                joint="curve",
            )

            draw.line(
                [
                    p(0.30, 0.34),
                    p(0.41, 0.31),
                ],
                fill=celadon,
                width=thin,
            )

            draw.line(
                [
                    p(0.58, 0.31),
                    p(0.69, 0.34),
                ],
                fill=orange,
                width=thin,
            )

            draw.line(
                [
                    p(0.49, 0.21),
                    p(0.49, 0.61),
                ],
                fill=blue,
                width=thin,
            )

        # ------------------------------------------------------
        # PROJET ACTIF
        # Petit livre assembl? / progression.
        # ------------------------------------------------------

        elif kind == "active":

            draw.rounded_rectangle(
                [
                    p(0.23, 0.17),
                    p(0.72, 0.66),
                ],
                radius=max(
                    5,
                    int(side * 0.025),
                ),
                outline=pale,
                width=stroke,
            )

            draw.line(
                [
                    p(0.33, 0.17),
                    p(0.33, 0.66),
                ],
                fill=blue,
                width=thin,
            )

            draw.line(
                [
                    p(0.42, 0.31),
                    p(0.62, 0.31),
                ],
                fill=celadon,
                width=thin,
            )

            draw.line(
                [
                    p(0.42, 0.42),
                    p(0.59, 0.42),
                ],
                fill=orange,
                width=thin,
            )

            # Marque-page tr?s discret.
            draw.line(
                [
                    p(0.62, 0.17),
                    p(0.62, 0.40),
                    p(0.67, 0.35),
                    p(0.72, 0.40),
                    p(0.72, 0.18),
                ],
                fill=orange,
                width=thin,
            )

        else:

            draw.ellipse(
                [
                    p(0.28, 0.22),
                    p(0.72, 0.66),
                ],
                outline=pale,
                width=stroke,
            )

        image = image.resize(
            (
                int(size),
                int(size),
            ),
            Image.Resampling.LANCZOS,
        )

        photo = ImageTk.PhotoImage(
            image
        )

        self._line_icon_cache[
            cache_key
        ] = photo

        return photo

    # ==========================================================
    # BOUTON GLOBAL
    # ==========================================================

    def _button(
        self,
        parent,
        text: str,
        command,
        *,
        accent: bool = False,
        enabled: bool = True,
        compact: bool = False,
        width: int | None = None,
    ):

        return TLButton(
            parent,
            text,
            command,
            primary=accent,
            compact=compact,
            state=(
                "normal"
                if enabled
                else "disabled"
            ),
            width=width,
        )


    # ==========================================================
    # ACCUEIL
    # ==========================================================

    def show_home(
        self,
    ) -> None:

        self._clear()

        screen = tk.Frame(
            self,
            bg=theme.WINDOW_DEEP,
        )

        screen.pack(
            fill="both",
            expand=True,
        )

        background = tk.Label(
            screen,
            bg=theme.WINDOW_DEEP,
            bd=0,
        )

        background.place(
            x=0,
            y=0,
            relwidth=1,
            relheight=1,
        )

        def refresh_background(
            event,
        ):

            photo = (
                self._background_photo(
                    BACKGROUND_HOME,
                    event.width,
                    event.height,
                    "home",
                )
            )

            if photo is not None:
                background.configure(
                    image=photo
                )

                background.image = (
                    photo
                )

        screen.bind(
            "<Configure>",
            refresh_background,
            add="+",
        )

        # ------------------------------------------------------
        # IDENTITE
        # ------------------------------------------------------

        header = tk.Frame(
            screen,
            bg=theme.WINDOW_DEEP,
        )

        header.place(
            relx=0.085,
            rely=0.045,
            relwidth=0.83,
            relheight=0.145,
        )

        brand = tk.Frame(
            header,
            bg=theme.WINDOW_DEEP,
        )

        brand.place(
            relx=0,
            rely=0,
            relwidth=0.68,
            relheight=1,
        )

        icon = (
            self._brand_icon_photo(
                92
            )
        )

        if icon is not None:

            label = tk.Label(
                brand,
                image=icon,
                bg=theme.WINDOW_DEEP,
                bd=0,
            )

            label.image = icon

            label.place(
                x=0,
                y=2,
            )

        title = (
            self._brand_title_photo(
                455
            )
        )

        if title is not None:

            label = tk.Label(
                brand,
                image=title,
                bg=theme.WINDOW_DEEP,
                bd=0,
            )

            label.image = title

            label.place(
                x=110,
                y=8,
            )

        else:

            tk.Label(
                brand,
                text="TomeLinea",
                bg=theme.WINDOW_DEEP,
                fg=theme.INK,
                font=(
                    theme.FONT_TITLE,
                    34,
                ),
            ).place(
                x=110,
                y=10,
            )

        tk.Label(
            brand,
            text="V4",
            bg=theme.WINDOW_DEEP,
            fg=theme.ACCENT,
            font=(
                theme.FONT_UI,
                13,
                "bold",
            ),
        ).place(
            x=575,
            y=16,
        )

        tk.Label(
            brand,
            text=(
                "LA LIGNE ÉDITORIALE "
                "JUSQU’AU LIVRE"
            ),
            bg=theme.WINDOW_DEEP,
            fg=theme.ACCENT,
            font=(
                theme.FONT_UI,
                9,
                "bold",
            ),
        ).place(
            x=114,
            y=75,
        )

        tools = tk.Frame(
            header,
            bg=theme.WINDOW_DEEP,
        )

        tools.place(
            relx=0.76,
            rely=0.17,
            relwidth=0.19,
            relheight=0.44,
        )

        tk.Label(
            tools,
            text="?  Aide",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(
                theme.FONT_UI,
                9,
            ),
            cursor="hand2",
        ).pack(
            side="left",
            padx=(0, 22),
        )

        tk.Label(
            tools,
            text="⚙  Préférences",
            bg=theme.WINDOW_DEEP,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                9,
            ),
            cursor="hand2",
        ).pack(
            side="left",
        )

        close = tk.Label(
            header,
            text="✕",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(
                theme.FONT_UI,
                15,
                "bold",
            ),
            cursor="hand2",
            padx=8,
            pady=2,
        )

        close.place(
            relx=0.995,
            y=7,
            anchor="ne",
        )

        close.bind(
            "<Button-1>",
            lambda _event: (
                self.destroy()
            ),
        )

        close.bind(
            "<Enter>",
            lambda _event: (
                close.configure(
                    fg=theme.ERROR
                )
            ),
        )

        close.bind(
            "<Leave>",
            lambda _event: (
                close.configure(
                    fg=theme.INK
                )
            ),
        )

        # ------------------------------------------------------
        # TITRE ACCUEIL
        # ------------------------------------------------------

        intro = tk.Frame(
            screen,
            bg=theme.WINDOW_DEEP,
        )

        intro.place(
            relx=0.105,
            rely=0.235,
            relwidth=0.77,
            relheight=0.105,
        )

        tk.Label(
            intro,
            text="VOTRE LIVRE",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(
                theme.FONT_UI,
                14,
                "bold",
            ),
        ).pack(
            anchor="w"
        )

        tk.Label(
            intro,
            text=(
                "Un projet TomeLinea commence "
                "par sa Source. "
                "Le livre sera compris avant "
                "d'être organisé."
            ),
            bg=theme.WINDOW_DEEP,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                9,
            ),
        ).pack(
            anchor="w",
            pady=(5, 0),
        )

        # Ligne éditoriale / stations.
        line = tk.Canvas(
            intro,
            bg=theme.WINDOW_DEEP,
            height=15,
            bd=0,
            highlightthickness=0,
        )

        line.pack(
            fill="x",
            pady=(12, 0),
        )

        line.create_line(
            0,
            7,
            520,
            7,
            fill=theme.BORDER,
            width=1,
        )

        station_colors = (
            theme.ACCENT,
            "#8DA7C4",
            "#D28A6E",
        )

        for index, color in enumerate(
            station_colors
        ):
            x = (
                80
                + index * 175
            )

            line.create_oval(
                x - 4,
                3,
                x + 4,
                11,
                fill=color,
                outline="",
            )

        # ------------------------------------------------------
        # 3 ACTIONS — NOUVELLE LOGIQUE V4
        # ------------------------------------------------------

        # Les trois entr?es sont pos?es directement
        # sur l'?cran afin que le fond ?ditorial reste
        # visible entre elles.
        cards = screen

        active = (
            self.session is not None
        )

        active_name = (
            self.session.project.title
            if active
            else "Aucun projet actif"
        )

        self._home_action_panel(
            cards,
            column=0,
            icon_kind="create",
            title="Créer un projet",
            text=(
                "Créer l'espace de travail, "
                "puis apporter la Source du livre."
            ),
            button="Créer",
            command=(
                self._create_project_dialog
            ),
            primary=True,
        )

        self._home_action_panel(
            cards,
            column=1,
            icon_kind="open",
            title="Ouvrir",
            text=(
                "Ouvrir un projet TomeLinea V4 "
                "déjà enregistré."
            ),
            button="Ouvrir un projet",
            command=self._open_project,
        )

        self._home_action_panel(
            cards,
            column=2,
            icon_kind="active",
            title="Projet actif",
            text=active_name,
            button="Accéder au projet",
            command=lambda: (
                self.show_workspace(
                    self.current_workspace
                )
            ),
            enabled=active,
        )



    def _home_action_panel(
        self,
        parent,
        *,
        column: int,
        icon_kind: str,
        title: str,
        text: str,
        button: str,
        command,
        primary: bool = False,
        enabled: bool = True,
    ) -> None:

        # M?me mati?re pour les trois entr?es :
        # l'action principale est indiqu?e par le contenu,
        # pas par un ?norme encadrement color?.
        panel = CutPanel(
            parent,
            fill="#252C35",
            border="#44505A",
            cut=10,
            padding=(
                18,
                15,
            ),
        )

        positions = {
            0: 0.120,
            1: 0.385,
            2: 0.650,
        }

        panel.place(
            relx=positions[column],
            rely=0.405,
            relwidth=0.230,
            relheight=0.285,
        )

        body = panel.body

        # Petit bandeau sup?rieur, plus proche d'une station
        # que d'une carte d'application.
        top = tk.Frame(
            body,
            bg="#252C35",
        )

        top.pack(
            fill="x",
            pady=(0, 9),
        )

        icon = self._line_icon(
            icon_kind,
            36,
        )

        icon_label = tk.Label(
            top,
            image=icon,
            bg="#252C35",
            bd=0,
        )

        icon_label.image = icon

        icon_label.pack(
            side="left"
        )

        # Trait ?ditorial discret.
        rule = tk.Canvas(
            top,
            width=72,
            height=12,
            bg="#252C35",
            bd=0,
            highlightthickness=0,
        )

        rule.pack(
            side="left",
            padx=(11, 0),
        )

        rule.create_line(
            1,
            6,
            68,
            6,
            fill=(
                theme.ACCENT
                if primary
                else theme.BORDER
            ),
            width=1,
        )

        rule.create_oval(
            30,
            3,
            36,
            9,
            fill=(
                theme.ACCENT
                if primary
                else theme.MUTED_DARK
            ),
            outline="",
        )


        tk.Label(
            body,
            text=title,
            bg="#252C35",
            fg=theme.INK,
            font=(
                theme.FONT_TITLE,
                15,
                "bold",
            ),
        ).pack(
            anchor="w",
            pady=(3, 6),
        )

        tk.Label(
            body,
            text=text,
            bg="#252C35",
            fg=theme.MUTED,
            justify="left",
            wraplength=230,
            font=(
                theme.FONT_UI,
                8,
            ),
        ).pack(
            anchor="w"
        )

        tk.Frame(
            body,
            bg="#252C35",
            height=9,
        ).pack(
            fill="x"
        )

        tk.Frame(
            body,
            bg="#252C35",
        ).pack(
            fill="both",
            expand=True,
        )

        self._button(
            body,
            button,
            command,
            accent=primary,
            enabled=enabled,
            compact=True,
        ).pack(
            anchor="w",
            pady=(5, 2),
        )

    # ==========================================================
    # CREATION — AUCUN TYPE DE LIVRE
    # ==========================================================

    def _create_project_dialog(
        self,
    ) -> None:

        dialog = tk.Toplevel(
            self
        )

        dialog.withdraw()

        try:
            dialog.overrideredirect(
                True
            )
        except tk.TclError:
            pass

        dialog.configure(
            bg=theme.WINDOW_DEEP
        )

        dialog.transient(
            self
        )

        dialog.geometry(
            "520x300"
        )

        outer = CutPanel(
            dialog,
            fill="#252C35",
            border=theme.ACCENT_DARK,
            cut=18,
            padding=(
                28,
                24,
            ),
        )

        outer.pack(
            fill="both",
            expand=True,
        )

        body = outer.body

        top = tk.Frame(
            body,
            bg="#252C35",
        )

        top.pack(
            fill="x"
        )

        tk.Label(
            top,
            text="CRÉER UN PROJET",
            bg="#252C35",
            fg=theme.INK,
            font=(
                theme.FONT_TITLE,
                20,
                "bold",
            ),
        ).pack(
            side="left"
        )

        close = tk.Label(
            top,
            text="✕",
            bg="#252C35",
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                12,
                "bold",
            ),
            cursor="hand2",
        )

        close.pack(
            side="right"
        )

        close.bind(
            "<Button-1>",
            lambda _event: (
                dialog.destroy()
            ),
        )

        tk.Label(
            body,
            text=(
                "TomeLinea commencera ensuite "
                "par la Source et son analyse."
            ),
            bg="#252C35",
            fg=theme.MUTED,
            justify="left",
            font=(
                theme.FONT_UI,
                9,
            ),
        ).pack(
            anchor="w",
            pady=(8, 24),
        )

        tk.Label(
            body,
            text="NOM DU PROJET",
            bg="#252C35",
            fg=theme.MUTED_DARK,
            font=(
                theme.FONT_UI,
                8,
                "bold",
            ),
        ).pack(
            anchor="w",
            pady=(0, 7),
        )

        title_var = tk.StringVar(
            value="Nouveau livre"
        )

        entry = tk.Entry(
            body,
            textvariable=title_var,
            bg=theme.PANEL_ALT,
            fg=theme.INK,
            insertbackground=theme.INK,
            selectbackground=theme.ACCENT_DARK,
            selectforeground=theme.WHITE,
            relief="flat",
            bd=0,
            font=(
                theme.FONT_UI,
                11,
            ),
        )

        entry.pack(
            fill="x",
            ipady=10,
        )

        footer = tk.Frame(
            body,
            bg="#252C35",
        )

        footer.pack(
            fill="x",
            pady=(24, 0),
        )

        self._button(
            footer,
            "Créer le projet",
            lambda: (
                self._create_project(
                    title_var.get(),
                    dialog,
                )
            ),
            accent=True,
        ).pack(
            side="right"
        )

        entry.bind(
            "<Return>",
            lambda _event: (
                self._create_project(
                    title_var.get(),
                    dialog,
                )
            ),
        )

        dialog.update_idletasks()

        x = (
            self.winfo_rootx()
            + (
                self.winfo_width()
                - dialog.winfo_width()
            ) // 2
        )

        y = (
            self.winfo_rooty()
            + (
                self.winfo_height()
                - dialog.winfo_height()
            ) // 2
        )

        dialog.geometry(
            (
                f"520x300"
                f"+{max(0, x)}"
                f"+{max(0, y)}"
            )
        )

        dialog.deiconify()
        dialog.lift()

        try:
            dialog.grab_set()
        except Exception:
            pass

        entry.focus_set()

        entry.selection_range(
            0,
            tk.END,
        )


    # ==========================================================
    # BARRE ESPACE PROJET
    # ==============================================================

    def _build_workspace_header(
        self,
        parent,
    ) -> None:

        has_book = (
            self.session.project.book
            is not None
        )

        bar = tk.Frame(
            parent,
            bg=theme.WINDOW_DEEP,
            height=68,
        )

        bar.pack(
            fill="x"
        )

        bar.pack_propagate(
            False
        )

        # Accueil.
        left = tk.Frame(
            bar,
            bg=theme.WINDOW_DEEP,
        )

        left.pack(
            side="left",
            fill="y",
            padx=(18, 10),
        )

        self._button(
            left,
            "Accueil",
            self.show_home,
            compact=True,
        ).pack(
            side="left",
            pady=17,
        )

        # Marque compacte.
        brand = tk.Frame(
            left,
            bg=theme.WINDOW_DEEP,
        )

        brand.pack(
            side="left",
            padx=(17, 20),
            pady=8,
        )

        icon = self._brand_icon_photo(
            42
        )

        if icon is not None:

            label = tk.Label(
                brand,
                image=icon,
                bg=theme.WINDOW_DEEP,
                bd=0,
            )

            label.image = icon

            label.pack(
                side="left"
            )

        title = (
            self._brand_title_photo(
                150
            )
        )

        if title is not None:

            label = tk.Label(
                brand,
                image=title,
                bg=theme.WINDOW_DEEP,
                bd=0,
            )

            label.image = title

            label.pack(
                side="left",
                padx=(7, 0),
            )

        # Navigation.
        nav = tk.Frame(
            bar,
            bg=theme.WINDOW_DEEP,
        )

        nav.pack(
            side="left",
            fill="y",
        )

        for key, label in theme.NAV_ITEMS:

            enabled = (
                key == "source"
                or has_book
            )

            active = (
                key
                == self.current_workspace
            )

            wrap = tk.Frame(
                nav,
                bg=theme.WINDOW_DEEP,
            )

            wrap.pack(
                side="left",
                fill="y",
                padx=3,
            )

            button = tk.Button(
                wrap,
                text=label,
                command=lambda k=key: (
                    self.show_workspace(
                        k
                    )
                ),
                state=(
                    tk.NORMAL
                    if enabled
                    else tk.DISABLED
                ),
                bg=theme.WINDOW_DEEP,
                fg=(
                    theme.ACCENT_BRIGHT
                    if active
                    else theme.MUTED
                ),
                disabledforeground=theme.MUTED_DARK,
                activebackground=theme.WINDOW_DEEP,
                activeforeground=theme.WHITE,
                relief="flat",
                bd=0,
                padx=12,
                pady=8,
                font=(
                    theme.FONT_UI,
                    9,
                    (
                        "bold"
                        if active
                        else "normal"
                    ),
                ),
                cursor=(
                    "hand2"
                    if enabled
                    else "arrow"
                ),
            )

            button.pack(
                pady=(13, 0),
            )

            tk.Frame(
                wrap,
                bg=(
                    theme.ACCENT
                    if active
                    else theme.WINDOW_DEEP
                ),
                height=2,
            ).pack(
                fill="x",
                padx=8,
            )

        # Outils à droite.
        right = tk.Frame(
            bar,
            bg=theme.WINDOW_DEEP,
        )

        right.pack(
            side="right",
            fill="y",
            padx=(10, 18),
        )

        close = tk.Label(
            right,
            text="✕",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(
                theme.FONT_UI,
                13,
                "bold",
            ),
            cursor="hand2",
            padx=8,
        )

        close.pack(
            side="right",
            pady=20,
            padx=(8, 0),
        )

        close.bind(
            "<Button-1>",
            lambda _event: (
                self.destroy()
            ),
        )

        close.bind(
            "<Enter>",
            lambda _event: (
                close.configure(
                    fg=theme.ERROR
                )
            ),
        )

        close.bind(
            "<Leave>",
            lambda _event: (
                close.configure(
                    fg=theme.INK
                )
            ),
        )

        self._button(
            right,
            "Enregistrer",
            self._save_project,
            accent=True,
            compact=True,
        ).pack(
            side="right",
            pady=17,
            padx=4,
        )

        self._button(
            right,
            "Rétablir",
            self._redo,
            compact=True,
            enabled=self.session.can_redo,
        ).pack(
            side="right",
            pady=17,
            padx=3,
        )

        self._button(
            right,
            "Annuler",
            self._undo,
            compact=True,
            enabled=self.session.can_undo,
        ).pack(
            side="right",
            pady=17,
            padx=3,
        )


    # ==========================================================
    # SOURCE — PEAU TOMELINEA
    # ==============================================================

    def _build_source(
        self,
        parent,
    ) -> None:

        project = (
            self.session.project
        )

        bg = tk.Label(
            parent,
            bg=theme.WINDOW,
            bd=0,
        )

        bg.place(
            x=0,
            y=0,
            relwidth=1,
            relheight=1,
        )

        def refresh(
            event,
        ):

            photo = (
                self._background_photo(
                    BACKGROUND_SOFT,
                    event.width,
                    event.height,
                    "source",
                )
            )

            if photo is not None:

                bg.configure(
                    image=photo
                )

                bg.image = photo

        parent.bind(
            "<Configure>",
            refresh,
            add="+",
        )

        # ------------------------------------------------------
        # COLONNE PROJET
        # ------------------------------------------------------

        summary = CutPanel(
            parent,
            fill="#252C35",
            border="#49545E",
            cut=16,
        )

        summary.place(
            relx=0.045,
            rely=0.075,
            relwidth=0.20,
            relheight=0.80,
        )

        body = summary.body

        icon = self._line_icon(
            "source",
            38,
            theme.ACCENT_BRIGHT,
        )

        label = tk.Label(
            body,
            image=icon,
            bg="#252C35",
            bd=0,
        )

        label.image = icon

        label.pack(
            anchor="w",
            pady=(4, 14),
        )

        tk.Label(
            body,
            text="PROJET",
            bg="#252C35",
            fg=theme.ACCENT,
            font=(
                theme.FONT_UI,
                8,
                "bold",
            ),
        ).pack(
            anchor="w"
        )

        tk.Label(
            body,
            text=project.title,
            bg="#252C35",
            fg=theme.INK,
            wraplength=225,
            justify="left",
            font=(
                theme.FONT_TITLE,
                18,
                "bold",
            ),
        ).pack(
            anchor="w",
            pady=(5, 24),
        )

        source_count = len(
            project.source.elements
        )

        self._summary_value(
            body,
            "SOURCE",
            (
                "À importer"
                if source_count == 0
                else f"{source_count} élément(s)"
            ),
        )

        self._summary_value(
            body,
            "ANALYSE",
            (
                "En attente"
                if project.book is None
                else "Disponible"
            ),
        )

        self._summary_value(
            body,
            "LIVRE",
            (
                "À construire"
                if project.book is None
                else "Construit"
            ),
        )

        tk.Frame(
            body,
            bg="#252C35",
        ).pack(
            fill="both",
            expand=True,
        )

        tk.Label(
            body,
            text=(
                "TomeLinea ne présume rien "
                "du livre avant l'analyse."
            ),
            bg="#252C35",
            fg=theme.MUTED_DARK,
            justify="left",
            wraplength=220,
            font=(
                theme.FONT_UI,
                8,
            ),
        ).pack(
            anchor="w",
            pady=(10, 4),
        )

        # ------------------------------------------------------
        # CONTENU PRINCIPAL
        # ------------------------------------------------------

        main = tk.Frame(
            parent,
            bg=theme.WINDOW_DEEP,
        )

        main.place(
            relx=0.285,
            rely=0.075,
            relwidth=0.67,
            relheight=0.80,
        )

        tk.Label(
            main,
            text="SOURCE DU LIVRE",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(
                theme.FONT_UI,
                14,
                "bold",
            ),
        ).pack(
            anchor="w"
        )

        tk.Label(
            main,
            text=(
                "TomeLinea commence par comprendre "
                "le document original avant de proposer "
                "la moindre organisation."
            ),
            bg=theme.WINDOW_DEEP,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                9,
            ),
        ).pack(
            anchor="w",
            pady=(6, 20),
        )

        # Ligne logique.
        timeline = tk.Canvas(
            main,
            bg=theme.WINDOW_DEEP,
            height=28,
            bd=0,
            highlightthickness=0,
        )

        timeline.pack(
            fill="x"
        )

        timeline.create_line(
            55,
            14,
            760,
            14,
            fill=theme.BORDER,
            width=1,
        )

        stage_colors = (
            theme.ACCENT,
            "#8DA7C4",
            "#D28A6E",
        )

        stage_positions = (
            80,
            410,
            735,
        )

        for x, color in zip(
            stage_positions,
            stage_colors,
        ):

            timeline.create_oval(
                x - 6,
                8,
                x + 6,
                20,
                fill=color,
                outline=theme.WINDOW_DEEP,
                width=2,
            )

        stages = tk.Frame(
            main,
            bg=theme.WINDOW_DEEP,
        )

        stages.pack(
            fill="x",
            pady=(4, 22),
        )

        for index, (
            number,
            title,
            text,
        ) in enumerate(
            (
                (
                    "01",
                    "Source",
                    (
                        "Importer le document "
                        "original."
                    ),
                ),
                (
                    "02",
                    "Analyse",
                    (
                        "Examiner le livre aussi "
                        "complètement que nécessaire."
                    ),
                ),
                (
                    "03",
                    "Structure",
                    (
                        "Proposer une organisation "
                        "révisable."
                    ),
                ),
            )
        ):

            stage = tk.Frame(
                stages,
                bg=theme.WINDOW_DEEP,
            )

            stage.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=(
                    0 if index == 0 else 10,
                    0 if index == 2 else 10,
                ),
            )

            stages.grid_columnconfigure(
                index,
                weight=1,
                uniform="stage",
            )

            tk.Label(
                stage,
                text=number,
                bg=theme.WINDOW_DEEP,
                fg=stage_colors[
                    index
                ],
                font=(
                    theme.FONT_UI,
                    8,
                    "bold",
                ),
            ).pack(
                anchor="w"
            )

            tk.Label(
                stage,
                text=title,
                bg=theme.WINDOW_DEEP,
                fg=theme.INK,
                font=(
                    theme.FONT_TITLE,
                    15,
                    "bold",
                ),
            ).pack(
                anchor="w",
                pady=(3, 4),
            )

            tk.Label(
                stage,
                text=text,
                bg=theme.WINDOW_DEEP,
                fg=theme.MUTED,
                justify="left",
                wraplength=210,
                font=(
                    theme.FONT_UI,
                    8,
                ),
            ).pack(
                anchor="w"
            )

        action = CutPanel(
            main,
            fill="#252C35",
            border=theme.ACCENT_DARK,
            cut=14,
            height=165,
        )

        action.pack(
            fill="x",
            pady=(10, 0),
        )

        action.body.grid_columnconfigure(
            1,
            weight=1,
        )

        source_icon = (
            self._line_icon(
                "source",
                42,
                theme.ACCENT_BRIGHT,
            )
        )

        icon_label = tk.Label(
            action.body,
            image=source_icon,
            bg="#252C35",
            bd=0,
        )

        icon_label.image = (
            source_icon
        )

        icon_label.grid(
            row=0,
            column=0,
            rowspan=2,
            sticky="nw",
            padx=(0, 18),
            pady=4,
        )

        tk.Label(
            action.body,
            text=(
                "Aucune Source importée"
                if source_count == 0
                else "Source disponible"
            ),
            bg="#252C35",
            fg=theme.INK,
            font=(
                theme.FONT_TITLE,
                16,
                "bold",
            ),
        ).grid(
            row=0,
            column=1,
            sticky="sw",
        )

        tk.Label(
            action.body,
            text=(
                "La Source reste l'original. "
                "TomeLinea travaillera ensuite "
                "sur son interprétation."
            ),
            bg="#252C35",
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                8,
            ),
        ).grid(
            row=1,
            column=1,
            sticky="nw",
            pady=(4, 0),
        )

        self._button(
            action.body,
            "Importer une source",
            self._source_import_not_connected,
            accent=True,
        ).grid(
            row=0,
            column=2,
            rowspan=2,
            sticky="e",
            padx=(28, 2),
        )


    def _summary_value(
        self,
        parent,
        label: str,
        value: str,
    ) -> None:

        tk.Label(
            parent,
            text=label,
            bg="#252C35",
            fg=theme.MUTED_DARK,
            font=(
                theme.FONT_UI,
                8,
                "bold",
            ),
        ).pack(
            anchor="w",
            pady=(12, 2),
        )

        tk.Label(
            parent,
            text=value,
            bg="#252C35",
            fg=theme.INK,
            font=(
                theme.FONT_UI,
                10,
            ),
        ).pack(
            anchor="w"
        )


    # ==========================================================
    # BARRE BASSE
    # ==============================================================

    def _build_status(
        self,
        parent,
    ) -> None:

        bar = tk.Frame(
            parent,
            bg="#1E242C",
            height=27,
        )

        bar.pack(
            fill="x",
            side="bottom",
        )

        bar.pack_propagate(
            False
        )

        path_text = (
            str(
                self.project_path
            )
            if self.project_path
            else "Projet non enregistré"
        )

        tk.Label(
            bar,
            text=path_text,
            bg="#1E242C",
            fg=theme.MUTED_DARK,
            font=(
                theme.FONT_UI,
                8,
            ),
        ).pack(
            side="left",
            padx=14,
        )

        phase = (
            "Source · Analyse"
            if self.session.project.book
            is None
            else (
                self.current_workspace.capitalize()
            )
        )

        tk.Label(
            bar,
            text=(
                f"TomeLinea V4   •   {phase}"
            ),
            bg="#1E242C",
            fg=theme.ACCENT_DARK,
            font=(
                theme.FONT_UI,
                8,
                "bold",
            ),
        ).pack(
            side="right",
            padx=14,
        )
