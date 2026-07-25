from dataclasses import dataclass


@dataclass(frozen=True)
class PageFormat:
    """
    Décrit un format de page en millimètres.
    """

    name: str
    width_mm: float
    height_mm: float

    @property
    def portrait(self):
        return self.width_mm <= self.height_mm

    @property
    def landscape(self):
        return self.width_mm > self.height_mm


# ------------------------------------------------------------------
# Formats standards
# ------------------------------------------------------------------

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