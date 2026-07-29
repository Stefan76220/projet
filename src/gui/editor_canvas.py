from __future__ import annotations

from dataclasses import dataclass, replace
import tkinter as tk

from customtkinter import CTkCanvas

from src.engine.camera.viewport import Viewport
from src.engine.document import Document
from src.engine.foundation import Point, Rect, Size
from src.engine.graphics import Rectangle
from src.engine.page_format import A5
from src.gui.renderer.canvas_renderer import CanvasRenderer


@dataclass(frozen=True, slots=True)
class CanvasObject:
    """Objet graphique manipulable par le canvas."""

    kind: str
    bounds: Rect
    fill: str = "#F4F4F4"
    outline: str = "#222222"
    line_width: int = 2
    text: str = "Bloc de texte"
    text_color: str = "#222222"
    font_family: str = "Arial"
    font_size: int = 12
    bold: bool = False
    italic: bool = False
    align: str = "left"


class EditorCanvas(CTkCanvas):
    """
    Canvas principal de l'éditeur.
    """

    SHADOW_OFFSET = 8
    MIN_OBJECT_SIZE_MM = 1.0
    HANDLE_SIZE_PX = 8
    HANDLE_HIT_MARGIN_PX = 6

    def __init__(
        self,
        master,
        **kwargs,
    ) -> None:

        super().__init__(
            master,
            highlightthickness=0,
            bg="#808080",
            **kwargs,
        )

        self.document = Document(
            "Page en cours",
        )

        self.document.create_page()

        self.workspace = self.document.workspace

        self.viewport = Viewport(
            self.workspace.camera,
        )

        self.viewport.add_listener(
            self.redraw,
        )

        self.renderer = CanvasRenderer(
            self,
            viewport=self.viewport,
        )

        self.page_format = A5

        self.page_left = 0.0
        self.page_top = 0.0

        self.mouse_x_px = 0.0
        self.mouse_y_px = 0.0

        self.mouse_x_mm = 0.0
        self.mouse_y_mm = 0.0

        self._mouse_listeners: list = []
        self._selection_listeners: list = []

        self._dragging = False
        self._last_x = 0
        self._last_y = 0

        self._active_tool = "selection"
        self._page_selected = False
        self._objects: list[CanvasObject] = []

        self._selected_object_index: int | None = None
        self._selected_object_indices: set[int] = set()
        self._interaction_mode: str | None = None
        self._interaction_handle: str | None = None
        self._interaction_start_mm: Point | None = None
        self._interaction_original_bounds: Rect | None = None
        self._interaction_original_bounds_by_index: dict[int, Rect] = {}

        self._drawing = False
        self._drawing_start_mm: Point | None = None
        self._preview_rectangle_id: int | None = None

        self._marquee_start_mm: Point | None = None
        self._marquee_rectangle_id: int | None = None

        self._text_editor: tk.Text | None = None
        self._text_editor_window_id: int | None = None
        self._text_edit_object_index: int | None = None
        self._text_edit_closing = False

        # Historique local du canvas. Il reste indépendant des liaisons
        # clavier existantes afin de ne jamais les neutraliser.
        self._undo_history: list[tuple[list[CanvasObject], int | None, set[int]]] = []
        self._redo_history: list[tuple[list[CanvasObject], int | None, set[int]]] = []

        self._bind_events()

    # ==========================================================
    # Initialisation
    # ==========================================================

    def _bind_events(self) -> None:

        self.bind(
            "<Configure>",
            self._on_resize,
        )

        self.bind(
            "<Motion>",
            self._mouse_move,
        )

        self.bind(
            "<ButtonPress-1>",
            self._on_left_press,
        )

        self.bind(
            "<B1-Motion>",
            self._on_left_drag,
        )

        self.bind(
            "<ButtonRelease-1>",
            self._on_left_release,
        )

        self.bind(
            "<Double-Button-1>",
            self._on_text_double_click,
        )

        self.bind(
            "<ButtonPress-2>",
            self._start_pan,
        )

        self.bind(
            "<B2-Motion>",
            self._pan,
        )

        self.bind(
            "<ButtonRelease-2>",
            self._stop_pan,
        )

        self.bind(
            "<MouseWheel>",
            self._on_mousewheel,
        )

        self.focus_set()

        self.bind(
            "<Control-0>",
            self._fit_page,
        )

        self.bind(
            "<Key-r>",
            self._activate_rectangle_tool,
        )

        self.bind(
            "<Key-R>",
            self._activate_rectangle_tool,
        )

        self.bind(
            "<Key-e>",
            self._activate_ellipse_tool,
        )

        self.bind(
            "<Key-E>",
            self._activate_ellipse_tool,
        )

        self.bind(
            "<Key-t>",
            self._activate_text_tool,
        )

        self.bind(
            "<Key-T>",
            self._activate_text_tool,
        )

        self.bind(
            "<Escape>",
            self._activate_selection_tool,
        )

        self.bind(
            "<Left>",
            self._move_selection_with_keyboard,
        )
        self.bind(
            "<Right>",
            self._move_selection_with_keyboard,
        )
        self.bind(
            "<Up>",
            self._move_selection_with_keyboard,
        )
        self.bind(
            "<Down>",
            self._move_selection_with_keyboard,
        )

        self.bind(
            "<Control-d>",
            self._duplicate_selection,
        )
        self.bind(
            "<Control-D>",
            self._duplicate_selection,
        )
        self.bind(
            "<Delete>",
            self._delete_selection,
        )
        self.bind(
            "<BackSpace>",
            self._delete_selection,
        )
        self.bind(
            "<Control-z>",
            self._undo_last_action,
        )
        self.bind(
            "<Control-Z>",
            self._undo_last_action,
        )
        self.bind(
            "<Control-y>",
            self._redo_last_action,
        )
        self.bind(
            "<Control-Y>",
            self._redo_last_action,
        )

        self.bind_all(
            "<Control-a>",
            self._select_all_objects,
            add="+",
        )
        self.bind_all(
            "<Control-A>",
            self._select_all_objects,
            add="+",
        )

    def _snapshot_state(
        self,
    ) -> tuple[list[CanvasObject], int | None, set[int]]:

        return (
            list(self._objects),
            self._selected_object_index,
            set(self._selected_object_indices),
        )

    def _restore_state(
        self,
        state: tuple[list[CanvasObject], int | None, set[int]],
    ) -> None:

        objects, selected_index, selected_indices = state
        self._objects = list(objects)
        self._selected_object_index = selected_index
        self._selected_object_indices = {
            index
            for index in selected_indices
            if 0 <= index < len(self._objects)
        }
        if self._selected_object_index not in self._selected_object_indices:
            self._selected_object_index = (
                max(self._selected_object_indices)
                if self._selected_object_indices
                else None
            )
        self.redraw()
        self._notify_selection()

    def _remember_current_state(self) -> None:

        self._undo_history.append(
            self._snapshot_state(),
        )
        self._redo_history.clear()

    def _undo_last_action(
        self,
        event=None,
    ) -> str:

        if self._undo_history:
            self._redo_history.append(
                self._snapshot_state(),
            )
            self._restore_state(
                self._undo_history.pop(),
            )

        return "break"

    def _redo_last_action(
        self,
        event=None,
    ) -> str:

        if self._redo_history:
            self._undo_history.append(
                self._snapshot_state(),
            )
            self._restore_state(
                self._redo_history.pop(),
            )

        return "break"

    def _duplicate_selection(
        self,
        event=None,
    ) -> str | None:

        selected_object = self.get_selected_object()

        if selected_object is None:
            return None

        offset = 5.0
        bounds = selected_object.bounds
        new_x = min(
            bounds.left + offset,
            self.page_format.width_mm - bounds.width,
        )
        new_y = min(
            bounds.top + offset,
            self.page_format.height_mm - bounds.height,
        )

        duplicate = replace(
            selected_object,
            bounds=Rect(
                Point(new_x, new_y),
                bounds.size,
            ),
        )

        self._remember_current_state()
        self._objects.append(duplicate)
        self._selected_object_index = len(self._objects) - 1
        self._selected_object_indices = {self._selected_object_index}
        self.redraw()
        self._notify_selection()

        return "break"

    def _delete_selection(
        self,
        event=None,
    ) -> str | None:

        if self._selected_object_index is None:
            return None

        if not 0 <= self._selected_object_index < len(self._objects):
            return None

        self._remember_current_state()
        deleted_index = self._selected_object_index
        del self._objects[deleted_index]
        self._selected_object_indices = {
            index - 1 if index > deleted_index else index
            for index in self._selected_object_indices
            if index != deleted_index
        }
        self._selected_object_index = (
            max(self._selected_object_indices)
            if self._selected_object_indices
            else None
        )
        self.redraw()
        self._notify_selection()

        return "break"

    def _move_selection_with_keyboard(
        self,
        event,
    ) -> str | None:

        selected_indices = sorted(self._selected_object_indices)

        if not selected_indices:
            return None

        step = 10.0 if event.state & 0x0001 else 1.0
        dx = 0.0
        dy = 0.0

        if event.keysym == "Left":
            dx = -step
        elif event.keysym == "Right":
            dx = step
        elif event.keysym == "Up":
            dy = -step
        elif event.keysym == "Down":
            dy = step
        else:
            return None

        selected_bounds = [
            self._objects[index].bounds
            for index in selected_indices
            if 0 <= index < len(self._objects)
        ]

        if not selected_bounds:
            return None

        min_left = min(bounds.left for bounds in selected_bounds)
        min_top = min(bounds.top for bounds in selected_bounds)
        max_right = max(bounds.right for bounds in selected_bounds)
        max_bottom = max(bounds.bottom for bounds in selected_bounds)

        dx = min(max(dx, -min_left), self.page_format.width_mm - max_right)
        dy = min(max(dy, -min_top), self.page_format.height_mm - max_bottom)

        if dx == 0.0 and dy == 0.0:
            return "break"

        self._remember_current_state()

        for index in selected_indices:
            if not 0 <= index < len(self._objects):
                continue

            graphic_object = self._objects[index]
            bounds = graphic_object.bounds
            self._objects[index] = replace(
                graphic_object,
                bounds=Rect(
                    Point(bounds.left + dx, bounds.top + dy),
                    bounds.size,
                ),
            )

        self.redraw()
        self._notify_selection()

        return "break"

    # ==========================================================
    # Observateurs
    # ==========================================================

    def add_mouse_listener(
        self,
        callback,
    ) -> None:

        if callback not in self._mouse_listeners:
            self._mouse_listeners.append(
                callback,
            )

    def _notify_mouse(self) -> None:

        for callback in self._mouse_listeners:
            callback()

    def add_selection_listener(self, callback) -> None:

        if callback not in self._selection_listeners:
            self._selection_listeners.append(callback)

    def _notify_selection(self) -> None:

        # La notification est exécutée après la fin complète de l'événement
        # souris. Cela évite de rafraîchir le panneau pendant que Tk traite
        # encore le clic sur le canvas.
        self.after_idle(self._dispatch_selection_changed)

    def _dispatch_selection_changed(self) -> None:

        selected = self.get_selected_object()

        for callback in tuple(self._selection_listeners):
            callback(selected)

        self.event_generate(
            "<<SelectionChanged>>",
            when="tail",
        )

    def get_selected_object(self) -> CanvasObject | None:

        if self._selected_object_index is None:
            return None
        if not 0 <= self._selected_object_index < len(self._objects):
            return None
        return self._objects[self._selected_object_index]

    def get_selected_objects(self) -> list[CanvasObject]:

        return [
            self._objects[index]
            for index in sorted(self._selected_object_indices)
            if 0 <= index < len(self._objects)
        ]

    def update_selected_object(self, **changes) -> None:

        if self._selected_object_index is None:
            return
        if not 0 <= self._selected_object_index < len(self._objects):
            return

        current = self._objects[self._selected_object_index]
        self._objects[self._selected_object_index] = replace(current, **changes)
        self.redraw()
        self._notify_selection()

    def update_selected_bounds(
        self,
        *,
        x: float,
        y: float,
        width: float,
        height: float,
    ) -> None:

        if self._selected_object_index is None:
            return

        width = max(self.MIN_OBJECT_SIZE_MM, min(width, self.page_format.width_mm))
        height = max(self.MIN_OBJECT_SIZE_MM, min(height, self.page_format.height_mm))
        x = max(0.0, min(x, self.page_format.width_mm - width))
        y = max(0.0, min(y, self.page_format.height_mm - height))

        self.update_selected_object(
            bounds=Rect(Point(x, y), Size(width, height)),
        )

    # ==========================================================
    # Configuration
    # ==========================================================

    def set_page_format(
        self,
        page_format,
    ) -> None:

        self.page_format = page_format
        self.redraw()

    def set_tool(
        self,
        tool_name: str,
    ) -> None:

        normalized_name = str(tool_name).strip().lower()

        if normalized_name not in {
            "selection",
            "rectangle",
            "ellipse",
            "text",
        }:
            normalized_name = "selection"

        self._active_tool = normalized_name
        self._cancel_drawing()

        cursor = (
            "crosshair"
            if self._active_tool in {"rectangle", "ellipse", "text"}
            else "arrow"
        )

        self.configure(
            cursor=cursor,
        )

    @property
    def active_tool(self) -> str:
        return self._active_tool

    # ==========================================================
    # Dessin
    # ==========================================================

    def redraw(self) -> None:

        self.delete(
            "all",
        )

        page_width = self.viewport.mm_to_px(
            self.page_format.width_mm,
        )

        page_height = self.viewport.mm_to_px(
            self.page_format.height_mm,
        )

        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()

        self.page_left = (
            (canvas_width - page_width) / 2
            + self.viewport.offset_x_px
        )

        self.page_top = (
            (canvas_height - page_height) / 2
            + self.viewport.offset_y_px
        )

        self.renderer.set_origin(
            self.page_left,
            self.page_top,
        )

        self._draw_shadow(
            page_width,
            page_height,
        )

        self._draw_page(
            page_width,
            page_height,
        )

        self._draw_workspace()
        self._draw_objects()
        self._position_text_editor()

    def _draw_shadow(
        self,
        width: float,
        height: float,
    ) -> None:

        self.create_rectangle(
            self.page_left + self.SHADOW_OFFSET,
            self.page_top + self.SHADOW_OFFSET,
            self.page_left + width + self.SHADOW_OFFSET,
            self.page_top + height + self.SHADOW_OFFSET,
            fill="#666666",
            width=0,
        )

    def _draw_page(
        self,
        width: float,
        height: float,
    ) -> None:

        self.create_rectangle(
            self.page_left,
            self.page_top,
            self.page_left + width,
            self.page_top + height,
            fill="white",
            outline="#3874CB" if self._page_selected else "#BBBBBB",
            width=2 if self._page_selected else 1,
        )

    def _draw_workspace(self) -> None:

        for page in self.workspace.document:

            self.renderer.draw_page(
                page,
            )

            for layer in page:

                for drawable in layer:

                    self.renderer.draw_drawable(
                        drawable,
                    )

    def _draw_objects(self) -> None:

        for index, graphic_object in enumerate(self._objects):

            bounds = graphic_object.bounds
            selected = index in self._selected_object_indices

            coordinates = (
                self.page_left + self.viewport.mm_to_px(bounds.left),
                self.page_top + self.viewport.mm_to_px(bounds.top),
                self.page_left + self.viewport.mm_to_px(bounds.right),
                self.page_top + self.viewport.mm_to_px(bounds.bottom),
            )

            options = {
                "fill": graphic_object.fill,
                "outline": "#3874CB" if selected else graphic_object.outline,
                "width": graphic_object.line_width,
            }

            if graphic_object.kind == "ellipse":
                self.create_oval(
                    *coordinates,
                    **options,
                )
            else:
                self.create_rectangle(
                    *coordinates,
                    **options,
                )

            if graphic_object.kind == "text":
                padding = 6
                text_width = max(1, coordinates[2] - coordinates[0] - (padding * 2))
                font_style = []
                if graphic_object.bold:
                    font_style.append("bold")
                if graphic_object.italic:
                    font_style.append("italic")
                anchor_by_align = {
                    "left": "nw",
                    "center": "n",
                    "right": "ne",
                }
                x_by_align = {
                    "left": coordinates[0] + padding,
                    "center": (coordinates[0] + coordinates[2]) / 2,
                    "right": coordinates[2] - padding,
                }
                self.create_text(
                    x_by_align.get(graphic_object.align, coordinates[0] + padding),
                    coordinates[1] + padding,
                    anchor=anchor_by_align.get(graphic_object.align, "nw"),
                    justify=graphic_object.align if graphic_object.align in {"left", "center", "right"} else "left",
                    text=graphic_object.text,
                    width=text_width,
                    fill=graphic_object.text_color,
                    font=(
                        graphic_object.font_family,
                        graphic_object.font_size,
                        " ".join(font_style),
                    ),
                )

            if selected and index == self._selected_object_index:
                self._draw_selection_handles(bounds)

    def _draw_selection_handles(self, bounds: Rect) -> None:

        for x_px, y_px in self._selection_handle_positions(bounds).values():

            half = self.HANDLE_SIZE_PX / 2

            self.create_rectangle(
                x_px - half,
                y_px - half,
                x_px + half,
                y_px + half,
                fill="white",
                outline="#3874CB",
                width=2,
            )

    def _selection_handle_positions(
        self,
        bounds: Rect,
    ) -> dict[str, tuple[float, float]]:

        left = self.page_left + self.viewport.mm_to_px(bounds.left)
        top = self.page_top + self.viewport.mm_to_px(bounds.top)
        right = self.page_left + self.viewport.mm_to_px(bounds.right)
        bottom = self.page_top + self.viewport.mm_to_px(bounds.bottom)

        center_x = (left + right) / 2
        center_y = (top + bottom) / 2

        return {
            "nw": (left, top),
            "n": (center_x, top),
            "ne": (right, top),
            "e": (right, center_y),
            "se": (right, bottom),
            "s": (center_x, bottom),
            "sw": (left, bottom),
            "w": (left, center_y),
        }

    # ==========================================================
    # Outils graphiques
    # ==========================================================

    def _activate_rectangle_tool(
        self,
        event=None,
    ) -> str:

        self.set_tool(
            "rectangle",
        )

        return "break"

    def _activate_ellipse_tool(
        self,
        event=None,
    ) -> str:

        self.set_tool(
            "ellipse",
        )

        return "break"

    def _select_all_objects(
        self,
        event=None,
    ) -> str:

        if self._text_editor is not None:
            return ""

        if not self._objects:
            return "break"

        self.set_tool(
            "selection",
        )

        self._selected_object_indices = set(range(len(self._objects)))
        self._selected_object_index = len(self._objects) - 1
        self._page_selected = False
        self._interaction_mode = None
        self._interaction_handle = None
        self._interaction_start_mm = None
        self._interaction_original_bounds = None
        self._interaction_original_bounds_by_index = {}

        self._notify_selection()
        self.redraw()
        self.focus_set()

        return "break"

    def _activate_text_tool(
        self,
        event=None,
    ) -> str:

        self.set_tool(
            "text",
        )

        return "break"

    def _activate_selection_tool(
        self,
        event=None,
    ) -> str:

        self.set_tool(
            "selection",
        )

        self._selected_object_index = None
        self._selected_object_indices.clear()
        self._interaction_mode = None
        self._interaction_handle = None
        self._interaction_start_mm = None
        self._interaction_original_bounds = None
        self._interaction_original_bounds_by_index = {}

        self._notify_selection()
        self.redraw()

        return "break"

    def _on_text_double_click(
        self,
        event,
    ) -> str | None:

        point = self._event_to_page_mm(
            event,
        )

        object_index = self._hit_test_object(
            point,
        )

        if object_index is None:
            return None

        if self._objects[object_index].kind != "text":
            return None

        self._selected_object_index = object_index
        self._selected_object_indices = {object_index}
        self._start_text_editing(
            object_index,
        )

        return "break"

    def _start_text_editing(
        self,
        object_index: int,
    ) -> None:

        self.commit_active_text_edit()

        if not 0 <= object_index < len(self._objects):
            return

        graphic_object = self._objects[object_index]

        if graphic_object.kind != "text":
            return

        self._text_edit_object_index = object_index
        self._text_editor = tk.Text(
            self,
            wrap="word",
            undo=True,
            relief="solid",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground="#3874CB",
            highlightcolor="#3874CB",
            background=graphic_object.fill,
            foreground=graphic_object.text_color,
            insertbackground=graphic_object.text_color,
            font=(
                graphic_object.font_family,
                graphic_object.font_size,
                " ".join(
                    style
                    for style, enabled in (
                        ("bold", graphic_object.bold),
                        ("italic", graphic_object.italic),
                    )
                    if enabled
                ),
            ),
            padx=5,
            pady=4,
        )

        self._text_editor.insert(
            "1.0",
            graphic_object.text,
        )

        self._text_editor.bind(
            "<Return>",
            self._validate_text_edit,
        )
        self._text_editor.bind(
            "<Escape>",
            self._cancel_text_edit,
        )
        self._text_editor.bind(
            "<FocusOut>",
            self._validate_text_edit,
        )

        self.redraw()
        self._text_editor.focus_set()
        self._text_editor.tag_add(
            "sel",
            "1.0",
            "end-1c",
        )

    def _position_text_editor(self) -> None:

        if self._text_editor is None:
            return

        object_index = self._text_edit_object_index

        if object_index is None or not 0 <= object_index < len(self._objects):
            self._finish_text_editing(
                commit=False,
                redraw=False,
            )
            return

        bounds = self._objects[object_index].bounds
        left = self.page_left + self.viewport.mm_to_px(bounds.left)
        top = self.page_top + self.viewport.mm_to_px(bounds.top)
        width = max(30, self.viewport.mm_to_px(bounds.width))
        height = max(24, self.viewport.mm_to_px(bounds.height))

        self._text_editor_window_id = self.create_window(
            left,
            top,
            anchor="nw",
            window=self._text_editor,
            width=width,
            height=height,
        )

    def _validate_text_edit(
        self,
        event=None,
    ) -> str:

        self._finish_text_editing(
            commit=True,
        )
        return "break"

    def _cancel_text_edit(
        self,
        event=None,
    ) -> str:

        self._finish_text_editing(
            commit=False,
        )
        return "break"

    def _finish_text_editing(
        self,
        commit: bool,
        redraw: bool = True,
    ) -> None:

        if self._text_edit_closing:
            return

        if self._text_editor is None:
            return

        self._text_edit_closing = True

        editor = self._text_editor
        object_index = self._text_edit_object_index

        if (
            commit
            and object_index is not None
            and 0 <= object_index < len(self._objects)
        ):
            edited_text = editor.get(
                "1.0",
                "end-1c",
            )
            self._objects[object_index] = replace(
                self._objects[object_index],
                text=edited_text,
            )
            self._notify_selection()

        if self._text_editor_window_id is not None:
            self.delete(
                self._text_editor_window_id,
            )

        editor.destroy()
        self._text_editor = None
        self._text_editor_window_id = None
        self._text_edit_object_index = None
        self._text_edit_closing = False

        self.focus_set()

        if redraw:
            self.redraw()

    def commit_active_text_edit(self) -> None:

        self._finish_text_editing(
            commit=True,
        )

    def _on_left_press(
        self,
        event,
    ) -> None:

        self.focus_set()

        start = self._event_to_page_mm(
            event,
        )

        self._page_selected = start is not None

        if self._active_tool in {"rectangle", "ellipse", "text"}:

            if start is None:
                return

            self._selected_object_index = None
            self._selected_object_indices.clear()
            self._drawing = True
            self._drawing_start_mm = start

            preview_method = (
                self.create_oval
                if self._active_tool == "ellipse"
                else self.create_rectangle
            )

            self._preview_rectangle_id = preview_method(
                event.x,
                event.y,
                event.x,
                event.y,
                outline="#3874CB",
                width=2,
                dash=(5, 3),
            )
            return

        handle = self._hit_test_handle(
            event.x,
            event.y,
        )

        if handle is not None and self._selected_object_index is not None:

            self._interaction_mode = "resize"
            self._interaction_handle = handle
            self._interaction_start_mm = self._event_to_page_mm(
                event,
                clamp_to_page=True,
            )
            self._interaction_original_bounds = self._objects[
                self._selected_object_index
            ].bounds
            return

        object_index = self._hit_test_object(
            start,
        )

        control_pressed = bool(event.state & 0x0004)

        if control_pressed:
            if object_index is not None:
                if object_index in self._selected_object_indices:
                    self._selected_object_indices.remove(object_index)
                    if self._selected_object_index == object_index:
                        self._selected_object_index = (
                            max(self._selected_object_indices)
                            if self._selected_object_indices
                            else None
                        )
                else:
                    self._selected_object_indices.add(object_index)
                    self._selected_object_index = object_index

            self._interaction_mode = None
            self._interaction_start_mm = None
            self._interaction_original_bounds = None

        else:
            if (
                object_index is not None
                and object_index in self._selected_object_indices
                and len(self._selected_object_indices) > 1
            ):
                self._selected_object_index = object_index
            else:
                self._selected_object_index = object_index
                self._selected_object_indices = (
                    {object_index}
                    if object_index is not None
                    else set()
                )

            if object_index is not None and start is not None:

                self._interaction_mode = "move"
                self._interaction_start_mm = start
                self._interaction_original_bounds = self._objects[
                    object_index
                ].bounds
                self._interaction_original_bounds_by_index = {
                    index: self._objects[index].bounds
                    for index in self._selected_object_indices
                    if 0 <= index < len(self._objects)
                }

            else:

                self._interaction_mode = "marquee"
                self._interaction_start_mm = start
                self._interaction_original_bounds = None
                self._interaction_original_bounds_by_index = {}
                self._marquee_start_mm = start
                self._marquee_rectangle_id = self.create_rectangle(
                    event.x,
                    event.y,
                    event.x,
                    event.y,
                    outline="#3874CB",
                    width=1,
                    dash=(4, 3),
                    fill="",
                )

        self.redraw()
        if self._interaction_mode == "marquee" and self._marquee_start_mm is not None:
            start_x = self.page_left + self.viewport.mm_to_px(self._marquee_start_mm.x)
            start_y = self.page_top + self.viewport.mm_to_px(self._marquee_start_mm.y)
            self._marquee_rectangle_id = self.create_rectangle(
                start_x,
                start_y,
                start_x,
                start_y,
                outline="#3874CB",
                width=1,
                dash=(4, 3),
                fill="",
            )
        self._notify_selection()

    def _on_left_drag(
        self,
        event,
    ) -> None:

        if self._drawing:

            if self._preview_rectangle_id is None:
                return

            if self._drawing_start_mm is None:
                return

            current = self._event_to_page_mm(
                event,
                clamp_to_page=True,
            )

            if current is None:
                return

            start_x = (
                self.page_left
                + self.viewport.mm_to_px(
                    self._drawing_start_mm.x,
                )
            )

            start_y = (
                self.page_top
                + self.viewport.mm_to_px(
                    self._drawing_start_mm.y,
                )
            )

            current_x = (
                self.page_left
                + self.viewport.mm_to_px(
                    current.x,
                )
            )

            current_y = (
                self.page_top
                + self.viewport.mm_to_px(
                    current.y,
                )
            )

            self.coords(
                self._preview_rectangle_id,
                start_x,
                start_y,
                current_x,
                current_y,
            )
            return

        if self._interaction_mode == "marquee":
            if self._marquee_start_mm is None or self._marquee_rectangle_id is None:
                return

            current = self._event_to_page_mm(
                event,
                clamp_to_page=True,
            )
            if current is None:
                return

            start_x = self.page_left + self.viewport.mm_to_px(self._marquee_start_mm.x)
            start_y = self.page_top + self.viewport.mm_to_px(self._marquee_start_mm.y)
            current_x = self.page_left + self.viewport.mm_to_px(current.x)
            current_y = self.page_top + self.viewport.mm_to_px(current.y)
            self.coords(
                self._marquee_rectangle_id,
                start_x,
                start_y,
                current_x,
                current_y,
            )
            return

        if self._selected_object_index is None:
            return

        if self._interaction_start_mm is None:
            return

        if self._interaction_original_bounds is None:
            return

        current = self._event_to_page_mm(
            event,
            clamp_to_page=True,
        )

        if current is None:
            return

        if self._interaction_mode == "move":
            self._move_selected_object(current)

        elif self._interaction_mode == "resize":
            self._resize_selected_object(current)

    def _on_left_release(
        self,
        event,
    ) -> None:

        if self._drawing:

            start = self._drawing_start_mm

            current = self._event_to_page_mm(
                event,
                clamp_to_page=True,
            )

            self._cancel_preview()

            if start is None or current is None:
                self._finish_drawing()
                return

            left = min(
                start.x,
                current.x,
            )

            top = min(
                start.y,
                current.y,
            )

            width = abs(
                current.x - start.x,
            )

            height = abs(
                current.y - start.y,
            )

            if (
                width < self.MIN_OBJECT_SIZE_MM
                or height < self.MIN_OBJECT_SIZE_MM
            ):
                self._finish_drawing()
                return

            bounds = Rect(
                Point(
                    left,
                    top,
                ),
                Size(
                    width,
                    height,
                ),
            )

            graphic_object = CanvasObject(
                kind=self._active_tool,
                bounds=bounds,
            )

            self._objects.append(
                graphic_object,
            )

            self._selected_object_index = (
                len(self._objects) - 1
            )
            self._selected_object_indices = {self._selected_object_index}

            self._finish_drawing()
            self.set_tool(
                "selection",
            )
            self.redraw()
            self._notify_selection()
            return

        if self._interaction_mode == "marquee":
            start = self._marquee_start_mm
            current = self._event_to_page_mm(
                event,
                clamp_to_page=True,
            )

            if self._marquee_rectangle_id is not None:
                self.delete(self._marquee_rectangle_id)

            self._marquee_rectangle_id = None
            self._marquee_start_mm = None

            if start is not None and current is not None:
                left = min(start.x, current.x)
                top = min(start.y, current.y)
                right = max(start.x, current.x)
                bottom = max(start.y, current.y)

                if abs(right - left) >= 0.5 or abs(bottom - top) >= 0.5:
                    selected = {
                        index
                        for index, graphic_object in enumerate(self._objects)
                        if not (
                            graphic_object.bounds.right < left
                            or graphic_object.bounds.left > right
                            or graphic_object.bounds.bottom < top
                            or graphic_object.bounds.top > bottom
                        )
                    }
                    self._selected_object_indices = selected
                    self._selected_object_index = max(selected) if selected else None

            self.redraw()
            self._notify_selection()

        self._interaction_mode = None
        self._interaction_handle = None
        self._interaction_start_mm = None
        self._interaction_original_bounds = None
        self._interaction_original_bounds_by_index = {}

    def _hit_test_object(
        self,
        point: Point | None,
    ) -> int | None:

        if point is None:
            return None

        for index in range(
            len(self._objects) - 1,
            -1,
            -1,
        ):

            if self._objects[index].bounds.contains(point):
                return index

        return None

    def _hit_test_handle(
        self,
        x_px: float,
        y_px: float,
    ) -> str | None:

        if self._selected_object_index is None:
            return None

        bounds = self._objects[
            self._selected_object_index
        ].bounds

        margin = (
            self.HANDLE_SIZE_PX / 2
            + self.HANDLE_HIT_MARGIN_PX
        )

        for name, (handle_x, handle_y) in (
            self._selection_handle_positions(bounds).items()
        ):

            if (
                abs(x_px - handle_x) <= margin
                and abs(y_px - handle_y) <= margin
            ):
                return name

        return None

    def _move_selected_object(
        self,
        current: Point,
    ) -> None:

        if self._selected_object_index is None:
            return

        if self._interaction_start_mm is None:
            return

        original_bounds = self._interaction_original_bounds_by_index

        if not original_bounds:
            return

        dx = current.x - self._interaction_start_mm.x
        dy = current.y - self._interaction_start_mm.y

        min_left = min(bounds.left for bounds in original_bounds.values())
        min_top = min(bounds.top for bounds in original_bounds.values())
        max_right = max(bounds.right for bounds in original_bounds.values())
        max_bottom = max(bounds.bottom for bounds in original_bounds.values())

        dx = min(max(dx, -min_left), self.page_format.width_mm - max_right)
        dy = min(max(dy, -min_top), self.page_format.height_mm - max_bottom)

        for index, original in original_bounds.items():
            if not 0 <= index < len(self._objects):
                continue

            graphic_object = self._objects[index]
            self._objects[index] = replace(
                graphic_object,
                bounds=Rect(
                    Point(original.left + dx, original.top + dy),
                    original.size,
                ),
            )

        self.redraw()
        self._notify_selection()

    def _resize_selected_object(
        self,
        current: Point,
    ) -> None:

        if self._selected_object_index is None:
            return

        if self._interaction_original_bounds is None:
            return

        if self._interaction_handle is None:
            return

        original = self._interaction_original_bounds
        handle = self._interaction_handle

        left = original.left
        top = original.top
        right = original.right
        bottom = original.bottom

        if "w" in handle:
            left = min(
                current.x,
                right - self.MIN_OBJECT_SIZE_MM,
            )

        if "e" in handle:
            right = max(
                current.x,
                left + self.MIN_OBJECT_SIZE_MM,
            )

        if "n" in handle:
            top = min(
                current.y,
                bottom - self.MIN_OBJECT_SIZE_MM,
            )

        if "s" in handle:
            bottom = max(
                current.y,
                top + self.MIN_OBJECT_SIZE_MM,
            )

        left = max(
            0.0,
            left,
        )

        top = max(
            0.0,
            top,
        )

        right = min(
            self.page_format.width_mm,
            right,
        )

        bottom = min(
            self.page_format.height_mm,
            bottom,
        )

        selected_object = self._objects[
            self._selected_object_index
        ]

        self._objects[
            self._selected_object_index
        ] = replace(
            selected_object,
            bounds=Rect(
                Point(
                    left,
                    top,
                ),
                Size(
                    right - left,
                    bottom - top,
                ),
            ),
        )

        self.redraw()
        self._notify_selection()

    def _event_to_page_mm(
        self,
        event,
        clamp_to_page: bool = False,
    ) -> Point | None:

        x_mm = self.viewport.px_to_mm(
            event.x - self.page_left,
        )

        y_mm = self.viewport.px_to_mm(
            event.y - self.page_top,
        )

        if clamp_to_page:
            x_mm = min(
                max(
                    x_mm,
                    0.0,
                ),
                self.page_format.width_mm,
            )

            y_mm = min(
                max(
                    y_mm,
                    0.0,
                ),
                self.page_format.height_mm,
            )

        elif not (
            0.0 <= x_mm <= self.page_format.width_mm
            and 0.0 <= y_mm <= self.page_format.height_mm
        ):
            return None

        return Point(
            x_mm,
            y_mm,
        )

    def _cancel_preview(self) -> None:

        if self._preview_rectangle_id is not None:

            self.delete(
                self._preview_rectangle_id,
            )

            self._preview_rectangle_id = None

    def _finish_drawing(self) -> None:

        self._drawing = False
        self._drawing_start_mm = None

    def _cancel_drawing(self) -> None:

        self._cancel_preview()
        self._finish_drawing()

    # ==========================================================
    # Évènements
    # ==========================================================

    def _on_resize(
        self,
        event,
    ) -> None:

        self.redraw()

    def _mouse_move(
        self,
        event,
    ) -> None:

        self.mouse_x_px = event.x
        self.mouse_y_px = event.y

        self.mouse_x_mm = self.viewport.px_to_mm(
            event.x - self.page_left,
        )

        self.mouse_y_mm = self.viewport.px_to_mm(
            event.y - self.page_top,
        )

        self._notify_mouse()

    def _start_pan(
        self,
        event,
    ) -> None:

        self._dragging = True

        self._last_x = event.x
        self._last_y = event.y

    def _pan(
        self,
        event,
    ) -> None:

        if not self._dragging:
            return

        dx = event.x - self._last_x
        dy = event.y - self._last_y

        self.viewport.move(
            dx,
            dy,
        )

        self._last_x = event.x
        self._last_y = event.y

    def _stop_pan(
        self,
        event,
    ) -> None:

        self._dragging = False

    def _on_mousewheel(
        self,
        event,
    ) -> None:

        factor = 1.1 if event.delta > 0 else 0.9

        old_x = self.viewport.px_to_mm(
            event.x - self.page_left,
        )

        old_y = self.viewport.px_to_mm(
            event.y - self.page_top,
        )

        self.viewport.zoom_at(
            factor,
        )

        new_page_x = (
            event.x
            - self.viewport.mm_to_px(
                old_x,
            )
        )

        new_page_y = (
            event.y
            - self.viewport.mm_to_px(
                old_y,
            )
        )

        canvas_width = self.winfo_width()
        canvas_height = self.winfo_height()

        page_width = self.viewport.mm_to_px(
            self.page_format.width_mm,
        )

        page_height = self.viewport.mm_to_px(
            self.page_format.height_mm,
        )

        self.viewport.set_offset(
            new_page_x
            - (canvas_width - page_width) / 2,
            new_page_y
            - (canvas_height - page_height) / 2,
        )

    def _fit_page(
        self,
        event=None,
    ) -> None:

        width = self.winfo_width()
        height = self.winfo_height()

        if width <= 0 or height <= 0:
            return

        base = self.viewport.pixels_per_mm

        zoom_x = (
            width * 0.85
        ) / (
            self.page_format.width_mm * base
        )

        zoom_y = (
            height * 0.85
        ) / (
            self.page_format.height_mm * base
        )

        self.viewport.set_zoom(
            min(
                zoom_x,
                zoom_y,
            )
        )

        self.viewport.set_offset(
            0,
            0,
        )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            "EditorCanvas("
            f"tool={self._active_tool!r})"
        )