from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PageFormat:
    """
    Décrit un format de page en millimètres.
    """

    name: str
    width_mm: float
    height_mm: float

    @property
    def portrait(self) -> bool:

        return self.width_mm <= self.height_mm

    @property
    def landscape(self) -> bool:

        return self.width_mm > self.height_mm

    @property
    def size(self) -> tuple[float, float]:

        return (
            self.width_mm,
            self.height_mm,
        )

    def __repr__(self) -> str:

        return (
            f"PageFormat("
            f"name={self.name!r}, "
            f"width_mm={self.width_mm}, "
            f"height_mm={self.height_mm})"
        )


# ==========================================================
# Formats standards
# ==========================================================

A5 = PageFormat(
    name="A5",
    width_mm=148.0,
    height_mm=210.0,
)

A4 = PageFormat(
    name="A4",
    width_mm=210.0,
    height_mm=297.0,
)

BOOK_16X24 = PageFormat(
    name="16x24",
    width_mm=160.0,
    height_mm=240.0,
)

BOOK_17X24 = PageFormat(
    name="17x24",
    width_mm=170.0,
    height_mm=240.0,
)

__all__ = [
    "PageFormat",
    "A5",
    "A4",
    "BOOK_16X24",
    "BOOK_17X24",
]