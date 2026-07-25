import customtkinter as ctk
from tkinter import simpledialog

from src.theme.colors import Colors
from src.theme.fonts import Fonts
from src.theme.spacing import Spacing
from src.widgets.document_card import DocumentCard


class DocumentView:

    def __init__(
        self,
        parent,
        project,
        application,
        on_open_document=None,
        on_refresh=None
    ):

        self.parent = parent
        self.project = project
        self.application = application
        self.on_open_document = on_open_document
        self.on_refresh = on_refresh

    def show(self):

        header = ctk.CTkFrame(
            self.parent,
            fg_color="transparent"
        )

        header.pack(
            fill="x",
            padx=Spacing.XL,
            pady=(Spacing.XL, Spacing.LG)
        )

        header.grid_columnconfigure(0, weight=1)

        title_frame = ctk.CTkFrame(
            header,
            fg_color="transparent"
        )

        title_frame.grid(
            row=0,
            column=0,
            sticky="w"
        )

        ctk.CTkLabel(
            title_frame,
            text="Projet",
            font=Fonts.TITLE,
            text_color=Colors.TEXT
        ).pack(anchor="w")

        ctk.CTkLabel(
            title_frame,
            text=f"{len(self.project.documents)} document(s)",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT
        ).pack(anchor="w")

        ctk.CTkButton(
            header,
            text="+ Nouveau document",
            width=180,
            command=self.new_document
        ).grid(
            row=0,
            column=1,
            sticky="e",
            padx=(20, 0)
        )

        content = ctk.CTkScrollableFrame(
            self.parent,
            fg_color="transparent"
        )

        content.pack(
            fill="both",
            expand=True,
            padx=Spacing.XL,
            pady=(0, Spacing.LG)
        )

        if not self.project.documents:

            ctk.CTkLabel(
                content,
                text="Aucun document."
            ).pack(anchor="w")

            return

        for document in self.project.documents:

            DocumentCard(
                content,
                document,
                on_open=self.open_document
            ).pack(
                fill="x",
                pady=(0, 15)
            )

    def new_document(self):

        nom = simpledialog.askstring(
            "Nouveau document",
            "Nom du document :"
        )

        if not nom:
            return

        self.application.controller.create_document(nom)

    def open_document(self, document):

        if self.on_open_document is not None:
            self.on_open_document(document)