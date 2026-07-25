from __future__ import annotations

from src.engine.commands.command import Command


class CommandManager:
    """
    Gère l'historique des commandes du moteur.
    """

    def __init__(self):

        self._undo_stack: list[Command] = []
        self._redo_stack: list[Command] = []

    def execute(self, command: Command) -> None:

        command.execute()

        self._undo_stack.append(command)
        self._redo_stack.clear()

    def undo(self) -> None:

        if not self._undo_stack:
            return

        command = self._undo_stack.pop()
        command.undo()

        self._redo_stack.append(command)

    def redo(self) -> None:

        if not self._redo_stack:
            return

        command = self._redo_stack.pop()
        command.execute()

        self._undo_stack.append(command)

    def clear(self) -> None:

        self._undo_stack.clear()
        self._redo_stack.clear()

    @property
    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo_stack)