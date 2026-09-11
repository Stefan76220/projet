from __future__ import annotations

"""
TomeLinea V4 — agrégat Projet.

ProjectV4 représente l'état persistant complet d'un projet TomeLinea.

Il rassemble sans les confondre :
    Source -> Analyse -> Propositions -> Livre

La Composition viendra ensuite modifier le Livre lui-même.
Le Visionneur lira le Livre mais ne possédera aucun état parallèle.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from src.v4.analysis import AnalysisV4
from src.v4.domain import BookV4
from src.v4.proposal import BookProposal
from src.v4.source import SourceV4


def new_id() -> str:
    return str(uuid4())


def utc_now() -> str:
    return datetime.now(
        timezone.utc
    ).isoformat()


@dataclass(slots=True)
class ProjectV4:
    """
    Racine persistante d'un projet TomeLinea V4.

    Rien dans l'interface ne doit constituer une seconde vérité
    parallèle à cet objet.
    """

    id: str = field(
        default_factory=new_id
    )

    title: str = ""

    created_at: str = field(
        default_factory=utc_now
    )

    updated_at: str = field(
        default_factory=utc_now
    )

    source: SourceV4 = field(
        default_factory=SourceV4
    )

    analysis: AnalysisV4 = field(
        default_factory=AnalysisV4
    )

    # Le Livre n'existe pas obligatoirement immédiatement :
    # il peut être créé seulement après l'analyse initiale.
    book: BookV4 | None = None

    # Les propositions sont conservées pour assurer la traçabilité
    # des passages Analyse -> Livre et des réanalyses successives.
    proposals: dict[
        str,
        BookProposal,
    ] = field(
        default_factory=dict
    )

    active_proposal_id: str | None = None

    metadata: dict[str, Any] = field(
        default_factory=dict
    )

    history: list[
        dict[str, Any]
    ] = field(
        default_factory=list
    )

    def touch(self) -> None:
        self.updated_at = utc_now()

    def add_proposal(
        self,
        proposal: BookProposal,
        *,
        activate: bool = True,
    ) -> None:

        proposal.validate()

        if proposal.id in self.proposals:
            raise ValueError(
                f"Proposition déjà présente : {proposal.id}"
            )

        self.proposals[
            proposal.id
        ] = proposal

        if activate:
            self.active_proposal_id = (
                proposal.id
            )

        self.history.append(
            {
                "action": "proposition_ajoutee",
                "proposal_id": proposal.id,
                "date": utc_now(),
            }
        )

        self.touch()
        self.validate()

    @property
    def active_proposal(
        self,
    ) -> BookProposal | None:

        if self.active_proposal_id is None:
            return None

        proposal = self.proposals.get(
            self.active_proposal_id
        )

        if proposal is None:
            raise ValueError(
                "La proposition active est inconnue : "
                f"{self.active_proposal_id}"
            )

        return proposal

    def set_book(
        self,
        book: BookV4,
        *,
        proposal_id: str | None = None,
    ) -> None:

        book.validate()

        if (
            proposal_id is not None
            and proposal_id not in self.proposals
        ):
            raise ValueError(
                "Impossible de rattacher le Livre "
                "à une proposition inconnue : "
                f"{proposal_id}"
            )

        self.book = book

        self.history.append(
            {
                "action": "livre_defini",
                "book_id": book.id,
                "proposal_id": proposal_id,
                "date": utc_now(),
            }
        )

        self.touch()
        self.validate()

    def validate(self) -> None:
        if not self.id:
            raise ValueError(
                "Identité Projet absente."
            )

        self.source.validate()
        self.analysis.validate()

        if self.book is not None:
            self.book.validate()

        for proposal_id, proposal in (
            self.proposals.items()
        ):
            if proposal.id != proposal_id:
                raise ValueError(
                    "Incohérence d'identité Proposition : "
                    f"{proposal_id}"
                )

            proposal.validate()

        if (
            self.active_proposal_id is not None
            and self.active_proposal_id
            not in self.proposals
        ):
            raise ValueError(
                "Proposition active inconnue : "
                f"{self.active_proposal_id}"
            )
