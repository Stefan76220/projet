from pathlib import Path
import py_compile
import shutil

ROOT = Path(r"C:\Users\PC\projet")
BACKUP = Path(r"C:\Users\PC\projet\cache\correctifs\avant_B_zoom_surimpression_v8_20260816_191446\book_canvas.py")
TARGET = ROOT / "src" / "gui_v3" / "book_canvas.py"

if not BACKUP.exists():
    raise RuntimeError(f"Sauvegarde introuvable : {BACKUP}")
shutil.copy2(BACKUP, TARGET)
py_compile.compile(str(TARGET), doraise=True)
print("RETOUR_AVANT_ZOOM_SURIMPRESSION_V8_OK")
print("B restaure exactement dans son etat avant la V8.")
print("Lance maintenant : python main_v3.py")
