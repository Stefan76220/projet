print(">>> Début du test <<<")
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.library.page_types.page_type import PageType
from src.library.page_types.page_type_library import PageTypeLibrary


library = PageTypeLibrary()

library.clear()

page_type = PageType(
    id="text_page",
    name="Page de texte",
    description="Type de page utilisé pour le texte."
)

library.add(page_type)

print("Avant sauvegarde :")
print(library.all())

library.save()

library.clear()

print("\nAprès clear :")
print(library.all())

library.load()

print("\nAprès chargement :")
print(library.all())