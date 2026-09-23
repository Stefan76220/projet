"""API Livre commune de TomeLinea V5.

V5-02 conserve exactement le moteur de domaine V4 valide.
Les noms publics V5 sont volontairement neutres et ne portent plus
le suffixe historique V4.
"""

from src.v4.domain import (
    BookFormat,
    BookKind,
    BookV4 as Book,
    PageOrigin,
    PageV4 as Page,
    PartV4 as Part,
    SourceLink,
)

__all__ = [
    "Book",
    "Page",
    "Part",
    "BookFormat",
    "BookKind",
    "PageOrigin",
    "SourceLink",
]