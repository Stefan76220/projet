from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Size:
    width: float
    height: float

    @property
    def is_empty(self) -> bool:
        return self.width <= 0 or self.height <= 0

    def scale(self, factor: float) -> "Size":
        return Size(
            self.width * factor,
            self.height * factor,
        )