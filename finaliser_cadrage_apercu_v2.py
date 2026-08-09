from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"

REQUIRED_MARKER = "APERCU_MAQUETTAGE_GRANDE_VUE_SEULE_V1"
NEW_MARKER = "APERCU_CADRAGE_VERTICAL_CENTRE_V1"

OLD_NAV = '        _, navigation_controls = preview_group(\n            "Navigation",\n            140,\n            self.SKY,\n        )\n'
NEW_NAV = '        _, navigation_controls = preview_group(\n            "Navigation",\n            150,\n            self.SKY,\n        )\n'

OLD_WINDOW = '        _, window_controls = preview_group(\n            "Fenêtre",\n            72,\n            self.CORAL,\n        )\n'
NEW_WINDOW = '        _, window_controls = preview_group(\n            "Fenêtre",\n            80,\n            self.CORAL,\n        )\n'

OLD_SPREAD = "        spread.grid(row=0, column=0)\n"
NEW_SPREAD = '        # Le bloc page(s) + légende reste réellement centré sur la hauteur\n        # disponible, y compris lorsque la fenêtre est redimensionnée.\n        spread.place(relx=0.5, rely=0.5, anchor="center")\n'


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if NEW_MARKER in original:
        print("APERCU_CADRAGE_VERTICAL_DEJA_APPLIQUE")
        return

    if REQUIRED_MARKER not in original:
        fail(
            "la version attendue du Maquettage n'est pas détectée. "
            "Applique d'abord la suppression de Vue Ensemble."
        )

    if 'text="Ensemble"' in original or '"overview"' in original:
        fail("Vue Ensemble est encore présente : aucune modification appliquée.")

    candidate = original

    # Intègre aussi la petite correction de largeur si le script précédent
    # n'a pas encore été exécuté.
    if OLD_NAV in candidate:
        candidate = candidate.replace(OLD_NAV, NEW_NAV, 1)

    if OLD_WINDOW in candidate:
        candidate = candidate.replace(OLD_WINDOW, NEW_WINDOW, 1)

    if '            "Navigation",\n            150,\n' not in candidate:
        fail("largeur Navigation inattendue")
    if '            "Fenêtre",\n            80,\n' not in candidate:
        fail("largeur Fenêtre inattendue")

    if candidate.count(OLD_SPREAD) != 1:
        fail("emplacement du bloc de pages introuvable ou ambigu")

    candidate = candidate.replace(OLD_SPREAD, NEW_SPREAD, 1)

    marker_line = f"        # {REQUIRED_MARKER}\n"
    if marker_line not in candidate:
        fail("emplacement du marqueur principal introuvable")
    candidate = candidate.replace(
        marker_line,
        marker_line + f"        # {NEW_MARKER}\n",
        1,
    )

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"mockup_view_avant_cadrage_vertical_apercu_{stamp}.py"
    temporary = TARGET.with_suffix(".cadrage_vertical.tmp")

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

    print("APERCU_CADRAGE_VERTICAL_OK")
    print("Pages : centrées précisément sur la hauteur disponible.")
    print("Navigation : largeur 150.")
    print("Fenêtre : largeur 80.")
    print("Grande vue, animation et pagination : inchangées.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
