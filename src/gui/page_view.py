class PageView:

    PAGE_WIDTH = 420
    PAGE_HEIGHT = 595

    def __init__(self, workspace_canvas, x=100, y=100):

        self.canvas = workspace_canvas

        self.x = x
        self.y = y

        self.page = None
        self.selection = None

        self.draw()

    # ---------------------------------------------------------

    def draw(self):

        # Contour de sélection (dessiné sous la page)
        self.selection = self.canvas.create_rectangle(
            self.x - 3,
            self.y - 3,
            self.x + self.PAGE_WIDTH + 3,
            self.y + self.PAGE_HEIGHT + 3,
            outline="#2D7FF9",
            width=3,
            state="hidden"
        )

        # Feuille blanche
        self.page = self.canvas.create_rectangle(
            self.x,
            self.y,
            self.x + self.PAGE_WIDTH,
            self.y + self.PAGE_HEIGHT,
            fill="white",
            outline="#606060",
            width=1
        )

    # ---------------------------------------------------------

    def select(self):

        self.canvas.itemconfigure(
            self.selection,
            state="normal"
        )

    # ---------------------------------------------------------

    def unselect(self):

        self.canvas.itemconfigure(
            self.selection,
            state="hidden"
        )

    # ---------------------------------------------------------

    def contains(self, x, y):

        return (
            self.x <= x <= self.x + self.PAGE_WIDTH
            and
            self.y <= y <= self.y + self.PAGE_HEIGHT
        )