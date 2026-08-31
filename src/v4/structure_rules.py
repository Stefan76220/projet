from __future__ import annotations

"""
TomeLinea V4 — règles Structure locales et étendues.

Principe :
    Local -> Étendre -> Scinder

Une règle locale appartient à une occurrence précise de PageV4.

Étendre :
    transforme cette règle en règle générale pour toutes
    les pages du même type.

Scinder :
    supprime la règle générale mais conserve la règle
    uniquement sur la page choisie.

Les règles restent séparées de leur matérialisation physique.
Ce module ne crée ni ne supprime aucune page automatique.
"""

from typing import Any

from src.v4.domain import (
    BookV4,
    PageV4,
)


STRUCTURE_RULES_KEY = "structure_rules"

PAGE_AUTO_TYPE_RULES_KEY = "page_auto_by_type"
RECTO_VERSO_TYPE_RULES_KEY = "recto_verso_by_type"

LOCAL_OVERRIDES_KEY = "structure_rule_overrides"

EXCLUDED = "__none__"

BEFORE = "before"
AFTER = "after"

RECTO = "recto"
VERSO = "verso"


# ==============================================================
# Helpers
# ==============================================================

def _source_type(
    page: PageV4,
) -> str:

    return str(
        page.page_type or ""
    ).strip().lower()


def _position(
    value: str,
) -> str:

    result = str(
        value or ""
    ).strip().lower()

    if result not in {
        BEFORE,
        AFTER,
    }:
        raise ValueError(
            "Position AV/AP invalide : "
            f"{value}"
        )

    return result


def _page(
    book: BookV4,
    page_id: str,
) -> PageV4:

    page = book.pages.get(
        page_id
    )

    if page is None:
        raise KeyError(
            page_id
        )

    if bool(
        page.metadata.get(
            "automatic_structure",
            False,
        )
    ):
        raise ValueError(
            "Une page automatique ne peut pas "
            "porter une règle Structure source."
        )

    return page


def _rules_root(
    book: BookV4,
    *,
    create: bool = False,
) -> dict[str, Any]:

    raw = book.metadata.get(
        STRUCTURE_RULES_KEY
    )

    if isinstance(
        raw,
        dict,
    ):
        return raw

    if not create:
        return {}

    result: dict[str, Any] = {}

    book.metadata[
        STRUCTURE_RULES_KEY
    ] = result

    return result


def _type_rules(
    book: BookV4,
    key: str,
    *,
    create: bool = False,
) -> dict[str, Any]:

    root = _rules_root(
        book,
        create=create,
    )

    raw = root.get(
        key
    )

    if isinstance(
        raw,
        dict,
    ):
        return raw

    if not create:
        return {}

    result: dict[str, Any] = {}

    root[
        key
    ] = result

    return result


def _overrides(
    page: PageV4,
    *,
    create: bool = False,
) -> dict[str, Any]:

    raw = page.metadata.get(
        LOCAL_OVERRIDES_KEY
    )

    if isinstance(
        raw,
        dict,
    ):
        return raw

    if not create:
        return {}

    result: dict[str, Any] = {}

    page.metadata[
        LOCAL_OVERRIDES_KEY
    ] = result

    return result


def _cleanup_overrides(
    page: PageV4,
) -> None:

    raw = page.metadata.get(
        LOCAL_OVERRIDES_KEY
    )

    if (
        isinstance(raw, dict)
        and not raw
    ):
        page.metadata.pop(
            LOCAL_OVERRIDES_KEY,
            None,
        )


def _same_type_pages(
    book: BookV4,
    source_type: str,
) -> list[PageV4]:

    return [
        page
        for page in book.pages.values()
        if (
            not bool(
                page.metadata.get(
                    "automatic_structure",
                    False,
                )
            )
            and _source_type(
                page
            ) == source_type
        )
    ]


# ==============================================================
# AV / AP
# ==============================================================

def _page_auto_override_key(
    position: str,
) -> str:

    position = _position(
        position
    )

    return (
        "page_auto_before"
        if position == BEFORE
        else "page_auto_after"
    )


def page_auto_type_rules(
    book: BookV4,
) -> dict[str, dict[str, str]]:

    raw = _type_rules(
        book,
        PAGE_AUTO_TYPE_RULES_KEY,
    )

    result: dict[
        str,
        dict[str, str],
    ] = {}

    for source_type, entry in raw.items():
        if not isinstance(
            entry,
            dict,
        ):
            continue

        normalized: dict[
            str,
            str,
        ] = {}

        for position in (
            BEFORE,
            AFTER,
        ):
            value = str(
                entry.get(
                    position
                )
                or ""
            ).strip()

            if value:
                normalized[
                    position
                ] = value

        if normalized:
            result[
                str(source_type)
            ] = normalized

    return result


def effective_page_auto_rule(
    book: BookV4,
    page_id: str,
    position: str,
) -> str:

    page = _page(
        book,
        page_id,
    )

    position = _position(
        position
    )

    override_key = (
        _page_auto_override_key(
            position
        )
    )

    overrides = _overrides(
        page
    )

    if override_key in overrides:
        value = str(
            overrides[
                override_key
            ]
            or ""
        ).strip()

        if value == EXCLUDED:
            return ""

        return value

    source_type = _source_type(
        page
    )

    return (
        page_auto_type_rules(
            book
        )
        .get(
            source_type,
            {},
        )
        .get(
            position,
            "",
        )
    )


def set_local_page_auto_rule(
    book: BookV4,
    page_id: str,
    *,
    position: str,
    target_type: str,
) -> None:

    book.validate()

    page = _page(
        book,
        page_id,
    )

    position = _position(
        position
    )

    target = str(
        target_type or ""
    ).strip()

    if not target:
        raise ValueError(
            "Le type de page AV/AP "
            "ne peut pas être vide."
        )

    overrides = _overrides(
        page,
        create=True,
    )

    overrides[
        _page_auto_override_key(
            position
        )
    ] = target

    book.history.append(
        {
            "action": "regle_av_ap_locale",
            "page_id": page.id,
            "position": position,
            "target_type": target,
        }
    )


def exclude_local_page_auto_rule(
    book: BookV4,
    page_id: str,
    *,
    position: str,
) -> None:

    page = _page(
        book,
        page_id,
    )

    position = _position(
        position
    )

    overrides = _overrides(
        page,
        create=True,
    )

    overrides[
        _page_auto_override_key(
            position
        )
    ] = EXCLUDED


def clear_local_page_auto_rule(
    book: BookV4,
    page_id: str,
    *,
    position: str,
) -> bool:

    page = _page(
        book,
        page_id,
    )

    key = _page_auto_override_key(
        position
    )

    overrides = _overrides(
        page
    )

    if key not in overrides:
        return False

    overrides.pop(
        key,
        None,
    )

    _cleanup_overrides(
        page
    )

    return True


def extend_page_auto_rule(
    book: BookV4,
    page_id: str,
    *,
    position: str,
) -> None:
    """
    Transforme une règle locale en règle du type entier.
    """

    book.validate()

    page = _page(
        book,
        page_id,
    )

    position = _position(
        position
    )

    key = _page_auto_override_key(
        position
    )

    overrides = _overrides(
        page
    )

    value = str(
        overrides.get(
            key
        )
        or ""
    ).strip()

    if (
        not value
        or value == EXCLUDED
    ):
        raise ValueError(
            "Aucune règle AV/AP locale "
            "à étendre sur cette page."
        )

    source_type = _source_type(
        page
    )

    if not source_type:
        raise ValueError(
            "La page n'a pas de type."
        )

    rules = _type_rules(
        book,
        PAGE_AUTO_TYPE_RULES_KEY,
        create=True,
    )

    entry = rules.get(
        source_type
    )

    if not isinstance(
        entry,
        dict,
    ):
        entry = {}

    entry[
        position
    ] = value

    rules[
        source_type
    ] = entry

    # Étendre repart d'un état homogène :
    # les anciennes exceptions du même type disparaissent.
    for candidate in _same_type_pages(
        book,
        source_type,
    ):
        candidate_overrides = (
            _overrides(
                candidate
            )
        )

        candidate_overrides.pop(
            key,
            None,
        )

        _cleanup_overrides(
            candidate
        )

    book.history.append(
        {
            "action": "regle_av_ap_etendue",
            "source_type": source_type,
            "position": position,
            "target_type": value,
        }
    )


def scind_page_auto_rule(
    book: BookV4,
    page_id: str,
    *,
    position: str,
) -> None:
    """
    Retire la règle générale et la conserve localement
    uniquement sur la page choisie.
    """

    book.validate()

    page = _page(
        book,
        page_id,
    )

    position = _position(
        position
    )

    source_type = _source_type(
        page
    )

    rules = _type_rules(
        book,
        PAGE_AUTO_TYPE_RULES_KEY,
        create=True,
    )

    entry = rules.get(
        source_type
    )

    if not isinstance(
        entry,
        dict,
    ):
        raise ValueError(
            "Aucune règle AV/AP générale "
            "à scinder."
        )

    general_value = str(
        entry.get(
            position
        )
        or ""
    ).strip()

    if not general_value:
        raise ValueError(
            "Aucune règle AV/AP générale "
            "à scinder."
        )

    selected_value = (
        effective_page_auto_rule(
            book,
            page.id,
            position,
        )
    )

    if not selected_value:
        raise ValueError(
            "La page sélectionnée est exclue "
            "de cette règle."
        )

    entry.pop(
        position,
        None,
    )

    if entry:
        rules[
            source_type
        ] = entry
    else:
        rules.pop(
            source_type,
            None,
        )

    key = _page_auto_override_key(
        position
    )

    for candidate in _same_type_pages(
        book,
        source_type,
    ):
        overrides = _overrides(
            candidate
        )

        overrides.pop(
            key,
            None,
        )

        _cleanup_overrides(
            candidate
        )

    selected_overrides = _overrides(
        page,
        create=True,
    )

    selected_overrides[
        key
    ] = selected_value

    book.history.append(
        {
            "action": "regle_av_ap_scindee",
            "page_id": page.id,
            "source_type": source_type,
            "position": position,
            "target_type": selected_value,
        }
    )


# ==============================================================
# Recto / Verso
# ==============================================================

def recto_verso_type_rules(
    book: BookV4,
) -> dict[str, str]:

    raw = _type_rules(
        book,
        RECTO_VERSO_TYPE_RULES_KEY,
    )

    result: dict[str, str] = {}

    for source_type, side in raw.items():
        value = str(
            side or ""
        ).strip().lower()

        if value in {
            RECTO,
            VERSO,
        }:
            result[
                str(source_type)
            ] = value

    return result


def effective_recto_verso_rule(
    book: BookV4,
    page_id: str,
) -> str:

    page = _page(
        book,
        page_id,
    )

    overrides = _overrides(
        page
    )

    if "recto_verso" in overrides:
        value = str(
            overrides[
                "recto_verso"
            ]
            or ""
        ).strip().lower()

        if value == EXCLUDED:
            return ""

        if value in {
            RECTO,
            VERSO,
        }:
            return value

    source_type = _source_type(
        page
    )

    general = (
        recto_verso_type_rules(
            book
        ).get(
            source_type,
            "",
        )
    )

    if general:
        return general

    # Une valeur déjà portée par PageV4 reste la valeur sous-jacente.
    # Les règles Structure ne la détruisent jamais.
    underlying = str(
        page.recto_verso or ""
    ).strip().lower()

    return (
        underlying
        if underlying in {
            RECTO,
            VERSO,
        }
        else ""
    )


def set_local_recto_verso_rule(
    book: BookV4,
    page_id: str,
    side: str,
) -> None:

    book.validate()

    page = _page(
        book,
        page_id,
    )

    value = str(
        side or ""
    ).strip().lower()

    if value not in {
        RECTO,
        VERSO,
    }:
        raise ValueError(
            "Côté R/V invalide : "
            f"{side}"
        )

    overrides = _overrides(
        page,
        create=True,
    )

    overrides[
        "recto_verso"
    ] = value

    book.history.append(
        {
            "action": "regle_recto_verso_locale",
            "page_id": page.id,
            "side": value,
        }
    )


def exclude_local_recto_verso_rule(
    book: BookV4,
    page_id: str,
) -> None:

    page = _page(
        book,
        page_id,
    )

    overrides = _overrides(
        page,
        create=True,
    )

    overrides[
        "recto_verso"
    ] = EXCLUDED


def clear_local_recto_verso_rule(
    book: BookV4,
    page_id: str,
) -> bool:

    page = _page(
        book,
        page_id,
    )

    overrides = _overrides(
        page
    )

    if "recto_verso" not in overrides:
        return False

    overrides.pop(
        "recto_verso",
        None,
    )

    _cleanup_overrides(
        page
    )

    return True


def extend_recto_verso_rule(
    book: BookV4,
    page_id: str,
) -> None:

    book.validate()

    page = _page(
        book,
        page_id,
    )

    overrides = _overrides(
        page
    )

    side = str(
        overrides.get(
            "recto_verso"
        )
        or ""
    ).strip().lower()

    if side not in {
        RECTO,
        VERSO,
    }:
        raise ValueError(
            "Aucune règle R/V locale "
            "à étendre."
        )

    source_type = _source_type(
        page
    )

    rules = _type_rules(
        book,
        RECTO_VERSO_TYPE_RULES_KEY,
        create=True,
    )

    rules[
        source_type
    ] = side

    for candidate in _same_type_pages(
        book,
        source_type,
    ):
        candidate_overrides = (
            _overrides(
                candidate
            )
        )

        candidate_overrides.pop(
            "recto_verso",
            None,
        )

        _cleanup_overrides(
            candidate
        )

    book.history.append(
        {
            "action": "regle_recto_verso_etendue",
            "source_type": source_type,
            "side": side,
        }
    )


def scind_recto_verso_rule(
    book: BookV4,
    page_id: str,
) -> None:

    book.validate()

    page = _page(
        book,
        page_id,
    )

    source_type = _source_type(
        page
    )

    rules = _type_rules(
        book,
        RECTO_VERSO_TYPE_RULES_KEY,
        create=True,
    )

    general = str(
        rules.get(
            source_type
        )
        or ""
    ).strip().lower()

    if general not in {
        RECTO,
        VERSO,
    }:
        raise ValueError(
            "Aucune règle R/V générale "
            "à scinder."
        )

    selected_side = (
        effective_recto_verso_rule(
            book,
            page.id,
        )
    )

    if selected_side not in {
        RECTO,
        VERSO,
    }:
        raise ValueError(
            "La page sélectionnée est exclue "
            "de cette règle."
        )

    rules.pop(
        source_type,
        None,
    )

    for candidate in _same_type_pages(
        book,
        source_type,
    ):
        overrides = _overrides(
            candidate
        )

        overrides.pop(
            "recto_verso",
            None,
        )

        _cleanup_overrides(
            candidate
        )

    selected_overrides = _overrides(
        page,
        create=True,
    )

    selected_overrides[
        "recto_verso"
    ] = selected_side

    book.history.append(
        {
            "action": "regle_recto_verso_scindee",
            "page_id": page.id,
            "source_type": source_type,
            "side": selected_side,
        }
    )


# ==============================================================
# Validation
# ==============================================================

def structure_rule_issues(
    book: BookV4,
) -> list[str]:

    issues: list[str] = []

    root = book.metadata.get(
        STRUCTURE_RULES_KEY,
        {},
    )

    if not isinstance(
        root,
        dict,
    ):
        return [
            "structure_rules invalide"
        ]

    page_auto = root.get(
        PAGE_AUTO_TYPE_RULES_KEY,
        {},
    )

    if not isinstance(
        page_auto,
        dict,
    ):
        issues.append(
            "page_auto_by_type invalide"
        )

    else:
        for source_type, entry in page_auto.items():
            if not str(
                source_type or ""
            ).strip():
                issues.append(
                    "type source AV/AP vide"
                )

            if not isinstance(
                entry,
                dict,
            ):
                issues.append(
                    "règle AV/AP invalide : "
                    f"{source_type}"
                )
                continue

            extra = set(
                entry
            ) - {
                BEFORE,
                AFTER,
            }

            if extra:
                issues.append(
                    "position AV/AP inconnue : "
                    f"{sorted(extra)}"
                )

            for position, target in entry.items():
                if (
                    position
                    in {
                        BEFORE,
                        AFTER,
                    }
                    and not str(
                        target or ""
                    ).strip()
                ):
                    issues.append(
                        "cible AV/AP vide : "
                        f"{source_type}/{position}"
                    )

    rv = root.get(
        RECTO_VERSO_TYPE_RULES_KEY,
        {},
    )

    if not isinstance(
        rv,
        dict,
    ):
        issues.append(
            "recto_verso_by_type invalide"
        )

    else:
        for source_type, side in rv.items():
            if str(
                side or ""
            ).strip().lower() not in {
                RECTO,
                VERSO,
            }:
                issues.append(
                    "règle R/V invalide : "
                    f"{source_type}"
                )

    return issues
