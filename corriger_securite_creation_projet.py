from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\PC\projet")
TARGET = ROOT / "src" / "core" / "project.py"
BACKUP_DIR = ROOT / "cache" / "correctifs"

if not TARGET.exists():
    raise SystemExit(f"Fichier introuvable : {TARGET}")

source = TARGET.read_text(encoding="utf-8")

needle = (
    "        self.name = name\n"
    "        self.project_type = self._normalize_project_type(project_type)\n"
    "        self.root = Path(folder) / name\n"
    "\n"
    "        now = datetime.now().isoformat()\n"
)

replacement = (
    "        target_root = Path(folder) / name\n"
    "        if target_root.exists():\n"
    "            raise FileExistsError(\n"
    "                f\"Un projet ou dossier nommé « {name} » existe déjà à cet emplacement.\"\n"
    "            )\n"
    "\n"
    "        self.name = name\n"
    "        self.project_type = self._normalize_project_type(project_type)\n"
    "        self.root = target_root\n"
    "\n"
    "        now = datetime.now().isoformat()\n"
)

if needle not in source:
    raise SystemExit(
        "CORRECTION_NON_APPLIQUEE : bloc de création attendu introuvable. "
        "Aucun fichier n'a été modifié."
    )

new_source = source.replace(needle, replacement, 1)

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"project_avant_securite_creation_{stamp}.py"
shutil.copy2(TARGET, backup)

TARGET.write_text(new_source, encoding="utf-8")

print("SECURITE_CREATION_PROJET_OK")
print(f"Fichier modifié : {TARGET}")
print(f"Sauvegarde : {backup}")
print("Un nouveau projet ne pourra plus réutiliser un dossier existant.")
