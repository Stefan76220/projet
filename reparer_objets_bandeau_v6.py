from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"

OLD = '            soft = self._blend_hex(color, "#FFFFFF", 0.35)\n'
NEW = '            # CORRECTION_ICÔNES_CANVAS_V6\n            # Éclaircissement local de la couleur, sans dépendre d\'une\n            # méthode utilitaire externe au bandeau.\n            rgb = hex_to_rgb(color)\n            soft_rgb = tuple(\n                int(round(channel + (255 - channel) * 0.35))\n                for channel in rgb\n            )\n            soft = "#{:02X}{:02X}{:02X}".format(*soft_rgb)\n'
MARKER = "CORRECTION_ICÔNES_CANVAS_V6"


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if MARKER in original:
        print("CORRECTION_ICÔNES_CANVAS_DEJA_APPLIQUEE")
        return

    if OLD not in original:
        fail(
            "la ligne fautive du bandeau V6 n'a pas été trouvée. "
            "Le fichier a probablement changé."
        )

    candidate = original.replace(OLD, NEW, 1)

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version corrigée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"document_view_avant_correction_icones_v6_{stamp}.py"
    temp = TARGET.with_suffix(".icones_v6.tmp")

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

    print("CORRECTION_ICÔNES_CANVAS_V6_OK")
    print("Le fond du bandeau est conservé.")
    print("Les icônes et libellés doivent maintenant réapparaître.")
    print("Accueil reste juste avant Centre.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
