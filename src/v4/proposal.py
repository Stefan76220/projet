from __future__ import annotations

"""
TomeLinea V4 — contrat entre Analyse et Livre.

L'Analyse propose.
Le Livre constitue l'état réellement retenu du projet.

Les identités internes du Livre ne sont jamais les clés temporaires
de l'Analyse :
- proposal_key identifie une page proposée ;
- part_key identifie une partie proposée ;
- PageV4.id et PartV4.id sont les identités permanentes du Livre.
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
    PartV4,
    SourceLink,
)


def new_id() -> str:
    return str(uuid4())


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass(frozen=True, slots=True)
class ProposedPart:
    """
    Partie proposée par l'Analyse.

    proposal_key est une identité d'analyse.
    Elle ne devient jamais directement PartV4.id.
    """

    proposal_key: str

    title: str = ""
    part_type: str = "partie"

    parent_key: str | None = None

    analysis_refs: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ProposedPage:
    """
    Page proposée par l'Analyse.

    proposal_key permet de retrouver l'élément logique au cours
    des réanalyses.

    part_key référence ProposedPart.proposal_key.
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
    code: str
    message: str

    target_key: str | None = None
    severity: str = "a_verifier"


@dataclass(slots=True)
class BookProposal:
    """
    Photographie complète d'une proposition calculée par l'Analyse.
    """

    id: str = field(default_factory=new_id)
    created_at: str = field(default_factory=utc_now)

    suggested_kind: BookKind = BookKind.UNKNOWN

    source_version_ids: tuple[str, ...] = ()

    parts: list[ProposedPart] = field(
        default_factory=list
    )

    pages: list[ProposedPage] = field(
        default_factory=list
    )

    models: dict[str, dict[str, Any]] = field(
        default_factory=dict
    )

    issues: list[ProposalIssue] = field(
        default_factory=list
    )

    analysis_refs: tuple[str, ...] = ()

    def add_part(
        self,
        part: ProposedPart,
    ) -> None:

        if any(
            existing.proposal_key == part.proposal_key
            for existing in self.parts
        ):
            raise ValueError(
                "Clé de partie proposée dupliquée : "
                f"{part.proposal_key}"
            )

        self.parts.append(part)

    def add_page(
        self,
        page: ProposedPage,
    ) -> None:

        if any(
            existing.proposal_key == page.proposal_key
            for existing in self.pages
        ):
            raise ValueError(
                "Clé de page proposée dupliquée : "
                f"{page.proposal_key}"
            )

        self.pages.append(page)

    def validate(self) -> None:
        # ------------------------------------------------------
        # Parties
        # ------------------------------------------------------

        part_keys = [
            part.proposal_key
            for part in self.parts
        ]

        if len(part_keys) != len(set(part_keys)):
            raise ValueError(
                "Une clé de partie apparaît plusieurs fois "
                "dans la proposition."
            )

        known_part_keys = set(part_keys)

        parent_by_key = {
            part.proposal_key: part.parent_key
            for part in self.parts
        }

        for part in self.parts:
            if (
                part.parent_key is not None
                and part.parent_key not in known_part_keys
            ):
                raise ValueError(
                    f"Partie parente inconnue pour "
                    f"{part.proposal_key} : {part.parent_key}"
                )

            if part.parent_key == part.proposal_key:
                raise ValueError(
                    "Une partie proposée ne peut pas "
                    "être sa propre parente."
                )

        # Détection des cycles hiérarchiques.
        for start_key in part_keys:
            seen: set[str] = set()
            current: str | None = start_key

            while current is not None:
                if current in seen:
                    raise ValueError(
                        "Cycle détecté dans la hiérarchie "
                        f"des parties autour de {start_key}."
                    )

                seen.add(current)
                current = parent_by_key.get(current)

        # ------------------------------------------------------
        # Pages
        # ------------------------------------------------------

        page_keys = [
            page.proposal_key
            for page in self.pages
        ]

        if len(page_keys) != len(set(page_keys)):
            raise ValueError(
                "Une clé de page apparaît plusieurs fois "
                "dans la proposition."
            )

        for page in self.pages:
            if (
                page.part_key is not None
                and page.part_key not in known_part_keys
            ):
                raise ValueError(
                    f"Partie proposée inconnue pour "
                    f"{page.proposal_key} : {page.part_key}"
                )

            if page.source is not None:
                if not page.source.source_id:
                    raise ValueError(
                        f"Source absente pour {page.proposal_key}"
                    )

                if not page.source.source_version_id:
                    raise ValueError(
                        "Version Source absente pour "
                        f"{page.proposal_key}"
                    )


@dataclass(frozen=True, slots=True)
class ProposalApplication:
    """
    Trace précise du passage Proposition -> Livre.
    """

    proposal_id: str
    book_id: str

    page_ids_by_proposal_key: dict[str, str]
    part_ids_by_proposal_key: dict[str, str]

    applied_at: str


def proposal_order_keys(
    proposal: BookProposal,
) -> list[str]:

    return [
        page.proposal_key
        for page in proposal.pages
    ]


def proposal_part_order_keys(
    proposal: BookProposal,
) -> list[str]:

    return [
        part.proposal_key
        for part in proposal.parts
    ]


def book_order_keys(
    book: BookV4,
) -> list[str]:
    """
    Ordre des pages provenant de l'Analyse.

    Les pages manuelles sont volontairement ignorées ici.
    """

    result: list[str] = []

    for page in book.ordered_pages():
        proposal_key = page.metadata.get(
            "proposal_key"
        )

        if proposal_key is not None:
            result.append(
                str(proposal_key)
            )

    return result


def book_part_order_keys(
    book: BookV4,
) -> list[str]:
    """
    Ordre des parties provenant de l'Analyse.

    Les parties créées manuellement seront distinguées de la même
    manière que les pages manuelles.
    """

    result: list[str] = []

    for part in book.ordered_parts():
        proposal_key = part.metadata.get(
            "proposal_key"
        )

        if proposal_key is not None:
            result.append(
                str(proposal_key)
            )

    return result


def proposed_part_baseline(
    proposed: ProposedPart,
) -> dict[str, Any]:
    """
    État automatique initial d'une partie.

    parent_key reste ici une clé d'Analyse afin de pouvoir comparer
    les propositions successives indépendamment des UUID du Livre.
    """

    return {
        "title": proposed.title,
        "part_type": proposed.part_type,
        "parent_key": proposed.parent_key,
    }


def proposed_page_baseline(
    proposed: ProposedPage,
    *,
    resolved_part_id: str | None = None,
) -> dict[str, Any]:
    """
    Valeurs automatiques ayant servi à créer une PageV4.

    Lors de la création du Livre, resolved_part_id contient le vrai
    PartV4.id.

    Sans résolution explicite, la fonction conserve le comportement
    nécessaire aux comparaisons de proposition. La réanalyse sera
    raccordée à la résolution des parties à l'étape suivante.
    """

    source = None

    if proposed.source is not None:
        source = {
            "source_id": proposed.source.source_id,
            "source_version_id": (
                proposed.source.source_version_id
            ),
            "source_page": proposed.source.source_page,
        }

    part_value = resolved_part_id

    if (
        part_value is None
        and proposed.part_key is not None
    ):
        part_value = proposed.part_key

    return {
        "page_type": proposed.page_type,
        "title": proposed.title,
        "origin": proposed.origin.value,
        "source": source,
        "part_id": part_value,
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
    Crée un nouveau LivreV4.

    Les clés de proposition sont transformées en identités permanentes.
    """

    proposal.validate()

    book = BookV4(
        title=title,
        kind=proposal.suggested_kind,
    )

    # ==========================================================
    # Parties
    # ==========================================================

    part_mapping: dict[str, str] = {}

    # Premier passage :
    # toutes les parties existent avant de construire la hiérarchie.
    for proposed_part in proposal.parts:
        part = PartV4(
            title=proposed_part.title,
            part_type=proposed_part.part_type,
        )

        part.metadata["proposal_key"] = (
            proposed_part.proposal_key
        )

        part.metadata["proposal_id"] = (
            proposal.id
        )

        part.metadata["analysis_refs"] = list(
            proposed_part.analysis_refs
        )

        part.metadata["analysis_baseline"] = (
            proposed_part_baseline(
                proposed_part
            )
        )

        book.add_part(part)

        part_mapping[
            proposed_part.proposal_key
        ] = part.id

    # Second passage :
    # conversion parent_key -> vrai UUID.
    for proposed_part in proposal.parts:
        if proposed_part.parent_key is None:
            continue

        part_id = part_mapping[
            proposed_part.proposal_key
        ]

        parent_id = part_mapping[
            proposed_part.parent_key
        ]

        book.parts[
            part_id
        ].parent_id = parent_id

    # ==========================================================
    # Pages
    # ==========================================================

    page_mapping: dict[str, str] = {}

    for proposed in proposal.pages:
        resolved_part_id: str | None = None

        if proposed.part_key is not None:
            resolved_part_id = part_mapping[
                proposed.part_key
            ]

        page = PageV4(
            page_type=proposed.page_type,
            title=proposed.title,
            origin=proposed.origin,
            source=proposed.source,
            part_id=resolved_part_id,
            model_id=proposed.model_key,
            recto_verso=proposed.recto_verso,
            spread_id=proposed.spread_key,
            spread_side=proposed.spread_side,
            is_compensation=(
                proposed.is_compensation
            ),
        )

        page.metadata["proposal_key"] = (
            proposed.proposal_key
        )

        page.metadata["proposal_id"] = (
            proposal.id
        )

        page.metadata["analysis_refs"] = list(
            proposed.analysis_refs
        )

        page.metadata["analysis_baseline"] = (
            proposed_page_baseline(
                proposed,
                resolved_part_id=resolved_part_id,
            )
        )

        book.add_page(page)

        page_mapping[
            proposed.proposal_key
        ] = page.id

    # ==========================================================
    # Modèles et métadonnées
    # ==========================================================

    book.models = {
        key: dict(value)
        for key, value in proposal.models.items()
    }

    book.metadata["initial_proposal_id"] = (
        proposal.id
    )

    book.metadata["source_version_ids"] = list(
        proposal.source_version_ids
    )

    book.metadata["analysis_order_baseline"] = (
        proposal_order_keys(proposal)
    )

    book.metadata[
        "analysis_part_order_baseline"
    ] = proposal_part_order_keys(
        proposal
    )

    application = ProposalApplication(
        proposal_id=proposal.id,
        book_id=book.id,
        page_ids_by_proposal_key=page_mapping,
        part_ids_by_proposal_key=part_mapping,
        applied_at=utc_now(),
    )

    book.history.append(
        {
            "action": "creation_depuis_proposition",
            "proposal_id": proposal.id,
            "pages_created": len(page_mapping),
            "parts_created": len(part_mapping),
            "date": application.applied_at,
        }
    )

    book.validate()

    return book, application
