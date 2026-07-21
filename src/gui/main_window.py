import customtkinter as ctk

from src.gui.menu_bar import MenuBar
from src.gui.navigation import Navigation
from src.gui.workspace import Workspace


class MainWindow:

    def __init__(self, project_manager):

        self.project_manager = project_manager

        self.root = ctk.CTk()

        self.root.title("Générateur de livres")
        self.root.geometry("1400x900")

        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=0)
        self.root.grid_columnconfigure(1, weight=1)

        self.menu = MenuBar(
            self.root,
            self.project_manager
        )

        self.navigation = Navigation(self.root)

        self.workspace = Workspace(self.root)

    def run(self):

        self.root.mainloop()