from tkinter import messagebox


class ApplicationController:

    def __init__(self, application):

        self.application = application

    # -------------------------------------------------
    # Documents
    # -------------------------------------------------

    def create_document(self, name):

        document = self.application.document_manager.new_document(name)

        self.application.window.workspace.show_documents(
            self.application.project_manager.get_project()
        )

        messagebox.showinfo(
            "Document créé",
            f"Le document '{name}' a été créé."
        )

        return document