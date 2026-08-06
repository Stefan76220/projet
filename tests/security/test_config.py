"""Tests de la configuration PageMaître Security."""

from __future__ import annotations

import os
import unittest
from unittest.mock import patch

from src.security.config import SecurityConfig, SecurityMode


class SecurityConfigTests(unittest.TestCase):
    def test_default_security_is_disabled(self) -> None:
        config = SecurityConfig()

        self.assertEqual(config.mode, SecurityMode.DISABLED)
        self.assertFalse(config.is_enabled)
        self.assertFalse(config.is_enforced)

    def test_development_mode_is_enabled_but_not_enforced(self) -> None:
        config = SecurityConfig(mode=SecurityMode.DEVELOPMENT)

        self.assertTrue(config.is_enabled)
        self.assertFalse(config.is_enforced)

    def test_enforced_mode_is_enabled_and_enforced(self) -> None:
        config = SecurityConfig(mode=SecurityMode.ENFORCED)

        self.assertTrue(config.is_enabled)
        self.assertTrue(config.is_enforced)

    def test_environment_can_enable_development_mode(self) -> None:
        with patch.dict(
            os.environ,
            {"PAGEMAITRE_SECURITY_MODE": "development"},
            clear=False,
        ):
            config = SecurityConfig.from_environment()

        self.assertEqual(config.mode, SecurityMode.DEVELOPMENT)

    def test_invalid_environment_value_keeps_security_disabled(self) -> None:
        with patch.dict(
            os.environ,
            {"PAGEMAITRE_SECURITY_MODE": "valeur-inconnue"},
            clear=False,
        ):
            config = SecurityConfig.from_environment()

        self.assertEqual(config.mode, SecurityMode.DISABLED)

    def test_invalid_device_limit_is_rejected(self) -> None:
        config = SecurityConfig(maximum_authorized_devices=0)

        with self.assertRaises(ValueError):
            config.validate()


if __name__ == "__main__":
    unittest.main()