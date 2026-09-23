"""Contrat d'attente commun de TomeLinea V5.

V5-08 ne recree pas l'animation. Il reutilise le moteur V4 valide :
- meme GIF TomeLinea ;
- boucle visuelle pendant le travail reel ;
- quand le travail se termine, le mouvement finit proprement au lieu d'etre coupe ;
- aucun pourcentage artificiel ;
- aucun delai fixe impose au traitement.

Les libelles de phase sont de la metadonnee applicative. Ils sont reels et
peuvent etre affiches par n'importe quel hote V5 sans dupliquer le moteur.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Callable

from src.gui_v4.startup_runtime import (
    FINISH_TAIL_MS,
    TARGET_CYCLE_MS,
    WAIT_HEIGHT,
    WAIT_MEDIA,
    WAIT_WIDTH,
    StartupAnimation,
    start_wait_animation_async,
)


class WaitPhase(str, Enum):
    OPEN_PROJECT = "open_project"
    IMPORT_SOURCE = "import_source"
    ANALYZE_SOURCE = "analyze_source"
    PREPARE_COMPOSITION = "prepare_composition"
    RECOMPOSE_BOOK = "recompose_book"
    SAVE_PROJECT = "save_project"
    LONG_OPERATION = "long_operation"


WAIT_LABELS: dict[WaitPhase, str] = {
    WaitPhase.OPEN_PROJECT: "Ouverture du projet",
    WaitPhase.IMPORT_SOURCE: "Import de la Source",
    WaitPhase.ANALYZE_SOURCE: "Analyse de la Source",
    WaitPhase.PREPARE_COMPOSITION: "Préparation de la Composition",
    WaitPhase.RECOMPOSE_BOOK: "Recomposition du Livre",
    WaitPhase.SAVE_PROJECT: "Enregistrement du projet",
    WaitPhase.LONG_OPERATION: "Traitement TomeLinea",
}


@dataclass(frozen=True, slots=True)
class WaitSnapshot:
    phase: WaitPhase
    label: str
    detail: str
    finished: bool


class WaitSession:
    """Session applicative legere autour du moteur d'animation valide."""

    __slots__ = ("_controller", "_phase", "_detail", "_finished")

    def __init__(
        self,
        controller: StartupAnimation,
        phase: WaitPhase,
        detail: str = "",
    ) -> None:
        self._controller = controller
        self._phase = WaitPhase(phase)
        self._detail = str(detail or "").strip()
        self._finished = False

    @property
    def controller(self) -> StartupAnimation:
        return self._controller

    @property
    def phase(self) -> WaitPhase:
        return self._phase

    @property
    def label(self) -> str:
        return WAIT_LABELS[self._phase]

    @property
    def detail(self) -> str:
        return self._detail

    @property
    def finished(self) -> bool:
        return self._finished

    @property
    def snapshot(self) -> WaitSnapshot:
        return WaitSnapshot(
            phase=self._phase,
            label=self.label,
            detail=self._detail,
            finished=self._finished,
        )

    def set_phase(
        self,
        phase: WaitPhase,
        detail: str = "",
    ) -> WaitSnapshot:
        """Change uniquement le libelle reel de l'operation en cours."""

        if self._finished:
            return self.snapshot

        self._phase = WaitPhase(phase)
        self._detail = str(detail or "").strip()
        return self.snapshot

    def finish(
        self,
        *,
        pump: Callable[[], None] | None = None,
        timeout: float = 15.0,
    ) -> None:
        """Termine l'animation selon la fin de cycle validee en V4."""

        if self._finished:
            return

        self._controller.finish_after_cycle(
            pump=pump,
            timeout=float(timeout),
        )
        self._finished = True


def start_wait(
    phase: WaitPhase = WaitPhase.LONG_OPERATION,
    detail: str = "",
    *,
    starter: Callable[[], StartupAnimation] | None = None,
) -> WaitSession:
    """Demarre l'attente sans retarder le travail reel."""

    factory = starter or start_wait_animation_async
    controller = factory()

    return WaitSession(
        controller=controller,
        phase=WaitPhase(phase),
        detail=detail,
    )


def wait_asset() -> Path:
    return Path(WAIT_MEDIA)


__all__ = [
    "WAIT_WIDTH",
    "WAIT_HEIGHT",
    "TARGET_CYCLE_MS",
    "FINISH_TAIL_MS",
    "WaitPhase",
    "WAIT_LABELS",
    "WaitSnapshot",
    "WaitSession",
    "start_wait",
    "wait_asset",
]