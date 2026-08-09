from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"

REQUIRED = "CODE_TYPE_PAGE_V8"
MARKER = "CODE_TYPE_PAGE_LISIBLE_V9"

OLD_BAND = """            band_h = 6 * scale
"""
NEW_BAND = """            # CODE_TYPE_PAGE_LISIBLE_V9
            # Bandeau légèrement plus haut pour une lecture immédiate
            # sans alourdir la miniature.
            band_h = 9 * scale
"""

OLD_FONT = """                font=(
                    Fonts.FAMILY,
                    max(5, int(5.5 * scale)),
                    "bold",
                ),
"""
NEW_FONT = """                font=(
                    Fonts.FAMILY,
                    max(7, int(7.5 * scale)),
                    "bold",
                ),
"""

OLD_X = """                x + 4 * scale,
"""
NEW_X = """                x + 5 * scale,
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
        print("CODE_TYPE_PAGE_LISIBLE_V9_DEJA_APPLIQUE")
        return

    if REQUIRED not in original:
        fail("la version Code type V8 n'est pas détectée")

    candidate = original

    if OLD_BAND not in candidate:
        fail("hauteur du bandeau V8 introuvable")
    candidate = candidate.replace(OLD_BAND, NEW_BAND, 1)

    if OLD_FONT not in candidate:
        fail("taille de police du code V8 introuvable")
    candidate = candidate.replace(OLD_FONT, NEW_FONT, 1)

    # Ne remplace que le premier x du code type après le marqueur V8.
    marker_pos = candidate.find("text=type_code_for_item(item)")
    if marker_pos == -1:
        fail("texte du code type introuvable")

    start = candidate.rfind("            wall.create_text(", 0, marker_pos)
    end = candidate.find("            )", marker_pos)
    if start == -1 or end == -1:
        fail("bloc du code type introuvable")

    block = candidate[start:end + len("            )")]
    if OLD_X in block:
        block_new = block.replace(OLD_X, NEW_X, 1)
        candidate = candidate[:start] + block_new + candidate[end + len("            )"):]
    else:
        fail("position horizontale du code introuvable")

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"document_view_avant_code_type_v9_{stamp}.py"
    temp = TARGET.with_suffix(".code_type_v9.tmp")

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

    print("CODE_TYPE_PAGE_LISIBLE_V9_OK")
    print("Le bandeau passe de 6 à 9 px environ.")
    print("Le code type est nettement plus grand et plus lisible.")
    print("La disposition générale du synoptique reste inchangée.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
