from __future__ import annotations

import unittest
from pathlib import Path

from tomelinea.document import (
    TLDOCUMENT_SCHEMA,
    TLDOCUMENT_VERSION,
    build_tldocument_from_docx,
)


class V5TLDocumentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = (
            Path(__file__).resolve().parent
            / "Livres_test"
            / "TL_DOCX_TEST_REFERENCE_01.docx"
        )
        if not cls.fixture.is_file():
            raise FileNotFoundError(cls.fixture)
        cls.document, cls.report = build_tldocument_from_docx(cls.fixture)

    def test_schema(self) -> None:
        self.assertEqual(self.document.schema, TLDOCUMENT_SCHEMA)
        self.assertEqual(self.document.schema_version, TLDOCUMENT_VERSION)

    def test_phase1_to_tldocument_is_lossless_for_core_objects(self) -> None:
        checks = self.report.checks
        self.assertTrue(checks["Phase1 -> TLDocument : paragraphes"])
        self.assertTrue(checks["Phase1 -> TLDocument : texte exact"])
        self.assertTrue(checks["Phase1 -> TLDocument : tableaux"])
        self.assertTrue(checks["Phase1 -> TLDocument : images"])
        self.assertTrue(checks["Phase1 -> TLDocument : sections"])

    def test_ooxml_text_and_counts_reach_phase1(self) -> None:
        checks = self.report.checks
        self.assertTrue(checks["OOXML -> Phase1 : nombre de paragraphes"])
        self.assertTrue(checks["OOXML -> Phase1 : texte exact des paragraphes"])
        self.assertTrue(checks["OOXML -> Phase1 : nombre de tableaux"])

    def test_ids_are_stable_and_not_page_based(self) -> None:
        first = min(
            self.document.paragraphs.values(),
            key=lambda item: item.source_paragraph,
        )
        self.assertTrue(first.id.startswith("p:"))
        self.assertNotIn("page", first.id.lower())

    def test_document_validates(self) -> None:
        self.document.validate()


if __name__ == "__main__":
    unittest.main()
