from pathlib import Path
import py_compile
import shutil

ROOT = Path(r"C:\Users\PC\projet")
BOOK_BACKUP = Path(r"C:\Users\PC\projet\cache\correctifs\avant_structure_v29_20260817_193255\book_canvas.py")
IMAGE_BACKUP_DIR = Path(r"C:\Users\PC\projet\cache\correctifs\avant_structure_v29_20260817_193255\page_thumbnails")
THUMBS = ROOT / "assets" / "page_thumbnails"
BOOK = ROOT / "src" / "gui_v3" / "book_canvas.py"

shutil.copy2(BOOK_BACKUP, BOOK)
THUMBS.mkdir(parents=True, exist_ok=True)

manifest = IMAGE_BACKUP_DIR / "_manifest.txt"
if manifest.exists():
    for line in manifest.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        name, existed = line.split("|", 1)
        target = THUMBS / name
        backup = IMAGE_BACKUP_DIR / name
        if existed == "1":
            if backup.exists():
                shutil.copy2(backup, target)
        else:
            if target.exists():
                target.unlink()

py_compile.compile(str(BOOK), doraise=True)
print("RETOUR_AVANT_STRUCTURE_V29_OK")
print("Lance maintenant : python main_v3.py")
