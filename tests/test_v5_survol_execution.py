from __future__ import annotations

from types import SimpleNamespace
import unittest

from tomelinea.book import Book
from tomelinea.pagination import (
    PAGINATION_CHOICE_ENABLED,
)
from tomelinea.rules import (
    Situation,
    decide,
    group_cases,
)
from tomelinea.survol import (
    REVIEW_METADATA_KEY,
    ReviewStatus,
    SurvolReviewState,
    execute_current_decision,
)
from tomelinea.text import (
    TEXT_CHOICE_IGNORED,
)
import tomelinea.survol.execution as execution


class FakeProject:
    def __init__(self, book) -> None:
        self.book = book


def make_decision(
    situation: Situation,
    choice: str,
):
    case = group_cases(
        [situation]
    )[0]

    return decide(
        case,
        situation.id,
        choice,
    )


class V5SurvolExecutionTests(unittest.TestCase):
    def test_text_decision_is_delegated_then_persisted(self) -> None:
        book = Book(
            title="Survol texte",
        )
        project = FakeProject(
            book
        )

        situation = Situation(
            domain="text",
            kind="widow",
            subject_id="element-1",
            page_id="page-1",
        )

        review = SurvolReviewState()
        review.open_page(
            "page-1",
            (situation,),
        )

        decision = make_decision(
            situation,
            TEXT_CHOICE_IGNORED,
        )

        original = execution.execute_text_decision
        calls = []

        try:
            def fake_execute(
                current_book,
                current_situation,
                current_decision,
            ):
                calls.append(
                    (
                        current_book,
                        current_situation,
                        current_decision,
                    )
                )
                return SimpleNamespace(
                    changed=False,
                )

            execution.execute_text_decision = fake_execute

            result = execute_current_decision(
                project,
                review,
                decision,
            )
        finally:
            execution.execute_text_decision = original

        self.assertEqual(
            len(calls),
            1,
        )
        self.assertIs(
            calls[0][0],
            book,
        )
        self.assertEqual(
            review.status("element-1"),
            ReviewStatus.SEEN,
        )
        self.assertTrue(
            result.page_complete,
        )
        self.assertIn(
            REVIEW_METADATA_KEY,
            book.metadata,
        )

    def test_pagination_decision_is_delegated_to_project_engine(self) -> None:
        book = Book(
            title="Survol pagination",
        )
        project = FakeProject(
            book
        )

        situation = Situation(
            domain="pagination",
            kind="page_right",
            subject_id="page-1",
            page_id="page-1",
        )

        review = SurvolReviewState()
        review.open_page(
            "page-1",
            (situation,),
        )

        decision = make_decision(
            situation,
            PAGINATION_CHOICE_ENABLED,
        )

        original = execution.execute_pagination_decision
        calls = []

        try:
            def fake_execute(
                current_project,
                current_situation,
                current_decision,
            ):
                calls.append(
                    (
                        current_project,
                        current_situation,
                        current_decision,
                    )
                )
                return SimpleNamespace(
                    changed_page_ids=("page-1",),
                )

            execution.execute_pagination_decision = fake_execute

            result = execute_current_decision(
                project,
                review,
                decision,
            )
        finally:
            execution.execute_pagination_decision = original

        self.assertEqual(
            len(calls),
            1,
        )
        self.assertIs(
            calls[0][0],
            project,
        )
        self.assertEqual(
            result.domain,
            "pagination",
        )
        self.assertTrue(
            result.page_complete,
        )

    def test_failed_domain_execution_does_not_advance_or_persist(self) -> None:
        book = Book(
            title="Survol echec",
        )
        project = FakeProject(
            book
        )

        situation = Situation(
            domain="text",
            kind="widow",
            subject_id="element-1",
            page_id="page-1",
        )

        review = SurvolReviewState()
        review.open_page(
            "page-1",
            (situation,),
        )

        decision = make_decision(
            situation,
            TEXT_CHOICE_IGNORED,
        )

        original = execution.execute_text_decision

        try:
            def fail(*args, **kwargs):
                raise ValueError(
                    "echec moteur",
                )

            execution.execute_text_decision = fail

            with self.assertRaises(
                ValueError,
            ):
                execute_current_decision(
                    project,
                    review,
                    decision,
                )
        finally:
            execution.execute_text_decision = original

        self.assertEqual(
            review.current_situation.id,
            situation.id,
        )
        self.assertEqual(
            review.status("element-1"),
            ReviewStatus.NEW,
        )
        self.assertNotIn(
            REVIEW_METADATA_KEY,
            book.metadata,
        )

    def test_only_one_situation_is_completed_inside_same_case(self) -> None:
        book = Book(
            title="Survol deux situations",
        )
        project = FakeProject(
            book
        )

        first = Situation(
            domain="text",
            kind="widow",
            subject_id="element-1",
            page_id="page-1",
        )
        second = Situation(
            domain="text",
            kind="hyphenation",
            subject_id="element-1",
            page_id="page-1",
        )

        review = SurvolReviewState()
        review.open_page(
            "page-1",
            (
                first,
                second,
            ),
        )

        decision = make_decision(
            first,
            TEXT_CHOICE_IGNORED,
        )

        original = execution.execute_text_decision

        try:
            execution.execute_text_decision = (
                lambda *args, **kwargs: SimpleNamespace(
                    changed=False,
                )
            )

            result = execute_current_decision(
                project,
                review,
                decision,
            )
        finally:
            execution.execute_text_decision = original

        self.assertFalse(
            result.page_complete,
        )
        self.assertEqual(
            review.current_situation.id,
            second.id,
        )

    def test_decision_must_target_current_survol_situation(self) -> None:
        book = Book(
            title="Survol cible",
        )
        project = FakeProject(
            book
        )

        first = Situation(
            domain="text",
            kind="widow",
            subject_id="element-1",
            page_id="page-1",
        )
        second = Situation(
            domain="text",
            kind="widow",
            subject_id="element-2",
            page_id="page-1",
        )

        review = SurvolReviewState()
        review.open_page(
            "page-1",
            (
                first,
                second,
            ),
        )

        wrong = make_decision(
            second,
            TEXT_CHOICE_IGNORED,
        )

        with self.assertRaises(
            ValueError,
        ):
            execute_current_decision(
                project,
                review,
                wrong,
            )

        self.assertEqual(
            review.current_situation.id,
            first.id,
        )

    def test_unknown_domain_is_not_marked_seen(self) -> None:
        book = Book(
            title="Survol domaine",
        )
        project = FakeProject(
            book
        )

        situation = Situation(
            domain="image",
            kind="future_case",
            subject_id="image-1",
            page_id="page-1",
        )

        review = SurvolReviewState()
        review.open_page(
            "page-1",
            (situation,),
        )

        decision = make_decision(
            situation,
            "accepted",
        )

        with self.assertRaises(
            ValueError,
        ):
            execute_current_decision(
                project,
                review,
                decision,
            )

        self.assertEqual(
            review.status("image-1"),
            ReviewStatus.NEW,
        )
        self.assertNotIn(
            REVIEW_METADATA_KEY,
            book.metadata,
        )

    def test_execution_layer_has_no_navigation_object(self) -> None:
        forbidden = (
            "navigation",
            "queue",
            "canvas",
            "webview",
            "activate_page",
            "go_to_page",
        )

        names = {
            name.lower()
            for name in dir(execution)
        }

        for name in forbidden:
            self.assertNotIn(
                name,
                names,
            )


if __name__ == "__main__":
    unittest.main()