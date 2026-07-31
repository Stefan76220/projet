from __future__ import annotations

from dataclasses import replace
import tkinter as tk
from tkinter import colorchooser

import customtkinter as ctk

from src.engine.foundation import Point, Rect, Size
from src.engine.page_format import A4, A5, BOOK_16X24, BOOK_17X24
from src.gui.editor_canvas import CanvasObject, EditorCanvas
from src.gui.rulers.horizontal_ruler import HorizontalRuler
from src.gui.rulers.vertical_ruler import VerticalRuler
from src.gui.status_bar import StatusBar
from src.theme.colors import Colors
from src.theme.fonts import Fonts


PAGE_FORMATS = {
    "A4": A4,
    "A5": A5,
    "16x24": BOOK_16X24,
    "16 × 24": BOOK_16X24,
    "17x24": BOOK_17X24,
    "17 × 24": BOOK_17X24,
}


class PageEditorView:
    """
    Vue d'édition d'une page.
    """

    RULER_SIZE = 30
    MIN_READY_SIZE = 100
    DISPLAY_RETRY_DELAY_MS = 50
    MAX_DISPLAY_RETRIES = 20

    def __init__(
        self,
        parent,
        page,
        on_back=None,
    ) -> None:

        self.parent = parent
        self.page = page
        self.on_back = on_back

        self.root = None
        self.workspace: EditorCanvas | None = None
        self.status_bar: StatusBar | None = None
        self._display_retry_count = 0
        self._save_status_text = tk.StringVar(
            value="",
        )
        self._selection_x_text = tk.StringVar(
            value="X : — mm",
        )
        self._selection_y_text = tk.StringVar(
            value="Y : — mm",
        )
        self._copied_properties: dict[str, object] | None = None

    def show(self) -> None:

        self._clear_parent()

        self.root = ctk.CTkFrame(
            self.parent,
            fg_color="#909090",
        )
        self.root.pack(
            fill="both",
            expand=True,
        )

        self._create_header(self.root)
        self._create_alignment_toolbar(self.root)

        editor_area = tk.Frame(
            self.root,
            bg="#909090",
        )
        editor_area.pack(
            fill="both",
            expand=True,
        )

        editor_area.grid_rowconfigure(1, weight=1)
        editor_area.grid_columnconfigure(1, weight=1)

        self._create_corner(editor_area)
        self._create_canvas(editor_area)
        self._create_rulers(editor_area)
        self._create_status_bar(self.root)

        self._display_retry_count = 0
        self.parent.after_idle(self._prepare_first_display)

    def _create_header(self, parent) -> None:

        header = ctk.CTkFrame(
            parent,
            fg_color="transparent",
            height=60,
        )
        header.pack(
            fill="x",
            padx=20,
            pady=(20, 10),
        )
        header.pack_propagate(False)

        ctk.CTkButton(
            header,
            text="← Retour",
            width=120,
            command=self.back,
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            text=self.page.display_title,
            font=Fonts.H1,
            text_color=Colors.TEXT,
        ).pack(
            side="left",
            padx=20,
        )

        coordinates = ctk.CTkFrame(
            header,
            fg_color="transparent",
        )
        coordinates.pack(
            side="left",
            padx=(0, 20),
        )

        ctk.CTkLabel(
            coordinates,
            textvariable=self._selection_x_text,
            width=92,
            anchor="w",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
        ).pack(side="left")

        ctk.CTkLabel(
            coordinates,
            textvariable=self._selection_y_text,
            width=92,
            anchor="w",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
        ).pack(side="left")

        ctk.CTkLabel(
            header,
            textvariable=self._save_status_text,
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
        ).pack(
            side="left",
            padx=(0, 20),
        )

        page_type = getattr(
            self.page,
            "page_type",
            "Page vide",
        )

        ctk.CTkLabel(
            header,
            text=page_type,
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
        ).pack(side="right")

    def _create_alignment_toolbar(self, parent) -> None:

        toolbar = ctk.CTkFrame(
            parent,
            fg_color="#D9D9D9",
            corner_radius=0,
        )
        toolbar.pack(
            fill="x",
            padx=20,
            pady=(0, 10),
        )

        alignment_row = ctk.CTkFrame(
            toolbar,
            fg_color="transparent",
        )
        alignment_row.pack(fill="x", padx=8, pady=(6, 3))

        ctk.CTkLabel(
            alignment_row,
            text="Alignement",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
            width=90,
            anchor="w",
        ).pack(side="left", padx=(4, 8))

        buttons = (
            ("Gauche", "left"),
            ("Centre H", "center_horizontal"),
            ("Droite", "right"),
            ("Haut", "top"),
            ("Centre V", "center_vertical"),
            ("Bas", "bottom"),
        )

        for label, alignment in buttons:
            ctk.CTkButton(
                alignment_row,
                text=label,
                width=86,
                height=30,
                command=lambda value=alignment: self._align_selection(value),
            ).pack(side="left", padx=3)

        ctk.CTkButton(
            alignment_row,
            text="Distribuer H",
            width=104,
            height=30,
            command=self._distribute_selection_horizontally,
        ).pack(side="left", padx=(12, 3))

        ctk.CTkButton(
            alignment_row,
            text="Distribuer V",
            width=104,
            height=30,
            command=self._distribute_selection_vertically,
        ).pack(side="left", padx=3)

        properties_row = ctk.CTkFrame(
            toolbar,
            fg_color="transparent",
        )
        properties_row.pack(fill="x", padx=8, pady=(3, 6))

        ctk.CTkLabel(
            properties_row,
            text="Dimensions",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
            width=90,
            anchor="w",
        ).pack(side="left", padx=(4, 8))

        ctk.CTkButton(
            properties_row,
            text="Même largeur",
            width=110,
            height=30,
            command=self._make_selection_same_width,
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            properties_row,
            text="Même hauteur",
            width=110,
            height=30,
            command=self._make_selection_same_height,
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            properties_row,
            text="Même taille",
            width=104,
            height=30,
            command=self._make_selection_same_size,
        ).pack(side="left", padx=3)

        appearance_row = ctk.CTkFrame(
            toolbar,
            fg_color="transparent",
        )
        appearance_row.pack(fill="x", padx=8, pady=(3, 6))

        ctk.CTkLabel(
            appearance_row,
            text="Apparence",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
            width=90,
            anchor="w",
        ).pack(side="left", padx=(4, 8))

        ctk.CTkButton(
            appearance_row,
            text="Remplissage",
            width=110,
            height=30,
            command=self._choose_fill_color,
        ).pack(side="left", padx=3)

        ctk.CTkLabel(
            appearance_row,
            text="Copie sélective",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
            width=110,
            anchor="e",
        ).pack(side="left", padx=(22, 8))

        ctk.CTkButton(
            appearance_row,
            text="Copier propriétés",
            width=132,
            height=30,
            command=self._open_copy_properties_dialog,
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            appearance_row,
            text="Coller propriétés",
            width=132,
            height=30,
            command=self._paste_properties,
        ).pack(side="left", padx=3)

    def _align_selection(self, alignment: str) -> None:
        """Aligne chaque objet sélectionné individuellement sur la page."""

        if self.workspace is None:
            return

        selected_indices = [
            index
            for index in sorted(self.workspace._selected_object_indices)
            if 0 <= index < len(self.workspace._objects)
        ]

        if not selected_indices:
            return

        page_width = self.workspace.page_format.width_mm
        page_height = self.workspace.page_format.height_mm

        self.workspace._remember_current_state()

        for index in selected_indices:
            graphic_object = self.workspace._objects[index]
            bounds = graphic_object.bounds
            new_x = bounds.left
            new_y = bounds.top

            if alignment == "left":
                new_x = 0.0
            elif alignment == "center_horizontal":
                new_x = (page_width - bounds.width) / 2
            elif alignment == "right":
                new_x = page_width - bounds.width
            elif alignment == "top":
                new_y = 0.0
            elif alignment == "center_vertical":
                new_y = (page_height - bounds.height) / 2
            elif alignment == "bottom":
                new_y = page_height - bounds.height
            else:
                return

            self.workspace._objects[index] = replace(
                graphic_object,
                bounds=Rect(
                    Point(new_x, new_y),
                    bounds.size,
                ),
            )

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()


    def _distribute_selection_horizontally(self) -> None:
        """Répartit régulièrement les objets sélectionnés de gauche à droite."""

        if self.workspace is None:
            return

        selected_indices = [
            index
            for index in self.workspace._selected_object_indices
            if 0 <= index < len(self.workspace._objects)
        ]

        if len(selected_indices) < 3:
            return

        selected_indices.sort(
            key=lambda index: self.workspace._objects[index].bounds.left
        )

        selected_objects = [
            self.workspace._objects[index]
            for index in selected_indices
        ]

        first_bounds = selected_objects[0].bounds
        last_bounds = selected_objects[-1].bounds
        total_width = sum(
            graphic_object.bounds.width
            for graphic_object in selected_objects
        )
        available_width = last_bounds.right - first_bounds.left
        spacing = (available_width - total_width) / (len(selected_objects) - 1)

        self.workspace._remember_current_state()

        current_x = first_bounds.left

        for index, graphic_object in zip(selected_indices, selected_objects):
            bounds = graphic_object.bounds
            self.workspace._objects[index] = replace(
                graphic_object,
                bounds=Rect(
                    Point(current_x, bounds.top),
                    bounds.size,
                ),
            )
            current_x += bounds.width + spacing

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()

    def _distribute_selection_vertically(self) -> None:
        """Répartit régulièrement les objets sélectionnés de haut en bas."""

        if self.workspace is None:
            return

        selected_indices = [
            index
            for index in self.workspace._selected_object_indices
            if 0 <= index < len(self.workspace._objects)
        ]

        if len(selected_indices) < 3:
            return

        selected_indices.sort(
            key=lambda index: self.workspace._objects[index].bounds.top
        )

        selected_objects = [
            self.workspace._objects[index]
            for index in selected_indices
        ]

        first_bounds = selected_objects[0].bounds
        last_bounds = selected_objects[-1].bounds
        total_height = sum(
            graphic_object.bounds.height
            for graphic_object in selected_objects
        )
        available_height = last_bounds.bottom - first_bounds.top
        spacing = (available_height - total_height) / (len(selected_objects) - 1)

        self.workspace._remember_current_state()

        current_y = first_bounds.top

        for index, graphic_object in zip(selected_indices, selected_objects):
            bounds = graphic_object.bounds
            self.workspace._objects[index] = replace(
                graphic_object,
                bounds=Rect(
                    Point(bounds.left, current_y),
                    bounds.size,
                ),
            )
            current_y += bounds.height + spacing

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()

    def _make_selection_same_width(self) -> None:
        """Donne aux objets cibles la largeur de l'objet rouge."""

        if self.workspace is None:
            return

        reference_index = self.workspace.get_reference_object_index()

        if reference_index is None:
            self._save_status_text.set("Choisir d'abord l'objet rouge")
            return

        selected_indices = [
            index
            for index in sorted(self.workspace._selected_object_indices)
            if (
                0 <= index < len(self.workspace._objects)
                and index != reference_index
            )
        ]

        if not selected_indices:
            self._save_status_text.set("Sélectionner au moins un objet cible")
            return

        reference_width = self.workspace._objects[
            reference_index
        ].bounds.width

        self.workspace._remember_current_state()

        for index in selected_indices:
            graphic_object = self.workspace._objects[index]
            bounds = graphic_object.bounds
            self.workspace._objects[index] = replace(
                graphic_object,
                bounds=Rect(
                    bounds.origin,
                    Size(reference_width, bounds.height),
                ),
            )

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()
        self._save_status_text.set(
            f"Largeur appliquée à {len(selected_indices)} objet(s)"
        )

    def _make_selection_same_height(self) -> None:
        """Donne aux objets cibles la hauteur de l'objet rouge."""

        if self.workspace is None:
            return

        reference_index = self.workspace.get_reference_object_index()

        if reference_index is None:
            self._save_status_text.set("Choisir d'abord l'objet rouge")
            return

        selected_indices = [
            index
            for index in sorted(self.workspace._selected_object_indices)
            if (
                0 <= index < len(self.workspace._objects)
                and index != reference_index
            )
        ]

        if not selected_indices:
            self._save_status_text.set("Sélectionner au moins un objet cible")
            return

        reference_height = self.workspace._objects[
            reference_index
        ].bounds.height

        self.workspace._remember_current_state()

        for index in selected_indices:
            graphic_object = self.workspace._objects[index]
            bounds = graphic_object.bounds
            self.workspace._objects[index] = replace(
                graphic_object,
                bounds=Rect(
                    bounds.origin,
                    Size(bounds.width, reference_height),
                ),
            )

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()
        self._save_status_text.set(
            f"Hauteur appliquée à {len(selected_indices)} objet(s)"
        )

    def _make_selection_same_size(self) -> None:
        """Donne aux objets cibles la taille de l'objet rouge."""

        if self.workspace is None:
            return

        reference_index = self.workspace.get_reference_object_index()

        if reference_index is None:
            self._save_status_text.set("Choisir d'abord l'objet rouge")
            return

        selected_indices = [
            index
            for index in sorted(self.workspace._selected_object_indices)
            if (
                0 <= index < len(self.workspace._objects)
                and index != reference_index
            )
        ]

        if not selected_indices:
            self._save_status_text.set("Sélectionner au moins un objet cible")
            return

        reference_bounds = self.workspace._objects[
            reference_index
        ].bounds

        self.workspace._remember_current_state()

        for index in selected_indices:
            graphic_object = self.workspace._objects[index]
            bounds = graphic_object.bounds
            self.workspace._objects[index] = replace(
                graphic_object,
                bounds=Rect(
                    bounds.origin,
                    Size(
                        reference_bounds.width,
                        reference_bounds.height,
                    ),
                ),
            )

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()
        self._save_status_text.set(
            f"Taille appliquée à {len(selected_indices)} objet(s)"
        )


    def _choose_fill_color(self) -> None:
        """Modifie la couleur de remplissage des objets sélectionnés."""

        if self.workspace is None:
            return

        selected_indices = [
            index
            for index in sorted(self.workspace._selected_object_indices)
            if 0 <= index < len(self.workspace._objects)
        ]

        if not selected_indices:
            self._save_status_text.set("Sélectionner au moins un objet")
            return

        initial_color = self.workspace._objects[selected_indices[0]].fill
        chosen_color = colorchooser.askcolor(
            color=initial_color,
            title="Couleur de remplissage",
            parent=self.parent.winfo_toplevel(),
        )[1]

        if not chosen_color:
            self.workspace.focus_set()
            return

        self.workspace._remember_current_state()

        for index in selected_indices:
            graphic_object = self.workspace._objects[index]
            self.workspace._objects[index] = replace(
                graphic_object,
                fill=chosen_color,
            )

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()
        self._save_status_text.set(
            f"Remplissage modifié sur {len(selected_indices)} objet(s)"
        )

    def _open_copy_properties_dialog(self) -> None:
        """Ouvre le choix des propriétés à copier depuis l'objet rouge."""

        if self.workspace is None:
            return

        reference_index = self.workspace.get_reference_object_index()

        if reference_index is None:
            self._save_status_text.set("Choisir d'abord l'objet rouge")
            return

        if not (0 <= reference_index < len(self.workspace._objects)):
            return

        source = self.workspace._objects[reference_index]

        dialog = ctk.CTkToplevel(self.parent)
        dialog.title("Copier les propriétés")
        dialog.geometry("390x520")
        dialog.resizable(False, False)
        dialog.transient(self.parent.winfo_toplevel())
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text="Propriétés à copier",
            font=Fonts.H1,
            text_color=Colors.TEXT,
        ).pack(padx=24, pady=(22, 12), anchor="w")

        ctk.CTkLabel(
            dialog,
            text="La forme rouge est utilisée comme modèle.",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
        ).pack(padx=24, pady=(0, 12), anchor="w")

        property_choices = (
            ("fill", "Remplissage"),
            ("outline", "Couleur du contour"),
            ("line_width", "Épaisseur du contour"),
            ("text_color", "Couleur du texte"),
            ("font_family", "Police"),
            ("font_size", "Taille de police"),
            ("bold", "Gras"),
            ("italic", "Italique"),
            ("align", "Alignement du texte"),
        )

        variables: dict[str, tk.BooleanVar] = {}

        options_frame = ctk.CTkScrollableFrame(
            dialog,
            fg_color="transparent",
            height=330,
        )
        options_frame.pack(fill="both", expand=True, padx=18, pady=(0, 12))

        for property_name, label in property_choices:
            is_available = property_name == "fill"
            variable = tk.BooleanVar(value=is_available)
            variables[property_name] = variable
            checkbox = ctk.CTkCheckBox(
                options_frame,
                text=label if is_available else f"{label} — bientôt disponible",
                variable=variable,
                font=Fonts.NORMAL,
            )
            checkbox.pack(anchor="w", padx=8, pady=7)
            if not is_available:
                checkbox.configure(state="disabled")

        buttons_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons_frame.pack(fill="x", padx=20, pady=(0, 18))

        def confirm_copy() -> None:
            selected_properties = {
                name: getattr(source, name)
                for name, variable in variables.items()
                if variable.get()
            }

            if not selected_properties:
                self._save_status_text.set("Aucune propriété choisie")
                return

            self._copied_properties = selected_properties
            self._save_status_text.set(
                f"{len(selected_properties)} propriété(s) copiée(s)"
            )
            dialog.grab_release()
            dialog.destroy()
            self.workspace.focus_set()

        ctk.CTkButton(
            buttons_frame,
            text="Annuler",
            width=110,
            command=dialog.destroy,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            buttons_frame,
            text="Copier",
            width=110,
            command=confirm_copy,
        ).pack(side="right")

        dialog.protocol("WM_DELETE_WINDOW", dialog.destroy)
        dialog.after(50, dialog.focus_force)

    def _paste_properties(self) -> None:
        """Applique les propriétés mémorisées aux objets sélectionnés."""

        if self.workspace is None:
            return

        if not self._copied_properties:
            self._save_status_text.set("Aucune propriété copiée")
            return

        reference_index = self.workspace.get_reference_object_index()

        selected_indices = [
            index
            for index in sorted(self.workspace._selected_object_indices)
            if (
                0 <= index < len(self.workspace._objects)
                and index != reference_index
            )
        ]

        if not selected_indices:
            self._save_status_text.set("Aucun objet cible sélectionné")
            return

        self.workspace._remember_current_state()

        for index in selected_indices:
            graphic_object = self.workspace._objects[index]
            self.workspace._objects[index] = replace(
                graphic_object,
                **self._copied_properties,
            )

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()
        self._save_status_text.set(
            f"Propriétés appliquées à {len(selected_indices)} objet(s)"
        )

    def _create_corner(self, parent) -> None:

        corner = tk.Frame(
            parent,
            bg="#CFCFCF",
            width=self.RULER_SIZE,
            height=self.RULER_SIZE,
        )
        corner.grid(
            row=0,
            column=0,
            sticky="nsew",
        )
        corner.grid_propagate(False)

    def _create_canvas(self, parent) -> None:

        canvas_container = tk.Frame(
            parent,
            bg="#909090",
        )
        canvas_container.grid(
            row=1,
            column=1,
            sticky="nsew",
        )

        self.workspace = EditorCanvas(canvas_container)
        self.workspace.pack(
            fill="both",
            expand=True,
        )

        self.workspace.set_page_format(
            self._resolve_page_format(),
        )

        saved_objects = self._load_page_objects()

        if saved_objects:
            self.workspace._objects = saved_objects

        self.workspace.add_selection_listener(
            self._refresh_selection_label,
        )

        window = self.parent.winfo_toplevel()
        window.bind(
            "<Control-s>",
            self._save_shortcut,
            add="+",
        )
        window.bind(
            "<Control-S>",
            self._save_shortcut,
            add="+",
        )

    def _refresh_selection_label(
        self,
        selected_object: CanvasObject | None,
    ) -> None:

        if selected_object is None:
            self._selection_x_text.set("X : — mm")
            self._selection_y_text.set("Y : — mm")
        else:
            self._selection_x_text.set(
                f"X : {selected_object.bounds.left:.2f} mm",
            )
            self._selection_y_text.set(
                f"Y : {selected_object.bounds.top:.2f} mm",
            )

        self._save_page_objects(show_status=False)

    def _create_rulers(self, parent) -> None:

        if self.workspace is None:
            return

        horizontal_ruler = HorizontalRuler(
            parent,
            self.workspace,
        )
        horizontal_ruler.grid(
            row=0,
            column=1,
            sticky="ew",
        )

        vertical_ruler = VerticalRuler(
            parent,
            self.workspace,
        )
        vertical_ruler.grid(
            row=1,
            column=0,
            sticky="ns",
        )

        self.workspace.viewport.add_listener(
            horizontal_ruler.redraw,
        )

        self.workspace.viewport.add_listener(
            vertical_ruler.redraw,
        )

    def _create_status_bar(self, parent) -> None:

        if self.workspace is None:
            return

        self.status_bar = StatusBar(parent)
        self.status_bar.pack(
            fill="x",
            side="bottom",
        )

        self.status_bar.attach(self.workspace)

        self.workspace.add_mouse_listener(
            self.status_bar.refresh,
        )

    def _prepare_first_display(self) -> None:

        if self.workspace is None:
            return

        if not self.workspace.winfo_exists():
            return

        self.workspace.update_idletasks()

        width = self.workspace.winfo_width()
        height = self.workspace.winfo_height()

        if (
            width < self.MIN_READY_SIZE
            or height < self.MIN_READY_SIZE
        ):
            self._display_retry_count += 1

            if self._display_retry_count <= self.MAX_DISPLAY_RETRIES:
                self.parent.after(
                    self.DISPLAY_RETRY_DELAY_MS,
                    self._prepare_first_display,
                )
            return

        self.workspace._fit_page()
        self.workspace.redraw()

    def _resolve_page_format(self):

        format_name = str(
            getattr(
                self.page,
                "format",
                "A5",
            )
        ).strip()

        page_format = PAGE_FORMATS.get(
            format_name,
            A5,
        )

        orientation = str(
            getattr(
                self.page,
                "orientation",
                "Portrait",
            )
        ).strip().lower()

        if orientation == "paysage":
            return type(page_format)(
                name=page_format.name,
                width_mm=page_format.height_mm,
                height_mm=page_format.width_mm,
            )

        return page_format

    def _load_page_objects(self) -> list[CanvasObject]:

        objects: list[CanvasObject] = []

        for element in getattr(self.page, "elements", []):
            if element.get("type") != "canvas_object":
                continue

            bounds = element.get("bounds", {})

            try:
                objects.append(
                    CanvasObject(
                        kind=str(element.get("kind", "rectangle")),
                        bounds=Rect(
                            Point(
                                float(bounds.get("x", 0.0)),
                                float(bounds.get("y", 0.0)),
                            ),
                            Size(
                                float(bounds.get("width", 0.0)),
                                float(bounds.get("height", 0.0)),
                            ),
                        ),
                        fill=str(element.get("fill", "#F4F4F4")),
                        outline=str(element.get("outline", "#222222")),
                        line_width=int(element.get("line_width", 2)),
                        text=str(element.get("text", "Bloc de texte")),
                        text_color=str(element.get("text_color", "#222222")),
                        font_family=str(element.get("font_family", "Arial")),
                        font_size=int(element.get("font_size", 12)),
                        bold=bool(element.get("bold", False)),
                        italic=bool(element.get("italic", False)),
                        align=str(element.get("align", "left")),
                    )
                )
            except (TypeError, ValueError):
                continue

        if objects:
            return objects

        saved_objects = getattr(
            self.page,
            "_editor_objects",
            None,
        )

        return list(saved_objects or [])

    @staticmethod
    def _serialize_object(canvas_object: CanvasObject) -> dict:

        return {
            "type": "canvas_object",
            "kind": canvas_object.kind,
            "bounds": {
                "x": canvas_object.bounds.left,
                "y": canvas_object.bounds.top,
                "width": canvas_object.bounds.width,
                "height": canvas_object.bounds.height,
            },
            "fill": canvas_object.fill,
            "outline": canvas_object.outline,
            "line_width": canvas_object.line_width,
            "text": canvas_object.text,
            "text_color": canvas_object.text_color,
            "font_family": canvas_object.font_family,
            "font_size": canvas_object.font_size,
            "bold": canvas_object.bold,
            "italic": canvas_object.italic,
            "align": canvas_object.align,
        }

    def _save_shortcut(self, event=None) -> str:

        self._save_page_objects(show_status=True)
        return "break"

    def _save_page_objects(
        self,
        show_status: bool = False,
    ) -> None:

        if self.workspace is None:
            return

        current_objects = list(self.workspace._objects)
        self.page._editor_objects = current_objects

        preserved_elements = [
            element
            for element in getattr(self.page, "elements", [])
            if element.get("type") != "canvas_object"
        ]

        self.page.elements = preserved_elements + [
            self._serialize_object(canvas_object)
            for canvas_object in current_objects
        ]

        save_page = getattr(self.page, "save", None)

        if callable(save_page):
            save_page(update_history=False)

        if show_status:
            self._save_status_text.set("Enregistré")
            if self.root is not None:
                self.root.after(
                    1500,
                    lambda: self._save_status_text.set(""),
                )

    def back(self) -> None:

        self._save_page_objects()

        self.workspace = None
        self.status_bar = None
        self.root = None

        if self.on_back is not None:
            self.on_back()

    def _clear_parent(self) -> None:

        for widget in self.parent.winfo_children():
            widget.destroy()

    def __repr__(self) -> str:

        return (
            "PageEditorView("
            f"page={self.page.display_title!r})"
        )