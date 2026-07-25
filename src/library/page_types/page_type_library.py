from pathlib import Path
import json

from src.library.page_types.page_type import PageType


class PageTypeLibrary:
    """
    Bibliothèque des types de pages.
    """

    def __init__(self):

        self._page_types: dict[str, PageType] = {}

        self.storage_path = (
            Path(__file__).resolve()
            .parents[3]
            / "data"
            / "page_types"
        )

        self.storage_path.mkdir(parents=True, exist_ok=True)

    def add(self, page_type: PageType) -> None:

        self._page_types[page_type.id] = page_type

    def get(self, page_type_id: str) -> PageType | None:

        return self._page_types.get(page_type_id)

    def all(self) -> list[PageType]:

        return list(self._page_types.values())

    def exists(self, page_type_id: str) -> bool:

        return page_type_id in self._page_types

    def clear(self) -> None:

        self._page_types.clear()

    def save(self) -> None:

        for page_type in self._page_types.values():

            filename = self.storage_path / f"{page_type.id}.json"

            with open(filename, "w", encoding="utf-8") as f:

                json.dump(
                    page_type.to_dict(),
                    f,
                    ensure_ascii=False,
                    indent=4
                )

    def load(self) -> None:

        self.clear()

        for filename in self.storage_path.glob("*.json"):

            with open(filename, "r", encoding="utf-8") as f:

                data = json.load(f)

            page_type = PageType.from_dict(data)

            self.add(page_type)

        default_page_types = [
            PageType(
                id="text_page",
                name="Page de texte",
                description="Page contenant principalement du texte."
            ),
            PageType(
                id="image_page",
                name="Page image",
                description="Page contenant principalement une image."
            ),
            PageType(
                id="chapter_page",
                name="Page de chapitre",
                description="Première page d'un chapitre."
            ),
        ]

        modified = False

        for page_type in default_page_types:

            if not self.exists(page_type.id):
                self.add(page_type)
                modified = True

        if modified:
            self.save()