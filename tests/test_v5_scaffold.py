from __future__ import annotations

import unittest

import tomelinea.architecture as architecture


class V5ScaffoldTests(unittest.TestCase):
    def test_architecture_version(self) -> None:
        self.assertEqual(architecture.V5_ARCHITECTURE_VERSION, 1)

    def test_core_principles(self) -> None:
        required = {
            "single_book_truth",
            "stable_ids",
            "shared_navigation",
            "survol_uses_navigation",
            "source_separate_from_composition",
            "deterministic_rule_engine",
            "multi_project_types",
        }
        self.assertTrue(required.issubset(set(architecture.PRINCIPLES)))


if __name__ == "__main__":
    unittest.main()