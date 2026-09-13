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

import tkinter as tk

from src.gui_v4 import theme
from src.gui_v4.editorial_shell import (
    TomeLineaV4Editorial,
)
from src.v4.editorial_structure_classifier import (
    apply_structure_choice,
)
from src.v4.structure_covers import (
    is_cover_face,
)
from src.v4.survol import (
    SurvolMarker,
    build_survol_markers,
    future_similar_markers,
)


class TomeLineaV4Survol(
    TomeLineaV4Editorial
):
    """Habillage V4 + premier fonctionnement testable du Survol."""

    _SURVOL_NORMAL_DELAY_MS = 450
    _SURVOL_RULE_DELAY_MS = 900

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
        self._survol_force_first_tool = True
        self._survol_user_left_tool = False

        super().__init__(
            defer_show=defer_show,
        )

    # ==========================================================
    # ETAT PERSISTANT
    # ==========================================================

    def _survol_state(self) -> dict:
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
            return {
                "schema": (
                    "tomelinea.survol.v1"
                ),
                "cursor": 0,
                "reviewed_marker_ids": [],
                "rules": {},
                "completed": False,
            }

        raw = project.metadata.get(
            "survol_v1"
        )
        if not isinstance(raw, dict):
            raw = {}

        raw.setdefault(
            "schema",
            "tomelinea.survol.v1",
        )
        raw.setdefault(
            "cursor",
            0,
        )
        raw.setdefault(
            "reviewed_marker_ids",
            [],
        )
        raw.setdefault(
            "rules",
            {},
        )
        raw.setdefault(
            "completed",
            False,
        )

        project.metadata[
            "survol_v1"
        ] = raw
        return raw

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

    # ==========================================================
    # ANCIENNE QUESTION STRUCTURELLE -> SURVOL
    # ==========================================================

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

    # ==========================================================
    # ONGLET SURVOL
    # ==========================================================

    def _composition_current_tool(
        self,
    ) -> str:
        if (
            self._survol_force_first_tool
            and not self._survol_user_left_tool
            and not bool(
                self._survol_state().get(
                    "completed",
                    False,
                )
            )
        ):
            return "survol"

        if (
            str(
                getattr(
                    self,
                    "_composition_active_tool",
                    "",
                )
                or ""
            )
            == "survol"
        ):
            return "survol"

        return super()._composition_current_tool()

    def _composition_activate_tool(
        self,
        tool: str,
    ) -> None:
        tool = str(
            tool
            or "book"
        )

        if tool == "survol":
            self._survol_force_first_tool = False
            self._survol_user_left_tool = False
            self._composition_active_tool = (
                "survol"
            )
            self._composition_book_state_open = (
                False
            )
            self._composition_constraints_open = (
                False
            )
            self._composition_pages_open = (
                False
            )
            self._composition_content_open = (
                False
            )
            self._composition_text_flow_open = (
                False
            )
            self._composition_refresh_tool_tabs()
            self._composition_update_inspector_context()
            return

        self._survol_force_first_tool = False
        self._survol_user_left_tool = True
        self._survol_pause(
            refresh=False,
            message=None,
        )
        super()._composition_activate_tool(
            tool
        )

    def _composition_build_tool_rail(
        self,
        parent,
    ):
        """Survol devient le premier onglet permanent."""

        if (
            self._survol_force_first_tool
            and not self._survol_user_left_tool
            and not bool(
                self._survol_state().get(
                    "completed",
                    False,
                )
            )
        ):
            self._composition_active_tool = (
                "survol"
            )

        rail = tk.Frame(
            parent,
            bg=theme.PANEL_ALT,
            width=72,
        )
        rail.pack_propagate(
            False
        )

        self._composition_tool_tabs = {}

        definitions = (
            (
                "survol",
                "Survol",
                40,
            ),
            (
                "book",
                "Format",
                40,
            ),
            (
                "constraints",
                "Contraintes",
                44,
            ),
            (
                "text",
                "Texte",
                40,
            ),
            (
                "layout",
                "Images",
                40,
            ),
        )

        for key, label, height in definitions:
            tab = tk.Canvas(
                rail,
                width=70,
                height=height,
                bg=theme.PANEL_ALT,
                highlightthickness=0,
                bd=0,
                cursor="hand2",
                takefocus=True,
            )
            tab.pack(
                fill="x",
                padx=(1, 1),
                pady=(1, 0),
            )

            text_id = tab.create_text(
                35,
                height / 2,
                text=label,
                width=64,
                justify="center",
                fill=theme.MUTED,
                font=(
                    theme.FONT_UI,
                    8,
                    "bold",
                ),
            )

            self._composition_tool_tabs[
                key
            ] = (
                tab,
                text_id,
            )

            def activate(
                _event=None,
                selected_tool=key,
            ):
                self._composition_activate_tool(
                    selected_tool
                )
                return "break"

            def enter(
                _event=None,
                selected_tool=key,
                selected_tab=tab,
            ):
                if (
                    self._composition_current_tool()
                    != selected_tool
                ):
                    try:
                        selected_tab.configure(
                            bg=theme.PANEL_SOFT
                        )
                    except Exception:
                        pass

            tab.bind(
                "<Button-1>",
                activate,
            )
            tab.bind(
                "<Return>",
                activate,
            )
            tab.bind(
                "<space>",
                activate,
            )
            tab.bind(
                "<Enter>",
                enter,
            )
            tab.bind(
                "<Leave>",
                lambda _event: (
                    self._composition_refresh_tool_tabs()
                ),
            )

        self._composition_refresh_tool_tabs()
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

    # ==========================================================
    # REPÈRES
    # ==========================================================

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

    def _survol_markers(
        self,
    ) -> dict[
        str,
        list[SurvolMarker],
    ]:
        book = getattr(
            getattr(
                self,
                "session",
                None,
            ),
            "book",
            None,
        )

        return build_survol_markers(
            book,
            getattr(
                self,
                "_phase2_editorial_structure_analysis",
                None,
            ),
            self._survol_structure_page_ids(),
            cover_page_ids=(
                self._survol_cover_page_ids()
            ),
        )

    def _survol_page_order(
        self,
    ) -> list[str]:
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
            return []

        return [
            str(page_id)
            for page_id in list(
                getattr(
                    book,
                    "page_order",
                    (),
                )
                or ()
            )
        ]

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

    # ==========================================================
    # PANNEAU
    # ==========================================================

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

    def _composition_render_survol_panel(
        self,
        host,
    ) -> None:
        state = self._survol_state()
        order = self._survol_page_order()
        total = len(order)

        tk.Label(
            host,
            text="SURVOL",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                9,
                "bold",
            ),
        ).pack(
            anchor="w",
            padx=18,
            pady=(10, 4),
        )

        active_page_id = str(
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
        page_no = (
            self._survol_page_number(
                active_page_id
            )
        )

        if page_no is not None:
            progress_text = (
                f"Page {page_no} / {total}"
            )
        else:
            cursor = max(
                0,
                int(
                    state.get(
                        "cursor",
                        0,
                    )
                    or 0
                ),
            )
            progress_text = (
                f"Page "
                f"{min(cursor + 1, max(1, total))}"
                f" / {total}"
            )

        self._survol_label(
            host,
            progress_text,
            strong=True,
            accent=True,
        ).pack(
            fill="x",
            padx=18,
            pady=(0, 8),
        )

        self._survol_label(
            host,
            (
                self._survol_message
                or (
                    "TomeLinea parcourt le livre "
                    "dans son ordre réel."
                )
            ),
            muted=False,
        ).pack(
            fill="x",
            padx=18,
            pady=(0, 10),
        )

        if bool(
            state.get(
                "completed",
                False,
            )
        ):
            self._survol_label(
                host,
                (
                    "Le livre a été parcouru jusqu'à "
                    "sa dernière page."
                ),
                strong=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(2, 10),
            )
            self._button(
                host,
                "Recommencer le Survol",
                self._survol_restart,
                compact=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(0, 6),
            )
            return

        if self._survol_preview_markers:
            self._survol_render_preview_actions(
                host
            )
            return

        if self._survol_current_marker is not None:
            self._survol_render_marker_actions(
                host,
                self._survol_current_marker,
            )
            return

        if self._survol_offer_marker is not None:
            self._survol_render_offer_actions(
                host,
                self._survol_offer_marker,
            )
            return

        if not self._survol_started:
            self._survol_label(
                host,
                (
                    "Toutes les pages seront réellement "
                    "affichées. TomeLinea ne s'arrêtera "
                    "que lorsqu'une décision humaine est "
                    "utile."
                ),
                muted=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(0, 10),
            )
            self._button(
                host,
                "Commencer le Survol",
                self._survol_start,
                compact=True,
                accent=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(0, 6),
            )
            return

        if self._survol_running:
            self._button(
                host,
                "Pause",
                self._survol_pause,
                compact=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(0, 6),
            )
        else:
            self._button(
                host,
                "Continuer",
                self._survol_continue,
                compact=True,
                accent=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(0, 6),
            )

    def _survol_render_marker_actions(
        self,
        host,
        marker: SurvolMarker,
    ) -> None:
        tk.Frame(
            host,
            bg=theme.PAGE_BORDER,
            height=1,
        ).pack(
            fill="x",
            padx=18,
            pady=(3, 10),
        )

        self._survol_label(
            host,
            marker.title,
            strong=True,
            accent=marker.doubtful,
        ).pack(
            fill="x",
            padx=18,
            pady=(0, 5),
        )

        self._survol_label(
            host,
            marker.message,
            muted=True,
        ).pack(
            fill="x",
            padx=18,
            pady=(0, 10),
        )

        if marker.kind == "structure":
            if marker.doubtful:
                self._button(
                    host,
                    "Créer cette division",
                    lambda: (
                        self._survol_validate_marker(
                            "create"
                        )
                    ),
                    compact=True,
                    accent=True,
                ).pack(
                    fill="x",
                    padx=18,
                    pady=(0, 5),
                )
                self._button(
                    host,
                    "Rattacher à la précédente",
                    lambda: (
                        self._survol_validate_marker(
                            "merge"
                        )
                    ),
                    compact=True,
                ).pack(
                    fill="x",
                    padx=18,
                    pady=(0, 5),
                )
            else:
                self._button(
                    host,
                    "Valider",
                    lambda: (
                        self._survol_validate_marker(
                            "accept"
                        )
                    ),
                    compact=True,
                    accent=True,
                ).pack(
                    fill="x",
                    padx=18,
                    pady=(0, 5),
                )
                self._button(
                    host,
                    "Cette division n'a pas lieu d'être",
                    lambda: (
                        self._survol_validate_marker(
                            "merge"
                        )
                    ),
                    compact=True,
                ).pack(
                    fill="x",
                    padx=18,
                    pady=(0, 5),
                )
        else:
            self._button(
                host,
                "Valider",
                lambda: (
                    self._survol_validate_marker(
                        "accept"
                    )
                ),
                compact=True,
                accent=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(0, 5),
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

    # ==========================================================
    # PARCOURS AUTOMATIQUE
    # ==========================================================

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

    def _survol_start(
        self,
    ) -> None:
        state = self._survol_state()

        if bool(
            state.get(
                "completed",
                False,
            )
        ):
            return

        self._survol_started = True
        self._survol_running = True
        self._survol_current_marker = None
        self._survol_offer_marker = None
        self._survol_message = (
            "Survol en cours…"
        )
        self._survol_refresh_panel()
        self._survol_schedule(
            10,
            self._survol_step,
        )

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

    def _survol_page_ready(
        self,
        page_id: str,
    ) -> bool:
        if (
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
            != str(page_id)
        ):
            return False

        try:
            internal_ids = set(
                str(value)
                for value in self._phase2_internal_page_ids()
            )
        except Exception:
            internal_ids = set()

        if str(page_id) not in internal_ids:
            return True

        if bool(
            getattr(
                self,
                "_phase2_switch_in_progress",
                False,
            )
        ):
            return False

        state = str(
            getattr(
                self,
                "_phase2_canvas_state",
                "",
            )
            or ""
        )

        return state in {
            "ready",
            "prepared",
        }

    def _survol_wait_then(
        self,
        page_id: str,
        callback,
        *,
        attempt: int = 0,
    ) -> None:
        if self._survol_page_ready(
            page_id
        ):
            callback()
            return

        if attempt >= 80:
            callback()
            return

        self._survol_schedule(
            75,
            lambda: (
                self._survol_wait_then(
                    page_id,
                    callback,
                    attempt=attempt + 1,
                )
            ),
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

    def _survol_step(
        self,
    ) -> None:
        self._survol_after_id = None

        if not self._survol_running:
            return

        order = self._survol_page_order()
        if not order:
            self._survol_message = (
                "Aucune page à survoler."
            )
            self._survol_running = False
            self._survol_refresh_panel()
            return

        state = self._survol_state()
        cursor = max(
            0,
            int(
                state.get(
                    "cursor",
                    0,
                )
                or 0
            ),
        )

        if cursor >= len(order):
            state[
                "completed"
            ] = True
            state[
                "cursor"
            ] = len(order)
            self._survol_running = False
            self._survol_message = (
                "Survol terminé."
            )
            self._survol_touch()
            self._survol_refresh_panel()
            return

        page_id = str(
            order[
                cursor
            ]
        )

        markers_by_page = (
            self._survol_markers()
        )
        markers = list(
            markers_by_page.get(
                page_id,
                (),
            )
        )
        reviewed = (
            self._survol_reviewed_ids()
        )

        current_marker = None
        applied_rule = None
        applied_rule_marker = None

        for marker in markers:
            if (
                marker.marker_id
                in reviewed
            ):
                continue

            rule = self._survol_rule_for(
                marker
            )

            if rule is not None:
                reviewed.add(
                    marker.marker_id
                )
                if applied_rule is None:
                    applied_rule = rule
                    applied_rule_marker = marker
                continue

            current_marker = marker
            break

        self._survol_current_marker = (
            current_marker
        )
        self._survol_offer_marker = None

        if current_marker is not None:
            self._survol_running = False
            self._survol_message = (
                current_marker.message
            )
        elif applied_rule is not None:
            anchor = (
                applied_rule.get(
                    "anchor_page_number"
                )
                or "?"
            )
            self._survol_message = (
                "Règle déjà définie à partir "
                f"de la page {anchor}."
            )
        else:
            self._survol_message = (
                "Survol en cours…"
            )

        try:
            self._activate_page(
                page_id
            )
        except Exception:
            try:
                self.session.set_active_page(
                    page_id
                )
                self._composition_update_editor()
            except Exception:
                pass

        # Une règle étendue n'est réellement appliquée qu'au moment où
        # la vraie page correspondante est survolée. Ainsi aucun cas futur
        # ne disparaît du parcours et l'utilisateur voit bien le livre entier.
        if (
            applied_rule is not None
            and applied_rule_marker is not None
        ):
            decision = str(
                applied_rule.get(
                    "decision",
                    "accept",
                )
                or "accept"
            )
            if (
                applied_rule_marker.kind
                == "structure"
                and decision
                in {
                    "create",
                    "merge",
                }
            ):
                self._survol_apply_structure_decision(
                    applied_rule_marker,
                    decision,
                )

        if reviewed != self._survol_reviewed_ids():
            self._survol_set_reviewed_ids(
                reviewed
            )

        self._survol_refresh_panel()

        if current_marker is not None:
            return

        delay = (
            self._SURVOL_RULE_DELAY_MS
            if applied_rule is not None
            else self._SURVOL_NORMAL_DELAY_MS
        )

        self._survol_wait_then(
            page_id,
            lambda: (
                self._survol_advance_from(
                    cursor,
                    delay_ms=delay,
                )
            ),
        )

    # ==========================================================
    # DECISION SUR UN REPERE
    # ==========================================================

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

    # ==========================================================
    # CAS SIMILAIRES
    # ==========================================================

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

        state[
            "cursor"
        ] = anchor_index + 1
        self._survol_touch()

        self._survol_running = True
        self._survol_refresh_panel()
        self._survol_schedule(
            350,
            self._survol_step,
        )

    # ==========================================================
    # RECOMMENCER
    # ==========================================================

    def _survol_restart(
        self,
    ) -> None:
        state = self._survol_state()
        state[
            "cursor"
        ] = 0
        state[
            "reviewed_marker_ids"
        ] = []
        state[
            "rules"
        ] = {}
        state[
            "completed"
        ] = False

        self._survol_touch()

        self._survol_cached_order = None
        self._survol_cached_markers = None
        self._survol_cache_book_id = None

        self._survol_started = False
        self._survol_running = False
        self._survol_current_marker = None
        self._survol_offer_marker = None
        self._survol_last_decision = None
        self._survol_preview_markers = []
        self._survol_preview_index = -1
        self._survol_preview_excluded_page_ids = set()
        self._survol_preview_return_page_id = None

        self._survol_message = (
            "TomeLinea parcourra le livre "
            "dans son ordre réel."
        )

        order = self._survol_page_order()
        if order:
            try:
                self._activate_page(
                    order[
                        0
                    ]
                )
            except Exception:
                pass

        self._survol_refresh_panel()

    # ==========================================================
    # PHASE 2.39D — SURVOL ERGONOMIQUE
    # ==========================================================

    # Une page doit rester visible assez longtemps pour qu'un humain puisse
    # comprendre ce qui vient de changer et atteindre Pause sans anticiper.
    _SURVOL_NORMAL_DELAY_MS = 1300
    _SURVOL_RULE_DELAY_MS = 1700

    def _survol_prepare_route(self, *, force: bool = False) -> None:
        """Pré-calcule l'ordre et les repères une seule fois avant le Survol."""

        book = getattr(getattr(self, "session", None), "book", None)
        if book is None:
            self._survol_cached_order = []
            self._survol_cached_markers = {}
            self._survol_cache_book_id = None
            return

        book_id = id(book)
        if (
            not force
            and getattr(self, "_survol_cache_book_id", None) == book_id
            and isinstance(getattr(self, "_survol_cached_order", None), list)
            and isinstance(getattr(self, "_survol_cached_markers", None), dict)
        ):
            return

        order = [
            str(page_id)
            for page_id in list(getattr(book, "page_order", ()) or ())
        ]
        markers = build_survol_markers(
            book,
            getattr(self, "_phase2_editorial_structure_analysis", None),
            self._survol_structure_page_ids(),
            cover_page_ids=self._survol_cover_page_ids(),
        )

        self._survol_cached_order = order
        self._survol_cached_markers = markers
        self._survol_cache_book_id = book_id

        # Les règles 2.39C de structure utilisaient une famille trop large
        # (ex. structure:chapter). Elles ne doivent pas continuer à avaler
        # tous les futurs arrêts après installation de 2.39D.
        state = self._survol_state()
        raw_rules = state.get("rules", {})
        if isinstance(raw_rules, dict):
            cleaned = {}
            for key, value in raw_rules.items():
                key = str(key)
                if key.startswith("structure:") and key.count(":") < 5:
                    continue
                cleaned[key] = value
            if cleaned != raw_rules:
                state["rules"] = cleaned
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

    def _activate_page(
        self,
        page_id: str,
        *,
        preserve_page_selection: bool = False,
    ) -> None:
        """Une navigation manuelle suspend immédiatement le Survol."""

        if bool(getattr(self, "_survol_running", False)):
            try:
                order = self._survol_page_order()
                cursor = max(0, int(self._survol_state().get("cursor", 0) or 0))
                expected = order[cursor] if 0 <= cursor < len(order) else None
            except Exception:
                expected = None

            if expected is not None and str(page_id) != str(expected):
                self._survol_pause(
                    refresh=False,
                    message=(
                        "Survol en pause — vous avez repris la navigation manuelle. "
                        "Cliquez sur Continuer pour repartir de ce point de contrôle."
                    ),
                )

        return super()._activate_page(
            page_id,
            preserve_page_selection=preserve_page_selection,
        )

    def _phase2_on_page_changed(self, event: dict) -> None:
        """Même protection quand la navigation vient directement du Canvas."""

        if bool(getattr(self, "_survol_running", False)):
            try:
                layout = getattr(self, "_phase2_chapter_layout", None)
                chapter_index = getattr(self, "_phase2_active_chapter_index", None)
                local_page_no = int(event.get("pageNo") or event.get("page_no") or 0)
                if layout is not None and chapter_index is not None and local_page_no >= 1:
                    target = int(layout.global_index(int(chapter_index), local_page_no - 1))
                    expected = max(0, int(self._survol_state().get("cursor", 0) or 0))
                    if target != expected:
                        self._survol_pause(
                            refresh=False,
                            message=(
                                "Survol en pause — navigation manuelle détectée. "
                                "TomeLinea ne vous ramènera pas automatiquement en avant."
                            ),
                        )
            except Exception:
                pass

        return super()._phase2_on_page_changed(event)

    def _composition_render_survol_panel(self, host) -> None:
        """Panneau stable : progression, commande permanente, puis décision."""

        state = self._survol_state()
        order = self._survol_page_order()
        total = len(order)
        active_page_id = str(getattr(getattr(self, "session", None), "active_page_id", "") or "")
        page_no = self._survol_page_number(active_page_id)

        tk.Label(
            host,
            text="SURVOL",
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(theme.FONT_UI, 9, "bold"),
        ).pack(anchor="w", padx=18, pady=(10, 2))

        progress = (
            f"Page {page_no} / {total}"
            if page_no is not None
            else f"Page {min(max(1, int(state.get('cursor', 0) or 0) + 1), max(1, total))} / {total}"
        )
        tk.Label(
            host,
            text=progress,
            bg=theme.PANEL,
            fg=theme.ACCENT_BRIGHT,
            font=(theme.FONT_UI, 10, "bold"),
        ).pack(anchor="w", padx=18, pady=(0, 7))

        blocked_by_decision = bool(
            self._survol_current_marker is not None
            or self._survol_offer_marker is not None
            or self._survol_preview_markers
        )

        # La commande de rythme reste toujours au même endroit. L'utilisateur
        # n'a plus à la chercher pendant que les pages bougent.
        if not bool(state.get("completed", False)) and not blocked_by_decision:
            if self._survol_running:
                self._button(
                    host,
                    "Pause",
                    self._survol_pause,
                    compact=True,
                ).pack(fill="x", padx=18, pady=(0, 7))
            elif self._survol_started:
                self._button(
                    host,
                    "Continuer",
                    self._survol_continue,
                    compact=True,
                    accent=True,
                ).pack(fill="x", padx=18, pady=(0, 7))

        if self._survol_current_marker is not None:
            status = "Arrêt automatique : TomeLinea a besoin de votre décision."
        elif self._survol_offer_marker is not None:
            status = "Décision prise : vérifiez maintenant si elle peut devenir une règle."
        elif self._survol_preview_markers:
            status = "Vous regardez des exemples similaires ; le curseur principal n'a pas bougé."
        elif self._survol_running:
            status = "Survol en cours — une page reste visible assez longtemps pour pouvoir réagir."
        elif self._survol_started:
            status = self._survol_message or "Survol en pause."
        else:
            status = "Le livre sera parcouru dans son ordre réel, sans saut de catégorie."

        tk.Label(
            host,
            text=status,
            bg=theme.PANEL,
            fg=theme.MUTED,
            wraplength=215,
            justify="left",
            anchor="w",
            font=(theme.FONT_UI, 8),
        ).pack(fill="x", padx=18, pady=(0, 9))

        if bool(state.get("completed", False)):
            tk.Label(
                host,
                text="Le livre a été parcouru jusqu'à sa dernière page.",
                bg=theme.PANEL,
                fg=theme.INK,
                wraplength=215,
                justify="left",
                font=(theme.FONT_UI, 9, "bold"),
            ).pack(fill="x", padx=18, pady=(3, 9))
            self._button(
                host,
                "Recommencer le Survol",
                self._survol_restart,
                compact=True,
            ).pack(fill="x", padx=18, pady=(0, 6))
            return

        if self._survol_preview_markers:
            self._survol_render_preview_actions(host)
            return

        if self._survol_current_marker is not None:
            self._survol_render_marker_actions(host, self._survol_current_marker)
            return

        if self._survol_offer_marker is not None:
            self._survol_render_offer_actions(host, self._survol_offer_marker)
            return

        if not self._survol_started:
            tk.Label(
                host,
                text=(
                    "Précédente, Suivante ou un clic dans la Structure mettront "
                    "automatiquement le Survol en pause : TomeLinea ne luttera plus "
                    "contre votre navigation."
                ),
                bg=theme.PANEL,
                fg=theme.MUTED,
                wraplength=215,
                justify="left",
                anchor="w",
                font=(theme.FONT_UI, 8),
            ).pack(fill="x", padx=18, pady=(0, 10))
            self._button(
                host,
                "Commencer le Survol",
                self._survol_start,
                compact=True,
                accent=True,
            ).pack(fill="x", padx=18, pady=(0, 6))

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
