from __future__ import annotations

from dataclasses import dataclass, field

from .shadow import Shadow
from .stroke import Stroke
from .style import Style


@dataclass(slots=True, frozen=True)
class ImageStyle(Style):
    """
    Style complet d'une image.
    """

    stroke: Stroke = field(default_factory=Stroke)
    shadow: Shadow = field(default_factory=Shadow)

    opacity: float = 1.0

    keep_aspect_ratio: bool = True
    smoothing: bool = True

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def with_stroke(
        self,
        stroke: Stroke,
    ) -> "ImageStyle":

        return self.copy(stroke=stroke)

    def with_shadow(
        self,
        shadow: Shadow,
    ) -> "ImageStyle":

        return self.copy(shadow=shadow)

    def with_opacity(
        self,
        opacity: float,
    ) -> "ImageStyle":

        return self.copy(opacity=opacity)

    def with_keep_aspect_ratio(
        self,
        keep_aspect_ratio: bool,
    ) -> "ImageStyle":

        return self.copy(
            keep_aspect_ratio=keep_aspect_ratio,
        )

    def with_smoothing(
        self,
        smoothing: bool,
    ) -> "ImageStyle":

        return self.copy(smoothing=smoothing)