from __future__ import annotations

import unittest

from src.v4 import image_quality as v4_image_quality

from tomelinea.book import Book, Page
from tomelinea.images import (
    IMAGE_QUALITY_CRITICAL,
    IMAGE_QUALITY_LIMITED,
    MINIMUM_DPI,
    TARGET_DPI,
    audit_book_images,
    effective_dpi,
    image_quality_situations,
)
from tomelinea.rules import group_cases


def add_image(
    page: Page,
    element_id: str,
    *,
    width_px: int,
    height_px: int,
    width_mm: float,
    height_mm: float,
) -> None:
    page.content.append(
        {
            "id": element_id,
            "kind": "image",
            "geometry": {
                "x_mm": 10.0,
                "y_mm": 10.0,
                "width_mm": width_mm,
                "height_mm": height_mm,
            },
            "payload": {
                "width_px": width_px,
                "height_px": height_px,
            },
            "metadata": {},
        }
    )


class V5ImageQualitySituationTests(unittest.TestCase):
    def test_v5_reuses_exact_v4_quality_engine_and_thresholds(self) -> None:
        self.assertIs(
            effective_dpi,
            v4_image_quality.effective_dpi,
        )
        self.assertEqual(
            TARGET_DPI,
            300.0,
        )
        self.assertEqual(
            MINIMUM_DPI,
            200.0,
        )

    def test_audit_reproduces_v4_status_contract(self) -> None:
        book = Book(
            title="Images V5-19",
        )
        page = Page(
            title="Images",
        )
        book.add_page(
            page
        )

        add_image(
            page,
            "image-conforme",
            width_px=3000,
            height_px=3000,
            width_mm=100.0,
            height_mm=100.0,
        )
        add_image(
            page,
            "image-limited",
            width_px=1000,
            height_px=1000,
            width_mm=100.0,
            height_mm=100.0,
        )
        add_image(
            page,
            "image-critical",
            width_px=500,
            height_px=500,
            width_mm=100.0,
            height_mm=100.0,
        )

        audit = audit_book_images(
            book
        )

        self.assertEqual(
            audit.total,
            3,
        )
        self.assertEqual(
            audit.conforme,
            1,
        )
        self.assertEqual(
            audit.limited,
            1,
        )
        self.assertEqual(
            audit.critical,
            1,
        )
        self.assertEqual(
            len(audit.issues),
            2,
        )

    def test_only_non_conforming_images_become_situations(self) -> None:
        book = Book(
            title="Situations Images",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )

        add_image(
            page,
            "image-ok",
            width_px=2400,
            height_px=2400,
            width_mm=100.0,
            height_mm=100.0,
        )
        add_image(
            page,
            "image-limit",
            width_px=1000,
            height_px=1000,
            width_mm=100.0,
            height_mm=100.0,
        )
        add_image(
            page,
            "image-bad",
            width_px=500,
            height_px=500,
            width_mm=100.0,
            height_mm=100.0,
        )

        situations = image_quality_situations(
            book
        )

        self.assertEqual(
            len(situations),
            2,
        )
        self.assertEqual(
            {
                item.kind
                for item in situations
            },
            {
                IMAGE_QUALITY_LIMITED,
                IMAGE_QUALITY_CRITICAL,
            },
        )

    def test_image_situation_keeps_stable_element_and_page_ids(self) -> None:
        book = Book(
            title="Stable image",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )

        add_image(
            page,
            "image-stable-1",
            width_px=500,
            height_px=500,
            width_mm=100.0,
            height_mm=100.0,
        )

        situation = image_quality_situations(
            book
        )[0]

        self.assertEqual(
            situation.domain,
            "image",
        )
        self.assertEqual(
            situation.subject_id,
            "image-stable-1",
        )
        self.assertEqual(
            situation.page_id,
            page.id,
        )
        self.assertEqual(
            situation.kind,
            IMAGE_QUALITY_CRITICAL,
        )
        self.assertEqual(
            situation.facts["minimum_dpi"],
            200.0,
        )
        self.assertEqual(
            situation.facts["target_dpi"],
            300.0,
        )

    def test_multiple_image_situations_for_same_object_form_one_case(self) -> None:
        book = Book(
            title="Groupement Images",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )

        add_image(
            page,
            "image-1",
            width_px=500,
            height_px=500,
            width_mm=100.0,
            height_mm=100.0,
        )

        quality = image_quality_situations(
            book
        )[0]

        from tomelinea.rules import Situation

        future_anchor = Situation(
            domain="image",
            kind="image_anchor_review",
            subject_id="image-1",
            page_id=page.id,
        )

        cases = group_cases(
            (
                quality,
                future_anchor,
            )
        )

        self.assertEqual(
            len(cases),
            1,
        )
        self.assertEqual(
            len(cases[0].situations),
            2,
        )

    def test_invalid_image_metrics_are_skipped_like_v4_audit(self) -> None:
        book = Book(
            title="Image invalide",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )

        page.content.append(
            {
                "id": "image-invalide",
                "kind": "image",
                "geometry": {
                    "width_mm": 100.0,
                    "height_mm": 100.0,
                },
                "payload": {
                    "width_px": 0,
                    "height_px": 0,
                },
                "metadata": {},
            }
        )

        audit = audit_book_images(
            book
        )

        self.assertEqual(
            audit.total,
            0,
        )
        self.assertEqual(
            audit.issues,
            (),
        )


if __name__ == "__main__":
    unittest.main()