from __future__ import annotations

from src.engine.foundation import Point
from src.engine.graphics import Drawable, Layer, Page


class HitTest:
    """
    Recherche l'objet situé sous un point.
    """

    @staticmethod
    def drawable_at(page: Page, point: Point) -> Drawable | None:

        for layer in reversed(page.layers):

            drawables = sorted(
                layer.drawables(),
                key=lambda drawable: drawable.z_index,
                reverse=True,
            )

            for drawable in drawables:

                if not drawable.visible:
                    continue

                if drawable.bounds.contains(point):
                    return drawable

        return None