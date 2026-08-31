from __future__ import annotations

"""
TomeLinea V4 — organisation des éléments de Composition.

La sélection visuelle n'est PAS persistée dans le Livre.
Les fonctions reçoivent simplement les UUID actuellement sélectionnés.

Fonctions :
- alignement ;
- distribution ;
- égalisation ;
- ordre de superposition ;
- association / dissociation.

L'ordre de PageV4.content représente l'ordre des calques :
premier = arrière, dernier = avant.
"""

from copy import deepcopy
from dataclasses import fields
from datetime import datetime, timezone
from typing import Iterable
from uuid import uuid4

from src.v4.domain import (
    BookV4,
    PageV4,
)

from src.v4.composition import (
    COMPOSITION_SCHEMA,
    element_by_id,
    update_element_geometry,
)


GROUP_KEY = "composition_group_id"


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _restore_book(
    book: BookV4,
    snapshot: BookV4,
) -> None:

    for field_info in fields(
        BookV4
    ):
        setattr(
            book,
            field_info.name,
            deepcopy(
                getattr(
                    snapshot,
                    field_info.name,
                )
            ),
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


def _composition_ids(
    page: PageV4,
) -> list[str]:

    return [
        str(element["id"])
        for element in page.content
        if (
            isinstance(
                element,
                dict,
            )
            and element.get(
                "schema"
            ) == COMPOSITION_SCHEMA
            and element.get(
                "id"
            )
        )
    ]


def normalize_selection(
    book: BookV4,
    page_id: str,
    element_ids: Iterable[str],
    *,
    include_associated: bool = True,
) -> list[str]:
    """
    Normalise une sélection temporaire.

    - élimine les doublons ;
    - vérifie que les éléments existent ;
    - peut étendre la sélection aux membres associés ;
    - respecte l'ordre de superposition de la page.
    """

    page = _page(
        book,
        page_id,
    )

    requested = {
        str(value)
        for value in element_ids
    }

    for element_id in requested:
        element_by_id(
            page,
            element_id,
        )

    if include_associated:
        group_ids: set[str] = set()

        for element_id in requested:
            element = element_by_id(
                page,
                element_id,
            )

            metadata = element.get(
                "metadata",
                {},
            )

            group_id = metadata.get(
                GROUP_KEY
            )

            if group_id:
                group_ids.add(
                    str(group_id)
                )

        if group_ids:
            for element in page.content:
                if not isinstance(
                    element,
                    dict,
                ):
                    continue

                if element.get(
                    "schema"
                ) != COMPOSITION_SCHEMA:
                    continue

                metadata = element.get(
                    "metadata",
                    {},
                )

                if str(
                    metadata.get(
                        GROUP_KEY,
                        "",
                    )
                ) in group_ids:
                    requested.add(
                        str(
                            element["id"]
                        )
                    )

    return [
        element_id
        for element_id in _composition_ids(
            page
        )
        if element_id in requested
    ]


def _selection(
    book: BookV4,
    page_id: str,
    element_ids: Iterable[str],
    *,
    minimum: int,
    include_associated: bool = True,
) -> tuple[
    PageV4,
    list[str],
    list[dict],
]:

    page = _page(
        book,
        page_id,
    )

    ids = normalize_selection(
        book,
        page_id,
        element_ids,
        include_associated=(
            include_associated
        ),
    )

    if len(ids) < minimum:
        raise ValueError(
            "Sélection insuffisante : "
            f"{minimum} élément(s) minimum."
        )

    elements = [
        element_by_id(
            page,
            element_id,
        )
        for element_id in ids
    ]

    return (
        page,
        ids,
        elements,
    )


def _geometry(
    element: dict,
) -> tuple[
    float,
    float,
    float,
    float,
]:

    g = element[
        "geometry"
    ]

    return (
        float(g["x_mm"]),
        float(g["y_mm"]),
        float(g["width_mm"]),
        float(g["height_mm"]),
    )


def _record(
    book: BookV4,
    page: PageV4,
    action: str,
    element_ids: list[str],
    **extra,
) -> None:

    book.history.append(
        {
            "action": action,
            "page_id": page.id,
            "element_ids": list(
                element_ids
            ),
            "date": utc_now(),
            **extra,
        }
    )


# =============================================================
# ALIGNEMENT
# =============================================================

def align_elements(
    book: BookV4,
    page_id: str,
    element_ids: Iterable[str],
    *,
    mode: str,
) -> list[str]:
    """
    Modes :
    left, hcenter, right,
    top, vcenter, bottom
    """

    book.validate()

    mode = str(
        mode
    ).strip().lower()

    allowed = {
        "left",
        "hcenter",
        "right",
        "top",
        "vcenter",
        "bottom",
    }

    if mode not in allowed:
        raise ValueError(
            f"Alignement inconnu : {mode}"
        )

    page, ids, elements = _selection(
        book,
        page_id,
        element_ids,
        minimum=2,
    )

    snapshot = deepcopy(
        book
    )

    try:
        geometries = [
            _geometry(
                element
            )
            for element in elements
        ]

        left = min(
            x
            for x, y, w, h
            in geometries
        )

        right = max(
            x + w
            for x, y, w, h
            in geometries
        )

        top = min(
            y
            for x, y, w, h
            in geometries
        )

        bottom = max(
            y + h
            for x, y, w, h
            in geometries
        )

        hcenter = (
            left + right
        ) / 2.0

        vcenter = (
            top + bottom
        ) / 2.0

        for element_id, element in zip(
            ids,
            elements,
        ):
            x, y, width, height = (
                _geometry(
                    element
                )
            )

            kwargs = {}

            if mode == "left":
                kwargs["x_mm"] = left

            elif mode == "hcenter":
                kwargs["x_mm"] = (
                    hcenter
                    - width / 2.0
                )

            elif mode == "right":
                kwargs["x_mm"] = (
                    right - width
                )

            elif mode == "top":
                kwargs["y_mm"] = top

            elif mode == "vcenter":
                kwargs["y_mm"] = (
                    vcenter
                    - height / 2.0
                )

            elif mode == "bottom":
                kwargs["y_mm"] = (
                    bottom - height
                )

            update_element_geometry(
                book,
                page_id,
                element_id,
                **kwargs,
            )

        _record(
            book,
            page,
            "composition_elements_aligned",
            ids,
            mode=mode,
        )

        book.validate()

        return ids

    except Exception:
        _restore_book(
            book,
            snapshot,
        )
        raise


# =============================================================
# DISTRIBUTION
# =============================================================

def distribute_elements(
    book: BookV4,
    page_id: str,
    element_ids: Iterable[str],
    *,
    axis: str,
) -> list[str]:
    """
    Répartit des espaces égaux entre au moins 3 éléments.

    Le premier et le dernier restent fixes.
    """

    book.validate()

    axis = str(
        axis
    ).strip().lower()

    if axis not in {
        "horizontal",
        "vertical",
    }:
        raise ValueError(
            f"Axe de distribution inconnu : {axis}"
        )

    page, ids, elements = _selection(
        book,
        page_id,
        element_ids,
        minimum=3,
    )

    snapshot = deepcopy(
        book
    )

    try:
        items = []

        for element_id, element in zip(
            ids,
            elements,
        ):
            x, y, width, height = (
                _geometry(
                    element
                )
            )

            items.append(
                {
                    "id": element_id,
                    "x": x,
                    "y": y,
                    "width": width,
                    "height": height,
                }
            )

        if axis == "horizontal":
            items.sort(
                key=lambda item: (
                    item["x"],
                    item["id"],
                )
            )

            start = items[0]["x"]
            end = (
                items[-1]["x"]
                + items[-1]["width"]
            )

            total_width = sum(
                item["width"]
                for item in items
            )

            gap = (
                end
                - start
                - total_width
            ) / (
                len(items) - 1
            )

            cursor = start

            for item in items:
                update_element_geometry(
                    book,
                    page_id,
                    item["id"],
                    x_mm=cursor,
                )

                cursor += (
                    item["width"]
                    + gap
                )

        else:
            items.sort(
                key=lambda item: (
                    item["y"],
                    item["id"],
                )
            )

            start = items[0]["y"]
            end = (
                items[-1]["y"]
                + items[-1]["height"]
            )

            total_height = sum(
                item["height"]
                for item in items
            )

            gap = (
                end
                - start
                - total_height
            ) / (
                len(items) - 1
            )

            cursor = start

            for item in items:
                update_element_geometry(
                    book,
                    page_id,
                    item["id"],
                    y_mm=cursor,
                )

                cursor += (
                    item["height"]
                    + gap
                )

        _record(
            book,
            page,
            "composition_elements_distributed",
            ids,
            axis=axis,
        )

        book.validate()

        return ids

    except Exception:
        _restore_book(
            book,
            snapshot,
        )
        raise


# =============================================================
# EGALISATION
# =============================================================

def equalize_elements(
    book: BookV4,
    page_id: str,
    element_ids: Iterable[str],
    *,
    mode: str,
) -> list[str]:
    """
    width, height ou both.

    Le premier élément explicitement sélectionné sert de référence.
    """

    book.validate()

    mode = str(
        mode
    ).strip().lower()

    if mode not in {
        "width",
        "height",
        "both",
    }:
        raise ValueError(
            f"Égalisation inconnue : {mode}"
        )

    raw_ids = [
        str(value)
        for value in element_ids
    ]

    if not raw_ids:
        raise ValueError(
            "Sélection vide."
        )

    page, ids, elements = _selection(
        book,
        page_id,
        raw_ids,
        minimum=2,
    )

    reference = element_by_id(
        page,
        raw_ids[0],
    )

    ref_x, ref_y, ref_width, ref_height = (
        _geometry(
            reference
        )
    )

    snapshot = deepcopy(
        book
    )

    try:
        for element_id in ids:
            kwargs = {}

            if mode in {
                "width",
                "both",
            }:
                kwargs[
                    "width_mm"
                ] = ref_width

            if mode in {
                "height",
                "both",
            }:
                kwargs[
                    "height_mm"
                ] = ref_height

            update_element_geometry(
                book,
                page_id,
                element_id,
                **kwargs,
            )

        _record(
            book,
            page,
            "composition_elements_equalized",
            ids,
            mode=mode,
            reference_element_id=(
                raw_ids[0]
            ),
        )

        book.validate()

        return ids

    except Exception:
        _restore_book(
            book,
            snapshot,
        )
        raise


# =============================================================
# SUPERPOSITION
# =============================================================

def _reorder_selection(
    book: BookV4,
    page_id: str,
    element_ids: Iterable[str],
    *,
    operation: str,
) -> list[str]:

    book.validate()

    page, ids, elements = _selection(
        book,
        page_id,
        element_ids,
        minimum=1,
    )

    selected = set(
        ids
    )

    snapshot = deepcopy(
        book
    )

    try:
        content = page.content

        def element_id(
            item,
        ):
            if (
                isinstance(
                    item,
                    dict,
                )
                and item.get(
                    "schema"
                ) == COMPOSITION_SCHEMA
            ):
                return str(
                    item.get(
                        "id",
                        "",
                    )
                )

            return ""

        if operation in {
            "front",
            "back",
        }:
            chosen = [
                item
                for item in content
                if element_id(
                    item
                ) in selected
            ]

            others = [
                item
                for item in content
                if element_id(
                    item
                ) not in selected
            ]

            if operation == "front":
                page.content = (
                    others + chosen
                )
            else:
                page.content = (
                    chosen + others
                )

        elif operation == "forward":
            for index in range(
                len(content) - 2,
                -1,
                -1,
            ):
                current_id = (
                    element_id(
                        content[index]
                    )
                )

                next_id = (
                    element_id(
                        content[index + 1]
                    )
                )

                if (
                    current_id in selected
                    and next_id not in selected
                ):
                    (
                        content[index],
                        content[index + 1],
                    ) = (
                        content[index + 1],
                        content[index],
                    )

        elif operation == "backward":
            for index in range(
                1,
                len(content),
            ):
                current_id = (
                    element_id(
                        content[index]
                    )
                )

                previous_id = (
                    element_id(
                        content[index - 1]
                    )
                )

                if (
                    current_id in selected
                    and previous_id not in selected
                ):
                    (
                        content[index],
                        content[index - 1],
                    ) = (
                        content[index - 1],
                        content[index],
                    )

        else:
            raise ValueError(
                f"Opération de calque inconnue : {operation}"
            )

        _record(
            book,
            page,
            "composition_z_order_changed",
            ids,
            operation=operation,
        )

        book.validate()

        return ids

    except Exception:
        _restore_book(
            book,
            snapshot,
        )
        raise


def bring_to_front(
    book,
    page_id,
    element_ids,
):
    return _reorder_selection(
        book,
        page_id,
        element_ids,
        operation="front",
    )


def send_to_back(
    book,
    page_id,
    element_ids,
):
    return _reorder_selection(
        book,
        page_id,
        element_ids,
        operation="back",
    )


def bring_forward(
    book,
    page_id,
    element_ids,
):
    return _reorder_selection(
        book,
        page_id,
        element_ids,
        operation="forward",
    )


def send_backward(
    book,
    page_id,
    element_ids,
):
    return _reorder_selection(
        book,
        page_id,
        element_ids,
        operation="backward",
    )


# =============================================================
# ASSOCIATION / DISSOCIATION
# =============================================================

def associate_elements(
    book: BookV4,
    page_id: str,
    element_ids: Iterable[str],
) -> str:
    """
    Associe au moins deux éléments.

    Si l'un appartenait déjà à un groupe, tout ce groupe est inclus.
    """

    book.validate()

    page, ids, elements = _selection(
        book,
        page_id,
        element_ids,
        minimum=2,
        include_associated=True,
    )

    group_id = str(
        uuid4()
    )

    snapshot = deepcopy(
        book
    )

    try:
        for element in elements:
            metadata = element.setdefault(
                "metadata",
                {},
            )

            metadata[
                GROUP_KEY
            ] = group_id

        _record(
            book,
            page,
            "composition_elements_associated",
            ids,
            group_id=group_id,
        )

        book.validate()

        return group_id

    except Exception:
        _restore_book(
            book,
            snapshot,
        )
        raise


def dissociate_elements(
    book: BookV4,
    page_id: str,
    element_ids: Iterable[str],
) -> list[str]:
    """
    Dissocie tous les groupes touchés par la sélection.
    """

    book.validate()

    page = _page(
        book,
        page_id,
    )

    selected = normalize_selection(
        book,
        page_id,
        element_ids,
        include_associated=True,
    )

    if not selected:
        raise ValueError(
            "Sélection vide."
        )

    snapshot = deepcopy(
        book
    )

    try:
        changed: list[str] = []

        for element_id in selected:
            element = element_by_id(
                page,
                element_id,
            )

            metadata = element.get(
                "metadata",
                {},
            )

            if GROUP_KEY in metadata:
                metadata.pop(
                    GROUP_KEY,
                    None,
                )

                changed.append(
                    element_id
                )

        if not changed:
            raise ValueError(
                "Aucun élément sélectionné n'est associé."
            )

        _record(
            book,
            page,
            "composition_elements_dissociated",
            changed,
        )

        book.validate()

        return changed

    except Exception:
        _restore_book(
            book,
            snapshot,
        )
        raise
