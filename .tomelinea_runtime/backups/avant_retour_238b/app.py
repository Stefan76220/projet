from __future__ import annotations

from src.v4.page_content_classifier import classify_book_pages
from src.v4.page_content_inventory import page_content_inventory
from src.v4.page_element_roles import page_element_roles
from src.v4.text_flow import page_text_flow_entries
from src.v4.book_import_state import (
    detect_book_import_state,
    apply_book_layout_settings,
)
from src.v4.format_catalog import (
    BY_KEY as STANDARD_FORMATS_BY_KEY,
    STANDARD_BOOK_FORMATS,
    find_standard_format,
    nearest_standard_format,
    formats_by_ui_family,
    ui_family_for_format,
)

from src.gui_v4.controls import TLButton, TLScrollbar

from pathlib import Path
from copy import deepcopy
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from PIL import Image, ImageTk

from src.gui_v4 import theme

from src.v4.project import ProjectV4
from src.v4.workspace import WorkspaceSessionV4
from src.v4.source_pipeline import (
    accept_initial_proposal,
    analyze_source_to_proposal,
)
from src.v4.structure_auto import is_auto_origin_page, is_structural_auto_page
from src.v4.book_pagination import (
    interior_page_count,
    interior_page_ids,
    pagination_summary,
)
from src.v4.structure_sync import sync_structure_rules
from src.v4.structure_spreads import page_spread
from src.v4.structure_ops import (
    insert_manual_page_relative,
    manual_page_relative_index,
)
from src.v4.structure_blocks import (
    atomic_block_for_page,
    move_atomic_block,
)
from src.v4.structure_delete import delete_selected_pages
from src.v4.structure_covers import (
    INSIDE_BACK_COVER,
    INSIDE_FRONT_COVER,
    adjacent_inside_cover_candidate,
    assign_page_as_inside_cover,
    blank_inside_cover,
    can_insert_relative,
    cover_face,
    cover_label,
    inside_cover_candidate_face,
    inside_cover_confirmation_issues,
    inside_cover_confirmation_status,
    is_cover_face,
    is_generated_cover_placeholder,
    is_inside_cover_pending,
    use_adjacent_page_as_inside_cover,
)
from src.v4.structure_editorial import (
    BLANK_AFTER,
    BLANK_BEFORE,
    CONSTRAINT_HELP,
    CONSTRAINT_LABELS,
    DOUBLE_PAGE,
    KNOWN_CONSTRAINTS,
    PAGE_LEFT,
    PAGE_RIGHT,
    SIMILARITY_THRESHOLD,
    active_constraint_kinds,
    constraint_enabled,
    constraint_summary,
    double_page_selection_reason,
    extension_memberships,
    extend_constraint_to_similar,
    similar_page_ids,
    equivalent_automatic_page_ids,
    extend_automatic_page_content,
    remove_similarity_extension,
    set_constraint_on_pages,
)


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

WAIT_MEDIA = (
    PROJECT_ROOT
    / "assets"
    / "branding"
    / "tomelinea"
    / "wait"
    / "TomeLinea_wait_model.gif"
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

    def __init__(self, *, start_hidden: bool = False) -> None:
        super().__init__()

        # L'habillage éditorial peut préparer toute la fenêtre hors écran,
        # puis l'afficher une seule fois quand elle est complètement prête.
        # Cela évite les flashes 1440x900 -> plein écran -> reconstruction.
        if start_hidden:
            try:
                self.withdraw()
            except tk.TclError:
                pass

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

        # Les repères géométriques du Livre sont visibles par défaut.
        # Leur visibilité est un choix d'affichage, pas une donnée éditoriale.
        self._composition_margin_guides_visible = True
        self._composition_bleed_guides_visible = True

        # Sauvegarde temporaire de l'ancien projet pendant Créer / Ouvrir.
        # Le remplacement n'est validé qu'une fois le nouveau parcours réussi.
        self._project_transition_backup = None

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


    def _toolbar_button(
        self,
        parent,
        *,
        text: str | None = None,
        textvariable=None,
        command=None,
        width: int | None = None,
        foreground: str | None = None,
        bold: bool = False,
    ) -> tk.Button:
        """Petit bouton de barre clairement interactif (survol + pression)."""

        kwargs = {}
        if width is not None:
            kwargs["width"] = int(width)

        button = tk.Button(
            parent,
            text=(text or "") if textvariable is None else "",
            textvariable=textvariable,
            command=command,
            bg=theme.PANEL_ALT,
            fg=foreground or theme.INK,
            activebackground=theme.ACCENT_DARK,
            activeforeground=theme.WHITE,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=theme.PAGE_BORDER,
            highlightcolor=theme.ACCENT,
            padx=8,
            pady=4,
            cursor="hand2",
            font=(
                theme.FONT_UI,
                9 if not bold else 8,
                "bold" if bold else "normal",
            ),
            **kwargs,
        )

        normal_bg = theme.PANEL_ALT
        hover_bg = theme.PANEL_SOFT

        def on_enter(_event=None):
            try:
                if str(button.cget("state")) != str(tk.DISABLED):
                    button.configure(bg=hover_bg)
            except Exception:
                pass

        def on_leave(_event=None):
            try:
                button.configure(bg=normal_bg)
            except Exception:
                pass

        button.bind("<Enter>", on_enter, add="+")
        button.bind("<Leave>", on_leave, add="+")

        return button


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



    # ==========================================================
    # SECURITE DES TRANSITIONS DE PROJET
    # ==========================================================

    def _begin_project_transition(
        self,
    ) -> None:
        self._project_transition_backup = (
            self.session,
            self.project_path,
            self.current_workspace,
        )

    def _finish_project_transition(
        self,
    ) -> None:
        self._project_transition_backup = None

    def _rollback_project_transition(
        self,
        *,
        refresh_home: bool = True,
    ) -> None:
        backup = self._project_transition_backup

        if backup is None:
            return

        (
            self.session,
            self.project_path,
            self.current_workspace,
        ) = backup

        self._project_transition_backup = None

        if refresh_home:
            try:
                self.show_home()
            except Exception:
                pass


    def _create_project_from_source(
        self,
    ) -> None:
        """
        Parcours normal V4 :

        Créer un livre
            -> choisir le document
            -> création du Projet
            -> import
            -> analyse
            -> construction automatique
            -> Composition

        Aucun nom n'est demandé ? l'utilisateur.
        """

        filename = filedialog.askopenfilename(
            parent=self,
            title="Créer un livre TomeLinea",
            filetypes=(
                (
                    "Documents pris en charge",
                    "*.pdf *.odt",
                ),
                (
                    "Document PDF",
                    "*.pdf",
                ),
                (
                    "OpenDocument Texte",
                    "*.odt",
                ),
            ),
        )

        if not filename:
            return

        source_path = Path(
            filename
        )

        # Nom automatique à partir du fichier.
        clean_title = (
            source_path.stem
            .replace("_", " ")
            .strip()
        )

        clean_title = (
            " ".join(
                clean_title.split()
            )
            or "Nouveau livre"
        )

        # L'ancien projet actif reste récupérable jusqu'à ce que
        # l'import, l'analyse et la construction du Livre aient réussi.
        self._begin_project_transition()

        try:
            project = ProjectV4(
                title=clean_title
            )

            self.session = (
                WorkspaceSessionV4(
                    project
                )
            )

            self.project_path = None

            # Le résultat attendu du parcours est
            # désormais Composition.
            self.current_workspace = (
                "composition"
            )

            import_started = self._source_import_file(
                str(source_path)
            )

            if not import_started:
                self._rollback_project_transition()

        except Exception as exc:
            self._rollback_project_transition()

            messagebox.showerror(
                "TomeLinea V4",
                (
                    "Le nouveau projet n'a pas pu "
                    "être préparé.\n\n"
                    f"{exc}"
                ),
                parent=self,
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

        # Un nouveau projet TomeLinea commence par sa Source.
        # Le sélecteur s'ouvre dès que l'écran Source est affiché.
        self.after(
            150,
            self._source_import,
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

        # Annuler ne change strictement rien au projet actif.
        if not filename:
            return

        self._begin_project_transition()

        # L'ouverture d'un projet peut prendre plusieurs secondes (lecture,
        # validation, reconstruction de Structure et Composition). L'animation
        # TomeLinea apparaît immédiatement et masque ce travail sans ajouter
        # un délai fixe : le moteur d'attente termine son mouvement dès que le
        # projet est prêt.
        wait_controller = None
        try:
            from src.gui_v4.startup_runtime import start_wait_animation_async
            wait_controller = start_wait_animation_async()
            # Ne jamais attendre l'animation avant de charger le projet :
            # elle accompagne le travail réel, elle ne doit pas le retarder.
        except Exception:
            wait_controller = None

        try:
            # Le nouveau projet est d'abord chargé dans une variable locale.
            # L'ancien reste intact tant que cette étape n'a pas abouti.
            new_session = (
                WorkspaceSessionV4.open(
                    filename
                )
            )

            new_path = Path(
                filename
            )

            if (
                new_session.project.book
                is None
            ):
                new_workspace = "source"
            else:
                new_workspace = "composition"

            self.session = new_session
            self.project_path = new_path
            self.current_workspace = new_workspace

            # Même l'affichage doit réussir avant de remplacer définitivement
            # le projet actif précédent.
            self.show_workspace(
                new_workspace
            )

            self._finish_project_transition()

            if wait_controller is not None:
                try:
                    wait_controller.finish_after_cycle(
                        pump=self.update_idletasks,
                    )
                except Exception:
                    pass

            try:
                self.lift()
                self.focus_force()
            except Exception:
                pass

        except Exception as exc:
            if wait_controller is not None:
                try:
                    wait_controller.finish_after_cycle(
                        pump=self.update_idletasks,
                    )
                except Exception:
                    pass

            self._rollback_project_transition()

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

        # Les commandes d'historique restent techniquement cliquables :
        # leur action consulte l'état réel de la pile au moment du clic.
        # Cela évite qu'un état Tkinter visuel devenu obsolète sous Windows
        # puisse rendre Annuler/Rétablir réellement inopérants.
        self._workspace_redo_button = self._button(
            right,
            "Rétablir",
            self._redo,
            compact=True,
            enabled=True,
        )
        self._workspace_redo_button.pack(
            side="right",
            pady=18,
            padx=4,
        )

        self._workspace_undo_button = self._button(
            right,
            "Annuler",
            self._undo,
            compact=True,
            enabled=True,
        )
        self._workspace_undo_button.pack(
            side="right",
            pady=18,
            padx=4,
        )

        # La pile d'historique pilote directement le bandeau supérieur.
        # Aucun rafraîchissement manuel ne doit être nécessaire après une action.
        try:
            self.session.set_history_change_callback(
                self._refresh_history_buttons
            )
        except Exception:
            self._refresh_history_buttons()

        # Deuxième synchronisation une fois que Tk a réellement construit
        # le bandeau (utile sous Windows après un changement de vue).
        try:
            self.after_idle(self._refresh_history_buttons)
        except Exception:
            pass


    def _refresh_history_buttons(
        self,
        *_history_state,
    ) -> None:
        """Synchronise l'état visuel des commandes Annuler/Rétablir."""

        if self.session is None:
            return

        pairs = (
            (
                getattr(self, "_workspace_undo_button", None),
                bool(self.session.can_undo),
            ),
            (
                getattr(self, "_workspace_redo_button", None),
                bool(self.session.can_redo),
            ),
            (
                getattr(self, "_composition_undo_button", None),
                bool(self.session.can_undo),
            ),
            (
                getattr(self, "_composition_redo_button", None),
                bool(self.session.can_redo),
            ),
        )

        for button, enabled in pairs:
            if button is None:
                continue
            try:
                # Ne jamais utiliser l'état Tk DISABLED pour l'historique.
                # La disponibilité est seulement rendue visuellement ;
                # _undo/_redo relisent can_undo/can_redo au moment du clic.
                # Ainsi, même si Windows retarde un rafraîchissement visuel,
                # une action réellement disponible reste exécutable.
                button.configure(
                    state=tk.NORMAL,
                    cursor=("hand2" if enabled else "arrow"),
                    fg=(theme.INK if enabled else theme.MUTED_DARK),
                    bg=(theme.PANEL_SOFT if enabled else theme.PANEL_ALT),
                    activebackground=(
                        theme.ACCENT_DARK if enabled else theme.PANEL_ALT
                    ),
                )
            except Exception:
                pass


    # ==========================================================
    # SOURCE / ANALYSE
    # ==========================================================

    def _primary_source_element_id(
        self,
    ) -> str | None:

        project = self.session.project

        stored = project.metadata.get(
            "primary_source_element_id"
        )

        if (
            stored is not None
            and stored in project.source.elements
        ):
            return str(stored)

        if not project.source.elements:
            return None

        # Compatibilité avec un projet créé avant
        # l'enregistrement explicite de la Source principale.
        first_id = next(
            iter(
                project.source.elements
            )
        )

        project.metadata[
            "primary_source_element_id"
        ] = first_id

        return first_id


    def _primary_source_version(
        self,
    ):

        element_id = (
            self._primary_source_element_id()
        )

        if element_id is None:
            return None

        element = (
            self.session.project
            .source.elements[
                element_id
            ]
        )

        return element.active_version



    def _build_source(
        self,
        parent,
    ) -> None:
        """
        Compatibilité interne uniquement.

        Source n'est plus un bureau utilisateur.
        Le moteur Source reste actif dans src.v4.
        """

        project = self.session.project

        if project.book is not None:
            self.current_workspace = "composition"

            self.after_idle(
                lambda: self.show_workspace(
                    "composition"
                )
            )

            return

        # Ce cas ne doit normalement plus être visible :
        # la création attend simplement que l'analyse construise
        # le Livre avant d'ouvrir Composition.
        tk.Label(
            parent,
            text="Préparation du livre\u2026",
            bg=theme.WINDOW_DEEP,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                10,
            ),
        ).pack(
            expand=True,
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

        background = (
            theme.ACCENT_SOFT
            if active
            else theme.PANEL
        )

        tk.Label(
            card,
            text=number,
            bg=background,
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
            bg=background,
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
            bg=background,
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


    # ==========================================================
    # IMPORT SOURCE
    # ==========================================================

    def _source_import(
        self,
    ) -> None:

        if self.session.project.book is not None:
            messagebox.showinfo(
                "TomeLinea V4",
                (
                    "Le Livre existe déjà.\n\n"
                    "L'ajout de contenu complémentaire "
                    "sera traité séparément."
                ),
                parent=self,
            )
            return

        filename = filedialog.askopenfilename(
            parent=self,
            title="Choisir la Source du livre",
            filetypes=(
                (
                    "Documents pris en charge",
                    "*.pdf *.odt",
                ),
                (
                    "Document PDF",
                    "*.pdf",
                ),
                (
                    "OpenDocument Texte",
                    "*.odt",
                ),
            ),
        )

        if not filename:
            return

        self._source_import_file(
            filename
        )

    def _source_import_file(
        self,
        filename: str,
    ) -> bool:

        suffix = (
            Path(filename)
            .suffix
            .lower()
        )

        if suffix not in {
            ".pdf",
            ".odt",
        }:
            messagebox.showerror(
                "TomeLinea V4",
                (
                    "Les formats actuellement "
                    "pris en charge sont PDF et ODT."
                ),
                parent=self,
            )
            return False

        project = (
            self.session.project
        )

        try:
            element = (
                project.source.register_file(
                    Path(filename)
                )
            )

            project.metadata[
                "primary_source_element_id"
            ] = element.id

            project.touch()
            project.validate()

        except Exception as exc:
            messagebox.showerror(
                "TomeLinea V4",
                (
                    "Impossible d'importer cette Source."
                    "\n\n"
                    f"{exc}"
                ),
                parent=self,
            )
            return False

        # La Source est maintenant acquise.
        # L'analyse et la construction du Livre
        # restent entièrement automatiques.


        self.after(
            80,
            self._source_analyze_primary,
        )

        return True


    def _source_analyze_primary(
        self,
    ) -> None:

        if getattr(
            self,
            "_source_analysis_running",
            False,
        ):
            return

        project = self.session.project

        element_id = (
            self._primary_source_element_id()
        )

        if element_id is None:
            messagebox.showerror(
                "TomeLinea V4",
                "Aucune Source à analyser.",
                parent=self,
            )
            self._rollback_project_transition()
            return

        # Sauvegarde de la couche Analyse / Proposition.
        # La Source importée reste intacte si l'analyse échoue.
        analysis_before = deepcopy(
            project.analysis
        )

        proposals_before = deepcopy(
            project.proposals
        )

        active_before = (
            project.active_proposal_id
        )

        history_before = deepcopy(
            project.history
        )

        updated_before = (
            project.updated_at
        )

        self._source_analysis_running = True

        # ------------------------------------------------------
        # Fenêtre d'attente commune TomeLinea.
        # Même moteur que le lancement, démarré sans bloquer
        # le début de l'analyse.
        # ------------------------------------------------------

        wait_controller = None

        try:
            from src.gui_v4.startup_runtime import (
                start_wait_animation_async,
            )

            wait_controller = (
                start_wait_animation_async()
            )

        except Exception:
            wait_controller = None

        state = {
            "done": False,
            "result": None,
            "error": None,
        }

        def worker():
            try:
                state["result"] = (
                    analyze_source_to_proposal(
                        project,
                        source_element_id=(
                            element_id
                        ),
                    )
                )

            except Exception as exc:

                project.analysis = (
                    analysis_before
                )

                project.proposals = (
                    proposals_before
                )

                project.active_proposal_id = (
                    active_before
                )

                project.history = (
                    history_before
                )

                project.updated_at = (
                    updated_before
                )

                state["error"] = exc

            finally:
                state["done"] = True

        thread = threading.Thread(
            target=worker,
            daemon=True,
        )

        thread.start()

        def poll():

            if not state["done"]:

                self.after(
                    120,
                    poll,
                )

                return

            self._source_analysis_running = False

            if wait_controller is not None:
                try:
                    wait_controller.finish_after_cycle(
                        pump=self.update_idletasks,
                    )
                except Exception:
                    pass

            if state["error"] is not None:

                messagebox.showerror(
                    "TomeLinea V4",
                    (
                        "L'analyse de la Source "
                        "n'a pas pu être terminée."
                        "\n\n"
                        f"{state['error']}"
                    ),
                    parent=self,
                )

                self._rollback_project_transition()
                return

            analysis_result = (
                state["result"]
            )

            # --------------------------------------------------
            # V4 :
            # une analyse réussie construit immédiatement
            # le premier Livre.
            #
            # Il n'y a plus de validation page par page
            # ni de confirmation intermédiaire.
            # --------------------------------------------------

            try:
                book_result = (
                    accept_initial_proposal(
                        project
                    )
                )

                self.session.refresh_context()

                # Bilan conservé dans le Projet.
                # Il sera prochainement présenté directement
                # dans l'interface, sans fenêtre modale.
                project.metadata[
                    "last_source_analysis_summary"
                ] = {
                    "source_pages": (
                        analysis_result
                        .extraction
                        .page_count
                    ),
                    "families": len(
                        analysis_result
                        .similarity
                        .families
                    ),
                    "book_pages": (
                        book_result.page_count
                    ),
                    "parts": (
                        book_result.part_count
                    ),
                    "models": (
                        analysis_result
                        .proposed_model_count
                    ),
                    "issues": (
                        analysis_result
                        .issue_count
                    ),
                }

                project.touch()
                project.validate()

            except Exception as exc:

                messagebox.showerror(
                    "TomeLinea V4",
                    (
                        "L'analyse est terminée, "
                        "mais le Livre n'a pas pu "
                        "être construit."
                        "\n\n"
                        f"{exc}"
                    ),
                    parent=self,
                )

                self._rollback_project_transition()
                return

            # Pas de fenêtre "Analyse terminée".
            # Pas de bouton "Valider la proposition".
            #
            # Le Livre existe : on entre directement
            # dans sa Structure.
            # Le nouveau projet devient réellement actif seulement ici.
            self._finish_project_transition()

            self._composition_book_state_open = True
            self._composition_text_flow_open = False
            self._composition_book_state_edit = False
            self.show_workspace(
                "composition"
            )

            image_audit = (
                self._composition_audit_book_images()
            )

            project.metadata[
                "last_image_quality_audit"
            ] = image_audit

            project.touch()

            # L'analyse qualité des images reste disponible dans
            # Mise en page, mais elle ne s'impose plus au démarrage.

        self.after(
            100,
            poll,
        )


    def _source_accept_proposal(
        self,
    ) -> None:

        project = self.session.project

        if project.book is not None:
            self.show_workspace(
                "structure"
            )
            return

        proposal = (
            project.active_proposal
        )

        if proposal is None:
            messagebox.showerror(
                "TomeLinea V4",
                "Aucune proposition disponible.",
                parent=self,
            )
            return

        try:
            accept_initial_proposal(
                project
            )

            self.session.refresh_context()

        except Exception as exc:
            messagebox.showerror(
                "TomeLinea V4",
                (
                    "Impossible de construire "
                    "le Livre."
                    "\n\n"
                    f"{exc}"
                ),
                parent=self,
            )
            return

        self.show_workspace(
            "structure"
        )



    def _build_structure(
        self,
        parent,
    ) -> None:
        """
        Compatibilité interne uniquement.

        Structure n'est plus un bureau utilisateur.
        Les calculs Structure restent actifs dans src.v4.
        """

        if (
            self.session is not None
            and self.session.project.book is not None
        ):
            self.current_workspace = "composition"

            self.after_idle(
                lambda: self.show_workspace(
                    "composition"
                )
            )

            return

        tk.Label(
            parent,
            text="Livre indisponible",
            bg=theme.WINDOW_DEEP,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                10,
            ),
        ).pack(
            expand=True,
        )

    def _activate_page(
        self,
        page_id: str,
        *,
        preserve_page_selection: bool = False,
    ) -> None:
        """Active une page et la revele dans l'Explorateur Composition."""

        page_id = str(page_id)

        if not preserve_page_selection:
            self._composition_selected_page_ids = {
                page_id
            }

        self.session.set_active_page(
            page_id
        )

        if (
            self.current_workspace
            == "composition"
        ):
            # Tous les chemins de navigation convergent ici : clic dans
            # l'Explorateur, Aller, Precedente et Suivante. Le Plan, le
            # centre et l'inspecteur droit suivent donc la meme page active.
            # Si la page se trouve dans une branche repliee, cette branche
            # est ouverte juste assez pour rendre la page active visible.
            self._composition_update_plan_selection()
            self._composition_scroll_to_page(
                page_id,
                animated=False,
            )
            self._composition_refresh_center_navigation()
            self._composition_update_editor()
            return

        self.show_workspace(
            self.current_workspace
        )

    def _build_composition(
        self,
        parent,
    ) -> None:
        """Composition : naviguer à gauche, contrôler au centre, agir à droite."""

        book = self.session.book

        if book is None:
            return

        page_order = list(
            book.page_order
        )

        root = tk.Frame(
            parent,
            bg=theme.WINDOW,
        )
        root.pack(
            fill="both",
            expand=True,
        )

        # ======================================================
        # GAUCHE — EXPLORATEUR DU LIVRE
        # ======================================================

        plan = tk.Frame(
            root,
            bg=theme.PANEL,
            width=320,
        )
        plan.pack(
            side="left",
            fill="y",
        )
        plan.pack_propagate(
            False
        )

        editor_host = tk.Frame(
            root,
            bg=theme.WINDOW,
        )
        editor_host.pack(
            side="left",
            fill="both",
            expand=True,
        )

        tk.Label(
            plan,
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
            padx=18,
            pady=(18, 3),
        )

        tk.Label(
            plan,
            text=book.title,
            bg=theme.PANEL,
            fg=theme.INK,
            wraplength=275,
            justify="left",
            font=(
                theme.FONT_TITLE,
                15,
                "bold",
            ),
        ).pack(
            anchor="w",
            padx=18,
        )

        self._composition_page_count_var = (
            tk.StringVar(
                value=pagination_summary(book)
            )
        )

        tk.Label(
            plan,
            textvariable=(
                self._composition_page_count_var
            ),
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                9,
            ),
        ).pack(
            anchor="w",
            padx=18,
            pady=(4, 10),
        )

        # Navigation directe, utile surtout pour les gros livres.
        jump = tk.Frame(
            plan,
            bg=theme.PANEL,
        )
        jump.pack(
            fill="x",
            padx=18,
            pady=(0, 10),
        )

        # Le champ Aller fait partie de la navigation synchronisee : il
        # affiche toujours le numero physique de la page active, quel que
        # soit le moyen utilise pour naviguer dans le Livre.
        self._composition_jump_page_var = tk.StringVar()
        page_var = self._composition_jump_page_var

        entry = tk.Entry(
            jump,
            textvariable=page_var,
            width=8,
            justify="center",
            bg=theme.PANEL_ALT,
            fg=theme.INK,
            insertbackground=theme.INK,
            relief="flat",
            font=(
                theme.FONT_UI,
                9,
            ),
        )
        entry.pack(
            side="left",
            fill="x",
            expand=True,
            ipady=5,
        )

        def go_to_page(
            _event=None,
        ):
            try:
                number = int(
                    page_var.get()
                )
            except ValueError:
                return

            # Toujours lire l'ordre actuel du Livre : la structure peut
            # avoir change depuis la construction du bureau Composition.
            # Les quatre faces de couverture sont physiques mais ne
            # font jamais partie de la pagination intérieure saisie ici.
            current_order = interior_page_ids(
                self.session.book
            )

            if not (
                1
                <= number
                <= len(current_order)
            ):
                return

            self._activate_page(
                current_order[number - 1]
            )

        self._button(
            jump,
            "Aller",
            go_to_page,
            compact=True,
        ).pack(
            side="left",
            padx=(6, 0),
        )

        entry.bind(
            "<Return>",
            go_to_page,
        )

        # La quantité d'information affichée est entièrement choisie
        # par l'utilisateur, comme dans l'Explorateur Windows.
        explorer_host = tk.Frame(
            plan,
            bg=theme.PANEL,
        )
        explorer_host.pack(
            fill="both",
            expand=True,
            padx=(8, 4),
            pady=(0, 8),
        )

        if not hasattr(
            self,
            "_composition_tree_open_nodes",
        ):
            self._composition_tree_open_nodes = set()

        if not hasattr(
            self,
            "_composition_selected_page_ids",
        ):
            active_page_id = (
                self.session.active_page_id
            )
            self._composition_selected_page_ids = (
                {str(active_page_id)}
                if active_page_id is not None
                else set()
            )

        if not hasattr(
            self,
            "_composition_constraints_open",
        ):
            self._composition_constraints_open = False

        if not hasattr(
            self,
            "_composition_pages_open",
        ):
            self._composition_pages_open = False

        if not hasattr(
            self,
            "_composition_book_state_open",
        ):
            self._composition_book_state_open = True

        if not hasattr(
            self,
            "_composition_book_state_edit",
        ):
            self._composition_book_state_edit = False

        if not hasattr(
            self,
            "_composition_active_tool",
        ):
            self._composition_active_tool = "book"

        if not hasattr(self, "_composition_text_problem_index"):
            self._composition_text_problem_index = 0


        from src.gui_v4.composition_explorer import (
            CompositionExplorer,
        )

        self._composition_navigator = (
            CompositionExplorer(
                explorer_host,
                app=self,
                book=book,
            )
        )
        self._composition_navigator.pack(
            fill="both",
            expand=True,
        )

        # ======================================================
        # CENTRE + DROITE
        # ======================================================

        self._build_composition_editor(
            editor_host
        )


    def _composition_source_thumbnail(
        self,
        page,
        width=82,
        height=112,
    ):

        if not hasattr(
            self,
            "_composition_thumb_cache",
        ):
            self._composition_thumb_cache = {}

        link = getattr(
            page,
            "source",
            None,
        )

        if link is None:
            return None

        element_id = (
            getattr(
                link,
                "source_id",
                None,
            )
            or getattr(
                link,
                "source_element_id",
                None,
            )
        )

        version_id = (
            getattr(
                link,
                "source_version_id",
                None,
            )
            or getattr(
                link,
                "version_id",
                None,
            )
        )

        page_number = (
            getattr(
                link,
                "source_page",
                None,
            )
            or getattr(
                link,
                "page_number",
                None,
            )
        )

        if (
            element_id is None
            or page_number is None
        ):
            return None

        project = self.session.project

        element = (
            project.source.elements.get(
                element_id
            )
        )

        if element is None:
            return None

        version = None

        for candidate in element.versions:

            if (
                version_id is None
                or candidate.id
                == version_id
            ):
                version = candidate

                if version_id is not None:
                    break

        if version is None:
            version = (
                element.active_version
            )

        if version is None:
            return None

        source_path = Path(
            version.original_path
        )

        if (
            source_path.suffix.lower()
            != ".pdf"
        ):
            return None

        key = (
            str(source_path),
            int(page_number),
            width,
            height,
        )

        cached = (
            self._composition_thumb_cache.get(
                key
            )
        )

        if cached is not None:
            return cached

        try:
            import pymupdf

            document = pymupdf.open(
                str(source_path)
            )

            pdf_page = document.load_page(
                int(page_number) - 1
            )

            rect = pdf_page.rect

            scale = min(
                width
                / max(
                    1,
                    rect.width,
                ),
                height
                / max(
                    1,
                    rect.height,
                ),
            )

            scale = max(
                0.15,
                scale * 1.8,
            )

            pix = pdf_page.get_pixmap(
                matrix=pymupdf.Matrix(
                    scale,
                    scale,
                ),
                alpha=False,
            )

            image = Image.frombytes(
                "RGB",
                (
                    pix.width,
                    pix.height,
                ),
                pix.samples,
            )

            image.thumbnail(
                (
                    width,
                    height,
                ),
                Image.Resampling.LANCZOS,
            )

            document.close()

            photo = ImageTk.PhotoImage(
                image
            )

            self._composition_thumb_cache[
                key
            ] = photo

            return photo

        except Exception:
            return None


    def _composition_mousewheel(
        self,
        event,
    ) -> None:

        # Une action manuelle de l'utilisateur
        # interrompt immédiatement le déroulement automatique.
        self._composition_scroll_generation = (
            getattr(
                self,
                "_composition_scroll_generation",
                0,
            )
            + 1
        )

        canvas = getattr(
            self,
            "_composition_plan_canvas",
            None,
        )

        if canvas is None:
            return

        canvas.yview_scroll(
            int(
                -event.delta / 120
            ),
            "units",
        )


    def _composition_render_plan(
        self,
        focus_page_id=None,
        animate=False,
    ) -> None:
        """Rafraîchit l'Explorateur sans ouvrir ni fermer de branche."""

        book = self.session.book

        if book is None:
            return

        counter = getattr(
            self,
            "_composition_page_count_var",
            None,
        )
        if counter is not None:
            try:
                counter.set(
                    f"{len(book.page_order)} pages"
                )
            except Exception:
                pass

        navigator = getattr(
            self,
            "_composition_navigator",
            None,
        )

        if navigator is None:
            return

        navigator.book = book
        navigator.refresh(
            focus_page_id=(
                str(focus_page_id)
                if focus_page_id is not None
                else None
            )
        )


    def _composition_update_plan_selection(
        self,
    ) -> None:
        navigator = getattr(
            self,
            "_composition_navigator",
            None,
        )

        if navigator is not None:
            navigator.update_selection()


    def _composition_selected_page_ids_in_order(
        self,
        *,
        editable_only: bool = False,
    ) -> list[str]:

        book = self.session.book
        selected = set(
            getattr(
                self,
                "_composition_selected_page_ids",
                set(),
            )
        )

        result = []
        for page_id in book.page_order:
            if page_id not in selected:
                continue
            if (
                editable_only
                and is_structural_auto_page(book.pages[page_id])
            ):
                continue
            result.append(page_id)

        return result


    def _composition_plan_page_click(
        self,
        event,
        page_id: str,
    ) -> None:

        page_id = str(page_id)
        book = self.session.book
        page = book.pages.get(page_id)
        if page is None:
            return

        ctrl = bool(
            getattr(event, "state", 0) & 0x0004
        )

        selected = set(
            getattr(
                self,
                "_composition_selected_page_ids",
                set(),
            )
        )

        if not ctrl:
            selected = {page_id}
            self._composition_selected_page_ids = selected
            self._activate_page(
                page_id,
                preserve_page_selection=True,
            )
            return

        if page_id in selected:
            if len(selected) > 1:
                selected.remove(page_id)
            else:
                return
        else:
            selected.add(page_id)

        self._composition_selected_page_ids = selected

        if page_id in selected:
            self._activate_page(
                page_id,
                preserve_page_selection=True,
            )
            return

        # Si la page active vient d'être retirée de la sélection, on active
        # la dernière page sélectionnée dans l'ordre physique du Livre.
        if self.session.active_page_id not in selected:
            ordered = self._composition_selected_page_ids_in_order()
            if ordered:
                self._activate_page(
                    ordered[-1],
                    preserve_page_selection=True,
                )
                return

        self._composition_update_plan_selection()
        self._composition_update_inspector_context()

    def _composition_move_page_from_explorer(
        self,
        page_id: str,
        anchor_page_id: str,
        position: str,
    ) -> bool:
        """Déplace réellement une page depuis l'Explorateur Composition.

        Le moteur Structure reste l'unique autorité : une 2P et les pages
        automatiques AV/AP liées sont déplacées comme un bloc atomique, puis
        toutes les règles (parité, pages automatiques, compensations) sont
        recalculées dans la même transaction Undo/Redo.
        """

        if self.session is None:
            return False

        book = self.session.book
        page_id = str(page_id)
        anchor_page_id = str(anchor_page_id)
        position = str(position or "").strip().lower()

        if page_id not in book.pages or anchor_page_id not in book.pages:
            return False

        if position not in {"before", "after"}:
            return False

        source_page = book.pages[page_id]
        if is_cover_face(source_page):
            return False

        try:
            target_index = manual_page_relative_index(
                book,
                anchor_page_id,
                position=position,
            )
        except Exception as exc:
            messagebox.showerror(
                "TomeLinea",
                f"Impossible de déterminer cet emplacement.\n\n{exc}",
                parent=self,
            )
            return False

        anchor_page = book.pages[anchor_page_id]
        target_part_id = (
            None
            if is_cover_face(anchor_page)
            else anchor_page.part_id
        )

        # Évite de créer une entrée Annuler pour un dépôt qui ne change ni
        # l'ordre physique ni le classement de la page.
        try:
            source_block = atomic_block_for_page(
                book,
                page_id,
            )
            positions = [
                book.page_order.index(current_id)
                for current_id in source_block.page_ids
            ]
            source_start = min(positions)
            source_end = max(positions) + 1
            same_part = (
                target_part_id is not None
                and all(
                    book.pages[current_id].part_id == target_part_id
                    for current_id in source_block.page_ids
                )
            )
            if (
                source_start <= target_index <= source_end
                and (target_part_id is None or same_part)
            ):
                return False
        except Exception:
            # Le moteur transactionnel reste l'autorité et produira le message
            # utile si le bloc est réellement incohérent.
            pass

        def action(project):
            return move_atomic_block(
                project.book,
                page_id,
                target_index,
                target_part_id=target_part_id,
            )

        try:
            changed = bool(
                self.session.execute(
                    "Déplacer une page dans la Structure",
                    action,
                )
            )
        except Exception as exc:
            messagebox.showerror(
                "TomeLinea",
                (
                    "Ce déplacement n'est pas possible sans casser "
                    "la Structure du livre.\n\n"
                    f"{exc}"
                ),
                parent=self,
            )
            return False

        if not changed:
            return False

        # Le déplacement vient d'un geste simple : la page glissée reste la
        # page active. Si elle appartient à une 2P, le moteur a déplacé les
        # deux moitiés ensemble sans rompre leur association.
        self._composition_refresh_after_structure_change(
            {page_id},
            page_id,
        )

        # Le nouvel emplacement peut être dans une autre partie fermée. On
        # révèle donc immédiatement le chemin réel jusqu'à la page déplacée.
        self._composition_scroll_to_page(
            page_id,
            animated=False,
        )

        return True


    def _composition_scroll_to_page(
        self,
        page_id: str,
        *,
        animated: bool = False,
    ) -> None:
        navigator = getattr(
            self,
            "_composition_navigator",
            None,
        )

        if navigator is not None:
            navigator.scroll_to_page(
                str(page_id),
                expand=True,
            )


    def _composition_selected_element(
        self,
    ):
        """
        Retourne l'élément Composition actuellement sélectionné.
        """

        page = self.session.active_page

        if page is None:
            return None

        selected = list(
            getattr(
                self.session,
                "selected_element_ids",
                [],
            )
        )

        if not selected:
            return None

        selected_id = str(
            selected[0]
        )

        for element in page.content:

            if not isinstance(
                element,
                dict,
            ):
                continue

            if str(
                element.get(
                    "id",
                    "",
                )
            ) == selected_id:
                return element

        return None


    def _composition_clear_context_selection(
        self,
    ) -> None:

        self.session.clear_selection()

        self._composition_update_inspector_context()

        canvas = getattr(
            self,
            "_composition_editor_canvas",
            None,
        )

        if canvas is not None:
            self._draw_page(
                canvas
            )


    def _composition_text_value(
        self,
        element,
    ) -> str:
        """
        Retourne le contenu textuel uniquement pour calculer
        sa mise en forme. Le contenu n'est jamais modifie.
        """

        value = str(
            element.get(
                "payload",
                {},
            ).get(
                "text",
                "",
            )
        )

        # Les anciens PDF pouvaient contenir des retours
        # correspondant seulement aux lignes visuelles.
        return " ".join(
            value.split()
        )


    def _composition_text_font_path(
        self,
        element,
    ):
        """
        Trouve la police complete Windows correspondant
        aux informations typographiques de la Source.
        """

        from pathlib import Path

        spans = element.get(
            "payload",
            {},
        ).get(
            "spans",
            [],
        )

        if (
            not isinstance(
                spans,
                list,
            )
            or not spans
            or not isinstance(
                spans[0],
                dict,
            )
        ):
            return None

        raw = str(
            spans[0].get(
                "font",
                "",
            )
        )

        if "+" in raw:
            raw = raw.split(
                "+",
                1,
            )[1]

        lower = (
            raw.replace(
                " ",
                "",
            ).lower()
        )

        bold = (
            "bold" in lower
            or "semibold" in lower
            or "demibold" in lower
        )

        italic = (
            "italic" in lower
            or "oblique" in lower
        )

        if (
            bold
            and italic
        ):
            style = "BoldItalic"

        elif bold:
            style = "Bold"

        elif italic:
            style = "Italic"

        else:
            style = "Regular"

        family = None

        if "liberationsansnarrow" in lower:
            family = "LiberationSansNarrow"

        elif "liberationsans" in lower:
            family = "LiberationSans"

        elif "liberationserif" in lower:
            family = "LiberationSerif"

        elif "liberationmono" in lower:
            family = "LiberationMono"

        fonts = Path(
            r"C:\Windows\Fonts"
        )

        if family is not None:

            candidate = (
                fonts
                / (
                    family
                    + "-"
                    + style
                    + ".ttf"
                )
            )

            if candidate.is_file():
                return candidate

        # Secours : Arial complete de Windows.
        fallback = (
            fonts
            / (
                "arial"
                + (
                    "bi"
                    if bold and italic
                    else "bd"
                    if bold
                    else "i"
                    if italic
                    else ""
                )
                + ".ttf"
            )
        )

        if fallback.is_file():
            return fallback

        return None


    def _composition_text_original_size(
        self,
        element,
    ) -> float:

        spans = element.get(
            "payload",
            {},
        ).get(
            "spans",
            [],
        )

        if (
            isinstance(
                spans,
                list,
            )
            and spans
            and isinstance(
                spans[0],
                dict,
            )
        ):

            try:
                value = float(
                    spans[0].get(
                        "size",
                        10.0,
                    )
                    or 10.0
                )

                if value > 0:
                    return value

            except (
                TypeError,
                ValueError,
            ):
                pass

        return 10.0


    def _composition_text_reflow_info(
        self,
        element,
        width_mm,
    ):
        """Recompose un texte avec le moteur typographique TomeLinea.

        La mesure du texte utilise désormais Pillow/FreeType, déjà présent dans
        TomeLinea. MuPDF n'intervient plus dans le moteur de recomposition : il
        reste seulement utilisé par les anciennes fonctions de lecture/rendu PDF
        tant que leur migration juridique n'est pas terminée.
        """

        from src.v4.font_availability import match_pdf_font
        from src.v4.text_compositor import compose_text, pillow_text_metrics

        payload = element.get("payload", {})
        if not isinstance(payload, dict):
            return None

        value = str(payload.get("text", "") or "")
        if not value.strip():
            return None

        spans = payload.get("spans", [])
        if not isinstance(spans, list):
            return None

        first_span = next(
            (
                span for span in spans
                if isinstance(span, dict) and str(span.get("text", "") or "").strip()
            ),
            None,
        )
        if first_span is None:
            return None

        pdf_font = str(first_span.get("font", "") or "")
        match = match_pdf_font(pdf_font)
        if match.status != "exact" or not match.installed_path:
            return {
                "status": match.status,
                "family": match.family,
                "style": match.style,
                "pdf_font": pdf_font,
            }

        try:
            font_size = max(0.1, float(first_span.get("size", 10.0) or 10.0))
        except (TypeError, ValueError):
            font_size = 10.0

        try:
            metrics = pillow_text_metrics(str(match.installed_path), font_size)
        except Exception:
            return {
                "status": "unavailable",
                "family": match.family,
                "style": match.style,
                "pdf_font": pdf_font,
            }

        requested_width_mm = max(0.1, float(width_mm))
        width_pt = requested_width_mm * 72.0 / 25.4

        metadata = element.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}

        book = getattr(self.session, "book", None)
        book_metadata = getattr(book, "metadata", {}) if book is not None else {}
        rules = (
            book_metadata.get("text_general_rules", {})
            if isinstance(book_metadata, dict)
            else {}
        )
        if not isinstance(rules, dict):
            rules = {}

        alignment = str(
            metadata.get("text_alignment", rules.get("alignment", "justify"))
            or "justify"
        ).lower()
        hyphenation = str(rules.get("hyphenation", "controlled") or "controlled").lower()
        if hyphenation == "undecided":
            # Tant que l'utilisateur n'a pas choisi, ne jamais introduire de
            # césure nouvelle lors d'une recomposition.
            hyphenation = "forbid"

        try:
            first_line_indent_mm = max(0.0, float(rules.get("first_line_indent_mm") or 0.0))
        except (TypeError, ValueError):
            first_line_indent_mm = 0.0
        if bool(metadata.get("format_flow_continuation", False)):
            first_line_indent_mm = 0.0
        first_line_indent_pt = first_line_indent_mm * 72.0 / 25.4

        composed = compose_text(
            value,
            width=width_pt,
            measure=metrics.measure,
            alignment=alignment,
            hyphenation=hyphenation,
            min_word_length=int(rules.get("hyphen_min_word_length", 7) or 7),
            min_left=int(rules.get("hyphen_min_left", 3) or 3),
            min_right=int(rules.get("hyphen_min_right", 3) or 3),
            max_consecutive_hyphens=int(rules.get("hyphen_max_consecutive", 2) or 2),
            first_line_indent=first_line_indent_pt,
        )
        lines = [line.text for line in composed.lines] or [""]

        natural_line_height_pt = max(font_size, float(metrics.line_height_pt))
        try:
            line_pitch_mm = float(rules.get("line_pitch_mm") or 0.0)
        except (TypeError, ValueError):
            line_pitch_mm = 0.0
        natural_line_height_mm = natural_line_height_pt * 25.4 / 72.0
        line_pitch_mm = max(natural_line_height_mm, line_pitch_mm)
        try:
            paragraph_gap_mm = max(0.0, float(rules.get("paragraph_gap_mm") or 0.0))
        except (TypeError, ValueError):
            paragraph_gap_mm = 0.0
        paragraph_breaks = sum(1 for line in composed.lines[:-1] if line.paragraph_end)
        required_height_mm = (
            line_pitch_mm * len(lines)
            + paragraph_gap_mm * paragraph_breaks
            + 0.4
        )

        try:
            color_value = int(first_span.get("color", 0) or 0)
        except (TypeError, ValueError):
            color_value = 0
        color = (
            ((color_value >> 16) & 255) / 255.0,
            ((color_value >> 8) & 255) / 255.0,
            (color_value & 255) / 255.0,
        )

        return {
            "status": "exact",
            "alignment": alignment,
            "font_path": str(match.installed_path),
            "family": match.family,
            "style": match.style,
            "font_size_pt": font_size,
            "metrics": metrics,
            "composition": composed,
            "lines": lines,
            "line_height_pt": natural_line_height_pt,
            "line_pitch_mm": line_pitch_mm,
            "paragraph_gap_mm": paragraph_gap_mm,
            "first_line_indent_mm": first_line_indent_mm,
            "width_mm": requested_width_mm,
            "height_mm": required_height_mm,
            "color": color,
            "text_engine": "tomelinea.text_compositor",
            "measurement_engine": "Pillow/FreeType",
            "unicode_breaks": bool(composed.unicode_engine_available),
            "french_hyphenation": bool(composed.hyphenator_available),
        }


    def _composition_text_guardrail(
        self,
        element,
        requested_width_mm,
    ):

        info = (
            self._composition_text_reflow_info(
                element,
                requested_width_mm,
            )
        )

        if (
            not isinstance(
                info,
                dict,
            )
            or info.get(
                "status"
            ) != "exact"
        ):

            geometry = element.get(
                "geometry",
                {},
            )

            try:

                return (
                    float(
                        geometry.get(
                            "width_mm",
                            requested_width_mm,
                        )
                    ),
                    float(
                        geometry.get(
                            "height_mm",
                            1.0,
                        )
                    ),
                    1,
                )

            except (
                TypeError,
                ValueError,
            ):

                return (
                    float(
                        requested_width_mm
                    ),
                    1.0,
                    1,
                )

        return (
            float(
                info["width_mm"]
            ),
            float(
                info["height_mm"]
            ),
            len(
                info["lines"]
            ),
        )

    def _composition_apply_geometry_edit(
        self,
    ) -> None:

        page = self.session.active_page

        element = (
            self._composition_selected_element()
        )

        variables = getattr(
            self,
            "_composition_geometry_vars",
            None,
        )

        if (
            page is None
            or element is None
            or not isinstance(
                variables,
                dict,
            )
        ):
            return

        # Le texte éditorial n'a pas de géométrie à régler bloc par bloc.
        if (
            self._composition_text_uses_editorial_flow(element)
            and not self._composition_text_manual_targets_element(element)
        ):
            return

        requested = {}

        try:

            for key in (
                "x_mm",
                "y_mm",
                "width_mm",
                "height_mm",
            ):

                raw = (
                    variables[key]
                    .get()
                    .strip()
                    .replace(
                        ",",
                        ".",
                    )
                )

                requested[
                    key
                ] = float(
                    raw
                )

        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            return

        if (
            requested[
                "width_mm"
            ] <= 0
            or requested[
                "height_mm"
            ] <= 0
        ):
            return

        values = dict(
            requested
        )

        kind = str(
            element.get(
                "kind",
                "",
            )
        ).lower()

        current_geometry = (
            element.get(
                "geometry",
                {}
            )
        )

        if kind == "text":

            try:
                current_width = float(
                    current_geometry.get(
                        "width_mm",
                        requested[
                            "width_mm"
                        ],
                    )
                )

                current_height = float(
                    current_geometry.get(
                        "height_mm",
                        requested[
                            "height_mm"
                        ],
                    )
                )

            except (
                TypeError,
                ValueError,
            ):

                current_width = (
                    requested[
                        "width_mm"
                    ]
                )

                current_height = (
                    requested[
                        "height_mm"
                    ]
                )

            (
                safe_width,
                minimum_height,
                line_count,
            ) = (
                self._composition_text_guardrail(
                    element,
                    requested[
                        "width_mm"
                    ],
                )
            )

            width_changed = (
                abs(
                    requested[
                        "width_mm"
                    ]
                    - current_width
                )
                > 0.01
            )

            height_changed = (
                abs(
                    requested[
                        "height_mm"
                    ]
                    - current_height
                )
                > 0.01
            )

            values[
                "width_mm"
            ] = safe_width

            # Si l'utilisateur agit seulement sur la largeur,
            # TomeLinea recadre automatiquement la hauteur
            # au strict besoin du texte recompose.
            if (
                width_changed
                and not height_changed
            ):

                values[
                    "height_mm"
                ] = minimum_height

            else:

                # Si l'utilisateur demande aussi une hauteur,
                # on l'accepte tant qu'elle ne coupe pas le texte.
                values[
                    "height_mm"
                ] = max(
                    requested[
                        "height_mm"
                    ],
                    minimum_height,
                )

        else:

            line_count = None

        page_id = page.id

        element_id = str(
            element.get(
                "id",
                "",
            )
        )

        if not element_id:
            return

        def action(
            project,
        ):

            from src.v4.composition import (
                update_element_geometry,
            )

            book = project.book

            if book is None:
                raise RuntimeError(
                    "Livre indisponible."
                )

            result = (
                update_element_geometry(
                    book,
                    page_id,
                    element_id,
                    **values,
                )
            )

            if (
                kind == "text"
            ):

                metadata = (
                    result.setdefault(
                        "metadata",
                        {},
                    )
                )

                metadata[
                    "text_layout_mode"
                ] = "fixed_font"

                metadata[
                    "text_original_font_size_pt"
                ] = (
                    self._composition_text_original_size(
                        result
                    )
                )

                metadata[
                    "text_layout_line_count"
                ] = line_count

                metadata[
                    "text_guardrail"
                ] = True

            return result

        self.session.execute(
            "Modifier le cadre",
            action,
        )

        self.session.set_selection(
            [element_id],
            include_associated=False,
        )

        self._composition_update_inspector_context()

        canvas = getattr(
            self,
            "_composition_editor_canvas",
            None,
        )

        if canvas is not None:
            self._draw_page(
                canvas
            )

    def _composition_inspector_mousewheel(
        self,
        event,
    ) -> str:

        canvas = getattr(
            self,
            "_composition_inspector_canvas",
            None,
        )
        if canvas is None:
            return "break"

        delta = getattr(event, "delta", 0)
        if delta:
            steps = -1 if delta > 0 else 1
        else:
            steps = 0

        if steps:
            canvas.yview_scroll(steps, "units")

        return "break"


    def _composition_finalize_inspector_context(
        self,
    ) -> None:

        host = getattr(
            self,
            "_composition_inspector_context",
            None,
        )
        canvas = getattr(
            self,
            "_composition_inspector_canvas",
            None,
        )
        scrollbar = getattr(
            self,
            "_composition_inspector_scrollbar",
            None,
        )

        if host is None or canvas is None:
            return

        def bind_tree(widget):
            try:
                if not widget.winfo_exists():
                    return
                widget.bind(
                    "<MouseWheel>",
                    self._composition_inspector_mousewheel,
                )
                children = widget.winfo_children()
            except Exception:
                # Un changement de vue (notamment Undo/Redo) peut détruire
                # l'ancien inspecteur avant l'exécution de ce after_idle.
                return
            for child in children:
                bind_tree(child)

        bind_tree(host)

        try:
            host.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            bbox = canvas.bbox("all")
            content_height = (bbox[3] - bbox[1]) if bbox else 0
            visible_height = max(1, canvas.winfo_height())
            needs_scroll = content_height > visible_height + 2

            if scrollbar is not None:
                if needs_scroll and not scrollbar.winfo_ismapped():
                    scrollbar.pack(side="right", fill="y")
                elif not needs_scroll and scrollbar.winfo_ismapped():
                    scrollbar.pack_forget()
        except Exception:
            pass


    def _composition_set_inspector_tool_priority(
        self,
        active: bool,
    ) -> None:

        image_block = getattr(
            self,
            "_composition_image_quality_block",
            None,
        )
        context_shell = getattr(
            self,
            "_composition_inspector_context_shell",
            None,
        )

        if image_block is None or context_shell is None:
            return

        try:
            manager = str(image_block.winfo_manager() or "")
            if active:
                if manager:
                    image_block.pack_forget()
            elif manager != "pack":
                image_block.pack(
                    fill="x",
                    padx=18,
                    pady=(3, 5),
                    before=context_shell,
                )
        except Exception:
            pass


    def _composition_schedule_help_tooltip(
        self,
        widget,
        text: str,
    ) -> None:

        self._composition_hide_constraint_tooltip()

        def show():
            self._composition_constraint_tooltip_job = None
            if not text:
                return

            window = tk.Toplevel(self)
            window.overrideredirect(True)
            window.configure(bg=theme.WINDOW_DEEP)
            self._composition_constraint_tooltip = window

            tk.Label(
                window,
                text=text,
                bg=theme.WINDOW_DEEP,
                fg=theme.INK,
                justify="left",
                wraplength=250,
                padx=10,
                pady=7,
                font=(theme.FONT_UI, 8),
            ).pack()

            try:
                window.geometry(
                    f"+{widget.winfo_rootx() + 12}+{widget.winfo_rooty() + 22}"
                )
            except Exception:
                pass

        self._composition_constraint_tooltip_job = self.after(350, show)


    def _composition_hide_constraint_tooltip(
        self,
    ) -> None:

        job = getattr(
            self,
            "_composition_constraint_tooltip_job",
            None,
        )
        if job is not None:
            try:
                self.after_cancel(job)
            except Exception:
                pass
            self._composition_constraint_tooltip_job = None

        window = getattr(
            self,
            "_composition_constraint_tooltip",
            None,
        )
        if window is not None:
            try:
                window.destroy()
            except Exception:
                pass
            self._composition_constraint_tooltip = None


    def _composition_schedule_constraint_tooltip(
        self,
        widget,
        page_id: str,
    ) -> None:

        self._composition_hide_constraint_tooltip()

        def show():
            self._composition_constraint_tooltip_job = None
            book = self.session.book
            try:
                labels = constraint_summary(book, page_id)
            except Exception:
                labels = []
            if not labels:
                return

            window = tk.Toplevel(self)
            window.overrideredirect(True)
            window.configure(bg=theme.WINDOW_DEEP)
            self._composition_constraint_tooltip = window

            text = "Contraintes éditoriales\n" + "\n".join(
                "• " + label
                for label in labels
            )

            tk.Label(
                window,
                text=text,
                bg=theme.WINDOW_DEEP,
                fg=theme.INK,
                justify="left",
                padx=10,
                pady=7,
                font=(theme.FONT_UI, 8),
            ).pack()

            try:
                window.geometry(
                    f"+{widget.winfo_rootx() + 12}+{widget.winfo_rooty() + 18}"
                )
            except Exception:
                pass

        self._composition_constraint_tooltip_job = self.after(350, show)


    def _composition_open_constraints_from_marker(
        self,
        event,
        page_id: str,
    ) -> str:

        self._composition_hide_constraint_tooltip()
        self._composition_plan_page_click(event, page_id)
        self._composition_constraints_open = True
        self._composition_pages_open = False
        self._composition_content_open = False
        self._composition_text_flow_open = False
        self._composition_update_inspector_context()
        return "break"


    def _composition_constraint_state(
        self,
        kind: str,
        page_ids: list[str],
    ) -> int:

        if not page_ids:
            return 0

        book = self.session.book

        # Une double page est une RELATION entre deux pages, pas une simple
        # propriété répétée. Avec deux pages sélectionnées, la coche n'est
        # pleine que si ces deux UUID forment réellement la même 2P.
        if kind == DOUBLE_PAGE:
            ordered_ids = [
                page_id
                for page_id in book.page_order
                if page_id in {str(value) for value in page_ids}
            ]
            if len(ordered_ids) == 1:
                page = book.pages[ordered_ids[0]]
                return 1 if page.spread_id else 0
            if len(ordered_ids) == 2:
                left = book.pages[ordered_ids[0]]
                right = book.pages[ordered_ids[1]]
                if left.spread_id and left.spread_id == right.spread_id:
                    return 1
                if left.spread_id or right.spread_id:
                    return -1
                return 0

            values = [
                bool(book.pages[page_id].spread_id)
                for page_id in ordered_ids
            ]
            if values and all(values):
                return 1
            if not any(values):
                return 0
            return -1

        values = [
            constraint_enabled(
                book,
                page_id,
                kind,
            )
            for page_id in page_ids
        ]

        if all(values):
            return 1
        if not any(values):
            return 0
        return -1


    def _composition_refresh_after_structure_change(
        self,
        selected_page_ids,
        active_page_id,
    ) -> None:

        book = self.session.book
        selected = {
            str(page_id)
            for page_id in selected_page_ids
            if str(page_id) in book.pages
        }

        if not selected and active_page_id in book.pages:
            selected = {str(active_page_id)}

        self._composition_selected_page_ids = selected

        if active_page_id not in book.pages:
            ordered = self._composition_selected_page_ids_in_order()
            active_page_id = ordered[-1] if ordered else (book.page_order[0] if book.page_order else None)

        if active_page_id is not None:
            self.session.set_active_page(str(active_page_id))
            page = book.pages.get(str(active_page_id))
            if page is not None:
                self._composition_open_part_id = page.part_id

        count_var = getattr(self, "_composition_page_count_var", None)
        if count_var is not None:
            count_var.set(pagination_summary(book))

        status_var = getattr(self, "_composition_book_status_var", None)
        if status_var is not None:
            status_var.set(
                f"{len(book.page_order)} pages · {len(book.part_order)} parties"
            )

        self._composition_render_plan(
            focus_page_id=active_page_id,
            animate=False,
        )
        self._composition_update_editor()
        self._refresh_history_buttons()


    def _composition_constraint_checkbox_changed(
        self,
        kind: str,
        variable,
        target_page_ids,
        active_page_id: str,
    ) -> None:

        desired = int(variable.get()) == 1
        targets = [str(value) for value in target_page_ids]
        if not targets:
            return

        selected_snapshot = tuple(
            getattr(
                self,
                "_composition_selected_page_ids",
                set(targets),
            )
        )

        def action(project):
            set_constraint_on_pages(
                project.book,
                targets,
                kind,
                desired,
            )
            sync_structure_rules(project.book)
            project.touch()

        try:
            self.session.execute(
                CONSTRAINT_LABELS[kind],
                action,
            )
        except Exception as exc:
            messagebox.showwarning(
                "Contraintes éditoriales",
                str(exc),
                parent=self,
            )
            self._composition_update_inspector_context()
            return

        self._composition_refresh_after_structure_change(
            selected_snapshot,
            active_page_id,
        )


    def _composition_extend_constraint_to_similar(
        self,
        kind: str,
        active_page_id: str,
    ) -> None:

        selected_snapshot = tuple(
            getattr(
                self,
                "_composition_selected_page_ids",
                {active_page_id},
            )
        )
        result_holder = {}

        def action(project):
            result_holder.update(
                extend_constraint_to_similar(
                    project,
                    active_page_id,
                    kind,
                    threshold=SIMILARITY_THRESHOLD,
                )
            )
            sync_structure_rules(project.book)
            project.touch()

        try:
            self.session.execute(
                "Étendre la contrainte aux pages similaires",
                action,
            )
        except Exception as exc:
            messagebox.showwarning(
                "Contraintes éditoriales",
                str(exc),
                parent=self,
            )
            return

        self._composition_constraints_message = (
            f"Règle étendue à {len(result_holder.get('page_ids', []))} page(s) similaires."
        )
        self._composition_refresh_after_structure_change(
            selected_snapshot,
            active_page_id,
        )


    def _composition_remove_similarity_extension(
        self,
        extension_id: str,
        active_page_id: str,
    ) -> None:

        selected_snapshot = tuple(
            getattr(
                self,
                "_composition_selected_page_ids",
                {active_page_id},
            )
        )

        def action(project):
            remove_similarity_extension(
                project.book,
                extension_id,
            )
            sync_structure_rules(project.book)
            project.touch()

        try:
            self.session.execute(
                "Supprimer une règle étendue",
                action,
            )
        except Exception as exc:
            messagebox.showwarning(
                "Contraintes éditoriales",
                str(exc),
                parent=self,
            )
            return

        self._composition_constraints_message = "Règle étendue supprimée."
        self._composition_refresh_after_structure_change(
            selected_snapshot,
            active_page_id,
        )


    def _composition_extend_automatic_page_content(
        self,
        active_page_id: str,
    ) -> None:
        book = self.session.book
        try:
            equivalents = equivalent_automatic_page_ids(book, active_page_id)
        except Exception as exc:
            messagebox.showwarning(
                "Page automatique",
                str(exc),
                parent=self,
            )
            return

        targets = [page_id for page_id in equivalents if page_id != active_page_id]
        if not targets:
            self._composition_constraints_message = (
                "Aucune autre page automatique du même type n'est présente dans le Livre."
            )
            self._composition_update_inspector_context()
            return

        selected_snapshot = tuple(
            getattr(self, "_composition_selected_page_ids", {active_page_id})
        )
        changed_holder: list[str] = []

        def action(project):
            changed_holder.extend(
                extend_automatic_page_content(
                    project.book,
                    active_page_id,
                    equivalents,
                )
            )
            project.touch()

        try:
            self.session.execute(
                "Étendre le contenu de la page automatique",
                action,
            )
        except Exception as exc:
            messagebox.showwarning(
                "Page automatique",
                str(exc),
                parent=self,
            )
            return

        self._composition_constraints_message = (
            f"Contenu étendu à {len(changed_holder)} autre(s) page(s) automatique(s) du même type."
        )
        self._composition_refresh_after_structure_change(
            selected_snapshot,
            active_page_id,
        )


    def _composition_add_manual_page(
        self,
        position: str,
    ) -> None:

        selected = self._composition_selected_page_ids_in_order()
        if len(selected) != 1:
            messagebox.showinfo(
                "Ajouter une page",
                "Sélectionnez une seule page pour choisir l’emplacement.",
                parent=self,
            )
            return

        anchor_page_id = selected[0]

        try:
            new_page_id = self.session.execute(
                "Ajouter une page",
                lambda project: insert_manual_page_relative(
                    project.book,
                    anchor_page_id,
                    position=position,
                ).id,
            )
        except Exception as exc:
            messagebox.showerror(
                "Ajouter une page",
                str(exc),
                parent=self,
            )
            return

        # L'ajout est une action relative à la page visée : la nouvelle page
        # ne devient jamais la nouvelle cible implicite. L'utilisateur peut
        # ainsi enchaîner « ajouter avant » puis « ajouter après » autour de
        # la même page sans devoir la resélectionner.
        self._composition_selected_page_ids = {anchor_page_id}
        self.session.set_active_page(anchor_page_id)
        self._composition_constraints_open = False
        self._composition_pages_open = True
        self._composition_content_open = False
        self._composition_text_flow_open = False
        self._composition_refresh_after_structure_change(
            (anchor_page_id,),
            anchor_page_id,
        )


    def _composition_cover_selector_body_page_ids(self) -> list[str]:
        """Pages du corps disponibles pour une 2e/3e de couverture."""

        return interior_page_ids(
            self.session.book
        )


    def _composition_cover_selector_label(self, face: str) -> str:
        return (
            "2e de couverture"
            if face == INSIDE_FRONT_COVER
            else "3e de couverture"
        )


    def _composition_cover_selector_default_candidate(self, face: str) -> str | None:
        candidate_id = adjacent_inside_cover_candidate(self.session.book, face)
        if candidate_id in self.session.book.pages:
            return candidate_id

        body_ids = self._composition_cover_selector_body_page_ids()
        if not body_ids:
            return None

        return body_ids[0] if face == INSIDE_FRONT_COVER else body_ids[-1]


    def _composition_cover_selector_close(self) -> None:
        window = getattr(self, "_composition_cover_selector_window", None)
        self._composition_cover_selector_window = None
        self._composition_cover_selector_cards = {}
        self._composition_cover_selector_photos = {}
        self._composition_cover_selector_initial = False
        self._composition_cover_selector_faces = ()
        self._composition_cover_selector_candidates = {}
        self._composition_cover_selector_choices = {}

        if window is None:
            return

        try:
            window.grab_release()
        except Exception:
            pass
        try:
            window.destroy()
        except Exception:
            pass


    def _composition_cover_selector_shift_candidate(self, face: str, delta: int) -> None:
        body_ids = self._composition_cover_selector_body_page_ids()
        if not body_ids:
            return

        candidates = getattr(self, "_composition_cover_selector_candidates", {})
        current = candidates.get(face)

        if current in body_ids:
            index = body_ids.index(current)
        else:
            index = 0 if face == INSIDE_FRONT_COVER else len(body_ids) - 1

        index = max(0, min(len(body_ids) - 1, index + int(delta)))
        new_id = body_ids[index]
        if new_id == current:
            return

        candidates[face] = new_id
        self._composition_cover_selector_candidates = candidates

        # Si l'utilisateur avait choisi la page précédente, changer de page
        # annule uniquement ce choix. Le choix "blanche" reste volontairement
        # intact jusqu'à ce qu'il clique sur "Utiliser cette page".
        choices = getattr(self, "_composition_cover_selector_choices", {})
        if choices.get(face) not in {None, "__blank__"}:
            choices[face] = None
        self._composition_cover_selector_choices = choices

        self._composition_render_cover_selector_card(face)
        self._composition_cover_selector_refresh_validate_button()


    def _composition_cover_selector_choose(self, face: str, choice: str) -> None:
        choices = getattr(self, "_composition_cover_selector_choices", {})
        if choice == "__candidate__":
            choice = str(
                getattr(self, "_composition_cover_selector_candidates", {}).get(face)
                or ""
            )
            if not choice:
                return

        choices[face] = choice
        self._composition_cover_selector_choices = choices

        self._composition_render_cover_selector_card(face)
        self._composition_cover_selector_refresh_validate_button()


    def _composition_cover_selector_refresh_validate_button(self) -> None:
        button = getattr(self, "_composition_cover_selector_validate_button", None)
        if button is None:
            return

        faces = tuple(getattr(self, "_composition_cover_selector_faces", ()) or ())
        choices = getattr(self, "_composition_cover_selector_choices", {})
        ready = bool(faces) and all(choices.get(face) for face in faces)

        try:
            button.configure(state=(tk.NORMAL if ready else tk.DISABLED))
        except Exception:
            pass

        status = getattr(self, "_composition_cover_selector_status_var", None)
        if status is not None:
            missing = [
                self._composition_cover_selector_label(face)
                for face in faces
                if not choices.get(face)
            ]
            if missing:
                if len(faces) > 1:
                    status.set(
                        "Choisissez une option dans chaque colonne pour activer « Valider les couvertures »."
                    )
                else:
                    status.set("Choisissez le nouveau contenu de cette face.")
            else:
                if len(faces) > 1:
                    status.set(
                        "✓ Les deux choix sont prêts. Cliquez sur « Valider les couvertures »."
                    )
                else:
                    status.set(
                        "✓ Choix prêt. Cliquez sur « Enregistrer la modification »."
                    )


    def _composition_render_cover_selector_card(self, face: str) -> None:
        """Carte de choix : aperçu au centre, toutes les commandes en bas."""

        cards = getattr(self, "_composition_cover_selector_cards", {})
        host = cards.get(face)
        if host is None:
            return

        for child in host.winfo_children():
            child.destroy()

        label = self._composition_cover_selector_label(face)
        candidate_id = getattr(
            self,
            "_composition_cover_selector_candidates",
            {},
        ).get(face)
        candidate = self.session.book.pages.get(candidate_id) if candidate_id else None
        choice = getattr(self, "_composition_cover_selector_choices", {}).get(face)

        host.grid_columnconfigure(0, weight=1)
        host.grid_rowconfigure(2, weight=1)

        tk.Label(
            host,
            text=label.upper(),
            bg=theme.PANEL_ALT,
            fg=theme.INK,
            font=(theme.FONT_UI, 10, "bold"),
        ).grid(row=0, column=0, sticky="w", padx=14, pady=(12, 2))

        if choice == "__blank__":
            state_text = "✓ Face blanche"
            state_color = theme.ACCENT_BRIGHT
        elif choice:
            state_text = "✓ Cette page sera utilisée"
            state_color = theme.ACCENT_BRIGHT
        else:
            state_text = "À choisir"
            state_color = theme.WARNING

        tk.Label(
            host,
            text=state_text,
            bg=theme.PANEL_ALT,
            fg=state_color,
            font=(theme.FONT_UI, 8, "bold"),
        ).grid(row=1, column=0, sticky="w", padx=14, pady=(0, 5))

        # L'aperçu reste la partie centrale dominante de la carte.
        preview_area = tk.Frame(host, bg=theme.PANEL_ALT)
        preview_area.grid(row=2, column=0, sticky="nsew", padx=14, pady=(0, 5))

        preview_frame = tk.Frame(
            preview_area,
            bg=theme.WINDOW_DEEP,
            width=285,
            height=310,
            highlightthickness=1,
            highlightbackground=theme.BORDER_SOFT,
            cursor=("hand2" if candidate is not None else "arrow"),
        )
        preview_frame.pack(expand=True)
        preview_frame.pack_propagate(False)

        if candidate is not None:
            preview_frame.bind(
                "<Button-1>",
                lambda _event, current_face=face: self._composition_cover_selector_choose(
                    current_face,
                    "__candidate__",
                ),
                add="+",
            )
            photo = self._composition_source_thumbnail(
                candidate,
                width=265,
                height=290,
            )
        else:
            photo = None

        if photo is not None:
            photos = getattr(self, "_composition_cover_selector_photos", {})
            photos[face] = photo
            self._composition_cover_selector_photos = photos
            image_label = tk.Label(
                preview_frame,
                image=photo,
                bg=theme.WINDOW_DEEP,
                bd=0,
                cursor="hand2",
            )
            image_label.pack(expand=True)
            image_label.bind(
                "<Button-1>",
                lambda _event, current_face=face: self._composition_cover_selector_choose(
                    current_face,
                    "__candidate__",
                ),
                add="+",
            )
        else:
            page_canvas = tk.Canvas(
                preview_frame,
                width=255,
                height=288,
                bg=theme.WINDOW_DEEP,
                bd=0,
                highlightthickness=0,
            )
            page_canvas.pack(expand=True)
            page_canvas.create_rectangle(
                24, 10, 231, 278,
                fill=theme.PAGE,
                outline=theme.PAGE_BORDER,
            )
            page_canvas.create_text(
                127,
                144,
                text=(
                    str(getattr(candidate, "title", "") or getattr(candidate, "page_type", "") or "Page")
                    if candidate is not None
                    else "Aucune page disponible"
                ),
                fill="#626262",
                width=180,
                justify="center",
                font=(theme.FONT_UI, 9),
            )

        body_ids = self._composition_cover_selector_body_page_ids()
        candidate_index = (
            body_ids.index(candidate_id)
            if candidate_id in body_ids
            else None
        )

        if candidate is not None and candidate_index is not None:
            page_name = str(candidate.title or candidate.page_type or "Page")
            candidate_text = f"Page du corps {candidate_index + 1}/{len(body_ids)} · {page_name}"
        else:
            candidate_text = "Aucune page du corps disponible"

        tk.Label(
            host,
            text=candidate_text,
            bg=theme.PANEL_ALT,
            fg=theme.MUTED,
            wraplength=390,
            justify="center",
            font=(theme.FONT_UI, 8),
        ).grid(row=3, column=0, sticky="ew", padx=12, pady=(0, 5))

        # Toutes les commandes de cette face sont regroupées en bas.
        commands = tk.Frame(host, bg=theme.PANEL_ALT)
        commands.grid(row=4, column=0, sticky="ew", padx=14, pady=(0, 10))

        nav = tk.Frame(commands, bg=theme.PANEL_ALT)
        nav.pack(fill="x", pady=(0, 5))

        prev_enabled = candidate_index is not None and candidate_index > 0
        next_enabled = (
            candidate_index is not None
            and candidate_index < len(body_ids) - 1
        )

        self._button(
            nav,
            "← Page précédente",
            lambda current_face=face: self._composition_cover_selector_shift_candidate(
                current_face, -1,
            ),
            compact=True,
            enabled=prev_enabled,
        ).pack(side="left", fill="x", expand=True, padx=(0, 3))

        self._button(
            nav,
            "Page suivante →",
            lambda current_face=face: self._composition_cover_selector_shift_candidate(
                current_face, 1,
            ),
            compact=True,
            enabled=next_enabled,
        ).pack(side="left", fill="x", expand=True, padx=(3, 0))

        use_button = self._button(
            commands,
            (
                f"✓ Utiliser cette page comme {label}"
                if choice and choice != "__blank__"
                else f"Utiliser cette page comme {label}"
            ),
            lambda current_face=face: self._composition_cover_selector_choose(
                current_face, "__candidate__",
            ),
            accent=bool(choice and choice != "__blank__"),
            compact=True,
            enabled=candidate is not None,
        )
        use_button.pack(fill="x", pady=(0, 4))

        blank_button = self._button(
            commands,
            (
                f"✓ Laisser la {label} blanche"
                if choice == "__blank__"
                else f"Laisser la {label} blanche"
            ),
            lambda current_face=face: self._composition_cover_selector_choose(
                current_face, "__blank__",
            ),
            accent=(choice == "__blank__"),
            compact=True,
        )
        blank_button.pack(fill="x")


    def _composition_cover_selector_validate(self) -> None:
        faces = tuple(getattr(self, "_composition_cover_selector_faces", ()) or ())
        choices = dict(getattr(self, "_composition_cover_selector_choices", {}) or {})
        if not faces or any(not choices.get(face) for face in faces):
            return

        used_pages = [
            str(choices[face])
            for face in faces
            if choices.get(face) not in {None, "__blank__"}
        ]
        if len(used_pages) != len(set(used_pages)):
            messagebox.showwarning(
                "Couvertures",
                "Une même page ne peut pas être utilisée à la fois comme 2e et 3e de couverture.",
                parent=getattr(self, "_composition_cover_selector_window", self),
            )
            return

        initial = bool(getattr(self, "_composition_cover_selector_initial", False))
        active_before = str(self.session.active_page_id or "")

        def action(project):
            for face in faces:
                choice = choices[face]
                if choice == "__blank__":
                    blank_inside_cover(project.book, face)
                else:
                    assign_page_as_inside_cover(
                        project.book,
                        face,
                        str(choice),
                    )
            project.touch()

        label = (
            "Définir les couvertures intérieures"
            if len(faces) > 1
            else f"Modifier la {self._composition_cover_selector_label(faces[0])}"
        )
        try:
            self.session.execute(label, action)
        except Exception as exc:
            messagebox.showwarning(
                "Couvertures",
                str(exc),
                parent=getattr(self, "_composition_cover_selector_window", self),
            )
            return

        project = self.session.project
        if initial and not inside_cover_confirmation_issues(self.session.book):
            project.metadata["inside_cover_initial_review_required"] = False
            project.metadata["inside_cover_initial_review_completed"] = True
            project.touch()

        self._composition_cover_selector_close()

        if active_before in self.session.book.pages:
            next_active = active_before
        else:
            body_ids = self._composition_cover_selector_body_page_ids()
            next_active = body_ids[0] if body_ids else None

        selected = (next_active,) if next_active else ()
        self._composition_selected_page_ids = set(selected)
        if next_active:
            self.session.set_active_page(next_active)

        self._composition_refresh_after_structure_change(
            selected,
            next_active,
        )

        if initial and not bool(project.metadata.get("book_import_state_reviewed", False)):
            self._composition_book_state_open = True
            self._composition_pages_open = False
            self._composition_active_tool = "book"
            self._composition_refresh_tool_tabs()
            self._composition_update_inspector_context()


    def _composition_open_cover_selector(
        self,
        *,
        faces: tuple[str, ...] | list[str] | None = None,
        initial: bool = False,
    ) -> bool:
        """Ouvre le sélecteur compact des 2e/3e de couverture."""

        if str(getattr(self, "current_workspace", "")) != "composition":
            return False

        existing = getattr(self, "_composition_cover_selector_window", None)
        if existing is not None:
            try:
                if existing.winfo_exists():
                    existing.lift()
                    existing.focus_force()
                    return True
            except Exception:
                pass

        if faces is None:
            pending = {
                str(issue.get("face", "") or "")
                for issue in inside_cover_confirmation_issues(self.session.book)
            }
            faces = tuple(
                face
                for face in (INSIDE_FRONT_COVER, INSIDE_BACK_COVER)
                if face in pending
            )

        faces = tuple(
            face
            for face in (faces or ())
            if face in {INSIDE_FRONT_COVER, INSIDE_BACK_COVER}
        )
        if not faces:
            return False

        window = tk.Toplevel(self)
        self._composition_cover_selector_window = window
        self._composition_cover_selector_initial = bool(initial)
        self._composition_cover_selector_faces = faces
        self._composition_cover_selector_cards = {}
        self._composition_cover_selector_photos = {}
        self._composition_cover_selector_candidates = {
            face: self._composition_cover_selector_default_candidate(face)
            for face in faces
        }
        self._composition_cover_selector_choices = {
            face: None
            for face in faces
        }

        window.title("Couvertures")
        window.configure(bg=theme.PANEL)

        # La décision repose sur le contenu réel des pages. Le sélecteur est
        # donc une vraie fenêtre de travail, grande mais non modale : elle peut
        # être déplacée ou réduite pendant que l'utilisateur parcourt le Plan
        # derrière pour vérifier une page ou ouvrir une partie.
        width = 980 if len(faces) > 1 else 560
        height = 700
        window.geometry(f"{width}x{height}")
        window.minsize(width, height)
        window.resizable(True, True)

        # Surtout pas de grab_set()/transient ici : cela bloquait le bureau et
        # empêchait d'ouvrir une partie pour contrôler la candidate de 3e.
        if initial:
            window.protocol("WM_DELETE_WINDOW", lambda: None)
        else:
            window.protocol("WM_DELETE_WINDOW", self._composition_cover_selector_close)

        window.grid_columnconfigure(0, weight=1)
        window.grid_rowconfigure(1, weight=1)

        header = tk.Frame(window, bg=theme.PANEL)
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(16, 9))

        tk.Label(
            header,
            text=(
                "Définir les couvertures intérieures"
                if len(faces) > 1
                else f"Modifier la {self._composition_cover_selector_label(faces[0])}"
            ),
            bg=theme.PANEL,
            fg=theme.INK,
            font=(theme.FONT_UI, 13, "bold"),
        ).pack(anchor="w")

        tk.Label(
            header,
            text=(
                "Choisissez une option pour chaque face, puis validez."
                if len(faces) > 1
                else "Choisissez le contenu de cette face."
            ),
            bg=theme.PANEL,
            fg=theme.MUTED,
            justify="left",
            font=(theme.FONT_UI, 9),
        ).pack(anchor="w", pady=(3, 0))

        cards_host = tk.Frame(window, bg=theme.PANEL)
        cards_host.grid(row=1, column=0, sticky="nsew", padx=16, pady=(0, 8))
        cards_host.grid_rowconfigure(0, weight=1)

        for index, face in enumerate(faces):
            card = tk.Frame(
                cards_host,
                bg=theme.PANEL_ALT,
                highlightthickness=1,
                highlightbackground=theme.BORDER_SOFT,
                width=455,
            )
            card.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=(0 if index == 0 else 6, 6 if index == 0 else 0),
            )
            cards_host.grid_columnconfigure(index, weight=1)
            self._composition_cover_selector_cards[face] = card
            self._composition_render_cover_selector_card(face)

        # Le pied de fenêtre est une ligne fixe de la grille. Il ne peut plus
        # être repoussé hors écran par la hauteur demandée des aperçus.
        footer = tk.Frame(
            window,
            bg=theme.WINDOW_DEEP,
            highlightthickness=1,
            highlightbackground=theme.BORDER_SOFT,
        )
        footer.grid(row=2, column=0, sticky="ew", padx=14, pady=(0, 12))

        # État conservé pour la logique, mais aucun texte explicatif permanent
        # n'occupe le pied : le bouton de validation est l'unique commande finale.
        self._composition_cover_selector_status_var = tk.StringVar(value="")

        if not initial:
            self._button(
                footer,
                "Annuler",
                self._composition_cover_selector_close,
                compact=True,
            ).pack(side="right", padx=(7, 12), pady=9)

        self._composition_cover_selector_validate_button = self._button(
            footer,
            (
                "Valider les couvertures"
                if len(faces) > 1
                else "Enregistrer la modification"
            ),
            self._composition_cover_selector_validate,
            accent=True,
            enabled=False,
            compact=False,
        )
        self._composition_cover_selector_validate_button.pack(
            side="right",
            padx=(12, 0),
            pady=9,
        )

        self._composition_cover_selector_refresh_validate_button()

        try:
            window.update_idletasks()
            x = self.winfo_rootx() + max(20, (self.winfo_width() - width) // 2)
            y = self.winfo_rooty() + max(20, (self.winfo_height() - height) // 2)
            window.geometry(f"{width}x{height}+{x}+{y}")
        except Exception:
            pass

        try:
            window.lift()
            window.focus_force()
        except Exception:
            pass

        return True


    def _composition_pending_inside_cover_face(self) -> str | None:
        """Première décision 2e/3e encore attendue, dans l'ordre physique."""

        issues = inside_cover_confirmation_issues(self.session.book)
        faces = {str(issue.get("face", "") or "") for issue in issues}
        if INSIDE_FRONT_COVER in faces:
            return INSIDE_FRONT_COVER
        if INSIDE_BACK_COVER in faces:
            return INSIDE_BACK_COVER
        return None


    def _composition_cover_review_label(self, face: str) -> str:
        return (
            "2e de couverture"
            if face == INSIDE_FRONT_COVER
            else "3e de couverture"
        )


    def _composition_cover_review_candidate_id(self, face: str) -> str | None:
        """Page actuellement affichée et utilisable comme face intérieure."""

        page_id = str(self.session.active_page_id or "")
        page = self.session.book.pages.get(page_id)
        if page is None or is_cover_face(page):
            return None

        if bool(getattr(self, "_composition_cover_manual_pick", False)):
            origin_id = str(getattr(self, "_composition_cover_manual_pick_origin_id", "") or "")
            if origin_id and page_id == origin_id:
                return None

        return page_id


    def _composition_render_initial_cover_review_banner(self) -> None:
        banner = getattr(self, "_composition_cover_review_banner", None)
        canvas = getattr(self, "_composition_editor_canvas", None)
        if banner is None:
            return

        for child in banner.winfo_children():
            child.destroy()

        active = bool(getattr(self, "_composition_cover_review_active", False))
        face = getattr(self, "_composition_cover_review_face", None)
        pending_face = self._composition_pending_inside_cover_face()

        if not active or face not in {INSIDE_FRONT_COVER, INSIDE_BACK_COVER}:
            try:
                banner.pack_forget()
            except Exception:
                pass
            return

        # En validation initiale, si la face courante a déjà été tranchée,
        # on passe automatiquement à la suivante.
        if bool(getattr(self, "_composition_cover_review_initial", False)):
            if pending_face is None:
                try:
                    banner.pack_forget()
                except Exception:
                    pass
                return
            if face != pending_face:
                face = pending_face
                self._composition_cover_review_face = face

        try:
            if not banner.winfo_manager():
                kwargs = dict(fill="x", padx=34, pady=(0, 8))
                if canvas is not None:
                    kwargs["before"] = canvas
                banner.pack(**kwargs)
        except Exception:
            pass

        label = self._composition_cover_review_label(face)
        manual_pick = bool(getattr(self, "_composition_cover_manual_pick", False))
        candidate_id = self._composition_cover_review_candidate_id(face)
        candidate = self.session.book.pages.get(candidate_id) if candidate_id else None

        top = tk.Frame(banner, bg=theme.PANEL_ALT)
        top.pack(fill="x", padx=12, pady=(8, 2))

        initial_review = bool(getattr(self, "_composition_cover_review_initial", False))
        heading = (
            f"{label.upper()} À DÉFINIR"
            if initial_review
            else f"MODIFIER LA {label.upper()}"
        )
        tk.Label(
            top,
            text=heading,
            bg=theme.PANEL_ALT,
            fg=theme.WARNING,
            font=(theme.FONT_UI, 9, "bold"),
        ).pack(side="left")

        if initial_review:
            tk.Label(
                top,
                text="CHOIX INITIAL",
                bg=theme.PANEL_ALT,
                fg=theme.MUTED,
                font=(theme.FONT_UI, 7, "bold"),
            ).pack(side="right")

        if manual_pick:
            if candidate is None:
                message = (
                    f"Cliquez dans le Plan sur la page à utiliser comme {label}. "
                    "Son contenu s'affichera ici avant toute validation."
                )
            else:
                page_name = str(candidate.title or candidate.page_type or "Page choisie")
                message = (
                    f"Page choisie : {page_name}. Vérifiez son contenu au centre, "
                    f"puis confirmez si elle doit devenir la {label}."
                )
        else:
            edge = (
                "première page du corps"
                if face == INSIDE_FRONT_COVER
                else "dernière page du corps"
            )
            if initial_review:
                message = (
                    f"TomeLinea affiche la {edge}. "
                    f"Décidez maintenant si elle devient la {label}."
                )
            else:
                message = (
                    f"TomeLinea affiche la {edge}. Vous pouvez l'utiliser comme nouvelle {label}, "
                    "laisser cette face blanche ou choisir une autre page."
                )

        tk.Label(
            banner,
            text=message,
            bg=theme.PANEL_ALT,
            fg=theme.INK,
            justify="left",
            anchor="w",
            wraplength=720,
            font=(theme.FONT_UI, 9),
        ).pack(fill="x", padx=12, pady=(0, 7))

        actions = tk.Frame(banner, bg=theme.PANEL_ALT)
        actions.pack(fill="x", padx=12, pady=(0, 7))

        use_label = f"Utiliser cette page comme {label}"
        self._button(
            actions,
            use_label,
            lambda current_face=face: self._composition_confirm_displayed_inside_cover(current_face),
            accent=True,
            enabled=candidate is not None,
            compact=True,
        ).pack(side="left", padx=(0, 8))

        blank_label = f"Laisser la {label} blanche"
        self._button(
            actions,
            blank_label,
            lambda current_face=face: self._composition_blank_inside_cover(current_face),
            compact=True,
        ).pack(side="left")

        lower = tk.Frame(banner, bg=theme.PANEL_ALT)
        lower.pack(fill="x", padx=12, pady=(0, 8))

        if manual_pick:
            alt_text = "Revenir à la page proposée"
            alt_command = lambda current_face=face: self._composition_show_default_inside_cover_candidate(current_face)
        else:
            alt_text = "Choisir une autre page"
            alt_command = lambda current_face=face: self._composition_choose_other_inside_cover_page(current_face)

        tk.Button(
            lower,
            text=alt_text,
            command=alt_command,
            bg=theme.PANEL_ALT,
            fg=theme.MUTED,
            activebackground=theme.PANEL_SOFT,
            activeforeground=theme.INK,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(theme.FONT_UI, 8, "bold"),
        ).pack(side="left")

        if not initial_review:
            tk.Button(
                lower,
                text="Annuler la modification",
                command=self._composition_cancel_inside_cover_edit,
                bg=theme.PANEL_ALT,
                fg=theme.MUTED_DARK,
                activebackground=theme.PANEL_SOFT,
                activeforeground=theme.INK,
                relief="flat",
                bd=0,
                cursor="hand2",
                font=(theme.FONT_UI, 8),
            ).pack(side="right")


    def _composition_show_cover_review_page(self, page_id: str) -> None:
        page_id = str(page_id or "")
        if page_id not in self.session.book.pages:
            return

        page = self.session.book.pages[page_id]
        self._composition_open_part_id = getattr(page, "part_id", None)
        self._composition_selected_page_ids = {page_id}
        self.session.set_active_page(page_id)
        self._composition_book_state_open = False
        self._composition_constraints_open = False
        self._composition_pages_open = True
        self._composition_active_tool = "pages"
        self._composition_render_plan(focus_page_id=page_id, animate=False)
        self._composition_update_editor()
        self._composition_refresh_tool_tabs()


    def _composition_begin_initial_cover_review_if_needed(
        self,
    ) -> bool:
        """Signale les couvertures intérieures sans imposer de fenêtre."""

        if (
            str(
                getattr(
                    self,
                    "current_workspace",
                    "",
                )
            )
            != "composition"
        ):
            return False

        issues = (
            inside_cover_confirmation_issues(
                self.session.book
            )
        )

        pending = {
            str(
                issue.get(
                    "face",
                    "",
                )
                or ""
            )
            for issue in issues
        }

        project = self.session.project

        if not pending:
            project.metadata[
                "inside_cover_initial_review_required"
            ] = False
            project.metadata[
                "inside_cover_initial_review_completed"
            ] = True
            project.touch()
            return False

        # Décision disponible dans l'onglet Pages,
        # jamais imposée à l'ouverture du Livre.
        project.metadata[
            "inside_cover_initial_review_required"
        ] = True
        project.metadata[
            "inside_cover_initial_review_completed"
        ] = False
        project.touch()

        return False

    def _composition_begin_inside_cover_edit(self, face: str) -> None:
        """Réouvre le même sélecteur pour modifier une 2e/3e plus tard."""

        if face not in {INSIDE_FRONT_COVER, INSIDE_BACK_COVER}:
            return
        self._composition_open_cover_selector(
            faces=(face,),
            initial=False,
        )

    def _composition_cancel_inside_cover_edit(self) -> None:
        self._composition_cover_selector_close()

    def _composition_choose_other_inside_cover_page(self, face: str) -> None:
        if face not in {INSIDE_FRONT_COVER, INSIDE_BACK_COVER}:
            return
        self._composition_cover_review_face = face
        self._composition_cover_review_active = True
        self._composition_cover_manual_pick = True
        self._composition_cover_manual_pick_origin_id = str(self.session.active_page_id or "")
        self._composition_render_initial_cover_review_banner()


    def _composition_show_default_inside_cover_candidate(self, face: str) -> None:
        self._composition_cover_manual_pick = False
        self._composition_cover_manual_pick_origin_id = None
        candidate_id = adjacent_inside_cover_candidate(self.session.book, face)
        if candidate_id is not None:
            self._composition_show_cover_review_page(candidate_id)
        else:
            self._composition_render_initial_cover_review_banner()


    def _composition_confirm_displayed_inside_cover(self, face: str) -> None:
        candidate_id = self._composition_cover_review_candidate_id(face)
        if candidate_id is None:
            messagebox.showinfo(
                "Couverture",
                "Affichez d'abord une page du corps du livre.",
                parent=self,
            )
            return

        result: dict[str, str] = {}

        def action(project):
            result["page_id"] = assign_page_as_inside_cover(
                project.book,
                face,
                candidate_id,
            )
            project.touch()

        label = f"Définir la {self._composition_cover_review_label(face)}"
        try:
            self.session.execute(label, action)
        except Exception as exc:
            messagebox.showwarning("Couverture", str(exc), parent=self)
            return

        page_id = result.get("page_id")
        if page_id and page_id in self.session.book.pages:
            self._composition_refresh_after_structure_change((page_id,), page_id)
        self._composition_cover_manual_pick = False
        self._composition_cover_manual_pick_origin_id = None

        if bool(getattr(self, "_composition_cover_review_initial", False)):
            self.after_idle(self._composition_begin_initial_cover_review_if_needed)
        else:
            self._composition_cover_review_active = False
            self._composition_cover_review_face = None
            self._composition_render_initial_cover_review_banner()


    def _composition_focus_inside_cover_candidate(
        self,
        face: str,
    ) -> None:

        candidate_id = adjacent_inside_cover_candidate(
            self.session.book,
            face,
        )
        if not candidate_id or candidate_id not in self.session.book.pages:
            return

        candidate = self.session.book.pages[candidate_id]
        self._composition_open_part_id = getattr(
            candidate,
            "part_id",
            None,
        )
        self._composition_selected_page_ids = {candidate_id}
        self.session.set_active_page(candidate_id)
        self._composition_activate_tool("pages")
        self._composition_render_plan()
        self._composition_update_editor()
        self._composition_update_inspector_context()



    def _composition_use_adjacent_as_inside_cover(
        self,
        face: str,
    ) -> None:

        result: dict[str, str] = {}

        def action(project):
            result["page_id"] = use_adjacent_page_as_inside_cover(
                project.book,
                face,
            )
            project.touch()

        label = (
            "Définir la 2e de couverture"
            if face == INSIDE_FRONT_COVER
            else "Définir la 3e de couverture"
        )

        try:
            self.session.execute(label, action)
        except Exception as exc:
            messagebox.showwarning(
                "Couverture",
                str(exc),
                parent=self,
            )
            return

        page_id = result.get("page_id")
        if not page_id or page_id not in self.session.book.pages:
            return

        self._composition_selected_page_ids = {page_id}
        self.session.set_active_page(page_id)
        self._composition_pages_open = True
        self._composition_refresh_after_structure_change(
            (page_id,),
            page_id,
        )

        if bool(getattr(self, "_composition_cover_review_initial", False)):
            self.after_idle(self._composition_begin_initial_cover_review_if_needed)


    def _composition_blank_inside_cover(
        self,
        face: str,
    ) -> None:

        current_page_id = str(self.session.active_page_id or "")
        result: dict[str, str] = {}

        def action(project):
            result["page_id"] = blank_inside_cover(
                project.book,
                face,
            )
            project.touch()

        label = (
            "Remettre la 2e de couverture en blanc"
            if face == INSIDE_FRONT_COVER
            else "Remettre la 3e de couverture en blanc"
        )

        try:
            self.session.execute(label, action)
        except Exception as exc:
            messagebox.showwarning(
                "Couverture",
                str(exc),
                parent=self,
            )
            return

        page_id = result.get("page_id")
        if not page_id or page_id not in self.session.book.pages:
            return

        # Quand la décision est prise depuis la page candidate visible, on
        # laisse l'utilisateur exactement là où il travaillait.
        focus_id = (
            current_page_id
            if current_page_id in self.session.book.pages
            else page_id
        )
        self._composition_selected_page_ids = {focus_id}
        self.session.set_active_page(focus_id)
        self._composition_pages_open = True
        self._composition_refresh_after_structure_change(
            (focus_id,),
            focus_id,
        )

        self._composition_cover_manual_pick = False
        self._composition_cover_manual_pick_origin_id = None
        if bool(getattr(self, "_composition_cover_review_initial", False)):
            self.after_idle(self._composition_begin_initial_cover_review_if_needed)
        elif bool(getattr(self, "_composition_cover_review_active", False)):
            self._composition_cover_review_active = False
            self._composition_cover_review_face = None
            self._composition_render_initial_cover_review_banner()


    def _composition_delete_pages(self) -> None:

        targets = self._composition_selected_page_ids_in_order()
        if not targets:
            return

        book = self.session.book
        auto_targets = [
            page_id
            for page_id in targets
            if is_structural_auto_page(book.pages[page_id])
        ]
        if auto_targets:
            messagebox.showinfo(
                "Supprimer une page",
                (
                    "Une page automatique rose dépend d’une décision éditoriale.\n\n"
                    "Retirez la contrainte qui la crée plutôt que de supprimer la page directement."
                ),
                parent=self,
            )
            return

        selected_indexes = [book.page_order.index(page_id) for page_id in targets]
        fallback_index = min(selected_indexes)
        active_before = str(self.session.active_page_id or "")

        has_content = any(bool(book.pages[page_id].content) for page_id in targets)
        has_source = any(book.pages[page_id].source is not None for page_id in targets)
        has_spread = any(bool(book.pages[page_id].spread_id) for page_id in targets)
        has_constraints = False
        for page_id in targets:
            try:
                if active_constraint_kinds(book, page_id):
                    has_constraints = True
                    break
            except Exception:
                pass

        is_free_manual_blank = (
            len(targets) == 1
            and bool(book.pages[targets[0]].metadata.get("manual_editorial_page"))
            and not has_content
            and not has_spread
            and not has_constraints
        )

        if not is_free_manual_blank:
            lines = [
                (
                    "Supprimer cette page du Livre ?"
                    if len(targets) == 1
                    else f"Supprimer les {len(targets)} pages sélectionnées du Livre ?"
                )
            ]
            details = []
            if has_content:
                details.append("Du contenu est présent sur la sélection.")
            if has_spread:
                details.append("La double page concernée sera dissociée.")
            if has_constraints:
                details.append("Les autres pages seront réajustées automatiquement.")
            if has_source:
                details.append("La Source originale restera conservée.")
            if details:
                lines.append("")
                lines.extend(details)

            if not messagebox.askyesno(
                "Supprimer",
                "\n".join(lines),
                parent=self,
            ):
                return

        try:
            self.session.execute(
                (
                    "Supprimer une page"
                    if len(targets) == 1
                    else "Supprimer des pages"
                ),
                lambda project: delete_selected_pages(project.book, targets),
            )
        except Exception as exc:
            messagebox.showerror(
                "Supprimer",
                str(exc),
                parent=self,
            )
            return

        book = self.session.book
        if active_before in book.pages:
            next_active = active_before
        elif book.page_order:
            next_active = book.page_order[min(fallback_index, len(book.page_order) - 1)]
        else:
            next_active = None

        selected_after = (str(next_active),) if next_active is not None else ()
        self._composition_selected_page_ids = set(selected_after)
        self._composition_constraints_open = False
        self._composition_pages_open = bool(next_active)
        self._composition_content_open = False
        self._composition_text_flow_open = False
        self._composition_refresh_after_structure_change(
            selected_after,
            next_active,
        )


    def _composition_mark_book_state_reviewed(self) -> None:
        """Valide uniquement l'état général du format du Livre.

        Les décisions concernant des pages particulières (notamment 2e/3e de
        couverture) restent indépendantes et sont traitées depuis Pages.
        """
        project = self.session.project
        project.metadata["book_import_state_reviewed"] = True
        project.touch()
        self._composition_book_state_open = False
        self._composition_book_state_edit = False
        self._composition_active_tool = "layout"
        self._composition_update_inspector_context()


    def _composition_show_import_exception(self, source_page: int) -> None:
        try:
            number = int(source_page)
        except (TypeError, ValueError):
            return
        for page_id in self.session.book.page_order:
            page = self.session.book.pages[page_id]
            source = page.source
            if source is not None and source.source_page == number:
                self._composition_selected_page_ids = {page_id}
                self.session.clear_selection()
                self.session.set_active_page(page_id)
                self._composition_book_state_open = True
                self._composition_text_flow_open = False
                self._composition_book_state_edit = False
                self._composition_refresh_plan_selection()
                self._draw_page(self._composition_canvas)
                self._composition_update_inspector_context()
                return


    def _composition_apply_format_change(
        self,
        format_key,
    ) -> None:
        """Convertit tout le Livre vers un format standard du catalogue."""

        selected_key = str(
            format_key.get()
            if hasattr(format_key, "get")
            else format_key
        ).strip()
        standard_format = STANDARD_FORMATS_BY_KEY.get(selected_key)
        if standard_format is None:
            messagebox.showerror(
                "TomeLinea V4",
                "Choisissez un format éditorial dans le catalogue.",
                parent=self,
            )
            return

        book_before = self.session.book
        fmt_before = book_before.format
        active_before = self.session.active_page_id
        try:
            active_index_before = (
                book_before.page_order.index(active_before)
                if active_before in book_before.page_order
                else 0
            )
        except Exception:
            active_index_before = 0

        wait_controller = None
        try:
            width = float(standard_format.width_mm)
            height = float(standard_format.height_mm)

            if (
                abs(float(fmt_before.width_mm) - width) <= 0.05
                and abs(float(fmt_before.height_mm) - height) <= 0.05
            ):
                self.session.project.metadata["book_import_state_reviewed"] = True
                self.session.project.touch()
                self._composition_update_inspector_context()
                return

            try:
                from src.gui_v4.startup_runtime import start_wait_animation_async

                wait_controller = start_wait_animation_async()
                self.update_idletasks()
            except Exception:
                wait_controller = None

            def action(project):
                book = project.book
                current = book.format
                reflow_result = apply_book_layout_settings(
                    project,
                    width_mm=width,
                    height_mm=height,
                    margin_top_mm=float(current.margin_top_mm),
                    margin_bottom_mm=float(current.margin_bottom_mm),
                    margin_inside_mm=float(current.margin_inside_mm),
                    margin_outside_mm=float(current.margin_outside_mm),
                    bleed_mm=max(
                        float(current.bleed_top_mm),
                        float(current.bleed_right_mm),
                        float(current.bleed_bottom_mm),
                        float(current.bleed_left_mm),
                    ),
                    composition_extent=str(
                        book.metadata.get("composition_extent", "margins")
                        or "margins"
                    ),
                )
                sync_result = sync_structure_rules(project.book)
                project.book.metadata["format_catalog_key"] = standard_format.key
                project.book.metadata["format_catalog_label"] = standard_format.label
                project.book.metadata["format_platforms"] = list(
                    standard_format.platforms
                )
                project.book.metadata["format_reflow_final_page_count"] = (
                    interior_page_count(project.book)
                )
                return reflow_result, sync_result

            self.session.execute(
                f"Format du Livre : {standard_format.label}",
                action,
            )

        except Exception as exc:
            if wait_controller is not None:
                try:
                    wait_controller.finish_after_cycle(
                        pump=self.update_idletasks,
                    )
                except Exception:
                    pass
            messagebox.showerror(
                "TomeLinea V4",
                str(exc),
                parent=self,
            )
            return

        book = self.session.book
        if active_before in book.pages:
            active_after = active_before
        elif book.page_order:
            active_after = book.page_order[
                min(active_index_before, len(book.page_order) - 1)
            ]
        else:
            active_after = None

        selected_after = (str(active_after),) if active_after is not None else ()
        self._composition_selected_page_ids = set(selected_after)
        self._composition_book_state_open = True

        self._composition_refresh_after_structure_change(
            selected_after,
            active_after,
        )
        self._refresh_history_buttons()
        try:
            self.update_idletasks()
        except Exception:
            pass

        if wait_controller is not None:
            try:
                wait_controller.finish_after_cycle(
                    pump=self.update_idletasks,
                )
            except Exception:
                pass


    def _composition_open_format_chooser(self) -> None:
        """Catalogue compact : formats courants visibles, familles pour le reste."""

        existing = getattr(self, "_composition_format_chooser", None)
        if existing is not None:
            try:
                if existing.winfo_exists():
                    existing.lift()
                    existing.focus_force()
                    return
            except Exception:
                pass

        book = self.session.book
        fmt = book.format
        current = find_standard_format(
            float(fmt.width_mm),
            float(fmt.height_mm),
        ) or nearest_standard_format(
            float(fmt.width_mm),
            float(fmt.height_mm),
        )

        window = tk.Toplevel(self)
        self._composition_format_chooser = window
        window.configure(bg=theme.WINDOW_DEEP)
        window.transient(self)
        # La fenêtre a son propre bandeau sombre : on supprime le bandeau Windows
        # qui faisait doublon et cassait l'esthétique TomeLinea.
        try:
            window.overrideredirect(True)
        except Exception:
            pass
        window.geometry("680x520")
        window.resizable(False, False)

        try:
            self.update_idletasks()
            px = self.winfo_rootx() + max(0, (self.winfo_width() - 680) // 2)
            py = self.winfo_rooty() + max(0, (self.winfo_height() - 520) // 2)
            window.geometry(f"680x520+{px}+{py}")
        except Exception:
            pass

        def close():
            try:
                try:
                    window.grab_release()
                except Exception:
                    pass
                window.destroy()
            finally:
                self._composition_format_chooser = None

        header = tk.Frame(window, bg=theme.WINDOW_DEEP)
        header.pack(fill="x", padx=14, pady=(10, 7))
        title = tk.Label(
            header,
            text="Choisir un format",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(theme.FONT_UI, 13, "bold"),
            anchor="w",
        )
        title.pack(side="left", fill="x", expand=True)
        close_button = tk.Button(
            header,
            text="✕",
            command=close,
            bg=theme.WINDOW_DEEP,
            fg=theme.MUTED,
            activebackground=theme.WINDOW_DEEP,
            activeforeground=theme.WHITE,
            relief="flat",
            bd=0,
            font=(theme.FONT_UI, 11),
            cursor="hand2",
        )
        close_button.pack(side="right")

        # Le bandeau peut servir de poignée de déplacement malgré overrideredirect.
        drag = {"x": 0, "y": 0}
        def drag_start(event):
            drag["x"] = int(event.x_root - window.winfo_x())
            drag["y"] = int(event.y_root - window.winfo_y())
        def drag_move(event):
            window.geometry(f"+{int(event.x_root-drag['x'])}+{int(event.y_root-drag['y'])}")
        for widget in (header, title):
            widget.bind("<ButtonPress-1>", drag_start, add="+")
            widget.bind("<B1-Motion>", drag_move, add="+")

        body = tk.Frame(window, bg=theme.WINDOW_DEEP)
        body.pack(fill="both", expand=True, padx=14, pady=(0, 8))
        body.grid_columnconfigure(1, weight=1)
        body.grid_rowconfigure(1, weight=1)

        selected_key = tk.StringVar(value=current.key)
        family_groups = formats_by_ui_family()
        family_buttons = {}

        quick_keys = (
            "a5_148x210",
            "a4_210x297",
            "coollibri_a5_landscape",
            "a4_landscape",
        )
        quick = tk.Frame(body, bg=theme.PANEL_SOFT)
        quick.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        tk.Label(
            quick,
            text="Formats courants",
            bg=theme.PANEL_SOFT,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 8, "bold"),
        ).pack(side="left", padx=(10, 8), pady=7)

        families = tk.Frame(body, bg=theme.PANEL_ALT, width=175)
        families.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        families.grid_propagate(False)
        formats_host = tk.Frame(body, bg=theme.PANEL)
        formats_host.grid(row=1, column=1, sticky="nsew")

        def clear_host():
            for child in formats_host.winfo_children():
                child.destroy()

        def show_family(family_name: str) -> None:
            for name, button in family_buttons.items():
                button.configure(
                    bg=(theme.ACCENT_DARK if name == family_name else theme.PANEL_ALT),
                    fg=(theme.WHITE if name == family_name else theme.INK),
                )

            clear_host()
            tk.Label(
                formats_host,
                text=family_name,
                bg=theme.PANEL,
                fg=theme.INK,
                font=(theme.FONT_UI, 11, "bold"),
                anchor="w",
            ).pack(fill="x", padx=12, pady=(10, 6))

            items = dict(family_groups).get(family_name, ())
            # Les formats ISO familiers apparaissent en tête de leur famille.
            items = tuple(sorted(items, key=lambda item: (
                0 if item.key in quick_keys else 1,
                item.width_mm * item.height_mm,
                item.label,
            )))
            list_shell = tk.Frame(formats_host, bg=theme.PANEL)
            list_shell.pack(fill="both", expand=True, padx=10)
            listbox = tk.Listbox(
                list_shell,
                bg=theme.PANEL_SOFT,
                fg=theme.INK,
                selectbackground=theme.ACCENT_DARK,
                selectforeground=theme.WHITE,
                activestyle="none",
                relief="flat",
                bd=0,
                highlightthickness=0,
                exportselection=False,
                font=(theme.FONT_UI, 10),
            )
            keys = []
            for index, item in enumerate(items):
                keys.append(item.key)
                listbox.insert("end", item.display_label)
                if item.key in quick_keys:
                    try:
                        listbox.itemconfig(index, foreground=theme.ACCENT_BRIGHT)
                    except Exception:
                        pass
                if item.key == selected_key.get():
                    listbox.selection_set(index)
                    listbox.activate(index)
                    listbox.see(index)
            scrollbar = TLScrollbar(list_shell, orient="vertical", command=listbox.yview)
            listbox.configure(yscrollcommand=scrollbar.set)
            listbox.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y", padx=(4, 0))

            summary = tk.Frame(formats_host, bg=theme.PANEL_SOFT)
            summary.pack(fill="x", padx=10, pady=(8, 2))
            title_var = tk.StringVar()
            platforms_var = tk.StringVar()
            tk.Label(
                summary, textvariable=title_var, bg=theme.PANEL_SOFT,
                fg=theme.ACCENT_BRIGHT, font=(theme.FONT_UI, 9, "bold"), anchor="w",
            ).pack(fill="x", padx=9, pady=(6, 1))
            tk.Label(
                summary, textvariable=platforms_var, bg=theme.PANEL_SOFT,
                fg=theme.MUTED, font=(theme.FONT_UI, 8), anchor="w",
                justify="left", wraplength=420,
            ).pack(fill="x", padx=9, pady=(0, 6))

            def update_summary():
                item = STANDARD_FORMATS_BY_KEY.get(selected_key.get())
                if item is None:
                    title_var.set(""); platforms_var.set(""); return
                title_var.set(item.display_label)
                platforms = " · ".join(item.platforms) if item.platforms else "Catalogue TomeLinea"
                platforms_var.set(f"Compatible : {platforms}")

            def choose(_event=None):
                selection = listbox.curselection()
                if not selection:
                    return
                idx = int(selection[0])
                if 0 <= idx < len(keys):
                    selected_key.set(keys[idx])
                    update_summary()

            listbox.bind("<<ListboxSelect>>", choose, add="+")
            update_summary()

        for family_name, _items in family_groups:
            button = tk.Button(
                families,
                text=family_name,
                command=lambda name=family_name: show_family(name),
                bg=theme.PANEL_ALT, fg=theme.INK,
                activebackground=theme.ACCENT_DARK, activeforeground=theme.WHITE,
                relief="flat", bd=0, padx=9, pady=7, anchor="w",
                font=(theme.FONT_UI, 9, "bold"), cursor="hand2",
            )
            button.pack(fill="x", padx=5, pady=1)
            family_buttons[family_name] = button

        def pick_quick(key: str):
            item = STANDARD_FORMATS_BY_KEY.get(key)
            if item is None:
                return
            selected_key.set(key)
            show_family(ui_family_for_format(item))

        quick_labels = (
            ("A5", "a5_148x210"),
            ("A4", "a4_210x297"),
            ("A5 paysage", "coollibri_a5_landscape"),
            ("A4 paysage", "a4_landscape"),
        )
        for label, key in quick_labels:
            tk.Button(
                quick, text=label, command=lambda k=key: pick_quick(k),
                bg=theme.WINDOW_DEEP, fg=theme.ACCENT_BRIGHT,
                activebackground=theme.ACCENT_DARK, activeforeground=theme.WHITE,
                relief="flat", bd=0, padx=9, pady=4,
                font=(theme.FONT_UI, 8, "bold"), cursor="hand2",
            ).pack(side="left", padx=2, pady=5)

        footer = tk.Frame(window, bg=theme.WINDOW_DEEP)
        footer.pack(fill="x", padx=14, pady=(0, 12))
        self._button(footer, "Retour", close, compact=True).pack(side="left")

        def apply_choice():
            key = selected_key.get()
            close()
            self._composition_apply_format_change(key)

        self._button(footer, "Appliquer", apply_choice, compact=True, accent=True).pack(side="right")

        show_family(ui_family_for_format(current))

        # La fenêtre de choix est réellement active dès son apparition :
        # le premier clic de l'utilisateur doit agir, pas seulement donner
        # le focus à une fenêtre overrideredirect sous Windows.
        try:
            window.update_idletasks()
            window.lift()
            window.grab_set()
            window.focus_force()
            window.attributes("-topmost", True)
            def release_topmost():
                try:
                    if window.winfo_exists():
                        window.attributes("-topmost", False)
                except Exception:
                    pass
            window.after(120, release_topmost)
        except Exception:
            pass

    def _composition_render_book_state_panel(self, host) -> None:
        """Format : format physique et marges générales du Livre.

        Les autres anciens "réglages généraux" restent conservés dans le
        modèle mais ne sont plus exposés ici : le fond perdu sera redistribué
        vers Images et l'étendue sera traitée au niveau des éléments.
        """

        project = self.session.project
        book = self.session.book
        state = detect_book_import_state(project)
        fmt = book.format

        width_mm = float(fmt.width_mm)
        height_mm = float(fmt.height_mm)
        current_standard = find_standard_format(width_mm, height_mm)
        current_dims = f"{width_mm:.1f} × {height_mm:.1f} mm"
        current_value = (
            f"{current_standard.label} · {current_dims}"
            if current_standard is not None
            else f"{current_dims} · hors catalogue"
        )

        if state.source_width_mm is not None and state.source_height_mm is not None:
            source_item = find_standard_format(
                state.source_width_mm,
                state.source_height_mm,
            )
            source_dims = (
                f"{float(state.source_width_mm):.1f} × "
                f"{float(state.source_height_mm):.1f} mm"
            )
            source_value = (
                f"{source_item.label} · {source_dims}"
                if source_item is not None
                else f"{source_dims} · format source libre"
            )
        else:
            source_value = "Indisponible"

        def card(title: str, value: str, *, accent: bool = False):
            box = tk.Frame(host, bg=theme.PANEL_SOFT)
            box.pack(fill="x", padx=12, pady=(6, 0))
            tk.Label(
                box,
                text=title,
                bg=theme.PANEL_SOFT,
                fg=theme.MUTED,
                font=(theme.FONT_UI, 8, "bold"),
                anchor="w",
            ).pack(fill="x", padx=9, pady=(7, 2))
            tk.Label(
                box,
                text=value,
                bg=theme.PANEL_SOFT,
                fg=(theme.ACCENT_BRIGHT if accent else theme.INK),
                font=(theme.FONT_UI, 9, "bold"),
                anchor="w",
                justify="left",
                wraplength=215,
            ).pack(fill="x", padx=9, pady=(0, 7))

        card("Format source", source_value, accent="libre" in source_value)
        card("Format du livre", current_value, accent=current_standard is None)

        self._button(
            host,
            "Changer le format",
            self._composition_open_format_chooser,
            compact=True,
            accent=True,
        ).pack(fill="x", padx=12, pady=(10, 6))

        # Les marges concernent tout le Livre au même titre que le format :
        # elles vivent donc dans le même onglet.
        tk.Frame(host, bg=theme.PAGE_BORDER, height=1).pack(
            fill="x", padx=12, pady=(10, 6)
        )
        tk.Label(
            host, text="Marges générales", bg=theme.PANEL, fg=theme.INK,
            font=(theme.FONT_UI, 9, "bold"), anchor="w",
        ).pack(fill="x", padx=18, pady=(0, 4))

        margin_vars = {
            "top": tk.StringVar(value=f"{float(fmt.margin_top_mm):g}"),
            "bottom": tk.StringVar(value=f"{float(fmt.margin_bottom_mm):g}"),
            "inside": tk.StringVar(value=f"{float(fmt.margin_inside_mm):g}"),
            "outside": tk.StringVar(value=f"{float(fmt.margin_outside_mm):g}"),
        }

        for key, label in (
            ("top", "Haut"),
            ("bottom", "Bas"),
            ("inside", "Intérieure"),
            ("outside", "Extérieure"),
        ):
            row = tk.Frame(host, bg=theme.PANEL)
            row.pack(fill="x", padx=18, pady=2)
            tk.Label(
                row, text=label, bg=theme.PANEL, fg=theme.INK,
                font=(theme.FONT_UI, 9), anchor="w",
            ).pack(side="left", fill="x", expand=True)
            tk.Label(
                row, text="mm", bg=theme.PANEL, fg=theme.MUTED,
                font=(theme.FONT_UI, 8),
            ).pack(side="right", padx=(5, 0))
            tk.Entry(
                row, textvariable=margin_vars[key], width=7, justify="right",
                bg=theme.PANEL_SOFT, fg=theme.INK, insertbackground=theme.INK,
                relief="flat", font=(theme.FONT_UI, 9),
            ).pack(side="right", ipady=3)

        margin_guides_var = tk.BooleanVar(
            value=bool(getattr(self, "_composition_margin_guides_visible", True))
        )
        display_row = tk.Frame(host, bg=theme.PANEL)
        display_row.pack(fill="x", padx=18, pady=(5, 0))
        indicator = tk.Button(
            display_row, text="", width=2, bg=theme.PANEL_SOFT,
            fg=theme.ACCENT_BRIGHT, activebackground=theme.PANEL_SOFT,
            activeforeground=theme.INK, relief="solid", bd=1,
            padx=0, pady=0, font=(theme.FONT_UI, 9, "bold"), cursor="hand2",
        )
        indicator.pack(side="left", padx=(0, 6))
        display_label = tk.Button(
            display_row, text="Afficher les marges", anchor="w",
            bg=theme.PANEL, fg=theme.INK, activebackground=theme.PANEL,
            activeforeground=theme.INK, relief="flat", bd=0,
            font=(theme.FONT_UI, 9), cursor="hand2",
        )
        display_label.pack(side="left", fill="x", expand=True)

        def refresh_margin_visibility():
            selected = bool(margin_guides_var.get())
            indicator.configure(
                text=("✓" if selected else ""),
                bg=(theme.ACCENT_DARK if selected else theme.PANEL_SOFT),
                fg=(theme.WHITE if selected else theme.ACCENT_BRIGHT),
            )

        def toggle_margin_visibility():
            margin_guides_var.set(not bool(margin_guides_var.get()))
            self._composition_margin_guides_visible = bool(margin_guides_var.get())
            refresh_margin_visibility()
            canvas = getattr(self, "_composition_editor_canvas", None)
            if canvas is not None:
                self._draw_page(canvas)

        indicator.configure(command=toggle_margin_visibility)
        display_label.configure(command=toggle_margin_visibility)
        refresh_margin_visibility()

        def apply_margins():
            try:
                values = {
                    key: float(var.get().strip().replace(",", "."))
                    for key, var in margin_vars.items()
                }
            except Exception:
                messagebox.showerror(
                    "Format",
                    "Saisissez quatre valeurs numériques en millimètres.",
                    parent=self,
                )
                return
            self._composition_apply_general_settings(
                margin_top_mm=values["top"],
                margin_bottom_mm=values["bottom"],
                margin_inside_mm=values["inside"],
                margin_outside_mm=values["outside"],
            )

        self._button(
            host, "Appliquer les marges", apply_margins,
            compact=True, accent=True,
        ).pack(fill="x", padx=18, pady=(10, 6))

    def _composition_apply_general_settings(
        self,
        *,
        margin_top_mm: float | None = None,
        margin_bottom_mm: float | None = None,
        margin_inside_mm: float | None = None,
        margin_outside_mm: float | None = None,
        bleed_mm: float | None = None,
        composition_extent: str | None = None,
    ) -> bool:
        """Applique uniquement les réglages géométriques généraux du Livre."""

        book_before = self.session.book
        fmt = book_before.format
        if find_standard_format(float(fmt.width_mm), float(fmt.height_mm)) is None:
            messagebox.showinfo(
                "Format",
                "Choisissez d'abord un format standard avant de modifier les marges.",
                parent=self,
            )
            return False

        top = float(fmt.margin_top_mm if margin_top_mm is None else margin_top_mm)
        bottom = float(fmt.margin_bottom_mm if margin_bottom_mm is None else margin_bottom_mm)
        inside = float(fmt.margin_inside_mm if margin_inside_mm is None else margin_inside_mm)
        outside = float(fmt.margin_outside_mm if margin_outside_mm is None else margin_outside_mm)
        current_bleed = max(
            float(fmt.bleed_top_mm),
            float(fmt.bleed_right_mm),
            float(fmt.bleed_bottom_mm),
            float(fmt.bleed_left_mm),
        )
        bleed = current_bleed if bleed_mm is None else float(bleed_mm)
        extent = str(
            composition_extent
            if composition_extent is not None
            else book_before.metadata.get("composition_extent", "margins")
            or "margins"
        )

        if min(top, bottom, inside, outside, bleed) < 0:
            messagebox.showerror(
                "Format",
                "Les valeurs ne peuvent pas être négatives.",
                parent=self,
            )
            return False
        if inside + outside >= float(fmt.width_mm) or top + bottom >= float(fmt.height_mm):
            messagebox.showerror(
                "Format",
                "Les marges ne laissent aucune zone de composition utilisable.",
                parent=self,
            )
            return False
        if extent not in {"margins", "page", "bleed"}:
            return False

        active_before = self.session.active_page_id
        try:
            active_index_before = (
                book_before.page_order.index(active_before)
                if active_before in book_before.page_order
                else 0
            )
        except Exception:
            active_index_before = 0

        margins_changed = any((
            abs(top - float(fmt.margin_top_mm)) > 0.01,
            abs(bottom - float(fmt.margin_bottom_mm)) > 0.01,
            abs(inside - float(fmt.margin_inside_mm)) > 0.01,
            abs(outside - float(fmt.margin_outside_mm)) > 0.01,
        ))

        wait_controller = None
        try:
            if margins_changed:
                try:
                    from src.gui_v4.startup_runtime import start_wait_animation_async
                    wait_controller = start_wait_animation_async()
                    self.update_idletasks()
                except Exception:
                    wait_controller = None

                def action(project):
                    result = apply_book_layout_settings(
                        project,
                        width_mm=float(project.book.format.width_mm),
                        height_mm=float(project.book.format.height_mm),
                        margin_top_mm=top,
                        margin_bottom_mm=bottom,
                        margin_inside_mm=inside,
                        margin_outside_mm=outside,
                        bleed_mm=bleed,
                        composition_extent=extent,
                    )
                    sync_structure_rules(project.book)
                    return result
            else:
                def action(project):
                    current = project.book.format
                    current.bleed_top_mm = bleed
                    current.bleed_right_mm = bleed
                    current.bleed_bottom_mm = bleed
                    current.bleed_left_mm = bleed
                    current.validate()
                    project.book.metadata["composition_extent"] = extent
                    project.book.history.append({
                        "action": "reglages_generaux_livre_modifies",
                        "bleed_mm": bleed,
                        "composition_extent": extent,
                    })
                    project.touch()
                    project.validate()
                    return None

            self.session.execute("Réglages généraux du Livre", action)
        except Exception as exc:
            if wait_controller is not None:
                try:
                    wait_controller.finish_after_cycle(pump=self.update_idletasks)
                except Exception:
                    pass
            messagebox.showerror(
                "Réglages généraux",
                str(exc),
                parent=self,
            )
            return False

        book = self.session.book
        if active_before in book.pages:
            active_after = active_before
        elif book.page_order:
            active_after = book.page_order[min(active_index_before, len(book.page_order)-1)]
        else:
            active_after = None

        selected_after = (str(active_after),) if active_after else ()
        self._composition_selected_page_ids = set(selected_after)
        self._composition_refresh_after_structure_change(selected_after, active_after)
        self._refresh_history_buttons()

        if wait_controller is not None:
            try:
                wait_controller.finish_after_cycle(pump=self.update_idletasks)
            except Exception:
                pass
        return True


    def _composition_render_general_settings_panel(self, host) -> None:
        """Une seule vue : marges, fond perdu, étendue, un seul Appliquer."""

        fmt = self.session.book.format
        current_extent = str(
            self.session.book.metadata.get("composition_extent", "margins")
            or "margins"
        )
        current_bleed = max(
            float(fmt.bleed_top_mm),
            float(fmt.bleed_right_mm),
            float(fmt.bleed_bottom_mm),
            float(fmt.bleed_left_mm),
        )

        margin_vars = {
            "top": tk.StringVar(value=f"{float(fmt.margin_top_mm):g}"),
            "bottom": tk.StringVar(value=f"{float(fmt.margin_bottom_mm):g}"),
            "inside": tk.StringVar(value=f"{float(fmt.margin_inside_mm):g}"),
            "outside": tk.StringVar(value=f"{float(fmt.margin_outside_mm):g}"),
        }
        bleed_var = tk.DoubleVar(
            value=min((0.0, 3.0, 5.0), key=lambda v: abs(v-current_bleed))
        )
        extent_var = tk.StringVar(value=current_extent)

        def section(title: str):
            tk.Label(
                host, text=title, bg=theme.PANEL, fg=theme.INK,
                font=(theme.FONT_UI, 9, "bold"), anchor="w",
            ).pack(fill="x", padx=18, pady=(10, 4))

        def divider():
            tk.Frame(host, bg=theme.PAGE_BORDER, height=1).pack(
                fill="x", padx=18, pady=(9, 0)
            )

        def square_choice(parent, text, variable, value, group):
            row = tk.Frame(parent, bg=theme.PANEL)
            row.pack(fill="x", pady=1)
            indicator = tk.Button(
                row, text="", width=2, bg=theme.PANEL_SOFT,
                fg=theme.ACCENT_BRIGHT, activebackground=theme.PANEL_SOFT,
                activeforeground=theme.INK, relief="solid", bd=1,
                padx=0, pady=0, font=(theme.FONT_UI, 9, "bold"), cursor="hand2",
            )
            indicator.pack(side="left", padx=(0, 6))
            label = tk.Button(
                row, text=text, anchor="w", bg=theme.PANEL, fg=theme.INK,
                activebackground=theme.PANEL, activeforeground=theme.INK,
                relief="flat", bd=0, font=(theme.FONT_UI, 9), cursor="hand2",
            )
            label.pack(side="left", fill="x", expand=True)
            group.append((indicator, variable, value))
            def choose():
                variable.set(value)
                refresh_group(group)
            indicator.configure(command=choose)
            label.configure(command=choose)
            return row

        def refresh_group(group):
            for indicator, variable, value in group:
                selected = variable.get() == value
                indicator.configure(
                    text=("✓" if selected else ""),
                    bg=(theme.ACCENT_DARK if selected else theme.PANEL_SOFT),
                    fg=(theme.WHITE if selected else theme.ACCENT_BRIGHT),
                )

        def square_toggle(parent, text: str, variable, command):
            row = tk.Frame(parent, bg=theme.PANEL)
            row.pack(fill="x", pady=1)
            indicator = tk.Button(
                row, text="", width=2, bg=theme.PANEL_SOFT,
                fg=theme.ACCENT_BRIGHT, activebackground=theme.PANEL_SOFT,
                activeforeground=theme.INK, relief="solid", bd=1,
                padx=0, pady=0, font=(theme.FONT_UI, 9, "bold"), cursor="hand2",
            )
            indicator.pack(side="left", padx=(0, 6))
            label = tk.Button(
                row, text=text, anchor="w", bg=theme.PANEL, fg=theme.INK,
                activebackground=theme.PANEL, activeforeground=theme.INK,
                relief="flat", bd=0, font=(theme.FONT_UI, 9), cursor="hand2",
            )
            label.pack(side="left", fill="x", expand=True)

            def refresh():
                selected = bool(variable.get())
                indicator.configure(
                    text=("✓" if selected else ""),
                    bg=(theme.ACCENT_DARK if selected else theme.PANEL_SOFT),
                    fg=(theme.WHITE if selected else theme.ACCENT_BRIGHT),
                )

            def toggle():
                variable.set(not bool(variable.get()))
                refresh()
                command(bool(variable.get()))

            indicator.configure(command=toggle)
            label.configure(command=toggle)
            refresh()
            return row

        margin_guides_var = tk.BooleanVar(
            value=bool(getattr(self, "_composition_margin_guides_visible", True))
        )
        bleed_guides_var = tk.BooleanVar(
            value=bool(getattr(self, "_composition_bleed_guides_visible", True))
        )

        def set_margin_guides(visible: bool):
            self._composition_margin_guides_visible = bool(visible)
            canvas = getattr(self, "_composition_editor_canvas", None)
            if canvas is not None:
                self._draw_page(canvas)

        def set_bleed_guides(visible: bool):
            self._composition_bleed_guides_visible = bool(visible)
            canvas = getattr(self, "_composition_editor_canvas", None)
            if canvas is not None:
                self._draw_page(canvas)

        # 1. Marges
        section("Marges")
        for key, label in (
            ("top", "Haut"),
            ("bottom", "Bas"),
            ("inside", "Intérieure"),
            ("outside", "Extérieure"),
        ):
            row = tk.Frame(host, bg=theme.PANEL)
            row.pack(fill="x", padx=18, pady=2)
            tk.Label(
                row, text=label, bg=theme.PANEL, fg=theme.INK,
                font=(theme.FONT_UI, 9), anchor="w",
            ).pack(side="left", fill="x", expand=True)
            tk.Label(
                row, text="mm", bg=theme.PANEL, fg=theme.MUTED,
                font=(theme.FONT_UI, 8),
            ).pack(side="right", padx=(5, 0))
            tk.Entry(
                row, textvariable=margin_vars[key], width=7, justify="right",
                bg=theme.PANEL_SOFT, fg=theme.INK, insertbackground=theme.INK,
                relief="flat", font=(theme.FONT_UI, 9),
            ).pack(side="right", ipady=3)

        margin_display = tk.Frame(host, bg=theme.PANEL)
        margin_display.pack(fill="x", padx=18, pady=(4, 0))
        square_toggle(
            margin_display, "Afficher les marges",
            margin_guides_var, set_margin_guides,
        )

        # 2. Fond perdu
        divider(); section("Fond perdu")
        bleed_group = []
        bleed_box = tk.Frame(host, bg=theme.PANEL)
        bleed_box.pack(fill="x", padx=18)
        for value, label in ((0.0, "Aucun"), (3.0, "3 mm"), (5.0, "5 mm")):
            square_choice(bleed_box, label, bleed_var, value, bleed_group)
        refresh_group(bleed_group)
        square_toggle(
            bleed_box, "Afficher le fond perdu",
            bleed_guides_var, set_bleed_guides,
        )

        # 3. Étendue
        divider(); section("Étendue")
        extent_group = []
        extent_box = tk.Frame(host, bg=theme.PANEL)
        extent_box.pack(fill="x", padx=18)
        for value, label in (
            ("margins", "Dans les marges"),
            ("page", "Jusqu’au bord de la page"),
            ("bleed", "Jusqu’au fond perdu"),
        ):
            square_choice(extent_box, label, extent_var, value, extent_group)
        refresh_group(extent_group)

        def apply_all():
            try:
                values = {
                    key: float(var.get().strip().replace(",", "."))
                    for key, var in margin_vars.items()
                }
            except Exception:
                messagebox.showerror(
                    "Réglages généraux",
                    "Saisissez quatre valeurs numériques en millimètres.",
                    parent=self,
                )
                return
            self._composition_apply_general_settings(
                margin_top_mm=values["top"],
                margin_bottom_mm=values["bottom"],
                margin_inside_mm=values["inside"],
                margin_outside_mm=values["outside"],
                bleed_mm=float(bleed_var.get()),
                composition_extent=extent_var.get(),
            )

        self._button(
            host, "Appliquer", apply_all, compact=True, accent=True,
        ).pack(fill="x", padx=18, pady=(14, 6))

    def _composition_render_pages_panel(
        self,
        host,
        selected_page_ids,
        active_page_id: str,
    ) -> None:
        """Gestion corrective des pages, sans outils de création superflus."""

        header = tk.Frame(
            host,
            bg=theme.PANEL,
        )
        header.pack(
            fill="x",
            padx=18,
            pady=(8, 6),
        )

        tk.Label(
            header,
            text="PAGES",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                9,
                "bold",
            ),
        ).pack(
            side="left"
        )

        book = self.session.book
        single = (
            len(selected_page_ids)
            == 1
        )

        selected_cover_face = None
        selected_cover_page = None

        if (
            single
            and selected_page_ids[0]
            in book.pages
        ):
            selected_cover_page = (
                book.pages[
                    selected_page_ids[0]
                ]
            )
            selected_cover_face = (
                cover_face(
                    selected_cover_page
                )
            )

        # Couvertures : choix manuel seulement lorsque l'utilisateur
        # vient volontairement sur la 2e ou la 3e.
        if (
            selected_cover_face
            in {
                INSIDE_FRONT_COVER,
                INSIDE_BACK_COVER,
            }
            and selected_cover_page
            is not None
        ):
            current_label = (
                "2e de couverture"
                if (
                    selected_cover_face
                    == INSIDE_FRONT_COVER
                )
                else "3e de couverture"
            )

            pending = (
                is_inside_cover_pending(
                    selected_cover_page
                )
            )

            tk.Label(
                host,
                text=(
                    f"{current_label}"
                    + (
                        " · à confirmer"
                        if pending
                        else ""
                    )
                ),
                bg=theme.PANEL,
                fg=(
                    theme.ACCENT_BRIGHT
                    if pending
                    else theme.INK
                ),
                wraplength=210,
                justify="left",
                font=(
                    theme.FONT_UI,
                    9,
                    "bold",
                ),
            ).pack(
                anchor="w",
                padx=18,
                pady=(2, 6),
            )

            self._button(
                host,
                (
                    f"Définir la {current_label}"
                    if pending
                    else f"Modifier la {current_label}"
                ),
                lambda face=selected_cover_face:
                self._composition_begin_inside_cover_edit(
                    face
                ),
                compact=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(0, 9),
            )

        has_structural_auto = any(
            page_id in book.pages
            and is_structural_auto_page(
                book.pages[page_id]
            )
            for page_id in selected_page_ids
        )

        has_cover_face = any(
            page_id in book.pages
            and is_cover_face(
                book.pages[page_id]
            )
            for page_id in selected_page_ids
        )

        # Supprimer reste une correction utile. Les commandes
        # "Ajouter une page" sont retirées de l'interface normale.
        delete_text = (
            "Supprimer cette page"
            if len(selected_page_ids) <= 1
            else (
                "Supprimer les "
                f"{len(selected_page_ids)} "
                "pages sélectionnées"
            )
        )

        self._button(
            host,
            delete_text,
            self._composition_delete_pages,
            compact=True,
            enabled=(
                bool(selected_page_ids)
                and not has_structural_auto
                and not has_cover_face
            ),
        ).pack(
            fill="x",
            padx=18,
            pady=(4, 6),
        )

        if has_cover_face:
            tk.Label(
                host,
                text=(
                    "Les quatre faces de couverture "
                    "restent protégées."
                ),
                bg=theme.PANEL,
                fg=theme.MUTED,
                wraplength=210,
                justify="left",
                font=(
                    theme.FONT_UI,
                    8,
                ),
            ).pack(
                anchor="w",
                padx=18,
                pady=(2, 0),
            )

        if has_structural_auto:
            tk.Label(
                host,
                text=(
                    "Page automatique : sa gestion "
                    "reste liée à la contrainte qui l'a créée."
                ),
                bg=theme.PANEL,
                fg="#E7A3B0",
                wraplength=210,
                justify="left",
                font=(
                    theme.FONT_UI,
                    8,
                    "bold",
                ),
            ).pack(
                anchor="w",
                padx=18,
                pady=(2, 0),
            )

    def _composition_set_position_constraint(
        self,
        page_ids: list[str],
        active_page_id: str,
        position: str,
    ) -> None:
        targets = [str(value) for value in page_ids]
        if not targets:
            return
        position = str(position or "free")
        selected_snapshot = tuple(targets)

        def action(project):
            book = project.book
            if position == "right":
                set_constraint_on_pages(book, targets, PAGE_LEFT, False)
                set_constraint_on_pages(book, targets, PAGE_RIGHT, True)
            elif position == "left":
                set_constraint_on_pages(book, targets, PAGE_RIGHT, False)
                set_constraint_on_pages(book, targets, PAGE_LEFT, True)
            else:
                set_constraint_on_pages(book, targets, PAGE_RIGHT, False)
                set_constraint_on_pages(book, targets, PAGE_LEFT, False)
            sync_structure_rules(book)
            project.touch()

        try:
            self.session.execute("Position éditoriale", action)
        except Exception as exc:
            messagebox.showwarning("Contraintes éditoriales", str(exc), parent=self)
            self._composition_update_inspector_context()
            return
        self._composition_refresh_after_structure_change(selected_snapshot, active_page_id)


    def _composition_extend_active_constraints_to_similar(
        self,
        active_page_id: str,
    ) -> None:
        book = self.session.book
        kinds = [
            kind
            for kind in active_constraint_kinds(book, active_page_id)
            if kind != DOUBLE_PAGE
        ]
        if not kinds:
            self._composition_constraints_message = (
                "Choisissez d’abord une règle à étendre."
            )
            self._composition_update_inspector_context()
            return

        selected_snapshot = tuple(
            getattr(self, "_composition_selected_page_ids", {active_page_id})
        )
        result_holder = []

        def action(project):
            for kind in kinds:
                result_holder.append(
                    extend_constraint_to_similar(
                        project,
                        active_page_id,
                        kind,
                        threshold=SIMILARITY_THRESHOLD,
                    )
                )
            sync_structure_rules(project.book)
            project.touch()

        try:
            self.session.execute("Étendre aux pages similaires", action)
        except Exception as exc:
            messagebox.showwarning("Contraintes éditoriales", str(exc), parent=self)
            return

        total = max(
            [len(result.get("page_ids", ())) for result in result_holder]
            or [0]
        )
        self._composition_constraints_message = (
            f"Règle étendue à {total} page{'s' if total != 1 else ''}."
        )
        self._composition_refresh_after_structure_change(selected_snapshot, active_page_id)


    def _composition_toggle_constraints_similar_extension(
        self,
        active_page_id: str,
    ) -> None:
        """Coche/décoche l'extension automatique des règles aux pages similaires."""

        book = self.session.book
        active_page_id = str(active_page_id)
        if active_page_id not in book.pages:
            return
        active_kinds = [
            kind for kind in active_constraint_kinds(book, active_page_id)
            if kind != DOUBLE_PAGE
        ]
        if not active_kinds:
            self._composition_constraints_message = "Choisissez d’abord une règle à étendre."
            self._composition_update_inspector_context()
            return

        anchored = [
            item for item in extension_memberships(book, active_page_id)
            if (
                str(item.get("anchor_page_id") or "") == active_page_id
                and str(item.get("kind") or "") in active_kinds
            )
        ]
        selected_snapshot = tuple(
            getattr(self, "_composition_selected_page_ids", {active_page_id})
        )

        if anchored:
            extension_ids = sorted({str(item.get("id")) for item in anchored if item.get("id")})
            def action(project):
                for extension_id in extension_ids:
                    remove_similarity_extension(project.book, extension_id)
                sync_structure_rules(project.book)
                project.touch()
            try:
                self.session.execute("Retirer l’extension aux pages similaires", action)
            except Exception as exc:
                messagebox.showwarning("Contraintes éditoriales", str(exc), parent=self)
                return
            self._composition_constraints_message = "Extension aux pages similaires retirée."
            self._composition_refresh_after_structure_change(selected_snapshot, active_page_id)
            return

        self._composition_extend_active_constraints_to_similar(active_page_id)


    def _composition_render_constraints_panel(
        self,
        host,
        page_ids: list[str],
        active_page_id: str,
    ) -> None:
        """Une vue compacte : Position, Autour, Double page, Étendre."""

        book = self.session.book
        page_ids = [str(value) for value in page_ids if str(value) in book.pages]
        if not page_ids:
            return

        automatic_targets = [
            page_id for page_id in page_ids
            if is_structural_auto_page(book.pages[page_id])
        ]
        cover_targets = [
            page_id for page_id in page_ids
            if is_cover_face(book.pages[page_id])
        ]

        def section(title: str):
            tk.Label(
                host, text=title, bg=theme.PANEL, fg=theme.INK,
                font=(theme.FONT_UI, 9, "bold"), anchor="w",
            ).pack(fill="x", padx=18, pady=(10, 4))

        def divider():
            tk.Frame(host, bg=theme.PAGE_BORDER, height=1).pack(
                fill="x", padx=18, pady=(10, 0)
            )

        def square_row(text, checked, command, *, enabled=True, mixed=False):
            row = tk.Frame(host, bg=theme.PANEL)
            row.pack(fill="x", padx=18, pady=2)
            mark = "—" if mixed else "✓" if checked else ""
            indicator = tk.Button(
                row, text=mark, command=command,
                state=(tk.NORMAL if enabled else tk.DISABLED),
                bg=(theme.ACCENT_DARK if checked and not mixed else theme.PANEL_SOFT),
                fg=(theme.WHITE if checked and not mixed else theme.ACCENT_BRIGHT),
                disabledforeground=theme.MUTED_DARK,
                activebackground=theme.PANEL_SOFT, activeforeground=theme.INK,
                relief="solid", bd=1, width=2, padx=0, pady=0,
                font=(theme.FONT_UI, 9, "bold"),
                cursor=("hand2" if enabled else "arrow"),
            )
            indicator.pack(side="left", padx=(0, 7))
            label = tk.Button(
                row, text=text, command=command,
                state=(tk.NORMAL if enabled else tk.DISABLED),
                bg=theme.PANEL, fg=theme.INK,
                disabledforeground=theme.MUTED_DARK,
                activebackground=theme.PANEL, activeforeground=theme.INK,
                relief="flat", bd=0, anchor="w",
                font=(theme.FONT_UI, 9),
                cursor=("hand2" if enabled else "arrow"),
            )
            label.pack(side="left", fill="x", expand=True)
            return row

        # 1. POSITION — choix exclusif, mais représentation carrée partout.
        section("Position")
        right_state = self._composition_constraint_state(PAGE_RIGHT, page_ids)
        left_state = self._composition_constraint_state(PAGE_LEFT, page_ids)
        if right_state == 1 and left_state != 1:
            position_value = "right"
        elif left_state == 1 and right_state != 1:
            position_value = "left"
        elif right_state == 0 and left_state == 0:
            position_value = "free"
        else:
            position_value = "mixed"

        disabled_position = bool(cover_targets or automatic_targets)
        for value, label in (
            ("free", "Libre"),
            ("right", "Page à droite (recto)"),
            ("left", "Page à gauche (verso)"),
        ):
            square_row(
                label,
                position_value == value,
                lambda v=value: self._composition_set_position_constraint(
                    page_ids, active_page_id, v
                ),
                enabled=not disabled_position,
                mixed=(position_value == "mixed"),
            )

        # 2. AUTOUR DE LA PAGE
        divider(); section("Autour de la page")
        for kind in (BLANK_BEFORE, BLANK_AFTER):
            state = self._composition_constraint_state(kind, page_ids)
            disabled = bool(cover_targets or automatic_targets)
            def toggle(k=kind, current=state):
                variable = tk.IntVar(self, value=(0 if current == 1 else 1))
                self._composition_constraint_checkbox_changed(
                    k, variable, tuple(page_ids), active_page_id,
                )
            square_row(
                CONSTRAINT_LABELS[kind], state == 1, toggle,
                enabled=not disabled, mixed=(state == -1),
            )

        # 3. DOUBLE PAGE — même langage visuel carré.
        divider(); section("Double page")
        spread_state = self._composition_constraint_state(DOUBLE_PAGE, page_ids)
        reason = "" if spread_state == 1 else double_page_selection_reason(book, page_ids)
        def toggle_spread():
            variable = tk.IntVar(self, value=(0 if spread_state == 1 else 1))
            self._composition_constraint_checkbox_changed(
                DOUBLE_PAGE, variable, tuple(page_ids), active_page_id,
            )
        square_row(
            "Associer les pages sélectionnées",
            spread_state == 1,
            toggle_spread,
            enabled=(spread_state == 1 or not bool(reason)),
            mixed=(spread_state == -1),
        )
        if reason:
            tk.Label(
                host, text=reason, bg=theme.PANEL, fg=theme.MUTED,
                wraplength=215, justify="left", font=(theme.FONT_UI, 7),
            ).pack(fill="x", padx=43, pady=(2, 0))

        # 4. ÉTENDRE — TomeLinea choisit seul les pages similaires (>= 88 %).
        divider(); section("Étendre")
        active_non_spread = [
            kind for kind in active_constraint_kinds(book, active_page_id)
            if kind != DOUBLE_PAGE
        ] if active_page_id in book.pages else []

        anchored_memberships = [
            item for item in extension_memberships(book, active_page_id)
            if (
                str(item.get("anchor_page_id") or "") == str(active_page_id)
                and str(item.get("kind") or "") in active_non_spread
            )
        ]
        similar_checked = bool(anchored_memberships)
        try:
            similar_count = len(similar_page_ids(
                self.session.project,
                active_page_id,
                threshold=SIMILARITY_THRESHOLD,
            )) if active_non_spread else 0
        except Exception:
            similar_count = 0

        square_row(
            "Pages similaires",
            similar_checked,
            lambda: self._composition_toggle_constraints_similar_extension(active_page_id),
            enabled=bool(active_non_spread),
        )
        if active_non_spread:
            tk.Label(
                host,
                text=(
                    f"{similar_count} page{'s' if similar_count != 1 else ''} détectée"
                    f"{'s' if similar_count != 1 else ''} automatiquement (≥ 88 %)"
                ),
                bg=theme.PANEL, fg=theme.MUTED,
                font=(theme.FONT_UI, 7), anchor="w",
            ).pack(fill="x", padx=43, pady=(2, 0))

        message = str(getattr(self, "_composition_constraints_message", "") or "")
        if message:
            tk.Label(
                host, text=message, bg=theme.PANEL, fg=theme.ACCENT_BRIGHT,
                justify="left", wraplength=215,
                font=(theme.FONT_UI, 8, "bold"),
            ).pack(fill="x", padx=18, pady=(6, 0))

    def _composition_select_content_inventory_element(
        self,
        element_id: str,
    ) -> None:
        """Sélectionne un élément depuis l'inventaire de la page.

        Le panneau Contenu reste ouvert : la liste sert alors de navigateur
        direct vers les vrais objets de Composition.
        """

        page = self.session.active_page
        element_id = str(element_id or "")

        if page is None or not element_id:
            return

        element = next(
            (
                item
                for item in page.content
                if isinstance(item, dict)
                and str(item.get("id", "")) == element_id
            ),
            None,
        )
        if element is None:
            return

        self.session.set_selection(
            [element_id],
            include_associated=False,
        )

        kind = str(element.get("kind", "") or "").lower()
        self._composition_live_detach_ids = (
            {element_id}
            if kind in ("image", "text")
            else set()
        )

        self._composition_content_open = True
        self._composition_text_flow_open = False
        self._composition_update_inspector_context()

        canvas = getattr(
            self,
            "_composition_editor_canvas",
            None,
        )
        if canvas is not None:
            self._draw_page(canvas)


    def _composition_scroll_content_selection_into_view(
        self,
        element_id: str,
    ) -> None:
        """Recale discrètement la liste sur l'élément sélectionné."""

        rows = getattr(
            self,
            "_composition_content_rows",
            {},
        )
        row = rows.get(str(element_id or "")) if isinstance(rows, dict) else None
        canvas = getattr(
            self,
            "_composition_inspector_canvas",
            None,
        )
        host = getattr(
            self,
            "_composition_inspector_context",
            None,
        )
        if row is None or canvas is None or host is None:
            return

        try:
            host.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))
            bbox = canvas.bbox("all")
            if not bbox:
                return
            total = max(1.0, float(bbox[3] - bbox[1]))
            visible = max(1.0, float(canvas.winfo_height()))
            top = float(row.winfo_y())
            bottom = top + float(row.winfo_height())
            first, last = canvas.yview()
            visible_top = first * total
            visible_bottom = last * total
            if top < visible_top + 4:
                canvas.yview_moveto(max(0.0, (top - 8.0) / total))
            elif bottom > visible_bottom - 4:
                target = (bottom - visible + 8.0) / total
                canvas.yview_moveto(max(0.0, min(1.0, target)))
        except Exception:
            pass


    def _composition_render_content_panel(
        self,
        host,
        active_page_id: str,
    ) -> None:

        header = tk.Frame(host, bg=theme.PANEL)
        header.pack(fill="x", padx=18, pady=(8, 6))

        tk.Label(
            header,
            text="CONTENU DE LA PAGE",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 9, "bold"),
        ).pack(side="left")

        tk.Button(
            header,
            text="×",
            command=lambda: (
                setattr(self, "_composition_content_open", False),
                self._composition_update_inspector_context(),
            ),
            bg=theme.PANEL,
            fg=theme.MUTED,
            activebackground=theme.PANEL_SOFT,
            activeforeground=theme.INK,
            relief="flat",
            bd=0,
            font=(theme.FONT_UI, 11, "bold"),
            cursor="hand2",
        ).pack(side="right")

        try:
            inventory = page_content_inventory(
                self.session.book,
                active_page_id,
            )
        except Exception as exc:
            tk.Label(
                host,
                text=str(exc),
                bg=theme.PANEL,
                fg=theme.MUTED,
                justify="left",
                wraplength=220,
                font=(theme.FONT_UI, 8),
            ).pack(anchor="w", padx=18, pady=(4, 8))
            return

        try:
            editorial_roles = page_element_roles(
                self.session.book,
                active_page_id,
            )
        except Exception:
            editorial_roles = {}

        counts = inventory.get("counts", {})
        text_count = int(counts.get("text", 0) or 0)
        image_count = int(counts.get("image", 0) or 0)
        document_count = int(counts.get("document", 0) or 0)
        table_count = int(counts.get("table_structure", 0) or 0)
        list_count = int(counts.get("list_structure", 0) or 0)

        summary_parts = []
        if text_count:
            summary_parts.append(
                f"{text_count} zone{'s' if text_count != 1 else ''} texte"
            )
        if image_count:
            summary_parts.append(
                f"{image_count} image{'s' if image_count != 1 else ''}"
            )
        if document_count:
            summary_parts.append(
                f"{document_count} document{'s' if document_count != 1 else ''}"
            )
        if not summary_parts:
            summary_parts.append("Aucun élément de contenu")

        tk.Label(
            host,
            text=" · ".join(summary_parts),
            bg=theme.PANEL,
            fg=theme.INK,
            justify="left",
            wraplength=220,
            font=(theme.FONT_UI, 9, "bold"),
        ).pack(anchor="w", padx=18, pady=(2, 4))

        structure_parts = []
        if table_count:
            structure_parts.append(
                f"{table_count} structure{'s' if table_count != 1 else ''} tabulaire{'s' if table_count != 1 else ''}"
            )
        if list_count:
            structure_parts.append(
                f"{list_count} liste{'s' if list_count != 1 else ''} structurée{'s' if list_count != 1 else ''}"
            )
        if structure_parts:
            tk.Label(
                host,
                text="Structures repérées : " + " · ".join(structure_parts),
                bg=theme.PANEL,
                fg=theme.MUTED,
                justify="left",
                wraplength=220,
                font=(theme.FONT_UI, 8),
            ).pack(anchor="w", padx=18, pady=(0, 6))

        fonts = list(inventory.get("fonts", []) or [])
        if fonts:
            tk.Label(
                host,
                text=(
                    "Polices / variantes : "
                    + " · ".join(str(font) for font in fonts)
                ),
                bg=theme.PANEL,
                fg=theme.MUTED,
                justify="left",
                wraplength=220,
                font=(theme.FONT_UI, 8),
            ).pack(anchor="w", padx=18, pady=(0, 8))

        tk.Label(
            host,
            text="ÉLÉMENTS REPÉRÉS",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 8, "bold"),
        ).pack(anchor="w", padx=18, pady=(5, 5))

        by_id = {
            str(item.get("id", "")): item
            for item in inventory.get("elements", [])
            if isinstance(item, dict)
        }
        ordered = []
        for item_id in inventory.get("visual_order", []):
            item = by_id.get(str(item_id))
            if item is not None:
                ordered.append(item)
        for item in inventory.get("elements", []):
            if isinstance(item, dict) and item not in ordered:
                ordered.append(item)

        selected_ids = {
            str(item_id)
            for item_id in (
                getattr(
                    self.session,
                    "selected_element_ids",
                    (),
                )
                or ()
            )
        }
        self._composition_content_rows = {}

        for number, item in enumerate(ordered, 1):
            kind = str(item.get("kind", "") or "")
            element_id = str(item.get("id", "") or "")
            is_selected = bool(element_id and element_id in selected_ids)
            if kind == "text":
                prefix = "T"
                label = str(item.get("label", "Texte") or "Texte")
            elif kind == "image":
                prefix = "I"
                label = str(item.get("label", "Image") or "Image")
                quality = item.get("quality")
                if isinstance(quality, dict):
                    try:
                        dpi = round(float(quality.get("effective_dpi", 0.0)))
                    except Exception:
                        dpi = 0
                    if dpi:
                        label += f" · {dpi} dpi"
            else:
                prefix = "D"
                label = str(item.get("label", "Document") or "Document")

            role = editorial_roles.get(element_id)
            if role is not None and getattr(role, "role", ""):
                label = f"{role.role} · {label}"

            row_bg = theme.ACCENT_DARK if is_selected else theme.PANEL_SOFT
            row = tk.Frame(
                host,
                bg=row_bg,
                cursor="hand2",
                takefocus=True,
            )
            row.pack(fill="x", padx=18, pady=(0, 3))
            if element_id:
                self._composition_content_rows[element_id] = row

            prefix_label = tk.Label(
                row,
                text=f"{prefix}{number}",
                bg=row_bg,
                fg=(theme.WHITE if is_selected else theme.ACCENT_BRIGHT),
                font=(theme.FONT_UI, 8, "bold"),
                width=3,
                anchor="w",
                cursor="hand2",
            )
            prefix_label.pack(side="left", padx=(6, 2), pady=5)
            text_label = tk.Label(
                row,
                text=label,
                bg=row_bg,
                fg=theme.INK,
                justify="left",
                anchor="w",
                wraplength=174,
                font=(theme.FONT_UI, 8, "bold" if is_selected else "normal"),
                cursor="hand2",
            )
            text_label.pack(side="left", fill="x", expand=True, padx=(0, 6), pady=5)

            if element_id:
                callback = lambda _event, eid=element_id: (
                    self._composition_select_content_inventory_element(eid),
                    "break",
                )[1]
                for widget in (row, prefix_label, text_label):
                    widget.bind("<Button-1>", callback, add="+")
                row.bind(
                    "<Return>",
                    lambda _event, eid=element_id: (
                        self._composition_select_content_inventory_element(eid),
                        "break",
                    )[1],
                    add="+",
                )

        if selected_ids:
            selected_id = next(iter(selected_ids), "")
            if selected_id:
                self.after_idle(
                    lambda eid=selected_id: self._composition_scroll_content_selection_into_view(eid)
                )

        structures = [
            item
            for item in inventory.get("structures", [])
            if isinstance(item, dict)
        ]
        if structures:
            tk.Label(
                host,
                text="STRUCTURES SOURCE",
                bg=theme.PANEL,
                fg=theme.MUTED,
                font=(theme.FONT_UI, 8, "bold"),
            ).pack(anchor="w", padx=18, pady=(8, 5))
            for item in structures:
                label = str(item.get("label", "Structure") or "Structure")
                if item.get("kind") == "list_structure":
                    count = int(item.get("item_count", 0) or 0)
                    if count:
                        label += f" · {count} éléments"
                tk.Label(
                    host,
                    text=label,
                    bg=theme.PANEL_SOFT,
                    fg=theme.INK,
                    justify="left",
                    anchor="w",
                    wraplength=205,
                    font=(theme.FONT_UI, 8),
                    padx=7,
                    pady=5,
                ).pack(fill="x", padx=18, pady=(0, 3))


    def _composition_select_text_flow_element(
        self,
        element_id: str,
    ) -> None:
        """Sélectionne une zone depuis le contrôle des flux de texte."""

        page = self.session.active_page
        element_id = str(element_id or "")
        if page is None or not element_id:
            return

        element = next(
            (
                item
                for item in page.content
                if isinstance(item, dict)
                and str(item.get("id", "")) == element_id
            ),
            None,
        )
        if element is None:
            return

        self.session.set_selection(
            [element_id],
            include_associated=False,
        )
        self._composition_live_detach_ids = {element_id}
        self._composition_text_flow_open = True
        self._composition_content_open = False
        self._composition_update_inspector_context()

        canvas = getattr(self, "_composition_editor_canvas", None)
        if canvas is not None:
            self._draw_page(canvas)


    def _composition_render_text_flow_panel(
        self,
        host,
        active_page_id: str,
    ) -> None:
        header = tk.Frame(host, bg=theme.PANEL)
        header.pack(fill="x", padx=18, pady=(8, 6))

        tk.Label(
            header,
            text="FLUX DE TEXTE",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 9, "bold"),
        ).pack(side="left")

        tk.Button(
            header,
            text="×",
            command=lambda: (
                setattr(self, "_composition_text_flow_open", False),
                self._composition_update_inspector_context(),
            ),
            bg=theme.PANEL,
            fg=theme.MUTED,
            activebackground=theme.PANEL_SOFT,
            activeforeground=theme.INK,
            relief="flat",
            bd=0,
            font=(theme.FONT_UI, 11, "bold"),
            cursor="hand2",
        ).pack(side="right")

        try:
            entries = page_text_flow_entries(
                self.session.book,
                active_page_id,
            )
        except Exception as exc:
            tk.Label(
                host,
                text=str(exc),
                bg=theme.PANEL,
                fg=theme.MUTED,
                justify="left",
                wraplength=220,
                font=(theme.FONT_UI, 8),
            ).pack(anchor="w", padx=18, pady=(4, 8))
            return

        tk.Label(
            host,
            text=(
                "TomeLinea relie ici uniquement les zones qui semblent "
                "appartenir au même corps de texte."
            ),
            bg=theme.PANEL,
            fg=theme.MUTED,
            justify="left",
            wraplength=220,
            font=(theme.FONT_UI, 8),
        ).pack(anchor="w", padx=18, pady=(0, 8))

        if not entries:
            tk.Label(
                host,
                text="Aucun flux de corps de texte repéré sur cette page.",
                bg=theme.PANEL_SOFT,
                fg=theme.INK,
                justify="left",
                wraplength=205,
                font=(theme.FONT_UI, 8),
                padx=7,
                pady=7,
            ).pack(fill="x", padx=18, pady=(0, 4))
            return

        selected_ids = {
            str(item_id)
            for item_id in (
                getattr(self.session, "selected_element_ids", ()) or ()
            )
        }
        self._composition_text_flow_rows = {}

        def page_number(page_id: str | None) -> int | None:
            if not page_id:
                return None
            try:
                return self.session.book.page_order.index(page_id) + 1
            except ValueError:
                return None

        for entry in entries:
            flow_no = int(entry.get("flow_number", 0) or 0)
            previous_no = page_number(entry.get("previous_page_id"))
            next_no = page_number(entry.get("next_page_id"))
            if previous_no and next_no:
                status = f"Suite de la page {previous_no} · continue page {next_no}"
            elif previous_no:
                status = f"Suite de la page {previous_no} · se termine ici"
            elif next_no:
                status = f"Débute ici · continue page {next_no}"
            else:
                status = "Flux contenu sur cette page"

            tk.Label(
                host,
                text=f"FLUX {flow_no}",
                bg=theme.PANEL,
                fg=theme.ACCENT_BRIGHT,
                font=(theme.FONT_UI, 8, "bold"),
            ).pack(anchor="w", padx=18, pady=(5, 1))
            tk.Label(
                host,
                text=status,
                bg=theme.PANEL,
                fg=theme.MUTED,
                justify="left",
                wraplength=220,
                font=(theme.FONT_UI, 8),
            ).pack(anchor="w", padx=18, pady=(0, 2))

            typography = entry.get("typography", {})
            if isinstance(typography, dict):
                def fmt_measure(value, digits=2):
                    try:
                        number = float(value)
                    except (TypeError, ValueError):
                        return None
                    text = f"{number:.{digits}f}".rstrip("0").rstrip(".")
                    return text.replace(".", ",")

                font_name = str(typography.get("dominant_font", "") or "").strip()
                size = fmt_measure(typography.get("dominant_size_pt"), 2)
                pitch = fmt_measure(typography.get("line_pitch_mm"), 2)
                profile_parts = []
                if font_name:
                    profile_parts.append(font_name)
                if size:
                    profile_parts.append(f"{size} pt")
                if pitch:
                    profile_parts.append(f"interligne ≈ {pitch} mm")
                if profile_parts:
                    tk.Label(
                        host,
                        text="Source · " + " · ".join(profile_parts),
                        bg=theme.PANEL,
                        fg=theme.INK,
                        justify="left",
                        wraplength=220,
                        font=(theme.FONT_UI, 8),
                    ).pack(anchor="w", padx=18, pady=(0, 2))

                indent = fmt_measure(typography.get("first_line_indent_mm"), 2)
                gap = fmt_measure(typography.get("block_gap_mm"), 2)
                detail_parts = []
                if indent is not None:
                    detail_parts.append(f"retrait 1re ligne ≈ {indent} mm")
                if gap is not None:
                    detail_parts.append(f"écart entre blocs ≈ {gap} mm")
                if detail_parts:
                    tk.Label(
                        host,
                        text=" · ".join(detail_parts),
                        bg=theme.PANEL,
                        fg=theme.MUTED,
                        justify="left",
                        wraplength=220,
                        font=(theme.FONT_UI, 8),
                    ).pack(anchor="w", padx=18, pady=(0, 4))
                else:
                    tk.Frame(host, bg=theme.PANEL, height=2).pack(fill="x")

            for number, segment in enumerate(entry.get("segments", []) or (), 1):
                element_id = str(segment.get("element_id", "") or "")
                text = " ".join(str(segment.get("text", "") or "").split())
                if len(text) > 72:
                    text = text[:71].rstrip() + "…"
                is_selected = bool(element_id and element_id in selected_ids)
                row_bg = theme.ACCENT_DARK if is_selected else theme.PANEL_SOFT
                row = tk.Frame(host, bg=row_bg, cursor="hand2", takefocus=True)
                row.pack(fill="x", padx=18, pady=(0, 3))
                if element_id:
                    self._composition_text_flow_rows[element_id] = row

                number_label = tk.Label(
                    row,
                    text=str(number),
                    bg=row_bg,
                    fg=(theme.WHITE if is_selected else theme.ACCENT_BRIGHT),
                    font=(theme.FONT_UI, 8, "bold"),
                    width=2,
                    anchor="w",
                    cursor="hand2",
                )
                number_label.pack(side="left", padx=(6, 2), pady=5)
                text_label = tk.Label(
                    row,
                    text=text or "Zone de texte",
                    bg=row_bg,
                    fg=theme.INK,
                    justify="left",
                    anchor="w",
                    wraplength=182,
                    font=(theme.FONT_UI, 8, "bold" if is_selected else "normal"),
                    cursor="hand2",
                )
                text_label.pack(side="left", fill="x", expand=True, padx=(0, 6), pady=5)

                if element_id:
                    callback = lambda _event, eid=element_id: (
                        self._composition_select_text_flow_element(eid),
                        "break",
                    )[1]
                    for widget in (row, number_label, text_label):
                        widget.bind("<Button-1>", callback, add="+")
                    row.bind(
                        "<Return>",
                        lambda _event, eid=element_id: (
                            self._composition_select_text_flow_element(eid),
                            "break",
                        )[1],
                        add="+",
                    )



    def _composition_text_prepare_rules(self) -> None:
        """Initialise les règles et corrige les fautes objectives à l'ouverture de Texte."""
        book = getattr(self.session, "book", None)
        if book is None:
            return
        try:
            from src.v4.text_rules import immutable_text_issues
            metadata = getattr(book, "metadata", {})
            has_rules = isinstance(metadata, dict) and isinstance(metadata.get("text_general_rules"), dict)
            pending = immutable_text_issues(book)
        except Exception as exc:
            self._composition_text_inline_notice = str(exc)
            return

        if has_rules and not pending:
            return

        def action(project):
            from src.v4.text_engine import prepare_text
            report = prepare_text(project.book)
            if report.rules_created or report.automatic_corrections:
                project.touch()
            return {
                "created": report.rules_created,
                "corrections": list(report.automatic_corrections),
                "rules": dict(report.rules),
            }

        try:
            result = self.session.execute("Préparer les règles générales du texte", action)
        except Exception as exc:
            self._composition_text_inline_notice = str(exc)
            return

        count = len((result or {}).get("corrections", ()) or ())
        if count:
            self._composition_text_auto_notice = (
                f"{count} correction{'s' if count != 1 else ''} technique"
                f"{'s' if count != 1 else ''} appliquée{'s' if count != 1 else ''} automatiquement."
            )
        if bool((result or {}).get("created")):
            self._composition_text_rules_edit = True
            self._composition_text_rules_draft = dict((result or {}).get("rules", {}) or {})

    def _composition_text_rules(self) -> dict:
        book = getattr(self.session, "book", None)
        if book is None:
            return {}
        try:
            from src.v4.text_rules import text_general_rules
            return dict(text_general_rules(book, create=False) or {})
        except Exception:
            return {}

    def _composition_text_begin_rules_edit(self) -> None:
        self._composition_text_rules_edit = True
        self._composition_text_rules_draft = self._composition_text_rules()
        self._composition_text_correction_review_state = None
        self._composition_text_inline_notice = ""
        self._composition_update_inspector_context()

    def _composition_text_rule_draft_set(self, key: str, value) -> None:
        draft = self.__dict__.get("_composition_text_rules_draft")
        if not isinstance(draft, dict):
            draft = self._composition_text_rules()
            self._composition_text_rules_draft = draft
        draft[str(key)] = value

    def _composition_text_choose_hyphenation(self, policy: str) -> None:
        policy = str(policy or "undecided").lower()
        if policy not in {"forbid", "controlled"}:
            return
        self._composition_text_rule_draft_set("hyphenation", policy)
        self._composition_update_inspector_context()

    @staticmethod
    def _composition_text_rule_number(value, default=None):
        text = str(value if value is not None else "").strip().replace(",", ".")
        if not text:
            return default
        try:
            return round(float(text), 2)
        except (TypeError, ValueError):
            return default

    def _composition_text_confirm_rules(self) -> None:
        draft = self.__dict__.get("_composition_text_rules_draft")
        if not isinstance(draft, dict):
            draft = self._composition_text_rules()
        policy = str(draft.get("hyphenation", "undecided") or "undecided").lower()
        if policy not in {"forbid", "controlled"}:
            self._composition_text_inline_notice = "Choisissez d'abord la règle générale des césures."
            self._composition_update_inspector_context()
            return

        variables = self.__dict__.get("_composition_text_rule_vars", {})
        if isinstance(variables, dict):
            for key in ("first_line_indent_mm", "line_pitch_mm", "paragraph_gap_mm"):
                var = variables.get(key)
                if var is not None:
                    try:
                        draft[key] = self._composition_text_rule_number(var.get(), draft.get(key))
                    except Exception:
                        pass

        def action(project):
            from src.v4.text_rules import update_text_general_rules
            rules = update_text_general_rules(
                project.book,
                confirmed=True, alignment="justify", inside_margins=True,
                hyphenation=policy,
                first_line_indent_mm=draft.get("first_line_indent_mm"),
                line_pitch_mm=draft.get("line_pitch_mm"),
                paragraph_gap_mm=draft.get("paragraph_gap_mm"),
            )
            project.touch()
            return dict(rules)

        try:
            self.session.execute("Valider les règles générales du texte", action)
        except Exception as exc:
            self._composition_text_inline_notice = str(exc)
            self._composition_update_inspector_context()
            return
        self._composition_text_rules_edit = False
        self._composition_text_rules_draft = None
        self._composition_text_rule_vars = None
        self._composition_text_problem_index = 0
        self._composition_text_inline_notice = ""
        # Le passage des règles au contrôle doit être explicite : une fois le
        # choix enregistré, TomeLinea relance l'analyse et annonce le nombre de
        # problèmes qui demandent réellement l'avis de l'utilisateur.
        try:
            problem_count = len(self._composition_text_problem_entries())
        except Exception:
            problem_count = 0
        self._composition_text_auto_notice = (
            f"Analyse terminée : {problem_count} problème{'s' if problem_count != 1 else ''} à examiner."
            if problem_count
            else "Analyse terminée : aucun problème ne demande votre décision."
        )
        self._composition_text_focus_current_problem()
        self._composition_update_inspector_context()

    def _composition_render_text_general_rules(self, host) -> bool:
        """Affiche les règles générales. Retourne True si leur réglage occupe tout le panneau."""
        rules = self._composition_text_rules()
        editing = bool(self.__dict__.get("_composition_text_rules_edit", False)) or not bool(rules.get("confirmed"))
        draft = self.__dict__.get("_composition_text_rules_draft")
        if not isinstance(draft, dict):
            draft = dict(rules)
            self._composition_text_rules_draft = draft

        card = tk.Frame(host, bg=theme.PANEL_SOFT, highlightthickness=1, highlightbackground=theme.PAGE_BORDER)
        card.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(
            card, text="RÈGLES GÉNÉRALES", bg=theme.PANEL_SOFT, fg=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 8, "bold"), anchor="w",
        ).pack(fill="x", padx=10, pady=(8, 4))

        def fmt(value, suffix=" mm"):
            try:
                number = float(value)
            except (TypeError, ValueError):
                return "—"
            return f"{number:.2f}".rstrip("0").rstrip(".").replace(".", ",") + suffix

        font = str(rules.get("font_family", "") or "").strip() or "Police de la Source"
        size = rules.get("font_size_pt")
        font_text = font + (f" · {fmt(size, ' pt')}" if size is not None else "")
        tk.Label(
            card, text="Police · " + font_text + " (import)", bg=theme.PANEL_SOFT, fg=theme.INK,
            wraplength=205, justify="left", anchor="w", font=(theme.FONT_UI, 8),
        ).pack(fill="x", padx=10, pady=(0, 3))
        tk.Label(
            card, text="Texte courant · justifié · entre les marges", bg=theme.PANEL_SOFT, fg=theme.INK,
            wraplength=205, justify="left", anchor="w", font=(theme.FONT_UI, 8, "bold"),
        ).pack(fill="x", padx=10, pady=(0, 5))

        if editing:
            self._composition_text_rules_edit = True
            vars_map = {}
            for key, label in (
                ("first_line_indent_mm", "Retrait 1re ligne"),
                ("line_pitch_mm", "Interligne"),
                ("paragraph_gap_mm", "Espace entre paragraphes"),
            ):
                row = tk.Frame(card, bg=theme.PANEL_SOFT)
                row.pack(fill="x", padx=10, pady=(1, 2))
                tk.Label(row, text=label, bg=theme.PANEL_SOFT, fg=theme.MUTED, font=(theme.FONT_UI, 7), anchor="w").pack(side="left", fill="x", expand=True)
                value = draft.get(key)
                var = tk.StringVar(value="" if value is None else str(value).replace(".", ","))
                vars_map[key] = var
                tk.Entry(
                    row, textvariable=var, width=6, justify="right", bg=theme.PANEL, fg=theme.INK,
                    insertbackground=theme.INK, relief="flat", bd=0, highlightthickness=1,
                    highlightbackground=theme.PAGE_BORDER, font=(theme.FONT_UI, 7),
                ).pack(side="right")
            self._composition_text_rule_vars = vars_map

            tk.Label(
                card, text="Césures", bg=theme.PANEL_SOFT, fg=theme.MUTED,
                font=(theme.FONT_UI, 7, "bold"), anchor="w",
            ).pack(fill="x", padx=10, pady=(6, 3))
            policy = str(draft.get("hyphenation", "undecided") or "undecided")
            buttons = tk.Frame(card, bg=theme.PANEL_SOFT)
            buttons.pack(fill="x", padx=10, pady=(0, 5))
            self._button(
                buttons, "Sans césures", lambda: self._composition_text_choose_hyphenation("forbid"),
                compact=True, accent=(policy == "forbid"),
            ).pack(side="left", fill="x", expand=True, padx=(0, 3))
            self._button(
                buttons, "Autorisées et contrôlées", lambda: self._composition_text_choose_hyphenation("controlled"),
                compact=True, accent=(policy == "controlled"),
            ).pack(side="left", fill="x", expand=True, padx=(3, 0))
            policy_help = {
                "forbid": (
                    "Aucune coupure de mot : TomeLinea signalera les césures et les retirera après votre accord."
                ),
                "controlled": (
                    "Les césures correctes sont admises. TomeLinea ne signalera que les coupures gênantes ou fragiles."
                ),
                "undecided": "Choisissez une règle une seule fois pour l'ensemble du livre.",
            }.get(policy, "Choisissez une règle une seule fois pour l'ensemble du livre.")
            tk.Label(
                card, text=policy_help,
                bg=theme.PANEL_SOFT, fg=(theme.WARNING if policy == "undecided" else theme.MUTED),
                wraplength=200, justify="left", anchor="w",
                font=(theme.FONT_UI, 7, "bold" if policy == "undecided" else "normal"),
            ).pack(fill="x", padx=10, pady=(0, 5))

            self._button(
                card, "Valider et analyser le texte", self._composition_text_confirm_rules,
                compact=True, accent=True, enabled=(policy != "undecided"),
            ).pack(fill="x", padx=10, pady=(3, 10))
            return True

        summary = []
        if rules.get("first_line_indent_mm") is not None:
            summary.append("retrait " + fmt(rules.get("first_line_indent_mm")))
        if rules.get("line_pitch_mm") is not None:
            summary.append("interligne " + fmt(rules.get("line_pitch_mm")))
        if rules.get("paragraph_gap_mm") is not None:
            summary.append("écart " + fmt(rules.get("paragraph_gap_mm")))
        policy_label = "sans césures" if rules.get("hyphenation") == "forbid" else "césures contrôlées"
        if summary:
            tk.Label(
                card, text="Paragraphes · " + " · ".join(summary), bg=theme.PANEL_SOFT, fg=theme.MUTED,
                wraplength=205, justify="left", anchor="w", font=(theme.FONT_UI, 7),
            ).pack(fill="x", padx=10, pady=(0, 2))
        tk.Label(
            card, text="Césures · " + policy_label, bg=theme.PANEL_SOFT, fg=theme.MUTED,
            font=(theme.FONT_UI, 7), anchor="w",
        ).pack(fill="x", padx=10, pady=(0, 5))
        self._button(
            card, "Modifier les règles", self._composition_text_begin_rules_edit, compact=True,
        ).pack(fill="x", padx=10, pady=(1, 9))
        return False

    def _composition_text_problem_entries(self) -> list[dict]:
        """Retourne uniquement les anomalies issues d'un moteur identifié.

        Aucune heuristique d'interface n'invente désormais un problème à partir
        d'une position ou d'un simple tiret. Le moteur Texte V4 est l'autorité ;
        des moteurs spécialisés peuvent encore fournir explicitement des
        anomalies via les métadonnées de page ou d'élément.
        """

        book = self.session.book
        if book is None:
            return []

        decisions = book.metadata.get("text_problem_decisions", {})
        if not isinstance(decisions, dict):
            decisions = {}

        try:
            from src.v4.text_anomalies import anomalies_by_page
            automatic_issues_by_page = anomalies_by_page(book)
        except Exception:
            automatic_issues_by_page = {}

        result: list[dict] = []
        seen: set[str] = set()

        def add_issue(*, page, element, element_index, raw):
            if not isinstance(raw, dict):
                return
            kind = str(raw.get("type", raw.get("kind", "text")) or "text").lower()
            element_id = ""
            if isinstance(element, dict):
                element_id = str(element.get("id", "") or "")
            if not element_id:
                element_id = str(raw.get("element_id", "") or "")
            key = str(raw.get("id", "") or f"{page.id}:{element_id or element_index}:{kind}")
            if key in seen:
                return
            state = str(decisions.get(key, "") or "")
            if state == "ignored":
                return
            # Une anomalie du moteur automatique disparaît uniquement lorsqu'il
            # ne la retrouve plus. Un ancien clic « corrigé » ne peut donc pas
            # masquer une régression.
            if state == "corrected" and str(raw.get("engine", "") or "") != "tomelinea.text_anomalies":
                return

            geometry = raw.get("geometry")
            if not isinstance(geometry, dict) and isinstance(element, dict):
                geometry = element.get("geometry")
            title = str(raw.get("title", raw.get("message", "Ce passage mérite votre attention")) or "")
            why = str(raw.get("why", raw.get("reason", "TomeLinea a repéré un écart à la règle du livre.")) or "")
            proposal = str(raw.get("proposal", raw.get("suggestion", "Corriger cet écart selon la règle du livre.")) or "")
            term = str(raw.get("technical_term", "") or "")
            result.append({
                "key": key,
                "page_id": str(page.id),
                "element_id": element_id,
                "element_index": int(element_index),
                "kind": kind,
                "title": title,
                "term": term,
                "why": why,
                "proposal": proposal,
                "geometry": dict(geometry) if isinstance(geometry, dict) else None,
                "engine": str(raw.get("engine", "") or ""),
            })
            seen.add(key)

        for page_id in book.page_order:
            page = book.pages.get(page_id)
            if page is None:
                continue

            # 1) Moteur Texte TomeLinea.
            for number, raw in enumerate(automatic_issues_by_page.get(str(page.id), ())):
                add_issue(page=page, element=None, element_index=100000 + number, raw=raw)

            # 2) Anomalies explicites fournies par un autre moteur de TomeLinea.
            page_issues = getattr(page, "metadata", {}).get("text_anomalies", ())
            if isinstance(page_issues, dict):
                page_issues = (page_issues,)
            if isinstance(page_issues, (list, tuple)):
                for number, raw in enumerate(page_issues):
                    add_issue(page=page, element=None, element_index=200000 + number, raw=raw)

            for element_index, element in enumerate(getattr(page, "content", ())):
                if not isinstance(element, dict) or str(element.get("kind", "")).lower() != "text":
                    continue
                metadata = element.get("metadata", {})
                if not isinstance(metadata, dict):
                    continue
                explicit = metadata.get("text_anomalies", ())
                if isinstance(explicit, dict):
                    explicit = (explicit,)
                if not isinstance(explicit, (list, tuple)):
                    continue
                for number, raw in enumerate(explicit):
                    add_issue(
                        page=page,
                        element=element,
                        element_index=element_index * 100 + number,
                        raw=raw,
                    )

        return result


    def _composition_text_current_problem(self):
        problems = self._composition_text_problem_entries()
        if not problems:
            self._composition_text_problem_index = 0
            return None, problems
        index = int(getattr(self, "_composition_text_problem_index", 0) or 0)
        index = max(0, min(index, len(problems) - 1))
        self._composition_text_problem_index = index
        return problems[index], problems

    def _composition_text_focus_current_problem(self) -> None:
        problem, _problems = self._composition_text_current_problem()
        if problem is None:
            canvas = getattr(self, "_composition_editor_canvas", None)
            if canvas is not None:
                self._draw_page(canvas)
            return
        page_id = str(problem.get("page_id", "") or "")
        if page_id and page_id in self.session.book.pages:
            self._composition_selected_page_ids = {page_id}
            if str(self.session.active_page_id or "") != page_id:
                self._activate_page(page_id)
            else:
                canvas = getattr(self, "_composition_editor_canvas", None)
                if canvas is not None:
                    self._draw_page(canvas)

    def _composition_text_move_problem(self, delta: int) -> None:
        # Quitter explicitement l'état « correction appliquée » avant de
        # naviguer : tant que l'utilisateur ne demande pas à avancer, TomeLinea
        # reste sur la correction qu'il vient d'effectuer.
        self._composition_text_correction_review_state = None
        self._composition_text_inline_notice = ""
        _problem, problems = self._composition_text_current_problem()
        if not problems:
            return
        self._composition_text_problem_index = (
            int(getattr(self, "_composition_text_problem_index", 0) or 0) + int(delta)
        ) % len(problems)
        self._composition_text_focus_current_problem()
        self._composition_update_inspector_context()

    def _composition_text_correction_review(self) -> dict | None:
        value = self.__dict__.get("_composition_text_correction_review_state")
        return value if isinstance(value, dict) else None

    def _composition_text_manual_correction(self) -> dict | None:
        value = self.__dict__.get("_composition_text_manual_state")
        return value if isinstance(value, dict) else None

    def _composition_text_manual_targets_element(self, element) -> bool:
        state = self._composition_text_manual_correction()
        if state is None or not isinstance(element, dict):
            return False
        return str(element.get("id", "") or "") == str(state.get("element_id", "") or "")

    def _composition_text_problem_element(self, problem: dict | None):
        if not isinstance(problem, dict) or self.session is None:
            return None
        page = self.session.book.pages.get(str(problem.get("page_id", "") or ""))
        if page is None:
            return None
        element_id = str(problem.get("element_id", "") or "")
        for element in getattr(page, "content", ()):
            if isinstance(element, dict) and str(element.get("id", "") or "") == element_id:
                return element
        return None

    def _composition_text_begin_manual_correction(self, problem: dict | None = None) -> None:
        from copy import deepcopy

        if problem is None:
            problem, _ = self._composition_text_current_problem()
        if not isinstance(problem, dict):
            return
        element = self._composition_text_problem_element(problem)
        if not isinstance(element, dict):
            self._composition_text_inline_notice = (
                "TomeLinea a repéré ce problème, mais la zone concernée ne peut pas être modifiée directement."
            )
            self._composition_update_inspector_context()
            return
        payload = element.get("payload", {})
        if not isinstance(payload, dict):
            payload = {}
        self._composition_text_correction_review_state = None
        self._composition_text_inline_notice = ""
        self._composition_text_manual_state = {
            "key": str(problem.get("key", "") or ""),
            "problem": dict(problem),
            "page_id": str(problem.get("page_id", "") or ""),
            "element_id": str(problem.get("element_id", "") or ""),
            "draft_text": str(payload.get("text", "") or ""),
            "original_text": str(payload.get("text", "") or ""),
            "original_payload": deepcopy(payload),
            "original_geometry": deepcopy(element.get("geometry", {}) or {}),
            "original_metadata": deepcopy(element.get("metadata", {}) or {}),
            "notice": "",
        }
        if str(problem.get("kind", "") or "") == "style_outlier":
            spans = payload.get("spans", []) if isinstance(payload, dict) else []
            sizes = []
            if isinstance(spans, list):
                for span in spans:
                    if not isinstance(span, dict):
                        continue
                    try:
                        value = float(span.get("size", 0.0) or 0.0)
                    except (TypeError, ValueError):
                        value = 0.0
                    if value > 0:
                        sizes.append(value)
            current_size = sum(sizes) / len(sizes) if sizes else 10.0
            try:
                from src.v4.text_anomalies import book_body_text_size
                suggested_size = float(book_body_text_size(self.session.book))
            except Exception:
                suggested_size = 10.0
            self._composition_text_manual_state["font_size_current"] = current_size
            self._composition_text_manual_state["font_size_draft"] = current_size
            self._composition_text_manual_state["font_size_suggested"] = suggested_size

        page_id = str(problem.get("page_id", "") or "")
        element_id = str(problem.get("element_id", "") or "")
        if page_id and page_id in self.session.book.pages:
            self._composition_selected_page_ids = {page_id}
            if str(self.session.active_page_id or "") != page_id:
                self.session.set_active_page(page_id)
        if element_id:
            self.session.set_selection([element_id], include_associated=False)
        canvas = self.__dict__.get("_composition_editor_canvas")
        if canvas is not None:
            self._draw_page(canvas)
        self._composition_update_inspector_context()

    def _composition_text_capture_manual_draft(self, widget) -> None:
        state = self._composition_text_manual_correction()
        if state is None:
            return
        try:
            state["draft_text"] = widget.get("1.0", "end-1c")
        except Exception:
            pass

    def _composition_text_capture_manual_font_size(self, variable) -> None:
        state = self._composition_text_manual_correction()
        if state is None:
            return
        try:
            raw = str(variable.get() or "").strip().replace(",", ".")
            state["font_size_draft"] = float(raw)
            state["font_size_error"] = ""
        except Exception:
            state["font_size_error"] = "Entrez une taille valide en points."

    def _composition_text_restore_manual_snapshot(self, snapshot: dict) -> None:
        from copy import deepcopy

        if not isinstance(snapshot, dict) or self.session is None:
            return
        page_id = str(snapshot.get("page_id", "") or "")
        element_id = str(snapshot.get("element_id", "") or "")
        original_text = str(snapshot.get("original_text", "") or "")
        original_payload = deepcopy(snapshot.get("original_payload"))
        original_geometry = deepcopy(snapshot.get("original_geometry", {}) or {})
        original_metadata = deepcopy(snapshot.get("original_metadata", {}) or {})

        def action(project):
            page = project.book.pages.get(page_id)
            if page is None:
                return
            for element in getattr(page, "content", ()):
                if not isinstance(element, dict) or str(element.get("id", "") or "") != element_id:
                    continue
                if isinstance(original_payload, dict):
                    element["payload"] = deepcopy(original_payload)
                else:
                    payload = element.get("payload")
                    if not isinstance(payload, dict):
                        payload = {}
                        element["payload"] = payload
                    payload["text"] = original_text
                element["geometry"] = deepcopy(original_geometry)
                element["metadata"] = deepcopy(original_metadata)
                project.touch()
                return

        try:
            self.session.execute("Rétablir la correction manuelle", action)
        except Exception:
            pass

    def _composition_text_cancel_manual_correction(self) -> None:
        state = self._composition_text_manual_correction()
        if state is None:
            return
        key = str(state.get("key", "") or "")
        self._composition_text_restore_manual_snapshot(state)
        self._composition_text_manual_state = None
        self._composition_text_inline_notice = ""
        problems = self._composition_text_problem_entries()
        for index, item in enumerate(problems):
            if str(item.get("key", "") or "") == key:
                self._composition_text_problem_index = index
                break
        self._composition_text_focus_current_problem()
        self._composition_update_inspector_context()

    @staticmethod
    def _composition_text_change_excerpt(before: str, after: str, radius: int = 55) -> tuple[str, str]:
        before = str(before or "")
        after = str(after or "")
        if before == after:
            return "", ""
        limit = min(len(before), len(after))
        index = 0
        while index < limit and before[index] == after[index]:
            index += 1
        start = max(0, index - radius)
        b = before[start:index + radius].replace("\n", " ").strip()
        a = after[start:index + radius].replace("\n", " ").strip()
        if start > 0:
            b = "…" + b
            a = "…" + a
        if index + radius < len(before):
            b += "…"
        if index + radius < len(after):
            a += "…"
        return b, a

    def _composition_text_verify_manual_correction(self) -> None:
        state = self._composition_text_manual_correction()
        if state is None or self.session is None:
            return
        problem = state.get("problem")
        if not isinstance(problem, dict):
            return
        element = self._composition_text_problem_element(problem)
        if not isinstance(element, dict):
            state["notice"] = "La zone de texte n'est plus disponible."
            self._composition_update_inspector_context()
            return

        payload = element.get("payload", {})
        current_text = str(payload.get("text", "") or "") if isinstance(payload, dict) else ""
        draft_text = str(state.get("draft_text", current_text) or "")
        result = {
            "changed": False,
            "kind": "manual",
            "before_text": str(state.get("original_text", "") or ""),
            "after_text": current_text,
            "page_id": str(state.get("page_id", "") or ""),
            "element_id": str(state.get("element_id", "") or ""),
            "geometry": dict(element.get("geometry", {}) or {}),
        }

        if draft_text != current_text:
            try:
                from src.v4.text_anomalies import apply_manual_text_edit

                def action(project):
                    correction = apply_manual_text_edit(project.book, problem, draft_text)
                    project.book.metadata["text_reflow_requested"] = True
                    project.touch()
                    return correction

                result = dict(self.session.execute("Correction manuelle du texte", action) or {})
            except Exception as exc:
                state["notice"] = str(exc)
                self._composition_update_inspector_context()
                return

        if "font_size_draft" in state:
            try:
                target_size = float(state.get("font_size_draft"))
                current_size = float(state.get("font_size_current", target_size))
            except (TypeError, ValueError):
                state["notice"] = "Entrez une taille de texte valide."
                self._composition_update_inspector_context()
                return
            if abs(target_size - current_size) > 0.01:
                try:
                    from src.v4.text_anomalies import apply_manual_text_size

                    def style_action(project):
                        correction = apply_manual_text_size(project.book, problem, target_size)
                        project.book.metadata["text_reflow_requested"] = True
                        project.touch()
                        return correction

                    style_result = dict(self.session.execute("Modifier la taille du texte", style_action) or {})
                    result.update(style_result)
                    result["before_line"] = f"Taille : {current_size:.1f} pt"
                    result["after_line"] = f"Taille : {target_size:.1f} pt"
                    state["font_size_current"] = target_size
                except Exception as exc:
                    state["notice"] = str(exc)
                    self._composition_update_inspector_context()
                    return

        try:
            from src.v4.text_anomalies import text_issue_still_present
            still_present = bool(text_issue_still_present(self.session.book, problem))
        except Exception as exc:
            state["notice"] = str(exc)
            self._composition_update_inspector_context()
            return

        # Toujours relire l'état courant : l'utilisateur peut avoir déplacé ou
        # redimensionné la zone directement sur la page avant de vérifier.
        element = self._composition_text_problem_element(problem)
        if isinstance(element, dict):
            payload = element.get("payload", {})
            result["after_text"] = str(payload.get("text", "") or "") if isinstance(payload, dict) else ""
            result["geometry"] = dict(element.get("geometry", {}) or {})

        if still_present:
            state["draft_text"] = str(result.get("after_text", draft_text) or "")
            state["notice"] = (
                "Le problème est encore présent. Modifiez le texte ou la zone sur la page, puis vérifiez de nouveau."
            )
            canvas = self.__dict__.get("_composition_editor_canvas")
            if canvas is not None:
                self._draw_page(canvas)
            self._composition_update_inspector_context()
            return

        before_excerpt, after_excerpt = self._composition_text_change_excerpt(
            str(state.get("original_text", "") or ""), str(result.get("after_text", "") or "")
        )
        if not str(result.get("before_line", "") or ""):
            result["before_line"] = before_excerpt
        if not str(result.get("after_line", "") or ""):
            result["after_line"] = after_excerpt
        result["kind"] = "manual"

        remaining = self._composition_text_problem_entries()
        current_index = int(getattr(self, "_composition_text_problem_index", 0) or 0)
        next_index = current_index if current_index < len(remaining) else 0
        self._composition_text_problem_index = next_index if remaining else 0
        self._composition_text_manual_state = None
        self._composition_text_inline_notice = ""
        self._composition_text_correction_review_state = {
            "key": str(state.get("key", "") or ""),
            "page_id": str(state.get("page_id", "") or ""),
            "element_id": str(state.get("element_id", "") or ""),
            "geometry": dict(problem.get("geometry") or {}),
            "problem_geometry": dict(problem.get("geometry") or {}),
            "correction_geometry": dict(result.get("geometry") or problem.get("geometry") or {}),
            "problem": dict(problem),
            "result": dict(result),
            "remaining_count": len(remaining),
            "next_index": next_index,
            "manual": True,
            "manual_snapshot": state,
        }
        canvas = self.__dict__.get("_composition_editor_canvas")
        if canvas is not None:
            self._draw_page(canvas)
        self._composition_update_inspector_context()

    def _composition_text_finish_correction_review(self) -> None:
        review = self._composition_text_correction_review()
        self._composition_text_correction_review_state = None
        self._composition_text_manual_state = None
        self._composition_text_inline_notice = ""
        problems = self._composition_text_problem_entries()
        if problems:
            wanted = int((review or {}).get("next_index", 0) or 0)
            self._composition_text_problem_index = wanted % len(problems)
            self._composition_text_focus_current_problem()
        else:
            self._composition_text_problem_index = 0
            canvas = getattr(self, "_composition_editor_canvas", None)
            if canvas is not None:
                self._draw_page(canvas)
        self._composition_update_inspector_context()

    def _composition_text_undo_review_correction(self) -> None:
        review = self._composition_text_correction_review()
        if review is None:
            return
        key = str(review.get("key", "") or "")
        self._composition_text_correction_review_state = None
        self._composition_text_inline_notice = ""

        if bool(review.get("manual")):
            snapshot = review.get("manual_snapshot")
            if isinstance(snapshot, dict):
                self._composition_text_restore_manual_snapshot(snapshot)
        elif self.session is not None and self.session.can_undo:
            # Les corrections automatiques sûres restent une transaction simple.
            self._composition_undo()

        problems = self._composition_text_problem_entries()
        for index, item in enumerate(problems):
            if str(item.get("key", "") or "") == key:
                self._composition_text_problem_index = index
                break
        self._composition_text_focus_current_problem()
        self._composition_update_inspector_context()

    @staticmethod
    def _composition_text_correction_summary(kind: str) -> str:
        return {
            "double_space": "L'espace en trop a été supprimé.",
            "space_before_punctuation": "L'espace inutile avant le signe a été supprimé.",
            "missing_space_after_punctuation": "L'espace manquant après le signe a été ajouté.",
            "text_outside_margins": "Le texte a été replacé à l'intérieur des marges.",
            "text_too_close_edge": "Le texte a été replacé dans la zone de lecture.",
            "text_not_justified": "Le paragraphe a été justifié.",
            "hyphenation": "La césure a été retirée et le passage recomposé.",
            "style_outlier": "Le texte a retrouvé la mise en forme générale du livre.",
            "title_orphan": "Le titre a été rattaché au texte qu'il annonce.",
            "orphan_line": "Le changement de page a été rééquilibré pour garder plusieurs lignes ensemble.",
            "widow": "Le changement de page a été rééquilibré pour garder plusieurs lignes ensemble.",
            "manual": "Votre correction a été vérifiée : TomeLinea ne retrouve plus ce problème.",
        }.get(str(kind or "").lower(), "La correction proposée a été appliquée.")

    def _composition_text_decide_problem(self, decision: str) -> None:
        problem, _problems_before = self._composition_text_current_problem()
        if problem is None:
            return

        decision = "corrected" if str(decision) == "corrected" else "ignored"
        key = str(problem.get("key", "") or "")
        current_index = int(getattr(self, "_composition_text_problem_index", 0) or 0)

        if decision == "corrected":
            try:
                from src.v4.text_engine import correct_after_approval, correction_supported
            except Exception as exc:
                self._composition_text_inline_notice = str(exc)
                self._composition_update_inspector_context()
                return

            if not correction_supported(self.session.book, problem):
                self._composition_text_inline_notice = (
                    "TomeLinea a bien repéré ce problème, mais sa correction automatique "
                    "n'est pas encore disponible. Il ne le déclarera pas corrigé."
                )
                self._composition_update_inspector_context()
                return

            def action(project):
                book = project.book
                correction = correct_after_approval(book, problem)
                states = book.metadata.setdefault("text_problem_decisions", {})
                if not isinstance(states, dict):
                    states = {}
                    book.metadata["text_problem_decisions"] = states
                states[key] = "corrected"
                book.metadata["text_reflow_requested"] = True
                project.touch()
                return correction

            label = "Corriger un problème de texte"

        else:
            def action(project):
                from src.v4.text_engine import accept_specific_exception
                accept_specific_exception(project.book, problem)
                project.touch()

            label = "Conserver cette exception de texte"

        try:
            result = self.session.execute(label, action)
        except Exception as exc:
            # Le parcours guidé ne doit jamais être interrompu par une popup.
            self._composition_text_inline_notice = str(exc)
            self._composition_update_inspector_context()
            return

        remaining = self._composition_text_problem_entries()
        if decision == "corrected":
            # Le problème corrigé a disparu de la liste, mais on ne saute pas
            # encore au suivant : l'utilisateur doit d'abord voir le résultat.
            next_index = current_index if current_index < len(remaining) else 0
            self._composition_text_problem_index = next_index if remaining else 0
            self._composition_text_inline_notice = ""
            self._composition_text_correction_review_state = {
                "key": key,
                "page_id": str(problem.get("page_id", "") or ""),
                "element_id": str(problem.get("element_id", "") or ""),
                "geometry": dict(problem.get("geometry") or {}),
                "problem_geometry": dict(problem.get("geometry") or {}),
                "correction_geometry": dict((result or {}).get("geometry") or problem.get("geometry") or {}),
                "problem": dict(problem),
                "result": dict(result or {}),
                "remaining_count": len(remaining),
                "next_index": next_index,
                "manual": False,
            }

            # Rester physiquement sur la page corrigée.
            page_id = str(problem.get("page_id", "") or "")
            if page_id and page_id in self.session.book.pages:
                self._composition_selected_page_ids = {page_id}
                if str(self.session.active_page_id or "") != page_id:
                    self.session.set_active_page(page_id)
                canvas = self.__dict__.get("_composition_editor_canvas")
                if canvas is not None:
                    self._draw_page(canvas)
            self._composition_update_inspector_context()

            # Montrer réellement la correction sans imposer un second clic :
            # le cadre + surlignage restent visibles 1,8 s, puis TomeLinea
            # passe automatiquement au problème suivant. « Annuler » reste
            # disponible pendant cet intervalle.
            review_key = key
            def _advance_after_review():
                current = self._composition_text_correction_review()
                if current is None or str(current.get("key", "") or "") != review_key:
                    return
                self._composition_text_finish_correction_review()
            try:
                self.after(1800, _advance_after_review)
            except Exception:
                # Hôte de test sans boucle Tk : le bouton « Problème suivant »
                # reste le repli déterministe.
                pass
            return

        # « Laisser comme ça » reste une décision : elle peut avancer
        # immédiatement puisque rien n'a été modifié à contrôler visuellement.
        self._composition_text_correction_review_state = None
        self._composition_text_inline_notice = ""
        if remaining:
            self._composition_text_problem_index = min(current_index, len(remaining) - 1)
        else:
            self._composition_text_problem_index = 0
        self._composition_text_focus_current_problem()
        self._composition_update_inspector_context()

    def _composition_render_text_panel(self, host) -> None:
        """Texte grand public : comprendre, corriger, puis constater."""

        review = self._composition_text_correction_review()

        tk.Label(
            host, text="Texte", bg=theme.PANEL, fg=theme.INK,
            font=(theme.FONT_UI, 11, "bold"), anchor="w",
        ).pack(fill="x", padx=18, pady=(10, 6))

        rules_setup = self._composition_render_text_general_rules(host)
        auto_notice = str(self.__dict__.get("_composition_text_auto_notice", "") or "").strip()
        if auto_notice:
            tk.Label(
                host, text=auto_notice, bg=theme.PANEL, fg=theme.ACCENT_BRIGHT,
                wraplength=218, justify="left", anchor="w", font=(theme.FONT_UI, 7, "bold"),
            ).pack(fill="x", padx=18, pady=(0, 7))
            self._composition_text_auto_notice = ""
        if rules_setup:
            return

        manual = self._composition_text_manual_correction()
        if manual is not None:
            problem = manual.get("problem", {}) if isinstance(manual.get("problem"), dict) else {}
            tk.Label(
                host, text="CORRECTION MANUELLE", bg=theme.PANEL, fg=theme.ACCENT_BRIGHT,
                font=(theme.FONT_UI, 9, "bold"), anchor="w",
            ).pack(fill="x", padx=18, pady=(4, 5))
            tk.Label(
                host,
                text=str(problem.get("title", "Ce passage mérite votre attention")),
                bg=theme.PANEL, fg=theme.INK, wraplength=218, justify="left", anchor="w",
                font=(theme.FONT_UI, 9, "bold"),
            ).pack(fill="x", padx=18, pady=(0, 6))
            tk.Label(
                host,
                text=(
                    "Modifiez le texte ci-dessous. Pour un problème de position ou de taille, "
                    "vous pouvez aussi déplacer la zone encadrée directement sur la page."
                ),
                bg=theme.PANEL, fg=theme.MUTED, wraplength=218, justify="left", anchor="w",
                font=(theme.FONT_UI, 8),
            ).pack(fill="x", padx=18, pady=(0, 7))

            if str(problem.get("kind", "") or "") == "style_outlier":
                current_size = float(manual.get("font_size_current", 10.0) or 10.0)
                suggested_size = float(manual.get("font_size_suggested", 10.0) or 10.0)
                tk.Label(
                    host,
                    text=f"Taille actuelle : {current_size:.1f} pt   •   Taille habituelle : {suggested_size:.1f} pt",
                    bg=theme.PANEL, fg=theme.MUTED, wraplength=218, justify="left", anchor="w",
                    font=(theme.FONT_UI, 8),
                ).pack(fill="x", padx=18, pady=(0, 4))
                size_var = tk.StringVar(value=f"{float(manual.get('font_size_draft', current_size)):.1f}")
                size_entry = tk.Entry(
                    host, textvariable=size_var, bg=theme.PANEL_SOFT, fg=theme.INK,
                    insertbackground=theme.INK, relief="flat", bd=0, highlightthickness=1,
                    highlightbackground=theme.PAGE_BORDER, highlightcolor=theme.ACCENT_BRIGHT,
                    font=(theme.FONT_UI, 8),
                )
                size_entry.pack(fill="x", padx=12, pady=(0, 7))
                size_entry.bind(
                    "<KeyRelease>",
                    lambda _event, var=size_var: self._composition_text_capture_manual_font_size(var),
                    add="+",
                )

            editor = tk.Text(
                host, height=10, wrap="word", bg=theme.PANEL_SOFT, fg=theme.INK,
                insertbackground=theme.INK, relief="flat", bd=0, highlightthickness=1,
                highlightbackground=theme.PAGE_BORDER, highlightcolor=theme.ACCENT_BRIGHT,
                font=(theme.FONT_UI, 8), undo=True,
            )
            editor.pack(fill="x", padx=12, pady=(0, 7))
            editor.insert("1.0", str(manual.get("draft_text", "") or ""))
            editor.bind(
                "<KeyRelease>",
                lambda _event, widget=editor: self._composition_text_capture_manual_draft(widget),
                add="+",
            )

            notice = str(manual.get("notice", "") or "").strip()
            if notice:
                tk.Label(
                    host, text=notice, bg=theme.PANEL, fg=theme.WARNING,
                    wraplength=218, justify="left", anchor="w",
                    font=(theme.FONT_UI, 8, "bold"),
                ).pack(fill="x", padx=18, pady=(0, 7))

            actions = tk.Frame(host, bg=theme.PANEL)
            actions.pack(fill="x", padx=12, pady=(0, 8))
            self._button(
                actions, "Annuler", self._composition_text_cancel_manual_correction, compact=True,
            ).pack(side="left", fill="x", expand=True, padx=(0, 4))
            self._button(
                actions, "Vérifier ma correction", self._composition_text_verify_manual_correction,
                compact=True, accent=True,
            ).pack(side="left", fill="x", expand=True, padx=(4, 0))
            return

        if review is not None:
            result = review.get("result", {}) if isinstance(review.get("result"), dict) else {}
            kind = str(result.get("kind", "") or "")

            tk.Label(
                host, text="CORRECTION APPLIQUÉE",
                bg=theme.PANEL, fg=theme.ACCENT_BRIGHT,
                font=(theme.FONT_UI, 9, "bold"), anchor="w",
            ).pack(fill="x", padx=18, pady=(4, 7))

            card = tk.Frame(
                host, bg=theme.PANEL_SOFT, highlightthickness=1,
                highlightbackground=theme.ACCENT_BRIGHT,
            )
            card.pack(fill="x", padx=12, pady=(0, 8))

            tk.Label(
                card, text=self._composition_text_correction_summary(kind),
                bg=theme.PANEL_SOFT, fg=theme.INK,
                wraplength=205, justify="left", anchor="w",
                font=(theme.FONT_UI, 9, "bold"),
            ).pack(fill="x", padx=10, pady=(10, 7))

            before_line = str(result.get("before_line", "") or "").strip()
            after_line = str(result.get("after_line", "") or "").strip()
            if before_line and after_line and before_line != after_line:
                for label, value, color in (
                    ("AVANT", before_line, theme.MUTED),
                    ("APRÈS", after_line, theme.ACCENT_BRIGHT),
                ):
                    tk.Label(
                        card, text=label, bg=theme.PANEL_SOFT, fg=theme.MUTED,
                        font=(theme.FONT_UI, 8, "bold"), anchor="w",
                    ).pack(fill="x", padx=10, pady=(4, 1))
                    tk.Label(
                        card, text=value, bg=theme.PANEL_SOFT, fg=color,
                        wraplength=205, justify="left", anchor="w",
                        font=(theme.FONT_UI, 8, "bold" if label == "APRÈS" else "normal"),
                    ).pack(fill="x", padx=10, pady=(0, 4))

            remaining_count = int(review.get("remaining_count", 0) or 0)
            tk.Label(
                card,
                text=(
                    f"Il reste {remaining_count} problème{'s' if remaining_count != 1 else ''} à examiner."
                    if remaining_count
                    else "Tous les problèmes détectés ont été examinés."
                ),
                bg=theme.PANEL_SOFT, fg=theme.MUTED, wraplength=205,
                justify="left", anchor="w", font=(theme.FONT_UI, 8),
            ).pack(fill="x", padx=10, pady=(5, 10))

            actions = tk.Frame(host, bg=theme.PANEL)
            actions.pack(fill="x", padx=12, pady=(0, 8))
            self._button(
                actions, "Annuler", self._composition_text_undo_review_correction, compact=True,
            ).pack(side="left", fill="x", expand=True, padx=(0, 4))
            self._button(
                actions,
                "Problème suivant" if remaining_count else "Terminer",
                self._composition_text_finish_correction_review,
                compact=True, accent=True,
            ).pack(side="left", fill="x", expand=True, padx=(4, 0))
            return

        problem, problems = self._composition_text_current_problem()

        if problem is None:
            tk.Label(
                host,
                text="Aucun problème de texte à examiner.",
                bg=theme.PANEL, fg=theme.INK,
                wraplength=210, justify="left",
                font=(theme.FONT_UI, 9, "bold"),
            ).pack(anchor="w", padx=18, pady=(8, 3))
            tk.Label(
                host,
                text="TomeLinea n'a rien repéré qui demande votre décision.",
                bg=theme.PANEL, fg=theme.MUTED,
                wraplength=210, justify="left",
                font=(theme.FONT_UI, 8),
            ).pack(anchor="w", padx=18, pady=(0, 8))
            return

        tk.Label(
            host, text="ANOMALIES À EXAMINER", bg=theme.PANEL, fg=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 8, "bold"), anchor="w",
        ).pack(fill="x", padx=18, pady=(3, 2))

        nav = tk.Frame(host, bg=theme.PANEL)
        nav.pack(fill="x", padx=18, pady=(1, 8))
        self._button(
            nav, "‹", lambda: self._composition_text_move_problem(-1), compact=True,
        ).pack(side="left")
        tk.Label(
            nav,
            text=f"Problème {self._composition_text_problem_index + 1} sur {len(problems)}",
            bg=theme.PANEL, fg=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 8, "bold"),
        ).pack(side="left", expand=True)
        self._button(
            nav, "›", lambda: self._composition_text_move_problem(1), compact=True,
        ).pack(side="right")

        card = tk.Frame(host, bg=theme.PANEL_SOFT, highlightthickness=1, highlightbackground=theme.ACCENT_BRIGHT)
        card.pack(fill="x", padx=12, pady=(0, 8))

        def heading(value):
            tk.Label(
                card, text=value, bg=theme.PANEL_SOFT, fg=theme.MUTED,
                font=(theme.FONT_UI, 8, "bold"), anchor="w",
            ).pack(fill="x", padx=10, pady=(9, 2))

        heading("CE QUI SE PASSE")
        term = str(problem.get("term", "") or "").strip()
        title = str(problem.get("title", "") or "").strip()
        if term:
            title = f"{title} ({term})"
        tk.Label(
            card, text=title, bg=theme.PANEL_SOFT, fg=theme.INK,
            wraplength=205, justify="left", anchor="w",
            font=(theme.FONT_UI, 9, "bold"),
        ).pack(fill="x", padx=10, pady=(0, 4))

        heading("POURQUOI TOMELINEA LE SIGNALE")
        tk.Label(
            card, text=str(problem.get("why", "")), bg=theme.PANEL_SOFT, fg=theme.INK,
            wraplength=205, justify="left", anchor="w", font=(theme.FONT_UI, 8),
        ).pack(fill="x", padx=10, pady=(0, 4))

        heading("CE QUE TOMELINEA PROPOSE")
        tk.Label(
            card, text=str(problem.get("proposal", "")), bg=theme.PANEL_SOFT, fg=theme.INK,
            wraplength=205, justify="left", anchor="w", font=(theme.FONT_UI, 8),
        ).pack(fill="x", padx=10, pady=(0, 10))

        try:
            from src.v4.text_anomalies import safe_text_correction_supported
            can_correct = bool(safe_text_correction_supported(problem, self.session.book))
        except Exception:
            can_correct = False

        notice = str(self.__dict__.get("_composition_text_inline_notice", "") or "").strip()
        if not can_correct and not notice:
            notice = (
                "TomeLinea a repéré ce problème. La correction automatique de ce cas "
                "n'est pas encore disponible ; le problème reste donc à traiter."
            )
        if notice:
            tk.Label(
                host, text=notice, bg=theme.PANEL,
                fg=(theme.WARNING if can_correct else theme.MUTED),
                wraplength=218, justify="left", anchor="w",
                font=(theme.FONT_UI, 8, "bold" if can_correct else "normal"),
            ).pack(fill="x", padx=18, pady=(0, 8))

        actions = tk.Frame(host, bg=theme.PANEL)
        actions.pack(fill="x", padx=12, pady=(0, 8))
        self._button(
            actions, "Corriger", lambda: self._composition_text_decide_problem("corrected"),
            compact=True, accent=True, enabled=can_correct,
        ).pack(side="left", fill="x", expand=True, padx=(0, 4))
        self._button(
            actions, "Laisser comme ça", lambda: self._composition_text_decide_problem("ignored"),
            compact=True,
        ).pack(side="left", fill="x", expand=True, padx=(4, 0))

    def _composition_draw_text_problem_highlight(self, canvas: tk.Canvas) -> None:
        """Cadre = anomalie d'origine ; surlignage = résultat de la correction."""

        canvas.delete("composition_text_problem")
        canvas.delete("composition_text_correction")

        if self._composition_current_tool() != "text":
            return

        review = self._composition_text_correction_review()
        if review is not None:
            page_id = str(review.get("page_id", "") or "")
            problem_geometry = review.get("problem_geometry") or review.get("geometry")
            correction_geometry = review.get("correction_geometry") or problem_geometry
            correction_mode = True
        else:
            problem, _problems = self._composition_text_current_problem()
            if problem is None:
                return
            page_id = str(problem.get("page_id", "") or "")
            problem_geometry = problem.get("geometry")
            correction_geometry = None
            correction_mode = False

        if page_id != str(self.session.active_page_id or ""):
            return
        view = getattr(self, "_composition_page_view", None)
        if not isinstance(view, dict):
            return

        def box(geometry):
            if not isinstance(geometry, dict):
                return None
            try:
                scale = float(view["scale"])
                x = float(view["x"]) + float(geometry.get("x_mm", 0.0) or 0.0) * scale
                y = float(view["y"]) + float(geometry.get("y_mm", 0.0) or 0.0) * scale
                w = max(8.0, float(geometry.get("width_mm", 0.0) or 0.0) * scale)
                h = max(8.0, float(geometry.get("height_mm", 0.0) or 0.0) * scale)
                return x, y, w, h
            except (KeyError, TypeError, ValueError):
                return None

        original = box(problem_geometry)
        if original is None:
            return
        x, y, w, h = original
        canvas.create_rectangle(
            x - 5, y - 5, x + w + 5, y + h + 5,
            fill="", outline=theme.ACCENT_BRIGHT, width=4,
            tags=("composition_text_problem",),
        )

        if correction_mode:
            corrected = box(correction_geometry) or original
            cx, cy, cw, ch = corrected
            canvas.create_rectangle(
                cx - 1, cy - 1, cx + cw + 1, cy + ch + 1,
                fill="#F3D77A", stipple="gray25", outline="#C8A94D", width=2,
                tags=("composition_text_correction",),
            )
            canvas.create_text(
                cx, cy - 8, text="CORRECTION APPLIQUÉE", anchor="sw",
                fill=theme.ACCENT_BRIGHT, font=(theme.FONT_UI, 9, "bold"),
                tags=("composition_text_correction",),
            )
            canvas.tag_raise("composition_text_problem")
            canvas.tag_raise("composition_text_correction")
            return

        canvas.create_text(
            x, y - 8, text="PROBLÈME ICI", anchor="sw",
            fill=theme.ACCENT_BRIGHT, font=(theme.FONT_UI, 9, "bold"),
            tags=("composition_text_problem",),
        )
        canvas.tag_raise("composition_text_problem")

    def _composition_current_tool(
        self,
    ) -> str:
        """Retourne l'onglet d'outil actuellement prioritaire."""

        if bool(getattr(self, "_composition_book_state_open", False)):
            tool = "book"
        elif bool(getattr(self, "_composition_constraints_open", False)):
            tool = "constraints"
        elif bool(getattr(self, "_composition_pages_open", False)):
            tool = "pages"
        else:
            tool = str(
                getattr(self, "_composition_active_tool", "book")
                or "book"
            )

        if tool not in {
            "book",
            "constraints",
            "pages",
            "text",
            "layout",
            "control",
        }:
            tool = "book"

        self._composition_active_tool = tool
        return tool

    def _composition_activate_tool(
        self,
        tool: str,
    ) -> None:
        """Change d'outil en un clic, dans l'ordre de construction du Livre."""

        tool = str(tool or "book")
        if tool not in {
            "book",
            "constraints",
            "pages",
            "text",
            "layout",
            "control",
        }:
            tool = "book"

        self._composition_active_tool = tool
        self._composition_book_state_open = (tool == "book")
        self._composition_constraints_open = (tool == "constraints")
        self._composition_pages_open = (tool == "pages")

        self._composition_content_open = False
        self._composition_text_flow_open = False

        if tool != "book":
            self._composition_book_state_edit = False
        if tool != "constraints":
            self._composition_constraints_message = ""

        if tool == "text":
            self._composition_text_manual_state = None
            self._composition_text_prepare_rules()

        self._composition_refresh_tool_tabs()
        self._composition_update_inspector_context()
        if tool == "text":
            self.after_idle(self._composition_text_focus_current_problem)

    def _composition_refresh_tool_tabs(
        self,
    ) -> None:
        tabs = getattr(
            self,
            "_composition_tool_tabs",
            {},
        )
        if not isinstance(tabs, dict):
            return

        active = self._composition_current_tool()

        for key, value in tabs.items():
            try:
                canvas, text_id = value
            except Exception:
                continue

            selected = key == active
            background = (
                theme.ACCENT_DARK
                if selected
                else theme.PANEL_ALT
            )
            foreground = (
                theme.WHITE
                if selected
                else theme.MUTED
            )

            try:
                canvas.configure(
                    bg=background,
                )
                canvas.itemconfigure(
                    text_id,
                    fill=foreground,
                )
            except Exception:
                pass


    def _composition_build_tool_rail(
        self,
        parent,
    ):
        """Onglets permanents dans l'ordre pragmatique de construction."""

        rail = tk.Frame(
            parent,
            bg=theme.PANEL_ALT,
            width=72,
        )
        rail.pack_propagate(False)
        self._composition_tool_tabs = {}

        definitions = (
            ("book", "Format", 40),
            ("constraints", "Contraintes", 44),
            ("text", "Texte", 40),
            ("layout", "Images", 40),
        )

        for key, label, height in definitions:
            tab = tk.Canvas(
                rail,
                width=70,
                height=height,
                bg=theme.PANEL_ALT,
                highlightthickness=0,
                bd=0,
                cursor="hand2",
                takefocus=True,
            )
            tab.pack(fill="x", padx=(1, 1), pady=(1, 0))
            text_id = tab.create_text(
                35,
                height / 2,
                text=label,
                width=64,
                justify="center",
                fill=theme.MUTED,
                font=(theme.FONT_UI, 8, "bold"),
            )
            self._composition_tool_tabs[key] = (tab, text_id)

            def activate(_event=None, selected_tool=key):
                self._composition_activate_tool(selected_tool)
                return "break"

            def enter(_event=None, selected_tool=key, selected_tab=tab):
                if self._composition_current_tool() != selected_tool:
                    try:
                        selected_tab.configure(bg=theme.PANEL_SOFT)
                    except Exception:
                        pass

            tab.bind("<Button-1>", activate)
            tab.bind("<Return>", activate)
            tab.bind("<space>", activate)
            tab.bind("<Enter>", enter)
            tab.bind("<Leave>", lambda _event: self._composition_refresh_tool_tabs())

        self._composition_refresh_tool_tabs()
        return rail

    def _composition_center_margin_images(
        self,
    ) -> None:
        """Centre en une seule action toutes les images liées aux marges."""

        def action(project):
            from src.v4.layout_automation import (
                center_margin_images_horizontally,
            )

            book = project.book
            if book is None:
                raise RuntimeError("Livre indisponible.")

            return center_margin_images_horizontally(book)

        try:
            self.session.execute(
                "Centrer les images dans les marges",
                action,
            )
        except Exception:
            return

        self._composition_update_inspector_context()

        canvas = getattr(
            self,
            "_composition_editor_canvas",
            None,
        )
        if canvas is not None:
            self._draw_page(canvas)


    def _composition_render_layout_panel(
        self,
        host,
        active_page_id: str,
    ) -> None:
        """Outils de mise en page : uniquement des actions utiles."""

        tk.Frame(
            host,
            bg=theme.PAGE_BORDER,
            height=1,
        ).pack(
            fill="x",
            padx=18,
            pady=(7, 6),
        )

        tk.Label(
            host,
            text="MISE EN PAGE",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 9, "bold"),
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 8),
        )

        audit = self._composition_audit_book_images()
        total = int(audit.get("total", 0) or 0)
        if total <= 0:
            return

        tk.Label(
            host,
            text="IMAGES",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 8, "bold"),
        ).pack(
            anchor="w",
            padx=18,
            pady=(2, 5),
        )

        self._button(
            host,
            "Centrer dans les marges",
            self._composition_center_margin_images,
            compact=True,
        ).pack(
            fill="x",
            padx=18,
            pady=(0, 5),
        )

        if (
            int(audit.get("limited", 0) or 0) > 0
            or int(audit.get("critical", 0) or 0) > 0
        ):
            self._button(
                host,
                "Contrôler les images",
                self._composition_open_image_quality_palette,
                compact=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(0, 5),
            )


    def _composition_render_control_panel(
        self,
        host,
    ) -> None:
        """Contrôles réels, sans interrompre le travail."""

        tk.Frame(
            host,
            bg=theme.PAGE_BORDER,
            height=1,
        ).pack(
            fill="x",
            padx=18,
            pady=(7, 6),
        )

        tk.Label(
            host,
            text="CONTRÔLE",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                9,
                "bold",
            ),
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 7),
        )

        image_audit = (
            self._composition_audit_book_images()
        )
        image_issues = list(
            image_audit.get(
                "issues",
                (),
            )
            or ()
        )

        page_issues = (
            inside_cover_confirmation_issues(
                self.session.book
            )
        )

        total = (
            len(image_issues)
            + len(page_issues)
        )

        tk.Label(
            host,
            text=(
                f"{total} point"
                f"{'s' if total != 1 else ''} "
                "à contrôler"
            ),
            bg=theme.PANEL,
            fg=(
                theme.ACCENT_BRIGHT
                if total
                else theme.INK
            ),
            font=(
                theme.FONT_UI,
                10,
                "bold",
            ),
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 3),
        )

        tk.Label(
            host,
            text=(
                "Aucun contrôle ne bloque le travail. "
                "Le Visionneur reste le contrôle visuel global du livre."
            ),
            bg=theme.PANEL,
            fg=theme.MUTED,
            wraplength=210,
            justify="left",
            font=(
                theme.FONT_UI,
                8,
            ),
        ).pack(
            anchor="w",
            padx=18,
            pady=(0, 10),
        )

        self._button(
            host,
            "Ouvrir le contrôle",
            self._composition_open_anomalies_palette,
            compact=True,
        ).pack(
            fill="x",
            padx=18,
            pady=(0, 5),
        )
    def _composition_update_inspector_context(
        self,
    ) -> None:

        self._composition_refresh_image_quality_indicator()

        host = getattr(
            self,
            "_composition_inspector_context",
            None,
        )

        if host is None:
            return

        for child in host.winfo_children():
            child.destroy()

        self._composition_geometry_vars = None
        self.after_idle(
            self._composition_finalize_inspector_context
        )

        page = self.session.active_page
        element = self._composition_selected_element()

        active_tool = self._composition_current_tool()
        self._composition_refresh_tool_tabs()

        selected_page_ids = (
            self._composition_selected_page_ids_in_order()
        )
        active_page_id = str(
            self.session.active_page_id
            or ""
        )

        if (
            active_page_id
            and active_page_id not in selected_page_ids
            and page is not None
        ):
            selected_page_ids = [
                active_page_id
            ]

        def render_page_summary() -> None:
            if page is None:
                return

            if is_cover_face(page):
                summary = cover_label(page)
                if is_generated_cover_placeholder(page):
                    summary += (
                        " · ? À définir"
                        if is_inside_cover_pending(page)
                        else " · blanche"
                    )
            else:
                summary = (
                    page.title
                    or "Sans titre"
                )
                if page.page_type:
                    summary += (
                        f" · {page.page_type}"
                    )

            prefix = (
                f"{len(selected_page_ids)} PAGES SÉLECTIONNÉES"
                if len(selected_page_ids) > 1
                else "PAGE ACTIVE"
            )

            tk.Label(
                host,
                text=f"{prefix} · {summary}",
                bg=theme.PANEL,
                fg=theme.MUTED,
                wraplength=190,
                justify="left",
                font=(
                    theme.FONT_UI,
                    8,
                    "bold",
                ),
            ).pack(
                anchor="w",
                padx=18,
                pady=(6, 3),
            )

            if is_auto_origin_page(
                page
            ):
                tk.Label(
                    host,
                    text=(
                        "Page automatique · protégée"
                        if page.metadata.get(
                            "automatic_user_protected"
                        )
                        or page.metadata.get(
                            "automatic_retained"
                        )
                        or page.content
                        else "Page automatique"
                    ),
                    bg=theme.PANEL,
                    fg="#E7A3B0",
                    font=(
                        theme.FONT_UI,
                        8,
                        "bold",
                    ),
                ).pack(
                    anchor="w",
                    padx=18,
                    pady=(1, 2),
                )

        # Les onglets restent visibles en permanence. Les outils de livre,
        # contraintes et pages gardent leur contexte même si un objet est
        # sélectionné au centre.
        if active_tool == "book":
            self._composition_set_inspector_tool_priority(
                True
            )
            self._composition_render_book_state_panel(
                host
            )
            return

        if active_tool == "constraints":
            self._composition_set_inspector_tool_priority(
                True
            )
            if page is None:
                return
            render_page_summary()
            self._composition_render_constraints_panel(
                host,
                selected_page_ids,
                active_page_id,
            )
            return

        if active_tool == "text":
            self._composition_set_inspector_tool_priority(
                True
            )
            self._composition_render_text_panel(host)
            return

        if active_tool == "pages":
            self._composition_set_inspector_tool_priority(
                True
            )
            if page is None:
                return
            render_page_summary()
            self._composition_render_pages_panel(
                host,
                selected_page_ids,
                active_page_id,
            )
            return

        if active_tool == "control":
            self._composition_set_inspector_tool_priority(
                True
            )
            render_page_summary()
            self._composition_render_control_panel(
                host
            )
            return

        # Ajuster : sans objet sélectionné, on affiche uniquement les
        # actions générales utiles. Les informations techniques restent
        # internes à TomeLinea.
        if element is None:
            self._composition_set_inspector_tool_priority(
                True
            )
            if page is None:
                return
            render_page_summary()
            self._composition_render_layout_panel(
                host,
                active_page_id,
            )
            return

        self._composition_set_inspector_tool_priority(
            False
        )

        # ======================================================
        # ELEMENT SELECTIONNE
        # ======================================================

        kind = str(
            element.get(
                "kind",
                "",
            )
        ).lower()

        if kind == "text":
            title = "TEXTE"

        elif kind == "image":
            title = "IMAGE"

        elif kind == "document":
            title = "DOCUMENT"

        else:
            title = "\u00c9L\u00c9MENT"

        tk.Label(
            host,
            text="\u00c9L\u00c9MENT S\u00c9LECTIONN\u00c9",
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
            pady=(18, 7),
        )

        tk.Label(
            host,
            text=title,
            bg=theme.PANEL,
            fg=theme.ACCENT_BRIGHT,
            font=(
                theme.FONT_TITLE,
                17,
                "bold",
            ),
        ).pack(
            anchor="w",
            padx=22,
        )

        geometry = element.get(
            "geometry",
            {},
        )

        try:
            gx = float(
                geometry.get(
                    "x_mm",
                    0.0,
                )
            )
            gy = float(
                geometry.get(
                    "y_mm",
                    0.0,
                )
            )
            gw = float(
                geometry.get(
                    "width_mm",
                    0.0,
                )
            )
            gh = float(
                geometry.get(
                    "height_mm",
                    0.0,
                )
            )

        except (
            TypeError,
            ValueError,
        ):
            gx = gy = gw = gh = 0.0

        # ======================================================
        # IMAGE
        # ======================================================

        if kind == "image":

            payload = element.get(
                "payload",
                {},
            )

            px_w = int(
                payload.get(
                    "width_px",
                    0,
                )
                or 0
            )

            px_h = int(
                payload.get(
                    "height_px",
                    0,
                )
                or 0
            )

            if (
                px_w > 0
                and px_h > 0
            ):

                tk.Label(
                    host,
                    text="SOURCE",
                    bg=theme.PANEL,
                    fg=theme.MUTED,
                    font=(
                        theme.FONT_UI,
                        8,
                        "bold",
                    ),
                ).pack(
                    anchor="w",
                    padx=22,
                    pady=(20, 6),
                )

                tk.Label(
                    host,
                    text=(
                        f"{px_w} \u00d7 {px_h} px"
                    ),
                    bg=theme.PANEL,
                    fg=theme.INK,
                    font=(
                        theme.FONT_UI,
                        9,
                    ),
                ).pack(
                    anchor="w",
                    padx=22,
                )

        # ======================================================
        # GEOMETRIE
        # ======================================================

        tk.Label(
            host,
            text="POSITION & DIMENSIONS",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                8,
                "bold",
            ),
        ).pack(
            anchor="w",
            padx=22,
            pady=(20, 6),
        )

        geometry_frame = tk.Frame(
            host,
            bg=theme.PANEL,
        )

        geometry_frame.pack(
            fill="x",
            padx=22,
        )

        values = {
            "x_mm": gx,
            "y_mm": gy,
            "width_mm": gw,
            "height_mm": gh,
        }

        labels = (
            ("X", "x_mm"),
            ("Y", "y_mm"),
            ("L", "width_mm"),
            ("H", "height_mm"),
        )

        variables = {}

        for index, (
            label,
            key,
        ) in enumerate(
            labels
        ):

            row = index // 2
            column = (
                index % 2
            ) * 2

            tk.Label(
                geometry_frame,
                text=label,
                bg=theme.PANEL,
                fg=theme.MUTED,
                font=(
                    theme.FONT_UI,
                    8,
                    "bold",
                ),
            ).grid(
                row=row,
                column=column,
                sticky="w",
                padx=(
                    0,
                    4,
                ),
                pady=3,
            )

            var = tk.StringVar(
                value=(
                    f"{values[key]:.1f}"
                )
            )

            variables[
                key
            ] = var

            entry = tk.Entry(
                geometry_frame,
                textvariable=var,
                width=7,
                bg=theme.WINDOW_DEEP,
                fg=theme.INK,
                insertbackground=theme.INK,
                relief="flat",
                bd=0,
                justify="right",
                font=(
                    theme.FONT_UI,
                    9,
                ),
            )

            entry.grid(
                row=row,
                column=column + 1,
                sticky="w",
                padx=(
                    0,
                    12,
                ),
                pady=3,
            )

        self._composition_geometry_vars = (
            variables
        )

        tk.Button(
            host,
            text="Appliquer dimensions",
            command=(
                self._composition_apply_geometry_edit
            ),
            bg=theme.PANEL,
            fg=theme.INK,
            activebackground=theme.WINDOW_DEEP,
            activeforeground=theme.INK,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(
                theme.FONT_UI,
                8,
            ),
        ).pack(
            anchor="w",
            padx=18,
            pady=(8, 0),
        )

        metadata = element.get(
            "metadata",
            {},
        )

        if metadata.get(
            "source_visual_preserved"
        ):

            tk.Label(
                host,
                text=(
                    "Source originale "
                    "pr\u00e9serv\u00e9e"
                ),
                bg=theme.PANEL,
                fg=theme.MUTED,
                font=(
                    theme.FONT_UI,
                    8,
                ),
            ).pack(
                anchor="w",
                padx=22,
                pady=(14, 0),
            )

        tk.Button(
            host,
            text="D\u00e9s\u00e9lectionner",
            command=(
                self._composition_clear_context_selection
            ),
            bg=theme.PANEL,
            fg=theme.INK,
            activebackground=theme.WINDOW_DEEP,
            activeforeground=theme.INK,
            relief="flat",
            bd=0,
            cursor="hand2",
            font=(
                theme.FONT_UI,
                9,
            ),
        ).pack(
            anchor="w",
            padx=18,
            pady=(22, 12),
        )


    def _composition_update_editor(
        self,
    ) -> None:

        self._composition_update_inspector_context()

        canvas = getattr(
            self,
            "_composition_editor_canvas",
            None,
        )

        if canvas is not None:
            self._draw_page(
                canvas
            )

        # Le choix initial des 2e/3e reste toujours synchronisé avec la page
        # effectivement affichée au centre, y compris après un clic dans le Plan.
        self._composition_render_initial_cover_review_banner()

    def _composition_refresh_after_history(
        self,
        selected_snapshot,
        active_page_id,
    ) -> None:

        # Un Undo/Redo peut invalider le résultat que la carte Texte était en
        # train de montrer : ne jamais conserver un surlignage devenu faux.
        self._composition_text_correction_review_state = None
        self._composition_text_inline_notice = ""
        self._composition_cancel_image_preview()

        self._composition_drag_state = None
        self._composition_live_detach_ids = set()
        self._composition_detached_image_preview_photos = {}

        # Undo/Redo remplace BookV4 par un snapshot profond. Il faut donc
        # reconstruire le Plan, le compteur de pages et l'inspecteur à partir
        # des UUID stables, pas seulement redessiner la page centrale.
        self._composition_refresh_after_structure_change(
            selected_snapshot,
            active_page_id,
        )

        self._composition_refresh_image_quality_indicator()
        self._refresh_history_buttons()


    def _composition_undo(
        self,
        _event=None,
    ):

        if self.session is None or not self.session.can_undo:
            self._refresh_history_buttons()
            return "break"

        selected_snapshot = tuple(
            getattr(
                self,
                "_composition_selected_page_ids",
                (),
            )
        )
        active_page_id = self.session.active_page_id

        try:
            self.session.undo()
        except Exception:
            self._refresh_history_buttons()
            return "break"

        self._composition_refresh_after_history(
            selected_snapshot,
            active_page_id,
        )

        return "break"


    def _composition_redo(
        self,
        _event=None,
    ):

        if self.session is None or not self.session.can_redo:
            self._refresh_history_buttons()
            return "break"

        selected_snapshot = tuple(
            getattr(
                self,
                "_composition_selected_page_ids",
                (),
            )
        )
        active_page_id = self.session.active_page_id

        try:
            self.session.redo()
        except Exception:
            self._refresh_history_buttons()
            return "break"

        self._composition_refresh_after_history(
            selected_snapshot,
            active_page_id,
        )

        return "break"


    def _composition_image_quality_indicator_text(
        self,
        audit=None,
    ) -> str:

        if audit is None:

            audit = (
                self._composition_audit_book_images()
            )

        limited = int(
            audit.get(
                "limited",
                0,
            )
            or 0
        )

        critical = int(
            audit.get(
                "critical",
                0,
            )
            or 0
        )

        if (
            limited <= 0
            and critical <= 0
        ):

            return "Toutes conformes"

        parts = []

        if limited > 0:

            parts.append(
                f"{limited} \u00e0 surveiller"
            )

        if critical > 0:

            parts.append(
                f"{critical} non conforme"
                + (
                    ""
                    if critical == 1
                    else "s"
                )
            )

        return " \u00b7 ".join(
            parts
        )

    def _composition_refresh_image_quality_indicator(
        self,
    ) -> None:

        variable = getattr(
            self,
            "_composition_image_quality_var",
            None,
        )

        try:

            audit = (
                self._composition_audit_book_images()
            )

            if variable is not None:
                variable.set(
                    self._composition_image_quality_indicator_text(
                        audit
                    )
                )

            self._composition_refresh_anomaly_indicator(
                audit
            )

        except Exception:
            pass



    def _composition_anomaly_indicator_text(
        self,
        image_audit=None,
    ) -> str:

        if image_audit is None:
            image_audit = self._composition_audit_book_images()

        page_issues = inside_cover_confirmation_issues(self.session.book)
        total = (
            int(image_audit.get("limited", 0) or 0)
            + int(image_audit.get("critical", 0) or 0)
            + len(page_issues)
        )

        return (
            f"● {total} anomalie"
            + ("" if total == 1 else "s")
        )


    def _composition_anomaly_indicator_color(
        self,
        image_audit=None,
    ) -> str:

        if image_audit is None:
            image_audit = self._composition_audit_book_images()

        critical = int(image_audit.get("critical", 0) or 0)
        limited = int(image_audit.get("limited", 0) or 0)
        page_issues = inside_cover_confirmation_issues(self.session.book)

        if critical > 0:
            return theme.ERROR
        if limited > 0 or page_issues:
            return theme.WARNING
        return theme.ACCENT


    def _composition_refresh_anomaly_indicator(
        self,
        image_audit=None,
    ) -> None:

        variable = getattr(
            self,
            "_composition_anomaly_var",
            None,
        )
        button = getattr(
            self,
            "_composition_anomaly_button",
            None,
        )

        if variable is None and button is None:
            return

        if image_audit is None:
            image_audit = self._composition_audit_book_images()

        if variable is not None:
            try:
                variable.set(
                    self._composition_anomaly_indicator_text(
                        image_audit
                    )
                )
            except Exception:
                pass

        if button is not None:
            try:
                button.configure(
                    fg=self._composition_anomaly_indicator_color(
                        image_audit
                    )
                )
            except Exception:
                pass


    def _composition_focus_image_anomaly(
        self,
        issue,
    ) -> None:

        if not isinstance(issue, dict):
            return

        page_id = str(issue.get("page_id", "") or "")
        element_id = str(issue.get("element_id", "") or "")

        if not page_id:
            return

        try:
            self._activate_page(page_id)
        except Exception:
            try:
                self.session.set_active_page(page_id)
                self._composition_update_editor()
            except Exception:
                return

        if element_id:
            try:
                self.session.set_selection(
                    [element_id],
                    include_associated=False,
                )
                self._composition_update_inspector_context()
                canvas = getattr(
                    self,
                    "_composition_editor_canvas",
                    None,
                )
                if canvas is not None:
                    self._draw_page(canvas)
            except Exception:
                pass


    def _composition_focus_page_anomaly(
        self,
        issue,
    ) -> None:

        if not isinstance(issue, dict):
            return
        face = str(issue.get("face", "") or "")
        if face not in {INSIDE_FRONT_COVER, INSIDE_BACK_COVER}:
            return
        self._composition_focus_inside_cover_candidate(face)



    def _composition_open_anomalies_palette(
        self,
    ) -> None:

        image_audit = self._composition_audit_book_images()
        image_issues = list(
            image_audit.get("issues", ()) or ()
        )

        page_issues = inside_cover_confirmation_issues(self.session.book)

        categories = {
            "images": image_issues,
            "pages": page_issues,
            "texte": [],
            "autres": [],
        }

        total = sum(len(items) for items in categories.values())

        previous = getattr(
            self,
            "_composition_anomalies_palette",
            None,
        )
        if previous is not None:
            try:
                if previous.winfo_exists():
                    previous.destroy()
            except Exception:
                pass

        window = tk.Toplevel(self)
        self._composition_anomalies_palette = window
        window.overrideredirect(True)
        window.configure(bg=theme.PAGE_BORDER)
        window.transient(self)

        palette_width = 470
        palette_height = 350
        window.minsize(palette_width, palette_height)
        window.maxsize(palette_width, palette_height)

        try:
            self.update_idletasks()
            root_x = int(self.winfo_rootx())
            root_y = int(self.winfo_rooty())
            root_w = int(self.winfo_width())
            screen_w = int(self.winfo_screenwidth())
            screen_h = int(self.winfo_screenheight())
            pos_x = root_x + max(20, (root_w - palette_width) // 2)
            pos_y = root_y + 105
            pos_x = max(0, min(pos_x, screen_w - palette_width))
            pos_y = max(0, min(pos_y, screen_h - palette_height - 30))
        except Exception:
            pos_x = 100
            pos_y = 100

        window.geometry(
            f"{palette_width}x{palette_height}+{pos_x}+{pos_y}"
        )

        outer = tk.Frame(window, bg=theme.PANEL)
        outer.pack(fill="both", expand=True, padx=1, pady=1)

        title_bar = tk.Frame(
            outer,
            bg=theme.WINDOW_DEEP,
            height=40,
        )
        title_bar.pack(fill="x")
        title_bar.pack_propagate(False)

        tk.Label(
            title_bar,
            text=(
                f"ANOMALIES  ·  {total}"
            ),
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(theme.FONT_UI, 10, "bold"),
        ).pack(side="left", padx=14)

        def close_palette():
            try:
                window.destroy()
            except Exception:
                pass
            self._composition_anomalies_palette = None

        tk.Button(
            title_bar,
            text="✕",
            command=close_palette,
            bg=theme.WINDOW_DEEP,
            fg=theme.MUTED,
            activebackground=theme.PANEL,
            activeforeground=theme.INK,
            relief="flat",
            bd=0,
            cursor="hand2",
            width=3,
            font=(theme.FONT_UI, 11),
        ).pack(side="right", padx=6)

        drag = {}

        def drag_start(event):
            drag["root_x"] = event.x_root
            drag["root_y"] = event.y_root
            drag["x"] = window.winfo_x()
            drag["y"] = window.winfo_y()

        def drag_motion(event):
            if not drag:
                return
            try:
                new_x = drag["x"] + event.x_root - drag["root_x"]
                new_y = drag["y"] + event.y_root - drag["root_y"]
                window.geometry(f"+{new_x}+{new_y}")
            except Exception:
                pass

        title_bar.bind("<Button-1>", drag_start)
        title_bar.bind("<B1-Motion>", drag_motion)

        tab_bar = tk.Frame(outer, bg=theme.PANEL)
        tab_bar.pack(fill="x", padx=12, pady=(10, 6))

        body = tk.Frame(outer, bg=theme.PANEL)
        body.pack(fill="both", expand=True, padx=12, pady=(0, 8))

        footer_var = tk.StringVar(
            value="Les anomalies n'interrompent pas le travail en cours."
        )
        tk.Label(
            outer,
            textvariable=footer_var,
            bg=theme.PANEL,
            fg=theme.MUTED_DARK,
            anchor="w",
            font=(theme.FONT_UI, 8),
        ).pack(fill="x", padx=14, pady=(0, 10))

        tabs = {}

        labels = (
            ("images", "Images"),
            ("pages", "Pages"),
            ("texte", "Texte"),
            ("autres", "Autres"),
        )

        def render(category):
            for child in body.winfo_children():
                child.destroy()

            for key, button in tabs.items():
                active = key == category
                button.configure(
                    bg=(theme.ACCENT_SOFT if active else theme.WINDOW_DEEP),
                    fg=(theme.ACCENT_BRIGHT if active else theme.MUTED),
                )

            items = categories.get(category, [])
            if not items:
                tk.Label(
                    body,
                    text="Aucune anomalie détectée dans cette catégorie.",
                    bg=theme.PANEL,
                    fg=theme.MUTED,
                    anchor="w",
                    justify="left",
                    font=(theme.FONT_UI, 9),
                ).pack(fill="x", pady=18)
                return

            list_canvas = tk.Canvas(
                body,
                bg=theme.PANEL,
                highlightthickness=0,
                bd=0,
            )
            list_canvas.pack(side="left", fill="both", expand=True)

            scrollbar = tk.Scrollbar(
                body,
                orient="vertical",
                command=list_canvas.yview,
                width=8,
                bg=theme.PANEL_ALT,
                troughcolor=theme.PANEL,
                activebackground=theme.PANEL_SOFT,
                relief="flat",
                bd=0,
            )
            rows = tk.Frame(list_canvas, bg=theme.PANEL)
            rows_window = list_canvas.create_window(
                (0, 0),
                window=rows,
                anchor="nw",
            )
            list_canvas.configure(yscrollcommand=scrollbar.set)

            def sync_scroll(_event=None):
                try:
                    list_canvas.configure(scrollregion=list_canvas.bbox("all"))
                except Exception:
                    pass

            def sync_width(event):
                try:
                    list_canvas.itemconfigure(rows_window, width=event.width)
                except Exception:
                    pass

            rows.bind("<Configure>", sync_scroll)
            list_canvas.bind("<Configure>", sync_width)

            if len(items) > 5:
                scrollbar.pack(side="right", fill="y")

            if category == "images":
                for issue in items:
                    status = (
                        "NON CONFORME"
                        if issue.get("status") == "critical"
                        else "À SURVEILLER"
                    )
                    label = (
                        f"Page {issue.get('page_number', '?')}  ·  "
                        f"{status}  ·  {float(issue.get('dpi', 0.0)):.0f} dpi"
                    )
                    tk.Button(
                        rows,
                        text=label,
                        command=(
                            lambda current=issue:
                                self._composition_focus_image_anomaly(current)
                        ),
                        bg=theme.WINDOW_DEEP,
                        fg=theme.INK,
                        activebackground=theme.ACCENT_SOFT,
                        activeforeground=theme.INK,
                        relief="flat",
                        bd=0,
                        cursor="hand2",
                        anchor="w",
                        padx=10,
                        pady=8,
                        font=(theme.FONT_UI, 9),
                    ).pack(fill="x", pady=(0, 4))

            elif category == "pages":
                for issue in items:
                    page_number = issue.get("candidate_page_number")
                    suffix = (
                        f" · page {page_number}"
                        if page_number is not None
                        else ""
                    )
                    tk.Button(
                        rows,
                        text=f"{issue.get('label', 'Couverture à confirmer')}{suffix}",
                        command=(
                            lambda current=issue:
                                self._composition_focus_page_anomaly(current)
                        ),
                        bg=theme.WINDOW_DEEP,
                        fg=theme.INK,
                        activebackground=theme.ACCENT_SOFT,
                        activeforeground=theme.INK,
                        relief="flat",
                        bd=0,
                        cursor="hand2",
                        anchor="w",
                        padx=10,
                        pady=8,
                        font=(theme.FONT_UI, 9),
                    ).pack(fill="x", pady=(0, 4))

        for key, label in labels:
            button = tk.Button(
                tab_bar,
                text=f"{label} ({len(categories[key])})",
                command=lambda current=key: render(current),
                bg=theme.WINDOW_DEEP,
                fg=theme.MUTED,
                activebackground=theme.ACCENT_SOFT,
                activeforeground=theme.INK,
                relief="flat",
                bd=0,
                cursor="hand2",
                padx=9,
                pady=5,
                font=(theme.FONT_UI, 8, "bold"),
            )
            button.pack(side="left", padx=(0, 4))
            tabs[key] = button

        render(
            "images"
            if categories["images"]
            else ("pages" if categories["pages"] else "images")
        )

        try:
            window.lift()
            window.focus_force()
        except Exception:
            pass

    def _composition_open_image_quality_palette(
        self,
    ) -> None:

        audit = (
            self._composition_audit_book_images()
        )

        variable = getattr(
            self,
            "_composition_image_quality_var",
            None,
        )

        if variable is not None:

            variable.set(
                self._composition_image_quality_indicator_text(
                    audit
                )
            )

        if (
            audit.get(
                "limited",
                0,
            )
            or audit.get(
                "critical",
                0,
            )
        ):

            self._composition_show_image_quality_report(
                audit
            )


    def _composition_refresh_center_navigation(
        self,
    ) -> None:
        book = self.session.book
        active_page_id = str(
            self.session.active_page_id
            or ""
        )

        if book is None:
            return

        order = list(
            book.page_order
        )

        try:
            index = order.index(
                active_page_id
            )
        except ValueError:
            index = -1

        label_var = getattr(
            self,
            "_composition_nav_page_var",
            None,
        )
        jump_var = getattr(
            self,
            "_composition_jump_page_var",
            None,
        )

        if label_var is not None:
            if index >= 0:
                label_var.set(
                    f"Page {index + 1} / {len(order)}"
                )
            else:
                label_var.set(
                    f"{len(order)} pages"
                )

        # Le numero dans Aller suit lui aussi la page active. Cela rend
        # visible la synchronisation dans les deux sens sans ajouter de
        # commande ni de repere supplementaire a l'interface.
        if jump_var is not None:
            jump_var.set(
                str(index + 1)
                if index >= 0
                else ""
            )

        previous_button = getattr(
            self,
            "_composition_prev_button",
            None,
        )
        next_button = getattr(
            self,
            "_composition_next_button",
            None,
        )

        try:
            if previous_button is not None:
                previous_button.configure(
                    state=(
                        tk.NORMAL
                        if index > 0
                        else tk.DISABLED
                    )
                )
        except Exception:
            pass

        try:
            if next_button is not None:
                next_button.configure(
                    state=(
                        tk.NORMAL
                        if (
                            index >= 0
                            and index < len(order) - 1
                        )
                        else tk.DISABLED
                    )
                )
        except Exception:
            pass

    def _composition_previous_page(
        self,
    ) -> None:
        book = self.session.book

        if book is None:
            return

        order = list(
            book.page_order
        )
        active = str(
            self.session.active_page_id
            or ""
        )

        try:
            index = order.index(
                active
            )
        except ValueError:
            return

        if index > 0:
            self._activate_page(
                order[index - 1]
            )

    def _composition_next_page(
        self,
    ) -> None:
        book = self.session.book

        if book is None:
            return

        order = list(
            book.page_order
        )
        active = str(
            self.session.active_page_id
            or ""
        )

        try:
            index = order.index(
                active
            )
        except ValueError:
            return

        if index < len(order) - 1:
            self._activate_page(
                order[index + 1]
            )
    def _build_composition_editor(
        self,
        parent,
    ) -> None:

        page = self.session.active_page
        book = self.session.book

        inspector = tk.Frame(
            parent,
            bg=theme.PANEL,
            # 72 px d'onglets explicites + 1 px de séparation
            # + 260 px réellement disponibles pour les outils.
            width=333,
        )

        inspector.pack(
            side="right",
            fill="y",
        )

        inspector.pack_propagate(
            False
        )

        # ======================================================
        # OUTILS — ONGLETS VERTICAUX PERMANENTS
        # ======================================================

        # Les outils retrouvent 260 px utiles. La bande d'onglets
        # explicites (72 px) ne vient plus réduire leur largeur.
        image_audit = self._composition_audit_book_images()
        self._composition_image_quality_var = tk.StringVar(
            value=self._composition_image_quality_indicator_text(
                image_audit
            )
        )
        self._composition_image_quality_block = None

        tool_shell = tk.Frame(
            inspector,
            bg=theme.PANEL,
        )
        tool_shell.pack(
            fill="both",
            expand=True,
        )

        tool_rail = self._composition_build_tool_rail(
            tool_shell
        )
        tool_rail.pack(
            side="left",
            fill="y",
        )

        tk.Frame(
            tool_shell,
            bg=theme.PAGE_BORDER,
            width=1,
        ).pack(
            side="left",
            fill="y",
        )

        # ======================================================
        # INSPECTEUR CONTEXTUEL — ZONE PRIORITAIRE ET DÉFILABLE
        # ======================================================

        context_shell = tk.Frame(
            tool_shell,
            bg=theme.PANEL,
        )
        self._composition_inspector_context_shell = context_shell
        context_shell.pack(
            side="left",
            fill="both",
            expand=True,
        )

        context_canvas = tk.Canvas(
            context_shell,
            bg=theme.PANEL,
            highlightthickness=0,
            bd=0,
        )
        self._composition_inspector_canvas = context_canvas
        context_canvas.pack(
            side="left",
            fill="both",
            expand=True,
        )

        context_scrollbar = tk.Scrollbar(
            context_shell,
            orient="vertical",
            command=context_canvas.yview,
            width=8,
            bg=theme.PANEL_ALT,
            troughcolor=theme.PANEL,
            activebackground=theme.PANEL_SOFT,
            relief="flat",
            bd=0,
        )
        self._composition_inspector_scrollbar = context_scrollbar
        context_canvas.configure(
            yscrollcommand=context_scrollbar.set
        )

        self._composition_inspector_context = tk.Frame(
            context_canvas,
            bg=theme.PANEL,
        )
        context_window = context_canvas.create_window(
            (0, 0),
            window=self._composition_inspector_context,
            anchor="nw",
        )

        def refresh_context_scroll(
            _event=None,
        ):
            try:
                context_canvas.configure(
                    scrollregion=context_canvas.bbox(
                        "all"
                    )
                )
                self.after_idle(
                    self._composition_finalize_inspector_context
                )
            except Exception:
                pass

        def resize_context_inside(
            event,
        ):
            try:
                context_canvas.itemconfigure(
                    context_window,
                    width=event.width,
                )
            except Exception:
                pass

        self._composition_inspector_context.bind(
            "<Configure>",
            refresh_context_scroll,
        )
        context_canvas.bind(
            "<Configure>",
            resize_context_inside,
        )
        context_canvas.bind(
            "<MouseWheel>",
            self._composition_inspector_mousewheel,
        )

        self._composition_update_inspector_context()

        # ======================================================
        # PAGE CENTRALE
        # ======================================================

        center = tk.Frame(
            parent,
            bg=theme.WINDOW,
        )

        center.pack(
            fill="both",
            expand=True,
        )

        if not hasattr(
            self,
            "_composition_zoom_factor",
        ):
            self._composition_zoom_factor = (
                1.0
            )
            self._composition_pan_x = 0.0
            self._composition_pan_y = 0.0

        zoom_bar = tk.Frame(
            center,
            bg=theme.WINDOW,
        )

        zoom_bar.pack(
            fill="x",
            padx=34,
            pady=(0, 7),
        )

        # NAVIGATION PAGE PRECEDENTE / SUIVANTE
        nav_group = tk.Frame(
            zoom_bar,
            bg=theme.WINDOW,
        )
        nav_group.pack(
            side="right",
        )

        self._composition_prev_button = self._toolbar_button(
            nav_group,
            text="‹ Précédente",
            command=self._composition_previous_page,
        )
        self._composition_prev_button.pack(
            side="left",
        )

        self._composition_nav_page_var = tk.StringVar(
            value=""
        )
        tk.Label(
            nav_group,
            textvariable=self._composition_nav_page_var,
            bg=theme.WINDOW,
            fg=theme.MUTED,
            width=14,
            font=(
                theme.FONT_UI,
                8,
                "bold",
            ),
        ).pack(
            side="left",
            padx=6,
        )

        self._composition_next_button = self._toolbar_button(
            nav_group,
            text="Suivante ›",
            command=self._composition_next_page,
        )
        self._composition_next_button.pack(
            side="left",
        )

        self._composition_refresh_center_navigation()

        self._composition_zoom_out_button = self._toolbar_button(
            zoom_bar,
            text="−",
            command=self._composition_zoom_out,
            width=3,
            bold=True,
        )
        self._composition_zoom_out_button.pack(
            side="left",
        )

        self._composition_zoom_var = (
            tk.StringVar(
                value=(
                    f"{int(round(self._composition_zoom_factor * 100))} %"
                )
            )
        )

        tk.Label(
            zoom_bar,
            textvariable=(
                self._composition_zoom_var
            ),
            bg=theme.WINDOW,
            fg=theme.MUTED,
            width=7,
            font=(
                theme.FONT_UI,
                9,
            ),
        ).pack(
            side="left",
        )

        self._composition_zoom_in_button = self._toolbar_button(
            zoom_bar,
            text="+",
            command=self._composition_zoom_in,
            width=3,
            bold=True,
        )
        self._composition_zoom_in_button.pack(
            side="left",
        )

        self._composition_zoom_fit_button = self._toolbar_button(
            zoom_bar,
            text="Ajuster",
            command=self._composition_zoom_reset,
        )
        self._composition_zoom_fit_button.pack(
            side="left",
            padx=(10, 0),
        )

        # Le bandeau principal contient deja Annuler / Retablir.
        # Ici, la barre centrale reste dediee au confort de lecture
        # et aux garde-fous : aucun doublon d'historique.
        self._composition_undo_button = None
        self._composition_redo_button = None

        anomaly_audit = self._composition_audit_book_images()
        self._composition_anomaly_var = tk.StringVar(
            value=self._composition_anomaly_indicator_text(
                anomaly_audit
            )
        )

        self._composition_anomaly_button = self._toolbar_button(
            zoom_bar,
            textvariable=self._composition_anomaly_var,
            command=self._composition_open_anomalies_palette,
            foreground=self._composition_anomaly_indicator_color(
                anomaly_audit
            ),
            bold=True,
        )
        self._composition_anomaly_button.pack(
            side="left",
            padx=(26, 0),
        )

        self._refresh_history_buttons()

        # Bandeau temporaire de validation des 2e/3e de couverture.
        # Il n'occupe de place que pendant la première validation (ou une
        # modification volontaire ultérieure) puis disparaît totalement.
        self._composition_cover_review_banner = tk.Frame(
            center,
            bg=theme.PANEL_ALT,
            highlightthickness=1,
            highlightbackground=theme.WARNING,
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

        self._composition_editor_canvas = (
            canvas
        )

        canvas.bind(
            "<Control-z>",
            self._composition_undo,
        )

        canvas.bind(
            "<Control-y>",
            self._composition_redo,
        )

        canvas.bind(
            "<Control-Shift-Z>",
            self._composition_redo,
        )

        canvas.bind(
            "<Control-Shift-z>",
            self._composition_redo,
        )

        canvas.bind(
            "<Configure>",
            lambda _event:
            self._draw_page(
                canvas
            ),
        )

        # Après l'analyse, les éventuelles décisions de 2e/3e de couverture
        # sont seulement signalées dans Pages ; elles ne bloquent jamais Format.
        self.after_idle(
            self._composition_begin_initial_cover_review_if_needed
        )

    def _composition_text_uses_editorial_flow(
        self,
        element,
    ) -> bool:
        """
        Vrai quand un texte appartient au contenu éditorial du livre.

        Un texte éditorial n'est pas un cadre graphique : il est piloté
        par les règles de texte (marges, styles, retraits, listes, etc.).
        Les fragments issus de l'analyse Source restent utiles au moteur
        pour reconstruire le flux, mais ne sont jamais présentés comme
        des mini-boîtes manipulables.

        Une véritable zone de texte indépendante (fiche, bulle BD,
        cartouche...) peut forcer le mode objet dans ses métadonnées.
        """

        if not isinstance(element, dict):
            return False

        if str(element.get("kind", "")).lower() != "text":
            return False

        metadata = element.get("metadata", {})
        if not isinstance(metadata, dict):
            metadata = {}

        # Une zone explicitement créée comme objet graphique garde ses
        # poignées, y compris dans un Roman.
        if (
            bool(metadata.get("independent_text_zone"))
            or bool(metadata.get("text_box"))
            or str(metadata.get("text_object_mode", "")).lower()
            in {"box", "frame", "independent", "bubble", "cartouche"}
        ):
            return False

        if (
            bool(metadata.get("semantic_text"))
            or str(metadata.get("text_layout_mode", "")).lower()
            in {"flow", "editorial_flow"}
        ):
            return True

        book = getattr(self.session, "book", None)
        kind = str(getattr(getattr(book, "kind", None), "value", getattr(book, "kind", ""))).lower()

        # En BD, le texte est fréquemment spatial (bulle/cartouche).
        # On ne convertit donc pas implicitement tout texte Source en flux.
        if kind == "bande_dessinee":
            return False

        # Les blocs détectés dans une Source sont des fragments d'analyse,
        # pas des objets de composition. TomeLinea les regroupe ensuite par
        # rôle et par flux pour appliquer les règles globales.
        if (
            str(metadata.get("origin", "")).lower() == "analysis_source"
            or str(metadata.get("analysis_key", "")).lower()
            == "fact.layout.text_blocks"
        ):
            return True

        # Dans un Roman, tout texte non déclaré comme zone indépendante
        # appartient par défaut au flux éditorial.
        return kind == "roman"


    def _composition_element_at_canvas_point(
        self,
        event,
    ):
        """
        Retourne l'élément Composition situ? sous le pointeur.

        Les coordonnées Composition sont exprimées en mm.
        On choisit l'élément le plus précis sous le clic :
        en pratique la plus petite zone correspondante.
        Cela évite qu'une grande image de fond masque un texte.
        """

        page = self.session.active_page

        if page is None:
            return None

        view = getattr(
            self,
            "_composition_page_view",
            None,
        )

        if not isinstance(
            view,
            dict,
        ):
            return None

        if (
            view.get("page_id")
            != page.id
        ):
            return None

        scale = float(
            view.get(
                "scale",
                0.0,
            )
            or 0.0
        )

        if scale <= 0:
            return None

        px = float(event.x)
        py = float(event.y)

        page_x = float(
            view["x"]
        )

        page_y = float(
            view["y"]
        )

        page_w = float(
            view["page_w"]
        )

        page_h = float(
            view["page_h"]
        )

        if not (
            page_x <= px <= page_x + page_w
            and page_y <= py <= page_y + page_h
        ):
            return None

        x_mm = (
            px - page_x
        ) / scale

        y_mm = (
            py - page_y
        ) / scale

        candidates = []

        for z_index, element in enumerate(
            page.content
        ):

            if not isinstance(
                element,
                dict,
            ):
                continue

            # Le texte éditorial se sélectionnera comme du texte (caret /
            # plage / rôle) lorsque l'éditeur de texte sera branché. Il ne
            # doit jamais entrer dans le mode objet géométrique.
            if (
                self._composition_text_uses_editorial_flow(element)
                and not self._composition_text_manual_targets_element(element)
            ):
                continue

            geometry = element.get(
                "geometry"
            )

            if not isinstance(
                geometry,
                dict,
            ):
                continue

            try:
                x = float(
                    geometry.get(
                        "x_mm",
                        0.0,
                    )
                )

                y = float(
                    geometry.get(
                        "y_mm",
                        0.0,
                    )
                )

                width = float(
                    geometry.get(
                        "width_mm",
                        0.0,
                    )
                )

                height = float(
                    geometry.get(
                        "height_mm",
                        0.0,
                    )
                )

            except (
                TypeError,
                ValueError,
            ):
                continue

            if (
                width <= 0
                or height <= 0
            ):
                continue

            if (
                x <= x_mm <= x + width
                and y <= y_mm <= y + height
            ):

                area = (
                    width
                    * height
                )

                # À surface identique,
                # préférer le dernier élément
                # de la pile.
                candidates.append(
                    (
                        area,
                        -z_index,
                        element,
                    )
                )

        if not candidates:
            return None

        candidates.sort(
            key=lambda item: (
                item[0],
                item[1],
            )
        )

        return candidates[0][2]


    def _composition_paint_selection_geometry(
        self,
        canvas,
        geometry,
    ) -> None:

        view = getattr(
            self,
            "_composition_page_view",
            None,
        )

        if not isinstance(
            view,
            dict,
        ):
            return

        try:

            scale = float(
                view["scale"]
            )

            left = (
                float(
                    view["x"]
                )
                + float(
                    geometry["x_mm"]
                )
                * scale
            )

            top = (
                float(
                    view["y"]
                )
                + float(
                    geometry["y_mm"]
                )
                * scale
            )

            right = (
                left
                + float(
                    geometry["width_mm"]
                )
                * scale
            )

            bottom = (
                top
                + float(
                    geometry["height_mm"]
                )
                * scale
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            return

        canvas.delete(
            "composition_selection"
        )

        outline = getattr(
            theme,
            "ACCENT",
            "#C7A66A",
        )

        canvas.create_rectangle(
            left,
            top,
            right,
            bottom,
            fill="",
            outline=outline,
            width=1,
            tags=(
                "composition_selection",
            ),
        )

        middle_x = (
            left + right
        ) / 2.0

        middle_y = (
            top + bottom
        ) / 2.0

        positions = {
            "nw": (
                left,
                top,
            ),
            "n": (
                middle_x,
                top,
            ),
            "ne": (
                right,
                top,
            ),
            "e": (
                right,
                middle_y,
            ),
            "se": (
                right,
                bottom,
            ),
            "s": (
                middle_x,
                bottom,
            ),
            "sw": (
                left,
                bottom,
            ),
            "w": (
                left,
                middle_y,
            ),
        }

        # Poignees discretes visuellement, tout en gardant une zone
        # de clic confortable pour ne pas degrader la manipulation.
        radius = 3.0

        hit_radius = 9.0

        regions = {}

        handle_fill = getattr(
            theme,
            "WINDOW",
            "#252525",
        )

        for handle, (
            cx,
            cy,
        ) in positions.items():

            canvas.create_rectangle(
                cx - radius,
                cy - radius,
                cx + radius,
                cy + radius,
                fill=handle_fill,
                outline=outline,
                width=1,
                tags=(
                    "composition_selection",
                    "composition_handle",
                ),
            )

            regions[handle] = (
                cx - hit_radius,
                cy - hit_radius,
                cx + hit_radius,
                cy + hit_radius,
            )

        self._composition_handle_regions = (
            regions
        )


    def _composition_handle_at_canvas_point(
        self,
        event,
    ):

        regions = getattr(
            self,
            "_composition_handle_regions",
            None,
        )

        if not isinstance(
            regions,
            dict,
        ):
            return None

        px = float(
            event.x
        )

        py = float(
            event.y
        )

        for handle, region in (
            regions.items()
        ):

            (
                left,
                top,
                right,
                bottom,
            ) = region

            if (
                left <= px <= right
                and top <= py <= bottom
            ):
                return handle

        return None


    def _composition_drag_geometry(
        self,
        state,
        event,
    ):

        base = dict(
            state["geometry"]
        )

        scale = max(
            0.0001,
            float(
                state["scale"]
            ),
        )

        dx = (
            float(
                event.x
            )
            - float(
                state["start_x"]
            )
        ) / scale

        dy = (
            float(
                event.y
            )
            - float(
                state["start_y"]
            )
        ) / scale

        mode = state[
            "mode"
        ]

        if mode == "move":

            base["x_mm"] = (
                float(
                    base["x_mm"]
                )
                + dx
            )

            base["y_mm"] = (
                float(
                    base["y_mm"]
                )
                + dy
            )

            return base

        handle = str(
            state.get(
                "handle",
                "",
            )
        )

        x = float(
            base["x_mm"]
        )

        y = float(
            base["y_mm"]
        )

        width = float(
            base["width_mm"]
        )

        height = float(
            base["height_mm"]
        )

        kind = str(
            state.get(
                "kind",
                "",
            )
        ).lower()

        minimum = 0.5

        # ----------------------------------------------------
        # TEXTE :
        # les angles sont libres pour permettre de remodeler
        # reellement le paragraphe.
        # ----------------------------------------------------

        if kind == "text":

            if "e" in handle:
                width = max(
                    minimum,
                    width + dx,
                )

            if "w" in handle:

                right = (
                    x + width
                )

                width = max(
                    minimum,
                    width - dx,
                )

                x = (
                    right - width
                )

            if "s" in handle:
                height = max(
                    minimum,
                    height + dy,
                )

            if "n" in handle:

                bottom = (
                    y + height
                )

                height = max(
                    minimum,
                    height - dy,
                )

                y = (
                    bottom - height
                )

        # ----------------------------------------------------
        # AUTRES CONTENEURS :
        # cotes libres, angles proportionnels.
        # ----------------------------------------------------

        else:

            if handle == "e":

                width = max(
                    minimum,
                    width + dx,
                )

            elif handle == "w":

                right = (
                    x + width
                )

                width = max(
                    minimum,
                    width - dx,
                )

                x = (
                    right - width
                )

            elif handle == "s":

                height = max(
                    minimum,
                    height + dy,
                )

            elif handle == "n":

                bottom = (
                    y + height
                )

                height = max(
                    minimum,
                    height - dy,
                )

                y = (
                    bottom - height
                )

            else:

                if handle in (
                    "ne",
                    "se",
                ):
                    candidate_width = (
                        width + dx
                    )
                else:
                    candidate_width = (
                        width - dx
                    )

                if handle in (
                    "sw",
                    "se",
                ):
                    candidate_height = (
                        height + dy
                    )
                else:
                    candidate_height = (
                        height - dy
                    )

                scale_x = (
                    candidate_width
                    / width
                )

                scale_y = (
                    candidate_height
                    / height
                )

                if abs(
                    scale_x - 1.0
                ) >= abs(
                    scale_y - 1.0
                ):
                    factor = scale_x
                else:
                    factor = scale_y

                factor = max(
                    minimum / width,
                    minimum / height,
                    factor,
                )

                new_width = (
                    width * factor
                )

                new_height = (
                    height * factor
                )

                if "w" in handle:
                    x = (
                        x
                        + width
                        - new_width
                    )

                if "n" in handle:
                    y = (
                        y
                        + height
                        - new_height
                    )

                width = new_width
                height = new_height

        base["x_mm"] = x
        base["y_mm"] = y
        base["width_mm"] = width
        base["height_mm"] = height

        return base


    def _composition_preview_geometry_vars(
        self,
        geometry,
    ) -> None:

        variables = getattr(
            self,
            "_composition_geometry_vars",
            None,
        )

        if not isinstance(
            variables,
            dict,
        ):
            return

        for key in (
            "x_mm",
            "y_mm",
            "width_mm",
            "height_mm",
        ):

            variable = variables.get(
                key
            )

            if variable is None:
                continue

            try:

                variable.set(
                    f"{float(geometry[key]):.2f}"
                )

            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                pass


    def _composition_pointer_hover(
        self,
        event,
    ):

        if bool(
            getattr(
                self,
                "_composition_space_pan_active",
                False,
            )
        ):
            return

        canvas = getattr(
            self,
            "_composition_editor_canvas",
            None,
        )

        if canvas is None:
            return

        handle = (
            self._composition_handle_at_canvas_point(
                event
            )
        )

        cursors = {
            "n": "sb_v_double_arrow",
            "s": "sb_v_double_arrow",
            "e": "sb_h_double_arrow",
            "w": "sb_h_double_arrow",
            "nw": "size_nw_se",
            "se": "size_nw_se",
            "ne": "size_ne_sw",
            "sw": "size_ne_sw",
        }

        cursor = (
            cursors.get(
                handle,
                "",
            )
        )

        try:
            canvas.configure(
                cursor=cursor
            )
        except Exception:
            pass


    def _composition_pointer_press(
        self,
        event,
    ):

        try:
            event.widget.focus_set()
        except Exception:
            pass

        if bool(
            getattr(
                self,
                "_composition_space_pan_active",
                False,
            )
        ):

            return self._composition_pan_start(
                event
            )

        # Dans une double page, un clic sur l'autre moitié la rend
        # active sans quitter la vue de l'ouverture.
        clicked_page_id = self._composition_page_id_at_canvas_point(
            event
        )
        active_page_id = self.session.active_page_id

        if (
            clicked_page_id is not None
            and clicked_page_id != active_page_id
        ):
            self.session.clear_selection()
            self.session.set_active_page(
                clicked_page_id
            )
            self._composition_selected_page_ids = {
                clicked_page_id
            }
            self._composition_update_plan_selection()
            self._composition_update_inspector_context()

            canvas = getattr(
                self,
                "_composition_editor_canvas",
                None,
            )
            if canvas is not None:
                self._draw_page(
                    canvas
                )
            return "break"

        selected = (
            self._composition_selected_element()
        )

        handle = (
            self._composition_handle_at_canvas_point(
                event
            )
        )

        if (
            handle is not None
            and selected is not None
            and (
                not self._composition_text_uses_editorial_flow(selected)
                or self._composition_text_manual_targets_element(selected)
            )
        ):

            geometry = selected.get(
                "geometry"
            )

            view = getattr(
                self,
                "_composition_page_view",
                None,
            )

            if (
                isinstance(
                    geometry,
                    dict,
                )
                and isinstance(
                    view,
                    dict,
                )
            ):

                self._composition_drag_state = {
                    "mode": "resize",
                    "handle": handle,
                    "element_id": str(
                        selected.get(
                            "id",
                            "",
                        )
                    ),
                    "kind": str(
                        selected.get(
                            "kind",
                            "",
                        )
                    ).lower(),
                    "geometry": dict(
                        geometry
                    ),
                    "start_x": float(
                        event.x
                    ),
                    "start_y": float(
                        event.y
                    ),
                    "scale": float(
                        view["scale"]
                    ),
                    "moved": False,
                }

                return "break"

        element = (
            self._composition_element_at_canvas_point(
                event
            )
        )

        if element is None:

            self.session.clear_selection()

            self._composition_drag_state = (
                None
            )

            self._composition_update_inspector_context()

            canvas = getattr(
                self,
                "_composition_editor_canvas",
                None,
            )

            if canvas is not None:
                self._draw_page(
                    canvas
                )

            return "break"

        element_id = str(
            element.get(
                "id",
                "",
            )
        )

        if not element_id:
            return "break"

        self.session.set_selection(
            [element_id],
            include_associated=False,
        )

        kind = str(
            element.get(
                "kind",
                "",
            )
        ).lower()

        if kind in (
            "image",
            "text",
        ):

            self._composition_live_detach_ids = {
                element_id
            }

        else:

            self._composition_live_detach_ids = set()

        self._composition_update_inspector_context()

        canvas = getattr(
            self,
            "_composition_editor_canvas",
            None,
        )

        if canvas is not None:
            self._draw_page(
                canvas
            )

        geometry = element.get(
            "geometry"
        )

        view = getattr(
            self,
            "_composition_page_view",
            None,
        )

        if (
            isinstance(
                geometry,
                dict,
            )
            and isinstance(
                view,
                dict,
            )
        ):

            self._composition_drag_state = {
                "mode": "move",
                "handle": None,
                "element_id": element_id,
                "kind": str(
                    element.get(
                        "kind",
                        "",
                    )
                ).lower(),
                "geometry": dict(
                    geometry
                ),
                "start_x": float(
                    event.x
                ),
                "start_y": float(
                    event.y
                ),
                "scale": float(
                    view["scale"]
                ),
                "moved": False,
            }

        return "break"


    def _composition_preview_detached_image(
        self,
        state,
        geometry,
    ) -> None:

        canvas = getattr(
            self,
            "_composition_editor_canvas",
            None,
        )

        view = getattr(
            self,
            "_composition_page_view",
            None,
        )

        if (
            canvas is None
            or not isinstance(
                view,
                dict,
            )
        ):
            return

        element_id = str(
            state.get(
                "element_id",
                "",
            )
        )

        if not element_id:
            return

        items = getattr(
            self,
            "_composition_detached_image_items",
            {},
        )

        if not isinstance(
            items,
            dict,
        ):
            return

        canvas_id = items.get(
            element_id
        )

        if canvas_id is None:
            return

        try:

            scale = float(
                view["scale"]
            )

            left = (
                float(
                    view["x"]
                )
                + float(
                    geometry["x_mm"]
                )
                * scale
            )

            top = (
                float(
                    view["y"]
                )
                + float(
                    geometry["y_mm"]
                )
                * scale
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            return

        # La position reste strictement collee
        # au pointeur, sans aucun traitement image.
        try:

            canvas.coords(
                canvas_id,
                left,
                top,
            )

        except Exception:
            return

        if (
            state.get(
                "mode"
            )
            != "resize"
        ):
            return

        # Ne conserver que la derniere demande.
        self._composition_image_preview_pending = {
            "state":
                state,

            "geometry":
                dict(
                    geometry
                ),
        }

        # Un seul recalcul peut etre programme.
        if getattr(
            self,
            "_composition_image_preview_after",
            None,
        ) is None:

            self._composition_image_preview_after = (
                canvas.after(
                    20,
                    self._composition_flush_image_preview,
                )
            )

    def _composition_flush_image_preview(
        self,
    ) -> None:

        self._composition_image_preview_after = (
            None
        )

        pending = getattr(
            self,
            "_composition_image_preview_pending",
            None,
        )

        self._composition_image_preview_pending = (
            None
        )

        if not isinstance(
            pending,
            dict,
        ):
            return

        state = pending.get(
            "state"
        )

        geometry = pending.get(
            "geometry"
        )

        # Si le geste est termine entre-temps,
        # aucun vieux preview ne doit reapparaitre.
        if (
            state is not getattr(
                self,
                "_composition_drag_state",
                None,
            )
            or not isinstance(
                geometry,
                dict,
            )
        ):
            return

        canvas = getattr(
            self,
            "_composition_editor_canvas",
            None,
        )

        view = getattr(
            self,
            "_composition_page_view",
            None,
        )

        if (
            canvas is None
            or not isinstance(
                view,
                dict,
            )
        ):
            return

        element_id = str(
            state.get(
                "element_id",
                "",
            )
        )

        items = getattr(
            self,
            "_composition_detached_image_items",
            {},
        )

        sources = getattr(
            self,
            "_composition_detached_image_sources",
            {},
        )

        if (
            not element_id
            or not isinstance(
                items,
                dict,
            )
            or not isinstance(
                sources,
                dict,
            )
        ):
            return

        canvas_id = items.get(
            element_id
        )

        source_image = sources.get(
            element_id
        )

        if (
            canvas_id is None
            or source_image is None
        ):
            return

        try:

            scale = float(
                view["scale"]
            )

            width_px = max(
                1,
                int(
                    round(
                        float(
                            geometry[
                                "width_mm"
                            ]
                        )
                        * scale
                    )
                ),
            )

            height_px = max(
                1,
                int(
                    round(
                        float(
                            geometry[
                                "height_mm"
                            ]
                        )
                        * scale
                    )
                ),
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            return

        # Quelques pixels de difference n'ont aucun
        # interet visuel pendant le geste.
        old_size = state.get(
            "_preview_image_size"
        )

        if (
            isinstance(
                old_size,
                tuple,
            )
            and abs(
                old_size[0]
                - width_px
            ) < 3
            and abs(
                old_size[1]
                - height_px
            ) < 3
        ):
            return

        size = (
            width_px,
            height_px,
        )

        state[
            "_preview_image_size"
        ] = size

        # Construire une seule petite source de travail.
        cache = getattr(
            self,
            "_composition_drag_image_sources",
            None,
        )

        if not isinstance(
            cache,
            dict,
        ):

            cache = {}

            self._composition_drag_image_sources = (
                cache
            )

        entry = cache.get(
            element_id
        )

        source_identity = id(
            source_image
        )

        if (
            not isinstance(
                entry,
                tuple,
            )
            or len(entry) != 2
            or entry[0] != source_identity
        ):

            try:

                drag_source = (
                    source_image.copy()
                )

                drag_source.thumbnail(
                    (
                        1000,
                        1000,
                    ),
                    Image.Resampling.BILINEAR,
                )

                cache[
                    element_id
                ] = (
                    source_identity,
                    drag_source,
                )

            except Exception:
                return

        else:

            drag_source = entry[1]

        try:

            from PIL import ImageOps

            # Qualite volontairement legere pendant
            # le geste uniquement.
            preview = ImageOps.fit(
                drag_source,
                size,
                method=(
                    Image.Resampling.NEAREST
                ),
                centering=(
                    0.5,
                    0.5,
                ),
            )

            photo = ImageTk.PhotoImage(
                preview
            )

            canvas.itemconfigure(
                canvas_id,
                image=photo,
            )

        except Exception:
            return

        photos = getattr(
            self,
            "_composition_detached_image_preview_photos",
            None,
        )

        if not isinstance(
            photos,
            dict,
        ):

            photos = {}

            self._composition_detached_image_preview_photos = (
                photos
            )

        photos[
            element_id
        ] = photo


    def _composition_cancel_image_preview(
        self,
    ) -> None:

        canvas = getattr(
            self,
            "_composition_editor_canvas",
            None,
        )

        after_id = getattr(
            self,
            "_composition_image_preview_after",
            None,
        )

        if (
            canvas is not None
            and after_id is not None
        ):

            try:

                canvas.after_cancel(
                    after_id
                )

            except Exception:
                pass

        self._composition_image_preview_after = (
            None
        )

        self._composition_image_preview_pending = (
            None
        )


    def _composition_pointer_motion(
        self,
        event,
    ):

        if bool(
            getattr(
                self,
                "_composition_space_pan_active",
                False,
            )
        ):

            return self._composition_pan_motion(
                event
            )

        state = getattr(
            self,
            "_composition_drag_state",
            None,
        )

        if not isinstance(
            state,
            dict,
        ):
            return None

        pixel_dx = abs(
            float(
                event.x
            )
            - float(
                state["start_x"]
            )
        )

        pixel_dy = abs(
            float(
                event.y
            )
            - float(
                state["start_y"]
            )
        )

        if (
            pixel_dx < 1.0
            and pixel_dy < 1.0
        ):
            return "break"

        geometry = (
            self._composition_drag_geometry(
                state,
                event,
            )
        )

        if str(
            state.get(
                "kind",
                "",
            )
        ).lower() == "image":

            geometry = (
                self._composition_guard_image_geometry(
                    state,
                    geometry,
                )
            )

        state["moved"] = True

        state[
            "preview_geometry"
        ] = geometry

        canvas = getattr(
            self,
            "_composition_editor_canvas",
            None,
        )

        if canvas is not None:

            self._composition_paint_selection_geometry(
                canvas,
                geometry,
            )

        self._composition_preview_geometry_vars(
            geometry
        )

        kind = str(
            state.get(
                "kind",
                "",
            )
        ).lower()

        if kind == "image":

            self._composition_preview_detached_image(
                state,
                geometry,
            )

        elif kind == "text":

            self._composition_preview_detached_text_move(
                state,
                geometry,
            )

        return "break"

    def _composition_pointer_release(
        self,
        event,
    ):

        if bool(
            getattr(
                self,
                "_composition_space_pan_active",
                False,
            )
        ):

            return self._composition_pan_end(
                event
            )

        self._composition_cancel_image_preview()

        state = getattr(
            self,
            "_composition_drag_state",
            None,
        )

        self._composition_drag_state = (
            None
        )

        self._composition_live_detach_ids = (
            set()
        )

        if (
            not isinstance(
                state,
                dict,
            )
            or not state.get(
                "moved",
                False,
            )
        ):
            return None

        page = self.session.active_page

        element = (
            self._composition_selected_element()
        )

        if (
            page is None
            or element is None
        ):
            return None

        requested = (
            state.get(
                "preview_geometry"
            )
            or self._composition_drag_geometry(
                state,
                event,
            )
        )

        page_id = page.id

        element_id = str(
            state["element_id"]
        )

        mode = str(
            state["mode"]
        )

        kind = str(
            state.get(
                "kind",
                "",
            )
        ).lower()

        handle = state.get(
            "handle"
        )

        if kind == "image":

            requested = (
                self._composition_guard_image_geometry(
                    state,
                    requested,
                )
            )

        if mode == "move":

            base = state[
                "geometry"
            ]

            dx_mm = (
                float(
                    requested["x_mm"]
                )
                - float(
                    base["x_mm"]
                )
            )

            dy_mm = (
                float(
                    requested["y_mm"]
                )
                - float(
                    base["y_mm"]
                )
            )

            def action(
                project,
            ):

                from src.v4.composition_geometry import (
                    translate_element,
                )

                book = project.book

                if book is None:
                    raise RuntimeError(
                        "Livre indisponible."
                    )

                return translate_element(
                    book,
                    page_id,
                    element_id,
                    dx_mm=dx_mm,
                    dy_mm=dy_mm,
                )

            self.session.execute(
                "Deplacer le cadre",
                action,
            )

        elif kind == "text":

            values = dict(
                requested
            )

            (
                safe_width,
                minimum_height,
                line_count,
            ) = (
                self._composition_text_guardrail(
                    element,
                    values[
                        "width_mm"
                    ],
                )
            )

            old_right = (
                float(
                    values["x_mm"]
                )
                + float(
                    values["width_mm"]
                )
            )

            old_bottom = (
                float(
                    values["y_mm"]
                )
                + float(
                    values["height_mm"]
                )
            )

            values["width_mm"] = (
                safe_width
            )

            if (
                handle
                and "w" in handle
            ):

                values["x_mm"] = (
                    old_right
                    - safe_width
                )

            # Poignee horizontale :
            # le cadre se recadre automatiquement
            # sur la hauteur necessaire au texte.
            if handle in (
                "e",
                "w",
            ):

                values["height_mm"] = (
                    minimum_height
                )

            else:

                values["height_mm"] = max(
                    float(
                        values["height_mm"]
                    ),
                    minimum_height,
                )

                if (
                    handle
                    and "n" in handle
                    and values[
                        "height_mm"
                    ] > float(
                        requested[
                            "height_mm"
                        ]
                    )
                ):

                    values["y_mm"] = (
                        old_bottom
                        - values[
                            "height_mm"
                        ]
                    )

            def action(
                project,
            ):

                from src.v4.composition import (
                    update_element_geometry,
                )

                book = project.book

                if book is None:
                    raise RuntimeError(
                        "Livre indisponible."
                    )

                result = (
                    update_element_geometry(
                        book,
                        page_id,
                        element_id,
                        x_mm=values[
                            "x_mm"
                        ],
                        y_mm=values[
                            "y_mm"
                        ],
                        width_mm=values[
                            "width_mm"
                        ],
                        height_mm=values[
                            "height_mm"
                        ],
                    )
                )

                metadata = (
                    result.setdefault(
                        "metadata",
                        {},
                    )
                )

                metadata[
                    "text_layout_mode"
                ] = "fixed_font"

                metadata[
                    "text_layout_line_count"
                ] = line_count

                metadata[
                    "text_guardrail"
                ] = True

                return result

            self.session.execute(
                "Redimensionner le texte",
                action,
            )

        else:

            scale = max(
                0.0001,
                float(
                    state["scale"]
                ),
            )

            dx_mm = (
                float(
                    event.x
                )
                - float(
                    state["start_x"]
                )
            ) / scale

            dy_mm = (
                float(
                    event.y
                )
                - float(
                    state["start_y"]
                )
            ) / scale

            def action(
                project,
            ):

                from src.v4.composition_geometry import (
                    resize_from_handle,
                )

                book = project.book

                if book is None:
                    raise RuntimeError(
                        "Livre indisponible."
                    )

                return resize_from_handle(
                    book,
                    page_id,
                    element_id,
                    handle=handle,
                    dx_mm=dx_mm,
                    dy_mm=dy_mm,
                    min_size_mm=0.5,
                )

            self.session.execute(
                "Redimensionner le cadre",
                action,
            )

        self.session.set_selection(
            [element_id],
            include_associated=False,
        )

        self._composition_update_inspector_context()

        canvas = getattr(
            self,
            "_composition_editor_canvas",
            None,
        )

        if canvas is not None:
            self._draw_page(
                canvas
            )

        return "break"


    def _composition_canvas_click(
        self,
        event,
    ) -> None:

        try:
            event.widget.focus_set()
        except Exception:
            pass

        if bool(
            getattr(
                self,
                "_composition_space_pan_active",
                False,
            )
        ):

            self._composition_pan_start(
                event
            )

            return "break"

        element = (
            self._composition_element_at_canvas_point(
                event
            )
        )

        if element is None:

            self.session.clear_selection()

        else:

            element_id = str(
                element.get(
                    "id",
                    "",
                )
            )

            if element_id:

                self.session.set_selection(
                    [element_id],
                    include_associated=False,
                )

            else:

                self.session.clear_selection()

        self._composition_update_inspector_context()

        canvas = getattr(
            self,
            "_composition_editor_canvas",
            None,
        )

        if canvas is not None:

            self._draw_page(
                canvas
            )

        return None

    def _composition_set_zoom(
        self,
        value,
        *,
        anchor_x=None,
        anchor_y=None,
    ) -> None:
        """
        Zoom de Composition uniquement.

        Le point situe sous le pointeur reste fixe
        pendant le changement d'echelle.
        """

        canvas = getattr(
            self,
            "_composition_editor_canvas",
            None,
        )

        page = self.session.active_page

        if (
            canvas is None
            or page is None
        ):
            return

        old_zoom = float(
            getattr(
                self,
                "_composition_zoom_factor",
                1.0,
            )
            or 1.0
        )

        new_zoom = max(
            0.25,
            min(
                5.0,
                float(
                    value
                ),
            ),
        )

        if (
            anchor_x is None
            or anchor_y is None
        ):

            anchor_x = (
                max(
                    canvas.winfo_width(),
                    100,
                )
                / 2.0
            )

            anchor_y = (
                max(
                    canvas.winfo_height(),
                    100,
                )
                / 2.0
            )

        view = getattr(
            self,
            "_composition_page_view",
            None,
        )
        anchor_page_id = page.id

        # En vue double, le zoom suit la moitié réellement située
        # sous le pointeur, même si l'autre page est active.
        for candidate_page_id, candidate_view in getattr(
            self,
            "_composition_page_views",
            {},
        ).items():
            if not isinstance(candidate_view, dict):
                continue
            try:
                vx = float(candidate_view["x"])
                vy = float(candidate_view["y"])
                vw = float(candidate_view["page_w"])
                vh = float(candidate_view["page_h"])
            except (KeyError, TypeError, ValueError):
                continue

            if (
                vx <= float(anchor_x) <= vx + vw
                and vy <= float(anchor_y) <= vy + vh
            ):
                view = candidate_view
                anchor_page_id = str(candidate_page_id)
                break

        page_mm_x = None
        page_mm_y = None

        if (
            isinstance(
                view,
                dict,
            )
            and float(
                view.get(
                    "scale",
                    0.0,
                )
                or 0.0
            ) > 0
        ):

            old_scale = float(
                view["scale"]
            )

            page_mm_x = (
                float(
                    anchor_x
                )
                - float(
                    view["x"]
                )
            ) / old_scale

            page_mm_y = (
                float(
                    anchor_y
                )
                - float(
                    view["y"]
                )
            ) / old_scale

        self._composition_zoom_factor = (
            new_zoom
        )

        if (
            page_mm_x is not None
            and page_mm_y is not None
        ):

            book = self.session.book
            fmt = book.format

            width = max(
                canvas.winfo_width(),
                100,
            )

            height = max(
                canvas.winfo_height(),
                100,
            )

            spread_pair = self._composition_spread_for_page_id(
                page.id
            )
            spread_mode = spread_pair is not None

            fit_width_mm = float(fmt.width_mm) * (
                2.0 if spread_mode else 1.0
            )

            fit_scale = min(
                (width - 140)
                / max(1.0, fit_width_mm),
                (height - 100)
                / float(
                    fmt.height_mm
                ),
            )

            fit_scale = max(
                0.2,
                fit_scale,
            )

            new_scale = (
                fit_scale
                * new_zoom
            )

            page_w = (
                float(
                    fmt.width_mm
                )
                * new_scale
            )

            page_h = (
                float(
                    fmt.height_mm
                )
                * new_scale
            )

            if spread_mode:
                spread_x = (
                    width / 2.0
                    - page_w
                )
                centered_x = (
                    spread_x
                    if anchor_page_id == spread_pair.left_page_id
                    else spread_x + page_w
                )
            else:
                centered_x = (
                    width / 2.0
                    - page_w / 2.0
                )

            centered_y = (
                height / 2.0
                - page_h / 2.0
            )

            self._composition_pan_x = (
                float(
                    anchor_x
                )
                - centered_x
                - page_mm_x
                * new_scale
            )

            self._composition_pan_y = (
                float(
                    anchor_y
                )
                - centered_y
                - page_mm_y
                * new_scale
            )

        zoom_var = getattr(
            self,
            "_composition_zoom_var",
            None,
        )

        if zoom_var is not None:
            zoom_var.set(
                f"{int(round(new_zoom * 100))} %"
            )

        self._draw_page(
            canvas
        )


    def _composition_zoom_wheel(
        self,
        event,
    ):

        current = float(
            getattr(
                self,
                "_composition_zoom_factor",
                1.0,
            )
            or 1.0
        )

        if event.delta > 0:
            target = (
                current
                * 1.12
            )
        else:
            target = (
                current
                / 1.12
            )

        self._composition_set_zoom(
            target,
            anchor_x=event.x,
            anchor_y=event.y,
        )

        return "break"


    def _composition_zoom_in(
        self,
    ) -> None:

        current = float(
            getattr(
                self,
                "_composition_zoom_factor",
                1.0,
            )
            or 1.0
        )

        self._composition_set_zoom(
            current * 1.20
        )


    def _composition_zoom_out(
        self,
    ) -> None:

        current = float(
            getattr(
                self,
                "_composition_zoom_factor",
                1.0,
            )
            or 1.0
        )

        self._composition_set_zoom(
            current / 1.20
        )


    def _composition_zoom_reset(
        self,
    ) -> None:

        self._composition_zoom_factor = (
            1.0
        )

        self._composition_pan_x = (
            0.0
        )

        self._composition_pan_y = (
            0.0
        )

        zoom_var = getattr(
            self,
            "_composition_zoom_var",
            None,
        )

        if zoom_var is not None:
            zoom_var.set(
                "100 %"
            )

        canvas = getattr(
            self,
            "_composition_editor_canvas",
            None,
        )

        if canvas is not None:
            self._draw_page(
                canvas
            )


    def _composition_space_pan_press(
        self,
        _event,
    ):

        self._composition_space_pan_active = (
            True
        )

        canvas = getattr(
            self,
            "_composition_editor_canvas",
            None,
        )

        if canvas is not None:

            try:
                canvas.configure(
                    cursor="fleur"
                )
            except Exception:
                pass

        return "break"


    def _composition_space_pan_release(
        self,
        _event,
    ):

        self._composition_space_pan_active = (
            False
        )

        self._composition_pan_state = None

        canvas = getattr(
            self,
            "_composition_editor_canvas",
            None,
        )

        if canvas is not None:

            try:
                canvas.configure(
                    cursor=""
                )
            except Exception:
                pass

        return "break"


    def _composition_pan_start(
        self,
        event,
    ):

        if not bool(
            getattr(
                self,
                "_composition_space_pan_active",
                False,
            )
        ):
            return None

        self._composition_pan_state = {
            "last_x": float(
                event.x
            ),
            "last_y": float(
                event.y
            ),
        }

        return "break"

    def _composition_pan_motion(
        self,
        event,
    ):

        if not bool(
            getattr(
                self,
                "_composition_space_pan_active",
                False,
            )
        ):
            return None

        state = getattr(
            self,
            "_composition_pan_state",
            None,
        )

        if not isinstance(
            state,
            dict,
        ):
            return "break"

        canvas = getattr(
            self,
            "_composition_editor_canvas",
            None,
        )

        if canvas is None:
            return "break"

        current_x = float(
            event.x
        )

        current_y = float(
            event.y
        )

        dx = (
            current_x
            - state["last_x"]
        )

        dy = (
            current_y
            - state["last_y"]
        )

        if (
            dx == 0
            and dy == 0
        ):
            return "break"

        # Deplace immediatement le rendu deja present.
        # Aucun recalcul de page ici.
        canvas.move(
            "all",
            dx,
            dy,
        )

        self._composition_pan_x = (
            float(
                getattr(
                    self,
                    "_composition_pan_x",
                    0.0,
                )
                or 0.0
            )
            + dx
        )

        self._composition_pan_y = (
            float(
                getattr(
                    self,
                    "_composition_pan_y",
                    0.0,
                )
                or 0.0
            )
            + dy
        )

        # Maintenir egalement la geometrie de vue
        # synchronisee avec ce qui est affiche.
        view = getattr(
            self,
            "_composition_page_view",
            None,
        )

        if isinstance(
            view,
            dict,
        ):
            view["x"] = (
                float(
                    view.get(
                        "x",
                        0.0,
                    )
                )
                + dx
            )

            view["y"] = (
                float(
                    view.get(
                        "y",
                        0.0,
                    )
                )
                + dy
            )

        state["last_x"] = (
            current_x
        )

        state["last_y"] = (
            current_y
        )

        return "break"

    def _composition_pan_end(
        self,
        _event,
    ):

        state = getattr(
            self,
            "_composition_pan_state",
            None,
        )

        self._composition_pan_state = (
            None
        )

        if not isinstance(
            state,
            dict,
        ):
            return None

        canvas = getattr(
            self,
            "_composition_editor_canvas",
            None,
        )

        if canvas is not None:
            self._draw_page(
                canvas
            )

        return "break"

    def _composition_draw_selection(
        self,
        canvas,
    ) -> None:

        self._composition_handle_regions = {}

        page = self.session.active_page

        if page is None:
            return

        selected_ids = set(
            getattr(
                self.session,
                "selected_element_ids",
                (),
            )
            or ()
        )

        if not selected_ids:
            return

        view = getattr(
            self,
            "_composition_page_view",
            None,
        )

        if (
            not isinstance(
                view,
                dict,
            )
            or view.get(
                "page_id"
            ) != page.id
        ):
            return

        for element in page.content:

            if not isinstance(
                element,
                dict,
            ):
                continue

            if str(
                element.get(
                    "id",
                    "",
                )
            ) not in selected_ids:
                continue

            # Même si une ancienne commande interne a conservé l'identité
            # d'un fragment de texte Source, ne jamais dessiner de cadre ni
            # de poignées autour du texte éditorial.
            if (
                self._composition_text_uses_editorial_flow(element)
                and not self._composition_text_manual_targets_element(element)
            ):
                continue

            geometry = element.get(
                "geometry"
            )

            if not isinstance(
                geometry,
                dict,
            ):
                continue

            self._composition_paint_selection_geometry(
                canvas,
                geometry,
            )

            # Une seule selection manipulable actuellement.
            break

    def _composition_source_image_geometry(
        self,
        element,
        pdf_page,
        fmt,
    ):
        """
        Reconstitue la geometrie d'origine de l'image
        telle qu'elle a ete materialisee dans le Livre.
        """

        metadata = element.get(
            "metadata",
            {},
        )

        if not isinstance(
            metadata,
            dict,
        ):
            return None

        bbox = metadata.get(
            "source_bbox_norm"
        )

        if (
            not isinstance(
                bbox,
                (list, tuple),
            )
            or len(bbox) != 4
        ):
            return None

        try:

            x0 = float(
                bbox[0]
            )

            y0 = float(
                bbox[1]
            )

            x1 = float(
                bbox[2]
            )

            y1 = float(
                bbox[3]
            )

            source_width_mm = (
                float(
                    pdf_page.rect.width
                )
                * 25.4
                / 72.0
            )

            source_height_mm = (
                float(
                    pdf_page.rect.height
                )
                * 25.4
                / 72.0
            )

            book_width_mm = float(
                fmt.width_mm
            )

            book_height_mm = float(
                fmt.height_mm
            )

        except (
            TypeError,
            ValueError,
        ):
            return None

        if (
            source_width_mm <= 0
            or source_height_mm <= 0
        ):
            return None

        factor = min(
            book_width_mm
            / source_width_mm,
            book_height_mm
            / source_height_mm,
        )

        rendered_width = (
            source_width_mm
            * factor
        )

        rendered_height = (
            source_height_mm
            * factor
        )

        offset_x = (
            book_width_mm
            - rendered_width
        ) / 2.0

        offset_y = (
            book_height_mm
            - rendered_height
        ) / 2.0

        return {
            "x_mm":
                offset_x
                + x0
                * rendered_width,

            "y_mm":
                offset_y
                + y0
                * rendered_height,

            "width_mm":
                (
                    x1 - x0
                )
                * rendered_width,

            "height_mm":
                (
                    y1 - y0
                )
                * rendered_height,
        }


    def _composition_image_is_detached(
        self,
        element,
        pdf_page,
        fmt,
    ) -> bool:

        metadata = element.get(
            "metadata",
            {},
        )

        if isinstance(metadata, dict):
            # Une correction de contenu est prioritaire : afficher l'ancien
            # visuel Source après avoir changé le texte serait trompeur.
            if bool(metadata.get("text_content_modified", False)):
                return True
            if bool(metadata.get("format_keep_source_visual", False)):
                return False
            if bool(metadata.get("format_content_adapted", False)):
                return True

        element_id = str(
            element.get(
                "id",
                "",
            )
        )

        forced = set(
            getattr(
                self,
                "_composition_live_detach_ids",
                (),
            )
            or ()
        )

        if (
            element_id
            and element_id in forced
        ):
            return True

        source_geometry = (
            self._composition_source_image_geometry(
                element,
                pdf_page,
                fmt,
            )
        )

        current = element.get(
            "geometry"
        )

        if (
            source_geometry is None
            or not isinstance(
                current,
                dict,
            )
        ):
            return False

        for key in (
            "x_mm",
            "y_mm",
            "width_mm",
            "height_mm",
        ):

            try:

                if abs(
                    float(
                        current[key]
                    )
                    - float(
                        source_geometry[key]
                    )
                ) > 0.05:
                    return True

            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                return False

        return False


    def _composition_image_source_rect(
        self,
        element,
        pdf_page,
    ):

        metadata = element.get(
            "metadata",
            {},
        )

        if not isinstance(
            metadata,
            dict,
        ):
            return None

        bbox = metadata.get(
            "source_bbox_norm"
        )

        if (
            not isinstance(
                bbox,
                (list, tuple),
            )
            or len(bbox) != 4
        ):
            return None

        try:

            return (
                float(
                    bbox[0]
                )
                * pdf_page.rect.width,

                float(
                    bbox[1]
                )
                * pdf_page.rect.height,

                float(
                    bbox[2]
                )
                * pdf_page.rect.width,

                float(
                    bbox[3]
                )
                * pdf_page.rect.height,
            )

        except (
            TypeError,
            ValueError,
        ):
            return None


    def _composition_extract_pdf_image(
        self,
        document,
        pdf_page,
        element,
    ):
        """
        Extrait l'image elle-meme depuis son xref PDF.
        """

        import io
        import pymupdf

        payload = element.get(
            "payload",
            {},
        )

        if not isinstance(
            payload,
            dict,
        ):
            return None

        try:

            xref = int(
                payload.get(
                    "xref",
                    0,
                )
                or 0
            )

        except (
            TypeError,
            ValueError,
        ):
            return None

        if xref <= 0:
            return None

        smask = 0

        try:

            for image_info in (
                pdf_page.get_images(
                    full=True
                )
            ):

                if (
                    len(image_info) >= 2
                    and int(
                        image_info[0]
                    ) == xref
                ):

                    smask = int(
                        image_info[1]
                        or 0
                    )

                    break

        except Exception:
            smask = 0

        try:

            pix = pymupdf.Pixmap(
                document,
                xref,
            )

            if smask > 0:

                try:

                    mask = pymupdf.Pixmap(
                        document,
                        smask,
                    )

                    pix = pymupdf.Pixmap(
                        pix,
                        mask,
                    )

                except Exception:
                    pass

            png = pix.tobytes(
                "png"
            )

            image = Image.open(
                io.BytesIO(
                    png
                )
            ).copy()

            return image

        except Exception:
            return None


    def _composition_prepare_detached_images(
        self,
        document,
        pdf_page,
        page,
        fmt,
    ):
        """
        Prepare les images qui sont devenues des objets
        Composition autonomes.

        Le PDF Source sur disque n'est jamais modifie.
        """

        import pymupdf

        detached = []

        for element in getattr(
            page,
            "content",
            (),
        ):

            if not isinstance(
                element,
                dict,
            ):
                continue

            if str(
                element.get(
                    "kind",
                    "",
                )
            ).lower() != "image":
                continue

            if not (
                self._composition_image_is_detached(
                    element,
                    pdf_page,
                    fmt,
                )
            ):
                continue

            source_rect = (
                self._composition_image_source_rect(
                    element,
                    pdf_page,
                )
            )

            image = (
                self._composition_extract_pdf_image(
                    document,
                    pdf_page,
                    element,
                )
            )

            geometry = element.get(
                "geometry"
            )

            if (
                source_rect is None
                or image is None
                or not isinstance(
                    geometry,
                    dict,
                )
            ):
                continue

            rect = pymupdf.Rect(
                *source_rect
            )

            if rect.is_empty:
                continue

            detached.append(
                {
                    "id":
                        str(
                            element.get(
                                "id",
                                "",
                            )
                        ),

                    "image":
                        image,

                    "geometry":
                        dict(
                            geometry
                        ),

                    "source_rect":
                        rect,
                }
            )

        if not detached:
            return []

        # Supprime seulement les pixels d'image aux anciens
        # emplacements. Le texte et les dessins vectoriels
        # du PDF restent intacts.
        for item in detached:

            pdf_page.add_redact_annot(
                item[
                    "source_rect"
                ],
                fill=False,
                cross_out=False,
            )

        try:

            pdf_page.apply_redactions(
                images=2,
                graphics=0,
                text=1,
            )

        except Exception:

            return []

        return detached


    def _composition_draw_detached_images(
        self,
        canvas,
        detached,
        *,
        page_x,
        page_y,
        scale,
    ) -> None:

        if not detached:

            self._composition_detached_image_items = {}
            self._composition_detached_image_sources = {}
            self._composition_detached_image_photos = {}

            return

        from PIL import ImageOps

        items = {}
        sources = {}
        photos = {}

        for item in detached:

            geometry = item[
                "geometry"
            ]

            source_image = item[
                "image"
            ]

            element_id = str(
                item.get(
                    "id",
                    "",
                )
            )

            if not element_id:
                continue

            try:

                width_px = max(
                    1,
                    int(
                        round(
                            float(
                                geometry[
                                    "width_mm"
                                ]
                            )
                            * scale
                        )
                    ),
                )

                height_px = max(
                    1,
                    int(
                        round(
                            float(
                                geometry[
                                    "height_mm"
                                ]
                            )
                            * scale
                        )
                    ),
                )

                left = (
                    float(
                        page_x
                    )
                    + float(
                        geometry[
                            "x_mm"
                        ]
                    )
                    * scale
                )

                top = (
                    float(
                        page_y
                    )
                    + float(
                        geometry[
                            "y_mm"
                        ]
                    )
                    * scale
                )

            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                continue

            try:

                # Changement de format : préserver l'image entière par défaut.
                # On adapte l'image à son nouveau cadre sans la rogner.
                contained = ImageOps.contain(
                    source_image,
                    (
                        width_px,
                        height_px,
                    ),
                    method=Image.Resampling.LANCZOS,
                )

                mode = "RGBA" if contained.mode == "RGBA" else "RGB"
                background = (255, 255, 255, 0) if mode == "RGBA" else (255, 255, 255)
                fitted = Image.new(
                    mode,
                    (width_px, height_px),
                    background,
                )
                offset = (
                    max(0, (width_px - contained.width) // 2),
                    max(0, (height_px - contained.height) // 2),
                )
                if contained.mode == "RGBA":
                    fitted.paste(contained, offset, contained)
                else:
                    fitted.paste(contained, offset)

                photo = ImageTk.PhotoImage(
                    fitted
                )

            except Exception:
                continue

            canvas_id = canvas.create_image(
                left,
                top,
                image=photo,
                anchor="nw",
                tags=(
                    "composition_detached_image",
                ),
            )

            items[
                element_id
            ] = canvas_id

            sources[
                element_id
            ] = source_image

            photos[
                element_id
            ] = photo

        self._composition_detached_image_items = (
            items
        )

        self._composition_detached_image_sources = (
            sources
        )

        self._composition_detached_image_photos = (
            photos
        )

    def _composition_source_text_geometry(
        self,
        element,
        pdf_page,
        fmt,
    ):

        metadata = element.get(
            "metadata",
            {},
        )

        if not isinstance(
            metadata,
            dict,
        ):
            return None

        bbox = metadata.get(
            "source_bbox_norm"
        )

        if (
            not isinstance(
                bbox,
                (list, tuple),
            )
            or len(bbox) != 4
        ):
            return None

        try:

            x0 = float(bbox[0])
            y0 = float(bbox[1])
            x1 = float(bbox[2])
            y1 = float(bbox[3])

            source_width_mm = (
                float(
                    pdf_page.rect.width
                )
                * 25.4
                / 72.0
            )

            source_height_mm = (
                float(
                    pdf_page.rect.height
                )
                * 25.4
                / 72.0
            )

            book_width_mm = float(
                fmt.width_mm
            )

            book_height_mm = float(
                fmt.height_mm
            )

        except (
            TypeError,
            ValueError,
        ):
            return None

        if (
            source_width_mm <= 0
            or source_height_mm <= 0
        ):
            return None

        factor = min(
            book_width_mm
            / source_width_mm,
            book_height_mm
            / source_height_mm,
        )

        rendered_width = (
            source_width_mm
            * factor
        )

        rendered_height = (
            source_height_mm
            * factor
        )

        offset_x = (
            book_width_mm
            - rendered_width
        ) / 2.0

        offset_y = (
            book_height_mm
            - rendered_height
        ) / 2.0

        return {
            "x_mm":
                offset_x
                + x0 * rendered_width,

            "y_mm":
                offset_y
                + y0 * rendered_height,

            "width_mm":
                (x1 - x0)
                * rendered_width,

            "height_mm":
                (y1 - y0)
                * rendered_height,
        }


    def _composition_text_is_detached(
        self,
        element,
        pdf_page,
        fmt,
    ) -> bool:

        metadata = element.get(
            "metadata",
            {},
        )

        if isinstance(metadata, dict):
            if bool(metadata.get("format_keep_source_visual", False)):
                return False
            if bool(metadata.get("format_content_adapted", False)):
                return True

        element_id = str(
            element.get(
                "id",
                "",
            )
        )

        forced = set(
            getattr(
                self,
                "_composition_live_detach_ids",
                (),
            )
            or ()
        )

        if (
            element_id
            and element_id in forced
        ):
            return True

        source_geometry = (
            self._composition_source_text_geometry(
                element,
                pdf_page,
                fmt,
            )
        )

        current = element.get(
            "geometry"
        )

        if (
            source_geometry is None
            or not isinstance(
                current,
                dict,
            )
        ):
            return False

        for key in (
            "x_mm",
            "y_mm",
            "width_mm",
            "height_mm",
        ):

            try:

                if abs(
                    float(
                        current[key]
                    )
                    - float(
                        source_geometry[key]
                    )
                ) > 0.05:
                    return True

            except (
                KeyError,
                TypeError,
                ValueError,
            ):
                return False

        return False


    def _composition_prepare_detached_texts(
        self,
        document,
        pdf_page,
        page,
        fmt,
    ):

        import pymupdf

        candidates = []

        for element in getattr(
            page,
            "content",
            (),
        ):

            if not isinstance(
                element,
                dict,
            ):
                continue

            if str(
                element.get(
                    "kind",
                    "",
                )
            ).lower() != "text":
                continue

            if not (
                self._composition_text_is_detached(
                    element,
                    pdf_page,
                    fmt,
                )
            ):
                continue

            metadata = element.get(
                "metadata",
                {},
            )

            bbox = (
                metadata.get(
                    "source_bbox_norm"
                )
                if isinstance(
                    metadata,
                    dict,
                )
                else None
            )

            if (
                not isinstance(
                    bbox,
                    (list, tuple),
                )
                or len(bbox) != 4
            ):
                continue

            try:

                source_rect = pymupdf.Rect(
                    float(bbox[0])
                    * pdf_page.rect.width,

                    float(bbox[1])
                    * pdf_page.rect.height,

                    float(bbox[2])
                    * pdf_page.rect.width,

                    float(bbox[3])
                    * pdf_page.rect.height,
                )

            except (
                TypeError,
                ValueError,
            ):
                continue

            if source_rect.is_empty:
                continue

            source_geometry = (
                self._composition_source_text_geometry(
                    element,
                    pdf_page,
                    fmt,
                )
            )

            geometry = element.get(
                "geometry"
            )

            if (
                source_geometry is None
                or not isinstance(
                    geometry,
                    dict,
                )
            ):
                continue

            candidates.append(
                {
                    "id":
                        str(
                            element.get(
                                "id",
                                "",
                            )
                        ),

                    "source_rect":
                        source_rect,

                    "source_geometry":
                        source_geometry,

                    "geometry":
                        dict(
                            geometry
                        ),

                    "element":
                        element,
                }
            )

        if not candidates:
            return []

        # ----------------------------------------------------
        # FABRIQUER UNE PAGE QUI NE CONTIENT QUE LE TEXTE
        # ----------------------------------------------------

        text_document = pymupdf.open()

        try:

            text_document.insert_pdf(
                document,
                from_page=int(
                    pdf_page.number
                ),
                to_page=int(
                    pdf_page.number
                ),
            )

            text_page = (
                text_document.load_page(
                    0
                )
            )

            text_page.add_redact_annot(
                text_page.rect,
                fill=False,
                cross_out=False,
            )

            # Garder le texte.
            # Retirer images et graphiques de cette copie.
            text_page.apply_redactions(
                images=2,
                graphics=2,
                text=1,
            )

        except Exception:

            text_document.close()

            return []

        # ----------------------------------------------------
        # RETIRER LES BLOCS TEXTE DU FOND DE COMPOSITION
        # ----------------------------------------------------

        for item in candidates:

            try:

                pdf_page.add_redact_annot(
                    item[
                        "source_rect"
                    ],
                    fill=False,
                    cross_out=False,
                )

            except Exception:
                pass

        try:

            # Retirer seulement le texte.
            # Images et graphiques restent intacts.
            pdf_page.apply_redactions(
                images=0,
                graphics=0,
                text=0,
            )

        except Exception:

            text_document.close()

            return []

        for item in candidates:
            item[
                "text_document"
            ] = text_document

        return candidates


    def _composition_render_reflow_text(
        self,
        element,
        geometry,
        scale,
    ):
        """Rend le texte recomposé avec Pillow/FreeType.

        La nouvelle composition n'utilise plus MuPDF pour mesurer ou dessiner le
        texte. Cela réduit la dépendance juridique du futur moteur de composition
        sans modifier, pour l'instant, la lecture du PDF Source historique.
        """
        from src.v4.text_compositor import render_composition_pillow

        info = self._composition_text_reflow_info(
            element, geometry.get("width_mm", 1.0),
        )
        if not isinstance(info, dict) or info.get("status") != "exact":
            return None

        width_mm = float(geometry.get("width_mm", info["width_mm"]))
        height_mm = float(geometry.get("height_mm", info["height_mm"]))
        result = info.get("composition")
        if result is None:
            return None

        return render_composition_pillow(
            result,
            font_path=info["font_path"],
            font_size_pt=float(info["font_size_pt"]),
            width_mm=width_mm,
            height_mm=height_mm,
            scale_px_per_mm=float(scale),
            alignment=str(info.get("alignment", "justify") or "justify"),
            color=tuple(info.get("color", (0.0, 0.0, 0.0))),
            line_pitch_mm=float(info.get("line_pitch_mm", 0.0) or 0.0) or None,
            paragraph_gap_mm=float(info.get("paragraph_gap_mm", 0.0) or 0.0),
        )


    def _composition_draw_detached_texts(
        self,
        canvas,
        detached,
        *,
        page_x,
        page_y,
        scale,
    ) -> None:

        import pymupdf

        if not detached:

            self._composition_detached_text_items = {}
            self._composition_detached_text_photos = {}

            return

        items = {}
        photos = {}

        text_document = detached[0].get(
            "text_document"
        )

        if text_document is None:
            return

        try:

            text_page = (
                text_document.load_page(
                    0
                )
            )

            for item in detached:

                element_id = str(
                    item.get(
                        "id",
                        "",
                    )
                )

                if not element_id:
                    continue

                source_rect = item[
                    "source_rect"
                ]

                source_geometry = item[
                    "source_geometry"
                ]

                geometry = item[
                    "geometry"
                ]

                element = item.get(
                    "element"
                )

                try:

                    source_width = float(
                        source_geometry[
                            "width_mm"
                        ]
                    )

                    current_width = float(
                        geometry[
                            "width_mm"
                        ]
                    )

                    width_changed = (
                        abs(
                            current_width
                            - source_width
                        )
                        > 0.05
                    )

                    element_metadata = (
                        element.get("metadata", {})
                        if isinstance(element, dict)
                        else {}
                    )
                    force_reflow = bool(
                        isinstance(element_metadata, dict)
                        and (
                            element_metadata.get("format_content_adapted", False)
                            or element_metadata.get("text_content_modified", False)
                        )
                    )

                    image = None

                    if (
                        (width_changed or force_reflow)
                        and isinstance(
                            element,
                            dict,
                        )
                    ):

                        image = (
                            self._composition_render_reflow_text(
                                element,
                                geometry,
                                scale,
                            )
                        )

                    # Si aucune recomposition n'est necessaire
                    # ou impossible, garder le rendu Source exact.
                    if image is None:

                        desired_width = max(
                            1,
                            int(
                                round(
                                    source_width
                                    * scale
                                )
                            ),
                        )

                        render_scale = (
                            desired_width
                            / max(
                                1.0,
                                float(
                                    source_rect.width
                                ),
                            )
                        )

                        render_scale = max(
                            0.5,
                            render_scale
                            * 1.35,
                        )

                        pix = text_page.get_pixmap(
                            matrix=pymupdf.Matrix(
                                render_scale,
                                render_scale,
                            ),
                            clip=source_rect,
                            alpha=True,
                        )

                        image = Image.frombytes(
                            "RGBA",
                            (
                                pix.width,
                                pix.height,
                            ),
                            pix.samples,
                        )

                        width_px = max(
                            1,
                            int(
                                round(
                                    source_width
                                    * scale
                                )
                            ),
                        )

                        height_px = max(
                            1,
                            int(
                                round(
                                    float(
                                        source_geometry[
                                            "height_mm"
                                        ]
                                    )
                                    * scale
                                )
                            ),
                        )

                        image.thumbnail(
                            (
                                width_px,
                                height_px,
                            ),
                            Image.Resampling.LANCZOS,
                        )

                    photo = ImageTk.PhotoImage(
                        image
                    )

                    left = (
                        float(
                            page_x
                        )
                        + float(
                            geometry[
                                "x_mm"
                            ]
                        )
                        * scale
                    )

                    top = (
                        float(
                            page_y
                        )
                        + float(
                            geometry[
                                "y_mm"
                            ]
                        )
                        * scale
                    )

                except Exception:
                    continue

                canvas_id = canvas.create_image(
                    left,
                    top,
                    image=photo,
                    anchor="nw",
                    tags=(
                        "composition_detached_text",
                    ),
                )

                items[
                    element_id
                ] = canvas_id

                photos[
                    element_id
                ] = photo

        finally:

            try:
                text_document.close()
            except Exception:
                pass

        self._composition_detached_text_items = (
            items
        )

        self._composition_detached_text_photos = (
            photos
        )

    def _composition_preview_detached_text_move(
        self,
        state,
        geometry,
    ) -> None:

        if (
            state.get(
                "mode"
            )
            != "move"
        ):
            return

        canvas = getattr(
            self,
            "_composition_editor_canvas",
            None,
        )

        view = getattr(
            self,
            "_composition_page_view",
            None,
        )

        items = getattr(
            self,
            "_composition_detached_text_items",
            {},
        )

        if (
            canvas is None
            or not isinstance(
                view,
                dict,
            )
            or not isinstance(
                items,
                dict,
            )
        ):
            return

        element_id = str(
            state.get(
                "element_id",
                "",
            )
        )

        canvas_id = items.get(
            element_id
        )

        if canvas_id is None:
            return

        try:

            left = (
                float(
                    view["x"]
                )
                + float(
                    geometry[
                        "x_mm"
                    ]
                )
                * float(
                    view["scale"]
                )
            )

            top = (
                float(
                    view["y"]
                )
                + float(
                    geometry[
                        "y_mm"
                    ]
                )
                * float(
                    view["scale"]
                )
            )

            canvas.coords(
                canvas_id,
                left,
                top,
            )

        except Exception:
            pass


    def _composition_audit_book_images(
        self,
    ) -> dict:

        from src.v4.image_quality import (
            effective_dpi,
        )

        book = self.session.book

        audit = {
            "total": 0,
            "conforme": 0,
            "limited": 0,
            "critical": 0,
            "issues": [],
        }

        if book is None:
            return audit

        for page_index, page in enumerate(
            book.ordered_pages(),
            start=1,
        ):

            for element in getattr(
                page,
                "content",
                (),
            ):

                if not isinstance(
                    element,
                    dict,
                ):
                    continue

                if str(
                    element.get(
                        "kind",
                        "",
                    )
                ).lower() != "image":
                    continue

                payload = element.get(
                    "payload",
                    {},
                )

                geometry = element.get(
                    "geometry",
                    {},
                )

                if (
                    not isinstance(
                        payload,
                        dict,
                    )
                    or not isinstance(
                        geometry,
                        dict,
                    )
                ):
                    continue

                try:

                    quality = effective_dpi(
                        width_px=int(
                            payload.get(
                                "width_px",
                                0,
                            )
                            or 0
                        ),
                        height_px=int(
                            payload.get(
                                "height_px",
                                0,
                            )
                            or 0
                        ),
                        width_mm=float(
                            geometry[
                                "width_mm"
                            ]
                        ),
                        height_mm=float(
                            geometry[
                                "height_mm"
                            ]
                        ),
                    )

                except (
                    KeyError,
                    TypeError,
                    ValueError,
                ):
                    continue

                audit["total"] += 1
                audit[
                    quality.status
                ] += 1

                if (
                    quality.status
                    == "conforme"
                ):
                    continue

                source_page = None

                source = getattr(
                    page,
                    "source",
                    None,
                )

                if source is not None:

                    source_page = getattr(
                        source,
                        "source_page",
                        None,
                    )

                audit["issues"].append(
                    {
                        "page_id":
                            page.id,

                        "element_id":
                            str(
                                element.get(
                                    "id",
                                    "",
                                )
                            ),

                        "page_number":
                            page_index,

                        "source_page":
                            source_page,

                        "page_title":
                            (
                                page.title
                                or page.page_type
                                or (
                                    "Page "
                                    + str(
                                        page_index
                                    )
                                )
                            ),

                        "status":
                            quality.status,

                        "dpi":
                            float(
                                quality.effective_dpi
                            ),

                        "width_px":
                            quality.width_px,

                        "height_px":
                            quality.height_px,

                        "width_mm":
                            quality.width_mm,

                        "height_mm":
                            quality.height_mm,

                        "max_width_mm":
                            quality.max_width_mm,

                        "max_height_mm":
                            quality.max_height_mm,
                    }
                )

        return audit


    def _composition_offer_image_quality_report(
        self,
        audit,
    ) -> None:

        if not isinstance(
            audit,
            dict,
        ):
            return

        limited = int(
            audit.get(
                "limited",
                0,
            )
            or 0
        )

        critical = int(
            audit.get(
                "critical",
                0,
            )
            or 0
        )

        if (
            limited <= 0
            and critical <= 0
        ):
            return

        self._composition_show_image_quality_report(
            audit
        )

    def _composition_show_image_quality_report(
        self,
        audit,
    ) -> None:

        issues = list(
            audit.get(
                "issues",
                (),
            )
            or ()
        )

        if not issues:
            return

        # ----------------------------------------------------
        # UNE SEULE PALETTE
        # ----------------------------------------------------

        previous = getattr(
            self,
            "_composition_image_quality_palette",
            None,
        )

        if previous is not None:

            try:

                if previous.winfo_exists():
                    previous.destroy()

            except Exception:
                pass

        # ----------------------------------------------------
        # PALETTE FLOTTANTE TOMELINEA
        # ----------------------------------------------------

        window = tk.Toplevel(
            self
        )

        self._composition_image_quality_palette = (
            window
        )

        window.overrideredirect(
            True
        )

        window.configure(
            bg=theme.PAGE_BORDER,
        )

        window.transient(
            self
        )

        palette_width = 370
        palette_height = 520

        try:

            self.update_idletasks()

            root_x = int(
                self.winfo_rootx()
            )

            root_y = int(
                self.winfo_rooty()
            )

            root_w = int(
                self.winfo_width()
            )

            screen_w = int(
                self.winfo_screenwidth()
            )

            screen_h = int(
                self.winfo_screenheight()
            )

            # Si de la place existe a droite de TomeLinea,
            # utiliser cette zone.
            free_right = (
                screen_w
                - (
                    root_x
                    + root_w
                )
            )

            if (
                free_right
                >= palette_width
                + 20
            ):

                pos_x = (
                    root_x
                    + root_w
                    + 8
                )

            else:

                # Sinon la palette prend place sur la zone
                # droite de TomeLinea, essentiellement au-dessus
                # de l'inspecteur et non de la feuille.
                pos_x = (
                    root_x
                    + root_w
                    - palette_width
                    - 18
                )

            pos_y = (
                root_y
                + 82
            )

            pos_x = max(
                0,
                min(
                    pos_x,
                    screen_w
                    - palette_width,
                ),
            )

            pos_y = max(
                0,
                min(
                    pos_y,
                    screen_h
                    - palette_height
                    - 30,
                ),
            )

        except Exception:

            pos_x = 100
            pos_y = 100

        window.geometry(
            f"{palette_width}x{palette_height}"
            f"+{pos_x}+{pos_y}"
        )

        outer = tk.Frame(
            window,
            bg=theme.PANEL,
        )

        outer.pack(
            fill="both",
            expand=True,
            padx=1,
            pady=1,
        )

        # ----------------------------------------------------
        # BANDEAU
        # ----------------------------------------------------

        title_bar = tk.Frame(
            outer,
            bg=theme.WINDOW_DEEP,
            height=42,
        )

        title_bar.pack(
            fill="x",
        )

        title_bar.pack_propagate(
            False
        )

        tk.Label(
            title_bar,
            text="QUALIT\u00c9 DES IMAGES",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(
                theme.FONT_UI,
                10,
                "bold",
            ),
        ).pack(
            side="left",
            padx=14,
        )

        def close_palette():

            try:
                window.destroy()
            except Exception:
                pass

            self._composition_image_quality_palette = (
                None
            )

        tk.Button(
            title_bar,
            text="\u2715",
            command=close_palette,
            bg=theme.WINDOW_DEEP,
            fg=theme.MUTED,
            activebackground=theme.PANEL,
            activeforeground=theme.INK,
            relief="flat",
            bd=0,
            cursor="hand2",
            width=3,
            font=(
                theme.FONT_UI,
                11,
            ),
        ).pack(
            side="right",
            padx=6,
        )

        # ----------------------------------------------------
        # DEPLACEMENT DE LA PALETTE
        # ----------------------------------------------------

        drag = {}

        def drag_start(event):

            drag["root_x"] = (
                event.x_root
            )

            drag["root_y"] = (
                event.y_root
            )

            drag["x"] = (
                window.winfo_x()
            )

            drag["y"] = (
                window.winfo_y()
            )

        def drag_motion(event):

            if not drag:
                return

            dx = (
                event.x_root
                - drag["root_x"]
            )

            dy = (
                event.y_root
                - drag["root_y"]
            )

            new_x = (
                drag["x"]
                + dx
            )

            new_y = (
                drag["y"]
                + dy
            )

            try:

                screen_w = (
                    window.winfo_screenwidth()
                )

                screen_h = (
                    window.winfo_screenheight()
                )

                new_x = max(
                    0,
                    min(
                        new_x,
                        screen_w
                        - palette_width,
                    ),
                )

                new_y = max(
                    0,
                    min(
                        new_y,
                        screen_h
                        - palette_height
                        - 30,
                    ),
                )

                window.geometry(
                    f"+{new_x}+{new_y}"
                )

            except Exception:
                pass

        title_bar.bind(
            "<Button-1>",
            drag_start,
        )

        title_bar.bind(
            "<B1-Motion>",
            drag_motion,
        )

        # ----------------------------------------------------
        # RESUME
        # ----------------------------------------------------

        limited = int(
            audit.get(
                "limited",
                0,
            )
            or 0
        )

        critical = int(
            audit.get(
                "critical",
                0,
            )
            or 0
        )

        summary = tk.Frame(
            outer,
            bg=theme.PANEL,
        )

        summary.pack(
            fill="x",
            padx=16,
            pady=(14, 8),
        )

        tk.Label(
            summary,
            text=(
                f"{limited} limit\u00e9e"
                + (
                    ""
                    if limited == 1
                    else "s"
                )
                + "   \u00b7   "
                + f"{critical} non conforme"
                + (
                    ""
                    if critical == 1
                    else "s"
                )
            ),
            bg=theme.PANEL,
            fg=theme.INK,
            font=(
                theme.FONT_UI,
                9,
                "bold",
            ),
        ).pack(
            anchor="w",
        )

        tk.Label(
            summary,
            text=(
                "Cliquez sur une ligne pour afficher "
                "l'image correspondante."
            ),
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                8,
            ),
        ).pack(
            anchor="w",
            pady=(4, 0),
        )

        tk.Frame(
            outer,
            bg=theme.PAGE_BORDER,
            height=1,
        ).pack(
            fill="x",
            padx=16,
        )

        # ----------------------------------------------------
        # LISTE
        # ----------------------------------------------------

        list_canvas = tk.Canvas(
            outer,
            bg=theme.PANEL,
            bd=0,
            highlightthickness=0,
        )

        list_canvas.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=(10, 6),
        )

        rows = tk.Frame(
            list_canvas,
            bg=theme.PANEL,
        )

        rows_window = (
            list_canvas.create_window(
                4,
                0,
                anchor="nw",
                window=rows,
            )
        )

        def update_scroll(
            _event=None,
        ):

            try:

                list_canvas.configure(
                    scrollregion=(
                        list_canvas.bbox(
                            "all"
                        )
                    )
                )

                list_canvas.itemconfigure(
                    rows_window,
                    width=max(
                        1,
                        list_canvas.winfo_width()
                        - 8,
                    ),
                )

                list_canvas.xview_moveto(
                    0.0
                )

            except Exception:
                pass

        rows.bind(
            "<Configure>",
            update_scroll,
        )

        list_canvas.bind(
            "<Configure>",
            update_scroll,
        )

        selected = {
            "index": None
        }

        buttons = []

        detail_var = tk.StringVar(
            value=""
        )

        def highlight(index):

            selected["index"] = (
                index
            )

            for i, button in enumerate(
                buttons
            ):

                if i == index:

                    button.configure(
                        bg=theme.ACCENT,
                        fg=theme.WINDOW_DEEP,
                    )

                else:

                    button.configure(
                        bg=theme.WINDOW_DEEP,
                        fg=theme.INK,
                    )

        def open_issue(index):

            if not (
                0
                <= index
                < len(
                    issues
                )
            ):
                return

            issue = issues[
                index
            ]

            try:

                self._activate_page(
                    issue[
                        "page_id"
                    ]
                )

            except Exception:

                try:

                    self.session.set_active_page(
                        issue[
                            "page_id"
                        ]
                    )

                    self._composition_update_editor()

                except Exception:
                    return

            try:

                self.session.set_selection(
                    [
                        issue[
                            "element_id"
                        ]
                    ],
                    include_associated=False,
                )

                self._composition_update_inspector_context()

                canvas = getattr(
                    self,
                    "_composition_editor_canvas",
                    None,
                )

                if canvas is not None:

                    self._draw_page(
                        canvas
                    )

            except Exception:
                pass

            detail_var.set(
                f"{issue['width_px']} x "
                f"{issue['height_px']} px   \u00b7   "
                f"{issue['width_mm']:.1f} x "
                f"{issue['height_mm']:.1f} mm   \u00b7   "
                f"{issue['dpi']:.0f} dpi"
            )

            highlight(
                index
            )

            try:
                window.lift()
            except Exception:
                pass

        # ----------------------------------------------------
        # LIGNES COMPACTES
        # ----------------------------------------------------

        for index, issue in enumerate(
            issues
        ):

            status = (
                "NON CONFORME"
                if issue[
                    "status"
                ] == "critical"
                else "LIMIT\u00c9E"
            )

            label = (
                f"Page {issue['page_number']}   "
                f"\u00b7   {status}   "
                f"\u00b7   {issue['dpi']:.0f} dpi"
            )

            button = tk.Button(
                rows,
                text=label,
                command=(
                    lambda i=index:
                        open_issue(i)
                ),
                bg=theme.WINDOW_DEEP,
                fg=theme.INK,
                activebackground=theme.ACCENT,
                activeforeground=theme.WINDOW_DEEP,
                relief="flat",
                bd=0,
                cursor="hand2",
                anchor="w",
                padx=10,
                pady=8,
                font=(
                    theme.FONT_UI,
                    9,
                ),
            )

            button.pack(
                fill="x",
                pady=(0, 4),
            )

            buttons.append(
                button
            )

        # ----------------------------------------------------
        # MOLETTE
        # ----------------------------------------------------

        def wheel(event):

            direction = (
                -1
                if event.delta > 0
                else 1
            )

            try:

                list_canvas.yview_scroll(
                    direction * 3,
                    "units",
                )

            except Exception:
                pass

            return "break"

        list_canvas.bind(
            "<MouseWheel>",
            wheel,
        )

        rows.bind(
            "<MouseWheel>",
            wheel,
        )

        for button in buttons:

            button.bind(
                "<MouseWheel>",
                wheel,
            )

        # ----------------------------------------------------
        # DETAIL IMAGE ACTIVE
        # ----------------------------------------------------

        detail = tk.Label(
            outer,
            textvariable=detail_var,
            bg=theme.PANEL,
            fg=theme.MUTED,
            anchor="w",
            font=(
                theme.FONT_UI,
                8,
            ),
        )

        detail.pack(
            fill="x",
            padx=16,
            pady=(0, 8),
        )

        # ----------------------------------------------------
        # PRECEDENTE / SUIVANTE
        # ----------------------------------------------------

        footer = tk.Frame(
            outer,
            bg=theme.PANEL,
        )

        footer.pack(
            fill="x",
            padx=16,
            pady=(0, 14),
        )

        def previous_issue():

            index = (
                selected["index"]
                if selected[
                    "index"
                ] is not None
                else 0
            )

            open_issue(
                max(
                    0,
                    index - 1,
                )
            )

        def next_issue():

            index = (
                selected["index"]
                if selected[
                    "index"
                ] is not None
                else -1
            )

            open_issue(
                min(
                    len(
                        issues
                    )
                    - 1,
                    index + 1,
                )
            )

        tk.Button(
            footer,
            text="\u2039",
            command=previous_issue,
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            activebackground=theme.ACCENT,
            activeforeground=theme.WINDOW_DEEP,
            relief="flat",
            bd=0,
            cursor="hand2",
            width=4,
            pady=6,
            font=(
                theme.FONT_UI,
                10,
                "bold",
            ),
        ).pack(
            side="left",
        )

        tk.Button(
            footer,
            text="\u203a",
            command=next_issue,
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            activebackground=theme.ACCENT,
            activeforeground=theme.WINDOW_DEEP,
            relief="flat",
            bd=0,
            cursor="hand2",
            width=4,
            pady=6,
            font=(
                theme.FONT_UI,
                10,
                "bold",
            ),
        ).pack(
            side="left",
            padx=(6, 0),
        )

        tk.Button(
            footer,
            text="Fermer",
            command=close_palette,
            bg=theme.PANEL,
            fg=theme.MUTED,
            activebackground=theme.WINDOW_DEEP,
            activeforeground=theme.INK,
            relief="flat",
            bd=0,
            cursor="hand2",
            padx=10,
            pady=6,
            font=(
                theme.FONT_UI,
                8,
            ),
        ).pack(
            side="right",
        )

        try:
            window.lift()
        except Exception:
            pass

    def _composition_guard_image_geometry(
        self,
        state,
        geometry,
    ):

        from src.v4.image_quality import (
            effective_dpi,
            MINIMUM_DPI,
        )

        if (
            not isinstance(
                state,
                dict,
            )
            or not isinstance(
                geometry,
                dict,
            )
        ):
            return geometry

        if str(
            state.get(
                "kind",
                "",
            )
        ).lower() != "image":
            return geometry

        element = (
            self._composition_selected_element()
        )

        if not isinstance(
            element,
            dict,
        ):
            return geometry

        payload = element.get(
            "payload",
            {},
        )

        base = state.get(
            "geometry",
            {},
        )

        if (
            not isinstance(
                payload,
                dict,
            )
            or not isinstance(
                base,
                dict,
            )
        ):
            return geometry

        try:

            width_px = int(
                payload.get(
                    "width_px",
                    0,
                )
                or 0
            )

            height_px = int(
                payload.get(
                    "height_px",
                    0,
                )
                or 0
            )

            base_width = float(
                base[
                    "width_mm"
                ]
            )

            base_height = float(
                base[
                    "height_mm"
                ]
            )

            requested_width = float(
                geometry[
                    "width_mm"
                ]
            )

            requested_height = float(
                geometry[
                    "height_mm"
                ]
            )

        except (
            KeyError,
            TypeError,
            ValueError,
        ):
            return geometry

        if (
            width_px <= 0
            or height_px <= 0
            or base_width <= 0
            or base_height <= 0
        ):
            return geometry

        try:

            current = effective_dpi(
                width_px=width_px,
                height_px=height_px,
                width_mm=base_width,
                height_mm=base_height,
            )

        except ValueError:
            return geometry

        # Taille maximale absolue pour 200 dpi.
        absolute_max_width = (
            width_px
            / MINIMUM_DPI
            * 25.4
        )

        absolute_max_height = (
            height_px
            / MINIMUM_DPI
            * 25.4
        )

        # Une image deja critique ne doit jamais
        # etre agrandie davantage. La reduire reste libre.
        if (
            current.effective_dpi
            < MINIMUM_DPI
        ):

            allowed_width = base_width
            allowed_height = base_height

        else:

            allowed_width = (
                absolute_max_width
            )

            allowed_height = (
                absolute_max_height
            )

        result = dict(
            geometry
        )

        handle = str(
            state.get(
                "handle",
                "",
            )
            or ""
        ).lower()

        original_right = (
            float(
                geometry[
                    "x_mm"
                ]
            )
            + requested_width
        )

        original_bottom = (
            float(
                geometry[
                    "y_mm"
                ]
            )
            + requested_height
        )

        hit = False

        # Poignees d'angle :
        # conserver la proportion calculee par
        # le moteur geometrique.
        if handle in (
            "nw",
            "ne",
            "sw",
            "se",
        ):

            factor = min(
                1.0,
                allowed_width
                / requested_width,
                allowed_height
                / requested_height,
            )

            if factor < 1.0:

                hit = True

                new_width = (
                    requested_width
                    * factor
                )

                new_height = (
                    requested_height
                    * factor
                )

                result[
                    "width_mm"
                ] = new_width

                result[
                    "height_mm"
                ] = new_height

                if "w" in handle:

                    result[
                        "x_mm"
                    ] = (
                        original_right
                        - new_width
                    )

                if "n" in handle:

                    result[
                        "y_mm"
                    ] = (
                        original_bottom
                        - new_height
                    )

        else:

            new_width = min(
                requested_width,
                allowed_width,
            )

            new_height = min(
                requested_height,
                allowed_height,
            )

            if (
                new_width
                < requested_width
                - 0.001
            ):

                hit = True

                result[
                    "width_mm"
                ] = new_width

                if "w" in handle:

                    result[
                        "x_mm"
                    ] = (
                        original_right
                        - new_width
                    )

            if (
                new_height
                < requested_height
                - 0.001
            ):

                hit = True

                result[
                    "height_mm"
                ] = new_height

                if "n" in handle:

                    result[
                        "y_mm"
                    ] = (
                        original_bottom
                        - new_height
                    )

        state[
            "image_quality_guardrail_hit"
        ] = hit

        return result


    def _composition_spread_for_page_id(
        self,
        page_id: str | None,
    ):
        if page_id is None:
            return None

        try:
            return page_spread(
                self.session.book,
                str(page_id),
            )
        except Exception:
            return None


    def _composition_page_id_at_canvas_point(
        self,
        event,
    ) -> str | None:
        """Retourne la page physique sous le pointeur dans la vue centrale."""

        for page_id, view in getattr(
            self,
            "_composition_page_views",
            {},
        ).items():
            if not isinstance(view, dict):
                continue

            try:
                x = float(view["x"])
                y = float(view["y"])
                page_w = float(view["page_w"])
                page_h = float(view["page_h"])
            except (KeyError, TypeError, ValueError):
                continue

            if (
                x <= float(event.x) <= x + page_w
                and y <= float(event.y) <= y + page_h
            ):
                return str(page_id)

        return None


    def _composition_draw_spread_companion_preview(
        self,
        canvas: tk.Canvas,
        page,
        view: dict,
    ) -> None:
        """
        Dessine la seconde page d'une double page comme contexte visuel.

        La page active reste le seul plan d'édition à cet instant. Un clic
        sur la seconde moitié la rend active sans quitter la vue double.
        """

        x = float(view["x"])
        y = float(view["y"])
        page_w = float(view["page_w"])
        page_h = float(view["page_h"])
        automatic_page = is_auto_origin_page(page)
        page_fill = "#E7A3B0" if automatic_page else theme.PAGE

        canvas.create_rectangle(
            x,
            y,
            x + page_w,
            y + page_h,
            fill=page_fill,
            outline=theme.PAGE_BORDER,
        )

        preview = self._composition_source_thumbnail(
            page,
            width=max(120, int(round(page_w))),
            height=max(160, int(round(page_h))),
        )

        if preview is not None:
            photos = getattr(
                self,
                "_composition_spread_preview_photos",
                {},
            )
            photos[str(page.id)] = preview
            self._composition_spread_preview_photos = photos

            canvas.create_image(
                x + page_w / 2,
                y + page_h / 2,
                image=preview,
                anchor="center",
            )
        else:
            canvas.create_text(
                x + page_w / 2,
                y + page_h / 2,
                text=(
                    page.title
                    or page.page_type
                    or (
                        "Page automatique"
                        if automatic_page
                        else "Page"
                    )
                ),
                fill="#6B4B52" if automatic_page else "#777777",
                width=max(120, int(page_w * 0.70)),
                justify="center",
                font=(theme.FONT_UI, 9),
            )

        canvas.create_rectangle(
            x,
            y,
            x + page_w,
            y + page_h,
            fill="",
            outline=theme.PAGE_BORDER,
        )
        self._composition_draw_layout_guides(canvas, page, view)


    def _composition_draw_generated_page_content(
        self,
        canvas: tk.Canvas,
        page,
        *,
        page_x: float,
        page_y: float,
        scale: float,
    ) -> bool:
        """Dessine une page recomposee par TomeLinea sans fond Source PDF."""

        if not bool(getattr(page, "metadata", {}).get("format_reflow_generated", False)):
            return False

        drawn = False
        photos = {}
        for element in getattr(page, "content", ()):
            if not isinstance(element, dict):
                continue
            if str(element.get("kind", "") or "").strip().lower() != "text":
                continue

            geometry = element.get("geometry", {})
            payload = element.get("payload", {})
            if not isinstance(geometry, dict) or not isinstance(payload, dict):
                continue

            value = str(payload.get("text", "") or "").strip()
            if not value:
                continue

            try:
                gx = float(geometry.get("x_mm", 0.0) or 0.0)
                gy = float(geometry.get("y_mm", 0.0) or 0.0)
                gw = max(1.0, float(geometry.get("width_mm", 1.0) or 1.0))
            except (TypeError, ValueError):
                continue

            # Sur la machine de l'utilisateur, employer la police Source exacte
            # lorsqu'elle est disponible. Le canevas Tk reste seulement le
            # secours lorsque cette police ne peut pas être retrouvée.
            rendered = None
            try:
                rendered = self._composition_render_reflow_text(
                    element,
                    geometry,
                    scale,
                )
            except Exception:
                rendered = None

            if rendered is not None:
                try:
                    photo = ImageTk.PhotoImage(rendered)
                    canvas.create_image(
                        float(page_x) + gx * float(scale),
                        float(page_y) + gy * float(scale),
                        image=photo,
                        anchor="nw",
                        tags=("composition_reflow_text",),
                    )
                    photos[str(element.get("id", "") or id(element))] = photo
                    drawn = True
                    continue
                except Exception:
                    pass

            font_size_pt = 10.0
            color = "#202020"
            spans = payload.get("spans", [])
            if isinstance(spans, list) and spans and isinstance(spans[0], dict):
                try:
                    font_size_pt = max(5.0, float(spans[0].get("size", 10.0) or 10.0))
                except (TypeError, ValueError):
                    font_size_pt = 10.0
                try:
                    rgb = int(spans[0].get("color", 0) or 0) & 0xFFFFFF
                    color = f"#{rgb:06x}"
                except (TypeError, ValueError):
                    color = "#202020"

            font_px = max(7, int(round(font_size_pt * 25.4 / 72.0 * float(scale))))
            canvas.create_text(
                float(page_x) + gx * float(scale),
                float(page_y) + gy * float(scale),
                text=value,
                anchor="nw",
                width=max(20, int(round(gw * float(scale))),),
                justify="left",
                fill=color,
                font=(theme.FONT_UI, -font_px),
                tags=("composition_reflow_text",),
            )
            drawn = True

        self._composition_reflow_generated_photos = photos
        if drawn:
            self._composition_draw_selection(canvas)
        return drawn


    def _composition_draw_layout_guides(
        self,
        canvas: tk.Canvas,
        page,
        view: dict | None,
    ) -> None:
        """Dessine les marges et le fond perdu du Livre sur la page centrale.

        Ces repères sont visibles par défaut et peuvent être masqués sans
        modifier les valeurs du Livre. Intérieur / extérieur suivent la
        position physique recto-verso.
        """

        if not isinstance(view, dict):
            return

        try:
            x = float(view["x"])
            y = float(view["y"])
            page_w = float(view["page_w"])
            page_h = float(view["page_h"])
            scale = float(view["scale"])
        except (KeyError, TypeError, ValueError):
            return

        fmt = self.session.book.format

        if bool(getattr(self, "_composition_bleed_guides_visible", True)):
            try:
                bleed_left = max(0.0, float(fmt.bleed_left_mm)) * scale
                bleed_right = max(0.0, float(fmt.bleed_right_mm)) * scale
                bleed_top = max(0.0, float(fmt.bleed_top_mm)) * scale
                bleed_bottom = max(0.0, float(fmt.bleed_bottom_mm)) * scale
            except (TypeError, ValueError):
                bleed_left = bleed_right = bleed_top = bleed_bottom = 0.0

            if max(bleed_left, bleed_right, bleed_top, bleed_bottom) > 0.01:
                canvas.create_rectangle(
                    x - bleed_left,
                    y - bleed_top,
                    x + page_w + bleed_right,
                    y + page_h + bleed_bottom,
                    fill="",
                    outline=theme.BLEED,
                    width=2,
                    dash=(6, 4),
                    tags=("composition_layout_guides", "composition_bleed_guide"),
                )

        # Les marges sont un repère global du Livre et restent visibles sur
        # toutes les pages, y compris les couvertures pleine page. Une image
        # peut dépasser ces marges sans les faire disparaître : le repère sert
        # précisément à montrer cette différence entre contenu pleine page et
        # zone de texte sûre.
        if bool(getattr(self, "_composition_margin_guides_visible", True)):
            side = str(getattr(page, "recto_verso", "") or "").strip().lower()
            if side not in {"recto", "verso"}:
                try:
                    index = self.session.book.page_order.index(str(page.id))
                    side = "recto" if index % 2 == 0 else "verso"
                except Exception:
                    side = "recto"

            try:
                top = max(0.0, float(fmt.margin_top_mm)) * scale
                bottom = max(0.0, float(fmt.margin_bottom_mm)) * scale
                inside = max(0.0, float(fmt.margin_inside_mm)) * scale
                outside = max(0.0, float(fmt.margin_outside_mm)) * scale
            except (TypeError, ValueError):
                return

            left = inside if side == "recto" else outside
            right = outside if side == "recto" else inside
            x0 = x + min(left, max(0.0, page_w - 1.0))
            x1 = x + page_w - min(right, max(0.0, page_w - 1.0))
            y0 = y + min(top, max(0.0, page_h - 1.0))
            y1 = y + page_h - min(bottom, max(0.0, page_h - 1.0))

            if x1 > x0 and y1 > y0:
                canvas.create_rectangle(
                    x0, y0, x1, y1,
                    fill="",
                    outline=theme.ACCENT_BRIGHT,
                    width=2,
                    dash=(5, 3),
                    tags=("composition_layout_guides", "composition_margin_guide"),
                )


    def _draw_page(
        self,
        canvas: tk.Canvas,
    ) -> None:

        canvas.delete(
            "all"
        )

        page = (
            self.session.active_page
        )

        if page is None:
            return

        book = self.session.book
        fmt = book.format

        width = max(
            canvas.winfo_width(),
            100,
        )

        height = max(
            canvas.winfo_height(),
            100,
        )

        spread_pair = self._composition_spread_for_page_id(
            page.id
        )
        spread_mode = spread_pair is not None

        fit_width_mm = float(fmt.width_mm) * (
            2.0 if spread_mode else 1.0
        )

        fit_scale = min(
            (width - 140)
            / max(1.0, fit_width_mm),
            (height - 100)
            / float(fmt.height_mm),
        )

        fit_scale = max(
            0.2,
            fit_scale,
        )

        zoom = float(
            getattr(
                self,
                "_composition_zoom_factor",
                1.0,
            )
            or 1.0
        )

        zoom = max(
            0.25,
            min(
                5.0,
                zoom,
            ),
        )

        self._composition_zoom_factor = (
            zoom
        )

        scale = (
            fit_scale
            * zoom
        )

        zoom_var = getattr(
            self,
            "_composition_zoom_var",
            None,
        )

        if zoom_var is not None:
            zoom_var.set(
                f"{int(round(zoom * 100))} %"
            )

        page_w = (
            float(fmt.width_mm)
            * scale
        )

        page_h = (
            float(fmt.height_mm)
            * scale
        )

        pan_x = float(
            getattr(
                self,
                "_composition_pan_x",
                0.0,
            )
            or 0.0
        )
        pan_y = float(
            getattr(
                self,
                "_composition_pan_y",
                0.0,
            )
            or 0.0
        )

        y = (
            height / 2
            - page_h / 2
            + pan_y
        )

        self._composition_spread_preview_photos = {}
        self._composition_page_views = {}

        if spread_mode:
            spread_x = (
                width / 2
                - page_w
                + pan_x
            )
            left_x = spread_x
            right_x = spread_x + page_w

            left_view = {
                "page_id": spread_pair.left_page_id,
                "x": left_x,
                "y": y,
                "page_w": page_w,
                "page_h": page_h,
                "scale": scale,
            }
            right_view = {
                "page_id": spread_pair.right_page_id,
                "x": right_x,
                "y": y,
                "page_w": page_w,
                "page_h": page_h,
                "scale": scale,
            }

            self._composition_page_views = {
                spread_pair.left_page_id: left_view,
                spread_pair.right_page_id: right_view,
            }

            active_view = (
                left_view
                if page.id == spread_pair.left_page_id
                else right_view
            )
            x = float(active_view["x"])
            self._composition_page_view = active_view

            # La double page est dessinée comme une seule ouverture.
            canvas.create_rectangle(
                spread_x - 3,
                y - 3,
                spread_x + page_w * 2 + 3,
                y + page_h + 3,
                fill="",
                outline="#D6B56C",
                width=2,
            )
            canvas.create_line(
                spread_x + page_w,
                y,
                spread_x + page_w,
                y + page_h,
                fill="#8E805F",
                width=1,
            )

            companion_id = (
                spread_pair.right_page_id
                if page.id == spread_pair.left_page_id
                else spread_pair.left_page_id
            )
            companion = book.pages.get(companion_id)
            companion_view = self._composition_page_views.get(companion_id)
            if companion is not None and companion_view is not None:
                self._composition_draw_spread_companion_preview(
                    canvas,
                    companion,
                    companion_view,
                )

        else:
            x = (
                width / 2
                - page_w / 2
                + pan_x
            )

            self._composition_page_view = {
                "page_id": page.id,
                "x": x,
                "y": y,
                "page_w": page_w,
                "page_h": page_h,
                "scale": scale,
            }
            self._composition_page_views = {
                page.id: self._composition_page_view,
            }

        # Le Canvas possède désormais son interaction
        # Composition sans créer de nouveau système
        # de sélection.
        canvas.bind(
            "<Button-1>",
            self._composition_pointer_press,
        )

        canvas.bind(
            "<MouseWheel>",
            self._composition_zoom_wheel,
        )

        canvas.bind(
            "<Motion>",
            self._composition_pointer_hover,
        )

        canvas.bind(
            "<KeyPress-space>",
            self._composition_space_pan_press,
        )

        canvas.bind(
            "<KeyRelease-space>",
            self._composition_space_pan_release,
        )

        canvas.bind(
            "<B1-Motion>",
            self._composition_pointer_motion,
        )

        canvas.bind(
            "<ButtonRelease-1>",
            self._composition_pointer_release,
        )

        canvas.bind(
            "<plus>",
            lambda _event:
                self._composition_zoom_in(),
        )

        canvas.bind(
            "<minus>",
            lambda _event:
                self._composition_zoom_out(),
        )

        canvas.bind(
            "<KP_Add>",
            lambda _event:
                self._composition_zoom_in(),
        )

        canvas.bind(
            "<KP_Subtract>",
            lambda _event:
                self._composition_zoom_out(),
        )

        # ======================================================
        # PAGE PHYSIQUE
        # ======================================================

        canvas.create_rectangle(
            x,
            y,
            x + page_w,
            y + page_h,
            fill=(
                "#E7A3B0"
                if is_auto_origin_page(page)
                else theme.PAGE
            ),
            outline=theme.PAGE_BORDER,
        )
        self._composition_draw_layout_guides(
            canvas, page, self._composition_page_view,
        )

        if spread_mode:
            canvas.create_rectangle(
                x - 2,
                y - 2,
                x + page_w + 2,
                y + page_h + 2,
                fill="",
                outline=theme.ERROR,
                width=2,
                tags=("composition_active_page_outline",),
            )
        # ======================================================
        # COUCHE SOURCE FIDELE
        #
        # A ce stade elle est volontairement non éditable.
        # Les futures zones TomeLinea viendront par-dessus.
        # ======================================================

        source_link = getattr(
            page,
            "source",
            None,
        )

        if source_link is None:

            # Une page issue d'une recomposition de format n'a plus une unique
            # page Source physique : son contenu Composition devient le rendu.
            if self._composition_draw_generated_page_content(
                canvas,
                page,
                page_x=x,
                page_y=y,
                scale=scale,
            ):
                canvas.create_rectangle(
                    x,
                    y,
                    x + page_w,
                    y + page_h,
                    fill="",
                    outline=theme.PAGE_BORDER,
                )
                canvas.tag_raise("composition_layout_guides")
                self._composition_draw_text_problem_highlight(canvas)
                return

            # Autre page creee par TomeLinea : aucune Source physique.
            canvas.create_text(
                x + page_w / 2,
                y + page_h / 2,
                text=(
                    page.title
                    or page.page_type
                    or "Page TomeLinea"
                ),
                fill="#777777",
                width=max(
                    120,
                    int(page_w * 0.70),
                ),
                justify="center",
                font=(
                    theme.FONT_UI,
                    9,
                ),
            )

            self._composition_draw_text_problem_highlight(canvas)
            return

        source_element_id = (
            getattr(
                source_link,
                "source_id",
                None,
            )
            or getattr(
                source_link,
                "source_element_id",
                None,
            )
        )

        source_version_id = (
            getattr(
                source_link,
                "source_version_id",
                None,
            )
            or getattr(
                source_link,
                "version_id",
                None,
            )
        )

        source_page_number = (
            getattr(
                source_link,
                "source_page",
                None,
            )
            or getattr(
                source_link,
                "page_number",
                None,
            )
        )

        if (
            source_element_id is None
            or source_page_number is None
        ):
            return

        project = (
            self.session.project
        )

        element = (
            project.source.elements.get(
                source_element_id
            )
        )

        if element is None:
            return

        version = None

        for candidate in element.versions:

            if (
                source_version_id is not None
                and candidate.id
                == source_version_id
            ):
                version = candidate
                break

        if version is None:
            version = (
                element.active_version
            )

        if version is None:
            return

        source_path = Path(
            version.original_path
        )

        # Première étape réelle :
        # rendu fidèle des PDF.
        if (
            source_path.suffix.lower()
            != ".pdf"
        ):

            canvas.create_text(
                x + page_w / 2,
                y + page_h / 2,
                text=(
                    "Source présente\n"
                    "Rendu Composition à venir "
                    "pour ce format"
                ),
                fill="#777777",
                justify="center",
                font=(
                    theme.FONT_UI,
                    9,
                ),
            )

            canvas.tag_raise("composition_layout_guides")
            self._composition_draw_text_problem_highlight(canvas)
            return

        if not source_path.is_file():

            canvas.create_text(
                x + page_w / 2,
                y + page_h / 2,
                text=(
                    "Fichier Source indisponible"
                ),
                fill="#777777",
                justify="center",
                font=(
                    theme.FONT_UI,
                    9,
                ),
            )

            canvas.tag_raise("composition_layout_guides")
            self._composition_draw_text_problem_highlight(canvas)
            return

        try:
            import pymupdf

            document = pymupdf.open(
                str(source_path)
            )

            pdf_index = (
                int(source_page_number)
                - 1
            )

            if not (
                0
                <= pdf_index
                < document.page_count
            ):
                document.close()
                return

            pdf_page = (
                document.load_page(
                    pdf_index
                )
            )

            rect = pdf_page.rect

            detached_images = (
                self._composition_prepare_detached_images(
                    document,
                    pdf_page,
                    page,
                    fmt,
                )
            )

            detached_texts = (
                self._composition_prepare_detached_texts(
                    document,
                    pdf_page,
                    page,
                    fmt,
                )
            )

            # On genere approximativement a la resolution
            # réellement nécessaire à l'écran.
            render_scale = min(
                page_w
                / max(
                    1.0,
                    float(rect.width),
                ),
                page_h
                / max(
                    1.0,
                    float(rect.height),
                ),
            )

            render_scale = max(
                0.25,
                render_scale * 1.35,
            )

            pix = pdf_page.get_pixmap(
                matrix=pymupdf.Matrix(
                    render_scale,
                    render_scale,
                ),
                alpha=False,
            )

            image = Image.frombytes(
                "RGB",
                (
                    pix.width,
                    pix.height,
                ),
                pix.samples,
            )

            document.close()

            target_w = max(
                1,
                int(page_w),
            )

            target_h = max(
                1,
                int(page_h),
            )

            if bool(getattr(page, "metadata", {}).get("format_content_adapted", False)):
                # Les objets ont été remappés sur le nouveau format. Le reliquat
                # graphique de la Source suit donc la même transformation afin
                # de rester aligné avec eux. Texte et images ont déjà été retirés
                # de cette couche puis redessinés par Composition.
                image = image.resize(
                    (target_w, target_h),
                    Image.Resampling.LANCZOS,
                )
            else:
                # Page à mise en page fixe : ne jamais tronquer la Source.
                image.thumbnail(
                    (
                        target_w,
                        target_h,
                    ),
                    Image.Resampling.LANCZOS,
                )

            photo = ImageTk.PhotoImage(
                image
            )

            # Important :
            # conserver la référence Tk.
            self._composition_source_photo = (
                photo
            )

            image_x = (
                x
                + page_w / 2
            )

            image_y = (
                y
                + page_h / 2
            )

            canvas.create_image(
                image_x,
                image_y,
                image=photo,
                anchor="center",
            )

            # Les images devenues objets Composition
            # sont dessinees au-dessus du fond Source.
            self._composition_draw_detached_images(
                canvas,
                detached_images,
                page_x=x,
                page_y=y,
                scale=scale,
            )

            self._composition_draw_detached_texts(
                canvas,
                detached_texts,
                page_x=x,
                page_y=y,
                scale=scale,
            )

            # Les zones modifiees par l'utilisateur
            # sont maintenant sous controle TomeLinea.

            # Fin contour physique :
            # il reste visible au-dessus de la Source.
            canvas.create_rectangle(
                x,
                y,
                x + page_w,
                y + page_h,
                fill="",
                outline=theme.PAGE_BORDER,
            )

            # Les zones sont invisibles au repos.
            # Seule la sélection active apparaît.
            self._composition_draw_selection(
                canvas
            )
            canvas.tag_raise("composition_layout_guides")
            canvas.tag_raise("composition_selection")
            self._composition_draw_text_problem_highlight(canvas)

        except Exception as exc:

            # Aucun message modal pendant un redraw.
            canvas.create_text(
                x + page_w / 2,
                y + page_h / 2,
                text=(
                    "Impossible d'afficher "
                    "la Source\n\n"
                    f"{exc}"
                ),
                fill="#777777",
                width=max(
                    150,
                    int(page_w * 0.75),
                ),
                justify="center",
                font=(
                    theme.FONT_UI,
                    8,
                ),
            )


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
