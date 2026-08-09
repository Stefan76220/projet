from pathlib import Path
from datetime import datetime
import shutil
import re

ROOT = Path(r"C:\Users\PC\projet")
TARGET = ROOT / "src" / "core" / "project.py"
BACKUP_DIR = ROOT / "cache" / "correctifs"

if not TARGET.exists():
    raise SystemExit(f"Fichier introuvable : {TARGET}")

source = TARGET.read_text(encoding="utf-8")

pattern = re.compile(
    r'(?ms)^    def _ensure_mockup_file\(self\) -> None:\n'
    r'        self\.mockup_folder\.mkdir\(\n'
    r'            parents=True,\n'
    r'            exist_ok=True,\n'
    r'        \)\n\n'
    r'        if self\.mockup_file\.exists\(\):\n'
    r'            return\n\n'
    r'        self\.save_mockup\(\n'
    r'            self\._default_mockup_data\(\)\n'
    r'        \)\n'
)

replacement = (
    "    def _ensure_mockup_file(self) -> None:\n"
    "        # Le bureau Maquettage initialise lui-même premaquette.json.\n"
    "        self.mockup_folder.mkdir(\n"
    "            parents=True,\n"
    "            exist_ok=True,\n"
    "        )\n"
)

new_source, count = pattern.subn(replacement, source, count=1)

if count != 1:
    raise SystemExit(
        "CORRECTION_NON_APPLIQUEE : la fonction _ensure_mockup_file "
        "n'a pas la forme attendue. Aucun fichier n'a été modifié."
    )

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"project_avant_initialisation_maquettage_{stamp}.py"
shutil.copy2(TARGET, backup)

TARGET.write_text(new_source, encoding="utf-8")

print("INITIALISATION_MAQUETTAGE_CORRIGEE_OK")
print(f"Fichier modifié : {TARGET.relative_to(ROOT)}")
print(f"Sauvegarde : {backup}")
print("Nouveau projet : premaquette.json sera créé par le bureau Maquettage.")
print("Les projets existants restent inchangés.")
