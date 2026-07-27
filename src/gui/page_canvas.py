from __future__ import annotations

import tkinter as tk

from src.engine.foundation import Point, Rect, Size
from src.engine.graphics import Rectangle
from src.engine.graphics.styles import (
    Fill,
    ShapeStyle,
    Stroke,
)
from src.gui.renderer import CanvasRenderer


class PageCanvas:

    PAGE_WIDTH = 420
    PAGE_HEIGHT = 595

    def __init__(
        self,
        parent,
    ) -> None:

        self.canvas = tk.Canvas(
            parent,
            width=self.PAGE_WIDTH,
            height=self.PAGE_HEIGHT,
            bg="white",
            relief="flat",
            highlightthickness=2,
            highlightbackground="#404040",
        )

        self.canvas.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )

        self.renderer = CanvasRenderer(self.canvas)

        self.objects: list[Rectangle] = []

        # ==========================================================
        # Rectangle de démonstration
        # ==========================================================

        self.add_object(
            Rectangle(
                bounds=Rect(
                    Point(110, 140),
                    Size(200, 120),
                ),
                style=ShapeStyle(
                    fill=Fill(
                        color="#D8E8FF",
                    ),
                    stroke=Stroke(
                        color="#2D7FF9",
                        width=2,
                    ),
                ),
            )
        )

        self.redraw()

    # ==========================================================
    # Accès
    # ==========================================================

    def widget(self) -> tk.Canvas:

        return self.canvas

    # ==========================================================
    # Gestion
    # ==========================================================

    def add_object(
        self,
        obj: Rectangle,
    ) -> None:

        self.objects.append(obj)

    def clear(self) -> None:

        self.objects.clear()
        self.redraw()

    # ==========================================================
    # Affichage
    # ==========================================================

    def redraw(self) -> None:

        self.renderer.begin_frame()

        for obj in self.objects:
            self.renderer.draw_drawable(obj)

        self.renderer.end_frame()

    def set_page_selected(
        self,
        value: bool,
    ) -> None:

        self.canvas.configure(
            highlightbackground="#2D7FF9" if value else "#404040",
            highlightthickness=3 if value else 2,
        )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"PageCanvas("
            f"objects={len(self.objects)})"
        )