from pathlib import Path
import os, sys
ROOT = Path('C:\\Users\\PC\\projet')
TARGET = Path('C:\\Users\\PC\\Documents\\TomeLinea\\Projets\\LABO RÈGLES STRUCTURE')
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))
from src.gui_v3.app import TomeLineaV3
app = TomeLineaV3()
project = app.project_manager.open_project(str(TARGET))
app._remember_recent(project)
app.show_workspace(project)
app.active_tab = 'structure'
try:
    app._set_workspace_tab('structure')
except Exception:
    pass
app.mainloop()
