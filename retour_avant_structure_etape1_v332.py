from __future__ import annotations
import json
import py_compile
import shutil
from pathlib import Path

ROOT = Path(r"C:\Users\PC\projet")
BACKUP = Path(r"C:\Users\PC\projet\cache\correctifs\avant_structure_etape1_v332_20260818_070845")
MANIFEST = Path(r"C:\Users\PC\projet\cache\correctifs\avant_structure_etape1_v332_20260818_070845\manifest.json")

manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
for rel, existed in manifest.items():
    target = ROOT / rel
    backup = BACKUP / rel
    if existed:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(backup, target)
    elif target.exists():
        target.unlink()

for rel in ("src/gui_v3/book_canvas.py", "src/gui_v3/page_visual_catalog.py"):
    py_compile.compile(str(ROOT / rel), doraise=True)

print("RETOUR_AVANT_STRUCTURE_ETAPE1_OK")
print("Lance maintenant : python main_v3.py")
