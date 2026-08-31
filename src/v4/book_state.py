from __future__ import annotations

"""
TomeLinea V4 — contrat de lecture de l'état réel du Livre.

Ce module ne modifie jamais BookV4.

Il produit une photographie :
- complète pour la structure et la composition ;
- détachée des objets mutables du Livre ;
- récursivement non modifiable ;
- stable et versionnée ;
- munie d'une empreinte permettant à un consommateur
  (notamment le Visionneur) de savoir si l'état réel a changé.

Le Visionneur ne devient jamais propriétaire de cet état.
Il ne fait que le lire.

Les historiques d'audit ne font volontairement pas partie du contrat
de rendu : ils restent dans BookV4 et dans la persistance du Projet,
mais une simple écriture d'historique ne doit pas provoquer à elle
seule une reconstruction visuelle du livre.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from hashlib import sha256
import json
from types import MappingProxyType
from typing import Any

from src.v4.domain import (
    BookV4,
    PageV4,
    PartV4,
    SourceLink,
)


BOOK_STATE_CONTRACT = "tomelinea-book-state"
BOOK_STATE_VERSION = 1


# ==============================================================
# États publics immuables
# ==============================================================

@dataclass(frozen=True, slots=True)
class BookFormatState:
    width_mm: float
    height_mm: float

    margin_top_mm: float
    margin_bottom_mm: float
    margin_inside_mm: float
    margin_outside_mm: float

    bleed_top_mm: float
    bleed_right_mm: float
    bleed_bottom_mm: float
    bleed_left_mm: float


@dataclass(frozen=True, slots=True)
class SourceLinkState:
    source_id: str
    source_version_id: str
    source_page: int | None


@dataclass(frozen=True, slots=True)
class PartState:
    id: str
    title: str
    part_type: str
    parent_id: str | None

    metadata: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class PageState:
    id: str

    page_type: str
    title: str
    origin: str

    source: SourceLinkState | None

    part_id: str | None
    model_id: str | None

    recto_verso: str | None

    spread_id: str | None
    spread_side: str | None

    auto_before: tuple[str, ...]
    auto_after: tuple[str, ...]

    is_compensation: bool

    content: tuple[Any, ...]
    modifications: tuple[Any, ...]

    metadata: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class BookState:
    """
    Contrat public de lecture du Livre réel.
    """

    contract: str
    contract_version: int

    book_id: str
    title: str
    kind: str

    format: BookFormatState

    part_order: tuple[str, ...]
    parts: Mapping[str, PartState]

    page_order: tuple[str, ...]
    pages: Mapping[str, PageState]

    models: Mapping[str, Any]
    metadata: Mapping[str, Any]

    fingerprint: str

    def ordered_parts(
        self,
    ) -> tuple[PartState, ...]:

        return tuple(
            self.parts[part_id]
            for part_id in self.part_order
        )

    def ordered_pages(
        self,
    ) -> tuple[PageState, ...]:

        return tuple(
            self.pages[page_id]
            for page_id in self.page_order
        )

    def part(
        self,
        part_id: str,
    ) -> PartState:

        return self.parts[
            part_id
        ]

    def page(
        self,
        page_id: str,
    ) -> PageState:

        return self.pages[
            page_id
        ]


# ==============================================================
# Copie JSON détachée et gel récursif
# ==============================================================

def _json_clone(
    value: Any,
) -> Any:
    """
    Produit une copie profonde ne partageant aucun conteneur
    avec le Livre.

    Le contrat V4 persistant étant JSON, une valeur non compatible
    est considérée comme une incohérence du modèle.
    """

    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            "L'état du Livre contient une valeur "
            "non compatible avec le contrat JSON V4."
        ) from exc

    return json.loads(
        encoded
    )


def _freeze(
    value: Any,
) -> Any:
    """
    Rend récursivement les structures non modifiables.
    """

    if isinstance(
        value,
        dict,
    ):
        return MappingProxyType(
            {
                str(key): _freeze(item)
                for key, item
                in value.items()
            }
        )

    if isinstance(
        value,
        list,
    ):
        return tuple(
            _freeze(item)
            for item in value
        )

    return value


def _frozen_json(
    value: Any,
) -> Any:

    return _freeze(
        _json_clone(
            value
        )
    )


# ==============================================================
# Conversion des éléments
# ==============================================================

def _source_payload(
    source: SourceLink | None,
) -> dict[str, Any] | None:

    if source is None:
        return None

    return {
        "source_id": source.source_id,
        "source_version_id": (
            source.source_version_id
        ),
        "source_page": source.source_page,
    }


def _source_state(
    source: SourceLink | None,
) -> SourceLinkState | None:

    if source is None:
        return None

    return SourceLinkState(
        source_id=source.source_id,
        source_version_id=(
            source.source_version_id
        ),
        source_page=source.source_page,
    )


def _part_payload(
    part: PartV4,
) -> dict[str, Any]:

    return {
        "id": part.id,
        "title": part.title,
        "part_type": part.part_type,
        "parent_id": part.parent_id,
        "metadata": part.metadata,
    }


def _part_state(
    part: PartV4,
) -> PartState:

    return PartState(
        id=part.id,
        title=part.title,
        part_type=part.part_type,
        parent_id=part.parent_id,
        metadata=_frozen_json(
            part.metadata
        ),
    )


def _page_payload(
    page: PageV4,
) -> dict[str, Any]:

    return {
        "id": page.id,
        "page_type": page.page_type,
        "title": page.title,
        "origin": page.origin.value,

        "source": _source_payload(
            page.source
        ),

        "part_id": page.part_id,
        "model_id": page.model_id,

        "recto_verso": (
            page.recto_verso
        ),

        "spread_id": page.spread_id,
        "spread_side": (
            page.spread_side
        ),

        "auto_before": list(
            page.auto_before
        ),

        "auto_after": list(
            page.auto_after
        ),

        "is_compensation": (
            page.is_compensation
        ),

        "content": page.content,

        "modifications": (
            page.modifications
        ),

        "metadata": page.metadata,
    }


def _page_state(
    page: PageV4,
) -> PageState:

    frozen_content = (
        _frozen_json(
            page.content
        )
    )

    frozen_modifications = (
        _frozen_json(
            page.modifications
        )
    )

    return PageState(
        id=page.id,

        page_type=page.page_type,
        title=page.title,
        origin=page.origin.value,

        source=_source_state(
            page.source
        ),

        part_id=page.part_id,
        model_id=page.model_id,

        recto_verso=(
            page.recto_verso
        ),

        spread_id=page.spread_id,
        spread_side=(
            page.spread_side
        ),

        auto_before=tuple(
            page.auto_before
        ),

        auto_after=tuple(
            page.auto_after
        ),

        is_compensation=(
            page.is_compensation
        ),

        content=frozen_content,

        modifications=(
            frozen_modifications
        ),

        metadata=_frozen_json(
            page.metadata
        ),
    )


# ==============================================================
# Empreinte de l'état réel
# ==============================================================

def _book_payload(
    book: BookV4,
) -> dict[str, Any]:

    return {
        "contract": BOOK_STATE_CONTRACT,
        "contract_version": (
            BOOK_STATE_VERSION
        ),

        "book_id": book.id,
        "title": book.title,
        "kind": book.kind.value,

        "format": {
            "width_mm": (
                float(book.format.width_mm)
            ),
            "height_mm": (
                float(book.format.height_mm)
            ),

            "margin_top_mm": (
                float(book.format.margin_top_mm)
            ),
            "margin_bottom_mm": (
                float(book.format.margin_bottom_mm)
            ),
            "margin_inside_mm": (
                float(book.format.margin_inside_mm)
            ),
            "margin_outside_mm": (
                float(book.format.margin_outside_mm)
            ),

            "bleed_top_mm": (
                float(book.format.bleed_top_mm)
            ),
            "bleed_right_mm": (
                float(book.format.bleed_right_mm)
            ),
            "bleed_bottom_mm": (
                float(book.format.bleed_bottom_mm)
            ),
            "bleed_left_mm": (
                float(book.format.bleed_left_mm)
            ),
        },

        "part_order": list(
            book.part_order
        ),

        "parts": [
            _part_payload(
                book.parts[part_id]
            )
            for part_id in book.part_order
        ],

        "page_order": list(
            book.page_order
        ),

        "pages": [
            _page_payload(
                book.pages[page_id]
            )
            for page_id in book.page_order
        ],

        "models": book.models,
        "metadata": book.metadata,
    }


def _fingerprint(
    payload: dict[str, Any],
) -> str:

    # Validation + détachement JSON.
    clean = _json_clone(
        payload
    )

    canonical = json.dumps(
        clean,
        ensure_ascii=False,
        sort_keys=True,
        separators=(
            ",",
            ":",
        ),
    )

    return sha256(
        canonical.encode(
            "utf-8"
        )
    ).hexdigest()


# ==============================================================
# Contrat public
# ==============================================================

def build_book_state(
    book: BookV4,
) -> BookState:
    """
    Construit une photographie immuable de l'état courant.

    Modifier BookV4 après cet appel ne modifie jamais l'ancien
    BookState. Un nouvel appel produit une nouvelle photographie
    et, si l'état a réellement changé, une nouvelle empreinte.
    """

    book.validate()

    payload = _book_payload(
        book
    )

    fingerprint = _fingerprint(
        payload
    )

    parts = MappingProxyType(
        {
            part_id: _part_state(
                book.parts[
                    part_id
                ]
            )
            for part_id
            in book.part_order
        }
    )

    pages = MappingProxyType(
        {
            page_id: _page_state(
                book.pages[
                    page_id
                ]
            )
            for page_id
            in book.page_order
        }
    )

    state = BookState(
        contract=BOOK_STATE_CONTRACT,
        contract_version=(
            BOOK_STATE_VERSION
        ),

        book_id=book.id,
        title=book.title,
        kind=book.kind.value,

        format=BookFormatState(
            width_mm=(
                book.format.width_mm
            ),
            height_mm=(
                book.format.height_mm
            ),

            margin_top_mm=(
                book.format.margin_top_mm
            ),
            margin_bottom_mm=(
                book.format.margin_bottom_mm
            ),
            margin_inside_mm=(
                book.format.margin_inside_mm
            ),
            margin_outside_mm=(
                book.format.margin_outside_mm
            ),

            bleed_top_mm=(
                book.format.bleed_top_mm
            ),
            bleed_right_mm=(
                book.format.bleed_right_mm
            ),
            bleed_bottom_mm=(
                book.format.bleed_bottom_mm
            ),
            bleed_left_mm=(
                book.format.bleed_left_mm
            ),
        ),

        part_order=tuple(
            book.part_order
        ),
        parts=parts,

        page_order=tuple(
            book.page_order
        ),
        pages=pages,

        models=_frozen_json(
            book.models
        ),

        metadata=_frozen_json(
            book.metadata
        ),

        fingerprint=fingerprint,
    )

    return state
