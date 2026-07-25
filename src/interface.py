import tkinter as tk

from src.menus import creer_menu


class InterfacePrincipale:

    LARGEUR_NAVIGATION = 220
    HAUTEUR_ACTIONS = 42
    HAUTEUR_STATUS = 24

    def __init__(self):

        self.fenetre = tk.Tk()

        self.fenetre.title("Générateur de livres - Les Graines de Sens")

        self.fenetre.geometry("1400x900")
        self.fenetre.minsize(1100, 700)

        creer_menu(self.fenetre)

        self.creer_interface()

    # ------------------------------------------------------------------

    def creer_interface(self):

        self.creer_barre_actions()

        self.creer_zone_centrale()

        self.creer_barre_etat()

    # ------------------------------------------------------------------

    def creer_barre_actions(self):

        self.barre_actions = tk.Frame(
            self.fenetre,
            height=self.HAUTEUR_ACTIONS,
            bd=1,
            relief="groove"
        )

        self.barre_actions.pack(
            side="top",
            fill="x"
        )

        boutons = [
            "📁 Projet",
            "📄 Nouveau",
            "📂 Ouvrir",
            "💾 Enregistrer",
            "👁 Aperçu",
            "🖨 Générer"
        ]

        for texte in boutons:

            tk.Button(
                self.barre_actions,
                text=texte,
                padx=10
            ).pack(
                side="left",
                padx=4,
                pady=4
            )

    # ------------------------------------------------------------------

    def creer_zone_centrale(self):

        self.zone_centrale = tk.Frame(self.fenetre)

        self.zone_centrale.pack(
            fill="both",
            expand=True
        )

        self.creer_navigation()

        self.creer_workspace()

    # ------------------------------------------------------------------

    def creer_navigation(self):

        self.navigation = tk.Frame(
            self.zone_centrale,
            width=self.LARGEUR_NAVIGATION,
            bd=1,
            relief="groove"
        )

        self.navigation.pack(
            side="left",
            fill="y"
        )

        self.navigation.pack_propagate(False)

        titre = tk.Label(
            self.navigation,
            text="Navigation",
            font=("Arial", 12, "bold")
        )

        titre.pack(
            pady=(10, 15)
        )

        elements = [
            "📚 Livre",
            "📖 Chapitres",
            "📄 Pages",
            "🖼 Ressources",
            "⚙ Paramètres"
        ]

        for element in elements:

            tk.Button(
                self.navigation,
                text=element,
                anchor="w"
            ).pack(
                fill="x",
                padx=8,
                pady=2
            )

    # ------------------------------------------------------------------

    def creer_workspace(self):

        self.workspace = tk.Frame(
            self.zone_centrale,
            bd=1,
            relief="groove"
        )

        self.workspace.pack(
            side="left",
            fill="both",
            expand=True
        )

        titre = tk.Label(
            self.workspace,
            text="Zone de travail",
            font=("Arial", 20, "bold")
        )

        titre.pack(
            pady=(50, 15)
        )

        texte = tk.Label(
            self.workspace,
            text=(
                "Bienvenue dans le Générateur de livres.\n\n"
                "Cette zone affichera successivement :\n"
                "• le mode Production\n"
                "• l'Atelier\n"
                "• les aperçus\n"
                "• les paramètres\n"
                "• les outils de génération"
            ),
            justify="center",
            font=("Arial", 11)
        )

        texte.pack()

    # ------------------------------------------------------------------

    def creer_barre_etat(self):

        self.barre_etat = tk.Frame(
            self.fenetre,
            height=self.HAUTEUR_STATUS,
            bd=1,
            relief="groove"
        )

        self.barre_etat.pack(
            side="bottom",
            fill="x"
        )

        self.barre_etat.pack_propagate(False)

        self.message = tk.Label(
            self.barre_etat,
            text="Prêt",
            anchor="w"
        )

        self.message.pack(
            side="left",
            padx=8
        )

    # ------------------------------------------------------------------

    def lancer(self):

        self.fenetre.mainloop()