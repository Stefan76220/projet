from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class BookModel:
    """
    Représente un modèle de livre.

    Un modèle de livre définit les types de pages autorisés.
    Chaque type de page proposera ensuite ses propres gabarits.
    """

    id: str
    name: str

    description: str = ""

    page_types: list[str] = field(default_factory=list)

    parameters: dict[str, object] = field(default_factory=dict)

    # ==========================================================
    # Sérialisation
    # ==========================================================

    def to_dict(self) -> dict:

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "page_types": list(self.page_types),
            "parameters": dict(self.parameters),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "BookModel":

        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get(
                "description",
                "",
            ),
            page_types=list(
                data.get(
                    "page_types",
                    [],
                )
            ),
            parameters=dict(
                data.get(
                    "parameters",
                    {},
                )
            ),
        )

    # ==========================================================
    # Gestion des types de pages
    # ==========================================================

    def add_page_type(
        self,
        page_type_id: str,
    ) -> None:

        if page_type_id not in self.page_types:
            self.page_types.append(page_type_id)

    def remove_page_type(
        self,
        page_type_id: str,
    ) -> bool:

        if page_type_id not in self.page_types:
            return False

        self.page_types.remove(page_type_id)

        return True

    def has_page_type(
        self,
        page_type_id: str,
    ) -> bool:

        return page_type_id in self.page_types

    # ==========================================================
    # Paramètres
    # ==========================================================

    def get_parameter(
        self,
        name: str,
        default=None,
    ):

        return self.parameters.get(
            name,
            default,
        )

    def set_parameter(
        self,
        name: str,
        value,
    ) -> None:

        self.parameters[name] = value

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"BookModel("
            f"id={self.id!r}, "
            f"name={self.name!r})"
        )