"""Tests de signature des licences PageMaître Security."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)

from src.security.license import LicensePayload, SignedLicense
from src.security.signature import (
    LicenseKeyError,
    sign_license_payload,
    verify_signed_license,
)


class LicenseSignatureTests(unittest.TestCase):
    def setUp(self) -> None:
        now = datetime(2026, 8, 6, 8, 0, tzinfo=timezone.utc)
        self.payload = LicensePayload(
            license_id="LICENCE-TEST-001",
            product_id="fr.eqds.pagemaître",
            customer_reference="CLIENT-TEST",
            issued_at=now,
            valid_from=now + timedelta(minutes=1),
            expires_at=now + timedelta(days=365),
            authorized_devices=("a" * 64,),
            maximum_authorized_devices=1,
            features=("edition", "export-pdf"),
        )

        self.private_key = Ed25519PrivateKey.generate()
        self.private_key_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        self.public_key_pem = self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def test_signed_license_is_verified(self) -> None:
        signed_license = sign_license_payload(
            self.payload,
            self.private_key_pem,
        )

        self.assertTrue(
            verify_signed_license(
                signed_license,
                self.public_key_pem,
            )
        )

    def test_modified_payload_invalidates_signature(self) -> None:
        signed_license = sign_license_payload(
            self.payload,
            self.private_key_pem,
        )
        modified_payload = LicensePayload.from_dict(
            {
                **self.payload.to_dict(),
                "customer_reference": "CLIENT-MODIFIE",
            }
        )
        modified_license = SignedLicense(
            payload=modified_payload,
            signature=signed_license.signature,
        )

        self.assertFalse(
            verify_signed_license(
                modified_license,
                self.public_key_pem,
            )
        )

    def test_wrong_public_key_is_rejected(self) -> None:
        signed_license = sign_license_payload(
            self.payload,
            self.private_key_pem,
        )
        other_public_key_pem = (
            Ed25519PrivateKey.generate()
            .public_key()
            .public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo,
            )
        )

        self.assertFalse(
            verify_signed_license(
                signed_license,
                other_public_key_pem,
            )
        )

    def test_invalid_private_key_is_rejected(self) -> None:
        with self.assertRaises(LicenseKeyError):
            sign_license_payload(
                self.payload,
                b"cle-privee-invalide",
            )

    def test_invalid_public_key_is_rejected(self) -> None:
        signed_license = sign_license_payload(
            self.payload,
            self.private_key_pem,
        )

        with self.assertRaises(LicenseKeyError):
            verify_signed_license(
                signed_license,
                b"cle-publique-invalide",
            )

    def test_encrypted_private_key_can_sign_with_password(self) -> None:
        password = b"mot-de-passe-de-test"
        encrypted_private_key_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.BestAvailableEncryption(
                password
            ),
        )

        signed_license = sign_license_payload(
            self.payload,
            encrypted_private_key_pem,
            password=password,
        )

        self.assertTrue(
            verify_signed_license(
                signed_license,
                self.public_key_pem,
            )
        )


if __name__ == "__main__":
    unittest.main()