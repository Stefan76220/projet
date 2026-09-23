"""Contrat de Navigation commune de TomeLinea V5.

Ce module extrait le principe valide de la V4 sans embarquer Tk, WebView
ni logique de Survol :

- une seule destination demandee a la fois ;
- une nouvelle demande remplace immediatement la precedente ;
- aucune file croissante de navigations ;
- les entrees Structure / Aller / Precedente / Suivante / Survol
  utilisent le meme contrat ;
- la destination est un identifiant stable du Livre ;
- le rendu Canvas reste un consommateur de Navigation.

Le Livre reste l'autorite sur l'ordre physique des pages.
"""

from __future__ import annotations

from dataclasses import dataclass

from tomelinea.book import Book


@dataclass(frozen=True, slots=True)
class NavigationTarget:
    """Photographie immutable de la derniere destination demandee."""

    page_id: str
    global_index: int
    generation: int


class NavigationState:
    """Etat transitoire de navigation, volontairement sans file d'attente."""

    __slots__ = ("_target", "_generation")

    def __init__(self) -> None:
        self._target: NavigationTarget | None = None
        self._generation = 0

    @property
    def target(self) -> NavigationTarget | None:
        return self._target

    @property
    def generation(self) -> int:
        return self._generation

    @property
    def requested_page_id(self) -> str | None:
        return self._target.page_id if self._target is not None else None

    @property
    def requested_index(self) -> int | None:
        return self._target.global_index if self._target is not None else None

    def clear(self) -> None:
        """Oublie la destination transitoire sans modifier le Livre."""

        self._target = None

    def request_page(
        self,
        book: Book,
        page_id: str,
    ) -> NavigationTarget:
        """Demande une page existante du Livre.

        La nouvelle destination remplace la precedente : last request wins.
        """

        page_id = str(page_id)

        if page_id not in book.pages:
            raise KeyError(page_id)

        try:
            index = book.page_order.index(page_id)
        except ValueError as exc:
            raise ValueError(
                f"Page absente de l'ordre physique : {page_id}"
            ) from exc

        self._generation += 1
        self._target = NavigationTarget(
            page_id=page_id,
            global_index=index,
            generation=self._generation,
        )
        return self._target

    def request_index(
        self,
        book: Book,
        global_index: int,
    ) -> NavigationTarget:
        """Demande un index physique valide du Livre."""

        index = int(global_index)

        if index < 0 or index >= len(book.page_order):
            raise IndexError(index)

        return self.request_page(
            book,
            book.page_order[index],
        )

    def request_neighbor(
        self,
        book: Book,
        active_page_id: str,
        delta: int,
    ) -> NavigationTarget | None:
        """Demande la page voisine, ou None si la borne du Livre est atteinte."""

        active_page_id = str(active_page_id)

        if active_page_id not in book.pages:
            raise KeyError(active_page_id)

        try:
            index = book.page_order.index(active_page_id)
        except ValueError as exc:
            raise ValueError(
                f"Page active absente de l'ordre physique : {active_page_id}"
            ) from exc

        target_index = index + int(delta)

        if target_index < 0 or target_index >= len(book.page_order):
            return None

        return self.request_index(
            book,
            target_index,
        )


__all__ = [
    "NavigationTarget",
    "NavigationState",
]