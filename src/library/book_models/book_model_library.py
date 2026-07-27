from __future__ import annotations

import json
from pathlib import Path

from .book_model import BookModel


class BookModelLibrary:
    """
    Bibliothèque des modèles de livres.
    """

    def __init__(self) -> None:

        self._models: dict[str, BookModel] = {}

        self.storage_path = (
            Path(__file__).resolve().parents[3]
            / "data"
            / "book_models"
        )

        self.storage_path.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ==========================================================
    # Accès
    # ==========================================================

    def add(
        self,
        model: BookModel,
    ) -> None:

        self._models[model.id] = model

    def get(
        self,
        model_id: str,
    ) -> BookModel | None:

        return self._models.get(model_id)

    def all(self) -> list[BookModel]:

        return list(self._models.values())

    def exists(
        self,
        model_id: str,
    ) -> bool:

        return model_id in self._models

    def remove(
        self,
        model_id: str,
    ) -> bool:

        return self._models.pop(model_id, None) is not None

    def clear(self) -> None:

        self._models.clear()

    # ==========================================================
    # Sauvegarde
    # ==========================================================

    def save(self) -> None:

        for model in self._models.values():

            filename = (
                self.storage_path
                / f"{model.id}.json"
            )

            with open(
                filename,
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    model.to_dict(),
                    file,
                    ensure_ascii=False,
                    indent=4,
                )

    def load(self) -> None:

        self.clear()

        for filename in sorted(
            self.storage_path.glob("*.json")
        ):

            with open(
                filename,
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(file)

            self.add(
                BookModel.from_dict(data)
            )

        if not self._models:
            self._create_default_model()

    # ==========================================================
    # Initialisation
    # ==========================================================

    def _create_default_model(self) -> None:

        model = BookModel(
            id="empty_book",
            name="Livre vide",
            description="Modèle créé automatiquement.",
        )

        self.add(model)
        self.save()

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __len__(self) -> int:

        return len(self._models)

    def __iter__(self):

        return iter(self._models.values())

    def __repr__(self) -> str:

        return (
            f"BookModelLibrary("
            f"models={len(self._models)})"
        )