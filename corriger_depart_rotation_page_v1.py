from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"

REQUIRED_MARKER = "APERCU_GRANDE_VUE_V3"
NEW_MARKER = "APERCU_ROTATION_ALIGNEE_V1"

OLD = '            page_height = min(424, max(320, body_height - 70))\n            page_width = max(\n                1,\n                int(round(page_height * 300 / 424)),\n            )\n            spine_x = body_width // 2\n            top_y = max(10, (body_height - page_height) // 2 - 6)\n'
NEW = "            page_height = min(424, max(320, body_height - 70))\n            page_width = max(\n                1,\n                int(round(page_height * 300 / 424)),\n            )\n            spine_x = body_width // 2\n\n            # APERCU_ROTATION_ALIGNEE_V1\n            # L'animation démarre exactement à la hauteur de la page\n            # réellement affichée, au lieu d'estimer sa position à partir\n            # du centre de la fenêtre.\n            top_y = max(0, (body_height - page_height) // 2)\n            try:\n                body.update_idletasks()\n\n                def descendants(widget):\n                    for child in widget.winfo_children():\n                        yield child\n                        yield from descendants(child)\n\n                page_candidates = []\n                for widget in descendants(body):\n                    try:\n                        width = int(widget.winfo_width())\n                        height = int(widget.winfo_height())\n                        if (\n                            widget.winfo_ismapped()\n                            and abs(width - 300) <= 4\n                            and abs(height - 424) <= 4\n                        ):\n                            page_candidates.append(widget)\n                    except Exception:\n                        pass\n\n                if page_candidates:\n                    top_y = min(\n                        int(widget.winfo_rooty() - body.winfo_rooty())\n                        for widget in page_candidates\n                    )\n                    page_height = int(page_candidates[0].winfo_height())\n                    page_width = int(page_candidates[0].winfo_width())\n            except Exception:\n                pass\n"


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if NEW_MARKER in original:
        print("APERCU_ROTATION_ALIGNEE_DEJA_APPLIQUE")
        return

    if REQUIRED_MARKER not in original:
        fail(
            "la Grande vue V3 n'est pas détectée. "
            "Par sécurité, aucune modification n'est appliquée."
        )

    if OLD not in original:
        fail(
            "le calcul actuel de position de l'animation n'a pas été trouvé. "
            "Aucune modification n'est appliquée."
        )

    candidate = original.replace(OLD, NEW, 1)

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"mockup_view_avant_rotation_alignee_{stamp}.py"
    temporary = TARGET.with_suffix(".rotation_alignee.tmp")

    try:
        temporary.write_text(candidate, encoding="utf-8")
        py_compile.compile(str(temporary), doraise=True)
        shutil.copy2(TARGET, backup)
        temporary.replace(TARGET)
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as exc:
        try:
            temporary.unlink(missing_ok=True)
        except Exception:
            pass
        if backup.exists():
            shutil.copy2(backup, TARGET)
        fail(f"installation annulée automatiquement : {exc}")

    print("APERCU_ROTATION_ALIGNEE_OK")
    print("Fichier modifié : src/gui/views/mockup_view.py")
    print(f"Sauvegarde : {backup}")
    print("Animation : départ recalé sur la position verticale réelle des pages.")
    print("Effet de rotation V3 : conservé.")
    print("Fenêtre, fond, outils et mise en page : inchangés.")
    print("Ferme complètement PageMaître puis relance-le.")


if __name__ == "__main__":
    main()
