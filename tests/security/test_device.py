"""Tests de l’identité d’appareil PageMaître Security."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from src.security.device import (
    DeviceIdentity,
    _hash_material,
    get_device_identity,
)


class DeviceIdentityTests(unittest.TestCase):
    def test_machine_guid_is_converted_to_sha256_fingerprint(self) -> None:
        with patch(
            "src.security.device._read_windows_machine_guid",
            return_value="GUID-DE-TEST",
        ):
            identity = get_device_identity("fr.eqds.pagemaître")

        self.assertEqual(identity.source, "windows-machine-guid")
        self.assertEqual(len(identity.fingerprint), 64)
        self.assertNotIn("guid-de-test", identity.fingerprint.lower())

    def test_fallback_is_used_when_machine_guid_is_missing(self) -> None:
        with (
            patch(
                "src.security.device._read_windows_machine_guid",
                return_value=None,
            ),
            patch(
                "src.security.device._build_fallback_material",
                return_value="materiau-de-secours",
            ),
        ):
            identity = get_device_identity("fr.eqds.pagemaître")

        self.assertEqual(identity.source, "system-fallback")
        self.assertEqual(len(identity.fingerprint), 64)

    def test_same_material_produces_same_fingerprint(self) -> None:
        first = _hash_material(
            "fr.eqds.pagemaître",
            "test-source",
            "MATERIAU-IDENTIQUE",
        )
        second = _hash_material(
            "fr.eqds.pagemaître",
            "test-source",
            "materiau-identique",
        )

        self.assertEqual(first, second)

    def test_application_id_changes_fingerprint(self) -> None:
        first = _hash_material(
            "fr.eqds.pagemaître",
            "test-source",
            "materiau-identique",
        )
        second = _hash_material(
            "fr.eqds.autre-produit",
            "test-source",
            "materiau-identique",
        )

        self.assertNotEqual(first, second)

    def test_empty_application_id_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            get_device_identity("   ")

    def test_invalid_fingerprint_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            DeviceIdentity(
                fingerprint="empreinte-invalide",
                source="test",
            )


if __name__ == "__main__":
    unittest.main()