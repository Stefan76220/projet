from __future__ import annotations

import traceback

import customtkinter as ctk

from src.gui.views.page_editor_view import PageEditorView
from src.theme.colors import Colors
from src.theme.fonts import Fonts
from src.widgets.page_card import PageCard


class RenamePageDialog(ctk.CTkToplevel):
    """
    Fenêtre permettant de renommer une page.
    """

    def __init__(
        self,
        parent,
        current_name: str,
        on_validate,
    ) -> None:

        super().__init__(parent)

        self.on_validate = on_validate

        self.title("Renommer la page")
        self.geometry("440x210")
        self.resizable(False, False)

        self.transient(parent.winfo_toplevel())
        self.grab_set()

        self.configure(
            fg_color=Colors.WINDOW,
        )

        self.protocol(
            "WM_DELETE_WINDOW",
            self.cancel,
        )

        self._create_content(
            current_name,
        )

        self.after(
            50,
            self._prepare_entry,
        )

    # ==========================================================
    # Construction
    # ==========================================================

    def _create_content(
        self,
        current_name: str,
    ) -> None:

        container = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        container.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=22,
        )

        ctk.CTkLabel(
            container,
            text="Renommer la page",
            font=Fonts.H2,
            text_color=Colors.TEXT,
            anchor="w",
        ).pack(
            fill="x",
            pady=(0, 8),
        )

        ctk.CTkLabel(
            container,
            text="Saisis le nouveau nom de la page.",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
        ).pack(
            fill="x",
            pady=(0, 14),
        )

        self.name_entry = ctk.CTkEntry(
            container,
            height=38,
            font=Fonts.NORMAL,
            border_color=Colors.BORDER,
        )

        self.name_entry.pack(
            fill="x",
        )

        self.name_entry.insert(
            0,
            current_name,
        )

        self.name_entry.bind(
            "<Return>",
            self.validate,
        )

        self.name_entry.bind(
            "<Escape>",
            self.cancel,
        )

        buttons = ctk.CTkFrame(
            container,
            fg_color="transparent",
        )

        buttons.pack(
            fill="x",
            pady=(18, 0),
        )

        ctk.CTkButton(
            buttons,
            text="Annuler",
            width=110,
            fg_color=Colors.BUTTON,
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            command=self.cancel,
        ).pack(
            side="right",
            padx=(8, 0),
        )

        ctk.CTkButton(
            buttons,
            text="Valider",
            width=110,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            command=self.validate,
        ).pack(
            side="right",
        )

    # ==========================================================
    # Actions
    # ==========================================================

    def _prepare_entry(self) -> None:

        self.name_entry.focus_set()

        self.name_entry.select_range(
            0,
            "end",
        )

    def validate(
        self,
        event=None,
    ) -> None:

        new_name = self.name_entry.get().strip()

        if not new_name:
            self.name_entry.focus_set()
            return

        try:
            self.on_validate(
                new_name,
            )

        finally:
            self.destroy()

    def cancel(
        self,
        event=None,
    ) -> None:

        self.destroy()


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

        self.document = (
            self.application.document_manager.get_document()
        )

        self.rename_dialog: RenamePageDialog | None = None

    # ==========================================================
    # Affichage
    # ==========================================================

    def show(self) -> None:

        self.document = (
            self.application.document_manager.get_document()
        )

        self._clear_parent()

        root = ctk.CTkFrame(
            self.parent,
            fg_color="transparent",
        )

        root.pack(
            fill="both",
            expand=True,
        )

        header = self._create_header(
            root,
        )

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
            ).pack(
                anchor="w",
            )

            return

        if not self.document.pages:

            ctk.CTkLabel(
                content,
                text="Ce document ne contient encore aucune page.",
            ).pack(
                anchor="w",
            )

            return

        for page in self.document.pages:

            PageCard(
                content,
                page,
                on_open=self.open_page,
                on_rename=self.rename_page,
                on_duplicate=self.duplicate_page,
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
        ).pack(
            side="left",
        )

        title = (
            self.document.name
            if self.document is not None
            else "Document"
        )

        ctk.CTkLabel(
            header,
            text=title,
            font=Fonts.H1,
            text_color=Colors.TEXT,
        ).pack(
            side="left",
            padx=20,
        )

        ctk.CTkButton(
            header,
            text="+ Nouvelle page",
            width=160,
            fg_color=Colors.PRIMARY,
            hover_color=Colors.PRIMARY_HOVER,
            command=self.new_page,
        ).pack(
            side="right",
        )

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

    def rename_page(
        self,
        page_info: dict,
    ) -> None:

        if self.document is None:
            return

        try:
            page = self.document.get_page(
                page_info["numero"],
            )

            if page is None:
                return

            if page.locked:
                return

            current_name = page.display_title

            self.rename_dialog = RenamePageDialog(
                parent=self.parent,
                current_name=current_name,
                on_validate=lambda new_name: self._apply_page_name(
                    page,
                    new_name,
                ),
            )

        except Exception:
            traceback.print_exc()

    def duplicate_page(
        self,
        page_info: dict,
    ) -> None:

        if self.document is None:
            return

        try:
            duplicated_page = self.document.duplicate_page(
                page_info["numero"],
            )

            if duplicated_page is None:
                return

            self.document = (
                self.application.document_manager.get_document()
            )

            self.show()

        except Exception:
            traceback.print_exc()

    def _apply_page_name(
        self,
        page,
        new_name: str,
    ) -> None:

        try:
            page.rename(
                new_name,
            )

            self.document.update_page_summary(
                page,
            )

            self.show()

        except Exception:
            traceback.print_exc()

    def back(self) -> None:

        if self.on_back is not None:
            self.on_back()

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        count = (
            0
            if self.document is None
            else len(self.document.pages)
        )

        return (
            f"DocumentEditorView("
            f"pages={count})"
        )