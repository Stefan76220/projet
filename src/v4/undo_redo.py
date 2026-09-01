from __future__ import annotations

"""
TomeLinea V4 — Annuler / Rétablir du poste de travail.

Portée :
- Structure ;
- Composition ;
- états de travail persistants du Projet
  (verrouillages, Fonds guides, etc.).

Non concerné :
- import Source ;
- analyse / réanalyse complète ;
- propositions Analyse -> Livre.

L'historique Undo/Redo est TRANSITOIRE :
il n'est jamais stocké dans ProjectV4 ni dans le fichier projet.

Principe :
une action utilisateur est exécutée dans une transaction.
Si elle échoue, l'état du poste de travail est restauré.
Si elle réussit, elle devient annulable.

Les objets UI ne doivent jamais conserver une référence directe
à une ancienne PageV4 après Undo/Redo : ils doivent retrouver
les objets par leurs UUID stables.
"""

from copy import deepcopy
from dataclasses import dataclass
from typing import Callable, Generic, TypeVar, Any

from src.v4.domain import BookV4
from src.v4.project import ProjectV4


T = TypeVar("T")


@dataclass(slots=True)
class _WorkspaceSnapshot:
    book: BookV4 | None
    metadata: dict[str, Any]
    history: list[dict[str, Any]]
    updated_at: str


@dataclass(slots=True)
class _HistoryEntry:
    label: str
    snapshot: _WorkspaceSnapshot


def _snapshot(
    project: ProjectV4,
) -> _WorkspaceSnapshot:

    return _WorkspaceSnapshot(
        book=deepcopy(
            project.book
        ),
        metadata=deepcopy(
            project.metadata
        ),
        history=deepcopy(
            project.history
        ),
        updated_at=str(
            project.updated_at
        ),
    )


def _restore(
    project: ProjectV4,
    snapshot: _WorkspaceSnapshot,
) -> None:

    project.book = deepcopy(
        snapshot.book
    )

    project.metadata = deepcopy(
        snapshot.metadata
    )

    project.history = deepcopy(
        snapshot.history
    )

    project.updated_at = str(
        snapshot.updated_at
    )

    project.validate()


class WorkspaceUndoRedoV4(Generic[T]):

    def __init__(
        self,
        project: ProjectV4,
        *,
        max_depth: int = 30,
    ) -> None:

        if max_depth < 1:
            raise ValueError(
                "La profondeur Undo doit être >= 1."
            )

        project.validate()

        self.project = project
        self.max_depth = int(
            max_depth
        )

        self._undo: list[
            _HistoryEntry
        ] = []

        self._redo: list[
            _HistoryEntry
        ] = []


    @property
    def can_undo(self) -> bool:
        return bool(
            self._undo
        )


    @property
    def can_redo(self) -> bool:
        return bool(
            self._redo
        )


    @property
    def undo_depth(self) -> int:
        return len(
            self._undo
        )


    @property
    def redo_depth(self) -> int:
        return len(
            self._redo
        )


    @property
    def next_undo_label(
        self,
    ) -> str | None:

        if not self._undo:
            return None

        return self._undo[
            -1
        ].label


    @property
    def next_redo_label(
        self,
    ) -> str | None:

        if not self._redo:
            return None

        return self._redo[
            -1
        ].label


    def _append_undo(
        self,
        entry: _HistoryEntry,
    ) -> None:

        self._undo.append(
            entry
        )

        excess = (
            len(self._undo)
            - self.max_depth
        )

        if excess > 0:
            del self._undo[
                :excess
            ]


    def _append_redo(
        self,
        entry: _HistoryEntry,
    ) -> None:

        self._redo.append(
            entry
        )

        excess = (
            len(self._redo)
            - self.max_depth
        )

        if excess > 0:
            del self._redo[
                :excess
            ]


    def run(
        self,
        label: str,
        action: Callable[
            [ProjectV4],
            T,
        ],
    ) -> T:
        """
        Exécute une action Structure/Composition atomique.

        Une action échouée :
        - ne reste pas partiellement appliquée ;
        - n'ajoute rien dans Undo ;
        - ne détruit pas Redo.
        """

        clean_label = str(
            label or ""
        ).strip()

        if not clean_label:
            raise ValueError(
                "Libellé Undo absent."
            )

        before = _snapshot(
            self.project
        )

        try:
            result = action(
                self.project
            )

            self.project.validate()

        except Exception:
            _restore(
                self.project,
                before,
            )

            raise

        self._append_undo(
            _HistoryEntry(
                label=clean_label,
                snapshot=before,
            )
        )

        # Toute nouvelle action crée une nouvelle branche.
        self._redo.clear()

        return result


    def undo(
        self,
    ) -> str:
        """
        Revient exactement avant la dernière action.
        """

        if not self._undo:
            raise ValueError(
                "Aucune action à annuler."
            )

        current = _snapshot(
            self.project
        )

        entry = self._undo.pop()

        self._append_redo(
            _HistoryEntry(
                label=entry.label,
                snapshot=current,
            )
        )

        _restore(
            self.project,
            entry.snapshot,
        )

        return entry.label


    def redo(
        self,
    ) -> str:
        """
        Rétablit exactement la dernière action annulée.
        """

        if not self._redo:
            raise ValueError(
                "Aucune action à rétablir."
            )

        current = _snapshot(
            self.project
        )

        entry = self._redo.pop()

        self._append_undo(
            _HistoryEntry(
                label=entry.label,
                snapshot=current,
            )
        )

        _restore(
            self.project,
            entry.snapshot,
        )

        return entry.label


    def clear(
        self,
    ) -> None:
        """
        À utiliser notamment après ouverture d'un autre projet.
        """

        self._undo.clear()
        self._redo.clear()
