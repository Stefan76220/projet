from __future__ import annotations

import unittest

from src.v4 import structure_editorial as v4_editorial
from tomelinea.book import Book, Page
from tomelinea.pagination import (
    BLANK_AFTER,
    BLANK_BEFORE,
    CONSTRAINT_HELP,
    CONSTRAINT_LABELS,
    DOUBLE_PAGE,
    PAGINATION_SITUATION_KINDS,
    PAGE_LEFT,
    PAGE_RIGHT,
    SIMILARITY_THRESHOLD,
    PaginationSituationClass,
    double_page_situation,
    pagination_situation,
    pagination_situation_class,
    similar_pagination_page_ids,
)
from tomelinea.rules import Situation, group_cases


def make_book(count: int = 3) -> tuple[Book, list[Page]]:
    book = Book(title="Pagination V5-11")
    pages = []

    for index in range(count):
        page = Page(title=f"Page {index + 1}")
        book.add_page(page)
        pages.append(page)

    return book, pages


class V5PaginationSituationTests(unittest.TestCase):
    def test_catalog_reuses_the_five_validated_v4_constraints(self) -> None:
        self.assertEqual(
            PAGINATION_SITUATION_KINDS,
            v4_editorial.KNOWN_CONSTRAINTS,
        )
        self.assertEqual(
            PAGINATION_SITUATION_KINDS,
            (
                PAGE_RIGHT,
                PAGE_LEFT,
                BLANK_BEFORE,
                BLANK_AFTER,
                DOUBLE_PAGE,
            ),
        )

        self.assertIs(
            CONSTRAINT_LABELS,
            v4_editorial.CONSTRAINT_LABELS,
        )
        self.assertIs(
            CONSTRAINT_HELP,
            v4_editorial.CONSTRAINT_HELP,
        )
        self.assertEqual(
            SIMILARITY_THRESHOLD,
            0.88,
        )

    def test_classes_match_the_validated_interface_groups(self) -> None:
        self.assertEqual(
            pagination_situation_class(PAGE_RIGHT),
            PaginationSituationClass.POSITION,
        )
        self.assertEqual(
            pagination_situation_class(PAGE_LEFT),
            PaginationSituationClass.POSITION,
        )
        self.assertEqual(
            pagination_situation_class(BLANK_BEFORE),
            PaginationSituationClass.AROUND,
        )
        self.assertEqual(
            pagination_situation_class(BLANK_AFTER),
            PaginationSituationClass.AROUND,
        )
        self.assertEqual(
            pagination_situation_class(DOUBLE_PAGE),
            PaginationSituationClass.SPREAD,
        )

    def test_single_page_constraint_becomes_v5_situation(self) -> None:
        book, pages = make_book()

        situation = pagination_situation(
            book,
            pages[0].id,
            PAGE_RIGHT,
        )

        self.assertIsInstance(situation, Situation)
        self.assertEqual(situation.domain, "pagination")
        self.assertEqual(situation.kind, PAGE_RIGHT)
        self.assertEqual(situation.subject_id, pages[0].id)
        self.assertEqual(situation.page_id, pages[0].id)
        self.assertEqual(
            situation.facts["label"],
            "Page à droite (recto)",
        )
        self.assertEqual(
            situation.facts["classification"],
            "position",
        )
        self.assertEqual(
            situation.facts["physical_side"],
            "recto",
        )
        self.assertFalse(situation.facts["enabled"])

    def test_multiple_rules_on_same_page_form_one_case(self) -> None:
        book, pages = make_book()

        situations = (
            pagination_situation(
                book,
                pages[1].id,
                PAGE_LEFT,
            ),
            pagination_situation(
                book,
                pages[1].id,
                BLANK_BEFORE,
            ),
        )

        cases = group_cases(situations)

        self.assertEqual(len(cases), 1)
        self.assertEqual(
            cases[0].subject_id,
            pages[1].id,
        )
        self.assertEqual(
            [item.kind for item in cases[0].situations],
            [PAGE_LEFT, BLANK_BEFORE],
        )

    def test_double_page_uses_two_explicit_neighbor_ids(self) -> None:
        book, pages = make_book()

        situation = double_page_situation(
            book,
            [pages[0].id, pages[1].id],
        )

        self.assertEqual(
            situation.kind,
            DOUBLE_PAGE,
        )
        self.assertEqual(
            situation.subject_id,
            f"double_page:{pages[0].id}:{pages[1].id}",
        )
        self.assertEqual(
            situation.facts["member_page_ids"],
            (pages[0].id, pages[1].id),
        )
        self.assertTrue(
            situation.facts["valid"],
        )
        self.assertFalse(
            situation.facts["enabled"],
        )

    def test_double_page_keeps_v4_reason_for_invalid_selection(self) -> None:
        book, pages = make_book()

        situation = double_page_situation(
            book,
            [pages[0].id, pages[2].id],
        )

        self.assertFalse(
            situation.facts["valid"],
        )
        self.assertIn(
            "voisines",
            situation.facts["reason"],
        )

    def test_double_page_similarity_is_forbidden(self) -> None:
        with self.assertRaises(ValueError):
            similar_pagination_page_ids(
                object(),
                "page-1",
                DOUBLE_PAGE,
            )


if __name__ == "__main__":
    unittest.main()