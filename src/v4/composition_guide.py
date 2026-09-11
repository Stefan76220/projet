from __future__ import annotations

"""
TomeLinea V4 — Fond guide de Composition.

Le Fond guide appartient à l'espace de travail du Projet,
PAS au Livre.

Conséquences :
- jamais imprimé ;
- jamais exporté ;
- jamais envoyé au Visionneur ;
- sa visibilité/transparence ne modifie pas BookState ;
- il reste cependant sauvegardé avec le Projet ;
- il est rattaché à l'UUID stable de la page.

Le fichier réel sera géré plus tard par le gestionnaire d'assets.
Ici, asset_ref est une référence logique JSON.
"""

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from src.v4.project import ProjectV4

from src.v4.composition import (
    MARGINS,
    normalize_reference_frame,
    frame_bounds,
)


GUIDES_KEY = "composition_guides"

GUIDE_SCHEMA = (
    "tomelinea-composition-guide"
)

GUIDE_VERSION = 1


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


def new_id() -> str:
    return str(
        uuid4()
    )


def _book(
    project: ProjectV4,
):
    if project.book is None:
        raise ValueError(
            "Le Projet ne possède aucun Livre."
        )

    return project.book


def _page_exists(
    project: ProjectV4,
    page_id: str,
) -> None:

    book = _book(
        project
    )

    if page_id not in book.pages:
        raise KeyError(
            page_id
        )


def _guides_root(
    project: ProjectV4,
    *,
    create: bool = True,
) -> dict[str, dict[str, Any]]:

    raw = project.metadata.get(
        GUIDES_KEY
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
        dict[str, Any],
    ] = {}

    project.metadata[
        GUIDES_KEY
    ] = result

    return result


def validate_guide(
    guide: dict[str, Any],
) -> None:

    if not isinstance(
        guide,
        dict,
    ):
        raise ValueError(
            "Fond guide invalide."
        )

    if guide.get(
        "schema"
    ) != GUIDE_SCHEMA:
        raise ValueError(
            "Schéma Fond guide inconnu."
        )

    if guide.get(
        "version"
    ) != GUIDE_VERSION:
        raise ValueError(
            "Version Fond guide inconnue."
        )

    if not str(
        guide.get(
            "id"
        )
        or ""
    ).strip():
        raise ValueError(
            "UUID Fond guide absent."
        )

    if not str(
        guide.get(
            "page_id"
        )
        or ""
    ).strip():
        raise ValueError(
            "Page Fond guide absente."
        )

    asset_ref = guide.get(
        "asset_ref"
    )

    if not isinstance(
        asset_ref,
        dict,
    ):
        raise ValueError(
            "Référence d'asset Fond guide invalide."
        )

    if not asset_ref:
        raise ValueError(
            "Référence d'asset Fond guide vide."
        )

    opacity = float(
        guide.get(
            "opacity",
            1.0,
        )
    )

    if not (
        0.0 <= opacity <= 1.0
    ):
        raise ValueError(
            "La transparence doit être comprise "
            "entre 0 et 1."
        )

    normalize_reference_frame(
        str(
            guide.get(
                "reference_frame",
                ""
            )
        )
    )

    if not isinstance(
        guide.get(
            "visible"
        ),
        bool,
    ):
        raise ValueError(
            "État de visibilité Fond guide invalide."
        )


def guide_for_page(
    project: ProjectV4,
    page_id: str,
) -> dict[str, Any] | None:

    _page_exists(
        project,
        page_id,
    )

    raw = _guides_root(
        project,
        create=False,
    ).get(
        page_id
    )

    if raw is None:
        return None

    validate_guide(
        raw
    )

    return deepcopy(
        raw
    )


def set_guide(
    project: ProjectV4,
    page_id: str,
    *,
    asset_ref: dict[str, Any],
    opacity: float = 0.5,
    visible: bool = True,
    reference_frame: str = MARGINS,
) -> dict[str, Any]:
    """
    Importe ou remplace le Fond guide d'une page.

    Si un guide existe déjà, son UUID est conservé.
    """

    project.validate()

    _page_exists(
        project,
        page_id,
    )

    if not isinstance(
        asset_ref,
        dict,
    ) or not asset_ref:
        raise ValueError(
            "Référence d'asset invalide."
        )

    value_opacity = float(
        opacity
    )

    if not (
        0.0 <= value_opacity <= 1.0
    ):
        raise ValueError(
            "La transparence doit être comprise "
            "entre 0 et 1."
        )

    frame = normalize_reference_frame(
        reference_frame
    )

    guides = _guides_root(
        project
    )

    existing = guides.get(
        page_id
    )

    guide_id = (
        str(existing["id"])
        if isinstance(
            existing,
            dict,
        )
        and existing.get(
            "id"
        )
        else new_id()
    )

    date = utc_now()

    guide = {
        "schema": GUIDE_SCHEMA,
        "version": GUIDE_VERSION,
        "id": guide_id,
        "page_id": page_id,
        "asset_ref": deepcopy(
            asset_ref
        ),
        "visible": bool(
            visible
        ),
        "opacity": value_opacity,
        "reference_frame": frame,
        "updated_at": date,
    }

    if (
        isinstance(
            existing,
            dict,
        )
        and existing.get(
            "created_at"
        )
    ):
        guide[
            "created_at"
        ] = existing[
            "created_at"
        ]
    else:
        guide[
            "created_at"
        ] = date

    validate_guide(
        guide
    )

    guides[
        page_id
    ] = guide

    project.history.append(
        {
            "action": (
                "composition_guide_set"
            ),
            "page_id": page_id,
            "guide_id": guide_id,
            "date": date,
        }
    )

    project.touch()
    project.validate()

    return deepcopy(
        guide
    )


def replace_guide_asset(
    project: ProjectV4,
    page_id: str,
    *,
    asset_ref: dict[str, Any],
) -> dict[str, Any]:

    current = guide_for_page(
        project,
        page_id,
    )

    if current is None:
        raise ValueError(
            "Aucun Fond guide à remplacer."
        )

    return set_guide(
        project,
        page_id,
        asset_ref=asset_ref,
        opacity=float(
            current["opacity"]
        ),
        visible=bool(
            current["visible"]
        ),
        reference_frame=str(
            current[
                "reference_frame"
            ]
        ),
    )


def set_guide_visibility(
    project: ProjectV4,
    page_id: str,
    visible: bool,
) -> dict[str, Any]:

    guides = _guides_root(
        project
    )

    guide = guides.get(
        page_id
    )

    if guide is None:
        raise ValueError(
            "Aucun Fond guide sur cette page."
        )

    validate_guide(
        guide
    )

    guide[
        "visible"
    ] = bool(
        visible
    )

    guide[
        "updated_at"
    ] = utc_now()

    project.touch()

    return deepcopy(
        guide
    )


def set_guide_opacity(
    project: ProjectV4,
    page_id: str,
    opacity: float,
) -> dict[str, Any]:

    value = float(
        opacity
    )

    if not (
        0.0 <= value <= 1.0
    ):
        raise ValueError(
            "La transparence doit être comprise "
            "entre 0 et 1."
        )

    guides = _guides_root(
        project
    )

    guide = guides.get(
        page_id
    )

    if guide is None:
        raise ValueError(
            "Aucun Fond guide sur cette page."
        )

    validate_guide(
        guide
    )

    guide[
        "opacity"
    ] = value

    guide[
        "updated_at"
    ] = utc_now()

    project.touch()

    return deepcopy(
        guide
    )


def set_guide_frame(
    project: ProjectV4,
    page_id: str,
    reference_frame: str,
) -> dict[str, Any]:

    frame = normalize_reference_frame(
        reference_frame
    )

    guides = _guides_root(
        project
    )

    guide = guides.get(
        page_id
    )

    if guide is None:
        raise ValueError(
            "Aucun Fond guide sur cette page."
        )

    validate_guide(
        guide
    )

    guide[
        "reference_frame"
    ] = frame

    guide[
        "updated_at"
    ] = utc_now()

    project.touch()

    return deepcopy(
        guide
    )


def guide_bounds(
    project: ProjectV4,
    page_id: str,
) -> tuple[
    float,
    float,
    float,
    float,
]:

    guide = guide_for_page(
        project,
        page_id,
    )

    if guide is None:
        raise ValueError(
            "Aucun Fond guide sur cette page."
        )

    return frame_bounds(
        _book(project),
        page_id,
        str(
            guide[
                "reference_frame"
            ]
        ),
    )


def remove_guide(
    project: ProjectV4,
    page_id: str,
) -> bool:

    guides = _guides_root(
        project,
        create=False,
    )

    guide = guides.get(
        page_id
    )

    if guide is None:
        return False

    guide_id = str(
        guide.get(
            "id",
            "",
        )
    )

    guides.pop(
        page_id
    )

    project.history.append(
        {
            "action": (
                "composition_guide_removed"
            ),
            "page_id": page_id,
            "guide_id": guide_id,
            "date": utc_now(),
        }
    )

    project.touch()

    return True


def composition_guide_issues(
    project: ProjectV4,
) -> list[str]:

    issues: list[str] = []

    if project.book is None:
        if _guides_root(
            project,
            create=False,
        ):
            issues.append(
                "Des Fonds guides existent "
                "sans Livre."
            )

        return issues

    for page_id, guide in (
        _guides_root(
            project,
            create=False,
        ).items()
    ):
        if page_id not in (
            project.book.pages
        ):
            issues.append(
                "Fond guide rattaché à une "
                f"page inconnue : {page_id}"
            )

            continue

        try:
            validate_guide(
                guide
            )

            if str(
                guide.get(
                    "page_id"
                )
            ) != page_id:
                issues.append(
                    "Identité de page Fond guide "
                    f"incohérente : {page_id}"
                )

        except Exception as exc:
            issues.append(
                f"Fond guide {page_id} : {exc}"
            )

    return issues
