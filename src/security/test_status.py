"""Tests des résultats PageMaître Security."""

from __future__ import annotations

import unittest

from src.security.status import (
    SecurityCheckResult,
    SecurityCheckState,
    SecurityReport,
    SecuritySeverity,
)


class SecurityStatusTests(unittest.TestCase):
    def test_passed_result_is_not_blocking(self) -> None:
        result = SecurityCheckResult(
            check_id="configuration",
            state=SecurityCheckState.PASSED,
            message="Configuration valide.",
        )

        self.assertTrue(result.is_success)
        self.assertFalse(result.is_failure)
        self.assertFalse(result.is_blocking)

    def test_blocking_failure_blocks_application_start(self) -> None:
        result = SecurityCheckResult(
            check_id="licence",
            state=SecurityCheckState.FAILED,
            message="Licence invalide.",
            severity=SecuritySeverity.BLOCKING,
        )
        report = SecurityReport.from_results([result])

        self.assertTrue(report.has_failures)
        self.assertTrue(report.has_blocking_failure)
        self.assertFalse(report.can_start_application)

    def test_warning_failure_does_not_block_application_start(self) -> None:
        result = SecurityCheckResult(
            check_id="integrite",
            state=SecurityCheckState.FAILED,
            message="Contrôle d’intégrité incomplet.",
            severity=SecuritySeverity.WARNING,
        )
        report = SecurityReport.from_results([result])

        self.assertTrue(report.has_failures)
        self.assertFalse(report.has_blocking_failure)
        self.assertTrue(report.can_start_application)

    def test_report_counts_each_state(self) -> None:
        report = SecurityReport.from_results(
            [
                SecurityCheckResult(
                    check_id="configuration",
                    state=SecurityCheckState.PASSED,
                    message="Configuration valide.",
                ),
                SecurityCheckResult(
                    check_id="licence",
                    state=SecurityCheckState.FAILED,
                    message="Licence absente.",
                    severity=SecuritySeverity.WARNING,
                ),
                SecurityCheckResult(
                    check_id="appareil",
                    state=SecurityCheckState.SKIPPED,
                    message="Contrôle désactivé.",
                ),
            ]
        )

        self.assertEqual(report.passed_count, 1)
        self.assertEqual(report.failed_count, 1)
        self.assertEqual(report.skipped_count, 1)

    def test_empty_identifier_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            SecurityCheckResult(
                check_id=" ",
                state=SecurityCheckState.PASSED,
                message="Résultat valide.",
            )

    def test_passed_result_cannot_be_blocking(self) -> None:
        with self.assertRaises(ValueError):
            SecurityCheckResult(
                check_id="configuration",
                state=SecurityCheckState.PASSED,
                message="Configuration valide.",
                severity=SecuritySeverity.BLOCKING,
            )


if __name__ == "__main__":
    unittest.main()