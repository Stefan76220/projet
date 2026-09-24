from __future__ import annotations

import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from tomelinea.rendering.libreoffice_engine import (
    LibreOfficeEngine,
    render_document_to_pdf,
)


class LibreOfficeEngineTests(unittest.TestCase):
    def test_render_preserves_working_document(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "book.docx"
            source.write_bytes(b"source")
            exe = root / "soffice.com"
            exe.write_bytes(b"fake")
            out = root / "out"

            def fake_run(args, **kwargs):
                out.mkdir(parents=True, exist_ok=True)
                (out / "book.pdf").write_bytes(b"%PDF-1.4\n%%EOF\n")
                class Done:
                    returncode = 0
                    stdout = "ok"
                    stderr = ""
                return Done()

            engine = LibreOfficeEngine(exe, "environment")
            with patch(
                "tomelinea.rendering.libreoffice_engine.subprocess.run",
                side_effect=fake_run,
            ):
                result = render_document_to_pdf(source, out, engine=engine)

            self.assertTrue(result.source_unchanged)
            self.assertEqual(source.read_bytes(), b"source")
            self.assertTrue(result.pdf_path.is_file())


if __name__ == "__main__":
    unittest.main()