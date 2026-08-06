"""Format des licences PageMaître Security.

Ce module définit uniquement la structure des futures licences :
produit, période de validité, appareils autorisés et fonctions disponibles.

La vérification cryptographique sera ajoutée dans un module séparé.
Aucune licence n’est encore exigée au démarrage de PageMaître.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import base64
import json
from typing import Any


LICENSE_FORMAT_VERSION = 1
SUPPORTED_SIGNATURE_ALGORITHM = "ed25519"


def _require_aware_datetime(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(
            f"{field_name} doit contenir un fuseau horaire."
        )


def _datetime_to_text(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _datetime_from_text(value: str, field_name: str) -> datetime:
    text = str(value).strip()
    if not text:
        raise ValueError(f"{field_name} ne peut pas être vide.")

    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"

    try:
        parsed = datetime.fromisoformat(text)
    except ValueError as error:
        raise ValueError(
            f"{field_name} n’est pas une date ISO 8601 valide."
        ) from error

    _require_aware_datetime(parsed, field_name)
    return parsed.astimezone(timezone.utc)


def _validate_fingerprint(value: str) -> str:
    fingerprint = value.strip().lower()

    if len(fingerprint) != 64:
        raise ValueError(
            "Une empreinte d’appareil doit contenir 64 caractères."
        )

    try:
        int(fingerprint, 16)
    except ValueError as error:
        raise ValueError(
            "Une empreinte d’appareil doit être hexadécimale."
        ) from error

    return fingerprint


@dataclass(frozen=True, slots=True)
class LicensePayload:
    """Données signées d’une licence PageMaître."""

    license_id: str
    product_id: str
    customer_reference: str
    issued_at: datetime
    valid_from: datetime
    expires_at: datetime | None = None
    authorized_devices: tuple[str, ...] = ()
    maximum_authorized_devices: int = 1
    features: tuple[str, ...] = ()
    format_version: int = LICENSE_FORMAT_VERSION

    def __post_init__(self) -> None:
        text_fields = {
            "license_id": self.license_id,
            "product_id": self.product_id,
            "customer_reference": self.customer_reference,
        }

        for field_name, value in text_fields.items():
            if not value.strip():
                raise ValueError(f"{field_name} ne peut pas être vide.")

        if self.format_version != LICENSE_FORMAT_VERSION:
            raise ValueError(
                "Version de format de licence non prise en charge."
            )

        _require_aware_datetime(self.issued_at, "issued_at")
        _require_aware_datetime(self.valid_from, "valid_from")

        if self.expires_at is not None:
            _require_aware_datetime(self.expires_at, "expires_at")

        issued_at = self.issued_at.astimezone(timezone.utc)
        valid_from = self.valid_from.astimezone(timezone.utc)

        if valid_from < issued_at:
            raise ValueError(
                "valid_from ne peut pas précéder issued_at."
            )

        if self.expires_at is not None:
            expires_at = self.expires_at.astimezone(timezone.utc)
            if expires_at <= valid_from:
                raise ValueError(
                    "expires_at doit être postérieure à valid_from."
                )

        if self.maximum_authorized_devices < 1:
            raise ValueError(
                "maximum_authorized_devices doit être supérieur ou égal à 1."
            )

        normalized_devices = tuple(
            _validate_fingerprint(value)
            for value in self.authorized_devices
        )

        if len(set(normalized_devices)) != len(normalized_devices):
            raise ValueError(
                "Une empreinte d’appareil est présente plusieurs fois."
            )

        if len(normalized_devices) > self.maximum_authorized_devices:
            raise ValueError(
                "Le nombre d’appareils dépasse la limite de la licence."
            )

        normalized_features = tuple(
            feature.strip()
            for feature in self.features
            if feature.strip()
        )

        if len(set(normalized_features)) != len(normalized_features):
            raise ValueError(
                "Une fonction de licence est présente plusieurs fois."
            )

        object.__setattr__(self, "authorized_devices", normalized_devices)
        object.__setattr__(self, "features", normalized_features)

    def to_dict(self) -> dict[str, Any]:
        """Retourne les données dans un ordre stable."""

        return {
            "format_version": self.format_version,
            "license_id": self.license_id,
            "product_id": self.product_id,
            "customer_reference": self.customer_reference,
            "issued_at": _datetime_to_text(self.issued_at),
            "valid_from": _datetime_to_text(self.valid_from),
            "expires_at": (
                _datetime_to_text(self.expires_at)
                if self.expires_at is not None
                else None
            ),
            "authorized_devices": list(self.authorized_devices),
            "maximum_authorized_devices": self.maximum_authorized_devices,
            "features": list(self.features),
        }

    def to_canonical_bytes(self) -> bytes:
        """Produit les octets déterministes destinés à être signés."""

        return json.dumps(
            self.to_dict(),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LicensePayload":
        """Reconstruit et valide une licence depuis un dictionnaire."""

        if not isinstance(data, dict):
            raise ValueError("Le contenu de la licence doit être un objet JSON.")

        expires_value = data.get("expires_at")

        return cls(
            format_version=int(
                data.get("format_version", LICENSE_FORMAT_VERSION)
            ),
            license_id=str(data.get("license_id", "")),
            product_id=str(data.get("product_id", "")),
            customer_reference=str(
                data.get("customer_reference", "")
            ),
            issued_at=_datetime_from_text(
                str(data.get("issued_at", "")),
                "issued_at",
            ),
            valid_from=_datetime_from_text(
                str(data.get("valid_from", "")),
                "valid_from",
            ),
            expires_at=(
                _datetime_from_text(
                    str(expires_value),
                    "expires_at",
                )
                if expires_value is not None
                else None
            ),
            authorized_devices=tuple(
                str(value)
                for value in data.get("authorized_devices", ())
            ),
            maximum_authorized_devices=int(
                data.get("maximum_authorized_devices", 1)
            ),
            features=tuple(
                str(value)
                for value in data.get("features", ())
            ),
        )


@dataclass(frozen=True, slots=True)
class SignedLicense:
    """Enveloppe contenant les données et leur future signature."""

    payload: LicensePayload
    signature: str
    algorithm: str = SUPPORTED_SIGNATURE_ALGORITHM

    def __post_init__(self) -> None:
        if self.algorithm != SUPPORTED_SIGNATURE_ALGORITHM:
            raise ValueError(
                "Algorithme de signature de licence non pris en charge."
            )

        signature_text = self.signature.strip()
        if not signature_text:
            raise ValueError("La signature de licence ne peut pas être vide.")

        try:
            signature_bytes = base64.b64decode(
                signature_text,
                validate=True,
            )
        except (ValueError, TypeError) as error:
            raise ValueError(
                "La signature de licence n’est pas un Base64 valide."
            ) from error

        if not signature_bytes:
            raise ValueError("La signature de licence est vide.")

        object.__setattr__(self, "signature", signature_text)

    def to_json(self) -> str:
        """Sérialise la licence signée dans un format stable."""

        return json.dumps(
            {
                "algorithm": self.algorithm,
                "payload": self.payload.to_dict(),
                "signature": self.signature,
            },
            ensure_ascii=False,
            sort_keys=True,
            indent=2,
        )

    @classmethod
    def from_json(cls, text: str) -> "SignedLicense":
        """Charge et valide la structure d’une licence signée."""

        try:
            data = json.loads(text)
        except json.JSONDecodeError as error:
            raise ValueError(
                "Le fichier de licence n’est pas un JSON valide."
            ) from error

        if not isinstance(data, dict):
            raise ValueError(
                "Le fichier de licence doit contenir un objet JSON."
            )

        payload_data = data.get("payload")
        if not isinstance(payload_data, dict):
            raise ValueError(
                "Le fichier de licence ne contient pas de payload valide."
            )

        return cls(
            algorithm=str(data.get("algorithm", "")),
            payload=LicensePayload.from_dict(payload_data),
            signature=str(data.get("signature", "")),
        )