from pathlib import Path

from src.core.page import Page


class PageManager:

    def __init__(self):

        pass

    def new_page(self, document_folder: str | Path, number: int):

        pages_folder = Path(document_folder) / "pages"
        pages_folder.mkdir(exist_ok=True)

        page = Page()

        page.create(
            pages_folder,
            number
        )

        return page