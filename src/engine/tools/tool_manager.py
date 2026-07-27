from __future__ import annotations

from .tool import Tool


class ToolManager:
    """
    Gère l'outil actif.
    """

    def __init__(self) -> None:

        self._active_tool: Tool | None = None

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def active_tool(self) -> Tool | None:
        return self._active_tool

    @property
    def has_active_tool(self) -> bool:
        return self._active_tool is not None

    # ==========================================================
    # Gestion des outils
    # ==========================================================

    def set_active_tool(
        self,
        tool: Tool | None,
    ) -> None:

        if tool is self._active_tool:
            return

        if self._active_tool is not None:
            self._active_tool.deactivate()

        self._active_tool = tool

        if self._active_tool is not None:
            self._active_tool.activate()

    def clear(self) -> None:

        self.set_active_tool(None)

    # ==========================================================
    # Évènements souris
    # ==========================================================

    def mouse_press(
        self,
        x: float,
        y: float,
        button: int,
    ) -> None:

        if self._active_tool is not None:
            self._active_tool.mouse_press(x, y, button)

    def mouse_move(
        self,
        x: float,
        y: float,
    ) -> None:

        if self._active_tool is not None:
            self._active_tool.mouse_move(x, y)

    def mouse_release(
        self,
        x: float,
        y: float,
        button: int,
    ) -> None:

        if self._active_tool is not None:
            self._active_tool.mouse_release(x, y, button)

    # ==========================================================
    # Évènements clavier
    # ==========================================================

    def key_press(
        self,
        key: str,
    ) -> None:

        if self._active_tool is not None:
            self._active_tool.key_press(key)

    def key_release(
        self,
        key: str,
    ) -> None:

        if self._active_tool is not None:
            self._active_tool.key_release(key)

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __bool__(self) -> bool:

        return self.has_active_tool

    def __str__(self) -> str:

        return (
            self._active_tool.name
            if self._active_tool is not None
            else "Aucun outil"
        )