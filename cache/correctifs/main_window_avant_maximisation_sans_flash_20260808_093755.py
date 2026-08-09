from __future__ import annotations

import customtkinter as ctk

from src.gui.menu_bar import MenuBar
from src.gui.navigation import Navigation
from src.gui.shortcut_manager import GlobalShortcutManager
from src.gui.workspace import Workspace


class MainWindow:
    """
    Fenêtre principale de l'application.
    """

    def __init__(self, application) -> None:

        self.application = application

        self.root = ctk.CTk()
        self.shortcut_manager = GlobalShortcutManager(
            self.root,
        )

        self._configure_window()
        self._configure_grid()
        self._create_widgets()

    # ==========================================================
    # Construction
    # ==========================================================

    def _configure_window(self) -> None:

        self.root.title("Générateur de livres")
        self.root.geometry("1400x900")
        # OUVERTURE_FENETRE_MAXIMISEE_V1
        # Ouvre PageMaître maximisé tout en gardant la barre Windows.
        try:
            self.root.state("zoomed")
        except Exception:
            pass
        self.root.protocol(
            "WM_DELETE_WINDOW",
            self.close,
        )

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

    def close(self) -> None:

        self.shortcut_manager.close()
        self.root.destroy()

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return "MainWindow()"