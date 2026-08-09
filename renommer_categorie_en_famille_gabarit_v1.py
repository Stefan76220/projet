from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "model_workshop_view.py"

MARKER = "LIBELLE_FAMILLE_GABARIT_V1"

REPLACEMENTS = (
    (
        'self._label(form, "Catégorie facultative", row=2)',
        'self._label(form, "Famille de gabarit (facultatif)", row=2)',
    ),
    (
        'text="＋ Catégorie",',
        'text="＋ Famille",',
    ),
)


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    source = TARGET.read_text(encoding="utf-8")

    if MARKER in source:
        print("LIBELLE_FAMILLE_GABARIT_V1_DEJA_APPLIQUE")
        return

    save_start = source.find("class SaveProjectModelDialog")
    library_start = source.find("class ModelLibraryDialog")

    if save_start < 0 or library_start < 0 or save_start >= library_start:
        fail("zone SaveProjectModelDialog introuvable")

    before = source[:save_start]
    block = source[save_start:library_start]
    after = source[library_start:]

    for old, new in REPLACEMENTS:
        if old not in block:
            fail(f"libellé attendu introuvable : {old}")
        block = block.replace(old, new, 1)

    block = (
        "    # LIBELLE_FAMILLE_GABARIT_V1\n"
        + block
    )

    candidate = before + block + after

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"model_workshop_view_avant_libelle_famille_{stamp}.py"
    )
    temp = TARGET.with_suffix(".famille_gabarit.tmp")

    try:
        temp.write_text(candidate, encoding="utf-8")
        py_compile.compile(str(temp), doraise=True)

        shutil.copy2(TARGET, backup)
        temp.replace(TARGET)

        py_compile.compile(str(TARGET), doraise=True)

    except Exception as exc:
        try:
            temp.unlink(missing_ok=True)
        except Exception:
            pass

        if backup.exists():
            shutil.copy2(backup, TARGET)

        fail(f"installation annulée automatiquement : {exc}")

    print("LIBELLE_FAMILLE_GABARIT_V1_OK")
    print("Catégorie facultative -> Famille de gabarit (facultatif)")
    print("+ Catégorie -> + Famille")
    print("Aucune donnée interne ni logique n'a été modifiée.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
