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
    (accueil, liste des documents, nettoyage et éditeur).
    """

    def __init__(
        self,
        parent,
        application,
    ) -> None:

        self.application = application
        self.current_project = None
        self._documents_transitioning = False
        self._cleanup_transitioning = False
        self._cleanup_view = None

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

        self._cleanup_view = None

    def show_dashboard(self) -> None:

        self._destroy_cleanup_view()
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
        self._destroy_cleanup_view()

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
                command=self.show_project_cleanup,
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

        self._destroy_cleanup_view()
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

    def show_project_cleanup(self) -> None:

        if (
            self.current_project is None
            or self._cleanup_transitioning
        ):
            return

        self._cleanup_transitioning = True

        # Construction hors écran : la page apparaît une seule fois,
        # déjà analysée et complètement mise en page.
        self.frame.grid_remove()

        try:
            self._set_navigation_visible(True)
            self.clear()

            self._cleanup_view = ProjectCleanupDialog(
                self.frame,
                self.current_project,
                on_close=self.back_to_documents,
            )

            self.frame.update_idletasks()

        finally:
            self.frame.grid(
                row=0,
                column=1,
                sticky="nsew",
            )
            self.frame.after_idle(
                self._finish_cleanup_transition
            )

    def _finish_cleanup_transition(self) -> None:

        self._cleanup_transitioning = False

    def _open_project_cleanup(self) -> None:
        """
        Compatibilité avec les appels plus anciens.

        Le nettoyage est maintenant une page intégrée à l'espace
        de travail et non une fenêtre indépendante.
        """

        self.show_project_cleanup()

    def _destroy_cleanup_view(self) -> None:

        view = self._cleanup_view

        if view is None:
            return

        try:
            view.on_close = None

            if view.winfo_exists():
                view.destroy()
        except Exception:
            pass

        self._cleanup_view = None

    def _close_cleanup_dialog(self) -> None:
        """
        Compatibilité avec l'ancien nom de méthode.
        """

        self._destroy_cleanup_view()

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