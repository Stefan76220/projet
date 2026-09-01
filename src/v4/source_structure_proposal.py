from __future__ import annotations

"""
TomeLinea V4 — construction d'une proposition de Livre
à partir de l'Analyse de Source.

Cette couche :
- lit AnalysisV4 ;
- ne modifie jamais SourceV4 ;
- ne crée pas encore BookV4 ;
- produit un BookProposal traçable.

La proposition peut contenir des éléments générés par TomeLinea
lorsque la structure physique du Livre l'exige.
"""

from typing import Any

from src.v4.analysis import AnalysisV4
from src.v4.domain import (
    BookKind,
    PageOrigin,
    SourceLink,
)
from src.v4.proposal import (
    BookProposal,
    ProposalIssue,
    ProposedPage,
    ProposedPart,
)
from src.v4.source import SourceVersion


ROLE_TO_PAGE_TYPE = {
    "1re_couverture": "1re de couverture",
    "2e_couverture": "2e de couverture",
    "3e_couverture": "3e de couverture",
    "4e_couverture": "4e de couverture",
    "page_titre": "Page de titre",
    "sommaire": "Sommaire",
    "ouverture_partie": "Ouverture de partie",
    "fiche": "Fiche",
    "page_texte": "Page texte",
    "texte_image": "Texte + image",
    "illustration": "Illustration",
    "galerie": "Galerie",
    "tableau": "Tableau",
    "document_facsimile": "Document / fac-similé",
    "intercalaire": "Intercalaire",
    "page_blanche": "Page blanche",
    "conclusion_annexe": "Conclusion / annexe",
    "a_verifier": "À vérifier",
}


FRONT_ROLES = {
    "1re_couverture",
    "2e_couverture",
    "page_titre",
    "sommaire",
}


BACK_ROLES = {
    "3e_couverture",
    "4e_couverture",
}


def _page_target(
    version: SourceVersion,
    page_number: int,
) -> str:
    return (
        f"{version.id}:page:"
        f"{page_number}"
    )


def _effective(
    analysis: AnalysisV4,
    *,
    target_type: str,
    target_id: str,
    key: str,
    default: Any = None,
) -> Any:
    value = analysis.effective_value(
        target_type=target_type,
        target_id=target_id,
        key=key,
    )

    if value is None:
        return default

    return value


def _refs_for(
    analysis: AnalysisV4,
    *,
    target_type: str,
    target_id: str,
    keys: tuple[str, ...],
) -> tuple[str, ...]:
    """
    Retourne les références des décisions réellement pertinentes.

    Une correction humaine est référencée en priorité.
    Sinon on conserve le finding automatique le plus récent.
    """

    result: list[str] = []

    for key in keys:
        lookup = (
            target_type,
            target_id,
            key,
        )

        human = (
            analysis.human_decisions.get(
                lookup
            )
        )

        if human is not None:
            result.append(
                human.id
            )
            continue

        matches = [
            finding
            for finding
            in analysis.findings.values()
            if (
                finding.target_type
                == target_type
                and finding.target_id
                == target_id
                and finding.key
                == key
            )
        ]

        if not matches:
            continue

        matches.sort(
            key=lambda item: (
                item.created_at,
                item.id,
            )
        )

        result.append(
            matches[-1].id
        )

    # dédoublonnage stable
    return tuple(
        dict.fromkeys(
            result
        )
    )


def _lines(
    text: str,
) -> list[str]:
    return [
        " ".join(
            line.split()
        )
        for line
        in text.splitlines()
        if line.strip()
    ]


def _page_title(
    *,
    role: str,
    text: str,
) -> str:
    lines = _lines(
        text
    )

    if not lines:
        return (
            ROLE_TO_PAGE_TYPE.get(
                role,
                "Page",
            )
        )

    return lines[0]


def _suggested_kind(
    roles: dict[int, str],
) -> BookKind:
    fiche_count = sum(
        role == "fiche"
        for role
        in roles.values()
    )

    if fiche_count >= 2:
        return BookKind.SHEETS

    return BookKind.UNKNOWN


def build_book_proposal(
    analysis: AnalysisV4,
    *,
    source_element_id: str,
    version: SourceVersion,
) -> BookProposal:
    """
    Construit une photographie de Structure proposée.

    Aucun BookV4 n'est créé ici.
    """

    page_count = _effective(
        analysis,
        target_type="source_version",
        target_id=version.id,
        key="fact.document.page_count",
    )

    if page_count is None:
        raise ValueError(
            "Nombre de pages Source absent."
        )

    page_count = int(
        page_count
    )

    roles: dict[
        int,
        str,
    ] = {}

    texts: dict[
        int,
        str,
    ] = {}

    family_ids: dict[
        int,
        str,
    ] = {}

    family_roles: dict[
        int,
        str,
    ] = {}

    # ==========================================================
    # Lecture de l'analyse
    # ==========================================================

    for page_number in range(
        1,
        page_count + 1,
    ):
        target_id = _page_target(
            version,
            page_number,
        )

        role = _effective(
            analysis,
            target_type="source_page",
            target_id=target_id,
            key="editorial.page_role",
        )

        if role is None:
            role = "a_verifier"

        roles[
            page_number
        ] = str(role)

        texts[
            page_number
        ] = str(
            _effective(
                analysis,
                target_type="source_page",
                target_id=target_id,
                key="fact.text.content",
                default="",
            )
            or ""
        )

        family_id = _effective(
            analysis,
            target_type="source_page",
            target_id=target_id,
            key="similarity.family_id",
        )

        family_role = _effective(
            analysis,
            target_type="source_page",
            target_id=target_id,
            key="similarity.family_role",
        )

        if family_id is not None:
            family_ids[
                page_number
            ] = str(
                family_id
            )

        if family_role is not None:
            family_roles[
                page_number
            ] = str(
                family_role
            )

    proposal = BookProposal(
        suggested_kind=(
            _suggested_kind(
                roles
            )
        ),
        source_version_ids=(
            version.id,
        ),
    )

    # ==========================================================
    # Modèles proposés à partir des familles détectées
    # ==========================================================

    grouped_families: dict[
        str,
        list[int],
    ] = {}

    for (
        page_number,
        family_id,
    ) in family_ids.items():
        grouped_families.setdefault(
            family_id,
            [],
        ).append(
            page_number
        )

    model_key_by_family: dict[
        str,
        str,
    ] = {}

    for (
        family_id,
        pages,
    ) in grouped_families.items():

        ordered_pages = sorted(
            pages
        )

        model_key = (
            f"model:{source_element_id}:"
            f"family:{ordered_pages[0]}"
        )

        model_key_by_family[
            family_id
        ] = model_key

        proposal.models[
            model_key
        ] = {
            "kind": "source_family",
            "source_family_id": (
                family_id
            ),
            "source_element_id": (
                source_element_id
            ),
            "source_version_id": (
                version.id
            ),
            "pages": (
                ordered_pages
            ),
            "core_pages": [
                page
                for page
                in ordered_pages
                if family_roles.get(
                    page
                ) == "noyau"
            ],
            "variant_pages": [
                page
                for page
                in ordered_pages
                if family_roles.get(
                    page
                ) == "variante"
            ],
        }

    # ==========================================================
    # Parties
    # ==========================================================

    debut_key = (
        f"part:{source_element_id}:debut"
    )

    fin_key = (
        f"part:{source_element_id}:fin"
    )

    body_part_for_page: dict[
        int,
        str,
    ] = {}

    body_parts: list[
        ProposedPart
    ] = []

    current_body_key: str | None = None

    generic_body_created = False

    for page_number in range(
        1,
        page_count + 1,
    ):
        role = roles[
            page_number
        ]

        if role in FRONT_ROLES:
            continue

        if role in BACK_ROLES:
            continue

        if role == "ouverture_partie":
            current_body_key = (
                f"part:{source_element_id}:"
                f"opening:{page_number}"
            )

            target_id = _page_target(
                version,
                page_number,
            )

            title = _page_title(
                role=role,
                text=texts[
                    page_number
                ],
            )

            refs = _refs_for(
                analysis,
                target_type="source_page",
                target_id=target_id,
                keys=(
                    "editorial.page_role",
                    "fact.text.content",
                ),
            )

            body_parts.append(
                ProposedPart(
                    proposal_key=(
                        current_body_key
                    ),
                    title=title,
                    part_type="partie",
                    analysis_refs=refs,
                )
            )

            body_part_for_page[
                page_number
            ] = current_body_key

            continue

        if current_body_key is None:
            current_body_key = (
                f"part:{source_element_id}:corps"
            )

            if not generic_body_created:
                body_parts.append(
                    ProposedPart(
                        proposal_key=(
                            current_body_key
                        ),
                        title="Corps",
                        part_type="partie",
                    )
                )

                generic_body_created = True

        body_part_for_page[
            page_number
        ] = current_body_key

    front_refs: list[str] = []
    back_refs: list[str] = []

    for page_number in range(
        1,
        page_count + 1,
    ):
        target_id = _page_target(
            version,
            page_number,
        )

        refs = _refs_for(
            analysis,
            target_type="source_page",
            target_id=target_id,
            keys=(
                "editorial.page_role",
            ),
        )

        if (
            roles[page_number]
            in FRONT_ROLES
        ):
            front_refs.extend(
                refs
            )

        if (
            roles[page_number]
            in BACK_ROLES
        ):
            back_refs.extend(
                refs
            )

    proposal.add_part(
        ProposedPart(
            proposal_key=debut_key,
            title="Début",
            part_type="debut",
            analysis_refs=tuple(
                dict.fromkeys(
                    front_refs
                )
            ),
        )
    )

    for part in body_parts:
        proposal.add_part(
            part
        )

    proposal.add_part(
        ProposedPart(
            proposal_key=fin_key,
            title="Fin",
            part_type="fin",
            analysis_refs=tuple(
                dict.fromkeys(
                    back_refs
                )
            ),
        )
    )

    # ==========================================================
    # Pages Source + éventuelles pages générées
    # ==========================================================

    has_third_cover = any(
        role == "3e_couverture"
        for role
        in roles.values()
    )

    has_fourth_cover = any(
        role == "4e_couverture"
        for role
        in roles.values()
    )

    must_generate_third_cover = (
        has_fourth_cover
        and not has_third_cover
    )

    generated_third_cover = False

    all_analysis_refs: list[
        str
    ] = []

    def add_generated_third_cover() -> None:
        nonlocal generated_third_cover

        if generated_third_cover:
            return

        refs = tuple(
            dict.fromkeys(
                back_refs
            )
        )

        proposal.add_page(
            ProposedPage(
                proposal_key=(
                    f"page:{source_element_id}:"
                    f"auto:3e_couverture"
                ),
                page_type="3e de couverture",
                title="3e de couverture",
                origin=(
                    PageOrigin.TOMELINEA
                ),
                source=None,
                part_key=fin_key,
                analysis_refs=refs,
            )
        )

        all_analysis_refs.extend(
            refs
        )

        proposal.issues.append(
            ProposalIssue(
                code=(
                    "3e_couverture_absente_source"
                ),
                message=(
                    "Une 4e de couverture est identifiée "
                    "mais aucune 3e de couverture n'est "
                    "présente dans la Source. TomeLinea "
                    "propose une face 3e générée."
                ),
                target_key=(
                    f"page:{source_element_id}:"
                    f"auto:3e_couverture"
                ),
                severity="information",
            )
        )

        generated_third_cover = True

    for page_number in range(
        1,
        page_count + 1,
    ):
        role = roles[
            page_number
        ]

        # La face manquante se place immédiatement
        # avant la 4e de couverture.
        if (
            role == "4e_couverture"
            and must_generate_third_cover
        ):
            add_generated_third_cover()

        target_id = _page_target(
            version,
            page_number,
        )

        if role in FRONT_ROLES:
            part_key = debut_key

        elif role in BACK_ROLES:
            part_key = fin_key

        else:
            part_key = (
                body_part_for_page.get(
                    page_number
                )
            )

        family_id = (
            family_ids.get(
                page_number
            )
        )

        model_key = None

        if family_id is not None:
            model_key = (
                model_key_by_family.get(
                    family_id
                )
            )

        refs = _refs_for(
            analysis,
            target_type="source_page",
            target_id=target_id,
            keys=(
                "editorial.page_role",
                "fact.text.content",
                "similarity.family_id",
                "similarity.family_role",
            ),
        )

        all_analysis_refs.extend(
            refs
        )

        proposal.add_page(
            ProposedPage(
                proposal_key=(
                    f"page:{source_element_id}:"
                    f"source:{page_number}"
                ),
                page_type=(
                    ROLE_TO_PAGE_TYPE.get(
                        role,
                        "Page",
                    )
                ),
                title=_page_title(
                    role=role,
                    text=texts[
                        page_number
                    ],
                ),
                origin=(
                    PageOrigin.AUTHOR
                ),
                source=SourceLink(
                    source_id=(
                        source_element_id
                    ),
                    source_version_id=(
                        version.id
                    ),
                    source_page=(
                        page_number
                    ),
                ),
                part_key=part_key,
                model_key=model_key,
                analysis_refs=refs,
            )
        )

        if role == "a_verifier":
            proposal.issues.append(
                ProposalIssue(
                    code="page_role_a_verifier",
                    message=(
                        "Le rôle éditorial de cette "
                        "page doit être vérifié."
                    ),
                    target_key=(
                        f"page:{source_element_id}:"
                        f"source:{page_number}"
                    ),
                    severity="a_verifier",
                )
            )

    proposal.analysis_refs = tuple(
        dict.fromkeys(
            all_analysis_refs
        )
    )

    proposal.validate()

    return proposal
