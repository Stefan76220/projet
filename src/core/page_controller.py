from __future__ import annotations

from typing import Any


class PageController:
    """
    Contrôleur de la sélection d'une page.
    """

    def __init__(self, canvas) -> None:

        self.canvas = canvas

        self.page_selected = False
        self.selected_object: Any | None = None

    # ==========================================================
    # Propriétés
    # ==========================================================

    @property
    def has_selected_object(self) -> bool:

        return self.selected_object is not None

    # ==========================================================
    # Sélection de la page
    # ==========================================================

    def select_page(self) -> None:

        if self.page_selected:
            return

        self.page_selected = True

        self.canvas.set_page_selected(True)

    def unselect_page(self) -> None:

        if not self.page_selected:
            return

        self.page_selected = False

        self.canvas.set_page_selected(False)

    # ==========================================================
    # Sélection des objets
    # ==========================================================

    def select_object(
        self,
        obj: Any | None,
    ) -> None:

        self.select_page()

        if self.selected_object is obj:
            return

        self.unselect_object()

        self.selected_object = obj

        if obj is not None:
            obj.set_selected(True)

    def unselect_object(self) -> None:

        if self.selected_object is None:
            return

        self.selected_object.set_selected(False)

        self.selected_object = None

    # ==========================================================
    # Désélection
    # ==========================================================

    def unselect_all(self) -> None:

        self.unselect_object()
        self.unselect_page()

    # ==========================================================
    # Accès
    # ==========================================================

    def get_selected_object(self) -> Any | None:

        return self.selected_object

    # ==========================================================
    # Utilitaires
    # ==========================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"page_selected={self.page_selected}, "
            f"object_selected={self.has_selected_object})"
        )