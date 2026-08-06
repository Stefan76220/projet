"""Signature cryptographique des licences PageMaître Security.

PageMaître utilise Ed25519 pour vérifier qu’une licence a réellement été
émise par son propriétaire et qu’elle n’a pas été modifiée.

Règle essentielle :
- la clé publique pourra être intégrée à PageMaître ;
- la clé privée ne devra jamais être distribuée avec l’application.
"""

from __future__ import annotations

import base64

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)

from src.security.license import (
    LicensePayload,
    SignedLicense,
    SUPPORTED_SIGNATURE_ALGORITHM,
)


class LicenseKeyError(ValueError):
    """Erreur produite lorsqu’une clé de licence est invalide."""


def load_private_key(
    private_key_pem: bytes,
    *,
    password: bytes | None = None,
) -> Ed25519PrivateKey:
    """Charge une clé privée Ed25519 au format PEM."""

    if not private_key_pem.strip():
        raise LicenseKeyError("La clé privée ne peut pas être vide.")

    try:
        key = serialization.load_pem_private_key(
            private_key_pem,
            password=password,
        )
    except (TypeError, ValueError) as error:
        raise LicenseKeyError(
            "La clé privée fournie est invalide ou son mot de passe est incorrect."
        ) from error

    if not isinstance(key, Ed25519PrivateKey):
        raise LicenseKeyError(
            "La clé privée fournie n’est pas une clé Ed25519."
        )

    return key


def load_public_key(public_key_pem: bytes) -> Ed25519PublicKey:
    """Charge une clé publique Ed25519 au format PEM."""

    if not public_key_pem.strip():
        raise LicenseKeyError("La clé publique ne peut pas être vide.")

    try:
        key = serialization.load_pem_public_key(public_key_pem)
    except (TypeError, ValueError) as error:
        raise LicenseKeyError(
            "La clé publique fournie est invalide."
        ) from error

    if not isinstance(key, Ed25519PublicKey):
        raise LicenseKeyError(
            "La clé publique fournie n’est pas une clé Ed25519."
        )

    return key


def sign_license_payload(
    payload: LicensePayload,
    private_key_pem: bytes,
    *,
    password: bytes | None = None,
) -> SignedLicense:
    """Signe une licence avec la clé privée conservée hors de PageMaître."""

    private_key = load_private_key(
        private_key_pem,
        password=password,
    )
    signature_bytes = private_key.sign(payload.to_canonical_bytes())
    signature_text = base64.b64encode(signature_bytes).decode("ascii")

    return SignedLicense(
        payload=payload,
        signature=signature_text,
        algorithm=SUPPORTED_SIGNATURE_ALGORITHM,
    )


def verify_signed_license(
    signed_license: SignedLicense,
    public_key_pem: bytes,
) -> bool:
    """Vérifie la signature d’une licence sans exposer de clé privée."""

    if signed_license.algorithm != SUPPORTED_SIGNATURE_ALGORITHM:
        return False

    public_key = load_public_key(public_key_pem)

    try:
        signature_bytes = base64.b64decode(
            signed_license.signature,
            validate=True,
        )
        public_key.verify(
            signature_bytes,
            signed_license.payload.to_canonical_bytes(),
        )
    except (InvalidSignature, ValueError):
        return False

    return True