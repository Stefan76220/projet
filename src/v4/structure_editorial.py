from __future__ import annotations

"""
TomeLinea V4 — façade éditoriale du moteur Structure V3/V4.

Cette couche ne possède aucun moteur physique parallèle.
Elle traduit uniquement des décisions utilisateur explicites vers
les règles Structure déjà portées de la V3 :

    règle locale -> extension volontaire -> exception locale -> sync Structure

La matérialisation des pages automatiques, la parité et les doubles pages
restent exclusivement du ressort de structure_rules / structure_sync.
"""

from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Iterable
from uuid import uuid4

from src.v4.project import ProjectV4
from src.v4.page_content_classifier import similar_layout_page_ids
from src.v4.structure_auto import (
    AUTO_ORIGIN_ROLES_KEY,
    is_auto_origin_page,
    is_structural_auto_page,
    protect_auto_page,
)
from src.v4.structure_spreads import (
    SPREAD_LEFT,
    SPREAD_RIGHT,
    page_spread,
    pair_pages,
    split_spread,
)
from src.v4.structure_covers import is_cover_face
from src.v4.structure_rules import (
    AFTER,
    BEFORE,
    RECTO,
    VERSO,
    clear_local_page_auto_rule,
    clear_local_recto_verso_rule,
    effective_page_auto_rule,
    effective_recto_verso_rule,
    exclude_local_page_auto_rule,
    exclude_local_recto_verso_rule,
    page_auto_type_rules,
    recto_verso_type_rules,
    set_local_page_auto_rule,
    set_local_recto_verso_rule,
)


PAGE_RIGHT = "page_right"
PAGE_LEFT = "page_left"
BLANK_BEFORE = "blank_before"
BLANK_AFTER = "blank_after"
DOUBLE_PAGE = "double_page"

KNOWN_CONSTRAINTS = (
    PAGE_RIGHT,
    PAGE_LEFT,
    BLANK_BEFORE,
    BLANK_AFTER,
    DOUBLE_PAGE,
)

CONSTRAINT_LABELS = {
    PAGE_RIGHT: "Page à droite (recto)",
    PAGE_LEFT: "Page à gauche (verso)",
    BLANK_BEFORE: "Page blanche avant",
    BLANK_AFTER: "Page blanche après",
    DOUBLE_PAGE: "Double page (gauche + droite)",
}

CONSTRAINT_HELP = {
    PAGE_RIGHT: "Cette page apparaîtra à droite.",
    PAGE_LEFT: "Cette page apparaîtra à gauche.",
    BLANK_BEFORE: "Une page blanche sera conservée juste avant.",
    BLANK_AFTER: "Une page blanche sera conservée juste après.",
    DOUBLE_PAGE: "Ces deux pages resteront ensemble, gauche + droite.",
}

SIMILARITY_THRESHOLD = 0.88
EXTENSIONS_KEY = "editorial_similarity_extensions"
EXTENSIONS_SCHEMA = "tomelinea.structure_editorial_extensions.v1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _book(project: ProjectV4):
    if project.book is None:
        raise ValueError("Le Projet ne possède aucun Livre.")
    return project.book


def _page(book, page_id: str, *, allow_auto: bool = False):
    page = book.pages.get(str(page_id))
    if page is None:
        raise KeyError(page_id)
    if is_structural_auto_page(page) and not allow_auto:
        raise ValueError(
            "Cette contrainte ne s'applique pas directement à une page ajoutée automatiquement."
        )
    return page


def _normalize_ids(book, page_ids: Iterable[str], *, include_auto: bool = False) -> list[str]:
    wanted = {str(value) for value in page_ids}
    result: list[str] = []
    for page_id in book.page_order:
        if page_id not in wanted:
            continue
        page = book.pages[page_id]
        if is_structural_auto_page(page) and not include_auto:
            continue
        result.append(page_id)
    return result


def _page_type(page) -> str:
    return str(page.page_type or "").strip().lower()


def _extension_root(book, *, create: bool = False) -> dict[str, Any]:
    raw = book.metadata.get(EXTENSIONS_KEY)
    if isinstance(raw, dict):
        if raw.get("schema") == EXTENSIONS_SCHEMA and isinstance(raw.get("items"), dict):
            return raw
        # Tolérance : ancien dictionnaire d'items sans enveloppe.
        if "schema" not in raw:
            root = {"schema": EXTENSIONS_SCHEMA, "items": dict(raw)}
            book.metadata[EXTENSIONS_KEY] = root
            return root
    if not create:
        return {"schema": EXTENSIONS_SCHEMA, "items": {}}
    root = {"schema": EXTENSIONS_SCHEMA, "items": {}}
    book.metadata[EXTENSIONS_KEY] = root
    return root


def similarity_extensions(book) -> dict[str, dict[str, Any]]:
    root = _extension_root(book)
    items = root.get("items", {})
    if not isinstance(items, dict):
        return {}
    result: dict[str, dict[str, Any]] = {}
    for extension_id, raw in items.items():
        if not isinstance(raw, dict):
            continue
        kind = str(raw.get("kind") or "")
        if kind not in KNOWN_CONSTRAINTS:
            continue
        result[str(extension_id)] = raw
    return result


def _save_extension(book, extension_id: str, record: dict[str, Any]) -> None:
    root = _extension_root(book, create=True)
    root["items"][str(extension_id)] = record


def _remove_extension_record(book, extension_id: str) -> None:
    root = _extension_root(book, create=True)
    root.get("items", {}).pop(str(extension_id), None)
    if not root.get("items"):
        book.metadata.pop(EXTENSIONS_KEY, None)


def extension_memberships(book, page_id: str, *, kind: str | None = None) -> list[dict[str, Any]]:
    page_id = str(page_id)
    result: list[dict[str, Any]] = []
    for extension_id, record in similarity_extensions(book).items():
        if kind is not None and str(record.get("kind")) != kind:
            continue
        members = {str(value) for value in record.get("member_page_ids", record.get("page_ids", []))}
        if page_id not in members:
            continue
        excluded = {str(value) for value in record.get("excluded_page_ids", [])}
        excluded_key = page_id
        if str(record.get("kind") or "") == DOUBLE_PAGE:
            mapping = record.get("pair_anchor_by_member", {})
            if isinstance(mapping, dict):
                excluded_key = str(mapping.get(page_id) or page_id)
        result.append(
            {
                "id": extension_id,
                "kind": str(record.get("kind") or ""),
                "anchor_page_id": str(record.get("anchor_page_id") or ""),
                "threshold": float(record.get("threshold", SIMILARITY_THRESHOLD)),
                "page_count": len(members),
                "excluded": excluded_key in excluded,
            }
        )
    return result


def _set_extension_excluded(book, extension_id: str, page_id: str, excluded: bool) -> None:
    root = _extension_root(book, create=True)
    record = root.get("items", {}).get(str(extension_id))
    if not isinstance(record, dict):
        return
    values = {str(value) for value in record.get("excluded_page_ids", [])}
    key = str(page_id)
    if str(record.get("kind") or "") == DOUBLE_PAGE:
        mapping = record.get("pair_anchor_by_member", {})
        if isinstance(mapping, dict):
            key = str(mapping.get(key) or key)
    if excluded:
        values.add(key)
    else:
        values.discard(key)
    record["excluded_page_ids"] = sorted(values)


def _native_enabled(book, page_id: str, kind: str) -> bool:
    if kind == PAGE_RIGHT:
        return effective_recto_verso_rule(book, page_id) == RECTO
    if kind == PAGE_LEFT:
        return effective_recto_verso_rule(book, page_id) == VERSO
    if kind == BLANK_BEFORE:
        return bool(effective_page_auto_rule(book, page_id, BEFORE))
    if kind == BLANK_AFTER:
        return bool(effective_page_auto_rule(book, page_id, AFTER))
    if kind == DOUBLE_PAGE:
        page = _page(book, page_id, allow_auto=True)
        return bool(page.spread_id and page_spread(book, page_id) is not None)
    raise ValueError(f"Contrainte inconnue : {kind}")


def constraint_enabled(book, page_id: str, kind: str) -> bool:
    kind = str(kind)
    page = _page(book, page_id, allow_auto=(kind == DOUBLE_PAGE))
    if is_cover_face(page):
        return False
    return _native_enabled(book, str(page_id), kind)


def active_constraint_kinds(book, page_id: str) -> tuple[str, ...]:
    page = _page(book, page_id, allow_auto=True)
    if is_cover_face(page):
        return ()
    if is_structural_auto_page(page):
        return (DOUBLE_PAGE,) if _native_enabled(book, page_id, DOUBLE_PAGE) else ()
    return tuple(kind for kind in KNOWN_CONSTRAINTS if _native_enabled(book, page_id, kind))


def _native_disable(book, page_id: str, kind: str) -> None:
    if kind == DOUBLE_PAGE:
        page = _page(book, page_id, allow_auto=True)
        if page.spread_id:
            split_spread(book, page.spread_id)
        return
    page = _page(book, page_id)
    page_type = _page_type(page)

    if kind in {PAGE_RIGHT, PAGE_LEFT}:
        side = RECTO if kind == PAGE_RIGHT else VERSO
        general = recto_verso_type_rules(book).get(page_type, "")
        if general == side:
            exclude_local_recto_verso_rule(book, page_id)
        else:
            clear_local_recto_verso_rule(book, page_id)
        return

    position = BEFORE if kind == BLANK_BEFORE else AFTER
    general = page_auto_type_rules(book).get(page_type, {}).get(position, "")
    if general:
        exclude_local_page_auto_rule(book, page_id, position=position)
    else:
        clear_local_page_auto_rule(book, page_id, position=position)


def _native_enable(book, page_id: str, kind: str) -> None:
    if kind == DOUBLE_PAGE:
        raise ValueError(
            "Une double page se crée en sélectionnant explicitement les deux pages à associer."
        )

    _page(book, page_id)

    if kind == PAGE_RIGHT:
        set_local_recto_verso_rule(book, page_id, RECTO)
        return
    if kind == PAGE_LEFT:
        set_local_recto_verso_rule(book, page_id, VERSO)
        return
    if kind == BLANK_BEFORE:
        set_local_page_auto_rule(
            book,
            page_id,
            position=BEFORE,
            target_type="Page blanche",
        )
        return
    if kind == BLANK_AFTER:
        set_local_page_auto_rule(
            book,
            page_id,
            position=AFTER,
            target_type="Page blanche",
        )
        return
    raise ValueError(f"Contrainte inconnue : {kind}")


def set_local_constraint(book, page_id: str, kind: str, enabled: bool) -> None:
    """Ajoute/retire une contrainte sur UNE page, sans toucher aux autres."""
    page_id = str(page_id)
    kind = str(kind)
    page = _page(book, page_id, allow_auto=(kind == DOUBLE_PAGE))
    if kind not in KNOWN_CONSTRAINTS:
        raise ValueError(f"Contrainte inconnue : {kind}")
    if is_cover_face(page):
        raise ValueError(
            "Les faces de couverture ont une position physique fixe et n'acceptent pas de contrainte de page."
        )

    # Les deux côtés sont mutuellement exclusifs. Une décision locale
    # opposée devient une exception éventuelle à l'extension précédente.
    opposite = None
    if kind == PAGE_RIGHT:
        opposite = PAGE_LEFT
    elif kind == PAGE_LEFT:
        opposite = PAGE_RIGHT

    if enabled and opposite is not None and _native_enabled(book, page_id, opposite):
        for membership in extension_memberships(book, page_id, kind=opposite):
            _set_extension_excluded(book, membership["id"], page_id, True)
        _native_disable(book, page_id, opposite)

    memberships = extension_memberships(book, page_id, kind=kind)

    if enabled:
        for membership in memberships:
            _set_extension_excluded(book, membership["id"], page_id, False)
        _native_enable(book, page_id, kind)
    else:
        for membership in memberships:
            _set_extension_excluded(book, membership["id"], page_id, True)
        _native_disable(book, page_id, kind)


def _double_page_conflict(book, left_id: str, right_id: str) -> str:
    left = book.pages[left_id]
    right = book.pages[right_id]
    if left.part_id != right.part_id:
        return "Les deux pages doivent appartenir à la même partie."
    if left.spread_id or right.spread_id:
        if left.spread_id and left.spread_id == right.spread_id:
            return ""
        return "Une des pages appartient déjà à une autre double page."
    if not is_structural_auto_page(left):
        side = effective_recto_verso_rule(book, left.id)
        if side == RECTO:
            return "La page de gauche est imposée à droite (recto)."
    if not is_structural_auto_page(right):
        side = effective_recto_verso_rule(book, right.id)
        if side == VERSO:
            return "La page de droite est imposée à gauche (verso)."
    return ""


def double_page_selection_reason(book, page_ids: Iterable[str]) -> str:
    """Explique pourquoi la sélection ne peut pas devenir UNE double page.

    La décision éditoriale porte toujours sur deux UUID explicitement choisis.
    TomeLinea ne choisit jamais la page précédente/suivante à la place de
    l'utilisateur.
    """

    targets = _normalize_ids(book, page_ids, include_auto=True)
    if len(targets) != 2:
        return "Sélectionnez exactement deux pages pour créer une double page."

    positions = [book.page_order.index(page_id) for page_id in targets]
    ordered = [page_id for _pos, page_id in sorted(zip(positions, targets))]
    left_id, right_id = ordered

    if is_cover_face(book.pages[left_id]) or is_cover_face(book.pages[right_id]):
        return "Les faces de couverture ne peuvent pas appartenir à une double page éditoriale."

    if book.page_order.index(right_id) != book.page_order.index(left_id) + 1:
        return (
            "Les deux pages sélectionnées doivent être voisines dans le Livre "
            "pour former une double page."
        )

    if (
        book.pages[left_id].spread_id
        and book.pages[left_id].spread_id == book.pages[right_id].spread_id
    ):
        return ""

    return _double_page_conflict(book, left_id, right_id)


def _set_double_page_selection(book, page_ids: Iterable[str], enabled: bool) -> list[str]:
    targets = _normalize_ids(book, page_ids, include_auto=True)
    if not targets:
        return []

    if not enabled:
        spread_ids = []
        for page_id in targets:
            page = book.pages[page_id]
            if page.spread_id and page.spread_id not in spread_ids:
                spread_ids.append(page.spread_id)
        for spread_id in spread_ids:
            split_spread(book, spread_id)
        return targets

    reason = double_page_selection_reason(book, targets)
    if reason:
        raise ValueError(reason)

    positions = [book.page_order.index(page_id) for page_id in targets]
    ordered = [page_id for _pos, page_id in sorted(zip(positions, targets))]
    left_id, right_id = ordered

    if not (
        book.pages[left_id].spread_id
        and book.pages[left_id].spread_id == book.pages[right_id].spread_id
    ):
        pair_pages(book, left_id, right_id)
    return ordered


def set_constraint_on_pages(book, page_ids: Iterable[str], kind: str, enabled: bool) -> list[str]:
    """Même décision locale répétée indépendamment, sauf 2P qui est une relation physique."""
    kind = str(kind)
    if kind == DOUBLE_PAGE:
        return _set_double_page_selection(book, page_ids, enabled)
    targets = _normalize_ids(book, page_ids)
    for page_id in targets:
        set_local_constraint(book, page_id, kind, enabled)
    return targets


def copy_active_constraints_to_pages(book, anchor_page_id: str, page_ids: Iterable[str]) -> list[str]:
    """Étend volontairement les règles ACTIVES de la page de référence à une sélection.

    Il ne crée aucune liaison entre les pages : chaque cible reçoit sa décision locale.
    """
    anchor_page_id = str(anchor_page_id)
    kinds = active_constraint_kinds(book, anchor_page_id)
    targets = [value for value in _normalize_ids(book, page_ids) if value != anchor_page_id]
    for kind in kinds:
        if kind == DOUBLE_PAGE:
            continue
        for page_id in targets:
            set_local_constraint(book, page_id, kind, True)
    return targets


def similar_page_ids(
    project: ProjectV4,
    anchor_page_id: str,
    *,
    threshold: float = SIMILARITY_THRESHOLD,
) -> list[str]:
    """Pages de mise en page similaire selon le moteur 88 % déjà utilisé pour Fiche."""

    book = _book(project)
    anchor_page_id = str(anchor_page_id)
    _page(book, anchor_page_id)

    candidates = similar_layout_page_ids(
        book,
        anchor_page_id,
        threshold=float(threshold),
    )

    return [
        page_id
        for page_id in candidates
        if (
            page_id in book.pages
            and not is_structural_auto_page(book.pages[page_id])
        )
    ]


def extend_constraint_to_similar(
    project: ProjectV4,
    anchor_page_id: str,
    kind: str,
    *,
    threshold: float = SIMILARITY_THRESHOLD,
) -> dict[str, Any]:
    """Étend volontairement une règle à la famille similaire de la page.

    La règle physique reste matérialisée par les règles locales V3/V4.
    Le record d'extension ne sert qu'à mémoriser la portée choisie,
    le seuil et les exceptions pour l'interface et l'audit final.
    """
    book = _book(project)
    anchor_page_id = str(anchor_page_id)
    kind = str(kind)
    _page(book, anchor_page_id, allow_auto=(kind == DOUBLE_PAGE))
    if kind not in KNOWN_CONSTRAINTS:
        raise ValueError(f"Contrainte inconnue : {kind}")
    if not constraint_enabled(book, anchor_page_id, kind):
        raise ValueError("La contrainte doit d'abord être appliquée à la page de référence.")

    if kind == DOUBLE_PAGE:
        raise ValueError(
            "Une double page relie deux pages choisies explicitement ; "
            "elle ne s'étend pas automatiquement par similarité."
        )

    candidates = similar_page_ids(project, anchor_page_id, threshold=threshold)
    if anchor_page_id not in candidates:
        candidates.insert(0, anchor_page_id)

    # Réutilise l'extension de même ancre et même contrainte si elle existe.
    existing_id = None
    existing_record = None
    for extension_id, record in similarity_extensions(book).items():
        if (
            str(record.get("anchor_page_id") or "") == anchor_page_id
            and str(record.get("kind") or "") == kind
        ):
            existing_id = extension_id
            existing_record = record
            break

    extension_id = existing_id or str(uuid4())
    previous_excluded = {
        str(value)
        for value in (existing_record or {}).get("excluded_page_ids", [])
    }
    preexisting = {
        page_id
        for page_id in candidates
        if constraint_enabled(book, page_id, kind)
    }

    excluded = set(previous_excluded)
    applied: list[str] = []
    member_page_ids: set[str] = set(candidates)
    pair_anchor_by_member: dict[str, str] = {}
    created_spread_ids: list[str] = []
    opposite = PAGE_LEFT if kind == PAGE_RIGHT else PAGE_RIGHT if kind == PAGE_LEFT else None

    if kind == DOUBLE_PAGE:
        anchor_spread = page_spread(book, anchor_page_id)
        if anchor_spread is None:
            raise ValueError("La double page doit d'abord être créée sur la page de référence.")
        anchor = book.pages[anchor_page_id]
        anchor_side = anchor.spread_side

        for page_id in candidates:
            if page_id in excluded:
                continue
            page = book.pages[page_id]
            index = book.page_order.index(page_id)
            if anchor_side == SPREAD_RIGHT:
                if index <= 0:
                    excluded.add(page_id); continue
                left_id, right_id = book.page_order[index - 1], page_id
            else:
                if index + 1 >= len(book.page_order):
                    excluded.add(page_id); continue
                left_id, right_id = page_id, book.page_order[index + 1]

            member_page_ids.update((left_id, right_id))
            pair_anchor_by_member[left_id] = page_id
            pair_anchor_by_member[right_id] = page_id

            existing = page_spread(book, page_id)
            if existing is not None:
                if {existing.left_page_id, existing.right_page_id} == {left_id, right_id}:
                    applied.append(page_id)
                    continue
                excluded.add(page_id); continue

            reason = _double_page_conflict(book, left_id, right_id)
            if reason:
                excluded.add(page_id); continue
            spread = pair_pages(book, left_id, right_id)
            created_spread_ids.append(spread.spread_id)
            applied.append(page_id)
    else:
        for page_id in candidates:
            if page_id in excluded:
                continue
            if opposite is not None and constraint_enabled(book, page_id, opposite):
                # Ne jamais écraser silencieusement une décision éditoriale contraire.
                excluded.add(page_id)
                continue
            set_local_constraint(book, page_id, kind, True)
            applied.append(page_id)

    record = {
        "id": extension_id,
        "kind": kind,
        "anchor_page_id": anchor_page_id,
        "threshold": float(threshold),
        "page_ids": list(candidates),
        "member_page_ids": sorted(member_page_ids),
        "pair_anchor_by_member": dict(pair_anchor_by_member),
        "created_spread_ids": list(created_spread_ids),
        "excluded_page_ids": sorted(excluded),
        "preexisting_page_ids": sorted(preexisting),
        "created_at": str((existing_record or {}).get("created_at") or _now()),
        "updated_at": _now(),
    }
    _save_extension(book, extension_id, record)

    return {
        "extension_id": extension_id,
        "page_ids": list(candidates),
        "applied_page_ids": applied,
        "excluded_page_ids": sorted(excluded),
        "threshold": float(threshold),
    }


def remove_similarity_extension(book, extension_id: str) -> list[str]:
    extension_id = str(extension_id)
    record = similarity_extensions(book).get(extension_id)
    if record is None:
        raise KeyError(extension_id)

    kind = str(record.get("kind") or "")
    members = {str(value) for value in record.get("page_ids", [])}
    excluded = {str(value) for value in record.get("excluded_page_ids", [])}
    preexisting = {str(value) for value in record.get("preexisting_page_ids", [])}

    changed: list[str] = []
    if kind == DOUBLE_PAGE:
        for spread_id in list(record.get("created_spread_ids", [])):
            try:
                pair = split_spread(book, str(spread_id))
            except (ValueError, KeyError):
                continue
            changed.extend([pair.left_page_id, pair.right_page_id])
    else:
        for page_id in _normalize_ids(book, members):
            if page_id in excluded or page_id in preexisting:
                continue
            if constraint_enabled(book, page_id, kind):
                _native_disable(book, page_id, kind)
                changed.append(page_id)

    _remove_extension_record(book, extension_id)
    return changed


def constraint_summary(book, page_id: str) -> list[str]:
    return [CONSTRAINT_LABELS[kind] for kind in active_constraint_kinds(book, page_id)]


def _automatic_content_signature(page) -> tuple:
    """Signature éditoriale stable d'une page née automatiquement.

    Les rôles purement liés à une double page (DP) ne changent pas la famille
    d'origine de la page. Une page AV devenue moitié gauche d'une 2P reste donc
    comparable aux autres pages AV équivalentes.
    """
    if not is_auto_origin_page(page):
        return ()

    raw = page.metadata.get(AUTO_ORIGIN_ROLES_KEY)
    if not isinstance(raw, list) or not raw:
        raw = page.metadata.get("automatic_roles")

    roles: list[tuple[str, str]] = []
    if isinstance(raw, list):
        for role in raw:
            if not isinstance(role, dict):
                continue
            code = str(role.get("code") or "").strip().upper()
            target_type = str(role.get("target_type") or page.page_type or "Page blanche").strip()
            if not code or code == "DP":
                continue
            roles.append((code, target_type))

    if not roles:
        kind = str(page.metadata.get("automatic_kind") or "").strip().lower()
        position = str(page.metadata.get("automatic_position") or "").strip().lower()
        roles.append((kind or position or "auto", str(page.page_type or "Page blanche")))

    return (
        str(page.page_type or "Page blanche").strip().lower(),
        tuple(sorted(set(roles))),
    )


def equivalent_automatic_page_ids(book, anchor_page_id: str) -> list[str]:
    """Retourne les autres pages automatiques éditorialement équivalentes.

    C'est uniquement une proposition de portée. L'utilisateur choisit ensuite
    explicitement s'il veut étendre son contenu.
    """
    anchor_page_id = str(anchor_page_id)
    anchor = book.pages.get(anchor_page_id)
    if anchor is None:
        raise KeyError(anchor_page_id)
    if not is_auto_origin_page(anchor):
        raise ValueError("Cette page n'est pas une page ajoutée automatiquement.")

    signature = _automatic_content_signature(anchor)
    return [
        page_id
        for page_id in book.page_order
        if page_id in book.pages
        and is_auto_origin_page(book.pages[page_id])
        and _automatic_content_signature(book.pages[page_id]) == signature
    ]


def extend_automatic_page_content(book, anchor_page_id: str, page_ids: Iterable[str] | None = None) -> list[str]:
    """Copie volontairement le contenu d'une page auto vers ses équivalentes.

    Les pages touchées deviennent protégées : leur contenu éditorial ne peut
    plus disparaître lors d'un recalcul structurel.
    """
    anchor_page_id = str(anchor_page_id)
    anchor = book.pages.get(anchor_page_id)
    if anchor is None:
        raise KeyError(anchor_page_id)
    if not is_auto_origin_page(anchor):
        raise ValueError("Cette page n'est pas une page ajoutée automatiquement.")
    if not anchor.content:
        raise ValueError("Cette page automatique ne contient encore aucun contenu à étendre.")

    equivalents = set(equivalent_automatic_page_ids(book, anchor_page_id))
    if page_ids is None:
        targets = [page_id for page_id in book.page_order if page_id in equivalents]
    else:
        wanted = {str(value) for value in page_ids}
        targets = [page_id for page_id in book.page_order if page_id in equivalents and page_id in wanted]

    protect_auto_page(anchor)
    changed: list[str] = []
    for page_id in targets:
        page = book.pages[page_id]
        if page_id != anchor_page_id:
            page.content = deepcopy(anchor.content)
            page.modifications = deepcopy(anchor.modifications)
        protect_auto_page(page)
        page.history.append({
            "action": "contenu_page_auto_etendu",
            "source_page_id": anchor_page_id,
        })
        if page_id != anchor_page_id:
            changed.append(page_id)

    book.history.append({
        "action": "contenu_pages_auto_etendu",
        "source_page_id": anchor_page_id,
        "page_ids": list(changed),
    })
    return changed


def prune_similarity_extensions_for_deleted_pages(book, page_ids: Iterable[str]) -> None:
    """Retire des règles étendues les UUID qui n'existent plus.

    Les contraintes déjà matérialisées sur les autres pages restent intactes.
    Si la page de référence d'une extension disparaît, une page membre restante
    devient simplement la nouvelle référence d'interface.
    """

    deleted = {str(value) for value in page_ids}
    if not deleted:
        return

    root = _extension_root(book, create=True)
    items = root.get("items", {})
    if not isinstance(items, dict):
        return

    remove_ids: list[str] = []

    for extension_id, record in list(items.items()):
        if not isinstance(record, dict):
            continue

        page_ids_value = [
            str(value)
            for value in record.get("page_ids", [])
            if str(value) not in deleted and str(value) in book.pages
        ]
        member_ids = [
            str(value)
            for value in record.get("member_page_ids", page_ids_value)
            if str(value) not in deleted and str(value) in book.pages
        ]
        excluded_ids = [
            str(value)
            for value in record.get("excluded_page_ids", [])
            if str(value) not in deleted and str(value) in book.pages
        ]
        preexisting_ids = [
            str(value)
            for value in record.get("preexisting_page_ids", [])
            if str(value) not in deleted and str(value) in book.pages
        ]

        mapping = record.get("pair_anchor_by_member", {})
        if isinstance(mapping, dict):
            record["pair_anchor_by_member"] = {
                str(member): str(anchor)
                for member, anchor in mapping.items()
                if (
                    str(member) not in deleted
                    and str(anchor) not in deleted
                    and str(member) in book.pages
                    and str(anchor) in book.pages
                )
            }

        record["page_ids"] = page_ids_value
        record["member_page_ids"] = member_ids
        record["excluded_page_ids"] = excluded_ids
        record["preexisting_page_ids"] = preexisting_ids

        anchor = str(record.get("anchor_page_id") or "")
        if anchor in deleted or anchor not in book.pages:
            candidates = [value for value in page_ids_value if value in book.pages]
            if candidates:
                record["anchor_page_id"] = candidates[0]
            else:
                remove_ids.append(str(extension_id))

    for extension_id in remove_ids:
        items.pop(extension_id, None)

    if not items:
        book.metadata.pop(EXTENSIONS_KEY, None)
