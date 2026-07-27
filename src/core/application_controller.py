from __future__ import annotations

from tkinter import messagebox

from src.core.document import Document


class ApplicationController:
    """
    Contrôleur principal de l'application.
    Coordonne les échanges entre l'interface et les services.
    """

    def __init__(self, application) -> None:

        self.application = application

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def project_manager(self):

        return self.application.project_manager

    @property
    def document_manager(self):

        return self.application.document_manager

    @property
    def window(self):

        return self.application.window

    @property
    def workspace(self):

        return self.window.workspace

    # ==========================================================
    # Documents
    # ==========================================================

    def create_document(self, name: str) -> Document:

        document = self.document_manager.new_document(
            name,
        )

        self.refresh_workspace()

        messagebox.showinfo(
            title="Document créé",
            message=f"Le document '{name}' a été créé.",
        )

        return document

    def refresh_workspace(self) -> None:

        project = self.project_manager.get_project()

        if project is None:
            return

        self.workspace.show_documents(
            project,
        )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return f"{self.__class__.__name__}()"