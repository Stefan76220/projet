from __future__ import annotations

import tkinter as tk

from src.gui.page_view import PageView


class WorkspaceCanvas:
    """
    Zone de travail contenant les différentes pages affichées.
    """

    def __init__(
        self,
        parent,
    ) -> None:

        self.canvas = tk.Canvas(
            parent,
            bg="#909090",
            highlightthickness=0,
            bd=0,
        )

        self.canvas.pack(
            fill="both",
            expand=True,
        )

        self.pages: list[PageView] = []
        self.selected_page: PageView | None = None

        self.canvas.bind(
            "<Button-1>",
            self._on_click,
        )

    # ==========================================================
    # Accès
    # ==========================================================

    def widget(self) -> tk.Canvas:

        return self.canvas

    # ==========================================================
    # Pages
    # ==========================================================

    def create_page(
        self,
        x: float = 100,
        y: float = 100,
    ) -> PageView:

        page = PageView(
            self.canvas,
            x,
            y,
        )

        self.pages.append(page)

        return page

    # ==========================================================
    # Sélection
    # ==========================================================

    def _on_click(
        self,
        event,
    ) -> None:

        for page in reversed(self.pages):

            if page.contains(event.x, event.y):
                self.select_page(page)
                return

        self.unselect_page()

    def select_page(
        self,
        page: PageView,
    ) -> None:

        if self.selected_page is page:
            return

        if self.selected_page is not None:
            self.selected_page.unselect()

        self.selected_page = page
        page.select()

    def unselect_page(self) -> None:

        if self.selected_page is None:
            return

        self.selected_page.unselect()
        self.selected_page = None

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __iter__(self):

        return iter(self.pages)

    def __len__(self) -> int:

        return len(self.pages)

    def __repr__(self) -> str:

        return (
            f"WorkspaceCanvas("
            f"pages={len(self.pages)}, "
            f"selected={self.selected_page!r})"
        )