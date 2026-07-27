from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Size:
    width: float
    height: float

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def is_empty(self) -> bool:
        return self.width <= 0 or self.height <= 0

    @property
    def area(self) -> float:
        return self.width * self.height

    # ==========================================================
    # Géométrie
    # ==========================================================

    def scale(
        self,
        factor: float,
    ) -> "Size":

        return Size(
            self.width * factor,
            self.height * factor,
        )

    # ==========================================================
    # Opérateurs
    # ==========================================================

    def __iter__(self):

        yield self.width
        yield self.height