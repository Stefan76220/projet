from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"

MARKER = "ROUTE_A_PRODUIRE_VERS_CONCEPTION_V1"
REQUIRED = "STATUTS_AVANCEMENT_CENTRE_V1"


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def patch(source: str) -> str:
    if MARKER in source:
        return source

    if REQUIRED not in source:
        fail("les statuts d'avancement du Centre ne sont pas détectés")

    old = (
        "        conception_page = self._conception_page_for_synoptic_item(item)\n"
        "        if conception_page is not None:\n"
        "            self._hide_project_tools_for_subspace()\n"
        "            self._open_page(conception_page)\n"
        "            return\n"
        "\n"
        "        model_id = self._associated_model_id_for_synoptic_item(item)\n"
    )

    new = (
        "        conception_page = self._conception_page_for_synoptic_item(item)\n"
        "        if conception_page is not None:\n"
        "            self._hide_project_tools_for_subspace()\n"
        "            self._open_page(conception_page)\n"
        "            return\n"
        "\n"
        "        # ROUTE_A_PRODUIRE_VERS_CONCEPTION_V1\n"
        "        if self._transferred_model_id_for_synoptic_item(item):\n"
        "            self._open_atelier()\n"
        "            return\n"
        "\n"
        "        model_id = self._associated_model_id_for_synoptic_item(item)\n"
    )

    if old not in source:
        fail("routeur Centre actuel introuvable")

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
        print("ROUTE_A_PRODUIRE_VERS_CONCEPTION_V1_DEJA_APPLIQUE")
        return

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"document_view_avant_route_a_produire_{stamp}.py"
    )
    temp = TARGET.with_suffix(".route_a_produire.tmp")

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

    print("ROUTE_A_PRODUIRE_VERS_CONCEPTION_V1_OK")
    print("PRODUITE : ouvre directement la page Conception.")
    print("À PRODUIRE : ouvre le Bureau Conception.")
    print("GABARIT : ouvre l'Atelier.")
    print("MAQUETTAGE : ouvre le Maquettage.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
