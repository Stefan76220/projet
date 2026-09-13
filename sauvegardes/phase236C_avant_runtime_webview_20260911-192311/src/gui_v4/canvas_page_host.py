# -*- coding: utf-8 -*-
"""TomeLinea V4 - hôte Canvas Editor / WebView2.

Version 11 — zoom 150 % ouvert depuis le haut :
- attend une vraie taille Tk avant création de WebView2 ;
- sert la page sur localhost au lieu d'un HTML opaque ;
- attend que Canvas Editor soit réellement prêt avant les commandes TL ;
- affiche une erreur visible au centre au lieu de laisser une zone vide ;
- conserve l'API utilisée par editorial_shell.py.
"""

from __future__ import annotations

import json
import socket
import threading
import tkinter as tk
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Callable

try:
    from tkwry import WebView
except Exception as exc:
    WebView = None
    _TKWRY_IMPORT_ERROR = exc
else:
    _TKWRY_IMPORT_ERROR = None


MM_TO_PX = 96.0 / 25.4


def _mm_px(value: float) -> float:
    return max(0.0, float(value)) * MM_TO_PX


def _plain_text_to_elements(text: str) -> list[dict[str, Any]]:
    value = str(text or "")
    if not value:
        return [{"value": ""}]

    result: list[dict[str, Any]] = []
    for line in value.splitlines(keepends=True):
        body = line.rstrip("\r\n")
        ending = len(line) != len(body)
        if body:
            result.append({"value": body})
        if ending:
            result.append({"value": "\n"})
    return result or [{"value": ""}]


def _editor_data_from_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    saved = metadata.get("canvas_editor_value")
    if isinstance(saved, dict):
        data = saved.get("data")
        if isinstance(data, dict) and isinstance(data.get("main"), list):
            return data

    return {
        "header": [],
        "main": _plain_text_to_elements(metadata.get("plain_text", "")),
        "footer": [],
    }


def _build_html(
    *,
    data: dict[str, Any],
    width_mm: float,
    height_mm: float,
    top_mm: float,
    right_mm: float,
    bottom_mm: float,
    left_mm: float,
) -> str:
    payload = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    config = json.dumps(
        {
            "width": _mm_px(width_mm),
            "height": _mm_px(height_mm),
            "margins": [
                _mm_px(top_mm),
                _mm_px(right_mm),
                _mm_px(bottom_mm),
                _mm_px(left_mm),
            ],
        },
        ensure_ascii=False,
    )

    return f"""<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<style>
* {{ box-sizing:border-box; }}
html,body {{
  margin:0;
  width:100%;
  height:100%;
  background:#20252b;
  overflow:hidden;
  font-family:"Segoe UI",Arial,sans-serif;
}}
#stage {{
  position:fixed;
  inset:0;
  padding:18px;
  overflow:hidden;
}}
#pageClip {{
  width:100%;
  height:100%;
  overflow:auto;
  display:flex;
  align-items:center;
  justify-content:center;
  scrollbar-width:none;
  overscroll-behavior:contain;
}}
#pageClip::-webkit-scrollbar {{
  display:none;
}}
#pageSurface {{
  position:relative;
  flex:0 0 auto;
  overflow:hidden;
  background:#fff;
  box-shadow:0 2px 14px rgba(0,0,0,.28);
}}
#editor {{
  position:absolute;
  left:0;
  top:0;
  width:max-content;
  margin:0;
}}
#boot {{
  position:fixed;
  inset:0;
  display:flex;
  align-items:center;
  justify-content:center;
  background:#20252b;
  color:#d3d7dc;
  z-index:9999;
  font:13px "Segoe UI",Arial,sans-serif;
}}
#boot.error {{
  color:#ffd0d0;
  padding:30px;
  white-space:pre-wrap;
  text-align:center;
}}
</style>
</head>
<body>
<div id="boot">Préparation de la vraie page…</div>
<div id="stage"><div id="pageClip"><div id="pageSurface"><div id="editor"></div></div></div></div>
<script type="module">
const DATA = {payload};
const CFG = {config};
const MM = {MM_TO_PX!r};
const boot = document.getElementById("boot");
const pageClip = document.getElementById("pageClip");
const pageSurface = document.getElementById("pageSurface");
const editorRoot = document.getElementById("editor");

let editor = null;
let activePage = 0;
let requestedScale = 1;
let effectiveScale = 1;
let resizeTimer = null;

function pageCanvases() {{
  return Array.from(
    document.querySelectorAll(".ce-page-container canvas")
  );
}}

function fitScale() {{
  const availableW = Math.max(120, pageClip.clientWidth - 8);
  const availableH = Math.max(120, pageClip.clientHeight - 8);
  return Math.min(
    availableW / CFG.width,
    availableH / CFG.height,
    1
  );
}}

function positionActivePage(resetPan=false) {{
  const canvases = pageCanvases();
  if (!canvases.length) return;

  window.tlPageCount = Math.max(1, canvases.length);

  activePage = Math.max(
    0,
    Math.min(activePage, canvases.length - 1)
  );

  const target = canvases[activePage];
  const pageW = Math.max(1, target.offsetWidth);
  const pageH = Math.max(1, target.offsetHeight);

  pageSurface.style.width = pageW + "px";
  pageSurface.style.height = pageH + "px";

  // 100 % : page entière centrée.
  // 150 % : si la page dépasse la fenêtre, son HAUT reste accessible.
  // Même principe horizontal : on évite qu'un bord devienne inaccessible.
  const overflowX = pageW > pageClip.clientWidth;
  const overflowY = pageH > pageClip.clientHeight;

  pageClip.style.justifyContent = overflowX ? "flex-start" : "center";
  pageClip.style.alignItems = overflowY ? "flex-start" : "center";

  // Le document reste continu dans Canvas Editor, mais TomeLinea
  // ne montre que le canvas de la page active.
  editorRoot.style.top = (-target.offsetTop) + "px";
  editorRoot.style.left = "0px";

  if (resetPan) {{
    // À 150 %, on ouvre toujours la page depuis son haut.
    // Horizontalement, on garde le centre de la page comme point de départ.
    pageClip.scrollLeft = overflowX
      ? Math.max(0, (pageW - pageClip.clientWidth) / 2)
      : 0;
    pageClip.scrollTop = 0;
  }}
}}

function applyDisplayScale(resetPan=false) {{
  if (!editor) return;

  // Dans TomeLinea, 100 % = page entière visible.
  // 200 % = deux fois cette vue, sans afficher les pages voisines.
  const targetScale = Math.max(
    0.20,
    Math.min(4, fitScale() * requestedScale)
  );

  if (Math.abs(targetScale - effectiveScale) > 0.001) {{
    effectiveScale = targetScale;
    editor.command.executePageScale(effectiveScale);
  }}

  requestAnimationFrame(() => {{
    requestAnimationFrame(() => {{
      positionActivePage(resetPan);
    }});
  }});
}}

function showOnlyPage(pageIndex, report=false, resetPan=true) {{
  const canvases = pageCanvases();
  if (!canvases.length) return;

  const next = Math.max(
    0,
    Math.min(Number(pageIndex) || 0, canvases.length - 1)
  );
  const changed = next !== activePage;
  activePage = next;
  positionActivePage(resetPan || changed);

  if (report && changed) {{
    send({{
      type:"active_page",
      page_no:activePage
    }});
  }}
}}

function send(payload) {{
  try {{
    window.ipc.postMessage(JSON.stringify(payload));
  }} catch (_) {{}}
}}

async function start() {{
  try {{
    const mod = await import(
      "https://cdn.jsdelivr.net/npm/@hufe921/canvas-editor@1.0.2/+esm"
    );

    const Editor = mod.default || mod.Editor;
    if (!Editor) throw new Error("Export Editor introuvable.");

    editor = new Editor(
      document.getElementById("editor"),
      DATA,
      {{
        width: CFG.width,
        height: CFG.height,
        margins: CFG.margins,
        scale: 1,
        pageMode: "paging",
        pageGap: 24,
        defaultFont: "Arial",
        defaultSize: 16
      }}
    );

    window.tlEditor = editor;
    window.tlPageCount = Math.max(1, pageCanvases().length);

    async function snapshot(reason="change") {{
      try {{
        const value = editor.command.getValue();
        const text = await editor.command.getText();
        send({{
          type:"snapshot",
          reason,
          value,
          text,
          page_count:window.tlPageCount || 1
        }});
      }} catch (err) {{
        send({{type:"error", message:"Snapshot : " + String(err)}});
      }}
    }}

    let snapshotTimer = null;

    editor.listener.contentChange = () => {{
      clearTimeout(snapshotTimer);
      snapshotTimer = setTimeout(() => snapshot("change"), 180);
      requestAnimationFrame(() => positionActivePage(false));
    }};

    editor.listener.pageSizeChange = count => {{
      window.tlPageCount = Math.max(1, Number(count) || 1);
      activePage = Math.min(
        activePage,
        window.tlPageCount - 1
      );
      requestAnimationFrame(() => positionActivePage(false));
      send({{
        type:"page_count",
        page_count:window.tlPageCount
      }});
    }};

    // Quand le curseur passe réellement sur une autre page
    // (saisie au bas d'une page, clic, flèches...), la vue TomeLinea
    // suit cette page sans transformer le document en long rouleau.
    editor.eventBus.on("rangeChange", () => {{
      try {{
        const context = editor.command.getRangeContext();
        if (
          context &&
          Number.isFinite(Number(context.pageNo))
        ) {{
          showOnlyPage(Number(context.pageNo), true, true);
        }}
      }} catch (_) {{}}
    }});

    editor.eventBus.on("renderChange", () => {{
      requestAnimationFrame(() => positionActivePage(false));
    }});

    window.tlSetFormat = (
      widthMm, heightMm,
      topMm, rightMm, bottomMm, leftMm
    ) => {{
      CFG.width = Number(widthMm) * MM;
      CFG.height = Number(heightMm) * MM;
      CFG.margins = [
        Number(topMm) * MM,
        Number(rightMm) * MM,
        Number(bottomMm) * MM,
        Number(leftMm) * MM
      ];

      editor.command.executePaperSize(
        CFG.width,
        CFG.height
      );
      editor.command.executeSetPaperMargin(CFG.margins);
      requestAnimationFrame(() => applyDisplayScale(true));
    }};

    window.tlSetScale = scale => {{
      requestedScale = Math.max(
        0.25,
        Math.min(4, Number(scale) || 1)
      );
      applyDisplayScale(true);
    }};

    window.tlGoPage = pageIndex => {{
      showOnlyPage(pageIndex, true, true);
    }};

    window.tlNextPage = () => {{
      showOnlyPage(activePage + 1, true, true);
    }};

    window.tlPreviousPage = () => {{
      showOnlyPage(activePage - 1, true, true);
    }};

    window.tlSnapshot = () => snapshot("save");

    window.tlInsertImage = (
      dataUrl, widthPx, heightPx, display="surround"
    ) => {{
      editor.command.executeImage({{
        width:Number(widthPx),
        height:Number(heightPx),
        value:String(dataUrl),
        imgDisplay:String(display)
      }});
    }};

    window.addEventListener("resize", () => {{
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => {{
        applyDisplayScale(false);
      }}, 80);
    }});

    // Première vue : une seule page entière, centrée.
    applyDisplayScale(true);

    boot.style.display = "none";
    send({{type:"ready"}});
    setTimeout(() => {{
      window.tlPageCount = Math.max(
        1,
        pageCanvases().length
      );
      send({{
        type:"page_count",
        page_count:window.tlPageCount
      }});
      positionActivePage(true);
      snapshot("ready");
    }}, 180);

  }} catch (err) {{
    console.error(err);
    boot.className = "error";
    boot.textContent =
      "Canvas Editor n'a pas pu démarrer.\\n\\n" + String(err);
    send({{
      type:"error",
      message:"Canvas Editor : " + String(err)
    }});
  }}
}}

start();
</script>
</body>
</html>"""


class _SinglePageServer:
    def __init__(self, html: str) -> None:
        body = html.encode("utf-8")

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path not in ("/", "/index.html"):
                    self.send_response(404)
                    self.end_headers()
                    return
                self.send_response(200)
                self.send_header(
                    "Content-Type",
                    "text/html; charset=utf-8",
                )
                self.send_header("Cache-Control", "no-store")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, _format, *_args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.server = server
        self.url = f"http://127.0.0.1:{server.server_port}/"
        self.thread = threading.Thread(
            target=server.serve_forever,
            daemon=True,
        )
        self.thread.start()

    def close(self) -> None:
        try:
            self.server.shutdown()
        except Exception:
            pass
        try:
            self.server.server_close()
        except Exception:
            pass


class TLCanvasPageHost:
    def __init__(
        self,
        app,
        parent,
        metadata: dict[str, Any],
        fmt,
        *,
        on_snapshot: Callable[[dict[str, Any]], None] | None = None,
        on_page_count: Callable[[int], None] | None = None,
    ) -> None:
        if WebView is None:
            raise RuntimeError(
                "tkwry n'est pas disponible : "
                + str(_TKWRY_IMPORT_ERROR)
            )

        self.app = app
        self.parent = parent
        self.metadata = metadata
        self.on_snapshot = on_snapshot
        self.on_page_count = on_page_count

        self.native_ready = False
        self.ready = False
        self.failed = False
        self.page_count = max(
            1,
            int(metadata.get("canvas_page_count", 1) or 1),
        )
        self.current_page_index = max(
            0,
            int(metadata.get("canvas_active_page", 0) or 0),
        )

        self._pending_format = fmt
        self._pending_scale = 1.0
        self._pending_page = 0
        self._destroyed = False

        try:
            parent.update_idletasks()
        except Exception:
            pass

        width = max(320, int(parent.winfo_width() or 0))
        height = max(240, int(parent.winfo_height() or 0))

        self.frame = tk.Frame(
            parent,
            bg="#20252b",
            width=width,
            height=height,
            bd=0,
            highlightthickness=0,
        )
        self.frame.place(x=0, y=0, width=width, height=height)
        self.frame.update_idletasks()

        self.status = tk.Label(
            self.frame,
            text="Ouverture de la vraie page…",
            bg="#20252b",
            fg="#cfd4da",
            font=("Segoe UI", 10),
            justify="center",
        )
        self.status.place(
            relx=0.5,
            rely=0.5,
            anchor="center",
        )

        html = _build_html(
            data=_editor_data_from_metadata(metadata),
            width_mm=float(fmt.width_mm),
            height_mm=float(fmt.height_mm),
            top_mm=float(fmt.margin_top_mm),
            right_mm=float(fmt.margin_outside_mm),
            bottom_mm=float(fmt.margin_bottom_mm),
            left_mm=float(fmt.margin_inside_mm),
        )
        self._server = _SinglePageServer(html)

        # IMPORTANT :
        # tkwry ne lève pas forcément d'exception si WebView2 échoue.
        # On attache donc explicitement les deux signaux.
        try:
            self.web = WebView(
                self.frame,
                url=self._server.url,
                on_ipc=self._on_ipc,
                devtools=False,
                focused=False,
            )
        except Exception as exc:
            self.failed = True
            self._set_status(
                "WebView2 n'a pas pu démarrer.\n\n" + str(exc),
                error=True,
            )
            try:
                self._server.close()
            except Exception:
                pass
            raise

        try:
            self.web.when_ready(
                lambda *_args: self._on_native_ready()
            )
        except Exception:
            pass

        try:
            self.web.when_failed(
                lambda *args: self._on_native_failed(
                    args[-1] if args else "échec WebView2"
                )
            )
        except Exception:
            pass

        self.parent.bind(
            "<Configure>",
            self._sync_bounds,
            add="+",
        )

        # Plus jamais de zone vide silencieuse.
        try:
            self.app.after(
                12000,
                self._check_start_timeout,
            )
        except Exception:
            pass

    def _safe_after(self, callback) -> None:
        try:
            if not self._destroyed:
                self.app.after(0, callback)
        except Exception:
            pass

    def _set_status(self, text: str, *, error: bool = False) -> None:
        if self._destroyed:
            return
        try:
            self.status.configure(
                text=text,
                fg="#ffd1d1" if error else "#cfd4da",
            )
            self.status.place(
                relx=0.5,
                rely=0.5,
                anchor="center",
            )
            self.status.lift()
        except Exception:
            pass

    def _on_native_ready(self) -> None:
        self.native_ready = True
        try:
            self.status.place_forget()
        except Exception:
            pass
        try:
            self.web.sync_bounds()
        except Exception:
            pass

    def _on_native_failed(self, exc) -> None:
        message = str(exc)
        self.failed = True
        self.native_ready = False
        self.ready = False

        try:
            self.web.destroy()
        except Exception:
            pass

        self._set_status(
            "WebView2 n'a pas pu être créé.\n\n" + message,
            error=True,
        )
        print("TomeLinea Canvas / WebView2 :", message)

    def _check_start_timeout(self) -> None:
        if self._destroyed or self.ready or self.failed:
            return

        phase = ""
        error = ""
        try:
            phase = str(getattr(self.web, "phase", "") or "")
            error = str(
                getattr(self.web, "creation_error", "") or ""
            )
        except Exception:
            pass

        try:
            self.web.destroy()
        except Exception:
            pass

        details = error or phase or "aucun signal de démarrage"
        self.failed = True
        self._set_status(
            "La page WebView2 existe mais Canvas Editor "
            "n'a pas démarré.\n\n"
            + details,
            error=True,
        )
        print(
            "TomeLinea Canvas : démarrage expiré -",
            details,
        )

    def _sync_bounds(self, _event=None) -> None:
        if self._destroyed:
            return

        try:
            width = max(2, int(self.parent.winfo_width()))
            height = max(2, int(self.parent.winfo_height()))
            self.frame.place(
                x=0,
                y=0,
                width=width,
                height=height,
            )
            self.frame.update_idletasks()
        except Exception:
            pass

        try:
            self.web.sync_bounds()
        except Exception:
            pass

    def _on_ipc(self, raw: str) -> None:
        try:
            msg = json.loads(raw)
        except Exception:
            return

        kind = str(msg.get("type", ""))

        if kind == "ready":
            self.ready = True
            self.failed = False
            try:
                self.status.place_forget()
            except Exception:
                pass
            self._flush_pending()
            try:
                self.web.focus()
            except Exception:
                pass
            return

        if kind == "snapshot":
            value = msg.get("value")
            text = msg.get("text")
            count = max(
                1,
                int(msg.get("page_count", self.page_count) or 1),
            )

            if isinstance(value, dict):
                self.metadata["canvas_editor_value"] = value

            if isinstance(text, dict):
                main = text.get("main")
                if isinstance(main, str):
                    self.metadata["plain_text"] = main
            elif isinstance(text, str):
                self.metadata["plain_text"] = text

            self.page_count = count
            self.metadata["canvas_page_count"] = count

            if self.on_snapshot is not None:
                self.on_snapshot(msg)
            return

        if kind == "page_count":
            count = max(
                1,
                int(msg.get("page_count", 1) or 1),
            )
            self.page_count = count
            self.metadata["canvas_page_count"] = count

            if self.on_page_count is not None:
                self.on_page_count(count)
            return

        if kind == "active_page":
            page_no = max(
                0,
                int(msg.get("page_no", 0) or 0),
            )
            self.current_page_index = page_no
            self.metadata["canvas_active_page"] = page_no

            # IMPORTANT :
            # Canvas Editor ne commande plus la navigation TomeLinea.
            # Structure / Aller / Précédente / Suivante restent l'autorité.
            # Cela évite que le curseur resté sur l'ancienne page renvoie
            # immédiatement TomeLinea vers la page 1 après un clic Structure.
            return

        if kind == "error":
            message = str(msg.get("message", ""))
            self.metadata["canvas_editor_error"] = message
            print("TomeLinea Canvas Editor :", message)

    def _eval(self, script: str) -> None:
        if self._destroyed or not self.ready:
            return
        try:
            self.web.eval_js(
                script,
                on_error=lambda exc: print(
                    "TomeLinea Canvas JS :", exc
                ),
            )
        except TypeError:
            # Compatibilité avec versions de tkwry plus anciennes.
            try:
                self.web.eval_js(script)
            except Exception as exc:
                print("TomeLinea Canvas JS :", exc)
        except Exception as exc:
            print("TomeLinea Canvas JS :", exc)

    def _flush_pending(self) -> None:
        if not self.ready:
            return
        self.set_format(self._pending_format)
        self.set_scale(self._pending_scale)
        self.show_page(self._pending_page)

    def show(self) -> None:
        if self._destroyed:
            return
        self._sync_bounds()
        try:
            self.frame.lift()
        except Exception:
            pass
        if self.ready:
            try:
                self.web.focus()
            except Exception:
                pass

    def hide(self) -> None:
        if self._destroyed:
            return
        try:
            self.frame.place_forget()
        except Exception:
            pass

    def destroy(self) -> None:
        if self._destroyed:
            return
        self._destroyed = True

        try:
            self.web.destroy()
        except Exception:
            pass
        try:
            self._server.close()
        except Exception:
            pass
        try:
            self.frame.destroy()
        except Exception:
            pass

    def set_format(self, fmt) -> None:
        self._pending_format = fmt
        if not self.ready:
            return

        values = (
            fmt.width_mm,
            fmt.height_mm,
            fmt.margin_top_mm,
            fmt.margin_outside_mm,
            fmt.margin_bottom_mm,
            fmt.margin_inside_mm,
        )
        self._eval(
            "window.tlSetFormat && window.tlSetFormat("
            + ",".join(json.dumps(float(v)) for v in values)
            + ");"
        )

    def set_scale(self, scale: float) -> None:
        self._pending_scale = float(scale)
        if not self.ready:
            return
        self._eval(
            "window.tlSetScale && window.tlSetScale("
            + json.dumps(float(scale))
            + ");"
        )

    def show_page(self, page_index: int) -> None:
        self._pending_page = max(0, int(page_index))
        self.current_page_index = self._pending_page
        if not self.ready:
            return
        self._eval(
            "window.tlGoPage && window.tlGoPage("
            + str(self._pending_page)
            + ");"
        )

    def next_page(self) -> None:
        if not self.ready:
            return
        self._eval("window.tlNextPage && window.tlNextPage();")

    def previous_page(self) -> None:
        if not self.ready:
            return
        self._eval("window.tlPreviousPage && window.tlPreviousPage();")

    def request_snapshot(self) -> None:
        self._eval(
            "window.tlSnapshot && window.tlSnapshot();"
        )

    def insert_image(
        self,
        *,
        data_url: str,
        width_px: float,
        height_px: float,
        display: str = "surround",
    ) -> None:
        self._eval(
            "window.tlInsertImage && window.tlInsertImage("
            + ",".join(
                (
                    json.dumps(str(data_url)),
                    json.dumps(float(width_px)),
                    json.dumps(float(height_px)),
                    json.dumps(str(display)),
                )
            )
            + ");"
        )
