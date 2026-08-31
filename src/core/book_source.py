from __future__ import annotations

"""
TomeLinea — Source du livre V2

Brique commune du moteur "Source du livre".

V2 :
- PDF : comptage des pages et format ;
- stockage de la source originale dans un projet TomeLinea ;
- manifeste source_livre.json ;
- rendu local d'une page PDF en PNG pour Structure / Gabarits ;
- API PyMuPDF moderne : import pymupdf.

Cette brique reste indépendante de l'interface.
"""

from dataclasses import asdict, dataclass
from datetime import datetime
import argparse
import json
from pathlib import Path
import shutil
from typing import Any


SOURCE_MANIFEST_VERSION = 2


@dataclass
class SourcePage:
    source_page: int
    width_pt: float | None = None
    height_pt: float | None = None


@dataclass
class BookSourceInfo:
    version: int
    source_name: str
    source_type: str
    source_path: str
    page_count: int
    backend: str
    inspected_at: str
    pages: list[SourcePage]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _load_pymupdf():
    try:
        import pymupdf
        return pymupdf
    except Exception:
        return None


def _inspect_with_pymupdf(path: Path) -> BookSourceInfo | None:
    pymupdf = _load_pymupdf()
    if pymupdf is None:
        return None

    doc = pymupdf.open(str(path))
    try:
        pages: list[SourcePage] = []
        for index in range(len(doc)):
            page = doc[index]
            rect = page.rect
            pages.append(
                SourcePage(
                    source_page=index + 1,
                    width_pt=round(float(rect.width), 3),
                    height_pt=round(float(rect.height), 3),
                )
            )

        return BookSourceInfo(
            version=SOURCE_MANIFEST_VERSION,
            source_name=path.name,
            source_type="pdf",
            source_path=str(path.resolve()),
            page_count=len(pages),
            backend="PyMuPDF",
            inspected_at=datetime.now().isoformat(),
            pages=pages,
        )
    finally:
        doc.close()


def _inspect_with_pypdf(path: Path) -> BookSourceInfo | None:
    reader_cls = None
    backend = ""

    try:
        from pypdf import PdfReader
        reader_cls = PdfReader
        backend = "pypdf"
    except Exception:
        try:
            from PyPDF2 import PdfReader
            reader_cls = PdfReader
            backend = "PyPDF2"
        except Exception:
            return None

    reader = reader_cls(str(path))
    pages: list[SourcePage] = []

    for index, page in enumerate(reader.pages):
        width = None
        height = None
        try:
            box = page.mediabox
            width = round(float(box.width), 3)
            height = round(float(box.height), 3)
        except Exception:
            pass

        pages.append(
            SourcePage(
                source_page=index + 1,
                width_pt=width,
                height_pt=height,
            )
        )

    return BookSourceInfo(
        version=SOURCE_MANIFEST_VERSION,
        source_name=path.name,
        source_type="pdf",
        source_path=str(path.resolve()),
        page_count=len(pages),
        backend=backend,
        inspected_at=datetime.now().isoformat(),
        pages=pages,
    )


def inspect_pdf(source: str | Path) -> BookSourceInfo:
    path = Path(source).expanduser().resolve()

    if not path.is_file():
        raise FileNotFoundError(f"Fichier source introuvable : {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Source V2 : seul le PDF est analysé pour le moment.")

    for inspector in (_inspect_with_pymupdf, _inspect_with_pypdf):
        info = inspector(path)
        if info is not None:
            return info

    raise RuntimeError(
        "Aucun moteur PDF disponible. "
        "Installer PyMuPDF avec : python -m pip install PyMuPDF"
    )


def render_pdf_page(
    source: str | Path,
    page_number: int,
    output_path: str | Path,
    *,
    max_width: int = 1400,
) -> Path:
    """
    Rend une page PDF en PNG local.

    page_number est basé sur 1, comme les numéros vus par l'utilisateur.
    Le PDF original n'est jamais modifié.
    """
    pymupdf = _load_pymupdf()
    if pymupdf is None:
        raise RuntimeError(
            "PyMuPDF est requis pour rendre une page PDF."
        )

    source_path = Path(source).expanduser().resolve()
    if not source_path.is_file():
        raise FileNotFoundError(f"Fichier source introuvable : {source_path}")

    doc = pymupdf.open(str(source_path))
    try:
        if page_number < 1 or page_number > len(doc):
            raise IndexError(
                f"Page source invalide : {page_number} "
                f"(document de {len(doc)} pages)."
            )

        page = doc[page_number - 1]
        rect = page.rect

        if rect.width <= 0:
            zoom = 1.0
        else:
            zoom = min(4.0, max(0.5, float(max_width) / float(rect.width)))

        matrix = pymupdf.Matrix(zoom, zoom)
        pix = page.get_pixmap(
            matrix=matrix,
            alpha=False,
        )

        target = Path(output_path).expanduser().resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        pix.save(str(target))
        return target
    finally:
        doc.close()


def sources_folder(project_root: str | Path) -> Path:
    root = Path(project_root).expanduser().resolve()
    return root / "sources_originales"


def source_cache_folder(project_root: str | Path) -> Path:
    root = Path(project_root).expanduser().resolve()
    return root / "cache" / "source_livre"


def load_project_source(
    project_root: str | Path,
) -> tuple[Path, BookSourceInfo]:
    """Retourne la Source du livre enregistrée et ses métadonnées.

    La source reste référencée par un chemin relatif au projet dans
    ``sources_originales/source_livre.json``. Cette fonction constitue le
    point d'entrée commun pour Structure, Gabarits et Production.
    """
    root = Path(project_root).expanduser().resolve()
    manifest = sources_folder(root) / "source_livre.json"

    if not manifest.is_file():
        raise FileNotFoundError(
            "Aucune Source du livre enregistrée dans ce projet."
        )

    data = json.loads(manifest.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Le manifeste de la Source du livre est invalide.")

    relative_source = str(data.get("source_path", "")).strip()
    if not relative_source:
        raise ValueError("Le manifeste ne contient pas de source_path.")

    source = (root / relative_source).resolve()
    if not source.is_file():
        raise FileNotFoundError(f"Fichier source introuvable : {source}")

    raw_pages = data.get("pages", [])
    pages: list[SourcePage] = []
    if isinstance(raw_pages, list):
        for index, raw in enumerate(raw_pages, start=1):
            if not isinstance(raw, dict):
                continue
            pages.append(
                SourcePage(
                    source_page=int(raw.get("source_page", index)),
                    width_pt=(
                        float(raw["width_pt"])
                        if raw.get("width_pt") is not None
                        else None
                    ),
                    height_pt=(
                        float(raw["height_pt"])
                        if raw.get("height_pt") is not None
                        else None
                    ),
                )
            )

    page_count = int(data.get("page_count", len(pages)) or len(pages))
    if page_count < 1:
        raise ValueError("La Source du livre ne contient aucune page.")

    if not pages:
        pages = [SourcePage(source_page=index) for index in range(1, page_count + 1)]

    info = BookSourceInfo(
        version=int(data.get("version", SOURCE_MANIFEST_VERSION)),
        source_name=str(data.get("source_name") or source.name),
        source_type=str(data.get("source_type") or source.suffix.lstrip(".")).lower(),
        source_path=relative_source,
        page_count=page_count,
        backend=str(data.get("backend") or ""),
        inspected_at=str(data.get("inspected_at") or ""),
        pages=pages,
    )
    return source, info


def detect_pdf_cover_pages(source: str | Path) -> dict[str, int]:
    """Repère prudemment les faces de couverture explicitement identifiables.

    Le moteur ne cherche pas encore à typer toutes les pages : il reconnaît
    uniquement les mentions très explicites de 2e/3e/4e de couverture.
    La première page n'est considérée comme 1re de couverture que lorsque le
    document présente aussi une 2e de couverture en page 2 et une 4e en fin de
    document. Cette règle évite de prendre une simple page de titre pour une
    couverture dans un manuscrit ordinaire.
    """
    path = Path(source).expanduser().resolve()
    if path.suffix.lower() != ".pdf" or not path.is_file():
        return {}

    pymupdf = _load_pymupdf()
    if pymupdf is None:
        return {}

    import unicodedata

    def normalized(text: str) -> str:
        folded = unicodedata.normalize("NFKD", str(text or ""))
        ascii_text = folded.encode("ascii", "ignore").decode("ascii")
        return " ".join(ascii_text.upper().split())

    roles: dict[str, int] = {}
    doc = pymupdf.open(str(path))
    try:
        page_count = len(doc)
        for index in range(page_count):
            try:
                raw_text = doc[index].get_text("text")
            except Exception:
                raw_text = ""
            lines = [normalized(line) for line in str(raw_text or "").splitlines() if str(line).strip()]
            heading = lines[0] if lines else ""
            page_number = index + 1
            if heading.startswith("2E DE COUVERTURE") or heading.startswith("DEUXIEME DE COUVERTURE"):
                roles.setdefault("second_cover", page_number)
            if heading.startswith("3E DE COUVERTURE") or heading.startswith("TROISIEME DE COUVERTURE"):
                roles.setdefault("third_cover", page_number)
            if heading.startswith("4E DE COUVERTURE") or heading.startswith("QUATRIEME DE COUVERTURE"):
                roles.setdefault("back_cover", page_number)
            if (
                heading.startswith("1RE DE COUVERTURE")
                or heading.startswith("1ERE DE COUVERTURE")
                or heading.startswith("PREMIERE DE COUVERTURE")
            ):
                roles.setdefault("front_cover", page_number)

        if (
            "front_cover" not in roles
            and page_count >= 2
            and roles.get("second_cover") == 2
            and roles.get("back_cover") == page_count
        ):
            roles["front_cover"] = 1
    finally:
        doc.close()

    return roles


def render_project_source_page(
    project_root: str | Path,
    page_number: int,
    *,
    max_width: int = 1400,
) -> Path:
    """
    Rend la page source déjà enregistrée dans un projet TomeLinea.
    Le PNG est placé dans cache/source_livre/.
    """
    root = Path(project_root).expanduser().resolve()
    source, _info = load_project_source(root)
    target = (
        source_cache_folder(root)
        / f"page_{int(page_number):04d}_{int(max_width)}.png"
    )

    if target.is_file():
        return target

    return render_pdf_page(
        source,
        page_number,
        target,
        max_width=max_width,
    )


def store_source_in_project(
    project_root: str | Path,
    source: str | Path,
) -> tuple[Path, Path, BookSourceInfo]:
    """
    Copie la source auteur dans le projet et écrit son manifeste.
    """
    root = Path(project_root).expanduser().resolve()
    project_file = root / "projet.json"

    if not project_file.is_file():
        raise FileNotFoundError(
            f"Ce dossier n'est pas un projet TomeLinea : {project_file} absent."
        )

    source_path = Path(source).expanduser().resolve()
    info = inspect_pdf(source_path)

    folder = sources_folder(root)
    folder.mkdir(parents=True, exist_ok=True)

    destination = folder / source_path.name
    if destination.resolve() != source_path.resolve():
        if destination.exists():
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            destination = folder / f"{source_path.stem}_{stamp}{source_path.suffix}"
        shutil.copy2(source_path, destination)

    stored_info = BookSourceInfo(
        version=info.version,
        source_name=destination.name,
        source_type=info.source_type,
        source_path=str(destination.relative_to(root).as_posix()),
        page_count=info.page_count,
        backend=info.backend,
        inspected_at=info.inspected_at,
        pages=info.pages,
    )

    manifest = folder / "source_livre.json"
    temporary = manifest.with_suffix(".tmp")
    temporary.write_text(
        json.dumps(stored_info.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    temporary.replace(manifest)

    return destination, manifest, stored_info


def _print_info(info: BookSourceInfo) -> None:
    print("TOMELINEA · SOURCE DU LIVRE V2")
    print(f"Fichier       : {info.source_name}")
    print(f"Type          : {info.source_type.upper()}")
    print(f"Moteur PDF    : {info.backend}")
    print(f"Pages         : {info.page_count}")

    sizes = {
        (page.width_pt, page.height_pt)
        for page in info.pages
        if page.width_pt is not None and page.height_pt is not None
    }

    if len(sizes) == 1:
        width, height = next(iter(sizes))
        print(f"Format unique : {width:g} × {height:g} pt")
    elif sizes:
        print(f"Formats       : {len(sizes)} formats différents")
    else:
        print("Format        : non relevé")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspecte, stocke ou rend la Source du livre TomeLinea."
    )
    parser.add_argument("source", nargs="?", help="PDF source auteur")
    parser.add_argument(
        "--project",
        help="Dossier d'un projet TomeLinea : copie la source et crée le manifeste.",
    )
    parser.add_argument(
        "--render-page",
        type=int,
        help="Rend cette page PDF en PNG.",
    )
    parser.add_argument(
        "--output",
        help="Fichier PNG de sortie pour --render-page.",
    )
    parser.add_argument(
        "--width",
        type=int,
        default=1400,
        help="Largeur de rendu cible en pixels (défaut : 1400).",
    )
    args = parser.parse_args()

    if not args.source:
        parser.error("un PDF source est requis")

    if args.render_page is not None:
        target = args.output or f"source_page_{args.render_page:04d}.png"
        rendered = render_pdf_page(
            args.source,
            args.render_page,
            target,
            max_width=args.width,
        )
        print("TOMELINEA · RENDU SOURCE : OK")
        print(f"Page          : {args.render_page}")
        print(f"PNG           : {rendered}")
        return 0

    if args.project:
        destination, manifest, info = store_source_in_project(
            args.project,
            args.source,
        )
        _print_info(info)
        print("")
        print(f"Source copiée : {destination}")
        print(f"Manifeste     : {manifest}")
        return 0

    info = inspect_pdf(args.source)
    _print_info(info)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
