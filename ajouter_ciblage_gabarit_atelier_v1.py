from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "model_workshop_view.py"

MARKER = "def focus_model("
ANCHOR = "    def hide(self) -> None:\n"
INSERT = '\n    @property\n    def active_model_id(self) -> str:\n        """Identifiant du gabarit actuellement affiché dans l\'Atelier."""\n        return str(self._working_model_id or "")\n\n    @property\n    def is_visible(self) -> bool:\n        """Indique si l\'Atelier est actuellement au premier plan."""\n        return bool(self._is_visible)\n\n    def focus_model(self, model_identifier: str) -> bool:\n        """Affiche directement un gabarit du projet dans l\'Atelier.\n\n        Cette entrée publique est destinée au Centre de régulation et à la\n        future fenêtre Visualisation. Si le gabarit demandé est déjà affiché,\n        l\'Atelier est simplement ramené au premier plan sans reconstruction.\n        """\n        identifier = str(model_identifier or "").strip()\n        if not identifier:\n            return False\n\n        self.show()\n\n        if self._working_model_id == identifier:\n            self._focus_current_editor()\n            return True\n\n        self._project_models = self._load_project_models()\n        target = next(\n            (\n                model\n                for model in self._project_models\n                if str(model.identifier) == identifier\n            ),\n            None,\n        )\n        if target is None:\n            return False\n\n        # Un gabarit enregistré est rappelé par le même mécanisme que depuis\n        # la Bibliothèque de l\'Atelier. On ne crée donc aucun second chemin\n        # d\'ouverture ni aucun éditeur parallèle.\n        self._use_model(\n            target,\n            "gabarits",\n            on_ready=self._focus_current_editor,\n        )\n        return True\n'


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if MARKER in original:
        print("CIBLAGE_GABARIT_ATELIER_V1_DEJA_APPLIQUE")
        return

    required = (
        "class ModelWorkshopView:",
        "def _use_model(",
        "_working_model_id",
        "def _load_project_models(",
        "def _focus_current_editor(",
    )
    for token in required:
        if token not in original:
            fail(f"élément Atelier attendu introuvable : {token}")

    if ANCHOR not in original:
        fail("point d'insertion après show() introuvable")

    candidate = original.replace(
        ANCHOR,
        INSERT.rstrip() + "\n\n" + ANCHOR,
        1,
    )

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"model_workshop_view_avant_ciblage_gabarit_{stamp}.py"
    )
    temp = TARGET.with_suffix(".ciblage_gabarit.tmp")

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

    print("CIBLAGE_GABARIT_ATELIER_V1_OK")
    print("ModelWorkshopView expose maintenant focus_model(model_identifier).")
    print("Un gabarit déjà ouvert est simplement ramené au premier plan.")
    print("Un autre gabarit est chargé par le mécanisme existant de la Bibliothèque.")
    print("active_model_id et is_visible sont également disponibles pour le Centre.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
