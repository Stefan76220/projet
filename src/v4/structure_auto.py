from __future__ import annotations

"""
TomeLinea V4 — pages automatiques structurelles AV/AP.

Une page automatique :
- appartient réellement au Livre ;
- possède son propre UUID stable ;
- est créée par TomeLinea ;
- n'a pas de fausse Source auteur ;
- reste reliée explicitement à sa page source ;
- peut être placée Avant (AV) ou Après (AP).

Sur une double page :
- AV se place avant la moitié gauche ;
- AP se place après la moitié droite ;
- jamais entre les deux moitiés.
"""

from src.v4.domain import (
    BookV4,
    PageOrigin,
    PageV4,
)
from src.v4.structure_spreads import (
    spread_members,
)


AUTO_BEFORE = "before"
AUTO_AFTER = "after"

AUTO_CODE_BEFORE = "AV"
AUTO_CODE_AFTER = "AP"


def is_structural_auto_page(
    page: PageV4,
) -> bool:

    return bool(
        page.metadata.get(
            "automatic_structure",
            False,
        )
    )


def _normalize_position(
    position: str,
) -> str:

    value = str(
        position or ""
    ).strip().lower()

    if value not in {
        AUTO_BEFORE,
        AUTO_AFTER,
    }:
        raise ValueError(
            "Position automatique inconnue : "
            f"{position}"
        )

    return value


def structural_auto_source_ids(
    page: PageV4,
) -> tuple[str, ...]:

    if not is_structural_auto_page(
        page
    ):
        return ()

    result: list[str] = []

    roles = page.metadata.get(
        "automatic_roles"
    )

    if isinstance(
        roles,
        list,
    ):
        for role in roles:
            if not isinstance(
                role,
                dict,
            ):
                continue

            source_id = str(
                role.get(
                    "source_id"
                )
                or ""
            ).strip()

            if (
                source_id
                and source_id not in result
            ):
                result.append(
                    source_id
                )

    if result:
        return tuple(
            result
        )

    source_id = str(
        page.metadata.get(
            "source_page_id"
        )
        or ""
    ).strip()

    if source_id:
        return (
            source_id,
        )

    return ()


def _anchor_page(
    book: BookV4,
    source_page_id: str,
    position: str,
) -> PageV4:
    """
    Sur une 2P :
        before -> moitié gauche
        after  -> moitié droite
    """

    position = _normalize_position(
        position
    )

    source = book.pages.get(
        source_page_id
    )

    if source is None:
        raise KeyError(
            source_page_id
        )

    if is_structural_auto_page(
        source
    ):
        raise ValueError(
            "Une page automatique ne peut pas "
            "servir de source AV/AP."
        )

    if not source.spread_id:
        return source

    members = spread_members(
        book,
        source.spread_id,
    )

    if members is None:
        raise ValueError(
            "La page source appartient à une "
            "double page invalide."
        )

    left, right = members

    return (
        left
        if position == AUTO_BEFORE
        else right
    )


def _check_existing_layout(
    book: BookV4,
    anchor: PageV4,
    position: str,
) -> None:

    position = _normalize_position(
        position
    )

    anchor_index = (
        book.page_order.index(
            anchor.id
        )
    )

    if position == AUTO_BEFORE:
        ids = list(
            anchor.auto_before
        )

        if not ids:
            return

        start = (
            anchor_index
            - len(ids)
        )

        if (
            start < 0
            or book.page_order[
                start:anchor_index
            ] != ids
        ):
            raise ValueError(
                "Les pages AV existantes ne sont "
                "plus contiguës à leur source."
            )

    else:
        ids = list(
            anchor.auto_after
        )

        if not ids:
            return

        actual = book.page_order[
            anchor_index + 1:
            anchor_index + 1 + len(ids)
        ]

        if actual != ids:
            raise ValueError(
                "Les pages AP existantes ne sont "
                "plus contiguës à leur source."
            )


def add_structural_auto_page(
    book: BookV4,
    source_page_id: str,
    *,
    position: str,
    page_type: str = "Page blanche",
    title: str = "",
    is_compensation: bool = False,
) -> PageV4:
    """
    Matérialise une page AV/AP dans le Livre.

    Les listes auto_before / auto_after conservent l'ordre
    physique réel.
    """

    book.validate()

    position = _normalize_position(
        position
    )

    requested_source = (
        book.pages.get(
            source_page_id
        )
    )

    if requested_source is None:
        raise KeyError(
            source_page_id
        )

    anchor = _anchor_page(
        book,
        source_page_id,
        position,
    )

    _check_existing_layout(
        book,
        anchor,
        position,
    )

    code = (
        AUTO_CODE_BEFORE
        if position == AUTO_BEFORE
        else AUTO_CODE_AFTER
    )

    page = PageV4(
        page_type=page_type,
        title=title,
        origin=PageOrigin.TOMELINEA,
        source=None,
        part_id=anchor.part_id,
        is_compensation=(
            is_compensation
        ),
    )

    page.metadata[
        "creation_kind"
    ] = "automatic_structure"

    page.metadata[
        "automatic_structure"
    ] = True

    page.metadata[
        "automatic_position"
    ] = position

    page.metadata[
        "source_page_id"
    ] = anchor.id

    page.metadata[
        "requested_source_page_id"
    ] = requested_source.id

    page.metadata[
        "automatic_roles"
    ] = [
        {
            "code": code,
            "source_id": anchor.id,
            "target_type": page_type,
        }
    ]

    anchor_index = (
        book.page_order.index(
            anchor.id
        )
    )

    if position == AUTO_BEFORE:
        # Les anciennes AV restent plus éloignées ;
        # la nouvelle devient la plus proche de la source.
        insert_index = (
            anchor_index
        )

        book.add_page(
            page,
            index=insert_index,
        )

        anchor.auto_before.append(
            page.id
        )

    else:
        # Les AP sont mémorisées de la plus proche
        # à la plus éloignée de la source.
        insert_index = (
            anchor_index
            + 1
            + len(
                anchor.auto_after
            )
        )

        book.add_page(
            page,
            index=insert_index,
        )

        anchor.auto_after.append(
            page.id
        )

    book.history.append(
        {
            "action": (
                "page_automatique_structure_ajoutee"
            ),
            "page_id": page.id,
            "source_page_id": anchor.id,
            "requested_source_page_id": (
                requested_source.id
            ),
            "position": position,
            "code": code,
        }
    )

    book.validate()

    issues = structure_auto_issues(
        book
    )

    if issues:
        raise ValueError(
            "Structure AV/AP incohérente : "
            + " ; ".join(
                issues
            )
        )

    return page


def structure_auto_issues(
    book: BookV4,
) -> list[str]:

    issues: list[str] = []

    references: dict[
        str,
        list[
            tuple[str, str]
        ],
    ] = {}

    for source in book.pages.values():
        if is_structural_auto_page(
            source
        ):
            if (
                source.auto_before
                or source.auto_after
            ):
                issues.append(
                    "page automatique portant elle-même "
                    f"AV/AP : {source.id}"
                )

            if source.spread_id:
                issues.append(
                    "page automatique appartenant "
                    f"à une 2P : {source.id}"
                )

            continue

        for position, ids in (
            (
                AUTO_BEFORE,
                source.auto_before,
            ),
            (
                AUTO_AFTER,
                source.auto_after,
            ),
        ):
            if len(ids) != len(
                set(ids)
            ):
                issues.append(
                    f"AV/AP dupliquée sur {source.id}"
                )

            for page_id in ids:
                references.setdefault(
                    page_id,
                    [],
                ).append(
                    (
                        source.id,
                        position,
                    )
                )

                page = book.pages.get(
                    page_id
                )

                if page is None:
                    issues.append(
                        "page automatique inconnue : "
                        f"{page_id}"
                    )
                    continue

                if not is_structural_auto_page(
                    page
                ):
                    issues.append(
                        "page AV/AP non automatique : "
                        f"{page_id}"
                    )

                if (
                    page.part_id
                    != source.part_id
                ):
                    issues.append(
                        "page AV/AP dans une autre partie : "
                        f"{page_id}"
                    )

            if not ids:
                continue

            try:
                source_index = (
                    book.page_order.index(
                        source.id
                    )
                )
            except ValueError:
                issues.append(
                    "source AV/AP absente de l'ordre : "
                    f"{source.id}"
                )
                continue

            if position == AUTO_BEFORE:
                start = (
                    source_index
                    - len(ids)
                )

                actual = (
                    book.page_order[
                        max(
                            0,
                            start,
                        ):
                        source_index
                    ]
                    if start >= 0
                    else []
                )

                if actual != list(
                    ids
                ):
                    issues.append(
                        "AV non contiguë à la source : "
                        f"{source.id}"
                    )

            else:
                actual = (
                    book.page_order[
                        source_index + 1:
                        source_index + 1
                        + len(ids)
                    ]
                )

                if actual != list(
                    ids
                ):
                    issues.append(
                        "AP non contiguë à la source : "
                        f"{source.id}"
                    )

    for page in book.pages.values():
        if not is_structural_auto_page(
            page
        ):
            continue

        if page.id not in references:
            issues.append(
                "page automatique orpheline : "
                f"{page.id}"
            )

        source_ids = (
            structural_auto_source_ids(
                page
            )
        )

        if not source_ids:
            issues.append(
                "page automatique sans source : "
                f"{page.id}"
            )

    return issues
