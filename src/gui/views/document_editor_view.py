from __future__ import annotations

import traceback
from tkinter import colorchooser

import customtkinter as ctk

from src.gui.views.page_editor_view import PageEditorView
from src.library.page_types.page_type_library import PageTypeLibrary
from src.theme.colors import Colors
from src.theme.fonts import Fonts
from src.widgets.page_card import PageCard


PAGE_TYPE_APPEARANCES = {
    "Page vide": {
        "icone": "📄",
        "couleur": "#D9D4C7",
    },
    "Page de texte": {
        "icone": "📝",
        "couleur": "#B8C8D8",
    },
    "Page image": {
        "icone": "🖼️",
        "couleur": "#C8B8D8",
    },
    "Page de chapitre": {
        "icone": "📖",
        "couleur": "#D8C3A5",
    },
}


class RenamePageDialog(ctk.CTkToplevel):
    """Fenêtre permettant de renommer une page."""

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
        self.configure(fg_color=Colors.WINDOW)
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self._create_content(current_name)
        self.after(50, self._prepare_entry)

    def _create_content(self, current_name: str) -> None:
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
        self.name_entry.pack(fill="x")
        self.name_entry.insert(0, current_name)
        self.name_entry.bind("<Return>", self.validate)
        self.name_entry.bind("<Escape>", self.cancel)

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
        ).pack(side="right")

    def _prepare_entry(self) -> None:
        self.name_entry.focus_set()
        self.name_entry.select_range(0, "end")

    def validate(self, event=None) -> None:
        new_name = self.name_entry.get().strip()

        if not new_name:
            self.name_entry.focus_set()
            return

        try:
            self.on_validate(new_name)
        finally:
            self.destroy()

    def cancel(self, event=None) -> None:
        self.destroy()


class ChangePageTypeDialog(ctk.CTkToplevel):
    """Fenêtre permettant de choisir le type d'une page."""

    def __init__(
        self,
        parent,
        current_type: str,
        page_types: list,
        on_validate,
    ) -> None:
        super().__init__(parent)

        self.on_validate = on_validate
        self.page_types = page_types
        self.type_names = [
            page_type.name
            for page_type in page_types
        ]

        if "Page vide" not in self.type_names:
            self.type_names.insert(0, "Page vide")

        selected_type = (
            current_type
            if current_type in self.type_names
            else self.type_names[0]
        )

        self.selected_type = ctk.StringVar(
            value=selected_type,
        )

        self.title("Changer le type de page")
        self.geometry("500x330")
        self.resizable(False, False)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self.configure(fg_color=Colors.WINDOW)
        self.protocol("WM_DELETE_WINDOW", self.cancel)

        self._create_content()
        self.after(50, self._center_window)

    def _create_content(self) -> None:
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
            text="Changer le type de page",
            font=Fonts.H2,
            text_color=Colors.TEXT,
            anchor="w",
        ).pack(
            fill="x",
            pady=(0, 8),
        )

        ctk.CTkLabel(
            container,
            text="Choisis la fonction éditoriale de cette page.",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
        ).pack(
            fill="x",
            pady=(0, 16),
        )

        ctk.CTkOptionMenu(
            container,
            values=self.type_names,
            variable=self.selected_type,
            height=40,
            font=Fonts.NORMAL,
            dropdown_font=Fonts.NORMAL,
            fg_color=Colors.BUTTON,
            button_color=Colors.PRIMARY,
            button_hover_color=Colors.PRIMARY_HOVER,
            text_color=Colors.TEXT,
            command=self._update_description,
        ).pack(fill="x")

        self.description_label = ctk.CTkLabel(
            container,
            text="",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
            anchor="w",
            justify="left",
            wraplength=410,
            fg_color=Colors.CARD,
            corner_radius=10,
        )
        self.description_label.pack(
            fill="x",
            pady=(16, 0),
            ipady=14,
            padx=1,
        )

        self._update_description(
            self.selected_type.get(),
        )

        buttons = ctk.CTkFrame(
            container,
            fg_color="transparent",
        )
        buttons.pack(
            fill="x",
            side="bottom",
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
        ).pack(side="right")

    def _update_description(self, selected_name: str) -> None:
        if selected_name == "Page vide":
            description = "Page libre sans structure éditoriale imposée."
        else:
            description = "Aucune description disponible."

            for page_type in self.page_types:
                if page_type.name == selected_name:
                    description = page_type.description or description
                    break

        appearance = PAGE_TYPE_APPEARANCES.get(
            selected_name,
            PAGE_TYPE_APPEARANCES["Page vide"],
        )

        self.description_label.configure(
            text=f"{appearance['icone']}  {description}",
        )

    def validate(self) -> None:
        selected_name = self.selected_type.get().strip()

        if not selected_name:
            return

        try:
            self.on_validate(selected_name)
        finally:
            self.destroy()

    def cancel(self) -> None:
        self.destroy()

    def _center_window(self) -> None:
        self.update_idletasks()

        parent = self.master.winfo_toplevel()

        x = parent.winfo_x() + max(
            0,
            (parent.winfo_width() - self.winfo_width()) // 2,
        )
        y = parent.winfo_y() + max(
            0,
            (parent.winfo_height() - self.winfo_height()) // 2,
        )

        self.geometry(f"+{x}+{y}")


class DocumentEditorView:
    """Vue d'édition d'un document."""

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
        self.change_type_dialog: ChangePageTypeDialog | None = None

        # CIBLAGE_PAGE_CONCEPTION_V1
        self._active_page_number: int | None = None

        self.page_type_library = PageTypeLibrary()
        self.page_type_library.load()

    def show(self) -> None:
        self.document = (
            self.application.document_manager.get_document()
        )
        self._active_page_number = None

        self._clear_parent()

        root = ctk.CTkFrame(
            self.parent,
            fg_color="transparent",
        )
        root.pack(
            fill="both",
            expand=True,
        )

        self._create_header(root).pack(
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
                on_rename=self.rename_page,
                on_duplicate=self.duplicate_page,
                on_change_type=self.change_page_type,
                on_change_color=self.change_page_color,
            ).pack(
                fill="x",
                pady=(0, 10),
            )

    def _create_header(self, parent) -> ctk.CTkFrame:
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
        ).pack(side="right")

        return header

    def _clear_parent(self) -> None:
        for widget in self.parent.winfo_children():
            widget.destroy()

    def new_page(self) -> None:
        try:
            self.application.document_manager.add_page()
            self.document = (
                self.application.document_manager.get_document()
            )
            self.show()
        except Exception:
            traceback.print_exc()

    @property
    def active_page_number(self) -> int | None:
        """Numéro de la page actuellement ouverte dans Conception."""
        return self._active_page_number

    def focus_page(self, page_number: int) -> bool:
        """Ouvre directement une page précise dans le Bureau Conception."""
        self.document = (
            self.application.document_manager.get_document()
        )
        if self.document is None:
            return False

        try:
            number = int(page_number)
        except (TypeError, ValueError):
            return False

        try:
            page = self.document.get_page(number)
        except Exception:
            traceback.print_exc()
            return False

        if page is None:
            return False

        self._active_page_number = number

        try:
            PageEditorView(
                self.parent,
                page,
                on_back=self.show,
            ).show()
        except Exception:
            self._active_page_number = None
            traceback.print_exc()
            return False

        return True

    def open_page(self, page_info) -> None:
        try:
            self.focus_page(page_info["numero"])
        except (KeyError, TypeError):
            return

    def rename_page(self, page_info: dict) -> None:
        page = self._get_editable_page(page_info)

        if page is None:
            return

        try:
            self.rename_dialog = RenamePageDialog(
                parent=self.parent,
                current_name=page.display_title,
                on_validate=lambda new_name: self._apply_page_name(
                    page,
                    new_name,
                ),
            )
        except Exception:
            traceback.print_exc()

    def duplicate_page(self, page_info: dict) -> None:
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

    def change_page_type(self, page_info: dict) -> None:
        page = self._get_editable_page(page_info)

        if page is None:
            return

        try:
            self.page_type_library.load()

            self.change_type_dialog = ChangePageTypeDialog(
                parent=self.parent,
                current_type=page.page_type,
                page_types=self.page_type_library.all(),
                on_validate=lambda page_type: self._apply_page_type(
                    page,
                    page_type,
                ),
            )
        except Exception:
            traceback.print_exc()

    def change_page_color(self, page_info: dict) -> None:
        page = self._get_editable_page(page_info)

        if page is None:
            return

        current_color = getattr(
            page,
            "color",
            "#D9D4C7",
        )

        try:
            selected = colorchooser.askcolor(
                color=current_color,
                title="Choisir la couleur éditoriale",
                parent=self.parent.winfo_toplevel(),
            )

            selected_color = selected[1]

            if not selected_color:
                return

            self._apply_page_color(
                page,
                selected_color.upper(),
            )

        except Exception:
            traceback.print_exc()

    def _get_editable_page(self, page_info: dict):
        if self.document is None:
            return None

        try:
            page = self.document.get_page(
                page_info["numero"],
            )
        except (KeyError, TypeError, ValueError):
            return None

        if page is None or page.locked:
            return None

        return page

    def _apply_page_name(
        self,
        page,
        new_name: str,
    ) -> None:
        try:
            page.rename(new_name)
            self.document.update_page_summary(page)
            self.show()
        except Exception:
            traceback.print_exc()

    def _apply_page_type(
        self,
        page,
        page_type: str,
    ) -> None:
        try:
            appearance = PAGE_TYPE_APPEARANCES.get(
                page_type,
                PAGE_TYPE_APPEARANCES["Page vide"],
            )

            page.set_type(page_type)
            page.icon = appearance["icone"]
            page.color = appearance["couleur"]
            page.save(update_history=False)

            self.document.update_page_summary(page)
            self.show()

        except Exception:
            traceback.print_exc()

    def _apply_page_color(
        self,
        page,
        color: str,
    ) -> None:
        try:
            page.color = color
            page.save(update_history=False)

            self.document.update_page_summary(page)
            self.show()

        except Exception:
            traceback.print_exc()

    def back(self) -> None:
        if self.on_back is not None:
            self.on_back()

    def __repr__(self) -> str:
        count = (
            0
            if self.document is None
            else len(self.document.pages)
        )

        return f"DocumentEditorView(pages={count})"