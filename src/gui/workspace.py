from __future__ import annotations

import customtkinter as ctk

from src.gui.views.dashboard_view import DashboardView
from src.gui.views.document_editor_view import DocumentEditorView
from src.gui.views.document_view import DocumentView
from src.theme.colors import Colors


class Workspace:
    """
    Zone de travail principale de l'application.

    Cette classe pilote les différentes vues affichées
    (tableau de bord, liste des documents, éditeur).
    """

    def __init__(
        self,
        parent,
        application,
    ) -> None:

        self.application = application
        self.current_project = None

        self.frame = ctk.CTkFrame(
            parent,
            fg_color=Colors.WINDOW,
            corner_radius=0,
        )

        self.frame.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        self.show_dashboard()

    # ==========================================================
    # Gestion des vues
    # ==========================================================

    def clear(self) -> None:

        for widget in self.frame.winfo_children():
            widget.destroy()

    def show_dashboard(self) -> None:

        self.clear()

        DashboardView(
            self.frame,
        ).show()

    def show_documents(
        self,
        project,
    ) -> None:

        self.current_project = project

        self.clear()

        DocumentView(
            self.frame,
            project,
            self.application,
            on_open_document=self.show_document,
            on_refresh=self.back_to_documents,
        ).show()

    def show_document(
        self,
        document_info,
    ) -> None:

        self.clear()

        self.application.document_manager.load_document(
            document_info["nom"],
        )

        DocumentEditorView(
            self.frame,
            self.application,
            on_back=self.back_to_documents,
        ).show()

    def back_to_documents(self) -> None:

        if self.current_project is not None:
            self.show_documents(self.current_project)

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"Workspace("
            f"current_project={self.current_project!r})"
        )