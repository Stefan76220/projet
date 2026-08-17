from pathlib import Path
import py_compile
import shutil

ROOT = Path(r"C:\Users\PC\projet")
BACKUP = Path(r"C:\Users\PC\projet\cache\correctifs\avant_briques_pages_auto_v18_20260817_142351\app.py")
APP = ROOT / "src" / "gui_v3" / "app.py"

shutil.copy2(BACKUP, APP)
py_compile.compile(str(APP), doraise=True)
print("RETOUR_AVANT_BRIQUES_PAGES_AUTO_V18_OK")
print("Lance maintenant : python main_v3.py")
