from __future__ import annotations

from typing import TYPE_CHECKING

from src.engine.camera import Camera
from src.engine.commands import CommandManager
from src.engine.selection import SelectionManager
from src.engine.tools import ToolManager

if TYPE_CHECKING:
    from src.engine.document import Document


class Workspace:
    """
    Workspace du moteur.

    Il centralise uniquement les services utilisés pendant
    l'édition.

    Les données (pages, couches, objets...) appartiennent
    exclusivement au Document.
    """

    def __init__(
        self,
        document: "Document",
    ) -> None:

        self._document = document

        self._camera = Camera()
        self._selection = SelectionManager()
        self._commands = CommandManager()
        self._tools = ToolManager()

    # ==========================================================
    # Accès au document
    # ==========================================================

    @property
    def document(self) -> "Document":
        return self._document

    # ==========================================================
    # Services
    # ==========================================================

    @property
    def camera(self) -> Camera:
        return self._camera

    @property
    def selection(self) -> SelectionManager:
        return self._selection

    @property
    def commands(self) -> CommandManager:
        return self._commands

    @property
    def tools(self) -> ToolManager:
        return self._tools