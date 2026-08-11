from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from src.gui_v2 import theme


class PageMaitreV2(tk.Tk):
    """Prototype parallèle : tous les grands écrans existent en permanence."""

    def __init__(self) -> None:
        super().__init__()

        self.title("PageMaître — Interface V2")
        self.configure(bg=theme.WINDOW)
        self.minsize(1180, 720)
        self.geometry("1400x860")

        self._screens: dict[str, tk.Frame] = {}
        self._nav_buttons: dict[str, tk.Button] = {}
        self._active = "accueil"

        self._configure_style()
        self._build_shell()
        self._build_all_screens_once()
        self.show_screen("accueil")

        try:
            self.state("zoomed")
        except tk.TclError:
            pass

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

        self.header = tk.Frame(
            self,
            bg=theme.PANEL,
            height=76,
            highlightthickness=1,
            highlightbackground=theme.BORDER,
        )
        self.header.grid(row=0, column=0, sticky="ew")
        self.header.grid_propagate(False)

        brand = tk.Frame(self.header, bg=theme.PANEL)
        brand.pack(side="left", padx=(22, 16), pady=10)

        tk.Label(
            brand,
            text="PageMaître",
            bg=theme.PANEL,
            fg=theme.INK,
            font=("Segoe UI", 19, "bold"),
        ).pack(anchor="w")

        tk.Label(
            brand,
            text="Concevez, organisez, publiez",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=("Segoe UI", 9),
        ).pack(anchor="w")

        self.nav = tk.Frame(self.header, bg=theme.PANEL)
        self.nav.pack(side="left", fill="x", expand=True, padx=10)

        for key, icon, label, accent in theme.NAV_ITEMS:
            btn = tk.Button(
                self.nav,
                text=f"{icon}  {label}",
                command=lambda name=key: self.show_screen(name),
                relief="flat",
                bd=0,
                padx=12,
                pady=9,
                bg=theme.PANEL,
                fg=theme.INK,
                activebackground=accent,
                activeforeground=theme.INK,
                font=("Segoe UI", 9, "bold"),
                cursor="hand2",
            )
            btn.pack(side="left", padx=2)
            self._nav_buttons[key] = btn

        manage = tk.Button(
            self.header,
            text="⚙  Gérer",
            command=self.open_manage_window,
            relief="flat",
            bd=0,
            padx=14,
            pady=9,
            bg=theme.INK,
            fg=theme.WHITE,
            activebackground=theme.CORAL,
            activeforeground=theme.WHITE,
            font=("Segoe UI", 9, "bold"),
            cursor="hand2",
        )
        manage.pack(side="right", padx=18)

        self.host = tk.Frame(self, bg=theme.WINDOW)
        self.host.grid(row=1, column=0, sticky="nsew")
        self.host.grid_rowconfigure(0, weight=1)
        self.host.grid_columnconfigure(0, weight=1)

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

        for key, btn in self._nav_buttons.items():
            accent = next(
                (item[3] for item in theme.NAV_ITEMS if item[0] == key),
                theme.SKY,
            )
            if key == name:
                btn.configure(bg=accent, fg=theme.INK)
            else:
                btn.configure(bg=theme.PANEL, fg=theme.INK)

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

    def _build_accueil(self, parent: tk.Frame) -> None:
        self._screen_header(
            parent,
            "Accueil",
            "Ouverture et accès aux projets — prototype V2",
            theme.SKY,
            visualisation=False,
        )

        hero = tk.Frame(parent, bg=theme.WINDOW)
        hero.pack(fill="x", padx=22, pady=8)

        left = self._card(
            hero,
            "Projet actif",
            "Projet de démonstration\nStructure visuelle conservée, fonctions non branchées.",
            accent=theme.CELADON,
            width=430,
            height=190,
        )
        left.pack(side="left", fill="x", expand=True, padx=(0, 7))

        right = self._card(
            hero,
            "Accès rapide",
            "Les boutons de navigation du bandeau supérieur sont actifs.",
            accent=theme.LILAC,
            width=430,
            height=190,
        )
        right.pack(side="left", fill="x", expand=True, padx=(7, 0))

        tools = tk.Frame(parent, bg=theme.WINDOW)
        tools.pack(fill="x", padx=22, pady=12)

        for label in (
            "Nouveau projet",
            "Ouvrir un projet",
            "Dupliquer",
            "Archiver",
            "Bibliothèque",
            "Ressources",
        ):
            self._disabled_button(tools, label).pack(
                side="left",
                padx=(0, 7),
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
            color = (theme.SKY, theme.LILAC, theme.CELADON, theme.CORAL)[index % 4]
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
                accent=(theme.SKY, theme.CELADON, theme.LILAC, theme.CORAL)[idx % 4],
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
