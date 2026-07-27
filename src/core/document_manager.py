from __future__ import annotations

from pathlib import Path

from src.core.document import Document


class DocumentManager:
    """
    Gestionnaire des documents du projet courant.
    """

    def __init__(
        self,
        project_manager,
    ) -> None:

        self.project_manager = project_manager
        self.current_document: Document | None = None

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def has_document(self) -> bool:

        return self.current_document is not None

    # ==========================================================
    # Documents
    # ==========================================================

    def new_document(
        self,
        name: str,
    ) -> Document:

        project = self._require_project()

        documents_folder = Path(project.root) / "documents"

        document = Document()
        document.create(
            documents_folder,
            name,
        )

        project.add_document(
            document.name,
        )

        self.current_document = document

        return document

    def load_document(
        self,
        document_name: str,
    ) -> Document:

        project = self._require_project()

        documents_folder = Path(project.root) / "documents"

        document = Document()
        document.load(
            documents_folder / document_name,
        )

        self.current_document = document

        return document

    def save_document(self) -> None:

        if not self.has_document:
            return

        self.current_document.save()

    def close_document(self) -> None:

        self.current_document = None

    def get_document(self) -> Document | None:

        return self.current_document

    # ==========================================================
    # Pages
    # ==========================================================

    def add_page(
        self,
        page_type=None,
    ):

        return self._require_document().add_page(
            page_type,
        )

    # ==========================================================
    # Vérifications
    # ==========================================================

    def _require_project(self):

        project = self.project_manager.get_project()

        if project is None:
            raise RuntimeError(
                "Aucun projet ouvert."
            )

        return project

    def _require_document(self) -> Document:

        if self.current_document is None:
            raise RuntimeError(
                "Aucun document ouvert."
            )

        return self.current_document

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"current_document={self.current_document!r})"
        )