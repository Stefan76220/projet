from __future__ import annotations

from types import SimpleNamespace
import unittest

from src.v4 import image_quality as v4_image_quality

from tomelinea.book import Book, Page
from tomelinea.images import (
    IMAGE_CHOICE_CORRECTED,
    IMAGE_CHOICE_IGNORED,
    IMAGE_QUALITY_CRITICAL,
    IMAGE_QUALITY_LIMITED,
    execute_image_decision,
    image_quality_situations,
)
from tomelinea.rules import (
    DecisionScope,
    Situation,
    decide,
    group_cases,
)
from tomelinea.survol import (
    ReviewStatus,
    SurvolReviewState,
    execute_current_decision,
)
import tomelinea.images.execution as image_execution
import tomelinea.survol.execution as survol_execution


class FakeProject:
    def __init__(self, book) -> None:
        self.book = book


def add_image(
    page: Page,
    element_id: str,
    *,
    width_px: int,
    height_px: int,
    width_mm: float,
    height_mm: float,
) -> dict:
    element = {
        "id": element_id,
        "kind": "image",
        "geometry": {
            "x_mm": 12.0,
            "y_mm": 18.0,
            "width_mm": width_mm,
            "height_mm": height_mm,
        },
        "payload": {
            "width_px": width_px,
            "height_px": height_px,
        },
        "metadata": {},
    }
    page.content.append(
        element
    )
    return element


def decision_for(
    situation: Situation,
    choice: str,
    *,
    scope: DecisionScope = DecisionScope.LOCAL,
    similar=(),
):
    case = group_cases(
        (situation,)
    )[0]

    return decide(
        case,
        situation.id,
        choice,
        scope=scope,
        similar_subject_ids=similar,
    )


class V5ImageQualityExecutionTests(unittest.TestCase):
    def test_execution_reuses_v4_clamp_engine(self) -> None:
        self.assertIs(
            image_execution.clamp_size_to_minimum_dpi,
            v4_image_quality.clamp_size_to_minimum_dpi,
        )

    def test_critical_image_can_be_reduced_to_v4_minimum(self) -> None:
        book = Book(
            title="Correction image",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )

        element = add_image(
            page,
            "image-1",
            width_px=500,
            height_px=500,
            width_mm=100.0,
            height_mm=100.0,
        )

        situation = image_quality_situations(
            book
        )[0]

        self.assertEqual(
            situation.kind,
            IMAGE_QUALITY_CRITICAL,
        )

        decision = decision_for(
            situation,
            IMAGE_CHOICE_CORRECTED,
        )

        result = execute_image_decision(
            book,
            situation,
            decision,
        )

        self.assertTrue(
            result.changed,
        )
        self.assertLess(
            result.width_mm_after,
            result.width_mm_before,
        )
        self.assertLess(
            result.height_mm_after,
            result.height_mm_before,
        )
        self.assertGreaterEqual(
            result.dpi_after + 1e-6,
            200.0,
        )
        self.assertEqual(
            element["geometry"]["x_mm"],
            12.0,
        )
        self.assertEqual(
            element["geometry"]["y_mm"],
            18.0,
        )
        self.assertEqual(
            element["metadata"]["image_quality_decisions"][
                IMAGE_QUALITY_CRITICAL
            ],
            "corrected",
        )

    def test_ignored_image_is_recorded_without_geometry_change(self) -> None:
        book = Book(
            title="Image conservee",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )

        element = add_image(
            page,
            "image-1",
            width_px=500,
            height_px=500,
            width_mm=100.0,
            height_mm=100.0,
        )

        before = dict(
            element["geometry"]
        )

        situation = image_quality_situations(
            book
        )[0]
        decision = decision_for(
            situation,
            IMAGE_CHOICE_IGNORED,
        )

        result = execute_image_decision(
            book,
            situation,
            decision,
        )

        self.assertFalse(
            result.changed,
        )
        self.assertEqual(
            element["geometry"],
            before,
        )
        self.assertEqual(
            element["metadata"]["image_quality_decisions"][
                IMAGE_QUALITY_CRITICAL
            ],
            "ignored",
        )

    def test_limited_image_has_no_invented_automatic_correction(self) -> None:
        book = Book(
            title="Image limitee",
        )
        page = Page(
            title="Page",
        )
        book.add_page(
            page
        )

        element = add_image(
            page,
            "image-limited",
            width_px=1000,
            height_px=1000,
            width_mm=100.0,
            height_mm=100.0,
        )

        situation = image_quality_situations(
            book
        )[0]

        self.assertEqual(
            situation.kind,
            IMAGE_QUALITY_LIMITED,
        )

        decision = decision_for(
            situation,
            IMAGE_CHOICE_CORRECTED,
        )

        before = dict(
            element["geometry"]
        )

        with self.assertRaises(
            ValueError,
        ):
            execute_image_decision(
                book,
                situation,
                decision,
            )

        self.assertEqual(
            element["geometry"],
            before,
        )
        self.assertNotIn(
            "image_quality_decisions",
            element["metadata"],
        )

    def test_image_similarity_scope_is_rejected(self) -> None:
        book = Book(
            title="Image similarite",
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

        situation = image_quality_situations(
            book
        )[0]

        decision = decision_for(
            situation,
            IMAGE_CHOICE_IGNORED,
            scope=DecisionScope.SIMILAR,
            similar=("image-2",),
        )

        with self.assertRaises(
            ValueError,
        ):
            execute_image_decision(
                book,
                situation,
                decision,
            )

    def test_survol_delegates_image_domain_then_marks_seen(self) -> None:
        book = Book(
            title="Survol image",
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

        situation = image_quality_situations(
            book
        )[0]
        review = SurvolReviewState()
        review.open_page(
            page.id,
            (situation,),
        )
        decision = decision_for(
            situation,
            IMAGE_CHOICE_IGNORED,
        )

        project = FakeProject(
            book
        )

        original = survol_execution.execute_image_decision
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

            survol_execution.execute_image_decision = fake_execute

            result = execute_current_decision(
                project,
                review,
                decision,
            )
        finally:
            survol_execution.execute_image_decision = original

        self.assertEqual(
            len(calls),
            1,
        )
        self.assertIs(
            calls[0][0],
            book,
        )
        self.assertEqual(
            result.domain,
            "image",
        )
        self.assertEqual(
            review.status("image-1"),
            ReviewStatus.SEEN,
        )
        self.assertTrue(
            result.page_complete,
        )

    def test_unknown_image_kind_is_rejected(self) -> None:
        book = Book(
            title="Image inconnue",
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

        situation = Situation(
            domain="image",
            kind="future_image_case",
            subject_id="image-1",
            page_id=page.id,
        )

        decision = decision_for(
            situation,
            IMAGE_CHOICE_IGNORED,
        )

        with self.assertRaises(
            ValueError,
        ):
            execute_image_decision(
                book,
                situation,
                decision,
            )


if __name__ == "__main__":
    unittest.main()