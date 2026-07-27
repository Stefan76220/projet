from __future__ import annotations

import traceback

import customtkinter as ctk

from src.gui.views.page_editor_view import PageEditorView
from src.widgets.page_card import PageCard


class DocumentEditorView:
    """
    Vue d'édition d'un document.
    """

    def __init__(
        self,
        parent,
        application,
        on_back=None,
    ) -> None:

        self.parent = parent
        self.application = application
        self.on_back = on_back

        self.document = self.application.document_manager.get_document()

    # ==========================================================
    # Affichage
    # ==========================================================

    def show(self) -> None:

        self.document = self.application.document_manager.get_document()

        self._clear_parent()

        root = ctk.CTkFrame(
            self.parent,
            fg_color="transparent",
        )
        root.pack(
            fill="both",
            expand=True,
        )

        header = self._create_header(root)
        header.pack(
            fill="x",
            padx=20,
            pady=20,
        )

        content = ctk.CTkScrollableFrame(
            root,
            fg_color="transparent",
        )
        content.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20),
        )

        if self.document is None:

            ctk.CTkLabel(
                content,
                text="Aucun document chargé.",
            ).pack(anchor="w")

            return

        if not self.document.pages:

            ctk.CTkLabel(
                content,
                text="Ce document ne contient encore aucune page.",
            ).pack(anchor="w")

            return

        for page in self.document.pages:

            PageCard(
                content,
                page,
                on_open=self.open_page,
            ).pack(
                fill="x",
                pady=(0, 10),
            )

    # ==========================================================
    # Construction
    # ==========================================================

    def _create_header(
        self,
        parent,
    ) -> ctk.CTkFrame:

        header = ctk.CTkFrame(
            parent,
            fg_color="transparent",
        )

        ctk.CTkButton(
            header,
            text="← Retour",
            width=120,
            command=self.back,
        ).pack(side="left")

        title = (
            self.document.name
            if self.document is not None
            else "Document"
        )

        ctk.CTkLabel(
            header,
            text=title,
            font=("Arial", 24, "bold"),
        ).pack(
            side="left",
            padx=20,
        )

        ctk.CTkButton(
            header,
            text="+ Nouvelle page",
            width=160,
            command=self.new_page,
        ).pack(side="right")

        return header

    def _clear_parent(self) -> None:

        for widget in self.parent.winfo_children():
            widget.destroy()

    # ==========================================================
    # Actions
    # ==========================================================

    def new_page(self) -> None:

        try:

            self.application.document_manager.add_page()

            self.document = (
                self.application.document_manager.get_document()
            )

            self.show()

        except Exception:

            traceback.print_exc()

    def open_page(
        self,
        page_info,
    ) -> None:

        try:

            page = self.document.get_page(
                page_info["numero"],
            )

            if page is None:
                return

            PageEditorView(
                self.parent,
                page,
                on_back=self.show,
            ).show()

        except Exception:

            traceback.print_exc()

    def back(self) -> None:

        if self.on_back is not None:
            self.on_back()

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        count = 0 if self.document is None else len(self.document.pages)

        return (
            f"DocumentEditorView("
            f"pages={count})"
        )