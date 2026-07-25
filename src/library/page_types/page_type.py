from dataclasses import dataclass, field


@dataclass(slots=True)
class PageType:
    id: str
    name: str
    description: str = ""

    templates: list[str] = field(default_factory=list)

    parameters: dict[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict:

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "templates": self.templates,
            "parameters": self.parameters,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PageType":

        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            templates=data.get("templates", []),
            parameters=data.get("parameters", {}),
        )