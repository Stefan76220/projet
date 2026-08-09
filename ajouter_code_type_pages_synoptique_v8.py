from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"

REQUIRED = "SYNOPTIQUE_VISUEL_EPURE_V7"
MARKER = "CODE_TYPE_PAGE_V8"

OLD_HELPER_ANCHOR = '        def expand_items() -> list[dict]:\n'
NEW_HELPER = '        def type_code_for_item(item: dict) -> str:\n            # CODE_TYPE_PAGE_V8\n            # Code très court intégré au bandeau de couleur pour identifier\n            # le type sans ajouter de cartouche ni de hauteur.\n            page_type = str(item.get("type", ""))\n\n            mapping = {\n                "couverture": "COUV",\n                "deuxieme_couverture": "2C",\n                "page_titre": "TITRE",\n                "sommaire": "SOM",\n                "avant_propos": "AVP",\n                "chapitre": "CHAP",\n                "fiche": "FICHE",\n                "texte": "TXT",\n                "illustration": "ILL",\n                "transition": "TRANS",\n                "page_blanche": "BL",\n                "conclusion": "CONCL",\n                "troisieme_couverture": "3C",\n                "quatrieme": "4C",\n            }\n\n            if page_type in mapping:\n                return mapping[page_type]\n\n            definition = snapshot["page_types"].get(page_type, {})\n            short = str(\n                definition.get("short")\n                or definition.get("title")\n                or page_type\n                or "PAGE"\n            ).strip()\n\n            compact = "".join(\n                character\n                for character in short.upper()\n                if character.isalnum()\n            )\n\n            return compact[:5] or "PAGE"\n\n        def expand_items() -> list[dict]:\n'
OLD_BAND = '            wall.create_rectangle(\n                x,\n                y,\n                x + page_w,\n                y + band_h,\n                fill=accent,\n                outline="",\n                tags=(tag,),\n            )\n\n            if automatic:\n'
NEW_BAND = '            wall.create_rectangle(\n                x,\n                y,\n                x + page_w,\n                y + band_h,\n                fill=accent,\n                outline="",\n                tags=(tag,),\n            )\n\n            wall.create_text(\n                x + 4 * scale,\n                y + band_h / 2,\n                text=type_code_for_item(item),\n                fill="#FFFFFF",\n                font=(\n                    Fonts.FAMILY,\n                    max(5, int(5.5 * scale)),\n                    "bold",\n                ),\n                anchor="w",\n                tags=(tag,),\n            )\n\n            if automatic:\n'


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if MARKER in original:
        print("CODE_TYPE_PAGE_V8_DEJA_APPLIQUE")
        return

    if REQUIRED not in original:
        fail("la version Synoptique visuel V7 n'est pas détectée")

    if OLD_HELPER_ANCHOR not in original:
        fail("point d'insertion du code type introuvable")

    candidate = original.replace(
        OLD_HELPER_ANCHOR,
        NEW_HELPER,
        1,
    )

    if OLD_BAND not in candidate:
        fail("bandeau de couleur actuel introuvable")

    candidate = candidate.replace(
        OLD_BAND,
        NEW_BAND,
        1,
    )

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"document_view_avant_code_type_v8_{stamp}.py"
    temp = TARGET.with_suffix(".code_type_v8.tmp")

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

    print("CODE_TYPE_PAGE_V8_OK")
    print("Le type de page est maintenant indiqué dans le bandeau coloré.")
    print("Aucune hauteur supplémentaire n'est ajoutée.")
    print("La logique double page et les statuts restent inchangés.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
