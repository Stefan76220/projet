from __future__ import annotations

"""
TomeLinea V4 — noyau Composition.

Le Livre reste l'unique autorité.

Les éléments de Composition sont stockés dans PageV4.content
sous une forme JSON explicite et versionnée.

Principes :
- chaque élément possède un UUID stable ;
- coordonnées et dimensions sont exprimées en millimètres ;
- l'origine (0, 0) est le coin supérieur gauche du format fini ;
- Marges / Page / Fond perdu sont des référentiels de travail,
  jamais des barrières dures ;
- un élément peut donc dépasser volontairement ces limites ;
- l'ordre dans PageV4.content constitue l'ordre de superposition ;
- un élément placé peut conserver une trace précise vers sa Source.
"""

from copy import deepcopy
from datetime import datetime, timezone
import json
from math import isfinite
from typing import Any
from uuid import uuid4

from src.v4.domain import (
    BookV4,
    PageV4,
)
from src.v4.structure_parity import (
    physical_side,
)


COMPOSITION_SCHEMA = (
    "tomelinea-composition-element"
)
COMPOSITION_VERSION = 1

TEXT = "text"
IMAGE = "image"
DOCUMENT = "document"

ELEMENT_KINDS = {
    TEXT,
    IMAGE,
    DOCUMENT,
}

MARGINS = "margins"
PAGE = "page"
BLEED = "bleed"

REFERENCE_FRAMES = {
    MARGINS,
    PAGE,
    BLEED,
}


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def new_id() -> str:
    return str(
        uuid4()
    )


def _page(
    book: BookV4,
    page_id: str,
) -> PageV4:

    page = book.pages.get(
        page_id
    )

    if page is None:
        raise KeyError(
            page_id
        )

    return page


def _json_compatible(
    value: Any,
) -> None:

    try:
        json.dumps(
            value,
            ensure_ascii=False,
        )

    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            "Valeur Composition non compatible JSON."
        ) from exc


def _number(
    value: Any,
    name: str,
) -> float:

    try:
        result = float(
            value
        )
    except (
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            f"Valeur géométrique invalide : {name}"
        ) from exc

    if not isfinite(
        result
    ):
        raise ValueError(
            f"Valeur géométrique non finie : {name}"
        )

    return result


def normalize_kind(
    value: str,
) -> str:

    result = str(
        value or ""
    ).strip().lower()

    if result not in ELEMENT_KINDS:
        raise ValueError(
            "Type d'élément Composition inconnu : "
            f"{value}"
        )

    return result


def normalize_reference_frame(
    value: str,
) -> str:

    result = str(
        value or ""
    ).strip().lower()

    if result not in REFERENCE_FRAMES:
        raise ValueError(
            "Référentiel Composition inconnu : "
            f"{value}"
        )

    return result


def frame_bounds(
    book: BookV4,
    page_id: str,
    reference_frame: str,
) -> tuple[
    float,
    float,
    float,
    float,
]:
    """
    Retourne x, y, largeur, hauteur du référentiel en mm.

    Pour les marges, intérieur/extérieur sont résolus selon
    le côté physique de la page.
    """

    book.validate()

    _page(
        book,
        page_id,
    )

    frame = normalize_reference_frame(
        reference_frame
    )

    fmt = book.format

    if frame == PAGE:
        return (
            0.0,
            0.0,
            float(fmt.width_mm),
            float(fmt.height_mm),
        )

    if frame == BLEED:
        return (
            -float(
                fmt.bleed_left_mm
            ),
            -float(
                fmt.bleed_top_mm
            ),
            float(
                fmt.width_mm
                + fmt.bleed_left_mm
                + fmt.bleed_right_mm
            ),
            float(
                fmt.height_mm
                + fmt.bleed_top_mm
                + fmt.bleed_bottom_mm
            ),
        )

    side = physical_side(
        book,
        page_id,
    )

    if side == "recto":
        left_margin = float(
            fmt.margin_inside_mm
        )
        right_margin = float(
            fmt.margin_outside_mm
        )
    else:
        left_margin = float(
            fmt.margin_outside_mm
        )
        right_margin = float(
            fmt.margin_inside_mm
        )

    top = float(
        fmt.margin_top_mm
    )
    bottom = float(
        fmt.margin_bottom_mm
    )

    width = (
        float(fmt.width_mm)
        - left_margin
        - right_margin
    )

    height = (
        float(fmt.height_mm)
        - top
        - bottom
    )

    if (
        width <= 0
        or height <= 0
    ):
        raise ValueError(
            "Les marges ne laissent aucune zone "
            "de composition utilisable."
        )

    return (
        left_margin,
        top,
        width,
        height,
    )


def source_reference(
    *,
    source_element_id: str,
    source_version_id: str,
    source_page: int | None = None,
) -> dict[str, Any]:

    element_id = str(
        source_element_id or ""
    ).strip()

    version_id = str(
        source_version_id or ""
    ).strip()

    if not element_id:
        raise ValueError(
            "source_element_id absent."
        )

    if not version_id:
        raise ValueError(
            "source_version_id absent."
        )

    if (
        source_page is not None
        and int(source_page) < 1
    ):
        raise ValueError(
            "source_page doit être >= 1."
        )

    return {
        "source_element_id": (
            element_id
        ),
        "source_version_id": (
            version_id
        ),
        "source_page": (
            int(source_page)
            if source_page is not None
            else None
        ),
    }


def new_element(
    *,
    kind: str,
    x_mm: float,
    y_mm: float,
    width_mm: float,
    height_mm: float,
    rotation_deg: float = 0.0,
    reference_frame: str = MARGINS,
    source_ref: dict[str, Any] | None = None,
    payload: dict[str, Any] | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:

    element = {
        "schema": (
            COMPOSITION_SCHEMA
        ),
        "version": (
            COMPOSITION_VERSION
        ),
        "id": new_id(),
        "kind": normalize_kind(
            kind
        ),
        "geometry": {
            "x_mm": _number(
                x_mm,
                "x_mm",
            ),
            "y_mm": _number(
                y_mm,
                "y_mm",
            ),
            "width_mm": _number(
                width_mm,
                "width_mm",
            ),
            "height_mm": _number(
                height_mm,
                "height_mm",
            ),
            "rotation_deg": _number(
                rotation_deg,
                "rotation_deg",
            ),
        },
        "reference_frame": (
            normalize_reference_frame(
                reference_frame
            )
        ),
        "source_ref": (
            deepcopy(
                source_ref
            )
            if source_ref is not None
            else None
        ),
        "payload": deepcopy(
            payload or {}
        ),
        "metadata": deepcopy(
            metadata or {}
        ),
    }

    validate_element(
        element
    )

    return element


def validate_element(
    element: dict[str, Any],
) -> None:

    if not isinstance(
        element,
        dict,
    ):
        raise ValueError(
            "Élément Composition invalide."
        )

    if element.get(
        "schema"
    ) != COMPOSITION_SCHEMA:
        raise ValueError(
            "Schéma Composition inconnu."
        )

    if element.get(
        "version"
    ) != COMPOSITION_VERSION:
        raise ValueError(
            "Version Composition inconnue."
        )

    if not str(
        element.get(
            "id"
        )
        or ""
    ).strip():
        raise ValueError(
            "UUID Composition absent."
        )

    normalize_kind(
        element.get(
            "kind",
            "",
        )
    )

    normalize_reference_frame(
        element.get(
            "reference_frame",
            "",
        )
    )

    geometry = element.get(
        "geometry"
    )

    if not isinstance(
        geometry,
        dict,
    ):
        raise ValueError(
            "Géométrie Composition absente."
        )

    width = _number(
        geometry.get(
            "width_mm"
        ),
        "width_mm",
    )

    height = _number(
        geometry.get(
            "height_mm"
        ),
        "height_mm",
    )

    _number(
        geometry.get(
            "x_mm"
        ),
        "x_mm",
    )

    _number(
        geometry.get(
            "y_mm"
        ),
        "y_mm",
    )

    _number(
        geometry.get(
            "rotation_deg",
            0.0,
        ),
        "rotation_deg",
    )

    if (
        width <= 0
        or height <= 0
    ):
        raise ValueError(
            "Largeur et hauteur doivent être positives."
        )

    source_ref = element.get(
        "source_ref"
    )

    if source_ref is not None:
        if not isinstance(
            source_ref,
            dict,
        ):
            raise ValueError(
                "Référence Source Composition invalide."
            )

        source_reference(
            source_element_id=(
                source_ref.get(
                    "source_element_id",
                    ""
                )
            ),
            source_version_id=(
                source_ref.get(
                    "source_version_id",
                    ""
                )
            ),
            source_page=(
                source_ref.get(
                    "source_page"
                )
            ),
        )

    payload = element.get(
        "payload",
        {},
    )

    metadata = element.get(
        "metadata",
        {},
    )

    if not isinstance(
        payload,
        dict,
    ):
        raise ValueError(
            "Payload Composition invalide."
        )

    if not isinstance(
        metadata,
        dict,
    ):
        raise ValueError(
            "Métadonnées Composition invalides."
        )

    _json_compatible(
        element
    )


def element_by_id(
    page: PageV4,
    element_id: str,
) -> dict[str, Any]:

    for element in page.content:
        if (
            isinstance(
                element,
                dict,
            )
            and element.get(
                "schema"
            ) == COMPOSITION_SCHEMA
            and str(
                element.get(
                    "id"
                )
            ) == element_id
        ):
            return element

    raise KeyError(
        element_id
    )


def add_element(
    book: BookV4,
    page_id: str,
    **kwargs: Any,
) -> dict[str, Any]:

    book.validate()

    page = _page(
        book,
        page_id,
    )

    element = new_element(
        **kwargs
    )

    page.content.append(
        element
    )

    date = utc_now()

    page.modifications.append(
        {
            "action": (
                "composition_element_added"
            ),
            "element_id": (
                element["id"]
            ),
            "date": date,
        }
    )

    book.history.append(
        {
            "action": (
                "composition_element_added"
            ),
            "page_id": page.id,
            "element_id": (
                element["id"]
            ),
            "date": date,
        }
    )

    return element


def update_element_geometry(
    book: BookV4,
    page_id: str,
    element_id: str,
    *,
    x_mm: float | None = None,
    y_mm: float | None = None,
    width_mm: float | None = None,
    height_mm: float | None = None,
    rotation_deg: float | None = None,
) -> dict[str, Any]:

    book.validate()

    page = _page(
        book,
        page_id,
    )

    element = element_by_id(
        page,
        element_id,
    )

    candidate = deepcopy(
        element
    )

    geometry = candidate[
        "geometry"
    ]

    values = {
        "x_mm": x_mm,
        "y_mm": y_mm,
        "width_mm": width_mm,
        "height_mm": height_mm,
        "rotation_deg": rotation_deg,
    }

    for key, value in values.items():
        if value is not None:
            geometry[
                key
            ] = _number(
                value,
                key,
            )

    validate_element(
        candidate
    )

    element[
        "geometry"
    ] = geometry

    date = utc_now()

    page.modifications.append(
        {
            "action": (
                "composition_geometry_changed"
            ),
            "element_id": (
                element_id
            ),
            "date": date,
        }
    )

    book.history.append(
        {
            "action": (
                "composition_geometry_changed"
            ),
            "page_id": page.id,
            "element_id": (
                element_id
            ),
            "date": date,
        }
    )

    return element


def remove_element(
    book: BookV4,
    page_id: str,
    element_id: str,
) -> dict[str, Any]:

    book.validate()

    page = _page(
        book,
        page_id,
    )

    for index, element in enumerate(
        page.content
    ):
        if (
            isinstance(
                element,
                dict,
            )
            and element.get(
                "schema"
            ) == COMPOSITION_SCHEMA
            and str(
                element.get(
                    "id"
                )
            ) == element_id
        ):
            removed = page.content.pop(
                index
            )

            date = utc_now()

            page.modifications.append(
                {
                    "action": (
                        "composition_element_removed"
                    ),
                    "element_id": (
                        element_id
                    ),
                    "date": date,
                }
            )

            book.history.append(
                {
                    "action": (
                        "composition_element_removed"
                    ),
                    "page_id": page.id,
                    "element_id": (
                        element_id
                    ),
                    "date": date,
                }
            )

            return removed

    raise KeyError(
        element_id
    )


def composition_issues(
    book: BookV4,
) -> list[str]:

    issues: list[str] = []

    for page_id in book.page_order:
        page = book.pages[
            page_id
        ]

        ids: list[str] = []

        for index, element in enumerate(
            page.content
        ):
            try:
                validate_element(
                    element
                )

                ids.append(
                    str(
                        element[
                            "id"
                        ]
                    )
                )

            except Exception as exc:
                issues.append(
                    f"{page_id}/élément {index} : {exc}"
                )

        if len(ids) != len(
            set(ids)
        ):
            issues.append(
                f"{page_id} : UUID Composition dupliqué"
            )

    return issues
