from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil
import re

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"

REQUIRED = "ROUTEUR_CENTRE_MAQUETTAGE_ATELIER_V1"
MARKER = "STATUT_GABARIT_CENTRE_V2"

PATTERN = re.compile(
    r"(?ms)^        def page_status\(item: dict\) -> tuple\[str, str\]:\n"
    r".*?"
    r"(?=^        def make_background\()"
)

NEW = """        def page_status(item: dict) -> tuple[str, str]:
            # STATUT_GABARIT_CENTRE_V2
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
        print("STATUT_GABARIT_CENTRE_V2_DEJA_APPLIQUE")
        return

    if REQUIRED not in source:
        fail("le routeur Centre -> Atelier n'est pas détecté")

    match = PATTERN.search(source)
    if match is None:
        fail("fonction page_status impossible à localiser")

    candidate = (
        source[:match.start()]
        + NEW
        + source[match.end():]
    )

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"document_view_avant_statut_gabarit_v2_{stamp}.py"
    temp = TARGET.with_suffix(".statut_gabarit_v2.tmp")

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

    print("STATUT_GABARIT_CENTRE_V2_OK")
    print("Sans gabarit : MAQUETTAGE")
    print("Avec gabarit : GABARIT")
    print("Page automatique : AUTO")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
