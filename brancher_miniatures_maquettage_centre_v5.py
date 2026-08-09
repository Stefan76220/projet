from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"

REQUIRED = "PAGE_RESPIRATION_AUTO_V4"
MARKER = "MINIATURES_MAQUETTAGE_CENTRE_V5"

REPLACEMENTS = [('        wall._regulation_bg_photo = None\n', '        wall._regulation_bg_photo = None\n        # MINIATURES_MAQUETTAGE_CENTRE_V5\n        # Les PhotoImage des pages doivent rester référencées tant que\n        # le Canvas les affiche.\n        wall._page_thumb_photos = []\n'), ('        def expand_items() -> list[dict]:\n', '        def thumbnail_filename_for_type(page_type: str) -> str:\n            mapping = {\n                "couverture": "type_page_couverture.png",\n                "deuxieme_couverture": "type_page_deuxieme_couverture.png",\n                "page_titre": "type_page_titre.png",\n                "sommaire": "type_page_sommaire.png",\n                "avant_propos": "type_page_avant_propos.png",\n                "chapitre": "type_page_chapitre.png",\n                "fiche": "type_page_fiche.png",\n                "texte": "type_page_texte.png",\n                "illustration": "type_page_illustration.png",\n                "transition": "type_page_transition.png",\n                "page_blanche": "type_page_blanche.png",\n                "conclusion": "type_page_conclusion.png",\n                "troisieme_couverture": "type_page_troisieme_couverture.png",\n                "quatrieme": "type_page_quatrieme_couverture.png",\n            }\n            return mapping.get(\n                page_type,\n                "type_page_personnalisee.png",\n            )\n\n        def thumbnail_path_for_item(item: dict) -> Path | None:\n            page_type = str(item.get("type", ""))\n            definition = snapshot["page_types"].get(page_type, {})\n\n            # Les types personnalisés utilisent d\'abord leur miniature\n            # propre enregistrée par le Maquettage.\n            if bool(definition.get("custom", False)):\n                stored = str(\n                    definition.get("thumbnail", "")\n                ).strip()\n                if stored:\n                    path = Path(stored)\n                    if not path.is_absolute():\n                        project_root = getattr(\n                            self.project,\n                            "root",\n                            None,\n                        )\n                        if project_root is not None:\n                            path = Path(project_root) / path\n                    if path.is_file():\n                        return path\n\n            library = (\n                Path(__file__).resolve().parents[3]\n                / "assets"\n                / "page_thumbnails"\n            )\n\n            standard = (\n                library\n                / thumbnail_filename_for_type(page_type)\n            )\n            if standard.is_file():\n                return standard\n\n            generic = library / "type_page_personnalisee.png"\n            return generic if generic.is_file() else None\n\n        def expand_items() -> list[dict]:\n'), ('            wall.create_rectangle(\n                thumb_x1,\n                thumb_y1,\n                thumb_x2,\n                thumb_y2,\n                fill=soft,\n                outline=blend(accent, 0.35),\n                width=1,\n                tags=(tag,),\n            )\n\n            inner_w = thumb_x2 - thumb_x1\n            inner_h = thumb_y2 - thumb_y1\n\n            wall.create_rectangle(\n                thumb_x1 + 7 * scale,\n                thumb_y1 + 8 * scale,\n                thumb_x1 + inner_w * 0.43,\n                thumb_y1 + inner_h * 0.48,\n                fill="#FFFFFF",\n                outline=accent,\n                width=1,\n                tags=(tag,),\n            )\n\n            for line_index in range(4):\n                yy = (\n                    thumb_y1\n                    + 12 * scale\n                    + line_index * 8 * scale\n                )\n                wall.create_line(\n                    thumb_x1 + inner_w * 0.52,\n                    yy,\n                    thumb_x2 - 7 * scale,\n                    yy,\n                    fill=blend(accent, 0.50),\n                    width=1,\n                    tags=(tag,),\n                )\n\n            wall.create_line(\n                thumb_x1 + 7 * scale,\n                thumb_y2 - 13 * scale,\n                thumb_x2 - 7 * scale,\n                thumb_y2 - 13 * scale,\n                fill=blend(accent, 0.45),\n                width=1,\n                tags=(tag,),\n            )\n', '            wall.create_rectangle(\n                thumb_x1,\n                thumb_y1,\n                thumb_x2,\n                thumb_y2,\n                fill=soft,\n                outline=blend(accent, 0.35),\n                width=1,\n                tags=(tag,),\n            )\n\n            # Tant qu\'aucun gabarit réel n\'est enregistré, le Centre\n            # affiche exactement la miniature officielle du Maquettage.\n            thumbnail_path = thumbnail_path_for_item(item)\n            thumbnail_drawn = False\n\n            if thumbnail_path is not None:\n                try:\n                    from PIL import Image, ImageTk\n\n                    source = Image.open(thumbnail_path).convert("RGBA")\n                    available_w = max(\n                        1,\n                        int(round(thumb_x2 - thumb_x1 - 4 * scale)),\n                    )\n                    available_h = max(\n                        1,\n                        int(round(thumb_y2 - thumb_y1 - 4 * scale)),\n                    )\n\n                    source.thumbnail(\n                        (available_w, available_h),\n                        Image.Resampling.LANCZOS,\n                    )\n\n                    photo = ImageTk.PhotoImage(source)\n                    wall._page_thumb_photos.append(photo)\n\n                    wall.create_image(\n                        (thumb_x1 + thumb_x2) / 2,\n                        (thumb_y1 + thumb_y2) / 2,\n                        image=photo,\n                        anchor="center",\n                        tags=(tag,),\n                    )\n                    thumbnail_drawn = True\n                except Exception:\n                    thumbnail_drawn = False\n\n            # Secours uniquement si l\'image attendue est absente ou illisible.\n            if not thumbnail_drawn:\n                inner_w = thumb_x2 - thumb_x1\n                inner_h = thumb_y2 - thumb_y1\n\n                wall.create_rectangle(\n                    thumb_x1 + 7 * scale,\n                    thumb_y1 + 8 * scale,\n                    thumb_x1 + inner_w * 0.43,\n                    thumb_y1 + inner_h * 0.48,\n                    fill="#FFFFFF",\n                    outline=accent,\n                    width=1,\n                    tags=(tag,),\n                )\n\n                for line_index in range(4):\n                    yy = (\n                        thumb_y1\n                        + 12 * scale\n                        + line_index * 8 * scale\n                    )\n                    wall.create_line(\n                        thumb_x1 + inner_w * 0.52,\n                        yy,\n                        thumb_x2 - 7 * scale,\n                        yy,\n                        fill=blend(accent, 0.50),\n                        width=1,\n                        tags=(tag,),\n                    )\n\n                wall.create_line(\n                    thumb_x1 + 7 * scale,\n                    thumb_y2 - 13 * scale,\n                    thumb_x2 - 7 * scale,\n                    thumb_y2 - 13 * scale,\n                    fill=blend(accent, 0.45),\n                    width=1,\n                    tags=(tag,),\n                )\n'), ('            wall.delete("all")\n\n            left_margin = 22\n', '            wall.delete("all")\n            wall._page_thumb_photos = []\n\n            left_margin = 22\n')]


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if MARKER in original:
        print("MINIATURES_MAQUETTAGE_CENTRE_V5_DEJA_APPLIQUE")
        return

    if REQUIRED not in original:
        fail("la version Page respiration V4 n'est pas détectée")

    candidate = original

    for old, new in REPLACEMENTS:
        if old not in candidate:
            fail(
                "un bloc attendu n'a pas été trouvé ; "
                "le fichier a probablement changé"
            )
        candidate = candidate.replace(old, new, 1)

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    # Vérifie la présence de la bibliothèque standard déjà installée.
    thumb_dir = PROJECT / "assets" / "page_thumbnails"
    if not thumb_dir.is_dir():
        fail(
            "bibliothèque assets/page_thumbnails introuvable"
        )

    required_images = {
        "type_page_couverture.png",
        "type_page_deuxieme_couverture.png",
        "type_page_titre.png",
        "type_page_sommaire.png",
        "type_page_avant_propos.png",
        "type_page_chapitre.png",
        "type_page_fiche.png",
        "type_page_texte.png",
        "type_page_illustration.png",
        "type_page_transition.png",
        "type_page_blanche.png",
        "type_page_conclusion.png",
        "type_page_troisieme_couverture.png",
        "type_page_quatrieme_couverture.png",
        "type_page_personnalisee.png",
    }

    missing = sorted(
        name
        for name in required_images
        if not (thumb_dir / name).is_file()
    )
    if missing:
        fail(
            "miniatures manquantes : "
            + ", ".join(missing)
        )

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"document_view_avant_miniatures_centre_v5_{stamp}.py"
    )
    temp = TARGET.with_suffix(".miniatures_centre_v5.tmp")

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

    print("MINIATURES_MAQUETTAGE_CENTRE_V5_OK")
    print("Le synoptique utilise maintenant les vraies miniatures du Maquettage.")
    print("Les types personnalisés réutilisent leur PNG propre s'il existe.")
    print("Le statut reste MAQUETTAGE tant qu'aucun gabarit n'est branché.")
    print("Couverture, doubles pages et pages AUTO restent inchangées.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
