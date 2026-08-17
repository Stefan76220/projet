from __future__ import annotations

from dataclasses import dataclass


TL_NAVY = "#173B6C"
TL_INK = "#24384D"
TL_WHITE = "#FFFFFF"
TL_NEUTRAL_SHADOW = "#CDD2D6"


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def mix(a: str, b: str, amount: float) -> str:
    """amount=0 -> a ; amount=1 -> b"""
    amount = max(0.0, min(1.0, amount))
    ar, ag, ab = _hex_to_rgb(a)
    br, bg, bb = _hex_to_rgb(b)
    return _rgb_to_hex((
        round(ar + (br - ar) * amount),
        round(ag + (bg - ag) * amount),
        round(ab + (bb - ab) * amount),
    ))


def rounded_rect(canvas, x1, y1, x2, y2, radius, **kwargs):
    radius = max(1, min(radius, (x2 - x1) / 2, (y2 - y1) / 2))
    points = [
        x1 + radius, y1,
        x2 - radius, y1,
        x2, y1,
        x2, y1 + radius,
        x2, y2 - radius,
        x2, y2,
        x2 - radius, y2,
        x1 + radius, y2,
        x1, y2,
        x1, y2 - radius,
        x1, y1 + radius,
        x1, y1,
    ]
    return canvas.create_polygon(
        points,
        smooth=True,
        splinesteps=28,
        **kwargs,
    )


@dataclass(frozen=True)
class TLCommandButton:
    """Référence unique pour toutes les vraies commandes TomeLinea."""

    tag: str
    text: str
    cx: float
    cy: float
    min_width: int = 108
    height: int = 36

    def draw(self, canvas, state: str = "normal"):
        # Une seule couleur de commande dans tout TomeLinea.
        accent = TL_NAVY
        height = 36  # hauteur volontairement figée
        width = max(108, self.min_width, int(len(self.text) * 7.2) + 34)

        pressed = state == "pressed"
        hover = state == "hover"
        dy = 1 if pressed else 0

        x1 = self.cx - width / 2
        x2 = self.cx + width / 2
        y1 = self.cy - height / 2 + dy
        y2 = self.cy + height / 2 + dy

        if pressed:
            face = mix(accent, TL_WHITE, 0.88)
            outline = mix(accent, TL_WHITE, 0.18)
            shadow_offset = 1
            shadow = mix(accent, "#8E969E", 0.72)
        elif hover:
            face = mix(accent, TL_WHITE, 0.93)
            outline = mix(accent, TL_WHITE, 0.04)
            shadow_offset = 3
            shadow = mix(accent, "#9EA6AD", 0.80)
        else:
            face = mix(accent, TL_WHITE, 0.965)
            outline = mix(accent, TL_WHITE, 0.42)
            shadow_offset = 2
            shadow = TL_NEUTRAL_SHADOW

        # Ombre neutre : volume léger, pas d'effet plastique.
        rounded_rect(
            canvas,
            x1 + 1,
            y1 + shadow_offset,
            x2 + 1,
            y2 + shadow_offset,
            11,
            fill=shadow,
            outline="",
            tags=(self.tag, "tl_command"),
        )

        # Surface claire très légèrement bleutée.
        rounded_rect(
            canvas,
            x1,
            y1,
            x2,
            y2,
            11,
            fill=face,
            outline=outline,
            width=1 if not hover else 2,
            tags=(self.tag, "tl_command"),
        )

        # Trait intérieur extrêmement discret, sans reflet horizontal.
        rounded_rect(
            canvas,
            x1 + 2,
            y1 + 2,
            x2 - 2,
            y2 - 2,
            9,
            fill="",
            outline=mix(accent, TL_WHITE, 0.86),
            width=1,
            tags=(self.tag, "tl_command"),
        )

        canvas.create_text(
            self.cx,
            self.cy - 1 + dy,
            text=self.text,
            fill=TL_NAVY,
            font=("Segoe UI", 9, "bold"),
            anchor="center",
            tags=(self.tag, "tl_command"),
        )
        return x1, y1, x2, y2


@dataclass(frozen=True)
class TLChoiceCard:
    """Référence unique des cartes de sélection TomeLinea."""

    tag: str
    x1: float
    y1: float
    x2: float
    y2: float
    accent: str
    selected: bool = False

    def draw(self, canvas, state: str = "normal") -> int:
        pressed = state == "pressed"
        hover = state == "hover"
        dy = 1 if pressed else 0

        x1 = self.x1
        x2 = self.x2
        y1 = self.y1 + dy
        y2 = self.y2 + dy

        if self.selected:
            face_mix = 0.875 if not hover else 0.84
            border_mix = 0.08
            border_width = 2
        elif hover:
            face_mix = 0.915
            border_mix = 0.28
            border_width = 1
        else:
            face_mix = 0.955
            border_mix = 0.48
            border_width = 1

        face = mix(self.accent, TL_WHITE, face_mix)
        border = mix(self.accent, TL_WHITE, border_mix)
        shadow = mix(self.accent, "#A7A7A4", 0.86)
        shadow_offset = 1 if pressed else (3 if hover else 2)

        # Ombre plus faible que celle d'un bouton : c'est un choix, pas une commande.
        rounded_rect(
            canvas,
            x1 + 1,
            y1 + shadow_offset,
            x2 + 1,
            y2 + shadow_offset,
            14,
            fill=shadow,
            outline="",
            tags=(self.tag, "home_choice", "tl_choice"),
        )

        rounded_rect(
            canvas,
            x1,
            y1,
            x2,
            y2,
            14,
            fill=face,
            outline=border,
            width=border_width,
            tags=(self.tag, "home_choice", "tl_choice"),
        )

        # Un très léger filet intérieur suffit à donner une finition premium.
        rounded_rect(
            canvas,
            x1 + 3,
            y1 + 3,
            x2 - 3,
            y2 - 3,
            11,
            fill="",
            outline=mix(self.accent, TL_WHITE, 0.88),
            width=1,
            tags=(self.tag, "home_choice", "tl_choice"),
        )

        return dy

@dataclass(frozen=True)
class TLShortcutCard:
    """Tuile de navigation TomeLinea : sobre, légère et immédiatement identifiable."""

    tag: str
    x1: float
    y1: float
    x2: float
    y2: float
    accent: str
    title: str
    subtitle: str

    def draw(self, canvas, state: str = "normal") -> int:
        pressed = state == "pressed"
        hover = state == "hover"
        dy = 1 if pressed else 0

        x1 = self.x1
        x2 = self.x2
        y1 = self.y1 + dy
        y2 = self.y2 + dy

        if pressed:
            face = mix(self.accent, TL_WHITE, 0.965)
            border = mix(self.accent, TL_WHITE, 0.50)
            shadow_offset = 1
        elif hover:
            face = mix(self.accent, TL_WHITE, 0.955)
            border = mix(self.accent, TL_WHITE, 0.34)
            shadow_offset = 3
        else:
            face = "#FCFCFB"
            border = "#D8DADD"
            shadow_offset = 2

        shadow = "#D4D7DA"

        rounded_rect(
            canvas,
            x1 + 1,
            y1 + shadow_offset,
            x2 + 1,
            y2 + shadow_offset,
            11,
            fill=shadow,
            outline="",
            tags=(self.tag, "home_shortcuts", "tl_shortcut"),
        )

        rounded_rect(
            canvas,
            x1,
            y1,
            x2,
            y2,
            11,
            fill=face,
            outline=border,
            width=1 if not hover else 2,
            tags=(self.tag, "home_shortcuts", "tl_shortcut"),
        )

        station_x = x1 + 17
        station_y = y1 + 17

        canvas.create_oval(
            station_x - 6,
            station_y - 6,
            station_x + 6,
            station_y + 6,
            fill=mix(self.accent, TL_WHITE, 0.82),
            outline=self.accent,
            width=1,
            tags=(self.tag, "home_shortcuts", "tl_shortcut"),
        )
        canvas.create_oval(
            station_x - 2.5,
            station_y - 2.5,
            station_x + 2.5,
            station_y + 2.5,
            fill=self.accent,
            outline="",
            tags=(self.tag, "home_shortcuts", "tl_shortcut"),
        )

        canvas.create_text(
            x1 + 31,
            y1 + 17,
            text=self.title,
            fill=TL_NAVY,
            font=("Segoe UI", 8, "bold"),
            anchor="w",
            tags=(self.tag, "home_shortcuts", "tl_shortcut"),
        )

        canvas.create_text(
            x1 + 12,
            y1 + 39,
            text=self.subtitle,
            fill="#53606B",
            font=("Segoe UI", 7),
            anchor="w",
            tags=(self.tag, "home_shortcuts", "tl_shortcut"),
        )

        return dy

