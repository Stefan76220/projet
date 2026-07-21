from src.core.project_manager import ProjectManager
from src.gui.main_window import MainWindow


class Application:

    def __init__(self):

        self.project_manager = ProjectManager()

        self.window = MainWindow(
            self.project_manager
        )

    def run(self):

        self.window.run()