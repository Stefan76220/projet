from __future__ import annotations

import base64
import json
import os
import sys
import time
import tkinter as tk
from pathlib import Path
from tkinter import messagebox

from src.gui_v3.startup_runtime import RUNTIME_PY, WEB_ROOT, activate_local_runtime


class Viewer3DOverlay(tk.Frame):
    """Visionneur 3D enfant de TomeLinea, sans fenêtre navigateur externe."""

    def __init__(self, master: tk.Misc, *, on_return=None, on_action=None, on_navigate=None, bg: str = "#222831") -> None:
        super().__init__(master, bg=bg, bd=0, highlightthickness=0)
        self._on_return = on_return
        self._on_action = on_action
        self._on_navigate = on_navigate
        self._origin_tab = "structure"
        self._current_page = 1
        self._page_count = 1
        self._pages_info: list[dict] = []
        self._can_undo = False
        self._can_redo = False
        self._web = None
        self._host = tk.Frame(self, bg=bg, bd=0, highlightthickness=0)
        self._host.pack(fill="both", expand=True)
        self._failed = False
        self._failure_detail = ""
        self._page_loaded = False
        self._returning = False
        self._pending_configure = False
        self._texture_payloads: dict[int, str] = {}
        self._texture_push_generation = 0
        self._bridge_reload_count = 0
        self._texture_push_active: set[tuple[int, int]] = set()

    @property
    def active(self) -> bool:
        try:
            return bool(self.winfo_ismapped())
        except Exception:
            return False

    def _ensure_runtime_path(self) -> None:
        activate_local_runtime()
        value = str(RUNTIME_PY)
        if RUNTIME_PY.is_dir() and value not in sys.path:
            sys.path.insert(0, value)

    def _ensure_webview(self) -> bool:
        if self._web is not None:
            return True
        if self._failed:
            self._show_failure()
            return False

        self._ensure_runtime_path()
        try:
            from tkwry import WebView
        except Exception as exc:
            self._failed = True
            self._failure_detail = (
                "Le moteur interne du Visionneur n'est pas disponible.\n\n"
                "Ferme TomeLinea puis relance-le : la fenêtre de lancement "
                "tentera de préparer le composant automatiquement.\n\n"
                f"Détail : {type(exc).__name__}: {exc}"
            )
            self._show_failure()
            return False

        if not (WEB_ROOT / "index.html").is_file():
            self._failed = True
            self._failure_detail = "Le fichier interne du Visionneur est introuvable."
            self._show_failure()
            return False

        try:
            csp = (
                "default-src 'self' data: blob:; "
                "script-src 'self' 'unsafe-inline'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: blob:; "
                "connect-src 'self'; font-src 'self' data:;"
            )
            web = WebView(
                self._host,
                app=str(WEB_ROOT),
                app_dev=True,
                ipc_handler=self._handle_ipc,
                on_page_load=self._on_page_load,
                on_creation_failed=self._on_creation_failed,
                background_color=(34, 40, 49, 255),
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
            return True
        except Exception as exc:
            self._failed = True
            self._failure_detail = (
                "Impossible d'initialiser le Visionneur interne.\n\n"
                f"Détail : {type(exc).__name__}: {exc}"
            )
            self._show_failure()
            return False

    def _on_creation_failed(self, exc=None, *_args) -> None:
        self._failed = True
        detail = str(exc or "Erreur inconnue")
        self._failure_detail = (
            "Le moteur WebView2 n'a pas pu être créé. TomeLinea reste actif.\n\n"
            "Ferme puis relance TomeLinea afin que la fenêtre de lancement "
            "puisse vérifier les moteurs.\n\n"
            f"Détail : {detail}"
        )
        self.after_idle(self._show_failure)

    def _show_failure(self) -> None:
        if not self._failure_detail:
            return
        try:
            self.place_forget()
        except Exception:
            pass
        messagebox.showerror(
            "Visionneur TomeLinea",
            self._failure_detail,
            parent=self.winfo_toplevel(),
        )

    def _on_web_ready(self, *_args) -> None:
        self._pending_configure = True
        self.after(80, self._configure_webview)

    def _on_page_load(self, *_args) -> None:
        self._page_loaded = True
        self._pending_configure = True
        self.after(80, self._configure_webview)

    def _prepare_pages_info(self, pages_info: list[dict] | None) -> list[dict]:
        """Sépare les métadonnées du livre des pixels des pages.

        Les textures restent côté Python. Three.js demande seulement les pages
        visibles via l'IPC déjà utilisé par le Visionneur ; Python les transmet
        ensuite en fragments JavaScript séquentiels accusés réception. On évite
        ainsi les URL de fichiers, les gros scripts et un protocole RPC distinct.
        """
        rows = [dict(value) for value in (pages_info or []) if isinstance(value, dict)]
        payloads: dict[int, str] = {}

        for row in rows:
            raw = str(row.get("textureData") or "").strip()
            row.pop("textureUrl", None)
            row.pop("textureData", None)
            if not raw.startswith("data:image/png;base64,"):
                row["hasTexture"] = False
                continue
            try:
                encoded = raw.split(",", 1)[1]
                png = base64.b64decode(encoded, validate=True)
                if not png.startswith(b"\x89PNG\r\n\x1a\n"):
                    raise ValueError("texture non PNG")
                page_no = max(1, int(row.get("number") or 1))
            except Exception:
                row["hasTexture"] = False
                continue
            payloads[page_no] = encoded
            row["hasTexture"] = True

        self._texture_payloads = payloads
        self._texture_push_generation = int(getattr(self, "_texture_push_generation", 0) or 0) + 1
        self._trace_texture(
            f"generation {self._texture_push_generation} preparee : "
            + ", ".join(f"p{n}={len(data)}" for n, data in sorted(payloads.items()))
        )
        return rows

    def _trace_texture(self, message: str) -> None:
        """Trace courte du trajet réel des textures, uniquement dans cache/."""
        try:
            root = Path(__file__).resolve().parents[2]
            path = root / "cache" / "viewer3d_texture_trace.log"
            path.parent.mkdir(parents=True, exist_ok=True)
            stamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with path.open("a", encoding="utf-8") as stream:
                stream.write(f"[{stamp}] {str(message)}\n")
        except Exception:
            pass

    def _queue_page_texture_push(self, page_number: int, generation: int) -> None:
        """Transmet une texture par petits scripts JS accusés réception.

        Le Visionneur utilise déjà ``window.ipc`` pour ses commandes et
        ``eval_js_with_callback`` pour sa configuration. On réutilise donc
        uniquement ces deux chemins éprouvés au lieu d'ajouter un troisième
        protocole de transport pour les pixels. Chaque fragment est envoyé
        seulement après l'accusé de réception du précédent.
        """
        try:
            page_no = max(1, int(page_number or 1))
            requested_generation = int(generation or 0)
        except Exception:
            return
        current_generation = int(getattr(self, "_texture_push_generation", 0) or 0)
        if requested_generation != current_generation:
            return
        encoded = str(dict(getattr(self, "_texture_payloads", {}) or {}).get(page_no) or "")
        if not encoded:
            self._notify_texture_failure(page_no, current_generation, "missing")
            return
        key = (page_no, current_generation)
        active = getattr(self, "_texture_push_active", None)
        if not isinstance(active, set):
            active = set()
            self._texture_push_active = active
        if key in active:
            return
        self._trace_texture(f"demande page {page_no} generation {current_generation} ({len(encoded)} caracteres)")
        active.add(key)
        self.after_idle(lambda: self._push_page_texture(page_no, current_generation, encoded))

    def _push_page_texture(self, page_no: int, generation: int, encoded: str) -> None:
        web = self._web
        key = (int(page_no), int(generation))
        if web is None or self._failed:
            self._texture_push_active.discard(key)
            return
        if generation != int(getattr(self, "_texture_push_generation", 0) or 0):
            self._texture_push_active.discard(key)
            return

        # 48 Kio de Base64 donnent des scripts très petits par rapport aux
        # limites de WebView2/tkwry et évitent tout écrasement de file.
        chunk_size = 48 * 1024
        chunks = [encoded[i:i + chunk_size] for i in range(0, len(encoded), chunk_size)]

        def fail(_exc=None, reason: str = "transport") -> None:
            self._texture_push_active.discard(key)
            self._trace_texture(f"echec transport page {page_no} generation {generation} : {reason} {_exc!r}")
            self._notify_texture_failure(page_no, generation, reason)

        def send_end() -> None:
            if generation != int(getattr(self, "_texture_push_generation", 0) or 0):
                self._texture_push_active.discard(key)
                return
            script = (
                "window.tomeLineaViewerTextureEnd&&"
                f"window.tomeLineaViewerTextureEnd({int(page_no)},{int(generation)})"
            )

            def ended(_result: str = "") -> None:
                self._texture_push_active.discard(key)
                self._trace_texture(f"transfert JS termine page {page_no} generation {generation} resultat={_result!r}")

            try:
                web.eval_js_with_callback(script, ended, on_error=fail)
            except Exception as exc:
                fail(exc, "end")

        def send_chunk(index: int) -> None:
            if generation != int(getattr(self, "_texture_push_generation", 0) or 0):
                self._texture_push_active.discard(key)
                return
            if index >= len(chunks):
                send_end()
                return
            payload = json.dumps(chunks[index])
            script = (
                "window.tomeLineaViewerTextureChunk&&"
                f"window.tomeLineaViewerTextureChunk({int(page_no)},{int(generation)},{payload})"
            )

            def sent(_result: str = "", next_index: int = index + 1) -> None:
                send_chunk(next_index)

            try:
                web.eval_js_with_callback(script, sent, on_error=fail)
            except Exception as exc:
                fail(exc, f"chunk-{index}")

        begin_script = (
            "window.tomeLineaViewerTextureBegin&&"
            f"window.tomeLineaViewerTextureBegin({int(page_no)},{int(generation)},{len(encoded)})"
        )

        def begun(_result: str = "") -> None:
            send_chunk(0)

        try:
            web.eval_js_with_callback(begin_script, begun, on_error=fail)
        except Exception as exc:
            fail(exc, "begin")

    def _notify_texture_failure(self, page_no: int, generation: int, reason: str) -> None:
        web = self._web
        if web is None or self._failed:
            return
        payload = json.dumps(str(reason or "inconnue"))
        script = (
            "window.tomeLineaViewerTextureFailed&&"
            f"window.tomeLineaViewerTextureFailed({int(page_no)},{int(generation)},{payload})"
        )
        try:
            web.eval_js_with_callback(script, lambda _result: None, on_error=lambda _exc: None)
        except Exception:
            pass

    def _configure_webview(self) -> None:
        web = self._web
        if web is None or self._failed:
            return
        self._pending_configure = False
        generation = int(getattr(self, "_texture_push_generation", 0) or 0)
        payload = json.dumps(
            {
                "pageCount": max(1, int(self._page_count or 1)),
                "startPage": max(1, int(self._current_page or 1)),
                "pages": list(self._pages_info or []),
                "canUndo": bool(self._can_undo),
                "canRedo": bool(self._can_redo),
                "textureGeneration": generation,
            },
            ensure_ascii=False,
        )
        script = (
            "(()=>{if(window.TOMELINEA_VIEWER_TEXTURE_BRIDGE!==212)return false;"
            "if(!window.tomeLineaViewerConfigure)return false;"
            f"window.tomeLineaViewerConfigure({payload});return true;}})()"
        )

        def _configured(result: str = "") -> None:
            # Le callback vérifie aussi la version du code réellement chargé
            # dans WebView2. Cela évite qu'un index.html ancien resté en cache
            # fasse croire qu'un correctif est actif alors qu'il ne l'est pas.
            if generation != int(getattr(self, "_texture_push_generation", 0) or 0):
                return
            if str(result or "").strip().lower() in {"false", "null", "undefined", ""}:
                _reload_bridge()
                return
            self._bridge_reload_count = 0
            try:
                if self._web is not None:
                    self._web.sync_bounds()
                    self._web.focus()
            except Exception:
                pass

        def _reload_bridge() -> None:
            web_now = self._web
            if web_now is None or self._failed:
                return
            attempts = int(getattr(self, "_bridge_reload_count", 0) or 0)
            if attempts < 2:
                self._bridge_reload_count = attempts + 1
                try:
                    web_now.reload()
                    return
                except Exception:
                    pass
            _configure_failed()

        def _configure_failed(_exc=None) -> None:
            if self.active and not self._pending_configure:
                self._pending_configure = True
                self.after(250, self._configure_webview)

        try:
            web.eval_js_with_callback(script, _configured, on_error=_configure_failed)
        except Exception:
            _configure_failed()

    def _handle_ipc(self, message: str) -> None:
        try:
            data = json.loads(message) if isinstance(message, str) else message
        except Exception:
            return
        if not isinstance(data, dict):
            return
        kind = str(data.get("type", ""))
        if kind == "texture_request":
            try:
                page_no = int(data.get("page") or 0)
                generation = int(data.get("generation") or 0)
            except Exception:
                return
            self._queue_page_texture_push(page_no, generation)
            return
        if kind == "texture_status":
            self._trace_texture(
                f"etat JS page {data.get('page')} generation {data.get('generation')} : "
                f"{data.get('status')} {data.get('reason') or ''} "
                f"{data.get('width') or ''}x{data.get('height') or ''}"
            )
            # Le JavaScript affiche lui-même une alerte visuelle uniquement en cas d'échec.
            return
        if kind == "page":
            candidates = (data.get("current"), data.get("left"), data.get("right"))
            for raw in candidates:
                try:
                    value = int(raw)
                except Exception:
                    continue
                if value > 0:
                    self._current_page = min(max(1, value), max(1, self._page_count))
                    break
            return
        if kind == "action":
            action = str(data.get("action") or "").strip()
            try:
                page = int(data.get("page") or self._current_page)
            except Exception:
                page = self._current_page
            if action and callable(self._on_action):
                self.after_idle(lambda a=action, p=page: self._run_action(a, p))
            return
        if kind == "navigate":
            target = str(data.get("target") or "").strip().lower()
            if target not in {"structure", "gabarits", "production", "sortie"}:
                return
            try:
                page = int(data.get("page") or self._current_page)
            except Exception:
                page = self._current_page
            self._current_page = min(max(1, page), max(1, self._page_count))
            if self._returning:
                return
            self._returning = True
            self.after_idle(lambda t=target, p=self._current_page: self._navigate_to_workspace(t, p))
            return
        if kind == "return":
            if self._returning:
                return
            try:
                page = int(data.get("page") or self._current_page)
            except Exception:
                page = self._current_page
            self._current_page = min(max(1, page), max(1, self._page_count))
            self._returning = True
            self.after_idle(lambda: self.hide(return_to_origin=True))

    def _navigate_to_workspace(self, target_tab: str, page: int) -> None:
        try:
            if self._web is not None:
                self._web.focus_parent()
        except Exception:
            pass
        try:
            self.place_forget()
        except Exception:
            pass

        def _navigate() -> None:
            try:
                if callable(self._on_navigate):
                    self._on_navigate(str(target_tab or "structure"), int(page or 1))
            finally:
                self.after(180, self._clear_return_guard)

        self.after_idle(_navigate)

    def _run_action(self, action: str, page: int) -> None:
        try:
            result = self._on_action(action, page) if callable(self._on_action) else None
        except Exception as exc:
            result = {"ok": False, "message": f"Action impossible : {exc}"}
        if not isinstance(result, dict):
            return
        try:
            self._page_count = max(1, int(result.get("page_count") or self._page_count or 1))
            self._current_page = min(max(1, int(result.get("page") or page or 1)), self._page_count)
        except Exception:
            pass
        pages = result.get("pages_info")
        if isinstance(pages, list):
            self._pages_info = self._prepare_pages_info(pages)
        if "can_undo" in result:
            self._can_undo = bool(result.get("can_undo"))
        if "can_redo" in result:
            self._can_redo = bool(result.get("can_redo"))
        self._configure_webview()
        message = str(result.get("message") or "").strip()
        if message and self._web is not None:
            payload = json.dumps({"ok": bool(result.get("ok", False)), "message": message}, ensure_ascii=False)
            try:
                self._web.eval_js(f"window.tomeLineaViewerActionResult && window.tomeLineaViewerActionResult({payload});", on_error=lambda _exc: None)
            except Exception:
                pass

    def prewarm(self, *, timeout_ms: int = 12000, progress=None) -> bool:
        """Crée et charge le vrai Visionneur avant que TomeLinea soit affiché.

        Le WebView utilisé ensuite par l'utilisateur est exactement celui-ci :
        on ne détruit donc pas le moteur après la préparation.
        """
        if self._web is not None and self._page_loaded and not self._failed:
            return True

        top = self.winfo_toplevel()
        self._page_count = max(1, int(self._page_count or 1))
        self._current_page = max(1, int(self._current_page or 1))

        # Le parent est momentanément mappé hors écran par TomeLinea. Cela
        # donne à tkwry un vrai HWND et des dimensions réelles, nécessaires
        # pour initialiser WebView2 et charger Three.js pendant le lancement.
        self.place(x=0, y=0, relwidth=1, relheight=1)
        self.tk.call("raise", self._w)
        try:
            top.update_idletasks()
            top.update()
        except Exception:
            pass

        if callable(progress):
            try:
                progress("Visionneur", "Initialisation du moteur WebView2…")
            except Exception:
                pass

        if not self._ensure_webview():
            try:
                self.place_forget()
            except Exception:
                pass
            return False

        try:
            if self._web is not None:
                self._web.sync_bounds()
        except Exception:
            pass

        deadline = time.monotonic() + max(1.0, timeout_ms / 1000.0)
        while not self._page_loaded and not self._failed and time.monotonic() < deadline:
            try:
                top.update_idletasks()
                top.update()
            except Exception:
                break
            time.sleep(0.015)

        # Laisse passer quelques trames : le premier rendu Three.js et la
        # compilation des shaders ont ainsi lieu dans la fenêtre de préparation.
        if self._page_loaded and not self._failed:
            if callable(progress):
                try:
                    progress("Visionneur", "Préparation du rendu 3D…")
                except Exception:
                    pass
            settle_until = min(deadline, time.monotonic() + 0.55)
            while time.monotonic() < settle_until:
                try:
                    top.update_idletasks()
                    top.update()
                except Exception:
                    break
                time.sleep(0.015)

        try:
            if self._web is not None:
                self._web.focus_parent()
        except Exception:
            pass
        try:
            self.place_forget()
        except Exception:
            pass

        return bool(self._page_loaded and not self._failed)

    def show(
        self,
        *,
        origin_tab: str,
        page: int,
        page_count: int,
        pages_info: list[dict] | None = None,
        can_undo: bool = False,
        can_redo: bool = False,
    ) -> None:
        self._returning = False
        self._origin_tab = str(origin_tab or "structure")
        self._page_count = max(1, int(page_count or 1))
        self._current_page = min(max(1, int(page or 1)), self._page_count)
        self._pages_info = self._prepare_pages_info(pages_info)
        self._can_undo = bool(can_undo)
        self._can_redo = bool(can_redo)

        # Le Frame couvre la pile TomeLinea ; la WebView reste un véritable
        # enfant natif de ce Frame et non une seconde application Windows.
        self.place(x=0, y=0, relwidth=1, relheight=1)
        self.tk.call("raise", self._w)
        self.update_idletasks()

        if not self._ensure_webview():
            return
        self.after(80, self._configure_webview)

    def hide(self, *, return_to_origin: bool = False) -> None:
        try:
            if self._web is not None:
                self._web.focus_parent()
        except Exception:
            pass
        self.place_forget()

        if return_to_origin and callable(self._on_return):
            origin = self._origin_tab
            page = self._current_page

            def _return() -> None:
                try:
                    self._on_return(origin, page)
                finally:
                    self.after(180, self._clear_return_guard)

            self.after_idle(_return)
        else:
            self.after(180, self._clear_return_guard)

    def _clear_return_guard(self) -> None:
        self._returning = False

    def shutdown(self) -> None:
        web = self._web
        self._web = None
        if web is not None:
            try:
                web.destroy()
            except Exception:
                pass
