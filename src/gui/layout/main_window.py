from __future__ import annotations

import os
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

        # Taille de secours uniquement.
        self.root.geometry("1400x900")

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
    # Maximisation Windows
    # ==========================================================

    def _maximize_window(self) -> None:
        """
        Maximisation robuste sous Windows.

        L'appel est fait après le démarrage de la boucle graphique,
        quand Windows a réellement créé la fenêtre.
        """
        try:
            self.root.update_idletasks()
        except Exception:
            pass

        # Méthode Tk standard.
        try:
            self.root.state("zoomed")
        except Exception:
            pass

        # Renfort Windows natif si Tk/CustomTkinter remet la fenêtre
        # dans sa géométrie initiale.
        if os.name == "nt":
            try:
                import ctypes

                hwnd = int(self.root.winfo_id())
                SW_MAXIMIZE = 3
                ctypes.windll.user32.ShowWindow(hwnd, SW_MAXIMIZE)
            except Exception:
                pass

    # ==========================================================
    # Exécution
    # ==========================================================

    def run(self) -> None:

        # La maximisation est volontairement demandée après création réelle
        # de la fenêtre, puis confirmée une seconde fois pour contrer un
        # éventuel recalcul initial de CustomTkinter.
        self.root.after(10, self._maximize_window)
        self.root.after(250, self._maximize_window)

        self.root.mainloop()

    def close(self) -> None:

        self.shortcut_manager.close()
        self.root.destroy()

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return "MainWindow()"
