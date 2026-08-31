from __future__ import annotations

"""
TomeLinea V4 — noyau du domaine.

Ce module ne dépend d'aucun modèle V3.

Le Livre, ses pages et ses parties possèdent des identités stables
indépendantes de leur nom, position ou représentation dans l'interface.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
from uuid import uuid4


def new_id() -> str:
    """Crée une identité interne stable."""
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

    source_page est basé sur 1.
    Une page générée par TomeLinea peut ne pas avoir de SourceLink.
    """

    source_id: str
    source_version_id: str
    source_page: int | None = None

    def __post_init__(self) -> None:
        if self.source_page is not None and self.source_page < 1:
            raise ValueError(
                "source_page doit être >= 1"
            )


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
            raise ValueError(
                "Le format du livre doit être positif."
            )

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
            raise ValueError(
                "Marges et fonds perdus ne peuvent pas être négatifs."
            )


@dataclass(slots=True)
class PartV4:
    """
    Partie logique du Livre.

    Peut représenter par exemple :
    - début ;
    - liminaires ;
    - partie ;
    - chapitre ;
    - annexe ;
    - fin.

    Son id reste stable même si elle est renommée ou déplacée.
    """

    id: str = field(default_factory=new_id)

    title: str = ""
    part_type: str = "partie"

    # Permet une hiérarchie future :
    # Partie 1 > Chapitre 1, par exemple.
    parent_id: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    history: list[dict[str, Any]] = field(
        default_factory=list
    )


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

    # Référence vers PartV4.id.
    part_id: str | None = None

    model_id: str | None = None

    recto_verso: str | None = None

    spread_id: str | None = None
    spread_side: str | None = None

    auto_before: list[str] = field(
        default_factory=list
    )

    auto_after: list[str] = field(
        default_factory=list
    )

    is_compensation: bool = False

    content: list[dict[str, Any]] = field(
        default_factory=list
    )

    modifications: list[dict[str, Any]] = field(
        default_factory=list
    )

    history: list[dict[str, Any]] = field(
        default_factory=list
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )


@dataclass(slots=True)
class BookV4:
    """
    Autorité unique sur l'état courant du livre.

    Les ordres sont séparés des objets :
    - pages + page_order ;
    - parts + part_order.

    Déplacer un élément ne change donc jamais son identité.
    """

    id: str = field(default_factory=new_id)
    title: str = ""
    kind: BookKind = BookKind.UNKNOWN

    format: BookFormat = field(
        default_factory=BookFormat
    )

    pages: dict[str, PageV4] = field(
        default_factory=dict
    )

    page_order: list[str] = field(
        default_factory=list
    )

    parts: dict[str, PartV4] = field(
        default_factory=dict
    )

    part_order: list[str] = field(
        default_factory=list
    )

    models: dict[str, dict[str, Any]] = field(
        default_factory=dict
    )

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    history: list[dict[str, Any]] = field(
        default_factory=list
    )

    # ==========================================================
    # Pages
    # ==========================================================

    def add_page(
        self,
        page: PageV4,
        *,
        index: int | None = None,
    ) -> None:

        if page.id in self.pages:
            raise ValueError(
                f"Page déjà présente : {page.id}"
            )

        if (
            page.part_id is not None
            and page.part_id not in self.parts
        ):
            raise ValueError(
                f"Partie inconnue pour la page : {page.part_id}"
            )

        self.pages[page.id] = page

        if index is None:
            self.page_order.append(
                page.id
            )
        else:
            self.page_order.insert(
                index,
                page.id,
            )

        self.validate()

    def remove_page(
        self,
        page_id: str,
    ) -> PageV4:

        if page_id not in self.pages:
            raise KeyError(page_id)

        self.page_order.remove(
            page_id
        )

        page = self.pages.pop(
            page_id
        )

        self.validate()

        return page

    def move_page(
        self,
        page_id: str,
        new_index: int,
    ) -> None:

        if page_id not in self.pages:
            raise KeyError(page_id)

        self.page_order.remove(
            page_id
        )

        self.page_order.insert(
            new_index,
            page_id,
        )

        self.validate()

    def ordered_pages(
        self,
    ) -> list[PageV4]:

        return [
            self.pages[page_id]
            for page_id in self.page_order
        ]

    # ==========================================================
    # Parties
    # ==========================================================

    def add_part(
        self,
        part: PartV4,
        *,
        index: int | None = None,
    ) -> None:

        if part.id in self.parts:
            raise ValueError(
                f"Partie déjà présente : {part.id}"
            )

        if (
            part.parent_id is not None
            and part.parent_id not in self.parts
        ):
            raise ValueError(
                f"Partie parente inconnue : {part.parent_id}"
            )

        self.parts[part.id] = part

        if index is None:
            self.part_order.append(
                part.id
            )
        else:
            self.part_order.insert(
                index,
                part.id,
            )

        self.validate()

    def move_part(
        self,
        part_id: str,
        new_index: int,
    ) -> None:

        if part_id not in self.parts:
            raise KeyError(part_id)

        self.part_order.remove(
            part_id
        )

        self.part_order.insert(
            new_index,
            part_id,
        )

        self.validate()

    def remove_part(
        self,
        part_id: str,
    ) -> PartV4:
        """
        Une partie contenant encore des pages ou des sous-parties
        ne peut pas être supprimée silencieusement.
        """

        if part_id not in self.parts:
            raise KeyError(part_id)

        if any(
            page.part_id == part_id
            for page in self.pages.values()
        ):
            raise ValueError(
                "Impossible de supprimer une partie "
                "qui contient encore des pages."
            )

        if any(
            part.parent_id == part_id
            for part in self.parts.values()
        ):
            raise ValueError(
                "Impossible de supprimer une partie "
                "qui possède encore des sous-parties."
            )

        self.part_order.remove(
            part_id
        )

        part = self.parts.pop(
            part_id
        )

        self.validate()

        return part

    def ordered_parts(
        self,
    ) -> list[PartV4]:

        return [
            self.parts[part_id]
            for part_id in self.part_order
        ]

    # ==========================================================
    # Validation globale
    # ==========================================================

    def validate(self) -> None:
        self.format.validate()

        if (
            len(self.page_order)
            != len(set(self.page_order))
        ):
            raise ValueError(
                "Une page apparaît plusieurs fois "
                "dans l'ordre du livre."
            )

        known_pages = set(
            self.pages
        )

        ordered_pages = set(
            self.page_order
        )

        missing_pages = (
            known_pages - ordered_pages
        )

        unknown_pages = (
            ordered_pages - known_pages
        )

        if missing_pages:
            raise ValueError(
                "Pages présentes mais absentes de l'ordre : "
                f"{sorted(missing_pages)}"
            )

        if unknown_pages:
            raise ValueError(
                "Identifiants de pages inconnus dans l'ordre : "
                f"{sorted(unknown_pages)}"
            )

        if (
            len(self.part_order)
            != len(set(self.part_order))
        ):
            raise ValueError(
                "Une partie apparaît plusieurs fois "
                "dans l'ordre du livre."
            )

        known_parts = set(
            self.parts
        )

        ordered_parts = set(
            self.part_order
        )

        missing_parts = (
            known_parts - ordered_parts
        )

        unknown_parts = (
            ordered_parts - known_parts
        )

        if missing_parts:
            raise ValueError(
                "Parties présentes mais absentes de l'ordre : "
                f"{sorted(missing_parts)}"
            )

        if unknown_parts:
            raise ValueError(
                "Identifiants de parties inconnus dans l'ordre : "
                f"{sorted(unknown_parts)}"
            )

        for part in self.parts.values():
            if (
                part.parent_id is not None
                and part.parent_id not in self.parts
            ):
                raise ValueError(
                    f"Partie parente inconnue : {part.parent_id}"
                )

            if part.parent_id == part.id:
                raise ValueError(
                    "Une partie ne peut pas être sa propre parente."
                )

        for page in self.pages.values():
            if (
                page.part_id is not None
                and page.part_id not in self.parts
            ):
                raise ValueError(
                    f"Page {page.id} rattachée "
                    f"à une partie inconnue : {page.part_id}"
                )
