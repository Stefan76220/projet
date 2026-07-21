import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox


class MenuBar:

    def __init__(self, root, project_manager):

        self.root = root
        self.project_manager = project_manager

        self.menu = tk.Menu(root)

        fichier = tk.Menu(self.menu, tearoff=False)

        fichier.add_command(
            label="Nouveau projet",
            command=self.new_project
        )

        fichier.add_command(
            label="Ouvrir un projet",
            command=self.open_project
        )

        fichier.add_separator()

        fichier.add_command(
            label="Quitter",
            command=root.destroy
        )

        self.menu.add_cascade(
            label="Fichier",
            menu=fichier
        )

        self.root.config(menu=self.menu)

    def new_project(self):

        dossier = filedialog.askdirectory(
            title="Choisir le dossier du projet"
        )

        if not dossier:
            return

        nom = simpledialog.askstring(
            "Nouveau projet",
            "Nom du projet :"
        )

        if not nom:
            return

        self.project_manager.new_project(
            dossier,
            nom
        )

        self.root.title(
            f"Générateur de livres - {self.project_manager.get_project_name()}"
        )

        messagebox.showinfo(
            "Projet créé",
            f"Le projet '{nom}' a été créé."
        )

    def open_project(self):

        dossier = filedialog.askdirectory(
            title="Choisir le dossier du projet"
        )

        if not dossier:
            return

        try:

            self.project_manager.open_project(dossier)

            self.root.title(
                f"Générateur de livres - {self.project_manager.get_project_name()}"
            )

            messagebox.showinfo(
                "Projet ouvert",
                f"Le projet '{self.project_manager.get_project_name()}' est ouvert."
            )

        except Exception as e:

            messagebox.showerror(
                "Erreur",
                str(e)
            )