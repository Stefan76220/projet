from pathlib import Path
import py_compile
import shutil

ROOT = Path(r"C:\Users\PC\projet")
APP_BACKUP = Path(r"C:\Users\PC\projet\cache\correctifs\avant_structure_page_auto_v251_20260817_180126\app.py")
BOOK_BACKUP = Path(r"C:\Users\PC\projet\cache\correctifs\avant_structure_page_auto_v251_20260817_180126\book_canvas.py")
APP = ROOT / "src" / "gui_v3" / "app.py"
BOOK = ROOT / "src" / "gui_v3" / "book_canvas.py"

shutil.copy2(APP_BACKUP, APP)
shutil.copy2(BOOK_BACKUP, BOOK)
py_compile.compile(str(APP), doraise=True)
py_compile.compile(str(BOOK), doraise=True)
print("RETOUR_AVANT_STRUCTURE_V251_OK")
print("Lance maintenant : python main_v3.py")
