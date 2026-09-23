from __future__ import annotations

import unittest

from src.v4 import canvas_contract as v4_canvas
from src.v4 import composition as v4_composition

from tomelinea.book import Book, BookFormat, Page
from tomelinea.canvas import ContractResult, build_contract
from tomelinea import canvas as v5_canvas
from tomelinea import composition as v5_composition


class V5CompositionCanvasEquivalenceTests(unittest.TestCase):
    def test_composition_public_api_uses_frozen_v4_engine(self) -> None:
        self.assertEqual(
            v5_composition.COMPOSITION_SCHEMA,
            v4_composition.COMPOSITION_SCHEMA,
        )
        self.assertEqual(
            v5_composition.COMPOSITION_VERSION,
            v4_composition.COMPOSITION_VERSION,
        )
        self.assertIs(v5_composition.add_element, v4_composition.add_element)
        self.assertIs(
            v5_composition.update_element_geometry,
            v4_composition.update_element_geometry,
        )
        self.assertIs(
            v5_composition.remove_element,
            v4_composition.remove_element,
        )
        self.assertIs(
            v5_composition.frame_bounds,
            v4_composition.frame_bounds,
        )

    def test_composition_writes_into_the_single_book(self) -> None:
        book = Book(title="Livre V5-04")
        page = Page(title="Page 1")
        book.add_page(page)

        element = v5_composition.add_element(
            book,
            page.id,
            kind=v5_composition.TEXT,
            x_mm=20.0,
            y_mm=25.0,
            width_mm=80.0,
            height_mm=30.0,
            payload={"text": "TomeLinea"},
        )

        self.assertIs(page.content[0], element)
        self.assertEqual(element["geometry"]["x_mm"], 20.0)
        self.assertEqual(element["geometry"]["width_mm"], 80.0)
        self.assertEqual(element["payload"]["text"], "TomeLinea")
        self.assertEqual(
            page.modifications[-1]["element_id"],
            element["id"],
        )
        self.assertEqual(
            book.history[-1]["element_id"],
            element["id"],
        )
        self.assertEqual(v5_composition.composition_issues(book), [])

    def test_geometry_update_keeps_element_identity(self) -> None:
        book = Book()
        page = Page()
        book.add_page(page)

        element = v5_composition.add_element(
            book,
            page.id,
            kind=v5_composition.IMAGE,
            x_mm=10,
            y_mm=10,
            width_mm=40,
            height_mm=30,
        )
        stable_id = element["id"]

        updated = v5_composition.update_element_geometry(
            book,
            page.id,
            stable_id,
            x_mm=15,
            rotation_deg=12,
        )

        self.assertIs(updated, element)
        self.assertEqual(updated["id"], stable_id)
        self.assertEqual(updated["geometry"]["x_mm"], 15.0)
        self.assertEqual(updated["geometry"]["rotation_deg"], 12.0)

    def test_margin_frame_uses_real_physical_parity(self) -> None:
        book = Book(
            format=BookFormat(
                width_mm=148,
                height_mm=210,
                margin_top_mm=15,
                margin_bottom_mm=15,
                margin_inside_mm=20,
                margin_outside_mm=10,
            )
        )

        first = Page(title="Recto")
        second = Page(title="Verso")
        book.add_page(first)
        book.add_page(second)

        first_bounds = v5_composition.frame_bounds(
            book,
            first.id,
            v5_composition.MARGINS,
        )
        second_bounds = v5_composition.frame_bounds(
            book,
            second.id,
            v5_composition.MARGINS,
        )

        self.assertEqual(first_bounds, (20.0, 15.0, 118.0, 180.0))
        self.assertEqual(second_bounds, (10.0, 15.0, 118.0, 180.0))

    def test_canvas_public_api_uses_frozen_v4_contract(self) -> None:
        self.assertIs(ContractResult, v4_canvas.CanvasContractResult)
        self.assertIs(build_contract, v4_canvas.build_canvas_contract)
        self.assertEqual(v5_canvas.CANVAS_SCHEMA, v4_canvas.CANVAS_SCHEMA)
        self.assertEqual(
            v5_canvas.CANVAS_SCHEMA_VERSION,
            v4_canvas.CANVAS_SCHEMA_VERSION,
        )

    def test_canvas_contract_translates_without_owning_pagination(self) -> None:
        model = {
            "schema": v5_canvas.PHASE2_SCHEMA,
            "readiness": {
                "ready_for_canvas": True,
                "canvas_created": False,
            },
            "source": {
                "name": "test.docx",
            },
            "fonts": {
                "requirements": [],
                "resolution": [],
            },
            "resources": {
                "images": [],
                "hyperlinks": [],
                "bookmarks": [],
                "content_controls": [],
                "tracked_changes": {},
                "tracked_change_ranges": [],
                "footnotes": [],
                "endnotes": [],
                "comments": [],
                "headers_footers": [],
            },
            "flow": [
                {
                    "kind": "paragraph",
                    "source_paragraph": 1,
                    "text": "Bonjour TomeLinea",
                    "style_chain": [],
                    "effective": {},
                    "direct": {},
                    "runs": [
                        {
                            "run": 1,
                            "text": "Bonjour TomeLinea",
                            "effective": {},
                            "direct": {},
                            "controls": [],
                        }
                    ],
                }
            ],
            "sections": [],
            "counts": {
                "paragraph_blocks": 1,
                "table_blocks": 0,
                "sections": 0,
            },
        }

        result = build_contract(model)

        self.assertTrue(result.valid)
        self.assertEqual(result.errors, ())
        self.assertEqual(
            result.contract["schema"],
            v5_canvas.CANVAS_SCHEMA,
        )
        self.assertEqual(
            result.contract["coverage"]["paragraphs"],
            1,
        )
        self.assertTrue(
            result.contract["layout_policy"]["canvas_owns_pagination"]
        )
        self.assertFalse(
            result.contract["layout_policy"]["manual_line_coordinates"]
        )
        self.assertFalse(
            result.contract["readiness"]["canvas_created"]
        )


if __name__ == "__main__":
    unittest.main()