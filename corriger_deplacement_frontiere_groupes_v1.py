from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"
REQUIRED_MARKER = "RUBAN_COULEURS_GROUPES_V1"
NEW_MARKER = "DEPLACEMENT_FRONTIERE_GROUPES_V1"

NEW_METHOD = '    def _move_item(self, index: int, delta: int) -> None:\n        items = self._items()\n        if not 0 <= index < len(items):\n            return\n        if not self._can_move_item(index, delta):\n            return\n\n        current = items[index]\n        current_id = str(current.get("id", ""))\n        current_group = self._plan_group_id(current)\n\n        base_items = [\n            item\n            for item in items\n            if not bool(item.get("automatic_recto_verso", False))\n        ]\n        base_index = next(\n            (\n                position\n                for position, item in enumerate(base_items)\n                if str(item.get("id", "")) == current_id\n            ),\n            None,\n        )\n        if base_index is None:\n            return\n\n        target_index = base_index + delta\n        if not 0 <= target_index < len(base_items):\n            return\n\n        target = base_items[target_index]\n        target_type = str(target.get("type", ""))\n        target_group = self._plan_group_id(target)\n\n        self._record_history()\n\n        if target_group != current_group:\n            # Franchir une frontière de groupe ne doit PAS sauter la première\n            # ou la dernière page du groupe voisin :\n            # - Descendre => la page devient la première du groupe suivant.\n            # - Monter    => la page devient la dernière du groupe précédent.\n            # L\'ordre physique ne change donc pas ici ; seule l\'appartenance\n            # au groupe change.\n            current["plan_group"] = target_group\n        elif self._is_locked_structural_type(target_type):\n            # Même groupe mais borne structurelle verrouillée : pas d\'échange.\n            return\n        else:\n            # À l\'intérieur d\'un même groupe, Monter/Descendre reste un échange\n            # classique avec la page voisine.\n            base_items[base_index], base_items[target_index] = (\n                base_items[target_index],\n                base_items[base_index],\n            )\n\n        self._items()[:] = base_items\n        self._enforce_structural_order()\n        self._save_data()\n        self._refresh_sequence()'


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def replace_method(source: str, name: str, new_block: str) -> str:
    lines = source.splitlines(keepends=True)
    start = None
    for index, line in enumerate(lines):
        if line.startswith(f"    def {name}("):
            start = index
            break
    if start is None:
        fail(f"méthode {name} introuvable")

    end = len(lines)
    for index in range(start + 1, len(lines)):
        line = lines[index]
        if line.startswith("    def ") or line.startswith("    @"):
            end = index
            break

    return "".join(lines[:start]) + new_block.rstrip() + "\n\n" + "".join(lines[end:])


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if NEW_MARKER in original:
        print("DEPLACEMENT_FRONTIERE_GROUPES_DEJA_APPLIQUE")
        return

    if REQUIRED_MARKER not in original:
        fail(
            "la version actuelle du ruban harmonisé n'est pas détectée. "
            "Par sécurité, la correction est refusée."
        )

    candidate = replace_method(original, "_move_item", NEW_METHOD)
    candidate = candidate.replace(
        "# RUBAN_COULEURS_GROUPES_V1",
        "# RUBAN_COULEURS_GROUPES_V1\n        # DEPLACEMENT_FRONTIERE_GROUPES_V1",
        1,
    )

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"mockup_view_avant_frontiere_groupes_{stamp}.py"
    temporary = TARGET.with_suffix(".frontiere_groupes.tmp")

    try:
        temporary.write_text(candidate, encoding="utf-8")
        py_compile.compile(str(temporary), doraise=True)
        shutil.copy2(TARGET, backup)
        temporary.replace(TARGET)
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as exc:
        try:
            temporary.unlink(missing_ok=True)
        except Exception:
            pass
        if backup.exists():
            shutil.copy2(backup, TARGET)
        fail(f"installation annulée automatiquement : {exc}")

    print("DEPLACEMENT_FRONTIERE_GROUPES_OK")
    print("Fichier modifié : src/gui/views/mockup_view.py")
    print(f"Sauvegarde : {backup}")
    print("Descendre vers un autre groupe : devient première page du groupe.")
    print("Monter vers un autre groupe : devient dernière page du groupe.")
    print("Dans un même groupe : déplacement d'une position comme avant.")
    print("Le ruban supérieur n'est pas modifié.")
    print("Ferme complètement PageMaître puis relance-le.")


if __name__ == "__main__":
    main()
