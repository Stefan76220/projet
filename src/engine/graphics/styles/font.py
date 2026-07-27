from __future__ import annotations

from dataclasses import dataclass

from .style import Style


@dataclass(slots=True, frozen=True)
class Font(Style):
    """
    Décrit les propriétés typographiques.
    """

    family: str = "Arial"
    size: float = 12.0
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strike: bool = False
    color: str = "#000000"
    line_spacing: float = 1.0
    letter_spacing: float = 0.0

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def with_family(
        self,
        family: str,
    ) -> "Font":

        return self.copy(family=family)

    def with_size(
        self,
        size: float,
    ) -> "Font":

        return self.copy(size=size)

    def with_color(
        self,
        color: str,
    ) -> "Font":

        return self.copy(color=color)

    def with_bold(
        self,
        bold: bool,
    ) -> "Font":

        return self.copy(bold=bold)

    def with_italic(
        self,
        italic: bool,
    ) -> "Font":

        return self.copy(italic=italic)

    def with_underline(
        self,
        underline: bool,
    ) -> "Font":

        return self.copy(underline=underline)

    def with_strike(
        self,
        strike: bool,
    ) -> "Font":

        return self.copy(strike=strike)

    def with_line_spacing(
        self,
        line_spacing: float,
    ) -> "Font":

        return self.copy(line_spacing=line_spacing)

    def with_letter_spacing(
        self,
        letter_spacing: float,
    ) -> "Font":

        return self.copy(letter_spacing=letter_spacing)