from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "model_workshop_view.py"

MARKER = "AFFICHAGE_IMMEDIAT_ATELIER_V1"
REQUIRED = "OUVERTURE_GABARIT_UN_CLIC_V1"


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def patch(source: str) -> str:
    if MARKER in source:
        return source

    if REQUIRED not in source:
        fail("la correction d'ouverture en un clic n'est pas détectée")

    old = (
        "        if self._working_model_id == identifier:\n"
        "            self._focus_current_editor()\n"
        "            # APERCU_REEL_GABARIT_ATELIER_V2\n"
        "            self.parent.after(\n"
        "                120,\n"
        "                self._save_active_model_centre_preview,\n"
        "            )\n"
        "            return True\n"
        "\n"
        "        self._project_models = self._load_project_models()\n"
    )

    new = (
        "        if self._working_model_id == identifier:\n"
        "            self._focus_current_editor()\n"
        "            # APERCU_REEL_GABARIT_ATELIER_V2\n"
        "            self.parent.after(\n"
        "                120,\n"
        "                self._save_active_model_centre_preview,\n"
        "            )\n"
        "            return True\n"
        "\n"
        "        # AFFICHAGE_IMMEDIAT_ATELIER_V1\n"
        "        # Force l'affichage de l'Atelier avant le travail plus lourd\n"
        "        # de reconstruction du gabarit demandé.\n"
        "        root = self._root_frame\n"
        "        if root is not None:\n"
        "            try:\n"
        "                if root.winfo_exists():\n"
        "                    root.lift()\n"
        "                    self._is_visible = True\n"
        "                    self._status_var.set(\"Ouverture du gabarit…\")\n"
        "                    self.parent.update_idletasks()\n"
        "            except tk.TclError:\n"
        "                self._root_frame = None\n"
        "\n"
        "        self._project_models = self._load_project_models()\n"
    )

    if old not in source:
        fail("zone de focus_model attendue introuvable")

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
        print("AFFICHAGE_IMMEDIAT_ATELIER_V1_DEJA_APPLIQUE")
        return

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"model_workshop_view_avant_affichage_immediat_{stamp}.py"
    )
    temp = TARGET.with_suffix(".affichage_immediat.tmp")

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

    print("AFFICHAGE_IMMEDIAT_ATELIER_V1_OK")
    print("L'Atelier est maintenant affiché avant le chargement du gabarit.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
