from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import re
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "main_window.py"

MARKER = "OUVERTURE_FENETRE_MAXIMISEE_V1"


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if MARKER in original:
        print("OUVERTURE_MAXIMISEE_DEJA_APPLIQUEE")
        return

    # On touche uniquement à la configuration de la fenêtre principale.
    pattern = re.compile(
        r'(?m)^(?P<indent>\s*)self\.root\.geometry\((?P<args>[^\n]+)\)\s*$'
    )
    matches = list(pattern.finditer(original))
    if len(matches) != 1:
        fail(
            "la ligne de taille de la fenêtre principale n'a pas été trouvée "
            "de manière sûre et unique"
        )

    match = matches[0]
    indent = match.group("indent")
    geometry_line = match.group(0)

    replacement = (
        geometry_line
        + "\n"
        + indent
        + f"# {MARKER}\n"
        + indent
        + "# Ouverture maximisée Windows, avec barre de titre et boutons système.\n"
        + indent
        + "try:\n"
        + indent
        + '    self.root.state("zoomed")\n'
        + indent
        + "except Exception:\n"
        + indent
        + "    pass"
    )

    candidate = original[:match.start()] + replacement + original[match.end():]

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"main_window_avant_ouverture_maximisee_{stamp}.py"
    temp = TARGET.with_suffix(".maximisee.tmp")

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

    print("OUVERTURE_MAXIMISEE_OK")
    print("PageMaître s'ouvrira désormais maximisé sur l'écran.")
    print("La barre de titre Windows reste visible.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
