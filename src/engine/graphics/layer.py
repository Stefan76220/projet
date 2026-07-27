from __future__ import annotations

from src.engine.container import Container

from .drawable import Drawable


class Layer(Container[Drawable]):
    """
    Représente un calque d'une page.

    Un calque est un conteneur d'objets graphiques.
    """

    def __init__(self) -> None:

        super().__init__()

        self.name: str = "Calque"
        self.visible: bool = True
        self.locked: bool = False

    # ==========================================================
    # Gestion des objets
    # ==========================================================

    def add(
        self,
        drawable: Drawable,
    ) -> None:

        if drawable in self:
            return

        drawable.set_z_index(self.count)

        super().add(drawable)

    def remove(
        self,
        drawable: Drawable,
    ) -> None:

        if drawable not in self:
            return

        super().remove(drawable)

        self._update_z_index()

    def clear(self) -> None:

        super().clear()

    def drawable(
        self,
        index: int,
    ) -> Drawable:

        return self[index]

    @property
    def drawables(self) -> tuple[Drawable, ...]:

        return self.children

    @property
    def drawable_count(self) -> int:

        return self.count

    @property
    def has_drawables(self) -> bool:

        return not self.is_empty

    @property
    def first_drawable(self) -> Drawable | None:

        return self.first

    @property
    def last_drawable(self) -> Drawable | None:

        return self.last

    # ==========================================================
    # Recherche
    # ==========================================================

    def get_by_id(
        self,
        drawable_id: int,
    ) -> Drawable | None:

        for drawable in self:

            if drawable.id == drawable_id:
                return drawable

        return None

    # ==========================================================
    # Outils internes
    # ==========================================================

    def _update_z_index(self) -> None:

        for index, drawable in enumerate(self):

            drawable.set_z_index(index)

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __iter__(self):

        return iter(self.children)