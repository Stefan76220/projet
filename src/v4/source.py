from __future__ import annotations

"""
TomeLinea V4 — registre des Sources.

Une Source décrit ce que l'auteur a fourni.
Elle ne contient aucune interprétation éditoriale de TomeLinea.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from uuid import uuid4


def new_id() -> str:
    return str(uuid4())


def file_sha256(path: str | Path) -> str:
    source = Path(path).expanduser().resolve()

    if not source.is_file():
        raise FileNotFoundError(source)

    digest = sha256()

    with source.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)

    return digest.hexdigest()


@dataclass(frozen=True, slots=True)
class SourceVersion:
    """
    Version précise d'un fichier auteur.

    Une version enregistrée n'est jamais modifiée.
    """

    id: str
    original_name: str
    original_path: str
    file_type: str
    fingerprint: str
    size_bytes: int
    imported_at: str

    @classmethod
    def from_file(cls, path: str | Path) -> "SourceVersion":
        source = Path(path).expanduser().resolve()

        if not source.is_file():
            raise FileNotFoundError(source)

        return cls(
            id=new_id(),
            original_name=source.name,
            original_path=str(source),
            file_type=source.suffix.lower().lstrip("."),
            fingerprint=file_sha256(source),
            size_bytes=source.stat().st_size,
            imported_at=datetime.now(timezone.utc).isoformat(),
        )


@dataclass(slots=True)
class SourceElement:
    """
    Élément logique stable.

    L'id de l'élément reste identique lorsqu'une nouvelle version
    du même document remplace la précédente.
    """

    id: str = field(default_factory=new_id)
    versions: list[SourceVersion] = field(default_factory=list)
    active_version_id: str | None = None

    def add_version(
        self,
        version: SourceVersion,
        *,
        activate: bool = True,
    ) -> None:
        if any(existing.id == version.id for existing in self.versions):
            raise ValueError(f"Version déjà présente : {version.id}")

        self.versions.append(version)

        if activate:
            self.active_version_id = version.id

    @property
    def active_version(self) -> SourceVersion | None:
        if self.active_version_id is None:
            return None

        for version in self.versions:
            if version.id == self.active_version_id:
                return version

        raise ValueError(
            f"Version active inconnue : {self.active_version_id}"
        )


@dataclass(slots=True)
class SourceV4:
    """
    Registre de tout ce que l'auteur a fourni au projet.
    """

    id: str = field(default_factory=new_id)
    elements: dict[str, SourceElement] = field(default_factory=dict)

    def register_file(self, path: str | Path) -> SourceElement:
        version = SourceVersion.from_file(path)

        element = SourceElement()
        element.add_version(version)

        self.elements[element.id] = element
        return element

    def add_file_version(
        self,
        element_id: str,
        path: str | Path,
    ) -> SourceVersion:
        if element_id not in self.elements:
            raise KeyError(element_id)

        version = SourceVersion.from_file(path)
        self.elements[element_id].add_version(version)
        return version

    def validate(self) -> None:
        for element_id, element in self.elements.items():
            if element.id != element_id:
                raise ValueError(
                    f"Incohérence d'identité Source : {element_id}"
                )

            ids = [version.id for version in element.versions]

            if len(ids) != len(set(ids)):
                raise ValueError(
                    f"Version Source dupliquée : {element_id}"
                )

            if (
                element.active_version_id is not None
                and element.active_version_id not in ids
            ):
                raise ValueError(
                    f"Version active invalide : {element_id}"
                )
