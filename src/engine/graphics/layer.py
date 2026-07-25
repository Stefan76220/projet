from __future__ import annotations

from src.engine.graphics.drawable import Drawable


class Layer:
    """
    Une couche contient des objets graphiques.
    """

    def __init__(self):

        self._drawables: list[Drawable] = []

    def add(self, drawable: Drawable) -> None:

        if drawable in self._drawables:
            return

        drawable.set_z_index(len(self._drawables))
        self._drawables.append(drawable)

    def remove(self, drawable: Drawable) -> None:

        if drawable not in self._drawables:
            return

        self._drawables.remove(drawable)

        for index, item in enumerate(self._drawables):
            item.set_z_index(index)

    def clear(self) -> None:

        self._drawables.clear()

    def get_by_id(self, drawable_id: int) -> Drawable | None:

        for drawable in self._drawables:
            if drawable.id == drawable_id:
                return drawable

        return None

    def drawables(self) -> list[Drawable]:

        return sorted(
            self._drawables,
            key=lambda drawable: drawable.z_index,
        )

    def __iter__(self):
        return iter(self._drawables)

    def __len__(self):
        return len(self._drawables)