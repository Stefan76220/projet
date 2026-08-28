from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image

from src.gui_v3.book_canvas import _PILCanvasTarget

WEB_ROOT = Path(__file__).resolve().parent / "viewer3d" / "web"
SNAPSHOT_DIR = WEB_ROOT / "_page_snapshots"


def _safe_json(value) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    except Exception:
        return repr(value)


def _source_stamp(canvas, element: dict) -> tuple:
    source = str(element.get("source") or element.get("path") or element.get("image") or "").strip()
    if not source:
        return ("",)
    try:
        path = canvas._production_resolve_content_path(source)
        if path is not None and path.is_file():
            st = path.stat()
            return (str(path), int(st.st_mtime_ns), int(st.st_size))
    except Exception:
        pass
    return (source,)


def _signature(canvas, item: dict, page_number: int, width: int) -> str:
    elements = item.get("production_elements") if isinstance(item.get("production_elements"), list) else []
    payload = {
        "page": int(page_number),
        "width": int(width),
        "id": str(item.get("id") or ""),
        "zones": item.get("gabarit_zones") or [],
        "settings": item.get("gabarit_page_settings") or {},
        "elements": elements,
        "sources": [_source_stamp(canvas, e) for e in elements if isinstance(e, dict)],
        "preview": {k: item.get(k) for k in (
            "production_preview", "production_thumbnail", "rendered_preview",
            "content_preview", "page_render_path", "gabarit_preview",
            "template_preview", "layout_preview", "model_preview", "gabarit_image",
        ) if item.get(k)},
    }
    try:
        payload["format_mm"] = tuple(round(float(v), 4) for v in canvas._gabarit_page_mm())
    except Exception:
        payload["format_mm"] = (210.0, 297.0)
    return hashlib.sha1(_safe_json(payload).encode("utf-8")).hexdigest()[:16]


def build_page_snapshot(canvas, item: dict, page_number: int, *, width: int = 1200, quality: int = 88) -> str:
    """Fabrique une photo WebP propre de la page Production.

    On réutilise volontairement les fonctions de dessin déjà utilisées par
    Production : aperçu de page puis contenus de zones. Aucun cadre de zone,
    marge, poignée, halo ou élément d'interface n'est dessiné.
    """
    if canvas is None or not isinstance(item, dict):
        return ""
    if not isinstance(item.get("production_elements"), list) and not any(
        item.get(k) for k in ("production_preview", "production_thumbnail", "rendered_preview", "content_preview", "page_render_path")
    ):
        return ""

    # Première version volontairement prudente : les vraies 2P gardent le rendu
    # de démonstration tant qu'un cadrage gauche/droite dédié n'est pas validé.
    try:
        if str(canvas._double_page_pair_id(item) or ""):
            return ""
    except Exception:
        pass

    width = max(640, min(1600, int(width or 1200)))
    try:
        page_w_mm, page_h_mm = canvas._gabarit_page_mm()
        page_w_mm = max(1.0, float(page_w_mm))
        page_h_mm = max(1.0, float(page_h_mm))
    except Exception:
        page_w_mm, page_h_mm = 210.0, 297.0
    height = max(640, min(2400, int(round(width * page_h_mm / page_w_mm))))

    signature = _signature(canvas, item, page_number, width)
    project_root = getattr(getattr(canvas, "project", None), "root", None)
    project_key = hashlib.sha1(str(project_root or "project").encode("utf-8")).hexdigest()[:8]
    filename = f"{project_key}_p{int(page_number):05d}_{signature}.webp"
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    target_path = SNAPSHOT_DIR / filename
    if target_path.is_file():
        return f"_page_snapshots/{filename}"

    try:
        settings = canvas._gabarit_sheet_settings(item)
        background = str(settings.get("background") or "#FAF9F4")
    except Exception:
        background = "#FAF9F4"

    frame = Image.new("RGB", (width, height), background)
    target = _PILCanvasTarget(frame)

    old_mode = str(getattr(canvas, "_work_mode", "") or "")
    try:
        # Les routines Production contrôlent elles-mêmes ce mode.
        canvas._work_mode = "production"
        try:
            canvas._production_draw_page_preview(target, 0.0, 0.0, float(width), float(height), item)
        except Exception:
            pass

        zones = item.get("gabarit_zones") if isinstance(item.get("gabarit_zones"), list) else []
        for zone in zones:
            if not isinstance(zone, dict):
                continue
            try:
                zx = float(zone.get("x", 0.0) or 0.0) * width
                zy = float(zone.get("y", 0.0) or 0.0) * height
                zw = max(0.001, float(zone.get("w", 0.0) or 0.0)) * width
                zh = max(0.001, float(zone.get("h", 0.0) or 0.0)) * height
                angle = float(canvas._gabarit_zone_rotation(zone) or 0.0)
                canvas._production_draw_zone_content(target, zone, item, zx, zy, zw, zh, angle)
            except Exception:
                continue
    finally:
        canvas._work_mode = old_mode

    tmp = target_path.with_suffix(".tmp.webp")
    frame.save(tmp, format="WEBP", quality=max(75, min(95, int(quality))), method=4)
    tmp.replace(target_path)

    # Petit ménage : les anciennes versions de la même page ne servent plus.
    prefix = f"{project_key}_p{int(page_number):05d}_"
    try:
        olds = sorted((p for p in SNAPSHOT_DIR.glob(prefix + "*.webp") if p != target_path), key=lambda p: p.stat().st_mtime, reverse=True)
        for old in olds[2:]:
            old.unlink(missing_ok=True)
    except Exception:
        pass

    return f"_page_snapshots/{filename}"
