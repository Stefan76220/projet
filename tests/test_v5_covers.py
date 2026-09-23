from __future__ import annotations

from types import SimpleNamespace
import unittest

from src.v4 import structure_covers as v4_covers

from tomelinea.book import Book, Page
from tomelinea.covers import (
    COVER_CHOICE_BLANK,
    COVER_CHOICE_CONTENT,
    INSIDE_BACK_COVER,
    INSIDE_FRONT_COVER,
    cover_situations,
    execute_cover_decision,
)
from tomelinea.rules import (
    DecisionScope,
    decide,
    group_cases,
)
from tomelinea.survol import (
    ReviewStatus,
    SurvolReviewState,
    execute_current_decision,
)
import tomelinea.survol.execution as survol_execution


class FakeProject:
    def __init__(self, book) -> None:
        self.book = book
        self.touch_count = 0

    def touch(self) -> None:
        self.touch_count += 1


def page(
    title: str,
    page_type: str,
) -> Page:
    return Page(
        title=title,
        page_type=page_type,
    )


def make_cover_book():
    book = Book(
        title="Couvertures V5-21",
    )

    front = page(
        "Couverture avant",
        "1re de couverture",
    )
    body = page(
        "Premiere page du livre",
        "Page",
    )
    back = page(
        "Couverture arriere",
        "4e de couverture",
    )

    book.add_page(
        front
    )
    book.add_page(
        body
    )
    book.add_page(
        back
    )

    v4_covers.ensure_physical_cover_faces(
        book
    )
    v4_covers.prepare_inside_cover_confirmation(
        book
    )

    return book, body


def decision_for(
    situation,
    choice,
    *,
    scope=DecisionScope.LOCAL,
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


class V5CoverTests(unittest.TestCase):
    def test_catalog_uses_real_v4_pending_detector(self) -> None:
        book, body = make_cover_book()

        raw = v4_covers.inside_cover_confirmation_issues(
            book
        )
        situations = cover_situations(
            book
        )

        self.assertEqual(
            len(situations),
            len(raw),
        )
        self.assertEqual(
            {
                item.facts["face"]
                for item in situations
            },
            {
                INSIDE_FRONT_COVER,
                INSIDE_BACK_COVER,
            },
        )

    def test_survol_page_is_the_visible_candidate_when_available(self) -> None:
        book, body = make_cover_book()

        situation = next(
            item
            for item in cover_situations(
                book
            )
            if item.facts["face"] == INSIDE_FRONT_COVER
        )

        self.assertEqual(
            situation.page_id,
            body.id,
        )
        self.assertEqual(
            situation.domain,
            "cover",
        )

    def test_blank_choice_uses_v4_blank_engine(self) -> None:
        book, body = make_cover_book()
        project = FakeProject(
            book
        )

        situation = next(
            item
            for item in cover_situations(
                book
            )
            if item.facts["face"] == INSIDE_FRONT_COVER
        )

        decision = decision_for(
            situation,
            COVER_CHOICE_BLANK,
        )

        result = execute_cover_decision(
            project,
            situation,
            decision,
        )

        active_id = v4_covers.cover_ids(
            book
        )[INSIDE_FRONT_COVER]

        self.assertEqual(
            v4_covers.inside_cover_confirmation_status(
                book.pages[
                    active_id
                ]
            ),
            "blank",
        )
        self.assertEqual(
            result.choice,
            "blank",
        )
        self.assertEqual(
            project.touch_count,
            1,
        )

    def test_content_choice_promotes_exact_candidate_with_v4_engine(self) -> None:
        book, body = make_cover_book()
        project = FakeProject(
            book
        )

        situation = next(
            item
            for item in cover_situations(
                book
            )
            if item.facts["face"] == INSIDE_FRONT_COVER
        )

        self.assertEqual(
            situation.facts["candidate_page_id"],
            body.id,
        )

        decision = decision_for(
            situation,
            COVER_CHOICE_CONTENT,
        )

        result = execute_cover_decision(
            project,
            situation,
            decision,
        )

        ids = v4_covers.cover_ids(
            book
        )

        self.assertEqual(
            ids[INSIDE_FRONT_COVER],
            body.id,
        )
        self.assertEqual(
            result.result_page_id,
            body.id,
        )
        self.assertEqual(
            v4_covers.inside_cover_confirmation_status(
                body
            ),
            "content",
        )

    def test_stale_candidate_is_rejected_before_mutation(self) -> None:
        book, body = make_cover_book()
        project = FakeProject(
            book
        )

        situation = next(
            item
            for item in cover_situations(
                book
            )
            if item.facts["face"] == INSIDE_FRONT_COVER
        )

        extra = page(
            "Nouvelle premiere page",
            "Page",
        )
        book.pages[
            extra.id
        ] = extra

        old_index = book.page_order.index(
            body.id
        )
        book.page_order.insert(
            old_index,
            extra.id,
        )

        decision = decision_for(
            situation,
            COVER_CHOICE_CONTENT,
        )

        with self.assertRaises(
            ValueError,
        ):
            execute_cover_decision(
                project,
                situation,
                decision,
            )

        self.assertEqual(
            project.touch_count,
            0,
        )

    def test_cover_similarity_is_forbidden(self) -> None:
        book, body = make_cover_book()
        project = FakeProject(
            book
        )

        situation = cover_situations(
            book
        )[0]

        decision = decision_for(
            situation,
            COVER_CHOICE_BLANK,
            scope=DecisionScope.SIMILAR,
            similar=("another-cover",),
        )

        with self.assertRaises(
            ValueError,
        ):
            execute_cover_decision(
                project,
                situation,
                decision,
            )

    def test_survol_delegates_cover_domain_then_marks_seen(self) -> None:
        book, body = make_cover_book()
        project = FakeProject(
            book
        )

        situation = next(
            item
            for item in cover_situations(
                book
            )
            if item.facts["face"] == INSIDE_FRONT_COVER
        )

        review = SurvolReviewState()
        review.open_page(
            situation.page_id,
            (situation,),
        )

        decision = decision_for(
            situation,
            COVER_CHOICE_BLANK,
        )

        original = survol_execution.execute_cover_decision
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
                    choice="blank",
                )

            survol_execution.execute_cover_decision = fake_execute

            result = execute_current_decision(
                project,
                review,
                decision,
            )
        finally:
            survol_execution.execute_cover_decision = original

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
            "cover",
        )
        self.assertEqual(
            review.status(
                situation.subject_id
            ),
            ReviewStatus.SEEN,
        )


if __name__ == "__main__":
    unittest.main()