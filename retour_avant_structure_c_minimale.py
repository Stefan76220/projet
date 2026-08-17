from pathlib import Path
import py_compile
import shutil
ROOT = Path(r"C:\Users\PC\projet")
BACKUP = Path(r"C:\Users\PC\projet\cache\correctifs\avant_structure_c_minimale_20260816_212308\app.py")
TARGET = ROOT / "src" / "gui_v3" / "app.py"
shutil.copy2(BACKUP, TARGET)
py_compile.compile(str(TARGET), doraise=True)
print("RETOUR_AVANT_STRUCTURE_C_MINIMALE_OK")
print("Lance maintenant : python main_v3.py")
