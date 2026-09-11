from __future__ import annotations

"""
TomeLinea V4 — moteur géométrique de Composition.

Ce module ne contient aucune interface graphique.

Principes :
- déplacement libre ;
- poignées latérales = largeur/hauteur indépendante ;
- poignées d'angle = proportions conservées ;
- l'angle opposé reste fixe pendant un redimensionnement ;
- rotation libre ;
- accrochage possible aux Marges / Page / Fond perdu ;
- les référentiels restent des guides, jamais des barrières.
"""

from typing import Literal

from src.v4.domain import BookV4
from src.v4.composition import (
    MARGINS,
    element_by_id,
    frame_bounds,
    update_element_geometry,
)


Handle = Literal[
    "nw", "n", "ne",
    "w",       "e",
    "sw", "s", "se",
]

HorizontalSnap = Literal[
    "left",
    "center",
    "right",
]

VerticalSnap = Literal[
    "top",
    "center",
    "bottom",
]


HANDLES = {
    "nw", "n", "ne",
    "w", "e",
    "sw", "s", "se",
}

CORNER_HANDLES = {
    "nw",
    "ne",
    "sw",
    "se",
}


def _geometry(
    book: BookV4,
    page_id: str,
    element_id: str,
) -> dict[str, float]:

    page = book.pages.get(
        page_id
    )

    if page is None:
        raise KeyError(
            page_id
        )

    element = element_by_id(
        page,
        element_id,
    )

    geometry = element[
        "geometry"
    ]

    return {
        "x_mm": float(
            geometry["x_mm"]
        ),
        "y_mm": float(
            geometry["y_mm"]
        ),
        "width_mm": float(
            geometry["width_mm"]
        ),
        "height_mm": float(
            geometry["height_mm"]
        ),
        "rotation_deg": float(
            geometry.get(
                "rotation_deg",
                0.0,
            )
        ),
    }


def translate_element(
    book: BookV4,
    page_id: str,
    element_id: str,
    *,
    dx_mm: float,
    dy_mm: float,
):
    """
    Déplace librement un élément.

    Aucun référentiel ne limite le déplacement.
    """

    geometry = _geometry(
        book,
        page_id,
        element_id,
    )

    return update_element_geometry(
        book,
        page_id,
        element_id,
        x_mm=(
            geometry["x_mm"]
            + float(dx_mm)
        ),
        y_mm=(
            geometry["y_mm"]
            + float(dy_mm)
        ),
    )


def set_rotation(
    book: BookV4,
    page_id: str,
    element_id: str,
    angle_deg: float,
):
    """
    Définit l'angle absolu de rotation.
    """

    return update_element_geometry(
        book,
        page_id,
        element_id,
        rotation_deg=float(
            angle_deg
        ),
    )


def rotate_element(
    book: BookV4,
    page_id: str,
    element_id: str,
    *,
    delta_deg: float,
):
    """
    Rotation relative.
    """

    geometry = _geometry(
        book,
        page_id,
        element_id,
    )

    return set_rotation(
        book,
        page_id,
        element_id,
        geometry["rotation_deg"]
        + float(delta_deg),
    )


def resize_from_handle(
    book: BookV4,
    page_id: str,
    element_id: str,
    *,
    handle: Handle,
    dx_mm: float,
    dy_mm: float,
    min_size_mm: float = 0.1,
):
    """
    Redimensionnement depuis une poignée.

    Les côtés modifient une seule dimension.
    Les angles conservent les proportions.
    Le côté ou l'angle opposé reste fixe.
    """

    handle = str(
        handle
    ).strip().lower()

    if handle not in HANDLES:
        raise ValueError(
            f"Poignée inconnue : {handle}"
        )

    minimum = float(
        min_size_mm
    )

    if minimum <= 0:
        raise ValueError(
            "La taille minimale doit être positive."
        )

    dx = float(
        dx_mm
    )
    dy = float(
        dy_mm
    )

    geometry = _geometry(
        book,
        page_id,
        element_id,
    )

    x = geometry[
        "x_mm"
    ]
    y = geometry[
        "y_mm"
    ]
    width = geometry[
        "width_mm"
    ]
    height = geometry[
        "height_mm"
    ]

    # ---------------------------------------------------------
    # Poignées latérales
    # ---------------------------------------------------------

    if handle == "e":
        new_width = max(
            minimum,
            width + dx,
        )

        return update_element_geometry(
            book,
            page_id,
            element_id,
            width_mm=new_width,
        )

    if handle == "w":
        right = x + width

        new_width = max(
            minimum,
            width - dx,
        )

        return update_element_geometry(
            book,
            page_id,
            element_id,
            x_mm=right - new_width,
            width_mm=new_width,
        )

    if handle == "s":
        new_height = max(
            minimum,
            height + dy,
        )

        return update_element_geometry(
            book,
            page_id,
            element_id,
            height_mm=new_height,
        )

    if handle == "n":
        bottom = y + height

        new_height = max(
            minimum,
            height - dy,
        )

        return update_element_geometry(
            book,
            page_id,
            element_id,
            y_mm=bottom - new_height,
            height_mm=new_height,
        )

    # ---------------------------------------------------------
    # Poignées d'angle proportionnelles
    # ---------------------------------------------------------

    if handle in {
        "ne",
        "se",
    }:
        candidate_width = (
            width + dx
        )
    else:
        candidate_width = (
            width - dx
        )

    if handle in {
        "sw",
        "se",
    }:
        candidate_height = (
            height + dy
        )
    else:
        candidate_height = (
            height - dy
        )

    scale_x = (
        candidate_width
        / width
    )

    scale_y = (
        candidate_height
        / height
    )

    # Le déplacement relatif dominant pilote
    # le changement proportionnel.
    if abs(
        scale_x - 1.0
    ) >= abs(
        scale_y - 1.0
    ):
        scale = scale_x
    else:
        scale = scale_y

    minimum_scale = max(
        minimum / width,
        minimum / height,
    )

    scale = max(
        minimum_scale,
        scale,
    )

    new_width = (
        width * scale
    )

    new_height = (
        height * scale
    )

    if handle == "se":
        new_x = x
        new_y = y

    elif handle == "sw":
        new_x = (
            x
            + width
            - new_width
        )
        new_y = y

    elif handle == "ne":
        new_x = x
        new_y = (
            y
            + height
            - new_height
        )

    else:  # nw
        new_x = (
            x
            + width
            - new_width
        )
        new_y = (
            y
            + height
            - new_height
        )

    return update_element_geometry(
        book,
        page_id,
        element_id,
        x_mm=new_x,
        y_mm=new_y,
        width_mm=new_width,
        height_mm=new_height,
    )


def snap_to_frame(
    book: BookV4,
    page_id: str,
    element_id: str,
    *,
    reference_frame: str = MARGINS,
    horizontal: HorizontalSnap | None = None,
    vertical: VerticalSnap | None = None,
):
    """
    Accroche la boîte de l'élément à un référentiel.

    Cela modifie seulement sa position.
    Le référentiel mémorisé de l'élément n'est pas changé.
    """

    if (
        horizontal is None
        and vertical is None
    ):
        raise ValueError(
            "Aucun accrochage demandé."
        )

    if (
        horizontal is not None
        and horizontal
        not in {
            "left",
            "center",
            "right",
        }
    ):
        raise ValueError(
            "Accrochage horizontal invalide."
        )

    if (
        vertical is not None
        and vertical
        not in {
            "top",
            "center",
            "bottom",
        }
    ):
        raise ValueError(
            "Accrochage vertical invalide."
        )

    geometry = _geometry(
        book,
        page_id,
        element_id,
    )

    frame_x, frame_y, frame_w, frame_h = (
        frame_bounds(
            book,
            page_id,
            reference_frame,
        )
    )

    x = geometry[
        "x_mm"
    ]
    y = geometry[
        "y_mm"
    ]
    width = geometry[
        "width_mm"
    ]
    height = geometry[
        "height_mm"
    ]

    if horizontal == "left":
        x = frame_x

    elif horizontal == "center":
        x = (
            frame_x
            + (
                frame_w
                - width
            ) / 2.0
        )

    elif horizontal == "right":
        x = (
            frame_x
            + frame_w
            - width
        )

    if vertical == "top":
        y = frame_y

    elif vertical == "center":
        y = (
            frame_y
            + (
                frame_h
                - height
            ) / 2.0
        )

    elif vertical == "bottom":
        y = (
            frame_y
            + frame_h
            - height
        )

    return update_element_geometry(
        book,
        page_id,
        element_id,
        x_mm=x,
        y_mm=y,
    )
