from __future__ import annotations

from src.engine.commands.command import Command


class CommandManager:
    """
    Gère l'historique des commandes du moteur.
    """

    def __init__(self) -> None:

        self._undo_stack: list[Command] = []
        self._redo_stack: list[Command] = []

    # ==========================================================
    # Exécution
    # ==========================================================

    def execute(
        self,
        command: Command,
    ) -> None:

        command.execute()

        self._undo_stack.append(command)
        self._redo_stack.clear()

    # ==========================================================
    # Undo / Redo
    # ==========================================================

    def undo(self) -> None:

        if not self.can_undo:
            return

        command = self._undo_stack.pop()
        command.undo()

        self._redo_stack.append(command)

    def redo(self) -> None:

        if not self.can_redo:
            return

        command = self._redo_stack.pop()
        command.redo()

        self._undo_stack.append(command)

    # ==========================================================
    # Historique
    # ==========================================================

    def clear(self) -> None:

        self._undo_stack.clear()
        self._redo_stack.clear()

    @property
    def undo_count(self) -> int:
        return len(self._undo_stack)

    @property
    def redo_count(self) -> int:
        return len(self._redo_stack)

    @property
    def can_undo(self) -> bool:
        return bool(self._undo_stack)

    @property
    def can_redo(self) -> bool:
        return bool(self._redo_stack)

    @property
    def next_undo(self) -> Command | None:

        return (
            self._undo_stack[-1]
            if self._undo_stack
            else None
        )

    @property
    def next_redo(self) -> Command | None:

        return (
            self._redo_stack[-1]
            if self._redo_stack
            else None
        )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __len__(self) -> int:

        return self.undo_count

    def __bool__(self) -> bool:

        return self.can_undo or self.can_redo