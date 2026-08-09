from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil
import struct
import zipfile

PROJECT = Path(r"C:\Users\PC\projet")
DOWNLOADS = Path.home() / "Downloads"
TARGET = PROJECT / "assets" / "page_thumbnails"

EXPECTED = {
    "type_page_couverture.png",
    "type_page_deuxieme_couverture.png",
    "type_page_titre.png",
    "type_page_sommaire.png",
    "type_page_avant_propos.png",
    "type_page_chapitre.png",
    "type_page_fiche.png",
    "type_page_texte.png",
    "type_page_illustration.png",
    "type_page_transition.png",
    "type_page_blanche.png",
    "type_page_conclusion.png",
    "type_page_troisieme_couverture.png",
    "type_page_quatrieme_couverture.png",
    "type_page_personnalisee.png",
}


def fail(message: str) -> None:
    raise SystemExit(f"ERREUR : {message}\nAucun fichier du logiciel n'a été modifié.")


def png_size(data: bytes) -> tuple[int, int]:
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("ce n'est pas un PNG valide")
    if data[12:16] != b"IHDR":
        raise ValueError("en-tête PNG IHDR absent")
    return struct.unpack(">II", data[16:24])


def find_zip() -> Path:
    candidates = sorted(
        DOWNLOADS.glob("PageMaitre_bibliotheque_types_pages_FINAL*.zip"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        fail(
            "archive introuvable dans Téléchargements. "
            "Le nom doit commencer par PageMaitre_bibliotheque_types_pages_FINAL"
        )
    return candidates[0]


def main() -> None:
    archive = find_zip()

    with zipfile.ZipFile(archive, "r") as zf:
        files = {
            Path(name).name: name
            for name in zf.namelist()
            if name and not name.endswith("/")
        }

        missing = sorted(EXPECTED - set(files))
        extra = sorted(set(files) - EXPECTED)

        if missing:
            fail("images manquantes : " + ", ".join(missing))
        if extra:
            fail("fichiers inattendus dans l'archive : " + ", ".join(extra))

        checked: dict[str, bytes] = {}
        for filename in sorted(EXPECTED):
            data = zf.read(files[filename])
            width, height = png_size(data)
            if (width, height) != (300, 424):
                fail(
                    f"{filename} mesure {width}x{height} px au lieu de 300x424 px"
                )
            checked[filename] = data

    backup = None
    if TARGET.exists() and any(TARGET.iterdir()):
        backup_root = PROJECT / "cache" / "correctifs"
        backup_root.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup = backup_root / f"page_thumbnails_avant_installation_{stamp}"
        shutil.copytree(TARGET, backup)

    TARGET.mkdir(parents=True, exist_ok=True)

    # Nettoie uniquement les anciennes miniatures standards connues.
    for filename in EXPECTED:
        old = TARGET / filename
        if old.exists():
            old.unlink()

    for filename, data in checked.items():
        (TARGET / filename).write_bytes(data)

    print("BIBLIOTHEQUE_MINIATURES_OK")
    print(f"Archive utilisée : {archive}")
    print(f"Dossier installé : {TARGET}")
    print("15 PNG vérifiés : 300 x 424 px.")
    print("14 types standards + 1 miniature personnalisée générique.")
    if backup is not None:
        print(f"Sauvegarde précédente : {backup}")
    print("Aucun code de PageMaître n'a encore été modifié.")


if __name__ == "__main__":
    main()
