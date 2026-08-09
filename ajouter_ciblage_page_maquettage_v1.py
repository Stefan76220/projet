from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"

MARKER = "def focus_page("
ANCHOR = "    def _create_header(self, parent) -> ctk.CTkFrame:\n"
INSERT = '\n    def focus_page(\n        self,\n        item_id: str,\n        occurrence: int = 1,\n    ) -> bool:\n        """Sélectionne une page du Maquettage et la place au centre de la vue.\n\n        Cette méthode publique est destinée au Centre de régulation et à la\n        future fenêtre Visualisation. Elle ne reconstruit pas le Maquettage :\n        elle s\'appuie sur la ligne déjà rendue et sur son identifiant stable.\n\n        ``occurrence`` est conservé pour les types présents plusieurs fois.\n        Aujourd\'hui le Maquettage les regroupe encore dans une même ligne ;\n        le paramètre prépare donc le ciblage individuel futur sans casser\n        l\'interface actuelle.\n        """\n        page_id = str(item_id or "").strip()\n        if not page_id:\n            return False\n\n        item = next(\n            (\n                candidate\n                for candidate in self._items()\n                if str(candidate.get("id", "")) == page_id\n            ),\n            None,\n        )\n        if item is None:\n            return False\n\n        try:\n            occurrence_value = max(1, int(occurrence))\n        except (TypeError, ValueError):\n            occurrence_value = 1\n\n        self._external_focus_occurrence = occurrence_value\n        self._selected_page_ids = {page_id}\n        self._selection_anchor_id = page_id\n\n        self._refresh_selection_visuals()\n        self._update_selection_controls()\n\n        frame = self._sequence_frame\n        if frame is None:\n            return True\n\n        # Le défilement est différé : Tk doit avoir calculé la géométrie\n        # exacte des cartes avant de pouvoir centrer la cible.\n        try:\n            frame.after_idle(\n                lambda selected=page_id: self._scroll_to_page_id(selected)\n            )\n        except tk.TclError:\n            pass\n\n        return True\n\n    def _scroll_to_page_id(self, item_id: str) -> None:\n        """Centre dans le Plan du livre la ligne correspondant à ``item_id``."""\n        frame = self._sequence_frame\n        record = self._sequence_row_widgets.get(str(item_id))\n\n        if frame is None or record is None:\n            return\n\n        row = record.get("row")\n        if row is None:\n            return\n\n        try:\n            frame.update_idletasks()\n            row.update_idletasks()\n\n            canvas = getattr(frame, "_parent_canvas", None)\n            if canvas is None:\n                return\n\n            viewport_height = max(1, int(canvas.winfo_height()))\n            row_y = int(row.winfo_y())\n            row_height = max(1, int(row.winfo_height()))\n\n            # La frame intérieure porte toutes les cartes.\n            content_height = max(\n                int(frame.winfo_height()),\n                int(frame.winfo_reqheight()),\n                row_y + row_height,\n            )\n\n            maximum_scroll = max(0, content_height - viewport_height)\n            if maximum_scroll <= 0:\n                canvas.yview_moveto(0.0)\n                return\n\n            target_top = (\n                row_y\n                - max(0, (viewport_height - row_height) // 2)\n            )\n            fraction = max(\n                0.0,\n                min(1.0, target_top / maximum_scroll),\n            )\n            canvas.yview_moveto(fraction)\n\n            # Une seconde passe stabilise le centrage sur certains facteurs\n            # d\'échelle Windows/CustomTkinter.\n            canvas.update_idletasks()\n        except (tk.TclError, TypeError, ValueError):\n            return\n'


def fail(message: str) -> None:
    raise SystemExit(
        f"ERREUR : {message}\nAucun fichier n'a été modifié."
    )


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if MARKER in original:
        print("CIBLAGE_PAGE_MAQUETTAGE_V1_DEJA_APPLIQUE")
        return

    if ANCHOR not in original:
        fail("point d'insertion après show() introuvable")

    if "_sequence_row_widgets" not in original:
        fail("registre des lignes du Plan du livre introuvable")

    candidate = original.replace(
        ANCHOR,
        INSERT.rstrip() + "\n\n" + ANCHOR,
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
        / f"mockup_view_avant_ciblage_page_{stamp}.py"
    )
    temp = TARGET.with_suffix(".ciblage_page.tmp")

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

    print("CIBLAGE_PAGE_MAQUETTAGE_V1_OK")
    print("MockupView expose maintenant focus_page(item_id, occurrence=1).")
    print("La page ciblée est sélectionnée et centrée dans le Plan du livre.")
    print("Aucun comportement existant du Maquettage n'est modifié.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
