from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "core" / "page.py"

MARKER = "LIEN_STABLE_MAQUETTAGE_CONCEPTION_V1"


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def patch(source: str) -> str:
    if MARKER in source:
        return source

    init_old = (
        '        # Sources éventuelles\n'
        '        self.source_model_id = ""\n'
        '        self.source_model_version = ""\n'
        '        self.source_content_id = ""\n'
    )
    init_new = (
        '        # Sources éventuelles\n'
        '        self.source_model_id = ""\n'
        '        self.source_model_version = ""\n'
        '        self.source_content_id = ""\n'
        '\n'
        '        # LIEN_STABLE_MAQUETTAGE_CONCEPTION_V1\n'
        '        # Référence de la page logique prévue au Maquettage.\n'
        '        self.source_mockup_item_id = ""\n'
        '        self.source_mockup_occurrence = 1\n'
    )
    if init_old not in source:
        fail("bloc des sources de Page introuvable")
    source = source.replace(init_old, init_new, 1)

    load_old = (
        '        self.source_content_id = str(\n'
        '            sources.get(\n'
        '                "contenu",\n'
        '                "",\n'
        '            )\n'
        '        )\n'
        '\n'
        '        # Métadonnées\n'
    )
    load_new = (
        '        self.source_content_id = str(\n'
        '            sources.get(\n'
        '                "contenu",\n'
        '                "",\n'
        '            )\n'
        '        )\n'
        '\n'
        '        self.source_mockup_item_id = str(\n'
        '            sources.get(\n'
        '                "maquettage_item",\n'
        '                "",\n'
        '            )\n'
        '        ).strip()\n'
        '\n'
        '        try:\n'
        '            self.source_mockup_occurrence = max(\n'
        '                1,\n'
        '                int(sources.get("maquettage_occurrence", 1)),\n'
        '            )\n'
        '        except (TypeError, ValueError):\n'
        '            self.source_mockup_occurrence = 1\n'
        '\n'
        '        # Métadonnées\n'
    )
    if load_old not in source:
        fail("chargement des sources de Page introuvable")
    source = source.replace(load_old, load_new, 1)

    summary_old = (
        '            "verrouillee": self.locked,\n'
        '            "dossier": self.folder_name,\n'
        '            "date_creation": self.created,\n'
    )
    summary_new = (
        '            "verrouillee": self.locked,\n'
        '            "dossier": self.folder_name,\n'
        '            "source_modele": self.source_model_id,\n'
        '            "source_maquettage_id": self.source_mockup_item_id,\n'
        '            "source_maquettage_occurrence": self.source_mockup_occurrence,\n'
        '            "date_creation": self.created,\n'
    )
    if summary_old not in source:
        fail("résumé de Page introuvable")
    source = source.replace(summary_old, summary_new, 1)

    dict_old = (
        '                "sources": {\n'
        '                    "modele": self.source_model_id,\n'
        '                    "version_modele": self.source_model_version,\n'
        '                    "contenu": self.source_content_id,\n'
        '                },\n'
    )
    dict_new = (
        '                "sources": {\n'
        '                    "modele": self.source_model_id,\n'
        '                    "version_modele": self.source_model_version,\n'
        '                    "contenu": self.source_content_id,\n'
        '                    "maquettage_item": self.source_mockup_item_id,\n'
        '                    "maquettage_occurrence": self.source_mockup_occurrence,\n'
        '                },\n'
    )
    if dict_old not in source:
        fail("sérialisation des sources de Page introuvable")
    source = source.replace(dict_old, dict_new, 1)

    method_anchor = (
        '    # ==========================================================\n'
        '    # Création\n'
        '    # ==========================================================\n'
        '\n'
        '    def create(\n'
    )
    method_new = (
        '    def set_mockup_source(\n'
        '        self,\n'
        '        item_id: str,\n'
        '        occurrence: int = 1,\n'
        '    ) -> None:\n'
        '        # Associe cette page à une occurrence précise du Maquettage.\n'
        '        self.source_mockup_item_id = str(item_id or "").strip()\n'
        '\n'
        '        try:\n'
        '            self.source_mockup_occurrence = max(1, int(occurrence))\n'
        '        except (TypeError, ValueError):\n'
        '            self.source_mockup_occurrence = 1\n'
        '\n'
        '    # ==========================================================\n'
        '    # Création\n'
        '    # ==========================================================\n'
        '\n'
        '    def create(\n'
    )
    if method_anchor not in source:
        fail("point d'insertion de set_mockup_source introuvable")
    source = source.replace(method_anchor, method_new, 1)

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
        print("LIEN_STABLE_MAQUETTAGE_CONCEPTION_V1_DEJA_APPLIQUE")
        return

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"page_avant_lien_maquettage_conception_{stamp}.py"
    )
    temp = TARGET.with_suffix(".lien_maquettage_conception.tmp")

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

    print("LIEN_STABLE_MAQUETTAGE_CONCEPTION_V1_OK")
    print("Chaque page peut maintenant mémoriser son origine Maquettage.")
    print("Le lien comprend l'identifiant logique et l'occurrence.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
