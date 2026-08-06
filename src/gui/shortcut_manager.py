"""Gestion centrale des raccourcis clavier de PageMaître.

Le gestionnaire installe une seule série de raccourcis sur la fenêtre
principale. Chaque bureau active ensuite son propre contexte de commandes.

Raccourcis communs :
- Ctrl + Z : annuler ;
- Ctrl + Y : rétablir ;
- Ctrl + Maj + Z : rétablir ;
- Ctrl + A : tout sélectionner.

Les champs de saisie conservent leur comportement natif.
"""

from __future__ import annotations

import sys
import tkinter as tk
from dataclasses import dataclass
from typing import Callable


ShortcutCommand = Callable[[], object]


@dataclass(slots=True)
class ShortcutContext:
    """Commandes disponibles dans le bureau actuellement affiché."""

    owner: tk.Misc
    undo: ShortcutCommand | None = None
    redo: ShortcutCommand | None = None
    select_all: ShortcutCommand | None = None
    name: str = ""


class GlobalShortcutManager:
    """Distribue les raccourcis généraux au bureau actif."""

    _TEXT_INPUT_CLASSES = frozenset(
        {
            "entry",
            "text",
            "spinbox",
            "tentry",
            "tspinbox",
            "ttk::entry",
            "ttk::spinbox",
        }
    )

    def __init__(self, root: tk.Misc) -> None:
        self.root = root
        self._context: ShortcutContext | None = None
        self._binding_ids: dict[str, str] = {}

        setattr(
            self.root,
            "_pagemaitre_shortcut_manager",
            self,
        )

        self._bind_shortcuts()

    # ==========================================================
    # Activation d’un bureau
    # ==========================================================

    def activate(
        self,
        *,
        owner: tk.Misc,
        undo: ShortcutCommand | None = None,
        redo: ShortcutCommand | None = None,
        select_all: ShortcutCommand | None = None,
        name: str = "",
    ) -> None:
        """Déclare les commandes du bureau actuellement visible."""

        self._context = ShortcutContext(
            owner=owner,
            undo=undo,
            redo=redo,
            select_all=select_all,
            name=name.strip(),
        )

    def deactivate(
        self,
        owner: tk.Misc | None = None,
    ) -> None:
        """Retire le contexte actif.

        Lorsque ``owner`` est fourni, le contexte n’est retiré que s’il
        appartient réellement à ce widget.
        """

        context = self._context
        if context is None:
            return

        if owner is not None and context.owner is not owner:
            return

        self._context = None

    @property
    def active_context_name(self) -> str:
        """Nom du bureau actuellement raccordé."""

        context = self._valid_context()
        return context.name if context is not None else ""

    # ==========================================================
    # Liaisons générales
    # ==========================================================

    def _bind_shortcuts(self) -> None:
        shortcuts = {
            "<Control-z>": self._handle_undo,
            "<Control-Z>": self._handle_undo,
            "<Control-y>": self._handle_redo,
            "<Control-Y>": self._handle_redo,
            "<Control-Shift-z>": self._handle_redo,
            "<Control-Shift-Z>": self._handle_redo,
            "<Control-a>": self._handle_select_all,
            "<Control-A>": self._handle_select_all,
        }

        for sequence, callback in shortcuts.items():
            try:
                binding_id = self.root.bind(
                    sequence,
                    callback,
                    add="+",
                )
            except tk.TclError:
                binding_id = None

            if binding_id:
                self._binding_ids[sequence] = binding_id

    def close(self) -> None:
        """Retire les liaisons lors de la fermeture de PageMaître."""

        for sequence, binding_id in tuple(
            self._binding_ids.items()
        ):
            try:
                self.root.unbind(
                    sequence,
                    binding_id,
                )
            except tk.TclError:
                pass

        self._binding_ids.clear()
        self._context = None

        if (
            getattr(
                self.root,
                "_pagemaitre_shortcut_manager",
                None,
            )
            is self
        ):
            delattr(
                self.root,
                "_pagemaitre_shortcut_manager",
            )

    # ==========================================================
    # Distribution
    # ==========================================================

    def _handle_undo(self, event) -> str | None:
        return self._dispatch(
            event,
            "undo",
        )

    def _handle_redo(self, event) -> str | None:
        return self._dispatch(
            event,
            "redo",
        )

    def _handle_select_all(self, event) -> str | None:
        return self._dispatch(
            event,
            "select_all",
        )

    def _dispatch(
        self,
        event,
        command_name: str,
    ) -> str | None:
        if self._must_preserve_native_shortcut(event):
            return None

        context = self._valid_context()
        if context is None:
            return None

        callback = getattr(
            context,
            command_name,
            None,
        )
        if not callable(callback):
            return None

        try:
            result = callback()
        except Exception:
            self.root.report_callback_exception(
                *sys.exc_info()
            )
            return "break"

        # Un retour explicite False signifie que le bureau n’a rien traité.
        return None if result is False else "break"

    def _valid_context(self) -> ShortcutContext | None:
        context = self._context
        if context is None:
            return None

        try:
            exists = bool(
                context.owner.winfo_exists()
            )
        except (AttributeError, tk.TclError):
            exists = False

        if not exists:
            self._context = None
            return None

        return context

    def _must_preserve_native_shortcut(
        self,
        event,
    ) -> bool:
        """Laisse les champs de saisie gérer eux-mêmes leurs raccourcis."""

        widget = getattr(
            event,
            "widget",
            None,
        )
        if widget is None:
            return False

        try:
            widget_class = str(
                widget.winfo_class()
            ).strip().lower()
        except (AttributeError, tk.TclError):
            return False

        return widget_class in self._TEXT_INPUT_CLASSES


def get_global_shortcut_manager(
    widget: tk.Misc,
) -> GlobalShortcutManager | None:
    """Retrouve le gestionnaire installé sur la fenêtre principale."""

    try:
        root = widget.winfo_toplevel()
    except (AttributeError, tk.TclError):
        return None

    manager = getattr(
        root,
        "_pagemaitre_shortcut_manager",
        None,
    )

    return (
        manager
        if isinstance(
            manager,
            GlobalShortcutManager,
        )
        else None
    )