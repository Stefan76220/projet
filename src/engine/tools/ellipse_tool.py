from __future__ import annotations

from src.engine.commands import CreateDrawableCommand
from src.engine.foundation import Point, Rect, Size
from src.engine.graphics import Ellipse
from src.engine.graphics.styles import ShapeStyle

from .tool import Tool


class EllipseTool(Tool):
    """
    Outil de création d'ellipses.
    """

    def __init__(self, workspace) -> None:

        super().__init__(workspace)

        self._start_x = 0.0
        self._start_y = 0.0
        self._drawing = False

    @property
    def name(self) -> str:
        return "Ellipse"

    # ==========================================================
    # Souris
    # ==========================================================

    def mouse_press(
        self,
        x: float,
        y: float,
        button: int,
    ) -> None:

        if button != 1:
            return

        self._start_x = x
        self._start_y = y
        self._drawing = True

    def mouse_move(
        self,
        x: float,
        y: float,
    ) -> None:
        """
        Le dessin interactif (aperçu) sera ajouté ultérieurement.
        """
        ...

    def mouse_release(
        self,
        x: float,
        y: float,
        button: int,
    ) -> None:

        if not self._drawing or button != 1:
            return

        self._drawing = False

        left = min(self._start_x, x)
        top = min(self._start_y, y)
        width = abs(x - self._start_x)
        height = abs(y - self._start_y)

        if width <= 0 or height <= 0:
            return

        ellipse = Ellipse(
            bounds=Rect(
                Point(left, top),
                Size(width, height),
            ),
            style=ShapeStyle(),
        )

        if self.workspace.page_count == 0:
            self.workspace.create_page()

        page = self.workspace.pages[0]

        if page.layer_count == 0:
            return

        layer = page.layers[0]

        self.workspace.commands.execute(
            CreateDrawableCommand(
                layer=layer,
                drawable=ellipse,
            )
        )