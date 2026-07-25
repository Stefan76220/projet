from pathlib import Path
import json
from datetime import datetime


class Page:

    VERSION = "1.0"

    def __init__(self):

        self.number = 1
        self.title = ""
        self.page_type = "Page vide"
        self.state = "Brouillon"

        self.author = ""
        self.description = ""

        self.format = "A5"
        self.orientation = "Portrait"

        self.elements = []
        self.history = []

        self.created = None
        self.modified = None

        self.root = None

    # ---------------------------------------------------------

    def create(self, pages_folder: str | Path, number: int):

        self.number = number

        now = datetime.now().isoformat()

        self.created = now
        self.modified = now

        folder_name = f"page_{number:04d}"

        self.root = Path(pages_folder) / folder_name

        self.root.mkdir(parents=True, exist_ok=True)

        self.save()

        return self.root

    # ---------------------------------------------------------

    def save(self):

        if self.root is None:
            return

        self.modified = datetime.now().isoformat()

        page_data = {

            "identite": {

                "numero": self.number,
                "nom": self.title or f"Page {self.number:03d}",
                "type": self.page_type,
                "etat": self.state,
                "version": self.VERSION

            },

            "metadonnees": {

                "auteur": self.author,
                "creation": self.created,
                "modification": self.modified,
                "description": self.description

            },

            "mise_en_page": {

                "format": self.format,
                "orientation": self.orientation

            },

            "elements": self.elements,

            "historique": self.history

        }

        with open(
            self.root / "page.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                page_data,
                f,
                indent=4,
                ensure_ascii=False
            )

    # ---------------------------------------------------------

    def load(self, folder: str | Path):

        self.root = Path(folder)

        with open(
            self.root / "page.json",
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        identite = data.get("identite", {})
        meta = data.get("metadonnees", {})
        mise_en_page = data.get("mise_en_page", {})

        self.number = identite.get("numero", 1)
        self.title = identite.get("nom", "")
        self.page_type = identite.get("type", "Page vide")
        self.state = identite.get("etat", "Brouillon")

        self.author = meta.get("auteur", "")
        self.created = meta.get("creation")
        self.modified = meta.get("modification")
        self.description = meta.get("description", "")

        self.format = mise_en_page.get("format", "A5")
        self.orientation = mise_en_page.get("orientation", "Portrait")

        self.elements = data.get("elements", [])
        self.history = data.get("historique", [])

        return self