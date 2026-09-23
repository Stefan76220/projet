from __future__ import annotations

"""Banc console V5-28A pour un vrai DOCX utilisateur."""

import argparse
from pathlib import Path

from .api import build_tldocument_from_docx


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Contrôle Source DOCX -> Phase1 -> TLDocument."
    )
    parser.add_argument("source", help="Chemin du DOCX à analyser.")
    args = parser.parse_args()

    source = Path(args.source).expanduser().resolve()
    _document, report = build_tldocument_from_docx(source)
    print(report.to_text())
    return 0 if report.ready_for_visual_twin else 2


if __name__ == "__main__":
    raise SystemExit(main())
