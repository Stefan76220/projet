"""Configuration centrale du futur module PageMaître Security.

Ce fichier ne protège encore rien et ne modifie pas le démarrage de PageMaître.
Il prépare uniquement une configuration commune pour les futurs composants :
licence, verrouillage, intégrité, chiffrement local et liaison à un appareil.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import os


class SecurityMode(str, Enum):
    """Niveau d’activation du système de sécurité."""

    DISABLED = "disabled"
    DEVELOPMENT = "development"
    ENFORCED = "enforced"


@dataclass(frozen=True, slots=True)
class SecurityConfig:
    """Paramètres généraux du module PageMaître Security."""

    mode: SecurityMode = SecurityMode.DISABLED
    application_id: str = "fr.eqds.pagemaître"
    product_name: str = "PageMaître"

    license_filename: str = "license.dat"
    integrity_manifest_filename: str = "integrity.json"
    security_state_filename: str = "security_state.dat"

    maximum_authorized_devices: int = 1
    offline_grace_period_days: int = 30
    maximum_failed_unlock_attempts: int = 5

    bind_license_to_device: bool = True
    verify_application_integrity: bool = True
    encrypt_local_security_data: bool = True

    @property
    def is_enabled(self) -> bool:
        """Indique si un niveau de sécurité est activé."""

        return self.mode is not SecurityMode.DISABLED

    @property
    def is_enforced(self) -> bool:
        """Indique si les contrôles doivent bloquer l’application."""

        return self.mode is SecurityMode.ENFORCED

    def validate(self) -> None:
        """Vérifie la cohérence de la configuration."""

        if self.maximum_authorized_devices < 1:
            raise ValueError(
                "maximum_authorized_devices doit être supérieur ou égal à 1."
            )

        if self.offline_grace_period_days < 0:
            raise ValueError(
                "offline_grace_period_days ne peut pas être négatif."
            )

        if self.maximum_failed_unlock_attempts < 1:
            raise ValueError(
                "maximum_failed_unlock_attempts doit être supérieur ou égal à 1."
            )

        required_text_values = {
            "application_id": self.application_id,
            "product_name": self.product_name,
            "license_filename": self.license_filename,
            "integrity_manifest_filename": self.integrity_manifest_filename,
            "security_state_filename": self.security_state_filename,
        }

        for field_name, value in required_text_values.items():
            if not value.strip():
                raise ValueError(f"{field_name} ne peut pas être vide.")

    @classmethod
    def from_environment(cls) -> "SecurityConfig":
        """Construit la configuration depuis les variables d’environnement.

        Variable reconnue :
        PAGEMAITRE_SECURITY_MODE = disabled | development | enforced

        Une valeur absente ou incorrecte laisse la sécurité désactivée.
        """

        raw_mode = os.getenv(
            "PAGEMAITRE_SECURITY_MODE",
            SecurityMode.DISABLED.value,
        ).strip().lower()

        try:
            mode = SecurityMode(raw_mode)
        except ValueError:
            mode = SecurityMode.DISABLED

        config = cls(mode=mode)
        config.validate()
        return config


DEFAULT_SECURITY_CONFIG = SecurityConfig()
DEFAULT_SECURITY_CONFIG.validate()