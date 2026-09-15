from __future__ import annotations

"""Classification éditoriale autonome des unités DOCX de TomeLinea V4.

Le moteur Canvas peut découper le document en unités techniques de composition.
Ce module leur donne un sens éditorial sans confondre « Heading 1 » avec
« chapitre ». Les décisions sûres sont automatiques ; les frontières réelles
mais sémantiquement inconnues sont remontées à l'utilisateur.
"""

from copy import deepcopy
import json
from pathlib import Path
import re
import unicodedata
from typing import Any


def _norm(value: Any) -> str:
    text = str(value or "").strip().casefold()
    text = "".join(
        ch for ch in unicodedata.normalize("NFKD", text)
        if not unicodedata.combining(ch)
    )
    text = text.replace("’", "'").replace("–", "-").replace("—", "-")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _tl(element: dict[str, Any]) -> dict[str, Any]:
    ext = element.get("extension")
    if not isinstance(ext, dict):
        return {}
    value = ext.get("tomelinea")
    return value if isinstance(value, dict) else {}


def _paragraph_info(element: dict[str, Any]) -> tuple[str | None, str | None, int | None]:
    tl = _tl(element)
    trace = tl.get("sourceTrace") if isinstance(tl.get("sourceTrace"), dict) else {}
    paragraph = tl.get("paragraph")
    if not isinstance(paragraph, dict):
        paragraph = trace.get("paragraph")
    if not isinstance(paragraph, dict):
        paragraph = {}
    fmt = paragraph.get("format") if isinstance(paragraph.get("format"), dict) else {}

    para_id = paragraph.get("id")
    style_id = fmt.get("style_id")
    source_para = paragraph.get("sourceParagraph")

    if para_id is None and tl.get("paragraphEnd") is not None:
        source_para = tl.get("paragraphEnd")
        para_id = f"p:{source_para}"
        fmt2 = tl.get("format")
        if isinstance(fmt2, dict):
            style_id = fmt2.get("style_id")

    return (
        str(para_id) if para_id is not None else None,
        str(style_id) if style_id is not None else None,
        int(source_para) if isinstance(source_para, int) else None,
    )


def _element_text(element: dict[str, Any]) -> str:
    value = element.get("value")
    return value if isinstance(value, str) else ""


def _flatten_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    flat: list[dict[str, Any]] = []
    for section in payload.get("sections") or []:
        main = section.get("data", {}).get("main", []) if isinstance(section, dict) else []
        for element in main:
            if isinstance(element, dict):
                flat.append(element)
    return flat


def _unit_paragraphs(flat: list[dict[str, Any]], start: int, end: int) -> tuple[list[str], str | None]:
    order: list[str] = []
    texts: dict[str, list[str]] = {}
    first_style: str | None = None
    synthetic_counter = 0

    for element in flat[max(0, start):max(0, end)]:
        para_id, style_id, source_para = _paragraph_info(element)
        if first_style is None and style_id:
            first_style = style_id
        if para_id is None:
            if source_para is not None:
                para_id = f"source:{source_para}"
            else:
                synthetic_counter += 1
                para_id = f"synthetic:{synthetic_counter}"
        if para_id not in texts:
            texts[para_id] = []
            order.append(para_id)
        text = _element_text(element)
        if text and text != "\n":
            texts[para_id].append(text)

    paragraphs = ["".join(texts[key]).strip() for key in order]
    paragraphs = [value for value in paragraphs if value]
    return paragraphs, first_style


def _is_heading_style(style_id: str | None) -> bool:
    value = _norm(style_id).replace("_", " ").replace("-", " ")
    compact = value.replace(" ", "")
    return (
        "heading" in value
        or "titre" in value
        or compact in {"heading1", "heading2", "titre1", "titre2"}
    )


def _clean_toc_entry(text: str) -> str:
    value = str(text or "").strip()
    value = re.sub(r"\.{2,}\s*[0-9ivxlcdm]+\s*$", "", value, flags=re.I)
    value = re.sub(r"\s+[0-9ivxlcdm]+\s*$", "", value, flags=re.I)
    return _norm(value)


def _unit_key(index: int, title: str, start_paragraph: Any) -> str:
    return f"{int(index)}:{start_paragraph}:{_norm(title)}"


def load_structure_catalog(path: str | Path) -> dict[str, Any]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict) or not isinstance(data.get("known_types"), list):
        raise ValueError("Catalogue éditorial invalide.")
    return data


def _candidate_scores(
    *,
    title: str,
    paragraphs: list[str],
    style_id: str | None,
    known_types: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    normalized_title = _norm(title)
    excerpt = _norm("\n".join(paragraphs[:8]))
    results: list[dict[str, Any]] = []

    for item in known_types:
        if not isinstance(item, dict):
            continue
        score = 0
        reasons: list[str] = []

        aliases = [_norm(value) for value in item.get("aliases", []) if str(value or "").strip()]
        for alias in aliases:
            if normalized_title == alias:
                score = max(score, 60)
                reasons.append("intitulé reconnu")
            elif normalized_title.startswith(alias + " ") or normalized_title.startswith(alias + "-"):
                score = max(score, 52)
                reasons.append("intitulé apparenté")

        for pattern in item.get("title_regex", []) or []:
            try:
                if re.search(str(pattern), normalized_title, flags=re.I):
                    score = max(score, 60)
                    reasons.append("forme de titre reconnue")
            except re.error:
                continue

        content_hits = 0
        for pattern in item.get("content_regex", []) or []:
            try:
                if re.search(str(pattern), excerpt, flags=re.I):
                    content_hits += 1
            except re.error:
                if _norm(pattern) and _norm(pattern) in excerpt:
                    content_hits += 1
        if content_hits:
            score += min(30, content_hits * 15)
            reasons.append("contenu caractéristique")

        # Le style seul prouve une frontière, pas le sens éditorial.
        # Il ne renforce donc qu'un type déjà reconnu par son intitulé ou son contenu.
        if score > 0 and _is_heading_style(style_id):
            score += 10
            reasons.append("niveau de titre")

        if score > 0:
            results.append({
                "type": str(item.get("id") or "unknown"),
                "label": str(item.get("label") or item.get("id") or ""),
                "score": int(score),
                "default_zone": str(item.get("default_zone") or "bodymatter"),
                "allowed_zones": list(item.get("allowed_zones") or []),
                "reasons": reasons,
            })

    results.sort(key=lambda value: int(value.get("score", 0)), reverse=True)
    return results


def _zone_for_candidate(
    index: int,
    candidate: dict[str, Any] | None,
    *,
    first_body: int | None,
    first_back: int | None,
) -> str:
    if candidate is not None:
        kind = str(candidate.get("type") or "")
        default_zone = str(candidate.get("default_zone") or "bodymatter")
        allowed = {str(value) for value in candidate.get("allowed_zones") or []}

        if kind in {"part", "chapter", "interlude"}:
            return "bodymatter"
        if default_zone == "frontmatter" and "bodymatter" not in allowed:
            return "frontmatter"
        if default_zone == "backmatter" and "bodymatter" not in allowed:
            return "backmatter"

        if first_body is not None and index < first_body:
            return "frontmatter"
        if first_back is not None and index >= first_back:
            return "backmatter"
        return default_zone

    if first_body is None:
        return "frontmatter" if index == 0 else "bodymatter"
    if index < first_body:
        return "frontmatter"
    if first_back is not None and index >= first_back:
        return "backmatter"
    return "bodymatter"


def classify_editorial_structure(
    payload: dict[str, Any],
    detection: Any,
    *,
    catalog_path: str | Path,
    persisted_choices: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Classe les unités Canvas en zones et types éditoriaux.

    Une unité issue d'un repli technique n'est jamais transformée en section
    éditoriale ni présentée à l'utilisateur comme une ambiguïté.
    """

    catalog = load_structure_catalog(catalog_path)
    known_types = [item for item in catalog.get("known_types", []) if isinstance(item, dict)]
    scoring = catalog.get("scoring") if isinstance(catalog.get("scoring"), dict) else {}
    auto_threshold = int(scoring.get("semantic_auto_threshold", 80) or 80)
    ask_threshold = int(scoring.get("semantic_ask_threshold", 55) or 55)
    boundary_threshold = int(scoring.get("boundary_threshold", 70) or 70)
    choices = persisted_choices if isinstance(persisted_choices, dict) else {}

    chapters = list(getattr(detection, "chapters", ()) or ())
    flat = _flatten_payload(payload)
    raw_units: list[dict[str, Any]] = []

    for zero_index, chapter in enumerate(chapters):
        title = str(getattr(chapter, "title", "") or "").strip() or f"Unité {zero_index + 1}"
        start = int(getattr(chapter, "start_global", 0) or 0)
        end = int(getattr(chapter, "end_global", start + 1) or (start + 1))
        paragraphs, style_id = _unit_paragraphs(flat, start, end)
        detected_by = str(getattr(chapter, "detected_by", "") or "")
        start_paragraph = getattr(chapter, "start_paragraph", None)
        key = _unit_key(zero_index, title, start_paragraph)

        candidates = _candidate_scores(
            title=title,
            paragraphs=paragraphs,
            style_id=style_id,
            known_types=known_types,
        )
        raw_units.append({
            "canvas_index": zero_index,
            "chapter_index": int(getattr(chapter, "index", zero_index + 1) or (zero_index + 1)),
            "key": key,
            "title": title,
            "start_paragraph": start_paragraph,
            "end_paragraph": getattr(chapter, "end_paragraph", None),
            "detected_by": detected_by,
            "style_id": style_id,
            "paragraphs": paragraphs[:12],
            "candidates": candidates,
            "boundary_confidence": (
                100 if detected_by == "prelude"
                else 90 if detected_by == "style"
                else 35 if "technical" in detected_by
                else 70
            ),
        })

    # Les candidats sémantiques forts fournissent les points d'ancrage de la
    # structure : premier corps puis première fin d'ouvrage.
    first_body: int | None = None
    first_back: int | None = None
    for unit in raw_units:
        candidates = unit["candidates"]
        best = candidates[0] if candidates else None
        if best is None or int(best.get("score", 0)) < 50:
            continue
        kind = str(best.get("type") or "")
        if first_body is None and kind in {"part", "chapter", "interlude"}:
            first_body = int(unit["canvas_index"])
        if first_body is not None and first_back is None:
            if str(best.get("default_zone") or "") == "backmatter":
                first_back = int(unit["canvas_index"])

    # Repère le sommaire pour reconnaître certains chapitres non numérotés.
    toc_titles: set[str] = set()
    for unit in raw_units:
        candidates = unit["candidates"]
        if not candidates:
            continue
        best = candidates[0]
        if str(best.get("type")) != "toc" or int(best.get("score", 0)) < 50:
            continue
        for paragraph in unit.get("paragraphs", []):
            cleaned = _clean_toc_entry(paragraph)
            if cleaned and cleaned not in {_norm(unit.get("title"))}:
                toc_titles.add(cleaned)

    units: list[dict[str, Any]] = []
    for unit in raw_units:
        detected_by = str(unit.get("detected_by") or "")
        title = str(unit.get("title") or "")
        key = str(unit.get("key") or "")

        if detected_by == "prelude":
            resolved = {
                **unit,
                "editorial_type": "frontmatter_bundle",
                "editorial_label": "Pages liminaires",
                "zone": "frontmatter",
                "confidence": 100,
                "ask_user": False,
                "decision": "automatic",
                "reasons": ["contenu placé avant la première unité structurée"],
                "toc_match": False,
            }
            units.append(resolved)
            continue

        if "technical" in detected_by:
            resolved = {
                **unit,
                "editorial_type": "technical_unit",
                "editorial_label": "Unité technique",
                "zone": "bodymatter",
                "confidence": 100,
                "ask_user": False,
                "decision": "technical",
                "reasons": ["découpage technique Canvas, invisible éditorialement"],
                "toc_match": False,
            }
            units.append(resolved)
            continue

        candidates = unit.get("candidates") or []
        best = candidates[0] if candidates else None
        zone = _zone_for_candidate(
            int(unit.get("canvas_index", 0)),
            best,
            first_body=first_body,
            first_back=first_back,
        )

        toc_match = _norm(title) in toc_titles
        if not toc_match:
            nt = _norm(title)
            toc_match = any(nt and (nt == item or nt in item or item in nt) for item in toc_titles)

        score = int(best.get("score", 0)) if best else 0
        reasons = list(best.get("reasons", [])) if best else []
        if best is not None:
            default_zone = str(best.get("default_zone") or "bodymatter")
            allowed = {default_zone, *[str(value) for value in best.get("allowed_zones") or []]}
            if zone in allowed or str(best.get("type")) in {"part", "chapter", "interlude"}:
                score += 15
                reasons.append("position cohérente dans le livre")
            else:
                score -= 30
                reasons.append("position inhabituelle")
        if toc_match:
            score += 10
            reasons.append("présent dans le sommaire")

        kind = str(best.get("type") or "unknown") if best else "unknown"
        label = str(best.get("label") or title) if best else title
        auto = best is not None and score >= auto_threshold

        resolved = {
            **unit,
            "editorial_type": kind if auto else "unknown",
            "editorial_label": label if auto else title,
            "zone": zone,
            "confidence": max(0, min(100, int(score))),
            "ask_user": False,
            "decision": "automatic" if auto else "unresolved",
            "reasons": reasons,
            "toc_match": bool(toc_match),
        }
        units.append(resolved)

    # Chapitres non numérotés : au moins deux unités inconnues consécutives,
    # dans le Corps, au même niveau de titre et présentes au sommaire. Ce seuil
    # évite de transformer une unité isolée (« Carnet de terrain ») en chapitre.
    i = 0
    while i < len(units):
        if not (
            units[i].get("editorial_type") == "unknown"
            and units[i].get("zone") == "bodymatter"
            and units[i].get("toc_match")
            and _is_heading_style(units[i].get("style_id"))
        ):
            i += 1
            continue
        j = i
        style = _norm(units[i].get("style_id"))
        while j < len(units):
            current = units[j]
            if not (
                current.get("editorial_type") == "unknown"
                and current.get("zone") == "bodymatter"
                and current.get("toc_match")
                and _norm(current.get("style_id")) == style
            ):
                break
            j += 1
        run = units[i:j]
        if len(run) >= 2:
            previous_type = str(units[i - 1].get("editorial_type") or "") if i > 0 else ""
            next_type = str(units[j].get("editorial_type") or "") if j < len(units) else ""
            if previous_type in {"part", "chapter", "introduction", "prologue"} or next_type in {"part", "conclusion", "epilogue"}:
                for current in run:
                    current["editorial_type"] = "chapter"
                    current["editorial_label"] = "Chapitre"
                    current["confidence"] = max(82, int(current.get("confidence", 0)))
                    current["decision"] = "automatic_pattern"
                    current["reasons"] = list(current.get("reasons") or []) + [
                        "série cohérente de chapitres non numérotés"
                    ]
        i = max(j, i + 1)

    # Applique les choix déjà enregistrés, sinon demande uniquement pour une
    # vraie frontière structurante inconnue. Un score sémantique faible ne
    # suffit pas à imposer une classification.
    for index, unit in enumerate(units):
        key = str(unit.get("key") or "")
        choice = choices.get(key)
        if isinstance(choice, dict):
            decision = str(choice.get("decision") or "")
            if decision == "create":
                unit["editorial_type"] = "custom_section"
                unit["editorial_label"] = str(choice.get("name") or unit.get("title") or "Section")
                unit["zone"] = str(choice.get("zone") or unit.get("zone") or "bodymatter")
                unit["confidence"] = 100
                unit["ask_user"] = False
                unit["decision"] = "user_create"
                continue
            if decision == "merge":
                unit["editorial_type"] = "merge_previous"
                unit["confidence"] = 100
                unit["ask_user"] = False
                unit["decision"] = "user_merge"
                continue

        if unit.get("editorial_type") != "unknown":
            continue
        boundary = int(unit.get("boundary_confidence", 0))
        confidence = int(unit.get("confidence", 0))
        if boundary >= boundary_threshold and confidence < auto_threshold:
            unit["ask_user"] = True
            unit["decision"] = "ask"
        elif confidence >= ask_threshold:
            unit["ask_user"] = True
            unit["decision"] = "ask"
        else:
            # Frontière faible : ne pas déranger l'utilisateur.
            unit["editorial_type"] = "merge_previous"
            unit["decision"] = "automatic_merge"
            unit["ask_user"] = False

    return {
        "schema": "tomelinea.editorial_structure_analysis.v1",
        "catalog_version": str(catalog.get("version") or "1.0"),
        "mode": str(getattr(detection, "mode", "") or ""),
        "units": units,
        "ambiguous_keys": [str(unit.get("key")) for unit in units if unit.get("ask_user")],
        "summary": {
            "frontmatter": sum(1 for unit in units if unit.get("zone") == "frontmatter"),
            "bodymatter": sum(1 for unit in units if unit.get("zone") == "bodymatter"),
            "backmatter": sum(1 for unit in units if unit.get("zone") == "backmatter"),
            "ambiguous": sum(1 for unit in units if unit.get("ask_user")),
        },
    }


def apply_structure_choice(
    analysis: dict[str, Any],
    unit_key: str,
    *,
    create_section: bool,
    name: str | None = None,
) -> dict[str, Any]:
    """Retourne une copie de l'analyse avec un choix utilisateur appliqué."""
    result = deepcopy(analysis)
    for unit in result.get("units", []) or []:
        if str(unit.get("key") or "") != str(unit_key):
            continue
        if create_section:
            unit["editorial_type"] = "custom_section"
            unit["editorial_label"] = str(name or unit.get("title") or "Section").strip() or "Section"
            unit["decision"] = "user_create"
        else:
            unit["editorial_type"] = "merge_previous"
            unit["decision"] = "user_merge"
        unit["confidence"] = 100
        unit["ask_user"] = False
        break
    result["ambiguous_keys"] = [
        str(unit.get("key"))
        for unit in result.get("units", []) or []
        if unit.get("ask_user")
    ]
    if isinstance(result.get("summary"), dict):
        result["summary"]["ambiguous"] = len(result["ambiguous_keys"])
    return result
