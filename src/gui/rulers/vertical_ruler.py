from __future__ import annotations

import customtkinter as ctk


class VerticalRuler(ctk.CTkCanvas):

    WIDTH = 30

    def __init__(
        self,
        master,
        editor_canvas,
        **kwargs,
    ) -> None:

        super().__init__(
            master,
            width=self.WIDTH,
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

        top_page = self.editor.page_top

        start_mm = max(
            0,
            int(viewport.px_to_mm(-top_page)),
        )

        end_mm = (
            int(
                viewport.px_to_mm(
                    height - top_page,
                )
            )
            + 2
        )

        for mm in range(start_mm, end_mm):

            y = top_page + viewport.mm_to_px(mm)

            self._draw_tick(
                y,
                mm,
                width,
            )

        self.create_line(
            width - 1,
            0,
            width - 1,
            height,
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
        y: float,
        mm: int,
        width: int,
    ) -> None:

        if mm % 10 == 0:

            tick = 16

            self.create_text(
                2,
                y,
                text=str(mm),
                anchor="nw",
                angle=90,
                font=("Segoe UI", 8),
                fill="#303030",
            )

        elif mm % 5 == 0:

            tick = 10

        else:

            tick = 5

        self.create_line(
            width,
            y,
            width - tick,
            y,
            fill="#404040",
        )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return "VerticalRuler()"