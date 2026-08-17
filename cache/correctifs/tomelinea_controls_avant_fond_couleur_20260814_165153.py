from __future__ import annotations

from dataclasses import dataclass

TL_PANEL = "#34373D"
TL_HOVER = "#3A3E45"
TL_PRESSED = "#2E3137"
TL_ACTIVE = "#40444B"
TL_BORDER = "#4C515A"
TL_SHADOW = "#21242A"
TL_TEXT = "#F1F2F4"
TL_MUTED = "#B6BBC3"
TL_WHITE = "#FFFFFF"


def _hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return tuple(int(value[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def mix(a: str, b: str, amount: float) -> str:
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
    return canvas.create_polygon(points, smooth=True, splinesteps=28, **kwargs)


@dataclass(frozen=True)
class TLCommandButton:
    tag: str
    text: str
    cx: float
    cy: float
    min_width: int = 108
    height: int = 36

    def draw(self, canvas, state: str = "normal"):
        height = 36
        width = max(108, self.min_width, int(len(self.text) * 7.2) + 34)
        pressed = state == "pressed"
        hover = state == "hover"
        dy = 1 if pressed else 0
        x1 = self.cx - width / 2
        x2 = self.cx + width / 2
        y1 = self.cy - height / 2 + dy
        y2 = self.cy + height / 2 + dy
        if pressed:
            face, outline, shadow_offset = TL_PRESSED, "#59606A", 1
        elif hover:
            face, outline, shadow_offset = TL_HOVER, "#646A74", 2
        else:
            face, outline, shadow_offset = TL_PANEL, TL_BORDER, 2
        rounded_rect(canvas, x1+1, y1+shadow_offset, x2+1, y2+shadow_offset, 11,
                     fill=TL_SHADOW, outline="", tags=(self.tag,"tl_command"))
        rounded_rect(canvas, x1,y1,x2,y2,11, fill=face, outline=outline,
                     width=1 if not hover else 2, tags=(self.tag,"tl_command"))
        rounded_rect(canvas, x1+2,y1+2,x2-2,y2-2,9, fill="",
                     outline=mix(outline,face,0.56), width=1, tags=(self.tag,"tl_command"))
        canvas.create_text(self.cx,self.cy-1+dy,text=self.text,fill=TL_TEXT,
                           font=("Segoe UI",9,"bold"),anchor="center",tags=(self.tag,"tl_command"))
        return x1,y1,x2,y2


@dataclass(frozen=True)
class TLChoiceCard:
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
        x1,x2,y1,y2=self.x1,self.x2,self.y1+dy,self.y2+dy
        if pressed: face=TL_PRESSED
        elif self.selected: face=TL_ACTIVE
        elif hover: face=TL_HOVER
        else: face=TL_PANEL
        border=self.accent if self.selected else TL_BORDER
        bw=2 if self.selected or hover else 1
        so=1 if pressed else (3 if hover else 2)
        rounded_rect(canvas,x1+1,y1+so,x2+1,y2+so,14,fill=TL_SHADOW,outline="",
                     tags=(self.tag,"home_choice","tl_choice"))
        rounded_rect(canvas,x1,y1,x2,y2,14,fill=face,outline=border,width=bw,
                     tags=(self.tag,"home_choice","tl_choice"))
        rounded_rect(canvas,x1+3,y1+3,x2-3,y2-3,11,fill="",outline=mix(border,face,0.65),width=1,
                     tags=(self.tag,"home_choice","tl_choice"))
        return dy


@dataclass(frozen=True)
class TLShortcutCard:
    tag: str
    x1: float
    y1: float
    x2: float
    y2: float
    accent: str
    title: str
    subtitle: str

    def draw(self, canvas, state: str = "normal") -> int:
        pressed=state=="pressed"
        hover=state=="hover"
        dy=1 if pressed else 0
        x1,x2,y1,y2=self.x1,self.x2,self.y1+dy,self.y2+dy
        if pressed: face,so=TL_PRESSED,1
        elif hover: face,so=TL_HOVER,3
        else: face,so=TL_PANEL,2
        rounded_rect(canvas,x1+1,y1+so,x2+1,y2+so,11,fill=TL_SHADOW,outline="",
                     tags=(self.tag,"home_shortcuts","tl_shortcut"))
        rounded_rect(canvas,x1,y1,x2,y2,11,fill=face,outline=TL_BORDER,width=1 if not hover else 2,
                     tags=(self.tag,"home_shortcuts","tl_shortcut"))
        station_x=x1+17; station_y=y1+17
        canvas.create_oval(station_x-6,station_y-6,station_x+6,station_y+6,
                           fill=mix(self.accent,TL_PANEL,0.70),outline=self.accent,width=1,
                           tags=(self.tag,"home_shortcuts","tl_shortcut"))
        canvas.create_oval(station_x-2.5,station_y-2.5,station_x+2.5,station_y+2.5,
                           fill=self.accent,outline="",tags=(self.tag,"home_shortcuts","tl_shortcut"))
        canvas.create_text(x1+31,y1+17,text=self.title,fill=TL_TEXT,font=("Segoe UI",8,"bold"),
                           anchor="w",tags=(self.tag,"home_shortcuts","tl_shortcut"))
        canvas.create_text(x1+12,y1+39,text=self.subtitle,fill=TL_MUTED,font=("Segoe UI",7),
                           anchor="w",tags=(self.tag,"home_shortcuts","tl_shortcut"))
        return dy
