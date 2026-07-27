from __future__ import annotations

from dataclasses import dataclass

from .style import Style


@dataclass(slots=True, frozen=True)
class Shadow(Style):
    """
    Décrit une ombre portée.
    """

    color: str = "#666666"
    offset_x: float = 4.0
    offset_y: float = 4.0
    blur: float = 0.0
    spread: float = 0.0

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def with_color(
        self,
        color: str,
    ) -> "Shadow":

        return self.copy(color=color)

    def with_offset(
        self,
        offset_x: float,
        offset_y: float,
    ) -> "Shadow":

        return self.copy(
            offset_x=offset_x,
            offset_y=offset_y,
        )

    def with_blur(
        self,
        blur: float,
    ) -> "Shadow":

        return self.copy(blur=blur)

    def with_spread(
        self,
        spread: float,
    ) -> "Shadow":

        return self.copy(spread=spread)