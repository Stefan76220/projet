from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, replace
from math import atan2, cos, degrees, pi, radians, sin
from pathlib import Path
import tkinter as tk
from typing import Any, Callable

from customtkinter import CTkCanvas
from PIL import Image, ImageDraw, ImageOps, ImageTk

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
    content_type: str = ""
    content_mode: str = "variable"
    content_label: str = ""
    image_path: str = ""
    image_fit: str = "cover"
    image_zoom: float = 1.0
    image_focus_x: float = 0.5
    image_focus_y: float = 0.5
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
    rotation: float = 0.0
    locked: bool = False
    group_id: int | None = None


class EditorCanvas(CTkCanvas):
    """
    Canvas principal de l'éditeur.
    """

    SHADOW_OFFSET = 8
    MIN_OBJECT_SIZE_MM = 1.0
    HANDLE_SIZE_PX = 8
    HANDLE_HIT_MARGIN_PX = 6
    ROTATION_HANDLE_DISTANCE_PX = 28
    ROTATION_HANDLE_RADIUS_PX = 6
    ELLIPSE_SEGMENTS = 64

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
        self._space_pan_active = False
        self._left_pan_active = False

        self._active_tool = "selection"
        self._page_selected = False
        self._objects: list[CanvasObject] = []

        self._selected_object_index: int | None = None
        self._selected_object_indices: set[int] = set()
        self._reference_object_index: int | None = None
        self._interaction_mode: str | None = None
        self._interaction_handle: str | None = None
        self._interaction_start_mm: Point | None = None
        self._interaction_original_bounds: Rect | None = None
        self._interaction_original_bounds_by_index: dict[int, Rect] = {}
        self._interaction_original_rotations_by_index: dict[int, float] = {}
        self._interaction_original_centers_by_index: dict[int, Point] = {}
        self._interaction_rotation_pivot: Point | None = None
        self._interaction_start_angle_deg: float | None = None

        self._drawing = False
        self._drawing_start_mm: Point | None = None
        self._preview_rectangle_id: int | None = None

        self._marquee_start_mm: Point | None = None
        self._marquee_rectangle_id: int | None = None

        self._text_editor: tk.Text | None = None
        self._text_editor_window_id: int | None = None
        self._text_edit_object_index: int | None = None
        self._text_edit_closing = False

        # Les images de contenu sont conservées en mémoire pendant le rendu
        # afin que Tkinter ne les supprime pas après create_image().
        self._rendered_object_images: list[ImageTk.PhotoImage] = []
        self._source_image_cache: dict[str, tuple[int, int, Image.Image]] = {}
        self._image_path_resolver: Callable[[str], Path | None] | None = None

        # Historique local du canvas. Il peut aussi mémoriser un état
        # externe fourni par la vue, par exemple l'image de fond de la page.
        self._history_external_snapshot: Callable[[], Any] | None = None
        self._history_external_restore: Callable[[Any], None] | None = None
        self._undo_history: list[tuple[list[CanvasObject], int | None, set[int], Any]] = []
        self._redo_history: list[tuple[list[CanvasObject], int | None, set[int], Any]] = []

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

        # Déplacement de la vue à la manière des logiciels de mise en page :
        # maintenir Espace puis faire glisser avec le bouton gauche.
        self.bind(
            "<KeyPress-space>",
            self._activate_space_pan,
        )
        self.bind(
            "<KeyRelease-space>",
            self._deactivate_space_pan,
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
            "<Escape>",
            self._cancel_reference_with_escape,
        )

        # Le focus peut se trouver sur un bouton de la barre d’outils.
        # La liaison à la fenêtre garantit que Échap annule tout de même
        # la sélection et l’objet de référence du canvas.
        self.after_idle(
            self._bind_escape_to_window,
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

        self.bind(
            "<Control-l>",
            self._toggle_selection_lock,
        )
        self.bind(
            "<Control-L>",
            self._toggle_selection_lock,
        )

        # Grouper : Ctrl + G. Dissocier : Ctrl + Maj + G.
        self.bind(
            "<Control-g>",
            self._group_selection_with_keyboard,
        )
        self.bind(
            "<Control-Shift-g>",
            self._ungroup_selection_with_keyboard,
        )
        self.bind(
            "<Control-Shift-G>",
            self._ungroup_selection_with_keyboard,
        )

    def _bind_escape_to_window(self) -> None:

        top_level = self.winfo_toplevel()

        top_level.bind(
            "<Escape>",
            self._cancel_reference_with_escape,
            add="+",
        )

    def _clear_reference_state(
        self,
        *,
        clear_selection: bool,
        redraw: bool = True,
        notify: bool = True,
    ) -> None:

        self._reference_object_index = None

        if clear_selection:
            self._selected_object_index = None
            self._selected_object_indices.clear()

        self._page_selected = False
        self._interaction_mode = None
        self._interaction_handle = None
        self._interaction_start_mm = None
        self._interaction_original_bounds = None
        self._interaction_original_bounds_by_index = {}
        self._interaction_original_rotations_by_index = {}
        self._interaction_original_centers_by_index = {}
        self._interaction_rotation_pivot = None
        self._interaction_start_angle_deg = None
        self._marquee_start_mm = None

        if self._marquee_rectangle_id is not None:
            self.delete(
                self._marquee_rectangle_id,
            )
            self._marquee_rectangle_id = None

        if notify:
            self._notify_selection()

        if redraw:
            self.redraw()

    def _cancel_reference_with_escape(
        self,
        event=None,
    ) -> str | None:

        # Pendant l’édition d’un texte, Échap reste réservé à
        # l’annulation de cette édition.
        if self._text_editor is not None:
            return None

        self.set_tool(
            "selection",
        )

        self._clear_reference_state(
            clear_selection=True,
        )

        self.focus_set()

        return "break"

    def set_image_path_resolver(
        self,
        resolver: Callable[[str], Path | None] | None,
    ) -> None:
        """Associe un résolveur aux chemins d’images enregistrés dans les zones."""

        self._image_path_resolver = resolver
        self._source_image_cache.clear()
        self.redraw()

    def set_external_history_state(
        self,
        snapshot_callback: Callable[[], Any] | None,
        restore_callback: Callable[[Any], None] | None,
    ) -> None:
        """Associe un état externe aux instantanés d'annulation.

        La vue de page l'utilise pour intégrer le fond de page au même
        historique que les formes et les autres objets du canvas.
        """

        self._history_external_snapshot = snapshot_callback
        self._history_external_restore = restore_callback

    def _snapshot_state(
        self,
    ) -> tuple[list[CanvasObject], int | None, set[int], Any]:

        external_state = None
        if self._history_external_snapshot is not None:
            external_state = deepcopy(
                self._history_external_snapshot()
            )

        return (
            list(self._objects),
            self._selected_object_index,
            set(self._selected_object_indices),
            external_state,
        )

    def _restore_state(
        self,
        state: tuple[list[CanvasObject], int | None, set[int], Any],
    ) -> None:

        objects, selected_index, selected_indices, external_state = state
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

        if self._history_external_restore is not None:
            self._history_external_restore(
                deepcopy(external_state)
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

        selected_indices = sorted(
            self._expand_indices_to_groups(self._selected_object_indices)
        )
        if not selected_indices:
            return None

        selected_bounds = [
            self._object_visual_bounds(self._objects[index])
            for index in selected_indices
        ]
        min_left = min(bounds.left for bounds in selected_bounds)
        min_top = min(bounds.top for bounds in selected_bounds)
        max_right = max(bounds.right for bounds in selected_bounds)
        max_bottom = max(bounds.bottom for bounds in selected_bounds)

        offset = 5.0
        dx = min(offset, self.page_format.width_mm - max_right)
        dy = min(offset, self.page_format.height_mm - max_bottom)
        if dx <= 0.0 and dy <= 0.0:
            dx = max(-offset, -min_left)
            dy = max(-offset, -min_top)

        existing_group_ids = sorted({
            self._objects[index].group_id
            for index in selected_indices
            if self._objects[index].group_id is not None
        })
        next_group_id = self._next_group_id()
        group_mapping = {
            group_id: next_group_id + offset_index
            for offset_index, group_id in enumerate(existing_group_ids)
        }

        self._remember_current_state()
        first_new_index = len(self._objects)

        for index in selected_indices:
            selected_object = self._objects[index]
            bounds = selected_object.bounds
            duplicate = replace(
                selected_object,
                bounds=Rect(
                    Point(bounds.left + dx, bounds.top + dy),
                    bounds.size,
                ),
                locked=False,
                group_id=(
                    group_mapping.get(selected_object.group_id)
                    if selected_object.group_id is not None
                    else None
                ),
            )
            self._objects.append(duplicate)

        new_indices = set(range(first_new_index, len(self._objects)))
        self._selected_object_indices = new_indices
        self._selected_object_index = max(new_indices)
        self.redraw()
        self._notify_selection()

        return "break"

    def _delete_selection(
        self,
        event=None,
    ) -> str | None:

        selected_indices = sorted(
            self._expand_indices_to_groups(self._selected_object_indices)
        )
        deletable_indices = [
            index
            for index in selected_indices
            if not self._objects[index].locked
        ]
        if not deletable_indices:
            return "break"

        deleted_set = set(deletable_indices)
        old_reference_index = self._reference_object_index

        self._remember_current_state()
        old_objects = list(self._objects)
        self._objects = [
            graphic_object
            for index, graphic_object in enumerate(old_objects)
            if index not in deleted_set
        ]

        old_to_new: dict[int, int] = {}
        new_index = 0
        for old_index in range(len(old_objects)):
            if old_index in deleted_set:
                continue
            old_to_new[old_index] = new_index
            new_index += 1

        self._selected_object_indices = {
            old_to_new[index]
            for index in selected_indices
            if index in old_to_new
        }
        self._selected_object_index = (
            max(self._selected_object_indices)
            if self._selected_object_indices
            else None
        )
        self._reference_object_index = (
            old_to_new.get(old_reference_index)
            if old_reference_index is not None
            else None
        )

        self.redraw()
        self._notify_selection()

        return "break"

    def _move_selection_with_keyboard(
        self,
        event,
    ) -> str | None:

        selected_indices = [
            index
            for index in sorted(self._selected_object_indices)
            if (
                0 <= index < len(self._objects)
                and not self._objects[index].locked
            )
        ]

        if not selected_indices:
            return "break"

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
            self._object_visual_bounds(self._objects[index])
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
    # Verrouillage
    # ==========================================================

    def _selected_indices_for_locking(self) -> list[int]:

        selected_indices = [
            index
            for index in sorted(self._selected_object_indices)
            if 0 <= index < len(self._objects)
        ]

        if (
            not selected_indices
            and self._selected_object_index is not None
            and 0 <= self._selected_object_index < len(self._objects)
        ):
            selected_indices = [self._selected_object_index]

        return selected_indices

    def get_selection_lock_state(self) -> bool | None:
        """Retourne l'état de verrouillage commun de la sélection."""

        selected_indices = self._selected_indices_for_locking()
        if not selected_indices:
            return None

        return all(
            self._objects[index].locked
            for index in selected_indices
        )

    def set_selection_locked(self, locked: bool) -> bool:
        """Verrouille ou déverrouille les objets bleus sélectionnés."""

        selected_indices = self._selected_indices_for_locking()
        if not selected_indices:
            return False

        changed_indices = [
            index
            for index in selected_indices
            if self._objects[index].locked != locked
        ]
        if not changed_indices:
            return False

        self.commit_active_text_edit()
        self._remember_current_state()

        for index in changed_indices:
            self._objects[index] = replace(
                self._objects[index],
                locked=locked,
            )

        self._interaction_mode = None
        self._interaction_handle = None
        self._interaction_start_mm = None
        self._interaction_original_bounds = None
        self._interaction_original_bounds_by_index = {}
        self._interaction_original_rotations_by_index = {}
        self._interaction_original_centers_by_index = {}
        self._interaction_rotation_pivot = None
        self._interaction_start_angle_deg = None

        self.redraw()
        self._notify_selection()
        return True

    def toggle_selection_lock(self) -> bool:
        """Bascule le verrouillage de la sélection."""

        state = self.get_selection_lock_state()
        if state is None:
            return False

        return self.set_selection_locked(not state)

    def _toggle_selection_lock(
        self,
        event=None,
    ) -> str:

        self.toggle_selection_lock()
        return "break"

    # ==========================================================
    # Groupement
    # ==========================================================

    def _group_indices_for_object(self, object_index: int) -> set[int]:
        """Retourne tous les membres du groupe de l'objet."""

        if not 0 <= object_index < len(self._objects):
            return set()

        group_id = self._objects[object_index].group_id
        if group_id is None:
            return {object_index}

        return {
            index
            for index, graphic_object in enumerate(self._objects)
            if graphic_object.group_id == group_id
        }

    def _expand_indices_to_groups(self, indices) -> set[int]:
        """Étend une sélection afin qu'un groupe reste toujours entier."""

        expanded: set[int] = set()
        for index in indices:
            if 0 <= index < len(self._objects):
                expanded.update(self._group_indices_for_object(index))
        return expanded

    def _next_group_id(self) -> int:
        group_ids = [
            graphic_object.group_id
            for graphic_object in self._objects
            if graphic_object.group_id is not None
        ]
        return (max(group_ids) + 1) if group_ids else 1

    def can_group_selection(self) -> bool:
        selected_indices = self._expand_indices_to_groups(
            self._selected_object_indices,
        )
        return (
            len(selected_indices) >= 2
            and all(
                not self._objects[index].locked
                for index in selected_indices
            )
        )

    def can_ungroup_selection(self) -> bool:
        selected_indices = self._expand_indices_to_groups(
            self._selected_object_indices,
        )
        grouped_indices = [
            index
            for index in selected_indices
            if self._objects[index].group_id is not None
        ]
        return bool(grouped_indices) and all(
            not self._objects[index].locked
            for index in grouped_indices
        )

    def group_selection(self) -> bool:
        """Réunit les objets bleus en un seul groupe logique."""

        selected_indices = self._expand_indices_to_groups(
            self._selected_object_indices,
        )
        if len(selected_indices) < 2:
            return False
        if any(self._objects[index].locked for index in selected_indices):
            return False

        self.commit_active_text_edit()
        self._remember_current_state()
        group_id = self._next_group_id()

        for index in selected_indices:
            self._objects[index] = replace(
                self._objects[index],
                group_id=group_id,
            )

        # Une référence rouge désigne toujours un objet indépendant.
        # Si cet objet vient d'être intégré au groupe, la référence est annulée
        # afin qu'aucun membre ne paraisse isolé du groupe.
        if self._reference_object_index in selected_indices:
            self._reference_object_index = None

        self._selected_object_indices = set(selected_indices)
        if self._selected_object_index not in self._selected_object_indices:
            self._selected_object_index = max(self._selected_object_indices)

        self.redraw()
        self._notify_selection()
        return True

    def ungroup_selection(self) -> bool:
        """Dissocie entièrement les groupes présents dans la sélection."""

        selected_indices = self._expand_indices_to_groups(
            self._selected_object_indices,
        )
        group_ids = {
            self._objects[index].group_id
            for index in selected_indices
            if self._objects[index].group_id is not None
        }
        if not group_ids:
            return False

        grouped_indices = {
            index
            for index, graphic_object in enumerate(self._objects)
            if graphic_object.group_id in group_ids
        }
        if any(self._objects[index].locked for index in grouped_indices):
            return False

        self.commit_active_text_edit()
        self._remember_current_state()

        for index in grouped_indices:
            self._objects[index] = replace(
                self._objects[index],
                group_id=None,
            )

        self._selected_object_indices = set(grouped_indices)
        if self._selected_object_index not in self._selected_object_indices:
            self._selected_object_index = max(self._selected_object_indices)

        self.redraw()
        self._notify_selection()
        return True

    def _group_selection_with_keyboard(self, event=None) -> str:
        self.group_selection()
        return "break"

    def _ungroup_selection_with_keyboard(self, event=None) -> str:
        self.ungroup_selection()
        return "break"

    # ==========================================================
    # Rotation et géométrie
    # ==========================================================

    @staticmethod
    def _normalize_rotation(angle: float) -> float:
        normalized = float(angle) % 360.0
        if abs(normalized - 360.0) < 1e-9 or abs(normalized) < 1e-9:
            return 0.0
        return normalized

    @staticmethod
    def _object_center(graphic_object: CanvasObject) -> Point:
        bounds = graphic_object.bounds
        return Point(
            bounds.left + bounds.width / 2,
            bounds.top + bounds.height / 2,
        )

    @staticmethod
    def _rotate_point(
        point: Point,
        pivot: Point,
        angle_degrees: float,
    ) -> Point:
        angle = radians(angle_degrees)
        dx = point.x - pivot.x
        dy = point.y - pivot.y
        return Point(
            pivot.x + dx * cos(angle) - dy * sin(angle),
            pivot.y + dx * sin(angle) + dy * cos(angle),
        )

    def _inverse_rotate_point(
        self,
        point: Point,
        pivot: Point,
        angle_degrees: float,
    ) -> Point:
        return self._rotate_point(point, pivot, -angle_degrees)

    def _object_corners(self, graphic_object: CanvasObject) -> list[Point]:
        bounds = graphic_object.bounds
        center = self._object_center(graphic_object)
        corners = [
            Point(bounds.left, bounds.top),
            Point(bounds.right, bounds.top),
            Point(bounds.right, bounds.bottom),
            Point(bounds.left, bounds.bottom),
        ]
        rotation = self._normalize_rotation(graphic_object.rotation)
        if rotation == 0.0:
            return corners
        return [
            self._rotate_point(point, center, rotation)
            for point in corners
        ]

    def _object_visual_bounds(self, graphic_object: CanvasObject) -> Rect:
        corners = self._object_corners(graphic_object)
        left = min(point.x for point in corners)
        top = min(point.y for point in corners)
        right = max(point.x for point in corners)
        bottom = max(point.y for point in corners)
        return Rect(Point(left, top), Size(right - left, bottom - top))

    def _selection_visual_bounds(self, indices) -> Rect | None:
        visual_bounds = [
            self._object_visual_bounds(self._objects[index])
            for index in indices
            if 0 <= index < len(self._objects)
        ]
        if not visual_bounds:
            return None
        left = min(bounds.left for bounds in visual_bounds)
        top = min(bounds.top for bounds in visual_bounds)
        right = max(bounds.right for bounds in visual_bounds)
        bottom = max(bounds.bottom for bounds in visual_bounds)
        return Rect(Point(left, top), Size(right - left, bottom - top))

    def _shift_indices_inside_page(self, indices) -> None:
        selection_bounds = self._selection_visual_bounds(indices)
        if selection_bounds is None:
            return

        dx = 0.0
        dy = 0.0
        if selection_bounds.left < 0.0:
            dx = -selection_bounds.left
        elif selection_bounds.right > self.page_format.width_mm:
            dx = self.page_format.width_mm - selection_bounds.right

        if selection_bounds.top < 0.0:
            dy = -selection_bounds.top
        elif selection_bounds.bottom > self.page_format.height_mm:
            dy = self.page_format.height_mm - selection_bounds.bottom

        if abs(dx) < 1e-9 and abs(dy) < 1e-9:
            return

        for index in indices:
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

    def _selected_indices_for_rotation(self) -> list[int]:
        indices = sorted(
            self._expand_indices_to_groups(self._selected_object_indices)
        )
        if not indices:
            return []
        if any(self._objects[index].locked for index in indices):
            return []
        return indices

    def get_selection_rotation(self) -> float | None:
        indices = self._selected_indices_for_rotation()
        if not indices:
            return None
        primary_index = self._selected_object_index
        if primary_index not in indices:
            primary_index = indices[-1]
        return self._normalize_rotation(
            self._objects[primary_index].rotation
        )

    def set_selection_rotation(self, angle: float) -> bool:
        indices = self._selected_indices_for_rotation()
        if not indices:
            return False

        primary_index = self._selected_object_index
        if primary_index not in indices:
            primary_index = indices[-1]

        current_angle = self._normalize_rotation(
            self._objects[primary_index].rotation
        )
        target_angle = self._normalize_rotation(angle)
        delta = (target_angle - current_angle + 180.0) % 360.0 - 180.0
        if abs(delta) < 1e-9:
            return False

        selection_bounds = self._selection_visual_bounds(indices)
        if selection_bounds is None:
            return False
        pivot = Point(
            selection_bounds.left + selection_bounds.width / 2,
            selection_bounds.top + selection_bounds.height / 2,
        )

        self.commit_active_text_edit()
        self._remember_current_state()

        for index in indices:
            graphic_object = self._objects[index]
            center = self._object_center(graphic_object)
            rotated_center = self._rotate_point(center, pivot, delta)
            bounds = graphic_object.bounds
            self._objects[index] = replace(
                graphic_object,
                bounds=Rect(
                    Point(
                        rotated_center.x - bounds.width / 2,
                        rotated_center.y - bounds.height / 2,
                    ),
                    bounds.size,
                ),
                rotation=self._normalize_rotation(
                    graphic_object.rotation + delta
                ),
            )

        self._shift_indices_inside_page(indices)
        self.redraw()
        self._notify_selection()
        return True

    def _selection_is_single_group(self) -> bool:
        indices = self._selected_indices_for_rotation()
        if not indices:
            return False
        group_ids = {self._objects[index].group_id for index in indices}
        return len(group_ids) == 1 and None not in group_ids

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

    def get_reference_object_index(self) -> int | None:
        """Retourne l'index de l'objet choisi comme référence."""

        if self._reference_object_index is None:
            return None
        if not 0 <= self._reference_object_index < len(self._objects):
            self._reference_object_index = None
            return None
        return self._reference_object_index

    def update_selected_object(self, **changes) -> None:

        if self._selected_object_index is None:
            return
        if not 0 <= self._selected_object_index < len(self._objects):
            return

        current = self._objects[self._selected_object_index]
        if current.locked:
            return

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

    def align_selection(self, mode: str) -> bool:
        """Aligne la sélection multiple sur l'objet actif."""

        selected_indices = [
            index
            for index in sorted(self._selected_object_indices)
            if 0 <= index < len(self._objects)
        ]

        if len(selected_indices) < 2:
            return False

        reference_index = self._selected_object_index
        if reference_index not in selected_indices:
            reference_index = selected_indices[-1]

        reference_bounds = self._objects[reference_index].bounds
        valid_modes = {
            "left",
            "center_x",
            "right",
            "top",
            "center_y",
            "bottom",
        }

        if mode not in valid_modes:
            return False

        self._remember_current_state()

        for index in selected_indices:
            if index == reference_index:
                continue

            graphic_object = self._objects[index]
            if graphic_object.locked:
                continue

            bounds = graphic_object.bounds
            new_x = bounds.left
            new_y = bounds.top

            if mode == "left":
                new_x = reference_bounds.left
            elif mode == "center_x":
                new_x = (
                    reference_bounds.left
                    + (reference_bounds.width - bounds.width) / 2
                )
            elif mode == "right":
                new_x = reference_bounds.right - bounds.width
            elif mode == "top":
                new_y = reference_bounds.top
            elif mode == "center_y":
                new_y = (
                    reference_bounds.top
                    + (reference_bounds.height - bounds.height) / 2
                )
            elif mode == "bottom":
                new_y = reference_bounds.bottom - bounds.height

            self._objects[index] = replace(
                graphic_object,
                bounds=Rect(
                    Point(new_x, new_y),
                    bounds.size,
                ),
            )

        self.redraw()
        self._notify_selection()
        return True

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
        self._rendered_object_images.clear()

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

    def _point_to_canvas_px(self, point: Point) -> tuple[float, float]:
        return (
            self.page_left + self.viewport.mm_to_px(point.x),
            self.page_top + self.viewport.mm_to_px(point.y),
        )

    def _object_polygon_points_px(
        self,
        graphic_object: CanvasObject,
    ) -> list[float]:
        points: list[float] = []
        for point in self._object_corners(graphic_object):
            x_px, y_px = self._point_to_canvas_px(point)
            points.extend((x_px, y_px))
        return points

    def _ellipse_polygon_points_px(
        self,
        graphic_object: CanvasObject,
    ) -> list[float]:
        bounds = graphic_object.bounds
        center = self._object_center(graphic_object)
        radius_x = bounds.width / 2
        radius_y = bounds.height / 2
        rotation = self._normalize_rotation(graphic_object.rotation)
        points: list[float] = []

        for step in range(self.ELLIPSE_SEGMENTS):
            angle = 2 * pi * step / self.ELLIPSE_SEGMENTS
            local_point = Point(
                center.x + radius_x * cos(angle),
                center.y + radius_y * sin(angle),
            )
            rotated_point = self._rotate_point(
                local_point,
                center,
                rotation,
            )
            x_px, y_px = self._point_to_canvas_px(rotated_point)
            points.extend((x_px, y_px))

        return points

    @staticmethod
    def _has_text_content(graphic_object: CanvasObject) -> bool:
        """Indique si la zone est destinée à recevoir du texte."""

        return (
            graphic_object.kind == "text"
            or graphic_object.content_type == "text"
        )

    @staticmethod
    def _has_image_content(graphic_object: CanvasObject) -> bool:
        return graphic_object.content_type == "image"

    @staticmethod
    def _content_is_fixed(graphic_object: CanvasObject) -> bool:
        return getattr(graphic_object, "content_mode", "variable") == "fixed"

    @staticmethod
    def _content_label(graphic_object: CanvasObject) -> str:
        label = getattr(graphic_object, "content_label", "").strip()
        if label:
            return label
        if graphic_object.content_type == "image":
            return "IMAGE"
        if graphic_object.content_type == "text" or graphic_object.kind == "text":
            return "TEXTE"
        return "CONTENU"

    def _draw_placeholder_line(
        self,
        graphic_object: CanvasObject,
        start: Point,
        end: Point,
        *,
        width: int = 2,
    ) -> None:
        center = self._object_center(graphic_object)
        rotation = self._normalize_rotation(graphic_object.rotation)
        rotated_start = self._rotate_point(start, center, rotation)
        rotated_end = self._rotate_point(end, center, rotation)
        start_x, start_y = self._point_to_canvas_px(rotated_start)
        end_x, end_y = self._point_to_canvas_px(rotated_end)
        self.create_line(
            start_x,
            start_y,
            end_x,
            end_y,
            fill="#8A8A8A",
            width=width,
            capstyle="round",
        )

    def _draw_content_placeholder(self, graphic_object: CanvasObject) -> None:
        """Dessine la balise visuelle d'un contenu variable de gabarit."""

        bounds = graphic_object.bounds
        center = self._object_center(graphic_object)
        padding = min(bounds.width, bounds.height) * 0.16
        padding = max(2.0, min(8.0, padding))
        inner_left = bounds.left + padding
        inner_right = bounds.right - padding
        inner_top = bounds.top + padding
        inner_bottom = bounds.bottom - padding

        if inner_right <= inner_left or inner_bottom <= inner_top:
            return

        if graphic_object.content_type == "image":
            image_top = inner_top
            image_bottom = inner_bottom - min(7.0, bounds.height * 0.22)
            if image_bottom > image_top:
                self._draw_placeholder_line(
                    graphic_object,
                    Point(inner_left, image_bottom),
                    Point(inner_left + (inner_right - inner_left) * 0.32, image_top + (image_bottom - image_top) * 0.56),
                )
                self._draw_placeholder_line(
                    graphic_object,
                    Point(inner_left + (inner_right - inner_left) * 0.32, image_top + (image_bottom - image_top) * 0.56),
                    Point(inner_left + (inner_right - inner_left) * 0.52, image_top + (image_bottom - image_top) * 0.76),
                )
                self._draw_placeholder_line(
                    graphic_object,
                    Point(inner_left + (inner_right - inner_left) * 0.52, image_top + (image_bottom - image_top) * 0.76),
                    Point(inner_right, image_top + (image_bottom - image_top) * 0.28),
                )

                sun_center = Point(
                    inner_left + (inner_right - inner_left) * 0.72,
                    image_top + (image_bottom - image_top) * 0.24,
                )
                radius = min(bounds.width, bounds.height) * 0.045
                radius = max(1.0, min(3.0, radius))
                points: list[float] = []
                rotation = self._normalize_rotation(graphic_object.rotation)
                for step in range(20):
                    angle = 2 * pi * step / 20
                    point = Point(
                        sun_center.x + radius * cos(angle),
                        sun_center.y + radius * sin(angle),
                    )
                    point = self._rotate_point(point, center, rotation)
                    x_px, y_px = self._point_to_canvas_px(point)
                    points.extend((x_px, y_px))
                self.create_polygon(
                    *points,
                    fill="",
                    outline="#8A8A8A",
                    width=2,
                    smooth=True,
                )
        else:
            available_height = inner_bottom - inner_top
            line_count = 4
            line_gap = available_height / max(1, line_count - 1)
            for line_index in range(line_count):
                y = inner_top + line_index * line_gap
                end_ratio = 0.68 if line_index == line_count - 1 else 1.0
                self._draw_placeholder_line(
                    graphic_object,
                    Point(inner_left, y),
                    Point(
                        inner_left + (inner_right - inner_left) * end_ratio,
                        y,
                    ),
                    width=2,
                )

        label_point = self._rotate_point(
            Point(center.x, inner_bottom),
            center,
            self._normalize_rotation(graphic_object.rotation),
        )
        label_x, label_y = self._point_to_canvas_px(label_point)
        self.create_text(
            label_x,
            label_y,
            text=self._content_label(graphic_object),
            fill="#666666",
            font=("Arial", 9, "bold"),
            anchor="s",
            angle=-self._normalize_rotation(graphic_object.rotation),
        )

    def _resolve_object_image_path(
        self,
        graphic_object: CanvasObject,
    ) -> Path | None:
        raw_path = graphic_object.image_path.strip()
        if not raw_path:
            return None

        if self._image_path_resolver is not None:
            try:
                resolved = self._image_path_resolver(raw_path)
            except (OSError, RuntimeError, TypeError, ValueError):
                resolved = None
            if resolved is not None:
                path = Path(resolved)
                return path if path.is_file() else None

        path = Path(raw_path)
        return path if path.is_file() else None

    def _load_source_image(
        self,
        path: Path,
    ) -> Image.Image | None:
        try:
            stat = path.stat()
            cache_key = str(path.resolve())
            signature = (stat.st_mtime_ns, stat.st_size)
            cached = self._source_image_cache.get(cache_key)
            if cached is not None and cached[:2] == signature:
                return cached[2]

            with Image.open(path) as source:
                loaded = ImageOps.exif_transpose(source).convert("RGBA")
                loaded.load()

            self._source_image_cache[cache_key] = (
                signature[0],
                signature[1],
                loaded,
            )
            return loaded
        except (OSError, ValueError):
            return None

    @staticmethod
    def _clamp(value: float, minimum: float, maximum: float) -> float:
        return max(minimum, min(maximum, float(value)))

    def _prepare_zone_image(
        self,
        graphic_object: CanvasObject,
        source: Image.Image,
        width_px: int,
        height_px: int,
    ) -> Image.Image:
        source_width, source_height = source.size
        if source_width <= 0 or source_height <= 0:
            return Image.new("RGBA", (width_px, height_px), (0, 0, 0, 0))

        fit_mode = graphic_object.image_fit.strip().lower()
        if fit_mode not in {"cover", "contain"}:
            fit_mode = "cover"

        base_scale = (
            min(width_px / source_width, height_px / source_height)
            if fit_mode == "contain"
            else max(width_px / source_width, height_px / source_height)
        )
        zoom = max(0.05, float(graphic_object.image_zoom))
        scale = max(0.001, base_scale * zoom)
        resized_width = max(1, round(source_width * scale))
        resized_height = max(1, round(source_height * scale))
        resized = source.resize(
            (resized_width, resized_height),
            Image.Resampling.LANCZOS,
        )

        focus_x = self._clamp(graphic_object.image_focus_x, 0.0, 1.0)
        focus_y = self._clamp(graphic_object.image_focus_y, 0.0, 1.0)
        overflow_x = max(0, resized_width - width_px)
        overflow_y = max(0, resized_height - height_px)
        free_x = max(0, width_px - resized_width)
        free_y = max(0, height_px - resized_height)

        paste_x = (
            -round(overflow_x * focus_x)
            if overflow_x
            else round(free_x * focus_x)
        )
        paste_y = (
            -round(overflow_y * focus_y)
            if overflow_y
            else round(free_y * focus_y)
        )

        prepared = Image.new(
            "RGBA",
            (width_px, height_px),
            (0, 0, 0, 0),
        )
        prepared.alpha_composite(resized, (paste_x, paste_y))

        if graphic_object.kind == "ellipse":
            mask = Image.new("L", (width_px, height_px), 0)
            ImageDraw.Draw(mask).ellipse(
                (0, 0, width_px - 1, height_px - 1),
                fill=255,
            )
            prepared.putalpha(
                Image.composite(prepared.getchannel("A"), mask, mask)
            )

        return prepared

    def _draw_zone_image(self, graphic_object: CanvasObject) -> bool:
        path = self._resolve_object_image_path(graphic_object)
        if path is None:
            return False

        source = self._load_source_image(path)
        if source is None:
            return False

        width_px = max(1, round(self.viewport.mm_to_px(graphic_object.bounds.width)))
        height_px = max(1, round(self.viewport.mm_to_px(graphic_object.bounds.height)))
        prepared = self._prepare_zone_image(
            graphic_object,
            source,
            width_px,
            height_px,
        )

        rotation = self._normalize_rotation(graphic_object.rotation)
        if rotation:
            prepared = prepared.rotate(
                -rotation,
                resample=Image.Resampling.BICUBIC,
                expand=True,
            )

        tk_image = ImageTk.PhotoImage(prepared)
        self._rendered_object_images.append(tk_image)
        center = self._object_center(graphic_object)
        center_x, center_y = self._point_to_canvas_px(center)
        self.create_image(
            center_x,
            center_y,
            image=tk_image,
            anchor="center",
        )
        return True

    def _draw_objects(self) -> None:

        for index, graphic_object in enumerate(self._objects):

            selected = index in self._selected_object_indices

            # Un groupe sélectionné est représenté uniquement par son cadre
            # commun. Aucun de ses membres ne conserve un cadre bleu isolé.
            selected_individually = (
                selected
                and graphic_object.group_id is None
            )
            is_reference = (
                index == self._reference_object_index
                and graphic_object.group_id is None
            )

            outline = (
                "#D62828"
                if is_reference
                else "#3874CB"
                if selected_individually
                else graphic_object.outline
            )
            line_width = (
                2
                if is_reference or selected_individually
                else graphic_object.line_width
            )

            points = (
                self._ellipse_polygon_points_px(graphic_object)
                if graphic_object.kind == "ellipse"
                else self._object_polygon_points_px(graphic_object)
            )

            has_image = self._has_image_content(graphic_object)
            content_is_fixed = self._content_is_fixed(graphic_object)
            has_fixed_image = (
                has_image
                and content_is_fixed
                and bool(graphic_object.image_path.strip())
            )
            has_variable_content = (
                bool(graphic_object.content_type)
                and not content_is_fixed
            )

            self.create_polygon(
                *points,
                fill=graphic_object.fill,
                outline=("" if has_fixed_image else outline),
                width=(0 if has_fixed_image else line_width),
                smooth=(graphic_object.kind == "ellipse"),
                splinesteps=24,
            )

            if has_fixed_image:
                self._draw_zone_image(graphic_object)
                self.create_polygon(
                    *points,
                    fill="",
                    outline=outline,
                    width=line_width,
                    smooth=(graphic_object.kind == "ellipse"),
                    splinesteps=24,
                )

            if (
                self._has_text_content(graphic_object)
                and content_is_fixed
            ):
                self._draw_rotated_text(graphic_object)
            elif has_variable_content:
                self._draw_content_placeholder(graphic_object)

            if graphic_object.locked:
                self._draw_lock_indicator(
                    self._object_visual_bounds(graphic_object)
                )

            if (
                selected
                and index == self._selected_object_index
                and not graphic_object.locked
                and graphic_object.group_id is None
            ):
                self._draw_selection_handles(
                    graphic_object.bounds,
                    rotation=graphic_object.rotation,
                    is_reference=is_reference,
                )

        self._draw_selected_group_outlines()

    def _draw_rotated_text(self, graphic_object: CanvasObject) -> None:
        bounds = graphic_object.bounds
        center = self._object_center(graphic_object)
        rotation = self._normalize_rotation(graphic_object.rotation)
        padding_px = 6
        padding_mm = self.viewport.px_to_mm(padding_px)
        text_width = max(1, self.viewport.mm_to_px(bounds.width) - padding_px * 2)

        anchor_by_align = {
            "left": "nw",
            "center": "n",
            "right": "ne",
        }
        local_x_by_align = {
            "left": bounds.left + padding_mm,
            "center": bounds.left + bounds.width / 2,
            "right": bounds.right - padding_mm,
        }
        local_anchor = Point(
            local_x_by_align.get(
                graphic_object.align,
                bounds.left + padding_mm,
            ),
            bounds.top + padding_mm,
        )
        anchor_point = self._rotate_point(local_anchor, center, rotation)
        anchor_x, anchor_y = self._point_to_canvas_px(anchor_point)

        font_style = []
        if graphic_object.bold:
            font_style.append("bold")
        if graphic_object.italic:
            font_style.append("italic")

        self.create_text(
            anchor_x,
            anchor_y,
            anchor=anchor_by_align.get(graphic_object.align, "nw"),
            justify=(
                graphic_object.align
                if graphic_object.align in {"left", "center", "right"}
                else "left"
            ),
            text=graphic_object.text,
            width=text_width,
            fill=graphic_object.text_color,
            font=(
                graphic_object.font_family,
                graphic_object.font_size,
                " ".join(font_style),
            ),
            angle=-rotation,
        )

    def _draw_selected_group_outlines(self) -> None:
        """Matérialise les groupes sélectionnés sans lettre ni abréviation."""

        selected_group_ids = {
            self._objects[index].group_id
            for index in self._selected_object_indices
            if (
                0 <= index < len(self._objects)
                and self._objects[index].group_id is not None
            )
        }

        for group_id in selected_group_ids:
            group_indices = {
                index
                for index, graphic_object in enumerate(self._objects)
                if graphic_object.group_id == group_id
            }
            if not group_indices or not group_indices.issubset(
                self._selected_object_indices
            ):
                continue

            group_bounds = self._selection_visual_bounds(group_indices)
            if group_bounds is None:
                continue

            margin = 4
            left = self.page_left + self.viewport.mm_to_px(group_bounds.left)
            top = self.page_top + self.viewport.mm_to_px(group_bounds.top)
            right = self.page_left + self.viewport.mm_to_px(group_bounds.right)
            bottom = self.page_top + self.viewport.mm_to_px(group_bounds.bottom)

            self.create_rectangle(
                left - margin,
                top - margin,
                right + margin,
                bottom + margin,
                outline="#3874CB",
                width=2,
                dash=(6, 4),
                fill="",
            )

            if (
                group_indices == self._selected_object_indices
                and not any(self._objects[index].locked for index in group_indices)
            ):
                # Le groupe se manipule comme une seule unité : huit poignées
                # de redimensionnement et une poignée ronde de rotation.
                self._draw_selection_handles(
                    group_bounds,
                    rotation=0.0,
                )

    def _draw_lock_indicator(
        self,
        bounds: Rect,
    ) -> None:
        """Dessine un petit cadenas, sans lettre ni abréviation."""

        right = self.page_left + self.viewport.mm_to_px(bounds.right)
        top = self.page_top + self.viewport.mm_to_px(bounds.top)
        badge_x = right - 10
        badge_y = top + 10

        self.create_oval(
            badge_x - 9,
            badge_y - 9,
            badge_x + 9,
            badge_y + 9,
            fill="#F4F4F4",
            outline="#666666",
            width=1,
        )

        # Anse du cadenas.
        self.create_arc(
            badge_x - 4,
            badge_y - 6,
            badge_x + 4,
            badge_y + 2,
            start=0,
            extent=180,
            style="arc",
            outline="#444444",
            width=2,
        )

        # Corps du cadenas.
        self.create_rectangle(
            badge_x - 5,
            badge_y - 1,
            badge_x + 5,
            badge_y + 6,
            fill="#666666",
            outline="#444444",
            width=1,
        )

        # Entrée de clé.
        self.create_oval(
            badge_x - 1,
            badge_y + 1,
            badge_x + 1,
            badge_y + 3,
            fill="#F4F4F4",
            outline="",
        )

    def _draw_selection_handles(
        self,
        bounds: Rect,
        rotation: float = 0.0,
        is_reference: bool = False,
    ) -> None:

        color = "#D62828" if is_reference else "#3874CB"
        positions = self._selection_handle_positions(bounds, rotation)

        for name, (x_px, y_px) in positions.items():
            if name == "rotate":
                continue

            half = self.HANDLE_SIZE_PX / 2

            self.create_rectangle(
                x_px - half,
                y_px - half,
                x_px + half,
                y_px + half,
                fill="white",
                outline=color,
                width=2,
            )

        top_x, top_y = positions["n"]
        rotate_x, rotate_y = positions["rotate"]
        self.create_line(
            top_x,
            top_y,
            rotate_x,
            rotate_y,
            fill=color,
            width=2,
        )
        radius = self.ROTATION_HANDLE_RADIUS_PX
        self.create_oval(
            rotate_x - radius,
            rotate_y - radius,
            rotate_x + radius,
            rotate_y + radius,
            fill="white",
            outline=color,
            width=2,
        )

    def _selection_handle_positions(
        self,
        bounds: Rect,
        rotation: float = 0.0,
    ) -> dict[str, tuple[float, float]]:

        center = Point(
            bounds.left + bounds.width / 2,
            bounds.top + bounds.height / 2,
        )
        page_positions = {
            "nw": Point(bounds.left, bounds.top),
            "n": Point(center.x, bounds.top),
            "ne": Point(bounds.right, bounds.top),
            "e": Point(bounds.right, center.y),
            "se": Point(bounds.right, bounds.bottom),
            "s": Point(center.x, bounds.bottom),
            "sw": Point(bounds.left, bounds.bottom),
            "w": Point(bounds.left, center.y),
        }

        normalized_rotation = self._normalize_rotation(rotation)
        rotated_positions = {
            name: self._rotate_point(point, center, normalized_rotation)
            for name, point in page_positions.items()
        }
        canvas_positions = {
            name: self._point_to_canvas_px(point)
            for name, point in rotated_positions.items()
        }

        center_x, center_y = self._point_to_canvas_px(center)
        top_x, top_y = canvas_positions["n"]
        vector_x = top_x - center_x
        vector_y = top_y - center_y
        length = max((vector_x ** 2 + vector_y ** 2) ** 0.5, 1.0)
        canvas_positions["rotate"] = (
            top_x + vector_x / length * self.ROTATION_HANDLE_DISTANCE_PX,
            top_y + vector_y / length * self.ROTATION_HANDLE_DISTANCE_PX,
        )

        return canvas_positions

    def _group_rotation_handle_position(
        self,
        bounds: Rect,
    ) -> tuple[float, float]:
        center_x = self.page_left + self.viewport.mm_to_px(
            bounds.left + bounds.width / 2
        )
        top_y = self.page_top + self.viewport.mm_to_px(bounds.top)
        return center_x, top_y - self.ROTATION_HANDLE_DISTANCE_PX

    def _draw_group_rotation_handle(self, bounds: Rect) -> None:
        center_x = self.page_left + self.viewport.mm_to_px(
            bounds.left + bounds.width / 2
        )
        top_y = self.page_top + self.viewport.mm_to_px(bounds.top)
        rotate_x, rotate_y = self._group_rotation_handle_position(bounds)
        self.create_line(
            center_x,
            top_y,
            rotate_x,
            rotate_y,
            fill="#3874CB",
            width=2,
        )
        radius = self.ROTATION_HANDLE_RADIUS_PX
        self.create_oval(
            rotate_x - radius,
            rotate_y - radius,
            rotate_x + radius,
            rotate_y + radius,
            fill="white",
            outline="#3874CB",
            width=2,
        )

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
        self._interaction_original_rotations_by_index = {}
        self._interaction_original_centers_by_index = {}
        self._interaction_rotation_pivot = None
        self._interaction_start_angle_deg = None

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

        self._clear_reference_state(
            clear_selection=True,
        )

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

        if (
            not self._has_text_content(self._objects[object_index])
            or not self._content_is_fixed(self._objects[object_index])
        ):
            return None

        if (
            self._objects[object_index].locked
            or self._objects[object_index].group_id is not None
        ):
            return "break"

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

        if (
            not self._has_text_content(graphic_object)
            or not self._content_is_fixed(graphic_object)
            or graphic_object.locked
            or graphic_object.group_id is not None
        ):
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
            "<Control-Return>",
            self._validate_text_edit,
        )
        self._text_editor.bind(
            "<Control-KP_Enter>",
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
            and not self._objects[object_index].locked
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

        if self._space_pan_active:
            self.commit_active_text_edit()
            self._left_pan_active = True
            self._start_pan(event)
            return

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

        preliminary_object_index = self._hit_test_object(start)

        # La poignée de rotation se trouve volontairement hors de l'objet.
        # Elle doit donc être testée avant d'annuler la sélection.
        handle = self._hit_test_handle(
            event.x,
            event.y,
        )

        # Un clic simple dans le vide annule immédiatement la référence rouge
        # et la sélection bleue, y compris hors de la page.
        if preliminary_object_index is None and handle is None:
            self._clear_reference_state(
                clear_selection=True,
                redraw=False,
                notify=False,
            )

        if handle is not None and self._selected_object_index is not None:

            if handle == "rotate":
                rotation_indices = self._selected_indices_for_rotation()
                selection_bounds = self._selection_visual_bounds(rotation_indices)
                if not rotation_indices or selection_bounds is None:
                    return

                self.commit_active_text_edit()
                self._remember_current_state()
                self._interaction_mode = "rotate"
                self._interaction_handle = handle
                self._interaction_rotation_pivot = Point(
                    selection_bounds.left + selection_bounds.width / 2,
                    selection_bounds.top + selection_bounds.height / 2,
                )
                pointer = self._event_to_page_mm_unbounded(event)
                pivot = self._interaction_rotation_pivot
                self._interaction_start_angle_deg = degrees(
                    atan2(pointer.y - pivot.y, pointer.x - pivot.x)
                )
                self._interaction_original_bounds_by_index = {
                    index: self._objects[index].bounds
                    for index in rotation_indices
                }
                self._interaction_original_rotations_by_index = {
                    index: self._objects[index].rotation
                    for index in rotation_indices
                }
                self._interaction_original_centers_by_index = {
                    index: self._object_center(self._objects[index])
                    for index in rotation_indices
                }
                self._interaction_start_mm = pointer
                self._interaction_original_bounds = self._objects[
                    self._selected_object_index
                ].bounds
                return

            self.commit_active_text_edit()
            self._interaction_mode = "resize"
            self._interaction_handle = handle
            self._interaction_start_mm = self._event_to_page_mm(
                event,
                clamp_to_page=True,
            )

            if self._selection_is_single_group():
                resize_indices = self._selected_indices_for_rotation()
                group_bounds = self._selection_visual_bounds(resize_indices)
                if not resize_indices or group_bounds is None:
                    self._interaction_mode = None
                    self._interaction_handle = None
                    self._interaction_start_mm = None
                    return

                self._interaction_original_bounds = group_bounds
                self._interaction_original_bounds_by_index = {
                    index: self._objects[index].bounds
                    for index in resize_indices
                }
                self._interaction_original_centers_by_index = {
                    index: self._object_center(self._objects[index])
                    for index in resize_indices
                }
            else:
                self._interaction_original_bounds = self._objects[
                    self._selected_object_index
                ].bounds
                self._interaction_original_bounds_by_index = {}
                self._interaction_original_centers_by_index = {}

            return

        object_index = preliminary_object_index

        control_pressed = bool(event.state & 0x0004)

        if control_pressed:
            if object_index is not None:
                clicked_indices = self._group_indices_for_object(object_index)
                if clicked_indices.issubset(self._selected_object_indices):
                    self._selected_object_indices.difference_update(clicked_indices)
                    if self._selected_object_index in clicked_indices:
                        self._selected_object_index = (
                            max(self._selected_object_indices)
                            if self._selected_object_indices
                            else None
                        )
                else:
                    self._selected_object_indices.update(clicked_indices)
                    self._selected_object_index = object_index

            self._interaction_mode = None
            self._interaction_start_mm = None
            self._interaction_original_bounds = None
            self._interaction_original_bounds_by_index = {}
            self._interaction_original_rotations_by_index = {}
            self._interaction_original_centers_by_index = {}
            self._interaction_rotation_pivot = None
            self._interaction_start_angle_deg = None

        else:
            clicked_selected_object = (
                object_index is not None
                and object_index in self._selected_object_indices
            )

            if clicked_selected_object:
                clicked_group_indices = self._group_indices_for_object(
                    object_index,
                )

                if self._objects[object_index].group_id is not None:
                    # Un groupe reste une seule unité de sélection. Un clic sur
                    # l'un de ses membres ne peut donc pas transformer ce seul
                    # membre en objet rouge de référence.
                    self._selected_object_indices = set(clicked_group_indices)
                    self._selected_object_index = object_index
                    if self._reference_object_index in clicked_group_indices:
                        self._reference_object_index = None
                else:
                    # Un second clic sur un objet indépendant déjà sélectionné
                    # le désigne comme référence permanente.
                    self._selected_object_index = object_index
                    self._reference_object_index = object_index
            else:
                self._selected_object_index = object_index
                self._selected_object_indices = (
                    self._group_indices_for_object(object_index)
                    if object_index is not None
                    else set()
                )

            if (
                object_index is not None
                and start is not None
                and not self._objects[object_index].locked
            ):

                self._interaction_mode = "move"
                self._interaction_start_mm = start
                self._interaction_original_bounds = self._objects[
                    object_index
                ].bounds
                self._interaction_original_bounds_by_index = {
                    index: self._objects[index].bounds
                    for index in self._selected_object_indices
                    if (
                        0 <= index < len(self._objects)
                        and not self._objects[index].locked
                    )
                }
                self._interaction_original_rotations_by_index = {}
                self._interaction_original_centers_by_index = {}
                self._interaction_rotation_pivot = None
                self._interaction_start_angle_deg = None

            elif object_index is not None:

                self._interaction_mode = None
                self._interaction_start_mm = None
                self._interaction_original_bounds = None
                self._interaction_original_bounds_by_index = {}
                self._interaction_original_rotations_by_index = {}
                self._interaction_original_centers_by_index = {}
                self._interaction_rotation_pivot = None
                self._interaction_start_angle_deg = None

            else:

                marquee_start = (
                    start
                    if start is not None
                    else self._event_to_page_mm_unbounded(event)
                )
                self._interaction_mode = "marquee"
                self._interaction_start_mm = marquee_start
                self._interaction_original_bounds = None
                self._interaction_original_bounds_by_index = {}
                self._interaction_original_rotations_by_index = {}
                self._interaction_original_centers_by_index = {}
                self._interaction_rotation_pivot = None
                self._interaction_start_angle_deg = None
                self._marquee_start_mm = marquee_start
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

        if self._left_pan_active:
            self._pan(event)
            return

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

            current = self._event_to_page_mm_unbounded(event)

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

        current = (
            self._event_to_page_mm_unbounded(event)
            if self._interaction_mode == "rotate"
            else self._event_to_page_mm(
                event,
                clamp_to_page=True,
            )
        )

        if current is None:
            return

        if self._interaction_mode == "move":
            self._move_selected_object(current)

        elif self._interaction_mode == "resize":
            self._resize_selected_object(current)

        elif self._interaction_mode == "rotate":
            self._rotate_selection_to_pointer(
                current,
                snap_to_15_degrees=bool(event.state & 0x0001),
            )

    def _on_left_release(
        self,
        event,
    ) -> None:

        if self._left_pan_active:
            self._left_pan_active = False
            self._stop_pan(event)
            self.configure(
                cursor="hand2" if self._space_pan_active else "",
            )
            return

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
                content_type=(
                    "text"
                    if self._active_tool == "text"
                    else ""
                ),
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
            current = self._event_to_page_mm_unbounded(event)

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
                            self._object_visual_bounds(graphic_object).right < left
                            or self._object_visual_bounds(graphic_object).left > right
                            or self._object_visual_bounds(graphic_object).bottom < top
                            or self._object_visual_bounds(graphic_object).top > bottom
                        )
                    }
                    selected = self._expand_indices_to_groups(selected)
                    self._selected_object_indices = selected
                    self._selected_object_index = max(selected) if selected else None

            self.redraw()
            self._notify_selection()

        self._interaction_mode = None
        self._interaction_handle = None
        self._interaction_start_mm = None
        self._interaction_original_bounds = None
        self._interaction_original_bounds_by_index = {}
        self._interaction_original_rotations_by_index = {}
        self._interaction_original_centers_by_index = {}
        self._interaction_rotation_pivot = None
        self._interaction_start_angle_deg = None

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
            graphic_object = self._objects[index]
            bounds = graphic_object.bounds
            center = self._object_center(graphic_object)
            local_point = self._inverse_rotate_point(
                point,
                center,
                graphic_object.rotation,
            )

            if graphic_object.kind == "ellipse":
                radius_x = bounds.width / 2
                radius_y = bounds.height / 2
                if radius_x <= 0.0 or radius_y <= 0.0:
                    continue
                normalized_x = (local_point.x - center.x) / radius_x
                normalized_y = (local_point.y - center.y) / radius_y
                if normalized_x ** 2 + normalized_y ** 2 <= 1.0:
                    return index
            elif bounds.contains(local_point):
                return index

        return None

    def _hit_test_handle(
        self,
        x_px: float,
        y_px: float,
    ) -> str | None:

        if self._selected_object_index is None:
            return None

        rotation_indices = self._selected_indices_for_rotation()
        if not rotation_indices:
            return None

        if self._selection_is_single_group():
            group_bounds = self._selection_visual_bounds(rotation_indices)
            if group_bounds is None:
                return None

            positions = self._selection_handle_positions(
                group_bounds,
                rotation=0.0,
            )

            rotate_x, rotate_y = positions["rotate"]
            rotate_margin = (
                self.ROTATION_HANDLE_RADIUS_PX
                + self.HANDLE_HIT_MARGIN_PX
            )
            if (
                abs(x_px - rotate_x) <= rotate_margin
                and abs(y_px - rotate_y) <= rotate_margin
            ):
                return "rotate"

            resize_margin = (
                self.HANDLE_SIZE_PX / 2
                + self.HANDLE_HIT_MARGIN_PX
            )
            for name, (handle_x, handle_y) in positions.items():
                if name == "rotate":
                    continue
                if (
                    abs(x_px - handle_x) <= resize_margin
                    and abs(y_px - handle_y) <= resize_margin
                ):
                    return name

            return None

        selected_object = self._objects[self._selected_object_index]
        if selected_object.locked or selected_object.group_id is not None:
            return None

        positions = self._selection_handle_positions(
            selected_object.bounds,
            selected_object.rotation,
        )

        rotate_x, rotate_y = positions["rotate"]
        rotate_margin = (
            self.ROTATION_HANDLE_RADIUS_PX
            + self.HANDLE_HIT_MARGIN_PX
        )
        if (
            abs(x_px - rotate_x) <= rotate_margin
            and abs(y_px - rotate_y) <= rotate_margin
        ):
            return "rotate"

        margin = (
            self.HANDLE_SIZE_PX / 2
            + self.HANDLE_HIT_MARGIN_PX
        )

        for name, (handle_x, handle_y) in positions.items():
            if name == "rotate":
                continue
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

        original_visual_bounds = []
        for index, bounds in original_bounds.items():
            if not 0 <= index < len(self._objects):
                continue
            original_visual_bounds.append(
                self._object_visual_bounds(
                    replace(self._objects[index], bounds=bounds)
                )
            )

        if not original_visual_bounds:
            return

        min_left = min(bounds.left for bounds in original_visual_bounds)
        min_top = min(bounds.top for bounds in original_visual_bounds)
        max_right = max(bounds.right for bounds in original_visual_bounds)
        max_bottom = max(bounds.bottom for bounds in original_visual_bounds)

        dx = min(max(dx, -min_left), self.page_format.width_mm - max_right)
        dy = min(max(dy, -min_top), self.page_format.height_mm - max_bottom)

        for index, original in original_bounds.items():
            if not 0 <= index < len(self._objects):
                continue

            graphic_object = self._objects[index]
            if graphic_object.locked:
                continue

            self._objects[index] = replace(
                graphic_object,
                bounds=Rect(
                    Point(original.left + dx, original.top + dy),
                    original.size,
                ),
            )

        self.redraw()
        self._notify_selection()

    def _resize_selected_group(
        self,
        current: Point,
        group_indices: list[int],
    ) -> None:
        """Redimensionne proportionnellement tous les membres d'un groupe."""

        original_group = self._interaction_original_bounds
        handle = self._interaction_handle
        original_bounds_by_index = self._interaction_original_bounds_by_index

        if original_group is None or handle is None:
            return
        if not original_bounds_by_index:
            return
        if original_group.width <= 0.0 or original_group.height <= 0.0:
            return

        valid_indices = [
            index
            for index in group_indices
            if (
                index in original_bounds_by_index
                and 0 <= index < len(self._objects)
                and not self._objects[index].locked
            )
        ]
        if not valid_indices:
            return

        # Empêche qu'un membre du groupe devienne plus petit que la taille
        # minimale autorisée par le canvas.
        minimum_group_width = max(
            self.MIN_OBJECT_SIZE_MM
            * original_group.width
            / max(original_bounds_by_index[index].width, 1e-9)
            for index in valid_indices
        )
        minimum_group_height = max(
            self.MIN_OBJECT_SIZE_MM
            * original_group.height
            / max(original_bounds_by_index[index].height, 1e-9)
            for index in valid_indices
        )

        left = original_group.left
        top = original_group.top
        right = original_group.right
        bottom = original_group.bottom

        if "w" in handle:
            left = min(current.x, right - minimum_group_width)
        if "e" in handle:
            right = max(current.x, left + minimum_group_width)
        if "n" in handle:
            top = min(current.y, bottom - minimum_group_height)
        if "s" in handle:
            bottom = max(current.y, top + minimum_group_height)

        new_width = right - left
        new_height = bottom - top
        scale_x = new_width / original_group.width
        scale_y = new_height / original_group.height

        for index in valid_indices:
            graphic_object = self._objects[index]
            original_bounds = original_bounds_by_index[index]
            original_center = self._interaction_original_centers_by_index.get(
                index,
                Point(
                    original_bounds.left + original_bounds.width / 2,
                    original_bounds.top + original_bounds.height / 2,
                ),
            )

            relative_x = (
                original_center.x - original_group.left
            ) / original_group.width
            relative_y = (
                original_center.y - original_group.top
            ) / original_group.height

            new_center = Point(
                left + relative_x * new_width,
                top + relative_y * new_height,
            )
            object_width = max(
                original_bounds.width * scale_x,
                self.MIN_OBJECT_SIZE_MM,
            )
            object_height = max(
                original_bounds.height * scale_y,
                self.MIN_OBJECT_SIZE_MM,
            )

            self._objects[index] = replace(
                graphic_object,
                bounds=Rect(
                    Point(
                        new_center.x - object_width / 2,
                        new_center.y - object_height / 2,
                    ),
                    Size(object_width, object_height),
                ),
            )

        self._shift_indices_inside_page(valid_indices)
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

        selected_object = self._objects[self._selected_object_index]
        if selected_object.locked:
            return

        if (
            selected_object.group_id is not None
            and self._interaction_original_bounds_by_index
        ):
            group_indices = sorted(
                self._expand_indices_to_groups(
                    self._selected_object_indices,
                )
            )
            group_ids = {
                self._objects[index].group_id
                for index in group_indices
                if 0 <= index < len(self._objects)
            }
            if len(group_ids) == 1 and None not in group_ids:
                self._resize_selected_group(
                    current,
                    group_indices,
                )
                return

        original = self._interaction_original_bounds
        handle = self._interaction_handle
        center = Point(
            original.left + original.width / 2,
            original.top + original.height / 2,
        )
        local_current = self._inverse_rotate_point(
            current,
            center,
            selected_object.rotation,
        )

        left = original.left
        top = original.top
        right = original.right
        bottom = original.bottom

        if "w" in handle:
            left = min(local_current.x, right - self.MIN_OBJECT_SIZE_MM)
        if "e" in handle:
            right = max(local_current.x, left + self.MIN_OBJECT_SIZE_MM)
        if "n" in handle:
            top = min(local_current.y, bottom - self.MIN_OBJECT_SIZE_MM)
        if "s" in handle:
            bottom = max(local_current.y, top + self.MIN_OBJECT_SIZE_MM)

        local_center = Point(
            (left + right) / 2,
            (top + bottom) / 2,
        )
        world_center = self._rotate_point(
            local_center,
            center,
            selected_object.rotation,
        )
        width = right - left
        height = bottom - top

        self._objects[self._selected_object_index] = replace(
            selected_object,
            bounds=Rect(
                Point(
                    world_center.x - width / 2,
                    world_center.y - height / 2,
                ),
                Size(width, height),
            ),
        )

        self.redraw()
        self._notify_selection()

    def _rotate_selection_to_pointer(
        self,
        current: Point,
        *,
        snap_to_15_degrees: bool,
    ) -> None:
        pivot = self._interaction_rotation_pivot
        start_angle = self._interaction_start_angle_deg
        if pivot is None or start_angle is None:
            return
        if not self._interaction_original_bounds_by_index:
            return

        current_angle = degrees(
            atan2(current.y - pivot.y, current.x - pivot.x)
        )
        delta = current_angle - start_angle
        if snap_to_15_degrees:
            delta = round(delta / 15.0) * 15.0

        for index, original_bounds in (
            self._interaction_original_bounds_by_index.items()
        ):
            if not 0 <= index < len(self._objects):
                continue
            graphic_object = self._objects[index]
            if graphic_object.locked:
                continue

            original_center = self._interaction_original_centers_by_index[index]
            rotated_center = self._rotate_point(
                original_center,
                pivot,
                delta,
            )
            original_rotation = (
                self._interaction_original_rotations_by_index[index]
            )

            self._objects[index] = replace(
                graphic_object,
                bounds=Rect(
                    Point(
                        rotated_center.x - original_bounds.width / 2,
                        rotated_center.y - original_bounds.height / 2,
                    ),
                    original_bounds.size,
                ),
                rotation=self._normalize_rotation(
                    original_rotation + delta
                ),
            )

        self._shift_indices_inside_page(
            self._interaction_original_bounds_by_index.keys()
        )
        self.redraw()
        self._notify_selection()

    def _event_to_page_mm_unbounded(self, event) -> Point:
        return Point(
            self.viewport.px_to_mm(event.x - self.page_left),
            self.viewport.px_to_mm(event.y - self.page_top),
        )

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

    def _activate_space_pan(
        self,
        _event=None,
    ) -> str:

        if self._text_editor is not None:
            return "break"

        self._space_pan_active = True
        if not self._dragging:
            self.configure(cursor="hand2")
        return "break"

    def _deactivate_space_pan(
        self,
        _event=None,
    ) -> str:

        self._space_pan_active = False
        if not self._left_pan_active:
            self.configure(cursor="")
        return "break"

    def _start_pan(
        self,
        event,
    ) -> None:

        self._dragging = True
        self.configure(cursor="fleur")

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
        self.configure(
            cursor="hand2" if self._space_pan_active else "",
        )

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