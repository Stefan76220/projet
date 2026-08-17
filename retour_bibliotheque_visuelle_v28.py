from pathlib import Path
import shutil

ROOT = Path(r"C:\Users\PC\projet")
BACKUP_DIR = Path(r"C:\Users\PC\projet\cache\correctifs\avant_bibliotheque_visuelle_v28_20260817_192008")
THUMBS = ROOT / "assets" / "page_thumbnails"

if not BACKUP_DIR.exists():
    raise RuntimeError("Sauvegarde introuvable : " + str(BACKUP_DIR))

THUMBS.mkdir(parents=True, exist_ok=True)
for src in BACKUP_DIR.glob("*.png"):
    shutil.copy2(src, THUMBS / src.name)

print("RETOUR_BIBLIOTHEQUE_VISUELLE_V28_OK")
print("Lance maintenant : python main_v3.py")
