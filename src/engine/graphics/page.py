from __future__ import annotations

from src.engine.container import Container
from src.engine.foundation import Rect

from .layer import Layer
from .styles import PageStyle


class Page(Container[Layer]):
    """
    Représente une page du document.

    Une page est un conteneur de calques et possède ses
    paramètres de mise en page.
    """

    def __init__(
        self,
        bounds: Rect,
        style: PageStyle | None = None,
    ) -> None:

        super().__init__()

        # ==========================================================
        # Géométrie
        # ==========================================================

        self.bounds = bounds

        # ==========================================================
        # Apparence
        # ==========================================================

        self.style = style or PageStyle()

        # ==========================================================
        # Mise en page
        # ==========================================================

        self.margin_left = 0.0
        self.margin_right = 0.0
        self.margin_top = 0.0
        self.margin_bottom = 0.0

        self.bleed = 0.0

        self.show_margins = False
        self.show_bleed = False
        self.show_safe_area = False
        self.show_grid = False
        self.show_guides = True

    # ==========================================================
    # Calques
    # ==========================================================

    def add_layer(
        self,
        layer: Layer,
    ) -> None:

        if layer not in self:
            super().add(layer)

    def remove_layer(
        self,
        layer: Layer,
    ) -> None:

        if layer in self:
            super().remove(layer)

    def clear_layers(self) -> None:

        super().clear()

    def layer(
        self,
        index: int,
    ) -> Layer:

        return self[index]

    @property
    def layers(self) -> tuple[Layer, ...]:
        return self.children

    @property
    def layer_count(self) -> int:
        return self.count

    @property
    def has_layers(self) -> bool:
        return not self.is_empty

    @property
    def first_layer(self) -> Layer | None:
        return self.first

    @property
    def last_layer(self) -> Layer | None:
        return self.last

    # ==========================================================
    # Rendu
    # ==========================================================

    def draw(
        self,
        renderer,
    ) -> None:

        renderer.draw_page(self)

        for layer in self:

            if not layer.visible:
                continue

            for drawable in layer:

                if drawable.visible:
                    renderer.draw_drawable(drawable)

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __iter__(self):

        return iter(self.children)