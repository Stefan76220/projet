from __future__ import annotations

from dataclasses import replace
import tkinter as tk

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
            height=48,
            corner_radius=0,
        )
        toolbar.pack(
            fill="x",
            padx=20,
            pady=(0, 10),
        )
        toolbar.pack_propagate(False)

        ctk.CTkLabel(
            toolbar,
            text="Alignement",
            font=Fonts.NORMAL,
            text_color=Colors.TEXT,
        ).pack(side="left", padx=(12, 8))

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
                toolbar,
                text=label,
                width=88,
                height=30,
                command=lambda value=alignment: self._align_selection(value),
            ).pack(side="left", padx=3, pady=9)

    def _align_selection(self, alignment: str) -> None:
        """Aligne la sélection sur la page en conservant les écarts entre objets."""

        if self.workspace is None:
            return

        selected_indices = [
            index
            for index in sorted(self.workspace._selected_object_indices)
            if 0 <= index < len(self.workspace._objects)
        ]

        if not selected_indices:
            return

        selected_objects = [
            self.workspace._objects[index]
            for index in selected_indices
        ]

        group_left = min(obj.bounds.left for obj in selected_objects)
        group_top = min(obj.bounds.top for obj in selected_objects)
        group_right = max(obj.bounds.right for obj in selected_objects)
        group_bottom = max(obj.bounds.bottom for obj in selected_objects)
        group_width = group_right - group_left
        group_height = group_bottom - group_top

        page_width = self.workspace.page_format.width_mm
        page_height = self.workspace.page_format.height_mm

        target_left = group_left
        target_top = group_top

        if alignment == "left":
            target_left = 0.0
        elif alignment == "center_horizontal":
            target_left = (page_width - group_width) / 2
        elif alignment == "right":
            target_left = page_width - group_width
        elif alignment == "top":
            target_top = 0.0
        elif alignment == "center_vertical":
            target_top = (page_height - group_height) / 2
        elif alignment == "bottom":
            target_top = page_height - group_height
        else:
            return

        delta_x = target_left - group_left
        delta_y = target_top - group_top

        self.workspace._remember_current_state()

        for index in selected_indices:
            graphic_object = self.workspace._objects[index]
            bounds = graphic_object.bounds
            self.workspace._objects[index] = replace(
                graphic_object,
                bounds=Rect(
                    Point(
                        bounds.left + delta_x,
                        bounds.top + delta_y,
                    ),
                    bounds.size,
                ),
            )

        self.workspace.redraw()
        self.workspace._notify_selection()
        self.workspace.focus_set()

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