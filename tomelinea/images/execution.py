"""Execution des Decisions de qualite Image de TomeLinea V5.

Le module reutilise exclusivement le moteur V4 ``image_quality`` :

- une image critique (< 200 dpi) peut etre reduite proportionnellement jusqu'au
  minimum valide via ``clamp_size_to_minimum_dpi`` ;
- ``Laisser comme ca`` ne modifie jamais la geometrie et memorise le choix ;
- une image seulement limitee (200-299 dpi) n'a pas de correction automatique
  inventee vers 300 dpi : elle peut etre conservee ou corrigee plus tard par un
  outil specialise/remplacement d'image.

Aucune similarite Image n'est appliquee ici.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.v4.image_quality import (
    MINIMUM_DPI,
    clamp_size_to_minimum_dpi,
    effective_dpi,
)

from tomelinea.rules import (
    Decision,
    DecisionScope,
    Situation,
)

from .api import (
    IMAGE_QUALITY_CRITICAL,
    IMAGE_QUALITY_LIMITED,
    IMAGE_QUALITY_SITUATION_KINDS,
)


IMAGE_CHOICE_CORRECTED = "corrected"
IMAGE_CHOICE_IGNORED = "ignored"
IMAGE_DECISION_CHOICES = (
    IMAGE_CHOICE_CORRECTED,
    IMAGE_CHOICE_IGNORED,
)

_IMAGE_DECISIONS_KEY = "image_quality_decisions"


@dataclass(frozen=True, slots=True)
class ImageDecisionExecution:
    situation_id: str
    subject_id: str
    choice: str
    changed: bool
    dpi_before: float
    dpi_after: float
    width_mm_before: float
    height_mm_before: float
    width_mm_after: float
    height_mm_after: float


def _validate_image_decision(
    situation: Situation,
    decision: Decision,
) -> str:
    if not isinstance(
        situation,
        Situation,
    ):
        raise TypeError(
            "Une Situation Image V5 est requise."
        )

    if not isinstance(
        decision,
        Decision,
    ):
        raise TypeError(
            "Une Decision V5 est requise."
        )

    if str(
        situation.domain
    ) != "image":
        raise ValueError(
            "Cette Situation n'appartient pas au domaine Image."
        )

    if str(
        situation.kind
    ) not in IMAGE_QUALITY_SITUATION_KINDS:
        raise ValueError(
            "Situation Image non prise en charge par le moteur qualite."
        )

    if decision.situation_id != situation.id:
        raise ValueError(
            "La Decision ne correspond pas a cette Situation."
        )

    if str(
        decision.subject_id
    ) != str(
        situation.subject_id
    ):
        raise ValueError(
            "La Decision ne vise pas la meme image stable."
        )

    if decision.scope != DecisionScope.LOCAL:
        raise ValueError(
            "Aucune extension par similarite Image n'est encore validee."
        )

    choice = str(
        decision.choice
        or ""
    ).strip()

    if choice not in IMAGE_DECISION_CHOICES:
        raise ValueError(
            "Choix Image inconnu : "
            + choice
        )

    return choice


def _find_image(
    book: Any,
    situation: Situation,
) -> dict[str, Any]:
    page_id = str(
        situation.page_id
        or ""
    ).strip()

    if not page_id:
        raise ValueError(
            "Situation Image sans page stable."
        )

    page = getattr(
        book,
        "pages",
        {},
    ).get(
        page_id
    )

    if page is None:
        raise ValueError(
            "La page de l'image n'existe plus."
        )

    subject_id = str(
        situation.subject_id
    )

    for element in getattr(
        page,
        "content",
        (),
    ):
        if not isinstance(
            element,
            dict,
        ):
            continue

        if str(
            element.get(
                "id",
                "",
            )
            or ""
        ) != subject_id:
            continue

        if str(
            element.get(
                "kind",
                "",
            )
            or ""
        ).lower() != "image":
            raise ValueError(
                "L'objet stable vise n'est plus une image."
            )

        return element

    raise ValueError(
        "L'image stable n'existe plus sur sa page."
    )


def _metrics(
    element: dict[str, Any],
):
    payload = element.get(
        "payload",
        {},
    )
    geometry = element.get(
        "geometry",
        {},
    )

    if not isinstance(
        payload,
        dict,
    ) or not isinstance(
        geometry,
        dict,
    ):
        raise ValueError(
            "Image sans donnees de qualite exploitables."
        )

    try:
        width_px = int(
            payload.get(
                "width_px",
                0,
            )
            or 0
        )
        height_px = int(
            payload.get(
                "height_px",
                0,
            )
            or 0
        )
        width_mm = float(
            geometry[
                "width_mm"
            ]
        )
        height_mm = float(
            geometry[
                "height_mm"
            ]
        )
    except (
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        raise ValueError(
            "Image sans donnees de qualite exploitables."
        ) from exc

    quality = effective_dpi(
        width_px=width_px,
        height_px=height_px,
        width_mm=width_mm,
        height_mm=height_mm,
    )

    return (
        payload,
        geometry,
        quality,
    )


def _record_choice(
    element: dict[str, Any],
    situation: Situation,
    choice: str,
) -> None:
    metadata = element.get(
        "metadata",
    )

    if not isinstance(
        metadata,
        dict,
    ):
        metadata = {}
        element[
            "metadata"
        ] = metadata

    decisions = metadata.setdefault(
        _IMAGE_DECISIONS_KEY,
        {},
    )

    if not isinstance(
        decisions,
        dict,
    ):
        decisions = {}
        metadata[
            _IMAGE_DECISIONS_KEY
        ] = decisions

    decisions[
        str(
            situation.kind
        )
    ] = choice


def execute_image_decision(
    book: Any,
    situation: Situation,
    decision: Decision,
) -> ImageDecisionExecution:
    """Execute Corriger / Laisser comme ca pour la qualite d'une image."""

    choice = _validate_image_decision(
        situation,
        decision,
    )

    element = _find_image(
        book,
        situation,
    )

    payload, geometry, before = _metrics(
        element
    )

    width_before = float(
        before.width_mm
    )
    height_before = float(
        before.height_mm
    )
    dpi_before = float(
        before.effective_dpi
    )

    if choice == IMAGE_CHOICE_IGNORED:
        _record_choice(
            element,
            situation,
            choice,
        )

        return ImageDecisionExecution(
            situation_id=situation.id,
            subject_id=situation.subject_id,
            choice=choice,
            changed=False,
            dpi_before=dpi_before,
            dpi_after=dpi_before,
            width_mm_before=width_before,
            height_mm_before=height_before,
            width_mm_after=width_before,
            height_mm_after=height_before,
        )

    if str(
        situation.kind
    ) != IMAGE_QUALITY_CRITICAL:
        raise ValueError(
            "Une image limitee entre 200 et 300 dpi n'a pas de "
            "correction automatique V4 validee."
        )

    if dpi_before >= float(
        MINIMUM_DPI
    ):
        raise ValueError(
            "Cette image n'est plus critique ; la Situation doit etre reanalysee."
        )

    new_width, new_height, changed = clamp_size_to_minimum_dpi(
        width_px=before.width_px,
        height_px=before.height_px,
        requested_width_mm=width_before,
        requested_height_mm=height_before,
    )

    if not changed:
        raise ValueError(
            "Le moteur V4 n'a produit aucune correction de taille."
        )

    geometry[
        "width_mm"
    ] = float(
        new_width
    )
    geometry[
        "height_mm"
    ] = float(
        new_height
    )

    after = effective_dpi(
        width_px=int(
            payload.get(
                "width_px",
                0,
            )
            or 0
        ),
        height_px=int(
            payload.get(
                "height_px",
                0,
            )
            or 0
        ),
        width_mm=float(
            geometry[
                "width_mm"
            ]
        ),
        height_mm=float(
            geometry[
                "height_mm"
            ]
        ),
    )

    if float(
        after.effective_dpi
    ) + 1e-6 < float(
        MINIMUM_DPI
    ):
        geometry[
            "width_mm"
        ] = width_before
        geometry[
            "height_mm"
        ] = height_before

        raise ValueError(
            "La correction Image n'atteint pas le minimum de 200 dpi."
        )

    _record_choice(
        element,
        situation,
        choice,
    )

    return ImageDecisionExecution(
        situation_id=situation.id,
        subject_id=situation.subject_id,
        choice=choice,
        changed=True,
        dpi_before=dpi_before,
        dpi_after=float(
            after.effective_dpi
        ),
        width_mm_before=width_before,
        height_mm_before=height_before,
        width_mm_after=float(
            geometry[
                "width_mm"
            ]
        ),
        height_mm_after=float(
            geometry[
                "height_mm"
            ]
        ),
    )


__all__ = [
    "IMAGE_CHOICE_CORRECTED",
    "IMAGE_CHOICE_IGNORED",
    "IMAGE_DECISION_CHOICES",
    "ImageDecisionExecution",
    "execute_image_decision",
    "clamp_size_to_minimum_dpi",
]