from __future__ import annotations

import unittest

from tomelinea.book import Book, Page
from tomelinea.navigation import NavigationState, NavigationTarget


def make_book(count: int = 4) -> tuple[Book, list[Page]]:
    book = Book(title="Navigation V5-05")
    pages: list[Page] = []

    for index in range(count):
        page = Page(title=f"Page {index + 1}")
        book.add_page(page)
        pages.append(page)

    return book, pages


class V5NavigationTests(unittest.TestCase):
    def test_request_page_uses_stable_book_identity(self) -> None:
        book, pages = make_book()

        navigation = NavigationState()
        target = navigation.request_page(book, pages[2].id)

        self.assertIsInstance(target, NavigationTarget)
        self.assertEqual(target.page_id, pages[2].id)
        self.assertEqual(target.global_index, 2)
        self.assertEqual(navigation.requested_page_id, pages[2].id)
        self.assertEqual(navigation.requested_index, 2)

    def test_last_request_wins_without_queue(self) -> None:
        book, pages = make_book()
        navigation = NavigationState()

        first = navigation.request_page(book, pages[0].id)
        second = navigation.request_page(book, pages[1].id)
        third = navigation.request_page(book, pages[3].id)

        self.assertEqual(first.generation, 1)
        self.assertEqual(second.generation, 2)
        self.assertEqual(third.generation, 3)
        self.assertEqual(navigation.generation, 3)
        self.assertIs(navigation.target, third)
        self.assertEqual(navigation.requested_page_id, pages[3].id)

        # Le contrat ne contient volontairement aucune collection de demandes.
        self.assertFalse(hasattr(navigation, "queue"))
        self.assertFalse(hasattr(navigation, "requests"))

    def test_previous_and_next_share_the_same_request_contract(self) -> None:
        book, pages = make_book()
        navigation = NavigationState()

        next_target = navigation.request_neighbor(
            book,
            pages[1].id,
            +1,
        )
        self.assertIsNotNone(next_target)
        self.assertEqual(next_target.page_id, pages[2].id)

        previous_target = navigation.request_neighbor(
            book,
            pages[2].id,
            -1,
        )
        self.assertIsNotNone(previous_target)
        self.assertEqual(previous_target.page_id, pages[1].id)

    def test_neighbor_stops_at_book_bounds(self) -> None:
        book, pages = make_book()
        navigation = NavigationState()

        self.assertIsNone(
            navigation.request_neighbor(
                book,
                pages[0].id,
                -1,
            )
        )
        self.assertIsNone(
            navigation.request_neighbor(
                book,
                pages[-1].id,
                +1,
            )
        )

    def test_request_index_is_strict_for_user_level_navigation(self) -> None:
        book, pages = make_book()
        navigation = NavigationState()

        target = navigation.request_index(book, 1)
        self.assertEqual(target.page_id, pages[1].id)

        with self.assertRaises(IndexError):
            navigation.request_index(book, -1)

        with self.assertRaises(IndexError):
            navigation.request_index(book, len(pages))

    def test_unknown_or_unordered_page_is_rejected(self) -> None:
        book, pages = make_book()
        navigation = NavigationState()

        with self.assertRaises(KeyError):
            navigation.request_page(book, "page-inconnue")

        removed_from_order = pages[2].id
        book.page_order.remove(removed_from_order)

        with self.assertRaises(ValueError):
            navigation.request_page(
                book,
                removed_from_order,
            )

    def test_page_move_changes_index_not_identity(self) -> None:
        book, pages = make_book()
        navigation = NavigationState()

        stable_id = pages[3].id

        # Mouvement volontaire direct de l'ordre pour tester uniquement
        # le contrat Navigation, sans imposer ici la logique Structure V4.
        book.page_order.remove(stable_id)
        book.page_order.insert(1, stable_id)

        target = navigation.request_page(
            book,
            stable_id,
        )

        self.assertEqual(target.page_id, stable_id)
        self.assertEqual(target.global_index, 1)

    def test_clear_does_not_change_book(self) -> None:
        book, pages = make_book()
        navigation = NavigationState()

        original_order = list(book.page_order)
        navigation.request_page(book, pages[1].id)
        navigation.clear()

        self.assertIsNone(navigation.target)
        self.assertEqual(book.page_order, original_order)
        self.assertIn(pages[1].id, book.pages)


if __name__ == "__main__":
    unittest.main()