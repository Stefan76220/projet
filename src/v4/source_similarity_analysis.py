from __future__ import annotations

"""
TomeLinea V4 — enregistrement des ressemblances dans AnalysisV4.

Le moteur source_similarity calcule.
Ce module conserve ses résultats comme conclusions traçables.

Aucune modification de SourceV4 ou BookV4.
Aucune IA.
"""

from dataclasses import dataclass

from src.v4.analysis import (
    AnalysisFinding,
    AnalysisV4,
    ConfidenceLevel,
)
from src.v4.source import SourceVersion
from src.v4.source_similarity import (
    PageFamilyCandidate,
    PageSimilarityRelation,
    compare_source_pages,
    detect_page_families,
)


ENGINE_NAME = "tomelinea.source_similarity"
ENGINE_VERSION = "1"


@dataclass(frozen=True, slots=True)
class SimilarityAnalysisSummary:
    relations: tuple[PageSimilarityRelation, ...]
    families: tuple[PageFamilyCandidate, ...]
    finding_ids: tuple[str, ...]


def _page_target(
    version: SourceVersion,
    page_number: int,
) -> str:
    return (
        f"{version.id}:page:{page_number}"
    )


def _pair_target(
    version: SourceVersion,
    left: int,
    right: int,
) -> str:
    return (
        f"{version.id}:pair:"
        f"{left}-{right}"
    )


def _family_target(
    version: SourceVersion,
    pages: tuple[int, ...],
) -> str:
    members = "-".join(
        str(page)
        for page in pages
    )

    return (
        f"{version.id}:family:{members}"
    )


def analyze_source_similarity(
    analysis: AnalysisV4,
    version: SourceVersion,
) -> SimilarityAnalysisSummary:
    """
    Calcule puis mémorise les ressemblances d'une version Source.
    """

    relations = compare_source_pages(
        analysis,
        version,
    )

    families = detect_page_families(
        relations
    )

    recorded: list[
        AnalysisFinding
    ] = []

    source_ids = (
        version.id,
    )

    # ----------------------------------------------------------
    # Relations entre deux pages
    # ----------------------------------------------------------

    for relation in relations:
        target_id = _pair_target(
            version,
            relation.page_a,
            relation.page_b,
        )

        evidence = (
            _page_target(
                version,
                relation.page_a,
            ),
            _page_target(
                version,
                relation.page_b,
            ),
        )

        recorded.append(
            analysis.add_finding(
                target_type="source_page_pair",
                target_id=target_id,
                key="similarity.score",
                value=relation.score,
                confidence=(
                    ConfidenceLevel.SURE
                ),
                engine=ENGINE_NAME,
                engine_version=ENGINE_VERSION,
                source_version_ids=source_ids,
                evidence=evidence,
            )
        )

        recorded.append(
            analysis.add_finding(
                target_type="source_page_pair",
                target_id=target_id,
                key="similarity.relation",
                value=relation.relation,
                confidence=(
                    ConfidenceLevel.PROBABLE
                ),
                engine=ENGINE_NAME,
                engine_version=ENGINE_VERSION,
                source_version_ids=source_ids,
                evidence=evidence,
            )
        )

    # ----------------------------------------------------------
    # Familles
    # ----------------------------------------------------------

    for family in families:
        family_id = _family_target(
            version,
            family.pages,
        )

        evidence = tuple(
            _page_target(
                version,
                page,
            )
            for page in family.pages
        )

        for key, value in (
            (
                "family.pages",
                list(family.pages),
            ),
            (
                "family.core_pages",
                list(
                    family.core_pages
                ),
            ),
            (
                "family.variant_pages",
                list(
                    family.variant_pages
                ),
            ),
        ):
            recorded.append(
                analysis.add_finding(
                    target_type=(
                        "source_page_family"
                    ),
                    target_id=family_id,
                    key=key,
                    value=value,
                    confidence=(
                        ConfidenceLevel.PROBABLE
                    ),
                    engine=ENGINE_NAME,
                    engine_version=(
                        ENGINE_VERSION
                    ),
                    source_version_ids=(
                        source_ids
                    ),
                    evidence=evidence,
                )
            )

        # ------------------------------------------------------
        # Chaque page connaît aussi son appartenance.
        # ------------------------------------------------------

        for page in family.pages:
            page_target = _page_target(
                version,
                page,
            )

            role = (
                "noyau"
                if page
                in family.core_pages
                else "variante"
            )

            recorded.append(
                analysis.add_finding(
                    target_type="source_page",
                    target_id=page_target,
                    key=(
                        "similarity.family_id"
                    ),
                    value=family_id,
                    confidence=(
                        ConfidenceLevel.PROBABLE
                    ),
                    engine=ENGINE_NAME,
                    engine_version=(
                        ENGINE_VERSION
                    ),
                    source_version_ids=(
                        source_ids
                    ),
                    evidence=evidence,
                )
            )

            recorded.append(
                analysis.add_finding(
                    target_type="source_page",
                    target_id=page_target,
                    key=(
                        "similarity.family_role"
                    ),
                    value=role,
                    confidence=(
                        ConfidenceLevel.PROBABLE
                    ),
                    engine=ENGINE_NAME,
                    engine_version=(
                        ENGINE_VERSION
                    ),
                    source_version_ids=(
                        source_ids
                    ),
                    evidence=evidence,
                )
            )

    return SimilarityAnalysisSummary(
        relations=relations,
        families=families,
        finding_ids=tuple(
            finding.id
            for finding in recorded
        ),
    )
