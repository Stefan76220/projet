from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"
PAGE_FILE = PROJECT / "src" / "core" / "page.py"

MARKER = "ROUTEUR_CENTRE_VERS_CONCEPTION_V1"
REQUIRED_PAGE_MARKER = "LIEN_STABLE_MAQUETTAGE_CONCEPTION_V1"


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def patch(source: str) -> str:
    if MARKER in source:
        return source

    route_old = (
        '    def _route_synoptic_page(self, item: dict) -> None:\n'
        '        """Ouvre la page dans l\'espace correspondant à son état réel."""\n'
        '        model_id = self._associated_model_id_for_synoptic_item(item)\n'
    )

    route_new = (
        '    def _route_synoptic_page(self, item: dict) -> None:\n'
        '        """Ouvre la page dans l\'espace correspondant à son état réel."""\n'
        '        # ROUTEUR_CENTRE_VERS_CONCEPTION_V1\n'
        '        conception_page = self._conception_page_for_synoptic_item(item)\n'
        '        if conception_page is not None:\n'
        '            self._hide_project_tools_for_subspace()\n'
        '            self._open_page(conception_page)\n'
        '            return\n'
        '\n'
        '        model_id = self._associated_model_id_for_synoptic_item(item)\n'
    )

    if route_old not in source:
        fail("routeur du synoptique introuvable")
    source = source.replace(route_old, route_new, 1)

    helper_anchor = '    def _route_synoptic_page(self, item: dict) -> None:\n'

    helper = (
        '    def _conception_page_for_synoptic_item(\n'
        '        self,\n'
        '        item: dict,\n'
        '    ) -> dict | None:\n'
        '        item_id = str(item.get("id", "")).strip()\n'
        '        if not item_id:\n'
        '            return None\n'
        '\n'
        '        try:\n'
        '            occurrence = max(\n'
        '                1,\n'
        '                int(item.get("_occurrence", 1) or 1),\n'
        '            )\n'
        '        except (TypeError, ValueError):\n'
        '            occurrence = 1\n'
        '\n'
        '        for page in self._load_project_pages():\n'
        '            if str(page.get("source_maquettage_id", "")).strip() != item_id:\n'
        '                continue\n'
        '\n'
        '            try:\n'
        '                page_occurrence = max(\n'
        '                    1,\n'
        '                    int(page.get("source_maquettage_occurrence", 1) or 1),\n'
        '                )\n'
        '            except (TypeError, ValueError):\n'
        '                page_occurrence = 1\n'
        '\n'
        '            if page_occurrence == occurrence:\n'
        '                return page\n'
        '\n'
        '        return None\n'
        '\n'
    )

    if helper_anchor not in source:
        fail("point d'insertion du lien Conception introuvable")
    source = source.replace(
        helper_anchor,
        helper + helper_anchor,
        1,
    )

    return source


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    if not PAGE_FILE.is_file():
        fail(f"fichier introuvable : {PAGE_FILE}")

    page_source = PAGE_FILE.read_text(encoding="utf-8")
    if REQUIRED_PAGE_MARKER not in page_source:
        fail(
            "le lien stable Maquettage -> Conception n'est pas installé "
            "dans page.py"
        )

    source = TARGET.read_text(encoding="utf-8")
    candidate = patch(source)

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    if candidate == source:
        print("ROUTEUR_CENTRE_VERS_CONCEPTION_V1_DEJA_APPLIQUE")
        return

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"document_view_avant_route_conception_{stamp}.py"
    )
    temp = TARGET.with_suffix(".route_conception.tmp")

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

    print("ROUTEUR_CENTRE_VERS_CONCEPTION_V1_OK")
    print("Priorité de clic : Conception -> Atelier -> Maquettage.")
    print("Le lien tient compte de l'occurrence exacte.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
