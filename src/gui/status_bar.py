from __future__ import annotations

import customtkinter as ctk


class StatusBar(ctk.CTkFrame):

    HEIGHT = 26

    def __init__(
        self,
        master,
    ) -> None:

        super().__init__(
            master,
            height=self.HEIGHT,
            corner_radius=0,
        )

        self.grid_columnconfigure(
            0,
            weight=1,
        )

        self._editor = None

        self.label = ctk.CTkLabel(
            self,
            text="Prêt",
            anchor="w",
            padx=10,
            font=("Segoe UI", 12),
        )

        self.label.grid(
            row=0,
            column=0,
            sticky="ew",
        )

    # ==========================================================
    # Attachement
    # ==========================================================

    def attach(
        self,
        editor,
    ) -> None:

        self._editor = editor

        editor.viewport.add_listener(self.refresh)

        self.refresh()

    # ==========================================================
    # Rafraîchissement
    # ==========================================================

    def refresh(self) -> None:

        if self._editor is None:
            return

        self.label.configure(
            text=(
                f"X : {self._editor.mouse_x_mm:8.2f} mm     "
                f"Y : {self._editor.mouse_y_mm:8.2f} mm     "
                f"Zoom : {self._editor.viewport.zoom * 100:6.1f} %     "
                f"Format : {self._editor.page_format.name}"
            )
        )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"StatusBar("
            f"editor={self._editor!r})"
        )