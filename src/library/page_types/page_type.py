from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class PageType:
    """
    Décrit un type de page disponible dans l'application.
    """

    id: str
    name: str

    description: str = ""

    templates: list[str] = field(default_factory=list)

    parameters: dict[str, object] = field(default_factory=dict)

    # ==========================================================
    # Sérialisation
    # ==========================================================

    def to_dict(self) -> dict:

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "templates": list(self.templates),
            "parameters": dict(self.parameters),
        }

    @classmethod
    def from_dict(
        cls,
        data: dict,
    ) -> "PageType":

        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get(
                "description",
                "",
            ),
            templates=list(
                data.get(
                    "templates",
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
    # Gestion des gabarits
    # ==========================================================

    def add_template(
        self,
        template_id: str,
    ) -> None:

        if template_id not in self.templates:
            self.templates.append(template_id)

    def remove_template(
        self,
        template_id: str,
    ) -> bool:

        if template_id not in self.templates:
            return False

        self.templates.remove(template_id)

        return True

    def has_template(
        self,
        template_id: str,
    ) -> bool:

        return template_id in self.templates

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
            f"PageType("
            f"id={self.id!r}, "
            f"name={self.name!r})"
        )