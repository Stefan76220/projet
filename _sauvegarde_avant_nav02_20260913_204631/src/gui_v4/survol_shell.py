from __future__ import annotations

"""Intégration du Survol guidé dans Composition.

Le Survol reste un parcours chronologique du Livre :
- toutes les vraies pages sont réellement affichées ;
- TomeLinea s'arrête seulement sur un repère qui demande une validation ;
- une règle étendue n'efface jamais les pages suivantes : elles sont survolées
  avec l'indication de la page où la décision a été prise ;
- la consultation des cas similaires est une parenthèse, puis le Survol reprend
  exactement à son curseur chronologique.
"""

import json
import tkinter as tk

from src.gui_v4 import theme
from src.gui_v4.editorial_shell import (
    TomeLineaV4Editorial,
    PROJECT_ROOT,
)
from src.gui_v4.canvas_editor_host import CanvasEditorWebHost
from src.v4.canvas_loading import CanvasLoadSession
from src.v4.editorial_structure_classifier import (
    apply_structure_choice,
)
from src.v4.structure_covers import (
    is_cover_face,
)
from src.v4.survol import (
    SurvolMarker,
    SURVOL_STATE_SCHEMA,
    build_survol_markers,
    evaluate_page_markers,
    future_similar_markers,
    normalize_survol_state,
)

class TomeLineaV4Survol(
    TomeLineaV4Editorial
):
    """Survol guidé de Composition — version consolidée."""

    def __init__(
        self,
        *,
        defer_show: bool = False,
    ) -> None:
        self._survol_running = False
        self._survol_started = False
        self._survol_after_id = None
        self._survol_message = (
            "TomeLinea parcourra le livre dans son ordre réel."
        )
        self._survol_current_marker: SurvolMarker | None = None
        self._survol_offer_marker: SurvolMarker | None = None
        self._survol_last_decision: str | None = None

        self._survol_preview_markers: list[
            SurvolMarker
        ] = []
        self._survol_preview_index = -1
        self._survol_preview_excluded_page_ids: set[
            str
        ] = set()
        self._survol_preview_return_page_id: str | None = None

        # Au premier passage dans Composition, Survol est l'outil actif.
        # Dès que l'utilisateur choisit lui-même un autre onglet, cette
        # priorité disparaît.
        self._survol_force_first_tool = False
        self._survol_user_left_tool = False

        self._survol_cache_signature = None
        self._survol_cached_order = None
        self._survol_cached_markers = None
        self._survol_buffer_reveal_after_id = None
        self._survol_buffer_swap_pending = False
        self._survol_buffer_target_local_page = None
        self._survol_buffer_target_global_index = None

        super().__init__(
            defer_show=defer_show,
        )

        # Pendant le Survol, Espace devient la commande de rythme la plus
        # naturelle : les yeux restent sur la page. Le clic restera disponible
        # pour sélectionner du texte ou une image dans la suite du travail.
        try:
            self.bind_all("<space>", self._survol_space_toggle, add="+")
        except Exception:
            pass

    def _survol_touch(self) -> None:
        project = getattr(
            getattr(
                self,
                "session",
                None,
            ),
            "project",
            None,
        )
        if project is None:
            return
        try:
            project.touch()
        except Exception:
            pass

    def _survol_reviewed_ids(
        self,
    ) -> set[str]:
        state = self._survol_state()
        return {
            str(value)
            for value in list(
                state.get(
                    "reviewed_marker_ids",
                    [],
                )
                or []
            )
        }

    def _survol_set_reviewed_ids(
        self,
        values,
    ) -> None:
        state = self._survol_state()
        state[
            "reviewed_marker_ids"
        ] = sorted(
            {
                str(value)
                for value in values
                if str(value)
            }
        )
        self._survol_touch()

    def _survol_mark_reviewed(
        self,
        marker: SurvolMarker,
    ) -> None:
        reviewed = (
            self._survol_reviewed_ids()
        )
        reviewed.add(
            marker.marker_id
        )
        self._survol_set_reviewed_ids(
            reviewed
        )

    def _phase239_begin_structure_review(
        self,
        canvas,
    ) -> None:
        """Ne pose plus de question modale avant Composition.

        Les frontières ambiguës restent dans l'analyse et seront présentées
        chronologiquement par le Survol.
        """

        self._phase239_review_queue = (
            self._phase239_ambiguous_structure_units()
        )
        self._phase239_review_current = None
        self._phase239_review_prompt_open = False

        project = getattr(
            getattr(
                self,
                "session",
                None,
            ),
            "project",
            None,
        )
        if project is not None:
            project.metadata[
                "survol_structure_pending"
            ] = bool(
                self._phase239_review_queue
            )
            self._survol_touch()

        layout = getattr(
            self,
            "_phase2_chapter_layout",
            None,
        )
        detection = getattr(
            self,
            "_phase2_chapter_detection",
            None,
        )

        if layout is not None:
            self._phase2_sync_page_count(
                layout.total_pages
            )

        # Prépare le trajet du Survol pendant que Composition est encore dans
        # sa phase de préparation. Le passage des pages n'aura donc pas à
        # reconstruire les repères à chaque étape.
        try:
            self._survol_prepare_route(force=True)
        except Exception:
            pass

        total_pages = (
            int(layout.total_pages)
            if layout is not None
            else 0
        )
        units = (
            len(
                getattr(
                    detection,
                    "chapters",
                    (),
                )
                or ()
            )
            if detection is not None
            else 0
        )

        self._phase2_show_overlay(
            canvas,
            "Composition prête",
            (
                f"{units} unité(s) — "
                f"{total_pages} page(s). "
                "Les points à confirmer seront "
                "présentés dans le Survol."
            ),
        )

        target = max(
            0,
            int(
                self._phase2_active_page_index()
                or 0
            ),
        )

        self.after(
            20,
            lambda: (
                self._phase2_request_global_page(
                    canvas,
                    target,
                    force=True,
                )
            ),
        )

    def _composition_mark_book_state_reviewed(self) -> None:
        """Après le Format, conduire naturellement vers les règles du texte."""
        super()._composition_mark_book_state_reviewed()
        self._composition_active_tool = "text"
        self._composition_book_state_open = False
        self._composition_constraints_open = False
        self._composition_pages_open = False
        try:
            self._composition_refresh_tool_tabs()
            self._composition_update_inspector_context()
        except Exception:
            pass

    def _composition_render_text_panel(self, host) -> None:
        """Conserve Texte puis propose le Survol comme étape suivante."""
        super()._composition_render_text_panel(host)

        state = self._survol_state()
        if bool(state.get("completed", False)) or bool(getattr(self, "_survol_started", False)):
            return

        tk.Frame(
            host,
            bg=theme.PAGE_BORDER,
            height=1,
        ).pack(fill="x", padx=18, pady=(12, 9))

        tk.Label(
            host,
            text="QUAND LES RÈGLES GÉNÉRALES SONT PRÊTES",
            bg=theme.PANEL,
            fg=theme.MUTED,
            wraplength=215,
            justify="left",
            font=(theme.FONT_UI, 8, "bold"),
        ).pack(anchor="w", padx=18, pady=(0, 5))

        self._button(
            host,
            "Commencer le Survol",
            self._survol_begin_from_text_rules,
            compact=True,
            accent=True,
        ).pack(fill="x", padx=18, pady=(0, 6))

    def _survol_begin_from_text_rules(self) -> None:
        self._composition_activate_tool("survol")
        self.after_idle(self._survol_start)

    def _composition_current_tool(self) -> str:
        """Étape actuelle : un seul onglet, Navigation."""
        return "survol"

    def _composition_activate_tool(self, tool: str) -> None:
        """Aucun autre outil tant que la navigation n'est pas validée."""
        self._composition_active_tool = "survol"
        self._survol_running = False
        self._survol_started = False
        try:
            self._composition_refresh_tool_tabs()
        except Exception:
            pass
        try:
            self._composition_update_inspector_context()
        except Exception:
            pass

    def _composition_build_tool_rail(self, parent):
        """Rail minimal : un seul onglet Navigation."""
        self._composition_active_tool = "survol"
        rail = tk.Frame(parent, bg=theme.PANEL_ALT, width=76)
        rail.pack_propagate(False)
        self._composition_tool_tabs = {}

        tab = tk.Canvas(
            rail,
            width=74,
            height=44,
            bg=theme.PANEL_SOFT,
            highlightthickness=0,
            bd=0,
            takefocus=False,
        )
        tab.pack(fill="x", padx=(1, 1), pady=(1, 0))
        text_id = tab.create_text(
            37,
            22,
            text="Navigation",
            width=68,
            justify="center",
            fill="#F3F5F5",
            font=(theme.FONT_UI, 8, "bold"),
        )
        self._composition_tool_tabs["survol"] = (tab, text_id)
        return rail

    def _composition_update_inspector_context(
        self,
    ) -> None:
        if (
            self._composition_current_tool()
            != "survol"
        ):
            super()._composition_update_inspector_context()
            return

        try:
            self._composition_refresh_image_quality_indicator()
        except Exception:
            pass

        host = getattr(
            self,
            "_composition_inspector_context",
            None,
        )
        if host is None:
            return

        for child in host.winfo_children():
            child.destroy()

        self._composition_geometry_vars = None

        try:
            self.after_idle(
                self._composition_finalize_inspector_context
            )
        except Exception:
            pass

        try:
            self._composition_set_inspector_tool_priority(
                True
            )
        except Exception:
            pass

        self._composition_refresh_tool_tabs()
        self._composition_render_survol_panel(
            host
        )

    def _survol_structure_page_ids(
        self,
    ) -> dict[str, str]:
        analysis = getattr(
            self,
            "_phase2_editorial_structure_analysis",
            None,
        )
        if not isinstance(
            analysis,
            dict,
        ):
            return {}

        try:
            internal_ids = list(
                self._phase2_internal_page_ids()
            )
        except Exception:
            internal_ids = []

        if not internal_ids:
            return {}

        result = {}

        for unit in list(
            analysis.get(
                "units",
                [],
            )
            or []
        ):
            if not isinstance(
                unit,
                dict,
            ):
                continue

            key = str(
                unit.get("key")
                or ""
            )
            if not key:
                continue

            try:
                start_page, _ = (
                    self._phase239_unit_page_range(
                        unit
                    )
                )
            except Exception:
                continue

            index = (
                int(start_page)
                - 1
            )
            if (
                0
                <= index
                < len(internal_ids)
            ):
                result[
                    key
                ] = str(
                    internal_ids[
                        index
                    ]
                )

        return result

    def _survol_cover_page_ids(
        self,
    ) -> set[str]:
        book = getattr(
            getattr(
                self,
                "session",
                None,
            ),
            "book",
            None,
        )
        if book is None:
            return set()

        result = set()

        for page_id in list(
            getattr(
                book,
                "page_order",
                (),
            )
            or ()
        ):
            page = getattr(
                book,
                "pages",
                {},
            ).get(page_id)

            if (
                page is not None
                and is_cover_face(
                    page
                )
            ):
                result.add(
                    str(page_id)
                )

        return result

    def _survol_page_number(
        self,
        page_id: str,
    ) -> int | None:
        order = self._survol_page_order()
        try:
            return (
                order.index(
                    str(page_id)
                )
                + 1
            )
        except ValueError:
            return None

    def _survol_rule_for(
        self,
        marker: SurvolMarker,
    ) -> dict | None:
        rules = self._survol_state().get(
            "rules",
            {},
        )
        if not isinstance(
            rules,
            dict,
        ):
            return None

        rule = rules.get(
            marker.family
        )
        if not isinstance(
            rule,
            dict,
        ):
            return None

        excluded = {
            str(value)
            for value in list(
                rule.get(
                    "excluded_page_ids",
                    [],
                )
                or []
            )
        }

        if marker.page_id in excluded:
            return None

        return rule

    def _survol_label(
        self,
        parent,
        text: str,
        *,
        strong: bool = False,
        accent: bool = False,
        muted: bool = False,
        pady=(0, 6),
    ):
        return tk.Label(
            parent,
            text=text,
            bg=theme.PANEL,
            fg=(
                theme.ACCENT_BRIGHT
                if accent
                else (
                    theme.MUTED
                    if muted
                    else theme.INK
                )
            ),
            wraplength=215,
            justify="left",
            anchor="w",
            font=(
                theme.FONT_UI,
                9,
                (
                    "bold"
                    if strong
                    else "normal"
                ),
            ),
        )

    def _survol_render_offer_actions(
        self,
        host,
        marker: SurvolMarker,
    ) -> None:
        candidates = (
            self._survol_similar_candidates(
                marker
            )
        )

        count = len(candidates)

        self._survol_label(
            host,
            (
                f"{count} cas similaire"
                f"{'s' if count != 1 else ''} "
                "détecté"
                f"{'s' if count != 1 else ''} "
                "plus loin dans le livre."
            ),
            strong=True,
        ).pack(
            fill="x",
            padx=18,
            pady=(3, 8),
        )

        reason = ""
        if isinstance(marker.metadata, dict):
            reason = str(marker.metadata.get("similarity_reason") or "").strip()
        if reason:
            self._survol_label(
                host,
                "Pourquoi similaires ? " + reason + ".",
                muted=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(0, 8),
            )

        self._survol_label(
            host,
            (
                "Vous pouvez les regarder avant "
                "d'étendre la décision. Le Survol "
                "reprendra ensuite exactement ici."
            ),
            muted=True,
        ).pack(
            fill="x",
            padx=18,
            pady=(0, 10),
        )

        if count:
            self._button(
                host,
                "Voir les cas similaires",
                self._survol_start_preview,
                compact=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(0, 5),
            )

            self._button(
                host,
                "Étendre cette décision",
                self._survol_extend_decision,
                compact=True,
                accent=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(0, 5),
            )

        self._button(
            host,
            "Ce cas seulement",
            self._survol_current_only,
            compact=True,
        ).pack(
            fill="x",
            padx=18,
            pady=(0, 5),
        )

    def _survol_render_preview_actions(
        self,
        host,
    ) -> None:
        total = len(
            self._survol_preview_markers
        )
        index = max(
            0,
            int(
                self._survol_preview_index
            ),
        )

        marker = (
            self._survol_preview_markers[
                index
            ]
            if (
                0
                <= index
                < total
            )
            else None
        )

        self._survol_label(
            host,
            (
                f"Exemple similaire "
                f"{index + 1} / {total}"
            ),
            strong=True,
            accent=True,
        ).pack(
            fill="x",
            padx=18,
            pady=(3, 7),
        )

        if marker is not None:
            self._survol_label(
                host,
                marker.title,
                strong=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(0, 5),
            )

        if (
            marker is not None
            and marker.page_id
            in self._survol_preview_excluded_page_ids
        ):
            self._survol_label(
                host,
                (
                    "Ce cas est marqué comme différent : "
                    "il ne recevra pas la règle étendue."
                ),
                muted=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(0, 8),
            )

        if index + 1 < total:
            self._button(
                host,
                "Cas suivant",
                self._survol_preview_next,
                compact=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(0, 5),
            )

        self._button(
            host,
            "Ce cas est différent",
            self._survol_preview_exclude_current,
            compact=True,
        ).pack(
            fill="x",
            padx=18,
            pady=(0, 5),
        )

        self._button(
            host,
            "Étendre la décision",
            self._survol_extend_decision,
            compact=True,
            accent=True,
        ).pack(
            fill="x",
            padx=18,
            pady=(0, 5),
        )

        self._button(
            host,
            "Retour au Survol",
            self._survol_return_from_preview,
            compact=True,
        ).pack(
            fill="x",
            padx=18,
            pady=(0, 5),
        )

    def _survol_space_toggle(self, event=None):
        """Le Survol automatique reste neutralisé pendant cette étape."""
        return "break"

    def _survol_cancel_after(
        self,
    ) -> None:
        after_id = getattr(
            self,
            "_survol_after_id",
            None,
        )
        if after_id is not None:
            try:
                self.after_cancel(
                    after_id
                )
            except Exception:
                pass
        self._survol_after_id = None

    def _survol_schedule(
        self,
        delay_ms: int,
        callback,
    ) -> None:
        self._survol_cancel_after()
        try:
            self._survol_after_id = (
                self.after(
                    int(delay_ms),
                    callback,
                )
            )
        except Exception:
            self._survol_after_id = None

    def _survol_refresh_panel(
        self,
    ) -> None:
        if (
            self._composition_current_tool()
            == "survol"
        ):
            self._composition_update_inspector_context()

    def _survol_start(self) -> None:
        """Le Survol automatique sera réintroduit après validation de la navigation."""
        self._survol_running = False
        self._survol_started = False

    def _survol_pause(
        self,
        *,
        refresh: bool = True,
        message: str | None = (
            "Survol en pause."
        ),
    ) -> None:
        self._survol_running = False
        self._survol_cancel_after()

        if message is not None:
            self._survol_message = (
                message
            )

        if refresh:
            self._survol_refresh_panel()

    def _survol_continue(
        self,
    ) -> None:
        if (
            self._survol_current_marker is not None
            or self._survol_offer_marker is not None
            or self._survol_preview_markers
        ):
            return

        self._survol_started = True
        self._survol_running = True
        self._survol_message = (
            "Survol en cours…"
        )
        self._survol_refresh_panel()
        self._survol_schedule(
            10,
            self._survol_step,
        )

    def _survol_advance_from(
        self,
        cursor: int,
        *,
        delay_ms: int,
    ) -> None:
        def advance():
            if not self._survol_running:
                return

            state = self._survol_state()
            state[
                "cursor"
            ] = int(cursor) + 1
            self._survol_touch()
            self._survol_step()

        self._survol_schedule(
            delay_ms,
            advance,
        )

    def _survol_apply_structure_decision(
        self,
        marker: SurvolMarker,
        decision: str,
        *,
        sync: bool = True,
    ) -> None:
        if (
            marker.kind
            != "structure"
            or not marker.unit_key
            or decision
            not in {
                "create",
                "merge",
            }
        ):
            return

        analysis = getattr(
            self,
            "_phase2_editorial_structure_analysis",
            None,
        )
        if not isinstance(
            analysis,
            dict,
        ):
            return

        unit = (
            marker.metadata.get(
                "unit",
                {},
            )
            if isinstance(
                marker.metadata,
                dict,
            )
            else {}
        )
        if not isinstance(
            unit,
            dict,
        ):
            unit = {}

        title = str(
            unit.get("title")
            or unit.get("editorial_label")
            or "Section"
        ).strip() or "Section"

        zone = str(
            unit.get("zone")
            or "bodymatter"
        )

        create = (
            decision
            == "create"
        )

        analysis = apply_structure_choice(
            analysis,
            marker.unit_key,
            create_section=create,
            name=(
                title
                if create
                else None
            ),
        )

        self._phase2_editorial_structure_analysis = (
            analysis
        )

        project = getattr(
            getattr(
                self,
                "session",
                None,
            ),
            "project",
            None,
        )

        if project is not None:
            stored = (
                project.metadata.get(
                    "editorial_structure_choices"
                )
            )
            if not isinstance(
                stored,
                dict,
            ):
                stored = {}
            else:
                stored = {
                    str(key): dict(value)
                    for key, value in stored.items()
                    if isinstance(
                        value,
                        dict,
                    )
                }

            if create:
                stored[
                    marker.unit_key
                ] = {
                    "decision": "create",
                    "name": title,
                    "zone": zone,
                }
            else:
                stored[
                    marker.unit_key
                ] = {
                    "decision": "merge",
                    "zone": zone,
                }

            project.metadata[
                "editorial_structure_choices"
            ] = stored
            project.metadata[
                "editorial_structure_last_summary"
            ] = dict(
                analysis.get(
                    "summary",
                    {},
                )
                or {}
            )
            self._survol_touch()

        if sync:
            layout = getattr(
                self,
                "_phase2_chapter_layout",
                None,
            )
            if layout is not None:
                try:
                    self._phase2_sync_page_count(
                        layout.total_pages
                    )
                except Exception:
                    pass

    def _survol_validate_marker(
        self,
        decision: str,
    ) -> None:
        marker = (
            self._survol_current_marker
        )
        if marker is None:
            return

        decision = str(
            decision
            or "accept"
        )

        if decision in {
            "create",
            "merge",
        }:
            self._survol_apply_structure_decision(
                marker,
                decision,
            )

        self._survol_last_decision = (
            decision
        )
        self._survol_mark_reviewed(
            marker
        )
        self._survol_current_marker = None

        candidates = (
            self._survol_similar_candidates(
                marker
            )
        )

        if candidates:
            self._survol_offer_marker = (
                marker
            )
            self._survol_running = False
            self._survol_message = (
                "Décision prise ici. "
                f"{len(candidates)} cas similaire"
                f"{'s' if len(candidates) != 1 else ''} "
                "existent plus loin."
            )
            self._survol_refresh_panel()
            return

        self._survol_offer_marker = None
        self._survol_resume_after_current_page()

    def _survol_similar_candidates(
        self,
        marker: SurvolMarker,
    ) -> list[SurvolMarker]:
        return future_similar_markers(
            self._survol_markers(),
            self._survol_page_order(),
            marker,
            after_page_id=marker.page_id,
            reviewed_marker_ids=(
                self._survol_reviewed_ids()
            ),
            excluded_page_ids=(
                self._survol_preview_excluded_page_ids
            ),
        )

    def _survol_resume_after_current_page(
        self,
    ) -> None:
        order = self._survol_page_order()
        state = self._survol_state()

        try:
            current = order.index(
                str(
                    getattr(
                        getattr(
                            self,
                            "session",
                            None,
                        ),
                        "active_page_id",
                        "",
                    )
                    or ""
                )
            )
        except ValueError:
            current = max(
                0,
                int(
                    state.get(
                        "cursor",
                        0,
                    )
                    or 0
                ),
            )

        state[
            "cursor"
        ] = current + 1
        self._survol_touch()

        self._survol_running = True
        self._survol_message = (
            "Survol en cours…"
        )
        self._survol_refresh_panel()
        self._survol_schedule(
            120,
            self._survol_step,
        )

    def _survol_current_only(
        self,
    ) -> None:
        self._survol_offer_marker = None
        self._survol_preview_excluded_page_ids = set()
        self._survol_resume_after_current_page()

    def _survol_start_preview(
        self,
    ) -> None:
        marker = (
            self._survol_offer_marker
        )
        if marker is None:
            return

        candidates = (
            self._survol_similar_candidates(
                marker
            )
        )
        if not candidates:
            return

        self._survol_running = False
        self._survol_preview_markers = (
            candidates
        )
        self._survol_preview_index = 0
        self._survol_preview_excluded_page_ids = set()
        self._survol_preview_return_page_id = (
            marker.page_id
        )

        self._survol_show_preview_current()

    def _survol_show_preview_current(
        self,
    ) -> None:
        if not self._survol_preview_markers:
            return

        index = max(
            0,
            min(
                int(
                    self._survol_preview_index
                ),
                len(
                    self._survol_preview_markers
                )
                - 1,
            ),
        )
        self._survol_preview_index = (
            index
        )

        marker = (
            self._survol_preview_markers[
                index
            ]
        )

        self._survol_message = (
            "Consultation volontaire d'un "
            "cas similaire. Le curseur du "
            "Survol n'a pas bougé."
        )

        try:
            self._activate_page(
                marker.page_id
            )
        except Exception:
            pass

        self._survol_refresh_panel()

    def _survol_preview_next(
        self,
    ) -> None:
        if not self._survol_preview_markers:
            return

        if (
            self._survol_preview_index + 1
            >= len(
                self._survol_preview_markers
            )
        ):
            self._survol_return_from_preview()
            return

        self._survol_preview_index += 1
        self._survol_show_preview_current()

    def _survol_preview_exclude_current(
        self,
    ) -> None:
        if not self._survol_preview_markers:
            return

        marker = (
            self._survol_preview_markers[
                self._survol_preview_index
            ]
        )
        self._survol_preview_excluded_page_ids.add(
            marker.page_id
        )
        self._survol_message = (
            "Ce cas restera une exception : "
            "la règle étendue ne lui sera pas appliquée."
        )

        if (
            self._survol_preview_index + 1
            < len(
                self._survol_preview_markers
            )
        ):
            self._survol_preview_index += 1
            self._survol_show_preview_current()
        else:
            self._survol_refresh_panel()

    def _survol_return_from_preview(
        self,
    ) -> None:
        return_page_id = (
            self._survol_preview_return_page_id
        )

        self._survol_preview_markers = []
        self._survol_preview_index = -1
        self._survol_preview_return_page_id = None
        self._survol_message = (
            "Retour au point où le Survol "
            "s'était arrêté."
        )

        if return_page_id:
            try:
                self._activate_page(
                    return_page_id
                )
            except Exception:
                pass

        self._survol_refresh_panel()

    def _survol_extend_decision(
        self,
    ) -> None:
        marker = (
            self._survol_offer_marker
        )
        if marker is None:
            return

        decision = str(
            self._survol_last_decision
            or "accept"
        )

        candidates = (
            self._survol_similar_candidates(
                marker
            )
        )

        excluded = set(
            self._survol_preview_excluded_page_ids
        )

        state = self._survol_state()
        rules = state.get(
            "rules",
            {},
        )
        if not isinstance(
            rules,
            dict,
        ):
            rules = {}

        anchor_number = (
            self._survol_page_number(
                marker.page_id
            )
        )

        rules[
            marker.family
        ] = {
            "anchor_page_id": marker.page_id,
            "anchor_page_number": anchor_number,
            "decision": decision,
            "excluded_page_ids": sorted(
                excluded
            ),
        }

        state[
            "rules"
        ] = rules
        self._survol_touch()

        return_page_id = marker.page_id

        self._survol_preview_markers = []
        self._survol_preview_index = -1
        self._survol_preview_return_page_id = None
        self._survol_preview_excluded_page_ids = set()
        self._survol_offer_marker = None

        self._survol_message = (
            "Règle étendue. Les cas similaires "
            "seront quand même réellement survolés."
        )

        try:
            self._activate_page(
                return_page_id
            )
        except Exception:
            pass

        order = self._survol_page_order()
        state = self._survol_state()
        try:
            anchor_index = order.index(
                return_page_id
            )
        except ValueError:
            anchor_index = int(
                state.get(
                    "cursor",
                    0,
                )
                or 0
            )

        # L'extension est une décision importante : TomeLinea revient sur la
        # page qui l'a déclenchée et y reste. La reprise commencera à la page
        # suivante seulement lorsque l'utilisateur le demandera.
        state[
            "cursor"
        ] = anchor_index + 1
        self._survol_touch()

        self._survol_running = False
        self._survol_started = True
        self._survol_message = (
            "Règle étendue. Vous êtes revenu sur la page qui a déclenché "
            "la décision. Espace pour reprendre à la page suivante."
        )
        self._survol_refresh_panel()

    def _survol_prepare_route(self, *, force: bool = False) -> None:
        """Prépare le parcours sur l'état RÉEL et courant du Livre.

        La 2.39E mettait le parcours en cache avec seulement ``id(book)``.
        Or la pagination Canvas ajoute ensuite des pages dans le même objet Book :
        un trajet préparé à 26 pages restait donc bloqué à 26 alors que le Livre
        final en contenait 53. Les repères pouvaient être figés trop tôt de la même
        manière.

        Ici le cache dépend de la liste réelle des pages, de la correspondance des
        unités éditoriales vers les pages et de l'analyse éditoriale elle-même.
        """

        book = getattr(getattr(self, "session", None), "book", None)
        if book is None:
            self._survol_cached_order = []
            self._survol_cached_markers = {}
            self._survol_cache_signature = None
            return

        order = tuple(
            str(page_id)
            for page_id in list(getattr(book, "page_order", ()) or ())
        )

        analysis = getattr(
            self,
            "_phase2_editorial_structure_analysis",
            None,
        )
        if not isinstance(analysis, dict):
            analysis = {}

        structure_page_ids = self._survol_structure_page_ids()

        analysis_signature = []
        for unit in list(analysis.get("units") or []):
            if not isinstance(unit, dict):
                continue
            candidates = unit.get("candidates")
            first_candidate = ""
            if isinstance(candidates, list) and candidates and isinstance(candidates[0], dict):
                first_candidate = str(candidates[0].get("type") or "")
            analysis_signature.append((
                str(unit.get("key") or ""),
                str(unit.get("editorial_type") or ""),
                str(unit.get("editorial_label") or ""),
                str(unit.get("decision") or ""),
                bool(unit.get("ask_user")),
                str(unit.get("style_id") or ""),
                str(unit.get("detected_by") or ""),
                str(unit.get("zone") or ""),
                int(unit.get("confidence", 0) or 0),
                first_candidate,
                str(structure_page_ids.get(str(unit.get("key") or "")) or ""),
            ))

        layout = getattr(self, "_phase2_chapter_layout", None)
        page_counts = tuple(
            int(value)
            for value in list(getattr(layout, "page_counts", ()) or ())
        )

        signature = (
            id(book),
            order,
            tuple(sorted((str(k), str(v)) for k, v in structure_page_ids.items())),
            tuple(analysis_signature),
            page_counts,
        )

        if (
            not force
            and getattr(self, "_survol_cache_signature", None) == signature
            and isinstance(getattr(self, "_survol_cached_order", None), list)
            and isinstance(getattr(self, "_survol_cached_markers", None), dict)
        ):
            return

        markers = build_survol_markers(
            book,
            analysis,
            structure_page_ids,
            cover_page_ids=self._survol_cover_page_ids(),
        )

        self._survol_cached_order = list(order)
        self._survol_cached_markers = markers
        self._survol_cache_signature = signature
        self._survol_cache_book_id = id(book)

        state = self._survol_state()
        try:
            cursor = max(0, int(state.get("cursor", 0) or 0))
        except (TypeError, ValueError):
            cursor = 0

        total = len(order)
        if cursor > total:
            state["cursor"] = total
            cursor = total

        # Cas observé : un ancien trajet avait été déclaré terminé à 26/26 alors
        # que Canvas venait de porter le Livre à 53 pages. Dès qu'un trajet grandit,
        # l'état "terminé" devient automatiquement faux et le Survol reprend à
        # l'endroit où il s'était arrêté.
        if bool(state.get("completed", False)) and cursor < total:
            state["completed"] = False
            if cursor >= total and total:
                state["cursor"] = total - 1
            self._survol_message = (
                "Le Livre contient maintenant davantage de pages. "
                "Le Survol reprend là où il s'était arrêté."
            )
            self._survol_touch()

    def _survol_page_order(self) -> list[str]:
        self._survol_prepare_route()
        return list(getattr(self, "_survol_cached_order", []) or [])

    def _survol_markers(self) -> dict[str, list[SurvolMarker]]:
        self._survol_prepare_route()
        value = getattr(self, "_survol_cached_markers", {})
        return value if isinstance(value, dict) else {}

    def _survol_structure_reason_text(self, marker: SurvolMarker) -> str:
        unit = marker.metadata.get("unit", {}) if isinstance(marker.metadata, dict) else {}
        if not isinstance(unit, dict):
            unit = {}

        reasons = [
            str(value).strip().casefold()
            for value in list(unit.get("reasons", ()) or ())
            if str(value).strip()
        ]

        friendly = []
        mapping = (
            ("intitulé reconnu", "son intitulé correspond à un type connu du livre"),
            ("forme de titre reconnue", "la forme de son titre correspond à une vraie division"),
            ("contenu caractéristique", "son contenu correspond à ce type de division"),
            ("niveau de titre", "son niveau de titre marque une rupture dans la hiérarchie"),
            ("position cohérente dans le livre", "sa position est cohérente avec cette place dans le livre"),
            ("présent dans le sommaire", "ce titre apparaît aussi dans le sommaire"),
            ("série cohérente de chapitres non numérotés", "il appartient à une série de titres construits de la même façon"),
        )
        for needle, explanation in mapping:
            if any(needle in reason for reason in reasons) and explanation not in friendly:
                friendly.append(explanation)

        style = str(unit.get("style_id") or "").strip()
        if not friendly and style:
            friendly.append(f"le document l'identifie avec le style « {style} »")

        zone = str(unit.get("zone") or "").strip()
        if not friendly and zone:
            zone_text = {
                "frontmatter": "les pages liminaires",
                "bodymatter": "le corps du livre",
                "backmatter": "la fin d'ouvrage",
            }.get(zone, zone)
            friendly.append(f"sa position correspond à {zone_text}")

        if not friendly:
            friendly.append("plusieurs indices de structure convergent à cet endroit")

        if len(friendly) == 1:
            reason_text = friendly[0]
        else:
            reason_text = ", ".join(friendly[:-1]) + " et " + friendly[-1]

        if marker.doubtful:
            return (
                "TomeLinea voit ici une vraie rupture, mais les indices ne sont "
                "pas assez sûrs pour la classer seul. Il s'appuie notamment sur "
                + reason_text
                + "."
            )

        label = str(unit.get("editorial_label") or marker.title or "cette division").strip()
        return (
            f"TomeLinea propose « {label} » parce que {reason_text}. "
            "Vous validez donc la raison de cette division, pas seulement son existence."
        )

    def _survol_marker_reason_text(self, marker: SurvolMarker) -> str:
        if marker.kind == "structure":
            return self._survol_structure_reason_text(marker)
        if marker.kind == "image":
            return (
                "TomeLinea s'arrête parce que cette page contient une image qui "
                "peut modifier la composition ou devenir une règle de placement."
            )
        if marker.kind == "document":
            return (
                "TomeLinea s'arrête parce qu'un document inséré peut nécessiter "
                "une règle de placement différente du texte courant."
            )
        if marker.kind == "table":
            return (
                "TomeLinea s'arrête parce qu'un tableau peut imposer une règle "
                "de coupure ou de placement particulière."
            )
        return "TomeLinea a rencontré ici un élément qui mérite une décision humaine."

    def _phase2_show_overlay(self, canvas, title, message, *args, **kwargs):
        """Masque les transitions techniques entre unités pendant le Survol."""

        normalized = str(title or "").strip().casefold()
        technical_transition = (
            "changement de chapitre" in normalized
            or "ouverture de l’unité" in normalized
            or "ouverture de l'unité" in normalized
        )
        try:
            survol_active = self._composition_current_tool() == "survol"
        except Exception:
            survol_active = False

        if survol_active and technical_transition:
            # Le moteur par chapitre continue son travail, mais l'utilisateur
            # n'est plus sollicité par un panneau de chargement à chaque unité.
            try:
                self._phase2_destroy_overlay()
            except Exception:
                pass
            return None

        return super()._phase2_show_overlay(
            canvas,
            title,
            message,
            *args,
            **kwargs,
        )

    def _composition_render_survol_panel(self, host) -> None:
        """Panneau minimal : aucune décision éditoriale à cette étape."""
        active_host = getattr(self, "_phase2_canvas_host", None)
        if active_host is not None:
            self._survol_install_stable_navigation(active_host)

        tk.Label(
            host,
            text="NAVIGATION DU LIVRE",
            bg=theme.PANEL,
            fg=theme.TEXT,
            font=(theme.FONT_UI, 9, "bold"),
            anchor="w",
        ).pack(fill="x", padx=14, pady=(14, 5))

        tk.Label(
            host,
            text=(
                "Parcours manuel uniquement.\n"
                "Utilisez Précédente et Suivante au-dessus de la page."
            ),
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 8),
            justify="left",
            anchor="w",
            wraplength=220,
        ).pack(fill="x", padx=14, pady=(0, 8))

        try:
            self.after_idle(self._survol_preload_following_chapter)
        except Exception:
            pass

    def _survol_render_marker_actions(self, host, marker: SurvolMarker) -> None:
        """Un seul message, mais il explique enfin la raison de l'arrêt."""

        card = tk.Frame(
            host,
            bg=theme.PANEL_ALT,
            highlightthickness=1,
            highlightbackground=theme.PAGE_BORDER,
        )
        card.pack(fill="x", padx=14, pady=(2, 8))

        heading = "À CONFIRMER" if marker.doubtful else "PROPOSITION TOMELINEA"
        tk.Label(
            card,
            text=heading,
            bg=theme.PANEL_ALT,
            fg=(theme.WARNING if marker.doubtful else theme.ACCENT_BRIGHT),
            font=(theme.FONT_UI, 8, "bold"),
        ).pack(anchor="w", padx=10, pady=(9, 3))

        tk.Label(
            card,
            text=marker.title,
            bg=theme.PANEL_ALT,
            fg=theme.INK,
            wraplength=200,
            justify="left",
            anchor="w",
            font=(theme.FONT_UI, 10, "bold"),
        ).pack(fill="x", padx=10, pady=(0, 7))

        tk.Label(
            card,
            text="Pourquoi ?",
            bg=theme.PANEL_ALT,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 8, "bold"),
        ).pack(anchor="w", padx=10, pady=(0, 2))

        tk.Label(
            card,
            text=self._survol_marker_reason_text(marker),
            bg=theme.PANEL_ALT,
            fg=theme.INK,
            wraplength=200,
            justify="left",
            anchor="w",
            font=(theme.FONT_UI, 8),
        ).pack(fill="x", padx=10, pady=(0, 10))

        if marker.kind == "structure":
            if marker.doubtful:
                self._button(
                    host,
                    "Créer cette division",
                    lambda: self._survol_validate_marker("create"),
                    compact=True,
                    accent=True,
                ).pack(fill="x", padx=18, pady=(0, 5))
                self._button(
                    host,
                    "Rattacher à la précédente",
                    lambda: self._survol_validate_marker("merge"),
                    compact=True,
                ).pack(fill="x", padx=18, pady=(0, 5))
            else:
                self._button(
                    host,
                    "Valider cette division",
                    lambda: self._survol_validate_marker("accept"),
                    compact=True,
                    accent=True,
                ).pack(fill="x", padx=18, pady=(0, 5))
                self._button(
                    host,
                    "Cette division n'a pas lieu d'être",
                    lambda: self._survol_validate_marker("merge"),
                    compact=True,
                ).pack(fill="x", padx=18, pady=(0, 5))
        else:
            self._button(
                host,
                "Valider",
                lambda: self._survol_validate_marker("accept"),
                compact=True,
                accent=True,
            ).pack(fill="x", padx=18, pady=(0, 5))

    _SURVOL_NORMAL_DELAY_MS = 1700

    _SURVOL_RULE_DELAY_MS = 2200

    _SURVOL_READY_POLL_MS = 75

    _SURVOL_READY_MAX_ATTEMPTS = 200

    def _survol_state(self) -> dict:
        """État v2 : aucune ancienne extension ne peut avaler les arrêts."""

        project = getattr(getattr(self, "session", None), "project", None)
        if project is None:
            return normalize_survol_state(None)

        raw = project.metadata.get("survol_v1")
        normalized = normalize_survol_state(raw if isinstance(raw, dict) else None)
        if raw != normalized:
            project.metadata["survol_v1"] = normalized
            try:
                project.touch()
            except Exception:
                pass
        return project.metadata["survol_v1"]

    def _survol_rules(self) -> dict:
        state = self._survol_state()
        rules = state.get("rules", {})
        return rules if isinstance(rules, dict) else {}

    def _survol_set_cursor_to_page(self, page_id: str) -> None:
        order = self._survol_page_order()
        try:
            index = order.index(str(page_id))
        except ValueError:
            return
        state = self._survol_state()
        state["cursor"] = index
        state["completed"] = False
        self._survol_touch()

    def _survol_page_ready(self, page_id: str) -> bool:
        """Vrai seulement quand la page demandée est réellement affichable."""

        if str(getattr(getattr(self, "session", None), "active_page_id", "") or "") != str(page_id):
            return False

        try:
            internal_ids = set(str(value) for value in self._phase2_internal_page_ids())
        except Exception:
            internal_ids = set()

        if str(page_id) not in internal_ids:
            return True

        if bool(getattr(self, "_phase2_switch_in_progress", False)):
            return False

        host = getattr(self, "_phase2_canvas_host", None)
        if host is None or not bool(getattr(host, "ready", False)):
            return False

        return str(getattr(self, "_phase2_canvas_state", "") or "") == "ready"

    def _survol_wait_then(
        self,
        page_id: str,
        callback,
        *,
        attempt: int = 0,
    ) -> None:
        if not bool(getattr(self, "_survol_running", False)):
            return

        if self._survol_page_ready(page_id):
            callback()
            return

        if int(attempt) >= int(self._SURVOL_READY_MAX_ATTEMPTS):
            # Ne jamais s'arrêter silencieusement : si le moteur n'a réellement
            # pas rendu la page après 15 s, le Survol reste explicitement en pause.
            self._survol_pause(
                message=(
                    "Survol suspendu : cette page n'a pas pu être affichée dans "
                    "le délai normal. TomeLinea conserve votre position."
                )
            )
            return

        self._survol_schedule(
            self._SURVOL_READY_POLL_MS,
            lambda: self._survol_wait_then(
                page_id,
                callback,
                attempt=int(attempt) + 1,
            ),
        )

    def _survol_step(self) -> None:
        """Un seul curseur ; une règle n'empêche jamais un nouveau repère d'arrêter."""

        self._survol_after_id = None
        if not bool(getattr(self, "_survol_running", False)):
            return

        order = self._survol_page_order()
        if not order:
            self._survol_pause(message="Aucune page à survoler.")
            return

        state = self._survol_state()
        cursor = max(0, int(state.get("cursor", 0) or 0))

        if cursor >= len(order):
            state["completed"] = True
            state["cursor"] = len(order)
            self._survol_running = False
            self._survol_message = "Survol terminé."
            self._survol_touch()
            self._survol_refresh_panel()
            return

        page_id = str(order[cursor])
        markers = list(self._survol_markers().get(page_id, ()) or ())
        reviewed_before = self._survol_reviewed_ids()
        current_marker, applied_rule, applied_rule_marker, reviewed_after = evaluate_page_markers(
            markers,
            reviewed_before,
            self._survol_rules(),
        )

        self._survol_current_marker = current_marker
        self._survol_offer_marker = None

        if current_marker is not None:
            self._survol_running = False
            self._survol_message = "TomeLinea a besoin de votre décision sur cette page."
        elif applied_rule is not None:
            anchor = applied_rule.get("anchor_page_number") or "?"
            self._survol_message = f"Règle déjà définie à partir de la page {anchor}."
        else:
            self._survol_message = "Survol en cours…"

        # Cette cible reste l'autorité jusqu'à ce que Canvas ait confirmé la page.
        self._survol_expected_page_id = page_id
        self._survol_expected_global_index = cursor
        try:
            import time as _time
            self._survol_programmatic_until = _time.monotonic() + 2.5
        except Exception:
            self._survol_programmatic_until = 0.0

        self._survol_internal_navigation = True
        try:
            self._activate_page(page_id)
        except Exception:
            try:
                self.session.set_active_page(page_id)
                self._composition_update_editor()
            except Exception:
                pass
        finally:
            self._survol_internal_navigation = False

        # Prépare déjà l'unité suivante sous la page courante. La page affichée
        # reste donc stable pendant la construction du chapitre suivant.
        self._survol_preload_following_chapter()

        if applied_rule is not None and applied_rule_marker is not None:
            decision = str(applied_rule.get("decision", "accept") or "accept")
            if applied_rule_marker.kind == "structure" and decision in {"create", "merge"}:
                self._survol_apply_structure_decision(applied_rule_marker, decision)

        if reviewed_after != reviewed_before:
            self._survol_set_reviewed_ids(reviewed_after)

        self._survol_refresh_panel()

        if current_marker is not None:
            return

        delay = self._SURVOL_RULE_DELAY_MS if applied_rule is not None else self._SURVOL_NORMAL_DELAY_MS
        self._survol_wait_then(
            page_id,
            lambda: self._survol_advance_from(cursor, delay_ms=delay),
        )

    def _activate_page(
        self,
        page_id: str,
        *,
        preserve_page_selection: bool = False,
    ) -> None:
        internal = bool(getattr(self, "_survol_internal_navigation", False))
        running = bool(getattr(self, "_survol_running", False))
        expected = str(getattr(self, "_survol_expected_page_id", "") or "")
        target = str(page_id or "")

        if running and not internal and expected and target != expected:
            self._survol_set_cursor_to_page(target)
            self._survol_pause(
                refresh=False,
                message=(
                    "Survol en pause — navigation manuelle. Continuer repartira "
                    "de la page que vous avez choisie."
                ),
            )

        return super()._activate_page(
            page_id,
            preserve_page_selection=preserve_page_selection,
        )

    def _phase2_on_page_changed(self, event: dict) -> None:
        """Navigation manuelle stable et recentrée sur chaque page."""
        result = super()._phase2_on_page_changed(event)

        host = getattr(self, "_phase2_canvas_host", None)
        if host is not None:
            self._survol_install_stable_navigation(host)

        if not bool(getattr(self, "_navigation_only_first_page_done", False)):
            try:
                self.after_idle(self._navigation_only_open_first_book_page)
            except Exception:
                self._navigation_only_open_first_book_page()

        try:
            self.after_idle(self._survol_preload_following_chapter)
        except Exception:
            pass

        return result

    def _survol_destroy_host_instance(self, host) -> None:
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

    def _survol_dispose_buffer(self) -> None:
        reveal_after = getattr(self, "_survol_buffer_reveal_after_id", None)
        if reveal_after is not None:
            try:
                self.after_cancel(reveal_after)
            except Exception:
                pass
        self._survol_buffer_reveal_after_id = None
        self._survol_buffer_swap_pending = False
        self._survol_buffer_target_local_page = None
        self._survol_buffer_target_global_index = None

        host = getattr(self, "_survol_buffer_host", None)
        if host is not None and host is not getattr(self, "_phase2_canvas_host", None):
            self._survol_destroy_host_instance(host)
        self._survol_buffer_host = None
        self._survol_buffer_chapter_index = None
        self._survol_buffer_ready_flag = False
        self._survol_buffer_requested_global_index = None

    def _survol_install_stable_navigation(self, host) -> None:
        """Navigation embarquée sans phase visible « transform:none ».

        Le moteur d'origine mesure la nouvelle page après avoir temporairement
        supprimé la transformation du document. Sur un WebView visible, cette
        seule frame suffit à donner l'impression que la page part à gauche.
        Cette version calcule la géométrie native par inversion de la matrice
        actuelle et applique directement la nouvelle transformation.
        """
        web = getattr(host, "_web", None)
        if web is None:
            return

        script = r"""
(() => {
  if (window.__TL_SURVOL_STABLE_NAV__) return true;
  window.__TL_SURVOL_STABLE_NAV__ = true;

  window.tomeLineaCanvasGoToPage = function(pageNo, behavior = 'auto') {
    const pages = [...document.querySelectorAll('.ce-page-container canvas[data-index]')];
    const targetNo = Math.max(1, Math.min(Number(pageNo) || 1, pages.length));
    const node = pages[targetNo - 1];
    const rootNode = document.getElementById('document');
    if (!node || !rootNode) return {ok:false, pageNo:targetNo, pageCount:pages.length};

    const rect = node.getBoundingClientRect();
    if (!(rect.width > 0 && rect.height > 0)) {
      return {ok:false, pageNo:targetNo, pageCount:pages.length};
    }

    const css = getComputedStyle(rootNode).transform;
    let scale0 = 1, tx0 = 0, ty0 = 0;
    try {
      if (css && css !== 'none') {
        const m = new DOMMatrixReadOnly(css);
        scale0 = Math.abs(Number(m.a || 1)) || 1;
        tx0 = Number(m.e || 0);
        ty0 = Number(m.f || 0);
      }
    } catch (_) {}

    const rawLeft = (rect.left - tx0) / scale0;
    const rawTop = (rect.top - ty0) / scale0;
    const rawWidth = rect.width / scale0;
    const rawHeight = rect.height / scale0;

    const padX = Math.max(26, Math.min(54, window.innerWidth * 0.045));
    const padY = Math.max(22, Math.min(46, window.innerHeight * 0.045));
    const fit = Math.min(
      (window.innerWidth - 2 * padX) / rawWidth,
      (window.innerHeight - 2 * padY) / rawHeight,
      0.92
    );
    const scale = Math.max(0.20, fit);
    const targetLeft = (window.innerWidth - rawWidth * scale) / 2;
    const targetTop = (window.innerHeight - rawHeight * scale) / 2;
    const tx = targetLeft - rawLeft * scale;
    const ty = targetTop - rawTop * scale;

    rootNode.style.transformOrigin = '0 0';
    rootNode.style.transform = `translate(${tx}px, ${ty}px) scale(${scale})`;

    try {
      if (typeof state !== 'undefined') {
        state.activePage = targetNo;
        state.embeddedScale = scale;
      }
    } catch (_) {}

    try {
      const active = document.activeElement;
      if (active && typeof active.blur === 'function') active.blur();
    } catch (_) {}

    try {
      if (window.ipc && typeof window.ipc.postMessage === 'function') {
        window.ipc.postMessage(JSON.stringify({
          type:'page_changed',
          pageNo:targetNo,
          pageCount:pages.length
        }));
      }
    } catch (_) {}

    return {ok:true, pageNo:targetNo, pageCount:pages.length, scale};
  };
  return true;
})()
"""
        try:
            web.eval_js(script)
        except Exception:
            pass

    def _survol_probe_buffer_center(self, host, *, attempt: int = 0, stable: int = 0) -> None:
        """Révèle le buffer seulement après deux mesures réellement centrées."""
        if host is not getattr(self, "_survol_buffer_host", None):
            return
        if not bool(getattr(self, "_survol_buffer_swap_pending", False)):
            return

        wanted = getattr(self, "_survol_buffer_target_local_page", None)
        web = getattr(host, "_web", None)
        if wanted is None or web is None:
            return

        script = f"""
JSON.stringify((() => {{
  const pages = [...document.querySelectorAll('.ce-page-container canvas[data-index]')];
  const node = pages[{int(wanted) - 1}];
  if (!node) return {{ok:false}};
  const r = node.getBoundingClientRect();
  const dx = Math.abs((r.left + r.width / 2) - window.innerWidth / 2);
  const dy = Math.abs((r.top + r.height / 2) - window.innerHeight / 2);
  return {{
    ok: r.width > 0 && r.height > 0,
    dx, dy, width:r.width, height:r.height
  }};
}})())
"""

        def done(raw=None, *_args):
            value = raw
            for _ in range(3):
                if isinstance(value, dict):
                    break
                if not isinstance(value, str):
                    break
                try:
                    value = json.loads(value)
                except Exception:
                    break
            if not isinstance(value, dict):
                value = {}

            centered = bool(
                value.get("ok")
                and float(value.get("dx", 9999) or 9999) <= 4.0
                and float(value.get("dy", 9999) or 9999) <= 4.0
            )
            next_stable = int(stable) + 1 if centered else 0
            if next_stable >= 2:
                self._survol_commit_buffer_swap()
                return

            if int(attempt) >= 80:
                self._phase2_switch_in_progress = False
                self._survol_pause(
                    message=(
                        "Survol en pause : la page suivante est prête mais son "
                        "centrage n'est pas encore stable."
                    )
                )
                return

            if int(attempt) in {12, 28, 48}:
                try:
                    host.go_to_page(int(wanted), smooth=False)
                except Exception:
                    pass

            try:
                self.after(
                    35,
                    lambda: self._survol_probe_buffer_center(
                        host,
                        attempt=int(attempt) + 1,
                        stable=next_stable,
                    ),
                )
            except Exception:
                pass

        try:
            web.eval_js_with_callback(script, done)
        except TypeError:
            try:
                web.eval_js_with_callback(script, done)
            except Exception:
                pass
        except Exception:
            pass

    def _survol_buffer_page_changed(self, host, event: dict) -> None:
        """Les événements du buffer préparent l'image, ils ne naviguent pas le Livre."""

        if host is getattr(self, "_phase2_canvas_host", None):
            self._phase2_on_page_changed(event)
            return

        if host is not getattr(self, "_survol_buffer_host", None):
            return
        if not bool(getattr(self, "_survol_buffer_swap_pending", False)):
            return

        try:
            page_no = int(event.get("pageNo") or event.get("page_no") or 0)
        except (TypeError, ValueError):
            page_no = 0

        wanted = getattr(self, "_survol_buffer_target_local_page", None)
        if wanted is None or page_no != int(wanted):
            return

        # Le signal page_changed n'est plus suffisant : on mesure réellement
        # le centre de la page avant d'échanger les WebView.
        self._survol_probe_buffer_center(host)

    def _survol_buffer_failed(self, canvas, host, chapter_index: int, failure: dict) -> None:
        if host is not getattr(self, "_survol_buffer_host", None):
            return
        requested = getattr(self, "_survol_buffer_requested_global_index", None)
        self._survol_dispose_buffer()
        if requested is not None:
            self._phase2_switch_in_progress = False
            # Repli rare : utiliser le chemin historique plutôt que bloquer le Survol.
            super()._phase2_request_global_page(canvas, int(requested), force=True)

    def _survol_buffer_ready(self, canvas, host, chapter_index: int, snapshot: dict) -> None:
        if host is None or host is not getattr(self, "_survol_buffer_host", None):
            self._survol_destroy_host_instance(host)
            return

        layout = getattr(self, "_phase2_chapter_layout", None)
        if layout is None:
            self._survol_dispose_buffer()
            return

        try:
            count = int((snapshot or {}).get("page_count") or 0)
        except (TypeError, ValueError):
            count = 0
        if count > 0 and count != layout.page_counts[int(chapter_index)]:
            layout.set_page_count(int(chapter_index), count)
            self._phase2_sync_page_count(layout.total_pages)

        self._survol_buffer_ready_flag = True
        self._survol_install_stable_navigation(host)
        try:
            host.lower()
            active = getattr(self, "_phase2_canvas_host", None)
            if active is not None:
                active.tk.call("raise", active._w)
        except Exception:
            pass

        requested = getattr(self, "_survol_buffer_requested_global_index", None)
        if requested is not None:
            target_chapter, local_index = layout.locate_global_index(int(requested))
            if int(target_chapter) == int(chapter_index):
                self._survol_use_buffer(canvas, int(requested), int(chapter_index), int(local_index))

    def _survol_preload_chapter(self, canvas, chapter_index: int) -> None:
        prepared = getattr(self, "_phase2_chapter_prepared", None)
        plans = list(getattr(self, "_phase2_chapter_plans", ()) or ())
        detection = getattr(self, "_phase2_chapter_detection", None)
        if prepared is None or detection is None:
            return
        if not (0 <= int(chapter_index) < len(plans)):
            return
        if int(chapter_index) == int(getattr(self, "_phase2_active_chapter_index", -1) or -1):
            return

        existing = getattr(self, "_survol_buffer_host", None)
        existing_index = getattr(self, "_survol_buffer_chapter_index", None)
        if existing is not None and existing_index == int(chapter_index):
            return
        if existing is not None:
            self._survol_dispose_buffer()

        holder = {}
        source = self._phase2_source_path()
        host = CanvasEditorWebHost(
            canvas,
            project_root=PROJECT_ROOT,
            on_ready=lambda snapshot, idx=int(chapter_index): self._survol_buffer_ready(
                canvas, holder.get("host"), idx, snapshot
            ),
            on_failed=lambda failure, idx=int(chapter_index): self._survol_buffer_failed(
                canvas, holder.get("host"), idx, failure
            ),
            on_editorial_choice=lambda event, src=source: (
                self._phase2_persist_choice(src, event) if src is not None else None
            ),
            on_page_changed=lambda event: self._survol_buffer_page_changed(
                holder.get("host"), event
            ),
            background=theme.WINDOW_DEEP,
        )
        holder["host"] = host

        self._survol_buffer_host = host
        self._survol_buffer_chapter_index = int(chapter_index)
        self._survol_buffer_ready_flag = False
        self._survol_buffer_requested_global_index = None

        # Le nouveau chapitre a besoin de sa vraie taille pour paginer, mais il
        # reste placé SOUS le WebView visible. L'utilisateur conserve donc la
        # dernière vraie page au lieu de regarder une construction technique.
        host.place(x=0, y=0, relwidth=1, relheight=1)
        try:
            host.lower()
            active = getattr(self, "_phase2_canvas_host", None)
            if active is not None:
                active.tk.call("raise", active._w)
        except Exception:
            pass

        try:
            host.load_document(
                plans[int(chapter_index)],
                CanvasLoadSession(prepared.canvas.contract),
            )
        except Exception as exc:
            self._survol_buffer_failed(
                canvas,
                host,
                int(chapter_index),
                {"stage": "survol_preload", "message": str(exc)},
            )

    def _survol_preload_following_chapter(self) -> None:
        if self._composition_current_tool() != "survol":
            return
        if bool(getattr(self, "_phase2_switch_in_progress", False)):
            return
        layout = getattr(self, "_phase2_chapter_layout", None)
        current = getattr(self, "_phase2_active_chapter_index", None)
        canvas = getattr(self, "_composition_editor_canvas", None)
        if layout is None or current is None or canvas is None:
            return
        next_index = int(current) + 1
        plans = list(getattr(self, "_phase2_chapter_plans", ()) or ())
        if next_index < len(plans):
            self._survol_preload_chapter(canvas, next_index)


    def _survol_schedule_buffer_reveal(self, *, delay_ms: int) -> None:
        previous = getattr(self, "_survol_buffer_reveal_after_id", None)
        if previous is not None:
            try:
                self.after_cancel(previous)
            except Exception:
                pass

        try:
            self._survol_buffer_reveal_after_id = self.after(
                int(delay_ms),
                self._survol_commit_buffer_swap,
            )
        except Exception:
            self._survol_buffer_reveal_after_id = None
            self._survol_commit_buffer_swap()

    def _survol_commit_buffer_swap(self) -> None:
        self._survol_buffer_reveal_after_id = None
        if not bool(getattr(self, "_survol_buffer_swap_pending", False)):
            return

        host = getattr(self, "_survol_buffer_host", None)
        chapter_index = getattr(self, "_survol_buffer_chapter_index", None)
        global_index = getattr(self, "_survol_buffer_target_global_index", None)
        local_page = getattr(self, "_survol_buffer_target_local_page", None)

        if (
            host is None
            or not bool(getattr(host, "ready", False))
            or chapter_index is None
            or global_index is None
            or local_page is None
        ):
            return

        old_host = getattr(self, "_phase2_canvas_host", None)

        self._phase2_canvas_host = host
        self._phase2_active_chapter_index = int(chapter_index)
        self._phase2_loading_chapter_index = None
        self._phase2_pending_global_index = int(global_index)
        self._phase2_switch_in_progress = False
        self._phase2_canvas_state = "ready"

        self._survol_buffer_host = None
        self._survol_buffer_chapter_index = None
        self._survol_buffer_ready_flag = False
        self._survol_buffer_requested_global_index = None
        self._survol_buffer_swap_pending = False
        self._survol_buffer_target_local_page = None
        self._survol_buffer_target_global_index = None

        try:
            host.show_when_ready(x=0, y=0, relwidth=1, relheight=1)
        except Exception:
            pass

        try:
            self._phase2_destroy_overlay()
        except Exception:
            pass

        if old_host is not None and old_host is not host:
            try:
                self.after(120, lambda h=old_host: self._survol_destroy_host_instance(h))
            except Exception:
                self._survol_destroy_host_instance(old_host)

        try:
            self.after_idle(self._survol_preload_following_chapter)
        except Exception:
            pass

    def _survol_use_buffer(
        self,
        canvas,
        global_index: int,
        chapter_index: int,
        local_index: int,
    ) -> None:
        """Positionne le prochain chapitre AVANT de le rendre visible.

        L'ancienne version révélait le WebView puis demandait la page. Pendant une
        frame, la page pouvait donc apparaître décalée à gauche. Le WebView reste
        maintenant sous l'ancienne page jusqu'au recentrage de sa cible.
        """

        host = getattr(self, "_survol_buffer_host", None)
        if host is None or not bool(getattr(host, "ready", False)):
            return
        if getattr(self, "_survol_buffer_chapter_index", None) != int(chapter_index):
            return

        self._survol_buffer_requested_global_index = int(global_index)
        self._survol_buffer_target_global_index = int(global_index)
        self._survol_buffer_target_local_page = int(local_index) + 1
        self._survol_buffer_swap_pending = True

        # Important : le buffer reste SOUS l'hôte actif.
        try:
            host.lower()
            active = getattr(self, "_phase2_canvas_host", None)
            if active is not None and active is not host:
                active.tk.call("raise", active._w)
        except Exception:
            pass

        self._survol_install_stable_navigation(host)
        try:
            host.go_to_page(int(local_index) + 1, smooth=False)
        except Exception:
            pass

        # Aucun échange sur simple délai : la page doit être réellement centrée.
        try:
            self.after(
                35,
                lambda h=host: self._survol_probe_buffer_center(h),
            )
        except Exception:
            self._survol_probe_buffer_center(host)

    def _phase2_request_global_page(self, canvas, global_index: int, *, force: bool = False) -> None:
        """Pendant Survol, échange les chapitres sans détruire la page visible."""

        layout = getattr(self, "_phase2_chapter_layout", None)
        if layout is None:
            return super()._phase2_request_global_page(canvas, global_index, force=force)

        global_index = max(0, min(int(global_index), layout.total_pages - 1))
        self._phase2_pending_global_index = global_index

        try:
            survol_active = self._composition_current_tool() == "survol"
        except Exception:
            survol_active = False

        host = getattr(self, "_phase2_canvas_host", None)
        active_chapter = getattr(self, "_phase2_active_chapter_index", None)
        if (
            not survol_active
            or host is None
            or not bool(getattr(host, "ready", False))
            or active_chapter is None
            or str(getattr(self, "_phase2_canvas_state", "") or "") not in {"ready", "chapter_switch"}
        ):
            return super()._phase2_request_global_page(canvas, global_index, force=force)

        chapter_index, local_index = layout.locate_global_index(global_index)
        chapter_index = int(chapter_index)
        local_index = int(local_index)

        if int(active_chapter) == chapter_index:
            self._survol_install_stable_navigation(host)
            host.go_to_page(local_index + 1, smooth=False)
            self._phase2_canvas_state = "ready"
            return

        # Changement d'unité : l'ancien WebView reste visible. Si le suivant a
        # déjà été préchargé, l'échange est immédiat ; sinon il se prépare dessous.
        self._phase2_switch_in_progress = True
        self._phase2_canvas_state = "chapter_switch"
        self._survol_buffer_requested_global_index = global_index

        if (
            getattr(self, "_survol_buffer_chapter_index", None) == chapter_index
            and bool(getattr(self, "_survol_buffer_ready_flag", False))
            and getattr(self, "_survol_buffer_host", None) is not None
        ):
            self._survol_use_buffer(canvas, global_index, chapter_index, local_index)
            return

        if getattr(self, "_survol_buffer_chapter_index", None) != chapter_index:
            self._survol_preload_chapter(canvas, chapter_index)
            self._survol_buffer_requested_global_index = global_index

    def _survol_restart(self) -> None:
        # Le buffer n'est jamais un état éditorial ; il peut être jeté sans perte.
        self._survol_dispose_buffer()
        state = self._survol_state()
        state["cursor"] = 0
        state["reviewed_marker_ids"] = []
        state["rules"] = {}
        state["completed"] = False
        state["schema"] = SURVOL_STATE_SCHEMA
        self._survol_touch()

        self._survol_started = False
        self._survol_running = False
        self._survol_current_marker = None
        self._survol_offer_marker = None
        self._survol_last_decision = None
        self._survol_preview_markers = []
        self._survol_preview_index = -1
        self._survol_preview_excluded_page_ids = set()
        self._survol_preview_return_page_id = None
        self._survol_expected_page_id = None
        self._survol_expected_global_index = None
        self._survol_message = "TomeLinea parcourra le livre dans son ordre réel."

        order = self._survol_page_order()
        if order:
            self._survol_internal_navigation = True
            try:
                self._activate_page(order[0])
            except Exception:
                pass
            finally:
                self._survol_internal_navigation = False
        self._survol_refresh_panel()


    def _navigation_only_open_first_book_page(self) -> None:
        """Ouvre le Livre sur sa première page réelle, couverture comprise."""
        if bool(getattr(self, "_navigation_only_first_page_done", False)):
            return

        book = getattr(getattr(self, "session", None), "book", None)
        order = list(getattr(book, "page_order", ()) or ()) if book is not None else []
        if not order:
            return

        first_page_id = str(order[0])
        self._navigation_only_first_page_done = True

        current = str(getattr(getattr(self, "session", None), "active_page_id", "") or "")
        if current == first_page_id:
            return

        try:
            self._activate_page(first_page_id)
        except Exception:
            self._navigation_only_first_page_done = False
