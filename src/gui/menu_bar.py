from __future__ import annotations

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog

from src.core.document_manager import DocumentManager


class MenuBar:
    """
    Barre de menus principale de l'application.
    """

    def __init__(
        self,
        root,
        project_manager,
        workspace,
    ) -> None:

        self.root = root
        self.project_manager = project_manager
        self.workspace = workspace

        self.document_manager = DocumentManager(project_manager)

        self.menu = tk.Menu(root)

        self._build_file_menu()

        self.root.config(menu=self.menu)

    # ==========================================================
    # Construction des menus
    # ==========================================================

    def _build_file_menu(self) -> None:

        fichier = tk.Menu(
            self.menu,
            tearoff=False,
        )

        fichier.add_command(
            label="Nouveau projet",
            command=self.new_project,
        )

        fichier.add_command(
            label="Ouvrir un projet",
            command=self.open_project,
        )

        fichier.add_separator()

        fichier.add_command(
            label="Nouveau document",
            command=self.new_document,
        )

        fichier.add_separator()

        fichier.add_command(
            label="Quitter",
            command=self.root.destroy,
        )

        self.menu.add_cascade(
            label="Fichier",
            menu=fichier,
        )

    # ==========================================================
    # Projets
    # ==========================================================

    def new_project(self) -> None:

        dossier = filedialog.askdirectory(
            title="Choisir le dossier du projet",
        )

        if not dossier:
            return

        nom = simpledialog.askstring(
            "Nouveau projet",
            "Nom du projet :",
        )

        if not nom:
            return

        self.project_manager.new_project(
            dossier,
            nom,
        )

        self._refresh_workspace()

        messagebox.showinfo(
            "Projet créé",
            f"Le projet '{nom}' a été créé.",
        )

    def open_project(self) -> None:

        dossier = filedialog.askdirectory(
            title="Choisir le dossier du projet",
        )

        if not dossier:
            return

        try:

            self.project_manager.open_project(
                dossier,
            )

            self._refresh_workspace()

            messagebox.showinfo(
                "Projet ouvert",
                (
                    f"Le projet "
                    f"'{self.project_manager.get_project_name()}' "
                    f"est ouvert."
                ),
            )

        except Exception as exc:

            messagebox.showerror(
                "Erreur",
                str(exc),
            )

    # ==========================================================
    # Documents
    # ==========================================================

    def new_document(self) -> None:

        if not self.project_manager.has_project():

            messagebox.showwarning(
                "Aucun projet",
                (
                    "Ouvrez ou créez un projet "
                    "avant de créer un document."
                ),
            )

            return

        nom = simpledialog.askstring(
            "Nouveau document",
            "Nom du document :",
        )

        if not nom:
            return

        self.document_manager.new_document(
            nom,
        )

        self.workspace.show_documents(
            self.project_manager.get_project(),
        )

        messagebox.showinfo(
            "Document créé",
            f"Le document '{nom}' a été créé.",
        )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def _refresh_workspace(self) -> None:

        self.root.title(
            "Générateur de livres - "
            f"{self.project_manager.get_project_name()}"
        )

        self.workspace.show_documents(
            self.project_manager.get_project(),
        )

    def __repr__(self) -> str:

        return (
            f"MenuBar("
            f"project={self.project_manager.get_project_name() if self.project_manager.has_project() else None!r})"
        )