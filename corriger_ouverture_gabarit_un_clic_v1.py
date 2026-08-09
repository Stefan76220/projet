from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "model_workshop_view.py"

MARKER = "OUVERTURE_GABARIT_UN_CLIC_V1"
REQUIRED = "APERCU_REEL_GABARIT_ATELIER_V2"


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def patch(source: str) -> str:
    if MARKER in source:
        return source

    if REQUIRED not in source:
        fail("la version attendue de focus_model n'est pas détectée")

    old = (
        "        def ready_with_preview() -> None:\n"
        "            self._focus_current_editor()\n"
        "            self.parent.after(\n"
        "                120,\n"
        "                lambda current_model=target: self._save_model_centre_preview(\n"
        "                    current_model\n"
        "                ),\n"
        "            )\n"
    )

    new = (
        "        def ready_with_preview() -> None:\n"
        "            # OUVERTURE_GABARIT_UN_CLIC_V1\n"
        "            # Le premier focus_model() construit parfois l'Atelier\n"
        "            # derrière le Centre. Le chargement du gabarit remplaçait\n"
        "            # alors le callback chargé de révéler l'Atelier.\n"
        "            root = self._root_frame\n"
        "            if root is not None:\n"
        "                try:\n"
        "                    if root.winfo_exists():\n"
        "                        self._reveal_workshop(root, ())\n"
        "                except tk.TclError:\n"
        "                    self._root_frame = None\n"
        "\n"
        "            self._focus_current_editor()\n"
        "            self.parent.after(\n"
        "                120,\n"
        "                lambda current_model=target: self._save_model_centre_preview(\n"
        "                    current_model\n"
        "                ),\n"
        "            )\n"
    )

    if old not in source:
        fail("callback de chargement du gabarit introuvable")

    return source.replace(old, new, 1)


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    source = TARGET.read_text(encoding="utf-8")
    candidate = patch(source)

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    if candidate == source:
        print("OUVERTURE_GABARIT_UN_CLIC_V1_DEJA_APPLIQUE")
        return

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"model_workshop_view_avant_ouverture_un_clic_{stamp}.py"
    )
    temp = TARGET.with_suffix(".ouverture_un_clic.tmp")

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

    print("OUVERTURE_GABARIT_UN_CLIC_V1_OK")
    print("Un gabarit ouvert depuis le Centre doit maintenant apparaître au premier clic.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
