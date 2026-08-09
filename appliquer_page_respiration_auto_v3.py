from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"

REQUIRED = "CENTRE_VISUALISATION_DOUBLE_PAGE_V2"
MARKER = "PAGE_RESPIRATION_AUTO_V3"

REPLACEMENTS = [('        def item_accent(item: dict) -> str:\n            if bool(item.get("automatic_recto_verso", False)):\n                return "#AEB5BC"\n\n            group_id = str(\n', '        def item_accent(item: dict) -> str:\n            # PAGE_RESPIRATION_AUTO_V3\n            # Une page automatique conserve la couleur de son groupe :\n            # "automatique" décrit son origine, pas son identité graphique.\n            group_id = str(\n'), ('        def page_status(item: dict) -> tuple[str, str]:\n            if bool(item.get("automatic_recto_verso", False)):\n                return "BLANC AUTO", "#87919A"\n            return "MAQUETTAGE", item_accent(item)\n', '        def page_status(item: dict) -> tuple[str, str]:\n            if bool(item.get("automatic_recto_verso", False)):\n                return "AUTO  ✦", item_accent(item)\n            return "MAQUETTAGE", item_accent(item)\n'), ('            page_w = 101 * scale\n            page_h = 143 * scale\n\n            accent = item_accent(item)\n', '            automatic = bool(\n                item.get("automatic_recto_verso", False)\n            )\n\n            nominal_w = 101 * scale\n            nominal_h = 143 * scale\n\n            # Même format physique, représentation visuelle 6 % plus petite.\n            visual_ratio = 0.94 if automatic else 1.0\n            page_w = nominal_w * visual_ratio\n            page_h = nominal_h * visual_ratio\n\n            if automatic:\n                x += (nominal_w - page_w) / 2\n                y += (nominal_h - page_h) / 2\n\n            accent = item_accent(item)\n'), ('            title = item_title(item)\n\n            wall.create_text(\n', '            title = item_title(item)\n\n            if automatic:\n                wall.create_text(\n                    x + page_w - 9 * scale,\n                    y + 12 * scale,\n                    text="✦",\n                    fill=accent,\n                    font=(\n                        Fonts.FAMILY,\n                        max(8, int(10 * scale)),\n                        "bold",\n                    ),\n                    anchor="ne",\n                    tags=(tag,),\n                )\n\n            wall.create_text(\n'), ('            if not bool(item.get("automatic_recto_verso", False)):\n                wall.tag_bind(\n                    tag,\n                    "<Button-1>",\n                    lambda _evt: self._open_mockup(),\n                )\n                wall.tag_bind(\n                    tag,\n                    "<Enter>",\n                    lambda _evt: wall.configure(cursor="hand2"),\n                )\n                wall.tag_bind(\n                    tag,\n                    "<Leave>",\n                    lambda _evt: wall.configure(cursor="arrow"),\n                )\n\n            return page_w, page_h\n', '            # Une page automatique est désormais modifiable comme les autres.\n            wall.tag_bind(\n                tag,\n                "<Button-1>",\n                lambda _evt: self._open_mockup(),\n            )\n            wall.tag_bind(\n                tag,\n                "<Enter>",\n                lambda _evt: wall.configure(cursor="hand2"),\n            )\n            wall.tag_bind(\n                tag,\n                "<Leave>",\n                lambda _evt: wall.configure(cursor="arrow"),\n            )\n\n            return page_w, page_h\n')]


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if MARKER in original:
        print("PAGE_RESPIRATION_AUTO_V3_DEJA_APPLIQUEE")
        return

    if REQUIRED not in original:
        fail("la version Double page V2 n'est pas détectée")

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

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"document_view_avant_page_respiration_{stamp}.py"
    )
    temp = TARGET.with_suffix(".page_respiration.tmp")

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

    print("PAGE_RESPIRATION_AUTO_V3_OK")
    print("La page automatique conserve la couleur de son groupe.")
    print("Elle est représentée 6 % plus petite et marquée par ✦.")
    print("Son statut devient AUTO ✦.")
    print("Elle est désormais cliquable comme les autres pages.")
    print("Les calculs de production obligatoire restent inchangés.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
