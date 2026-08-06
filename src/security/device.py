"""Identification locale d’un appareil pour PageMaître Security.

Le module produit une empreinte pseudonymisée et stable à partir d’un
identifiant système. La valeur système brute n’est jamais retournée ni
enregistrée par ce module.

Aucun contrôle n’est encore relié au démarrage de PageMaître.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import platform
import uuid


@dataclass(frozen=True, slots=True)
class DeviceIdentity:
    """Identité pseudonymisée de l’appareil courant."""

    fingerprint: str
    source: str

    def __post_init__(self) -> None:
        if len(self.fingerprint) != 64:
            raise ValueError(
                "L’empreinte de l’appareil doit être un SHA-256 hexadécimal."
            )

        try:
            int(self.fingerprint, 16)
        except ValueError as error:
            raise ValueError(
                "L’empreinte de l’appareil contient des caractères invalides."
            ) from error

        if not self.source.strip():
            raise ValueError("La source de l’identité ne peut pas être vide.")


def get_device_identity(application_id: str) -> DeviceIdentity:
    """Retourne une empreinte stable propre à PageMaître.

    Sous Windows, la fonction privilégie MachineGuid.
    Un matériau de secours est utilisé lorsque cet identifiant est indisponible.
    """

    normalized_application_id = application_id.strip()
    if not normalized_application_id:
        raise ValueError("application_id ne peut pas être vide.")

    machine_guid = _read_windows_machine_guid()
    if machine_guid:
        return DeviceIdentity(
            fingerprint=_hash_material(
                normalized_application_id,
                "windows-machine-guid",
                machine_guid,
            ),
            source="windows-machine-guid",
        )

    fallback_material = _build_fallback_material()
    return DeviceIdentity(
        fingerprint=_hash_material(
            normalized_application_id,
            "system-fallback",
            fallback_material,
        ),
        source="system-fallback",
    )


def _hash_material(
    application_id: str,
    source: str,
    raw_material: str,
) -> str:
    """Transforme une valeur système brute en empreinte non réversible."""

    normalized_material = raw_material.strip().lower()
    if not normalized_material:
        raise ValueError("Le matériau d’identification ne peut pas être vide.")

    payload = (
        f"PageMaitreSecurity:v1\n"
        f"application={application_id}\n"
        f"source={source}\n"
        f"value={normalized_material}"
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _read_windows_machine_guid() -> str | None:
    """Lit MachineGuid sous Windows sans créer de dépendance non-Windows."""

    if platform.system().lower() != "windows":
        return None

    try:
        import winreg

        access_flags = winreg.KEY_READ
        wow64_flag = getattr(winreg, "KEY_WOW64_64KEY", 0)

        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography",
            0,
            access_flags | wow64_flag,
        ) as registry_key:
            value, _ = winreg.QueryValueEx(registry_key, "MachineGuid")
    except (ImportError, OSError):
        return None

    machine_guid = str(value).strip()
    return machine_guid or None


def _build_fallback_material() -> str:
    """Construit une valeur de secours lorsque MachineGuid est inaccessible."""

    values = (
        platform.system(),
        platform.release(),
        platform.machine(),
        platform.node(),
        f"{uuid.getnode():012x}",
    )

    normalized_values = [
        str(value).strip().lower()
        for value in values
        if str(value).strip()
    ]

    if not normalized_values:
        raise RuntimeError(
            "Impossible de construire une identité pour cet appareil."
        )

    return "|".join(normalized_values)