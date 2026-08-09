from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"

REQUIRED = "PAGE_RESPIRATION_AUTO_V3"
MARKER = "PAGE_RESPIRATION_AUTO_V4"

OLD = """            visual_ratio = 0.94 if automatic else 1.0
"""
NEW = """            # PAGE_RESPIRATION_AUTO_V4
            # Différence un peu plus visible : 10 % plus petite.
            visual_ratio = 0.90 if automatic else 1.0
"""


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if MARKER in original:
        print("PAGE_RESPIRATION_AUTO_V4_DEJA_APPLIQUEE")
        return

    if REQUIRED not in original:
        fail("la version V3 n'est pas détectée")

    if OLD not in original:
        fail(
            "le réglage 0.94 attendu n'a pas été trouvé ; "
            "le fichier a probablement changé"
        )

    candidate = original.replace(OLD, NEW, 1)

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"document_view_avant_respiration_v4_{stamp}.py"
    )
    temp = TARGET.with_suffix(".respiration_v4.tmp")

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

    print("PAGE_RESPIRATION_AUTO_V4_OK")
    print("La page automatique est maintenant représentée 10 % plus petite.")
    print("Le reste du synoptique est inchangé.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
