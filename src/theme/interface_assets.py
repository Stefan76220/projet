from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class InterfaceAssets:
    """Accès aux ressources visuelles internes de PageMaître."""

    APPLICATION_ROOT = Path(__file__).resolve().parents[2]
    ROOT = APPLICATION_ROOT / "assets" / "interface"

    CATALOG = ROOT / "catalogue.json"

    TEXTURES = ROOT / "textures"

    DECORS = ROOT / "decors"
    CORNERS = DECORS / "coins"
    WATERMARKS = DECORS / "filigranes"
    SEPARATORS = DECORS / "separateurs"
    BANNERS = DECORS / "bandeaux"
    BOOKS_AND_PAPER = DECORS / "livres_et_papier"

    ICONS = ROOT / "icones"
    STANDARD_ICONS = ICONS / "standard"
    CUSTOM_ICONS = ICONS / "personnalisees"

    @classmethod
    def path(cls, family: str, filename: str) -> Path:
        folders = {
            "textures": cls.TEXTURES,
            "coins": cls.CORNERS,
            "filigranes": cls.WATERMARKS,
            "separateurs": cls.SEPARATORS,
            "bandeaux": cls.BANNERS,
            "livres_et_papier": cls.BOOKS_AND_PAPER,
            "icones_standard": cls.STANDARD_ICONS,
            "icones_personnalisees": cls.CUSTOM_ICONS,
        }

        key = str(family).strip().lower()

        if key not in folders:
            raise KeyError(
                f"Famille de ressource inconnue : {family}"
            )

        clean_filename = str(filename).strip()

        if not clean_filename:
            raise ValueError(
                "Le nom du fichier est obligatoire."
            )

        return folders[key] / clean_filename

    @classmethod
    def load_catalog(cls) -> dict[str, Any]:
        if not cls.CATALOG.is_file():
            raise FileNotFoundError(
                f"Catalogue introuvable : {cls.CATALOG}"
            )

        with cls.CATALOG.open(
            "r",
            encoding="utf-8-sig",
        ) as handle:
            data = json.load(handle)

        if not isinstance(data, dict):
            raise ValueError(
                "Le catalogue des ressources d'interface est invalide."
            )

        return data

    @classmethod
    def required_folders(cls) -> tuple[Path, ...]:
        return (
            cls.ROOT,
            cls.TEXTURES,
            cls.DECORS,
            cls.CORNERS,
            cls.WATERMARKS,
            cls.SEPARATORS,
            cls.BANNERS,
            cls.BOOKS_AND_PAPER,
            cls.ICONS,
            cls.STANDARD_ICONS,
            cls.CUSTOM_ICONS,
        )

    @classmethod
    def validate(cls) -> list[str]:
        errors: list[str] = []

        for folder in cls.required_folders():
            if not folder.is_dir():
                errors.append(
                    f"Dossier manquant : {folder}"
                )

        if not cls.CATALOG.is_file():
            errors.append(
                f"Catalogue manquant : {cls.CATALOG}"
            )

        return errors