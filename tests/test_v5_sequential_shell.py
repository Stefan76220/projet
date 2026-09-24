from __future__ import annotations

from pathlib import Path
import unittest


class SequentialShellContractTests(unittest.TestCase):
    def test_main_v5_uses_sequential_shell(self) -> None:
        text = Path("main_v5.py").read_text(encoding="utf-8")
        self.assertIn("TomeLineaV5SequentialShell", text)
        self.assertNotIn("TomeLineaV5RomanStage", text)

    def test_old_survol_shell_is_not_deleted(self) -> None:
        self.assertTrue(Path("src/gui_v5/roman_shell.py").is_file())

    def test_sequential_shell_contains_no_survol_start(self) -> None:
        text = Path("src/gui_v5/sequential_shell.py").read_text(encoding="utf-8")
        self.assertNotIn("_survol_start(", text)
        self.assertIn("Non classées", text)
        self.assertIn("render_document_to_pdf", text)


if __name__ == "__main__":
    unittest.main()