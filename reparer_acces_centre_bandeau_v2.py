from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"
BROKEN = "        decor.lower()\n"
MARKER = "CORRECTION_CANVAS_LOWER_V2"


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if MARKER in original:
        print("CORRECTION_CANVAS_LOWER_DEJA_APPLIQUEE")
        return

    if BROKEN not in original:
        fail("la ligne fautive decor.lower() n'a pas été trouvée")

    candidate = original.replace(
        BROKEN,
        "        # CORRECTION_CANVAS_LOWER_V2\n"
        "        # Le Canvas a été créé avant les contrôles : il reste naturellement\n"
        "        # en arrière-plan. Canvas.lower() attend un identifiant d'item Tk\n"
        "        # et ne doit pas être utilisé pour abaisser le widget lui-même.\n",
        1,
    )

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version corrigée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"document_view_avant_correction_canvas_{stamp}.py"
    temp = TARGET.with_suffix(".canvas_fix.tmp")

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

    print("CORRECTION_CANVAS_LOWER_OK")
    print("Le blocage du Centre est corrigé.")
    print("Le bandeau décoratif V2 est conservé.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
