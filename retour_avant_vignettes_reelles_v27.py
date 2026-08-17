from pathlib import Path
import shutil

ROOT = Path(r"C:\Users\PC\projet")
BACKUP_DIR = Path(r"C:\Users\PC\projet\cache\correctifs\avant_vignettes_reelles_v27_20260817_190313")
TARGET_DIR = ROOT / "assets" / "page_thumbnails"

if not BACKUP_DIR.exists():
    raise RuntimeError("Sauvegarde introuvable : " + str(BACKUP_DIR))

TARGET_DIR.mkdir(parents=True, exist_ok=True)
for src in BACKUP_DIR.glob("*.png"):
    shutil.copy2(src, TARGET_DIR / src.name)

print("RETOUR_AVANT_VIGNETTES_REELLES_V27_OK")
print("Lance maintenant : python main_v3.py")
