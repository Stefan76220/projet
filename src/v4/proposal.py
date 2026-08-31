from __future__ import annotations

"""
TomeLinea V4 — contrat entre Analyse et Livre.

L'Analyse propose.
Le Livre constitue l'état réellement retenu du projet.

Une proposition ne modifie jamais directement un Livre existant.
Chaque page créée conserve aussi la photographie des valeurs
automatiques dont elle est issue. Cette référence permettra aux
réanalyses futures de distinguer une évolution automatique d'une
correction humaine.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from src.v4.domain import (
    BookKind,
    BookV4,
    PageOrigin,
    PageV4,
    SourceLink,
)


def new_id() -> str:
    return str(uuid4())


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True, slots=True)
class ProposedPage:
    """
    Page proposée par l'Analyse.

    proposal_key est stable à l'intérieur d'une proposition et permet
    de savoir précisément quel élément proposé a créé une PageV4.
    """

    proposal_key: str

    page_type: str = "Page"
    title: str = ""
    origin: PageOrigin = PageOrigin.AUTHOR

    source: SourceLink | None = None

    part_key: str | None = None
    model_key: str | None = None

    recto_verso: str | None = None

    spread_key: str | None = None
    spread_side: str | None = None

    is_compensation: bool = False

    analysis_refs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ProposalIssue:
    """
    Élément que TomeLinea souhaite signaler à l'utilisateur.
    """

    code: str
    message: str
    target_key: str | None = None
    severity: str = "a_verifier"


@dataclass(slots=True)
class BookProposal:
    """
    Photographie d'une proposition calculée par l'Analyse.
    """

    id: str = field(default_factory=new_id)
    created_at: str = field(default_factory=utc_now)

    suggested_kind: BookKind = BookKind.UNKNOWN

    source_version_ids: tuple[str, ...] = ()

    pages: list[ProposedPage] = field(default_factory=list)
    parts: list[dict[str, Any]] = field(default_factory=list)
    models: dict[str, dict[str, Any]] = field(default_factory=dict)

    issues: list[ProposalIssue] = field(default_factory=list)

    analysis_refs: tuple[str, ...] = ()

    def add_page(self, page: ProposedPage) -> None:
        if any(
            existing.proposal_key == page.proposal_key
            for existing in self.pages
        ):
            raise ValueError(
                f"Clé de proposition dupliquée : {page.proposal_key}"
            )

        self.pages.append(page)

    def validate(self) -> None:
        keys = [page.proposal_key for page in self.pages]

        if len(keys) != len(set(keys)):
            raise ValueError(
                "Une clé de page apparaît plusieurs fois dans la proposition."
            )

        for page in self.pages:
            if page.source is not None:
                if not page.source.source_id:
                    raise ValueError(
                        f"Source absente pour {page.proposal_key}"
                    )

                if not page.source.source_version_id:
                    raise ValueError(
                        f"Version Source absente pour {page.proposal_key}"
                    )


@dataclass(frozen=True, slots=True)
class ProposalApplication:
    """
    Trace du passage Proposition -> Livre.
    """

    proposal_id: str
    book_id: str
    page_ids_by_proposal_key: dict[str, str]
    applied_at: str


def proposed_page_baseline(
    proposed: ProposedPage,
) -> dict[str, Any]:
    """
    Valeurs automatiques qui ont servi à créer la page.

    Cette photographie ne représente pas l'état courant de la page.
    Elle sert de référence lors des réanalyses.
    """

    source = None

    if proposed.source is not None:
        source = {
            "source_id": proposed.source.source_id,
            "source_version_id": proposed.source.source_version_id,
            "source_page": proposed.source.source_page,
        }

    return {
        "page_type": proposed.page_type,
        "title": proposed.title,
        "origin": proposed.origin.value,
        "source": source,
        "part_id": proposed.part_key,
        "model_id": proposed.model_key,
        "recto_verso": proposed.recto_verso,
        "spread_id": proposed.spread_key,
        "spread_side": proposed.spread_side,
        "is_compensation": proposed.is_compensation,
    }


def create_book_from_proposal(
    proposal: BookProposal,
    *,
    title: str = "",
) -> tuple[BookV4, ProposalApplication]:
    """
    Crée un nouveau LivreV4 à partir d'une proposition.

    Important :
    cette fonction sert à l'initialisation d'un livre.
    Elle ne synchronise pas silencieusement un livre déjà modifié.
    """

    proposal.validate()

    book = BookV4(
        title=title,
        kind=proposal.suggested_kind,
    )

    book.parts = [dict(item) for item in proposal.parts]

    book.models = {
        key: dict(value)
        for key, value in proposal.models.items()
    }

    mapping: dict[str, str] = {}

    for proposed in proposal.pages:
        page = PageV4(
            page_type=proposed.page_type,
            title=proposed.title,
            origin=proposed.origin,
            source=proposed.source,
            part_id=proposed.part_key,
            model_id=proposed.model_key,
            recto_verso=proposed.recto_verso,
            spread_id=proposed.spread_key,
            spread_side=proposed.spread_side,
            is_compensation=proposed.is_compensation,
        )

        page.metadata["proposal_key"] = proposed.proposal_key
        page.metadata["proposal_id"] = proposal.id
        page.metadata["analysis_refs"] = list(
            proposed.analysis_refs
        )

        page.metadata["analysis_baseline"] = (
            proposed_page_baseline(proposed)
        )

        book.add_page(page)

        mapping[proposed.proposal_key] = page.id

    book.metadata["initial_proposal_id"] = proposal.id
    book.metadata["source_version_ids"] = list(
        proposal.source_version_ids
    )

    application = ProposalApplication(
        proposal_id=proposal.id,
        book_id=book.id,
        page_ids_by_proposal_key=mapping,
        applied_at=utc_now(),
    )

    book.history.append(
        {
            "action": "creation_depuis_proposition",
            "proposal_id": proposal.id,
            "date": application.applied_at,
        }
    )

    book.validate()

    return book, application
