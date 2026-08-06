"""Orchestration des contrôles PageMaître Security.

Le gestionnaire centralise l’exécution des futurs contrôles de sécurité.
Lorsque la sécurité est désactivée, aucun contrôle n’est exécuté et aucun
blocage de PageMaître n’est possible.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Protocol, runtime_checkable

from src.security.config import SecurityConfig, SecurityMode
from src.security.status import (
    SecurityCheckResult,
    SecurityCheckState,
    SecurityReport,
    SecuritySeverity,
)


@runtime_checkable
class SecurityCheck(Protocol):
    """Contrat commun à tous les futurs contrôles de sécurité."""

    check_id: str

    def run(self, config: SecurityConfig) -> SecurityCheckResult:
        """Exécute le contrôle et retourne son résultat."""


@dataclass(slots=True)
class SecurityManager:
    """Exécute les contrôles enregistrés selon le mode de sécurité."""

    config: SecurityConfig
    checks: tuple[SecurityCheck, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        self.config.validate()

        identifiers: set[str] = set()
        for check in self.checks:
            check_id = getattr(check, "check_id", "").strip()

            if not check_id:
                raise ValueError(
                    "Chaque contrôle de sécurité doit posséder un check_id."
                )

            if check_id in identifiers:
                raise ValueError(
                    f"Le contrôle de sécurité {check_id!r} est enregistré deux fois."
                )

            identifiers.add(check_id)

    def run_startup_checks(self) -> SecurityReport:
        """Exécute les contrôles prévus au démarrage de PageMaître."""

        if not self.config.is_enabled:
            return SecurityReport.from_results(
                self._skipped_result(check)
                for check in self.checks
            )

        results: list[SecurityCheckResult] = []

        for check in self.checks:
            try:
                result = check.run(self.config)
                results.append(self._validate_result(check, result))
            except Exception as error:
                results.append(self._error_result(check, error))

        return SecurityReport.from_results(results)

    @staticmethod
    def _skipped_result(check: SecurityCheck) -> SecurityCheckResult:
        return SecurityCheckResult(
            check_id=check.check_id,
            state=SecurityCheckState.SKIPPED,
            message="Contrôle désactivé dans la configuration actuelle.",
            severity=SecuritySeverity.INFORMATION,
        )

    @staticmethod
    def _validate_result(
        check: SecurityCheck,
        result: SecurityCheckResult,
    ) -> SecurityCheckResult:
        if result.check_id != check.check_id:
            raise ValueError(
                "Le résultat d’un contrôle doit conserver son check_id."
            )

        return result

    def _error_result(
        self,
        check: SecurityCheck,
        error: Exception,
    ) -> SecurityCheckResult:
        severity = (
            SecuritySeverity.BLOCKING
            if self.config.mode is SecurityMode.ENFORCED
            else SecuritySeverity.WARNING
        )

        return SecurityCheckResult(
            check_id=check.check_id,
            state=SecurityCheckState.FAILED,
            message="Le contrôle de sécurité n’a pas pu être exécuté.",
            severity=severity,
            technical_details=f"{type(error).__name__}: {error}",
        )