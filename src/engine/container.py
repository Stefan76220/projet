from __future__ import annotations

from collections.abc import Iterable, Iterator
from typing import Generic, TypeVar


T = TypeVar("T")


class Container(Generic[T]):
    """
    Conteneur générique.

    Classe de base de tous les conteneurs du moteur.
    """

    def __init__(self) -> None:

        self._children: list[T] = []

    # ==========================================================
    # Gestion
    # ==========================================================

    def add(
        self,
        child: T,
    ) -> None:

        self._children.append(child)

    def extend(
        self,
        children: Iterable[T],
    ) -> None:

        self._children.extend(children)

    def insert(
        self,
        index: int,
        child: T,
    ) -> None:

        self._children.insert(index, child)

    def remove(
        self,
        child: T,
    ) -> None:

        self._children.remove(child)

    def pop(
        self,
        index: int = -1,
    ) -> T:

        return self._children.pop(index)

    def clear(self) -> None:

        self._children.clear()

    # ==========================================================
    # Recherche
    # ==========================================================

    def index(
        self,
        child: T,
    ) -> int:

        return self._children.index(child)

    def contains(
        self,
        child: T,
    ) -> bool:

        return child in self._children

    def first(self) -> T | None:

        return self._children[0] if self._children else None

    def last(self) -> T | None:

        return self._children[-1] if self._children else None

    # ==========================================================
    # Collections Python
    # ==========================================================

    def __contains__(
        self,
        child: object,
    ) -> bool:

        return child in self._children

    def __getitem__(
        self,
        index: int,
    ) -> T:

        return self._children[index]

    def __iter__(self) -> Iterator[T]:

        return iter(self._children)

    def __len__(self) -> int:

        return len(self._children)

    # ==========================================================
    # Accès
    # ==========================================================

    @property
    def children(self) -> tuple[T, ...]:

        return tuple(self._children)

    @property
    def is_empty(self) -> bool:

        return not self._children

    @property
    def count(self) -> int:

        return len(self._children)

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(count={self.count})"
        )