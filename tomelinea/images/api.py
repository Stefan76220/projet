"""Catalogue V5 des Situations de qualite d'impression des images.

Le calcul reste celui de la V4 :
- 300 dpi et plus : conforme ;
- 200 a moins de 300 dpi : limitee ;
- moins de 200 dpi : non conforme.

La V5 ne corrige ni ne redimensionne automatiquement une image dans ce module.
Elle transforme seulement les constats V4 ``limited`` et ``critical`` en
Situations factuelles pour le Survol.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.v4.image_quality import (
    MINIMUM_DPI,
    TARGET_DPI,
    ImageQuality,
    effective_dpi,
)

from tomelinea.rules import Situation


IMAGE_QUALITY_LIMITED = "image_quality_limited"
IMAGE_QUALITY_CRITICAL = "image_quality_critical"

IMAGE_QUALITY_SITUATION_KINDS = (
    IMAGE_QUALITY_LIMITED,
    IMAGE_QUALITY_CRITICAL,
)


@dataclass(frozen=True, slots=True)
class ImageQualityAudit:
    total: int
    conforme: int
    limited: int
    critical: int
    issues: tuple[dict[str, Any], ...]


def _image_quality(
    element: dict[str, Any],
) -> ImageQuality | None:
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
        return None

    try:
        return effective_dpi(
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
    except (
        KeyError,
        TypeError,
        ValueError,
    ):
        return None


def audit_book_images(
    book: Any,
) -> ImageQualityAudit:
    """Equivalent pur du controle V4 auparavant porte par l'interface."""

    total = 0
    conforme = 0
    limited = 0
    critical = 0
    issues: list[dict[str, Any]] = []

    if book is None:
        return ImageQualityAudit(
            total=0,
            conforme=0,
            limited=0,
            critical=0,
            issues=(),
        )

    for page_index, page in enumerate(
        book.ordered_pages(),
        start=1,
    ):
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
                    "kind",
                    "",
                )
                or ""
            ).lower() != "image":
                continue

            quality = _image_quality(
                element
            )

            if quality is None:
                continue

            total += 1

            if quality.status == "conforme":
                conforme += 1
                continue

            if quality.status == "limited":
                limited += 1
            elif quality.status == "critical":
                critical += 1
            else:
                continue

            source_page = None
            source = getattr(
                page,
                "source",
                None,
            )

            if source is not None:
                source_page = getattr(
                    source,
                    "source_page",
                    None,
                )

            issues.append(
                {
                    "page_id": str(
                        page.id
                    ),
                    "element_id": str(
                        element.get(
                            "id",
                            "",
                        )
                        or ""
                    ),
                    "page_number": page_index,
                    "source_page": source_page,
                    "page_title": (
                        page.title
                        or page.page_type
                        or f"Page {page_index}"
                    ),
                    "status": quality.status,
                    "dpi": float(
                        quality.effective_dpi
                    ),
                    "width_px": quality.width_px,
                    "height_px": quality.height_px,
                    "width_mm": quality.width_mm,
                    "height_mm": quality.height_mm,
                    "max_width_mm": quality.max_width_mm,
                    "max_height_mm": quality.max_height_mm,
                }
            )

    return ImageQualityAudit(
        total=total,
        conforme=conforme,
        limited=limited,
        critical=critical,
        issues=tuple(
            issues
        ),
    )


def image_quality_issue_to_situation(
    issue: dict[str, Any],
) -> Situation:
    status = str(
        issue.get(
            "status",
            "",
        )
        or ""
    ).strip().lower()

    if status == "limited":
        kind = IMAGE_QUALITY_LIMITED
        title = "Cette image a une qualité limitée pour l'impression"
        why = (
            "Sa résolution effective est inférieure à la cible de 300 dpi, "
            "mais reste au-dessus du minimum de 200 dpi."
        )
        proposal = (
            "Conserver cette taille en connaissance de cause, réduire l'image "
            "ou utiliser un fichier de meilleure définition."
        )
    elif status == "critical":
        kind = IMAGE_QUALITY_CRITICAL
        title = "Cette image n'est pas conforme pour l'impression"
        why = (
            "Sa résolution effective est inférieure au minimum de 200 dpi."
        )
        proposal = (
            "Réduire l'image jusqu'à une taille compatible ou utiliser "
            "un fichier de meilleure définition."
        )
    else:
        raise ValueError(
            "Seules les images limited ou critical produisent une Situation."
        )

    page_id = str(
        issue.get(
            "page_id",
            "",
        )
        or ""
    ).strip()
    element_id = str(
        issue.get(
            "element_id",
            "",
        )
        or ""
    ).strip()

    if not page_id:
        raise ValueError(
            "Controle Image sans page stable."
        )

    if not element_id:
        raise ValueError(
            "Controle Image sans element stable."
        )

    return Situation(
        domain="image",
        kind=kind,
        subject_id=element_id,
        page_id=page_id,
        facts={
            "classification": "print_quality",
            "title": title,
            "technical_term": "résolution d'impression",
            "why": why,
            "proposal": proposal,
            "status": status,
            "dpi": float(
                issue.get(
                    "dpi",
                    0.0,
                )
                or 0.0
            ),
            "target_dpi": float(
                TARGET_DPI
            ),
            "minimum_dpi": float(
                MINIMUM_DPI
            ),
            "width_px": int(
                issue.get(
                    "width_px",
                    0,
                )
                or 0
            ),
            "height_px": int(
                issue.get(
                    "height_px",
                    0,
                )
                or 0
            ),
            "width_mm": float(
                issue.get(
                    "width_mm",
                    0.0,
                )
                or 0.0
            ),
            "height_mm": float(
                issue.get(
                    "height_mm",
                    0.0,
                )
                or 0.0
            ),
            "max_width_mm": float(
                issue.get(
                    "max_width_mm",
                    0.0,
                )
                or 0.0
            ),
            "max_height_mm": float(
                issue.get(
                    "max_height_mm",
                    0.0,
                )
                or 0.0
            ),
            "page_number": issue.get(
                "page_number"
            ),
            "source_page": issue.get(
                "source_page"
            ),
            "page_title": str(
                issue.get(
                    "page_title",
                    "",
                )
                or ""
            ),
        },
    )


def image_quality_situations(
    book: Any,
) -> tuple[Situation, ...]:
    audit = audit_book_images(
        book
    )

    return tuple(
        image_quality_issue_to_situation(
            issue
        )
        for issue in audit.issues
    )


__all__ = [
    "TARGET_DPI",
    "MINIMUM_DPI",
    "ImageQuality",
    "effective_dpi",
    "IMAGE_QUALITY_LIMITED",
    "IMAGE_QUALITY_CRITICAL",
    "IMAGE_QUALITY_SITUATION_KINDS",
    "ImageQualityAudit",
    "audit_book_images",
    "image_quality_issue_to_situation",
    "image_quality_situations",
]