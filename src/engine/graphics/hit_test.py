from __future__ import annotations

from src.engine.foundation import Point

from .drawable import Drawable
from .page import Page


class HitTest:
    """
    Recherche l'objet graphique situé sous un point.
    """

    @staticmethod
    def drawable_at(
        page: Page,
        point: Point,
    ) -> Drawable | None:

        for layer in reversed(page.layers):

            if not layer.visible:
                continue

            drawables = sorted(
                layer,
                key=lambda drawable: drawable.z_index,
                reverse=True,
            )

            for drawable in drawables:

                if not drawable.visible:
                    continue

                if drawable.contains(point):
                    return drawable

        return None