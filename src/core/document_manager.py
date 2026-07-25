from pathlib import Path

from src.core.document import Document


class DocumentManager:

    def __init__(self, project_manager):

        self.project_manager = project_manager
        self.current_document = None

    def new_document(self, name: str):

        project = self.project_manager.get_project()

        if project is None:
            raise RuntimeError("Aucun projet ouvert.")

        documents_folder = Path(project.root) / "documents"

        document = Document()

        document.create(
            documents_folder,
            name
        )

        # Enregistrement dans le projet
        project.add_document(
            document.name
        )

        # Le document devient le document courant
        self.current_document = document

        return document

    def load_document(self, document_name: str):

        project = self.project_manager.get_project()

        if project is None:
            raise RuntimeError("Aucun projet ouvert.")

        documents_folder = Path(project.root) / "documents"

        document = Document()

        document.load(
            documents_folder / document_name
        )

        self.current_document = document

        return document

    def close_document(self):

        self.current_document = None

    def get_document(self):

        return self.current_document

    def add_page(self, page_type=None):

        if self.current_document is None:
            raise RuntimeError("Aucun document ouvert.")

        return self.current_document.add_page(page_type)

    def save_document(self):

        if self.current_document is not None:
            self.current_document.save()