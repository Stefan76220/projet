from dataclasses import dataclass, field


@dataclass(slots=True)
class BookModel:
    """
    Représente un modèle de livre.

    Un modèle de livre définit les types de pages autorisés.
    Chaque type de page proposera ensuite ses propres gabarits.

    Le modèle ne contient jamais le contenu du livre.
    """

    id: str
    name: str
    description: str = ""

    # Identifiants des types de pages autorisés
    page_types: list[str] = field(default_factory=list)

    # Paramètres spécifiques au modèle
    parameters: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convertit le modèle en dictionnaire."""

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "page_types": self.page_types,
            "parameters": self.parameters,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BookModel":
        """Construit un modèle à partir d'un dictionnaire."""

        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            page_types=list(data.get("page_types", [])),
            parameters=dict(data.get("parameters", {})),
        )