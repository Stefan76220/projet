from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"

REQUIRED_CENTRE = "CIBLAGE_CENTRE_MAQUETTAGE_V1"
MARKER = "ROUTEUR_CENTRE_MAQUETTAGE_ATELIER_V1"

OLD_CLICK = """            wall.tag_bind(
                tag,
                "<Button-1>",
                lambda _evt, current_item=item: self._open_mockup_page(
                    current_item
                ),
            )
"""

NEW_CLICK = """            wall.tag_bind(
                tag,
                "<Button-1>",
                lambda _evt, current_item=item: self._route_synoptic_page(
                    current_item
                ),
            )
"""

ANCHOR = """    def _open_mockup_page(self, item: dict) -> None:
"""

ROUTER = """    def _associated_model_id_for_synoptic_item(
        self,
        item: dict,
    ) -> str:
        # ROUTEUR_CENTRE_MAQUETTAGE_ATELIER_V1
        page_type = str(item.get("type", "")).strip()
        if not page_type:
            return ""

        path = (
            Path(self.project.models_folder)
            / "maquettage_associations.json"
        )
        if not path.is_file():
            return ""

        try:
            with path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (OSError, json.JSONDecodeError):
            return ""

        associations = (
            data.get("associations", {})
            if isinstance(data, dict)
            else {}
        )
        if not isinstance(associations, dict):
            return ""

        return str(associations.get(page_type, "")).strip()

    def _route_synoptic_page(self, item: dict) -> None:
        \"\"\"Ouvre la page dans l'espace correspondant à son état réel.\"\"\"
        model_id = self._associated_model_id_for_synoptic_item(item)

        if model_id:
            self._hide_project_tools_for_subspace()

            if self._model_workshop_view is None:
                self._model_workshop_view = ModelWorkshopView(
                    parent=self.parent,
                    project=self.project,
                    on_back=self._close_model_workshop,
                )

            if self._model_workshop_view.focus_model(model_id):
                return

            # Association devenue invalide : on revient sans bloquer
            # au comportement de base du Maquettage.
            try:
                self._model_workshop_view.hide()
            except Exception:
                pass

        self._open_mockup_page(item)

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
        print("ROUTEUR_CENTRE_MAQUETTAGE_ATELIER_V1_DEJA_APPLIQUE")
        return

    if REQUIRED_CENTRE not in source:
        fail("le ciblage Centre -> Maquettage précédent n'est pas détecté")

    if "import json" not in source:
        fail("import json attendu introuvable")

    if "ModelWorkshopView" not in source:
        fail("ModelWorkshopView attendu introuvable")

    if OLD_CLICK not in source:
        fail("liaison de clic du synoptique introuvable")

    candidate = source.replace(
        OLD_CLICK,
        NEW_CLICK,
        1,
    )

    if ANCHOR not in candidate:
        fail("méthode _open_mockup_page introuvable")

    candidate = candidate.replace(
        ANCHOR,
        ROUTER + ANCHOR,
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
        / f"document_view_avant_routeur_atelier_{stamp}.py"
    )
    temp = TARGET.with_suffix(".routeur_atelier.tmp")

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

    print("ROUTEUR_CENTRE_MAQUETTAGE_ATELIER_V1_OK")
    print("Sans gabarit associé : clic -> Maquettage sur la page.")
    print("Avec gabarit associé : clic -> Atelier sur ce gabarit.")
    print("Une association invalide retombe automatiquement sur Maquettage.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
