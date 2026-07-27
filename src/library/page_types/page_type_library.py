from __future__ import annotations

import json
from pathlib import Path

from src.library.page_types.page_type import PageType


class PageTypeLibrary:
    """
    Bibliothèque des types de pages.
    """

    def __init__(self) -> None:

        self._page_types: dict[str, PageType] = {}

        self.storage_path = (
            Path(__file__).resolve().parents[3]
            / "data"
            / "page_types"
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
        page_type: PageType,
    ) -> None:

        self._page_types[page_type.id] = page_type

    def get(
        self,
        page_type_id: str,
    ) -> PageType | None:

        return self._page_types.get(page_type_id)

    def all(self) -> list[PageType]:

        return list(self._page_types.values())

    def exists(
        self,
        page_type_id: str,
    ) -> bool:

        return page_type_id in self._page_types

    def remove(
        self,
        page_type_id: str,
    ) -> bool:

        return self._page_types.pop(page_type_id, None) is not None

    def clear(self) -> None:

        self._page_types.clear()

    # ==========================================================
    # Sauvegarde
    # ==========================================================

    def save(self) -> None:

        for page_type in self._page_types.values():

            filename = (
                self.storage_path
                / f"{page_type.id}.json"
            )

            with open(
                filename,
                "w",
                encoding="utf-8",
            ) as file:

                json.dump(
                    page_type.to_dict(),
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
                PageType.from_dict(data)
            )

        self._ensure_default_page_types()

    # ==========================================================
    # Initialisation
    # ==========================================================

    def _ensure_default_page_types(self) -> None:

        defaults = [

            PageType(
                id="text_page",
                name="Page de texte",
                description="Page contenant principalement du texte.",
            ),

            PageType(
                id="image_page",
                name="Page image",
                description="Page contenant principalement une image.",
            ),

            PageType(
                id="chapter_page",
                name="Page de chapitre",
                description="Première page d'un chapitre.",
            ),
        ]

        modified = False

        for page_type in defaults:

            if self.exists(page_type.id):
                continue

            self.add(page_type)
            modified = True

        if modified:
            self.save()

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __len__(self) -> int:

        return len(self._page_types)

    def __iter__(self):

        return iter(self._page_types.values())

    def __repr__(self) -> str:

        return (
            f"PageTypeLibrary("
            f"page_types={len(self._page_types)})"
        )