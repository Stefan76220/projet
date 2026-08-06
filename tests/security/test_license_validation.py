"""Tests de validation logique des licences PageMaître Security."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from src.security.config import SecurityConfig
from src.security.device import DeviceIdentity
from src.security.license import LicensePayload
from src.security.license_validation import (
    LicenseValidationCode,
    validate_license_payload,
)


class LicenseValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 8, 6, 8, 0, tzinfo=timezone.utc)
        self.device = DeviceIdentity(
            fingerprint="a" * 64,
            source="test",
        )
        self.config = SecurityConfig(
            application_id="fr.eqds.pagemaître",
            maximum_authorized_devices=1,
            bind_license_to_device=True,
        )

    def make_payload(self, **changes: object) -> LicensePayload:
        values: dict[str, object] = {
            "license_id": "LICENCE-TEST-001",
            "product_id": "fr.eqds.pagemaître",
            "customer_reference": "CLIENT-TEST",
            "issued_at": self.now - timedelta(days=1),
            "valid_from": self.now - timedelta(hours=1),
            "expires_at": self.now + timedelta(days=365),
            "authorized_devices": (self.device.fingerprint,),
            "maximum_authorized_devices": 1,
            "features": ("edition", "export-pdf"),
        }
        values.update(changes)
        return LicensePayload(**values)

    def test_valid_license_is_accepted(self) -> None:
        result = validate_license_payload(
            self.make_payload(),
            self.config,
            self.device,
            now=self.now,
        )

        self.assertTrue(result.is_valid)
        self.assertEqual(result.code, LicenseValidationCode.VALID)

    def test_wrong_product_is_rejected(self) -> None:
        result = validate_license_payload(
            self.make_payload(product_id="fr.eqds.autre-produit"),
            self.config,
            self.device,
            now=self.now,
        )

        self.assertEqual(result.code, LicenseValidationCode.WRONG_PRODUCT)

    def test_not_yet_valid_license_is_rejected(self) -> None:
        result = validate_license_payload(
            self.make_payload(valid_from=self.now + timedelta(hours=1)),
            self.config,
            self.device,
            now=self.now,
        )

        self.assertEqual(result.code, LicenseValidationCode.NOT_YET_VALID)

    def test_expired_license_is_rejected(self) -> None:
        result = validate_license_payload(
            self.make_payload(expires_at=self.now),
            self.config,
            self.device,
            now=self.now,
        )

        self.assertEqual(result.code, LicenseValidationCode.EXPIRED)

    def test_unlisted_device_is_rejected(self) -> None:
        result = validate_license_payload(
            self.make_payload(authorized_devices=("b" * 64,)),
            self.config,
            self.device,
            now=self.now,
        )

        self.assertEqual(
            result.code,
            LicenseValidationCode.DEVICE_NOT_AUTHORIZED,
        )

    def test_unbound_license_is_rejected_when_binding_is_required(self) -> None:
        result = validate_license_payload(
            self.make_payload(authorized_devices=()),
            self.config,
            self.device,
            now=self.now,
        )

        self.assertEqual(
            result.code,
            LicenseValidationCode.DEVICE_NOT_ACTIVATED,
        )


if __name__ == "__main__":
    unittest.main()