from pathlib import Path
import shutil
target = Path('C:\\Users\\PC\\Documents\\TomeLinea\\Projets\\TEST STRUCTURE — PAS À PAS')
ref = target / 'maquettage' / 'premaquette_REFERENCE.json'
cur = target / 'maquettage' / 'premaquette.json'
if not ref.exists(): raise SystemExit('Référence de test introuvable.')
shutil.copy2(ref, cur)
print('TEST_STRUCTURE_REINITIALISE')
