from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import unittest

from src.v4.canvas_editor_document import build_canvas_editor_document
from src.v4.canvas_editor_payload import build_canvas_editor_payload
from src.v4.canvas_loading import prepare_canvas_load
from src.v4.docx_phase1 import analyze_docx_phase1
from src.v4.general_text_rules_runtime import apply_rules_to_plan, set_plans_mode


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "Livres_test" / "TL_DOCX_TEST_REFERENCE_01.docx"


class ContentFirstImportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.phase1 = analyze_docx_phase1(FIXTURE)
        cls.prepared = prepare_canvas_load(FIXTURE, project_root=ROOT)
        cls.payload = build_canvas_editor_payload(cls.prepared.canvas.contract)

    def test_fixture_content_is_fully_inventoried(self) -> None:
        document = self.phase1.model["document"]
        self.assertEqual(self.phase1.paragraph_count, 67)
        self.assertEqual(document["table_count"], 2)
        self.assertEqual(document["placed_image_count"], 2)
        self.assertEqual(document["section_count"], 3)

    def test_canvas_contract_preserves_content_counts(self) -> None:
        self.assertTrue(self.prepared.phase2.ready_for_canvas)
        self.assertTrue(self.prepared.canvas.valid)
        self.assertTrue(self.payload.valid, self.payload.errors)
        coverage = self.prepared.canvas.contract["coverage"]
        translated = self.payload.payload["translated_counts"]
        self.assertEqual(translated["paragraphs"], coverage["paragraphs"])
        self.assertEqual(translated["tables"], coverage["tables"])
        self.assertEqual(translated["images"], coverage["images"])
        document = build_canvas_editor_document(self.payload.payload)
        self.assertTrue(document.valid, document.errors)

    def test_working_font_is_neutral_but_source_font_is_kept(self) -> None:
        render_fonts: set[str] = set()
        source_fonts: set[str] = set()

        def walk(items):
            for item in items:
                if not isinstance(item, dict):
                    continue
                if item.get("font"):
                    render_fonts.add(str(item["font"]))
                extension = item.get("extension")
                tl = extension.get("tomelinea") if isinstance(extension, dict) else None
                if isinstance(tl, dict) and tl.get("sourceFontFamily"):
                    source_fonts.add(str(tl["sourceFontFamily"]))
                nested = item.get("valueList")
                if isinstance(nested, list):
                    walk(nested)

        for section in self.payload.payload["sections"]:
            walk(section["data"]["main"])

        self.assertEqual(render_fonts, {"Arial"})
        self.assertTrue(source_fonts)

    def test_images_are_logical_source_markers(self) -> None:
        markers = []

        def walk(items):
            for item in items:
                if not isinstance(item, dict):
                    continue
                extension = item.get("extension")
                tl = extension.get("tomelinea") if isinstance(extension, dict) else None
                if item.get("type") == "image" and isinstance(tl, dict):
                    markers.append((item.get("imgDisplay"), tl.get("placementStatus")))
                nested = item.get("valueList")
                if isinstance(nested, list):
                    walk(nested)

        for section in self.payload.payload["sections"]:
            walk(section["data"]["main"])

        self.assertEqual(len(markers), 2)
        self.assertTrue(all(display == "inline" for display, _status in markers))
        self.assertTrue(all(status == "source_marker_pending_tomelinea_decision" for _display, status in markers))


class GeneralRulesTests(unittest.TestCase):
    def test_rules_do_not_invent_tabs_or_blank_paragraphs(self) -> None:
        plan = {
            "render_segments": [{
                "data": {
                    "main": [{
                        "value": "Texte courant",
                        "font": "Arial",
                        "size": 14,
                        "extension": {
                            "tomelinea": {
                                "paragraph": {
                                    "id": "p:1",
                                    "format": {"style_id": "Normal"},
                                }
                            }
                        },
                    }, {
                        "value": "\n",
                        "extension": {"tomelinea": {"paragraphEnd": 1, "format": {"style_id": "Normal"}}},
                    }]
                },
                "options": {},
            }]
        }
        before = deepcopy(plan["render_segments"][0]["data"]["main"])
        report = apply_rules_to_plan(plan, {
            "font_family": "Georgia",
            "font_size_pt": 11,
            "alignment": "justify",
            "first_line_indent_mm": 5,
            "line_spacing_multiple": 1.25,
            "paragraph_gap_mm": 3,
            "hyphenation": "forbid",
        })
        after = plan["render_segments"][0]["data"]["main"]
        self.assertEqual(len(after), len(before))
        self.assertFalse(any(item.get("type") == "tab" for item in after))
        self.assertFalse(any(
            isinstance(item.get("extension"), dict)
            and isinstance(item["extension"].get("tomelinea"), dict)
            and item["extension"]["tomelinea"].get("generalTextRuleGenerated")
            for item in after
        ))
        self.assertEqual(after[0]["font"], "Georgia")
        self.assertEqual(after[0]["rowFlex"], "alignment")
        self.assertNotIn("rowMargin", after[0])
        self.assertEqual(report["paragraphs"], 1)
        self.assertIn("first_line_indent_mm", plan["tomelinea_rules"]["deferred_to_composition_engine"])

    def test_readonly_mode_is_metadata_only(self) -> None:
        plans = [{"render_segments": []}]
        set_plans_mode(plans, "readonly")
        self.assertEqual(plans[0]["tomelinea_ui"]["mode"], "readonly")
        set_plans_mode(plans, "edit")
        self.assertEqual(plans[0]["tomelinea_ui"]["mode"], "edit")


if __name__ == "__main__":
    unittest.main()
