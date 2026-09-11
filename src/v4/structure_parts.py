from __future__ import annotations

"""
TomeLinea V4 ? rattachement des op?rations Structure aux parties.

Une position physique permet de d?duire la partie cible lorsque
la destination est sans ambigu?t?.

? la fronti?re exacte entre deux parties diff?rentes, l'appelant
doit pr?ciser explicitement la partie voulue.
"""

from src.v4.domain import BookV4


def boundary_part_id(
    book: BookV4,
    index: int,
    *,
    page_order: list[str] | None = None,
    requested_part_id: str | None = None,
) -> str | None:

    order = (
        list(page_order)
        if page_order is not None
        else list(book.page_order)
    )

    if (
        index < 0
        or index > len(order)
    ):
        raise IndexError(
            "Position de partie invalide : "
            f"{index}"
        )

    requested = (
        str(requested_part_id)
        if requested_part_id is not None
        else None
    )

    if (
        requested is not None
        and requested not in book.parts
    ):
        raise KeyError(
            requested
        )

    # Une partie explicitement indiqu?e par l'interface
    # est l'autorit?.
    if requested is not None:
        return requested

    left_part = (
        book.pages[
            order[index - 1]
        ].part_id
        if index > 0
        else None
    )

    right_part = (
        book.pages[
            order[index]
        ].part_id
        if index < len(order)
        else None
    )

    # Int?rieur d'une m?me partie.
    if (
        index > 0
        and index < len(order)
        and left_part == right_part
    ):
        return left_part

    # D?but du livre : la premi?re page donne la partie.
    if index == 0:
        return right_part

    # Fin du livre : la derni?re page donne la partie.
    if index == len(order):
        return left_part

    # Fronti?re entre une zone sans partie et une partie :
    # la partie r?elle prend priorit?.
    if left_part is None:
        return right_part

    if right_part is None:
        return left_part

    # Deux parties r?elles diff?rentes :
    # l'index seul ne permet pas de savoir si l'utilisateur
    # vise la fin de gauche ou le d?but de droite.
    raise ValueError(
        "La destination se trouve exactement entre "
        "deux parties diff?rentes. "
        "Pr?cisez target_part_id."
    )
