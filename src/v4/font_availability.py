from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os
import re
import sys


SUBSET_PREFIX = re.compile(
    r"^[A-Z]{6}\+"
)

STYLE_SUFFIXES = (
    ("bolditalic", "bold_italic"),
    ("boldoblique", "bold_italic"),
    ("semibolditalic", "bold_italic"),
    ("demibolditalic", "bold_italic"),
    ("italic", "italic"),
    ("oblique", "italic"),
    ("semibold", "bold"),
    ("demibold", "bold"),
    ("bold", "bold"),
    ("regular", "regular"),
    ("roman", "regular"),
)


@dataclass(frozen=True)
class InstalledFont:
    family: str
    style: str
    path: str
    origin: str = "system"


@dataclass(frozen=True)
class FontMatch:
    pdf_name: str
    family: str
    style: str
    status: str
    installed_family: str | None = None
    installed_style: str | None = None
    installed_path: str | None = None
    installed_origin: str | None = None


def _key(value: str) -> str:

    return "".join(
        char.lower()
        for char in str(value)
        if char.isalnum()
    )


def _style_key(value: str) -> str:

    normalized = _key(
        value
    )

    bold = any(
        token in normalized
        for token in (
            "bold",
            "semibold",
            "demibold",
        )
    )

    italic = any(
        token in normalized
        for token in (
            "italic",
            "oblique",
        )
    )

    if bold and italic:
        return "bold_italic"

    if bold:
        return "bold"

    if italic:
        return "italic"

    return "regular"


def normalize_pdf_font_name(
    value: str,
) -> str:

    value = str(
        value or ""
    ).strip()

    value = SUBSET_PREFIX.sub(
        "",
        value,
    )

    return value


def split_pdf_font_name(
    value: str,
) -> tuple[str, str]:

    value = normalize_pdf_font_name(
        value
    )

    compact = _key(
        value
    )

    style = "regular"

    for suffix, candidate_style in STYLE_SUFFIXES:

        if compact.endswith(
            suffix
        ):

            style = candidate_style

            # Prefer the explicit separator from the PDF name.
            for separator in (
                "-",
                ",",
                "_",
            ):

                if separator in value:

                    head, tail = value.rsplit(
                        separator,
                        1,
                    )

                    if _style_key(
                        tail
                    ) == candidate_style:

                        value = head

                        return (
                            value.strip(),
                            style,
                        )

            # No separator: remove the textual suffix.
            raw_lower = value.lower()

            position = raw_lower.rfind(
                suffix
            )

            if position > 0:
                value = value[
                    :position
                ]

            break

    return (
        value.strip(),
        style,
    )


@lru_cache(maxsize=1)
def installed_fonts() -> tuple[InstalledFont, ...]:

    try:
        from PIL import ImageFont
    except ImportError as exc:
        raise RuntimeError(
            "Pillow is required for font inspection."
        ) from exc

    candidates: list[tuple[Path, str]] = []

    # Bibliothèque privée TomeLinea : elle est inspectée même si les fichiers
    # ne sont pas installés globalement dans le système.
    try:
        from src.v4.font_library import discover_font_files

        candidates.extend(
            (path, "tomelinea")
            for path in discover_font_files()
        )
    except Exception:
        pass

    system_dirs: list[Path] = []

    if sys.platform == "win32":
        windir = Path(os.environ.get("WINDIR", r"C:\Windows"))
        system_dirs.append(windir / "Fonts")

        local_appdata = os.environ.get("LOCALAPPDATA", "").strip()
        if local_appdata:
            # Les polices installées "pour cet utilisateur" ne vivent pas
            # toujours dans C:\Windows\Fonts.
            system_dirs.append(
                Path(local_appdata) / "Microsoft" / "Windows" / "Fonts"
            )

    elif sys.platform == "darwin":
        system_dirs.extend(
            [
                Path("/System/Library/Fonts"),
                Path("/Library/Fonts"),
                Path.home() / "Library" / "Fonts",
            ]
        )

    else:
        system_dirs.extend(
            [
                Path("/usr/share/fonts"),
                Path("/usr/local/share/fonts"),
                Path.home() / ".local" / "share" / "fonts",
                Path.home() / ".fonts",
            ]
        )

    for font_dir in system_dirs:
        if not font_dir.is_dir():
            continue
        try:
            paths = font_dir.rglob("*")
            candidates.extend(
                (path, "system")
                for path in paths
                if path.is_file()
                and path.suffix.lower() in (".ttf", ".otf", ".ttc")
            )
        except OSError:
            continue

    result: list[InstalledFont] = []
    seen_paths: set[str] = set()

    for path, origin in candidates:

        path_key = str(path).casefold()
        if path_key in seen_paths:
            continue
        seen_paths.add(path_key)

        try:
            font = ImageFont.truetype(
                str(path),
                size=12,
            )
            family, style = font.getname()
        except Exception:
            continue

        family = str(family or "").strip()
        style = str(style or "").strip()
        if not family:
            continue

        result.append(
            InstalledFont(
                family=family,
                style=_style_key(style),
                path=str(path),
                origin=origin,
            )
        )

    # Les polices TomeLinea sont prioritaires : elles sont contrôlées,
    # portables avec le projet et ne dépendent pas d'une installation Windows.
    result.sort(
        key=lambda item: (
            0 if item.origin == "tomelinea" else 1,
            _key(item.family),
            item.style,
            item.path.casefold(),
        )
    )

    return tuple(result)


def match_pdf_font(
    pdf_name: str,
) -> FontMatch:

    family, style = split_pdf_font_name(
        pdf_name
    )

    family_key = _key(
        family
    )

    inventory = installed_fonts()

    same_family = [
        item
        for item in inventory
        if _key(
            item.family
        ) == family_key
    ]

    for item in same_family:

        if item.style == style:

            return FontMatch(
                pdf_name=normalize_pdf_font_name(
                    pdf_name
                ),
                family=family,
                style=style,
                status="exact",
                installed_family=item.family,
                installed_style=item.style,
                installed_path=item.path,
                installed_origin=item.origin,
            )

    if same_family:

        item = same_family[0]

        return FontMatch(
            pdf_name=normalize_pdf_font_name(
                pdf_name
            ),
            family=family,
            style=style,
            status="family_only",
            installed_family=item.family,
            installed_style=item.style,
            installed_path=item.path,
            installed_origin=item.origin,
        )

    return FontMatch(
        pdf_name=normalize_pdf_font_name(
            pdf_name
        ),
        family=family,
        style=style,
        status="missing",
    )


def audit_pdf_fonts(
    path: str | Path,
) -> list[dict]:

    try:
        import pymupdf
    except ImportError as exc:
        raise RuntimeError(
            "PyMuPDF is required for PDF font inspection."
        ) from exc

    path = Path(
        path
    )

    document = pymupdf.open(
        str(path)
    )

    try:

        usage: dict[str, set[int]] = {}

        for page_index in range(
            document.page_count
        ):

            page = document.load_page(
                page_index
            )

            for item in page.get_fonts(
                full=True
            ):

                if len(item) < 4:
                    continue

                pdf_name = str(
                    item[3]
                )

                usage.setdefault(
                    pdf_name,
                    set(),
                ).add(
                    page_index + 1
                )

        result = []

        for pdf_name in sorted(
            usage,
            key=str.lower,
        ):

            match = match_pdf_font(
                pdf_name
            )

            result.append(
                {
                    "pdf_name":
                        match.pdf_name,

                    "family":
                        match.family,

                    "style":
                        match.style,

                    "status":
                        match.status,

                    "installed_family":
                        match.installed_family,

                    "installed_style":
                        match.installed_style,

                    "installed_path":
                        match.installed_path,

                    "installed_origin":
                        match.installed_origin,

                    "pages":
                        sorted(
                            usage[
                                pdf_name
                            ]
                        ),
                }
            )

        return result

    finally:
        document.close()
