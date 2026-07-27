from __future__ import annotations

import tkinter as tk


class GraphicObject:
    """
    Objet graphique interactif de base.
    """

    def __init__(
        self,
        canvas: tk.Canvas,
        x: float,
        y: float,
        width: float,
        height: float,
        text: str = "",
        on_click=None,
    ) -> None:

        self.canvas = canvas
        self.on_click = on_click

        self.selected = False

        self.drag_x = 0.0
        self.drag_y = 0.0

        self.items: list[int] = []

        self._create_items(
            x,
            y,
            width,
            height,
            text,
        )

        self._bind_events()

    # ==========================================================
    # Construction
    # ==========================================================

    def _create_items(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        text: str,
    ) -> None:

        rectangle = self.canvas.create_rectangle(
            x,
            y,
            x + width,
            y + height,
            fill="#D8E8FF",
            outline="#606060",
            width=2,
        )

        self.items.append(rectangle)

        if text:

            label = self.canvas.create_text(
                x + width / 2,
                y + height / 2,
                text=text,
                font=("Arial", 12),
            )

            self.items.append(label)

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def is_selected(self) -> bool:

        return self.selected

    # ==========================================================
    # Évènements
    # ==========================================================

    def _bind_events(self) -> None:

        for item in self.items:

            self.canvas.tag_bind(
                item,
                "<Button-1>",
                self._click,
            )

            self.canvas.tag_bind(
                item,
                "<B1-Motion>",
                self._drag,
            )

    def _click(self, event) -> str:

        self.drag_x = event.x
        self.drag_y = event.y

        if self.on_click is not None:
            self.on_click(self)

        return "break"

    def _drag(self, event) -> str:

        if not self.selected:
            return "break"

        dx = event.x - self.drag_x
        dy = event.y - self.drag_y

        self.move(
            dx,
            dy,
        )

        self.drag_x = event.x
        self.drag_y = event.y

        return "break"

    # ==========================================================
    # Manipulation
    # ==========================================================

    def move(
        self,
        dx: float,
        dy: float,
    ) -> None:

        for item in self.items:

            self.canvas.move(
                item,
                dx,
                dy,
            )

    def set_selected(
        self,
        value: bool,
    ) -> None:

        self.selected = value

        self.canvas.itemconfigure(
            self.items[0],
            outline="#2D7FF9" if value else "#606060",
            width=3 if value else 2,
        )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"selected={self.selected})"
        )