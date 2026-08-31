from __future__ import annotations

"""
TomeLinea V4 — synchronisation complète des règles Structure.

Chaîne :
    règles locales / étendues
        ->
    matérialisation AV/AP
        ->
    calcul physique Recto/Verso
        ->
    compensation éventuelle

Principes :
- BookV4 reste l'unique autorité ;
- les pages principales ne sont jamais recréées ;
- une page AV/AP conserve son UUID lorsque sa relation
  structurelle existe toujours ;
- une page automatique devenue inutile disparaît ;
- une page automatique peut porter plusieurs rôles compatibles ;
- AP à gauche et AV à droite peuvent partager une même page
  lorsque leur type cible est identique ;
- une vraie 2P est traitée comme un bloc physique unique.
"""

from dataclasses import dataclass

from src.v4.domain import (
    BookV4,
    PageOrigin,
    PageV4,
)
from src.v4.structure_auto import (
    is_structural_auto_page,
    structure_auto_issues,
)
from src.v4.structure_parity import (
    sync_structure_parity,
)
from src.v4.structure_rules import (
    AFTER,
    BEFORE,
    effective_page_auto_rule,
    effective_recto_verso_rule,
    structure_rule_issues,
)
from src.v4.structure_spreads import (
    SPREAD_LEFT,
    SPREAD_RIGHT,
    structure_spread_issues,
)


@dataclass(frozen=True, slots=True)
class StructureSyncResult:
    reused_auto_pages: int
    created_auto_pages: int
    removed_auto_pages: int
    compensation_pages: int


@dataclass(frozen=True, slots=True)
class _Unit:
    page_ids: tuple[str, ...]

    @property
    def left_page_id(self) -> str:
        return self.page_ids[0]

    @property
    def right_page_id(self) -> str:
        return self.page_ids[-1]


@dataclass(frozen=True, slots=True)
class _DesiredAuto:
    roles: tuple[
        tuple[str, str, str],
        ...
    ]
    part_id: str | None

    @property
    def target_type(self) -> str:
        if not self.roles:
            return "Page blanche"

        value = self.roles[0][2]

        return (
            value
            if value
            else "Page blanche"
        )


# ==============================================================
# Rôles
# ==============================================================

def _roles(
    page: PageV4,
) -> list[dict]:

    raw = page.metadata.get(
        "automatic_roles"
    )

    if not isinstance(
        raw,
        list,
    ):
        return []

    result: list[dict] = []
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


def _relation_keys(
    page: PageV4,
) -> set[
    tuple[str, str]
]:

    return {
        (
            str(role["code"]),
            str(role["source_id"]),
        )
        for role in _roles(page)
        if role["code"] in {
            "AV",
            "AP",
        }
    }


def _parity_roles(
    page: PageV4,
) -> list[dict]:

    return [
        role
        for role in _roles(page)
        if role["code"] in {
            "R",
            "V",
            "DP",
        }
    ]


def _set_roles(
    page: PageV4,
    roles: tuple[
        tuple[str, str, str],
        ...
    ],
) -> None:

    normalized = [
        {
            "code": code,
            "source_id": source_id,
            "target_type": target_type,
        }
        for (
            code,
            source_id,
            target_type,
        ) in roles
    ]

    page.metadata[
        "automatic_roles"
    ] = normalized

    page.metadata[
        "automatic_markers"
    ] = [
        code
        for (
            code,
            _source_id,
            _target_type,
        ) in roles
    ]

    source_ids: list[str] = []

    for (
        _code,
        source_id,
        _target_type,
    ) in roles:
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


# ==============================================================
# Unités physiques source / 2P
# ==============================================================

def _base_order(
    book: BookV4,
) -> list[str]:

    return [
        page_id
        for page_id in book.page_order
        if not is_structural_auto_page(
            book.pages[page_id]
        )
    ]


def _units(
    book: BookV4,
    base_order: list[str],
) -> list[_Unit]:

    result: list[_Unit] = []
    consumed: set[str] = set()

    positions = {
        page_id: index
        for index, page_id
        in enumerate(base_order)
    }

    for page_id in base_order:
        if page_id in consumed:
            continue

        page = book.pages[
            page_id
        ]

        if not page.spread_id:
            result.append(
                _Unit(
                    page_ids=(
                        page.id,
                    )
                )
            )

            consumed.add(
                page.id
            )
            continue

        members = [
            candidate
            for candidate in book.pages.values()
            if (
                not is_structural_auto_page(
                    candidate
                )
                and candidate.spread_id
                == page.spread_id
            )
        ]

        if len(members) != 2:
            raise ValueError(
                "Double page invalide pendant "
                "la synchronisation Structure."
            )

        left = next(
            (
                candidate
                for candidate in members
                if candidate.spread_side
                == SPREAD_LEFT
            ),
            None,
        )

        right = next(
            (
                candidate
                for candidate in members
                if candidate.spread_side
                == SPREAD_RIGHT
            ),
            None,
        )

        if left is None or right is None:
            raise ValueError(
                "Double page sans côtés "
                "gauche/droite valides."
            )

        if (
            positions.get(right.id)
            != positions.get(left.id, -2) + 1
        ):
            raise ValueError(
                "Les deux moitiés de la 2P "
                "ne sont pas contiguës."
            )

        result.append(
            _Unit(
                page_ids=(
                    left.id,
                    right.id,
                )
            )
        )

        consumed.update(
            {
                left.id,
                right.id,
            }
        )

    return result


# ==============================================================
# Demandes AV/AP
# ==============================================================

def _unit_before_roles(
    book: BookV4,
    unit: _Unit,
) -> list[
    tuple[str, str, str]
]:

    anchor_id = (
        unit.left_page_id
    )

    result: list[
        tuple[str, str, str]
    ] = []

    for requested_id in unit.page_ids:
        target = (
            effective_page_auto_rule(
                book,
                requested_id,
                BEFORE,
            )
        )

        if not target:
            continue

        role = (
            "AV",
            anchor_id,
            target,
        )

        if role not in result:
            result.append(
                role
            )

    return result


def _unit_after_roles(
    book: BookV4,
    unit: _Unit,
) -> list[
    tuple[str, str, str]
]:

    anchor_id = (
        unit.right_page_id
    )

    result: list[
        tuple[str, str, str]
    ] = []

    for requested_id in unit.page_ids:
        target = (
            effective_page_auto_rule(
                book,
                requested_id,
                AFTER,
            )
        )

        if not target:
            continue

        role = (
            "AP",
            anchor_id,
            target,
        )

        if role not in result:
            result.append(
                role
            )

    return result


def _bucket_roles(
    roles: list[
        tuple[str, str, str]
    ],
    *,
    part_id: str | None,
) -> list[_DesiredAuto]:
    """
    Les rôles sont fournis dans l'ordre physique :
        AP venant de gauche
        puis AV venant de droite.

    Deux rôles consécutifs visant le même type peuvent partager
    une seule page automatique.
    """

    if not roles:
        return []

    result: list[
        _DesiredAuto
    ] = []

    current: list[
        tuple[str, str, str]
    ] = []

    current_type = ""

    for role in roles:
        target_type = (
            role[2]
            or "Page blanche"
        )

        if (
            current
            and target_type
            != current_type
        ):
            result.append(
                _DesiredAuto(
                    roles=tuple(
                        current
                    ),
                    part_id=part_id,
                )
            )

            current = []

        current.append(
            role
        )

        current_type = (
            target_type
        )

    if current:
        result.append(
            _DesiredAuto(
                roles=tuple(
                    current
                ),
                part_id=part_id,
            )
        )

    return result


def _desired_slots(
    book: BookV4,
    units: list[_Unit],
) -> list[
    list[_DesiredAuto]
]:
    """
    N unités donnent N+1 frontières.
    """

    slots: list[
        list[_DesiredAuto]
    ] = [
        []
        for _ in range(
            len(units) + 1
        )
    ]

    for index in range(
        len(slots)
    ):
        roles: list[
            tuple[str, str, str]
        ] = []

        left_unit = (
            units[index - 1]
            if index > 0
            else None
        )

        right_unit = (
            units[index]
            if index < len(units)
            else None
        )

        if left_unit is not None:
            roles.extend(
                _unit_after_roles(
                    book,
                    left_unit,
                )
            )

        if right_unit is not None:
            roles.extend(
                _unit_before_roles(
                    book,
                    right_unit,
                )
            )

        part_id: str | None = None

        # Même choix que le moteur V3 aux frontières :
        # la partie située à droite prend priorité.
        if right_unit is not None:
            part_id = book.pages[
                right_unit.left_page_id
            ].part_id

        elif left_unit is not None:
            part_id = book.pages[
                left_unit.right_page_id
            ].part_id

        slots[index] = (
            _bucket_roles(
                roles,
                part_id=part_id,
            )
        )

    return slots


# ==============================================================
# Réutilisation des UUID
# ==============================================================

def _candidate_score(
    page: PageV4,
    desired: _DesiredAuto,
) -> int:

    old_relations = (
        _relation_keys(
            page
        )
    )

    wanted_relations = {
        (
            code,
            source_id,
        )
        for (
            code,
            source_id,
            _target_type,
        ) in desired.roles
    }

    overlap = len(
        old_relations
        & wanted_relations
    )

    if overlap == 0:
        return 0

    score = (
        overlap * 100
    )

    if (
        str(page.page_type)
        == desired.target_type
    ):
        score += 10

    return score


def _prepare_auto(
    page: PageV4,
    desired: _DesiredAuto,
) -> None:

    page.page_type = (
        desired.target_type
    )

    page.title = ""

    page.origin = (
        PageOrigin.TOMELINEA
    )

    page.source = None

    page.part_id = (
        desired.part_id
    )

    page.model_id = None

    page.spread_id = None
    page.spread_side = None

    page.auto_before = []
    page.auto_after = []

    page.is_compensation = False

    page.metadata[
        "creation_kind"
    ] = "automatic_structure"

    page.metadata[
        "automatic_structure"
    ] = True

    page.metadata[
        "automatic_kind"
    ] = "page_auto"

    page.metadata[
        "automatic_position"
    ] = "shared"

    _set_roles(
        page,
        desired.roles,
    )


# ==============================================================
# Synchronisation AV/AP
# ==============================================================

def _sync_av_ap(
    book: BookV4,
) -> tuple[
    int,
    int,
    int,
]:
    """
    Retour :
        reused, created, removed
    """

    base_order = (
        _base_order(
            book
        )
    )

    units = _units(
        book,
        base_order,
    )

    desired_slots = (
        _desired_slots(
            book,
            units,
        )
    )

    candidates = [
        page
        for page in book.pages.values()
        if is_structural_auto_page(
            page
        )
    ]

    old_auto_ids = {
        page.id
        for page in candidates
    }

    parity_candidates = {
        page.id: list(
            _parity_roles(
                page
            )
        )
        for page in candidates
        if _parity_roles(
            page
        )
    }

    # On détache toutes les autos avant reconstruction.
    for page in book.pages.values():
        if is_structural_auto_page(
            page
        ):
            continue

        page.auto_before = []
        page.auto_after = []

    book.page_order = list(
        base_order
    )

    for page_id in old_auto_ids:
        book.pages.pop(
            page_id,
            None,
        )

    used: set[str] = set()

    reused = 0
    created = 0

    slot_pages: list[
        list[PageV4]
    ] = []

    for slot in desired_slots:
        built: list[
            PageV4
        ] = []

        for desired in slot:
            best: PageV4 | None = None
            best_score = 0

            for candidate in candidates:
                if candidate.id in used:
                    continue

                score = _candidate_score(
                    candidate,
                    desired,
                )

                if score > best_score:
                    best = candidate
                    best_score = score

            if best is None:
                best = PageV4()
                created += 1
            else:
                used.add(
                    best.id
                )
                reused += 1

            _prepare_auto(
                best,
                desired,
            )

            book.pages[
                best.id
            ] = best

            built.append(
                best
            )

        slot_pages.append(
            built
        )

    # Ordre physique :
    # slot 0, unité 0, slot 1, unité 1...
    rebuilt_order: list[str] = []

    for index, unit in enumerate(
        units
    ):
        rebuilt_order.extend(
            page.id
            for page in slot_pages[
                index
            ]
        )

        rebuilt_order.extend(
            unit.page_ids
        )

    rebuilt_order.extend(
        page.id
        for page in slot_pages[
            len(units)
        ]
    )

    book.page_order = (
        rebuilt_order
    )

    # Reconstruction des références auto_before / auto_after.
    for built in slot_pages:
        for auto in built:
            for (
                code,
                source_id,
                _target_type,
            ) in [
                (
                    str(role["code"]),
                    str(role["source_id"]),
                    str(role["target_type"]),
                )
                for role in _roles(
                    auto
                )
            ]:
                source = book.pages.get(
                    source_id
                )

                if source is None:
                    raise ValueError(
                        "Source AV/AP inconnue : "
                        f"{source_id}"
                    )

                if code == "AV":
                    source.auto_before.append(
                        auto.id
                    )

                elif code == "AP":
                    source.auto_after.append(
                        auto.id
                    )

    # Les anciennes pages purement R/V/DP non utilisées sont
    # temporairement remises dans le Livre. sync_structure_parity()
    # les retirera immédiatement et pourra réutiliser leur UUID.
    for candidate in candidates:
        if candidate.id in used:
            continue

        parity = parity_candidates.get(
            candidate.id
        )

        if not parity:
            continue

        candidate.auto_before = []
        candidate.auto_after = []
        candidate.spread_id = None
        candidate.spread_side = None

        candidate.metadata[
            "automatic_structure"
        ] = True

        candidate.metadata[
            "creation_kind"
        ] = "automatic_structure"

        candidate.metadata[
            "automatic_roles"
        ] = [
            dict(role)
            for role in parity
        ]

        candidate.metadata[
            "automatic_markers"
        ] = [
            str(role["code"])
            for role in parity
        ]

        book.pages[
            candidate.id
        ] = candidate

        book.page_order.append(
            candidate.id
        )

    book.validate()

    surviving_old_ids = (
        old_auto_ids
        & set(
            book.pages
        )
    )

    removed = len(
        old_auto_ids
        - surviving_old_ids
    )

    return (
        reused,
        created,
        removed,
    )


# ==============================================================
# Synchronisation publique
# ==============================================================

def sync_structure_rules(
    book: BookV4,
) -> StructureSyncResult:

    book.validate()

    rule_issues = (
        structure_rule_issues(
            book
        )
    )

    if rule_issues:
        raise ValueError(
            "Règles Structure invalides : "
            + " ; ".join(
                rule_issues
            )
        )

    spread_issues = (
        structure_spread_issues(
            book
        )
    )

    if spread_issues:
        raise ValueError(
            "Double page invalide : "
            + " ; ".join(
                spread_issues
            )
        )

    reused, created, removed = (
        _sync_av_ap(
            book
        )
    )

    # Le moteur de parité déjà validé lit PageV4.recto_verso.
    # On lui présente temporairement les règles R/V effectives,
    # puis on restaure exactement les valeurs métier originales.
    originals = {
        page.id: page.recto_verso
        for page in book.pages.values()
        if not is_structural_auto_page(
            page
        )
    }

    try:
        for page_id in originals:
            side = (
                effective_recto_verso_rule(
                    book,
                    page_id,
                )
            )

            book.pages[
                page_id
            ].recto_verso = (
                side
                if side
                else None
            )

        compensation_count = (
            sync_structure_parity(
                book
            )
        )

    finally:
        for page_id, value in (
            originals.items()
        ):
            page = book.pages.get(
                page_id
            )

            if page is not None:
                page.recto_verso = (
                    value
                )

    book.validate()

    issues = (
        structure_spread_issues(
            book
        )
        + structure_auto_issues(
            book
        )
        + structure_rule_issues(
            book
        )
    )

    if issues:
        raise ValueError(
            "Structure incohérente après "
            "synchronisation : "
            + " ; ".join(
                issues
            )
        )

    book.history.append(
        {
            "action": "regles_structure_synchronisees",
            "reused_auto_pages": reused,
            "created_auto_pages": created,
            "removed_auto_pages": removed,
            "compensation_pages": compensation_count,
        }
    )

    return StructureSyncResult(
        reused_auto_pages=reused,
        created_auto_pages=created,
        removed_auto_pages=removed,
        compensation_pages=(
            compensation_count
        ),
    )
