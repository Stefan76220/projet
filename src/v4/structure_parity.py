from __future__ import annotations

"""
TomeLinea V4 — parité physique, Recto/Verso et compensation.

Principes :
- première page physique comptée = Recto ;
- une règle R/V ne change jamais l'identité d'une page ;
- une page automatique AV/AP peut déjà satisfaire la parité ;
- sinon TomeLinea ajoute une page blanche de compensation ;
- une même page automatique peut porter plusieurs rôles ;
- une vraie 2P impose :
      gauche = Verso
      droite = Recto
- les règles R/V mémorisées sur les deux moitiés d'une 2P
  sont suspendues tant que la paire existe.
"""

from src.v4.domain import (
    BookV4,
    PageOrigin,
    PageV4,
)
from src.v4.structure_auto import (
    is_structural_auto_page,
    structure_auto_issues,
)
from src.v4.structure_spreads import (
    SPREAD_LEFT,
    spread_members,
    structure_spread_issues,
)


RECTO = "recto"
VERSO = "verso"

PARITY_ROLES = {
    "R",
    "V",
    "DP",
}


def counts_for_parity(
    page: PageV4,
) -> bool:
    """
    Prépare également le futur cas des couvertures
    qui pourront être exclues explicitement du calcul.
    """

    return not bool(
        page.metadata.get(
            "physical_parity_exempt",
            False,
        )
    )


def physical_side(
    book: BookV4,
    page_id: str,
) -> str | None:

    page = book.pages.get(
        page_id
    )

    if page is None:
        raise KeyError(
            page_id
        )

    if not counts_for_parity(
        page
    ):
        return None

    try:
        index = book.page_order.index(
            page_id
        )
    except ValueError as exc:
        raise ValueError(
            f"Page absente de l'ordre : {page_id}"
        ) from exc

    physical_index = 0

    for current_id in book.page_order[:index]:
        current = book.pages[
            current_id
        ]

        if counts_for_parity(
            current
        ):
            physical_index += 1

    return (
        RECTO
        if physical_index % 2 == 0
        else VERSO
    )


def required_recto_verso(
    page: PageV4,
) -> str | None:

    value = str(
        page.recto_verso or ""
    ).strip().lower()

    if value in {
        RECTO,
        VERSO,
    }:
        return value

    return None


def _normalized_roles(
    page: PageV4,
) -> list[dict]:

    raw = page.metadata.get(
        "automatic_roles"
    )

    result: list[dict] = []

    if not isinstance(
        raw,
        list,
    ):
        return result

    seen: set[
        tuple[str, str, str]
    ] = set()

    for role in raw:
        if not isinstance(
            role,
            dict,
        ):
            continue

        code = str(
            role.get(
                "code"
            )
            or ""
        ).strip().upper()

        source_id = str(
            role.get(
                "source_id"
            )
            or ""
        ).strip()

        target_type = str(
            role.get(
                "target_type"
            )
            or ""
        ).strip()

        if not code or not source_id:
            continue

        key = (
            code,
            source_id,
            target_type,
        )

        if key in seen:
            continue

        seen.add(
            key
        )

        result.append(
            {
                "code": code,
                "source_id": source_id,
                "target_type": target_type,
            }
        )

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
        str(
            role.get(
                "code"
            )
            or ""
        )
        for role in roles
    ]


def _add_role(
    page: PageV4,
    *,
    code: str,
    source_id: str,
    target_type: str = "Page blanche",
) -> None:

    roles = _normalized_roles(
        page
    )

    role = {
        "code": str(
            code
        ).upper(),
        "source_id": source_id,
        "target_type": target_type,
    }

    if role not in roles:
        roles.append(
            role
        )

    _set_roles(
        page,
        roles,
    )


def _strip_old_parity_state(
    book: BookV4,
) -> dict[
    tuple[str, str],
    PageV4,
]:
    """
    Retire les anciens rôles R/V/DP avant recalcul.

    Les pages AV/AP restent.
    Les pages qui ne portaient qu'une correction sont retirées
    temporairement mais conservées comme candidates afin de
    réutiliser leur UUID si la même correction reste nécessaire.
    """

    reusable: dict[
        tuple[str, str],
        PageV4,
    ] = {}

    remove_ids: set[str] = set()

    for page in list(
        book.pages.values()
    ):
        if not is_structural_auto_page(
            page
        ):
            continue

        roles = _normalized_roles(
            page
        )

        parity = [
            role
            for role in roles
            if role["code"]
            in PARITY_ROLES
        ]

        structural = [
            role
            for role in roles
            if role["code"]
            not in PARITY_ROLES
        ]

        for role in parity:
            key = (
                role["code"],
                role["source_id"],
            )

            reusable.setdefault(
                key,
                page,
            )

        if structural:
            _set_roles(
                page,
                structural,
            )

        elif parity:
            remove_ids.add(
                page.id
            )

    if remove_ids:
        for source in book.pages.values():
            source.auto_before = [
                page_id
                for page_id
                in source.auto_before
                if page_id not in remove_ids
            ]

            source.auto_after = [
                page_id
                for page_id
                in source.auto_after
                if page_id not in remove_ids
            ]

        book.page_order = [
            page_id
            for page_id in book.page_order
            if page_id not in remove_ids
        ]

        for page_id in remove_ids:
            book.pages.pop(
                page_id,
                None,
            )

    book.validate()

    return reusable


def _previous_associated_auto(
    book: BookV4,
    source: PageV4,
) -> PageV4 | None:
    """
    Retourne uniquement la page automatique immédiatement placée
    avant la source et réellement attachée à son auto_before.
    """

    try:
        index = book.page_order.index(
            source.id
        )
    except ValueError:
        return None

    if index <= 0:
        return None

    previous_id = book.page_order[
        index - 1
    ]

    if previous_id not in source.auto_before:
        return None

    previous = book.pages.get(
        previous_id
    )

    if (
        previous is None
        or not is_structural_auto_page(
            previous
        )
    ):
        return None

    return previous


def _insert_compensation(
    book: BookV4,
    source: PageV4,
    *,
    code: str,
    reusable: dict[
        tuple[str, str],
        PageV4,
    ],
) -> PageV4:

    key = (
        code,
        source.id,
    )

    page = reusable.pop(
        key,
        None,
    )

    if page is None:
        page = PageV4(
            page_type="Page blanche",
            title="",
            origin=PageOrigin.TOMELINEA,
            source=None,
            part_id=source.part_id,
            is_compensation=True,
        )

    page.part_id = (
        source.part_id
    )

    page.is_compensation = (
        True
    )

    page.spread_id = None
    page.spread_side = None

    page.auto_before = []
    page.auto_after = []

    page.metadata[
        "creation_kind"
    ] = "automatic_structure"

    page.metadata[
        "automatic_structure"
    ] = True

    page.metadata[
        "automatic_kind"
    ] = "parity_correction"

    page.metadata[
        "automatic_position"
    ] = "before"

    page.metadata[
        "source_page_id"
    ] = source.id

    _set_roles(
        page,
        [
            {
                "code": code,
                "source_id": source.id,
                "target_type": "Page blanche",
            }
        ],
    )

    source_index = (
        book.page_order.index(
            source.id
        )
    )

    book.add_page(
        page,
        index=source_index,
    )

    source.auto_before.append(
        page.id
    )

    book.history.append(
        {
            "action": (
                "compensation_parite_ajoutee"
            ),
            "page_id": page.id,
            "source_page_id": (
                source.id
            ),
            "code": code,
        }
    )

    return page


def _satisfy_constraint(
    book: BookV4,
    source: PageV4,
    *,
    required_side: str,
    code: str,
    reusable: dict[
        tuple[str, str],
        PageV4,
    ],
) -> PageV4 | None:

    actual = physical_side(
        book,
        source.id,
    )

    if actual == required_side:
        previous = (
            _previous_associated_auto(
                book,
                source,
            )
        )

        if previous is not None:
            _add_role(
                previous,
                code=code,
                source_id=source.id,
            )

        return None

    correction = (
        _insert_compensation(
            book,
            source,
            code=code,
            reusable=reusable,
        )
    )

    if physical_side(
        book,
        source.id,
    ) != required_side:
        raise RuntimeError(
            "La compensation n'a pas corrigé "
            "la parité attendue."
        )

    return correction


def sync_structure_parity(
    book: BookV4,
) -> int:
    """
    Réconcilie toute la parité du Livre.

    Retourne le nombre de pages de compensation réellement
    nécessaires après recalcul.
    """

    book.validate()

    spread_issues = (
        structure_spread_issues(
            book
        )
    )

    if spread_issues:
        raise ValueError(
            "Impossible de calculer la parité : "
            + " ; ".join(
                spread_issues
            )
        )

    reusable = (
        _strip_old_parity_state(
            book
        )
    )

    base_ids = [
        page_id
        for page_id in book.page_order
        if not is_structural_auto_page(
            book.pages[
                page_id
            ]
        )
    ]

    processed_spreads: set[str] = set()

    compensation_count = 0

    for page_id in base_ids:
        page = book.pages[
            page_id
        ]

        if page.spread_id:
            if (
                page.spread_id
                in processed_spreads
            ):
                continue

            members = spread_members(
                book,
                page.spread_id,
            )

            if members is None:
                raise ValueError(
                    "Double page invalide pendant "
                    "le calcul de parité."
                )

            left, right = members

            processed_spreads.add(
                page.spread_id
            )

            # Une vraie 2P impose sa propre parité.
            # Les valeurs recto_verso mémorisées sur ses pages
            # ne sont volontairement pas modifiées.
            correction = (
                _satisfy_constraint(
                    book,
                    left,
                    required_side=VERSO,
                    code="DP",
                    reusable=reusable,
                )
            )

            if correction is not None:
                compensation_count += 1

            if physical_side(
                book,
                left.id,
            ) != VERSO:
                raise RuntimeError(
                    "La moitié gauche de la 2P "
                    "n'est pas Verso."
                )

            if physical_side(
                book,
                right.id,
            ) != RECTO:
                raise RuntimeError(
                    "La moitié droite de la 2P "
                    "n'est pas Recto."
                )

            continue

        required = (
            required_recto_verso(
                page
            )
        )

        if required is None:
            continue

        code = (
            "R"
            if required == RECTO
            else "V"
        )

        correction = (
            _satisfy_constraint(
                book,
                page,
                required_side=required,
                code=code,
                reusable=reusable,
            )
        )

        if correction is not None:
            compensation_count += 1

    book.validate()

    issues = (
        structure_spread_issues(
            book
        )
        + structure_auto_issues(
            book
        )
    )

    if issues:
        raise ValueError(
            "Structure incohérente après "
            "calcul de parité : "
            + " ; ".join(
                issues
            )
        )

    book.history.append(
        {
            "action": (
                "parite_structure_recalculee"
            ),
            "compensations": (
                compensation_count
            ),
        }
    )

    return compensation_count
