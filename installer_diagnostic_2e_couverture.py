from pathlib import Path
from datetime import datetime
import shutil

ROOT = Path(r"C:\Users\PC\projet")
TARGET = ROOT / "src" / "gui" / "views" / "mockup_view.py"
BACKUP_DIR = ROOT / "cache" / "correctifs"

if not TARGET.exists():
    raise SystemExit(f"Fichier introuvable : {TARGET}")

source = TARGET.read_text(encoding="utf-8")

if "import traceback\n" not in source:
    marker = "import re\n"
    if marker not in source:
        raise SystemExit("DIAGNOSTIC_NON_APPLIQUE : zone d'imports introuvable.")
    source = source.replace(marker, marker + "import traceback\n", 1)

needle = (
    "    def _new_item_from_definition(\n"
    "        self,\n"
    "        definition: dict[str, Any],\n"
    "    ) -> dict[str, Any]:\n"
    "        return {\n"
)

replacement = (
    "    def _new_item_from_definition(\n"
    "        self,\n"
    "        definition: dict[str, Any],\n"
    "    ) -> dict[str, Any]:\n"
    "        page_type_debug = str(definition.get(\"type\", \"\"))\n"
    "        if page_type_debug == \"deuxieme_couverture\":\n"
    "            try:\n"
    "                diagnostic = Path(r\"C:\\\\Users\\\\PC\\\\projet\\\\cache\\\\diagnostic_maquettage_2e.txt\")\n"
    "                diagnostic.parent.mkdir(parents=True, exist_ok=True)\n"
    "                with diagnostic.open(\"a\", encoding=\"utf-8\") as debug_file:\n"
    "                    debug_file.write(\"\\n\" + \"=\" * 70 + \"\\n\")\n"
    "                    debug_file.write(\n"
    "                        f\"CREATION 2E COUVERTURE : {datetime.now().isoformat()}\\n\"\n"
    "                    )\n"
    "                    debug_file.write(\n"
    "                        f\"PROJET : {getattr(self.project, 'root', '')}\\n\"\n"
    "                    )\n"
    "                    debug_file.write(\"PILE D'APPEL :\\n\")\n"
    "                    debug_file.write(\"\".join(traceback.format_stack(limit=20)))\n"
    "            except Exception:\n"
    "                pass\n"
    "\n"
    "        return {\n"
)

if needle not in source:
    raise SystemExit(
        "DIAGNOSTIC_NON_APPLIQUE : _new_item_from_definition "
        "n'a pas la forme attendue. Aucun fichier modifié."
    )

source = source.replace(needle, replacement, 1)

BACKUP_DIR.mkdir(parents=True, exist_ok=True)
stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
backup = BACKUP_DIR / f"mockup_view_avant_diagnostic_2e_{stamp}.py"
shutil.copy2(TARGET, backup)

TARGET.write_text(source, encoding="utf-8")

log = ROOT / "cache" / "diagnostic_maquettage_2e.txt"
if log.exists():
    log.unlink()

print("DIAGNOSTIC_2E_INSTALLE_OK")
print(f"Fichier modifié : {TARGET}")
print(f"Sauvegarde : {backup}")
print(f"Journal : {log}")
print("Ferme complètement PageMaître puis relance-le.")
