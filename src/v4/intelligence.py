from __future__ import annotations

"""
TomeLinea V4 — contrat d'intelligence éditoriale.

Ce module ne contient aucune IA.

Il sépare :
- l'extraction factuelle déterministe ;
- les signaux dérivés produits par les moteurs TomeLinea ;
- la future intelligence éditoriale ;
- la mémoire d'analyse V4.

L'intelligence reçoit uniquement une photographie détachée.
Elle ne reçoit jamais SourceV4, BookV4 ou AnalysisV4 sous forme mutable.
"""

from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from src.v4.analysis import (
    AnalysisFinding,
    AnalysisV4,
    ConfidenceLevel,
)


FACT_KEY_PREFIX = "fact."
EDITORIAL_KEY_PREFIX = "editorial."
RATIONALE_EVIDENCE_PREFIX = "justification:"


def _fact_key(key: str) -> str:
    clean = str(key).strip()

    if not clean:
        raise ValueError(
            "Clé d'observation factuelle absente."
        )

    if clean.startswith(
        FACT_KEY_PREFIX
    ):
        return clean

    return (
        FACT_KEY_PREFIX
        + clean
    )


def _editorial_key(
    key: str,
) -> str:
    clean = str(key).strip()

    if not clean:
        raise ValueError(
            "Clé de proposition éditoriale absente."
        )

    if clean.startswith(
        FACT_KEY_PREFIX
    ):
        raise ValueError(
            "Une proposition éditoriale ne peut pas utiliser "
            "l'espace réservé aux faits."
        )

    return clean


@dataclass(
    frozen=True,
    slots=True,
)
class FactualObservation:
    """
    Photographie détachée d'un fait enregistré dans AnalysisV4.
    """

    finding_id: str
    target_type: str
    target_id: str
    key: str
    value: Any

    source_version_ids: tuple[
        str,
        ...
    ] = ()

    evidence: tuple[
        str,
        ...
    ] = ()

    created_at: str = ""


@dataclass(
    frozen=True,
    slots=True,
)
class AnalysisSignal:
    """
    Résultat dérivé d'un moteur TomeLinea.

    Exemple :
    - ressemblance de pages ;
    - appartenance à une famille ;
    - rôle noyau / variante.

    Ce n'est pas un fait brut de la Source.
    Ce n'est pas non plus une décision éditoriale finale.
    """

    finding_id: str

    target_type: str
    target_id: str

    key: str
    value: Any

    confidence: ConfidenceLevel

    engine: str
    engine_version: str

    source_version_ids: tuple[
        str,
        ...
    ] = ()

    evidence: tuple[
        str,
        ...
    ] = ()

    created_at: str = ""


@dataclass(
    frozen=True,
    slots=True,
)
class IntelligenceContext:
    """
    Contexte remis à l'intelligence éditoriale.

    observations :
        faits directement extraits de la Source.

    signals :
        résultats déterministes déjà calculés par TomeLinea.

    Aucun objet persistant mutable n'est transmis.
    """

    source_version_ids: tuple[
        str,
        ...
    ]

    observations: tuple[
        FactualObservation,
        ...
    ]

    signals: tuple[
        AnalysisSignal,
        ...
    ] = ()


@dataclass(
    frozen=True,
    slots=True,
)
class EditorialProposal:
    """
    Proposition produite par une intelligence éditoriale.
    """

    target_type: str
    target_id: str

    key: str
    value: Any

    confidence: ConfidenceLevel

    rationale: str = ""

    source_version_ids: tuple[
        str,
        ...
    ] = ()

    evidence: tuple[
        str,
        ...
    ] = ()

    def validate(
        self,
    ) -> None:

        if not self.target_type.strip():
            raise ValueError(
                "Type de cible absent."
            )

        if not self.target_id.strip():
            raise ValueError(
                "Identité de cible absente."
            )

        _editorial_key(
            self.key
        )


@runtime_checkable
class EditorialIntelligenceEngine(
    Protocol
):
    """
    Contrat stable de l'intelligence TomeLinea.

    Une implémentation pourra être :
    - un moteur de règles ;
    - une IA locale ;
    - plusieurs outils spécialisés.
    """

    engine_name: str
    engine_version: str

    def propose(
        self,
        context: IntelligenceContext,
    ) -> tuple[
        EditorialProposal,
        ...
    ]:
        ...


@dataclass(
    frozen=True,
    slots=True,
)
class NullEditorialIntelligence:
    """
    Moteur neutre sans IA.
    """

    engine_name: str = (
        "tomelinea.intelligence.none"
    )

    engine_version: str = "1"

    def propose(
        self,
        context: IntelligenceContext,
    ) -> tuple[
        EditorialProposal,
        ...
    ]:
        del context
        return ()


def record_fact(
    analysis: AnalysisV4,
    *,
    target_type: str,
    target_id: str,
    key: str,
    value: Any,
    engine: str,
    engine_version: str,
    source_version_ids: tuple[
        str,
        ...
    ] = (),
    evidence: tuple[
        str,
        ...
    ] = (),
) -> AnalysisFinding:
    """
    Enregistre un fait objectif extrait d'une Source.
    """

    return analysis.add_finding(
        target_type=target_type,
        target_id=target_id,
        key=_fact_key(key),
        value=deepcopy(
            value
        ),
        confidence=(
            ConfidenceLevel.SURE
        ),
        engine=str(
            engine
        ),
        engine_version=str(
            engine_version
        ),
        source_version_ids=tuple(
            str(item)
            for item
            in source_version_ids
        ),
        evidence=tuple(
            str(item)
            for item
            in evidence
        ),
    )


def _source_matches(
    finding: AnalysisFinding,
    requested: set[str],
) -> bool:
    if not requested:
        return True

    linked = set(
        finding.source_version_ids
    )

    if not linked:
        return True

    return not linked.isdisjoint(
        requested
    )


def build_intelligence_context(
    analysis: AnalysisV4,
    *,
    source_version_ids: tuple[
        str,
        ...
    ] = (),
) -> IntelligenceContext:
    """
    Produit une photographie détachée des informations utiles.

    Les conclusions éditoriales déjà produites sont volontairement
    exclues des signaux afin d'éviter qu'un moteur se nourrisse de
    ses propres anciennes réponses.

    En revanche, les résultats techniques intermédiaires tels que
    similarity.* sont transmis.
    """

    requested = {
        str(item)
        for item
        in source_version_ids
    }

    observations: list[
        FactualObservation
    ] = []

    signals: list[
        AnalysisSignal
    ] = []

    ordered_findings = sorted(
        analysis.findings.values(),
        key=lambda item: (
            item.created_at,
            item.id,
        ),
    )

    for finding in ordered_findings:

        if not _source_matches(
            finding,
            requested,
        ):
            continue

        # ------------------------------------------------------
        # Faits bruts
        # ------------------------------------------------------

        if finding.key.startswith(
            FACT_KEY_PREFIX
        ):
            observations.append(
                FactualObservation(
                    finding_id=(
                        finding.id
                    ),
                    target_type=(
                        finding.target_type
                    ),
                    target_id=(
                        finding.target_id
                    ),
                    key=finding.key[
                        len(
                            FACT_KEY_PREFIX
                        ):
                    ],
                    value=deepcopy(
                        finding.value
                    ),
                    source_version_ids=tuple(
                        finding.source_version_ids
                    ),
                    evidence=tuple(
                        finding.evidence
                    ),
                    created_at=(
                        finding.created_at
                    ),
                )
            )

            continue

        # ------------------------------------------------------
        # Les anciennes conclusions éditoriales ne sont pas
        # réinjectées comme preuves d'une nouvelle analyse.
        # ------------------------------------------------------

        if finding.key.startswith(
            EDITORIAL_KEY_PREFIX
        ):
            continue

        # ------------------------------------------------------
        # Signaux dérivés
        # ------------------------------------------------------

        signals.append(
            AnalysisSignal(
                finding_id=(
                    finding.id
                ),
                target_type=(
                    finding.target_type
                ),
                target_id=(
                    finding.target_id
                ),
                key=finding.key,
                value=deepcopy(
                    finding.value
                ),
                confidence=(
                    finding.confidence
                ),
                engine=(
                    finding.engine
                ),
                engine_version=(
                    finding.engine_version
                ),
                source_version_ids=tuple(
                    finding.source_version_ids
                ),
                evidence=tuple(
                    finding.evidence
                ),
                created_at=(
                    finding.created_at
                ),
            )
        )

    return IntelligenceContext(
        source_version_ids=tuple(
            str(item)
            for item
            in source_version_ids
        ),
        observations=tuple(
            observations
        ),
        signals=tuple(
            signals
        ),
    )


def record_editorial_proposal(
    analysis: AnalysisV4,
    *,
    proposal: EditorialProposal,
    engine: str,
    engine_version: str,
    default_source_version_ids: tuple[
        str,
        ...
    ] = (),
) -> AnalysisFinding:
    """
    Enregistre une proposition comme conclusion AnalysisV4 traçable.
    """

    proposal.validate()

    evidence = [
        str(item)
        for item
        in proposal.evidence
    ]

    if proposal.rationale.strip():
        evidence.insert(
            0,
            (
                RATIONALE_EVIDENCE_PREFIX
                + proposal.rationale.strip()
            ),
        )

    source_ids = (
        proposal.source_version_ids
        if proposal.source_version_ids
        else default_source_version_ids
    )

    return analysis.add_finding(
        target_type=(
            proposal.target_type
        ),
        target_id=(
            proposal.target_id
        ),
        key=_editorial_key(
            proposal.key
        ),
        value=deepcopy(
            proposal.value
        ),
        confidence=(
            proposal.confidence
        ),
        engine=str(
            engine
        ),
        engine_version=str(
            engine_version
        ),
        source_version_ids=tuple(
            str(item)
            for item
            in source_ids
        ),
        evidence=tuple(
            evidence
        ),
    )


def run_editorial_intelligence(
    analysis: AnalysisV4,
    engine: EditorialIntelligenceEngine,
    *,
    source_version_ids: tuple[
        str,
        ...
    ] = (),
) -> tuple[
    AnalysisFinding,
    ...
]:
    """
    Exécute l'intelligence contre un contexte détaché.

    Le moteur ne reçoit jamais AnalysisV4 lui-même.
    """

    context = (
        build_intelligence_context(
            analysis,
            source_version_ids=(
                source_version_ids
            ),
        )
    )

    proposals = tuple(
        engine.propose(
            context
        )
    )

    recorded: list[
        AnalysisFinding
    ] = []

    for proposal in proposals:
        recorded.append(
            record_editorial_proposal(
                analysis,
                proposal=proposal,
                engine=(
                    engine.engine_name
                ),
                engine_version=(
                    engine.engine_version
                ),
                default_source_version_ids=(
                    context.source_version_ids
                ),
            )
        )

    return tuple(
        recorded
    )


def proposal_rationale(
    finding: AnalysisFinding,
) -> str:
    """
    Retourne la justification d'une proposition enregistrée.
    """

    for item in finding.evidence:
        if item.startswith(
            RATIONALE_EVIDENCE_PREFIX
        ):
            return item[
                len(
                    RATIONALE_EVIDENCE_PREFIX
                ):
            ]

    return ""
