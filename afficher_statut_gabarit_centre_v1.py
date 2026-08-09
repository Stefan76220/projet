from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"

REQUIRED = "ROUTEUR_CENTRE_MAQUETTAGE_ATELIER_V1"
MARKER = "STATUT_GABARIT_CENTRE_V1"

OLD = """        def page_status(item: dict) -> tuple[str, str]:
            if bool(item.get("automatic_recto_verso", False)):
                return "AUTO  ✦", item_accent(item)
            return "MAQUETTAGE", item_accent(item)
"""

NEW = """        def page_status(item: dict) -> tuple[str, str]:
            # STATUT_GABARIT_CENTRE_V1
            if bool(item.get("automatic_recto_verso", False)):
                return "AUTO  ✦", item_accent(item)

            model_id = self._associated_model_id_for_synoptic_item(item)
            if model_id:
                return "GABARIT", self.ATELIER

            return "MAQUETTAGE", item_accent(item)
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
        print("STATUT_GABARIT_CENTRE_V1_DEJA_APPLIQUE")
        return

    if REQUIRED not in source:
        fail("le routeur Centre -> Atelier n'est pas détecté")

    if OLD not in source:
        fail("fonction page_status attendue introuvable")

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
        / f"document_view_avant_statut_gabarit_{stamp}.py"
    )
    temp = TARGET.with_suffix(".statut_gabarit.tmp")

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

    print("STATUT_GABARIT_CENTRE_V1_OK")
    print("Sans gabarit associé : MAQUETTAGE.")
    print("Avec gabarit associé : GABARIT en vert Atelier.")
    print("Les pages automatiques restent AUTO.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
