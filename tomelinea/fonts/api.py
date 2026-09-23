"""Service de polices commun de TomeLinea V5.

Contrat V5 :
1. chercher d'abord dans les polices du systeme ;
2. puis dans resources/fonts/core ;
3. puis dans resources/fonts/user ;
4. ne jamais substituer silencieusement une famille ou une graisse ;
5. conserver le chemin et l'origine de la police retenue ;
6. aucun telechargement obligatoire au lancement.

Le catalogue editorial des 45 familles libres reste celui valide en V4.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import json
import os
from pathlib import Path
import sys
from typing import Iterable, Mapping

from src.v4.font_library import (
    CATALOG_VERSION,
    CORE_FONT_FAMILIES,
    FONT_EXTENSIONS,
    CoreFontFamily,
    FontReplacementSuggestion,
    replacement_suggestions,
)


ORIGIN_SYSTEM = "system"
ORIGIN_CORE = "core"
ORIGIN_USER = "user"

ORIGIN_PRIORITY = {
    ORIGIN_SYSTEM: 0,
    ORIGIN_CORE: 1,
    ORIGIN_USER: 2,
}


@dataclass(frozen=True, slots=True)
class FontFace:
    family: str
    style: str
    path: str
    origin: str


@dataclass(frozen=True, slots=True)
class FontResolution:
    family: str
    style: str
    status: str
    resolved_family: str | None = None
    resolved_style: str | None = None
    path: str | None = None
    origin: str | None = None
    substituted: bool = False


def _project_root(project_root: str | Path | None = None) -> Path:
    if project_root is not None:
        return Path(project_root).expanduser().resolve()

    override = os.environ.get("TOMELINEA_PROJECT_ROOT", "").strip()
    if override:
        return Path(override).expanduser().resolve()

    return Path(__file__).resolve().parents[2]


def font_root(project_root: str | Path | None = None) -> Path:
    return _project_root(project_root) / "resources" / "fonts"


def core_font_root(project_root: str | Path | None = None) -> Path:
    return font_root(project_root) / "core"


def user_font_root(project_root: str | Path | None = None) -> Path:
    return font_root(project_root) / "user"


def _catalog_payload() -> dict:
    return {
        "catalog_version": CATALOG_VERSION,
        "provider": "google/fonts",
        "provider_url": "https://github.com/google/fonts",
        "download_policy": "explicit_only",
        "resolution_priority": ["system", "core", "user"],
        "families": [
            asdict(item) | {"source_url": item.source_url}
            for item in CORE_FONT_FAMILIES
        ],
    }


def prepare_library(project_root: str | Path | None = None) -> dict:
    """Cree la structure locale et le catalogue sans telecharger de police."""

    root = font_root(project_root)
    core_font_root(project_root).mkdir(parents=True, exist_ok=True)
    user_font_root(project_root).mkdir(parents=True, exist_ok=True)

    payload = _catalog_payload()
    (root / "catalog.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return payload


def system_font_dirs() -> tuple[Path, ...]:
    dirs: list[Path] = []

    if sys.platform == "win32":
        windir = Path(os.environ.get("WINDIR", r"C:\Windows"))
        dirs.append(windir / "Fonts")

        local_appdata = os.environ.get("LOCALAPPDATA", "").strip()
        if local_appdata:
            dirs.append(Path(local_appdata) / "Microsoft" / "Windows" / "Fonts")

    elif sys.platform == "darwin":
        dirs.extend(
            [
                Path("/System/Library/Fonts"),
                Path("/Library/Fonts"),
                Path.home() / "Library" / "Fonts",
            ]
        )

    else:
        dirs.extend(
            [
                Path("/usr/share/fonts"),
                Path("/usr/local/share/fonts"),
                Path.home() / ".local" / "share" / "fonts",
                Path.home() / ".fonts",
            ]
        )

    return tuple(dirs)


def _font_files(root: Path) -> tuple[Path, ...]:
    if not root.is_dir():
        return ()

    try:
        paths = [
            path
            for path in root.rglob("*")
            if path.is_file() and path.suffix.lower() in FONT_EXTENSIONS
        ]
    except OSError:
        return ()

    return tuple(sorted(paths, key=lambda value: str(value).casefold()))


def _style_key(value: str) -> str:
    raw = "".join(ch.lower() for ch in str(value or "") if ch.isalnum())

    bold = any(token in raw for token in ("bold", "semibold", "demibold"))
    italic = any(token in raw for token in ("italic", "oblique"))

    if bold and italic:
        return "bold_italic"
    if bold:
        return "bold"
    if italic:
        return "italic"
    return "regular"


def _family_key(value: str) -> str:
    return "".join(ch.lower() for ch in str(value or "") if ch.isalnum())


def _inspect_font(path: Path, origin: str) -> FontFace | None:
    try:
        from PIL import ImageFont

        font = ImageFont.truetype(str(path), size=12)
        family, style = font.getname()
    except Exception:
        return None

    family = str(family or "").strip()
    if not family:
        return None

    return FontFace(
        family=family,
        style=_style_key(str(style or "")),
        path=str(path),
        origin=origin,
    )


def _faces_from_paths(paths: Iterable[Path], origin: str) -> list[FontFace]:
    result: list[FontFace] = []

    for path in paths:
        face = _inspect_font(path, origin)
        if face is not None:
            result.append(face)

    return result


def font_inventory(
    project_root: str | Path | None = None,
) -> tuple[FontFace, ...]:
    """Inventaire ordonne strictement : systeme, core, user."""

    result: list[FontFace] = []

    for directory in system_font_dirs():
        result.extend(
            _faces_from_paths(
                _font_files(directory),
                ORIGIN_SYSTEM,
            )
        )

    result.extend(
        _faces_from_paths(
            _font_files(core_font_root(project_root)),
            ORIGIN_CORE,
        )
    )

    result.extend(
        _faces_from_paths(
            _font_files(user_font_root(project_root)),
            ORIGIN_USER,
        )
    )

    # La priorite ne depend jamais de l'ordre de parcours du disque.
    result.sort(
        key=lambda item: (
            ORIGIN_PRIORITY.get(item.origin, 99),
            _family_key(item.family),
            item.style,
            item.path.casefold(),
        )
    )

    return tuple(result)


def resolve_font(
    family: str,
    style: str = "regular",
    *,
    project_root: str | Path | None = None,
    inventory: Iterable[FontFace] | None = None,
) -> FontResolution:
    """Resout une famille sans aucune substitution implicite."""

    requested_family = str(family or "").strip()
    requested_style = _style_key(style)

    if not requested_family:
        return FontResolution(
            family="",
            style=requested_style,
            status="missing_family",
        )

    faces = tuple(
        inventory
        if inventory is not None
        else font_inventory(project_root)
    )

    ordered = sorted(
        faces,
        key=lambda item: (
            ORIGIN_PRIORITY.get(item.origin, 99),
            _family_key(item.family),
            item.style,
            item.path.casefold(),
        )
    )

    same_family = [
        item
        for item in ordered
        if _family_key(item.family) == _family_key(requested_family)
    ]

    exact = next(
        (
            item
            for item in same_family
            if item.style == requested_style
        ),
        None,
    )

    if exact is not None:
        return FontResolution(
            family=requested_family,
            style=requested_style,
            status="exact",
            resolved_family=exact.family,
            resolved_style=exact.style,
            path=exact.path,
            origin=exact.origin,
            substituted=False,
        )

    if same_family:
        first = same_family[0]
        return FontResolution(
            family=requested_family,
            style=requested_style,
            status="family_only",
            resolved_family=first.family,
            resolved_style=first.style,
            path=first.path,
            origin=first.origin,
            substituted=False,
        )

    return FontResolution(
        family=requested_family,
        style=requested_style,
        status="missing_family",
        substituted=False,
    )


def resolve_requirements(
    requirements: Iterable[Mapping[str, str]],
    *,
    project_root: str | Path | None = None,
    inventory: Iterable[FontFace] | None = None,
    substitutions: Mapping[str, Mapping[str, str]] | None = None,
) -> list[dict]:
    """Resout des exigences Source.

    ``substitutions`` est la seule voie autorisee pour remplacer une famille.
    Aucune suggestion n'est appliquee automatiquement.
    """

    faces = tuple(
        inventory
        if inventory is not None
        else font_inventory(project_root)
    )

    explicit = {
        _family_key(key): dict(value)
        for key, value in (substitutions or {}).items()
    }

    result: list[dict] = []

    for requirement in requirements:
        family = str(requirement.get("family") or "").strip()
        style = _style_key(str(requirement.get("style") or "regular"))

        resolution = resolve_font(
            family,
            style,
            inventory=faces,
        )

        if resolution.status != "exact":
            replacement = explicit.get(_family_key(family))

            if replacement:
                replacement_family = str(
                    replacement.get("family") or ""
                ).strip()
                replacement_style = _style_key(
                    str(replacement.get("style") or style)
                )

                candidate = resolve_font(
                    replacement_family,
                    replacement_style,
                    inventory=faces,
                )

                if candidate.status == "exact":
                    resolution = FontResolution(
                        family=family,
                        style=style,
                        status="substituted",
                        resolved_family=candidate.resolved_family,
                        resolved_style=candidate.resolved_style,
                        path=candidate.path,
                        origin=candidate.origin,
                        substituted=True,
                    )

        result.append(asdict(resolution))

    return result


def unresolved_requirements(resolutions: Iterable[Mapping[str, object]]) -> list[dict]:
    return [
        dict(item)
        for item in resolutions
        if str(item.get("status") or "") not in {"exact", "substituted"}
    ]


__all__ = [
    "CATALOG_VERSION",
    "CORE_FONT_FAMILIES",
    "CoreFontFamily",
    "FontReplacementSuggestion",
    "replacement_suggestions",
    "ORIGIN_SYSTEM",
    "ORIGIN_CORE",
    "ORIGIN_USER",
    "ORIGIN_PRIORITY",
    "FontFace",
    "FontResolution",
    "font_root",
    "core_font_root",
    "user_font_root",
    "prepare_library",
    "system_font_dirs",
    "font_inventory",
    "resolve_font",
    "resolve_requirements",
    "unresolved_requirements",
]