from __future__ import annotations

"""TomeLinea — prototype isolé « un Canvas par chapitre ».

Aucun fichier de production n'est modifié. Les éditions faites dans ce prototype
ne sont pas enregistrées dans la Source : ce lanceur sert uniquement à mesurer
la réactivité et la viabilité de l'architecture.
"""

from pathlib import Path
import queue
import sys
import threading
import tkinter as tk
from tkinter import ttk

from src.v4.canvas_loading import CanvasLoadSession, prepare_canvas_load
from src.v4.canvas_editor_payload import build_canvas_editor_payload
from src.v4.canvas_editor_document import build_canvas_editor_document
from src.gui_v4.canvas_editor_host import CanvasEditorWebHost
from src.v4.canvas_chapter_slice import detect_chapters, slice_payload


def desktop_test_dir() -> Path:
    home = Path.home()
    candidates = [home / "Desktop", home / "Bureau"]
    desktop = next((path for path in candidates if path.exists()), candidates[0])
    target = desktop / "test tomelinea"
    target.mkdir(parents=True, exist_ok=True)
    return target


def main() -> int:
    root_dir = Path(__file__).resolve().parent
    source = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else desktop_test_dir() / "TEST_REEL.docx"

    app = tk.Tk()
    app.title("TomeLinea — Prototype Canvas par chapitre")
    app.geometry("1180x820")
    app.minsize(900, 650)
    app.configure(bg="#252A30")

    top = tk.Frame(app, bg="#1F2429", height=52)
    top.pack(side="top", fill="x")
    top.pack_propagate(False)

    title = tk.Label(top, text="Test isolé — un Canvas par chapitre", bg="#1F2429", fg="#E7EAED", font=("Segoe UI", 12, "bold"))
    title.pack(side="left", padx=(16, 10))

    status = tk.Label(top, text="Analyse…", bg="#1F2429", fg="#AEB7BE", font=("Segoe UI", 10))
    status.pack(side="right", padx=16)

    selector_var = tk.StringVar()
    selector = ttk.Combobox(top, textvariable=selector_var, state="readonly", width=48)
    selector.pack(side="left", padx=12, pady=10)

    holder = tk.Frame(app, bg="#252A30")
    holder.pack(fill="both", expand=True)

    q: queue.Queue = queue.Queue()
    state = {"prepared": None, "translated": None, "detection": None, "host": None}

    def destroy_host() -> None:
        host = state.get("host")
        if host is not None:
            try:
                host.destroy()
            except Exception:
                pass
            state["host"] = None

    def load_chapter(index: int) -> None:
        translated = state["translated"]
        detection = state["detection"]
        if translated is None or detection is None:
            return
        chapters = detection.chapters
        if not (0 <= index < len(chapters)):
            return
        chapter = chapters[index]
        destroy_host()
        status.config(text=f"Chargement : {chapter.title}")

        chapter_payload = slice_payload(translated.payload, chapter)
        document = build_canvas_editor_document(chapter_payload)
        if not document.valid:
            status.config(text="Plan chapitre invalide")
            return
        # Le prototype est autonome : pas de panneau éditorial ni de persistance.
        document.plan["tomelinea_ui"] = {"mode": "standalone"}

        # Le verrou Canvas ne contient pas le document rendu ; il ne fait que
        # suivre l'ordre des étapes de chargement. Une session neuve suffit donc
        # pour chaque chapitre, sans relancer l'analyse complète du DOCX.
        prepared = state["prepared"]
        chapter_session = CanvasLoadSession(prepared.canvas.contract)

        def on_ready(snapshot: dict) -> None:
            count = snapshot.get("page_count") or snapshot.get("pageCount") or "?"
            status.config(text=f"{chapter.title} — {count} page(s) — TESTEZ LA FRAPPE")

        def on_failed(failure: dict) -> None:
            status.config(text=f"Erreur Canvas : {failure.get('stage', '?')}")

        host = CanvasEditorWebHost(holder, project_root=root_dir, on_ready=on_ready, on_failed=on_failed)
        state["host"] = host
        host.pack(fill="both", expand=True)
        host.load_document(document.plan, chapter_session)

    def on_select(_event=None) -> None:
        detection = state.get("detection")
        if not detection:
            return
        try:
            idx = selector.current()
        except Exception:
            idx = -1
        if idx >= 0:
            load_chapter(idx)

    selector.bind("<<ComboboxSelected>>", on_select)

    def worker() -> None:
        try:
            prepared = prepare_canvas_load(source, project_root=root_dir)
            translated = build_canvas_editor_payload(prepared.canvas.contract)
            detection = detect_chapters(translated.payload)
            q.put(("ready", prepared, translated, detection))
        except Exception as exc:
            q.put(("error", exc))

    def poll() -> None:
        try:
            kind, *payload = q.get_nowait()
        except queue.Empty:
            app.after(60, poll)
            return
        if kind == "error":
            status.config(text=f"Erreur : {type(payload[0]).__name__}")
            return
        prepared, translated, detection = payload
        state["prepared"] = prepared
        state["translated"] = translated
        state["detection"] = detection
        if not detection.chapters:
            status.config(text="Aucun contenu détecté")
            return
        labels = [f"{c.index:02d} — {c.title}" for c in detection.chapters]
        selector["values"] = labels
        selector.current(1 if len(labels) > 1 and detection.chapters[0].detected_by == "prelude" else 0)
        status.config(text=f"{len(labels)} bloc(s) — détection : {detection.mode}")
        app.after(50, lambda: load_chapter(selector.current()))

    threading.Thread(target=worker, daemon=True).start()
    app.after(60, poll)
    app.protocol("WM_DELETE_WINDOW", lambda: (destroy_host(), app.destroy()))
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
