from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from src.library.book_models.book_model import BookModel
from src.library.book_models.book_model_library import BookModelLibrary


class BookModelLibraryTests(unittest.TestCase):
    """Vérifie la bibliothèque sans toucher aux données réelles du projet."""

    def setUp(self) -> None:
        self._temporary_directory = TemporaryDirectory()
        self.library = BookModelLibrary()
        self.library.storage_path = Path(self._temporary_directory.name)

    def tearDown(self) -> None:
        self._temporary_directory.cleanup()

    def test_save_then_load_restores_complete_book_model(self) -> None:
        model = BookModel(
            id="guide_plantes_test",
            name="Guide des plantes de test",
            description="Modèle temporaire utilisé uniquement par les tests.",
            page_types=["text_page", "image_page"],
            parameters={"format": "A4", "recto_verso": True},
        )

        self.library.add(model)
        self.library.save()

        self.assertTrue(
            (self.library.storage_path / "guide_plantes_test.json").is_file()
        )

        self.library.clear()
        self.assertEqual(self.library.all(), [])

        self.library.load()

        restored = self.library.get("guide_plantes_test")
        self.assertIsNotNone(restored)
        self.assertEqual(restored.name, "Guide des plantes de test")
        self.assertEqual(
            restored.description,
            "Modèle temporaire utilisé uniquement par les tests.",
        )
        self.assertEqual(restored.page_types, ["text_page", "image_page"])
        self.assertEqual(
            restored.parameters,
            {"format": "A4", "recto_verso": True},
        )

    def test_load_creates_default_only_inside_temporary_directory(self) -> None:
        self.library.load()

        self.assertTrue(self.library.exists("empty_book"))
        self.assertTrue(
            (self.library.storage_path / "empty_book.json").is_file()
        )


if __name__ == "__main__":
    unittest.main()