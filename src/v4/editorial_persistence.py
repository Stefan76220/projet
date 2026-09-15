from __future__ import annotations

"""Persistance minimale des décisions humaines de composition.

Cette couche ne touche jamais à la Source. Elle mémorise uniquement les choix
humains appliqués à la version de composition, indexés par identifiants stables.
Le fichier JSON utilisé par le banc Phase 2 sera remplacé par le stockage projet
lors de l'intégration finale dans TomeLinea.
"""

from hashlib import sha256
from pathlib import Path
from typing import Any
import json

SCHEMA = "tomelinea.editorial_state.v1"


def source_fingerprint(path: str | Path) -> str:
    p = Path(path)
    h = sha256()
    with p.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def decision_key(item: dict[str, Any]) -> str:
    domain = str(item.get("domain") or "editorial")
    if domain == "table":
        table_id = str(item.get("tableId") or item.get("table_id") or "")
        segment = str(item.get("segment") or "")
        if table_id:
            return f"table:{segment}:{table_id}"
    stable_id = str(item.get("stable_id") or item.get("id") or "")
    if stable_id:
        return f"{domain}:{stable_id}"
    return ""


def _blank_state(source: str | Path) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "source_fingerprint": source_fingerprint(source),
        "decisions": {},
    }


def load_editorial_state(state_path: str | Path, source: str | Path) -> dict[str, Any]:
    path = Path(state_path)
    expected = source_fingerprint(source)
    if not path.is_file():
        return _blank_state(source)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return _blank_state(source)
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        return _blank_state(source)
    if data.get("source_fingerprint") != expected:
        return _blank_state(source)
    decisions = data.get("decisions")
    if not isinstance(decisions, dict):
        decisions = {}
    return {
        "schema": SCHEMA,
        "source_fingerprint": expected,
        "decisions": {str(k): dict(v) for k, v in decisions.items() if isinstance(v, dict)},
    }


def save_editorial_state(state_path: str | Path, state: dict[str, Any]) -> None:
    path = Path(state_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def record_editorial_choice(
    state_path: str | Path,
    source: str | Path,
    event: dict[str, Any],
) -> dict[str, Any]:
    key = decision_key(event)
    state = load_editorial_state(state_path, source)
    if not key:
        return state
    choice = str(event.get("choice") or "")
    if not choice:
        return state
    state["decisions"][key] = {
        "domain": str(event.get("domain") or "editorial"),
        "table_id": event.get("tableId") or event.get("table_id"),
        "segment": event.get("segment"),
        "stable_id": event.get("stable_id") or event.get("id"),
        "choice": choice,
    }
    save_editorial_state(state_path, state)
    return state


def persisted_choices_for_plan(state: dict[str, Any]) -> list[dict[str, Any]]:
    decisions = state.get("decisions", {}) if isinstance(state, dict) else {}
    if not isinstance(decisions, dict):
        return []
    result: list[dict[str, Any]] = []
    for key, value in decisions.items():
        if not isinstance(value, dict):
            continue
        item = dict(value)
        item["key"] = str(key)
        result.append(item)
    return result
