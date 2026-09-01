from __future__ import annotations

"""
TomeLinea V4 — session du poste de travail.

Cette couche est le contrat entre l'interface graphique et le noyau.

Elle possède uniquement des états transitoires d'interface :
- page active ;
- sélection courante ;
- pile Undo/Redo ;
- révision d'affichage.

Elle ne possède JAMAIS une copie du Livre.

Toute modification réelle passe par ProjectV4 / BookV4.
"""

from pathlib import Path
from typing import Callable, Iterable, TypeVar

from src.v4.project import ProjectV4
from src.v4.storage import (
    load_project,
    save_project,
)
from src.v4.book_state import (
    BookState,
    build_book_state,
)
from src.v4.composition import (
    element_by_id,
)
from src.v4.composition_arrange import (
    normalize_selection,
)
from src.v4.undo_redo import (
    WorkspaceUndoRedoV4,
)


T = TypeVar("T")


class WorkspaceSessionV4:

    def __init__(
        self,
        project: ProjectV4,
        *,
        max_undo_depth: int = 30,
    ) -> None:

        project.validate()

        self.project = project

        self.max_undo_depth = int(
            max_undo_depth
        )

        self.undo_redo = (
            WorkspaceUndoRedoV4(
                project,
                max_depth=self.max_undo_depth,
            )
        )

        self.active_page_id: str | None = None

        self.selected_element_ids: list[str] = []

        self.revision: int = 0

        self._choose_initial_page()


    # ==========================================================
    # CONTEXTE
    # ==========================================================

    @property
    def book(self):

        if self.project.book is None:
            raise ValueError(
                "Le Projet ne possède aucun Livre."
            )

        return self.project.book


    def _choose_initial_page(
        self,
    ) -> None:

        if (
            self.project.book is not None
            and self.project.book.page_order
        ):
            self.active_page_id = (
                self.project.book.page_order[0]
            )

        else:
            self.active_page_id = None

        self.selected_element_ids = []


    def _reconcile_context(
        self,
    ) -> None:
        """
        Répare uniquement le contexte transitoire après une mutation.

        Aucun objet du domaine n'est modifié.
        """

        if self.project.book is None:
            self.active_page_id = None
            self.selected_element_ids = []
            return

        book = self.project.book

        if (
            self.active_page_id is None
            or self.active_page_id
            not in book.pages
        ):
            self.active_page_id = (
                book.page_order[0]
                if book.page_order
                else None
            )

        if self.active_page_id is None:
            self.selected_element_ids = []
            return

        page = book.pages[
            self.active_page_id
        ]

        valid: list[str] = []

        for element_id in (
            self.selected_element_ids
        ):
            try:
                element_by_id(
                    page,
                    element_id,
                )
                valid.append(
                    element_id
                )
            except KeyError:
                pass

        self.selected_element_ids = valid


    def _touch_revision(
        self,
    ) -> None:

        self.revision += 1


    # ==========================================================
    # PAGE ACTIVE
    # ==========================================================

    def set_active_page(
        self,
        page_id: str,
    ) -> str:

        if page_id not in self.book.pages:
            raise KeyError(
                page_id
            )

        if (
            self.active_page_id
            != page_id
        ):
            self.active_page_id = page_id

            # Une sélection ne traverse jamais implicitement
            # d'une page à une autre.
            self.selected_element_ids = []

            self._touch_revision()

        return page_id


    @property
    def active_page(
        self,
    ):

        if self.active_page_id is None:
            return None

        return self.book.pages.get(
            self.active_page_id
        )


    # ==========================================================
    # SELECTION TRANSITOIRE
    # ==========================================================

    def set_selection(
        self,
        element_ids: Iterable[str],
        *,
        include_associated: bool = True,
    ) -> list[str]:

        if self.active_page_id is None:
            raise ValueError(
                "Aucune page active."
            )

        result = normalize_selection(
            self.book,
            self.active_page_id,
            element_ids,
            include_associated=(
                include_associated
            ),
        )

        self.selected_element_ids = list(
            result
        )

        self._touch_revision()

        return list(
            self.selected_element_ids
        )


    def clear_selection(
        self,
    ) -> None:

        if self.selected_element_ids:
            self.selected_element_ids = []
            self._touch_revision()


    # ==========================================================
    # ACTIONS TRANSACTIONNELLES
    # ==========================================================

    def execute(
        self,
        label: str,
        action: Callable[
            [ProjectV4],
            T,
        ],
    ) -> T:

        result = self.undo_redo.run(
            label,
            action,
        )

        self._reconcile_context()
        self._touch_revision()

        return result


    @property
    def can_undo(
        self,
    ) -> bool:

        return self.undo_redo.can_undo


    @property
    def can_redo(
        self,
    ) -> bool:

        return self.undo_redo.can_redo


    def undo(
        self,
    ) -> str:

        label = self.undo_redo.undo()

        self._reconcile_context()
        self._touch_revision()

        return label


    def redo(
        self,
    ) -> str:

        label = self.undo_redo.redo()

        self._reconcile_context()
        self._touch_revision()

        return label


    # ==========================================================
    # ETAT REEL DU LIVRE
    # ==========================================================

    def book_state(
        self,
    ) -> BookState:

        return build_book_state(
            self.book
        )


    # ==========================================================
    # SAUVEGARDE / OUVERTURE
    # ==========================================================

    def save(
        self,
        path: str | Path,
    ) -> None:

        save_project(
            self.project,
            Path(path),
        )


    @classmethod
    def open(
        cls,
        path: str | Path,
        *,
        max_undo_depth: int = 30,
    ) -> "WorkspaceSessionV4":

        project = load_project(
            Path(path)
        )

        return cls(
            project,
            max_undo_depth=max_undo_depth,
        )
