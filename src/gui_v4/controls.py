from __future__ import annotations

import tkinter as tk

from src.gui_v4 import theme


def _color(
    name: str,
    fallback: str,
) -> str:

    return str(
        getattr(
            theme,
            name,
            fallback,
        )
    )


class TLButton(tk.Button):
    """
    Bouton TomeLinea.

    Reprend le comportement du V3Button :
    - survol gere explicitement ;
    - clic visuel ;
    - curseur main ;
    - aucun comportement dependant du theme Windows.
    """

    def __init__(
        self,
        parent,
        text: str,
        command=None,
        *,
        primary: bool = False,
        compact: bool = False,
        state: str = "normal",
        **kwargs,
    ):

        if primary:

            bg = _color(
                "ACCENT_DARK",
                _color(
                    "ACCENT",
                    "#487A79",
                ),
            )

            hover_bg = _color(
                "ACCENT",
                "#5A9996",
            )

            fg = _color(
                "WHITE",
                "#F2F3F4",
            )

            hover_fg = _color(
                "WINDOW_DEEP",
                "#151A20",
            )

        else:

            bg = _color(
                "PANEL_SOFT",
                _color(
                    "PANEL_ALT",
                    "#30363D",
                ),
            )

            hover_bg = _color(
                "ACCENT_SOFT",
                "#405B5B",
            )

            fg = _color(
                "INK",
                "#E4E7E9",
            )

            hover_fg = _color(
                "WHITE",
                "#FFFFFF",
            )

        options = {
            "text":
                text,

            "command":
                command,

            "state":
                state,

            "bg":
                bg,

            "fg":
                fg,

            "activebackground":
                hover_bg,

            "activeforeground":
                hover_fg,

            "disabledforeground":
                _color(
                    "MUTED",
                    "#777F87",
                ),

            "relief":
                "flat",

            "bd":
                0,

            "padx":
                10
                if compact
                else 15,

            "pady":
                5
                if compact
                else 8,

            "font":
                (
                    _color(
                        "FONT_UI",
                        "Segoe UI",
                    ),
                    8
                    if compact
                    else 9,
                    "bold",
                ),

            "cursor":
                (
                    "hand2"
                    if state
                    != "disabled"
                    else "arrow"
                ),
        }

        options.update(
            kwargs
        )

        super().__init__(
            parent,
            **options,
        )

        self._tl_base_bg = str(
            self.cget(
                "bg"
            )
        )

        self._tl_hover_bg = hover_bg

        self._tl_base_fg = str(
            self.cget(
                "fg"
            )
        )

        self._tl_hover_fg = hover_fg

        self.bind(
            "<Enter>",
            self._tl_enter,
            add="+",
        )

        self.bind(
            "<Leave>",
            self._tl_leave,
            add="+",
        )

        self.bind(
            "<ButtonPress-1>",
            self._tl_press,
            add="+",
        )

        self.bind(
            "<ButtonRelease-1>",
            self._tl_release,
            add="+",
        )


    def _tl_enabled(
        self,
    ) -> bool:

        return (
            str(
                self.cget(
                    "state"
                )
            )
            != "disabled"
        )


    def _tl_enter(
        self,
        _event=None,
    ):

        if not self._tl_enabled():
            return

        self.configure(
            bg=self._tl_hover_bg,
            fg=self._tl_hover_fg,
            relief="raised",
        )


    def _tl_leave(
        self,
        _event=None,
    ):

        self.configure(
            bg=self._tl_base_bg,
            fg=self._tl_base_fg,
            relief="flat",
        )


    def _tl_press(
        self,
        _event=None,
    ):

        if not self._tl_enabled():
            return

        self.configure(
            bg=_color(
                "ACCENT",
                "#5A9996",
            ),
            relief="sunken",
        )


    def _tl_release(
        self,
        _event=None,
    ):

        if not self._tl_enabled():
            return

        self.configure(
            bg=self._tl_hover_bg,
            fg=self._tl_hover_fg,
            relief="raised",
        )


class TLScrollbar(tk.Canvas):
    """
    Curseur TomeLinea issu de la V3.

    Aucun widget Scrollbar Windows n'est utilise.
    """

    def __init__(
        self,
        parent,
        *,
        orient: str,
        command,
    ):

        self.orient = orient
        self.command = command

        width = (
            12
            if orient == "vertical"
            else 1
        )

        height = (
            1
            if orient == "vertical"
            else 12
        )

        super().__init__(
            parent,
            width=width,
            height=height,
            bg=_color(
                "WINDOW_DEEP",
                "#171C22",
            ),
            bd=0,
            highlightthickness=0,
            cursor="hand2",
        )

        self._first = 0.0
        self._last = 1.0

        self._drag_offset = 0.0
        self._dragging = False

        self.bind(
            "<Configure>",
            self._redraw,
        )

        self.bind(
            "<Button-1>",
            self._press,
        )

        self.bind(
            "<B1-Motion>",
            self._drag,
        )

        self.bind(
            "<ButtonRelease-1>",
            self._release,
        )


    def set(
        self,
        first,
        last,
    ):

        try:

            self._first = max(
                0.0,
                min(
                    1.0,
                    float(
                        first
                    ),
                ),
            )

            self._last = max(
                self._first,
                min(
                    1.0,
                    float(
                        last
                    ),
                ),
            )

        except (
            TypeError,
            ValueError,
        ):

            self._first = 0.0
            self._last = 1.0

        self._redraw()


    def _axis_length(
        self,
    ) -> int:

        if (
            self.orient
            == "vertical"
        ):

            return max(
                1,
                self.winfo_height(),
            )

        return max(
            1,
            self.winfo_width(),
        )


    def _cross_length(
        self,
    ) -> int:

        if (
            self.orient
            == "vertical"
        ):

            return max(
                1,
                self.winfo_width(),
            )

        return max(
            1,
            self.winfo_height(),
        )


    def _thumb_geometry(
        self,
    ) -> tuple[float, float]:

        length = (
            self._axis_length()
        )

        start = (
            self._first
            * length
        )

        end = (
            self._last
            * length
        )

        min_thumb = min(
            length,
            28,
        )

        if (
            end - start
            < min_thumb
        ):

            center = (
                start + end
            ) / 2.0

            start = max(
                0.0,
                min(
                    length
                    - min_thumb,
                    center
                    - min_thumb
                    / 2.0,
                ),
            )

            end = min(
                length,
                start
                + min_thumb,
            )

        return (
            start,
            end,
        )


    def _redraw(
        self,
        _event=None,
    ):

        self.delete(
            "all"
        )

        length = (
            self._axis_length()
        )

        cross = (
            self._cross_length()
        )

        rail = _color(
            "BORDER_SOFT",
            _color(
                "PAGE_BORDER",
                "#364048",
            ),
        )

        thumb = _color(
            "ACCENT_DARK",
            _color(
                "ACCENT",
                "#487A79",
            ),
        )

        outline = _color(
            "ACCENT_BRIGHT",
            "#7AB9B5",
        )

        if (
            self.orient
            == "vertical"
        ):

            cx = (
                cross
                / 2.0
            )

            self.create_line(
                cx,
                5,
                cx,
                max(
                    5,
                    length - 5,
                ),
                fill=rail,
                width=2,
            )

        else:

            cy = (
                cross
                / 2.0
            )

            self.create_line(
                5,
                cy,
                max(
                    5,
                    length - 5,
                ),
                cy,
                fill=rail,
                width=2,
            )

        # Rien a afficher si tout le contenu tient.
        if (
            self._last
            >= 0.999
            and self._first
            <= 0.001
        ):
            return

        start, end = (
            self._thumb_geometry()
        )

        pad = 3

        if (
            self.orient
            == "vertical"
        ):

            x1 = pad

            x2 = max(
                pad + 2,
                cross - pad,
            )

            self.create_rectangle(
                x1,
                start,
                x2,
                end,
                fill=thumb,
                outline=outline,
                width=1,
            )

            # Signature or discrete de la V3.
            self.create_line(
                x1 + 1,
                start + 2,
                x2 - 1,
                start + 2,
                fill="#E7C37A",
                width=1,
            )

        else:

            y1 = pad

            y2 = max(
                pad + 2,
                cross - pad,
            )

            self.create_rectangle(
                start,
                y1,
                end,
                y2,
                fill=thumb,
                outline=outline,
                width=1,
            )

            self.create_line(
                start + 2,
                y1 + 1,
                start + 2,
                y2 - 1,
                fill="#E7C37A",
                width=1,
            )


    def _coord(
        self,
        event,
    ) -> float:

        if (
            self.orient
            == "vertical"
        ):

            return float(
                event.y
            )

        return float(
            event.x
        )


    def _press(
        self,
        event,
    ):

        if (
            self._last
            >= 0.999
            and self._first
            <= 0.001
        ):
            return "break"

        position = (
            self._coord(
                event
            )
        )

        start, end = (
            self._thumb_geometry()
        )

        if (
            start
            <= position
            <= end
        ):

            self._dragging = True

            self._drag_offset = (
                position
                - start
            )

        else:

            thumb = max(
                1.0,
                end - start,
            )

            target = (
                position
                - thumb / 2.0
            ) / max(
                1.0,
                self._axis_length()
                - thumb,
            )

            self.command(
                "moveto",
                max(
                    0.0,
                    min(
                        1.0,
                        target,
                    ),
                ),
            )

        return "break"


    def _drag(
        self,
        event,
    ):

        if not self._dragging:
            return "break"

        start, end = (
            self._thumb_geometry()
        )

        thumb = max(
            1.0,
            end - start,
        )

        target = (
            self._coord(
                event
            )
            - self._drag_offset
        ) / max(
            1.0,
            self._axis_length()
            - thumb,
        )

        self.command(
            "moveto",
            max(
                0.0,
                min(
                    1.0,
                    target,
                ),
            ),
        )

        return "break"


    def _release(
        self,
        _event=None,
    ):

        self._dragging = False

        return "break"
