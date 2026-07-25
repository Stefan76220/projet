from dataclasses import dataclass


@dataclass
class PageReference:
    """
    Référence légère vers une page.

    Cette classe est utilisée par les documents afin d'éviter
    de charger les pages complètes tant qu'elles ne sont pas
    ouvertes dans l'éditeur.
    """

    number: int
    folder: str

    title: str
    page_type: str
    state: str
    version: str = "1.0"

    # ---------------------------------------------------------

    @property
    def display_name(self):

        return f"Page {self.number:03d}"

    # ---------------------------------------------------------

    @property
    def folder_name(self):

        return self.folder

    # ---------------------------------------------------------

    def to_dict(self):

        return {
            "numero": self.number,
            "dossier": self.folder,
            "nom": self.title,
            "type": self.page_type,
            "etat": self.state,
            "version": self.version
        }

    # ---------------------------------------------------------

    @classmethod
    def from_dict(cls, data):

        numero = data.get("numero", 1)

        return cls(
            number=numero,
            folder=data.get("dossier", f"page_{numero:04d}"),
            title=data.get("nom", f"Page {numero:03d}"),
            page_type=data.get("type", "Page vide"),
            state=data.get("etat", "Brouillon"),
            version=data.get("version", "1.0")
        )