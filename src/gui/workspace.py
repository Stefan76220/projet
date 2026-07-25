import customtkinter as ctk

from src.theme.colors import Colors
from src.gui.views.dashboard_view import DashboardView
from src.gui.views.document_view import DocumentView
from src.gui.views.document_editor_view import DocumentEditorView


class Workspace:

    def __init__(self, parent, application):

        self.application = application

        self.frame = ctk.CTkFrame(
            parent,
            fg_color=Colors.WINDOW,
            corner_radius=0
        )

        self.frame.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.current_project = None

        self.show_dashboard()

    def clear(self):

        for widget in self.frame.winfo_children():
            widget.destroy()

    def show_dashboard(self):

        self.clear()

        DashboardView(
            self.frame
        ).show()

    def show_documents(self, project):

        self.current_project = project

        self.clear()

        DocumentView(
            self.frame,
            project,
            self.application,
            on_open_document=self.show_document,
            on_refresh=self.back_to_documents
        ).show()

    def show_document(self, document_info):

        self.clear()

        self.application.document_manager.load_document(
            document_info["nom"]
        )

        DocumentEditorView(
            self.frame,
            self.application,
            on_back=self.back_to_documents
        ).show()

    def back_to_documents(self):

        if self.current_project is not None:
            self.show_documents(self.current_project)