def _create_navigation(self) -> None:

    self.navigation = tk.Frame(
        self.zone_centrale,
        width=self.LARGEUR_NAVIGATION,
        bd=1,
        relief="groove",
    )

    self.navigation.pack(
        side="left",
        fill="y",
    )

    self.navigation.pack_propagate(False)

    tk.Label(
        self.navigation,
        text="Projet",
        font=("Arial", 12, "bold"),
    ).pack(
        pady=(10, 15),
    )

    sections = [

        ("📁 Gestion des projets", (
            "Tableau de bord",
            "Documents",
        )),

        ("📚 Contenu", (
            "Pages",
            "Composants",
            "Styles",
        )),

        ("🖼 Ressources", (
            "Images",
            "Illustrations",
            "Icônes",
            "Logos",
        )),

        ("🌿 Modules", (
            "Botanique",
        )),

        ("📦 Export", (
            "Contrôle",
            "Exports",
        )),
    ]

    for titre, entrees in sections:

        tk.Label(
            self.navigation,
            text=titre,
            anchor="w",
            font=("Arial", 10, "bold"),
        ).pack(
            fill="x",
            padx=8,
            pady=(8, 2),
        )

        for entree in entrees:

            tk.Button(
                self.navigation,
                text=entree,
                anchor="w",
            ).pack(
                fill="x",
                padx=18,
                pady=1,
            )