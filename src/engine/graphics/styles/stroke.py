from __future__ import annotations

from dataclasses import dataclass

from .style import Style


@dataclass(slots=True, frozen=True)
class Stroke(Style):
    """
    Décrit le contour d'un objet graphique.
    """

    color: str = "#000000"
    width: float = 1.0
    dash: tuple[float, ...] = ()
    line_join: str = "miter"
    line_cap: str = "butt"

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def with_color(
        self,
        color: str,
    ) -> "Stroke":

        return self.copy(color=color)

    def with_width(
        self,
        width: float,
    ) -> "Stroke":

        return self.copy(width=width)

    def with_dash(
        self,
        dash: tuple[float, ...],
    ) -> "Stroke":

        return self.copy(dash=dash)

    def with_line_join(
        self,
        line_join: str,
    ) -> "Stroke":

        return self.copy(line_join=line_join)

    def with_line_cap(
        self,
        line_cap: str,
    ) -> "Stroke":

        return self.copy(line_cap=line_cap)