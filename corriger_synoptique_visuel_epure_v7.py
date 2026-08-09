from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"

REQUIRED = "MINIATURES_MAQUETTAGE_CENTRE_V5"
MARKER = "SYNOPTIQUE_VISUEL_EPURE_V7"

NEW_STATUS = '        def page_status(item: dict) -> tuple[str, str]:\n            # SYNOPTIQUE_VISUEL_EPURE_V7\n            # La phase d\'avancement est indépendante de la nature de la page.\n            # Une page automatique reste donc "Maquettage" tant qu\'elle\n            # n\'a pas progressé vers l\'Atelier/Conception.\n            return "Maquettage", self.MAQUETTAGE\n'
NEW_DRAW = '        def draw_page(\n            x: float,\n            y: float,\n            item: dict,\n            *,\n            page_side: str,\n            page_number: int | None,\n            scale: float = 1.0,\n        ) -> tuple[float, float]:\n            automatic = bool(\n                item.get("automatic_recto_verso", False)\n            )\n\n            nominal_w = 101 * scale\n            nominal_h = 143 * scale\n\n            visual_ratio = 0.90 if automatic else 1.0\n            page_w = nominal_w * visual_ratio\n            page_h = nominal_h * visual_ratio\n\n            if automatic:\n                x += (nominal_w - page_w) / 2\n                y += (nominal_h - page_h) / 2\n\n            accent = item_accent(item)\n            phase_text, phase_color = page_status(item)\n\n            tag = (\n                f"visual_page_"\n                f"{item.get(\'_source_index\', 0)}_"\n                f"{item.get(\'_occurrence\', 1)}"\n            )\n\n            wall.create_rectangle(\n                x,\n                y,\n                x + page_w,\n                y + page_h,\n                fill="#FFFDFC",\n                outline=accent,\n                width=1,\n                tags=(tag,),\n            )\n\n            image_x1 = x + 1\n            image_y1 = y + 1\n            image_x2 = x + page_w - 1\n            image_y2 = y + page_h - 1\n\n            thumbnail_path = thumbnail_path_for_item(item)\n            thumbnail_drawn = False\n\n            if thumbnail_path is not None:\n                try:\n                    from PIL import Image, ImageTk\n\n                    source = Image.open(thumbnail_path).convert("RGBA")\n                    available_w = max(\n                        1,\n                        int(round(image_x2 - image_x1)),\n                    )\n                    available_h = max(\n                        1,\n                        int(round(image_y2 - image_y1)),\n                    )\n\n                    source = source.resize(\n                        (available_w, available_h),\n                        Image.Resampling.LANCZOS,\n                    )\n\n                    photo = ImageTk.PhotoImage(source)\n                    wall._page_thumb_photos.append(photo)\n\n                    wall.create_image(\n                        image_x1,\n                        image_y1,\n                        image=photo,\n                        anchor="nw",\n                        tags=(tag,),\n                    )\n                    thumbnail_drawn = True\n                except Exception:\n                    thumbnail_drawn = False\n\n            if not thumbnail_drawn:\n                wall.create_rectangle(\n                    image_x1,\n                    image_y1,\n                    image_x2,\n                    image_y2,\n                    fill=blend(accent, 0.90),\n                    outline="",\n                    tags=(tag,),\n                )\n                for index in range(5):\n                    yy = image_y1 + 18 * scale + index * 12 * scale\n                    wall.create_line(\n                        image_x1 + 12 * scale,\n                        yy,\n                        image_x2 - 12 * scale,\n                        yy,\n                        fill=blend(accent, 0.48),\n                        width=1,\n                        tags=(tag,),\n                    )\n\n            band_h = 6 * scale\n            wall.create_rectangle(\n                x,\n                y,\n                x + page_w,\n                y + band_h,\n                fill=accent,\n                outline="",\n                tags=(tag,),\n            )\n\n            if automatic:\n                wall.create_text(\n                    x + page_w - 5 * scale,\n                    y + band_h / 2,\n                    text="✦",\n                    fill="#FFFFFF",\n                    font=(\n                        Fonts.FAMILY,\n                        max(7, int(8 * scale)),\n                        "bold",\n                    ),\n                    anchor="e",\n                    tags=(tag,),\n                )\n\n            phase_y = y + page_h + 10 * scale\n            dot_r = 2.7 * scale\n            phase_center_x = x + page_w / 2\n            estimated_text_w = 46 * scale\n            dot_x = phase_center_x - estimated_text_w / 2\n\n            wall.create_oval(\n                dot_x - dot_r,\n                phase_y - dot_r,\n                dot_x + dot_r,\n                phase_y + dot_r,\n                fill=phase_color,\n                outline="",\n                tags=(tag,),\n            )\n            wall.create_text(\n                dot_x + 7 * scale,\n                phase_y,\n                text=phase_text,\n                fill=phase_color,\n                font=(\n                    Fonts.FAMILY,\n                    max(6, int(7 * scale)),\n                    "bold",\n                ),\n                anchor="w",\n                tags=(tag,),\n            )\n\n            if page_number is not None:\n                number_x = (\n                    x\n                    if page_side == "left"\n                    else x + page_w\n                )\n                number_anchor = (\n                    "nw"\n                    if page_side == "left"\n                    else "ne"\n                )\n                wall.create_text(\n                    number_x,\n                    phase_y + 9 * scale,\n                    text=str(page_number),\n                    fill=self.TEXT_MUTED,\n                    font=(Fonts.FAMILY, max(6, int(7 * scale))),\n                    anchor=number_anchor,\n                    tags=(tag,),\n                )\n\n            wall.tag_bind(\n                tag,\n                "<Button-1>",\n                lambda _evt: self._open_mockup(),\n            )\n            wall.tag_bind(\n                tag,\n                "<Enter>",\n                lambda _evt: wall.configure(cursor="hand2"),\n            )\n            wall.tag_bind(\n                tag,\n                "<Leave>",\n                lambda _evt: wall.configure(cursor="arrow"),\n            )\n\n            return page_w, page_h\n'
OLD_SINGLE = '                    if kind in {"single_cover", "single_back"}:\n                        item = unit["pages"][0]\n\n                        label = (\n                            "COUVERTURE"\n                            if kind == "single_cover"\n                            else "4e DE COUVERTURE"\n                        )\n\n                        wall.create_text(\n                            ux + unit_w / 2,\n                            uy + 7,\n                            text=label,\n                            fill=self.TEXT_MUTED,\n                            font=(Fonts.FAMILY, 7, "bold"),\n                            anchor="n",\n                        )\n\n                        draw_page(\n                            ux + (unit_w - 111) / 2,\n                            uy + 24,\n'
NEW_SINGLE = '                    if kind in {"single_cover", "single_back"}:\n                        item = unit["pages"][0]\n\n                        draw_page(\n                            ux + (unit_w - 111) / 2,\n                            uy + 10,\n'
OLD_SPREAD = '                        wall.create_rectangle(\n                            ux + 5,\n                            uy + 17,\n                            ux + unit_w - 5,\n                            uy + unit_h - 5,\n                            fill="#FFFFFF",\n                            outline=blend("#718096", 0.70),\n                            width=1,\n                            stipple="gray25",\n                        )\n\n                        wall.create_text(\n                            ux + unit_w / 2,\n                            uy + 6,\n                            text="DOUBLE PAGE",\n                            fill=self.TEXT_MUTED,\n                            font=(Fonts.FAMILY, 7, "bold"),\n                            anchor="n",\n                        )\n\n                        page_y = uy + 27\n'
NEW_SPREAD = '                        # Un seul cadre léger matérialise la double page.\n                        # Aucun fond : le décor PageMaître reste visible.\n                        wall.create_rectangle(\n                            ux + 5,\n                            uy + 4,\n                            ux + unit_w - 5,\n                            uy + unit_h - 4,\n                            fill="",\n                            outline=blend("#718096", 0.64),\n                            width=1,\n                        )\n\n                        page_y = uy + 10\n'


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def replace_nested(source: str, start_marker: str, end_marker: str, replacement: str) -> str:
    try:
        start = source.index(start_marker)
        end = source.index(end_marker, start)
    except ValueError:
        fail(f"bloc introuvable : {start_marker.strip()}")
    return source[:start] + replacement.rstrip() + "\n\n" + source[end:]


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if MARKER in original:
        print("SYNOPTIQUE_VISUEL_EPURE_V7_DEJA_APPLIQUE")
        return

    if REQUIRED not in original:
        fail("la version Centre V5 n'est pas détectée")

    candidate = replace_nested(
        original,
        "        def page_status(item: dict) -> tuple[str, str]:",
        "        def make_background",
        NEW_STATUS,
    )

    candidate = replace_nested(
        candidate,
        "        def draw_page(",
        "        def make_display_units()",
        NEW_DRAW,
    )

    if OLD_SINGLE not in candidate:
        fail("bloc Couverture / 4e introuvable")
    candidate = candidate.replace(OLD_SINGLE, NEW_SINGLE, 1)

    if OLD_SPREAD not in candidate:
        fail("bloc Double page introuvable")
    candidate = candidate.replace(OLD_SPREAD, NEW_SPREAD, 1)

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"document_view_avant_synoptique_epure_v7_{stamp}.py"
    )
    temp = TARGET.with_suffix(".synoptique_epure_v7.tmp")

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

    print("SYNOPTIQUE_VISUEL_EPURE_V7_OK")
    print("La miniature remplit maintenant toute la page.")
    print("Seul le fin bandeau de couleur reste sur la vignette.")
    print("Les libellés Couverture / Double page / 4e ont disparu.")
    print("La phase Maquettage est affichée hors page par un voyant discret.")
    print("La page automatique conserve son étoile et sa taille réduite.")
    print("Le cadre de double page est transparent.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
