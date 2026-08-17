from pathlib import Path
import py_compile
import shutil

ROOT = Path(r"C:\Users\PC\projet")
BACKUP = Path(r"C:\Users\PC\projet\cache\correctifs\avant_structure_commandes_v20_20260817_151330\book_canvas.py")
BOOK = ROOT / "src" / "gui_v3" / "book_canvas.py"

shutil.copy2(BACKUP, BOOK)
py_compile.compile(str(BOOK), doraise=True)
print("RETOUR_AVANT_STRUCTURE_COMMANDES_V20_OK")
print("Lance maintenant : python main_v3.py")
