from __future__ import annotations

from dataclasses import dataclass, field

from .fill import Fill
from .font import Font
from .shadow import Shadow
from .stroke import Stroke
from .style import Style


@dataclass(slots=True, frozen=True)
class TextStyle(Style):
    """
    Style complet d'un objet texte.
    """

    font: Font = field(default_factory=Font)

    fill: Fill = field(
        default_factory=lambda: Fill(
            color="#000000",
        )
    )

    stroke: Stroke = field(default_factory=Stroke)

    shadow: Shadow = field(default_factory=Shadow)

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def with_font(
        self,
        font: Font,
    ) -> "TextStyle":

        return self.copy(font=font)

    def with_fill(
        self,
        fill: Fill,
    ) -> "TextStyle":

        return self.copy(fill=fill)

    def with_stroke(
        self,
        stroke: Stroke,
    ) -> "TextStyle":

        return self.copy(stroke=stroke)

    def with_shadow(
        self,
        shadow: Shadow,
    ) -> "TextStyle":

        return self.copy(shadow=shadow)