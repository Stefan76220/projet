from __future__ import annotations

"""Coque GUI V5 Roman.

La V5 reutilise la coque V4 validee. Toute activation manuelle de page passe
par la Navigation commune de ``RomanSession``.

V5-25 remplace uniquement le moteur/panneau Survol d'observation de la coque
heritee par le parcours decisionnel V5. Le rendu Canvas/WebView reste entierement
celui de la V4.
"""

from typing import Any
import tkinter as tk

from src.gui_v4 import theme
from src.gui_v4.settings_shell import TomeLineaV4SettingsStage

from tomelinea.project_types.roman import RomanSession
from tomelinea.survol import review_subject_ids

from .survol_presenter import (
    decision_for_current,
    presentation_for_situation,
)


class TomeLineaV5RomanStage(
    TomeLineaV4SettingsStage
):
    """Hote graphique V5 du Roman, construit sur la coque V4 validee."""

    def __init__(
        self,
        *,
        defer_show: bool = False,
    ) -> None:
        self._v5_roman_session: RomanSession | None = None
        self._v5_roman_project: Any = None
        self._v5_roman_book: Any = None
        self._v5_survol_last_error = ""
        self._v5_final_review_active = False
        self._v5_final_review_page_id = ""

        super().__init__(
            defer_show=defer_show
        )

        try:
            self.title(
                "TomeLinea V5"
            )
        except Exception:
            pass

    @property
    def v5_roman_session(
        self,
    ) -> RomanSession | None:
        return self._v5_roman_session

    def _v5_current_project(
        self,
    ) -> Any:
        workspace = getattr(
            self,
            "session",
            None,
        )

        if workspace is None:
            return None

        return getattr(
            workspace,
            "project",
            None,
        )

    def _v5_ensure_roman_session(
        self,
    ) -> RomanSession | None:
        project = self._v5_current_project()

        if project is None:
            self._v5_roman_session = None
            self._v5_roman_project = None
            self._v5_roman_book = None
            return None

        book = getattr(
            project,
            "book",
            None,
        )

        if book is None:
            self._v5_roman_session = None
            self._v5_roman_project = project
            self._v5_roman_book = None
            return None

        current = self._v5_roman_session

        if (
            current is not None
            and self._v5_roman_project is project
            and self._v5_roman_book is book
            and current.project is project
            and current.book is book
        ):
            return current

        current = RomanSession(
            project
        )

        self._v5_roman_session = current
        self._v5_roman_project = project
        self._v5_roman_book = book

        return current

    def _v5_apply_navigation_target(
        self,
        page_id: str,
        *,
        preserve_page_selection: bool = False,
    ) -> None:
        """Rend une cible deja demandee sans creer une seconde demande V5."""

        super()._activate_page(
            str(
                page_id
            ),
            preserve_page_selection=preserve_page_selection,
        )

    def _activate_page(
        self,
        page_id: str,
        *,
        preserve_page_selection: bool = False,
    ) -> None:
        """Porte unique V5 : Navigation commune d'abord, rendu V4 ensuite."""

        page_id = str(
            page_id
        )

        roman = self._v5_ensure_roman_session()

        if roman is not None:
            target = roman.navigation.request_page(
                roman.book,
                page_id,
            )

            if target.page_id != page_id:
                raise RuntimeError(
                    "La Navigation V5 n'a pas conserve la page demandee."
                )

        self._v5_apply_navigation_target(
            page_id,
            preserve_page_selection=preserve_page_selection,
        )

    # ==========================================================
    # SURVOL V5 — RomanSession + rendu V4
    # ==========================================================

    def _v5_sync_survol_flags(
        self,
        roman: RomanSession,
    ) -> None:
        self._survol_running = bool(
            roman.survol.running
        )
        self._survol_started = bool(
            roman.survol.started
        )
        self._survol_completed = bool(
            roman.survol.completed
        )
        self._survol_position = int(
            roman.survol.position
        )

    def _v5_schedule_visible(
        self,
        generation: int,
        page_id: str,
    ) -> None:
        self._survol_watch_after_id = self.after(
            50,
            lambda g=generation, pid=str(page_id): self._survol_wait_visible(
                g,
                self._survol_position,
                pid,
            ),
        )

    def _v5_schedule_dwell(
        self,
        generation: int,
    ) -> None:
        self._survol_dwell_after_id = self.after(
            int(
                getattr(
                    self,
                    "_survol_dwell_ms",
                    2000,
                )
                or 2000
            ),
            lambda g=generation: self._survol_advance(
                g,
                self._survol_position,
            ),
        )

    def _v5_render_requested_target(
        self,
        target,
        *,
        message: str,
    ) -> None:
        self._survol_cancel_timers()
        self._survol_generation += 1
        generation = int(
            self._survol_generation
        )

        self._survol_position = int(
            target.global_index
        )
        self._survol_expected_global_index = int(
            target.global_index
        )
        self._survol_message = str(
            message
        )

        self._survol_refresh_panel()

        # La cible a DEJA ete demandee par RomanSession.
        # Ne jamais repasser par _activate_page(), sinon Navigation compterait
        # une seconde demande.
        self._v5_apply_navigation_target(
            target.page_id
        )

        self._survol_attach_click_hook()
        self._v5_schedule_visible(
            generation,
            target.page_id,
        )

    def _survol_start(
        self,
    ) -> None:
        if bool(
            getattr(
                self,
                "_settings_ui_locked",
                False,
            )
        ):
            return

        roman = self._v5_ensure_roman_session()

        if roman is None:
            self._survol_message = "Aucun Livre Roman à survoler."
            self._survol_refresh_panel()
            return

        self._v5_final_review_active = False
        self._v5_final_review_page_id = ""

        try:
            target = roman.start()
        except Exception as exc:
            self._v5_survol_last_error = str(
                exc
            )
            self._survol_message = (
                "Le Survol n'a pas pu démarrer : "
                + str(exc)
            )
            self._survol_refresh_panel()
            return

        self._v5_sync_survol_flags(
            roman
        )

        if target is None:
            self._survol_message = "Aucune page à survoler."
            self._survol_refresh_panel()
            return

        total = len(
            getattr(
                roman.book,
                "page_order",
                (),
            )
        )

        self._v5_render_requested_target(
            target,
            message=f"Survol en cours — {total} pages.",
        )

    def _survol_wait_visible(
        self,
        generation: int,
        position: int,
        page_id: str,
    ) -> None:
        self._survol_watch_after_id = None

        if generation != int(
            getattr(
                self,
                "_survol_generation",
                0,
            )
            or 0
        ):
            return

        roman = self._v5_ensure_roman_session()

        if roman is None:
            return

        self._v5_sync_survol_flags(
            roman
        )

        if not roman.survol.running:
            return

        self._survol_attach_click_hook()

        state = str(
            getattr(
                self,
                "_phase2_canvas_state",
                "",
            )
            or ""
        )
        active = str(
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
        host = getattr(
            self,
            "_phase2_canvas_host",
            None,
        )

        ready = bool(
            active == str(
                page_id
            )
            and host is not None
            and bool(
                getattr(
                    host,
                    "ready",
                    False,
                )
            )
            and state == "ready"
            and not bool(
                getattr(
                    self,
                    "_phase2_switch_in_progress",
                    False,
                )
            )
        )

        if not ready:
            self._survol_watch_after_id = self.after(
                60,
                lambda g=generation, p=position, pid=page_id: self._survol_wait_visible(
                    g,
                    p,
                    pid,
                ),
            )
            return

        self._v5_on_page_visible(
            generation,
            page_id,
        )

    def _v5_on_page_visible(
        self,
        generation: int,
        page_id: str,
    ) -> None:
        roman = self._v5_ensure_roman_session()

        if roman is None:
            return

        try:
            snapshot = roman.page_visible(
                page_id
            )
        except Exception as exc:
            self._v5_survol_last_error = str(
                exc
            )
            self._survol_message = (
                "Impossible d'analyser cette page : "
                + str(exc)
            )
            roman.pause(
                active_page_id=page_id
            )
            self._v5_sync_survol_flags(
                roman
            )
            self._survol_refresh_panel()
            return

        total = len(
            getattr(
                roman.book,
                "page_order",
                (),
            )
        )
        page_no = int(
            roman.survol.position
        ) + 1

        if snapshot.current_situation is not None:
            self._survol_message = (
                f"Page {page_no} / {total} — décision requise."
            )
            self._survol_refresh_panel()
            return

        self._survol_message = (
            f"Page {page_no} / {total} — aucun point à traiter."
        )
        self._survol_refresh_panel()
        self._v5_schedule_dwell(
            generation
        )

    def _survol_advance(
        self,
        generation: int | None = None,
        position: int | None = None,
    ) -> None:
        self._survol_dwell_after_id = None

        if (
            generation is not None
            and generation != int(
                getattr(
                    self,
                    "_survol_generation",
                    0,
                )
                or 0
            )
        ):
            return

        roman = self._v5_ensure_roman_session()

        if roman is None:
            return

        if not roman.survol.running:
            self._v5_sync_survol_flags(
                roman
            )
            return

        if not roman.review.page_complete:
            self._survol_message = "Une décision est encore nécessaire sur cette page."
            self._survol_refresh_panel()
            return

        try:
            target = roman.advance()
        except Exception as exc:
            self._v5_survol_last_error = str(
                exc
            )
            self._survol_message = str(
                exc
            )
            self._survol_refresh_panel()
            return

        self._v5_sync_survol_flags(
            roman
        )

        if target is None:
            self._survol_message = "Survol terminé — dernière page atteinte."
            self._survol_set_click_hook_active(
                False
            )
            self._survol_refresh_panel()
            return

        self._v5_render_requested_target(
            target,
            message=(
                f"Ouverture de la page "
                f"{target.global_index + 1} / "
                f"{len(roman.book.page_order)}…"
            ),
        )

    def _survol_pause(
        self,
        message: str = "Survol en pause.",
    ) -> None:
        roman = self._v5_ensure_roman_session()

        if roman is None or not roman.survol.started:
            return

        self._survol_cancel_timers()

        active = str(
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

        roman.pause(
            active_page_id=(
                active
                or None
            )
        )
        self._v5_sync_survol_flags(
            roman
        )

        self._survol_generation += 1
        self._survol_message = str(
            message
            or "Survol en pause."
        )
        self._survol_set_click_hook_active(
            False
        )
        self._survol_refresh_panel()

    def _survol_continue(
        self,
    ) -> None:
        if bool(
            getattr(
                self,
                "_settings_ui_locked",
                False,
            )
        ):
            return

        roman = self._v5_ensure_roman_session()

        if roman is None:
            return

        active = str(
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

        try:
            target = roman.resume(
                active_page_id=(
                    active
                    or None
                )
            )
        except Exception as exc:
            self._survol_message = str(
                exc
            )
            self._survol_refresh_panel()
            return

        self._v5_sync_survol_flags(
            roman
        )

        if target is None:
            self._survol_message = "Aucune page à reprendre."
            self._survol_refresh_panel()
            return

        self._v5_render_requested_target(
            target,
            message="Survol repris.",
        )

    def _survol_stop(
        self,
        message: str = "Survol arrêté.",
    ) -> None:
        roman = self._v5_ensure_roman_session()

        self._survol_cancel_timers()

        if roman is not None:
            active = str(
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

            roman.stop(
                active_page_id=(
                    active
                    or None
                )
            )
            self._v5_sync_survol_flags(
                roman
            )

        self._survol_generation += 1
        self._survol_message = str(
            message
            or "Survol arrêté."
        )
        self._survol_detach_click_hook()
        self._survol_refresh_panel()

    def _v5_survol_choose(
        self,
        choice: str,
    ) -> None:
        roman = self._v5_ensure_roman_session()

        if roman is None:
            return

        try:
            decision = decision_for_current(
                roman.review,
                choice,
            )
            result = roman.execute(
                decision
            )
        except Exception as exc:
            self._v5_survol_last_error = str(
                exc
            )
            self._survol_message = (
                "Cette décision ne peut pas être appliquée : "
                + str(exc)
            )
            self._survol_refresh_panel()
            return

        self._v5_sync_survol_flags(
            roman
        )

        if result.review.current_situation is not None:
            self._survol_message = "Décision enregistrée — autre point sur cette page."
            self._survol_refresh_panel()
            return

        self._survol_message = "Décision enregistrée."
        self._survol_refresh_panel()

        if bool(
            getattr(
                self,
                "_v5_final_review_active",
                False,
            )
        ):
            self._survol_generation += 1
            generation = int(
                self._survol_generation
            )
            self._v5_schedule_final_dwell(
                generation
            )
            return

        if roman.survol.running:
            self._survol_generation += 1
            generation = int(
                self._survol_generation
            )
            self._v5_schedule_dwell(
                generation
            )


    # ==========================================================
    # CONTROLE FINAL V5 — objets A revoir, meme Navigation
    # ==========================================================

    def _v5_schedule_final_visible(
        self,
        generation: int,
        page_id: str,
    ) -> None:
        self._survol_watch_after_id = self.after(
            50,
            lambda g=generation, pid=str(page_id): self._v5_wait_final_visible(
                g,
                pid,
            ),
        )

    def _v5_schedule_final_dwell(
        self,
        generation: int,
    ) -> None:
        self._survol_dwell_after_id = self.after(
            int(
                getattr(
                    self,
                    "_survol_dwell_ms",
                    2000,
                )
                or 2000
            ),
            lambda g=generation: self._v5_advance_final_review(
                g
            ),
        )

    def _v5_render_final_request(
        self,
        request,
    ) -> None:
        self._survol_cancel_timers()
        self._survol_generation += 1
        generation = int(
            self._survol_generation
        )

        self._v5_final_review_active = True
        self._v5_final_review_page_id = str(
            request.target.page_id
        )
        self._survol_position = int(
            request.target.global_index
        )
        self._survol_expected_global_index = int(
            request.target.global_index
        )
        self._survol_message = (
            "Contrôle final — ouverture de la page "
            f"{request.target.global_index + 1}."
        )
        self._survol_set_click_hook_active(
            False
        )
        self._survol_refresh_panel()

        # RomanSession.final_review() a DEJA effectue l'unique demande
        # Navigation. Ici on ne fait que rendre cette cible.
        self._v5_apply_navigation_target(
            request.navigation.page_id
        )
        self._v5_schedule_final_visible(
            generation,
            request.navigation.page_id,
        )

    def _v5_start_final_review(
        self,
    ) -> None:
        roman = self._v5_ensure_roman_session()

        if roman is None or not roman.survol.completed:
            return

        pending = review_subject_ids(
            roman.review
        )

        if not pending:
            self._v5_final_review_active = False
            self._v5_final_review_page_id = ""
            self._survol_message = "Aucun élément à revoir."
            self._survol_refresh_panel()
            return

        try:
            request = roman.final_review()
        except Exception as exc:
            self._v5_survol_last_error = str(
                exc
            )
            self._survol_message = (
                "Le contrôle final ne peut pas démarrer : "
                + str(exc)
            )
            self._survol_refresh_panel()
            return

        if request is None:
            self._v5_final_review_active = False
            self._v5_final_review_page_id = ""
            self._survol_message = (
                f"{len(pending)} élément(s) restent À revoir, "
                "mais aucune page actuelle ne permet de les ouvrir."
            )
            self._survol_refresh_panel()
            return

        self._v5_render_final_request(
            request
        )

    def _v5_wait_final_visible(
        self,
        generation: int,
        page_id: str,
    ) -> None:
        self._survol_watch_after_id = None

        if generation != int(
            getattr(
                self,
                "_survol_generation",
                0,
            )
            or 0
        ):
            return

        if not bool(
            getattr(
                self,
                "_v5_final_review_active",
                False,
            )
        ):
            return

        state = str(
            getattr(
                self,
                "_phase2_canvas_state",
                "",
            )
            or ""
        )
        active = str(
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
        host = getattr(
            self,
            "_phase2_canvas_host",
            None,
        )

        ready = bool(
            active == str(
                page_id
            )
            and host is not None
            and bool(
                getattr(
                    host,
                    "ready",
                    False,
                )
            )
            and state == "ready"
            and not bool(
                getattr(
                    self,
                    "_phase2_switch_in_progress",
                    False,
                )
            )
        )

        if not ready:
            self._survol_watch_after_id = self.after(
                60,
                lambda g=generation, pid=page_id: self._v5_wait_final_visible(
                    g,
                    pid,
                ),
            )
            return

        self._v5_on_final_page_visible(
            generation,
            page_id,
        )

    def _v5_on_final_page_visible(
        self,
        generation: int,
        page_id: str,
    ) -> None:
        roman = self._v5_ensure_roman_session()

        if roman is None:
            return

        try:
            snapshot = roman.page_visible(
                page_id
            )
        except Exception as exc:
            self._v5_survol_last_error = str(
                exc
            )
            self._survol_message = (
                "Impossible de revoir cette page : "
                + str(exc)
            )
            self._v5_finish_final_review(
                interrupted=True
            )
            return

        if snapshot.current_situation is not None:
            self._survol_message = "Contrôle final — décision requise."
            self._survol_refresh_panel()
            return

        self._survol_message = "Contrôle final — aucun point restant sur cette page."
        self._survol_refresh_panel()
        self._v5_schedule_final_dwell(
            generation
        )

    def _v5_advance_final_review(
        self,
        generation: int | None = None,
    ) -> None:
        self._survol_dwell_after_id = None

        if (
            generation is not None
            and generation != int(
                getattr(
                    self,
                    "_survol_generation",
                    0,
                )
                or 0
            )
        ):
            return

        if not bool(
            getattr(
                self,
                "_v5_final_review_active",
                False,
            )
        ):
            return

        roman = self._v5_ensure_roman_session()

        if roman is None:
            return

        current_page_id = str(
            getattr(
                self,
                "_v5_final_review_page_id",
                "",
            )
            or ""
        )

        try:
            request = roman.final_review(
                after_page_id=(
                    current_page_id
                    or None
                )
            )
        except Exception as exc:
            self._v5_survol_last_error = str(
                exc
            )
            self._survol_message = (
                "Le contrôle final ne peut pas continuer : "
                + str(exc)
            )
            self._v5_finish_final_review(
                interrupted=True
            )
            return

        if request is not None:
            self._v5_render_final_request(
                request
            )
            return

        remaining = review_subject_ids(
            roman.review
        )

        self._v5_final_review_active = False
        self._v5_final_review_page_id = ""
        self._survol_set_click_hook_active(
            False
        )

        if remaining:
            self._survol_message = (
                f"{len(remaining)} élément(s) restent À revoir. "
                "Aucun retour automatique en arrière n'est effectué."
            )
        else:
            self._survol_message = "Contrôle final terminé."

        self._survol_refresh_panel()

    def _v5_finish_final_review(
        self,
        *,
        interrupted: bool = False,
    ) -> None:
        self._survol_cancel_timers()
        self._survol_generation += 1
        self._v5_final_review_active = False
        self._v5_final_review_page_id = ""
        self._survol_set_click_hook_active(
            False
        )

        if interrupted:
            if not str(
                getattr(
                    self,
                    "_survol_message",
                    "",
                )
                or ""
            ):
                self._survol_message = (
                    "Contrôle final interrompu — les éléments À revoir sont conservés."
                )
        else:
            self._survol_message = (
                "Contrôle final interrompu — les éléments À revoir sont conservés."
            )

        self._survol_refresh_panel()

    def _survol_render_panel(
        self,
        host,
    ) -> None:
        for child in host.winfo_children():
            try:
                child.destroy()
            except Exception:
                pass

        roman = self._v5_ensure_roman_session()

        total = 0
        position = 0

        if roman is not None:
            total = len(
                getattr(
                    roman.book,
                    "page_order",
                    (),
                )
            )
            position = int(
                roman.survol.position
            )
            self._v5_sync_survol_flags(
                roman
            )

            if bool(
                getattr(
                    self,
                    "_v5_final_review_active",
                    False,
                )
            ):
                position = int(
                    getattr(
                        self,
                        "_survol_position",
                        position,
                    )
                )

        tk.Label(
            host,
            text="SURVOL",
            bg=theme.PANEL,
            fg=theme.ACCENT_BRIGHT,
            font=(
                theme.FONT_UI,
                10,
                "bold",
            ),
            anchor="w",
        ).pack(
            fill="x",
            padx=18,
            pady=(
                14,
                3,
            ),
        )

        tk.Label(
            host,
            text=(
                f"Page {position + 1} / {total}"
                if total
                else "Aucune page"
            ),
            bg=theme.PANEL,
            fg=theme.MUTED,
            font=(
                theme.FONT_UI,
                9,
                "bold",
            ),
            anchor="w",
        ).pack(
            fill="x",
            padx=18,
            pady=(
                0,
                8,
            ),
        )

        tk.Label(
            host,
            text=str(
                getattr(
                    self,
                    "_survol_message",
                    "",
                )
                or "Le Survol est prêt."
            ),
            bg=theme.PANEL,
            fg=theme.INK,
            wraplength=215,
            justify="left",
            anchor="w",
            font=(
                theme.FONT_UI,
                8,
            ),
        ).pack(
            fill="x",
            padx=18,
            pady=(
                0,
                10,
            ),
        )

        situation = (
            roman.review.current_situation
            if roman is not None
            else None
        )

        if situation is not None:
            presentation = presentation_for_situation(
                situation
            )

            tk.Label(
                host,
                text=presentation.title,
                bg=theme.PANEL,
                fg=theme.INK,
                wraplength=215,
                justify="left",
                anchor="w",
                font=(
                    theme.FONT_UI,
                    9,
                    "bold",
                ),
            ).pack(
                fill="x",
                padx=18,
                pady=(
                    2,
                    6,
                ),
            )

            if presentation.technical_term:
                tk.Label(
                    host,
                    text=f"({presentation.technical_term})",
                    bg=theme.PANEL,
                    fg=theme.MUTED,
                    wraplength=215,
                    justify="left",
                    anchor="w",
                    font=(
                        theme.FONT_UI,
                        8,
                    ),
                ).pack(
                    fill="x",
                    padx=18,
                    pady=(
                        0,
                        6,
                    ),
                )

            if presentation.why:
                tk.Label(
                    host,
                    text=presentation.why,
                    bg=theme.PANEL,
                    fg=theme.INK,
                    wraplength=215,
                    justify="left",
                    anchor="w",
                    font=(
                        theme.FONT_UI,
                        8,
                    ),
                ).pack(
                    fill="x",
                    padx=18,
                    pady=(
                        0,
                        7,
                    ),
                )

            if presentation.proposal:
                tk.Label(
                    host,
                    text=presentation.proposal,
                    bg=theme.PANEL,
                    fg=theme.MUTED,
                    wraplength=215,
                    justify="left",
                    anchor="w",
                    font=(
                        theme.FONT_UI,
                        8,
                    ),
                ).pack(
                    fill="x",
                    padx=18,
                    pady=(
                        0,
                        9,
                    ),
                )

            for option in presentation.choices:
                self._button(
                    host,
                    option.label,
                    lambda value=option.choice: self._v5_survol_choose(
                        value
                    ),
                    compact=True,
                    accent=option.accent,
                    enabled=option.enabled,
                ).pack(
                    fill="x",
                    padx=18,
                    pady=(
                        0,
                        7,
                    ),
                )

            if bool(
                getattr(
                    self,
                    "_v5_final_review_active",
                    False,
                )
            ):
                self._button(
                    host,
                    "Quitter le contrôle final",
                    self._v5_finish_final_review,
                    compact=True,
                ).pack(
                    fill="x",
                    padx=18,
                    pady=(
                        5,
                        7,
                    ),
                )
                return

            if roman.survol.running:
                self._button(
                    host,
                    "Pause",
                    self._survol_pause,
                    compact=True,
                ).pack(
                    fill="x",
                    padx=18,
                    pady=(
                        5,
                        7,
                    ),
                )
            elif roman.survol.started and not roman.survol.completed:
                self._button(
                    host,
                    "Reprendre",
                    self._survol_continue,
                    compact=True,
                ).pack(
                    fill="x",
                    padx=18,
                    pady=(
                        5,
                        7,
                    ),
                )

            self._button(
                host,
                "Arrêter",
                self._survol_stop,
                compact=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(
                    0,
                    7,
                ),
            )
            return

        if (
            roman is not None
            and bool(
                getattr(
                    self,
                    "_v5_final_review_active",
                    False,
                )
            )
        ):
            tk.Label(
                host,
                text="Contrôle final en cours…",
                bg=theme.PANEL,
                fg=theme.MUTED,
                wraplength=215,
                justify="left",
                anchor="w",
                font=(
                    theme.FONT_UI,
                    8,
                    "bold",
                ),
            ).pack(
                fill="x",
                padx=18,
                pady=(
                    0,
                    8,
                ),
            )
            self._button(
                host,
                "Quitter le contrôle final",
                self._v5_finish_final_review,
                compact=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(
                    0,
                    7,
                ),
            )
            return

        if roman is not None and roman.survol.completed:
            pending_review = review_subject_ids(
                roman.review
            )

            if pending_review:
                tk.Label(
                    host,
                    text=(
                        f"{len(pending_review)} élément(s) ont été modifiés "
                        "pendant le Survol et doivent être revus."
                    ),
                    bg=theme.PANEL,
                    fg=theme.INK,
                    wraplength=215,
                    justify="left",
                    anchor="w",
                    font=(
                        theme.FONT_UI,
                        8,
                        "bold",
                    ),
                ).pack(
                    fill="x",
                    padx=18,
                    pady=(
                        0,
                        8,
                    ),
                )
                self._button(
                    host,
                    "Faire le contrôle final",
                    self._v5_start_final_review,
                    compact=True,
                    accent=True,
                ).pack(
                    fill="x",
                    padx=18,
                    pady=(
                        0,
                        7,
                    ),
                )
                return

        if roman is not None and roman.survol.completed:
            self._button(
                host,
                "Recommencer le Survol",
                self._survol_start,
                compact=True,
                accent=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(
                    0,
                    7,
                ),
            )
            return

        if roman is not None and roman.survol.running:
            self._button(
                host,
                "Pause",
                self._survol_pause,
                compact=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(
                    0,
                    7,
                ),
            )
            self._button(
                host,
                "Arrêter",
                self._survol_stop,
                compact=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(
                    0,
                    7,
                ),
            )
            return

        if roman is not None and roman.survol.started:
            self._button(
                host,
                "Reprendre",
                self._survol_continue,
                compact=True,
                accent=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(
                    0,
                    7,
                ),
            )
            self._button(
                host,
                "Arrêter",
                self._survol_stop,
                compact=True,
            ).pack(
                fill="x",
                padx=18,
                pady=(
                    0,
                    7,
                ),
            )
            return

        if bool(
            getattr(
                self,
                "_settings_ui_locked",
                False,
            )
        ):
            tk.Label(
                host,
                text="Validez d'abord les réglages du Livre.",
                bg=theme.PANEL,
                fg=theme.MUTED_DARK,
                wraplength=215,
                justify="left",
                anchor="w",
                font=(
                    theme.FONT_UI,
                    8,
                    "bold",
                ),
            ).pack(
                fill="x",
                padx=18,
                pady=(
                    0,
                    8,
                ),
            )
            return

        self._button(
            host,
            "Commencer le Survol",
            self._survol_start,
            compact=True,
            accent=True,
        ).pack(
            fill="x",
            padx=18,
            pady=(
                0,
                7,
            ),
        )


__all__ = [
    "TomeLineaV5RomanStage",
]