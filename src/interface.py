import tkinter as tk
from src.menus import creer_menu


class InterfacePrincipale:

    def __init__(self):

        self.fenetre = tk.Tk()

        self.fenetre.title("Générateur de fiches - Les Graines de Sens")

        self.fenetre.geometry("1200x800")

        creer_menu(self.fenetre)

        self.creer_zone_centrale()

    def creer_zone_centrale(self):

        cadre = tk.Frame(self.fenetre)

        cadre.pack(fill="both", expand=True)

        titre = tk.Label(
            cadre,
            text="Générateur de fiches",
            font=("Arial", 24, "bold")
        )

        titre.pack(pady=30)

        texte = tk.Label(
            cadre,
            text="Bienvenue.\n\nLe logiciel est prêt à être développé.",
            font=("Arial", 12)
        )

        texte.pack()

    def lancer(self):

        self.fenetre.mainloop()