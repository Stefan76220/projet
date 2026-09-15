from __future__ import annotations

"""TomeLinea V4 — copie de travail persistante par chapitre.

La Source originale n'est jamais modifiée. Seul l'état de Composition exporté
par Canvas est enregistré. Si la Source change, la copie est invalidée.
"""

from copy import deepcopy
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any
import json

from src.v4.canvas_chapter_runtime import ChapterSlice, apply_exported_state

SCHEMA = "tomelinea.chapter_working_copy.v1"

def source_fingerprint(path: str | Path) -> str:
    source = Path(path)
    digest = sha256()
    with source.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()

def chapter_key(chapter: ChapterSlice) -> str:
    return "|".join((
        str(int(chapter.index)),
        str(chapter.start_paragraph if chapter.start_paragraph is not None else ""),
        str(chapter.end_paragraph if chapter.end_paragraph is not None else ""),
        str(chapter.detected_by or ""),
    ))

def _blank_state(source: str | Path) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "source_fingerprint": source_fingerprint(source),
        "updated_at_utc": None,
        "chapters": {},
    }

def load_chapter_working_copy(state_path: str | Path, source: str | Path) -> dict[str, Any]:
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
    chapters = data.get("chapters")
    if not isinstance(chapters, dict):
        chapters = {}
    clean = {}
    for key, value in chapters.items():
        if not isinstance(value, dict):
            continue
        exported = value.get("exported")
        if not isinstance(exported, dict):
            continue
        if exported.get("ok") is not True:
            continue
        if not isinstance(exported.get("segments"), list):
            continue
        clean[str(key)] = {
            "title": str(value.get("title") or ""),
            "index": value.get("index"),
            "start_paragraph": value.get("start_paragraph"),
            "end_paragraph": value.get("end_paragraph"),
            "detected_by": str(value.get("detected_by") or ""),
            "saved_at_utc": value.get("saved_at_utc"),
            "exported": deepcopy(exported),
        }
    return {
        "schema": SCHEMA,
        "source_fingerprint": expected,
        "updated_at_utc": data.get("updated_at_utc"),
        "chapters": clean,
    }

def save_chapter_working_copy(state_path: str | Path, state: dict[str, Any]) -> None:
    path = Path(state_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)

def record_chapter_export(
    state_path: str | Path,
    source: str | Path,
    chapter: ChapterSlice,
    exported: dict[str, Any],
) -> bool:
    if not isinstance(exported, dict) or exported.get("ok") is not True:
        return False
    if not isinstance(exported.get("segments"), list):
        return False
    state = load_chapter_working_copy(state_path, source)
    now = datetime.now(timezone.utc).isoformat()
    state["chapters"][chapter_key(chapter)] = {
        "title": str(chapter.title or ""),
        "index": int(chapter.index),
        "start_paragraph": chapter.start_paragraph,
        "end_paragraph": chapter.end_paragraph,
        "detected_by": str(chapter.detected_by or ""),
        "saved_at_utc": now,
        "exported": deepcopy(exported),
    }
    state["updated_at_utc"] = now
    save_chapter_working_copy(state_path, state)
    return True

def restore_chapter_export(
    plan: dict[str, Any],
    state: dict[str, Any],
    chapter: ChapterSlice,
) -> bool:
    chapters = state.get("chapters", {}) if isinstance(state, dict) else {}
    if not isinstance(chapters, dict):
        return False
    item = chapters.get(chapter_key(chapter))
    if not isinstance(item, dict):
        return False
    exported = item.get("exported")
    if not isinstance(exported, dict):
        return False
    return bool(apply_exported_state(plan, exported))
