from __future__ import annotations

import unittest
from unittest.mock import patch

from tomelinea.book import Book, Page
from tomelinea.covers import INSIDE_FRONT_COVER
from tomelinea.project_types.roman import (
    RomanReviewPreparation,
    open_roman_review_page,
    prepare_roman_review,
)
from tomelinea.rules import Situation
from tomelinea.survol import SurvolReviewState
from tomelinea.text import TextReviewPreparation


def add_element(
    page: Page,
    element_id: str,
    kind: str,
    *,
    y_mm: float,
) -> None:
    page.content.append(
        {
            "id": element_id,
            "kind": kind,
            "geometry": {
                "x_mm": 15.0,
                "y_mm": y_mm,
                "width_mm": 80.0,
                "height_mm": 10.0,
            },
            "payload": {},
            "metadata": {},
        }
    )


class V5RomanReviewTests(unittest.TestCase):
    def test_roman_profile_combines_existing_domains_in_physical_page_order(self) -> None:
        book = Book(
            title="Roman V5-22",
        )
        first = Page(
            title="Page 1",
        )
        second = Page(
            title="Page 2",
        )
        book.add_page(
            first
        )
        book.add_page(
            second
        )

        text_situation = Situation(
            domain="text",
            kind="widow",
            subject_id="text-2",
            page_id=second.id,
            facts={
                "geometry": {
                    "x_mm": 15.0,
                    "y_mm": 30.0,
                }
            },
        )

        image_situation = Situation(
            domain="image",
            kind="image_quality_critical",
            subject_id="image-1",
            page_id=first.id,
        )

        cover_situation = Situation(
            domain="cover",
            kind="inside_cover_confirmation",
            subject_id="cover-1",
            page_id=first.id,
            qualifier=INSIDE_FRONT_COVER,
        )

        fake_text = TextReviewPreparation(
            rules={},
            rules_created=False,
            automatic_corrections=(),
            situations=(
                text_situation,
            ),
        )

        with patch(
            "tomelinea.project_types.roman.review.prepare_text_review",
            return_value=fake_text,
        ), patch(
            "tomelinea.project_types.roman.review.image_quality_situations",
            return_value=(
                image_situation,
            ),
        ), patch(
            "tomelinea.project_types.roman.review.cover_situations",
            return_value=(
                cover_situation,
            ),
        ):
            preparation = prepare_roman_review(
                book
            )

        self.assertEqual(
            [
                item.domain
                for item in preparation.situations
            ],
            [
                "cover",
                "image",
                "text",
            ],
        )
        self.assertEqual(
            [
                item.page_id
                for item in preparation.situations
            ],
            [
                first.id,
                first.id,
                second.id,
            ],
        )

    def test_objects_on_same_page_follow_vertical_position_not_domain_passes(self) -> None:
        book = Book(
            title="Roman ordre page",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )

        add_element(
            page,
            "image-haute",
            "image",
            y_mm=20.0,
        )
        add_element(
            page,
            "text-bas",
            "text",
            y_mm=80.0,
        )

        text_situation = Situation(
            domain="text",
            kind="widow",
            subject_id="text-bas",
            page_id=page.id,
        )

        image_situation = Situation(
            domain="image",
            kind="image_quality_critical",
            subject_id="image-haute",
            page_id=page.id,
        )

        fake_text = TextReviewPreparation(
            rules={},
            rules_created=False,
            automatic_corrections=(),
            situations=(
                text_situation,
            ),
        )

        with patch(
            "tomelinea.project_types.roman.review.prepare_text_review",
            return_value=fake_text,
        ), patch(
            "tomelinea.project_types.roman.review.image_quality_situations",
            return_value=(
                image_situation,
            ),
        ), patch(
            "tomelinea.project_types.roman.review.cover_situations",
            return_value=(),
        ):
            preparation = prepare_roman_review(
                book
            )

        self.assertEqual(
            [
                item.subject_id
                for item in preparation.situations
            ],
            [
                "image-haute",
                "text-bas",
            ],
        )

    def test_text_technical_preparation_is_reused_not_reimplemented(self) -> None:
        book = Book(
            title="Roman texte",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )

        fake_text = TextReviewPreparation(
            rules={
                "alignment": "justify",
            },
            rules_created=True,
            automatic_corrections=(
                {
                    "type": "double_space",
                    "changed": True,
                },
            ),
            situations=(),
        )

        with patch(
            "tomelinea.project_types.roman.review.prepare_text_review",
            return_value=fake_text,
        ) as text_prepare, patch(
            "tomelinea.project_types.roman.review.image_quality_situations",
            return_value=(),
        ), patch(
            "tomelinea.project_types.roman.review.cover_situations",
            return_value=(),
        ):
            preparation = prepare_roman_review(
                book
            )

        text_prepare.assert_called_once_with(
            book
        )
        self.assertTrue(
            preparation.text_rules_created,
        )
        self.assertEqual(
            preparation.automatic_text_corrections[0]["type"],
            "double_space",
        )

    def test_pagination_choices_are_not_invented_by_roman_collector(self) -> None:
        book = Book(
            title="Roman sans pagination inventee",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )

        fake_text = TextReviewPreparation(
            rules={},
            rules_created=False,
            automatic_corrections=(),
            situations=(),
        )

        with patch(
            "tomelinea.project_types.roman.review.prepare_text_review",
            return_value=fake_text,
        ), patch(
            "tomelinea.project_types.roman.review.image_quality_situations",
            return_value=(),
        ), patch(
            "tomelinea.project_types.roman.review.cover_situations",
            return_value=(),
        ):
            preparation = prepare_roman_review(
                book
            )

        self.assertFalse(
            any(
                item.domain == "pagination"
                for item in preparation.situations
            )
        )

    def test_unordered_situation_is_reported_not_silently_attached(self) -> None:
        book = Book(
            title="Roman situation orpheline",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )

        orphan = Situation(
            domain="text",
            kind="widow",
            subject_id="element-orphan",
            page_id="missing-page",
        )

        fake_text = TextReviewPreparation(
            rules={},
            rules_created=False,
            automatic_corrections=(),
            situations=(
                orphan,
            ),
        )

        with patch(
            "tomelinea.project_types.roman.review.prepare_text_review",
            return_value=fake_text,
        ), patch(
            "tomelinea.project_types.roman.review.image_quality_situations",
            return_value=(),
        ), patch(
            "tomelinea.project_types.roman.review.cover_situations",
            return_value=(),
        ):
            preparation = prepare_roman_review(
                book
            )

        self.assertEqual(
            preparation.situations,
            (),
        )
        self.assertEqual(
            preparation.unresolved_situations,
            (
                orphan,
            ),
        )

    def test_open_page_feeds_existing_common_review(self) -> None:
        page_id = "page-1"
        situation = Situation(
            domain="text",
            kind="widow",
            subject_id="element-1",
            page_id=page_id,
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

        review = SurvolReviewState()

        snapshot = open_roman_review_page(
            review,
            preparation,
            page_id,
        )

        self.assertEqual(
            snapshot.page_id,
            page_id,
        )
        self.assertEqual(
            snapshot.current_situation.id,
            situation.id,
        )
        self.assertIs(
            review.current_situation,
            snapshot.current_situation,
        )

    def test_roman_profile_has_no_navigation_engine(self) -> None:
        import tomelinea.project_types.roman.review as module

        forbidden = {
            "NavigationState",
            "SurvolState",
            "queue",
            "page_queue",
            "canvas",
            "webview",
        }

        names = set(
            dir(
                module
            )
        )

        self.assertTrue(
            forbidden.isdisjoint(
                names
            )
        )


if __name__ == "__main__":
    unittest.main()