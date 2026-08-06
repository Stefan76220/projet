"""Résultats communs des contrôles PageMaître Security.

Ce module définit uniquement les états et rapports utilisés par les futurs
contrôles de licence, d’intégrité, d’appareil et de verrouillage.
Il ne bloque pas encore l’application.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Iterable


class SecuritySeverity(str, Enum):
    """Importance d’un résultat de sécurité."""

    INFORMATION = "information"
    WARNING = "warning"
    BLOCKING = "blocking"


class SecurityCheckState(str, Enum):
    """État produit par un contrôle de sécurité."""

    PASSED = "passed"
    SKIPPED = "skipped"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class SecurityCheckResult:
    """Résultat d’un contrôle de sécurité individuel."""

    check_id: str
    state: SecurityCheckState
    message: str
    severity: SecuritySeverity = SecuritySeverity.INFORMATION
    technical_details: str | None = None

    def __post_init__(self) -> None:
        if not self.check_id.strip():
            raise ValueError("check_id ne peut pas être vide.")

        if not self.message.strip():
            raise ValueError("message ne peut pas être vide.")

        if (
            self.state is SecurityCheckState.PASSED
            and self.severity is SecuritySeverity.BLOCKING
        ):
            raise ValueError(
                "Un contrôle réussi ne peut pas avoir une gravité bloquante."
            )

    @property
    def is_success(self) -> bool:
        """Indique si le contrôle est réussi."""

        return self.state is SecurityCheckState.PASSED

    @property
    def is_failure(self) -> bool:
        """Indique si le contrôle a échoué."""

        return self.state is SecurityCheckState.FAILED

    @property
    def is_blocking(self) -> bool:
        """Indique si le résultat doit pouvoir bloquer PageMaître."""

        return (
            self.state is SecurityCheckState.FAILED
            and self.severity is SecuritySeverity.BLOCKING
        )


@dataclass(frozen=True, slots=True)
class SecurityReport:
    """Synthèse immutable de plusieurs contrôles de sécurité."""

    results: tuple[SecurityCheckResult, ...] = field(default_factory=tuple)

    @classmethod
    def from_results(
        cls,
        results: Iterable[SecurityCheckResult],
    ) -> "SecurityReport":
        """Construit un rapport à partir de résultats successifs."""

        return cls(results=tuple(results))

    @property
    def has_failures(self) -> bool:
        """Indique si au moins un contrôle a échoué."""

        return any(result.is_failure for result in self.results)

    @property
    def has_blocking_failure(self) -> bool:
        """Indique si au moins un échec est bloquant."""

        return any(result.is_blocking for result in self.results)

    @property
    def passed_count(self) -> int:
        """Nombre de contrôles réussis."""

        return sum(result.is_success for result in self.results)

    @property
    def failed_count(self) -> int:
        """Nombre de contrôles échoués."""

        return sum(result.is_failure for result in self.results)

    @property
    def skipped_count(self) -> int:
        """Nombre de contrôles ignorés volontairement."""

        return sum(
            result.state is SecurityCheckState.SKIPPED
            for result in self.results
        )

    @property
    def can_start_application(self) -> bool:
        """Autorise le démarrage tant qu’aucun échec bloquant n’existe."""

        return not self.has_blocking_failure

    def blocking_results(self) -> tuple[SecurityCheckResult, ...]:
        """Retourne uniquement les résultats bloquants."""

        return tuple(result for result in self.results if result.is_blocking)