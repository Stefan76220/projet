from __future__ import annotations

import unittest

import tomelinea.architecture as architecture


class V5ScaffoldTests(unittest.TestCase):
    def test_architecture_version(self) -> None:
        self.assertEqual(architecture.V5_ARCHITECTURE_VERSION, 3)

    def test_core_principles(self) -> None:
        required = {
            "single_book_truth",
            "stable_ids",
            "shared_navigation",
            "survol_uses_navigation",
            "source_separate_from_composition",
            "deterministic_rule_engine",
            "multi_project_types",
            "logical_document_before_book",
            "sequential_editorial_pipeline",
            "stage_scoped_mutations",
            "targeted_invalidation",
            "logical_structure_independent_of_layout",
            "office_layout_engine_behind_adapter",
            "render_is_projection_not_truth",
        }
        self.assertTrue(required.issubset(set(architecture.PRINCIPLES)))


if __name__ == "__main__":
    unittest.main()