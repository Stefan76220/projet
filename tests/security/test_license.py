"""Tests du format de licence PageMaître Security."""

from __future__ import annotations

import base64
from datetime import datetime, timedelta, timezone
import unittest

from src.security.license import LicensePayload, SignedLicense


class LicenseFormatTests(unittest.TestCase):
    def setUp(self) -> None:
        self.issued_at = datetime(2026, 8, 6, 8, 0, tzinfo=timezone.utc)
        self.valid_from = self.issued_at + timedelta(minutes=1)
        self.fingerprint = "a" * 64

    def make_payload(self, **changes: object) -> LicensePayload:
        values: dict[str, object] = {
            "license_id": "LICENCE-TEST-001",
            "product_id": "fr.eqds.pagemaître",
            "customer_reference": "CLIENT-TEST",
            "issued_at": self.issued_at,
            "valid_from": self.valid_from,
            "expires_at": self.valid_from + timedelta(days=365),
            "authorized_devices": (self.fingerprint,),
            "maximum_authorized_devices": 1,
            "features": ("edition", "export-pdf"),
        }
        values.update(changes)
        return LicensePayload(**values)

    def test_payload_produces_stable_canonical_bytes(self) -> None:
        payload = self.make_payload()

        first = payload.to_canonical_bytes()
        second = payload.to_canonical_bytes()

        self.assertEqual(first, second)
        self.assertIn(b"LICENCE-TEST-001", first)

    def test_payload_round_trip_through_dictionary(self) -> None:
        original = self.make_payload()

        restored = LicensePayload.from_dict(original.to_dict())

        self.assertEqual(restored, original)

    def test_signed_license_round_trip_through_json(self) -> None:
        signature = base64.b64encode(b"signature-de-test").decode("ascii")
        original = SignedLicense(
            payload=self.make_payload(),
            signature=signature,
        )

        restored = SignedLicense.from_json(original.to_json())

        self.assertEqual(restored, original)

    def test_too_many_authorized_devices_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.make_payload(
                authorized_devices=("a" * 64, "b" * 64),
                maximum_authorized_devices=1,
            )

    def test_expiration_before_validity_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.make_payload(
                expires_at=self.valid_from - timedelta(seconds=1),
            )

    def test_invalid_base64_signature_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            SignedLicense(
                payload=self.make_payload(),
                signature="signature non base64 !",
            )


if __name__ == "__main__":
    unittest.main()