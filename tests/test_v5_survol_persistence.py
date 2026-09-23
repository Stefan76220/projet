from __future__ import annotations

import unittest

from src.v4.storage import (
    project_from_dict,
    project_to_dict,
)
from tomelinea.app import Project
from tomelinea.book import Book, Page
from tomelinea.rules import Situation
from tomelinea.survol import (
    REVIEW_METADATA_KEY,
    REVIEW_SCHEMA,
    ReviewStatus,
    SurvolReviewState,
    load_review_state,
    save_review_state,
)


def text_situation(
    subject_id: str,
    *,
    page_id: str = "page-1",
    kind: str = "widow",
) -> Situation:
    return Situation(
        domain="text",
        kind=kind,
        subject_id=subject_id,
        page_id=page_id,
    )


class V5SurvolPersistenceTests(unittest.TestCase):
    def test_export_contains_only_durable_state(self) -> None:
        review = SurvolReviewState()
        item = text_situation(
            "element-1",
        )

        review.open_page(
            "page-1",
            (item,),
        )
        review.complete_current_situation()
        review.mark_for_review(
            ("element-2",)
        )

        payload = review.export_state()

        self.assertEqual(
            payload["schema"],
            REVIEW_SCHEMA,
        )
        self.assertIn(
            "element-1",
            payload["known_situations"],
        )
        self.assertEqual(
            payload["forced_review"],
            ["element-2"],
        )

        for forbidden in (
            "page_id",
            "case_index",
            "situation_index",
            "position",
            "navigation",
        ):
            self.assertNotIn(
                forbidden,
                payload,
            )

    def test_restore_resets_transient_cursor_but_keeps_review_state(self) -> None:
        original = SurvolReviewState()
        item = text_situation(
            "element-1",
        )

        original.open_page(
            "page-1",
            (item,),
        )
        original.complete_current_situation()
        original.mark_for_review(
            ("element-2",)
        )

        restored = SurvolReviewState.from_state(
            original.export_state()
        )

        self.assertEqual(
            restored.page_id,
            "",
        )
        self.assertTrue(
            restored.page_complete,
        )
        self.assertEqual(
            restored.status("element-1"),
            ReviewStatus.SEEN,
        )
        self.assertEqual(
            restored.status("element-2"),
            ReviewStatus.REVIEW,
        )

    def test_book_metadata_is_the_only_persistence_location(self) -> None:
        book = Book(
            title="Survol V5-15",
        )
        review = SurvolReviewState()

        item = text_situation(
            "element-1",
        )

        review.mark_seen(
            (item,)
        )

        payload = save_review_state(
            book,
            review,
        )

        self.assertEqual(
            book.metadata[REVIEW_METADATA_KEY],
            payload,
        )

        restored = load_review_state(
            book
        )

        self.assertEqual(
            restored.status("element-1"),
            ReviewStatus.SEEN,
        )

    def test_review_survives_real_v4_project_storage_round_trip(self) -> None:
        book = Book(
            title="Survol persistant",
        )

        page = Page(
            title="Page test",
        )
        book.add_page(
            page
        )

        review = SurvolReviewState()

        item = text_situation(
            "element-stable-42",
            page_id=page.id,
        )

        review.mark_seen(
            (item,)
        )
        review.mark_for_review(
            ("element-stable-99",)
        )

        save_review_state(
            book,
            review,
        )

        project = Project(
            title="Projet V5-15",
            book=book,
        )

        serialized = project_to_dict(
            project
        )
        restored_project = project_from_dict(
            serialized
        )

        restored_review = load_review_state(
            restored_project.book
        )

        self.assertEqual(
            restored_review.status("element-stable-42"),
            ReviewStatus.SEEN,
        )
        self.assertEqual(
            restored_review.status("element-stable-99"),
            ReviewStatus.REVIEW,
        )

    def test_page_reorder_does_not_change_status_bound_to_stable_id(self) -> None:
        book = Book(
            title="Survol stable IDs",
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

        review = SurvolReviewState()

        item = text_situation(
            "element-stable-7",
            page_id=first.id,
        )

        review.mark_seen(
            (item,)
        )

        save_review_state(
            book,
            review,
        )

        book.page_order = [
            second.id,
            first.id,
        ]
        first.title = "Titre renomme"

        restored = load_review_state(
            book
        )

        self.assertEqual(
            restored.status("element-stable-7"),
            ReviewStatus.SEEN,
        )

    def test_invalid_or_old_payload_starts_clean(self) -> None:
        book = Book(
            title="Survol invalid payload",
        )

        book.metadata[
            REVIEW_METADATA_KEY
        ] = {
            "schema": "tomelinea.survol_review.old",
            "known_situations": {
                "element-1": [
                    "text:widow:element-1",
                ]
            },
            "forced_review": [
                "element-2",
            ],
        }

        review = load_review_state(
            book
        )

        self.assertEqual(
            review.status("element-1"),
            ReviewStatus.NEW,
        )
        self.assertEqual(
            review.status("element-2"),
            ReviewStatus.NEW,
        )

    def test_saved_state_is_json_compatible_through_v4_serializer(self) -> None:
        book = Book(
            title="Survol JSON",
        )

        review = SurvolReviewState()
        review.mark_for_review(
            (
                "element-2",
                "element-1",
            )
        )

        save_review_state(
            book,
            review,
        )

        project = Project(
            title="Projet JSON",
            book=book,
        )

        root = project_to_dict(
            project
        )

        payload = root["project"]["book"]["metadata"][
            REVIEW_METADATA_KEY
        ]

        self.assertEqual(
            payload["schema"],
            REVIEW_SCHEMA,
        )
        self.assertEqual(
            payload["forced_review"],
            [
                "element-1",
                "element-2",
            ],
        )


if __name__ == "__main__":
    unittest.main()