from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"
PAGE_FILE = PROJECT / "src" / "core" / "page.py"

MARKER = "CREATION_CONCEPTION_DEPUIS_GABARIT_V1"
REQUIRED_ROUTE = "ROUTE_A_PRODUIRE_VERS_CONCEPTION_V1"
REQUIRED_PAGE = "LIEN_STABLE_MAQUETTAGE_CONCEPTION_V1"


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def patch(source: str) -> str:
    if MARKER in source:
        return source

    if REQUIRED_ROUTE not in source:
        fail("le routage À PRODUIRE n'est pas détecté")

    helper_anchor = "    def _route_synoptic_page(self, item: dict) -> None:\n"

    helpers = (
        "    def _transferred_model_for_synoptic_item(self, item: dict):\n"
        "        model_id = self._transferred_model_id_for_synoptic_item(item)\n"
        "        if not model_id:\n"
        "            return None\n"
        "\n"
        "        try:\n"
        "            from src.core.model import Model\n"
        "        except Exception:\n"
        "            return None\n"
        "\n"
        "        ready_folder = (\n"
        "            Path(self.project.models_folder)\n"
        "            / \"prets_conception\"\n"
        "        )\n"
        "        manifest_file = ready_folder / \"manifest.json\"\n"
        "        if not manifest_file.is_file():\n"
        "            return None\n"
        "\n"
        "        try:\n"
        "            with manifest_file.open(\"r\", encoding=\"utf-8\") as file:\n"
        "                data = json.load(file)\n"
        "        except (OSError, json.JSONDecodeError):\n"
        "            return None\n"
        "\n"
        "        entries = data.get(\"gabarits\", []) if isinstance(data, dict) else []\n"
        "        for entry in entries:\n"
        "            if not isinstance(entry, dict):\n"
        "                continue\n"
        "            if str(entry.get(\"identifiant\", \"\")).strip() != model_id:\n"
        "                continue\n"
        "\n"
        "            folder_name = str(entry.get(\"dossier\", \"\")).strip()\n"
        "            if not folder_name:\n"
        "                return None\n"
        "\n"
        "            folder = ready_folder / folder_name\n"
        "            if not (folder / \"modele.json\").is_file():\n"
        "                return None\n"
        "\n"
        "            try:\n"
        "                return Model().load(folder)\n"
        "            except (OSError, ValueError, RuntimeError):\n"
        "                return None\n"
        "\n"
        "        return None\n"
        "\n"
        "    def _create_conception_page_from_synoptic(self, item: dict) -> bool:\n"
        "        # CREATION_CONCEPTION_DEPUIS_GABARIT_V1\n"
        "        model = self._transferred_model_for_synoptic_item(item)\n"
        "        if model is None:\n"
        "            return False\n"
        "\n"
        "        documents = list(getattr(self.project, \"documents\", []))\n"
        "        if not documents:\n"
        "            return False\n"
        "\n"
        "        document_name = str(documents[0].get(\"nom\", \"\")).strip()\n"
        "        if not document_name:\n"
        "            return False\n"
        "\n"
        "        item_id = str(item.get(\"id\", \"\")).strip()\n"
        "        if not item_id:\n"
        "            return False\n"
        "\n"
        "        try:\n"
        "            occurrence = max(1, int(item.get(\"_occurrence\", 1) or 1))\n"
        "        except (TypeError, ValueError):\n"
        "            occurrence = 1\n"
        "\n"
        "        try:\n"
        "            occurrence_count = max(\n"
        "                1,\n"
        "                int(item.get(\"_occurrence_count\", 1) or 1),\n"
        "            )\n"
        "        except (TypeError, ValueError):\n"
        "            occurrence_count = 1\n"
        "\n"
        "        try:\n"
        "            from copy import deepcopy\n"
        "\n"
        "            document = self.application.document_manager.load_document(\n"
        "                document_name\n"
        "            )\n"
        "\n"
        "            # Sécurité anti-doublon si un double clic survient.\n"
        "            for summary in list(getattr(document, \"pages\", [])):\n"
        "                if str(summary.get(\"source_maquettage_id\", \"\")).strip() != item_id:\n"
        "                    continue\n"
        "                try:\n"
        "                    summary_occurrence = max(\n"
        "                        1,\n"
        "                        int(summary.get(\"source_maquettage_occurrence\", 1) or 1),\n"
        "                    )\n"
        "                except (TypeError, ValueError):\n"
        "                    summary_occurrence = 1\n"
        "                if summary_occurrence == occurrence:\n"
        "                    existing = document.get_page(summary.get(\"numero\"))\n"
        "                    if existing is not None:\n"
        "                        self._hide_project_tools_for_subspace()\n"
        "                        PageEditorView(\n"
        "                            self.parent,\n"
        "                            existing,\n"
        "                            on_back=self._back_to_centre,\n"
        "                        ).show()\n"
        "                        return True\n"
        "\n"
        "            definition = deepcopy(model.page_definition)\n"
        "            editorial = definition.get(\"editorial\", {})\n"
        "\n"
        "            page_type = str(\n"
        "                editorial.get(\"type\", item.get(\"type\", \"Page produite\"))\n"
        "            ).strip() or \"Page produite\"\n"
        "\n"
        "            new_page = document.add_page(page_type=page_type)\n"
        "\n"
        "            title = str(item.get(\"title\", \"Page\")).strip() or \"Page\"\n"
        "            if occurrence_count > 1:\n"
        "                title = f\"{title} {occurrence}\"\n"
        "\n"
        "            new_page.title = title\n"
        "            new_page.color = str(editorial.get(\"couleur\", new_page.color))\n"
        "            new_page.icon = str(editorial.get(\"icone\", new_page.icon))\n"
        "            new_page.page_kind = \"page_produite\"\n"
        "            new_page.structure_workspace = \"\"\n"
        "            new_page.content_workspace = \"production\"\n"
        "            new_page.locked = False\n"
        "            new_page.source_model_id = model.identifier\n"
        "            new_page.source_model_version = model.version_label\n"
        "            new_page._load_layout(\n"
        "                deepcopy(definition.get(\"mise_en_page\", {}))\n"
        "            )\n"
        "            new_page.content = deepcopy(\n"
        "                definition.get(\"contenu_fixe\", {})\n"
        "            )\n"
        "            new_page.elements = deepcopy(\n"
        "                definition.get(\"elements\", [])\n"
        "            )\n"
        "            new_page.set_mockup_source(\n"
        "                item_id,\n"
        "                occurrence=occurrence,\n"
        "            )\n"
        "\n"
        "            try:\n"
        "                new_page._add_history(\n"
        "                    action=\"creation_conception\",\n"
        "                    description=(\n"
        "                        f\"Page créée dans Conception depuis le gabarit \"\n"
        "                        f\"« {model.name} » {model.version_label}.\"\n"
        "                    ),\n"
        "                )\n"
        "            except Exception:\n"
        "                pass\n"
        "\n"
        "            new_page.save(update_history=False)\n"
        "            document.update_page_summary(new_page)\n"
        "\n"
        "            self._hide_project_tools_for_subspace()\n"
        "            PageEditorView(\n"
        "                self.parent,\n"
        "                new_page,\n"
        "                on_back=self._back_to_centre,\n"
        "            ).show()\n"
        "            return True\n"
        "\n"
        "        except Exception:\n"
        "            return False\n"
        "\n"
    )

    if helper_anchor not in source:
        fail("point d'insertion du créateur Conception introuvable")

    source = source.replace(
        helper_anchor,
        helpers + helper_anchor,
        1,
    )

    route_old = (
        "        # ROUTE_A_PRODUIRE_VERS_CONCEPTION_V1\n"
        "        if self._transferred_model_id_for_synoptic_item(item):\n"
        "            self._open_atelier()\n"
        "            return\n"
    )

    route_new = (
        "        # ROUTE_A_PRODUIRE_VERS_CONCEPTION_V1\n"
        "        if self._transferred_model_id_for_synoptic_item(item):\n"
        "            if self._create_conception_page_from_synoptic(item):\n"
        "                return\n"
        "            self._open_atelier()\n"
        "            return\n"
    )

    if route_old not in source:
        fail("route À PRODUIRE actuelle introuvable")

    source = source.replace(route_old, route_new, 1)

    return source


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    if not PAGE_FILE.is_file():
        fail(f"fichier introuvable : {PAGE_FILE}")

    page_source = PAGE_FILE.read_text(encoding="utf-8")
    if REQUIRED_PAGE not in page_source:
        fail("le lien stable Maquettage -> Conception n'est pas installé")

    source = TARGET.read_text(encoding="utf-8")
    candidate = patch(source)

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    if candidate == source:
        print("CREATION_CONCEPTION_DEPUIS_GABARIT_V1_DEJA_APPLIQUE")
        return

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"document_view_avant_creation_conception_{stamp}.py"
    )
    temp = TARGET.with_suffix(".creation_conception.tmp")

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

    print("CREATION_CONCEPTION_DEPUIS_GABARIT_V1_OK")
    print("À PRODUIRE crée maintenant la vraie page depuis le gabarit.")
    print("L'origine Maquettage et l'occurrence sont enregistrées.")
    print("La page s'ouvre immédiatement dans Conception.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
