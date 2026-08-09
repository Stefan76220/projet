from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"

REQUIRED = "VOYANT_PAGE_OUVERTE_ATELIER_V1"
MARKER = "VOYANT_ATELIER_COTE_EXTERIEUR_V2"

OLD = """                activity_tag = f"{tag}_atelier_active"
                tab_x1 = x + page_w - 1
                tab_y1 = y + 31 * scale
                tab_x2 = x + page_w + 13 * scale
                tab_y2 = y + 56 * scale
"""

NEW = """                activity_tag = f"{tag}_atelier_active"
                # VOYANT_ATELIER_COTE_EXTERIEUR_V2
                # Le voyant reste toujours à l'extérieur du livre ouvert :
                # gauche pour une page gauche, droite pour une page droite.
                if page_side == "left":
                    tab_x1 = x - 13 * scale
                    tab_x2 = x + 1 * scale
                else:
                    tab_x1 = x + page_w - 1 * scale
                    tab_x2 = x + page_w + 13 * scale

                tab_y1 = y + 31 * scale
                tab_y2 = y + 56 * scale
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
        print("VOYANT_ATELIER_COTE_EXTERIEUR_V2_DEJA_APPLIQUE")
        return

    if REQUIRED not in source:
        fail("le voyant Atelier V1 n'est pas détecté")

    if OLD not in source:
        fail("bloc de positionnement du voyant Atelier introuvable")

    candidate = source.replace(OLD, NEW, 1)

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"document_view_avant_voyant_exterieur_{stamp}.py"
    )
    temp = TARGET.with_suffix(".voyant_exterieur.tmp")

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

    print("VOYANT_ATELIER_COTE_EXTERIEUR_V2_OK")
    print("Page gauche : voyant A sur le bord extérieur gauche.")
    print("Page droite : voyant A sur le bord extérieur droit.")
    print("Le centre de la double page reste désormais dégagé.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
