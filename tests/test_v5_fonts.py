from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tomelinea.fonts import (
    CORE_FONT_FAMILIES,
    ORIGIN_CORE,
    ORIGIN_SYSTEM,
    ORIGIN_USER,
    FontFace,
    core_font_root,
    prepare_library,
    resolve_font,
    resolve_requirements,
    unresolved_requirements,
    user_font_root,
)


class V5FontsTests(unittest.TestCase):
    def test_catalog_keeps_the_45_validated_families(self) -> None:
        self.assertEqual(len(CORE_FONT_FAMILIES), 45)

        names = {item.family for item in CORE_FONT_FAMILIES}
        self.assertIn("EB Garamond", names)
        self.assertIn("Source Serif 4", names)
        self.assertIn("Inter", names)
        self.assertIn("Atkinson Hyperlegible", names)

    def test_prepare_library_creates_core_user_and_catalog_without_fonts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)

            payload = prepare_library(root)

            self.assertTrue(core_font_root(root).is_dir())
            self.assertTrue(user_font_root(root).is_dir())

            catalog = root / "resources" / "fonts" / "catalog.json"
            self.assertTrue(catalog.is_file())

            data = json.loads(catalog.read_text(encoding="utf-8"))
            self.assertEqual(data["download_policy"], "explicit_only")
            self.assertEqual(
                data["resolution_priority"],
                ["system", "core", "user"],
            )
            self.assertEqual(len(data["families"]), 45)
            self.assertEqual(payload["catalog_version"], data["catalog_version"])

            font_files = list(
                (root / "resources" / "fonts").rglob("*.ttf")
            )
            self.assertEqual(font_files, [])

    def test_system_has_priority_over_core_and_user(self) -> None:
        inventory = (
            FontFace("Test Family", "regular", "user.ttf", ORIGIN_USER),
            FontFace("Test Family", "regular", "core.ttf", ORIGIN_CORE),
            FontFace("Test Family", "regular", "system.ttf", ORIGIN_SYSTEM),
        )

        resolved = resolve_font(
            "Test Family",
            "regular",
            inventory=inventory,
        )

        self.assertEqual(resolved.status, "exact")
        self.assertEqual(resolved.origin, ORIGIN_SYSTEM)
        self.assertEqual(resolved.path, "system.ttf")

    def test_core_has_priority_over_user_when_system_is_absent(self) -> None:
        inventory = (
            FontFace("Test Family", "regular", "user.ttf", ORIGIN_USER),
            FontFace("Test Family", "regular", "core.ttf", ORIGIN_CORE),
        )

        resolved = resolve_font(
            "Test Family",
            "regular",
            inventory=inventory,
        )

        self.assertEqual(resolved.origin, ORIGIN_CORE)
        self.assertEqual(resolved.path, "core.ttf")

    def test_missing_style_is_not_silently_replaced(self) -> None:
        inventory = (
            FontFace("Test Family", "regular", "system.ttf", ORIGIN_SYSTEM),
        )

        resolved = resolve_font(
            "Test Family",
            "bold",
            inventory=inventory,
        )

        self.assertEqual(resolved.status, "family_only")
        self.assertFalse(resolved.substituted)
        self.assertEqual(resolved.resolved_style, "regular")

    def test_missing_family_remains_blocking_without_explicit_choice(self) -> None:
        resolutions = resolve_requirements(
            [{"family": "Missing Family", "style": "regular"}],
            inventory=(),
        )

        self.assertEqual(resolutions[0]["status"], "missing_family")
        self.assertFalse(resolutions[0]["substituted"])
        self.assertEqual(len(unresolved_requirements(resolutions)), 1)

    def test_substitution_requires_explicit_mapping(self) -> None:
        inventory = (
            FontFace("Arimo", "regular", "arimo.ttf", ORIGIN_CORE),
        )

        without_choice = resolve_requirements(
            [{"family": "Arial", "style": "regular"}],
            inventory=inventory,
        )
        self.assertEqual(without_choice[0]["status"], "missing_family")

        with_choice = resolve_requirements(
            [{"family": "Arial", "style": "regular"}],
            inventory=inventory,
            substitutions={
                "Arial": {
                    "family": "Arimo",
                    "style": "regular",
                }
            },
        )

        self.assertEqual(with_choice[0]["status"], "substituted")
        self.assertTrue(with_choice[0]["substituted"])
        self.assertEqual(with_choice[0]["resolved_family"], "Arimo")
        self.assertEqual(with_choice[0]["origin"], ORIGIN_CORE)
        self.assertEqual(unresolved_requirements(with_choice), [])


if __name__ == "__main__":
    unittest.main()