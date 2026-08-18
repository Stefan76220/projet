from __future__ import annotations

import ast
import json
from pathlib import Path
import unittest

from src.gui_v3.book_canvas import BookCanvas
from src.gui_v3.page_visual_catalog import PAGE_VISUAL_CATALOG
from src.gui_v3.structure_catalog import CATALOG_BY_TYPE, STRUCTURE_ORDER, structure_builtin_catalog
from src.gui_v3.structure_core import migrate_structure_data, structure_integrity_issues


ROOT = Path(__file__).resolve().parents[1]


class StructureStage1Tests(unittest.TestCase):
    def test_catalogue_structure_has_one_canonical_source(self):
        builtins = structure_builtin_catalog()
        keys = [str(entry.get("type") or "") for entry in builtins]
        self.assertEqual(keys, list(STRUCTURE_ORDER))
        self.assertEqual(len(keys), len(set(keys)))
        for key in keys:
            self.assertIn(key, CATALOG_BY_TYPE)

    def test_visual_catalog_uses_canonical_definitions(self):
        for entry in PAGE_VISUAL_CATALOG:
            key = str(entry.get("type") or "")
            self.assertIn(key, CATALOG_BY_TYPE)

    def test_legacy_page_auto_migration(self):
        old = {
            "automatic_follow_rules": {"chapitre": "page_blanche"},
            "page_auto_type_rules": {
                "chapitre": {"before": "citation"},
                "texte": {"after": "illustration"},
            },
            "items": [
                {"id": "p1", "type": "chapitre", "auto_follow_override": "__none__"},
                {
                    "id": "a1", "type": "page_blanche", "automatic": True,
                    "automatic_kind": "follow_rule", "parent_id": "p1",
                },
            ],
        }
        new, changed = migrate_structure_data(old)
        self.assertTrue(changed)
        self.assertNotIn("automatic_follow_rules", new)
        self.assertEqual(new["page_auto_type_rules"]["chapitre"]["before"], "citation")
        self.assertEqual(new["page_auto_type_rules"]["chapitre"]["after"], "page_blanche")
        self.assertEqual(new["page_auto_type_rules"]["texte"]["after"], "illustration")
        self.assertNotIn("auto_follow_override", new["items"][0])
        self.assertEqual(new["items"][0]["page_auto_after_override"], "__none__")
        self.assertEqual(new["items"][1]["automatic_kind"], "page_auto_after")

    def test_new_after_rule_has_priority_over_legacy_rule(self):
        old = {
            "automatic_follow_rules": {"chapitre": "page_blanche"},
            "page_auto_type_rules": {"chapitre": {"after": "illustration"}},
        }
        new, _changed = migrate_structure_data(old)
        self.assertEqual(new["page_auto_type_rules"]["chapitre"]["after"], "illustration")

    def test_before_and_after_remain_independent(self):
        canvas = BookCanvas.__new__(BookCanvas)
        canvas._data = {
            "page_auto_type_rules": {
                "chapitre": {"before": "citation", "after": "page_blanche"}
            }
        }
        canvas.project = None
        canvas.structure_auto_target_options = lambda: [
            ("citation", "Citation"), ("page_blanche", "Page blanche")
        ]
        canvas._sync_all_page_auto = lambda **kwargs: False
        self.assertTrue(canvas.structure_remove_page_auto_type_rule("chapitre", "before"))
        self.assertEqual(canvas.structure_get_page_auto_type_rule("chapitre", "before"), "")
        self.assertEqual(canvas.structure_get_page_auto_type_rule("chapitre", "after"), "page_blanche")

    def test_part_numbers_are_recomputed_from_real_order(self):
        canvas = BookCanvas.__new__(BookCanvas)
        canvas.groups = [
            {"id": canvas.START_GROUP_ID, "title": "Début du livre"},
            {"id": "p-a", "title": "Partie 9"},
            {"id": "p-b", "title": "Partie 9"},
            {"id": "p-c", "title": "Partie 2"},
            {"id": canvas.END_GROUP_ID, "title": "Fin du livre"},
        ]
        self.assertTrue(canvas._structure_renumber_parts())
        self.assertEqual(
            [g["title"] for g in canvas.groups[1:-1]],
            ["Partie 1", "Partie 2", "Partie 3"],
        )

    def test_auto_page_drag_resolves_to_parent_block(self):
        canvas = BookCanvas.__new__(BookCanvas)
        canvas.items = [
            {"id": "main", "type": "chapitre"},
            {
                "id": "auto", "type": "page_blanche", "automatic": True,
                "automatic_kind": "page_auto_after", "parent_id": "main",
            },
            {"id": "other", "type": "texte"},
        ]
        block = canvas._drag_block_indices(1)
        self.assertEqual(block, [0, 1])

    def test_reference_book_fixture_is_structurally_coherent(self):
        fixture = json.loads(
            (ROOT / "tests" / "fixtures" / "structure_reference_book.json").read_text(encoding="utf-8")
        )
        self.assertEqual(structure_integrity_issues(fixture), [])

    def test_book_canvas_contains_no_old_page_auto_engine(self):
        source = (ROOT / "src" / "gui_v3" / "book_canvas.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        old_methods = {
            "structure_general_auto_rules", "structure_get_general_auto_rule",
            "structure_set_general_auto_rule", "structure_remove_general_auto_rule",
            "_auto_follow_rule_target_for_item", "_auto_follow_generated_for_parent",
            "_sync_auto_follow_for_source", "_sync_all_auto_follow",
            "structure_selected_auto_context", "structure_set_selected_auto_override",
        }
        found = {
            node.name for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name in old_methods
        }
        self.assertEqual(found, set())
        self.assertNotIn('"automatic_follow_rules"', source)
        self.assertNotIn('"auto_follow_override"', source)


if __name__ == "__main__":
    unittest.main()
