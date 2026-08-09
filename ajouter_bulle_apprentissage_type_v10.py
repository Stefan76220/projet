from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "document_view.py"

REQUIRED = "CODE_TYPE_PAGE_LISIBLE_V9"
MARKER = "BULLE_TYPE_PAGE_V10"

OLD_WALL_STATE = """        wall._regulation_bg_photo = None
        # MINIATURES_MAQUETTAGE_CENTRE_V5
"""

NEW_WALL_STATE = """        wall._regulation_bg_photo = None
        # BULLE_TYPE_PAGE_V10
        wall._type_tooltip_after = None
        # MINIATURES_MAQUETTAGE_CENTRE_V5
"""

OLD_HELPER_ANCHOR = """        def expand_items() -> list[dict]:
"""

NEW_HELPERS = """        def type_label_for_item(item: dict) -> str:
            page_type = str(item.get("type", ""))

            labels = {
                "couverture": "Couverture",
                "deuxieme_couverture": "Deuxième de couverture",
                "page_titre": "Page de titre",
                "sommaire": "Sommaire",
                "avant_propos": "Avant-propos",
                "chapitre": "Chapitre",
                "fiche": "Fiche",
                "texte": "Page de texte",
                "illustration": "Illustration",
                "transition": "Page de transition",
                "page_blanche": "Page blanche",
                "conclusion": "Conclusion",
                "troisieme_couverture": "Troisième de couverture",
                "quatrieme": "Quatrième de couverture",
            }

            if page_type in labels:
                return labels[page_type]

            definition = snapshot["page_types"].get(page_type, {})
            return str(
                definition.get("title")
                or definition.get("short")
                or page_type.replace("_", " ").title()
                or "Page"
            )

        def hide_type_tooltip() -> None:
            pending = getattr(
                wall,
                "_type_tooltip_after",
                None,
            )
            if pending is not None:
                try:
                    wall.after_cancel(pending)
                except tk.TclError:
                    pass
                wall._type_tooltip_after = None

            wall.delete("type_page_tooltip")

        def show_type_tooltip(
            event,
            item: dict,
        ) -> None:
            hide_type_tooltip()

            code = type_code_for_item(item)
            label = type_label_for_item(item)
            accent = item_accent(item)

            canvas_x = wall.canvasx(event.x)
            canvas_y = wall.canvasy(event.y)

            def display() -> None:
                wall._type_tooltip_after = None
                wall.delete("type_page_tooltip")

                text = f"{code}  ·  {label}"

                text_id = wall.create_text(
                    canvas_x + 14,
                    canvas_y - 15,
                    text=text,
                    fill=self.INK,
                    font=(Fonts.FAMILY, 8, "bold"),
                    anchor="sw",
                    tags=("type_page_tooltip",),
                )

                bbox = wall.bbox(text_id)
                if bbox is None:
                    return

                x1, y1, x2, y2 = bbox
                pad_x = 8
                pad_y = 5

                # Reste dans la zone visible lorsque le pointeur est près
                # du bord droit ou du haut.
                view_left = wall.canvasx(0)
                view_top = wall.canvasy(0)
                view_right = wall.canvasx(wall.winfo_width())
                view_bottom = wall.canvasy(wall.winfo_height())

                shift_x = 0
                shift_y = 0

                if x2 + pad_x > view_right - 5:
                    shift_x = (view_right - 5) - (x2 + pad_x)
                if x1 - pad_x < view_left + 5:
                    shift_x = (view_left + 5) - (x1 - pad_x)

                if y1 - pad_y < view_top + 5:
                    shift_y = (view_top + 5) - (y1 - pad_y)
                if y2 + pad_y > view_bottom - 5:
                    shift_y = (view_bottom - 5) - (y2 + pad_y)

                if shift_x or shift_y:
                    wall.move(
                        text_id,
                        shift_x,
                        shift_y,
                    )
                    bbox = wall.bbox(text_id)
                    if bbox is None:
                        return
                    x1, y1, x2, y2 = bbox

                shadow = wall.create_rectangle(
                    x1 - pad_x + 2,
                    y1 - pad_y + 2,
                    x2 + pad_x + 2,
                    y2 + pad_y + 2,
                    fill="#D7DBD8",
                    outline="",
                    tags=("type_page_tooltip",),
                )

                bubble = wall.create_rectangle(
                    x1 - pad_x,
                    y1 - pad_y,
                    x2 + pad_x,
                    y2 + pad_y,
                    fill="#FFFDFC",
                    outline=accent,
                    width=1,
                    tags=("type_page_tooltip",),
                )

                wall.tag_lower(shadow, bubble)
                wall.tag_raise(text_id, bubble)

            wall._type_tooltip_after = wall.after(
                320,
                display,
            )

        def expand_items() -> list[dict]:
"""

OLD_BINDINGS = """            wall.tag_bind(
                tag,
                "<Enter>",
                lambda _evt: wall.configure(cursor="hand2"),
            )
            wall.tag_bind(
                tag,
                "<Leave>",
                lambda _evt: wall.configure(cursor="arrow"),
            )
"""

NEW_BINDINGS = """            def enter_page(
                event,
                current_item=item,
            ) -> None:
                wall.configure(cursor="hand2")
                show_type_tooltip(
                    event,
                    current_item,
                )

            def leave_page(_event) -> None:
                wall.configure(cursor="arrow")
                hide_type_tooltip()

            wall.tag_bind(
                tag,
                "<Enter>",
                enter_page,
            )
            wall.tag_bind(
                tag,
                "<Leave>",
                leave_page,
            )
"""


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if MARKER in original:
        print("BULLE_TYPE_PAGE_V10_DEJA_APPLIQUEE")
        return

    if REQUIRED not in original:
        fail(
            "la version Code type lisible V9 n'est pas détectée"
        )

    candidate = original

    if OLD_WALL_STATE not in candidate:
        fail("état du Canvas attendu introuvable")
    candidate = candidate.replace(
        OLD_WALL_STATE,
        NEW_WALL_STATE,
        1,
    )

    if OLD_HELPER_ANCHOR not in candidate:
        fail("point d'insertion de la bulle introuvable")
    candidate = candidate.replace(
        OLD_HELPER_ANCHOR,
        NEW_HELPERS,
        1,
    )

    if OLD_BINDINGS not in candidate:
        fail("liaisons de survol actuelles introuvables")
    candidate = candidate.replace(
        OLD_BINDINGS,
        NEW_BINDINGS,
        1,
    )

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = (
        backup_dir
        / f"document_view_avant_bulle_type_v10_{stamp}.py"
    )
    temp = TARGET.with_suffix(".bulle_type_v10.tmp")

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

    print("BULLE_TYPE_PAGE_V10_OK")
    print("Survol 0,32 s : affichage du code et du type en clair.")
    print("Exemple : TXT · Page de texte.")
    print("La bulle suit la palette de la page et disparaît à la sortie.")
    print("Aucun élément permanent supplémentaire n'est ajouté.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
