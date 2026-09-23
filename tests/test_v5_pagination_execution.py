from __future__ import annotations

from types import SimpleNamespace
import unittest

from src.v4 import structure_editorial as v4_editorial
from src.v4 import structure_sync as v4_sync

from tomelinea.book import Book, Page
from tomelinea.pagination import (
    DOUBLE_PAGE,
    PAGE_LEFT,
    PAGE_RIGHT,
    PAGINATION_CHOICE_DISABLED,
    PAGINATION_CHOICE_ENABLED,
    double_page_situation,
    execute_pagination_decision,
    pagination_situation,
)
from tomelinea.rules import (
    DecisionScope,
    decide,
    group_cases,
)
import tomelinea.pagination.execution as execution


class FakeProject:
    def __init__(self, book) -> None:
        self.book = book
        self.touch_count = 0

    def touch(self) -> None:
        self.touch_count += 1


def make_book(count: int = 3) -> tuple[Book, list[Page]]:
    book = Book(
        title="Pagination V5-13",
    )
    pages: list[Page] = []

    for index in range(
        count
    ):
        page = Page(
            title=f"Page {index + 1}",
        )
        book.add_page(
            page
        )
        pages.append(
            page
        )

    return (
        book,
        pages,
    )


class V5PaginationExecutionTests(unittest.TestCase):
    def test_execution_reuses_validated_v4_functions(self) -> None:
        self.assertIs(
            execution.set_constraint_on_pages,
            v4_editorial.set_constraint_on_pages,
        )
        self.assertIs(
            execution.extend_constraint_to_similar,
            v4_editorial.extend_constraint_to_similar,
        )
        self.assertIs(
            execution.sync_structure_rules,
            v4_sync.sync_structure_rules,
        )

    def test_local_enabled_uses_real_v4_constraint_engine(self) -> None:
        book, pages = make_book()
        project = FakeProject(
            book
        )

        situation = pagination_situation(
            book,
            pages[0].id,
            PAGE_LEFT,
        )

        case = group_cases(
            [situation]
        )[0]

        decision = decide(
            case,
            situation.id,
            PAGINATION_CHOICE_ENABLED,
        )

        original_sync = execution.sync_structure_rules

        try:
            execution.sync_structure_rules = (
                lambda current_book: SimpleNamespace()
            )

            result = execute_pagination_decision(
                project,
                situation,
                decision,
            )
        finally:
            execution.sync_structure_rules = original_sync

        self.assertTrue(
            v4_editorial.constraint_enabled(
                book,
                pages[0].id,
                PAGE_LEFT,
            )
        )
        self.assertEqual(
            result.choice,
            "enabled",
        )
        self.assertEqual(
            result.changed_page_ids,
            (pages[0].id,),
        )
        self.assertEqual(
            project.touch_count,
            1,
        )

    def test_local_disabled_uses_same_v4_engine(self) -> None:
        book, pages = make_book()
        v4_editorial.set_constraint_on_pages(
            book,
            [pages[0].id],
            PAGE_RIGHT,
            True,
        )

        project = FakeProject(
            book
        )

        situation = pagination_situation(
            book,
            pages[0].id,
            PAGE_RIGHT,
        )

        case = group_cases(
            [situation]
        )[0]

        decision = decide(
            case,
            situation.id,
            PAGINATION_CHOICE_DISABLED,
        )

        original_sync = execution.sync_structure_rules

        try:
            execution.sync_structure_rules = (
                lambda current_book: SimpleNamespace()
            )

            execute_pagination_decision(
                project,
                situation,
                decision,
            )
        finally:
            execution.sync_structure_rules = original_sync

        self.assertFalse(
            v4_editorial.constraint_enabled(
                book,
                pages[0].id,
                PAGE_RIGHT,
            )
        )

    def test_double_page_uses_two_explicit_ids(self) -> None:
        book, pages = make_book()
        project = FakeProject(
            book
        )

        situation = double_page_situation(
            book,
            [
                pages[0].id,
                pages[1].id,
            ],
        )

        case = group_cases(
            [situation]
        )[0]

        decision = decide(
            case,
            situation.id,
            PAGINATION_CHOICE_ENABLED,
        )

        original_sync = execution.sync_structure_rules

        try:
            execution.sync_structure_rules = (
                lambda current_book: SimpleNamespace()
            )

            result = execute_pagination_decision(
                project,
                situation,
                decision,
            )
        finally:
            execution.sync_structure_rules = original_sync

        self.assertEqual(
            result.changed_page_ids,
            (
                pages[0].id,
                pages[1].id,
            ),
        )
        self.assertTrue(
            book.pages[pages[0].id].spread_id
        )
        self.assertEqual(
            book.pages[pages[0].id].spread_id,
            book.pages[pages[1].id].spread_id,
        )

    def test_double_page_similar_scope_is_rejected(self) -> None:
        book, pages = make_book()

        situation = double_page_situation(
            book,
            [
                pages[0].id,
                pages[1].id,
            ],
        )

        case = group_cases(
            [situation]
        )[0]

        decision = decide(
            case,
            situation.id,
            PAGINATION_CHOICE_ENABLED,
            scope=DecisionScope.SIMILAR,
            similar_subject_ids=(
                pages[2].id,
            ),
        )

        project = FakeProject(
            book
        )

        with self.assertRaises(
            ValueError,
        ):
            execute_pagination_decision(
                project,
                situation,
                decision,
            )

    def test_similar_scope_checks_explicit_family_before_mutation(self) -> None:
        book, pages = make_book()
        project = FakeProject(
            book
        )

        situation = pagination_situation(
            book,
            pages[0].id,
            PAGE_RIGHT,
        )

        case = group_cases(
            [situation]
        )[0]

        decision = decide(
            case,
            situation.id,
            PAGINATION_CHOICE_ENABLED,
            scope=DecisionScope.SIMILAR,
            similar_subject_ids=(
                pages[1].id,
            ),
        )

        original_similar = execution.similar_pagination_page_ids
        original_set = execution.set_constraint_on_pages

        calls = []

        try:
            execution.similar_pagination_page_ids = (
                lambda *args, **kwargs: (
                    pages[2].id,
                )
            )

            def fake_set(*args, **kwargs):
                calls.append(
                    (
                        args,
                        kwargs,
                    )
                )
                return []

            execution.set_constraint_on_pages = fake_set

            with self.assertRaises(
                ValueError,
            ):
                execute_pagination_decision(
                    project,
                    situation,
                    decision,
                )
        finally:
            execution.similar_pagination_page_ids = original_similar
            execution.set_constraint_on_pages = original_set

        self.assertEqual(
            calls,
            [],
        )
        self.assertEqual(
            project.touch_count,
            0,
        )

    def test_similar_scope_delegates_to_v4_extension_after_validation(self) -> None:
        book, pages = make_book()
        project = FakeProject(
            book
        )

        situation = pagination_situation(
            book,
            pages[0].id,
            PAGE_RIGHT,
        )

        case = group_cases(
            [situation]
        )[0]

        decision = decide(
            case,
            situation.id,
            PAGINATION_CHOICE_ENABLED,
            scope=DecisionScope.SIMILAR,
            similar_subject_ids=(
                pages[1].id,
                pages[2].id,
            ),
        )

        original_similar = execution.similar_pagination_page_ids
        original_set = execution.set_constraint_on_pages
        original_extend = execution.extend_constraint_to_similar
        original_sync = execution.sync_structure_rules

        calls = {
            "set": [],
            "extend": [],
            "sync": 0,
        }

        try:
            execution.similar_pagination_page_ids = (
                lambda *args, **kwargs: (
                    pages[0].id,
                    pages[1].id,
                    pages[2].id,
                )
            )

            def fake_set(
                current_book,
                targets,
                kind,
                enabled,
            ):
                calls["set"].append(
                    (
                        tuple(targets),
                        kind,
                        enabled,
                    )
                )
                return list(
                    targets
                )

            def fake_extend(
                current_project,
                anchor_page_id,
                kind,
                *,
                threshold,
            ):
                calls["extend"].append(
                    (
                        anchor_page_id,
                        kind,
                        threshold,
                    )
                )
                return {
                    "extension_id": "ext-1",
                    "page_ids": [
                        pages[0].id,
                        pages[1].id,
                        pages[2].id,
                    ],
                    "applied_page_ids": [
                        pages[0].id,
                        pages[1].id,
                        pages[2].id,
                    ],
                    "excluded_page_ids": [],
                    "threshold": threshold,
                }

            def fake_sync(
                current_book,
            ):
                calls["sync"] += 1
                return SimpleNamespace()

            execution.set_constraint_on_pages = fake_set
            execution.extend_constraint_to_similar = fake_extend
            execution.sync_structure_rules = fake_sync

            result = execute_pagination_decision(
                project,
                situation,
                decision,
            )
        finally:
            execution.similar_pagination_page_ids = original_similar
            execution.set_constraint_on_pages = original_set
            execution.extend_constraint_to_similar = original_extend
            execution.sync_structure_rules = original_sync

        self.assertEqual(
            calls["set"],
            [
                (
                    (pages[0].id,),
                    PAGE_RIGHT,
                    True,
                )
            ],
        )
        self.assertEqual(
            calls["extend"],
            [
                (
                    pages[0].id,
                    PAGE_RIGHT,
                    0.88,
                )
            ],
        )
        self.assertEqual(
            calls["sync"],
            1,
        )
        self.assertEqual(
            result.extension_id,
            "ext-1",
        )
        self.assertEqual(
            result.changed_page_ids,
            (
                pages[0].id,
                pages[1].id,
                pages[2].id,
            ),
        )
        self.assertEqual(
            project.touch_count,
            1,
        )

    def test_similar_disabled_is_rejected_as_ambiguous(self) -> None:
        book, pages = make_book()
        project = FakeProject(
            book
        )

        situation = pagination_situation(
            book,
            pages[0].id,
            PAGE_RIGHT,
        )

        case = group_cases(
            [situation]
        )[0]

        decision = decide(
            case,
            situation.id,
            PAGINATION_CHOICE_DISABLED,
            scope=DecisionScope.SIMILAR,
            similar_subject_ids=(
                pages[1].id,
            ),
        )

        with self.assertRaises(
            ValueError,
        ):
            execute_pagination_decision(
                project,
                situation,
                decision,
            )

    def test_unknown_choice_is_rejected(self) -> None:
        book, pages = make_book()
        project = FakeProject(
            book
        )

        situation = pagination_situation(
            book,
            pages[0].id,
            PAGE_RIGHT,
        )

        case = group_cases(
            [situation]
        )[0]

        decision = decide(
            case,
            situation.id,
            "invented",
        )

        with self.assertRaises(
            ValueError,
        ):
            execute_pagination_decision(
                project,
                situation,
                decision,
            )


if __name__ == "__main__":
    unittest.main()