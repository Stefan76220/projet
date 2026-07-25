from pathlib import Path
import sys

# Ajoute la racine du projet au chemin de recherche Python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.library.book_models.book_model import BookModel
from src.library.book_models.book_model_library import BookModelLibrary


def main():

    library = BookModelLibrary()

    # Nettoyage
    library.clear()

    # Création d'un modèle
    model = BookModel(
        id="guide_plantes",
        name="Guide des plantes",
        description="Modèle de test"
    )

    # Ajout
    library.add(model)

    print("=== Avant sauvegarde ===")
    for m in library.all():
        print(m)

    # Sauvegarde
    library.save()

    # Vidage mémoire
    library.clear()

    print("\n=== Après clear() ===")
    print(library.all())

    # Rechargement
    library.load()

    print("\n=== Après load() ===")
    for m in library.all():
        print(m)


if __name__ == "__main__":
    main()