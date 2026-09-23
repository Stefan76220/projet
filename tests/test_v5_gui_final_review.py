from __future__ import annotations

from types import SimpleNamespace
import unittest
from unittest.mock import patch

from src.gui_v5.roman_shell import TomeLineaV5RomanStage

from tomelinea.book import Book, Page
from tomelinea.project_types.roman import (
    RomanReviewPreparation,
    RomanSession,
)
from tomelinea.rules import Situation


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


def make_shell(
    book: Book,
):
    project = FakeProject(
        book
    )
    shell = object.__new__(
        TomeLineaV5RomanStage
    )
    shell.session = SimpleNamespace(
        project=project,
        book=book,
        active_page_id=None,
    )
    shell._v5_roman_session = None
    shell._v5_roman_project = None
    shell._v5_roman_book = None
    shell._v5_survol_last_error = ""
    shell._v5_final_review_active = False
    shell._v5_final_review_page_id = ""
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


def complete_main_survol(
    shell,
    preparation,
):
    roman = shell._v5_ensure_roman_session()
    roman._preparation = preparation

    target = roman.start()

    while target is not None:
        roman.page_visible(
            target.page_id
        )

        if not roman.review.page_complete:
            raise AssertionError(
                "La preparation du test doit permettre de finir le Survol principal."
            )

        target = roman.advance()

    shell._v5_sync_survol_flags(
        roman
    )
    return roman


class V5GuiFinalReviewTests(unittest.TestCase):
    def test_main_completion_never_starts_backward_review_automatically(self) -> None:
        book = Book(
            title="Pas de retour automatique",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )

        shell = make_shell(
            book
        )
        roman = complete_main_survol(
            shell,
            empty_preparation(),
        )

        roman.review.mark_for_review(
            (
                page.id,
            )
        )

        generation_before = roman.navigation.generation

        with patch.object(
            RomanSession,
            "final_review",
            wraps=roman.final_review,
        ) as final_review:
            shell._survol_refresh_panel = lambda: None

            self.assertTrue(
                roman.survol.completed
            )
            self.assertFalse(
                shell._v5_final_review_active
            )
            self.assertEqual(
                roman.navigation.generation,
                generation_before,
            )
            final_review.assert_not_called()

    def test_explicit_final_review_reuses_same_navigation_once(self) -> None:
        book = Book(
            title="Controle explicite",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )

        shell = make_shell(
            book
        )
        roman = complete_main_survol(
            shell,
            empty_preparation(),
        )

        roman.review.mark_for_review(
            (
                page.id,
            )
        )

        generation_before = roman.navigation.generation
        rendered = []
        scheduled = []

        with patch.object(
            TomeLineaV5RomanStage,
            "_survol_refresh_panel",
            return_value=None,
        ), patch.object(
            TomeLineaV5RomanStage,
            "_survol_set_click_hook_active",
            return_value=None,
        ), patch.object(
            TomeLineaV5RomanStage,
            "_v5_apply_navigation_target",
            side_effect=lambda page_id, **kwargs: rendered.append(
                page_id
            ),
        ), patch.object(
            TomeLineaV5RomanStage,
            "_v5_schedule_final_visible",
            side_effect=lambda generation, page_id: scheduled.append(
                (
                    generation,
                    page_id,
                )
            ),
        ):
            shell._v5_start_final_review()

        self.assertTrue(
            shell._v5_final_review_active
        )
        self.assertEqual(
            shell._v5_final_review_page_id,
            page.id,
        )
        self.assertEqual(
            roman.navigation.generation,
            generation_before + 1,
        )
        self.assertEqual(
            rendered,
            [
                page.id,
            ],
        )
        self.assertEqual(
            scheduled[0][1],
            page.id,
        )
        self.assertIs(
            roman.survol.navigation,
            roman.navigation,
        )

    def test_final_visible_page_reopens_forced_case(self) -> None:
        book = Book(
            title="Cas A revoir",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
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

        shell = make_shell(
            book
        )
        roman = complete_main_survol(
            shell,
            empty_preparation(),
        )

        roman._preparation = preparation
        roman.review.mark_seen(
            (
                situation,
            )
        )
        roman.review.mark_for_review(
            (
                situation.subject_id,
            )
        )

        shell._v5_final_review_active = True
        shell._v5_final_review_page_id = page.id

        with patch.object(
            TomeLineaV5RomanStage,
            "_survol_refresh_panel",
            return_value=None,
        ), patch.object(
            TomeLineaV5RomanStage,
            "_v5_schedule_final_dwell",
            return_value=None,
        ):
            shell._v5_on_final_page_visible(
                1,
                page.id,
            )

        self.assertEqual(
            roman.review.current_situation.id,
            situation.id,
        )

    def test_completed_final_case_schedules_final_dwell_not_main_dwell(self) -> None:
        book = Book(
            title="Decision controle final",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
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

        shell = make_shell(
            book
        )
        roman = complete_main_survol(
            shell,
            empty_preparation(),
        )

        roman._preparation = preparation
        roman.review.mark_seen(
            (
                situation,
            )
        )
        roman.review.mark_for_review(
            (
                situation.subject_id,
            )
        )
        roman.page_visible(
            page.id
        )

        shell._v5_final_review_active = True
        shell._v5_final_review_page_id = page.id

        final_dwell = []
        main_dwell = []

        def fake_execute(
            current_self,
            decision,
        ):
            current_self.review.complete_current_situation()
            return SimpleNamespace(
                review=current_self.review.snapshot,
            )

        with patch.object(
            RomanSession,
            "execute",
            new=fake_execute,
        ), patch.object(
            TomeLineaV5RomanStage,
            "_survol_refresh_panel",
            return_value=None,
        ), patch.object(
            TomeLineaV5RomanStage,
            "_v5_schedule_final_dwell",
            side_effect=lambda generation: final_dwell.append(
                generation
            ),
        ), patch.object(
            TomeLineaV5RomanStage,
            "_v5_schedule_dwell",
            side_effect=lambda generation: main_dwell.append(
                generation
            ),
        ):
            shell._v5_survol_choose(
                "ignored"
            )

        self.assertEqual(
            len(final_dwell),
            1,
        )
        self.assertEqual(
            main_dwell,
            [],
        )

    def test_final_review_moves_forward_in_current_physical_order(self) -> None:
        book = Book(
            title="Ordre final",
        )
        pages = [
            Page(
                title=f"Page {index + 1}",
            )
            for index in range(3)
        ]

        for page in pages:
            book.add_page(
                page
            )

        shell = make_shell(
            book
        )
        roman = complete_main_survol(
            shell,
            empty_preparation(),
        )

        roman.review.mark_for_review(
            (
                pages[0].id,
                pages[2].id,
            )
        )

        request = roman.final_review()

        self.assertEqual(
            request.target.page_id,
            pages[0].id,
        )

        roman.review.clear_review_flag(
            pages[0].id
        )

        shell._v5_final_review_active = True
        shell._v5_final_review_page_id = pages[0].id

        rendered = []

        with patch.object(
            TomeLineaV5RomanStage,
            "_survol_refresh_panel",
            return_value=None,
        ), patch.object(
            TomeLineaV5RomanStage,
            "_survol_set_click_hook_active",
            return_value=None,
        ), patch.object(
            TomeLineaV5RomanStage,
            "_v5_apply_navigation_target",
            side_effect=lambda page_id, **kwargs: rendered.append(
                page_id
            ),
        ), patch.object(
            TomeLineaV5RomanStage,
            "_v5_schedule_final_visible",
            return_value=None,
        ):
            shell._v5_advance_final_review()

        self.assertEqual(
            shell._v5_final_review_page_id,
            pages[2].id,
        )
        self.assertEqual(
            rendered,
            [
                pages[2].id,
            ],
        )

    def test_final_review_never_wraps_backward_automatically(self) -> None:
        book = Book(
            title="Pas de boucle",
        )
        pages = [
            Page(
                title=f"Page {index + 1}",
            )
            for index in range(3)
        ]

        for page in pages:
            book.add_page(
                page
            )

        shell = make_shell(
            book
        )
        roman = complete_main_survol(
            shell,
            empty_preparation(),
        )

        roman.review.mark_for_review(
            (
                pages[0].id,
            )
        )

        shell._v5_final_review_active = True
        shell._v5_final_review_page_id = pages[2].id

        with patch.object(
            TomeLineaV5RomanStage,
            "_survol_refresh_panel",
            return_value=None,
        ), patch.object(
            TomeLineaV5RomanStage,
            "_survol_set_click_hook_active",
            return_value=None,
        ):
            shell._v5_advance_final_review()

        self.assertFalse(
            shell._v5_final_review_active
        )
        self.assertIn(
            "Aucun retour automatique en arrière",
            shell._survol_message,
        )
        self.assertTrue(
            roman.survol.completed
        )


if __name__ == "__main__":
    unittest.main()