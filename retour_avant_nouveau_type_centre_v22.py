from pathlib import Path
import py_compile
import shutil

ROOT = Path(r"C:\Users\PC\projet")
BACKUP = Path(r"C:\Users\PC\projet\cache\correctifs\avant_nouveau_type_centre_v22_20260817_155734\app.py")
APP = ROOT / "src" / "gui_v3" / "app.py"

shutil.copy2(BACKUP, APP)
py_compile.compile(str(APP), doraise=True)
print("RETOUR_AVANT_NOUVEAU_TYPE_CENTRE_V22_OK")
print("Lance maintenant : python main_v3.py")
