from __future__ import annotations

"""
TomeLinea V4 — modèle des résultats d'analyse.

Cette couche décrit ce que TomeLinea comprend des Sources.
Elle ne modifie ni la Source originale ni directement le Livre.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


def new_id() -> str:
    return str(uuid4())


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class ConfidenceLevel(str, Enum):
    SURE = "sur"
    PROBABLE = "probable"
    REVIEW = "a_verifier"


class DecisionOrigin(str, Enum):
    AUTOMATIC = "automatique"
    HUMAN = "humaine"


@dataclass(frozen=True, slots=True)
class AnalysisFinding:
    """
    Conclusion produite par un moteur d'analyse.

    target_type :
        source, page_source, livre, groupe, modele, etc.

    key :
        nom logique de la conclusion, par exemple :
        type_livre, type_page, double_page, titre, chapitre...
    """

    id: str
    target_type: str
    target_id: str
    key: str
    value: Any

    confidence: ConfidenceLevel
    engine: str
    engine_version: str

    source_version_ids: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()

    created_at: str = field(default_factory=utc_now)


@dataclass(frozen=True, slots=True)
class HumanDecision:
    """
    Décision explicite de l'utilisateur.

    Elle est prioritaire sur une conclusion automatique de même cible/clé.
    """

    id: str
    target_type: str
    target_id: str
    key: str
    value: Any

    created_at: str = field(default_factory=utc_now)


@dataclass(slots=True)
class AnalysisV4:
    """
    Mémoire centrale des analyses V4.

    Les résultats automatiques restent conservés même lorsqu'une
    décision humaine les remplace.
    """

    findings: dict[str, AnalysisFinding] = field(default_factory=dict)

    human_decisions: dict[
        tuple[str, str, str],
        HumanDecision
    ] = field(default_factory=dict)

    analyzed_source_versions: dict[str, str] = field(default_factory=dict)

    dirty_dependencies: set[str] = field(default_factory=set)

    def add_finding(
        self,
        *,
        target_type: str,
        target_id: str,
        key: str,
        value: Any,
        confidence: ConfidenceLevel,
        engine: str,
        engine_version: str,
        source_version_ids: tuple[str, ...] = (),
        evidence: tuple[str, ...] = (),
    ) -> AnalysisFinding:

        finding = AnalysisFinding(
            id=new_id(),
            target_type=target_type,
            target_id=target_id,
            key=key,
            value=value,
            confidence=confidence,
            engine=engine,
            engine_version=engine_version,
            source_version_ids=source_version_ids,
            evidence=evidence,
        )

        self.findings[finding.id] = finding
        return finding

    def set_human_decision(
        self,
        *,
        target_type: str,
        target_id: str,
        key: str,
        value: Any,
    ) -> HumanDecision:

        decision = HumanDecision(
            id=new_id(),
            target_type=target_type,
            target_id=target_id,
            key=key,
            value=value,
        )

        lookup = (target_type, target_id, key)
        self.human_decisions[lookup] = decision

        return decision

    def effective_value(
        self,
        *,
        target_type: str,
        target_id: str,
        key: str,
    ) -> Any:
        """
        Retourne la décision réellement applicable.

        Priorité :
        1. correction humaine ;
        2. conclusion automatique la plus récente ;
        3. None.
        """

        lookup = (target_type, target_id, key)

        human = self.human_decisions.get(lookup)
        if human is not None:
            return human.value

        matches = [
            finding
            for finding in self.findings.values()
            if finding.target_type == target_type
            and finding.target_id == target_id
            and finding.key == key
        ]

        if not matches:
            return None

        matches.sort(key=lambda item: item.created_at)
        return matches[-1].value

    def mark_source_version_analyzed(
        self,
        source_version_id: str,
        fingerprint: str,
    ) -> None:
        self.analyzed_source_versions[source_version_id] = fingerprint

    def source_version_needs_analysis(
        self,
        source_version_id: str,
        fingerprint: str,
    ) -> bool:
        return (
            self.analyzed_source_versions.get(source_version_id)
            != fingerprint
        )

    def invalidate(self, *dependencies: str) -> None:
        self.dirty_dependencies.update(dependencies)

    def clear_invalidation(self, *dependencies: str) -> None:
        for dependency in dependencies:
            self.dirty_dependencies.discard(dependency)

    def validate(self) -> None:
        for finding_id, finding in self.findings.items():
            if finding.id != finding_id:
                raise ValueError(
                    f"Incohérence d'identité Analyse : {finding_id}"
                )

        for lookup, decision in self.human_decisions.items():
            expected = (
                decision.target_type,
                decision.target_id,
                decision.key,
            )

            if lookup != expected:
                raise ValueError(
                    f"Incohérence de décision humaine : {lookup}"
                )
