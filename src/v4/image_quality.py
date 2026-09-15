from __future__ import annotations

from dataclasses import dataclass


TARGET_DPI = 300.0
MINIMUM_DPI = 200.0


@dataclass(frozen=True)
class ImageQuality:
    width_px: int
    height_px: int
    width_mm: float
    height_mm: float

    dpi_x: float
    dpi_y: float
    effective_dpi: float

    status: str

    max_width_mm: float
    max_height_mm: float

    target_width_mm: float
    target_height_mm: float


def _positive_float(
    value,
    name: str,
) -> float:

    result = float(
        value
    )

    if result <= 0:
        raise ValueError(
            f"{name} doit etre positif."
        )

    return result


def _positive_int(
    value,
    name: str,
) -> int:

    result = int(
        value
    )

    if result <= 0:
        raise ValueError(
            f"{name} doit etre positif."
        )

    return result


def effective_dpi(
    *,
    width_px,
    height_px,
    width_mm,
    height_mm,
) -> ImageQuality:

    width_px = _positive_int(
        width_px,
        "width_px",
    )

    height_px = _positive_int(
        height_px,
        "height_px",
    )

    width_mm = _positive_float(
        width_mm,
        "width_mm",
    )

    height_mm = _positive_float(
        height_mm,
        "height_mm",
    )

    width_in = (
        width_mm
        / 25.4
    )

    height_in = (
        height_mm
        / 25.4
    )

    dpi_x = (
        width_px
        / width_in
    )

    dpi_y = (
        height_px
        / height_in
    )

    effective = min(
        dpi_x,
        dpi_y,
    )

    if effective >= TARGET_DPI:

        status = "conforme"

    elif effective >= MINIMUM_DPI:

        status = "limited"

    else:

        status = "critical"

    # Taille physique maximale permettant
    # de rester au-dessus du minimum absolu.
    max_width_mm = (
        width_px
        / MINIMUM_DPI
        * 25.4
    )

    max_height_mm = (
        height_px
        / MINIMUM_DPI
        * 25.4
    )

    # Taille physique correspondant à la
    # cible de qualité de 300 dpi.
    target_width_mm = (
        width_px
        / TARGET_DPI
        * 25.4
    )

    target_height_mm = (
        height_px
        / TARGET_DPI
        * 25.4
    )

    return ImageQuality(
        width_px=width_px,
        height_px=height_px,

        width_mm=width_mm,
        height_mm=height_mm,

        dpi_x=dpi_x,
        dpi_y=dpi_y,
        effective_dpi=effective,

        status=status,

        max_width_mm=max_width_mm,
        max_height_mm=max_height_mm,

        target_width_mm=target_width_mm,
        target_height_mm=target_height_mm,
    )


def clamp_size_to_minimum_dpi(
    *,
    width_px,
    height_px,
    requested_width_mm,
    requested_height_mm,
) -> tuple[float, float, bool]:

    quality = effective_dpi(
        width_px=width_px,
        height_px=height_px,
        width_mm=requested_width_mm,
        height_mm=requested_height_mm,
    )

    if (
        quality.effective_dpi
        >= MINIMUM_DPI
    ):

        return (
            float(
                requested_width_mm
            ),
            float(
                requested_height_mm
            ),
            False,
        )

    scale = min(
        quality.max_width_mm
        / float(
            requested_width_mm
        ),
        quality.max_height_mm
        / float(
            requested_height_mm
        ),
    )

    scale = min(
        1.0,
        scale,
    )

    return (
        float(
            requested_width_mm
        )
        * scale,

        float(
            requested_height_mm
        )
        * scale,

        True,
    )
