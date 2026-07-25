from pathlib import Path
import json

from .book_model import BookModel


class BookModelLibrary:
    """
    Bibliothèque des modèles de livres.
    """

    def __init__(self):

        self._models: dict[str, BookModel] = {}

        self.storage_path = (
            Path(__file__).resolve()
            .parents[3]
            / "data"
            / "book_models"
        )

        self.storage_path.mkdir(parents=True, exist_ok=True)

    def add(self, model: BookModel) -> None:
        self._models[model.id] = model

    def get(self, model_id: str) -> BookModel | None:
        return self._models.get(model_id)

    def all(self) -> list[BookModel]:
        return list(self._models.values())

    def exists(self, model_id: str) -> bool:
        return model_id in self._models

    def clear(self) -> None:
        self._models.clear()

    def save(self) -> None:

        for model in self._models.values():

            filename = self.storage_path / f"{model.id}.json"

            with open(filename, "w", encoding="utf-8") as f:
                json.dump(
                    model.to_dict(),
                    f,
                    ensure_ascii=False,
                    indent=4
                )

    def load(self) -> None:

        self.clear()

        for filename in self.storage_path.glob("*.json"):

            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)

            model = BookModel.from_dict(data)

            self.add(model)

        if not self._models:

            default_model = BookModel(
                id="empty_book",
                name="Livre vide",
                description="Modèle créé automatiquement."
            )

            self.add(default_model)
            self.save()