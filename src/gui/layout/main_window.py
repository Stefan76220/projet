from __future__ import annotations

import customtkinter as ctk

from src.gui.menu_bar import MenuBar
from src.gui.navigation import Navigation
from src.gui.workspace import Workspace


class MainWindow:
    """
    Fenêtre principale de l'application.
    """

    def __init__(self, application) -> None:

        self.application = application

        self.root = ctk.CTk()

        self._configure_window()
        self._configure_grid()
        self._create_widgets()

    # ==========================================================
    # Construction
    # ==========================================================

    def _configure_window(self) -> None:

        self.root.title("Générateur de livres")
        self.root.geometry("1400x900")

    def _configure_grid(self) -> None:

        self.root.grid_rowconfigure(
            0,
            weight=1,
        )

        self.root.grid_columnconfigure(
            0,
            weight=0,
        )

        self.root.grid_columnconfigure(
            1,
            weight=1,
        )

    def _create_widgets(self) -> None:

        self.navigation = Navigation(
            self.root,
        )

        self.workspace = Workspace(
            self.root,
            self.application,
        )

        self.menu = MenuBar(
            self.root,
            self.application.project_manager,
            self.workspace,
        )

    # ==========================================================
    # Exécution
    # ==========================================================

    def run(self) -> None:

        self.root.mainloop()

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return "MainWindow()"