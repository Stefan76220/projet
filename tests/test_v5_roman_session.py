from __future__ import annotations

from types import SimpleNamespace
import unittest
from unittest.mock import patch

from tomelinea.book import Book, Page
from tomelinea.navigation import NavigationState
from tomelinea.project_types.roman import (
    RomanReviewPreparation,
    RomanSession,
)
from tomelinea.rules import (
    Situation,
    decide,
    group_cases,
)
from tomelinea.survol import (
    ReviewStatus,
    SurvolDecisionExecution,
    SurvolReviewState,
    save_review_state,
)


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


class V5RomanSessionTests(unittest.TestCase):
    def test_session_owns_one_shared_navigation_used_by_survol(self) -> None:
        book = Book(
            title="Session Roman",
        )
        book.add_page(
            Page(
                title="Page",
            )
        )

        navigation = NavigationState()
        session = RomanSession(
            FakeProject(
                book
            ),
            navigation=navigation,
        )

        self.assertIs(
            session.navigation,
            navigation,
        )
        self.assertIs(
            session.survol.navigation,
            navigation,
        )

    def test_session_restores_durable_review_from_book(self) -> None:
        book = Book(
            title="Revue persistante",
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
            subject_id="element-1",
            page_id=page.id,
        )

        previous = SurvolReviewState()
        previous.mark_seen(
            (situation,)
        )
        save_review_state(
            book,
            previous,
        )

        session = RomanSession(
            FakeProject(
                book
            )
        )

        self.assertEqual(
            session.review.status(
                "element-1"
            ),
            ReviewStatus.SEEN,
        )

    def test_start_prepares_then_requests_first_page(self) -> None:
        book = Book(
            title="Demarrage Roman",
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

        session = RomanSession(
            FakeProject(
                book
            )
        )

        with patch(
            "tomelinea.project_types.roman.session.prepare_roman_review",
            return_value=empty_preparation(),
        ):
            target = session.start()

        self.assertTrue(
            session.prepared,
        )
        self.assertEqual(
            target.page_id,
            first.id,
        )
        self.assertEqual(
            session.navigation.target,
            target,
        )

    def test_page_visible_opens_common_review_only_after_render_confirmation(self) -> None:
        book = Book(
            title="Page visible",
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
            subject_id="element-1",
            page_id=page.id,
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

        session = RomanSession(
            FakeProject(
                book
            )
        )

        with patch(
            "tomelinea.project_types.roman.session.prepare_roman_review",
            return_value=preparation,
        ):
            target = session.start()

        self.assertEqual(
            session.review.page_id,
            "",
        )

        snapshot = session.page_visible(
            target.page_id
        )

        self.assertEqual(
            snapshot.current_situation.id,
            situation.id,
        )

    def test_advance_is_blocked_while_page_has_pending_case(self) -> None:
        book = Book(
            title="Blocage page",
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
            subject_id="element-1",
            page_id=page.id,
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

        session = RomanSession(
            FakeProject(
                book
            )
        )

        with patch(
            "tomelinea.project_types.roman.session.prepare_roman_review",
            return_value=preparation,
        ):
            target = session.start()

        session.page_visible(
            target.page_id
        )

        with self.assertRaises(
            ValueError,
        ):
            session.advance()

    def test_execute_delegates_to_common_engine_and_refreshes_same_page(self) -> None:
        book = Book(
            title="Decision Roman",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )

        first = Situation(
            domain="text",
            kind="widow",
            subject_id="element-1",
            page_id=page.id,
        )
        second = Situation(
            domain="image",
            kind="image_quality_critical",
            subject_id="image-1",
            page_id=page.id,
        )

        initial = RomanReviewPreparation(
            text_rules={},
            text_rules_created=False,
            automatic_text_corrections=(),
            situations=(
                first,
                second,
            ),
            unresolved_situations=(),
        )

        refreshed = RomanReviewPreparation(
            text_rules={},
            text_rules_created=False,
            automatic_text_corrections=(),
            situations=(
                first,
                second,
            ),
            unresolved_situations=(),
        )

        session = RomanSession(
            FakeProject(
                book
            )
        )

        with patch(
            "tomelinea.project_types.roman.session.prepare_roman_review",
            return_value=initial,
        ):
            target = session.start()

        session.page_visible(
            target.page_id
        )

        case = group_cases(
            (first,)
        )[0]
        decision = decide(
            case,
            first.id,
            "ignored",
        )

        def fake_execute(
            project,
            review,
            current_decision,
        ):
            review.complete_current_situation()
            return SimpleNamespace(
                domain="text",
                page_complete=False,
            )

        with patch(
            "tomelinea.project_types.roman.session.execute_current_decision",
            side_effect=fake_execute,
        ) as execute_mock, patch(
            "tomelinea.project_types.roman.session.prepare_roman_review",
            return_value=refreshed,
        ):
            result = session.execute(
                decision
            )

        execute_mock.assert_called_once()
        self.assertEqual(
            result.review.current_situation.id,
            second.id,
        )
        self.assertEqual(
            result.review.page_id,
            page.id,
        )

    def test_completed_main_survol_uses_same_navigation_for_final_review(self) -> None:
        book = Book(
            title="Passage final Session",
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

        session = RomanSession(
            FakeProject(
                book
            )
        )

        with patch(
            "tomelinea.project_types.roman.session.prepare_roman_review",
            return_value=empty_preparation(),
        ):
            target = session.start()

        session.page_visible(
            target.page_id
        )

        second_target = session.advance()
        session.page_visible(
            second_target.page_id
        )

        end = session.advance()

        self.assertIsNone(
            end
        )
        self.assertTrue(
            session.survol.completed,
        )

        session.review.mark_for_review(
            (
                first.id,
            )
        )

        request = session.final_review()

        self.assertIsNotNone(
            request
        )
        self.assertEqual(
            request.target.page_id,
            first.id,
        )
        self.assertEqual(
            request.navigation,
            session.navigation.target,
        )
        self.assertIs(
            session.survol.navigation,
            session.navigation,
        )

    def test_session_has_no_gui_or_second_navigation_engine(self) -> None:
        import tomelinea.project_types.roman.session as module

        names = {
            name.lower()
            for name in dir(
                module
            )
        }

        forbidden = {
            "tk",
            "tkinter",
            "webview",
            "canvas",
            "navigationqueue",
            "pagequeue",
        }

        self.assertTrue(
            forbidden.isdisjoint(
                names
            )
        )


if __name__ == "__main__":
    unittest.main()