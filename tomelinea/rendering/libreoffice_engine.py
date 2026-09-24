from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import time
from typing import Iterable


class LayoutEngineError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class LibreOfficeEngine:
    executable: Path
    origin: str

    @property
    def is_embedded(self) -> bool:
        return self.origin in {"environment", "embedded_project", "embedded_app"}


@dataclass(frozen=True, slots=True)
class RenderResult:
    source_path: Path
    pdf_path: Path
    engine: LibreOfficeEngine
    elapsed_seconds: float
    stdout: str
    stderr: str
    source_sha256_before: str
    source_sha256_after: str

    @property
    def source_unchanged(self) -> bool:
        return self.source_sha256_before == self.source_sha256_after


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _program_candidates(home: Path) -> Iterable[Path]:
    home = home.expanduser()
    yield home / "program" / "soffice.com"
    yield home / "program" / "soffice.exe"
    yield home / "soffice.com"
    yield home / "soffice.exe"


def locate_libreoffice_engine(*, project_root: str | Path | None = None) -> LibreOfficeEngine:
    env_home = os.environ.get("TOMELINEA_LIBREOFFICE_HOME")
    if env_home:
        for candidate in _program_candidates(Path(env_home)):
            if candidate.is_file():
                return LibreOfficeEngine(candidate.resolve(), "environment")

    root = (
        Path(project_root).expanduser().resolve()
        if project_root is not None
        else Path(__file__).resolve().parents[2]
    )

    for candidate in _program_candidates(root / "resources" / "libreoffice"):
        if candidate.is_file():
            return LibreOfficeEngine(candidate.resolve(), "embedded_project")

    app_root = Path(sys.executable).resolve().parent
    for candidate in _program_candidates(app_root / "libreoffice"):
        if candidate.is_file():
            return LibreOfficeEngine(candidate.resolve(), "embedded_app")

    system_candidates: list[Path] = []
    for env_name in ("ProgramFiles", "ProgramFiles(x86)"):
        value = os.environ.get(env_name)
        if value:
            system_candidates.extend(_program_candidates(Path(value) / "LibreOffice"))

    for candidate in system_candidates:
        if candidate.is_file():
            return LibreOfficeEngine(candidate.resolve(), "system")

    found = shutil.which("soffice.com") or shutil.which("soffice")
    if found:
        return LibreOfficeEngine(Path(found).resolve(), "system_path")

    raise LayoutEngineError(
        "Moteur LibreOffice introuvable. "
        "La distribution TomeLinea devra embarquer son propre moteur."
    )


def render_document_to_pdf(
    source: str | Path,
    output_dir: str | Path,
    *,
    engine: LibreOfficeEngine | None = None,
    timeout_seconds: float = 120.0,
) -> RenderResult:
    source_path = Path(source).expanduser().resolve()
    if not source_path.is_file():
        raise FileNotFoundError(source_path)
    if source_path.suffix.lower() not in {".docx", ".odt"}:
        raise ValueError("Le moteur accepte DOCX ou ODT.")

    out_dir = Path(output_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    layout_engine = engine or locate_libreoffice_engine()
    executable = layout_engine.executable
    expected_pdf = out_dir / f"{source_path.stem}.pdf"

    if expected_pdf.exists():
        expected_pdf.unlink()

    before = _sha256(source_path)
    started = time.monotonic()

    with tempfile.TemporaryDirectory(prefix="TL_LO_PROFILE_") as profile:
        profile_uri = Path(profile).resolve().as_uri()
        args = [
            str(executable),
            f"-env:UserInstallation={profile_uri}",
            "--headless",
            "--convert-to",
            "pdf:writer_pdf_Export",
            "--outdir",
            str(out_dir),
            str(source_path),
        ]

        creationflags = 0
        if os.name == "nt" and hasattr(subprocess, "CREATE_NO_WINDOW"):
            creationflags = subprocess.CREATE_NO_WINDOW

        try:
            completed = subprocess.run(
                args,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=timeout_seconds,
                check=False,
                creationflags=creationflags,
            )
        except subprocess.TimeoutExpired as exc:
            raise LayoutEngineError(
                f"Le moteur n'a pas terminé en {timeout_seconds:.0f} s."
            ) from exc

    elapsed = time.monotonic() - started
    after = _sha256(source_path)

    if before != after:
        raise LayoutEngineError("Le document de travail a changé pendant le rendu.")
    if completed.returncode != 0:
        raise LayoutEngineError(
            f"LibreOffice a échoué (code {completed.returncode}).\n"
            f"{completed.stdout}\n{completed.stderr}"
        )
    if not expected_pdf.is_file():
        raise LayoutEngineError(
            "LibreOffice a terminé sans produire le PDF attendu : "
            f"{expected_pdf}"
        )

    return RenderResult(
        source_path=source_path,
        pdf_path=expected_pdf,
        engine=layout_engine,
        elapsed_seconds=elapsed,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
        source_sha256_before=before,
        source_sha256_after=after,
    )