"""Tests du gestionnaire PageMaître Security."""

from __future__ import annotations

import unittest
from dataclasses import dataclass

from src.security.config import SecurityConfig, SecurityMode
from src.security.manager import SecurityManager
from src.security.status import (
    SecurityCheckResult,
    SecurityCheckState,
    SecuritySeverity,
)


@dataclass
class SuccessfulCheck:
    check_id: str = "controle-reussi"
    run_count: int = 0

    def run(self, config: SecurityConfig) -> SecurityCheckResult:
        self.run_count += 1
        return SecurityCheckResult(
            check_id=self.check_id,
            state=SecurityCheckState.PASSED,
            message="Contrôle réussi.",
        )


@dataclass
class FailingCheck:
    check_id: str = "controle-erreur"
    run_count: int = 0

    def run(self, config: SecurityConfig) -> SecurityCheckResult:
        self.run_count += 1
        raise RuntimeError("Erreur simulée.")


@dataclass
class InvalidIdentifierCheck:
    check_id: str = "controle-identifiant"

    def run(self, config: SecurityConfig) -> SecurityCheckResult:
        return SecurityCheckResult(
            check_id="autre-identifiant",
            state=SecurityCheckState.PASSED,
            message="Résultat incohérent.",
        )


class SecurityManagerTests(unittest.TestCase):
    def test_disabled_mode_skips_checks_without_running_them(self) -> None:
        check = SuccessfulCheck()
        manager = SecurityManager(
            config=SecurityConfig(mode=SecurityMode.DISABLED),
            checks=(check,),
        )

        report = manager.run_startup_checks()

        self.assertEqual(check.run_count, 0)
        self.assertEqual(report.skipped_count, 1)
        self.assertTrue(report.can_start_application)

    def test_development_mode_runs_successful_check(self) -> None:
        check = SuccessfulCheck()
        manager = SecurityManager(
            config=SecurityConfig(mode=SecurityMode.DEVELOPMENT),
            checks=(check,),
        )

        report = manager.run_startup_checks()

        self.assertEqual(check.run_count, 1)
        self.assertEqual(report.passed_count, 1)
        self.assertTrue(report.can_start_application)

    def test_development_error_is_warning_only(self) -> None:
        check = FailingCheck()
        manager = SecurityManager(
            config=SecurityConfig(mode=SecurityMode.DEVELOPMENT),
            checks=(check,),
        )

        report = manager.run_startup_checks()
        result = report.results[0]

        self.assertTrue(result.is_failure)
        self.assertEqual(result.severity, SecuritySeverity.WARNING)
        self.assertTrue(report.can_start_application)

    def test_enforced_error_is_blocking(self) -> None:
        check = FailingCheck()
        manager = SecurityManager(
            config=SecurityConfig(mode=SecurityMode.ENFORCED),
            checks=(check,),
        )

        report = manager.run_startup_checks()
        result = report.results[0]

        self.assertTrue(result.is_blocking)
        self.assertFalse(report.can_start_application)

    def test_duplicate_check_identifier_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            SecurityManager(
                config=SecurityConfig(),
                checks=(SuccessfulCheck(), SuccessfulCheck()),
            )

    def test_result_identifier_mismatch_becomes_warning_in_development(self) -> None:
        manager = SecurityManager(
            config=SecurityConfig(mode=SecurityMode.DEVELOPMENT),
            checks=(InvalidIdentifierCheck(),),
        )

        report = manager.run_startup_checks()
        result = report.results[0]

        self.assertTrue(result.is_failure)
        self.assertEqual(result.severity, SecuritySeverity.WARNING)
        self.assertIn("ValueError", result.technical_details or "")


if __name__ == "__main__":
    unittest.main()