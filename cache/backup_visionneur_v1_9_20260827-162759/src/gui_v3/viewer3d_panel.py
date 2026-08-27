from __future__ import annotations

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
        self._web = None
        self._host = tk.Frame(self, bg=bg, bd=0, highlightthickness=0)
        self._host.pack(fill="both", expand=True)
        self._failed = False
        self._failure_detail = ""
        self._page_loaded = False
        self._returning = False
        self._pending_configure = False

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

    def _configure_webview(self) -> None:
        web = self._web
        if web is None or self._failed:
            return
        self._pending_configure = False
        payload = json.dumps(
            {
                "pageCount": max(1, int(self._page_count or 1)),
                "startPage": max(1, int(self._current_page or 1)),
                "pages": list(self._pages_info or []),
                "canUndo": bool(self._can_undo),
            },
            ensure_ascii=False,
        )
        script = (
            "window.tomeLineaViewerConfigure && "
            f"window.tomeLineaViewerConfigure({payload});"
        )
        try:
            web.eval_js(script, on_error=lambda _exc: None)
            web.sync_bounds()
            web.focus()
        except Exception:
            # Un premier appel peut arriver pendant la navigation. Le callback
            # on_page_load réessaie ensuite sans reconstruire le moteur.
            if self.active and not self._pending_configure:
                self._pending_configure = True
                self.after(250, self._configure_webview)

    def _handle_ipc(self, message: str) -> None:
        try:
            data = json.loads(message) if isinstance(message, str) else message
        except Exception:
            return
        if not isinstance(data, dict):
            return
        kind = str(data.get("type", ""))
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
            self._pages_info = [dict(value) for value in pages if isinstance(value, dict)]
        if "can_undo" in result:
            self._can_undo = bool(result.get("can_undo"))
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
    ) -> None:
        self._returning = False
        self._origin_tab = str(origin_tab or "structure")
        self._page_count = max(1, int(page_count or 1))
        self._current_page = min(max(1, int(page or 1)), self._page_count)
        self._pages_info = [dict(value) for value in (pages_info or []) if isinstance(value, dict)]
        self._can_undo = bool(can_undo)

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
