from __future__ import annotations

from dataclasses import replace
import tkinter as tk
from tkinter import colorchooser, font as tkfont

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
        self._font_family_var = tk.StringVar(value="Arial")
        self._font_size_var = tk.StringVar(value="12")
        self._font_family_combo = None
        self._font_size_entry = None
        self._text_color_button = None
        self._bold_button = None
        self._italic_button = None
        self._text_align_buttons: dict[str, object] = {}
        self._text_controls: list[object] = []
        self._updating_text_controls = False
        self._fill_color_button = None
        self._outline_color_button = None
        self._line_width_var = tk.StringVar(value="2")
        self._line_width_combo = None
        self._shape_controls: list[object] = []
        self._updating_shape_controls = False
        self._lock_button = None
        self._group_button = None
        self._ungroup_button = None

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

        order_row = ctk.CTkFrame(
            toolbar,
            fg_color="transparent",
        )
        order_row.pack(fill="x", padx=8, pady=(3, 6))

        ctk.CTkLabel(
            order_row,
            text="Ordre",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
            width=90,
            anchor="w",
        ).pack(side="left", padx=(4, 8))

        ctk.CTkButton(
            order_row,
            text="Arrière-plan",
            width=112,
            height=30,
            command=lambda: self._change_object_order("back"),
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            order_row,
            text="Reculer",
            width=92,
            height=30,
            command=lambda: self._change_object_order("backward"),
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            order_row,
            text="Avancer",
            width=92,
            height=30,
            command=lambda: self._change_object_order("forward"),
        ).pack(side="left", padx=3)

        ctk.CTkButton(
            order_row,
            text="Premier plan",
            width=112,
            height=30,
            command=lambda: self._change_object_order("front"),
        ).pack(side="left", padx=3)

        protection_row = ctk.CTkFrame(
            toolbar,
            fg_color="transparent",
        )
        protection_row.pack(fill="x", padx=8, pady=(3, 6))

        ctk.CTkLabel(
            protection_row,
            text="Protection",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
            width=90,
            anchor="w",
        ).pack(side="left", padx=(4, 8))

        self._lock_button = ctk.CTkButton(
            protection_row,
            text="Verrouiller",
            width=120,
            height=30,
            command=self._toggle_selection_lock,
            state="disabled",
        )
        self._lock_button.pack(side="left", padx=3)

        ctk.CTkLabel(
            protection_row,
            text="Raccourci : Ctrl + L",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
        ).pack(side="left", padx=(10, 0))

        group_row = ctk.CTkFrame(
            toolbar,
            fg_color="transparent",
        )
        group_row.pack(fill="x", padx=8, pady=(3, 6))

        ctk.CTkLabel(
            group_row,
            text="Groupement",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
            width=90,
            anchor="w",
        ).pack(side="left", padx=(4, 8))

        self._group_button = ctk.CTkButton(
            group_row,
            text="Grouper",
            width=110,
            height=30,
            command=self._group_selection,
            state="disabled",
        )
        self._group_button.pack(side="left", padx=3)

        self._ungroup_button = ctk.CTkButton(
            group_row,
            text="Dissocier",
            width=110,
            height=30,
            command=self._ungroup_selection,
            state="disabled",
        )
        self._ungroup_button.pack(side="left", padx=3)

        ctk.CTkLabel(
            group_row,
            text="Raccourcis : Ctrl + G / Ctrl + Maj + G",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT_LIGHT,
        ).pack(side="left", padx=(10, 0))

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

        self._fill_color_button = ctk.CTkButton(
            appearance_row,
            text="Remplissage",
            width=110,
            height=30,
            command=self._choose_fill_color,
        )
        self._fill_color_button.pack(side="left", padx=3)

        self._outline_color_button = ctk.CTkButton(
            appearance_row,
            text="Contour",
            width=94,
            height=30,
            command=self._choose_outline_color,
        )
        self._outline_color_button.pack(side="left", padx=3)

        ctk.CTkLabel(
            appearance_row,
            text="Épaisseur",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
            width=72,
        ).pack(side="left", padx=(8, 2))

        self._line_width_combo = ctk.CTkComboBox(
            appearance_row,
            variable=self._line_width_var,
            values=["Sans contour", "1", "2", "3", "4", "5", "6", "8", "10"],
            width=66,
            height=30,
            state="readonly",
            command=self._change_line_width,
        )
        self._line_width_combo.pack(side="left", padx=3)

        self._shape_controls = [
            self._fill_color_button,
            self._outline_color_button,
            self._line_width_combo,
        ]
        self._set_shape_controls_enabled(False)

        ctk.CTkLabel(
            appearance_row,
            text="Copie sélective",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
            width=110,
            anchor="e",
        ).pack(side="left", padx=(18, 8))

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

        text_row = ctk.CTkFrame(
            toolbar,
            fg_color="transparent",
        )
        text_row.pack(fill="x", padx=8, pady=(3, 8))

        ctk.CTkLabel(
            text_row,
            text="Texte",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
            width=90,
            anchor="w",
        ).pack(side="left", padx=(4, 8))

        font_values = self._available_font_families()
        self._font_family_combo = ctk.CTkComboBox(
            text_row,
            variable=self._font_family_var,
            values=font_values,
            width=190,
            height=30,
            state="readonly",
            command=self._change_font_family,
        )
        self._font_family_combo.pack(side="left", padx=3)

        ctk.CTkLabel(
            text_row,
            text="Taille",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
            width=48,
        ).pack(side="left", padx=(10, 2))

        self._font_size_entry = ctk.CTkEntry(
            text_row,
            textvariable=self._font_size_var,
            width=58,
            height=30,
            justify="center",
        )
        self._font_size_entry.pack(side="left", padx=3)
        self._font_size_entry.bind(
            "<Return>",
            self._apply_font_size,
        )
        self._font_size_entry.bind(
            "<FocusOut>",
            self._apply_font_size,
        )

        self._bold_button = ctk.CTkButton(
            text_row,
            text="G",
            width=38,
            height=30,
            command=lambda: self._toggle_text_style("bold"),
        )
        self._bold_button.pack(side="left", padx=(10, 3))

        self._italic_button = ctk.CTkButton(
            text_row,
            text="I",
            width=38,
            height=30,
            command=lambda: self._toggle_text_style("italic"),
        )
        self._italic_button.pack(side="left", padx=3)

        self._text_color_button = ctk.CTkButton(
            text_row,
            text="Couleur",
            width=88,
            height=30,
            command=self._choose_text_color,
        )
        self._text_color_button.pack(side="left", padx=(10, 3))

        for label, alignment in (
            ("À gauche", "left"),
            ("Centré", "center"),
            ("À droite", "right"),
        ):
            button = ctk.CTkButton(
                text_row,
                text=label,
                width=82,
                height=30,
                command=lambda value=alignment: self._set_text_alignment(value),
            )
            button.pack(side="left", padx=3)
            self._text_align_buttons[alignment] = button

        self._text_controls = [
            self._font_family_combo,
            self._font_size_entry,
            self._bold_button,
            self._italic_button,
            self._text_color_button,
            *self._text_align_buttons.values(),
        ]
        self._set_text_controls_enabled(False)

    def _unlocked_indices(self, indices) -> list[int]:
        """Conserve uniquement les objets existants et déverrouillés."""

        if self.workspace is None:
            return []

        return [
            index
            for index in indices
            if (
                0 <= index < len(self.workspace._objects)
                and not self.workspace._objects[index].locked
            )
        ]

    def _refresh_lock_control(self) -> None:
        """Actualise le bouton de verrouillage selon la sélection courante."""

        if self._lock_button is None:
            return

        if self.workspace is None:
            self._lock_button.configure(
                text="Verrouiller",
                state="disabled",
            )
            return

        state = self.workspace.get_selection_lock_state()

        if state is None:
            self._lock_button.configure(
                text="Verrouiller",
                state="disabled",
            )
        elif state:
            self._lock_button.configure(
                text="Déverrouiller",
                state="normal",
            )
        else:
            self._lock_button.configure(
                text="Verrouiller",
                state="normal",
            )

    def _toggle_selection_lock(self) -> None:
        """Verrouille ou déverrouille les objets actuellement sélectionnés."""

        if self.workspace is None:
            return

        state = self.workspace.get_selection_lock_state()

        if state is None:
            self._save_status_text.set("Sélectionner au moins un objet")
            return

        target_locked_state = not state
        changed = self.workspace.set_selection_locked(target_locked_state)

        if changed:
            if target_locked_state:
                self._save_status_text.set("Objet(s) verrouillé(s)")
            else:
                self._save_status_text.set("Objet(s) déverrouillé(s)")

        self._refresh_lock_control()
        self.workspace.focus_set()

    def _refresh_group_controls(self) -> None:
        """Actualise les commandes de groupement selon la sélection."""

        if self._group_button is None or self._ungroup_button is None:
            return

        if self.workspace is None:
            self._group_button.configure(state="disabled")
            self._ungroup_button.configure(state="disabled")
            return

        self._group_button.configure(
            state=(
                "normal"
                if self.workspace.can_group_selection()
                else "disabled"
            ),
        )
        self._ungroup_button.configure(
            state=(
                "normal"
                if self.workspace.can_ungroup_selection()
                else "disabled"
            ),
        )

    def _group_selection(self) -> None:
        """Groupe les objets bleus sélectionnés."""

        if self.workspace is None:
            return

        if self.workspace.group_selection():
            self._save_status_text.set("Objets groupés")
        else:
            self._save_status_text.set(
                "Sélectionner au moins deux objets déverrouillés",
            )

        self._refresh_group_controls()
        self.workspace.focus_set()

    def _ungroup_selection(self) -> None:
        """Dissocie le ou les groupes sélectionnés."""

        if self.workspace is None:
            return

        if self.workspace.ungroup_selection():
            self._save_status_text.set("Groupe dissocié")
        else:
            self._save_status_text.set(
                "Sélectionner un groupe déverrouillé",
            )

        self._refresh_group_controls()
        self.workspace.focus_set()

    def _selected_order_indices(self) -> list[int]:
        """Retourne les objets bleus concernés par l'ordre d'empilement."""

        if self.workspace is None:
            return []

        selected_indices = self._unlocked_indices(
            sorted(self.workspace._selected_object_indices)
        )

        if not selected_indices:
            primary_index = self.workspace._selected_object_index
            if (
                primary_index is not None
                and 0 <= primary_index < len(self.workspace._objects)
                and not self.workspace._objects[primary_index].locked
            ):
                selected_indices = [primary_index]

        reference_index = self.workspace.get_reference_object_index()
        target_indices = [
            index
            for index in selected_indices
            if index != reference_index
        ]

        return target_indices or selected_indices

    @staticmethod
    def _index_by_identity(objects: list[CanvasObject], target) -> int | None:
        if target is None:
            return None

        for index, graphic_object in enumerate(objects):
            if graphic_object is target:
                return index

        return None

    def _restore_indices_after_reorder(
        self,
        selected_objects: list[CanvasObject],
        primary_object,
        reference_object,
    ) -> None:
        """Rétablit sélection et référence après réorganisation de la liste."""

        if self.workspace is None:
            return

        objects = self.workspace._objects
        selected_indices = {
            index
            for selected_object in selected_objects
            if (
                index := self._index_by_identity(objects, selected_object)
            ) is not None
        }

        primary_index = self._index_by_identity(objects, primary_object)
        if primary_index not in selected_indices:
            primary_index = max(selected_indices) if selected_indices else None

        self.workspace._selected_object_indices = selected_indices
        self.workspace._selected_object_index = primary_index
        self.workspace._reference_object_index = self._index_by_identity(
            objects,
            reference_object,
        )

    def _change_object_order(self, action: str) -> None:
        """Modifie l'ordre d'empilement des objets sélectionnés."""

        if self.workspace is None:
            return

        target_indices = self._selected_order_indices()
        if not target_indices:
            self._save_status_text.set("Sélectionner au moins un objet")
            return

        self.workspace.commit_active_text_edit()

        objects = list(self.workspace._objects)
        target_objects = [objects[index] for index in target_indices]
        target_identities = {id(graphic_object) for graphic_object in target_objects}

        selected_objects = [
            objects[index]
            for index in sorted(self.workspace._selected_object_indices)
            if 0 <= index < len(objects)
        ]
        primary_object = (
            objects[self.workspace._selected_object_index]
            if (
                self.workspace._selected_object_index is not None
                and 0 <= self.workspace._selected_object_index < len(objects)
            )
            else None
        )
        reference_index = self.workspace.get_reference_object_index()
        reference_object = (
            objects[reference_index]
            if reference_index is not None
            else None
        )

        reordered = list(objects)

        if action == "front":
            reordered = [
                graphic_object
                for graphic_object in objects
                if id(graphic_object) not in target_identities
            ] + target_objects
            status_label = "Placé au premier plan"

        elif action == "back":
            reordered = target_objects + [
                graphic_object
                for graphic_object in objects
                if id(graphic_object) not in target_identities
            ]
            status_label = "Placé à l’arrière-plan"

        elif action == "forward":
            for index in range(len(reordered) - 2, -1, -1):
                current_selected = id(reordered[index]) in target_identities
                next_selected = id(reordered[index + 1]) in target_identities
                if current_selected and not next_selected:
                    reordered[index], reordered[index + 1] = (
                        reordered[index + 1],
                        reordered[index],
                    )
            status_label = "Avancé d’un niveau"

        elif action == "backward":
            for index in range(1, len(reordered)):
                current_selected = id(reordered[index]) in target_identities
                previous_selected = id(reordered[index - 1]) in target_identities
                if current_selected and not previous_selected:
                    reordered[index], reordered[index - 1] = (
                        reordered[index - 1],
                        reordered[index],
                    )
            status_label = "Reculé d’un niveau"

        else:
            return

        changed = any(
            before is not after
            for before, after in zip(objects, reordered)
        )

        if not changed:
            self._save_status_text.set("Ordre déjà atteint")
            self.workspace.focus_set()
            return

        self.workspace._remember_current_state()
        self.workspace._objects = reordered
        self._restore_indices_after_reorder(
            selected_objects,
            primary_object,
            reference_object,
        )
        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()
        self._save_status_text.set(
            f"{status_label} : {len(target_objects)} objet(s)"
        )

    def _available_font_families(self) -> list[str]:
        """Retourne les polices installées, avec les plus courantes en tête."""

        preferred = [
            "Arial",
            "Calibri",
            "Cambria",
            "Garamond",
            "Georgia",
            "Times New Roman",
            "Verdana",
            "Courier New",
        ]

        try:
            installed = sorted(
                {
                    name
                    for name in tkfont.families(self.parent)
                    if name and not name.startswith("@")
                },
                key=str.casefold,
            )
        except tk.TclError:
            installed = []

        ordered = [name for name in preferred if name in installed]
        ordered.extend(name for name in installed if name not in ordered)

        return ordered or preferred

    def _selected_shape_indices(self) -> list[int]:
        """Retourne les objets ciblés par les commandes d'apparence.

        Toutes les zones graphiques possèdent un remplissage et un contour,
        y compris les zones de texte. La référence rouge est protégée dès
        qu'une ou plusieurs cibles bleues sont sélectionnées.
        """

        if self.workspace is None:
            return []

        selected_indices = self._unlocked_indices(
            sorted(self.workspace._selected_object_indices)
        )

        # L'index principal ne sert que de secours lorsque le canvas vient de
        # sélectionner un objet et que l'ensemble multiple n'est pas encore
        # renseigné. Il n'est jamais ajouté à une sélection déjà existante.
        if not selected_indices:
            primary_index = self.workspace._selected_object_index
            if (
                primary_index is not None
                and 0 <= primary_index < len(self.workspace._objects)
                and not self.workspace._objects[primary_index].locked
            ):
                selected_indices = [primary_index]

        reference_index = self.workspace.get_reference_object_index()
        target_indices = [
            index
            for index in selected_indices
            if index != reference_index
        ]

        return target_indices or selected_indices

    def _set_shape_controls_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"

        for control in self._shape_controls:
            if control is not None:
                control.configure(state=state)

        if enabled and self._line_width_combo is not None:
            self._line_width_combo.configure(state="readonly")

    def _refresh_shape_controls(self) -> None:
        if self.workspace is None:
            return

        shape_indices = self._selected_shape_indices()
        self._updating_shape_controls = True

        try:
            if not shape_indices:
                self._line_width_var.set("2")
                self._set_shape_controls_enabled(False)
                return

            line_widths = {
                self.workspace._objects[index].line_width
                for index in shape_indices
            }
            if len(line_widths) == 1:
                line_width = next(iter(line_widths))
                self._line_width_var.set(
                    "Sans contour" if line_width == 0 else str(line_width)
                )
            else:
                self._line_width_var.set("")
            self._set_shape_controls_enabled(True)
        finally:
            self._updating_shape_controls = False

    def _apply_shape_changes(self, status_label: str, **changes) -> bool:
        if self.workspace is None or self._updating_shape_controls:
            return False

        shape_indices = self._selected_shape_indices()

        if not shape_indices:
            self._save_status_text.set("Sélectionner au moins un objet")
            return False

        self.workspace.commit_active_text_edit()
        self.workspace._remember_current_state()

        for index in shape_indices:
            self.workspace._objects[index] = replace(
                self.workspace._objects[index],
                **changes,
            )

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()
        self._save_status_text.set(
            f"{status_label} sur {len(shape_indices)} objet(s)"
        )
        return True

    def _selected_text_indices(self) -> list[int]:
        """Retourne les zones de texte réellement sélectionnées.

        Comme pour les formes, la référence rouge est exclue lorsqu'il existe
        des cibles bleues, mais reste modifiable lorsqu'elle est seule.
        """

        if self.workspace is None:
            return []

        selected_indices = set(self.workspace._selected_object_indices)
        primary_index = self.workspace._selected_object_index

        if (
            primary_index is not None
            and 0 <= primary_index < len(self.workspace._objects)
        ):
            selected_indices.add(primary_index)

        text_indices = [
            index
            for index in sorted(selected_indices)
            if (
                0 <= index < len(self.workspace._objects)
                and self.workspace._objects[index].kind == "text"
                and not self.workspace._objects[index].locked
            )
        ]

        reference_index = self.workspace.get_reference_object_index()
        target_indices = [
            index
            for index in text_indices
            if index != reference_index
        ]

        return target_indices or text_indices

    def _set_text_controls_enabled(self, enabled: bool) -> None:
        state = "normal" if enabled else "disabled"

        for control in self._text_controls:
            if control is not None:
                control.configure(state=state)

        if enabled and self._font_family_combo is not None:
            self._font_family_combo.configure(state="readonly")

    @staticmethod
    def _set_toggle_button_state(button, active: bool) -> None:
        if button is None:
            return

        button.configure(
            fg_color="#3874CB" if active else "#AFAFAF",
            hover_color="#2F63AE" if active else "#999999",
            text_color="#FFFFFF" if active else "#222222",
        )

    def _refresh_text_controls(self) -> None:
        if self.workspace is None:
            return

        text_indices = self._selected_text_indices()
        self._updating_text_controls = True

        try:
            if not text_indices:
                self._font_family_var.set("Arial")
                self._font_size_var.set("12")
                self._set_toggle_button_state(self._bold_button, False)
                self._set_toggle_button_state(self._italic_button, False)
                for button in self._text_align_buttons.values():
                    self._set_toggle_button_state(button, False)
                self._set_text_controls_enabled(False)
                return

            text_objects = [
                self.workspace._objects[index]
                for index in text_indices
            ]

            font_families = {obj.font_family for obj in text_objects}
            font_sizes = {obj.font_size for obj in text_objects}
            bold_values = {obj.bold for obj in text_objects}
            italic_values = {obj.italic for obj in text_objects}
            alignments = {obj.align for obj in text_objects}

            self._font_family_var.set(
                next(iter(font_families))
                if len(font_families) == 1
                else ""
            )
            self._font_size_var.set(
                str(next(iter(font_sizes)))
                if len(font_sizes) == 1
                else ""
            )

            self._set_toggle_button_state(
                self._bold_button,
                bold_values == {True},
            )
            self._set_toggle_button_state(
                self._italic_button,
                italic_values == {True},
            )

            active_alignment = (
                next(iter(alignments))
                if len(alignments) == 1
                else None
            )
            for alignment, button in self._text_align_buttons.items():
                self._set_toggle_button_state(
                    button,
                    alignment == active_alignment,
                )

            self._set_text_controls_enabled(True)
        finally:
            self._updating_text_controls = False

    def _apply_text_changes(self, **changes) -> bool:
        if self.workspace is None or self._updating_text_controls:
            return False

        text_indices = self._selected_text_indices()

        if not text_indices:
            self._save_status_text.set("Sélectionner une zone de texte")
            return False

        self.workspace.commit_active_text_edit()
        self.workspace._remember_current_state()

        for index in text_indices:
            self.workspace._objects[index] = replace(
                self.workspace._objects[index],
                **changes,
            )

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()
        self._save_status_text.set(
            f"Texte modifié sur {len(text_indices)} zone(s)"
        )
        return True

    def _change_font_family(self, font_family: str) -> None:
        if font_family:
            self._apply_text_changes(font_family=font_family)

    def _apply_font_size(self, event=None) -> str | None:
        if self._updating_text_controls:
            return None

        value = self._font_size_var.get().strip()

        try:
            font_size = int(value)
        except ValueError:
            self._save_status_text.set("Taille de police invalide")
            self._refresh_text_controls()
            return "break" if event is not None else None

        if not 1 <= font_size <= 500:
            self._save_status_text.set("Taille comprise entre 1 et 500")
            self._refresh_text_controls()
            return "break" if event is not None else None

        self._apply_text_changes(font_size=font_size)
        return "break" if event is not None else None

    def _toggle_text_style(self, property_name: str) -> None:
        if self.workspace is None:
            return

        text_indices = self._selected_text_indices()

        if not text_indices:
            self._save_status_text.set("Sélectionner une zone de texte")
            return

        new_value = not all(
            bool(getattr(self.workspace._objects[index], property_name))
            for index in text_indices
        )
        self._apply_text_changes(**{property_name: new_value})

    def _choose_text_color(self) -> None:
        if self.workspace is None:
            return


        text_indices = self._selected_text_indices()

        if not text_indices:
            self._save_status_text.set("Sélectionner une zone de texte")
            return

        initial_color = self.workspace._objects[text_indices[0]].text_color
        chosen_color = colorchooser.askcolor(
            color=initial_color,
            title="Couleur du texte",
            parent=self.parent.winfo_toplevel(),
        )[1]

        if not chosen_color:
            self.workspace.focus_set()
            return

        self._apply_text_changes(text_color=chosen_color)

    def _set_text_alignment(self, alignment: str) -> None:
        if alignment not in {"left", "center", "right"}:
            return

        self._apply_text_changes(align=alignment)

    def _align_selection(self, alignment: str) -> None:
        """Aligne chaque objet sélectionné individuellement sur la page."""

        if self.workspace is None:
            return

        selected_indices = self._unlocked_indices(
            sorted(self.workspace._selected_object_indices)
        )

        if not selected_indices:
            self._save_status_text.set("Aucun objet modifiable sélectionné")
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

        selected_indices = self._unlocked_indices(
            self.workspace._selected_object_indices
        )

        if len(selected_indices) < 3:
            self._save_status_text.set(
                "Sélectionner au moins trois objets déverrouillés"
            )
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

        selected_indices = self._unlocked_indices(
            self.workspace._selected_object_indices
        )

        if len(selected_indices) < 3:
            self._save_status_text.set(
                "Sélectionner au moins trois objets déverrouillés"
            )
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
                and not self.workspace._objects[index].locked
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
                and not self.workspace._objects[index].locked
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
                and not self.workspace._objects[index].locked
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
        """Modifie le remplissage des objets sélectionnés."""

        if self.workspace is None:
            return

        shape_indices = self._selected_shape_indices()

        if not shape_indices:
            self._save_status_text.set("Sélectionner au moins un objet")
            return

        initial_color = self.workspace._objects[shape_indices[0]].fill
        chosen_color = colorchooser.askcolor(
            color=initial_color,
            title="Couleur de remplissage",
            parent=self.parent.winfo_toplevel(),
        )[1]

        if not chosen_color:
            self.workspace.focus_set()
            return

        self._apply_shape_changes(
            "Remplissage modifié",
            fill=chosen_color,
        )

    def _choose_outline_color(self) -> None:
        """Modifie la couleur du contour des objets sélectionnés."""

        if self.workspace is None:
            return

        shape_indices = self._selected_shape_indices()

        if not shape_indices:
            self._save_status_text.set("Sélectionner au moins un objet")
            return

        initial_color = self.workspace._objects[shape_indices[0]].outline
        chosen_color = colorchooser.askcolor(
            color=initial_color,
            title="Couleur du contour",
            parent=self.parent.winfo_toplevel(),
        )[1]

        if not chosen_color:
            self.workspace.focus_set()
            return

        self._apply_shape_changes(
            "Contour modifié",
            outline=chosen_color,
        )

    def _change_line_width(self, value: str) -> None:
        """Modifie l'épaisseur du contour des objets sélectionnés."""

        if self._updating_shape_controls:
            return

        if value == "Sans contour":
            line_width = 0
            status_label = "Contour supprimé"
        else:
            try:
                line_width = int(value)
            except (TypeError, ValueError):
                self._save_status_text.set("Épaisseur de contour invalide")
                self._refresh_shape_controls()
                return

            if not 1 <= line_width <= 50:
                self._save_status_text.set("Épaisseur comprise entre 1 et 50")
                self._refresh_shape_controls()
                return

            status_label = "Épaisseur modifiée"

        self._apply_shape_changes(
            status_label,
            line_width=line_width,
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
            ("fill", "Remplissage", "appearance"),
            ("outline", "Couleur du contour", "appearance"),
            ("line_width", "Épaisseur du contour", "appearance"),
            ("text_color", "Couleur du texte", "text"),
            ("font_family", "Police", "text"),
            ("font_size", "Taille de police", "text"),
            ("bold", "Gras", "text"),
            ("italic", "Italique", "text"),
            ("align", "Alignement du texte", "text"),
        )

        variables: dict[str, tk.BooleanVar] = {}
        source_is_text = source.kind == "text"

        options_frame = ctk.CTkScrollableFrame(
            dialog,
            fg_color="transparent",
            height=330,
        )
        options_frame.pack(fill="both", expand=True, padx=18, pady=(0, 12))

        for property_name, label, property_group in property_choices:
            is_available = property_group == "appearance" or source_is_text
            variable = tk.BooleanVar(value=is_available)
            variables[property_name] = variable

            checkbox_text = label
            if not is_available:
                checkbox_text = f"{label} — réservé aux textes"

            checkbox = ctk.CTkCheckBox(
                options_frame,
                text=checkbox_text,
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
                and not self.workspace._objects[index].locked
            )
        ]

        if not selected_indices:
            self._save_status_text.set("Aucun objet cible sélectionné")
            return

        appearance_properties = {
            "fill",
            "outline",
            "line_width",
        }
        text_properties = {
            "text_color",
            "font_family",
            "font_size",
            "bold",
            "italic",
            "align",
        }

        self.workspace._remember_current_state()

        modified_count = 0

        for index in selected_indices:
            graphic_object = self.workspace._objects[index]

            applicable_properties = {
                name: value
                for name, value in self._copied_properties.items()
                if (
                    name in appearance_properties
                    or (
                        name in text_properties
                        and graphic_object.kind == "text"
                    )
                )
            }

            if not applicable_properties:
                continue

            self.workspace._objects[index] = replace(
                graphic_object,
                **applicable_properties,
            )
            modified_count += 1

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()

        if modified_count == 0:
            self._save_status_text.set(
                "Aucune propriété compatible avec les objets cibles"
            )
            return

        self._save_status_text.set(
            f"Propriétés appliquées à {modified_count} objet(s)"
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

        self._refresh_shape_controls()
        self._refresh_text_controls()
        self._refresh_lock_control()
        self._refresh_group_controls()
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
                        locked=bool(element.get("locked", False)),
                        group_id=(
                            int(element["group_id"])
                            if element.get("group_id") is not None
                            else None
                        ),
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
            "locked": canvas_object.locked,
            "group_id": canvas_object.group_id,
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