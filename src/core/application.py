from __future__ import annotations

from src.core.application_controller import ApplicationController
from src.core.document_manager import DocumentManager
from src.core.project_manager import ProjectManager

from src.gui.layout.main_window import MainWindow

from src.library.book_models.book_model_library import BookModelLibrary
from src.library.page_types.page_type_library import PageTypeLibrary


class Application:
    """
    Application principale.
    Responsable de l'initialisation de tous les services.
    """

    def __init__(self) -> None:

        self.book_models = BookModelLibrary()
        self.page_types = PageTypeLibrary()

        self.project_manager = ProjectManager()

        self.document_manager = DocumentManager(
            self.project_manager,
        )

        self.controller = ApplicationController(
            self,
        )

        self.window = MainWindow(
            self,
        )

        self._initialize()

    # ==========================================================
    # Initialisation
    # ==========================================================

    def _initialize(self) -> None:

        self._load_libraries()

    def _load_libraries(self) -> None:

        self.book_models.load()
        self.page_types.load()

    # ==========================================================
    # Accesseurs
    # ==========================================================

    @property
    def main_window(self) -> MainWindow:

        return self.window

    # ==========================================================
    # Exécution
    # ==========================================================

    def run(self) -> None:

        self.window.run()

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return f"{self.__class__.__name__}()"