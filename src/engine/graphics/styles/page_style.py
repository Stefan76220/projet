from __future__ import annotations

from dataclasses import dataclass, field

from .fill import Fill
from .shadow import Shadow
from .stroke import Stroke
from .style import Style


@dataclass(slots=True, frozen=True)
class PageStyle(Style):
    """
    Style d'affichage d'une page.

    Il décrit uniquement son apparence et ne contient
    aucune information de mise en page.
    """

    fill: Fill = field(
        default_factory=lambda: Fill(
            color="#FFFFFF",
        )
    )

    stroke: Stroke = field(
        default_factory=lambda: Stroke(
            color="#B5B5B5",
            width=1.0,
        )
    )

    shadow: Shadow = field(
        default_factory=lambda: Shadow(
            color="#808080",
            offset_x=6.0,
            offset_y=6.0,
            blur=0.0,
            spread=0.0,
        )
    )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def with_fill(
        self,
        fill: Fill,
    ) -> "PageStyle":

        return self.copy(fill=fill)

    def with_stroke(
        self,
        stroke: Stroke,
    ) -> "PageStyle":

        return self.copy(stroke=stroke)

    def with_shadow(
        self,
        shadow: Shadow,
    ) -> "PageStyle":

        return self.copy(shadow=shadow)