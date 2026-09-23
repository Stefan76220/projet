from __future__ import annotations

import unittest

from tomelinea.book import Book, Page
from tomelinea.navigation import NavigationState
from tomelinea.rules import Situation
from tomelinea.survol import (
    SurvolReviewState,
    SurvolState,
    final_review_plan,
    next_final_review_target,
    request_final_review_page,
)


def add_element(
    page: Page,
    element_id: str,
) -> None:
    page.content.append(
        {
            "id": element_id,
            "kind": "text",
            "geometry": {},
            "payload": {
                "text": element_id,
            },
            "metadata": {},
        }
    )


def complete_main_survol(
    survol: SurvolState,
    book: Book,
) -> None:
    survol.start(
        book
    )

    while survol.running:
        survol.advance(
            book
        )


class V5FinalReviewTests(unittest.TestCase):
    def test_plan_groups_subjects_by_current_physical_page(self) -> None:
        book = Book(
            title="Passage final",
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

        add_element(
            first,
            "element-a",
        )
        add_element(
            first,
            "element-b",
        )

        review = SurvolReviewState()
        review.mark_for_review(
            (
                "element-b",
                second.id,
                "element-a",
            )
        )

        plan = final_review_plan(
            book,
            review,
        )

        self.assertEqual(
            len(plan.targets),
            2,
        )
        self.assertEqual(
            plan.targets[0].page_id,
            first.id,
        )
        self.assertEqual(
            plan.targets[0].subject_ids,
            (
                "element-a",
                "element-b",
            ),
        )
        self.assertEqual(
            plan.targets[1].page_id,
            second.id,
        )

    def test_plan_is_recomputed_after_page_move(self) -> None:
        book = Book(
            title="Ordre vivant",
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

        add_element(
            first,
            "element-a",
        )
        add_element(
            second,
            "element-b",
        )

        review = SurvolReviewState()
        review.mark_for_review(
            (
                "element-a",
                "element-b",
            )
        )

        before = final_review_plan(
            book,
            review,
        )

        book.page_order = [
            second.id,
            first.id,
        ]

        after = final_review_plan(
            book,
            review,
        )

        self.assertEqual(
            before.targets[0].page_id,
            first.id,
        )
        self.assertEqual(
            after.targets[0].page_id,
            second.id,
        )

    def test_missing_subject_is_reported_not_invented(self) -> None:
        book = Book(
            title="Sujet disparu",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )

        review = SurvolReviewState()
        review.mark_for_review(
            (
                "element-disparu",
            )
        )

        plan = final_review_plan(
            book,
            review,
        )

        self.assertTrue(
            plan.empty,
        )
        self.assertEqual(
            plan.unresolved_subject_ids,
            (
                "element-disparu",
            ),
        )

    def test_next_target_never_wraps_backward_automatically(self) -> None:
        book = Book(
            title="Pas de retour",
        )
        pages = [
            Page(
                title=f"Page {index}",
            )
            for index in range(3)
        ]

        for page in pages:
            book.add_page(
                page
            )

        review = SurvolReviewState()
        review.mark_for_review(
            (
                pages[0].id,
                pages[2].id,
            )
        )

        target = next_final_review_target(
            book,
            review,
            after_page_id=pages[2].id,
        )

        self.assertIsNone(
            target
        )

    def test_final_review_cannot_start_before_main_survol_completion(self) -> None:
        book = Book(
            title="Ordre des phases",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )

        navigation = NavigationState()
        survol = SurvolState(
            navigation
        )

        review = SurvolReviewState()
        review.mark_for_review(
            (
                page.id,
            )
        )

        with self.assertRaises(
            ValueError,
        ):
            request_final_review_page(
                survol,
                book,
                review,
            )

    def test_request_uses_exact_same_navigation_state(self) -> None:
        book = Book(
            title="Navigation commune",
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

        navigation = NavigationState()
        survol = SurvolState(
            navigation
        )

        complete_main_survol(
            survol,
            book,
        )

        review = SurvolReviewState()
        review.mark_for_review(
            (
                second.id,
            )
        )

        request = request_final_review_page(
            survol,
            book,
            review,
        )

        self.assertIsNotNone(
            request
        )
        self.assertIs(
            survol.navigation,
            navigation,
        )
        self.assertEqual(
            request.navigation,
            navigation.target,
        )
        self.assertEqual(
            request.navigation.page_id,
            second.id,
        )

    def test_final_review_has_no_persistent_queue(self) -> None:
        from tomelinea.survol import final_review as module

        forbidden_names = {
            "queue",
            "pending_queue",
            "navigation_queue",
            "page_queue",
        }

        names = {
            name.lower()
            for name in dir(
                module
            )
        }

        self.assertTrue(
            forbidden_names.isdisjoint(
                names
            )
        )


if __name__ == "__main__":
    unittest.main()