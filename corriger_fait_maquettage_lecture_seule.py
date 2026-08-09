from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import re
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "views" / "mockup_view.py"


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def patch_done_checkbox(source: str) -> str:
    pattern = re.compile(
        r"(?ms)^        done_check = "
        r"(?P<widget>tk\.Checkbutton|ctk\.CTkCheckBox)\(\n"
        r".*?^        \)\n"
        r"        done_check\.grid\("
    )
    match = pattern.search(source)
    if match is None:
        if "FAIT_LECTURE_SEULE" in source:
            return source
        fail("case « Fait » introuvable dans _create_sequence_row")

    block = match.group(0)

    block = re.sub(
        r"(?ms)^            command=lambda "
        r"current=item_id, variable=done_var: \(\n"
        r"                self\._set_done_by_id\(current, variable\.get\(\)\)\n"
        r"            \),\n",
        "",
        block,
    )

    block = block.replace('            cursor="hand2",\n', '            cursor="arrow",\n')

    if '            state="disabled",\n' not in block:
        final_close = "\n        )\n        done_check.grid("
        if final_close not in block:
            fail("fin du bloc « Fait » introuvable")
        block = block.replace(
            final_close,
            '            state="disabled",\n'
            '            # FAIT_LECTURE_SEULE\n'
            + final_close,
            1,
        )

    return source[:match.start()] + block + source[match.end():]


def patch_refresh_state(source: str) -> str:
    old = (
        '            "disabled" if automatic_blank else "normal",\n'
        '            "disabled" if automatic_blank or required else "normal",\n'
    )
    new = (
        '            "disabled",  # Fait : état automatique, jamais manuel\n'
        '            "disabled" if automatic_blank or required else "normal",\n'
    )
    if old in source:
        return source.replace(old, new, 1)
    if '"disabled",  # Fait : état automatique, jamais manuel' in source:
        return source
    return source


def add_legacy_cleanup(source: str) -> str:
    call = "        self._clear_legacy_manual_done_flags()\n"
    load_line = "        self.data: dict[str, Any] = self._load_data()\n"

    if call not in source:
        if load_line not in source:
            fail("chargement des données de maquettage introuvable")
        source = source.replace(load_line, load_line + call, 1)

    method_marker = "    def _clear_legacy_manual_done_flags(self) -> None:\n"
    if method_marker in source:
        return source

    insertion_point = source.find("    def _run_silent_structure_check(")
    if insertion_point < 0:
        insertion_point = source.find("    def _items(")
    if insertion_point < 0:
        fail("point d'insertion du nettoyage des anciens états introuvable")

    method = '''    def _clear_legacy_manual_done_flags(self) -> None:\n        """Supprime les anciens « Fait » cochés manuellement.\n\n        À l'avenir, seul le Bureau de conception pourra fournir un état\n        marqué done_source='conception'.\n        """\n        changed = False\n        for item in self._items():\n            if str(item.get("done_source", "")).casefold() == "conception":\n                continue\n            if bool(item.get("done", False)):\n                item["done"] = False\n                changed = True\n\n        if changed:\n            self.data["updated_at"] = datetime.now().isoformat()\n            self._write_json(self._mockup_file(), self.data)\n\n'''
    return source[:insertion_point] + method + source[insertion_point:]


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")
    source = original

    source = patch_done_checkbox(source)
    source = patch_refresh_state(source)
    source = add_legacy_cleanup(source)

    if source == original:
        print("FAIT_MAQUETTAGE_DEJA_CORRECT")
        return

    compile(source, str(TARGET), "exec")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"mockup_view_avant_fait_auto_{stamp}.py"
    shutil.copy2(TARGET, backup)

    try:
        TARGET.write_text(source, encoding="utf-8")
        py_compile.compile(str(TARGET), doraise=True)
    except Exception as exc:
        shutil.copy2(backup, TARGET)
        fail(f"correction annulée automatiquement : {exc}")

    pycache = TARGET.parent / "__pycache__"
    if pycache.exists():
        shutil.rmtree(pycache, ignore_errors=True)

    print("FAIT_MAQUETTAGE_LECTURE_SEULE_OK")
    print("Fichier modifié : src/gui/views/mockup_view.py")
    print(f"Sauvegarde : {backup}")
    print("Les anciens états « Fait » cochés manuellement seront nettoyés à la prochaine ouverture.")
    print("Ferme complètement PageMaître puis relance-le.")


if __name__ == "__main__":
    main()
