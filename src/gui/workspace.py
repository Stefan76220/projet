from __future__ import annotations

import customtkinter as ctk

from src.gui.views.dashboard_view import DashboardView
from src.gui.views.document_editor_view import DocumentEditorView
from src.gui.views.document_view import DocumentView
from src.gui.views.project_cleanup_dialog import ProjectCleanupDialog
from src.theme.colors import Colors
from src.theme.fonts import Fonts


class Workspace:
    """
    Zone de travail principale de l'application.

    Cette classe pilote les différentes vues affichées
    (accueil, liste des documents et éditeur).
    """

    def __init__(
        self,
        parent,
        application,
    ) -> None:

        self.application = application
        self.current_project = None
        self._documents_transitioning = False
        self._cleanup_dialog = None

        self.frame = ctk.CTkFrame(
            parent,
            fg_color=Colors.WINDOW,
            corner_radius=0,
        )

        self.frame.grid(
            row=0,
            column=1,
            sticky="nsew",
        )

        self.show_dashboard()

    # ==========================================================
    # Gestion des vues
    # ==========================================================

    def clear(self) -> None:

        for widget in self.frame.winfo_children():
            widget.destroy()

    def show_dashboard(self) -> None:

        self._close_cleanup_dialog()
        self._set_navigation_visible(False)
        self.clear()

        DashboardView(
            self.frame,
        ).show()

    def show_documents(
        self,
        project,
    ) -> None:

        if self._documents_transitioning:
            return

        self._documents_transitioning = True
        self.current_project = project
        self._close_cleanup_dialog()

        # La vue est construite hors écran puis affichée une seule fois.
        # Cela évite le double rafraîchissement visible à l'ouverture
        # du Centre du projet.
        self.frame.grid_remove()

        try:
            self._set_navigation_visible(True)
            self.clear()

            centre = ctk.CTkFrame(
                self.frame,
                fg_color=Colors.WINDOW,
                corner_radius=0,
            )
            centre.pack(fill="both", expand=True)

            tools_bar = ctk.CTkFrame(
                centre,
                height=48,
                fg_color=Colors.WINDOW,
                corner_radius=0,
            )
            tools_bar.pack(
                fill="x",
                padx=22,
                pady=(10, 0),
            )
            tools_bar.pack_propagate(False)

            ctk.CTkLabel(
                tools_bar,
                text="Outils du projet",
                font=Fonts.NORMAL,
                text_color=Colors.TEXT_LIGHT,
            ).pack(side="left", padx=(2, 12))

            ctk.CTkButton(
                tools_bar,
                text="Nettoyage de la base",
                width=190,
                height=36,
                corner_radius=10,
                fg_color="#17365D",
                hover_color="#244B79",
                text_color="#FFFFFF",
                font=Fonts.NORMAL,
                command=self._open_project_cleanup,
            ).pack(side="right")

            content = ctk.CTkFrame(
                centre,
                fg_color=Colors.WINDOW,
                corner_radius=0,
            )
            content.pack(fill="both", expand=True)

            DocumentView(
                content,
                project,
                self.application,
                on_open_document=self.show_document,
                on_refresh=self.back_to_documents,
            ).show()

            self.frame.update_idletasks()

        finally:
            self.frame.grid(
                row=0,
                column=1,
                sticky="nsew",
            )
            self.frame.after_idle(
                self._finish_documents_transition
            )

    def _finish_documents_transition(self) -> None:

        self._documents_transitioning = False

    def show_document(
        self,
        document_info,
    ) -> None:

        self._close_cleanup_dialog()
        self._set_navigation_visible(True)
        self.clear()

        self.application.document_manager.load_document(
            document_info["nom"],
        )

        DocumentEditorView(
            self.frame,
            self.application,
            on_back=self.back_to_documents,
        ).show()

    def back_to_documents(self) -> None:

        if self.current_project is not None:
            self.show_documents(self.current_project)

    # ==========================================================
    # Nettoyage du projet
    # ==========================================================

    def _open_project_cleanup(self) -> None:

        if self.current_project is None:
            return

        if (
            self._cleanup_dialog is not None
            and self._cleanup_dialog.winfo_exists()
        ):
            self._cleanup_dialog.lift()
            self._cleanup_dialog.focus_force()
            return

        self._cleanup_dialog = ProjectCleanupDialog(
            self.frame,
            self.current_project,
            on_close=self._on_cleanup_dialog_closed,
        )

    def _on_cleanup_dialog_closed(self) -> None:

        self._cleanup_dialog = None

    def _close_cleanup_dialog(self) -> None:

        dialog = self._cleanup_dialog

        if dialog is None:
            return

        try:
            if dialog.winfo_exists():
                dialog.close()
        except Exception:
            pass

        self._cleanup_dialog = None

    # ==========================================================
    # Navigation latérale
    # ==========================================================

    def _set_navigation_visible(
        self,
        visible: bool,
    ) -> None:
        """
        Masque la navigation sur l'accueil et la réaffiche dès
        qu'un projet ou un document est présenté.

        La barre de navigation occupe la colonne 0 de la fenêtre
        principale. ``grid_remove`` conserve sa configuration afin
        qu'elle puisse être restaurée sans recréation.
        """

        parent = self.frame.master

        if parent is None:
            return

        try:
            navigation_widgets = parent.grid_slaves(
                row=0,
                column=0,
            )
        except Exception:
            return

        for widget in navigation_widgets:
            if visible:
                widget.grid()
            else:
                widget.grid_remove()

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"Workspace("
            f"current_project={self.current_project!r})"
        )