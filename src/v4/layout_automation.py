from __future__ import annotations

"""Automatisations de mise en page TomeLinea V4.

Les fonctions de ce module réalisent des actions collectives explicites sur
le Livre. Elles n'ajoutent aucune information d'interface et restent
transactionnelles lorsqu'elles sont appelées via WorkspaceSessionV4.execute().
"""

from src.v4.composition import MARGINS, frame_bounds, update_element_geometry
from src.v4.domain import BookV4
from src.v4.structure_covers import is_cover_face


def center_margin_images_horizontally(book: BookV4) -> int:
    """Centre horizontalement les images rattachées au référentiel Marges.

    - Les quatre faces de couverture sont laissées intactes.
    - Les images Page / Fond perdu sont laissées intactes : leur position peut
      être volontairement liée au bord fini ou au fond perdu.
    - La largeur et la hauteur de l'image ne changent jamais.

    Retourne le nombre d'images réellement déplacées.
    """

    changed = 0

    for page in book.ordered_pages():
        if is_cover_face(page):
            continue

        left, _top, usable_width, _usable_height = frame_bounds(
            book,
            page.id,
            MARGINS,
        )

        for element in page.content:
            if not isinstance(element, dict):
                continue
            if str(element.get("kind", "")).strip().lower() != "image":
                continue
            if str(element.get("reference_frame", MARGINS)).strip().lower() != MARGINS:
                continue

            geometry = element.get("geometry", {})
            if not isinstance(geometry, dict):
                continue

            try:
                current_x = float(geometry.get("x_mm", 0.0) or 0.0)
                width = float(geometry.get("width_mm", 0.0) or 0.0)
            except (TypeError, ValueError):
                continue

            if width <= 0:
                continue

            target_x = float(left) + (float(usable_width) - width) / 2.0
            if abs(target_x - current_x) <= 0.01:
                continue

            element_id = str(element.get("id", "") or "")
            if not element_id:
                continue

            update_element_geometry(
                book,
                page.id,
                element_id,
                x_mm=target_x,
            )
            changed += 1

    return changed
