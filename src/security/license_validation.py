"""Validation logique des licences PageMaître Security.

Ce module contrôle les données d’une licence déjà chargée :
produit concerné, période de validité, limite d’appareils et identité locale.

La signature cryptographique sera vérifiée séparément avant cet examen.
Aucun contrôle n’est encore relié au démarrage de PageMaître.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from src.security.config import SecurityConfig
from src.security.device import DeviceIdentity
from src.security.license import LicensePayload


class LicenseValidationCode(str, Enum):
    """Motif précis produit par la validation d’une licence."""

    VALID = "valid"
    WRONG_PRODUCT = "wrong_product"
    NOT_YET_VALID = "not_yet_valid"
    EXPIRED = "expired"
    DEVICE_LIMIT_EXCEEDED = "device_limit_exceeded"
    DEVICE_NOT_ACTIVATED = "device_not_activated"
    DEVICE_NOT_AUTHORIZED = "device_not_authorized"


@dataclass(frozen=True, slots=True)
class LicenseValidationResult:
    """Résultat détaillé de la validation logique d’une licence."""

    code: LicenseValidationCode
    message: str

    def __post_init__(self) -> None:
        if not self.message.strip():
            raise ValueError("Le message de validation ne peut pas être vide.")

    @property
    def is_valid(self) -> bool:
        """Indique si la licence peut être acceptée."""

        return self.code is LicenseValidationCode.VALID


def validate_license_payload(
    payload: LicensePayload,
    config: SecurityConfig,
    device: DeviceIdentity,
    *,
    now: datetime | None = None,
) -> LicenseValidationResult:
    """Vérifie qu’une licence est utilisable sur l’appareil courant."""

    config.validate()
    current_time = now or datetime.now(timezone.utc)

    if current_time.tzinfo is None or current_time.utcoffset() is None:
        raise ValueError("now doit contenir un fuseau horaire.")

    current_time = current_time.astimezone(timezone.utc)
    valid_from = payload.valid_from.astimezone(timezone.utc)

    if payload.product_id != config.application_id:
        return LicenseValidationResult(
            code=LicenseValidationCode.WRONG_PRODUCT,
            message="Cette licence ne correspond pas à PageMaître.",
        )

    if current_time < valid_from:
        return LicenseValidationResult(
            code=LicenseValidationCode.NOT_YET_VALID,
            message="Cette licence n’est pas encore valide.",
        )

    if payload.expires_at is not None:
        expires_at = payload.expires_at.astimezone(timezone.utc)
        if current_time >= expires_at:
            return LicenseValidationResult(
                code=LicenseValidationCode.EXPIRED,
                message="Cette licence a expiré.",
            )

    if (
        payload.maximum_authorized_devices
        > config.maximum_authorized_devices
    ):
        return LicenseValidationResult(
            code=LicenseValidationCode.DEVICE_LIMIT_EXCEEDED,
            message=(
                "La limite d’appareils de cette licence dépasse "
                "la politique de PageMaître."
            ),
        )

    if config.bind_license_to_device:
        if not payload.authorized_devices:
            return LicenseValidationResult(
                code=LicenseValidationCode.DEVICE_NOT_ACTIVATED,
                message="Cette licence n’est encore liée à aucun appareil.",
            )

        if device.fingerprint not in payload.authorized_devices:
            return LicenseValidationResult(
                code=LicenseValidationCode.DEVICE_NOT_AUTHORIZED,
                message="Cet ordinateur n’est pas autorisé par la licence.",
            )

    return LicenseValidationResult(
        code=LicenseValidationCode.VALID,
        message="Licence valide pour cet ordinateur.",
    )