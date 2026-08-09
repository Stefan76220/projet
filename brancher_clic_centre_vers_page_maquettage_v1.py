from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
DOCUMENT_VIEW = PROJECT / "src" / "gui" / "views" / "document_view.py"
MOCKUP_VIEW = PROJECT / "src" / "gui" / "views" / "mockup_view.py"

REQUIRED_DOCUMENT = "BULLE_TYPE_PAGE_V10"
REQUIRED_MOCKUP = "def focus_page("
MARKER = "CIBLAGE_CENTRE_MAQUETTAGE_V1"

OLD_CLICK = """            wall.tag_bind(
                tag,
                "<Button-1>",
                lambda _evt: self._open_mockup(),
            )
"""

NEW_CLICK = """            # CIBLAGE_CENTRE_MAQUETTAGE_V1
            wall.tag_bind(
                tag,
                "<Button-1>",
                lambda _evt, current_item=item: self._open_mockup_page(
                    current_item
                ),
            )
"""

OPEN_MODEL_ANCHOR = "    def _open_model_workshop(self) -> None:\n"
NEW_METHOD = '    def _open_mockup_page(self, item: dict) -> None:\n        """Ouvre le Maquettage directement sur la page issue du synoptique."""\n        item_id = str(item.get("id", "")).strip()\n\n        try:\n            occurrence = max(\n                1,\n                int(item.get("_occurrence", 1) or 1),\n            )\n        except (TypeError, ValueError):\n            occurrence = 1\n\n        self._hide_project_tools_for_subspace()\n\n        view = MockupView(\n            parent=self.parent,\n            project=self.project,\n            on_back=self._return_to_project_centre,\n        )\n        view.show()\n\n        if not item_id:\n            return\n\n        # Le ciblage est confié au Maquettage lui-même. Cela conserve une\n        # seule logique de sélection et prépare le futur routeur Centre :\n        # Maquettage -> Atelier -> Conception selon l\'état réel de la page.\n        view.focus_page(\n            item_id,\n            occurrence=occurrence,\n        )\n\n'


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def main() -> None:
    if not DOCUMENT_VIEW.is_file():
        fail(f"fichier introuvable : {DOCUMENT_VIEW}")
    if not MOCKUP_VIEW.is_file():
        fail(f"fichier introuvable : {MOCKUP_VIEW}")

    document_source = DOCUMENT_VIEW.read_text(encoding="utf-8")
    mockup_source = MOCKUP_VIEW.read_text(encoding="utf-8")

    if MARKER in document_source:
        print("CIBLAGE_CENTRE_MAQUETTAGE_V1_DEJA_APPLIQUE")
        return

    if REQUIRED_DOCUMENT not in document_source:
        fail("la version Centre V10 n'est pas détectée")

    if REQUIRED_MOCKUP not in mockup_source:
        fail(
            "la commande focus_page() du Maquettage n'est pas détectée ; "
            "applique d'abord ajouter_ciblage_page_maquettage_v1.py"
        )

    if OLD_CLICK not in document_source:
        fail("liaison de clic actuelle du synoptique introuvable")

    candidate = document_source.replace(
        OLD_CLICK,
        NEW_CLICK,
        1,
    )

    if OPEN_MODEL_ANCHOR not in candidate:
        fail("point d'insertion près de _open_mockup introuvable")

    candidate = candidate.replace(
        OPEN_MODEL_ANCHOR,
        NEW_METHOD + OPEN_MODEL_ANCHOR,
        1,
    )

    try:
        compile(candidate, str(DOCUMENT_VIEW), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"document_view_avant_ciblage_centre_{stamp}.py"
    )
    temp = DOCUMENT_VIEW.with_suffix(".ciblage_centre.tmp")

    try:
        temp.write_text(candidate, encoding="utf-8")
        py_compile.compile(str(temp), doraise=True)

        shutil.copy2(DOCUMENT_VIEW, backup)
        temp.replace(DOCUMENT_VIEW)

        py_compile.compile(str(DOCUMENT_VIEW), doraise=True)

    except Exception as exc:
        try:
            temp.unlink(missing_ok=True)
        except Exception:
            pass

        if backup.exists():
            shutil.copy2(backup, DOCUMENT_VIEW)

        fail(f"installation annulée automatiquement : {exc}")

    print("CIBLAGE_CENTRE_MAQUETTAGE_V1_OK")
    print("Un clic sur une page du synoptique ouvre maintenant le Maquettage.")
    print("La carte correspondant à cette page est sélectionnée et centrée.")
    print("Le clic du ruban Maquettage reste inchangé : il ouvre le bureau normalement.")
    print("Ce branchement servira ensuite de base au routeur Atelier/Conception.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
