from __future__ import annotations

import tkinter as tk
from copy import deepcopy
from typing import Callable
from uuid import uuid4

from src.gui_v3 import theme


class TLScrollbar(tk.Canvas):
    """Curseur TomeLinea léger et indépendant du thème Windows."""

    def __init__(self, parent, *, orient: str, command):
        self.orient = orient
        self.command = command
        width = 12 if orient == "vertical" else 1
        height = 1 if orient == "vertical" else 12
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=theme.WINDOW_DEEP,
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )
        self._first = 0.0
        self._last = 1.0
        self._drag_offset = 0.0
        self._dragging = False
        self.bind("<Configure>", self._redraw)
        self.bind("<Button-1>", self._press)
        self.bind("<B1-Motion>", self._drag)
        self.bind("<ButtonRelease-1>", self._release)

    def set(self, first, last):
        try:
            self._first = max(0.0, min(1.0, float(first)))
            self._last = max(self._first, min(1.0, float(last)))
        except (TypeError, ValueError):
            self._first, self._last = 0.0, 1.0
        self._redraw()

    def _axis_length(self) -> int:
        return max(1, self.winfo_height() if self.orient == "vertical" else self.winfo_width())

    def _cross_length(self) -> int:
        return max(1, self.winfo_width() if self.orient == "vertical" else self.winfo_height())

    def _thumb_geometry(self) -> tuple[float, float]:
        length = self._axis_length()
        start = self._first * length
        end = self._last * length
        min_thumb = min(length, 28)
        if end - start < min_thumb:
            center = (start + end) / 2.0
            start = max(0.0, min(length - min_thumb, center - min_thumb / 2.0))
            end = min(length, start + min_thumb)
        return start, end

    def _redraw(self, _event=None):
        self.delete("all")
        length = self._axis_length()
        cross = self._cross_length()
        # Rail graphite, trait céladon et petite touche or rappelant la signature TomeLinea.
        if self.orient == "vertical":
            cx = cross / 2.0
            self.create_line(cx, 5, cx, max(5, length - 5), fill=theme.BORDER_SOFT, width=2)
        else:
            cy = cross / 2.0
            self.create_line(5, cy, max(5, length - 5), cy, fill=theme.BORDER_SOFT, width=2)

        if self._last >= 0.999 and self._first <= 0.001:
            return

        start, end = self._thumb_geometry()
        pad = 3
        if self.orient == "vertical":
            x1, x2 = pad, max(pad + 2, cross - pad)
            self.create_rectangle(x1, start, x2, end, fill=theme.ACCENT_DARK, outline=theme.ACCENT_BRIGHT, width=1)
            self.create_line(x1 + 1, start + 2, x2 - 1, start + 2, fill="#E7C37A", width=1)
        else:
            y1, y2 = pad, max(pad + 2, cross - pad)
            self.create_rectangle(start, y1, end, y2, fill=theme.ACCENT_DARK, outline=theme.ACCENT_BRIGHT, width=1)
            self.create_line(start + 2, y1 + 1, start + 2, y2 - 1, fill="#E7C37A", width=1)

    def _coord(self, event) -> float:
        return float(event.y if self.orient == "vertical" else event.x)

    def _press(self, event):
        if self._last >= 0.999 and self._first <= 0.001:
            return "break"
        pos = self._coord(event)
        start, end = self._thumb_geometry()
        if start <= pos <= end:
            self._dragging = True
            self._drag_offset = pos - start
        else:
            thumb = max(1.0, end - start)
            target = (pos - thumb / 2.0) / max(1.0, self._axis_length() - thumb)
            self.command("moveto", max(0.0, min(1.0, target)))
        return "break"

    def _drag(self, event):
        if not self._dragging:
            return "break"
        start, end = self._thumb_geometry()
        thumb = max(1.0, end - start)
        target = (self._coord(event) - self._drag_offset) / max(1.0, self._axis_length() - thumb)
        self.command("moveto", max(0.0, min(1.0, target)))
        return "break"

    def _release(self, _event=None):
        self._dragging = False
        return "break"


class BookCanvas(tk.Frame):
    """Zone B TomeLinea : structure du livre en deux niveaux, parties puis pages."""

    MIN_ZOOM = 20
    MAX_ZOOM = 800
    BASE_PAGE_W = 420
    BASE_PAGE_H = 594
    BASE_GAP = 34
    BASE_GROUP_GAP = 76
    MARGIN = 34
    GROUP_H = 58
    GROUP_TO_PAGE = 16
    EMPTY_SLOT_W = 260

    START_GROUP_ID = "debut_livre"
    DEFAULT_GROUP_ID = "pages_interieures"
    END_GROUP_ID = "fin_livre"

    GOLD = "#E7C37A"
    ORANGE = "#E47A45"
    BOOK_GREEN = "#86A98C"

    DEFAULT_GROUPS = (
        {
            "id": START_GROUP_ID,
            "title": "Début du livre",
            "part_title": "",
            "symbol": "flag",
            "accent": GOLD,
            "protected": True,
        },
        {
            "id": DEFAULT_GROUP_ID,
            "title": "Partie 1",
            "part_title": "",
            "symbol": "book",
            "accent": theme.ACCENT_BRIGHT,
            "protected": False,
        },
        {
            "id": END_GROUP_ID,
            "title": "Fin du livre",
            "part_title": "",
            "symbol": "book_end",
            "accent": BOOK_GREEN,
            "protected": True,
        },
    )

    COVER_TYPES = {"couverture", "cover", "front_cover"}
    BACK_COVER_TYPES = {"quatrieme", "quatrieme_couverture", "4e_couverture", "back_cover"}
    SECOND_COVER_TYPES = {
        "deuxieme_couverture", "2e_couverture", "second_cover", "inside_front_cover",
        "2e de couverture", "deuxieme de couverture", "deuxième de couverture",
    }
    THIRD_COVER_TYPES = {
        "troisieme_couverture", "3e_couverture", "third_cover", "inside_back_cover",
        "3e de couverture", "troisieme de couverture", "troisième de couverture",
    }

    # Défilement de bord volontairement progressif : précis près de la cible,
    # encore assez vif pour traverser une longue partie.
    AUTO_SCROLL_EDGE = 88
    AUTO_SCROLL_INTERVAL_MS = 46
    AUTO_SCROLL_MAX_SPEED = 3

    PAGE_SIZE_SMALL = 0.72
    PAGE_SIZE_MEDIUM = 0.90
    PAGE_SIZE_LARGE = 1.14
    PAGE_LABEL_H = 26

    def __init__(
        self,
        parent,
        *,
        on_open_item: Callable[[dict, int], None],
        on_change: Callable[[], None] | None = None,
        on_focus_change: Callable[[bool], None] | None = None,
    ):
        super().__init__(parent, bg=theme.PANEL)
        self.on_open_item = on_open_item
        self.on_change = on_change
        self.on_focus_change = on_focus_change
        self.project = None
        self.items: list[dict] = []
        self.groups: list[dict] = [dict(group) for group in self.DEFAULT_GROUPS]
        self._data: dict = {}

        self._selected_index: int | None = None
        self._selected_group_id: str | None = None
        self._page_hitboxes: dict[int, tuple[float, float, float, float]] = {}
        self._group_hitboxes: dict[str, tuple[float, float, float, float]] = {}
        self._group_page_bounds: dict[str, tuple[float, float]] = {}
        self._visual_indices: list[int] = []

        self._drag_kind: str | None = None
        self._drag_start_index: int | None = None
        self._drag_target_index: int | None = None
        self._drag_target_group_id: str | None = None
        self._drag_target_local_pos: int | None = None
        self._drag_group_id: str | None = None
        self._drag_group_target: int | None = None
        self._drag_start_xy: tuple[int, int] | None = None
        self._dragging = False
        self._drag_pointer_xy: tuple[int, int] | None = None
        self._drag_autoscroll_direction = 0
        self._drag_autoscroll_speed = 0
        self._drag_autoscroll_job = None
        self._render_pending = None
        self._page_focus = False
        self._book_zoom_cap = 100
        self._hover_index: int | None = None
        self._hover_group_id: str | None = None
        self._v_scroll_needed = False
        self._h_scroll_needed = False
        self._sticky_part_job = None
        self._title_editor = None
        self._title_editor_window = None
        self._editing_group_id: str | None = None

        self.zoom_var = tk.IntVar(value=36)
        self.zoom_text_var = tk.StringVar(value="36 %")
        self.status_var = tk.StringVar(value="Livre en attente")

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self._build_toolbar()
        self._build_canvas()

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def _build_toolbar(self):
        bar = tk.Frame(self, bg=theme.PANEL)
        bar.grid(row=0, column=0, sticky="ew", pady=(0, 7))
        bar.grid_columnconfigure(1, weight=1)

        tk.Label(
            bar,
            text="Structure du livre",
            bg=theme.PANEL,
            fg=theme.INK,
            font=(theme.FONT_TITLE, 13, "bold"),
        ).grid(row=0, column=0, sticky="w")

        tk.Label(
            bar,
            textvariable=self.status_var,
            bg=theme.PANEL,
            fg=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 8, "bold"),
        ).grid(row=0, column=1, sticky="w", padx=(16, 12))

        controls = tk.Frame(bar, bg=theme.PANEL)
        controls.grid(row=0, column=2, sticky="e")
        self._tool_button(controls, "−", lambda: self.step_zoom(-10), width=3).pack(side="left", padx=(0, 4))

        self.zoom_scale = tk.Scale(
            controls,
            from_=self.MIN_ZOOM,
            to=self.MAX_ZOOM,
            orient="horizontal",
            variable=self.zoom_var,
            command=self._on_scale,
            showvalue=False,
            length=175,
            resolution=1,
            bg=theme.PANEL,
            fg=theme.INK,
            troughcolor=theme.PANEL_SOFT,
            activebackground=theme.ACCENT,
            highlightthickness=0,
            bd=0,
            sliderrelief="flat",
        )
        self.zoom_scale.pack(side="left")
        self._tool_button(controls, "+", lambda: self.step_zoom(10), width=3).pack(side="left", padx=(4, 7))

        tk.Label(
            controls,
            textvariable=self.zoom_text_var,
            width=6,
            anchor="e",
            bg=theme.PANEL,
            fg=theme.INK,
            font=(theme.FONT_UI, 8, "bold"),
        ).pack(side="left", padx=(0, 8))

        self._tool_button(controls, "Tout le livre", self.fit_book).pack(side="left", padx=(0, 4))
        self._tool_button(controls, "Page", self.fit_selected).pack(side="left")

    def _tool_button(self, parent, text, command, width=None):
        return tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            bg=theme.PANEL_SOFT,
            fg=theme.INK,
            activebackground=theme.ACCENT_SOFT,
            activeforeground=theme.WHITE,
            relief="flat",
            bd=0,
            padx=8,
            pady=4,
            font=(theme.FONT_UI, 8, "bold"),
            cursor="hand2",
        )

    def _build_canvas(self):
        viewer = tk.Frame(self, bg=theme.WINDOW_DEEP)
        viewer.grid(row=1, column=0, sticky="nsew")
        viewer.grid_rowconfigure(0, weight=1)
        viewer.grid_columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            viewer,
            bg=theme.WINDOW_DEEP,
            bd=0,
            highlightthickness=0,
            cursor="arrow",
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.canvas._tl_item_hover_only = True

        self.v_scroll = TLScrollbar(viewer, orient="vertical", command=self.canvas.yview)
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll = TLScrollbar(viewer, orient="horizontal", command=self.canvas.xview)
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        self.canvas.configure(xscrollcommand=self._on_canvas_xview, yscrollcommand=self._on_canvas_yview)

        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_release)
        self.canvas.bind("<Double-Button-1>", self._on_double_click)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Shift-MouseWheel>", self._on_shift_mousewheel)
        self.canvas.bind("<Control-MouseWheel>", self._on_ctrl_mousewheel)
        self.canvas.bind("<Configure>", self._schedule_render)
        self.canvas.bind("<Motion>", self._on_hover_motion)
        self.canvas.bind("<Leave>", self._on_hover_leave)

    # ------------------------------------------------------------------
    # Projet / données
    # ------------------------------------------------------------------

    def set_project(self, project):
        self.project = project
        self.items = []
        self.groups = [dict(group) for group in self.DEFAULT_GROUPS]
        self._data = {}

        if project is not None:
            try:
                data = project.load_mockup()
                if not isinstance(data, dict):
                    data = {}
            except Exception:
                data = {}

            data, changed = self._ensure_minimum_structure(data)
            self._data = data
            self.groups = [dict(group) for group in data.get("groups", []) if isinstance(group, dict)]
            self.items = [dict(item) for item in data.get("items", []) if isinstance(item, dict)]
            if changed:
                try:
                    project.save_mockup(data)
                except Exception:
                    pass

        self._selected_index = 0 if self.items else None
        self._selected_group_id = None
        self._page_focus = False
        self.render()
        if self.items:
            self.after_idle(self._open_default_view)

    def _ensure_minimum_structure(self, source: dict) -> tuple[dict, bool]:
        data = deepcopy(source) if isinstance(source, dict) else {}
        changed = False

        defaults = {str(group["id"]): dict(group) for group in self.DEFAULT_GROUPS}
        raw_groups = data.get("groups", [])
        middle: list[dict] = []
        seen: set[str] = set()
        structural_titles: dict[str, str] = {}
        if isinstance(raw_groups, list):
            for raw in raw_groups:
                if not isinstance(raw, dict) or bool(raw.get("deleted", False)):
                    continue
                group_id = str(raw.get("id", "")).strip()
                if not group_id or group_id in seen:
                    continue
                if group_id in {self.START_GROUP_ID, self.END_GROUP_ID}:
                    structural_titles[group_id] = str(
                        raw.get("part_title") or raw.get("titre_partie") or raw.get("subtitle") or ""
                    ).strip()
                    seen.add(group_id)
                    continue
                title = str(raw.get("title") or raw.get("name") or "Partie").strip() or "Partie"
                part_title = str(
                    raw.get("part_title")
                    or raw.get("titre_partie")
                    or raw.get("subtitle")
                    or ""
                ).strip()
                accent = str(raw.get("accent") or theme.ACCENT_BRIGHT)
                middle.append(
                    {
                        **raw,
                        "id": group_id,
                        "title": title,
                        "part_title": part_title,
                        "symbol": str(raw.get("symbol") or "book"),
                        "accent": accent,
                        "protected": False,
                    }
                )
                seen.add(group_id)

        if self.DEFAULT_GROUP_ID not in seen:
            middle.insert(0, dict(defaults[self.DEFAULT_GROUP_ID]))

        start_group = dict(defaults[self.START_GROUP_ID])
        end_group = dict(defaults[self.END_GROUP_ID])
        if self.START_GROUP_ID in structural_titles:
            start_group["part_title"] = structural_titles[self.START_GROUP_ID]
        if self.END_GROUP_ID in structural_titles:
            end_group["part_title"] = structural_titles[self.END_GROUP_ID]
        groups = [start_group, *middle, end_group]
        if data.get("groups") != groups:
            data["groups"] = groups
            changed = True

        valid_group_ids = [str(group.get("id", "")) for group in groups]
        valid_group_set = set(valid_group_ids)
        page_type_group: dict[str, str] = {}
        raw_defs = data.get("page_types", [])
        if isinstance(raw_defs, list):
            for definition in raw_defs:
                if not isinstance(definition, dict):
                    continue
                page_type = str(definition.get("type", "")).strip()
                group_id = str(definition.get("group", "")).strip()
                if page_type and group_id in valid_group_set:
                    page_type_group[page_type] = group_id

        raw_items = data.get("items", [])
        items = [dict(item) for item in raw_items if isinstance(item, dict)] if isinstance(raw_items, list) else []

        cover = next((item for item in items if self._is_cover(item)), None)
        back = next((item for item in items if self._is_back_cover(item)), None)
        if cover is None:
            cover = {
                "id": f"MAQUETTE-{uuid4().hex[:12].upper()}",
                "type": "couverture",
                "title": "Couverture",
                "count": 1,
                "done": False,
                "plan_group": self.START_GROUP_ID,
            }
            items.insert(0, cover)
            changed = True
        if back is None:
            back = {
                "id": f"MAQUETTE-{uuid4().hex[:12].upper()}",
                "type": "quatrieme",
                "title": "Quatrième de couverture",
                "count": 1,
                "done": False,
                "plan_group": self.END_GROUP_ID,
            }
            items.append(back)
            changed = True

        for item in items:
            # Les anciens champs sont conservés, mais B n'affiche plus de catégorie
            # générique « Page intérieure ». Le libellé visible est le vrai type
            # éditorial (Sommaire, Texte, Illustration, Chapitre, etc.).
            if not str(item.get("attribute", "")).strip():
                item["attribute"] = self._legacy_page_attribute(item)
                changed = True

            old_group = str(item.get("plan_group", "")).strip()
            if self._is_cover(item) or self._is_second_cover(item):
                group_id = self.START_GROUP_ID
            elif self._is_third_cover(item) or self._is_back_cover(item):
                group_id = self.END_GROUP_ID
            elif old_group in valid_group_set:
                group_id = old_group
            else:
                page_type = str(item.get("type", "")).strip()
                group_id = page_type_group.get(page_type, self.DEFAULT_GROUP_ID)
                if group_id not in valid_group_set:
                    group_id = self.DEFAULT_GROUP_ID
            if old_group != group_id:
                item["plan_group"] = group_id
                changed = True

        ordered: list[dict] = []
        for group in groups:
            group_id = str(group.get("id", ""))
            grouped = [item for item in items if str(item.get("plan_group", "")) == group_id]
            if group_id == self.START_GROUP_ID:
                grouped.sort(key=self._start_group_sort_key)
            elif group_id == self.END_GROUP_ID:
                grouped.sort(key=self._end_group_sort_key)
            ordered.extend(grouped)

        # Conserve sans perte un éventuel item dont le groupe serait incohérent.
        known_ids = {id(item) for item in ordered}
        ordered.extend(item for item in items if id(item) not in known_ids)
        if ordered != items:
            changed = True
        data["items"] = ordered
        data.setdefault("page_types", [])
        data.setdefault("recto_verso_rules", [])
        return data, changed

    def _save_order(self):
        if self.project is None:
            return
        try:
            data = self.project.load_mockup()
        except Exception:
            data = deepcopy(self._data)
        if not isinstance(data, dict):
            data = {}
        data["groups"] = [dict(group) for group in self.groups]
        data["items"] = [dict(item) for item in self.items]
        data, _ = self._ensure_minimum_structure(data)
        self.groups = [dict(group) for group in data.get("groups", []) if isinstance(group, dict)]
        self.items = [dict(item) for item in data.get("items", []) if isinstance(item, dict)]
        self._data = data
        self.project.save_mockup(data)
        if self.on_change is not None:
            self.on_change()

    @staticmethod
    def _type_of(item: dict) -> str:
        return str(item.get("type") or item.get("kind") or item.get("page_type") or "").strip().lower()

    def _is_cover(self, item: dict) -> bool:
        return self._type_of(item) in self.COVER_TYPES

    def _is_back_cover(self, item: dict) -> bool:
        return self._type_of(item) in self.BACK_COVER_TYPES

    def _is_second_cover(self, item: dict) -> bool:
        return self._type_of(item) in self.SECOND_COVER_TYPES

    def _is_third_cover(self, item: dict) -> bool:
        return self._type_of(item) in self.THIRD_COVER_TYPES

    def _is_locked_page(self, item: dict) -> bool:
        return self._is_cover(item) or self._is_second_cover(item) or self._is_third_cover(item) or self._is_back_cover(item)

    def _start_group_sort_key(self, item: dict) -> tuple[int]:
        if self._is_cover(item):
            return (0,)
        if self._is_second_cover(item):
            return (1,)
        return (2,)

    def _end_group_sort_key(self, item: dict) -> tuple[int]:
        if self._is_back_cover(item):
            return (2,)
        if self._is_third_cover(item):
            return (1,)
        return (0,)

    def _item_group_id(self, item: dict) -> str:
        if self._is_cover(item) or self._is_second_cover(item):
            return self.START_GROUP_ID
        if self._is_third_cover(item) or self._is_back_cover(item):
            return self.END_GROUP_ID
        group_id = str(item.get("plan_group", "")).strip()
        valid = {str(group.get("id", "")) for group in self.groups}
        return group_id if group_id in valid else self.DEFAULT_GROUP_ID

    def _item_label(self, item: dict, index: int) -> str:
        for key in ("name", "nom", "title", "titre", "label", "type_name", "page_type_name"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        kind = item.get("type") or item.get("kind") or item.get("page_type")
        if isinstance(kind, str) and kind.strip():
            return kind.replace("_", " ").strip().capitalize()
        return f"Page {index + 1}"

    def _legacy_page_attribute(self, item: dict) -> str:
        """Déduit l'attribut éditorial d'un ancien item sans perdre son libellé."""
        if self._is_cover(item):
            return "1re de couverture"
        if self._is_second_cover(item):
            return "2e de couverture"
        if self._is_third_cover(item):
            return "3e de couverture"
        if self._is_back_cover(item):
            return "4e de couverture"
        for key in ("attribut", "role", "fonction", "title", "titre", "name", "nom", "label", "type_name", "page_type_name"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        kind = item.get("type") or item.get("kind") or item.get("page_type")
        if isinstance(kind, str) and kind.strip():
            return kind.replace("_", " ").strip().capitalize()
        return "À définir"

    def _page_type_label(self, item: dict, index: int | None = None) -> str:
        """Libellé éditorial visible sous la miniature, jamais une famille générique."""
        if self._is_cover(item):
            return "Couverture"
        if self._is_second_cover(item):
            return "2e de couverture"
        if self._is_third_cover(item):
            return "3e de couverture"
        if self._is_back_cover(item):
            return "4e de couverture"

        raw_type = self._type_of(item)
        aliases = {
            "text": "Texte", "texte": "Texte",
            "sommaire": "Sommaire", "toc": "Sommaire",
            "illustration": "Illustration", "image": "Illustration",
            "chapitre": "Chapitre", "chapter": "Chapitre",
            "annexe": "Annexe", "appendix": "Annexe",
            "titre": "Page de titre", "title_page": "Page de titre",
            "dedicace": "Dédicace", "dédicace": "Dédicace",
            "remerciements": "Remerciements",
            "blanche": "Page blanche", "blank": "Page blanche",
        }
        if raw_type in aliases:
            return aliases[raw_type]

        # Les projets existants portent souvent l'information utile dans
        # attribute/attribut/type_name. On la privilégie aux libellés techniques.
        for key in ("type_name", "page_type_name", "attribute", "attribut", "role", "fonction"):
            value = item.get(key)
            if isinstance(value, str) and value.strip():
                value = value.strip()
                if value.lower() not in {"page intérieure", "page interieur", "page interior"}:
                    return value
        if raw_type and raw_type not in {"page", "page_interieure", "page intérieure"}:
            return raw_type.replace("_", " ").strip().capitalize()
        if index is not None:
            label = self._item_label(item, index)
            if label:
                return label
        return "Page"

    def _page_attribute_label(self, item: dict, index: int) -> str:
        # Compatibilité avec les données V3 : l'attribut reste disponible pour
        # les futures fonctions métier mais n'est plus dupliqué sur la vignette.
        return self._page_type_label(item, index)

    @staticmethod
    def _group_name(group: dict) -> str:
        return str(group.get("title") or group.get("name") or "Partie").strip() or "Partie"

    @staticmethod
    def _group_part_title(group: dict) -> str:
        value = str(
            group.get("part_title")
            or group.get("titre_partie")
            or group.get("subtitle")
            or ""
        ).strip()
        return value or "Titre à définir"

    # ------------------------------------------------------------------
    # Zoom continu
    # ------------------------------------------------------------------

    @property
    def zoom(self) -> int:
        return max(self.MIN_ZOOM, min(self.MAX_ZOOM, int(self.zoom_var.get())))

    @property
    def page_focus(self) -> bool:
        return bool(self._page_focus)

    def _normal_page_available_height(self) -> int:
        if not hasattr(self, "canvas"):
            return 180
        viewport_h = max(180, self.canvas.winfo_height())
        reserved = self.MARGIN * 2 + self.GROUP_H + self.GROUP_TO_PAGE + self.PAGE_LABEL_H
        return max(120, viewport_h - reserved)

    def _book_height_cap(self) -> int:
        # Le plus grand des trois formats doit tenir entièrement dans B en vue livre.
        value = int(
            self._normal_page_available_height()
            / float(self.BASE_PAGE_H * self.PAGE_SIZE_LARGE)
            * 100
        )
        return max(self.MIN_ZOOM, min(self.MAX_ZOOM, value))

    def _open_default_view(self):
        """Ouverture confortable : pages plus grandes, sans forcer tout le livre à l'écran."""
        if not self.items or not self.canvas.winfo_exists():
            return
        # L'appel initial peut arriver avant que Tk ait attribué sa vraie hauteur à B.
        # On attend alors le premier vrai Configure au lieu de figer le zoom au minimum.
        if self.canvas.winfo_height() < 280:
            self.after(60, self._open_default_view)
            return
        if self._page_focus:
            self._set_page_focus(False)
        target = min(38, self._book_height_cap())
        self.set_zoom(max(self.MIN_ZOOM, target), center_selected=False)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)
        self.after_idle(self._update_visible_part_marker)

    def _active_group_id(self) -> str:
        if self._selected_group_id and any(str(g.get("id", "")) == self._selected_group_id for g in self.groups):
            return self._selected_group_id
        if self._selected_index is not None and 0 <= self._selected_index < len(self.items):
            return self._item_group_id(self.items[self._selected_index])
        return self.START_GROUP_ID

    def _page_size_factor(self, index: int, active_group_id: str | None = None) -> float:
        """Trois tailles : sélection, partie active, contexte."""
        active_group_id = active_group_id or self._active_group_id()
        group_id = self._item_group_id(self.items[index])
        if index == self._selected_index and group_id == active_group_id:
            return self.PAGE_SIZE_LARGE
        if group_id == active_group_id:
            return self.PAGE_SIZE_MEDIUM
        # Les couvertures extrêmes gardent une présence visuelle suffisante.
        if self._is_cover(self.items[index]) or self._is_back_cover(self.items[index]):
            return max(self.PAGE_SIZE_SMALL, 0.82)
        return self.PAGE_SIZE_SMALL

    def _set_page_focus(self, active: bool):
        active = bool(active)
        if active == self._page_focus:
            return
        if active and self._selected_index is None:
            if not self.items:
                return
            self._selected_index = 0
        self._page_focus = active
        if self.on_focus_change is not None:
            self.on_focus_change(active)

    def _on_scale(self, value):
        self.set_zoom(int(float(value)))

    def set_zoom(self, value: int, *, center_selected=True):
        requested = max(self.MIN_ZOOM, min(self.MAX_ZOOM, int(value)))
        if not self._page_focus:
            cap = self._book_height_cap()
            self._book_zoom_cap = cap
            if requested > cap and self._selected_index is not None:
                self._set_page_focus(True)
                value = requested
            else:
                value = min(requested, cap)
        else:
            if requested <= self._book_zoom_cap:
                self._set_page_focus(False)
                value = requested
            else:
                value = requested

        value = max(self.MIN_ZOOM, min(self.MAX_ZOOM, int(value)))
        if value == self.zoom and self.zoom_text_var.get() == f"{value} %":
            return
        self.zoom_var.set(value)
        self.zoom_text_var.set(f"{value} %")
        self.render()
        if center_selected and self._selected_index is not None:
            self.after_idle(self.center_selected)

    def step_zoom(self, delta: int):
        current = self.zoom
        if current < 100:
            step = 10
        elif current < 300:
            step = 25
        else:
            step = 50
        self.set_zoom(current + (step if delta > 0 else -step))

    def _logical_slots(self) -> int:
        count = 0
        for group in self.groups:
            group_id = str(group.get("id", ""))
            group_items = [item for item in self.items if self._item_group_id(item) == group_id]
            count += max(1, len(group_items))
        return max(1, count)

    def fit_book(self):
        if not self.items or not self.canvas.winfo_exists():
            return
        if self._page_focus:
            self._set_page_focus(False)
            self.after_idle(self.fit_book)
            return

        viewport_w = max(300, self.canvas.winfo_width() - 20)
        viewport_h = max(180, self.canvas.winfo_height() - 12)
        active_group_id = self._active_group_id()
        group_count = max(1, len(self.groups))

        logical_w = 0.0
        for group in self.groups:
            group_id = str(group.get("id", ""))
            indexes = self._group_items(group_id)
            if indexes:
                widths = [self.BASE_PAGE_W * self._page_size_factor(i, active_group_id) for i in indexes]
                logical_w += sum(widths) + self.BASE_GAP * max(0, len(indexes) - 1)
            else:
                logical_w += self.EMPTY_SLOT_W
        logical_w += self.BASE_GROUP_GAP * max(0, group_count - 1)

        logical_h = self.BASE_PAGE_H * self.PAGE_SIZE_LARGE + self.GROUP_H + self.GROUP_TO_PAGE + self.PAGE_LABEL_H
        zoom_x = int(viewport_w / max(1, logical_w + self.MARGIN * 2) * 100)
        zoom_y = int((viewport_h - self.GROUP_H - self.GROUP_TO_PAGE - self.MARGIN * 2 - self.PAGE_LABEL_H) / (self.BASE_PAGE_H * self.PAGE_SIZE_LARGE) * 100)
        self._book_zoom_cap = self._book_height_cap()
        value = max(self.MIN_ZOOM, min(self._book_zoom_cap, zoom_x, zoom_y))
        self.set_zoom(value, center_selected=False)
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

    def fit_selected(self):
        if self._selected_index is None:
            if self.items:
                self._selected_index = 0
            else:
                return
        if not self._page_focus:
            self._book_zoom_cap = self._book_height_cap()
            self._set_page_focus(True)
            self.after_idle(self.fit_selected)
            return

        viewport_w = max(300, self.canvas.winfo_width() - 70)
        viewport_h = max(180, self.canvas.winfo_height() - 70)
        zoom_x = int(viewport_w / self.BASE_PAGE_W * 100)
        zoom_y = int(viewport_h / self.BASE_PAGE_H * 100)
        value = max(self.MIN_ZOOM, min(self.MAX_ZOOM, zoom_x, zoom_y))
        self.set_zoom(value)

    def center_selected(self):
        index = self._selected_index
        if index is None or index not in self._page_hitboxes:
            return
        self.canvas.update_idletasks()
        x1, y1, x2, y2 = self._page_hitboxes[index]
        region = self.canvas.cget("scrollregion")
        if not region:
            return
        try:
            rx1, ry1, rx2, ry2 = map(float, str(region).split())
        except Exception:
            return
        total_w = max(1.0, rx2 - rx1)
        total_h = max(1.0, ry2 - ry1)
        view_w = max(1.0, self.canvas.winfo_width())
        view_h = max(1.0, self.canvas.winfo_height())
        target_left = ((x1 + x2) / 2.0) - view_w / 2.0
        target_top = ((y1 + y2) / 2.0) - view_h / 2.0
        if total_w > view_w + 2:
            self.canvas.xview_moveto(max(0.0, min(1.0, target_left / max(1.0, total_w - view_w))))
        else:
            self.canvas.xview_moveto(0)
        if total_h > view_h + 2:
            self.canvas.yview_moveto(max(0.0, min(1.0, target_top / max(1.0, total_h - view_h))))
        else:
            self.canvas.yview_moveto(0)

    # ------------------------------------------------------------------
    # Rendu
    # ------------------------------------------------------------------

    def _schedule_render(self, _event=None):
        if self._render_pending is not None:
            try:
                self.after_cancel(self._render_pending)
            except Exception:
                pass
        self._render_pending = self.after(35, self.render)

    def _group_items(self, group_id: str) -> list[int]:
        return [index for index, item in enumerate(self.items) if self._item_group_id(item) == group_id]

    def _draw_group_icon(self, x: float, y: float, kind: str, accent: str, *, tags=()):
        if kind == "flag":
            self.canvas.create_line(x - 7, y - 9, x - 7, y + 8, fill=self.GOLD, width=2, tags=tags)
            self.canvas.create_polygon(x - 6, y - 8, x + 7, y - 4, x - 6, y + 1, fill=self.ORANGE, outline=self.GOLD, width=1, tags=tags)
            return
        # Livre ouvert, dessiné comme le petit livre du monogramme : deux pages et une ligne centrale.
        self.canvas.create_polygon(x - 9, y - 6, x - 1, y - 3, x - 1, y + 7, x - 9, y + 4, fill="", outline=accent, width=2, tags=tags)
        self.canvas.create_polygon(x + 1, y - 3, x + 9, y - 6, x + 9, y + 4, x + 1, y + 7, fill="", outline=accent, width=2, tags=tags)
        self.canvas.create_line(x, y - 3, x, y + 7, fill=self.GOLD, width=1, tags=tags)
        if kind == "book_end":
            self.canvas.create_line(x - 8, y + 7, x + 8, y + 7, fill=self.ORANGE, width=1, tags=tags)

    def _draw_group_header(self, group: dict, x1: float, x2: float, y1: float, y2: float):
        group_id = str(group.get("id", ""))
        selected = group_id == self._selected_group_id
        hovered = group_id == self._hover_group_id and not self._dragging
        protected = group_id in {self.START_GROUP_ID, self.END_GROUP_ID} or bool(group.get("protected", False))
        accent = str(group.get("accent") or theme.ACCENT_BRIGHT)
        fill = theme.PANEL_ALT if not (selected or hovered) else theme.ACCENT_SOFT
        outline = self.GOLD if selected else (theme.ACCENT_BRIGHT if hovered else theme.BORDER_SOFT)
        width = 2 if selected or hovered else 1
        tag = (f"group:{group_id}", "group")

        self.canvas.create_rectangle(x1, y1, x2, y2, fill=fill, outline=outline, width=width, tags=tag)
        self.canvas.create_line(x1 + 1, y2 - 2, x2 - 1, y2 - 2, fill=accent, width=2, tags=tag)
        icon_x = x1 + 18
        icon_y = (y1 + y2) / 2.0
        kind = str(group.get("symbol") or "book")
        if group_id == self.START_GROUP_ID:
            kind = "flag"
        elif group_id == self.END_GROUP_ID:
            kind = "book_end"
        else:
            kind = "book"
        self._draw_group_icon(icon_x, icon_y, kind, accent, tags=tag)

        name = self._group_name(group)
        part_title = self._group_part_title(group)
        count = len(self._group_items(group_id))
        self.canvas.create_text(
            x1 + 34,
            icon_y - 8,
            anchor="w",
            text=name,
            fill=theme.INK,
            font=(theme.FONT_UI, 8, "bold"),
            tags=tag,
        )
        self.canvas.create_text(
            x1 + 34,
            icon_y + 7,
            anchor="w",
            text=part_title,
            fill=theme.ACCENT_BRIGHT if part_title != "Titre à définir" else theme.MUTED_DARK,
            font=(theme.FONT_UI, 6, "italic"),
            tags=tag,
        )
        self.canvas.create_text(
            x2 - 8,
            icon_y - 8,
            anchor="e",
            text=str(count),
            fill=theme.MUTED_DARK,
            font=(theme.FONT_UI, 6),
            tags=tag,
        )

    def _draw_waiting_slot(self, x1: float, y1: float, x2: float, y2: float, group: dict):
        accent = str(group.get("accent") or theme.ACCENT_BRIGHT)
        self.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill=theme.WINDOW_DEEP,
            outline=theme.BORDER,
            width=1,
            dash=(6, 5),
            tags=("waiting",),
        )
        cx = (x1 + x2) / 2.0
        cy = (y1 + y2) / 2.0
        self._draw_group_icon(cx, cy - 18, "book", accent, tags=("waiting",))
        self.canvas.create_text(
            cx,
            cy + 5,
            text="Pages à ajouter",
            fill=theme.MUTED,
            font=(theme.FONT_UI, 8, "bold"),
            tags=("waiting",),
        )
        self.canvas.create_text(
            cx,
            cy + 23,
            text="Le livre attend son contenu",
            fill=theme.MUTED_DARK,
            font=(theme.FONT_UI, 7),
            tags=("waiting",),
        )

    def _draw_type_preview(self, item: dict, x: float, y: float, w: float, h: float, label: str, scale: float):
        """Miniature symbolique du type de page, lisible même à faible zoom."""
        inset = max(5, min(18, int(18 * scale)))
        x1, y1, x2, y2 = x + inset, y + inset * 1.4, x + w - inset, y + h - inset * 1.5
        if x2 <= x1 or y2 <= y1:
            return
        low = label.lower()
        line = "#8B918F"
        accent = self.GOLD if self._is_locked_page(item) else theme.ACCENT_DARK

        if "couverture" in low:
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#263833", outline=accent, width=max(1, int(2 * scale)))
            cx, cy = (x1 + x2) / 2.0, (y1 + y2) / 2.0
            self._draw_group_icon(cx, cy - max(4, 12 * scale), "book", self.GOLD)
            self.canvas.create_line(x1 + 8, y2 - max(12, 22 * scale), x2 - 8, y2 - max(12, 22 * scale), fill=self.GOLD, width=1)
            return
        if "illustration" in low or "image" in low:
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#DDE5E1", outline="#BFC9C5", width=1)
            horizon = y1 + (y2 - y1) * 0.68
            self.canvas.create_polygon(x1, horizon, x1 + (x2 - x1) * .28, y1 + (y2 - y1) * .42, x1 + (x2 - x1) * .48, horizon, fill="#A6B8AF", outline="")
            self.canvas.create_polygon(x1 + (x2 - x1) * .30, horizon, x1 + (x2 - x1) * .65, y1 + (y2 - y1) * .30, x2, horizon, fill="#8FA79B", outline="")
            self.canvas.create_oval(x2 - max(10, 24 * scale), y1 + max(5, 10 * scale), x2 - max(4, 10 * scale), y1 + max(11, 24 * scale), fill="#D7BE7C", outline="")
            return
        if "sommaire" in low:
            title_y = y1 + max(4, 8 * scale)
            self.canvas.create_line(x1 + 4, title_y, x2 - 4, title_y, fill=accent, width=2)
            rows = 5
            for r in range(rows):
                yy = y1 + (y2 - y1) * (0.26 + r * 0.12)
                self.canvas.create_line(x1 + 5, yy, x2 - 16, yy, fill=line, width=1)
                self.canvas.create_oval(x2 - 10, yy - 1, x2 - 8, yy + 1, fill=accent, outline="")
            return
        if "chapitre" in low or "titre" in low:
            cx = (x1 + x2) / 2.0
            self.canvas.create_text(cx, y1 + (y2 - y1) * .30, text="CH.", fill="#59615F", font=(theme.FONT_TITLE, max(7, int(10 * scale)), "bold"))
            self.canvas.create_line(x1 + (x2 - x1) * .22, y1 + (y2 - y1) * .48, x2 - (x2 - x1) * .22, y1 + (y2 - y1) * .48, fill=accent, width=2)
            self.canvas.create_line(x1 + (x2 - x1) * .32, y1 + (y2 - y1) * .62, x2 - (x2 - x1) * .32, y1 + (y2 - y1) * .62, fill=line, width=1)
            return
        if "annexe" in low or "carte" in low:
            self.canvas.create_rectangle(x1, y1, x2, y2, fill="#E6E8E3", outline="#C8CEC9", width=1)
            for frac in (.28, .52, .74):
                xx = x1 + (x2 - x1) * frac
                self.canvas.create_line(xx, y1 + 4, xx - 5, y2 - 4, fill="#A5AAA6", width=1)
            self.canvas.create_line(x1 + 5, y2 - 8, x1 + (x2 - x1) * .42, y1 + (y2 - y1) * .44, x2 - 5, y1 + 10, fill=accent, width=2, smooth=True)
            return

        # Texte et types inconnus : une vraie silhouette de mise en page, pas un mot au centre.
        first = True
        yy = y1 + max(4, 8 * scale)
        step = max(4, 10 * scale)
        while yy < y2 - 3:
            left = x1 + (10 if first else 3)
            right = x2 - (max(7, 16 * scale) if int((yy - y1) / step) % 4 == 3 else 3)
            self.canvas.create_line(left, yy, right, yy, fill=line, width=1)
            first = False
            yy += step

    def _draw_page(self, index: int, x: float, y: float, page_w: float, page_h: float, scale: float, *, show_label: bool = True):
        item = self.items[index]
        selected = index == self._selected_index
        hovered = index == self._hover_index and not self._dragging
        if selected:
            fill = "#EDF1EE"
            outline = self.GOLD if hovered else theme.ACCENT
            outline_width = 4 if hovered else 3
        elif hovered:
            fill = "#F0F3F1"
            outline = theme.ACCENT_BRIGHT
            outline_width = 2
        else:
            fill = "#F0F1EE"
            outline = "#D5D7D3"
            outline_width = 1

        shadow = max(1, min(10, int(3 * scale)))
        self.canvas.create_rectangle(x + shadow, y + shadow, x + page_w + shadow, y + page_h + shadow, fill="#151B21", outline="")
        self.canvas.create_rectangle(x, y, x + page_w, y + page_h, fill=fill, outline=outline, width=outline_width)

        rail_h = max(2, min(9, int(5 * scale)))
        top_pad = max(2, 8 * scale)
        rail_color = self.GOLD if self._is_locked_page(item) else theme.ACCENT_DARK
        self.canvas.create_rectangle(x + top_pad, y + top_pad, x + page_w - top_pad, y + top_pad + rail_h, fill=rail_color, outline="")

        page_type = self._page_type_label(item, index)
        self._draw_type_preview(item, x, y, page_w, page_h, page_type, scale)

        if page_w >= 34:
            number_size = max(6, min(18, int(6 + self.zoom / 65)))
            self.canvas.create_text(
                x + page_w - max(8, 13 * scale),
                y + page_h - max(7, 12 * scale),
                anchor="se",
                text=str(index + 1),
                fill="#737B78",
                font=(theme.FONT_UI, number_size),
            )

        if show_label:
            label_size = max(6, min(15, int(7 + self.zoom / 80)))
            self.canvas.create_text(
                x + page_w / 2.0,
                y + page_h + max(9, 14 * scale),
                anchor="n",
                text=page_type,
                fill=theme.INK,
                width=max(50, page_w + 26),
                font=(theme.FONT_UI, label_size, "bold" if selected else "normal"),
                justify="center",
            )
        self._page_hitboxes[index] = (x, y, x + page_w, y + page_h)

    def render(self):
        self._render_pending = None
        if not hasattr(self, "canvas"):
            return

        viewport_w = max(300, self.canvas.winfo_width())
        viewport_h = max(180, self.canvas.winfo_height())
        self._close_title_editor(commit=True)
        self.canvas.delete("all")
        self._page_hitboxes = {}
        self._group_hitboxes = {}
        self._group_page_bounds = {}
        self._visual_indices = []

        if not self._page_focus:
            cap = self._book_height_cap()
            self._book_zoom_cap = cap
            if self.zoom > cap:
                self.zoom_var.set(cap)
        self.zoom_text_var.set(f"{self.zoom} %")

        if not self.items:
            self.status_var.set("Aucun projet chargé")
            self.canvas.create_text(viewport_w / 2, viewport_h / 2, text="Ouvrez un projet pour afficher son livre.", fill=theme.MUTED, font=(theme.FONT_UI, 10))
            self.canvas.configure(scrollregion=(0, 0, viewport_w, viewport_h))
            self._update_scrollbars(viewport_w, viewport_h)
            return

        if self._selected_index is None or not (0 <= self._selected_index < len(self.items)):
            self._selected_index = 0

        selected_page_number = self._selected_index + 1
        middle_count = sum(1 for group in self.groups if str(group.get("id", "")) not in {self.START_GROUP_ID, self.END_GROUP_ID})
        if self._page_focus:
            self.status_var.set(f"Page {selected_page_number} sur {len(self.items)}  •  travail détaillé")
        else:
            self.status_var.set(f"{middle_count} partie{'s' if middle_count != 1 else ''}  •  {len(self.items)} page{'s' if len(self.items) != 1 else ''}")

        scale = self.zoom / 100.0
        gap = max(8, self.BASE_GAP * scale)
        group_gap = max(20, self.BASE_GROUP_GAP * scale)
        margin = max(20, self.MARGIN * min(scale, 1.0))

        if self._page_focus:
            page_w = max(16, self.BASE_PAGE_W * scale)
            page_h = max(22, self.BASE_PAGE_H * scale)
            total_w = max(viewport_w, page_w + margin * 2)
            total_h = max(viewport_h, page_h + self.PAGE_LABEL_H + margin * 2)
            x = max(margin, (total_w - page_w) / 2.0)
            y = max(margin, (total_h - page_h - self.PAGE_LABEL_H) / 2.0)
            self._draw_page(self._selected_index, x, y, page_w, page_h, scale)
        else:
            active_group_id = self._active_group_id()
            specs: dict[int, tuple[float, float]] = {}
            for index in range(len(self.items)):
                factor = self._page_size_factor(index, active_group_id)
                specs[index] = (
                    max(16, self.BASE_PAGE_W * scale * factor),
                    max(22, self.BASE_PAGE_H * scale * factor),
                )

            # On calcule d'abord toutes les largeurs pour pouvoir centrer un livre court.
            group_layout: list[tuple[dict, list[int], float]] = []
            for group in self.groups:
                group_id = str(group.get("id", ""))
                indexes = self._group_items(group_id)
                if indexes:
                    body_w = sum(specs[i][0] for i in indexes) + gap * max(0, len(indexes) - 1)
                else:
                    body_w = max(90, self.EMPTY_SLOT_W * scale)
                min_header = max(150, min(300, 174 + max(len(self._group_name(group)), len(self._group_part_title(group))) * 2))
                group_layout.append((group, indexes, max(body_w, min_header)))

            content_w = sum(width for _g, _i, width in group_layout) + group_gap * max(0, len(group_layout) - 1)
            x = margin if content_w + margin * 2 > viewport_w else (viewport_w - content_w) / 2.0
            group_y1 = margin
            group_y2 = group_y1 + self.GROUP_H

            max_page_h = max((h for _w, h in specs.values()), default=self.BASE_PAGE_H * scale)
            row_needed = max_page_h + self.PAGE_LABEL_H
            available_top = group_y2 + self.GROUP_TO_PAGE
            available_h = max(0, viewport_h - available_top - margin)
            page_row_top = available_top + max(0, (available_h - row_needed) / 2.0)
            page_bottom = page_row_top + row_needed

            for group_pos, (group, indexes, group_width) in enumerate(group_layout):
                group_id = str(group.get("id", ""))
                start_x = x
                cursor_x = start_x
                if indexes:
                    for local_pos, index in enumerate(indexes):
                        self._visual_indices.append(index)
                        page_w, page_h = specs[index]
                        page_y = page_row_top + (max_page_h - page_h)
                        self._draw_page(index, cursor_x, page_y, page_w, page_h, scale)
                        cursor_x += page_w
                        if local_pos < len(indexes) - 1:
                            cursor_x += gap
                else:
                    empty_w = max(90, self.EMPTY_SLOT_W * scale)
                    if group_id not in {self.START_GROUP_ID, self.END_GROUP_ID}:
                        slot_h = min(max_page_h, max(100, self.BASE_PAGE_H * scale * self.PAGE_SIZE_SMALL))
                        slot_y = page_row_top + (max_page_h - slot_h)
                        self._draw_waiting_slot(cursor_x, slot_y, cursor_x + empty_w, slot_y + slot_h, group)
                    cursor_x += empty_w

                end_x = start_x + group_width
                self._group_hitboxes[group_id] = (start_x, group_y1, end_x, group_y2)
                self._group_page_bounds[group_id] = (start_x, end_x)
                self._draw_group_header(group, start_x, end_x, group_y1, group_y2)
                x = end_x
                if group_pos < len(group_layout) - 1:
                    separator_x = x + group_gap / 2.0
                    self.canvas.create_line(separator_x, group_y1 + 4, separator_x, page_row_top + max_page_h, fill=theme.BORDER_SOFT, width=1, dash=(3, 5))
                    x += group_gap

            total_w = max(viewport_w, content_w + margin * 2)
            required_h = page_bottom + margin
            total_h = viewport_h if required_h <= viewport_h + 1 else required_h

        self.canvas.configure(scrollregion=(0, 0, total_w, total_h))
        self._update_scrollbars(total_w, total_h)

        if self._dragging and not self._page_focus:
            if self._drag_kind == "group" and self._drag_group_target is not None:
                self._draw_group_drop_indicator(self._drag_group_target)
            elif self._drag_kind == "page" and self._drag_target_group_id is not None:
                self._draw_page_drop_indicator()

        self.after_idle(self._update_visible_part_marker)

    def _update_scrollbars(self, total_w: float, total_h: float):
        view_w = max(1, self.canvas.winfo_width())
        view_h = max(1, self.canvas.winfo_height())
        need_h = total_w > view_w + 2
        need_v = total_h > view_h + 2

        if need_h != self._h_scroll_needed:
            self._h_scroll_needed = need_h
            if need_h:
                self.h_scroll.grid()
            else:
                self.h_scroll.grid_remove()
                self.canvas.xview_moveto(0)
        if need_v != self._v_scroll_needed:
            self._v_scroll_needed = need_v
            if need_v:
                self.v_scroll.grid()
            else:
                self.v_scroll.grid_remove()
                self.canvas.yview_moveto(0)

    # ------------------------------------------------------------------
    # Repère de partie et édition directe du titre
    # ------------------------------------------------------------------

    def _on_canvas_xview(self, first, last):
        self.h_scroll.set(first, last)
        if self._sticky_part_job is None:
            self._sticky_part_job = self.after_idle(self._update_visible_part_marker)

    def _on_canvas_yview(self, first, last):
        self.v_scroll.set(first, last)
        if self._sticky_part_job is None:
            self._sticky_part_job = self.after_idle(self._update_visible_part_marker)

    def _visible_group_id(self) -> str:
        if not self._group_page_bounds or self._page_focus:
            return self._active_group_id()
        center_x = self.canvas.canvasx(max(1, self.canvas.winfo_width()) / 2.0)
        return self._group_id_at_x(center_x)

    def _update_visible_part_marker(self):
        """Repère fixe dans la barre de B : la partie sous le centre de la vue."""
        self._sticky_part_job = None
        if not hasattr(self, "canvas") or not self.canvas.winfo_exists() or not self.groups:
            return
        if self._page_focus:
            if self._selected_index is not None:
                self.status_var.set(f"Page {self._selected_index + 1} sur {len(self.items)}  •  travail détaillé")
            return
        group_id = self._visible_group_id()
        group = next((g for g in self.groups if str(g.get("id", "")) == group_id), None)
        if group is None:
            return
        name = self._group_name(group)
        title = self._group_part_title(group)
        self.status_var.set(f"Partie visible  •  {name} — {title}")

    def _group_id_from_current_tags(self) -> str | None:
        current = self.canvas.find_withtag("current")
        if not current:
            return None
        for tag in self.canvas.gettags(current[-1]):
            if tag.startswith("group:"):
                return tag.split(":", 1)[1]
            if tag.startswith("sticky_group:"):
                return tag.split(":", 1)[1]
        return None

    def _begin_group_title_edit(self, group_id: str):
        group = next((g for g in self.groups if str(g.get("id", "")) == group_id), None)
        box = self._group_hitboxes.get(group_id)
        if group is None or box is None:
            return
        self._close_title_editor(commit=True)

        view_left = self.canvas.canvasx(0)
        view_right = self.canvas.canvasx(max(1, self.canvas.winfo_width()))
        visible_left = max(box[0], view_left + 10)
        visible_right = min(box[2], view_right - 10)
        if visible_right - visible_left < 120:
            visible_left = max(box[0], view_left + 10)
            visible_right = min(box[2], visible_left + 220)

        entry = tk.Entry(
            self.canvas,
            bg=theme.PANEL_ALT, fg=theme.INK, insertbackground=self.GOLD,
            selectbackground=theme.ACCENT_DARK, selectforeground=theme.WHITE,
            relief="flat", bd=0, font=(theme.FONT_UI, 9, "bold"),
        )
        value = str(group.get("part_title") or group.get("titre_partie") or group.get("subtitle") or "").strip()
        entry.insert(0, value)
        world_x = visible_left + 35
        world_y = box[1] + self.GROUP_H - 17
        width = max(110, min(260, visible_right - world_x - 8))
        window = self.canvas.create_window(world_x, world_y, anchor="w", window=entry, width=width, height=22, tags=("title_editor",))
        self._title_editor = entry
        self._title_editor_window = window
        self._editing_group_id = group_id
        entry.bind("<Return>", lambda _e: self._close_title_editor(commit=True))
        entry.bind("<Escape>", lambda _e: self._close_title_editor(commit=False))
        entry.bind("<FocusOut>", lambda _e: self._close_title_editor(commit=True))
        entry.focus_set()
        entry.selection_range(0, "end")

    def _close_title_editor(self, *, commit: bool):
        entry = self._title_editor
        group_id = self._editing_group_id
        window = self._title_editor_window
        if entry is None:
            return
        value = entry.get().strip() if commit else None
        self._title_editor = None
        self._title_editor_window = None
        self._editing_group_id = None
        try:
            if window is not None:
                self.canvas.delete(window)
            entry.destroy()
        except Exception:
            pass
        if commit and group_id is not None:
            group = next((g for g in self.groups if str(g.get("id", "")) == group_id), None)
            if group is not None:
                group["part_title"] = value or ""
                self._selected_group_id = group_id
                self._save_order()
                self.after_idle(self.render)

    # ------------------------------------------------------------------
    # Sélection / glisser-déposer
    # ------------------------------------------------------------------

    def _index_at(self, event) -> int | None:
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        for index, (x1, y1, x2, y2) in self._page_hitboxes.items():
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                return index
        return None

    def _group_at(self, event) -> str | None:
        cx = self.canvas.canvasx(event.x)
        cy = self.canvas.canvasy(event.y)
        for group_id, (x1, y1, x2, y2) in self._group_hitboxes.items():
            if x1 <= cx <= x2 and y1 <= cy <= y2:
                return group_id
        return None

    def _group_id_at_x(self, canvas_x: float) -> str:
        """Retourne la partie correspondant à x, y compris dans les espaces entre parties."""
        if not self._group_page_bounds:
            return self.DEFAULT_GROUP_ID
        ordered = []
        for group in self.groups:
            group_id = str(group.get("id", ""))
            bounds = self._group_page_bounds.get(group_id)
            if bounds is not None:
                ordered.append((group_id, bounds[0], bounds[1]))
        if not ordered:
            return self.DEFAULT_GROUP_ID
        if canvas_x <= ordered[0][1]:
            return ordered[0][0]
        for pos, (group_id, x1, x2) in enumerate(ordered):
            if x1 <= canvas_x <= x2:
                return group_id
            if pos < len(ordered) - 1:
                next_id, next_x1, _next_x2 = ordered[pos + 1]
                boundary = (x2 + next_x1) / 2.0
                if canvas_x < boundary:
                    return group_id
                if canvas_x < next_x1:
                    return next_id
        return ordered[-1][0]

    def _target_local_pos_from_x(self, canvas_x: float, group_id: str, *, dragged_index: int | None = None) -> int:
        indexes = self._group_items(group_id)
        # Pendant le déplacement dans la même partie, on raisonne comme si la page déplacée
        # avait déjà été retirée. La position visuelle reste alors symétrique dans les deux sens.
        visible_indexes = [index for index in indexes if index != dragged_index]
        pos = 0
        for index in visible_indexes:
            box = self._page_hitboxes.get(index)
            if box is None:
                continue
            if canvas_x < (box[0] + box[2]) / 2.0:
                return pos
            pos += 1
        return pos

    def _refresh_drag_target(self):
        if not self._dragging or self._drag_pointer_xy is None:
            return
        pointer_x, _pointer_y = self._drag_pointer_xy
        canvas_x = self.canvas.canvasx(pointer_x)
        if self._drag_kind == "group":
            self._drag_group_target = self._target_movable_group_index(canvas_x)
        elif self._drag_kind == "page" and self._drag_start_index is not None:
            group_id = self._group_id_at_x(canvas_x)
            self._drag_target_group_id = group_id
            self._drag_target_local_pos = self._target_local_pos_from_x(
                canvas_x,
                group_id,
                dragged_index=self._drag_start_index,
            )

    def _redraw_drop_indicator_only(self):
        self.canvas.delete("drop_indicator")
        if not self._dragging or self._page_focus:
            return
        if self._drag_kind == "group" and self._drag_group_target is not None:
            self._draw_group_drop_indicator(self._drag_group_target)
        elif self._drag_kind == "page" and self._drag_target_group_id is not None:
            self._draw_page_drop_indicator()

    def _set_drag_autoscroll(self, pointer_x: int):
        if not self._dragging or not self._h_scroll_needed:
            self._drag_autoscroll_direction = 0
            self._drag_autoscroll_speed = 0
            self._cancel_drag_autoscroll()
            return
        width = max(1, self.canvas.winfo_width())
        edge = min(self.AUTO_SCROLL_EDGE, max(36, width // 5))
        direction = 0
        speed = 0
        if pointer_x < edge:
            direction = -1
            proximity = max(0.0, min(1.0, (edge - pointer_x) / edge))
            speed = 1 + int((proximity ** 1.8) * (self.AUTO_SCROLL_MAX_SPEED - 1))
        elif pointer_x > width - edge:
            direction = 1
            proximity = max(0.0, min(1.0, (pointer_x - (width - edge)) / edge))
            speed = 1 + int((proximity ** 1.8) * (self.AUTO_SCROLL_MAX_SPEED - 1))
        self._drag_autoscroll_direction = direction
        self._drag_autoscroll_speed = speed
        if direction == 0:
            self._cancel_drag_autoscroll()
        elif self._drag_autoscroll_job is None:
            self._drag_autoscroll_job = self.after(self.AUTO_SCROLL_INTERVAL_MS, self._drag_autoscroll_tick)

    def _cancel_drag_autoscroll(self):
        job = self._drag_autoscroll_job
        self._drag_autoscroll_job = None
        if job is not None:
            try:
                self.after_cancel(job)
            except Exception:
                pass

    def _drag_autoscroll_tick(self):
        self._drag_autoscroll_job = None
        if not self._dragging or self._drag_autoscroll_direction == 0 or not self._h_scroll_needed:
            return
        first, last = self.canvas.xview()
        direction = self._drag_autoscroll_direction
        if (direction < 0 and first <= 0.0001) or (direction > 0 and last >= 0.9999):
            return
        self.canvas.xview_scroll(direction * max(1, self._drag_autoscroll_speed), "units")
        self._refresh_drag_target()
        self._redraw_drop_indicator_only()
        self._drag_autoscroll_job = self.after(self.AUTO_SCROLL_INTERVAL_MS, self._drag_autoscroll_tick)

    def _on_hover_motion(self, event):
        if self._dragging or (getattr(event, "state", 0) & 0x0100):
            return
        index = self._index_at(event)
        group_id = None if index is not None else self._group_at(event)
        cursor = "hand2" if index is not None or group_id is not None else "arrow"
        self.canvas.configure(cursor=cursor)
        if index == self._hover_index and group_id == self._hover_group_id:
            return
        self._hover_index = index
        self._hover_group_id = group_id
        self.render()

    def _on_hover_leave(self, _event=None):
        if self._hover_index is None and self._hover_group_id is None:
            return
        self._hover_index = None
        self._hover_group_id = None
        try:
            self.canvas.configure(cursor="arrow")
        except Exception:
            pass
        self.render()

    def _on_press(self, event):
        if self._page_focus:
            index = self._index_at(event)
            if index is not None:
                self._selected_index = index
                self.render()
            return "break"

        group_id = self._group_at(event)
        index = self._index_at(event)
        self._drag_start_xy = (event.x, event.y)
        self._dragging = False
        self._drag_target_index = None
        self._drag_target_group_id = None
        self._drag_target_local_pos = None
        self._drag_group_target = None
        self._drag_pointer_xy = (event.x, event.y)
        self._drag_autoscroll_direction = 0
        self._drag_autoscroll_speed = 0
        self._cancel_drag_autoscroll()

        if group_id is not None:
            self._selected_group_id = group_id
            self._selected_index = self._selected_index
            if group_id not in {self.START_GROUP_ID, self.END_GROUP_ID}:
                self._drag_kind = "group"
                self._drag_group_id = group_id
                self._drag_group_target = self._movable_group_ids().index(group_id) if group_id in self._movable_group_ids() else None
            else:
                self._drag_kind = None
                self._drag_group_id = None
            self.render()
            return "break"

        self._selected_group_id = None
        self._drag_kind = "page" if index is not None else None
        self._drag_start_index = index
        if index is not None:
            self._selected_index = index
            self._selected_group_id = self._item_group_id(self.items[index])
            self._drag_target_index = index
            self._drag_target_group_id = self._item_group_id(self.items[index])
            group_indexes = self._group_items(self._drag_target_group_id)
            self._drag_target_local_pos = group_indexes.index(index) if index in group_indexes else 0
            self.render()
        return "break"

    def _movable_group_ids(self) -> list[str]:
        return [str(group.get("id", "")) for group in self.groups if str(group.get("id", "")) not in {self.START_GROUP_ID, self.END_GROUP_ID}]

    def _on_drag(self, event):
        if self._drag_kind is None or self._drag_start_xy is None:
            return "break"
        self._drag_pointer_xy = (event.x, event.y)
        dx = abs(event.x - self._drag_start_xy[0])
        dy = abs(event.y - self._drag_start_xy[1])
        if not self._dragging and max(dx, dy) < 6:
            return "break"

        if self._drag_kind == "page" and self._drag_start_index is not None:
            if self._is_locked_page(self.items[self._drag_start_index]):
                self._dragging = False
                self._cancel_drag_autoscroll()
                return "break"

        self._dragging = True
        self._refresh_drag_target()
        self._set_drag_autoscroll(event.x)
        self.render()
        return "break"

    def _target_movable_group_index(self, canvas_x: float) -> int:
        ids = self._movable_group_ids()
        if not ids:
            return 0
        for pos, group_id in enumerate(ids):
            box = self._group_hitboxes.get(group_id)
            if box and canvas_x < (box[0] + box[2]) / 2.0:
                return pos
        return len(ids)

    def _target_index_from_x(self, canvas_x: float, group_id: str) -> int:
        indexes = self._group_items(group_id)
        if not indexes:
            # Insertion à la frontière du groupe : avant le premier groupe suivant.
            group_order = [str(group.get("id", "")) for group in self.groups]
            pos = group_order.index(group_id) if group_id in group_order else 0
            following = set(group_order[pos + 1 :])
            for index, item in enumerate(self.items):
                if self._item_group_id(item) in following:
                    return index
            return len(self.items)
        for index in indexes:
            box = self._page_hitboxes.get(index)
            if box and canvas_x < (box[0] + box[2]) / 2.0:
                return index
        return indexes[-1] + 1

    def _draw_group_drop_indicator(self, target: int):
        ids = self._movable_group_ids()
        if not ids:
            return
        if target >= len(ids):
            box = self._group_hitboxes.get(ids[-1])
            x = (box[2] + 12) if box else 0
        else:
            box = self._group_hitboxes.get(ids[target])
            x = (box[0] - 12) if box else 0
        y1 = min(box_[1] for box_ in self._group_hitboxes.values()) if self._group_hitboxes else 0
        y2 = max((box_[3] for box_ in self._page_hitboxes.values()), default=y1 + 100)
        self.canvas.create_line(x, y1 - 3, x, y2 + 6, fill=self.GOLD, width=4, tags=("drop_indicator",))

    def _draw_page_drop_indicator(self):
        group_id = self._drag_target_group_id
        local_pos = self._drag_target_local_pos
        if group_id is None or local_pos is None:
            return
        group_indexes = self._group_items(group_id)
        if self._drag_start_index in group_indexes:
            group_indexes = [index for index in group_indexes if index != self._drag_start_index]
        y1 = min((box[1] for box in self._page_hitboxes.values()), default=self.MARGIN + self.GROUP_H)
        y2 = max((box[3] for box in self._page_hitboxes.values()), default=y1 + 100)
        if local_pos < len(group_indexes) and group_indexes[local_pos] in self._page_hitboxes:
            x = self._page_hitboxes[group_indexes[local_pos]][0] - 7
        elif group_indexes and group_indexes[-1] in self._page_hitboxes:
            x = self._page_hitboxes[group_indexes[-1]][2] + 7
        else:
            bounds = self._group_page_bounds.get(group_id)
            x = bounds[0] + 6 if bounds else 0
        self.canvas.create_line(x, y1 - 8, x, y2 + 8, fill=self.GOLD, width=4, tags=("drop_indicator",))

    def _reorder_items_by_group_order(self):
        ordered: list[dict] = []
        for group in self.groups:
            group_id = str(group.get("id", ""))
            grouped = [item for item in self.items if self._item_group_id(item) == group_id]
            if group_id == self.START_GROUP_ID:
                grouped.sort(key=self._start_group_sort_key)
            elif group_id == self.END_GROUP_ID:
                grouped.sort(key=self._end_group_sort_key)
            ordered.extend(grouped)
        self.items = ordered

    def _move_page_to_group_position(self, item: dict, target_group: str, target_local_pos: int) -> None:
        """Déplace une page avec une position locale, indépendamment du sens de déplacement."""
        source_group = self._item_group_id(item)
        source_group_items = [candidate for candidate in self.items if self._item_group_id(candidate) == source_group]
        target_group_items = [
            candidate for candidate in self.items
            if self._item_group_id(candidate) == target_group and candidate is not item
        ]

        self.items.remove(item)
        item["plan_group"] = target_group
        target_local_pos = max(0, min(len(target_group_items), int(target_local_pos)))
        target_group_items.insert(target_local_pos, item)

        rebuilt: list[dict] = []
        for group in self.groups:
            group_id = str(group.get("id", ""))
            if group_id == target_group:
                grouped = list(target_group_items)
            elif group_id == source_group and source_group != target_group:
                grouped = [candidate for candidate in source_group_items if candidate is not item]
            else:
                grouped = [candidate for candidate in self.items if self._item_group_id(candidate) == group_id]
            if group_id == self.START_GROUP_ID:
                grouped.sort(key=self._start_group_sort_key)
            elif group_id == self.END_GROUP_ID:
                grouped.sort(key=self._end_group_sort_key)
            rebuilt.extend(grouped)
        self.items = rebuilt

    def _on_release(self, _event):
        kind = self._drag_kind
        dragged = self._dragging
        start = self._drag_start_index
        target = self._drag_target_index
        target_group = self._drag_target_group_id
        target_local_pos = self._drag_target_local_pos
        drag_group_id = self._drag_group_id
        group_target = self._drag_group_target

        self._drag_kind = None
        self._drag_start_index = None
        self._drag_target_index = None
        self._drag_target_group_id = None
        self._drag_target_local_pos = None
        self._drag_group_id = None
        self._drag_group_target = None
        self._drag_start_xy = None
        self._drag_pointer_xy = None
        self._dragging = False
        self._drag_autoscroll_direction = 0
        self._drag_autoscroll_speed = 0
        self._cancel_drag_autoscroll()

        if not dragged:
            self.render()
            return "break"

        if kind == "group" and drag_group_id and group_target is not None:
            middle = [group for group in self.groups if str(group.get("id", "")) not in {self.START_GROUP_ID, self.END_GROUP_ID}]
            source_pos = next((i for i, group in enumerate(middle) if str(group.get("id", "")) == drag_group_id), None)
            if source_pos is not None:
                group = middle.pop(source_pos)
                if group_target > source_pos:
                    group_target -= 1
                group_target = max(0, min(len(middle), group_target))
                middle.insert(group_target, group)
                start_group = next(group for group in self.groups if str(group.get("id", "")) == self.START_GROUP_ID)
                end_group = next(group for group in self.groups if str(group.get("id", "")) == self.END_GROUP_ID)
                self.groups = [start_group, *middle, end_group]
                self._reorder_items_by_group_order()
                self._selected_group_id = drag_group_id
                self._save_order()
            self.render()
            return "break"

        if kind == "page" and start is not None and target_group is not None and target_local_pos is not None:
            if start >= len(self.items) or self._is_locked_page(self.items[start]):
                self.render()
                return "break"

            item = self.items[start]
            # Aucun index global : le dépôt est défini par partie + position locale.
            self._move_page_to_group_position(item, target_group, target_local_pos)

            try:
                self._selected_index = self.items.index(item)
            except ValueError:
                self._selected_index = 0
            self._save_order()
            self.render()
            self.after_idle(self.center_selected)
            return "break"

        self.render()
        return "break"

    def _on_double_click(self, event):
        index = self._index_at(event)
        if index is not None:
            self._selected_index = index
            self._selected_group_id = self._item_group_id(self.items[index])
            self.render()
            self.on_open_item(self.items[index], index)
            return "break"
        group_id = self._group_id_from_current_tags() or self._group_at(event)
        if group_id is not None:
            self._selected_group_id = group_id
            self.render()
            self.after_idle(lambda gid=group_id: self._begin_group_title_edit(gid))
        return "break"

    # ------------------------------------------------------------------
    # Souris
    # ------------------------------------------------------------------

    def _on_ctrl_mousewheel(self, event):
        if event.delta == 0:
            return "break"
        self.step_zoom(1 if event.delta > 0 else -1)
        return "break"

    def _on_shift_mousewheel(self, event):
        if self._h_scroll_needed:
            delta = -1 if event.delta > 0 else 1
            self.canvas.xview_scroll(delta * 4, "units")
            self.after_idle(self._update_visible_part_marker)
        return "break"

    def _on_mousewheel(self, event):
        delta = -1 if event.delta > 0 else 1
        if self._v_scroll_needed:
            self.canvas.yview_scroll(delta * 4, "units")
        elif self._h_scroll_needed:
            self.canvas.xview_scroll(delta * 4, "units")
            self.after_idle(self._update_visible_part_marker)
        return "break"
