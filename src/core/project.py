from pathlib import Path
import json
from datetime import datetime


class Project:

    VERSION = "1.0"

    def __init__(self):

        self.name = ""
        self.format = "A5"
        self.book_model_id = ""
        self.root = None

        # État du projet en mémoire
        self.documents = []
        self.ressources = []

    def create(self, folder: str, name: str):

        self.name = name

        root = Path(folder) / name
        self.root = root

        (root / "documents").mkdir(parents=True, exist_ok=True)

        (root / "ressources").mkdir(exist_ok=True)
        (root / "ressources" / "images").mkdir(exist_ok=True)
        (root / "ressources" / "illustrations").mkdir(exist_ok=True)
        (root / "ressources" / "icones").mkdir(exist_ok=True)
        (root / "ressources" / "logos").mkdir(exist_ok=True)

        (root / "modeles").mkdir(exist_ok=True)

        (root / "exports").mkdir(exist_ok=True)

        (root / "cache").mkdir(exist_ok=True)

        self.documents = []
        self.ressources = []

        project_data = {
            "nom": self.name,
            "version": self.VERSION,
            "format": self.format,
            "book_model": self.book_model_id,
            "date_creation": datetime.now().isoformat(),
            "date_modification": datetime.now().isoformat(),
            "documents": self.documents,
            "ressources": self.ressources
        }

        with open(
            root / "projet.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                project_data,
                f,
                indent=4,
                ensure_ascii=False
            )

        return root

    def load(self, project_folder: str):

        # ----------------------------
        # Diagnostic temporaire
        # ----------------------------

        print("\n===== DIAGNOSTIC OUVERTURE PROJET =====")
        print("Dossier reçu :", project_folder)

        root = Path(project_folder)
        project_file = root / "projet.json"

        print("Recherche :", project_file)
        print("Existe :", project_file.exists())
        print("=======================================\n")

        # ----------------------------

        if not project_file.exists():
            raise FileNotFoundError(
                "Le fichier projet.json est introuvable."
            )

        with open(
            project_file,
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        self.root = root
        self.name = data.get("nom", "")
        self.format = data.get("format", "A5")
        self.book_model_id = data.get("book_model", "")

        self.documents = data.get("documents", [])
        self.ressources = data.get("ressources", [])

        return self

    def add_document(self, name: str, document_type: str = "Livre"):

        document = {
            "nom": name,
            "type": document_type
        }

        self.documents.append(document)

        project_file = self.root / "projet.json"

        project_data = {
            "nom": self.name,
            "version": self.VERSION,
            "format": self.format,
            "book_model": self.book_model_id,
            "date_creation": datetime.now().isoformat(),
            "date_modification": datetime.now().isoformat(),
            "documents": self.documents,
            "ressources": self.ressources
        }

        with open(
            project_file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                project_data,
                f,
                indent=4,
                ensure_ascii=False
            )