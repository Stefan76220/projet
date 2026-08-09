from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"

REQUIRED = "MINIATURES_MAQUETTAGE_CENTRE_V5"
MARKER = "PAGE_VISUELLE_PLEINE_V6"

REPLACEMENTS = [('            # Bande de famille / type.\n            wall.create_rectangle(\n                x,\n                y,\n                x + page_w,\n                y + 7 * scale,\n                fill=accent,\n                outline="",\n                tags=(tag,),\n            )\n\n            thumb_x1 = x + 12 * scale\n            thumb_y1 = y + 17 * scale\n            thumb_x2 = x + page_w - 12 * scale\n            thumb_y2 = y + 84 * scale\n', '            # PAGE_VISUELLE_PLEINE_V6\n            # La miniature est la page : plus de fiche dans la fiche.\n            # Seul un fin bandeau de couleur rappelle son groupe/type.\n            wall.create_rectangle(\n                x,\n                y,\n                x + page_w,\n                y + 6 * scale,\n                fill=accent,\n                outline="",\n                tags=(tag,),\n            )\n\n            thumb_x1 = x + 1 * scale\n            thumb_y1 = y + 6 * scale\n            thumb_x2 = x + page_w - 1 * scale\n            thumb_y2 = y + page_h - 1 * scale\n'), ('                    available_w = max(\n                        1,\n                        int(round(thumb_x2 - thumb_x1 - 4 * scale)),\n                    )\n                    available_h = max(\n                        1,\n                        int(round(thumb_y2 - thumb_y1 - 4 * scale)),\n                    )\n\n                    source.thumbnail(\n                        (available_w, available_h),\n                        Image.Resampling.LANCZOS,\n                    )\n\n                    photo = ImageTk.PhotoImage(source)\n', '                    available_w = max(\n                        1,\n                        int(round(thumb_x2 - thumb_x1)),\n                    )\n                    available_h = max(\n                        1,\n                        int(round(thumb_y2 - thumb_y1)),\n                    )\n\n                    # Recadrage "cover" : la vignette remplit réellement\n                    # la page, sans bande vide autour.\n                    source_ratio = source.width / max(1, source.height)\n                    target_ratio = available_w / max(1, available_h)\n\n                    if target_ratio > source_ratio:\n                        resize_w = available_w\n                        resize_h = max(\n                            available_h,\n                            int(round(available_w / source_ratio)),\n                        )\n                    else:\n                        resize_h = available_h\n                        resize_w = max(\n                            available_w,\n                            int(round(available_h * source_ratio)),\n                        )\n\n                    source = source.resize(\n                        (resize_w, resize_h),\n                        Image.Resampling.LANCZOS,\n                    )\n\n                    crop_left = max(0, (resize_w - available_w) // 2)\n                    crop_top = max(0, (resize_h - available_h) // 2)\n                    source = source.crop(\n                        (\n                            crop_left,\n                            crop_top,\n                            crop_left + available_w,\n                            crop_top + available_h,\n                        )\n                    )\n\n                    photo = ImageTk.PhotoImage(source)\n'), ('            title = item_title(item)\n\n            if automatic:\n                wall.create_text(\n                    x + page_w - 9 * scale,\n                    y + 12 * scale,\n                    text="✦",\n                    fill=accent,\n                    font=(\n                        Fonts.FAMILY,\n                        max(8, int(10 * scale)),\n                        "bold",\n                    ),\n                    anchor="ne",\n                    tags=(tag,),\n                )\n\n            wall.create_text(\n                x + 8 * scale,\n                y + 92 * scale,\n                text=self._truncate(title, 18),\n                fill=self.INK,\n                font=(Fonts.FAMILY, max(7, int(8 * scale)), "bold"),\n                anchor="nw",\n                tags=(tag,),\n            )\n\n            pill_x1 = x + 8 * scale\n            pill_y1 = y + 111 * scale\n            pill_x2 = x + page_w - 8 * scale\n            pill_y2 = y + 128 * scale\n\n            wall.create_rectangle(\n                pill_x1,\n                pill_y1,\n                pill_x2,\n                pill_y2,\n                fill=blend(status_color, 0.84),\n                outline=blend(status_color, 0.35),\n                width=1,\n                tags=(tag,),\n            )\n\n            wall.create_text(\n                (pill_x1 + pill_x2) / 2,\n                (pill_y1 + pill_y2) / 2,\n                text=status_text,\n                fill=status_color,\n                font=(Fonts.FAMILY, max(6, int(7 * scale)), "bold"),\n                anchor="center",\n                tags=(tag,),\n            )\n\n            if page_number is not None:\n                anchor = "sw" if page_side == "left" else "se"\n                number_x = (\n                    x + 8 * scale\n                    if page_side == "left"\n                    else x + page_w - 8 * scale\n                )\n                wall.create_text(\n                    number_x,\n                    y + page_h - 5 * scale,\n                    text=str(page_number),\n                    fill=self.TEXT_MUTED,\n                    font=(Fonts.FAMILY, max(6, int(7 * scale))),\n                    anchor=anchor,\n                    tags=(tag,),\n                )\n', '            title = item_title(item)\n\n            if automatic:\n                # Marque décorative de respiration, posée sur le bandeau.\n                wall.create_text(\n                    x + page_w - 6 * scale,\n                    y + 3 * scale,\n                    text="✦",\n                    fill="#FFFFFF",\n                    font=(\n                        Fonts.FAMILY,\n                        max(7, int(8 * scale)),\n                        "bold",\n                    ),\n                    anchor="e",\n                    tags=(tag,),\n                )\n\n            # Le statut sort de la page : petit onglet de suivi accroché\n            # sous la vignette, comme une étiquette de régulation.\n            tab_h = 14 * scale\n            tab_w = min(page_w * 0.72, 72 * scale)\n            tab_x1 = x + (page_w - tab_w) / 2\n            tab_y1 = y + page_h + 3 * scale\n            tab_x2 = tab_x1 + tab_w\n            tab_y2 = tab_y1 + tab_h\n\n            wall.create_rectangle(\n                tab_x1,\n                tab_y1,\n                tab_x2,\n                tab_y2,\n                fill=blend(status_color, 0.76),\n                outline=status_color,\n                width=1,\n                tags=(tag,),\n            )\n\n            wall.create_text(\n                (tab_x1 + tab_x2) / 2,\n                (tab_y1 + tab_y2) / 2,\n                text=status_text,\n                fill=status_color,\n                font=(\n                    Fonts.FAMILY,\n                    max(6, int(7 * scale)),\n                    "bold",\n                ),\n                anchor="center",\n                tags=(tag,),\n            )\n\n            # Numéro hors de la page pour préserver totalement le visuel.\n            if page_number is not None:\n                number_x = (\n                    x\n                    if page_side == "left"\n                    else x + page_w\n                )\n                wall.create_text(\n                    number_x,\n                    tab_y2 + 3 * scale,\n                    text=str(page_number),\n                    fill=self.TEXT_MUTED,\n                    font=(Fonts.FAMILY, max(6, int(7 * scale))),\n                    anchor="n" if page_side == "left" else "n",\n                    tags=(tag,),\n                )\n'), ('                        wall.create_text(\n                            ux + unit_w / 2,\n                            uy + 7,\n                            text=label,\n                            fill=self.TEXT_MUTED,\n                            font=(Fonts.FAMILY, 7, "bold"),\n                            anchor="n",\n                        )\n\n                        draw_page(\n                            ux + (unit_w - 111) / 2,\n                            uy + 24,\n', '                        draw_page(\n                            ux + (unit_w - 111) / 2,\n                            uy + 10,\n'), ('                        wall.create_text(\n                            ux + unit_w / 2,\n                            uy + 6,\n                            text="DOUBLE PAGE",\n                            fill=self.TEXT_MUTED,\n                            font=(Fonts.FAMILY, 7, "bold"),\n                            anchor="n",\n                        )\n\n                        page_y = uy + 27\n', '                        page_y = uy + 12\n')]


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if MARKER in original:
        print("PAGE_VISUELLE_PLEINE_V6_DEJA_APPLIQUEE")
        return

    if REQUIRED not in original:
        fail("la version Miniatures Centre V5 n'est pas détectée")

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
        / f"document_view_avant_page_visuelle_v6_{stamp}.py"
    )
    temp = TARGET.with_suffix(".page_visuelle_v6.tmp")

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

    print("PAGE_VISUELLE_PLEINE_V6_OK")
    print("La miniature remplit désormais tout le cadre de page.")
    print("Seul le bandeau de couleur reste dans la page.")
    print("Les libellés Couverture / Double page / 4e ont été retirés.")
    print("Le statut devient un onglet extérieur sous chaque page.")
    print("La disposition couverture / doubles pages / quatrième est conservée.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
