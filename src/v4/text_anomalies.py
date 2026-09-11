from __future__ import annotations

"""TomeLinea V4 - analyse déterministe des anomalies de texte.

Le moteur ne reçoit aucune "vérité attendue". Il observe uniquement le livre
composé (texte, lignes, styles et géométrie) et retourne des anomalies en
langage courant. Les règles de cette première version privilégient les cas à
forte confiance afin de limiter les fausses alertes.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from statistics import median
from typing import Any, Iterable
import re

from src.v4.text_compositor import (
    controlled_hyphenation_reason as _engine_hyphenation_reason,
    load_french_hyphenator,
)


@dataclass(frozen=True, slots=True)
class _Line:
    index: int
    text: str
    geometry: dict[str, float]


@dataclass(frozen=True, slots=True)
class _Node:
    page_id: str
    source_page: int | None
    element_id: str
    text: str
    geometry: dict[str, float]
    lines: tuple[_Line, ...]
    size_pt: float
    font_family: str
    bold: bool
    page_width_mm: float
    page_height_mm: float
    page_type: str
    reference_frame: str
    origin: str
    rule_exceptions: frozenset[str]
    text_alignment: str


@dataclass(frozen=True, slots=True)
class _Profile:
    body_size_pt: float
    body_font_family: str
    repeated_margin_texts: frozenset[str]


def _float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _norm_font(value: Any) -> str:
    text = str(value or "").strip().lower()
    if "+" in text and len(text.split("+", 1)[0]) <= 8:
        text = text.split("+", 1)[1]
    for token in (
        "bolditalic", "bold-italic", "bold", "italic", "regular", "roman",
        "oblique", "book",
    ):
        text = text.replace(token, "")
    return " ".join(text.replace("-", " ").replace("_", " ").split())


def _is_bold_font(value: Any) -> bool:
    text = str(value or "").lower()
    return "bold" in text or "black" in text or "semibold" in text


def _source_page(element: dict[str, Any], page: Any) -> int | None:
    source_ref = element.get("source_ref", {})
    if isinstance(source_ref, dict):
        value = source_ref.get("source_page")
        try:
            if value is not None:
                return int(value)
        except (TypeError, ValueError):
            pass
    metadata = getattr(page, "metadata", {})
    if isinstance(metadata, dict):
        for key in ("source_page", "source_page_number"):
            try:
                value = metadata.get(key)
                if value is not None:
                    return int(value)
            except (TypeError, ValueError):
                pass
    return None


def _node_lines(
    element: dict[str, Any],
    *,
    page_width_mm: float,
    page_height_mm: float,
) -> tuple[_Line, ...]:
    payload = element.get("payload", {})
    if not isinstance(payload, dict):
        payload = {}
    metadata = element.get("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
    current_text_modified = bool(metadata.get("text_content_modified", False))

    spans = payload.get("spans", ())
    if not isinstance(spans, (list, tuple)):
        spans = ()
    # Après une correction TomeLinea, le texte de payload est l'autorité. Les
    # spans Source restent conservés pour leur style, mais leur texte ne doit
    # plus réintroduire l'ancienne version dans l'analyse.
    if current_text_modified:
        spans = ()

    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for span in spans:
        if not isinstance(span, dict):
            continue
        try:
            line_index = int(span.get("line_index", 0) or 0)
        except (TypeError, ValueError):
            line_index = 0
        grouped[line_index].append(span)

    lines: list[_Line] = []
    for line_index in sorted(grouped):
        line_spans = sorted(
            grouped[line_index],
            key=lambda item: _float((item.get("bbox_norm") or [0])[0] if isinstance(item.get("bbox_norm"), (list, tuple)) and item.get("bbox_norm") else 0),
        )
        text = "".join(str(span.get("text", "")) for span in line_spans).rstrip("\r\n")
        boxes = [
            span.get("bbox_norm")
            for span in line_spans
            if isinstance(span.get("bbox_norm"), (list, tuple)) and len(span.get("bbox_norm")) >= 4
        ]
        if boxes:
            x0 = min(_float(box[0]) for box in boxes) * page_width_mm
            y0 = min(_float(box[1]) for box in boxes) * page_height_mm
            x1 = max(_float(box[2]) for box in boxes) * page_width_mm
            y1 = max(_float(box[3]) for box in boxes) * page_height_mm
            geometry = {
                "x_mm": x0,
                "y_mm": y0,
                "width_mm": max(0.0, x1 - x0),
                "height_mm": max(0.0, y1 - y0),
            }
        else:
            geometry = dict(element.get("geometry", {}) or {})
        if text.strip():
            lines.append(_Line(index=line_index, text=text, geometry=geometry))

    if lines:
        return tuple(lines)

    text = str(payload.get("text", "") or "")
    if not text.strip():
        return ()
    geometry = dict(element.get("geometry", {}) or {})
    raw_lines = [line for line in text.splitlines() if line.strip()] or [text]
    # Estimation simple de la géométrie des lignes corrigées : suffisante pour
    # conserver un repère visuel cohérent sans prétendre reconstruire ici le
    # moteur de composition complet.
    count = max(1, len(raw_lines))
    total_h = max(0.1, _float(geometry.get("height_mm"), 0.1))
    line_h = total_h / count
    base_y = _float(geometry.get("y_mm"))
    line_geometry = []
    for index in range(count):
        line_geometry.append({
            "x_mm": _float(geometry.get("x_mm")),
            "y_mm": base_y + index * line_h,
            "width_mm": _float(geometry.get("width_mm")),
            "height_mm": line_h,
        })
    return tuple(
        _Line(index=index, text=line, geometry=line_geometry[index])
        for index, line in enumerate(raw_lines)
    )


def _make_node(page: Any, element: dict[str, Any], book: Any) -> _Node | None:
    if str(element.get("kind", "")).lower() != "text":
        return None
    payload = element.get("payload", {})
    if not isinstance(payload, dict):
        return None
    text = str(payload.get("text", "") or "").strip()
    if not text:
        return None
    geometry = dict(element.get("geometry", {}) or {})
    page_width = _float(getattr(book.format, "width_mm", 0.0), 0.0)
    page_height = _float(getattr(book.format, "height_mm", 0.0), 0.0)
    spans = payload.get("spans", ())
    if not isinstance(spans, (list, tuple)):
        spans = ()
    sizes = [_float(span.get("size")) for span in spans if isinstance(span, dict) and _float(span.get("size")) > 0]
    fonts = [str(span.get("font", "")) for span in spans if isinstance(span, dict) and str(span.get("font", ""))]
    size = float(median(sizes)) if sizes else _float(payload.get("size_pt"), 0.0)
    family_counts = Counter(_norm_font(font) for font in fonts if _norm_font(font))
    family = family_counts.most_common(1)[0][0] if family_counts else ""
    bold = any(_is_bold_font(font) for font in fonts)
    return _Node(
        page_id=str(page.id),
        source_page=_source_page(element, page),
        element_id=str(element.get("id", "") or ""),
        text=text,
        geometry={
            "x_mm": _float(geometry.get("x_mm")),
            "y_mm": _float(geometry.get("y_mm")),
            "width_mm": _float(geometry.get("width_mm")),
            "height_mm": _float(geometry.get("height_mm")),
        },
        lines=_node_lines(element, page_width_mm=page_width, page_height_mm=page_height),
        size_pt=size,
        font_family=family,
        bold=bold,
        page_width_mm=page_width,
        page_height_mm=page_height,
        page_type=str(getattr(page, "page_type", "") or ""),
        reference_frame=str(element.get("reference_frame", "") or "").strip().lower(),
        origin=str((element.get("metadata", {}) or {}).get("origin", "") or "").strip().lower()
        if isinstance(element.get("metadata", {}), dict) else "",
        rule_exceptions=frozenset(
            str(key) for key, enabled in (
                ((element.get("metadata", {}) or {}).get("text_rule_exceptions", {}) or {}).items()
                if isinstance((element.get("metadata", {}) or {}).get("text_rule_exceptions", {}), dict)
                else ()
            ) if enabled
        ),
        text_alignment=str((element.get("metadata", {}) or {}).get("text_alignment", "") or "").strip().lower()
        if isinstance(element.get("metadata", {}), dict) else "",
    )


def _collect_nodes(book: Any) -> tuple[list[_Node], dict[str, list[_Node]]]:
    all_nodes: list[_Node] = []
    by_page: dict[str, list[_Node]] = {}
    for page in book.ordered_pages():
        page_nodes: list[_Node] = []
        for element in getattr(page, "content", ()):
            if not isinstance(element, dict):
                continue
            node = _make_node(page, element, book)
            if node is not None:
                page_nodes.append(node)
                all_nodes.append(node)
        page_nodes.sort(key=lambda n: (n.geometry["y_mm"], n.geometry["x_mm"]))
        by_page[str(page.id)] = page_nodes
    return all_nodes, by_page


def _build_profile(nodes: Iterable[_Node]) -> _Profile:
    nodes = list(nodes)
    long_nodes = [
        node for node in nodes
        if len(node.text) >= 75
        and node.size_pt > 0
        and node.geometry["y_mm"] > 12.0
        and node.geometry["y_mm"] + node.geometry["height_mm"] < node.page_height_mm - 12.0
    ]
    sizes = [node.size_pt for node in long_nodes]
    body_size = float(median(sizes)) if sizes else 10.0

    near_body = [
        node for node in long_nodes
        if body_size * 0.78 <= node.size_pt <= body_size * 1.22
    ]
    family_counts = Counter(node.font_family for node in near_body if node.font_family)
    body_family = family_counts.most_common(1)[0][0] if family_counts else ""

    margin_counts: Counter[str] = Counter()
    for node in nodes:
        top = node.geometry["y_mm"] <= 12.0
        bottom = node.geometry["y_mm"] + node.geometry["height_mm"] >= node.page_height_mm - 12.0
        if not (top or bottom):
            continue
        norm = " ".join(node.text.lower().split())
        if norm and len(norm) <= 80:
            margin_counts[norm] += 1
    repeated = frozenset(text for text, count in margin_counts.items() if count >= 3)
    return _Profile(body_size_pt=body_size, body_font_family=body_family, repeated_margin_texts=repeated)


def _is_running_margin(node: _Node, profile: _Profile) -> bool:
    top = node.geometry["y_mm"] <= 12.0
    bottom = node.geometry["y_mm"] + node.geometry["height_mm"] >= node.page_height_mm - 12.0
    if not (top or bottom):
        return False
    norm = " ".join(node.text.lower().split())
    if norm in profile.repeated_margin_texts:
        return True
    if re.fullmatch(r"[\[(]?\s*\d{1,5}\s*[\])]?$", norm):
        return True
    return node.size_pt > 0 and node.size_pt <= profile.body_size_pt * 0.86 and len(node.text) <= 80


def _title_like(node: _Node, profile: _Profile) -> bool:
    text = node.text.strip()
    if not text or len(text) > 120:
        return False
    metadata_style = False
    # The first engine is visual: explicit metadata is not required.
    if node.size_pt >= profile.body_size_pt * 1.35:
        metadata_style = True
    if node.bold and node.size_pt >= profile.body_size_pt * 1.16:
        metadata_style = True
    if text.isupper() and any(ch.isalpha() for ch in text) and len(text) <= 90:
        metadata_style = True
    return metadata_style


def _body_like(node: _Node, profile: _Profile) -> bool:
    if _is_running_margin(node, profile) or _title_like(node, profile):
        return False
    if len(node.text.strip()) < 18:
        return False
    if node.size_pt <= 0:
        return True
    return profile.body_size_pt * 0.65 <= node.size_pt <= profile.body_size_pt * 1.75


def _union_geometry(items: Iterable[dict[str, float]]) -> dict[str, float] | None:
    boxes = [item for item in items if isinstance(item, dict)]
    if not boxes:
        return None
    x0 = min(_float(box.get("x_mm")) for box in boxes)
    y0 = min(_float(box.get("y_mm")) for box in boxes)
    x1 = max(_float(box.get("x_mm")) + _float(box.get("width_mm")) for box in boxes)
    y1 = max(_float(box.get("y_mm")) + _float(box.get("height_mm")) for box in boxes)
    return {"x_mm": x0, "y_mm": y0, "width_mm": max(0.0, x1-x0), "height_mm": max(0.0, y1-y0)}


def _intersection(a: dict[str, float], b: dict[str, float]) -> dict[str, float] | None:
    x0=max(_float(a.get("x_mm")),_float(b.get("x_mm")))
    y0=max(_float(a.get("y_mm")),_float(b.get("y_mm")))
    x1=min(_float(a.get("x_mm"))+_float(a.get("width_mm")),_float(b.get("x_mm"))+_float(b.get("width_mm")))
    y1=min(_float(a.get("y_mm"))+_float(a.get("height_mm")),_float(b.get("y_mm"))+_float(b.get("height_mm")))
    if x1 <= x0 or y1 <= y0:
        return None
    return {"x_mm":x0,"y_mm":y0,"width_mm":x1-x0,"height_mm":y1-y0}


def _issue(
    node: _Node,
    kind: str,
    *,
    title: str,
    term: str,
    why: str,
    proposal: str,
    geometry: dict[str, float] | None = None,
    suffix: str = "",
    confidence: float = 0.95,
    extra_element_ids: tuple[str, ...] = (),
) -> dict[str, Any]:
    suffix_part = f":{suffix}" if suffix else ""
    element_ids = tuple(dict.fromkeys((node.element_id,) + tuple(extra_element_ids)))
    return {
        "id": f"{node.page_id}:{':'.join(element_ids)}:{kind}{suffix_part}",
        "type": kind,
        "kind": kind,
        "page_id": node.page_id,
        "source_page": node.source_page,
        "element_id": node.element_id,
        "element_ids": element_ids,
        "title": title,
        "technical_term": term,
        "why": why,
        "proposal": proposal,
        "geometry": dict(geometry or node.geometry),
        "confidence": round(float(confidence), 3),
        "engine": "tomelinea.text_anomalies",
        "engine_version": "2",
    }


def _hyphenation_parts(line_text: str, next_text: str) -> tuple[str, str]:
    left_match = re.search(r"([A-Za-zÀ-ÖØ-öø-ÿŒœÆæ]+)-\s*$", str(line_text or ""))
    right_match = re.match(r"^\s*([a-zà-öø-ÿœæ]+)", str(next_text or ""))
    return (left_match.group(1) if left_match else "", right_match.group(1) if right_match else "")


def _controlled_hyphenation_reason(
    node: _Node,
    index: int,
    left: str,
    right: str,
    *,
    min_word_length: int = 7,
    min_left: int = 3,
    min_right: int = 3,
    max_consecutive: int = 2,
    allow_last_word: bool = False,
) -> str | None:
    """Contrôle une césure avec les motifs français lorsqu'ils sont disponibles.

    Les heuristiques historiques ne servent plus qu'à compléter les règles
    linguistiques (enchaînement de césures et fin de page).
    """
    if not left or not right:
        return "La coupure du mot n'a pas pu être vérifiée."

    def ends_with_hyphen(pos: int) -> bool:
        return 0 <= pos < len(node.lines) - 1 and bool(
            node.lines[pos].text.rstrip().endswith("-")
            and re.match(r"^[a-zà-öø-ÿœæ]", node.lines[pos + 1].text.lstrip())
        )

    consecutive = 1
    if ends_with_hyphen(index - 1):
        consecutive += 1
    if ends_with_hyphen(index + 1):
        consecutive += 1

    node_bottom = node.geometry["y_mm"] + node.geometry["height_mm"]
    near_page_bottom = node_bottom >= node.page_height_mm - 18.0
    near_block_end = index >= max(0, len(node.lines) - 3)
    next_line_text = node.lines[index + 1].text.strip() if index + 1 < len(node.lines) else ""
    right_word_only = bool(
        right
        and re.fullmatch(
            re.escape(right) + r"[\s\.,;:!?…»”'\"]*",
            next_line_text,
            flags=re.IGNORECASE,
        )
    )

    return _engine_hyphenation_reason(
        left=left,
        right=right,
        hyphenator=load_french_hyphenator(),
        min_word_length=min_word_length,
        min_left=min_left,
        min_right=min_right,
        consecutive_count=consecutive,
        max_consecutive=max_consecutive,
        near_page_end=bool(near_page_bottom and near_block_end),
        is_last_word=bool(right_word_only and not allow_last_word),
    )


def _line_regex_issues(
    node: _Node,
    *,
    hyphenation_policy: str = "",
    hyphen_min_word_length: int = 7,
    hyphen_min_left: int = 3,
    hyphen_min_right: int = 3,
    hyphen_max_consecutive: int = 2,
    hyphen_last_word: bool = False,
) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for line in node.lines:
        text = line.text
        if re.search(r"(?<=\S) {2,}(?=\S)", text):
            result.append(_issue(
                node, "double_space", suffix=f"line{line.index}", geometry=line.geometry,
                title="Il y a un espace en trop ici", term="espace double",
                why="Deux espaces se suivent alors qu'un seul suffit entre ces mots.",
                proposal="Ramener cet espacement à un seul espace.",
                confidence=0.995,
            ))
        if re.search(r"\s+[,.](?!\.)", text):
            result.append(_issue(
                node, "space_before_punctuation", suffix=f"line{line.index}", geometry=line.geometry,
                title="Il y a un espace inutile avant ce signe", term="espace avant ponctuation",
                why="En français, une virgule ou un point suit directement le mot qui le précède.",
                proposal="Supprimer l'espace placé juste avant ce signe.",
                confidence=0.995,
            ))
        if (
            re.search(r"(?<=[A-Za-zÀ-ÖØ-öø-ÿ0-9])[.!?](?=[A-ZÀ-ÖØ-Þ])", text)
            or re.search(r"(?<=[A-Za-zÀ-ÖØ-öø-ÿ0-9]),(?=[A-Za-zÀ-ÖØ-öø-ÿ])", text)
        ):
            result.append(_issue(
                node, "missing_space_after_punctuation", suffix=f"line{line.index}", geometry=line.geometry,
                title="Il manque un espace après ce signe", term="espacement de ponctuation",
                why="Deux mots ou deux phrases se retrouvent collés autour de la ponctuation.",
                proposal="Ajouter l'espace manquant après ce signe.",
                confidence=0.99,
            ))
        # En français, ces espaces existent déjà visuellement dans la Source ;
        # TomeLinea les rend simplement insécables pour empêcher la ponctuation
        # de se retrouver seule en début de ligne.
        if (
            re.search(r" (?=[;:!?»])", text)
            or re.search(r"(?<=«) ", text)
        ):
            result.append(_issue(
                node, "french_nonbreaking_space", suffix=f"line{line.index}", geometry=line.geometry,
                title="Cet espace doit rester attaché à la ponctuation",
                term="espace insécable",
                why="Une coupure de ligne à cet endroit pourrait isoler un signe de ponctuation.",
                proposal="Conserver le même espacement visuel mais empêcher la coupure de ligne.",
                confidence=0.998,
            ))

    policy = str(hyphenation_policy or "").lower()
    if policy != "undecided":
        for index, line in enumerate(node.lines[:-1]):
            nxt = node.lines[index + 1]
            if not (line.text.rstrip().endswith("-") and re.match(r"^[a-zà-öø-ÿ]", nxt.text.lstrip())):
                continue
            left, right = _hyphenation_parts(line.text, nxt.text)
            reason = _controlled_hyphenation_reason(
                node,
                index,
                left,
                right,
                min_word_length=hyphen_min_word_length,
                min_left=hyphen_min_left,
                min_right=hyphen_min_right,
                max_consecutive=hyphen_max_consecutive,
                allow_last_word=hyphen_last_word,
            ) if policy == "controlled" else None
            if policy == "controlled" and reason is None:
                # Césure ordinaire : elle respecte la règle « contrôlées ».
                continue
            geometry = _union_geometry((line.geometry, nxt.geometry))
            issue = _issue(
                node, "hyphenation", suffix=f"line{line.index}", geometry=geometry,
                title=(
                    "Cette césure mérite d'être corrigée"
                    if policy == "controlled"
                    else "Une césure est présente alors que le livre est réglé sans césures"
                    if policy == "forbid"
                    else "Ce mot est coupé en fin de ligne"
                ),
                term="césure",
                why=(
                    reason
                    if policy == "controlled" and reason
                    else "La règle générale du livre demande de ne pas couper les mots en fin de ligne."
                    if policy == "forbid"
                    else "La coupure peut être correcte, mais elle mérite d'être vérifiée car elle interrompt le mot."
                ),
                proposal="Recomposer la ligne pour remettre le mot entier sans modifier le texte.",
                confidence=0.985 if policy in {"forbid", "controlled"} else 0.97,
            )
            issue["line_index"] = int(line.index)
            issue["hyphen_left"] = left
            issue["hyphen_right"] = right
            issue["hyphenation_policy"] = policy or "source"
            result.append(issue)

        # Un caractère de césure discrétionnaire est interdit en mode « sans
        # césures ». En mode contrôlé il est accepté tant qu'il n'est pas
        # effectivement rendu dans une situation problématique ci-dessus.
        if "\u00ad" in node.text and policy != "controlled":
            issue = _issue(
                node, "hyphenation", suffix="soft", title=(
                    "Une césure est présente alors que le livre est réglé sans césures"
                    if policy == "forbid" else "Ce mot est coupé en fin de ligne"
                ), term="césure",
                why=(
                    "La règle générale du livre demande de ne pas couper les mots en fin de ligne."
                    if policy == "forbid" else "Une césure est présente dans ce passage."
                ),
                proposal="Retirer cette césure et recomposer le passage.", confidence=0.98,
            )
            issue["hyphenation_policy"] = policy or "source"
            result.append(issue)
    return result


def _margin_overflow_geometry(node: _Node, book: Any, tolerance_mm: float = 0.8) -> dict[str, float] | None:
    """Retourne uniquement la partie du texte qui déborde des marges du Livre.

    Une zone Page/Fond perdu explicitement créée par l'utilisateur est une
    exception volontaire. Les fragments issus de l'analyse Source restent en
    revanche contrôlés par rapport aux marges détectées du Livre.
    """
    if node.reference_frame in {"page", "bleed"} and node.origin != "analysis_source":
        return None
    try:
        from src.v4.composition import MARGINS, frame_bounds
        left, top, width, height = frame_bounds(book, node.page_id, MARGINS)
        right = float(left) + float(width)
        bottom = float(top) + float(height)
    except Exception:
        return None

    x = node.geometry["x_mm"]
    y = node.geometry["y_mm"]
    r = x + node.geometry["width_mm"]
    b = y + node.geometry["height_mm"]
    t = max(0.0, float(tolerance_mm))
    boxes: list[dict[str, float]] = []
    if x < float(left) - t:
        boxes.append({"x_mm": x, "y_mm": y, "width_mm": max(0.1, min(r, float(left)) - x), "height_mm": max(0.1, b-y)})
    if r > right + t:
        boxes.append({"x_mm": max(x, right), "y_mm": y, "width_mm": max(0.1, r-max(x, right)), "height_mm": max(0.1, b-y)})
    if y < float(top) - t:
        boxes.append({"x_mm": x, "y_mm": y, "width_mm": max(0.1, r-x), "height_mm": max(0.1, min(b, float(top))-y)})
    if b > bottom + t:
        boxes.append({"x_mm": x, "y_mm": max(y, bottom), "width_mm": max(0.1, r-x), "height_mm": max(0.1, b-max(y, bottom))})
    return _union_geometry(boxes) if boxes else None


def text_issue_still_present(book: Any, issue: dict[str, Any] | None) -> bool:
    """Vérifie qu'un problème précis existe encore après intervention."""
    if book is None or not isinstance(issue, dict):
        return False
    issue_id = str(issue.get("id", issue.get("key", "")) or "")
    kind = str(issue.get("type", issue.get("kind", "")) or "")
    page_id = str(issue.get("page_id", "") or "")
    element_id = str(issue.get("element_id", "") or "")
    current = analyze_book_text_anomalies(book)
    if issue_id and any(str(item.get("id", "") or "") == issue_id for item in current):
        return True
    # Pour les problèmes géométriques ou de bloc, l'identifiant ne comporte
    # pas de ligne : une anomalie du même type sur le même élément est le même
    # problème, même si sa géométrie a légèrement bougé.
    if kind in {
        "text_outside_margins", "text_too_close_edge", "style_outlier", "text_not_justified",
        "title_orphan", "text_overlap", "short_line_run", "orphan_line", "widow",
    }:
        return any(
            str(item.get("type", "") or "") == kind
            and str(item.get("page_id", "") or "") == page_id
            and str(item.get("element_id", "") or "") == element_id
            for item in current
        )
    return False


def analyze_book_text_anomalies(book: Any) -> list[dict[str, Any]]:
    """Analyse uniquement les problèmes réellement utiles à l'utilisateur.

    Les incohérences géométriques que TomeLinea doit empêcher par construction
    (bloc courant qui sort des marges, blocs qui se chevauchent spontanément)
    ne sont pas présentées comme des « anomalies éditoriales ». Elles relèvent
    des tests internes du moteur de composition.

    Le parcours utilisateur conserve les défauts réalistes d'un manuscrit ou
    d'une composition : micro-typographie, règle générale non respectée,
    césures, styles locaux accidentels, titres isolés et veuves/orphelines.
    """
    if book is None:
        return []
    nodes, by_page = _collect_nodes(book)
    if not nodes:
        return []
    profile = _build_profile(nodes)
    issues: list[dict[str, Any]] = []

    metadata = getattr(book, "metadata", {})
    general_rules = metadata.get("text_general_rules", {}) if isinstance(metadata, dict) else {}
    if not isinstance(general_rules, dict):
        general_rules = {}
    rules_confirmed = bool(general_rules.get("confirmed", False))
    alignment_rule = str(general_rules.get("alignment", "") or "").lower() if rules_confirmed else ""
    hyphenation_policy = str(general_rules.get("hyphenation", "undecided") or "undecided").lower() if rules_confirmed else "undecided"
    try:
        hyphen_min_word_length = max(4, int(general_rules.get("hyphen_min_word_length", 7) or 7))
    except (TypeError, ValueError):
        hyphen_min_word_length = 7
    try:
        hyphen_min_left = max(2, int(general_rules.get("hyphen_min_left", 3) or 3))
    except (TypeError, ValueError):
        hyphen_min_left = 3
    try:
        hyphen_min_right = max(2, int(general_rules.get("hyphen_min_right", 3) or 3))
    except (TypeError, ValueError):
        hyphen_min_right = 3
    try:
        hyphen_max_consecutive = max(0, int(general_rules.get("hyphen_max_consecutive", 2) or 2))
    except (TypeError, ValueError):
        hyphen_max_consecutive = 2
    hyphen_last_word = bool(general_rules.get("hyphen_last_word", False))
    expected_font = _norm_font(general_rules.get("font_family", ""))
    try:
        expected_size = float(general_rules.get("font_size_pt") or 0.0)
    except (TypeError, ValueError):
        expected_size = 0.0

    # 1) Défauts du texte courant et écarts aux règles générales.
    for node in nodes:
        if not _body_like(node, profile):
            continue
        issues.extend(_line_regex_issues(
            node,
            hyphenation_policy=hyphenation_policy,
            hyphen_min_word_length=hyphen_min_word_length,
            hyphen_min_left=hyphen_min_left,
            hyphen_min_right=hyphen_min_right,
            hyphen_max_consecutive=hyphen_max_consecutive,
            hyphen_last_word=hyphen_last_word,
        ))

        if (
            alignment_rule == "justify"
            and "alignment" not in node.rule_exceptions
            and node.text_alignment != "justify"
            and len(node.lines) >= 4
            and node.page_type.lower() not in {"tableau", "sommaire", "galerie"}
        ):
            widths = [max(0.0, line.geometry.get("width_mm", 0.0)) for line in node.lines]
            widest = max(widths, default=0.0)
            non_last = widths[:-1]
            if widest > 20.0 and non_last:
                full_ratio = sum(1 for width in non_last if width >= widest * 0.94) / len(non_last)
                short_ratio = sum(1 for width in non_last if width <= widest * 0.88) / len(non_last)
                if full_ratio < 0.55 and short_ratio >= 0.35:
                    issues.append(_issue(
                        node, "text_not_justified",
                        geometry=_union_geometry(line.geometry for line in node.lines) or node.geometry,
                        title="Ce paragraphe n'est pas justifié",
                        term="justification",
                        why="Le texte courant du livre est réglé pour être aligné sur les deux marges.",
                        proposal="Justifier automatiquement ce paragraphe en conservant sa police et sa taille.",
                        confidence=0.96,
                    ))

        # Une modification locale de police/taille après copier-coller est un
        # cas fréquent. On compare d'abord à la règle générale validée, puis au
        # profil dominant si la règle n'a pas de valeur exploitable.
        size_reference = expected_size if rules_confirmed and expected_size > 0 else 0.0
        font_reference = expected_font if rules_confirmed else ""
        size_outlier = (
            len(node.text) >= 60
            and node.size_pt > 0
            and size_reference > 0
            and (
                node.size_pt > size_reference * 1.22
                or node.size_pt < size_reference * 0.82
            )
        )
        font_outlier = bool(
            len(node.text) >= 60
            and node.font_family
            and font_reference
            and node.font_family != font_reference
        )
        if (
            (size_outlier or font_outlier)
            and "style" not in node.rule_exceptions
        ):
            detail = (
                "Sa police est différente de celle du texte courant."
                if font_outlier and not size_outlier
                else "Sa taille est différente de celle du texte courant."
                if size_outlier and not font_outlier
                else "Sa police et sa taille sont différentes de celles du texte courant."
            )
            issues.append(_issue(
                node, "style_outlier",
                title="Ce paragraphe n’a pas la même apparence que le texte courant",
                term="mise en forme locale",
                why=detail,
                proposal="Rétablir automatiquement la règle générale de ce texte si cette différence n'est pas volontaire.",
                confidence=0.96,
            ))

    # 2) Titre isolé en bas de page : problème classique de composition.
    for _page_id, page_nodes in by_page.items():
        for node in page_nodes:
            if not _title_like(node, profile):
                continue
            bottom = node.geometry["y_mm"] + node.geometry["height_mm"]
            if bottom < node.page_height_mm * 0.76:
                continue
            following_body = any(
                _body_like(other, profile)
                and other.geometry["y_mm"] >= bottom + 2.0
                for other in page_nodes
                if other.element_id != node.element_id
            )
            if not following_body:
                issues.append(_issue(
                    node, "title_orphan",
                    title="Ce titre est isolé en bas de la page",
                    term="titre orphelin",
                    why="Le texte qu'il annonce commence seulement sur la page suivante.",
                    proposal="Garder ce titre avec au moins le début du paragraphe suivant.",
                    confidence=0.97,
                ))

    # 3) Une seule ligne de paragraphe au passage de page.
    by_source: dict[int, list[_Node]] = defaultdict(list)
    for node in nodes:
        if node.source_page is not None and _body_like(node, profile):
            by_source[int(node.source_page)].append(node)
    for source_page, page_nodes in by_source.items():
        page_nodes.sort(key=lambda n: (n.geometry["y_mm"], n.geometry["x_mm"]))
        if not page_nodes:
            continue
        last = page_nodes[-1]
        next_nodes = sorted(
            by_source.get(source_page + 1, []),
            key=lambda n: (n.geometry["y_mm"], n.geometry["x_mm"]),
        )
        if not next_nodes:
            continue
        first_next = next_nodes[0]
        last_is_single = len(last.lines) == 1
        next_is_single = len(first_next.lines) == 1
        last_low = last.geometry["y_mm"] + last.geometry["height_mm"] >= last.page_height_mm * 0.82
        next_high = first_next.geometry["y_mm"] <= first_next.page_height_mm * 0.17
        unfinished = not re.search(r"[.!?…][\"'»)]?\s*$", last.text.strip())
        continuation = bool(re.match(r"^[a-zà-öø-ÿ]", first_next.text.strip()))
        if last_is_single and next_is_single and last_low and next_high and unfinished and continuation:
            issues.append(_issue(
                last, "orphan_line",
                title="Une seule ligne de ce paragraphe reste en bas de la page",
                term="orpheline",
                why="Le paragraphe commence par une seule ligne avant de continuer sur la page suivante.",
                proposal="Rééquilibrer la composition pour garder au moins deux lignes ensemble.",
                confidence=0.96,
            ))
            issues.append(_issue(
                first_next, "widow",
                title="Une seule ligne de ce paragraphe se retrouve en haut de la page",
                term="veuve",
                why="Cette ligne termine seule un paragraphe commencé sur la page précédente.",
                proposal="Rééquilibrer la composition pour garder au moins deux lignes ensemble.",
                confidence=0.96,
            ))

    dedup: dict[tuple[Any, ...], dict[str, Any]] = {}
    for issue in issues:
        geo = issue.get("geometry", {}) or {}
        key = (
            issue.get("page_id"),
            issue.get("type"),
            round(_float(geo.get("x_mm")), 1),
            round(_float(geo.get("y_mm")), 1),
        )
        current = dedup.get(key)
        if current is None or _float(issue.get("confidence")) > _float(current.get("confidence")):
            dedup[key] = issue

    page_rank = {str(page.id): index for index, page in enumerate(book.ordered_pages())}
    return sorted(
        dedup.values(),
        key=lambda issue: (
            page_rank.get(str(issue.get("page_id", "")), 10**9),
            _float((issue.get("geometry") or {}).get("y_mm")),
            str(issue.get("type", "")),
        ),
    )


def book_body_text_size(book: Any) -> float:
    """Taille dominante du texte courant, utilisée seulement comme repère manuel."""
    if book is None:
        return 10.0
    nodes, _ = _collect_nodes(book)
    if not nodes:
        return 10.0
    return float(_build_profile(nodes).body_size_pt)


def anomalies_by_page(book: Any) -> dict[str, list[dict[str, Any]]]:
    result: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for issue in analyze_book_text_anomalies(book):
        result[str(issue.get("page_id", ""))].append(issue)
    return dict(result)

# Compatibilité : « sûres » désigne les corrections immuables historiques.
SAFE_TEXT_CORRECTION_KINDS = frozenset({
    "double_space",
    "space_before_punctuation",
    "missing_space_after_punctuation",
    "french_nonbreaking_space",
})

AUTOMATIC_TEXT_CORRECTION_KINDS = frozenset(set(SAFE_TEXT_CORRECTION_KINDS) | {
    "text_not_justified",
    "style_outlier",
    "hyphenation",
    "title_orphan",
    "orphan_line",
    "widow",
})


def safe_text_correction_supported(issue: dict[str, Any] | None, book: Any = None) -> bool:
    """Vrai lorsque « Corriger » peut réellement exécuter la correction proposée."""
    if not isinstance(issue, dict):
        return False
    kind = str(issue.get("type", issue.get("kind", "")) or "").lower()
    if kind not in AUTOMATIC_TEXT_CORRECTION_KINDS:
        return False
    if kind == "hyphenation" and book is not None:
        metadata = getattr(book, "metadata", {})
        rules = metadata.get("text_general_rules", {}) if isinstance(metadata, dict) else {}
        policy = str(rules.get("hyphenation", "") or "").lower() if isinstance(rules, dict) else ""
        return policy in {"forbid", "controlled"}
    return kind != "hyphenation" or book is None


def _safe_text_transform(kind: str, text: str) -> str:
    """Transformations micro-typographiques volontairement conservatrices."""
    value = str(text or "")
    if kind == "double_space":
        return re.sub(r"(?<=\S) {2,}(?=\S)", " ", value)
    if kind == "space_before_punctuation":
        return re.sub(r"\s+([,.])(?!\.)", r"\1", value)
    if kind == "missing_space_after_punctuation":
        value = re.sub(
            r"(?<=[A-Za-zÀ-ÖØ-öø-ÿ0-9])([.!?])(?=[A-ZÀ-ÖØ-Þ])",
            r"\1 ",
            value,
        )
        return re.sub(
            r"(?<=[A-Za-zÀ-ÖØ-öø-ÿ0-9]),(?=[A-Za-zÀ-ÖØ-öø-ÿ])",
            ", ",
            value,
        )
    if kind == "french_nonbreaking_space":
        value = re.sub(r" (?=[;:!?»])", "\u00a0", value)
        value = re.sub(r"(?<=«) ", "\u00a0", value)
        return value
    return value


def _issue_line_index(issue: dict[str, Any]) -> int | None:
    value = issue.get("line_index")
    try:
        if value is not None:
            return int(value)
    except (TypeError, ValueError):
        pass
    issue_id = str(issue.get("id", issue.get("key", "")) or "")
    match = re.search(r":line(\d+)(?:$|:)", issue_id)
    return int(match.group(1)) if match else None


def _correct_span_boundary(kind: str, left: str, right: str) -> tuple[str, str]:
    """Corrige un défaut situé exactement entre deux spans sans perdre leurs styles."""
    if not left or not right:
        return left, right

    if kind == "double_space":
        trailing = len(left) - len(left.rstrip(" "))
        leading = len(right) - len(right.lstrip(" "))
        if trailing + leading >= 2:
            before = left[:-trailing] if trailing else left
            after = right[leading:] if leading else right
            if before and after and not before[-1].isspace() and not after[0].isspace():
                return before + " ", after

    if kind == "space_before_punctuation":
        if left.endswith((" ", "\t")) and right.lstrip().startswith((",", ".")):
            return left.rstrip(" \t"), right

    if kind == "missing_space_after_punctuation":
        first = right[0]
        last = left[-1]
        if not first.isspace():
            if last in ".!?" and re.match(r"[A-ZÀ-ÖØ-Þ]", first):
                return left + " ", right
            if last == "," and re.match(r"[A-Za-zÀ-ÖØ-öø-ÿ]", first):
                return left + " ", right

    if kind == "french_nonbreaking_space":
        if left.endswith(" ") and right.startswith((";", ":", "!", "?", "»")):
            return left[:-1] + "\u00a0", right
        if left.endswith("«") and right.startswith(" "):
            return left, "\u00a0" + right[1:]

    return left, right


def apply_manual_text_size(book: Any, issue: dict[str, Any], size_pt: float) -> dict[str, Any]:
    """Modifie la taille de la zone ciblée pendant une correction manuelle."""
    if book is None or not isinstance(issue, dict):
        raise ValueError("Problème de texte invalide.")
    try:
        value = float(size_pt)
    except (TypeError, ValueError) as exc:
        raise ValueError("Taille de texte invalide.") from exc
    if value < 4.0 or value > 96.0:
        raise ValueError("La taille doit rester comprise entre 4 et 96 pt.")
    page_id = str(issue.get("page_id", "") or "")
    element_id = str(issue.get("element_id", "") or "")
    page = getattr(book, "pages", {}).get(page_id)
    if page is None:
        raise ValueError("La page du problème n'existe plus.")
    target = next((
        element for element in getattr(page, "content", ())
        if isinstance(element, dict) and str(element.get("id", "") or "") == element_id
    ), None)
    if target is None:
        raise ValueError("La zone de texte du problème n'existe plus.")
    payload = target.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("Le contenu de cette zone de texte est invalide.")
    spans = payload.get("spans", [])
    if not isinstance(spans, list) or not spans:
        raise ValueError("La taille de cette zone ne peut pas être modifiée directement.")
    old_sizes = []
    changed = False
    for span in spans:
        if not isinstance(span, dict):
            continue
        try:
            old = float(span.get("size", value) or value)
        except (TypeError, ValueError):
            old = value
        old_sizes.append(old)
        if abs(old - value) > 0.01:
            span["size"] = value
            changed = True
    if not changed:
        return {
            "changed": False, "kind": "manual", "page_id": page_id,
            "element_id": element_id, "geometry": dict(target.get("geometry", {}) or {}),
        }
    before = float(median(old_sizes)) if old_sizes else value
    metadata = target.setdefault("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
        target["metadata"] = metadata
    metadata["text_content_modified"] = True
    history = metadata.setdefault("text_correction_history", [])
    if not isinstance(history, list):
        history = []
        metadata["text_correction_history"] = history
    history.append({
        "issue_id": str(issue.get("id", issue.get("key", "")) or ""),
        "kind": "manual_font_size", "before_size_pt": before, "after_size_pt": value,
    })
    return {
        "changed": True, "kind": "manual", "page_id": page_id, "element_id": element_id,
        "before_size_pt": before, "after_size_pt": value,
        "geometry": dict(target.get("geometry", {}) or {}),
    }


def apply_manual_text_edit(book: Any, issue: dict[str, Any], new_text: str) -> dict[str, Any]:
    """Applique le texte saisi par l'utilisateur sur la zone signalée.

    La géométrie n'est pas modifiée ici : elle peut être ajustée directement
    dans Composition pendant le même mode manuel. Les spans Source sont
    conservés pour la police/couleur ; payload.text devient l'autorité de
    contenu et le rendu TomeLinea recompose ensuite la zone.
    """
    if book is None or not isinstance(issue, dict):
        raise ValueError("Problème de texte invalide.")
    value = str(new_text or "")
    if not value.strip():
        raise ValueError("La zone de texte ne peut pas être laissée vide ici.")
    page_id = str(issue.get("page_id", "") or "")
    element_id = str(issue.get("element_id", "") or "")
    page = getattr(book, "pages", {}).get(page_id)
    if page is None:
        raise ValueError("La page du problème n'existe plus.")
    target = next((
        element for element in getattr(page, "content", ())
        if isinstance(element, dict) and str(element.get("id", "") or "") == element_id
    ), None)
    if target is None:
        raise ValueError("La zone de texte du problème n'existe plus.")
    payload = target.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("Le contenu de cette zone de texte est invalide.")
    before = str(payload.get("text", "") or "")
    if value == before:
        return {
            "changed": False, "kind": "manual", "page_id": page_id,
            "element_id": element_id, "before_text": before, "after_text": before,
            "geometry": dict(target.get("geometry", {}) or {}),
        }
    payload["text"] = value
    metadata = target.setdefault("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
        target["metadata"] = metadata
    history = metadata.setdefault("text_correction_history", [])
    if not isinstance(history, list):
        history = []
        metadata["text_correction_history"] = history
    history.append({
        "issue_id": str(issue.get("id", issue.get("key", "")) or ""),
        "kind": "manual", "before_text": before, "after_text": value,
    })
    metadata["text_content_modified"] = True
    return {
        "changed": True, "kind": "manual", "page_id": page_id,
        "element_id": element_id, "before_text": before, "after_text": value,
        "geometry": dict(target.get("geometry", {}) or {}),
    }


def _find_issue_element(book: Any, issue: dict[str, Any]) -> tuple[Any, dict[str, Any]]:
    page_id = str(issue.get("page_id", "") or "")
    element_id = str(issue.get("element_id", "") or "")
    page = getattr(book, "pages", {}).get(page_id)
    if page is None:
        raise ValueError("La page du problème n'existe plus.")
    target = next((
        element for element in getattr(page, "content", ())
        if isinstance(element, dict) and (not element_id or str(element.get("id", "") or "") == element_id)
    ), None)
    if target is None:
        raise ValueError("La zone de texte du problème n'existe plus.")
    return page, target


def _history(target: dict[str, Any]) -> list[dict[str, Any]]:
    metadata = target.setdefault("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
        target["metadata"] = metadata
    history = metadata.setdefault("text_correction_history", [])
    if not isinstance(history, list):
        history = []
        metadata["text_correction_history"] = history
    return history


def _apply_geometry_to_margins(book: Any, issue: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    from src.v4.composition import MARGINS, frame_bounds
    page_id = str(issue.get("page_id", "") or "")
    left, top, width, height = frame_bounds(book, page_id, MARGINS)
    right = float(left) + float(width)
    bottom = float(top) + float(height)
    geometry = target.get("geometry", {})
    if not isinstance(geometry, dict):
        geometry = {}
        target["geometry"] = geometry
    before = dict(geometry)
    x = _float(geometry.get("x_mm"))
    y = _float(geometry.get("y_mm"))
    w = max(0.1, _float(geometry.get("width_mm"), 0.1))
    h = max(0.1, _float(geometry.get("height_mm"), 0.1))
    new_x = max(float(left), min(x, right - 0.1))
    new_y = max(float(top), min(y, bottom - 0.1))
    new_right = min(right, max(new_x + 0.1, x + w))
    new_bottom = min(bottom, max(new_y + 0.1, y + h))
    geometry.update({
        "x_mm": new_x, "y_mm": new_y,
        "width_mm": max(0.1, new_right - new_x),
        "height_mm": max(0.1, new_bottom - new_y),
    })
    target["reference_frame"] = MARGINS
    metadata = target.setdefault("metadata", {})
    if isinstance(metadata, dict):
        metadata["text_content_modified"] = True
    changed = geometry != before
    if changed:
        _history(target).append({
            "issue_id": str(issue.get("id", issue.get("key", "")) or ""),
            "kind": str(issue.get("type", issue.get("kind", "")) or ""),
            "before_geometry": before, "after_geometry": dict(geometry),
        })
    return {
        "changed": changed, "kind": str(issue.get("type", issue.get("kind", "")) or ""),
        "page_id": page_id, "element_id": str(target.get("id", "") or ""),
        "before_geometry": before, "after_geometry": dict(geometry),
        "geometry": dict(geometry),
    }


def _apply_forbidden_hyphenation(book: Any, issue: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    metadata_book = getattr(book, "metadata", {})
    rules = metadata_book.get("text_general_rules", {}) if isinstance(metadata_book, dict) else {}
    policy = str(rules.get("hyphenation", "") or "").lower() if isinstance(rules, dict) else ""
    if policy not in {"forbid", "controlled"}:
        raise ValueError("Choisissez d'abord la règle générale des césures.")
    # En mode contrôlé, cette fonction n'est appelée que pour une césure que
    # le moteur a déjà classée comme problématique. Une césure ordinaire n'est
    # jamais proposée à la correction.
    payload = target.get("payload", {})
    if not isinstance(payload, dict):
        raise ValueError("Le contenu de cette zone de texte est invalide.")
    before_text = str(payload.get("text", "") or "")
    spans = payload.get("spans", ())
    if isinstance(spans, tuple):
        spans = list(spans)
        payload["spans"] = spans
    line_index = _issue_line_index(issue)
    changed = False
    before_line = ""
    after_line = ""
    if isinstance(spans, list) and line_index is not None:
        current_indexes = []
        next_indexes = []
        for idx, span in enumerate(spans):
            if not isinstance(span, dict):
                continue
            try:
                li = int(span.get("line_index", 0) or 0)
            except (TypeError, ValueError):
                li = 0
            if li == line_index:
                current_indexes.append(idx)
            elif li == line_index + 1:
                next_indexes.append(idx)
        if current_indexes and next_indexes:
            left_idx = current_indexes[-1]
            right_idx = next_indexes[0]
            left = str(spans[left_idx].get("text", "") or "")
            right = str(spans[right_idx].get("text", "") or "")
            if left.rstrip().endswith("-") and right.lstrip():
                before_line = left + right
                left_clean = left.rstrip()[:-1]
                lead = len(right) - len(right.lstrip())
                right_clean = right[lead:]
                spans[left_idx]["text"] = left_clean
                spans[right_idx]["text"] = right_clean
                # Le contenu logique ne doit plus contenir la coupure de ligne.
                pattern = re.escape(left.rstrip()) + r"\s*" + re.escape(right.lstrip())
                joined = left_clean + right_clean
                payload["text"] = re.sub(pattern, joined, before_text, count=1)
                if payload["text"] == before_text:
                    payload["text"] = before_text.replace(left.rstrip(), left_clean, 1)
                after_line = joined
                changed = True
    if not changed and "\u00ad" in before_text:
        payload["text"] = before_text.replace("\u00ad", "")
        before_line = before_text
        after_line = str(payload["text"] or "")
        changed = after_line != before_line
    if not changed:
        raise ValueError("TomeLinea n'a pas pu retirer cette césure sans modifier le mot.")
    metadata = target.setdefault("metadata", {})
    if isinstance(metadata, dict):
        metadata["text_content_modified"] = True
    _history(target).append({
        "issue_id": str(issue.get("id", issue.get("key", "")) or ""),
        "kind": "hyphenation", "before_text": before_text,
        "after_text": str(payload.get("text", "") or ""),
        "before_line": before_line, "after_line": after_line,
    })
    return {
        "changed": True, "kind": "hyphenation",
        "page_id": str(issue.get("page_id", "") or ""),
        "element_id": str(target.get("id", "") or ""),
        "before_text": before_text, "after_text": str(payload.get("text", "") or ""),
        "before_line": before_line, "after_line": after_line,
        "geometry": dict(target.get("geometry", {}) or {}),
    }


def _apply_justification(issue: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    metadata = target.setdefault("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
        target["metadata"] = metadata
    before = str(metadata.get("text_alignment", "") or "")
    metadata["text_alignment"] = "justify"
    metadata["text_content_modified"] = True
    changed = before != "justify"
    if changed:
        _history(target).append({
            "issue_id": str(issue.get("id", issue.get("key", "")) or ""),
            "kind": "text_not_justified", "before_alignment": before or "source",
            "after_alignment": "justify",
        })
    return {
        "changed": changed, "kind": "text_not_justified",
        "page_id": str(issue.get("page_id", "") or ""),
        "element_id": str(target.get("id", "") or ""),
        "before_line": "Alignement de la Source", "after_line": "Texte justifié",
        "geometry": dict(target.get("geometry", {}) or {}),
    }


def _apply_body_style(book: Any, issue: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    metadata_book = getattr(book, "metadata", {})
    rules = metadata_book.get("text_general_rules", {}) if isinstance(metadata_book, dict) else {}
    if not isinstance(rules, dict):
        rules = {}
    try:
        body_size = float(rules.get("font_size_pt") or book_body_text_size(book))
    except (TypeError, ValueError):
        body_size = float(book_body_text_size(book))
    body_font = str(rules.get("font_family", "") or "").strip()

    payload = target.get("payload", {})
    if not isinstance(payload, dict):
        raise ValueError("Le contenu de cette zone de texte est invalide.")
    spans = payload.get("spans", ())
    if not isinstance(spans, list) or not spans:
        raise ValueError("La mise en forme de ce texte ne peut pas être rétablie automatiquement.")

    old_sizes: list[float] = []
    old_fonts: list[str] = []
    changed = False
    for span in spans:
        if not isinstance(span, dict):
            continue
        old_size = _float(span.get("size"), body_size)
        old_font = str(span.get("font", "") or "")
        old_sizes.append(old_size)
        if old_font:
            old_fonts.append(old_font)
        if abs(old_size - body_size) > 0.01:
            span["size"] = body_size
            changed = True
        if body_font and _norm_font(old_font) != _norm_font(body_font):
            span["font"] = body_font
            changed = True

    if not changed:
        raise ValueError("Ce texte utilise déjà la mise en forme générale du livre.")

    metadata = target.setdefault("metadata", {})
    if isinstance(metadata, dict):
        metadata["text_content_modified"] = True
    before_size = float(median(old_sizes)) if old_sizes else body_size
    before_font = Counter(old_fonts).most_common(1)[0][0] if old_fonts else ""
    before_bits = []
    if before_font:
        before_bits.append(before_font)
    before_bits.append(f"{before_size:g} pt")
    after_bits = []
    if body_font:
        after_bits.append(body_font)
    after_bits.append(f"{body_size:g} pt")

    _history(target).append({
        "issue_id": str(issue.get("id", issue.get("key", "")) or ""),
        "kind": "style_outlier",
        "before_size_pt": before_size,
        "after_size_pt": body_size,
        "before_font": before_font,
        "after_font": body_font,
    })
    return {
        "changed": True,
        "kind": "style_outlier",
        "page_id": str(issue.get("page_id", "") or ""),
        "element_id": str(target.get("id", "") or ""),
        "before_line": " · ".join(before_bits),
        "after_line": " · ".join(after_bits),
        "geometry": dict(target.get("geometry", {}) or {}),
    }



def _page_after(book: Any, page_id: str):
    order = list(getattr(book, "page_order", ()) or ())
    try:
        index = order.index(str(page_id))
    except ValueError:
        return None
    if index + 1 >= len(order):
        return None
    return getattr(book, "pages", {}).get(order[index + 1])


def _page_before(book: Any, page_id: str):
    order = list(getattr(book, "page_order", ()) or ())
    try:
        index = order.index(str(page_id))
    except ValueError:
        return None
    if index <= 0:
        return None
    return getattr(book, "pages", {}).get(order[index - 1])


def _body_elements_for_page(book: Any, page: Any) -> list[dict[str, Any]]:
    """Corps de texte probable, trié de haut en bas, sans en-têtes/pagination."""
    nodes, _by_page = _collect_nodes(book)
    profile = _build_profile(nodes)
    ids = {
        node.element_id
        for node in nodes
        if node.page_id == str(getattr(page, "id", "")) and _body_like(node, profile)
    }
    result = [
        element for element in getattr(page, "content", ())
        if isinstance(element, dict) and str(element.get("id", "") or "") in ids
    ]
    result.sort(key=lambda element: (
        _float((element.get("geometry", {}) or {}).get("y_mm")),
        _float((element.get("geometry", {}) or {}).get("x_mm")),
    ))
    return result


def _shift_elements_vertically(elements: Iterable[dict[str, Any]], delta_mm: float) -> None:
    delta = float(delta_mm)
    if abs(delta) <= 1e-9:
        return
    for element in elements:
        geometry = element.get("geometry", {})
        if isinstance(geometry, dict):
            geometry["y_mm"] = _float(geometry.get("y_mm")) + delta
            metadata = element.setdefault("metadata", {})
            if isinstance(metadata, dict):
                metadata["text_content_modified"] = True


def _apply_title_orphan(book: Any, issue: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    """Garde un titre avec le texte qu'il annonce et recompose réellement.

    La correction est confiée au moteur de flux : si l'ajout du titre remplit la
    page suivante, les paragraphes excédentaires sont reportés proprement au
    lieu d'être comprimés ou superposés.
    """
    from src.v4.text_recomposition import attach_heading_to_next_page

    source_page, _ = _find_issue_element(book, issue)
    result = attach_heading_to_next_page(book, issue, target)
    _history(target).append({
        "issue_id": str(issue.get("id", issue.get("key", "")) or ""),
        "kind": "title_orphan",
        "from_page_id": str(source_page.id),
        "to_page_id": str(result.get("page_id", "") or ""),
        "before_geometry": dict(result.get("before_geometry", {}) or {}),
        "after_geometry": dict(result.get("geometry", {}) or {}),
        "recomposition": dict(result.get("flow", {}) or {}),
    })
    return result

def _split_line_pair(book: Any, issue: dict[str, Any]) -> tuple[Any, dict[str, Any], Any, dict[str, Any]]:
    """Retrouve les deux fragments d'un même paragraphe coupé sur deux pages."""
    kind = str(issue.get("type", issue.get("kind", "")) or "").lower()
    page, target = _find_issue_element(book, issue)
    if kind == "orphan_line":
        previous_page, previous_element = page, target
        next_page = _page_after(book, str(page.id))
        if next_page is None:
            raise ValueError("La page suivante n'est pas disponible.")
        next_body = _body_elements_for_page(book, next_page)
        if not next_body:
            raise ValueError("Le début du paragraphe suivant est introuvable.")
        return previous_page, previous_element, next_page, next_body[0]

    if kind == "widow":
        next_page, next_element = page, target
        previous_page = _page_before(book, str(page.id))
        if previous_page is None:
            raise ValueError("La page précédente n'est pas disponible.")
        previous_body = _body_elements_for_page(book, previous_page)
        if not previous_body:
            raise ValueError("La fin du paragraphe précédent est introuvable.")
        return previous_page, previous_body[-1], next_page, next_element

    raise ValueError("Ce problème n'est pas une veuve/orpheline corrigeable.")


def _apply_widow_orphan(book: Any, issue: dict[str, Any]) -> dict[str, Any]:
    """Réunit le paragraphe coupé puis laisse le moteur redistribuer le flux."""
    from src.v4.text_recomposition import recombine_split_paragraph

    previous_page, previous_element, next_page, next_element = _split_line_pair(book, issue)
    previous_lines = _node_lines(
        previous_element,
        page_width_mm=_float(getattr(book.format, "width_mm", 148.0), 148.0),
        page_height_mm=_float(getattr(book.format, "height_mm", 210.0), 210.0),
    )
    next_lines = _node_lines(
        next_element,
        page_width_mm=_float(getattr(book.format, "width_mm", 148.0), 148.0),
        page_height_mm=_float(getattr(book.format, "height_mm", 210.0), 210.0),
    )
    if len(previous_lines) != 1 or len(next_lines) != 1:
        raise ValueError("Cette coupure demande une recomposition plus large et n'est pas sûre automatiquement.")

    result = recombine_split_paragraph(
        book,
        previous_page=previous_page,
        previous_element=previous_element,
        next_page=next_page,
        next_element=next_element,
    )
    _history(next_element).append({
        "issue_id": str(issue.get("id", issue.get("key", "")) or ""),
        "kind": "widow_orphan",
        "from_page_id": str(previous_page.id),
        "to_page_id": str(next_page.id),
        "before_text": str(result.get("before_text", "") or ""),
        "after_text": str(result.get("after_text", "") or ""),
        "recomposition": dict(result.get("flow", {}) or {}),
    })
    return {
        "changed": True,
        "kind": str(issue.get("type", issue.get("kind", "")) or ""),
        "page_id": str(result.get("page_id", next_page.id)),
        "element_id": str(result.get("element_id", next_element.get("id", "")) or ""),
        "before_line": "Une ligne isolée au changement de page",
        "after_line": "Le paragraphe a été recomposé pour garder ses lignes ensemble",
        "geometry": dict(result.get("geometry", {}) or {}),
        "flow": dict(result.get("flow", {}) or {}),
    }

def apply_safe_text_correction(book: Any, issue: dict[str, Any]) -> dict[str, Any]:
    """Applique une correction texte sûre sur la ligne exacte signalée.

    La fonction ne marque jamais elle-même le problème comme traité : l'appelant
    doit relancer l'analyse et vérifier que l'anomalie a réellement disparu.
    L'ancienne valeur est conservée dans les métadonnées de l'élément ; la
    transaction Workspace fournit en plus l'Undo global de TomeLinea.
    """
    if book is None or not isinstance(issue, dict):
        raise ValueError("Problème de texte invalide.")

    kind = str(issue.get("type", issue.get("kind", "")) or "").lower()
    if kind not in AUTOMATIC_TEXT_CORRECTION_KINDS:
        raise ValueError("Cette correction automatique n'est pas encore disponible.")

    _page, rule_target = _find_issue_element(book, issue)
    if kind == "text_not_justified":
        result = _apply_justification(issue, rule_target)
        if not result.get("changed"):
            raise ValueError("Ce paragraphe est déjà justifié.")
        return result
    if kind == "style_outlier":
        return _apply_body_style(book, issue, rule_target)
    if kind == "hyphenation":
        return _apply_forbidden_hyphenation(book, issue, rule_target)
    if kind == "title_orphan":
        return _apply_title_orphan(book, issue, rule_target)
    if kind in {"orphan_line", "widow"}:
        return _apply_widow_orphan(book, issue)

    page_id = str(issue.get("page_id", "") or "")
    element_id = str(issue.get("element_id", "") or "")
    page = getattr(book, "pages", {}).get(page_id)
    if page is None:
        raise ValueError("La page du problème n'existe plus.")

    target = None
    for element in getattr(page, "content", ()):
        if not isinstance(element, dict):
            continue
        if element_id and str(element.get("id", "") or "") == element_id:
            target = element
            break
    if target is None:
        raise ValueError("La zone de texte du problème n'existe plus.")

    payload = target.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("Le contenu de cette zone de texte est invalide.")

    before_text = str(payload.get("text", "") or "")
    spans = payload.get("spans", ())
    if isinstance(spans, tuple):
        spans = list(spans)
        payload["spans"] = spans
    line_index = _issue_line_index(issue)
    changed = False
    old_line = ""
    new_line = ""

    if isinstance(spans, list) and spans and line_index is not None:
        span_indexes = []
        for index, span in enumerate(spans):
            if not isinstance(span, dict):
                continue
            try:
                current_line = int(span.get("line_index", 0) or 0)
            except (TypeError, ValueError):
                current_line = 0
            if current_line == line_index:
                span_indexes.append(index)

        if span_indexes:
            parts = [str(spans[index].get("text", "") or "") for index in span_indexes]
            old_line = "".join(parts)
            corrected = [_safe_text_transform(kind, part) for part in parts]
            for local_index in range(len(corrected) - 1):
                corrected[local_index], corrected[local_index + 1] = _correct_span_boundary(
                    kind, corrected[local_index], corrected[local_index + 1]
                )
            new_line = "".join(corrected)
            if new_line != old_line:
                for index, value in zip(span_indexes, corrected):
                    spans[index]["text"] = value
                if old_line and old_line in before_text:
                    payload["text"] = before_text.replace(old_line, new_line, 1)
                else:
                    payload["text"] = _safe_text_transform(kind, before_text)
                changed = str(payload.get("text", "") or "") != before_text or new_line != old_line

    if not changed:
        after = _safe_text_transform(kind, before_text)
        if after != before_text:
            payload["text"] = after
            old_line = before_text
            new_line = after
            changed = True

    if not changed:
        raise ValueError("TomeLinea n'a trouvé aucune modification sûre à appliquer ici.")

    after_text = str(payload.get("text", "") or "")
    metadata = target.setdefault("metadata", {})
    if not isinstance(metadata, dict):
        metadata = {}
        target["metadata"] = metadata
    history = metadata.setdefault("text_correction_history", [])
    if not isinstance(history, list):
        history = []
        metadata["text_correction_history"] = history
    history.append({
        "issue_id": str(issue.get("id", issue.get("key", "")) or ""),
        "kind": kind,
        "line_index": line_index,
        "before_text": before_text,
        "after_text": after_text,
        "before_line": old_line,
        "after_line": new_line,
    })
    # La page Source reste intacte sur disque. Ce drapeau dit simplement au
    # rendu Composition de masquer le texte Source de cette zone et de redessiner
    # désormais son contenu TomeLinea actuel. Sans cela la correction existe
    # dans le modèle mais l'utilisateur continuerait à voir l'ancien PDF.
    metadata["text_content_modified"] = True

    return {
        "changed": True,
        "kind": kind,
        "page_id": page_id,
        "element_id": element_id,
        "line_index": line_index,
        "before_text": before_text,
        "after_text": after_text,
        "before_line": old_line,
        "after_line": new_line,
        "geometry": dict(issue.get("geometry") or {}),
    }

