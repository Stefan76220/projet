from __future__ import annotations

"""TomeLinea V4 — Phase 2.6 : hôte WebView2 pour Canvas Editor.

L'hôte réutilise le runtime tkwry/WebView2 déjà embarqué par TomeLinea.
Il ne calcule ni retours à la ligne ni pagination : ces responsabilités restent
entièrement dans @hufe921/canvas-editor. Composition n'est rendue visible
qu'après le signal global ``render_complete`` du document.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from copy import deepcopy
import base64
import hashlib
import json
import os
import shutil
import sys
import tkinter as tk

from src.v4.canvas_editor_document import DOCUMENT_SCHEMA
from src.v4.canvas_loading import CanvasLoadSession, CanvasLoadStateError

ENGINE_NAME = "tomelinea.canvas_editor_webview_host"
ENGINE_VERSION = "9"
HOST_BOOT_MAX_PROBES = 80
HOST_BOOT_RETRY_MS = 100
CANVAS_EDITOR_VERSION = "1.0.2"
CANVAS_EDITOR_CDN = (
    "https://cdn.jsdelivr.net/npm/@hufe921/canvas-editor@1.0.2/"
    "dist/canvas-editor.js"
)


@dataclass(frozen=True, slots=True)
class CanvasWebAssets:
    root: Path
    index_html: Path
    host_js: Path
    vendor_js: Path
    vendor_license: Path
    runtime_python: Path
    tkwry_init: Path

    @classmethod
    def from_project(cls, project_root: str | Path) -> "CanvasWebAssets":
        root = Path(project_root).resolve()
        web = root / "src" / "gui_v4" / "web_canvas"
        runtime = root / "runtime" / "python"
        return cls(
            root=root,
            index_html=web / "index.html",
            host_js=web / "host.js",
            vendor_js=web / "vendor" / "canvas-editor.js",
            vendor_license=web / "vendor" / "LICENSE.canvas-editor.txt",
            runtime_python=runtime,
            tkwry_init=runtime / "tkwry" / "__init__.py",
        )

    def validation(self) -> dict[str, Any]:
        vendor_size = self.vendor_js.stat().st_size if self.vendor_js.is_file() else 0
        checks = {
            "index_html": self.index_html.is_file(),
            "host_js": self.host_js.is_file(),
            "vendor_js": self.vendor_js.is_file() and vendor_size >= 500_000,
            "vendor_license": self.vendor_license.is_file(),
            "runtime_python": self.runtime_python.is_dir(),
            "tkwry": self.tkwry_init.is_file(),
        }
        return {
            "valid": all(checks.values()),
            "checks": checks,
            "vendor_size_bytes": vendor_size,
            "canvas_editor_version": CANVAS_EDITOR_VERSION,
            "canvas_editor_cdn": CANVAS_EDITOR_CDN,
            "web_root": str(self.index_html.parent),
            "runtime_python": str(self.runtime_python),
        }


def activate_tkwry_runtime(project_root: str | Path) -> Path:
    assets = CanvasWebAssets.from_project(project_root)
    runtime = assets.runtime_python
    value = str(runtime)
    if runtime.is_dir() and value not in sys.path:
        sys.path.insert(0, value)
    return runtime


_WEB_PLAN_KEYS = (
    "schema",
    "schema_version",
    "engine",
    "render_segments",
    "persisted_editorial_choices",
    "visual_review",
    "tomelinea_ui",
    "tomelinea_chapter",
)
_RUNTIME_MEDIA_READY: set[str] = set()
_RUNTIME_MEDIA_THRESHOLD = 256 * 1024


def _runtime_media_root(project_root: str | Path) -> Path:
    web_root = Path(project_root).resolve() / "src" / "gui_v4" / "web_canvas"
    media_root = web_root / "_runtime_media"
    key = str(media_root).casefold()
    if key not in _RUNTIME_MEDIA_READY:
        try:
            shutil.rmtree(media_root)
        except FileNotFoundError:
            pass
        except OSError:
            # Un ancien fichier peut rester verrouillé quelques millisecondes
            # par WebView2. On ne bloque pas l'ouverture pour un cache.
            pass
        media_root.mkdir(parents=True, exist_ok=True)
        _RUNTIME_MEDIA_READY.add(key)
    return media_root


def _data_image_parts(value: str) -> tuple[str, bytes] | None:
    if not isinstance(value, str) or not value.startswith("data:image/"):
        return None
    try:
        header, encoded = value.split(",", 1)
    except ValueError:
        return None
    if ";base64" not in header.casefold():
        return None
    mime = header[5:].split(";", 1)[0].casefold()
    try:
        raw = base64.b64decode(encoded, validate=False)
    except Exception:
        return None
    if not raw:
        return None
    return mime, raw


def _externalize_large_images(value: Any, *, media_root: Path) -> None:
    if isinstance(value, list):
        for item in value:
            _externalize_large_images(item, media_root=media_root)
        return
    if not isinstance(value, dict):
        return

    if str(value.get("type") or "").casefold() == "image":
        image_value = value.get("value")
        if isinstance(image_value, str) and len(image_value) >= _RUNTIME_MEDIA_THRESHOLD:
            parsed = _data_image_parts(image_value)
            if parsed is not None:
                mime, raw = parsed
                ext = {
                    "image/png": ".png",
                    "image/jpeg": ".jpg",
                    "image/jpg": ".jpg",
                    "image/gif": ".gif",
                    "image/webp": ".webp",
                    "image/bmp": ".bmp",
                    "image/svg+xml": ".svg",
                }.get(mime, ".img")
                name = hashlib.sha256(raw).hexdigest() + ext
                destination = media_root / name
                if not destination.is_file() or destination.stat().st_size != len(raw):
                    temp = destination.with_suffix(destination.suffix + ".tmp")
                    temp.write_bytes(raw)
                    os.replace(temp, destination)
                # Le WebView est servi depuis web_canvas : URL relative même origine.
                value["value"] = f"_runtime_media/{name}"

    for item in value.values():
        _externalize_large_images(item, media_root=media_root)


def _plan_for_webview(plan: dict[str, Any], *, project_root: str | Path) -> dict[str, Any]:
    # Le navigateur n'utilise qu'une petite partie du plan. Ne jamais lui envoyer
    # logical_document, qui duplique intégralement le contenu de render_segments
    # et doublait notamment chaque image Base64.
    result = {
        key: deepcopy(plan[key])
        for key in _WEB_PLAN_KEYS
        if key in plan
    }

    media_root = _runtime_media_root(project_root)
    _externalize_large_images(result, media_root=media_root)
    return result


def _decode_eval_json_object(raw: Any) -> dict[str, Any]:
    """Décode les retours tkwry, parfois JSON-encodés deux fois."""
    value: Any = raw
    for _ in range(3):
        if isinstance(value, dict):
            return value
        if not isinstance(value, str) or not value:
            break
        try:
            value = json.loads(value)
        except (json.JSONDecodeError, TypeError):
            break
    return {"raw": str(value)}


def validate_host_plan(plan: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if plan.get("schema") != DOCUMENT_SCHEMA:
        errors.append("schema_document_invalide")
    strategy = plan.get("render_strategy", {})
    if strategy.get("pagination_owner") != "canvas-editor":
        errors.append("pagination_owner_invalide")
    if strategy.get("line_break_owner") != "canvas-editor":
        errors.append("line_break_owner_invalide")
    if strategy.get("manual_line_coordinates") is not False:
        errors.append("coordonnees_lignes_manuelles_interdites")
    segments = plan.get("render_segments", [])
    if not isinstance(segments, list) or not segments:
        errors.append("aucun_segment_rendu")
    return errors


class CanvasEditorWebHost(tk.Frame):
    """WebView enfant de TomeLinea qui héberge les segments Canvas Editor."""

    def __init__(
        self,
        master: tk.Misc,
        *,
        project_root: str | Path,
        on_ready: Callable[[dict[str, Any]], None] | None = None,
        on_failed: Callable[[dict[str, Any]], None] | None = None,
        on_editorial_choice: Callable[[dict[str, Any]], None] | None = None,
        on_page_changed: Callable[[dict[str, Any]], None] | None = None,
        on_page_count_changed: Callable[[dict[str, Any]], None] | None = None,
        background: str = "#252A30",
    ) -> None:
        super().__init__(master, bg=background, bd=0, highlightthickness=0)
        self.project_root = Path(project_root).resolve()
        self.assets = CanvasWebAssets.from_project(self.project_root)
        self._on_ready_callback = on_ready
        self._on_failed_callback = on_failed
        self._on_editorial_choice_callback = on_editorial_choice
        self._on_page_changed_callback = on_page_changed
        self._on_page_count_changed_callback = on_page_count_changed
        self._web = None
        self._page_loaded = False
        self._failed = False
        self._failure: dict[str, Any] | None = None
        self._plan: dict[str, Any] | None = None
        self._session: CanvasLoadSession | None = None
        self._pending_load = False
        self._host_loaded = False
        self._vendor_loaded = False
        self._last_probe: dict[str, Any] | None = None
        self._host_probe_attempts = 0
        self._table_first_row_orphan_fixes: list[dict[str, Any]] = []
        self._table_editorial_decisions: list[dict[str, Any]] = []
        self._table_pagination_probe: list[dict[str, Any]] = []
        self._visual_review: dict[str, Any] = {}
        self._editorial_choices_applied: list[dict[str, Any]] = []
        self._editorial_similar_choices_applied: list[dict[str, Any]] = []
        self._editorial_persisted_choices_restored: dict[str, Any] = {}
        self._active_page: int | None = None
        self._host_frame = tk.Frame(self, bg=background, bd=0, highlightthickness=0)
        self._host_frame.pack(fill="both", expand=True)

    @property
    def ready(self) -> bool:
        return bool(self._session and self._session.composition_visible and not self._failed)

    @property
    def page_count(self) -> int | None:
        return self._session.page_count if self._session else None

    def _ensure_webview(self) -> None:
        if self._web is not None:
            return
        validation = self.assets.validation()
        if not validation["valid"]:
            missing = [name for name, ok in validation["checks"].items() if not ok]
            raise RuntimeError("Ressources Canvas incomplètes : " + ", ".join(missing))

        activate_tkwry_runtime(self.project_root)
        from tkwry import WebView

        csp = (
            "default-src 'self' data: blob:; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: blob:; "
            "font-src 'self' data:; connect-src 'self'; "
            "worker-src 'self' blob:;"
        )
        web = WebView(
            self._host_frame,
            app=str(self.assets.index_html.parent),
            ipc_handler=self._handle_ipc,
            on_page_load=self._on_page_load,
            on_title_changed=self._on_document_title,
            on_creation_failed=self._on_creation_failed,
            background_color=(37, 42, 48, 255),
            focused=False,
            devtools=False,
            csp=csp,
        )
        web.pack(fill="both", expand=True)
        try:
            web.when_ready(self._on_web_ready)
        except Exception:
            pass
        try:
            web.when_failed(self._on_creation_failed)
        except Exception:
            pass
        self._web = web

    def _on_document_title(self, title: str) -> None:
        """Consomme les notifications de titre sans changer la fenetre Tk."""
        self._document_title = str(title)

    def load_document(
        self,
        plan: dict[str, Any],
        session: CanvasLoadSession,
        *,
        on_ready: Callable[[dict[str, Any]], None] | None = None,
        on_failed: Callable[[dict[str, Any]], None] | None = None,
    ) -> None:
        errors = validate_host_plan(plan)
        if errors:
            raise ValueError("Plan Canvas invalide : " + ", ".join(errors))
        if session.contract.get("readiness", {}).get("composition_visible"):
            raise ValueError("La session initiale ne doit pas être visible.")

        # Un même WebView sert successivement aux unités de pré-pagination.
        # Le JS détruit déjà l'éditeur Canvas courant avant de charger le suivant.
        # On réinitialise donc l'état du document, pas le moteur natif WebView2.
        if on_ready is not None:
            self._on_ready_callback = on_ready
        if on_failed is not None:
            self._on_failed_callback = on_failed
        self._failed = False
        self._failure = None
        self._plan = plan
        self._session = session
        self._pending_load = True
        self._host_probe_attempts = 0
        self._last_probe = None
        self._table_first_row_orphan_fixes = []
        self._table_editorial_decisions = []
        self._table_pagination_probe = []
        self._visual_review = {}
        self._editorial_choices_applied = []
        self._editorial_similar_choices_applied = []
        self._editorial_persisted_choices_restored = {}
        self._active_page = None
        self._ensure_webview()
        if self._page_loaded:
            self.after_idle(self._push_plan)

    def _on_web_ready(self, *_args) -> None:
        if self._pending_load:
            self.after(30, self._push_plan)

    def _on_page_load(self, *_args) -> None:
        self._page_loaded = True
        if self._pending_load:
            self.after(30, self._push_plan)

    def _push_plan(self) -> None:
        if not self._pending_load or self._web is None or self._plan is None:
            return

        # Avant d'envoyer le gros document, vérifier que host.js a réellement
        # fini de s'initialiser. L'ancienne version utilisait un && silencieux :
        # si le module JS n'était pas chargé, rien ne se passait jusqu'au timeout.
        probe_script = (
            "JSON.stringify({"
            "load:typeof window.tomeLineaCanvasLoad,"
            "status:typeof window.tomeLineaCanvasStatus,"
            "boot:window.tomeLineaCanvasBoot||null,"
            "ipc:!!(window.ipc&&typeof window.ipc.postMessage==='function'),"
            "href:location.href,"
            "inlineHost:!!window.__TL_INLINE_HOST__"
            "})"
        )
        try:
            self._web.eval_js_with_callback(
                probe_script,
                self._on_host_probe,
                on_error=self._on_eval_failed,
            )
        except TypeError:
            # Compatibilité défensive si la signature locale ne prend pas on_error.
            self._web.eval_js_with_callback(probe_script, self._on_host_probe)
        except Exception as exc:
            self._fail("host_probe", exc)

    def _on_host_probe(self, raw: Any = None, *_args) -> None:
        if not self._pending_load or self._web is None or self._plan is None:
            return
        self._last_probe = _decode_eval_json_object(raw)

        if self._last_probe.get("load") != "function":
            # WebView2 signale parfois « ready » alors qu'il affiche encore
            # about:blank. C'est particulièrement visible après une nouvelle
            # analyse déclenchée depuis l'écran « Composition suspendue ».
            # Ne jamais transformer ce délai normal de navigation en blocage.
            self._host_probe_attempts += 1
            if self._host_probe_attempts < HOST_BOOT_MAX_PROBES:
                self.after(HOST_BOOT_RETRY_MS, self._push_plan)
                return
            self._fail(
                "host_boot",
                "Bootstrap Canvas non initialisé après attente : "
                + json.dumps(self._last_probe, ensure_ascii=False),
            )
            return

        self._host_probe_attempts = 0
        try:
            web_plan = _plan_for_webview(self._plan, project_root=self.project_root)
        except Exception as exc:
            self._fail("font_prepare", exc)
            return
        payload = json.dumps(web_plan, ensure_ascii=False, separators=(",", ":"))
        script = (
            "Promise.resolve(window.tomeLineaCanvasLoad("
            + payload
            + ")); true;"
        )
        try:
            # Navigation sans résultat : tkwry coalesce nativement les eval_js
            # rapides (last-wins). Ne jamais utiliser eval_js_with_callback ici.
            self._web.eval_js(script, on_error=self._on_eval_failed)
            self._web.sync_bounds()
            self._pending_load = False
        except Exception as exc:
            self._fail("push_plan", exc)

    def _on_eval_failed(self, exc=None, *_args) -> None:
        self._fail("eval_js", exc or "Échec JavaScript")

    def _on_creation_failed(self, exc=None, *_args) -> None:
        self._fail("webview_create", exc or "WebView2 non créé")

    def _fail(self, stage: str, error: Any) -> None:
        if self._failed:
            return
        self._failed = True
        self._failure = {"stage": str(stage), "message": str(error)}
        if self._session is not None:
            self._session.fail(str(stage), str(error))
        if callable(self._on_failed_callback):
            self.after_idle(lambda: self._on_failed_callback(dict(self._failure or {})))

    def _handle_ipc(self, message: str) -> None:
        try:
            data = json.loads(message) if isinstance(message, str) else message
        except Exception:
            return
        if not isinstance(data, dict):
            return
        event = str(data.get("type") or "")
        session = self._session
        if session is None:
            return
        try:
            if event == "host_loaded":
                self._host_loaded = True
            elif event == "vendor_loaded":
                self._vendor_loaded = True
            elif event == "canvas_created":
                session.mark_canvas_created()
            elif event == "fonts_loaded":
                session.mark_fonts_loaded()
            elif event == "layout_complete":
                session.mark_layout_complete()
            elif event == "pagination_stable":
                raw = data.get("pageCount")
                page_count = int(raw) if raw is not None else None
                session.mark_pagination_stable(page_count)
            elif event == "table_pagination_probe":
                self._table_pagination_probe.append({k: v for k, v in data.items() if k != "type"})
            elif event == "table_first_row_orphan_fixed":
                self._table_first_row_orphan_fixes.append({k: v for k, v in data.items() if k != "type"})
            elif event == "table_editorial_decision_required":
                self._table_editorial_decisions.append({k: v for k, v in data.items() if k != "type"})
            elif event == "visual_review_ready":
                self._visual_review = {k: v for k, v in data.items() if k != "type"}
            elif event == "editorial_choice_applied":
                choice_event = {k: v for k, v in data.items() if k != "type"}
                self._editorial_choices_applied.append(choice_event)
                if callable(self._on_editorial_choice_callback):
                    self.after_idle(lambda event=dict(choice_event): self._on_editorial_choice_callback(event))
            elif event == "editorial_similar_choice_applied":
                self._editorial_similar_choices_applied.append({k: v for k, v in data.items() if k != "type"})
            elif event == "editorial_persisted_choices_restored":
                self._editorial_persisted_choices_restored = {k: v for k, v in data.items() if k != "type"}
            elif event == "page_count_changed":
                raw_count = data.get("pageCount")
                try:
                    page_count = int(raw_count)
                except (TypeError, ValueError):
                    page_count = 0
                if page_count > 0 and callable(self._on_page_count_changed_callback):
                    event_data = {k: v for k, v in data.items() if k != "type"}
                    self.after_idle(lambda event=dict(event_data): self._on_page_count_changed_callback(event))
            elif event == "page_changed":
                raw_page = data.get("pageNo")
                try:
                    page_no = int(raw_page)
                except (TypeError, ValueError):
                    page_no = 0
                if page_no > 0:
                    self._active_page = page_no
                    if callable(self._on_page_changed_callback):
                        event_data = {k: v for k, v in data.items() if k != "type"}
                        self.after_idle(lambda event=dict(event_data): self._on_page_changed_callback(event))
            elif event == "render_complete":
                session.mark_render_complete()
                if callable(self._on_ready_callback):
                    snapshot = session.snapshot()
                    self.after_idle(lambda: self._on_ready_callback(snapshot))
            elif event == "error":
                self._fail(str(data.get("stage") or "javascript"), data.get("message") or "Erreur Canvas")
        except (CanvasLoadStateError, ValueError, TypeError) as exc:
            self._fail("lifecycle", exc)


    def go_to_page(self, page_no: int, *, smooth: bool = True) -> None:
        """Centre la page physique demandée dans le Canvas sans recalculer la mise en page."""
        if self._web is None or not self.ready:
            return
        try:
            target = max(1, int(page_no))
        except (TypeError, ValueError):
            return
        behavior = "smooth" if smooth else "auto"
        self._active_page = target
        script = (
            "window.tomeLineaCanvasGoToPage && "
            f"window.tomeLineaCanvasGoToPage({target}, {json.dumps(behavior)}); true;"
        )
        try:
            # Navigation sans résultat : tkwry coalesce nativement les eval_js
            # rapides (last-wins). Aucun callback, aucun redimensionnement natif.
            self._web.eval_js(script, on_error=self._on_eval_failed)
        except Exception as exc:
            self._fail("page_navigation", exc)

    def export_document_state(
        self,
        callback: Callable[[dict[str, Any]], None],
        *,
        freeze_visual: bool = False,
    ) -> None:
        """Retourne l'état édité du Canvas sans toucher à la Source.

        Utilisé par l'architecture par chapitre avant de détruire le WebView
        actif. Le prochain chargement du même chapitre repart alors de cette
        copie de travail en mémoire.
        """
        if self._web is None or not self.ready:
            self.after_idle(lambda: callback({"ok": False, "reason": "not_ready"}))
            return

        freeze_script = (
            "try{window.tomeLineaCanvasFreezeCurrentPage&&"
            "window.tomeLineaCanvasFreezeCurrentPage();}catch(_){ }"
            if freeze_visual
            else ""
        )
        script = (
            "JSON.stringify((()=>{"
            + freeze_script
            + "return window.tomeLineaCanvasExportState ? "
            "window.tomeLineaCanvasExportState() : "
            "{ok:false,reason:'export_api_missing'};})());"
        )

        def _done(raw: Any = None, *_args) -> None:
            value = _decode_eval_json_object(raw)
            try:
                self.after_idle(lambda data=dict(value): callback(data))
            except Exception:
                callback(dict(value))

        try:
            self._web.eval_js_with_callback(
                script,
                _done,
                on_error=lambda exc=None, *_args: self.after_idle(
                    lambda: callback({
                        "ok": False,
                        "reason": "eval_error",
                        "message": str(exc or "Erreur JavaScript"),
                    })
                ),
            )
        except TypeError:
            self._web.eval_js_with_callback(script, _done)
        except Exception as exc:
            self.after_idle(lambda: callback({
                "ok": False,
                "reason": "exception",
                "message": str(exc),
            }))

    def show_when_ready(self, **place_kwargs: Any) -> None:
        if not self.ready:
            raise RuntimeError("Composition ne peut pas être affichée avant render_complete.")
        if place_kwargs:
            self.place(**place_kwargs)
        else:
            self.place(x=0, y=0, relwidth=1, relheight=1)
        self.tk.call("raise", self._w)
        try:
            if self._web is not None:
                self._web.sync_bounds()
                mode = str(((self._plan or {}).get("tomelinea_ui") or {}).get("mode") or "")
                if mode == "embedded_composition":
                    # Dans la vraie Composition, le Canvas affiche la page mais
                    # ne vole ni le clavier ni la souris à TomeLinea.
                    try:
                        self._web.focus_parent()
                    except Exception:
                        pass
                else:
                    self._web.focus()
        except Exception:
            pass

    def hide(self) -> None:
        try:
            if self._web is not None:
                self._web.focus_parent()
        except Exception:
            pass
        self.place_forget()

    def shutdown(self) -> None:
        web = self._web
        self._web = None
        if web is not None:
            try:
                web.destroy()
            except Exception:
                pass

    def snapshot(self) -> dict[str, Any]:
        return {
            "engine": {"name": ENGINE_NAME, "version": ENGINE_VERSION},
            "assets": self.assets.validation(),
            "page_loaded": self._page_loaded,
            "host_loaded": self._host_loaded,
            "vendor_loaded": self._vendor_loaded,
            "last_probe": self._last_probe,
            "table_first_row_orphan_fixes": list(self._table_first_row_orphan_fixes),
            "table_editorial_decisions": list(self._table_editorial_decisions),
            "table_pagination_probe": list(self._table_pagination_probe),
            "visual_review": dict(self._visual_review),
            "editorial_choices_applied": list(self._editorial_choices_applied),
            "editorial_similar_choices_applied": list(self._editorial_similar_choices_applied),
            "editorial_persisted_choices_restored": dict(self._editorial_persisted_choices_restored),
            "active_page": self._active_page,
            "failed": self._failed,
            "failure": self._failure,
            "ready": self.ready,
            "page_count": self.page_count,
            "session": self._session.snapshot() if self._session else None,
        }
