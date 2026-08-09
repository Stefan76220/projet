from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "core" / "production.py"
PAGE_FILE = PROJECT / "src" / "core" / "page.py"

MARKER = "PRODUCTION_LIEE_MAQUETTAGE_V1"
REQUIRED_PAGE_MARKER = "LIEN_STABLE_MAQUETTAGE_CONCEPTION_V1"


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def patch(source: str) -> str:
    if MARKER in source:
        return source

    signature_old = (
        "    def produce_page(\n"
        "        self,\n"
        "        document: Document,\n"
        "        model: Model,\n"
        "        sheet: ContentSheet,\n"
        "        *,\n"
        "        title: str | None = None,\n"
        '        mapping_mode: str = "automatique",\n'
        "    ) -> ProductionResult:\n"
    )
    signature_new = (
        "    def produce_page(\n"
        "        self,\n"
        "        document: Document,\n"
        "        model: Model,\n"
        "        sheet: ContentSheet,\n"
        "        *,\n"
        "        title: str | None = None,\n"
        '        mapping_mode: str = "automatique",\n'
        '        source_mockup_item_id: str = "",\n'
        "        source_mockup_occurrence: int = 1,\n"
        "    ) -> ProductionResult:\n"
    )
    if signature_old not in source:
        fail("signature de ProductionEngine.produce_page introuvable")
    source = source.replace(signature_old, signature_new, 1)

    save_old = (
        "            self._apply_page_definition(\n"
        "                page=page,\n"
        "                page_definition=page_definition,\n"
        "                model=model,\n"
        "                sheet=sheet,\n"
        "                title=title,\n"
        "                assignments=assignments,\n"
        "            )\n"
        "\n"
        "            page.save(\n"
    )
    save_new = (
        "            self._apply_page_definition(\n"
        "                page=page,\n"
        "                page_definition=page_definition,\n"
        "                model=model,\n"
        "                sheet=sheet,\n"
        "                title=title,\n"
        "                assignments=assignments,\n"
        "            )\n"
        "\n"
        "            # PRODUCTION_LIEE_MAQUETTAGE_V1\n"
        "            if str(source_mockup_item_id or \"\").strip():\n"
        "                page.set_mockup_source(\n"
        "                    source_mockup_item_id,\n"
        "                    occurrence=source_mockup_occurrence,\n"
        "                )\n"
        "\n"
        "            page.save(\n"
    )
    if save_old not in source:
        fail("point de sauvegarde de la page produite introuvable")
    source = source.replace(save_old, save_new, 1)

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
        print("PRODUCTION_LIEE_MAQUETTAGE_V1_DEJA_APPLIQUE")
        return

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"production_avant_lien_maquettage_{stamp}.py"
    )
    temp = TARGET.with_suffix(".production_liee_maquettage.tmp")

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

    print("PRODUCTION_LIEE_MAQUETTAGE_V1_OK")
    print("Le moteur de production accepte maintenant l'origine Maquettage.")
    print("Compatibilité conservée pour les anciens appels.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
