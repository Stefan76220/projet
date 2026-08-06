from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.library.page_types.page_type import PageType
from src.library.page_types.page_type_library import PageTypeLibrary


class PageTypeLibraryTests(unittest.TestCase):
    """Vérifie la bibliothèque sans toucher aux données réelles du projet."""

    def setUp(self) -> None:
        self._temporary_directory = TemporaryDirectory()
        self.library = PageTypeLibrary()
        self.library.storage_path = Path(self._temporary_directory.name)

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def test_save_then_load_restores_page_type(self) -> None:
        page_type = PageType(
            id="test_text_page",
            name="Page de texte de test",
            description="Type temporaire utilisé uniquement par les tests.",
        )

        self.library.add(page_type)
        self.library.save()

        self.assertTrue(
            (self.library.storage_path / "test_text_page.json").is_file()
        )

        self.library.clear()
        self.assertEqual(self.library.all(), [])

        self.library.load()

        restored = self.library.get("test_text_page")
        self.assertIsNotNone(restored)
        self.assertEqual(restored.name, "Page de texte de test")
        self.assertEqual(
            restored.description,
            "Type temporaire utilisé uniquement par les tests.",
        )

    def test_load_creates_defaults_only_inside_temporary_directory(self) -> None:
        self.library.load()

        self.assertTrue(self.library.exists("text_page"))
        self.assertTrue(self.library.exists("image_page"))
        self.assertTrue(self.library.exists("chapter_page"))
        self.assertTrue(
            (self.library.storage_path / "text_page.json").is_file()
        )


if __name__ == "__main__":
    unittest.main()