from __future__ import annotations

"""Recomposition locale et déterministe du texte TomeLinea.

Ce module ne décide pas *quoi* corriger. Il applique une décision déjà prise
(par les règles générales ou par l'utilisateur) puis remet le corps du livre
en composition : largeur utile, hauteur réelle des paragraphes, veuves /
orphelines et report du texte suivant si nécessaire.

Aucune dépendance copyleft n'est ajoutée ici. La mesure passe par
``format_text_layout`` qui utilise Pillow/FreeType et, lorsqu'ils sont
installés, les composants typographiques permissifs choisis par TomeLinea.
"""

from copy import deepcopy
from typing import Any, Iterable
from uuid import uuid4

from src.v4.composition import MARGINS, frame_bounds
from src.v4.domain import PageOrigin, PageV4
from src.v4.format_text_layout import join_layout_lines, measure_text_layout
from src.v4.page_element_roles import ROLE_BODY, page_element_roles
from src.v4.text_rules import text_general_rules

_FLOW_ORDER = "text_recomposition_order"
_MODIFIED = "text_content_modified"
_GENERATED_PAGE = "text_recomposition_generated"
_PARAGRAPH_ID = "text_paragraph_group_id"
_CONTINUATION = "format_flow_continuation"


def _num(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _geometry(element: dict[str, Any]) -> dict[str, Any]:
    value = element.get("geometry")
    if isinstance(value, dict):
        return value
    value = {}
    element["geometry"] = value
    return value


def _metadata(element: dict[str, Any]) -> dict[str, Any]:
    value = element.get("metadata")
    if isinstance(value, dict):
        return value
    value = {}
    element["metadata"] = value
    return value


def _element_bottom(element: dict[str, Any]) -> float:
    geo = _geometry(element)
    return _num(geo.get("y_mm")) + _num(geo.get("height_mm"))


def _sorted(elements: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(
        elements,
        key=lambda element: (
            _num(_metadata(element).get(_FLOW_ORDER), 10**12),
            _num(_geometry(element).get("y_mm")),
            _num(_geometry(element).get("x_mm")),
        ),
    )


def _role_map(book: Any, page_id: str) -> dict[str, str]:
    try:
        return {
            str(element_id): str(value.role)
            for element_id, value in page_element_roles(book, page_id).items()
        }
    except Exception:
        return {}


def body_elements(book: Any, page_id: str) -> list[dict[str, Any]]:
    """Retourne le corps de texte éditorial de la page, dans l'ordre de flux."""
    page = getattr(book, "pages", {}).get(str(page_id))
    if page is None:
        return []
    roles = _role_map(book, str(page_id))
    values: list[dict[str, Any]] = []
    for element in getattr(page, "content", ()):
        if not isinstance(element, dict) or str(element.get("kind", "")).lower() != "text":
            continue
        element_id = str(element.get("id", "") or "")
        meta = _metadata(element)
        # Les éléments déjà identifiés comme corps pendant une recomposition
        # gardent ce rôle même si leur géométrie temporaire change.
        forced_role = str(meta.get("text_recomposition_role", "") or "")
        role = forced_role or roles.get(element_id, "")
        if role == ROLE_BODY:
            meta["text_recomposition_role"] = ROLE_BODY
            values.append(element)
    return _sorted(values)


def ensure_flow_order(book: Any) -> None:
    """Fige l'ordre logique du corps avant le premier déplacement géométrique."""
    counter = 0
    for page_id in list(getattr(book, "page_order", ())):
        page = getattr(book, "pages", {}).get(page_id)
        if page is None:
            continue
        # Lors de la première passe l'ordre visuel Source est l'autorité.
        candidates = body_elements(book, page_id)
        for element in candidates:
            meta = _metadata(element)
            if _FLOW_ORDER not in meta:
                meta[_FLOW_ORDER] = counter
            counter = max(counter + 1, int(_num(meta.get(_FLOW_ORDER), counter)) + 1)




def _set_element_text(element: dict[str, Any], text: str) -> None:
    payload = element.setdefault("payload", {})
    if not isinstance(payload, dict):
        payload = {}
        element["payload"] = payload
    payload["text"] = str(text or "")
    spans = payload.get("spans", [])
    if isinstance(spans, list) and spans:
        first = next((span for span in spans if isinstance(span, dict)), None)
        if first is not None:
            style = dict(first)
            style["text"] = str(text or "")
            style["line_index"] = 0
            payload["spans"] = [style]
    _metadata(element)[_MODIFIED] = True


def _paragraph_identity(element: dict[str, Any]) -> str:
    meta = _metadata(element)
    value = str(meta.get(_PARAGRAPH_ID, "") or "").strip()
    if not value:
        value = str(element.get("id", "") or uuid4())
        meta[_PARAGRAPH_ID] = value
    return value


def _clone_continuation(
    element: dict[str, Any],
    *,
    text: str,
    flow_order: float,
    continuation_index: int,
) -> dict[str, Any]:
    clone = deepcopy(element)
    clone["id"] = str(uuid4())
    _set_element_text(clone, text)
    meta = _metadata(clone)
    meta[_FLOW_ORDER] = float(flow_order)
    meta[_PARAGRAPH_ID] = _paragraph_identity(element)
    meta[_CONTINUATION] = True
    meta["text_recomposition_continuation_index"] = int(continuation_index)
    meta["text_recomposition_role"] = ROLE_BODY
    return clone


def _layout_for_element(book: Any, page_id: str, element: dict[str, Any]) -> tuple[Any, float, float, float, float]:
    frame_x, top, frame_width, frame_height = frame_bounds(book, page_id, MARGINS)
    geo = _geometry(element)
    rules = text_general_rules(book)
    layout = measure_text_layout(
        element,
        frame_width,
        source_geometry=dict(geo),
        rules=rules,
    )
    return layout, frame_x, top, frame_width, frame_height


def _split_for_available_height(
    book: Any,
    page_id: str,
    element: dict[str, Any],
    available_mm: float,
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    """Scinde un paragraphe uniquement à une frontière de ligne admissible."""
    layout, _x, _top, _width, _height = _layout_for_element(book, page_id, element)
    lines = list(layout.lines)
    flags = list(layout.line_hyphenated or tuple(False for _ in lines))
    if len(lines) < 2:
        return None
    line_height = max(0.5, float(layout.line_height_mm))
    max_lines = int(max(0.0, float(available_mm) - 0.4) // line_height)
    rules = text_general_rules(book)
    try:
        orphan_min = max(1, int(rules.get("orphan_min_lines", 2) or 2))
    except (TypeError, ValueError):
        orphan_min = 2
    try:
        widow_min = max(1, int(rules.get("widow_min_lines", 2) or 2))
    except (TypeError, ValueError):
        widow_min = 2
    take = min(max_lines, len(lines) - widow_min)
    if take < orphan_min:
        return None
    if len(lines) - take < widow_min:
        return None

    first_text = join_layout_lines(tuple(lines[:take]), tuple(flags[:take]))
    rest_text = join_layout_lines(tuple(lines[take:]), tuple(flags[take:]))
    if not first_text or not rest_text:
        return None

    meta = _metadata(element)
    base_order = _num(meta.get(_FLOW_ORDER), 0.0)
    continuation_index = int(_num(meta.get("text_recomposition_continuation_index"), 0.0)) + 1
    remainder = _clone_continuation(
        element,
        text=rest_text,
        flow_order=base_order + min(0.9, continuation_index * 0.001),
        continuation_index=continuation_index,
    )
    _set_element_text(element, first_text)
    meta[_PARAGRAPH_ID] = _paragraph_identity(element)
    # La première partie garde son retrait ; la continuation ne l'aura pas.
    first_layout, frame_x, _top, frame_width, _height = _layout_for_element(book, page_id, element)
    geo = _geometry(element)
    geo["x_mm"] = frame_x
    geo["width_mm"] = frame_width
    geo["height_mm"] = max(0.8, float(first_layout.required_height_mm))
    return element, remainder


def _page_after(book: Any, page_id: str) -> Any | None:
    order = list(getattr(book, "page_order", ()))
    try:
        index = order.index(str(page_id))
    except ValueError:
        return None
    if index + 1 >= len(order):
        return None
    return getattr(book, "pages", {}).get(order[index + 1])


def _copy_fixed_text_for_new_page(book: Any, prototype: Any, page: PageV4) -> None:
    """Copie uniquement les éléments répétitifs supérieurs, jamais le corps.

    Le folio n'est volontairement pas copié : le moteur de pagination / sortie
    est l'autorité pour sa valeur. Cette page est marquée pour qu'il puisse le
    reconstruire ensuite.
    """
    roles = _role_map(book, str(getattr(prototype, "id", "")))
    try:
        _x, top, _w, _h = frame_bounds(book, str(getattr(prototype, "id", "")), MARGINS)
    except Exception:
        top = _num(getattr(book.format, "margin_top_mm", 15.0), 15.0)
    for element in getattr(prototype, "content", ()):
        if not isinstance(element, dict) or str(element.get("kind", "")).lower() != "text":
            continue
        element_id = str(element.get("id", "") or "")
        meta = _metadata(element)
        forced_role = str(meta.get("text_recomposition_role", "") or "")
        role = forced_role or roles.get(element_id, "")
        geo = _geometry(element)
        # En-tête courant : élément non-corps au-dessus de la zone utile.
        # Un fragment de corps déjà recomposé reste du corps même si l'analyse
        # éditoriale heuristique le prend momentanément pour un titre.
        if role == ROLE_BODY or _num(geo.get("y_mm")) > top + 1.0:
            continue
        clone = deepcopy(element)
        _metadata(clone)[_MODIFIED] = True
        page.content.append(clone)


def _create_following_text_page(book: Any, prototype: Any) -> Any:
    """Crée une page intérieure uniquement quand le flux n'a plus de destination."""
    order = list(getattr(book, "page_order", ()))
    try:
        index = order.index(str(prototype.id)) + 1
    except (ValueError, AttributeError):
        index = len(order)
    page = PageV4(
        page_type="Page texte",
        title=str(getattr(prototype, "title", "") or ""),
        origin=PageOrigin.TOMELINEA,
        part_id=getattr(prototype, "part_id", None),
    )
    page.metadata[_GENERATED_PAGE] = True
    page.metadata["creation_kind"] = "text_recomposition_auto"
    page.metadata["source_visual_preserved"] = False
    _copy_fixed_text_for_new_page(book, prototype, page)
    book.add_page(page, index=index)
    history = getattr(book, "history", None)
    if isinstance(history, list):
        history.append({
            "action": "page_texte_recomposition_ajoutee",
            "page_id": page.id,
            "after_page_id": str(getattr(prototype, "id", "")),
        })
    return page


def _paragraph_gap(rules: dict[str, Any]) -> float:
    value = rules.get("paragraph_gap_mm")
    return max(0.0, _num(value, 0.0))


def _first_body_y(book: Any, page_id: str, *, body: list[dict[str, Any]] | None = None) -> float:
    """Détermine le début du corps sans déplacer l'en-tête courant."""
    x, top, width, height = frame_bounds(book, page_id, MARGINS)
    values = body if body is not None else body_elements(book, page_id)
    if values:
        current = min(_num(_geometry(element).get("y_mm"), top) for element in values)
        # Une Source peut débuter légèrement sous la marge en raison d'un
        # en-tête courant. On conserve ce départ tant qu'il reste dans le cadre.
        if top - 0.2 <= current <= top + height * 0.35:
            return current

    # Si aucun corps n'est présent, laisser la place aux éléments fixes placés
    # au-dessus du cadre utile (en-tête courant, titre courant...).
    page = getattr(book, "pages", {}).get(page_id)
    fixed_bottom = top
    if page is not None:
        roles = _role_map(book, page_id)
        for element in getattr(page, "content", ()):
            if not isinstance(element, dict) or str(element.get("kind", "")).lower() != "text":
                continue
            if roles.get(str(element.get("id", "") or "")) == ROLE_BODY:
                continue
            geo = _geometry(element)
            y = _num(geo.get("y_mm"))
            bottom = _element_bottom(element)
            if y <= top + height * 0.20 and bottom <= top + height * 0.30:
                fixed_bottom = max(fixed_bottom, bottom + 4.0)
    return fixed_bottom


def recompose_element(book: Any, page_id: str, element: dict[str, Any]) -> dict[str, Any]:
    """Recompose un paragraphe à la largeur *réelle* du bloc de marges."""
    frame_x, _top, frame_width, _frame_height = frame_bounds(book, page_id, MARGINS)
    geo = _geometry(element)
    before = dict(geo)
    rules = text_general_rules(book)
    layout = measure_text_layout(
        element,
        frame_width,
        source_geometry=before,
        rules=rules,
    )
    geo["x_mm"] = float(frame_x)
    geo["width_mm"] = float(frame_width)
    geo["height_mm"] = max(0.8, float(layout.required_height_mm))
    meta = _metadata(element)
    meta[_MODIFIED] = True
    meta["text_recomposition_role"] = ROLE_BODY
    meta["text_recomposition_exact_font"] = bool(layout.exact_font)
    return {
        "before_geometry": before,
        "after_geometry": dict(geo),
        "line_count": len(layout.lines),
        "line_height_mm": float(layout.line_height_mm),
    }


def _mark_moved(element: dict[str, Any], *, from_page: str, to_page: str) -> None:
    meta = _metadata(element)
    meta[_MODIFIED] = True
    meta["text_recomposition_role"] = ROLE_BODY
    history = meta.setdefault("text_recomposition_history", [])
    if isinstance(history, list):
        history.append({"action": "flow_to_next_page", "from_page_id": from_page, "to_page_id": to_page})


def _insert_before_existing_body(page: Any, moved: list[dict[str, Any]], existing: list[dict[str, Any]]) -> None:
    # Les positions sont temporairement utilisées pour conserver l'ordre au
    # moment où page_element_roles est recalculé. L'ordre logique stable reste
    # stocké dans _FLOW_ORDER.
    if existing:
        base = min(_num(_geometry(element).get("y_mm")) for element in existing)
    else:
        base = 0.0
    for index, element in enumerate(moved):
        _geometry(element)["y_mm"] = base - (len(moved) - index) * 0.01
        if element not in page.content:
            page.content.append(element)


def recompose_page_flow(
    book: Any,
    page_id: str,
    *,
    start_y: float | None = None,
    cascade: bool = True,
    _depth: int = 0,
) -> dict[str, Any]:
    """Recompose le corps d'une page et reporte les paragraphes excédentaires.

    Le report se fait par paragraphes entiers. La routine ne tronque jamais un
    bloc et ne réduit jamais arbitrairement police ou marges. Une limite de
    profondeur empêche toute boucle sur un livre incohérent.
    """
    if _depth > max(20, len(getattr(book, "page_order", ())) + 5):
        raise ValueError("La recomposition du texte n'arrive pas à stabiliser la pagination.")
    page = getattr(book, "pages", {}).get(str(page_id))
    if page is None:
        raise ValueError("Page de recomposition introuvable.")

    ensure_flow_order(book)
    frame_x, top, frame_width, frame_height = frame_bounds(book, str(page_id), MARGINS)
    bottom = top + frame_height
    rules = text_general_rules(book)
    gap = _paragraph_gap(rules)
    body = body_elements(book, str(page_id))
    if not body:
        return {"changed": False, "page_id": str(page_id), "moved": 0, "overflow": False}

    y = float(start_y) if start_y is not None else _first_body_y(book, str(page_id), body=body)
    overflow_index: int | None = None
    changed = False

    for index, element in enumerate(body):
        before = dict(_geometry(element))
        info = recompose_element(book, str(page_id), element)
        geo = _geometry(element)
        geo["x_mm"] = frame_x
        geo["width_mm"] = frame_width
        geo["y_mm"] = y
        if dict(geo) != before:
            changed = True
        if _element_bottom(element) > bottom + 0.2:
            overflow_index = index
            break
        y = _element_bottom(element) + gap

    if overflow_index is None:
        return {"changed": changed, "page_id": str(page_id), "moved": 0, "overflow": False}

    if not cascade:
        return {"changed": changed, "page_id": str(page_id), "moved": 0, "overflow": True}

    overflow_element = body[overflow_index]
    available_mm = max(0.0, bottom - _num(_geometry(overflow_element).get("y_mm"), y))

    # Un paragraphe long peut légitimement traverser une page. On ne déplace
    # donc pas systématiquement le bloc entier : si au moins le nombre minimal
    # de lignes requis peut rester en bas de page *et* au moins le minimum
    # veuve peut ouvrir la suivante, on le scinde à une vraie frontière de
    # ligne produite par le compositeur. Les traits de césure purement visuels
    # ne sont jamais écrits dans le contenu logique.
    split = _split_for_available_height(
        book,
        str(page_id),
        overflow_element,
        available_mm,
    )
    if split is not None:
        first_fragment, remainder = split
        first_geo = _geometry(first_fragment)
        first_geo["x_mm"] = frame_x
        first_geo["width_mm"] = frame_width
        first_geo["y_mm"] = y
        if _element_bottom(first_fragment) <= bottom + 0.2:
            moved = [remainder, *body[overflow_index + 1:]]
            # Le premier fragment reste sur la page courante. Seuls les blocs
            # qui le suivent sont retirés avant d'être insérés dans la page
            # suivante.
            for element in body[overflow_index + 1:]:
                try:
                    page.content.remove(element)
                except ValueError:
                    pass
            changed = True
        else:
            # Garde-fou : si les métriques ont changé entre les deux mesures,
            # revenir au report par paragraphe entier plutôt que de tronquer.
            moved = body[overflow_index:]
            for element in moved:
                try:
                    page.content.remove(element)
                except ValueError:
                    pass
    else:
        moved = body[overflow_index:]
        # Pas assez de lignes pour respecter veuve/orpheline : le paragraphe
        # entier passe à la page suivante.
        for element in moved:
            try:
                page.content.remove(element)
            except ValueError:
                pass

    following = _page_after(book, str(page_id))
    if following is None:
        following = _create_following_text_page(book, page)
    existing = body_elements(book, str(following.id))
    _insert_before_existing_body(following, moved, existing)
    for element in moved:
        _mark_moved(element, from_page=str(page_id), to_page=str(following.id))

    next_start = _first_body_y(book, str(following.id), body=existing) if existing else None
    nested = recompose_page_flow(
        book,
        str(following.id),
        start_y=next_start,
        cascade=True,
        _depth=_depth + 1,
    )
    return {
        "changed": True,
        "page_id": str(page_id),
        "moved": len(moved) + int(nested.get("moved", 0) or 0),
        "overflow": bool(nested.get("overflow", False)),
        "next_page_id": str(following.id),
    }


def attach_heading_to_next_page(book: Any, issue: dict[str, Any], heading: dict[str, Any]) -> dict[str, Any]:
    """Garde un titre avec le début du texte qu'il annonce, puis recompose."""
    page_id = str(issue.get("page_id", "") or "")
    page = getattr(book, "pages", {}).get(page_id)
    if page is None:
        raise ValueError("La page du titre est introuvable.")
    following = _page_after(book, page_id)
    if following is None:
        following = _create_following_text_page(book, page)

    ensure_flow_order(book)
    body = body_elements(book, str(following.id))
    if not body:
        raise ValueError("TomeLinea ne trouve pas le paragraphe annoncé par ce titre.")

    before_geometry = dict(_geometry(heading))
    try:
        page.content.remove(heading)
    except ValueError:
        raise ValueError("Le titre n'est plus présent sur sa page d'origine.")

    frame_x, top, frame_width, _height = frame_bounds(book, str(following.id), MARGINS)
    first_y = _first_body_y(book, str(following.id), body=body)
    title_geo = _geometry(heading)
    title_h = max(0.8, _num(title_geo.get("height_mm"), 3.0))
    gap = max(2.0, _paragraph_gap(text_general_rules(book)))
    desired_y = max(top, first_y - title_h - gap)
    needed_shift = max(0.0, desired_y + title_h + gap - first_y)

    title_geo["x_mm"] = max(frame_x, min(_num(title_geo.get("x_mm"), frame_x), frame_x + frame_width))
    title_geo["y_mm"] = desired_y
    meta = _metadata(heading)
    meta[_MODIFIED] = True
    meta["keep_with_next_lines"] = max(2, int(text_general_rules(book).get("heading_keep_lines", 2) or 2))
    meta["moved_by_tomelinea"] = True
    following.content.append(heading)

    # Si le titre doit prendre une place supplémentaire, on recompose le corps
    # juste après lui ; le moteur reporte automatiquement la fin de page.
    body_start = first_y + needed_shift
    if needed_shift <= 0.0:
        body_start = desired_y + title_h + gap
    flow = recompose_page_flow(book, str(following.id), start_y=body_start, cascade=True)
    return {
        "changed": True,
        "kind": "title_orphan",
        "page_id": str(following.id),
        "element_id": str(heading.get("id", "") or ""),
        "before_line": "Titre isolé en bas de page",
        "after_line": "Titre gardé avec le texte qu'il annonce",
        "geometry": dict(title_geo),
        "before_geometry": before_geometry,
        "flow": flow,
    }


def recombine_split_paragraph(
    book: Any,
    *,
    previous_page: Any,
    previous_element: dict[str, Any],
    next_page: Any,
    next_element: dict[str, Any],
) -> dict[str, Any]:
    """Réunit deux fragments Source d'un même paragraphe puis recompose.

    Le fragment isolé de la page précédente est déplacé logiquement au début de
    la page suivante. La nouvelle hauteur et les reports éventuels sont calculés
    par le même moteur que le reste du corps.
    """
    previous_payload = previous_element.get("payload", {})
    next_payload = next_element.get("payload", {})
    if not isinstance(previous_payload, dict) or not isinstance(next_payload, dict):
        raise ValueError("Le contenu du paragraphe est invalide.")
    previous_text = str(previous_payload.get("text", "") or "").strip()
    next_text = str(next_payload.get("text", "") or "").strip()
    if not previous_text or not next_text:
        raise ValueError("Le paragraphe coupé n'a pas pu être reconstitué.")

    ensure_flow_order(book)
    # Les deux fragments sont consécutifs d'un même paragraphe : préserver un
    # trait d'union lexical, mais supprimer une césure de fin de ligne Source.
    if previous_text.endswith("-") and next_text[:1].islower():
        previous_text = previous_text[:-1]
        combined = previous_text + next_text
    else:
        combined = previous_text + " " + next_text

    before_text = next_text
    next_payload["text"] = combined
    spans = next_payload.get("spans", [])
    if isinstance(spans, list) and spans:
        first = next((span for span in spans if isinstance(span, dict)), None)
        if first is not None:
            style = dict(first)
            style["text"] = combined
            style["line_index"] = 0
            next_payload["spans"] = [style]
    _metadata(next_element)[_MODIFIED] = True
    _metadata(next_element)["widow_orphan_corrected"] = True

    try:
        previous_page.content.remove(previous_element)
    except ValueError:
        raise ValueError("Le fragment isolé n'est plus présent sur la page précédente.")

    # Le paragraphe réuni doit ouvrir la page suivante. Sa recomposition peut
    # pousser les blocs suivants, sans jamais les superposer ou les tronquer.
    current_start = _num(_geometry(next_element).get("y_mm"), _first_body_y(book, str(next_page.id)))
    flow = recompose_page_flow(book, str(next_page.id), start_y=current_start, cascade=True)
    return {
        "changed": True,
        "page_id": str(next_page.id),
        "element_id": str(next_element.get("id", "") or ""),
        "before_text": before_text,
        "after_text": combined,
        "geometry": dict(_geometry(next_element)),
        "flow": flow,
    }
