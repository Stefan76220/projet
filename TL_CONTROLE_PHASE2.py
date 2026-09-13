from __future__ import annotations

from pathlib import Path
import json
import queue
import shutil
import sys
import threading
import tkinter as tk
from tkinter import filedialog

from src.v4.canvas_loading import prepare_canvas_load
from src.v4.canvas_editor_payload import build_canvas_editor_payload
from src.v4.canvas_editor_document import build_canvas_editor_document
from src.gui_v4.canvas_editor_host import CanvasEditorWebHost
from src.v4.editorial_review import build_editorial_review
from src.v4.source_phase2 import Phase2BlockedError, clear_font_inventory_cache, list_available_font_faces
from src.v4.blocking_review import build_blocking_user_view
from src.v4.editorial_persistence import (
    load_editorial_state,
    persisted_choices_for_plan,
    record_editorial_choice,
)

PHASE = "2.35"

WAITING_MESSAGES = (
    "Lecture de la source…",
    "Analyse de la structure…",
    "Vérification des polices et ressources…",
    "Préparation de la composition…",
)


def desktop_test_dir() -> Path:
    home = Path.home()
    candidates = [home / "Desktop", home / "Bureau"]
    desktop = next((path for path in candidates if path.exists()), candidates[0])
    target = desktop / "test tomelinea"
    target.mkdir(parents=True, exist_ok=True)
    return target


def main() -> int:
    root_dir = Path(__file__).resolve().parent
    test_dir = desktop_test_dir()
    source = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else test_dir / "TEST_REEL.docx"
    output = test_dir / "A_M_ENVOYER.json"
    editorial_state_file = test_dir / "ETAT_COMPOSITION_TEST.json"

    report: dict = {
        "phase": PHASE,
        "source": str(source),
        "real_webview_created": False,
        "actual_render_performed": False,
        "render_complete_received": False,
        "page_count": None,
        "composition_visible": False,
        "errors": [],
        "preparation_flow": {"state": "waiting", "events": []},
        "visual_fixes": [
            "page_number_native_canvas",
            "page_break_label_french",
            "page_break_native_wrap_value",
            "table_first_row_orphan_auto_fix",
            "table_other_splits_editorial_decision",
            "editorial_review_three_levels",
            "real_book_end_to_end_control",
            "floating_square_wrap_native_canvas",
            "word_justify_to_canvas_alignment",
            "french_words_never_split_on_accents_or_apostrophes",
            "text_obvious_errors_auto_corrected",
            "text_particularities_editorial_decisions",
            "blocking_anomaly_with_proposed_solution",
            "visual_review_panel_before_after",
            "visual_review_canvas_search_highlight",
            "visual_review_navigate_to_first_match",
            "visual_review_whitespace_tolerant_search",
            "visual_review_changed_char_visible",
            "automatic_corrections_hidden_from_workflow",
            "automatic_correction_journal_on_demand",
            "editorial_decisions_only_in_control",
            "visual_review_vertically_centered",
            "visual_review_french_only",
            "internal_kind_codes_hidden_from_user",
            "grammar_sentence_initial_capital_auto_corrected",
            "existing_mid_sentence_capitals_preserved",
            "editorial_only_when_interpretation_required",
            "runtime_table_decisions_visible_in_control",
            "runtime_editorial_decision_test_fixture",
            "editorial_decision_buttons_actionable",
            "table_move_choice_reflows_canvas",
            "editorial_choice_recorded_in_report",
            "editorial_table_move_uses_stable_runtime_data",
            "editorial_choice_remains_visible_and_reversible",
            "blocking_case_visible_before_composition",
            "blocking_problem_and_solution_in_right_panel",
            "blocking_never_substitutes_silently",
            "single_preparation_window_for_analysis_and_blocking",
            "waiting_state_visible_during_analysis",
            "blocking_state_transforms_same_window",
            "blocking_retry_returns_to_waiting_state",
            "blocking_flow_generic_for_all_blockers",
            "missing_font_can_be_added_from_blocking_state",
            "missing_font_can_be_replaced_explicitly",
            "font_substitution_reanalyzes_before_composition",
            "font_substitution_never_silent",
            "canvas_boot_waits_for_real_page_after_reanalysis",
            "editorial_similar_cases_grouped_only_when_safe",
            "editorial_bulk_choice_applies_to_safe_similar_cases",
            "editorial_bulk_choice_keeps_individual_exceptions",
            "editorial_choices_persist_between_reopenings",
            "editorial_persistence_uses_stable_target_ids",
            "editorial_persistence_never_modifies_source",
        ],
        "editorial_persistence": {
            "state_file": str(editorial_state_file),
            "loaded_count": 0,
            "saved_count": 0,
            "source_scoped": True,
        },
    }

    def write_report() -> None:
        output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    def flow_event(state: str, **details) -> None:
        report["preparation_flow"]["state"] = state
        report["preparation_flow"].setdefault("events", []).append({"state": state, **details})
        write_report()

    app = tk.Tk()
    app.title("TomeLinea — Phase 2.35")
    app.geometry("1180x820")
    app.minsize(900, 650)
    app.configure(bg="#252A30")

    host_holder = tk.Frame(app, bg="#252A30", bd=0, highlightthickness=0)
    host_holder.pack(fill="both", expand=True)

    overlay = tk.Frame(app, bg="#20252A", bd=0, highlightthickness=0)
    overlay.place(x=0, y=0, relwidth=1, relheight=1)

    left = tk.Frame(overlay, bg="#20252A", bd=0, highlightthickness=0)
    left.pack(side="left", fill="both", expand=True)

    wait_title = tk.Label(
        left,
        text="TOMELINEA",
        bg="#20252A",
        fg="#E8EBEE",
        font=("Segoe UI", 21, "bold"),
    )
    wait_title.place(relx=0.5, rely=0.42, anchor="center")

    wait_status = tk.Label(
        left,
        text=WAITING_MESSAGES[0],
        bg="#20252A",
        fg="#B8C0C7",
        font=("Segoe UI", 11),
        justify="center",
        wraplength=560,
    )
    wait_status.place(relx=0.5, rely=0.51, anchor="center")

    line = tk.Canvas(left, width=330, height=20, bg="#20252A", highlightthickness=0, bd=0)
    line.place(relx=0.5, rely=0.58, anchor="center")
    line.create_line(15, 10, 315, 10, fill="#59636C", width=2)
    glow_outer = line.create_oval(10, 5, 20, 15, fill="#9CA7AF", outline="")
    glow_inner = line.create_oval(13, 8, 17, 12, fill="#F0E6C8", outline="")

    right = tk.Frame(overlay, bg="#2D333A", width=390, bd=0, highlightthickness=0)
    right.pack_propagate(False)

    result_queue: queue.Queue = queue.Queue()
    host_ref: dict[str, CanvasEditorWebHost] = {}
    finished = {"value": False}
    analysis_running = {"value": False}
    generation = {"value": 0}
    waiting_index = {"value": 0}
    animation_x = {"value": 15}
    blocker_index = {"value": 0}
    blocker_views: list[dict] = []
    blocker_raw: list[dict] = []
    font_substitutions: dict[str, dict[str, str]] = {}

    def animate_waiting() -> None:
        if report["preparation_flow"].get("state") not in {"waiting", "rendering"}:
            app.after(80, animate_waiting)
            return
        x = animation_x["value"] + 5
        if x > 315:
            x = 15
        animation_x["value"] = x
        line.coords(glow_outer, x - 5, 5, x + 5, 15)
        line.coords(glow_inner, x - 2, 8, x + 2, 12)
        app.after(30, animate_waiting)

    def rotate_waiting_text() -> None:
        if report["preparation_flow"].get("state") == "waiting":
            waiting_index["value"] = (waiting_index["value"] + 1) % len(WAITING_MESSAGES)
            wait_status.config(text=WAITING_MESSAGES[waiting_index["value"]])
        app.after(900, rotate_waiting_text)

    def show_waiting(*, rendering: bool = False) -> None:
        overlay.place(x=0, y=0, relwidth=1, relheight=1)
        right.pack_forget()
        wait_title.config(text="TOMELINEA", font=("Segoe UI", 21, "bold"))
        wait_status.config(
            text="Mise en page, pagination et vérification du livre…" if rendering else WAITING_MESSAGES[0],
            fg="#B8C0C7",
            font=("Segoe UI", 11),
        )
        line.place(relx=0.5, rely=0.58, anchor="center")
        waiting_index["value"] = 0
        flow_event("rendering" if rendering else "waiting")

    def clear_right() -> None:
        for child in right.winfo_children():
            child.destroy()

    def add_section(parent: tk.Misc, label: str, value: str) -> None:
        tk.Label(
            parent, text=label, bg="#2D333A", fg="#99A3AB",
            font=("Segoe UI", 9, "bold"), anchor="w", pady=5,
        ).pack(fill="x")
        tk.Label(
            parent, text=value, bg="#2D333A", fg="#E5E8EA",
            font=("Segoe UI", 10), wraplength=330, justify="left", anchor="w",
        ).pack(fill="x", pady=(0, 8))

    def current_blocker_view() -> dict:
        if not blocker_views:
            return {}
        blocker_index["value"] = max(0, min(blocker_index["value"], len(blocker_views) - 1))
        return blocker_views[blocker_index["value"]]

    def install_font_and_retry() -> None:
        path = filedialog.askopenfilename(
            parent=app,
            title="Ajouter une police à TomeLinea",
            filetypes=[
                ("Polices", "*.ttf *.otf *.ttc *.otc"),
                ("Tous les fichiers", "*.*"),
            ],
        )
        if not path:
            return
        src = Path(path)
        if src.suffix.lower() not in {".ttf", ".otf", ".ttc", ".otc"}:
            wait_status.config(text="Ce fichier n’est pas une police prise en charge.")
            return
        target_dir = root_dir / "resources" / "fonts" / "user"
        target_dir.mkdir(parents=True, exist_ok=True)
        target = target_dir / src.name
        try:
            shutil.copy2(src, target)
            clear_font_inventory_cache()
            report.setdefault("blocking_actions", []).append({
                "action": "add_font",
                "source": str(src),
                "installed_to": str(target),
            })
            write_report()
        except Exception as exc:
            report.setdefault("blocking_actions", []).append({
                "action": "add_font",
                "failed": True,
                "message": f"{type(exc).__name__}: {exc}",
            })
            write_report()
            wait_status.config(text=f"Impossible d’ajouter cette police : {exc}")
            return
        start_analysis(reason="font_added")


    def _font_key(family: str, style: str) -> str:
        clean = "".join(ch.lower() for ch in str(family or "") if ch.isalnum())
        style_clean = str(style or "regular").strip().lower() or "regular"
        return f"{clean}::{style_clean}"

    def choose_font_substitute_and_retry() -> None:
        view = current_blocker_view()
        raw = view.get("raw", {}) if isinstance(view, dict) else {}
        details = raw.get("details", {}) if isinstance(raw, dict) else {}
        fonts = details.get("fonts", []) if isinstance(details, dict) else []
        missing = next((item for item in fonts if isinstance(item, dict)), None)
        if not missing:
            wait_status.config(text="Aucune police manquante n’a été identifiée.")
            return

        source_family = str(missing.get("family") or "").strip()
        source_style = str(missing.get("style") or "regular").strip().lower() or "regular"
        available = [
            item for item in list_available_font_faces(root_dir)
            if item.get("style") == source_style
        ]
        if not available:
            wait_status.config(text="Aucune police de remplacement compatible n’est disponible.")
            return

        # Une seule entrée par famille pour éviter une liste inutilement longue.
        unique: list[dict[str, str]] = []
        seen: set[str] = set()
        for item in available:
            family = str(item.get("family") or "").strip()
            marker = family.casefold()
            if not family or marker in seen:
                continue
            seen.add(marker)
            unique.append(item)

        dialog = tk.Toplevel(app)
        dialog.title("Choisir une police de remplacement")
        dialog.transient(app)
        dialog.grab_set()
        dialog.configure(bg="#2D333A")
        dialog.geometry("520x520")
        dialog.minsize(430, 420)

        tk.Label(
            dialog,
            text=f"Remplacer : {source_family} ({source_style})",
            bg="#2D333A", fg="#F2F4F5", font=("Segoe UI", 12, "bold"),
            anchor="w", padx=18, pady=14,
        ).pack(fill="x")
        tk.Label(
            dialog,
            text="Ce choix modifie uniquement la version de travail. La Source reste intacte.",
            bg="#2D333A", fg="#AEB6BD", font=("Segoe UI", 9),
            anchor="w", justify="left", wraplength=470, padx=18, pady=4,
        ).pack(fill="x")

        frame = tk.Frame(dialog, bg="#2D333A", padx=18, pady=10)
        frame.pack(fill="both", expand=True)
        scrollbar = tk.Scrollbar(frame, orient="vertical")
        listbox = tk.Listbox(
            frame, yscrollcommand=scrollbar.set, exportselection=False,
            bg="#20252A", fg="#E8EBEE", selectbackground="#59636C",
            selectforeground="#FFFFFF", relief="flat", bd=0,
            font=("Segoe UI", 10), activestyle="none",
        )
        scrollbar.config(command=listbox.yview)
        scrollbar.pack(side="right", fill="y")
        listbox.pack(side="left", fill="both", expand=True)
        for item in unique:
            origin = str(item.get("origin") or "")
            suffix = " — Windows" if origin == "system" else " — TomeLinea"
            listbox.insert("end", f"{item['family']}{suffix}")

        # Arial est un bon choix de départ sur Windows si elle existe, sinon première entrée.
        initial = 0
        for idx, item in enumerate(unique):
            if str(item.get("family") or "").casefold() == "arial":
                initial = idx
                break
        if unique:
            listbox.selection_set(initial)
            listbox.see(initial)

        buttons = tk.Frame(dialog, bg="#2D333A", padx=18, pady=14)
        buttons.pack(fill="x")

        def apply_choice() -> None:
            selected = listbox.curselection()
            if not selected:
                return
            target = unique[int(selected[0])]
            key = _font_key(source_family, source_style)
            font_substitutions[key] = {
                "family": str(target.get("family") or ""),
                "style": str(target.get("style") or source_style),
            }
            report["font_substitutions"] = {k: dict(v) for k, v in font_substitutions.items()}
            report.setdefault("blocking_actions", []).append({
                "action": "choose_font_substitute",
                "source_family": source_family,
                "source_style": source_style,
                "replacement_family": font_substitutions[key]["family"],
                "replacement_style": font_substitutions[key]["style"],
                "explicit_user_choice": True,
            })
            write_report()
            dialog.destroy()
            start_analysis(reason="font_substitution_selected")

        tk.Button(
            buttons, text="Annuler", command=dialog.destroy,
            bg="#343B42", fg="#DDE1E4", relief="flat", bd=0, padx=14, pady=8,
        ).pack(side="right", padx=(8, 0))
        tk.Button(
            buttons, text="Utiliser cette police", command=apply_choice,
            bg="#46515A", fg="#FFFFFF", relief="flat", bd=0, padx=14, pady=8,
        ).pack(side="right")

        dialog.wait_window()

    def render_blocker() -> None:
        view = current_blocker_view()
        if not view:
            return
        clear_right()
        right.pack(side="right", fill="y")
        wait_title.config(text="Composition suspendue", font=("Segoe UI", 19, "bold"))
        wait_status.config(
            text="TomeLinea n’ouvre pas une composition qu’il ne peut pas garantir.",
            fg="#AEB6BD",
        )
        line.place_forget()

        inner = tk.Frame(right, bg="#2D333A", padx=24, pady=28)
        inner.pack(fill="both", expand=True)

        header = "ANOMALIE BLOQUANTE"
        if len(blocker_views) > 1:
            header += f"  {blocker_index['value'] + 1}/{len(blocker_views)}"
        tk.Label(
            inner, text=header, bg="#2D333A", fg="#F0C674",
            font=("Segoe UI", 10, "bold"), anchor="w",
        ).pack(fill="x")
        tk.Label(
            inner, text=view.get("title", "TomeLinea a besoin de votre intervention"),
            bg="#2D333A", fg="#F2F4F5", font=("Segoe UI", 15, "bold"),
            wraplength=330, justify="left", anchor="w", pady=10,
        ).pack(fill="x")

        add_section(inner, "CE QUI BLOQUE", view.get("problem", ""))
        add_section(inner, "PROBLÈME ICI", view.get("detail", ""))
        add_section(inner, "POURQUOI TOMELINEA S’ARRÊTE", view.get("why", ""))
        add_section(inner, "SOLUTION PROPOSÉE", view.get("solution", ""))

        tk.Label(
            inner,
            text="Le document source reste intact. Aucune substitution n’est faite automatiquement.",
            bg="#2D333A", fg="#AEB6BD", font=("Segoe UI", 9),
            wraplength=330, justify="left", anchor="w", pady=8,
        ).pack(fill="x")

        actions = tk.Frame(inner, bg="#2D333A")
        actions.pack(side="bottom", fill="x", pady=(18, 0))

        for spec in view.get("actions", []):
            action_id = spec.get("id")
            if action_id == "add_font":
                command = install_font_and_retry
            elif action_id == "choose_font_substitute":
                command = choose_font_substitute_and_retry
            elif action_id == "retry":
                command = lambda: start_analysis(reason="user_retry")
            else:
                continue
            tk.Button(
                actions, text=spec.get("label", action_id), command=command,
                bg="#394149", fg="#F2F4F5", activebackground="#444D56",
                activeforeground="#FFFFFF", relief="flat", bd=0,
                padx=14, pady=9, cursor="hand2",
            ).pack(fill="x", pady=(0, 7))

        if len(blocker_views) > 1:
            nav = tk.Frame(actions, bg="#2D333A")
            nav.pack(fill="x", pady=(4, 0))

            def previous() -> None:
                blocker_index["value"] = (blocker_index["value"] - 1) % len(blocker_views)
                render_blocker()

            def following() -> None:
                blocker_index["value"] = (blocker_index["value"] + 1) % len(blocker_views)
                render_blocker()

            tk.Button(nav, text="Précédent", command=previous, bg="#343B42", fg="#DDE1E4", relief="flat").pack(side="left", fill="x", expand=True, padx=(0, 4))
            tk.Button(nav, text="Suivant", command=following, bg="#343B42", fg="#DDE1E4", relief="flat").pack(side="left", fill="x", expand=True, padx=(4, 0))

    def show_blocked(blocking: list[dict], *, stage: str = "analysis") -> None:
        nonlocal blocker_views, blocker_raw
        blocker_raw = list(blocking)
        user_view = build_blocking_user_view(blocking)
        blocker_views = list(user_view.get("views", []))
        blocker_index["value"] = 0
        report["editorial_review"] = build_editorial_review({}, blocking_anomalies=blocking)
        report["blocking_user_view"] = user_view
        report["errors"] = blocking
        report["composition_visible"] = False
        flow_event("blocked", stage=stage, count=len(blocking))
        render_blocker()

    def refresh_host_snapshot() -> None:
        host = host_ref.get("host")
        if host is None:
            return
        snap = host.snapshot()
        report["host"] = snap
        text_review = report.get("text_quality", {})
        report["editorial_review"] = build_editorial_review(snap, text_review=text_review)
        report["real_webview_created"] = bool(snap.get("page_loaded") or snap.get("ready"))
        report["page_count"] = snap.get("page_count")

    def destroy_host() -> None:
        host = host_ref.pop("host", None)
        if host is None:
            return
        try:
            host.shutdown()
        except Exception:
            pass
        try:
            host.destroy()
        except Exception:
            pass

    def on_ready(session_snapshot: dict) -> None:
        refresh_host_snapshot()
        report.update({
            "real_webview_created": True,
            "actual_render_performed": True,
            "render_complete_received": True,
            "page_count": session_snapshot.get("page_count"),
            "composition_visible": bool(session_snapshot.get("composition_visible")),
            "session": session_snapshot,
            "errors": [],
        })
        flow_event("composition")
        overlay.place_forget()
        app.title("TomeLinea — Phase 2.35 — Composition")
        host = host_ref.get("host")
        if host is not None:
            try:
                if host._web is not None:
                    host._web.sync_bounds()
                    host._web.focus()
            except Exception:
                pass

    def on_canvas_failed(failure: dict) -> None:
        refresh_host_snapshot()
        blocking = [{
            "domain": "composition",
            "kind": "canvas_render_failure",
            "severity": "blocking",
            "message": "La mise en page n’a pas pu être terminée.",
            "details": {"failure": failure},
            "proposed_solution": "Relancer l’analyse. Si le problème persiste, conserver le rapport de diagnostic avant toute modification du document.",
        }]
        show_blocked(blocking, stage="canvas")

    def persist_editorial_choice(event: dict) -> None:
        state = record_editorial_choice(editorial_state_file, source, event)
        report["editorial_persistence"]["saved_count"] = len(state.get("decisions", {}))
        report["editorial_persistence"]["last_saved_choice"] = dict(event)
        write_report()

    def start_canvas(prepared, document) -> None:
        destroy_host()
        show_waiting(rendering=True)
        host = CanvasEditorWebHost(
            host_holder,
            project_root=root_dir,
            on_ready=on_ready,
            on_failed=on_canvas_failed,
            on_editorial_choice=persist_editorial_choice,
        )
        host_ref["host"] = host
        host.pack(fill="both", expand=True)
        try:
            host.load_document(document.plan, prepared.session)
        except Exception as exc:
            on_canvas_failed({"stage": "load_document", "message": f"{type(exc).__name__}: {exc}"})
            return

        current_generation = generation["value"]

        def timeout_check() -> None:
            if generation["value"] != current_generation:
                return
            if report.get("composition_visible"):
                return
            if report["preparation_flow"].get("state") == "rendering":
                on_canvas_failed({"stage": "timeout", "message": "render_complete non reçu après 45 secondes"})

        app.after(45_000, timeout_check)

    def analysis_worker(my_generation: int) -> None:
        try:
            prepared = prepare_canvas_load(
                source,
                project_root=root_dir,
                font_substitutions={k: dict(v) for k, v in font_substitutions.items()},
            )
            translated = build_canvas_editor_payload(prepared.canvas.contract)
            document = build_canvas_editor_document(translated.payload)
            persisted_state = load_editorial_state(editorial_state_file, source)
            persisted_choices = persisted_choices_for_plan(persisted_state)
            document.plan["persisted_editorial_choices"] = persisted_choices
            report["editorial_persistence"]["loaded_count"] = len(persisted_choices)
            report["editorial_persistence"]["loaded_choices"] = persisted_choices
            if not prepared.ready or not translated.valid or not document.valid:
                raise RuntimeError("Préparation Canvas invalide avant rendu réel.")
            text_review = {
                "automatic_corrections": list(prepared.text_quality.automatic_corrections),
                "editorial_decisions": list(prepared.text_quality.editorial_decisions),
                "blocking_anomalies": list(prepared.text_quality.blocking_anomalies),
            }
            document.plan["visual_review"] = text_review
            result_queue.put((my_generation, "ready", prepared, translated, document, text_review))
        except Phase2BlockedError as exc:
            blocking = [
                {
                    "domain": "composition",
                    "kind": item.code,
                    "severity": "blocking",
                    "message": item.message,
                    "details": item.details,
                    "proposed_solution": item.solution,
                }
                for item in exc.blockers
            ]
            result_queue.put((my_generation, "blocked", blocking))
        except Exception as exc:
            result_queue.put((my_generation, "error", {"stage": "preparation", "message": f"{type(exc).__name__}: {exc}"}))

    def start_analysis(*, reason: str = "initial") -> None:
        if analysis_running["value"]:
            return
        destroy_host()
        finished["value"] = False
        report["composition_visible"] = False
        report["render_complete_received"] = False
        report["errors"] = []
        report.setdefault("analysis_attempts", []).append({"reason": reason})
        generation["value"] += 1
        my_generation = generation["value"]
        analysis_running["value"] = True
        show_waiting(rendering=False)
        thread = threading.Thread(target=analysis_worker, args=(my_generation,), daemon=True)
        thread.start()

    def poll_results() -> None:
        try:
            while True:
                item = result_queue.get_nowait()
                my_generation, kind, *payload = item
                if my_generation != generation["value"]:
                    continue
                analysis_running["value"] = False
                if kind == "blocked":
                    show_blocked(payload[0], stage="analysis")
                elif kind == "error":
                    failure = payload[0]
                    show_blocked([{
                        "domain": "composition",
                        "kind": "analysis_failure",
                        "severity": "blocking",
                        "message": "L’analyse n’a pas pu être terminée.",
                        "details": {"failure": failure},
                        "proposed_solution": "Relancer l’analyse. Si le problème persiste, conserver le rapport de diagnostic.",
                    }], stage="analysis")
                else:
                    prepared, translated, document, text_review = payload
                    report.update({
                        "preparation_ready": prepared.ready,
                        "canvas_contract_valid": prepared.canvas.valid,
                        "canvas_editor_payload_valid": translated.valid,
                        "document_plan_valid": document.valid,
                        "segments": len(document.plan.get("render_segments", [])),
                        "pagination_owner": document.plan.get("render_strategy", {}).get("pagination_owner"),
                        "line_break_owner": document.plan.get("render_strategy", {}).get("line_break_owner"),
                        "manual_line_coordinates": document.plan.get("render_strategy", {}).get("manual_line_coordinates"),
                        "text_quality": {
                            "counts": prepared.text_quality.counts,
                            **text_review,
                        },
                    })
                    write_report()
                    start_canvas(prepared, document)
        except queue.Empty:
            pass
        app.after(60, poll_results)

    def close_window() -> None:
        refresh_host_snapshot()
        if report["preparation_flow"].get("state") in {"waiting", "rendering"}:
            report["errors"] = [{"stage": "user_close", "message": "Fenêtre fermée pendant la préparation"}]
        write_report()
        destroy_host()
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", close_window)
    animate_waiting()
    rotate_waiting_text()
    poll_results()
    flow_event("waiting", reason="initial")
    app.after_idle(start_analysis)
    app.mainloop()

    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
