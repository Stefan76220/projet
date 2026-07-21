import customtkinter as ctk

from src.theme.colors import Colors
from src.theme.fonts import Fonts


class SidebarButton(ctk.CTkButton):

    def __init__(self, parent, text, command=None):

        super().__init__(
            parent,
            text=text,
            command=command,
            height=44,
            corner_radius=10,
            fg_color=Colors.BUTTON,
            hover_color=Colors.BUTTON_HOVER,
            text_color=Colors.TEXT,
            font=Fonts.NORMAL,
            anchor="w"
        )