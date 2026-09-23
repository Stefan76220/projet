from __future__ import annotations

import unittest

from tomelinea.rules import Situation
from tomelinea.survol import (
    ReviewStatus,
    SurvolReviewState,
)


def situation(
    kind: str,
    subject_id: str,
    page_id: str = "page-1",
    qualifier: str = "",
) -> Situation:
    return Situation(
        domain="text",
        kind=kind,
        subject_id=subject_id,
        page_id=page_id,
        qualifier=qualifier,
    )


class V5SurvolReviewTests(unittest.TestCase):
    def test_same_object_is_one_case_and_situations_are_sequential(self) -> None:
        review = SurvolReviewState()

        first = situation(
            "widow",
            "element-1",
        )
        second = situation(
            "hyphenation",
            "element-1",
        )

        snapshot = review.open_page(
            "page-1",
            (
                first,
                second,
            ),
        )

        self.assertEqual(
            snapshot.case_count,
            1,
        )
        self.assertEqual(
            snapshot.situation_count,
            2,
        )
        self.assertEqual(
            snapshot.current_situation.id,
            first.id,
        )

        snapshot = review.complete_current_situation()

        self.assertFalse(
            snapshot.page_complete,
        )
        self.assertEqual(
            snapshot.current_situation.id,
            second.id,
        )

        snapshot = review.complete_current_situation()

        self.assertTrue(
            snapshot.page_complete,
        )
        self.assertEqual(
            review.status("element-1"),
            ReviewStatus.SEEN,
        )

    def test_page_is_complete_only_after_every_case_is_processed(self) -> None:
        review = SurvolReviewState()

        review.open_page(
            "page-1",
            (
                situation(
                    "widow",
                    "element-1",
                ),
                situation(
                    "style_outlier",
                    "element-2",
                ),
            ),
        )

        self.assertFalse(
            review.page_complete,
        )

        review.complete_current_situation()

        self.assertFalse(
            review.page_complete,
        )
        self.assertEqual(
            review.current_case.subject_id,
            "element-2",
        )

        review.complete_current_situation()

        self.assertTrue(
            review.page_complete,
        )

    def test_seen_case_does_not_stop_next_survol(self) -> None:
        review = SurvolReviewState()
        item = situation(
            "widow",
            "element-1",
        )

        review.open_page(
            "page-1",
            (item,),
        )
        review.complete_current_situation()

        snapshot = review.open_page(
            "page-1",
            (item,),
        )

        self.assertTrue(
            snapshot.page_complete,
        )
        self.assertEqual(
            review.status("element-1"),
            ReviewStatus.SEEN,
        )

    def test_new_situation_on_seen_subject_is_new(self) -> None:
        review = SurvolReviewState()

        first = situation(
            "widow",
            "element-1",
        )

        review.open_page(
            "page-1",
            (first,),
        )
        review.complete_current_situation()

        second = situation(
            "hyphenation",
            "element-1",
        )

        snapshot = review.open_page(
            "page-1",
            (
                first,
                second,
            ),
        )

        self.assertFalse(
            snapshot.page_complete,
        )
        self.assertEqual(
            snapshot.current_situation.id,
            second.id,
        )
        self.assertEqual(
            review.case_status(snapshot.current_case),
            ReviewStatus.NEW,
        )

    def test_mark_for_review_reopens_seen_case_without_navigation(self) -> None:
        review = SurvolReviewState()

        item = situation(
            "widow",
            "element-1",
        )

        review.open_page(
            "page-1",
            (item,),
        )
        review.complete_current_situation()

        page_before = review.page_id

        review.mark_for_review(
            ("element-1",)
        )

        self.assertEqual(
            review.status("element-1"),
            ReviewStatus.REVIEW,
        )
        self.assertEqual(
            review.page_id,
            page_before,
        )

        snapshot = review.open_page(
            "page-1",
            (item,),
        )

        self.assertFalse(
            snapshot.page_complete,
        )
        self.assertEqual(
            review.case_status(snapshot.current_case),
            ReviewStatus.REVIEW,
        )

    def test_mark_seen_supports_rules_extended_to_other_cases(self) -> None:
        review = SurvolReviewState()

        target = situation(
            "widow",
            "element-2",
            page_id="page-2",
        )

        review.mark_seen(
            (target,)
        )

        self.assertEqual(
            review.status("element-2"),
            ReviewStatus.SEEN,
        )

        snapshot = review.open_page(
            "page-2",
            (target,),
        )

        self.assertTrue(
            snapshot.page_complete,
        )

    def test_page_filter_keeps_physical_survol_order_external(self) -> None:
        review = SurvolReviewState()

        page_1 = situation(
            "widow",
            "element-1",
            page_id="page-1",
        )
        page_2 = situation(
            "widow",
            "element-2",
            page_id="page-2",
        )

        snapshot = review.open_page(
            "page-2",
            (
                page_1,
                page_2,
            ),
        )

        self.assertEqual(
            snapshot.case_count,
            1,
        )
        self.assertEqual(
            snapshot.current_case.subject_id,
            "element-2",
        )

    def test_review_state_has_no_parallel_navigation_engine(self) -> None:
        review = SurvolReviewState()

        forbidden = {
            "navigation",
            "page_order",
            "queue",
            "requests",
            "canvas",
            "webview",
            "go_to_page",
            "activate_page",
        }

        names = {
            str(name).lower()
            for name in SurvolReviewState.__slots__
        }

        self.assertTrue(
            forbidden.isdisjoint(
                names
            )
        )

        for name in forbidden:
            self.assertFalse(
                hasattr(
                    review,
                    name,
                )
            )


if __name__ == "__main__":
    unittest.main()