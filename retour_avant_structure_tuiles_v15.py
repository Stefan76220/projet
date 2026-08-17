from pathlib import Path
import py_compile
import shutil

ROOT = Path(r"C:\Users\PC\projet")
APP_BACKUP = Path(r"C:\Users\PC\projet\cache\correctifs\avant_structure_tuiles_v15_20260817_135237\app.py")
APP = ROOT / "src" / "gui_v3" / "app.py"
ASSET = ROOT / r"assets/gui_v3/structure/structure_tile_reference_v15.png"

shutil.copy2(APP_BACKUP, APP)
if ASSET.exists():
    ASSET.unlink()
py_compile.compile(str(APP), doraise=True)
print("RETOUR_AVANT_STRUCTURE_TUILES_V15_OK")
print("Lance maintenant : python main_v3.py")
