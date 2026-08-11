from __future__ import annotations

import tkinter as tk


class PMCommandButton(tk.Canvas):
    """Bouton de commande universel PageMaître, dessiné en code."""

    PALETTES = {
        "green": "#86A978",
        "blue": "#729DCC",
        "violet": "#A486CC",
        "coral": "#DF806B",
        "gold": "#C8A85C",
        "neutral": "#8E948D",
    }

    SIZES = {
        "sm": {"height": 34, "font": 9, "shadow": 3, "radius": 11},
        "md": {"height": 42, "font": 10, "shadow": 4, "radius": 13},
        "lg": {"height": 50, "font": 11, "shadow": 5, "radius": 15},
    }

    def __init__(
        self,
        parent,
        *,
        text: str,
        command=None,
        color: str = "green",
        size: str = "md",
        icon: str | None = "✦",
        width: int = 182,
        enabled: bool = True,
    ) -> None:
        self._parent_bg = self._read_parent_bg(parent)
        self._preset = self.SIZES.get(size, self.SIZES["md"])
        self._button_width = width
        self._face_height = self._preset["height"]
        self._shadow_depth = self._preset["shadow"]
        total_height = self._face_height + self._shadow_depth + 3

        super().__init__(
            parent,
            width=width,
            height=total_height,
            bg=self._parent_bg,
            highlightthickness=0,
            bd=0,
            relief="flat",
            cursor="hand2" if enabled else "arrow",
        )

        self._text = text
        self._command = command
        self._icon = icon
        self._color = color
        self._enabled = enabled
        self._state = "normal" if enabled else "disabled"
        self._pressed = False

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self.bind("<Configure>", self._on_configure)
        self._draw()

    @staticmethod
    def _read_parent_bg(parent) -> str:
        try:
            return parent.cget("bg")
        except Exception:
            return "#F8F4EC"

    @staticmethod
    def _hex_to_rgb(value: str) -> tuple[int, int, int]:
        value = value.lstrip("#")
        return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))

    @classmethod
    def _mix(cls, a: str, b: str, ratio: float) -> str:
        ratio = max(0.0, min(1.0, ratio))
        ar, ag, ab = cls._hex_to_rgb(a)
        br, bg, bb = cls._hex_to_rgb(b)
        r = round(ar * (1 - ratio) + br * ratio)
        g = round(ag * (1 - ratio) + bg * ratio)
        bl = round(ab * (1 - ratio) + bb * ratio)
        return f"#{r:02X}{g:02X}{bl:02X}"

    def _base_color(self) -> str:
        if self._color.startswith("#"):
            return self._color
        return self.PALETTES.get(self._color, self.PALETTES["green"])

    def _palette(self) -> dict[str, str]:
        base = self._base_color()
        if self._state == "disabled":
            return {
                "face": "#F0F1EC",
                "rim": "#D3D7CC",
                "text": "#A5AA9F",
                "shadow1": self._parent_bg,
                "shadow2": self._parent_bg,
                "shine": "#FFFFFF",
            }

        if self._state == "hover":
            face = self._mix(base, "#FFFFFF", 0.76)
            shadow1 = self._mix(base, "#53654F", 0.36)
            shadow2 = self._mix(base, "#6B8066", 0.50)
        elif self._state == "pressed":
            face = self._mix(base, "#FFFFFF", 0.64)
            shadow1 = self._mix(base, "#4B5D48", 0.33)
            shadow2 = self._mix(base, "#60735C", 0.44)
        else:
            face = self._mix(base, "#FFFFFF", 0.82)
            shadow1 = self._mix(base, "#53654F", 0.38)
            shadow2 = self._mix(base, "#6B8066", 0.53)

        return {
            "face": face,
            "rim": self._mix(base, "#64775F", 0.28),
            "text": self._mix(base, "#203023", 0.60),
            "shadow1": shadow1,
            "shadow2": shadow2,
            "shine": self._mix(base, "#FFFFFF", 0.94),
        }

    def _rounded_rect(self, x1, y1, x2, y2, radius, *, fill, outline="", width=1):
        r = max(1, min(radius, (x2 - x1) / 2, (y2 - y1) / 2))
        points = [
            x1 + r, y1,
            x2 - r, y1,
            x2, y1,
            x2, y1 + r,
            x2, y2 - r,
            x2, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1, y2,
            x1, y2 - r,
            x1, y1 + r,
            x1, y1,
        ]
        return self.create_polygon(
            points,
            smooth=True,
            splinesteps=24,
            fill=fill,
            outline=outline,
            width=width,
        )

    def _draw(self) -> None:
        self.delete("all")
        w = max(self.winfo_width(), self._button_width)
        face_h = self._face_height
        radius = self._preset["radius"]
        colors = self._palette()

        press_offset = 2 if self._state == "pressed" else 0
        lift = 1 if self._state == "hover" else 0

        # Relief profond doux : deux niveaux d'ombre, puis la face.
        self._rounded_rect(
            4,
            self._shadow_depth + 2,
            w - 4,
            face_h + self._shadow_depth,
            radius,
            fill=colors["shadow1"],
        )
        self._rounded_rect(
            3,
            self._shadow_depth,
            w - 3,
            face_h + self._shadow_depth - 1,
            radius,
            fill=colors["shadow2"],
        )

        y1 = 1 + press_offset - lift
        y2 = face_h + press_offset - lift
        self._rounded_rect(
            1,
            y1,
            w - 1,
            y2,
            radius,
            fill=colors["rim"],
        )
        self._rounded_rect(
            2,
            y1 + 1,
            w - 2,
            y2 - 1,
            max(3, radius - 1),
            fill=colors["face"],
        )

        # Filet supérieur très léger pour l'effet de matière.
        self.create_line(
            14,
            y1 + 3,
            w - 14,
            y1 + 3,
            fill=colors["shine"],
            width=1,
        )

        label = f"{self._icon}   {self._text}" if self._icon else self._text
        self.create_text(
            w / 2,
            y1 + face_h / 2 - 1,
            text=label,
            fill=colors["text"],
            font=("Segoe UI", self._preset["font"], "bold"),
            anchor="center",
        )

    def _on_configure(self, _event=None) -> None:
        self._draw()

    def _on_enter(self, _event=None) -> None:
        if self._enabled and not self._pressed:
            self._state = "hover"
            self._draw()

    def _on_leave(self, _event=None) -> None:
        if self._enabled:
            self._pressed = False
            self._state = "normal"
            self._draw()

    def _on_press(self, _event=None) -> None:
        if not self._enabled:
            return
        self._pressed = True
        self._state = "pressed"
        self._draw()

    def _on_release(self, event) -> None:
        if not self._enabled:
            return
        self._pressed = False
        inside = 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height()
        self._state = "hover" if inside else "normal"
        self._draw()
        if inside and callable(self._command):
            self.after_idle(self._command)

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        self._state = "normal" if enabled else "disabled"
        self.configure(cursor="hand2" if enabled else "arrow")
        self._draw()

    def set_text(self, text: str) -> None:
        self._text = text
        self._draw()

    def set_color(self, color: str) -> None:
        self._color = color
        self._draw()

    def set_icon(self, icon: str | None) -> None:
        self._icon = icon
        self._draw()
