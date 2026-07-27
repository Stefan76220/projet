from __future__ import annotations


class PageView:
    """
    Représentation graphique d'une page dans le Workspace.
    """

    PAGE_WIDTH = 420
    PAGE_HEIGHT = 595

    def __init__(
        self,
        workspace_canvas,
        x: float = 100,
        y: float = 100,
    ) -> None:

        self.canvas = workspace_canvas

        self.x = x
        self.y = y

        self.page = None
        self.selection = None

        self.draw()

    # ==========================================================
    # Dessin
    # ==========================================================

    def draw(self) -> None:

        self.selection = self.canvas.create_rectangle(
            self.x - 3,
            self.y - 3,
            self.x + self.PAGE_WIDTH + 3,
            self.y + self.PAGE_HEIGHT + 3,
            outline="#2D7FF9",
            width=3,
            state="hidden",
        )

        self.page = self.canvas.create_rectangle(
            self.x,
            self.y,
            self.x + self.PAGE_WIDTH,
            self.y + self.PAGE_HEIGHT,
            fill="white",
            outline="#606060",
            width=1,
        )

    # ==========================================================
    # Sélection
    # ==========================================================

    def select(self) -> None:

        self.canvas.itemconfigure(
            self.selection,
            state="normal",
        )

    def unselect(self) -> None:

        self.canvas.itemconfigure(
            self.selection,
            state="hidden",
        )

    # ==========================================================
    # Géométrie
    # ==========================================================

    def contains(
        self,
        x: float,
        y: float,
    ) -> bool:

        return (
            self.x <= x <= self.x + self.PAGE_WIDTH
            and
            self.y <= y <= self.y + self.PAGE_HEIGHT
        )

    @property
    def bounds(self) -> tuple[float, float, float, float]:

        return (
            self.x,
            self.y,
            self.x + self.PAGE_WIDTH,
            self.y + self.PAGE_HEIGHT,
        )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"PageView("
            f"x={self.x}, "
            f"y={self.y})"
        )