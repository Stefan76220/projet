from __future__ import annotations

from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

from src.gui_v4 import theme

from src.v4.project import ProjectV4
from src.v4.workspace import WorkspaceSessionV4


PROJECT_ROOT = Path(__file__).resolve().parents[2]

BRAND_ROOT = (
    PROJECT_ROOT
    / "assets"
    / "branding"
    / "tomelinea"
    / "Tomelinea_logo_pack"
)

BRAND_LOGO = (
    BRAND_ROOT
    / "01_logo_complet"
    / "Tomelinea_logo_complet_600px.png"
)

BRAND_ICON = (
    BRAND_ROOT
    / "04_windows"
    / "Tomelinea.ico"
)


class TomeLineaV4(tk.Tk):
    """
    Interface TomeLinea V4.

    Principe fondamental :

        Projet
          ↓
        Source
          ↓
        Analyse exhaustive
          ↓
        Livre
          ↓
        Structure
          ↓
        Composition
          ↓
        Sortie

    L'interface ne possède jamais de copie du Livre.
    """

    def __init__(self) -> None:
        super().__init__()

        self.title("TomeLinea V4")
        self.geometry("1440x900")
        self.minsize(1100, 700)

        self.configure(
            bg=theme.WINDOW_DEEP
        )

        try:
            if BRAND_ICON.exists():
                self.iconbitmap(
                    str(BRAND_ICON)
                )
        except Exception:
            pass

        self.session: WorkspaceSessionV4 | None = None
        self.project_path: Path | None = None

        self.current_workspace = "source"

        self._images: list[
            ImageTk.PhotoImage
        ] = []

        self.show_home()


    # ==========================================================
    # GENERIQUE
    # ==========================================================

    def _clear(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()


    def _load_logo(
        self,
        *,
        max_width: int,
        max_height: int,
    ) -> ImageTk.PhotoImage | None:

        if not BRAND_LOGO.exists():
            return None

        try:
            image = Image.open(
                BRAND_LOGO
            ).convert("RGBA")

            image.thumbnail(
                (
                    max_width,
                    max_height,
                ),
                Image.Resampling.LANCZOS,
            )

            photo = ImageTk.PhotoImage(
                image
            )

            self._images.append(
                photo
            )

            return photo

        except Exception:
            return None


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
    ) -> tk.Button:

        kwargs = {}

        if width is not None:
            kwargs["width"] = width

        return tk.Button(
            parent,
            text=text,
            command=command,
            state=(
                tk.NORMAL
                if enabled
                else tk.DISABLED
            ),
            bg=(
                theme.ACCENT_DARK
                if accent
                else theme.PANEL_ALT
            ),
            fg=theme.INK,
            activebackground=(
                theme.ACCENT
                if accent
                else theme.PANEL_SOFT
            ),
            activeforeground=theme.WHITE,
            disabledforeground=theme.MUTED_DARK,
            relief="flat",
            bd=0,
            padx=(
                14 if compact else 20
            ),
            pady=(
                7 if compact else 12
            ),
            font=(
                theme.FONT_UI,
                10 if compact else 11,
                "bold",
            ),
            cursor=(
                "hand2"
                if enabled
                else "arrow"
            ),
            **kwargs,
        )


    # ==========================================================
    # ACCUEIL
    # ==========================================================

    def show_home(self) -> None:

        self._clear()

        root = tk.Frame(
            self,
            bg=theme.WINDOW_DEEP,
        )

        root.pack(
            fill="both",
            expand=True,
        )

        top = tk.Frame(
            root,
            bg=theme.WINDOW_DEEP,
        )

        top.pack(
            fill="x",
            padx=48,
            pady=(34, 10),
        )

        logo = self._load_logo(
            max_width=430,
            max_height=150,
        )

        if logo is not None:
            tk.Label(
                top,
                image=logo,
                bg=theme.WINDOW_DEEP,
            ).pack(
                anchor="w"
            )

        else:
            tk.Label(
                top,
                text="TOMELINEA",
                bg=theme.WINDOW_DEEP,
                fg=theme.INK,
                font=(
                    theme.FONT_TITLE,
                    30,
                    "bold",
                ),
            ).pack(
                anchor="w"
            )

        tk.Label(
            top,
            text="V4 • espace éditorial",
            bg=theme.WINDOW_DEEP,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                11,
            ),
        ).pack(
            anchor="w",
            pady=(8, 0),
        )

        body = tk.Frame(
            root,
            bg=theme.WINDOW_DEEP,
        )

        body.pack(
            expand=True,
            padx=70,
            pady=(20, 70),
        )

        tk.Label(
            body,
            text="Votre livre",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(
                theme.FONT_TITLE,
                25,
                "bold",
            ),
        ).pack(
            anchor="w",
            pady=(0, 24),
        )

        cards = tk.Frame(
            body,
            bg=theme.WINDOW_DEEP,
        )

        cards.pack()

        self._home_card(
            cards,
            column=0,
            title="Créer un projet",
            text=(
                "Créer l'espace de travail. "
                "La nature du livre sera comprise "
                "ensuite à partir de sa Source."
            ),
            button="Créer",
            command=self._create_project_dialog,
            accent=True,
        )

        self._home_card(
            cards,
            column=1,
            title="Ouvrir",
            text=(
                "Ouvrir un projet TomeLinea V4 "
                "déjà enregistré."
            ),
            button="Ouvrir un projet",
            command=self._open_project,
        )

        active = (
            self.session is not None
        )

        active_name = (
            self.session.project.title
            if active
            else "Aucun projet actif"
        )

        self._home_card(
            cards,
            column=2,
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


    def _home_card(
        self,
        parent,
        *,
        column: int,
        title: str,
        text: str,
        button: str,
        command,
        accent: bool = False,
        enabled: bool = True,
    ) -> None:

        card = tk.Frame(
            parent,
            bg=theme.PANEL,
            width=310,
            height=230,
            highlightthickness=1,
            highlightbackground=theme.BORDER_SOFT,
        )

        card.grid(
            row=0,
            column=column,
            padx=12,
            sticky="nsew",
        )

        card.grid_propagate(
            False
        )

        tk.Label(
            card,
            text=title,
            bg=theme.PANEL,
            fg=theme.INK,
            font=(
                theme.FONT_UI,
                15,
                "bold",
            ),
        ).pack(
            anchor="w",
            padx=24,
            pady=(28, 12),
        )

        tk.Label(
            card,
            text=text,
            bg=theme.PANEL,
            fg=theme.MUTED,
            justify="left",
            wraplength=255,
            font=(
                theme.FONT_UI,
                10,
            ),
        ).pack(
            anchor="w",
            padx=24,
        )

        tk.Frame(
            card,
            bg=theme.PANEL,
        ).pack(
            fill="both",
            expand=True,
        )

        self._button(
            card,
            button,
            command,
            accent=accent,
            enabled=enabled,
        ).pack(
            anchor="w",
            padx=24,
            pady=24,
        )


    # ==========================================================
    # CREER
    # ==========================================================

    def _create_project_dialog(
        self,
    ) -> None:

        dialog = tk.Toplevel(
            self
        )

        dialog.title(
            "Créer un projet TomeLinea"
        )

        dialog.configure(
            bg=theme.WINDOW
        )

        dialog.resizable(
            False,
            False,
        )

        dialog.transient(
            self
        )

        dialog.grab_set()

        frame = tk.Frame(
            dialog,
            bg=theme.WINDOW,
            padx=30,
            pady=28,
        )

        frame.pack()

        tk.Label(
            frame,
            text="Créer un projet",
            bg=theme.WINDOW,
            fg=theme.INK,
            font=(
                theme.FONT_TITLE,
                20,
                "bold",
            ),
        ).pack(
            anchor="w"
        )

        tk.Label(
            frame,
            text=(
                "TomeLinea déterminera ensuite "
                "la nature et la structure du livre "
                "à partir de sa Source."
            ),
            bg=theme.WINDOW,
            fg=theme.MUTED,
            justify="left",
            wraplength=390,
            font=(
                theme.FONT_UI,
                10,
            ),
        ).pack(
            anchor="w",
            pady=(8, 22),
        )

        tk.Label(
            frame,
            text="Nom du projet",
            bg=theme.WINDOW,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                10,
            ),
        ).pack(
            anchor="w",
            pady=(0, 6),
        )

        title_var = tk.StringVar(
            value="Nouveau livre"
        )

        entry = tk.Entry(
            frame,
            textvariable=title_var,
            width=44,
            bg=theme.PANEL_ALT,
            fg=theme.INK,
            insertbackground=theme.INK,
            relief="flat",
            font=(
                theme.FONT_UI,
                11,
            ),
        )

        entry.pack(
            fill="x",
            ipady=9,
        )

        self._button(
            frame,
            "Créer le projet",
            lambda: self._create_project(
                title_var.get(),
                dialog,
            ),
            accent=True,
        ).pack(
            anchor="e",
            pady=(24, 0),
        )

        entry.bind(
            "<Return>",
            lambda _event: self._create_project(
                title_var.get(),
                dialog,
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
            f"+{max(0, x)}+{max(0, y)}"
        )

        entry.focus_set()
        entry.selection_range(
            0,
            tk.END,
        )


    def _create_project(
        self,
        title: str,
        dialog: tk.Toplevel,
    ) -> None:

        clean_title = (
            str(title).strip()
            or "Nouveau livre"
        )

        # ------------------------------------------------------
        # NOUVELLE LOGIQUE V4
        #
        # On crée uniquement le Projet.
        #
        # Aucun BookV4.
        # Aucune page.
        # Aucun type de livre.
        # Aucun classement anticipé.
        # ------------------------------------------------------

        project = ProjectV4(
            title=clean_title
        )

        self.session = (
            WorkspaceSessionV4(
                project
            )
        )

        self.project_path = None

        self.current_workspace = (
            "source"
        )

        dialog.destroy()

        self.show_workspace(
            "source"
        )


    # ==========================================================
    # OUVRIR
    # ==========================================================

    def _open_project(
        self,
    ) -> None:

        filename = filedialog.askopenfilename(
            parent=self,
            title="Ouvrir un projet TomeLinea V4",
            filetypes=(
                (
                    "Projet TomeLinea V4",
                    "*.json",
                ),
                (
                    "Tous les fichiers",
                    "*.*",
                ),
            ),
        )

        if not filename:
            return

        try:
            self.session = (
                WorkspaceSessionV4.open(
                    filename
                )
            )

            self.project_path = Path(
                filename
            )

            if (
                self.session.project.book
                is None
            ):
                self.current_workspace = (
                    "source"
                )
            else:
                self.current_workspace = (
                    "structure"
                )

            self.show_workspace(
                self.current_workspace
            )

        except Exception as exc:
            messagebox.showerror(
                "TomeLinea",
                (
                    "Impossible d'ouvrir "
                    "ce projet.\n\n"
                    f"{exc}"
                ),
                parent=self,
            )


    # ==========================================================
    # ESPACE PROJET
    # ==========================================================

    def show_workspace(
        self,
        workspace: str,
    ) -> None:

        if self.session is None:
            self.show_home()
            return

        allowed = {
            "source",
            "structure",
            "composition",
            "sortie",
        }

        if workspace not in allowed:
            workspace = "source"

        has_book = (
            self.session.project.book
            is not None
        )

        # Tant que l'analyse n'a pas produit le Livre,
        # Structure / Composition / Sortie n'ont rien à montrer.
        if (
            workspace != "source"
            and not has_book
        ):
            workspace = "source"

        self.current_workspace = workspace

        self._clear()

        root = tk.Frame(
            self,
            bg=theme.WINDOW_DEEP,
        )

        root.pack(
            fill="both",
            expand=True,
        )

        self._build_workspace_header(
            root
        )

        content = tk.Frame(
            root,
            bg=theme.WINDOW,
        )

        content.pack(
            fill="both",
            expand=True,
        )

        if workspace == "source":
            self._build_source(
                content
            )

        elif workspace == "structure":
            self._build_structure(
                content
            )

        elif workspace == "composition":
            self._build_composition(
                content
            )

        else:
            self._build_output(
                content
            )

        self._build_status(
            root
        )


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
            height=72,
        )

        bar.pack(
            fill="x"
        )

        bar.pack_propagate(
            False
        )

        left = tk.Frame(
            bar,
            bg=theme.WINDOW_DEEP,
        )

        left.pack(
            side="left",
            fill="y",
            padx=(20, 10),
        )

        self._button(
            left,
            "Accueil",
            self.show_home,
            compact=True,
        ).pack(
            side="left",
            pady=18,
        )

        tk.Label(
            left,
            text="TOMELINEA",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(
                theme.FONT_TITLE,
                15,
                "bold",
            ),
        ).pack(
            side="left",
            padx=(18, 12),
            pady=22,
        )

        nav = tk.Frame(
            bar,
            bg=theme.WINDOW_DEEP,
        )

        nav.pack(
            side="left",
            fill="y",
            padx=15,
        )

        for key, label in theme.NAV_ITEMS:

            active = (
                key
                == self.current_workspace
            )

            enabled = (
                key == "source"
                or has_book
            )

            button = tk.Button(
                nav,
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
                bg=(
                    theme.ACCENT_SOFT
                    if active
                    else theme.WINDOW_DEEP
                ),
                fg=(
                    theme.ACCENT_BRIGHT
                    if active
                    else theme.MUTED
                ),
                disabledforeground=theme.MUTED_DARK,
                activebackground=theme.PANEL,
                activeforeground=theme.WHITE,
                relief="flat",
                bd=0,
                padx=18,
                pady=10,
                font=(
                    theme.FONT_UI,
                    11,
                    "bold",
                ),
                cursor=(
                    "hand2"
                    if enabled
                    else "arrow"
                ),
            )

            button.pack(
                side="left",
                padx=2,
                pady=15,
            )

        right = tk.Frame(
            bar,
            bg=theme.WINDOW_DEEP,
        )

        right.pack(
            side="right",
            fill="y",
            padx=20,
        )

        self._button(
            right,
            "Enregistrer",
            self._save_project,
            accent=True,
            compact=True,
        ).pack(
            side="right",
            pady=18,
            padx=(8, 0),
        )

        self._button(
            right,
            "Rétablir",
            self._redo,
            compact=True,
            enabled=self.session.can_redo,
        ).pack(
            side="right",
            pady=18,
            padx=4,
        )

        self._button(
            right,
            "Annuler",
            self._undo,
            compact=True,
            enabled=self.session.can_undo,
        ).pack(
            side="right",
            pady=18,
            padx=4,
        )


    # ==========================================================
    # SOURCE / ANALYSE
    # ==========================================================

    def _build_source(
        self,
        parent,
    ) -> None:

        project = self.session.project

        sidebar = tk.Frame(
            parent,
            bg=theme.PANEL,
            width=280,
        )

        sidebar.pack(
            side="left",
            fill="y",
        )

        sidebar.pack_propagate(
            False
        )

        tk.Label(
            sidebar,
            text="PROJET",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                9,
                "bold",
            ),
        ).pack(
            anchor="w",
            padx=24,
            pady=(26, 5),
        )

        tk.Label(
            sidebar,
            text=project.title,
            bg=theme.PANEL,
            fg=theme.INK,
            wraplength=220,
            justify="left",
            font=(
                theme.FONT_TITLE,
                17,
                "bold",
            ),
        ).pack(
            anchor="w",
            padx=24,
        )

        source_count = len(
            project.source.elements
        )

        tk.Label(
            sidebar,
            text=(
                f"{source_count} source(s)"
            ),
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                10,
            ),
        ).pack(
            anchor="w",
            padx=24,
            pady=(10, 0),
        )

        tk.Label(
            sidebar,
            text="LIVRE",
            bg=theme.PANEL,
            fg=theme.MUTED_DARK,
            font=(
                theme.FONT_UI,
                9,
                "bold",
            ),
        ).pack(
            anchor="w",
            padx=24,
            pady=(34, 5),
        )

        tk.Label(
            sidebar,
            text=(
                "À construire"
                if project.book is None
                else "Construit"
            ),
            bg=theme.PANEL,
            fg=(
                theme.ACCENT_BRIGHT
                if project.book is not None
                else theme.MUTED
            ),
            font=(
                theme.FONT_UI,
                10,
            ),
        ).pack(
            anchor="w",
            padx=24,
        )

        main = tk.Frame(
            parent,
            bg=theme.WINDOW,
        )

        main.pack(
            fill="both",
            expand=True,
            padx=46,
            pady=34,
        )

        tk.Label(
            main,
            text="Source du livre",
            bg=theme.WINDOW,
            fg=theme.INK,
            font=(
                theme.FONT_TITLE,
                26,
                "bold",
            ),
        ).pack(
            anchor="w"
        )

        tk.Label(
            main,
            text=(
                "TomeLinea commence par comprendre le livre. "
                "Aucune structure éditoriale n'est imposée à l'avance."
            ),
            bg=theme.WINDOW,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                11,
            ),
        ).pack(
            anchor="w",
            pady=(8, 30),
        )

        flow = tk.Frame(
            main,
            bg=theme.WINDOW,
        )

        flow.pack(
            anchor="w"
        )

        self._stage_card(
            flow,
            column=0,
            number="1",
            title="Ajouter la Source",
            text=(
                "Importer le document original "
                "qui servira de base au livre."
            ),
            active=True,
        )

        self._stage_card(
            flow,
            column=1,
            number="2",
            title="Analyse exhaustive",
            text=(
                "TomeLinea examine autant que nécessaire "
                "le contenu, les pages et leur organisation."
            ),
            active=False,
        )

        self._stage_card(
            flow,
            column=2,
            number="3",
            title="Livre compris",
            text=(
                "La Structure est proposée à partir de "
                "l'analyse, puis reste entièrement révisable."
            ),
            active=False,
        )

        action = tk.Frame(
            main,
            bg=theme.PANEL,
            highlightthickness=1,
            highlightbackground=theme.BORDER_SOFT,
        )

        action.pack(
            fill="x",
            pady=(36, 0),
        )

        inner = tk.Frame(
            action,
            bg=theme.PANEL,
        )

        inner.pack(
            fill="x",
            padx=24,
            pady=22,
        )

        tk.Label(
            inner,
            text=(
                "Aucune Source importée"
                if source_count == 0
                else "Source disponible"
            ),
            bg=theme.PANEL,
            fg=theme.INK,
            font=(
                theme.FONT_UI,
                13,
                "bold",
            ),
        ).pack(
            side="left"
        )

        self._button(
            inner,
            "Importer une source",
            self._source_import_not_connected,
            accent=True,
        ).pack(
            side="right"
        )

        tk.Label(
            main,
            text=(
                "Le raccord réel de l'import et de l'analyse "
                "sera la prochaine étape. Cette version ne crée "
                "volontairement aucun faux livre pour contourner l'analyse."
            ),
            bg=theme.WINDOW,
            fg=theme.MUTED_DARK,
            wraplength=760,
            justify="left",
            font=(
                theme.FONT_UI,
                9,
            ),
        ).pack(
            anchor="w",
            pady=(16, 0),
        )


    def _stage_card(
        self,
        parent,
        *,
        column: int,
        number: str,
        title: str,
        text: str,
        active: bool,
    ) -> None:

        card = tk.Frame(
            parent,
            bg=(
                theme.ACCENT_SOFT
                if active
                else theme.PANEL
            ),
            width=275,
            height=170,
            highlightthickness=1,
            highlightbackground=(
                theme.ACCENT_DARK
                if active
                else theme.BORDER_SOFT
            ),
        )

        card.grid(
            row=0,
            column=column,
            padx=(0, 14),
        )

        card.grid_propagate(
            False
        )

        tk.Label(
            card,
            text=number,
            bg=(
                theme.ACCENT_SOFT
                if active
                else theme.PANEL
            ),
            fg=(
                theme.ACCENT_BRIGHT
                if active
                else theme.MUTED_DARK
            ),
            font=(
                theme.FONT_TITLE,
                22,
                "bold",
            ),
        ).pack(
            anchor="w",
            padx=20,
            pady=(18, 2),
        )

        tk.Label(
            card,
            text=title,
            bg=(
                theme.ACCENT_SOFT
                if active
                else theme.PANEL
            ),
            fg=theme.INK,
            font=(
                theme.FONT_UI,
                12,
                "bold",
            ),
        ).pack(
            anchor="w",
            padx=20,
        )

        tk.Label(
            card,
            text=text,
            bg=(
                theme.ACCENT_SOFT
                if active
                else theme.PANEL
            ),
            fg=theme.MUTED,
            wraplength=225,
            justify="left",
            font=(
                theme.FONT_UI,
                9,
            ),
        ).pack(
            anchor="w",
            padx=20,
            pady=(8, 0),
        )


    def _source_import_not_connected(
        self,
    ) -> None:

        messagebox.showinfo(
            "TomeLinea V4",
            (
                "La logique est maintenant correcte :\n\n"
                "Projet → Source → Analyse → Livre.\n\n"
                "Le moteur réel d'import et d'analyse "
                "sera raccordé dans l'étape suivante."
            ),
            parent=self,
        )


    # ==========================================================
    # STRUCTURE
    # ==========================================================

    def _build_structure(
        self,
        parent,
    ) -> None:

        book = self.session.book

        sidebar = tk.Frame(
            parent,
            bg=theme.PANEL,
            width=280,
        )

        sidebar.pack(
            side="left",
            fill="y",
        )

        sidebar.pack_propagate(
            False
        )

        tk.Label(
            sidebar,
            text="STRUCTURE",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                9,
                "bold",
            ),
        ).pack(
            anchor="w",
            padx=24,
            pady=(26, 5),
        )

        tk.Label(
            sidebar,
            text=book.title,
            bg=theme.PANEL,
            fg=theme.INK,
            wraplength=220,
            justify="left",
            font=(
                theme.FONT_TITLE,
                17,
                "bold",
            ),
        ).pack(
            anchor="w",
            padx=24,
        )

        tk.Label(
            sidebar,
            text=(
                f"{len(book.page_order)} page(s)"
            ),
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                10,
            ),
        ).pack(
            anchor="w",
            padx=24,
            pady=(8, 0),
        )

        main = tk.Frame(
            parent,
            bg=theme.WINDOW,
        )

        main.pack(
            fill="both",
            expand=True,
            padx=34,
            pady=28,
        )

        tk.Label(
            main,
            text="Structure du livre",
            bg=theme.WINDOW,
            fg=theme.INK,
            font=(
                theme.FONT_TITLE,
                24,
                "bold",
            ),
        ).pack(
            anchor="w",
            pady=(0, 6),
        )

        pages_frame = tk.Frame(
            main,
            bg=theme.WINDOW,
        )

        pages_frame.pack(
            fill="both",
            expand=True,
            pady=(20, 0),
        )

        for index, page_id in enumerate(
            book.page_order,
            start=1,
        ):

            page = book.pages[
                page_id
            ]

            active = (
                page_id
                == self.session.active_page_id
            )

            row = tk.Button(
                pages_frame,
                command=lambda pid=page_id: (
                    self._activate_page(
                        pid
                    )
                ),
                bg=(
                    theme.ACCENT_SOFT
                    if active
                    else theme.PANEL
                ),
                fg=theme.INK,
                activebackground=theme.PANEL_ALT,
                activeforeground=theme.WHITE,
                relief="flat",
                bd=0,
                anchor="w",
                padx=18,
                pady=12,
                font=(
                    theme.FONT_UI,
                    10,
                ),
                text=(
                    f"{index:02d}    "
                    f"{page.title or 'Sans titre'}"
                    f"    ·    {page.page_type}"
                ),
                cursor="hand2",
            )

            row.pack(
                fill="x",
                pady=2,
            )


    def _activate_page(
        self,
        page_id: str,
    ) -> None:

        self.session.set_active_page(
            page_id
        )

        self.show_workspace(
            self.current_workspace
        )


    # ==========================================================
    # COMPOSITION
    # ==========================================================

    def _build_composition(
        self,
        parent,
    ) -> None:

        page = self.session.active_page

        inspector = tk.Frame(
            parent,
            bg=theme.PANEL,
            width=260,
        )

        inspector.pack(
            side="right",
            fill="y",
        )

        inspector.pack_propagate(
            False
        )

        tk.Label(
            inspector,
            text="PAGE ACTIVE",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                9,
                "bold",
            ),
        ).pack(
            anchor="w",
            padx=22,
            pady=(26, 8),
        )

        if page is not None:

            tk.Label(
                inspector,
                text=(
                    page.title
                    or "Sans titre"
                ),
                bg=theme.PANEL,
                fg=theme.INK,
                wraplength=210,
                justify="left",
                font=(
                    theme.FONT_TITLE,
                    16,
                    "bold",
                ),
            ).pack(
                anchor="w",
                padx=22,
            )

            tk.Label(
                inspector,
                text=page.page_type,
                bg=theme.PANEL,
                fg=theme.ACCENT_BRIGHT,
                font=(
                    theme.FONT_UI,
                    10,
                ),
            ).pack(
                anchor="w",
                padx=22,
                pady=(5, 22),
            )

        center = tk.Frame(
            parent,
            bg=theme.WINDOW,
        )

        center.pack(
            fill="both",
            expand=True,
        )

        tk.Label(
            center,
            text="Composition",
            bg=theme.WINDOW,
            fg=theme.INK,
            font=(
                theme.FONT_TITLE,
                22,
                "bold",
            ),
        ).pack(
            anchor="w",
            padx=34,
            pady=(28, 10),
        )

        canvas = tk.Canvas(
            center,
            bg=theme.WINDOW_DEEP,
            bd=0,
            highlightthickness=0,
        )

        canvas.pack(
            fill="both",
            expand=True,
            padx=34,
            pady=(0, 28),
        )

        canvas.bind(
            "<Configure>",
            lambda _event: (
                self._draw_page(
                    canvas
                )
            ),
        )


    def _draw_page(
        self,
        canvas: tk.Canvas,
    ) -> None:

        canvas.delete(
            "all"
        )

        page = self.session.active_page

        if page is None:
            return

        fmt = self.session.book.format

        width = max(
            canvas.winfo_width(),
            100,
        )

        height = max(
            canvas.winfo_height(),
            100,
        )

        scale = min(
            (width - 120)
            / float(fmt.width_mm),
            (height - 100)
            / float(fmt.height_mm),
        )

        scale = max(
            0.2,
            scale,
        )

        page_w = (
            float(fmt.width_mm)
            * scale
        )

        page_h = (
            float(fmt.height_mm)
            * scale
        )

        x = (
            width / 2
            - page_w / 2
        )

        y = (
            height / 2
            - page_h / 2
        )

        canvas.create_rectangle(
            x,
            y,
            x + page_w,
            y + page_h,
            fill=theme.PAGE,
            outline=theme.PAGE_BORDER,
        )


    # ==========================================================
    # SORTIE
    # ==========================================================

    def _build_output(
        self,
        parent,
    ) -> None:

        body = tk.Frame(
            parent,
            bg=theme.WINDOW,
        )

        body.pack(
            fill="both",
            expand=True,
            padx=50,
            pady=42,
        )

        tk.Label(
            body,
            text="Sortie",
            bg=theme.WINDOW,
            fg=theme.INK,
            font=(
                theme.FONT_TITLE,
                26,
                "bold",
            ),
        ).pack(
            anchor="w"
        )


    # ==========================================================
    # SAUVEGARDE / UNDO
    # ==========================================================

    def _save_project(
        self,
    ) -> None:

        if self.session is None:
            return

        path = self.project_path

        if path is None:

            filename = filedialog.asksaveasfilename(
                parent=self,
                title=(
                    "Enregistrer le projet TomeLinea V4"
                ),
                defaultextension=".json",
                filetypes=(
                    (
                        "Projet TomeLinea V4",
                        "*.json",
                    ),
                ),
            )

            if not filename:
                return

            path = Path(
                filename
            )

            self.project_path = path

        try:
            self.session.save(
                path
            )

            self.show_workspace(
                self.current_workspace
            )

        except Exception as exc:
            messagebox.showerror(
                "TomeLinea",
                (
                    "Impossible d'enregistrer "
                    "le projet.\n\n"
                    f"{exc}"
                ),
                parent=self,
            )


    def _undo(
        self,
    ) -> None:

        if (
            self.session is None
            or not self.session.can_undo
        ):
            return

        self.session.undo()

        self.show_workspace(
            self.current_workspace
        )


    def _redo(
        self,
    ) -> None:

        if (
            self.session is None
            or not self.session.can_redo
        ):
            return

        self.session.redo()

        self.show_workspace(
            self.current_workspace
        )


    # ==========================================================
    # STATUS
    # ==========================================================

    def _build_status(
        self,
        parent,
    ) -> None:

        bar = tk.Frame(
            parent,
            bg=theme.WINDOW_DEEP,
            height=28,
        )

        bar.pack(
            fill="x",
            side="bottom",
        )

        bar.pack_propagate(
            False
        )

        path_text = (
            str(self.project_path)
            if self.project_path
            else "Projet non enregistré"
        )

        tk.Label(
            bar,
            text=path_text,
            bg=theme.WINDOW_DEEP,
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
            "Source / Analyse"
            if self.session.project.book
            is None
            else self.current_workspace.capitalize()
        )

        tk.Label(
            bar,
            text=f"TomeLinea V4 • {phase}",
            bg=theme.WINDOW_DEEP,
            fg=theme.MUTED_DARK,
            font=(
                theme.FONT_UI,
                8,
            ),
        ).pack(
            side="right",
            padx=14,
        )
