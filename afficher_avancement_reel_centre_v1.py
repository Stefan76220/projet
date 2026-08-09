from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"

MARKER = "STATUTS_AVANCEMENT_CENTRE_V1"
REQUIRED = "ROUTEUR_CENTRE_VERS_CONCEPTION_V1"


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def patch(source: str) -> str:
    if MARKER in source:
        return source

    if REQUIRED not in source:
        fail("le routage Centre -> Conception n'est pas détecté")

    helper_anchor = (
        "    def _route_synoptic_page(self, item: dict) -> None:\n"
    )

    helper = (
        "    def _transferred_model_id_for_synoptic_item(\n"
        "        self,\n"
        "        item: dict,\n"
        "    ) -> str:\n"
        "        model_id = self._associated_model_id_for_synoptic_item(item)\n"
        "        if not model_id:\n"
        "            return \"\"\n"
        "\n"
        "        manifest_file = (\n"
        "            Path(self.project.models_folder)\n"
        "            / \"prets_conception\"\n"
        "            / \"manifest.json\"\n"
        "        )\n"
        "        if not manifest_file.is_file():\n"
        "            return \"\"\n"
        "\n"
        "        try:\n"
        "            with manifest_file.open(\"r\", encoding=\"utf-8\") as file:\n"
        "                data = json.load(file)\n"
        "        except (OSError, json.JSONDecodeError):\n"
        "            return \"\"\n"
        "\n"
        "        entries = (\n"
        "            data.get(\"gabarits\", [])\n"
        "            if isinstance(data, dict)\n"
        "            else []\n"
        "        )\n"
        "        for entry in entries:\n"
        "            if not isinstance(entry, dict):\n"
        "                continue\n"
        "            if str(entry.get(\"identifiant\", \"\")).strip() == model_id:\n"
        "                return model_id\n"
        "\n"
        "        return \"\"\n"
        "\n"
    )

    if helper_anchor not in source:
        fail("point d'insertion du statut Conception introuvable")

    source = source.replace(
        helper_anchor,
        helper + helper_anchor,
        1,
    )

    old_status = (
        "        def page_status(item: dict) -> tuple[str, str]:\n"
        "            # STATUT_GABARIT_CENTRE_V2\n"
        "            if bool(item.get(\"automatic_recto_verso\", False)):\n"
        "                return \"AUTO  ✦\", item_accent(item)\n"
        "\n"
        "            model_id = self._associated_model_id_for_synoptic_item(item)\n"
        "            if model_id:\n"
        "                return \"GABARIT\", self.ATELIER\n"
        "\n"
        "            return \"MAQUETTAGE\", item_accent(item)\n"
    )

    new_status = (
        "        def page_status(item: dict) -> tuple[str, str]:\n"
        "            # STATUT_GABARIT_CENTRE_V2\n"
        "            # STATUTS_AVANCEMENT_CENTRE_V1\n"
        "            if bool(item.get(\"automatic_recto_verso\", False)):\n"
        "                return \"AUTO  ✦\", item_accent(item)\n"
        "\n"
        "            if self._conception_page_for_synoptic_item(item) is not None:\n"
        "                return \"PRODUITE\", self.CONCEPTION\n"
        "\n"
        "            if self._transferred_model_id_for_synoptic_item(item):\n"
        "                return \"À PRODUIRE\", self.CONCEPTION\n"
        "\n"
        "            model_id = self._associated_model_id_for_synoptic_item(item)\n"
        "            if model_id:\n"
        "                return \"GABARIT\", self.ATELIER\n"
        "\n"
        "            return \"MAQUETTAGE\", item_accent(item)\n"
    )

    if old_status not in source:
        fail("fonction page_status actuelle introuvable")

    source = source.replace(
        old_status,
        new_status,
        1,
    )

    return source


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
        print("STATUTS_AVANCEMENT_CENTRE_V1_DEJA_APPLIQUE")
        return

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"document_view_avant_statuts_avancement_{stamp}.py"
    )
    temp = TARGET.with_suffix(".statuts_avancement.tmp")

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

    print("STATUTS_AVANCEMENT_CENTRE_V1_OK")
    print("MAQUETTAGE : aucun gabarit.")
    print("GABARIT : gabarit associé.")
    print("À PRODUIRE : gabarit transféré vers Conception.")
    print("PRODUITE : vraie page Conception liée.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
