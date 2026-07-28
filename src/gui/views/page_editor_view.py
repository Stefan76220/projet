from __future__ import annotations

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
        }

    def _save_page_objects(self) -> None:

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