from __future__ import annotations

import tkinter as tk

from src.engine.foundation import Point, Rect, Size
from src.engine.graphics import Rectangle
from src.gui.renderer import CanvasRenderer


class PageCanvas:

    PAGE_WIDTH = 420
    PAGE_HEIGHT = 595

    def __init__(self, parent):

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

        self.objects = []

        # -----------------------------
        # Rectangle de démonstration
        # -----------------------------

        self.add_object(
            Rectangle(
                Rect(
                    Point(110, 140),
                    Size(200, 120),
                ),
                fill_color="#D8E8FF",
                outline_color="#2D7FF9",
                outline_width=2,
            )
        )

        self.redraw()

    # --------------------------------------------------

    def widget(self):

        return self.canvas

    # --------------------------------------------------

    def add_object(self, obj):

        self.objects.append(obj)

    # --------------------------------------------------

    def redraw(self):

        self.renderer.begin_frame()

        for obj in self.objects:
            self.renderer.draw_drawable(obj)

        self.renderer.end_frame()

    # --------------------------------------------------

    def clear(self):

        self.objects.clear()
        self.redraw()

    # --------------------------------------------------

    def set_page_selected(self, value: bool):

        self.canvas.configure(
            highlightbackground="#2D7FF9" if value else "#404040",
            highlightthickness=3 if value else 2,
        )