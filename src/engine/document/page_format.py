from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PageFormat:
    """
    Représente un format de page.

    Les dimensions sont exprimées en millimètres.
    """

    name: str
    width: float
    height: float


# ----------------------------------------------------------------------
# Formats standards
# ----------------------------------------------------------------------

A5 = PageFormat(
    name="A5",
    width=148,
    height=210,
)

A4 = PageFormat(
    name="A4",
    width=210,
    height=297,
)

A3 = PageFormat(
    name="A3",
    width=297,
    height=420,
)

LETTER = PageFormat(
    name="Letter",
    width=215.9,
    height=279.4,
)