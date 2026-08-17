from pathlib import Path
import py_compile
import shutil

ROOT = Path(r"C:\Users\PC\projet")
BACKUP = Path(r"C:\Users\PC\projet\cache\correctifs\avant_structure_v24_20260817_165837\book_canvas.py")
BOOK = ROOT / "src" / "gui_v3" / "book_canvas.py"

shutil.copy2(BACKUP, BOOK)
py_compile.compile(str(BOOK), doraise=True)
print("RETOUR_AVANT_STRUCTURE_V24_OK")
print("Lance maintenant : python main_v3.py")
