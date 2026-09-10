from __future__ import annotations

"""Lanceur temporaire de contrôle de la Phase 1 DOCX."""

from pathlib import Path
import sys
import webbrowser

from src.v4.docx_phase1 import analyze_docx_phase1
from src.v4.source_phase1_report import write_phase1_report


def choose_docx() -> str:
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        value = filedialog.askopenfilename(
            title="TomeLinea — choisir le DOCX à contrôler",
            filetypes=(("Document Word", "*.docx"),),
        )
        root.destroy()
        return value
    except Exception:
        return ""


def main() -> int:
    filename = sys.argv[1] if len(sys.argv) > 1 else choose_docx()
    if not filename:
        print("Aucun DOCX sélectionné.")
        return 1

    source = Path(filename).expanduser().resolve()
    result = analyze_docx_phase1(source)
    output_dir = Path.home() / "Downloads" / "TomeLinea_Phase1_Rapports"
    paths = write_phase1_report(result.model, output_dir)

    print("\nPHASE 1 TERMINEE")
    print("----------------")
    print(f"Source      : {source}")
    print(f"Paragraphes : {result.paragraph_count}")
    print(f"Sections    : {result.section_count}")
    print(f"Rapport     : {paths['html']}")
    print(f"Modele JSON : {paths['json']}")
    print(f"Resume      : {paths['text']}")
    print("\nAucun Canvas et aucune regle editoriale n'ont ete executes.")

    try:
        webbrowser.open(Path(paths["html"]).as_uri())
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
