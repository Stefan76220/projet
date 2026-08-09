from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil

PROJECT = Path(r"C:\Users\PC\projet")
TARGET = PROJECT / "src" / "gui" / "layout" / "main_window.py"
MARKER = "OUVERTURE_MAXIMISEE_SANS_FLASH_V3"

NEW_RUN = '    def run(self) -> None:\n        # OUVERTURE_MAXIMISEE_SANS_FLASH_V3\n        # Windows calcule d\'abord la fenêtre, puis elle est maximisée\n        # avant d\'être rendue visible. Cela évite le petit format initial.\n        try:\n            self.root.update_idletasks()\n            self.root.state("zoomed")\n            self.root.deiconify()\n            self.root.lift()\n        except Exception:\n            # Repli sûr : si le gestionnaire de fenêtres refuse "zoomed",\n            # PageMaître reste utilisable dans sa géométrie normale.\n            try:\n                self.root.deiconify()\n            except Exception:\n                pass\n\n        self.root.mainloop()\n'


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier n'a été modifié.")


def replace_method(source: str, name: str, new_block: str) -> str:
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

    return "".join(lines[:start]) + new_block.rstrip() + "\n\n" + "".join(lines[end:])


def main() -> None:
    if not TARGET.is_file():
        fail(f"fichier introuvable : {TARGET}")

    original = TARGET.read_text(encoding="utf-8")

    if MARKER in original:
        print("OUVERTURE_MAXIMISEE_SANS_FLASH_DEJA_APPLIQUEE")
        return

    anchor = "        self.root = ctk.CTk()\n"
    if anchor not in original:
        fail("création de la fenêtre principale introuvable")

    candidate = original.replace(
        anchor,
        anchor
        + f"        # {MARKER}\n"
        + "        # La fenêtre n'est affichée qu'une fois réellement maximisée.\n"
        + "        self.root.withdraw()\n",
        1,
    )

    candidate = replace_method(candidate, "run", NEW_RUN)

    try:
        compile(candidate, str(TARGET), "exec")
    except Exception as exc:
        fail(f"la version préparée ne compile pas : {exc}")

    backup_dir = PROJECT / "cache" / "correctifs"
    backup_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = backup_dir / f"main_window_avant_maximisation_sans_flash_{stamp}.py"
    temp = TARGET.with_suffix(".max_sans_flash.tmp")

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

    print("OUVERTURE_MAXIMISEE_SANS_FLASH_OK")
    print(f"Fichier modifié : {TARGET}")
    print("PageMaître s'ouvrira masqué puis apparaîtra directement maximisé.")
    print("La barre Windows reste visible.")
    print(f"Sauvegarde : {backup}")


if __name__ == "__main__":
    main()
