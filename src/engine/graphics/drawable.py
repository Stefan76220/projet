from __future__ import annotations

from abc import ABC, abstractmethod

from src.engine.foundation import Rect
from src.engine.utils import IdGenerator

from .constraints import Constraints
from .interaction_state import InteractionState
from .selection_state import SelectionState
from .styles import Style
from .transform import Transform


class Drawable(ABC):
    """
    Classe de base de tous les objets graphiques.
    """

    def __init__(
        self,
        bounds: Rect,
        style: Style | None = None,
    ) -> None:

        self._id = IdGenerator.next()

        self._transform = Transform(
            position=bounds.origin,
            size=bounds.size,
        )

        self._style = style or Style()

        self._selection = SelectionState()
        self._interaction = InteractionState()
        self._constraints = Constraints()

        self._visible = True
        self._locked = False
        self._z_index = 0

    @property
    def id(self) -> int:
        return self._id

    @property
    def transform(self) -> Transform:
        return self._transform

    @property
    def bounds(self) -> Rect:
        return self._transform.bounds

    @property
    def style(self) -> Style:
        return self._style

    def set_style(
        self,
        style: Style,
    ) -> None:
        self._style = style

    @property
    def selection(self) -> SelectionState:
        return self._selection

    @property
    def interaction(self) -> InteractionState:
        return self._interaction

    @property
    def constraints(self) -> Constraints:
        return self._constraints

    @property
    def visible(self) -> bool:
        return self._visible

    def set_visible(
        self,
        value: bool,
    ) -> None:
        self._visible = value

    @property
    def locked(self) -> bool:
        return self._locked

    def set_locked(
        self,
        value: bool,
    ) -> None:
        self._locked = value

    @property
    def z_index(self) -> int:
        return self._z_index

    def set_z_index(
        self,
        value: int,
    ) -> None:
        self._z_index = value

    @abstractmethod
    def clone(self):
        ...

    @abstractmethod
    def draw(
        self,
        renderer,
    ) -> None:
        ...

    @abstractmethod
    def contains(
        self,
        point,
    ) -> bool:
        ...