from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PageStyle:
    """
    Apparence d'une page.

    Cette classe regroupe uniquement les informations visuelles.
    Elle ne contient aucune logique de rendu.
    """

    # ------------------------------------------------------------------
    # Fond
    # ------------------------------------------------------------------

    background_color: str = "#FFFFFF"

    # ------------------------------------------------------------------
    # Bordure
    # ------------------------------------------------------------------

    border_color: str = "#BBBBBB"
    border_width: float = 1.0

    # ------------------------------------------------------------------
    # Ombre
    # ------------------------------------------------------------------

    shadow_enabled: bool = True
    shadow_color: str = "#666666"
    shadow_offset_x: float = 8.0
    shadow_offset_y: float = 8.0

    # ------------------------------------------------------------------
    # Divers
    # ------------------------------------------------------------------

    opacity: float = 1.0