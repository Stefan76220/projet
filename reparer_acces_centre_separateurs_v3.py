from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"
MARKER = "CORRECTION_SEPARATEURS_PLACE_V3"

OLD_1 = '        ctk.CTkFrame(\n            ribbon,\n            width=1,\n            fg_color="#D9E0E5",\n            corner_radius=0,\n        ).place(relx=0, x=226, y=13, height=48)\n'
NEW_1 = '        ctk.CTkFrame(\n            ribbon,\n            width=1,\n            height=48,\n            fg_color="#D9E0E5",\n            corner_radius=0,\n        ).place(relx=0, x=226, y=13)\n'
OLD_2 = '        ctk.CTkFrame(\n            ribbon,\n            width=1,\n            fg_color="#D9E0E5",\n            corner_radius=0,\n        ).place(relx=1, x=-94, y=13, height=48)\n'
NEW_2 = '        ctk.CTkFrame(\n            ribbon,\n            width=1,\n            height=48,\n            fg_color="#D9E0E5",\n            corner_radius=0,\n        ).place(relx=1, x=-94, y=13)\n'


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if MARKER in original:
        print("CORRECTION_SEPARATEURS_DEJA_APPLIQUEE")
        return

    if OLD_1 not in original or OLD_2 not in original:
        fail("les deux séparateurs fautifs n'ont pas été trouvés exactement")

    candidate = original.replace(OLD_1, NEW_1, 1)
    candidate = candidate.replace(OLD_2, NEW_2, 1)

    marker_anchor = "        # Fines séparations uniquement structurelles.\n"
    if marker_anchor in candidate:
        candidate = candidate.replace(
            marker_anchor,
            marker_anchor + "        # " + MARKER + "\n",
            1,
        )

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version corrigée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"document_view_avant_correction_separateurs_{stamp}.py"
    temp = TARGET.with_suffix(".separateurs_fix.tmp")

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

    print("CORRECTION_SEPARATEURS_PLACE_OK")
    print("Les dimensions des séparateurs sont maintenant données au constructeur.")
    print("Le bandeau décoratif V2 est conservé.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
