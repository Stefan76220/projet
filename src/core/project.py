from pathlib import Path
import json
from datetime import datetime


class Project:

    VERSION = "1.0"

    def __init__(self):

        self.name = ""
        self.format = "A5"
        self.template = "Nature Premium"
        self.root = None

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

        project_data = {
            "nom": self.name,
            "version": self.VERSION,
            "format": self.format,
            "modele": self.template,
            "date_creation": datetime.now().isoformat(),
            "date_modification": datetime.now().isoformat(),
            "documents": [],
            "ressources": []
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

        root = Path(project_folder)
        project_file = root / "projet.json"

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
        self.template = data.get("modele", "Nature Premium")

        return self