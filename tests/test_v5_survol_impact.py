from __future__ import annotations

from types import SimpleNamespace
import unittest

from tomelinea.book import Book, Page
from tomelinea.rules import Situation, decide, group_cases
from tomelinea.survol import (
    ReviewStatus,
    SurvolReviewState,
    book_impact_snapshot,
    changed_subject_ids,
    execute_current_decision,
    impacted_seen_subject_ids,
)
from tomelinea.text import TEXT_CHOICE_IGNORED
import tomelinea.survol.execution as execution


class FakeProject:
    def __init__(self, book) -> None:
        self.book = book


def add_text_element(
    page: Page,
    element_id: str,
    *,
    text: str = "Texte",
    y_mm: float = 20.0,
) -> dict:
    element = {
        "id": element_id,
        "kind": "text",
        "geometry": {
            "x_mm": 15.0,
            "y_mm": y_mm,
            "width_mm": 100.0,
            "height_mm": 10.0,
        },
        "payload": {
            "text": text,
        },
        "metadata": {},
    }
    page.content.append(
        element
    )
    return element


def make_decision(
    situation: Situation,
    choice: str = TEXT_CHOICE_IGNORED,
):
    case = group_cases(
        [situation]
    )[0]
    return decide(
        case,
        situation.id,
        choice,
    )


class V5SurvolImpactTests(unittest.TestCase):
    def test_moved_seen_element_is_detected_by_stable_id(self) -> None:
        book = Book(
            title="Impact element",
        )
        page = Page(
            title="Page 1",
        )
        book.add_page(
            page
        )
        element = add_text_element(
            page,
            "element-2",
        )

        before = book_impact_snapshot(
            book
        )
        element["geometry"]["y_mm"] = 42.0
        after = book_impact_snapshot(
            book
        )

        self.assertEqual(
            changed_subject_ids(
                before,
                after,
                ("element-2",),
            ),
            ("element-2",),
        )

    def test_physical_page_shift_impacts_seen_page_and_its_element(self) -> None:
        book = Book(
            title="Impact parite",
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
        add_text_element(
            second,
            "element-2",
        )

        before = book_impact_snapshot(
            book
        )

        inserted = Page(
            title="Intercalee",
        )
        book.pages[
            inserted.id
        ] = inserted
        book.page_order.insert(
            0,
            inserted.id,
        )

        after = book_impact_snapshot(
            book
        )

        changed = changed_subject_ids(
            before,
            after,
            (
                second.id,
                "element-2",
            ),
        )

        self.assertEqual(
            set(changed),
            {
                second.id,
                "element-2",
            },
        )

    def test_only_seen_subjects_are_candidates_for_review(self) -> None:
        book = Book(
            title="Impact vus",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )
        seen_element = add_text_element(
            page,
            "seen-element",
        )
        new_element = add_text_element(
            page,
            "new-element",
            y_mm=40.0,
        )

        review = SurvolReviewState()

        seen_situation = Situation(
            "text",
            "widow",
            "seen-element",
            page.id,
        )
        review.mark_seen(
            (seen_situation,)
        )

        before = book_impact_snapshot(
            book
        )

        seen_element["geometry"]["y_mm"] = 25.0
        new_element["geometry"]["y_mm"] = 45.0

        after = book_impact_snapshot(
            book
        )

        self.assertEqual(
            impacted_seen_subject_ids(
                review,
                before,
                after,
            ),
            ("seen-element",),
        )

    def test_current_subject_is_excluded_from_a_revoir(self) -> None:
        book = Book(
            title="Impact sujet courant",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )
        element = add_text_element(
            page,
            "element-1",
        )

        review = SurvolReviewState()
        situation = Situation(
            "text",
            "widow",
            "element-1",
            page.id,
        )
        review.mark_seen(
            (situation,)
        )

        before = book_impact_snapshot(
            book
        )
        element["geometry"]["y_mm"] = 35.0
        after = book_impact_snapshot(
            book
        )

        self.assertEqual(
            impacted_seen_subject_ids(
                review,
                before,
                after,
                exclude=("element-1",),
            ),
            (),
        )

    def test_survol_execution_marks_other_seen_changed_subject_a_revoir(self) -> None:
        book = Book(
            title="Impact execution",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )

        add_text_element(
            page,
            "element-1",
        )
        impacted = add_text_element(
            page,
            "element-2",
            y_mm=40.0,
        )

        project = FakeProject(
            book
        )

        current = Situation(
            "text",
            "widow",
            "element-1",
            page.id,
        )
        old = Situation(
            "text",
            "style_outlier",
            "element-2",
            page.id,
        )

        review = SurvolReviewState()
        review.mark_seen(
            (old,)
        )
        review.open_page(
            page.id,
            (current,),
        )

        decision = make_decision(
            current
        )

        original = execution.execute_text_decision

        try:
            def fake_execute(
                current_book,
                current_situation,
                current_decision,
            ):
                impacted["geometry"]["y_mm"] = 55.0
                return SimpleNamespace(
                    changed=True,
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
            result.impacted_subject_ids,
            ("element-2",),
        )
        self.assertEqual(
            review.status("element-2"),
            ReviewStatus.REVIEW,
        )
        self.assertEqual(
            review.status("element-1"),
            ReviewStatus.SEEN,
        )
        self.assertTrue(
            result.page_complete,
        )

    def test_impact_marking_does_not_change_survol_page_or_navigate(self) -> None:
        book = Book(
            title="Impact sans navigation",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )
        changed = add_text_element(
            page,
            "element-2",
        )

        review = SurvolReviewState()
        old = Situation(
            "text",
            "widow",
            "element-2",
            page.id,
        )
        review.mark_seen(
            (old,)
        )
        review.open_page(
            page.id,
            (),
        )

        before_page = review.page_id
        before = book_impact_snapshot(
            book
        )
        changed["payload"]["text"] = "Texte modifie"
        after = book_impact_snapshot(
            book
        )

        impacted_ids = impacted_seen_subject_ids(
            review,
            before,
            after,
        )
        review.mark_for_review(
            impacted_ids
        )

        self.assertEqual(
            review.page_id,
            before_page,
        )
        self.assertEqual(
            review.status("element-2"),
            ReviewStatus.REVIEW,
        )
        self.assertFalse(
            hasattr(
                review,
                "navigation",
            )
        )


if __name__ == "__main__":
    unittest.main()