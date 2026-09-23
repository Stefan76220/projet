from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from src.v4.domain import BookV4, PageV4, PartV4
from src.v4.project import ProjectV4
from src.v4.source import SourceV4

from tomelinea.app import Project
from tomelinea.book import Book, Page, Part
from tomelinea.source import Source


class V5CoreEquivalenceTests(unittest.TestCase):
    def test_public_v5_names_use_frozen_v4_engines(self) -> None:
        self.assertIs(Source, SourceV4)
        self.assertIs(Book, BookV4)
        self.assertIs(Page, PageV4)
        self.assertIs(Part, PartV4)
        self.assertIs(Project, ProjectV4)

    def test_source_registers_real_file_without_parallel_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source_test.docx"
            path.write_bytes(b"TomeLinea V5-02")

            source = Source()
            element = source.register_file(path)

            self.assertIn(element.id, source.elements)
            self.assertIs(source.elements[element.id], element)
            self.assertIsNotNone(element.active_version)
            self.assertEqual(element.active_version.original_name, "source_test.docx")
            self.assertEqual(element.active_version.size_bytes, len(b"TomeLinea V5-02"))
            source.validate()

    def test_book_keeps_stable_object_identity(self) -> None:
        book = Book(title="Livre V5-02")
        part = Part(title="Chapitre 1", part_type="chapitre")
        book.add_part(part)

        page = Page(title="Page initiale", part_id=part.id)
        book.add_page(page)

        original_page_id = page.id
        original_part_id = part.id

        page.title = "Page renommee"
        part.title = "Chapitre renomme"

        self.assertEqual(page.id, original_page_id)
        self.assertEqual(part.id, original_part_id)
        self.assertIs(book.pages[page.id], page)
        self.assertIs(book.parts[part.id], part)
        self.assertEqual(book.page_order, [page.id])
        self.assertEqual(book.part_order, [part.id])
        book.validate()

    def test_project_uses_the_same_book_instance(self) -> None:
        project = Project(title="Projet V5-02")
        book = Book(title="Livre central")

        project.set_book(book)

        self.assertIs(project.book, book)
        self.assertIsInstance(project.source, Source)
        self.assertEqual(project.history[-1]["book_id"], book.id)
        project.validate()


if __name__ == "__main__":
    unittest.main()