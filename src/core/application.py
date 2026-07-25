from src.core.project_manager import ProjectManager
from src.core.document_manager import DocumentManager
from src.core.application_controller import ApplicationController

from src.gui.layout.main_window import MainWindow

from src.library.book_models.book_model_library import BookModelLibrary
from src.library.page_types.page_type_library import PageTypeLibrary


class Application:

    def __init__(self):

        # Bibliothèques globales
        self.book_models = BookModelLibrary()
        self.book_models.load()

        self.page_types = PageTypeLibrary()
        self.page_types.load()

        # Gestionnaires
        self.project_manager = ProjectManager()
        self.document_manager = DocumentManager(self.project_manager)

        # Contrôleur central
        self.controller = ApplicationController(self)

        # Interface
        self.window = MainWindow(self)

    def run(self):

        self.window.run()