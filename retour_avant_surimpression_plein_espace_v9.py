from pathlib import Path
import py_compile
import shutil

ROOT = Path(r"C:\Users\PC\projet")
BACKUP = Path(r"C:\Users\PC\projet\cache\correctifs\avant_B_surimpression_plein_espace_v9_20260816_192324\book_canvas.py")
TARGET = ROOT / "src" / "gui_v3" / "book_canvas.py"

if not BACKUP.exists():
    raise RuntimeError(f"Sauvegarde introuvable : {BACKUP}")
shutil.copy2(BACKUP, TARGET)
py_compile.compile(str(TARGET), doraise=True)
print("RETOUR_AVANT_SURIMPRESSION_PLEIN_ESPACE_V9_OK")
print("B restaure exactement dans son etat avant la V9.")
print("Lance maintenant : python main_v3.py")
