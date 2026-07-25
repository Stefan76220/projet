from __future__ import annotations

from abc import ABC, abstractmethod

from src.engine.foundation import Rect
from src.engine.graphics.transform import Transform
from src.engine.utils import IdGenerator


class Drawable(ABC):
    """
    Classe de base de tous les objets graphiques.
    """

    def __init__(self, bounds: Rect):

        self._id = IdGenerator.next()

        self._transform = Transform(
            position=bounds.origin,
            size=bounds.size,
        )

        self._selected = False
        self._visible = True
        self._z_index = 0

    @property
    def id(self) -> int:
        return self._id

    @property
    def transform(self) -> Transform:
        return self._transform

    @property
    def bounds(self) -> Rect:
        return Rect(
            self._transform.position,
            self._transform.size,
        )

    @property
    def selected(self) -> bool:
        return self._selected

    @property
    def visible(self) -> bool:
        return self._visible

    @property
    def z_index(self) -> int:
        return self._z_index

    def set_visible(self, visible: bool) -> None:
        self._visible = visible

    def set_z_index(self, value: int) -> None:
        self._z_index = value

    def select(self) -> None:
        self._selected = True

    def unselect(self) -> None:
        self._selected = False

    def move(self, dx: float, dy: float) -> None:
        self._transform.move(dx, dy)

    def resize(self, width: float, height: float) -> None:
        self._transform.resize(width, height)

    @abstractmethod
    def draw(self, renderer) -> None:
        raise NotImplementedError