from __future__ import annotations

"""
TomeLinea V4 — noyau du domaine.

Ce module ne dépend d'aucun modèle V3.
Il définit l'identité stable d'une page et l'état réel du livre.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


def new_id() -> str:
    """Crée une identité interne stable et indépendante de l'affichage."""
    return str(uuid4())


class BookKind(str, Enum):
    UNKNOWN = "indetermine"
    ROMAN = "roman"
    COMIC = "bande_dessinee"
    SHEETS = "livre_de_fiches"


class PageOrigin(str, Enum):
    AUTHOR = "auteur"
    TOMELINEA = "tomelinea"


@dataclass(frozen=True, slots=True)
class SourceLink:
    """
    Liaison stable vers une source auteur.

    Le numéro de page source est basé sur 1.
    Une page générée par TomeLinea peut ne pas avoir de SourceLink.
    """

    source_id: str
    source_version_id: str
    source_page: int | None = None

    def __post_init__(self) -> None:
        if self.source_page is not None and self.source_page < 1:
            raise ValueError("source_page doit être >= 1")


@dataclass(slots=True)
class BookFormat:
    width_mm: float = 148.0
    height_mm: float = 210.0

    margin_top_mm: float = 15.0
    margin_bottom_mm: float = 15.0
    margin_inside_mm: float = 15.0
    margin_outside_mm: float = 15.0

    bleed_top_mm: float = 0.0
    bleed_right_mm: float = 0.0
    bleed_bottom_mm: float = 0.0
    bleed_left_mm: float = 0.0

    def validate(self) -> None:
        if self.width_mm <= 0 or self.height_mm <= 0:
            raise ValueError("Le format du livre doit être positif.")

        values = (
            self.margin_top_mm,
            self.margin_bottom_mm,
            self.margin_inside_mm,
            self.margin_outside_mm,
            self.bleed_top_mm,
            self.bleed_right_mm,
            self.bleed_bottom_mm,
            self.bleed_left_mm,
        )
        if any(value < 0 for value in values):
            raise ValueError("Marges et fonds perdus ne peuvent pas être négatifs.")


@dataclass(slots=True)
class PageV4:
    """
    Une page logique TomeLinea.

    Son id ne change jamais lorsque la page est renommée, déplacée,
    reclassée ou change de type.
    """

    id: str = field(default_factory=new_id)

    page_type: str = "Page"
    title: str = ""
    origin: PageOrigin = PageOrigin.AUTHOR

    source: SourceLink | None = None

    part_id: str | None = None
    model_id: str | None = None

    recto_verso: str | None = None

    spread_id: str | None = None
    spread_side: str | None = None

    auto_before: list[str] = field(default_factory=list)
    auto_after: list[str] = field(default_factory=list)

    is_compensation: bool = False

    content: list[dict[str, Any]] = field(default_factory=list)
    modifications: list[dict[str, Any]] = field(default_factory=list)
    history: list[dict[str, Any]] = field(default_factory=list)

    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class BookV4:
    """
    Autorité unique sur l'état courant du livre.

    `pages` contient les objets.
    `page_order` contient uniquement leurs identifiants et définit
    l'ordre réel du livre.
    """

    id: str = field(default_factory=new_id)
    title: str = ""
    kind: BookKind = BookKind.UNKNOWN

    format: BookFormat = field(default_factory=BookFormat)

    pages: dict[str, PageV4] = field(default_factory=dict)
    page_order: list[str] = field(default_factory=list)

    parts: list[dict[str, Any]] = field(default_factory=list)
    models: dict[str, dict[str, Any]] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, Any]] = field(default_factory=list)

    def add_page(
        self,
        page: PageV4,
        *,
        index: int | None = None,
    ) -> None:
        if page.id in self.pages:
            raise ValueError(f"Page déjà présente : {page.id}")

        self.pages[page.id] = page

        if index is None:
            self.page_order.append(page.id)
        else:
            self.page_order.insert(index, page.id)

        self.validate()

    def remove_page(self, page_id: str) -> PageV4:
        if page_id not in self.pages:
            raise KeyError(page_id)

        self.page_order.remove(page_id)
        page = self.pages.pop(page_id)

        self.validate()
        return page

    def move_page(self, page_id: str, new_index: int) -> None:
        if page_id not in self.pages:
            raise KeyError(page_id)

        self.page_order.remove(page_id)
        self.page_order.insert(new_index, page_id)

        self.validate()

    def ordered_pages(self) -> list[PageV4]:
        return [self.pages[page_id] for page_id in self.page_order]

    def validate(self) -> None:
        self.format.validate()

        if len(self.page_order) != len(set(self.page_order)):
            raise ValueError("Une page apparaît plusieurs fois dans l'ordre du livre.")

        known = set(self.pages)
        ordered = set(self.page_order)

        missing = known - ordered
        unknown = ordered - known

        if missing:
            raise ValueError(
                f"Pages présentes mais absentes de l'ordre : {sorted(missing)}"
            )

        if unknown:
            raise ValueError(
                f"Identifiants inconnus dans l'ordre : {sorted(unknown)}"
            )
