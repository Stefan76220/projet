from __future__ import annotations

"""
TomeLinea V4 — premières règles éditoriales déterministes.

Ce moteur :
- ne contient aucune IA ;
- ne modifie ni SourceV4 ni BookV4 ;
- reçoit uniquement le contexte détaché d'intelligence ;
- produit des propositions éditoriales avec niveau de confiance.

Il constitue une première implémentation du contrat
EditorialIntelligenceEngine.
"""

from dataclasses import dataclass
import re
from typing import Any

from src.v4.analysis import ConfidenceLevel
from src.v4.intelligence import (
    EditorialProposal,
    FactualObservation,
    IntelligenceContext,
)


def _normalized_lines(
    text: str,
) -> list[str]:
    return [
        " ".join(line.strip().split())
        for line in text.splitlines()
        if line.strip()
    ]


def _normalized(
    value: str,
) -> str:
    return (
        value.lower()
        .replace("’", "'")
        .strip()
    )


def _looks_like_contents(
    text: str,
) -> bool:
    lines = _normalized_lines(text)

    if not lines:
        return False

    headings = {
        "sommaire",
        "table des matières",
        "table des matieres",
        "contents",
    }

    heading_found = any(
        _normalized(line) in headings
        for line in lines[:4]
    )

    if not heading_found:
        return False

    # Dans certains formats structur?s (notamment ODT),
    # le texte d'une cellule et son num?ro de page peuvent ?tre
    # concat?n?s sans espace lors de l'extraction :
    # "Rosier sauvage - fiche6".
    #
    # La pr?sence explicite d'un titre de sommaire constitue d?j?
    # un indice fort ; on v?rifie donc ensuite simplement que
    # plusieurs lignes se terminent par un num?ro de page.
    numbered_entries = sum(
        1
        for line in lines[1:]
        if re.search(
            r"\d{1,4}\s*$",
            line,
        )
    )

    return numbered_entries >= 2


def _looks_like_part_opening(
    text: str,
    word_count: int,
) -> bool:
    if word_count > 180:
        return False

    lines = _normalized_lines(text)

    if not lines:
        return False

    first = lines[0]

    return bool(
        re.match(
            r"^(partie|part|section|livre)"
            r"\s+"
            r"(?:[ivxlcdm]+|\d+)"
            r"(?:\b|\s|[-–—:])",
            first,
            flags=re.IGNORECASE,
        )
    )


def _page_observations(
    context: IntelligenceContext,
) -> dict[
    str,
    dict[str, FactualObservation],
]:
    pages: dict[
        str,
        dict[str, FactualObservation],
    ] = {}

    for observation in context.observations:
        if observation.target_type != "source_page":
            continue

        pages.setdefault(
            observation.target_id,
            {},
        )[observation.key] = observation

    return pages


def _value(
    facts: dict[
        str,
        FactualObservation,
    ],
    key: str,
    default: Any = None,
) -> Any:
    observation = facts.get(key)

    if observation is None:
        return default

    return observation.value


def _evidence(
    facts: dict[
        str,
        FactualObservation,
    ],
    *keys: str,
) -> tuple[str, ...]:
    return tuple(
        facts[key].finding_id
        for key in keys
        if key in facts
    )


@dataclass(frozen=True, slots=True)
class DeterministicEditorialRules:
    """
    Première intelligence éditoriale TomeLinea.

    Elle utilise uniquement des règles explicites et reproductibles.
    """

    engine_name: str = (
        "tomelinea.editorial_rules"
    )

    engine_version: str = "1"

    def propose(
        self,
        context: IntelligenceContext,
    ) -> tuple[
        EditorialProposal,
        ...
    ]:

        result: list[
            EditorialProposal
        ] = []

        pages = _page_observations(
            context
        )

        ordered = sorted(
            pages.items(),
            key=lambda item: int(
                _value(
                    item[1],
                    "page.number",
                    999999,
                )
            ),
        )

        for target_id, facts in ordered:
            text = str(
                _value(
                    facts,
                    "text.content",
                    "",
                )
                or ""
            )

            char_count = int(
                _value(
                    facts,
                    "text.char_count",
                    0,
                )
                or 0
            )

            word_count = int(
                _value(
                    facts,
                    "text.word_count",
                    0,
                )
                or 0
            )

            image_count = int(
                _value(
                    facts,
                    "image.count",
                    0,
                )
                or 0
            )

            table_count = int(
                _value(
                    facts,
                    "table.count",
                    0,
                )
                or 0
            )

            # --------------------------------------------------
            # Page sans contenu détectable
            # --------------------------------------------------

            if (
                char_count == 0
                and image_count == 0
                and table_count == 0
            ):
                result.append(
                    EditorialProposal(
                        target_type="source_page",
                        target_id=target_id,
                        key="editorial.page_role",
                        value="page_blanche",
                        confidence=(
                            ConfidenceLevel.PROBABLE
                        ),
                        rationale=(
                            "Aucun texte, aucune image "
                            "et aucun tableau détectés."
                        ),
                        source_version_ids=(
                            context.source_version_ids
                        ),
                        evidence=_evidence(
                            facts,
                            "text.char_count",
                            "image.count",
                            "table.count",
                        ),
                    )
                )

                continue

            # --------------------------------------------------
            # Illustration sans texte
            # --------------------------------------------------

            if (
                char_count == 0
                and image_count > 0
            ):
                result.append(
                    EditorialProposal(
                        target_type="source_page",
                        target_id=target_id,
                        key="editorial.page_role",
                        value="illustration",
                        confidence=(
                            ConfidenceLevel.PROBABLE
                        ),
                        rationale=(
                            "La page contient une ou "
                            "plusieurs images mais aucun texte."
                        ),
                        source_version_ids=(
                            context.source_version_ids
                        ),
                        evidence=_evidence(
                            facts,
                            "text.char_count",
                            "image.count",
                            "image.coverage_ratio",
                        ),
                    )
                )

                continue

            # --------------------------------------------------
            # Sommaire
            # --------------------------------------------------

            if _looks_like_contents(
                text
            ):
                result.append(
                    EditorialProposal(
                        target_type="source_page",
                        target_id=target_id,
                        key="editorial.page_role",
                        value="sommaire",
                        confidence=(
                            ConfidenceLevel.PROBABLE
                        ),
                        rationale=(
                            "Titre de sommaire détecté "
                            "avec plusieurs entrées "
                            "associées à des numéros."
                        ),
                        source_version_ids=(
                            context.source_version_ids
                        ),
                        evidence=_evidence(
                            facts,
                            "text.content",
                            "text.word_count",
                        ),
                    )
                )

                continue

            # --------------------------------------------------
            # Ouverture de partie
            # --------------------------------------------------

            if _looks_like_part_opening(
                text,
                word_count,
            ):
                result.append(
                    EditorialProposal(
                        target_type="source_page",
                        target_id=target_id,
                        key="editorial.page_role",
                        value="ouverture_partie",
                        confidence=(
                            ConfidenceLevel.PROBABLE
                        ),
                        rationale=(
                            "Le premier titre correspond "
                            "à une ouverture de partie, "
                            "section ou livre et la page "
                            "contient peu de texte."
                        ),
                        source_version_ids=(
                            context.source_version_ids
                        ),
                        evidence=_evidence(
                            facts,
                            "text.content",
                            "text.word_count",
                        ),
                    )
                )

        return tuple(result)
