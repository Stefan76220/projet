from __future__ import annotations

from src.engine.foundation import Rect
from src.engine.graphics.drawable import Drawable
from src.engine.graphics.layer import Layer


class Page(Drawable):
    """
    Une page contient plusieurs couches.
    """

    def __init__(self, bounds: Rect):

        super().__init__(bounds)

        self._layers: list[Layer] = []

    def add_layer(self, layer: Layer) -> None:

        if layer not in self._layers:
            self._layers.append(layer)

    def remove_layer(self, layer: Layer) -> None:

        if layer in self._layers:
            self._layers.remove(layer)

    def layer(self, index: int) -> Layer:
        return self._layers[index]

    @property
    def layers(self) -> tuple[Layer, ...]:
        return tuple(self._layers)

    def draw(self, renderer) -> None:

        renderer.draw_page(self)

        for layer in self._layers:
            for drawable in layer.drawables():
                if drawable.visible:
                    renderer.draw_drawable(drawable)