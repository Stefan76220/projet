from __future__ import annotations

from datetime import datetime
from pathlib import Path
import re
import shutil

TARGET = Path("src/gui/views/document_view.py")


def main() -> None:
    if not TARGET.is_file():
        raise SystemExit(
            "ERREUR : lance ce script depuis C:\\Users\\PC\\projet"
        )

    original = TARGET.read_text(encoding="utf-8")

    marker = "    def _create_recent_pages("
    start = original.find(marker)
    if start < 0:
        raise SystemExit(
            "ERREUR : fonction _create_recent_pages introuvable. Aucun fichier modifié."
        )

    match = re.search(
        r"^    def [A-Za-z_][A-Za-z0-9_]*\(",
        original[start + len(marker):],
        re.M,
    )
    end = (
        len(original)
        if match is None
        else start + len(marker) + match.start()
    )

    block = original[start:end]

    dynamic = (
        '                text=(\n'
        '                    "Aucune planche"\n'
        '                    if self._project_type_key() == "bande_dessinee"\n'
        '                    else "Aucune page"\n'
        '                ),\n'
    )

    if '"Aucune planche"' in block and 'self._project_type_key()' in block:
        print("LIBELLE_BD_RECENTES_DEJA_CORRECT")
        return

    old = '                text="Aucune page",\n'
    if old not in block:
        raise SystemExit(
            "ERREUR : libellé 'Aucune page' introuvable dans Récentes. "
            "Aucun fichier modifié."
        )

    new_block = block.replace(old, dynamic, 1)
    updated = original[:start] + new_block + original[end:]

    compile(updated, str(TARGET), "exec")

    backup_dir = Path("cache") / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"document_view_avant_libelle_bd_{stamp}.py"
    shutil.copy2(TARGET, backup)

    TARGET.write_text(updated, encoding="utf-8")

    pycache = TARGET.parent / "__pycache__"
    if pycache.exists():
        shutil.rmtree(pycache, ignore_errors=True)

    print("LIBELLE_BD_RECENTES_OK")
    print("Fichier modifié : src/gui/views/document_view.py")
    print(f"Sauvegarde : {backup}")
    print("Ferme complètement PageMaître puis relance-le.")


if __name__ == "__main__":
    main()
