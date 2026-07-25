from pathlib import Path
import json
from datetime import datetime

from src.core.page import Page


class Document:

    VERSION = "1.0"

    def __init__(self):

        self.name = ""
        self.type = "Livre"
        self.root = None
        self.pages = []

    # ------------------------------------------------------------------

    def create(self, documents_folder: str | Path, name: str):

        self.name = name

        self.root = Path(documents_folder) / name

        self.root.mkdir(parents=True, exist_ok=True)
        (self.root / "pages").mkdir(exist_ok=True)

        self.pages = []

        self.save()

        return self

    # ------------------------------------------------------------------

    def load(self, folder: str | Path):

        self.root = Path(folder)

        with open(
            self.root / "document.json",
            "r",
            encoding="utf-8"
        ) as f:

            data = json.load(f)

        self.name = data.get("nom", self.root.name)
        self.type = data.get("type", "Livre")

        self.pages = []

        for page in data.get("pages", []):

            # Nouveau format
            if "dossier" in page:

                self.pages.append(
                    {
                        "numero": page["numero"],
                        "dossier": page["dossier"]
                    }
                )

            # Ancien format (compatibilité)
            else:

                numero = page.get("numero", len(self.pages) + 1)

                self.pages.append(
                    {
                        "numero": numero,
                        "dossier": f"page_{numero:04d}"
                    }
                )

        return self

    # ------------------------------------------------------------------

    def save(self):

        if self.root is None:
            return

        document_data = {
            "nom": self.name,
            "type": self.type,
            "version": self.VERSION,
            "date_modification": datetime.now().isoformat(),
            "pages": self.pages
        }

        with open(
            self.root / "document.json",
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                document_data,
                f,
                indent=4,
                ensure_ascii=False
            )

    # ------------------------------------------------------------------

    def add_page(self, page_type=None):

        if page_type is None:
            page_type = "Page vide"

        numero = len(self.pages) + 1

        page = Page()
        page.page_type = page_type

        page.create(
            self.root / "pages",
            numero
        )

        self.pages.append(
            {
                "numero": numero,
                "dossier": f"page_{numero:04d}"
            }
        )

        self.save()

        return page

    # ------------------------------------------------------------------

    def get_page(self, numero):

        dossier = self.root / "pages" / f"page_{numero:04d}"

        if not dossier.exists():
            return None

        page = Page()
        page.load(dossier)

        return page