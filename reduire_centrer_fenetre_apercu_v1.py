from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"

REQUIRED_MARKERS = (
    "APERCU_GRANDE_VUE_V3",
    "APERCU_ROTATION_ALIGNEE_V1",
)
NEW_MARKER = "APERCU_FENETRE_CENTREE_V1"

OLD = '        # APERCU_GRANDE_VUE_V3\n        # Fenêtre resserrée autour du livre : elle reste redimensionnable.\n        window.geometry("900x650")\n        window.minsize(780, 560)\n        window.configure(fg_color=self.WINDOW_BG)\n'
NEW = '        # APERCU_GRANDE_VUE_V3\n        # Fenêtre resserrée autour du livre : elle reste redimensionnable.\n        preview_width = 840\n        preview_height = 650\n        window.minsize(740, 560)\n        window.update_idletasks()\n\n        screen_width = int(window.winfo_screenwidth())\n        screen_height = int(window.winfo_screenheight())\n        pos_x = max(0, (screen_width - preview_width) // 2)\n        pos_y = max(0, (screen_height - preview_height) // 2)\n\n        window.geometry(\n            f"{preview_width}x{preview_height}+{pos_x}+{pos_y}"\n        )\n        window.configure(fg_color=self.WINDOW_BG)\n'


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if NEW_MARKER in original:
        print("APERCU_FENETRE_CENTREE_DEJA_APPLIQUE")
        return

    missing = [marker for marker in REQUIRED_MARKERS if marker not in original]
    if missing:
        fail(
            "la version attendue de la Grande vue n'est pas détectée : "
            + ", ".join(missing)
        )

    if OLD not in original:
        fail(
            "la géométrie actuelle de la fenêtre n'a pas été trouvée. "
            "Aucune modification n'est appliquée."
        )

    candidate = original.replace(OLD, NEW, 1)

    marker_anchor = "        # APERCU_GRANDE_VUE_V3\n"
    if marker_anchor not in candidate:
        fail("marqueur de la Grande vue introuvable")
    candidate = candidate.replace(
        marker_anchor,
        marker_anchor + "        # APERCU_FENETRE_CENTREE_V1\n",
        1,
    )

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"mockup_view_avant_fenetre_apercu_centree_{stamp}.py"
    temporary = TARGET.with_suffix(".apercu_fenetre_centree.tmp")

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

    print("APERCU_FENETRE_CENTREE_OK")
    print("Fichier modifié : src/gui/views/mockup_view.py")
    print(f"Sauvegarde : {backup}")
    print("Largeur initiale : 840 px au lieu de 900 px.")
    print("Hauteur : 650 px conservée.")
    print("Ouverture : centrée automatiquement sur l'écran.")
    print("Animation, fond, outils et pages : inchangés.")
    print("Ferme complètement PageMaître puis relance-le.")


if __name__ == "__main__":
    main()
