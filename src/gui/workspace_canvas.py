import tkinter as tk

from src.gui.page_view import PageView


class WorkspaceCanvas:

    def __init__(self, parent):

        self.canvas = tk.Canvas(
            parent,
            bg="#909090",
            highlightthickness=0,
            bd=0
        )

        self.canvas.pack(fill="both", expand=True)

        self.pages = []
        self.selected_page = None

        self.canvas.bind("<Button-1>", self._on_click)

    # ---------------------------------------------------------

    def widget(self):

        return self.canvas

    # ---------------------------------------------------------

    def create_page(self, x=100, y=100):

        page = PageView(self.canvas, x, y)

        self.pages.append(page)

        return page

    # ---------------------------------------------------------

    def _on_click(self, event):

        for page in reversed(self.pages):

            if page.contains(event.x, event.y):

                self.select_page(page)

                return

        self.unselect_page()

    # ---------------------------------------------------------

    def select_page(self, page):

        if self.selected_page is page:
            return

        if self.selected_page is not None:
            self.selected_page.unselect()

        self.selected_page = page
        page.select()

    # ---------------------------------------------------------

    def unselect_page(self):

        if self.selected_page is not None:
            self.selected_page.unselect()
            self.selected_page = None