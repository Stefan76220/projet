from __future__ import annotations

"""Bibliothèque de polices privée de TomeLinea.

Principe :
- aucune installation globale dans le système ;
- les familles libres choisies par TomeLinea sont téléchargées une seule fois
  depuis le dépôt officiel Google Fonts et conservées dans resources/fonts/core ;
- les polices ajoutées par l'utilisateur sont copiées dans resources/fonts/user ;
- sous Windows les fichiers sont enregistrés comme polices *privées au processus*
  avec AddFontResourceExW afin que Tk/TomeLinea puisse les utiliser ;
- les fichiers de police ne sont jamais remplacés silencieusement.

Le catalogue ci-dessous est volontairement éditorial : corps de texte, titres,
sans-serif, accessibilité et quelques familles techniques. Toutes les familles
sont distribuées sous SIL Open Font License 1.1 dans Google Fonts.
"""

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Callable, Iterable
import argparse
import ctypes
import json
import os
import shutil
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request


FONT_EXTENSIONS = {".ttf", ".otf", ".ttc"}
CATALOG_VERSION = 2
GOOGLE_FONTS_API = "https://api.github.com/repos/google/fonts/contents"


@dataclass(frozen=True, slots=True)
class CoreFontFamily:
    family: str
    slug: str
    category: str
    collection: str
    use: str
    license: str = "OFL-1.1"
    license_dir: str = "ofl"

    @property
    def source_url(self) -> str:
        return f"https://github.com/google/fonts/tree/main/{self.license_dir}/{self.slug}"


# Sélection large mais raisonnable : elle couvre l'essentiel des besoins de
# romans, essais, livres illustrés, documentation, titres et accessibilité.
CORE_FONT_FAMILIES: tuple[CoreFontFamily, ...] = (
    CoreFontFamily("EB Garamond", "ebgaramond", "Serif", "Classiques éditoriaux", "Roman, littérature, essais"),
    CoreFontFamily("Crimson Pro", "crimsonpro", "Serif", "Classiques éditoriaux", "Roman, littérature, essais"),
    CoreFontFamily("Source Serif 4", "sourceserif4", "Serif", "Adobe Source", "Corps de texte, édition générale"),
    CoreFontFamily("Literata", "literata", "Serif", "Lecture longue", "Lecture longue, roman, numérique et papier"),
    CoreFontFamily("Lora", "lora", "Serif", "Lecture longue", "Roman, essai, texte courant"),
    CoreFontFamily("Merriweather", "merriweather", "Serif", "Lecture longue", "Texte dense, lecture confortable"),
    CoreFontFamily("Spectral", "spectral", "Serif", "Éditorial", "Livres, documents éditoriaux, titres et texte"),
    CoreFontFamily("Alegreya", "alegreya", "Serif", "Éditorial", "Littérature et lecture longue"),
    CoreFontFamily("Vollkorn", "vollkorn", "Serif", "Éditorial", "Corps de texte robuste, ouvrages longs"),
    CoreFontFamily("Libre Baskerville", "librebaskerville", "Serif", "Classiques éditoriaux", "Texte courant, essais"),
    CoreFontFamily("Noto Serif", "notoserif", "Serif", "Noto", "Multilingue, texte courant"),
    CoreFontFamily("IBM Plex Serif", "ibmplexserif", "Serif", "IBM Plex", "Édition moderne, documentation"),
    CoreFontFamily("Charis SIL", "charissil", "Serif", "SIL", "Longs documents, langues et signes étendus"),
    CoreFontFamily("Gentium Plus", "gentiumplus", "Serif", "SIL", "Édition multilingue et universitaire"),
    CoreFontFamily("Carlito", "carlito", "Sans-serif", "Compatibilité métrique", "Alternative métrique à Calibri pour documents importés"),
    CoreFontFamily("Caladea", "caladea", "Serif", "Compatibilité métrique", "Alternative métrique à Cambria pour documents importés"),
    CoreFontFamily("Arimo", "arimo", "Sans-serif", "Compatibilité métrique", "Alternative métrique à Arial pour documents importés"),
    CoreFontFamily("Tinos", "tinos", "Serif", "Compatibilité métrique", "Alternative métrique à Times New Roman"),
    CoreFontFamily("Cousine", "cousine", "Monospace", "Compatibilité métrique", "Alternative métrique à Courier New"),
    CoreFontFamily("Gelasio", "gelasio", "Serif", "Compatibilité métrique", "Alternative métrique à Georgia"),
    CoreFontFamily("Source Sans 3", "sourcesans3", "Sans-serif", "Adobe Source", "Titres, légendes, documentation"),
    CoreFontFamily("Inter", "inter", "Sans-serif", "Sans modernes", "Titres, tableaux, documents contemporains"),
    CoreFontFamily("Fira Sans", "firasans", "Sans-serif", "Sans modernes", "Titres, encadrés, documentation"),
    CoreFontFamily("Noto Sans", "notosans", "Sans-serif", "Noto", "Multilingue, documentation, légendes"),
    CoreFontFamily("IBM Plex Sans", "ibmplexsans", "Sans-serif", "IBM Plex", "Titres, documentation, édition moderne"),
    CoreFontFamily("Atkinson Hyperlegible", "atkinsonhyperlegible", "Sans-serif", "Accessibilité", "Lisibilité renforcée"),
    CoreFontFamily("Alegreya Sans", "alegreyasans", "Sans-serif", "Éditorial", "Titres et texte humaniste"),
    CoreFontFamily("Libre Franklin", "librefranklin", "Sans-serif", "Sans modernes", "Titres, documentation, affichage"),
    CoreFontFamily("Open Sans", "opensans", "Sans-serif", "Usages très répandus", "Documents importés, documentation, texte courant"),
    CoreFontFamily("PT Sans", "ptsans", "Sans-serif", "Usages éditoriaux", "Documentation, légendes, texte courant"),
    CoreFontFamily("PT Serif", "ptserif", "Serif", "Usages éditoriaux", "Livres, essais, texte courant"),
    CoreFontFamily("Roboto", "roboto", "Sans-serif", "Usages très répandus", "Documents importés, titres, texte courant"),
    CoreFontFamily("Lato", "lato", "Sans-serif", "Usages très répandus", "Documents importés, édition générale"),
    CoreFontFamily("Montserrat", "montserrat", "Sans-serif", "Usages très répandus", "Titres, couvertures, documents illustrés"),
    CoreFontFamily("Poppins", "poppins", "Sans-serif", "Usages très répandus", "Titres, documents illustrés, modèles bureautiques"),
    CoreFontFamily("Nunito Sans", "nunitosans", "Sans-serif", "Sans modernes", "Documents contemporains, titres et légendes"),
    CoreFontFamily("Work Sans", "worksans", "Sans-serif", "Sans modernes", "Documentation, titres, texte contemporain"),
    CoreFontFamily("Raleway", "raleway", "Sans-serif", "Titres", "Titres, ouvertures, documents illustrés"),
    CoreFontFamily("Oswald", "oswald", "Sans condensée", "Titres", "Titres étroits, affichage, couvertures"),
    CoreFontFamily("Bitter", "bitter", "Serif", "Éditorial", "Texte courant, essais, documents numériques"),
    CoreFontFamily("Cardo", "cardo", "Serif", "Édition savante", "Ouvrages universitaires, historiques, caractères étendus"),
    CoreFontFamily("Playfair Display", "playfairdisplay", "Display serif", "Titres", "Titres et ouvertures de chapitres"),
    CoreFontFamily("Cormorant Garamond", "cormorantgaramond", "Display serif", "Titres", "Titres élégants, ouvrages illustrés"),
    CoreFontFamily("IBM Plex Sans Condensed", "ibmplexsanscondensed", "Sans condensée", "IBM Plex", "Titres étroits, tableaux, légendes"),
    CoreFontFamily("IBM Plex Mono", "ibmplexmono", "Monospace", "IBM Plex", "Code, données techniques, tableaux"),
)


@dataclass(frozen=True, slots=True)
class FontLibraryStatus:
    total_families: int
    ready_families: int
    missing_families: tuple[str, ...]
    font_files: int

    @property
    def complete(self) -> bool:
        return self.ready_families == self.total_families


@dataclass(frozen=True, slots=True)
class FontReplacementSuggestion:
    requested: str
    replacement: str
    kind: str
    note: str


# Ces correspondances ne sont JAMAIS appliquées automatiquement. Les entrées
# « metric » servent à préserver au mieux les largeurs et donc les retours à la
# ligne lorsqu'une police propriétaire manque. Les entrées « visual » ne sont
# que des pistes proches et exigent encore davantage une validation utilisateur.
_METRIC_REPLACEMENTS: dict[str, tuple[str, str]] = {
    "calibri": ("Carlito", "Compatible métriquement avec Calibri"),
    "cambria": ("Caladea", "Compatible métriquement avec Cambria"),
    "arial": ("Arimo", "Compatible métriquement avec Arial"),
    "times new roman": ("Tinos", "Compatible métriquement avec Times New Roman"),
    "courier new": ("Cousine", "Compatible métriquement avec Courier New"),
    "georgia": ("Gelasio", "Compatible métriquement avec Georgia"),
}

_VISUAL_REPLACEMENTS: dict[str, tuple[str, ...]] = {
    "garamond": ("EB Garamond", "Cormorant Garamond"),
    "baskerville": ("Libre Baskerville",),
    "minion": ("Source Serif 4", "Crimson Pro"),
    "franklin gothic": ("Libre Franklin",),
    "avenir": ("Fira Sans", "Montserrat"),
    "futura": ("Montserrat", "Poppins"),
    "segoe ui": ("Open Sans", "Source Sans 3"),
}

def replacement_suggestions(requested_family: str) -> tuple[FontReplacementSuggestion, ...]:
    """Propose des remplacements sans jamais les appliquer silencieusement."""
    raw = " ".join(str(requested_family or "").strip().casefold().split())
    if not raw:
        return ()

    metric = _METRIC_REPLACEMENTS.get(raw)
    if metric is not None:
        replacement, note = metric
        return (FontReplacementSuggestion(requested_family, replacement, "metric", note),)

    visual = _VISUAL_REPLACEMENTS.get(raw, ())
    return tuple(
        FontReplacementSuggestion(
            requested=requested_family,
            replacement=name,
            kind="visual",
            note="Police visuellement proche : la recomposition peut modifier les lignes et la pagination",
        )
        for name in visual
    )


def project_root() -> Path:
    override = os.environ.get("TOMELINEA_PROJECT_ROOT", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parents[2]


def font_root() -> Path:
    override = os.environ.get("TOMELINEA_FONT_ROOT", "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return project_root() / "resources" / "fonts"


def core_font_root() -> Path:
    return font_root() / "core"


def user_font_root() -> Path:
    return font_root() / "user"


def _safe_folder_name(value: str) -> str:
    safe = "".join(ch if ch.isalnum() else "_" for ch in str(value).strip())
    safe = "_".join(part for part in safe.split("_") if part)
    return safe or "font"


def _request_json(url: str, timeout: float = 30.0):
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "TomeLinea-V4-FontLibrary/1.0",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def _download_file(url: str, destination: Path, timeout: float = 60.0) -> None:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "TomeLinea-V4-FontLibrary/1.0"},
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        with destination.open("wb") as output:
            shutil.copyfileobj(response, output)


def _family_ready(folder: Path) -> bool:
    if not folder.is_dir():
        return False
    return any(path.suffix.lower() in FONT_EXTENSIONS for path in folder.iterdir() if path.is_file())


def catalog_by_name() -> dict[str, CoreFontFamily]:
    return {item.family.casefold(): item for item in CORE_FONT_FAMILIES}


def core_library_status() -> FontLibraryStatus:
    root = core_font_root()
    ready = 0
    missing: list[str] = []
    font_files = 0
    for item in CORE_FONT_FAMILIES:
        folder = root / item.slug
        files = [
            path for path in folder.glob("*")
            if path.is_file() and path.suffix.lower() in FONT_EXTENSIONS
        ] if folder.is_dir() else []
        if files:
            ready += 1
            font_files += len(files)
        else:
            missing.append(item.family)
    return FontLibraryStatus(
        total_families=len(CORE_FONT_FAMILIES),
        ready_families=ready,
        missing_families=tuple(missing),
        font_files=font_files,
    )


def _write_catalog_manifest(root: Path) -> None:
    payload = {
        "catalog_version": CATALOG_VERSION,
        "provider": "google/fonts",
        "provider_url": "https://github.com/google/fonts",
        "families": [asdict(item) | {"source_url": item.source_url} for item in CORE_FONT_FAMILIES],
    }
    root.mkdir(parents=True, exist_ok=True)
    (root / "catalog.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def install_core_family(
    family: CoreFontFamily,
    *,
    force: bool = False,
    timeout: float = 30.0,
) -> tuple[bool, str]:
    destination = core_font_root() / family.slug
    if _family_ready(destination) and not force:
        return True, "déjà présente"

    api_url = (
        f"{GOOGLE_FONTS_API}/{family.license_dir}/{family.slug}"
        f"?ref=main"
    )

    try:
        entries = _request_json(api_url, timeout=timeout)
    except urllib.error.HTTPError as exc:
        return False, f"source indisponible (HTTP {exc.code})"
    except Exception as exc:
        return False, f"source indisponible ({exc})"

    if not isinstance(entries, list):
        return False, "réponse de source inattendue"

    wanted: list[tuple[str, str]] = []
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("type") != "file":
            continue
        name = str(entry.get("name", ""))
        download_url = str(entry.get("download_url", "") or "")
        suffix = Path(name).suffix.lower()
        is_font = suffix in FONT_EXTENSIONS
        is_metadata = name.lower() in {
            "ofl.txt",
            "license.txt",
            "license.md",
            "metadata.pb",
            "fontlog.txt",
            "description.en_us.html",
        }
        if download_url and (is_font or is_metadata):
            wanted.append((name, download_url))

    if not any(Path(name).suffix.lower() in FONT_EXTENSIONS for name, _ in wanted):
        return False, "aucun fichier de police trouvé dans la source"

    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(prefix=f"tl_font_{family.slug}_", dir=str(destination.parent)))
    try:
        for name, download_url in wanted:
            _download_file(download_url, temp_dir / name, timeout=max(timeout, 60.0))

        metadata = {
            "family": family.family,
            "slug": family.slug,
            "category": family.category,
            "collection": family.collection,
            "use": family.use,
            "license": family.license,
            "source_url": family.source_url,
            "provider": "google/fonts",
        }
        (temp_dir / "tomelinea.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        if destination.exists():
            shutil.rmtree(destination)
        temp_dir.replace(destination)
        return True, "installée"
    except Exception as exc:
        return False, f"échec du téléchargement ({exc})"
    finally:
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)


def install_core_library(
    *,
    force: bool = False,
    progress: Callable[[int, int, CoreFontFamily, bool, str], None] | None = None,
) -> dict[str, object]:
    root = core_font_root()
    root.mkdir(parents=True, exist_ok=True)
    user_font_root().mkdir(parents=True, exist_ok=True)
    _write_catalog_manifest(font_root())

    successes: list[str] = []
    failures: dict[str, str] = {}
    total = len(CORE_FONT_FAMILIES)

    for index, family in enumerate(CORE_FONT_FAMILIES, start=1):
        ok, message = install_core_family(family, force=force)
        if ok:
            successes.append(family.family)
        else:
            failures[family.family] = message
        if progress is not None:
            progress(index, total, family, ok, message)

    return {
        "successes": successes,
        "failures": failures,
        "status": asdict(core_library_status()),
    }


def discover_font_files() -> tuple[Path, ...]:
    root = font_root()
    if not root.exists():
        return ()
    paths = [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in FONT_EXTENSIONS
    ]
    return tuple(sorted(paths, key=lambda p: str(p).casefold()))


def register_private_font_file(path: str | Path) -> bool:
    """Rend la police disponible au processus courant sans installation système."""
    path = Path(path)
    if sys.platform != "win32" or not path.is_file():
        return False
    FR_PRIVATE = 0x10
    try:
        added = ctypes.windll.gdi32.AddFontResourceExW(str(path), FR_PRIVATE, 0)
        return bool(added)
    except Exception:
        return False


def register_private_fonts() -> int:
    if sys.platform != "win32":
        return 0
    count = 0
    for path in discover_font_files():
        if register_private_font_file(path):
            count += 1
    return count


def _inspect_font(path: Path) -> tuple[str, str]:
    try:
        from PIL import ImageFont
    except ImportError as exc:
        raise RuntimeError("Pillow est nécessaire pour inspecter une police.") from exc
    font = ImageFont.truetype(str(path), size=12)
    family, style = font.getname()
    return str(family or "").strip(), str(style or "").strip()


def add_user_font(
    source: str | Path,
    *,
    register: bool = True,
) -> dict[str, str]:
    """Ajoute une police fournie par l'utilisateur à la bibliothèque TomeLinea.

    Aucun jugement de licence n'est fait ici : le fichier vient explicitement de
    l'utilisateur. L'interface devra rappeler qu'il lui appartient de disposer
    des droits nécessaires.
    """
    source = Path(source).expanduser().resolve()
    if not source.is_file():
        raise FileNotFoundError(source)
    if source.suffix.lower() not in FONT_EXTENSIONS:
        raise ValueError("Format de police non pris en charge (TTF/OTF/TTC uniquement).")

    family, style = _inspect_font(source)
    if not family:
        raise ValueError("Le nom de famille de la police n'a pas pu être lu.")

    destination_dir = user_font_root() / _safe_folder_name(family)
    destination_dir.mkdir(parents=True, exist_ok=True)
    destination = destination_dir / source.name

    if source != destination:
        shutil.copy2(source, destination)

    manifest_path = destination_dir / "tomelinea-user-fonts.json"
    existing: list[dict[str, str]] = []
    if manifest_path.is_file():
        try:
            raw = json.loads(manifest_path.read_text(encoding="utf-8"))
            if isinstance(raw, list):
                existing = [item for item in raw if isinstance(item, dict)]
        except Exception:
            existing = []

    record = {
        "family": family,
        "style": style,
        "file": destination.name,
        "origin": "user",
    }
    existing = [item for item in existing if item.get("file") != destination.name]
    existing.append(record)
    manifest_path.write_text(
        json.dumps(existing, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if register:
        register_private_font_file(destination)
        try:
            from src.v4.font_availability import installed_fonts
            installed_fonts.cache_clear()
        except Exception:
            pass

    return record | {"path": str(destination)}


def _progress_console(index: int, total: int, family: CoreFontFamily, ok: bool, message: str) -> None:
    marker = "OK" if ok else "!!"
    print(f"[{index:02d}/{total:02d}] {marker} {family.family}: {message}", flush=True)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Bibliothèque de polices TomeLinea")
    parser.add_argument("--install-core", action="store_true", help="Télécharge le socle de polices libres TomeLinea")
    parser.add_argument("--force", action="store_true", help="Retélécharge les familles déjà présentes")
    parser.add_argument("--status", action="store_true", help="Affiche l'état de la bibliothèque")
    parser.add_argument("--add", metavar="FONT_FILE", help="Ajoute une police utilisateur TTF/OTF/TTC")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.install_core:
        print("TomeLinea — préparation de la bibliothèque de polices libres")
        result = install_core_library(force=args.force, progress=_progress_console)
        failures = result["failures"]
        status = core_library_status()
        print(f"Bibliothèque : {status.ready_families}/{status.total_families} familles prêtes, {status.font_files} fichiers de police.")
        if failures:
            print("Certaines familles n'ont pas pu être récupérées maintenant :")
            for name, reason in failures.items():
                print(f" - {name}: {reason}")
            return 2
        return 0

    if args.add:
        record = add_user_font(args.add)
        print(f"Ajoutée : {record['family']} — {record['style']} ({record['path']})")
        return 0

    status = core_library_status()
    print(json.dumps(asdict(status), ensure_ascii=False, indent=2))
    return 0 if status.complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
