from __future__ import annotations

import customtkinter as ctk


class HorizontalRuler(ctk.CTkCanvas):

    HEIGHT = 30

    def __init__(
        self,
        master,
        editor_canvas,
        **kwargs,
    ) -> None:

        super().__init__(
            master,
            height=self.HEIGHT,
            highlightthickness=0,
            bg="#ECECEC",
            **kwargs,
        )

        self.editor = editor_canvas

        self.bind(
            "<Configure>",
            lambda _event: self.redraw(),
        )

    # ==========================================================
    # Affichage
    # ==========================================================

    def redraw(self) -> None:

        self.delete("all")

        viewport = self.editor.viewport

        width = self.winfo_width()
        height = self.winfo_height()

        self._draw_background(
            width,
            height,
        )

        pixels_per_mm = viewport.mm_to_px(1)

        if pixels_per_mm <= 0:
            return

        left_page = self.editor.page_left

        start_mm = max(
            0,
            int(viewport.px_to_mm(-left_page)),
        )

        end_mm = (
            int(
                viewport.px_to_mm(
                    width - left_page,
                )
            )
            + 2
        )

        for mm in range(start_mm, end_mm):

            x = left_page + viewport.mm_to_px(mm)

            self._draw_tick(
                x,
                mm,
                height,
            )

        self.create_line(
            0,
            height - 1,
            width,
            height - 1,
            fill="#B5B5B5",
        )

    # ==========================================================
    # Dessin
    # ==========================================================

    def _draw_background(
        self,
        width: int,
        height: int,
    ) -> None:

        self.create_rectangle(
            0,
            0,
            width,
            height,
            fill="#ECECEC",
            outline="#C8C8C8",
        )

    def _draw_tick(
        self,
        x: float,
        mm: int,
        height: int,
    ) -> None:

        if mm % 10 == 0:

            tick = 16

            self.create_text(
                x + 2,
                2,
                text=str(mm),
                anchor="nw",
                font=("Segoe UI", 8),
                fill="#303030",
            )

        elif mm % 5 == 0:

            tick = 10

        else:

            tick = 5

        self.create_line(
            x,
            height,
            x,
            height - tick,
            fill="#404040",
        )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return "HorizontalRuler()"