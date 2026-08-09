from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"

OLD_NAV = '        _, navigation_controls = preview_group(\n            "Navigation",\n            140,\n            self.SKY,\n        )\n'
NEW_NAV = '        _, navigation_controls = preview_group(\n            "Navigation",\n            150,\n            self.SKY,\n        )\n'

OLD_WINDOW = '        _, window_controls = preview_group(\n            "Fenêtre",\n            72,\n            self.CORAL,\n        )\n'
NEW_WINDOW = '        _, window_controls = preview_group(\n            "Fenêtre",\n            80,\n            self.CORAL,\n        )\n'

MARKER = "APERCU_MAQUETTAGE_GRANDE_VUE_SEULE_V1"
NEW_MARKER = "APERCU_OUTILS_RESPIRATION_V1"


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if NEW_MARKER in original:
        print("APERCU_OUTILS_RESPIRATION_DEJA_APPLIQUE")
        return

    if MARKER not in original:
        fail(
            "la version attendue du Maquettage n'est pas détectée. "
            "Le correctif précédent doit être présent."
        )

    if 'text="Ensemble"' in original or '"overview"' in original:
        fail("Vue Ensemble est encore présente : correctif cosmétique annulé.")

    if original.count(OLD_NAV) != 1:
        fail("bloc Navigation attendu introuvable ou ambigu")

    if original.count(OLD_WINDOW) != 1:
        fail("bloc Fenêtre attendu introuvable ou ambigu")

    candidate = original.replace(OLD_NAV, NEW_NAV, 1)
    candidate = candidate.replace(OLD_WINDOW, NEW_WINDOW, 1)

    marker_line = f"        # {MARKER}\n"
    if marker_line in candidate:
        candidate = candidate.replace(
            marker_line,
            marker_line + f"        # {NEW_MARKER}\n",
            1,
        )
    else:
        fail("emplacement du marqueur introuvable")

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"mockup_view_avant_cosmetique_apercu_{stamp}.py"
    temporary = TARGET.with_suffix(".cosmetique_apercu.tmp")

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

    print("APERCU_OUTILS_RESPIRATION_OK")
    print("Navigation : zone élargie de 140 à 150.")
    print("Fenêtre : zone élargie de 72 à 80.")
    print("Grande vue, animation et pagination : inchangées.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
