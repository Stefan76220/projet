from __future__ import annotations

import tkinter as tk
from collections.abc import Callable

from src.gui_v3 import theme


class FocusToolbar(tk.Frame):
    """Barre compacte affichée uniquement lorsque B travaille sur une page.

    Elle ne contient aucune donnée propre : elle pilote le BookCanvas existant
    et le contexte de travail actif. Le panneau C reste donc l'unique source
    des outils détaillés et n'est jamais reconstruit.
    """

    def __init__(
        self,
        parent,
        *,
        book_canvas,
        tabs: tuple[tuple[str, str], ...],
        on_select_tab: Callable[[str], None],
    ) -> None:
        super().__init__(
            parent,
            bg=theme.WINDOW_DEEP,
            highlightthickness=1,
            highlightbackground=theme.BORDER,
            bd=0,
        )
        self.book_canvas = book_canvas
        self.on_select_tab = on_select_tab
        self._tab_buttons: dict[str, tk.Button] = {}
        self._active_tab = "structure"

        self.grid_columnconfigure(6, weight=1)

        self._button(self, "← Livre", self.book_canvas.fit_book, primary=True).grid(
            row=0, column=0, padx=(8, 6), pady=7
        )

        tab_host = tk.Frame(self, bg=theme.WINDOW_DEEP)
        tab_host.grid(row=0, column=1, padx=(0, 8), pady=6, sticky="w")
        for index, (key, label) in enumerate(tabs):
            button = self._button(
                tab_host,
                label,
                lambda k=key: self.on_select_tab(k),
                compact=True,
            )
            button.pack(side="left", padx=(0 if index == 0 else 3, 0))
            self._tab_buttons[key] = button

        self._separator(2)

        self._button(self, "−", lambda: self.book_canvas.step_zoom(-10), compact=True, width=3).grid(
            row=0, column=3, padx=(8, 3), pady=7
        )
        tk.Label(
            self,
            textvariable=self.book_canvas.zoom_text_var,
            width=7,
            anchor="center",
            bg=theme.WINDOW_DEEP,
            fg=theme.INK,
            font=(theme.FONT_UI, 9, "bold"),
        ).grid(row=0, column=4, padx=2)
        self._button(self, "+", lambda: self.book_canvas.step_zoom(10), compact=True, width=3).grid(
            row=0, column=5, padx=(3, 8), pady=7
        )

        self._button(self, "Ajuster page", self.book_canvas.fit_selected, compact=True).grid(
            row=0, column=7, padx=(4, 8), pady=7
        )

        self.set_active_tab(self._active_tab)

    def _button(self, parent, text, command, *, compact=False, primary=False, width=None):
        if primary:
            bg = theme.ACCENT_DARK
            fg = theme.WHITE
            active_bg = theme.ACCENT
            active_fg = theme.WINDOW_DEEP
        else:
            bg = theme.PANEL_SOFT
            fg = theme.INK
            active_bg = theme.ACCENT_SOFT
            active_fg = theme.WHITE
        return tk.Button(
            parent,
            text=text,
            command=command,
            width=width,
            bg=bg,
            fg=fg,
            activebackground=active_bg,
            activeforeground=active_fg,
            relief="flat",
            bd=0,
            padx=8 if compact else 11,
            pady=4 if compact else 5,
            font=(theme.FONT_UI, 8 if compact else 9, "bold"),
            cursor="hand2",
        )

    def _separator(self, column: int):
        tk.Frame(self, bg=theme.BORDER_SOFT, width=1).grid(
            row=0, column=column, sticky="ns", pady=9
        )

    def set_active_tab(self, key: str) -> None:
        if key not in self._tab_buttons:
            return
        self._active_tab = key
        for tab_key, button in self._tab_buttons.items():
            if tab_key == key:
                button.configure(
                    bg=theme.ACCENT_DARK,
                    fg=theme.WHITE,
                    activebackground=theme.ACCENT,
                    activeforeground=theme.WINDOW_DEEP,
                )
            else:
                button.configure(
                    bg=theme.PANEL_SOFT,
                    fg=theme.INK,
                    activebackground=theme.ACCENT_SOFT,
                    activeforeground=theme.WHITE,
                )
