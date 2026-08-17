from pathlib import Path
import py_compile
import shutil

ROOT = Path(r"C:\Users\PC\projet")
BACKUP = Path(r"C:\Users\PC\projet\cache\correctifs\avant_visionneuse_v15_20260816_201028\book_canvas.py")
TARGET = ROOT / "src" / "gui_v3" / "book_canvas.py"
shutil.copy2(BACKUP, TARGET)
py_compile.compile(str(TARGET), doraise=True)
print("RETOUR_AVANT_VISIONNEUSE_V15_OK")
print("Lance maintenant : python main_v3.py")
