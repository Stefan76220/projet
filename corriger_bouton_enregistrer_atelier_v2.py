from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "model_workshop_view.py"

REQUIRED = "ASSOCIATION_MAQUETTAGE_GABARIT_V1"
MARKER = "CORRECTION_SIGNATURE_DIALOGUE_GABARIT_V2"

WRONG_SIG = """        categories: list[dict[str, Any]],
        page_types: list[dict[str, Any]],
        default_page_type: str,
        on_create_category: Callable[
"""

NORMAL_SIG = """        categories: list[dict[str, Any]],
        on_create_category: Callable[
"""

ENHANCED_SIG = """        categories: list[dict[str, Any]],
        page_types: list[dict[str, Any]],
        default_page_type: str,
        on_create_category: Callable[
"""


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    source = TARGET.read_text(encoding="utf-8")

    if MARKER in source:
        print("CORRECTION_SIGNATURE_DIALOGUE_GABARIT_V2_DEJA_APPLIQUEE")
        return

    if REQUIRED not in source:
        fail("le correctif d'association précédent n'est pas détecté")

    new_model_start = source.find("class NewModelDialog")
    save_model_start = source.find("class SaveProjectModelDialog")
    library_start = source.find("class ModelLibraryDialog")

    if min(new_model_start, save_model_start, library_start) < 0:
        fail("classes Atelier attendues introuvables")

    if not (new_model_start < save_model_start < library_start):
        fail("ordre des classes Atelier inattendu")

    new_model_block = source[new_model_start:save_model_start]
    save_model_block = source[save_model_start:library_start]

    # 1. NewModelDialog retrouve sa signature normale.
    if WRONG_SIG in new_model_block:
        new_model_block = new_model_block.replace(
            WRONG_SIG,
            NORMAL_SIG,
            1,
        )
    elif NORMAL_SIG not in new_model_block:
        fail("signature de NewModelDialog inattendue")

    # 2. SaveProjectModelDialog reçoit bien les deux paramètres
    #    utilisés par son corps et par l'appel _save_as_project_model().
    if ENHANCED_SIG not in save_model_block:
        if NORMAL_SIG not in save_model_block:
            fail("signature de SaveProjectModelDialog inattendue")
        save_model_block = save_model_block.replace(
            NORMAL_SIG,
            ENHANCED_SIG,
            1,
        )

    marker_line = (
        "    # CORRECTION_SIGNATURE_DIALOGUE_GABARIT_V2\n"
    )
    save_model_block = marker_line + save_model_block

    candidate = (
        source[:new_model_start]
        + new_model_block
        + save_model_block
        + source[library_start:]
    )

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"model_workshop_view_avant_correction_dialogue_{stamp}.py"
    )
    temp = TARGET.with_suffix(".correction_dialogue.tmp")

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

    print("CORRECTION_SIGNATURE_DIALOGUE_GABARIT_V2_OK")
    print("Le bouton Enregistrer peut de nouveau ouvrir son dialogue.")
    print("NewModelDialog retrouve sa signature normale.")
    print("SaveProjectModelDialog reçoit correctement page_types et default_page_type.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
