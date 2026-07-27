from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PageReference:
    """
    Référence légère vers une page.
    """

    number: int
    folder: str

    title: str
    page_type: str
    state: str

    version: str = "1.0"

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def display_name(self) -> str:

        return self.title or f"Page {self.number:03d}"

    @property
    def folder_name(self) -> str:

        return self.folder

    @property
    def is_draft(self) -> bool:

        return self.state == "Brouillon"

    # ==========================================================
    # Sérialisation
    # ==========================================================

    def to_dict(self) -> dict:

        return {
            "numero": self.number,
            "dossier": self.folder,
            "nom": self.title,
            "type": self.page_type,
            "etat": self.state,
            "version": self.version,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "PageReference":

        number = data.get(
            "numero",
            1,
        )

        return cls(
            number=number,
            folder=data.get(
                "dossier",
                f"page_{number:04d}",
            ),
            title=data.get(
                "nom",
                f"Page {number:03d}",
            ),
            page_type=data.get(
                "type",
                "Page vide",
            ),
            state=data.get(
                "etat",
                "Brouillon",
            ),
            version=data.get(
                "version",
                "1.0",
            ),
        )

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"number={self.number}, "
            f"title={self.display_name!r})"
        )