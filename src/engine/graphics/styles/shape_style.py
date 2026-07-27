from __future__ import annotations

from dataclasses import dataclass, field

from .fill import Fill
from .shadow import Shadow
from .stroke import Stroke
from .style import Style


@dataclass(slots=True, frozen=True)
class ShapeStyle(Style):
    """
    Style complet d'une forme graphique.

    Il regroupe les différents sous-styles nécessaires
    au rendu d'une forme.
    """

    fill: Fill = field(default_factory=Fill)
    stroke: Stroke = field(default_factory=Stroke)
    shadow: Shadow = field(default_factory=Shadow)

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def with_fill(
        self,
        fill: Fill,
    ) -> "ShapeStyle":

        return self.copy(fill=fill)

    def with_stroke(
        self,
        stroke: Stroke,
    ) -> "ShapeStyle":

        return self.copy(stroke=stroke)

    def with_shadow(
        self,
        shadow: Shadow,
    ) -> "ShapeStyle":

        return self.copy(shadow=shadow)