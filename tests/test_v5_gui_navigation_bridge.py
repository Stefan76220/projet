from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import main_v5

from src.gui_v4.settings_shell import TomeLineaV4SettingsStage
from src.gui_v5 import TomeLineaV5RomanStage

from tomelinea.book import Book, Page
from tomelinea.project_types.roman import RomanSession


class V5GuiNavigationBridgeTests(unittest.TestCase):
    def make_shell(
        self,
        book: Book,
    ):
        project = SimpleNamespace(
            book=book,
        )
        workspace = SimpleNamespace(
            project=project,
            book=book,
        )

        shell = object.__new__(
            TomeLineaV5RomanStage
        )
        shell.session = workspace
        shell._v5_roman_session = None
        shell._v5_roman_project = None
        shell._v5_roman_book = None

        return (
            shell,
            project,
            workspace,
        )

    def test_v5_shell_reuses_validated_v4_shell(self) -> None:
        self.assertTrue(
            issubclass(
                TomeLineaV5RomanStage,
                TomeLineaV4SettingsStage,
            )
        )

    def test_main_v5_has_its_own_entry_point(self) -> None:
        self.assertTrue(
            callable(
                main_v5.main
            )
        )
        self.assertTrue(
            Path(
                "main_v5.py"
            ).exists()
        )

    def test_activate_page_records_common_navigation_before_v4_render(self) -> None:
        book = Book(
            title="Pont Navigation",
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

        shell, project, workspace = self.make_shell(
            book
        )

        calls = []

        def fake_v4_activate(
            current_self,
            page_id,
            *,
            preserve_page_selection=False,
        ):
            roman = current_self.v5_roman_session

            self.assertIsNotNone(
                roman
            )
            self.assertEqual(
                roman.navigation.requested_page_id,
                page_id,
            )

            calls.append(
                (
                    page_id,
                    preserve_page_selection,
                )
            )

        with patch.object(
            TomeLineaV4SettingsStage,
            "_activate_page",
            new=fake_v4_activate,
        ):
            shell._activate_page(
                second.id,
                preserve_page_selection=True,
            )

        self.assertEqual(
            calls,
            [
                (
                    second.id,
                    True,
                )
            ],
        )
        self.assertEqual(
            shell.v5_roman_session.navigation.requested_page_id,
            second.id,
        )

    def test_all_repeated_ui_navigation_reuses_same_roman_session(self) -> None:
        book = Book(
            title="Une session",
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

        shell, project, workspace = self.make_shell(
            book
        )

        with patch.object(
            TomeLineaV4SettingsStage,
            "_activate_page",
            return_value=None,
        ):
            shell._activate_page(
                first.id
            )
            roman = shell.v5_roman_session

            shell._activate_page(
                second.id
            )

        self.assertIs(
            shell.v5_roman_session,
            roman,
        )
        self.assertIs(
            roman.project,
            project,
        )
        self.assertIs(
            roman.book,
            book,
        )
        self.assertEqual(
            roman.navigation.requested_page_id,
            second.id,
        )
        self.assertEqual(
            roman.navigation.generation,
            2,
        )

    def test_project_change_replaces_roman_session_not_book_truth(self) -> None:
        first_book = Book(
            title="Premier",
        )
        first_page = Page(
            title="Page 1",
        )
        first_book.add_page(
            first_page
        )

        shell, first_project, workspace = self.make_shell(
            first_book
        )

        with patch.object(
            TomeLineaV4SettingsStage,
            "_activate_page",
            return_value=None,
        ):
            shell._activate_page(
                first_page.id
            )

        old_roman = shell.v5_roman_session

        second_book = Book(
            title="Second",
        )
        second_page = Page(
            title="Page 2",
        )
        second_book.add_page(
            second_page
        )
        second_project = SimpleNamespace(
            book=second_book,
        )

        workspace.project = second_project
        workspace.book = second_book

        with patch.object(
            TomeLineaV4SettingsStage,
            "_activate_page",
            return_value=None,
        ):
            shell._activate_page(
                second_page.id
            )

        self.assertIsNot(
            shell.v5_roman_session,
            old_roman,
        )
        self.assertIs(
            shell.v5_roman_session.book,
            second_book,
        )
        self.assertIs(
            shell.v5_roman_session.project,
            second_project,
        )

    def test_source_only_project_does_not_create_fake_roman_session(self) -> None:
        project = SimpleNamespace(
            book=None,
        )
        shell = object.__new__(
            TomeLineaV5RomanStage
        )
        shell.session = SimpleNamespace(
            project=project,
        )
        shell._v5_roman_session = None
        shell._v5_roman_project = None
        shell._v5_roman_book = None

        self.assertIsNone(
            shell._v5_ensure_roman_session()
        )

    def test_gui_v5_does_not_define_a_second_navigation_class(self) -> None:
        import src.gui_v5.roman_shell as module

        self.assertFalse(
            hasattr(
                module,
                "NavigationState",
            )
        )
        self.assertFalse(
            hasattr(
                module,
                "SurvolState",
            )
        )


if __name__ == "__main__":
    unittest.main()