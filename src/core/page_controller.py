class PageController:

    def __init__(self, canvas):

        self.canvas = canvas

        self.page_selected = False
        self.selected_object = None

    # ---------------------------------------------------------

    def select_page(self):

        self.page_selected = True

        self.canvas.set_page_selected(True)

    # ---------------------------------------------------------

    def unselect_page(self):

        self.page_selected = False

        self.canvas.set_page_selected(False)

    # ---------------------------------------------------------

    def select_object(self, obj):

        self.select_page()

        if self.selected_object is not None:

            self.selected_object.set_selected(False)

        self.selected_object = obj

        obj.set_selected(True)

    # ---------------------------------------------------------

    def unselect_object(self):

        if self.selected_object is not None:

            self.selected_object.set_selected(False)

            self.selected_object = None

    # ---------------------------------------------------------

    def unselect_all(self):

        self.unselect_object()

        self.unselect_page()