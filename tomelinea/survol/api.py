"""Noyau Survol de TomeLinea V5.

Ce module extrait uniquement l'etat et la progression du Survol valide en V4.

Regles :
- Survol est un CLIENT de NavigationState ;
- il ne possede aucun moteur de page parallele ;
- il ne connait ni Tk, ni WebView, ni Canvas ;
- il ne gere ni temporisation, ni polling, ni centrage ;
- chaque ouverture passe par NavigationState ;
- l'ordre physique du Livre reste l'autorite.

L'hote d'interface decide quand une page est reellement visible et quand
il faut appeler ``advance``. Un clic utilisateur peut simplement appeler
``pause``.
"""

from __future__ import annotations

from tomelinea.book import Book
from tomelinea.navigation import NavigationState, NavigationTarget


class SurvolState:
    """Etat simple du Survol, branche sur une Navigation partagee."""

    __slots__ = (
        "navigation",
        "_running",
        "_started",
        "_completed",
        "_position",
        "_generation",
    )

    def __init__(self, navigation: NavigationState) -> None:
        if not isinstance(navigation, NavigationState):
            raise TypeError("Survol requiert le NavigationState commun.")

        self.navigation = navigation
        self._running = False
        self._started = False
        self._completed = False
        self._position = 0
        self._generation = 0

    @property
    def running(self) -> bool:
        return self._running

    @property
    def started(self) -> bool:
        return self._started

    @property
    def completed(self) -> bool:
        return self._completed

    @property
    def position(self) -> int:
        return self._position

    @property
    def generation(self) -> int:
        return self._generation

    def page_order(self, book: Book) -> list[str]:
        return [str(page_id) for page_id in book.page_order]

    def current_position(
        self,
        book: Book,
        active_page_id: str | None = None,
    ) -> int:
        """Position courante, recalee sur la page active si elle est connue."""

        order = self.page_order(book)

        if not order:
            return 0

        active = str(active_page_id or "")

        if active:
            try:
                return order.index(active)
            except ValueError:
                pass

        return max(
            0,
            min(int(self._position), len(order) - 1),
        )

    def request_position(
        self,
        book: Book,
        position: int,
    ) -> NavigationTarget | None:
        """Demande une position par l'unique Navigation commune."""

        if not self._running:
            return None

        order = self.page_order(book)

        if not order:
            self.stop()
            return None

        position = max(
            0,
            min(int(position), len(order) - 1),
        )

        self._generation += 1
        self._position = position

        return self.navigation.request_page(
            book,
            order[position],
        )

    def start(self, book: Book) -> NavigationTarget | None:
        """Demarre toujours au debut de l'ordre physique courant."""

        order = self.page_order(book)

        if not order:
            self._running = False
            self._started = False
            self._completed = False
            self._position = 0
            return None

        self._generation += 1
        self._running = True
        self._started = True
        self._completed = False
        self._position = 0

        return self.request_position(
            book,
            0,
        )

    def pause(
        self,
        book: Book,
        *,
        active_page_id: str | None = None,
    ) -> None:
        """Met le Survol en pause sans toucher a la Navigation partagee."""

        if not self._started:
            return

        self._running = False
        self._generation += 1
        self._position = self.current_position(
            book,
            active_page_id,
        )

    def resume(
        self,
        book: Book,
        *,
        active_page_id: str | None = None,
    ) -> NavigationTarget | None:
        """Reprend depuis la position courante reelle du Livre."""

        order = self.page_order(book)

        if not order:
            return None

        self._position = self.current_position(
            book,
            active_page_id,
        )
        self._generation += 1
        self._running = True
        self._started = True
        self._completed = False

        return self.request_position(
            book,
            self._position,
        )

    def advance(self, book: Book) -> NavigationTarget | None:
        """Passe a la page physique suivante.

        L'hote appelle cette methode uniquement lorsque la page courante
        a fini son temps d'affichage ou son traitement.
        """

        if not self._running:
            return None

        order = self.page_order(book)

        if not order:
            self.stop()
            return None

        next_position = int(self._position) + 1

        if next_position >= len(order):
            self._running = False
            self._started = True
            self._completed = True
            self._generation += 1
            return None

        return self.request_position(
            book,
            next_position,
        )

    def stop(
        self,
        book: Book | None = None,
        *,
        active_page_id: str | None = None,
    ) -> None:
        """Arrete le Survol sans effacer la destination Navigation partagee."""

        if book is not None:
            self._position = self.current_position(
                book,
                active_page_id,
            )

        self._running = False
        self._started = False
        self._completed = False
        self._generation += 1


__all__ = [
    "SurvolState",
]