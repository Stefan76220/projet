from __future__ import annotations

"""
TomeLinea V4 — compréhension éditoriale déterministe.

Ce moteur ne contient aucune IA.

Il reçoit :
- les faits objectifs extraits de la Source ;
- les signaux déterministes déjà calculés par TomeLinea
  (familles de pages, variantes, etc.).

Il produit uniquement des propositions éditoriales traçables.
Il ne modifie ni SourceV4 ni BookV4.
"""

from dataclasses import dataclass
import re
from typing import Any

from src.v4.analysis import ConfidenceLevel
from src.v4.intelligence import (
    AnalysisSignal,
    EditorialProposal,
    FactualObservation,
    IntelligenceContext,
)


def _normalized_lines(
    text: str,
) -> list[str]:
    return [
        " ".join(
            line.strip().split()
        )
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
    lines = _normalized_lines(
        text
    )

    if not lines:
        return False

    headings = {
        "sommaire",
        "table des matières",
        "table des matieres",
        "contents",
    }

    heading_found = any(
        _normalized(line)
        in headings
        for line
        in lines[:4]
    )

    if not heading_found:
        return False

    numbered_entries = sum(
        1
        for line
        in lines[1:]
        if re.search(
            r"\d{1,4}\s*$",
            line,
        )
    )

    return (
        numbered_entries >= 2
    )


def _looks_like_part_opening(
    text: str,
    word_count: int,
) -> bool:
    if word_count > 180:
        return False

    lines = _normalized_lines(
        text
    )

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
    dict[
        str,
        FactualObservation,
    ],
]:
    pages: dict[
        str,
        dict[
            str,
            FactualObservation,
        ],
    ] = {}

    for observation in (
        context.observations
    ):
        if (
            observation.target_type
            != "source_page"
        ):
            continue

        pages.setdefault(
            observation.target_id,
            {},
        )[
            observation.key
        ] = observation

    return pages


def _page_signals(
    context: IntelligenceContext,
) -> dict[
    str,
    dict[
        str,
        AnalysisSignal,
    ],
]:
    pages: dict[
        str,
        dict[
            str,
            AnalysisSignal,
        ],
    ] = {}

    for signal in context.signals:
        if (
            signal.target_type
            != "source_page"
        ):
            continue

        pages.setdefault(
            signal.target_id,
            {},
        )[
            signal.key
        ] = signal

    return pages


def _value(
    facts: dict[
        str,
        FactualObservation,
    ],
    key: str,
    default: Any = None,
) -> Any:
    observation = facts.get(
        key
    )

    if observation is None:
        return default

    return observation.value


def _signal_value(
    signals: dict[
        str,
        AnalysisSignal,
    ],
    key: str,
    default: Any = None,
) -> Any:
    signal = signals.get(
        key
    )

    if signal is None:
        return default

    return signal.value


def _evidence(
    facts: dict[
        str,
        FactualObservation,
    ],
    signals: dict[
        str,
        AnalysisSignal,
    ],
    fact_keys: tuple[
        str,
        ...
    ] = (),
    signal_keys: tuple[
        str,
        ...
    ] = (),
) -> tuple[
    str,
    ...
]:
    result: list[str] = []

    for key in fact_keys:
        if key in facts:
            result.append(
                facts[key].finding_id
            )

    for key in signal_keys:
        if key in signals:
            result.append(
                signals[key].finding_id
            )

    return tuple(result)


def _proposal(
    *,
    context: IntelligenceContext,
    target_id: str,
    role: str,
    confidence: ConfidenceLevel,
    rationale: str,
    facts: dict[
        str,
        FactualObservation,
    ],
    signals: dict[
        str,
        AnalysisSignal,
    ],
    fact_keys: tuple[
        str,
        ...
    ] = (),
    signal_keys: tuple[
        str,
        ...
    ] = (),
) -> EditorialProposal:

    return EditorialProposal(
        target_type="source_page",
        target_id=target_id,
        key="editorial.page_role",
        value=role,
        confidence=confidence,
        rationale=rationale,
        source_version_ids=(
            context.source_version_ids
        ),
        evidence=_evidence(
            facts,
            signals,
            fact_keys,
            signal_keys,
        ),
    )


@dataclass(
    frozen=True,
    slots=True,
)
class DeterministicEditorialRules:
    """
    Première compréhension éditoriale reproductible de TomeLinea.
    """

    engine_name: str = (
        "tomelinea.editorial_rules"
    )

    engine_version: str = "2"

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

        pages = (
            _page_observations(
                context
            )
        )

        page_signals = (
            _page_signals(
                context
            )
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

        for (
            target_id,
            facts,
        ) in ordered:

            signals = (
                page_signals.get(
                    target_id,
                    {},
                )
            )

            page_number = int(
                _value(
                    facts,
                    "page.number",
                    0,
                )
                or 0
            )

            text = str(
                _value(
                    facts,
                    "text.content",
                    "",
                )
                or ""
            )

            lines = (
                _normalized_lines(
                    text
                )
            )

            first_line = (
                _normalized(
                    lines[0]
                )
                if lines
                else ""
            )

            normalized_text = (
                _normalized(
                    text
                )
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

            family_role = (
                _signal_value(
                    signals,
                    "similarity.family_role",
                )
            )

            # ==================================================
            # Blanc réel
            # ==================================================

            if (
                char_count == 0
                and image_count == 0
                and table_count == 0
            ):
                result.append(
                    _proposal(
                        context=context,
                        target_id=target_id,
                        role="page_blanche",
                        confidence=(
                            ConfidenceLevel.PROBABLE
                        ),
                        rationale=(
                            "Aucun texte, aucune image "
                            "et aucun tableau détectés."
                        ),
                        facts=facts,
                        signals=signals,
                        fact_keys=(
                            "text.char_count",
                            "image.count",
                            "table.count",
                        ),
                    )
                )
                continue

            # ==================================================
            # Couvertures explicitement nommées
            # ==================================================

            if re.match(
                r"^(2e|2eme|2ème|deuxieme|deuxième)"
                r"\s+de\s+couverture",
                first_line,
            ):
                result.append(
                    _proposal(
                        context=context,
                        target_id=target_id,
                        role="2e_couverture",
                        confidence=(
                            ConfidenceLevel.SURE
                        ),
                        rationale=(
                            "La page se désigne explicitement "
                            "comme deuxième de couverture."
                        ),
                        facts=facts,
                        signals=signals,
                        fact_keys=(
                            "text.content",
                        ),
                    )
                )
                continue

            if re.match(
                r"^(4e|4eme|4ème|quatrieme|quatrième)"
                r"\s+de\s+couverture",
                first_line,
            ):
                result.append(
                    _proposal(
                        context=context,
                        target_id=target_id,
                        role="4e_couverture",
                        confidence=(
                            ConfidenceLevel.SURE
                        ),
                        rationale=(
                            "La page se désigne explicitement "
                            "comme quatrième de couverture."
                        ),
                        facts=facts,
                        signals=signals,
                        fact_keys=(
                            "text.content",
                        ),
                    )
                )
                continue

            # ==================================================
            # Sommaire
            # ==================================================

            if _looks_like_contents(
                text
            ):
                result.append(
                    _proposal(
                        context=context,
                        target_id=target_id,
                        role="sommaire",
                        confidence=(
                            ConfidenceLevel.PROBABLE
                        ),
                        rationale=(
                            "Un titre de sommaire est suivi "
                            "de plusieurs entrées terminées "
                            "par des numéros de pages."
                        ),
                        facts=facts,
                        signals=signals,
                        fact_keys=(
                            "text.content",
                            "text.word_count",
                        ),
                    )
                )
                continue

            # ==================================================
            # Ouverture de partie
            # ==================================================

            if _looks_like_part_opening(
                text,
                word_count,
            ):
                result.append(
                    _proposal(
                        context=context,
                        target_id=target_id,
                        role="ouverture_partie",
                        confidence=(
                            ConfidenceLevel.PROBABLE
                        ),
                        rationale=(
                            "Le titre correspond à une "
                            "ouverture de partie ou section."
                        ),
                        facts=facts,
                        signals=signals,
                        fact_keys=(
                            "text.content",
                            "text.word_count",
                        ),
                    )
                )
                continue

            # ==================================================
            # Famille répétitive de fiches
            # ==================================================

            fiche_markers = sum(
                marker in normalized_text
                for marker in (
                    "repères",
                    "reperes",
                    "observation",
                    "conseil pratique",
                )
            )

            if (
                family_role
                in {
                    "noyau",
                    "variante",
                }
                and fiche_markers >= 2
            ):
                result.append(
                    _proposal(
                        context=context,
                        target_id=target_id,
                        role="fiche",
                        confidence=(
                            ConfidenceLevel.PROBABLE
                        ),
                        rationale=(
                            "La page appartient à une famille "
                            "répétitive détectée et présente "
                            "plusieurs sections caractéristiques "
                            "d'une fiche."
                        ),
                        facts=facts,
                        signals=signals,
                        fact_keys=(
                            "text.content",
                            "image.count",
                        ),
                        signal_keys=(
                            "similarity.family_id",
                            "similarity.family_role",
                        ),
                    )
                )
                continue

            # ==================================================
            # Illustration sans texte
            # ==================================================

            if (
                char_count == 0
                and image_count > 0
            ):
                result.append(
                    _proposal(
                        context=context,
                        target_id=target_id,
                        role="illustration",
                        confidence=(
                            ConfidenceLevel.PROBABLE
                        ),
                        rationale=(
                            "La page contient une image "
                            "mais aucun texte."
                        ),
                        facts=facts,
                        signals=signals,
                        fact_keys=(
                            "text.char_count",
                            "image.count",
                            "image.coverage_ratio",
                        ),
                    )
                )
                continue

            # ==================================================
            # Galerie
            # ==================================================

            if (
                image_count >= 3
                and char_count > 0
            ):
                result.append(
                    _proposal(
                        context=context,
                        target_id=target_id,
                        role="galerie",
                        confidence=(
                            ConfidenceLevel.PROBABLE
                        ),
                        rationale=(
                            "Plusieurs images distinctes sont "
                            "réunies sur une même page avec "
                            "du contenu textuel."
                        ),
                        facts=facts,
                        signals=signals,
                        fact_keys=(
                            "image.count",
                            "text.content",
                        ),
                    )
                )
                continue

            # ==================================================
            # Tableau
            # ==================================================

            if (
                first_line.startswith(
                    "tableau"
                )
                or first_line.startswith(
                    "table "
                )
            ):
                result.append(
                    _proposal(
                        context=context,
                        target_id=target_id,
                        role="tableau",
                        confidence=(
                            ConfidenceLevel.PROBABLE
                        ),
                        rationale=(
                            "Le titre de la page identifie "
                            "un contenu tabulaire."
                        ),
                        facts=facts,
                        signals=signals,
                        fact_keys=(
                            "text.content",
                            "table.count",
                        ),
                    )
                )
                continue

            # ==================================================
            # Document / fac-similé
            # ==================================================

            document_markers = (
                "fac-simil" in normalized_text
                or "extrait reproduit"
                in normalized_text
                or "reproduit tel que fourni"
                in normalized_text
            )

            if (
                document_markers
                and image_count >= 1
            ):
                result.append(
                    _proposal(
                        context=context,
                        target_id=target_id,
                        role="document_facsimile",
                        confidence=(
                            ConfidenceLevel.PROBABLE
                        ),
                        rationale=(
                            "Le texte indique qu'un document "
                            "ou extrait est reproduit comme "
                            "élément distinct."
                        ),
                        facts=facts,
                        signals=signals,
                        fact_keys=(
                            "text.content",
                            "image.count",
                        ),
                    )
                )
                continue

            # ==================================================
            # Intercalaire
            # ==================================================

            if (
                first_line
                == "intercalaire"
            ):
                result.append(
                    _proposal(
                        context=context,
                        target_id=target_id,
                        role="intercalaire",
                        confidence=(
                            ConfidenceLevel.SURE
                        ),
                        rationale=(
                            "La page se désigne explicitement "
                            "comme intercalaire."
                        ),
                        facts=facts,
                        signals=signals,
                        fact_keys=(
                            "text.content",
                        ),
                    )
                )
                continue

            # ==================================================
            # Conclusion / annexe
            # ==================================================

            if (
                first_line.startswith(
                    "conclusion"
                )
                and "annexe"
                in first_line
            ):
                result.append(
                    _proposal(
                        context=context,
                        target_id=target_id,
                        role="conclusion_annexe",
                        confidence=(
                            ConfidenceLevel.SURE
                        ),
                        rationale=(
                            "Le titre identifie explicitement "
                            "une conclusion accompagnée "
                            "d'une annexe."
                        ),
                        facts=facts,
                        signals=signals,
                        fact_keys=(
                            "text.content",
                        ),
                    )
                )
                continue

            # ==================================================
            # Première de couverture probable
            # ==================================================

            if (
                page_number == 1
                and image_count >= 1
                and word_count <= 60
            ):
                result.append(
                    _proposal(
                        context=context,
                        target_id=target_id,
                        role="1re_couverture",
                        confidence=(
                            ConfidenceLevel.PROBABLE
                        ),
                        rationale=(
                            "Première page du document, "
                            "contenu court et grande composante "
                            "illustrée : couverture probable."
                        ),
                        facts=facts,
                        signals=signals,
                        fact_keys=(
                            "page.number",
                            "text.word_count",
                            "image.count",
                        ),
                    )
                )
                continue

            # ==================================================
            # Page de titre probable
            # ==================================================

            if (
                2 <= page_number <= 4
                and 3 <= len(lines) <= 8
                and word_count <= 40
                and image_count <= 1
            ):
                result.append(
                    _proposal(
                        context=context,
                        target_id=target_id,
                        role="page_titre",
                        confidence=(
                            ConfidenceLevel.PROBABLE
                        ),
                        rationale=(
                            "Page liminaire courte comportant "
                            "plusieurs lignes de titre/crédit "
                            "et très peu de contenu courant."
                        ),
                        facts=facts,
                        signals=signals,
                        fact_keys=(
                            "page.number",
                            "text.content",
                            "text.word_count",
                            "image.count",
                        ),
                    )
                )
                continue

            # ==================================================
            # Texte + image
            # ==================================================

            if (
                char_count > 0
                and image_count > 0
            ):
                result.append(
                    _proposal(
                        context=context,
                        target_id=target_id,
                        role="texte_image",
                        confidence=(
                            ConfidenceLevel.PROBABLE
                        ),
                        rationale=(
                            "La page associe du texte "
                            "et une illustration."
                        ),
                        facts=facts,
                        signals=signals,
                        fact_keys=(
                            "text.char_count",
                            "image.count",
                        ),
                    )
                )
                continue

            # ==================================================
            # Page essentiellement textuelle
            # ==================================================

            if (
                char_count > 0
                and image_count == 0
            ):
                result.append(
                    _proposal(
                        context=context,
                        target_id=target_id,
                        role="page_texte",
                        confidence=(
                            ConfidenceLevel.PROBABLE
                        ),
                        rationale=(
                            "La page contient du texte "
                            "sans illustration détectée."
                        ),
                        facts=facts,
                        signals=signals,
                        fact_keys=(
                            "text.char_count",
                            "image.count",
                        ),
                    )
                )
                continue

            # ==================================================
            # Cas restant
            # ==================================================

            result.append(
                _proposal(
                    context=context,
                    target_id=target_id,
                    role="a_verifier",
                    confidence=(
                        ConfidenceLevel.REVIEW
                    ),
                    rationale=(
                        "Les règles déterministes actuelles "
                        "ne permettent pas encore de classer "
                        "cette page avec suffisamment "
                        "de confiance."
                    ),
                    facts=facts,
                    signals=signals,
                )
            )

        return tuple(
            result
        )
