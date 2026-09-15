from __future__ import annotations

"""Règles physiques des quatre faces de couverture TomeLinea V4.

Les faces de couverture ne sont pas des pages éditoriales ordinaires :
- 1re et 2e restent au tout début du livre ;
- 3e et 4e restent à la toute fin ;
- aucune page ne peut être insérée à l'extérieur de ces deux paires ;
- les faces sont protégées contre suppression/déplacement/contraintes.

Le rôle physique est mémorisé dans ``metadata['physical_cover_face']`` dès
qu'il est reconnu afin qu'un renommage ultérieur de ``page_type`` ne fasse
pas perdre la protection.
"""

import re
import unicodedata
from typing import Any


FRONT_COVER = "front"
INSIDE_FRONT_COVER = "inside_front"
INSIDE_BACK_COVER = "inside_back"
BACK_COVER = "back"

COVER_FACES = (
    FRONT_COVER,
    INSIDE_FRONT_COVER,
    INSIDE_BACK_COVER,
    BACK_COVER,
)


_FACE_LABELS = {
    FRONT_COVER: "1re de couverture",
    INSIDE_FRONT_COVER: "2e de couverture",
    INSIDE_BACK_COVER: "3e de couverture",
    BACK_COVER: "4e de couverture",
}


def _norm(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = "".join(
        char
        for char in unicodedata.normalize("NFD", text)
        if unicodedata.category(char) != "Mn"
    )
    text = text.replace("’", "'")
    text = re.sub(r"[_\-]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _infer_face_from_text(value: Any) -> str | None:
    text = _norm(value)
    if not text:
        return None

    # Variantes historiques et libellés V4 actuels.
    if text in {
        "couverture",
        "1re couverture",
        "1re de couverture",
        "1ere couverture",
        "1ere de couverture",
        "premiere couverture",
        "premiere de couverture",
    }:
        return FRONT_COVER

    if text in {
        "2e couverture",
        "2e de couverture",
        "2eme couverture",
        "2eme de couverture",
        "deuxieme couverture",
        "deuxieme de couverture",
    }:
        return INSIDE_FRONT_COVER

    if text in {
        "3e couverture",
        "3e de couverture",
        "3eme couverture",
        "3eme de couverture",
        "troisieme couverture",
        "troisieme de couverture",
    }:
        return INSIDE_BACK_COVER

    if text in {
        "4e couverture",
        "4e de couverture",
        "4eme couverture",
        "4eme de couverture",
        "quatrieme couverture",
        "quatrieme de couverture",
    }:
        return BACK_COVER

    return None


def cover_face(page: Any) -> str | None:
    metadata = getattr(page, "metadata", None)
    if isinstance(metadata, dict):
        stored = str(metadata.get("physical_cover_face") or "").strip()
        if stored in COVER_FACES:
            return stored
        # Une page explicitement libérée d'une attribution automatique ne doit
        # pas être reclassée aussitôt à cause de son ancien titre Source.
        if metadata.get("released_from_cover") or metadata.get("cover_candidate_for"):
            return None

    # page_type est la source métier principale. Le titre n'est qu'un secours
    # pour les anciens projets qui ne portaient pas encore le rôle physique.
    face = _infer_face_from_text(getattr(page, "page_type", ""))
    if face is not None:
        return face

    return _infer_face_from_text(getattr(page, "title", ""))


def mark_cover_face(page: Any) -> str | None:
    face = cover_face(page)
    if face is None:
        return None

    metadata = getattr(page, "metadata", None)
    if isinstance(metadata, dict):
        metadata["physical_cover_face"] = face
        metadata["physical_cover_protected"] = True
        metadata["physical_cover_label"] = _FACE_LABELS[face]
        # Les quatre faces ne participent pas à la parité des pages intérieures.
        metadata["physical_parity_exempt"] = True

    # Le rôle physique doit être explicite dans toute l'interface, même pour
    # les anciens projets qui utilisaient simplement « Couverture ».
    if hasattr(page, "page_type"):
        page.page_type = _FACE_LABELS[face]

    return face


def is_cover_face(page: Any) -> bool:
    return cover_face(page) is not None


def cover_label(page: Any) -> str:
    face = cover_face(page)
    return _FACE_LABELS.get(face, "couverture")


def cover_ids(book: Any) -> dict[str, str]:
    result: dict[str, str] = {}
    for page_id in list(getattr(book, "page_order", ())):
        page = book.pages.get(page_id)
        if page is None:
            continue
        face = mark_cover_face(page)
        if face is not None and face not in result:
            result[face] = page_id
    return result


def normalize_cover_structure(book: Any) -> bool:
    """Répare un ancien ordre où des pages ont dépassé les couvertures.

    Aucun contenu n'est supprimé : les pages éventuellement placées avant la
    1re ou après la 4e sont simplement replacées dans l'intérieur du livre,
    en conservant leur ordre relatif. Les deux paires physiques redeviennent
    alors : 1re + 2e | intérieur | 3e + 4e.
    """

    order = list(getattr(book, "page_order", ()))
    if not order:
        return False

    by_face: dict[str, str] = {}
    for page_id in order:
        page = book.pages.get(page_id)
        if page is None:
            continue
        face = mark_cover_face(page)
        if face is not None and face not in by_face:
            by_face[face] = page_id

    fixed_ids = {page_id for page_id in by_face.values()}
    middle = [page_id for page_id in order if page_id not in fixed_ids]

    leading = [
        by_face[face]
        for face in (FRONT_COVER, INSIDE_FRONT_COVER)
        if face in by_face
    ]
    trailing = [
        by_face[face]
        for face in (INSIDE_BACK_COVER, BACK_COVER)
        if face in by_face
    ]

    new_order = leading + middle + trailing
    if new_order == order:
        return False

    book.page_order = new_order
    history = getattr(book, "history", None)
    if isinstance(history, list):
        history.append(
            {
                "action": "structure_couvertures_reparee",
                "reason": "faces_physiques_aux_extremites",
            }
        )
    return True


def cover_structure_issues(book: Any) -> list[str]:
    """Retourne les incohérences physiques de couverture sans modifier le livre."""

    order = list(getattr(book, "page_order", ()))
    if not order:
        return []

    roles: dict[str, list[str]] = {face: [] for face in COVER_FACES}
    for page_id in order:
        page = book.pages.get(page_id)
        if page is None:
            continue
        face = cover_face(page)
        if face is not None:
            roles[face].append(page_id)

    issues: list[str] = []

    for face, ids in roles.items():
        if len(ids) > 1:
            issues.append(f"Plusieurs pages portent le rôle {_FACE_LABELS[face]}.")

    front = roles[FRONT_COVER][0] if roles[FRONT_COVER] else None
    inside_front = roles[INSIDE_FRONT_COVER][0] if roles[INSIDE_FRONT_COVER] else None
    inside_back = roles[INSIDE_BACK_COVER][0] if roles[INSIDE_BACK_COVER] else None
    back = roles[BACK_COVER][0] if roles[BACK_COVER] else None

    if front is not None and order[0] != front:
        issues.append("La 1re de couverture doit rester la première face du livre.")

    if back is not None and order[-1] != back:
        issues.append("La 4e de couverture doit rester la dernière face du livre.")

    if front is not None and inside_front is not None:
        if order.index(inside_front) != order.index(front) + 1:
            issues.append("Aucune page ne peut être placée entre la 1re et la 2e de couverture.")

    if inside_back is not None and back is not None:
        if order.index(back) != order.index(inside_back) + 1:
            issues.append("Aucune page ne peut être placée entre la 3e et la 4e de couverture.")

    return issues


def protected_cover_boundaries(book: Any) -> set[int]:
    """Frontières où une page éditoriale ne peut jamais être insérée."""

    order = list(getattr(book, "page_order", ()))
    ids = cover_ids(book)
    protected: set[int] = set()

    front = ids.get(FRONT_COVER)
    inside_front = ids.get(INSIDE_FRONT_COVER)
    inside_back = ids.get(INSIDE_BACK_COVER)
    back = ids.get(BACK_COVER)

    if front is not None:
        protected.update(range(0, order.index(front) + 1))
        # Avant la 1re : index 0. Le range couvre aussi un ancien ordre invalide.
        protected.add(0)

    if front is not None and inside_front is not None:
        left = order.index(front)
        right = order.index(inside_front)
        if right == left + 1:
            protected.add(right)

    if inside_back is not None and back is not None:
        left = order.index(inside_back)
        right = order.index(back)
        if right == left + 1:
            protected.add(right)

    if back is not None:
        back_index = order.index(back)
        protected.update(range(back_index + 1, len(order) + 1))
        protected.add(len(order))

    return protected


def interior_insertion_bounds(book: Any) -> tuple[int, int]:
    """Retourne [min, max] des frontières où des pages intérieures peuvent vivre."""

    order = list(getattr(book, "page_order", ()))
    ids = cover_ids(book)

    lower = 0
    if ids.get(INSIDE_FRONT_COVER) in order:
        lower = order.index(ids[INSIDE_FRONT_COVER]) + 1
    elif ids.get(FRONT_COVER) in order:
        lower = order.index(ids[FRONT_COVER]) + 1

    upper = len(order)
    if ids.get(INSIDE_BACK_COVER) in order:
        upper = order.index(ids[INSIDE_BACK_COVER])
    elif ids.get(BACK_COVER) in order:
        upper = order.index(ids[BACK_COVER])

    if upper < lower:
        upper = lower

    return lower, upper


def relative_insertion_index(book: Any, anchor_page_id: str, position: str) -> int:
    """Frontière logique avant/après une page en respectant les couvertures."""

    value = str(position or "").strip().lower()
    if value not in {"before", "after"}:
        raise ValueError("Position attendue : before ou after.")

    order = list(getattr(book, "page_order", ()))
    if anchor_page_id not in order:
        raise KeyError(anchor_page_id)

    page = book.pages[anchor_page_id]
    face = cover_face(page)
    lower, upper = interior_insertion_bounds(book)

    if face in {FRONT_COVER, INSIDE_FRONT_COVER}:
        if value == "before":
            raise ValueError("Aucune page ne peut être ajoutée avant ou dans la couverture avant.")
        return lower

    if face in {INSIDE_BACK_COVER, BACK_COVER}:
        if value == "after":
            raise ValueError("Aucune page ne peut être ajoutée après ou dans la couverture arrière.")
        return upper

    index = order.index(anchor_page_id)
    candidate = index if value == "before" else index + 1

    if candidate < lower:
        candidate = lower
    if candidate > upper:
        candidate = upper

    return candidate


def can_insert_relative(book: Any, anchor_page_id: str, position: str) -> bool:
    try:
        relative_insertion_index(book, anchor_page_id, position)
    except (KeyError, ValueError):
        return False
    return True



def is_generated_cover_placeholder(page: Any) -> bool:
    metadata = getattr(page, "metadata", None)
    return bool(
        isinstance(metadata, dict)
        and metadata.get("generated_cover_placeholder")
    )


def _new_cover_placeholder(
    face: str,
    *,
    part_id: str | None,
) -> Any:
    if face not in {INSIDE_FRONT_COVER, INSIDE_BACK_COVER}:
        raise ValueError("Seules les 2e et 3e de couverture peuvent être générées ici.")

    # Import local pour éviter de créer une dépendance circulaire au chargement.
    from src.v4.domain import PageOrigin, PageV4

    label = _FACE_LABELS[face]
    page = PageV4(
        page_type=label,
        title=label,
        origin=PageOrigin.TOMELINEA,
        source=None,
        part_id=part_id,
    )
    page.metadata["physical_cover_face"] = face
    page.metadata["physical_cover_protected"] = True
    page.metadata["physical_parity_exempt"] = True
    page.metadata["physical_cover_label"] = label
    page.metadata["generated_cover_placeholder"] = True

    # 2.38A : une 2e/3e absente de la Source est une vraie page physique
    # créée par TomeLinea. Elle appartient donc explicitement aux pages auto.
    # ``automatic_structure`` reste réservé aux pages AV/AP.
    page.metadata["automatic_origin"] = True
    page.metadata["automatic_kind"] = "physical_cover"
    page.metadata["creation_kind"] = "automatic_physical_cover"
    page.metadata["automatic_page"] = True

    # L'emplacement physique existe immédiatement, mais TomeLinea ne décide
    # jamais seul si la face est blanche ou si la page voisine doit l'occuper.
    page.metadata["cover_content_status"] = "pending"
    page.metadata["cover_confirmation"] = "pending"
    return page

def ensure_inside_cover_faces(book: Any) -> bool:
    """Garantit l'existence physique des 2e et 3e de couverture.

    Les emplacements existent toujours, mais restent ``pending`` tant que
    l'utilisateur n'a pas confirmé soit la page voisine, soit une face blanche.
    Aucun contenu auteur n'est supprimé et aucune page voisine n'est consommée
    automatiquement.
    """

    order = list(getattr(book, "page_order", ()))
    if not order:
        return False

    ids = cover_ids(book)
    changed = False

    front_id = ids.get(FRONT_COVER)
    back_id = ids.get(BACK_COVER)

    if front_id is not None and ids.get(INSIDE_FRONT_COVER) is None:
        front = book.pages[front_id]
        placeholder = _new_cover_placeholder(
            INSIDE_FRONT_COVER,
            part_id=getattr(front, "part_id", None),
        )
        insert_at = book.page_order.index(front_id) + 1
        book.pages[placeholder.id] = placeholder
        book.page_order.insert(insert_at, placeholder.id)
        changed = True

    # Recalcul nécessaire car l'ajout de la 2e a décalé les indices.
    ids = cover_ids(book)

    if back_id is not None and ids.get(INSIDE_BACK_COVER) is None:
        back = book.pages[back_id]
        placeholder = _new_cover_placeholder(
            INSIDE_BACK_COVER,
            part_id=getattr(back, "part_id", None),
        )
        insert_at = book.page_order.index(back_id)
        book.pages[placeholder.id] = placeholder
        book.page_order.insert(insert_at, placeholder.id)
        changed = True

    if changed:
        normalize_cover_structure(book)

    return changed


def _new_outer_cover_placeholder(face: str) -> Any:
    """Crée l'emplacement physique obligatoire d'une 1re ou 4e absente."""

    if face not in {FRONT_COVER, BACK_COVER}:
        raise ValueError("Seules les 1re et 4e de couverture sont créées ici.")

    from src.v4.domain import PageOrigin, PageV4

    label = _FACE_LABELS[face]
    page = PageV4(
        page_type=label,
        title=label,
        origin=PageOrigin.TOMELINEA,
        source=None,
        part_id=None,
    )
    page.metadata["physical_cover_face"] = face
    page.metadata["physical_cover_protected"] = True
    page.metadata["physical_parity_exempt"] = True
    page.metadata["physical_cover_label"] = label
    page.metadata["required_outer_cover_placeholder"] = True
    page.metadata["cover_content_status"] = "missing_source"
    page.metadata["cover_confirmation"] = "missing_source"
    return page


def ensure_physical_cover_faces(book: Any) -> bool:
    """Garantit la structure physique minimale 1re + 2e | Livre | 3e + 4e.

    Si 1re/4e sont absentes, TomeLinea réserve leur emplacement physique à
    compléter. Si 2e/3e sont absentes, elles sont créées comme pages automatiques.
    """

    changed = False
    ids = cover_ids(book)

    if ids.get(FRONT_COVER) is None:
        page = _new_outer_cover_placeholder(FRONT_COVER)
        book.pages[page.id] = page
        book.page_order.insert(0, page.id)
        changed = True

    ids = cover_ids(book)
    if ids.get(BACK_COVER) is None:
        page = _new_outer_cover_placeholder(BACK_COVER)
        book.pages[page.id] = page
        book.page_order.append(page.id)
        changed = True

    if ensure_inside_cover_faces(book):
        changed = True

    if normalize_cover_structure(book):
        changed = True

    return changed

def _clear_cover_role(page: Any, *, fallback_page_type: str = "Page") -> None:
    metadata = getattr(page, "metadata", None)
    previous_type = None
    if isinstance(metadata, dict):
        previous_type = metadata.pop("cover_previous_page_type", None)
        metadata.pop("physical_cover_face", None)
        metadata.pop("physical_cover_protected", None)
        metadata.pop("physical_parity_exempt", None)
        metadata.pop("physical_cover_label", None)
        metadata.pop("generated_cover_placeholder", None)
        metadata.pop("cover_content_status", None)
        metadata["released_from_cover"] = True

    if hasattr(page, "page_type"):
        page.page_type = str(previous_type or fallback_page_type)


def _assign_cover_role(page: Any, face: str) -> None:
    if face not in {INSIDE_FRONT_COVER, INSIDE_BACK_COVER}:
        raise ValueError("Seules les 2e et 3e de couverture sont réattribuables.")

    metadata = getattr(page, "metadata", None)
    if isinstance(metadata, dict):
        if "cover_previous_page_type" not in metadata:
            metadata["cover_previous_page_type"] = str(
                getattr(page, "page_type", "") or "Page"
            )
        metadata["physical_cover_face"] = face
        metadata["physical_cover_protected"] = True
        metadata["physical_parity_exempt"] = True
        metadata["physical_cover_label"] = _FACE_LABELS[face]
        metadata["cover_assigned_by_user"] = True
        metadata.pop("released_from_cover", None)
        metadata.pop("cover_analysis_suggestion", None)
        metadata["cover_confirmation"] = "content"
        metadata["cover_content_status"] = "content"
        metadata.pop("generated_cover_placeholder", None)
        metadata.pop("cover_candidate_for", None)

    if hasattr(page, "page_type"):
        page.page_type = _FACE_LABELS[face]


def adjacent_inside_cover_candidate(book: Any, face: str) -> str | None:
    """Page du corps immédiatement voisine d'une 2e/3e de couverture."""

    if face not in {INSIDE_FRONT_COVER, INSIDE_BACK_COVER}:
        return None

    ids = cover_ids(book)
    cover_id = ids.get(face)
    if cover_id is None or cover_id not in book.page_order:
        return None

    index = book.page_order.index(cover_id)
    candidate_index = index + 1 if face == INSIDE_FRONT_COVER else index - 1
    if candidate_index < 0 or candidate_index >= len(book.page_order):
        return None

    candidate_id = book.page_order[candidate_index]
    candidate = book.pages.get(candidate_id)
    if candidate is None or is_cover_face(candidate):
        return None

    return candidate_id


def assign_page_as_inside_cover(
    book: Any,
    face: str,
    candidate_id: str,
) -> str:
    """Affecte explicitement une page du corps à la 2e/3e de couverture.

    Cette opération est volontairement distincte de l'analyse : aucune page
    n'est promue en couverture sans action de l'utilisateur.

    Si l'emplacement actuel est un blanc généré par TomeLinea, il disparaît.
    S'il contient un vrai contenu, ce contenu est conservé et reprend la place
    occupée par la page choisie dans le corps. Aucun contenu n'est supprimé.
    """

    if face not in {INSIDE_FRONT_COVER, INSIDE_BACK_COVER}:
        raise ValueError("Seules les 2e et 3e de couverture sont réattribuables.")

    ensure_inside_cover_faces(book)
    ids = cover_ids(book)
    current_id = ids.get(face)

    candidate_id = str(candidate_id or "")
    if current_id is None:
        raise ValueError("Face de couverture introuvable.")
    if candidate_id not in getattr(book, "pages", {}):
        raise ValueError("Page choisie introuvable.")
    if candidate_id == current_id:
        raise ValueError("Choisissez une page du corps du livre.")

    candidate = book.pages[candidate_id]
    if is_cover_face(candidate):
        raise ValueError("Une autre face de couverture ne peut pas être utilisée ici.")

    current = book.pages[current_id]
    current_index = book.page_order.index(current_id)
    candidate_index = book.page_order.index(candidate_id)
    cover_part_id = getattr(current, "part_id", None)
    body_part_id = getattr(candidate, "part_id", None)

    if is_generated_cover_placeholder(current):
        book.page_order.remove(current_id)
        book.pages.pop(current_id, None)
    else:
        # Échange physique : le contenu anciennement classé en couverture
        # rejoint le corps à la place de la page explicitement choisie.
        book.page_order[current_index], book.page_order[candidate_index] = (
            book.page_order[candidate_index],
            book.page_order[current_index],
        )
        _clear_cover_role(current)
        current.part_id = body_part_id

    _assign_cover_role(candidate, face)
    candidate.part_id = cover_part_id

    normalize_cover_structure(book)
    return candidate.id


def use_adjacent_page_as_inside_cover(book: Any, face: str) -> str:
    """Affecte la page du corps immédiatement voisine à la 2e/3e."""

    candidate_id = adjacent_inside_cover_candidate(book, face)
    if candidate_id is None:
        direction = "suivante" if face == INSIDE_FRONT_COVER else "précédente"
        raise ValueError(f"Aucune page {direction} du corps n'est disponible.")

    return assign_page_as_inside_cover(
        book,
        face,
        candidate_id,
    )


def blank_inside_cover(book: Any, face: str) -> str:
    """Remet la 2e/3e de couverture en blanc sans perdre son contenu actuel."""

    if face not in {INSIDE_FRONT_COVER, INSIDE_BACK_COVER}:
        raise ValueError("Seules les 2e et 3e de couverture peuvent être remises en blanc.")

    ensure_inside_cover_faces(book)
    ids = cover_ids(book)
    current_id = ids.get(face)
    if current_id is None:
        raise ValueError("Face de couverture introuvable.")

    current = book.pages[current_id]
    if is_generated_cover_placeholder(current):
        metadata = getattr(current, "metadata", None)
        if isinstance(metadata, dict):
            metadata["cover_confirmation"] = "blank"
            metadata["cover_content_status"] = "blank"
        return current.id

    current_index = book.page_order.index(current_id)
    candidate_id = adjacent_inside_cover_candidate(book, face)
    body_part_id = (
        getattr(book.pages[candidate_id], "part_id", None)
        if candidate_id is not None
        else None
    )
    cover_part_id = getattr(current, "part_id", None)

    _clear_cover_role(current)
    current.part_id = body_part_id

    placeholder = _new_cover_placeholder(face, part_id=cover_part_id)
    placeholder.metadata["cover_confirmation"] = "blank"
    placeholder.metadata["cover_content_status"] = "blank"
    book.pages[placeholder.id] = placeholder

    if face == INSIDE_FRONT_COVER:
        # Le blanc reprend la place physique de la 2e ; l'ancien contenu
        # devient immédiatement la première page du corps.
        book.page_order.insert(current_index, placeholder.id)
    else:
        # L'ancien contenu devient immédiatement la dernière page du corps,
        # puis vient le blanc de 3e avant la 4e.
        book.page_order.insert(current_index + 1, placeholder.id)

    normalize_cover_structure(book)
    return placeholder.id



def inside_cover_confirmation_status(page: Any) -> str | None:
    """État de décision utilisateur pour une 2e/3e de couverture."""

    face = cover_face(page)
    if face not in {INSIDE_FRONT_COVER, INSIDE_BACK_COVER}:
        return None

    metadata = getattr(page, "metadata", None)
    if not isinstance(metadata, dict):
        return "pending"

    value = str(metadata.get("cover_confirmation") or "").strip().lower()
    if value in {"pending", "blank", "content"}:
        return value

    if metadata.get("cover_assigned_by_user"):
        return "content"

    return "pending"


def is_inside_cover_pending(page: Any) -> bool:
    return inside_cover_confirmation_status(page) == "pending"


def prepare_inside_cover_confirmation(book: Any) -> bool:
    """Migre les anciennes décisions automatiques vers un choix explicite.

    Une page auteur précédemment classée automatiquement en 2e/3e redevient
    candidate du corps. TomeLinea place alors un emplacement physique
    ``à confirmer`` à sa place. Les choix déjà faits explicitement par
    l'utilisateur sont conservés.
    """

    changed = False

    ids = cover_ids(book)
    for face in (INSIDE_FRONT_COVER, INSIDE_BACK_COVER):
        page_id = ids.get(face)
        if page_id is None:
            continue
        page = book.pages.get(page_id)
        if page is None:
            continue

        metadata = getattr(page, "metadata", None)
        if not isinstance(metadata, dict):
            continue

        confirmation = str(metadata.get("cover_confirmation") or "").strip().lower()
        explicitly_confirmed = bool(metadata.get("cover_assigned_by_user")) or (
            confirmation in {"blank", "content"}
        )

        if is_generated_cover_placeholder(page):
            if not explicitly_confirmed:
                metadata["cover_confirmation"] = "pending"
                metadata["cover_content_status"] = "pending"
            continue

        if explicitly_confirmed:
            continue

        # Ancienne analyse automatique : on ne la transforme plus en décision.
        _clear_cover_role(page, fallback_page_type="Page")
        page.metadata["cover_candidate_for"] = face
        page.metadata["cover_analysis_suggestion"] = True
        changed = True

    if ensure_physical_cover_faces(book):
        changed = True

    ids = cover_ids(book)
    for face in (INSIDE_FRONT_COVER, INSIDE_BACK_COVER):
        page_id = ids.get(face)
        if page_id is None:
            continue
        cover_page = book.pages.get(page_id)
        if cover_page is None:
            continue

        metadata = getattr(cover_page, "metadata", None)
        if isinstance(metadata, dict) and is_generated_cover_placeholder(cover_page):
            if str(metadata.get("cover_confirmation") or "").strip().lower() not in {
                "blank",
                "content",
            }:
                metadata["cover_confirmation"] = "pending"
                metadata["cover_content_status"] = "pending"

        candidate_id = adjacent_inside_cover_candidate(book, face)
        if candidate_id is not None:
            candidate = book.pages.get(candidate_id)
            candidate_meta = getattr(candidate, "metadata", None)
            if isinstance(candidate_meta, dict):
                if is_inside_cover_pending(cover_page):
                    candidate_meta["cover_candidate_for"] = face
                else:
                    candidate_meta.pop("cover_candidate_for", None)

    if normalize_cover_structure(book):
        changed = True

    return changed


def inside_cover_candidate_face(book: Any, page_id: str) -> str | None:
    """Retourne la face en attente dont ``page_id`` est la candidate visible."""

    if page_id not in getattr(book, "pages", {}):
        return None

    ids = cover_ids(book)
    for face in (INSIDE_FRONT_COVER, INSIDE_BACK_COVER):
        cover_id = ids.get(face)
        if cover_id is None:
            continue
        cover_page = book.pages.get(cover_id)
        if cover_page is None or not is_inside_cover_pending(cover_page):
            continue
        if adjacent_inside_cover_candidate(book, face) == page_id:
            return face

    return None


def inside_cover_confirmation_issues(book: Any) -> list[dict[str, Any]]:
    """Décisions de couverture restant à prendre, pour le garde-fou Anomalies."""

    issues: list[dict[str, Any]] = []
    ids = cover_ids(book)

    for face in (INSIDE_FRONT_COVER, INSIDE_BACK_COVER):
        cover_id = ids.get(face)
        if cover_id is None:
            continue
        cover_page = book.pages.get(cover_id)
        if cover_page is None or not is_inside_cover_pending(cover_page):
            continue

        candidate_id = adjacent_inside_cover_candidate(book, face)
        candidate = book.pages.get(candidate_id) if candidate_id else None
        try:
            page_number = (
                book.page_order.index(candidate_id) + 1
                if candidate_id is not None
                else None
            )
        except ValueError:
            page_number = None

        label = _FACE_LABELS[face]
        issues.append(
            {
                "kind": "inside_cover_confirmation",
                "face": face,
                "cover_page_id": cover_id,
                "candidate_page_id": candidate_id,
                "candidate_part_id": getattr(candidate, "part_id", None),
                "candidate_page_number": page_number,
                "label": f"{label} à confirmer",
                "message": (
                    f"Vérifier la page candidate puis confirmer {label} "
                    "ou laisser cette face blanche."
                ),
            }
        )

    return issues
