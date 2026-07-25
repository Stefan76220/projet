import traceback

import customtkinter as ctk

from src.widgets.page_card import PageCard
from src.gui.views.page_editor_view import PageEditorView


class DocumentEditorView:

    def __init__(self, parent, application, on_back=None):

        self.parent = parent
        self.application = application
        self.on_back = on_back

        self.document = self.application.document_manager.get_document()

    # ---------------------------------------------------------

    def show(self):

        self.document = self.application.document_manager.get_document()

        for widget in self.parent.winfo_children():
            widget.destroy()

        root = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )

        root.pack(fill="both", expand=True)

        header = ctk.CTkFrame(
            root,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=20,
            pady=20
        )

        ctk.CTkButton(
            header,
            text="← Retour",
            width=120,
            command=self.back
        ).pack(side="left")

        titre = "Document"

        if self.document is not None:
            titre = self.document.name

        ctk.CTkLabel(
            header,
            text=titre,
            font=("Arial", 24, "bold")
        ).pack(side="left", padx=20)

        ctk.CTkButton(
            header,
            text="+ Nouvelle page",
            width=160,
            command=self.new_page
        ).pack(side="right")

        content = ctk.CTkScrollableFrame(
            root,
            fg_color="transparent"
        )

        content.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        if self.document is None:

            ctk.CTkLabel(
                content,
                text="Aucun document chargé."
            ).pack(anchor="w")

            return

        if len(self.document.pages) == 0:

            ctk.CTkLabel(
                content,
                text="Ce document ne contient encore aucune page."
            ).pack(anchor="w")

            return

        for page in self.document.pages:

            PageCard(
                content,
                page,
                on_open=self.open_page
            ).pack(
                fill="x",
                pady=(0, 10)
            )

    # ---------------------------------------------------------

    def new_page(self):

        try:

            self.application.document_manager.add_page()

            self.document = self.application.document_manager.get_document()

            self.show()

        except Exception:

            traceback.print_exc()

    # ---------------------------------------------------------

    def open_page(self, page_info):

        print("\n==============================")
        print("DocumentEditorView.open_page()")
        print("==============================")

        try:

            print("1 - page_info :", page_info)

            numero = page_info["numero"]

            print("2 - numéro :", numero)

            page = self.document.get_page(numero)

            print("3 - page :", page)

            if page is None:

                print("4 - get_page() retourne None")

                return

            print("5 - création de PageEditorView")

            editor = PageEditorView(
                self.parent,
                page,
                on_back=self.show
            )

            print("6 - objet créé")

            print("7 - appel de show()")

            editor.show()

            print("8 - retour de show()")

        except Exception:

            print("EXCEPTION :")

            traceback.print_exc()

    # ---------------------------------------------------------

    def back(self):

        if self.on_back is not None:
            self.on_back()