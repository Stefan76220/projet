from __future__ import annotations

"""Catalogue fermé des formats papier TomeLinea V4.

Le catalogue regroupe les tailles courantes de l'édition française et les
formats fixes des principales plateformes utilisées depuis la France.
Les dimensions libres ne font volontairement pas partie de V4.

Les plateformes sont des métadonnées : elles serviront surtout au bureau
Sortie pour filtrer les formats et appliquer les profils techniques propres à
chaque prestataire.
"""

from dataclasses import dataclass
from math import hypot
from typing import Iterable


PLATFORM_KDP = "Amazon KDP"
PLATFORM_TBE = "TheBookEdition"
PLATFORM_BOOKELIS = "Bookelis"
PLATFORM_COOLLIBRI = "CoolLibri"
PLATFORM_BOD = "BoD"
PLATFORM_LULU = "Lulu"
PLATFORM_FR = "Édition française"


@dataclass(frozen=True, slots=True)
class StandardBookFormat:
    key: str
    label: str
    width_mm: float
    height_mm: float
    family: str
    platforms: tuple[str, ...] = ()

    @property
    def dimensions_label(self) -> str:
        def n(value: float) -> str:
            if abs(value - round(value)) < 1e-9:
                return str(int(round(value)))
            return f"{value:.1f}".replace(".", ",")

        return f"{n(self.width_mm)} × {n(self.height_mm)} mm"

    @property
    def display_label(self) -> str:
        return f"{self.label} — {self.dimensions_label}"


# Sources de maintenance (consultées en septembre 2026) :
# - Amazon KDP : aide « Définir la taille de coupe, le fond perdu et les marges »
# - TheBookEdition : centre d'aide « Quels types de livres et formats sont proposés ? »
# - Bookelis : guide des formats de livres disponibles
# - CoolLibri : page Autoédition de livre
# - BoD France : « Comment choisir son format de livre ? »
# - Lulu : Getting Started with Lulu Guide, Book Sizes
#
# Les tailles presque identiques restent séparées quand une plateforme exige
# ses dimensions exactes (ex. 152 × 229 Lulu et 152,4 × 228,6 KDP).

STANDARD_BOOK_FORMATS: tuple[StandardBookFormat, ...] = (
    # Formats éditoriaux français usuels (hors catalogue POD exact).
    StandardBookFormat("fr_poche_110x180", "Poche français", 110.0, 180.0, "Poche", (PLATFORM_FR,)),
    StandardBookFormat("fr_broche_130x200", "Broché français", 130.0, 200.0, "Roman", (PLATFORM_FR,)),
    StandardBookFormat("fr_broche_140x220", "Grand broché français", 140.0, 220.0, "Roman", (PLATFORM_FR,)),

    # Petits formats / poche / manga.
    StandardBookFormat("lulu_pocket_108x175", "Pocket Book", 108.0, 175.0, "Poche", (PLATFORM_LULU,)),
    StandardBookFormat("tbe_poche_110x170", "Poche", 110.0, 170.0, "Poche", (PLATFORM_TBE, PLATFORM_COOLLIBRI)),
    StandardBookFormat("tbe_romantique_110x200", "Romantique", 110.0, 200.0, "Poche", (PLATFORM_TBE,)),
    StandardBookFormat("tbe_manga_120x180", "Manga", 120.0, 180.0, "Manga", (PLATFORM_TBE,)),
    StandardBookFormat("bod_120x190", "Petit roman / manga", 120.0, 190.0, "Poche", (PLATFORM_BOD,)),
    StandardBookFormat("bookelis_130x180", "Poche classique", 130.0, 180.0, "Poche", (PLATFORM_BOOKELIS,)),

    # Romans et essais, métriques françaises/européennes.
    StandardBookFormat("bod_135x215", "Roman moyen", 135.0, 215.0, "Roman", (PLATFORM_BOD,)),
    StandardBookFormat("a5_148x210", "A5", 148.0, 210.0, "Roman", (PLATFORM_TBE, PLATFORM_BOOKELIS, PLATFORM_COOLLIBRI, PLATFORM_BOD, PLATFORM_LULU)),
    StandardBookFormat("bod_155x220", "Livre pratique", 155.0, 220.0, "Roman", (PLATFORM_BOD,)),
    StandardBookFormat("bookelis_156x234", "Confort", 156.0, 234.0, "Roman", (PLATFORM_BOOKELIS, PLATFORM_LULU)),
    StandardBookFormat("coollibri_160x240", "Roman 16 × 24", 160.0, 240.0, "Roman", (PLATFORM_COOLLIBRI,)),
    StandardBookFormat("bod_170x220", "Livre pratique illustré", 170.0, 220.0, "Grand livre", (PLATFORM_BOD,)),
    StandardBookFormat("bookelis_170x244", "Grand format", 170.0, 244.0, "Grand livre", (PLATFORM_BOOKELIS,)),
    StandardBookFormat("bod_190x270", "Brochure / rapport", 190.0, 270.0, "Grand livre", (PLATFORM_BOD,)),

    # Amazon KDP — tailles de coupe exactes.
    StandardBookFormat("kdp_127x2032", "KDP 5 × 8", 127.0, 203.2, "KDP", (PLATFORM_KDP,)),
    StandardBookFormat("kdp_1285x1984", "KDP 5,06 × 7,81", 128.5, 198.4, "KDP", (PLATFORM_KDP,)),
    StandardBookFormat("kdp_1334x2032", "KDP 5,25 × 8", 133.4, 203.2, "KDP", (PLATFORM_KDP,)),
    StandardBookFormat("kdp_1397x2159", "KDP 5,5 × 8,5", 139.7, 215.9, "KDP", (PLATFORM_KDP,)),
    StandardBookFormat("kdp_1524x2286", "KDP 6 × 9", 152.4, 228.6, "KDP", (PLATFORM_KDP,)),
    StandardBookFormat("kdp_156x2339", "KDP 6,14 × 9,21", 156.0, 233.9, "KDP", (PLATFORM_KDP,)),
    StandardBookFormat("kdp_1699x2441", "KDP 6,69 × 9,61", 169.9, 244.1, "KDP", (PLATFORM_KDP,)),
    StandardBookFormat("kdp_1778x254", "KDP 7 × 10", 177.8, 254.0, "KDP", (PLATFORM_KDP,)),
    StandardBookFormat("kdp_189x2461", "KDP 7,44 × 9,69", 189.0, 246.1, "KDP", (PLATFORM_KDP,)),
    StandardBookFormat("kdp_1905x235", "KDP 7,5 × 9,25", 190.5, 235.0, "KDP", (PLATFORM_KDP,)),
    StandardBookFormat("kdp_2032x254", "KDP 8 × 10", 203.2, 254.0, "KDP", (PLATFORM_KDP,)),
    StandardBookFormat("kdp_landscape_2096x1524", "KDP paysage 8,25 × 6", 209.6, 152.4, "Paysage", (PLATFORM_KDP,)),
    StandardBookFormat("kdp_square_2096", "KDP carré 8,25", 209.6, 209.6, "Carré", (PLATFORM_KDP,)),
    StandardBookFormat("kdp_2096x2794", "KDP 8,25 × 11", 209.6, 279.4, "Grand livre", (PLATFORM_KDP,)),
    StandardBookFormat("kdp_square_2159", "KDP carré 8,5", 215.9, 215.9, "Carré", (PLATFORM_KDP,)),
    StandardBookFormat("kdp_letter_2159x2794", "KDP 8,5 × 11", 215.9, 279.4, "Grand livre", (PLATFORM_KDP,)),

    # Lulu — tailles exactes distinctes de KDP quand nécessaire.
    StandardBookFormat("lulu_novella_127x203", "Novella", 127.0, 203.0, "Roman", (PLATFORM_LULU,)),
    StandardBookFormat("lulu_digest_140x216", "Digest", 140.0, 216.0, "Roman", (PLATFORM_LULU,)),
    StandardBookFormat("lulu_trade_152x229", "US Trade", 152.0, 229.0, "Roman", (PLATFORM_LULU,)),
    StandardBookFormat("lulu_comic_168x260", "Comic Book", 168.0, 260.0, "BD / Comics", (PLATFORM_LULU,)),
    StandardBookFormat("lulu_executive_178x254", "Executive", 178.0, 254.0, "Grand livre", (PLATFORM_LULU,)),
    StandardBookFormat("lulu_crown_189x246", "Crown Quarto", 189.0, 246.0, "Grand livre", (PLATFORM_LULU,)),
    StandardBookFormat("lulu_letter_216x279", "US Letter", 216.0, 279.0, "Grand livre", (PLATFORM_LULU,)),

    # BD, comics et grands formats utilisés en France.
    StandardBookFormat("tbe_comics_160x250", "Comics US", 160.0, 250.0, "BD / Comics", (PLATFORM_TBE,)),
    StandardBookFormat("tbe_mdo_180x260", "MDO / BD", 180.0, 260.0, "BD / Comics", (PLATFORM_TBE,)),
    StandardBookFormat("a4_210x297", "A4", 210.0, 297.0, "Grand livre", (PLATFORM_KDP, PLATFORM_TBE, PLATFORM_BOOKELIS, PLATFORM_COOLLIBRI, PLATFORM_BOD, PLATFORM_LULU)),
    StandardBookFormat("fr_bd_240x320", "BD franco-belge", 240.0, 320.0, "BD / Comics", (PLATFORM_FR,)),

    # Carrés.
    StandardBookFormat("tbe_square_150", "Carré 15", 150.0, 150.0, "Carré", (PLATFORM_TBE,)),
    StandardBookFormat("square_170", "Carré 17", 170.0, 170.0, "Carré", (PLATFORM_BOOKELIS, PLATFORM_BOD)),
    StandardBookFormat("lulu_square_190", "Carré 19", 190.0, 190.0, "Carré", (PLATFORM_LULU,)),
    StandardBookFormat("square_210", "Grand carré 21", 210.0, 210.0, "Carré", (PLATFORM_TBE, PLATFORM_COOLLIBRI, PLATFORM_BOD)),
    StandardBookFormat("lulu_square_216", "Carré 21,6", 216.0, 216.0, "Carré", (PLATFORM_LULU,)),

    # Paysages explicites : pas de rotation générique de tous les formats.
    StandardBookFormat("bookelis_landscape_190x150", "Paysage 19 × 15", 190.0, 150.0, "Paysage", (PLATFORM_TBE, PLATFORM_BOOKELIS)),
    StandardBookFormat("coollibri_a5_landscape", "A5 paysage", 210.0, 148.0, "Paysage", (PLATFORM_COOLLIBRI,)),
    StandardBookFormat("bod_landscape_210x150", "Italienne 21 × 15", 210.0, 150.0, "Paysage", (PLATFORM_BOD,)),
    StandardBookFormat("lulu_small_landscape", "Small Landscape", 229.0, 178.0, "Paysage", (PLATFORM_LULU,)),
    StandardBookFormat("tbe_landscape_260x180", "Paysage rigide 26 × 18", 260.0, 180.0, "Paysage", (PLATFORM_TBE,)),
    StandardBookFormat("lulu_letter_landscape", "US Letter paysage", 279.0, 216.0, "Paysage", (PLATFORM_LULU,)),
    StandardBookFormat("a4_landscape", "A4 paysage", 297.0, 210.0, "Paysage", (PLATFORM_TBE, PLATFORM_COOLLIBRI, PLATFORM_LULU)),
)


UI_FAMILY_ORDER: tuple[str, ...] = (
    "Poche / Manga",
    "Roman",
    "Grand livre / Illustré",
    "BD / Comics",
    "Carré",
    "Paysage",
    "A4 / grands formats",
)


def ui_family_for_format(item: StandardBookFormat) -> str:
    """Famille de navigation compacte utilisée par l'interface Format.

    Le catalogue conserve les familles techniques nécessaires à sa maintenance
    (par exemple les tailles KDP exactes), mais l'utilisateur navigue par type
    de livre plutôt que par plateforme.
    """
    if item.family == "Paysage":
        return "Paysage"
    if item.family == "Carré":
        return "Carré"
    if item.family == "BD / Comics":
        return "BD / Comics"
    if item.width_mm >= 209.0 and item.height_mm >= 270.0:
        return "A4 / grands formats"
    if item.family in {"Poche", "Manga"}:
        return "Poche / Manga"
    if item.family == "Grand livre":
        return "Grand livre / Illustré"
    if item.family == "KDP":
        if item.width_mm <= 170.0 and item.height_mm <= 245.0:
            return "Roman"
        return "Grand livre / Illustré"
    return "Roman"


def formats_by_ui_family() -> tuple[tuple[str, tuple[StandardBookFormat, ...]], ...]:
    grouped: dict[str, list[StandardBookFormat]] = {name: [] for name in UI_FAMILY_ORDER}
    for item in STANDARD_BOOK_FORMATS:
        grouped[ui_family_for_format(item)].append(item)
    for items in grouped.values():
        items.sort(key=lambda fmt: (fmt.width_mm * fmt.height_mm, fmt.width_mm, fmt.height_mm, fmt.label))
    return tuple((name, tuple(grouped[name])) for name in UI_FAMILY_ORDER if grouped[name])


BY_KEY = {item.key: item for item in STANDARD_BOOK_FORMATS}


def formats_by_family() -> tuple[tuple[str, tuple[StandardBookFormat, ...]], ...]:
    families: list[str] = []
    grouped: dict[str, list[StandardBookFormat]] = {}
    for item in STANDARD_BOOK_FORMATS:
        if item.family not in grouped:
            families.append(item.family)
            grouped[item.family] = []
        grouped[item.family].append(item)
    return tuple((family, tuple(grouped[family])) for family in families)


def find_standard_format(
    width_mm: float,
    height_mm: float,
    *,
    tolerance_mm: float = 0.15,
) -> StandardBookFormat | None:
    width = float(width_mm)
    height = float(height_mm)
    for item in STANDARD_BOOK_FORMATS:
        if (
            abs(item.width_mm - width) <= tolerance_mm
            and abs(item.height_mm - height) <= tolerance_mm
        ):
            return item
    return None


def require_standard_format(width_mm: float, height_mm: float) -> StandardBookFormat:
    item = find_standard_format(width_mm, height_mm)
    if item is None:
        raise ValueError(
            "TomeLinea V4 utilise uniquement les formats éditoriaux du catalogue. "
            "Choisissez un format proposé dans Format."
        )
    return item


def nearest_standard_format(width_mm: float, height_mm: float) -> StandardBookFormat:
    """Renvoie la taille standard géométriquement la plus proche.

    Utilisé uniquement pour présélectionner une proposition quand une Source
    importée possède un format qui n'est pas exactement dans le catalogue.
    """
    width = max(float(width_mm), 1.0)
    height = max(float(height_mm), 1.0)

    def distance(item: StandardBookFormat) -> float:
        # Erreur relative pour ne pas favoriser les grands formats.
        return hypot(
            (item.width_mm - width) / width,
            (item.height_mm - height) / height,
        )

    return min(STANDARD_BOOK_FORMATS, key=distance)


def compatible_platforms(width_mm: float, height_mm: float) -> tuple[str, ...]:
    item = find_standard_format(width_mm, height_mm)
    return item.platforms if item is not None else ()


def platform_formats(platform: str) -> tuple[StandardBookFormat, ...]:
    return tuple(item for item in STANDARD_BOOK_FORMATS if platform in item.platforms)
