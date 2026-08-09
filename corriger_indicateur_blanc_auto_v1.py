from __future__ import annotations

from datetime import datetime
from pathlib import Path
import hashlib
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"
MARKER = "INDICATEUR_DEPOT_BLOCS_AUTO_V1"
EXPECTED_METHOD_HASH = '5f4dd40f282b38a7c4876a6fed6d7f62357b37b567a6cfa9ebf3ff9086356fc2'
NEW_METHOD = '    def _show_page_drop_indicator(\n        self,\n        item_id: str,\n        pointer_y: int,\n    ) -> None:\n        """Affiche la ligne sur la frontière réelle entre deux blocs de pages."""\n        plan = self._page_drop_plan(item_id, pointer_y)\n        overlay = self._root\n        if plan is None or overlay is None:\n            self._hide_page_drop_indicator()\n            return\n\n        # INDICATEUR_DEPOT_BLOCS_AUTO_V1\n        # Le calcul logique du déplacement reste strictement inchangé.\n        # Ici, on corrige uniquement l\'endroit où la ligne est dessinée :\n        # une page et ses blancs automatiques associés forment un même bloc\n        # visuel. La ligne ne peut donc plus traverser un blanc automatique.\n        dragged_items, remaining_regular, insertion_index = plan\n        items = self._items()\n\n        dragged_ids = {\n            str(dragged.get("id", ""))\n            for dragged in dragged_items\n        }\n\n        previous_item = None\n        next_item = None\n        if insertion_index > 0:\n            previous_item = remaining_regular[insertion_index - 1]\n        else:\n            start_items = [\n                item\n                for item in items\n                if str(item.get("id", "")) not in dragged_ids\n                and str(item.get("type", "")) in self.START_STRUCTURAL_TYPES\n            ]\n            if start_items:\n                previous_item = start_items[-1]\n\n        if insertion_index < len(remaining_regular):\n            next_item = remaining_regular[insertion_index]\n        else:\n            end_items = [\n                item\n                for item in items\n                if str(item.get("id", "")) not in dragged_ids\n                and str(item.get("type", "")) in self.END_STRUCTURAL_TYPES\n            ]\n            if end_items:\n                next_item = end_items[0]\n\n        if previous_item is None or next_item is None:\n            self._hide_page_drop_indicator()\n            return\n\n        def block_rows(page_item: dict[str, Any]) -> list[Any]:\n            """Retourne la page et ses blancs automatiques réellement associés."""\n            page_id = str(page_item.get("id", ""))\n            rows: list[Any] = []\n\n            page_record = self._sequence_row_widgets.get(page_id)\n            if page_record is not None and page_record.get("row") is not None:\n                rows.append(page_record["row"])\n\n            for candidate in items:\n                if not bool(candidate.get("automatic_recto_verso", False)):\n                    continue\n                if str(candidate.get("recto_target_id", "")) != page_id:\n                    continue\n                record = self._sequence_row_widgets.get(\n                    str(candidate.get("id", ""))\n                )\n                if record is not None and record.get("row") is not None:\n                    rows.append(record["row"])\n\n            return rows\n\n        def block_bounds(\n            page_item: dict[str, Any],\n        ) -> tuple[Any, Any, int, int] | None:\n            rows = block_rows(page_item)\n            if not rows:\n                return None\n            try:\n                upper = min(rows, key=lambda row: row.winfo_rooty())\n                lower = max(\n                    rows,\n                    key=lambda row: row.winfo_rooty() + row.winfo_height(),\n                )\n                top = min(row.winfo_rooty() for row in rows)\n                bottom = max(\n                    row.winfo_rooty() + row.winfo_height()\n                    for row in rows\n                )\n            except Exception:\n                return None\n            return upper, lower, int(top), int(bottom)\n\n        previous_bounds = block_bounds(previous_item)\n        next_bounds = block_bounds(next_item)\n        if previous_bounds is None or next_bounds is None:\n            self._hide_page_drop_indicator()\n            return\n\n        previous_upper, previous_lower, _, previous_bottom = previous_bounds\n        next_upper, next_lower, next_top, _ = next_bounds\n\n        # Si le bloc source se trouve encore entre les deux blocs cibles,\n        # son bord supérieur/inférieur devient la frontière affichée.\n        source_blocks = []\n        for dragged_item in dragged_items:\n            bounds = block_bounds(dragged_item)\n            if bounds is not None:\n                source_blocks.append(bounds)\n\n        source_bounds = None\n        if source_blocks:\n            try:\n                source_bounds = min(\n                    source_blocks,\n                    key=lambda bounds: abs(\n                        ((bounds[2] + bounds[3]) / 2) - pointer_y\n                    ),\n                )\n            except Exception:\n                source_bounds = source_blocks[0]\n\n        marker_height_px = 4\n        try:\n            overlay.update_idletasks()\n\n            upper_row = previous_lower\n            lower_row = next_upper\n\n            if source_bounds is not None:\n                source_upper, source_lower, source_top, source_bottom = (\n                    source_bounds\n                )\n                if (\n                    previous_bottom <= source_top\n                    and source_bottom <= next_top\n                ):\n                    source_middle = (source_top + source_bottom) / 2\n                    if pointer_y < source_middle:\n                        lower_row = source_upper\n                        next_top = source_top\n                    else:\n                        upper_row = source_lower\n                        previous_bottom = source_bottom\n\n            gap_center = (previous_bottom + next_top) / 2\n            marker_root_y = gap_center - marker_height_px / 2\n\n            left_px = max(\n                upper_row.winfo_rootx(),\n                lower_row.winfo_rootx(),\n            )\n            right_px = min(\n                upper_row.winfo_rootx() + upper_row.winfo_width(),\n                lower_row.winfo_rootx() + lower_row.winfo_width(),\n            )\n            marker_width_px = max(80, right_px - left_px)\n\n            local_x, local_y, marker_width, marker_height = (\n                self._screen_geometry_for_place(\n                    overlay,\n                    left_px,\n                    marker_root_y,\n                    marker_width_px,\n                    marker_height_px,\n                )\n            )\n        except Exception:\n            self._hide_page_drop_indicator()\n            return\n\n        if self._page_drop_indicator is None:\n            self._page_drop_indicator = ctk.CTkFrame(\n                overlay,\n                width=marker_width,\n                height=marker_height,\n                fg_color=self.CORAL,\n                corner_radius=2,\n                border_width=1,\n                border_color=self.INK,\n            )\n\n        try:\n            self._page_drop_indicator.configure(\n                width=marker_width,\n                height=marker_height,\n            )\n            self._page_drop_indicator.place(x=local_x, y=local_y)\n            self._page_drop_indicator.lift()\n        except Exception:\n            self._hide_page_drop_indicator()\n'


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def get_method(source: str, name: str) -> str:
    lines = source.splitlines(keepends=True)
    start = None
    for i, line in enumerate(lines):
        if line.startswith(f"    def {name}("):
            start = i
            break
    if start is None:
        fail(f"méthode {name} introuvable")
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("    def ") or lines[i].startswith("    @"):
            end = i
            break
    return "".join(lines[start:end])


def replace_method(source: str, name: str, block: str) -> str:
    old = get_method(source, name)
    return source.replace(old, block.rstrip() + "\n\n", 1)


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if MARKER in original:
        print("INDICATEUR_DEPOT_BLOCS_AUTO_DEJA_APPLIQUE")
        return

    current_method = get_method(original, "_show_page_drop_indicator")
    current_hash = hashlib.sha256(
        current_method.encode("utf-8")
    ).hexdigest()

    if current_hash != EXPECTED_METHOD_HASH:
        fail(
            "la méthode de l'indicateur de dépôt a changé depuis la version "
            "transmise. Le correctif s'arrête par sécurité."
        )

    candidate = replace_method(
        original,
        "_show_page_drop_indicator",
        NEW_METHOD,
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
        / f"mockup_view_avant_indicateur_blocs_auto_{stamp}.py"
    )
    temp = TARGET.with_suffix(".indicateur_auto.tmp")

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

    print("INDICATEUR_DEPOT_BLOCS_AUTO_OK")
    print("La logique de déplacement et le recto-verso sont inchangés.")
    print("La ligne suit maintenant le bord du bloc page + blanc(s) auto.")
    print("Elle ne doit plus traverser une page blanche automatique.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
