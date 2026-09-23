from __future__ import annotations

import unittest

from tomelinea.book import Book, Page
from tomelinea.navigation import NavigationState
from tomelinea.survol import SurvolState


def make_book(count: int = 4) -> tuple[Book, list[Page]]:
    book = Book(title="Survol V5-06")
    pages: list[Page] = []

    for index in range(count):
        page = Page(title=f"Page {index + 1}")
        book.add_page(page)
        pages.append(page)

    return book, pages


class V5SurvolTests(unittest.TestCase):
    def test_survol_requires_shared_navigation(self) -> None:
        with self.assertRaises(TypeError):
            SurvolState(object())  # type: ignore[arg-type]

    def test_start_requests_first_page_through_navigation(self) -> None:
        book, pages = make_book()
        navigation = NavigationState()
        survol = SurvolState(navigation)

        target = survol.start(book)

        self.assertTrue(survol.running)
        self.assertTrue(survol.started)
        self.assertFalse(survol.completed)
        self.assertIsNotNone(target)
        self.assertIs(survol.navigation, navigation)
        self.assertIs(navigation.target, target)
        self.assertEqual(target.page_id, pages[0].id)

    def test_advance_uses_same_navigation_and_completes_on_last_page(self) -> None:
        book, pages = make_book(3)
        navigation = NavigationState()
        survol = SurvolState(navigation)

        survol.start(book)

        second = survol.advance(book)
        self.assertEqual(second.page_id, pages[1].id)
        self.assertIs(navigation.target, second)

        third = survol.advance(book)
        self.assertEqual(third.page_id, pages[2].id)
        self.assertIs(navigation.target, third)

        end = survol.advance(book)
        self.assertIsNone(end)
        self.assertFalse(survol.running)
        self.assertTrue(survol.started)
        self.assertTrue(survol.completed)

        # La Navigation partagee conserve simplement sa derniere destination.
        self.assertEqual(navigation.requested_page_id, pages[2].id)

    def test_pause_does_not_create_navigation_request(self) -> None:
        book, pages = make_book()
        navigation = NavigationState()
        survol = SurvolState(navigation)

        survol.start(book)
        generation_before = navigation.generation

        survol.pause(
            book,
            active_page_id=pages[0].id,
        )

        self.assertFalse(survol.running)
        self.assertTrue(survol.started)
        self.assertEqual(navigation.generation, generation_before)
        self.assertEqual(navigation.requested_page_id, pages[0].id)

    def test_resume_realigns_on_active_page_then_uses_navigation(self) -> None:
        book, pages = make_book()
        navigation = NavigationState()
        survol = SurvolState(navigation)

        survol.start(book)
        survol.pause(
            book,
            active_page_id=pages[2].id,
        )

        target = survol.resume(
            book,
            active_page_id=pages[2].id,
        )

        self.assertTrue(survol.running)
        self.assertEqual(survol.position, 2)
        self.assertEqual(target.page_id, pages[2].id)
        self.assertIs(navigation.target, target)

    def test_stop_does_not_clear_shared_navigation(self) -> None:
        book, pages = make_book()
        navigation = NavigationState()
        survol = SurvolState(navigation)

        survol.start(book)
        requested = navigation.target

        survol.stop(
            book,
            active_page_id=pages[0].id,
        )

        self.assertFalse(survol.running)
        self.assertFalse(survol.started)
        self.assertFalse(survol.completed)
        self.assertIs(navigation.target, requested)

    def test_empty_book_does_not_request_navigation(self) -> None:
        book = Book()
        navigation = NavigationState()
        survol = SurvolState(navigation)

        self.assertIsNone(survol.start(book))
        self.assertIsNone(navigation.target)
        self.assertFalse(survol.running)

    def test_survol_has_no_parallel_page_engine(self) -> None:
        navigation = NavigationState()
        survol = SurvolState(navigation)

        forbidden = {
            "webview",
            "canvas",
            "buffer",
            "preload",
            "polling",
            "centering",
            "queue",
        }

        slots = {
            str(name).lower()
            for name in SurvolState.__slots__
        }

        self.assertTrue(forbidden.isdisjoint(slots))
        self.assertFalse(hasattr(survol, "go_to_page"))
        self.assertFalse(hasattr(survol, "page_changed"))

    def test_page_order_is_read_from_book_each_time(self) -> None:
        book, pages = make_book(3)
        navigation = NavigationState()
        survol = SurvolState(navigation)

        survol.start(book)

        # La Structure change ; Survol ne possede aucune copie de l'ordre.
        book.page_order[1], book.page_order[2] = (
            book.page_order[2],
            book.page_order[1],
        )

        target = survol.advance(book)

        self.assertEqual(target.page_id, pages[2].id)
        self.assertEqual(survol.page_order(book), list(book.page_order))


if __name__ == "__main__":
    unittest.main()