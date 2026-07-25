import customtkinter as ctk


class HorizontalRuler(ctk.CTkCanvas):

    HEIGHT = 30

    def __init__(self, master, editor_canvas, **kwargs):

        super().__init__(
            master,
            height=self.HEIGHT,
            highlightthickness=0,
            bg="#ECECEC",
            **kwargs,
        )

        self.editor = editor_canvas

        self.bind("<Configure>", lambda e: self.redraw())

    # ------------------------------------------------------------------

    def redraw(self):

        self.delete("all")

        viewport = self.editor.viewport

        width = self.winfo_width()
        height = self.winfo_height()

        self.create_rectangle(
            0,
            0,
            width,
            height,
            fill="#ECECEC",
            outline="#C8C8C8",
        )

        pixels_per_mm = viewport.mm_to_px(1)

        if pixels_per_mm <= 0:
            return

        left_page = (
            (width - viewport.mm_to_px(self.editor.page_format.width_mm)) / 2
            + viewport.offset_x_px
        )

        start_mm = int(
            max(
                0,
                viewport.px_to_mm(-left_page),
            )
        )

        end_mm = int(
            viewport.px_to_mm(width - left_page)
        ) + 2

        for mm in range(start_mm, end_mm):

            x = left_page + viewport.mm_to_px(mm)

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

        self.create_line(
            0,
            height - 1,
            width,
            height - 1,
            fill="#B5B5B5",
        )