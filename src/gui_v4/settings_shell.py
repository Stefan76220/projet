from __future__ import annotations

"""Réglages généraux de Composition.

Cette couche contient uniquement les réglages du Livre.
"""

import tkinter as tk
import sys
import ctypes
from copy import deepcopy
from ctypes import wintypes

from src.gui_v4 import theme
from src.gui_v4.canvas_editor_host import CanvasEditorWebHost
from src.gui_v4.editorial_shell import TomeLineaV4Editorial, PROJECT_ROOT
from src.v4.canvas_loading import CanvasLoadSession
from src.v4.domain import BookFormat
from src.v4.general_text_rules_runtime import (
    apply_rules_to_plan,
    infer_rules_from_plans,
    normalize_general_text_rules,
)
from src.gui_v4.composition_explorer import navigation_model
from src.v4.format_catalog import (
    BY_KEY as STANDARD_FORMATS_BY_KEY,
    find_standard_format,
    nearest_standard_format,
    formats_by_ui_family,
)


class TomeLineaV4SettingsStage(TomeLineaV4Editorial):
    """Composition éditoriale + réglages généraux du Livre."""

    _TREE_GUARD_SEQUENCES = (
        "<ButtonPress-1>",
        "<ButtonRelease-1>",
        "<B1-Motion>",
        "<Double-Button-1>",
        "<KeyPress>",
    )

    def __init__(self, *, defer_show: bool = False) -> None:
        self._stage_display_tool = "settings"
        self._stage_tabs = {}
        self._settings_ui_locked = False
        self._settings_tree_guard_tag = None
        self._settings_disabled_widgets = []
        self._settings_initial_body_page_id = None
        self._settings_center_hwnd = None
        self._settings_center_was_enabled = None
        self._settings_format_key = None
        self._settings_format_label_var = None
        self._settings_format_apply_busy = False
        self._settings_format_apply_host = None
        self._settings_format_plan_changes = []
        self._settings_format_notice = ""
        self._settings_margin_vars = None
        self._settings_text_vars = None
        self._settings_applied_text_rules = None

        # Panneau persistant : les notifications Canvas ne détruisent plus
        # les contrôles pendant un clic ou une saisie.
        self._settings_panel_host_id = None
        self._settings_panel_root = None
        self._settings_panel_message_var = None
        self._settings_panel_notice_var = None
        self._settings_panel_action_button = None
        self._settings_panel_rebuild_count = 0

        # Survol observation simple : aucun arrêt automatique et aucun moteur
        # de navigation parallèle. Il consomme uniquement _activate_page().
        self._survol_running = False
        self._survol_started = False
        self._survol_completed = False
        self._survol_position = 0
        self._survol_expected_global_index = None
        self._survol_watch_after_id = None
        self._survol_dwell_after_id = None
        self._survol_generation = 0
        self._survol_dwell_ms = 2000
        self._survol_message = "Le Survol est prêt."
        self._survol_hook_host = None
        self._survol_hook_previous_callback = None

        super().__init__(defer_show=defer_show)

    def _settings_first_body_page_id(self) -> str | None:
        """Retourne la première vraie page du Corps selon l'Explorateur V4.

        Cette lecture est pure : elle ne navigue pas, ne construit pas de
        Canvas et ne déclenche aucun événement.
        """
        book = getattr(
            getattr(self, "session", None),
            "book",
            None,
        )
        if book is None:
            return None

        try:
            model = navigation_model(book)
        except Exception:
            return None

        candidates: list[tuple[int, str]] = []

        def collect(node) -> None:
            for item in list(node.get("pages") or ()):
                try:
                    number, page_id, _page = item
                    candidates.append(
                        (int(number), str(page_id))
                    )
                except Exception:
                    continue

            for child in list(node.get("children") or ()):
                if isinstance(child, dict):
                    collect(child)

        for root in list(model.get("roots") or ()):
            if not isinstance(root, dict):
                continue
            if str(root.get("id") or "") == "root:corps":
                collect(root)
                break

        if not candidates:
            return None

        candidates.sort(key=lambda item: item[0])
        return candidates[0][1]

    def _settings_prepare_initial_body_page(self) -> str | None:
        """Positionne la session AVANT la construction de Composition.

        C'est le point important de cette étape : aucun saut de page n'est
        demandé après le démarrage de Composition. Le moteur démarre directement
        avec la bonne page active.
        """
        target = self._settings_first_body_page_id()
        self._settings_initial_body_page_id = target

        if not target:
            return None

        session = getattr(self, "session", None)
        book = getattr(session, "book", None) if session is not None else None
        if book is None or target not in getattr(book, "pages", {}):
            return None

        # La session est positionnée avant que les widgets, le Canvas et les
        # callbacks de Composition n'existent.
        try:
            session.set_active_page(target)
        except Exception:
            return None

        # La sélection visuelle sera donc cohérente dès la construction du
        # Treeview. Aucun clic simulé, aucun _activate_page.
        self._composition_selected_page_ids = {target}
        return target

    def _build_composition(self, parent) -> None:
        # 1) Choisir la première page du Corps AVANT de lancer Composition.
        target = self._settings_prepare_initial_body_page()

        # 2) Composition est construite directement avec cette page active.
        super()._build_composition(parent)

        # 3) Verrou UI déjà validé à l'étape précédente.
        self._settings_ui_locked = True
        self._settings_apply_ui_lock()

        # Montrer la page active dans l'Explorateur sans appeler le moteur
        # de navigation. C'est uniquement une opération Treeview locale.
        navigator = getattr(self, "_composition_navigator", None)
        if navigator is not None and target:
            try:
                navigator.scroll_to_page(
                    str(target),
                    expand=True,
                )
                navigator.update_selection()
            except Exception:
                pass

        self._stage_display_tool = "settings"
        try:
            self._composition_refresh_tool_tabs()
        except Exception:
            pass
        try:
            self._composition_update_inspector_context()
        except Exception:
            pass

    def _composition_current_tool(self) -> str:
        tool = str(getattr(self, "_stage_display_tool", "settings") or "settings")
        if tool not in {"settings", "survol"}:
            tool = "settings"
        if bool(getattr(self, "_settings_ui_locked", False)) and tool == "survol":
            tool = "settings"
        self._stage_display_tool = tool
        self._composition_active_tool = tool
        return tool

    def _composition_activate_tool(self, tool: str) -> None:
        wanted = "survol" if str(tool) == "survol" else "settings"

        # Survol est réellement inaccessible tant que les choix initiaux
        # n'ont pas été validés.
        if wanted == "survol" and bool(getattr(self, "_settings_ui_locked", False)):
            wanted = "settings"

        if wanted == "settings" and bool(getattr(self, "_survol_running", False)):
            self._survol_pause("Survol en pause — réglages ouverts.")

        self._stage_display_tool = wanted
        self._composition_active_tool = wanted
        try:
            self._composition_refresh_tool_tabs()
        except Exception:
            pass
        try:
            self._composition_update_inspector_context()
        except Exception:
            pass

    def _composition_build_tool_rail(self, parent):
        """Réglages puis Survol : mécanique historique, moteur actuel conservé."""
        self._composition_active_tool = "settings"
        self._stage_display_tool = "settings"

        rail = tk.Frame(parent, bg=theme.PANEL_ALT, width=76)
        rail.pack_propagate(False)
        self._stage_tabs = {}
        self._composition_tool_tabs = {}

        def add_tab(key: str, label: str) -> None:
            tab = tk.Canvas(
                rail,
                width=74,
                height=44,
                bg=theme.PANEL_SOFT,
                highlightthickness=0,
                bd=0,
                takefocus=True,
                cursor="hand2",
            )
            tab.pack(fill="x", padx=(1, 1), pady=(1, 0))
            text_id = tab.create_text(
                37,
                22,
                text=label,
                width=68,
                justify="center",
                fill=theme.INK,
                font=(theme.FONT_UI, 8, "bold"),
            )

            def activate(_event=None, selected=key):
                self._composition_activate_tool(selected)
                return "break"

            tab.bind("<Button-1>", activate)
            tab.bind("<Return>", activate)
            tab.bind("<space>", activate)
            self._stage_tabs[key] = (tab, text_id)

        add_tab("survol", "Survol")
        add_tab("settings", "Réglages")
        self._composition_tool_tabs = dict(self._stage_tabs)
        self._composition_refresh_tool_tabs()
        return rail

    def _composition_refresh_tool_tabs(self) -> None:
        active = str(getattr(self, "_stage_display_tool", "settings") or "settings")
        locked = bool(getattr(self, "_settings_ui_locked", False))

        for key, pair in dict(getattr(self, "_stage_tabs", {}) or {}).items():
            try:
                canvas, text_id = pair
            except Exception:
                continue

            disabled = bool(key == "survol" and locked)
            selected = bool(key == active and not disabled)
            try:
                canvas.configure(
                    bg=(theme.ACCENT_DARK if selected else theme.PANEL_SOFT),
                    cursor=("arrow" if disabled else "hand2"),
                )
                canvas.itemconfigure(
                    text_id,
                    fill=(
                        theme.MUTED_DARK
                        if disabled
                        else theme.WHITE
                        if selected
                        else theme.INK
                    ),
                )
            except Exception:
                pass


    # ==========================================================
    # SURVOL OBSERVATION — moteur simple sur navigation validée
    # ==========================================================

    def _survol_page_order(self) -> list[str]:
        book = getattr(getattr(self, "session", None), "book", None)
        if book is None:
            return []
        return [str(page_id) for page_id in list(getattr(book, "page_order", ()) or ())]

    def _survol_current_position(self) -> int:
        order = self._survol_page_order()
        if not order:
            return 0
        active = str(getattr(getattr(self, "session", None), "active_page_id", "") or "")
        try:
            return order.index(active)
        except ValueError:
            return max(0, min(int(getattr(self, "_survol_position", 0) or 0), len(order) - 1))

    def _survol_cancel_timers(self) -> None:
        for attr in ("_survol_watch_after_id", "_survol_dwell_after_id"):
            after_id = getattr(self, attr, None)
            if after_id is not None:
                try:
                    self.after_cancel(after_id)
                except Exception:
                    pass
            setattr(self, attr, None)

    def _survol_set_click_hook_active(self, active: bool) -> None:
        host = getattr(self, "_phase2_canvas_host", None)
        if host is None or getattr(host, "_web", None) is None:
            return
        script = f"window.__TL_SURVOL_PAUSE_ACTIVE__ = {str(bool(active)).lower()}; true;"
        try:
            host._web.eval_js(script)
        except Exception:
            pass

    def _survol_attach_click_hook(self) -> None:
        host = getattr(self, "_phase2_canvas_host", None)
        if host is None or getattr(host, "_web", None) is None:
            return

        previous_host = getattr(self, "_survol_hook_host", None)
        if previous_host is not None and previous_host is not host:
            try:
                previous_host._on_page_changed_callback = getattr(
                    self, "_survol_hook_previous_callback", None
                )
            except Exception:
                pass
            self._survol_hook_host = None
            self._survol_hook_previous_callback = None

        if getattr(self, "_survol_hook_host", None) is not host:
            previous_callback = getattr(host, "_on_page_changed_callback", None)
            self._survol_hook_host = host
            self._survol_hook_previous_callback = previous_callback

            def on_page_event(event: dict) -> None:
                old = getattr(self, "_survol_hook_previous_callback", None)
                if callable(old):
                    try:
                        old(dict(event or {}))
                    except Exception:
                        pass
                payload = dict(event or {})
                if (
                    bool(payload.get("survolPause"))
                    or str(payload.get("reason") or "") == "survol_user_click"
                ):
                    if bool(getattr(self, "_survol_running", False)):
                        self._survol_pause("Survol en pause — clic sur la page.")

            host._on_page_changed_callback = on_page_event

        script = r"""
(() => {
  window.__TL_SURVOL_PAUSE_ACTIVE__ = true;
  if (window.__TL_SURVOL_PAUSE_HOOK__) return true;
  window.__TL_SURVOL_PAUSE_HOOK__ = true;
  document.addEventListener('pointerdown', (event) => {
    if (!window.__TL_SURVOL_PAUSE_ACTIVE__) return;
    const target = event.target instanceof Element ? event.target : null;
    if (!target || !target.closest('.ce-page-container')) return;
    try {
      const status = (typeof window.tomeLineaCanvasStatus === 'function')
        ? window.tomeLineaCanvasStatus()
        : {};
      const pageNo = Math.max(1, Number(status.activePage || 1));
      const pageCount = Math.max(1, Number(status.pageCount || 1));
      if (window.ipc && typeof window.ipc.postMessage === 'function') {
        window.ipc.postMessage(JSON.stringify({
          type: 'page_changed',
          pageNo,
          pageCount,
          reason: 'survol_user_click',
          survolPause: true,
        }));
      }
    } catch (_) {}
  }, true);
  return true;
})()
"""
        try:
            host._web.eval_js(script)
        except Exception:
            pass

    def _survol_detach_click_hook(self) -> None:
        host = getattr(self, "_survol_hook_host", None)
        if host is not None:
            try:
                host._on_page_changed_callback = getattr(
                    self, "_survol_hook_previous_callback", None
                )
            except Exception:
                pass
        self._survol_hook_host = None
        self._survol_hook_previous_callback = None
        self._survol_set_click_hook_active(False)

    def _survol_refresh_panel(self) -> None:
        if str(getattr(self, "_stage_display_tool", "settings")) != "survol":
            return
        try:
            self._composition_update_inspector_context()
        except Exception:
            pass

    def _survol_request_position(self, position: int) -> None:
        if not bool(getattr(self, "_survol_running", False)):
            return
        order = self._survol_page_order()
        if not order:
            self._survol_stop("Aucune page à survoler.")
            return

        position = max(0, min(int(position), len(order) - 1))
        self._survol_cancel_timers()
        self._survol_generation += 1
        generation = int(self._survol_generation)
        self._survol_position = position
        page_id = order[position]
        self._survol_message = f"Ouverture de la page {position + 1} / {len(order)}…"
        self._survol_refresh_panel()

        # Porte unique : exactement la même activation que Structure / Aller /
        # Précédente / Suivante. Le Survol ne sait rien charger lui-même.
        self._activate_page(page_id)

        try:
            expected = self._phase2_active_page_index()
        except Exception:
            expected = None
        self._survol_expected_global_index = expected
        self._survol_attach_click_hook()

        self._survol_watch_after_id = self.after(
            50,
            lambda g=generation, p=position, pid=page_id: self._survol_wait_visible(g, p, pid),
        )

    def _survol_wait_visible(self, generation: int, position: int, page_id: str) -> None:
        self._survol_watch_after_id = None
        if generation != int(getattr(self, "_survol_generation", 0) or 0):
            return
        if not bool(getattr(self, "_survol_running", False)):
            return

        self._survol_attach_click_hook()
        state = str(getattr(self, "_phase2_canvas_state", "") or "")
        active = str(getattr(getattr(self, "session", None), "active_page_id", "") or "")
        host = getattr(self, "_phase2_canvas_host", None)

        # Même critère que le Survol archivé fonctionnel :
        # la page demandée est active, le Canvas courant est prêt et son état
        # est ready. On ne dépend jamais d'un index affiché supplémentaire.
        ready = bool(
            active == str(page_id)
            and host is not None
            and bool(getattr(host, "ready", False))
            and state == "ready"
            and not bool(getattr(self, "_phase2_switch_in_progress", False))
        )

        if not ready:
            self._survol_watch_after_id = self.after(
                60,
                lambda g=generation, p=position, pid=page_id: self._survol_wait_visible(g, p, pid),
            )
            return

        order = self._survol_page_order()
        self._survol_message = f"Page {position + 1} / {len(order)}"
        self._survol_refresh_panel()
        self._survol_dwell_after_id = self.after(
            int(getattr(self, "_survol_dwell_ms", 2000) or 2000),
            lambda g=generation, p=position: self._survol_advance(g, p),
        )

    def _survol_advance(self, generation: int, position: int) -> None:
        self._survol_dwell_after_id = None
        if generation != int(getattr(self, "_survol_generation", 0) or 0):
            return
        if not bool(getattr(self, "_survol_running", False)):
            return

        order = self._survol_page_order()
        next_position = int(position) + 1
        if next_position >= len(order):
            self._survol_running = False
            self._survol_started = True
            self._survol_completed = True
            self._survol_message = "Survol terminé — dernière page atteinte."
            self._survol_set_click_hook_active(False)
            self._survol_refresh_panel()
            return

        self._survol_request_position(next_position)

    def _survol_start(self) -> None:
        if bool(getattr(self, "_settings_ui_locked", False)):
            return
        order = self._survol_page_order()
        if not order:
            self._survol_message = "Aucune page à survoler."
            self._survol_refresh_panel()
            return

        self._survol_cancel_timers()
        self._survol_running = True
        self._survol_started = True
        self._survol_completed = False
        self._survol_position = 0
        self._survol_message = f"Survol en cours — {len(order)} pages."
        self._survol_request_position(0)

    def _survol_pause(self, message: str = "Survol en pause.") -> None:
        if not bool(getattr(self, "_survol_started", False)):
            return
        self._survol_running = False
        self._survol_cancel_timers()
        self._survol_generation += 1
        self._survol_position = self._survol_current_position()
        self._survol_message = str(message or "Survol en pause.")
        self._survol_set_click_hook_active(False)
        self._survol_refresh_panel()

    def _survol_continue(self) -> None:
        if bool(getattr(self, "_settings_ui_locked", False)):
            return
        order = self._survol_page_order()
        if not order:
            return
        self._survol_cancel_timers()
        self._survol_running = True
        self._survol_started = True
        self._survol_completed = False
        self._survol_position = self._survol_current_position()
        self._survol_message = "Survol repris."
        self._survol_request_position(self._survol_position)

    def _survol_stop(self, message: str = "Survol arrêté.") -> None:
        self._survol_running = False
        self._survol_started = False
        self._survol_completed = False
        self._survol_cancel_timers()
        self._survol_generation += 1
        self._survol_position = self._survol_current_position()
        self._survol_message = str(message or "Survol arrêté.")
        self._survol_detach_click_hook()
        self._survol_refresh_panel()

    def _survol_render_panel(self, host) -> None:
        for child in host.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass

        order = self._survol_page_order()
        total = len(order)
        position = self._survol_current_position() if total else 0

        tk.Label(
            host,
            text="SURVOL",
            bg=theme.PANEL,
            fg=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 10, "bold"),
            anchor="w",
        ).pack(fill="x", padx=18, pady=(14, 3))

        tk.Label(
            host,
            text=(f"Page {position + 1} / {total}" if total else "Aucune page"),
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 9, "bold"),
            anchor="w",
        ).pack(fill="x", padx=18, pady=(0, 8))

        tk.Label(
            host,
            text=str(getattr(self, "_survol_message", "") or "Le Survol est prêt."),
            bg=theme.PANEL,
            fg=theme.INK,
            wraplength=215,
            justify="left",
            anchor="w",
            font=(theme.FONT_UI, 8),
        ).pack(fill="x", padx=18, pady=(0, 10))

        tk.Label(
            host,
            text="Aucun arrêt automatique · 2 s par page",
            bg=theme.PANEL,
            fg=theme.MUTED,
            wraplength=215,
            justify="left",
            anchor="w",
            font=(theme.FONT_UI, 8),
        ).pack(fill="x", padx=18, pady=(0, 12))

        if bool(getattr(self, "_survol_completed", False)):
            self._button(
                host,
                "Recommencer le Survol",
                self._survol_start,
                compact=True,
                accent=True,
            ).pack(fill="x", padx=18, pady=(0, 7))
            return

        if bool(getattr(self, "_survol_running", False)):
            self._button(host, "Pause", self._survol_pause, compact=True).pack(
                fill="x", padx=18, pady=(0, 7)
            )
            self._button(host, "Arrêter", self._survol_stop, compact=True).pack(
                fill="x", padx=18, pady=(0, 7)
            )
            return

        if bool(getattr(self, "_survol_started", False)):
            self._button(
                host,
                "Reprendre",
                self._survol_continue,
                compact=True,
                accent=True,
            ).pack(fill="x", padx=18, pady=(0, 7))
            self._button(host, "Arrêter", self._survol_stop, compact=True).pack(
                fill="x", padx=18, pady=(0, 7)
            )
            return

        if bool(getattr(self, "_settings_ui_locked", False)):
            tk.Label(
                host,
                text="Validez d'abord les réglages du Livre.",
                bg=theme.PANEL,
                fg=theme.MUTED_DARK,
                wraplength=215,
                justify="left",
                anchor="w",
                font=(theme.FONT_UI, 8, "bold"),
            ).pack(fill="x", padx=18, pady=(0, 8))
            return

        self._button(
            host,
            "Commencer le Survol",
            self._survol_start,
            compact=True,
            accent=True,
        ).pack(fill="x", padx=18, pady=(0, 7))

    @staticmethod
    def _settings_mm(value) -> str:
        try:
            number = float(value)
        except (TypeError, ValueError):
            return "?"
        if abs(number - round(number)) < 1e-9:
            return str(int(round(number)))
        return f"{number:.1f}".replace(".", ",")

    def _settings_current_format(self):
        book = getattr(
            getattr(self, "session", None),
            "book",
            None,
        )
        return getattr(book, "format", None) if book is not None else None

    def _settings_initial_format_key(self) -> str | None:
        fmt = self._settings_current_format()
        if fmt is None:
            return None

        try:
            exact = find_standard_format(
                float(fmt.width_mm),
                float(fmt.height_mm),
            )
        except Exception:
            exact = None

        if exact is not None:
            return str(exact.key)

        try:
            nearest = nearest_standard_format(
                float(fmt.width_mm),
                float(fmt.height_mm),
            )
        except Exception:
            nearest = None

        return str(nearest.key) if nearest is not None else None

    def _settings_format_display(self, key: str | None) -> str:
        item = STANDARD_FORMATS_BY_KEY.get(str(key or ""))
        if item is None:
            return "Choisir un format"
        return item.display_label

    def _settings_choose_format(self, key: str) -> None:
        key = str(key or "")
        if key not in STANDARD_FORMATS_BY_KEY:
            return

        # Étape 06 : choix purement UI.
        # Aucun Livre, plan, Canvas ou moteur de pagination n'est modifié.
        self._settings_format_key = key

        variable = getattr(
            self,
            "_settings_format_label_var",
            None,
        )
        if variable is not None:
            try:
                variable.set(
                    self._settings_format_display(key)
                )
            except Exception:
                pass

    @staticmethod
    def _settings_decimal(value, label: str) -> float:
        raw = str(value or "").strip().replace(",", ".")
        if not raw:
            raise ValueError(f"{label} : valeur manquante.")
        try:
            number = float(raw)
        except (TypeError, ValueError):
            raise ValueError(f"{label} : valeur invalide.")
        if number < 0 or number > 80:
            raise ValueError(f"{label} : utilisez une valeur entre 0 et 80 mm.")
        return float(number)

    def _settings_prepare_margin_vars(self) -> dict:
        vars_map = getattr(self, "_settings_margin_vars", None)
        if isinstance(vars_map, dict):
            return vars_map

        fmt = self._settings_current_format()
        if fmt is None:
            values = {
                "top": 15.0,
                "bottom": 15.0,
                "inside": 15.0,
                "outside": 15.0,
            }
        else:
            values = {
                "top": float(fmt.margin_top_mm),
                "bottom": float(fmt.margin_bottom_mm),
                "inside": float(fmt.margin_inside_mm),
                "outside": float(fmt.margin_outside_mm),
            }

        vars_map = {
            key: tk.StringVar(
                master=self,
                value=self._settings_mm(value),
            )
            for key, value in values.items()
        }
        self._settings_margin_vars = vars_map
        return vars_map

    def _settings_margin_values(self, target) -> dict:
        vars_map = self._settings_prepare_margin_vars()

        margins = {
            "top": self._settings_decimal(
                vars_map["top"].get(),
                "Marge haute",
            ),
            "bottom": self._settings_decimal(
                vars_map["bottom"].get(),
                "Marge basse",
            ),
            "inside": self._settings_decimal(
                vars_map["inside"].get(),
                "Marge intérieure",
            ),
            "outside": self._settings_decimal(
                vars_map["outside"].get(),
                "Marge extérieure",
            ),
        }

        width = float(target.width_mm)
        height = float(target.height_mm)

        if margins["inside"] + margins["outside"] >= width:
            raise ValueError(
                "Marges intérieure + extérieure : largeur utile nulle."
            )
        if margins["top"] + margins["bottom"] >= height:
            raise ValueError(
                "Marges haute + basse : hauteur utile nulle."
            )

        return margins

    def _settings_render_margin_card(self, host) -> None:
        vars_map = self._settings_prepare_margin_vars()

        card = tk.Frame(
            host,
            bg=theme.PANEL_SOFT,
            highlightthickness=1,
            highlightbackground=theme.BORDER_SOFT,
        )
        card.pack(
            fill="x",
            padx=12,
            pady=(0, 8),
        )

        tk.Label(
            card,
            text="2 — MARGES",
            bg=theme.PANEL_SOFT,
            fg=theme.INK,
            font=(theme.FONT_UI, 9, "bold"),
            anchor="w",
        ).pack(
            fill="x",
            padx=10,
            pady=(8, 5),
        )

        grid = tk.Frame(card, bg=theme.PANEL_SOFT)
        grid.pack(
            fill="x",
            padx=10,
            pady=(0, 9),
        )
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)

        fields = (
            ("Haut", "top", 0, 0),
            ("Bas", "bottom", 0, 1),
            ("Intérieure", "inside", 1, 0),
            ("Extérieure", "outside", 1, 1),
        )

        for label, key, row, column in fields:
            cell = tk.Frame(grid, bg=theme.PANEL_SOFT)
            cell.grid(
                row=row,
                column=column,
                sticky="ew",
                padx=((0, 5) if column == 0 else (5, 0)),
                pady=(0, 5) if row == 0 else (0, 0),
            )

            tk.Label(
                cell,
                text=label,
                bg=theme.PANEL_SOFT,
                fg=theme.MUTED,
                font=(theme.FONT_UI, 7),
                anchor="w",
            ).pack(fill="x")

            line = tk.Frame(cell, bg=theme.PANEL_SOFT)
            line.pack(fill="x", pady=(1, 0))

            entry = tk.Entry(
                line,
                textvariable=vars_map[key],
                width=6,
                bg=theme.PANEL_ALT,
                fg=theme.INK,
                insertbackground=theme.INK,
                disabledbackground=theme.PANEL_ALT,
                disabledforeground=theme.MUTED,
                relief="flat",
                bd=0,
                justify="right",
                font=(theme.FONT_UI, 8),
            )
            entry.pack(side="left", fill="x", expand=True, ipady=3)

            tk.Label(
                line,
                text="mm",
                bg=theme.PANEL_SOFT,
                fg=theme.MUTED,
                font=(theme.FONT_UI, 7),
            ).pack(side="left", padx=(4, 0))

    def _settings_initial_text_rules(self) -> dict:
        plans = list(getattr(self, "_phase2_chapter_plans", ()) or ())
        try:
            inferred = infer_rules_from_plans(plans) if plans else normalize_general_text_rules({})
        except Exception:
            inferred = normalize_general_text_rules({})

        book = getattr(getattr(self, "session", None), "book", None)
        metadata = getattr(book, "metadata", {}) if book is not None else {}
        existing = metadata.get("text_general_rules") if isinstance(metadata, dict) else None
        merged = dict(inferred)
        if isinstance(existing, dict):
            for key in (
                "font_family", "font_size_pt", "alignment",
                "first_line_indent_mm", "line_spacing_multiple",
                "paragraph_gap_mm",
            ):
                value = existing.get(key)
                if value not in (None, ""):
                    merged[key] = value
            if existing.get("line_spacing_multiple") in (None, "") and existing.get("line_pitch_mm") not in (None, ""):
                try:
                    size_pt = float(merged.get("font_size_pt") or 11.0)
                    pitch = float(existing.get("line_pitch_mm"))
                    base = size_pt * 25.4 / 72.0
                    if pitch > 0 and base > 0:
                        merged["line_spacing_multiple"] = pitch / base
                except Exception:
                    pass
        merged["hyphenation"] = "forbid"
        return normalize_general_text_rules(merged)

    def _settings_prepare_text_vars(self) -> dict:
        vars_map = getattr(self, "_settings_text_vars", None)
        if isinstance(vars_map, dict):
            return vars_map
        rules = self._settings_initial_text_rules()
        vars_map = {
            "font_family": tk.StringVar(master=self, value=str(rules.get("font_family") or "Arial")),
            "font_size_pt": tk.StringVar(master=self, value=self._settings_mm(rules.get("font_size_pt", 11))),
            "first_line_indent_mm": tk.StringVar(master=self, value=self._settings_mm(rules.get("first_line_indent_mm", 0))),
            "line_spacing_multiple": tk.StringVar(master=self, value=str(rules.get("line_spacing_multiple", 1.15)).replace(".", ",")),
            "paragraph_gap_mm": tk.StringVar(master=self, value=self._settings_mm(rules.get("paragraph_gap_mm", 0))),
            "alignment": tk.StringVar(master=self, value=str(rules.get("alignment") or "justify")),
        }
        self._settings_text_vars = vars_map
        return vars_map

    @staticmethod
    def _settings_text_number(raw, label: str, minimum: float, maximum: float) -> float:
        text = str(raw or "").strip().replace(",", ".")
        try:
            value = float(text)
        except (TypeError, ValueError):
            raise ValueError(f"{label} : valeur invalide.")
        if value < minimum or value > maximum:
            raise ValueError(f"{label} : valeur attendue entre {minimum:g} et {maximum:g}.")
        return float(value)

    def _settings_available_text_fonts(self) -> list[str]:
        names = set()
        try:
            names.update(str(name).strip() for name in self._global_settings_available_fonts() if str(name).strip())
        except Exception:
            pass
        try:
            current = str(self._settings_prepare_text_vars()["font_family"].get() or "").strip()
        except Exception:
            current = ""
        if current:
            names.add(current)
        if not names:
            names.update({"Arial", "Georgia", "Times New Roman", "Verdana"})
        return sorted(names, key=lambda value: value.casefold())

    def _settings_text_values(self) -> dict:
        vars_map = self._settings_prepare_text_vars()
        font = str(vars_map["font_family"].get() or "").strip()
        if not font:
            raise ValueError("Police : choisissez une police.")
        available = {name.casefold(): name for name in self._settings_available_text_fonts()}
        if available and font.casefold() not in available:
            raise ValueError(f"Police : {font} n'est pas disponible.")
        font = available.get(font.casefold(), font)
        return normalize_general_text_rules({
            "font_family": font,
            "font_size_pt": self._settings_text_number(vars_map["font_size_pt"].get(), "Taille", 6, 72),
            "alignment": str(vars_map["alignment"].get() or "justify"),
            "first_line_indent_mm": self._settings_text_number(vars_map["first_line_indent_mm"].get(), "Retrait de première ligne", 0, 30),
            "line_spacing_multiple": self._settings_text_number(vars_map["line_spacing_multiple"].get(), "Interligne", 0.8, 3),
            "paragraph_gap_mm": self._settings_text_number(vars_map["paragraph_gap_mm"].get(), "Espace après paragraphe", 0, 20),
            "hyphenation": "forbid",
        })

    def _settings_render_text_card(self, host) -> None:
        vars_map = self._settings_prepare_text_vars()
        card = tk.Frame(host, bg=theme.PANEL_SOFT, highlightthickness=1, highlightbackground=theme.BORDER_SOFT)
        card.pack(fill="x", padx=12, pady=(0, 8))
        tk.Label(card, text="3 — TEXTE COURANT", bg=theme.PANEL_SOFT, fg=theme.INK,
                 font=(theme.FONT_UI, 9, "bold"), anchor="w").pack(fill="x", padx=10, pady=(8, 4))

        font_button = tk.Menubutton(
            card, textvariable=vars_map["font_family"], bg=theme.PANEL_ALT, fg=theme.INK,
            activebackground=theme.PANEL_SOFT, activeforeground=theme.WHITE,
            relief="flat", bd=0, anchor="w", padx=7, pady=4,
            font=(theme.FONT_UI, 8), cursor="hand2",
        )
        font_button.pack(fill="x", padx=10, pady=(0, 5))
        font_menu = tk.Menu(font_button, tearoff=False, bg=theme.PANEL_ALT, fg=theme.INK,
                            activebackground=theme.ACCENT_DARK, activeforeground=theme.WHITE)
        fonts = self._settings_available_text_fonts()
        for label, start, end in (("A–F", "A", "G"), ("G–L", "G", "M"), ("M–R", "M", "S"), ("S–Z", "S", "ZZZZ")):
            values = [name for name in fonts if start <= name.upper() < end]
            if not values:
                continue
            submenu = tk.Menu(font_menu, tearoff=False, bg=theme.PANEL_ALT, fg=theme.INK,
                              activebackground=theme.ACCENT_DARK, activeforeground=theme.WHITE)
            for name in values:
                submenu.add_command(label=name, command=lambda value=name: vars_map["font_family"].set(value))
            font_menu.add_cascade(label=label, menu=submenu)
        font_button.configure(menu=font_menu)

        grid = tk.Frame(card, bg=theme.PANEL_SOFT)
        grid.pack(fill="x", padx=10, pady=(0, 5))
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)
        for label, key, suffix, row, column in (
            ("Taille", "font_size_pt", "pt", 0, 0),
            ("Retrait 1re ligne", "first_line_indent_mm", "mm", 0, 1),
            ("Interligne", "line_spacing_multiple", "×", 1, 0),
            ("Espace après", "paragraph_gap_mm", "mm", 1, 1),
        ):
            cell = tk.Frame(grid, bg=theme.PANEL_SOFT)
            cell.grid(row=row, column=column, sticky="ew",
                      padx=((0, 5) if column == 0 else (5, 0)),
                      pady=(0, 4) if row == 0 else (0, 0))
            tk.Label(cell, text=label, bg=theme.PANEL_SOFT, fg=theme.MUTED,
                     font=(theme.FONT_UI, 7), anchor="w").pack(fill="x")
            line = tk.Frame(cell, bg=theme.PANEL_SOFT)
            line.pack(fill="x", pady=(1, 0))
            tk.Entry(line, textvariable=vars_map[key], width=6, bg=theme.PANEL_ALT, fg=theme.INK,
                     insertbackground=theme.INK, relief="flat", bd=0, justify="right",
                     font=(theme.FONT_UI, 8)).pack(side="left", fill="x", expand=True, ipady=3)
            tk.Label(line, text=suffix, bg=theme.PANEL_SOFT, fg=theme.MUTED,
                     font=(theme.FONT_UI, 7)).pack(side="left", padx=(4, 0))

        row = tk.Frame(card, bg=theme.PANEL_SOFT)
        row.pack(fill="x", padx=10, pady=(4, 3))
        buttons = []
        def refresh():
            current = str(vars_map["alignment"].get() or "justify")
            for button, value in buttons:
                selected = current == value
                button.configure(bg=(theme.ACCENT_DARK if selected else theme.PANEL_ALT),
                                 fg=(theme.WHITE if selected else theme.INK))
        for index, (label, value) in enumerate((("Justifié", "justify"), ("À gauche", "left"))):
            button = tk.Button(
                row, text=label,
                command=lambda selected=value: (vars_map["alignment"].set(selected), refresh()),
                bg=theme.PANEL_ALT, fg=theme.INK,
                activebackground=theme.ACCENT_DARK, activeforeground=theme.WHITE,
                relief="flat", bd=0, cursor="hand2", font=(theme.FONT_UI, 7, "bold"),
            )
            button.pack(side="left", fill="x", expand=True,
                        padx=((0, 3) if index == 0 else (3, 0)), ipady=3)
            buttons.append((button, value))
        refresh()
        tk.Label(card, text="Titres exclus · césures interdites", bg=theme.PANEL_SOFT,
                 fg=theme.MUTED, font=(theme.FONT_UI, 7), anchor="w").pack(
                     fill="x", padx=10, pady=(2, 7))

    @staticmethod
    def _settings_format_px(mm_value: float) -> float:
        return float(mm_value) * 96.0 / 25.4

    @staticmethod
    def _settings_format_direction(width_mm: float, height_mm: float) -> str:
        return "horizontal" if float(width_mm) > float(height_mm) else "vertical"

    def _settings_restore_plan_changes(self) -> None:
        """Restaure exactement les seules valeurs modifiées dans les plans."""
        changes = list(
            getattr(self, "_settings_format_plan_changes", ()) or ()
        )
        self._settings_format_plan_changes = []

        for mapping, key, existed, old_value in reversed(changes):
            try:
                if existed:
                    mapping[key] = deepcopy(old_value)
                else:
                    mapping.pop(key, None)
            except Exception:
                pass

    def _settings_record_plan_value(self, mapping, key) -> None:
        if not isinstance(mapping, dict):
            return
        self._settings_format_plan_changes.append(
            (
                mapping,
                key,
                key in mapping,
                deepcopy(mapping.get(key)),
            )
        )

    def _settings_patch_page_break_options(
        self,
        main,
        *,
        width_px: float,
        height_px: float,
        direction: str,
        margins_px: list[float],
    ) -> int:
        """Met à jour les vrais sauts de section utilisés par Canvas."""
        changed = 0
        if not isinstance(main, list):
            return changed

        for item in main:
            if not isinstance(item, dict):
                continue
            if str(item.get("type") or "").lower() != "pagebreak":
                continue

            self._settings_record_plan_value(item, "paperDirection")
            item["paperDirection"] = direction

            ext = item.get("extension")
            tl = ext.get("tomelinea") if isinstance(ext, dict) else None
            next_options = (
                tl.get("nextSectionOptions")
                if isinstance(tl, dict)
                else None
            )
            if isinstance(next_options, dict):
                for key, value in (
                    ("width", width_px),
                    ("height", height_px),
                    ("paperDirection", direction),
                    ("margins", list(margins_px)),
                ):
                    self._settings_record_plan_value(next_options, key)
                    next_options[key] = deepcopy(value)

            changed += 1

        return changed

    def _settings_patch_all_plans_for_format(
        self,
        target,
        margins: dict,
        text_rules: dict,
    ) -> dict:
        """Modifie uniquement les options réellement consommées par host.js.

        Aucune pagination n'est lancée ici. Le Canvas de remplacement mesurera
        ensuite la page courante avec ces plans.
        """
        plans = list(getattr(self, "_phase2_chapter_plans", ()) or ())
        if not plans:
            raise RuntimeError("Composition n'est pas prête.")

        width_mm = float(target.width_mm)
        height_mm = float(target.height_mm)
        top = float(margins["top"])
        bottom = float(margins["bottom"])
        inside = float(margins["inside"])
        outside = float(margins["outside"])

        if inside + outside >= width_mm:
            raise ValueError(
                "Le format choisi est trop étroit pour les marges actuelles."
            )
        if top + bottom >= height_mm:
            raise ValueError(
                "Le format choisi est trop bas pour les marges actuelles."
            )

        width_px = self._settings_format_px(width_mm)
        height_px = self._settings_format_px(height_mm)
        direction = self._settings_format_direction(width_mm, height_mm)
        margins_px = [
            self._settings_format_px(top),
            self._settings_format_px(outside),
            self._settings_format_px(bottom),
            self._settings_format_px(inside),
        ]

        self._settings_format_plan_changes = []
        segment_count = 0
        page_break_count = 0
        paragraph_count = 0
        text_element_count = 0

        try:
            for plan in plans:
                if not isinstance(plan, dict):
                    continue
                for segment in list(plan.get("render_segments") or ()):
                    if not isinstance(segment, dict):
                        continue

                    data = segment.get("data")
                    if isinstance(data, dict) and isinstance(data.get("main"), list):
                        self._settings_record_plan_value(data, "main")

                    options = segment.get("options")
                    if not isinstance(options, dict):
                        options = {}
                        segment["options"] = options

                    self._settings_record_plan_value(options, "defaultTabWidth")

                    for key, value in (
                        ("width", width_px),
                        ("height", height_px),
                        ("paperDirection", direction),
                        ("margins", list(margins_px)),
                    ):
                        self._settings_record_plan_value(options, key)
                        options[key] = deepcopy(value)

                    data = segment.get("data")
                    main = data.get("main") if isinstance(data, dict) else None
                    page_break_count += self._settings_patch_page_break_options(
                        main,
                        width_px=width_px,
                        height_px=height_px,
                        direction=direction,
                        margins_px=margins_px,
                    )
                    segment_count += 1

                text_report = apply_rules_to_plan(plan, text_rules)
                paragraph_count += int(text_report.get("paragraphs", 0))
                text_element_count += int(text_report.get("elements", 0))

            if segment_count <= 0:
                raise RuntimeError("Aucun segment Canvas à recomposer.")

        except Exception:
            self._settings_restore_plan_changes()
            raise

        return {
            "plans": len(plans),
            "segments": segment_count,
            "page_breaks": page_break_count,
            "paragraphs": paragraph_count,
            "text_elements": text_element_count,
        }

    def _settings_cleanup_format_host(self) -> None:
        host = getattr(self, "_settings_format_apply_host", None)
        self._settings_format_apply_host = None
        if host is None:
            return
        try:
            host.hide()
        except Exception:
            pass
        try:
            host.shutdown()
        except Exception:
            pass
        try:
            host.destroy()
        except Exception:
            pass

    def _settings_abort_format_apply(self, message: str) -> None:
        """Échec avant échange : le Canvas Composition visible reste intact."""
        self._settings_cleanup_format_host()
        self._settings_restore_plan_changes()
        self._settings_format_apply_busy = False
        self._settings_format_notice = str(message or "Recomposition impossible.")
        try:
            self._composition_update_inspector_context()
        except Exception:
            pass

    def _settings_commit_book_format(
        self,
        target,
        margins: dict,
        text_rules: dict,
    ) -> None:
        """Enregistre le format seulement après réussite du Canvas caché."""
        fmt = self._settings_current_format()
        if fmt is None:
            raise RuntimeError("Format courant indisponible.")

        def action(project):
            from src.v4.text_rules import update_text_general_rules

            book = project.book
            current = book.format
            new_format = BookFormat(
                width_mm=float(target.width_mm),
                height_mm=float(target.height_mm),
                margin_top_mm=float(margins["top"]),
                margin_bottom_mm=float(margins["bottom"]),
                margin_inside_mm=float(margins["inside"]),
                margin_outside_mm=float(margins["outside"]),
                bleed_top_mm=float(current.bleed_top_mm),
                bleed_right_mm=float(current.bleed_right_mm),
                bleed_bottom_mm=float(current.bleed_bottom_mm),
                bleed_left_mm=float(current.bleed_left_mm),
            )
            new_format.validate()
            book.format = new_format
            book.metadata["format_catalog_key"] = str(target.key)
            book.metadata["format_catalog_label"] = str(target.label)
            book.metadata["format_platforms"] = list(target.platforms)
            book.metadata["format_user_modified"] = True
            book.metadata["layout_reflow_check_required"] = True

            saved_rules = update_text_general_rules(
                book,
                confirmed=True,
                font_family=text_rules["font_family"],
                font_size_pt=text_rules["font_size_pt"],
                alignment=text_rules["alignment"],
                inside_margins=True,
                hyphenation="forbid",
                first_line_indent_mm=text_rules["first_line_indent_mm"],
                line_pitch_mm=text_rules["line_pitch_mm"],
                paragraph_gap_mm=text_rules["paragraph_gap_mm"],
            )
            saved_rules["line_spacing_multiple"] = text_rules["line_spacing_multiple"]
            book.metadata["text_general_rules"] = saved_rules
            book.metadata["text_reflow_requested"] = True

            try:
                self._global_settings_apply_book_content(book, text_rules)
            except Exception:
                pass

            book.history.append({
                "action": "format_canvas_runtime",
                "format_key": str(target.key),
                "width_mm": float(target.width_mm),
                "height_mm": float(target.height_mm),
                "margins_mm": {
                    "top": float(margins["top"]),
                    "bottom": float(margins["bottom"]),
                    "inside": float(margins["inside"]),
                    "outside": float(margins["outside"]),
                },
                "text_rules": dict(text_rules),
            })
            project.metadata["global_editorial_settings_v1"] = {
                "confirmed": True,
                "settings": {
                    "format_key": str(target.key),
                    "width_mm": float(target.width_mm),
                    "height_mm": float(target.height_mm),
                    "margin_top_mm": float(margins["top"]),
                    "margin_bottom_mm": float(margins["bottom"]),
                    "margin_inside_mm": float(margins["inside"]),
                    "margin_outside_mm": float(margins["outside"]),
                    "text_rules": dict(text_rules),
                },
            }
            project.metadata["book_import_state_reviewed"] = True
            project.touch()
            project.validate()

        self.session.execute(
            f"Format du Livre : {target.label}",
            action,
        )

    def _settings_format_ready(
        self,
        *,
        new_host,
        old_host,
        chapter_index: int,
        wanted_local_page: int,
        target,
        margins: dict,
        text_rules: dict,
        snapshot: dict,
    ) -> None:
        """Échange le Canvas uniquement APRÈS son render_complete."""
        if new_host is not getattr(self, "_settings_format_apply_host", None):
            return

        layout = getattr(self, "_phase2_chapter_layout", None)
        if layout is None:
            self._settings_abort_format_apply("Pagination globale indisponible.")
            return

        try:
            page_count = max(
                1,
                int((snapshot or {}).get("page_count") or 1),
            )
        except (TypeError, ValueError):
            page_count = 1

        wanted = max(1, min(int(wanted_local_page), page_count))

        # Le nouveau Canvas est encore sous l'ancien : on peut donc terminer
        # les validations sans exposer un état intermédiaire.
        try:
            self._settings_commit_book_format(target, margins, text_rules)
            layout.set_page_count(int(chapter_index), page_count)
            self._phase2_sync_page_count(layout.total_pages)
        except Exception as exc:
            self._settings_abort_format_apply(str(exc))
            return


        # Aucun page_changed ne doit agir tant que le nouveau host est caché.
        new_host._on_page_count_changed_callback = None
        try:
            new_host.go_to_page(wanted, smooth=False)
        except Exception:
            pass

        try:
            self._phase2_canvas_host = new_host
            self._phase2_active_chapter_index = int(chapter_index)
            self._phase2_loading_chapter_index = None
            self._phase2_switch_in_progress = False
            self._phase2_canvas_state = "ready"
            self._phase2_wanted_global_index = layout.global_index(
                int(chapter_index),
                wanted - 1,
            )
            self._phase2_displayed_global_index = self._phase2_wanted_global_index
        except Exception as exc:
            self._settings_abort_format_apply(str(exc))
            return

        # À partir d'ici le nouveau host devient l'hôte officiel Composition.
        new_host._on_page_count_changed_callback = self._phase2_on_page_count_changed
        self._settings_format_apply_host = None

        try:
            new_host.show_when_ready(
                x=0,
                y=0,
                relwidth=1,
                relheight=1,
            )
        except Exception as exc:
            # Cas très rare : on garde l'ancien hôte au lieu de le détruire.
            self._phase2_canvas_host = old_host
            self._settings_format_apply_host = new_host
            self._settings_abort_format_apply(str(exc))
            return

        if old_host is not None and old_host is not new_host:
            try:
                old_host.hide()
            except Exception:
                pass
            try:
                old_host.shutdown()
            except Exception:
                pass
            try:
                old_host.destroy()
            except Exception:
                pass

        # Les plans restent volontairement modifiés : les chapitres suivants
        # seront préchargés normalement par Composition avec le même format.
        self._settings_format_plan_changes = []
        self._settings_format_apply_busy = False
        self._settings_applied_text_rules = dict(text_rules)
        self._settings_format_notice = (
            "Format, marges et texte appliqués."
        )


        # Première validation seulement : rendre maintenant les commandes.
        self._settings_finish_unlock_ui()

    def _settings_apply_format_initial(self) -> None:
        """Applique le format sans toucher au cycle de démarrage de Phase 2."""
        if self._settings_format_apply_busy:
            return

        key = str(getattr(self, "_settings_format_key", "") or "")
        target = STANDARD_FORMATS_BY_KEY.get(key)
        if target is None:
            self._settings_format_notice = "Choisissez un format."
            self._composition_update_inspector_context()
            return

        fmt = self._settings_current_format()
        if fmt is None:
            self._settings_format_notice = "Format courant indisponible."
            self._composition_update_inspector_context()
            return

        try:
            margins = self._settings_margin_values(target)
            text_rules = self._settings_text_values()
        except Exception as exc:
            self._settings_format_notice = str(exc)
            self._composition_update_inspector_context()
            return

        try:
            same_format = (
                abs(float(fmt.width_mm) - float(target.width_mm)) <= 0.05
                and abs(float(fmt.height_mm) - float(target.height_mm)) <= 0.05
            )
            same_margins = (
                abs(float(fmt.margin_top_mm) - margins["top"]) <= 0.05
                and abs(float(fmt.margin_bottom_mm) - margins["bottom"]) <= 0.05
                and abs(float(fmt.margin_inside_mm) - margins["inside"]) <= 0.05
                and abs(float(fmt.margin_outside_mm) - margins["outside"]) <= 0.05
            )
            applied_text = getattr(self, "_settings_applied_text_rules", None)
            same_text = isinstance(applied_text, dict) and dict(applied_text) == dict(text_rules)
            same = bool(same_format and same_margins and same_text)
        except Exception:
            same = False

        if same:
            self._settings_format_notice = "Aucun changement à appliquer."
            if self._settings_ui_locked:
                self._settings_finish_unlock_ui()
            else:
                self._composition_update_inspector_context()
            return

        canvas = getattr(self, "_composition_editor_canvas", None)
        old_host = getattr(self, "_phase2_canvas_host", None)
        prepared = getattr(self, "_phase2_chapter_prepared", None)
        plans = list(getattr(self, "_phase2_chapter_plans", ()) or ())
        chapter_index = getattr(self, "_phase2_active_chapter_index", None)

        if (
            canvas is None
            or old_host is None
            or not bool(getattr(old_host, "ready", False))
            or prepared is None
            or chapter_index is None
            or not (0 <= int(chapter_index) < len(plans))
        ):
            self._settings_format_notice = (
                "Composition n'est pas encore prête pour changer le format."
            )
            self._composition_update_inspector_context()
            return

        try:
            wanted_local = max(
                1,
                int(getattr(old_host, "_active_page", 1) or 1),
            )
        except Exception:
            wanted_local = 1

        self._settings_format_apply_busy = True
        self._settings_format_notice = "Recomposition du format…"
        try:
            self._composition_update_inspector_context()
        except Exception:
            pass


        try:
            report = self._settings_patch_all_plans_for_format(
                target,
                margins,
                text_rules,
            )
        except Exception as exc:
            self._settings_format_apply_busy = False
            self._settings_format_notice = str(exc)
            self._composition_update_inspector_context()
            return

        # Le nouveau host est créé SOUS l'ancien. Si son rendu échoue,
        # l'utilisateur garde la page Composition validée intacte.
        new_host = CanvasEditorWebHost(
            canvas,
            project_root=PROJECT_ROOT,
            on_ready=lambda snapshot: self._settings_format_ready(
                new_host=new_host,
                old_host=old_host,
                chapter_index=int(chapter_index),
                wanted_local_page=wanted_local,
                target=target,
                margins=dict(margins),
                text_rules=dict(text_rules),
                snapshot=snapshot,
            ),
            on_failed=lambda failure: self._settings_abort_format_apply(
                str((failure or {}).get("message") or "Recomposition impossible.")
            ),
            on_editorial_choice=None,
            on_page_changed=None,
            on_page_count_changed=None,
            background=theme.WINDOW_DEEP,
        )
        self._settings_format_apply_host = new_host

        new_host.place(x=0, y=0, relwidth=1, relheight=1)
        try:
            new_host.lower()
            old_host.tk.call("raise", old_host._w)
        except Exception:
            pass

        try:
            new_host.load_document(
                plans[int(chapter_index)],
                CanvasLoadSession(prepared.canvas.contract),
            )
        except Exception as exc:
            self._settings_abort_format_apply(str(exc))
            return

        # Le rapport est purement informatif : aucun autre moteur n'est lancé.
        self._settings_format_notice = (
            "Recomposition… "
            f"{int(report.get('paragraphs', 0))} paragraphe(s) de corps."
        )
        try:
            self._composition_update_inspector_context()
        except Exception:
            pass

    def _settings_render_format_card(self, host) -> None:
        fmt = self._settings_current_format()

        card = tk.Frame(
            host,
            bg=theme.PANEL_SOFT,
            highlightthickness=1,
            highlightbackground=theme.BORDER_SOFT,
        )
        card.pack(
            fill="x",
            padx=12,
            pady=(6, 8),
        )

        tk.Label(
            card,
            text="1 — FORMAT",
            bg=theme.PANEL_SOFT,
            fg=theme.INK,
            font=(theme.FONT_UI, 9, "bold"),
            anchor="w",
        ).pack(
            fill="x",
            padx=10,
            pady=(9, 4),
        )

        if fmt is not None:
            current_text = (
                "Actuel : "
                f"{self._settings_mm(getattr(fmt, 'width_mm', None))}"
                " × "
                f"{self._settings_mm(getattr(fmt, 'height_mm', None))}"
                " mm"
            )
        else:
            current_text = "Actuel : format indisponible"

        tk.Label(
            card,
            text=current_text,
            bg=theme.PANEL_SOFT,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 8),
            anchor="w",
        ).pack(
            fill="x",
            padx=10,
            pady=(0, 6),
        )

        if self._settings_format_key is None:
            self._settings_format_key = (
                self._settings_initial_format_key()
            )

        if self._settings_format_label_var is None:
            self._settings_format_label_var = tk.StringVar(
                master=self,
                value=self._settings_format_display(
                    self._settings_format_key
                ),
            )
        else:
            self._settings_format_label_var.set(
                self._settings_format_display(
                    self._settings_format_key
                )
            )

        selector = tk.Menubutton(
            card,
            textvariable=self._settings_format_label_var,
            bg=theme.PANEL_ALT,
            fg=theme.INK,
            activebackground=theme.PANEL_SOFT,
            activeforeground=theme.WHITE,
            relief="flat",
            bd=0,
            anchor="w",
            justify="left",
            padx=8,
            pady=6,
            font=(theme.FONT_UI, 8),
            cursor="hand2",
        )
        selector.pack(
            fill="x",
            padx=10,
            pady=(0, 10),
        )

        menu = tk.Menu(
            selector,
            tearoff=False,
            bg=theme.PANEL_ALT,
            fg=theme.INK,
            activebackground=theme.ACCENT_DARK,
            activeforeground=theme.WHITE,
        )

        for family, items in formats_by_ui_family():
            submenu = tk.Menu(
                menu,
                tearoff=False,
                bg=theme.PANEL_ALT,
                fg=theme.INK,
                activebackground=theme.ACCENT_DARK,
                activeforeground=theme.WHITE,
            )
            for item in items:
                submenu.add_command(
                    label=item.display_label,
                    command=lambda selected=item.key: (
                        self._settings_choose_format(selected)
                    ),
                )
            menu.add_cascade(
                label=family,
                menu=submenu,
            )

        selector.configure(menu=menu)

    def _settings_panel_is_alive(self, host) -> bool:
        root = getattr(self, "_settings_panel_root", None)
        if root is None or int(getattr(self, "_settings_panel_host_id", 0) or 0) != id(host):
            return False
        try:
            return bool(root.winfo_exists()) and root.master is host
        except Exception:
            return False

    def _settings_refresh_panel_state(self) -> None:
        message = (
            "Réglages généraux du Livre · titres exclus des règles de texte."
            if bool(getattr(self, "_settings_ui_locked", False))
            else "parcours retiré disponible · la navigation manuelle reste active."
        )
        variable = getattr(self, "_settings_panel_message_var", None)
        if variable is not None:
            try:
                variable.set(message)
            except Exception:
                pass

        notice = str(getattr(self, "_settings_format_notice", "") or "")
        variable = getattr(self, "_settings_panel_notice_var", None)
        if variable is not None:
            try:
                variable.set(notice)
            except Exception:
                pass

        busy = bool(getattr(self, "_settings_format_apply_busy", False))
        action = getattr(self, "_settings_panel_action_button", None)
        if action is not None:
            try:
                action.configure(
                    text=(
                        "Recomposition…"
                        if busy
                        else (
                            "Appliquer et continuer"
                            if bool(getattr(self, "_settings_ui_locked", False))
                            else "Appliquer les réglages"
                        )
                    ),
                    state=(tk.DISABLED if busy else tk.NORMAL),
                    cursor=("arrow" if busy else "hand2"),
                )
            except Exception:
                pass

        try:
            self._composition_refresh_tool_tabs()
        except Exception:
            pass

    def _settings_build_persistent_panel(self, host) -> None:
        for child in host.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass

        self._settings_panel_host_id = id(host)
        self._settings_panel_rebuild_count = int(
            getattr(self, "_settings_panel_rebuild_count", 0) or 0
        ) + 1

        root = tk.Frame(host, bg=theme.PANEL)
        root.pack(fill="both", expand=True)
        self._settings_panel_root = root

        try:
            self._composition_set_inspector_tool_priority(True)
        except Exception:
            pass
        self._composition_refresh_tool_tabs()

        tk.Label(
            root, text="RÉGLAGES", bg=theme.PANEL, fg=theme.INK,
            font=(theme.FONT_UI, 10, "bold"), anchor="w",
        ).pack(fill="x", padx=14, pady=(14, 4))

        self._settings_render_format_card(root)
        self._settings_render_margin_card(root)
        self._settings_render_text_card(root)

        self._settings_panel_message_var = tk.StringVar(master=self, value="")
        tk.Label(
            root, textvariable=self._settings_panel_message_var,
            bg=theme.PANEL, fg=theme.MUTED, font=(theme.FONT_UI, 8),
            anchor="w", justify="left", wraplength=220,
        ).pack(fill="x", padx=14, pady=(0, 6))

        self._settings_panel_notice_var = tk.StringVar(master=self, value="")
        tk.Label(
            root, textvariable=self._settings_panel_notice_var,
            bg=theme.PANEL, fg=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 8, "bold"), anchor="w",
            justify="left", wraplength=220,
        ).pack(fill="x", padx=14, pady=(0, 6))

        action = self._button(
            root, "Appliquer les réglages", self._settings_apply_format_initial,
            compact=True, accent=True, enabled=True,
        )
        action.pack(fill="x", padx=14, pady=(4, 12))
        self._settings_panel_action_button = action
        self._settings_refresh_panel_state()

    def _composition_update_inspector_context(self) -> None:
        tool = str(getattr(self, "_stage_display_tool", "settings") or "settings")

        if tool == "survol":
            host = getattr(self, "_composition_inspector_context", None)
            if host is None:
                return
            self._survol_render_panel(host)
            return

        host = getattr(self, "_composition_inspector_context", None)
        if host is None:
            return

        if not self._settings_panel_is_alive(host):
            self._settings_build_persistent_panel(host)
            return

        # Un événement Canvas met à jour l'état, mais ne détruit jamais les
        # widgets : clics, menus et saisies restent stables.
        self._settings_refresh_panel_state()

    # Garde d'événements AVANT les bindtags existants du Treeview.
    # Les bindings de Structure restent intacts sous le garde.
    def _settings_install_tree_guard(self) -> None:
        navigator = getattr(self, "_composition_navigator", None)
        tree = getattr(navigator, "tree", None)
        if tree is None:
            return

        existing_tag = getattr(self, "_settings_tree_guard_tag", None)
        if existing_tag:
            try:
                if existing_tag in tree.bindtags():
                    return
            except Exception:
                pass

        guard_tag = f"TLSettingsGuard_{id(tree)}"
        self._settings_tree_guard_tag = guard_tag

        def stop_event(_event=None):
            return "break"

        for sequence in self._TREE_GUARD_SEQUENCES:
            try:
                tree.bind_class(guard_tag, sequence, stop_event)
            except Exception:
                pass

        try:
            tags = tuple(tree.bindtags())
            if guard_tag not in tags:
                tree.bindtags((guard_tag,) + tags)
        except Exception:
            pass

        try:
            tree.configure(takefocus=False, cursor="arrow")
        except Exception:
            pass

    def _settings_remove_tree_guard(self) -> None:
        navigator = getattr(self, "_composition_navigator", None)
        tree = getattr(navigator, "tree", None)
        guard_tag = getattr(self, "_settings_tree_guard_tag", None)

        if tree is None or not guard_tag:
            return

        try:
            tree.bindtags(
                tuple(
                    tag
                    for tag in tree.bindtags()
                    if str(tag) != str(guard_tag)
                )
            )
        except Exception:
            pass

        for sequence in self._TREE_GUARD_SEQUENCES:
            try:
                tree.unbind_class(guard_tag, sequence)
            except Exception:
                pass

        try:
            tree.configure(takefocus=True, cursor="")
        except Exception:
            pass

        self._settings_tree_guard_tag = None

    def _settings_plan_frame(self):
        navigator = getattr(self, "_composition_navigator", None)
        if navigator is None:
            return None
        try:
            return navigator.master.master
        except Exception:
            return None

    @staticmethod
    def _settings_walk_widgets(parent):
        if parent is None:
            return
        stack = [parent]
        while stack:
            widget = stack.pop()
            yield widget
            try:
                stack.extend(widget.winfo_children())
            except Exception:
                pass

    def _settings_disable_widget_once(self, widget) -> None:
        if widget is None:
            return

        for saved_widget, _state, _cursor in self._settings_disabled_widgets:
            if saved_widget is widget:
                return

        try:
            state = str(widget.cget("state"))
        except Exception:
            state = None

        try:
            cursor = str(widget.cget("cursor"))
        except Exception:
            cursor = None

        self._settings_disabled_widgets.append((widget, state, cursor))

        try:
            widget.configure(state=tk.DISABLED)
        except Exception:
            return

        try:
            widget.configure(cursor="arrow")
        except Exception:
            pass

    def _settings_lock_center_input(self) -> None:
        """Bloque l'entrée utilisateur du centre au niveau Win32.

        Le Canvas Tk est le parent natif de la zone où les WebView2 sont
        créés. Désactiver ce parent bloque souris + clavier pour ses enfants
        actuels et futurs, sans arrêter leur rendu, leur pagination ni les
        messages internes.

        Aucun JavaScript, aucun changement de mode Canvas Editor, aucun timer.
        """
        if sys.platform != "win32":
            return

        canvas = getattr(self, "_composition_editor_canvas", None)
        if canvas is None:
            return

        try:
            canvas.update_idletasks()
            hwnd = int(canvas.winfo_id())
        except Exception:
            return

        if not hwnd:
            return

        try:
            user32 = ctypes.windll.user32
            user32.IsWindow.argtypes = [wintypes.HWND]
            user32.IsWindow.restype = wintypes.BOOL
            user32.IsWindowEnabled.argtypes = [wintypes.HWND]
            user32.IsWindowEnabled.restype = wintypes.BOOL
            user32.EnableWindow.argtypes = [wintypes.HWND, wintypes.BOOL]
            user32.EnableWindow.restype = wintypes.BOOL

            if not bool(user32.IsWindow(hwnd)):
                return

            was_enabled = bool(user32.IsWindowEnabled(hwnd))

            # Écarte le focus clavier du centre avant sa désactivation.
            try:
                self.focus_set()
            except Exception:
                pass

            user32.EnableWindow(hwnd, False)

            self._settings_center_hwnd = hwnd
            self._settings_center_was_enabled = was_enabled
        except Exception:
            self._settings_center_hwnd = None
            self._settings_center_was_enabled = None

    def _settings_unlock_center_input(self) -> None:
        """Rend exactement l'état natif précédent au centre."""
        if sys.platform != "win32":
            return

        hwnd = getattr(self, "_settings_center_hwnd", None)
        was_enabled = getattr(self, "_settings_center_was_enabled", None)

        self._settings_center_hwnd = None
        self._settings_center_was_enabled = None

        if not hwnd:
            return

        try:
            user32 = ctypes.windll.user32
            user32.IsWindow.argtypes = [wintypes.HWND]
            user32.IsWindow.restype = wintypes.BOOL
            user32.EnableWindow.argtypes = [wintypes.HWND, wintypes.BOOL]
            user32.EnableWindow.restype = wintypes.BOOL

            if bool(user32.IsWindow(int(hwnd))):
                user32.EnableWindow(
                    int(hwnd),
                    bool(True if was_enabled is None else was_enabled),
                )
        except Exception:
            pass

    def _settings_apply_ui_lock(self) -> None:
        # Commande "Aller" dans la colonne Structure.
        plan = self._settings_plan_frame()
        jump_var = getattr(self, "_composition_jump_page_var", None)
        jump_var_name = str(jump_var) if jump_var is not None else ""

        for widget in self._settings_walk_widgets(plan):
            try:
                if isinstance(widget, tk.Button):
                    if str(widget.cget("text") or "") == "Aller":
                        self._settings_disable_widget_once(widget)
                        continue
            except Exception:
                pass

            try:
                if isinstance(widget, tk.Entry):
                    textvar = str(widget.cget("textvariable") or "")
                    if jump_var_name and textvar == jump_var_name:
                        self._settings_disable_widget_once(widget)
            except Exception:
                pass

        self._settings_install_tree_guard()

        self._settings_lock_center_input()

    def _settings_finish_unlock_ui(self) -> None:
        if not self._settings_ui_locked:
            return

        self._settings_ui_locked = False
        self._settings_remove_tree_guard()
        self._settings_unlock_center_input()

        saved = list(self._settings_disabled_widgets)
        self._settings_disabled_widgets = []
        for widget, state, cursor in saved:
            try:
                if state is not None:
                    widget.configure(state=state)
            except Exception:
                pass
            try:
                if cursor is not None:
                    widget.configure(cursor=cursor)
            except Exception:
                pass

        # Comme dans le Survol observation historique : une fois les réglages
        # initiaux validés, l'étape suivante devient directement Survol.
        self._stage_display_tool = "survol"
        self._composition_active_tool = "survol"

        try:
            self._composition_refresh_tool_tabs()
        except Exception:
            pass
        try:
            self._composition_update_inspector_context()
        except Exception:
            pass

