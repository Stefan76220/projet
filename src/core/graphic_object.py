import tkinter as tk


class GraphicObject:

    def __init__(
        self,
        canvas: tk.Canvas,
        x: int,
        y: int,
        width: int,
        height: int,
        text="",
        on_click=None
    ):

        self.canvas = canvas
        self.on_click = on_click

        self.selected = False

        self.drag_x = 0
        self.drag_y = 0

        self.items = []

        rect = canvas.create_rectangle(
            x,
            y,
            x + width,
            y + height,
            fill="#D8E8FF",
            outline="#606060",
            width=2
        )

        self.items.append(rect)

        if text:

            label = canvas.create_text(
                x + width / 2,
                y + height / 2,
                text=text,
                font=("Arial", 12)
            )

            self.items.append(label)

        for item in self.items:

            canvas.tag_bind(
                item,
                "<Button-1>",
                self._click
            )

            canvas.tag_bind(
                item,
                "<B1-Motion>",
                self._drag
            )

    # ---------------------------------------------------------

    def _click(self, event):

        self.drag_x = event.x
        self.drag_y = event.y

        if self.on_click is not None:
            self.on_click(self)

        return "break"

    # ---------------------------------------------------------

    def _drag(self, event):

        if not self.selected:
            return

        dx = event.x - self.drag_x
        dy = event.y - self.drag_y

        for item in self.items:
            self.canvas.move(item, dx, dy)

        self.drag_x = event.x
        self.drag_y = event.y

        return "break"

    # ---------------------------------------------------------

    def set_selected(self, value):

        self.selected = value

        self.canvas.itemconfigure(
            self.items[0],
            outline="#2D7FF9" if value else "#606060",
            width=3 if value else 2
        )