import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

from src.core.document_manager import DocumentManager


class MenuBar:

    def __init__(self, root, project_manager, workspace):

        self.root = root
        self.project_manager = project_manager
        self.workspace = workspace

        self.document_manager = DocumentManager(project_manager)

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
            label="Nouveau document",
            command=self.new_document
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

        self.workspace.show_documents(
            self.project_manager.get_project()
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

            self.workspace.show_documents(
                self.project_manager.get_project()
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

    def new_document(self):

        if not self.project_manager.has_project():

            messagebox.showwarning(
                "Aucun projet",
                "Ouvrez ou créez un projet avant de créer un document."
            )

            return

        nom = simpledialog.askstring(
            "Nouveau document",
            "Nom du document :"
        )

        if not nom:
            return

        self.document_manager.new_document(nom)

        self.workspace.show_documents(
            self.project_manager.get_project()
        )

        messagebox.showinfo(
            "Document créé",
            f"Le document '{nom}' a été créé."
        )