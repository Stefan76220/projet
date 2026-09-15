from __future__ import annotations

"""
TomeLinea V4 — suppression sûre dans Structure.

Principes :
- une page simple est supprimée comme une unité ;
- une moitié de vraie 2P entraîne l'autre moitié ;
- les pages automatiques devenues orphelines disparaissent ;
- une page automatique partagée avec une source restante survit ;
- les règles Structure sont resynchronisées après suppression ;
- une page automatique ne se supprime jamais directement.
"""

from copy import deepcopy
from dataclasses import dataclass, fields

from src.v4.domain import BookV4, PageV4
from src.v4.structure_auto import (
    auto_page_is_protected,
    is_structural_auto_page,
    retain_auto_page,
    structure_auto_issues,
)
from src.v4.structure_pair_rules import (
    structure_pair_rule_issues,
)
from src.v4.structure_spreads import (
    split_spread,
    spread_members,
    structure_spread_issues,
)
from src.v4.structure_sync import (
    sync_structure_rules,
)


@dataclass(frozen=True, slots=True)
class StructureDeleteResult:
    deleted_page_ids: tuple[str, ...]
    deleted_base_page_ids: tuple[str, ...]
    deleted_auto_page_ids: tuple[str, ...]


def _roles(
    page: PageV4,
) -> list[dict]:

    raw = page.metadata.get(
        "automatic_roles"
    )

    if not isinstance(raw, list):
        return []

    result: list[dict] = []

    for role in raw:
        if not isinstance(role, dict):
            continue

        code = str(
            role.get("code")
            or ""
        ).strip().upper()

        source_id = str(
            role.get("source_id")
            or ""
        ).strip()

        target_type = str(
            role.get("target_type")
            or ""
        ).strip()

        if not code or not source_id:
            continue

        normalized = {
            "code": code,
            "source_id": source_id,
            "target_type": target_type,
        }

        if normalized not in result:
            result.append(normalized)

    return result


def _set_roles(
    page: PageV4,
    roles: list[dict],
) -> None:

    page.metadata[
        "automatic_roles"
    ] = [
        dict(role)
        for role in roles
    ]

    page.metadata[
        "automatic_markers"
    ] = [
        str(role["code"])
        for role in roles
    ]

    source_ids: list[str] = []

    for role in roles:
        source_id = str(
            role["source_id"]
        )

        if source_id not in source_ids:
            source_ids.append(
                source_id
            )

    page.metadata[
        "automatic_shared"
    ] = (
        len(source_ids) > 1
    )

    page.metadata[
        "source_page_id"
    ] = (
        source_ids[0]
        if len(source_ids) == 1
        else ""
    )

    requested = str(
        page.metadata.get(
            "requested_source_page_id"
        )
        or ""
    )

    if (
        requested
        and requested not in source_ids
    ):
        if len(source_ids) == 1:
            page.metadata[
                "requested_source_page_id"
            ] = source_ids[0]
        else:
            page.metadata.pop(
                "requested_source_page_id",
                None,
            )


def _base_page_ids(
    book: BookV4,
    page_id: str,
) -> tuple[str, ...]:

    page = book.pages.get(
        page_id
    )

    if page is None:
        raise KeyError(
            page_id
        )

    if is_structural_auto_page(page):
        raise ValueError(
            "Une page automatique Structure "
            "ne peut pas être supprimée directement."
        )

    if not page.spread_id:
        return (
            page.id,
        )

    members = spread_members(
        book,
        page.spread_id,
    )

    if members is None:
        raise ValueError(
            "La page appartient à une "
            "double page invalide."
        )

    left, right = members

    return (
        left.id,
        right.id,
    )


def _restore_book(
    book: BookV4,
    snapshot: BookV4,
) -> None:

    for field_info in fields(
        BookV4
    ):
        setattr(
            book,
            field_info.name,
            deepcopy(
                getattr(
                    snapshot,
                    field_info.name,
                )
            ),
        )


def delete_structure_block(
    book: BookV4,
    page_id: str,
) -> StructureDeleteResult:

    book.validate()

    snapshot = deepcopy(
        book
    )

    try:
        base_ids = (
            _base_page_ids(
                book,
                page_id,
            )
        )

        deleted_source_ids = set(
            base_ids
        )

        auto_remove_ids: set[str] = set()

        # ======================================================
        # 1 — Réduit les rôles des pages automatiques.
        #
        # Une auto partagée peut rester si elle possède encore
        # au moins une source réelle.
        # ======================================================

        for page in list(
            book.pages.values()
        ):
            if not is_structural_auto_page(
                page
            ):
                continue

            old_roles = _roles(
                page
            )

            kept_roles = [
                role
                for role in old_roles
                if role["source_id"]
                not in deleted_source_ids
            ]

            if kept_roles == old_roles:
                continue

            if kept_roles:
                _set_roles(
                    page,
                    kept_roles,
                )
            else:
                auto_remove_ids.add(
                    page.id
                )

        # ======================================================
        # 2 — Retire les références vers les autos supprimées.
        # ======================================================

        for source in book.pages.values():
            if is_structural_auto_page(
                source
            ):
                continue

            source.auto_before = [
                current_id
                for current_id
                in source.auto_before
                if current_id
                not in auto_remove_ids
            ]

            source.auto_after = [
                current_id
                for current_id
                in source.auto_after
                if current_id
                not in auto_remove_ids
            ]

        # ======================================================
        # 3 — Suppression physique des autos devenues inutiles.
        # ======================================================

        if auto_remove_ids:
            book.page_order = [
                current_id
                for current_id
                in book.page_order
                if current_id
                not in auto_remove_ids
            ]

            for current_id in (
                auto_remove_ids
            ):
                book.pages.pop(
                    current_id,
                    None,
                )

        # ======================================================
        # 4 — Suppression atomique de la ou des pages réelles.
        # ======================================================

        book.page_order = [
            current_id
            for current_id
            in book.page_order
            if current_id
            not in deleted_source_ids
        ]

        for current_id in (
            deleted_source_ids
        ):
            book.pages.pop(
                current_id,
                None,
            )

        book.validate()

        # ======================================================
        # 5 — Réconciliation complète.
        #
        # Les règles de type, 2P, AV/AP et R/V restent actives
        # pour les pages encore présentes.
        # ======================================================

        sync_structure_rules(
            book
        )

        book.validate()

        issues = (
            structure_spread_issues(
                book
            )
            + structure_auto_issues(
                book
            )
            + structure_pair_rule_issues(
                book
            )
        )

        if issues:
            raise ValueError(
                "Structure incohérente après suppression : "
                + " ; ".join(
                    issues
                )
            )

        deleted_all = (
            tuple(base_ids)
            + tuple(
                sorted(
                    auto_remove_ids
                )
            )
        )

        book.history.append(
            {
                "action": (
                    "bloc_structure_supprime"
                ),
                "requested_page_id": (
                    page_id
                ),
                "deleted_base_page_ids": (
                    list(base_ids)
                ),
                "deleted_auto_page_ids": (
                    sorted(
                        auto_remove_ids
                    )
                ),
            }
        )

        return StructureDeleteResult(
            deleted_page_ids=(
                deleted_all
            ),
            deleted_base_page_ids=(
                tuple(base_ids)
            ),
            deleted_auto_page_ids=(
                tuple(
                    sorted(
                        auto_remove_ids
                    )
                )
            ),
        )

    except Exception:
        _restore_book(
            book,
            snapshot,
        )
        raise



def delete_selected_pages(
    book: BookV4,
    page_ids,
) -> StructureDeleteResult:
    """Supprime exactement les pages éditoriales choisies.

    Contrairement à ``delete_structure_block`` (héritage V3), une moitié de
    double page n'entraîne pas automatiquement l'autre moitié : la relation 2P
    est dissociée, puis seule la sélection explicite est supprimée.

    Les pages automatiques structurelles roses ne se suppriment pas directement.
    Si une page automatique dépendante possède déjà du contenu éditorial, elle
    est retenue comme vraie page au lieu de disparaître avec sa source.
    """

    book.validate()

    wanted = {str(value) for value in page_ids}
    targets = [page_id for page_id in book.page_order if page_id in wanted]
    if not targets:
        raise ValueError("Aucune page à supprimer.")

    from src.v4.structure_covers import is_cover_face

    for page_id in targets:
        page = book.pages[page_id]
        if is_cover_face(page):
            raise ValueError(
                "Les quatre faces de couverture font partie de la structure physique du livre et ne peuvent pas être supprimées."
            )
        if is_structural_auto_page(page):
            raise ValueError(
                "Une page automatique ne se supprime pas directement. "
                "Modifiez la contrainte qui l'a créée."
            )

    snapshot = deepcopy(book)

    try:
        deleted_ids = set(targets)

        # 1. Une 2P est une relation éditoriale. La suppression d'une seule
        # moitié dissocie la paire mais ne choisit jamais de supprimer l'autre.
        spread_ids: list[str] = []
        for page_id in targets:
            spread_id = str(book.pages[page_id].spread_id or "")
            if spread_id and spread_id not in spread_ids:
                spread_ids.append(spread_id)
        for spread_id in spread_ids:
            try:
                split_spread(book, spread_id)
            except (KeyError, ValueError):
                pass

        auto_remove_ids: set[str] = set()
        retained_auto_ids: set[str] = set()

        # 2. Réduit les rôles des pages automatiques qui dépendaient des
        # pages supprimées. Les autos déjà utilisées éditorialement survivent.
        for page in list(book.pages.values()):
            if not is_structural_auto_page(page):
                continue

            old_roles = _roles(page)
            kept_roles = [
                role
                for role in old_roles
                if role["source_id"] not in deleted_ids
            ]

            if kept_roles == old_roles:
                continue

            if kept_roles:
                _set_roles(page, kept_roles)
                continue

            if auto_page_is_protected(page):
                retain_auto_page(page)
                retained_auto_ids.add(page.id)
            else:
                auto_remove_ids.add(page.id)

        # 3. Nettoie les références AV/AP vers les autos qui disparaissent.
        for source in list(book.pages.values()):
            source.auto_before = [
                current_id
                for current_id in source.auto_before
                if current_id not in auto_remove_ids
            ]
            source.auto_after = [
                current_id
                for current_id in source.auto_after
                if current_id not in auto_remove_ids
            ]

        if auto_remove_ids:
            book.page_order = [
                current_id
                for current_id in book.page_order
                if current_id not in auto_remove_ids
            ]
            for current_id in auto_remove_ids:
                book.pages.pop(current_id, None)

        # 4. Supprime exactement les UUID choisis.
        book.page_order = [
            current_id
            for current_id in book.page_order
            if current_id not in deleted_ids
        ]
        for current_id in deleted_ids:
            book.pages.pop(current_id, None)

        # 5. Nettoie uniquement la provenance des extensions d'interface.
        from src.v4.structure_editorial import (
            prune_similarity_extensions_for_deleted_pages,
        )
        prune_similarity_extensions_for_deleted_pages(book, deleted_ids)

        # 6. Le moteur reconstruit seulement ce qui reste nécessaire.
        sync_structure_rules(book)
        book.validate()

        issues = (
            structure_spread_issues(book)
            + structure_auto_issues(book)
            + structure_pair_rule_issues(book)
        )
        if issues:
            raise ValueError(
                "Structure incohérente après suppression : "
                + " ; ".join(issues)
            )

        deleted_auto = tuple(sorted(auto_remove_ids))
        deleted_all = tuple(targets) + deleted_auto

        book.history.append(
            {
                "action": "pages_supprimees_explicitement",
                "deleted_page_ids": list(targets),
                "deleted_auto_page_ids": list(deleted_auto),
                "retained_auto_page_ids": sorted(retained_auto_ids),
            }
        )

        return StructureDeleteResult(
            deleted_page_ids=deleted_all,
            deleted_base_page_ids=tuple(targets),
            deleted_auto_page_ids=deleted_auto,
        )

    except Exception:
        _restore_book(book, snapshot)
        raise
