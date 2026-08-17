from pathlib import Path
import py_compile
import shutil
ROOT=Path(r"C:\Users\PC\projet")
BACKUP=Path(r"C:\Users\PC\projet\cache\correctifs\avant_visionneuse_v11_20260816_195002\book_canvas.py")
TARGET=ROOT / "src" / "gui_v3" / "book_canvas.py"
if not BACKUP.exists():
    raise RuntimeError(f"Sauvegarde introuvable : {BACKUP}")
shutil.copy2(BACKUP,TARGET)
py_compile.compile(str(TARGET),doraise=True)
print("RETOUR_AVANT_VISIONNEUSE_V11_OK")
print("Lance maintenant : python main_v3.py")
