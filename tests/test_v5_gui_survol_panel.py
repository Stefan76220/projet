from __future__ import annotations

from types import SimpleNamespace
import unittest
from unittest.mock import patch

from src.gui_v4.settings_shell import TomeLineaV4SettingsStage
from src.gui_v5.roman_shell import TomeLineaV5RomanStage
from src.gui_v5.survol_presenter import (
    decision_for_current,
    presentation_for_situation,
)

from tomelinea.book import Book, Page
from tomelinea.project_types.roman import (
    RomanReviewPreparation,
    RomanSession,
)
from tomelinea.rules import Situation
from tomelinea.survol import SurvolReviewState


class FakeProject:
    def __init__(self, book) -> None:
        self.book = book
        self.touch_count = 0

    def touch(self) -> None:
        self.touch_count += 1


def empty_preparation():
    return RomanReviewPreparation(
        text_rules={},
        text_rules_created=False,
        automatic_text_corrections=(),
        situations=(),
        unresolved_situations=(),
    )


def shell_for(
    project,
):
    shell = object.__new__(
        TomeLineaV5RomanStage
    )
    shell.session = SimpleNamespace(
        project=project,
        book=project.book,
        active_page_id=None,
    )
    shell._v5_roman_session = None
    shell._v5_roman_project = None
    shell._v5_roman_book = None
    shell._v5_survol_last_error = ""
    shell._settings_ui_locked = False
    shell._survol_running = False
    shell._survol_started = False
    shell._survol_completed = False
    shell._survol_position = 0
    shell._survol_generation = 0
    shell._survol_expected_global_index = None
    shell._survol_watch_after_id = None
    shell._survol_dwell_after_id = None
    shell._survol_dwell_ms = 2000
    shell._survol_message = ""
    return shell


class V5SurvolPresenterTests(unittest.TestCase):
    def test_text_without_safe_correction_disables_corriger(self) -> None:
        situation = Situation(
            domain="text",
            kind="widow",
            subject_id="text-1",
            page_id="page-1",
            facts={
                "title": "Une ligne est isolée",
                "correction_supported": False,
            },
        )

        presentation = presentation_for_situation(
            situation
        )

        self.assertEqual(
            presentation.choices[0].label,
            "Corriger",
        )
        self.assertFalse(
            presentation.choices[0].enabled,
        )
        self.assertEqual(
            presentation.choices[1].label,
            "Laisser comme ça",
        )

    def test_critical_image_can_offer_corriger(self) -> None:
        situation = Situation(
            domain="image",
            kind="image_quality_critical",
            subject_id="image-1",
            page_id="page-1",
        )

        presentation = presentation_for_situation(
            situation
        )

        self.assertTrue(
            presentation.choices[0].enabled,
        )
        self.assertEqual(
            presentation.choices[0].choice,
            "corrected",
        )

    def test_limited_image_does_not_offer_fake_automatic_correction(self) -> None:
        situation = Situation(
            domain="image",
            kind="image_quality_limited",
            subject_id="image-1",
            page_id="page-1",
        )

        presentation = presentation_for_situation(
            situation
        )

        self.assertFalse(
            presentation.choices[0].enabled,
        )
        self.assertTrue(
            presentation.choices[1].enabled,
        )

    def test_cover_uses_exact_content_blank_choices(self) -> None:
        situation = Situation(
            domain="cover",
            kind="inside_cover_confirmation",
            subject_id="cover-2",
            page_id="candidate",
            facts={
                "candidate_page_id": "candidate",
            },
        )

        presentation = presentation_for_situation(
            situation
        )

        self.assertEqual(
            [
                item.choice
                for item in presentation.choices
            ],
            [
                "content",
                "blank",
            ],
        )

    def test_decision_is_created_from_current_common_case(self) -> None:
        review = SurvolReviewState()
        situation = Situation(
            domain="image",
            kind="image_quality_critical",
            subject_id="image-1",
            page_id="page-1",
        )
        review.open_page(
            "page-1",
            (
                situation,
            ),
        )

        decision = decision_for_current(
            review,
            "ignored",
        )

        self.assertEqual(
            decision.situation_id,
            situation.id,
        )
        self.assertEqual(
            decision.subject_id,
            "image-1",
        )


class V5GuiSurvolDecisionTests(unittest.TestCase):
    def test_start_uses_roman_session_target_without_second_navigation_request(self) -> None:
        book = Book(
            title="Survol GUI",
        )
        first = Page(
            title="Premiere",
        )
        second = Page(
            title="Deuxieme",
        )
        book.add_page(
            first
        )
        book.add_page(
            second
        )

        project = FakeProject(
            book
        )
        shell = shell_for(
            project
        )

        rendered = []
        scheduled = []

        with patch(
            "tomelinea.project_types.roman.session.prepare_roman_review",
            return_value=empty_preparation(),
        ), patch.object(
            TomeLineaV5RomanStage,
            "_v5_apply_navigation_target",
            side_effect=lambda page_id, **kwargs: rendered.append(page_id),
        ), patch.object(
            TomeLineaV5RomanStage,
            "_survol_refresh_panel",
            return_value=None,
        ), patch.object(
            TomeLineaV5RomanStage,
            "_survol_attach_click_hook",
            return_value=None,
        ), patch.object(
            TomeLineaV5RomanStage,
            "_v5_schedule_visible",
            side_effect=lambda generation, page_id: scheduled.append(
                (
                    generation,
                    page_id,
                )
            ),
        ):
            shell._survol_start()

        roman = shell.v5_roman_session

        self.assertIsNotNone(
            roman
        )
        self.assertEqual(
            roman.navigation.generation,
            1,
        )
        self.assertEqual(
            rendered,
            [
                first.id,
            ],
        )
        self.assertEqual(
            scheduled[0][1],
            first.id,
        )

    def test_visible_page_with_case_waits_for_decision(self) -> None:
        book = Book(
            title="Arret sur Cas",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )

        project = FakeProject(
            book
        )
        shell = shell_for(
            project
        )

        situation = Situation(
            domain="text",
            kind="widow",
            subject_id="text-1",
            page_id=page.id,
            facts={
                "correction_supported": False,
            },
        )

        preparation = RomanReviewPreparation(
            text_rules={},
            text_rules_created=False,
            automatic_text_corrections=(),
            situations=(
                situation,
            ),
            unresolved_situations=(),
        )

        dwell_calls = []

        with patch(
            "tomelinea.project_types.roman.session.prepare_roman_review",
            return_value=preparation,
        ), patch.object(
            TomeLineaV5RomanStage,
            "_v5_apply_navigation_target",
            return_value=None,
        ), patch.object(
            TomeLineaV5RomanStage,
            "_survol_refresh_panel",
            return_value=None,
        ), patch.object(
            TomeLineaV5RomanStage,
            "_survol_attach_click_hook",
            return_value=None,
        ), patch.object(
            TomeLineaV5RomanStage,
            "_v5_schedule_visible",
            return_value=None,
        ), patch.object(
            TomeLineaV5RomanStage,
            "_v5_schedule_dwell",
            side_effect=lambda generation: dwell_calls.append(generation),
        ):
            shell._survol_start()
            generation = shell._survol_generation
            shell._v5_on_page_visible(
                generation,
                page.id,
            )

        self.assertEqual(
            shell.v5_roman_session.review.current_situation.id,
            situation.id,
        )
        self.assertEqual(
            dwell_calls,
            [],
        )

    def test_visible_page_without_case_schedules_normal_dwell(self) -> None:
        book = Book(
            title="Page simple",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )

        project = FakeProject(
            book
        )
        shell = shell_for(
            project
        )

        dwell_calls = []

        with patch(
            "tomelinea.project_types.roman.session.prepare_roman_review",
            return_value=empty_preparation(),
        ), patch.object(
            TomeLineaV5RomanStage,
            "_v5_apply_navigation_target",
            return_value=None,
        ), patch.object(
            TomeLineaV5RomanStage,
            "_survol_refresh_panel",
            return_value=None,
        ), patch.object(
            TomeLineaV5RomanStage,
            "_survol_attach_click_hook",
            return_value=None,
        ), patch.object(
            TomeLineaV5RomanStage,
            "_v5_schedule_visible",
            return_value=None,
        ), patch.object(
            TomeLineaV5RomanStage,
            "_v5_schedule_dwell",
            side_effect=lambda generation: dwell_calls.append(generation),
        ):
            shell._survol_start()
            generation = shell._survol_generation
            shell._v5_on_page_visible(
                generation,
                page.id,
            )

        self.assertEqual(
            len(dwell_calls),
            1,
        )
        self.assertTrue(
            shell.v5_roman_session.review.page_complete,
        )

    def test_v5_shell_overrides_old_observation_survol_entry_points(self) -> None:
        own = TomeLineaV5RomanStage.__dict__

        for name in (
            "_survol_start",
            "_survol_wait_visible",
            "_survol_advance",
            "_survol_pause",
            "_survol_continue",
            "_survol_stop",
            "_survol_render_panel",
        ):
            self.assertIn(
                name,
                own,
            )

        self.assertIsNot(
            TomeLineaV5RomanStage._survol_start,
            TomeLineaV4SettingsStage._survol_start,
        )


if __name__ == "__main__":
    unittest.main()