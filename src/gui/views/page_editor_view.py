import tkinter as tk
import customtkinter as ctk

from src.gui.editor_canvas import EditorCanvas
from src.gui.rulers.horizontal_ruler import HorizontalRuler
from src.gui.rulers.vertical_ruler import VerticalRuler
from src.gui.status_bar import StatusBar


class PageEditorView:

    RULER_SIZE = 30

    def __init__(self, parent, page, on_back=None):

        self.parent = parent
        self.page = page
        self.on_back = on_back

        self.workspace = None
        self.status_bar = None

    # ---------------------------------------------------------

    def show(self):

        for widget in self.parent.winfo_children():
            widget.destroy()

        root = ctk.CTkFrame(
            self.parent,
            fg_color="#909090"
        )
        root.pack(fill="both", expand=True)

        # ---------------------------------------------------------
        # En-tête
        # ---------------------------------------------------------

        header = ctk.CTkFrame(
            root,
            fg_color="transparent",
            height=60
        )

        header.pack(fill="x", padx=20, pady=(20, 10))
        header.pack_propagate(False)

        ctk.CTkButton(
            header,
            text="← Retour",
            width=120,
            command=self.back
        ).pack(side="left")

        titre = self.page.title or f"Page {self.page.number:03d}"

        ctk.CTkLabel(
            header,
            text=titre,
            font=("Arial", 22, "bold")
        ).pack(side="left", padx=20)

        # ---------------------------------------------------------
        # Zone d'édition
        # ---------------------------------------------------------

        editor_area = tk.Frame(
            root,
            bg="#909090"
        )
        editor_area.pack(fill="both", expand=True)

        editor_area.grid_rowconfigure(1, weight=1)
        editor_area.grid_columnconfigure(1, weight=1)

        # ---------------------------------------------------------
        # Coin supérieur gauche
        # ---------------------------------------------------------

        corner = tk.Frame(
            editor_area,
            bg="#cfcfcf",
            width=self.RULER_SIZE,
            height=self.RULER_SIZE
        )
        corner.grid(row=0, column=0, sticky="nsew")
        corner.grid_propagate(False)

        # ---------------------------------------------------------
        # Canvas
        # ---------------------------------------------------------

        canvas_container = tk.Frame(
            editor_area,
            bg="#909090"
        )

        canvas_container.grid(
            row=1,
            column=1,
            sticky="nsew"
        )

        self.workspace = EditorCanvas(canvas_container)
        self.workspace.pack(fill="both", expand=True)

        # ---------------------------------------------------------
        # Règles
        # ---------------------------------------------------------

        horizontal_ruler = HorizontalRuler(
            editor_area,
            self.workspace
        )

        horizontal_ruler.grid(
            row=0,
            column=1,
            sticky="ew"
        )

        vertical_ruler = VerticalRuler(
            editor_area,
            self.workspace
        )

        vertical_ruler.grid(
            row=1,
            column=0,
            sticky="ns"
        )

        # Premier affichage

        horizontal_ruler.redraw()
        vertical_ruler.redraw()

        # ---------------------------------------------------------
        # Barre d'état
        # ---------------------------------------------------------

        self.status_bar = StatusBar(root)
        self.status_bar.pack(
            fill="x",
            side="bottom"
        )

        self._update_status()

    # ---------------------------------------------------------

    def _update_status(self):

        if self.workspace is None:
            return

        self.status_bar.update_status(
            self.workspace.mouse_x_mm,
            self.workspace.mouse_y_mm,
            self.workspace.viewport.zoom,
            self.workspace.page_format.name,
        )

        self.parent.after(
            30,
            self._update_status
        )

    # ---------------------------------------------------------

    def back(self):

        if self.on_back:
            self.on_back()