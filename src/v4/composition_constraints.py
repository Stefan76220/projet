from __future__ import annotations

"""
TomeLinea V4 — accrochage et contraintes de Composition.

Ce module constitue la couche sûre des commandes utilisateur.

Séparation :
- le Livre contient le résultat réel des manipulations ;
- le verrouillage appartient seulement à l'espace de travail Projet ;
- les moteurs bas niveau restent utilisables par les automatismes
  internes (modèles, synchronisations, etc.).

Principes :
- aucune limite dure Marges/Page/Fond perdu ;
- accrochage facultatif sur ces référentiels ;
- déplacement libre, horizontal ou vertical ;
- palier orthogonal de rotation ;
- un élément verrouillé refuse les commandes utilisateur ;
- le verrouillage ne modifie jamais BookState.
"""

from copy import deepcopy
from datetime import datetime, timezone
from typing import Iterable, Any

from src.v4.project import ProjectV4

from src.v4.composition import (
    MARGINS,
    PAGE,
    BLEED,
    element_by_id,
    frame_bounds,
    remove_element,
    update_element_geometry,
)

from src.v4.composition_geometry import (
    resize_from_handle,
    set_rotation,
)

from src.v4.composition_arrange import (
    normalize_selection,
    align_elements as _align_elements,
    distribute_elements as _distribute_elements,
    equalize_elements as _equalize_elements,
    bring_to_front,
    send_to_back,
    bring_forward,
    send_backward,
    associate_elements,
    dissociate_elements,
)


LOCKS_KEY = "composition_locks"

SNAP_FRAMES = (
    MARGINS,
    PAGE,
    BLEED,
)


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def _book(
    project: ProjectV4,
):
    if project.book is None:
        raise ValueError(
            "Le Projet ne possède aucun Livre."
        )

    return project.book


def _page(
    project: ProjectV4,
    page_id: str,
):
    book = _book(
        project
    )

    page = book.pages.get(
        page_id
    )

    if page is None:
        raise KeyError(
            page_id
        )

    return page


def _locks_root(
    project: ProjectV4,
    *,
    create: bool = True,
) -> dict[str, list[str]]:

    raw = project.metadata.get(
        LOCKS_KEY
    )

    if isinstance(
        raw,
        dict,
    ):
        return raw

    if not create:
        return {}

    result: dict[
        str,
        list[str],
    ] = {}

    project.metadata[
        LOCKS_KEY
    ] = result

    return result


def locked_element_ids(
    project: ProjectV4,
    page_id: str,
) -> set[str]:

    _page(
        project,
        page_id,
    )

    raw = _locks_root(
        project,
        create=False,
    ).get(
        page_id,
        [],
    )

    if not isinstance(
        raw,
        list,
    ):
        return set()

    return {
        str(value)
        for value in raw
    }


def is_element_locked(
    project: ProjectV4,
    page_id: str,
    element_id: str,
) -> bool:

    page = _page(
        project,
        page_id,
    )

    element_by_id(
        page,
        element_id,
    )

    return (
        str(element_id)
        in locked_element_ids(
            project,
            page_id,
        )
    )


def set_elements_locked(
    project: ProjectV4,
    page_id: str,
    element_ids: Iterable[str],
    *,
    locked: bool,
) -> list[str]:
    """
    Verrouille ou déverrouille une sélection.

    Une association est considérée comme un ensemble :
    sélectionner un de ses membres étend donc le verrouillage
    à tout le groupe.
    """

    project.validate()

    book = _book(
        project
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

    root = _locks_root(
        project
    )

    current = set(
        locked_element_ids(
            project,
            page_id,
        )
    )

    if locked:
        current.update(
            selected
        )
    else:
        current.difference_update(
            selected
        )

    if current:
        root[
            page_id
        ] = sorted(
            current
        )
    else:
        root.pop(
            page_id,
            None,
        )

    project.history.append(
        {
            "action": (
                "composition_elements_locked"
                if locked
                else "composition_elements_unlocked"
            ),
            "page_id": page_id,
            "element_ids": list(
                selected
            ),
            "date": utc_now(),
        }
    )

    project.touch()
    project.validate()

    return selected


def _ensure_unlocked(
    project: ProjectV4,
    page_id: str,
    element_ids: Iterable[str],
    *,
    include_associated: bool = True,
) -> list[str]:

    book = _book(
        project
    )

    selected = normalize_selection(
        book,
        page_id,
        element_ids,
        include_associated=(
            include_associated
        ),
    )

    if not selected:
        raise ValueError(
            "Sélection vide."
        )

    locked = (
        locked_element_ids(
            project,
            page_id,
        )
    )

    blocked = [
        element_id
        for element_id in selected
        if element_id in locked
    ]

    if blocked:
        raise ValueError(
            "Un ou plusieurs éléments sont verrouillés : "
            + ", ".join(
                blocked
            )
        )

    return selected


def _geometry(
    project: ProjectV4,
    page_id: str,
    element_id: str,
) -> dict[str, float]:

    element = element_by_id(
        _page(
            project,
            page_id,
        ),
        element_id,
    )

    geometry = element[
        "geometry"
    ]

    return {
        "x_mm": float(
            geometry[
                "x_mm"
            ]
        ),
        "y_mm": float(
            geometry[
                "y_mm"
            ]
        ),
        "width_mm": float(
            geometry[
                "width_mm"
            ]
        ),
        "height_mm": float(
            geometry[
                "height_mm"
            ]
        ),
        "rotation_deg": float(
            geometry.get(
                "rotation_deg",
                0.0,
            )
        ),
    }


def _best_snap(
    position: float,
    size: float,
    guides: Iterable[float],
    threshold: float,
) -> float:

    anchors = (
        position,
        position + size / 2.0,
        position + size,
    )

    best_delta: float | None = None

    for anchor in anchors:
        for guide in guides:
            delta = (
                float(guide)
                - anchor
            )

            if abs(
                delta
            ) > threshold:
                continue

            if (
                best_delta is None
                or abs(delta)
                < abs(best_delta)
            ):
                best_delta = delta

    if best_delta is None:
        return position

    return (
        position
        + best_delta
    )


def _frame_guides(
    project: ProjectV4,
    page_id: str,
    frames: Iterable[str],
) -> tuple[
    list[float],
    list[float],
]:

    book = _book(
        project
    )

    xs: list[float] = []
    ys: list[float] = []

    for frame in frames:
        x, y, width, height = (
            frame_bounds(
                book,
                page_id,
                frame,
            )
        )

        xs.extend(
            [
                x,
                x + width / 2.0,
                x + width,
            ]
        )

        ys.extend(
            [
                y,
                y + height / 2.0,
                y + height,
            ]
        )

    return (
        xs,
        ys,
    )


def move_element(
    project: ProjectV4,
    page_id: str,
    element_id: str,
    *,
    dx_mm: float,
    dy_mm: float,
    axis: str = "free",
    snapping: bool = True,
    snap_threshold_mm: float = 2.0,
    snap_frames: Iterable[str] = SNAP_FRAMES,
):
    """
    Déplacement utilisateur sécurisé.

    axis :
    - free
    - horizontal
    - vertical
    """

    _ensure_unlocked(
        project,
        page_id,
        [
            element_id
        ],
        include_associated=False,
    )

    axis = str(
        axis
    ).strip().lower()

    if axis not in {
        "free",
        "horizontal",
        "vertical",
    }:
        raise ValueError(
            f"Contrainte de déplacement inconnue : {axis}"
        )

    threshold = float(
        snap_threshold_mm
    )

    if threshold < 0:
        raise ValueError(
            "Seuil d'accrochage négatif."
        )

    geometry = _geometry(
        project,
        page_id,
        element_id,
    )

    dx = float(
        dx_mm
    )
    dy = float(
        dy_mm
    )

    if axis == "horizontal":
        dy = 0.0

    elif axis == "vertical":
        dx = 0.0

    x = (
        geometry[
            "x_mm"
        ]
        + dx
    )

    y = (
        geometry[
            "y_mm"
        ]
        + dy
    )

    if snapping:
        xs, ys = _frame_guides(
            project,
            page_id,
            snap_frames,
        )

        if axis != "vertical":
            x = _best_snap(
                x,
                geometry[
                    "width_mm"
                ],
                xs,
                threshold,
            )

        if axis != "horizontal":
            y = _best_snap(
                y,
                geometry[
                    "height_mm"
                ],
                ys,
                threshold,
            )

    result = update_element_geometry(
        _book(project),
        page_id,
        element_id,
        x_mm=x,
        y_mm=y,
    )

    project.touch()

    return result


def resize_element(
    project: ProjectV4,
    page_id: str,
    element_id: str,
    *,
    handle: str,
    dx_mm: float,
    dy_mm: float,
    min_size_mm: float = 0.1,
):
    """
    Redimensionnement sécurisé.

    Les règles proportionnelles des poignées d'angle
    restent celles du moteur géométrique déjà validé.
    """

    _ensure_unlocked(
        project,
        page_id,
        [
            element_id
        ],
        include_associated=False,
    )

    result = resize_from_handle(
        _book(project),
        page_id,
        element_id,
        handle=handle,
        dx_mm=dx_mm,
        dy_mm=dy_mm,
        min_size_mm=min_size_mm,
    )

    project.touch()

    return result


def orthogonal_angle(
    angle_deg: float,
    *,
    tolerance_deg: float = 4.0,
    step_deg: float = 90.0,
) -> float:
    """
    Palier orthogonal.

    Un angle suffisamment proche de 0/90/180/270...
    est parfaitement accroché.
    """

    angle = float(
        angle_deg
    )

    tolerance = float(
        tolerance_deg
    )

    step = float(
        step_deg
    )

    if tolerance < 0:
        raise ValueError(
            "Tolérance négative."
        )

    if step <= 0:
        raise ValueError(
            "Pas angulaire invalide."
        )

    nearest = round(
        angle / step
    ) * step

    if abs(
        angle - nearest
    ) <= tolerance:
        return float(
            nearest
        )

    return angle


def rotate_element(
    project: ProjectV4,
    page_id: str,
    element_id: str,
    *,
    angle_deg: float,
    orthogonal_snap: bool = True,
    tolerance_deg: float = 4.0,
):
    """
    Rotation absolue sécurisée.
    """

    _ensure_unlocked(
        project,
        page_id,
        [
            element_id
        ],
        include_associated=False,
    )

    angle = float(
        angle_deg
    )

    if orthogonal_snap:
        angle = orthogonal_angle(
            angle,
            tolerance_deg=(
                tolerance_deg
            ),
        )

    result = set_rotation(
        _book(project),
        page_id,
        element_id,
        angle,
    )

    project.touch()

    return result


def delete_element(
    project: ProjectV4,
    page_id: str,
    element_id: str,
):
    """
    Suppression utilisateur sécurisée.
    """

    _ensure_unlocked(
        project,
        page_id,
        [
            element_id
        ],
        include_associated=False,
    )

    removed = remove_element(
        _book(project),
        page_id,
        element_id,
    )

    root = _locks_root(
        project
    )

    current = set(
        root.get(
            page_id,
            [],
        )
    )

    current.discard(
        element_id
    )

    if current:
        root[
            page_id
        ] = sorted(
            current
        )
    else:
        root.pop(
            page_id,
            None,
        )

    project.touch()

    return removed


# =============================================================
# Organisation sécurisée
# =============================================================

def align_selection(
    project: ProjectV4,
    page_id: str,
    element_ids: Iterable[str],
    *,
    mode: str,
):

    selected = _ensure_unlocked(
        project,
        page_id,
        element_ids,
    )

    result = _align_elements(
        _book(project),
        page_id,
        selected,
        mode=mode,
    )

    project.touch()

    return result


def distribute_selection(
    project: ProjectV4,
    page_id: str,
    element_ids: Iterable[str],
    *,
    axis: str,
):

    selected = _ensure_unlocked(
        project,
        page_id,
        element_ids,
    )

    result = _distribute_elements(
        _book(project),
        page_id,
        selected,
        axis=axis,
    )

    project.touch()

    return result


def equalize_selection(
    project: ProjectV4,
    page_id: str,
    element_ids: Iterable[str],
    *,
    mode: str,
):

    raw = [
        str(value)
        for value in element_ids
    ]

    _ensure_unlocked(
        project,
        page_id,
        raw,
    )

    result = _equalize_elements(
        _book(project),
        page_id,
        raw,
        mode=mode,
    )

    project.touch()

    return result


def change_z_order(
    project: ProjectV4,
    page_id: str,
    element_ids: Iterable[str],
    *,
    operation: str,
):

    selected = _ensure_unlocked(
        project,
        page_id,
        element_ids,
    )

    operation = str(
        operation
    ).strip().lower()

    functions = {
        "front": bring_to_front,
        "back": send_to_back,
        "forward": bring_forward,
        "backward": send_backward,
    }

    function = functions.get(
        operation
    )

    if function is None:
        raise ValueError(
            "Opération de superposition inconnue : "
            f"{operation}"
        )

    result = function(
        _book(project),
        page_id,
        selected,
    )

    project.touch()

    return result


def associate_selection(
    project: ProjectV4,
    page_id: str,
    element_ids: Iterable[str],
):

    selected = _ensure_unlocked(
        project,
        page_id,
        element_ids,
    )

    result = associate_elements(
        _book(project),
        page_id,
        selected,
    )

    project.touch()

    return result


def dissociate_selection(
    project: ProjectV4,
    page_id: str,
    element_ids: Iterable[str],
):

    selected = _ensure_unlocked(
        project,
        page_id,
        element_ids,
    )

    result = dissociate_elements(
        _book(project),
        page_id,
        selected,
    )

    project.touch()

    return result


def composition_constraint_issues(
    project: ProjectV4,
) -> list[str]:

    issues: list[str] = []

    if project.book is None:
        if _locks_root(
            project,
            create=False,
        ):
            issues.append(
                "Des verrouillages existent sans Livre."
            )

        return issues

    for page_id, element_ids in (
        _locks_root(
            project,
            create=False,
        ).items()
    ):
        page = project.book.pages.get(
            page_id
        )

        if page is None:
            issues.append(
                "Verrouillage sur page inconnue : "
                f"{page_id}"
            )

            continue

        if not isinstance(
            element_ids,
            list,
        ):
            issues.append(
                "Liste de verrouillage invalide : "
                f"{page_id}"
            )

            continue

        for element_id in element_ids:
            try:
                element_by_id(
                    page,
                    str(element_id),
                )
            except KeyError:
                issues.append(
                    "Verrouillage sur élément inconnu : "
                    f"{page_id}/{element_id}"
                )

    return issues
