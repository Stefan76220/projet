from pathlib import Path
import py_compile
import shutil

ROOT = Path(r"C:\Users\PC\projet")
BACKUP = Path(r"C:\Users\PC\projet\cache\correctifs\avant_suppression_zoom_b_v13_20260816_195821\book_canvas.py")
TARGET = ROOT / "src" / "gui_v3" / "book_canvas.py"
shutil.copy2(BACKUP, TARGET)
py_compile.compile(str(TARGET), doraise=True)
print("RETOUR_AVANT_SUPPRESSION_ZOOM_B_V13_OK")
print("Lance maintenant : python main_v3.py")
