from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\PC\projet")
TARGET = ROOT / "src" / "core" / "project.py"
BACKUP_DIR = ROOT / "cache" / "correctifs"

if not TARGET.exists():
    raise SystemExit(f"Fichier introuvable : {TARGET}")

source = TARGET.read_text(encoding="utf-8")
lines = source.splitlines(keepends=True)

start = None
end = None

for i, line in enumerate(lines):
    if line.startswith("    def _ensure_mockup_file(self) -> None:"):
        start = i
        break

if start is None:
    raise SystemExit(
        "CORRECTION_NON_APPLIQUEE : fonction _ensure_mockup_file introuvable."
    )

for i in range(start + 1, len(lines)):
    if (
        lines[i].startswith("    @staticmethod")
        or lines[i].startswith("    @classmethod")
        or (
            lines[i].startswith("    def ")
            and not lines[i].startswith("        ")
        )
    ):
        end = i
        break

if end is None:
    raise SystemExit(
        "CORRECTION_NON_APPLIQUEE : fin de la fonction impossible à déterminer."
    )

newline = "\r\n" if "\r\n" in source else "\n"

replacement = [
    f"    def _ensure_mockup_file(self) -> None:{newline}",
    f"        # Le dossier est préparé ici ; MockupView crée premaquette.json.{newline}",
    f"        self.mockup_folder.mkdir({newline}",
    f"            parents=True,{newline}",
    f"            exist_ok=True,{newline}",
    f"        ){newline}",
    newline,
]

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"project_avant_initialisation_maquettage_{stamp}.py"
shutil.copy2(TARGET, backup)

new_lines = lines[:start] + replacement + lines[end:]
TARGET.write_text("".join(new_lines), encoding="utf-8", newline="")

print("INITIALISATION_MAQUETTAGE_CORRIGEE_OK")
print(f"Fichier modifié : {TARGET}")
print(f"Sauvegarde : {backup}")
print("Le projet ne crée plus l'ancien premaquette.json.")
print("Le bureau Maquettage initialisera lui-même les pages obligatoires.")
